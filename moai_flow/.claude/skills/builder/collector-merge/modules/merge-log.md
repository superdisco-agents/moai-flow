# Merge Log System

**Comprehensive audit trail for all sync and merge operations**

> **Version**: 1.0.0
> **Part of**: collector-merge skill
> **Last Updated**: 2025-12-04

---

## Purpose

The Merge Log System provides:

1. **Audit Trail**: Complete history of all sync decisions
2. **Rollback Support**: Ability to undo any merge operation
3. **User Decisions**: Record of what user approved/rejected
4. **Impact Tracking**: Before/after scores and changes

---

## Storage Location

```
.moai/flow/merge-logs/
├── index.json              # Merge registry
└── merges/
    ├── merge-2025-12-04-001.json
    ├── merge-2025-12-04-002.json
    └── merge-2025-12-03-001.json
```

---

## Schema Definitions

### Index Schema (index.json)

```json
{
  "version": "1.0.0",
  "last_updated": "2025-12-04T16:00:00Z",

  "merges": [
    {
      "id": "merge-2025-12-04-001",
      "timestamp": "2025-12-04T15:30:00Z",
      "type": "github_sync",
      "status": "success",
      "components_affected": 4,
      "rollback_available": true,
      "file": "merges/merge-2025-12-04-001.json"
    }
  ],

  "summary": {
    "total_merges": 15,
    "successful": 14,
    "failed": 1,
    "rolled_back": 0,
    "this_week": 3,
    "this_month": 8
  },

  "recent_components": [
    "foundation-core",
    "decision-framework",
    "builder-skill"
  ]
}
```

### Merge Log Schema (merges/*.json)

```json
{
  "merge_id": "merge-2025-12-04-001",
  "version": "1.0.0",

  "metadata": {
    "timestamp": "2025-12-04T15:30:00Z",
    "initiated_by": "user",
    "command": "/collector:github-sync --repo superdisco-agents/moai-adk",
    "mode": "bidirectional",
    "agent_version": "collector-merger v1.0.0"
  },

  "source": {
    "collection_id": "flow-2025-12-04-001",
    "learning_id": "learn-2025-12-04-001",
    "repo": "superdisco-agents/moai-adk",
    "branches_compared": ["main", "feature/SPEC-first", "feature/workspace"]
  },

  "decisions": [
    {
      "component": "foundation-core",
      "action": "UPDATE",
      "source_branch": "feature/SPEC-first",

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

      "files_changed": [
        {
          "path": ".claude/skills/moai-foundation-core/SKILL.md",
          "action": "replaced",
          "lines_added": 120,
          "lines_removed": 85
        },
        {
          "path": ".claude/skills/moai-foundation-core/modules/spec-fields.md",
          "action": "added",
          "lines_added": 45,
          "lines_removed": 0
        }
      ],

      "preserved_features": [],
      "merged_features": []
    },
    {
      "component": "decision-framework",
      "action": "SMART_MERGE",
      "source_branch": "local + main",

      "scores": {
        "local_before": 85,
        "remote": 88,
        "local_after": 90,
        "delta": "+5"
      },

      "user_decision": {
        "approved": true,
        "approved_at": "2025-12-04T15:26:00Z",
        "method": "manual",
        "reason": "User selected 'Smart Merge' option"
      },

      "files_changed": [
        {
          "path": ".claude/skills/decision-logic-framework/SKILL.md",
          "action": "merged",
          "lines_added": 25,
          "lines_removed": 5
        }
      ],

      "preserved_features": ["local-decision-tree"],
      "merged_features": ["rule-command-creation"]
    },
    {
      "component": "collector-scan",
      "action": "PRESERVE",
      "source_branch": "local",

      "scores": {
        "local_before": 88,
        "remote": null,
        "local_after": 88,
        "delta": "0"
      },

      "user_decision": {
        "approved": true,
        "approved_at": "2025-12-04T15:27:00Z",
        "method": "auto",
        "reason": "Local-only component, no remote equivalent"
      },

      "files_changed": [],
      "preserved_features": ["all"],
      "merged_features": []
    }
  ],

  "skipped": [
    {
      "component": "moai-lang-python",
      "reason": "Scores equal, no unique features",
      "local_score": 75,
      "remote_score": 75
    }
  ],

  "contributions": [
    {
      "component": "collector-scan",
      "action": "PROPOSE_UPSTREAM",
      "pr_draft": {
        "title": "feat: Add collector-scan skill for workspace comparison",
        "body": "## Summary\n\nAdds intelligent workspace scanning...",
        "labels": ["enhancement", "skills", "collector"],
        "target_branch": "main"
      },
      "pr_created": false,
      "pr_url": null
    }
  ],

  "backup": {
    "created": true,
    "location": ".moai/backups/sync-2025-12-04-001/",
    "files_backed_up": 12,
    "size_bytes": 45678,
    "expires_at": "2025-03-04T15:30:00Z"
  },

  "outcome": {
    "status": "success",
    "components_updated": 2,
    "components_preserved": 1,
    "components_merged": 1,
    "components_skipped": 1,
    "errors": [],
    "warnings": []
  },

  "rollback": {
    "available": true,
    "command": "/collector:rollback merge-2025-12-04-001",
    "expires_at": "2025-03-04T15:30:00Z"
  },

  "timing": {
    "scan_duration_ms": 5200,
    "learn_duration_ms": 12400,
    "merge_duration_ms": 3800,
    "total_duration_ms": 21400
  }
}
```

---

## Operations

### 1. Create Merge Log

When starting a merge operation:

```yaml
create_log:
  trigger: Merge operation started
  action:
    1. Generate merge_id: "merge-{date}-{sequence}"
    2. Create merges/{merge_id}.json
    3. Add entry to index.json
    4. Initialize with metadata
```

### 2. Record Decision

For each component decision:

```yaml
record_decision:
  trigger: User approves/rejects component
  action:
    1. Add decision to decisions array
    2. Record scores before/after
    3. Record user approval method
    4. List files affected
```

### 3. Update Outcome

After merge completes:

```yaml
update_outcome:
  trigger: Merge operation completes
  action:
    1. Set outcome.status (success/partial/failed)
    2. Count updated/preserved/merged/skipped
    3. Record any errors/warnings
    4. Set rollback availability
```

### 4. Rollback Support

Enable undo for merge:

```yaml
rollback_process:
  trigger: /collector:rollback {merge_id}
  action:
    1. Load backup from backup.location
    2. Restore files to pre-merge state
    3. Update merge log status to "rolled_back"
    4. Create new log entry for rollback action
```

---

## API Functions

### create_merge_log(metadata)

```python
def create_merge_log(
    command: str,
    mode: str,
    collection_id: str
) -> MergeLog:
    """
    Initialize new merge log entry.

    Args:
        command: Command that initiated merge
        mode: Sync mode (pull, bidirectional, etc.)
        collection_id: Associated collection

    Returns:
        MergeLog with generated ID and metadata
    """
    merge_id = generate_merge_id()

    log = MergeLog(
        merge_id=merge_id,
        metadata={
            "timestamp": now(),
            "initiated_by": "user",
            "command": command,
            "mode": mode,
            "agent_version": VERSION
        },
        source={
            "collection_id": collection_id
        }
    )

    save_merge_log(log)
    update_index(merge_id)

    return log
```

### record_decision(merge_id, decision)

```python
def record_decision(
    merge_id: str,
    component: str,
    action: str,
    scores: ScoreInfo,
    user_decision: UserDecision,
    files_changed: List[FileChange]
) -> None:
    """
    Record a component sync decision.
    """
    log = load_merge_log(merge_id)

    decision_entry = {
        "component": component,
        "action": action,
        "scores": scores,
        "user_decision": user_decision,
        "files_changed": files_changed
    }

    log.decisions.append(decision_entry)
    save_merge_log(log)
```

### finalize_merge(merge_id, outcome)

```python
def finalize_merge(
    merge_id: str,
    status: str,
    errors: List[str] = None
) -> None:
    """
    Finalize merge log with outcome.
    """
    log = load_merge_log(merge_id)

    log.outcome = {
        "status": status,
        "components_updated": count_action(log, "UPDATE"),
        "components_preserved": count_action(log, "PRESERVE"),
        "components_merged": count_action(log, "SMART_MERGE"),
        "components_skipped": len(log.skipped),
        "errors": errors or [],
        "warnings": []
    }

    log.rollback.available = (status == "success")

    save_merge_log(log)
    update_index(merge_id, status)
```

### rollback_merge(merge_id)

```python
def rollback_merge(merge_id: str) -> RollbackResult:
    """
    Rollback a previous merge operation.
    """
    log = load_merge_log(merge_id)

    if not log.rollback.available:
        return RollbackResult(success=False, reason="Rollback not available")

    if datetime.now() > log.rollback.expires_at:
        return RollbackResult(success=False, reason="Rollback expired")

    # Restore from backup
    restore_backup(log.backup.location)

    # Update log
    log.outcome.status = "rolled_back"
    log.rollback.available = False
    log.rollback.rolled_back_at = now()

    save_merge_log(log)

    return RollbackResult(success=True)
```

---

## User Decision Methods

Track how decisions were made:

| Method | Description | When Used |
|--------|-------------|-----------|
| `auto_approve` | Automatic based on score threshold | Score > 90 |
| `auto_preserve` | Automatic keep local | Local-only component |
| `manual` | User explicitly selected | Interactive menu |
| `batch` | Part of "Apply All" selection | User chose batch |
| `default` | Used default recommendation | User accepted default |

---

## Backup Integration

### Backup Creation

```yaml
backup_on_merge:
  trigger: Before applying changes
  action:
    1. Create backup directory
    2. Copy all files to be modified
    3. Record file list in merge log
    4. Set expiration (90 days default)
```

### Backup Structure

```
.moai/backups/sync-2025-12-04-001/
├── manifest.json
└── files/
    ├── .claude/skills/moai-foundation-core/SKILL.md
    ├── .claude/skills/decision-logic-framework/SKILL.md
    └── ...
```

---

## Querying Logs

### Recent Merges

```python
def get_recent_merges(days: int = 7) -> List[MergeSummary]:
    """
    Get summary of recent merge operations.
    """
    index = load_index()
    cutoff = datetime.now() - timedelta(days=days)

    return [
        m for m in index.merges
        if parse_date(m.timestamp) > cutoff
    ]
```

### Component History

```python
def get_component_history(component: str) -> List[MergeDecision]:
    """
    Get all merge decisions for a specific component.
    """
    results = []

    for merge_file in glob(".moai/flow/merge-logs/merges/*.json"):
        log = load_json(merge_file)
        for decision in log.decisions:
            if decision.component == component:
                results.append({
                    "merge_id": log.merge_id,
                    "date": log.metadata.timestamp,
                    "action": decision.action,
                    "score_delta": decision.scores.delta
                })

    return sorted(results, key=lambda x: x["date"], reverse=True)
```

---

## Retention Policy

```yaml
retention:
  merge_logs: 180 days
  backups: 90 days
  index_entries: 365 days

  cleanup:
    schedule: weekly
    action:
      - Remove expired logs
      - Remove expired backups
      - Compact index
```

---

## Quick Reference

| Operation | API Function | Trigger |
|-----------|--------------|---------|
| Start log | `create_merge_log()` | Merge begins |
| Record decision | `record_decision()` | Each component |
| Finalize | `finalize_merge()` | Merge completes |
| Rollback | `rollback_merge()` | User requests |
| Query | `get_recent_merges()` | Reporting |

---

**Version**: 1.0.0 | **Status**: Production Ready | **Last Updated**: 2025-12-04
