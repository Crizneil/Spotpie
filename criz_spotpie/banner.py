"""
ASCII Banners, Header Boxes, and Card Formatting for CRIZ_SPOTPIE.

Provides consistent IT-utility dark aesthetic using Unicode double-line
and single-line boxes, with ANSI-safe width calculation.
"""

from typing import List, Optional
from criz_spotpie.colors import (
    c_bold_primary,
    c_bold_white,
    c_border,
    c_dim,
    c_highlight,
    c_primary,
    c_secondary,
    visible_len,
)

# Box dimensions
DEFAULT_WIDTH = 52


def render_box(
    lines: List[str],
    width: int = DEFAULT_WIDTH,
    border_color_func=c_border,
) -> str:
    """Render a list of strings inside a double-line Unicode box."""
    inner_width = width - 2  # Subtract borders '║' and '║'
    out = []

    # Top border
    out.append(border_color_func(f"╔{'═' * inner_width}╗"))

    for line in lines:
        v_len = visible_len(line)
        if v_len > inner_width:
            # Line is too long, just include as is with border
            padding = 0
            out.append(f"{border_color_func('║')}{line}{border_color_func('║')}")
        else:
            padding = inner_width - v_len
            # Check if line already has custom padding or if we should right-pad
            out.append(
                f"{border_color_func('║')}{line}{' ' * padding}{border_color_func('║')}"
            )

    # Bottom border
    out.append(border_color_func(f"╚{'═' * inner_width}╝"))
    return "\n".join(out)


def center_line(text: str, width: int = DEFAULT_WIDTH - 2) -> str:
    """Center text within a given visible width."""
    v_len = visible_len(text)
    if v_len >= width:
        return text
    left_pad = (width - v_len) // 2
    right_pad = width - v_len - left_pad
    return f"{' ' * left_pad}{text}{' ' * right_pad}"


def get_startup_banner(width: int = DEFAULT_WIDTH) -> str:
    """Generate the official startup banner box."""
    inner_width = width - 2
    lines = [
        "",
        center_line(c_bold_primary("CRIZ_SPOTPIE"), inner_width),
        center_line(c_secondary("Spotify Terminal Utility"), inner_width),
        center_line(c_dim("v1.0.0 • Linux Edition"), inner_width),
        "",
    ]
    return render_box(lines, width=width)


def get_menu_header(width: int = DEFAULT_WIDTH) -> str:
    """Generate the main menu header box."""
    inner_width = width - 2
    top = c_border(f"╔{'═' * inner_width}╗")
    title_line = (
        f"{c_border('║')}{center_line(c_bold_primary('CRIZ_SPOTPIE'), inner_width)}{c_border('║')}"
    )
    divider = c_border(f"╠{'═' * inner_width}╣")
    return f"{top}\n{title_line}\n{divider}"


def get_section_header(title: str, width: int = DEFAULT_WIDTH) -> str:
    """Generate a clean section title box."""
    inner_width = width - 2
    lines = [
        center_line(c_bold_white(title.upper()), inner_width),
    ]
    return render_box(lines, width=width)


def render_card(
    title: str,
    key_values: List[tuple[str, str]],
    width: int = 48,
) -> str:
    """
    Render a clean key-value card matching:
    ╔════════════════════════════════════════╗
    ║           CRIZ_SPOTPIE STATUS          ║
    ╠════════════════════════════════════════╣
    ║ Spotify        : Installed             ║
    ...
    ╚════════════════════════════════════════╝
    """
    inner_width = width - 2
    top = c_border(f"╔{'═' * inner_width}╗")
    title_line = (
        f"{c_border('║')}{center_line(c_bold_primary(title), inner_width)}{c_border('║')}"
    )
    divider = c_border(f"╠{'═' * inner_width}╣")

    body_lines = []
    # Find max key length for clean alignment
    max_key_len = max((visible_len(k) for k, _ in key_values), default=14)
    key_col_width = max(max_key_len, 14)

    for key, val in key_values:
        k_padded = key.ljust(key_col_width)
        row_content = f" {c_dim(k_padded)} : {val}"
        v_len = visible_len(row_content)
        padding = max(0, inner_width - v_len)
        body_lines.append(
            f"{c_border('║')}{row_content}{' ' * padding}{c_border('║')}"
        )

    bottom = c_border(f"╚{'═' * inner_width}╝")

    return "\n".join([top, title_line, divider] + body_lines + [bottom])
