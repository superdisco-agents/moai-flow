# Consensus & Distributed Agents

> Distributed systems protocols for multi-agent agreement

## Overview

Claude-Flow includes 7 agents for distributed systems consensus - protocols borrowed from distributed computing for multi-agent coordination. MoAI has NO equivalent.

---

## Agent: `byzantine-coordinator`

### Purpose
Byzantine Fault Tolerance (BFT) for unreliable environments.

### The Byzantine Problem
```
Agent A says: "Use React"
Agent B says: "Use React"
Agent C says: "Use Vue"  ← Faulty/malicious agent
Agent D says: "Use React"

Result: Consensus on React (3/4 agree, tolerate 1 fault)
```

### Properties
- Tolerates f faulty agents with 3f+1 total agents
- Handles malicious or incorrect responses
- Guarantees agreement among honest agents

### Use Cases
- Critical decisions with potentially incorrect agent outputs
- High-stakes code reviews
- Security-sensitive operations

---

## Agent: `raft-manager`

### Purpose
Leader-based consensus protocol.

### How Raft Works
```
1. Election: Agents elect a leader
2. Replication: Leader distributes decisions
3. Commitment: Majority confirms
4. Recovery: New election if leader fails
```

### Properties
- Simple, understandable
- Strong consistency
- Leader-based coordination

### Use Cases
- Sequential task ordering
- Configuration management
- State machine replication

---

## Agent: `gossip-coordinator`

### Purpose
Epidemic-style information propagation.

### How Gossip Works
```
Round 1: Agent A tells Agent B
Round 2: A tells C, B tells D
Round 3: A tells D, B tells E, C tells F, D tells G
...
Eventually: All agents know
```

### Properties
- Eventually consistent
- Highly scalable
- Resilient to failures

### Use Cases
- Membership management
- Failure detection
- State synchronization

---

## Agent: `consensus-builder`

### Purpose
General consensus building across agents.

### Responsibilities
- Collect proposals from agents
- Evaluate trade-offs
- Build agreement
- Document decisions

### Techniques
- Voting
- Weighted scoring
- Iterative refinement
- Compromise negotiation

---

## Agent: `crdt-synchronizer`

### Purpose
Conflict-free Replicated Data Types synchronization.

### What are CRDTs?
Data structures that can be modified independently and merged without conflicts.

### Examples
```
G-Counter: Always incrementing counter
LWW-Register: Last-write-wins register
OR-Set: Observed-remove set
```

### Use Cases
- Concurrent editing
- Distributed state
- Offline-first systems

---

## Agent: `quorum-manager`

### Purpose
Quorum-based decision making.

### How Quorum Works
```
Total Agents: 5
Write Quorum: 3 (majority)
Read Quorum: 3 (majority)

Write succeeds if 3+ agents agree
Read succeeds if 3+ agents respond
```

### Properties
- Configurable consistency levels
- Trade-off between availability and consistency

### Use Cases
- Distributed storage decisions
- Feature flag voting
- Multi-agent approval

---

## Agent: `security-manager`

### Purpose
Security coordination across distributed agents.

### Responsibilities
- Access control
- Credential management
- Audit logging
- Threat detection

### Security Concerns in Multi-Agent
- Agent impersonation
- Message tampering
- Unauthorized access
- Information leakage

---

## MoAI Gap Analysis

### Complete Gap
MoAI has NO distributed systems agents.

| Protocol | MoAI Status |
|----------|-------------|
| Byzantine | Missing |
| Raft | Missing |
| Gossip | Missing |
| CRDT | Missing |
| Quorum | Missing |

### Why It Matters

Without consensus mechanisms:
- No way to handle disagreeing agents
- No fault tolerance for agent failures
- No scalable information propagation
- No conflict resolution for concurrent work

---

## Implementation Consideration

### Priority: MEDIUM

These protocols are valuable but complex. Consider:

1. **Start Simple**: Basic voting consensus
2. **Add Raft**: For leader-based coordination
3. **Add Gossip**: For large-scale information sharing
4. **Add Byzantine**: For critical operations

### Proposed MoAI Addition

```yaml
# New consensus agents
consensus-voting:      # Simple majority voting
consensus-raft:        # Leader election
consensus-gossip:      # Information propagation
consensus-quorum:      # Configurable quorum
```

---

## When You Need Consensus

| Scenario | Protocol |
|----------|----------|
| Multiple agents reviewing code | Voting |
| Coordinating sequential work | Raft |
| Spreading updates to all agents | Gossip |
| Critical decisions | Byzantine |
| Distributed state | CRDT |
