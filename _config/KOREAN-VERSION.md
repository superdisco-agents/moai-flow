# 한글 전용 MoAI-ADK 버전 안내

MoAI-ADK의 완전한 한글 전용 버전이 `MOAI-ADK-KO/` 디렉토리에 준비되어 있습니다.

## 🎯 위치

```
_config/MOAI-ADK-KO/
```

## 📋 포함 내용

- ✅ **100% 한글 문서화** - 11개 문서 완전 번역
- ✅ **한글 CLI 출력** - 5개 Python 스크립트 한글화 (355개 문자열)
- ✅ **Ghostty 한글 폰트** - D2Coding Nerd Font 자동 설치
- ✅ **한글 전용 설정** - config.json 한글 모드
- ✅ **자동 설치 스크립트** - 원클릭 환경 구축

## 🚀 빠른 시작

```bash
# 한글 버전 디렉토리로 이동
cd _config/MOAI-ADK-KO

# 빠른 시작 가이드 읽기 (3단계)
cat 빠른시작.md

# 또는 완전 설치 가이드 읽기 (14개 섹션)
cat INSTALL-MOAI-ADK.md

# 자동 한글 환경 설정 (D2Coding 폰트 + Ghostty)
bash scripts/setup-korean-environment.sh
```

## 📚 주요 문서

| 문서 | 설명 |
|------|------|
| `빠른시작.md` | 3단계 빠른 시작 가이드 |
| `README.md` | 메인 README (51 KB) |
| `INSTALL-MOAI-ADK.md` | 완전 설치 가이드 (29 KB, 14개 섹션) |
| `스크립트가이드.md` | 5개 검증 스크립트 문서 (25 KB) |
| `완료보고서.md` | 프로젝트 완료 보고서 |
| `파일목록.md` | 전체 파일 인벤토리 (18개 파일) |

## 🔧 주요 스크립트

모든 스크립트는 한글 출력을 지원합니다:

| 스크립트 | 번역 문자열 | 용도 |
|----------|-------------|------|
| `check-latest-version.py` | 45개 | 버전 확인 |
| `verify-mcp-servers.py` | 80개 | MCP 서버 검증 |
| `pre-install-check.py` | 85개 | 사전 설치 검사 |
| `uninstall-claude-flow.py` | 87개 | Claude-Flow 제거 |
| `clean-dot-folders.py` | 58개 | 닷 폴더 정리 |

## ✨ 특징

### 1. Ghostty 한글 폰트 자동 설정
```bash
bash scripts/setup-korean-environment.sh
```
- D2Coding Nerd Font 자동 설치
- Ghostty 설정 자동 업데이트
- 한글 깨짐 문제 완전 해결

### 2. 100% 한글 문서
- 모든 README 한글화
- 설치 가이드 완전 번역 (14개 섹션)
- 합니다체 formal Korean 스타일

### 3. 한글 CLI 출력
- 모든 Python 스크립트 한글 메시지
- 오류, 경고, 성공 메시지 한글화
- 355개 문자열 번역 완료

### 4. 한글 전용 설정
```json
{
  "language": {
    "conversation_language": "ko",
    "enforce_language_only": true
  }
}
```

## 📊 통계

- **총 파일**: 18개
- **문서**: 11개 (100% 한글)
- **스크립트**: 6개 (5 Python + 1 Bash)
- **번역 문자열**: 355개
- **총 크기**: ~180 KB

## 🎯 다음 단계

1. `_config/MOAI-ADK-KO/빠른시작.md` 읽기
2. `scripts/setup-korean-environment.sh` 실행
3. `INSTALL-MOAI-ADK.md` 따라 설치

## 📞 지원

- 문서: `_config/MOAI-ADK-KO/README.md`
- 이슈: https://github.com/modu-ai/moai-adk/issues
- 피드백: `/moai:9-feedback` (Claude Code)

---

**버전**: 1.0.0 | **날짜**: 2025-11-28 | **상태**: ✅ 완료
