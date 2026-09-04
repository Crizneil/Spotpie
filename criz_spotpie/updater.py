"""
Update Checker and Synchronizer for CRIZ_SPOTPIE.

Fetches remote release and version data from the official upstream SpotX-Bash
repository and handles safe script updates.
"""

import re
import urllib.request
from typing import Any, Dict, Optional, Tuple

from criz_spotpie.config import get_config
from criz_spotpie.spotx import (
    fetch_upstream_spotx,
    get_cached_spotx_version,
    is_spotx_cached,
)
from criz_spotpie.utils import log_debug, log_error, log_info


def _parse_version_tuple(v_str: str) -> tuple:
    """Parse a version string like 1.2.98.301 into a tuple of integers for comparison."""
    if not v_str:
        return (0,)
    parts = []
    for chunk in v_str.split("."):
        try:
            parts.append(int(re.sub(r"\D", "", chunk)))
        except ValueError:
            parts.append(0)
    return tuple(parts)


def fetch_latest_upstream_version() -> Tuple[Optional[str], Optional[str]]:
    """
    Fetch the latest buildVer from the upstream repository URL.
    Returns (latest_version, error_message).
    """
    config = get_config()
    url = config.get(
        "spotx_repo_url",
        "https://raw.githubusercontent.com/SpotX-Official/SpotX-Bash/main/spotx.sh",
    )
    log_info(f"Checking upstream version from {url}")

    try:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Criz_Spotpie-Linux/1.0.0",
                "Range": "bytes=0-2048",  # Request only header chunk for fast response
            },
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            content = resp.read().decode("utf-8", errors="ignore")

        match = re.search(r'buildVer=["\']([^"\']+)["\']', content)
        if match:
            full_ver = match.group(1)
            clean_match = re.match(r"^(\d+\.\d+\.\d+\.\d+)", full_ver)
            version = clean_match.group(1) if clean_match else full_ver
            log_debug(f"Remote upstream version detected: {version}")
            return version, None

        return None, "Could not locate version identifier in upstream response."
    except Exception as exc:
        err = f"Network error checking upstream: {exc}"
        log_error(err)
        return None, err


def check_spotx_update() -> Dict[str, Any]:
    """
    Check whether a new SpotX version is available.
    Returns dictionary with installed, latest, update_available, and error.
    """
    installed = get_cached_spotx_version()
    latest, err = fetch_latest_upstream_version()

    if err or not latest:
        return {
            "installed_version": installed or "Not Installed",
            "latest_version": "Unknown",
            "update_available": False,
            "error": err,
        }

    if not installed:
        # Not downloaded yet
        return {
            "installed_version": "Not Installed",
            "latest_version": latest,
            "update_available": True,
            "error": None,
        }

    installed_t = _parse_version_tuple(installed)
    latest_t = _parse_version_tuple(latest)
    update_available = latest_t > installed_t

    return {
        "installed_version": installed,
        "latest_version": latest,
        "update_available": update_available,
        "error": None,
    }


def update_spotx_now() -> Tuple[bool, str]:
    """Download and refresh the upstream SpotX script."""
    return fetch_upstream_spotx(force=True)
