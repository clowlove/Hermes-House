"""
AIRecon - Subdomain Enumeration Module

Production-grade wrapper for subdomain discovery tools (subfinder, amass)
executed inside a Docker sandbox. Returns structured, deduplicated results.
"""

from __future__ import annotations

import asyncio
import json
import logging
import re
from dataclasses import dataclass, field
from typing import Awaitable, Callable, List, Optional, Tuple

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class SubdomainResult:
    """Result from a single subdomain enumeration tool execution."""
    tool: str                            # e.g. "subfinder", "amass"
    domain: str                          # target domain
    subdomains: List[str] = field(default_factory=list)
    raw_output: str = ""                 # unparsed tool stdout
    errors: List[str] = field(default_factory=list)
    exit_code: int = 0


# ---------------------------------------------------------------------------
# Tool-specific parsers
# ---------------------------------------------------------------------------

def _parse_subfinder_output(output: str) -> List[str]:
    """
    Parse subfinder output lines (one subdomain per line).
    Filters out empty lines and comments.
    """
    subdomains: List[str] = []
    for line in output.splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            subdomains.append(line)
    return subdomains


def _parse_amass_output(output: str) -> List[str]:
    """
    Parse amass JSON lines output (supported via -json flag).
    Falls back to subdomain extraction from text output if JSON is not used.
    """
    subdomains: List[str] = []
    for line in output.splitlines():
        line = line.strip()
        if not line:
            continue
        # Try JSON first (amass -json)
        if line.startswith("{"):
            try:
                record = json.loads(line)
                if "name" in record:
                    subdomains.append(record["name"])
            except json.JSONDecodeError:
                # Not JSON – treat as plain text fallback
                subdomains.append(line)
        else:
            # Plain text: each line may be a subdomain
            subdomains.append(line)
    return subdomains


# ---------------------------------------------------------------------------
# Tool command builders
# ---------------------------------------------------------------------------

_BUILD_COMMAND = {
    "subfinder": lambda domain: (
        f"subfinder -d {domain} -o /dev/stdout -silent 2>/dev/null"
    ),
    "amass": lambda domain: (
        f"amass enum -passive -d {domain} "
        f"-json /dev/stdout -o /dev/null 2>/dev/null"
        # Use -passive to avoid heavy active scans; adjust as needed.
    ),
}

_PARSER = {
    "subfinder": _parse_subfinder_output,
    "amass": _parse_amass_output,
}

# Tools that we assume are pre-installed in the Kali sandbox.
# The module will try to install them if not found (fail-soft).
_INSTALL_COMMANDS = {
    "subfinder": "apt-get update -qq && apt-get install -y -qq subfinder 2>/dev/null",
    "amass": "apt-get update -qq && apt-get install -y -qq amass 2>/dev/null",
}


# ---------------------------------------------------------------------------
# Main module class
# ---------------------------------------------------------------------------

# Type alias for command execution callback
# Accepts a command string, returns (exit_code, stdout)
ExecCommand = Callable[[str], Awaitable[Tuple[int, str]]]


class SubdomainEnum:
    """
    Subdomain enumeration module.

    Wraps subfinder and amass inside a Docker sandbox and returns
    structured, deduplicated results.

    Usage:
        async def executor(cmd: str) -> Tuple[int, str]:
            # implement via docker-py container.exec_run
            ...

        module = SubdomainEnum(executor)
        results = await module.run("example.com", tools=["subfinder", "amass"])
    """

    def __init__(self, executor: ExecCommand):
        """
        Args:
            executor: An async callable that takes a shell command string and
                      returns a tuple (exit_code: int, stdout: str).
                      Typically wraps container.exec_run() inside the sandbox.
        """
        self._exec = executor
        self._lock = asyncio.Lock()  # optional: serialise tool runs if needed

    async def run(
        self,
        domain: str,
        tools: Optional[List[str]] = None,
        *,
        timeout: int = 300,
    ) -> List[SubdomainResult]:
        """
        Execute subdomain enumeration against a target domain.

        Args:
            domain: Target domain (e.g. "example.com").
            tools: List of tools to use. Defaults to ["subfinder", "amass"].
            timeout: Maximum seconds per tool execution.

        Returns:
            List of SubdomainResult, one per tool.

        Raises:
            ValueError: If an unknown tool is requested.
        """
        if tools is None:
            tools = ["subfinder", "amass"]
        if not tools:
            raise ValueError("At least one tool must be specified.")

        unknown = set(tools) - set(_BUILD_COMMAND.keys())
        if unknown:
            raise ValueError(f"Unknown tool(s): {unknown}")

        results: List[SubdomainResult] = []
        # Run tools sequentially to avoid resource contention in the sandbox.
        for tool in tools:
            result = await self._run_single_tool(tool, domain, timeout)
            results.append(result)

        return results

    async def _run_single_tool(
        self,
        tool: str,
        domain: str,
        timeout: int,
    ) -> SubdomainResult:
        """Execute a single tool and return parsed result."""
        result = SubdomainResult(tool=tool, domain=domain)
        build_cmd = _BUILD_COMMAND[tool]

        # 1. Ensure tool is installed
        install_cmd = _INSTALL_COMMANDS.get(tool)
        if install_cmd:
            try:
                exit_code_install, stdout_install = await asyncio.wait_for(
                    self._exec(install_cmd), timeout=120
                )
                if exit_code_install != 0:
                    logger.warning(
                        "Install of %s returned %d: %s",
                        tool,
                        exit_code_install,
                        stdout_install[:200],
                    )
            except asyncio.TimeoutError:
                logger.error("Timeout while installing %s", tool)
                result.errors.append(f"Installation timed out for {tool}")
                return result
            except Exception as exc:
                logger.error("Installation of %s failed: %s", tool, exc)
                result.errors.append(str(exc))
                return result

        # 2. Run the enumeration command
        cmd = build_cmd(domain)
        logger.info("Running %s for domain %s", tool, domain)
        try:
            exit_code, output = await asyncio.wait_for(
                self._exec(cmd), timeout=timeout
            )
        except asyncio.TimeoutError:
            logger.error("Tool %s timed out after %d seconds", tool, timeout)
            result.errors.append(f"Execution timed out after {timeout}s")
            return result
        except Exception as exc:
            logger.exception("Tool %s execution error", tool)
            result.errors.append(str(exc))
            return result

        result.exit_code = exit_code
        result.raw_output = output

        if exit_code != 0:
            logger.warning("Tool %s finished with exit code %d", tool, exit_code)
            result.errors.append(f"Exit code {exit_code}")
            # Attempt to parse partial output anyway
        else:
            logger.info("Tool %s completed successfully", tool)

        # 3. Parse output
        parser = _PARSER[tool]
        try:
            subdomains = parser(output)
        except Exception as exc:
            logger.error("Failed to parse %s output: %s", tool, exc)
            result.errors.append(f"Parsing error: {exc}")
        else:
            result.subdomains = list(dict.fromkeys(subdomains))  # dedup & preserve order

        return result


# ---------------------------------------------------------------------------
# Standalone test / usage demonstration (if executed directly)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO)

    # Dummy executor for demonstration – replace with real Docker executor.
    async def dummy_executor(cmd: str) -> Tuple[int, str]:
        print(f"[Dummy exec] {cmd[:80]}...")
        # Simulate subfinder output
        if "subfinder" in cmd:
            return 0, "sub1.example.com\nsub2.example.com\n"
        if "amass" in cmd:
            return 0, '{"name":"sub3.example.com"}\nsub4.example.com\n'
        return 1, "Tool not found"

    async def main():
        module = SubdomainEnum(dummy_executor)
        domain = sys.argv[1] if len(sys.argv) > 1 else "example.com"
        results = await module.run(domain)
        for r in results:
            print(f"\n=== {r.tool} ===")
            print(f"  Exit code: {r.exit_code}")
            print(f"  Errors: {r.errors or 'none'}")
            print(f"  Subdomains ({len(r.subdomains)}):")
            for sd in r.subdomains:
                print(f"    - {sd}")

    asyncio.run(main())