# MoAI-ADK Installer Skill

Complete installation and configuration toolkit for MoAI-ADK with Korean language support.

## Quick Start

```bash
# Check system requirements
uv run scripts/check_system.py

# Install MoAI-ADK
uv run scripts/install_moai.py

# Validate installation
uv run scripts/validate_install.py
```

## Scripts

### 1. check_system.py (~350 lines)
Validates system requirements before installation.

**Checks**:
- Python 3.11-3.14
- uv package manager
- git version control
- npx (Node.js)
- Disk space (2GB minimum)
- Terminal (Ghostty recommended)

**Usage**:
```bash
uv run scripts/check_system.py
uv run scripts/check_system.py --verbose
uv run scripts/check_system.py --json
```

### 2. install_moai.py (~450 lines)
Installs and configures MoAI-ADK.

**Steps**:
1. Install uv (if missing)
2. Install moai-adk via uv tool
3. Initialize project structure
4. Configure `.moai/` directory
5. Verify installation

**Usage**:
```bash
uv run scripts/install_moai.py
uv run scripts/install_moai.py --verbose
uv run scripts/install_moai.py --korean
uv run scripts/install_moai.py --json
```

### 3. configure_korean.py (~400 lines)
Configures Korean language support.

**Steps**:
1. Install D2Coding font (macOS via Homebrew)
2. Configure Ghostty terminal
3. Set up Korean locale
4. Test Korean rendering
5. Update MoAI config

**Usage**:
```bash
uv run scripts/configure_korean.py
uv run scripts/configure_korean.py --auto
uv run scripts/configure_korean.py --verbose
uv run scripts/configure_korean.py --json
```

### 4. validate_install.py (~550 lines)
Comprehensive 10-point installation validation.

**Validation Checklist**:
1. MoAI-ADK version
2. 26 agents available
3. `/moai:0` command
4. `/moai:1` command
5. `/moai:2` command
6. `/moai:3` command
7. `/moai:4` command
8. Project structure
9. Configuration files
10. Korean fonts (if enabled)

**Usage**:
```bash
uv run scripts/validate_install.py
uv run scripts/validate_install.py --verbose
uv run scripts/validate_install.py --comprehensive
uv run scripts/validate_install.py --json
```

### 5. test_korean_fonts.py (~380 lines)
Tests Korean font rendering and configuration.

**Tests**:
1. Korean character rendering
2. D2Coding font installation
3. Ghostty configuration
4. CJK character display
5. UTF-8 encoding

**Usage**:
```bash
uv run scripts/test_korean_fonts.py
uv run scripts/test_korean_fonts.py --verbose
uv run scripts/test_korean_fonts.py --json
```

### 6. test_portability.py (~450 lines)
Tests installation portability and isolation.

**Tests**:
1. Virtual environment isolation
2. Cross-platform compatibility
3. Korean font availability
4. UV tool portability
5. Configuration file portability
6. Dependency resolution

**Usage**:
```bash
uv run scripts/test_portability.py
uv run scripts/test_portability.py --verbose
uv run scripts/test_portability.py --json
```

## Installation Workflows

### Basic Installation

```bash
# 1. Check system
uv run scripts/check_system.py --verbose

# 2. Install MoAI-ADK
uv run scripts/install_moai.py --verbose

# 3. Validate
uv run scripts/validate_install.py --verbose
```

### Installation with Korean Support

```bash
# 1. Check system
uv run scripts/check_system.py

# 2. Install with Korean
uv run scripts/install_moai.py --korean

# 3. Configure Korean
uv run scripts/configure_korean.py --auto

# 4. Test fonts
uv run scripts/test_korean_fonts.py --verbose

# 5. Validate
uv run scripts/validate_install.py --comprehensive
```

### CI/CD Installation

```bash
# All in JSON mode for automation
uv run scripts/check_system.py --json > check.json
uv run scripts/install_moai.py --json > install.json
uv run scripts/validate_install.py --json > validate.json
uv run scripts/test_portability.py --json > portability.json
```

## Features

### PEP 723 Inline Dependencies

All scripts use PEP 723 format:

```python
#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11,<3.15"
# dependencies = [
#     "click>=8.1.0",
# ]
# ///
```

**Benefits**:
- No separate requirements.txt
- Dependencies isolated per script
- Automatic environment management
- Portable across systems

### Dual Output Modes

Each script supports two output modes:

1. **Human-readable** (default):
   - Formatted tables
   - Color-coded status
   - Progress indicators
   - Visual feedback

2. **JSON** (--json flag):
   - Machine-readable
   - Structured data
   - Automation-friendly
   - Consistent format

### Executable Flags

All scripts support:
- `--help` / `-h` - Show help message
- `--verbose` / `-v` - Detailed output
- `--json` - JSON output format

Additional script-specific flags:
- `--korean` / `-k` (install_moai.py) - Enable Korean support
- `--auto` / `-a` (configure_korean.py) - Skip confirmations
- `--comprehensive` / `-c` (validate_install.py) - Extended validation

## Directory Structure

After installation:

```
.moai/
├── agents/          # Agent definitions
├── commands/        # Custom commands
├── config/
│   └── moai.json   # Main configuration
├── logs/            # Application logs
├── cache/           # Temporary cache
├── README.md        # Project documentation
└── .gitignore       # Git ignore rules
```

## Platform Support

### macOS (Darwin)
- ✅ Full support
- ✅ D2Coding font via Homebrew
- ✅ Ghostty terminal
- ✅ All validation tests

### Linux
- ✅ Core support
- ⚠️ Manual D2Coding font installation
- ⚠️ Manual Ghostty installation
- ✅ All validation tests

## Requirements

- **Python**: 3.11, 3.12, 3.13, or 3.14
- **uv**: Latest version (auto-installed if missing)
- **git**: Any recent version
- **npx**: For MoAI-ADK commands
- **Disk space**: 2GB minimum
- **Terminal**: Ghostty recommended for Korean support

## Troubleshooting

### "uv not found"

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.cargo/bin:$PATH"
```

### "moai-adk command not available"

```bash
# Use via uv tool run
uv tool run moai-adk --version

# Or add to PATH
export PATH="$HOME/.local/share/uv/tools:$PATH"
```

### "Korean fonts not rendering"

```bash
# macOS
brew install --cask font-d2coding
brew install ghostty

# Linux
# Download from https://github.com/naver/d2codingfont
fc-cache -fv
```

### Low validation score

```bash
# Comprehensive validation
uv run scripts/validate_install.py --comprehensive --verbose

# Re-install if needed
uv run scripts/install_moai.py --verbose

# Re-validate
uv run scripts/validate_install.py --comprehensive
```

## Output Format

All scripts return consistent JSON structure:

```json
{
  "overall_status": "SUCCESS|FAILED|PARTIAL",
  "score": 10,
  "max_score": 10,
  "percentage": 100.0,
  "errors": [],
  "warnings": [],
  "results": {
    "step_name": {
      "status": "passed|failed|warning|skipped",
      "details": {}
    }
  }
}
```

## Best Practices

1. **Check before install**: Always run `check_system.py` first
2. **Use verbose mode**: Get detailed feedback
3. **Validate after install**: Confirm success with `validate_install.py`
4. **Test portability**: Before deploying to other systems
5. **JSON in CI/CD**: Use `--json` flag for automation
6. **Korean support**: Use `--korean` flag if needed

## Examples

### Check system requirements

```bash
$ uv run scripts/check_system.py --verbose
🔍 Checking system requirements for MoAI-ADK...

✓ Python 3.11.5 detected
✓ uv 0.5.9 detected
✓ git 2.42.0 detected
✓ npx detected with Node v20.10.0
✓ 150.23GB disk space available
✓ Ghostty terminal detected

Overall Status: READY
Checks Passed: 7/7
```

### Install MoAI-ADK

```bash
$ uv run scripts/install_moai.py --verbose
Installing MoAI-ADK...

✓ uv already installed
✓ MoAI-ADK installed: v1.0.0
✓ Created 5 directories
✓ Created 3 configuration files
✓ MoAI-ADK is available: 1.0.0

Overall Status: SUCCESS
Steps Completed: 5/5
```

### Validate installation

```bash
$ uv run scripts/validate_install.py --comprehensive
🔍 Running MoAI-ADK installation validation...

✓ Check 1: MoAI-ADK Version
✓ Check 2: Available Agents
✓ Check 3: MoAI Command Level 0
✓ Check 4: MoAI Command Level 1
✓ Check 5: MoAI Command Level 2
✓ Check 6: MoAI Command Level 3
✓ Check 7: MoAI Command Level 4
✓ Check 8: Project Structure
✓ Check 9: Configuration Files
✓ Check 10: Korean Font Support

Overall Status: EXCELLENT
Score: 10/10 (100.0%)
```

## Documentation

For complete documentation, see:
- [SKILL.md](./SKILL.md) - Detailed skill documentation with progressive disclosure
- [scripts/](./scripts/) - Individual script source code

## License

MIT License - See project root for details

## Support

For issues or questions:
1. Review validation output
2. Check troubleshooting section
3. See MoAI-ADK documentation: https://moai-adk.dev
