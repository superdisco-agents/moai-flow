# MoAI-Flow Consensus Algorithms

> Multi-agent consensus and decision-making algorithms

## Overview

This module provides consensus algorithm implementations for MoAI-Flow swarm coordination. These algorithms enable multiple agents to reach agreement on proposals, decisions, and state changes.

## Available Algorithms

### 1. Raft Consensus ✅

**File**: `raft_consensus.py`
**Status**: Production Ready
**LOC**: 422 lines

Leader-based consensus with automatic failover:
- Leader election via term-based voting
- Log replication for proposal consistency
- Majority-based decision making
- Automatic leader failover on failure
- Thread-safe concurrent operations

**Use Cases**:
- Critical decisions requiring strong consistency
- Leader-coordinated task allocation
- State synchronization across agents
- Ordered proposal execution

**Example**:
```python
from moai_flow.coordination.algorithms import RaftConsensus

raft = RaftConsensus(coordinator, election_timeout_ms=5000)
leader = raft.elect_leader()
result = raft.propose({"proposal_id": "deploy-v2"})
```

### 2. Quorum Consensus (Planned)

**Status**: Phase 6B
**Target**: Simple majority voting

Majority-based voting without leader:
- Direct vote collection from all agents
- Configurable quorum threshold (default: 50%+1)
- Faster than Raft for simple decisions
- No leader election overhead

**Use Cases**:
- Quick yes/no decisions
- Feature flags and toggles
- Non-critical consensus

### 3. Byzantine Consensus (Future)

**Status**: Phase 7+
**Target**: Fault-tolerant consensus

Byzantine fault-tolerant algorithm:
- Tolerates malicious/faulty agents
- Requires 3f+1 agents to tolerate f faults
- Strong security guarantees
- Higher overhead than Raft/Quorum

**Use Cases**:
- High-security environments
- Untrusted agent networks
- Financial/critical systems

## Architecture

### Base Protocol

All consensus algorithms implement the `ConsensusAlgorithm` protocol:

```python
from abc import ABC, abstractmethod
from typing import Dict, Any

class ConsensusAlgorithm(ABC):
    @abstractmethod
    def propose(
        self,
        proposal: Dict[str, Any],
        timeout_ms: int = 30000
    ) -> ConsensusResult:
        """Submit proposal for consensus decision."""
        pass

    @abstractmethod
    def get_state(self) -> Dict[str, Any]:
        """Get current algorithm state."""
        pass

    @abstractmethod
    def reset(self) -> bool:
        """Reset algorithm to initial state."""
        pass
```

### ConsensusResult

Standard result format across all algorithms:

```python
@dataclass
class ConsensusResult:
    decision: str              # "approved", "rejected", or "timeout"
    votes_for: int             # Number of votes in favor
    votes_against: int         # Number of votes against
    abstain: int               # Number of abstentions
    threshold: float           # Required threshold for approval
    participants: List[str]    # Participating agent IDs
    vote_details: Dict[str, str]  # Agent vote mapping
    metadata: Dict[str, Any]   # Algorithm-specific metadata
```

## Integration

### With SwarmCoordinator

```python
from moai_flow.core.swarm_coordinator import SwarmCoordinator
from moai_flow.coordination.algorithms import RaftConsensus

# Initialize coordinator
coordinator = SwarmCoordinator(topology="mesh")

# Register agents
for i in range(5):
    coordinator.register_agent(f"agent-{i}", {...})

# Create consensus algorithm
consensus = RaftConsensus(coordinator)

# Use coordinator's consensus interface
result = coordinator.request_consensus(proposal)
```

### With ConsensusManager (Future)

```python
from moai_flow.coordination import ConsensusManager

# Initialize manager with algorithm
manager = ConsensusManager(algorithm="raft", coordinator=coordinator)

# Submit proposal
result = manager.propose(proposal)

# Switch algorithms dynamically
manager.set_algorithm("quorum")
result2 = manager.propose(proposal2)
```

## Algorithm Comparison

| Feature | Raft | Quorum | Byzantine |
|---------|------|--------|-----------|
| **Leader** | Yes | No | No |
| **Fault Tolerance** | f < n/2 | f < n/2 | f < n/3 |
| **Performance** | Medium | Fast | Slow |
| **Complexity** | Medium | Low | High |
| **Use Case** | Strong consistency | Quick decisions | High security |
| **Overhead** | Medium | Low | High |

## Performance Characteristics

### Raft Consensus

- **Leader Election**: O(n) time, O(1) space
- **Proposal**: O(n) time, O(1) space
- **Typical Latency**: 2-5 seconds for 5-10 agents

### Quorum Consensus (Planned)

- **Proposal**: O(n) time, O(1) space
- **Typical Latency**: 1-3 seconds for 5-10 agents

## Configuration

### Raft Settings

```python
raft = RaftConsensus(
    coordinator=coordinator,
    election_timeout_ms=5000,    # Leader election timeout
    heartbeat_interval_ms=1000   # Leader heartbeat interval
)
```

**Recommendations**:
- Small swarms (3-5): `election_timeout_ms=3000-5000`
- Medium swarms (6-10): `election_timeout_ms=5000-8000`
- Large swarms (11+): `election_timeout_ms=8000-10000`

### Quorum Settings (Future)

```python
quorum = QuorumConsensus(
    coordinator=coordinator,
    threshold=0.66,      # 66% majority required
    timeout_ms=10000     # Vote collection timeout
)
```

## Examples

### Complete Examples

See `/moai_flow/examples/` for full demonstrations:
- `raft_consensus_demo.py` - Raft algorithm usage
- `quorum_consensus_demo.py` - Quorum voting (future)
- `consensus_comparison.py` - Algorithm comparison (future)

### Quick Start

```python
from moai_flow.core.swarm_coordinator import SwarmCoordinator
from moai_flow.coordination.algorithms import RaftConsensus

# Setup
coordinator = SwarmCoordinator(topology="mesh")
for i in range(5):
    coordinator.register_agent(f"agent-{i}", {"type": "worker"})

# Initialize Raft
raft = RaftConsensus(coordinator)
raft.elect_leader()

# Submit proposal
proposal = {
    "proposal_id": "feature-x",
    "description": "Implement feature X",
    "priority": "high"
}

result = raft.propose(proposal, timeout_ms=30000)

if result.decision == "approved":
    print(f"✅ Approved by {result.votes_for}/{len(result.participants)} agents")
    # Execute proposal
else:
    print(f"❌ {result.decision}: {result.metadata.get('reason', 'unknown')}")
```

## Testing

### Unit Tests

```bash
pytest tests/moai_flow/coordination/algorithms/
```

### Integration Tests

```bash
pytest tests/moai_flow/integration/test_consensus_integration.py
```

## Documentation

- [Raft Consensus](../algorithms/raft-consensus.md) - Detailed Raft guide
- [PRD-07: Consensus Mechanisms](../../specs/PRD-07-consensus-mechanisms.md) - Design rationale
- [Consensus Manager](../../docs/coordination/consensus-manager.md) - High-level API (future)

## Implementation Status

| Component | Status | LOC | Tests |
|-----------|--------|-----|-------|
| Base Protocol | ✅ Complete | 97 | N/A |
| Raft Consensus | ✅ Complete | 422 | Pending |
| Quorum Consensus | 🚧 Planned | - | - |
| Byzantine Consensus | 📋 Future | - | - |
| Consensus Manager | 📋 Future | - | - |

## Contributing

When implementing new consensus algorithms:

1. Implement `ConsensusAlgorithm` protocol
2. Return `ConsensusResult` from `propose()`
3. Ensure thread safety
4. Add comprehensive docstrings
5. Create example in `/moai_flow/examples/`
6. Write unit tests
7. Update this README

## Related

- [Swarm Coordinator](../../core/swarm_coordinator.py) - Main coordination interface
- [ICoordinator Protocol](../../core/interfaces.py) - Coordinator interface
- [Topology Patterns](../../topology/) - Agent network topologies

---

**Last Updated**: 2025-11-29
**Phase**: 6B (Consensus Mechanisms)
**Status**: Raft Complete, Quorum Pending
