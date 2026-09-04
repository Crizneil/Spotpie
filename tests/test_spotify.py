"""Unit tests for Spotify detection and process handling."""

import os
import shutil
import tempfile
import unittest
from pathlib import Path

from criz_spotpie.spotify import (
    SpotifyInstallation,
    _check_patch_status,
    _check_spa_in_dir,
    detect_spotify,
    launch_spotify,
)


class TestSpotifyDetection(unittest.TestCase):
    """Test suite for Spotify detection."""

    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp(prefix="criz_spotpie_test_spotify_"))

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_mock_spotify_installation(self):
        """Simulate a Spotify directory structure with xpui.spa."""
        app_dir = self.test_dir / "spotify"
        apps_dir = app_dir / "Apps"
        apps_dir.mkdir(parents=True)

        spa_file = apps_dir / "xpui.spa"
        spa_file.write_text("mock xpui content")

        found_spa = _check_spa_in_dir(app_dir)
        self.assertIsNotNone(found_spa)
        self.assertEqual(found_spa, spa_file)

        # Detect via custom path
        detected = detect_spotify(custom_path=str(app_dir))
        self.assertTrue(detected.installed)
        self.assertEqual(detected.install_type, "Custom Path")
        self.assertEqual(detected.app_path, str(app_dir))

    def test_patch_status_detection(self):
        """Test detection of backup files."""
        app_dir = self.test_dir / "spotify"
        apps_dir = app_dir / "Apps"
        apps_dir.mkdir(parents=True)
        spa_file = apps_dir / "xpui.spa"
        spa_file.write_text("mock")

        # Initially no backup
        is_patched, has_backup = _check_patch_status(str(app_dir), str(spa_file))
        self.assertFalse(has_backup)

        # Create backup file
        (app_dir / "spotify.bak").write_text("backup binary")
        is_patched, has_backup = _check_patch_status(str(app_dir), str(spa_file))
        self.assertTrue(has_backup)
        self.assertTrue(is_patched)

    def test_launch_not_installed(self):
        """Test launching when Spotify is not installed."""
        empty_install = SpotifyInstallation(installed=False)
        ok, msg = launch_spotify(empty_install)
        self.assertFalse(ok)
        self.assertIn("not installed", msg)


if __name__ == "__main__":
    unittest.main()
