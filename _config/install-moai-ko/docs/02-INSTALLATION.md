# MoAI-ADK Installation Guide

**Version**: 1.0.0
**Last Updated**: November 29, 2025
**Estimated Time**: 5-10 minutes

## 📋 Overview

This guide provides detailed installation instructions for MoAI-ADK (Mixture of Agents - Agent Development Kit) with complete Korean language support.

**Three Installation Methods**:
1. **Automated Script** (Recommended) - Interactive, handles everything
2. **Manual UV Installation** - Full control, step-by-step
3. **Traditional Pip Installation** - Fallback option

---

## 🎯 Pre-Installation Checklist

Before starting, ensure you have completed the requirements from `01-REQUIREMENTS.md`:

```bash
# Verify Python version (3.11-3.14)
python3 --version

# Verify UV installation (0.5.0+)
uv --version

# Check disk space (500+ MB free)
df -h .

# Verify shell (bash or zsh)
echo $SHELL

# Optional: Check Korean font
fc-list | grep -i d2coding
```

**All checks passed?** Proceed with installation.

---

## 🚀 Method 1: Automated Installation (Recommended)

### **Overview**

The automated script handles:
- ✅ Python version detection
- ✅ Virtual environment creation
- ✅ Dependency installation via UV
- ✅ Agent configuration (26 agents)
- ✅ Korean font setup (optional)
- ✅ Verification tests

### **Step 1: Download MoAI-ADK**

Choose ONE method:

#### Option A: Git Clone (Best for Development)
```bash
# Clone repository
cd ~/Documents
git clone https://github.com/your-org/moai-adk.git
cd moai-adk/_config/install-moai-ko

# Verify download
ls -la
# Should show: install-moai-ko.sh, moai.sh, requirements files
```

#### Option B: Download ZIP (Quick Start)
```bash
# Download from releases
curl -L https://github.com/your-org/moai-adk/archive/main.zip -o moai-adk.zip
unzip moai-adk.zip
cd moai-adk-main/_config/install-moai-ko
```

#### Option C: Direct Path (Already Downloaded)
```bash
# Navigate to existing download
cd /Users/rdmtv/Documents/claydev-local/agent-os-v2/moai-adk/_config/install-moai-ko
```

### **Step 2: Make Script Executable**

```bash
# Add execute permissions
chmod +x install-moai-ko.sh

# Verify permissions
ls -l install-moai-ko.sh
# Should show: -rwxr-xr-x (x = executable)
```

### **Step 3: Run Installation Script**

```bash
# Execute automated installation
./install-moai-ko.sh
```

### **Step 4: Follow Interactive Prompts**

The script will guide you through:

#### **Prompt 1: Installation Method**
```
Choose installation method:
1) UV (Recommended - Fast, modern)
2) Pip (Traditional - Slower)
3) Exit

Your choice [1]:
```
**Recommendation**: Press `1` (UV) or just `Enter` for default.

#### **Prompt 2: Python Version**
```
Detected Python versions:
1) Python 3.13.0 (/opt/homebrew/bin/python3.13)
2) Python 3.12.0 (/usr/local/bin/python3.12)
3) Python 3.11.5 (/usr/bin/python3.11)

Select Python version [1]:
```
**Recommendation**: Press `1` (latest version) or `Enter` for default.

#### **Prompt 3: Korean Support** (Optional)
```
🇰🇷 Enable Korean language support?
This will install D2Coding font and configure Korean locale.

Enable Korean support? (y/N):
```
**Recommendation**:
- Press `y` if you need Korean language support
- Press `n` or `Enter` to skip (English only)

### **Step 5: Wait for Installation**

The script will:
```
🚀 MoAI-ADK Installation Starting...
✅ Python 3.13 detected
✅ UV package manager found (v0.5.4)
✅ Creating virtual environment at .venv/
✅ Activating virtual environment
✅ Installing core dependencies...
   - pydantic (5s)
   - yaml (3s)
   - jinja2 (4s)
✅ Installing agent frameworks...
   - langchain (15s)
   - openai (8s)
✅ Configuring 26 agents...
   - SPEC-First agents (0-4) ✅
   - TDD agents (10-14) ✅
   - Development agents (20-24) ✅
   - Analysis agents (30-34) ✅
🇰🇷 Installing Korean support...
   - D2Coding font (8s) ✅
   - Korean locale configuration ✅
✅ Running verification tests...
   - Python imports ✅
   - Agent availability ✅
   - Korean encoding ✅

✅ Installation Complete!

Next steps:
1. Activate virtual environment:
   source .venv/bin/activate

2. Test installation:
   ./moai.sh --help

3. Run first SPEC-First command:
   ./moai.sh /moai:0 "Create hello world specification"
```

**Total Time**: 2-5 minutes (depending on internet speed)

### **Step 6: Activate Virtual Environment**

```bash
# Activate environment
source .venv/bin/activate

# Verify activation (prompt should show (.venv))
which python
# Expected: /path/to/moai-adk/.venv/bin/python
```

### **Step 7: Verify Installation**

```bash
# Test MoAI-ADK command
./moai.sh --help

# Expected output:
# MoAI-ADK - Mixture of Agents Development Kit
# Version: 1.0.0
#
# Available commands:
#   /moai:0-4   - SPEC-First workflow
#   /moai:10-14 - TDD workflow
#   ...

# Test SPEC-First agent
./moai.sh /moai:0 "Create a simple REST API specification"

# Test Korean support (if enabled)
./moai.sh /moai:0 "간단한 REST API 사양 작성"
```

**Installation successful if**:
- ✅ No import errors
- ✅ All agents available (26 total)
- ✅ Commands execute properly
- 🇰🇷 Korean characters display correctly (if enabled)

---

## 🔧 Method 2: Manual UV Installation

### **Overview**

For users who want full control over each step.

### **Step 1: Navigate to Project Directory**

```bash
cd /Users/rdmtv/Documents/claydev-local/agent-os-v2/moai-adk/_config/install-moai-ko
```

### **Step 2: Create Virtual Environment**

```bash
# Create .venv with Python 3.13
uv venv --python 3.13

# Verify creation
ls -la .venv/
# Should show: bin/, lib/, include/, pyvenv.cfg
```

### **Step 3: Activate Virtual Environment**

```bash
# Activate environment
source .venv/bin/activate

# Verify activation
which python
# Expected: /path/to/moai-adk/.venv/bin/python

python --version
# Expected: Python 3.13.x (or your selected version)
```

### **Step 4: Install Core Dependencies**

```bash
# Install from requirements file
uv pip install -r requirements.txt

# Or install inline dependencies (PEP 723)
uv pip install pydantic pyyaml jinja2 click rich

# Verify installation
python -c "import pydantic, yaml, jinja2; print('Core dependencies OK')"
```

### **Step 5: Install Agent Framework**

```bash
# Install LangChain and AI libraries
uv pip install langchain langchain-openai langchain-community

# Install additional agent dependencies
uv pip install openai anthropic tiktoken

# Verify
python -c "import langchain; print('Agent framework OK')"
```

### **Step 6: Configure Agents**

```bash
# Run agent configuration script
python scripts/configure-agents.py

# Expected output:
# Configuring 26 agents...
# ✅ SPEC-First agents (0-4)
# ✅ TDD agents (10-14)
# ✅ Development agents (20-24)
# ✅ Analysis agents (30-34)
# Configuration complete!
```

### **Step 7: Verify Installation**

```bash
# Test MoAI-ADK
./moai.sh --help

# Run verification script
python scripts/verify-installation.py

# Expected output:
# ✅ Python version: 3.13.0
# ✅ Virtual environment: Active
# ✅ Core dependencies: Installed
# ✅ Agent framework: Configured
# ✅ Total agents: 26
# ✅ Installation: VERIFIED
```

---

## 📦 Method 3: Traditional Pip Installation (Fallback)

### **When to Use This Method**

- UV installation fails
- Corporate firewall blocks UV
- Python version compatibility issues
- Prefer traditional tools

### **Step 1: Create Virtual Environment**

```bash
# Navigate to project
cd /Users/rdmtv/Documents/claydev-local/agent-os-v2/moai-adk/_config/install-moai-ko

# Create venv with Python
python3 -m venv .venv

# Activate environment
source .venv/bin/activate
```

### **Step 2: Upgrade Pip**

```bash
# Upgrade pip to latest version
pip install --upgrade pip setuptools wheel

# Verify pip version
pip --version
# Expected: pip 24.0+ (or latest)
```

### **Step 3: Install Dependencies**

```bash
# Install from requirements file
pip install -r requirements.txt

# Alternative: Install packages individually
pip install pydantic pyyaml jinja2 click rich
pip install langchain langchain-openai langchain-community
pip install openai anthropic tiktoken
```

**Note**: Pip installation is slower than UV (5-10x longer).

### **Step 4: Verify Installation**

```bash
# Test imports
python -c "import pydantic, langchain; print('Dependencies OK')"

# Configure agents
python scripts/configure-agents.py

# Test MoAI-ADK
./moai.sh --help
```

---

## 🇰🇷 Korean Language Support Installation

### **Automatic (via install script)**

If you chose "Yes" during automated installation, Korean support is already configured.

### **Manual Installation**

#### **Step 1: Install D2Coding Font**

```bash
# macOS (Homebrew)
brew tap homebrew/cask-fonts
brew install --cask font-d2coding

# Linux (Ubuntu/Debian)
wget https://github.com/naver/d2codingfont/releases/download/VER1.3.2/D2Coding-Ver1.3.2-20180524.zip
unzip D2Coding-Ver1.3.2-20180524.zip
sudo mkdir -p /usr/share/fonts/truetype/d2coding
sudo cp D2Coding/*.ttf /usr/share/fonts/truetype/d2coding/
sudo fc-cache -f -v

# Verify installation
fc-list | grep -i d2coding
```

#### **Step 2: Configure Terminal**

See `03-KOREAN-SETUP.md` for detailed terminal configuration.

Quick setup for Ghostty:
```bash
mkdir -p ~/.config/ghostty
cat >> ~/.config/ghostty/config << 'EOF'
font-family = "D2Coding"
font-size = 13
locale = ko_KR.UTF-8
EOF
```

#### **Step 3: Set Korean Locale**

```bash
# macOS
echo 'export LANG=ko_KR.UTF-8' >> ~/.zshrc
echo 'export LC_ALL=ko_KR.UTF-8' >> ~/.zshrc
source ~/.zshrc

# Linux
sudo locale-gen ko_KR.UTF-8
sudo update-locale LANG=ko_KR.UTF-8
echo 'export LANG=ko_KR.UTF-8' >> ~/.bashrc
source ~/.bashrc
```

#### **Step 4: Test Korean Support**

```bash
# Test Korean character display
echo "한글 테스트: MoAI-ADK 설치 완료"

# Test MoAI-ADK with Korean
./moai.sh /moai:0 "간단한 REST API 사양 작성"
```

---

## 🔍 Post-Installation Configuration

### **Environment Variables**

Create `.env` file for optional configuration:

```bash
# Create .env file
cat > .env << 'EOF'
# MoAI-ADK Configuration
MOAI_LOG_LEVEL=INFO
MOAI_AGENT_TIMEOUT=300
MOAI_MAX_CONCURRENT_AGENTS=5

# OpenAI API (optional - for AI-powered agents)
# OPENAI_API_KEY=sk-your-key-here

# Anthropic API (optional)
# ANTHROPIC_API_KEY=sk-ant-your-key-here

# Korean language support
LANG=ko_KR.UTF-8
LC_ALL=ko_KR.UTF-8
EOF
```

### **Shell Integration**

Add MoAI-ADK to your shell configuration:

```bash
# For zsh (macOS default)
cat >> ~/.zshrc << 'EOF'
# MoAI-ADK
export MOAI_HOME="/Users/rdmtv/Documents/claydev-local/agent-os-v2/moai-adk"
alias moai="$MOAI_HOME/_config/install-moai-ko/moai.sh"
alias moai-activate="source $MOAI_HOME/_config/install-moai-ko/.venv/bin/activate"
EOF

# For bash
cat >> ~/.bashrc << 'EOF'
# MoAI-ADK
export MOAI_HOME="/Users/rdmtv/Documents/claydev-local/agent-os-v2/moai-adk"
alias moai="$MOAI_HOME/_config/install-moai-ko/moai.sh"
alias moai-activate="source $MOAI_HOME/_config/install-moai-ko/.venv/bin/activate"
EOF

# Reload shell
source ~/.zshrc  # or source ~/.bashrc
```

Now you can use:
```bash
# From anywhere:
moai /moai:0 "Create specification"

# Or activate environment:
moai-activate
```

---

## ✅ Verification Checklist

After installation, verify all components:

```bash
# Activate environment
source .venv/bin/activate

# Run comprehensive verification
python scripts/verify-installation.py

# Manual verification steps:
# 1. Python version
python --version  # 3.11-3.14

# 2. Core dependencies
python -c "import pydantic, yaml, jinja2; print('✅ Core OK')"

# 3. Agent framework
python -c "import langchain; print('✅ Agents OK')"

# 4. MoAI-ADK command
./moai.sh --help  # Should show help text

# 5. Agent count
./moai.sh /moai:list | wc -l  # Should show 26

# 6. SPEC-First test
./moai.sh /moai:0 "Test specification"  # Should generate output

# 7. Korean support (if enabled)
echo "한글 테스트" | grep "한글"  # Should display Korean

# 8. File encoding
file -I outputs/test.txt  # Should show charset=utf-8
```

**All checks passed?** Installation is complete! Proceed to `04-VERIFICATION.md` for full validation.

---

## 🐛 Troubleshooting Installation Issues

### **Python Version Errors**

```bash
# Error: Python 3.11+ required
# Solution: Install correct Python version
pyenv install 3.13.0
pyenv local 3.13.0
```

### **UV Not Found**

```bash
# Error: uv: command not found
# Solution: Reinstall UV and add to PATH
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
```

### **Virtual Environment Issues**

```bash
# Error: Cannot activate .venv
# Solution: Remove and recreate
rm -rf .venv
uv venv --python 3.13
source .venv/bin/activate
```

### **Dependency Installation Failures**

```bash
# Error: Package installation failed
# Solution 1: Clear UV cache
uv cache clean

# Solution 2: Try pip instead
pip install -r requirements.txt

# Solution 3: Install build tools
# macOS
xcode-select --install

# Linux
sudo apt install build-essential python3-dev
```

### **Korean Font Issues**

```bash
# Error: Korean characters show as boxes
# Solution: Install D2Coding font
brew install --cask font-d2coding

# Restart terminal
# Configure terminal font to D2Coding
```

### **Permission Errors**

```bash
# Error: Permission denied on install-moai-ko.sh
# Solution: Add execute permission
chmod +x install-moai-ko.sh

# Error: Permission denied in /usr/local
# Solution: Use user-local installation or sudo
uv venv --python 3.13  # User-local (recommended)
# OR
sudo chown -R $(whoami) /usr/local  # Fix permissions
```

For detailed troubleshooting, see `05-TROUBLESHOOTING.md`.

---

## 🚀 Next Steps

After successful installation:

1. **Verify Installation**: Complete `04-VERIFICATION.md` checklist
2. **Configure Korean Support**: See `03-KOREAN-SETUP.md` (if needed)
3. **Learn MoAI-ADK**: Read `docs/api/moai-adk-api.md`
4. **Try First Workflow**:
   ```bash
   source .venv/bin/activate
   ./moai.sh /moai:0 "Create a todo list app specification"
   ```

---

## 📞 Support & Resources

- **Installation Issues**: See `05-TROUBLESHOOTING.md`
- **Korean Setup**: See `03-KOREAN-SETUP.md`
- **API Reference**: See `docs/api/moai-adk-api.md`
- **Examples**: See `examples/` directory

Happy coding with MoAI-ADK! 🚀🇰🇷
