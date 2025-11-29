# MCP Tool Categories

> Organization of Claude-Flow MCP tools by function

## Overview

Claude-Flow organizes MCP tools into distinct categories based on their purpose. This helps understand when to use each tool.

---

## Category 1: Coordination

Tools for setting up and managing agent coordination.

| Tool | Purpose |
|------|---------|
| `swarm_init` | Initialize swarm with topology |
| `agent_spawn` | Define agent type for coordination |
| `task_orchestrate` | High-level task orchestration |

### Usage

```javascript
// Initialize mesh topology with 6 agents max
mcp__claude-flow__swarm_init {
  topology: "mesh",
  maxAgents: 6
}

// Define agent types for coordination
mcp__claude-flow__agent_spawn { type: "researcher" }
mcp__claude-flow__agent_spawn { type: "coder" }

// Orchestrate high-level workflow
mcp__claude-flow__task_orchestrate {
  tasks: ["research", "implement", "test"],
  strategy: "sequential"
}
```

---

## Category 2: Monitoring

Tools for observing swarm and agent status.

| Tool | Purpose |
|------|---------|
| `swarm_status` | Current swarm state |
| `agent_list` | List active agents |
| `agent_metrics` | Performance metrics |
| `task_status` | Task progress |
| `task_results` | Completed task results |

### Usage

```javascript
// Check swarm health
mcp__claude-flow__swarm_status {}

// List active agents
mcp__claude-flow__agent_list {}

// Get agent performance
mcp__claude-flow__agent_metrics { agentId: "researcher-1" }

// Check task progress
mcp__claude-flow__task_status { taskId: "task-123" }
```

---

## Category 3: Memory & Neural

Tools for shared memory and neural features.

| Tool | Purpose |
|------|---------|
| `memory_usage` | Memory statistics |
| `neural_status` | Neural feature status |
| `neural_train` | Train on patterns |
| `neural_patterns` | View learned patterns |

### Usage

```javascript
// Check memory usage
mcp__claude-flow__memory_usage {}

// Train on successful patterns
mcp__claude-flow__neural_train {
  pattern: "api_implementation",
  success: true
}

// View learned patterns
mcp__claude-flow__neural_patterns {}
```

---

## Category 4: GitHub Integration

Tools for GitHub repository operations.

| Tool | Purpose |
|------|---------|
| `github_swarm` | GitHub-aware swarm |
| `repo_analyze` | Repository analysis |
| `pr_enhance` | PR enhancement |
| `issue_triage` | Issue management |
| `code_review` | Code review swarm |

### Usage

```javascript
// Analyze repository
mcp__claude-flow__repo_analyze {
  repo: "owner/repo"
}

// Enhance PR description
mcp__claude-flow__pr_enhance {
  pr: 123,
  analysis: true
}

// Triage issues
mcp__claude-flow__issue_triage {
  labels: ["bug", "feature"]
}
```

---

## Category 5: System

Tools for system management and benchmarking.

| Tool | Purpose |
|------|---------|
| `benchmark_run` | Run benchmarks |
| `features_detect` | Detect available features |
| `swarm_monitor` | Monitor swarm health |

### Usage

```javascript
// Run performance benchmark
mcp__claude-flow__benchmark_run {
  type: "swe-bench",
  iterations: 100
}

// Detect available features
mcp__claude-flow__features_detect {}
```

---

## MoAI MCP Tool Comparison

### MoAI Current MCP Tools

| Server | Tools | Purpose |
|--------|-------|---------|
| **context7** | `resolve-library-id`, `get-library-docs` | Documentation |
| **playwright** | `browser_*` | Browser automation |
| **sequential-thinking** | `sequentialthinking` | Complex reasoning |
| **figma** | `get_design_context`, `get_screenshot` | Design |
| **github** | `create-or-update-file`, `push-files` | GitHub |
| **notion** | (various) | Workspace |

### Category Mapping

| Claude-Flow Category | MoAI Equivalent |
|---------------------|-----------------|
| Coordination | None |
| Monitoring | None |
| Memory & Neural | None |
| GitHub | Partial (basic) |
| System | None |

---

## Gap Analysis

### Complete Gaps in MoAI

1. **Coordination Tools**: No swarm management
2. **Monitoring Tools**: No agent/task metrics
3. **Memory Tools**: No shared memory
4. **Neural Tools**: No pattern learning
5. **Benchmark Tools**: No performance measurement

### Partial Coverage

- **GitHub**: Basic file operations vs full PR/issue management

---

## Recommendation

### Priority 1: Add Coordination
```json
{
  "claude-flow": {
    "command": "npx",
    "args": ["claude-flow@alpha", "mcp", "start"]
  }
}
```

### Priority 2: Add Monitoring
Track agent performance within MoAI:
```json
{
  "performance": {
    "track_metrics": true,
    "agents_monitored": true
  }
}
```

### Priority 3: Add Memory
Cross-session memory persistence.

---

## Tool Count Comparison

| Category | Claude-Flow | MoAI |
|----------|-------------|------|
| Coordination | 3 | 0 |
| Monitoring | 5 | 0 |
| Memory/Neural | 4 | 0 |
| GitHub | 5 | 2 |
| System | 3 | 0 |
| Documentation | 0 | 2 |
| Browser | 0 | 20+ |
| Reasoning | 0 | 1 |
| Design | 0 | 5 |
| Workspace | 0 | 5+ |

Claude-Flow: More coordination-focused
MoAI: More capability-focused
