# MoAI-ADK Claude Code Integration

Complete Claude Code integration for MoAI-ADK installation system with Korean language support as a first-class feature.

## Overview

This integration provides a comprehensive installation and validation framework for MoAI-ADK, featuring:

- **4 Slash Commands**: Progressive disclosure-based installation workflows
- **2 Specialized Agents**: Installation orchestration and quality assurance
- **Korean Support**: First-class Korean language and font support
- **26 AI Agents**: Complete agent verification and validation
- **SPEC-First Approach**: Specification-driven development methodology
- **TDD Integration**: Test-driven development workflows

## Architecture

### Component Structure

```
.claude/
├── commands/                    # 4 slash commands
│   ├── prime.md                # Context loader (~80 lines)
│   ├── install.md              # Standard installation (~130 lines)
│   ├── install-korean.md       # Korean installation (~150 lines)
│   └── verify.md               # Validation (~200 lines)
├── agents/                      # 2 specialized agents
│   ├── installer.md            # Installation orchestrator (~320 lines, Sonnet 4.5)
│   └── validator.md            # QA validator (~400 lines, Haiku 4.5)
├── settings.json               # Configuration registry
└── COMMANDS_AND_AGENTS.md      # This file (~350 lines)
```

### Progressive Disclosure Pattern

All commands and agents follow the beyond-MCP progressive disclosure pattern with 5 levels:

1. **Level 1**: Quick Start (immediate action)
2. **Level 2**: Overview (context and what's included)
3. **Level 3**: Detailed Steps (full workflow)
4. **Level 4**: Troubleshooting (error recovery)
5. **Level 5**: Expert Mode (advanced customization)

## Slash Commands

### 1. `/prime` - Context Loader

**Purpose**: Load MoAI-ADK installation context without performing installation

**Lines**: ~80 lines

**Usage**:
```bash
/prime
```

**What It Provides**:
- Quick overview of MoAI-ADK system
- 26 AI agents breakdown by category
- Installation approaches available
- System architecture explanation
- Technology stack details

**Progressive Disclosure**:
- **Level 1**: Quick overview (what, why, where, how)
- **Level 2**: System architecture and directory structure
- **Level 3**: Installation workflows available
- **Level 4**: Commands and agents reference
- **Level 5**: SPEC-First methodology and technical details

**When to Use**:
- Before starting installation
- To understand available options
- To review system architecture
- To share context with team members

### 2. `/install` - Standard Installation

**Purpose**: Execute complete MoAI-ADK installation without Korean support

**Lines**: ~130 lines

**Usage**:
```bash
/install
```

**What It Does**:
- Verifies Python 3.13+ installation
- Checks uv package manager
- Creates virtual environment
- Installs all dependencies
- Verifies 26 agents
- Runs portability tests

**Progressive Disclosure**:
- **Level 1**: Quick start (immediate execution)
- **Level 2**: Pre-installation checklist
- **Level 3**: Detailed 5-phase workflow
- **Level 4**: Troubleshooting guide
- **Level 5**: Expert mode (manual installation)

**Phases**:
1. Environment preparation
2. Repository setup
3. Dependency installation
4. Agent verification
5. Post-installation validation

**Duration**: 5-10 minutes

**Success Criteria**:
- Python 3.13+ active
- 26/26 agents verified
- No import errors
- Basic tests passing

### 3. `/install-korean` - Korean Support Installation

**Purpose**: Execute MoAI-ADK installation with Korean fonts, terminal, and locale

**Lines**: ~150 lines

**Usage**:
```bash
/install-korean
```

**What It Does**:
- All standard installation steps
- Installs D2Coding font (Korean monospace)
- Installs Noto Sans KR font (Korean UI)
- Configures Ghostty terminal
- Sets Korean locale (ko_KR.UTF-8)
- Tests Korean character rendering

**Progressive Disclosure**:
- **Level 1**: Quick start (immediate execution)
- **Level 2**: Korean support overview
- **Level 3**: Detailed 5-phase workflow
- **Level 4**: Korean-specific troubleshooting
- **Level 5**: Expert mode (custom Korean setup)

**Phases**:
1. Standard installation (inherits from `/install`)
2. Korean font installation
3. Ghostty terminal configuration
4. Korean locale configuration
5. Korean support validation

**Duration**: 10-15 minutes

**Korean Components**:
- **D2Coding**: Monospace font designed for Korean coding
- **Noto Sans KR**: Korean UI font
- **Ghostty**: Terminal with excellent Korean support
- **ko_KR.UTF-8**: Korean locale for proper encoding

**Success Criteria**:
- All standard criteria met
- D2Coding font installed
- Ghostty configured
- Korean locale active
- Korean rendering works

### 4. `/verify` - Installation Validation

**Purpose**: Comprehensive validation of MoAI-ADK installation

**Lines**: ~200 lines

**Usage**:
```bash
# Full validation
/verify

# Korean fonts check
/verify --korean-fonts true

# Quick validation
/verify --mode quick
```

**What It Validates**:
- Python environment (version, uv, Git)
- All dependencies installed
- 26 agents importable
- Korean support (if installed)
- Portability tests
- Integration smoke tests

**Progressive Disclosure**:
- **Level 1**: Quick summary (pass/fail per category)
- **Level 2**: Category details (specific checks)
- **Level 3**: Issue diagnosis (failures with fixes)
- **Level 4**: Troubleshooting guide
- **Level 5**: Expert mode (custom validation)

**Validation Phases**:
1. Environment checks
2. Dependency validation
3. Agent verification (26 agents)
4. Korean support validation
5. Portability testing
6. Integration smoke tests
7. Report generation

**Duration**: 2-5 minutes

**Outputs**:
- Console summary
- `/tmp/moai-adk-validation-report.txt`
- `/tmp/portability_results.txt` (if tests run)

## Specialized Agents

### 1. `installer` - Installation Orchestrator

**Model**: Claude Sonnet 4.5 (claude-sonnet-4-5-20250929)

**Lines**: ~320 lines

**Role**: Orchestrate complete MoAI-ADK installation workflows

**Capabilities**:
- Installation orchestration
- Dependency management
- Environment configuration
- Korean localization
- Error recovery

**Modes**:

**Standard Mode**:
```bash
installer --mode standard --validate true
```
- Verifies system requirements
- Installs MoAI-ADK via uv
- Validates 26 agents
- Runs basic tests

**Korean Mode**:
```bash
installer --mode korean --fonts d2coding --terminal ghostty
```
- All standard mode steps
- Installs Korean fonts
- Configures Ghostty
- Sets Korean locale
- Tests Korean rendering

**Error Handling**:
- Python version mismatch → Suggest upgrade or pyenv
- uv installation failed → Install Rust first
- Virtual env conflicts → Remove and recreate
- Agent import failures → Reinstall with verbose output
- Korean font issues → Provide manual download links
- Ghostty not available → Suggest alternatives

**Coordination**:
- Spawns `validator` agent after installation
- Passes installation context for validation
- Updates Claude Flow hooks (pre-task, post-task)
- Stores configuration in memory

**Output Format**:
- Progress indicators: ✓ (success), ✗ (error), ⚠ (warning)
- Clear phase headers
- Detailed error messages with fixes
- Next steps guidance
- Summary of installed components

### 2. `validator` - QA Validator

**Model**: Claude Haiku 4.5 (claude-haiku-4-5-20250513)

**Lines**: ~400 lines

**Role**: Comprehensive installation validation and quality assurance

**Capabilities**:
- Installation validation
- Agent verification
- Korean support testing
- Portability testing
- Report generation

**Validation Modes**:

**Quick Mode** (< 1 min):
```bash
validator --mode quick
```
- Environment check only
- Agent count verification
- No tests

**Standard Mode** (2-3 min):
```bash
validator --mode standard
```
- Full environment validation
- All agent verification
- Basic integration tests

**Full Mode** (3-5 min):
```bash
validator --mode full --korean-fonts auto
```
- Complete environment check
- All 26 agents verified
- Korean support (auto-detect)
- Portability test suite
- Integration smoke tests
- Comprehensive report

**Korean-Only Mode** (1 min):
```bash
validator --mode korean
```
- Focus on Korean support
- Font verification
- Locale testing
- Character rendering

**Validation Categories**:

1. **Environment**:
   - Python 3.13+
   - uv package manager
   - Virtual environment
   - Git installation
   - Disk space

2. **Dependencies**:
   - MoAI-ADK package
   - Core packages (click, pydantic, rich, typer, httpx)
   - Optional packages

3. **Agents** (26 total):
   - Core Coordinators (5)
   - Consensus Agents (6)
   - Performance Agents (4)
   - Development Agents (5)
   - Specialized Agents (6)

4. **Korean Support**:
   - D2Coding font
   - Noto Sans KR font
   - Ghostty configuration
   - Korean locale (ko_KR.UTF-8)
   - Character rendering

5. **Portability**:
   - Cross-platform compatibility
   - Path resolution
   - File operations
   - Environment variables

6. **Integration**:
   - Agent imports
   - CLI availability
   - Basic workflows

**Report Generation**:
- Summary (pass/fail per category)
- Detailed results
- Recommendations
- Fix instructions
- Next steps

**Coordination**:
- Receives context from `installer`
- Validates claimed installation
- Reports discrepancies
- Suggests fixes
- Updates hooks with status

## Configuration Registry

The `settings.json` file registers all commands, agents, and workflows:

```json
{
  "commands": [
    { "name": "prime", "path": "commands/prime.md", ... },
    { "name": "install", "path": "commands/install.md", ... },
    { "name": "install-korean", "path": "commands/install-korean.md", ... },
    { "name": "verify", "path": "commands/verify.md", ... }
  ],
  "agents": [
    { "name": "installer", "model": "claude-sonnet-4-5-20250929", ... },
    { "name": "validator", "model": "claude-haiku-4-5-20250513", ... }
  ],
  "skills": [
    { "name": "moai-adk-installer", "commands": [...], "agents": [...] }
  ],
  "workflows": [
    { "name": "standard-installation", "steps": [...] },
    { "name": "korean-installation", "steps": [...] },
    { "name": "validation-only", "steps": [...] }
  ]
}
```

## Workflows

### Workflow 1: Standard Installation

**Steps**:
1. `/prime` - Load context
2. `/install` - Execute installation
3. `/verify` - Validate

**Duration**: ~10 minutes

**Command Chaining**:
```bash
/prime && /install && /verify
```

### Workflow 2: Korean Installation

**Steps**:
1. `/prime` - Load context
2. `/install-korean` - Execute with Korean support
3. `/verify --korean-fonts true` - Validate Korean setup

**Duration**: ~15 minutes

**Command Chaining**:
```bash
/prime && /install-korean && /verify --korean-fonts true
```

### Workflow 3: Validation Only

**Steps**:
1. `/verify` - Validate existing installation

**Duration**: ~5 minutes

**Use Case**: After manual installation or to check status

## Korean Support Details

### Fonts

**D2Coding**:
- Monospace font designed for Korean coding
- Proper Hangul character spacing
- Clear distinction between similar characters
- Optimized for terminal use

**Installation**:
- macOS: `brew install --cask font-d2coding`
- Linux: Download from GitHub releases

**Noto Sans KR**:
- Korean UI font from Google Fonts
- Variable font with multiple weights
- Used for non-terminal Korean text

### Terminal Configuration

**Ghostty**:
- Modern GPU-accelerated terminal
- Excellent Korean font rendering
- Native ligature support
- Cross-platform (macOS, Linux)

**Configuration** (`~/.config/ghostty/config`):
```
font-family = "D2Coding"
font-size = 14
locale = "ko_KR.UTF-8"
theme = "tokyo-night"
```

### Locale Setup

**Environment Variables**:
```bash
export LC_ALL=ko_KR.UTF-8
export LANG=ko_KR.UTF-8
export LANGUAGE=ko_KR.UTF-8
```

**Added to**: `~/.zshrc` or `~/.bashrc`

**Verification**:
```bash
locale  # Should show ko_KR.UTF-8
```

### Character Rendering Test

The installation includes a Korean rendering test:

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

print("MoAI-ADK 한글 지원 테스트")
print("Agent: 조정자 (Coordinator)")
print("한글: 가나다라마바사아자차카타파하")
```

## Agent Coordination

### Installation Flow

```mermaid
sequencer
  User -> /install-korean: Execute command
  /install-korean -> installer: Spawn agent
  installer -> System: Verify requirements
  installer -> System: Install dependencies
  installer -> System: Install Korean fonts
  installer -> System: Configure Ghostty
  installer -> System: Set locale
  installer -> validator: Spawn for validation
  validator -> System: Run validation
  validator -> User: Report results
```

### Hooks Integration

**Pre-Task**:
```bash
npx claude-flow@alpha hooks pre-task \
  --description "MoAI-ADK installation" \
  --agent "installer"
```

**Post-Task**:
```bash
npx claude-flow@alpha hooks post-task \
  --task-id "moai-adk-install" \
  --status "success"
```

**Session Management**:
```bash
npx claude-flow@alpha hooks session-restore \
  --session-id "moai-adk-$(date +%s)"
```

## Success Criteria

### Standard Installation Success

- ✓ Python 3.13+ environment active
- ✓ uv package manager installed
- ✓ Virtual environment created
- ✓ All dependencies installed
- ✓ 26/26 agents verified
- ✓ No import errors
- ✓ Basic tests passing

### Korean Installation Success

- ✓ All standard criteria met
- ✓ D2Coding font installed
- ✓ Noto Sans KR installed
- ✓ Ghostty terminal configured
- ✓ Korean locale (ko_KR.UTF-8) active
- ✓ Korean characters render correctly
- ✓ Korean input method available

### Validation Success

- ✓ Environment: PASS
- ✓ Dependencies: PASS
- ✓ Agents: PASS (26/26)
- ✓ Korean Support: CONFIGURED (if applicable)
- ✓ Portability: PASS
- ✓ Integration: PASS

## Troubleshooting

### Common Issues

**Issue**: Python version mismatch
**Fix**: Install Python 3.13+ or use pyenv

**Issue**: uv installation failed
**Fix**: Install Rust first: `curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh`

**Issue**: Korean fonts not showing
**Fix**: Rebuild font cache: `fc-cache -f -v`

**Issue**: Ghostty not found
**Fix**: Install: `brew install --cask ghostty` (macOS)

**Issue**: Agent import failures
**Fix**: Reinstall: `uv sync --reinstall`

### Validation Reports

**Location**: `/tmp/moai-adk-validation-report.txt`

**Contains**:
- Summary (pass/fail per category)
- Environment details
- Agent verification results
- Korean support status
- Recommendations
- Next steps

## File Metrics

| File | Lines | Purpose |
|------|-------|---------|
| `commands/prime.md` | ~80 | Context loader |
| `commands/install.md` | ~130 | Standard installation |
| `commands/install-korean.md` | ~150 | Korean installation |
| `commands/verify.md` | ~200 | Validation |
| `agents/installer.md` | ~320 | Installation orchestration |
| `agents/validator.md` | ~400 | QA validation |
| `settings.json` | ~150 | Configuration registry |
| `COMMANDS_AND_AGENTS.md` | ~350 | Documentation (this file) |

**Total**: ~1,780 lines of comprehensive installation framework

## Next Steps

After installation and validation:

1. **Activate Environment**:
   ```bash
   source .venv/bin/activate
   ```

2. **Explore Agents**:
   ```bash
   python -m moai_adk.agents list
   ```

3. **Run Examples**:
   ```bash
   python -m moai_adk.examples
   ```

4. **Read Documentation**:
   ```bash
   cat docs/README.md
   ```

5. **Test Korean Support** (if installed):
   ```bash
   # Open Ghostty terminal
   ghostty

   # Test Korean rendering
   python -c "print('한글 테스트: MoAI-ADK')"
   ```

## Version History

- **v1.0.0** (2025-11-29): Initial release
  - 4 slash commands
  - 2 specialized agents
  - Korean support as first-class feature
  - Progressive disclosure pattern
  - Comprehensive validation

---

**Documentation**: Complete Claude Code integration for MoAI-ADK
**Korean Support**: First-class feature (fonts, terminal, locale)
**Pattern**: Beyond-MCP progressive disclosure (5 levels)
**Agents**: 26 AI agents verified and validated
**Approach**: SPEC-First + TDD + Progressive Disclosure
