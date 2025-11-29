# SPARC Workflow Phases

> Detailed breakdown of each SPARC phase with execution patterns

## Phase 1: Specification

### Purpose
Define WHAT needs to be built with clear requirements and constraints.

### Activities

```
1. Requirements Analysis
   └── Gather functional requirements
   └── Identify non-functional requirements
   └── Define acceptance criteria

2. Constraint Identification
   └── Technical constraints
   └── Business constraints
   └── Timeline constraints

3. Scope Definition
   └── In-scope items
   └── Out-of-scope items
   └── Future considerations
```

### Deliverables
- Requirements document
- Constraint list
- Scope boundary definition

### MoAI-Flow Execution
```bash
npx moai-flow sparc run spec-pseudocode "Project description"
```

---

## Phase 2: Pseudocode

### Purpose
Design HOW to solve the problem algorithmically.

### Activities

```
1. Algorithm Design
   └── Core logic flow
   └── Decision points
   └── Loop structures

2. Data Structure Planning
   └── Input formats
   └── Output formats
   └── Internal state

3. Edge Case Identification
   └── Boundary conditions
   └── Error scenarios
   └── Recovery paths
```

### Deliverables
- Pseudocode documentation
- Flow diagrams
- Edge case catalog

### MoAI-Flow Execution
```bash
# Combined with Specification
npx moai-flow sparc run spec-pseudocode "Feature description"
```

---

## Phase 3: Architecture

### Purpose
Design the STRUCTURE of the system.

### Activities

```
1. Component Design
   └── Module boundaries
   └── Interface definitions
   └── Component responsibilities

2. Dependency Mapping
   └── Internal dependencies
   └── External dependencies
   └── Dependency injection points

3. Technology Selection
   └── Framework choice
   └── Library selection
   └── Tool decisions
```

### Deliverables
- Architecture diagram
- Component specifications
- Technology stack document

### MoAI-Flow Execution
```bash
npx moai-flow sparc run architect "System description"
```

---

## Phase 4: Refinement (TDD)

### Purpose
IMPLEMENT the solution using Test-Driven Development.

### The TDD Cycle

```
RED → GREEN → REFACTOR → Repeat
```

### Activities

```
1. RED Phase
   └── Write failing test
   └── Define expected behavior
   └── Verify test fails correctly

2. GREEN Phase
   └── Write minimal implementation
   └── Make test pass
   └── No extra functionality

3. REFACTOR Phase
   └── Improve code quality
   └── Maintain passing tests
   └── Clean up duplication
```

### Deliverables
- Working, tested code
- Test suite
- Refactored codebase

### MoAI-Flow Execution
```bash
npx moai-flow sparc tdd "Feature description"
```

---

## Phase 5: Completion

### Purpose
INTEGRATE and deliver the final product.

### Activities

```
1. Integration
   └── Connect components
   └── End-to-end testing
   └── System verification

2. Documentation
   └── API documentation
   └── User guides
   └── Deployment guides

3. Delivery Preparation
   └── Build artifacts
   └── Release notes
   └── Deployment scripts
```

### Deliverables
- Integrated system
- Complete documentation
- Deployment-ready package

### MoAI-Flow Execution
```bash
npx moai-flow sparc run integration "Integration description"
```

---

## Phase Flow Diagram

```
┌─────────────┐
│Specification│
└──────┬──────┘
       ▼
┌─────────────┐
│ Pseudocode  │
└──────┬──────┘
       ▼
┌─────────────┐
│Architecture │
└──────┬──────┘
       ▼
┌─────────────┐
│ Refinement  │◄──┐
│   (TDD)     │   │ Iterate
└──────┬──────┘───┘
       ▼
┌─────────────┐
│ Completion  │
└─────────────┘
```

---

## MoAI Phase Mapping

| SPARC Phase | MoAI Phase | Command |
|-------------|------------|---------|
| Specification | SPEC Generation | `/moai:1-plan` |
| Pseudocode | SPEC Algorithm Section | `/moai:1-plan` |
| Architecture | SPEC Architecture Section | `/moai:1-plan` |
| Refinement | TDD Implementation | `/moai:2-run` |
| Completion | Documentation Sync | `/moai:3-sync` |

---

## Key Difference

**MoAI-Flow**: 5 explicit phases, each with dedicated commands

**MoAI**: 3 commands that implicitly cover all phases
- `/moai:1-plan` = Specification + Pseudocode + Architecture
- `/moai:2-run` = Refinement
- `/moai:3-sync` = Completion
