---
name: moai-flow-coordination
description: Multi-agent coordination with consensus algorithms, conflict resolution, and state synchronization for distributed swarm intelligence
version: 1.0.0
updated: 2025-11-30
status: active
tags: coordination, consensus, swarm, distributed-systems, byzantine, gossip, state-sync
tools: Read, Bash, WebFetch, Grep, Glob
---

# MoAI Flow Coordination

Enterprise multi-agent coordination patterns for distributed swarm intelligence. Provides consensus algorithms, conflict resolution strategies, and state synchronization mechanisms for coordinating multiple AI agents working together.

## Quick Reference (30 seconds)

**What is MoAI Flow Coordination?**
Production-ready coordination layer for multi-agent systems with:

1. **Consensus Mechanisms** - Vote aggregation with multiple algorithms (Quorum, Weighted, Byzantine, Gossip)
2. **Conflict Resolution** - State conflict resolution via LWW, Vector Clocks, or CRDT strategies
3. **State Synchronization** - Distributed state sync across agent swarms with delta updates
4. **Fault Tolerance** - Byzantine fault tolerance and malicious agent detection

**Core Algorithms**:
- **Quorum** (simple/supermajority/unanimous) - Threshold-based voting
- **Weighted** - Priority-based voting with agent weights
- **Byzantine** - Fault-tolerant consensus (tolerates malicious agents)
- **Gossip** - Eventual consistency via epidemic propagation

**Quick Examples**:
```python
# Simple majority consensus
manager = ConsensusManager(coordinator, algorithm="quorum")
result = manager.request_consensus({"action": "deploy"}, timeout_ms=30000)

# Conflict resolution with CRDT
resolver = ConflictResolver(strategy="crdt")
resolved = resolver.resolve("counter", conflicting_states)

# State synchronization
synchronizer = StateSynchronizer(coordinator, memory, resolver)
synchronizer.synchronize_state("swarm-001", "task_queue")
```

**When to Use**:
- Multi-agent decision making requiring agreement
- Distributed state management across agent swarms
- Conflict resolution for concurrent state updates
- Byzantine fault tolerance for untrusted environments

**Module References**:
- [Consensus Algorithms](modules/consensus-algorithms.md) - Quorum, Byzantine, Gossip protocols
- [Conflict Resolution](modules/conflict-resolution.md) - LWW, Vector Clock, CRDT strategies
- [State Synchronization](modules/state-synchronization.md) - Full sync, delta sync, versioning
- [Task Delegation](modules/task-delegation.md) - Work distribution patterns

---

## Implementation Guide (5 minutes)

### 1. Consensus Manager - Multi-Algorithm Voting System

**Purpose**: Coordinate multi-agent decisions using pluggable consensus algorithms.

**Supported Algorithms**:

| Algorithm | Use Case | Complexity | Fault Tolerance |
|-----------|----------|------------|-----------------|
| **Quorum** | Simple voting | O(n) | No |
| **Weighted** | Priority-based | O(n) | No |
| **Byzantine** | Untrusted agents | O(n²) | Yes (f < n/3) |
| **Gossip** | Eventual consistency | O(n log n) | Yes |

**Basic Usage**:
```python
from moai_flow.coordination import ConsensusManager

# Initialize with coordinator
coordinator = SwarmCoordinator(topology="mesh")
manager = ConsensusManager(coordinator, default_algorithm="quorum")

# Request consensus decision
proposal = {
    "proposal_id": "deploy-v2.0",
    "action": "deploy",
    "version": "v2.0"
}
result = manager.request_consensus(proposal, timeout_ms=30000)

print(f"Decision: {result.decision}")  # "approved" or "rejected"
print(f"Votes: {result.votes_for} for, {result.votes_against} against")
print(f"Participants: {len(result.participants)}")
```

**Algorithm Selection Guide**:
```python
# Quorum - Simple majority (fastest, >50% threshold)
manager = ConsensusManager(coordinator, default_algorithm="quorum")
result = manager.request_consensus(proposal, algorithm="quorum")

# Weighted - Expert-based decisions (priority voting)
manager.register_algorithm("weighted", WeightedAlgorithm(
    threshold=0.6,
    agent_weights={"expert-1": 2.0, "expert-2": 1.5, "junior-1": 1.0}
))
result = manager.request_consensus(proposal, algorithm="weighted")

# Byzantine - Fault tolerance (tolerates malicious agents)
from moai_flow.coordination.algorithms import ByzantineConsensus
manager.register_algorithm("byzantine", ByzantineConsensus(fault_tolerance=1))
result = manager.request_consensus(proposal, algorithm="byzantine")

# Gossip - Eventual consistency (large-scale swarms)
from moai_flow.coordination.algorithms import GossipProtocol
manager.register_algorithm("gossip", GossipProtocol(fanout=3, rounds=5))
result = manager.request_consensus(proposal, algorithm="gossip")
```

**Vote Recording** (for agents responding to consensus requests):
```python
# Agent receives consensus_request broadcast
def on_consensus_request(message):
    proposal_id = message["proposal_id"]
    proposal = message["proposal"]

    # Agent makes decision
    vote = VoteType.FOR if analyze_proposal(proposal) else VoteType.AGAINST

    # Record vote with manager
    manager.record_vote(
        proposal_id=proposal_id,
        agent_id=self.agent_id,
        vote=vote,
        weight=1.0
    )
```

**Statistics Tracking**:
```python
stats = manager.get_algorithm_stats()
print(f"Total proposals: {stats['total_proposals']}")
print(f"Approval rate: {stats['approval_rate']:.2%}")
print(f"Average duration: {stats['avg_duration_ms']:.2f}ms")
```

---

### 2. Conflict Resolution - State Version Management

**Purpose**: Resolve conflicting state updates from multiple agents using configurable strategies.

**Resolution Strategies**:

| Strategy | Mechanism | Use Case | Guarantees |
|----------|-----------|----------|------------|
| **LWW** | Last-Write-Wins | Simple conflicts | Fast, eventual consistency |
| **Vector** | Vector clocks | Causality detection | Preserves causal order |
| **CRDT** | Semantic merge | Concurrent updates | Strong eventual consistency |

**Basic Usage**:
```python
from moai_flow.coordination import ConflictResolver, StateVersion
from datetime import datetime, timezone

# Initialize resolver with strategy
resolver = ConflictResolver(strategy="crdt")

# Create conflicting states
conflicts = [
    StateVersion(
        state_key="task_count",
        value=42,
        version=1,
        timestamp=datetime.now(timezone.utc),
        agent_id="agent-1",
        metadata={"crdt_type": "counter"}
    ),
    StateVersion(
        state_key="task_count",
        value=45,
        version=2,
        timestamp=datetime.now(timezone.utc),
        agent_id="agent-2",
        metadata={"crdt_type": "counter"}
    )
]

# Resolve conflicts
resolved = resolver.resolve("task_count", conflicts)
print(f"Resolved value: {resolved.value}")  # 87 (sum for counter CRDT)
```

**Strategy Selection**:
```python
# LWW - Timestamp-based (fastest, simple)
resolver = ConflictResolver(strategy="lww")
resolved = resolver.resolve("config", conflicts)
# Uses latest timestamp

# Vector Clock - Causality-aware
resolver = ConflictResolver(strategy="vector")
conflicts[0].metadata["vector_clock"] = {"agent-1": 5, "agent-2": 3}
conflicts[1].metadata["vector_clock"] = {"agent-1": 4, "agent-2": 6}
resolved = resolver.resolve("state", conflicts)
# Detects causal dominance

# CRDT - Semantic merge (most sophisticated)
resolver = ConflictResolver(strategy="crdt")
```

**CRDT Types**:
```python
from moai_flow.coordination import CRDTType

# Counter - Sum all values
conflicts[0].metadata["crdt_type"] = CRDTType.COUNTER.value
resolved = resolver.resolve("counter", conflicts)
# Result: sum of all counter values

# Set - Union of all sets
conflicts[0].value = {"task1", "task2"}
conflicts[1].value = {"task2", "task3"}
conflicts[0].metadata["crdt_type"] = CRDTType.SET.value
resolved = resolver.resolve("tasks", conflicts)
# Result: {"task1", "task2", "task3"}

# Map - LWW per key
conflicts[0].value = {"key1": "v1", "key2": "v2"}
conflicts[1].value = {"key2": "v3", "key3": "v4"}
conflicts[0].metadata["crdt_type"] = CRDTType.MAP.value
resolved = resolver.resolve("config", conflicts)
# Result: {"key1": "v1", "key2": "v3", "key3": "v4"} (LWW per key)
```

**Conflict Detection**:
```python
# Check for conflicts across agents
states = {
    "agent-1": StateVersion("counter", 10, 1, datetime.now(timezone.utc), "agent-1", {}),
    "agent-2": StateVersion("counter", 12, 2, datetime.now(timezone.utc), "agent-2", {})
}

conflicts = resolver.detect_conflicts(states)
print(f"Conflicting keys: {conflicts}")  # ["counter"]
```

---

### 3. State Synchronization - Distributed State Management

**Purpose**: Synchronize state across all agents in a swarm with conflict resolution and versioning.

**Synchronization Modes**:

| Mode | Description | Bandwidth | Use Case |
|------|-------------|-----------|----------|
| **Full Sync** | Broadcast all state | High | Initial sync, major updates |
| **Delta Sync** | Only changes since version N | Low | Incremental updates, reconnects |
| **Version Query** | Check current version | Minimal | Change detection |

**Basic Usage**:
```python
from moai_flow.coordination import StateSynchronizer

# Initialize synchronizer
coordinator = SwarmCoordinator()
memory = MemoryProvider()
resolver = ConflictResolver(strategy="crdt")

synchronizer = StateSynchronizer(
    coordinator=coordinator,
    memory=memory,
    conflict_resolver=resolver,
    default_timeout_ms=10000
)

# Full state synchronization
success = synchronizer.synchronize_state(
    swarm_id="swarm-001",
    state_key="task_queue",
    timeout_ms=10000
)

if success:
    print("State synchronized successfully")
```

**Synchronization Protocol**:
```python
# Protocol flow:
# 1. Broadcast state request to all agents
# 2. Collect state versions (with timeout)
# 3. Detect conflicts between versions
# 4. Resolve conflicts using ConflictResolver
# 5. Broadcast resolved state to all agents
# 6. Store in memory provider

# Example with full workflow
synchronizer.synchronize_state("swarm-001", "counter")
# -> Broadcasts state_request
# -> Agents respond with their state versions
# -> Conflicts detected and resolved
# -> Resolved state broadcasted back
# -> Stored in memory for persistence
```

**Delta Synchronization** (efficient for large swarms):
```python
# Agent reconnects after being offline
# Only fetch changes since last known version
changes = synchronizer.delta_sync(
    swarm_id="swarm-001",
    since_version=10
)

print(f"Received {len(changes)} state updates")
for change in changes:
    print(f"  {change.state_key} v{change.version}: {change.value}")
```

**Version Management**:
```python
# Check current state version
version = synchronizer.get_state_version("swarm-001", "task_queue")
print(f"Current version: {version}")

# Retrieve synchronized state
state = synchronizer.get_state("swarm-001", "task_queue")
if state:
    print(f"Value: {state.value}")
    print(f"Version: {state.version}")
    print(f"Timestamp: {state.timestamp}")
```

**State Cleanup**:
```python
# Clear specific state
synchronizer.clear_state("swarm-001", "temp_data")

# Clear all synchronized state for swarm
synchronizer.clear_state("swarm-001")
```

---

### 4. Integration Patterns

**Complete Coordination Pipeline**:
```python
from moai_flow.coordination import (
    ConsensusManager,
    ConflictResolver,
    StateSynchronizer
)
from moai_flow.core import SwarmCoordinator
from moai_flow.memory import MemoryProvider

# Setup coordination infrastructure
coordinator = SwarmCoordinator(topology="mesh")
memory = MemoryProvider()

# Consensus for decisions
consensus = ConsensusManager(coordinator, default_algorithm="quorum")

# Conflict resolution for state
resolver = ConflictResolver(strategy="crdt")

# State synchronization
synchronizer = StateSynchronizer(coordinator, memory, resolver)

# Workflow: Propose → Vote → Sync
proposal = {"action": "update_state", "key": "counter", "value": 100}
result = consensus.request_consensus(proposal)

if result.decision == "approved":
    # Synchronize the approved state change
    synchronizer.synchronize_state("swarm-001", "counter")
    print("State synchronized across swarm")
```

**Error Handling**:
```python
try:
    result = manager.request_consensus(proposal, timeout_ms=5000)
except ValueError as e:
    print(f"Invalid proposal: {e}")
except TimeoutError as e:
    print(f"Consensus timeout: {e}")

try:
    resolved = resolver.resolve("state", conflicts)
except ValueError as e:
    print(f"Resolution failed: {e}")
```

---

## Advanced Implementation (10+ minutes)

### Byzantine Fault Tolerance

**Byzantine Consensus** - Tolerates up to f malicious agents in n >= 3f+1 total agents:

```python
from moai_flow.coordination.algorithms import ByzantineConsensus
from moai_flow.coordination import Vote, VoteType

# Initialize Byzantine algorithm
# f=1 means tolerates 1 malicious agent
# Requires n >= 4 total agents (3*1 + 1)
byzantine = ByzantineConsensus(fault_tolerance=1, num_rounds=3)

# Register with consensus manager
manager.register_algorithm("byzantine", byzantine)

# Propose with Byzantine consensus
participants = ["agent-1", "agent-2", "agent-3", "agent-4"]
proposal_id = byzantine.propose(
    {"action": "critical_update"},
    participants
)

# Collect votes (including potentially malicious ones)
votes = [
    Vote("agent-1", VoteType.FOR),
    Vote("agent-2", VoteType.FOR),
    Vote("agent-3", VoteType.FOR),
    Vote("agent-4", VoteType.AGAINST)  # Potentially malicious
]

# Byzantine decision (requires 2f+1 = 3 agreements)
result = byzantine.decide(proposal_id, votes)

print(f"Decision: {result.decision}")
print(f"Malicious detected: {result.metadata['malicious_detected']}")
print(f"Malicious agents: {result.metadata['malicious_agents']}")
```

**Byzantine Requirements**:
- **n >= 3f+1**: Total agents must be at least 3 times fault tolerance plus 1
- **2f+1 agreement**: Requires 2f+1 votes for decision
- **Multi-round voting**: Minimum 3 rounds to detect vote changes
- **Malicious detection**: Identifies agents changing votes across rounds

**Configuration Examples**:
```python
# f=1, n>=4, threshold=3 (tolerate 1 malicious)
byzantine_f1 = ByzantineConsensus(fault_tolerance=1)

# f=2, n>=7, threshold=5 (tolerate 2 malicious)
byzantine_f2 = ByzantineConsensus(fault_tolerance=2)

# Higher rounds for stronger detection
byzantine_secure = ByzantineConsensus(fault_tolerance=1, num_rounds=5)
```

---

### Gossip Protocol - Eventual Consistency

**Gossip-based Consensus** - Probabilistic convergence for large-scale swarms:

```python
from moai_flow.coordination.algorithms import GossipProtocol

# Initialize gossip protocol
# fanout=3: Each agent shares with 3 random peers per round
# rounds=5: Maximum gossip propagation rounds
# convergence_threshold=0.95: 95% agreement needed
gossip = GossipProtocol(
    fanout=3,
    rounds=5,
    convergence_threshold=0.95
)

# Register with manager
manager.register_algorithm("gossip", gossip)

# Initial votes from all agents
votes = {
    f"agent-{i}": "approve" if i <= 7 else "reject"
    for i in range(1, 11)
}

# Gossip decision (eventual consistency)
result = gossip.decide(votes, threshold=0.66)

print(f"Decision: {result.decision}")
print(f"Rounds: {result.metadata['rounds_completed']}")
print(f"Converged: {result.metadata['converged']}")
print(f"Agreement: {result.metadata['agreement_ratio']:.2%}")
```

**Gossip Configuration**:
```python
# Standard configuration (medium networks 10-50 agents)
gossip_medium = GossipProtocol(fanout=3, rounds=5, convergence_threshold=0.95)

# High reliability (critical decisions)
gossip_critical = GossipProtocol(fanout=5, rounds=10, convergence_threshold=0.99)

# Fast convergence (large networks 100+ agents)
gossip_large = GossipProtocol(fanout=10, rounds=3, convergence_threshold=0.90)
```

**Gossip Algorithm**:
```
For each round (1 to max_rounds):
    For each agent:
        1. Select fanout random peers
        2. Share current vote with peers
        3. Update vote based on peer majority
    Check convergence (95%+ agreement)
    If converged → return decision
Return majority decision after max_rounds
```

**Convergence Metrics**:
- **O(log n)** rounds to convergence with high probability
- **O(n * log n)** total messages
- **Fault tolerant** - works with agent failures
- **No global coordination** - fully asynchronous

---

### Vector Clock Conflict Resolution

**Causal Ordering** with vector clocks:

```python
from datetime import datetime, timezone

resolver = ConflictResolver(strategy="vector")

# Create states with vector clocks
conflicts = [
    StateVersion(
        state_key="document",
        value="Version A",
        version=1,
        timestamp=datetime.now(timezone.utc),
        agent_id="agent-1",
        metadata={
            "vector_clock": {"agent-1": 5, "agent-2": 3}
        }
    ),
    StateVersion(
        state_key="document",
        value="Version B",
        version=2,
        timestamp=datetime.now(timezone.utc),
        agent_id="agent-2",
        metadata={
            "vector_clock": {"agent-1": 4, "agent-2": 6}
        }
    )
]

# Resolve with causality detection
resolved = resolver.resolve("document", conflicts)

# Check resolution strategy used
strategy = resolved.metadata.get("resolution_strategy")
if strategy == "vector_causal":
    print("Causal winner found")
elif strategy == "vector_concurrent_lww":
    print("Concurrent updates, fell back to LWW")
```

**Vector Clock Semantics**:
- **vc1[A] >= vc2[A]** for all agents → vc1 causally dominates vc2
- **Concurrent if neither dominates** → Fall back to LWW
- **Preserves happened-before relationships**

---

### CRDT Advanced Patterns

**Type-Specific CRDT Merging**:

```python
from moai_flow.coordination import CRDTType

# G-Counter (increment-only counter)
counter_conflicts = [
    StateVersion("counter", 42, 1, datetime.now(timezone.utc), "agent-1",
                 {"crdt_type": CRDTType.COUNTER.value}),
    StateVersion("counter", 45, 2, datetime.now(timezone.utc), "agent-2",
                 {"crdt_type": CRDTType.COUNTER.value})
]
resolved = resolver.resolve("counter", counter_conflicts)
# Result: 87 (42 + 45)

# G-Set (grow-only set)
set_conflicts = [
    StateVersion("tags", ["tag1", "tag2"], 1, datetime.now(timezone.utc), "agent-1",
                 {"crdt_type": CRDTType.SET.value}),
    StateVersion("tags", ["tag2", "tag3"], 2, datetime.now(timezone.utc), "agent-2",
                 {"crdt_type": CRDTType.SET.value})
]
resolved = resolver.resolve("tags", set_conflicts)
# Result: ["tag1", "tag2", "tag3"] (union)

# LWW-Map (last-write-wins per key)
map_conflicts = [
    StateVersion("config", {"key1": "v1", "key2": "v2"}, 1,
                 datetime(2025, 1, 1, tzinfo=timezone.utc), "agent-1",
                 {"crdt_type": CRDTType.MAP.value}),
    StateVersion("config", {"key2": "v3", "key3": "v4"}, 2,
                 datetime(2025, 1, 2, tzinfo=timezone.utc), "agent-2",
                 {"crdt_type": CRDTType.MAP.value})
]
resolved = resolver.resolve("config", map_conflicts)
# Result: {"key1": "v1", "key2": "v3", "key3": "v4"}
# key2 uses v3 (newer timestamp from agent-2)
```

**Custom CRDT Types**:
```python
# Auto-detect CRDT type from value
conflicts[0].value = 42  # Detected as COUNTER
conflicts[0].value = ["a", "b"]  # Detected as SET
conflicts[0].value = {"k": "v"}  # Detected as MAP
conflicts[0].value = "text"  # Detected as REGISTER (LWW)
```

---

### Performance Optimization

**Consensus Timeout Tuning**:
```python
# Fast consensus (local network)
result = manager.request_consensus(proposal, timeout_ms=5000)

# Standard consensus (distributed network)
result = manager.request_consensus(proposal, timeout_ms=30000)

# Patient consensus (unreliable network)
result = manager.request_consensus(proposal, timeout_ms=60000)
```

**State Sync Optimization**:
```python
# Use delta sync for reconnecting agents
last_version = agent.get_last_known_version()
changes = synchronizer.delta_sync("swarm-001", since_version=last_version)

# Apply only changed states
for change in changes:
    agent.update_state(change.state_key, change.value)
```

**Batch Synchronization**:
```python
# Sync multiple states efficiently
states_to_sync = ["counter", "task_queue", "agent_registry"]

for state_key in states_to_sync:
    synchronizer.synchronize_state("swarm-001", state_key, timeout_ms=5000)
```

---

## Works Well With

**MoAI-Flow Modules**:
- **moai-flow-core** - SwarmCoordinator, Agent interfaces, topology management
- **moai-flow-memory** - MemoryProvider for state persistence
- **moai-flow-messaging** - Message routing and broadcasting
- **moai-flow-orchestration** - High-level swarm orchestration patterns

**Coordination Stack**:
```
┌─────────────────────────────────────┐
│   Orchestration Layer               │
│   (Swarm workflows)                 │
├─────────────────────────────────────┤
│   Coordination Layer (THIS MODULE)  │
│   - Consensus algorithms            │
│   - Conflict resolution             │
│   - State synchronization           │
├─────────────────────────────────────┤
│   Messaging Layer                   │
│   (Message routing, broadcast)      │
├─────────────────────────────────────┤
│   Core Layer                        │
│   (Topology, agents, coordinator)   │
└─────────────────────────────────────┘
```

**External Tools**:
- **Redis** - Distributed state storage
- **etcd** - Consensus-based key-value store
- **ZooKeeper** - Coordination service
- **Kafka** - Event streaming for state changes

---

## Module Documentation

- [Consensus Algorithms](modules/consensus-algorithms.md) - Deep dive into Quorum, Byzantine, Gossip, Weighted algorithms
- [Conflict Resolution](modules/conflict-resolution.md) - LWW, Vector Clock, CRDT strategies explained
- [State Synchronization](modules/state-synchronization.md) - Full sync, delta sync, version management
- [Task Delegation](modules/task-delegation.md) - Work distribution and load balancing patterns

## Examples

- [Basic Coordination](examples/basic-coordination.md) - Simple consensus and state sync
- [Multi-Agent Swarm](examples/multi-agent-swarm.md) - Complete swarm coordination workflow
- [Advanced Consensus](examples/advanced-consensus.md) - Byzantine, Gossip, CRDT examples

---

**Version**: 1.0.0
**Status**: Production Ready
**Phase**: Phase 6B Complete
**Lines**: 495 (within 500-line limit)
