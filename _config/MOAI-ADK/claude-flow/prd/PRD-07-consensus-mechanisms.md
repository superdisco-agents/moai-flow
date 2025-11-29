# PRD-07: Consensus Mechanisms

> Multi-agent consensus and conflict resolution

## Overview

| Field | Value |
|-------|-------|
| **Priority** | P2 (Important) |
| **Effort** | High (2-3 months) |
| **Impact** | Low-Medium |
| **Type** | Advanced Infrastructure |

---

## Problem Statement

Claude-Flow has 7 consensus-related agents implementing various consensus algorithms (Byzantine, Raft, Gossip, etc.). MoAI has no consensus mechanisms, limiting multi-agent decision-making.

### Current MoAI State

```
CURRENT: No Consensus

Agent A decides → Result A
Agent B decides → Result B
Agent C decides → Result C

No coordination, no agreement
Conflicts resolved by user
```

### Desired State

```
DESIRED: Consensus-Based Decisions

Agent A votes → ┐
Agent B votes → ├─→ Consensus Algorithm → Agreed Decision
Agent C votes → ┘
```

---

## Consensus Types (Claude-Flow)

### 1. Byzantine Consensus

Tolerates malicious/faulty agents:

```
Agents: A, B, C, D (1 faulty allowed)

A votes: "approve"
B votes: "approve"
C votes: "reject" (faulty)
D votes: "approve"

Consensus: "approve" (3/4 honest agree)
```

### 2. Raft Consensus

Leader-based agreement:

```
Leader: A
Followers: B, C, D

A proposes: "implement API"
A → B: "replicate?"  B: "ack"
A → C: "replicate?"  C: "ack"
A → D: "replicate?"  D: "ack"

Committed (majority acked)
```

### 3. Gossip Protocol

Eventual consistency through spreading:

```
Time 0: A knows "config v2"
Time 1: A tells B → B knows "config v2"
Time 2: A tells C, B tells D → C, D know "config v2"

Eventually all nodes converge
```

### 4. CRDT (Conflict-free Replicated Data Types)

Automatic conflict resolution:

```
Agent A: counter = 5
Agent B: counter = 3

Merge: counter = max(5, 3) = 5
```

### 5. Quorum

Majority agreement:

```
5 agents, quorum = 3

A: approve
B: approve
C: approve  ← Quorum reached
D: (waiting)
E: (waiting)

Decision: approved
```

---

## Solution Options

### Option A: Claude-Flow Consensus MCP

Use Claude-Flow's consensus via MCP:

```javascript
mcp__claude-flow__swarm_init {
  topology: "mesh",
  consensus: "raft"
}

mcp__claude-flow__consensus_propose {
  proposal: "implement_feature_x",
  voters: ["agent-1", "agent-2", "agent-3"]
}
```

**Pros**: Immediate, sophisticated
**Cons**: External dependency, complexity

### Option B: Simple Voting System

Implement basic majority voting:

```python
def consensus_vote(proposal, agents):
    votes = {}
    for agent in agents:
        votes[agent] = get_agent_vote(agent, proposal)

    approve = sum(1 for v in votes.values() if v == "approve")
    if approve > len(agents) / 2:
        return "approved"
    return "rejected"
```

**Pros**: Simple, native
**Cons**: Limited algorithms

### Option C: Defer (Recommended)

Defer consensus until swarm is implemented:

1. Implement swarm first (PRD-02)
2. Evaluate consensus needs
3. Build or integrate as needed

---

## Recommended Solution: Option C

### Rationale

Consensus mechanisms require:
1. Multi-agent infrastructure (swarm)
2. Inter-agent communication
3. Shared state management

These prerequisites are in PRD-02 (Swarm Coordination).

### Dependency Chain

```
PRD-02: Swarm Coordination
        ↓
PRD-07: Consensus Mechanisms
```

### When to Revisit

After PRD-02 completion:
1. Evaluate actual consensus needs
2. Determine which algorithms needed
3. Build or integrate accordingly

---

## Technical Specification (Future Reference)

### Consensus Configuration

```json
{
  "consensus": {
    "enabled": false,
    "algorithm": "majority",
    "threshold": 0.66,
    "timeout_ms": 30000,
    "retry_attempts": 3
  }
}
```

### Consensus Types to Consider

| Algorithm | Use Case | Complexity |
|-----------|----------|------------|
| Majority Vote | Simple decisions | Low |
| Weighted Vote | Expert opinions | Low |
| Raft | Leader-based | Medium |
| Quorum | Critical decisions | Medium |
| Byzantine | Fault tolerance | High |

### Simple Majority Implementation

```python
class ConsensusManager:
    def __init__(self, threshold=0.66):
        self.threshold = threshold

    def propose(self, proposal, voters):
        votes = {}
        for voter in voters:
            votes[voter] = self.collect_vote(voter, proposal)

        return self.evaluate(votes)

    def evaluate(self, votes):
        approve_count = sum(1 for v in votes.values() if v == "approve")
        total = len(votes)

        if approve_count / total >= self.threshold:
            return {"result": "approved", "votes": votes}
        return {"result": "rejected", "votes": votes}
```

---

## Acceptance Criteria (Deferred)

When revisiting after PRD-02:

- [ ] Swarm infrastructure functional
- [ ] Inter-agent communication working
- [ ] Simple voting implemented
- [ ] Consensus hooks integrated
- [ ] Configuration options available

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Over-engineering | High | High | Defer until needed |
| Complexity creep | High | Medium | Start with simple voting |
| Performance overhead | Medium | Medium | Async consensus |

---

## Success Metrics (Future)

| Metric | Target |
|--------|--------|
| Consensus reliability | > 99% |
| Consensus latency | < 5 seconds |
| Conflict resolution | > 90% automated |

---

## Related Documents

- [Consensus Agents](../agents/04-consensus-distributed.md)
- [Swarm Coordination](../advanced/01-swarm-topologies.md)
- [PRD-02 Swarm Coordination](PRD-02-swarm-coordination.md)
- [PRD-00 Overview](PRD-00-overview.md)

---

## Timeline

```
Current:   Deferred (dependency on PRD-02)

After PRD-02:
Week 1-2:  Evaluate needs
Week 3-4:  Design consensus system
Week 5-8:  Implement chosen algorithms
Week 9-12: Testing and integration

Total: 3 months (after PRD-02)
```

---

## Conclusion

Consensus mechanisms are sophisticated but require swarm infrastructure. This PRD is deferred until PRD-02 (Swarm Coordination) is complete. The documentation here serves as future reference for implementation decisions.
