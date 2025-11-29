#!/bin/bash

################################################################################
# MOAI Korean Font Installation Script
# Purpose: Install Korean fonts for terminal and system use
# Platform: macOS
# Version: 1.0.0
################################################################################

set -euo pipefail

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="${SCRIPT_DIR}/install-korean-fonts.log"
FONT_DIR="${HOME}/Library/Fonts"
HOMEBREW_FONTS_TAP="homebrew/cask-fonts"

################################################################################
# Utility Functions
################################################################################

log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[${timestamp}] [${level}] ${message}" | tee -a "${LOG_FILE}"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $*"
    log "INFO" "$*"
}

print_success() {
    echo -e "${GREEN}✓${NC} $*"
    log "SUCCESS" "$*"
}

print_error() {
    echo -e "${RED}✗${NC} $*" >&2
    log "ERROR" "$*"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $*"
    log "WARNING" "$*"
}

print_header() {
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}$*${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    log "SECTION" "$*"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Get user confirmation
confirm() {
    local prompt="$1"
    local response
    
    while true; do
        read -p "$(echo -e "${YELLOW}?${NC} ${prompt} (y/n): ")" response
        case "$response" in
            [yY][eE][sS]|[yY])
                return 0
                ;;
            [nN][oO]|[nN])
                return 1
                ;;
            *)
                echo "Please answer y or n."
                ;;
        esac
    done
}

# Initialize log file
init_log() {
    mkdir -p "$(dirname "${LOG_FILE}")"
    echo "Korean Font Installation Log - $(date)" > "${LOG_FILE}"
}

################################################################################
# System Checks
################################################################################

check_macos() {
    print_header "Checking System Requirements"
    
    if [[ "$OSTYPE" != "darwin"* ]]; then
        print_error "This script is designed for macOS. Detected: $OSTYPE"
        return 1
    fi
    
    print_success "Running on macOS"
    
    local macos_version=$(sw_vers -productVersion)
    print_info "macOS version: ${macos_version}"
    
    if [[ ! -d "${FONT_DIR}" ]]; then
        print_error "Font directory not found: ${FONT_DIR}"
        return 1
    fi
    
    print_success "Font directory verified: ${FONT_DIR}"
}

check_homebrew() {
    print_header "Checking Homebrew Installation"
    
    if ! command_exists brew; then
        print_warning "Homebrew is not installed"
        if confirm "Install Homebrew?"; then
            print_info "Installing Homebrew..."
            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
            print_success "Homebrew installed"
        else
            print_error "Homebrew is required for font installation"
            return 1
        fi
    else
        local brew_version=$(brew --version | head -n 1)
        print_success "Homebrew is installed: ${brew_version}"
    fi
}

check_font_tap() {
    print_header "Setting up Homebrew Font Tap"
    
    if ! brew tap | grep -q "homebrew-cask-fonts"; then
        print_info "Adding fonts tap to Homebrew..."
        if ! brew tap homebrew/cask-fonts 2>/dev/null; then
            print_warning "Could not add official fonts tap, trying alternative..."
            brew tap gromgit/cask-fonts 2>/dev/null || true
        else
            print_success "Fonts tap added successfully"
        fi
    else
        print_success "Fonts tap already configured"
    fi
}

################################################################################
# Font Installation
################################################################################

install_font() {
    local font_cask="$1"
    local font_name="$2"
    
    print_info "Installing ${font_name}..."
    
    if brew list --cask "${font_cask}" &>/dev/null 2>&1; then
        print_warning "${font_name} is already installed"
        return 0
    fi
    
    if brew install --cask "${font_cask}" 2>&1 | tee -a "${LOG_FILE}"; then
        print_success "${font_name} installed successfully"
        return 0
    else
        print_error "Failed to install ${font_name}"
        return 1
    fi
}

install_fonts() {
    print_header "Installing Korean Fonts"
    
    local fonts=(
        "font-noto-sans-cjk:Noto Sans CJK (Google Font)"
        "font-noto-serif-cjk:Noto Serif CJK (Google Font)"
        "font-noto-mono:Noto Mono (Google Font)"
    )
    
    local terminal_fonts=(
        "font-meslo-lg-nerd-font:Meslo LG Nerd Font (Terminal)"
        "font-fira-code-nerd-font:Fira Code Nerd Font (Terminal)"
        "font-hack-nerd-font:Hack Nerd Font (Terminal)"
    )
    
    local installed_count=0
    local failed_count=0
    
    print_info "Installing system fonts for Korean language support..."
    
    for font_spec in "${fonts[@]}"; do
        IFS=':' read -r font_cask font_name <<< "$font_spec"
        if install_font "$font_cask" "$font_name"; then
            ((installed_count++))
        else
            ((failed_count++))
        fi
    done
    
    print_info ""
    print_info "Installing terminal fonts (recommended for Ghostty)..."
    
    for font_spec in "${terminal_fonts[@]}"; do
        IFS=':' read -r font_cask font_name <<< "$font_spec"
        if confirm "Install ${font_name}?"; then
            if install_font "$font_cask" "$font_name"; then
                ((installed_count++))
            else
                ((failed_count++))
            fi
        fi
    done
    
    print_info ""
    print_success "Font installation complete: ${installed_count} installed"
    if [[ ${failed_count} -gt 0 ]]; then
        print_warning "${failed_count} fonts failed to install"
    fi
}

################################################################################
# Font Verification
################################################################################

verify_fonts() {
    print_header "Verifying Installed Fonts"
    
    local required_fonts=(
        "Noto Sans CJK"
        "Noto Serif CJK"
        "Noto Mono"
    )
    
    local missing_count=0
    
    for font in "${required_fonts[@]}"; do
        if ls "${FONT_DIR}/"*"${font}"* >/dev/null 2>&1; then
            print_success "Found: ${font}"
        else
            print_warning "Not found: ${font}"
            ((missing_count++))
        fi
    done
    
    if [[ ${missing_count} -eq 0 ]]; then
        print_success "All required fonts are installed"
        return 0
    else
        print_warning "${missing_count} fonts are missing"
        return 1
    fi
}

################################################################################
# Font Cache Refresh
################################################################################

refresh_font_cache() {
    print_header "Refreshing Font Cache"
    
    print_info "Rebuilding font cache..."
    
    # macOS font cache
    fc-cache -fv 2>/dev/null || true
    
    # Reset macOS font database
    atsutil databases -removeUser 2>/dev/null || true
    
    print_success "Font cache refreshed"
}

################################################################################
# Clean Up
################################################################################

cleanup_temporary_files() {
    print_header "Cleaning Up"
    
    print_info "Removing temporary files..."
    # Add any cleanup operations here
    print_success "Cleanup complete"
}

################################################################################
# Final Report
################################################################################

print_summary() {
    print_header "Installation Summary"
    
    print_info "Log file: ${LOG_FILE}"
    
    echo ""
    print_success "Korean font installation completed!"
    echo ""
    print_info "Next steps:"
    echo "  1. Run: ./apply-ghostty-config.sh"
    echo "  2. Restart Ghostty for font changes to take effect"
    echo "  3. Run: ./verify-setup.sh to confirm everything is working"
    echo ""
}

################################################################################
# Main Execution
################################################################################

main() {
    clear
    print_header "MOAI Korean Font Installation"
    
    init_log
    log "INFO" "Starting Korean font installation"
    
    # Run all checks
    if ! check_macos; then
        print_error "System check failed"
        exit 1
    fi
    
    if ! check_homebrew; then
        print_error "Homebrew check failed"
        exit 1
    fi
    
    check_font_tap
    
    # Installation
    if ! install_fonts; then
        print_warning "Some fonts failed to install, but continuing..."
    fi
    
    # Verification
    if ! verify_fonts; then
        print_warning "Some fonts may not be properly installed"
    fi
    
    # Refresh cache
    refresh_font_cache
    
    # Cleanup
    cleanup_temporary_files
    
    # Summary
    print_summary
    
    log "INFO" "Korean font installation completed successfully"
}

# Error handling
trap 'print_error "Script interrupted"; exit 1' INT TERM
trap 'print_error "An error occurred on line $LINENO"; exit 1' ERR

# Run main function
main "$@"
