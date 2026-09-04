# CRIZ_SPOTPIE

```text
╔══════════════════════════════════════════════════╗
║                                                  ║
║                  CRIZ_SPOTPIE                    ║
║            Spotify Terminal Utility              ║
║             v1.0.0 • Linux Edition               ║
║                                                  ║
╚══════════════════════════════════════════════════╝
```

**CRIZ_SPOTPIE** is a modern, standalone Linux terminal utility and interactive management frontend for Spotify on Linux. Inspired by the dark terminal IT-utility aesthetic of CRIZ NETTOOL, it provides a safe, elegant wrapper around the official upstream **SpotX-Bash** project.

---

## Important Notice & Attribution

> [!NOTE]
> **CRIZ_SPOTPIE is an independent frontend and wrapper created by Crizneil.**
> It is **not** an official SpotX project, nor does it claim ownership or authorship of SpotX.
>
> **SpotX** is an open-source community project developed by the **SpotX-Official** team.
> CRIZ_SPOTPIE does **not** duplicate or bundle SpotX source code into this repository. Instead, it securely interfaces with the official upstream repository (`https://github.com/SpotX-Official/SpotX-Bash`) according to its documented interface and license.
>
> All modifications performed on the Spotify desktop client are managed through the official upstream SpotX scripts.

---

## Features

- **Dark Terminal Aesthetic**: Cyan/blue color scheme, Unicode double-line boxes, clean status badges, and subtle loading spinners.
- **Interactive Terminal Menu**: Simple numeric navigation with keyboard-friendly prompts and clean Ctrl+C cancellation handling.
- **Spotify Client Detection**: Automatically discovers Spotify installations across:
  - Standard Debian/Ubuntu native packages (`/usr/share/spotify`, `/opt/spotify`)
  - Flatpak sandbox (`com.spotify.Client`)
  - Snap package detection and advisory
  - `spotify-launcher` user distributions
  - Custom specified client directories
- **Safety & Non-Destructive Operation**:
  - Requires explicit confirmation before any system modifications.
  - Warns in advance if administrator privileges (`sudo`) will be requested by the upstream script for protected directories.
  - Never uses `sudo` silently or arbitrarily.
  - Preserves backup files (`spotify.bak`, `xpui.bak`) created by upstream SpotX.
- **Client Restoration**: Safely restores the unmodified Spotify client from backup files using upstream `--uninstall`.
- **Automatic & Manual Upstream Updates**: Checks upstream GitHub releases for new SpotX builds and updates cached scripts with a single command or menu selection.
- **Diagnostic Status Card**: Real-time read-only status display showing client location, installation type, patch status, and versions.
- **Client Launcher**: Launches Spotify cleanly as a detached background desktop process.
- **Custom Settings**: Adjust update checking, animations, color themes (`cyan_blue`, `neon_cyan`, `monochrome`), and patch preferences.
- **Zero Python Dependencies**: Powered entirely by the Python 3.10+ standard library. No `pip install` required.

---

## Terminal Interface Preview

### Main Menu

```text
╔══════════════════════════════════════════════════╗
║                   CRIZ_SPOTPIE                   ║
╠══════════════════════════════════════════════════╣
║                                                  ║
║  [1] SpotX Setup / Apply                         ║
║  [2] Restore Spotify                             ║
║  [3] Update SpotX                                ║
║  [4] Check Status                                ║
║  [5] Launch Spotify                              ║
║  [6] Settings                                    ║
║  [7] About                                       ║
║                                                  ║
║  [0] Exit                                        ║
║                                                  ║
╚══════════════════════════════════════════════════╝

 Select an option:
```

### Status Card

```text
╔════════════════════════════════════════════╗
║            CRIZ_SPOTPIE STATUS             ║
╠════════════════════════════════════════════╣
║ Spotify        : Installed                 ║
║ Spotify Path   : /usr/share/spotify        ║
║ SpotX          : Detected                  ║
║ SpotX Version  : 1.2.98.301                ║
║ Patch Status   : Patched (Backups present) ║
║ Criz_Spotpie   : 1.0.0                     ║
╚════════════════════════════════════════════╝
```

---

## Requirements

### Operating System
- **Linux** (Zorin OS, Ubuntu, Debian, Linux Mint, Pop!_OS, Arch, Fedora)
- Python **3.10** or higher
- Standard POSIX tools: `bash`, `curl`, `perl`, `unzip`, `zip`

### Spotify Client
- Official Spotify desktop client (APT package, Debian `.deb`, or Flatpak).
- *Note:* Snap installations use a read-only squashfs image. For best compatibility, install Spotify via the official APT repository or Flatpak.

---

## Installation

### Easiest Install on Any PC

If Python is already installed, the simplest path is:

```bash
pip install git+https://github.com/Crizneil/Spotpie.git
criz-spotpie
```

Or from a local clone:

```bash
git clone https://github.com/crizneil/criz-spotpie.git
cd criz-spotpie
python3 -m pip install .
criz-spotpie
```

Windows users can use:

```powershell
py -m pip install git+https://github.com/Crizneil/Spotpie.git
criz-spotpie
```

### Alternative quick launch

If you already have the repo/folder on the machine, this also works:

```bash
python -m criz_spotpie
```

This removes the need to remember a custom PATH or a shell wrapper.

### System-Wide Installation

To install for all system users in `/usr/local/bin`:

```bash
sudo ./scripts/install.sh --system
```

---

## Usage

### Interactive Mode

Run without arguments to enter the full interactive terminal interface:

```bash
criz-spotpie
```

### Command-Line Arguments

CRIZ_SPOTPIE can also run non-interactively via CLI flags:

| Command | Description |
| :--- | :--- |
| `criz-spotpie` | Launch the interactive menu (default) |
| `criz-spotpie --status` | Display the current status and diagnostics card and exit |
| `criz-spotpie --update` | Check for upstream SpotX updates and download if available |
| `criz-spotpie --version` | Display the application version and exit |
| `criz-spotpie --help` | Display command-line options and examples |
| `criz-spotpie --debug` | Enable verbose debug logging and traceback output |
| `criz-spotpie --nocolor` | Disable ANSI color codes |

---

## Configuration

Configuration is stored in standard XDG user directory:

```text
~/.config/criz-spotpie/config.json
```

Operation logs are stored in:

```text
~/.config/criz-spotpie/logs/criz_spotpie.log
```

Cached upstream scripts are stored in:

```text
~/.config/criz-spotpie/upstream/spotx.sh
```

### Configurable Keys

```json
{
  "app_version": "1.0.0",
  "check_updates_startup": true,
  "animations_enabled": true,
  "color_theme": "cyan_blue",
  "spotx_repo_url": "https://raw.githubusercontent.com/SpotX-Official/SpotX-Bash/main/spotx.sh",
  "spotx_github_repo": "https://github.com/SpotX-Official/SpotX-Bash",
  "custom_spotify_path": "",
  "paid_premium": false,
  "hide_non_music": false,
  "enable_devmode": false,
  "clear_cache": false,
  "debug_mode": false
}
```

---

## Troubleshooting

### Spotify not detected
- Ensure Spotify desktop client is installed.
- If Spotify is installed in a non-standard location, configure `custom_spotify_path` in `~/.config/criz-spotpie/config.json` or through Settings.

### Missing system utilities
- SpotX requires `perl`, `unzip`, `zip`, and `curl` to unpack and patch `xpui.spa`.
- Install them on Ubuntu/Debian via:
  ```bash
  sudo apt install perl unzip zip curl
  ```

### Sudo / Permission prompt
- When Spotify is installed system-wide in `/usr/share/spotify`, write permissions require root privileges. The upstream script will prompt for your normal `sudo` password. CRIZ_SPOTPIE never collects or caches credentials.

---

## Uninstallation

To remove CRIZ_SPOTPIE:

```bash
./scripts/uninstall.sh
```

To remove CRIZ_SPOTPIE including user configuration and logs:

```bash
./scripts/uninstall.sh --purge
```

> [!IMPORTANT]
> The uninstaller removes only CRIZ_SPOTPIE files and configuration. It does **not** touch, modify, or uninstall your Spotify client.

---

## Disclaimer

This project is not affiliated with, endorsed by, or sponsored by Spotify AB or the SpotX project. Use of client modifications may be subject to third-party terms of service. Use at your own discretion.

---

## License

This project is licensed under the [MIT License](LICENSE) &copy; 2026 Crizneil.
Upstream SpotX-Bash is licensed separately by the SpotX-Official team.
