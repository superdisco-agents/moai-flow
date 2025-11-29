# MOAI-ADK-KO 설정 가이드

## 개요

이 설정 파일은 MOAI-ADK의 **한국어 전용 모드**를 활성화합니다. 모든 사용자 대면 콘텐츠, 메시지, UI 요소가 한국어로만 표시됩니다.

## 설정 파일 위치

```
_config/MOAI-ADK-KO/config/config.json
```

## 주요 설정 항목

### 1. 언어 설정 (`language`)

```json
{
  "conversation_language": "ko",
  "conversation_language_name": "Korean",
  "agent_prompt_language": "ko",
  "enforce_language_only": true,
  "fallback_language": "ko",
  "disable_english_fallback": true
}
```

- **conversation_language**: 대화 언어 코드 (ISO 639-1)
- **conversation_language_name**: 언어 전체 이름
- **agent_prompt_language**: AI 에이전트 프롬프트 언어
- **enforce_language_only**: 한국어만 사용하도록 강제
- **fallback_language**: 대체 언어 (한국어로 고정)
- **disable_english_fallback**: 영어 대체 비활성화

### 2. 메시지 설정 (`messages`)

모든 시스템 메시지를 한국어로 표시:
- CLI 출력
- 오류 메시지
- 도움말 텍스트
- 로그 메시지

### 3. UI 설정 (`ui`)

```json
{
  "language": "ko",
  "locale": "ko_KR",
  "timezone": "Asia/Seoul"
}
```

- 사용자 인터페이스 언어: 한국어
- 로케일: 한국 (ko_KR)
- 시간대: 한국 표준시 (KST)

## 설정 변경 방법

### 기본 설정 유지 (권장)

대부분의 경우 기본 설정을 그대로 사용하는 것이 좋습니다. 한국어 전용 환경에 최적화되어 있습니다.

### 설정 수정

1. `config.json` 파일을 텍스트 편집기로 엽니다
2. 필요한 값을 수정합니다
3. JSON 형식이 올바른지 확인합니다
4. 파일을 저장합니다
5. 애플리케이션을 재시작합니다

### 예: 타임존 변경

```json
{
  "ui": {
    "timezone": "UTC"  // 한국 표준시에서 UTC로 변경
  }
}
```

## 주의사항

⚠️ **중요한 제한사항**

1. **언어 고정**: `enforce_language_only: true` 설정으로 인해 한국어 외 다른 언어로 전환할 수 없습니다
2. **영어 대체 비활성화**: 번역이 없는 경우에도 영어로 표시되지 않습니다
3. **프롬프트 언어**: AI 에이전트의 모든 프롬프트가 한국어로 작성됩니다

⚠️ **설정 변경 시 주의**

- JSON 형식 오류는 설정 파일 로딩 실패를 초래합니다
- `enforce_language_only`를 `false`로 변경하면 다국어 모드가 활성화됩니다
- 타임존 변경 시 날짜/시간 표시가 영향을 받습니다

## 문제 해결

### 설정 파일이 로드되지 않는 경우

1. JSON 문법 검증기로 파일 확인
2. 파일 권한 확인 (읽기 권한 필요)
3. 파일 경로가 올바른지 확인

### 한국어가 제대로 표시되지 않는 경우

1. 시스템의 한국어 폰트 설치 확인
2. UTF-8 인코딩 확인
3. 터미널/콘솔의 한국어 지원 확인

## 버전 정보

- **현재 버전**: 1.0.0
- **호환성**: MOAI-ADK v1.x
- **마지막 업데이트**: 2025-11-28

## 관련 문서

- [MOAI-ADK-KO 메인 README](../README.md)
- [한국어 프롬프트 가이드](../docs/prompts/README.md)
- [CLI 사용 가이드](../docs/CLI_GUIDE.md)

---

**참고**: 이 설정은 한국 사용자를 위해 특별히 설계되었습니다. 다국어 지원이 필요한 경우 표준 MOAI-ADK 배포판을 사용하세요.
