# MoAI-Flow Validation - File Path Reference

Quick reference for all validation-related files and directories.

---

## Validation Reports

All validation reports are located in:
```
/Users/rdmtv/Documents/claydev-local/agent-os-v2/moai-adk/.moai/reports/validation/
```

### Report Files

| File | Purpose | Format |
|------|---------|--------|
| `INDEX.md` | Report navigation and overview | Markdown |
| `QUICK-STATUS.txt` | Quick status card | ASCII text |
| `VALIDATION-SUMMARY.md` | Executive summary | Markdown |
| `phase8-validation-report-FINAL.md` | Full technical report | Markdown |
| `FILE-PATHS.md` | This file | Markdown |

### Test Data

| File | Purpose | Format |
|------|---------|--------|
| `../../temp/validation_results.json` | Raw test results | JSON |

---

## Modified Files

Files that were modified during validation:

### Python Module Exports

```
/Users/rdmtv/Documents/claydev-local/agent-os-v2/moai-adk/moai_flow/coordination/__init__.py
```

**Changes**:
- Added `QuorumAlgorithm` to imports (line 20)
- Added `WeightedAlgorithm` to imports (line 21)
- Added both to `__all__` exports (lines 74-75)

---

## MoAI-Flow Integration Structure

### Python Package

```
/Users/rdmtv/Documents/claydev-local/agent-os-v2/moai-adk/moai_flow/
├── core/
│   ├── __init__.py
│   ├── interfaces.py
│   └── swarm_coordinator.py
├── memory/
│   ├── __init__.py
│   ├── swarm_db.py
│   ├── semantic_memory.py
│   └── episodic_memory.py
├── optimization/
│   ├── __init__.py
│   ├── bottleneck_detector.py
│   ├── pattern_learner.py
│   └── self_healer.py
├── coordination/
│   ├── __init__.py
│   ├── consensus_manager.py
│   ├── conflict_resolver.py
│   ├── state_synchronizer.py
│   └── algorithms/
│       ├── __init__.py
│       ├── base.py
│       ├── raft_consensus.py
│       ├── quorum_consensus.py
│       ├── weighted_consensus.py
│       ├── gossip.py
│       ├── byzantine.py
│       └── crdt.py
└── patterns/
    ├── __init__.py
    └── pattern_collector.py
```

### Claude Code Integration

```
/Users/rdmtv/Documents/claydev-local/agent-os-v2/moai-adk/.claude/
├── agents/moai-flow/
│   ├── coordinator-swarm.md
│   ├── optimizer-bottleneck.md
│   ├── analyzer-consensus.md
│   └── healer-self.md
├── commands/moai-flow/
│   ├── swarm-init.md
│   ├── swarm-status.md
│   ├── topology-switch.md
│   └── consensus-request.md
└── hooks/moai-flow/
    ├── pre_swarm_task.py
    ├── post_swarm_task.py
    └── swarm_lifecycle.py
```

### Configuration

```
/Users/rdmtv/Documents/claydev-local/agent-os-v2/moai-adk/.moai/
├── config/
│   └── moai-flow.json
├── memory/moai-flow/
│   └── (session state files)
├── patterns/
│   └── (pattern collection files)
└── docs/moai-flow/
    ├── README.md
    ├── INTEGRATION.md
    └── HOOKS.md
```

---

## Test Coverage

### Category 1: Python Code (6 tests)

**Module Paths Tested**:
- `/Users/rdmtv/Documents/claydev-local/agent-os-v2/moai-adk/moai_flow/core/swarm_coordinator.py`
- `/Users/rdmtv/Documents/claydev-local/agent-os-v2/moai-adk/moai_flow/memory/swarm_db.py`
- `/Users/rdmtv/Documents/claydev-local/agent-os-v2/moai-adk/moai_flow/memory/semantic_memory.py`
- `/Users/rdmtv/Documents/claydev-local/agent-os-v2/moai-adk/moai_flow/memory/episodic_memory.py`
- `/Users/rdmtv/Documents/claydev-local/agent-os-v2/moai-adk/moai_flow/optimization/bottleneck_detector.py`
- `/Users/rdmtv/Documents/claydev-local/agent-os-v2/moai-adk/moai_flow/optimization/pattern_learner.py`
- `/Users/rdmtv/Documents/claydev-local/agent-os-v2/moai-adk/moai_flow/optimization/self_healer.py`
- `/Users/rdmtv/Documents/claydev-local/agent-os-v2/moai-adk/moai_flow/patterns/pattern_collector.py`

### Category 2: Claude Integration (11 tests)

**Agent Files**:
- `/Users/rdmtv/Documents/claydev-local/agent-os-v2/moai-adk/.claude/agents/moai-flow/coordinator-swarm.md`
- `/Users/rdmtv/Documents/claydev-local/agent-os-v2/moai-adk/.claude/agents/moai-flow/optimizer-bottleneck.md`
- `/Users/rdmtv/Documents/claydev-local/agent-os-v2/moai-adk/.claude/agents/moai-flow/analyzer-consensus.md`
- `/Users/rdmtv/Documents/claydev-local/agent-os-v2/moai-adk/.claude/agents/moai-flow/healer-self.md`

**Command Files**:
- `/Users/rdmtv/Documents/claydev-local/agent-os-v2/moai-adk/.claude/commands/moai-flow/swarm-init.md`
- `/Users/rdmtv/Documents/claydev-local/agent-os-v2/moai-adk/.claude/commands/moai-flow/swarm-status.md`
- `/Users/rdmtv/Documents/claydev-local/agent-os-v2/moai-adk/.claude/commands/moai-flow/topology-switch.md`
- `/Users/rdmtv/Documents/claydev-local/agent-os-v2/moai-adk/.claude/commands/moai-flow/consensus-request.md`

**Hook Files**:
- `/Users/rdmtv/Documents/claydev-local/agent-os-v2/moai-adk/.claude/hooks/moai-flow/pre_swarm_task.py`
- `/Users/rdmtv/Documents/claydev-local/agent-os-v2/moai-adk/.claude/hooks/moai-flow/post_swarm_task.py`
- `/Users/rdmtv/Documents/claydev-local/agent-os-v2/moai-adk/.claude/hooks/moai-flow/swarm_lifecycle.py`

### Category 3: State Management (5 tests)

**Configuration**:
- `/Users/rdmtv/Documents/claydev-local/agent-os-v2/moai-adk/.moai/config/moai-flow.json`

**Memory**:
- `/Users/rdmtv/Documents/claydev-local/agent-os-v2/moai-adk/.moai/memory/moai-flow/`

**Patterns**:
- `/Users/rdmtv/Documents/claydev-local/agent-os-v2/moai-adk/.moai/patterns/`

### Category 4: Configuration (4 tests)

**Config File**:
- `/Users/rdmtv/Documents/claydev-local/agent-os-v2/moai-adk/.moai/config/moai-flow.json`

### Category 5: Documentation (3 tests)

**Documentation Files**:
- `/Users/rdmtv/Documents/claydev-local/agent-os-v2/moai-adk/.moai/docs/moai-flow/README.md`
- `/Users/rdmtv/Documents/claydev-local/agent-os-v2/moai-adk/.moai/docs/moai-flow/INTEGRATION.md`
- `/Users/rdmtv/Documents/claydev-local/agent-os-v2/moai-adk/.moai/docs/moai-flow/HOOKS.md`

### Category 6: File Structure (4 tests)

**Directories Validated**:
- `/Users/rdmtv/Documents/claydev-local/agent-os-v2/moai-adk/.claude/agents/moai-flow/`
- `/Users/rdmtv/Documents/claydev-local/agent-os-v2/moai-adk/.claude/commands/moai-flow/`
- `/Users/rdmtv/Documents/claydev-local/agent-os-v2/moai-adk/.claude/hooks/moai-flow/`
- `/Users/rdmtv/Documents/claydev-local/agent-os-v2/moai-adk/.moai/config/`
- `/Users/rdmtv/Documents/claydev-local/agent-os-v2/moai-adk/.moai/memory/moai-flow/`
- `/Users/rdmtv/Documents/claydev-local/agent-os-v2/moai-adk/.moai/docs/moai-flow/`
- `/Users/rdmtv/Documents/claydev-local/agent-os-v2/moai-adk/moai_flow/core/`
- `/Users/rdmtv/Documents/claydev-local/agent-os-v2/moai-adk/moai_flow/memory/`
- `/Users/rdmtv/Documents/claydev-local/agent-os-v2/moai-adk/moai_flow/optimization/`
- `/Users/rdmtv/Documents/claydev-local/agent-os-v2/moai-adk/moai_flow/coordination/`

---

## Working Directory

All paths are relative to:
```
/Users/rdmtv/Documents/claydev-local/agent-os-v2/moai-adk
```

---

## Quick Access Commands

### View Reports

```bash
# Quick status
cat .moai/reports/validation/QUICK-STATUS.txt

# Executive summary
cat .moai/reports/validation/VALIDATION-SUMMARY.md

# Full technical report
cat .moai/reports/validation/phase8-validation-report-FINAL.md

# Report index
cat .moai/reports/validation/INDEX.md

# Raw test data
cat .moai/temp/validation_results.json | python3 -m json.tool
```

### Navigate to Key Directories

```bash
# Python package
cd moai_flow/

# Claude integration
cd .claude/

# Configuration
cd .moai/config/

# Documentation
cd .moai/docs/moai-flow/

# Validation reports
cd .moai/reports/validation/
```

---

## Environment

**OS**: macOS (Darwin 25.2.0)
**Working Directory**: `/Users/rdmtv/Documents/claydev-local/agent-os-v2/moai-adk`
**Python**: 3.x
**Date**: 2025-11-30

---

**Last Updated**: 2025-11-30 19:01:00
