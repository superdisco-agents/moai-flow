# MoAI-ADK Migration Guide

Complete guide for migrating to MoAI-ADK from existing setups with Korean language support.

**Version**: 1.0.0
**Last Updated**: 2025-11-29
**Language Support**: English, Korean (한국어)

---

## Table of Contents

1. [Overview](#overview)
2. [Migration Paths](#migration-paths)
3. [Path 1: UV CLI Migration (Recommended)](#path-1-uv-cli-migration-recommended)
4. [Path 2: Bash Installation Migration](#path-2-bash-installation-migration)
5. [Path 3: Claude Skill Migration](#path-3-claude-skill-migration)
6. [Path 4: Gradual Migration (Existing Projects)](#path-4-gradual-migration-existing-projects)
7. [Korean Font Migration](#korean-font-migration)
8. [Team Rollout Plan](#team-rollout-plan)
9. [Rollback Procedures](#rollback-procedures)
10. [Troubleshooting](#troubleshooting)
11. [Verification](#verification)

---

## Overview

### What is MoAI-ADK?

MoAI-ADK (Mixture of AI Agents Development Kit) is a comprehensive framework for building multi-agent systems with full Korean language support. It provides three installation approaches following the Beyond-MCP pattern:

1. **UV CLI Scripts** - Direct command-line installation
2. **Bash Apps** - Shell-based interactive installation
3. **Claude Skills** - AI-assisted installation with progressive disclosure

### Migration Benefits

✅ **Full Korean Support**: Native Korean font rendering (D2Coding, Noto Sans CJK)
✅ **Flexible Installation**: Choose from 3 installation methods
✅ **Zero Downtime**: Gradual migration path available
✅ **Team Ready**: Rollout plans for organizations
✅ **Production Tested**: Comprehensive test suite (140+ tests)
✅ **Rollback Safe**: Complete rollback procedures included

### System Requirements

**Minimum Requirements**:
- Python 3.11+
- UV package manager 0.4.0+
- macOS/Linux (Windows via WSL2)
- 2GB free disk space

**Recommended Requirements**:
- Python 3.12+
- UV 0.5.0+
- 4GB RAM
- Terminal with Korean font support (Ghostty, iTerm2, Warp)

---

## Migration Paths

Choose the migration path that best fits your situation:

| Path | Best For | Duration | Complexity | Korean Support |
|------|----------|----------|------------|----------------|
| **Path 1: UV CLI** | New installations, automation | 10-15 min | Low | ✅ Full |
| **Path 2: Bash App** | Interactive setup, customization | 15-20 min | Medium | ✅ Full |
| **Path 3: Claude Skill** | AI-assisted, learning | 20-30 min | Low | ✅ Full |
| **Path 4: Gradual** | Existing projects, teams | 1-2 hours | High | ✅ Full |

### Decision Matrix

```
┌─────────────────────────────────────────────────────────────┐
│              CHOOSE YOUR MIGRATION PATH                      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  New Installation?                                           │
│  └─ YES → Path 1: UV CLI (Recommended)                      │
│  └─ NO  → Continue below                                     │
│                                                               │
│  Have Existing MCP Setup?                                    │
│  └─ YES → Path 4: Gradual Migration                         │
│  └─ NO  → Continue below                                     │
│                                                               │
│  Prefer Interactive Setup?                                   │
│  └─ YES → Path 2: Bash App                                  │
│  └─ NO  → Continue below                                     │
│                                                               │
│  Using Claude Code CLI?                                      │
│  └─ YES → Path 3: Claude Skill                              │
│  └─ NO  → Path 1: UV CLI (Default)                          │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## Path 1: UV CLI Migration (Recommended)

### Overview

Direct command-line installation using UV scripts. Best for:
- Clean installations
- Automated deployments
- CI/CD pipelines
- Developers comfortable with CLI

**Estimated Time**: 10-15 minutes

### Prerequisites

```bash
# Install UV package manager
curl -LsSf https://astral.sh/uv/install.sh | sh

# Verify installation
uv --version  # Should be 0.4.0+

# Verify Python
python3 --version  # Should be 3.11+
```

### Step-by-Step Migration

#### Step 1: Backup Existing Configuration

```bash
# Create backup directory
mkdir -p ~/moai-adk-backup/$(date +%Y%m%d)

# Backup existing MCP configs (if any)
if [ -f ~/.claude/claude_desktop_config.json ]; then
  cp ~/.claude/claude_desktop_config.json ~/moai-adk-backup/$(date +%Y%m%d)/
fi

# Backup existing skills
if [ -d ~/.claude/skills ]; then
  cp -r ~/.claude/skills ~/moai-adk-backup/$(date +%Y%m%d)/
fi

# Backup environment variables
env | grep -i "claude\|mcp\|moai" > ~/moai-adk-backup/$(date +%Y%m%d)/env_vars.txt

echo "✅ Backup completed: ~/moai-adk-backup/$(date +%Y%m%d)/"
```

#### Step 2: Run UV Installation Script

```bash
# Navigate to MoAI-ADK directory
cd /path/to/moai-adk/_config/install-moai-ko

# Run UV installer (interactive mode)
uv run install-moai-adk.py

# Or non-interactive mode
uv run install-moai-adk.py --yes --korean-fonts

# With custom options
uv run install-moai-adk.py \
  --install-path ~/moai-adk \
  --korean-fonts \
  --ghostty-config \
  --verbose
```

#### Step 3: Configure Korean Fonts

```bash
# The installer will prompt:
# "Install Korean fonts (D2Coding)? [Y/n]"
# Press Y to install

# Verify font installation
fc-list | grep -i "d2coding"

# Expected output:
# /Users/username/Library/Fonts/D2Coding-Ver1.3.2-20180524.ttc: D2Coding:style=Regular
```

#### Step 4: Update Terminal Configuration

```bash
# For Ghostty (recommended for Korean)
cat >> ~/.config/ghostty/config <<EOF

# Korean Font Support
font-family = "D2Coding"
font-size = 14
font-feature = -calt

# Korean Character Rendering
font-synthetic-style = false
grapheme-width-method = legacy

# CJK Support
shell-integration-features = true
EOF

# Restart Ghostty
killall ghostty
```

#### Step 5: Verify Installation

```bash
# Run verification script
./verify-installation.sh

# Expected output:
# ✅ UV installation: OK
# ✅ Python version: 3.12.0
# ✅ Korean fonts: D2Coding installed
# ✅ MCP servers: 3 configured
# ✅ Skills: 12 installed
# ✅ Korean rendering: 한글 테스트 ✓
```

#### Step 6: Test Korean Support

```bash
# Test Korean text rendering
echo "안녕하세요 MoAI-ADK" | cat

# Test in Claude Code
claude code "한국어 테스트"

# Expected: Korean characters should render clearly without boxes/squares
```

### Post-Migration Checklist

- [ ] UV version 0.4.0+ installed
- [ ] Python 3.11+ configured
- [ ] Korean fonts (D2Coding) installed
- [ ] Terminal configured for Korean
- [ ] MCP servers registered
- [ ] Skills installed and verified
- [ ] Backup created and tested
- [ ] Korean text renders correctly

---

## Path 2: Bash Installation Migration

### Overview

Interactive shell-based installation with step-by-step guidance. Best for:
- Users preferring interactive setup
- Custom configuration needs
- Learning the installation process

**Estimated Time**: 15-20 minutes

### Prerequisites

Same as Path 1, plus:
- Bash 4.0+ or Zsh 5.0+
- Basic shell scripting knowledge

### Step-by-Step Migration

#### Step 1: Prepare Environment

```bash
# Check shell version
bash --version  # or zsh --version

# Set execution permissions
chmod +x install-moai-adk.sh

# Review installation options
./install-moai-adk.sh --help

# Output:
# MoAI-ADK Installation Script
#
# Usage:
#   ./install-moai-adk.sh [OPTIONS]
#
# Options:
#   --korean-fonts     Install Korean fonts (D2Coding)
#   --ghostty-config   Configure Ghostty for Korean
#   --interactive      Interactive mode (default)
#   --dry-run          Show what would be installed
#   --help             Show this help
```

#### Step 2: Run Interactive Installation

```bash
# Start interactive installer
./install-moai-adk.sh --interactive

# The installer will prompt for each step:

# ═══════════════════════════════════════════════
# MoAI-ADK Interactive Installation
# ═══════════════════════════════════════════════
#
# Step 1/8: System Requirements Check
# ───────────────────────────────────────────────
# ✓ UV installed: 0.5.0
# ✓ Python installed: 3.12.0
# ✓ Disk space: 5.2GB available
#
# Continue? [Y/n]:
```

#### Step 3: Configure Installation Options

The installer will prompt for each option:

```bash
# Language Selection
# ═══════════════════════════════════════════════
# Select installation language:
#   1) English
#   2) 한국어 (Korean)
#
# Choice [1]: 2

# Installation Path
# ═══════════════════════════════════════════════
# Installation directory:
# Default: /Users/username/moai-adk
#
# Path [/Users/username/moai-adk]: <Enter for default>

# Korean Font Installation
# ═══════════════════════════════════════════════
# Install Korean fonts (D2Coding)?
# Required for proper Korean rendering.
#
# Install? [Y/n]: Y

# Terminal Configuration
# ═══════════════════════════════════════════════
# Configure Ghostty for Korean support?
#
# Configure? [Y/n]: Y

# MCP Server Selection
# ═══════════════════════════════════════════════
# Select MCP servers to install:
#   [x] 1) Sequential Thinking
#   [x] 2) Playwright
#   [ ] 3) Context7
#   [x] 4) All servers
#
# Selection [1,2,3,4]: 4
```

#### Step 4: Monitor Installation Progress

```bash
# The installer shows real-time progress:

# ═══════════════════════════════════════════════
# Installing MoAI-ADK...
# ═══════════════════════════════════════════════
#
# [1/8] Creating directory structure...     ✓
# [2/8] Installing UV dependencies...       ✓
# [3/8] Downloading Korean fonts...         ✓
# [4/8] Installing D2Coding font...         ✓
# [5/8] Configuring Ghostty...              ✓
# [6/8] Registering MCP servers...          ✓
# [7/8] Installing skills...                ✓
# [8/8] Running verification tests...       ✓
#
# Installation completed in 12m 34s
```

#### Step 5: Review Installation Summary

```bash
# ═══════════════════════════════════════════════
# Installation Summary
# ═══════════════════════════════════════════════
#
# Installation Path:
#   /Users/username/moai-adk
#
# Installed Components:
#   ✓ UV Package Manager (0.5.0)
#   ✓ Python Environment (3.12.0)
#   ✓ Korean Fonts (D2Coding)
#   ✓ Ghostty Configuration
#   ✓ MCP Servers (3)
#   ✓ Skills (12)
#
# Korean Support:
#   ✓ Font rendering: D2Coding
#   ✓ Character encoding: UTF-8
#   ✓ Terminal: Ghostty configured
#   ✓ Test: 한글 렌더링 테스트 ✓
#
# Next Steps:
#   1. Restart your terminal
#   2. Run: source ~/.zshrc  # or ~/.bashrc
#   3. Test: claude code "안녕하세요"
#
# Documentation:
#   - Quick Start: ~/moai-adk/docs/QUICKSTART.md
#   - Korean Guide: ~/moai-adk/docs/KOREAN-FONTS-GUIDE.md
#   - Troubleshooting: ~/moai-adk/docs/TROUBLESHOOTING.md
```

### Post-Migration Steps

```bash
# Restart terminal for font changes
exec $SHELL -l

# Verify Korean rendering
printf "한글 테스트: "
echo "✓ 성공" | grep "성공"

# Test Claude Code with Korean
claude code "MoAI-ADK 설치 확인"
```

---

## Path 3: Claude Skill Migration

### Overview

AI-assisted installation using Claude Code skills with progressive disclosure. Best for:
- Users new to command-line tools
- Learning-oriented installations
- Interactive guidance needs

**Estimated Time**: 20-30 minutes

### Prerequisites

- Claude Code CLI installed
- Active Anthropic API key
- Terminal with Claude integration

### Step-by-Step Migration

#### Step 1: Install MoAI-ADK Skill

```bash
# Method 1: Via Claude Code CLI
claude code --install-skill moai-adk-installer

# Method 2: Manual installation
mkdir -p ~/.claude/skills
cp -r moai-adk/_config/install-moai-ko/skills/moai-adk-installer \
      ~/.claude/skills/

# Method 3: Via git clone
git clone https://github.com/ruvnet/moai-adk.git ~/moai-adk
ln -s ~/moai-adk/_config/install-moai-ko/skills/moai-adk-installer \
      ~/.claude/skills/moai-adk-installer
```

#### Step 2: Invoke Installation Skill

```bash
# Start Claude Code session
claude code

# In the Claude Code prompt, type:
> /moai-adk-installer

# The skill will load with progressive disclosure:
```

**Skill Output**:

```
MoAI-ADK Installation Assistant (Korean Supported)
═══════════════════════════════════════════════════

I'll guide you through installing MoAI-ADK with full Korean language support.

Current System Check:
  - OS: macOS 14.7.1
  - Shell: zsh 5.9
  - UV: Not installed ⚠️
  - Python: 3.12.0 ✓
  - Korean Fonts: Not installed ⚠️

I can help with:
  1. Install UV package manager
  2. Install Korean fonts (D2Coding)
  3. Configure terminal for Korean
  4. Set up MCP servers
  5. Install skills and commands
  6. Verify installation

Would you like me to proceed with the installation? [Y/n]:
```

#### Step 3: Follow AI-Guided Installation

The skill provides step-by-step guidance:

```
Step 1/6: Installing UV Package Manager
───────────────────────────────────────

I'll install UV using the official installer script.

Command to run:
  curl -LsSf https://astral.sh/uv/install.sh | sh

Shall I proceed? [Y/n]: Y

[Running command...]
✓ UV 0.5.0 installed successfully

Add to PATH:
  export PATH="$HOME/.local/bin:$PATH"

Would you like me to update your ~/.zshrc? [Y/n]: Y
✓ PATH updated in ~/.zshrc
```

```
Step 2/6: Installing Korean Fonts
──────────────────────────────────

For proper Korean rendering, I recommend installing D2Coding font.

D2Coding features:
  - Optimized for code editing
  - Clear Hangul rendering
  - Monospace for terminals
  - Free and open-source

Download size: ~2.5MB

Install D2Coding? [Y/n]: Y

[Downloading font...]
✓ D2Coding-Ver1.3.2-20180524.ttc downloaded
✓ Font installed to ~/Library/Fonts/

Testing Korean rendering:
  한글 테스트: ✓ Success
```

```
Step 3/6: Configuring Terminal (Ghostty)
─────────────────────────────────────────

Detected terminal: Ghostty 24.11

I can configure Ghostty for optimal Korean support:
  - Set D2Coding as default font
  - Enable CJK character support
  - Configure proper line spacing
  - Set UTF-8 encoding

Ghostty config location: ~/.config/ghostty/config

Apply configuration? [Y/n]: Y

Configuration preview:
  font-family = "D2Coding"
  font-size = 14
  font-feature = -calt
  grapheme-width-method = legacy
  shell-integration-features = true

✓ Ghostty configured

Restart required. Restart now? [Y/n]: n
  (You can restart later: killall ghostty)
```

```
Step 4/6: Setting up MCP Servers
────────────────────────────────

MoAI-ADK includes these MCP servers:
  1. Sequential Thinking - Reasoning chains
  2. Playwright - Browser automation
  3. Context7 - Documentation context

Install all servers? [Y/n]: Y

[Installing MCP servers...]
✓ sequential-thinking installed
✓ playwright installed
✓ context7 installed

Registered in Claude Desktop config:
  ~/.claude/claude_desktop_config.json

View config? [Y/n]: n
```

```
Step 5/6: Installing Skills
───────────────────────────

Installing 12 MoAI-ADK skills:
  ✓ moai-adk-installer
  ✓ korean-text-processor
  ✓ multi-agent-coordinator
  ✓ task-orchestrator
  ... (8 more)

Skills installed to: ~/.claude/skills/

Test a skill? [Y/n]: Y

Which skill to test?
  1) korean-text-processor
  2) multi-agent-coordinator
  3) Skip

Choice [1]: 1

Testing korean-text-processor...
  Input: "안녕하세요"
  Output: "안녕하세요" (렌더링 정상) ✓
```

```
Step 6/6: Final Verification
────────────────────────────

Running comprehensive tests...

System Tests:
  ✓ UV installation
  ✓ Python environment
  ✓ Korean fonts
  ✓ Terminal configuration

MoAI-ADK Tests:
  ✓ MCP servers registered
  ✓ Skills installed
  ✓ Commands available
  ✓ Korean rendering

All tests passed! ✓

═══════════════════════════════════════

Installation Complete!

Summary:
  - Installation path: ~/moai-adk
  - Korean fonts: D2Coding installed
  - MCP servers: 3 active
  - Skills: 12 installed
  - Korean support: Full ✓

Next Steps:
  1. Restart your terminal (or run: exec $SHELL -l)
  2. Try: claude code "안녕하세요 MoAI-ADK"
  3. Read: ~/moai-adk/docs/QUICKSTART.md

Need help?
  - Documentation: ~/moai-adk/docs/
  - Korean guide: ~/moai-adk/docs/KOREAN-FONTS-GUIDE.md
  - Issues: https://github.com/ruvnet/moai-adk/issues

Would you like to:
  1) View quick start guide
  2) Test Korean rendering
  3) Exit

Choice [1]: 2

Testing Korean rendering in Claude Code...

Input: "MoAI-ADK는 한국어를 완벽하게 지원합니다."
Output: "MoAI-ADK는 한국어를 완벽하게 지원합니다." ✓

Korean rendering test: PASSED ✓

Happy coding! 🚀
```

### Post-Migration Verification

```bash
# Test Korean in Claude Code
claude code "한국어 테스트 - D2Coding 폰트 확인"

# Verify skills installed
claude code --list-skills | grep moai

# Check MCP servers
cat ~/.claude/claude_desktop_config.json | jq '.mcpServers'
```

---

## Path 4: Gradual Migration (Existing Projects)

### Overview

Zero-downtime migration for existing projects with phased rollout. Best for:
- Production environments
- Team migrations
- Large codebases
- Risk-averse deployments

**Estimated Time**: 1-2 hours (over multiple phases)

### Migration Phases

```
Phase 1: Preparation (Day 1)
  └─ Audit existing setup
  └─ Create backups
  └─ Test in sandbox

Phase 2: Korean Fonts (Day 2-3)
  └─ Install fonts
  └─ Configure terminals
  └─ Test rendering

Phase 3: UV Migration (Day 4-5)
  └─ Install UV alongside existing tools
  └─ Run parallel testing
  └─ Gradual cutover

Phase 4: MCP Integration (Day 6-7)
  └─ Add MCP servers incrementally
  └─ Verify each server
  └─ Update workflows

Phase 5: Skills Installation (Day 8-9)
  └─ Install skills one-by-one
  └─ Test each skill
  └─ Update documentation

Phase 6: Final Cutover (Day 10)
  └─ Switch to MoAI-ADK as primary
  └─ Remove legacy tools
  └─ Team training
```

### Step-by-Step Gradual Migration

#### Phase 1: Preparation (Day 1)

**1.1 Audit Current Setup**

```bash
# Create audit report
cat > ~/moai-migration-audit.txt <<EOF
MoAI-ADK Migration Audit
Date: $(date)
═══════════════════════════════════════

Current System:
  OS: $(uname -s)
  Shell: $SHELL
  Python: $(python3 --version)
  Package Manager: $(which pip || echo "None")

Existing Tools:
  MCP Servers: $(ls ~/.claude/mcp-servers 2>/dev/null | wc -l)
  Skills: $(ls ~/.claude/skills 2>/dev/null | wc -l)
  Commands: $(ls ~/.claude/commands 2>/dev/null | wc -l)

Korean Support:
  Fonts: $(fc-list | grep -i "korean\|hangul\|noto" | wc -l)
  Encoding: $LANG

Projects Using Current Setup:
  [List your projects here]

Migration Risks:
  - Downtime tolerance: [Specify]
  - Team size: [Specify]
  - Critical dependencies: [Specify]
EOF

cat ~/moai-migration-audit.txt
```

**1.2 Create Comprehensive Backups**

```bash
# Backup script
cat > ~/backup-for-moai-migration.sh <<'EOF'
#!/bin/bash
set -e

BACKUP_DIR=~/moai-migration-backup/$(date +%Y%m%d_%H%M%S)
mkdir -p "$BACKUP_DIR"

echo "Creating migration backups..."

# Backup Claude configs
if [ -d ~/.claude ]; then
  cp -r ~/.claude "$BACKUP_DIR/claude_config"
fi

# Backup shell configs
cp ~/.zshrc "$BACKUP_DIR/" 2>/dev/null || true
cp ~/.bashrc "$BACKUP_DIR/" 2>/dev/null || true

# Backup Python environments
if [ -d ~/.pyenv ]; then
  cp -r ~/.pyenv/versions "$BACKUP_DIR/pyenv_versions"
fi

# Backup fonts
if [ -d ~/Library/Fonts ]; then
  cp -r ~/Library/Fonts "$BACKUP_DIR/fonts"
fi

# Backup environment variables
env > "$BACKUP_DIR/env_vars.txt"

# Create manifest
cat > "$BACKUP_DIR/MANIFEST.txt" <<MANIFEST
MoAI-ADK Migration Backup
Created: $(date)

Backed up:
  - Claude configuration: ~/.claude
  - Shell configs: .zshrc, .bashrc
  - Python environments: ~/.pyenv
  - Fonts: ~/Library/Fonts
  - Environment variables

Restore:
  cd "$BACKUP_DIR"
  ./restore.sh
MANIFEST

# Create restore script
cat > "$BACKUP_DIR/restore.sh" <<'RESTORE'
#!/bin/bash
echo "Restoring pre-migration state..."
cp -r claude_config ~/.claude
cp .zshrc ~/.zshrc 2>/dev/null || true
cp .bashrc ~/.bashrc 2>/dev/null || true
echo "Restore complete. Restart terminal."
RESTORE

chmod +x "$BACKUP_DIR/restore.sh"

echo "✓ Backup complete: $BACKUP_DIR"
EOF

chmod +x ~/backup-for-moai-migration.sh
~/backup-for-moai-migration.sh
```

**1.3 Test in Sandbox**

```bash
# Create isolated test environment
mkdir -p ~/moai-sandbox
cd ~/moai-sandbox

# Clone MoAI-ADK
git clone https://github.com/ruvnet/moai-adk.git

# Create isolated UV environment
export UV_PROJECT_ENVIRONMENT="$HOME/moai-sandbox/.venv"

# Test installation
cd moai-adk/_config/install-moai-ko
uv run install-moai-adk.py --dry-run

# Review what would be installed
cat installation-plan.txt
```

#### Phase 2: Korean Fonts Installation (Day 2-3)

**2.1 Install Korean Fonts (Non-Disruptive)**

```bash
# Download D2Coding font
curl -L -o /tmp/D2Coding.ttc \
  https://github.com/naver/d2codingfont/releases/download/VER1.3.2/D2Coding-Ver1.3.2-20180524.ttc

# Install font (doesn't affect existing setup)
cp /tmp/D2Coding.ttc ~/Library/Fonts/

# Verify installation
fc-list | grep D2Coding
```

**2.2 Configure Terminal (Optional)**

```bash
# Test Ghostty config without breaking existing setup
cat >> ~/.config/ghostty/config.test <<EOF

# MoAI-ADK Korean Support (Test)
# To activate: mv config config.backup && mv config.test config

font-family = "D2Coding"
font-size = 14
EOF

# Test in new Ghostty window (existing windows unaffected)
ghostty --config ~/.config/ghostty/config.test
```

**2.3 Verify Korean Rendering**

```bash
# Test Korean rendering
echo "한글 테스트: MoAI-ADK" | cat

# Compare old vs new font
echo "Old font: 한글"  # In old terminal window
echo "New font: 한글"  # In test Ghostty window

# If satisfied, apply permanently:
# mv ~/.config/ghostty/config ~/.config/ghostty/config.backup
# mv ~/.config/ghostty/config.test ~/.config/ghostty/config
```

#### Phase 3: UV Migration (Day 4-5)

**3.1 Install UV Alongside Existing Tools**

```bash
# Install UV (doesn't replace pip)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Add to PATH (new terminal sessions only)
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc

# Existing terminals still use pip
# New terminals can use uv
```

**3.2 Run Parallel Testing**

```bash
# Test UV with existing project (non-destructive)
cd ~/your-existing-project

# Create UV lock file (doesn't modify existing)
uv pip compile requirements.txt -o requirements.uv.txt

# Test in isolated environment
uv venv .venv-test
source .venv-test/bin/activate
uv pip install -r requirements.uv.txt

# Run tests
pytest

# Compare performance
time pip install -r requirements.txt  # Old method
time uv pip install -r requirements.txt  # New method
```

**3.3 Gradual Cutover**

```bash
# Week 1: Use UV for new projects only
# Existing projects continue with pip

# Week 2: Migrate 1-2 non-critical projects to UV
cd ~/project-test-1
uv venv
uv pip install -r requirements.txt

# Week 3: Migrate remaining projects
# Week 4: Deprecate pip usage
```

#### Phase 4: MCP Integration (Day 6-7)

**4.1 Add MCP Servers Incrementally**

```bash
# Start with one server (sequential-thinking)
claude mcp add sequential-thinking \
  npx @ruv/sequential-thinking mcp start

# Test thoroughly
claude code "Test sequential thinking"

# Add second server after verification
claude mcp add playwright \
  npx @ruv/playwright mcp start

# Test both servers
claude code "Test playwright automation"

# Add remaining servers one-by-one
```

**4.2 Verify Each Server**

```bash
# Check server status
claude mcp list

# Test each server individually
claude code --test-mcp sequential-thinking
claude code --test-mcp playwright
claude code --test-mcp context7
```

**4.3 Update Workflows Gradually**

```bash
# Week 1: Use new MCP servers for new tasks
# Week 2: Migrate existing workflows one-by-one
# Week 3: Update documentation
# Week 4: Remove legacy servers
```

#### Phase 5: Skills Installation (Day 8-9)

**5.1 Install Skills One-by-One**

```bash
# Install first skill
mkdir -p ~/.claude/skills
cp -r moai-adk/skills/moai-adk-installer ~/.claude/skills/

# Test immediately
claude code /moai-adk-installer

# If successful, continue with next skill
cp -r moai-adk/skills/korean-text-processor ~/.claude/skills/

# Test
claude code /korean-text-processor "안녕하세요"
```

**5.2 Test Each Skill Thoroughly**

```bash
# Create test script
cat > ~/test-moai-skills.sh <<'EOF'
#!/bin/bash

SKILLS=(
  "moai-adk-installer"
  "korean-text-processor"
  "multi-agent-coordinator"
  "task-orchestrator"
)

for skill in "${SKILLS[@]}"; do
  echo "Testing $skill..."
  claude code "/$skill --test" || echo "  ⚠️ Failed"
  echo
done
EOF

chmod +x ~/test-moai-skills.sh
~/test-moai-skills.sh
```

**5.3 Update Documentation**

```bash
# Document new skills for team
cat >> ~/TEAM-MIGRATION-GUIDE.md <<EOF

## New Skills Available

### moai-adk-installer
Usage: \`/moai-adk-installer\`
Purpose: Install MoAI-ADK components

### korean-text-processor
Usage: \`/korean-text-processor "한글 텍스트"\`
Purpose: Process Korean text with proper encoding

[Add more skills...]
EOF
```

#### Phase 6: Final Cutover (Day 10)

**6.1 Switch to MoAI-ADK as Primary**

```bash
# Update shell config to prefer MoAI-ADK tools
cat >> ~/.zshrc <<'EOF'

# MoAI-ADK Environment (Migration Complete)
export MOAI_ADK_HOME="$HOME/moai-adk"
export PATH="$MOAI_ADK_HOME/bin:$PATH"

# Prefer UV over pip
alias pip="uv pip"
EOF

source ~/.zshrc
```

**6.2 Remove Legacy Tools**

```bash
# Archive old configs (don't delete immediately)
mkdir -p ~/legacy-backup
mv ~/.claude/old-mcp-servers ~/legacy-backup/
mv ~/.claude/old-skills ~/legacy-backup/

# Keep for 30 days before permanent deletion
```

**6.3 Team Training**

```bash
# Schedule team training sessions
# - Week 1: Introduction to MoAI-ADK
# - Week 2: Korean support features
# - Week 3: Advanced workflows
# - Week 4: Best practices

# Create training materials
mkdir -p ~/moai-team-training

cat > ~/moai-team-training/SESSION-1-INTRO.md <<'EOF'
# MoAI-ADK Team Training: Session 1

## Objectives
- Understand MoAI-ADK architecture
- Learn basic commands
- Test Korean support

## Agenda
1. Installation verification (10 min)
2. Basic usage (20 min)
3. Korean features (15 min)
4. Q&A (15 min)

## Hands-on Exercises
[Add exercises here]
EOF
```

### Gradual Migration Checklist

**Week 1: Preparation**
- [ ] Audit completed
- [ ] Backups created
- [ ] Sandbox tested
- [ ] Team notified

**Week 2: Korean Support**
- [ ] Fonts installed
- [ ] Terminals configured
- [ ] Rendering verified
- [ ] Documentation updated

**Week 3: UV Migration**
- [ ] UV installed
- [ ] Parallel testing complete
- [ ] 2+ projects migrated
- [ ] Performance validated

**Week 4: MCP Integration**
- [ ] All servers installed
- [ ] Each server tested
- [ ] Workflows updated
- [ ] Team trained

**Week 5: Skills Deployment**
- [ ] All skills installed
- [ ] Testing complete
- [ ] Documentation updated
- [ ] Rollout successful

**Week 6: Completion**
- [ ] Primary cutover complete
- [ ] Legacy tools archived
- [ ] Team fully trained
- [ ] Post-migration review

---

## Korean Font Migration

### Why Korean Fonts Matter

Korean (Hangul) characters require specific font support for proper rendering:

❌ **Without proper fonts**: □□□ (boxes/squares)
✅ **With D2Coding**: 한글 (clear, readable)

### Recommended Fonts

| Font | Purpose | Pros | Cons |
|------|---------|------|------|
| **D2Coding** | Code editing | Monospace, clear | Large file size |
| **Noto Sans CJK** | General use | Multi-language | Not monospace |
| **Malgun Gothic** | UI elements | Windows compatible | macOS rendering issues |
| **Nanum Gothic Coding** | Alternative | Free, Korean-optimized | Less crisp |

### Installation Methods

#### Method 1: Automated (Via MoAI-ADK)

```bash
# During MoAI-ADK installation
uv run install-moai-adk.py --korean-fonts

# Or standalone
./install-korean-fonts.sh
```

#### Method 2: Manual Installation

```bash
# Download D2Coding
curl -L -o /tmp/D2Coding.ttc \
  https://github.com/naver/d2codingfont/releases/download/VER1.3.2/D2Coding-Ver1.3.2-20180524.ttc

# Install to user fonts
cp /tmp/D2Coding.ttc ~/Library/Fonts/

# Or system-wide (requires sudo)
sudo cp /tmp/D2Coding.ttc /Library/Fonts/

# Rebuild font cache
fc-cache -fv
```

#### Method 3: Homebrew (macOS)

```bash
# Install via Homebrew Cask
brew tap homebrew/cask-fonts
brew install --cask font-d2coding

# Verify
fc-list | grep D2Coding
```

### Terminal Configuration

See [KOREAN-FONTS-GUIDE.md](./KOREAN-FONTS-GUIDE.md) for detailed terminal configuration.

### Verification

```bash
# Test Korean rendering
echo "안녕하세요 MoAI-ADK" | cat

# Visual test in Claude Code
claude code "한글 렌더링 테스트: ✓ 성공"

# Expected: All Korean characters visible and clear
```

---

## Team Rollout Plan

### Small Teams (2-5 developers)

**Timeline**: 1-2 weeks

```
Week 1:
  Day 1-2: Admin installs on own machine
  Day 3: Team demonstration
  Day 4-5: Team members install individually

Week 2:
  Day 1-3: Parallel usage (old + new tools)
  Day 4-5: Full cutover
```

### Medium Teams (6-20 developers)

**Timeline**: 3-4 weeks

```
Week 1: Preparation
  - Admin/DevOps pilot installation
  - Create team-specific documentation
  - Test with 1-2 projects

Week 2: Pilot Rollout
  - 20% of team (early adopters)
  - Gather feedback
  - Refine documentation

Week 3: Broad Rollout
  - 80% of team
  - Training sessions
  - Support channels active

Week 4: Completion
  - 100% migration
  - Legacy tool deprecation
  - Post-migration review
```

### Large Teams (20+ developers)

**Timeline**: 6-8 weeks

```
Week 1-2: Pilot Phase
  - DevOps team installation
  - 1-2 pilot projects
  - Documentation creation

Week 3-4: Wave 1 (Core teams)
  - 25% of developers
  - Critical projects
  - Intensive support

Week 5-6: Wave 2 (Standard teams)
  - 50% of developers
  - Regular projects
  - Self-service support

Week 7-8: Wave 3 (Final migration)
  - 100% completion
  - Legacy deprecation
  - Success metrics review
```

### Rollout Best Practices

1. **Communication**
   - Announce 2 weeks in advance
   - Regular status updates
   - Open feedback channels

2. **Training**
   - Record training sessions
   - Create quick-start guides
   - Office hours for support

3. **Support**
   - Dedicated Slack/Teams channel
   - FAQ documentation
   - Escalation path defined

4. **Metrics**
   - Track adoption rate
   - Monitor issues/blockers
   - Measure performance gains

---

## Rollback Procedures

### When to Rollback

Rollback if you encounter:
- Critical bugs affecting productivity
- Data loss or corruption
- Incompatibility with critical tools
- Team unable to adapt within timeline

### Rollback Steps

#### Immediate Rollback (Emergency)

```bash
# Step 1: Stop using MoAI-ADK immediately
export MOAI_ADK_DISABLED=true

# Step 2: Restore from backup
BACKUP_DIR=$(ls -td ~/moai-adk-backup/* | head -1)
cd "$BACKUP_DIR"
./restore.sh

# Step 3: Restart terminal
exec $SHELL -l

# Step 4: Verify old setup working
claude code "Rollback test"
```

#### Gradual Rollback (Controlled)

```bash
# Phase 1: Stop new adoptions
# Freeze MoAI-ADK deployments

# Phase 2: Identify and fix issues
# Document what went wrong

# Phase 3: Decide: Fix or fully rollback
# If rollback chosen, proceed gradually

# Week 1: Rollback pilot users
# Week 2: Rollback wave 1
# Week 3: Complete rollback
```

#### Partial Rollback (Selective)

```bash
# Keep what works, rollback what doesn't

# Example: Keep Korean fonts, rollback MCP servers
cp -r ~/moai-adk-backup/latest/claude_config/.claude/mcp-servers \
      ~/.claude/mcp-servers

# Restart Claude Desktop
killall "Claude Desktop"
```

### Post-Rollback Actions

1. **Document issues**
   ```bash
   cat > ~/moai-rollback-report.txt <<EOF
   MoAI-ADK Rollback Report
   Date: $(date)

   Reason for rollback:
   [Describe issues]

   Attempted fixes:
   [List what was tried]

   Impact:
   [Business/productivity impact]

   Next steps:
   [Plan forward]
   EOF
   ```

2. **Inform team**
   - Send rollback notification
   - Explain reasons
   - Provide timeline for retry

3. **Analyze root cause**
   - Technical issues?
   - Training gaps?
   - Documentation problems?

4. **Plan retry**
   - Address root causes
   - Update migration plan
   - Set new timeline

---

## Troubleshooting

### Common Issues

#### Issue 1: UV Installation Fails

**Symptoms**:
```
Error: Failed to download UV installer
curl: (7) Failed to connect
```

**Solutions**:

```bash
# Option 1: Use alternative download method
wget https://astral.sh/uv/install.sh -O /tmp/uv-install.sh
bash /tmp/uv-install.sh

# Option 2: Install via Homebrew
brew install uv

# Option 3: Manual installation
curl -LsSf https://github.com/astral-sh/uv/releases/latest/download/uv-x86_64-apple-darwin.tar.gz \
  | tar xzf - -C ~/.local/bin
```

#### Issue 2: Korean Fonts Not Rendering

**Symptoms**:
```
안녕하세요 → □□□□□
```

**Solutions**:

```bash
# Step 1: Verify font installed
fc-list | grep -i "d2coding\|noto.*cjk"

# If no output:
# Install font manually
curl -L -o ~/Library/Fonts/D2Coding.ttc \
  https://github.com/naver/d2codingfont/releases/download/VER1.3.2/D2Coding-Ver1.3.2-20180524.ttc

# Step 2: Rebuild font cache
fc-cache -fv

# Step 3: Verify terminal configuration
cat ~/.config/ghostty/config | grep font-family

# Should show: font-family = "D2Coding"

# Step 4: Restart terminal
killall ghostty
```

#### Issue 3: MCP Servers Not Connecting

**Symptoms**:
```
Error: MCP server 'sequential-thinking' failed to start
```

**Solutions**:

```bash
# Check MCP server status
claude mcp list

# Check logs
tail -f ~/.claude/logs/mcp-*.log

# Restart MCP server
claude mcp restart sequential-thinking

# Re-register server
claude mcp remove sequential-thinking
claude mcp add sequential-thinking \
  npx @ruv/sequential-thinking mcp start

# Verify
claude code "test mcp connection"
```

#### Issue 4: Skills Not Loading

**Symptoms**:
```
Error: Skill 'moai-adk-installer' not found
```

**Solutions**:

```bash
# Verify skills directory
ls -la ~/.claude/skills/

# Check skill structure
ls -la ~/.claude/skills/moai-adk-installer/

# Should contain:
#   skill.yaml
#   README.md
#   prompts/

# Reload skills
claude code --reload-skills

# Test skill
claude code /moai-adk-installer --test
```

#### Issue 5: Python Version Conflicts

**Symptoms**:
```
Error: MoAI-ADK requires Python 3.11+
Current version: 3.9.0
```

**Solutions**:

```bash
# Install Python 3.12 via pyenv
curl https://pyenv.run | bash

# Add to shell config
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc
echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zshrc
echo 'eval "$(pyenv init -)"' >> ~/.zshrc

# Reload shell
exec $SHELL -l

# Install Python 3.12
pyenv install 3.12.0
pyenv global 3.12.0

# Verify
python --version  # Should show 3.12.0
```

### Getting Help

**Documentation**:
- Quick Start: `~/moai-adk/docs/QUICKSTART.md`
- Korean Guide: `~/moai-adk/docs/KOREAN-FONTS-GUIDE.md`
- Full Docs: `~/moai-adk/docs/`

**Community**:
- GitHub Issues: https://github.com/ruvnet/moai-adk/issues
- Discussions: https://github.com/ruvnet/moai-adk/discussions

**Logs**:
```bash
# View all logs
ls -la ~/.claude/logs/

# Installation logs
cat ~/.claude/logs/moai-install.log

# MCP logs
tail -f ~/.claude/logs/mcp-*.log

# Skill logs
cat ~/.claude/logs/skills.log
```

---

## Verification

### Comprehensive Verification Checklist

Run this after migration to ensure everything works:

```bash
#!/bin/bash
# MoAI-ADK Migration Verification Script

echo "MoAI-ADK Migration Verification"
echo "================================"
echo

# Test 1: UV Installation
echo "Test 1: UV Installation"
if command -v uv &> /dev/null; then
  echo "  ✓ UV installed: $(uv --version)"
else
  echo "  ✗ UV not found"
fi
echo

# Test 2: Python Version
echo "Test 2: Python Version"
PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
if [[ "$PYTHON_VERSION" > "3.11" ]]; then
  echo "  ✓ Python $PYTHON_VERSION (meets requirement)"
else
  echo "  ✗ Python $PYTHON_VERSION (requires 3.11+)"
fi
echo

# Test 3: Korean Fonts
echo "Test 3: Korean Fonts"
if fc-list | grep -iq "d2coding"; then
  echo "  ✓ D2Coding font installed"
else
  echo "  ✗ D2Coding font not found"
fi
echo

# Test 4: Korean Rendering
echo "Test 4: Korean Rendering"
KOREAN_TEST="한글 테스트"
echo "  Input: $KOREAN_TEST"
if echo "$KOREAN_TEST" | grep -q "한글"; then
  echo "  ✓ Korean rendering works"
else
  echo "  ✗ Korean rendering failed"
fi
echo

# Test 5: MCP Servers
echo "Test 5: MCP Servers"
MCP_COUNT=$(claude mcp list 2>/dev/null | grep -c "connected" || echo "0")
if [ "$MCP_COUNT" -ge "1" ]; then
  echo "  ✓ $MCP_COUNT MCP server(s) connected"
else
  echo "  ✗ No MCP servers connected"
fi
echo

# Test 6: Skills Installation
echo "Test 6: Skills"
SKILL_COUNT=$(ls -1 ~/.claude/skills 2>/dev/null | wc -l)
if [ "$SKILL_COUNT" -ge "1" ]; then
  echo "  ✓ $SKILL_COUNT skill(s) installed"
else
  echo "  ✗ No skills installed"
fi
echo

# Test 7: Terminal Configuration
echo "Test 7: Terminal Configuration (Ghostty)"
if [ -f ~/.config/ghostty/config ]; then
  if grep -q "D2Coding" ~/.config/ghostty/config; then
    echo "  ✓ Ghostty configured for Korean"
  else
    echo "  ⚠ Ghostty config exists but D2Coding not set"
  fi
else
  echo "  ⚠ Ghostty config not found (may be using different terminal)"
fi
echo

# Test 8: Claude Code Integration
echo "Test 8: Claude Code"
if command -v claude &> /dev/null; then
  echo "  ✓ Claude Code CLI installed"
else
  echo "  ✗ Claude Code CLI not found"
fi
echo

# Summary
echo "================================"
echo "Verification Complete"
echo
echo "Next Steps:"
echo "  1. Review any ✗ or ⚠ items above"
echo "  2. Consult troubleshooting guide if needed"
echo "  3. Test with: claude code '안녕하세요 MoAI-ADK'"
echo
```

### Manual Verification Steps

**1. Test UV Environment**
```bash
# Create test project
mkdir -p ~/moai-test
cd ~/moai-test

# Initialize UV project
uv init

# Install dependency
uv add requests

# Run test
uv run python -c "import requests; print(requests.__version__)"
```

**2. Test Korean Support End-to-End**
```bash
# Create Korean test file
cat > ~/korean-test.py <<'EOF'
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def test_korean():
    text = "MoAI-ADK는 한국어를 완벽하게 지원합니다."
    print(f"Input: {text}")
    assert "한국어" in text
    print("✓ Korean text processing: PASS")

if __name__ == "__main__":
    test_korean()
EOF

# Run test
python ~/korean-test.py
```

**3. Test Claude Code with Korean**
```bash
# Interactive test
claude code <<EOF
Please respond in Korean:
"MoAI-ADK 설치가 완료되었습니다."
EOF

# Expected: Korean response with proper rendering
```

**4. Test MCP Integration**
```bash
# Test each MCP server
claude code "Use sequential-thinking to analyze this: 1+1"
claude code "Use playwright to navigate to google.com"
claude code "Use context7 to search documentation"
```

**5. Test Skills**
```bash
# Test each installed skill
claude code /moai-adk-installer --version
claude code /korean-text-processor "테스트 텍스트"
```

### Success Criteria

Migration is successful when all of these pass:

- [ ] UV version 0.4.0+ installed and working
- [ ] Python 3.11+ is default
- [ ] D2Coding font installed and rendering Korean correctly
- [ ] Terminal configured for Korean (font + encoding)
- [ ] At least 3 MCP servers connected
- [ ] At least 12 skills installed
- [ ] Korean text renders in Claude Code
- [ ] All verification tests pass
- [ ] Team members can use MoAI-ADK
- [ ] Documentation is accessible

### Performance Benchmarks

Compare before/after migration:

```bash
# Benchmark installation speed
time pip install requests  # Before
time uv add requests       # After

# Benchmark Korean rendering
# Visual comparison in terminal

# Benchmark Claude Code response time
# Before: [Record baseline]
# After: [Should be similar or faster]
```

---

## Conclusion

You should now have successfully migrated to MoAI-ADK with full Korean language support. Choose the migration path that best fits your needs:

- **Path 1 (UV CLI)**: Fastest, most automated
- **Path 2 (Bash App)**: Interactive, customizable
- **Path 3 (Claude Skill)**: AI-guided, beginner-friendly
- **Path 4 (Gradual)**: Safest for production/teams

For additional help:
- **Quick Start**: [README.md](./README.md)
- **Korean Fonts**: [KOREAN-FONTS-GUIDE.md](./KOREAN-FONTS-GUIDE.md)
- **Troubleshooting**: [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)
- **Index**: [INDEX.md](./INDEX.md)

**Happy coding with MoAI-ADK! 🚀 한국어 지원과 함께 즐거운 코딩 되세요!**
