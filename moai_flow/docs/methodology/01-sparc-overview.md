# SPARC Methodology Overview

> Specification, Pseudocode, Architecture, Refinement, Completion

## What is SPARC?

SPARC is MoAI-Flow's systematic development methodology that breaks down complex tasks into 5 distinct phases.

```
S → Specification    (What to build)
P → Pseudocode       (How to design)
A → Architecture     (System structure)
R → Refinement       (TDD implementation)
C → Completion       (Integration & delivery)
```

---

## The 5 Phases

### 1. Specification Phase

**Purpose**: Define requirements and constraints

**Activities**:
- Requirements analysis
- Constraint identification
- Success criteria definition
- Scope boundaries

**Output**: Clear specification document

### 2. Pseudocode Phase

**Purpose**: Design algorithms and logic flow

**Activities**:
- Algorithm design
- Logic flow mapping
- Edge case identification
- Data structure planning

**Output**: Pseudocode documentation

### 3. Architecture Phase

**Purpose**: Design system structure

**Activities**:
- Component design
- Interface definitions
- Dependency mapping
- Technology selection

**Output**: Architecture document

### 4. Refinement Phase

**Purpose**: TDD implementation

**Activities**:
- Write failing tests (RED)
- Implement to pass (GREEN)
- Refactor for quality (REFACTOR)
- Iterate until complete

**Output**: Working, tested code

### 5. Completion Phase

**Purpose**: Integration and delivery

**Activities**:
- System integration
- End-to-end testing
- Documentation finalization
- Deployment preparation

**Output**: Production-ready deliverable

---

## SPARC Execution Modes

MoAI-Flow provides specific modes for each phase:

| Mode | Command | Purpose |
|------|---------|---------|
| `spec-pseudocode` | `sparc run spec-pseudocode` | Combined Spec + Pseudocode |
| `architect` | `sparc run architect` | Architecture design |
| `tdd` | `sparc tdd` | Full TDD workflow |
| `integration` | `sparc run integration` | Completion phase |

---

## MoAI Comparison

MoAI uses a 4-command workflow instead of 5 phases:

| SPARC Phase | MoAI Equivalent |
|-------------|-----------------|
| Specification | `/moai:1-plan` (SPEC generation) |
| Pseudocode | `/moai:1-plan` (included in SPEC) |
| Architecture | `/moai:1-plan` (included in SPEC) |
| Refinement | `/moai:2-run` (TDD implementation) |
| Completion | `/moai:3-sync` (documentation & integration) |

### Key Differences

| Aspect | SPARC | MoAI |
|--------|-------|------|
| Phases | 5 distinct | 4 commands |
| Spec/Pseudo | Separate | Combined in SPEC |
| Architecture | Dedicated phase | Part of planning |
| TDD | Refinement phase | `/moai:2-run` |
| Integration | Completion phase | `/moai:3-sync` |

---

## SPARC Strengths

1. **Clear Phase Boundaries**: Each phase has distinct deliverables
2. **Explicit Pseudocode**: Separate algorithm design step
3. **Dedicated Architecture**: Focused structural planning
4. **Named Methodology**: "SPARC" is memorable and marketable

## MoAI Strengths

1. **Streamlined Flow**: 4 commands vs 5 phases
2. **SPEC Documents**: Comprehensive single artifact
3. **EARS Format**: Structured requirement format
4. **Automated TDD**: manager-tdd handles RED-GREEN-REFACTOR

---

## Recommendation

Consider adding explicit pseudocode phase to `/moai:1-plan`:

```markdown
SPEC-001 Structure:
1. Overview (Specification)
2. Algorithm Design (Pseudocode)   ← NEW
3. Architecture (Architecture)
4. Implementation Plan (Refinement prep)
5. Success Criteria (Completion criteria)
```

This would give MoAI SPARC-like coverage while maintaining its streamlined command structure.
