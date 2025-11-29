---
name: moai-adk-installer
description: MoAI-ADK installation and configuration toolkit with Korean language support
version: 1.0.0
author: MoAI Team
category: installation
tags: [moai-adk, installation, korean, uv, portability, validation]
---

# MoAI-ADK Installer Skill

Complete installation and configuration toolkit for MoAI-ADK with Korean language support.

## Quick Start

```bash
# Check system requirements
uv run scripts/check_system.py

# Install MoAI-ADK
uv run scripts/install_moai.py

# Configure Korean support (optional)
uv run scripts/configure_korean.py

# Validate installation
uv run scripts/validate_install.py
```

## Progressive Disclosure

### Level 1: Basic Installation

**Goal**: Get MoAI-ADK running quickly

**Scripts**:
- `check_system.py` - Verify system requirements
- `install_moai.py` - Install MoAI-ADK

**Example**:
```bash
uv run scripts/check_system.py --verbose
uv run scripts/install_moai.py --verbose
```

### Level 2: Korean Language Support

**Goal**: Enable Korean font rendering and language support

**Scripts**:
- `configure_korean.py` - Configure Korean fonts and locale
- `test_korean_fonts.py` - Test Korean rendering

**Example**:
```bash
uv run scripts/configure_korean.py --auto
uv run scripts/test_korean_fonts.py --verbose
```

### Level 3: Validation & Testing

**Goal**: Comprehensive validation and portability testing

**Scripts**:
- `validate_install.py` - 10-point installation validation
- `test_portability.py` - 6-point portability testing

**Example**:
```bash
uv run scripts/validate_install.py --comprehensive
uv run scripts/test_portability.py --verbose
```

## Scripts Overview

### 1. check_system.py (~350 lines)

**Purpose**: Validate system requirements before installation

**Checks**:
- Python 3.11-3.14 version
- uv package manager
- git version control
- npx (Node.js)
- Disk space (2GB minimum)
- Terminal (Ghostty recommended)

**Flags**:
- `--help` - Show help message
- `--verbose` - Detailed output
- `--json` - JSON output format

**Example**:
```bash
# Basic check
uv run scripts/check_system.py

# Verbose with details
uv run scripts/check_system.py --verbose

# JSON output for automation
uv run scripts/check_system.py --json
```

**Output Modes**:
- Human-readable (default): Formatted table with status indicators
- JSON: Machine-readable structured data

### 2. install_moai.py (~450 lines)

**Purpose**: Install and configure MoAI-ADK

**Steps**:
1. Install uv package manager (if missing)
2. Install moai-adk via `uv tool install`
3. Initialize `.moai/` project structure
4. Configure default settings
5. Verify installation

**Flags**:
- `--help` - Show help message
- `--verbose` - Detailed output
- `--json` - JSON output format
- `--korean` - Enable Korean support

**Example**:
```bash
# Standard installation
uv run scripts/install_moai.py

# With Korean support
uv run scripts/install_moai.py --korean --verbose

# JSON output for CI/CD
uv run scripts/install_moai.py --json
```

**Created Structure**:
```
.moai/
├── agents/
├── commands/
├── config/
│   └── moai.json
├── logs/
├── cache/
├── README.md
└── .gitignore
```

### 3. configure_korean.py (~400 lines)

**Purpose**: Configure Korean language support

**Steps**:
1. Install D2Coding font via Homebrew (macOS)
2. Configure Ghostty terminal for Korean
3. Set up UTF-8 locale
4. Test Korean character rendering
5. Update MoAI config

**Flags**:
- `--help` - Show help message
- `--verbose` - Detailed output
- `--json` - JSON output format
- `--auto` - Skip confirmations

**Example**:
```bash
# Interactive configuration
uv run scripts/configure_korean.py

# Automatic mode
uv run scripts/configure_korean.py --auto

# Verbose with details
uv run scripts/configure_korean.py --verbose --auto
```

**Platform Support**:
- macOS: Full support (Homebrew + Ghostty)
- Linux: Manual font installation required

### 4. validate_install.py (~550 lines)

**Purpose**: Comprehensive 10-point installation validation

**Validation Checklist**:
1. ✓ MoAI-ADK version check
2. ✓ Verify 26 agents available
3. ✓ Test `/moai:0` command
4. ✓ Test `/moai:1` command
5. ✓ Test `/moai:2` command
6. ✓ Test `/moai:3` command
7. ✓ Test `/moai:4` command
8. ✓ Verify project structure
9. ✓ Check configuration files
10. ✓ Verify Korean fonts (if configured)

**Flags**:
- `--help` - Show help message
- `--verbose` - Detailed output
- `--json` - JSON output format
- `--comprehensive` - Extended validation

**Example**:
```bash
# Quick validation
uv run scripts/validate_install.py

# Comprehensive validation
uv run scripts/validate_install.py --comprehensive --verbose

# CI/CD validation
uv run scripts/validate_install.py --json
```

**Scoring**:
- 90-100%: EXCELLENT ✅
- 70-89%: GOOD ✓
- 50-69%: FAIR ⚠️
- <50%: POOR ❌

### 5. test_korean_fonts.py (~380 lines)

**Purpose**: Test Korean font rendering and configuration

**Tests**:
1. Korean character rendering (안녕하세요)
2. D2Coding font installation
3. Ghostty terminal configuration
4. CJK character display (Chinese, Japanese, Korean)
5. UTF-8 encoding validation

**Flags**:
- `--help` - Show help message
- `--verbose` - Detailed output with visual tests
- `--json` - JSON output format

**Example**:
```bash
# Basic font test
uv run scripts/test_korean_fonts.py

# Verbose with visual rendering
uv run scripts/test_korean_fonts.py --verbose

# JSON output
uv run scripts/test_korean_fonts.py --json
```

**Visual Test Output**:
```
안녕하세요 (Hello)
MoAI-ADK 한글 지원 (MoAI-ADK Korean Support)
인공지능 개발 도구 (AI Development Tools)
```

### 6. test_portability.py (~450 lines)

**Purpose**: Test installation portability and isolation

**Portability Tests**:
1. Virtual environment isolation
2. Cross-platform compatibility
3. Korean font availability
4. UV tool portability
5. Configuration file portability
6. Dependency resolution (PEP 723)

**Flags**:
- `--help` - Show help message
- `--verbose` - Detailed output
- `--json` - JSON output format

**Example**:
```bash
# Basic portability test
uv run scripts/test_portability.py

# Verbose with platform details
uv run scripts/test_portability.py --verbose

# JSON for analysis
uv run scripts/test_portability.py --json
```

**Platform Info**:
- System: Darwin, Linux, etc.
- Python version: 3.11-3.14
- Machine architecture: x86_64, arm64, etc.

## Usage Patterns

### Pattern 1: First-Time Installation

```bash
# Step 1: Check requirements
uv run scripts/check_system.py --verbose

# Step 2: Install MoAI-ADK
uv run scripts/install_moai.py --verbose

# Step 3: Validate
uv run scripts/validate_install.py --verbose
```

### Pattern 2: Installation with Korean Support

```bash
# Step 1: Check system
uv run scripts/check_system.py

# Step 2: Install with Korean flag
uv run scripts/install_moai.py --korean

# Step 3: Configure Korean
uv run scripts/configure_korean.py --auto

# Step 4: Test fonts
uv run scripts/test_korean_fonts.py --verbose

# Step 5: Validate
uv run scripts/validate_install.py --comprehensive
```

### Pattern 3: CI/CD Automation

```bash
#!/bin/bash
# ci-install.sh

# All checks in JSON mode for parsing
uv run scripts/check_system.py --json > check_results.json
uv run scripts/install_moai.py --json > install_results.json
uv run scripts/validate_install.py --json > validate_results.json
uv run scripts/test_portability.py --json > portability_results.json

# Parse results and fail if needed
if ! grep -q '"overall_status": "SUCCESS"' install_results.json; then
    echo "Installation failed"
    exit 1
fi
```

### Pattern 4: Troubleshooting

```bash
# Check what's wrong
uv run scripts/validate_install.py --comprehensive --verbose

# Test specific components
uv run scripts/test_korean_fonts.py --verbose
uv run scripts/test_portability.py --verbose

# Re-configure if needed
uv run scripts/configure_korean.py --auto
```

## Technical Details

### PEP 723 Inline Dependencies

All scripts use PEP 723 format for inline dependencies:

```python
#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11,<3.15"
# dependencies = [
#     "click>=8.1.0",
#     "rich>=13.0.0",  # For colored output
# ]
# ///
```

**Benefits**:
- No separate requirements.txt needed
- Dependencies isolated per script
- Automatic environment management via uv
- Portable across systems

### Beyond-MCP Context Efficiency

Scripts follow beyond-MCP principles:
- **Dual output modes**: Human-readable + JSON
- **Structured data**: Consistent result format
- **Error handling**: Detailed error messages
- **Idempotency**: Safe to run multiple times
- **Self-contained**: No external config needed

### Output Format Standard

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

## Platform Support

### macOS (Darwin)

**Fully Supported**:
- ✅ uv installation via curl
- ✅ D2Coding font via Homebrew
- ✅ Ghostty terminal configuration
- ✅ All validation tests

**Requirements**:
- macOS 11.0+
- Homebrew (recommended)
- Python 3.11-3.14

### Linux

**Supported**:
- ✅ uv installation via curl
- ⚠️ D2Coding font (manual installation)
- ⚠️ Ghostty (may require manual install)
- ✅ All validation tests

**Requirements**:
- Ubuntu 20.04+, Debian 11+, or equivalent
- Python 3.11-3.14
- fontconfig (for font management)

## Troubleshooting

### Issue: "uv not found"

**Solution**:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.cargo/bin:$PATH"
```

### Issue: "moai-adk command not available"

**Solution**:
```bash
# Try via uv tool run
uv tool run moai-adk --version

# Or add to PATH
export PATH="$HOME/.local/share/uv/tools:$PATH"
```

### Issue: "Korean fonts not rendering"

**Solution**:
```bash
# macOS
brew install --cask font-d2coding
brew install ghostty

# Linux
# Download from https://github.com/naver/d2codingfont
# Extract and install to ~/.fonts/
fc-cache -fv
```

### Issue: "Validation score is low"

**Solution**:
```bash
# Run comprehensive validation to see details
uv run scripts/validate_install.py --comprehensive --verbose

# Fix identified issues
uv run scripts/install_moai.py --verbose
uv run scripts/configure_korean.py --auto

# Re-validate
uv run scripts/validate_install.py --comprehensive
```

## Best Practices

1. **Always check system first**: Run `check_system.py` before installation
2. **Use verbose mode**: Get detailed feedback during installation
3. **Validate after install**: Run `validate_install.py` to confirm success
4. **Test portability**: Run `test_portability.py` before deploying to other systems
5. **Enable Korean if needed**: Use `--korean` flag during installation
6. **Use JSON in automation**: Parse JSON output in CI/CD pipelines
7. **Check logs**: Review `.moai/logs/` for detailed error messages

## Environment Variables

Optional environment variables for customization:

```bash
# Skip interactive prompts
export MOAI_AUTO_INSTALL=1

# Custom installation directory
export MOAI_INSTALL_DIR=/custom/path

# Enable debug logging
export MOAI_DEBUG=1

# Force Korean configuration
export MOAI_KOREAN=1
```

## Integration Examples

### Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Validate installation before commit
uv run scripts/validate_install.py --json > /tmp/validate.json

if ! grep -q '"overall_status": "EXCELLENT"' /tmp/validate.json; then
    echo "Installation validation failed. Run: uv run scripts/validate_install.py"
    exit 1
fi
```

### GitHub Actions

```yaml
name: MoAI-ADK Installation Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install uv
        run: curl -LsSf https://astral.sh/uv/install.sh | sh

      - name: Check system
        run: uv run scripts/check_system.py --json

      - name: Install MoAI-ADK
        run: uv run scripts/install_moai.py --json

      - name: Validate installation
        run: uv run scripts/validate_install.py --comprehensive --json

      - name: Test portability
        run: uv run scripts/test_portability.py --json
```

## Contributing

To add new scripts to this skill:

1. Follow PEP 723 format for dependencies
2. Implement dual output modes (human + JSON)
3. Add comprehensive error handling
4. Document all flags and options
5. Update this SKILL.md file

## License

MIT License - See project root for details

## Support

For issues or questions:
- Check troubleshooting section above
- Review validation output: `uv run scripts/validate_install.py --verbose`
- Check MoAI-ADK documentation: https://moai-adk.dev
