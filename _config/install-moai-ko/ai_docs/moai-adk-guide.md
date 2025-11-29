# MoAI-ADK Guide (AI Documentation)

**Version**: 1.0.0
**Last Updated**: November 29, 2025
**Target**: AI Assistants and Automated Tools

## Quick Summary

MoAI-ADK (Mixture of Agents - Agent Development Kit) is a SPEC-First/TDD development framework with 26 specialized agents and optional Korean language support.

**Key Features**:
- 🔧 SPEC-First methodology (systematic development from specification to completion)
- 🧪 Test-Driven Development workflow
- 👨‍💻 Full-stack development agents
- 📊 Code analysis and refactoring tools
- 🇰🇷 Korean language support

**Requirements**:
- Python 3.11+ (3.13 recommended)
- UV package manager (0.5.0+)
- 500+ MB disk space

---

## Installation Quick Start

### 3-Step Installation

```bash
# Step 1: Install UV package manager
curl -LsSf https://astral.sh/uv/install.sh | sh

# Step 2: Create virtual environment
cd /path/to/moai-adk/_config/install-moai-ko
uv venv --python 3.13
source .venv/bin/activate

# Step 3: Install dependencies and configure
uv pip install -r requirements.txt
python scripts/configure-agents.py

# Verify installation
./moai.sh --help
```

### Automated Installation

```bash
# Run installation script (interactive)
chmod +x install-moai-ko.sh
./install-moai-ko.sh

# Follow prompts:
# 1. Choose UV installation (recommended)
# 2. Select Python version (3.13 recommended)
# 3. Optional: Enable Korean support
```

---

## SPEC-First Methodology

SPEC-First is a systematic development approach with 5 phases:

### Phase 0: Specification (`/moai:0`)

Transform requirements into formal specifications.

**Usage**:
```bash
./moai.sh /moai:0 "Create a REST API for user management"
```

**Output**: Detailed specification document with:
- Functional requirements
- Non-functional requirements
- User stories
- Acceptance criteria

### Phase 1: Pseudocode (`/moai:1`)

Generate algorithmic pseudocode from specification.

**Usage**:
```bash
./moai.sh /moai:1 "$(cat specification.txt)"
```

**Output**: High-level algorithm design in pseudocode format.

### Phase 2: Architecture (`/moai:2`)

Design system architecture and component structure.

**Usage**:
```bash
./moai.sh /moai:2 "$(cat specification.txt)"
```

**Output**: Architecture diagrams, technology stack, design patterns.

### Phase 3: Refinement (`/moai:3`)

Refine and improve specifications for clarity and completeness.

**Usage**:
```bash
./moai.sh /moai:3 "$(cat specification.txt)"
```

**Output**: Enhanced specification with edge cases and improvements.

### Phase 4: Completion (`/moai:4`)

Validate specification completeness and readiness.

**Usage**:
```bash
./moai.sh /moai:4 "$(cat specification.txt)"
```

**Output**: Completeness checklist and implementation readiness report.

---

## 26 Agents Reference

### SPEC-First Agents (0-4)

| Agent | Command | Purpose |
|-------|---------|---------|
| Specification | `/moai:0` | Create formal specifications |
| Pseudocode | `/moai:1` | Generate algorithmic pseudocode |
| Architecture | `/moai:2` | Design system architecture |
| Refinement | `/moai:3` | Refine and improve specs |
| Completion | `/moai:4` | Validate completeness |

### TDD Agents (10-14)

| Agent | Command | Purpose |
|-------|---------|---------|
| Test Specification | `/moai:10` | Define test requirements |
| Test Implementation | `/moai:11` | Generate test code |
| Code Implementation | `/moai:12` | Implement code to pass tests |
| Test Validation | `/moai:13` | Validate test coverage |
| Integration | `/moai:14` | Integration testing |

### Development Agents (20-24)

| Agent | Command | Purpose |
|-------|---------|---------|
| Frontend Developer | `/moai:20` | Build UI components |
| Backend Developer | `/moai:21` | Implement server logic |
| API Developer | `/moai:22` | Design and implement APIs |
| Database Developer | `/moai:23` | Design schemas and queries |
| DevOps Engineer | `/moai:24` | Setup deployment and CI/CD |

### Analysis Agents (30-34)

| Agent | Command | Purpose |
|-------|---------|---------|
| Code Reviewer | `/moai:30` | Perform code review |
| Security Analyst | `/moai:31` | Analyze security vulnerabilities |
| Performance Analyst | `/moai:32` | Optimize performance |
| Refactoring Agent | `/moai:33` | Suggest code improvements |
| Documentation Agent | `/moai:34` | Generate documentation |

---

## Common Workflows

### Complete SPEC-First Workflow

```bash
# Create project directory
mkdir -p outputs/{spec,code,tests}

# Phase 0: Specification
./moai.sh /moai:0 "Build a todo list web app with user auth" > outputs/spec/specification.txt

# Phase 1: Pseudocode
./moai.sh /moai:1 "$(cat outputs/spec/specification.txt)" > outputs/spec/pseudocode.txt

# Phase 2: Architecture
./moai.sh /moai:2 "$(cat outputs/spec/specification.txt)" > outputs/spec/architecture.txt

# Phase 3: Refinement
./moai.sh /moai:3 "$(cat outputs/spec/specification.txt)" > outputs/spec/refined-spec.txt

# Phase 4: Completion check
./moai.sh /moai:4 "$(cat outputs/spec/refined-spec.txt)" > outputs/spec/completion-report.txt
```

### TDD Workflow

```bash
# Generate test specification
./moai.sh /moai:10 "User authentication feature" > outputs/tests/test-spec.txt

# Implement tests
./moai.sh /moai:11 "$(cat outputs/tests/test-spec.txt)" > outputs/tests/auth.test.js

# Implement code to pass tests
./moai.sh /moai:12 "$(cat outputs/tests/auth.test.js)" > outputs/code/auth.js

# Validate tests
./moai.sh /moai:13 "$(cat outputs/tests/auth.test.js)"
```

### Full-Stack Development

```bash
# Backend API
./moai.sh /moai:21 "REST API for user management" > backend/api.js

# Frontend UI
./moai.sh /moai:20 "User management UI with React" > frontend/UserManager.jsx

# Database schema
./moai.sh /moai:23 "User database schema with roles" > database/schema.sql

# DevOps setup
./moai.sh /moai:24 "Docker setup for Node.js app" > Dockerfile
```

### Code Review and Analysis

```bash
# Code review
./moai.sh /moai:30 "$(cat src/app.js)" > reviews/code-review.txt

# Security analysis
./moai.sh /moai:31 "$(cat src/app.js)" > reviews/security.txt

# Performance analysis
./moai.sh /moai:32 "$(cat src/app.js)" > reviews/performance.txt

# Refactoring suggestions
./moai.sh /moai:33 "$(cat src/app.js)" > reviews/refactoring.txt
```

---

## Korean Language Support

### Setup Overview

Korean support is **optional** and requires:
1. D2Coding font installation
2. Terminal configuration
3. Korean locale setup

### Quick Korean Setup

**macOS**:
```bash
# Install D2Coding font
brew tap homebrew/cask-fonts
brew install --cask font-d2coding

# Set locale
echo 'export LANG=ko_KR.UTF-8' >> ~/.zshrc
echo 'export LC_ALL=ko_KR.UTF-8' >> ~/.zshrc
source ~/.zshrc

# Configure terminal to use D2Coding font
```

**Linux**:
```bash
# Install D2Coding font
wget https://github.com/naver/d2codingfont/releases/download/VER1.3.2/D2Coding-Ver1.3.2-20180524.zip
unzip D2Coding-Ver1.3.2-20180524.zip
sudo cp D2Coding/D2Coding/*.ttf /usr/share/fonts/truetype/
sudo fc-cache -f -v

# Set locale
sudo locale-gen ko_KR.UTF-8
echo 'export LANG=ko_KR.UTF-8' >> ~/.bashrc
source ~/.bashrc
```

### Korean Command Examples

```bash
# SPEC-First in Korean
./moai.sh /moai:0 "간단한 할 일 목록 웹 애플리케이션 만들기"

# TDD in Korean
./moai.sh /moai:10 "사용자 인증 기능 테스트 명세서"

# Mixed Korean-English
./moai.sh /moai:0 "Create REST API for 사용자 관리 with JWT authentication"
```

### Testing Korean Support

```bash
# Test Korean character display
echo "한글 테스트: MoAI-ADK 설치 완료"

# If characters display correctly: ✅ Korean support working
# If boxes appear (□□□): ❌ Need to install D2Coding font

# Test MoAI-ADK with Korean
./moai.sh /moai:0 "테스트 사양" > outputs/korean-test.txt
cat outputs/korean-test.txt
```

**For detailed Korean setup**, see: `ai_docs/korean-setup.md`

---

## Configuration

### Environment Variables

```bash
# Core configuration
export MOAI_HOME="/path/to/moai-adk"
export MOAI_OUTPUT_DIR="outputs"
export MOAI_LOG_LEVEL="INFO"

# Agent configuration
export MOAI_MAX_CONCURRENT_AGENTS=5
export MOAI_AGENT_TIMEOUT=300

# Korean support
export LANG=ko_KR.UTF-8
export PYTHONUTF8=1

# Optional: AI provider API keys
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
```

### Configuration File (`config/moai.yaml`)

```yaml
general:
  output_directory: outputs
  log_level: INFO

agents:
  max_concurrent: 5
  timeout: 300

language:
  default_locale: ko_KR.UTF-8
  korean_support_enabled: true

spec_first:
  phases:
    - specification
    - pseudocode
    - architecture
    - refinement
    - completion

tdd:
  test_framework: jest
  coverage_threshold: 80
```

---

## Common Commands

### List All Agents

```bash
./moai.sh /moai:list
# Output: All 26 agents with descriptions
```

### Get Help

```bash
# General help
./moai.sh /moai:help

# Specific agent help
./moai.sh /moai:help 0
```

### Version Information

```bash
./moai.sh /moai:version
# Output: MoAI-ADK version, Python version, dependencies
```

### Output Formats

```bash
# Default: Markdown output to stdout
./moai.sh /moai:0 "test"

# Save to file
./moai.sh /moai:0 "test" > specification.txt

# JSON format
./moai.sh /moai:0 "test" --format json > spec.json

# YAML format
./moai.sh /moai:2 "test" --format yaml > architecture.yaml
```

---

## Troubleshooting Quick Reference

### Python Version Error

```bash
# Error: Python 3.11+ required
# Solution: Install correct Python
pyenv install 3.13.0
pyenv local 3.13.0
rm -rf .venv
uv venv --python 3.13
```

### UV Not Found

```bash
# Error: uv: command not found
# Solution: Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"
```

### Import Errors

```bash
# Error: ModuleNotFoundError
# Solution: Activate virtual environment
source .venv/bin/activate
uv pip install -r requirements.txt
```

### Korean Characters as Boxes

```bash
# Error: Korean text shows as □□□
# Solution: Install D2Coding font
brew install --cask font-d2coding  # macOS
# Then configure terminal font to D2Coding
# Restart terminal
```

### Agent Not Found

```bash
# Error: Agent /moai:0 not found
# Solution: Configure agents
python scripts/configure-agents.py
./moai.sh /moai:list  # Verify agents
```

---

## Best Practices

### 1. Always Start with Specification

```bash
# Good: Start with /moai:0
./moai.sh /moai:0 "detailed requirements" > spec.txt

# Then proceed to other phases
./moai.sh /moai:1 "$(cat spec.txt)" > pseudocode.txt
```

### 2. Save Intermediate Results

```bash
# Create organized output structure
mkdir -p outputs/{spec,tests,code,docs}

# Save each phase
./moai.sh /moai:0 "req" > outputs/spec/initial.txt
./moai.sh /moai:1 "$(cat outputs/spec/initial.txt)" > outputs/spec/pseudocode.txt
```

### 3. Use Piping for Workflows

```bash
# Chain agents together
./moai.sh /moai:0 "requirements" | ./moai.sh /moai:1
```

### 4. Validate with Multiple Agents

```bash
# Review code from multiple perspectives
./moai.sh /moai:30 "$(cat src/app.js)" > reviews/code.txt
./moai.sh /moai:31 "$(cat src/app.js)" > reviews/security.txt
./moai.sh /moai:32 "$(cat src/app.js)" > reviews/performance.txt
```

### 5. Korean-English Mixing

```bash
# You can naturally mix languages
./moai.sh /moai:0 "Create REST API for 사용자 관리 with JWT authentication"
```

---

## Performance Tips

### Concurrent Agent Execution

```bash
# Set max concurrent agents
export MOAI_MAX_CONCURRENT_AGENTS=5

# Agents will run in parallel when possible
```

### Caching

```bash
# Enable caching for faster repeated operations
export MOAI_CACHE_ENABLED=true
export MOAI_CACHE_DIR=".moai/cache"
```

### Timeout Adjustment

```bash
# Increase timeout for long-running tasks
export MOAI_AGENT_TIMEOUT=600  # 10 minutes
```

---

## Integration Examples

### Git Integration

```bash
# Generate specification and commit
./moai.sh /moai:0 "Feature requirements" > spec.txt
git add spec.txt
git commit -m "Add feature specification"
```

### CI/CD Integration

```yaml
# .github/workflows/moai-spec.yml
name: Generate Specification
on: [push]
jobs:
  spec:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup MoAI-ADK
        run: |
          curl -LsSf https://astral.sh/uv/install.sh | sh
          uv venv && source .venv/bin/activate
          uv pip install -r requirements.txt
      - name: Generate Spec
        run: ./moai.sh /moai:0 "$(cat requirements.md)" > specification.txt
```

### Docker Integration

```dockerfile
# Dockerfile for MoAI-ADK
FROM python:3.13-slim

WORKDIR /moai-adk

# Install UV
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Copy files
COPY requirements.txt .
COPY moai.sh .
COPY scripts/ scripts/
COPY agents/ agents/

# Install dependencies
RUN uv venv && \
    . .venv/bin/activate && \
    uv pip install -r requirements.txt

# Configure agents
RUN python scripts/configure-agents.py

ENTRYPOINT ["./moai.sh"]
```

---

## Related Documentation

- **Full Installation Guide**: `../docs/02-INSTALLATION.md`
- **Korean Setup**: `korean-setup.md` (this directory)
- **UV Guide**: `uv-inline-dependencies.md` (this directory)
- **API Reference**: `../docs/api/moai-adk-api.md`
- **Troubleshooting**: `../docs/05-TROUBLESHOOTING.md`

---

## Version Information

- **MoAI-ADK**: 1.0.0
- **Python**: 3.11+ (3.13 recommended)
- **UV**: 0.5.0+
- **D2Coding Font**: 1.3.2 (for Korean support)
- **Documentation**: AI-optimized guide v1.0.0

---

**MoAI-ADK** - SPEC-First development with 26 specialized agents 🚀🇰🇷
