"""
Configuration Manager for CRIZ_SPOTPIE.

Stores user settings in the standard OS-specific config directory with safe atomic
writes and directory permission enforcement.
"""

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict

DEFAULT_CONFIG: Dict[str, Any] = {
    "app_version": "1.0.0",
    "check_updates_startup": True,
    "animations_enabled": True,
    "color_theme": "cyan_blue",
    "spotx_repo_url": "https://raw.githubusercontent.com/SpotX-Official/SpotX-Bash/main/spotx.sh",
    "spotx_github_repo": "https://github.com/SpotX-Official/SpotX-Bash",
    "custom_spotify_path": "",
    "paid_premium": False,
    "hide_non_music": False,
    "enable_devmode": False,
    "clear_cache": False,
    "debug_mode": False,
}


def is_windows() -> bool:
    """Return True when running on Windows."""
    return os.name == "nt" or sys.platform.startswith("win")


def default_config_dir() -> Path:
    """Return the OS-appropriate user configuration directory for CRIZ_SPOTPIE."""
    if is_windows():
        appdata = os.environ.get("APPDATA")
        if appdata:
            return Path(appdata) / "criz-spotpie"
        return Path.home() / "AppData" / "Roaming" / "criz-spotpie"

    config_home = os.environ.get("XDG_CONFIG_HOME")
    if config_home:
        return Path(config_home) / "criz-spotpie"
    return Path.home() / ".config" / "criz-spotpie"


class Config:
    """Manages CRIZ_SPOTPIE user configuration."""

    def __init__(self, config_dir: Path = None):
        if config_dir is None:
            self.config_dir = default_config_dir()
        else:
            self.config_dir = Path(config_dir)

        self.config_file = self.config_dir / "config.json"
        self.logs_dir = self.config_dir / "logs"
        self.upstream_dir = self.config_dir / "upstream"
        self._data: Dict[str, Any] = {}
        self.ensure_dirs()
        self.load()

    def ensure_dirs(self) -> None:
        """Ensure config, logs, and upstream directories exist with proper permissions."""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
            self.logs_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
            self.upstream_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
        except OSError:
            pass

    def load(self) -> Dict[str, Any]:
        """Load configuration from disk or populate with defaults."""
        if not self.config_file.exists():
            self._data = dict(DEFAULT_CONFIG)
            self.save()
            return self._data

        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                # Merge with default keys for forward compatibility
                self._data = dict(DEFAULT_CONFIG)
                self._data.update(loaded)
        except (json.JSONDecodeError, OSError):
            self._data = dict(DEFAULT_CONFIG)
            self.save()

        return self._data

    def save(self) -> bool:
        """Atomically save configuration to disk."""
        self.ensure_dirs()
        tmp_file = self.config_dir / "config.json.tmp"
        try:
            with open(tmp_file, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2)
            os.chmod(tmp_file, 0o600)
            tmp_file.replace(self.config_file)
            return True
        except OSError:
            return False

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve a configuration value."""
        return self._data.get(key, default if default is not None else DEFAULT_CONFIG.get(key))

    def set(self, key: str, value: Any) -> bool:
        """Set a configuration value and persist immediately."""
        self._data[key] = value
        return self.save()

    def reset(self) -> bool:
        """Reset configuration back to default values."""
        self._data = dict(DEFAULT_CONFIG)
        return self.save()

    def all(self) -> Dict[str, Any]:
        """Return a copy of all configuration settings."""
        return dict(self._data)


# Global singleton instance for easy import across modules
_CONFIG_INSTANCE: Config = None


def get_config(config_dir: Path = None) -> Config:
    """Get or initialize the global Config singleton."""
    global _CONFIG_INSTANCE
    if _CONFIG_INSTANCE is None or config_dir is not None:
        _CONFIG_INSTANCE = Config(config_dir=config_dir)
    return _CONFIG_INSTANCE
