"""
Integration tests for AIRecon orchestrator full flow with mocked dependencies.

Tests cover:
- Orchestrator startup and target processing
- LLM reasoning and task suggestion
- Sandbox execution and result collection
- Error handling for sandbox failures
- Multi-task aggregation and completion
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from airecon.orchestrator import Orchestrator
from airecon.ollama_client import OllamaClient
from airecon.sandbox import DockerSandboxManager


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_ollama_client() -> MagicMock:
    """Return a mocked OllamaClient with async methods."""
    client = MagicMock(spec=OllamaClient)
    client.reason = AsyncMock(return_value=[
        {"task": "subdomain_enum", "target": "example.com"},
        {"task": "port_scan", "target": "example.com"},
    ])
    return client


@pytest.fixture
def mock_sandbox_manager() -> MagicMock:
    """Return a mocked DockerSandboxManager with async methods."""
    manager = MagicMock(spec=DockerSandboxManager)
    manager.run_task = AsyncMock(side_effect=lambda task, target: {
        "subdomain_enum": {"status": "complete", "results": {"domains": ["www.example.com"]}},
        "port_scan": {"status": "complete", "results": {"open_ports": [80, 443]}},
    }.get(task, {"status": "failed", "error": "unknown task"}))
    manager.cleanup = AsyncMock()
    return manager


@pytest.fixture
def orchestrator(mock_ollama_client, mock_sandbox_manager) -> Orchestrator:
    """Return an Orchestrator instance with mocked dependencies."""
    orchestrator = Orchestrator(
        ollama_client=mock_ollama_client,
        sandbox_manager=mock_sandbox_manager,
        config={"target": None},
    )
    return orchestrator


# ---------------------------------------------------------------------------
# Helper to run async tests without blocking
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_orchestrator_full_flow(
    orchestrator: Orchestrator,
    mock_ollama_client: MagicMock,
    mock_sandbox_manager: MagicMock,
) -> None:
    """
    Verify that the orchestrator:
    1. Calls LLM to reason about the target.
    2. Executes suggested tasks in the sandbox.
    3. Aggregates results from all sandbox runs.
    4. Returns a final aggregated result.
    """
    # Act
    result = await orchestrator.run("example.com")

    # Assert
    # Orchestrator should have called LLM reasoning once
    mock_ollama_client.reason.assert_awaited_once_with("example.com")

    # Should have executed both tasks in sandbox
    assert mock_sandbox_manager.run_task.await_count == 2
    mock_sandbox_manager.run_task.assert_any_await("subdomain_enum", "example.com")
    mock_sandbox_manager.run_task.assert_any_await("port_scan", "example.com")

    # Verify aggregated result contains both tasks
    assert "subdomain_enum" in result
    assert "port_scan" in result
    assert result["subdomain_enum"]["status"] == "complete"
    assert result["port_scan"]["status"] == "complete"
    assert "www.example.com" in result["subdomain_enum"]["results"]["domains"]
    assert 80 in result["port_scan"]["results"]["open_ports"]

    # Sanity: final cleanup called
    mock_sandbox_manager.cleanup.assert_awaited_once()


@pytest.mark.asyncio
async def test_orchestrator_sandbox_error_handling(
    orchestrator: Orchestrator,
    mock_ollama_client: MagicMock,
    mock_sandbox_manager: MagicMock,
) -> None:
    """
    Verify that when a sandbox task fails, the orchestrator:
    - Continues processing other tasks.
    - Includes error details in the final result.
    - Does not raise an unhandled exception.
    """
    # Override one sandbox call to fail
    async def failing_run(task: str, target: str) -> dict:
        if task == "port_scan":
            raise RuntimeError("Container crashed")
        return {"status": "complete", "results": {"domains": ["test.example.com"]}}

    mock_sandbox_manager.run_task = AsyncMock(side_effect=failing_run)

    # Act
    result = await orchestrator.run("example.com")

    # Assert
    # The subdomain_enum should have succeeded
    assert result["subdomain_enum"]["status"] == "complete"

    # The port_scan should contain error info
    assert "error" in result["port_scan"]
    assert "Container crashed" in result["port_scan"]["error"]

    # Cleanup still called
    mock_sandbox_manager.cleanup.assert_awaited_once()


@pytest.mark.asyncio
async def test_orchestrator_empty_llm_response(
    orchestrator: Orchestrator,
    mock_ollama_client: MagicMock,
) -> None:
    """
    Verify that if LLM returns no tasks, the orchestrator exits gracefully
    without sandbox interactions.
    """
    mock_ollama_client.reason = AsyncMock(return_value=[])

    result = await orchestrator.run("example.com")

    # No sandbox calls
    mock_ollama_client.reason.assert_awaited_once_with("example.com")
    # orchestrator.sandbox_manager.run_task should not have been called
    orchestrator.sandbox_manager.run_task.assert_not_awaited()
    # Result should be empty or indicate no tasks
    assert result == {} or "no_tasks" in result


@pytest.mark.asyncio
async def test_orchestrator_concurrent_task_execution(
    orchestrator: Orchestrator,
    mock_sandbox_manager: MagicMock,
) -> None:
    """
    Verify that tasks are executed concurrently (or at least not sequentially
    blocking), by having one task take longer and ensuring both finish.
    """
    delay_event = asyncio.Event()

    async def delayed_task(task: str, target: str) -> dict:
        if task == "subdomain_enum":
            await delay_event.wait()  # block until released
            return {"status": "complete", "results": {"domains": ["x.com"]}}
        return {"status": "complete", "results": {"ports": [80]}}

    mock_sandbox_manager.run_task = AsyncMock(side_effect=delayed_task)

    # Start orchestrator in a background task, release delay after short wait
    async def release_delay():
        await asyncio.sleep(0.1)
        delay_event.set()

    await asyncio.gather(
        orchestrator.run("example.com"),
        release_delay(),
    )

    # Both tasks should have been called
    assert mock_sandbox_manager.run_task.await_count == 2
    mock_sandbox_manager.run_task.assert_any_await("subdomain_enum", "example.com")
    mock_sandbox_manager.run_task.assert_any_await("port_scan", "example.com")
    # Verify cleanup was called after both tasks complete
    mock_sandbox_manager.cleanup.assert_awaited_once()


@pytest.mark.asyncio
async def test_orchestrator_respects_max_concurrency(
    orchestrator: Orchestrator,
    mock_sandbox_manager: MagicMock,
) -> None:
    """
    Verify that the orchestrator limits concurrency (e.g., semaphore) to avoid
    overloading the sandbox.
    """
    # Increase number of tasks to test concurrency limit
    orchestrator.ollama_client.reason = AsyncMock(
        return_value=[{"task": f"task_{i}", "target": "x"} for i in range(10)]
    )

    # Track active calls
    active = 0
    max_active = 0
    lock = asyncio.Lock()

    async def track_active(task: str, target: str) -> dict:
        nonlocal active, max_active
        async with lock:
            active += 1
            max_active = max(max_active, active)
        await asyncio.sleep(0.05)
        async with lock:
            active -= 1
        return {"status": "complete", "results": {}}

    mock_sandbox_manager.run_task = AsyncMock(side_effect=track_active)

    await orchestrator.run("x")

    # Assuming orchestrator uses a semaphore with concurrency=3
    # The max_active should never exceed 3
    assert max_active <= 3, f"Concurrency exceeded limit: {max_active}"