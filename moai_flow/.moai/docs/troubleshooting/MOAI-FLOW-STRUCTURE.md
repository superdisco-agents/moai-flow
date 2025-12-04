# MoAI Flow Integration - Directory Structure

## Phase 1 Complete: Directory Creation

Created on: 2025-11-30

### Directory Tree

```
.claude/
├── moai-flow-config.json                   # MoAI Flow configuration file
├── agents/
│   └── moai-flow/                          # MoAI Flow agent definitions (empty, ready for Phase 2)
├── commands/
│   └── moai-flow/                          # MoAI Flow slash commands (empty, ready for Phase 2)
├── hooks/
│   └── moai-flow/                          # MoAI Flow hook scripts (empty, ready for Phase 2)
├── output-styles/
│   └── moai-flow/                          # MoAI Flow output styles (empty, ready for Phase 2)
└── skills/
    ├── moai-flow-coordination/
    │   ├── SKILL.md                        # ✅ Created
    │   ├── modules/                        # Ready for content extraction
    │   └── examples/                       # Ready for examples
    ├── moai-flow-memory/
    │   ├── SKILL.md                        # ✅ Created
    │   ├── modules/                        # Ready for content extraction
    │   └── examples/                       # Ready for examples
    ├── moai-flow-optimization/
    │   ├── SKILL.md                        # ✅ Created
    │   ├── modules/                        # Ready for content extraction
    │   └── examples/                       # Ready for examples
    └── moai-flow-github/
        ├── SKILL.md                        # ✅ Created
        ├── modules/                        # Ready for content extraction
        └── examples/                       # Ready for examples
```

## Configuration Files

### moai-flow-config.json

Location: `/Users/rdmtv/Documents/claydev-local/agent-os-v2/moai-adk/.claude/moai-flow-config.json`

**Purpose**: Centralized configuration for MoAI Flow integration, separate from Claude Code's strict settings.json schema.

**Contents**:
- Enabled status and version tracking
- Agent registry (4 agents)
- Command registry (4 commands)
- Skill registry (4 skills)
- Directory path mappings

## Skill Definitions

### 1. moai-flow-coordination

**Purpose**: Multi-agent coordination patterns, swarm orchestration, and intelligent task delegation

**Capabilities**:
- Swarm Orchestration
- Task Delegation
- Consensus Mechanisms
- Topology Management

**Status**: ✅ Structure created, ready for module extraction

---

### 2. moai-flow-memory

**Purpose**: Distributed memory management, context persistence, and knowledge sharing

**Capabilities**:
- Distributed Memory
- Context Persistence
- Knowledge Sharing
- State Management

**Status**: ✅ Structure created, ready for module extraction

---

### 3. moai-flow-optimization

**Purpose**: Performance optimization, bottleneck detection, and resource allocation

**Capabilities**:
- Bottleneck Detection
- Performance Monitoring
- Resource Allocation
- Adaptive Scaling

**Status**: ✅ Structure created, ready for module extraction

---

### 4. moai-flow-github

**Purpose**: GitHub workflow integration for multi-agent systems

**Capabilities**:
- Multi-Agent PR Management
- Collaborative Review
- Workflow Automation
- Issue Triage

**Status**: ✅ Structure created, ready for module extraction

---

## Validation Results

### Directory Count

```bash
Total directories created: 18
├── 4 skill directories
├── 8 subdirectories (modules + examples)
└── 4 moai-flow workspace directories
```

### File Count

```bash
Files created: 5
├── 1 configuration file (moai-flow-config.json)
└── 4 skill definition files (SKILL.md)
```

### Size Summary

```bash
Total lines in SKILL.md files: 88 lines
Average per skill: 22 lines
```

## Next Steps (Phase 2)

1. **Extract Modules from moai-ir-deck**:
   - Coordination patterns → moai-flow-coordination/modules/
   - Memory management → moai-flow-memory/modules/
   - Optimization patterns → moai-flow-optimization/modules/
   - GitHub integration → moai-flow-github/modules/

2. **Create Agent Definitions**:
   - coordinator-swarm.md
   - optimizer-bottleneck.md
   - analyzer-consensus.md
   - healer-self.md

3. **Create Slash Commands**:
   - swarm-init.md
   - swarm-status.md
   - topology-switch.md
   - consensus-request.md

4. **Create Hooks**:
   - Pre/Post coordination hooks
   - Memory persistence hooks
   - Optimization monitoring hooks

## Integration Notes

### Why Separate Configuration?

Claude Code's `settings.json` has strict schema validation and doesn't support custom fields. Therefore:

- ✅ Created `moai-flow-config.json` for MoAI Flow-specific configuration
- ✅ Keeps existing settings.json intact
- ✅ Allows future extension without schema conflicts

### Compatibility

This structure follows the same pattern as moai-ir-deck:
- Agent definitions in `.claude/agents/`
- Commands in `.claude/commands/`
- Skills in `.claude/skills/`
- Configuration in separate JSON file

---

**Phase 1 Status**: ✅ **COMPLETE**

**Ready for**: Phase 2 (Skills Extraction)
