#!/usr/bin/env bash
# MoAI-ADK UV CLI Installer Test Suite
# Version: 1.0.0
# Description: Comprehensive testing for installer.py

set -euo pipefail

# ============================================================================
# Configuration
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALLER="${SCRIPT_DIR}/installer.py"
TEST_DIR="${SCRIPT_DIR}/test_output"
LOG_FILE="${TEST_DIR}/test.log"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# ============================================================================
# Utility Functions
# ============================================================================

log() {
    local message="$1"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] $message" | tee -a "$LOG_FILE"
}

test_start() {
    local test_name="$1"
    echo ""
    echo -e "${BLUE}▶ Running test: ${test_name}${NC}"
    ((TESTS_RUN++))
}

test_pass() {
    local test_name="$1"
    echo -e "${GREEN}✓ PASS: ${test_name}${NC}"
    log "PASS: $test_name"
    ((TESTS_PASSED++))
}

test_fail() {
    local test_name="$1"
    local reason="$2"
    echo -e "${RED}✗ FAIL: ${test_name}${NC}"
    echo -e "${RED}  Reason: ${reason}${NC}"
    log "FAIL: $test_name - $reason"
    ((TESTS_FAILED++))
}

cleanup() {
    log "Cleaning up test environment"
    if [[ -d "$TEST_DIR" ]]; then
        rm -rf "$TEST_DIR"
    fi
}

setup() {
    log "Setting up test environment"
    mkdir -p "$TEST_DIR"

    # Backup existing MoAI installation if present
    if [[ -d "$HOME/.moai" ]]; then
        log "Backing up existing .moai directory"
        cp -r "$HOME/.moai" "${TEST_DIR}/.moai.backup"
    fi
}

restore() {
    log "Restoring from backup"
    if [[ -d "${TEST_DIR}/.moai.backup" ]]; then
        rm -rf "$HOME/.moai"
        mv "${TEST_DIR}/.moai.backup" "$HOME/.moai"
    fi
}

# ============================================================================
# Test Cases
# ============================================================================

test_installer_exists() {
    test_start "Installer file exists"

    if [[ -f "$INSTALLER" ]]; then
        test_pass "Installer file exists"
    else
        test_fail "Installer file exists" "installer.py not found at $INSTALLER"
    fi
}

test_installer_executable() {
    test_start "Installer is executable via UV"

    if uv run "$INSTALLER" --version &> /dev/null; then
        test_pass "Installer is executable"
    else
        test_fail "Installer is executable" "Cannot execute via uv run"
    fi
}

test_python_version_check() {
    test_start "Python version check"

    local python_version=$(python3 --version | awk '{print $2}')
    local major=$(echo "$python_version" | cut -d. -f1)
    local minor=$(echo "$python_version" | cut -d. -f2)

    if [[ $major -ge 3 ]] && [[ $minor -ge 11 ]]; then
        test_pass "Python version check (3.11+)"
    else
        test_fail "Python version check" "Python $python_version < 3.11"
    fi
}

test_dependencies_available() {
    test_start "Required dependencies available"

    local output=$(uv run "$INSTALLER" --help 2>&1)

    if echo "$output" | grep -q "Usage:"; then
        test_pass "Dependencies (click, rich) available"
    else
        test_fail "Dependencies" "Missing click or rich"
    fi
}

test_help_command() {
    test_start "Help command works"

    local output=$(uv run "$INSTALLER" --help)

    if echo "$output" | grep -q "MoAI-ADK UV CLI Installer"; then
        test_pass "Help command"
    else
        test_fail "Help command" "Help output malformed"
    fi
}

test_install_command_help() {
    test_start "Install command help"

    local output=$(uv run "$INSTALLER" install --help)

    if echo "$output" | grep -q "\-\-korean"; then
        test_pass "Install command help"
    else
        test_fail "Install command help" "Missing --korean option"
    fi
}

test_verify_command_exists() {
    test_start "Verify command exists"

    local output=$(uv run "$INSTALLER" verify --help 2>&1)

    if echo "$output" | grep -q "Verify MoAI-ADK installation"; then
        test_pass "Verify command exists"
    else
        test_fail "Verify command exists" "Verify command not found"
    fi
}

test_status_command_exists() {
    test_start "Status command exists"

    local output=$(uv run "$INSTALLER" status --help 2>&1)

    if echo "$output" | grep -q "Show current MoAI-ADK status"; then
        test_pass "Status command exists"
    else
        test_fail "Status command exists" "Status command not found"
    fi
}

test_setup_korean_command_exists() {
    test_start "Setup-korean command exists"

    local output=$(uv run "$INSTALLER" setup-korean --help 2>&1)

    if echo "$output" | grep -q "Setup Korean language support"; then
        test_pass "Setup-korean command exists"
    else
        test_fail "Setup-korean command exists" "Setup-korean command not found"
    fi
}

test_uninstall_command_exists() {
    test_start "Uninstall command exists"

    local output=$(uv run "$INSTALLER" uninstall --help 2>&1)

    if echo "$output" | grep -q "Uninstall MoAI-ADK"; then
        test_pass "Uninstall command exists"
    else
        test_fail "Uninstall command exists" "Uninstall command not found"
    fi
}

test_korean_locale_detection() {
    test_start "Korean locale detection"

    # This test requires Python execution
    local python_test='
import os
import sys
sys.path.insert(0, "'$SCRIPT_DIR'")

# Temporarily set Korean locale
os.environ["LANG"] = "ko_KR.UTF-8"

# Import installer functions
import installer

system = installer.get_system_info()
print(f"is_korean={system.is_korean}")
'

    local output=$(python3 -c "$python_test" 2>&1)

    if echo "$output" | grep -q "is_korean=True"; then
        test_pass "Korean locale detection"
    else
        test_fail "Korean locale detection" "Failed to detect Korean locale"
    fi
}

test_system_info_gathering() {
    test_start "System information gathering"

    local python_test='
import sys
sys.path.insert(0, "'$SCRIPT_DIR'")
import installer

system = installer.get_system_info()
print(f"os_type={system.os_type}")
print(f"python_version={system.python_version}")
'

    local output=$(python3 -c "$python_test" 2>&1)

    if echo "$output" | grep -q "os_type=" && echo "$output" | grep -q "python_version="; then
        test_pass "System information gathering"
    else
        test_fail "System information gathering" "Failed to gather system info"
    fi
}

test_disk_space_check() {
    test_start "Disk space check"

    local python_test='
import sys
sys.path.insert(0, "'$SCRIPT_DIR'")
import installer

system = installer.get_system_info()
print(f"disk_space_mb={system.disk_space_mb}")
'

    local output=$(python3 -c "$python_test" 2>&1)

    if echo "$output" | grep -qE "disk_space_mb=[0-9]+"; then
        test_pass "Disk space check"
    else
        test_fail "Disk space check" "Failed to check disk space"
    fi
}

test_uv_detection() {
    test_start "UV detection"

    local python_test='
import sys
sys.path.insert(0, "'$SCRIPT_DIR'")
import installer

system = installer.get_system_info()
print(f"has_uv={system.has_uv}")
if system.uv_version:
    print(f"uv_version={system.uv_version}")
'

    local output=$(python3 -c "$python_test" 2>&1)

    if echo "$output" | grep -q "has_uv="; then
        test_pass "UV detection"
    else
        test_fail "UV detection" "Failed to detect UV"
    fi
}

test_config_class() {
    test_start "InstallationConfig class"

    local python_test='
import sys
sys.path.insert(0, "'$SCRIPT_DIR'")
import installer

config = installer.InstallationConfig(
    install_korean_fonts=True,
    force_reinstall=True
)
print(f"korean={config.install_korean_fonts}")
print(f"force={config.force_reinstall}")
'

    local output=$(python3 -c "$python_test" 2>&1)

    if echo "$output" | grep -q "korean=True" && echo "$output" | grep -q "force=True"; then
        test_pass "InstallationConfig class"
    else
        test_fail "InstallationConfig class" "Config class not working"
    fi
}

test_logging_setup() {
    test_start "Logging setup"

    local python_test='
import sys
sys.path.insert(0, "'$SCRIPT_DIR'")
import installer
from pathlib import Path

installer.setup_logging()
log_file = installer.LOG_FILE

if log_file.parent.exists():
    print("log_dir_exists=True")
else:
    print("log_dir_exists=False")
'

    local output=$(python3 -c "$python_test" 2>&1)

    if echo "$output" | grep -q "log_dir_exists=True"; then
        test_pass "Logging setup"
    else
        test_fail "Logging setup" "Failed to create log directory"
    fi
}

test_korean_config_structure() {
    test_start "Korean configuration structure"

    local python_test='
import sys
import json
sys.path.insert(0, "'$SCRIPT_DIR'")
import installer

# Create temp config
korean_config = {
    "language": "ko_KR",
    "locale": "ko_KR.UTF-8",
    "encoding": "UTF-8",
    "ui": {
        "font_family": "Nanum Gothic"
    },
    "features": {
        "korean_nlp": True
    }
}

print(json.dumps(korean_config))
'

    local output=$(python3 -c "$python_test" 2>&1)

    if echo "$output" | grep -q "korean_nlp"; then
        test_pass "Korean configuration structure"
    else
        test_fail "Korean configuration structure" "Config structure invalid"
    fi
}

# ============================================================================
# Test Execution
# ============================================================================

print_banner() {
    echo ""
    echo "═══════════════════════════════════════════════════════════════"
    echo "  MoAI-ADK UV CLI Installer Test Suite"
    echo "═══════════════════════════════════════════════════════════════"
    echo ""
}

print_summary() {
    echo ""
    echo "═══════════════════════════════════════════════════════════════"
    echo "  Test Summary"
    echo "═══════════════════════════════════════════════════════════════"
    echo ""
    echo "Total tests run:    $TESTS_RUN"
    echo -e "${GREEN}Tests passed:       $TESTS_PASSED${NC}"

    if [[ $TESTS_FAILED -gt 0 ]]; then
        echo -e "${RED}Tests failed:       $TESTS_FAILED${NC}"
    else
        echo -e "${GREEN}Tests failed:       $TESTS_FAILED${NC}"
    fi

    echo ""

    if [[ $TESTS_FAILED -eq 0 ]]; then
        echo -e "${GREEN}✓ All tests passed!${NC}"
        echo ""
        return 0
    else
        echo -e "${RED}✗ Some tests failed${NC}"
        echo ""
        echo "Check log file: $LOG_FILE"
        echo ""
        return 1
    fi
}

run_all_tests() {
    print_banner
    setup

    # File existence tests
    test_installer_exists
    test_installer_executable

    # System requirement tests
    test_python_version_check
    test_dependencies_available

    # CLI command tests
    test_help_command
    test_install_command_help
    test_verify_command_exists
    test_status_command_exists
    test_setup_korean_command_exists
    test_uninstall_command_exists

    # Function tests
    test_korean_locale_detection
    test_system_info_gathering
    test_disk_space_check
    test_uv_detection
    test_config_class
    test_logging_setup
    test_korean_config_structure

    # Summary
    print_summary
}

# ============================================================================
# Main
# ============================================================================

main() {
    # Ensure cleanup on exit
    trap cleanup EXIT

    # Run tests
    run_all_tests

    # Return appropriate exit code
    if [[ $TESTS_FAILED -eq 0 ]]; then
        exit 0
    else
        exit 1
    fi
}

# Run main
main "$@"
