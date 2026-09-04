"""Unit tests for CRIZ_SPOTPIE command-line interface."""

import io
import sys
import unittest
from unittest.mock import patch

from criz_spotpie.cli import build_parser, main


class TestCLI(unittest.TestCase):
    """Test suite for CLI argument handling."""

    def test_parser_options(self):
        """Verify CLI argument flags exist."""
        parser = build_parser()
        args = parser.parse_args(["--version"])
        self.assertTrue(args.version)

        args = parser.parse_args(["--status"])
        self.assertTrue(args.status)

        args = parser.parse_args(["--update"])
        self.assertTrue(args.update)

    def test_cli_version_output(self):
        """Verify --version returns code 0 and prints CRIZ_SPOTPIE v1.0.0."""
        captured = io.StringIO()
        with patch("sys.stdout", captured):
            exit_code = main(["--version"])

        self.assertEqual(exit_code, 0)
        output = captured.getvalue()
        self.assertIn("CRIZ_SPOTPIE", output)
        self.assertIn("1.0.0", output)

    def test_cli_status_output(self):
        """Verify --status returns code 0 and outputs card."""
        captured = io.StringIO()
        with patch("sys.stdout", captured):
            exit_code = main(["--status"])

        self.assertEqual(exit_code, 0)
        output = captured.getvalue()
        self.assertIn("CRIZ_SPOTPIE STATUS", output)


if __name__ == "__main__":
    unittest.main()
