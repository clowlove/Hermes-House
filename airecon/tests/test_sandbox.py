"""
Tests for the Docker sandbox manager module.

These tests mock the docker-py library to verify correct lifecycle management
of Kali Linux containers, command execution, and error handling.
"""

from unittest.mock import MagicMock, PropertyMock, patch

import pytest
from docker.errors import DockerException, NotFound

from airecon.sandbox import SandboxManager


@pytest.fixture
def mock_docker_client():
    """Return a MagicMock simulating a docker DockerClient."""
    client = MagicMock()
    # Simulate default container and exec result
    container = MagicMock()
    container.id = "abc123"
    container.short_id = "abc"
    container.status = "created"
    client.containers.create.return_value = container
    client.containers.get.return_value = container
    return client


@pytest.fixture
def sandbox_manager(mock_docker_client):
    """Return a SandboxManager instance with a mocked Docker client."""
    with patch("airecon.sandbox.docker.from_env", return_value=mock_docker_client):
        manager = SandboxManager(
            image="kalilinux/kali-rolling:latest",
            container_name="test-sandbox",
            memory_limit="512m",
        )
        yield manager


class TestSandboxManager:
    """Test suite for SandboxManager."""

    def test_initialization(self, sandbox_manager):
        """Verify that SandboxManager initializes with correct attributes."""
        assert sandbox_manager.image == "kalilinux/kali-rolling:latest"
        assert sandbox_manager.container_name == "test-sandbox"
        assert sandbox_manager.memory_limit == "512m"
        assert sandbox_manager.client is not None
        assert sandbox_manager.container is None

    def test_create_container_success(self, sandbox_manager, mock_docker_client):
        """Test creating a container successfully."""
        container = sandbox_manager.create_container(
            command="sleep infinity", detach=True
        )
        mock_docker_client.containers.create.assert_called_once_with(
            image="kalilinux/kali-rolling:latest",
            command="sleep infinity",
            detach=True,
            name="test-sandbox",
            mem_limit="512m",
            tty=True,
            stdin_open=True,
        )
        assert container is not None
        assert container.id == "abc123"
        assert sandbox_manager.container == container

    def test_create_container_failure(self, sandbox_manager, mock_docker_client):
        """Test that DockerException is propagated when container creation fails."""
        mock_docker_client.containers.create.side_effect = DockerException(
            "Image not found"
        )
        with pytest.raises(DockerException, match="Image not found"):
            sandbox_manager.create_container()

    def test_execute_command_success(self, sandbox_manager):
        """Test running a command inside the container."""
        # Simulate a running container
        container_mock = MagicMock()
        container_mock.exec_run.return_value = (0, b"nmap output\n")
        sandbox_manager.container = container_mock

        exit_code, output = sandbox_manager.execute_command(
            "nmap -sV 127.0.0.1"
        )
        container_mock.exec_run.assert_called_once_with(
            cmd="nmap -sV 127.0.0.1", stdout=True, stderr=True, stream=False
        )
        assert exit_code == 0
        assert output == "nmap output\n"

    def test_execute_command_without_container(self, sandbox_manager):
        """Test that executing a command without a container raises an error."""
        sandbox_manager.container = None
        with pytest.raises(RuntimeError, match="No active container"):
            sandbox_manager.execute_command("ls")

    def test_execute_command_failure(self, sandbox_manager):
        """Test that command failure returns non-zero exit code."""
        container_mock = MagicMock()
        container_mock.exec_run.return_value = (1, b"error: permission denied\n")
        sandbox_manager.container = container_mock

        exit_code, output = sandbox_manager.execute_command("id")
        assert exit_code != 0
        assert "error" in output

    def test_cleanup_removes_container(self, sandbox_manager):
        """Test that cleanup removes and discards the container reference."""
        container_mock = MagicMock()
        sandbox_manager.container = container_mock

        sandbox_manager.cleanup()
        container_mock.remove.assert_called_once_with(force=True)
        assert sandbox_manager.container is None

    def test_cleanup_does_nothing_if_no_container(self, sandbox_manager):
        """Test cleanup gracefully handles no container."""
        sandbox_manager.container = None
        sandbox_manager.cleanup()  # Should not raise

    def test_cleanup_handles_not_found_error(self, sandbox_manager):
        """Test that cleanup ignores NotFound error (container already gone)."""
        container_mock = MagicMock()
        container_mock.remove.side_effect = NotFound("container not found")
        sandbox_manager.container = container_mock

        sandbox_manager.cleanup()
        assert sandbox_manager.container is None  # still cleared

    def test_get_container_returns_container(self, sandbox_manager, mock_docker_client):
        """Test retrieving an existing container by name."""
        mock_docker_client.containers.get.return_value = MagicMock()
        container = sandbox_manager.get_container("existing-sandbox")
        mock_docker_client.containers.get.assert_called_once_with("existing-sandbox")
        assert container is not None

    def test_get_container_not_found_returns_none(
        self, sandbox_manager, mock_docker_client
    ):
        """Test that get_container returns None when container does not exist."""
        mock_docker_client.containers.get.side_effect = NotFound("not found")
        container = sandbox_manager.get_container("nonexistent")
        assert container is None

    def test_docker_connection_failure(self):
        """Test that SandboxManager raises an error if Docker is unavailable."""
        with patch(
            "airecon.sandbox.docker.from_env",
            side_effect=DockerException("Docker not running"),
        ):
            with pytest.raises(DockerException, match="Docker not running"):
                SandboxManager()

    def test_resource_limits_passed_to_create(
        self, sandbox_manager, mock_docker_client
    ):
        """Verify that memory and CPU limits are passed to Docker."""
        # Create a new manager with custom limits
        with patch("airecon.sandbox.docker.from_env", return_value=mock_docker_client):
            manager = SandboxManager(
                image="kalilinux/kali-rolling:latest",
                container_name="sandbox-limited",
                memory_limit="1g",
                cpu_quota=50000,
            )
            manager.create_container()
            mock_docker_client.containers.create.assert_called_with(
                image="kalilinux/kali-rolling:latest",
                command="sleep infinity",
                detach=True,
                name="sandbox-limited",
                mem_limit="1g",
                cpu_quota=50000,
                tty=True,
                stdin_open=True,
            )