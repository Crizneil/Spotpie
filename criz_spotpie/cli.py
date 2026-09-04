"""
Command-Line Interface Entry Point for CRIZ_SPOTPIE.

Parses command-line arguments, configures logging and themes,
and dispatches between interactive menu mode and CLI command flags.
"""

import argparse
import sys

from criz_spotpie import __title__, __version__
from criz_spotpie.colors import set_colors_enabled, set_theme
from criz_spotpie.config import get_config
from criz_spotpie.status import render_status_card
from criz_spotpie.updater import check_spotx_update, update_spotx_now
from criz_spotpie.utils import (
    log_info,
    print_error,
    print_info,
    print_success,
    print_warning,
    setup_logging,
)


def build_parser() -> argparse.ArgumentParser:
    """Build argument parser with clean help formatting."""
    parser = argparse.ArgumentParser(
        prog="criz-spotpie",
        description="CRIZ_SPOTPIE - Spotify Terminal Utility (Linux Frontend for SpotX)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  criz-spotpie             Launch interactive terminal menu (default)
  criz-spotpie --status    Check Spotify and SpotX installation status
  criz-spotpie --update    Check and update upstream SpotX script
  criz-spotpie --version   Print application version

Project: https://github.com/crizneil/criz-spotpie
Upstream: https://github.com/SpotX-Official/SpotX-Bash
        """,
    )

    parser.add_argument(
        "-v",
        "--version",
        action="store_true",
        help="Display CRIZ_SPOTPIE version and exit",
    )
    parser.add_argument(
        "-s",
        "--status",
        action="store_true",
        help="Display current Spotify and SpotX diagnostics card and exit",
    )
    parser.add_argument(
        "-u",
        "--update",
        action="store_true",
        help="Check and download the latest upstream SpotX script",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable verbose debugging output and tracebacks",
    )
    parser.add_argument(
        "--nocolor",
        action="store_true",
        help="Disable ANSI color codes in output",
    )

    return parser


def handle_cli_update() -> int:
    """Run non-interactive update check via CLI."""
    print("Checking upstream SpotX repository...")
    info = check_spotx_update()

    installed = info.get("installed_version", "Not Installed")
    latest = info.get("latest_version", "Unknown")
    update_avail = info.get("update_available", False)
    error = info.get("error")

    print(f"Installed version : {installed}")
    print(f"Latest version    : {latest}")

    if error:
        print(f"\n[ERROR] Update check failed: {error}")
        return 1

    if update_avail:
        print("\nUpdate available. Downloading latest upstream SpotX...")
        ok, msg = update_spotx_now()
        if ok:
            print(f"[SUCCESS] SpotX updated to version {latest}.")
            return 0
        else:
            print(f"[ERROR] Failed to update: {msg}")
            return 1
    else:
        print("\n[SUCCESS] SpotX is already up to date.")
        return 0


def main(argv=None) -> int:
    """Main CLI entrypoint."""
    parser = build_parser()
    args = parser.parse_args(argv)

    # Configure flags
    if args.nocolor:
        set_colors_enabled(False)

    config = get_config()
    theme = config.get("color_theme", "cyan_blue")
    set_theme(theme)

    is_debug = args.debug or config.get("debug_mode", False)
    setup_logging(debug=is_debug)
    log_info("Starting Criz_Spotpie")

    # --version
    if args.version:
        print(f"\n{__title__} v{__version__}\n")
        return 0

    # --status
    if args.status:
        print()
        print(render_status_card(width=46))
        print()
        return 0

    # --update
    if args.update:
        print()
        return handle_cli_update()

    # Default: Interactive Menu
    from criz_spotpie.menu import MenuController

    try:
        controller = MenuController()
        controller.start()
        return 0
    except KeyboardInterrupt:
        print("\nExited.")
        return 0
    except Exception as exc:
        if is_debug:
            raise
        print_error("Fatal application error.", details=str(exc))
        return 1


if __name__ == "__main__":
    sys.exit(main())
