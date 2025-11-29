---
description: Execute standard MoAI-ADK installation workflow
tags: [moai, install, automation]
---

# Install: Standard MoAI-ADK Installation

Execute complete MoAI-ADK installation with system validation and agent verification.

## Progressive Disclosure Structure

### Level 1: Quick Start (Immediate Action)

Execute the `installer` agent to perform standard installation:

```bash
# Spawn installer agent for standard installation
installer --mode standard --validate true
```

**Expected Duration**: 5-10 minutes
**What Gets Installed**:
- MoAI-ADK Python package
- 26 AI agents
- Core dependencies
- Development tools

### Level 2: Pre-Installation Checklist

**System Requirements**:
- Python 3.13+ installed
- uv package manager (auto-installed if missing)
- Git 2.0+
- 500 MB disk space
- Internet connection

**Quick Verification**:
```bash
python --version  # Should be 3.13+
git --version     # Should be 2.0+
which uv || curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Level 3: Installation Workflow (Detailed Steps)

**Phase 1: Environment Preparation**
```bash
# Verify system requirements
npx claude-flow@alpha hooks pre-task --description "MoAI-ADK standard installation"

# Check Python version
python_version=$(python --version 2>&1 | awk '{print $2}')
if [[ ! "$python_version" =~ ^3\.(13|14|15) ]]; then
  echo "Error: Python 3.13+ required, found $python_version"
  exit 1
fi

# Verify uv installation
if ! command -v uv &> /dev/null; then
  echo "Installing uv package manager..."
  curl -LsSf https://astral.sh/uv/install.sh | sh
  source $HOME/.cargo/env
fi

# Verify Git installation
if ! command -v git &> /dev/null; then
  echo "Error: Git is required but not installed"
  exit 1
fi
```

**Phase 2: Repository Setup**
```bash
# Navigate to installation directory
cd /Users/rdmtv/Documents/claydev-local/agent-os-v2/moai-adk/_config/install-moai-ko

# Ensure clean state
if [ -d ".venv" ]; then
  echo "Removing existing virtual environment..."
  rm -rf .venv
fi

# Verify project files exist
required_files=("pyproject.toml" "uv.lock")
for file in "${required_files[@]}"; do
  if [ ! -f "$file" ]; then
    echo "Error: Required file $file not found"
    exit 1
  fi
done
```

**Phase 3: Dependency Installation**
```bash
# Create virtual environment and install dependencies
echo "Installing MoAI-ADK dependencies..."
uv sync --all-extras

# Activate virtual environment
source .venv/bin/activate

# Verify installation
python -c "import moai_adk; print(f'MoAI-ADK version: {moai_adk.__version__}')"
```

**Phase 4: Agent Verification**
```bash
# Verify all 26 agents are available
echo "Verifying agent availability..."

# Expected agent count
expected_agents=26

# Count available agents (implementation-specific)
available_agents=$(python -c "from moai_adk import agents; print(len(agents.list_all()))")

if [ "$available_agents" -eq "$expected_agents" ]; then
  echo "✓ All $expected_agents agents verified"
else
  echo "⚠ Warning: Expected $expected_agents agents, found $available_agents"
fi
```

**Phase 5: Post-Installation Validation**
```bash
# Run basic portability tests
echo "Running portability tests..."
uv run pytest tests/portability/ -v

# Update coordination hooks
npx claude-flow@alpha hooks post-task --task-id "moai-adk-install"

# Generate installation report
echo "Installation completed successfully!"
echo "Next steps: Run /verify to validate installation"
```

### Level 4: Troubleshooting Guide

**Common Issues**:

1. **Python Version Mismatch**
   ```bash
   Error: Python 3.13+ required
   Solution: Install Python 3.13 from python.org or use pyenv
   ```

2. **uv Installation Failed**
   ```bash
   Error: Could not install uv
   Solution: Install Rust toolchain first
   curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
   ```

3. **Virtual Environment Conflicts**
   ```bash
   Error: .venv already exists
   Solution: Remove and recreate
   rm -rf .venv && uv sync
   ```

4. **Missing Dependencies**
   ```bash
   Error: Could not resolve dependencies
   Solution: Update uv and retry
   uv self update && uv sync
   ```

5. **Agent Verification Failed**
   ```bash
   Error: Expected 26 agents, found fewer
   Solution: Check pyproject.toml entry points
   grep -A 30 'project.entry-points' pyproject.toml
   ```

### Level 5: Expert Mode (Manual Installation)

**For Advanced Users**:

```bash
# Manual installation with full control
cd /Users/rdmtv/Documents/claydev-local/agent-os-v2/moai-adk/_config/install-moai-ko

# Step 1: Create virtual environment
uv venv --python 3.13

# Step 2: Install dependencies individually
source .venv/bin/activate
uv pip install -e ".[dev,test]"

# Step 3: Verify each agent category
python -c "from moai_adk.agents import core; print(f'Core agents: {len(core.list_agents())}')"
python -c "from moai_adk.agents import consensus; print(f'Consensus agents: {len(consensus.list_agents())}')"
python -c "from moai_adk.agents import performance; print(f'Performance agents: {len(performance.list_agents())}')"

# Step 4: Run comprehensive tests
uv run pytest tests/ -v --cov=moai_adk --cov-report=html

# Step 5: Build documentation
uv run mkdocs build
```

## Post-Installation

**Verify Installation**:
```bash
/verify
```

**Test Korean Support** (optional):
```bash
/install-korean  # Adds Korean fonts and terminal config
```

**Start Development**:
```bash
source .venv/bin/activate
python -m moai_adk.cli --help
```

## Success Criteria

Installation is successful when:
- ✓ Python 3.13+ environment active
- ✓ All dependencies installed via uv
- ✓ 26 agents verified and available
- ✓ Portability tests passing
- ✓ No import errors or warnings

## Next Steps

1. Run `/verify` to validate installation
2. Explore agents: `python -m moai_adk.agents list`
3. Run example workflows: `python -m moai_adk.examples`
4. Read documentation: `docs/README.md`

---

**Installation Type**: Standard (no Korean support)
**Estimated Time**: 5-10 minutes
**Agent**: `installer` (Sonnet 4.5)
