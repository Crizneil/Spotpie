"""
ANSI Color and Theme Management for CRIZ_SPOTPIE.

Provides dark-terminal IT utility aesthetic with Cyan/Blue emphasis,
regex-based ANSI stripping for clean border alignment, and support
for multiple color themes and monochrome fallback.
"""

import os
import re
import sys

# ANSI escape sequence regex
ANSI_ESCAPE_PATTERN = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

# Color enabled state
_COLORS_ENABLED = True
_ACTIVE_THEME = "cyan_blue"


def set_colors_enabled(enabled: bool) -> None:
    """Explicitly enable or disable ANSI colors."""
    global _COLORS_ENABLED
    _COLORS_ENABLED = enabled


def are_colors_enabled() -> bool:
    """Check whether colors are enabled."""
    global _COLORS_ENABLED
    if not _COLORS_ENABLED:
        return False
    # Respect NO_COLOR standard (https://no-color.org)
    if "NO_COLOR" in os.environ:
        return False
    # Check if terminal supports colors or stdout is a tty
    return sys.stdout.isatty() or os.environ.get("FORCE_COLOR") == "1"


def set_theme(theme_name: str) -> None:
    """Set the active color theme."""
    global _ACTIVE_THEME
    if theme_name in ("cyan_blue", "neon_cyan", "monochrome"):
        _ACTIVE_THEME = theme_name


def get_active_theme() -> str:
    """Get the name of the currently active theme."""
    return _ACTIVE_THEME


def strip_ansi(text: str) -> str:
    """Remove all ANSI color codes from a string for accurate length calculations."""
    if not text:
        return ""
    return ANSI_ESCAPE_PATTERN.sub("", text)


def visible_len(text: str) -> int:
    """Return the visible length of a string ignoring ANSI escape codes."""
    return len(strip_ansi(text))


# Raw ANSI constants
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
UNDERLINE = "\033[4m"

# Standard / Bright Colors
BLACK = "\033[30m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"
WHITE = "\033[97m"
DARK_CYAN = "\033[36m"
DARK_BLUE = "\033[34m"
GRAY = "\033[90m"


def colorize(text: str, code: str) -> str:
    """Wrap text in an ANSI code if colors are enabled."""
    if not are_colors_enabled() or _ACTIVE_THEME == "monochrome":
        return str(text)
    return f"{code}{text}{RESET}"


# High-level semantic styling functions
def c_primary(text: str) -> str:
    """Primary brand color (Bright Cyan)."""
    if _ACTIVE_THEME == "neon_cyan":
        return colorize(text, BOLD + CYAN)
    return colorize(text, CYAN)


def c_secondary(text: str) -> str:
    """Secondary accent color (Blue / Dark Cyan)."""
    if _ACTIVE_THEME == "neon_cyan":
        return colorize(text, CYAN)
    return colorize(text, BLUE)


def c_accent(text: str) -> str:
    """Third accent color (Dark Cyan)."""
    return colorize(text, DARK_CYAN)


def c_success(text: str) -> str:
    """Success color (Bright Green)."""
    return colorize(text, GREEN)


def c_warning(text: str) -> str:
    """Warning color (Bright Yellow)."""
    return colorize(text, YELLOW)


def c_error(text: str) -> str:
    """Error color (Bright Red)."""
    return colorize(text, RED)


def c_dim(text: str) -> str:
    """Muted / Dim text (Gray)."""
    return colorize(text, GRAY)


def c_bold(text: str) -> str:
    """Bold text."""
    return colorize(text, BOLD)


def c_bold_primary(text: str) -> str:
    """Bold primary cyan text."""
    return colorize(text, BOLD + CYAN)


def c_bold_secondary(text: str) -> str:
    """Bold blue text."""
    return colorize(text, BOLD + BLUE)


def c_bold_white(text: str) -> str:
    """Bold white text."""
    return colorize(text, BOLD + WHITE)


def c_highlight(text: str) -> str:
    """Highlighted value text (White)."""
    return colorize(text, WHITE)


def c_border(text: str) -> str:
    """Border color (Cyan / Dark Cyan)."""
    if _ACTIVE_THEME == "neon_cyan":
        return colorize(text, CYAN)
    return colorize(text, DARK_CYAN)
