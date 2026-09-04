#!/usr/bin/env python3
"""One-click installer for CRIZ_SPOTPIE.

Usage:
  python scripts/install.py
  py scripts\install.py
"""

from __future__ import annotations

import os
import site
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def is_windows() -> bool:
    return os.name == "nt" or sys.platform.startswith("win")


def get_user_scripts_dir() -> Path:
    if is_windows():
        return Path(site.USER_BASE) / "Scripts"
    return Path(site.USER_BASE) / "bin"


def ensure_user_scripts_in_path() -> None:
    scripts_dir = get_user_scripts_dir()
    path_entries = os.environ.get("PATH", "").split(os.pathsep)
    if str(scripts_dir) not in path_entries:
        print("\n[INFO] Your user Scripts directory is not in PATH yet:")
        print(f"  {scripts_dir}")
        if is_windows():
            print("Run this in a new PowerShell window after installation:")
            print(f"  $env:Path += ';{scripts_dir}'")
        else:
            print("Add this line to your ~/.bashrc or ~/.zshrc:")
            print(f"  export PATH=\"{scripts_dir}:$PATH\"")


def run_install() -> None:
    print(f"Installing CRIZ_SPOTPIE from: {PROJECT_ROOT}")
    cmd = [sys.executable, "-m", "pip", "install", "--user", str(PROJECT_ROOT)]
    print("Running:", " ".join(cmd))
    subprocess.run(cmd, check=True)


def main() -> int:
    try:
        run_install()
    except subprocess.CalledProcessError as exc:
        print(f"\n[ERROR] Installation failed with exit code {exc.returncode}")
        return exc.returncode

    print("\n[OK] CRIZ_SPOTPIE installed successfully.")
    print("You can run it with:")
    print("  criz-spotpie")
    print("\nIf that command is not recognized yet, open a new terminal window and try again.")
    ensure_user_scripts_in_path()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
