# Module: Scan Workspace

## Overview

Detailed procedures for scanning a single MoAI workspace to extract metadata.

---

## Scan Steps

### Step 1: Validate Workspace Structure

```bash
# Required directories
[ -d "{path}/.claude" ] && echo "✓ .claude exists"
[ -d "{path}/.moai" ] && echo "✓ .moai exists"
[ -d "{path}/moai-adk" ] && echo "✓ moai-adk exists"
[ -f "{path}/CLAUDE.md" ] && echo "✓ CLAUDE.md exists"
```

### Step 2: Extract Skills

```bash
# List all skill directories
ls -1 {path}/.claude/skills/ 2>/dev/null | sort

# Count skills
ls -1 {path}/.claude/skills/ 2>/dev/null | wc -l | tr -d ' '

# Get skill metadata (from frontmatter)
for skill in {path}/.claude/skills/*/SKILL.md; do
  head -20 "$skill" | grep -E "^(name|version|tier):"
done
```

### Step 3: Extract Agents

```bash
# List agent files
find {path}/.claude/agents -name "*.md" -type f 2>/dev/null | sort

# Count agents
find {path}/.claude/agents -name "*.md" -type f 2>/dev/null | wc -l | tr -d ' '
```

### Step 4: Extract Commands

```bash
# List command files
ls -1 {path}/.claude/commands/*.md 2>/dev/null | sort

# Count commands
ls -1 {path}/.claude/commands/*.md 2>/dev/null | wc -l | tr -d ' '
```

### Step 5: Extract MoAI-ADK Info

```bash
# Get version from pyproject.toml
grep '^version' {path}/moai-adk/pyproject.toml | cut -d'"' -f2

# Get last git commit
cd {path}/moai-adk && git log -1 --format='{"sha":"%H","date":"%ci","message":"%s"}'
```

### Step 6: Extract Config

```bash
# Get project name from config.json
jq -r '.project.name' {path}/.moai/config/config.json

# Check optimized status
jq -r '.project.optimized' {path}/.moai/config/config.json
```

---

## Output Schema

```json
{
  "$schema": "moai-flow-scan-v1",
  "id": "string (workspace identifier)",
  "path": "string (absolute path)",
  "scanned_at": "ISO8601 datetime",
  "moai_version": "semver string",
  "project": {
    "name": "string",
    "description": "string",
    "optimized": "boolean"
  },
  "components": {
    "skills": {
      "count": "integer",
      "list": ["string array of skill names"]
    },
    "agents": {
      "count": "integer",
      "list": ["string array of agent names"]
    },
    "commands": {
      "count": "integer",
      "list": ["string array of command names"]
    }
  },
  "git": {
    "last_commit_sha": "string (40 char)",
    "last_commit_date": "ISO8601 date",
    "last_commit_message": "string"
  }
}
```

---

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| Directory not found | Invalid path | Verify workspace path exists |
| Permission denied | Access rights | Check file permissions |
| Git not available | No git repo | Skip git metadata, log warning |
| Invalid JSON | Corrupt config | Use defaults, log warning |
