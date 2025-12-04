# Module: Copy Operations

## Overview

Procedures for copying components between workspaces with proper backup and validation.

---

## Copy Types

### 1. Fresh Copy (Component doesn't exist in target)

```bash
# Verify source exists
[ -d "{source}/.claude/skills/{skill}" ] || exit 1

# Verify target location exists
[ -d "{target}/.claude/skills" ] || mkdir -p "{target}/.claude/skills"

# Copy entire directory
cp -r "{source}/.claude/skills/{skill}" "{target}/.claude/skills/"

# Verify copy
[ -d "{target}/.claude/skills/{skill}" ] && echo "✓ Copied"
```

### 2. Replace Copy (Component exists, replacing entirely)

```bash
# Create backup directory
backup_dir="{target}/.moai/flow/backups/{consolidation_id}"
mkdir -p "$backup_dir"

# Backup existing
cp -r "{target}/.claude/skills/{skill}" "$backup_dir/"

# Remove existing
rm -rf "{target}/.claude/skills/{skill}"

# Copy new
cp -r "{source}/.claude/skills/{skill}" "{target}/.claude/skills/"

# Verify
diff -r "{source}/.claude/skills/{skill}" "{target}/.claude/skills/{skill}"
```

### 3. Selective Copy (Only specific files/directories)

```bash
# Copy specific subdirectory
cp -r "{source}/.claude/skills/{skill}/workflow" "{target}/.claude/skills/{skill}/"

# Copy specific file
cp "{source}/.claude/skills/{skill}/modules/new-module.md" \
   "{target}/.claude/skills/{skill}/modules/"
```

---

## Component Type Handlers

### Skills

```bash
copy_skill() {
  local source_ws=$1
  local target_ws=$2
  local skill_name=$3

  local src="${source_ws}/.claude/skills/${skill_name}"
  local dst="${target_ws}/.claude/skills/${skill_name}"

  # Validate source
  [ -f "${src}/SKILL.md" ] || return 1

  # Copy
  cp -r "$src" "$dst"

  # Validate destination
  [ -f "${dst}/SKILL.md" ] || return 1

  return 0
}
```

### Agents

```bash
copy_agent() {
  local source_ws=$1
  local target_ws=$2
  local agent_name=$3

  local src="${source_ws}/.claude/agents/moai/${agent_name}.md"
  local dst="${target_ws}/.claude/agents/moai/${agent_name}.md"

  # Validate source
  [ -f "$src" ] || return 1

  # Backup if exists
  [ -f "$dst" ] && cp "$dst" "${dst}.backup"

  # Copy
  cp "$src" "$dst"

  return 0
}
```

### Commands

```bash
copy_command() {
  local source_ws=$1
  local target_ws=$2
  local cmd_name=$3

  local src="${source_ws}/.claude/commands/${cmd_name}.md"
  local dst="${target_ws}/.claude/commands/${cmd_name}.md"

  # Validate source
  [ -f "$src" ] || return 1

  # Backup if exists
  [ -f "$dst" ] && cp "$dst" "${dst}.backup"

  # Copy
  cp "$src" "$dst"

  return 0
}
```

---

## Backup Strategy

### Backup Structure

```
{target}/.moai/flow/backups/
└── {consolidation_id}/
    ├── manifest.json
    ├── skills/
    │   └── {backed_up_skills}/
    ├── agents/
    │   └── {backed_up_agents}.md
    └── commands/
        └── {backed_up_commands}.md
```

### Manifest Format

```json
{
  "consolidation_id": "cons-2025-12-02-001",
  "created_at": "2025-12-02T16:00:00Z",
  "items": [
    {
      "type": "skill",
      "name": "builder",
      "original_path": ".claude/skills/builder",
      "backup_path": "skills/builder",
      "file_count": 8,
      "total_bytes": 24500
    }
  ],
  "retention_days": 30
}
```

### Cleanup Old Backups

```bash
# Remove backups older than 30 days
find "{target}/.moai/flow/backups" -maxdepth 1 -type d -mtime +30 -exec rm -rf {} \;
```

---

## Validation Checks

### Post-Copy Validation

| Check | Method | Pass Condition |
|-------|--------|----------------|
| Exists | `[ -d ]` or `[ -f ]` | Path exists |
| Complete | `diff -r` | No differences |
| Valid YAML | `head -20 \| grep "^---"` | Two `---` lines |
| Size sanity | Compare bytes | Within 1% |

### Validation Script

```bash
validate_copy() {
  local source=$1
  local dest=$2

  # Check existence
  [ -e "$dest" ] || { echo "FAIL: doesn't exist"; return 1; }

  # Check completeness (for directories)
  if [ -d "$source" ]; then
    local src_count=$(find "$source" -type f | wc -l)
    local dst_count=$(find "$dest" -type f | wc -l)
    [ "$src_count" -eq "$dst_count" ] || { echo "FAIL: file count mismatch"; return 1; }
  fi

  # Check content match
  diff -rq "$source" "$dest" >/dev/null || { echo "FAIL: content differs"; return 1; }

  echo "PASS: copy validated"
  return 0
}
```

---

## Error Handling

| Error | Cause | Recovery |
|-------|-------|----------|
| Permission denied | Access rights | Check/fix permissions |
| No space left | Disk full | Clear space, retry |
| Source not found | Path wrong | Verify source path |
| Copy interrupted | Process killed | Remove partial, retry |

### Atomic Copy Pattern

```bash
# Copy to temp location first
temp_dir=$(mktemp -d)
cp -r "$source" "$temp_dir/component"

# Validate temp copy
validate_copy "$source" "$temp_dir/component" || {
  rm -rf "$temp_dir"
  exit 1
}

# Move to final location (atomic on same filesystem)
mv "$temp_dir/component" "$dest"
rm -rf "$temp_dir"
```
