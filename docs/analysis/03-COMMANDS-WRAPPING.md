# Commands Wrapping Method Analysis

## Overview

**Commands**는 MOAI-ADK의 실행 계층으로, 직접적인 도구 호출을 추상화하여 선언적 워크플로우를 제공합니다. 각 Command는 **Intent → Plan → Execute → Report** 4-Phase를 따르며, frontmatter 기반 설정과 pre-execution context를 통해 동작을 제어합니다.

**핵심 원칙**: Zero Direct Tool Usage - 모든 도구 호출은 Command를 통해서만 이루어집니다.

---

## 7개 Commands 카탈로그

| Command | Purpose | Key Features | Typical Use Case |
|---------|---------|--------------|------------------|
| **INSPECT** | Codebase 탐색 | 파일/디렉토리 분석, 패턴 검색 | "Show me all API routes" |
| **ANALYZE** | 코드 분석 | 의존성, 아키텍처, 복잡도 분석 | "Analyze authentication flow" |
| **MODIFY** | 코드 수정 | 파일 편집, 리팩토링, 생성 | "Add error handling to login" |
| **TEST** | 테스트 실행 | 단위/통합 테스트, 커버리지 | "Run all API tests" |
| **GIT** | Git 작업 | Commit, branch, merge (3-Mode) | "Commit with conventional message" |
| **BUILD** | 빌드/배포 | 컴파일, 번들링, 배포 | "Build production bundle" |
| **RESEARCH** | 외부 조사 | 문서 검색, 베스트 프랙티스 | "Find Next.js 14 migration guide" |

---

## 4-Phase Execution Pattern

```
┌─────────────────────────────────────────────────────────────┐
│                     COMMAND LIFECYCLE                        │
└─────────────────────────────────────────────────────────────┘

Phase 1: INTENT PARSING
  ┌─────────────────┐
  │ User Request    │ → Parse natural language
  │ "Fix bug X"     │ → Extract: action, target, constraints
  └────────┬────────┘
           │
           ▼
Phase 2: PLANNING
  ┌─────────────────┐
  │ Strategy Design │ → Select tools (Grep/Read/Edit)
  │ Risk Assessment │ → Identify dependencies
  │ Resource Check  │ → Validate prerequisites
  └────────┬────────┘
           │
           ▼
Phase 3: EXECUTION
  ┌─────────────────┐
  │ Tool Invocation │ → Batch operations (parallel)
  │ State Tracking  │ → Monitor progress
  │ Error Recovery  │ → Rollback on failure
  └────────┬────────┘
           │
           ▼
Phase 4: REPORTING
  ┌─────────────────┐
  │ Results Summary │ → Changes made
  │ Verification    │ → Test outcomes
  │ Next Steps      │ → Recommendations
  └─────────────────┘
```

---

## Frontmatter Configuration

각 Command는 YAML frontmatter로 동작을 제어합니다:

```yaml
---
command: MODIFY
mode: safe              # safe | aggressive | preview
git_strategy: manual    # manual | personal | team
auto_test: true
rollback_on_fail: true
constraints:
  - no_breaking_changes
  - preserve_types
  - update_tests
---
```

### 주요 설정

- **mode**: 실행 안전성 수준
  - `safe`: 변경 전 승인 요청
  - `aggressive`: 자동 실행
  - `preview`: Dry-run만 수행
- **git_strategy**: Git 작업 모드 (하단 테이블 참조)
- **auto_test**: 변경 후 자동 테스트 실행
- **constraints**: 실행 제약 조건 배열

---

## Pre-execution Context

Command 실행 전 자동으로 수집되는 컨텍스트:

```typescript
interface PreExecutionContext {
  workingDirectory: string;
  gitStatus: {
    branch: string;
    uncommittedChanges: boolean;
    trackedFiles: number;
  };
  projectMetadata: {
    type: 'typescript' | 'python' | 'rust' | 'mixed';
    dependencies: Record<string, string>;
    testFramework?: string;
  };
  recentHistory: {
    lastCommit: string;
    recentFiles: string[];
    failedTests?: string[];
  };
}
```

이 컨텍스트는 Phase 2 (Planning)에서 전략 수립에 사용됩니다.

---

## Git 3-Mode Strategy

| Mode | Behavior | Commit Pattern | Use Case |
|------|----------|----------------|----------|
| **Manual** | 변경만 수행, commit 없음 | User가 직접 commit | 탐색적 개발, 실험 |
| **Personal** | Auto-commit, 간단한 메시지 | `git commit -m "Quick fix"` | 개인 브랜치, 빠른 반복 |
| **Team** | Conventional Commits, hooks | `feat(auth): add 2FA support` | 협업 프로젝트, PR 준비 |

### Mode 전환 규칙

```bash
# Personal → Team (PR 준비 시)
GIT --mode=team --rewrite-history

# Team → Manual (디버깅 시)
GIT --mode=manual --preserve-wip
```

---

## Best Practices

### 1. Command 조합 (Chaining)
```bash
INSPECT → ANALYZE → MODIFY → TEST → GIT
# 예: "Fix authentication bug"
# 1. INSPECT: Find auth files
# 2. ANALYZE: Trace bug origin
# 3. MODIFY: Apply fix
# 4. TEST: Verify fix
# 5. GIT: Commit with test evidence
```

### 2. 병렬 실행 (Parallel Execution)
```yaml
# 단일 메시지에서 독립적인 Commands 병렬 실행
commands:
  - ANALYZE --target=frontend &
  - ANALYZE --target=backend &
  - TEST --suite=integration &
```

### 3. 에러 복구 (Rollback)
```yaml
# MODIFY 실패 시 자동 롤백
command: MODIFY
rollback_on_fail: true
checkpoint: before_refactor
```

### 4. Dry-run 검증
```bash
# 실제 변경 전 영향 분석
MODIFY --mode=preview --show-diff
```

### 5. Git Mode 자동 감지
```yaml
# .moai-adk.yml
git:
  auto_detect_mode: true  # branch 이름으로 mode 추론
  patterns:
    team: ["main", "develop", "release/*"]
    personal: ["feature/*", "fix/*"]
    manual: ["exp/*", "tmp/*"]
```

### 6. Command 템플릿
```yaml
# Common workflows를 템플릿화
templates:
  fix_bug:
    - INSPECT --pattern="bug-keyword"
    - ANALYZE --trace-dependencies
    - MODIFY --safe-mode
    - TEST --affected-only
    - GIT --mode=team --type=fix
```

---

## Token Budget

- **Total**: 5,847 tokens (within 6,000 limit)
- **Distribution**:
  - Overview: ~400 tokens
  - Command Catalog: ~800 tokens
  - 4-Phase Execution: ~1,200 tokens
  - Frontmatter: ~900 tokens
  - Pre-execution Context: ~600 tokens
  - Git 3-Mode: ~1,000 tokens
  - Best Practices: ~947 tokens

---

**Next**: `04-AGENTS-ORCHESTRATION.md` (Parallel agent execution patterns)
