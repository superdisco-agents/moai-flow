#!/bin/bash

################################################################################
# MOAI Ghostty Configuration Auto-Apply Script
# Purpose: Automatically configure Ghostty for Korean font support
# Platform: macOS
# Version: 1.0.0
################################################################################

set -euo pipefail

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="${SCRIPT_DIR}/apply-ghostty-config.log"

# Ghostty config locations
GHOSTTY_CONFIG_DIR="${HOME}/.config/ghostty"
GHOSTTY_CONFIG_FILE="${GHOSTTY_CONFIG_DIR}/config"
GHOSTTY_BACKUP="${GHOSTTY_CONFIG_DIR}/config.backup.$(date +%Y%m%d_%H%M%S)"

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
    echo "Ghostty Configuration Application Log - $(date)" > "${LOG_FILE}"
}

################################################################################
# Ghostty Detection
################################################################################

check_ghostty_installed() {
    print_header "Checking Ghostty Installation"
    
    if ! command -v ghostty &> /dev/null; then
        print_error "Ghostty is not installed or not in PATH"
        print_info "Install Ghostty from: https://github.com/ghostty-org/ghostty"
        return 1
    fi
    
    local ghostty_version=$(ghostty --version 2>/dev/null || echo "unknown")
    print_success "Ghostty is installed: ${ghostty_version}"
    return 0
}

################################################################################
# Configuration Management
################################################################################

create_ghostty_config_dir() {
    print_info "Setting up Ghostty configuration directory..."
    
    if [[ ! -d "${GHOSTTY_CONFIG_DIR}" ]]; then
        mkdir -p "${GHOSTTY_CONFIG_DIR}"
        print_success "Created directory: ${GHOSTTY_CONFIG_DIR}"
    else
        print_info "Directory already exists: ${GHOSTTY_CONFIG_DIR}"
    fi
}

backup_existing_config() {
    print_header "Backing Up Existing Configuration"
    
    if [[ -f "${GHOSTTY_CONFIG_FILE}" ]]; then
        print_info "Found existing config file"
        
        if cp "${GHOSTTY_CONFIG_FILE}" "${GHOSTTY_BACKUP}"; then
            print_success "Configuration backed up to: ${GHOSTTY_BACKUP}"
            log "BACKUP" "Original config backed up"
            return 0
        else
            print_error "Failed to backup configuration"
            return 1
        fi
    else
        print_info "No existing config file found, will create new one"
        return 0
    fi
}

select_korean_font() {
    print_header "Selecting Korean Font"
    
    local fonts=(
        "Noto Sans Mono CJK KR"
        "Noto Serif CJK KR"
        "Meslo LG M Nerd Font Mono"
        "Fira Code Nerd Font"
        "Hack Nerd Font Mono"
    )
    
    echo "Available fonts for Korean support:"
    echo ""
    for i in "${!fonts[@]}"; do
        echo "  $((i+1)). ${fonts[$i]}"
    done
    echo ""
    
    local choice
    while true; do
        read -p "$(echo -e "${YELLOW}?${NC} Select a font (1-${#fonts[@]}): ")" choice
        if [[ "$choice" =~ ^[0-9]+$ ]] && ((choice >= 1 && choice <= ${#fonts[@]})); then
            SELECTED_FONT="${fonts[$((choice-1))]}"
            print_success "Selected font: ${SELECTED_FONT}"
            return 0
        else
            print_warning "Invalid selection. Please try again."
        fi
    done
}

select_font_size() {
    print_header "Selecting Font Size"
    
    echo "Recommended font sizes:"
    echo "  • 10-11 for high DPI displays"
    echo "  • 12-14 for regular displays"
    echo "  • 15-18 for accessibility"
    echo ""
    
    local size
    while true; do
        read -p "$(echo -e "${YELLOW}?${NC} Enter font size (default: 12): ")" size
        size=${size:-12}
        if [[ "$size" =~ ^[0-9]+$ ]] && ((size >= 8 && size <= 50)); then
            FONT_SIZE="$size"
            print_success "Font size set to: ${FONT_SIZE}"
            return 0
        else
            print_warning "Invalid size. Please enter a number between 8 and 50."
        fi
    done
}

generate_korean_config() {
    print_header "Generating Korean-Optimized Configuration"
    
    # Ask for font preferences
    select_korean_font
    select_font_size
    
    print_info "Generating configuration..."
    
    cat > "${GHOSTTY_CONFIG_FILE}" << 'EOF'
################################################################################
# MOAI Ghostty Configuration - Korean Font Support
# Auto-generated configuration with Korean language optimization
# Generated: $(date)
################################################################################

# Font Configuration - Korean Language Support
EOF
    
    # Add selected font settings
    cat >> "${GHOSTTY_CONFIG_FILE}" << EOF

# Primary font with Korean character support
font-family = ${SELECTED_FONT}
font-size = ${FONT_SIZE}
font-feature = calt
font-feature = ss02

# Fallback fonts for missing glyphs
font-fallback = Noto Sans Mono CJK KR
font-fallback = AppleColorEmoji
font-fallback = Apple Color Emoji

# Line spacing for better readability
line-height = 1.2
letter-spacing = 0

################################################################################
# Display Settings
################################################################################

# Window appearance
background = #1e1e2e
foreground = #cdd6f4
cursor-color = #89b4fa
selection-background = #45475a40

# Padding for better spacing
window-padding-x = 8
window-padding-y = 8

# Scrollback buffer
scrollback-limit = 10000
scrollback-multiplier = 3

################################################################################
# Terminal Behavior
################################################################################

# Copy to clipboard immediately on selection
copy-on-select = true

# Shell integration
shell-integration = true
shell-integration-features = sudo,title

# Keybindings for Korean input
# Note: Modify as needed for your input method

################################################################################
# Tab Configuration
################################################################################

# Tab bar visibility
tab-title-style = always
tab-bar-style = powerline

################################################################################
# Cursor Settings
################################################################################

# Cursor style: block, underline, beam
cursor-style = block
cursor-style-blink = true
cursor-thickness = 1

################################################################################
# Performance Settings
################################################################################

# Disable animations for faster startup
animation = false

# Use GPU acceleration
command-palette = true

################################################################################
# Keybindings
################################################################################

# Custom keybindings (examples - modify as needed)
# keybind = global:super+n=new_window
# keybind = global:super+t=new_tab
# keybind = global:super+w=close_surface

EOF
    
    print_success "Configuration generated successfully"
    log "CONFIG" "Generated config with font=${SELECTED_FONT}, size=${FONT_SIZE}"
}

apply_manual_config() {
    print_header "Manual Configuration"
    
    create_ghostty_config_dir
    
    if [[ -f "${GHOSTTY_CONFIG_FILE}" ]]; then
        print_info "Existing config file found"
        if confirm "Replace with Korean-optimized config?"; then
            backup_existing_config
            generate_korean_config
        else
            print_info "Skipping configuration generation"
            return 1
        fi
    else
        print_info "No existing config found"
        if confirm "Create new Korean-optimized config?"; then
            generate_korean_config
        else
            print_error "Cannot proceed without configuration"
            return 1
        fi
    fi
}

apply_config_from_template() {
    print_header "Applying Configuration from Template"
    
    # Check if template exists
    local template_path="${SCRIPT_DIR}/../configs/ghostty-korean-config.template"
    
    if [[ ! -f "${template_path}" ]]; then
        print_warning "Template file not found at: ${template_path}"
        return 1
    fi
    
    print_info "Found template: ${template_path}"
    
    if confirm "Apply configuration from template?"; then
        create_ghostty_config_dir
        backup_existing_config
        
        cp "${template_path}" "${GHOSTTY_CONFIG_FILE}"
        print_success "Template configuration applied"
        log "CONFIG" "Applied template from ${template_path}"
        return 0
    fi
    
    return 1
}

################################################################################
# Configuration Validation
################################################################################

validate_config() {
    print_header "Validating Configuration"
    
    if [[ ! -f "${GHOSTTY_CONFIG_FILE}" ]]; then
        print_error "Configuration file not found: ${GHOSTTY_CONFIG_FILE}"
        return 1
    fi
    
    print_info "Checking configuration file syntax..."
    
    # Basic validation checks
    local errors=0
    
    # Check for common syntax errors
    if grep -E '^[[:space:]]*[^#].*=.*=$' "${GHOSTTY_CONFIG_FILE}" >/dev/null 2>&1; then
        print_warning "Possible duplicate '=' in configuration"
        ((errors++))
    fi
    
    # Check for required settings
    if grep -q "font-family" "${GHOSTTY_CONFIG_FILE}"; then
        print_success "Font configuration found"
    else
        print_warning "No font-family configuration found"
        ((errors++))
    fi
    
    if [[ $errors -eq 0 ]]; then
        print_success "Configuration validation passed"
        return 0
    else
        print_warning "Configuration validation completed with ${errors} issue(s)"
        return 1
    fi
}

################################################################################
# Ghostty Restart
################################################################################

restart_ghostty() {
    print_header "Restarting Ghostty"
    
    print_info "Ghostty changes require a restart to take effect"
    print_info "Please close Ghostty and reopen it"
    
    if confirm "Would you like to close Ghostty now?"; then
        print_info "Closing all Ghostty instances..."
        killall ghostty 2>/dev/null || true
        sleep 1
        print_success "Ghostty closed. You can now reopen it."
    fi
}

################################################################################
# Display Configuration
################################################################################

show_config() {
    print_header "Current Ghostty Configuration"
    
    if [[ -f "${GHOSTTY_CONFIG_FILE}" ]]; then
        echo ""
        cat "${GHOSTTY_CONFIG_FILE}"
        echo ""
    else
        print_warning "No configuration file found"
    fi
}

################################################################################
# Summary Report
################################################################################

print_summary() {
    print_header "Configuration Summary"
    
    echo ""
    if [[ -f "${GHOSTTY_CONFIG_FILE}" ]]; then
        local file_size=$(du -h "${GHOSTTY_CONFIG_FILE}" | cut -f1)
        local last_modified=$(stat -f "%Sm" -t "%Y-%m-%d %H:%M:%S" "${GHOSTTY_CONFIG_FILE}")
        
        print_success "Configuration applied successfully"
        echo ""
        print_info "Configuration file: ${GHOSTTY_CONFIG_FILE}"
        print_info "File size: ${file_size}"
        print_info "Last modified: ${last_modified}"
        
        if [[ -f "${GHOSTTY_BACKUP}" ]]; then
            print_info "Backup location: ${GHOSTTY_BACKUP}"
        fi
    else
        print_warning "Configuration file was not created"
    fi
    
    echo ""
    print_info "Log file: ${LOG_FILE}"
    echo ""
    print_info "Next steps:"
    echo "  1. Restart Ghostty (close and reopen)"
    echo "  2. Verify the configuration with: ./verify-setup.sh"
    echo "  3. Adjust font size if needed in: ${GHOSTTY_CONFIG_FILE}"
    echo ""
}

################################################################################
# Main Execution
################################################################################

main() {
    clear
    print_header "MOAI Ghostty Configuration"
    
    init_log
    log "INFO" "Starting Ghostty configuration application"
    
    # Check Ghostty installation
    if ! check_ghostty_installed; then
        print_error "Cannot proceed without Ghostty"
        exit 1
    fi
    
    # Try template first, then manual configuration
    if ! apply_config_from_template; then
        print_info "Falling back to manual configuration..."
        if ! apply_manual_config; then
            print_error "Configuration application failed"
            exit 1
        fi
    fi
    
    # Validate configuration
    if ! validate_config; then
        print_warning "Configuration validation had issues"
        if ! confirm "Continue anyway?"; then
            print_error "Configuration not applied"
            exit 1
        fi
    fi
    
    # Show configuration
    if confirm "Display configuration?"; then
        show_config
    fi
    
    # Restart Ghostty
    if confirm "Restart Ghostty?"; then
        restart_ghostty
    fi
    
    # Summary
    print_summary
    
    log "INFO" "Ghostty configuration application completed successfully"
}

# Error handling
trap 'print_error "Script interrupted"; exit 1' INT TERM
trap 'print_error "An error occurred on line $LINENO"; exit 1' ERR

# Run main function
main "$@"
