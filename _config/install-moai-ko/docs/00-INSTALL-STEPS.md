# MoAI-ADK Installation Quick Start

**Version**: 1.0.0
**Last Updated**: November 29, 2025
**Estimated Time**: 5-10 minutes

## 🚀 Quick Start Guide

MoAI-ADK (Mixture of Agents - Agent Development Kit) is a powerful SPEC-First/TDD framework with 26 specialized agents and Korean language support.

### Prerequisites Check

Before starting, verify you have:
- ✅ Python 3.11, 3.12, 3.13, or 3.14
- ✅ Terminal with bash/zsh support
- ✅ Internet connection for downloads
- 🇰🇷 **Optional**: Korean font support (D2Coding recommended)

```bash
# Quick check
python3 --version  # Should show 3.11-3.14
which python3      # Verify installation path
```

---

## 📋 Installation Steps

### **Step 1: Install UV Package Manager** (30 seconds)

UV is the modern Python package installer that MoAI-ADK uses for inline dependencies.

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Verify installation
uv --version  # Should show uv 0.5.0 or higher
```

**Troubleshooting**:
- If `uv` command not found, restart terminal or add to PATH:
  ```bash
  export PATH="$HOME/.local/bin:$PATH"
  ```

---

### **Step 2: Download MoAI-ADK** (10 seconds)

Choose ONE of the following methods:

#### Option A: Git Clone (Recommended)
```bash
cd ~/Documents
git clone https://github.com/your-org/moai-adk.git
cd moai-adk/_config/install-moai-ko
```

#### Option B: Download ZIP
```bash
# Download and extract to your preferred location
cd ~/Downloads
unzip moai-adk-main.zip
cd moai-adk-main/_config/install-moai-ko
```

#### Option C: Direct Path
```bash
# If already downloaded
cd /Users/rdmtv/Documents/claydev-local/agent-os-v2/moai-adk/_config/install-moai-ko
```

---

### **Step 3: Run Installation Script** (2-3 minutes)

```bash
# Make script executable
chmod +x install-moai-ko.sh

# Run installation
./install-moai-ko.sh

# Follow interactive prompts:
# 1. Choose installation method (recommended: uv)
# 2. Select Python version (auto-detected)
# 3. Optional: Enable Korean support
```

**Expected Output**:
```
🚀 MoAI-ADK Installation Starting...
✅ Python 3.12 detected
✅ UV package manager found
✅ Creating virtual environment...
✅ Installing dependencies...
✅ Configuring 26 agents...
🇰🇷 Korean support: Optional (continue? y/n)
✅ Installation complete!

Run: source .venv/bin/activate
```

---

## 🇰🇷 Optional: Korean Language Support

**Recommended for Korean users** - enhances terminal output with proper CJK character rendering.

```bash
# Install D2Coding font (best Korean monospace font)
brew tap homebrew/cask-fonts
brew install --cask font-d2coding

# Configure Ghostty terminal (if using)
cat >> ~/.config/ghostty/config << 'EOF'
font-family = "D2Coding"
font-size = 13
EOF
```

**Skip this step if**:
- You don't need Korean language support
- You're using English-only workflows
- Your terminal already has Korean fonts

See `03-KOREAN-SETUP.md` for detailed configuration.

---

## ✅ Verification (1 minute)

Test your installation:

```bash
# Activate virtual environment
source .venv/bin/activate

# Verify MoAI-ADK commands
./moai.sh --help

# Test SPEC-First agent
./moai.sh /moai:0 "Create hello world specification"

# Test Korean support (optional)
./moai.sh /moai:0 "테스트 사양 작성"
```

**Expected Results**:
- ✅ No import errors
- ✅ 26 agents available
- ✅ SPEC-First workflow active
- 🇰🇷 Korean characters display correctly (if enabled)

---

## 📊 What You Get

After installation, you have access to:

### **26 Specialized Agents**
- **SPEC-First Agents** (0-4): Specification, Pseudocode, Architecture, Refinement, Completion
- **TDD Agents** (10-14): Test generation, implementation, validation
- **Development Agents**: Frontend, backend, API, database, DevOps
- **Analysis Agents**: Code review, security, performance, refactoring

### **Core Workflows**
1. **SPEC-First** (`/moai:0-4`): Systematic development from specification
2. **TDD** (`/moai:10-14`): Test-Driven Development workflow
3. **Code Review** (`/moai:20-24`): Quality assurance and security
4. **Refactoring** (`/moai:30-34`): Code improvement and optimization

### **Korean Support** (Optional)
- 🇰🇷 D2Coding font for clear Korean display
- 🇰🇷 UTF-8 encoding for all files
- 🇰🇷 Korean command examples and documentation

---

## 🎯 Next Steps

### Immediate Actions
1. ✅ Complete installation verification (see above)
2. 📖 Read `01-REQUIREMENTS.md` for system details
3. 🚀 Try your first SPEC-First workflow:
   ```bash
   ./moai.sh /moai:0 "Create a REST API specification for user management"
   ```

### Learn More
- **Installation Guide**: `02-INSTALLATION.md` - Detailed installation options
- **Korean Setup**: `03-KOREAN-SETUP.md` - Complete Korean configuration
- **Verification**: `04-VERIFICATION.md` - 10-point validation checklist
- **Troubleshooting**: `05-TROUBLESHOOTING.md` - Common issues and solutions

### Advanced Usage
- **API Reference**: `docs/api/moai-adk-api.md` - Full agent documentation
- **AI Documentation**: `ai_docs/` - Machine-readable guides
- **Examples**: `examples/` - Sample workflows and use cases

---

## 🆘 Quick Troubleshooting

### Python Version Issues
```bash
# Check Python version
python3 --version

# If wrong version, use pyenv:
pyenv install 3.12.0
pyenv global 3.12.0
```

### UV Not Found
```bash
# Reinstall UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Add to PATH
export PATH="$HOME/.local/bin:$PATH"
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
```

### Virtual Environment Issues
```bash
# Remove and recreate
rm -rf .venv
uv venv --python 3.12
source .venv/bin/activate
```

### Korean Font Not Working
```bash
# Verify D2Coding installation
fc-list | grep -i d2coding

# If missing:
brew install --cask font-d2coding

# Restart terminal
```

For detailed troubleshooting, see `05-TROUBLESHOOTING.md`.

---

## 📞 Support & Resources

- **Documentation**: `/docs` directory
- **Issues**: Report bugs and feature requests
- **Community**: Join our Discord/Slack
- **Updates**: Check GitHub releases

---

## 🎉 Success!

You've successfully installed MoAI-ADK! Start building with SPEC-First methodology and leverage 26 specialized agents for your development workflow.

**First Command to Try**:
```bash
source .venv/bin/activate
./moai.sh /moai:0 "Create specification for a todo list app"
```

Happy coding! 🚀🇰🇷
