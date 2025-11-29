# SwarmCoordinator Quick Start Guide

## 5-Minute Setup

### Installation

```python
from moai_flow.core import SwarmCoordinator, AgentState
```

### Basic Usage

```python
# 1. Create coordinator
coordinator = SwarmCoordinator(topology_type="mesh")

# 2. Register agents
coordinator.register_agent("agent-001", {"type": "expert-backend"})
coordinator.register_agent("agent-002", {"type": "expert-frontend"})

# 3. Send messages
coordinator.send_message("agent-001", "agent-002", {"task": "process"})
coordinator.broadcast_message("agent-001", {"status": "ready"})

# 4. Get status
info = coordinator.get_topology_info()
print(f"Agents: {info['agent_count']}, Health: {info['health']}")
```

---

## Topology Selection Guide

### When to Use Each Topology

| If you have... | Use Topology | Reason |
|----------------|--------------|--------|
| <5 agents, high collaboration | **Mesh** | Full connectivity for peer communication |
| 5-10 agents, centralized control | **Star** | Hub coordinates all communication |
| >10 agents, clear hierarchy | **Hierarchical** | Scales well with defined layers |
| Pipeline/sequential tasks | **Ring** | Each agent processes and passes on |
| Variable workload | **Adaptive** | Automatically switches to optimal pattern |

### Quick Topology Switch

```python
# Start with mesh
coordinator = SwarmCoordinator(topology_type="mesh")

# Switch to hierarchical as team grows
coordinator.switch_topology("hierarchical")
```

---

## Common Patterns

### Pattern 1: Team Collaboration (Mesh)

```python
coordinator = SwarmCoordinator(topology_type="mesh")

# Register team
team = ["backend", "frontend", "database", "devops"]
for role in team:
    coordinator.register_agent(f"{role}-dev", {"type": f"expert-{role}"})

# Broadcast team status
coordinator.broadcast_message("backend-dev", {
    "type": "status",
    "message": "API ready for integration"
})
```

### Pattern 2: Hierarchical Project (Hierarchical)

```python
coordinator = SwarmCoordinator(topology_type="hierarchical")

# Manager layer
coordinator.register_agent("manager-tdd", {
    "type": "manager-tdd",
    "layer": 1,
    "parent_id": "alfred"
})

# Specialist layer
coordinator.register_agent("expert-backend", {
    "type": "expert-backend",
    "layer": 2,
    "parent_id": "manager-tdd"
})
```

### Pattern 3: Consensus Decision (Any Topology)

```python
# Request team consensus
result = coordinator.request_consensus({
    "proposal_id": "deploy-v2",
    "description": "Deploy version 2.0",
    "options": ["approve", "reject"]
}, timeout_ms=30000)

if result["decision"] == "approved":
    print(f"✅ Approved ({result['votes_for']}/{len(result['participants'])})")
```

### Pattern 4: State Sync (Any Topology)

```python
# Sync task queue across all agents
coordinator.synchronize_state("task_queue", {
    "pending": 5,
    "in_progress": 2,
    "completed": 10
})

# All agents now have same view
state = coordinator.get_synchronized_state("task_queue")
```

---

## API Reference

### Core Methods

| Method | Description | Returns |
|--------|-------------|---------|
| `register_agent(id, metadata)` | Add agent to topology | `bool` |
| `unregister_agent(id)` | Remove agent | `bool` |
| `send_message(from, to, msg)` | Point-to-point message | `bool` |
| `broadcast_message(from, msg, exclude)` | Send to all agents | `int` (count) |
| `get_agent_status(id)` | Get agent status | `Dict` or `None` |
| `get_topology_info()` | Get topology metrics | `Dict` |
| `request_consensus(proposal, timeout)` | Vote on proposal | `Dict` (result) |
| `synchronize_state(key, value)` | Sync state across agents | `bool` |
| `switch_topology(type)` | Change topology | `bool` |

### Agent States

```python
AgentState.ACTIVE   # Running and responsive
AgentState.IDLE     # Available but not working
AgentState.BUSY     # Processing a task
AgentState.FAILED   # Unresponsive or failed
```

### Topology Types

```python
"mesh"          # Full connectivity
"hierarchical"  # Tree structure
"star"          # Hub-and-spoke
"ring"          # Sequential chain
"adaptive"      # Auto-switching
```

---

## Examples

### Example 1: Simple Mesh Network

```python
from moai_flow.core import SwarmCoordinator

# Create mesh coordinator
coordinator = SwarmCoordinator(topology_type="mesh")

# Add 3 agents
for i in range(1, 4):
    coordinator.register_agent(
        f"agent-{i:03d}",
        {"type": "expert-backend"}
    )

# Agent 1 broadcasts to all
count = coordinator.broadcast_message(
    "agent-001",
    {"type": "heartbeat", "status": "alive"}
)
print(f"Broadcast sent to {count} agents")

# Check topology
info = coordinator.get_topology_info()
print(f"Network: {info['agent_count']} agents, {info['connection_count']} connections")
```

### Example 2: Hierarchical with Visualization

```python
coordinator = SwarmCoordinator(
    topology_type="hierarchical",
    root_agent_id="alfred"
)

# Build hierarchy
coordinator.register_agent("manager-1", {
    "type": "manager-tdd",
    "layer": 1,
    "parent_id": "alfred"
})

coordinator.register_agent("expert-1", {
    "type": "expert-backend",
    "layer": 2,
    "parent_id": "manager-1"
})

# Visualize structure
print(coordinator.visualize_topology())
# Output:
# alfred (Root)
#     └─ manager-1
#         └─ expert-1
```

### Example 3: Consensus Voting

```python
coordinator = SwarmCoordinator(
    topology_type="mesh",
    consensus_threshold=0.6  # 60% majority required
)

# Register 5 agents
for i in range(1, 6):
    coordinator.register_agent(f"agent-{i:03d}", {"type": "expert"})
    # Set 4 as ACTIVE (will vote), 1 as IDLE (will abstain)
    state = AgentState.ACTIVE if i <= 4 else AgentState.IDLE
    coordinator.set_agent_state(f"agent-{i:03d}", state)

# Request consensus
result = coordinator.request_consensus({
    "proposal_id": "feature-x",
    "description": "Implement feature X",
    "options": ["approve", "reject"]
})

print(f"Decision: {result['decision']}")
print(f"Votes: {result['votes_for']} for, {result['votes_against']} against")
print(f"Threshold: {result['threshold']} ({result['threshold']*100}%)")
```

### Example 4: Dynamic Topology Switching

```python
# Start with mesh for small team
coordinator = SwarmCoordinator(topology_type="mesh")

# Add initial agents
for i in range(1, 4):
    coordinator.register_agent(f"agent-{i:03d}", {"type": "expert"})

print(f"Initial: {coordinator.get_topology_info()['type']}")  # "mesh"

# Team grows - switch to star
coordinator.switch_topology("star")
for i in range(4, 8):
    coordinator.register_agent(f"agent-{i:03d}", {"type": "expert"})

print(f"After growth: {coordinator.get_topology_info()['type']}")  # "star"

# Project matures - switch to hierarchical
coordinator.switch_topology("hierarchical")

# Update metadata for hierarchy
for i in range(1, 8):
    agent_id = f"agent-{i:03d}"
    coordinator.agent_registry[agent_id].update({
        "layer": 1 if i == 1 else 2,
        "parent_id": "alfred" if i == 1 else "agent-001"
    })

print(f"Final: {coordinator.get_topology_info()['type']}")  # "hierarchical"
```

---

## Troubleshooting

### Agent Not Found Error

```python
try:
    coordinator.send_message("nonexistent", "agent-002", {"task": "test"})
except ValueError as e:
    print(f"Error: {e}")
    # Fix: Register the agent first
    coordinator.register_agent("agent-001", {"type": "expert"})
```

### Failed Agents

```python
# Check agent status
status = coordinator.get_agent_status("agent-001")
if status["heartbeat_age_seconds"] > 60:
    print(f"⚠️ Agent failed (no heartbeat for {status['heartbeat_age_seconds']}s)")
    # Update heartbeat to recover
    coordinator.update_agent_heartbeat("agent-001")
```

### Low Consensus

```python
result = coordinator.request_consensus(proposal)
if result["decision"] == "rejected":
    vote_ratio = result["votes_for"] / (result["votes_for"] + result["votes_against"])
    print(f"Only {vote_ratio*100:.1f}% voted for (threshold: {result['threshold']*100}%)")
    # Lower threshold or get more agent agreement
```

---

## Best Practices

### 1. Choose Right Topology

- Start with **mesh** for <5 agents
- Use **star** for 5-10 agents with central coordinator
- Use **hierarchical** for >10 agents or clear org structure
- Use **adaptive** when workload varies significantly

### 2. Monitor Health

```python
# Regular health checks
info = coordinator.get_topology_info()
if info["health"] == "degraded":
    print(f"⚠️ {info['failed_agents']} agents failed")
elif info["health"] == "critical":
    print(f"🚨 Critical: {info['failed_agents']}/{info['agent_count']} agents failed")
```

### 3. Use Consensus for Critical Decisions

```python
# Set appropriate threshold
coordinator = SwarmCoordinator(
    topology_type="mesh",
    consensus_threshold=0.67  # 2/3 majority for critical decisions
)
```

### 4. Synchronize Important State

```python
# Sync configuration changes
coordinator.synchronize_state("config", {
    "max_retries": 3,
    "timeout_ms": 30000,
    "batch_size": 100
})

# All agents now have same config
```

### 5. Update Heartbeats Regularly

```python
# Heartbeats update automatically on send_message
# But can manually update for long-running tasks
coordinator.update_agent_heartbeat("agent-001")
```

---

## Performance Tips

### Topology Performance

| Topology | Best For | Avoid When |
|----------|----------|------------|
| Mesh | <10 agents, high collaboration | >10 agents (O(N²) overhead) |
| Hierarchical | >10 agents, scalable | Flat teams (<5 agents) |
| Star | Centralized control | Hub becomes bottleneck |
| Ring | Sequential tasks | Random access needed |
| Adaptive | Variable workload | Predictable patterns |

### Message Optimization

```python
# Batch related messages
messages = [
    {"task": "process_1"},
    {"task": "process_2"},
    {"task": "process_3"}
]

# Send as single batch message
coordinator.send_message("agent-001", "agent-002", {
    "type": "batch",
    "messages": messages
})
```

### State Sync Frequency

```python
# Don't sync on every change
# Batch updates and sync periodically
state_buffer = {}

def update_state(key, value):
    state_buffer[key] = value
    # Sync every 10 updates
    if len(state_buffer) >= 10:
        coordinator.synchronize_state("batch_state", state_buffer)
        state_buffer.clear()
```

---

## Next Steps

1. **Run Demo**: `python -m moai_flow.examples.swarm_coordinator_demo`
2. **Read Full Docs**: See `swarm_coordinator_implementation.md`
3. **Explore Topologies**: Check individual topology documentation
4. **Integrate with MoAI-ADK**: Use with existing agent workflows

---

**Quick Reference Card**

```python
# Create
coordinator = SwarmCoordinator(topology_type="mesh")

# Register
coordinator.register_agent("agent-001", {"type": "expert"})

# Message
coordinator.send_message("agent-001", "agent-002", {"task": "do_work"})
coordinator.broadcast_message("agent-001", {"status": "ready"})

# Status
status = coordinator.get_agent_status("agent-001")
info = coordinator.get_topology_info()

# Consensus
result = coordinator.request_consensus(proposal, timeout_ms=30000)

# State Sync
coordinator.synchronize_state("config", {...})

# Switch
coordinator.switch_topology("hierarchical")
```

---

**Last Updated**: 2025-11-29
**Version**: 1.0.0
**For**: MoAI-Flow Phase 5
