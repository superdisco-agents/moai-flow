#!/bin/bash

################################################################################
# MOAI Setup Verification Script
# Purpose: Verify Korean font installation and Ghostty configuration
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
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Symbols
CHECK='✓'
CROSS='✗'
WARN='⚠'
INFO='ℹ'
ARROW='→'

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="${SCRIPT_DIR}/verify-setup.log"
FONT_DIR="${HOME}/Library/Fonts"
GHOSTTY_CONFIG_FILE="${HOME}/.config/ghostty/config"

# Verification counters
CHECKS_TOTAL=0
CHECKS_PASSED=0
CHECKS_FAILED=0
CHECKS_WARNING=0

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
    echo -e "${BLUE}${INFO}${NC} $*"
    log "INFO" "$*"
}

print_success() {
    echo -e "${GREEN}${CHECK}${NC} $*"
    log "SUCCESS" "$*"
    ((CHECKS_PASSED++))
}

print_error() {
    echo -e "${RED}${CROSS}${NC} $*" >&2
    log "ERROR" "$*"
    ((CHECKS_FAILED++))
}

print_warning() {
    echo -e "${YELLOW}${WARN}${NC} $*"
    log "WARNING" "$*"
    ((CHECKS_WARNING++))
}

print_header() {
    echo ""
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}$*${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    log "SECTION" "$*"
}

print_subheader() {
    echo ""
    echo -e "${MAGENTA}▸ $*${NC}"
    echo ""
}

increment_check() {
    ((CHECKS_TOTAL++))
}

# Initialize log file
init_log() {
    mkdir -p "$(dirname "${LOG_FILE}")"
    echo "Setup Verification Log - $(date)" > "${LOG_FILE}"
}

################################################################################
# System Environment Checks
################################################################################

check_macos_version() {
    print_subheader "macOS Version"
    increment_check
    
    local os_version=$(sw_vers -productVersion)
    local os_name=$(sw_vers -productName)
    
    print_info "Operating System: ${os_name} ${os_version}"
    
    # Check if macOS version is 10.13 or later (required for font support)
    local major_version=$(echo "$os_version" | cut -d. -f1)
    local minor_version=$(echo "$os_version" | cut -d. -f2)
    
    if [[ $major_version -ge 11 ]] || [[ $major_version -eq 10 && $minor_version -ge 13 ]]; then
        print_success "macOS version compatible"
    else
        print_error "macOS version too old (requires 10.13+)"
    fi
}

check_architecture() {
    print_subheader "System Architecture"
    increment_check
    
    local arch=$(uname -m)
    print_info "Architecture: ${arch}"
    
    if [[ "$arch" == "arm64" ]] || [[ "$arch" == "x86_64" ]]; then
        print_success "Supported architecture"
    else
        print_warning "Unknown architecture: ${arch}"
    fi
}

check_font_directory() {
    print_subheader "Font Directory"
    increment_check
    
    if [[ -d "${FONT_DIR}" ]]; then
        print_success "Font directory exists: ${FONT_DIR}"
        
        # Check permissions
        if [[ -w "${FONT_DIR}" ]]; then
            print_success "Font directory is writable"
        else
            print_warning "Font directory is not writable"
        fi
        
        # Show font count
        local font_count=$(ls -1 "${FONT_DIR}" | wc -l)
        print_info "Installed fonts: ${font_count}"
    else
        print_error "Font directory not found: ${FONT_DIR}"
    fi
}

################################################################################
# Font Installation Checks
################################################################################

check_korean_font() {
    local font_name="$1"
    
    increment_check
    
    # Check in multiple possible locations
    if ls "${FONT_DIR}/"*"${font_name}"* 2>/dev/null | head -1 > /dev/null 2>&1; then
        local font_path=$(ls "${FONT_DIR}/"*"${font_name}"* 2>/dev/null | head -1)
        print_success "Found: ${font_name}"
        print_info "Location: ${font_path}"
        return 0
    else
        print_warning "Not found: ${font_name}"
        return 1
    fi
}

check_fonts() {
    print_header "Font Installation Verification"
    
    print_subheader "Required Fonts (Core Support)"
    
    local required_fonts=(
        "Noto Sans Mono CJK"
        "Noto Serif CJK"
        "Noto Mono"
    )
    
    local required_found=0
    
    for font in "${required_fonts[@]}"; do
        if check_korean_font "$font"; then
            ((required_found++))
        fi
    done
    
    echo ""
    
    print_subheader "Terminal Fonts (Optional but Recommended)"
    
    local terminal_fonts=(
        "Meslo LG Nerd Font"
        "Fira Code Nerd Font"
        "Hack Nerd Font"
    )
    
    for font in "${terminal_fonts[@]}"; do
        check_korean_font "$font"
    done
    
    echo ""
    
    if [[ ${required_found} -gt 0 ]]; then
        print_success "Korean font support available"
    else
        print_error "No Korean fonts detected"
    fi
}

################################################################################
# Ghostty Configuration Checks
################################################################################

check_ghostty_installed() {
    print_subheader "Ghostty Installation"
    increment_check
    
    if command -v ghostty &> /dev/null; then
        local version=$(ghostty --version 2>/dev/null || echo "unknown version")
        print_success "Ghostty is installed"
        print_info "Version: ${version}"
        return 0
    else
        print_error "Ghostty is not installed"
        return 1
    fi
}

check_ghostty_config_exists() {
    print_subheader "Configuration File"
    increment_check
    
    if [[ -f "${GHOSTTY_CONFIG_FILE}" ]]; then
        local file_size=$(du -h "${GHOSTTY_CONFIG_FILE}" | cut -f1)
        local modified=$(stat -f "%Sm" -t "%Y-%m-%d %H:%M:%S" "${GHOSTTY_CONFIG_FILE}")
        
        print_success "Configuration file found"
        print_info "Location: ${GHOSTTY_CONFIG_FILE}"
        print_info "Size: ${file_size}"
        print_info "Modified: ${modified}"
        return 0
    else
        print_error "Configuration file not found"
        print_info "Expected location: ${GHOSTTY_CONFIG_FILE}"
        return 1
    fi
}

check_ghostty_config_content() {
    print_subheader "Configuration Content"
    
    if [[ ! -f "${GHOSTTY_CONFIG_FILE}" ]]; then
        print_warning "Configuration file not found, skipping content check"
        return 1
    fi
    
    local errors=0
    
    # Check for font-family setting
    increment_check
    if grep -q "^font-family" "${GHOSTTY_CONFIG_FILE}" 2>/dev/null; then
        local font=$(grep "^font-family" "${GHOSTTY_CONFIG_FILE}" | cut -d= -f2 | xargs)
        print_success "Font family configured"
        print_info "Font: ${font}"
    else
        print_error "Font family not configured"
        ((errors++))
    fi
    
    # Check for font-size setting
    increment_check
    if grep -q "^font-size" "${GHOSTTY_CONFIG_FILE}" 2>/dev/null; then
        local size=$(grep "^font-size" "${GHOSTTY_CONFIG_FILE}" | cut -d= -f2 | xargs)
        print_success "Font size configured"
        print_info "Size: ${size}pt"
    else
        print_warning "Font size not configured (using default)"
        ((errors++))
    fi
    
    # Check for fallback fonts
    increment_check
    if grep -q "^font-fallback" "${GHOSTTY_CONFIG_FILE}" 2>/dev/null; then
        print_success "Fallback fonts configured"
    else
        print_warning "No fallback fonts configured"
        ((errors++))
    fi
    
    # Check for shell integration
    increment_check
    if grep -q "^shell-integration" "${GHOSTTY_CONFIG_FILE}" 2>/dev/null; then
        local shell_int=$(grep "^shell-integration" "${GHOSTTY_CONFIG_FILE}" | cut -d= -f2 | xargs)
        print_success "Shell integration configured: ${shell_int}"
    else
        print_info "Shell integration not explicitly configured"
    fi
    
    return $errors
}

check_ghostty_config() {
    print_header "Ghostty Configuration Verification"
    
    if ! check_ghostty_installed; then
        print_error "Cannot verify Ghostty configuration without Ghostty"
        return 1
    fi
    
    check_ghostty_config_exists
    check_ghostty_config_content
}

################################################################################
# Font Rendering Tests
################################################################################

test_korean_text() {
    print_header "Korean Text Rendering Test"
    print_subheader "Sample Korean Text"
    
    echo ""
    echo -e "${CYAN}안녕하세요 - Hello (Korean)${NC}"
    echo -e "${CYAN}こんにちは - Hello (Japanese)${NC}"
    echo -e "${CYAN}你好 - Hello (Chinese Simplified)${NC}"
    echo -e "${CYAN}你好 - Hello (Chinese Traditional)${NC}"
    echo ""
    
    print_info "If the above text displays correctly, your font configuration is working"
    echo ""
    
    increment_check
    if confirm "Does the Korean text display correctly?"; then
        print_success "Korean text rendering working"
    else
        print_error "Korean text rendering may have issues"
    fi
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
                return 1
                ;;
        esac
    done
}

################################################################################
# Homebrew Verification
################################################################################

check_homebrew() {
    print_header "Package Manager Verification"
    print_subheader "Homebrew"
    increment_check
    
    if command -v brew &> /dev/null; then
        local version=$(brew --version | head -n 1)
        print_success "Homebrew is installed"
        print_info "Version: ${version}"
    else
        print_warning "Homebrew is not installed"
        print_info "Homebrew can be installed from: https://brew.sh"
    fi
}

################################################################################
# System Integration Checks
################################################################################

check_system_integration() {
    print_header "System Integration Verification"
    print_subheader "Font Cache"
    increment_check
    
    # Check font cache
    local font_cache_dir="${HOME}/Library/FontCollections"
    if [[ -d "${font_cache_dir}" ]]; then
        print_success "Font cache directory found"
        local cache_size=$(du -sh "${font_cache_dir}" 2>/dev/null | cut -f1)
        print_info "Cache size: ${cache_size}"
    else
        print_info "Font cache not yet created (will be created on first use)"
    fi
}

################################################################################
# Generate Report
################################################################################

generate_report() {
    print_header "Verification Report"
    
    echo ""
    echo -e "${CYAN}Summary${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    local pass_rate=0
    if [[ ${CHECKS_TOTAL} -gt 0 ]]; then
        pass_rate=$((CHECKS_PASSED * 100 / CHECKS_TOTAL))
    fi
    
    echo ""
    echo -e "${GREEN}${CHECK} Checks Passed:${NC}     ${CHECKS_PASSED}/${CHECKS_TOTAL}"
    echo -e "${RED}${CROSS} Checks Failed:${NC}     ${CHECKS_FAILED}/${CHECKS_TOTAL}"
    echo -e "${YELLOW}${WARN} Warnings:${NC}         ${CHECKS_WARNING}/${CHECKS_TOTAL}"
    echo ""
    echo -e "Overall Status:         ${pass_rate}%"
    echo ""
    
    # Status indicator
    if [[ ${CHECKS_FAILED} -eq 0 ]] && [[ ${CHECKS_WARNING} -eq 0 ]]; then
        echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${GREEN}Setup Status: READY${NC}"
        echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    elif [[ ${CHECKS_FAILED} -eq 0 ]]; then
        echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${YELLOW}Setup Status: PARTIALLY READY (review warnings)${NC}"
        echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    else
        echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${RED}Setup Status: NEEDS ATTENTION (fix failures)${NC}"
        echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    fi
    
    echo ""
    print_info "Log file: ${LOG_FILE}"
    echo ""
}

print_recommendations() {
    print_header "Recommendations"
    
    local recommendations=()
    
    if [[ ${CHECKS_FAILED} -gt 0 ]]; then
        if ! command -v ghostty &> /dev/null; then
            recommendations+=("Install Ghostty from https://github.com/ghostty-org/ghostty")
        fi
        
        if [[ ! -f "${GHOSTTY_CONFIG_FILE}" ]]; then
            recommendations+=("Run: ./apply-ghostty-config.sh to apply configuration")
        fi
        
        if [[ ${#recommendations[@]} -eq 0 ]]; then
            recommendations+=("Re-run Korean font installation: ./install-korean-fonts.sh")
        fi
    fi
    
    if [[ ${CHECKS_WARNING} -gt 0 ]]; then
        if ! grep -q "font-family" "${GHOSTTY_CONFIG_FILE}" 2>/dev/null; then
            recommendations+=("Configure font-family in: ${GHOSTTY_CONFIG_FILE}")
        fi
    fi
    
    if [[ ${#recommendations[@]} -gt 0 ]]; then
        echo "Actions to improve setup:"
        echo ""
        local i=1
        for rec in "${recommendations[@]}"; do
            echo -e "  ${ARROW} $rec"
            ((i++))
        done
    else
        echo "Your setup appears to be complete and properly configured!"
    fi
    
    echo ""
}

################################################################################
# Main Execution
################################################################################

main() {
    clear
    print_header "MOAI Setup Verification"
    
    init_log
    log "INFO" "Starting setup verification"
    
    # System checks
    check_macos_version
    check_architecture
    check_font_directory
    
    # Font checks
    check_fonts
    
    # Ghostty checks
    check_ghostty_config
    
    # Integration checks
    check_homebrew
    check_system_integration
    
    # Text rendering test
    test_korean_text
    
    # Generate report
    generate_report
    print_recommendations
    
    log "INFO" "Setup verification completed"
    
    # Exit with appropriate code
    if [[ ${CHECKS_FAILED} -gt 0 ]]; then
        exit 1
    else
        exit 0
    fi
}

# Error handling
trap 'print_error "Script interrupted"; exit 1' INT TERM

# Run main function
main "$@"
