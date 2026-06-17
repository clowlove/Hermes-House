"""
Ollama API client with streaming, retries, and comprehensive error handling.

Provides both streaming and non-streaming methods for the ``/api/generate``
and ``/api/chat`` endpoints. All operations are async and thread-safe.

Example::

    async with OllamaClient() as client:
        async for token in client.generate_stream("Tell me a joke"):
            print(token, end="")
"""

from __future__ import annotations

import asyncio
import json
import logging
import random
from dataclasses import dataclass, field
from typing import (
    Any,
    AsyncGenerator,
    AsyncIterator,
    Dict,
    Final,
    List,
    Optional,
    TypedDict,
    Union,
)

import aiohttp
import aiohttp.client_exceptions

logger = logging.getLogger(__name__)

# ---------- Public API ----------
__all__ = [
    "OllamaClient",
    "OllamaClientError",
    "OllamaConnectionError",
    "OllamaHTTPError",
    "OllamaRateLimitError",
    "OllamaResponseError",
    "OllamaTimeoutError",
    "ClientConfig",
    "GeneratePayload",
    "ChatPayload",
    "ChatMessage",
    "Options",
    "StreamChunk",
]

# ---------- Constants ----------
DEFAULT_BASE_URL: Final[str] = "http://localhost:11434"
DEFAULT_MODEL: Final[str] = "llama3.1"
DEFAULT_TIMEOUT: Final[int] = 60  # seconds
DEFAULT_RETRY_ATTEMPTS: Final[int] = 3
BACKOFF_BASE: Final[float] = 2.0  # exponential backoff base
MAX_BACKOFF: Final[float] = 30.0  # maximum backoff in seconds
JITTER_FACTOR: Final[float] = 0.5  # random jitter as fraction of delay
# HTTP status codes eligible for retry (server errors)
RETRYABLE_STATUS_CODES: Final[frozenset[int]] = frozenset({408, 429, 500, 502, 503, 504})
# Maximum size of a single JSON line from Ollama (safety limit)
MAX_LINE_SIZE: Final[int] = 1024 * 1024  # 1 MiB
# Maximum concurrent requests (configurable)
DEFAULT_MAX_CONCURRENT: Final[int] = 10
# User agent sent in requests
USER_AGENT: Final[str] = "OllamaClient/2.0 (+https://github.com/pikpikcu/airecon)"
# Default keep alive
DEFAULT_KEEP_ALIVE: Final[str] = "5m"
# Session close grace period
SESSION_CLOSE_TIMEOUT: Final[float] = 2.0

# ---------- Type aliases ----------
ChatMessage = Dict[str, str]  # {"role": "...", "content": "..."}
Options = Dict[str, Any]  # e.g. {"temperature": 0.7}
StreamChunk = Dict[str, Any]  # Ollama streaming response JSON line


# ---------- Typed payloads for better validation ----------
class GeneratePayload(TypedDict, total=False):
    """Payload for /api/generate."""
    model: str
    prompt: str
    suffix: str
    system: str
    template: str
    context: List[int]
    options: Options
    format: str
    raw: bool
    stream: bool
    keep_alive: str


class ChatPayload(TypedDict, total=False):
    """Payload for /api/chat."""
    model: str
    messages: List[ChatMessage]
    options: Options
    format: str
    stream: bool
    keep_alive: str


# ========== Custom Exceptions ==========
class OllamaClientError(Exception):
    """Base exception for all Ollama client errors."""


class OllamaConnectionError(OllamaClientError):
    """Raised when a network or connection error occurs."""


class OllamaHTTPError(OllamaClientError):
    """Raised when the API returns a non‑200 HTTP status code.

    Attributes:
        status_code: The HTTP status code returned by the server.
        response_body: Raw response body (for debugging).
    """

    def __init__(self, message: str, status_code: int, response_body: str = "") -> None:
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body


class OllamaResponseError(OllamaClientError):
    """Raised when the response cannot be parsed correctly."""


class OllamaTimeoutError(OllamaClientError):
    """Raised when a request exceeds the configured timeout."""


class OllamaRateLimitError(OllamaHTTPError):
    """Raised on 429 Too Many Requests."""


# ========== Configuration dataclass ==========
@dataclass
class ClientConfig:
    """Immutable configuration for OllamaClient.

    Attributes:
        base_url: Ollama server URL.
        model: Default model name.
        timeout: Total request timeout in seconds.
        retry_attempts: Maximum number of retries for transient failures.
        max_concurrent: Maximum number of concurrent requests.
        keep_alive: Default keep_alive value sent in payloads.
        custom_headers: Additional HTTP headers to include.
        proxy: Optional proxy URL.
        verify_ssl: Whether to verify SSL certificates.
        connector_params: Additional aiohttp.TCPConnector parameters.
    """
    base_url: str = field(default=DEFAULT_BASE_URL)
    model: str = field(default=DEFAULT_MODEL)
    timeout: int = field(default=DEFAULT_TIMEOUT)
    retry_attempts: int = field(default=DEFAULT_RETRY_ATTEMPTS)
    max_concurrent: int = field(default=DEFAULT_MAX_CONCURRENT)
    keep_alive: str = field(default=DEFAULT_KEEP_ALIVE)
    custom_headers: Dict[str, str] = field(default_factory=dict)
    proxy: Optional[str] = field(default=None)
    verify_ssl: bool = field(default=True)
    connector_params: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate configuration parameters."""
        if not self.base_url.startswith(("http://", "https://")):
            raise ValueError(
                f"base_url must start with http:// or https://, got {self.base_url!r}"
            )
        if not self.model or not isinstance(self.model, str):
            raise ValueError(f"model must be a non-empty string, got {self.model!r}")
        if self.timeout < 0:
            raise ValueError(f"timeout must be >= 0, got {self.timeout}")
        if self.retry_attempts < 1:
            raise ValueError(f"retry_attempts must be >= 1, got {self.retry_attempts}")
        if self.max_concurrent < 1:
            raise ValueError(f"max_concurrent must be >= 1, got {self.max_concurrent}")
        if self.proxy is not None and not isinstance(self.proxy, str):
            raise ValueError(f"proxy must be a string or None, got {type(self.proxy).__name__}")
        if not isinstance(self.verify_ssl, bool):
            raise ValueError(f"verify_ssl must be bool, got {type(self.verify_ssl).__name__}")


# ========== Utility functions ==========
def _compute_backoff(attempt: int) -> float:
    """Compute backoff delay with jitter for the *attempt*-th retry.

    Uses exponential backoff with full jitter::

        delay = min(base^attempt, max_backoff) * uniform(0, 1)

    Args:
        attempt: Current retry attempt number (0‑based).

    Returns:
        Delay in seconds (including random jitter).
    """
    if attempt < 0:
        raise ValueError(f"attempt must be non-negative, got {attempt}")
    base_delay = min(BACKOFF_BASE ** attempt, MAX_BACKOFF)
    jitter = random.random() * JITTER_FACTOR * base_delay
    return base_delay + jitter


def _parse_stream_line(line: bytes) -> StreamChunk:
    """Parse a single JSON line from an Ollama streaming response.

    Args:
        line: Raw bytes line from the response body.

    Returns:
        Parsed JSON dictionary.

    Raises:
        OllamaResponseError: If line is not valid JSON or exceeds max size.
    """
    if len(line) > MAX_LINE_SIZE:
        raise OllamaResponseError(
            f"Stream line exceeds maximum size of {MAX_LINE_SIZE} bytes"
        )
    try:
        return json.loads(line)
    except json.JSONDecodeError as exc:
        raise OllamaResponseError(
            f"Failed to decode stream line as JSON: {exc}"
        ) from exc


def _validate_payload(payload: Union[GeneratePayload, ChatPayload], endpoint: str) -> None:
    """Validate required payload keys for the given endpoint.

    Args:
        payload: The payload dictionary.
        endpoint: API endpoint name (e.g. ``"generate"``, ``"chat"``).

    Raises:
        ValueError: If required keys are missing or invalid.
    """
    if not isinstance(payload, dict):
        raise ValueError(f"Payload must be a dict, got {type(payload).__name__}")

    if endpoint == "generate":
        if "prompt" not in payload:
            raise ValueError("Payload for /api/generate must contain 'prompt'")
        if not isinstance(payload["prompt"], str) or not payload["prompt"].strip():
            raise ValueError("'prompt' must be a non-empty string")
    elif endpoint == "chat":
        if "messages" not in payload or not payload["messages"]:
            raise ValueError("Payload for /api/chat must contain non-empty 'messages' list")
        if not isinstance(payload["messages"], list):
            raise ValueError("'messages' must be a list")
        for msg in payload["messages"]:
            if not isinstance(msg, dict) or "role" not in msg or "content" not in msg:
                raise ValueError("Each message must be a dict with 'role' and 'content'")
    else:
        raise ValueError(f"Unknown endpoint: {endpoint}")


def _sanitize_url(url: str) -> str:
    """Basic sanitization to prevent CRLF injection in URL paths.

    Args:
        url: URL string to sanitize.

    Returns:
        Sanitized URL string.
    """
    return url.replace("\n", "").replace("\r", "")


# ========== OllamaClient ==========
class OllamaClient:
    """Async HTTP client for the Ollama API.

    Supports streaming generation and chat, automatic retries, connection
    pooling, and configurable rate limiting.

    Args:
        config: :class:`ClientConfig` instance or keyword arguments.

    Keyword Args:
        **kwargs: Override default configuration values (see :class:`ClientConfig`).

    Raises:
        ValueError: If configuration is invalid.
    """

    def __init__(
        self,
        config: Optional[ClientConfig] = None,
        **kwargs: Any,
    ) -> None:
        if config is not None:
            if kwargs:
                raise ValueError("Cannot provide both config and keyword arguments")
            self._config = config
        else:
            self._config = ClientConfig(**kwargs)

        self._session: Optional[aiohttp.ClientSession] = None
        self._semaphore: asyncio.Semaphore = asyncio.Semaphore(
            self._config.max_concurrent
        )
        self._base_url: str = self._config.base_url.rstrip("/")
        self._default_headers: Dict[str, str] = {
            "User-Agent": USER_AGENT,
            "Content-Type": "application/json",
            "Accept": "application/json",
            **self._config.custom_headers,
        }

        logger.debug(
            "OllamaClient initialized: base_url=%s, model=%s, timeout=%s, "
            "retry_attempts=%s, max_concurrent=%s",
            self._base_url,
            self._config.model,
            self._config.timeout,
            self._config.retry_attempts,
            self._config.max_concurrent,
        )

    # ---------- Context manager ----------
    async def __aenter__(self) -> OllamaClient:
        await self._ensure_session()
        return self

    async def __aexit__(
        self,
        exc_type: Optional[type],
        exc_val: Optional[BaseException],
        exc_tb: Any,
    ) -> None:
        await self.close()

    async def close(self) -> None:
        """Close the underlying HTTP session and free resources.

        This method is safe to call multiple times.
        """
        session = self._session
        if session is not None and not session.closed:
            try:
                await asyncio.wait_for(
                    session.close(),
                    timeout=SESSION_CLOSE_TIMEOUT,
                )
            except (asyncio.TimeoutError, aiohttp.ClientError) as exc:
                logger.warning("Error closing session: %s", exc)
            finally:
                self._session = None
                logger.debug("Session closed")

    # ---------- Internal session management ----------
    async def _ensure_session(self) -> aiohttp.ClientSession:
        """Lazy initialization of the HTTP session with connection pooling.

        Returns:
            The active aiohttp.ClientSession.
        """
        if self._session is None or self._session.closed:
            connector_params: Dict[str, Any] = {
                "ssl": self._config.verify_ssl,
                "limit": self._config.max_concurrent,
                **self._config.connector_params,
            }
            connector = aiohttp.TCPConnector(**connector_params)
            timeout = aiohttp.ClientTimeout(total=self._config.timeout)
            self._session = aiohttp.ClientSession(
                headers=self._default_headers,
                timeout=timeout,
                connector=connector,
            )
            logger.debug("Created new aiohttp session with limit=%s", self._config.max_concurrent)
        return self._session

    # ---------- Public generation methods ----------
    async def generate(
        self,
        prompt: str,
        *,
        model: Optional[str] = None,
        system: Optional[str] = None,
        options: Optional[Options] = None,
        keep_alive: Optional[str] = None,
        **kwargs: Any,
    ) -> StreamChunk:
        """Non‑streaming generation via ``/api/generate``.

        Args:
            prompt: The input prompt (required).
            model: Model name (default: config.model).
            system: System prompt to override model's default.
            options: Model parameters (e.g., temperature, top_p).
            keep_alive: Duration to keep model loaded in memory.
            **kwargs: Additional payload fields (e.g., format, raw).

        Returns:
            The complete response dictionary.

        Raises:
            OllamaConnectionError: On network/fetch errors.
            OllamaHTTPError: On non‑2xx HTTP status.
            OllamaResponseError: On invalid response.
            ValueError: On invalid arguments.
        """
        if not prompt or not isinstance(prompt, str):
            raise ValueError("prompt must be a non-empty string")

        payload: GeneratePayload = {
            "model": model or self._config.model,
            "prompt": prompt,
            "stream": False,
            "keep_alive": keep_alive or self._config.keep_alive,
        }
        if system is not None:
            payload["system"] = system
        if options:
            payload["options"] = options
        payload.update(kwargs)

        return await self._request("generate", payload)

    async def generate_stream(
        self,
        prompt: str,
        *,
        model: Optional[str] = None,
        system: Optional[str] = None,
        options: Optional[Options] = None,
        keep_alive: Optional[str] = None,
        **kwargs: Any,
    ) -> AsyncGenerator[StreamChunk, None]:
        """Streaming generation via ``/api/generate``.

        Args:
            prompt: The input prompt (required).
            model: Model name (default: config.model).
            system: System prompt to override model's default.
            options: Model parameters (e.g., temperature, top_p).
            keep_alive: Duration to keep model loaded in memory.
            **kwargs: Additional payload fields (e.g., format, raw).

        Yields:
            Response chunks as they arrive from the server.

        Raises:
            OllamaConnectionError: On network/fetch errors.
            OllamaHTTPError: On non‑2xx HTTP status.
            OllamaResponseError: On invalid response line.
            ValueError: On invalid arguments.
        """
        if not prompt or not isinstance(prompt, str):
            raise ValueError("prompt must be a non-empty string")

        payload: GeneratePayload = {
            "model": model or self._config.model,
            "prompt": prompt,
            "stream": True,
            "keep_alive": keep_alive or self._config.keep_alive,
        }
        if system is not None:
            payload["system"] = system
        if options:
            payload["options"] = options
        payload.update(kwargs)

        async for chunk in self._stream_request("generate", payload):
            yield chunk

    # ---------- Public chat methods ----------
    async def chat(
        self,
        messages: List[ChatMessage],
        *,
        model: Optional[str] = None,
        options: Optional[Options] = None,
        keep_alive: Optional[str] = None,
        **kwargs: Any,
    ) -> StreamChunk:
        """Non‑streaming chat via ``/api/chat``.

        Args:
            messages: List of message dicts (e.g., [{"role": "user", "content": "..."}]).
            model: Model name (default: config.model).
            options: Model parameters.
            keep_alive: Duration to keep model loaded in memory.
            **kwargs: Additional payload fields.

        Returns:
            The complete response dictionary.

        Raises:
            OllamaConnectionError: On network/fetch errors.
            OllamaHTTPError: On non‑2xx HTTP status.
            OllamaResponseError: On invalid response.
            ValueError: On invalid arguments.
        """
        if not messages or not isinstance(messages, list):
            raise ValueError("messages must be a non-empty list of dicts")

        payload: ChatPayload = {
            "model": model or self._config.model,
            "messages": messages,
            "stream": False,
            "keep_alive": keep_alive or self._config.keep_alive,
        }
        if options:
            payload["options"] = options
        payload.update(kwargs)

        return await self._request("chat", payload)

    async def chat_stream(
        self,
        messages: List[ChatMessage],
        *,
        model: Optional[str] = None,
        options: Optional[Options] = None,
        keep_alive: Optional[str] = None,
        **kwargs: Any,
    ) -> AsyncGenerator[StreamChunk, None]:
        """Streaming chat via ``/api/chat``.

        Args:
            messages: List of message dicts.
            model: Model name (default: config.model).
            options: Model parameters.
            keep_alive: Duration to keep model loaded in memory.
            **kwargs: Additional payload fields.

        Yields:
            Response chunks as they arrive from the server.

        Raises:
            OllamaConnectionError: On network/fetch errors.
            OllamaHTTPError: On non‑2xx HTTP status.
            OllamaResponseError: On invalid response line.
            ValueError: On invalid arguments.
        """
        if not messages or not isinstance(messages, list):
            raise ValueError("messages must be a non-empty list of dicts")

        payload: ChatPayload = {
            "model": model or self._config.model,
            "messages": messages,
            "stream": True,
            "keep_alive": keep_alive or self._config.keep_alive,
        }
        if options:
            payload["options"] = options
        payload.update(kwargs)

        async for chunk in self._stream_request("chat", payload):
            yield chunk

    # ---------- Internal HTTP request methods ----------
    async def _request(
        self,
        endpoint: str,
        payload: Union[GeneratePayload, ChatPayload],
    ) -> StreamChunk:
        """Perform a non‑streaming request with automatic retries.

        Args:
            endpoint: API endpoint name (``"generate"`` or ``"chat"``).
            payload: Request payload.

        Returns:
            Parsed JSON response.

        Raises:
            OllamaConnectionError: On network/fetch errors after retries.
            OllamaHTTPError: On non‑2xx HTTP status after retries.
            OllamaResponseError: On invalid response.
        """
        _validate_payload(payload, endpoint)
        session = await self._ensure_session()
        url = f"{self._base_url}/api/{_sanitize_url(endpoint)}"

        last_exception: Optional[Exception] = None
        for attempt in range(self._config.retry_attempts + 1):
            try:
                async with self._semaphore:
                    async with session.post(url, json=payload) as response:
                        if response.status in RETRYABLE_STATUS_CODES:
                            if attempt < self._config.retry_attempts:
                                backoff = _compute_backoff(attempt)
                                logger.warning(
                                    "Status %s on attempt %d, retrying in %.2fs",
                                    response.status,
                                    attempt + 1,
                                    backoff,
                                )
                                await asyncio.sleep(backoff)
                                continue
                            else:
                                body = await self._safe_read_response(response)
                                raise self._build_http_error(
                                    response.status, body, endpoint
                                )

                        if response.status != 200:
                            body = await self._safe_read_response(response)
                            raise self._build_http_error(
                                response.status, body, endpoint
                            )

                        data = await response.json()
                        logger.debug(
                            "Non‑streaming request to %s succeeded (status %s)",
                            url,
                            response.status,
                        )
                        return data

            except asyncio.TimeoutError as exc:
                raise OllamaTimeoutError(
                    f"Request to {url} timed out after {self._config.timeout}s"
                ) from exc
            except aiohttp.ClientConnectionError as exc:
                last_exception = exc
                if attempt < self._config.retry_attempts:
                    backoff = _compute_backoff(attempt)
                    logger.warning(
                        "Connection error on attempt %d: %s. Retrying in %.2fs",
                        attempt + 1,
                        exc,
                        backoff,
                    )
                    await asyncio.sleep(backoff)
                    continue
                raise OllamaConnectionError(
                    f"Connection error to {url} after {self._config.retry_attempts} retries: {exc}"
                ) from exc
            except (aiohttp.ClientError, OllamaHTTPError) as exc:
                raise OllamaConnectionError(
                    f"Client error during request to {url}: {exc}"
                ) from exc
            except json.JSONDecodeError as exc:
                raise OllamaResponseError(
                    f"Invalid JSON response from {url}: {exc}"
                ) from exc

        # Should not reach here, but for safety:
        raise OllamaClientError(
            f"Request to {url} failed after {self._config.retry_attempts + 1} attempts"
        )

    async def _stream_request(
        self,
        endpoint: str,
        payload: Union[GeneratePayload, ChatPayload],
    ) -> AsyncGenerator[StreamChunk, None]:
        """Perform a streaming request with automatic retries.

        Args:
            endpoint: API endpoint name.
            payload: Request payload.

        Yields:
            Parsed JSON lines from the streaming response.

        Raises:
            OllamaConnectionError: On network/fetch errors after retries.
            OllamaHTTPError: On non‑2xx HTTP status after retries.
            OllamaResponseError: On invalid JSON line.
        """
        _validate_payload(payload, endpoint)
        session = await self._ensure_session()
        url = f"{self._base_url}/api/{_sanitize_url(endpoint)}"

        last_exception: Optional[Exception] = None
        for attempt in range(self._config.retry_attempts + 1):
            try:
                async with self._semaphore:
                    async with session.post(url, json=payload) as response:
                        if response.status in RETRYABLE_STATUS_CODES:
                            if attempt < self._config.retry_attempts:
                                backoff = _compute_backoff(attempt)
                                logger.warning(
                                    "Status %s on streaming attempt %d, retrying in %.2fs",
                                    response.status,
                                    attempt + 1,
                                    backoff,
                                )
                                await asyncio.sleep(backoff)
                                continue
                            else:
                                body = await self._safe_read_response(response)
                                raise self._build_http_error(
                                    response.status, body, endpoint
                                )

                        if response.status != 200:
                            body = await self._safe_read_response(response)
                            raise self._build_http_error(
                                response.status, body, endpoint
                            )

                        logger.debug(
                            "Streaming request to %s started (status %s)",
                            url,
                            response.status,
                        )
                        async for line in response.content:
                            if line.strip():
                                chunk = _parse_stream_line(line)
                                yield chunk
                                # Early exit if final chunk detected (done flag)
                                if chunk.get("done", False):
                                    logger.debug("Stream finished (done=True received)")
                                    return
                        # If we exit normally, the stream completed successfully
                        logger.debug("Stream finished normally")
                        return

            except asyncio.TimeoutError as exc:
                raise OllamaTimeoutError(
                    f"Streaming request to {url} timed out after {self._config.timeout}s"
                ) from exc
            except aiohttp.ClientConnectionError as exc:
                last_exception = exc
                if attempt < self._config.retry_attempts:
                    backoff = _compute_backoff(attempt)
                    logger.warning(
                        "Connection error on streaming attempt %d: %s. Retrying in %.2fs",
                        attempt + 1,
                        exc,
                        backoff,
                    )
                    await asyncio.sleep(backoff)
                    continue
                raise OllamaConnectionError(
                    f"Connection error to {url} after {self._config.retry_attempts} retries: {exc}"
                ) from exc
            except (aiohttp.ClientError, OllamaHTTPError) as exc:
                raise OllamaConnectionError(
                    f"Client error during streaming request to {url}: {exc}"
                ) from exc
            except json.JSONDecodeError as exc:
                raise OllamaResponseError(
                    f"Invalid JSON line from {url}: {exc}"
                ) from exc

        raise OllamaClientError(
            f"Streaming request to {url} failed after {self._config.retry_attempts + 1} attempts"
        )

    # ---------- Helper methods ----------
    @staticmethod
    async def _safe_read_response(response: aiohttp.ClientResponse) -> str:
        """Safely read the response body, handling potential errors.

        Args:
            response: aiohttp response object.

        Returns:
            Response body as string, or empty string on failure.
        """
        try:
            return await response.text()
        except (aiohttp.ClientError, asyncio.TimeoutError) as exc:
            logger.warning("Failed to read response body: %s", exc)
            return ""

    @staticmethod
    def _build_http_error(
        status_code: int,
        body: str,
        endpoint: str,
    ) -> OllamaHTTPError:
        """Construct the appropriate HTTP error based on status code.

        Args:
            status_code: HTTP status code.
            body: Response body string.
            endpoint: API endpoint name.

        Returns:
            OllamaHTTPError or OllamaRateLimitError instance.
        """
        message = (
            f"API {endpoint} returned HTTP {status_code}: "
            f"{body[:200] if body else 'No response body'}"
        )
        if status_code == 429:
            return OllamaRateLimitError(message, status_code, body)
        return OllamaHTTPError(message, status_code, body)