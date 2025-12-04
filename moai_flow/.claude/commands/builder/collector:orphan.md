---
description: Create or convert to orphan branch with scoped folders only (.claude, .moai, src/moai_adk)
arguments:
  - name: branch
    description: Branch name to create/convert (e.g., feature/my-feature)
    required: true
  - name: mode
    description: "create (new orphan) or convert (existing to orphan)"
    required: false
allowed-tools: Bash, Read, Write, Glob, Grep
---

# /collector:orphan

> **Collector Scope**: `.claude/` `.moai/` `src/moai_adk/`

Create or convert a branch to orphan format with only scoped folders.

---

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `branch` | Yes | Branch name (e.g., `feature/my-skill`) |
| `mode` | No | `create` (default) or `convert` |

---

## Workflow

### Mode: create (default)

1. **Create orphan branch**
   ```bash
   git checkout --orphan {{branch}}
   git rm -rf .
   ```

2. **Checkout scoped folders from main**
   ```bash
   git checkout main -- .claude/
   git checkout main -- .moai/
   git checkout main -- src/moai_adk/
   ```

3. **Generate BRANCH-SETUP.md**
   - Use template from `collector-publish/templates/BRANCH-SETUP.template.md`
   - Fill in: FILE_COUNT, LINE_COUNT, DATE, FILE_TREE
   - Place in primary skill folder

4. **Commit and push**
   ```bash
   git add .
   git commit -m "feat(collector): create orphan branch {{branch}}

   Scoped folders only:
   - .claude/
   - .moai/
   - src/moai_adk/

   🤖 Generated with [Claude Code](https://claude.com/claude-code)

   Co-Authored-By: Claude <noreply@anthropic.com>"

   git push -u origin {{branch}}
   ```

### Mode: convert

1. **Save current branch name**
   ```bash
   CURRENT={{branch}}
   ORPHAN="${CURRENT}-orphan"
   ```

2. **Create orphan version**
   ```bash
   git checkout --orphan "$ORPHAN"
   git rm -rf .
   git checkout "$CURRENT" -- .claude/ .moai/ src/moai_adk/
   ```

3. **Generate BRANCH-SETUP.md** (same as create)

4. **Commit and push**

5. **Report conversion**
   - Original branch: `{{branch}}`
   - Orphan branch: `{{branch}}-orphan`
   - Files: {count}
   - Lines: {count}

---

## Output Format

### Success

```markdown
## Orphan Branch Created ✓

**Branch**: {{branch}}
**Mode**: create

| Metric | Value |
|--------|-------|
| Files | 45 |
| Lines | 8,234 |
| Root Folders | .claude, .moai, src |

### Structure
\`\`\`
{{branch}}/
├── .claude/
│   ├── agents/
│   ├── skills/
│   └── commands/
├── .moai/
│   └── config/
└── src/moai_adk/
    └── ...
\`\`\`

### BRANCH-SETUP.md
Created at: `.claude/skills/{{primary-skill}}/BRANCH-SETUP.md`

### Commands
\`\`\`bash
# Push to GitHub
git push -u origin {{branch}}

# Merge to main
git checkout main
git merge {{branch}} --allow-unrelated-histories
\`\`\`
```

---

## Validation

Before completing, verify:

- [ ] Only `.claude/`, `.moai/`, `src/` at root level
- [ ] BRANCH-SETUP.md created
- [ ] File/line counts accurate
- [ ] No untracked files outside scope

```bash
# Verify root contents
git ls-tree --name-only HEAD
# Expected: .claude, .moai, src (nothing else)
```

---

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| Branch already exists | Name conflict | Use different name or add `-v2` |
| No .claude/ in main | Missing source | Ensure main has scoped folders |
| Merge conflicts | Files differ | Use `--allow-unrelated-histories` |

---

## Examples

```bash
# Create new orphan branch
/collector:orphan feature/new-skill

# Convert existing branch
/collector:orphan feature/old-branch convert
```

---

## Related

- **Template**: `collector-publish/templates/BRANCH-SETUP.template.md`
- **Module**: `collector-publish/modules/orphan-branch.md`
- **Skill**: `collector-publish`

---

**Version**: 1.0.0 | **Scope**: `.claude/` `.moai/` `src/moai_adk/`
