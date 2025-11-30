# Basic Coordination Examples

Simple consensus voting and state synchronization patterns for getting started with moai-flow-coordination.

## Example 1: Simple Majority Consensus

Basic quorum voting for deployment decisions.

```python
from moai_flow.core import SwarmCoordinator
from moai_flow.coordination import ConsensusManager

# Initialize swarm
coordinator = SwarmCoordinator(topology="mesh")

# Add agents to swarm
coordinator.add_agent("agent-1")
coordinator.add_agent("agent-2")
coordinator.add_agent("agent-3")

# Create consensus manager with default quorum algorithm
manager = ConsensusManager(coordinator, default_algorithm="quorum")

# Propose deployment
proposal = {
    "proposal_id": "deploy-v2.0",
    "action": "deploy",
    "version": "v2.0",
    "environment": "production"
}

# Request consensus (30 second timeout)
result = manager.request_consensus(proposal, timeout_ms=30000)

# Check decision
if result.decision == "approved":
    print(f"Deployment approved!")
    print(f"Votes: {result.votes_for} for, {result.votes_against} against")
    print(f"Participants: {result.participants}")
else:
    print(f"Deployment rejected")
```

**Output**:
```
Deployment approved!
Votes: 2 for, 1 against
Participants: ['agent-1', 'agent-2', 'agent-3']
```

---

## Example 2: State Synchronization

Synchronize a counter across all agents with CRDT conflict resolution.

```python
from moai_flow.core import SwarmCoordinator
from moai_flow.memory import MemoryProvider
from moai_flow.coordination import (
    StateSynchronizer,
    ConflictResolver,
    StateVersion,
    CRDTType
)
from datetime import datetime, timezone

# Setup
coordinator = SwarmCoordinator(topology="mesh")
memory = MemoryProvider()
resolver = ConflictResolver(strategy="crdt")

synchronizer = StateSynchronizer(
    coordinator=coordinator,
    memory=memory,
    conflict_resolver=resolver,
    default_timeout_ms=10000
)

# Agent 1 increments counter
agent1_state = StateVersion(
    state_key="task_count",
    value=42,
    version=1,
    timestamp=datetime.now(timezone.utc),
    agent_id="agent-1",
    metadata={"crdt_type": CRDTType.COUNTER.value}
)

# Agent 2 increments counter
agent2_state = StateVersion(
    state_key="task_count",
    value=38,
    version=1,
    timestamp=datetime.now(timezone.utc),
    agent_id="agent-2",
    metadata={"crdt_type": CRDTType.COUNTER.value}
)

# Synchronize (CRDT will sum both values)
success = synchronizer.synchronize_state(
    swarm_id="swarm-001",
    state_key="task_count",
    timeout_ms=10000
)

if success:
    # Retrieve synchronized state
    state = synchronizer.get_state("swarm-001", "task_count")
    print(f"Synchronized counter: {state.value}")  # 80 (42 + 38)
    print(f"Version: {state.version}")
```

**Output**:
```
Synchronized counter: 80
Version: 2
```

---

## Example 3: LWW Conflict Resolution

Simple last-write-wins for configuration updates.

```python
from moai_flow.coordination import ConflictResolver, StateVersion
from datetime import datetime, timezone

# Create resolver with LWW strategy
resolver = ConflictResolver(strategy="lww")

# Conflicting configuration updates
conflicts = [
    StateVersion(
        state_key="max_workers",
        value=10,
        version=1,
        timestamp=datetime(2025, 1, 1, 10, 0, 0, tzinfo=timezone.utc),
        agent_id="agent-1",
        metadata={}
    ),
    StateVersion(
        state_key="max_workers",
        value=15,
        version=2,
        timestamp=datetime(2025, 1, 1, 10, 0, 1, tzinfo=timezone.utc),
        agent_id="agent-2",
        metadata={}
    ),
    StateVersion(
        state_key="max_workers",
        value=12,
        version=3,
        timestamp=datetime(2025, 1, 1, 9, 59, 59, tzinfo=timezone.utc),
        agent_id="agent-3",
        metadata={}
    )
]

# Resolve conflicts
resolved = resolver.resolve("max_workers", conflicts)

print(f"Winner: agent-{resolved.agent_id}")
print(f"Value: {resolved.value}")  # 15 (newest timestamp)
print(f"Discarded: {resolved.metadata['discarded_versions']}")  # 2
```

**Output**:
```
Winner: agent-2
Value: 15
Discarded: 2
```

---

## Example 4: Delta Synchronization

Efficient incremental sync for reconnecting agents.

```python
from moai_flow.coordination import StateSynchronizer, ConflictResolver
from moai_flow.core import SwarmCoordinator
from moai_flow.memory import MemoryProvider

# Setup
coordinator = SwarmCoordinator()
memory = MemoryProvider()
resolver = ConflictResolver(strategy="lww")

synchronizer = StateSynchronizer(coordinator, memory, resolver)

# Agent was offline from version 5 to version 10
last_known_version = 5

# Fetch only changes since version 5
changes = synchronizer.delta_sync(
    swarm_id="swarm-001",
    since_version=last_known_version
)

print(f"Received {len(changes)} state updates")

# Apply changes
for change in changes:
    print(f"State '{change.state_key}' updated to v{change.version}")
    print(f"  New value: {change.value}")
    print(f"  Agent: {change.agent_id}")

# Update local last known version
new_last_version = max(c.version for c in changes)
print(f"Updated to version {new_last_version}")
```

**Output**:
```
Received 3 state updates
State 'task_count' updated to v7
  New value: 100
  Agent: coordinator
State 'agent_registry' updated to v9
  New value: {'agent-1': {...}, 'agent-2': {...}}
  Agent: coordinator
State 'metrics' updated to v10
  New value: {'cpu': 0.75, 'memory': 0.60}
  Agent: coordinator
Updated to version 10
```

---

## Example 5: Weighted Consensus

Expert-based voting with priority weights.

```python
from moai_flow.coordination import ConsensusManager, WeightedAlgorithm
from moai_flow.core import SwarmCoordinator

coordinator = SwarmCoordinator()
manager = ConsensusManager(coordinator)

# Define expert weights
agent_weights = {
    "expert-senior": 3.0,
    "expert-mid": 2.0,
    "expert-junior": 1.5,
    "agent-regular": 1.0
}

# Register weighted algorithm
weighted = WeightedAlgorithm(threshold=0.6, agent_weights=agent_weights)
manager.register_algorithm("weighted", weighted)

# Propose architecture change
proposal = {
    "proposal_id": "architecture-change",
    "action": "refactor",
    "component": "api-gateway"
}

# Request consensus with weighted voting
result = manager.request_consensus(proposal, algorithm="weighted")

print(f"Decision: {result.decision}")
print(f"Weighted approval: {result.metadata['weighted_approval']:.2%}")
print(f"Total weight: {result.metadata['total_weight']}")
```

**Output**:
```
Decision: approved
Weighted approval: 67%
Total weight: 7.5
```

---

## Example 6: Conflict Detection

Detect and list conflicting states across agents.

```python
from moai_flow.coordination import ConflictResolver, StateVersion
from datetime import datetime, timezone

resolver = ConflictResolver(strategy="lww")

# Agent states (same key, different values)
states = {
    "agent-1": StateVersion(
        "counter", 10, 1, datetime.now(timezone.utc), "agent-1", {}
    ),
    "agent-2": StateVersion(
        "counter", 12, 2, datetime.now(timezone.utc), "agent-2", {}
    ),
    "agent-3": StateVersion(
        "queue", ["task1"], 1, datetime.now(timezone.utc), "agent-3", {}
    )
}

# Detect conflicts
conflicts = resolver.detect_conflicts(states)

print(f"Conflicting state keys: {conflicts}")  # ["counter"]

# Resolve each conflict
for state_key in conflicts:
    conflicting_versions = [
        sv for sv in states.values() if sv.state_key == state_key
    ]

    resolved = resolver.resolve(state_key, conflicting_versions)
    print(f"Resolved '{state_key}': {resolved.value} (from {resolved.agent_id})")
```

**Output**:
```
Conflicting state keys: ['counter']
Resolved 'counter': 12 (from agent-2)
```

---

## Example 7: Statistics Tracking

Monitor consensus performance and approval rates.

```python
from moai_flow.coordination import ConsensusManager
from moai_flow.core import SwarmCoordinator

coordinator = SwarmCoordinator()
manager = ConsensusManager(coordinator, default_algorithm="quorum")

# Execute multiple consensus requests
proposals = [
    {"proposal_id": "deploy-1", "action": "deploy"},
    {"proposal_id": "rollback-1", "action": "rollback"},
    {"proposal_id": "scale-1", "action": "scale"}
]

for proposal in proposals:
    manager.request_consensus(proposal)

# Get statistics
stats = manager.get_algorithm_stats()

print(f"Total proposals: {stats['total_proposals']}")
print(f"Approved: {stats['approved']}")
print(f"Rejected: {stats['rejected']}")
print(f"Timeouts: {stats['timeouts']}")
print(f"Approval rate: {stats['approval_rate']:.2%}")
print(f"Average duration: {stats['avg_duration_ms']:.2f}ms")

# Per-algorithm stats
for algo_name, algo_stats in stats['by_algorithm'].items():
    print(f"\n{algo_name}:")
    print(f"  Proposals: {algo_stats['proposals']}")
    print(f"  Approval rate: {algo_stats['approval_rate']:.2%}")
```

**Output**:
```
Total proposals: 3
Approved: 2
Rejected: 1
Timeouts: 0
Approval rate: 67%
Average duration: 150.00ms

quorum:
  Proposals: 3
  Approval rate: 67%
```

---

## Example 8: Complete Pipeline

Full consensus → synchronization workflow.

```python
from moai_flow.core import SwarmCoordinator
from moai_flow.memory import MemoryProvider
from moai_flow.coordination import (
    ConsensusManager,
    ConflictResolver,
    StateSynchronizer
)

# Setup infrastructure
coordinator = SwarmCoordinator(topology="mesh")
memory = MemoryProvider()

# Initialize coordination components
consensus = ConsensusManager(coordinator, default_algorithm="quorum")
resolver = ConflictResolver(strategy="crdt")
synchronizer = StateSynchronizer(coordinator, memory, resolver)

# Workflow: Propose change → Vote → Sync state

# Step 1: Propose state update
proposal = {
    "proposal_id": "update-counter",
    "action": "increment",
    "state_key": "task_count",
    "value": 100
}

# Step 2: Request consensus
result = consensus.request_consensus(proposal, timeout_ms=10000)

print(f"Consensus: {result.decision}")

# Step 3: If approved, synchronize state
if result.decision == "approved":
    success = synchronizer.synchronize_state(
        swarm_id="swarm-001",
        state_key="task_count",
        timeout_ms=10000
    )

    if success:
        # Verify synchronized state
        state = synchronizer.get_state("swarm-001", "task_count")
        print(f"State synchronized: {state.value}")
        print(f"Version: {state.version}")
    else:
        print("Synchronization failed")
else:
    print("Proposal rejected, no synchronization")
```

**Output**:
```
Consensus: approved
State synchronized: 100
Version: 1
```

---

**Next**: [Multi-Agent Swarm Examples](multi-agent-swarm.md)
