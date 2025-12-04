# Module: Enhancement Application

## Overview

How to apply enhancement suggestions from the learner to consolidated components.

---

## Enhancement Types

### 1. Add Module

Create a new module file in an existing skill.

**Input from Learner**:
```json
{
  "type": "add_module",
  "target": "moai-connector-github",
  "module_name": "error-handling",
  "template": "...",
  "rationale": "Skill lacks error guidance"
}
```

**Application Steps**:

```bash
# 1. Verify target exists
[ -d "{target}/.claude/skills/moai-connector-github" ] || exit 1

# 2. Create modules directory if needed
mkdir -p "{target}/.claude/skills/moai-connector-github/modules"

# 3. Create module file
cat > "{target}/.claude/skills/moai-connector-github/modules/error-handling.md" << 'EOF'
# Module: Error Handling

## Overview
Common GitHub API errors and recovery strategies.

## Error Reference
| Code | Meaning | Recovery |
|------|---------|----------|
| 401 | Unauthorized | Re-authenticate with `gh auth login` |
| 403 | Forbidden | Check repo permissions |
| 404 | Not found | Verify resource exists |
| 422 | Validation failed | Check input format |
| 429 | Rate limited | Wait for reset, use `gh api -H "X-GitHub-Api-Version:2022-11-28"` |

## Recovery Patterns
...
EOF

# 4. Update SKILL.md modules table
# (append to Modules section)
```

**SKILL.md Update**:
```markdown
## Modules

| Module | Description |
|--------|-------------|
| `authentication.md` | Auth patterns and troubleshooting |
| `error-handling.md` | API errors and recovery ← NEW |
```

---

### 2. Add Script

Create a new automation script.

**Input from Learner**:
```json
{
  "type": "add_script",
  "target": "moai-flow-collector",
  "script_name": "flow_quick_scan.py",
  "purpose": "Automate workspace scanning"
}
```

**Application Steps**:

```bash
# 1. Create scripts directory
mkdir -p "{target}/.claude/skills/moai-flow-collector/scripts"

# 2. Generate script with standard template
cat > "{target}/.claude/skills/moai-flow-collector/scripts/flow_quick_scan.py" << 'EOF'
#!/usr/bin/env python3
"""
Quick scan a MoAI workspace.

Usage:
    uv run flow_quick_scan.py /path/to/workspace

Output:
    JSON scan result to stdout
"""

import json
import sys
from pathlib import Path
from datetime import datetime


def scan_workspace(workspace_path: str) -> dict:
    """Scan a MoAI workspace and return metadata."""
    ws = Path(workspace_path)

    result = {
        "path": str(ws.absolute()),
        "scanned_at": datetime.now().isoformat(),
        "components": {
            "skills": [],
            "agents": [],
            "commands": []
        }
    }

    # Scan skills
    skills_dir = ws / ".claude" / "skills"
    if skills_dir.exists():
        result["components"]["skills"] = sorted([
            d.name for d in skills_dir.iterdir() if d.is_dir()
        ])

    # Scan agents
    agents_dir = ws / ".claude" / "agents" / "moai"
    if agents_dir.exists():
        result["components"]["agents"] = sorted([
            f.stem for f in agents_dir.glob("*.md")
        ])

    # Scan commands
    commands_dir = ws / ".claude" / "commands"
    if commands_dir.exists():
        result["components"]["commands"] = sorted([
            f.stem for f in commands_dir.glob("*.md")
        ])

    return result


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: flow_quick_scan.py <workspace_path>", file=sys.stderr)
        sys.exit(1)

    result = scan_workspace(sys.argv[1])
    print(json.dumps(result, indent=2))
EOF

# 3. Make executable
chmod +x "{target}/.claude/skills/moai-flow-collector/scripts/flow_quick_scan.py"
```

---

### 3. Add Section

Add a new section to an existing file.

**Input from Learner**:
```json
{
  "type": "add_section",
  "target": "moai-foundation-core",
  "file": "SKILL.md",
  "section_name": "Edge Cases",
  "after_section": "Level 3",
  "content": "..."
}
```

**Application Steps**:

```python
def add_section(file_path, section_name, content, after_section):
    """Add a new section to a markdown file."""
    with open(file_path, 'r') as f:
        lines = f.readlines()

    # Find insertion point
    insert_idx = None
    in_target = False

    for i, line in enumerate(lines):
        if line.startswith(f'## {after_section}'):
            in_target = True
        elif in_target and line.startswith('## '):
            insert_idx = i
            break

    if insert_idx is None:
        insert_idx = len(lines)

    # Create new section
    new_section = f"\n## {section_name}\n\n{content}\n"

    # Insert
    lines.insert(insert_idx, new_section)

    with open(file_path, 'w') as f:
        f.writelines(lines)
```

---

### 4. Restructure

Reorganize files within a component.

**Input from Learner**:
```json
{
  "type": "restructure",
  "target": "legacy-skill",
  "current_structure": ["README.md (1200 lines)"],
  "new_structure": {
    "SKILL.md": "lines 1-200 (overview)",
    "modules/core-concepts.md": "lines 201-500",
    "modules/advanced-usage.md": "lines 501-900",
    "modules/troubleshooting.md": "lines 901-1200"
  }
}
```

**Application Steps**:

```bash
# 1. Backup original
cp "{target}/.claude/skills/legacy-skill/README.md" \
   "{target}/.claude/skills/legacy-skill/README.md.backup"

# 2. Create modules directory
mkdir -p "{target}/.claude/skills/legacy-skill/modules"

# 3. Split file (using line ranges from learner)
# This is typically done programmatically with section detection

# 4. Rename README.md to SKILL.md
mv "{target}/.claude/skills/legacy-skill/README.md" \
   "{target}/.claude/skills/legacy-skill/SKILL.md"

# 5. Validate new structure
ls -la "{target}/.claude/skills/legacy-skill/"
```

---

## Enhancement Validation

### Pre-Application Checks

```bash
validate_enhancement_applicable() {
  local target=$1
  local enhancement_type=$2

  case $enhancement_type in
    "add_module")
      # Target skill must exist
      [ -f "${target}/SKILL.md" ] || return 1
      ;;
    "add_script")
      # Target skill must exist
      [ -f "${target}/SKILL.md" ] || return 1
      ;;
    "add_section")
      # Target file must exist
      [ -f "${target}" ] || return 1
      ;;
  esac

  return 0
}
```

### Post-Application Checks

```bash
validate_enhancement_applied() {
  local target=$1
  local enhancement_type=$2
  local artifact=$3

  case $enhancement_type in
    "add_module")
      [ -f "${target}/modules/${artifact}.md" ] || return 1
      # Check module listed in SKILL.md
      grep -q "${artifact}" "${target}/SKILL.md" || return 1
      ;;
    "add_script")
      [ -f "${target}/scripts/${artifact}" ] || return 1
      [ -x "${target}/scripts/${artifact}" ] || return 1
      ;;
    "add_section")
      grep -q "## ${artifact}" "${target}" || return 1
      ;;
  esac

  return 0
}
```

---

## Enhancement Log

```json
{
  "enhancement_id": "enh-001",
  "applied_at": "2025-12-02T16:30:00Z",
  "type": "add_module",
  "target": "moai-connector-github",
  "artifact": "error-handling.md",
  "files_created": ["modules/error-handling.md"],
  "files_modified": ["SKILL.md"],
  "lines_added": 85,
  "status": "success",
  "validation": {
    "module_exists": true,
    "skill_md_updated": true,
    "syntax_valid": true
  }
}
```
