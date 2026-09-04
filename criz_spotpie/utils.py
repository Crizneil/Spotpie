"""
Utility Functions for CRIZ_SPOTPIE.

Provides safe subprocess handling, spinners, structured file logging,
clean prompt helpers, and formatted user status messages.
"""

import logging
import os
import subprocess
import sys
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

from criz_spotpie.colors import (
    c_bold,
    c_bold_primary,
    c_dim,
    c_error,
    c_highlight,
    c_primary,
    c_secondary,
    c_success,
    c_warning,
)
from criz_spotpie.config import get_config

logger = logging.getLogger("criz_spotpie")


def setup_logging(debug: bool = False) -> None:
    """Initialize structured logging to ~/.config/criz-spotpie/logs/criz_spotpie.log."""
    config = get_config()
    log_file = config.logs_dir / "criz_spotpie.log"

    logger.setLevel(logging.DEBUG if debug else logging.INFO)
    logger.handlers.clear()

    # Formatter matching: 2026-09-04 23:10:12 INFO Starting Criz_Spotpie
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    try:
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG if debug else logging.INFO)
        logger.addHandler(file_handler)
    except OSError:
        pass  # If log file cannot be created, fail silently into null handler


def log_info(msg: str) -> None:
    """Log an INFO level message."""
    logger.info(msg)


def log_debug(msg: str) -> None:
    """Log a DEBUG level message."""
    logger.debug(msg)


def log_warning(msg: str) -> None:
    """Log a WARNING level message."""
    logger.warning(msg)


def log_error(msg: str) -> None:
    """Log an ERROR level message."""
    logger.error(msg)


def clear_screen() -> None:
    """Clear terminal screen cleanly without glitching."""
    if sys.stdout.isatty():
        # ANSI clear screen + cursor to top-left
        sys.stdout.write("\033[2J\033[H")
        sys.stdout.flush()


def run_command(
    cmd: List[str],
    timeout: Optional[int] = 180,
    cwd: Optional[Path] = None,
    env: Optional[dict] = None,
) -> Tuple[int, str, str]:
    """
    Safely execute a command as a subprocess list without shell expansion.
    Returns (returncode, stdout, stderr).
    """
    log_debug(f"Executing command: {' '.join(cmd)}")
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)

    try:
        proc = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout,
            cwd=str(cwd) if cwd else None,
            env=merged_env,
        )
        log_debug(f"Command returned {proc.returncode}")
        return proc.returncode, proc.stdout, proc.stderr
    except FileNotFoundError:
        err = f"Command not found: {cmd[0]}"
        log_error(err)
        return 127, "", err
    except subprocess.TimeoutExpired:
        err = f"Command timed out after {timeout} seconds"
        log_error(err)
        return 124, "", err
    except Exception as exc:
        err = f"Execution error: {exc}"
        log_error(err)
        return 1, "", err


class Spinner:
    """A clean, non-intrusive terminal spinner with cyan glyphs."""

    SPINNER_FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

    def __init__(self, message: str = "Processing..."):
        self.message = message
        self.stop_event = threading.Event()
        self.thread: Optional[threading.Thread] = None
        self.enabled = (
            get_config().get("animations_enabled", True)
            and sys.stdout.isatty()
        )

    def _spin(self) -> None:
        idx = 0
        while not self.stop_event.is_set():
            frame = self.SPINNER_FRAMES[idx % len(self.SPINNER_FRAMES)]
            glyph = c_bold_primary(frame)
            sys.stdout.write(f"\r  {glyph} {self.message}")
            sys.stdout.flush()
            idx += 1
            time.sleep(0.08)

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def start(self) -> None:
        """Start the spinner thread."""
        if not self.enabled:
            print(f"  * {self.message}")
            return
        self.stop_event.clear()
        self.thread = threading.Thread(target=self._spin, daemon=True)
        self.thread.start()

    def stop(self) -> None:
        """Stop spinner and clear current line."""
        if self.thread and self.thread.is_alive():
            self.stop_event.set()
            self.thread.join(timeout=0.5)
            # Clear line
            sys.stdout.write("\r\033[K")
            sys.stdout.flush()


def prompt_yes_no(question: str, default: bool = False) -> bool:
    """Prompt the user for a yes/no confirmation cleanly."""
    hint = "[Y/n]" if default else "[y/N]"
    prompt_str = f" {c_primary('?')} {question} {c_dim(hint)}: "
    try:
        user_input = input(prompt_str).strip().lower()
        if not user_input:
            return default
        return user_input in ("y", "yes", "true", "1")
    except (KeyboardInterrupt, EOFError):
        print("\n")
        log_info("User cancelled prompt")
        return False


def prompt_enter(message: str = "Press Enter to return...") -> None:
    """Wait for the user to press Enter."""
    prompt_str = f"\n {c_dim(message)}"
    try:
        input(prompt_str)
    except (KeyboardInterrupt, EOFError):
        print("")


def print_success(msg: str) -> None:
    """Print formatted success message."""
    print(f" {c_success('[SUCCESS]')} {msg}")


def print_error(msg: str, details: Optional[str] = None, exit_code: Optional[int] = None) -> None:
    """Print formatted error message according to project specs."""
    print(f"\n {c_error('[ERROR]')} {msg}\n")
    if exit_code is not None:
        print(f" Exit code: {exit_code}")
    if details:
        print(f" {c_dim(details)}\n")


def print_warning(msg: str) -> None:
    """Print formatted warning message."""
    print(f" {c_warning('[WARNING]')} {msg}")


def print_info(msg: str) -> None:
    """Print formatted information message."""
    print(f" {c_secondary('[INFO]')} {msg}")
