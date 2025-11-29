# 🗿 MoAI-ADK 설치 가이드 (Claude Code용)

**버전**: 0.30.2 (항상 최신 릴리스 설치)
**플랫폼**: macOS, Linux, Windows (WSL)
**Python 필수**: 3.11 - 3.14
**소요 시간**: 15-20분

이 가이드는 **워크스페이스 독립적**입니다 — 이 파일을 Claude Code 프로젝트에 드래그 앤 드롭하여 MoAI-ADK를 처음부터 설치할 수 있습니다.

⚠️ **중요**: 이것은 **프로젝트 수준 설치**입니다 (가상 환경 필요). 전역 설치가 아닙니다.

---

## 📋 목차

0. [Ghostty 한글 폰트 설정 (선행 작업)](#0-ghostty-한글-폰트-설정-선행-작업)
1. [사전 요구사항 확인](#1-사전-요구사항-확인)
2. [기존 설치 제거](#2-기존-설치-제거)
3. [최신 MoAI-ADK 릴리스 가져오기](#3-최신-moai-adk-릴리스-가져오기)
4. [MoAI-ADK 설치](#4-moai-adk-설치)
5. [설치 확인](#5-설치-확인)
6. [문제 해결](#6-문제-해결)
7. [다음 단계](#7-다음-단계)
8. [한국어 언어 지원](#8-한국어-언어-지원-)
9. [MoAI-ADK 이해하기](#9-moai-adk-이해하기)
10. [고급 설정](#10-고급-설정)
11. [빠른 참조 카드](#11-빠른-참조-카드)
12. [도움말 받기](#12-도움말-받기)
13. [유지보수](#13-유지보수)
14. [제거](#14-제거)

---

## 0. Ghostty 한글 폰트 설정 (선행 작업)

### 왜 필요한가요?
한글이 깨져 보이는 것을 방지하기 위해 D2Coding 폰트를 설치합니다.

### 설치 방법
```bash
brew tap homebrew/cask-fonts
brew install --cask font-d2coding
```

### Ghostty 설정
파일: `~/.config/ghostty/config`
```ini
font-family = "JetBrains Mono"
font-family = "D2Coding"
font-size = 14
```

### 설정 적용
- `Cmd+Shift+,` 누르기 또는 Ghostty 재시작

### 확인
```bash
echo "한글 테스트 - 정상적으로 보이면 성공!"
```

---

## 1. 사전 요구사항 확인

### 필수 소프트웨어

설치 전 다음 항목을 확인하십시오:

```bash
# Python 버전 확인 (3.11+ 필수)
python3 --version

# git 설치 확인
git --version

# npx 사용 가능 확인 (MCP 서버용)
npx --version
```

**예상 출력**:
- Python: `3.11.x`, `3.12.x`, `3.13.x`, 또는 `3.14.x`
- Git: 모든 버전
- npx: 모든 버전 (Node.js와 함께 제공됨)

### 누락된 요구사항 설치

**Python 3.11+가 없는 경우**:

```bash
# macOS (Homebrew)
brew install python@3.13

# Ubuntu/Debian
sudo apt-get update
sudo apt-get install python3.13

# Windows (WSL)
sudo apt-get update
sudo apt-get install python3.13
```

**Node.js/npx가 없는 경우**:

```bash
# macOS (Homebrew)
brew install node

# Ubuntu/Debian
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# Windows (WSL)
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs
```

---

## 2. 기존 설치 제거

### 2.0 사전 설치 확인 (권장)

**포괄적인 검증을 위해 자동화된 사전 설치 검사기를 사용하십시오**:

```bash
# 자동 수정으로 포괄적인 사전 설치 확인 실행
python3 _config/MOAI-ADK/scripts/pre-install-check.py --auto-fix

# 또는 수정 없이 확인만 실행
python3 _config/MOAI-ADK/scripts/pre-install-check.py
```

**예상 출력**:
```
🔍 MoAI-ADK Pre-Install Check
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 System Requirements
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Python version: 3.13.0 (>= 3.11 required)
✅ Git installed: 2.39.0
✅ Node.js/npx installed: 20.10.0
✅ pip available: 24.0

🧹 Cleanup Status
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️  Found Claude Flow installation
   - .claude-flow/
   - .swarm/
   Auto-fix: ✅ Removed

⚠️  Found old MoAI installation
   - .venv/
   - .moai/
   Auto-fix: ✅ Removed

✅ System is ready for MoAI-ADK installation
```

**확인 항목**:
- ✅ Python 3.11+ 설치됨
- ✅ Git 및 npx 사용 가능
- ✅ Claude Flow 감지 및 제거
- ✅ 이전 MoAI 설치 감지 및 제거
- ✅ 시스템 준비 상태 검증

**장점**:
- 한 번의 명령으로 모든 것을 확인
- `--auto-fix`로 일반적인 문제 자동 수정
- 설치 충돌 방지
- 수동 확인 10-15분 절약

---

### 2.1 방법 1: 자동화된 정리 (권장)

**타겟팅된 제거를 위해 전문화된 정리 스크립트를 사용하십시오**:

**Claude Flow 제거**:
```bash
# 자동화된 Claude Flow 제거
python3 _config/MOAI-ADK/scripts/uninstall-claude-flow.py

# 자동 확인으로 (프롬프트 건너뛰기)
python3 _config/MOAI-ADK/scripts/uninstall-claude-flow.py --yes
```

**dot 폴더 정리** (`.claude-flow`, `.swarm`, `.moai` 등):
```bash
# 확인과 함께 대화형 정리
python3 _config/MOAI-ADK/scripts/clean-dot-folders.py

# 모든 제거 자동 확인
python3 _config/MOAI-ADK/scripts/clean-dot-folders.py --yes

# 드라이 런 (제거될 항목 미리보기)
python3 _config/MOAI-ADK/scripts/clean-dot-folders.py --dry-run
```

**예상 출력** (Claude Flow 제거 도구):
```
🗑️  Claude Flow Uninstaller
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔍 Scanning for Claude Flow installations...

Found directories:
  ✓ .claude-flow/
  ✓ .swarm/
  ✓ .hive-mind/

Found packages:
  ✓ claude-flow (global npm)

Remove these items? [y/N]: y

🧹 Cleaning up...
  ✅ Removed .claude-flow/
  ✅ Removed .swarm/
  ✅ Uninstalled claude-flow (npm)

✅ Claude Flow uninstalled successfully!
```

---

### 2.2 방법 2: 수동 정리

수동 제어를 선호하거나 자동화된 스크립트를 사용할 수 없는 경우:

**Claude Flow 제거 (존재하는 경우)**:

**중요**: MoAI-ADK는 Claude Flow와 호환되지 않습니다. 완전한 제거가 필요합니다.

```bash
# Claude Flow 디렉토리 제거
rm -rf .claude-flow
rm -rf .swarm
rm -rf .hive-mind
rm -rf .specstory
rm -rf node_modules/.cache/claude-flow

# 전역 npm 패키지 제거
npm uninstall -g claude-flow

# 제거 확인
ls -la | grep -E "\.claude-flow|\.swarm|\.hive-mind|\.specstory"
# 결과가 없어야 합니다
```

**기존 MoAI-ADK 설치 정리**:

이전 MoAI-ADK 설치가 있는 경우:

```bash
# 기존 가상 환경 제거
rm -rf .venv

# 기존 설정 제거 (최신 버전으로 교체됨)
rm -rf .moai
rm -rf .claude
rm -f .mcp.json
rm -f CLAUDE.md

# Python 패키지 제거 (전역으로 설치된 경우)
pip uninstall moai-adk -y
```

**깨끗한 상태 확인**:

```bash
# 남은 파일 확인
ls -la | grep -E "\.moai|\.claude|\.venv|\.mcp\.json"
# 결과가 없어야 합니다 (다른 Claude Code 설정이 있는 경우 .claude 폴더 제외)

# Python 패키지 확인
pip list | grep moai-adk
# 결과가 없어야 합니다
```

---

**권장사항**: 가장 빠르고 신뢰할 수 있는 정리를 위해 방법 1 (자동화된 스크립트)을 사용하십시오. 스크립트를 사용할 수 없는 경우에만 방법 2 (수동)를 사용하십시오.

---

## 3. 최신 MoAI-ADK 릴리스 가져오기

### 3.0 최신 버전 확인 (자동화)

**pre-install-check.py 스크립트는 이미 최신 버전이 사용 가능한지 확인했습니다**. 섹션 2.0을 건너뛴 경우 자동화된 버전 검사기를 사용하십시오:

```bash
# 버전 검사기 실행 (_config 디렉토리가 있는 경우)
python3 _config/MOAI-ADK/scripts/check-latest-version.py

# 또는 AI 강화 분석을 위한 Claude Agent SDK 모드로
python3 _config/MOAI-ADK/scripts/check-latest-version.py --agent
```

**또는 직접 다운로드**:

```bash
# 버전 검사기 스크립트 다운로드
curl -o check-latest-version.py https://raw.githubusercontent.com/modu-ai/moai-adk/main/_config/check-latest-version.py

# 버전 검사기 실행
python3 check-latest-version.py

# 또는 AI 강화 모드로 (claude-agent-sdk 필요)
python3 check-latest-version.py --agent
```

**예상 출력**:
```
🔍 MoAI-ADK Version Checker
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📦 Version Information
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Installed: ❌ Not installed
Latest:    🌟 v0.30.2

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 Recommendation: Install MoAI-ADK
```

**스크립트는 자동으로**:
- ✅ `moai-adk --version`을 통해 설치된 버전 확인
- ✅ GitHub API에서 최신 릴리스 가져오기 (클론 불필요)
- ✅ 버전 비교 및 조치 권장
- ✅ 업데이트 사용 가능 시 업그레이드 명령 제공

**기능**:
- **저장소 클론 불필요** - GitHub API 사용
- **대체 방법** - API가 다운되어도 작동
- **스마트 비교** - 시맨틱 버전 관리 인식
- **업그레이드 지침** - 정확한 업데이트 명령 표시

**참고**: 섹션 2.0에서 `pre-install-check.py --auto-fix`를 실행한 경우 이 버전 확인이 이미 자동으로 수행되었습니다.

### 3.1 MoAI-ADK 저장소 클론

```bash
# 소스 코드를 위한 임시 디렉토리 생성
mkdir -p moai-adk-source
cd moai-adk-source

# 저장소 클론
git clone https://github.com/modu-ai/moai-adk.git
cd moai-adk

# 모든 태그 가져오기
git fetch --tags

# 최신 릴리스 태그 가져오기
LATEST_TAG=$(git describe --tags `git rev-list --tags --max-count=1`)
echo "Latest release: $LATEST_TAG"

# 최신 릴리스 체크아웃
git checkout $LATEST_TAG

# 프로젝트 루트로 돌아가기
cd ../..
```

**예상 출력**:
```
Latest release: v0.30.2
Previous HEAD position was xxxxxxx...
HEAD is now at xxxxxxx Release v0.30.2
```

### 3.2 릴리스 버전 확인

```bash
# 현재 버전 표시
cd moai-adk-source/moai-adk
grep "^version" pyproject.toml
cd ../..
```

**예상 출력**:
```
version = "0.30.2"
```

---

## 4. MoAI-ADK 설치

### 4.1 Python 가상 환경 생성

```bash
# 프로젝트 루트에 가상 환경 생성
python3 -m venv .venv

# 가상 환경 활성화
source .venv/bin/activate

# 활성화 확인 (.venv 경로가 표시되어야 함)
which python
```

**예상 출력**:
```
/path/to/your/project/.venv/bin/python
```

### 4.2 개발 종속성과 함께 MoAI-ADK 설치

```bash
# 모든 종속성과 함께 편집 가능/개발 모드로 설치
pip install -e './moai-adk-source/moai-adk[dev]'

# 설치 완료 대기 (2-3분)
```

**예상 출력**:
```
Successfully installed moai-adk-0.30.2 click-8.1.x rich-13.x.x ...
```

**설치되는 주요 종속성** (v0.30.2):
- `click` - CLI 프레임워크
- `rich` - 아름다운 터미널 출력
- `pyfiglet` - ASCII 아트 배너
- `questionary` - 대화형 프롬프트
- `gitpython` - Git 작업
- `pytest` - 테스팅 프레임워크
- `google-genai` - Gemini 통합
- `pillow` - 이미지 처리
- `aiohttp` - 비동기 HTTP

### 4.3 설정 파일 복사

```bash
# MoAI 설정 복사
cp -r moai-adk-source/moai-adk/.moai .

# Claude Code 명령 복사
mkdir -p .claude/commands
cp -r moai-adk-source/moai-adk/.claude/commands/moai .claude/commands/

# MCP 서버 설정 복사
cp moai-adk-source/moai-adk/.mcp.json .

# CLAUDE.md 복사 (Alfred의 실행 지시문)
cp moai-adk-source/moai-adk/CLAUDE.md .

# 올바른 권한 설정
chmod -R 755 .moai
chmod -R 755 .claude
```

### 4.4 소스 파일 정리 (선택사항)

```bash
# 공간 절약을 위해 소스 디렉토리 제거
# 경고: 설치 성공 후에만 수행하십시오
rm -rf moai-adk-source
```

---

## 5. 설치 확인

### 5.1 설치 확인

```bash
# 가상 환경 활성화 (아직 활성화되지 않은 경우)
source .venv/bin/activate

# MoAI-ADK 버전 확인
moai-adk --version
```

**예상 출력**:
```
MoAI-ADK, version 0.30.2
```

### 5.2 시스템 진단 실행

```bash
# 포괄적인 시스템 확인 실행
moai-adk doctor
```

**예상 출력**:
```
Running system diagnostics...

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┓
┃ Check                                    ┃ Status ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━┩
│ Python >= 3.11                           │   ✓    │
│ Git installed                            │   ✓    │
│ Project structure (.moai/)               │   ✓    │
│ Config file (.moai/config/config.json)   │   ✓    │
└──────────────────────────────────────────┴────────┘

✓ All checks passed
```

### 5.3 프로젝트 상태 확인

```bash
# 프로젝트 상태 보기
moai-adk status
```

**예상 출력**:
```
╭───── Project Status ──────╮
│   Mode      development   │
│   Locale    ko            │
│   SPECs     0             │
╰───────────────────────────╯
```

### 5.4 Python 모듈 확인

```bash
# Python import 테스트
python -c "import moai_adk; print('✅ Version:', moai_adk.__version__)"
```

**예상 출력**:
```
✅ Version: 0.30.2
```

### 5.5 설정 구조 확인

```bash
# 설정 파일 확인
ls -la .moai/config/
ls -la .moai/config/presets/
ls -la .claude/commands/moai/
cat .mcp.json
```

**예상 출력**:
```
.moai/config/
├── config.json
├── presets/
│   ├── manual-local.json
│   ├── personal-github.json
│   └── team-github.json
└── statusline-config.yaml

.claude/commands/moai/
├── 0-project.md
├── 1-plan.md
├── 2-run.md
├── 3-sync.md
├── 9-feedback.md
├── 99-release.md
└── cleanup.md

.mcp.json (MCP 서버 설정됨)
```

### 5.6 MCP 서버 확인 (자동화)

**자동화된 확인 스크립트를 사용하십시오**:

```bash
# 포괄적인 MCP 서버 확인 실행
python3 _config/MOAI-ADK/scripts/verify-mcp-servers.py
```

**예상 출력**:
```
🔌 MCP Server Verification
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Found .mcp.json configuration

📋 Configured MCP Servers
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Testing: context7
  Status: ✅ npx available
  Package: ✅ Available on npm

Testing: sequential-thinking
  Status: ✅ npx available
  Package: ✅ Available on npm

Testing: playwright
  Status: ✅ npx available
  Package: ✅ Available on npm

Testing: figma-dev-mode-mcp-server
  Status: ⚠️  Not accessible (may need to start server)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Summary
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total servers:  4
Passed:         3 ✅
Failed:         1 ❌
```

**설정된 MCP 서버**:

```json
{
  "mcpServers": {
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp@latest"]
    },
    "playwright": {
      "command": "npx",
      "args": ["-y", "@playwright/mcp@latest"]
    },
    "sequential-thinking": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking@latest"]
    },
    "figma-dev-mode-mcp-server": {
      "type": "sse",
      "url": "http://127.0.0.1:3845/sse"
    }
  }
}
```

Claude Code에서 프롬프트가 표시되면 **모든 권한을 허용**하십시오:
- ✅ `mcp__context7__*` (모든 권한)
- ✅ `mcp__sequential-thinking__*` (모든 권한)
- ✅ `mcp__playwright__*` (모든 권한)

**참고**: 디자인 통합이 필요한 경우 Figma 서버는 수동 시작이 필요합니다.

---

## 6. 문제 해결

### 문제: "moai-adk: command not found"

**해결책 1**: 가상 환경 활성화
```bash
source .venv/bin/activate
moai-adk --version
```

**해결책 2**: 설치 확인
```bash
pip list | grep moai-adk
# 찾을 수 없는 경우 재설치
pip install -e './moai-adk-source/moai-adk[dev]'
```

### 문제: "Python version incompatible"

**해결책**: Python 3.11+ 설치
```bash
# macOS
brew install python@3.13

# Ubuntu/Debian
sudo apt-get install python3.13

# 가상 환경 재생성
rm -rf .venv
python3.13 -m venv .venv
source .venv/bin/activate
pip install -e './moai-adk-source/moai-adk[dev]'
```

### 문제: 설치 중 "Permission denied"

**해결책**: 디렉토리 권한 확인
```bash
# 권한 수정
chmod -R 755 .moai
chmod -R 755 .claude

# 설치 재시도
pip install -e './moai-adk-source/moai-adk[dev]'
```

### 문제: "Git not found" 또는 "No tags available"

**해결책**: git 설치 및 태그 가져오기
```bash
# git 설치 (macOS)
brew install git

# git 설치 (Ubuntu/Debian)
sudo apt-get install git

# 태그 가져오기
cd moai-adk-source/moai-adk
git fetch --tags
git describe --tags `git rev-list --tags --max-count=1`
```

### 문제: [dev]와 함께 "Shell parameter expansion error"

**해결책**: 패키지 경로를 따옴표로 묶기
```bash
# 잘못됨
pip install -e ./moai-adk-source/moai-adk[dev]

# 올바름
pip install -e './moai-adk-source/moai-adk[dev]'
```

### 문제: MCP 서버가 연결되지 않음

**해결책**: npx가 설치되어 있고 서버에 액세스할 수 있는지 확인
```bash
# npx 테스트
npx --version

# MCP 서버 수동 테스트
npx -y @upstash/context7-mcp@latest

# 수정 후 Claude Code 재시작
```

### 문제: `moai-adk init` 중 "Invalid argument"

**원인**: 대화형 프롬프트가 비TTY 환경에서 작동하지 않음

**해결책**: 설정 파일이 이미 복사되었으므로 `moai-adk init` 건너뛰기
```bash
# 설정이 존재하는지 확인
ls -la .moai/config/config.json
# 존재하면 MoAI-ADK를 사용할 준비가 된 것입니다
```

### 문제: 이전 설정 충돌

**해결책**: 제거 후 설정 재설치
```bash
# 이전 설정 백업 (필요한 경우)
cp -r .moai .moai.backup

# 이전 설정 제거
rm -rf .moai .claude .mcp.json CLAUDE.md

# 소스에서 새 설정 복사
cp -r moai-adk-source/moai-adk/.moai .
cp -r moai-adk-source/moai-adk/.claude/commands/moai .claude/commands/
cp moai-adk-source/moai-adk/.mcp.json .
cp moai-adk-source/moai-adk/CLAUDE.md .
```

---

## 7. 다음 단계

### 7.1 Git 전략 설정

`.moai/config/config.json` 편집:

```json
{
  "git_strategy": {
    "mode": "manual"  // 필요에 따라 "personal" 또는 "team"으로 변경
  }
}
```

**Git 전략 모드**:
- `manual` - 로컬 Git만 사용, 수동 브랜치 생성 (기본값)
- `personal` - 자동화된 GitHub 개인 프로젝트
- `team` - 완전한 거버넌스를 갖춘 GitHub 팀 프로젝트

프리셋 파일은 `.moai/config/presets/`에서 자동으로 로드됩니다

### 7.2 Claude Code 실행

```bash
# 가상 환경이 활성화되어 있는지 확인
source .venv/bin/activate

# Claude Code 실행
claude
```

### 7.3 MoAI 명령 사용 시작

Claude Code 내에서 다음 명령을 사용하십시오:

**프로젝트 관리**:
```
/moai:0-project          프로젝트 구조 초기화
```

**SPEC-First TDD 워크플로우**:
```
/moai:1-plan "기능"      SPEC 문서 생성
/moai:2-run SPEC-001     TDD로 구현 (RED-GREEN-REFACTOR)
/moai:3-sync SPEC-001    문서 동기화 및 PR 생성
```

**피드백 루프**:
```
/moai:9-feedback "improvement: <설명>"
```

**정리**:
```
/moai:cleanup            프로젝트 파일 정리
```

### 7.4 첫 번째 기능 테스트

다음 워크플로우를 시도해보십시오:

1. **계획**: `/moai:1-plan "사용자 인증 추가"`
2. **구현**: `/moai:2-run SPEC-001`
3. **문서화**: `/moai:3-sync SPEC-001`

`/moai:1-plan` 완료 후 컨텍스트를 재초기화하기 위해 **`/clear` 실행** (권장).

### 7.5 MCP 권한 허용

Claude Code에서 권한을 요청하면 **모두 허용**하십시오:

- ✅ 모든 `mcp__context7__*` 도구 허용
- ✅ 모든 `mcp__sequential-thinking__*` 도구 허용
- ✅ 모든 `mcp__playwright__*` 도구 허용

이는 MoAI-ADK 기능에 필수적입니다.

### 7.6 이름 설정 (선택사항)

`.moai/config/config.json` 편집:

```json
{
  "user": {
    "name": "YourName"  // Alfred가 이름으로 호칭합니다
  }
}
```

### 7.7 언어 조정 (선택사항)

`.moai/config/config.json` 편집:

```json
{
  "language": {
    "conversation_language": "en",  // "ko", "ja", "zh" 등
    "conversation_language_name": "English"
  }
}
```

---

## 8. 한국어 언어 지원 🇰🇷

MoAI-ADK는 **내장 한국어 지원**을 제공합니다. 시스템은 한국어를 기본 대화 언어로 사용하도록 사전 구성되어 있습니다.

### 언어 설정

**설정 파일**: `.moai/config/config.json`

```json
"language": {
    "conversation_language": "ko",
    "conversation_language_name": "Korean",
    "agent_prompt_language": "ko",
    "notes": "Language for sub-agent internal prompts"
}
```

### 한국어 문서

- **한국어 README**: `moai-adk/README.ko.md` (51KB)
- **전체 문서** 한국어로 제공
- **CLI 지원**: `--language ko` 플래그 사용

### 폰트 지원

특별한 폰트 설정이 필요하지 않습니다:
- 한국어는 Unicode/UTF-8을 통해 작동합니다
- 한국어 호환 터미널 폰트 사용:
  - **macOS**: D2Coding, Nanum Gothic Coding
  - **Windows**: Malgun Gothic, D2Coding
  - **Linux**: Nanum Gothic, Source Code Pro

### 언어 변경

한국어에서 다른 언어로 변경하려면:

```bash
# 설정 파일 편집
vim .moai/config/config.json

# 영어로 변경
"conversation_language": "en"

# 또는 CLI 플래그 사용
moai-adk --language en [command]
```

### 지원되는 언어

- **Korean (ko)** - 한국어 (기본값)
- **English (en)** - English
- **Japanese (ja)** - 日本語
- **Chinese (zh)** - 中文

---

## 9. MoAI-ADK 이해하기

### 주요 구성 요소

**Mr.Alfred** - 다음을 수행하는 SuperAgent 오케스트레이터:
- 요청 분석 (8단계 프로세스)
- 전문화된 에이전트로 실행 계획
- 24개 이상의 도메인 전문가에게 작업 위임
- 토큰 최적화 관리 (세션당 5,000개 이상의 토큰 절약)

**26개의 전문화된 에이전트** (5계층 계층 구조):
```
계층 1: expert-*   (도메인 전문가)      - 7개 에이전트
계층 2: manager-*  (워크플로우 관리자)   - 8개 에이전트
계층 3: builder-*  (메타 생성)         - 3개 에이전트
계층 4: mcp-*      (MCP 통합)          - 5개 에이전트
계층 5: ai-*       (AI 서비스)          - 1개 에이전트
```

**3가지 핵심 스킬**:
- `moai-foundation-core` - 기초 지식 (8,470 토큰)
- `moai-lang-unified` - 언어 전문 지식
- 추가 전문화된 스킬

### 워크플로우 철학

**SPEC-First**:
1. 코드 전에 SPEC 작성 (EARS 형식)
2. SPEC에서 테스트 자동 생성
3. RED-GREEN-REFACTOR로 구현
4. 문서 자동 동기화

**TDD 적용**:
- 85% 이상 테스트 커버리지 필요
- 구현 전에 테스트 작성
- 품질 게이트가 저품질 코드 방지

**토큰 최적화**:
- 간단한 작업: 0 토큰 (빠른 참조)
- 복잡한 작업: 8,470 토큰 (자동 로드 스킬)
- 평균 절감: 세션당 5,000 토큰

---

## 10. 고급 설정

### 자동 브랜치 생성 활성화

`.moai/config/config.json` 편집:

```json
{
  "git_strategy": {
    "branch_creation": {
      "prompt_always": false,
      "auto_enabled": true
    }
  }
}
```

### 테스트 커버리지 목표 변경

`.moai/config/config.json` 편집:

```json
{
  "constitution": {
    "test_coverage_target": 90  // 기본값: 90%
  }
}
```

### 자동 보고서 활성화

`.moai/config/config.json` 편집:

```json
{
  "report_generation": {
    "auto_create": true  // 기본값: false (최소 보고서)
  }
}
```

### MCP 서버 사용자 정의

서버를 추가/제거하려면 `.mcp.json` 편집:

```json
{
  "mcpServers": {
    "your-custom-server": {
      "command": "npx",
      "args": ["-y", "your-package@latest"]
    }
  }
}
```

---

## 11. 빠른 참조 카드

```bash
# 사전 설치 및 정리
python3 _config/MOAI-ADK/scripts/pre-install-check.py --auto-fix    # 포괄적인 사전 설치 확인
python3 _config/MOAI-ADK/scripts/uninstall-claude-flow.py           # Claude Flow 제거
python3 _config/MOAI-ADK/scripts/clean-dot-folders.py               # dot 폴더 정리

# 설치 및 업데이트
source .venv/bin/activate              # 항상 먼저 활성화
python3 _config/MOAI-ADK/scripts/check-latest-version.py            # 스마트 버전 확인 및 업데이트 가이드
python3 _config/MOAI-ADK/scripts/verify-mcp-servers.py              # MCP 서버 설정 확인
moai-adk --version                     # 버전 확인
moai-adk doctor                        # 진단 실행

# 명령 (Claude Code 내)
/moai:0-project                        # 프로젝트 초기화
/moai:1-plan "설명"                    # SPEC 생성
/moai:2-run SPEC-001                   # TDD 구현
/moai:3-sync SPEC-001                  # 문서 동기화
/moai:9-feedback "유형: 설명"          # 피드백 제출
/clear                                 # 컨텍스트 재설정 (/moai:1-plan 후)

# 설정
.moai/config/config.json               # 주 설정
.moai/config/presets/                  # Git 워크플로우 프리셋
.claude/commands/moai/                 # MoAI 명령
.mcp.json                              # MCP 서버
CLAUDE.md                              # Alfred의 지시문

# 확인
ls -la .moai .claude .mcp.json         # 파일 존재 확인
pip list | grep moai-adk               # 패키지 확인
moai-adk status                        # 프로젝트 상태
```

---

## 12. 도움말 받기

**문서**:
- GitHub: https://github.com/modu-ai/moai-adk
- README: https://github.com/modu-ai/moai-adk/blob/main/README.md
- 릴리스: https://github.com/modu-ai/moai-adk/releases

**지원**:
- 이슈: https://github.com/modu-ai/moai-adk/issues
- 피드백: Claude Code 내에서 `/moai:9-feedback` 사용

**Claude Code 내**:
- Alfred가 CLAUDE.md를 기반으로 자동으로 도움을 제공합니다
- 전체 기능을 위해 모든 MCP 권한 허용
- 도움이 필요하면 `/moai:9-feedback "question: <질문>"` 사용

---

## 13. 유지보수

### 업데이트 확인 (자동화)

**스마트 버전 검사기를 사용하십시오**:

```bash
# 먼저 가상 환경 활성화
source .venv/bin/activate

# 버전 검사기 실행
python3 _config/MOAI-ADK/scripts/check-latest-version.py
```

**예상 출력 (업데이트 사용 가능)**:
```
🔍 MoAI-ADK Version Checker
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📦 Version Information
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Installed: ✅ v0.29.0
Latest:    🌟 v0.30.2

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⬆️  Update available: v0.29.0 → v0.30.2

To update, run:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 1. 최신 릴리스 가져오기
cd moai-adk-source/moai-adk
git fetch --tags
git checkout v0.30.2
cd ../..

# 2. 재설치
source .venv/bin/activate
pip install -e './moai-adk-source/moai-adk[dev]' --upgrade

# 3. 설정 업데이트
cp -r moai-adk-source/moai-adk/.moai .
cp -r moai-adk-source/moai-adk/.claude/commands/moai .claude/commands/
cp moai-adk-source/moai-adk/.mcp.json .
cp moai-adk-source/moai-adk/CLAUDE.md .

# 4. 확인
moai-adk --version
moai-adk doctor
```

**예상 출력 (최신 상태)**:
```
✅ You have the latest version installed!
```

### 최신 버전으로 수동 업데이트

수동 제어를 선호하는 경우:

```bash
# 가상 환경 활성화
source .venv/bin/activate

# 최신 변경사항 가져오기
cd moai-adk-source/moai-adk
git fetch --tags
LATEST_TAG=$(git describe --tags `git rev-list --tags --max-count=1`)
git checkout $LATEST_TAG

# 재설치
cd ../..
pip install -e './moai-adk-source/moai-adk[dev]' --upgrade

# 설정 파일 업데이트
cp -r moai-adk-source/moai-adk/.moai .
cp -r moai-adk-source/moai-adk/.claude/commands/moai .claude/commands/
cp moai-adk-source/moai-adk/.mcp.json .
cp moai-adk-source/moai-adk/CLAUDE.md .

# 확인
moai-adk --version
moai-adk doctor
```

### 설정 백업

```bash
# 업데이트 전 백업
cp -r .moai .moai.backup.$(date +%Y%m%d)
cp -r .claude .claude.backup.$(date +%Y%m%d)
cp .mcp.json .mcp.json.backup.$(date +%Y%m%d)
```

---

## 14. 제거

MoAI-ADK를 완전히 제거하려면:

```bash
# 가상 환경 제거
rm -rf .venv

# 설정 제거
rm -rf .moai
rm -rf .claude/commands/moai
rm -f .mcp.json
rm -f CLAUDE.md

# 소스 제거 (보관한 경우)
rm -rf moai-adk-source

# 패키지 제거 (전역으로 설치된 경우)
pip uninstall moai-adk -y
```

---

**설치 가이드 버전**: 1.0.0
**마지막 업데이트**: 2025-11-28
**MoAI-ADK 버전**: 0.30.2
**테스트 환경**: macOS, Ubuntu 22.04, WSL2

**드래그 앤 드롭 준비**: 이 파일을 모든 프로젝트 폴더에 복사하여 단계별로 따라할 수 있습니다.
