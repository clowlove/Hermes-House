"""
AIRecon TUI - Textual User Interface for autonomous cybersecurity agent.

Screens:
    - Target history (left panel)
    - Output log (main area)
    - Input field / status bar (bottom)

Requires: textual >= 0.52.0, Python >= 3.11
"""

from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Optional

from textual import work
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.reactive import reactive
from textual.widgets import (
    Button,
    Header,
    Input,
    Label,
    ListItem,
    ListView,
    RichLog,
    Static,
)

# ---------------------------------------------------------------------------
# Custom widgets
# ---------------------------------------------------------------------------


class TargetHistory(VerticalScroll):
    """Displays previously entered targets in a scrollable list."""

    DEFAULT_CSS = """
    TargetHistory {
        width: 30%;
        border-right: solid $primary;
        background: $panel;
    }
    TargetHistory > Static {
        padding: 0 1;
        text-style: bold;
        color: $text-muted;
    }
    TargetHistory > ListView {
        margin: 0 1;
    }
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._targets: list[str] = []

    def compose(self) -> ComposeResult:
        yield Static("Target History")
        yield ListView(id="history-list", initial_index=None)

    def add_target(self, target: str) -> None:
        """Append a target to the history list."""
        self._targets.append(target)
        list_view = self.query_one("#history-list", ListView)
        list_view.append(ListItem(Label(f"  {target}")))
        # Scroll to bottom to show new entry
        list_view.scroll_end(animate=False)

    def clear_history(self) -> None:
        """Remove all targets from the history panel."""
        self._targets.clear()
        list_view = self.query_one("#history-list", ListView)
        list_view.clear()


class OutputLog(RichLog):
    """Rich log widget adapted for reconnaissance output."""

    DEFAULT_CSS = """
    OutputLog {
        height: 1fr;
        border: none;
        background: $surface;
        padding: 0 1;
    }
    """

    def write_line(self, text: str, style: str = "") -> None:
        """Write a single line with optional style."""
        self.write(text + "\n")

    def write_separator(self, char: str = "─") -> None:
        """Write a separator line."""
        self.write(f"{char * 40}\n")


class StatusBar(Static):
    """Bottom status bar showing current agent state."""

    status = reactive("idle", init=False)

    def watch_status(self, old: str, new: str) -> None:
        """Update displayed status on change."""
        self.renderable = f" Status: {new.upper()} "
        self.refresh()


# ---------------------------------------------------------------------------
# Main Application
# ---------------------------------------------------------------------------


class AIReconTUI(App):
    """Textual UI for the AIRecon autonomous agent."""

    CSS = """
    Screen {
        layout: vertical;
    }

    #main-container {
        height: 1fr;
    }

    #input-container {
        height: 3;
        dock: bottom;
        background: $boost;
        border-top: solid $primary;
    }

    Input {
        width: 1fr;
        margin: 0 1;
    }

    Button {
        width: 12;
        margin: 0 1;
    }
    """

    TITLE = "AIRecon"
    SUB_TITLE = "Autonomous Reconnaissance Agent"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_target: Optional[str] = None

    def compose(self) -> ComposeResult:
        """Build the UI layout."""
        yield Header(show_clock=True)
        with Container(id="main-container"):
            with Horizontal():
                yield TargetHistory(id="history-panel")
                yield OutputLog(id="output-log", highlight=True, markup=True)
        with Horizontal(id="input-container"):
            yield Input(placeholder="Enter target (domain/IP/command)...", id="target-input")
            yield Button("Run", id="run-button", variant="primary")
            yield StatusBar(id="status-bar")

    def on_mount(self) -> None:
        """Actions to perform when the app starts."""
        self.query_one("#target-input", Input).focus()
        self._log_startup_message()

    def _log_startup_message(self) -> None:
        """Print initial banner to output log."""
        log = self.query_one("#output-log", OutputLog)
        log.write_separator("=")
        log.write_line(" AIRecon TUI ready", style="bold green")
        log.write_line(" Type a target or command and press Enter.", style="italic")
        log.write_separator("=")

    # ------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle user pressing Enter in the input field."""
        self._process_input(event.value)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle the Run button click."""
        input_widget = self.query_one("#target-input", Input)
        if input_widget.value.strip():
            self._process_input(input_widget.value)

    @work(thread=True)
    def _process_input(self, raw_input: str) -> None:
        """Process user input: target or command."""
        raw_input = raw_input.strip()
        if not raw_input:
            return

        # Update status to running
        self.call_from_thread(self._set_status, "running")

        # Log input to output
        log = self.query_one("#output-log", OutputLog)
        self.call_from_thread(
            log.write_line,
            f"[{datetime.now().strftime('%H:%M:%S')}] Target: {raw_input}",
            style="cyan",
        )

        # Add to history
        history = self.query_one("#history-panel", TargetHistory)
        self.call_from_thread(history.add_target, raw_input)

        # Placeholder for actual orchestration
        # In production, this would call the Orchestrator, Ollama client, etc.
        self.call_from_thread(log.write_line, " [+] Starting analysis...", style="yellow")
        asyncio.run(self._simulate_recon(raw_input))

        # Update status to idle
        self.call_from_thread(self._set_status, "idle")

    async def _simulate_recon(self, target: str) -> None:
        """Simulated reconnaissance workflow (placeholder)."""
        log = self.query_one("#output-log", OutputLog)
        log.write_line(f" [*] Checking target: {target}", style="dim")
        await asyncio.sleep(1.5)
        log.write_line(" [✓] Target reachable", style="green")
        await asyncio.sleep(1.0)
        log.write_line(" [→] Suggested next: subdomain enumeration", style="blue")
        log.write_separator()

    def _set_status(self, status: str) -> None:
        """Helper to update status bar from any thread."""
        self.query_one("#status-bar", StatusBar).status = status

    def action_quit(self) -> None:
        """Custom quit action (Ctrl+Q)."""
        self.exit()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app = AIReconTUI()
    app.run()