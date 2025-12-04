# Module: Report Format

## Overview

JSON schema and format specification for MoAI Flow collection reports.

---

## Collection Report Schema

```json
{
  "$schema": "moai-flow-collection-v1",
  "collection_id": "flow-YYYY-MM-DD-NNN",
  "created_at": "ISO8601 datetime",
  "created_by": "moai-flow-collector v1.0.0",

  "workspaces": {
    "a": {
      "id": "workspace-name",
      "path": "/absolute/path",
      "scanned_at": "ISO8601 datetime"
    },
    "b": {
      "id": "workspace-name",
      "path": "/absolute/path",
      "scanned_at": "ISO8601 datetime"
    }
  },

  "summary": {
    "total_differences": "integer",
    "skills_diff": "integer",
    "agents_diff": "integer",
    "commands_diff": "integer",
    "newer_workspace": "a|b|tie",
    "recommendation": "string"
  },

  "comparisons": {
    "skills": {
      "only_in_a": ["array of skill names"],
      "only_in_b": ["array of skill names"],
      "in_both": ["array of skill names"],
      "in_both_different": ["array of skill names"]
    },
    "agents": { /* same structure */ },
    "commands": { /* same structure */ }
  },

  "files": {
    "claude_md": {
      "a_modified": "ISO8601",
      "b_modified": "ISO8601",
      "newer": "a|b|same",
      "a_lines": "integer",
      "b_lines": "integer"
    }
  },

  "metadata": {
    "a_moai_version": "semver",
    "b_moai_version": "semver",
    "a_git_commit": "sha",
    "b_git_commit": "sha"
  }
}
```

---

## Collection ID Format

```
flow-YYYY-MM-DD-NNN

Where:
- YYYY = 4-digit year
- MM = 2-digit month (01-12)
- DD = 2-digit day (01-31)
- NNN = 3-digit sequence (001-999)

Example: flow-2025-12-02-001
```

---

## File Storage

```
.moai/flow/collections/{collection_id}/
├── scan-a.json        # Full scan of workspace A
├── scan-b.json        # Full scan of workspace B
├── comparison.json    # Comparison results
└── metadata.json      # Collection metadata
```

---

## Integration Points

| Consumer | Uses | For |
|----------|------|-----|
| moai-flow-learner | comparison.json | Analyzing differences |
| moai-flow-consolidator | scan-*.json | Getting source paths |
| moai-flow-publisher | metadata.json | Commit messages |
