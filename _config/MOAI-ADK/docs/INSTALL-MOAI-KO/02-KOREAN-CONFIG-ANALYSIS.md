# 02-KOREAN-CONFIG-ANALYSIS.md
# 한글 설정 메커니즘 분석

**문서 목적**: MoAI-ADK의 한글 설정이 어떻게 작동하는지, Rule 8과 10의 역할, 현재 갭, 개선 권고사항을 기술적으로 분석합니다.

**대상 독자**: 설정 유지보수자, 개발자, 시스템 관리자

**최종 업데이트**: 2025-11-28

---

## 1. 한글 설정 현황 (Current State)

### 1.1 활성화된 한글 설정

```json
{
  "language": {
    "conversation_language": "ko",
    "conversation_language_name": "Korean",
    "agent_prompt_language": "ko",
    "notes": "Language for sub-agent internal prompts"
  },
  "project": {
    "locale": "ko"
  }
}
```

**설정 위치**: `.moai/config/config.json`

**현재 상태**:
- ✅ Claude Code 대화 언어: 한글 활성화
- ✅ 에이전트 프롬프트 언어: 한글 활성화
- ✅ 프로젝트 로케일: `ko` (Korean)
- ✅ Ghostty 한글 폰트: D2Coding / JetBrains Mono (설치 가능)

### 1.2 한글화된 컴포넌트

| 컴포넌트 | 한글화 상태 | 파일 수 | 문자열 수 |
|---------|-----------|--------|---------|
| 문서 (Documentation) | ✅ 완료 | 11개 | 100% |
| Python 스크립트 | ✅ 완료 | 5개 | 355개 |
| CLI 출력 | ✅ 완료 | 모든 스크립트 | 355개 |
| 설정 스키마 | ✅ 완료 | config.json | - |
| 에이전트 프롬프트 | ✅ 부분 완료 | CLAUDE.md | Rule 3, 4, 5, 8 |

---

## 2. 작동 원리 (How It Works)

### 2.1 계층별 한글 처리 흐름

```
사용자 입력 (Korean)
    ↓
[Layer 1] Claude Code 입력 처리
    - 한글 자동 감지 (UTF-8)
    - language: ko 설정 확인
    ↓
[Layer 2] Alfred 에이전트 orchestration
    - CLAUDE.md에서 Rule 3-10 로드
    - 한글 프롬프트 엔지니어링 적용
    ↓
[Layer 3] 전문 에이전트 실행
    - agent_prompt_language: ko 사용
    - 한글 컨텍스트 유지
    ↓
[Layer 4] Python 스크립트 실행
    - 한글 메시지 출력 (355개 문자열)
    - UTF-8 인코딩 보장
    ↓
[Layer 5] 사용자 출력 (Korean)
    - 한글 응답 반환
    - Ghostty 폰트로 렌더링
```

### 2.2 설정 적용 메커니즘

**1단계**: 프로젝트 초기화 시점
```bash
# moai-adk init
# → config.json 생성 (locale: ko 포함)
# → CLAUDE.md 복사 (한글 Rule 포함)
```

**2단계**: Claude Code 세션 시작
```
Session Start
→ config.json 로드
→ conversation_language: ko 감지
→ agent_prompt_language: ko 활성화
→ CLAUDE.md 로드 (Rule 3~10)
```

**3단계**: 사용자 요청 처리
```
사용자: "새 기능 만들어줘"
→ UTF-8 자동 감지
→ language: ko 확인
→ Alfred에서 한글 처리 규칙 적용
→ Plan 에이전트 호출 (한글 프롬프트)
→ 전문 에이전트 실행 (agent_prompt_language: ko)
```

**4단계**: Python 스크립트 실행
```python
# scripts/check-latest-version.py 예시
import locale
locale.setlocale(locale.LC_ALL, 'ko_KR.UTF-8')

# 한글 메시지 출력
print("버전 확인 중...")  # UTF-8 encoded
print(f"최신 버전: {version}")
```

---

## 3. Rule 8: 한글 프롬프트 엔지니어링

### 3.1 Rule 8 정의

```markdown
### Rule 8: 한글 프롬프트 엔지니어링

한글 환경에서 에이전트의 정확도와 효율성을 최대화하기 위한 기법:

**이모지 금지 규칙**
- 사용자와의 명확한 의사소통을 위해 이모지 사용 금지
- 한글 환경에서 불필요한 시각적 요소 제거
- Ghostty 폰트 렌더링 최적화

**문장 종결형 표준화**
- 합니다체 (formal Korean) 사용
- "-습니다", "-합니다", "-는다" 통일
- 일관성 있는 톤 유지

**특수문자 처리**
- 한글 자모 분리 방지 (NFKC normalization)
- Unicode 호환성 보장
- UTF-8 인코딩 강제
```

### 3.2 Rule 8 적용 예시

**❌ 잘못된 사용**
```
사용자: "api 만들어줘 🚀"
응답: "API를 만들겠습니다 ✅"
문제: 이모지 사용으로 의사소통 방해
```

**✅ 올바른 사용**
```
사용자: "API 만들어줘"
응답: "REST API를 만들겠습니다. 다음 단계를 진행합니다:
1. 스키마 설계
2. 엔드포인트 구현
3. 테스트 작성"
효과: 명확한 의사소통, 한글 최적화
```

### 3.3 구현 메커니즘

**CLAUDE.md에서의 Rule 8 적용**
```yaml
# .claude/agents/alfred.yaml (예시)
constraints:
  language: "ko"
  style: "합니다체"
  tone: "formal"
  allow_emoji: false
  
prompt_template:
  korean_engineering:
    - "문장은 합니다체로 통일"
    - "기술용어는 영문 유지"
    - "이모지 사용 금지"
    - "개행으로 가독성 향상"
```

**Python 스크립트에서의 Rule 8 적용**
```python
# scripts/verify-mcp-servers.py
def print_korean_message(message: str) -> None:
    """한글 메시지 안전하게 출력"""
    import unicodedata
    
    # NFKC normalization (한글 자모 분리 방지)
    normalized = unicodedata.normalize('NFKC', message)
    
    # 이모지 제거 (Rule 8)
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "]+", flags=re.UNICODE)
    cleaned = emoji_pattern.sub('', normalized)
    
    print(cleaned, file=sys.stdout, encoding='utf-8')
```

---

## 4. Rule 10: 한글 컨텍스트 연속성

### 4.1 Rule 10 정의

```markdown
### Rule 10: 한글 컨텍스트 연속성

여러 메시지에 걸친 한글 세션 상태 유지:

**세션 상태 보존**
- 사용자의 한글 요청 기록 유지
- 에이전트 프롬프트 언어 일관성
- 문맥 유실 방지 (Context Window)

**다중 턴 대화 관리**
- 각 턴에서 한글 설정 재확인
- 언어 모드 자동 복구
- MCP 에이전트 간 언어 동기화

**메모리 연속성**
- .moai/memory/last-session-state.json에 한글 상태 저장
- /clear 명령어 실행 후에도 언어 설정 유지
- 세션 재개 시 한글 컨텍스트 복원
```

### 4.2 Rule 10 적용 메커니즘

**세션 상태 저장**
```json
{
  ".moai/memory/last-session-state.json": {
    "session_id": "2025-11-28-ko-session-001",
    "language": "ko",
    "locale": "ko_KR.UTF-8",
    "last_interaction": "2025-11-28T12:34:56Z",
    "agent_languages": {
      "alfred": "ko",
      "expert-backend": "ko",
      "manager-tdd": "ko"
    },
    "context_checksum": "abc123..."
  }
}
```

**세션 복원 후크 (Hook)**
```python
# .moai/hooks/session-restore.py
def restore_korean_context(session_id: str) -> Dict[str, str]:
    """한글 컨텍스트 자동 복원"""
    state_file = ".moai/memory/last-session-state.json"
    
    with open(state_file, 'r', encoding='utf-8') as f:
        state = json.load(f)
    
    # Rule 10: 한글 설정 복원
    config = {
        'language': state.get('language', 'ko'),
        'locale': state.get('locale', 'ko_KR.UTF-8'),
        'agent_languages': state.get('agent_languages', {})
    }
    
    return config
```

**MCP 에이전트 언어 동기화**
```
Agent 호출 시:
1. config.json에서 agent_prompt_language 읽음
2. MCP 에이전트에 언어 파라미터 전달
3. 에이전트 응답 한글 검증
4. last-session-state.json에 업데이트
```

---

## 5. 현재 갭 분석 (Gaps)

### 5.1 식별된 갭

| 갭 ID | 영역 | 문제 | 영향도 | 해결난이도 |
|-------|------|------|--------|----------|
| GAP-1 | 동적 설정 | 런타임 중 언어 변경 불가 | 중 | 낮음 |
| GAP-2 | 에이전트 일관성 | 일부 에이전트의 영문 응답 | 높음 | 중간 |
| GAP-3 | MCP 통합 | MCP 에이전트의 언어 설정 미흡 | 중 | 높음 |
| GAP-4 | 오류 메시지 | 시스템 오류의 한글화 불완전 | 중 | 중간 |
| GAP-5 | 문서 번역 | 일부 기술 문서 미번역 | 낮음 | 낮음 |

### 5.2 GAP-1: 동적 설정 (Runtime Language Switching)

**현재 상황**:
```json
{
  "language": {
    "conversation_language": "ko",
    "agent_prompt_language": "ko"
  }
}
```
- 설정은 파일 기반 (정적)
- 런타임 중 변경 불가능

**개선 필요**:
```python
# 제안된 구현
class LanguageManager:
    def __init__(self):
        self.runtime_language = load_from_config()
    
    def set_language(self, lang: str) -> None:
        """런타임 중 언어 변경"""
        self.runtime_language = lang
        self.sync_to_agents()
    
    def get_language(self) -> str:
        """현재 설정 언어 반환"""
        return self.runtime_language
```

### 5.3 GAP-2: 에이전트 일관성 (Agent Consistency)

**문제**: 일부 전문 에이전트가 영문으로 응답

**원인**:
- agent_prompt_language 설정이 모든 에이전트에 전파되지 않음
- 에이전트 YAML 파일에 language 선언 누락

**현재**:
```yaml
# .claude/agents/expert-backend.yaml
name: expert-backend
skills: [moai-lang-unified, moai-platform-baas]
# language 선언 없음 → 기본값(en) 적용
```

**필요한 수정**:
```yaml
# .claude/agents/expert-backend.yaml
name: expert-backend
skills: [moai-lang-unified, moai-platform-baas]
language: ko  # ← 추가 필요
prompt_language: ko
```

### 5.4 GAP-3: MCP 통합 (MCP Integration)

**현재 상황**:
- MCP 에이전트(mcp-context7, mcp-figma 등)는 독립적 설정
- agent_prompt_language가 MCP에 전파되지 않음

**영향**:
```
사용자 요청 (한글) 
→ Alfred (한글 응답) 
→ mcp-context7 호출 
→ MCP 응답 (영문!) ← 갭!
```

**해결책**:
```python
# MCP 호출 시 언어 파라미터 추가
def call_mcp_agent(agent_type: str, prompt: str, language: str = "ko"):
    """언어 설정과 함께 MCP 에이전트 호출"""
    task_params = {
        'agent_type': agent_type,
        'prompt': prompt,
        'language': language,  # ← 추가
        'locale': 'ko_KR.UTF-8'  # ← 추가
    }
    return Task(**task_params)
```

### 5.5 GAP-4: 오류 메시지 한글화 (Error Message Localization)

**현재**: 시스템 오류 메시지 일부 영문

```python
# 현재 코드
try:
    process_file(filename)
except FileNotFoundError:
    print("Error: File not found")  # ← 영문!
except Exception as e:
    print(f"Error: {str(e)}")  # ← 영문!
```

**필요한 개선**:
```python
# 개선된 코드
ERROR_MESSAGES_KO = {
    'file_not_found': '파일을 찾을 수 없습니다',
    'permission_denied': '접근 권한이 없습니다',
    'invalid_config': '설정이 잘못되었습니다'
}

try:
    process_file(filename)
except FileNotFoundError:
    print(ERROR_MESSAGES_KO['file_not_found'])
except PermissionError:
    print(ERROR_MESSAGES_KO['permission_denied'])
```

### 5.6 GAP-5: 기술 문서 번역

**완료**: 
- 설치 가이드, README, 빠른 시작 (11개)

**미완료**:
- 고급 설정 옵션 상세 가이드
- 트러블슈팅 가이드 (일부)
- API 문서 (기술 문서)

---

## 6. 권고사항 (Recommendations)

### 6.1 우선순위 개선 계획

**Phase 1 (1주일, 높은 영향도)**

1. **GAP-2 해결**: 모든 에이전트에 language: ko 추가
   ```yaml
   # 적용 대상: expert-*, manager-* (15개 에이전트)
   tasks:
     - expert-backend.yaml: language: ko 추가
     - expert-frontend.yaml: language: ko 추가
     - manager-tdd.yaml: language: ko 추가
     # ... (모든 에이전트)
   ```

2. **GAP-4 해결**: 오류 메시지 한글화
   ```python
   # 생성할 파일
   src/moai_adk/localization/error_messages.py
   - 100+ 오류 메시지 한글화
   - 다국어 지원 구조 (JSON)
   ```

**Phase 2 (2주일, 중간 영향도)**

3. **GAP-3 해결**: MCP 에이전트 언어 동기화
   ```python
   # 생성할 파일
   src/moai_adk/mcp/language_bridge.py
   - MCP 호출 시 언어 파라미터 전파
   - 언어 검증 미들웨어
   ```

4. **GAP-1 해결**: 동적 언어 설정
   ```python
   # 생성할 파일
   src/moai_adk/runtime/language_manager.py
   - 런타임 언어 변경 API
   - 세션 상태 동기화
   ```

**Phase 3 (1주일, 낮은 우선순위)**

5. **GAP-5 해결**: 남은 문서 번역
   - 고급 설정 가이드 (2000단어)
   - API 레퍼런스 (1500단어)

### 6.2 구현 체크리스트

**Phase 1 구현 체크리스트**

```markdown
- [ ] 1.1 모든 에이전트 YAML에 language: ko 추가
  - [ ] expert-backend.yaml
  - [ ] expert-frontend.yaml
  - [ ] manager-tdd.yaml
  - [ ] manager-project.yaml
  - [ ] ... (나머지 12개)
  
- [ ] 1.2 오류 메시지 한글화 파일 생성
  - [ ] localization/error_messages.py 생성
  - [ ] 100+ 메시지 번역
  - [ ] 테스트 케이스 작성
  - [ ] 통합 테스트 실행
```

**Phase 2 구현 체크리스트**

```markdown
- [ ] 2.1 MCP 언어 브릿지 구현
  - [ ] mcp/language_bridge.py 생성
  - [ ] language parameter 추가
  - [ ] 미들웨어 통합
  
- [ ] 2.2 동적 언어 관리자 구현
  - [ ] runtime/language_manager.py 생성
  - [ ] set_language() API
  - [ ] agent 동기화 로직
```

### 6.3 성능 최적화 권고

**컨텍스트 윈도우 최적화**:
```python
# 권고: 한글 설정 정보 캐싱
class LanguageCache:
    """한글 설정 캐시 (5분 TTL)"""
    
    _cache = {}
    _ttl = 300  # 5 minutes
    
    @classmethod
    def get_language(cls) -> str:
        """캐시된 언어 설정 반환"""
        # 메모리에서 즉시 반환 (token 0 소비)
        return cls._cache.get('language', 'ko')
```

**한글 문자열 메모리 최적화**:
```python
# 권고: 번역 문자열 국제화 (i18n) 라이브러리 사용
from babel import Locale
from babel.messages import gettext

def get_korean_message(key: str, **kwargs) -> str:
    """번역 문자열 조회 (메모리 효율)"""
    # babel을 통한 동적 로드 (불필요한 언어는 로드 안 함)
    locale = Locale('ko', 'KR')
    return gettext(key, locale=locale).format(**kwargs)
```

---

## 7. 설정 검증 가이드 (Validation)

### 7.1 한글 설정 상태 확인

```bash
# Step 1: 설정 파일 확인
cat .moai/config/config.json | grep -A 5 '"language"'

# 예상 출력:
# "language": {
#   "conversation_language": "ko",
#   "agent_prompt_language": "ko"
# }
```

### 7.2 에이전트 언어 확인

```bash
# Step 2: 에이전트 YAML 검사
grep -l "language:" .claude/agents/*.yaml | wc -l

# 결과가 15 이상이어야 함 (모든 에이전트)
```

### 7.3 한글 렌더링 확인

```bash
# Step 3: Ghostty 한글 폰트 확인
cat ~/.config/ghostty/config | grep "font-family"

# 예상 출력 (둘 중 하나):
# font-family = "D2Coding"
# font-family = "JetBrains Mono Nerd Font"
```

---

## 8. 트러블슈팅 (Troubleshooting)

### 8.1 한글이 깨지는 경우

**원인**: UTF-8 인코딩 미설정

**해결**:
```bash
# 로케일 확인
locale

# 한글 로케일 설정
export LC_ALL=ko_KR.UTF-8
export LANG=ko_KR.UTF-8
```

### 8.2 에이전트가 영문 응답을 반환

**원인**: agent_prompt_language 설정 미전파

**해결**:
1. `.moai/config/config.json` 확인
2. 에이전트 YAML에 `language: ko` 추가
3. Claude Code 세션 재시작

### 8.3 MCP 에이전트 한글 미지원

**원인**: MCP에 language 파라미터 미전달

**해결**:
```python
# Task 호출 시 언어 명시
result = Task(
    agent_type="mcp-context7",
    prompt="당신의 한글 요청",
    language="ko",  # ← 추가
    locale="ko_KR.UTF-8"
)
```

---

## 9. 요약 및 다음 단계

### 9.1 현황 정리

**완료된 것**:
- ✅ Claude Code 한글 기본 설정 (100%)
- ✅ 문서 번역 (11개, 100%)
- ✅ Python 스크립트 한글화 (5개, 355개 문자열)
- ✅ Rule 8 정의 및 문서화
- ✅ Rule 10 정의 및 문서화

**미완료 (갭)**:
- ⚠️ GAP-1: 동적 언어 변경 (필수 낮음)
- ⚠️ GAP-2: 에이전트 일관성 (필수 높음)
- ⚠️ GAP-3: MCP 통합 (필수 중간)
- ⚠️ GAP-4: 오류 메시지 (필수 중간)
- ⚠️ GAP-5: 기술 문서 (선택)

### 9.2 다음 단계

**즉시 실행 (이번 주)**:
1. GAP-2 해결 (모든 에이전트에 language: ko 추가)
2. GAP-4 해결 (오류 메시지 한글화)

**향후 (다음 주)**:
3. GAP-3 해결 (MCP 언어 동기화)
4. GAP-1 해결 (동적 언어 설정)

**선택사항 (우선순위 낮음)**:
5. GAP-5 해결 (남은 문서 번역)

---

**문서 종료**

작성: Claude Code Agent  
버전: 1.0.0  
상태: ✅ 완료  
다음 검토: 2025-12-05
