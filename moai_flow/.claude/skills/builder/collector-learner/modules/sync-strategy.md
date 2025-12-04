# Sync Strategy Module

**Intelligent sync decision rules for multi-source comparison**

> **Version**: 1.0.0
> **Part of**: collector-learner skill
> **Last Updated**: 2025-12-04

---

## Core Principle

```
NEVER assume remote = better
NEVER assume newer = better
ALWAYS score both sides
ONLY update what's PROVEN better
PRESERVE local innovations
```

---

## Decision Matrix

| Scenario | Condition | Action |
|----------|-----------|--------|
| **Local Better** | local.score > remote.best + 10 | PRESERVE local |
| **Remote Better** | remote.best > local.score + 10 | UPDATE from remote |
| **Close Scores** | |local - remote| <= 10 | SMART MERGE |
| **Local Innovation** | local.score > 90 AND remote < 70 | PROPOSE upstream |
| **Same Quality** | scores equal, no unique features | SKIP |

---

## Sync Actions

### 1. PRESERVE

**When**: Local is significantly better than all remote sources.

```yaml
action: PRESERVE
condition: local.score > remote.best_score + 10
result:
  - Keep local version unchanged
  - Log: "Local version is superior"
  - Flag: Consider upstream contribution
```

**Example**:
```
collector-scan:
  local: 88/100
  main: (doesn't exist)
  feature/*: (doesn't exist)
  → PRESERVE (local-only innovation)
```

### 2. UPDATE

**When**: Remote (any branch) is significantly better.

```yaml
action: UPDATE
condition: remote.best_score > local.score + 10
result:
  - Replace local with remote.best_branch version
  - Preserve local unique features (if any)
  - Log: "Updated from {branch}"
```

**Example**:
```
moai-foundation-core:
  local: 72/100
  main: 75/100
  feature/SPEC-first: 91/100 ← BEST
  → UPDATE from feature/SPEC-first
```

### 3. SMART_MERGE

**When**: Scores are within 10 points, both have value.

```yaml
action: SMART_MERGE
condition: |local.score - remote.best_score| <= 10
result:
  - Use higher-scored version as base
  - Merge unique features from other source
  - Log: "Merged best of both"
```

**Example**:
```
builder-skill:
  local: 80/100 (has: uv-scripts)
  main: 78/100 (has: workflow-integration)
  → SMART_MERGE
    base: local (higher score)
    add: workflow-integration from main
```

### 4. ENHANCE

**When**: Remote has unique features local lacks.

```yaml
action: ENHANCE
condition: remote has features AND local.score >= remote.score
result:
  - Keep local base
  - Add remote's unique features
  - Log: "Enhanced with remote features"
```

**Example**:
```
decision-logic-framework:
  local: 85/100 (modules: 4)
  main: 78/100 (modules: 5, has: rule-command-creation.md)
  → ENHANCE
    keep: local base
    add: rule-command-creation.md from main
```

### 5. CONTRIBUTE

**When**: Local is a significant innovation.

```yaml
action: CONTRIBUTE
condition: local.score > 90 AND (remote.best_score < 70 OR !remote.exists)
result:
  - Keep local unchanged
  - Generate PR description
  - Flag: "Ready for upstream contribution"
```

**Example**:
```
collector-orchestrator:
  local: 92/100 (full orchestrator pattern)
  main: (single agent, score ~60)
  → CONTRIBUTE
    pr_title: "feat: Add collector orchestrator system"
    pr_body: "Replaces single agent with 6-agent orchestration..."
```

### 6. SKIP

**When**: No meaningful difference.

```yaml
action: SKIP
condition:
  - scores within 5 points AND
  - no unique features AND
  - no version difference
result:
  - No changes
  - Log: "No action needed"
```

---

## Multi-Source Priority

When multiple remote branches exist, prioritize:

```
1. Branch with highest adjusted score
2. If tied:
   a. Prefer branches merged to main
   b. Prefer more recently updated
   c. Prefer default branch (main)
3. Skip stale branches (>90 days inactive)
```

### Branch Scoring Adjustments

| Branch State | Score Modifier |
|--------------|----------------|
| Is `main` branch | +5 |
| Updated < 7 days | +3 |
| CI passing | +5 |
| Merged to main | +10 |
| Stale > 90 days | -10 |

---

## Feature Preservation Rules

### When Updating from Remote

Always preserve local unique features:

```yaml
update_with_preservation:
  1. Identify local_unique_features:
     - modules/ files not in remote
     - scripts/ files not in remote
     - workflows/ not in remote

  2. Apply remote base

  3. Restore local_unique_features:
     - Copy preserved files back
     - Update SKILL.md "Modules" section
     - Update any references
```

### When Keeping Local

Add valuable remote features:

```yaml
enhance_with_remote:
  1. Identify remote_unique_features:
     - modules/ files not in local
     - Better examples
     - Additional integrations

  2. Keep local base

  3. Add remote_unique_features:
     - Copy new files
     - Merge SKILL.md sections
     - Update version
```

---

## Conflict Resolution

### Same File, Different Changes

```yaml
file_conflict:
  detection: Both sources modified same file

  resolution_order:
    1. If one has frontmatter, other doesn't → keep with frontmatter
    2. If version differs → keep higher version
    3. If structure differs → prefer modular structure
    4. If content differs → smart merge (AI analysis)
    5. If irreconcilable → flag for manual review
```

### Structural Conflicts

```yaml
structure_conflict:
  detection: Different file/folder organization

  resolution:
    - Prefer: modules/ over flat files
    - Prefer: scripts/ with proper naming
    - Prefer: workflows/ with TOON
    - If incompatible → SKIP (needs manual decision)
```

---

## Output Schema

### Sync Strategy Report

```json
{
  "collection_id": "flow-2025-12-04-001",
  "strategy_generated_at": "2025-12-04T15:00:00Z",

  "summary": {
    "preserve_count": 5,
    "update_count": 3,
    "smart_merge_count": 2,
    "enhance_count": 1,
    "contribute_count": 2,
    "skip_count": 10
  },

  "actions": [
    {
      "component": "collector-scan",
      "action": "PRESERVE",
      "local_score": 88,
      "remote_best": null,
      "reasoning": "Local-only innovation, no remote equivalent"
    },
    {
      "component": "moai-foundation-core",
      "action": "UPDATE",
      "local_score": 72,
      "remote_best": 91,
      "best_branch": "feature/SPEC-first-builders",
      "preserve_features": ["collector-integration"],
      "reasoning": "Remote significantly better (+19 points)"
    },
    {
      "component": "builder-skill",
      "action": "SMART_MERGE",
      "local_score": 80,
      "remote_best": 78,
      "best_branch": "main",
      "merge_features": ["workflow-integration"],
      "reasoning": "Scores within 10 points, both have unique value"
    }
  ],

  "contributions": [
    {
      "component": "collector-orchestrator",
      "action": "CONTRIBUTE",
      "local_score": 92,
      "remote_score": 60,
      "pr_draft": {
        "title": "feat: Add collector orchestrator system",
        "body": "...",
        "target_branch": "main"
      }
    }
  ]
}
```

---

## Quick Reference

### Decision Flowchart

```
Component to sync
       │
       ▼
┌─────────────────────┐
│ Score local version │
│ Score all remotes   │
└──────────┬──────────┘
           │
     ┌─────┴─────┐
     │           │
  Remote      Local
  exists?     only?
     │           │
     YES         └─► PRESERVE
     │               (+ CONTRIBUTE if score > 90)
     ▼
┌─────────────────────┐
│ Compare scores      │
│ local vs best_remote│
└──────────┬──────────┘
           │
     ┌─────┼─────┐
     │     │     │
  Local  Close  Remote
  better        better
  (+10)  (±10)  (+10)
     │     │     │
     ▼     ▼     ▼
PRESERVE SMART  UPDATE
         MERGE
```

---

**Version**: 1.0.0 | **Status**: Production Ready | **Last Updated**: 2025-12-04
