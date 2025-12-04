# Module: Validation Checks

## Overview

Comprehensive validation procedures for before, during, and after consolidation.

---

## Pre-Consolidation Validation

### 1. Source Accessibility

```bash
validate_sources() {
  local source_a=$1
  local source_b=$2

  # Check paths exist
  [ -d "$source_a" ] || { echo "ERROR: Source A not found"; return 1; }
  [ -d "$source_b" ] || { echo "ERROR: Source B not found"; return 1; }

  # Check .claude directory exists
  [ -d "$source_a/.claude" ] || { echo "ERROR: Source A not a MoAI workspace"; return 1; }
  [ -d "$source_b/.claude" ] || { echo "ERROR: Source B not a MoAI workspace"; return 1; }

  # Check read permissions
  [ -r "$source_a/.claude/skills" ] || { echo "ERROR: Cannot read source A skills"; return 1; }
  [ -r "$source_b/.claude/skills" ] || { echo "ERROR: Cannot read source B skills"; return 1; }

  echo "✓ Sources accessible"
  return 0
}
```

### 2. Target Writability

```bash
validate_target() {
  local target=$1

  # Check path exists
  [ -d "$target" ] || { echo "ERROR: Target not found"; return 1; }

  # Check write permissions
  [ -w "$target/.claude/skills" ] || { echo "ERROR: Cannot write to target skills"; return 1; }

  # Check disk space (need at least 100MB free)
  local free_mb=$(df -m "$target" | tail -1 | awk '{print $4}')
  [ "$free_mb" -gt 100 ] || { echo "ERROR: Insufficient disk space"; return 1; }

  echo "✓ Target writable"
  return 0
}
```

### 3. Git Status Clean

```bash
validate_git_clean() {
  local target=$1

  cd "$target" || return 1

  # Check if git repo
  git rev-parse --git-dir > /dev/null 2>&1 || {
    echo "WARNING: Target is not a git repo"
    return 0  # Not fatal
  }

  # Check for uncommitted changes
  if [ -n "$(git status --porcelain)" ]; then
    echo "ERROR: Target has uncommitted changes"
    git status --short
    return 1
  fi

  echo "✓ Git status clean"
  return 0
}
```

### 4. Learning Report Valid

```bash
validate_learning_report() {
  local report_path=$1

  # Check file exists
  [ -f "$report_path" ] || { echo "ERROR: Learning report not found"; return 1; }

  # Check valid JSON
  python3 -c "import json; json.load(open('$report_path'))" 2>/dev/null || {
    echo "ERROR: Learning report is not valid JSON"
    return 1
  }

  # Check required fields
  python3 << EOF
import json
import sys

with open('$report_path') as f:
    report = json.load(f)

required = ['collection_id', 'analyses', 'summary']
missing = [r for r in required if r not in report]

if missing:
    print(f"ERROR: Missing required fields: {missing}")
    sys.exit(1)

print("✓ Learning report valid")
EOF
}
```

---

## During-Consolidation Validation

### Copy Validation

```bash
validate_copy() {
  local source=$1
  local dest=$2

  # Existence check
  [ -e "$dest" ] || { echo "FAIL: Copy target doesn't exist"; return 1; }

  # File count match (for directories)
  if [ -d "$source" ]; then
    local src_count=$(find "$source" -type f | wc -l | tr -d ' ')
    local dst_count=$(find "$dest" -type f | wc -l | tr -d ' ')

    [ "$src_count" -eq "$dst_count" ] || {
      echo "FAIL: File count mismatch ($src_count vs $dst_count)"
      return 1
    }
  fi

  # Size sanity (within 1%)
  local src_size=$(du -s "$source" | cut -f1)
  local dst_size=$(du -s "$dest" | cut -f1)
  local diff=$((src_size - dst_size))
  local threshold=$((src_size / 100))

  [ ${diff#-} -lt "$threshold" ] || {
    echo "FAIL: Size differs significantly"
    return 1
  }

  echo "✓ Copy validated"
  return 0
}
```

### Merge Validation

```bash
validate_merge() {
  local merged_path=$1

  # No conflict markers
  if grep -rq "<<<<<<" "$merged_path"; then
    echo "FAIL: Unresolved conflict markers found"
    grep -r "<<<<<<" "$merged_path"
    return 1
  fi

  # YAML frontmatter valid
  if [ -f "$merged_path/SKILL.md" ]; then
    python3 << EOF
import yaml
import sys

with open('$merged_path/SKILL.md') as f:
    content = f.read()

parts = content.split('---')
if len(parts) >= 3:
    try:
        yaml.safe_load(parts[1])
        print("✓ YAML frontmatter valid")
    except yaml.YAMLError as e:
        print(f"FAIL: Invalid YAML frontmatter: {e}")
        sys.exit(1)
EOF
  fi

  return 0
}
```

### Enhancement Validation

```bash
validate_enhancement() {
  local target=$1
  local enhancement_type=$2
  local artifact=$3

  case $enhancement_type in
    "add_module")
      [ -f "${target}/modules/${artifact}.md" ] || {
        echo "FAIL: Module not created"
        return 1
      }
      grep -q "${artifact}" "${target}/SKILL.md" || {
        echo "FAIL: Module not added to SKILL.md"
        return 1
      }
      ;;
    "add_script")
      [ -f "${target}/scripts/${artifact}" ] || {
        echo "FAIL: Script not created"
        return 1
      }
      [ -x "${target}/scripts/${artifact}" ] || {
        echo "FAIL: Script not executable"
        return 1
      }
      ;;
  esac

  echo "✓ Enhancement validated"
  return 0
}
```

---

## Post-Consolidation Validation

### 1. Complete Application

```bash
validate_all_applied() {
  local report_path=$1
  local target=$2

  python3 << EOF
import json

with open('$report_path') as f:
    report = json.load(f)

errors = []

for analysis in report['analyses']:
    if analysis['recommendation'] in ['must_merge', 'should_merge']:
        component = analysis['component']
        comp_type = analysis['type']

        if comp_type == 'skill':
            path = f"$target/.claude/skills/{component}"
        elif comp_type == 'agent':
            path = f"$target/.claude/agents/moai/{component}.md"
        elif comp_type == 'command':
            path = f"$target/.claude/commands/{component}.md"

        import os
        if not os.path.exists(path):
            errors.append(f"Missing: {component} ({comp_type})")

if errors:
    print("FAIL: Some components not applied:")
    for e in errors:
        print(f"  - {e}")
    exit(1)

print("✓ All approved components applied")
EOF
}
```

### 2. No Broken References

```bash
validate_references() {
  local target=$1

  # Check internal links in markdown files
  find "$target/.claude" -name "*.md" -exec grep -l "\](./" {} \; | while read file; do
    dir=$(dirname "$file")
    grep -o '\](\.\/[^)]*' "$file" | sed 's/\](\.\///' | while read link; do
      if [ ! -e "$dir/$link" ]; then
        echo "WARN: Broken link in $file: $link"
      fi
    done
  done

  echo "✓ Reference check complete"
}
```

### 3. Git Diff Summary

```bash
generate_diff_summary() {
  local target=$1

  cd "$target" || return 1

  echo "## Git Changes Summary"
  echo ""

  # Count changes
  local added=$(git status --porcelain | grep "^A" | wc -l | tr -d ' ')
  local modified=$(git status --porcelain | grep "^M" | wc -l | tr -d ' ')
  local deleted=$(git status --porcelain | grep "^D" | wc -l | tr -d ' ')

  echo "- Files added: $added"
  echo "- Files modified: $modified"
  echo "- Files deleted: $deleted"
  echo ""

  # List specific changes
  echo "### Added Files"
  git status --porcelain | grep "^A" | sed 's/^A  /- /'

  echo ""
  echo "### Modified Files"
  git status --porcelain | grep "^M" | sed 's/^M  /- /'
}
```

---

## Validation Report

### Output Format

```json
{
  "validation_id": "val-2025-12-02-001",
  "consolidation_id": "cons-2025-12-02-001",
  "validated_at": "2025-12-02T16:45:00Z",

  "pre_checks": {
    "sources_accessible": true,
    "target_writable": true,
    "git_clean": true,
    "report_valid": true
  },

  "during_checks": {
    "copies_validated": 3,
    "copies_failed": 0,
    "merges_validated": 1,
    "merges_failed": 0,
    "enhancements_validated": 2,
    "enhancements_failed": 0
  },

  "post_checks": {
    "all_applied": true,
    "broken_references": 0,
    "git_changes": {
      "added": 5,
      "modified": 2,
      "deleted": 0
    }
  },

  "overall_status": "passed",
  "warnings": [],
  "errors": []
}
```

---

## Quick Validation Commands

```bash
# Full pre-flight check
validate_preflight() {
  validate_sources "$1" "$2" && \
  validate_target "$3" && \
  validate_git_clean "$3" && \
  validate_learning_report "$4"
}

# Quick post-check
validate_postflight() {
  validate_all_applied "$1" "$2" && \
  validate_references "$2" && \
  generate_diff_summary "$2"
}
```
