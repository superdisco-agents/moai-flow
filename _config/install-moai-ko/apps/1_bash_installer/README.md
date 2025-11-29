# MoAI-ADK Bash Installer

Complete installation script for MoAI-ADK (Mixture of Agents AI Development Kit) with comprehensive Korean language support.

## Overview

The Bash installer provides a robust, production-ready installation experience with:

- **Python 3.11+ detection and validation**
- **UV package manager installation**
- **MoAI-ADK automated setup**
- **Korean language fonts and locale configuration**
- **Comprehensive error handling and logging**
- **Dry-run mode for testing**
- **Force reinstall capabilities**

## Quick Start

### Basic Installation

```bash
# Make the script executable
chmod +x install.sh

# Run installation
./install.sh
```

### Installation with Korean Support

```bash
# Install with Korean fonts and locale
./install.sh --korean
```

## Command Line Options

### Core Flags

| Flag | Long Form | Description |
|------|-----------|-------------|
| `-k` | `--korean` | Install Korean language fonts and configure locale |
| `-s` | `--skip-python` | Skip Python version check (use with caution) |
| `-u` | `--skip-uv` | Skip UV package manager installation |
| `-v` | `--verbose` | Enable detailed debug output |
| `-d` | `--dry-run` | Preview installation without making changes |
| `-f` | `--force` | Force reinstallation of existing packages |
| `-h` | `--help` | Display usage information |

### Flag Combinations

```bash
# Verbose installation with Korean support
./install.sh --korean --verbose

# Dry run to preview changes
./install.sh --dry-run --verbose

# Force complete reinstallation
./install.sh --force --korean

# Quick install (skip checks)
./install.sh --skip-python --skip-uv
```

## Features

### 1. System Compatibility Checks

The installer automatically detects and validates:

- **Operating System**: macOS, Linux, Windows (WSL/Cygwin)
- **Architecture**: x86_64, ARM64
- **Python Version**: 3.11+ required
- **Disk Space**: 500MB minimum recommended
- **Network Connectivity**: PyPI access verification

### 2. UV Package Manager

UV is the modern, fast Python package installer:

```bash
# Automatically installs UV from official source
curl -LsSf https://astral.sh/uv/install.sh | sh

# Adds UV to PATH in shell configuration
export PATH="$HOME/.cargo/bin:$PATH"
```

**Benefits:**
- 10-100x faster than pip
- Better dependency resolution
- Compatible with existing Python tools

### 3. Korean Language Support

When using `--korean` flag:

**macOS:**
```bash
# Installs Nanum fonts via Homebrew
brew install --cask font-nanum
brew install --cask font-nanum-gothic-coding
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install fonts-nanum fonts-nanum-coding
```

**Linux (Fedora/RHEL):**
```bash
sudo yum install google-noto-sans-cjk-ttc-fonts
```

**Linux (Arch):**
```bash
sudo pacman -S noto-fonts-cjk
```

**Configuration:**
Creates `~/.moai/config/settings.json`:
```json
{
  "language": "ko_KR",
  "locale": "ko_KR.UTF-8",
  "encoding": "UTF-8",
  "ui": {
    "font_family": "Nanum Gothic",
    "font_size": 14
  },
  "features": {
    "korean_nlp": true,
    "korean_tokenizer": true
  }
}
```

### 4. Installation Directory Structure

```
~/.moai/
├── models/           # Model storage
├── cache/            # Runtime cache
├── logs/             # Installation and runtime logs
│   └── install.log
├── config/           # Configuration files
│   └── settings.json
└── activate.sh       # Environment activation script
```

### 5. Logging System

All operations are logged to `~/.moai/logs/install.log`:

```
[2025-01-15 10:30:45] [INFO] Starting MoAI-ADK installation...
[2025-01-15 10:30:46] [SUCCESS] Python 3.11.5 is installed
[2025-01-15 10:30:50] [SUCCESS] UV installed successfully
[2025-01-15 10:31:20] [SUCCESS] MoAI-ADK installed successfully
```

### 6. Error Handling

The script handles common errors gracefully:

- **Missing Python**: Provides download link
- **Old Python version**: Shows upgrade instructions
- **Network issues**: Offers offline alternatives
- **Low disk space**: Warns and asks for confirmation
- **UV installation failure**: Provides manual installation steps

## Usage Examples

### Example 1: Development Installation

```bash
# Full installation with Korean support and verbose output
./install.sh --korean --verbose

# Verify installation
python3 -c "import moai_adk; print(moai_adk.__version__)"
```

### Example 2: CI/CD Pipeline

```bash
# Non-interactive installation
./install.sh --skip-python --force

# Run tests
python3 -m pytest tests/
```

### Example 3: Testing Changes

```bash
# Dry run to see what would happen
./install.sh --korean --dry-run --verbose

# Review proposed changes, then run for real
./install.sh --korean
```

### Example 4: Upgrade Existing Installation

```bash
# Force reinstall to upgrade
./install.sh --force

# Or with Korean support
./install.sh --force --korean
```

## Post-Installation

### Activate MoAI Environment

```bash
# Source activation script
source ~/.moai/activate.sh

# Verify environment variables
echo $MOAI_CONFIG_DIR
echo $MOAI_CACHE_DIR
```

### Verify Installation

```bash
# Check Python import
python3 -c "import moai_adk; print(f'Version: {moai_adk.__version__}')"

# Run MoAI-ADK CLI
python3 -m moai_adk --help

# Check configuration
cat ~/.moai/config/settings.json
```

### Test Korean Support

```python
import moai_adk
from moai_adk import config

# Load Korean configuration
cfg = config.load_settings()
print(f"Language: {cfg['language']}")
print(f"Locale: {cfg['locale']}")
print(f"Korean NLP: {cfg['features']['korean_nlp']}")
```

## Troubleshooting

### Issue: Python Version Too Old

```bash
# Error: Python version 3.9.0 is below minimum required version 3.11

# Solution: Install Python 3.11+
brew install python@3.11  # macOS
sudo apt-get install python3.11  # Ubuntu/Debian
```

### Issue: UV Not Found After Installation

```bash
# Error: UV is not installed or not in PATH

# Solution: Reload shell configuration
source ~/.bashrc  # or ~/.zshrc

# Or manually add to PATH
export PATH="$HOME/.cargo/bin:$PATH"
```

### Issue: Korean Fonts Not Displaying

```bash
# macOS: Install Homebrew first
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Then run installer with Korean flag
./install.sh --korean
```

### Issue: Network Connectivity Problems

```bash
# Test PyPI connectivity
curl -I https://pypi.org

# If offline, download UV manually
curl -LsSf https://astral.sh/uv/install.sh -o uv-install.sh
bash uv-install.sh

# Then skip UV installation
./install.sh --skip-uv
```

### Issue: Permission Denied

```bash
# Error: Permission denied: install.sh

# Solution: Make executable
chmod +x install.sh

# Run installation
./install.sh
```

### Issue: Low Disk Space

```bash
# Warning: Low disk space: 300MB available

# Solution: Free up space
# Clean brew cache (macOS)
brew cleanup

# Clean apt cache (Linux)
sudo apt-get clean

# Remove old Python packages
uv pip list --outdated
uv pip uninstall <package>
```

## Advanced Configuration

### Custom Installation Directory

Edit the script to change `MOAI_CONFIG_DIR`:

```bash
# Default
MOAI_CONFIG_DIR="${HOME}/.moai"

# Custom
MOAI_CONFIG_DIR="/opt/moai"
```

### Skip Confirmation Prompts

For automated installations:

```bash
# Use yes command
yes | ./install.sh --korean
```

### Custom Python Binary

```bash
# Set Python executable
export PYTHON=python3.11

# Run installation
./install.sh
```

## Uninstallation

```bash
# Remove UV package
uv pip uninstall moai-adk

# Remove configuration directory
rm -rf ~/.moai

# Remove UV (optional)
rm -rf ~/.cargo/bin/uv

# Remove shell configuration entry
# Edit ~/.bashrc or ~/.zshrc and remove:
# export PATH="$HOME/.cargo/bin:$PATH"
```

## Script Architecture

### Key Functions

| Function | Purpose |
|----------|---------|
| `check_python_version()` | Validate Python 3.11+ |
| `install_uv()` | Download and install UV |
| `install_moai_adk()` | Install MoAI-ADK package |
| `install_korean_fonts_macos()` | Korean fonts for macOS |
| `install_korean_fonts_linux()` | Korean fonts for Linux |
| `configure_korean_locale()` | Create Korean settings |
| `verify_installation()` | Post-install validation |

### Error Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |

### Logging Levels

| Level | Color | Purpose |
|-------|-------|---------|
| ERROR | Red | Fatal errors |
| SUCCESS | Green | Successful operations |
| WARNING | Yellow | Non-fatal issues |
| INFO | Blue | General information |
| DEBUG | Cyan | Verbose details |

## Comparison with Other Installers

| Feature | Bash Installer | UV CLI | Claude Skill |
|---------|---------------|--------|--------------|
| Ease of Use | ★★★★☆ | ★★★★★ | ★★★★★ |
| Customization | ★★★★★ | ★★★★☆ | ★★☆☆☆ |
| Korean Support | ★★★★★ | ★★★★★ | ★★★★★ |
| Automation | ★★★☆☆ | ★★★★☆ | ★★★★★ |
| Debugging | ★★★★★ | ★★★★☆ | ★★☆☆☆ |
| Portability | ★★★★★ | ★★★☆☆ | ★☆☆☆☆ |

## Contributing

To improve this installer:

1. **Add OS Support**: Extend `detect_os()` function
2. **New Features**: Add flags in `parse_arguments()`
3. **Better Validation**: Enhance check functions
4. **Localization**: Add more language support

## License

MIT License - See main MoAI-ADK repository for details.

## Support

- **Documentation**: See main README.md
- **Issues**: Report bugs in installer behavior
- **Logs**: Check `~/.moai/logs/install.log` for debugging

## Version History

- **1.0.0** (2025-01-29): Initial release
  - Python 3.11+ validation
  - UV package manager integration
  - Korean language support
  - Comprehensive logging
  - Dry-run mode
