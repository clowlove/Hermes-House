"""
Configuration loader for AIRecon.

Reads YAML configuration with sensible defaults for Ollama URL,
Docker image, and timeouts. Supports environment variable overrides.
The loading order (highest priority last): hard‑coded defaults < YAML file
< environment variables (AIRECON_*). All runtime validation is performed
on each field; invalid values raise a clear ValueError with context.
"""

from __future__ import annotations

import logging
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Final, Optional, Union

import yaml

logger = logging.getLogger(__name__)

__all__ = [
    "Config",
    "load_config",
    "DEFAULT_OLLAMA_URL",
    "DEFAULT_DOCKER_IMAGE",
    "DEFAULT_REQUEST_TIMEOUT",
    "DEFAULT_CONTAINER_TIMEOUT",
    "MIN_TIMEOUT",
    "MAX_TIMEOUT",
]

# ---- Constants ----
DEFAULT_OLLAMA_URL: Final[str] = "http://localhost:11434"
DEFAULT_DOCKER_IMAGE: Final[str] = "kalilinux/kali-rolling:latest"
DEFAULT_REQUEST_TIMEOUT: Final[float] = 120.0
DEFAULT_CONTAINER_TIMEOUT: Final[float] = 300.0
DEFAULT_CONFIG_PATH: Final[str] = "airecon.yaml"
MIN_TIMEOUT: Final[float] = 1.0
MAX_TIMEOUT: Final[float] = 86400.0  # 24 hours

# Pre‑compiled regex for Docker image validation (per Docker reference spec)
_DOCKER_IMAGE_REGEX: Final[re.Pattern] = re.compile(
    r"^[a-zA-Z0-9][a-zA-Z0-9._/-]*(?::[a-zA-Z0-9_.-]{1,128})?"
    r"(?:@sha256:[a-f0-9]{64})?$"
)

# Environment variable mapping (prefix AIRECON_)
ENV_MAP: Final[Dict[str, str]] = {
    "OLLAMA_URL": "AIRecon Ollama base URL",
    "DOCKER_IMAGE": "Docker image for sandbox containers",
    "REQUEST_TIMEOUT": "Timeout for LLM requests in seconds",
    "CONTAINER_TIMEOUT": "Timeout for reconnaissance task execution in seconds",
}


@dataclass(frozen=True)
class Config:
    """Immutable configuration container for AIRecon.

    Attributes:
        ollama_url: Base URL of the Ollama service.
        docker_image: Docker image tag for sandbox containers.
        request_timeout: Maximum time (seconds) for a single LLM API call.
        container_timeout: Maximum time (seconds) for a reconnaissance task
            inside a container.
        config_path: Filesystem path from which the configuration was loaded,
            if applicable. May be ``None`` if only defaults were used.
    """

    ollama_url: str = DEFAULT_OLLAMA_URL
    docker_image: str = DEFAULT_DOCKER_IMAGE
    request_timeout: float = DEFAULT_REQUEST_TIMEOUT
    container_timeout: float = DEFAULT_CONTAINER_TIMEOUT
    config_path: Optional[str] = None

    def __post_init__(self) -> None:
        """Validate every configuration field after initialisation.

        Raises:
            ValueError: If any field fails its validation rule.
            TypeError: If a field has an unexpected type.
        """
        # Validate numeric fields (positive, finite, within reasonable bounds)
        for field_name, value in (
            ("request_timeout", self.request_timeout),
            ("container_timeout", self.container_timeout),
        ):
            self._validate_timeout(field_name, value)

        # URL validation
        if not self.ollama_url or not isinstance(self.ollama_url, str):
            raise ValueError(
                f"ollama_url must be a non‑empty string, got {self.ollama_url!r}"
            )
        if not self.ollama_url.startswith(("http://", "https://")):
            raise ValueError(
                f"ollama_url must start with http:// or https://, "
                f"got {self.ollama_url!r}"
            )
        parsed = urlparse(self.ollama_url)
        if not parsed.hostname:
            raise ValueError(
                f"ollama_url has an empty hostname after parsing: "
                f"{self.ollama_url!r}"
            )

        # Docker image validation (basic sanity)
        if not self.docker_image or not isinstance(self.docker_image, str):
            raise ValueError(
                f"docker_image must be a non‑empty string, "
                f"got {self.docker_image!r}"
            )
        if not _DOCKER_IMAGE_REGEX.match(self.docker_image):
            raise ValueError(
                f"docker_image does not look like a valid Docker image reference: "
                f"{self.docker_image!r}"
            )

    @staticmethod
    def _validate_timeout(field_name: str, value: Union[int, float]) -> None:
        """Validate a numeric timeout field.

        Args:
            field_name: Name of the field (for error message).
            value: The value to validate.

        Raises:
            TypeError: If value is not int or float.
            ValueError: If value is not positive finite, or out of allowed range.
        """
        if not isinstance(value, (int, float)):
            raise TypeError(
                f"{field_name} must be int or float, got {type(value).__name__}"
            )
        if value <= 0:
            raise ValueError(
                f"{field_name} must be positive, got {value!r}"
            )
        # Catches NaN or infinite values
        if not (value > 0):
            raise ValueError(
                f"{field_name} is not a valid finite number: {value!r}"
            )
        if value < MIN_TIMEOUT:
            raise ValueError(
                f"{field_name} is too low ({value}); minimum allowed is {MIN_TIMEOUT}"
            )
        if value > MAX_TIMEOUT:
            raise ValueError(
                f"{field_name} is too high ({value}); maximum allowed is {MAX_TIMEOUT}"
            )


def _load_yaml(path: Union[str, Path]) -> Dict[str, Any]:
    """Load a YAML configuration file safely.

    Args:
        path: Absolute or relative path to the YAML file.

    Returns:
        A dictionary with the loaded content. If the file does not exist or
        cannot be parsed, an empty dict is returned and a warning is logged.
    """
    path_obj = Path(path).resolve()
    try:
        # Use text mode explicitly; yaml.safe_load accepts TextIO
        with path_obj.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if data is None:
            return {}
        if not isinstance(data, dict):
            logger.warning(
                "YAML file %s is not a mapping (root is %s), ignoring.",
                path_obj,
                type(data).__name__,
            )
            return {}
        return dict(data)
    except FileNotFoundError:
        logger.info("Configuration file %s not found, using defaults.", path_obj)
    except yaml.YAMLError as exc:
        logger.warning("Error parsing YAML file %s: %s", path_obj, exc)
    except PermissionError:
        logger.warning("Permission denied reading %s, using defaults.", path_obj)
    except OSError as exc:
        logger.warning("I/O error reading %s: %s", path_obj, exc)
    return {}


def _apply_env_overrides(config: Dict[str, Any]) -> Dict[str, Any]:
    """Apply environment variable overrides to the configuration dictionary.

    The following environment variables are considered (case‑sensitive after the
    ``AIRECON_`` prefix):

    * ``AIRECON_OLLAMA_URL``        -> ``ollama_url``
    * ``AIRECON_DOCKER_IMAGE``      -> ``docker_image``
    * ``AIRECON_REQUEST_TIMEOUT``   -> ``request_timeout``
    * ``AIRECON_CONTAINER_TIMEOUT`` -> ``container_timeout``

    Numeric fields are converted to ``float``. If conversion fails the variable
    is silently ignored (a warning is logged). Empty string values are also
    ignored.

    Args:
        config: Existing configuration dictionary (possibly from YAML).

    Returns:
        The same dictionary updated with environment variable values.
    """
    # Mapping from environment variable suffix to (config key, expected type)
    env_to_config: Dict[str, tuple[str, type]] = {
        "OLLAMA_URL": ("ollama_url", str),
        "DOCKER_IMAGE": ("docker_image", str),
        "REQUEST_TIMEOUT": ("request_timeout", float),
        "CONTAINER_TIMEOUT": ("container_timeout", float),
    }

    for env_suffix, (key, target_type) in env_to_config.items():
        env_var = f"AIRECON_{env_suffix}"
        value = os.environ.get(env_var)

        # Skip if not set or empty (after stripping)
        if value is None or (isinstance(value, str) and not value.strip()):
            continue

        # For numeric types, attempt conversion
        if target_type is float:
            try:
                numeric_value = float(value.strip())
            except (ValueError, TypeError) as exc:
                logger.warning(
                    "Environment variable %s has invalid value %r, ignoring. Error: %s",
                    env_var,
                    value,
                    exc,
                )
                continue
            config[key] = numeric_value
        else:
            # String values: store after stripping leading/trailing whitespace
            config[key] = value.strip()

    return config


def load_config(config_path: Optional[Union[str, Path]] = None) -> Config:
    """Load and return the AIRecon configuration.

    The loading order (lowest to highest priority) is:
        1. Hard‑coded defaults
        2. Values from YAML file (if exists and is valid)
        3. Environment variable overrides (``AIRECON_*``)

    Args:
        config_path: Path to a YAML configuration file. If ``None``, the
            default path ``airecon.yaml`` in the current working directory
            is used.

    Returns:
        A ``Config`` instance with all fields validated.

    Raises:
        ValueError: If the final configuration fails validation.
    """
    if config_path is None:
        config_path = DEFAULT_CONFIG_PATH

    # Start with an empty dict; defaults come from Config dataclass defaults
    config_data: Dict[str, Any] = {}

    # Step 1: YAML file
    yaml_data = _load_yaml(config_path)
    if yaml_data:
        config_data.update(yaml_data)

    # Step 2: Environment overrides (highest priority)
    config_data = _apply_env_overrides(config_data)

    # Merge with defaults: only override keys that appear in the data
    final_config = {
        "ollama_url": config_data.get("ollama_url", DEFAULT_OLLAMA_URL),
        "docker_image": config_data.get("docker_image", DEFAULT_DOCKER_IMAGE),
        "request_timeout": config_data.get("request_timeout", DEFAULT_REQUEST_TIMEOUT),
        "container_timeout": config_data.get("container_timeout", DEFAULT_CONTAINER_TIMEOUT),
        "config_path": str(Path(config_path).resolve()) if Path(config_path).exists() else None,
    }

    logger.debug(
        "Final configuration before validation: %s",
        {k: v for k, v in final_config.items() if k != "ollama_url"},  # omit sensitive? not really but keep log clean
    )

    return Config(**final_config)