# Korean Translation Summary - uninstall-claude-flow.py

## Translation Overview
**Source File**: `_config/MOAI-ADK/scripts/uninstall-claude-flow.py`
**Target File**: `_config/MOAI-ADK-KO/scripts/uninstall-claude-flow.py`
**Date**: 2025-11-28
**Total Strings Translated**: **87**

## Translation Categories

### 1. Header & Docstrings (5 strings)
- "Claude-Flow Comprehensive Uninstaller" → "Claude-Flow 종합 제거 도구"
- "Safely removes all claude-flow directories and packages" → "모든 claude-flow 디렉토리와 패키지를 안전하게 제거합니다"
- "Supports dry-run, backup, and AI-guided modes" → "테스트 모드, 백업, AI 가이드 모드를 지원합니다"
- "Terminal color codes" → "터미널 색상 코드"
- "Main uninstaller class" → "메인 제거 도구 클래스"

### 2. Status Messages (15 strings)
- "Scanning for claude-flow directories..." → "claude-flow 디렉토리 검색 중..."
- "Checking npm packages..." → "npm 패키지 확인 중..."
- "Found" → "발견"
- "Removing:" → "제거 중:"
- "Creating backup:" → "백업 생성 중:"
- "Verifying removal..." → "제거 확인 중..."
- "Cleaning npm cache..." → "npm 캐시 정리 중..."
- "Successfully removed" → "성공적으로 제거됨"
- "Removed successfully" → "성공적으로 제거됨"
- "Cache cleaned" → "캐시 정리됨"
- "Backup failed:" → "백업 실패:"
- "Removal failed:" → "제거 실패:"
- "Uninstall failed:" → "제거 실패:"
- "Cache clean failed:" → "캐시 정리 실패:"
- "Report saved to:" → "보고서 저장됨:"

### 3. Warning & Error Messages (18 strings)
- "WARNING: This will permanently remove claude-flow" → "경고: claude-flow가 영구적으로 제거됩니다"
- "No claude-flow directories found" → "claude-flow 디렉토리를 찾을 수 없음"
- "No claude-flow npm packages found" → "claude-flow npm 패키지를 찾을 수 없음"
- "Could not calculate size:" → "크기를 계산할 수 없음:"
- "Could not check npm packages:" → "npm 패키지를 확인할 수 없음:"
- "Failed to backup" → "백업 실패"
- "Failed to remove" → "제거 실패"
- "Failed to save report:" → "보고서 저장 실패:"
- "Some items could not be removed" → "일부 항목을 제거할 수 없습니다"
- "Uninstall cancelled" → "제거가 취소되었습니다"
- "Errors encountered:" → "발생한 오류:"
- "Unknown error" → "알 수 없는 오류"
- "Cache clean returned non-zero" → "캐시 정리가 0이 아닌 값 반환"
- "Claude Agent SDK not installed" → "Claude Agent SDK가 설치되지 않았습니다"
- "Install with: pip install claude-agent-sdk" → "설치 방법: pip install claude-agent-sdk"
- "Falling back to standalone mode..." → "독립 실행 모드로 전환 중..."
- "removed" → "제거됨"
- "still exists" → "여전히 존재함"

### 4. UI Labels & Headers (12 strings)
- "Claude-Flow Uninstaller" → "Claude-Flow 제거 도구"
- "DRY RUN" → "테스트 모드"
- "UNINSTALL" → "제거"
- "+ BACKUP" → "+ 백업"
- "Summary" → "요약"
- "Directories:" → "디렉토리:"
- "NPM Packages:" → "NPM 패키지:"
- "Total space to be freed:" → "확보될 공간:"
- "Backed up to:" → "백업 위치:"
- "Would remove" → "제거될 예정"
- "Removed" → "제거됨"
- "Failed" → "실패"

### 5. Interactive Prompts (6 strings)
- "Proceed with uninstall? (yes/no):" → "제거를 진행하시겠습니까? (yes/no):"
- "Proceed with uninstall based on AI analysis? (yes/no):" → "AI 분석 결과를 바탕으로 제거를 진행하시겠습니까? (yes/no):"
- "Backups will be saved to _backups/claude-flow-uninstall/" → "백업은 _backups/claude-flow-uninstall/에 저장됩니다"
- "Would remove (dry-run)" → "제거될 예정 (테스트 모드)"
- "Would uninstall (dry-run)" → "제거될 예정 (테스트 모드)"
- "Would clean cache (dry-run)" → "캐시 정리될 예정 (테스트 모드)"

### 6. Success Messages (7 strings)
- "Claude-Flow uninstalled successfully!" → "Claude-Flow가 성공적으로 제거되었습니다!"
- "Dry-run completed - no changes made" → "테스트 모드 완료 - 변경 사항 없음"
- "Uninstall completed with errors" → "제거가 오류와 함께 완료되었습니다"
- "No claude-flow installation found" → "claude-flow 설치를 찾을 수 없음"
- "Installing packaging..." → "packaging 설치 중..."
- "Uninstalling:" → "제거 중:"
- "Removing directories..." → "디렉토리 제거 중..."

### 7. CLI Help Text (12 strings)
- "Comprehensive claude-flow uninstaller" → "종합 claude-flow 제거 도구"
- "Preview what would be removed (no changes)" → "제거될 항목 미리보기 (변경 없음)"
- "Create backups before removing directories" → "디렉토리 제거 전 백업 생성"
- "Skip confirmation prompt" → "확인 프롬프트 건너뛰기"
- "Use Claude Agent SDK for AI-guided uninstallation" → "AI 가이드 제거를 위해 Claude Agent SDK 사용"
- "Show detailed output" → "상세 출력 표시"
- "Examples:" → "사용 예시:"
- "Preview what would be removed" → "제거될 항목 미리보기"
- "Same as above (explicit)" → "위와 동일 (명시적)"
- "Uninstall without confirmation" → "확인 없이 제거"
- "Backup before removing" → "제거 전 백업"
- "AI-guided uninstallation" → "AI 가이드 제거"

### 8. AI Agent Mode (12 strings)
- "Claude Agent SDK Mode" → "Claude Agent SDK 모드"
- "Analyzing with Claude..." → "Claude로 분석 중..."
- "I'm planning to uninstall claude-flow. Here's what was found:" → "claude-flow 제거를 계획 중입니다. 발견된 항목은 다음과 같습니다:"
- "Directories to remove:" → "제거할 디렉토리:"
- "NPM packages to uninstall:" → "제거할 NPM 패키지:"
- "None found" → "발견된 항목 없음"
- "Total space to free:" → "확보될 공간:"
- "Mode:" → "모드:"
- "Dry-run (preview only)" → "테스트 모드 (미리보기만)"
- "Full uninstall" → "전체 제거"
- "Backup enabled:" → "백업 활성화:"
- "You are a helpful assistant for claude-flow uninstallation." → "당신은 claude-flow 제거를 돕는 유용한 도우미입니다."

## Preserved Elements

### Code Elements (NOT translated)
- Variable names: `dry_run`, `backup`, `verbose`, `base_dir`, `removed_items`, `errors`, `total_size`
- Function names: `print_header()`, `get_directory_size()`, `format_size()`, `scan_directories()`
- Class names: `ClaudeFlowUninstaller`, `Colors`
- Constants: `DIRECTORIES`, `NPM_PACKAGES`
- Exit codes: 0, 1, 4
- File paths and technical terms

### Technical Terms (Kept in English/Original)
- claude-flow
- npm
- JSON
- UTF-8
- packaging
- subprocess

## Key Features Maintained

1. ✅ All functionality preserved
2. ✅ Exit codes unchanged (0, 1, 4)
3. ✅ UTF-8 encoding with BOM header (`# -*- coding: utf-8 -*-`)
4. ✅ `ensure_ascii=False` added to JSON dump for proper Korean display
5. ✅ Color codes intact
6. ✅ Command-line argument structure unchanged
7. ✅ Error handling logic preserved
8. ✅ Dry-run functionality maintained

## File Locations

**Original**: `_config/MOAI-ADK/scripts/uninstall-claude-flow.py`

**Korean Version**: `_config/MOAI-ADK-KO/scripts/uninstall-claude-flow.py`

**Report Path Modified**: Changed from `_config/MOAI-ADK/reports/` to `_config/MOAI-ADK-KO/reports/` for localized reports

## Testing Performed

- ✅ Python syntax validation passed
- ✅ UTF-8 encoding verified
- ✅ Korean characters render correctly
- ✅ No functional changes to code logic

## Usage Examples (Korean)

```bash
# 제거될 항목 미리보기
python3 uninstall-claude-flow.py

# 테스트 모드 (명시적)
python3 uninstall-claude-flow.py --dry-run

# 확인 없이 제거
python3 uninstall-claude-flow.py --yes

# 백업 후 제거
python3 uninstall-claude-flow.py --backup --yes

# AI 가이드 제거
python3 uninstall-claude-flow.py --agent
```

## Summary Statistics

| Category | Count |
|----------|-------|
| Header & Docstrings | 5 |
| Status Messages | 15 |
| Warning & Error Messages | 18 |
| UI Labels & Headers | 12 |
| Interactive Prompts | 6 |
| Success Messages | 7 |
| CLI Help Text | 12 |
| AI Agent Mode | 12 |
| **Total Strings Translated** | **87** |

## Quality Assurance

- ✅ All user-facing strings translated to Korean
- ✅ Technical terms preserved appropriately
- ✅ Code structure and logic unchanged
- ✅ UTF-8 encoding ensured for Korean characters
- ✅ No functionality loss
- ✅ Consistent terminology throughout
- ✅ Natural Korean language flow maintained
