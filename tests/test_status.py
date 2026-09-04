"""Unit tests for CRIZ_SPOTPIE status reporting and card formatting."""

import unittest

from criz_spotpie.banner import render_card
from criz_spotpie.colors import set_colors_enabled, strip_ansi
from criz_spotpie.status import get_status_data, render_status_card


class TestStatus(unittest.TestCase):
    """Test suite for status reporting."""

    def setUp(self):
        set_colors_enabled(False)

    def tearDown(self):
        set_colors_enabled(True)

    def test_get_status_data_structure(self):
        """Verify status data contains all required keys."""
        items = get_status_data()
        keys = [k for k, _ in items]
        self.assertIn("Spotify", keys)
        self.assertIn("Spotify Path", keys)
        self.assertIn("SpotX", keys)
        self.assertIn("SpotX Version", keys)
        self.assertIn("Criz_Spotpie", keys)

    def test_render_status_card(self):
        """Verify status card is properly framed with borders."""
        card = render_status_card(width=46)
        clean_card = strip_ansi(card)
        lines = clean_card.splitlines()

        # Check top and bottom borders
        self.assertTrue(lines[0].startswith("╔") and lines[0].endswith("╗"))
        self.assertTrue(lines[-1].startswith("╚") and lines[-1].endswith("╝"))

        # Verify all lines have identical character width
        width = len(lines[0])
        for idx, line in enumerate(lines):
            self.assertEqual(len(line), width, f"Line {idx} length mismatch: '{line}'")


if __name__ == "__main__":
    unittest.main()
