# Raft Consensus Algorithm

> Leader-based consensus for multi-agent coordination

## Overview

The Raft consensus algorithm provides reliable, leader-based decision-making for MoAI-Flow swarms. It ensures consistency across distributed agents through log replication and majority voting.

## Key Features

- ✅ **Leader Election**: Automatic leader selection via term-based voting
- ✅ **Log Replication**: Reliable proposal distribution to all agents
- ✅ **Majority Consensus**: Decisions require majority acknowledgment
- ✅ **Automatic Failover**: Re-election when leader becomes unhealthy
- ✅ **Thread-Safe**: Concurrent operation support
- ✅ **Simplified Raft**: Optimized for swarm coordination (no persistence)

## Architecture

### Raft States

```python
from moai_flow.coordination.algorithms import RaftState

RaftState.FOLLOWER   # Default state, follows leader
RaftState.CANDIDATE  # Requesting votes during election
RaftState.LEADER     # Current leader, manages log replication
```

### Consensus Flow

```
┌─────────────┐
│   Proposal  │
└──────┬──────┘
       │
       v
┌─────────────────────┐
│ Check Leader Health │
└──────┬──────────────┘
       │
       v
  ┌────┴────┐
  │ Leader? │
  └────┬────┘
       │ No
       v
┌──────────────┐
│ Elect Leader │
└──────┬───────┘
       │
       v
┌────────────────┐
│ Append to Log  │
└──────┬─────────┘
       │
       v
┌────────────────────┐
│ Replicate to Peers │
└──────┬─────────────┘
       │
       v
┌──────────────────┐
│ Wait for Majority│
└──────┬───────────┘
       │
       v
  ┌────┴────┐
  │Majority?│
  └────┬────┘
       │ Yes
       v
┌─────────────┐
│   Commit    │
└──────┬──────┘
       │
       v
┌─────────────┐
│   Approved  │
└─────────────┘
```

## Usage

### Basic Setup

```python
from moai_flow.core.swarm_coordinator import SwarmCoordinator
from moai_flow.coordination.algorithms import RaftConsensus

# Create coordinator
coordinator = SwarmCoordinator(topology="mesh")

# Register agents
for i in range(5):
    coordinator.register_agent(
        f"agent-{i}",
        {"type": "worker", "capabilities": ["compute"]}
    )

# Initialize Raft consensus
raft = RaftConsensus(
    coordinator,
    election_timeout_ms=5000,
    heartbeat_interval_ms=1000
)
```

### Leader Election

```python
# Trigger leader election
leader_id = raft.elect_leader()
print(f"Elected leader: {leader_id}")

# Check current state
state = raft.get_state()
print(f"Current state: {state['state']}")  # "leader" or "follower"
print(f"Current term: {state['term']}")
```

### Submit Proposal

```python
# Create proposal
proposal = {
    "proposal_id": "deploy-v2.0",
    "description": "Deploy version 2.0 to production",
    "changes": ["API updates", "Database migration"]
}

# Request consensus
result = raft.propose(proposal, timeout_ms=30000)

# Check result
if result.decision == "approved":
    print(f"Proposal approved by {result.votes_for} agents")
    print(f"Committed at log index: {result.metadata['commit_index']}")
elif result.decision == "rejected":
    print(f"Proposal rejected: {result.metadata.get('reason')}")
else:  # timeout
    print(f"Consensus timeout: {result.metadata.get('reason')}")
```

### Heartbeat Mechanism

```python
# Leader sends heartbeats to maintain leadership
if raft.send_heartbeat():
    print("Heartbeat sent successfully")
else:
    print("Not a leader, cannot send heartbeat")
```

## Configuration

### Constructor Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `coordinator` | ICoordinator | Required | Coordinator for agent communication |
| `election_timeout_ms` | int | 5000 | Leader election timeout (milliseconds) |
| `heartbeat_interval_ms` | int | 1000 | Leader heartbeat interval (milliseconds) |

### Recommended Settings

**Small Swarms (3-5 agents)**:
- `election_timeout_ms`: 3000-5000
- `heartbeat_interval_ms`: 1000

**Medium Swarms (6-10 agents)**:
- `election_timeout_ms`: 5000-8000
- `heartbeat_interval_ms`: 1500

**Large Swarms (11+ agents)**:
- `election_timeout_ms`: 8000-10000
- `heartbeat_interval_ms`: 2000

## API Reference

### RaftConsensus Class

#### Methods

**`propose(proposal: Dict[str, Any], timeout_ms: int = 30000) -> ConsensusResult`**

Submit proposal for consensus decision.

- **Args**:
  - `proposal`: Proposal data (must be JSON-serializable)
  - `timeout_ms`: Timeout in milliseconds
- **Returns**: `ConsensusResult` with decision outcome
- **Raises**: None (returns timeout result on failure)

**`elect_leader() -> Optional[str]`**

Trigger leader election.

- **Returns**: Elected leader ID or None if election failed

**`send_heartbeat() -> bool`**

Send heartbeat to maintain leadership (leader only).

- **Returns**: True if sent successfully, False if not a leader

**`get_state() -> Dict[str, Any]`**

Get current Raft state.

- **Returns**: Dict with state information:
  - `algorithm`: "raft"
  - `state`: Current Raft state ("follower", "candidate", "leader")
  - `term`: Current term number
  - `leader`: Current leader ID
  - `log_size`: Number of log entries
  - `commit_index`: Index of last committed entry
  - `last_heartbeat_ago_ms`: Milliseconds since last heartbeat

**`reset() -> bool`**

Reset Raft to initial state.

- **Returns**: True (always succeeds)

### ConsensusResult Class

Result of consensus decision.

**Attributes**:
- `decision`: str - "approved", "rejected", or "timeout"
- `votes_for`: int - Number of votes in favor
- `votes_against`: int - Number of votes against
- `abstain`: int - Number of abstentions
- `threshold`: float - Required threshold for approval
- `participants`: List[str] - List of participating agent IDs
- `vote_details`: Dict[str, str] - Mapping of agent_id to vote
- `metadata`: Dict[str, Any] - Algorithm-specific metadata
  - `term`: Current Raft term
  - `commit_index`: Log index where committed
  - `leader`: Leader ID
  - `algorithm`: "raft"

## Implementation Details

### Simplified Aspects

This implementation is **simplified for swarm coordination**:

1. **In-Memory Log**: No persistent storage (suitable for decision consensus)
2. **No Snapshots**: Log is kept in full (acceptable for coordination decisions)
3. **Simulated Voting**: Vote collection is simulated (real implementation would wait for actual agent responses)
4. **No Network Layer**: Relies on coordinator's messaging (no direct peer-to-peer communication)

### Full Raft Features Not Implemented

- Persistent log storage
- Log compaction and snapshotting
- Configuration changes (adding/removing nodes)
- Pre-vote optimization
- Leadership transfer

These features are deferred for production Raft implementations where full state machine replication is required.

### Thread Safety

All public methods are thread-safe using internal locking. Multiple threads can safely:
- Submit proposals concurrently
- Check state
- Trigger elections

## Performance Characteristics

| Operation | Time Complexity | Space Complexity |
|-----------|----------------|------------------|
| Leader Election | O(n) | O(1) |
| Propose | O(n) | O(1) |
| Log Append | O(1) | O(1) |
| Get State | O(1) | O(1) |

Where `n` = number of agents in swarm.

## Examples

See `/moai_flow/examples/raft_consensus_demo.py` for comprehensive examples:
- Leader election
- Proposal consensus
- Log replication
- Leader failover

## Troubleshooting

### Election Timeouts

**Symptom**: Elections fail frequently

**Solution**:
- Increase `election_timeout_ms`
- Check network latency between agents
- Verify agent health

### Consensus Timeouts

**Symptom**: Proposals timeout without decision

**Solution**:
- Increase proposal `timeout_ms`
- Check agent availability
- Verify majority of agents are responsive

### Log Growth

**Symptom**: Memory usage grows over time

**Solution**:
- Call `reset()` periodically to clear log
- Implement log compaction (future enhancement)

## Related

- [Quorum Consensus](./quorum-consensus.md) - Majority-based voting
- [Byzantine Consensus](./byzantine-consensus.md) - Fault-tolerant consensus
- [Consensus Manager](../coordination/consensus-manager.md) - High-level consensus API

## References

- [Raft Consensus Algorithm](https://raft.github.io/) - Official Raft specification
- [In Search of an Understandable Consensus Algorithm](https://raft.github.io/raft.pdf) - Original paper
- [PRD-07: Consensus Mechanisms](../../specs/PRD-07-consensus-mechanisms.md) - MoAI-Flow consensus design
