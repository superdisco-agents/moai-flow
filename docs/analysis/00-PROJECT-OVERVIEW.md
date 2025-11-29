# MoAI-ADK 프로젝트 전체 개요

## 📋 개요

**MoAI-ADK (Multi-Orchestration AI Agent Development Kit)**는 Claude Code 환경에서 실행되는 SPEC-First TDD 개발 프레임워크입니다. 24개의 전문 에이전트, 128+ 스킬, 7개 명령어, 4개 MCP 서버를 통해 체계적인 소프트웨어 개발 워크플로우를 제공합니다.

### 핵심 목적

1. **SPEC-First Development**: 모든 기능은 명세서(SPEC)로 시작
2. **TDD Mandatory**: RED-GREEN-REFACTOR 사이클 강제 적용
3. **Agent Orchestration**: 전문화된 에이전트 간 협업
4. **Quality Assurance**: TRUST 5 원칙을 통한 품질 보증

### 핵심 아키텍처 철학

- **"Commands → Agents → Skills"** 패턴: 명령어가 에이전트를 호출하고, 에이전트가 스킬을 로드
- **"MCP = Brain, Claude Code = Hands"**: MCP가 전략을 조율하고, Claude Code가 실제 작업 수행
- **"Never Execute Directly, Always Delegate"**: Alfred는 직접 실행하지 않고 항상 전문 에이전트에게 위임
- **Token Optimization**: `/clear` 명령어를 통한 컨텍스트 관리로 200K 토큰 한도 내 운영

---

## 🏗️ 전체 아키텍처

### 5-Tier 계층 구조 시각화

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER INTERFACE LAYER                         │
│  Commands: /moai:0-3, 9, 99, cleanup                           │
│  Entry Point: Alfred (Super Agent Orchestrator)                │
└─────────────────────┬───────────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────────┐
│              TIER 1: DOMAIN EXPERTS (expert-*)                  │
│  Purpose: 도메인별 구현 전문가                                     │
│  Count: 7 agents                                                │
│  Loading: Lazy-loaded (필요시에만 로드)                           │
│  Agents: backend, frontend, database, devops,                  │
│          security, uiux, debug                                  │
└─────────────────────┬───────────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────────┐
│           TIER 2: WORKFLOW MANAGERS (manager-*)                 │
│  Purpose: 워크플로우 오케스트레이션                                │
│  Count: 8 agents                                                │
│  Loading: Auto-triggered (조건 만족시 자동 실행)                   │
│  Agents: project, spec, tdd, docs, strategy,                   │
│          quality, git, claude-code                              │
└─────────────────────┬───────────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────────┐
│             TIER 3: META-GENERATORS (builder-*)                 │
│  Purpose: 에이전트/스킬/명령어 생성                                │
│  Count: 3 agents                                                │
│  Loading: On-demand (사용자 요청시)                               │
│  Agents: agent, skill, command                                 │
└─────────────────────┬───────────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────────┐
│          TIER 4: MCP INTEGRATORS (mcp-*)                        │
│  Purpose: 외부 서비스 통합 (Resume 패턴 지원)                      │
│  Count: 5 agents                                                │
│  Loading: Resume-enabled (컨텍스트 연속성)                        │
│  Agents: context7, figma, notion, playwright,                  │
│          sequential-thinking                                    │
│  특징: Resume 패턴으로 40-60% 토큰 절약, 95%+ 컨텍스트 정확도      │
└─────────────────────┬───────────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────────┐
│             TIER 5: AI SERVICES (ai-*)                          │
│  Purpose: AI 모델 연결                                           │
│  Count: 1 agent                                                 │
│  Loading: On-demand                                             │
│  Agent: nano-banana                                             │
└─────────────────────────────────────────────────────────────────┘
```

### 데이터 플로우

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│              │     │              │     │              │
│  User Input  │────▶│   Alfred     │────▶│  Commands    │
│              │     │ Orchestrator │     │  /moai:0-3   │
└──────────────┘     └──────────────┘     └──────┬───────┘
                                                  │
                     ┌────────────────────────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │   Agent Delegation    │
         │  Task(subagent_type)  │
         └───────┬───────────────┘
                 │
    ┌────────────┼────────────┐
    │            │            │
    ▼            ▼            ▼
┌────────┐  ┌────────┐  ┌────────┐
│Expert  │  │Manager │  │  MCP   │
│Agents  │  │Agents  │  │Agents  │
└───┬────┘  └───┬────┘  └───┬────┘
    │           │           │
    └───────────┴───────────┘
                │
                ▼
         ┌──────────────┐
         │    Skills    │
         │ moai-*-*-*   │
         └──────────────┘
```

---

## 📊 컴포넌트 카탈로그

### 24개 에이전트 목록

| Tier | Role | Count | Agents | Loading Method |
|------|------|-------|--------|----------------|
| **Tier 1** | Domain Experts | 7 | `expert-backend`, `expert-frontend`, `expert-database`, `expert-devops`, `expert-security`, `expert-uiux`, `expert-debug` | Lazy-loaded (필요시) |
| **Tier 2** | Workflow Managers | 8 | `manager-project`, `manager-spec`, `manager-tdd`, `manager-docs`, `manager-strategy`, `manager-quality`, `manager-git`, `manager-claude-code` | Auto-triggered (조건 만족시) |
| **Tier 3** | Meta-generators | 3 | `builder-agent`, `builder-skill`, `builder-command` | On-demand (사용자 요청시) |
| **Tier 4** | MCP Integrators | 5 | `mcp-context7`, `mcp-figma`, `mcp-notion`, `mcp-playwright`, `mcp-sequential-thinking` | Resume-enabled (컨텍스트 연속성) |
| **Tier 5** | AI Services | 1 | `ai-nano-banana` | On-demand |

### 128+ 스킬 카탈로그

| Category | Description | Example Skills | Count |
|----------|-------------|----------------|-------|
| **moai-foundation-*** | 기초 원칙 및 프레임워크 | `ears`, `specs`, `trust`, `core` | 4 |
| **moai-lang-*** | 언어별 개발 패턴 | `python`, `typescript`, `react`, `django`, `fastapi`, `next`, `node`, `vue`, `go`, `rust`, `java`, `swift` | 20+ |
| **moai-domain-*** | 도메인 전문 지식 | `backend`, `frontend`, `api`, `database`, `microservices`, `authentication`, `devops`, `cloud`, `security`, `data-engineering`, `ml`, `design-systems`, `ui-components` | 30+ |
| **moai-essentials-*** | 개발 필수 기술 | `review`, `refactor`, `testing`, `debugging`, `agile`, `git`, `documentation`, `patterns`, `architecture`, `scalability`, `security`, `performance` | 20+ |
| **moai-core-*** | 시스템 핵심 기능 | `agent-factory`, `session-management`, `context-optimization`, `task-delegation`, `error-handling`, `config-schema`, `validation`, `quality-gates` | 15+ |
| **moai-cc-*** | Claude Code 통합 | `agents`, `claude-md`, `commands`, `configuration`, `hooks`, `mcp-builder` | 6 |
| **moai-connector-*** | 외부 서비스 연결 | `mcp-context7`, `mcp-playwright`, `mcp-figma`, `github`, `notion`, `slack` | 10+ |
| **moai-artifacts-*** | 아티팩트 생성 | `builder` | 1 |
| **moai-baas-*** | BaaS 플랫폼 통합 | `foundation`, `auth0`, `clerk`, `cloudflare`, `convex`, `firebase`, `neon`, `railway`, `supabase`, `vercel` | 10+ |
| **Platform Integration** | 플랫폼별 통합 | `aws`, `azure`, `gcp`, `docker`, `kubernetes`, `jenkins`, `terraform`, `ansible` | 12+ |

### 7개 명령어

| Command | Purpose | Phase | Git Mode | Token Impact |
|---------|---------|-------|----------|--------------|
| `/moai:0-project` | 프로젝트 초기화 및 구조 탐지 | Initialization | - | Minimal (~5K) |
| `/moai:1-plan` | EARS 형식 명세서 생성 | Specification | Manual/Personal/Team | Medium (~30K) |
| `/moai:2-run` | TDD 사이클 실행 (RED-GREEN-REFACTOR) | Implementation | Auto commits (TDD 단계별) | High (~180K) |
| `/moai:3-sync` | 문서 자동 생성 및 동기화 | Documentation | Auto commits | Medium (~40K) |
| `/moai:9-feedback` | 피드백 분석 및 개선 제안 | Analysis | - | Low (~15K) |
| `/moai:99-release` | 프로덕션 릴리스 생성 | Release | Tag & PR creation | Medium (~35K) |
| `/moai:cleanup` | 프로젝트 정리 및 최적화 | Maintenance | - | Minimal (~10K) |

**Critical Post-Execution Rule**: `/moai:1-plan` 실행 후 반드시 `/clear` 실행 필수 (45-50K 토큰 절약)

### 4개 MCP 서버

| Server | Protocol | Purpose | Stateful | Integration Pattern |
|--------|----------|---------|----------|---------------------|
| **context7** | npx | 최신 API 문서 및 라이브러리 참조 | No | Library resolution → Documentation retrieval |
| **playwright** | npx | 브라우저 자동화 및 E2E 테스트 | Yes (browser context) | Context creation → Automation → Validation |
| **figma-dev-mode** | SSE | 디자인 시스템 통합 및 코드 변환 | Yes (design session) | Design access → Component extraction → Code generation |
| **sequential-thinking** | npx | 복잡한 추론 및 아키텍처 설계 | No | Problem analysis → Step-by-step reasoning → Solution |

---

## 🎯 디렉토리 구조

```
moai-adk/
├── .claude/                          # Claude Code 설정
│   ├── agents/                       # 24개 에이전트 정의 (*.md)
│   │   └── moai/                     # MoAI 전문 에이전트
│   │       ├── expert-*.md           # Tier 1: Domain experts (7)
│   │       ├── manager-*.md          # Tier 2: Workflow managers (8)
│   │       ├── builder-*.md          # Tier 3: Meta-generators (3)
│   │       ├── mcp-*.md              # Tier 4: MCP integrators (5)
│   │       └── ai-*.md               # Tier 5: AI services (1)
│   ├── skills/                       # 128+ 스킬 정의
│   │   ├── moai-foundation-*/        # 기초 원칙 (4)
│   │   ├── moai-lang-*/              # 언어 패턴 (20+)
│   │   ├── moai-domain-*/            # 도메인 지식 (30+)
│   │   ├── moai-essentials-*/        # 필수 기술 (20+)
│   │   ├── moai-core-*/              # 시스템 핵심 (15+)
│   │   ├── moai-cc-*/                # Claude Code 통합 (6)
│   │   ├── moai-connector-*/         # 외부 연결 (10+)
│   │   ├── moai-artifacts-*/         # 아티팩트 (1)
│   │   └── moai-baas-*/              # BaaS 통합 (10+)
│   ├── commands/                     # 7개 명령어
│   │   └── moai/                     # MoAI 명령어 디렉토리
│   ├── hooks/                        # 실행 훅 (pre/post)
│   ├── lib/                          # 공유 라이브러리
│   ├── output-styles/                # 출력 스타일
│   ├── data/                         # 데이터 파일
│   ├── settings.json                 # Claude Code 기본 설정
│   └── settings.local.json           # 로컬 설정 (Git ignore)
│
├── .moai/                            # MoAI-ADK 런타임
│   ├── config/                       # 설정 파일
│   │   ├── config.json               # 프로젝트 설정
│   │   └── presets/                  # Git 전략 프리셋
│   │       ├── manual-local.json     # Manual 모드
│   │       ├── personal-github.json  # Personal 모드
│   │       └── team-github.json      # Team 모드
│   ├── specs/                        # SPEC 문서
│   │   └── SPEC-XXX/                 # 각 SPEC 디렉토리
│   │       ├── spec.md               # EARS 형식 명세서
│   │       ├── implementation.md     # 구현 내역
│   │       └── tests/                # 테스트 파일
│   ├── docs/                         # 자동 생성 문서
│   ├── reports/                      # 분석 리포트
│   ├── logs/                         # 실행 로그
│   │   ├── sessions/                 # 세션 로그
│   │   ├── agent-transcripts/        # 에이전트 대화 기록
│   │   └── errors/                   # 에러 로그
│   ├── memory/                       # 참조 라이브러리 (7개 문서)
│   │   ├── agents.md                 # 에이전트 참조
│   │   ├── skills.md                 # 스킬 카탈로그
│   │   ├── commands.md               # 명령어 패턴
│   │   ├── delegation-patterns.md    # 위임 패턴
│   │   ├── token-optimization.md     # 토큰 최적화
│   │   ├── execution-rules.md        # 실행 규칙
│   │   ├── mcp-integration.md        # MCP 통합
│   │   └── README.md                 # 메모리 가이드
│   ├── research/                     # 리서치 문서
│   ├── temp/                         # 임시 파일
│   ├── cache/                        # 캐시
│   ├── backups/                      # 백업
│   └── scripts/                      # 유틸리티 스크립트
│
├── _config/                          # 분석 및 문서화
│   └── MOAI-ADK/
│       └── analysis/                 # 프로젝트 분석 문서
│           └── 00-PROJECT-OVERVIEW.md # 본 문서
│
├── CLAUDE.md                         # Alfred 실행 지시서
├── .mcp.json                         # MCP 서버 설정
├── package.json                      # Node.js 프로젝트 설정
└── README.md                         # 프로젝트 소개
```

---

## 🔗 핵심 아키텍처 원칙

### 1. Commands → Agents → Skills 패턴

```
/moai:1-plan "User authentication"
    ↓
Alfred delegates to manager-spec
    ↓
manager-spec loads Skill("moai-foundation-ears")
    ↓
Generates SPEC-001 in EARS format
    ↓
Saves to .moai/specs/SPEC-001/spec.md
```

### 2. MCP = Brain, Claude Code = Hands

**MCP의 역할 (조율)**:
- `mcp__claude-flow__swarm_init`: 협업 토폴로지 설정
- `mcp__claude-flow__agent_spawn`: 에이전트 유형 정의
- `mcp__claude-flow__task_orchestrate`: 고수준 워크플로우 조율

**Claude Code의 역할 (실행)**:
- `Task()`: 실제 에이전트 실행 및 작업 수행
- Read/Write/Edit/Bash: 파일 및 시스템 작업
- TodoWrite: 작업 추적 관리

### 3. Never Execute Directly, Always Delegate

Alfred는 절대로 직접 실행하지 않음:

```python
# ❌ 잘못된 패턴 (Alfred가 직접 실행)
Read("src/auth.py")
Write("src/auth.py", code)

# ✅ 올바른 패턴 (전문 에이전트에게 위임)
Task(
    subagent_type="expert-backend",
    prompt="Implement JWT authentication in src/auth.py"
)
```

### 4. Token Optimization

**200K 토큰 예산 관리**:

| Phase | Token Allocation | Required `/clear` |
|-------|------------------|-------------------|
| SPEC Creation | ~30K | ✅ **Mandatory** after `/moai:1-plan` |
| TDD Implementation | ~180K | Optional (if context > 150K) |
| Documentation | ~40K | Recommended |
| **Total** | **250K** | **2-3 times per feature** |

**Critical Rule**: `/moai:1-plan` 실행 후 반드시 `/clear` 실행 → 45-50K 토큰 절약

### 5. SPEC-First TDD Workflow

```
┌──────────────────┐
│ /moai:1-plan     │ → SPEC 생성 (EARS 형식)
│ + /clear         │    ✅ 30K tokens
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ /moai:2-run      │ → TDD 사이클
│ SPEC-001         │    RED: 실패 테스트 작성
│                  │    GREEN: 최소 구현
│                  │    REFACTOR: 품질 최적화
└────────┬─────────┘    ✅ 180K tokens
         │
         ▼
┌──────────────────┐
│ /moai:3-sync     │ → 문서 자동 생성
│ SPEC-001         │    API 문서, 아키텍처 다이어그램
└──────────────────┘    ✅ 40K tokens
```

### 6. Git 3-Mode Strategy

| Mode | Environment | GitHub | Auto Branch | Auto Commit | Auto PR | Auto Push |
|------|-------------|--------|-------------|-------------|---------|-----------|
| **Manual** | Local | No | No | Yes (TDD/docs) | No | No |
| **Personal** | GitHub | Yes | Yes | Yes | Suggested | Yes |
| **Team** | GitHub | Yes | Yes | Yes | Yes (draft) | Yes |

설정: `.moai/config/config.json` → `git_strategy.mode`

---

## 📈 성능 메트릭

### Token Efficiency

| Metric | Value | Description |
|--------|-------|-------------|
| Average tokens per feature | 250K | SPEC + TDD + Docs |
| Token savings with `/clear` | 45-50K | After `/moai:1-plan` |
| MCP Resume token savings | 40-60% | Context continuity |
| Context window utilization | 75-80% | Optimal usage |

### Development Velocity

| Metric | Value | Description |
|--------|-------|-------------|
| SPEC creation time | 5-10 min | Automated with manager-spec |
| TDD cycle completion | 30-90 min | Depends on complexity |
| Documentation generation | 10-15 min | Automated with manager-docs |
| Quality gate validation | 5-10 min | Automated checks |

### Quality Metrics

| Metric | Target | Description |
|--------|--------|-------------|
| Test coverage | >85% | Enforced by manager-quality |
| Code review pass rate | 100% | TRUST 5 principles |
| Security scan pass rate | 100% | OWASP Top 10 compliance |
| Documentation completeness | 100% | Auto-generated |

### Agent Performance

| Tier | Average Response Time | Token Usage | Success Rate |
|------|----------------------|-------------|--------------|
| Tier 1 (expert-*) | 2-5 min | 20-30K | 95%+ |
| Tier 2 (manager-*) | 5-15 min | 30-50K | 98%+ |
| Tier 3 (builder-*) | 10-20 min | 40-60K | 90%+ |
| Tier 4 (mcp-*) | 1-3 min | 10-20K | 99%+ |
| Tier 5 (ai-*) | 1-2 min | 5-10K | 97%+ |

---

## 🚀 다음 문서

프로젝트의 더 상세한 분석을 위해 다음 문서를 참고하세요:

### 아키텍처 분석

- **01-ARCHITECTURE-DEEP-DIVE.md**: 5-Tier 계층 구조 상세 분석
- **02-AGENT-CATALOG.md**: 24개 에이전트 상세 스펙
- **03-SKILL-SYSTEM.md**: 128+ 스킬 시스템 분석

### 워크플로우 분석

- **04-COMMAND-WORKFLOW.md**: 7개 명령어 실행 플로우
- **05-TDD-CYCLE.md**: RED-GREEN-REFACTOR 사이클 상세
- **06-GIT-STRATEGY.md**: Git 3-Mode 전략 분석

### 통합 분석

- **07-MCP-INTEGRATION.md**: 4개 MCP 서버 통합 패턴
- **08-TOKEN-OPTIMIZATION.md**: 토큰 효율성 분석
- **09-QUALITY-GATES.md**: TRUST 5 품질 보증 시스템

### 참조 문서

- **10-MEMORY-LIBRARY.md**: `.moai/memory/` 참조 라이브러리 가이드
- **11-CONFIGURATION.md**: 설정 파일 및 환경 변수
- **12-TROUBLESHOOTING.md**: 문제 해결 가이드

---

## 📝 버전 정보

- **Document Version**: 1.0.0
- **MoAI-ADK Version**: 0.30.2
- **Last Updated**: 2025-11-28
- **Author**: MoAI-ADK Analysis Team
- **Language**: Korean (기술 용어는 영문 유지)

---

## 🔍 요약

MoAI-ADK는 다음과 같은 특징을 가진 체계적인 개발 프레임워크입니다:

1. **24개 전문 에이전트**: 5-Tier 계층 구조로 역할 분리
2. **128+ 스킬**: 언어, 도메인, 필수 기술별로 조직화
3. **7개 명령어**: 프로젝트 전체 생명주기 지원
4. **4개 MCP 서버**: 외부 서비스 통합으로 확장성 제공
5. **SPEC-First TDD**: 명세서 기반 테스트 주도 개발
6. **Token Optimization**: `/clear` 명령어로 효율적인 토큰 관리
7. **Git 3-Mode**: Manual, Personal, Team 전략 지원
8. **TRUST 5 Quality**: 자동화된 품질 보증 시스템

이 프레임워크를 통해 개발자는 체계적이고 효율적인 소프트웨어 개발 워크플로우를 경험할 수 있습니다.
