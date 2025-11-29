#!/usr/bin/env bash
# MoAI-ADK Bash Installer
# Version: 1.0.0
# Description: Complete installation script for MoAI-ADK with Korean language support

set -euo pipefail

# ============================================================================
# Configuration & Constants
# ============================================================================

SCRIPT_VERSION="1.0.0"
PYTHON_MIN_VERSION="3.11"
MOAI_ADK_PACKAGE="moai-adk"
MOAI_CONFIG_DIR="${HOME}/.moai"
LOG_FILE="${MOAI_CONFIG_DIR}/install.log"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Installation flags
INSTALL_KOREAN_FONTS=false
SKIP_PYTHON_CHECK=false
SKIP_UV_INSTALL=false
VERBOSE=false
DRY_RUN=false
FORCE_REINSTALL=false

# ============================================================================
# Utility Functions
# ============================================================================

log() {
    local level=$1
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')

    if [[ "$VERBOSE" == "true" ]] || [[ "$level" != "DEBUG" ]]; then
        case "$level" in
            ERROR)
                echo -e "${RED}[ERROR]${NC} $message" >&2
                ;;
            SUCCESS)
                echo -e "${GREEN}[SUCCESS]${NC} $message"
                ;;
            WARNING)
                echo -e "${YELLOW}[WARNING]${NC} $message"
                ;;
            INFO)
                echo -e "${BLUE}[INFO]${NC} $message"
                ;;
            DEBUG)
                echo -e "${CYAN}[DEBUG]${NC} $message"
                ;;
        esac
    fi

    # Always log to file if directory exists
    if [[ -d "$MOAI_CONFIG_DIR" ]]; then
        echo "[$timestamp] [$level] $message" >> "$LOG_FILE"
    fi
}

print_banner() {
    cat << 'EOF'
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║           MoAI-ADK Installation Script v1.0.0               ║
║           Mixture of Agents AI Development Kit              ║
║                                                              ║
║           Support: Python 3.11+ | Korean Language           ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
EOF
}

print_usage() {
    cat << EOF

Usage: $0 [OPTIONS]

Options:
    -k, --korean          Install Korean language fonts and support
    -s, --skip-python     Skip Python version check
    -u, --skip-uv         Skip UV package manager installation
    -v, --verbose         Enable verbose output
    -d, --dry-run         Show what would be installed without installing
    -f, --force           Force reinstallation of existing packages
    -h, --help            Display this help message

Examples:
    # Basic installation
    $0

    # Install with Korean language support
    $0 --korean

    # Dry run to see what would be installed
    $0 --dry-run --verbose

    # Force reinstall everything
    $0 --force

EOF
}

confirm() {
    local prompt="$1"
    local default="${2:-n}"

    if [[ "$DRY_RUN" == "true" ]]; then
        log INFO "[DRY RUN] Would prompt: $prompt"
        return 0
    fi

    while true; do
        if [[ "$default" == "y" ]]; then
            read -p "$prompt [Y/n]: " yn
            yn=${yn:-y}
        else
            read -p "$prompt [y/N]: " yn
            yn=${yn:-n}
        fi

        case $yn in
            [Yy]* ) return 0;;
            [Nn]* ) return 1;;
            * ) echo "Please answer yes or no.";;
        esac
    done
}

check_command() {
    local cmd=$1
    if command -v "$cmd" &> /dev/null; then
        return 0
    else
        return 1
    fi
}

version_compare() {
    # Compare version strings (e.g., 3.11.0 vs 3.11)
    # Returns 0 if $1 >= $2, 1 otherwise
    local ver1=$1
    local ver2=$2

    if [[ "$ver1" == "$ver2" ]]; then
        return 0
    fi

    local IFS=.
    local i ver1_arr=($ver1) ver2_arr=($ver2)

    # Fill empty positions with zeros
    for ((i=${#ver1_arr[@]}; i<${#ver2_arr[@]}; i++)); do
        ver1_arr[i]=0
    done

    for ((i=0; i<${#ver1_arr[@]}; i++)); do
        if [[ -z ${ver2_arr[i]} ]]; then
            ver2_arr[i]=0
        fi
        if ((10#${ver1_arr[i]} > 10#${ver2_arr[i]})); then
            return 0
        fi
        if ((10#${ver1_arr[i]} < 10#${ver2_arr[i]})); then
            return 1
        fi
    done
    return 0
}

# ============================================================================
# System Checks
# ============================================================================

detect_os() {
    local os_type=""

    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        os_type="linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        os_type="macos"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        os_type="windows"
    else
        os_type="unknown"
    fi

    echo "$os_type"
}

detect_architecture() {
    local arch=$(uname -m)
    case "$arch" in
        x86_64|amd64)
            echo "x86_64"
            ;;
        arm64|aarch64)
            echo "arm64"
            ;;
        *)
            echo "unknown"
            ;;
    esac
}

check_python_version() {
    log INFO "Checking Python version..."

    if [[ "$SKIP_PYTHON_CHECK" == "true" ]]; then
        log WARNING "Skipping Python version check (--skip-python flag)"
        return 0
    fi

    if ! check_command python3; then
        log ERROR "Python 3 is not installed"
        log INFO "Please install Python ${PYTHON_MIN_VERSION} or higher"
        log INFO "Visit: https://www.python.org/downloads/"
        return 1
    fi

    local python_version=$(python3 --version | awk '{print $2}')
    log DEBUG "Found Python version: $python_version"

    if ! version_compare "$python_version" "$PYTHON_MIN_VERSION"; then
        log ERROR "Python version $python_version is below minimum required version $PYTHON_MIN_VERSION"
        log INFO "Please upgrade Python to ${PYTHON_MIN_VERSION} or higher"
        return 1
    fi

    log SUCCESS "Python $python_version is installed (minimum: $PYTHON_MIN_VERSION)"
    return 0
}

check_disk_space() {
    log INFO "Checking available disk space..."

    local required_mb=500
    local available_mb

    if [[ "$(detect_os)" == "macos" ]]; then
        available_mb=$(df -m ~ | awk 'NR==2 {print $4}')
    else
        available_mb=$(df -BM ~ | awk 'NR==2 {print $4}' | sed 's/M//')
    fi

    log DEBUG "Available disk space: ${available_mb}MB"

    if [[ $available_mb -lt $required_mb ]]; then
        log WARNING "Low disk space: ${available_mb}MB available (recommended: ${required_mb}MB)"
        if ! confirm "Continue with installation?"; then
            log ERROR "Installation cancelled due to low disk space"
            return 1
        fi
    else
        log SUCCESS "Sufficient disk space available: ${available_mb}MB"
    fi

    return 0
}

check_network_connectivity() {
    log INFO "Checking network connectivity..."

    if check_command curl; then
        if curl -s --head --max-time 5 https://pypi.org > /dev/null 2>&1; then
            log SUCCESS "Network connectivity verified"
            return 0
        fi
    elif check_command wget; then
        if wget --spider --timeout=5 https://pypi.org > /dev/null 2>&1; then
            log SUCCESS "Network connectivity verified"
            return 0
        fi
    fi

    log WARNING "Unable to verify network connectivity to PyPI"
    if ! confirm "Continue without network verification?"; then
        log ERROR "Installation cancelled"
        return 1
    fi

    return 0
}

# ============================================================================
# UV Package Manager Installation
# ============================================================================

install_uv() {
    log INFO "Installing UV package manager..."

    if [[ "$SKIP_UV_INSTALL" == "true" ]]; then
        log WARNING "Skipping UV installation (--skip-uv flag)"
        return 0
    fi

    if check_command uv && [[ "$FORCE_REINSTALL" == "false" ]]; then
        local uv_version=$(uv --version 2>/dev/null | awk '{print $2}')
        log SUCCESS "UV is already installed (version: $uv_version)"
        return 0
    fi

    if [[ "$DRY_RUN" == "true" ]]; then
        log INFO "[DRY RUN] Would install UV package manager"
        return 0
    fi

    log INFO "Downloading UV installer..."

    if check_command curl; then
        if curl -LsSf https://astral.sh/uv/install.sh | sh; then
            log SUCCESS "UV installed successfully"
        else
            log ERROR "Failed to install UV"
            return 1
        fi
    else
        log ERROR "curl is required to install UV"
        log INFO "Please install curl and try again"
        return 1
    fi

    # Add UV to PATH if not already present
    local shell_config=""
    if [[ -f "$HOME/.bashrc" ]]; then
        shell_config="$HOME/.bashrc"
    elif [[ -f "$HOME/.zshrc" ]]; then
        shell_config="$HOME/.zshrc"
    fi

    if [[ -n "$shell_config" ]]; then
        if ! grep -q 'export PATH="$HOME/.cargo/bin:$PATH"' "$shell_config"; then
            echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> "$shell_config"
            log INFO "Added UV to PATH in $shell_config"
            log WARNING "Please restart your shell or run: source $shell_config"
        fi
    fi

    return 0
}

# ============================================================================
# MoAI-ADK Installation
# ============================================================================

create_moai_directory() {
    log INFO "Creating MoAI configuration directory..."

    if [[ -d "$MOAI_CONFIG_DIR" ]]; then
        log DEBUG "Directory already exists: $MOAI_CONFIG_DIR"

        if [[ "$FORCE_REINSTALL" == "true" ]]; then
            log WARNING "Force reinstall: Backing up existing configuration"
            local backup_dir="${MOAI_CONFIG_DIR}.backup.$(date +%Y%m%d_%H%M%S)"

            if [[ "$DRY_RUN" == "false" ]]; then
                mv "$MOAI_CONFIG_DIR" "$backup_dir"
                log INFO "Backup created: $backup_dir"
            else
                log INFO "[DRY RUN] Would backup to: $backup_dir"
            fi
        fi
    fi

    if [[ "$DRY_RUN" == "false" ]]; then
        mkdir -p "$MOAI_CONFIG_DIR"/{models,cache,logs,config}
        log SUCCESS "Created MoAI directory structure"
    else
        log INFO "[DRY RUN] Would create: $MOAI_CONFIG_DIR"
    fi

    return 0
}

install_moai_adk() {
    log INFO "Installing MoAI-ADK package..."

    if ! check_command uv; then
        log ERROR "UV is not installed or not in PATH"
        log INFO "Run: source ~/.bashrc (or ~/.zshrc) to update PATH"
        return 1
    fi

    local install_cmd="uv pip install"

    if [[ "$FORCE_REINSTALL" == "true" ]]; then
        install_cmd="$install_cmd --force-reinstall"
        log INFO "Force reinstalling $MOAI_ADK_PACKAGE"
    fi

    if [[ "$DRY_RUN" == "true" ]]; then
        log INFO "[DRY RUN] Would run: $install_cmd $MOAI_ADK_PACKAGE"
        return 0
    fi

    if $install_cmd "$MOAI_ADK_PACKAGE"; then
        log SUCCESS "MoAI-ADK installed successfully"
    else
        log ERROR "Failed to install MoAI-ADK"
        return 1
    fi

    return 0
}

verify_installation() {
    log INFO "Verifying MoAI-ADK installation..."

    if [[ "$DRY_RUN" == "true" ]]; then
        log INFO "[DRY RUN] Would verify installation"
        return 0
    fi

    # Check if package is importable
    if python3 -c "import moai_adk; print(f'MoAI-ADK version: {moai_adk.__version__}')" 2>/dev/null; then
        log SUCCESS "MoAI-ADK is correctly installed and importable"
    else
        log ERROR "MoAI-ADK installation verification failed"
        log INFO "The package is installed but may not be properly configured"
        return 1
    fi

    return 0
}

# ============================================================================
# Korean Language Support
# ============================================================================

install_korean_fonts_macos() {
    log INFO "Installing Korean fonts for macOS..."

    if ! check_command brew; then
        log WARNING "Homebrew not found. Korean font installation skipped."
        log INFO "Install Homebrew from: https://brew.sh"
        return 1
    fi

    if [[ "$DRY_RUN" == "true" ]]; then
        log INFO "[DRY RUN] Would install Korean fonts via Homebrew"
        return 0
    fi

    local fonts=("font-nanum" "font-nanum-gothic-coding")

    for font in "${fonts[@]}"; do
        log INFO "Installing $font..."
        if brew install --cask "$font" 2>/dev/null; then
            log SUCCESS "Installed $font"
        else
            log WARNING "Failed to install $font (may already be installed)"
        fi
    done

    return 0
}

install_korean_fonts_linux() {
    log INFO "Installing Korean fonts for Linux..."

    if [[ "$DRY_RUN" == "true" ]]; then
        log INFO "[DRY RUN] Would install Korean fonts"
        return 0
    fi

    if check_command apt-get; then
        sudo apt-get update
        sudo apt-get install -y fonts-nanum fonts-nanum-coding
    elif check_command yum; then
        sudo yum install -y google-noto-sans-cjk-ttc-fonts
    elif check_command pacman; then
        sudo pacman -S --noconfirm noto-fonts-cjk
    else
        log WARNING "Unknown package manager. Please install Korean fonts manually."
        return 1
    fi

    log SUCCESS "Korean fonts installed"
    return 0
}

configure_korean_locale() {
    log INFO "Configuring Korean locale support..."

    local moai_config_file="${MOAI_CONFIG_DIR}/config/settings.json"

    if [[ "$DRY_RUN" == "true" ]]; then
        log INFO "[DRY RUN] Would create Korean locale configuration"
        return 0
    fi

    cat > "$moai_config_file" << 'EOF'
{
  "language": "ko_KR",
  "locale": "ko_KR.UTF-8",
  "encoding": "UTF-8",
  "ui": {
    "font_family": "Nanum Gothic",
    "font_size": 14
  },
  "features": {
    "korean_nlp": true,
    "korean_tokenizer": true
  }
}
EOF

    log SUCCESS "Korean locale configuration created: $moai_config_file"
    return 0
}

setup_korean_support() {
    if [[ "$INSTALL_KOREAN_FONTS" != "true" ]]; then
        return 0
    fi

    log INFO "Setting up Korean language support..."

    local os_type=$(detect_os)

    case "$os_type" in
        macos)
            install_korean_fonts_macos
            ;;
        linux)
            install_korean_fonts_linux
            ;;
        *)
            log WARNING "Korean font installation not supported on $os_type"
            ;;
    esac

    configure_korean_locale

    return 0
}

# ============================================================================
# Post-Installation
# ============================================================================

create_activation_script() {
    log INFO "Creating activation helper script..."

    local activate_script="${MOAI_CONFIG_DIR}/activate.sh"

    if [[ "$DRY_RUN" == "true" ]]; then
        log INFO "[DRY RUN] Would create activation script"
        return 0
    fi

    cat > "$activate_script" << 'EOF'
#!/usr/bin/env bash
# MoAI-ADK Activation Script

export MOAI_CONFIG_DIR="${HOME}/.moai"
export MOAI_CACHE_DIR="${MOAI_CONFIG_DIR}/cache"
export MOAI_LOG_DIR="${MOAI_CONFIG_DIR}/logs"

# Add UV to PATH if not already present
export PATH="${HOME}/.cargo/bin:${PATH}"

echo "MoAI-ADK environment activated"
echo "Config directory: $MOAI_CONFIG_DIR"
EOF

    chmod +x "$activate_script"
    log SUCCESS "Activation script created: $activate_script"
    log INFO "To activate, run: source $activate_script"

    return 0
}

print_next_steps() {
    cat << EOF

╔══════════════════════════════════════════════════════════════╗
║                  Installation Complete!                     ║
╚══════════════════════════════════════════════════════════════╝

Next Steps:

1. Activate MoAI environment:
   ${GREEN}source ${MOAI_CONFIG_DIR}/activate.sh${NC}

2. Verify installation:
   ${GREEN}python3 -c "import moai_adk; print(moai_adk.__version__)"${NC}

3. View documentation:
   ${GREEN}python3 -m moai_adk --help${NC}

4. Configuration directory:
   ${BLUE}${MOAI_CONFIG_DIR}${NC}

5. View installation logs:
   ${BLUE}${LOG_FILE}${NC}

EOF

    if [[ "$INSTALL_KOREAN_FONTS" == "true" ]]; then
        echo "Korean language support has been configured."
        echo "Settings: ${MOAI_CONFIG_DIR}/config/settings.json"
        echo ""
    fi
}

# ============================================================================
# Main Installation Flow
# ============================================================================

parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -k|--korean)
                INSTALL_KOREAN_FONTS=true
                shift
                ;;
            -s|--skip-python)
                SKIP_PYTHON_CHECK=true
                shift
                ;;
            -u|--skip-uv)
                SKIP_UV_INSTALL=true
                shift
                ;;
            -v|--verbose)
                VERBOSE=true
                shift
                ;;
            -d|--dry-run)
                DRY_RUN=true
                VERBOSE=true
                shift
                ;;
            -f|--force)
                FORCE_REINSTALL=true
                shift
                ;;
            -h|--help)
                print_usage
                exit 0
                ;;
            *)
                log ERROR "Unknown option: $1"
                print_usage
                exit 1
                ;;
        esac
    done
}

main() {
    parse_arguments "$@"

    print_banner

    if [[ "$DRY_RUN" == "true" ]]; then
        log WARNING "DRY RUN MODE: No changes will be made"
    fi

    log INFO "Starting MoAI-ADK installation..."
    log INFO "OS: $(detect_os) | Architecture: $(detect_architecture)"

    # System checks
    check_python_version || exit 1
    check_disk_space || exit 1
    check_network_connectivity || exit 1

    # Create config directory
    create_moai_directory || exit 1

    # Install UV
    install_uv || exit 1

    # Install MoAI-ADK
    install_moai_adk || exit 1

    # Verify installation
    verify_installation || exit 1

    # Korean language support
    setup_korean_support

    # Post-installation
    create_activation_script

    # Success
    log SUCCESS "Installation completed successfully!"

    if [[ "$DRY_RUN" == "false" ]]; then
        print_next_steps
    fi

    exit 0
}

# Run main function
main "$@"
