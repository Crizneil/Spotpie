#!/usr/bin/env bash
# ==============================================================================
# CRIZ_SPOTPIE Installer Script
# Installs `criz-spotpie` into user's ~/.local/bin or system-wide /usr/local/bin
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

# Resolve absolute path to project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

SYSTEM_INSTALL=false
DRY_RUN=false

for arg in "$@"; do
  case "$arg" in
    --system)
      SYSTEM_INSTALL=true
      ;;
    --dry-run)
      DRY_RUN=true
      ;;
    --help|-h)
      echo "CRIZ_SPOTPIE Installer"
      echo ""
      echo "Usage: ./scripts/install.sh [OPTIONS]"
      echo ""
      echo "Options:"
      echo "  --system     Install system-wide to /usr/local/bin (requires root/sudo)"
      echo "  --dry-run    Simulate installation without modifying files"
      echo "  --help, -h   Show this help message"
      exit 0
      ;;
  esac
done

echo -e "${CYAN}╔══════════════════════════════════════════════════╗${CLR}"
echo -e "${CYAN}║${CLR}           ${BOLD}${CYAN}CRIZ_SPOTPIE INSTALLER${CLR}                 ${CYAN}║${CLR}"
echo -e "${CYAN}║${CLR}          ${DIM}Spotify Terminal Utility${CLR}                ${CYAN}║${CLR}"
echo -e "${CYAN}╚══════════════════════════════════════════════════╝${CLR}"
echo ""

# 1. Check Python version
if ! command -v python3 >/dev/null 2>&1; then
  echo -e "${RED}[ERROR]${CLR} python3 is not installed on this system."
  echo "Please install Python 3.10 or newer (sudo apt install python3)."
  exit 1
fi

PY_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
PY_MAJOR=$(echo "${PY_VERSION}" | cut -d. -f1)
PY_MINOR=$(echo "${PY_VERSION}" | cut -d. -f2)

if [ "${PY_MAJOR}" -lt 3 ] || ([ "${PY_MAJOR}" -eq 3 ] && [ "${PY_MINOR}" -lt 10 ]); then
  echo -e "${RED}[ERROR]${CLR} Python 3.10+ is required (found Python ${PY_VERSION})."
  exit 1
fi
echo -e " ${GREEN}✔${CLR} Python ${PY_VERSION} detected."

# 2. Determine target directory
if [ "${SYSTEM_INSTALL}" = true ]; then
  TARGET_DIR="/usr/local/bin"
  if [ "$(id -u)" -ne 0 ]; then
    echo -e "${YELLOW}[NOTICE]${CLR} System-wide installation to ${TARGET_DIR} requires root privileges."
    SUDO="sudo"
  else
    SUDO=""
  fi
else
  TARGET_DIR="${HOME}/.local/bin"
  SUDO=""
fi

TARGET_BIN="${TARGET_DIR}/criz-spotpie"
echo -e " ${GREEN}✔${CLR} Target installation path: ${CYAN}${TARGET_BIN}${CLR}"

if [ "${DRY_RUN}" = true ]; then
  echo ""
  echo -e " ${YELLOW}[DRY-RUN]${CLR} Pre-flight verification passed successfully."
  echo -e " ${YELLOW}[DRY-RUN]${CLR} Would write launcher script to: ${TARGET_BIN}"
  exit 0
fi

# 3. Create target directory
mkdir -p "${TARGET_DIR}"

# 4. Generate launcher script
TEMP_LAUNCHER=$(mktemp)
cat << 'EOF' > "${TEMP_LAUNCHER}"
#!/usr/bin/env bash
# CRIZ_SPOTPIE Launcher
PROJECT_ROOT="__PROJECT_ROOT__"
PYTHON_BIN="__PYTHON_BIN__"

export PYTHONPATH="${PROJECT_ROOT}:${PYTHONPATH}"
exec "${PYTHON_BIN}" "${PROJECT_ROOT}/main.py" "$@"
EOF

# Substitute actual paths safely
sed -i "s|__PROJECT_ROOT__|${PROJECT_ROOT}|g" "${TEMP_LAUNCHER}"
sed -i "s|__PYTHON_BIN__|$(which python3)|g" "${TEMP_LAUNCHER}"
chmod 755 "${TEMP_LAUNCHER}"

if [ -n "${SUDO}" ]; then
  ${SUDO} mv "${TEMP_LAUNCHER}" "${TARGET_BIN}"
  ${SUDO} chmod 755 "${TARGET_BIN}"
else
  mv "${TEMP_LAUNCHER}" "${TARGET_BIN}"
  chmod 755 "${TARGET_BIN}"
fi

echo -e " ${GREEN}✔${CLR} Launcher script installed to ${BOLD}${TARGET_BIN}${CLR}."

# 5. Check PATH
case ":${PATH}:" in
  *:"${TARGET_DIR}":*)
    PATH_OK=true
    ;;
  *)
    PATH_OK=false
    ;;
esac

echo ""
echo -e "${GREEN}[SUCCESS] CRIZ_SPOTPIE installed successfully!${CLR}"
echo ""

if [ "${PATH_OK}" = false ]; then
  echo -e "${YELLOW}[NOTE]${CLR} ${TARGET_DIR} is not currently in your PATH environment variable."
  echo "To run '${CYAN}criz-spotpie${CLR}' from anywhere, add this line to your ~/.bashrc or ~/.profile:"
  echo ""
  echo -e "    ${BOLD}export PATH=\"\$HOME/.local/bin:\$PATH\"${CLR}"
  echo ""
  echo "Then reload your shell: source ~/.bashrc"
else
  echo -e "You can now launch the application by running: ${BOLD}${CYAN}criz-spotpie${CLR}"
fi
echo ""
