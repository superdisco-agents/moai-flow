#!/bin/bash

################################################################################
# MOAI Complete Setup Script
# Purpose: Run all installation scripts in sequence
# Platform: macOS
# Version: 1.0.0
################################################################################

set -euo pipefail

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m'

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="${SCRIPT_DIR}/logs"
MASTER_LOG="${LOG_DIR}/setup-all.log"

# Execution tracking
STEP_COUNT=0
STEP_CURRENT=0
START_TIME=$(date +%s)

################################################################################
# Utility Functions
################################################################################

log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    # Log to file
    mkdir -p "${LOG_DIR}"
    echo "[${timestamp}] [${level}] ${message}" | tee -a "${MASTER_LOG}"
}

print_header() {
    clear
    echo ""
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}$*${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

print_step() {
    ((STEP_CURRENT++))
    echo ""
    echo -e "${BLUE}Step ${STEP_CURRENT}/${STEP_COUNT}: $*${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    log "STEP" "[$((STEP_CURRENT))/${STEP_COUNT}] $*"
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

print_section() {
    echo ""
    echo -e "${MAGENTA}▸ $*${NC}"
    log "SECTION" "$*"
}

# Confirm before proceeding
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

# Check if script exists and is executable
check_script() {
    local script="$1"
    
    if [[ ! -f "${SCRIPT_DIR}/${script}" ]]; then
        print_error "Script not found: ${SCRIPT_DIR}/${script}"
        return 1
    fi
    
    if [[ ! -x "${SCRIPT_DIR}/${script}" ]]; then
        print_warning "Script not executable, making executable..."
        chmod +x "${SCRIPT_DIR}/${script}"
    fi
    
    return 0
}

# Run script and handle errors
run_script() {
    local script="$1"
    local description="$2"
    
    print_step "$description"
    
    if ! check_script "$script"; then
        print_error "Cannot proceed without $script"
        return 1
    fi
    
    print_info "Running: ${script}"
    
    if "${SCRIPT_DIR}/${script}" 2>&1 | tee -a "${MASTER_LOG}"; then
        print_success "$description completed successfully"
        return 0
    else
        print_error "$description failed"
        log "ERROR" "$script exited with error"
        return 1
    fi
}

# Get elapsed time
get_elapsed() {
    local end_time=$(date +%s)
    local elapsed=$((end_time - START_TIME))
    
    local hours=$((elapsed / 3600))
    local minutes=$(((elapsed % 3600) / 60))
    local seconds=$((elapsed % 60))
    
    if [[ $hours -gt 0 ]]; then
        echo "${hours}h ${minutes}m ${seconds}s"
    elif [[ $minutes -gt 0 ]]; then
        echo "${minutes}m ${seconds}s"
    else
        echo "${seconds}s"
    fi
}

################################################################################
# Pre-Installation Checks
################################################################################

check_prerequisites() {
    print_header "Checking Prerequisites"
    
    print_section "System Requirements"
    
    # Check macOS
    if [[ "$OSTYPE" != "darwin"* ]]; then
        print_error "This script requires macOS"
        return 1
    fi
    
    local macos_version=$(sw_vers -productVersion)
    print_info "macOS version: ${macos_version}"
    print_success "Running on macOS"
    
    # Check bash version
    print_section "Bash Version"
    local bash_version=${BASH_VERSION%.*}
    print_info "Bash version: ${bash_version}"
    
    if [[ ${bash_version%.*} -lt 4 ]]; then
        print_warning "Bash 4.0+ recommended (you have ${bash_version})"
    else
        print_success "Bash version compatible"
    fi
    
    # Check script dependencies
    print_section "Script Files"
    
    local required_scripts=(
        "install-korean-fonts.sh:Font Installation"
        "apply-ghostty-config.sh:Ghostty Configuration"
        "verify-setup.sh:Setup Verification"
    )
    
    for script_spec in "${required_scripts[@]}"; do
        IFS=':' read -r script desc <<< "$script_spec"
        if [[ -f "${SCRIPT_DIR}/${script}" ]]; then
            print_success "Found: ${script} (${desc})"
        else
            print_error "Missing: ${script}"
            return 1
        fi
    done
    
    echo ""
    print_success "All prerequisites met"
    return 0
}

################################################################################
# Setup Execution
################################################################################

run_all_steps() {
    print_header "MOAI Complete Setup"
    
    print_info "This script will run all setup steps in sequence"
    print_info "Total estimated time: 5-10 minutes"
    echo ""
    
    if ! confirm "Continue with installation?"; then
        print_warning "Installation cancelled"
        exit 0
    fi
    
    # Count steps
    STEP_COUNT=3
    STEP_CURRENT=0
    
    echo ""
    
    # Step 1: Install fonts
    if ! run_script "install-korean-fonts.sh" "Korean Font Installation"; then
        print_error "Font installation failed"
        if ! confirm "Continue with Ghostty configuration anyway?"; then
            print_error "Setup cancelled"
            return 1
        fi
    fi
    
    echo ""
    sleep 1
    
    # Step 2: Apply Ghostty config
    if ! run_script "apply-ghostty-config.sh" "Ghostty Configuration"; then
        print_error "Ghostty configuration failed"
        if ! confirm "Continue with verification anyway?"; then
            print_error "Setup cancelled"
            return 1
        fi
    fi
    
    echo ""
    sleep 1
    
    # Step 3: Verify setup
    if ! run_script "verify-setup.sh" "Setup Verification"; then
        print_warning "Verification found issues"
        print_info "Review the verification report above for details"
    fi
    
    return 0
}

################################################################################
# Summary Report
################################################################################

print_summary() {
    local elapsed=$(get_elapsed)
    
    print_header "Setup Complete"
    
    echo -e "${GREEN}Installation finished in ${elapsed}${NC}"
    echo ""
    
    print_section "Log Files"
    echo "Master log: ${MASTER_LOG}"
    echo "Script logs:"
    echo "  • install-korean-fonts.log"
    echo "  • apply-ghostty-config.log"
    echo "  • verify-setup.log"
    echo ""
    
    print_section "Configuration Files"
    if [[ -f ~/.config/ghostty/config ]]; then
        echo "Ghostty config: ~/.config/ghostty/config"
    fi
    
    if [[ -d ~/Library/Fonts ]]; then
        local korean_fonts=$(ls ~/Library/Fonts | grep -i noto | wc -l)
        echo "Korean fonts installed: $korean_fonts"
    fi
    echo ""
    
    print_section "Next Steps"
    echo "1. Restart Ghostty if it's currently running"
    echo "2. Open Ghostty and verify Korean text displays correctly"
    echo "3. Customize font size and colors as needed"
    echo "4. Test with: echo '안녕하세요'"
    echo ""
    
    print_section "Troubleshooting"
    echo "• Review logs: cat ${MASTER_LOG}"
    echo "• Check fonts: ls ~/Library/Fonts | grep -i noto"
    echo "• Verify config: cat ~/.config/ghostty/config"
    echo "• Run verification: ./verify-setup.sh"
    echo ""
    
    print_info "Setup documentation: README.md"
    print_info "Quick reference: QUICK-START.md"
    echo ""
}

################################################################################
# Error Handling & Cleanup
################################################################################

cleanup() {
    log "INFO" "Setup script completed"
}

show_help() {
    cat << 'EOF'
MOAI Complete Setup Script

Usage: ./setup-all.sh [OPTIONS]

Options:
  -h, --help          Show this help message
  -q, --quiet         Minimal output (logging only)
  -v, --verbose       Verbose output with detailed messages
  -l, --logs          Show log directory
  --no-verify         Skip verification step
  --dry-run          Show what would be done without running

Examples:
  ./setup-all.sh              Run complete setup interactively
  ./setup-all.sh --quiet      Run with minimal output
  ./setup-all.sh --help       Show this help message

EOF
}

################################################################################
# Main Execution
################################################################################

main() {
    # Initialize logging
    mkdir -p "${LOG_DIR}"
    
    log "INFO" "Starting MOAI complete setup"
    log "INFO" "Scripts directory: ${SCRIPT_DIR}"
    log "INFO" "Time: $(date)"
    
    print_header "MOAI Korean Font & Ghostty Setup"
    
    # Check prerequisites
    if ! check_prerequisites; then
        print_error "Prerequisites check failed"
        print_info "Please ensure all scripts are in: ${SCRIPT_DIR}"
        exit 1
    fi
    
    # Run all steps
    if ! run_all_steps; then
        print_error "Setup encountered errors"
        print_info "Check logs for details: ${MASTER_LOG}"
        exit 1
    fi
    
    # Print summary
    print_summary
    
    cleanup
    exit 0
}

# Error handling
trap 'print_error "Script interrupted"; exit 1' INT TERM
trap 'print_error "An error occurred on line $LINENO"; exit 1' ERR

# Handle command line arguments
case "${1:-}" in
    -h|--help)
        show_help
        exit 0
        ;;
    -l|--logs)
        echo "Log directory: ${LOG_DIR}"
        ls -lah "${LOG_DIR}" 2>/dev/null || echo "No logs yet"
        exit 0
        ;;
    *)
        main
        ;;
esac
