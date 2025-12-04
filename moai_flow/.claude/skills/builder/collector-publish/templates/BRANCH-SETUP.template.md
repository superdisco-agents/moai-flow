# {BRANCH_NAME} Branch Setup

> **Collector Scope**: `.claude/` `.moai/` `src/moai_adk/`

---

## Orphan Branch 사용 이유

이 브랜치는 **orphan branch**로 생성되어 스코프된 폴더만 포함합니다:

| Directory | Purpose |
|-----------|---------|
| `.claude/` | Claude Code 설정 (agents, skills, commands, hooks) |
| `.moai/` | MoAI 런타임 (config, specs, memory, docs) |
| `src/moai_adk/` | 프레임워크 소스 코드 |

**제외됨**: node_modules, dist, .git, README.md 등 모든 다른 폴더

---

## Branch Details

| Metric | Value |
|--------|-------|
| **Files** | {FILE_COUNT} |
| **Lines** | {LINE_COUNT} |
| **Created** | {DATE} |
| **Author** | {AUTHOR} |

---

## File Structure

```
{BRANCH_NAME}/
{FILE_TREE}
```

---

## Orphan Branch 재생성

이 브랜치를 처음부터 다시 만들려면:

```bash
# 1. Orphan 브랜치 생성 (히스토리 없이)
git checkout --orphan {BRANCH_NAME}

# 2. 모든 파일 제거
git rm -rf .

# 3. main에서 스코프된 폴더만 체크아웃
git checkout main -- .claude/ .moai/ src/moai_adk/

# 4. 커밋
git commit -m "feat({SCOPE}): {DESCRIPTION}

Orphan branch with scoped folders only:
- .claude/
- .moai/
- src/moai_adk/

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# 5. 푸시
git push -u origin {BRANCH_NAME}
```

---

## Main으로 머지

```bash
# 1. main으로 전환
git checkout main

# 2. Orphan 브랜치 머지 (--allow-unrelated-histories 필수)
git merge {BRANCH_NAME} --allow-unrelated-histories

# 3. 충돌 해결 (있는 경우)
# git add .
# git commit

# 4. 푸시
git push origin main
```

---

## Commit Scope Rules

| Prefix | 용도 | 예시 |
|--------|------|------|
| `feat({scope})` | 새 기능 | `feat(skill): add response-assistant` |
| `fix({scope})` | 버그 수정 | `fix(agent): correct workflow path` |
| `docs({scope})` | 문서 업데이트 | `docs(skill): update examples` |
| `refactor({scope})` | 리팩토링 | `refactor(skill): reorganize modules` |
| `chore({scope})` | 기타 작업 | `chore(config): update settings` |

**Scope Examples**: `skill`, `agent`, `command`, `hook`, `config`, `spec`

---

## 관련 링크

- **GitHub Branch**: https://github.com/superdisco-agents/moai-adk/tree/{BRANCH_NAME}
- **Main Repository**: https://github.com/superdisco-agents/moai-adk
- **Collector Skill**: `.claude/skills/builder/collector-*`

---

**Generated**: {DATE} | **Collector Version**: 2.0.0
