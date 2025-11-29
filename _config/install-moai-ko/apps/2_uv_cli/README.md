# MoAI-ADK UV CLI Installer (PRIMARY RECOMMENDED)

Modern, interactive CLI installer for MoAI-ADK built with Click and Rich, leveraging UV's PEP 723 single-file script capabilities.

## Overview

The UV CLI installer provides the most user-friendly installation experience with:

- **Click-based command groups** for intuitive command structure
- **Rich terminal output** with colors, tables, and progress bars
- **Interactive prompts** with smart defaults
- **Korean language auto-detection** based on system locale
- **PEP 723 dependency management** (no separate requirements.txt)
- **Comprehensive validation and error handling**
- **Real-time progress indicators**

## Why UV CLI? (Primary Recommendation)

### Advantages Over Other Methods

| Feature | UV CLI | Bash Installer | Claude Skill |
|---------|--------|----------------|--------------|
| User Experience | ★★★★★ | ★★★★☆ | ★★★★★ |
| Visual Feedback | ★★★★★ | ★★★☆☆ | ★★☆☆☆ |
| Error Messages | ★★★★★ | ★★★★☆ | ★★☆☆☆ |
| Interactivity | ★★★★★ | ★★☆☆☆ | ★★★★★ |
| Portability | ★★★★☆ | ★★★★★ | ★☆☆☆☆ |
| Debugging | ★★★★★ | ★★★★★ | ★★☆☆☆ |
| Korean Support | ★★★★★ | ★★★★★ | ★★★★★ |
| Auto-detection | ★★★★★ | ★★☆☆☆ | ★★★★★ |

**Key Differentiators:**
1. **Beautiful UI**: Rich library provides colored output, tables, progress bars
2. **Self-contained**: PEP 723 dependencies embedded in script
3. **Smart defaults**: Auto-detects Korean locale and suggests appropriate options
4. **Interactive**: Confirms actions before proceeding
5. **Comprehensive**: Single tool for install, verify, status, and uninstall

## Quick Start

### Prerequisites

- Python 3.11+
- UV package manager (automatically installed if missing)

### Installation

```bash
# Make executable (optional)
chmod +x installer.py

# Basic installation
uv run installer.py install

# Install with Korean support
uv run installer.py install --korean

# Interactive installation (auto-detects Korean)
uv run installer.py install
```

## Command Reference

### Install Command

```bash
uv run installer.py install [OPTIONS]
```

**Options:**

| Flag | Long Form | Description |
|------|-----------|-------------|
| `-k` | `--korean` | Install Korean language fonts and locale |
| `-s` | `--skip-python` | Skip Python version validation |
| `-u` | `--skip-uv` | Skip UV package manager installation |
| `-f` | `--force` | Force reinstallation of existing packages |
| `-v` | `--verbose` | Enable verbose debug output |

**Examples:**

```bash
# Auto-detect Korean and prompt
uv run installer.py install

# Force install with Korean
uv run installer.py install --korean --force

# Skip UV installation (already installed)
uv run installer.py install --skip-uv

# Verbose installation
uv run installer.py install --verbose
```

### Verify Command

Validate installation integrity:

```bash
uv run installer.py verify
```

**Output:**
```
╭─────────────────── Installation Status ────────────────────╮
│ Component          Status  Details                         │
├────────────────────────────────────────────────────────────┤
│ Config directory   ✓       /home/user/.moai                │
│ UV package manager ✓       Installed                       │
│ MoAI-ADK          ✓       v1.0.0                           │
│ Korean config      ✓       /home/user/.moai/config/...     │
╰────────────────────────────────────────────────────────────╯
```

### Status Command

Display comprehensive system and configuration status:

```bash
uv run installer.py status
```

**Output:**
```
╭────────────── System Information ───────────────╮
│ Os Type          Darwin                          │
│ Os Version       23.0.0                          │
│ Architecture     arm64                           │
│ Python Version   3.11.5                          │
│ Locale           ko_KR.UTF-8                     │
│ Is Korean        True                            │
╰─────────────────────────────────────────────────╯

╭──────────────── Configuration ─────────────────╮
│ {                                               │
│   "language": "ko_KR",                         │
│   "locale": "ko_KR.UTF-8",                     │
│   "ui": {                                       │
│     "font_family": "Nanum Gothic"              │
│   }                                             │
│ }                                               │
╰────────────────────────────────────────────────╯
```

### Setup Korean Command

Configure Korean language support post-installation:

```bash
uv run installer.py setup-korean
```

**What it does:**
1. Installs Korean fonts (platform-specific)
2. Creates Korean locale configuration
3. Enables Korean NLP features
4. Configures UI fonts

### Uninstall Command

Remove MoAI-ADK and optionally remove configuration:

```bash
uv run installer.py uninstall
```

**Interactive prompts:**
```
Are you sure you want to uninstall MoAI-ADK? [y/N]: y
Remove configuration directory /home/user/.moai? [Y/n]: y
```

### Help Command

```bash
uv run installer.py --help
uv run installer.py install --help
```

## Features Deep Dive

### 1. PEP 723 Dependency Management

The installer uses PEP 723 inline script metadata:

```python
# /// script
# dependencies = [
#   "click>=8.1.0",
#   "rich>=13.0.0",
# ]
# ///
```

**Benefits:**
- No separate requirements.txt file
- UV automatically resolves and installs dependencies
- Single-file distribution
- Version-locked dependencies

### 2. Rich Terminal UI

**Features:**
- **Colored output**: Success (green), errors (red), warnings (yellow)
- **Tables**: Structured data display
- **Progress bars**: Real-time installation feedback
- **Panels**: Grouped information with borders
- **Syntax highlighting**: JSON configuration display
- **Markdown rendering**: Documentation in terminal

**Example Output:**
```
╔══════════════════════════════════════════════════╗
║           MoAI-ADK Installer v1.0.0              ║
║     Mixture of Agents AI Development Kit         ║
╚══════════════════════════════════════════════════╝

╭────────────── System Information ──────────────╮
│ Property       │ Value                          │
├────────────────┼────────────────────────────────┤
│ OS             │ Darwin 23.0.0                  │
│ Python         │ 3.11.5                         │
│ Disk Space     │ 45000 MB                       │
│ Korean Detected│ Yes                            │
╰────────────────┴────────────────────────────────╯

Korean locale detected. Install Korean support? [Y/n]:
```

### 3. Interactive Prompts

**Auto-detection Logic:**
```python
# System locale detection
system = get_system_info()

if system.is_korean and not korean:
    if Confirm.ask("Korean locale detected. Install Korean support?", default=True):
        config.install_korean_fonts = True
```

**Confirmation Prompts:**
- Installation confirmation
- Korean language setup
- Uninstallation safety check
- Configuration removal

### 4. System Information Gathering

```python
@dataclass
class SystemInfo:
    os_type: str            # Darwin, Linux, Windows
    os_version: str         # 23.0.0
    architecture: str       # arm64, x86_64
    python_version: str     # 3.11.5
    python_executable: str  # /usr/bin/python3
    disk_space_mb: int      # 45000
    has_uv: bool           # True/False
    uv_version: str        # 0.1.0
    locale: str            # ko_KR.UTF-8
    is_korean: bool        # True/False
```

### 5. Korean Language Auto-Detection

**Detection Methods:**
1. **Locale environment variable**: `LANG=ko_KR.UTF-8`
2. **Locale prefix**: Starts with `ko_`
3. **Country code**: Contains `KR`

**Actions:**
- Automatically suggests Korean setup
- Pre-selects Korean fonts
- Configures Korean NLP features
- Sets Korean UI defaults

### 6. Progress Indicators

```python
with Progress(
    SpinnerColumn(),
    TextColumn("[progress.description]{task.description}"),
    BarColumn(),
    TaskProgressColumn(),
    console=console
) as progress:
    task = progress.add_task("Installing MoAI-ADK...", total=None)
    # Installation code
    progress.update(task, completed=100)
```

**Example:**
```
⠋ Installing MoAI-ADK... ━━━━━━━━━━━━━━━━ 45%
```

### 7. Logging System

All operations logged to `~/.moai/logs/installer.log`:

```
[2025-01-29 10:30:45] [INFO] Starting installation...
[2025-01-29 10:30:46] [SUCCESS] UV installed successfully
[2025-01-29 10:31:20] [SUCCESS] MoAI-ADK installed successfully
[2025-01-29 10:31:25] [INFO] Korean locale configured
```

## Korean Language Support

### Automatic Detection

```bash
# System with ko_KR.UTF-8 locale
uv run installer.py install

# Output:
Korean locale detected. Install Korean support? [Y/n]: y
```

### Manual Setup

```bash
# During installation
uv run installer.py install --korean

# Post-installation
uv run installer.py setup-korean
```

### Korean Fonts by Platform

**macOS:**
```bash
brew install --cask font-nanum
brew install --cask font-nanum-gothic-coding
```

**Ubuntu/Debian:**
```bash
sudo apt-get install fonts-nanum fonts-nanum-coding
```

**Fedora/RHEL:**
```bash
sudo yum install google-noto-sans-cjk-ttc-fonts
```

**Arch Linux:**
```bash
sudo pacman -S noto-fonts-cjk
```

### Korean Configuration File

`~/.moai/config/settings.json`:

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

## Installation Flow

### Complete Installation Process

```
1. Display banner and version
   ↓
2. Gather system information
   ↓
3. Display system info table
   ↓
4. Auto-detect Korean locale
   ↓
5. Prompt for installation confirmation
   ↓
6. Check Python version (3.11+)
   ↓
7. Create ~/.moai directory structure
   ↓
8. Install UV package manager
   ↓
9. Install MoAI-ADK via UV
   ↓
10. Verify installation (import check)
    ↓
11. Setup Korean support (if enabled)
    ↓
12. Create activation script
    ↓
13. Display next steps
```

### Korean Setup Flow

```
1. Detect operating system
   ↓
2. Install platform-specific fonts
   │
   ├─ macOS: Homebrew casks
   ├─ Linux (apt): fonts-nanum
   ├─ Linux (yum): google-noto-sans-cjk
   └─ Linux (pacman): noto-fonts-cjk
   ↓
3. Create Korean locale configuration
   ↓
4. Enable Korean NLP features
   ↓
5. Configure UI fonts
```

## Usage Examples

### Example 1: First-Time Installation

```bash
$ uv run installer.py install

╔══════════════════════════════════════════════════╗
║           MoAI-ADK Installer v1.0.0              ║
╚══════════════════════════════════════════════════╝

╭────────────── System Information ──────────────╮
│ OS              │ Darwin 23.0.0                 │
│ Python          │ 3.11.5                        │
│ Korean Detected │ Yes                           │
╰─────────────────┴───────────────────────────────╯

Korean locale detected. Install Korean support? [Y/n]: y

Proceed with installation? [Y/n]: y

Starting installation...

✓ Python 3.11.5 is installed
✓ Created directory: /Users/user/.moai
✓ UV installed successfully
⠋ Installing MoAI-ADK... ━━━━━━━━━━━━━━━━ 100%
✓ MoAI-ADK version 1.0.0 is correctly installed
✓ Korean fonts installed
✓ Korean configuration created
✓ Activation script created

╔══════════════════════════════════════════════════╗
║            Installation Complete!                ║
╚══════════════════════════════════════════════════╝
```

### Example 2: Verification After Installation

```bash
$ uv run installer.py verify

Verifying MoAI-ADK installation...

╭─────────────────── Installation Status ────────────────────╮
│ Component          Status  Details                         │
├────────────────────────────────────────────────────────────┤
│ Config directory   ✓       /Users/user/.moai               │
│ UV package manager ✓       Installed                       │
│ MoAI-ADK          ✓       v1.0.0                           │
│ Korean config      ✓       /Users/user/.moai/config/...    │
╰────────────────────────────────────────────────────────────╯
```

### Example 3: Check Status

```bash
$ uv run installer.py status

╭────────────── System Information ───────────────╮
│ Os Type          Darwin                          │
│ Python Version   3.11.5                          │
│ Locale           ko_KR.UTF-8                     │
│ Is Korean        True                            │
╰─────────────────────────────────────────────────╯

╭──────────────── Configuration ─────────────────╮
│ {                                               │
│   "language": "ko_KR",                         │
│   "ui": {                                       │
│     "font_family": "Nanum Gothic"              │
│   }                                             │
│ }                                               │
╰────────────────────────────────────────────────╯
```

### Example 4: Add Korean Support Later

```bash
$ uv run installer.py setup-korean

Korean Language Setup

Installing font-nanum...
✓ Installed font-nanum
Installing font-nanum-gothic-coding...
✓ Installed font-nanum-gothic-coding
✓ Korean configuration created

Korean language support configured
```

## Troubleshooting

### Issue: Dependencies Not Found

```bash
Error: Required dependencies not found
Install with: uv pip install click rich
```

**Solution:**
UV should auto-install dependencies. If not:
```bash
uv pip install click rich
python installer.py install
```

### Issue: UV Not Found

```bash
Error: UV not found in PATH
Run: source ~/.bashrc or source ~/.zshrc
```

**Solution:**
```bash
# Add UV to PATH
export PATH="$HOME/.cargo/bin:$PATH"

# Or reload shell config
source ~/.zshrc  # or ~/.bashrc
```

### Issue: Permission Denied

```bash
Error: Permission denied when installing fonts
```

**Solution:**
```bash
# macOS: Ensure Homebrew is installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Linux: Use sudo for font installation
sudo apt-get install fonts-nanum
```

### Issue: Korean Fonts Not Displaying

**Check installed fonts:**

macOS:
```bash
fc-list | grep -i nanum
```

Linux:
```bash
fc-list | grep -i nanum
fc-cache -fv
```

### Issue: Import Error After Installation

```bash
Error: MoAI-ADK import failed
```

**Solution:**
```bash
# Verify Python can find the package
python3 -c "import sys; print(sys.path)"

# Reinstall with force
uv run installer.py install --force
```

## Advanced Usage

### Custom Python Version

```bash
# Use specific Python version
python3.11 -m uv run installer.py install
```

### Environment Variables

```bash
# Set custom config directory (before installation)
export MOAI_CONFIG_DIR="/opt/moai"

# Run installer
uv run installer.py install
```

### Programmatic Usage

```python
from installer import (
    get_system_info,
    install_moai_adk,
    verify_installation,
    InstallationConfig
)

# Get system info
system = get_system_info()
print(f"Korean detected: {system.is_korean}")

# Create config
config = InstallationConfig(
    install_korean_fonts=True,
    force_reinstall=False
)

# Install
install_moai_adk(config)
verify_installation()
```

## Development

### Testing the Installer

```bash
# Run test script
bash test_installer.sh

# Manual testing
uv run installer.py install --dry-run --verbose
```

### Code Structure

```
installer.py
├── Configuration & Constants (lines 1-50)
├── Data Classes (lines 51-100)
│   ├── SystemInfo
│   ├── InstallationConfig
│   └── InstallationStatus
├── Utility Functions (lines 101-200)
├── Installation Functions (lines 201-400)
├── Korean Language Support (lines 401-500)
├── Post-Installation (lines 501-550)
└── CLI Commands (lines 551-700)
    ├── install
    ├── verify
    ├── status
    ├── uninstall
    └── setup-korean
```

## Comparison with Other Installers

See [COMPARISON.md](./COMPARISON.md) for detailed comparison.

## License

MIT License - See main MoAI-ADK repository.

## Support

- **Installation Issues**: Check logs at `~/.moai/logs/installer.log`
- **Korean Support**: See [KOREAN-SETUP.md](./KOREAN-SETUP.md)
- **Architecture Details**: See [ARCHITECTURE.md](./ARCHITECTURE.md)
