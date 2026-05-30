#!/usr/bin/env python3
"""
AIRecon – Autonomous Cybersecurity Agent.

Initializes configuration, logging, signal handlers, and runs the Textual TUI
together with the orchestrator.  Provides a robust, production‑grade CLI with
comprehensive error handling, type annotations, security checks, and logging.

Dependencies: pip install textual pyyaml
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import os
import signal
import sys
from enum import IntEnum
from pathlib import Path
from types import FrameType
from typing import Final, NoReturn, Optional, final

import yaml
from yaml.error import YAMLError

from airecon.config import Config, load_config
from airecon.orchestrator import Orchestrator
from airecon.tui.app import AIReconApp

logger: logging.Logger = logging.getLogger(__name__)

__version__: Final[str] = "1.0.0"

# ---------------------------------------------------------------------------
# Exit codes – POSIX style
# ---------------------------------------------------------------------------
class ExitCode(IntEnum):
    """POSIX exit codes for distinct failure modes."""
    SUCCESS = 0
    CONFIG_ERROR = 1          # Configuration file missing, malformed, or insecure
    RUNTIME_ERROR = 2         # Unhandled exception during execution


class ConfigLoadError(Exception):
    """Custom exception for configuration loading/validation failures.

    Wraps the original exception to preserve the root cause chain.
    """

    def __init__(self, message: str, original_exception: Optional[BaseException] = None) -> None:
        super().__init__(message)
        self.original_exception: Optional[BaseException] = original_exception


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------
@final
def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    """Parse command‑line arguments.

    Args:
        argv: List of argument strings (default: ``sys.argv[1:]``).

    Returns:
        ``argparse.Namespace`` with attributes:
            * ``config`` (Path) – configuration file path.
            * ``verbose`` (bool) – debug logging flag.
            * ``version`` (bool) – version display flag.

    Raises:
        SystemExit: If argument parsing fails (argparse default behaviour).
    """
    parser = argparse.ArgumentParser(
        description=(
            "AIRecon – Autonomous Cybersecurity Agent with Ollama "
            "and Kali Docker Sandbox"
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        epilog="See https://github.com/pikpikcu/airecon for details.",
    )
    parser.add_argument(
        "-c",
        "--config",
        type=Path,
        default=Path("config.yaml"),
        metavar="FILE",
        help="Path to YAML configuration file",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose (debug) logging",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"AIRecon {__version__}",
        help="Show version number and exit",
    )
    return parser.parse_args(argv)


# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------
@final
def setup_logging(verbose: bool = False) -> None:
    """Configure application logging.

    Writes to *stderr* to avoid interfering with the Textual TUI. Third‑party
    library loggers are throttled to WARNING to reduce noise.

    Args:
        verbose: If ``True``, set root logger level to ``DEBUG``; otherwise
            ``INFO``.
    """
    level: int = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stderr,
    )
    # Reduce verbosity from noisy libraries
    library_loggers: Final[tuple[str, ...]] = (
        "asyncio", "yaml", "urllib3", "httpcore", "httpx"
    )
    for lib in library_loggers:
        logging.getLogger(lib).setLevel(logging.WARNING)
    logger.debug("Logging configured at %s level", "DEBUG" if verbose else "INFO")


# ---------------------------------------------------------------------------
# Configuration loading with security checks
# ---------------------------------------------------------------------------
@final
def load_and_validate_config(config_path: Path) -> Config:
    """Load and validate the YAML configuration file.

    Security checks performed:
        * File exists and is a regular file.
        * File is not world‑writable.
        * File is readable (permission check).
        * YAML is syntactically valid.
        * Schema validation via :func:`airecon.config.load_config`.

    Args:
        config_path: Path to the configuration file.

    Returns:
        A validated :class:`Config` instance.

    Raises:
        ConfigLoadError: If any loading or validation step fails.
    """
    config_path = config_path.resolve()

    # --- existence and type ---
    if not config_path.exists():
        raise ConfigLoadError(f"Configuration file not found: {config_path}")
    if not config_path.is_file():
        raise ConfigLoadError(f"Path is not a regular file: {config_path}")

    # --- security: check file permissions (not world-writable) ---
    try:
        file_stat = config_path.stat()
        if file_stat.st_mode & 0o002:
            raise ConfigLoadError(
                f"Configuration file is world‑writable – refusing to load: {config_path}"
            )
    except OSError as exc:
        raise ConfigLoadError(
            f"Cannot stat configuration file: {exc}",
            original_exception=exc,
        )

    # --- YAML syntax and reading ---
    try:
        with config_path.open("r", encoding="utf-8") as fh:
            raw_config: Optional[dict] = yaml.safe_load(fh)
    except PermissionError as exc:
        raise ConfigLoadError(
            f"Permission denied reading configuration file: {exc}",
            original_exception=exc,
        )
    except IsADirectoryError as exc:
        raise ConfigLoadError(
            f"Configuration path is a directory: {exc}",
            original_exception=exc,
        )
    except OSError as exc:
        raise ConfigLoadError(
            f"I/O error reading configuration file: {exc}",
            original_exception=exc,
        )
    except YAMLError as exc:
        raise ConfigLoadError(
            f"Invalid YAML syntax in configuration file: {exc}",
            original_exception=exc,
        )

    if raw_config is None:
        raise ConfigLoadError(f"Configuration file is empty: {config_path}")

    # --- schema validation via the application's own loader ---
    try:
        config: Config = load_config(config_path)  # re‑reads file (minor inefficiency)
    except (YAMLError, ValueError, TypeError, KeyError) as exc:
        raise ConfigLoadError(
            f"Configuration validation failed: {exc}",
            original_exception=exc,
        )
    return config


# ---------------------------------------------------------------------------
# Signal handler registration
# ---------------------------------------------------------------------------
@final
def setup_signal_handlers(app: AIReconApp, loop: asyncio.AbstractEventLoop) -> None:
    """Register signal handlers for graceful shutdown.

    Handles SIGTERM and SIGINT. If the event loop is not available (None),
    registration is skipped with a warning.

    Args:
        app: The Textual application instance.
        loop: The running asyncio event loop.
    """
    if loop is None:
        logger.warning("No event loop available – signal handlers not registered")
        return

    def _signal_handler(signum: int, frame: Optional[FrameType]) -> None:
        """Handle incoming signal: schedule app exit and stop loop."""
        logger.info("Received signal %d – initiating graceful shutdown", signum)
        # Schedule the app's exit coroutine on the event loop
        if hasattr(app, 'exit') and callable(app.exit):
            # asyncio.ensure_future is deprecated; use loop.create_task
            loop.create_task(app.exit())
        else:
            logger.warning("App has no exit method; stopping event loop directly")
            loop.stop()

    signal.signal(signal.SIGTERM, _signal_handler)
    signal.signal(signal.SIGINT, _signal_handler)
    logger.debug("Signal handlers registered for SIGTERM and SIGINT")


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------
@final
async def async_main(config_path: Path, verbose: bool) -> int:
    """Asynchronous application entry point.

    Loads configuration, initializes the app and orchestrator, and runs the
    Textual TUI.  Returns an exit code.

    Args:
        config_path: Path to the configuration file.
        verbose: Enable debug logging if ``True``.

    Returns:
        ``ExitCode.SUCCESS`` on clean exit, ``ExitCode.RUNTIME_ERROR`` on
        unhandled exception.
    """
    # Logging must already be set up by caller (main)
    try:
        config: Config = load_and_validate_config(config_path)
    except ConfigLoadError as exc:
        logger.error("Configuration error: %s", exc)
        return ExitCode.CONFIG_ERROR

    logger.info("Configuration loaded successfully from %s", config_path)

    # Initialize application and orchestrator
    try:
        app: AIReconApp = AIReconApp(config=config)
        orchestrator: Orchestrator = Orchestrator(config=config)
    except Exception as exc:
        logger.exception("Failed to initialize application components: %s", exc)
        return ExitCode.RUNTIME_ERROR

    # Register signal handlers for graceful shutdown
    loop: asyncio.AbstractEventLoop = asyncio.get_running_loop()
    setup_signal_handlers(app, loop)

    # Run the Textual TUI (this blocks until the app exits)
    try:
        await app.run_async()
    except asyncio.CancelledError:
        logger.info("Application was cancelled")
    except Exception as exc:
        logger.exception("Unhandled exception during TUI execution: %s", exc)
        return ExitCode.RUNTIME_ERROR
    finally:
        logger.info("Shutting down orchestrator")
        try:
            await orchestrator.shutdown()
        except Exception as exc:
            logger.warning("Orchestrator shutdown raised an exception: %s", exc)

    return ExitCode.SUCCESS


@final
def main(argv: Optional[list[str]] = None) -> int:
    """Parse arguments, configure logging, and run the application.

    Args:
        argv: Command‑line argument list (default: :data:`sys.argv[1:]`).

    Returns:
        Exit code suitable for ``sys.exit()``.
    """
    # Parse command line
    try:
        args: argparse.Namespace = parse_args(argv)
    except SystemExit as exc:
        # argparse already printed the error and exited; propagate the code
        return exc.code if isinstance(exc.code, int) else 1

    # Configure logging
    setup_logging(verbose=args.verbose)
    logger.debug("AIRecon version %s starting", __version__)

    # Validate config path early (path type)
    config_path: Path = args.config
    if not isinstance(config_path, Path):
        logger.error("Config path must be a Path object; got %s", type(config_path).__name__)
        return ExitCode.CONFIG_ERROR

    # Run async entry
    try:
        exit_code: int = asyncio.run(async_main(config_path, args.verbose))
    except KeyboardInterrupt:
        logger.info("Interrupted by user (KeyboardInterrupt)")
        exit_code = ExitCode.SUCCESS
    except Exception as exc:
        logger.exception("Unhandled top‑level exception: %s", exc)
        exit_code = ExitCode.RUNTIME_ERROR
    finally:
        logging.shutdown()

    return exit_code


# ---------------------------------------------------------------------------
# Script entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    sys.exit(main())