# Module: Error Recovery

## Overview

Common Git and GitHub CLI errors during publishing and how to recover from them.

---

## Authentication Errors

### Error: `gh: Not logged in`

**Symptoms**:
```
gh: To use GitHub CLI, you need to be logged in.
```

**Recovery**:
```bash
# Interactive login
gh auth login

# Or with token
gh auth login --with-token < token.txt
```

### Error: `Permission denied (publickey)`

**Symptoms**:
```
Permission denied (publickey).
fatal: Could not read from remote repository.
```

**Recovery**:
```bash
# Check SSH key
ssh -T git@github.com

# If no key, generate one
ssh-keygen -t ed25519 -C "your_email@example.com"

# Add to GitHub
gh ssh-key add ~/.ssh/id_ed25519.pub --title "MoAI Flow"

# Or switch to HTTPS
git remote set-url origin https://github.com/superdisco-agents/moai-adk.git
```

### Error: `403 Forbidden`

**Symptoms**:
```
remote: Permission to superdisco-agents/moai-adk.git denied
```

**Recovery**:
1. Verify repo access: `gh repo view superdisco-agents/moai-adk`
2. Check token scopes: `gh auth status`
3. Refresh token: `gh auth refresh`

---

## Push Errors

### Error: `non-fast-forward`

**Symptoms**:
```
! [rejected]        flow/consolidate-2025-12-02-001 -> flow/consolidate-2025-12-02-001 (non-fast-forward)
error: failed to push some refs
```

**Cause**: Remote has changes not in local.

**Recovery**:
```bash
# Fetch latest
git fetch origin

# Rebase onto latest main
git rebase origin/main

# If conflicts, resolve them
git status
# ... fix conflicts ...
git add .
git rebase --continue

# Force push (safe for feature branches)
git push -f origin flow/consolidate-2025-12-02-001
```

### Error: `remote: Repository not found`

**Symptoms**:
```
remote: Repository not found.
fatal: repository 'https://github.com/superdisco-agents/moai-adk.git/' not found
```

**Recovery**:
```bash
# Verify remote URL
git remote -v

# Fix if wrong
git remote set-url origin git@github.com:superdisco-agents/moai-adk.git

# Verify access
gh repo view superdisco-agents/moai-adk
```

### Error: `refusing to update checked out branch`

**Symptoms**: Can't push to a branch that's checked out on remote.

**Recovery**: This shouldn't happen with feature branches. If it does:
```bash
# Create new branch with different name
git checkout -b flow/consolidate-2025-12-02-001-v2
git push -u origin flow/consolidate-2025-12-02-001-v2
```

---

## Branch Errors

### Error: Branch already exists

**Symptoms**:
```
fatal: A branch named 'flow/consolidate-2025-12-02-001' already exists.
```

**Recovery**:
```bash
# Option 1: Use next sequence number
git checkout -b flow/consolidate-2025-12-02-002 origin/main

# Option 2: Delete existing (if not pushed)
git branch -D flow/consolidate-2025-12-02-001
git checkout -b flow/consolidate-2025-12-02-001 origin/main

# Option 3: Delete existing (if pushed but not in PR)
git push origin --delete flow/consolidate-2025-12-02-001
git branch -D flow/consolidate-2025-12-02-001
git checkout -b flow/consolidate-2025-12-02-001 origin/main
```

### Error: Cannot delete branch with open PR

**Symptoms**:
```
Cannot delete branch 'flow/consolidate-2025-12-02-001' - has open pull request
```

**Recovery**:
```bash
# Close the PR first
gh pr close {pr_number}

# Then delete
git push origin --delete flow/consolidate-2025-12-02-001
```

---

## PR Errors

### Error: `pull request already exists`

**Symptoms**:
```
a]pull request already exists for superdisco-agents:flow/consolidate-2025-12-02-001
```

**Recovery**:
```bash
# Find existing PR
gh pr list --head flow/consolidate-2025-12-02-001

# Option 1: Update existing PR
gh pr edit {pr_number} --body "$(cat new_body.md)"

# Option 2: Close old, create new
gh pr close {pr_number}
gh pr create ...
```

### Error: `GraphQL: Could not resolve to a node`

**Symptoms**: PR creation fails with GraphQL error.

**Recovery**:
```bash
# Usually means branch not pushed yet
git push -u origin flow/consolidate-2025-12-02-001

# Then retry PR creation
gh pr create ...
```

### Error: `base branch does not exist`

**Symptoms**:
```
GraphQL: No such base branch (createPullRequest)
```

**Recovery**:
```bash
# Verify base branch exists
git ls-remote --heads origin main

# If using different default branch
gh pr create --base master ...
# or
gh pr create --base develop ...
```

---

## Conflict Resolution

### Merge Conflicts During Rebase

```bash
# See conflicting files
git status

# For each conflict:
# 1. Open file
# 2. Look for <<<<<<< HEAD
# 3. Resolve conflict
# 4. Save file

# Mark as resolved
git add <conflicting_file>

# Continue rebase
git rebase --continue

# If too complex, abort
git rebase --abort
```

### Content Conflicts in Skill Files

```bash
# If SKILL.md has conflicts
cat .claude/skills/builder/SKILL.md

# Look for:
<<<<<<< HEAD
# Your changes
=======
# Remote changes
>>>>>>> origin/main

# Resolution approach:
# 1. Keep structure from higher-scored version
# 2. Keep examples from more complete version
# 3. Merge unique sections from both
```

---

## Recovery Commands Reference

| Situation | Command |
|-----------|---------|
| Undo last commit (keep changes) | `git reset --soft HEAD~1` |
| Undo last commit (discard changes) | `git reset --hard HEAD~1` |
| Abort rebase | `git rebase --abort` |
| Abort merge | `git merge --abort` |
| Restore file from main | `git checkout origin/main -- <file>` |
| See what went wrong | `git reflog` |
| Recover deleted branch | `git checkout -b <branch> <sha>` |

---

## Prevention Checklist

Before publishing:
- [ ] `gh auth status` - Auth working
- [ ] `git fetch origin` - Latest from remote
- [ ] `git status` - Clean working directory
- [ ] `git log origin/main..HEAD` - Know what you're pushing
- [ ] `gh repo view` - Correct repository
