# Core Development Agents

> The fundamental 5 agents for basic development tasks

## Overview

Core development agents handle the primary coding, testing, and planning tasks. These map most directly to MoAI's agent system.

---

## Agent: `coder`

### Purpose
Primary code implementation agent.

### Responsibilities
- Write production code
- Implement features
- Fix bugs
- Refactor code

### MoAI Equivalent
Multiple specialized agents:
- `expert-backend` (backend code)
- `expert-frontend` (frontend code)
- `expert-database` (database code)

### Key Difference
MoAI-Flow has ONE general coder; MoAI has domain-specialized coders.

---

## Agent: `reviewer`

### Purpose
Code review and quality assessment.

### Responsibilities
- Review pull requests
- Check code quality
- Identify issues
- Suggest improvements

### MoAI Equivalent
- `manager-quality` (quality gates)
- Part of `manager-tdd` (review during TDD)

### Key Difference
MoAI integrates review into quality workflow rather than standalone agent.

---

## Agent: `tester`

### Purpose
Test creation and execution.

### Responsibilities
- Write unit tests
- Write integration tests
- Execute test suites
- Report coverage

### MoAI Equivalent
- `manager-tdd` (TDD implementation)
- Integrated into `/moai:2-run` workflow

### Key Difference
MoAI enforces TDD at constitution level; testing is part of implementation.

---

## Agent: `planner`

### Purpose
Task planning and decomposition.

### Responsibilities
- Break down requirements
- Create task lists
- Estimate effort
- Prioritize work

### MoAI Equivalent
- `manager-strategy` (strategic planning)
- `manager-spec` (SPEC planning)
- Built-in `Plan` agent

### Key Difference
MoAI separates strategy from specification planning.

---

## Agent: `researcher`

### Purpose
Research and information gathering.

### Responsibilities
- Analyze requirements
- Research solutions
- Gather best practices
- Document findings

### MoAI Equivalent
- Built-in `Explore` agent (codebase search)
- `mcp-context7` (documentation research)

### Key Difference
MoAI has specialized research for codebase vs external docs.

---

## Comparison Table

| MoAI-Flow | MoAI Equivalent | Notes |
|-------------|-----------------|-------|
| `coder` | `expert-backend`, `expert-frontend`, `expert-database` | MoAI specializes |
| `reviewer` | `manager-quality` | MoAI integrates with quality |
| `tester` | `manager-tdd` | MoAI enforces TDD |
| `planner` | `manager-strategy`, `manager-spec` | MoAI separates concerns |
| `researcher` | `Explore`, `mcp-context7` | MoAI specializes sources |

---

## Key Insight

MoAI-Flow uses **general-purpose** core agents that can handle any task in their domain.

MoAI uses **specialized** agents that excel in specific domains, requiring more agents but providing deeper expertise.

### Trade-offs

| Approach | Pros | Cons |
|----------|------|------|
| MoAI-Flow (General) | Simpler selection | Less specialized |
| MoAI (Specialized) | Deep expertise | More complex selection |

---

## Recommendation

MoAI's specialization is valuable for complex projects. Consider adding a general `coder` alias that delegates to appropriate expert based on file type.
