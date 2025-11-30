# Consensus Algorithms Module

Deep dive into consensus algorithms for multi-agent decision making: Quorum, Weighted, Byzantine, and Gossip protocols.

## Table of Contents

1. [Consensus Manager Architecture](#consensus-manager-architecture)
2. [Quorum Algorithm](#quorum-algorithm)
3. [Weighted Algorithm](#weighted-algorithm)
4. [Byzantine Consensus](#byzantine-consensus)
5. [Gossip Protocol](#gossip-protocol)
6. [Algorithm Selection Guide](#algorithm-selection-guide)
7. [Performance Characteristics](#performance-characteristics)

---

## Consensus Manager Architecture

The `ConsensusManager` provides a pluggable architecture for multi-algorithm consensus with runtime algorithm switching.

### Core Components

```python
class ConsensusManager:
    """
    Multi-algorithm consensus manager.

    Features:
    - Pluggable algorithm registry
    - Thread-safe vote collection
    - Timeout handling with graceful degradation
    - Comprehensive statistics tracking
    - Integration with ICoordinator for vote collection
    """

    def __init__(self, coordinator, default_algorithm="quorum"):
        self.coordinator = coordinator
        self.default_algorithm = default_algorithm
        self.algorithms = {}  # Registry pattern
        self.active_proposals = {}  # Tracking
        self.statistics = {}  # Metrics
        self._lock = threading.RLock()  # Thread safety
```

### Built-in Algorithms

| Algorithm | Registration Key | Default Threshold | Use Case |
|-----------|------------------|-------------------|----------|
| Quorum | `"quorum"` | 0.5 (50%) | Simple majority voting |
| Weighted | `"weighted"` | 0.6 (60%) | Expert-based decisions |
| Byzantine | `"byzantine"` | 2f+1 | Fault-tolerant consensus |
| Gossip | `"gossip"` | 0.95 (95% convergence) | Eventual consistency |

### Algorithm Registration

```python
# Built-in algorithms auto-registered
manager = ConsensusManager(coordinator, default_algorithm="quorum")

# Register custom algorithm
from moai_flow.coordination.algorithms import RaftConsensus
custom_algo = RaftConsensus(term=1, leader_id="agent-1")
manager.register_algorithm("raft", custom_algo)

# Use custom algorithm
result = manager.request_consensus(proposal, algorithm="raft")
```

### Request Consensus Flow

```
1. request_consensus(proposal, algorithm, timeout_ms)
   ↓
2. Select algorithm from registry
   ↓
3. Get participants from topology
   ↓
4. algo.propose(proposal, participants) → proposal_id
   ↓
5. Broadcast consensus_request to all agents
   ↓
6. Wait for votes (with timeout)
   ↓
7. Collect votes via record_vote()
   ↓
8. algo.decide(proposal_id, votes, timeout_reached) → ConsensusResult
   ↓
9. Update statistics
   ↓
10. Return ConsensusResult
```

---

## Quorum Algorithm

Simple majority (>50%) or configurable threshold consensus.

### Algorithm Details

**Principle**: Approval if votes_for / total_participants > threshold

**Thresholds**:
- **Simple majority**: 0.51 (>50%)
- **Supermajority**: 0.66 (2/3)
- **Strong majority**: 0.75 (3/4)
- **Unanimous**: 1.0 (100%)

### Implementation

```python
class QuorumAlgorithm(ConsensusAlgorithm):
    def __init__(self, threshold=0.5, require_majority=True):
        self.threshold = threshold
        self.require_majority = require_majority

    def decide(self, proposal_id, votes, timeout_reached=False):
        total_participants = len(self._proposals[proposal_id]["participants"])

        votes_for = sum(1 for v in votes if v.vote == VoteType.FOR)
        votes_against = sum(1 for v in votes if v.vote == VoteType.AGAINST)
        votes_abstain = sum(1 for v in votes if v.vote == VoteType.ABSTAIN)

        participation_rate = len(votes) / total_participants
        approval_rate = votes_for / total_participants

        # Decision logic
        if timeout_reached and participation_rate < 0.5 and self.require_majority:
            decision = ConsensusDecision.TIMEOUT
        elif approval_rate > self.threshold:
            decision = ConsensusDecision.APPROVED
        elif timeout_reached:
            decision = ConsensusDecision.TIMEOUT
        else:
            decision = ConsensusDecision.REJECTED
```

### Usage Examples

```python
# Simple majority (>50%)
quorum = QuorumAlgorithm(threshold=0.51)
manager.register_algorithm("simple", quorum)

# Supermajority (2/3)
supermajority = QuorumAlgorithm(threshold=0.66)
manager.register_algorithm("supermajority", supermajority)

# Unanimous
unanimous = QuorumAlgorithm(threshold=1.0)
manager.register_algorithm("unanimous", unanimous)

# Use specific quorum
result = manager.request_consensus(proposal, algorithm="supermajority")
```

### Quorum Presets

```python
QUORUM_PRESETS = {
    "simple": 0.51,       # Simple majority (>50%)
    "supermajority": 0.66,  # 2/3 majority
    "strong": 0.75,       # 3/4 majority
    "unanimous": 1.0      # All agents must approve
}

quorum = QuorumAlgorithm(threshold=QUORUM_PRESETS["supermajority"])
```

### Performance

- **Time complexity**: O(n) for vote counting
- **Space complexity**: O(n) for vote storage
- **Latency**: ~50-200ms (depends on network + agent response time)
- **Scalability**: Excellent (100+ agents)

---

## Weighted Algorithm

Priority-based voting where votes have different weights based on agent expertise or role.

### Algorithm Details

**Principle**: Approval if weighted_for / total_weight > threshold

**Use Cases**:
- Expert-based decisions (experts have higher weight)
- Hierarchical swarms (leaders have priority)
- Quality-weighted voting (high-performing agents count more)

### Implementation

```python
class WeightedAlgorithm(ConsensusAlgorithm):
    def __init__(self, threshold=0.6, agent_weights=None):
        self.threshold = threshold
        self.agent_weights = agent_weights or {}

    def decide(self, proposal_id, votes, timeout_reached=False):
        participants = self._proposals[proposal_id]["participants"]

        total_weight = sum(self.agent_weights.get(p, 1.0) for p in participants)

        weighted_for = sum(
            self.agent_weights.get(v.agent_id, 1.0)
            for v in votes if v.vote == VoteType.FOR
        )

        weighted_approval = weighted_for / total_weight

        if weighted_approval > self.threshold:
            decision = ConsensusDecision.APPROVED
        else:
            decision = ConsensusDecision.REJECTED
```

### Usage Examples

```python
# Expert-based voting
agent_weights = {
    "expert-senior": 3.0,
    "expert-mid": 2.0,
    "expert-junior": 1.5,
    "agent-regular": 1.0
}

weighted = WeightedAlgorithm(threshold=0.6, agent_weights=agent_weights)
manager.register_algorithm("weighted", weighted)

# Example scenario: 4 agents vote
# expert-senior (weight 3.0): FOR
# expert-mid (weight 2.0): FOR
# expert-junior (weight 1.5): AGAINST
# agent-regular (weight 1.0): AGAINST
# Total weight: 7.5
# Weighted FOR: 5.0 (3.0 + 2.0)
# Approval: 5.0 / 7.5 = 0.67 > 0.6 → APPROVED
```

### Dynamic Weight Adjustment

```python
# Adjust weights based on agent performance
def update_weights(agent_id, performance_score):
    if performance_score > 0.9:
        agent_weights[agent_id] = 2.0  # High performer
    elif performance_score > 0.7:
        agent_weights[agent_id] = 1.5  # Good performer
    else:
        agent_weights[agent_id] = 1.0  # Standard

# Update algorithm
weighted.agent_weights = agent_weights
```

### Performance

- **Time complexity**: O(n) for weighted vote counting
- **Space complexity**: O(n) for weights + votes
- **Latency**: ~50-200ms (same as Quorum)
- **Scalability**: Excellent (100+ agents)

---

## Byzantine Consensus

Fault-tolerant consensus that tolerates up to f malicious or faulty agents.

### Byzantine Theory

**Byzantine Generals Problem**: How to reach agreement when some participants are malicious or unreliable?

**Requirements**:
- **n >= 3f+1**: Total agents must be at least 3f+1 where f is fault tolerance
- **2f+1 agreement**: Requires 2f+1 votes for decision
- **Multi-round voting**: Minimum 3 rounds to detect vote changes

**Guarantees**:
- Tolerates up to f Byzantine (malicious/faulty) agents
- Ensures agreement among honest agents
- Detects malicious agents through vote consistency checks

### Implementation

```python
class ByzantineConsensus(ConsensusAlgorithm):
    def __init__(self, fault_tolerance=1, num_rounds=3):
        self.fault_tolerance = fault_tolerance
        self.num_rounds = num_rounds
        self.min_participants = 3 * fault_tolerance + 1
        self.agreement_threshold = 2 * fault_tolerance + 1
        self._detected_malicious = set()

    def propose(self, proposal, participants):
        n = len(participants)
        if n < self.min_participants:
            raise ValueError(
                f"Insufficient participants: need {self.min_participants}, got {n}"
            )
        # ... proposal creation

    def decide(self, proposal_id, votes, timeout_reached=False):
        # Execute multi-round voting
        round_votes = self._simulate_multi_round_voting(votes, participants)

        # Detect malicious agents (vote changers)
        malicious_agents = self._detect_malicious_agents(proposal_id, round_votes)

        # Count honest votes only
        honest_votes = [v for v in votes if v.agent_id not in malicious_agents]

        votes_for = sum(1 for v in honest_votes if v.vote == VoteType.FOR)

        # Decision: need 2f+1 agreements
        if votes_for >= self.agreement_threshold:
            decision = ConsensusDecision.APPROVED
        else:
            decision = ConsensusDecision.REJECTED
```

### Byzantine Configuration

```python
# f=1, n>=4, threshold=3 (tolerate 1 malicious)
byzantine_f1 = ByzantineConsensus(fault_tolerance=1)

# f=2, n>=7, threshold=5 (tolerate 2 malicious)
byzantine_f2 = ByzantineConsensus(fault_tolerance=2)

# Higher rounds for stronger detection
byzantine_secure = ByzantineConsensus(fault_tolerance=1, num_rounds=5)
```

### Malicious Agent Detection

```python
def _detect_malicious_agents(self, proposal_id, round_votes):
    """Detect agents that changed votes across rounds."""
    malicious = set()

    all_agents = set()
    for round_vote in round_votes:
        all_agents.update(round_vote.keys())

    for agent_id in all_agents:
        votes_in_rounds = [
            round_vote[agent_id]
            for round_vote in round_votes
            if agent_id in round_vote
        ]

        # Check if agent changed vote between rounds
        if len(set(votes_in_rounds)) > 1:
            malicious.add(agent_id)

    return malicious
```

### Usage Examples

```python
# Initialize Byzantine consensus
byzantine = ByzantineConsensus(fault_tolerance=1, num_rounds=3)
manager.register_algorithm("byzantine", byzantine)

# Propose with 4 agents (minimum for f=1)
participants = ["agent-1", "agent-2", "agent-3", "agent-4"]
proposal_id = byzantine.propose({"action": "critical_update"}, participants)

# Collect votes (including potentially malicious)
votes = [
    Vote("agent-1", VoteType.FOR),
    Vote("agent-2", VoteType.FOR),
    Vote("agent-3", VoteType.FOR),
    Vote("agent-4", VoteType.AGAINST)  # Malicious or minority
]

# Byzantine decision
result = byzantine.decide(proposal_id, votes)

print(f"Decision: {result.decision}")
print(f"Malicious detected: {result.metadata['malicious_detected']}")
print(f"Malicious agents: {result.metadata['malicious_agents']}")
```

### Performance

- **Time complexity**: O(n²) for multi-round voting
- **Space complexity**: O(n * rounds) for vote history
- **Latency**: ~500-2000ms (multiple rounds)
- **Scalability**: Good (up to 30-50 agents)

---

## Gossip Protocol

Epidemic-style eventual consistency protocol for large-scale swarms.

### Algorithm Details

**Principle**: Agents spread information via random peer selection until convergence

**Protocol**:
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

**Guarantees**:
- High probability of convergence (exponential)
- O(log n) message complexity per agent
- Tolerates agent failures
- No global clock needed

### Implementation

```python
class GossipProtocol(ConsensusAlgorithm):
    def __init__(self, fanout=3, rounds=5, convergence_threshold=0.95):
        self._config = GossipConfig(
            fanout=fanout,
            max_rounds=rounds,
            convergence_threshold=convergence_threshold
        )

    def decide(self, votes, threshold=0.66, metadata=None):
        # Execute gossip rounds
        final_state, rounds_completed, converged = self._execute_gossip_rounds(votes)

        # Aggregate majority
        decision, vote_counts = self._aggregate_majority(final_state)

        return ConsensusResult(
            decision=decision,
            rounds_completed=rounds_completed,
            converged=converged,
            ...
        )

    def _execute_gossip_rounds(self, initial_votes):
        current_state = dict(initial_votes)

        for round_num in range(1, self._config.max_rounds + 1):
            # Propagate one round
            new_state = self._propagate_round(current_state, all_agents)

            # Check convergence
            converged, agreement_ratio = self._check_convergence(new_state)

            if converged:
                return new_state, round_num, True

            current_state = new_state

        return current_state, self._config.max_rounds, False
```

### Gossip Configuration

```python
# Standard configuration (medium networks 10-50 agents)
gossip_medium = GossipProtocol(fanout=3, rounds=5, convergence_threshold=0.95)

# High reliability (critical decisions)
gossip_critical = GossipProtocol(fanout=5, rounds=10, convergence_threshold=0.99)

# Fast convergence (large networks 100+ agents)
gossip_large = GossipProtocol(fanout=10, rounds=3, convergence_threshold=0.90)
```

### Convergence Analysis

**Rounds to convergence**: O(log n) with high probability

**Total messages**: O(n * log n)

**Convergence probability**:
- After log₂(n) rounds: ~99.9% convergence
- After 2*log₂(n) rounds: ~99.999% convergence

**Example**: 100 agents, fanout=3
- Round 1: ~3% convergence
- Round 3: ~50% convergence
- Round 5: ~95% convergence
- Round 7: ~99% convergence

### Usage Examples

```python
# Initialize gossip
gossip = GossipProtocol(fanout=3, rounds=5, convergence_threshold=0.95)
manager.register_algorithm("gossip", gossip)

# Initial votes from 10 agents
votes = {
    f"agent-{i}": "approve" if i <= 7 else "reject"
    for i in range(1, 11)
}

# Gossip decision
result = gossip.decide(votes, threshold=0.66)

print(f"Decision: {result.decision}")
print(f"Rounds to convergence: {result.metadata['rounds_completed']}")
print(f"Final agreement: {result.metadata['agreement_ratio']:.2%}")
```

### Performance

- **Time complexity**: O(n * log n) messages
- **Space complexity**: O(n) for state
- **Latency**: ~100-500ms (depends on rounds)
- **Scalability**: Excellent (1000+ agents)

---

## Algorithm Selection Guide

### Decision Tree

```
Start
  ↓
Trusted agents?
  → YES → Network size?
      → Small (<50) → Quorum (simple majority)
      → Large (>50) → Gossip (eventual consistency)
  → NO → Byzantine tolerance needed?
      → YES → Byzantine (fault-tolerant)
      → NO → Priority voting needed?
          → YES → Weighted (expert-based)
          → NO → Quorum (threshold-based)
```

### Use Case Matrix

| Use Case | Algorithm | Rationale |
|----------|-----------|-----------|
| Simple voting | Quorum | Fast, straightforward |
| Expert-based decisions | Weighted | Prioritizes expertise |
| Untrusted agents | Byzantine | Fault tolerance |
| Large-scale swarms | Gossip | Scalability |
| Critical security | Byzantine | Malicious detection |
| Fast local consensus | Quorum | Low latency |
| Distributed network | Gossip | No coordination overhead |

### Configuration Recommendations

```python
# Fast consensus for local network (latency < 10ms)
manager = ConsensusManager(coordinator, default_algorithm="quorum")

# Expert-based with priority
manager = ConsensusManager(coordinator, default_algorithm="weighted")

# Untrusted environment (blockchain, multi-org)
manager = ConsensusManager(coordinator, default_algorithm="byzantine")

# Large-scale distributed (100+ agents)
manager = ConsensusManager(coordinator, default_algorithm="gossip")
```

---

## Performance Characteristics

### Comparison Table

| Algorithm | Latency | Throughput | Scalability | Fault Tolerance | Complexity |
|-----------|---------|------------|-------------|-----------------|------------|
| **Quorum** | 50-200ms | High | 100+ agents | No | O(n) |
| **Weighted** | 50-200ms | High | 100+ agents | No | O(n) |
| **Byzantine** | 500-2000ms | Medium | 30-50 agents | Yes (f < n/3) | O(n²) |
| **Gossip** | 100-500ms | Medium | 1000+ agents | Yes (probabilistic) | O(n log n) |

### Latency Breakdown

```python
# Quorum latency
network_latency = 10-50ms  # Agent communication
vote_collection = 20-100ms  # Parallel vote gathering
decision_logic = 1-5ms      # Vote counting
total = 50-200ms

# Byzantine latency
round_1 = 50-200ms  # First voting round
round_2 = 50-200ms  # Second round
round_3 = 50-200ms  # Third round
malicious_detection = 10-50ms  # Vote consistency checks
total = 500-2000ms

# Gossip latency
round_1 = 20-100ms  # First gossip round
round_2 = 20-100ms  # Second round
round_3 = 20-100ms  # Third round
convergence_check = 5-20ms  # Agreement calculation
total = 100-500ms
```

### Throughput (proposals/second)

- **Quorum**: 5-20 proposals/sec
- **Weighted**: 5-20 proposals/sec
- **Byzantine**: 1-5 proposals/sec
- **Gossip**: 2-10 proposals/sec

### Optimization Tips

**Quorum/Weighted**:
- Use shorter timeouts for fast networks
- Pre-fetch agent status to avoid delays
- Cache participant lists

**Byzantine**:
- Reduce num_rounds for faster (but less secure) decisions
- Use smaller fault_tolerance (f) when possible
- Pre-compute malicious agent blacklist

**Gossip**:
- Tune fanout based on network size
- Adjust convergence_threshold for speed vs accuracy trade-off
- Use delta updates for large state

---

**Next**: [Conflict Resolution Module](conflict-resolution.md)
