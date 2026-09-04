"""Unit tests for CRIZ_SPOTPIE config module."""

import json
import shutil
import tempfile
import unittest
from pathlib import Path

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


if __name__ == "__main__":
    unittest.main()
