#!/data/data/com.termux/files/usr/bin/bash

# =========================================================
# Gscan v10.2 Final - Professional Termux Installer
# Educational / Authorized Security Research Only
# =========================================================

set -e

# ================= COLORS =================
GREEN="\e[1;32m"
RED="\e[1;31m"
BLUE="\e[1;34m"
YELLOW="\e[1;33m"
CYAN="\e[1;36m"
MAGENTA="\e[1;35m"
RESET="\e[0m"

# ================= CONFIG =================
INSTALL_DIR="$(pwd)"
BIN_PATH="$PREFIX/bin/gscan"
CONFIG_DIR="$HOME/.gscan"
LOG_FILE="$CONFIG_DIR/install.log"

# ================= FUNCTIONS =================

banner() {
clear

echo -e "${BLUE}"
echo "===================================================="
echo "        Gscan v10.2 Final Installer"
echo "===================================================="
echo -e "${RESET}"

echo -e "${CYAN}Install Directory:${RESET} $INSTALL_DIR"
echo
}

log() {
mkdir -p "$CONFIG_DIR"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

success() {
echo -e "${GREEN}[+] $1${RESET}"
log "[SUCCESS] $1"
}

info() {
echo -e "${YELLOW}[*] $1${RESET}"
log "[INFO] $1"
}

error() {
echo -e "${RED}[!] $1${RESET}"
log "[ERROR] $1"
}

# ================= INTERNET CHECK =================

check_internet() {

info "Checking internet connection..."

if curl -Is https://github.com >/dev/null 2>&1; then
    success "Internet connection OK"
else
    error "No internet connection detected!"
    exit 1
fi
}

# ================= STORAGE =================

setup_storage() {

info "Setting up storage permission..."

termux-setup-storage || true

sleep 2
}

# ================= UPDATE =================

update_packages() {

info "Updating package lists..."

pkg update -y
pkg upgrade -y

success "Packages updated"
}

# ================= REPOSITORIES =================

setup_repositories() {

info "Installing additional repositories..."

pkg install -y tur-repo || true

success "Repositories configured"
}

# ================= CORE PACKAGES =================

install_core_packages() {

info "Installing core dependencies..."

pkg install -y \
python \
git \
clang \
rust \
openssl \
libxml2 \
libxslt \
libjpeg-turbo \
zlib \
wget \
curl

success "Core packages installed"
}

# ================= PYTHON CHECK =================

check_python() {

info "Checking Python installation..."

if ! command -v python >/dev/null 2>&1; then
    error "Python installation failed!"
    exit 1
fi

PY_VERSION=$(python --version)

success "$PY_VERSION detected"
}

# ================= FILE CHECK =================

check_main_file() {

info "Checking project files..."

if [ ! -f "$INSTALL_DIR/main.py" ]; then
    error "main.py not found!"
    echo
    echo -e "${CYAN}Put install.sh beside main.py${RESET}"
    exit 1
fi

if [ ! -f "$INSTALL_DIR/requirements.txt" ]; then
    error "requirements.txt not found!"
    exit 1
fi

success "Project files verified"
}

# ================= CONFIG =================

create_config() {

info "Creating configuration directory..."

mkdir -p "$CONFIG_DIR"

cat > "$CONFIG_DIR/config.json" << EOF
{
  "version": "10.2",
  "install_dir": "$INSTALL_DIR",
  "created": "$(date)"
}
EOF

success "Configuration created"
}

# ================= VENV =================

setup_venv() {

info "Creating virtual environment..."

python -m venv "$CONFIG_DIR/venv"

. "$CONFIG_DIR/venv/bin/activate"

success "Virtual environment created"
}

# ================= PIP =================

upgrade_pip() {

info "Upgrading pip/setuptools/wheel..."

pip install --upgrade \
pip \
setuptools \
wheel

success "Pip upgraded"
}

# ================= PYTHON MODULES =================

install_python_modules() {

info "Installing Python modules..."

pip install -r requirements.txt

success "Python modules installed"
}

# ================= OPTIONAL TOOLS =================

install_optional_tools() {

info "Installing optional tools..."

pip install holehe || true

success "Optional tools installed"
}

# ================= PLAYWRIGHT =================

install_playwright() {

echo
echo -e "${MAGENTA}[?] Install Playwright support? (y/n)${RESET}"
read -r PLAY

if [[ "$PLAY" == "y" || "$PLAY" == "Y" ]]; then

    info "Installing Playwright..."

    pip install playwright playwright-stealth || true

    echo
    echo -e "${YELLOW}[*] Chromium install may fail on some Termux devices.${RESET}"

    playwright install chromium || true

    success "Playwright installation finished"

else
    info "Skipping Playwright installation"
fi
}

# ================= GLOBAL LAUNCHER =================

create_launcher() {

info "Creating global launcher..."

cat > "$BIN_PATH" << EOF
#!/data/data/com.termux/files/usr/bin/bash

. "$CONFIG_DIR/venv/bin/activate"

python "$INSTALL_DIR/main.py" "\$@"
EOF

chmod +x "$BIN_PATH"

success "Global launcher created"
}

# ================= CLEANUP =================

cleanup() {

info "Cleaning pip cache..."

pip cache purge >/dev/null 2>&1 || true

success "Cleanup complete"
}

# ================= FINAL =================

finish() {

echo
echo -e "${GREEN}====================================================${RESET}"
echo -e "${GREEN}              INSTALLATION COMPLETE${RESET}"
echo -e "${GREEN}====================================================${RESET}"

echo
echo -e "${CYAN}Run the tool using:${RESET}"
echo -e "${GREEN}gscan${RESET}"

echo
echo -e "${CYAN}Manual launch:${RESET}"
echo -e "${GREEN}python main.py${RESET}"

echo
echo -e "${CYAN}Install directory:${RESET}"
echo "$INSTALL_DIR"

echo
echo -e "${CYAN}Config directory:${RESET}"
echo "$CONFIG_DIR"

echo
echo -e "${CYAN}Log file:${RESET}"
echo "$LOG_FILE"

echo
echo -e "${YELLOW}Educational / Authorized Use Only${RESET}"
echo
}

# ================= MAIN =================

main() {

banner

check_internet

setup_storage

update_packages

setup_repositories

install_core_packages

check_python

check_main_file

create_config

setup_venv

upgrade_pip

install_python_modules

install_optional_tools

install_playwright

create_launcher

cleanup

finish
}

# ================= RUN =================

main