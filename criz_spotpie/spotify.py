"""
Spotify Detection and Process Management for CRIZ_SPOTPIE.

Detects native packages (APT/Debian), Flatpak, Snap, spotify-launcher,
and custom paths. Provides client version discovery and safe detached launching.
"""

import os
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple

from criz_spotpie.config import get_config
from criz_spotpie.utils import log_debug, log_info, run_command


@dataclass
class SpotifyInstallation:
    """Represents a discovered Spotify client installation."""

    installed: bool = False
    install_type: str = "Not Found"  # "Native (APT/DEB)", "Flatpak", "Snap", "Spotify Launcher", "Custom"
    binary_path: Optional[str] = None
    app_path: Optional[str] = None
    xpui_spa_path: Optional[str] = None
    version: Optional[str] = None
    is_patched: bool = False
    has_backup: bool = False
    details: str = ""

    @property
    def display_path(self) -> str:
        """User-friendly display path."""
        if self.app_path:
            home = str(Path.home())
            if self.app_path.startswith(home):
                return self.app_path.replace(home, "~", 1)
            return self.app_path
        if self.binary_path:
            return self.binary_path
        return "N/A"


def _check_spa_in_dir(base_dir: Path) -> Optional[Path]:
    """Check for xpui.spa inside candidate directory structures."""
    candidates = [
        base_dir / "Apps" / "xpui.spa",
        base_dir / "extra" / "share" / "spotify" / "Apps" / "xpui.spa",
        base_dir / "files" / "extra" / "share" / "spotify" / "Apps" / "xpui.spa",
        base_dir / "share" / "spotify" / "Apps" / "xpui.spa",
        base_dir / "files" / "share" / "spotify" / "Apps" / "xpui.spa",
    ]
    for c in candidates:
        if c.is_file():
            return c
    return None


def _check_patch_status(app_path: Optional[str], xpui_spa: Optional[str]) -> Tuple[bool, bool]:
    """Check if backups exist or if patch signatures are detected."""
    has_backup = False
    is_patched = False

    if app_path:
        base = Path(app_path)
        # Check standard SpotX backup files
        spotify_bak = base / "spotify.bak"
        xpui_bak = base / "Apps" / "xpui.bak"
        if spotify_bak.exists() or xpui_bak.exists():
            has_backup = True
            is_patched = True

    return is_patched, has_backup


def _extract_version_from_binary(binary_path: str) -> Optional[str]:
    """Query spotify binary for its version string."""
    code, stdout, _ = run_command([binary_path, "--version"], timeout=5)
    if code == 0 and stdout:
        # Expected: "Spotify version 1.2.42.290.g242057a2"
        match = re.search(r"(\d+\.\d+\.\d+\.\d+)", stdout)
        if match:
            return match.group(1)
    return None


def detect_spotify(custom_path: Optional[str] = None) -> SpotifyInstallation:
    """
    Search and detect Spotify installation across standard Linux locations.
    Checks:
      1. Custom path from config or parameter
      2. Native APT/system packages (/usr/share/spotify, /opt/spotify, etc.)
      3. Spotify-Launcher (~/.local/share/spotify-launcher/...)
      4. Flatpak (com.spotify.Client)
      5. Snap (snap list spotify)
    """
    config = get_config()
    target_custom = custom_path or config.get("custom_spotify_path", "")

    # 1. Custom path check
    if target_custom:
        custom_dir = Path(target_custom).expanduser().resolve()
        if custom_dir.is_dir():
            spa = _check_spa_in_dir(custom_dir)
            if spa:
                app_dir = spa.parent.parent
                binary = str(app_dir / "spotify") if (app_dir / "spotify").is_file() else None
                version = _extract_version_from_binary(binary) if binary else None
                is_patched, has_backup = _check_patch_status(str(app_dir), str(spa))
                log_info(f"Detected custom Spotify at {app_dir}")
                return SpotifyInstallation(
                    installed=True,
                    install_type="Custom Path",
                    binary_path=binary,
                    app_path=str(app_dir),
                    xpui_spa_path=str(spa),
                    version=version or "Detected",
                    is_patched=is_patched,
                    has_backup=has_backup,
                    details=f"Custom directory: {app_dir}",
                )

    # 2. Native System Locations
    native_dirs = [
        Path("/usr/share/spotify"),
        Path("/opt/spotify"),
        Path("/usr/lib64/spotify-client"),
    ]
    for p in native_dirs:
        if p.is_dir():
            spa = _check_spa_in_dir(p)
            if spa:
                app_dir = spa.parent.parent
                binary = shutil.which("spotify") or (str(app_dir / "spotify") if (app_dir / "spotify").is_file() else None)
                version = _extract_version_from_binary(binary) if binary else None
                is_patched, has_backup = _check_patch_status(str(app_dir), str(spa))
                log_info(f"Detected native Spotify at {app_dir}")
                return SpotifyInstallation(
                    installed=True,
                    install_type="Native (APT/DEB)",
                    binary_path=binary,
                    app_path=str(app_dir),
                    xpui_spa_path=str(spa),
                    version=version or "Detected",
                    is_patched=is_patched,
                    has_backup=has_backup,
                    details=f"Native client at {app_dir}",
                )

    # 3. Spotify Launcher (~/.local/share/spotify-launcher)
    launcher_base = Path.home() / ".local/share/spotify-launcher/install/usr/share/spotify"
    if launcher_base.is_dir():
        spa = _check_spa_in_dir(launcher_base)
        if spa:
            app_dir = spa.parent.parent
            binary = shutil.which("spotify-launcher") or str(app_dir / "spotify")
            version = _extract_version_from_binary(str(app_dir / "spotify"))
            is_patched, has_backup = _check_patch_status(str(app_dir), str(spa))
            log_info(f"Detected spotify-launcher at {app_dir}")
            return SpotifyInstallation(
                installed=True,
                install_type="Spotify Launcher",
                binary_path=binary,
                app_path=str(app_dir),
                xpui_spa_path=str(spa),
                version=version or "Detected",
                is_patched=is_patched,
                has_backup=has_backup,
                details=f"Spotify-launcher user directory",
            )

    # 4. Flatpak Detection
    flatpak_candidates = [
        Path("/var/lib/flatpak/app/com.spotify.Client"),
        Path.home() / ".local/share/flatpak/app/com.spotify.Client",
        Path.home() / ".var/app/com.spotify.Client",
    ]
    if shutil.which("flatpak") and any(p.exists() for p in flatpak_candidates):
        code, stdout, _ = run_command(["flatpak", "info", "com.spotify.Client"], timeout=2)
        if code == 0:
            # Extract Flatpak location
            code_loc, loc_out, _ = run_command(
                ["flatpak", "info", "--show-location", "com.spotify.Client"], timeout=2
            )
            flatpak_loc = Path(loc_out.strip()) if code_loc == 0 and loc_out.strip() else None
            spa = _check_spa_in_dir(flatpak_loc) if flatpak_loc else None
            app_dir = spa.parent.parent if spa else flatpak_loc

            # Extract version
            v_match = re.search(r"Version:\s*(\d+\.\d+\.\d+\.\d+)", stdout)
            version = v_match.group(1) if v_match else None
            is_patched, has_backup = _check_patch_status(str(app_dir) if app_dir else None, str(spa) if spa else None)
            log_info("Detected Flatpak Spotify")
            return SpotifyInstallation(
                installed=True,
                install_type="Flatpak",
                binary_path="flatpak run com.spotify.Client",
                app_path=str(app_dir) if app_dir else "/var/lib/flatpak/app/com.spotify.Client",
                xpui_spa_path=str(spa) if spa else None,
                version=version or "Flatpak Client",
                is_patched=is_patched,
                has_backup=has_backup,
                details="Flatpak sandbox installation",
            )

    # 5. Snap Detection
    snap_candidates = [
        Path("/snap/spotify"),
        Path("/var/lib/snapd/snap/spotify"),
        Path.home() / "snap" / "spotify",
        Path("/snap/bin/spotify"),
    ]
    if shutil.which("snap") and any(p.exists() for p in snap_candidates):
        code, stdout, _ = run_command(["snap", "list", "spotify"], timeout=2)
        if code == 0:
            lines = stdout.strip().splitlines()
            version = None
            if len(lines) > 1:
                parts = lines[1].split()
                if len(parts) >= 2:
                    version = parts[1]
            snap_path = "/snap/spotify/current"
            spa = _check_spa_in_dir(Path(snap_path)) if Path(snap_path).is_dir() else None
            log_info("Detected Snap Spotify")
            return SpotifyInstallation(
                installed=True,
                install_type="Snap",
                binary_path="/snap/bin/spotify",
                app_path=snap_path,
                xpui_spa_path=str(spa) if spa else None,
                version=version or "Snap Client",
                is_patched=False,
                has_backup=False,
                details="Snap package (read-only squashfs)",
            )

    # 6. Fallback: check if 'spotify' executable exists on PATH
    which_spotify = shutil.which("spotify")
    if which_spotify:
        binary_path = str(Path(which_spotify).resolve())
        version = _extract_version_from_binary(binary_path)
        log_info(f"Detected Spotify binary at {binary_path}")
        return SpotifyInstallation(
            installed=True,
            install_type="Binary on PATH",
            binary_path=binary_path,
            app_path=str(Path(binary_path).parent),
            version=version or "Detected",
            details="Discovered via system PATH",
        )

    log_info("No Spotify installation found")
    return SpotifyInstallation(installed=False)


def launch_spotify(installation: SpotifyInstallation) -> Tuple[bool, str]:
    """
    Launch Spotify cleanly in a detached background process.
    Returns (success: bool, message: str).
    """
    if not installation.installed:
        return False, "Spotify is not installed on this system."

    cmd = []
    if installation.install_type == "Flatpak":
        cmd = ["flatpak", "run", "com.spotify.Client"]
    elif installation.install_type == "Snap":
        cmd = ["snap", "run", "spotify"]
    elif installation.binary_path and Path(installation.binary_path).is_file():
        cmd = [installation.binary_path]
    elif shutil.which("spotify"):
        cmd = ["spotify"]
    elif shutil.which("gtk-launch"):
        cmd = ["gtk-launch", "spotify"]
    else:
        return False, "No valid launch command could be determined."

    try:
        log_info(f"Launching Spotify with command: {' '.join(cmd)}")
        subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            start_new_session=True,  # Detaches from current terminal session
        )
        return True, f"Spotify launched successfully via {installation.install_type}."
    except Exception as exc:
        err = f"Failed to launch Spotify: {exc}"
        log_error(err)
        return False, err
