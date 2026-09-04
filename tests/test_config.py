"""Unit tests for CRIZ_SPOTPIE config module."""

import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from criz_spotpie.config import DEFAULT_CONFIG, Config


class TestConfig(unittest.TestCase):
    """Test suite for Config manager."""

    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp(prefix="criz_spotpie_test_config_"))
        self.config = Config(config_dir=self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_default_config_creation(self):
        """Verify default config is created and written to disk."""
        config_file = self.test_dir / "config.json"
        self.assertTrue(config_file.is_file())
        with open(config_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertEqual(data["app_version"], "1.0.0")
        self.assertTrue(data["check_updates_startup"])
        self.assertEqual(data["color_theme"], "cyan_blue")

    def test_get_and_set(self):
        """Test retrieving and mutating configuration values."""
        self.config.set("color_theme", "neon_cyan")
        self.assertEqual(self.config.get("color_theme"), "neon_cyan")

        # Reload from disk to verify persistence
        new_config_instance = Config(config_dir=self.test_dir)
        self.assertEqual(new_config_instance.get("color_theme"), "neon_cyan")

    def test_reset(self):
        """Test resetting config back to defaults."""
        self.config.set("check_updates_startup", False)
        self.assertFalse(self.config.get("check_updates_startup"))

        self.config.reset()
        self.assertTrue(self.config.get("check_updates_startup"))

    def test_fallback_on_corrupt_file(self):
        """Test recovery if config.json is corrupted."""
        config_file = self.test_dir / "config.json"
        with open(config_file, "w", encoding="utf-8") as f:
            f.write("{invalid_json: true")

        recovered = Config(config_dir=self.test_dir)
        self.assertEqual(recovered.get("app_version"), "1.0.0")

    @patch("criz_spotpie.config.is_windows", return_value=True)
    @patch("criz_spotpie.config.Path.home", return_value=Path("C:/Users/TestUser"))
    def test_windows_config_dir(self, _mock_home, _mock_is_windows):
        """Verify Windows config defaults to AppData/Roaming."""
        config = Config(config_dir=None)
        self.assertTrue(str(config.config_dir).endswith("AppData/Roaming/criz-spotpie"))


def test_windows_launcher_script(self):
    """Verify Windows launcher wrapper uses a .cmd file and Python entry."""
    from criz_spotpie.installer import create_launcher_script

    target = Path(tempfile.mkdtemp(prefix="criz_spotpie_win_test_"))
    source_root = Path(__file__).resolve().parents[1]
    ok, path = create_launcher_script(target, source_root, python_exe="python", windows=True)
    assert ok is True
    assert Path(path).suffix.lower() == ".cmd"


if __name__ == "__main__":
    unittest.main()
