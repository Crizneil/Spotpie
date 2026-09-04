"""
Diagnostics and Status Reporting for CRIZ_SPOTPIE.

Provides non-destructive status checks for Spotify, upstream SpotX,
and Criz_Spotpie runtime configurations.
"""

from typing import List, Tuple

from criz_spotpie import __version__
from criz_spotpie.banner import render_card
from criz_spotpie.colors import c_dim, c_error, c_highlight, c_success, c_warning
from criz_spotpie.config import get_config
from criz_spotpie.spotify import SpotifyInstallation, detect_spotify
from criz_spotpie.spotx import get_cached_spotx_version, is_spotx_cached


def get_status_data(custom_path: str = None) -> List[Tuple[str, str]]:
    """Collect read-only diagnostic data."""
    spotify = detect_spotify(custom_path=custom_path)
    spotx_cached = is_spotx_cached()
    spotx_version = get_cached_spotx_version()

    # Spotify status
    if spotify.installed:
        s_status = c_success("Installed")
        s_path = c_highlight(spotify.display_path)
    else:
        s_status = c_error("Not Found")
        s_path = c_dim("N/A")

    # SpotX status
    if spotx_cached:
        sx_status = c_success("Detected")
        sx_ver = c_highlight(spotx_version or "Cached")
    else:
        sx_status = c_dim("Not Cached")
        sx_ver = c_dim("N/A")

    # Patch / Backup status
    if spotify.installed:
        if spotify.has_backup:
            patch_status = c_success("Patched (Backups present)")
        elif spotify.is_patched:
            patch_status = c_warning("Patched")
        else:
            patch_status = c_dim("Original / Unmodified")
    else:
        patch_status = c_dim("N/A")

    items = [
        ("Spotify", s_status),
        ("Spotify Path", s_path),
        ("SpotX", sx_status),
        ("SpotX Version", sx_ver),
        ("Patch Status", patch_status),
        ("Criz_Spotpie", c_highlight(__version__)),
    ]
    return items


def render_status_card(width: int = 44) -> str:
    """Render the official status card matching project specification."""
    items = get_status_data()
    return render_card("CRIZ_SPOTPIE STATUS", items, width=width)
