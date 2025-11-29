# Claude-Flow 제거 도구 문서

## 개요

여러 안전 기능과 작동 모드를 갖춘 claude-flow 디렉토리 및 패키지를 안전하게 제거하기 위한 포괄적인 Python 스크립트입니다.

## 위치

```
_config/MOAI-ADK/scripts/uninstall-claude-flow.py
```

## 기능

### 🗑️ 제거 기능
- **디렉토리**: `.claude-flow`, `.swarm`, `.hive-mind`, `.specstory`, `node_modules/.cache/claude-flow`
- **NPM 패키지**: 전역 `claude-flow`, `@claude-flow/core`, `@claude-flow/cli`
- **NPM 캐시**: 패키지 제거 후 자동 캐시 정리

### 🛡️ 안전 기능
- **Dry-run 모드**: 실제 수정 없이 변경 사항 미리보기 (기본값)
- **백업 모드**: 삭제 전 디렉토리 아카이브
- **용량 계산**: 확보될 디스크 공간 표시
- **대화형 확인**: 명시적인 사용자 확인 요구
- **검증**: 실행 후 제거 성공 여부 확인
- **오류 처리**: 상세한 오류 보고 및 복구

### 🤖 작동 모드
1. **독립 실행 모드**: 컬러 출력이 있는 직접 실행
2. **Agent SDK 모드**: AI 가이드 분석 및 권장사항

### 📊 보고
- **실시간 진행상황**: 컬러 콘솔 출력
- **JSON 보고서**: `_config/MOAI-ADK/reports/`에 상세한 제거 로그 저장
- **종료 코드**: 표준 Unix 종료 코드 (0=성공, 1=오류, 4=정리 실패)

## 사용법

### 미리보기 모드 (기본)

```bash
# 실제 변경 없이 제거될 항목 표시
python3 _config/MOAI-ADK/scripts/uninstall-claude-flow.py

# 명시적 dry-run
python3 _config/MOAI-ADK/scripts/uninstall-claude-flow.py --dry-run

# 상세 출력
python3 _config/MOAI-ADK/scripts/uninstall-claude-flow.py --dry-run --verbose
```

### 제거 모드

```bash
# 기본 제거 (확인 포함)
python3 _config/MOAI-ADK/scripts/uninstall-claude-flow.py --yes

# 백업과 함께 제거
python3 _config/MOAI-ADK/scripts/uninstall-claude-flow.py --backup --yes

# 확인 없이 제거 (주의해서 사용)
python3 _config/MOAI-ADK/scripts/uninstall-claude-flow.py -y
```

### AI 가이드 모드

```bash
# AI 분석 및 권장사항
python3 _config/MOAI-ADK/scripts/uninstall-claude-flow.py --agent

# 백업과 함께 AI 가이드 제거
python3 _config/MOAI-ADK/scripts/uninstall-claude-flow.py --agent --backup
```

## 명령줄 옵션

```
옵션:
  --dry-run          제거될 항목 미리보기 (변경 없음)
  --backup           디렉토리 제거 전 백업 생성
  --yes, -y          확인 프롬프트 건너뛰기
  --agent            AI 가이드 제거를 위한 Claude Agent SDK 사용
  --verbose, -v      상세 출력 표시
  --help, -h         도움말 메시지 표시
```

## ⚠️ 중요 경고

**제거하기 전에 반드시 데이터를 백업하세요!**

Claude-Flow를 제거하면 다음 항목들이 영구적으로 삭제됩니다:
- 모든 설정 파일 및 사용자 데이터
- 학습된 신경망 패턴 및 세션 데이터
- 스웜 조정 정보 및 메모리
- 캐시된 작업 및 히스토리

안전한 제거를 위해:
1. 항상 먼저 `--dry-run`으로 미리보기 확인
2. 중요한 프로젝트에서는 `--backup` 플래그 사용
3. 다른 프로젝트가 claude-flow에 의존하지 않는지 확인
4. 활성 스웜 프로세스가 실행 중이지 않은지 확인

## 예제

### 예제 1: 제거 전 미리보기

```bash
# 1단계: 제거될 항목 확인
python3 _config/MOAI-ADK/scripts/uninstall-claude-flow.py

# 2단계: 만족스러우면 제거 진행
python3 _config/MOAI-ADK/scripts/uninstall-claude-flow.py --yes
```

**출력:**
```
🗑️  Claude-Flow Uninstaller [DRY RUN]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📂 Scanning for claude-flow directories...

  ✓ Found .claude-flow                      (12.45 MB)
  ✓ Found .swarm                            (3.21 MB)
  ✓ Found .hive-mind                        (5.67 MB)

📦 Checking npm packages...

  ✓ Found claude-flow                       (v2.0.0)

📊 Summary
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Directories:
  Would remove    .claude-flow                      (12.45 MB)
  Would remove    .swarm                            (3.21 MB)
  Would remove    .hive-mind                        (5.67 MB)

NPM Packages:
  Would remove    claude-flow                       (v2.0.0)

Total space to be freed: 21.33 MB
```

### 예제 2: 백업과 함께 안전한 제거

```bash
python3 _config/MOAI-ADK/scripts/uninstall-claude-flow.py --backup --yes
```

**출력:**
```
🗑️  Claude-Flow Uninstaller [UNINSTALL + BACKUP]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️  WARNING: This will permanently remove claude-flow
ℹ  Backups will be saved to _backups/claude-flow-uninstall/

🗑️  Removing directories...

  🗑️  Removing: .claude-flow
  📦 Creating backup: .claude-flow_20251128_143022
     ✓ Removed successfully

  🗑️  Removing: .swarm
  📦 Creating backup: .swarm_20251128_143023
     ✓ Removed successfully

🗑️  Uninstalling npm packages...

  🗑️  Uninstalling: claude-flow
     ✓ Uninstalled successfully

  🧹 Cleaning npm cache...
     ✓ Cache cleaned

🔍 Verifying removal...

  ✓ .claude-flow - removed
  ✓ .swarm - removed

✓ Report saved to: _config/MOAI-ADK/reports/claude-flow-uninstall_20251128_143025.json

✅ Claude-Flow uninstalled successfully!
```

### 예제 3: AI 가이드 분석

```bash
python3 _config/MOAI-ADK/scripts/uninstall-claude-flow.py --agent
```

**출력:**
```
🤖 Claude Agent SDK Mode
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🤖 Analyzing with Claude...

Based on my analysis of your claude-flow installation:

Assessment:
- 3 main directories will be removed (.claude-flow, .swarm, .hive-mind)
- 1 npm package will be uninstalled (claude-flow v2.0.0)
- Total disk space to be freed: 21.33 MB

Potential Issues:
- The .swarm directory contains coordination data that may be needed by other projects
- Consider backing up .hive-mind if you have custom neural patterns trained

Recommendations:
1. Use --backup flag to preserve data before removal
2. Check if other projects depend on claude-flow coordination features
3. Export any important session data or neural patterns
4. Verify no active swarm processes are running

This appears to be a complete uninstallation that will fully remove claude-flow
from your system. The backup option is highly recommended for safety.

Proceed with uninstall based on AI analysis? (yes/no):
```

## 종료 코드

스크립트는 표준 Unix 종료 코드를 사용합니다:

| 코드 | 의미 | 설명 |
|------|---------|-------------|
| 0 | 성공 | 제거가 성공적으로 완료되었거나 제거할 항목 없음 |
| 1 | 오류 | 제거 중 오류 발생 |
| 4 | 정리 실패 | 제거 후 검증에서 항목이 여전히 존재함 |

## 보고서 형식

JSON 보고서는 `_config/MOAI-ADK/reports/claude-flow-uninstall_TIMESTAMP.json`에 저장됩니다:

```json
{
  "timestamp": "2025-11-28T14:30:25.123456",
  "mode": "uninstall",
  "backup_enabled": true,
  "base_directory": "/Users/username/project",
  "directories": [
    {
      "name": ".claude-flow",
      "path": "/Users/username/project/.claude-flow",
      "size": 13058048,
      "size_formatted": "12.45 MB",
      "type": "directory",
      "removed": true,
      "backup_path": "_backups/claude-flow-uninstall/.claude-flow_20251128_143022"
    }
  ],
  "packages": [
    {
      "name": "claude-flow",
      "version": "2.0.0",
      "type": "npm-global",
      "removed": true
    }
  ],
  "total_size_bytes": 22371328,
  "total_size_formatted": "21.33 MB",
  "errors": [],
  "summary": {
    "directories_found": 3,
    "packages_found": 1,
    "items_removed": 4,
    "errors_count": 0
  }
}
```

## 백업 구조

백업은 `_backups/claude-flow-uninstall/`에 저장됩니다:

```
_backups/
└── claude-flow-uninstall/
    ├── .claude-flow_20251128_143022/
    ├── .swarm_20251128_143023/
    └── .hive-mind_20251128_143024/
```

## 테스트

기능을 확인하려면 테스트 스크립트를 실행하세요:

```bash
bash _config/MOAI-ADK/scripts/test-uninstall.sh
```

## 문제 해결

### 문제: "Permission denied" 오류

**해결책:**
```bash
# 스크립트를 실행 가능하게 만들기
chmod +x _config/MOAI-ADK/scripts/uninstall-claude-flow.py

# 또는 sudo로 실행 (권장하지 않음)
sudo python3 _config/MOAI-ADK/scripts/uninstall-claude-flow.py --yes
```

### 문제: NPM 패키지를 찾을 수 없음

**해결책:**
claude-flow가 전역으로 설치되지 않은 경우 정상입니다. 스크립트는 npm 제거를 건너뛰고 디렉토리만 제거합니다.

### 문제: 제거 후에도 디렉토리가 여전히 존재함

**해결책:**
```bash
# 프로세스가 디렉토리를 사용 중인지 확인
lsof | grep claude-flow

# 모든 프로세스 종료
pkill -f claude-flow

# 제거 도구 재실행
python3 _config/MOAI-ADK/scripts/uninstall-claude-flow.py --yes
```

### 문제: 백업에서 복원하고 싶음

**해결책:**
```bash
# 백업 목록 확인
ls -la _backups/claude-flow-uninstall/

# 특정 디렉토리 복원
cp -r _backups/claude-flow-uninstall/.claude-flow_20251128_143022 ./.claude-flow
```

## 의존성

스크립트는 필요한 의존성을 자동으로 설치합니다:
- `packaging` - 버전 비교 유틸리티

AI 모드를 위한 선택적 의존성:
- `claude-agent-sdk` - AI 가이드 제거

## 모범 사례

1. **항상 먼저 미리보기**: `--yes` 없이 실행하여 제거될 항목 확인
2. **프로덕션에서는 백업 사용**: 중요한 프로젝트 작업 시 `--backup` 플래그 추가
3. **보고서 확인**: 감사 추적을 위해 JSON 보고서 검토
4. **제거 검증**: 스크립트가 자동으로 검증하지만 중요한 디렉토리는 재확인
5. **AI 가이드**: 복잡한 시나리오나 확실하지 않을 때 `--agent` 모드 사용

## 관련 문서

- [설치 가이드](./INSTALL-MOAI-ADK.md)
- [버전 체커](./scripts/check-latest-version.py)
- [MoAI-ADK 구성](./CONFIGURATION.md)

## 지원

문제나 질문이 있는 경우:
1. 위의 문제 해결 섹션 확인
2. `_config/MOAI-ADK/reports/`의 JSON 보고서 검토
3. 상세 출력을 위해 `--verbose` 플래그로 실행
4. AI 기반 가이드를 위해 `--agent` 모드 사용
