#!/data/data/com.termux/files/usr/bin/bash

# =========================================================
# Gscan v11.0 Professional - Termux Installer
# Developer: Anupom
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
MAIN_FILE="gscan.py"
BIN_PATH="$PREFIX/bin/gscan"
CONFIG_DIR="$HOME/.gscan"
LOG_FILE="$CONFIG_DIR/install.log"

# ================= FUNCTIONS =================

banner() {
    clear
    echo -e "${MAGENTA}"
    echo "===================================================="
    echo "       Gscan v11.0 Professional Installer"
    echo "               Developed by: Anupom"
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
    info "Updating Termux package lists..."
    pkg update -y
    pkg upgrade -y
    success "Packages updated"
}

# ================= REPOSITORIES =================

setup_repositories() {
    info "Installing additional repositories..."
    pkg install -y tur-repo root-repo || true
    success "Repositories configured"
}

# ================= CORE PACKAGES =================

install_core_packages() {
    info "Installing core build dependencies for Python..."
    # make, pkg-config, and libffi are crucial for building Python packages like aiohttp
    pkg install -y \
        python git clang rust openssl \
        libxml2 libxslt libjpeg-turbo zlib \
        wget curl make pkg-config libffi

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
    if [ ! -f "$INSTALL_DIR/$MAIN_FILE" ]; then
        error "$MAIN_FILE not found!"
        echo
        echo -e "${CYAN}Put install.sh beside $MAIN_FILE${RESET}"
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
  "developer": "Anupom",
  "version": "11.0",
  "install_dir": "$INSTALL_DIR",
  "created": "$(date)"
}
EOF
    success "Configuration created"
}

# ================= VENV =================

setup_venv() {
    info "Creating secure virtual environment..."
    python -m venv "$CONFIG_DIR/venv"
    success "Virtual environment created"
}

# ================= PIP & REQUIREMENTS =================

install_python_modules() {
    info "Activating VENV & Upgrading Pip..."
    . "$CONFIG_DIR/venv/bin/activate"
    
    pip install --upgrade pip setuptools wheel
    
    info "Installing required Python modules..."
    pip install -r "$INSTALL_DIR/requirements.txt"
    
    # Installing holehe inside venv so subprocess can use it securely
    info "Installing OSINT modules (Holehe)..."
    pip install holehe
    
    success "All Python modules and tools installed"
}

# ================= GLOBAL LAUNCHER =================

create_launcher() {
    info "Creating global launcher command ('gscan')..."
    
    cat > "$BIN_PATH" << EOF
#!/data/data/com.termux/files/usr/bin/bash
. "$CONFIG_DIR/venv/bin/activate"
python "$INSTALL_DIR/$MAIN_FILE" "\$@"
EOF

    chmod +x "$BIN_PATH"
    success "Global launcher created"
}

# ================= CLEANUP =================

cleanup() {
    info "Cleaning package cache..."
    . "$CONFIG_DIR/venv/bin/activate"
    pip cache purge >/dev/null 2>&1 || true
    apt clean >/dev/null 2>&1 || true
    success "Cleanup complete"
}

# ================= FINAL =================

finish() {
    echo
    echo -e "${GREEN}====================================================${RESET}"
    echo -e "${GREEN}             INSTALLATION COMPLETE!                 ${RESET}"
    echo -e "${GREEN}====================================================${RESET}"
    echo
    echo -e "${CYAN}Run the tool from anywhere using command:${RESET}"
    echo -e "${GREEN}gscan${RESET}"
    echo
    echo -e "${CYAN}Developed by:${RESET} ${YELLOW}Anupom${RESET}"
    echo -e "${CYAN}Install directory:${RESET} $INSTALL_DIR"
    echo -e "${CYAN}Log file:${RESET} $LOG_FILE"
    echo
    echo -e "${YELLOW}[!] Note: Authorized Educational Research Only${RESET}"
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
    install_python_modules
    create_launcher
    cleanup
    finish
}

# ================= RUN =================
main