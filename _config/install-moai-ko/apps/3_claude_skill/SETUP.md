# Claude Skill Installer Setup Guide

Detailed setup instructions for configuring the MoAI-ADK Claude Skill installer within Claude Code.

## Prerequisites

### Required

1. **Claude Code CLI** installed and configured
   ```bash
   claude --version
   # Should show version 2.0.0+
   ```

2. **Claude API Access**
   - Valid API key configured
   - Active Claude subscription
   - API credits available

3. **Python 3.11+**
   ```bash
   python3 --version
   # Should show 3.11.0 or higher
   ```

### Optional

1. **UV Package Manager** (will be auto-installed)
2. **Korean fonts** (will be auto-installed if needed)
3. **Git** (for version control)

## Installation Methods

### Method 1: Symlink Installation (Recommended)

This method allows updates to propagate automatically.

```bash
# Navigate to Claude Skill directory
cd /Users/rdmtv/Documents/claydev-local/agent-os-v2/moai-adk/_config/install-moai-ko/apps/3_claude_skill

# Create symlink to Claude Code's skills directory
ln -s "$(pwd)/.claude" ~/.claude/skills/moai-installer

# Verify symlink
ls -la ~/.claude/skills/moai-installer
```

**Expected output:**
```
lrwxr-xr-x  1 user  staff  ... ~/.claude/skills/moai-installer -> /path/to/.claude
```

**Benefits:**
- Updates automatically propagate
- Single source of truth
- Easy to maintain

**Drawbacks:**
- Symlink must remain valid
- Moving source directory breaks link

### Method 2: Copy Installation

This method creates an independent copy.

```bash
# Copy to Claude Code's skills directory
cp -r .claude ~/.claude/skills/moai-installer

# Verify copy
ls -la ~/.claude/skills/moai-installer
```

**Benefits:**
- Independent of source location
- More portable
- Won't break if source moves

**Drawbacks:**
- Must manually update
- Duplicate files
- More disk space

### Method 3: Project-Specific Installation

Install skill only for specific projects.

```bash
# Navigate to your project
cd /path/to/your/project

# Create .claude directory if it doesn't exist
mkdir -p .claude/skills

# Copy skill
cp -r /path/to/3_claude_skill/.claude .claude/skills/moai-installer
```

**Benefits:**
- Project isolation
- Version control with project
- No global installation

**Drawbacks:**
- Must install per project
- Duplication across projects

## Directory Structure

After installation, you should have:

```
~/.claude/
├── skills/
│   └── moai-installer/
│       ├── skill.md                    # Main skill definition
│       ├── prompts/
│       │   ├── install.md              # Installation prompt
│       │   ├── verify.md               # Verification prompt
│       │   ├── korean-setup.md         # Korean setup prompt
│       │   └── troubleshoot.md         # Troubleshooting prompt
│       └── config/
│           ├── triggers.json           # Trigger phrases
│           └── settings.json           # Skill settings
```

## Configuration

### 1. Trigger Phrases

Edit `~/.claude/skills/moai-installer/config/triggers.json`:

```json
{
  "install_triggers": [
    "install moai-adk",
    "setup moai-adk",
    "add moai-adk",
    "moai-adk 설치",
    "moai-adk setup"
  ],
  "verify_triggers": [
    "verify moai-adk",
    "check moai-adk",
    "is moai-adk installed",
    "moai-adk 확인"
  ],
  "korean_triggers": [
    "korean support",
    "한국어 지원",
    "korean language",
    "korean fonts"
  ],
  "troubleshoot_triggers": [
    "moai-adk not working",
    "installation failed",
    "help with moai-adk",
    "문제 해결"
  ]
}
```

**Add your own triggers:**
```json
{
  "custom_triggers": [
    "set up mixture of agents",
    "install the ai toolkit",
    "add korean nlp"
  ]
}
```

### 2. Skill Settings

Edit `~/.claude/skills/moai-installer/config/settings.json`:

```json
{
  "skill_name": "moai-installer",
  "version": "1.0.0",
  "auto_detect_korean": true,
  "default_install_location": "~/.moai",
  "use_uv_installer": true,
  "verbose_output": true,
  "korean_detection_threshold": 0.7,
  "supported_languages": ["en", "ko"],
  "fallback_installer": "uv_cli"
}
```

**Configuration options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `auto_detect_korean` | boolean | true | Auto-detect Korean locale |
| `default_install_location` | string | ~/.moai | Installation directory |
| `use_uv_installer` | boolean | true | Use UV CLI installer |
| `verbose_output` | boolean | true | Show detailed output |
| `korean_detection_threshold` | float | 0.7 | Confidence threshold |
| `fallback_installer` | string | uv_cli | Fallback method |

### 3. Korean Auto-Detection

Configure Korean detection in `config/settings.json`:

```json
{
  "korean_detection": {
    "enabled": true,
    "threshold": 0.7,
    "signals": {
      "locale": { "weight": 1.0, "enabled": true },
      "message_language": { "weight": 1.0, "enabled": true },
      "project_files": { "weight": 0.7, "enabled": true },
      "claude_memory": { "weight": 0.8, "enabled": true },
      "keyboard_layout": { "weight": 0.6, "enabled": false }
    },
    "auto_install_fonts": true,
    "auto_configure_nlp": true
  }
}
```

**Signal explanations:**

- **locale** (1.0): System `LANG` environment variable
- **message_language** (1.0): Korean text in user message
- **project_files** (0.7): Existing Korean `.md`, `.txt` files
- **claude_memory** (0.8): Previous Korean preference
- **keyboard_layout** (0.6): Korean keyboard detected

## Activation

### Verify Installation

```bash
# Check if skill is recognized
claude skills list | grep moai-installer

# Should output:
# moai-installer (v1.0.0) - MoAI-ADK Installer
```

### Test Skill Activation

Start a Claude Code session:

```bash
claude
```

Then type a trigger phrase:

```
User: install moai-adk

Claude: I'll help you install MoAI-ADK. Let me check your system first...
```

**Expected behavior:**

1. Claude recognizes trigger phrase
2. Loads skill context from `.claude/`
3. Analyzes system environment
4. Begins installation conversation

## Trigger Phrase Examples

### English Triggers

**Installation:**
- "Install MoAI-ADK"
- "Set up MoAI-ADK"
- "Add MoAI-ADK to this project"
- "I need to install the Mixture of Agents kit"
- "Help me get MoAI-ADK running"

**Verification:**
- "Is MoAI-ADK installed?"
- "Check MoAI-ADK installation"
- "Verify MoAI-ADK setup"
- "Show me MoAI-ADK status"

**Korean Support:**
- "Install MoAI-ADK with Korean support"
- "Add Korean language features"
- "Set up Korean fonts for MoAI-ADK"

**Troubleshooting:**
- "MoAI-ADK isn't working"
- "The installation failed"
- "Help me fix MoAI-ADK"
- "Why can't I import moai_adk?"

### Korean Triggers

**설치 (Installation):**
- "MoAI-ADK 설치해줘"
- "MoAI-ADK 설정해줘"
- "프로젝트에 MoAI-ADK 추가해줘"
- "Mixture of Agents 설치 도와줘"

**확인 (Verification):**
- "MoAI-ADK 설치됐어?"
- "MoAI-ADK 상태 확인해줘"
- "설치 확인해줘"

**한국어 지원 (Korean Support):**
- "MoAI-ADK 한국어로 설정해줘"
- "한국어 폰트 추가해줘"
- "한국어 NLP 기능 켜줘"

**문제 해결 (Troubleshooting):**
- "MoAI-ADK가 안 돼"
- "설치 실패했어"
- "MoAI-ADK 문제 해결해줘"

### Mixed Language Triggers

- "Install MoAI-ADK 한국어 support"
- "MoAI-ADK setup with Korean language"
- "한국어 fonts for MoAI-ADK"

## Customization

### Add Custom Prompts

Create `~/.claude/skills/moai-installer/prompts/custom-install.md`:

```markdown
# Custom MoAI-ADK Installation

When user requests MoAI-ADK installation with custom requirements:

1. Analyze custom requirements
2. Check for conflicts with existing setup
3. Propose installation plan
4. Execute with user confirmation

## Example Custom Requirements:
- Specific Python version
- Virtual environment isolation
- Custom installation directory
- Additional packages
- Development mode installation
```

### Add Installation Variants

Create `~/.claude/skills/moai-installer/prompts/dev-install.md`:

```markdown
# Development Installation

For developers who want to contribute to MoAI-ADK:

1. Clone repository
2. Install in editable mode
3. Install development dependencies
4. Set up pre-commit hooks
5. Configure testing environment

Commands:
```bash
git clone https://github.com/your-org/moai-adk.git
cd moai-adk
uv pip install -e ".[dev]"
pre-commit install
```
```

## Integration with Existing Projects

### Claude Code Projects

If your project already has `.claude/` directory:

```bash
# Navigate to project
cd /path/to/your/project

# Merge skill into existing .claude
cp -r /path/to/3_claude_skill/.claude/* .claude/

# Or create skills subdirectory
mkdir -p .claude/skills
cp -r /path/to/3_claude_skill/.claude .claude/skills/moai-installer
```

### Git Integration

Add to `.gitignore`:

```gitignore
# MoAI-ADK installation
.moai/
*.log

# But track the skill definition
!.claude/skills/moai-installer/
```

Commit skill to version control:

```bash
git add .claude/skills/moai-installer/
git commit -m "Add MoAI-ADK Claude Skill installer"
```

## Troubleshooting Setup

### Issue: Skill Not Recognized

**Check skill directory:**
```bash
ls -la ~/.claude/skills/moai-installer

# Should show:
# skill.md
# prompts/
# config/
```

**Verify Claude Code configuration:**
```bash
claude config show | grep skills_directory
```

**Reload Claude Code:**
```bash
claude reload
```

### Issue: Triggers Not Working

**Test trigger manually:**
```bash
claude --skill moai-installer "install moai-adk"
```

**Check trigger configuration:**
```bash
cat ~/.claude/skills/moai-installer/config/triggers.json
```

**Verify JSON syntax:**
```bash
python3 -m json.tool ~/.claude/skills/moai-installer/config/triggers.json
```

### Issue: Korean Auto-Detection Not Working

**Check locale settings:**
```bash
locale
echo $LANG
```

**Verify detection settings:**
```bash
cat ~/.claude/skills/moai-installer/config/settings.json | grep korean_detection -A 10
```

**Test detection manually:**
```python
import os
import json

# Check locale
locale = os.environ.get('LANG', '')
print(f"Locale: {locale}")
print(f"Starts with 'ko_': {locale.startswith('ko_')}")
```

### Issue: Symlink Broken

**Check symlink status:**
```bash
ls -la ~/.claude/skills/moai-installer

# If broken, shows:
# ... -> /path/that/doesnt/exist (in red)
```

**Fix symlink:**
```bash
# Remove broken symlink
rm ~/.claude/skills/moai-installer

# Recreate with correct path
ln -s /correct/path/.claude ~/.claude/skills/moai-installer
```

### Issue: Permission Denied

**Check permissions:**
```bash
ls -la ~/.claude/skills/
ls -la ~/.claude/skills/moai-installer/
```

**Fix permissions:**
```bash
chmod -R 755 ~/.claude/skills/moai-installer
```

## Testing the Setup

### Test 1: Basic Recognition

```bash
claude

# In Claude session:
User: install moai-adk

# Expected: Claude recognizes and responds
```

### Test 2: Korean Detection

```bash
# Set Korean locale temporarily
export LANG=ko_KR.UTF-8

claude

User: MoAI-ADK 설치해줘

# Expected: Claude responds in Korean or acknowledges Korean
```

### Test 3: Skill Status

```bash
claude skills status moai-installer

# Expected output:
# moai-installer: Active
# Version: 1.0.0
# Triggers: 15 configured
# Last used: Never / [timestamp]
```

## Best Practices

### 1. Version Control

Track skill configuration with your project:

```bash
# .gitignore
.moai/
*.log

# But track
.claude/skills/moai-installer/
```

### 2. Team Setup

Share skill with team:

```bash
# In project README
## MoAI-ADK Setup

To install MoAI-ADK via Claude:

1. Ensure Claude Code is installed
2. The skill is included in `.claude/skills/moai-installer/`
3. Type: "install moai-adk"
```

### 3. Documentation

Document custom triggers:

```markdown
## Custom Claude Triggers

- "set up moai locally" → Installs MoAI-ADK
- "korean nlp setup" → Enables Korean features
- "check moai" → Verifies installation
```

### 4. Backup

Backup skill configuration:

```bash
# Create backup
tar -czf moai-skill-backup.tar.gz ~/.claude/skills/moai-installer/

# Restore backup
tar -xzf moai-skill-backup.tar.gz -C ~/
```

## Uninstallation

### Remove Skill

```bash
# If symlinked
rm ~/.claude/skills/moai-installer

# If copied
rm -rf ~/.claude/skills/moai-installer
```

### Verify Removal

```bash
claude skills list | grep moai-installer
# Should return nothing
```

## Next Steps

After successful setup:

1. **Read [README.md](./README.md)** for usage examples
2. **Try test installation** in a safe environment
3. **Customize triggers** for your workflow
4. **Review [COMPLETION.md](./COMPLETION.md)** for post-install guide

## Support

For setup issues:

1. Check Claude Code logs: `~/.claude/logs/`
2. Verify skill files are present
3. Test with simple trigger phrase
4. Fall back to UV CLI installer if needed

## License

MIT License - See main MoAI-ADK repository.
