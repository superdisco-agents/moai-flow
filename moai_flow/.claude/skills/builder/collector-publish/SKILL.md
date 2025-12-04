---
name: collector-publish
description: Publish consolidated improvements to GitHub with proper branching and PR workflow
version: 2.0.0
modularized: true
tier: 3
category: builder
last_updated: 2025-12-03
compliance_score: 95
auto_trigger_keywords:
  - publish
  - push to github
  - create pr
  - collector publish
  - collector
color: magenta
---

# Collector: Publish

**Push consolidated improvements to GitHub with proper workflow**

> **Version**: 2.0.0
> **Status**: Production Ready
> **Part of**: MoAI Flow System

---

## Collector Scope

> **SCOPE**: `.claude/` `.moai/` `src/moai_adk/` **ONLY**

| Directory | Purpose |
|-----------|---------|
| `.claude/` | Claude Code config (agents, skills, commands, hooks) |
| `.moai/` | MoAI runtime (config, specs, memory, docs) |
| `src/moai_adk/` | Framework source code |

**Excluded**: All other folders (node_modules, dist, .git, README.md, etc.)

## Quick Reference

### Purpose
Publish consolidated changes to GitHub:
- Create feature branch with meaningful name
- Commit changes with detailed messages
- Push to remote repository
- Create pull request with full context
- Support for review workflow

### Quick Invocation
```python
Skill("moai-flow-publisher")
```

### Source of Truth
```
GitHub Repository: superdisco-agents/moai-adk
All consolidations flow TO this repository
```

---

## Level 1: Publishing Workflow

### End-to-End Flow

```
Consolidated Workspace
        │
        ▼
┌───────────────────────────┐
│  1. Verify consolidation  │
│  2. Create feature branch │
│  3. Stage changes         │
│  4. Commit with context   │
│  5. Push to remote        │
│  6. Create pull request   │
│  7. Output PR link        │
└───────────┬───────────────┘
            │
            ▼
    Pull Request Ready
    for Review
```

### Branch Naming Convention

```
flow/consolidate-YYYY-MM-DD-NNN

Examples:
- flow/consolidate-2025-12-02-001
- flow/consolidate-2025-12-02-002
```

---

## Level 2: Git Operations

### Pre-Flight Checks

```bash
# 1. Verify in correct repository
git remote -v | grep "superdisco-agents/moai-adk"

# 2. Verify on main/correct base branch
git branch --show-current

# 3. Verify clean starting state
git status --porcelain | grep -v "^??" | wc -l  # Should be 0

# 4. Fetch latest from remote
git fetch origin main
```

### Create Feature Branch

```bash
# Generate branch name
BRANCH_NAME="flow/consolidate-$(date +%Y-%m-%d)-001"

# Check if branch already exists
if git show-ref --verify --quiet "refs/heads/${BRANCH_NAME}"; then
  # Increment sequence number
  BRANCH_NAME="flow/consolidate-$(date +%Y-%m-%d)-002"
fi

# Create and switch to branch
git checkout -b "$BRANCH_NAME" origin/main
```

### Stage Changes

```bash
# Stage all consolidated changes
git add .claude/skills/
git add .claude/agents/
git add .claude/commands/
git add CLAUDE.md  # If modified

# Review what's staged
git status
git diff --cached --stat
```

### Commit with Context

```bash
# Generate commit message from consolidation report
cat > /tmp/commit_msg.txt << 'EOF'
feat(flow): consolidate improvements from workspace comparison

## Summary
- Consolidated: 3 skills, 1 agent, 0 commands
- Enhanced: 2 skills with new modules
- Source: beyond-mcp workspace
- Target: moai-adk (GitHub)

## Changes

### Skills Added
- decision-logic-framework (score: 88)
- moai-connector-github (score: 82)

### Skills Merged
- builder (smart merge: workflow/ from A, scripts/ from B)

### Enhancements Applied
- moai-connector-github: added error-handling module
- builder: added integration examples

## Consolidation Details
- Collection ID: flow-2025-12-02-001
- Consolidation ID: cons-2025-12-02-001
- Learning Report: Approved with 3 must_merge, 2 should_merge

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF

git commit -F /tmp/commit_msg.txt
```

---

## Level 3: Push to Remote

### Push Command

```bash
# Push feature branch to origin
git push -u origin "$BRANCH_NAME"
```

### Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `rejected - non-fast-forward` | Branch diverged | Rebase onto latest main |
| `permission denied` | Auth issue | Run `gh auth login` |
| `remote: Repository not found` | Repo access | Check repo permissions |

### Rebase if Needed

```bash
# If push rejected
git fetch origin main
git rebase origin/main

# Resolve conflicts if any, then
git push -f origin "$BRANCH_NAME"
```

---

## Level 4: Create Pull Request

### Using GitHub CLI

```bash
# Create PR with full context
gh pr create \
  --title "feat(flow): Consolidate improvements from workspace comparison" \
  --body "$(cat << 'EOF'
## Summary

This PR consolidates improvements identified through MoAI Flow workspace comparison.

### Collection Information
- **Collection ID**: flow-2025-12-02-001
- **Source Workspace**: beyond-mcp
- **Compared Against**: moai-ir-deck

### Changes Included

#### Skills Added (2)
| Skill | Score | Rationale |
|-------|-------|-----------|
| decision-logic-framework | 88/100 | Provides structured decision-making |
| moai-connector-github | 82/100 | Better GitHub integration patterns |

#### Skills Merged (1)
| Skill | Strategy | Details |
|-------|----------|---------|
| builder | Smart merge | workflow/ from beyond-mcp + scripts/ from moai-ir-deck |

#### Enhancements Applied (2)
- **moai-connector-github**: Added `modules/error-handling.md`
- **builder**: Added integration examples section

### Learning Highlights

Patterns extracted during analysis:
1. **Visual Decision Trees**: Document decisions as flowcharts
2. **Module Organization**: Separate concerns into modules/

### Validation

- [x] All copies validated
- [x] Merges validated (no conflict markers)
- [x] Enhancements validated
- [x] No broken references
- [x] YAML frontmatter valid in all skills

### Test Plan

- [ ] Review skill documentation accuracy
- [ ] Verify examples work as documented
- [ ] Test any scripts in skills/*/scripts/

---

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)" \
  --base main \
  --head "$BRANCH_NAME"
```

### PR Labels

```bash
# Add appropriate labels
gh pr edit --add-label "moai-flow,consolidation,automated"
```

---

## Level 5: Post-Publish Actions

### Record Publication

```json
{
  "publication_id": "pub-2025-12-02-001",
  "published_at": "2025-12-02T17:00:00Z",
  "consolidation_id": "cons-2025-12-02-001",
  "collection_id": "flow-2025-12-02-001",

  "git": {
    "branch": "flow/consolidate-2025-12-02-001",
    "commit_sha": "abc123...",
    "remote": "origin",
    "repository": "superdisco-agents/moai-adk"
  },

  "pull_request": {
    "number": 42,
    "url": "https://github.com/superdisco-agents/moai-adk/pull/42",
    "title": "feat(flow): Consolidate improvements from workspace comparison",
    "state": "open"
  },

  "changes_published": {
    "skills_added": ["decision-logic-framework", "moai-connector-github"],
    "skills_merged": ["builder"],
    "skills_enhanced": ["moai-connector-github", "builder"],
    "agents_added": [],
    "commands_added": []
  }
}
```

### Notify Completion

```markdown
## Publication Complete ✓

**Pull Request**: https://github.com/superdisco-agents/moai-adk/pull/42

### Summary
- Branch: `flow/consolidate-2025-12-02-001`
- Commit: `abc123`
- Changes: 3 skills, 0 agents, 0 commands

### Next Steps
1. Review PR in GitHub
2. Request reviews if needed
3. Merge when approved
4. Clean up local branches after merge
```

---

## Level 6: Cleanup

### After PR Merged

```bash
# Switch back to main
git checkout main

# Pull latest (includes merged changes)
git pull origin main

# Delete local feature branch
git branch -d "flow/consolidate-2025-12-02-001"

# Delete remote feature branch (optional, GitHub can auto-delete)
git push origin --delete "flow/consolidate-2025-12-02-001"
```

### Cleanup Old Branches

```bash
# List all flow branches
git branch -a | grep "flow/consolidate"

# Delete branches older than 30 days (local)
git for-each-ref --sort=-committerdate --format='%(refname:short) %(committerdate:short)' refs/heads/flow/ | \
  while read branch date; do
    if [[ $(date -d "$date" +%s) -lt $(date -d "30 days ago" +%s) ]]; then
      git branch -D "$branch"
    fi
  done
```

---

## Works Well With

**Skills**:
- `moai-flow-consolidator` - Provides changes to publish
- `moai-connector-github` - GitHub CLI patterns

**Agents**:
- `moai-flow` - Orchestrates full pipeline

**Commands**:
- `/moai-flow:publish` - Triggers publication

---

## Modules

| Module | Description |
|--------|-------------|
| `branch-strategy.md` | Branch naming and management |
| `commit-messages.md` | Commit message templates |
| `pr-templates.md` | Pull request body templates |
| `error-recovery.md` | Git error handling procedures |
| `orphan-branch.md` | **Orphan branch creation and management** |

## Templates

| Template | Description |
|----------|-------------|
| `BRANCH-SETUP.template.md` | Branch documentation template for orphan branches |

---

## Quick Checklist

Before publishing:
- [ ] Consolidation completed successfully
- [ ] Audit report reviewed
- [ ] GitHub auth configured (`gh auth status`)
- [ ] On correct repository

After publishing:
- [ ] PR created successfully
- [ ] PR link saved/shared
- [ ] Publication record stored
- [ ] Local changes match remote

---

## Level 7: Orphan Branch Publishing

### Why Orphan Branches?

Orphan branches contain **ONLY** scoped folders, making:
- Clean diffs (exactly MoAI changes only)
- Easy comparisons between branches
- No noise from node_modules, dist, etc.

### Create Orphan Branch for Publishing

```bash
# 1. Create orphan branch
git checkout --orphan flow/consolidate-2025-12-04-001
git rm -rf .

# 2. Add ONLY scoped folders
git checkout main -- .claude/
git checkout main -- .moai/
git checkout main -- src/moai_adk/

# 3. Generate BRANCH-SETUP.md
# Use template from templates/BRANCH-SETUP.template.md

# 4. Commit
git add .
git commit -m "feat(collector): orphan branch with scoped folders

Scope: .claude/ .moai/ src/moai_adk/

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# 5. Push
git push -u origin flow/consolidate-2025-12-04-001
```

### BRANCH-SETUP.md Placement

Place in the primary skill folder being published:

```
flow/consolidate-2025-12-04-001/
└── .claude/
    └── skills/
        └── {primary-skill}/
            └── BRANCH-SETUP.md
```

### Quick Command

```bash
# Use /collector:orphan to automate
/collector:orphan flow/consolidate-2025-12-04-001
```

See `modules/orphan-branch.md` for detailed instructions.

---

**Version**: 2.0.0 | **Status**: Production Ready | **Last Updated**: 2025-12-04
