# MoAI-ADK Claude Code Integration

Complete Claude Code integration for MoAI-ADK installation with Korean support.

## Quick Start

```bash
# Load context
/prime

# Standard installation
/install

# Korean installation (recommended)
/install-korean

# Validate installation
/verify
```

## What's Included

### Slash Commands (4)

1. **`/prime`** (159 lines) - Load MoAI-ADK context
2. **`/install`** (241 lines) - Standard installation
3. **`/install-korean`** (422 lines) - Korean-enabled installation ⭐
4. **`/verify`** (534 lines) - Installation validation

### Specialized Agents (2)

1. **`installer`** (586 lines, Sonnet 4.5) - Installation orchestration
2. **`validator`** (712 lines, Haiku 4.5) - Quality assurance

### Configuration

- **`settings.json`** (135 lines) - Registry of commands, agents, workflows
- **`COMMANDS_AND_AGENTS.md`** (675 lines) - Complete documentation

**Total**: 3,464 lines of installation framework

## Features

- ✓ Progressive disclosure pattern (5 levels)
- ✓ Korean support as first-class feature
- ✓ 26 AI agents verification
- ✓ SPEC-First methodology
- ✓ Comprehensive error handling
- ✓ Automated validation
- ✓ Claude Flow hooks integration

## Korean Support

**Fonts**: D2Coding (monospace) + Noto Sans KR (UI)
**Terminal**: Ghostty with Korean configuration
**Locale**: ko_KR.UTF-8
**Rendering**: Full Hangul character support

## Installation Workflows

### Standard Installation (~10 min)
```bash
/prime && /install && /verify
```

### Korean Installation (~15 min)
```bash
/prime && /install-korean && /verify --korean-fonts true
```

### Validation Only (~5 min)
```bash
/verify
```

## Directory Structure

```
.claude/
├── commands/
│   ├── prime.md              # Context loader
│   ├── install.md            # Standard installation
│   ├── install-korean.md     # Korean installation
│   └── verify.md             # Validation
├── agents/
│   ├── installer.md          # Sonnet 4.5 installer
│   └── validator.md          # Haiku 4.5 validator
├── settings.json             # Configuration registry
├── COMMANDS_AND_AGENTS.md    # Complete documentation
└── README.md                 # This file
```

## Success Criteria

### Standard Installation
- ✓ Python 3.13+ environment
- ✓ 26/26 agents verified
- ✓ No import errors
- ✓ Tests passing

### Korean Installation
- ✓ All standard criteria
- ✓ D2Coding font installed
- ✓ Ghostty configured
- ✓ Korean locale active
- ✓ Korean rendering works

## Documentation

- **Overview**: `COMMANDS_AND_AGENTS.md`
- **Commands**: `commands/*.md`
- **Agents**: `agents/*.md`
- **Configuration**: `settings.json`

## Version

- **Version**: 1.0.0
- **Date**: 2025-11-29
- **Pattern**: Beyond-MCP Progressive Disclosure
- **Korean Support**: First-class feature

---

**Ready to install MoAI-ADK with precision and Korean support.**
