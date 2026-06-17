"""
airecon/core/sandbox.py

Production-grade Docker sandbox manager for AIRecon.
Manages container lifecycle: create, exec commands, file transfer, cleanup.
Uses docker-py with async wrappers for integration with asyncio-based orchestrator.

Security: Input validation prevents path traversal and command injection.
Performance: Uses asyncio.to_thread for all blocking Docker API calls.
Logging: Structured logging with appropriate levels.
Type Safety: Full type annotations throughout.
"""

import asyncio
import logging
import os
import re
import shlex
import tarfile
import tempfile
import uuid
from contextlib import asynccontextmanager
from io import BytesIO
from pathlib import Path
from types import TracebackType
from typing import (
    Any,
    AsyncIterator,
    Dict,
    Iterator,
    List,
    Optional,
    Sequence,
    Tuple,
    Type,
    Union,
    final,
)

import docker
from docker.errors import APIError, DockerException, ImageNotFound, NotFound
from docker.models.containers import Container
from docker.types import Mount as DockerMount

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Custom exceptions (hierarchical, specific)
# ---------------------------------------------------------------------------

class DockerSandboxError(Exception):
    """Base exception for all Docker sandbox operations."""


class ImageError(DockerSandboxError):
    """Raised when image operations (pull/get) fail."""


class ContainerCreationError(DockerSandboxError):
    """Raised when container creation or start fails."""


class ContainerExecutionError(DockerSandboxError):
    """Raised when command execution inside container fails."""


class FileRetrievalError(DockerSandboxError):
    """Raised when file retrieval from container fails."""


class FileTransferError(DockerSandboxError):
    """Raised when file transfer to container fails."""


class ContainerNotRunningError(DockerSandboxError):
    """Raised when an operation requires a running container but none exists."""


class InvalidInputError(DockerSandboxError):
    """Raised when input validation fails."""


class ContainerCleanupError(DockerSandboxError):
    """Raised when container cleanup fails."""


class TimeoutError(DockerSandboxError):
    """Raised when an operation times out."""


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_DEFAULT_IMAGE: str = "kalilinux/kali-rolling:latest"
_DEFAULT_CONTAINER_PREFIX: str = "airecon-sandbox-"
_DEFAULT_TIMEOUT: int = 300
_EXEC_CMD_ENCODING: str = "utf-8"
_VALID_COMMAND_CHARS: str = " \t\n\r\f\v" + "".join(
    chr(i) for i in range(0x20, 0x7E + 1)
)
_MAX_COMMAND_LENGTH: int = 4096
_MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100 MB
_MAX_FILE_PATH_LENGTH: int = 1024
_INTERNAL_CONTAINER_WORK_DIR: str = "/home/airecon"
_DEFAULT_MEMORY_LIMIT: str = "2g"
_DEFAULT_CPU_LIMIT: int = 2
_MAX_MOUNTS: int = 50
_MAX_ENV_VARS: int = 100
_MAX_CAPABILITIES: int = 20
_DOCKER_CLIENT_TIMEOUT: int = 60
_RETRY_MAX_ATTEMPTS: int = 3
_RETRY_BASE_DELAY: float = 1.0


# ---------------------------------------------------------------------------
# Type aliases
# ---------------------------------------------------------------------------

MountList = List[Dict[str, Any]]
CapAddList = List[str]
EnvList = List[Dict[str, str]]
PortBindings = Dict[str, Any]
ExecResult = Tuple[int, bytes, bytes]  # exit_code, stdout, stderr

# Regex for container name validation
_CONTAINER_NAME_PATTERN: re.Pattern = re.compile(r'^[a-zA-Z0-9][a-zA-Z0-9_.-]*$')
# Regex for valid file path (basic safety)
_SAFE_FILE_PATH_PATTERN: re.Pattern = re.compile(r'^[a-zA-Z0-9_./-]+$')


# ---------------------------------------------------------------------------
# Module-level utility functions (all with complete validation)
# ---------------------------------------------------------------------------

def _validate_command(command: Union[str, Sequence[str]]) -> None:
    """
    Validate a command string or list for safety and length.

    Args:
        command: Command string or sequence of arguments.

    Raises:
        InvalidInputError: If command is empty, too long, or contains invalid characters.
    """
    if isinstance(command, str):
        if not command:
            raise InvalidInputError("Command must be a non-empty string.")
        if len(command) > _MAX_COMMAND_LENGTH:
            raise InvalidInputError(
                f"Command length {len(command)} exceeds maximum {_MAX_COMMAND_LENGTH}."
            )
        # Check for control characters except whitespace
        invalid = set(command) - set(_VALID_COMMAND_CHARS)
        if invalid:
            raise InvalidInputError(
                f"Command contains invalid characters: {''.join(invalid)!r}"
            )
    elif isinstance(command, (list, tuple)):
        if not command:
            raise InvalidInputError("Command must be a non-empty sequence of strings.")
        for i, arg in enumerate(command):
            if not isinstance(arg, str) or not arg:
                raise InvalidInputError(
                    f"Command argument at index {i} must be a non-empty string."
                )
            if len(arg) > _MAX_COMMAND_LENGTH:
                raise InvalidInputError(
                    f"Command argument at index {i} length {len(arg)} exceeds maximum."
                )
            invalid = set(arg) - set(_VALID_COMMAND_CHARS)
            if invalid:
                raise InvalidInputError(
                    f"Command argument at index {i} contains invalid characters: "
                    f"{''.join(invalid)!r}"
                )
    else:
        raise InvalidInputError(
            "Command must be a string or a sequence of strings."
        )


def _validate_container_name(name: str) -> None:
    """
    Validate a Docker container name.

    Args:
        name: Container name.

    Raises:
        InvalidInputError: If name is empty or invalid pattern.
    """
    if not name or not isinstance(name, str):
        raise InvalidInputError("Container name must be a non-empty string.")
    if not _CONTAINER_NAME_PATTERN.match(name):
        raise InvalidInputError(
            f"Container name {name!r} contains invalid characters. "
            "Allowed: alphanumeric, underscore, dot, hyphen; must start with alphanumeric."
        )


def _validate_mounts(mounts: Optional[MountList]) -> None:
    """
    Validate a list of mount dictionaries.

    Args:
        mounts: List of mount dicts (each with source, target, type).

    Raises:
        InvalidInputError: If any mount is invalid or too many mounts.
    """
    if mounts is None:
        return
    if not isinstance(mounts, list):
        raise InvalidInputError("Mounts must be a list.")
    if len(mounts) > _MAX_MOUNTS:
        raise InvalidInputError(f"Mount count {len(mounts)} exceeds maximum {_MAX_MOUNTS}.")
    required_keys = {"source", "target", "type"}
    for i, mount in enumerate(mounts):
        if not isinstance(mount, dict):
            raise InvalidInputError(f"Mount at index {i} must be a dict, got {type(mount).__name__}.")
        missing = required_keys - set(mount.keys())
        if missing:
            raise InvalidInputError(f"Mount at index {i} missing required keys: {missing}.")
        source = mount.get("source")
        target = mount.get("target")
        mtype = mount.get("type")
        if not isinstance(source, str) or not isinstance(target, str) or not isinstance(mtype, str):
            raise InvalidInputError(
                f"Mount at index {i} 'source', 'target', 'type' must be strings."
            )
        if not os.path.isabs(source):
            raise InvalidInputError(f"Mount at index {i} source must be absolute path: {source!r}")
        if not target.startswith("/"):
            raise InvalidInputError(f"Mount at index {i} target must be absolute path: {target!r}")
        if mtype not in ("bind", "volume", "tmpfs"):
            raise InvalidInputError(
                f"Mount at index {i} type must be 'bind', 'volume', or 'tmpfs', got {mtype!r}"
            )
        # Validate additional optional keys if present
        optional_keys = {"read_only", "consistency", "propagation"}
        for key in mount:
            if key not in required_keys and key not in optional_keys:
                logger.warning(f"Mount at index {i} has unknown key: {key!r}")
        # read_only must be bool if present
        if "read_only" in mount and not isinstance(mount["read_only"], bool):
            raise InvalidInputError(f"Mount at index {i} 'read_only' must be bool, got {type(mount['read_only']).__name__}")


def _validate_env_vars(env_vars: Optional[EnvList]) -> None:
    """
    Validate a list of environment variable dictionaries.

    Args:
        env_vars: List of dicts with keys 'key' and 'value'.

    Raises:
        InvalidInputError: If invalid structure or too many vars.
    """
    if env_vars is None:
        return
    if not isinstance(env_vars, list):
        raise InvalidInputError("Environment variables must be a list.")
    if len(env_vars) > _MAX_ENV_VARS:
        raise InvalidInputError(f"Too many environment variables ({len(env_vars)} > {_MAX_ENV_VARS}).")
    for i, env in enumerate(env_vars):
        if not isinstance(env, dict):
            raise InvalidInputError(f"Env var at index {i} must be a dict, got {type(env).__name__}.")
        if "key" not in env or "value" not in env:
            raise InvalidInputError(f"Env var at index {i} must have 'key' and 'value' keys.")
        key = env["key"]
        value = env["value"]
        if not isinstance(key, str) or not key:
            raise InvalidInputError(f"Env var at index {i} 'key' must be a non-empty string.")
        if not isinstance(value, str):
            raise InvalidInputError(f"Env var at index {i} 'value' must be a string.")
        # Docker env var key must be alphanumeric and underscore only, start with letter
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', key):
            raise InvalidInputError(
                f"Env var at index {i} key {key!r} is not a valid Docker environment variable name."
            )


def _validate_file_path(path: str) -> None:
    """
    Validate a file path inside the container for safety.

    Args:
        path: Absolute path string.

    Raises:
        InvalidInputError: If path is unsafe or too long.
    """
    if not path or not isinstance(path, str):
        raise InvalidInputError("File path must be a non-empty string.")
    if len(path) > _MAX_FILE_PATH_LENGTH:
        raise InvalidInputError(
            f"File path length {len(path)} exceeds maximum {_MAX_FILE_PATH_LENGTH}."
        )
    if not path.startswith("/"):
        raise InvalidInputError(f"File path must be absolute, got {path!r}")
    # Reject path traversal with '..'
    if ".." in path.split("/"):
        raise InvalidInputError(f"File path must not contain '..' components: {path!r}")
    # Ensure only safe characters
    if not _SAFE_FILE_PATH_PATTERN.match(path.lstrip("/")):
        raise InvalidInputError(f"File path contains invalid characters: {path!r}")


def _validate_file_content(data: bytes) -> None:
    """
    Validate byte content for file transfer.

    Args:
        data: Byte content.

    Raises:
        InvalidInputError: If content exceeds maximum size.
    """
    if not isinstance(data, bytes):
        raise InvalidInputError("File content must be bytes.")
    if len(data) > _MAX_FILE_SIZE:
        raise InvalidInputError(
            f"File content size {len(data)} exceeds maximum {_MAX_FILE_SIZE} bytes."
        )


def _validate_image_name(image: str) -> None:
    """
    Validate Docker image name format (basic).

    Args:
        image: Image name string.

    Raises:
        InvalidInputError: If image name is invalid.
    """
    if not image or not isinstance(image, str):
        raise InvalidInputError("Image name must be a non-empty string.")
    # Basic validation: must contain at least one slash or colon, or be a simple name
    # Docker image names: [registry/][namespace/]repository[:tag]
    if len(image) > 256:
        raise InvalidInputError(f"Image name too long ({len(image)} > 256).")
    # Disallow control characters
    if any(ord(c) < 32 for c in image):
        raise InvalidInputError("Image name contains control characters.")


def _retry_async(max_attempts: int = _RETRY_MAX_ATTEMPTS, base_delay: float = _RETRY_BASE_DELAY):
    """
    Decorator for async functions to retry on transient Docker API errors.

    Args:
        max_attempts: Maximum number of retry attempts.
        base_delay: Base delay in seconds (exponential backoff).

    Returns:
        Decorated async function.
    """
    import functools

    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception: Optional[Exception] = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except (APIError, DockerException, asyncio.TimeoutError) as e:
                    last_exception = e
                    if attempt < max_attempts:
                        delay = base_delay * (2 ** (attempt - 1))
                        logger.warning(
                            "Retrying %s after attempt %d/%d due to %s. Waiting %.2fs",
                            func.__name__,
                            attempt,
                            max_attempts,
                            e,
                            delay
                        )
                        await asyncio.sleep(delay)
                    else:
                        logger.error(
                            "%s failed after %d attempts: %s",
                            func.__name__,
                            max_attempts,
                            e
                        )
            raise last_exception  # type: ignore[misc]
        return wrapper
    return decorator


# ---------------------------------------------------------------------------
# Helper to create DockerMount from dict
# ---------------------------------------------------------------------------

def _mount_from_dict(mount_dict: Dict[str, Any]) -> DockerMount:
    """
    Convert a validated mount dict to a Docker Mount object.

    Args:
        mount_dict: Dict with keys source, target, type.

    Returns:
        DockerMount instance.
    """
    return DockerMount(
        target=mount_dict["target"],
        source=mount_dict["source"],
        type=mount_dict["type"],
        read_only=mount_dict.get("read_only", False),
        consistency=mount_dict.get("consistency"),
        propagation=mount_dict.get("propagation"),
    )


# ---------------------------------------------------------------------------
# Main Sandbox Class
# ---------------------------------------------------------------------------

@final
class DockerSandbox:
    """
    Production-grade Docker sandbox for running security assessments.

    Automates container lifecycle: creation, command execution, file transfer,
    and cleanup. Designed to work with asyncio-based orchestration.

    Usage:
        sandbox = DockerSandbox()
        async with sandbox:
            sandbox.exec("nmap -sV target.com")

    Attributes:
        container_id: Unique container ID (set after creation).
        container: Docker Container object (available after creation).
        image: Docker image used.
        prefix: Container name prefix.
        timeout: Default command execution timeout.
        memory_limit: Memory limit for container.
        cpu_limit: CPU limit for container.
    """

    def __init__(
        self,
        image: str = _DEFAULT_IMAGE,
        prefix: str = _DEFAULT_CONTAINER_PREFIX,
        timeout: int = _DEFAULT_TIMEOUT,
        memory_limit: str = _DEFAULT_MEMORY_LIMIT,
        cpu_limit: int = _DEFAULT_CPU_LIMIT,
        work_dir: str = _INTERNAL_CONTAINER_WORK_DIR,
        docker_client: Optional[docker.DockerClient] = None,
        pull_policy: str = "missing",
    ) -> None:
        """
        Initialize the Docker Sandbox.

        Args:
            image: Docker image name (default: kalilinux/kali-rolling:latest).
            prefix: Container name prefix for auto-generation.
            timeout: Default execution timeout in seconds.
            memory_limit: Memory limit string (e.g., "2g", "512m").
            cpu_limit: CPU limit as integer (number of CPUs).
            work_dir: Working directory inside container.
            docker_client: Optional existing Docker client instance.
            pull_policy: Image pull policy: "always", "missing", "never".

        Raises:
            InvalidInputError: If any parameter is invalid.
        """
        _validate_image_name(image)
        _validate_container_name(prefix)  # prefix must be valid container name start
        if not isinstance(timeout, int) or timeout <= 0:
            raise InvalidInputError(f"Timeout must be positive int, got {timeout!r}")
        if not isinstance(memory_limit, str) or not memory_limit:
            raise InvalidInputError(f"Memory limit must be non-empty string, got {memory_limit!r}")
        if not isinstance(cpu_limit, int) or cpu_limit < 1:
            raise InvalidInputError(f"CPU limit must be positive int, got {cpu_limit!r}")
        if not isinstance(work_dir, str) or not work_dir.startswith("/"):
            raise InvalidInputError(f"Work dir must be absolute path, got {work_dir!r}")
        if pull_policy not in ("always", "missing", "never"):
            raise InvalidInputError(f"Pull policy must be one of 'always', 'missing', 'never', got {pull_policy!r}")

        self._image: str = image
        self._prefix: str = prefix
        self._timeout: int = timeout
        self._memory_limit: str = memory_limit
        self._cpu_limit: int = cpu_limit
        self._work_dir: str = work_dir
        self._pull_policy: str = pull_policy

        self._docker_client: Optional[docker.DockerClient] = docker_client
        self._own_client: bool = docker_client is None

        self._container: Optional[Container] = None
        self._container_name: Optional[str] = None
        self._container_id: Optional[str] = None
        self._closed: bool = False

        # Logger with component context
        self._logger = logging.getLogger(f"{__name__}.{id(self)}")
        self._logger.setLevel(logging.DEBUG)  # Allow propagation to root

    # -----------------------------------------------------------------------
    # Properties
    # -----------------------------------------------------------------------

    @property
    def container(self) -> Optional[Container]:
        """Docker Container object, None if not created."""
        return self._container

    @property
    def container_id(self) -> Optional[str]:
        """Container short ID, None if not created."""
        return self._container_id

    @property
    def container_name(self) -> Optional[str]:
        """Container name, None if not created."""
        return self._container_name

    @property
    def is_running(self) -> bool:
        """Check if container exists and is running."""
        if self._container is None:
            return False
        try:
            self._container.reload()
            return self._container.status == "running"
        except (APIError, NotFound, DockerException):
            return False

    @property
    def image(self) -> str:
        """Docker image name."""
        return self._image

    @property
    def timeout(self) -> int:
        """Default execution timeout."""
        return self._timeout

    # -----------------------------------------------------------------------
    # Private helpers
    # -----------------------------------------------------------------------

    def _get_client(self) -> docker.DockerClient:
        """
        Get or create Docker client instance.

        Returns:
            DockerClient instance.

        Raises:
            DockerSandboxError: If connection fails.
        """
        if self._docker_client is None:
            try:
                self._docker_client = docker.from_env(timeout=_DOCKER_CLIENT_TIMEOUT)
                # Test connection
                self._docker_client.ping()
            except DockerException as e:
                raise DockerSandboxError(f"Failed to connect to Docker daemon: {e}") from e
        return self._docker_client

    async def _ensure_image(self) -> None:
        """
        Ensure the Docker image is pulled according to policy.

        Raises:
            ImageError: If image cannot be obtained.
        """
        client = self._get_client()
        loop = asyncio.get_running_loop()

        try:
            # Check if image exists locally
            try:
                image = await loop.run_in_executor(
                    None, lambda: client.images.get(self._image)
                )
                if self._pull_policy == "always":
                    self._logger.info("Pull policy 'always' – pulling image %s", self._image)
                    await loop.run_in_executor(
                        None, lambda: client.images.pull(self._image)
                    )
                elif self._pull_policy == "missing":
                    self._logger.info("Image %s already exists, skipping pull", self._image)
                # 'never' and exists -> ok
            except ImageNotFound:
                if self._pull_policy == "never":
                    raise ImageError(
                        f"Image {self._image} not found locally and pull_policy is 'never'"
                    )
                self._logger.info("Pulling image %s (first time)", self._image)
                await loop.run_in_executor(
                    None, lambda: client.images.pull(self._image)
                )
        except DockerException as e:
            raise ImageError(f"Failed to ensure image {self._image}: {e}") from e

    def _generate_container_name(self) -> str:
        """Generate a unique container name using prefix and UUID."""
        return f"{self._prefix}{uuid.uuid4().hex[:12]}"

    # -----------------------------------------------------------------------
    # Public API
    # -----------------------------------------------------------------------

    @_retry_async()
    async def create(
        self,
        mounts: Optional[MountList] = None,
        env_vars: Optional[EnvList] = None,
        cap_add: Optional[CapAddList] = None,
        port_bindings: Optional[PortBindings] = None,
        extra_hosts: Optional[Dict[str, str]] = None,
        network_mode: Optional[str] = None,
        command: Optional[Union[str, List[str]]] = None,
        auto_remove: bool = True,
        privileged: bool = False,
        name: Optional[str] = None,
    ) -> Container:
        """
        Create and start the sandbox container.

        Args:
            mounts: List of mount dicts (validated).
            env_vars: List of environment variable dicts (validated).
            cap_add: List of Linux capabilities to add.
            port_bindings: Port binding mappings.
            extra_hosts: Extra host-to-IP mappings.
            network_mode: Docker network mode.
            command: Optional command to run instead of default.
            auto_remove: Whether to auto-remove container on stop.
            privileged: Run container in privileged mode (security warning).
            name: Explicit container name (must be valid). If None, auto-generated.

        Returns:
            Docker Container instance.

        Raises:
            InvalidInputError: If any argument is invalid.
            ContainerCreationError: If container creation fails.
        """
        if self._closed:
            raise DockerSandboxError("Sandbox is closed, cannot create new container.")
        if self._container is not None:
            raise ContainerCreationError("Container already exists. Use remove() first.")

        # Validate inputs
        _validate_mounts(mounts)
        _validate_env_vars(env_vars)
        if cap_add:
            if not isinstance(cap_add, list):
                raise InvalidInputError("cap_add must be a list of strings.")
            if len(cap_add) > _MAX_CAPABILITIES:
                raise InvalidInputError(f"Too many capabilities ({len(cap_add)} > {_MAX_CAPABILITIES}).")
            for cap in cap_add:
                if not isinstance(cap, str) or not cap:
                    raise InvalidInputError(f"Capability must be non-empty string, got {cap!r}")
        if command:
            _validate_command(command)
        if name:
            _validate_container_name(name)

        # Ensure image is available
        await self._ensure_image()

        client = self._get_client()
        container_name = name if name else self._generate_container_name()

        # Build Docker mounts
        docker_mounts: List[DockerMount] = []
        if mounts:
            for m in mounts:
                docker_mounts.append(_mount_from_dict(m))

        # Convert env_vars to list of "KEY=VALUE" strings
        environment: List[str] = []
        if env_vars:
            for env in env_vars:
                environment.append(f"{env['key']}={env['value']}")

        container_config: Dict[str, Any] = {
            "image": self._image,
            "command": command,
            "name": container_name,
            "detach": True,
            "tty": True,
            "stdin_open": True,  # Keep container alive for interactive use
            "working_dir": self._work_dir,
            "mem_limit": self._memory_limit,
            "cpu_period": 100000,
            "cpu_quota": self._cpu_limit * 100000,
            "privileged": privileged,
            "auto_remove": auto_remove,
            "mounts": docker_mounts if docker_mounts else None,
            "environment": environment if environment else None,
            "cap_add": cap_add,
            "ports": port_bindings,
            "extra_hosts": extra_hosts,
            "network_mode": network_mode,
            "hostname": "airecon-sandbox",
        }

        # Remove None values to avoid Docker API issues
        container_config = {k: v for k, v in container_config.items() if v is not None}

        loop = asyncio.get_running_loop()

        try:
            self._logger.info("Creating container '%s' from image %s", container_name, self._image)
            container = await loop.run_in_executor(
                None, lambda: client.containers.create(**container_config)
            )

            self._logger.info("Starting container '%s'", container_name)
            await loop.run_in_executor(None, container.start)

            # Reload to get full info
            await loop.run_in_executor(None, container.reload)

            self._container = container
            self._container_name = container_name
            self._container_id = container.short_id

            self._logger.info(
                "Sandbox container started: id=%s name=%s image=%s",
                self._container_id,
                container_name,
                self._image,
            )
            return container

        except (APIError, DockerException) as e:
            raise ContainerCreationError(f"Failed to create container: {e}") from e

    @_retry_async()
    async def exec_run(
        self,
        cmd: Union[str, Sequence[str]],
        timeout: Optional[int] = None,
        work_dir: Optional[str] = None,
        environment: Optional[Dict[str, str]] = None,
        user: Optional[str] = None,
        stream: bool = False,
    ) -> ExecResult:
        """
        Execute a command inside the sandbox container.

        Args:
            cmd: Command string or list of arguments.
            timeout: Execution timeout in seconds (default: self._timeout).
            work_dir: Working directory for the command.
            environment: Additional environment variables for this command.
            user: User to run command as (e.g., "root", "1000:1000").
            stream: If True, return async generator for streaming output (not yet implemented).

        Returns:
            Tuple of (exit_code, stdout_bytes, stderr_bytes).

        Raises:
            InvalidInputError: If command is invalid.
            ContainerNotRunningError: If container is not running.
            ContainerExecutionError: If execution fails.
        """
        _validate_command(cmd)

        if not self.is_running:
            raise ContainerNotRunningError("Container is not running. Call create() first.")

        # Build command as list if string
        if isinstance(cmd, str):
            cmd_list: List[str] = shlex.split(cmd)
        else:
            cmd_list = list(cmd)

        if timeout is None:
            timeout = self._timeout
        if not isinstance(timeout, int) or timeout <= 0:
            raise InvalidInputError(f"Timeout must be positive int, got {timeout!r}")

        exec_config: Dict[str, Any] = {
            "cmd": cmd_list,
            "stdout": True,
            "stderr": True,
            "stream": stream,
        }
        if work_dir:
            exec_config["workdir"] = work_dir
        if environment:
            exec_config["environment"] = environment
        if user:
            exec_config["user"] = user

        loop = asyncio.get_running_loop()

        try:
            self._logger.debug("Executing command: %s (timeout=%ds)", " ".join(cmd_list), timeout)
            exec_result = await asyncio.wait_for(
                loop.run_in_executor(
                    None,
                    lambda: self._container.exec_run(**exec_config),  # type: ignore[union-attr]
                ),
                timeout=timeout,
            )
            exit_code: int = exec_result.exit_code
            stdout: bytes = exec_result.output[0] if isinstance(exec_result.output, tuple) else exec_result.output
            # docker SDK returns (stdout, stderr) for exec_run if both streams are captured
            if isinstance(exec_result.output, tuple):
                stderr = exec_result.output[1]
            else:
                stderr = b""

            self._logger.info(
                "Command exit code: %d, stdout len: %d, stderr len: %d",
                exit_code,
                len(stdout),
                len(stderr),
            )
            return (exit_code, stdout, stderr)

        except asyncio.TimeoutError as e:
            raise TimeoutError(
                f"Command '{' '.join(cmd_list)}' timed out after {timeout}s."
            ) from e
        except (APIError, DockerException) as e:
            raise ContainerExecutionError(
                f"Failed to execute command: {' '.join(cmd_list)}: {e}"
            ) from e

    @_retry_async()
    async def get_file(self, path: str) -> bytes:
        """
        Retrieve a file from the container as bytes.

        Args:
            path: Absolute path inside container.

        Returns:
            File contents as bytes.

        Raises:
            InvalidInputError: If path is invalid.
            ContainerNotRunningError: If container is not running.
            FileRetrievalError: If file retrieval fails.
        """
        _validate_file_path(path)

        if not self.is_running:
            raise ContainerNotRunningError("Container is not running. Call create() first.")

        loop = asyncio.get_running_loop()
        temp_dir: Optional[tempfile.TemporaryDirectory] = None
        try:
            # Use get_archive to retrieve file as tar stream
            self._logger.debug("Retrieving file: %s", path)
            tar_stream, stat = await loop.run_in_executor(
                None,
                lambda: self._container.get_archive(path),  # type: ignore[union-attr]
            )

            # Read tar stream into bytes
            tar_bytes = b"".join(chunk for chunk in tar_stream)

            # Extract file from tar (handles both files and directories)
            tar_file = BytesIO(tar_bytes)
            with tarfile.open(fileobj=tar_file, mode="r") as tar:
                # Expecting only one file
                members = tar.getmembers()
                if not members:
                    raise FileRetrievalError(f"No files found in archive for {path!r}.")
                # Get the first member matching the exact path
                for member in members:
                    if member.name == path.lstrip("/"):
                        content = tar.extractfile(member)
                        if content is None:
                            raise FileRetrievalError(f"Failed to extract {path!r} from archive.")
                        data = content.read()
                        return data
                # Fallback: return tar itself? But we need the file content.
                # Usually the archive contains the file directly.
                # If not found, raise error.
                raise FileRetrievalError(
                    f"File {path!r} not found in tar archive. Members: {[m.name for m in members]}"
                )

        except NotFound as e:
            raise FileRetrievalError(f"File {path!r} not found in container: {e}") from e
        except (APIError, DockerException) as e:
            raise FileRetrievalError(f"Failed to retrieve file {path!r}: {e}") from e
        except Exception as e:
            raise FileRetrievalError(f"Unexpected error during file retrieval: {e}") from e
        finally:
            if temp_dir:
                temp_dir.cleanup()

    @_retry_async()
    async def put_file(self, path: str, data: bytes, mode: str = "644") -> None:
        """
        Upload a file to the container.

        Uses tar archive to transfer file.

        Args:
            path: Absolute destination path inside container.
            data: File content as bytes.
            mode: File permissions string (e.g., "644", "755").

        Raises:
            InvalidInputError: If path or data is invalid.
            ContainerNotRunningError: If container is not running.
            FileTransferError: If file transfer fails.
        """
        _validate_file_path(path)
        _validate_file_content(data)
        if not isinstance(mode, str) or not mode.isdigit() or len(mode) < 3:
            raise InvalidInputError(f"Mode must be a 3-4 digit octal string, got {mode!r}.")

        if not self.is_running:
            raise ContainerNotRunningError("Container is not running. Call create() first.")

        # Create tar archive with the file
        tar_buffer = BytesIO()
        try:
            with tarfile.open(fileobj=tar_buffer, mode="w") as tar:
                tarinfo = tarfile.TarInfo(name=path.lstrip("/"))
                tarinfo.size = len(data)
                tarinfo.mode = int(mode, 8)
                tar.addfile(tarinfo, BytesIO(data))

            tar_buffer.seek(0)
            tar_bytes = tar_buffer.getvalue()

            loop = asyncio.get_running_loop()
            self._logger.debug("Uploading file: %s (%d bytes)", path, len(data))
            success = await loop.run_in_executor(
                None,
                lambda: self._container.put_archive(  # type: ignore[union-attr]
                    "/",  # root, because archive paths are relative to target
                    tar_bytes,
                ),
            )
            if not success:
                raise FileTransferError(f"put_archive returned failure for {path!r}.")
            self._logger.info("File uploaded successfully: %s", path)

        except (APIError, DockerException) as e:
            raise FileTransferError(f"Failed to upload file {path!r}: {e}") from e
        except OSError as e:
            raise FileTransferError(f"Temporary file error: {e}") from e

    @_retry_async()
    async def exec_command_with_stdin(
        self,
        cmd: Union[str, Sequence[str]],
        stdin_data: bytes,
        timeout: Optional[int] = None,
    ) -> ExecResult:
        """
        Execute a command with stdin input (non-streaming).

        Args:
            cmd: Command string or list.
            stdin_data: Bytes to pipe to stdin.
            timeout: Execution timeout.

        Returns:
            Tuple (exit_code, stdout, stderr).

        Raises:
            InvalidInputError: If command invalid or stdin too large.
            ContainerNotRunningError: If container not running.
            ContainerExecutionError: If execution fails.
        """
        _validate_command(cmd)
        if not isinstance(stdin_data, bytes):
            raise InvalidInputError("stdin_data must be bytes.")
        if len(stdin_data) > 1024 * 1024:  # 1 MB limit for stdin
            raise InvalidInputError("stdin_data exceeds 1 MB limit.")

        if not self.is_running:
            raise ContainerNotRunningError("Container is not running. Call create() first.")

        if isinstance(cmd, str):
            cmd_list = shlex.split(cmd)
        else:
            cmd_list = list(cmd)

        timeout = timeout or self._timeout

        loop = asyncio.get_running_loop()

        try:
            exec_id = await loop.run_in_executor(
                None,
                lambda: self._container.exec_create(  # type: ignore[union-attr]
                    cmd=cmd_list,
                    stdin=True,
                    stdout=True,
                    stderr=True,
                ),
            )
            exec_output = await loop.run_in_executor(
                None,
                lambda: self._container.exec_start(  # type: ignore[union-attr]
                    exec_id=exec_id,
                    stdin=stdin_data,
                    stream=False,
                    detach=False,
                    tty=False,
                ),
            )
            # exec_start returns a tuple (exit_code, output) if both streams captured
            if isinstance(exec_output, tuple):
                exit_code, output = exec_output
                stdout = output[0] if isinstance(output, tuple) else output
                stderr = output[1] if isinstance(output, tuple) else b""
            else:
                # Only stdout
                exit_code = 0  # might not be accurate
                stdout = exec_output
                stderr = b""
                # Retrieve exit code via exec_inspect
                inspect = await loop.run_in_executor(
                    None,
                    lambda: self._container.exec_inspect(exec_id),  # type: ignore[union-attr]
                )
                exit_code = inspect["ExitCode"]

            return (exit_code, stdout, stderr)

        except asyncio.TimeoutError:
            raise TimeoutError(f"Command with stdin timed out after {timeout}s.")
        except (APIError, DockerException) as e:
            raise ContainerExecutionError(f"Failed to run command with stdin: {e}") from e

    @_retry_async()
    async def stop(self, timeout: int = 10) -> None:
        """
        Stop the sandbox container.

        Args:
            timeout: Seconds to wait before force-killing.

        Raises:
            ContainerCleanupError: If stop fails.
        """
        if self._container is None:
            self._logger.warning("No container to stop.")
            return

        loop = asyncio.get_running_loop()
        try:
            self._logger.info("Stopping container '%s' (timeout=%d)", self._container_name, timeout)
            await loop.run_in_executor(
                None,
                lambda: self._container.stop(timeout=timeout),  # type: ignore[union-attr]
            )
            self._logger.info("Container stopped.")
        except (APIError, DockerException, NotFound) as e:
            raise ContainerCleanupError(f"Failed to stop container: {e}") from e

    @_retry_async()
    async def remove(self, force: bool = True, v: bool = False) -> None:
        """
        Remove the sandbox container.

        Args:
            force: Force removal even if running.
            v: Remove associated volumes.

        Raises:
            ContainerCleanupError: If removal fails.
        """
        if self._container is None:
            self._logger.warning("No container to remove.")
            return

        loop = asyncio.get_running_loop()
        try:
            self._logger.info("Removing container '%s' (force=%s, v=%s)", self._container_name, force, v)
            await loop.run_in_executor(
                None,
                lambda: self._container.remove(force=force, v=v),  # type: ignore[union-attr]
            )
            self._container = None
            self._container_id = None
            self._container_name = None
            self._logger.info("Container removed.")
        except (APIError, DockerException, NotFound) as e:
            raise ContainerCleanupError(f"Failed to remove container: {e}") from e

    async def cleanup(self) -> None:
        """
        Stop and remove the container if it exists. Safe to call multiple times.
        """
        if self._container is not None:
            try:
                if self.is_running:
                    await self.stop()
                await self.remove(force=True)
            except (ContainerCleanupError, DockerSandboxError) as e:
                self._logger.error("Cleanup error: %s", e)
        else:
            self._logger.debug("Cleanup: nothing to do.")

    async def close(self) -> None:
        """
        Close the sandbox, release resources.
        """
        await self.cleanup()
        if self._own_client and self._docker_client is not None:
            try:
                self._docker_client.close()
                self._logger.debug("Docker client closed.")
            except DockerException as e:
                self._logger.error("Error closing Docker client: %s", e)
        self._closed = True

    async def __aenter__(self) -> "DockerSandbox":
        """Async context manager entry - create sandbox."""
        await self.create()
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        """Async context manager exit - clean up."""
        await self.close()

    def __del__(self) -> None:
        """Destructor - attempt cleanup if not explicitly closed."""
        if self._container is not None and not self._closed:
            try:
                # Attempt synchronous cleanup in destructor (best effort)
                import atexit
                atexit.register(self._force_cleanup)
            except Exception:
                pass

    def _force_cleanup(self) -> None:
        """Synchronous cleanup for destructor (best effort)."""
        try:
            if self._container is not None:
                try:
                    self._container.stop(timeout=5)
                except Exception:
                    pass
                try:
                    self._container.remove(force=True)
                except Exception:
                    pass
        except Exception:
            pass
        if self._own_client and self._docker_client is not None:
            try:
                self._docker_client.close()
            except Exception:
                pass

    def __repr__(self) -> str:
        return (
            f"DockerSandbox(image={self._image!r}, container={self._container_name!r}, "
            f"running={self.is_running}, closed={self._closed})"
        )