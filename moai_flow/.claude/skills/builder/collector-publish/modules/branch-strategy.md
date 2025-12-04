# Module: Branch Strategy

## Overview

Branch naming conventions and management strategies for MoAI Flow publications.

---

## Branch Naming Convention

### Format

```
flow/{action}-{date}-{sequence}

Where:
- action: consolidate | hotfix | sync
- date: YYYY-MM-DD
- sequence: 001-999 (zero-padded)
```

### Examples

```
flow/consolidate-2025-12-02-001  # First consolidation of the day
flow/consolidate-2025-12-02-002  # Second consolidation of the day
flow/hotfix-2025-12-02-001       # Urgent fix
flow/sync-2025-12-02-001         # Simple sync without learning
```

---

## Branch Types

### 1. Consolidation Branch

Full MoAI Flow process: collect → learn → consolidate → publish.

```bash
# Pattern
flow/consolidate-{date}-{seq}

# Example workflow
git checkout -b flow/consolidate-2025-12-02-001 origin/main
# ... apply consolidated changes ...
git push -u origin flow/consolidate-2025-12-02-001
gh pr create --title "feat(flow): Consolidate improvements"
```

### 2. Hotfix Branch

Urgent fix that bypasses full learning process.

```bash
# Pattern
flow/hotfix-{date}-{seq}

# Example workflow
git checkout -b flow/hotfix-2025-12-02-001 origin/main
# ... apply urgent fix ...
git push -u origin flow/hotfix-2025-12-02-001
gh pr create --title "fix(flow): Urgent fix for {issue}"
```

### 3. Sync Branch

Simple sync when no analysis needed.

```bash
# Pattern
flow/sync-{date}-{seq}

# Example workflow
git checkout -b flow/sync-2025-12-02-001 origin/main
# ... copy files directly ...
git push -u origin flow/sync-2025-12-02-001
gh pr create --title "chore(flow): Sync from workspace"
```

---

## Sequence Number Generation

### Algorithm

```bash
get_next_sequence() {
  local action=$1
  local date=$2
  local prefix="flow/${action}-${date}"

  # Get existing branches with this prefix
  local existing=$(git branch -a | grep "$prefix" | wc -l)

  # Next sequence
  printf "%03d" $((existing + 1))
}

# Usage
DATE=$(date +%Y-%m-%d)
SEQ=$(get_next_sequence "consolidate" "$DATE")
BRANCH="flow/consolidate-${DATE}-${SEQ}"
```

### Collision Handling

```bash
# If branch already exists, increment
while git show-ref --verify --quiet "refs/heads/${BRANCH}"; do
  SEQ=$(printf "%03d" $((10#$SEQ + 1)))
  BRANCH="flow/consolidate-${DATE}-${SEQ}"
done
```

---

## Base Branch Strategy

### Default: main

```bash
# Always branch from latest main
git fetch origin main
git checkout -b "$BRANCH" origin/main
```

### Alternative: develop (if using GitFlow)

```bash
# For GitFlow repositories
git fetch origin develop
git checkout -b "$BRANCH" origin/develop
```

---

## Branch Protection Rules

### Recommended GitHub Settings

For `main` branch:
- [x] Require pull request before merging
- [x] Require approvals (1+)
- [x] Dismiss stale reviews on new commits
- [x] Require status checks to pass
- [ ] Require linear history (optional)

For `flow/*` branches:
- No special protection (feature branches)
- Auto-delete after merge

---

## Branch Lifecycle

```
                 Create
                   │
                   ▼
    origin/main ──────▶ flow/consolidate-2025-12-02-001
                                     │
                                     │ develop
                                     │
                                     ▼
                                   Push
                                     │
                                     ▼
                              Create PR
                                     │
                                     │ review
                                     │
                                     ▼
                            Merge to main
                                     │
                                     ▼
                           Delete branch
```

---

## Multiple Flow Branches

### Parallel Work

If multiple consolidations are in progress:

```
main
  │
  ├── flow/consolidate-2025-12-02-001 (PR #42 - in review)
  │
  └── flow/consolidate-2025-12-02-002 (PR #43 - draft)
```

### Conflict Handling

If consolidation B depends on consolidation A:

```bash
# Wait for A to merge
gh pr checks 42 --watch

# After A merges, rebase B
git checkout flow/consolidate-2025-12-02-002
git fetch origin main
git rebase origin/main
git push -f origin flow/consolidate-2025-12-02-002
```

---

## Cleanup Commands

```bash
# List all flow branches (local)
git branch | grep "flow/"

# List all flow branches (remote)
git branch -r | grep "origin/flow/"

# Delete merged local branches
git branch --merged main | grep "flow/" | xargs git branch -d

# Delete remote branches that are merged
for branch in $(git branch -r --merged origin/main | grep "origin/flow/"); do
  git push origin --delete "${branch#origin/}"
done
```
