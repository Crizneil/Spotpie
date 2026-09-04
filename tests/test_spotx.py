"""Unit tests for SpotX upstream wrapper and dependency checks."""

import unittest
from unittest.mock import patch

from criz_spotpie.spotx import (
    check_dependencies,
    get_missing_dependencies,
    needs_elevation,
)


class TestSpotX(unittest.TestCase):
    """Test suite for SpotX integration."""

    def test_dependency_keys(self):
        """Verify all required system tools are checked."""
        deps = check_dependencies()
        self.assertIn("bash", deps)
        self.assertIn("curl", deps)
        self.assertIn("perl", deps)
        self.assertIn("unzip", deps)
        self.assertIn("zip", deps)

    @patch("shutil.which")
    def test_missing_dependencies_detection(self, mock_which):
        """Test detection when a tool is missing."""
        mock_which.side_effect = lambda tool: None if tool == "perl" else f"/usr/bin/{tool}"
        missing = get_missing_dependencies()
        self.assertIn("perl", missing)
        self.assertNotIn("bash", missing)

    def test_needs_elevation(self):
        """Test elevation detection."""
        self.assertFalse(needs_elevation(None))
        # /root typically not writable by unprivileged user
        self.assertTrue(needs_elevation("/root/spotify"))


if __name__ == "__main__":
    unittest.main()
