# _config Directory

This directory contains **drag-and-drop installation guides and configuration resources** organized by component.

## 📁 Directory Structure

```
_config/
├── README.md                              # This file - directory overview
├── KOREAN-VERSION.md                      # 🇰🇷 Pointer to Korean-only version
├── MOAI-ADK/                              # MoAI-ADK installation & config (English)
│   ├── README.md                          # MoAI-ADK specific documentation
│   ├── INSTALL-MOAI-ADK.md               # Installation guide (v0.30.2+)
│   └── scripts/                           # Verification & utility scripts
│       ├── check-latest-version.py        # Version checker (dual mode)
│       ├── verify-mcp-servers.py          # MCP server verification
│       ├── pre-install-check.py           # System requirements validator
│       ├── uninstall-claude-flow.py       # Claude Flow removal tool
│       └── clean-dot-folders.py           # Dot folder cleanup utility
└── MOAI-ADK-KO/                           # 🇰🇷 100% Korean version
    ├── README.md                          # 메인 README (51 KB, 한글 전용)
    ├── INSTALL-MOAI-ADK.md               # 설치 가이드 (29 KB, 14개 섹션)
    ├── 빠른시작.md                         # 빠른 시작 가이드 (3단계)
    ├── 스크립트가이드.md                    # 스크립트 문서 (25 KB)
    ├── 완료보고서.md                        # 프로젝트 완료 보고서
    ├── 파일목록.md                          # 전체 파일 인벤토리
    ├── config/                            # 한글 전용 설정
    │   ├── config.json                    # 한글 모드 JSON 설정
    │   └── 설정가이드.md                    # 설정 사용 가이드
    ├── scripts/                           # 한글화된 스크립트 (355개 문자열)
    │   ├── setup-korean-environment.sh    # 자동 한글 환경 설정
    │   ├── check-latest-version.py        # 버전 체커 (45개 문자열)
    │   ├── verify-mcp-servers.py          # MCP 검증 (80개 문자열)
    │   ├── pre-install-check.py           # 사전 검사 (85개 문자열)
    │   ├── uninstall-claude-flow.py       # 제거 도구 (87개 문자열)
    │   └── clean-dot-folders.py           # 폴더 정리 (58개 문자열)
    └── docs/                              # 한글 문서
        └── 제거가이드-CLAUDE-FLOW.md        # Claude-Flow 제거 가이드
```

## 🎯 Purpose

The `_config/` directory stores **workspace-agnostic** configuration and installation documentation that can be copied to any project. Each subdirectory is self-contained with its own README and resources.

## 🇰🇷 NEW: Korean-Only Version

A complete Korean-only version of MoAI-ADK is now available in `MOAI-ADK-KO/`:

- ✅ **100% Korean documentation** (11 files, ~180 KB)
- ✅ **Korean CLI output** (5 Python scripts, 355 translated strings)
- ✅ **Ghostty Korean font setup** (D2Coding Nerd Font auto-install)
- ✅ **Korean-only configuration** (config.json Korean mode)
- ✅ **Automated setup script** (one-click environment)

**Quick Start**:
```bash
# See Korean version details
cat _config/KOREAN-VERSION.md

# Or jump directly to Korean directory
cd _config/MOAI-ADK-KO
cat 빠른시작.md
```

## 📦 Components

### 1. MOAI-ADK/ (English Version)

Complete MoAI-ADK installation and configuration resources.

**Key Files**:
- `INSTALL-MOAI-ADK.md` - Full installation guide (15-20 min)
- `scripts/` - 5 verification and utility scripts:
  1. `pre-install-check.py` - System requirements validator
  2. `uninstall-claude-flow.py` - Claude Flow removal tool
  3. `clean-dot-folders.py` - Dot folder cleanup utility
  4. `check-latest-version.py` - Version checker
  5. `verify-mcp-servers.py` - MCP server verification

**Quick Start**:
```bash
# Pre-installation workflow
python3 _config/MOAI-ADK/scripts/pre-install-check.py
python3 _config/MOAI-ADK/scripts/clean-dot-folders.py --scan-only
python3 _config/MOAI-ADK/scripts/uninstall-claude-flow.py --dry-run

# Read installation guide
cat _config/MOAI-ADK/INSTALL-MOAI-ADK.md

# Post-installation verification
python3 _config/MOAI-ADK/scripts/check-latest-version.py
python3 _config/MOAI-ADK/scripts/verify-mcp-servers.py
```

**See**: `MOAI-ADK/README.md` for detailed documentation

### 2. MOAI-ADK-KO/ (🇰🇷 Korean Version)

**NEW**: 100% Korean-localized version with Ghostty font support.

**Features**:
- All documentation translated to Korean (합니다체 formal style)
- All Python scripts output Korean messages
- Automatic D2Coding Nerd Font installation
- Ghostty configuration for perfect Korean rendering
- Korean-only configuration mode

**Quick Start**:
```bash
cd _config/MOAI-ADK-KO

# Read quick start guide (Korean, 3 steps)
cat 빠른시작.md

# Auto-setup Korean environment (D2Coding font + Ghostty)
bash scripts/setup-korean-environment.sh

# Read full installation guide (Korean, 14 sections)
cat INSTALL-MOAI-ADK.md
```

**Statistics**:
- **Total files**: 18
- **Documentation**: 11 files (100% Korean)
- **Scripts**: 6 files (5 Python + 1 Bash, all Korean output)
- **Translated strings**: 355
- **Total size**: ~180 KB

**See**: `MOAI-ADK-KO/완료보고서.md` for complete project report

## 🚀 Usage Patterns

### Method 1: Drag and Drop

1. Open target project in Claude Code
2. Drag desired configuration files into project
3. Follow instructions in the file

### Method 2: Copy Command

```bash
# Copy entire MOAI-ADK directory (English)
cp -r _config/MOAI-ADK /path/to/target/project/

# Copy Korean version
cp -r _config/MOAI-ADK-KO /path/to/target/project/

# Or copy specific files
cp _config/MOAI-ADK-KO/INSTALL-MOAI-ADK.md /path/to/target/project/
```

### Method 3: Direct Reference

```bash
# From target project, reference from this repo
curl -O https://raw.githubusercontent.com/modu-ai/moai-adk/main/_config/MOAI-ADK/INSTALL-MOAI-ADK.md

# Korean version
curl -O https://raw.githubusercontent.com/modu-ai/moai-adk/main/_config/MOAI-ADK-KO/빠른시작.md
```

## 📋 What Each Component Provides

### MoAI-ADK Installation (English)

After following `MOAI-ADK/INSTALL-MOAI-ADK.md`, your project gets:

```
your-project/
├── .venv/                          # Python virtual environment
├── .moai/                          # MoAI configuration
│   ├── config/config.json          # Main config
│   ├── config/presets/             # Git workflow presets (3)
│   └── memory/                     # Agent memory files
├── .claude/commands/moai/          # MoAI commands (7 files)
├── .mcp.json                       # MCP server config (4 servers)
└── CLAUDE.md                       # Alfred execution directive (26KB)
```

**MCP Servers Configured**:
- `context7` - Real-time documentation (⭐⭐⭐ Critical)
- `sequential-thinking` - Complex reasoning (⭐⭐ Important)
- `playwright` - Browser automation (⭐ Optional)
- `figma-dev-mode` - Design integration (⭐ Optional)

**MoAI Commands Available**:
1. `/moai:0-project` - Project initialization
2. `/moai:1-plan` - SPEC generation
3. `/moai:2-run` - TDD implementation
4. `/moai:3-sync` - Documentation sync
5. `/moai:9-feedback` - Feedback submission
6. `/moai:99-release` - Release management
7. `/moai:cleanup` - Cleanup utilities

### 🇰🇷 MoAI-ADK Korean Installation

Same as above, but with:
- ✅ All CLI output in Korean
- ✅ All documentation in Korean
- ✅ D2Coding Nerd Font configured
- ✅ Ghostty Korean font rendering
- ✅ Korean-only configuration mode

## ✅ Verification

### Pre-Installation Checks

**Before installing MoAI-ADK, run these checks**:

```bash
# English version
python3 _config/MOAI-ADK/scripts/pre-install-check.py

# Korean version (outputs in Korean)
python3 _config/MOAI-ADK-KO/scripts/pre-install-check.py

# Scan for conflicting dot folders
python3 _config/MOAI-ADK/scripts/clean-dot-folders.py --scan-only

# Check for existing claude-flow installations
python3 _config/MOAI-ADK/scripts/uninstall-claude-flow.py --dry-run
```

### Post-Installation Verification

**After installation, verify with these scripts**:

```bash
# Check MoAI-ADK version status
python3 _config/MOAI-ADK/scripts/check-latest-version.py

# Or Korean version
python3 _config/MOAI-ADK-KO/scripts/check-latest-version.py

# Verify MCP server configuration
python3 _config/MOAI-ADK/scripts/verify-mcp-servers.py

# Check MoAI-ADK installation
moai-adk --version
moai-adk doctor
moai-adk status
```

### Script Exit Codes

| Script | Exit Code | Meaning |
|--------|-----------|---------| 
| `pre-install-check.py` | 0 | Ready to install |
| | 1 | Missing dependencies |
| | 2 | Warnings only |
| | 3 | Conflicts detected |
| `uninstall-claude-flow.py` | 0 | Completed successfully |
| | 1 | Errors occurred |
| | 2 | Dry-run completed |
| `clean-dot-folders.py` | 0 | Cleaned successfully |
| | 1 | Errors occurred |
| `check-latest-version.py` | 0 | Up to date |
| | 1 | API failed |
| | 2 | Not installed |
| | 3 | Update available |
| `verify-mcp-servers.py` | 0 | All servers passed |
| | 1 | Servers failed |

## 🔧 Maintenance

### Updating Installation Guides

When MoAI-ADK version changes:

1. Update `MOAI-ADK/INSTALL-MOAI-ADK.md`
2. Update `MOAI-ADK-KO/INSTALL-MOAI-ADK.md` (Korean version)
3. Update version references in both README files
4. Test with fresh installation
5. Update this README if structure changes

### Adding New Components

To add new configuration components:

1. Create new subdirectory (e.g., `NEW-COMPONENT/`)
2. Add `NEW-COMPONENT/README.md`
3. Add component-specific files
4. Update this README with new section
5. Consider creating Korean version if applicable

## 📚 Support & Resources

- **MoAI-ADK Documentation**: See `MOAI-ADK/README.md`
- **Korean Version**: See `MOAI-ADK-KO/README.md` or `KOREAN-VERSION.md`
- **Issues**: https://github.com/modu-ai/moai-adk/issues
- **Feedback**: Use `/moai:9-feedback` in Claude Code

## 📊 Version History

- **2.1.0** (2025-11-28) - Added complete Korean-only version
  - Created `MOAI-ADK-KO/` directory with 18 files
  - Translated all documentation to Korean (11 files, ~180 KB)
  - Localized all Python scripts (5 scripts, 355 strings)
  - Added Ghostty Korean font setup (D2Coding Nerd Font)
  - Created Korean-only configuration mode
  - Added automated setup script
  - Added `KOREAN-VERSION.md` pointer document

- **2.0.0** (2025-11-28) - Reorganized into component subdirectories
  - Created `MOAI-ADK/` subdirectory structure
  - Moved scripts to `MOAI-ADK/scripts/`
  - Added component-specific READMEs
  - Maintained backward compatibility

- **1.0.0** (2025-11-28) - Initial workspace-agnostic guide
  - Complete cleanup procedures
  - Latest release checking
  - Comprehensive verification

---

**Directory Purpose**: Workspace-agnostic installation guides and configuration resources
**Target Audience**: Developers installing components in new projects  
**Languages**: English (MOAI-ADK/) and Korean (MOAI-ADK-KO/)
**Maintenance**: Update when component versions change or processes update

## 🇰🇷 한국어 버전 보기

한글 전용 버전은 `MOAI-ADK-KO/` 디렉토리에 있습니다.

```bash
# 한글 버전 안내 보기
cat _config/KOREAN-VERSION.md

# 한글 버전 디렉토리로 이동
cd _config/MOAI-ADK-KO

# 빠른 시작 가이드 읽기
cat 빠른시작.md
```
