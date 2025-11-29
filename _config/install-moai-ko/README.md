# MoAI-ADK Installation Guide

**Version**: 1.0.0
**Korean Support**: Full (D2Coding font, UTF-8 encoding)
**Pattern**: Beyond-MCP (3 installation approaches)

Complete installation guide for MoAI-ADK (Mixture of AI Agents Development Kit) with native Korean language support.

---

## Table of Contents

1. [Overview](#overview)
2. [Beyond-MCP Pattern](#beyond-mcp-pattern)
3. [Installation Approaches](#installation-approaches)
4. [Quick Start](#quick-start)
5. [Korean Language Support](#korean-language-support)
6. [Comparison Matrix](#comparison-matrix)
7. [Progressive Disclosure](#progressive-disclosure)
8. [Directory Structure](#directory-structure)
9. [Requirements](#requirements)
10. [Examples](#examples)
11. [Documentation](#documentation)
12. [Troubleshooting](#troubleshooting)

---

## Overview

### What is MoAI-ADK?

MoAI-ADK is a comprehensive framework for building multi-agent AI systems with:

✅ **Full Korean Support**: Native Korean fonts (D2Coding), UTF-8 encoding, CJK rendering
✅ **Beyond-MCP Pattern**: 3 installation approaches (UV, Bash, Skills)
✅ **Progressive Disclosure**: Start simple, grow complex
✅ **Production Ready**: 140+ tests, comprehensive documentation
✅ **Team Friendly**: Rollout plans, rollback procedures

### Key Features

- **Multi-Agent Orchestration**: Coordinate multiple AI agents with swarm intelligence
- **Korean Language Native**: First-class Korean support throughout
- **Flexible Installation**: Choose the approach that fits your workflow
- **Terminal Agnostic**: Works with Ghostty, iTerm2, Warp, and more
- **MCP Integration**: Compatible with Model Context Protocol servers
- **Skill System**: Extensible with Claude Code skills
- **Production Tested**: Comprehensive test suite with CI/CD ready

---

## Beyond-MCP Pattern

MoAI-ADK implements the **Beyond-MCP** pattern, providing three installation approaches:

```
┌──────────────────────────────────────────────────────────┐
│           BEYOND-MCP INSTALLATION PATTERN                 │
├──────────────────────────────────────────────────────────┤
│                                                            │
│  Approach 1: UV CLI Scripts                               │
│  └─ Direct command-line installation                      │
│  └─ Best for: Automation, developers, CI/CD               │
│  └─ Speed: Fast (10-15 min)                               │
│                                                            │
│  Approach 2: Bash Apps                                    │
│  └─ Interactive shell-based installation                  │
│  └─ Best for: Customization, learning                     │
│  └─ Speed: Medium (15-20 min)                             │
│                                                            │
│  Approach 3: Claude Skills                                │
│  └─ AI-assisted installation with guidance                │
│  └─ Best for: Beginners, progressive disclosure           │
│  └─ Speed: Slower (20-30 min) but educational             │
│                                                            │
└──────────────────────────────────────────────────────────┘
```

### Why Beyond-MCP?

Traditional MCP (Model Context Protocol) installations are limited to server configurations. Beyond-MCP extends this with:

1. **Multiple Entry Points**: UV scripts, Bash apps, or AI skills
2. **Progressive Complexity**: Start simple, add features as needed
3. **User Choice**: Pick the approach matching your expertise level
4. **Consistent Results**: All approaches produce the same working system

### Pattern Benefits

| Benefit | UV CLI | Bash App | Claude Skill |
|---------|--------|----------|--------------|
| **Speed** | ⚡⚡⚡ | ⚡⚡ | ⚡ |
| **Automation** | ✅ | ⚠️ | ❌ |
| **Customization** | ⚠️ | ✅ | ✅ |
| **Learning** | ⚠️ | ✅ | ⚡⚡⚡ |
| **CI/CD Ready** | ✅ | ⚠️ | ❌ |
| **Beginner Friendly** | ⚠️ | ✅ | ⚡⚡⚡ |

---

## Installation Approaches

### Approach 1: UV CLI Scripts (Recommended)

**Best for**: Developers, automation, clean installations

**Installation**:

```bash
# Install UV package manager
curl -LsSf https://astral.sh/uv/install.sh | sh

# Navigate to install directory
cd /path/to/moai-adk/_config/install-moai-ko

# Run installer with Korean font support
uv run install-moai-adk.py --korean-fonts

# Or with full options
uv run install-moai-adk.py \
  --korean-fonts \
  --ghostty-config \
  --yes
```

**Features**:
- Fastest installation (10-15 minutes)
- Fully automated with optional flags
- CI/CD compatible
- Idempotent (safe to re-run)
- Comprehensive logging

**Korean Support**:
```bash
# Automatic Korean font installation
uv run install-moai-adk.py --korean-fonts

# Verify Korean rendering
echo "한글 테스트: MoAI-ADK" | cat
```

---

### Approach 2: Bash Apps

**Best for**: Interactive setup, customization, learning

**Installation**:

```bash
# Set executable permissions
chmod +x install-moai-adk.sh

# Run interactive installer
./install-moai-adk.sh --interactive

# Or with specific options
./install-moai-adk.sh \
  --korean-fonts \
  --ghostty-config \
  --verbose
```

**Features**:
- Interactive prompts for each step
- Visual progress indicators
- Customizable installation paths
- Real-time feedback
- Error recovery prompts

**Interactive Experience**:

```
═══════════════════════════════════════════════
MoAI-ADK Interactive Installation
═══════════════════════════════════════════════

Select language:
  1) English
  2) 한국어 (Korean)

Choice [1]: 2

Installation path [/Users/username/moai-adk]:

Install Korean fonts (D2Coding)? [Y/n]: Y

Configure Ghostty for Korean? [Y/n]: Y

Select MCP servers to install:
  [x] 1) Sequential Thinking
  [x] 2) Playwright
  [ ] 3) Context7
  [x] 4) All servers

Selection [4]:

[Installing...]
✓ MoAI-ADK installed successfully!
```

---

### Approach 3: Claude Skills

**Best for**: Beginners, AI-assisted setup, progressive learning

**Installation**:

```bash
# Method 1: Via Claude Code CLI
claude code --install-skill moai-adk-installer

# Method 2: Manual skill installation
mkdir -p ~/.claude/skills
cp -r moai-adk/_config/install-moai-ko/skills/moai-adk-installer \
      ~/.claude/skills/

# Invoke skill
claude code /moai-adk-installer
```

**Features**:
- AI-guided step-by-step installation
- Contextual explanations at each step
- Automatic error recovery
- Progressive disclosure of complexity
- Educational experience

**AI-Guided Experience**:

```
MoAI-ADK Installation Assistant
═══════════════════════════════════════════════

I'll guide you through installing MoAI-ADK with full Korean support.

Current System:
  - OS: macOS 14.7.1
  - UV: Not installed ⚠️
  - Korean Fonts: Not installed ⚠️

I recommend:
  1. Installing UV package manager (5 min)
  2. Installing D2Coding font (2 min)
  3. Configuring Ghostty terminal (3 min)
  4. Setting up MCP servers (5 min)

Total estimated time: 15 minutes

Shall we begin? [Y/n]: Y

Step 1/4: Installing UV Package Manager
───────────────────────────────────────

UV is a fast Python package manager. I'll install it using:
  curl -LsSf https://astral.sh/uv/install.sh | sh

This is safe and recommended by the UV project.

Proceed? [Y/n]:
```

---

## Quick Start

### 5-Minute Installation (UV CLI)

```bash
# 1. Install UV (1 min)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Clone or navigate to MoAI-ADK
cd /path/to/moai-adk/_config/install-moai-ko

# 3. Run installer (10-15 min)
uv run install-moai-adk.py --korean-fonts --yes

# 4. Verify installation (1 min)
./verify-installation.sh

# 5. Test Korean support
echo "안녕하세요 MoAI-ADK" | cat
```

### First Commands

```bash
# Test UV environment
uv --version

# Test Python
python --version

# Test Korean fonts
fc-list | grep -i d2coding

# Test Claude Code with Korean
claude code "한국어 테스트"

# List installed skills
claude code --list-skills | grep moai

# Check MCP servers
claude mcp list
```

---

## Korean Language Support

### Why Korean Support Matters

Korean (Hangul) requires specific font and encoding support:

❌ **Without proper support**: 안녕하세요 → □□□□□
✅ **With MoAI-ADK**: 안녕하세요 → 안녕하세요

### Included Korean Features

1. **D2Coding Font**
   - Optimized for code editing
   - Clear Hangul rendering
   - Monospace for terminals
   - Free and open-source

2. **UTF-8 Encoding**
   - Automatic UTF-8 configuration
   - Proper CJK character handling
   - Terminal encoding setup

3. **Terminal Configuration**
   - Ghostty optimized settings
   - Font rendering tweaks
   - Line spacing adjustments

4. **Testing**
   - Korean rendering tests
   - Font verification
   - Character encoding validation

### Korean Font Installation

```bash
# Automatic (recommended)
uv run install-moai-adk.py --korean-fonts

# Manual
curl -L -o ~/Library/Fonts/D2Coding.ttc \
  https://github.com/naver/d2codingfont/releases/download/VER1.3.2/D2Coding-Ver1.3.2-20180524.ttc

# Verify
fc-list | grep D2Coding
```

### Terminal Configuration for Korean

**Ghostty** (Recommended):

```toml
# ~/.config/ghostty/config

# Korean Font Support
font-family = "D2Coding"
font-size = 14
font-feature = -calt

# Korean Character Rendering
font-synthetic-style = false
grapheme-width-method = legacy

# CJK Support
shell-integration-features = true
```

**iTerm2**:

```
Preferences → Profiles → Text
  Font: D2Coding Regular 14pt
  Character Spacing: 1.0
  Line Spacing: 1.1

Preferences → Profiles → Terminal
  Character Encoding: UTF-8
```

**Warp**:

```toml
# ~/.warp/config.yaml

font:
  family: "D2Coding"
  size: 14

terminal:
  encoding: "UTF-8"
```

### Korean Testing

```bash
# Basic rendering test
echo "한글 테스트: MoAI-ADK" | cat

# Claude Code test
claude code "한국어로 응답해주세요: MoAI-ADK 설치 완료"

# Visual comparison
printf "Korean text: 안녕하세요\n"
printf "English text: Hello\n"
printf "Mixed: Hello 안녕하세요\n"

# Character encoding test
python3 -c "print('한글 인코딩 테스트: ✓'.encode('utf-8'))"
```

For detailed Korean configuration, see [KOREAN-FONTS-GUIDE.md](./KOREAN-FONTS-GUIDE.md).

---

## Comparison Matrix

### Installation Approaches Comparison

| Feature | UV CLI | Bash App | Claude Skill |
|---------|--------|----------|--------------|
| **Installation Time** | 10-15 min | 15-20 min | 20-30 min |
| **Automation** | Full | Partial | AI-guided |
| **Customization** | Flags | Interactive | Conversational |
| **CI/CD Ready** | ✅ Yes | ⚠️ Limited | ❌ No |
| **Beginner Friendly** | ⚠️ Moderate | ✅ Yes | ⚡ Excellent |
| **Error Recovery** | Automatic | Prompted | AI-assisted |
| **Documentation** | CLI help | Interactive | Contextual |
| **Learning Curve** | Steep | Moderate | Gentle |
| **Reproducibility** | High | Medium | Low |
| **Offline Support** | Partial | Yes | No (requires API) |

### Korean Support Comparison

| Feature | UV CLI | Bash App | Claude Skill |
|---------|--------|----------|--------------|
| **Font Installation** | ✅ Auto | ✅ Auto | ✅ Auto |
| **Terminal Config** | ✅ Auto | ✅ Interactive | ✅ Guided |
| **Encoding Setup** | ✅ Auto | ✅ Auto | ✅ Auto |
| **Rendering Test** | ✅ Yes | ✅ Yes | ✅ Yes |
| **Troubleshooting** | Docs | Interactive | AI-assisted |

### Use Case Recommendations

**Choose UV CLI if**:
- You're comfortable with command-line tools
- You need to automate installation
- You're setting up CI/CD pipelines
- You want the fastest installation
- You prefer idempotent scripts

**Choose Bash App if**:
- You prefer interactive setup
- You want to customize each step
- You're learning the installation process
- You need visual progress feedback
- You want to review before applying

**Choose Claude Skill if**:
- You're new to these tools
- You want AI guidance throughout
- You prefer conversational interfaces
- You value educational explanations
- You have an Anthropic API key

---

## Progressive Disclosure

MoAI-ADK follows progressive disclosure principles - start simple, grow as needed.

### Level 1: Basic Installation (5 minutes)

```bash
# Simplest possible installation
uv run install-moai-adk.py --yes
```

**What you get**:
- UV package manager
- Python environment
- Basic MCP servers
- Essential skills

### Level 2: Korean Support (10 minutes)

```bash
# Add Korean language support
uv run install-moai-adk.py --korean-fonts --yes
```

**Additional features**:
- D2Coding font installed
- Terminal configured for Korean
- UTF-8 encoding set up
- Korean rendering verified

### Level 3: Full Customization (15-20 minutes)

```bash
# Interactive installation with all options
./install-moai-adk.sh --interactive
```

**Full control over**:
- Installation directory
- MCP server selection
- Skill installation
- Terminal configuration
- Font preferences

### Level 4: Advanced Configuration (30+ minutes)

```bash
# Manual configuration for production
uv run install-moai-adk.py --dry-run
# Review installation plan
# Customize as needed
# Apply changes incrementally
```

**Advanced features**:
- Custom MCP server endpoints
- Skill development environment
- Multi-user setup
- Team rollout plan
- Production hardening

### Complexity Growth Path

```
Level 1: Basic      →  uv run install-moai-adk.py --yes
         (5 min)        Just get it working

Level 2: Korean     →  uv run install-moai-adk.py --korean-fonts --yes
         (10 min)       Add language support

Level 3: Custom     →  ./install-moai-adk.sh --interactive
         (20 min)       Tailor to your needs

Level 4: Advanced   →  Manual configuration + team rollout
         (1-2 hrs)      Production deployment
```

---

## Directory Structure

### Installation Directory Layout

```
moai-adk/
├── _config/
│   └── install-moai-ko/              # This installation guide
│       ├── README.md                 # This file (700 lines)
│       ├── MIGRATION-GUIDE.md        # Migration from existing setups (750 lines)
│       ├── KOREAN-FONTS-GUIDE.md     # Korean font documentation (600 lines)
│       ├── INDEX.md                  # Documentation index (350 lines)
│       ├── test-suite.sh             # Comprehensive tests (650 lines, 140+ tests)
│       ├── install-moai-adk.py       # UV installer script
│       ├── install-moai-adk.sh       # Bash installer app
│       ├── verify-installation.sh    # Post-install verification
│       ├── apps/                     # Bash apps
│       │   ├── interactive-installer.sh
│       │   ├── korean-font-setup.sh
│       │   └── terminal-config.sh
│       ├── scripts/                  # UV scripts
│       │   ├── install-uv.py
│       │   ├── install-fonts.py
│       │   ├── configure-terminal.py
│       │   └── setup-mcp.py
│       └── skills/                   # Claude skills
│           └── moai-adk-installer/
│               ├── skill.yaml
│               ├── README.md
│               └── prompts/
│                   ├── main.md
│                   ├── install-uv.md
│                   ├── install-fonts.md
│                   └── verify.md
│
├── docs/                             # Documentation
│   ├── QUICKSTART.md
│   ├── API-REFERENCE.md
│   ├── ARCHITECTURE.md
│   └── TROUBLESHOOTING.md
│
├── src/                              # Source code
│   ├── agents/                       # Multi-agent system
│   ├── orchestration/                # Swarm coordination
│   ├── korean/                       # Korean language support
│   └── mcp/                          # MCP integrations
│
├── tests/                            # Test suite
│   ├── unit/
│   ├── integration/
│   └── e2e/
│
└── examples/                         # Example projects
    ├── basic-agent/
    ├── korean-chatbot/
    └── multi-agent-swarm/
```

### Post-Installation Directory

After installation, you'll have:

```
~/moai-adk/                           # Installation root (or custom path)
├── bin/                              # Executables
│   ├── moai                          # Main CLI
│   └── moai-agent                    # Agent runner
│
├── lib/                              # Libraries
│   ├── python3.12/                   # Python packages
│   └── korean/                       # Korean support libs
│
├── share/                            # Shared resources
│   ├── fonts/                        # Installed fonts
│   ├── templates/                    # Project templates
│   └── docs/                         # Documentation
│
├── var/                              # Variable data
│   ├── logs/                         # Log files
│   └── cache/                        # Cache directory
│
└── .venv/                            # Python virtual environment
```

### Claude Configuration Updates

```
~/.claude/
├── claude_desktop_config.json        # MCP servers registered here
├── skills/                           # Skills installed here
│   ├── moai-adk-installer/
│   ├── korean-text-processor/
│   └── multi-agent-coordinator/
├── commands/                         # Custom commands
└── logs/                             # Claude logs
```

---

## Requirements

### System Requirements

**Minimum**:
- OS: macOS 12+, Ubuntu 20.04+, or Windows 11 (WSL2)
- RAM: 2GB free
- Disk: 2GB free space
- Python: 3.11+
- Internet: Required for installation

**Recommended**:
- OS: macOS 14+, Ubuntu 22.04+
- RAM: 4GB free
- Disk: 5GB free space
- Python: 3.12+
- Internet: High-speed connection

### Software Requirements

**Required**:
```bash
# UV package manager
curl -LsSf https://astral.sh/uv/install.sh | sh

# Python 3.11+
python3 --version

# Git (for cloning repositories)
git --version
```

**Optional but Recommended**:
```bash
# Claude Code CLI
npm install -g @anthropic-ai/claude-code

# Ghostty terminal (best Korean support)
brew install ghostty

# Homebrew (macOS)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### Terminal Requirements

For proper Korean rendering, your terminal must support:

✅ **UTF-8 encoding**
✅ **TrueType fonts (TTF/TTC)**
✅ **CJK character rendering**
✅ **Font ligatures** (optional but recommended)

**Tested Terminals**:
- ✅ Ghostty (Excellent Korean support)
- ✅ iTerm2 (Good Korean support)
- ✅ Warp (Good Korean support)
- ⚠️ Terminal.app (Basic support, may need tweaks)
- ⚠️ VS Code integrated terminal (Depends on VS Code font config)

### Network Requirements

**During Installation**:
- Access to `https://astral.sh` (UV installer)
- Access to `https://github.com` (fonts, packages)
- Access to `https://pypi.org` (Python packages)
- Access to Anthropic API (if using Claude Skill approach)

**After Installation**:
- MCP servers require internet (optional)
- Skills work offline (except API-dependent ones)

---

## Examples

### Example 1: Clean Installation with Korean Support

```bash
# Step 1: Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"

# Step 2: Clone MoAI-ADK (or navigate to existing directory)
git clone https://github.com/ruvnet/moai-adk.git ~/moai-adk
cd ~/moai-adk/_config/install-moai-ko

# Step 3: Run installer with Korean fonts
uv run install-moai-adk.py --korean-fonts --yes

# Step 4: Verify
./verify-installation.sh

# Step 5: Test Korean
echo "한글 테스트: ✓ 성공" | cat
claude code "안녕하세요 MoAI-ADK"
```

### Example 2: Interactive Customization

```bash
# Navigate to installer
cd ~/moai-adk/_config/install-moai-ko

# Make installer executable
chmod +x install-moai-adk.sh

# Run interactive installation
./install-moai-adk.sh --interactive

# Follow prompts:
# - Select language: Korean (2)
# - Installation path: (press Enter for default)
# - Install Korean fonts: Y
# - Configure Ghostty: Y
# - Select MCP servers: 4 (all)

# Wait for installation to complete
# Review summary
# Restart terminal
```

### Example 3: AI-Guided Installation

```bash
# Install skill first
claude code --install-skill moai-adk-installer

# Or manually
mkdir -p ~/.claude/skills
cp -r ~/moai-adk/_config/install-moai-ko/skills/moai-adk-installer \
      ~/.claude/skills/

# Invoke installation assistant
claude code /moai-adk-installer

# Chat with AI:
# You: "I want to install MoAI-ADK with Korean support"
# AI: "I'll guide you through the process..."
# [Follow AI instructions step-by-step]
```

### Example 4: CI/CD Automated Installation

```yaml
# .github/workflows/install-moai-adk.yml

name: Install MoAI-ADK
on: [push, pull_request]

jobs:
  install:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Install UV
        run: curl -LsSf https://astral.sh/uv/install.sh | sh

      - name: Install MoAI-ADK
        run: |
          cd _config/install-moai-ko
          uv run install-moai-adk.py --korean-fonts --yes

      - name: Verify Installation
        run: |
          cd _config/install-moai-ko
          ./verify-installation.sh

      - name: Test Korean Rendering
        run: |
          echo "한글 테스트" | grep "한글"
```

### Example 5: Custom Installation Path

```bash
# Install to custom location
uv run install-moai-adk.py \
  --install-path /opt/moai-adk \
  --korean-fonts \
  --verbose

# Add to PATH
echo 'export PATH="/opt/moai-adk/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

# Verify
which moai
moai --version
```

### Example 6: Team Rollout

```bash
# Admin prepares installation package
cd ~/moai-adk/_config/install-moai-ko
tar czf moai-adk-install-package.tar.gz \
  install-moai-adk.py \
  install-moai-adk.sh \
  apps/ \
  scripts/ \
  skills/

# Distribute to team
# Team members extract and run:
tar xzf moai-adk-install-package.tar.gz
cd install-moai-ko
./install-moai-adk.sh --interactive

# Or fully automated for team:
uv run install-moai-adk.py --korean-fonts --yes
```

---

## Documentation

### Available Documentation

**Core Documentation**:
- [README.md](./README.md) - This file (installation guide)
- [MIGRATION-GUIDE.md](./MIGRATION-GUIDE.md) - Migration from existing setups
- [KOREAN-FONTS-GUIDE.md](./KOREAN-FONTS-GUIDE.md) - Korean font configuration
- [INDEX.md](./INDEX.md) - Documentation index and navigation

**Additional Guides**:
- `~/moai-adk/docs/QUICKSTART.md` - Quick start tutorial
- `~/moai-adk/docs/API-REFERENCE.md` - API documentation
- `~/moai-adk/docs/ARCHITECTURE.md` - System architecture
- `~/moai-adk/docs/TROUBLESHOOTING.md` - Troubleshooting guide

### Getting Help

**Documentation**:
```bash
# View local documentation
cd ~/moai-adk/docs
ls -la

# Read specific guide
less ~/moai-adk/docs/QUICKSTART.md

# Search documentation
grep -r "korean font" ~/moai-adk/docs/
```

**Command Help**:
```bash
# UV installer help
uv run install-moai-adk.py --help

# Bash app help
./install-moai-adk.sh --help

# Claude skill help
claude code /moai-adk-installer --help
```

**Community Support**:
- GitHub Issues: https://github.com/ruvnet/moai-adk/issues
- Discussions: https://github.com/ruvnet/moai-adk/discussions
- Documentation: https://moai-adk.readthedocs.io

**Logs and Debugging**:
```bash
# View installation logs
cat ~/.claude/logs/moai-install.log

# View MCP logs
tail -f ~/.claude/logs/mcp-*.log

# Enable verbose logging
export MOAI_ADK_DEBUG=1
uv run install-moai-adk.py --verbose
```

---

## Troubleshooting

### Common Issues

#### Issue: Korean Characters Show as Boxes

**Symptom**: 안녕하세요 → □□□□□

**Solution**:
```bash
# 1. Verify font installed
fc-list | grep -i d2coding

# 2. If not found, install manually
curl -L -o ~/Library/Fonts/D2Coding.ttc \
  https://github.com/naver/d2codingfont/releases/download/VER1.3.2/D2Coding-Ver1.3.2-20180524.ttc

# 3. Rebuild font cache
fc-cache -fv

# 4. Restart terminal
exec $SHELL -l

# 5. Test again
echo "한글 테스트" | cat
```

#### Issue: UV Installation Fails

**Symptom**: `curl: (7) Failed to connect to astral.sh`

**Solution**:
```bash
# Alternative installation methods

# Method 1: Homebrew (macOS)
brew install uv

# Method 2: Manual download
curl -L https://github.com/astral-sh/uv/releases/latest/download/uv-x86_64-apple-darwin.tar.gz \
  | tar xzf - -C ~/.local/bin

# Method 3: pip
pip install uv

# Verify
uv --version
```

#### Issue: Python Version Too Old

**Symptom**: `Error: Python 3.11+ required, found 3.9.0`

**Solution**:
```bash
# Install Python 3.12 via pyenv
curl https://pyenv.run | bash

# Configure shell
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

#### Issue: MCP Servers Not Connecting

**Symptom**: `Error: MCP server failed to start`

**Solution**:
```bash
# Check server status
claude mcp list

# View logs
cat ~/.claude/logs/mcp-*.log

# Restart server
claude mcp restart [server-name]

# Re-register
claude mcp remove [server-name]
claude mcp add [server-name] [command]

# Test connection
claude code "test mcp"
```

For more troubleshooting, see [TROUBLESHOOTING.md](../docs/TROUBLESHOOTING.md).

---

## Next Steps

After installation:

1. **Verify Everything Works**
   ```bash
   ./verify-installation.sh
   ```

2. **Test Korean Support**
   ```bash
   echo "한글 테스트: ✓ 성공" | cat
   claude code "안녕하세요"
   ```

3. **Read Quick Start Guide**
   ```bash
   less ~/moai-adk/docs/QUICKSTART.md
   ```

4. **Try Example Projects**
   ```bash
   cd ~/moai-adk/examples/korean-chatbot
   uv run main.py
   ```

5. **Join Community**
   - Star the repo: https://github.com/ruvnet/moai-adk
   - Join discussions
   - Report issues or suggest features

---

## License

MoAI-ADK is open-source software licensed under MIT License.

## Credits

- **MoAI-ADK**: Mixture of AI Agents Development Kit
- **UV**: Astral.sh UV package manager
- **D2Coding Font**: Naver Corporation
- **Claude Code**: Anthropic
- **Beyond-MCP Pattern**: MoAI-ADK team

---

**Happy coding with MoAI-ADK! 🚀**

**한국어 지원과 함께 즐거운 코딩 되세요!**
