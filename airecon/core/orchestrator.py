"""
AIRecon Orchestrator — Async Core Loop.

Manages the reactive cycle of the AIRecon agent:
1. Listens for TUI events (user targets or context changes).
2. Invokes Ollama LLM to reason about the target and propose reconnaissance tasks.
3. Schedules tasks for isolated Kali Docker sandboxes.
4. Collects results, aggregates them, and feeds them back to the LLM for further reasoning.
5. Reports findings to the TUI.

Designed for Python 3.11+ with asyncio and production reliability.
This module provides abstract interfaces, domain types, and a concrete
orchestrator implementation.

All domain classes enforce validation in __post_init__ to ensure data integrity.
Logging is used throughout for observability without sacrificing performance.
"""

from __future__ import annotations

import asyncio
import logging
import signal
import sys
import time
from abc import ABC, abstractmethod
from collections.abc import AsyncIterator, Callable, Coroutine
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Final, Optional, Protocol, TypeVar
from uuid import uuid4

# ---------------------------------------------------------------------------
# Logging setup – structured and configurable
# ---------------------------------------------------------------------------

logger = logging.getLogger(__name__)
_logging_initialized = False


def setup_logging(
    level: int = logging.INFO,
    format_string: str = "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    json_output: bool = False,
) -> None:
    """Configure logging for the AIRecon orchestrator.

    Can be called once; subsequent calls are no-ops.

    Args:
        level: Minimum log level (e.g., logging.DEBUG).
        format_string: Standard format string (ignored if json_output is True).
        json_output: If True, use JSON-format logging (requires python-json-logger).
    """
    global _logging_initialized
    if _logging_initialized:
        return
    _logging_initialized = True

    if json_output:
        try:
            from pythonjsonlogger import jsonlogger  # type: ignore[import-untyped]
            handler = logging.StreamHandler(sys.stderr)
            formatter = jsonlogger.JsonFormatter("%(asctime)s %(levelname)s %(name)s %(message)s")
            handler.setFormatter(formatter)
            logging.basicConfig(level=level, handlers=[handler], force=True)
        except ImportError:
            logger.warning("python-json-logger not found; falling back to plain format")
            logging.basicConfig(level=level, format=format_string, force=True)
    else:
        logging.basicConfig(level=level, format=format_string, force=True)

    logger.debug("Logging configured at level %s", logging.getLevelName(level))


# ---------------------------------------------------------------------------
# Custom Exceptions
# ---------------------------------------------------------------------------

class AIReconError(Exception):
    """Base exception for all AIRecon errors.

    All custom exceptions inherit from this to allow catching all AIRecon-
    specific errors at a high level.
    """
    def __init__(self, message: str = "", *args: Any) -> None:
        self.message = message
        super().__init__(message, *args)


class ValidationError(AIReconError, ValueError):
    """Raised when input validation fails."""


class TaskExecutionError(AIReconError, RuntimeError):
    """Raised when a reconnaissance task fails in the sandbox.

    Attributes:
        task_id: Identifier of the failed task.
        exit_code: Exit code returned by the sandbox (if available).
        stderr: Standard error output (truncated).
    """
    def __init__(
        self,
        message: str = "",
        task_id: str | None = None,
        exit_code: int | None = None,
        stderr: str | None = None,
    ) -> None:
        self.task_id = task_id
        self.exit_code = exit_code
        self.stderr = stderr
        super().__init__(message)


class LLMConnectionError(AIReconError, ConnectionError):
    """Raised when the Ollama LLM service is unreachable."""


class LLMTimeoutError(AIReconError, TimeoutError):
    """Raised when the LLM does not respond within the configured timeout."""


class LLMResponseError(AIReconError, ValueError):
    """Raised when the LLM response cannot be parsed or is invalid."""


class ShutdownError(AIReconError, RuntimeError):
    """Raised when a graceful shutdown fails or takes too long."""


class ResourceExhaustedError(AIReconError, RuntimeError):
    """Raised when sandbox capacity or system resources are exhausted."""


# ---------------------------------------------------------------------------
# Domain Types
# ---------------------------------------------------------------------------

class EventType(Enum):
    """Events that can be pushed from the TUI or internal subsystems.

    Members:
        NEW_TARGET: A new target domain or IP was submitted.
        CONTEXT_UPDATE: Contextual information was updated (e.g., scope change).
        SHUTDOWN: System shutdown requested.
        LLM_RESPONSE: Response received from Ollama LLM.
        TASK_COMPLETED: A reconnaissance task finished execution.
        ERROR: An error occurred in a subsystem.
        RESULT_READY: Aggregated results ready for TUI display.
    """
    NEW_TARGET = auto()
    CONTEXT_UPDATE = auto()
    SHUTDOWN = auto()
    LLM_RESPONSE = auto()
    TASK_COMPLETED = auto()
    TASK_FAILED = auto()
    ERROR = auto()
    RESULT_READY = auto()


@dataclass(frozen=True, slots=True)
class Event:
    """A generic event with a type, payload, and optional correlation ID.

    Events are the primary means of communication between subsystems.
    They are immutable and validated upon creation.

    Attributes:
        type: The classification of the event.
        payload: Arbitrary data associated with the event. Must be a dict.
        correlation_id: Optional identifier for correlating events across subsystems.

    Raises:
        ValidationError: If any field fails validation.
    """

    type: EventType
    payload: dict[str, Any] = field(default_factory=dict)
    correlation_id: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.type, EventType):
            raise ValidationError(
                f"Invalid event type: {self.type!r}. Must be an EventType member."
            )
        if not isinstance(self.payload, dict):
            raise ValidationError(
                f"Payload must be a dictionary, got {type(self.payload).__name__}."
            )
        if self.correlation_id is not None:
            if not isinstance(self.correlation_id, str):
                raise ValidationError(
                    "correlation_id must be a string or None, "
                    f"got {type(self.correlation_id).__name__}."
                )
            if not self.correlation_id.strip():
                raise ValidationError("correlation_id must be non-empty if provided.")

        logger.debug(
            "Event created: type=%s, keys=%s, corr_id=%s",
            self.type.name,
            list(self.payload.keys()),
            self.correlation_id,
        )


@dataclass(frozen=True, slots=True)
class ReconTask:
    """A reconnaissance task to be executed inside a Kali Docker sandbox.

    Immutable after creation. Includes built-in security validation to prevent
    command injection.

    Attributes:
        id: Unique task identifier (auto-generated if not provided).
        command: Shell command to execute (must not contain forbidden characters).
        target: The target domain or IP.
        timeout: Maximum execution time in seconds (must be positive, default 300).
        env: Environment variables for the sandbox (optional).

    Raises:
        ValidationError: If any field fails validation.
        ValueError: If timeout is not a positive integer.
    """

    id: str = field(default_factory=lambda: uuid4().hex[:12])
    command: str
    target: str
    timeout: int = 300
    env: dict[str, str] = field(default_factory=dict)

    # Security: disallowed shell metacharacters to prevent injection
    _FORBIDDEN_CHARS: Final[frozenset[str]] = frozenset({";", "|", "&&", "`", "$", "(", ")", "\n"})

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValidationError("Task ID must be a non-empty string.")
        if not self.command.strip():
            raise ValidationError("Task command must be a non-empty string.")
        if not self.target.strip():
            raise ValidationError("Task target must be a non-empty string.")
        if not isinstance(self.timeout, int) or self.timeout <= 0:
            raise ValidationError(
                f"Timeout must be a positive integer, got {self.timeout!r}."
            )
        if not isinstance(self.env, dict):
            raise ValidationError("env must be a dictionary.")
        for key, value in self.env.items():
            if not isinstance(key, str) or not isinstance(value, str):
                raise ValidationError("Environment keys and values must be strings.")

        # Security: command injection prevention
        for char in self._FORBIDDEN_CHARS:
            if char in self.command:
                raise ValidationError(
                    f"Command contains forbidden character {char!r}. "
                    f"Forbidden set: {self._FORBIDDEN_CHARS}"
                )
        logger.debug("ReconTask validated: id=%s, target=%s", self.id, self.target)


@dataclass(frozen=True, slots=True)
class ReconResult:
    """Result of a reconnaissance task.

    Attributes:
        task_id: Identifier of the originating task.
        stdout: Standard output (may be truncated).
        stderr: Standard error output.
        exit_code: Exit code from the sandbox.
        execution_time: Wall-clock execution time in seconds.
    """
    task_id: str
    stdout: str
    stderr: str
    exit_code: int
    execution_time: float

    def __post_init__(self) -> None:
        if not self.task_id.strip():
            raise ValidationError("task_id must be non-empty")
        if self.exit_code < -127 or self.exit_code > 255:
            logger.warning(
                "Unusual exit code %d for task %s", self.exit_code, self.task_id
            )


@dataclass(frozen=True, slots=True)
class Target:
    """Represents a target domain or IP for reconnaissance.

    Attributes:
        hostname: The domain name or IP address.
        scope: Optional scope description (e.g., "in-scope").
        added_at: Unix timestamp when the target was added.
    """
    hostname: str
    scope: str = "default"
    added_at: float = field(default_factory=time.time)

    def __post_init__(self) -> None:
        if not self.hostname.strip():
            raise ValidationError("hostname must be non-empty")
        if not self.scope.strip():
            raise ValidationError("scope must be non-empty")


# ---------------------------------------------------------------------------
# Abstract Interfaces
# ---------------------------------------------------------------------------

class LLMClient(ABC):
    """Abstract base class for LLM interaction (Ollama)."""

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        timeout: float = 60.0,
        max_retries: int = 3,
    ) -> str:
        """Send a prompt to the LLM and return the response text.

        Args:
            prompt: The user prompt.
            system_prompt: Optional system-level instructions.
            timeout: Maximum time to wait for a response (seconds).
            max_retries: Number of retries on transient errors (e.g., timeout).

        Returns:
            The raw response string from the LLM.

        Raises:
            LLMConnectionError: If the LLM service is unreachable.
            LLMTimeoutError: If all retries exceed the timeout.
            LLMResponseError: If the response is empty or malformed.
        """
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the LLM service is responsive.

        Returns:
            True if the service responds within a short timeout.
        """
        ...


class SandboxManager(ABC):
    """Abstract base class for managing Kali Docker sandboxes."""

    @abstractmethod
    async def acquire_sandbox(self, timeout: float = 30.0) -> str:
        """Get the identifier of an available sandbox.

        Args:
            timeout: How long to wait for a free sandbox.

        Returns:
            Sandbox ID.

        Raises:
            ResourceExhaustedError: If no sandbox available within timeout.
        """
        ...

    @abstractmethod
    async def release_sandbox(self, sandbox_id: str) -> None:
        """Return a sandbox to the pool.

        Args:
            sandbox_id: The sandbox to release.
        """
        ...

    @abstractmethod
    async def execute_task(
        self,
        task: ReconTask,
        sandbox_id: str,
        timeout: float,
    ) -> ReconResult:
        """Run a reconnaissance task in the given sandbox.

        Args:
            task: The task to execute.
            sandbox_id: Target sandbox identifier.
            timeout: Maximum execution time (seconds).

        Returns:
            ReconResult with output and status.

        Raises:
            TaskExecutionError: If the sandbox fails or task exits abnormally.
            ResourceExhaustedError: If sandbox is no longer available.
        """
        ...

    @abstractmethod
    async def cleanup(self) -> None:
        """Release all resources and destroy sandboxes."""
        ...


class EventBus(ABC):
    """Abstract event bus for pub/sub communication."""

    @abstractmethod
    async def publish(self, event: Event) -> None:
        """Publish an event to all subscribers.

        Args:
            event: The event to distribute.
        """
        ...

    @abstractmethod
    async def subscribe(
        self,
        event_types: set[EventType] | None,
        callback: Callable[[Event], Coroutine[Any, Any, None]],
    ) -> None:
        """Register a callback for specific event types.

        Args:
            event_types: Set of types to subscribe to (None = all types).
            callback: Async function to handle events.
        """
        ...

    @abstractmethod
    async def unsubscribe(
        self,
        event_types: set[EventType] | None,
        callback: Callable[[Event], Coroutine[Any, Any, None]],
    ) -> None:
        """Remove a subscription."""
        ...

    @abstractmethod
    async def close(self) -> None:
        """Shut down the event bus and purge pending events."""
        ...


class ResultStore(ABC):
    """Abstract store for task results and findings."""

    @abstractmethod
    async def save_result(self, result: ReconResult) -> None:
        """Persist a task result.

        Args:
            result: The result to store.
        """
        ...

    @abstractmethod
    async def get_results(self, task_ids: list[str] | None = None) -> list[ReconResult]:
        """Retrieve stored results.

        Args:
            task_ids: Optional filter; if None, returns all.

        Returns:
            List of matching ReconResult objects, sorted by execution time.
        """
        ...

    @abstractmethod
    async def get_summary(self, target: str) -> dict[str, Any]:
        """Get a summary of findings for a target.

        Args:
            target: The target hostname.

        Returns:
            Dict with keys: 'total_tasks', 'findings', 'errors'.
        """
        ...


# ---------------------------------------------------------------------------
# Concrete EventBus Implementation (in-memory, async)
# ---------------------------------------------------------------------------

class InMemoryEventBus(EventBus):
    """Simple in-process event bus using asyncio queues.

    Thread-safe coroutine-based implementation. Supports wildcard subscription
    by passing ``event_types=None``.
    """

    def __init__(self, max_queue_size: int = 1000) -> None:
        self._subscriptions: dict[EventType | None, list[Callable[[Event], Coroutine[Any, Any, None]]]] = {}
        self._queue: asyncio.Queue[Event] = asyncio.Queue(maxsize=max_queue_size)
        self._closed = False
        self._worker_task: asyncio.Task[None] | None = None

    async def start(self) -> None:
        """Start the background worker that dispatches events."""
        if self._worker_task is not None:
            return
        self._worker_task = asyncio.create_task(self._dispatch_loop())
        logger.debug("Event bus worker started")

    async def publish(self, event: Event) -> None:
        if self._closed:
            logger.warning("Publishing on closed event bus: %s", event.type.name)
            return
        try:
            await asyncio.wait_for(self._queue.put(event), timeout=1.0)
        except asyncio.TimeoutError:
            logger.error("Event bus queue full; dropping event %s", event.type.name)

    async def subscribe(
        self,
        event_types: set[EventType] | None,
        callback: Callable[[Event], Coroutine[Any, Any, None]],
    ) -> None:
        key: EventType | None = None if event_types is None else frozenset(event_types)  # type: ignore[assignment]
        # Use a single key for wildcard or a representative set
        # Actually we'll use None for wildcard, frozenset for specific sets
        if event_types is None:
            key = None
        else:
            key = frozenset(event_types)  # type: ignore[assignment]
        self._subscriptions.setdefault(key, []).append(callback)
        logger.debug(
            "Subscribed callback %s for events %s",
            callback.__name__,
            "ALL" if event_types is None else [e.name for e in event_types],
        )

    async def unsubscribe(
        self,
        event_types: set[EventType] | None,
        callback: Callable[[Event], Coroutine[Any, Any, None]],
    ) -> None:
        key = None if event_types is None else frozenset(event_types)  # type: ignore[assignment]
        subs = self._subscriptions.get(key, [])
        if callback in subs:
            subs.remove(callback)
            if not subs:
                del self._subscriptions[key]
            logger.debug("Unsubscribed callback %s", callback.__name__)

    async def close(self) -> None:
        self._closed = True
        if self._worker_task and not self._worker_task.done():
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass
        self._worker_task = None
        logger.info("Event bus closed")

    async def _dispatch_loop(self) -> None:
        while not self._closed:
            try:
                event = await asyncio.wait_for(self._queue.get(), timeout=0.5)
            except asyncio.TimeoutError:
                continue
            # Gather all matching callbacks
            tasks: list[Coroutine[Any, Any, None]] = []
            # Wildcard subscribers
            wildcard_key: None = None
            for callback in self._subscriptions.get(wildcard_key, []):  # type: ignore[arg-type]
                tasks.append(callback(event))
            # Type-specific subscribers
            for key, callbacks in self._subscriptions.items():
                if key is None:
                    continue
                # key is frozenset[EventType] but type hint is tricky
                if event.type in key:  # type: ignore[operator]
                    for cb in callbacks:
                        tasks.append(cb(event))
            # Run all callbacks concurrently
            if tasks:
                results = await asyncio.gather(*tasks, return_exceptions=True)
                # Log exceptions
                for i, res in enumerate(results):
                    if isinstance(res, Exception):
                        logger.error("Event callback raised: %s", res, exc_info=res)
            self._queue.task_done()


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

T = TypeVar("T")


class Orchestrator:
    """Main orchestrator that drives the AIRecon reactive loop.

    Attributes:
        event_bus: Event bus for inter-component communication.
        llm_client: LLM abstraction (Ollama).
        sandbox_manager: Sandbox resource manager.
        result_store: Persistence for reconnaissance results.
        config: Orchestrator configuration (timeouts, limits, etc.).
    """

    def __init__(
        self,
        event_bus: EventBus,
        llm_client: LLMClient,
        sandbox_manager: SandboxManager,
        result_store: ResultStore,
        config: OrchestratorConfig | None = None,
    ) -> None:
        self.event_bus = event_bus
        self.llm_client = llm_client
        self.sandbox_manager = sandbox_manager
        self.result_store = result_store
        self.config = config or OrchestratorConfig()

        self._running = False
        self._tasks: dict[str, ReconTask] = {}
        self._sandbox_pool: dict[str, str] = {}  # task_id -> sandbox_id
        self._active_results: dict[str, ReconResult] = {}
        self._targets: dict[str, Target] = {}
        self._shutdown_event = asyncio.Event()

    async def start(self) -> None:
        """Start the orchestrator loop.

        Sets up signal handlers, subscribes to events, and begins processing.
        """
        if self._running:
            logger.warning("Orchestrator already running")
            return
        self._running = True

        # If event bus is InMemoryEventBus, start it
        if isinstance(self.event_bus, InMemoryEventBus):
            await self.event_bus.start()

        # Subscribe to events
        await self.event_bus.subscribe(
            {EventType.NEW_TARGET, EventType.CONTEXT_UPDATE},
            self._handle_target_event,
        )
        await self.event_bus.subscribe(
            {EventType.SHUTDOWN},
            self._handle_shutdown_event,
        )
        await self.event_bus.subscribe(
            {EventType.TASK_COMPLETED},
            self._handle_task_completed,
        )
        await self.event_bus.subscribe(
            {EventType.TASK_FAILED},
            self._handle_task_failed,
        )

        # Set up signal handlers for graceful shutdown
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            try:
                loop.add_signal_handler(
                    sig,
                    lambda: asyncio.ensure_future(self._signal_handler(sig)),
                )
            except NotImplementedError:
                logger.warning("Signal handling not supported on this platform")

        logger.info("Orchestrator started with config: %s", self.config)

        # Main idle loop – keep running until shutdown
        try:
            await self._shutdown_event.wait()
        except asyncio.CancelledError:
            logger.info("Orchestrator main task cancelled")
        finally:
            await self._shutdown()

    async def stop(self) -> None:
        """Initiate graceful shutdown."""
        await self.event_bus.publish(Event(EventType.SHUTDOWN, {"source": "api"}))

    # ------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------

    async def _handle_target_event(self, event: Event) -> None:
        target = event.payload.get("target")
        if not target or not isinstance(target, str):
            logger.warning("Invalid target event payload: %s", event.payload)
            return
        scope = event.payload.get("scope", "default")
        target_obj = Target(hostname=target, scope=scope)
        self._targets[target] = target_obj
        logger.info("New target registered: %s (scope=%s)", target, scope)

        # Request LLM to propose reconnaissance tasks
        try:
            tasks = await self._propose_tasks(target_obj)
        except (LLMConnectionError, LLMTimeoutError) as exc:
            logger.error("LLM unavailable for target '%s': %s", target, exc)
            await self._emit_error(f"LLM failed for {target}: {exc}")
            return
        except LLMResponseError as exc:
            logger.error("LLM response unparseable for target '%s': %s", target, exc)
            await self._emit_error(f"LLM response invalid for {target}: {exc}")
            return

        if not tasks:
            logger.info("LLM proposed no tasks for target '%s'", target)
            return

        # Schedule tasks
        scheduled = 0
        for task in tasks:
            try:
                await self._schedule_task(task)
                scheduled += 1
            except ResourceExhaustedError:
                logger.warning("Sandbox capacity reached; task %s queued", task.id)
                break
        logger.info(
            "Scheduled %d/%d tasks for target '%s'",
            scheduled,
            len(tasks),
            target,
        )

    async def _handle_shutdown_event(self, event: Event) -> None:
        logger.info("Shutdown requested: %s", event.payload.get("source", "unknown"))
        self._shutdown_event.set()

    async def _handle_task_completed(self, event: Event) -> None:
        result = event.payload.get("result")
        if not isinstance(result, ReconResult):
            logger.error("Task completed event missing valid result")
            return
        self._active_results[result.task_id] = result
        await self.result_store.save_result(result)

        # Release sandbox
        sandbox_id = self._sandbox_pool.pop(result.task_id, None)
        if sandbox_id:
            await self.sandbox_manager.release_sandbox(sandbox_id)

        # Optionally feed result back to LLM for further reasoning
        task = self._tasks.get(result.task_id)
        if task:
            logger.info("Task %s completed for %s (exit=%d)", task.id, task.target, result.exit_code)
            # Ask LLM to analyze result and propose follow-up
            await self._analyze_and_follow_up(task, result)

    async def _handle_task_failed(self, event: Event) -> None:
        task_id = event.payload.get("task_id", "unknown")
        error = event.payload.get("error", "Unknown error")
        logger.error("Task %s failed: %s", task_id, error)
        sandbox_id = self._sandbox_pool.pop(task_id, None)
        if sandbox_id:
            await self.sandbox_manager.release_sandbox(sandbox_id)
        await self._emit_error(f"Task {task_id} failed: {error}")

    # ------------------------------------------------------------------
    # Core logic: LLM interaction and task scheduling
    # ------------------------------------------------------------------

    async def _propose_tasks(self, target: Target) -> list[ReconTask]:
        """Ask the LLM to generate reconnaissance tasks for a target.

        Args:
            target: The target to recon.

        Returns:
            List of validated ReconTask objects.

        Raises:
            LLMConnectionError, LLMTimeoutError, LLMResponseError
        """
        prompt = (
            f"Given the target domain/IP: {target.hostname} (scope: {target.scope}),\n"
            "propose a list of reconnaissance commands to run in a Kali environment.\n"
            "Return ONLY a JSON list of objects with keys: 'command' (string), 'timeout' (int, seconds).\n"
            "Example: [{\"command\": \"nmap -sV {target}\", \"timeout\": 120}]\n"
            "Do NOT include any other text."
        )

        response = await self.llm_client.generate(
            prompt=prompt,
            system_prompt="You are a security reconnaissance planner. Output only valid JSON.",
            timeout=self.config.llm_timeout,
            max_retries=self.config.llm_retries,
        )

        # Parse JSON response
        import json
        try:
            raw_tasks = json.loads(response)
        except json.JSONDecodeError as exc:
            raise LLMResponseError(f"Invalid JSON from LLM: {exc}") from exc

        if not isinstance(raw_tasks, list):
            raise LLMResponseError("LLM response is not a list")

        tasks: list[ReconTask] = []
        for item in raw_tasks:
            command = item.get("command", "")
            timeout = item.get("timeout", 300)
            try:
                task = ReconTask(
                    command=command.format(target=target.hostname),
                    target=target.hostname,
                    timeout=int(timeout),
                )
                tasks.append(task)
            except (ValidationError, ValueError) as exc:
                logger.warning("Skipping invalid task from LLM: %s", exc)
                continue
        return tasks

    async def _schedule_task(self, task: ReconTask) -> None:
        """Acquire a sandbox and execute the task.

        Args:
            task: The task to schedule.

        Raises:
            ResourceExhaustedError: If no sandbox available.
        """
        sandbox_id = await self.sandbox_manager.acquire_sandbox(
            timeout=self.config.sandbox_acquire_timeout
        )
        self._sandbox_pool[task.id] = sandbox_id
        self._tasks[task.id] = task

        # Create a dedicated task for execution
        asyncio.create_task(self._execute_task_in_sandbox(task, sandbox_id))

    async def _execute_task_in_sandbox(self, task: ReconTask, sandbox_id: str) -> None:
        """Wrap sandbox execution and publish completion/failure event.

        Args:
            task: The task to run.
            sandbox_id: Identifier of the sandbox to use.
        """
        try:
            result = await self.sandbox_manager.execute_task(
                task=task,
                sandbox_id=sandbox_id,
                timeout=task.timeout,
            )
            await self.event_bus.publish(
                Event(
                    EventType.TASK_COMPLETED,
                    payload={"result": result, "task_id": task.id},
                    correlation_id=task.id,
                )
            )
        except TaskExecutionError as exc:
            await self.event_bus.publish(
                Event(
                    EventType.TASK_FAILED,
                    payload={
                        "task_id": task.id,
                        "error": str(exc),
                        "exit_code": exc.exit_code,
                        "stderr": exc.stderr,
                    },
                    correlation_id=task.id,
                )
            )
        except Exception as exc:
            logger.exception("Unexpected error executing task %s", task.id)
            await self.event_bus.publish(
                Event(
                    EventType.ERROR,
                    payload={"task_id": task.id, "error": str(exc)},
                    correlation_id=task.id,
                )
            )

    async def _analyze_and_follow_up(self, task: ReconTask, result: ReconResult) -> None:
        """Feed task result back to LLM to decide if follow-up actions needed.

        Args:
            task: The original task.
            result: The execution result.
        """
        if not self.config.follow_up_enabled:
            return

        prompt = (
            f"Task completed for target {task.target}:\n"
            f"Command: {task.command}\n"
            f"Exit code: {result.exit_code}\n"
            f"Stdout (first 500 chars): {result.stdout[:500]}\n"
            f"Stderr (first 500 chars): {result.stderr[:500]}\n\n"
            "Should any additional reconnaissance tasks be performed? "
            "If yes, return a JSON list of new tasks (same format as before). "
            'If no further action needed, return {"follow_up": false}."
        )
        try:
            response = await self.llm_client.generate(
                prompt=prompt,
                timeout=self.config.llm_timeout,
                max_retries=self.config.llm_retries,
            )
        except (LLMConnectionError, LLMTimeoutError, LLMResponseError) as exc:
            logger.warning("Follow-up LLM call failed: %s", exc)
            return

        import json
        try:
            data = json.loads(response)
        except json.JSONDecodeError:
            logger.warning("Follow-up LLM response not valid JSON")
            return

        if isinstance(data, dict) and data.get("follow_up") is False:
            return

        if isinstance(data, list):
            for item in data:
                command = item.get("command", "")
                timeout = item.get("timeout", 300)
                try:
                    new_task = ReconTask(
                        command=command.format(target=task.target),
                        target=task.target,
                        timeout=int(timeout),
                    )
                    await self._schedule_task(new_task)
                except (ValidationError, ValueError, ResourceExhaustedError) as exc:
                    logger.warning("Follow-up task rejected: %s", exc)
                    continue

    # ------------------------------------------------------------------
    # Utility methods
    # ------------------------------------------------------------------

    async def _emit_error(self, message: str) -> None:
        """Publish an error event with the given message.

        Args:
            message: Human-readable error description.
        """
        await self.event_bus.publish(
            Event(EventType.ERROR, payload={"message": message})
        )

    async def _signal_handler(self, sig: signal.Signals) -> None:
        logger.info("Received signal %s, initiating shutdown...", sig.name)
        self._shutdown_event.set()

    async def _shutdown(self) -> None:
        """Gracefully shut down all components.

        Cancels pending tasks, releases sandboxes, closes event bus.
        """
        logger.info("Shutting down orchestrator...")
        self._running = False

        # Cancel all in-flight execution tasks
        for task_id, sandbox_id in list(self._sandbox_pool.items()):
            try:
                await self.sandbox_manager.release_sandbox(sandbox_id)
            except Exception as exc:
                logger.error("Error releasing sandbox %s: %s", sandbox_id, exc)
        self._sandbox_pool.clear()
        self._tasks.clear()

        # Clean up sandbox manager
        try:
            await asyncio.wait_for(self.sandbox_manager.cleanup(), timeout=10.0)
        except asyncio.TimeoutError:
            logger.error("Sandbox cleanup timed out")
        except Exception as exc:
            logger.error("Sandbox cleanup failed: %s", exc)

        # Close event bus
        try:
            await self.event_bus.close()
        except Exception as exc:
            logger.error("Event bus close failed: %s", exc)

        logger.info("Orchestrator shutdown complete")


@dataclass(frozen=True, slots=True)
class OrchestratorConfig:
    """Configuration for the orchestrator.

    Attributes:
        llm_timeout: Max seconds to wait for LLM response (default 120).
        llm_retries: Number of retries on LLM failure (default 3).
        sandbox_acquire_timeout: Max seconds to wait for a free sandbox (default 60).
        max_concurrent_tasks: Maximum concurrent tasks across all sandboxes (default 10).
        follow_up_enabled: Whether to allow LLM-driven follow-up tasks (default True).
    """
    llm_timeout: float = 120.0
    llm_retries: int = 3
    sandbox_acquire_timeout: float = 60.0
    max_concurrent_tasks: int = 10
    follow_up_enabled: bool = True

    def __post_init__(self) -> None:
        if self.llm_timeout <= 0:
            raise ValidationError("llm_timeout must be positive")
        if self.llm_retries < 0:
            raise ValidationError("llm_retries must be non-negative")
        if self.sandbox_acquire_timeout <= 0:
            raise ValidationError("sandbox_acquire_timeout must be positive")
        if self.max_concurrent_tasks <= 0:
            raise ValidationError("max_concurrent_tasks must be positive")


# ---------------------------------------------------------------------------
# Entry point example (for testing)
# ---------------------------------------------------------------------------

async def main() -> None:
    """Example main function to start the orchestrator.

    This requires concrete implementations of LLMClient, SandboxManager,
    and ResultStore. For demonstration, dummy stubs are provided.
    """
    setup_logging(level=logging.DEBUG)

    # Dummy implementations for illustration
    class DummyLLM(LLMClient):
        async def generate(self, **kwargs) -> str:
            return '[]'
        async def health_check(self) -> bool:
            return True

    class DummySandbox(SandboxManager):
        def __init__(self):
            self._counter = 0
            self._pool = asyncio.Queue(maxsize=10)
            for _ in range(3):
                self._pool.put_nowait(f"sandbox-{uuid4().hex[:6]}")
        async def acquire_sandbox(self, timeout: float = 30.0) -> str:
            try:
                return await asyncio.wait_for(self._pool.get(), timeout=timeout)
            except asyncio.TimeoutError:
                raise ResourceExhaustedError("No sandbox available")
        async def release_sandbox(self, sandbox_id: str) -> None:
            await self._pool.put(sandbox_id)
        async def execute_task(self, task: ReconTask, sandbox_id: str, timeout: float) -> ReconResult:
            await asyncio.sleep(0.1)
            return ReconResult(
                task_id=task.id,
                stdout="dummy output",
                stderr="",
                exit_code=0,
                execution_time=0.1,
            )
        async def cleanup(self) -> None:
            pass

    class DummyStore(ResultStore):
        def __init__(self):
            self._results: list[ReconResult] = []
        async def save_result(self, result: ReconResult) -> None:
            self._results.append(result)
        async def get_results(self, task_ids: list[str] | None = None) -> list[ReconResult]:
            return self._results
        async def get_summary(self, target: str) -> dict[str, Any]:
            return {"total_tasks": len(self._results), "findings": [], "errors": 0}

    event_bus = InMemoryEventBus()
    llm = DummyLLM()
    sandbox = DummySandbox()
    store = DummyStore()
    config = OrchestratorConfig(follow_up_enabled=False)

    orchestrator = Orchestrator(event_bus, llm, sandbox, store, config)

    # Simulate a target event
    await event_bus.publish(
        Event(EventType.NEW_TARGET, payload={"target": "example.com", "scope": "in-scope"})
    )

    # Run orchestrator for a few seconds then shut down
    run_task = asyncio.create_task(orchestrator.start())

    await asyncio.sleep(3)
    await orchestrator.stop()
    await run_task

    logger.info("Demo completed")


if __name__ == "__main__":
    asyncio.run(main())