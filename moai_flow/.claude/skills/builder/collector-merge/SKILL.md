---
name: collector-merge
description: Handle merge operations with comprehensive logging and rollback support
version: 1.0.0
modularized: true
tier: 2
category: builder
last_updated: 2025-12-04
auto_trigger_keywords:
  - merge operations
  - collector merge
  - sync components
  - rollback merge
color: green
---

# Collector: Merge

**Intelligent merge operations with comprehensive audit trail and rollback capabilities**

> **Version**: 1.0.0
> **Status**: Production Ready
> **Part of**: MoAI Flow Collector System

---

## Purpose

Handle merge operations with enterprise-grade logging and safety:

- **Merge Execution**: Apply approved changes from learning reports
- **Audit Trail**: Complete logging of all decisions and changes
- **Rollback Support**: Undo any merge operation within 90 days
- **Safety First**: Backup before changes, validate after
- **User Control**: Record user decisions and approval methods

The collector-merge skill transforms learning decisions into actual workspace changes while maintaining full traceability and reversibility.

---

## Modules

| Module | Description |
|--------|-------------|
| [merge-log.md](./modules/merge-log.md) | Complete merge logging and audit trail system |
| [copy-operations.md](./modules/copy-operations.md) | File copy and backup procedures |
| [merge-strategies.md](./modules/merge-strategies.md) | Detailed merge algorithms |
| [enhancement-application.md](./modules/enhancement-application.md) | How to apply enhancements |
| [validation-checks.md](./modules/validation-checks.md) | Pre/post validation procedures |

---

## Quick Reference

### Invocation
```python
Skill("collector-merge")
```

### Core Actions
```yaml
PRESERVE:     Keep local version, no changes
UPDATE:       Replace with remote version
SMART_MERGE:  Intelligently combine both versions
ENHANCE:      Apply suggested improvements
```

### Safety Features
- Automatic backups before all changes
- Complete audit log with timestamps
- 90-day rollback window
- User approval tracking
- File-level change tracking

---

## Level 1: Merge Operations

### The Four Actions

Every component sync resolves to one of four actions:

#### 1. PRESERVE (Keep Local)

**When**: Local version is better or remote doesn't exist
**Action**: No changes, component stays as-is
**Log**: Records decision and reasoning

```yaml
action: PRESERVE
reason: "Local-only component, no remote equivalent"
files_changed: []
score_delta: 0
```

#### 2. UPDATE (Replace with Remote)

**When**: Remote version is clearly better (score delta > +10)
**Action**: Replace local with remote version
**Safety**: Backup created before replacement

```yaml
action: UPDATE
reason: "Remote score 91 vs local 72 (+19 improvement)"
files_changed:
  - path: .claude/skills/foundation-core/SKILL.md
    action: replaced
    lines_added: 120
    lines_removed: 85
```

#### 3. SMART_MERGE (Combine Best Features)

**When**: Both versions have unique valuable features
**Action**: Intelligently merge content
**Strategy**: Preserve best structure, add unique features

```yaml
action: SMART_MERGE
reason: "Local has decision-tree, remote has rule-creation"
preserved_features: ["local-decision-tree"]
merged_features: ["rule-command-creation"]
score_improvement: "+5 points"
```

#### 4. ENHANCE (Apply Improvements)

**When**: Learning report suggests enhancements
**Action**: Add modules, scripts, or sections
**Examples**: Add error-handling module, add automation scripts

```yaml
action: ENHANCE
type: add_module
module_added: error-handling.md
lines_added: 85
impact: "Improved error recovery documentation"
```

### Operation Flow

```
Learning Report Decision
         ↓
    Action Type?
    ┌────┴────┐
    │         │
PRESERVE   UPDATE / SMART_MERGE / ENHANCE
    │         │
    │     Create Backup
    │         │
    │     Apply Changes
    │         │
    └─────→ Validate
            │
        Update Log
            │
        Complete ✓
```

---

## Level 2: Backup & Rollback

### Automatic Backup Creation

Before ANY file modification:

```yaml
backup_process:
  trigger: Before UPDATE, SMART_MERGE, or ENHANCE
  action:
    1. Generate backup ID: "sync-{date}-{sequence}"
    2. Create backup directory in .moai/backups/
    3. Copy all files that will be modified
    4. Create manifest.json with file list
    5. Record backup location in merge log
    6. Set expiration date (90 days)
```

### Backup Structure

```
.moai/backups/sync-2025-12-04-001/
├── manifest.json              # What was backed up
├── metadata.json              # When, why, who
└── files/
    ├── .claude/skills/foundation-core/SKILL.md
    ├── .claude/skills/decision-framework/SKILL.md
    └── ...
```

### Rollback Command

Undo any merge within 90 days:

```bash
# Check available rollbacks
/collector:list-rollbacks

# Rollback specific merge
/collector:rollback merge-2025-12-04-001

# Verify rollback
git status
```

### Rollback Process

```yaml
rollback_execution:
  1. Load merge log by ID
  2. Verify rollback available (not expired)
  3. Verify backup exists
  4. Restore all files from backup
  5. Update merge log status to "rolled_back"
  6. Create rollback log entry
  7. Report success with file count
```

### Rollback Limitations

- **90-day window**: Backups expire after 90 days
- **One-time only**: Can't rollback a rollback
- **File conflicts**: Warns if files changed since merge
- **Clean state**: Requires no uncommitted changes

---

## Level 3: Merge Log Integration

### Complete Audit Trail

Every merge operation creates a comprehensive log:

```json
{
  "merge_id": "merge-2025-12-04-001",
  "timestamp": "2025-12-04T15:30:00Z",
  "command": "/collector:github-sync --repo org/repo",

  "decisions": [
    {
      "component": "foundation-core",
      "action": "UPDATE",
      "scores": {
        "local_before": 72,
        "remote": 91,
        "local_after": 91,
        "delta": "+19"
      },
      "user_decision": {
        "approved": true,
        "approved_at": "2025-12-04T15:25:00Z",
        "method": "auto_approve",
        "reason": "Score > 90 threshold"
      },
      "files_changed": [...]
    }
  ],

  "backup": {
    "location": ".moai/backups/sync-2025-12-04-001/",
    "files_backed_up": 12,
    "expires_at": "2025-03-04T15:30:00Z"
  },

  "rollback": {
    "available": true,
    "command": "/collector:rollback merge-2025-12-04-001"
  }
}
```

### Using Merge Logs

#### Query Recent Merges

```python
# Get last 7 days of merges
recent = get_recent_merges(days=7)

for merge in recent:
    print(f"{merge.id}: {merge.components_affected} components")
    print(f"  Status: {merge.status}")
    print(f"  Rollback: {merge.rollback_available}")
```

#### Component History

```python
# See all changes to specific component
history = get_component_history("foundation-core")

for entry in history:
    print(f"{entry.date}: {entry.action}")
    print(f"  Score delta: {entry.score_delta}")
    print(f"  Merge: {entry.merge_id}")
```

#### User Decision Tracking

Track how decisions were made:

| Method | Description | Example |
|--------|-------------|---------|
| `auto_approve` | Score > 90 threshold | Automatic UPDATE |
| `auto_preserve` | Local-only component | Automatic PRESERVE |
| `manual` | User selected explicitly | Interactive menu choice |
| `batch` | Part of "Apply All" | User chose batch mode |
| `default` | Accepted recommendation | User pressed enter |

### Log Benefits

1. **Accountability**: Know who approved what and when
2. **Debugging**: Trace issues to specific merge operations
3. **Reporting**: Generate merge statistics and trends
4. **Compliance**: Audit trail for team governance
5. **Learning**: Analyze which decisions worked best

---

## Works Well With

### Skills
- **collector-learner**: Provides the merge decisions this skill executes
- **collector-scanner**: Provides the workspace analysis
- **collector-ui**: Provides user interface for approvals

### Agents
- **builder-collector**: Orchestrates the entire collection flow
- **manager-git**: Handles git operations for commits

### Commands
- **/collector:github-sync**: Triggers sync with GitHub
- **/collector:rollback**: Executes rollback operation
- **/collector:list-rollbacks**: Shows available rollbacks

---

## Safety Checklist

Before merge:
- [ ] Learning report reviewed and approved
- [ ] Source files accessible
- [ ] Target workspace has clean git status
- [ ] Backup location has sufficient space
- [ ] No uncommitted changes in workspace

After merge:
- [ ] All approved changes applied successfully
- [ ] Merge log created with all decisions
- [ ] Backups created for modified files
- [ ] Validation checks passed
- [ ] Rollback command available

---

## Error Handling

### Common Issues

**Backup creation failed**
- Check disk space in .moai/backups/
- Verify write permissions
- Review backup location in config

**File conflict during merge**
- Check if files modified since scan
- Run fresh scan to get current state
- Consider PRESERVE for conflicted files

**Rollback unavailable**
- Check if backup expired (90 days)
- Verify backup files still exist
- Check if already rolled back once

**Validation failed after merge**
- Automatic rollback triggered
- Review validation errors in log
- Fix issues and retry merge

---

**Version**: 1.0.0 | **Status**: Production Ready | **Last Updated**: 2025-12-04
