# SPARC vs MoAI Workflow Comparison

> Side-by-side comparison of MoAI-Flow SPARC and MoAI-ADK workflows

## Overview

Both systems provide structured development workflows, but with different philosophies:

- **SPARC**: 5 explicit phases, CLI-driven
- **MoAI**: 4 commands, slash command-driven

---

## Workflow Comparison

### MoAI-Flow SPARC

```
┌────────────────────────────────────────────────┐
│                 SPARC Workflow                 │
├────────────────────────────────────────────────┤
│                                                │
│  1. Specification ──► spec-pseudocode          │
│         │                                      │
│         ▼                                      │
│  2. Pseudocode ────► spec-pseudocode           │
│         │                                      │
│         ▼                                      │
│  3. Architecture ──► architect                 │
│         │                                      │
│         ▼                                      │
│  4. Refinement ────► tdd                       │
│         │                                      │
│         ▼                                      │
│  5. Completion ────► integration               │
│                                                │
└────────────────────────────────────────────────┘
```

### MoAI-ADK

```
┌────────────────────────────────────────────────┐
│                 MoAI Workflow                  │
├────────────────────────────────────────────────┤
│                                                │
│  0. Project Setup ──► /moai:0-project          │
│         │                                      │
│         ▼                                      │
│  1. Planning ───────► /moai:1-plan             │
│    (Spec+Pseudo+Arch)                          │
│         │                                      │
│         ▼                                      │
│  2. Implementation ─► /moai:2-run              │
│    (TDD Cycle)                                 │
│         │                                      │
│         ▼                                      │
│  3. Synchronization ► /moai:3-sync             │
│    (Docs+Integration)                          │
│                                                │
└────────────────────────────────────────────────┘
```

---

## Feature Comparison

| Feature | SPARC (MoAI-Flow) | MoAI-ADK |
|---------|---------------------|----------|
| **Phases** | 5 (S-P-A-R-C) | 4 (0-1-2-3) |
| **CLI** | `npx moai-flow sparc` | Slash commands |
| **Spec Format** | Implicit | EARS format |
| **Pseudocode** | Dedicated phase | Part of SPEC |
| **Architecture** | Dedicated phase | Part of SPEC |
| **TDD** | `sparc tdd` | manager-tdd agent |
| **Integration** | `sparc run integration` | `/moai:3-sync` |
| **Agents** | 54 agents | 56 agents |
| **Feedback** | N/A | `/moai:9-feedback` |

---

## Artifact Comparison

### SPARC Deliverables

```
Phase 1: requirements.md
Phase 2: pseudocode.md
Phase 3: architecture.md
Phase 4: src/*.js + tests/*.test.js
Phase 5: docs/*, deployment/*
```

### MoAI Deliverables

```
/moai:1-plan: .moai/specs/SPEC-001/SPEC-001.md
/moai:2-run:  src/* + tests/*
/moai:3-sync: .moai/docs/*, README updates
```

---

## Agent Involvement

### SPARC Agents per Phase

| Phase | Primary Agents |
|-------|----------------|
| Specification | `researcher`, `planner` |
| Pseudocode | `specification`, `pseudocode` |
| Architecture | `system-architect`, `architecture` |
| Refinement | `coder`, `tester`, `tdd-london-swarm` |
| Completion | `reviewer`, `integration` |

### MoAI Agents per Command

| Command | Primary Agents |
|---------|----------------|
| `/moai:0-project` | `manager-project` |
| `/moai:1-plan` | `manager-spec`, `manager-strategy` |
| `/moai:2-run` | `manager-tdd`, `expert-*` |
| `/moai:3-sync` | `manager-docs`, `manager-git` |

---

## Strengths Analysis

### SPARC Strengths

1. **Explicit Phases**: Clear boundaries between activities
2. **CLI Tooling**: Dedicated command-line interface
3. **Batch Operations**: `sparc batch` for parallel execution
4. **Pipeline Command**: Single command for full workflow
5. **Named Methodology**: Marketing-friendly "SPARC" acronym

### MoAI Strengths

1. **Streamlined Commands**: 4 commands vs 5 phases
2. **SPEC Documents**: Comprehensive single artifact
3. **EARS Format**: Structured requirement writing
4. **Agent Specialization**: Domain-focused agents
5. **Skills System**: Modular knowledge capsules
6. **Configuration-Driven**: `.moai/config/config.json`
7. **Feedback Loop**: `/moai:9-feedback` for improvements

---

## Recommendation for MoAI

### Keep These MoAI Strengths
- Streamlined 4-command workflow
- SPEC document system
- Domain-focused agent hierarchy
- Skills and configuration system

### Consider Adding from SPARC
1. **Explicit Pseudocode Section** in SPEC documents
2. **CLI Tool** (`npx moai-adk`) for non-Claude Code usage
3. **Pipeline Command** for full workflow automation
4. **Named Methodology** (e.g., "STAR" - Spec, TDD, Architecture, Release)

---

## Migration Path

If moving from SPARC to MoAI:

| SPARC Command | MoAI Equivalent |
|---------------|-----------------|
| `sparc run spec-pseudocode "X"` | `/moai:1-plan X` |
| `sparc run architect "X"` | (Part of `/moai:1-plan`) |
| `sparc tdd "X"` | `/moai:2-run SPEC-ID` |
| `sparc run integration` | `/moai:3-sync` |
| `sparc pipeline "X"` | `/moai:1-plan` → `/moai:2-run` → `/moai:3-sync` |

---

## Conclusion

Both workflows achieve similar goals through different approaches. MoAI's streamlined command structure is more efficient, while SPARC's explicit phases provide clearer mental models. The ideal approach may be to maintain MoAI's efficiency while adopting SPARC's explicit phase naming for documentation purposes.
