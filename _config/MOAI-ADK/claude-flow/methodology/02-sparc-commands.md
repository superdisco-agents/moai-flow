# SPARC Commands Reference

> Claude-Flow CLI commands for SPARC methodology execution

## Overview

Claude-Flow provides a dedicated CLI (`npx claude-flow sparc`) for executing SPARC methodology phases.

---

## Core Commands

### List Available Modes

```bash
npx claude-flow sparc modes
```

Lists all available SPARC execution modes.

### Execute Specific Mode

```bash
npx claude-flow sparc run <mode> "<task>"
```

**Examples**:
```bash
npx claude-flow sparc run spec-pseudocode "Design user authentication system"
npx claude-flow sparc run architect "Design microservices architecture"
npx claude-flow sparc run integration "Integrate payment gateway"
```

### TDD Workflow

```bash
npx claude-flow sparc tdd "<feature>"
```

Runs complete TDD workflow for a feature:
1. Write failing tests
2. Implement to pass
3. Refactor
4. Iterate

**Example**:
```bash
npx claude-flow sparc tdd "User registration with email verification"
```

### Get Mode Information

```bash
npx claude-flow sparc info <mode>
```

Shows detailed information about a specific mode.

---

## Batchtools Commands

### Parallel Execution

```bash
npx claude-flow sparc batch <modes> "<task>"
```

Execute multiple modes in parallel.

**Example**:
```bash
npx claude-flow sparc batch "spec-pseudocode,architect" "Design API gateway"
```

### Full Pipeline

```bash
npx claude-flow sparc pipeline "<task>"
```

Runs all SPARC phases sequentially:
1. Specification
2. Pseudocode
3. Architecture
4. Refinement (TDD)
5. Completion

### Multi-Task Processing

```bash
npx claude-flow sparc concurrent <mode> "<tasks-file>"
```

Process multiple tasks from a file concurrently.

---

## MoAI Equivalent Commands

| SPARC Command | MoAI Equivalent |
|---------------|-----------------|
| `sparc modes` | Available in config (no CLI) |
| `sparc run spec-pseudocode` | `/moai:1-plan "description"` |
| `sparc run architect` | `/moai:1-plan` (architecture section) |
| `sparc tdd` | `/moai:2-run SPEC-ID` |
| `sparc run integration` | `/moai:3-sync` |
| `sparc pipeline` | `/moai:1-plan` → `/moai:2-run` → `/moai:3-sync` |
| `sparc batch` | No direct equivalent |
| `sparc concurrent` | No direct equivalent |

---

## Command Comparison

| Feature | Claude-Flow | MoAI |
|---------|-------------|------|
| CLI Tool | `npx claude-flow sparc` | Slash commands |
| Mode Selection | Explicit | Implicit in SPEC |
| Batch Execution | `sparc batch` | Task() parallel calls |
| Pipeline | `sparc pipeline` | Sequential commands |
| Info Command | `sparc info` | Skill documentation |

---

## Gap Analysis

### Missing in MoAI

1. **Dedicated CLI**: No `npx moai-adk` equivalent
2. **Batch Command**: No single command for parallel modes
3. **Mode Info**: No quick info lookup command
4. **Pipeline Command**: No single "run everything" command

### Potential Addition

```bash
# Proposed MoAI CLI
npx moai-adk plan "description"    # → /moai:1-plan
npx moai-adk run SPEC-001          # → /moai:2-run
npx moai-adk sync                  # → /moai:3-sync
npx moai-adk pipeline "task"       # → Full workflow
npx moai-adk batch "plan,run"      # → Parallel execution
```

---

## Usage Examples

### Claude-Flow Full Workflow

```bash
# Step 1: Specification
npx claude-flow sparc run spec-pseudocode "Build REST API for user management"

# Step 2: Architecture
npx claude-flow sparc run architect "Design service architecture"

# Step 3: TDD Implementation
npx claude-flow sparc tdd "User CRUD operations"

# Step 4: Integration
npx claude-flow sparc run integration "Connect to frontend"
```

### MoAI Equivalent Workflow

```bash
# Step 1: Planning (Spec + Architecture)
/moai:1-plan "Build REST API for user management"

# Step 2: TDD Implementation
/moai:2-run SPEC-001

# Step 3: Documentation & Integration
/moai:3-sync
```

---

## Key Takeaway

Claude-Flow has a richer CLI experience, while MoAI uses slash commands within Claude Code. Both achieve similar outcomes through different interfaces.
