# Orphan Branch Strategy

> **Collector Scope**: `.claude/` `.moai/` `src/moai_adk/`

---

## Why Orphan Branches?

Orphan 브랜치는 **스코프된 폴더만** 포함하여:

| Benefit | Description |
|---------|-------------|
| **Clean Diff** | 정확히 MoAI 변경사항만 표시 |
| **No Noise** | node_modules, dist 등 불필요한 파일 제외 |
| **Easy Compare** | 브랜치 간 비교가 명확 |
| **Collector Optimized** | Collector 시스템과 완벽 호환 |

---

## Scope Definition

```
Orphan Branch Root/
├── .claude/           ✓ INCLUDED
│   ├── agents/
│   ├── skills/
│   ├── commands/
│   └── hooks/
├── .moai/             ✓ INCLUDED
│   ├── config/
│   ├── specs/
│   └── docs/
└── src/moai_adk/      ✓ INCLUDED
    └── ...

❌ EXCLUDED: Everything else (README.md, package.json, node_modules, etc.)
```

---

## Creating an Orphan Branch

### Step 1: Start Fresh

```bash
# Create orphan branch (no history)
git checkout --orphan feature/my-new-feature

# Remove all files from staging
git rm -rf .
```

### Step 2: Add Scoped Folders Only

```bash
# Checkout only scoped folders from main
git checkout main -- .claude/
git checkout main -- .moai/
git checkout main -- src/moai_adk/

# Verify structure
ls -la
# Should show ONLY: .claude/ .moai/ src/
```

### Step 3: Create BRANCH-SETUP.md

```bash
# Generate file count
FILE_COUNT=$(find .claude .moai src/moai_adk -type f 2>/dev/null | wc -l)

# Generate line count
LINE_COUNT=$(find .claude .moai src/moai_adk -type f -exec cat {} \; 2>/dev/null | wc -l)

# Generate file tree
FILE_TREE=$(tree -L 3 --noreport 2>/dev/null || find . -type d | head -20)

# Create BRANCH-SETUP.md from template
# (Use collector-publish template)
```

### Step 4: Commit

```bash
git add .
git commit -m "feat(collector): create orphan branch with scoped folders

Orphan branch containing:
- .claude/ (agents, skills, commands, hooks)
- .moai/ (config, specs, docs)
- src/moai_adk/ (framework source)

Files: ${FILE_COUNT}
Lines: ${LINE_COUNT}

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

### Step 5: Push

```bash
git push -u origin feature/my-new-feature
```

---

## Converting Existing Branch to Orphan

기존 브랜치를 orphan으로 변환:

```bash
# 1. 현재 브랜치 저장
CURRENT_BRANCH=$(git branch --show-current)
ORPHAN_BRANCH="${CURRENT_BRANCH}-orphan"

# 2. Orphan 버전 생성
git checkout --orphan "$ORPHAN_BRANCH"
git rm -rf .

# 3. 원래 브랜치에서 스코프된 폴더만 가져오기
git checkout "$CURRENT_BRANCH" -- .claude/ .moai/ src/moai_adk/

# 4. 커밋
git add .
git commit -m "feat: convert to orphan branch (scoped folders only)"

# 5. 푸시
git push -u origin "$ORPHAN_BRANCH"

# 6. (선택) 원래 브랜치 삭제
# git branch -D "$CURRENT_BRANCH"
# git push origin --delete "$CURRENT_BRANCH"
```

---

## Merging Orphan Branch to Main

```bash
# 1. Switch to main
git checkout main

# 2. Merge with --allow-unrelated-histories (required for orphan)
git merge feature/my-new-feature --allow-unrelated-histories

# 3. Resolve conflicts if any
# Main's files take precedence unless explicitly overriding

# 4. Commit and push
git push origin main
```

---

## Detecting Orphan Branches

브랜치가 orphan인지 확인:

```bash
# Check if branch root contains ONLY scoped folders
ROOT_CONTENTS=$(git ls-tree --name-only HEAD)

# Expected for orphan:
# .claude
# .moai
# src

# If more than these 3, NOT a proper orphan branch
echo "$ROOT_CONTENTS" | wc -l  # Should be <= 3
```

### Validation Script

```python
import subprocess

def is_orphan_branch(branch_name):
    """Check if branch only contains scoped folders."""
    result = subprocess.run(
        ['git', 'ls-tree', '--name-only', branch_name],
        capture_output=True, text=True
    )

    root_items = set(result.stdout.strip().split('\n'))
    allowed = {'.claude', '.moai', 'src'}

    return root_items.issubset(allowed)
```

---

## BRANCH-SETUP.md Location

BRANCH-SETUP.md는 브랜치의 **주요 스킬 폴더**에 위치:

```
feature/response-assistant-korean/
└── .claude/
    └── skills/
        └── moai-response-assistant/
            └── BRANCH-SETUP.md    ← HERE
```

또는 브랜치가 여러 컴포넌트를 포함하는 경우:

```
feature/collector-system/
└── .claude/
    └── skills/
        └── builder/
            └── collector-scan/
                └── BRANCH-SETUP.md
```

---

## Quick Reference

| Action | Command |
|--------|---------|
| Create orphan | `git checkout --orphan <name>` |
| Clear all files | `git rm -rf .` |
| Add scoped folders | `git checkout main -- .claude/ .moai/ src/moai_adk/` |
| Merge orphan | `git merge <orphan> --allow-unrelated-histories` |
| Check if orphan | `git ls-tree --name-only HEAD` |

---

**Version**: 1.0.0 | **Last Updated**: 2025-12-04
