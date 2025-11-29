# MoAI-ADK System Requirements

**Version**: 1.0.0
**Last Updated**: November 29, 2025
**Compatibility**: macOS, Linux, Windows (WSL2)

## 📋 Overview

This document outlines all system requirements for MoAI-ADK installation and operation, including mandatory components and optional Korean language support.

---

## 🐍 Python Requirements

### **Supported Python Versions**

MoAI-ADK requires Python 3.11 or higher:

| Version | Status | Recommended | Notes |
|---------|--------|-------------|-------|
| 3.14.x | ✅ Supported | ⭐ Best | Latest features, optimal performance |
| 3.13.x | ✅ Supported | ⭐ Recommended | Stable, well-tested |
| 3.12.x | ✅ Supported | ⭐ Recommended | Most widely used |
| 3.11.x | ✅ Supported | ✔️ Minimum | Fully compatible |
| 3.10.x | ❌ Not Supported | - | Missing required features |
| 3.9.x and below | ❌ Not Supported | - | Too old |

### **Why Python 3.11+?**

MoAI-ADK uses modern Python features:
- **PEP 723**: Inline script metadata for UV dependencies
- **PEP 680**: `tomllib` standard library (built-in TOML parser)
- **PEP 654**: Exception groups and `except*` syntax
- **Structural pattern matching**: Advanced control flow
- **Performance**: 10-60% faster than Python 3.10

### **Checking Python Version**

```bash
# Check installed version
python3 --version

# Expected output:
# Python 3.12.0 (or 3.11.x, 3.13.x, 3.14.x)

# Check installation location
which python3

# Expected output:
# /usr/local/bin/python3 (or /opt/homebrew/bin/python3 on M1 Macs)
```

### **Installing Python**

#### macOS (Homebrew)
```bash
# Install latest Python
brew install python@3.13

# Verify installation
python3.13 --version
```

#### macOS (pyenv - Recommended)
```bash
# Install pyenv
brew install pyenv

# Install specific Python version
pyenv install 3.13.0

# Set as global default
pyenv global 3.13.0

# Add to shell configuration
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc
echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zshrc
echo 'eval "$(pyenv init -)"' >> ~/.zshrc
```

#### Linux (apt)
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.13 python3.13-venv python3.13-dev

# Verify
python3.13 --version
```

#### Linux (pyenv)
```bash
# Install pyenv
curl https://pyenv.run | bash

# Install Python
pyenv install 3.13.0
pyenv global 3.13.0
```

#### Windows (WSL2)
```bash
# Install WSL2 first, then use Ubuntu instructions
wsl --install
wsl
sudo apt update
sudo apt install python3.13 python3.13-venv
```

---

## 📦 UV Package Manager

### **What is UV?**

UV is a modern Python package installer and virtual environment manager:
- **Fast**: 10-100x faster than pip
- **Reliable**: Consistent dependency resolution
- **Modern**: Supports PEP 723 inline dependencies
- **Simple**: Single command installation

**Required Version**: `uv >= 0.5.0`

### **Installing UV**

#### macOS/Linux (Recommended)
```bash
# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Verify installation
uv --version

# Expected output:
# uv 0.5.4 (or higher)
```

#### Homebrew (Alternative)
```bash
brew install uv
uv --version
```

#### Windows (PowerShell)
```powershell
# Install UV
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Verify
uv --version
```

### **Configuring UV**

```bash
# Add UV to PATH (if not automatic)
export PATH="$HOME/.local/bin:$PATH"
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc

# Set UV cache location (optional)
export UV_CACHE_DIR="$HOME/.cache/uv"

# Configure UV settings
uv config set python-preference system
```

### **Why UV Instead of Pip?**

| Feature | UV | Pip | Advantage |
|---------|-----|-----|-----------|
| Speed | ⚡ 10-100x | ❌ Slow | Faster installs |
| PEP 723 | ✅ Yes | ❌ No | Inline dependencies |
| Lockfiles | ✅ Built-in | ❌ Needs pip-tools | Reproducible builds |
| Caching | ✅ Smart | ⚠️ Basic | Reduced downloads |
| Resolution | ✅ Fast | ❌ Slow | Better conflicts |

---

## 💻 System Requirements

### **Operating Systems**

| OS | Version | Status | Notes |
|----|---------|--------|-------|
| **macOS** | 11+ (Big Sur+) | ✅ Fully Supported | Intel and Apple Silicon |
| **Linux** | Ubuntu 20.04+ | ✅ Fully Supported | Debian-based distros |
| **Linux** | Fedora 35+ | ✅ Fully Supported | RPM-based distros |
| **Linux** | Arch Linux | ✅ Fully Supported | Rolling release |
| **Windows** | WSL2 | ✅ Supported | Requires WSL2 setup |
| **Windows** | Native | ⚠️ Experimental | Limited testing |

### **Hardware Requirements**

#### Minimum Requirements
- **CPU**: 2 cores, 2.0 GHz
- **RAM**: 4 GB
- **Storage**: 500 MB free space
- **Network**: Internet connection for initial setup

#### Recommended Requirements
- **CPU**: 4+ cores, 2.5+ GHz
- **RAM**: 8+ GB
- **Storage**: 2+ GB free space (for agent caching)
- **Network**: Stable broadband connection

#### Optimal Requirements (Large Projects)
- **CPU**: 8+ cores, 3.0+ GHz (for parallel agent execution)
- **RAM**: 16+ GB (for multiple agent instances)
- **Storage**: 10+ GB SSD (for fast file operations)
- **Network**: High-speed connection (for cloud integrations)

### **Shell Requirements**

MoAI-ADK requires a POSIX-compatible shell:

| Shell | Status | Notes |
|-------|--------|-------|
| **bash** | ✅ Recommended | Version 4.0+ |
| **zsh** | ✅ Recommended | Default on macOS |
| **fish** | ✅ Supported | Some script modifications needed |
| **sh** | ⚠️ Limited | Basic functionality only |
| **PowerShell** | ❌ Not Supported | Use WSL2 on Windows |

```bash
# Check current shell
echo $SHELL

# Expected output:
# /bin/zsh (or /bin/bash)
```

---

## 🇰🇷 Korean Language Support (Optional)

### **Font Requirements**

For proper Korean character rendering in terminal:

#### **Recommended: D2Coding**
- **Name**: D2Coding (D2 Coding font)
- **Version**: 1.3.2 or higher
- **License**: Open Source (OFL)
- **Features**:
  - Optimized for Korean programming
  - Clear distinction between similar characters
  - Excellent CJK (Chinese/Japanese/Korean) support
  - Ligatures for common code patterns

#### **Alternatives**
- **Nanum Gothic Coding**: Free, good Korean support
- **Jetbrains Mono**: Modern, Korean subset included
- **Source Code Pro**: Adobe font with Korean glyphs
- **Cascadia Code**: Microsoft font with Korean support

### **Installing D2Coding Font**

#### macOS
```bash
# Using Homebrew (Recommended)
brew tap homebrew/cask-fonts
brew install --cask font-d2coding

# Verify installation
fc-list | grep -i d2coding

# Expected output:
# /Users/you/Library/Fonts/D2Coding.ttc: D2Coding:style=Regular
```

#### Linux (Ubuntu/Debian)
```bash
# Download and install
wget https://github.com/naver/d2codingfont/releases/download/VER1.3.2/D2Coding-Ver1.3.2-20180524.zip
unzip D2Coding-Ver1.3.2-20180524.zip
sudo mkdir -p /usr/share/fonts/truetype/d2coding
sudo cp D2Coding/*.ttf /usr/share/fonts/truetype/d2coding/
sudo fc-cache -f -v

# Verify
fc-list | grep -i d2coding
```

#### Windows (WSL2)
```bash
# Download font to Windows
# Install via Windows Font Manager (double-click .ttf)
# WSL2 will inherit Windows fonts automatically
```

### **Terminal Configuration**

#### Ghostty (Recommended for Korean)
```bash
# Create/edit config
mkdir -p ~/.config/ghostty
cat >> ~/.config/ghostty/config << 'EOF'
# Korean font configuration
font-family = "D2Coding"
font-size = 13
font-feature = +liga +calt

# Character encoding
locale = ko_KR.UTF-8
shell-integration-features = true

# Korean input support
allow-alternate-screen = true
EOF

# Restart Ghostty
```

#### iTerm2 (macOS)
```
1. Open iTerm2 Preferences (⌘,)
2. Go to Profiles → Text
3. Change Font to "D2Coding 13pt"
4. Enable "Use Unicode version 9 widths"
5. Set Character Encoding to "UTF-8"
```

#### Terminal.app (macOS)
```
1. Open Terminal Preferences (⌘,)
2. Go to Profiles → Text
3. Click "Change" under Font
4. Select "D2Coding Regular 13"
5. Restart Terminal
```

#### GNOME Terminal (Linux)
```
1. Edit → Preferences
2. Select profile → Text
3. Uncheck "Use system font"
4. Select "D2Coding Regular 13"
5. Set Character Encoding to "UTF-8"
```

### **Locale Configuration**

For proper Korean text handling:

#### macOS
```bash
# Check current locale
locale

# Add to shell config
echo 'export LANG=ko_KR.UTF-8' >> ~/.zshrc
echo 'export LC_ALL=ko_KR.UTF-8' >> ~/.zshrc
source ~/.zshrc
```

#### Linux
```bash
# Install Korean locale
sudo locale-gen ko_KR.UTF-8
sudo update-locale LANG=ko_KR.UTF-8

# Add to shell config
echo 'export LANG=ko_KR.UTF-8' >> ~/.bashrc
echo 'export LC_ALL=ko_KR.UTF-8' >> ~/.bashrc
source ~/.bashrc
```

### **Testing Korean Support**

```bash
# Test Korean character display
echo "한글 테스트: MoAI-ADK 설치 완료"

# Expected output (with proper font):
# 한글 테스트: MoAI-ADK 설치 완료

# If broken (without Korean font):
# □□ □□: MoAI-ADK □□ □□
```

---

## 🔧 Additional Dependencies

### **Git (Recommended)**

For cloning repositories and version control:

```bash
# Check Git version
git --version

# Install if missing
# macOS
brew install git

# Linux
sudo apt install git  # Ubuntu/Debian
sudo dnf install git  # Fedora
```

**Minimum Version**: Git 2.30+

### **Build Tools (Optional)**

For compiling Python packages with C extensions:

#### macOS
```bash
# Install Xcode Command Line Tools
xcode-select --install
```

#### Linux
```bash
# Ubuntu/Debian
sudo apt install build-essential python3-dev

# Fedora
sudo dnf install gcc gcc-c++ python3-devel
```

### **SSL/TLS Libraries**

For secure HTTPS connections:

#### macOS
```bash
# Usually pre-installed, verify with:
brew list openssl
```

#### Linux
```bash
# Ubuntu/Debian
sudo apt install libssl-dev

# Fedora
sudo dnf install openssl-devel
```

---

## 📊 Disk Space Requirements

### **Installation Sizes**

| Component | Size | Location |
|-----------|------|----------|
| Python 3.13 | ~100 MB | `/usr/local/` or `/opt/homebrew/` |
| UV package manager | ~20 MB | `~/.local/bin/` |
| MoAI-ADK source | ~50 MB | Installation directory |
| Virtual environment | ~200 MB | `.venv/` |
| Agent cache | ~100 MB | `.moai/cache/` |
| Korean fonts | ~10 MB | `/usr/share/fonts/` |
| **Total** | **~480 MB** | - |

### **Runtime Storage**

During operation, MoAI-ADK may use:
- **Logs**: ~50 MB per month (`logs/`)
- **Agent outputs**: ~100 MB per project (`outputs/`)
- **Temporary files**: ~50 MB (`/tmp/moai-*`)

**Recommended Free Space**: 2+ GB for comfortable operation

---

## 🌐 Network Requirements

### **Internet Connection**

Required for:
- ✅ Initial installation (downloading packages)
- ✅ Agent dependency resolution
- ⚠️ Optional: Cloud integrations (if enabled)

### **Bandwidth Estimates**

| Operation | Data Transfer | Frequency |
|-----------|--------------|-----------|
| Initial install | ~300 MB | Once |
| Agent updates | ~50 MB | Monthly |
| Cloud sync (optional) | ~10 MB | Per session |

### **Firewall Configuration**

MoAI-ADK requires outbound HTTPS (port 443) access to:
- `pypi.org` - Python packages
- `github.com` - Git repositories
- `astral.sh` - UV downloads
- `fonts.googleapis.com` - Font downloads (optional)

**No inbound ports required** - MoAI-ADK operates entirely locally.

---

## ✅ Requirements Checklist

Before installation, verify:

### **Mandatory Requirements**
- [ ] Python 3.11, 3.12, 3.13, or 3.14 installed
- [ ] UV package manager (0.5.0+) installed
- [ ] 500+ MB free disk space
- [ ] POSIX-compatible shell (bash/zsh)
- [ ] Internet connection available

### **Recommended Components**
- [ ] Git version control (2.30+)
- [ ] Build tools (gcc, make)
- [ ] SSL/TLS libraries
- [ ] 2+ GB free disk space

### **Korean Support (Optional)**
- [ ] D2Coding font installed
- [ ] Terminal configured for UTF-8
- [ ] Korean locale enabled (ko_KR.UTF-8)
- [ ] Terminal font set to D2Coding

### **Verification Commands**
```bash
# Check all requirements
python3 --version     # 3.11-3.14
uv --version          # 0.5.0+
git --version         # 2.30+ (optional)
echo $SHELL           # bash or zsh
fc-list | grep D2     # D2Coding font (optional)
locale | grep UTF-8   # UTF-8 locale
df -h .               # Check disk space
```

---

## 🚀 Next Steps

Once all requirements are met:

1. **Proceed to Installation**: See `02-INSTALLATION.md`
2. **Configure Korean Support**: See `03-KOREAN-SETUP.md` (optional)
3. **Verify Installation**: See `04-VERIFICATION.md`

If you encounter issues, consult `05-TROUBLESHOOTING.md`.

---

## 📞 Support

For requirements-related questions:
- **Python Issues**: https://www.python.org/downloads/
- **UV Issues**: https://github.com/astral-sh/uv
- **Korean Font Issues**: See `03-KOREAN-SETUP.md`
- **General Help**: See `05-TROUBLESHOOTING.md`
