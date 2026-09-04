"""
Installation and Uninstallation Helper for CRIZ_SPOTPIE.

Manages setup of the `criz-spotpie` executable in the OS-appropriate user or
system bin directory, PATH validation, and clean uninstallation.
"""

import os
import shutil
import stat
import sys
from pathlib import Path
from typing import Optional, Tuple


def is_windows() -> bool:
    """Return True when running on Windows."""
    return os.name == "nt" or sys.platform.startswith("win")


def get_install_target_dir(system_wide: bool = False, windows: bool = False) -> Path:
    """Return the destination directory for the criz-spotpie launcher."""
    if windows or is_windows():
        if system_wide:
            return Path("C:/Program Files/CRIZ_SPOTPIE")
        return Path.home() / "AppData" / "Local" / "Programs" / "CRIZ_SPOTPIE"
    if system_wide:
        return Path("/usr/local/bin")
    return Path.home() / ".local" / "bin"


def is_dir_in_path(directory: Path) -> bool:
    """Check whether a directory is currently included in the PATH environment variable."""
    path_env = os.environ.get("PATH", "")
    resolved_dir = directory.resolve()
    for entry in path_env.split(os.pathsep):
        try:
            if Path(entry).resolve() == resolved_dir:
                return True
        except OSError:
            continue
    return False


def create_launcher_script(
    target_dir: Path,
    source_root: Path,
    python_exe: Optional[str] = None,
    windows: bool = False,
) -> Tuple[bool, str]:
    """
    Create a standalone launcher script in target_dir that invokes main.py with
    the proper Python interpreter on either Unix-like systems or Windows.
    """
    python_bin = python_exe or sys.executable
    launcher_name = "criz-spotpie.cmd" if windows or is_windows() else "criz-spotpie"
    launcher_path = target_dir / launcher_name
    main_py_path = (source_root / "main.py").resolve()

    if not main_py_path.is_file():
        return False, f"Could not find main.py at {main_py_path}"

    target_dir.mkdir(parents=True, exist_ok=True)

    if windows or is_windows():
        script_content = (
            "@echo off\r\n"
            "setlocal\r\n"
            f"set \"PYTHON_BIN={python_bin}\"\r\n"
            f"set \"PROJECT_ROOT={source_root.resolve()}\"\r\n"
            "set \"PYTHONPATH=%PROJECT_ROOT%;%PYTHONPATH%\"\r\n"
            "\"%PYTHON_BIN%\" \"%PROJECT_ROOT%\\main.py\" %*\r\n"
        )
    else:
        script_content = f"""#!/usr/bin/env bash
# CRIZ_SPOTPIE Launcher
# Auto-generated wrapper for criz-spotpie
PYTHON_BIN="{python_bin}"
PROJECT_ROOT="{source_root.resolve()}"

export PYTHONPATH="${{PROJECT_ROOT}}:${{PYTHONPATH}}"
exec "${{PYTHON_BIN}}" "${{PROJECT_ROOT}}/main.py" "$@"
"""

    try:
        with open(launcher_path, "w", encoding="utf-8", newline="") as f:
            f.write(script_content)

        if not (windows or is_windows()):
            st = launcher_path.stat()
            launcher_path.chmod(st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        return True, str(launcher_path)
    except Exception as exc:
        return False, f"Failed to create launcher script: {exc}"


def remove_launcher_script(target_dir: Path) -> Tuple[bool, str]:
    """Remove the criz-spotpie launcher from target_dir."""
    launcher_path = target_dir / "criz-spotpie"
    if not launcher_path.exists():
        return True, "Launcher not found (already removed)."

    try:
        launcher_path.unlink()
        return True, f"Removed launcher from {launcher_path}"
    except Exception as exc:
        return False, f"Failed to remove launcher: {exc}"
