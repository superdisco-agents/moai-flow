# MoAI-Flow Integration Guide

MoAI-Flow is a multi-agent swarm coordination system integrated with Claude Code and MoAI-ADK, enabling distributed task execution, consensus-based decision-making, and self-healing capabilities.

## Quick Start

### Initialize Swarm

```bash
/swarm-init mesh 5
```

Creates a swarm session with 5 agents using mesh topology.

### Check Status

```bash
/swarm-status
```

Displays current swarm state, metrics, and agent health.

### Switch Topology

```bash
/topology-switch adaptive
```

Dynamically switches to adaptive topology while preserving state.

### Request Consensus

```bash
/consensus-request "Approve deployment to production"
```

Requests distributed decision from all swarm agents.

---

## Architecture Overview

MoAI-Flow integrates across three architectural layers:

### 1. Claude Code Layer (`.claude/`)

**Location**: `/Users/rdmtv/Documents/claydev-local/agent-os-v2/moai-adk/.claude/`

#### Agents (`.claude/agents/moai-flow/`)

| Agent | Description | Skills |
|-------|-------------|--------|
| `coordinator-swarm` | Swarm coordination orchestrator | moai-flow-coordination, moai-flow-memory |
| `optimizer-bottleneck` | Performance bottleneck analyzer | moai-flow-optimization, moai-flow-monitoring |
| `analyzer-consensus` | Consensus pattern analyzer | moai-flow-coordination |
| `healer-self` | Auto-healing orchestrator | moai-flow-optimization, moai-flow-monitoring |

#### Commands (`.claude/commands/moai-flow/`)

| Command | Purpose | Parameters |
|---------|---------|------------|
| `/swarm-init` | Initialize swarm session | `[topology] [agent_count]` |
| `/swarm-status` | Display swarm status | None |
| `/topology-switch` | Switch topology | `<new_topology>` |
| `/consensus-request` | Request consensus | `"<proposal>" [timeout]` |

#### Hooks (`.claude/hooks/moai-flow/`)

| Hook | Trigger | Purpose |
|------|---------|---------|
| `pre_swarm_task.py` | Before task execution | Initialize coordination context |
| `post_swarm_task.py` | After task execution | Collect metrics and apply healing |
| `swarm_lifecycle.py` | Session start/end | Manage swarm lifecycle |

#### Skills (`.claude/skills/`)

| Skill | Purpose |
|-------|---------|
| `moai-flow-coordination` | Multi-agent coordination patterns |
| `moai-flow-memory` | Distributed memory management |
| `moai-flow-optimization` | Performance optimization strategies |
| `moai-flow-github` | GitHub workflow integration |

---

### 2. Python Implementation (`moai_flow/`)

**Location**: `/Users/rdmtv/Documents/claydev-local/agent-os-v2/moai-adk/moai_flow/`

#### Core Modules

- **SwarmCoordinator**: Manages swarm initialization, topology, and coordination protocols
- **Topology Management**: Supports hierarchical, mesh, star, ring, and adaptive topologies
- **Consensus Protocols**: Byzantine, Gossip, CRDT, Raft, Quorum, and Weighted algorithms

#### Memory System

- **SwarmDB**: SQLite-based state persistence for swarm sessions
- **Episodic Memory**: Task execution history and context
- **Semantic Memory**: Pattern learning and knowledge retention
- **Context Hints**: Intelligent context suggestions

#### Optimization Engine

- **Auto-Healing**: Detects failures and applies recovery strategies
- **Bottleneck Detection**: Identifies performance issues
- **Pattern Learning**: Learns from execution history
- **Predictive Healing**: Prevents failures before they occur

#### Monitoring System

- **Metrics Collection**: Task duration, throughput, latency
- **Health Checks**: Agent state and connectivity monitoring
- **Persistence**: Metrics storage for analysis

---

### 3. State Management (`.moai/`)

**Location**: `/Users/rdmtv/Documents/claydev-local/agent-os-v2/moai-adk/.moai/`

#### Configuration

**File**: `.moai/config/moai-flow.json`

```json
{
  "moai_flow": {
    "version": "1.0.0",
    "enabled": true,
    "swarm": {
      "default_topology": "mesh",
      "max_agents": 100,
      "consensus_algorithm": "raft"
    },
    "coordination": {
      "algorithms": ["byzantine", "gossip", "crdt", "raft", "quorum", "weighted"],
      "conflict_resolution": "automatic",
      "state_sync_interval_ms": 1000
    },
    "memory": {
      "semantic_enabled": true,
      "episodic_enabled": true,
      "context_hints_enabled": true,
      "persistence_path": ".moai/memory/moai-flow/swarm-sessions.db"
    },
    "optimization": {
      "bottleneck_detection": true,
      "self_healing": true,
      "pattern_learning": true,
      "predictive_healing": true
    },
    "monitoring": {
      "metrics_enabled": true,
      "health_checks_enabled": true,
      "persistence_enabled": true
    },
    "github": {
      "pr_agent_enabled": false,
      "issue_agent_enabled": false,
      "repo_health_enabled": false
    }
  }
}
```

#### Memory Persistence

| File | Purpose |
|------|---------|
| `.moai/memory/moai-flow/session-state.json` | Current session state |
| `.moai/memory/moai-flow/swarm-sessions.db` | Session history database |
| `.moai/memory/moai-flow/latest-metrics.json` | Latest performance metrics |

#### Documentation

**Location**: `.moai/docs/moai-flow/`

- `README.md` - This file (integration overview)
- `INTEGRATION.md` - Detailed integration guide
- `HOOKS.md` - Hook usage and customization

---

## Supported Topologies

### 1. Adaptive (Default)
- **Description**: Dynamically adjusts based on task requirements
- **Use Case**: General-purpose, handles varying workloads
- **Pros**: Flexible, self-optimizing
- **Cons**: Higher coordination overhead

### 2. Hierarchical
- **Description**: Tree-based structure with leader coordination
- **Use Case**: Large swarms with clear role hierarchy
- **Pros**: Scalable, efficient broadcasting
- **Cons**: Single point of failure at root

### 3. Mesh
- **Description**: Fully connected peer-to-peer network
- **Use Case**: Small to medium swarms requiring high resilience
- **Pros**: Fault-tolerant, no single point of failure
- **Cons**: High communication overhead

### 4. Star
- **Description**: Central coordinator with spoke agents
- **Use Case**: Simple coordination with centralized control
- **Pros**: Simple, low latency
- **Cons**: Coordinator is bottleneck

### 5. Ring
- **Description**: Circular coordination pattern
- **Use Case**: Token-based workflows, ordered execution
- **Pros**: Predictable, fair resource allocation
- **Cons**: Latency increases with ring size

---

## Consensus Algorithms

| Algorithm | Description | Use Case |
|-----------|-------------|----------|
| **Byzantine** | Byzantine fault tolerance | Critical systems requiring fault tolerance |
| **Gossip** | Probabilistic dissemination | Large swarms, eventual consistency |
| **CRDT** | Conflict-free replicated data | Distributed editing, real-time collaboration |
| **Raft** | Leader-based consensus | Strong consistency, ordered logs |
| **Quorum** | Majority voting | Simple decisions, fast consensus |
| **Weighted** | Priority-based voting | Agent expertise weighting |

---

## Usage Examples

### Example 1: Initialize Swarm with Custom Topology

```bash
# Initialize hierarchical topology with 10 agents
/swarm-init hierarchical 10
```

**Expected Output**:
```
Swarm session initialized:
- Session ID: swarm_001_20251130
- Topology: hierarchical
- Active agents: 10
- Consensus: raft
```

### Example 2: Monitor Performance and Optimize

```bash
# Check current status
/swarm-status

# If bottlenecks detected, switch topology
/topology-switch mesh
```

**Expected Output**:
```
Topology transition completed:
- Previous: hierarchical
- New: mesh
- Duration: 1.2s
- Agents migrated: 10/10
```

### Example 3: Request Distributed Decision

```bash
# Request consensus with custom timeout
/consensus-request "Deploy feature-x to production" 10000
```

**Expected Output**:
```
Consensus reached:
- Decision: APPROVED
- Vote breakdown: 8 yes, 2 abstain
- Duration: 3.4s
- Participating agents: 10
```

---

## State Persistence

### Session State Flow

```
1. Session Start
   ↓
   swarm_lifecycle.py (session_start)
   ↓
   Initialize SwarmCoordinator
   ↓
   Create session ID
   ↓
   Store in session-state.json

2. Task Execution
   ↓
   pre_swarm_task.py
   ↓
   Initialize coordination context
   ↓
   Execute task
   ↓
   post_swarm_task.py
   ↓
   Collect metrics & apply healing

3. Session End
   ↓
   swarm_lifecycle.py (session_end)
   ↓
   Persist to swarm-sessions.db
   ↓
   Cleanup resources
```

### Persistence Locations

| Data Type | File | Format |
|-----------|------|--------|
| Current session | `.moai/memory/moai-flow/session-state.json` | JSON |
| Session history | `.moai/memory/moai-flow/swarm-sessions.db` | SQLite |
| Performance metrics | `.moai/memory/moai-flow/latest-metrics.json` | JSON |
| Configuration | `.moai/config/moai-flow.json` | JSON |
| Hook config | `.claude/hooks/moai-flow/config.json` | JSON |

---

## Integration with MoAI-ADK

### Agent Delegation

MoAI-ADK agents can delegate to moai-flow agents using the Task() function:

```python
# Delegate to swarm coordinator
Task(
    subagent_type="coordinator-swarm",
    prompt="Initialize mesh topology for distributed task execution"
)

# Delegate to bottleneck optimizer
Task(
    subagent_type="optimizer-bottleneck",
    prompt="Analyze swarm performance and suggest optimizations"
)

# Delegate to consensus analyzer
Task(
    subagent_type="analyzer-consensus",
    prompt="Recommend consensus algorithm for high-availability system"
)

# Delegate to self-healer
Task(
    subagent_type="healer-self",
    prompt="Recover from agent failure in swarm session"
)
```

### Workflow Integration

MoAI-Flow integrates with MoAI-ADK workflows:

1. **Planning Phase** (`/moai:1-plan`): Coordinator analyzes task complexity and suggests swarm topology
2. **Implementation Phase** (`/moai:2-run`): Swarm executes distributed TDD cycles
3. **Documentation Phase** (`/moai:3-sync`): Collaborative documentation generation

---

## Troubleshooting

### Common Issues

#### Issue 1: Swarm Not Initializing

**Symptom**: `/swarm-init` fails with error

**Solutions**:
1. Check `.moai/config/moai-flow.json` exists
2. Verify `enabled: true` in config
3. Check Python path includes moai_flow module
4. Review logs in `.moai/logs/moai-flow/`

#### Issue 2: Consensus Timeout

**Symptom**: Consensus requests timing out

**Solutions**:
1. Increase timeout: `/consensus-request "proposal" 15000`
2. Check agent connectivity
3. Switch to faster consensus algorithm in config
4. Reduce swarm size

#### Issue 3: Performance Degradation

**Symptom**: Slow task execution

**Solutions**:
1. Check metrics: `/swarm-status`
2. Analyze bottlenecks with optimizer-bottleneck agent
3. Switch to more efficient topology
4. Enable predictive healing in config

---

## Configuration Reference

### Configuration Options

| Section | Option | Type | Default | Description |
|---------|--------|------|---------|-------------|
| `swarm` | `default_topology` | string | "mesh" | Default swarm topology |
| `swarm` | `max_agents` | number | 100 | Maximum agents in swarm |
| `swarm` | `consensus_algorithm` | string | "raft" | Default consensus algorithm |
| `coordination` | `conflict_resolution` | string | "automatic" | Conflict resolution strategy |
| `coordination` | `state_sync_interval_ms` | number | 1000 | State sync interval |
| `memory` | `semantic_enabled` | boolean | true | Enable semantic memory |
| `memory` | `episodic_enabled` | boolean | true | Enable episodic memory |
| `memory` | `context_hints_enabled` | boolean | true | Enable context hints |
| `optimization` | `bottleneck_detection` | boolean | true | Enable bottleneck detection |
| `optimization` | `self_healing` | boolean | true | Enable auto-healing |
| `optimization` | `pattern_learning` | boolean | true | Enable pattern learning |
| `optimization` | `predictive_healing` | boolean | true | Enable predictive healing |
| `monitoring` | `metrics_enabled` | boolean | true | Enable metrics collection |
| `monitoring` | `health_checks_enabled` | boolean | true | Enable health checks |

---

## Next Steps

- See [INTEGRATION.md](./INTEGRATION.md) for detailed Claude Code integration guide
- See [HOOKS.md](./HOOKS.md) for hook usage and customization
- Check `.claude/skills/moai-flow-*/` for skill documentation
- Review `.moai/config/moai-flow.json` for configuration options

---

## Version

**Current Version**: 1.0.0

**Last Updated**: 2025-11-30

**Compatibility**:
- MoAI-ADK: 0.30.2+
- Claude Code: Latest
- Python: 3.8+
