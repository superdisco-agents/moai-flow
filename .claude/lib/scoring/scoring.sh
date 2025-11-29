#!/usr/bin/env bash
#
# Directory Activity Scoring - Bash Implementation
#
# This script provides a shell-native implementation of directory activity scoring
# for integration with shell scripts and automation workflows.
#
# Usage:
#   ./scoring.sh <directory> [--format json|text] [--verbose]
#
# Exit Codes:
#   0 - Active (score >= 20)
#   1 - Borderline (0 <= score < 20)
#   2 - Archivable (score < 0)
#   3 - Error

# Check bash version for associative array support
if [ "${BASH_VERSINFO[0]}" -lt 4 ]; then
    echo "Error: This script requires Bash 4.0 or higher for associative arrays" >&2
    echo "Current version: ${BASH_VERSION}" >&2
    echo "On macOS, install with: brew install bash" >&2
    exit 3
fi

set -euo pipefail

# Configuration
ACTIVE_THRESHOLD=20
BORDERLINE_THRESHOLD=0

# Protected paths
PROTECTED_PATHS=(
    ".git" ".claude" "node_modules" ".venv" "venv"
    "__pycache__" "dist" "build" ".next" ".nuxt"
)

# Critical files
CRITICAL_FILES=(
    "package.json" "requirements.txt" "Cargo.toml" "go.mod"
    "pom.xml" "Gemfile" ".git" "Makefile" "CMakeLists.txt"
)

# Colors for output
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Global variables for scoring
declare -A FACTORS
declare -A WEIGHTS=(
    ["time_decay"]=1.0
    ["git_activity"]=2.0
    ["dependencies"]=1.5
    ["documentation"]=1.0
    ["file_activity"]=1.2
    ["project_structure"]=0.8
)

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $*" >&2
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $*" >&2
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $*" >&2
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $*" >&2
}

# Check if directory is protected
is_protected() {
    local path="$1"
    local base_name=$(basename "$path")

    for protected in "${PROTECTED_PATHS[@]}"; do
        if [[ "$path" == *"/$protected"* ]] || [[ "$base_name" == "$protected" ]]; then
            return 0
        fi
    done

    return 1
}

# Check if directory has critical files
has_critical_files() {
    local path="$1"

    for critical in "${CRITICAL_FILES[@]}"; do
        if [[ -e "$path/$critical" ]]; then
            return 0
        fi
    done

    return 1
}

# Detect project type
detect_project_type() {
    local path="$1"

    [[ -f "$path/package.json" ]] && echo "node" && return
    [[ -f "$path/requirements.txt" ]] || [[ -f "$path/setup.py" ]] && echo "python" && return
    [[ -f "$path/Cargo.toml" ]] && echo "rust" && return
    [[ -f "$path/go.mod" ]] && echo "go" && return
    [[ -f "$path/pom.xml" ]] || [[ -f "$path/build.gradle" ]] && echo "java" && return
    [[ -f "$path/Gemfile" ]] && echo "ruby" && return
    [[ -f "$path/composer.json" ]] && echo "php" && return
    [[ -d "$path/.git" ]] && echo "git" && return

    echo "unknown"
}

# Score time decay
score_time_decay() {
    local path="$1"
    local current_time=$(date +%s)

    # Find most recent file modification
    local last_mod
    if [[ -d "$path" ]]; then
        last_mod=$(find "$path" -type f -not -path "*/.*" -printf '%T@\n' 2>/dev/null | sort -rn | head -1)
        last_mod=${last_mod:-0}
    else
        last_mod=0
    fi

    if [[ "$last_mod" == "0" ]]; then
        echo "0"
        return
    fi

    local days_old=$(( (current_time - ${last_mod%.*}) / 86400 ))

    local score=0
    if (( days_old < 7 )); then
        score=10
    elif (( days_old < 30 )); then
        score=$(awk "BEGIN {printf \"%.2f\", 10 - (($days_old - 7) * (5.0 / 23))}")
    elif (( days_old < 90 )); then
        score=$(awk "BEGIN {printf \"%.2f\", 5 - (($days_old - 30) * (5.0 / 60))}")
    else
        score=$(awk "BEGIN {printf \"%.2f\", 0 - (($days_old - 90) * (5.0 / 180)); if (score < -5) score = -5}")
    fi

    echo "$score"
}

# Score git activity
score_git_activity() {
    local path="$1"
    local score=0

    if [[ ! -d "$path/.git" ]]; then
        echo "0"
        return
    fi

    score=5  # Base score for being a git repo

    # Check recent commits (last 30 days)
    if command -v git &> /dev/null; then
        local commit_count
        commit_count=$(git -C "$path" log --since="30 days ago" --oneline 2>/dev/null | wc -l || echo "0")

        if (( commit_count > 0 )); then
            local commit_score=$(awk "BEGIN {printf \"%.2f\", $commit_count * 1.5; if (score > 15) score = 15}")
            score=$(awk "BEGIN {printf \"%.2f\", $score + $commit_score}")
        fi

        # Check branch count
        local branch_count
        branch_count=$(git -C "$path" branch -a 2>/dev/null | wc -l || echo "0")

        if (( branch_count > 1 )); then
            score=$(awk "BEGIN {printf \"%.2f\", $score + 5}")
        fi

        # Check for uncommitted changes
        if git -C "$path" status --porcelain 2>/dev/null | grep -q .; then
            score=$(awk "BEGIN {printf \"%.2f\", $score + 10}")
        fi
    fi

    echo "$score"
}

# Score dependencies
score_dependencies() {
    local path="$1"
    local score=0

    local dep_files=(
        "package.json" "requirements.txt" "Cargo.toml" "go.mod"
        "pom.xml" "Gemfile" "composer.json" "Pipfile" "pyproject.toml"
    )

    local lock_files=(
        "package-lock.json" "yarn.lock" "Cargo.lock" "go.sum"
        "Gemfile.lock" "composer.lock" "Pipfile.lock" "poetry.lock"
    )

    local dep_count=0
    local lock_count=0

    for dep_file in "${dep_files[@]}"; do
        [[ -f "$path/$dep_file" ]] && ((dep_count++))
    done

    for lock_file in "${lock_files[@]}"; do
        [[ -f "$path/$lock_file" ]] && ((lock_count++))
    done

    (( dep_count > 0 )) && score=$((score + 10))
    (( lock_count > 0 )) && score=$((score + 5))
    (( dep_count > 1 )) && score=$((score + 3))

    echo "$score"
}

# Score documentation
score_documentation() {
    local path="$1"
    local score=0

    # Check for README
    if ls "$path"/[Rr][Ee][Aa][Dd][Mm][Ee]* &>/dev/null; then
        score=$((score + 8))
    fi

    # Check for other documentation
    local doc_files=(
        "contributing.md" "changelog.md" "license" "license.md"
        "code_of_conduct.md" "security.md" "api.md"
    )

    local doc_count=0
    for doc_file in "${doc_files[@]}"; do
        [[ -f "$path/$doc_file" ]] || [[ -f "$path/${doc_file^^}" ]] && ((doc_count++))
    done

    score=$((score + doc_count * 2))
    (( score > 18 )) && score=18

    # Check for docs directory
    [[ -d "$path/docs" ]] && score=$((score + 5))

    echo "$score"
}

# Score file activity
score_file_activity() {
    local path="$1"
    local score=0

    # Count files (excluding hidden)
    local file_count
    file_count=$(find "$path" -maxdepth 1 -type f -not -name ".*" 2>/dev/null | wc -l)

    (( file_count > 10 )) && score=$((score + 5))

    # Check for source code files
    local source_extensions=(
        "py" "js" "ts" "jsx" "tsx" "go" "rs" "java"
        "c" "cpp" "h" "hpp" "rb" "php" "swift" "kt"
    )

    local has_source=0
    for ext in "${source_extensions[@]}"; do
        if find "$path" -maxdepth 1 -type f -name "*.$ext" 2>/dev/null | grep -q .; then
            has_source=1
            break
        fi
    done

    (( has_source == 1 )) && score=$((score + 5))

    # Count unique extensions
    local ext_count
    ext_count=$(find "$path" -maxdepth 1 -type f 2>/dev/null | sed 's/.*\.//' | sort -u | wc -l)

    (( ext_count > 3 )) && score=$((score + 3))

    echo "$score"
}

# Score project structure
score_project_structure() {
    local path="$1"
    local score=0

    # Check for standard directories
    local standard_dirs=("src" "lib" "test" "tests" "docs" "examples" "scripts")
    local dir_count=0

    for dir in "${standard_dirs[@]}"; do
        [[ -d "$path/$dir" ]] && ((dir_count++))
    done

    score=$((dir_count * 2))
    (( score > 10 )) && score=10

    # Check for test directory
    if [[ -d "$path/test" ]] || [[ -d "$path/tests" ]] || [[ -d "$path/__tests__" ]] || [[ -d "$path/spec" ]]; then
        score=$((score + 5))
    fi

    # Check for CI/CD
    if [[ -d "$path/.github" ]] || [[ -f "$path/.gitlab-ci.yml" ]] || \
       [[ -f "$path/.travis.yml" ]] || [[ -f "$path/Jenkinsfile" ]] || [[ -d "$path/.circleci" ]]; then
        score=$((score + 5))
    fi

    echo "$score"
}

# Calculate total score
calculate_total_score() {
    local total=0

    for factor in "${!FACTORS[@]}"; do
        local factor_score="${FACTORS[$factor]}"
        local weight="${WEIGHTS[$factor]}"
        local weighted=$(awk "BEGIN {printf \"%.2f\", $factor_score * $weight}")
        total=$(awk "BEGIN {printf \"%.2f\", $total + $weighted}")
    done

    echo "$total"
}

# Classify based on score
classify_score() {
    local score="$1"

    if awk "BEGIN {exit !($score >= $ACTIVE_THRESHOLD)}"; then
        echo "Active"
    elif awk "BEGIN {exit !($score >= $BORDERLINE_THRESHOLD)}"; then
        echo "Borderline"
    else
        echo "Archivable"
    fi
}

# Get classification exit code
get_exit_code() {
    local classification="$1"

    case "$classification" in
        "Active") return 0 ;;
        "Borderline") return 1 ;;
        "Archivable") return 2 ;;
        *) return 3 ;;
    esac
}

# Main scoring function
score_directory() {
    local path="$1"
    local format="${2:-text}"
    local verbose="${3:-false}"

    # Validate directory
    if [[ ! -d "$path" ]]; then
        log_error "Not a directory: $path"
        return 3
    fi

    local protected="false"
    local warnings=()

    # Check if protected
    if is_protected "$path"; then
        protected="true"
        warnings+=("Directory is in protected paths list")
    fi

    # Detect project type
    local project_type
    project_type=$(detect_project_type "$path")

    # Calculate factor scores
    FACTORS["time_decay"]=$(score_time_decay "$path")
    FACTORS["git_activity"]=$(score_git_activity "$path")
    FACTORS["dependencies"]=$(score_dependencies "$path")
    FACTORS["documentation"]=$(score_documentation "$path")
    FACTORS["file_activity"]=$(score_file_activity "$path")
    FACTORS["project_structure"]=$(score_project_structure "$path")

    # Calculate total score
    local total_score
    total_score=$(calculate_total_score)

    # Override if protected
    if [[ "$protected" == "true" ]]; then
        if awk "BEGIN {exit !($total_score < $ACTIVE_THRESHOLD)}"; then
            total_score="$ACTIVE_THRESHOLD"
        fi
    fi

    # Classify
    local classification
    classification=$(classify_score "$total_score")

    # Get last modified time
    local last_modified
    last_modified=$(date -r "$path" "+%Y-%m-%d %H:%M:%S" 2>/dev/null || echo "Unknown")

    # Output results
    case "$format" in
        "json")
            cat <<EOF
{
  "path": "$path",
  "total_score": $total_score,
  "classification": "$classification",
  "project_type": "$project_type",
  "protected": $protected,
  "last_modified": "$last_modified",
  "factors": {
$(for factor in "${!FACTORS[@]}"; do
    echo "    \"$factor\": ${FACTORS[$factor]},"
done | sed '$ s/,$//')
  },
  "warnings": [$(printf '"%s",' "${warnings[@]}" | sed 's/,$//')]
}
EOF
            ;;

        "text")
            echo "======================================================================"
            echo "Path: $path"
            echo "Score: $total_score"
            echo "Classification: $classification"
            echo "Project Type: $project_type"
            echo "Protected: $protected"
            echo "Last Modified: $last_modified"

            if [[ ${#warnings[@]} -gt 0 ]]; then
                echo "Warnings: ${warnings[*]}"
            fi

            if [[ "$verbose" == "true" ]]; then
                echo ""
                echo "Factor Breakdown:"
                for factor in "${!FACTORS[@]}"; do
                    local factor_score="${FACTORS[$factor]}"
                    local weight="${WEIGHTS[$factor]}"
                    local weighted=$(awk "BEGIN {printf \"%.2f\", $factor_score * $weight}")
                    printf "  %-20s: %6.2f (weight: %.1f, weighted: %.2f)\n" \
                        "$factor" "$factor_score" "$weight" "$weighted"
                done
            fi

            echo "======================================================================"
            ;;
    esac

    # Return appropriate exit code
    get_exit_code "$classification"
    return $?
}

# Usage information
usage() {
    cat <<EOF
Usage: $0 <directory> [options]

Options:
    --format <format>    Output format: text (default) or json
    --verbose, -v        Show detailed factor breakdown
    --help, -h           Show this help message

Examples:
    $0 /path/to/project
    $0 /path/to/project --format json
    $0 /path/to/project --verbose

Exit Codes:
    0 - Active (score >= 20)
    1 - Borderline (0 <= score < 20)
    2 - Archivable (score < 0)
    3 - Error
EOF
}

# Parse command line arguments
main() {
    local path=""
    local format="text"
    local verbose="false"

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --format)
                format="$2"
                shift 2
                ;;
            --verbose|-v)
                verbose="true"
                shift
                ;;
            --help|-h)
                usage
                exit 0
                ;;
            *)
                if [[ -z "$path" ]]; then
                    path="$1"
                else
                    log_error "Unexpected argument: $1"
                    usage
                    exit 3
                fi
                shift
                ;;
        esac
    done

    if [[ -z "$path" ]]; then
        log_error "Missing required argument: directory path"
        usage
        exit 3
    fi

    score_directory "$path" "$format" "$verbose"
}

# Run main function if executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
