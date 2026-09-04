"""
CRIZ_SPOTPIE - Spotify Terminal Utility
A cross-platform terminal frontend and wrapper around the upstream SpotX project.
"""

__title__ = "CRIZ_SPOTPIE"
__version__ = "1.0.0"
__author__ = "Crizneil"
__license__ = "MIT"
__description__ = "A cross-platform terminal utility and frontend for SpotX"


def main() -> int:
    """Module entry point for `python -m criz_spotpie`."""
    from criz_spotpie.cli import main as cli_main

    return cli_main()
