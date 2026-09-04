"""
Interactive Menu and Navigation Controller for CRIZ_SPOTPIE.

Renders double-lined terminal boxes, captures user choices, dispatches
operations, and safely handles Ctrl+C and navigation without tracebacks.
"""

import sys
import time
from typing import Optional

from criz_spotpie import __author__, __version__
from criz_spotpie.banner import (
    DEFAULT_WIDTH,
    center_line,
    get_menu_header,
    get_section_header,
    get_startup_banner,
    render_box,
)
from criz_spotpie.colors import (
    c_bold,
    c_bold_primary,
    c_bold_white,
    c_border,
    c_dim,
    c_error,
    c_highlight,
    c_primary,
    c_secondary,
    c_success,
    c_warning,
    set_theme,
)
from criz_spotpie.config import get_config
from criz_spotpie.spotify import detect_spotify, launch_spotify
from criz_spotpie.spotx import (
    check_dependencies,
    execute_spotx_restore,
    execute_spotx_setup,
    fetch_upstream_spotx,
    get_cached_spotx_version,
    get_missing_dependencies,
    is_spotx_cached,
    needs_elevation,
)
from criz_spotpie.status import render_status_card
from criz_spotpie.updater import check_spotx_update, update_spotx_now
from criz_spotpie.utils import (
    Spinner,
    clear_screen,
    log_info,
    print_error,
    print_info,
    print_success,
    print_warning,
    prompt_enter,
    prompt_yes_no,
)


class MenuController:
    """Controls the interactive Criz_Spotpie terminal interface."""

    def __init__(self):
        self.config = get_config()
        self.running = True

    def run_startup(self) -> None:
        """Display the initial startup banner and environment checks."""
        clear_screen()
        print(get_startup_banner())
        print()

        with Spinner("Initializing..."):
            time.sleep(0.2)

        with Spinner("Checking Spotify..."):
            spot = detect_spotify()

        with Spinner("Checking SpotX..."):
            cached = is_spotx_cached()

        if self.config.get("check_updates_startup", True):
            with Spinner("Checking for SpotX updates..."):
                try:
                    update_info = check_spotx_update()
                    if update_info.get("update_available"):
                        print(f" {c_warning('!')} Upstream SpotX update available: {c_highlight(update_info.get('latest_version'))}")
                except Exception:
                    pass

        time.sleep(0.2)

    def render_main_menu(self) -> None:
        """Render the primary interactive menu."""
        clear_screen()
        header = get_menu_header(DEFAULT_WIDTH)
        inner_width = DEFAULT_WIDTH - 2

        menu_items = [
            ("1", "SpotX Setup / Apply"),
            ("2", "Restore Spotify"),
            ("3", "Update SpotX"),
            ("4", "Check Status"),
            ("5", "Launch Spotify"),
            ("6", "Settings"),
            ("7", "About"),
        ]

        body = [""]
        for num, label in menu_items:
            row = f"  {c_bold_primary('[' + num + ']')} {c_highlight(label)}"
            body.append(row)

        body.append("")
        body.append(f"  {c_dim('[0]')} {c_dim('Exit')}")
        body.append("")

        box_content = []
        for line in body:
            box_content.append(line)

        # Draw bottom box
        rendered_body = []
        for line in box_content:
            from criz_spotpie.colors import visible_len
            v_len = visible_len(line)
            padding = max(0, inner_width - v_len)
            rendered_body.append(f"{c_border('║')}{line}{' ' * padding}{c_border('║')}")

        bottom_border = c_border(f"╚{'═' * inner_width}╝")

        print(header)
        for r in rendered_body:
            print(r)
        print(bottom_border)
        print()

    def handle_setup(self) -> None:
        """Handle Option 1: SpotX Setup / Apply."""
        clear_screen()
        print(get_section_header("SPOTX SETUP / APPLY"))
        print()

        # Step 1: Detect Spotify
        with Spinner("Detecting Spotify client..."):
            spotify = detect_spotify()

        if not spotify.installed:
            print_error(
                "Spotify was not detected.",
                details="Please install Spotify first via APT, Flatpak, or official repository.",
            )
            prompt_enter()
            return

        print_success(f"Spotify detected: {c_highlight(spotify.install_type)}")
        print(f"  Path: {c_dim(spotify.display_path)}")
        if spotify.version:
            print(f"  Version: {c_dim(spotify.version)}")
        print()

        # Step 2: Check required dependencies
        missing = get_missing_dependencies()
        if missing:
            print_error(
                f"Missing required system utilities: {', '.join(missing)}",
                details=f"Please install them via: sudo apt install {' '.join(missing)}",
            )
            prompt_enter()
            return

        # Step 3: Check upstream SpotX
        if not is_spotx_cached():
            print_info("SpotX upstream script not cached. Downloading official release...")
            with Spinner("Retrieving SpotX-Bash from upstream repository..."):
                ok, msg = fetch_upstream_spotx()
            if not ok:
                print_error(f"Failed to obtain upstream SpotX: {msg}")
                prompt_enter()
                return
            print_success("Upstream SpotX retrieved successfully.")
        else:
            ver = get_cached_spotx_version()
            print_info(f"Using upstream SpotX-Bash {c_highlight(ver or 'cached')}")

        print()

        # Step 4: Show planned actions and options
        paid_premium = self.config.get("paid_premium", False)
        hide_non_music = self.config.get("hide_non_music", False)
        enable_devmode = self.config.get("enable_devmode", False)
        clear_cache = self.config.get("clear_cache", False)

        print(c_bold("Planned Actions:"))
        print(f" • Target: {c_highlight(spotify.display_path)}")
        print(f" • Premium Account Flag (-p): {c_highlight('Enabled' if paid_premium else 'Disabled (Free tier patches)')}")
        print(f" • Hide Podcasts/Audiobooks (-h): {c_highlight('Yes' if hide_non_music else 'No')}")
        if enable_devmode:
            print(f" • Developer Mode (-d): {c_highlight('Enabled')}")
        if clear_cache:
            print(f" • Clear Client Cache (-c): {c_highlight('Enabled')}")

        # Check permissions
        if needs_elevation(spotify.app_path):
            print()
            print_warning(
                "Spotify is located in a protected system directory.\n"
                "   The upstream SpotX script will prompt for normal sudo credentials to apply patches."
            )

        print()

        # Step 5: Ask confirmation
        confirmed = prompt_yes_no("Apply SpotX modifications now?", default=False)
        if not confirmed:
            print(f"\n {c_dim('Operation cancelled.')}")
            prompt_enter()
            return

        # Step 6: Execute upstream SpotX
        print(f"\n {c_primary('»')} Executing upstream SpotX process...\n")
        ok, output, code = execute_spotx_setup(
            installation=spotify,
            paid_premium=paid_premium,
            hide_non_music=hide_non_music,
            enable_devmode=enable_devmode,
            clear_cache=clear_cache,
        )

        if ok:
            print()
            print_success("SpotX modifications applied successfully!")
        else:
            print_error(
                "SpotX operation failed.",
                details=f"A detailed log has been saved to:\n {self.config.logs_dir}/criz_spotpie.log",
                exit_code=code,
            )

        prompt_enter()

    def handle_restore(self) -> None:
        """Handle Option 2: Restore Spotify."""
        clear_screen()
        print(get_section_header("RESTORE SPOTIFY"))
        print()

        with Spinner("Checking Spotify installation..."):
            spotify = detect_spotify()

        if not spotify.installed:
            print_error("Spotify was not detected.", details="Cannot restore an uninstalled client.")
            prompt_enter()
            return

        if not spotify.has_backup and not spotify.is_patched:
            print_warning("No existing SpotX backup files (spotify.bak / xpui.bak) were detected.")
            print(f"  {c_dim('The client appears to be already unpatched or unmodified.')}\n")

        print(c_bold("Restoration Details:"))
        print(f" • Target: {c_highlight(spotify.display_path)}")
        print(f" • Action: Upstream SpotX will restore original client backups (--uninstall)")

        if needs_elevation(spotify.app_path):
            print()
            print_warning(
                "Spotify is in a protected system directory.\n"
                "   Elevated privileges (sudo) may be requested by the upstream script to restore backups."
            )

        print()
        confirmed = prompt_yes_no("Restore original Spotify now?", default=False)
        if not confirmed:
            print(f"\n {c_dim('Operation cancelled.')}")
            prompt_enter()
            return

        print(f"\n {c_primary('»')} Invoking upstream SpotX restoration...\n")
        ok, output, code = execute_spotx_restore(spotify)

        if ok:
            print()
            print_success("Spotify restored to original state successfully!")
        else:
            print_error(
                "Spotify restoration encountered an error.",
                details=f"Check logs at: {self.config.logs_dir}/criz_spotpie.log",
                exit_code=code,
            )

        prompt_enter()

    def handle_update(self) -> None:
        """Handle Option 3: Update SpotX."""
        clear_screen()
        print(get_section_header("UPDATE SPOTX"))
        print()

        print("Checking SpotX...\n")
        with Spinner("Contacting upstream repository..."):
            info = check_spotx_update()

        installed = info.get("installed_version", "Not Installed")
        latest = info.get("latest_version", "Unknown")
        update_avail = info.get("update_available", False)
        error = info.get("error")

        print(f" Installed version : {c_highlight(installed)}")
        print(f" Latest version    : {c_highlight(latest)}")
        print()

        if error:
            print_error(f"Could not check upstream version: {error}")
            prompt_enter()
            return

        if update_avail:
            print_warning("Update available.\n")
            confirmed = prompt_yes_no("Update SpotX now?", default=True)
            if confirmed:
                with Spinner("Downloading updated upstream SpotX..."):
                    ok, msg = update_spotx_now()
                if ok:
                    print()
                    print_success(f"SpotX updated to version {c_highlight(latest)}!")
                else:
                    print_error(f"Failed to update SpotX: {msg}")
            else:
                print(f"\n {c_dim('Update skipped.')}")
        else:
            print_success("SpotX is already up to date.")

        prompt_enter()

    def handle_status(self) -> None:
        """Handle Option 4: Check Status."""
        clear_screen()
        print(render_status_card(width=46))
        prompt_enter()

    def handle_launch(self) -> None:
        """Handle Option 5: Launch Spotify."""
        clear_screen()
        print(get_section_header("LAUNCH SPOTIFY"))
        print()

        with Spinner("Locating Spotify application..."):
            spotify = detect_spotify()

        if not spotify.installed:
            print_error("Spotify is not installed.", details="Please install Spotify first.")
            prompt_enter()
            return

        with Spinner("Launching Spotify..."):
            ok, msg = launch_spotify(spotify)

        if ok:
            print_success(msg)
        else:
            print_error(msg)

        prompt_enter()

    def handle_settings(self) -> None:
        """Handle Option 6: Settings Submenu."""
        while True:
            clear_screen()
            header = get_section_header("SETTINGS", width=DEFAULT_WIDTH)
            inner_width = DEFAULT_WIDTH - 2

            auto_update = self.config.get("check_updates_startup", True)
            anim = self.config.get("animations_enabled", True)
            theme = self.config.get("color_theme", "cyan_blue")
            premium = self.config.get("paid_premium", False)
            hide_pod = self.config.get("hide_non_music", False)

            settings_lines = [
                "",
                f"  {c_bold_primary('[1]')} Check for updates automatically: {c_highlight('ON' if auto_update else 'OFF')}",
                f"  {c_bold_primary('[2]')} Animation on/off:                {c_highlight('ON' if anim else 'OFF')}",
                f"  {c_bold_primary('[3]')} Color theme:                    {c_highlight(theme.replace('_', ' ').title())}",
                f"  {c_bold_primary('[4]')} SpotX Paid Premium Flag:        {c_highlight('ON' if premium else 'OFF')}",
                f"  {c_bold_primary('[5]')} SpotX Hide Podcasts/Audiobooks: {c_highlight('ON' if hide_pod else 'OFF')}",
                f"  {c_bold_primary('[6]')} Reset configuration to defaults",
                "",
                f"  {c_dim('[0]')} {c_dim('Back to Main Menu')}",
                "",
            ]

            rendered_body = []
            for line in settings_lines:
                from criz_spotpie.colors import visible_len
                v_len = visible_len(line)
                padding = max(0, inner_width - v_len)
                rendered_body.append(f"{c_border('║')}{line}{' ' * padding}{c_border('║')}")

            bottom_border = c_border(f"╚{'═' * inner_width}╝")

            print(header)
            for r in rendered_body:
                print(r)
            print(bottom_border)
            print()

            try:
                choice = input(f" {c_primary('Select a setting to toggle [0-6]')}: ").strip()
            except (KeyboardInterrupt, EOFError):
                break

            if choice == "1":
                self.config.set("check_updates_startup", not auto_update)
            elif choice == "2":
                self.config.set("animations_enabled", not anim)
            elif choice == "3":
                # Cycle theme
                themes = ["cyan_blue", "neon_cyan", "monochrome"]
                current_idx = themes.index(theme) if theme in themes else 0
                next_theme = themes[(current_idx + 1) % len(themes)]
                self.config.set("color_theme", next_theme)
                set_theme(next_theme)
            elif choice == "4":
                self.config.set("paid_premium", not premium)
            elif choice == "5":
                self.config.set("hide_non_music", not hide_pod)
            elif choice == "6":
                if prompt_yes_no("Reset all configuration settings to default?", default=False):
                    self.config.reset()
                    set_theme("cyan_blue")
                    print_success("Configuration reset to defaults.")
                    time.sleep(0.5)
            elif choice == "0":
                break

    def handle_about(self) -> None:
        """Handle Option 7: About."""
        clear_screen()
        inner_width = DEFAULT_WIDTH - 2
        top_border = c_border(f"╔{'═' * inner_width}╗")
        title_line = f"{c_border('║')}{center_line(c_bold_primary('ABOUT CRIZ_SPOTPIE'), inner_width)}{c_border('║')}"
        divider = c_border(f"╠{'═' * inner_width}╣")
        bottom_border = c_border(f"╚{'═' * inner_width}╝")

        about_text = [
            "",
            f"  {c_bold_white('CRIZ_SPOTPIE')} {c_dim('v' + __version__)}",
            f"  Created by {c_primary(__author__)}.",
            "",
            f"  {c_dim('Criz_Spotpie is an independent frontend and wrapper.')}",
            f"  {c_dim('SpotX is an external upstream project.')}",
            "",
            f"  {c_dim('This project does not claim ownership of SpotX.')}",
            f"  {c_dim('See the upstream SpotX project for license and docs.')}",
            "",
            f"  Upstream Repo : {c_secondary('https://github.com/SpotX-Official/SpotX-Bash')}",
            f"  Project Repo  : {c_secondary('https://github.com/crizneil/criz-spotpie')}",
            f"  License       : {c_highlight('MIT License')}",
            "",
        ]

        rendered_body = []
        for line in about_text:
            from criz_spotpie.colors import visible_len
            v_len = visible_len(line)
            padding = max(0, inner_width - v_len)
            rendered_body.append(f"{c_border('║')}{line}{' ' * padding}{c_border('║')}")

        print(top_border)
        print(title_line)
        print(divider)
        for r in rendered_body:
            print(r)
        print(bottom_border)

        prompt_enter()

    def start(self) -> None:
        """Main interactive menu event loop."""
        self.run_startup()

        while self.running:
            try:
                self.render_main_menu()
                choice = input(f" {c_bold_primary('Select an option')}: ").strip()

                if choice == "1":
                    self.handle_setup()
                elif choice == "2":
                    self.handle_restore()
                elif choice == "3":
                    self.handle_update()
                elif choice == "4":
                    self.handle_status()
                elif choice == "5":
                    self.handle_launch()
                elif choice == "6":
                    self.handle_settings()
                elif choice == "7":
                    self.handle_about()
                elif choice == "0":
                    clear_screen()
                    print(f"\n {c_primary('Thank you for using CRIZ_SPOTPIE.')}\n")
                    self.running = False
                else:
                    # Invalid option
                    print(f"\n {c_warning('Invalid selection. Please choose an option from the menu.')}")
                    time.sleep(0.8)

            except KeyboardInterrupt:
                print(f"\n\n {c_dim('Operation cancelled.')}")
                print(f" {c_dim('Returning to main menu...')}\n")
                time.sleep(0.6)
            except EOFError:
                self.running = False
                break
            except Exception as exc:
                if self.config.get("debug_mode", False):
                    raise
                print_error("An unexpected error occurred in the menu loop.", details=str(exc))
                prompt_enter()
