"""
Custom Textual widgets for AIRecon TUI.

Provides:
- AsciiLogView: Enhanced log viewer with timestamps, severity levels, and auto-scroll.
- ScrollableOutput: Simple scrollable container for displaying multi-line text output.

All widgets are designed for use within the Textual TUI and comply with
Textual >=0.52.0 and Python >=3.11 requirements.
"""

from datetime import datetime
 from typing import Optional, List, Literal

 from rich.text import Text
 from rich.style import Style
 from textual.widgets import RichLog, Static, ScrollView
 from textual.reactive import reactive
 from textual import events


 class AsciiLogView(RichLog):
     """
     A custom log viewer that extends RichLog with timestamped entries,
     severity level coloring, and a configurable maximum line count.

     Usage:
         log_view = AsciiLogView(max_lines=500)
         log_view.write_line("Task started", level="info")
         log_view.write_line("Connection error", level="error")
     """

     DEFAULT_CSS = """
     AsciiLogView {
         height: 1fr;
         border: solid $secondary;
         padding: 0 1;
     }
     """

     # Define severity colors using Rich styles
     SEVERITY_STYLES: dict = {
         "info": Style(color="green"),
         "warning": Style(color="yellow"),
         "error": Style(color="red"),
         "debug": Style(color="blue"),
         "critical": Style(color="white", bgcolor="red"),
     }

     def __init__(
         self,
         max_lines: int = 1000,
         show_timestamp: bool = True,
         *args,
         **kwargs,
     ):
         """
         Initialize the log view.

         Args:
             max_lines: Maximum number of lines to keep in the log.
             show_timestamp: Whether to prepend each line with a timestamp.
         """
         # RichLog uses markdown by default; we want plain text/rich
         super().__init__(markup=True, highlight=True, *args, **kwargs)
         self.max_lines = max_lines
         self.show_timestamp = show_timestamp

     def write_line(
         self,
         message: str,
         level: str = "info",
         timestamp: Optional[datetime] = None,
     ) -> None:
         """
         Add a log line with proper formatting.

         Args:
             message: The log message to display.
             level: Severity level (info, warning, error, debug, critical).
             timestamp: Optional custom datetime; if None, current time is used.
         """
         if timestamp is None:
             timestamp = datetime.now()

         # Build the line parts
         parts: List[str] = []

         if self.show_timestamp:
             ts = timestamp.strftime("%H:%M:%S")
             parts.append(f"[{ts}]")

         # Format level as a short tag
         level_tag = level.upper()[:4].ljust(4)
         parts.append(f"[{level_tag}]")

         parts.append(message)

         full_text = " ".join(parts)

         # Create a Rich Text object with appropriate style
         style = self.SEVERITY_STYLES.get(level, Style())
         rich_text = Text(full_text, style=style)

         # Write to widget (RichLog automatically handles scrolling)
         self.write(rich_text)

         # Enforce max_lines by trimming oldest lines
         self._trim_lines()

     def _trim_lines(self) -> None:
         """
         Remove lines exceeding max_lines from the beginning of the log.
         This is a best-effort operation; exact line count depends on RichLog internals.
         """
         # RichLog inherits from Widget which has a `lines` attribute
         # that stores rendered lines. We can access it but it's not officially
         # public. We'll use a try/except to avoid breaking on Textual updates.
         try:
             # Access internal line storage
             internal_lines = self._lines  # type: ignore[attr-defined]
             if len(internal_lines) > self.max_lines:
                 excess = len(internal_lines) - self.max_lines
                 # Remove the oldest lines
                 del internal_lines[:excess]
                 # Force a refresh
                 self.refresh()
         except AttributeError:
             # Fallback: clear everything if internal is not accessible?
             # Better to do nothing and risk memory growth than crash.
             pass

     def clear_log(self) -> None:
         """Clear all log entries."""
         self.clear()


 class ScrollableOutput(ScrollView):
     """
     A scrollable container that displays multi-line text output.
     Suitable for showing command output, scan results, etc.

     The content is rendered as plain text with optional syntax highlighting
     (via Rich markup if `markup=True` is passed).

     Usage:
         output = ScrollableOutput()
         output.update_output("Nmap results:\n22/tcp open  ssh")
     """

     DEFAULT_CSS = """
     ScrollableOutput {
         height: 1fr;
         border: solid $primary;
         padding: 0 1;
     }
     """

     def __init__(
         self,
         initial_content: str = "",
         markup: bool = False,
         *args,
         **kwargs,
     ):
         """
         Initialize the scrollable output.

         Args:
             initial_content: Text to display initially.
             markup: If True, Rich markup is enabled (e.g., [red]text[/red]).
         """
         super().__init__(*args, **kwargs)
         self._markup = markup
         self._static: Optional[Static] = None
         self._set_initial_content(initial_content)

     def on_mount(self) -> None:
         """Create the internal Static widget after mount."""
         self._static = Static(
             self._initial_content,
             markup=self._markup,
         )
         self._static.styles.width = "100%"
         self._static.styles.height = "auto"
         self.mount(self._static)

     def _set_initial_content(self, content: str) -> None:
         """Store initial content to be set after mount."""
         self._initial_content = content

     def update_output(self, text: str) -> None:
         """
         Replace the content of the scrollable output with new text.

         Args:
             text: The new text to display.
         """
         if self._static is not None:
             self._static.update(text)
             # Scroll to top after update for consistency
             self.scroll_home(animate=False)

     def append_output(self, text: str) -> None:
         """
         Append text to the current output content.

         Args:
             text: Text to append (typically a new line).
         """
         if self._static is not None:
             current = self._static.renderable or ""
             new_content = f"{current}\n{text}"
             self._static.update(new_content)
             # Auto-scroll to bottom for continuous output
             self.scroll_end(animate=False)

     @property
     def content(self) -> str:
         """Return the current displayed content."""
         if self._static is not None:
             return str(self._static.renderable)
         return self._initial_content

     def clear(self) -> None:
         """Clear all content."""
         self.update_output("")

     def ensure_fit(self) -> None:
         """
         Adjust widget size to fit content if needed.
         Called internally when content changes.
         """
         if self._static is not None:
             self._static.styles.height = "auto"
             self._static.refresh()