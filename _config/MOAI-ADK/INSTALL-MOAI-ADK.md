# 🗿 MoAI-ADK Installation Guide for Claude Code

**Version**: 0.30.2 (Always installs latest release)
**Platform**: macOS, Linux, Windows (WSL)
**Python Required**: 3.11 - 3.14
**Time**: 15-20 minutes

This guide is **workspace-agnostic** — drag and drop this file into any Claude Code project to install MoAI-ADK from scratch.

---

## 📋 Table of Contents

1. [Prerequisites Check](#1-prerequisites-check)
2. [Clean Existing Installations](#2-clean-existing-installations)
3. [Fetch Latest MoAI-ADK Release](#3-fetch-latest-moai-adk-release)
4. [Install MoAI-ADK](#4-install-moai-adk)
5. [Verification](#5-verification)
6. [Troubleshooting](#6-troubleshooting)
7. [Next Steps](#7-next-steps)
8. [Korean Language Support](#8-korean-language-support-)
9. [Understanding MoAI-ADK](#9-understanding-moai-adk)
10. [Advanced Configuration](#10-advanced-configuration)
11. [Quick Reference Card](#11-quick-reference-card)
12. [Getting Help](#12-getting-help)
13. [Maintenance](#13-maintenance)
14. [Uninstallation](#14-uninstallation)

---

## 1. Prerequisites Check

### Required Software

Run these checks before installing:

```bash
# Check Python version (must be 3.11+)
python3 --version

# Check if git is installed
git --version

# Check if npx is available (for MCP servers)
npx --version
```

**Expected Output**:
- Python: `3.11.x`, `3.12.x`, `3.13.x`, or `3.14.x`
- Git: Any version
- npx: Any version (comes with Node.js)

### Install Missing Requirements

**If Python 3.11+ is missing**:

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

**If Node.js/npx is missing**:

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

## 2. Clean Existing Installations

### 2.0 Pre-Install Check (Recommended)

**Use the automated pre-install checker for comprehensive validation**:

```bash
# Run comprehensive pre-install check with auto-fix
python3 _config/MOAI-ADK/scripts/pre-install-check.py --auto-fix

# Or just check without fixing
python3 _config/MOAI-ADK/scripts/pre-install-check.py
```

**Expected Output**:
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

**What it checks**:
- ✅ Python 3.11+ installed
- ✅ Git and npx available
- ✅ Detects and removes Claude Flow
- ✅ Detects and removes old MoAI installations
- ✅ Validates system is ready

**Benefits**:
- One command to check everything
- Auto-fixes common issues with `--auto-fix`
- Prevents installation conflicts
- Saves 10-15 minutes of manual checks

---

### 2.1 Method 1: Automated Cleanup (Recommended)

**Use specialized cleanup scripts for targeted removal**:

**Remove Claude Flow**:
```bash
# Automated Claude Flow removal
python3 _config/MOAI-ADK/scripts/uninstall-claude-flow.py

# With auto-confirm (skip prompts)
python3 _config/MOAI-ADK/scripts/uninstall-claude-flow.py --yes
```

**Clean dot folders** (`.claude-flow`, `.swarm`, `.moai`, etc.):
```bash
# Interactive cleanup with confirmation
python3 _config/MOAI-ADK/scripts/clean-dot-folders.py

# Auto-confirm all removals
python3 _config/MOAI-ADK/scripts/clean-dot-folders.py --yes

# Dry run (preview what will be removed)
python3 _config/MOAI-ADK/scripts/clean-dot-folders.py --dry-run
```

**Expected Output** (Claude Flow uninstaller):
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

### 2.2 Method 2: Manual Cleanup

If you prefer manual control or automated scripts aren't available:

**Remove Claude Flow (If Present)**:

**IMPORTANT**: MoAI-ADK is incompatible with Claude Flow. Complete removal required.

```bash
# Remove Claude Flow directories
rm -rf .claude-flow
rm -rf .swarm
rm -rf .hive-mind
rm -rf .specstory
rm -rf node_modules/.cache/claude-flow

# Uninstall global npm package
npm uninstall -g claude-flow

# Verify removal
ls -la | grep -E "\.claude-flow|\.swarm|\.hive-mind|\.specstory"
# Should show no results
```

**Clean Existing MoAI-ADK Installation**:

If you have an old MoAI-ADK installation:

```bash
# Remove existing virtual environment
rm -rf .venv

# Remove existing configuration (will be replaced with latest)
rm -rf .moai
rm -rf .claude
rm -f .mcp.json
rm -f CLAUDE.md

# Uninstall Python package (if globally installed)
pip uninstall moai-adk -y
```

**Verify Clean State**:

```bash
# Check for leftover files
ls -la | grep -E "\.moai|\.claude|\.venv|\.mcp\.json"
# Should show no results (except .claude folder if you have other Claude Code configs)

# Check Python packages
pip list | grep moai-adk
# Should show no results
```

---

**Recommendation**: Use Method 1 (automated scripts) for fastest and most reliable cleanup. Use Method 2 (manual) only if scripts aren't available.

---

## 3. Fetch Latest MoAI-ADK Release

### 3.0 Check Latest Version (Automated)

**The pre-install-check.py script already verified latest version is available**. If you skipped Section 2.0, use the automated version checker:

```bash
# Run version checker (if you have the _config directory)
python3 _config/MOAI-ADK/scripts/check-latest-version.py

# Or with Claude Agent SDK mode for AI-enhanced analysis
python3 _config/MOAI-ADK/scripts/check-latest-version.py --agent
```

**Or download directly**:

```bash
# Download version checker script
curl -o check-latest-version.py https://raw.githubusercontent.com/modu-ai/moai-adk/main/_config/check-latest-version.py

# Run version checker
python3 check-latest-version.py

# Or with AI-enhanced mode (requires claude-agent-sdk)
python3 check-latest-version.py --agent
```

**Expected Output**:
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

**The script automatically**:
- ✅ Checks your installed version via `moai-adk --version`
- ✅ Fetches latest release from GitHub API (no cloning needed)
- ✅ Compares versions and recommends action
- ✅ Provides upgrade commands if update available

**Features**:
- **No repository cloning** - Uses GitHub API
- **Fallback methods** - Works even if API is down
- **Smart comparison** - Semantic versioning aware
- **Upgrade instructions** - Shows exact commands to update

**Note**: If you ran `pre-install-check.py --auto-fix` in Section 2.0, this version check was already performed automatically.

### 3.1 Clone MoAI-ADK Repository

```bash
# Create a temporary directory for source code
mkdir -p moai-adk-source
cd moai-adk-source

# Clone the repository
git clone https://github.com/modu-ai/moai-adk.git
cd moai-adk

# Fetch all tags
git fetch --tags

# Get latest release tag
LATEST_TAG=$(git describe --tags `git rev-list --tags --max-count=1`)
echo "Latest release: $LATEST_TAG"

# Checkout latest release
git checkout $LATEST_TAG

# Return to project root
cd ../..
```

**Expected Output**:
```
Latest release: v0.30.2
Previous HEAD position was xxxxxxx...
HEAD is now at xxxxxxx Release v0.30.2
```

### 3.2 Verify Release Version

```bash
# Show current version
cd moai-adk-source/moai-adk
grep "^version" pyproject.toml
cd ../..
```

**Expected Output**:
```
version = "0.30.2"
```

---

## 4. Install MoAI-ADK

### 4.1 Create Python Virtual Environment

```bash
# Create virtual environment at project root
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Verify activation (should show .venv path)
which python
```

**Expected Output**:
```
/path/to/your/project/.venv/bin/python
```

### 4.2 Install MoAI-ADK with Development Dependencies

```bash
# Install in editable/development mode with all dependencies
pip install -e './moai-adk-source/moai-adk[dev]'

# Wait for installation to complete (2-3 minutes)
```

**Expected Output**:
```
Successfully installed moai-adk-0.30.2 click-8.1.x rich-13.x.x ...
```

**Key Dependencies Installed** (v0.30.2):
- `click` - CLI framework
- `rich` - Beautiful terminal output
- `pyfiglet` - ASCII art banners
- `questionary` - Interactive prompts
- `gitpython` - Git operations
- `pytest` - Testing framework
- `google-genai` - Gemini integration
- `pillow` - Image processing
- `aiohttp` - Async HTTP

### 4.3 Copy Configuration Files

```bash
# Copy MoAI configuration
cp -r moai-adk-source/moai-adk/.moai .

# Copy Claude Code commands
mkdir -p .claude/commands
cp -r moai-adk-source/moai-adk/.claude/commands/moai .claude/commands/

# Copy MCP server configuration
cp moai-adk-source/moai-adk/.mcp.json .

# Copy CLAUDE.md (Alfred's execution directive)
cp moai-adk-source/moai-adk/CLAUDE.md .

# Set correct permissions
chmod -R 755 .moai
chmod -R 755 .claude
```

### 4.4 Clean Up Source Files (Optional)

```bash
# Remove source directory to save space
# WARNING: Only do this after successful installation
rm -rf moai-adk-source
```

---

## 5. Verification

### 5.1 Verify Installation

```bash
# Activate virtual environment (if not already active)
source .venv/bin/activate

# Check MoAI-ADK version
moai-adk --version
```

**Expected Output**:
```
MoAI-ADK, version 0.30.2
```

### 5.2 Run System Diagnostics

```bash
# Run comprehensive system check
moai-adk doctor
```

**Expected Output**:
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

### 5.3 Check Project Status

```bash
# View project status
moai-adk status
```

**Expected Output**:
```
╭───── Project Status ──────╮
│   Mode      development   │
│   Locale    ko            │
│   SPECs     0             │
╰───────────────────────────╯
```

### 5.4 Verify Python Module

```bash
# Test Python import
python -c "import moai_adk; print('✅ Version:', moai_adk.__version__)"
```

**Expected Output**:
```
✅ Version: 0.30.2
```

### 5.5 Verify Configuration Structure

```bash
# Check configuration files
ls -la .moai/config/
ls -la .moai/config/presets/
ls -la .claude/commands/moai/
cat .mcp.json
```

**Expected Output**:
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

.mcp.json (MCP servers configured)
```

### 5.6 Verify MCP Servers (Automated)

**Use the automated verification script**:

```bash
# Run comprehensive MCP server verification
python3 _config/MOAI-ADK/scripts/verify-mcp-servers.py
```

**Expected Output**:
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

**MCP Servers Configured**:

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

**Grant ALL permissions** when Claude Code prompts you:
- ✅ `mcp__context7__*` (all permissions)
- ✅ `mcp__sequential-thinking__*` (all permissions)
- ✅ `mcp__playwright__*` (all permissions)

**Note**: Figma server requires manual startup if you need design integration.

---

## 6. Troubleshooting

### Issue: "moai-adk: command not found"

**Solution 1**: Activate virtual environment
```bash
source .venv/bin/activate
moai-adk --version
```

**Solution 2**: Check installation
```bash
pip list | grep moai-adk
# If not found, reinstall
pip install -e './moai-adk-source/moai-adk[dev]'
```

### Issue: "Python version incompatible"

**Solution**: Install Python 3.11+
```bash
# macOS
brew install python@3.13

# Ubuntu/Debian
sudo apt-get install python3.13

# Recreate virtual environment
rm -rf .venv
python3.13 -m venv .venv
source .venv/bin/activate
pip install -e './moai-adk-source/moai-adk[dev]'
```

### Issue: "Permission denied" during installation

**Solution**: Check directory permissions
```bash
# Fix permissions
chmod -R 755 .moai
chmod -R 755 .claude

# Retry installation
pip install -e './moai-adk-source/moai-adk[dev]'
```

### Issue: "Git not found" or "No tags available"

**Solution**: Install git and fetch tags
```bash
# Install git (macOS)
brew install git

# Install git (Ubuntu/Debian)
sudo apt-get install git

# Fetch tags
cd moai-adk-source/moai-adk
git fetch --tags
git describe --tags `git rev-list --tags --max-count=1`
```

### Issue: "Shell parameter expansion error" with [dev]

**Solution**: Quote the package path
```bash
# Wrong
pip install -e ./moai-adk-source/moai-adk[dev]

# Correct
pip install -e './moai-adk-source/moai-adk[dev]'
```

### Issue: MCP servers not connecting

**Solution**: Ensure npx is installed and servers are accessible
```bash
# Test npx
npx --version

# Test MCP server manually
npx -y @upstash/context7-mcp@latest

# Restart Claude Code after fixing
```

### Issue: "Invalid argument" during `moai-adk init`

**Cause**: Interactive prompts don't work in non-TTY environment

**Solution**: Configuration files are already copied, skip `moai-adk init`
```bash
# Verify configuration exists
ls -la .moai/config/config.json
# If exists, you're ready to use MoAI-ADK
```

### Issue: Old configuration conflicts

**Solution**: Remove and reinstall configuration
```bash
# Backup old config (if needed)
cp -r .moai .moai.backup

# Remove old config
rm -rf .moai .claude .mcp.json CLAUDE.md

# Copy fresh config from source
cp -r moai-adk-source/moai-adk/.moai .
cp -r moai-adk-source/moai-adk/.claude/commands/moai .claude/commands/
cp moai-adk-source/moai-adk/.mcp.json .
cp moai-adk-source/moai-adk/CLAUDE.md .
```

---

## 7. Next Steps

### 7.1 Configure Git Strategy

Edit `.moai/config/config.json`:

```json
{
  "git_strategy": {
    "mode": "manual"  // Change to "personal" or "team" as needed
  }
}
```

**Git Strategy Modes**:
- `manual` - Local Git only, manual branch creation (default)
- `personal` - GitHub individual project with automation
- `team` - GitHub team project with full governance

Preset files are auto-loaded from `.moai/config/presets/`

### 7.2 Launch Claude Code

```bash
# Ensure virtual environment is active
source .venv/bin/activate

# Launch Claude Code
claude
```

### 7.3 Start Using MoAI Commands

Within Claude Code, use these commands:

**Project Management**:
```
/moai:0-project          Initialize project structure
```

**SPEC-First TDD Workflow**:
```
/moai:1-plan "feature"   Generate SPEC document
/moai:2-run SPEC-001     Implement with TDD (RED-GREEN-REFACTOR)
/moai:3-sync SPEC-001    Sync documentation and create PR
```

**Feedback Loop**:
```
/moai:9-feedback "improvement: <description>"
```

**Cleanup**:
```
/moai:cleanup            Organize project files
```

### 7.4 Test First Feature

Try this workflow:

1. **Plan**: `/moai:1-plan "Add user authentication"`
2. **Implement**: `/moai:2-run SPEC-001`
3. **Document**: `/moai:3-sync SPEC-001`

After `/moai:1-plan` completes, **execute `/clear`** to reinitialize context (recommended).

### 7.5 Grant MCP Permissions

When Claude Code asks for permissions, **grant ALL**:

- ✅ Allow all `mcp__context7__*` tools
- ✅ Allow all `mcp__sequential-thinking__*` tools
- ✅ Allow all `mcp__playwright__*` tools

These are essential for MoAI-ADK functionality.

### 7.6 Set Your Name (Optional)

Edit `.moai/config/config.json`:

```json
{
  "user": {
    "name": "YourName"  // Alfred will address you by name
  }
}
```

### 7.7 Adjust Language (Optional)

Edit `.moai/config/config.json`:

```json
{
  "language": {
    "conversation_language": "en",  // "ko", "ja", "zh", etc.
    "conversation_language_name": "English"
  }
}
```

---

## 8. Korean Language Support 🇰🇷

MoAI-ADK has **built-in Korean language support**. The system is pre-configured to use Korean as the default conversation language.

### Language Configuration

**Config File**: `.moai/config/config.json`

```json
"language": {
    "conversation_language": "ko",
    "conversation_language_name": "Korean",
    "agent_prompt_language": "ko",
    "notes": "Language for sub-agent internal prompts"
}
```

### Korean Documentation

- **Korean README**: `moai-adk/README.ko.md` (51KB)
- **Full documentation** available in Korean
- **CLI support**: Use `--language ko` flag

### Font Support

No special font configuration needed:
- Korean works through Unicode/UTF-8
- Use Korean-compatible terminal fonts:
  - **macOS**: D2Coding, Nanum Gothic Coding
  - **Windows**: Malgun Gothic, D2Coding
  - **Linux**: Nanum Gothic, Source Code Pro

### Changing Language

To change from Korean to another language:

```bash
# Edit config file
vim .moai/config/config.json

# Change to English
"conversation_language": "en"

# Or use CLI flag
moai-adk --language en [command]
```

### Supported Languages

- **Korean (ko)** - 한국어 (Default)
- **English (en)** - English
- **Japanese (ja)** - 日本語
- **Chinese (zh)** - 中文

---

## 9. Understanding MoAI-ADK

### Key Components

**Mr.Alfred** - SuperAgent orchestrator that:
- Analyzes your requests (8-step process)
- Plans execution with specialized agents
- Delegates tasks to 24+ domain experts
- Manages token optimization (5,000+ token savings/session)

**26 Specialized Agents** (5-Tier Hierarchy):
```
Tier 1: expert-*   (Domain Experts)      - 7 agents
Tier 2: manager-*  (Workflow Managers)   - 8 agents
Tier 3: builder-*  (Meta-creation)       - 3 agents
Tier 4: mcp-*      (MCP Integrations)    - 5 agents
Tier 5: ai-*       (AI Services)         - 1 agent
```

**3 Core Skills**:
- `moai-foundation-core` - Foundation knowledge (8,470 tokens)
- `moai-lang-unified` - Language expertise
- Additional specialized skills

### Workflow Philosophy

**SPEC-First**:
1. Write SPEC before code (EARS format)
2. Auto-generates tests from SPEC
3. Implements with RED-GREEN-REFACTOR
4. Documentation syncs automatically

**TDD Enforcement**:
- 85%+ test coverage required
- Tests written before implementation
- Quality gates prevent low-quality code

**Token Optimization**:
- Simple tasks: 0 tokens (Quick Reference)
- Complex tasks: 8,470 tokens (Auto-load skill)
- Average savings: 5,000 tokens/session

---

## 10. Advanced Configuration

### Enable Automatic Branch Creation

Edit `.moai/config/config.json`:

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

### Change Test Coverage Target

Edit `.moai/config/config.json`:

```json
{
  "constitution": {
    "test_coverage_target": 90  // Default: 90%
  }
}
```

### Enable Auto-Reports

Edit `.moai/config/config.json`:

```json
{
  "report_generation": {
    "auto_create": true  // Default: false (minimal reports)
  }
}
```

### Customize MCP Servers

Edit `.mcp.json` to add/remove servers:

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

## 11. Quick Reference Card

```bash
# Pre-Install & Cleanup
python3 _config/MOAI-ADK/scripts/pre-install-check.py --auto-fix    # Comprehensive pre-install check
python3 _config/MOAI-ADK/scripts/uninstall-claude-flow.py           # Remove Claude Flow
python3 _config/MOAI-ADK/scripts/clean-dot-folders.py               # Clean dot folders

# Installation & Updates
source .venv/bin/activate              # Always activate first
python3 _config/MOAI-ADK/scripts/check-latest-version.py            # Smart version check & update guide
python3 _config/MOAI-ADK/scripts/verify-mcp-servers.py              # Verify MCP server configuration
moai-adk --version                     # Check version
moai-adk doctor                        # Run diagnostics

# Commands (in Claude Code)
/moai:0-project                        # Initialize project
/moai:1-plan "description"             # Generate SPEC
/moai:2-run SPEC-001                   # Implement TDD
/moai:3-sync SPEC-001                  # Sync docs
/moai:9-feedback "type: description"   # Submit feedback
/clear                                 # Reset context (after /moai:1-plan)

# Configuration
.moai/config/config.json               # Main config
.moai/config/presets/                  # Git workflow presets
.claude/commands/moai/                 # MoAI commands
.mcp.json                              # MCP servers
CLAUDE.md                              # Alfred's directive

# Verification
ls -la .moai .claude .mcp.json         # Check files exist
pip list | grep moai-adk               # Check package
moai-adk status                        # Project status
```

---

## 12. Getting Help

**Documentation**:
- GitHub: https://github.com/modu-ai/moai-adk
- README: https://github.com/modu-ai/moai-adk/blob/main/README.md
- Releases: https://github.com/modu-ai/moai-adk/releases

**Support**:
- Issues: https://github.com/modu-ai/moai-adk/issues
- Feedback: Use `/moai:9-feedback` within Claude Code

**Within Claude Code**:
- Alfred automatically helps based on CLAUDE.md
- Grant all MCP permissions for full functionality
- Use `/moai:9-feedback "question: <your question>"` for help

---

## 13. Maintenance

### Check for Updates (Automated)

**Use the smart version checker**:

```bash
# Activate virtual environment first
source .venv/bin/activate

# Run version checker
python3 _config/MOAI-ADK/scripts/check-latest-version.py
```

**Example Output (Update Available)**:
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

# 1. Fetch latest release
cd moai-adk-source/moai-adk
git fetch --tags
git checkout v0.30.2
cd ../..

# 2. Reinstall
source .venv/bin/activate
pip install -e './moai-adk-source/moai-adk[dev]' --upgrade

# 3. Update configuration
cp -r moai-adk-source/moai-adk/.moai .
cp -r moai-adk-source/moai-adk/.claude/commands/moai .claude/commands/
cp moai-adk-source/moai-adk/.mcp.json .
cp moai-adk-source/moai-adk/CLAUDE.md .

# 4. Verify
moai-adk --version
moai-adk doctor
```

**Example Output (Up to Date)**:
```
✅ You have the latest version installed!
```

### Manual Update to Latest Version

If you prefer manual control:

```bash
# Activate virtual environment
source .venv/bin/activate

# Pull latest changes
cd moai-adk-source/moai-adk
git fetch --tags
LATEST_TAG=$(git describe --tags `git rev-list --tags --max-count=1`)
git checkout $LATEST_TAG

# Reinstall
cd ../..
pip install -e './moai-adk-source/moai-adk[dev]' --upgrade

# Update configuration files
cp -r moai-adk-source/moai-adk/.moai .
cp -r moai-adk-source/moai-adk/.claude/commands/moai .claude/commands/
cp moai-adk-source/moai-adk/.mcp.json .
cp moai-adk-source/moai-adk/CLAUDE.md .

# Verify
moai-adk --version
moai-adk doctor
```

### Backup Configuration

```bash
# Backup before updates
cp -r .moai .moai.backup.$(date +%Y%m%d)
cp -r .claude .claude.backup.$(date +%Y%m%d)
cp .mcp.json .mcp.json.backup.$(date +%Y%m%d)
```

---

## 14. Uninstallation

To completely remove MoAI-ADK:

```bash
# Remove virtual environment
rm -rf .venv

# Remove configuration
rm -rf .moai
rm -rf .claude/commands/moai
rm -f .mcp.json
rm -f CLAUDE.md

# Remove source (if kept)
rm -rf moai-adk-source

# Uninstall package (if globally installed)
pip uninstall moai-adk -y
```

---

**Installation Guide Version**: 1.0.0
**Last Updated**: 2025-11-28
**MoAI-ADK Version**: 0.30.2
**Tested On**: macOS, Ubuntu 22.04, WSL2

**Drag & Drop Ready**: This file can be copied to any project folder and followed step-by-step.
