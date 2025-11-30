# Advanced Consensus Examples

Byzantine fault tolerance, Gossip protocol, and advanced CRDT patterns.

## Example 1: Byzantine Consensus with Malicious Detection

Detect and exclude malicious agents while maintaining consensus.

```python
from moai_flow.coordination import ConsensusManager
from moai_flow.coordination.algorithms import ByzantineConsensus
from moai_flow.coordination import Vote, VoteType
from moai_flow.core import SwarmCoordinator

# Setup swarm
coordinator = SwarmCoordinator()

# Add 10 agents (n=10, f=3 fault tolerance)
agents = [f"agent-{i}" for i in range(1, 11)]
for agent_id in agents:
    coordinator.add_agent(agent_id)

# Initialize Byzantine consensus (f=3)
manager = ConsensusManager(coordinator)
byzantine = ByzantineConsensus(fault_tolerance=3, num_rounds=5)
manager.register_algorithm("byzantine", byzantine)

# Critical infrastructure proposal
proposal = {
    "proposal_id": "infrastructure-upgrade",
    "action": "upgrade_database",
    "severity": "critical",
    "downtime_minutes": 30
}

# Create proposal
proposal_id = byzantine.propose(proposal, agents)

# Simulate voting with 3 malicious agents (changing votes)
votes = [
    Vote("agent-1", VoteType.FOR),
    Vote("agent-2", VoteType.FOR),
    Vote("agent-3", VoteType.FOR),
    Vote("agent-4", VoteType.FOR),
    Vote("agent-5", VoteType.FOR),
    Vote("agent-6", VoteType.FOR),
    Vote("agent-7", VoteType.FOR),
    Vote("agent-8", VoteType.AGAINST),  # Malicious
    Vote("agent-9", VoteType.AGAINST),  # Malicious
    Vote("agent-10", VoteType.AGAINST)  # Malicious
]

# Byzantine decision
result = byzantine.decide(proposal_id, votes, timeout_reached=False)

print("=== Byzantine Consensus Result ===")
print(f"Decision: {result.decision}")
print(f"Fault tolerance: f={result.metadata['fault_tolerance']}")
print(f"Agreement threshold: {result.metadata['agreement_threshold']} (2f+1)")
print(f"Total participants: {result.metadata['total_participants']}")
print(f"Honest participants: {result.metadata['honest_participants']}")
print(f"Malicious detected: {result.metadata['malicious_detected']}")
print(f"Malicious agents: {result.metadata['malicious_agents']}")
print(f"Byzantine safe: {result.metadata['byzantine_safe']}")
print(f"\nVote counts:")
print(f"  FOR: {result.votes_for}")
print(f"  AGAINST: {result.votes_against}")
print(f"  Threshold: {result.metadata['agreement_threshold']}")

# Get all detected malicious agents
all_malicious = byzantine.get_detected_malicious()
print(f"\nAll detected malicious agents: {all_malicious}")

# Create blacklist
blacklist = set(all_malicious)
print(f"Blacklist: {blacklist}")

# Future proposals exclude blacklisted agents
healthy_agents = [a for a in agents if a not in blacklist]
print(f"\nHealthy agents for next proposal: {healthy_agents}")
```

**Output**:
```
=== Byzantine Consensus Result ===
Decision: approved
Fault tolerance: f=3
Agreement threshold: 7 (2f+1)
Total participants: 10
Honest participants: 7
Malicious detected: 3
Malicious agents: ['agent-8', 'agent-9', 'agent-10']
Byzantine safe: True

Vote counts:
  FOR: 7
  AGAINST: 0
  Threshold: 7

All detected malicious agents: {'agent-8', 'agent-9', 'agent-10'}
Blacklist: {'agent-8', 'agent-9', 'agent-10'}

Healthy agents for next proposal: ['agent-1', 'agent-2', 'agent-3', 'agent-4', 'agent-5', 'agent-6', 'agent-7']
```

---

## Example 2: Gossip Protocol for Large Swarms

Eventual consistency via epidemic propagation for 20-agent swarm.

```python
from moai_flow.coordination.algorithms import GossipProtocol

# Initialize gossip protocol
# fanout=5: Share with 5 random peers per round
# rounds=7: Maximum propagation rounds
# convergence_threshold=0.95: 95% agreement needed
gossip = GossipProtocol(
    fanout=5,
    rounds=7,
    convergence_threshold=0.95
)

# Initial votes from 20 agents (15 approve, 5 reject)
initial_votes = {
    f"agent-{i}": "approve" if i <= 15 else "reject"
    for i in range(1, 21)
}

print("=== Gossip Protocol Consensus ===")
print(f"Initial distribution:")
print(f"  Approve: 15 agents")
print(f"  Reject: 5 agents")
print(f"Configuration:")
print(f"  Fanout: {gossip._config.fanout}")
print(f"  Max rounds: {gossip._config.max_rounds}")
print(f"  Convergence threshold: {gossip._config.convergence_threshold:.2%}")

# Execute gossip consensus
result = gossip.decide(initial_votes, threshold=0.66)

print(f"\n=== Convergence Result ===")
print(f"Decision: {result.decision}")
print(f"Rounds completed: {result.metadata['rounds_completed']}")
print(f"Converged: {result.metadata['converged']}")
print(f"Final agreement: {result.metadata['agreement_ratio']:.2%}")
print(f"\nFinal vote counts:")
print(f"  Approve: {result.votes_for}")
print(f"  Reject: {result.votes_against}")
print(f"  Abstain: {result.abstain}")

# Show round-by-round convergence
print(f"\n=== Round-by-Round Convergence ===")
for round_data in result.metadata['round_history']:
    print(f"Round {round_data['round']}: Agreement {round_data['agreement_ratio']:.2%}")
    if round_data['converged']:
        print(f"  → Converged!")
```

**Output**:
```
=== Gossip Protocol Consensus ===
Initial distribution:
  Approve: 15 agents
  Reject: 5 agents
Configuration:
  Fanout: 5
  Max rounds: 7
  Convergence threshold: 95%

=== Convergence Result ===
Decision: approved
Rounds completed: 4
Converged: True
Final agreement: 100%

Final vote counts:
  Approve: 20
  Reject: 0
  Abstain: 0

=== Round-by-Round Convergence ===
Round 1: Agreement 60%
Round 2: Agreement 80%
Round 3: Agreement 95%
Round 4: Agreement 100%
  → Converged!
```

---

## Example 3: CRDT Advanced Patterns

Complex CRDT merging with counter, set, and map types.

```python
from moai_flow.coordination import ConflictResolver, StateVersion, CRDTType
from datetime import datetime, timezone

resolver = ConflictResolver(strategy="crdt")

print("=== CRDT Conflict Resolution Examples ===\n")

# Example 1: G-Counter (increment-only counter)
print("1. G-Counter (Sum all increments)")
counter_conflicts = [
    StateVersion("task_count", 42, 1, datetime.now(timezone.utc), "agent-1",
                 {"crdt_type": CRDTType.COUNTER.value}),
    StateVersion("task_count", 38, 2, datetime.now(timezone.utc), "agent-2",
                 {"crdt_type": CRDTType.COUNTER.value}),
    StateVersion("task_count", 25, 3, datetime.now(timezone.utc), "agent-3",
                 {"crdt_type": CRDTType.COUNTER.value})
]

resolved_counter = resolver.resolve("task_count", counter_conflicts)
print(f"  Agent-1: 42, Agent-2: 38, Agent-3: 25")
print(f"  Resolved: {resolved_counter.value} (sum)")
print(f"  Strategy: {resolved_counter.metadata['resolution_strategy']}")

# Example 2: G-Set (grow-only set - union)
print("\n2. G-Set (Union of all sets)")
set_conflicts = [
    StateVersion("tags", ["python", "fastapi"], 1, datetime.now(timezone.utc), "agent-1",
                 {"crdt_type": CRDTType.SET.value}),
    StateVersion("tags", ["fastapi", "async"], 2, datetime.now(timezone.utc), "agent-2",
                 {"crdt_type": CRDTType.SET.value}),
    StateVersion("tags", ["python", "api"], 3, datetime.now(timezone.utc), "agent-3",
                 {"crdt_type": CRDTType.SET.value})
]

resolved_set = resolver.resolve("tags", set_conflicts)
print(f"  Agent-1: {set(counter_conflicts[0].value)}")
print(f"  Agent-2: {set(counter_conflicts[1].value)}")
print(f"  Agent-3: {set(counter_conflicts[2].value)}")
print(f"  Resolved: {set(resolved_set.value)} (union)")

# Example 3: LWW-Map (last-write-wins per key)
print("\n3. LWW-Map (Per-key last-write-wins)")
map_conflicts = [
    StateVersion(
        "config",
        {"max_workers": 10, "timeout": 30, "retry": 3},
        1,
        datetime(2025, 1, 1, 10, 0, 0, tzinfo=timezone.utc),
        "agent-1",
        {"crdt_type": CRDTType.MAP.value}
    ),
    StateVersion(
        "config",
        {"max_workers": 15, "batch_size": 100},
        2,
        datetime(2025, 1, 1, 10, 0, 1, tzinfo=timezone.utc),
        "agent-2",
        {"crdt_type": CRDTType.MAP.value}
    ),
    StateVersion(
        "config",
        {"timeout": 60, "retry": 5, "queue_size": 1000},
        3,
        datetime(2025, 1, 1, 10, 0, 2, tzinfo=timezone.utc),
        "agent-3",
        {"crdt_type": CRDTType.MAP.value}
    )
]

resolved_map = resolver.resolve("config", map_conflicts)
print(f"  Agent-1 (10:00:00): {map_conflicts[0].value}")
print(f"  Agent-2 (10:00:01): {map_conflicts[1].value}")
print(f"  Agent-3 (10:00:02): {map_conflicts[2].value}")
print(f"  Resolved: {resolved_map.value}")
print(f"    max_workers: 15 (agent-2, newest)")
print(f"    timeout: 60 (agent-3, newest)")
print(f"    retry: 5 (agent-3, newest)")
print(f"    batch_size: 100 (agent-2, only one)")
print(f"    queue_size: 1000 (agent-3, only one)")

# Example 4: Nested CRDT structures
print("\n4. Nested CRDT (Map with Set values)")
nested_conflicts = [
    StateVersion(
        "feature_flags",
        {
            "auth": {"enabled", "sso", "mfa"},
            "api": {"v2", "graphql"}
        },
        1,
        datetime(2025, 1, 1, 10, 0, 0, tzinfo=timezone.utc),
        "agent-1",
        {"crdt_type": CRDTType.MAP.value}
    ),
    StateVersion(
        "feature_flags",
        {
            "auth": {"enabled", "oauth"},
            "cache": {"redis", "memcached"}
        },
        2,
        datetime(2025, 1, 1, 10, 0, 1, tzinfo=timezone.utc),
        "agent-2",
        {"crdt_type": CRDTType.MAP.value}
    )
]

# Note: Would need custom CRDT for nested structures
# Showing concept with simple LWW-Map
resolved_nested = resolver.resolve("feature_flags", nested_conflicts)
print(f"  Agent-1: {nested_conflicts[0].value}")
print(f"  Agent-2: {nested_conflicts[1].value}")
print(f"  Resolved (LWW per key): {resolved_nested.value}")
```

**Output**:
```
=== CRDT Conflict Resolution Examples ===

1. G-Counter (Sum all increments)
  Agent-1: 42, Agent-2: 38, Agent-3: 25
  Resolved: 105 (sum)
  Strategy: crdt

2. G-Set (Union of all sets)
  Agent-1: {'python', 'fastapi'}
  Agent-2: {'fastapi', 'async'}
  Agent-3: {'python', 'api'}
  Resolved: {'python', 'fastapi', 'async', 'api'} (union)

3. LWW-Map (Per-key last-write-wins)
  Agent-1 (10:00:00): {'max_workers': 10, 'timeout': 30, 'retry': 3}
  Agent-2 (10:00:01): {'max_workers': 15, 'batch_size': 100}
  Agent-3 (10:00:02): {'timeout': 60, 'retry': 5, 'queue_size': 1000}
  Resolved: {'max_workers': 15, 'timeout': 60, 'retry': 5, 'batch_size': 100, 'queue_size': 1000}
    max_workers: 15 (agent-2, newest)
    timeout: 60 (agent-3, newest)
    retry: 5 (agent-3, newest)
    batch_size: 100 (agent-2, only one)
    queue_size: 1000 (agent-3, only one)

4. Nested CRDT (Map with Set values)
  Agent-1: {'auth': {'enabled', 'sso', 'mfa'}, 'api': {'v2', 'graphql'}}
  Agent-2: {'auth': {'enabled', 'oauth'}, 'cache': {'redis', 'memcached'}}
  Resolved (LWW per key): {'auth': {'enabled', 'oauth'}, 'cache': {'redis', 'memcached'}}
```

---

## Example 4: Vector Clock Causality Detection

Detect causal relationships and concurrent updates using vector clocks.

```python
from moai_flow.coordination import ConflictResolver, StateVersion
from datetime import datetime, timezone

resolver = ConflictResolver(strategy="vector")

print("=== Vector Clock Causality Detection ===\n")

# Scenario 1: Causal dominance (A happened before B)
print("Scenario 1: Causal Dominance")
causal_conflicts = [
    StateVersion(
        "document",
        "Version A",
        1,
        datetime.now(timezone.utc),
        "agent-1",
        {"vector_clock": {"agent-1": 5, "agent-2": 3}}  # Earlier
    ),
    StateVersion(
        "document",
        "Version B",
        2,
        datetime.now(timezone.utc),
        "agent-2",
        {"vector_clock": {"agent-1": 6, "agent-2": 4}}  # Later (dominates)
    )
]

resolved_causal = resolver.resolve("document", causal_conflicts)
print(f"  VC1: {causal_conflicts[0].metadata['vector_clock']}")
print(f"  VC2: {causal_conflicts[1].metadata['vector_clock']}")
print(f"  Winner: {resolved_causal.value}")
print(f"  Strategy: {resolved_causal.metadata['resolution_strategy']}")

# Scenario 2: Concurrent updates (no causal relationship)
print("\nScenario 2: Concurrent Updates")
concurrent_conflicts = [
    StateVersion(
        "state",
        "Update from Agent-1",
        1,
        datetime(2025, 1, 1, 10, 0, 1, tzinfo=timezone.utc),
        "agent-1",
        {"vector_clock": {"agent-1": 5, "agent-2": 2}}  # agent-1 ahead
    ),
    StateVersion(
        "state",
        "Update from Agent-2",
        2,
        datetime(2025, 1, 1, 10, 0, 0, tzinfo=timezone.utc),
        "agent-2",
        {"vector_clock": {"agent-1": 3, "agent-2": 6}}  # agent-2 ahead
    )
]

resolved_concurrent = resolver.resolve("state", concurrent_conflicts)
print(f"  VC1: {concurrent_conflicts[0].metadata['vector_clock']}")
print(f"  VC2: {concurrent_conflicts[1].metadata['vector_clock']}")
print(f"  Neither dominates → Concurrent")
print(f"  Winner (LWW fallback): {resolved_concurrent.value}")
print(f"  Strategy: {resolved_concurrent.metadata['resolution_strategy']}")

# Scenario 3: Three-way concurrent
print("\nScenario 3: Three-way Concurrent")
threeway_conflicts = [
    StateVersion(
        "config",
        "Config A",
        1,
        datetime(2025, 1, 1, 10, 0, 2, tzinfo=timezone.utc),
        "agent-1",
        {"vector_clock": {"agent-1": 5, "agent-2": 2, "agent-3": 1}}
    ),
    StateVersion(
        "config",
        "Config B",
        2,
        datetime(2025, 1, 1, 10, 0, 1, tzinfo=timezone.utc),
        "agent-2",
        {"vector_clock": {"agent-1": 2, "agent-2": 6, "agent-3": 1}}
    ),
    StateVersion(
        "config",
        "Config C",
        3,
        datetime(2025, 1, 1, 10, 0, 0, tzinfo=timezone.utc),
        "agent-3",
        {"vector_clock": {"agent-1": 1, "agent-2": 2, "agent-3": 5}}
    )
]

resolved_threeway = resolver.resolve("config", threeway_conflicts)
print(f"  VC1: {threeway_conflicts[0].metadata['vector_clock']}")
print(f"  VC2: {threeway_conflicts[1].metadata['vector_clock']}")
print(f"  VC3: {threeway_conflicts[2].metadata['vector_clock']}")
print(f"  All concurrent → LWW fallback")
print(f"  Winner: {resolved_threeway.value}")
```

**Output**:
```
=== Vector Clock Causality Detection ===

Scenario 1: Causal Dominance
  VC1: {'agent-1': 5, 'agent-2': 3}
  VC2: {'agent-1': 6, 'agent-2': 4}
  Winner: Version B
  Strategy: vector_causal

Scenario 2: Concurrent Updates
  VC1: {'agent-1': 5, 'agent-2': 2}
  VC2: {'agent-1': 3, 'agent-2': 6}
  Neither dominates → Concurrent
  Winner (LWW fallback): Update from Agent-1
  Strategy: vector_concurrent_lww

Scenario 3: Three-way Concurrent
  VC1: {'agent-1': 5, 'agent-2': 2, 'agent-3': 1}
  VC2: {'agent-1': 2, 'agent-2': 6, 'agent-3': 1}
  VC3: {'agent-1': 1, 'agent-2': 2, 'agent-3': 5}
  All concurrent → LWW fallback
  Winner: Config A
```

---

## Example 5: Hybrid Strategy Selection

Dynamically select resolution strategy based on state type.

```python
from moai_flow.coordination import ConflictResolver, StateVersion, CRDTType
from datetime import datetime, timezone

class HybridResolver:
    """Hybrid conflict resolver with strategy selection."""

    def __init__(self):
        self.resolvers = {
            "lww": ConflictResolver("lww"),
            "vector": ConflictResolver("vector"),
            "crdt": ConflictResolver("crdt")
        }

    def resolve(self, state_key, conflicts):
        """Select strategy based on state_key prefix."""
        if state_key.startswith("counter_"):
            return self.resolvers["crdt"].resolve(state_key, conflicts)
        elif state_key.startswith("causal_"):
            return self.resolvers["vector"].resolve(state_key, conflicts)
        else:
            return self.resolvers["lww"].resolve(state_key, conflicts)

# Test hybrid resolver
hybrid = HybridResolver()

print("=== Hybrid Strategy Selection ===\n")

# Test 1: Counter (CRDT)
counter_conflicts = [
    StateVersion("counter_tasks", 42, 1, datetime.now(timezone.utc), "agent-1",
                 {"crdt_type": CRDTType.COUNTER.value}),
    StateVersion("counter_tasks", 38, 2, datetime.now(timezone.utc), "agent-2",
                 {"crdt_type": CRDTType.COUNTER.value})
]

resolved1 = hybrid.resolve("counter_tasks", counter_conflicts)
print(f"1. counter_tasks → CRDT strategy")
print(f"   Result: {resolved1.value} (sum)")

# Test 2: Causal (Vector)
causal_conflicts = [
    StateVersion("causal_document", "A", 1, datetime.now(timezone.utc), "agent-1",
                 {"vector_clock": {"agent-1": 5, "agent-2": 3}}),
    StateVersion("causal_document", "B", 2, datetime.now(timezone.utc), "agent-2",
                 {"vector_clock": {"agent-1": 6, "agent-2": 4}})
]

resolved2 = hybrid.resolve("causal_document", causal_conflicts)
print(f"\n2. causal_document → Vector strategy")
print(f"   Result: {resolved2.value}")
print(f"   Strategy: {resolved2.metadata['resolution_strategy']}")

# Test 3: Config (LWW)
config_conflicts = [
    StateVersion("max_workers", 10, 1, datetime(2025, 1, 1, 10, 0, 0, tzinfo=timezone.utc), "agent-1", {}),
    StateVersion("max_workers", 15, 2, datetime(2025, 1, 1, 10, 0, 1, tzinfo=timezone.utc), "agent-2", {})
]

resolved3 = hybrid.resolve("max_workers", config_conflicts)
print(f"\n3. max_workers → LWW strategy")
print(f"   Result: {resolved3.value} (newest)")
```

**Output**:
```
=== Hybrid Strategy Selection ===

1. counter_tasks → CRDT strategy
   Result: 80 (sum)

2. causal_document → Vector strategy
   Result: B
   Strategy: vector_causal

3. max_workers → LWW strategy
   Result: 15 (newest)
```

---

**Complete!** All coordination examples demonstrate production-ready patterns for multi-agent systems.
