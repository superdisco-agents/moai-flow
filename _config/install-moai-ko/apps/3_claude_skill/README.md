# MoAI-ADK Claude Skill Installer

Autonomous, conversational installation of MoAI-ADK through Claude Code with zero-command setup and intelligent Korean language auto-detection.

## Overview

The Claude Skill installer represents the most autonomous installation approach:

- **Zero-command installation** - Just ask Claude
- **Intelligent auto-detection** - Locale, system requirements, preferences
- **Conversational interface** - Natural language interaction
- **Context-aware decisions** - Claude adapts to your environment
- **Autonomous error recovery** - Self-healing installation
- **Seamless integration** - Native Claude Code workflow

## Philosophy

Unlike traditional installers that require learning commands and flags, the Claude Skill installer operates through natural conversation:

```
You: "Install MoAI-ADK with Korean support"

Claude: "I've detected your system is running macOS with Korean locale
         (ko_KR.UTF-8). I'll install:

         1. UV package manager
         2. MoAI-ADK package
         3. Nanum Gothic and Nanum Gothic Coding fonts
         4. Korean NLP configuration

         Starting installation..."
```

## Key Features

### 1. Autonomous Installation

**Traditional Approach:**
```bash
./install.sh --korean --verbose
# User must know flags, order, syntax
```

**Claude Skill Approach:**
```
User: "Set up MoAI-ADK for Korean language work"

Claude: *automatically detects locale*
        *installs fonts*
        *configures NLP*
        *verifies installation*
        "Done! MoAI-ADK is ready for Korean language processing."
```

### 2. Intelligent Auto-Detection

Claude analyzes multiple signals:

- **System locale** (`LANG`, `LC_ALL`)
- **User's language** in conversation
- **Previous interactions** (memory)
- **Project context** (existing files)
- **Keyboard layout** settings

**Example:**
```
User: "MoAI-ADK 설치해줘" (Korean: "Install MoAI-ADK")

Claude: "한국어로 대화하시는 것을 감지했습니다. (Detected Korean conversation)
         한국어 폰트와 NLP 기능을 포함하여 설치하겠습니다.
         (I'll install with Korean fonts and NLP features.)"
```

### 3. Context-Aware Decisions

Claude makes intelligent decisions based on context:

**Scenario 1: Developer Environment**
```
User: "Install MoAI-ADK"

Claude: *detects existing Python virtual environment*
        "I see you're using a virtual environment at ./venv.
         Should I install MoAI-ADK there, or system-wide?"
```

**Scenario 2: Korean User**
```
User: "Install MoAI-ADK"

Claude: *detects ko_KR.UTF-8 locale*
        *checks for existing Korean fonts*
        "I noticed you don't have Nanum fonts installed.
         I'll add them along with MoAI-ADK."
```

**Scenario 3: Upgrade**
```
User: "Install MoAI-ADK"

Claude: *detects existing installation*
        "I found MoAI-ADK v0.9.0 already installed.
         Would you like to upgrade to v1.0.0?"
```

### 4. Self-Healing Installation

Claude automatically handles errors:

```
Error: Python 3.9 detected (3.11+ required)

Claude: "I see Python 3.9, but MoAI-ADK needs 3.11+.
         I can:
         1. Help you install Python 3.11 via Homebrew
         2. Guide you to use pyenv for version management
         3. Show you manual installation steps

         Which would you prefer?"
```

### 5. Conversational Troubleshooting

```
User: "The installation isn't working"

Claude: "Let me check the logs...
         I see the issue: UV isn't in your PATH.
         Run this command to fix it:

         export PATH=\"$HOME/.cargo/bin:$PATH\"

         Then source your shell config:
         source ~/.zshrc

         Should I add this to your .zshrc permanently?"
```

## Setup Instructions

### Option 1: Symlink .claude/ Directory (Recommended)

```bash
# Navigate to installation location
cd /path/to/moai-adk/_config/install-moai-ko/apps/3_claude_skill

# Create symlink to Claude Code's skills directory
ln -s "$(pwd)/.claude" ~/.claude/skills/moai-installer

# Verify symlink
ls -la ~/.claude/skills/moai-installer
```

### Option 2: Copy .claude/ Directory

```bash
# Copy to Claude Code's skills directory
cp -r .claude ~/.claude/skills/moai-installer
```

### Option 3: Add to Project

```bash
# Copy to your project's .claude directory
cp -r .claude /path/to/your/project/.claude/moai-installer
```

## Usage

### Trigger Phrases

Claude recognizes natural language variations:

**English:**
- "Install MoAI-ADK"
- "Set up MoAI-ADK with Korean support"
- "I need MoAI-ADK installed"
- "Help me install the Mixture of Agents kit"
- "Add MoAI-ADK to this project"

**Korean:**
- "MoAI-ADK 설치해줘"
- "MoAI-ADK 한국어로 설정해줘"
- "Mixture of Agents 설치 도와줘"
- "MoAI-ADK 프로젝트에 추가해줘"

**Mixed:**
- "Install MoAI-ADK 한국어 support please"
- "MoAI-ADK setup for Korean language"

### Example Conversations

#### Example 1: Basic Installation

```
User: "Install MoAI-ADK"

Claude: "I'll install MoAI-ADK. Checking your system...

         ✓ Python 3.11.5 detected
         ✓ 45 GB disk space available
         ✓ Network connectivity confirmed

         Your system locale is ko_KR.UTF-8.
         Would you like Korean language support? (Y/n)"

User: "Yes"

Claude: "Installing:
         [1/5] Creating ~/.moai directory structure... ✓
         [2/5] Installing UV package manager... ✓
         [3/5] Installing MoAI-ADK via UV... ✓
         [4/5] Installing Korean fonts (Nanum Gothic)... ✓
         [5/5] Configuring Korean NLP features... ✓

         Installation complete!

         To get started:
         source ~/.moai/activate.sh

         Test it:
         python3 -c 'import moai_adk; print(moai_adk.__version__)'"
```

#### Example 2: Troubleshooting

```
User: "MoAI-ADK installation failed"

Claude: "Let me investigate...

         I found the issue in ~/.moai/logs/installer.log:

         Error: UV not found in PATH

         To fix this:

         1. Add UV to your PATH:
            echo 'export PATH=\"$HOME/.cargo/bin:$PATH\"' >> ~/.zshrc

         2. Reload your shell:
            source ~/.zshrc

         3. Verify UV is available:
            which uv

         Would you like me to retry the installation?"

User: "Yes, retry"

Claude: "Retrying installation...
         ✓ UV is now in PATH
         ✓ Installing MoAI-ADK...
         ✓ Installation successful!"
```

#### Example 3: Korean Language Request

```
User: "MoAI-ADK 설치하고 한국어 NLP 기능도 켜줘"

Claude: "한국어로 MoAI-ADK를 설치하겠습니다.
         (I'll install MoAI-ADK with Korean support.)

         설치 중... (Installing...)
         [1/5] 디렉토리 생성... ✓
         [2/5] UV 패키지 관리자 설치... ✓
         [3/5] MoAI-ADK 설치... ✓
         [4/5] 나눔고딕 폰트 설치... ✓
         [5/5] 한국어 NLP 설정... ✓

         설치 완료! (Installation complete!)

         테스트: (Test:)
         python3 -c 'import moai_adk; print(moai_adk.__version__)'"
```

#### Example 4: Upgrade Scenario

```
User: "Install MoAI-ADK"

Claude: "I found an existing MoAI-ADK installation:

         Current version: 0.9.5
         Latest version: 1.0.0

         This is an upgrade. Your current configuration will be preserved.

         Changes in v1.0.0:
         - Enhanced Korean NLP
         - Improved agent coordination
         - New mixture strategies

         Proceed with upgrade? (Y/n)"

User: "yes"

Claude: "Upgrading...
         ✓ Backing up current installation
         ✓ Installing MoAI-ADK v1.0.0
         ✓ Migrating configuration
         ✓ Upgrade complete!

         Your settings from ~/.moai/config/settings.json have been preserved."
```

## How It Works

### Architecture

```
User Request
    │
    ▼
┌─────────────────────────────────┐
│  Claude Code Skill Detection    │
│  - Recognizes trigger phrases   │
│  - Loads context from .claude/  │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│  System Analysis                │
│  - Detect OS & architecture     │
│  - Check Python version         │
│  - Detect locale (Korean?)      │
│  - Check existing installation  │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│  Intelligent Decision Making    │
│  - Auto-detect Korean need      │
│  - Choose installation strategy │
│  - Plan error recovery          │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│  Installation Execution         │
│  - Use UV CLI installer         │
│  - Monitor progress             │
│  - Handle errors autonomously   │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│  Verification & Feedback        │
│  - Test import                  │
│  - Verify Korean support        │
│  - Provide next steps           │
└─────────────────────────────────┘
```

### Korean Auto-Detection Logic

```python
def detect_korean_preference(context):
    signals = []

    # 1. System locale
    if os.environ.get('LANG', '').startswith('ko_'):
        signals.append(('locale', 1.0))

    # 2. User's conversation language
    if detect_korean_in_message(user_message):
        signals.append(('message', 1.0))

    # 3. Existing Korean files in project
    if has_korean_files_in_project():
        signals.append(('project', 0.7))

    # 4. Previous Claude interactions
    if claude_memory_has_korean_preference():
        signals.append(('memory', 0.8))

    # 5. Keyboard layout
    if get_keyboard_layout() == 'Korean':
        signals.append(('keyboard', 0.6))

    # Calculate confidence
    confidence = sum(weight for _, weight in signals) / len(signals)

    # Auto-install Korean if confidence > 0.7
    return confidence > 0.7
```

## Benefits Over Traditional Installers

### 1. No Command Memorization

**Traditional:**
```bash
# User must remember:
./install.sh --korean --verbose --force --skip-python
```

**Claude Skill:**
```
# User just asks naturally:
"Reinstall MoAI-ADK with Korean support, and show me what's happening"
```

### 2. Context-Aware

Claude understands your environment:

- Existing installations
- System capabilities
- User preferences (from memory)
- Project requirements
- Language preferences

### 3. Conversational Debugging

**Traditional:**
```bash
$ ./install.sh
Error: Python 3.9 < 3.11
# User must interpret error and Google solution
```

**Claude Skill:**
```
User: "Install MoAI-ADK"

Claude: "I see Python 3.9, but we need 3.11+.

         I can help you install Python 3.11:

         Option 1 (Recommended): Homebrew
           brew install python@3.11

         Option 2: pyenv (for managing multiple versions)
           brew install pyenv
           pyenv install 3.11.5

         Option 3: Official installer
           Download from python.org

         Which would you prefer?"
```

### 4. Adaptive Installation

Claude adapts to your specific situation:

- **Developer environment**: Installs in virtual environment
- **System-wide**: Uses system Python
- **Multiple Python versions**: Asks which to use
- **Korean user**: Auto-includes Korean support
- **English user**: English-only installation

### 5. Memory & Learning

Claude remembers your preferences:

```
First time:
User: "Install MoAI-ADK"
Claude: "Should I include Korean support? (Y/n)"
User: "Yes"

Next time (different project):
User: "Install MoAI-ADK"
Claude: "I remember you prefer Korean support.
         Installing with Nanum fonts and Korean NLP..."
```

## Limitations

### 1. Requires Claude Code

- Cannot be used standalone
- Needs Claude Code CLI installed
- Requires active Claude session

### 2. Internet Dependency

- Needs internet for Claude API
- Cannot work offline
- Requires API credits

### 3. Less Scriptable

- Not suitable for CI/CD
- Cannot be automated in traditional sense
- Requires human interaction

### 4. Debugging Complexity

- Harder to debug Claude's logic
- Cannot inspect intermediate steps easily
- Relies on Claude's interpretation

## When to Use Claude Skill Installer

### Perfect For:

1. **Claude Code Users**
   - Already using Claude for development
   - Prefer conversational interfaces
   - Want seamless integration

2. **First-Time Installers**
   - Don't know command-line options
   - Want guided installation
   - Need help troubleshooting

3. **Korean Language Users**
   - Want automatic Korean detection
   - Prefer bilingual support
   - Need Korean NLP features

4. **Adaptive Installation**
   - Different setups across machines
   - Want Claude to decide best approach
   - Complex environment requirements

### Avoid If:

1. **CI/CD Pipelines**
   - Use Bash installer instead
   - Need non-interactive execution
   - Require reproducible builds

2. **Offline Installation**
   - No internet access
   - Air-gapped environments
   - Use Bash installer

3. **Precise Control**
   - Need exact installation steps
   - Want to customize deeply
   - Use UV CLI or Bash installer

4. **Budget Constraints**
   - Limited Claude API credits
   - High-volume installations
   - Use free installers (Bash/UV CLI)

## Comparison with Other Methods

See [COMPARISON.md](../2_uv_cli/COMPARISON.md) for detailed comparison.

**Quick Summary:**

| Feature | Claude Skill | UV CLI | Bash |
|---------|--------------|--------|------|
| Ease of Use | ★★★★★ | ★★★★★ | ★★★★☆ |
| Automation | ★★★★★ | ★★★★☆ | ★★★☆☆ |
| Korean Auto-detect | ★★★★★ | ★★★★★ | ★★☆☆☆ |
| CI/CD Ready | ★☆☆☆☆ | ★★★☆☆ | ★★★★★ |
| Debugging | ★★☆☆☆ | ★★★★★ | ★★★★★ |
| Offline Use | ★☆☆☆☆ | ★★★☆☆ | ★★★★☆ |

## Next Steps

After setup:

1. **Try a test installation:**
   ```
   "Install MoAI-ADK in a test environment"
   ```

2. **Ask for help:**
   ```
   "Show me how to use MoAI-ADK"
   "What can MoAI-ADK do?"
   ```

3. **Customize:**
   ```
   "Configure MoAI-ADK for Korean NLP"
   "Change the UI font to Malgun Gothic"
   ```

4. **Troubleshoot:**
   ```
   "Why isn't Korean text displaying correctly?"
   "How do I upgrade MoAI-ADK?"
   ```

## Support

For issues with Claude Skill installer:

1. **Ask Claude:**
   ```
   "The MoAI-ADK installation failed. What went wrong?"
   ```

2. **Check Claude Code logs:**
   ```bash
   cat ~/.claude/logs/latest.log
   ```

3. **Fall back to UV CLI:**
   ```bash
   cd apps/2_uv_cli
   uv run installer.py install --korean
   ```

## License

MIT License - See main MoAI-ADK repository.
