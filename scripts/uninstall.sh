#!/usr/bin/env bash
# ==============================================================================
# CRIZ_SPOTPIE Uninstaller Script
# Removes `criz-spotpie` launcher and optional user configuration.
# NOTE: This NEVER touches or uninstalls Spotify itself.
# ==============================================================================

set -e

CLR='\033[0m'
CYAN='\033[96m'
BLUE='\033[94m'
GREEN='\033[92m'
YELLOW='\033[93m'
RED='\033[91m'
BOLD='\033[1m'
DIM='\033[2m'

DRY_RUN=false
PURGE=false

for arg in "$@"; do
  case "$arg" in
    --purge)
      PURGE=true
      ;;
    --dry-run)
      DRY_RUN=true
      ;;
    --help|-h)
      echo "CRIZ_SPOTPIE Uninstaller"
      echo ""
      echo "Usage: ./scripts/uninstall.sh [OPTIONS]"
      echo ""
      echo "Options:"
      echo "  --purge      Also delete user configuration & logs (~/.config/criz-spotpie)"
      echo "  --dry-run    Simulate uninstallation without removing files"
      echo "  --help, -h   Show this help message"
      exit 0
      ;;
  esac
done

echo -e "${CYAN}╔══════════════════════════════════════════════════╗${CLR}"
echo -e "${CYAN}║${CLR}          ${BOLD}${CYAN}CRIZ_SPOTPIE UNINSTALLER${CLR}                ${CYAN}║${CLR}"
echo -e "${CYAN}║${CLR}          ${DIM}Spotify Terminal Utility${CLR}                ${CYAN}║${CLR}"
echo -e "${CYAN}╚══════════════════════════════════════════════════╝${CLR}"
echo ""

CANDIDATES=(
  "${HOME}/.local/bin/criz-spotpie"
  "/usr/local/bin/criz-spotpie"
)

REMOVED=0

for bin in "${CANDIDATES[@]}"; do
  if [ -f "${bin}" ]; then
    if [ "${DRY_RUN}" = true ]; then
      echo -e " ${YELLOW}[DRY-RUN]${CLR} Would remove launcher: ${bin}"
      REMOVED=$((REMOVED + 1))
    else
      if [ -w "${bin}" ] || [ -w "$(dirname "${bin}")" ]; then
        rm -f "${bin}"
        echo -e " ${GREEN}✔${CLR} Removed launcher: ${bin}"
        REMOVED=$((REMOVED + 1))
      elif command -v sudo >/dev/null 2>&1; then
        echo -e " ${YELLOW}[NOTICE]${CLR} Removing ${bin} requires root privileges..."
        sudo rm -f "${bin}"
        echo -e " ${GREEN}✔${CLR} Removed launcher: ${bin}"
        REMOVED=$((REMOVED + 1))
      else
        echo -e " ${RED}[ERROR]${CLR} Cannot remove ${bin}: Permission denied."
      fi
    fi
  fi
done

CONFIG_DIR="${HOME}/.config/criz-spotpie"
if [ "${PURGE}" = true ] && [ -d "${CONFIG_DIR}" ]; then
  if [ "${DRY_RUN}" = true ]; then
    echo -e " ${YELLOW}[DRY-RUN]${CLR} Would purge configuration directory: ${CONFIG_DIR}"
  else
    rm -rf "${CONFIG_DIR}"
    echo -e " ${GREEN}✔${CLR} Purged configuration directory: ${CONFIG_DIR}"
  fi
elif [ -d "${CONFIG_DIR}" ]; then
  echo ""
  echo -e " ${DIM}Note: User configuration and logs preserved at: ${CONFIG_DIR}${CLR}"
  echo -e " ${DIM}Pass '--purge' to remove configuration as well.${CLR}"
fi

echo ""
if [ "${DRY_RUN}" = true ]; then
  echo -e "${GREEN}[SUCCESS] Dry run completed.${CLR}"
elif [ "${REMOVED}" -gt 0 ]; then
  echo -e "${GREEN}[SUCCESS] CRIZ_SPOTPIE was successfully uninstalled.${CLR}"
  echo -e "${DIM}Spotify was NOT modified or uninstalled.${CLR}"
else
  echo -e "${YELLOW}[INFO] No CRIZ_SPOTPIE launcher found in standard locations.${CLR}"
fi
echo ""
