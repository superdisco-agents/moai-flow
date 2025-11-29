# SPARC Methodology Agents

> Dedicated agents for SPARC phase execution

## Overview

MoAI-Flow has 6 agents specifically for executing SPARC methodology phases. These are workflow-specific agents that map to MoAI's manager tier.

---

## Agent: `sparc-coord`

### Purpose
Coordinate entire SPARC workflow.

### Responsibilities
- Manage phase transitions
- Track progress
- Ensure phase dependencies
- Handle phase failures

### Workflow Control
```
sparc-coord
    │
    ├── specification agent
    │       │
    │       ▼
    ├── pseudocode agent
    │       │
    │       ▼
    ├── architecture agent
    │       │
    │       ▼
    ├── refinement agent
    │       │
    │       ▼
    └── (completion via integration)
```

### MoAI Equivalent
Alfred (main orchestrator) handles workflow coordination.

---

## Agent: `sparc-coder`

### Purpose
SPARC-aware code implementation.

### Capabilities
- Follows SPARC phase context
- Respects architecture decisions
- Implements from pseudocode
- Validates against specification

### Key Difference from `coder`
`sparc-coder` understands SPARC phase context; `coder` is general-purpose.

---

## Agent: `specification`

### Purpose
Execute specification phase.

### Outputs
- Requirements document
- Constraints list
- Success criteria
- Scope definition

### Activities
```
1. Gather requirements
2. Identify constraints
3. Define success criteria
4. Set scope boundaries
5. Document everything
```

### MoAI Equivalent
`manager-spec` generates SPEC documents with similar content.

---

## Agent: `pseudocode`

### Purpose
Execute pseudocode phase.

### Outputs
- Algorithm designs
- Logic flow diagrams
- Edge case catalog
- Data structure plans

### Activities
```
1. Design algorithms
2. Map logic flows
3. Identify edge cases
4. Plan data structures
5. Validate completeness
```

### MoAI Gap
No dedicated pseudocode phase. Included implicitly in SPEC.

---

## Agent: `architecture`

### Purpose
Execute architecture phase.

### Outputs
- Architecture diagrams
- Component specifications
- Interface definitions
- Technology decisions

### Activities
```
1. Design components
2. Define interfaces
3. Map dependencies
4. Select technologies
5. Document decisions
```

### MoAI Equivalent
Partially in `manager-strategy` and SPEC architecture section.

---

## Agent: `refinement`

### Purpose
Execute refinement (TDD) phase.

### The TDD Loop
```
   RED ───────────────┐
    │                 │
    ▼                 │
Write failing test    │
    │                 │
    ▼                 │
  GREEN              │
    │                │
    ▼                │
Make test pass       │
    │                │
    ▼                │
REFACTOR            │
    │               │
    ▼               │
Improve code ───────┘
```

### MoAI Equivalent
`manager-tdd` handles TDD implementation in `/moai:2-run`.

---

## Comparison Table

| SPARC Agent | MoAI Equivalent | Notes |
|-------------|-----------------|-------|
| `sparc-coord` | Alfred | Main orchestrator |
| `sparc-coder` | `expert-*` | Domain-specialized |
| `specification` | `manager-spec` | SPEC generation |
| `pseudocode` | (in SPEC) | No dedicated agent |
| `architecture` | `manager-strategy` | Strategy + architecture |
| `refinement` | `manager-tdd` | TDD implementation |

---

## Key Insight

SPARC agents are **phase-specific** while MoAI agents are **command-specific**.

### SPARC Approach
- Each phase has dedicated agent
- Agents understand phase context
- Sequential phase execution

### MoAI Approach
- Commands trigger workflows
- Agents handle specific responsibilities
- Integrated specification phases

---

## Recommendation

MoAI's approach is more streamlined. Consider:

1. Adding explicit pseudocode section to SPEC template
2. Documenting implicit phase mapping
3. Keeping command-based approach for simplicity
