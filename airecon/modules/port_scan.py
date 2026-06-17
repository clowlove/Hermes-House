#!/usr/bin/env python3
"""
AIRecon - Port Scan Module
Runs nmap or masscan with predefined profiles.
"""

from __future__ import annotations

import asyncio
import json
import logging
import re
import subprocess
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Default timeout per scan in seconds
SCAN_TIMEOUT = 600  # 10 minutes for full scans

# Common port lists (IETF/IANA top 1000 ports placeholder – actual list too long)
# Use nmap-services or provide a subset; for brevity we rely on nmap/masscan -F etc.
TOP_1000_PORTS = "1-1000"  # Simplification; real tool handles it

# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


@dataclass
class PortScanResult:
    """Result of a single port scan on one host."""
    host: str
    hostname: Optional[str] = None
    opened_ports: List[Dict[str, Any]] = field(default_factory=list)
    raw_output: str = ""
    scan_type: str = ""  # "nmap" or "masscan"
    profile: str = ""
    error: Optional[str] = None


@dataclass
class ScanProfile:
    """Configuration for a scan profile."""
    name: str
    port_spec: str  # e.g., "1-1000", "top-100", "0-65535"
    arguments: List[str] = field(default_factory=list)
    description: str = ""

    def to_nmap_args(self) -> List[str]:
        """Convert profile to nmap arguments."""
        base: List[str] = []
        if self.port_spec.isdigit() or '-' in self.port_spec:
            # treat as port range
            base.extend(["-p", self.port_spec])
        elif self.port_spec == "top-100":
            base.extend(["--top-ports", "100"])
        elif self.port_spec == "top-1000":
            base.extend(["--top-ports", "1000"])
        else:
            # assume port list
            base.extend(["-p", self.port_spec])
        base.extend(self.arguments)
        return base

    def to_masscan_args(self) -> List[str]:
        """Convert profile to masscan arguments."""
        base: List[str] = []
        if self.port_spec in ("top-100", "top-1000"):
            # masscan cannot use --top-ports directly; approximate with range
            logger.warning("Masscan does not support top-ports, using full range.")
            base.extend(["-p", "1-65535"])
        else:
            base.extend(["-p", self.port_spec])
        base.extend(self.arguments)
        return base


# ---------------------------------------------------------------------------
# Predefined profiles
# ---------------------------------------------------------------------------

PROFILES: Dict[str, ScanProfile] = {
    "quick": ScanProfile(
        name="quick",
        port_spec="top-1000",
        arguments=["-T4", "--max-retries", "1"],
        description="Quick scan of top 1000 TCP ports (no service detection)",
    ),
    "top100": ScanProfile(
        name="top100",
        port_spec="top-100",
        arguments=["-T4", "--max-retries", "1"],
        description="Top 100 TCP ports",
    ),
    "full": ScanProfile(
        name="full",
        port_spec="1-65535",
        arguments=["-T4", "--max-retries", "2"],
        description="Full TCP port scan (all 65535 ports)",
    ),
    "service": ScanProfile(
        name="service",
        port_spec="top-1000",
        arguments=["-sV", "--version-intensity", "5", "-T4"],
        description="Top 1000 ports with service version detection",
    ),
    "aggressive": ScanProfile(
        name="aggressive",
        port_spec="top-1000",
        arguments=["-A", "-T4", "--max-retries", "1"],
        description="Aggressive scan with OS detection, scripts, and traceroute",
    ),
}


def get_profile(name: str, **overrides) -> ScanProfile:
    """Retrieve a profile by name, optionally merging custom arguments."""
    if name not in PROFILES:
        raise ValueError(f"Unknown profile: {name}. Available: {list(PROFILES.keys())}")
    prof = PROFILES[name]
    if overrides:
        # shallow copy and update
        import copy
        prof = copy.deepcopy(prof)
        if 'port_spec' in overrides:
            prof.port_spec = overrides['port_spec']
        if 'arguments' in overrides and isinstance(overrides['arguments'], list):
            prof.arguments = overrides['arguments']
    return prof


# ---------------------------------------------------------------------------
# Utility functions
# ---------------------------------------------------------------------------


def _is_tool_available(tool: str) -> bool:
    """Check if a command-line tool is available on the system."""
    try:
        subprocess.run(
            ["which", tool], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True
        )
        return True
    except subprocess.CalledProcessError:
        return False


def _parse_nmap_xml(xml_content: str) -> List[Dict[str, Any]]:
    """Parse nmap XML output into a list of open port dictionaries."""
    ports: List[Dict[str, Any]] = []
    try:
        root = ET.fromstring(xml_content)
    except ET.ParseError as e:
        logger.error("Failed to parse nmap XML: %s", e)
        return ports

    for host in root.findall("host"):
        for port_elem in host.findall(".//port"):
            state = port_elem.find("state")
            if state is not None and state.get("state") == "open":
                port_info = {
                    "port": int(port_elem.get("portid")),
                    "protocol": port_elem.get("protocol", "tcp"),
                    "service": port_elem.findtext("service/name", ""),
                    "version": port_elem.findtext("service/product", ""),
                    "state": "open",
                }
                ports.append(port_info)
    return ports


def _parse_masscan_json(data: str) -> List[Dict[str, Any]]:
    """Parse masscan JSON output into a list of port dictionaries."""
    ports: List[Dict[str, Any]] = []
    try:
        for line in data.strip().splitlines():
            if not line:
                continue
            record = json.loads(line)
            if record.get("reason") == "syn-ack":
                port_info = {
                    "port": record.get("port", 0),
                    "protocol": record.get("proto", "tcp"),
                    "ip": record.get("ip", ""),
                    "state": "open",
                }
                ports.append(port_info)
    except json.JSONDecodeError as e:
        logger.error("Failed to parse masscan JSON: %s", e)
    return ports


# ---------------------------------------------------------------------------
# Main scan functions
# ---------------------------------------------------------------------------


async def run_nmap_scan(
    target: str,
    profile: ScanProfile,
    timeout: int = SCAN_TIMEOUT,
    extra_args: Optional[List[str]] = None,
) -> PortScanResult:
    """
    Execute an nmap scan asynchronously.

    Args:
        target: IP or hostname to scan.
        profile: ScanProfile instance.
        timeout: Timeout in seconds.
        extra_args: Additional nmap arguments (e.g., ``["--exclude-ports", "22"]``).

    Returns:
        PortScanResult with parsed open ports.
    """
    logger.info("Running nmap scan on %s with profile '%s'", target, profile.name)

    cmd = ["nmap", "-oX", "-"]  # output XML to stdout
    cmd.extend(profile.to_nmap_args())
    if extra_args:
        cmd.extend(extra_args)
    cmd.append(target)

    # Ensure we run with sudo if required (nmap needs root for some scan types)
    # In Docker container we may be root anyway.
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
    except asyncio.TimeoutError:
        proc.terminate()
        return PortScanResult(
            host=target,
            error=f"Scan timed out after {timeout} seconds",
            scan_type="nmap",
            profile=profile.name,
        )
    except FileNotFoundError:
        return PortScanResult(
            host=target,
            error="nmap not found on system",
            scan_type="nmap",
            profile=profile.name,
        )

    if proc.returncode != 0:
        logger.warning("nmap returned non-zero exit code %d: %s", proc.returncode, stderr.decode())
        # still try to parse if there is output
    stdout_str = stdout.decode(errors="replace")
    parsed_ports = _parse_nmap_xml(stdout_str)

    result = PortScanResult(
        host=target,
        opened_ports=parsed_ports,
        raw_output=stdout_str,
        scan_type="nmap",
        profile=profile.name,
    )

    # Extract hostname if present
    try:
        root = ET.fromstring(stdout_str)
        host_elem = root.find("host")
        if host_elem is not None:
            hostnames = host_elem.find("hostnames")
            if hostnames is not None:
                hn = hostnames.find("hostname")
                if hn is not None:
                    result.hostname = hn.get("name")
    except ET.ParseError:
        pass

    return result


async def run_masscan_scan(
    target: str,
    profile: ScanProfile,
    timeout: int = SCAN_TIMEOUT,
    rate: int = 1000,
    extra_args: Optional[List[str]] = None,
) -> PortScanResult:
    """
    Execute a masscan scan asynchronously.

    Args:
        target: IP address (masscan does not resolve hostnames by default).
        profile: ScanProfile instance.
        timeout: Timeout in seconds.
        rate: Packets per second (default 1000).
        extra_args: Additional masscan arguments.

    Returns:
        PortScanResult with parsed open ports.
    """
    logger.info("Running masscan scan on %s with profile '%s'", target, profile.name)

    cmd = ["masscan", target, "--rate", str(rate), "-oJ", "-"]  # output JSON to stdout
    cmd.extend(profile.to_masscan_args())
    if extra_args:
        cmd.extend(extra_args)

    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
    except asyncio.TimeoutError:
        proc.terminate()
        return PortScanResult(
            host=target,
            error=f"Masscan timed out after {timeout} seconds",
            scan_type="masscan",
            profile=profile.name,
        )
    except FileNotFoundError:
        return PortScanResult(
            host=target,
            error="masscan not found on system",
            scan_type="masscan",
            profile=profile.name,
        )

    if proc.returncode != 0:
        logger.warning("masscan returned non-zero exit code %d: %s", proc.returncode, stderr.decode())

    stdout_str = stdout.decode(errors="replace")
    parsed_ports = _parse_masscan_json(stdout_str)

    return PortScanResult(
        host=target,
        opened_ports=parsed_ports,
        raw_output=stdout_str,
        scan_type="masscan",
        profile=profile.name,
    )


async def run_scan(
    target: str,
    profile_name: str = "quick",
    scan_type: str = "auto",
    timeout: int = SCAN_TIMEOUT,
    **kwargs,
) -> PortScanResult:
    """
    High-level scan entry point. Automatically picks the best available scanner.

    Args:
        target: IP address or hostname.
        profile_name: One of 'quick', 'top100', 'full', 'service', 'aggressive'.
        scan_type: 'nmap', 'masscan', or 'auto' (prefer masscan).
        timeout: Maximum scan duration in seconds.
        extra_args: Additional arguments for the scanner (optional).

    Returns:
        PortScanResult.
    """
    profile = get_profile(profile_name)
    extra_args = kwargs.get("extra_args")

    if scan_type == "auto":
        tool = "masscan" if _is_tool_available("masscan") else "nmap"
    else:
        tool = scan_type
        if not _is_tool_available(tool):
            logger.warning("Requested tool '%s' not available, falling back to nmap", tool)
            tool = "nmap"

    if tool == "masscan":
        result = await run_masscan_scan(target, profile, timeout=timeout, extra_args=extra_args)
    else:
        result = await run_nmap_scan(target, profile, timeout=timeout, extra_args=extra_args)
    return result


# ---------------------------------------------------------------------------
# Convenience synchronous wrapper (for non-async contexts)
# ---------------------------------------------------------------------------


def scan_sync(
    target: str,
    profile_name: str = "quick",
    scan_type: str = "auto",
    timeout: int = SCAN_TIMEOUT,
    **kwargs,
) -> PortScanResult:
    """Synchronous wrapper around :func:`run_scan`."""
    return asyncio.run(run_scan(target, profile_name, scan_type, timeout, **kwargs))


# ---------------------------------------------------------------------------
# Module-level helpers
# ---------------------------------------------------------------------------


def list_profiles() -> List[str]:
    """Return list of available profile names."""
    return list(PROFILES.keys())


def profile_details(name: str) -> Optional[Dict[str, Any]]:
    """Get details of a profile."""
    try:
        prof = get_profile(name)
    except ValueError:
        return None
    return {
        "name": prof.name,
        "port_spec": prof.port_spec,
        "arguments": prof.arguments,
        "description": prof.description,
    }


# ---------------------------------------------------------------------------
# Example usage (if run as script)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    target = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
    profile_name = sys.argv[2] if len(sys.argv) > 2 else "quick"
    print(f"Scanning {target} with profile '{profile_name}'...")
    result = scan_sync(target, profile_name)
    print(f"Result: {len(result.opened_ports)} open ports found.")
    for port in result.opened_ports:
        print(f"  {port.get('protocol','tcp').upper()}/{port['port']}  {port.get('service','')} {port.get('version','')}")
    if result.error:
        print(f"Error: {result.error}")