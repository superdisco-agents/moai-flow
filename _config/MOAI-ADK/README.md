# MoAI-ADK Installation & Configuration

This directory contains MoAI-ADK specific installation guides, scripts, and configuration files.

## 📋 Contents

### Installation Guide

**`INSTALL-MOAI-ADK.md`** - Comprehensive installation guide for MoAI-ADK v0.30.2+

**Features**:
- ✅ Workspace-agnostic - Works in any directory
- ✅ Complete cleanup - Removes claude-flow and old installations
- ✅ Latest release - Always fetches newest version from GitHub
- ✅ Full verification - Tests all components after installation
- ✅ Troubleshooting - Common issues and solutions
- ✅ Claude Code optimized - Designed for Claude Code workflow

**Time Required**: 15-20 minutes

**Prerequisites**: Python 3.11+, Git, Node.js

### Verification & Utility Scripts (5 Total)

#### 1. **`scripts/pre-install-check.py`** - System Requirements Validator

**Purpose**: Validates all prerequisites before MoAI-ADK installation

**Features**:
- ✅ Comprehensive checks - Python, Node.js, npm, git, pip, disk space, network
- ✅ Version validation - Ensures minimum requirements are met
- ✅ Network testing - Checks GitHub and npm registry accessibility
- ✅ Conflict detection - Identifies existing installations and conflicts
- ✅ Multiple output formats - Human-readable or JSON
- ✅ Exit codes - 0 (ready), 1 (errors), 2 (warnings), 3 (conflicts)

**Usage**:
```bash
# Standard check
python3 _config/MOAI-ADK/scripts/pre-install-check.py

# Verbose output
python3 _config/MOAI-ADK/scripts/pre-install-check.py --verbose

# JSON output (for automation)
python3 _config/MOAI-ADK/scripts/pre-install-check.py --json
```

**Checks Performed**:
- Python 3.11+ installed
- Node.js 18.0.0+ installed
- npm 9.0.0+ installed
- Git 2.30.0+ installed
- pip 23.0+ installed
- 500MB+ disk space available
- GitHub accessible
- npm registry accessible
- No conflicting installations

#### 2. **`scripts/uninstall-claude-flow.py`** - Claude Flow Removal Tool

**Purpose**: Safely removes claude-flow installations and related directories

**Features**:
- ✅ Dry-run mode - Preview changes before execution
- ✅ Comprehensive scanning - Finds all claude-flow directories
- ✅ Safe removal - Protected folders never touched
- ✅ Size reporting - Shows space to be freed
- ✅ JSON reports - Detailed removal logs saved
- ✅ Cross-platform - Works on macOS, Linux, Windows

**Usage**:
```bash
# Dry-run (preview only)
python3 _config/MOAI-ADK/scripts/uninstall-claude-flow.py --dry-run

# Execute removal
python3 _config/MOAI-ADK/scripts/uninstall-claude-flow.py
```

**What It Removes**:
- `.claude-flow/` directories
- `.swarm/` directories
- `.specstory/` directories
- npm global packages (claude-flow)
- Cache and temp files

**Protected Folders**: `.git`, `.moai`, `.claude`, `.venv`, `.env`

#### 3. **`scripts/clean-dot-folders.py`** - Dot Folder Cleanup Utility

**Purpose**: Scans and removes development dot folders safely

**Features**:
- ✅ Scan-only mode - Non-destructive inspection
- ✅ Smart detection - Identifies AI framework conflicts
- ✅ Protection system - Never removes critical folders
- ✅ Size analysis - Reports space usage
- ✅ Categorization - Groups folders by type (MoAI, whitelisted, conflicts)
- ✅ Detailed reporting - Color-coded output

**Usage**:
```bash
# Scan only (no changes)
python3 _config/MOAI-ADK/scripts/clean-dot-folders.py --scan-only

# Interactive cleanup
python3 _config/MOAI-ADK/scripts/clean-dot-folders.py

# Auto-remove all conflicts
python3 _config/MOAI-ADK/scripts/clean-dot-folders.py --auto-remove
```

**Detection Categories**:
- **MoAI folders** (protected): `.moai`, `.claude`, `.claude-flow`
- **Whitelisted** (protected): `.git`, `.venv`, `.env`
- **Conflicts** (removable): `.specstory`, `.swarm`, other AI frameworks

#### 4. **`scripts/check-latest-version.py`** - Version Checker

**Purpose**: Checks for MoAI-ADK updates from GitHub

**Features**:
- ✅ Pure Python - Cross-platform compatible
- ✅ No cloning required - Uses GitHub API
- ✅ Automatic detection - Finds installed version
- ✅ Smart comparison - Semantic versioning aware
- ✅ Upgrade guidance - Shows exact commands
- ✅ Dual modes - Standalone (fast) or Agent SDK (AI-enhanced)

**Usage**:
```bash
# Standalone mode (fast)
python3 _config/MOAI-ADK/scripts/check-latest-version.py

# Agent SDK mode (AI-enhanced)
python3 _config/MOAI-ADK/scripts/check-latest-version.py --agent
```

**Exit Codes**:
- 0: Up to date or installed version is newer
- 1: GitHub API failed
- 2: Not installed
- 3: Update available

#### 5. **`scripts/verify-mcp-servers.py`** - MCP Server Verification

**Purpose**: Tests MCP server configuration and connectivity

**Features**:
- ✅ Pure Python - Cross-platform compatible
- ✅ Comprehensive testing - Checks all configured MCP servers
- ✅ Smart detection - Distinguishes stdio vs SSE servers
- ✅ Package validation - Verifies npm packages
- ✅ Detailed reporting - Shows server purpose, criticality
- ✅ Dual modes - Standalone or Agent SDK

**Usage**:
```bash
# Standalone mode (fast)
python3 _config/MOAI-ADK/scripts/verify-mcp-servers.py

# Agent SDK mode (AI diagnostics)
python3 _config/MOAI-ADK/scripts/verify-mcp-servers.py --agent
```

**Exit Codes**:
- 0: All servers passed
- 1: One or more servers failed or not accessible

## 🚀 Quick Start

### Install MoAI-ADK

1. Open the installation guide:
   ```bash
   cat _config/MOAI-ADK/INSTALL-MOAI-ADK.md
   ```

2. Follow step-by-step instructions

3. Verify installation:
   ```bash
   python3 _config/MOAI-ADK/scripts/check-latest-version.py
   python3 _config/MOAI-ADK/scripts/verify-mcp-servers.py
   ```

### Recommended Workflow

**Before Installation**:
```bash
# 1. Check system requirements
python3 _config/MOAI-ADK/scripts/pre-install-check.py

# 2. Clean up conflicts (if detected)
python3 _config/MOAI-ADK/scripts/clean-dot-folders.py --scan-only
python3 _config/MOAI-ADK/scripts/uninstall-claude-flow.py --dry-run

# 3. If conflicts found, remove them
python3 _config/MOAI-ADK/scripts/clean-dot-folders.py
python3 _config/MOAI-ADK/scripts/uninstall-claude-flow.py
```

**After Installation**:
```bash
# 4. Verify installation
python3 _config/MOAI-ADK/scripts/check-latest-version.py
python3 _config/MOAI-ADK/scripts/verify-mcp-servers.py

# 5. Check MoAI status
moai-adk --version
moai-adk doctor
moai-adk status
```

### What Gets Installed

After installation, your project will have:

```
your-project/
├── .venv/                          # Python virtual environment
├── .moai/                          # MoAI configuration
│   ├── config/
│   │   ├── config.json            # Main configuration
│   │   └── presets/               # Git workflow presets
│   └── memory/                    # Agent memory files
├── .claude/
│   └── commands/
│       └── moai/                  # MoAI commands (7 files)
├── .mcp.json                      # MCP server configuration
├── CLAUDE.md                      # Alfred execution directive
└── moai-adk-source/               # Source code (optional)
```

## 📦 Configuration Files

### `.moai/config/config.json`
Main configuration with:
- MoAI version tracking
- Git strategy (manual/personal/team)
- TDD enforcement rules
- Test coverage targets
- Language settings

### `.moai/config/presets/`
Git workflow presets:
- `manual-local.json` - Local development
- `personal-github.json` - Individual projects
- `team-github.json` - Team collaboration

### `.claude/commands/moai/`
7 MoAI commands:
- `0-project.md` - Project initialization
- `1-plan.md` - SPEC generation
- `2-run.md` - TDD implementation
- `3-sync.md` - Documentation sync
- `9-feedback.md` - Feedback submission
- `99-release.md` - Release management
- `cleanup.md` - Cleanup utilities

### `.mcp.json`
MCP server integration:
- **context7** - Real-time documentation (⭐⭐⭐ Critical)
- **sequential-thinking** - Complex reasoning (⭐⭐ Important)
- **playwright** - Browser automation (⭐ Optional)
- **figma-dev-mode** - Design integration (⭐ Optional)

### `CLAUDE.md`
Alfred execution directive (26KB):
- 10 core rules for Alfred
- Agent delegation patterns
- Token optimization strategies
- MCP integration guidelines

## ✅ Verification Checklist

After installation, verify:

- [ ] `moai-adk --version` shows v0.30.2+
- [ ] `moai-adk doctor` passes all checks
- [ ] `moai-adk status` displays project info
- [ ] `.moai/config/config.json` exists
- [ ] `.claude/commands/moai/` has 7 command files
- [ ] `.mcp.json` has 4 MCP servers configured
- [ ] `CLAUDE.md` exists at project root
- [ ] Python import works: `import moai_adk`

## 🔧 Troubleshooting

Common issues documented in `INSTALL-MOAI-ADK.md`:

- **Command not found** → Activate venv
- **Permission denied** → Fix file permissions
- **Python version** → Install Python 3.11+
- **Git tags missing** → Fetch tags from repo
- **MCP not connecting** → Install Node.js/npx

## 📊 Script Exit Codes

| Script | Exit Code | Meaning |
|--------|-----------|---------|
| **pre-install-check.py** | 0 | All requirements met |
| | 1 | Critical errors (missing dependencies) |
| | 2 | Warnings only (upgrades recommended) |
| | 3 | Conflicts detected (cleanup required) |
| **uninstall-claude-flow.py** | 0 | Successfully removed or nothing to remove |
| | 1 | Errors during removal |
| | 2 | Dry-run completed successfully |
| **clean-dot-folders.py** | 0 | Successfully cleaned or scan completed |
| | 1 | Errors during removal |
| **check-latest-version.py** | 0 | Up to date or installed version is newer |
| | 1 | GitHub API failed |
| | 2 | Not installed |
| | 3 | Update available |
| **verify-mcp-servers.py** | 0 | All servers passed |
| | 1 | One or more servers failed or not accessible |

## 🔄 Updates

To update the installation guide:

```bash
# Edit installation guide
vim _config/MOAI-ADK/INSTALL-MOAI-ADK.md

# Test changes with a fresh installation
# Copy to test project and verify all steps work
```

## 📚 Support

- **Documentation**: See `INSTALL-MOAI-ADK.md`
- **Issues**: https://github.com/modu-ai/moai-adk/issues
- **Feedback**: Use `/moai:9-feedback` in Claude Code

---

**Directory Purpose**: MoAI-ADK installation, configuration, and verification tools
**Target Audience**: Developers installing MoAI-ADK in new projects
**Maintenance**: Update when MoAI-ADK version changes or installation process updates
