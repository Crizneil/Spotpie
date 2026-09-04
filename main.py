#!/usr/bin/env python3
"""
CRIZ_SPOTPIE - Spotify Terminal Utility
Main Application Entry Point.
"""

import sys
from pathlib import Path

# Ensure package is resolvable when invoked directly as a script
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from criz_spotpie.cli import main

if __name__ == "__main__":
    sys.exit(main())
