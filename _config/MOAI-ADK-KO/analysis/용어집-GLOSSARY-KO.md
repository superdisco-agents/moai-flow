# MOAI-ADK 기술 용어집 (Technical Glossary)

> MOAI Agent Development Kit의 핵심 개념과 용어 정리

## A-M 핵심 용어

### Agent (에이전트)
**정의**: 특정 작업을 자율적으로 수행하는 AI 기반 실행 단위. MCP 서버와 통신하며 도구를 활용해 목표를 달성합니다.
**예시**: `Task("Research agent", "분석 수행", "researcher")` - 연구 작업을 수행하는 에이전트 생성

### Auto-load (자동 로드)
**정의**: YAML 파일의 `autoLoad: true` 설정으로 Claude Code 시작 시 자동으로 스킬이나 명령어를 로드하는 기능.
**예시**: `.claude/skills/my-skill.yaml`에서 `autoLoad: true` 설정 시 자동 활성화

### Command (명령어)
**정의**: `/` 접두사로 시작하는 실행 가능한 작업 지시. `.claude/commands/` 디렉토리에 Markdown 파일로 저장됩니다.
**예시**: `/prime` - 프로젝트 컨텍스트 로드 명령어

### Context (컨텍스트)
**정의**: AI가 작업 수행 시 참조하는 프로젝트 정보, 파일, 설정의 집합. CLAUDE.md와 skill YAML에 정의됩니다.
**예시**: `context: ["README.md", "src/**/*.ts"]` - 타입스크립트 파일을 컨텍스트로 포함

### Delegation (위임)
**정의**: 상위 에이전트가 하위 에이전트에게 세부 작업을 분배하는 계층적 조정 패턴.
**예시**: Coordinator가 Coder, Tester, Reviewer에게 각각 구현, 테스트, 검토 작업 위임

### Frontmatter (프론트매터)
**정의**: YAML/Markdown 파일 상단의 메타데이터 블록(`---`로 구분). 스킬 설정, 명령어 속성을 정의합니다.
**예시**:
```yaml
---
name: my-skill
autoLoad: true
---
```

### Git 3-Mode (Git 3단계 모드)
**정의**: MOAI-ADK의 Git 통합 전략 - (1) 자동 커밋, (2) 수동 검토, (3) 변경사항만 확인.
**예시**: Mode 1 - 에이전트가 작업 완료 시 자동으로 커밋 및 푸시

### Hook (훅)
**정의**: 작업 전후로 실행되는 자동화 스크립트. `pre-task`, `post-edit`, `session-end` 등의 타이밍에 실행됩니다.
**예시**: `npx claude-flow hooks post-edit --file "src/main.ts"` - 파일 편집 후 자동 포맷팅

### JSON-RPC
**정의**: MCP(Model Context Protocol)의 통신 프로토콜. 클라이언트와 서버 간 메시지를 JSON 형식으로 교환합니다.
**예시**: `{"jsonrpc":"2.0","method":"tools/list","id":1}` - 도구 목록 요청

### MCP Server (MCP 서버)
**정의**: Model Context Protocol 서버. AI 에이전트가 사용할 도구, 리소스, 프롬프트를 제공하는 표준화된 인터페이스.
**예시**: `claude mcp add serena npx serena-mcp start` - Serena MCP 서버 등록

### Memory (메모리)
**정의**: 세션 간 컨텍스트를 유지하는 저장소. 에이전트가 이전 작업 결과를 참조하거나 상태를 복원할 때 사용합니다.
**예시**: `memory_usage({action: "store", key: "swarm/results", value: "..."})` - 작업 결과 저장

### Mesh Topology (메시 토폴로지)
**정의**: 모든 에이전트가 서로 직접 통신 가능한 분산형 네트워크 구조. P2P 협업에 최적화되어 있습니다.
**예시**: `swarm_init({topology: "mesh"})` - 6개 에이전트가 자유롭게 협업하는 구조

### Neural Pattern (뉴럴 패턴)
**정의**: AI가 반복 작업에서 학습한 최적화 패턴. 성공 사례를 분석해 향후 작업 성능을 개선합니다.
**예시**: `neural_train({pattern_type: "optimization", training_data: "..."})` - 코드 최적화 패턴 학습

### Orchestration (오케스트레이션)
**정의**: 여러 에이전트의 작업을 조정하고 순서를 관리하는 프로세스. 병렬 또는 순차 실행 전략을 결정합니다.
**예시**: `task_orchestrate({strategy: "parallel", task: "빌드 및 테스트"})` - 병렬 실행 조정

## P-Y 핵심 용어

### Prompt (프롬프트)
**정의**: AI에게 제공되는 지시사항 템플릿. `.claude/prompts/` 또는 MCP 서버에서 제공됩니다.
**예시**: `{"name": "코드리뷰", "prompt": "다음 코드를 검토하세요: {code}"}` - 재사용 가능한 프롬프트

### Resume Pattern (재개 패턴)
**정의**: 중단된 작업을 컨텍스트 손실 없이 재개하는 설계 패턴. 세션 ID와 메모리를 활용합니다.
**예시**: `session-restore --session-id "swarm-123"` - 이전 작업 상태 복원

### Skill (스킬)
**정의**: 특정 워크플로우를 캡슐화한 재사용 가능한 모듈. `.claude/skills/` 디렉토리에 YAML 파일로 정의됩니다.
**예시**: `Skill("pdf")` - PDF 처리 전문 워크플로우 실행

### SPARC
**정의**: Specification(명세) → Pseudocode(의사코드) → Architecture(설계) → Refinement(개선) → Completion(완성) 방법론.
**예시**: `npx claude-flow sparc tdd "사용자 인증 기능"` - TDD 기반 전체 개발 사이클 실행

### Stateful (상태 유지)
**정의**: 에이전트나 세션이 이전 작업의 상태를 기억하고 유지하는 특성. 메모리와 세션 관리로 구현됩니다.
**예시**: 에이전트가 3단계 작업 중 2단계에서 중단 후 동일 상태에서 재개

### Swarm (스웜)
**정의**: 공통 목표를 위해 협업하는 다수의 에이전트 그룹. 토폴로지(hierarchical, mesh, ring)에 따라 조정됩니다.
**예시**: `swarm_init({topology: "hierarchical", maxAgents: 8})` - 8개 에이전트 계층 구조 초기화

### Task() (태스크)
**정의**: Claude Code의 에이전트 생성 함수. 작업 설명과 역할을 지정해 병렬 실행합니다.
**예시**: `Task("Backend API 구현", "Express로 REST API 작성", "backend-dev")` - 백엔드 개발 에이전트 실행

### TDD (테스트 주도 개발)
**정의**: Test-Driven Development. 테스트 작성 → 구현 → 리팩토링 순서로 개발하는 방법론.
**예시**: `sparc tdd "로그인 기능"` - 테스트 먼저 작성 후 구현

### Tier (티어)
**정의**: 에이전트의 복잡도/권한 계층. Tier 1(단순 작업) ~ Tier 3(복잡한 조정) 수준으로 구분됩니다.
**예시**: Tier 1 Coder → Tier 2 Reviewer → Tier 3 Architect 순으로 복잡도 증가

### TodoWrite (할일 작성)
**정의**: Claude Code의 작업 추적 도구. 여러 작업을 한 번에 배치로 생성하고 상태를 관리합니다.
**예시**: `TodoWrite({todos: [{content: "API 구현", status: "pending"}, ...]})` - 8-10개 작업 일괄 등록

### Topology (토폴로지)
**정의**: 에이전트 간 통신 구조. hierarchical(계층), mesh(분산), ring(순환), star(중앙집중) 유형이 있습니다.
**예시**: `topology: "mesh"` - 모든 에이전트가 직접 통신 가능한 구조

### Workflow (워크플로우)
**정의**: 작업의 순서와 조건을 정의한 프로세스. YAML 파일이나 스킬로 재사용 가능하게 구성됩니다.
**예시**: 코드 작성 → 테스트 → 검토 → 배포 순서의 자동화된 파이프라인

### YAML
**정의**: 사람이 읽기 쉬운 데이터 직렬화 형식. MOAI-ADK에서 스킬, 설정, 명령어 정의에 사용됩니다.
**예시**:
```yaml
name: my-skill
description: "작업 설명"
autoLoad: true
```

### Zero-Shot
**정의**: 사전 학습 없이 작업을 즉시 수행하는 AI 능력. MOAI-ADK 에이전트는 명확한 지시만으로 작업을 실행합니다.
**예시**: "TypeScript로 REST API 작성" 지시만으로 즉시 구현 시작

## 용어 분류

### 아키텍처
- Agent, Swarm, Topology, MCP Server, Orchestration

### 개발 방법론
- SPARC, TDD, Workflow, Resume Pattern

### 설정 및 구조
- YAML, Frontmatter, Context, Skill, Command

### 실행 및 제어
- Task(), Hook, Delegation, TodoWrite

### 상태 및 저장
- Memory, Stateful, Session, Neural Pattern

### 통신
- JSON-RPC, MCP Server, Mesh Topology

## 관련 문서

- **아키텍처**: `/_config/MOAI-ADK/architecture/ARCHITECTURE.md`
- **워크플로우**: `/_config/MOAI-ADK/workflows/WORKFLOWS.md`
- **스킬 가이드**: `/.claude/skills/README.md`
- **명령어 참조**: `/.claude/commands/README.md`
- **MCP 통합**: `/_config/MOAI-ADK/mcp/MCP-INTEGRATION.md`

## 빠른 참조

```bash
# 용어 검색
grep -r "Agent" _config/MOAI-ADK/analysis/

# 스킬 예시 확인
ls .claude/skills/

# MCP 서버 목록
claude mcp list
```

---

**Version**: 1.0.0
**Last Updated**: 2025-11-28
**Maintained by**: MOAI-ADK Team
