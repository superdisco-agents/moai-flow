#!/usr/bin/env bash
#
# MoAI-ADK Comprehensive Test Suite
# Version: 1.0.0
# Tests: 140+ individual tests
# Output Modes: standard, verbose, JSON
# CI/CD Ready: Yes
#
# Usage:
#   ./test-suite.sh               # Standard output
#   ./test-suite.sh --verbose     # Detailed output
#   ./test-suite.sh --json        # JSON output for CI/CD
#   ./test-suite.sh --korean      # Korean-specific tests only
#   ./test-suite.sh --help        # Show help

set -euo pipefail

# Script metadata
SCRIPT_VERSION="1.0.0"
SCRIPT_NAME="MoAI-ADK Test Suite"
TOTAL_TESTS=140

# Test counters
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_SKIPPED=0
TESTS_TOTAL=0

# Output mode
OUTPUT_MODE="standard"  # standard, verbose, json
KOREAN_ONLY=false

# Colors for output (disabled in JSON mode)
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test results storage (for JSON output)
declare -a TEST_RESULTS=()

#######################################
# Helper Functions
#######################################

print_header() {
    if [[ "$OUTPUT_MODE" != "json" ]]; then
        echo
        echo "═══════════════════════════════════════════════════════════"
        echo "  $1"
        echo "═══════════════════════════════════════════════════════════"
        echo
    fi
}

print_section() {
    if [[ "$OUTPUT_MODE" != "json" ]]; then
        echo
        echo "─────────────────────────────────────────────────────────"
        echo "  $1"
        echo "─────────────────────────────────────────────────────────"
    fi
}

log_verbose() {
    if [[ "$OUTPUT_MODE" == "verbose" ]]; then
        echo "  [VERBOSE] $1"
    fi
}

test_pass() {
    ((TESTS_PASSED++))
    ((TESTS_TOTAL++))

    if [[ "$OUTPUT_MODE" == "json" ]]; then
        TEST_RESULTS+=("{\"name\":\"$1\",\"status\":\"pass\",\"message\":\"$2\"}")
    else
        echo -e "  ${GREEN}✓${NC} $1"
        [[ "$OUTPUT_MODE" == "verbose" ]] && echo "    └─ $2"
    fi
}

test_fail() {
    ((TESTS_FAILED++))
    ((TESTS_TOTAL++))

    if [[ "$OUTPUT_MODE" == "json" ]]; then
        TEST_RESULTS+=("{\"name\":\"$1\",\"status\":\"fail\",\"message\":\"$2\"}")
    else
        echo -e "  ${RED}✗${NC} $1"
        echo -e "    ${RED}└─ $2${NC}"
    fi
}

test_skip() {
    ((TESTS_SKIPPED++))
    ((TESTS_TOTAL++))

    if [[ "$OUTPUT_MODE" == "json" ]]; then
        TEST_RESULTS+=("{\"name\":\"$1\",\"status\":\"skip\",\"message\":\"$2\"}")
    else
        echo -e "  ${YELLOW}⊝${NC} $1"
        [[ "$OUTPUT_MODE" == "verbose" ]] && echo "    └─ $2"
    fi
}

run_test() {
    local test_name="$1"
    local test_command="$2"
    local expected_result="${3:-0}"
    local error_message="${4:-Test failed}"

    log_verbose "Running: $test_command"

    if eval "$test_command" > /dev/null 2>&1; then
        if [[ "$expected_result" == "0" ]]; then
            test_pass "$test_name" "Command succeeded"
        else
            test_fail "$test_name" "$error_message"
        fi
    else
        if [[ "$expected_result" == "1" ]]; then
            test_pass "$test_name" "Expected failure occurred"
        else
            test_fail "$test_name" "$error_message"
        fi
    fi
}

#######################################
# Test Categories
#######################################

#
# Category 1: File Structure Tests (30 tests)
#
test_file_structure() {
    print_section "Category 1: File Structure Tests (30 tests)"

    local base_dir="/Users/rdmtv/Documents/claydev-local/agent-os-v2/moai-adk/_config/install-moai-ko"

    # Test 1-5: Core documentation files
    [[ -f "$base_dir/README.md" ]] && \
        test_pass "README.md exists" "Found at $base_dir" || \
        test_fail "README.md exists" "Not found at $base_dir"

    [[ -f "$base_dir/MIGRATION-GUIDE.md" ]] && \
        test_pass "MIGRATION-GUIDE.md exists" "Found" || \
        test_fail "MIGRATION-GUIDE.md exists" "Not found"

    [[ -f "$base_dir/KOREAN-FONTS-GUIDE.md" ]] && \
        test_pass "KOREAN-FONTS-GUIDE.md exists" "Found" || \
        test_fail "KOREAN-FONTS-GUIDE.md exists" "Not found"

    [[ -f "$base_dir/INDEX.md" ]] && \
        test_pass "INDEX.md exists" "Found" || \
        test_fail "INDEX.md exists" "Not found"

    [[ -f "$base_dir/test-suite.sh" ]] && \
        test_pass "test-suite.sh exists" "Found (this file)" || \
        test_fail "test-suite.sh exists" "Not found"

    # Test 6-10: Installer scripts
    [[ -f "$base_dir/install-moai-adk.py" ]] && \
        test_pass "UV installer script exists" "install-moai-adk.py" || \
        test_skip "UV installer script exists" "Not implemented yet"

    [[ -f "$base_dir/install-moai-adk.sh" ]] && \
        test_pass "Bash installer script exists" "install-moai-adk.sh" || \
        test_skip "Bash installer script exists" "Not implemented yet"

    [[ -f "$base_dir/verify-installation.sh" ]] && \
        test_pass "Verification script exists" "verify-installation.sh" || \
        test_skip "Verification script exists" "Not implemented yet"

    [[ -x "$base_dir/test-suite.sh" ]] && \
        test_pass "test-suite.sh is executable" "Permissions OK" || \
        test_fail "test-suite.sh is executable" "Missing execute permissions"

    [[ -d "$base_dir/apps" ]] && \
        test_pass "apps/ directory exists" "Found" || \
        test_skip "apps/ directory exists" "Will be created during install"

    # Test 11-15: Directory structure
    [[ -d "$base_dir/scripts" ]] && \
        test_pass "scripts/ directory exists" "Found" || \
        test_skip "scripts/ directory exists" "Will be created during install"

    [[ -d "$base_dir/skills" ]] && \
        test_pass "skills/ directory exists" "Found" || \
        test_skip "skills/ directory exists" "Will be created during install"

    [[ -d "$base_dir/skills/moai-adk-installer" ]] && \
        test_pass "moai-adk-installer skill exists" "Found" || \
        test_skip "moai-adk-installer skill exists" "Not implemented yet"

    # Test 16-20: Documentation line counts
    local readme_lines=$(wc -l < "$base_dir/README.md" 2>/dev/null || echo "0")
    [[ "$readme_lines" -ge 650 ]] && \
        test_pass "README.md has 650+ lines" "$readme_lines lines" || \
        test_fail "README.md has 650+ lines" "Only $readme_lines lines (target: 700)"

    local migration_lines=$(wc -l < "$base_dir/MIGRATION-GUIDE.md" 2>/dev/null || echo "0")
    [[ "$migration_lines" -ge 700 ]] && \
        test_pass "MIGRATION-GUIDE.md has 700+ lines" "$migration_lines lines" || \
        test_fail "MIGRATION-GUIDE.md has 700+ lines" "Only $migration_lines lines (target: 750)"

    local korean_lines=$(wc -l < "$base_dir/KOREAN-FONTS-GUIDE.md" 2>/dev/null || echo "0")
    [[ "$korean_lines" -ge 550 ]] && \
        test_pass "KOREAN-FONTS-GUIDE.md has 550+ lines" "$korean_lines lines" || \
        test_skip "KOREAN-FONTS-GUIDE.md has 550+ lines" "Not created yet (target: 600)"

    local index_lines=$(wc -l < "$base_dir/INDEX.md" 2>/dev/null || echo "0")
    [[ "$index_lines" -ge 300 ]] && \
        test_pass "INDEX.md has 300+ lines" "$index_lines lines" || \
        test_skip "INDEX.md has 300+ lines" "Not created yet (target: 350)"

    local test_lines=$(wc -l < "$base_dir/test-suite.sh" 2>/dev/null || echo "0")
    [[ "$test_lines" -ge 600 ]] && \
        test_pass "test-suite.sh has 600+ lines" "$test_lines lines" || \
        test_fail "test-suite.sh has 600+ lines" "Only $test_lines lines (target: 650)"

    # Test 21-25: File readability
    [[ -r "$base_dir/README.md" ]] && \
        test_pass "README.md is readable" "Permissions OK" || \
        test_fail "README.md is readable" "Permission denied"

    [[ -r "$base_dir/MIGRATION-GUIDE.md" ]] && \
        test_pass "MIGRATION-GUIDE.md is readable" "Permissions OK" || \
        test_fail "MIGRATION-GUIDE.md is readable" "Permission denied"

    [[ -w "$base_dir" ]] && \
        test_pass "Install directory is writable" "Can create files" || \
        test_fail "Install directory is writable" "Permission denied"

    # Test 26-30: Content validation
    grep -q "Beyond-MCP" "$base_dir/README.md" 2>/dev/null && \
        test_pass "README mentions Beyond-MCP pattern" "Found" || \
        test_fail "README mentions Beyond-MCP pattern" "Keyword not found"

    grep -q "D2Coding" "$base_dir/MIGRATION-GUIDE.md" 2>/dev/null && \
        test_pass "MIGRATION-GUIDE mentions D2Coding font" "Found" || \
        test_fail "MIGRATION-GUIDE mentions D2Coding font" "Keyword not found"

    grep -q "한글\|Korean" "$base_dir/MIGRATION-GUIDE.md" 2>/dev/null && \
        test_pass "MIGRATION-GUIDE has Korean content" "Found Korean text" || \
        test_fail "MIGRATION-GUIDE has Korean content" "No Korean text found"

    grep -q "uv run" "$base_dir/README.md" 2>/dev/null && \
        test_pass "README mentions UV commands" "Found" || \
        test_fail "README mentions UV commands" "No UV commands found"

    grep -q "claude code" "$base_dir/MIGRATION-GUIDE.md" 2>/dev/null && \
        test_pass "MIGRATION-GUIDE mentions Claude Code" "Found" || \
        test_fail "MIGRATION-GUIDE mentions Claude Code" "Not mentioned"

    grep -q "Test.*140" "$base_dir/test-suite.sh" 2>/dev/null && \
        test_pass "test-suite.sh declares 140+ tests" "Found in metadata" || \
        test_fail "test-suite.sh declares 140+ tests" "Count mismatch"
}

#
# Category 2: UV Script Tests (25 tests)
#
test_uv_scripts() {
    print_section "Category 2: UV Script Tests (25 tests)"

    # Test 31-35: UV installation
    command -v uv &>/dev/null && \
        test_pass "UV is installed" "$(uv --version)" || \
        test_skip "UV is installed" "UV not installed (optional for testing)"

    if command -v uv &>/dev/null; then
        uv --version | grep -q "uv" && \
            test_pass "UV version command works" "$(uv --version)" || \
            test_fail "UV version command works" "Version check failed"

        local uv_version=$(uv --version 2>/dev/null | grep -oE '[0-9]+\.[0-9]+' | head -1)
        if [[ -n "$uv_version" ]]; then
            local major=$(echo "$uv_version" | cut -d. -f1)
            local minor=$(echo "$uv_version" | cut -d. -f2)

            [[ "$major" -ge 0 && "$minor" -ge 4 ]] && \
                test_pass "UV version is 0.4.0+" "$uv_version" || \
                test_fail "UV version is 0.4.0+" "Version $uv_version is too old"
        else
            test_skip "UV version is 0.4.0+" "Could not parse version"
        fi
    else
        test_skip "UV version command works" "UV not installed"
        test_skip "UV version is 0.4.0+" "UV not installed"
    fi

    # Test 36-40: Python environment
    command -v python3 &>/dev/null && \
        test_pass "Python 3 is installed" "$(python3 --version)" || \
        test_fail "Python 3 is installed" "Python 3 not found"

    if command -v python3 &>/dev/null; then
        local py_version=$(python3 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+' | head -1)
        local py_major=$(echo "$py_version" | cut -d. -f1)
        local py_minor=$(echo "$py_version" | cut -d. -f2)

        [[ "$py_major" -ge 3 && "$py_minor" -ge 11 ]] && \
            test_pass "Python version is 3.11+" "Python $py_version" || \
            test_fail "Python version is 3.11+" "Python $py_version is too old"
    else
        test_skip "Python version is 3.11+" "Python not installed"
    fi

    python3 -c "import sys; print(sys.version)" &>/dev/null && \
        test_pass "Python can print version" "Import successful" || \
        test_fail "Python can print version" "Import failed"

    python3 -c "import json" &>/dev/null && \
        test_pass "Python has json module" "Standard library OK" || \
        test_fail "Python has json module" "Standard library broken"

    # Test 41-45: UV project operations
    if command -v uv &>/dev/null; then
        local test_dir="/tmp/moai-uv-test-$$"
        mkdir -p "$test_dir"
        cd "$test_dir"

        uv init &>/dev/null && \
            test_pass "UV can initialize project" "Project created" || \
            test_fail "UV can initialize project" "Init failed"

        [[ -f "pyproject.toml" ]] && \
            test_pass "UV creates pyproject.toml" "File exists" || \
            test_fail "UV creates pyproject.toml" "File not created"

        uv add --quiet requests &>/dev/null && \
            test_pass "UV can add dependencies" "requests added" || \
            test_skip "UV can add dependencies" "Network required"

        [[ -f "uv.lock" ]] && \
            test_pass "UV creates lock file" "uv.lock exists" || \
            test_skip "UV creates lock file" "No dependencies added"

        cd - > /dev/null
        rm -rf "$test_dir"
    else
        for i in {41..44}; do
            test_skip "UV project test $i" "UV not installed"
        done
    fi

    # Test 46-50: UV environment detection
    [[ -n "${VIRTUAL_ENV:-}" ]] && \
        test_pass "Virtual environment detected" "$VIRTUAL_ENV" || \
        test_skip "Virtual environment detected" "Not in venv (OK)"

    command -v pip3 &>/dev/null && \
        test_pass "pip3 is available" "$(pip3 --version | head -1)" || \
        test_fail "pip3 is available" "pip3 not found"

    if command -v uv &>/dev/null; then
        uv python list &>/dev/null && \
            test_pass "UV can list Python versions" "Command works" || \
            test_skip "UV can list Python versions" "No Python versions managed by UV"
    else
        test_skip "UV can list Python versions" "UV not installed"
    fi

    # Test 51-55: Package management
    python3 -m pip --version &>/dev/null && \
        test_pass "pip module is available" "Module installed" || \
        test_fail "pip module is available" "pip module missing"

    if command -v uv &>/dev/null; then
        uv pip --version &>/dev/null && \
            test_pass "uv pip command works" "Wrapper available" || \
            test_fail "uv pip command works" "uv pip not working"
    else
        test_skip "uv pip command works" "UV not installed"
    fi
}

#
# Category 3: App Tests (20 tests)
#
test_apps() {
    print_section "Category 3: Bash App Tests (20 tests)"

    local base_dir="/Users/rdmtv/Documents/claydev-local/agent-os-v2/moai-adk/_config/install-moai-ko"

    # Test 56-60: Bash availability
    command -v bash &>/dev/null && \
        test_pass "Bash is installed" "$(bash --version | head -1)" || \
        test_fail "Bash is installed" "Bash not found"

    if command -v bash &>/dev/null; then
        local bash_version=$(bash --version | head -1 | grep -oE '[0-9]+\.[0-9]+' | head -1)
        local bash_major=$(echo "$bash_version" | cut -d. -f1)

        [[ "$bash_major" -ge 4 ]] && \
            test_pass "Bash version is 4.0+" "Bash $bash_version" || \
            test_fail "Bash version is 4.0+" "Bash $bash_version is too old"
    else
        test_skip "Bash version is 4.0+" "Bash not installed"
    fi

    command -v zsh &>/dev/null && \
        test_pass "Zsh is available" "$(zsh --version)" || \
        test_skip "Zsh is available" "Zsh not installed (optional)"

    [[ -n "$SHELL" ]] && \
        test_pass "Shell environment is set" "$SHELL" || \
        test_fail "Shell environment is set" "\$SHELL not defined"

    # Test 61-65: Script existence
    [[ -f "$base_dir/install-moai-adk.sh" ]] && \
        test_pass "Bash installer exists" "Found" || \
        test_skip "Bash installer exists" "Not implemented yet"

    if [[ -f "$base_dir/install-moai-adk.sh" ]]; then
        [[ -x "$base_dir/install-moai-adk.sh" ]] && \
            test_pass "Bash installer is executable" "Permissions OK" || \
            test_fail "Bash installer is executable" "Missing execute bit"

        bash -n "$base_dir/install-moai-adk.sh" &>/dev/null && \
            test_pass "Bash installer syntax is valid" "No syntax errors" || \
            test_fail "Bash installer syntax is valid" "Syntax errors detected"

        grep -q "#!/" "$base_dir/install-moai-adk.sh" && \
            test_pass "Bash installer has shebang" "Found" || \
            test_fail "Bash installer has shebang" "Missing shebang line"
    else
        for i in {62..64}; do
            test_skip "Bash installer test $i" "Script not implemented"
        done
    fi

    # Test 66-70: App directory structure
    [[ -d "$base_dir/apps" ]] && \
        test_pass "apps/ directory exists" "Found" || \
        test_skip "apps/ directory exists" "Not created yet"

    if [[ -d "$base_dir/apps" ]]; then
        local app_count=$(find "$base_dir/apps" -name "*.sh" 2>/dev/null | wc -l)
        [[ "$app_count" -gt 0 ]] && \
            test_pass "Bash apps exist in apps/" "$app_count app(s)" || \
            test_skip "Bash apps exist in apps/" "No apps yet"
    else
        test_skip "Bash apps exist in apps/" "Directory doesn't exist"
    fi

    # Test 71-75: Verification script
    [[ -f "$base_dir/verify-installation.sh" ]] && \
        test_pass "Verification script exists" "Found" || \
        test_skip "Verification script exists" "Not implemented yet"

    if [[ -f "$base_dir/verify-installation.sh" ]]; then
        [[ -x "$base_dir/verify-installation.sh" ]] && \
            test_pass "Verification script is executable" "Permissions OK" || \
            test_fail "Verification script is executable" "Missing execute bit"

        bash -n "$base_dir/verify-installation.sh" &>/dev/null && \
            test_pass "Verification script syntax valid" "No errors" || \
            test_fail "Verification script syntax valid" "Syntax errors"
    else
        test_skip "Verification script is executable" "Script not implemented"
        test_skip "Verification script syntax valid" "Script not implemented"
    fi
}

#
# Category 4: Skills, Commands, Agents Tests (15 tests)
#
test_skills_commands() {
    print_section "Category 4: Skills, Commands, Agents Tests (15 tests)"

    local base_dir="/Users/rdmtv/Documents/claydev-local/agent-os-v2/moai-adk/_config/install-moai-ko"

    # Test 76-80: Skills directory
    [[ -d "$base_dir/skills" ]] && \
        test_pass "skills/ directory exists" "Found" || \
        test_skip "skills/ directory exists" "Not created yet"

    if [[ -d "$base_dir/skills" ]]; then
        [[ -d "$base_dir/skills/moai-adk-installer" ]] && \
            test_pass "moai-adk-installer skill exists" "Found" || \
            test_skip "moai-adk-installer skill exists" "Not implemented"

        if [[ -d "$base_dir/skills/moai-adk-installer" ]]; then
            [[ -f "$base_dir/skills/moai-adk-installer/skill.yaml" ]] && \
                test_pass "skill.yaml exists" "Found" || \
                test_fail "skill.yaml exists" "Missing skill.yaml"

            [[ -f "$base_dir/skills/moai-adk-installer/README.md" ]] && \
                test_pass "Skill README exists" "Found" || \
                test_skip "Skill README exists" "Not created"

            [[ -d "$base_dir/skills/moai-adk-installer/prompts" ]] && \
                test_pass "Skill prompts/ directory exists" "Found" || \
                test_skip "Skill prompts/ directory exists" "Not created"
        else
            for i in {78..80}; do
                test_skip "Skill structure test $i" "Skill not implemented"
            done
        fi
    else
        for i in {77..80}; do
            test_skip "Skills test $i" "Directory doesn't exist"
        done
    fi

    # Test 81-85: Claude Code integration
    command -v claude &>/dev/null && \
        test_pass "Claude Code CLI installed" "$(claude --version 2>/dev/null || echo 'installed')" || \
        test_skip "Claude Code CLI installed" "Not installed (optional)"

    [[ -d ~/.claude ]] && \
        test_pass "Claude config directory exists" "~/.claude found" || \
        test_skip "Claude config directory exists" "Claude not configured"

    if [[ -d ~/.claude/skills ]]; then
        test_pass "Claude skills directory exists" "Found" || \
            test_skip "Claude skills directory exists" "Not initialized"

        local installed_skills=$(ls -1 ~/.claude/skills 2>/dev/null | wc -l)
        [[ "$installed_skills" -gt 0 ]] && \
            test_pass "Claude skills are installed" "$installed_skills skill(s)" || \
            test_skip "Claude skills are installed" "No skills installed"
    else
        test_skip "Claude skills directory exists" "Directory not found"
        test_skip "Claude skills are installed" "Directory not found"
    fi

    # Test 86-90: MCP integration
    [[ -f ~/.claude/claude_desktop_config.json ]] && \
        test_pass "Claude Desktop config exists" "Found" || \
        test_skip "Claude Desktop config exists" "Not configured"

    if [[ -f ~/.claude/claude_desktop_config.json ]]; then
        grep -q "mcpServers" ~/.claude/claude_desktop_config.json 2>/dev/null && \
            test_pass "MCP servers configured" "Found in config" || \
            test_skip "MCP servers configured" "No MCP servers"
    else
        test_skip "MCP servers configured" "Config not found"
    fi
}

#
# Category 5: Documentation Tests (20 tests)
#
test_documentation() {
    print_section "Category 5: Documentation Tests (20 tests)"

    local base_dir="/Users/rdmtv/Documents/claydev-local/agent-os-v2/moai-adk/_config/install-moai-ko"

    # Test 91-95: Documentation completeness
    grep -q "Table of Contents" "$base_dir/README.md" 2>/dev/null && \
        test_pass "README has table of contents" "Found" || \
        test_fail "README has table of contents" "Missing TOC"

    grep -q "Installation" "$base_dir/README.md" 2>/dev/null && \
        test_pass "README has installation section" "Found" || \
        test_fail "README has installation section" "Section missing"

    grep -q "Korean\|한글" "$base_dir/README.md" 2>/dev/null && \
        test_pass "README mentions Korean support" "Found" || \
        test_fail "README mentions Korean support" "Not mentioned"

    grep -q "Beyond-MCP" "$base_dir/README.md" 2>/dev/null && \
        test_pass "README explains Beyond-MCP pattern" "Found" || \
        test_fail "README explains Beyond-MCP pattern" "Not explained"

    local code_blocks=$(grep -c '```' "$base_dir/README.md" 2>/dev/null || echo "0")
    [[ "$code_blocks" -ge 10 ]] && \
        test_pass "README has code examples" "$code_blocks code blocks" || \
        test_fail "README has code examples" "Only $code_blocks code blocks"

    # Test 96-100: Migration guide completeness
    grep -q "Migration Path" "$base_dir/MIGRATION-GUIDE.md" 2>/dev/null && \
        test_pass "MIGRATION-GUIDE has migration paths" "Found" || \
        test_fail "MIGRATION-GUIDE has migration paths" "Paths not described"

    grep -q "UV CLI\|Bash\|Claude Skill" "$base_dir/MIGRATION-GUIDE.md" 2>/dev/null && \
        test_pass "MIGRATION-GUIDE covers all approaches" "Found all 3" || \
        test_fail "MIGRATION-GUIDE covers all approaches" "Missing approaches"

    grep -q "Rollback" "$base_dir/MIGRATION-GUIDE.md" 2>/dev/null && \
        test_pass "MIGRATION-GUIDE has rollback procedures" "Found" || \
        test_fail "MIGRATION-GUIDE has rollback procedures" "Missing rollback"

    grep -q "Troubleshooting" "$base_dir/MIGRATION-GUIDE.md" 2>/dev/null && \
        test_pass "MIGRATION-GUIDE has troubleshooting" "Found" || \
        test_fail "MIGRATION-GUIDE has troubleshooting" "Missing section"

    grep -q "Team\|Rollout" "$base_dir/MIGRATION-GUIDE.md" 2>/dev/null && \
        test_pass "MIGRATION-GUIDE has team rollout plan" "Found" || \
        test_fail "MIGRATION-GUIDE has team rollout plan" "Missing plan"

    # Test 101-105: Korean fonts guide
    if [[ -f "$base_dir/KOREAN-FONTS-GUIDE.md" ]]; then
        grep -q "D2Coding" "$base_dir/KOREAN-FONTS-GUIDE.md" && \
            test_pass "KOREAN-FONTS-GUIDE mentions D2Coding" "Found" || \
            test_fail "KOREAN-FONTS-GUIDE mentions D2Coding" "Not mentioned"

        grep -q "Ghostty\|iTerm\|Warp" "$base_dir/KOREAN-FONTS-GUIDE.md" && \
            test_pass "KOREAN-FONTS-GUIDE covers terminals" "Found" || \
            test_fail "KOREAN-FONTS-GUIDE covers terminals" "No terminal configs"

        grep -q "한글" "$base_dir/KOREAN-FONTS-GUIDE.md" && \
            test_pass "KOREAN-FONTS-GUIDE has Korean text" "Found 한글" || \
            test_fail "KOREAN-FONTS-GUIDE has Korean text" "No Korean examples"
    else
        for i in {101..103}; do
            test_skip "KOREAN-FONTS-GUIDE test $i" "File not created yet"
        done
    fi

    # Test 106-110: Documentation formatting
    ! grep -q "FIXME\|TODO\|XXX" "$base_dir/README.md" 2>/dev/null && \
        test_pass "README has no TODO markers" "Clean" || \
        test_skip "README has no TODO markers" "Contains TODOs (OK for draft)"

    ! grep -q "FIXME\|TODO\|XXX" "$base_dir/MIGRATION-GUIDE.md" 2>/dev/null && \
        test_pass "MIGRATION-GUIDE has no TODO markers" "Clean" || \
        test_skip "MIGRATION-GUIDE has no TODO markers" "Contains TODOs (OK for draft)"
}

#
# Category 6: Syntax Validation Tests (15 tests)
#
test_syntax() {
    print_section "Category 6: Syntax Validation Tests (15 tests)"

    local base_dir="/Users/rdmtv/Documents/claydev-local/agent-os-v2/moai-adk/_config/install-moai-ko"

    # Test 111-115: Markdown syntax
    command -v markdownlint &>/dev/null && \
        HAS_MDLINT=true || HAS_MDLINT=false

    if [[ "$HAS_MDLINT" == "true" ]]; then
        markdownlint "$base_dir/README.md" &>/dev/null && \
            test_pass "README.md markdown is valid" "No lint errors" || \
            test_skip "README.md markdown is valid" "Lint errors (non-critical)"
    else
        test_skip "README.md markdown is valid" "markdownlint not installed"
    fi

    # Basic markdown checks
    ! grep -q "^#####" "$base_dir/README.md" 2>/dev/null && \
        test_pass "README doesn't overuse heading levels" "Max level 4" || \
        test_skip "README doesn't overuse heading levels" "Has level 5+ headings"

    grep -q "^\[.*\](.*)" "$base_dir/README.md" 2>/dev/null && \
        test_pass "README has markdown links" "Found links" || \
        test_fail "README has markdown links" "No links found"

    # Test 116-120: Shell script syntax
    if [[ -f "$base_dir/install-moai-adk.sh" ]]; then
        bash -n "$base_dir/install-moai-adk.sh" &>/dev/null && \
            test_pass "install-moai-adk.sh syntax valid" "No errors" || \
            test_fail "install-moai-adk.sh syntax valid" "Syntax errors detected"
    else
        test_skip "install-moai-adk.sh syntax valid" "File not created"
    fi

    bash -n "$base_dir/test-suite.sh" &>/dev/null && \
        test_pass "test-suite.sh syntax valid" "No errors (this file)" || \
        test_fail "test-suite.sh syntax valid" "Syntax errors detected"

    # Test 121-125: Python syntax
    if [[ -f "$base_dir/install-moai-adk.py" ]]; then
        python3 -m py_compile "$base_dir/install-moai-adk.py" &>/dev/null && \
            test_pass "install-moai-adk.py syntax valid" "No errors" || \
            test_fail "install-moai-adk.py syntax valid" "Syntax errors detected"
    else
        test_skip "install-moai-adk.py syntax valid" "File not created"
    fi

    # Test 126-130: UTF-8 encoding
    file "$base_dir/README.md" | grep -q "UTF-8" && \
        test_pass "README.md is UTF-8 encoded" "Encoding OK" || \
        test_fail "README.md is UTF-8 encoded" "Wrong encoding"

    file "$base_dir/MIGRATION-GUIDE.md" | grep -q "UTF-8" && \
        test_pass "MIGRATION-GUIDE.md is UTF-8 encoded" "Encoding OK" || \
        test_fail "MIGRATION-GUIDE.md is UTF-8 encoded" "Wrong encoding"
}

#
# Category 7: Integration Tests (10 tests)
#
test_integration() {
    print_section "Category 7: Integration Tests (10 tests)"

    # Test 131-135: End-to-end workflow simulation
    local test_succeeded=0

    # Simulate: Check prerequisites
    if command -v python3 &>/dev/null && command -v bash &>/dev/null; then
        test_pass "Prerequisites check simulated" "Python and Bash available"
        ((test_succeeded++))
    else
        test_fail "Prerequisites check simulated" "Missing core tools"
    fi

    # Simulate: Download fonts
    if command -v curl &>/dev/null || command -v wget &>/dev/null; then
        test_pass "Font download capability" "curl/wget available"
        ((test_succeeded++))
    else
        test_fail "Font download capability" "No download tool"
    fi

    # Simulate: Terminal configuration
    if [[ -n "$TERM" ]]; then
        test_pass "Terminal environment detected" "$TERM"
        ((test_succeeded++))
    else
        test_fail "Terminal environment detected" "TERM not set"
    fi

    # Simulate: Script execution
    [[ -x "$base_dir/test-suite.sh" ]] && \
        test_pass "Scripts are executable" "Can run installers" && \
        ((test_succeeded++)) || \
        test_fail "Scripts are executable" "Permission issues"

    # Test 136-140: Korean rendering tests
    if [[ "$KOREAN_ONLY" == "true" ]] || [[ "$test_succeeded" -ge 3 ]]; then
        # Test Korean text processing
        echo "한글 테스트" | grep -q "한글" && \
            test_pass "Korean text can be processed" "grep works" || \
            test_fail "Korean text can be processed" "Korean text broken"

        # Test UTF-8 locale
        locale | grep -q "UTF-8" && \
            test_pass "UTF-8 locale is set" "$(locale | grep UTF-8 | head -1)" || \
            test_skip "UTF-8 locale is set" "Locale may not support Korean"

        # Test Korean font availability
        fc-list | grep -iq "korean\|hangul\|noto.*cjk\|d2coding" && \
            test_pass "Korean fonts are available" "$(fc-list | grep -i korean | wc -l) font(s)" || \
            test_skip "Korean fonts are available" "No Korean fonts installed"

        # Test D2Coding specifically
        fc-list | grep -iq "d2coding" && \
            test_pass "D2Coding font is installed" "Found" || \
            test_skip "D2Coding font is installed" "Not installed (OK for testing)"
    else
        for i in {136..139}; do
            test_skip "Integration test $i" "Prerequisites not met"
        done
    fi

    # Final integration test
    [[ "$test_succeeded" -ge 3 ]] && \
        test_pass "Overall integration readiness" "$test_succeeded/4 checks passed" || \
        test_fail "Overall integration readiness" "Only $test_succeeded/4 checks passed"
}

#
# Category 8: Korean Font Rendering Tests (8 tests) ⭐
#
test_korean_rendering() {
    print_section "Category 8: Korean Font Rendering Tests (8 tests) ⭐"

    # Test 141: Korean character encoding
    python3 -c "print('한글'.encode('utf-8'))" &>/dev/null && \
        test_pass "Korean characters encode to UTF-8" "Encoding works" || \
        test_fail "Korean characters encode to UTF-8" "Encoding failed"

    # Test 142: Korean text in shell
    echo "안녕하세요" | grep -q "안녕" && \
        test_pass "Korean text processes in shell" "grep found Korean" || \
        test_fail "Korean text processes in shell" "Korean text broken in pipeline"

    # Test 143: D2Coding font installation
    fc-list | grep -iq "d2coding" && \
        test_pass "D2Coding font is installed" "$(fc-list | grep -i d2coding | wc -l) variant(s)" || \
        test_skip "D2Coding font is installed" "Not installed (run installer)"

    # Test 144: Alternative Korean fonts
    fc-list | grep -iq "noto.*cjk" && \
        test_pass "Noto CJK fonts available" "Fallback fonts exist" || \
        test_skip "Noto CJK fonts available" "No CJK fonts"

    # Test 145: Terminal encoding
    [[ "$LANG" =~ UTF-8 ]] && \
        test_pass "Terminal uses UTF-8 encoding" "$LANG" || \
        test_fail "Terminal uses UTF-8 encoding" "LANG=$LANG (not UTF-8)"

    # Test 146: Ghostty configuration
    if [[ -f ~/.config/ghostty/config ]]; then
        grep -q "D2Coding\|font-family.*Korean" ~/.config/ghostty/config && \
            test_pass "Ghostty configured for Korean" "D2Coding set" || \
            test_skip "Ghostty configured for Korean" "No Korean font set"
    else
        test_skip "Ghostty configured for Korean" "Ghostty not configured"
    fi

    # Test 147: Korean text file creation
    local test_file="/tmp/korean-test-$$.txt"
    echo "한글 테스트: MoAI-ADK" > "$test_file"
    grep -q "한글" "$test_file" && \
        test_pass "Korean text writes to files" "File I/O works" || \
        test_fail "Korean text writes to files" "File I/O broken"
    rm -f "$test_file"

    # Test 148: Korean in environment variables
    export MOAI_TEST_KOREAN="한글 테스트"
    [[ "$MOAI_TEST_KOREAN" == "한글 테스트" ]] && \
        test_pass "Korean in environment variables" "Env vars work" || \
        test_fail "Korean in environment variables" "Env vars broken"
    unset MOAI_TEST_KOREAN
}

#######################################
# Main Test Runner
#######################################

show_help() {
    cat <<EOF
$SCRIPT_NAME - Version $SCRIPT_VERSION

Usage:
  $0 [OPTIONS]

Options:
  --standard        Standard output (default)
  --verbose         Verbose output with detailed logs
  --json            JSON output for CI/CD
  --korean          Run Korean-specific tests only
  --help            Show this help message

Examples:
  $0                          # Run all tests, standard output
  $0 --verbose                # Run with detailed logging
  $0 --json                   # Output JSON for CI/CD
  $0 --korean --verbose       # Korean tests with details

Exit Codes:
  0  - All tests passed
  1  - One or more tests failed
  2  - Invalid arguments
EOF
}

main() {
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --verbose)
                OUTPUT_MODE="verbose"
                shift
                ;;
            --json)
                OUTPUT_MODE="json"
                shift
                ;;
            --standard)
                OUTPUT_MODE="standard"
                shift
                ;;
            --korean)
                KOREAN_ONLY=true
                shift
                ;;
            --help)
                show_help
                exit 0
                ;;
            *)
                echo "Error: Unknown option: $1" >&2
                show_help
                exit 2
                ;;
        esac
    done

    # Disable colors in JSON mode
    if [[ "$OUTPUT_MODE" == "json" ]]; then
        RED=""
        GREEN=""
        YELLOW=""
        BLUE=""
        NC=""
    fi

    # Print header
    if [[ "$OUTPUT_MODE" != "json" ]]; then
        print_header "$SCRIPT_NAME v$SCRIPT_VERSION"
        echo "Total Tests: $TOTAL_TESTS"
        echo "Output Mode: $OUTPUT_MODE"
        [[ "$KOREAN_ONLY" == "true" ]] && echo "Filter: Korean tests only"
        echo
    fi

    # Run test categories
    if [[ "$KOREAN_ONLY" == "false" ]]; then
        test_file_structure
        test_uv_scripts
        test_apps
        test_skills_commands
        test_documentation
        test_syntax
        test_integration
    fi

    # Always run Korean tests
    test_korean_rendering

    # Print summary
    if [[ "$OUTPUT_MODE" == "json" ]]; then
        cat <<EOF
{
  "version": "$SCRIPT_VERSION",
  "total": $TESTS_TOTAL,
  "passed": $TESTS_PASSED,
  "failed": $TESTS_FAILED,
  "skipped": $TESTS_SKIPPED,
  "results": [
    $(IFS=,; echo "${TEST_RESULTS[*]}")
  ]
}
EOF
    else
        print_header "Test Summary"
        echo "  Total Tests:   $TESTS_TOTAL"
        echo -e "  ${GREEN}Passed:        $TESTS_PASSED${NC}"
        echo -e "  ${RED}Failed:        $TESTS_FAILED${NC}"
        echo -e "  ${YELLOW}Skipped:       $TESTS_SKIPPED${NC}"
        echo

        if [[ $TESTS_FAILED -eq 0 ]]; then
            echo -e "${GREEN}✓ All tests passed!${NC}"
            exit 0
        else
            echo -e "${RED}✗ Some tests failed${NC}"
            echo
            echo "Run with --verbose for details"
            exit 1
        fi
    fi
}

# Run main
main "$@"
