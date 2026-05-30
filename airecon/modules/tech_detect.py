"""
TechDetect - Technology detection module for AIRecon.

Uses WhatWeb or Wappalyzer inside a Kali Linux Docker container to identify
web technologies, frameworks, and CMS platforms.

Usage:
    detector = TechDetect()
    results = await detector.detect("https://example.com")
"""

import asyncio
import json
import logging
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Union

import docker
from docker.errors import DockerException

logger = logging.getLogger(__name__)

# Default Kali image to use
DEFAULT_KALI_IMAGE = "kalilinux/kali-rolling"

# Common tools paths inside Kali
WHATWEB_CMD = "whatweb --log-json=/tmp/whatweb_output.json {target} && cat /tmp/whatweb_output.json"
WAPPALYZER_CMD = "wappalyzer-cli {target} 2>/dev/null || node /opt/wappalyzer/src/index.js {target} 2>/dev/null || echo '{}'"


class TechDetectError(Exception):
    """Base exception for technology detection failures."""


class TechDetect:
    """Detect web technologies using containerized tools."""

    def __init__(
        self,
        docker_client: Optional[docker.DockerClient] = None,
        kali_image: str = DEFAULT_KALI_IMAGE,
        timeout: int = 120,
    ):
        """
        Initialize the detector.

        Args:
            docker_client: Pre-configured Docker client (creates one if None).
            kali_image: Docker image name for Kali container.
            timeout: Timeout in seconds for container execution.
        """
        self.kali_image = kali_image
        self.timeout = timeout
        self.docker = docker_client or self._create_docker_client()
        self._ensure_image()

    def _create_docker_client(self) -> docker.DockerClient:
        """Create a Docker client from environment or defaults."""
        try:
            return docker.from_env(version="auto", timeout=self.timeout + 10)
        except DockerException as e:
            raise TechDetectError(f"Failed to create Docker client: {e}")

    def _ensure_image(self) -> None:
        """Ensure the Kali image is available locally (pull if needed)."""
        try:
            self.docker.images.get(self.kali_image)
        except docker.errors.ImageNotFound:
            logger.info(f"Pulling Kali image: {self.kali_image}")
            self.docker.images.pull(self.kali_image, platform="linux/amd64")
        except Exception as e:
            logger.warning(f"Cannot verify/pull image {self.kali_image}: {e}")

    def _run_container(self, command: str, target: str) -> str:
        """
        Run a command inside a transient Kali container.

        Args:
            command: Shell command to execute (may contain {target} placeholder).
            target: The target URL/IP to substitute.

        Returns:
            stdout of the command.

        Raises:
            TechDetectError if container fails.
        """
        cmd = command.format(target=target)
        try:
            container = self.docker.containers.run(
                image=self.kali_image,
                command=["/bin/bash", "-c", cmd],
                detach=False,
                remove=True,
                mem_limit="512m",
                network_mode="bridge",
                stdout=True,
                stderr=True,
            )
            output = container.decode("utf-8", errors="replace").strip()
            return output
        except docker.errors.ContainerError as e:
            raise TechDetectError(f"Container execution failed: {e.stderr.decode()}")
        except Exception as e:
            raise TechDetectError(f"Docker error: {e}")

    async def detect(
        self, target: str, tool: str = "both"
    ) -> List[Dict[str, Union[str, List[str]]]]:
        """
        Detect technologies on a target.

        Args:
            target: Full URL (e.g., "https://example.com") or IP.
            tool: Which tool to use: "whatweb", "wappalyzer", or "both".

        Returns:
            List of dictionaries with keys: "name", "version", "certainty", "categories", "source".

        Note:
            Categories and version may be empty or lists depending on tool.
        """
        if tool not in ("whatweb", "wappalyzer", "both"):
            raise ValueError("tool must be 'whatweb', 'wappalyzer', or 'both'")

        results = []

        if tool in ("whatweb", "both"):
            try:
                logger.debug(f"Running WhatWeb against {target}")
                raw = await asyncio.get_event_loop().run_in_executor(
                    None, self._run_container, WHATWEB_CMD, target
                )
                parsed = self._parse_whatweb(raw)
                results.extend(parsed)
            except Exception as e:
                logger.warning(f"WhatWeb failed: {e}")

        if tool in ("wappalyzer", "both") and not results:
            try:
                logger.debug(f"Running Wappalyzer against {target}")
                raw = await asyncio.get_event_loop().run_in_executor(
                    None, self._run_container, WAPPALYZER_CMD, target
                )
                parsed = self._parse_wappalyzer(raw)
                results.extend(parsed)
            except Exception as e:
                logger.warning(f"Wappalyzer failed: {e}")

        if not results:
            logger.info(f"No technologies detected for {target}")

        return results

    def _parse_whatweb(self, raw_output: str) -> List[Dict]:
        """Parse WhatWeb JSON output into unified format."""
        if not raw_output or raw_output.startswith("WhatWeb"):
            return []

        try:
            data = json.loads(raw_output)
        except json.JSONDecodeError:
            logger.error("WhatWeb output is not valid JSON")
            return []

        # WhatWeb per-URL results are under keys like "https://example.com"
        results = []
        for url, plugins in data.items():
            if not isinstance(plugins, dict):
                continue
            for plugin_name, info in plugins.items():
                entry = {
                    "name": plugin_name,
                    "version": info.get("version", ""),
                    "certainty": info.get("certainty", 100),
                    "categories": info.get("categories", []),
                    "source": "whatweb",
                    "url": url,
                }
                results.append(entry)
        return results

    def _parse_wappalyzer(self, raw_output: str) -> List[Dict]:
        """Parse Wappalyzer JSON output into unified format."""
        if not raw_output:
            return []

        try:
            data = json.loads(raw_output)
        except json.JSONDecodeError:
            logger.error("Wappalyzer output is not valid JSON")
            return []

        # Wappalyzer returns a list with first element being the result dict
        if isinstance(data, list) and len(data) > 0:
            data = data[0]

        results = []
        # The data dict may have keys like "technologies" or be a flat dict
        technologies = data.get("technologies", data)
        if isinstance(technologies, dict):
            for tech_name, details in technologies.items():
                if not isinstance(details, dict):
                    details = {}
                entry = {
                    "name": tech_name,
                    "version": details.get("version", ""),
                    "certainty": details.get("confidence", 100),
                    "categories": details.get("categories", []),
                    "source": "wappalyzer",
                    "url": data.get("url", ""),
                }
                results.append(entry)
        elif isinstance(technologies, list):
            for tech in technologies:
                if isinstance(tech, dict):
                    entry = {
                        "name": tech.get("name", ""),
                        "version": tech.get("version", ""),
                        "certainty": tech.get("confidence", 100),
                        "categories": tech.get("categories", []),
                        "source": "wappalyzer",
                        "url": data.get("url", ""),
                    }
                    results.append(entry)
        return results

    async def close(self) -> None:
        """Clean up Docker client if we created it."""
        if hasattr(self, "docker") and self.docker:
            try:
                self.docker.close()
            except Exception:
                pass