# MoAI-ADK Troubleshooting Guide

**Version**: 1.0.0
**Last Updated**: November 29, 2025

## 📋 Overview

This comprehensive troubleshooting guide covers common installation and runtime issues for MoAI-ADK, including Korean language support problems, dependency conflicts, and platform-specific challenges.

---

## 🔍 Quick Diagnostic

### **Run Diagnostic Script**

```bash
# Navigate to MoAI-ADK directory
cd /Users/rdmtv/Documents/claydev-local/agent-os-v2/moai-adk/_config/install-moai-ko

# Run diagnostic
python << 'EOF'
#!/usr/bin/env python3
import sys
import os
import subprocess
from pathlib import Path

print("=" * 60)
print("MoAI-ADK Diagnostic Tool")
print("=" * 60)

# Check 1: Python version
print(f"\n1. Python Version: {sys.version}")
if sys.version_info < (3, 11):
    print("   ❌ ERROR: Python 3.11+ required")
else:
    print("   ✅ OK")

# Check 2: Virtual environment
venv_path = Path(".venv")
print(f"\n2. Virtual Environment:")
print(f"   Path exists: {venv_path.exists()}")
print(f"   Current prefix: {sys.prefix}")
if str(venv_path.absolute()) in sys.prefix:
    print("   ✅ OK: Virtual environment active")
else:
    print("   ⚠️  WARNING: Virtual environment not active")

# Check 3: Dependencies
print(f"\n3. Dependencies:")
deps = ['pydantic', 'yaml', 'jinja2', 'langchain']
for dep in deps:
    try:
        __import__(dep)
        print(f"   ✅ {dep}: Installed")
    except ImportError:
        print(f"   ❌ {dep}: Missing")

# Check 4: Encoding
print(f"\n4. Encoding:")
print(f"   Default: {sys.getdefaultencoding()}")
print(f"   Filesystem: {sys.getfilesystemencoding()}")
if sys.getdefaultencoding() == 'utf-8':
    print("   ✅ OK")
else:
    print("   ⚠️  WARNING: Not UTF-8")

# Check 5: MoAI script
moai_script = Path("moai.sh")
print(f"\n5. MoAI Script:")
print(f"   Exists: {moai_script.exists()}")
print(f"   Executable: {os.access(moai_script, os.X_OK)}")
if moai_script.exists() and os.access(moai_script, os.X_OK):
    print("   ✅ OK")
else:
    print("   ❌ ERROR: Script not executable")

print("\n" + "=" * 60)
EOF
```

---

## 🐍 Python-Related Issues

### **Issue: Wrong Python Version**

**Symptoms**:
```bash
python --version
# Python 3.10.x or lower
```

**Error Messages**:
- `SyntaxError: invalid syntax` (when using Python 3.10 features)
- `ModuleNotFoundError: No module named 'tomllib'`
- `ImportError: cannot import name 'Self' from 'typing'`

**Solutions**:

#### Solution 1: Install Correct Python Version (pyenv)
```bash
# Install pyenv (if not installed)
# macOS
brew install pyenv

# Linux
curl https://pyenv.run | bash

# Install Python 3.13
pyenv install 3.13.0

# Set local version for project
cd /path/to/moai-adk/_config/install-moai-ko
pyenv local 3.13.0

# Verify
python --version  # Should show 3.13.0

# Recreate virtual environment
rm -rf .venv
uv venv --python 3.13
source .venv/bin/activate
uv pip install -r requirements.txt
```

#### Solution 2: Use System Python (if 3.11+)
```bash
# Check available Python versions
ls -l /usr/local/bin/python3*
# or
ls -l /opt/homebrew/bin/python3*

# Use specific version
/usr/local/bin/python3.13 -m venv .venv
source .venv/bin/activate
```

#### Solution 3: Homebrew Installation (macOS)
```bash
# Install latest Python
brew install python@3.13

# Link to system
brew link python@3.13

# Verify
python3.13 --version

# Use for virtual environment
python3.13 -m venv .venv
```

---

### **Issue: Multiple Python Versions Conflict**

**Symptoms**:
- Wrong Python version activated
- `which python` shows unexpected location
- Virtual environment uses wrong interpreter

**Solutions**:

```bash
# Check all Python installations
which -a python3

# Expected output might show:
# /Users/you/.pyenv/shims/python3
# /opt/homebrew/bin/python3
# /usr/local/bin/python3
# /usr/bin/python3

# Solution 1: Use explicit Python path
/opt/homebrew/bin/python3.13 -m venv .venv

# Solution 2: Set pyenv priority
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc
echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zshrc
echo 'eval "$(pyenv init -)"' >> ~/.zshrc
source ~/.zshrc

# Solution 3: Use UV with specific Python
uv venv --python /opt/homebrew/bin/python3.13
```

---

### **Issue: Virtual Environment Not Activating**

**Symptoms**:
```bash
source .venv/bin/activate
# No change to prompt
which python
# Shows system Python, not .venv Python
```

**Solutions**:

```bash
# Solution 1: Check virtual environment exists
ls -la .venv/
# Should show: bin/, lib/, include/, pyvenv.cfg

# If missing, recreate:
rm -rf .venv
uv venv --python 3.13
source .venv/bin/activate

# Solution 2: Fix activation script
chmod +x .venv/bin/activate
source .venv/bin/activate

# Solution 3: Use full path
source "$(pwd)/.venv/bin/activate"

# Solution 4: Check shell compatibility
echo $SHELL
# If using fish or non-bash shell:
# fish
source .venv/bin/activate.fish
# csh/tcsh
source .venv/bin/activate.csh
```

---

## 📦 Dependency Issues

### **Issue: UV Not Found**

**Symptoms**:
```bash
uv --version
# zsh: command not found: uv
```

**Solutions**:

```bash
# Solution 1: Reinstall UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Solution 2: Add to PATH
export PATH="$HOME/.local/bin:$PATH"
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

# Solution 3: Use Homebrew (macOS)
brew install uv

# Solution 4: Verify installation location
find ~ -name "uv" -type f 2>/dev/null
# Add found path to PATH

# Verify
uv --version
```

---

### **Issue: Package Installation Fails**

**Symptoms**:
```bash
uv pip install -r requirements.txt
# ERROR: Failed building wheel for package-name
# ERROR: Could not build wheels for package-name
```

**Solutions**:

#### Solution 1: Install Build Tools

**macOS**:
```bash
# Install Xcode Command Line Tools
xcode-select --install

# Verify installation
xcode-select -p
# Expected: /Library/Developer/CommandLineTools

# If already installed but broken:
sudo rm -rf /Library/Developer/CommandLineTools
xcode-select --install
```

**Linux (Ubuntu/Debian)**:
```bash
sudo apt update
sudo apt install build-essential python3-dev
sudo apt install libssl-dev libffi-dev
```

**Linux (Fedora)**:
```bash
sudo dnf install gcc gcc-c++ python3-devel
sudo dnf install openssl-devel libffi-devel
```

#### Solution 2: Clear Cache and Retry
```bash
# Clear UV cache
uv cache clean

# Clear pip cache
pip cache purge

# Reinstall
uv pip install -r requirements.txt
```

#### Solution 3: Use Pip as Fallback
```bash
source .venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

#### Solution 4: Install Binary Packages
```bash
# Some packages have pre-built wheels
pip install --only-binary :all: package-name

# Or exclude problematic packages from binary builds
pip install --no-binary problematic-package -r requirements.txt
```

---

### **Issue: Import Errors After Installation**

**Symptoms**:
```python
ImportError: No module named 'pydantic'
ModuleNotFoundError: No module named 'langchain'
```

**Solutions**:

```bash
# Solution 1: Verify virtual environment is active
which python
# Should show: /path/to/.venv/bin/python

# If not active:
source .venv/bin/activate

# Solution 2: Reinstall dependencies
pip install --force-reinstall -r requirements.txt

# Solution 3: Check installed packages
pip list | grep -i pydantic
pip list | grep -i langchain

# If missing:
pip install pydantic langchain

# Solution 4: Verify Python environment
python -c "import sys; print('\n'.join(sys.path))"
# Should include .venv/lib/python3.x/site-packages
```

---

## 🖥️ MoAI-ADK Command Issues

### **Issue: moai.sh Permission Denied**

**Symptoms**:
```bash
./moai.sh --help
# bash: ./moai.sh: Permission denied
```

**Solutions**:

```bash
# Solution 1: Add execute permission
chmod +x moai.sh

# Solution 2: Also fix other scripts
chmod +x scripts/*.py
find . -name "*.sh" -exec chmod +x {} \;

# Solution 3: Run with bash explicitly
bash moai.sh --help

# Verify permissions
ls -l moai.sh
# Should show: -rwxr-xr-x
```

---

### **Issue: Agent Not Found**

**Symptoms**:
```bash
./moai.sh /moai:0 "test"
# Error: Agent /moai:0 not found
# Error: No agent configuration for: /moai:0
```

**Solutions**:

```bash
# Solution 1: Run agent configuration
python scripts/configure-agents.py

# Solution 2: Verify agent files exist
ls -l agents/
# Should show: spec-0.yaml, spec-1.yaml, etc.

# Solution 3: Check agent directory structure
find . -name "*.yaml" -path "*/agents/*"

# Solution 4: Regenerate agent configurations
rm -rf agents/
python scripts/setup-agents.py

# Verify agents
./moai.sh /moai:list
```

---

### **Issue: Command Execution Timeout**

**Symptoms**:
```bash
./moai.sh /moai:0 "long task"
# Timeout after 30 seconds
# Error: Command execution timeout
```

**Solutions**:

```bash
# Solution 1: Increase timeout in configuration
cat > config/timeout.yaml << 'EOF'
execution:
  timeout: 300  # 5 minutes
  max_timeout: 600  # 10 minutes
EOF

# Solution 2: Set environment variable
export MOAI_TIMEOUT=300
./moai.sh /moai:0 "long task"

# Solution 3: Run in background
./moai.sh /moai:0 "long task" &
# Monitor with: tail -f logs/moai.log
```

---

## 🇰🇷 Korean Language Issues

### **Issue: Korean Characters Display as Boxes**

**Symptoms**:
```bash
echo "한글 테스트"
# Output: □□ □□□
```

**Solutions**:

#### Solution 1: Install D2Coding Font

**macOS**:
```bash
brew tap homebrew/cask-fonts
brew install --cask font-d2coding

# Verify installation
fc-list | grep -i d2coding

# If still not working, restart terminal application
```

**Linux**:
```bash
# Download and install
wget https://github.com/naver/d2codingfont/releases/download/VER1.3.2/D2Coding-Ver1.3.2-20180524.zip
unzip D2Coding-Ver1.3.2-20180524.zip
sudo cp D2Coding/D2Coding/*.ttf /usr/share/fonts/truetype/
sudo fc-cache -f -v

# Verify
fc-list | grep D2Coding
```

#### Solution 2: Configure Terminal Font

**Ghostty**:
```bash
# Edit config
nano ~/.config/ghostty/config

# Add or update:
font-family = "D2Coding"
font-size = 13

# Restart Ghostty
```

**iTerm2**:
- Preferences → Profiles → Text
- Change font to "D2Coding 13pt"
- Restart iTerm2

**GNOME Terminal**:
- Edit → Preferences → Profiles → Text
- Select "D2Coding Regular 13"
- Restart terminal

#### Solution 3: Fallback Fonts
```bash
# If D2Coding not available, try:
# macOS
brew install --cask font-nanum-gothic-coding

# Linux
sudo apt install fonts-nanum-coding

# Configure terminal to use Nanum Gothic Coding
```

---

### **Issue: Korean Locale Not Set**

**Symptoms**:
```bash
locale
# LANG=en_US.UTF-8
# No ko_KR.UTF-8 shown
```

**Solutions**:

**macOS**:
```bash
# Add to shell config
echo 'export LANG=ko_KR.UTF-8' >> ~/.zshrc
echo 'export LC_ALL=ko_KR.UTF-8' >> ~/.zshrc
source ~/.zshrc

# Verify
locale | grep ko_KR
```

**Linux**:
```bash
# Generate Korean locale
sudo locale-gen ko_KR.UTF-8

# Update locale
sudo update-locale LANG=ko_KR.UTF-8

# Add to shell config
echo 'export LANG=ko_KR.UTF-8' >> ~/.bashrc
echo 'export LC_ALL=ko_KR.UTF-8' >> ~/.bashrc
source ~/.bashrc

# Verify
locale -a | grep ko_KR
```

---

### **Issue: Korean Input Not Working**

**Symptoms**:
- Cannot type Korean characters
- Korean keyboard input shows English

**Solutions**:

**macOS**:
```bash
# System Settings → Keyboard → Input Sources
# Add "Korean - 2-Set Korean"

# Switch input: Control + Space or Command + Space

# In terminal:
# Ensure terminal allows keyboard input
# Ghostty: allow-alternate-screen = true
# iTerm2: Enable "Applications in terminal may access clipboard"
```

**Linux (Ubuntu)**:
```bash
# Install Korean input method
sudo apt install ibus ibus-hangul

# Configure IBus
ibus-setup

# Add Hangul (Korean) input method
# Settings → Region & Language → Input Sources → Add Korean (Hangul)

# Switch input: Super+Space or Alt+Shift
```

---

### **Issue: Korean File Encoding Errors**

**Symptoms**:
```python
UnicodeDecodeError: 'utf-8' codec can't decode byte
UnicodeEncodeError: 'ascii' codec can't encode character
```

**Solutions**:

```bash
# Solution 1: Set Python UTF-8 mode
export PYTHONUTF8=1
export PYTHONIOENCODING=utf-8

# Add to shell config
echo 'export PYTHONUTF8=1' >> ~/.zshrc
echo 'export PYTHONIOENCODING=utf-8' >> ~/.zshrc

# Solution 2: Always use explicit encoding in code
python << 'EOF'
# Always specify encoding
with open('file.txt', 'r', encoding='utf-8') as f:
    content = f.read()

with open('output.txt', 'w', encoding='utf-8') as f:
    f.write("한글 content")
EOF

# Solution 3: Convert file encoding
iconv -f EUC-KR -t UTF-8 old-file.txt > new-file.txt

# Or using Python
python << 'EOF'
with open('old-file.txt', 'r', encoding='euc-kr') as f:
    content = f.read()
with open('new-file.txt', 'w', encoding='utf-8') as f:
    f.write(content)
EOF
```

---

## 🔧 Platform-Specific Issues

### **macOS Apple Silicon (M1/M2/M3) Issues**

**Issue: Architecture Mismatch**

**Symptoms**:
```bash
# ERROR: Cannot install package on ARM64
# WARNING: This package is not compatible with arm64
```

**Solutions**:

```bash
# Solution 1: Use native ARM Python
which python3
# Should show: /opt/homebrew/bin/python3 (not /usr/local)

# If wrong:
brew install python@3.13
brew link python@3.13

# Solution 2: Install Rosetta 2 (for Intel packages)
softwareupdate --install-rosetta

# Solution 3: Force ARM architecture
arch -arm64 brew install python@3.13
arch -arm64 uv venv --python 3.13
```

---

### **Linux Permissions Issues**

**Issue: Cannot Write to /usr/local**

**Symptoms**:
```bash
# ERROR: Permission denied: '/usr/local/lib/python3.x'
```

**Solutions**:

```bash
# Solution 1: Use user-local installation (recommended)
uv venv --python 3.13  # Creates in current directory
pip install --user package-name

# Solution 2: Fix ownership (careful!)
sudo chown -R $USER:$USER /usr/local

# Solution 3: Use virtual environment (best practice)
python3 -m venv ~/.venvs/moai-adk
source ~/.venvs/moai-adk/bin/activate
```

---

### **Windows WSL2 Issues**

**Issue: Path Differences**

**Symptoms**:
- Windows paths not accessible from WSL2
- Files created in WSL not visible in Windows

**Solutions**:

```bash
# Solution 1: Access Windows files from WSL
cd /mnt/c/Users/YourName/Documents

# Solution 2: Access WSL files from Windows
# In Windows Explorer, navigate to:
# \\wsl$\Ubuntu\home\username\

# Solution 3: Use WSL home directory
cd ~
# Keep MoAI-ADK in WSL filesystem for better performance
```

---

## 🐛 Common Runtime Errors

### **Issue: Out of Memory**

**Symptoms**:
```
MemoryError: Unable to allocate array
Killed
```

**Solutions**:

```bash
# Solution 1: Reduce concurrent agents
export MOAI_MAX_CONCURRENT_AGENTS=3

# Solution 2: Increase swap space (Linux)
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Solution 3: Monitor memory usage
top
# or
htop
```

---

### **Issue: Network/API Timeouts**

**Symptoms**:
```
TimeoutError: API request timed out
Connection timeout after 30 seconds
```

**Solutions**:

```bash
# Solution 1: Increase timeout
export MOAI_API_TIMEOUT=120

# Solution 2: Check network connectivity
ping -c 3 api.openai.com
ping -c 3 api.anthropic.com

# Solution 3: Configure proxy (if behind firewall)
export HTTP_PROXY=http://proxy.company.com:8080
export HTTPS_PROXY=http://proxy.company.com:8080
```

---

## 📊 Logging & Debugging

### **Enable Debug Mode**

```bash
# Set debug environment variables
export MOAI_LOG_LEVEL=DEBUG
export MOAI_VERBOSE=1

# Run command with debug output
./moai.sh /moai:0 "test" 2>&1 | tee debug.log

# Check logs
tail -f logs/moai.log
```

### **Common Log Locations**

```bash
# MoAI-ADK logs
ls -lh logs/

# Python logs
tail -f logs/python-errors.log

# Agent execution logs
tail -f logs/agents/spec-0.log
```

---

## 💡 FAQ

### **Q: Can I use MoAI-ADK without Korean support?**

**A:** Yes! Korean support is completely optional. All functionality works perfectly in English-only mode.

### **Q: Why does installation take so long?**

**A:** First-time installation downloads all dependencies. Subsequent activations are instant. Use UV instead of pip for 10-100x faster installs.

### **Q: Can I install MoAI-ADK globally?**

**A:** Not recommended. Use virtual environments to avoid conflicts with system packages.

### **Q: Do I need an API key?**

**A:** Not for basic SPEC-First workflow. AI-powered agents (optional) require OpenAI or Anthropic API keys.

### **Q: How do I update MoAI-ADK?**

**A:**
```bash
git pull origin main  # If using git
pip install --upgrade -r requirements.txt
```

### **Q: Can I use Python 3.10?**

**A:** No. Python 3.11+ is required for PEP 723 (inline dependencies) and modern features.

---

## 📞 Getting Help

### **Before Asking for Help**

1. ✅ Run diagnostic script (see top of this document)
2. ✅ Check verification: `04-VERIFICATION.md`
3. ✅ Review installation steps: `02-INSTALLATION.md`
4. ✅ Search this troubleshooting guide
5. ✅ Check logs: `tail -f logs/moai.log`

### **How to Report Issues**

Include this information:

```bash
# System info
uname -a
python --version
uv --version

# Environment info
which python
echo $VIRTUAL_ENV
locale

# Error output
./moai.sh /moai:0 "test" 2>&1

# Diagnostic output
python scripts/verify-installation.py
```

### **Support Channels**

- **Documentation**: Read all docs in `/docs`
- **Logs**: Check `logs/` directory
- **GitHub Issues**: Report bugs with full diagnostic output
- **Community**: Discord/Slack (check README for links)

---

## 🎯 Quick Solutions Reference

| Problem | Quick Fix |
|---------|-----------|
| `uv: command not found` | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| `Python version too old` | `pyenv install 3.13.0 && pyenv local 3.13.0` |
| `Permission denied: moai.sh` | `chmod +x moai.sh` |
| `Korean boxes □□□` | `brew install --cask font-d2coding` |
| `ModuleNotFoundError` | `source .venv/bin/activate && pip install -r requirements.txt` |
| `Agent not found` | `python scripts/configure-agents.py` |
| `Virtual env not activating` | `rm -rf .venv && uv venv --python 3.13 && source .venv/bin/activate` |

---

**Still stuck?** Review the complete installation process in `02-INSTALLATION.md` or start fresh with `00-INSTALL-STEPS.md`.
