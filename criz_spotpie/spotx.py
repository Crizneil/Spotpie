"""
Upstream SpotX-Bash Wrapper and Integration for CRIZ_SPOTPIE.

Safely checks system prerequisites (bash, curl, perl, unzip, zip),
caches official upstream SpotX scripts, verifies script integrity,
checks system permissions, and invokes upstream operations with explicit
user confirmation and structured logging.
"""

import os
import re
import shutil
import urllib.request
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from criz_spotpie.config import get_config
from criz_spotpie.spotify import SpotifyInstallation
from criz_spotpie.utils import (
    log_debug,
    log_error,
    log_info,
    log_warning,
    run_command,
)

REQUIRED_SYSTEM_TOOLS = ["bash", "curl", "perl", "unzip", "zip"]


def check_dependencies() -> Dict[str, bool]:
    """Check availability of all required system utilities on PATH."""
    results = {}
    for tool in REQUIRED_SYSTEM_TOOLS:
        results[tool] = shutil.which(tool) is not None
    return results


def get_missing_dependencies() -> List[str]:
    """Return list of missing system tools."""
    deps = check_dependencies()
    return [tool for tool, available in deps.items() if not available]


def get_spotx_script_path() -> Path:
    """Return local path to the cached upstream spotx.sh script."""
    config = get_config()
    return config.upstream_dir / "spotx.sh"


def is_spotx_cached() -> bool:
    """Check if upstream SpotX script is locally downloaded and valid."""
    script = get_spotx_script_path()
    if not script.is_file() or script.stat().st_size < 1000:
        return False
    # Validate integrity
    try:
        with open(script, "r", encoding="utf-8", errors="ignore") as f:
            header = f.read(512)
            return "buildVer=" in header or "#!/usr/bin/env bash" in header
    except OSError:
        return False


def fetch_upstream_spotx(force: bool = False) -> Tuple[bool, str]:
    """
    Download or refresh the official upstream spotx.sh script.
    Saves to ~/.config/criz-spotpie/upstream/spotx.sh with 0o755 permissions.
    """
    script_path = get_spotx_script_path()
    if is_spotx_cached() and not force:
        return True, f"SpotX upstream script already cached at {script_path}"

    config = get_config()
    url = config.get(
        "spotx_repo_url",
        "https://raw.githubusercontent.com/SpotX-Official/SpotX-Bash/main/spotx.sh",
    )
    log_info(f"Fetching official upstream SpotX from {url}")
    script_path.parent.mkdir(parents=True, exist_ok=True)

    tmp_path = script_path.with_suffix(".tmp")
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Criz_Spotpie-Linux/1.0.0"},
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            content = resp.read().decode("utf-8")

        # Validate content looks like SpotX-Bash
        if "buildVer=" not in content and "#!/usr/bin/env bash" not in content:
            msg = "Downloaded file does not match expected SpotX-Bash script signature."
            log_error(msg)
            return False, msg

        with open(tmp_path, "w", encoding="utf-8") as f:
            f.write(content)

        os.chmod(tmp_path, 0o755)
        tmp_path.replace(script_path)
        log_info("SpotX upstream script downloaded and verified successfully.")
        return True, "Upstream SpotX retrieved successfully."
    except Exception as exc:
        if tmp_path.exists():
            tmp_path.unlink(missing_ok=True)
        err = f"Failed to download upstream SpotX: {exc}"
        log_error(err)
        return False, err


def get_cached_spotx_version() -> Optional[str]:
    """Parse the build version from the cached spotx.sh script."""
    script_path = get_spotx_script_path()
    if not is_spotx_cached():
        return None

    try:
        with open(script_path, "r", encoding="utf-8", errors="ignore") as f:
            for _ in range(30):
                line = f.readline()
                if not line:
                    break
                # e.g., buildVer="1.2.98.301.gfcaeba72"
                match = re.search(r'buildVer=["\']([^"\']+)["\']', line)
                if match:
                    # Strip trailing git commit hash if present
                    full_ver = match.group(1)
                    clean_match = re.match(r"^(\d+\.\d+\.\d+\.\d+)", full_ver)
                    return clean_match.group(1) if clean_match else full_ver
    except OSError:
        pass

    # Fallback to executing bash spotx.sh -v
    code, stdout, _ = run_command(["bash", str(script_path), "-v"], timeout=5)
    if code == 0 and stdout:
        match = re.search(r"version\s+([0-9.]+)", stdout)
        if match:
            return match.group(1)

    return None


def needs_elevation(app_path: Optional[str]) -> bool:
    """Check if write permissions to the target Spotify directory require sudo."""
    if not app_path:
        return False
    target = Path(app_path)
    if not target.exists():
        target = target.parent
    return not os.access(target, os.W_OK)


def execute_spotx_setup(
    installation: SpotifyInstallation,
    paid_premium: bool = False,
    hide_non_music: bool = False,
    enable_devmode: bool = False,
    clear_cache: bool = False,
) -> Tuple[bool, str, int]:
    """
    Safely execute upstream SpotX setup.
    Passes user-selected flags:
      -P <path>
      --noninteractive
      -p / --premium
      -h / --hide
      -d / --devmode
      -c / --clearcache
    """
    if not is_spotx_cached():
        ok, msg = fetch_upstream_spotx()
        if not ok:
            return False, f"Could not obtain SpotX script: {msg}", 1

    script_path = get_spotx_script_path()
    cmd = ["bash", str(script_path), "--noninteractive"]

    # Point to detected client directory if available
    if installation.app_path and installation.install_type != "Flatpak":
        cmd.extend(["-P", installation.app_path])

    if paid_premium:
        cmd.append("-p")
    if hide_non_music:
        cmd.append("-h")
    if enable_devmode:
        cmd.append("-d")
    if clear_cache:
        cmd.append("-c")

    log_info(f"Invoking upstream SpotX setup: {' '.join(cmd)}")
    code, stdout, stderr = run_command(cmd, timeout=300)

    # SpotX output parsing
    output = stdout + ("\n" + stderr if stderr else "")
    log_debug(f"Upstream SpotX output: {output}")

    if code == 0:
        log_info("Upstream SpotX setup completed successfully.")
        return True, output, 0
    else:
        log_error(f"Upstream SpotX setup failed with code {code}.")
        return False, output, code


def execute_spotx_restore(installation: SpotifyInstallation) -> Tuple[bool, str, int]:
    """
    Safely invoke upstream SpotX restoration mechanism via `--uninstall`.
    Restores original .bak files and removes modifications.
    """
    if not is_spotx_cached():
        ok, msg = fetch_upstream_spotx()
        if not ok:
            return False, f"Could not obtain SpotX script: {msg}", 1

    script_path = get_spotx_script_path()
    cmd = ["bash", str(script_path), "--uninstall", "--noninteractive"]

    if installation.app_path and installation.install_type != "Flatpak":
        cmd.extend(["-P", installation.app_path])

    log_info(f"Invoking upstream SpotX restoration: {' '.join(cmd)}")
    code, stdout, stderr = run_command(cmd, timeout=120)

    output = stdout + ("\n" + stderr if stderr else "")
    log_debug(f"Upstream SpotX restore output: {output}")

    if code == 0 or "Finished uninstall" in output or "Original client restored" in output:
        log_info("Spotify restoration completed successfully.")
        return True, output, 0
    else:
        log_error(f"Spotify restoration failed with code {code}.")
        return False, output, code
