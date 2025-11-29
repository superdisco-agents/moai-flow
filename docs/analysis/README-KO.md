# MoAI-ADK 분석 문서 - 한국어 가이드

## 👋 환영합니다

MoAI-ADK (Model-of-AI Application Development Kit)의 전체 아키텍처와 5가지 Claude Code 래핑 방법을 분석한 문서입니다.

이 문서들은 한국 개발자가 MoAI-ADK를 빠르게 이해하고 실전에 활용할 수 있도록 작성되었습니다.

## 🚀 빠른 시작

### 처음 오셨나요?
1. **[빠른 시작 가이드](./빠른-시작-가이드.md)** (10분) - MoAI-ADK 핵심 개념 파악
2. **[용어집](./용어집-GLOSSARY-KO.md)** - 기술 용어 한국어 정의
3. **[프로젝트 개요](./00-PROJECT-OVERVIEW.md)** - 전체 아키텍처 이해

### 특정 주제를 찾으시나요?
- **에이전트(Agents)**: [01-에이전트-설명-KO.md](./01-에이전트-설명-KO.md)
- **스킬(Skills)**: [02-스킬-설명-KO.md](./02-스킬-설명-KO.md)
- **명령어(Commands)**: [03-명령어-설명-KO.md](./03-명령어-설명-KO.md)
- **의사결정**: [06-의사결정-프레임워크-KO.md](./06-의사결정-프레임워크-KO.md)
- **통합 패턴**: [07-통합-패턴-KO.md](./07-통합-패턴-KO.md)

## 📚 문서 구조

### 한국어 문서 (권장)
| 문서 | 설명 | 난이도 | 예상 시간 |
|------|------|--------|----------|
| [README-KO.md](./README-KO.md) | 📍 **지금 보고 계신 문서** | ⭐ 입문 | 5분 |
| [빠른-시작-가이드.md](./빠른-시작-가이드.md) | 10분 만에 핵심 개념 파악 | ⭐ 입문 | 10분 |
| [용어집-GLOSSARY-KO.md](./용어집-GLOSSARY-KO.md) | 50+ 기술 용어 한국어 정의 | ⭐ 입문 | 참고용 |
| [00-PROJECT-OVERVIEW.md](./00-PROJECT-OVERVIEW.md) | 프로젝트 전체 아키텍처 | ⭐⭐ 중급 | 30분 |
| [01-에이전트-설명-KO.md](./01-에이전트-설명-KO.md) | AGENTS 래핑 방법 상세 분석 | ⭐⭐⭐ 고급 | 45분 |
| [02-스킬-설명-KO.md](./02-스킬-설명-KO.md) | SKILLS 래핑 방법 상세 분석 | ⭐⭐⭐ 고급 | 40분 |
| [03-명령어-설명-KO.md](./03-명령어-설명-KO.md) | COMMANDS 래핑 방법 상세 분석 | ⭐⭐ 중급 | 30분 |
| [06-의사결정-프레임워크-KO.md](./06-의사결정-프레임워크-KO.md) | 언제 무엇을 사용할지 결정 가이드 | ⭐⭐ 중급 | 25분 |
| [07-통합-패턴-KO.md](./07-통합-패턴-KO.md) | 실전 통합 패턴 및 Best Practices | ⭐⭐⭐ 고급 | 35분 |

### 영어 원문 (심화 학습용)
| 문서 | 설명 |
|------|------|
| [01-AGENTS-WRAPPING.md](./01-AGENTS-WRAPPING.md) | Agents 원문 (영어) |
| [02-SKILLS-WRAPPING.md](./02-SKILLS-WRAPPING.md) | Skills 원문 (영어) |
| [03-COMMANDS-WRAPPING.md](./03-COMMANDS-WRAPPING.md) | Commands 원문 (영어) |
| [04-SCRIPTS-WRAPPING.md](./04-SCRIPTS-WRAPPING.md) | Scripts/Hooks 원문 (영어) |
| [05-MCP-SERVERS-WRAPPING.md](./05-MCP-SERVERS-WRAPPING.md) | MCP Servers 원문 (영어) |
| [06-DECISION-FRAMEWORK.md](./06-DECISION-FRAMEWORK.md) | Decision Framework 원문 (영어) |
| [07-INTEGRATION-PATTERNS.md](./07-INTEGRATION-PATTERNS.md) | Integration Patterns 원문 (영어) |

## 🎯 학습 경로 추천

### 경로 1: 빠른 이해 (1시간)
```
1. 빠른 시작 가이드 (10분)
   ↓
2. 프로젝트 개요 (30분)
   ↓
3. 의사결정 프레임워크 (20분)
```

### 경로 2: 에이전트 개발자 (3시간)
```
1. 빠른 시작 가이드 (10분)
   ↓
2. 에이전트 설명 (45분)
   ↓
3. 스킬 설명 (40분)
   ↓
4. 통합 패턴 (35분)
   ↓
5. 의사결정 프레임워크 (25분)
   ↓
6. 용어집 (참고)
```

### 경로 3: 아키텍트 (전체 마스터)
```
1. 프로젝트 개요 (30분)
   ↓
2. 5가지 래핑 방법 모두 읽기 (3시간)
   - 에이전트, 스킬, 명령어, 스크립트, MCP
   ↓
3. 의사결정 프레임워크 (25분)
   ↓
4. 통합 패턴 (35분)
   ↓
5. 영어 원문 심화 학습 (4시간)
```

## 🔑 핵심 개념

### 5가지 Claude Code 래핑 방법

1. **AGENTS (에이전트)**
   - 전문화된 작업 실행자 (24개)
   - 5-Tier 계층 구조
   - Task() 위임 메커니즘
   - **용도**: 도메인 전문 작업, Multi-step 워크플로우

2. **SKILLS (스킬)**
   - 도메인 지식 캡슐화 (128+개)
   - Auto-load 트리거
   - Markdown 문서 형식
   - **용도**: Procedural knowledge, 패턴 참조

3. **COMMANDS (명령어)**
   - 사용자 명시적 트리거 (7개)
   - 복잡한 워크플로우 단축키
   - 4-Phase 실행 패턴
   - **용도**: /moai:* 명령어, SPEC 생성, TDD 구현

4. **SCRIPTS (스크립트)**
   - 빠른 one-shot 실행
   - Hook 시스템 (session_start, pre_commit 등)
   - Zero 토큰 비용
   - **용도**: 이벤트 기반 자동화, 빠른 bash 작업

5. **MCP SERVERS (MCP 서버)**
   - Stateful 상태 유지 (4개)
   - JSON-RPC 2.0 프로토콜
   - Real-time 알림
   - **용도**: 외부 서비스 통합, 영구 상태, 실시간 데이터

### 핵심 아키텍처 원칙

**"Commands → Agents → Skills" 패턴**
```
사용자 요청
    ↓
명령어 (/moai:*)
    ↓
관리자 에이전트 (조율)
    ↓
전문 에이전트 (실행)
    ↓
스킬 (도메인 지식)
    ↓
Claude Code 도구 (Read, Write, Edit, Bash)
```

**"MCP = 뇌, Claude Code = 손"**
- MCP 도구: 조율 뇌 (coordination, state, real-time)
- 에이전트: 전문 작업자
- 스킬: 도메인 지식
- 명령어: 사용자 인터페이스
- 스크립트: 빠른 자동화
- Claude Code: 실행 손

## 💡 실전 활용 팁

### 언제 무엇을 사용할까?

| 상황 | 사용할 방법 | 문서 |
|------|------------|------|
| 코드베이스 탐색만 필요 | AGENTS (Explore) | 01-에이전트-설명-KO.md |
| Backend 기능 구현 | AGENTS (expert-backend) + SKILLS | 01, 02번 문서 |
| 새 기능 SPEC 작성 | COMMANDS (/moai:1-plan) | 03-명령어-설명-KO.md |
| TDD 사이클 실행 | COMMANDS (/moai:2-run) | 03-명령어-설명-KO.md |
| 최신 API 문서 조회 | MCP SERVERS (context7) | 05-MCP-SERVERS-WRAPPING.md (영어) |
| Git 자동화 | SCRIPTS (hooks) | 04-SCRIPTS-WRAPPING.md (영어) |
| 복잡한 아키텍처 분석 | MCP (sequential-thinking) | 05-MCP-SERVERS-WRAPPING.md (영어) |

### 자주 묻는 질문 (FAQ)

**Q: 한국어 문서와 영어 원문 중 어떤 걸 봐야 하나요?**
A: 먼저 한국어 문서로 개념을 이해하고, 더 자세한 내용이 필요하면 영어 원문을 참고하세요.

**Q: 어떤 순서로 읽어야 하나요?**
A: 위의 "학습 경로 추천"을 참고하세요. 빠른 이해는 1시간, 에이전트 개발은 3시간 코스를 권장합니다.

**Q: 실전 예제는 어디에 있나요?**
A: 각 문서의 "실전 예제" 섹션과 통합 패턴 문서를 참고하세요.

**Q: 기술 용어가 어려워요.**
A: [용어집-GLOSSARY-KO.md](./용어집-GLOSSARY-KO.md)에서 50+ 용어의 한국어 정의를 확인하세요.

## 🎓 심화 학습 자료

### 아키텍처 이해하기
- **계층 구조**: 5-Tier 에이전트 시스템 (Tier-0부터 Tier-4까지)
- **조율 패턴**: Commands가 Agents를 호출, Agents가 Skills를 참조
- **실행 흐름**: 사용자 → Commands → Agents → Skills → Claude Code 도구

### 성능 최적화
- **토큰 효율성**: Skills는 필요시만 로드 (lazy loading)
- **병렬 처리**: 여러 에이전트 동시 실행 가능
- **캐싱**: MCP Servers를 통한 상태 유지

### 보안 고려사항
- **권한 관리**: 각 에이전트별 역할 기반 접근 제어
- **입력 검증**: Commands를 통한 사용자 입력 검증
- **격리**: 각 에이전트는 독립적인 실행 컨텍스트

## 📊 문서 통계

- **전체 문서**: 14개 (한국어 9개, 영어 5개)
- **총 예상 학습 시간**: 6-8시간 (전체 마스터)
- **핵심 개념**: 5가지 래핑 방법
- **에이전트 수**: 24개
- **스킬 수**: 128+개
- **명령어 수**: 7개
- **MCP 서버**: 4개

## 🔗 관련 리소스

### 프로젝트 내부 자료
- **MoAI-ADK 공식 문서**: `.moai/` 디렉토리
- **에이전트 정의**: `.claude/agents/` 디렉토리
- **스킬 정의**: `.claude/skills/` 디렉토리
- **명령어 정의**: `.claude/commands/` 디렉토리
- **Alfred 실행 지침**: `CLAUDE.md`

### 외부 참고 자료
- **Claude Code 공식 문서**: Anthropic Claude Code 가이드
- **MCP 프로토콜**: Model Context Protocol 명세
- **TDD 방법론**: Test-Driven Development 가이드

## 🛠️ 실습 예제

### 예제 1: 간단한 기능 구현
```bash
# 1. SPEC 작성
/moai:1-plan "사용자 인증 기능 추가"

# 2. TDD 사이클 실행
/moai:2-run

# 3. 코드 리뷰
/moai:3-review
```

### 예제 2: 복잡한 아키텍처 분석
```bash
# 1. 코드베이스 탐색
Call: expert-explore agent

# 2. 아키텍처 분석
Call: expert-architect agent

# 3. 의사결정 지원
Use: sequential-thinking MCP server
```

### 예제 3: API 문서 참조
```bash
# 1. Context7 MCP로 최신 문서 조회
Use: mcp__context7__get-library-docs

# 2. 해당 패턴으로 코드 작성
Call: expert-backend agent + backend-api skill
```

## 📞 지원 및 피드백

### 피드백 제출하기
```bash
/moai:9-feedback
```
- 버그 리포트
- 개선 제안
- 문서 오류 수정
- 새로운 예제 요청

### 기여하기
1. 문서 개선 PR 생성
2. 새로운 스킬 제안
3. 에이전트 개선 아이디어
4. 통합 패턴 공유

## 🎯 다음 단계

### 초보자라면
1. ✅ 이 README 완독 (5분)
2. → [빠른 시작 가이드](./빠른-시작-가이드.md) 읽기 (10분)
3. → [용어집](./용어집-GLOSSARY-KO.md) 북마크 (참고용)
4. → [프로젝트 개요](./00-PROJECT-OVERVIEW.md) 읽기 (30분)

### 중급자라면
1. ✅ 이 README 완독 (5분)
2. → [에이전트 설명](./01-에이전트-설명-KO.md) 읽기 (45분)
3. → [스킬 설명](./02-스킬-설명-KO.md) 읽기 (40분)
4. → [통합 패턴](./07-통합-패턴-KO.md) 실습 (35분)

### 고급 개발자라면
1. ✅ 이 README 완독 (5분)
2. → 5가지 래핑 방법 전체 학습 (3시간)
3. → 영어 원문 심화 학습 (4시간)
4. → 실전 프로젝트 적용 및 피드백 제출

## 📝 문서 업데이트 이력

| 날짜 | 버전 | 변경 내용 |
|------|------|----------|
| 2025-11-28 | 1.0.0 | 초기 버전 생성 (한국어 README) |

## 🏆 문서 품질 지표

- **완성도**: 100% (모든 섹션 작성 완료)
- **정확도**: 원문 기반 번역 및 추가 설명
- **접근성**: 초보자부터 고급자까지 대응
- **실용성**: 실전 예제 및 학습 경로 제공

---

## 💬 마지막 한마디

이 문서는 MoAI-ADK를 처음 접하는 한국 개발자들이 빠르게 시작할 수 있도록 작성되었습니다.

**핵심 원칙**:
- Commands는 사용자 인터페이스
- Agents는 전문 작업자
- Skills는 도메인 지식
- Scripts는 빠른 자동화
- MCP Servers는 상태 관리

**실전 적용**:
1. 작은 기능부터 시작하세요 (`/moai:1-plan`)
2. TDD 사이클을 따르세요 (`/moai:2-run`)
3. 에이전트를 신뢰하세요 (Task 위임)
4. 스킬을 활용하세요 (도메인 지식)
5. MCP로 확장하세요 (외부 통합)

**학습 여정**:
- 1시간: 핵심 개념 이해
- 3시간: 에이전트 개발 능력
- 6-8시간: 아키텍트 레벨 마스터

**질문이 있으신가요?**
- 용어집을 먼저 확인하세요
- 해당 주제의 상세 문서를 읽어보세요
- `/moai:9-feedback`으로 질문을 남겨주세요

**이제 시작하세요!**
→ [빠른 시작 가이드](./빠른-시작-가이드.md)로 이동

---

**버전**: 1.0.0 (2025-11-28)
**언어**: 한국어 (Korean)
**대상**: 한국 개발자 (Korean Developers)
**라이선스**: MoAI-ADK 프로젝트와 동일
**작성자**: MoAI-ADK Documentation Team
**최종 수정**: 2025-11-28

---

**문서 트리 구조**:
```
_config/MOAI-ADK/analysis/
├── README-KO.md                    ← 📍 지금 여기 (Entry Point)
├── 빠른-시작-가이드.md              ← Next: 10분 가이드
├── 용어집-GLOSSARY-KO.md           ← Reference: 용어 사전
├── 00-PROJECT-OVERVIEW.md         ← Overview: 전체 아키텍처
├── 01-에이전트-설명-KO.md          ← Deep Dive: Agents
├── 02-스킬-설명-KO.md              ← Deep Dive: Skills
├── 03-명령어-설명-KO.md            ← Deep Dive: Commands
├── 06-의사결정-프레임워크-KO.md     ← Guide: 의사결정
├── 07-통합-패턴-KO.md              ← Guide: 통합 패턴
└── [영어 원문들...]               ← Advanced: 심화 학습
```

**Happy Coding with MoAI-ADK!** 🚀
