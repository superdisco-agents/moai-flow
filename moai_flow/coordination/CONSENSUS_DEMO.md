# ConsensusManager Demo - Phase 6B

## Overview

The ConsensusManager provides multi-algorithm consensus for swarm decision-making with pluggable algorithms, thread-safe operations, and comprehensive statistics.

## Quick Start

```python
from moai_flow.coordination import ConsensusManager, ConsensusDecision, QuorumAlgorithm, WeightedAlgorithm
from moai_flow.core.interfaces import ICoordinator

# Initialize with coordinator
coordinator = YourCoordinator()  # ICoordinator implementation
manager = ConsensusManager(coordinator, default_algorithm="quorum")

# Request consensus
proposal = {
    "action": "deploy",
    "version": "v2.0",
    "target": "production"
}

result = manager.request_consensus(proposal, timeout_ms=30000)

if result.decision == ConsensusDecision.APPROVED:
    print(f"Deployment approved! ({result.votes_for}/{len(result.participants)} votes)")
else:
    print(f"Deployment rejected: {result.decision}")
```

## Built-in Algorithms

### 1. Quorum Algorithm (Simple Majority)

Default algorithm requiring >50% approval from participants.

```python
# Uses default quorum algorithm
result = manager.request_consensus(proposal)

# Custom threshold (70% approval required)
custom_quorum = QuorumAlgorithm(threshold=0.7)
manager.register_algorithm("strict_quorum", custom_quorum)
result = manager.request_consensus(proposal, algorithm="strict_quorum")
```

**Use Cases**:
- General swarm decisions
- Feature flag enablement
- Configuration changes
- Task prioritization

### 2. Weighted Algorithm (Expert Voting)

Votes have different weights based on agent expertise, role, or priority.

```python
# Define agent weights (experts have higher weight)
agent_weights = {
    "expert-backend-001": 3.0,    # Senior backend expert
    "expert-frontend-001": 2.0,   # Senior frontend expert
    "agent-junior-001": 1.0,      # Junior agent
    "agent-junior-002": 1.0
}

weighted_algo = WeightedAlgorithm(
    threshold=0.6,
    agent_weights=agent_weights
)

manager.register_algorithm("expert_weighted", weighted_algo)

# Use weighted consensus for critical decisions
critical_proposal = {
    "action": "database_migration",
    "risk_level": "high"
}

result = manager.request_consensus(
    critical_proposal,
    algorithm="expert_weighted",
    timeout_ms=60000  # 60s for critical decisions
)
```

**Use Cases**:
- Architecture decisions
- Database migrations
- Security policy changes
- Critical deployments

## Advanced Features

### Custom Consensus Algorithm

Create your own consensus algorithm by extending `ConsensusAlgorithm`:

```python
from moai_flow.coordination import ConsensusAlgorithm, ConsensusResult, Vote, VoteType
from typing import Dict, Any, List

class UnanimousAlgorithm(ConsensusAlgorithm):
    """Requires 100% approval from all participants."""

    def propose(self, proposal: Dict[str, Any], participants: List[str]) -> str:
        proposal_id = f"unanimous_{int(time.time() * 1000)}"
        self._proposals = {proposal_id: participants}
        return proposal_id

    def decide(
        self,
        proposal_id: str,
        votes: List[Vote],
        timeout_reached: bool = False
    ) -> ConsensusResult:
        participants = self._proposals[proposal_id]
        votes_for = sum(1 for v in votes if v.vote == VoteType.FOR)
        votes_against = sum(1 for v in votes if v.vote == VoteType.AGAINST)

        # Require ALL participants to vote FOR
        decision = (
            "approved" if votes_for == len(participants) and not timeout_reached
            else "timeout" if timeout_reached
            else "rejected"
        )

        return ConsensusResult(
            decision=decision,
            votes_for=votes_for,
            votes_against=votes_against,
            threshold=1.0,
            participants=[v.agent_id for v in votes],
            algorithm_used="unanimous",
            duration_ms=0
        )

# Register and use
manager.register_algorithm("unanimous", UnanimousAlgorithm())
result = manager.request_consensus(
    {"action": "emergency_shutdown"},
    algorithm="unanimous"
)
```

### Statistics and Monitoring

Track consensus performance and patterns:

```python
# Get comprehensive statistics
stats = manager.get_algorithm_stats()

print(f"Total proposals: {stats['total_proposals']}")
print(f"Approval rate: {stats['approval_rate']:.1%}")
print(f"Average duration: {stats['avg_duration_ms']:.0f}ms")

# Per-algorithm statistics
for algo_name, algo_stats in stats['by_algorithm'].items():
    print(f"\n{algo_name.upper()}:")
    print(f"  Proposals: {algo_stats['proposals']}")
    print(f"  Approved: {algo_stats['approved']}")
    print(f"  Rejected: {algo_stats['rejected']}")
    print(f"  Timeouts: {algo_stats['timeouts']}")
    print(f"  Approval rate: {algo_stats['approval_rate']:.1%}")
```

### Vote Recording (Agent-Side)

Agents respond to consensus requests by recording votes:

```python
from moai_flow.coordination import VoteType

# Agent receives consensus_request message
def handle_consensus_request(message):
    proposal_id = message['proposal_id']
    proposal = message['proposal']

    # Agent evaluates proposal
    should_approve = evaluate_proposal(proposal)

    # Record vote
    vote = VoteType.FOR if should_approve else VoteType.AGAINST

    manager.record_vote(
        proposal_id=proposal_id,
        agent_id="agent-001",
        vote=vote,
        metadata={"reason": "deployment_approved"}
    )
```

## Real-World Scenarios

### Scenario 1: Feature Flag Deployment

```python
# Propose new feature activation
proposal = {
    "type": "feature_flag",
    "feature": "new_checkout_flow",
    "rollout_percentage": 10,  # Start with 10% traffic
    "monitoring_period_hours": 24
}

result = manager.request_consensus(proposal, algorithm="quorum")

if result.decision == ConsensusDecision.APPROVED:
    enable_feature_flag("new_checkout_flow", rollout=10)
    print(f"Feature approved by {result.votes_for} agents")
```

### Scenario 2: Database Schema Migration

```python
# Critical database migration requires expert consensus
migration_proposal = {
    "type": "database_migration",
    "migration_name": "add_user_preferences",
    "estimated_downtime_seconds": 120,
    "rollback_available": True
}

# Use weighted algorithm with 70% approval threshold
result = manager.request_consensus(
    migration_proposal,
    algorithm="expert_weighted",
    timeout_ms=60000
)

if result.decision == ConsensusDecision.APPROVED:
    weighted_approval = result.metadata.get("weighted_approval", 0)
    print(f"Migration approved (weighted: {weighted_approval:.1%})")
    execute_migration("add_user_preferences")
else:
    print(f"Migration rejected: {result.decision}")
    print(f"Votes: {result.votes_for} for, {result.votes_against} against")
```

### Scenario 3: Emergency System Rollback

```python
# Emergency rollback requires fast unanimous decision
rollback_proposal = {
    "type": "emergency_rollback",
    "severity": "critical",
    "target_version": "v1.9.5",
    "reason": "production_errors_spike"
}

# Use unanimous algorithm with short timeout (10s)
result = manager.request_consensus(
    rollback_proposal,
    algorithm="unanimous",
    timeout_ms=10000
)

if result.decision == ConsensusDecision.APPROVED:
    print("EMERGENCY ROLLBACK APPROVED - Executing immediately")
    trigger_rollback("v1.9.5")
elif result.decision == ConsensusDecision.TIMEOUT:
    print("TIMEOUT - Proceeding with automatic rollback")
    trigger_rollback("v1.9.5")  # Auto-rollback on timeout
```

## Integration with ICoordinator

The ConsensusManager integrates seamlessly with the ICoordinator interface:

```python
from moai_flow.core.interfaces import ICoordinator

class MyCoordinator(ICoordinator):
    def broadcast_message(self, from_agent: str, message: Dict[str, Any], exclude=None) -> int:
        # Broadcast consensus request to all agents
        for agent_id, agent in self.agents.items():
            if exclude and agent_id in exclude:
                continue

            # Send message to agent
            agent.receive_message(message)

        return len(self.agents)

    def get_topology_info(self) -> Dict[str, Any]:
        return {
            "type": "mesh",
            "agent_count": len(self.agents),
            "connection_count": self.calculate_connections(),
            "health": "healthy"
        }

# Use with ConsensusManager
coordinator = MyCoordinator()
manager = ConsensusManager(coordinator)
```

## Performance Characteristics

- **Vote Collection**: Thread-safe with RLock
- **Timeout Handling**: Graceful degradation (returns TIMEOUT result)
- **Memory**: O(n) where n = number of active proposals
- **Typical Duration**: <100ms for quorum, <200ms for weighted (depending on network latency)
- **Max Timeout**: 30s default (configurable up to 300s)

## Error Handling

### Timeout Handling

```python
result = manager.request_consensus(proposal, timeout_ms=5000)

if result.decision == ConsensusDecision.TIMEOUT:
    print(f"Consensus timeout: {result.votes_for}/{len(result.participants)} voted")
    # Implement fallback logic
    if result.votes_for > len(result.participants) * 0.7:
        print("Strong majority despite timeout - proceeding")
    else:
        print("Insufficient consensus - aborting")
```

### Agent Disconnection

```python
# Disconnected agents won't vote - handled automatically
result = manager.request_consensus(proposal)

participation_rate = len(result.participants) / expected_agents
if participation_rate < 0.5:
    print(f"WARNING: Low participation ({participation_rate:.1%})")
    # Consider re-proposing or adjusting thresholds
```

## Best Practices

1. **Choose Algorithm Wisely**:
   - `quorum`: General decisions, feature flags
   - `weighted`: Expert-driven, critical decisions
   - `unanimous`: Emergency situations, high-risk changes

2. **Set Appropriate Timeouts**:
   - Quick decisions: 5-10s
   - Standard: 30s
   - Critical/complex: 60s+

3. **Monitor Statistics**:
   - Track approval rates by algorithm
   - Identify bottlenecks (frequent timeouts)
   - Adjust thresholds based on patterns

4. **Handle Edge Cases**:
   - Low participation (< 50%)
   - Frequent timeouts (network issues)
   - Split decisions (50/50 votes)

5. **Test Custom Algorithms**:
   - Unit test decision logic
   - Simulate timeout scenarios
   - Verify thread safety

## Next Steps

- **Phase 6C**: Conflict Resolution mechanisms
- **Phase 6D**: Task Allocation strategies
- **Integration**: Connect with HeartbeatMonitor for agent health-aware consensus
- **Monitoring**: Track consensus patterns in MetricsStorage

## API Reference

See `moai_flow/coordination/consensus_manager.py` for full API documentation.

## License

MIT License - Part of MoAI-Flow Phase 6B

## Version

- **Implementation**: 1.0.0
- **Phase**: 6B (Coordination Intelligence)
- **Last Updated**: 2025-11-29
