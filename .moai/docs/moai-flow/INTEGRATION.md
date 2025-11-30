# MoAI-Flow Claude Code Integration Guide

This document provides detailed integration patterns for MoAI-Flow with Claude Code, including agent delegation, command usage, skill loading, and state management.

---

## Table of Contents

1. [Agent Integration](#agent-integration)
2. [Command Integration](#command-integration)
3. [Skill Integration](#skill-integration)
4. [Hook Integration](#hook-integration)
5. [Configuration Management](#configuration-management)
6. [State Persistence](#state-persistence)
7. [Extension Guide](#extension-guide)

---

## Agent Integration

MoAI-Flow provides 4 specialized agents for swarm coordination, optimization, consensus analysis, and self-healing.

### Agent Architecture

```
.claude/agents/moai-flow/
├── coordinator-swarm.md       # Swarm orchestration
├── optimizer-bottleneck.md    # Performance optimization
├── analyzer-consensus.md      # Consensus analysis
└── healer-self.md             # Auto-healing
```

---

### 1. Coordinator-Swarm Agent

**Purpose**: Orchestrate swarm coordination, manage topologies, and coordinate distributed agent lifecycles.

**Location**: `.claude/agents/moai-flow/coordinator-swarm.md`

**Skills**: `moai-flow-coordination`, `moai-flow-memory`

**Tools**: All

#### Agent Definition

```yaml
---
name: coordinator-swarm
description: Swarm coordination orchestrator for managing distributed agent topologies
skills:
  - moai-flow-coordination
  - moai-flow-memory
tools:
  - all
---
```

#### Capabilities

- Initialize swarm sessions with configurable topologies
- Switch topologies dynamically (hierarchical, mesh, star, ring, adaptive)
- Coordinate consensus among agents
- Manage agent lifecycle and state synchronization

#### Usage via Task()

```python
# Initialize swarm with custom topology
Task(
    subagent_type="coordinator-swarm",
    prompt="""
Initialize a new swarm session with the following requirements:
- Topology: mesh
- Agent count: 8
- Consensus algorithm: raft
- Purpose: Distributed code review across 5 repositories
"""
)

# Switch topology dynamically
Task(
    subagent_type="coordinator-swarm",
    prompt="""
Current swarm is experiencing coordination bottlenecks.
Switch from hierarchical to adaptive topology while preserving:
- Active task assignments
- Agent states
- Consensus history
"""
)

# Coordinate distributed decision
Task(
    subagent_type="coordinator-swarm",
    prompt="""
Request consensus from swarm agents on:
Proposal: "Deploy feature-auth to production environment"
Timeout: 10000ms
Required quorum: 75%
"""
)
```

#### Integration with MoAI-ADK

```python
# Alfred can delegate swarm initialization
# During /moai:1-plan phase
if task_complexity == "high" and requires_distributed_execution:
    Task(
        subagent_type="coordinator-swarm",
        prompt="Initialize adaptive swarm for distributed TDD implementation"
    )
```

---

### 2. Optimizer-Bottleneck Agent

**Purpose**: Detect performance bottlenecks in swarm coordination and suggest optimizations.

**Location**: `.claude/agents/moai-flow/optimizer-bottleneck.md`

**Skills**: `moai-flow-optimization`, `moai-flow-monitoring`

**Tools**: Read, Grep, Bash

#### Agent Definition

```yaml
---
name: optimizer-bottleneck
description: Performance bottleneck analyzer for moai-flow swarm systems
skills:
  - moai-flow-optimization
  - moai-flow-monitoring
tools:
  - Read
  - Grep
  - Bash
---
```

#### Capabilities

- Analyze swarm performance metrics
- Identify coordination bottlenecks
- Suggest optimization strategies
- Monitor resource utilization across agents

#### Usage via Task()

```python
# Analyze current performance
Task(
    subagent_type="optimizer-bottleneck",
    prompt="""
Analyze current swarm performance and identify bottlenecks:
- Check task throughput (tasks/sec)
- Measure consensus latency
- Identify slow agents
- Recommend topology optimization
"""
)

# Optimize resource allocation
Task(
    subagent_type="optimizer-bottleneck",
    prompt="""
Current swarm metrics show:
- Average task duration: 5.2s
- Consensus timeout rate: 15%
- Agent utilization: 45%

Suggest optimization strategy to:
1. Reduce task duration to < 3s
2. Decrease timeout rate to < 5%
3. Increase utilization to > 70%
"""
)

# Monitor continuous performance
Task(
    subagent_type="optimizer-bottleneck",
    prompt="""
Monitor swarm performance over next 100 tasks and report:
- Performance trends
- Degradation patterns
- Recommended preemptive optimizations
"""
)
```

---

### 3. Analyzer-Consensus Agent

**Purpose**: Analyze consensus algorithms and recommend strategies for distributed decision-making.

**Location**: `.claude/agents/moai-flow/analyzer-consensus.md`

**Skills**: `moai-flow-coordination`

**Tools**: Read, Grep, Bash

#### Agent Definition

```yaml
---
name: analyzer-consensus
description: Consensus pattern analyzer for distributed decision-making
skills:
  - moai-flow-coordination
tools:
  - Read
  - Grep
  - Bash
---
```

#### Capabilities

- Analyze consensus protocol configurations
- Recommend consensus algorithms based on requirements
- Validate consensus timeout and quorum settings
- Debug consensus failures

#### Usage via Task()

```python
# Recommend consensus algorithm
Task(
    subagent_type="analyzer-consensus",
    prompt="""
Recommend optimal consensus algorithm for:
- System type: High-availability distributed cache
- Swarm size: 50 agents
- Failure tolerance: Up to 15 agent failures
- Consistency requirement: Strong consistency
- Latency tolerance: < 500ms
"""
)

# Debug consensus failure
Task(
    subagent_type="analyzer-consensus",
    prompt="""
Consensus request failed with timeout.
Debug the following scenario:
- Algorithm: raft
- Swarm size: 12 agents
- Timeout: 5000ms
- Quorum: 7/12 required
- Result: Only 5 votes received

Analyze root cause and suggest fix.
"""
)

# Validate configuration
Task(
    subagent_type="analyzer-consensus",
    prompt="""
Validate current consensus configuration:
- Algorithm: byzantine
- Quorum: 67% (2f+1 where f=5)
- Timeout: 3000ms
- Network latency: ~200ms

Check for configuration issues or risks.
"""
)
```

---

### 4. Healer-Self Agent

**Purpose**: Detect failures in swarm coordination and apply automated healing strategies.

**Location**: `.claude/agents/moai-flow/healer-self.md`

**Skills**: `moai-flow-optimization`, `moai-flow-monitoring`

**Tools**: Read, Write, Edit, Bash

#### Agent Definition

```yaml
---
name: healer-self
description: Auto-healing orchestrator for swarm fault detection and recovery
skills:
  - moai-flow-optimization
  - moai-flow-monitoring
tools:
  - Read
  - Write
  - Edit
  - Bash
---
```

#### Capabilities

- Detect agent failures and coordination anomalies
- Apply healing strategies (restart, reassign, rebalance)
- Monitor recovery progress
- Prevent cascading failures

#### Usage via Task()

```python
# Recover from agent failure
Task(
    subagent_type="healer-self",
    prompt="""
Agent failure detected:
- Failed agent: agent_007
- Tasks in progress: 3
- Swarm topology: mesh
- Remaining agents: 11/12

Apply healing strategy:
1. Reassign tasks to healthy agents
2. Update topology to exclude failed agent
3. Maintain consensus quorum
4. Monitor recovery
"""
)

# Prevent cascading failures
Task(
    subagent_type="healer-self",
    prompt="""
Performance degradation detected:
- Slow agents: 4/15
- Task timeout rate increasing: 5% → 15%
- Consensus latency: 2s → 8s

Apply preemptive healing to prevent cascade:
1. Identify root cause
2. Isolate slow agents
3. Rebalance workload
4. Monitor stabilization
"""
)

# Monitor and heal continuously
Task(
    subagent_type="healer-self",
    prompt="""
Enable continuous monitoring and auto-healing:
- Health check interval: 5s
- Anomaly threshold: 2 sigma deviation
- Healing strategies: restart, reassign, rebalance
- Max healing attempts: 3
"""
)
```

---

## Command Integration

MoAI-Flow provides 4 slash commands for swarm management.

### Command Architecture

```
.claude/commands/moai-flow/
├── swarm-init.md          # Initialize swarm
├── swarm-status.md        # Display status
├── topology-switch.md     # Switch topology
└── consensus-request.md   # Request consensus
```

---

### 1. /swarm-init

**Purpose**: Initialize a new moai-flow swarm session with specified topology and configuration.

**Location**: `.claude/commands/moai-flow/swarm-init.md`

#### Syntax

```bash
/swarm-init [topology] [agent_count]
```

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `topology` | string | No | "adaptive" | Topology type |
| `agent_count` | number | No | 3 | Number of agents |

**Topology Options**: hierarchical, mesh, star, ring, adaptive

#### Examples

```bash
# Initialize with defaults (adaptive topology, 3 agents)
/swarm-init

# Initialize mesh topology with 5 agents
/swarm-init mesh 5

# Initialize hierarchical topology with default agent count
/swarm-init hierarchical
```

#### Behavior

1. Initialize SwarmCoordinator with specified topology
2. Create agent pool with requested count
3. Set up coordination protocols from config
4. Initialize shared memory (SwarmDB)
5. Report swarm session ID and status

#### Output

```
Swarm session initialized:
- Session ID: swarm_001_20251130_143022
- Topology: mesh
- Active agents: 5
- Consensus algorithm: raft
- State sync interval: 1000ms
- Auto-healing: enabled
```

#### Python Implementation

The command internally calls:

```python
from moai_flow.core.swarm_coordinator import SwarmCoordinator

coordinator = SwarmCoordinator()
session_id = coordinator.initialize_session(
    topology="mesh",
    agent_count=5
)
```

---

### 2. /swarm-status

**Purpose**: Display current moai-flow swarm status and performance metrics.

**Location**: `.claude/commands/moai-flow/swarm-status.md`

#### Syntax

```bash
/swarm-status
```

#### Parameters

None

#### Example

```bash
/swarm-status
```

#### Behavior

1. Query current swarm session from SwarmDB
2. Retrieve topology and agent states
3. Collect performance metrics from MetricsCollector
4. Format comprehensive status report

#### Output

```
Swarm Status:
═══════════════════════════════════════════

Session ID: swarm_001_20251130_143022
Topology: mesh
Uptime: 1h 23m 45s

Agents:
  Active: 5/5
  Healthy: 5/5
  Utilization: 68%

Consensus:
  Algorithm: raft
  State: STABLE
  Last consensus: 12s ago
  Success rate: 98.5%

Performance Metrics:
  Throughput: 12.3 tasks/sec
  Avg task duration: 2.4s
  Avg consensus latency: 320ms
  P95 latency: 580ms
  P99 latency: 920ms

Health:
  Status: HEALTHY
  Warnings: None
  Last healing: 45m ago (recovered agent_003)
```

#### Python Implementation

```python
from moai_flow.core.swarm_coordinator import SwarmCoordinator
from moai_flow.monitoring.metrics_collector import MetricsCollector

coordinator = SwarmCoordinator()
collector = MetricsCollector()

status = coordinator.get_status()
metrics = collector.get_latest_metrics()
```

---

### 3. /topology-switch

**Purpose**: Switch moai-flow swarm topology dynamically while preserving state.

**Location**: `.claude/commands/moai-flow/topology-switch.md`

#### Syntax

```bash
/topology-switch <new_topology>
```

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `new_topology` | string | Yes | Target topology |

**Topology Options**: hierarchical, mesh, star, ring, adaptive

#### Examples

```bash
# Switch to mesh topology
/topology-switch mesh

# Switch to adaptive topology
/topology-switch adaptive
```

#### Behavior

1. Validate current swarm session exists
2. Validate target topology is different from current
3. Preserve agent states and pending tasks
4. Transition to new topology (reconfigure connections)
5. Restore coordination protocols
6. Report transition success

#### Output

```
Topology Transition Report:
═══════════════════════════════════════════

Previous topology: hierarchical
New topology: mesh

Transition details:
  Duration: 1.24s
  Agents migrated: 5/5
  Tasks preserved: 8 pending, 0 lost
  Consensus state: STABLE

Warnings:
  - Temporary latency spike during migration (+150ms)

Status: SUCCESS
```

#### Python Implementation

```python
from moai_flow.core.swarm_coordinator import SwarmCoordinator

coordinator = SwarmCoordinator()
result = coordinator.switch_topology(
    new_topology="mesh",
    preserve_state=True
)
```

---

### 4. /consensus-request

**Purpose**: Request consensus decision from moai-flow swarm agents.

**Location**: `.claude/commands/moai-flow/consensus-request.md`

#### Syntax

```bash
/consensus-request "<proposal>" [timeout]
```

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `proposal` | string | Yes | - | Proposal description |
| `timeout` | number | No | 5000 | Timeout in milliseconds |

#### Examples

```bash
# Request consensus with default timeout
/consensus-request "Approve deployment to production"

# Request consensus with custom timeout
/consensus-request "Select optimization strategy" 10000
```

#### Behavior

1. Validate swarm session is active
2. Broadcast proposal to all active agents
3. Collect votes within timeout period
4. Apply configured consensus algorithm
5. Return agreed result or timeout error

#### Output (Success)

```
Consensus Result:
═══════════════════════════════════════════

Proposal: "Approve deployment to production"

Decision: APPROVED
Duration: 3.42s

Vote Breakdown:
  Yes: 8 agents
  No: 0 agents
  Abstain: 2 agents

Participating Agents:
  agent_001, agent_002, agent_003, agent_004, agent_005,
  agent_006, agent_007, agent_008, agent_009, agent_010

Consensus Algorithm: raft
Quorum: 7/10 (70% required, 80% achieved)

Status: SUCCESS
```

#### Output (Failure)

```
Consensus Result:
═══════════════════════════════════════════

Proposal: "Approve deployment to production"

Decision: TIMEOUT
Duration: 5.00s (timeout reached)

Vote Breakdown:
  Yes: 4 agents
  No: 1 agent
  Abstain: 0 agents
  No response: 5 agents

Quorum: 7/10 (70% required, 40% achieved)

Error: Consensus not reached within timeout period

Suggestions:
  - Increase timeout (current: 5000ms)
  - Check agent connectivity
  - Reduce quorum requirement
  - Switch to faster consensus algorithm

Status: FAILED
```

#### Python Implementation

```python
from moai_flow.core.swarm_coordinator import SwarmCoordinator

coordinator = SwarmCoordinator()
result = coordinator.request_consensus(
    proposal="Approve deployment to production",
    timeout_ms=5000
)
```

---

## Skill Integration

MoAI-Flow provides 4 skills loaded by agents.

### Skill Architecture

```
.claude/skills/
├── moai-flow-coordination/
│   ├── SKILL.md
│   ├── modules/
│   └── examples/
├── moai-flow-memory/
│   ├── SKILL.md
│   ├── modules/
│   └── examples/
├── moai-flow-optimization/
│   ├── SKILL.md
│   ├── modules/
│   └── examples/
└── moai-flow-github/
    ├── SKILL.md
    ├── modules/
    └── examples/
```

### Skill Loading Pattern

Skills are loaded via agent YAML frontmatter:

```yaml
---
name: coordinator-swarm
skills:
  - moai-flow-coordination
  - moai-flow-memory
---
```

When an agent is invoked via `Task(subagent_type="coordinator-swarm", ...)`, Claude Code automatically loads the specified skills.

### Skill Descriptions

| Skill | Purpose | Used By |
|-------|---------|---------|
| `moai-flow-coordination` | Multi-agent coordination patterns, swarm orchestration | coordinator-swarm, analyzer-consensus |
| `moai-flow-memory` | Distributed memory management, context persistence | coordinator-swarm |
| `moai-flow-optimization` | Performance optimization, bottleneck detection | optimizer-bottleneck, healer-self |
| `moai-flow-github` | GitHub workflow integration | (future agents) |

---

## Hook Integration

MoAI-Flow provides 3 lifecycle hooks for seamless integration.

### Hook Architecture

```
.claude/hooks/moai-flow/
├── config.json              # Hook configuration
├── pre_swarm_task.py       # Pre-task hook
├── post_swarm_task.py      # Post-task hook
├── swarm_lifecycle.py      # Lifecycle hook
└── lib/                    # Utility library
    ├── __init__.py
    ├── coordination_utils.py
    └── metrics_utils.py
```

### Hook Execution Flow

```
Session Start
    ↓
swarm_lifecycle.py (session_start event)
    ↓
Initialize SwarmCoordinator
    ↓
Return session_id
    ↓
[Normal Claude Code operation]
    ↓
Before each task
    ↓
pre_swarm_task.py
    ↓
Initialize coordination context
    ↓
Execute task
    ↓
After each task
    ↓
post_swarm_task.py
    ↓
Collect metrics & apply healing
    ↓
[Continue tasks...]
    ↓
Session End
    ↓
swarm_lifecycle.py (session_end event)
    ↓
Persist state to SwarmDB
    ↓
Cleanup resources
```

### Hook Details

See [HOOKS.md](./HOOKS.md) for detailed hook usage and customization guide.

---

## Configuration Management

### Configuration Files

| File | Purpose | Format |
|------|---------|--------|
| `.moai/config/moai-flow.json` | Main configuration | JSON |
| `.claude/moai-flow-config.json` | Claude Code registry | JSON |
| `.claude/hooks/moai-flow/config.json` | Hook configuration | JSON |

### Configuration Loading

```python
import json
from pathlib import Path

# Load main configuration
config_path = Path(".moai/config/moai-flow.json")
with open(config_path) as f:
    config = json.load(f)

# Access configuration
topology = config["moai_flow"]["swarm"]["default_topology"]  # "mesh"
consensus = config["moai_flow"]["swarm"]["consensus_algorithm"]  # "raft"
```

### Configuration Override

Configuration can be overridden at runtime:

```python
from moai_flow.core.swarm_coordinator import SwarmCoordinator

# Override default topology
coordinator = SwarmCoordinator(
    topology="hierarchical",  # Overrides config default
    consensus_algorithm="byzantine"
)
```

---

## State Persistence

### Persistence Architecture

```
.moai/memory/moai-flow/
├── session-state.json        # Current session (ephemeral)
├── swarm-sessions.db         # Session history (persistent)
└── latest-metrics.json       # Latest metrics (ephemeral)
```

### Session State JSON

```json
{
  "session_id": "swarm_001_20251130_143022",
  "topology": "mesh",
  "agent_count": 5,
  "started_at": "2025-11-30T14:30:22Z",
  "coordinator_state": {
    "active": true,
    "consensus_algorithm": "raft",
    "quorum_percentage": 0.7
  },
  "agents": [
    {"id": "agent_001", "status": "active", "tasks": 12},
    {"id": "agent_002", "status": "active", "tasks": 10}
  ]
}
```

### SwarmDB Schema

```sql
CREATE TABLE sessions (
    session_id TEXT PRIMARY KEY,
    topology TEXT NOT NULL,
    agent_count INTEGER NOT NULL,
    started_at TEXT NOT NULL,
    ended_at TEXT,
    status TEXT DEFAULT 'active'
);

CREATE TABLE metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    metric_type TEXT NOT NULL,
    value REAL NOT NULL,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
);
```

### Persistence API

```python
from moai_flow.memory.swarm_db import SwarmDB

db = SwarmDB()

# Save session state
db.persist_session_state({
    "session_id": "swarm_001",
    "topology": "mesh",
    "agent_count": 5
})

# Load session state
state = db.load_session_state("swarm_001")

# Save metrics
db.save_metric(
    session_id="swarm_001",
    metric_type="task_duration",
    value=2.4
)

# Query metrics
metrics = db.query_metrics(
    session_id="swarm_001",
    metric_type="task_duration"
)
```

---

## Extension Guide

### Adding New Agents

1. **Create agent definition** in `.claude/agents/moai-flow/new-agent.md`:

```yaml
---
name: new-agent
description: Custom agent description
skills:
  - moai-flow-coordination
tools:
  - Read
  - Write
---

# New Agent

## Purpose
Agent purpose here

## Capabilities
- Capability 1
- Capability 2
```

2. **Update moai-flow-config.json**:

```json
{
  "moai_flow": {
    "agents": [
      "coordinator-swarm",
      "optimizer-bottleneck",
      "analyzer-consensus",
      "healer-self",
      "new-agent"
    ]
  }
}
```

3. **Use via Task()**:

```python
Task(subagent_type="new-agent", prompt="...")
```

### Adding New Commands

1. **Create command definition** in `.claude/commands/moai-flow/new-command.md`:

```markdown
# /new-command

Description of new command.

## Usage

\`\`\`
/new-command <param>
\`\`\`

## Parameters

- `param` (required): Parameter description

## Examples

\`\`\`
/new-command value
\`\`\`
```

2. **Update moai-flow-config.json**:

```json
{
  "moai_flow": {
    "commands": [
      "swarm-init",
      "swarm-status",
      "topology-switch",
      "consensus-request",
      "new-command"
    ]
  }
}
```

3. **Use command**:

```bash
/new-command value
```

### Adding New Hooks

1. **Create hook file** in `.claude/hooks/moai-flow/new_hook.py`:

```python
"""New hook description."""

import sys
from pathlib import Path

moai_flow_path = Path(__file__).parent.parent.parent.parent / "moai_flow"
if moai_flow_path.exists():
    sys.path.insert(0, str(moai_flow_path.parent))

def execute(context):
    """
    Execute hook logic.

    Args:
        context: Hook context

    Returns:
        dict: Hook result
    """
    try:
        # Hook logic here
        return {"success": True, "result": "data"}
    except Exception as e:
        return {"success": False, "error": str(e)}
```

2. **Register hook** (when Claude Code supports custom hooks):

```json
{
  "hooks": {
    "CustomEvent": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "uv run \"$CLAUDE_PROJECT_DIR\"/.claude/hooks/moai-flow/new_hook.py"
          }
        ]
      }
    ]
  }
}
```

---

## Version

**Current Version**: 1.0.0

**Last Updated**: 2025-11-30

**Next**: See [HOOKS.md](./HOOKS.md) for hook customization guide
