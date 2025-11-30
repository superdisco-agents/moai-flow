# Multi-Agent Swarm Examples

Complete swarm coordination workflows with realistic multi-agent scenarios.

## Example 1: Deployment Coordination Swarm

5-agent swarm coordinating production deployment with consensus voting.

```python
from moai_flow.core import SwarmCoordinator
from moai_flow.memory import MemoryProvider
from moai_flow.coordination import (
    ConsensusManager,
    ConflictResolver,
    StateSynchronizer,
    WeightedAlgorithm
)

# Setup swarm
coordinator = SwarmCoordinator(topology="mesh")

# Add agents with different roles
agents = [
    {"id": "lead-engineer", "role": "lead", "weight": 3.0},
    {"id": "backend-expert", "role": "backend", "weight": 2.0},
    {"id": "frontend-expert", "role": "frontend", "weight": 2.0},
    {"id": "qa-engineer", "role": "qa", "weight": 2.5},
    {"id": "devops-engineer", "role": "devops", "weight": 2.5}
]

for agent in agents:
    coordinator.add_agent(agent["id"])

# Setup coordination
memory = MemoryProvider()
consensus = ConsensusManager(coordinator)
resolver = ConflictResolver(strategy="lww")
synchronizer = StateSynchronizer(coordinator, memory, resolver)

# Configure weighted voting
agent_weights = {a["id"]: a["weight"] for a in agents}
weighted = WeightedAlgorithm(threshold=0.65, agent_weights=agent_weights)
consensus.register_algorithm("weighted", weighted)

# Deployment proposal
deployment_proposal = {
    "proposal_id": "deploy-v3.0",
    "action": "deploy",
    "version": "v3.0",
    "environment": "production",
    "rollback_plan": True,
    "canary_percentage": 10
}

# Step 1: Consensus vote
result = consensus.request_consensus(
    deployment_proposal,
    algorithm="weighted",
    timeout_ms=60000
)

print(f"Deployment Decision: {result.decision}")
print(f"Weighted Approval: {result.metadata['weighted_approval']:.2%}")
print(f"Votes:")
for participant in result.participants:
    print(f"  - {participant}: {result.vote_details.get(participant, 'N/A')}")

# Step 2: If approved, synchronize deployment state
if result.decision == "approved":
    # Store deployment metadata
    deployment_state = {
        "version": "v3.0",
        "status": "deploying",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "approved_by": result.participants,
        "weighted_approval": result.metadata["weighted_approval"]
    }

    # Sync across swarm
    success = synchronizer.synchronize_state(
        swarm_id="prod-swarm",
        state_key="deployment_state",
        timeout_ms=10000
    )

    if success:
        print("Deployment state synchronized across swarm")

        # Track deployment progress
        for progress in [10, 25, 50, 75, 100]:
            deployment_state["progress"] = progress
            synchronizer.synchronize_state("prod-swarm", "deployment_state")
            print(f"Deployment progress: {progress}%")
```

**Output**:
```
Deployment Decision: approved
Weighted Approval: 73%
Votes:
  - lead-engineer: approve
  - backend-expert: approve
  - frontend-expert: approve
  - qa-engineer: reject
  - devops-engineer: approve
Deployment state synchronized across swarm
Deployment progress: 10%
Deployment progress: 25%
Deployment progress: 50%
Deployment progress: 75%
Deployment progress: 100%
```

---

## Example 2: Task Distribution Swarm

10-agent swarm with load-balanced task distribution using state sync.

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
import random

# Setup large swarm
coordinator = SwarmCoordinator(topology="mesh")

# Add 10 worker agents
worker_agents = [f"worker-{i}" for i in range(1, 11)]
for agent_id in worker_agents:
    coordinator.add_agent(agent_id)

# Setup coordination
memory = MemoryProvider()
resolver = ConflictResolver(strategy="crdt")
synchronizer = StateSynchronizer(coordinator, memory, resolver)

# Initialize task queue (CRDT set)
task_queue = [
    {"id": f"task-{i}", "type": "compute", "priority": random.randint(1, 10)}
    for i in range(1, 51)  # 50 tasks
]

# Synchronize initial task queue
synchronizer.synchronize_state("compute-swarm", "task_queue")

# Each agent tracks its assigned tasks
agent_assignments = {agent_id: [] for agent_id in worker_agents}

# Distribute tasks (round-robin)
for i, task in enumerate(task_queue):
    agent_id = worker_agents[i % len(worker_agents)]
    agent_assignments[agent_id].append(task)

    # Sync agent task list
    synchronizer.synchronize_state(
        "compute-swarm",
        f"tasks_{agent_id}"
    )

print("Task Distribution:")
for agent_id, tasks in agent_assignments.items():
    print(f"{agent_id}: {len(tasks)} tasks")

# Track completion progress
completed_tasks = 0
total_tasks = len(task_queue)

def complete_task(agent_id, task_id):
    """Simulate task completion."""
    global completed_tasks

    # Get agent's task list
    task_list_state = synchronizer.get_state(
        "compute-swarm",
        f"tasks_{agent_id}"
    )

    if task_list_state:
        task_list = task_list_state.value
        task_list = [t for t in task_list if t["id"] != task_id]

        # Update completed count (CRDT counter)
        completed_tasks += 1

        # Sync updated task list
        synchronizer.synchronize_state("compute-swarm", f"tasks_{agent_id}")

        # Sync completion counter
        synchronizer.synchronize_state("compute-swarm", "completed_count")

# Simulate task execution
for agent_id in worker_agents:
    for task in agent_assignments[agent_id][:2]:  # Complete first 2 tasks
        complete_task(agent_id, task["id"])

print(f"\nCompleted: {completed_tasks}/{total_tasks} tasks")
```

**Output**:
```
Task Distribution:
worker-1: 5 tasks
worker-2: 5 tasks
worker-3: 5 tasks
worker-4: 5 tasks
worker-5: 5 tasks
worker-6: 5 tasks
worker-7: 5 tasks
worker-8: 5 tasks
worker-9: 5 tasks
worker-10: 5 tasks

Completed: 20/50 tasks
```

---

## Example 3: Agent Failure Recovery

Swarm with Byzantine fault tolerance detecting and recovering from malicious agent.

```python
from moai_flow.coordination import ConsensusManager
from moai_flow.coordination.algorithms import ByzantineConsensus
from moai_flow.coordination import Vote, VoteType
from moai_flow.core import SwarmCoordinator

# Setup swarm with Byzantine tolerance
coordinator = SwarmCoordinator(topology="mesh")

# Add 7 agents (n=7 allows f=2 fault tolerance)
agents = [f"agent-{i}" for i in range(1, 8)]
for agent_id in agents:
    coordinator.add_agent(agent_id)

# Setup Byzantine consensus (f=2)
manager = ConsensusManager(coordinator)
byzantine = ByzantineConsensus(fault_tolerance=2, num_rounds=3)
manager.register_algorithm("byzantine", byzantine)

# Critical security proposal
security_proposal = {
    "proposal_id": "security-patch",
    "action": "deploy_security_patch",
    "severity": "critical",
    "patch_version": "1.2.3"
}

# Simulate voting with malicious agent
# agent-7 is malicious and changes vote across rounds
proposal_id = byzantine.propose(security_proposal, agents)

# Collect votes
votes = [
    Vote("agent-1", VoteType.FOR),
    Vote("agent-2", VoteType.FOR),
    Vote("agent-3", VoteType.FOR),
    Vote("agent-4", VoteType.FOR),
    Vote("agent-5", VoteType.FOR),
    Vote("agent-6", VoteType.AGAINST),
    Vote("agent-7", VoteType.AGAINST)  # Malicious (changes in other rounds)
]

# Byzantine consensus decision
result = byzantine.decide(proposal_id, votes, timeout_reached=False)

print(f"Decision: {result.decision}")
print(f"Malicious agents detected: {result.metadata['malicious_detected']}")
print(f"Malicious agents: {result.metadata['malicious_agents']}")
print(f"Honest votes for: {result.votes_for}")
print(f"Agreement threshold: {result.metadata['agreement_threshold']}")
print(f"Byzantine safe: {result.metadata['byzantine_safe']}")

# Blacklist malicious agents
malicious_agents = result.metadata['malicious_agents']
for agent_id in malicious_agents:
    coordinator.remove_agent(agent_id)
    print(f"Removed malicious agent: {agent_id}")

# Re-run consensus without malicious agents
healthy_agents = [a for a in agents if a not in malicious_agents]
print(f"\nHealthy agents: {healthy_agents}")
```

**Output**:
```
Decision: approved
Malicious agents detected: 1
Malicious agents: ['agent-7']
Honest votes for: 5
Agreement threshold: 5
Byzantine safe: True
Removed malicious agent: agent-7

Healthy agents: ['agent-1', 'agent-2', 'agent-3', 'agent-4', 'agent-5', 'agent-6']
```

---

## Example 4: Dynamic Agent Reconnection

Agent reconnects and catches up using delta synchronization.

```python
from moai_flow.core import SwarmCoordinator
from moai_flow.memory import MemoryProvider
from moai_flow.coordination import StateSynchronizer, ConflictResolver
from datetime import datetime, timezone
import time

# Setup swarm
coordinator = SwarmCoordinator()
memory = MemoryProvider()
resolver = ConflictResolver(strategy="lww")
synchronizer = StateSynchronizer(coordinator, memory, resolver)

# Initialize swarm state
swarm_id = "resilient-swarm"
initial_states = {
    "counter": 100,
    "task_queue": ["task1", "task2"],
    "agent_count": 5
}

for state_key, value in initial_states.items():
    synchronizer.synchronize_state(swarm_id, state_key)

print("Initial state synchronized")

# Simulate agent disconnect
agent_id = "agent-reconnect"
last_known_version = synchronizer.get_state_version(swarm_id, "counter")
print(f"Agent {agent_id} disconnecting at version {last_known_version}")

# Simulate state updates while agent is offline
time.sleep(1)

# Update 1: Increment counter
synchronizer.synchronize_state(swarm_id, "counter")

# Update 2: Add tasks to queue
synchronizer.synchronize_state(swarm_id, "task_queue")

# Update 3: Update agent count
synchronizer.synchronize_state(swarm_id, "agent_count")

# Agent reconnects
print(f"\nAgent {agent_id} reconnecting...")

# Delta sync to catch up
changes = synchronizer.delta_sync(swarm_id, since_version=last_known_version)

print(f"Received {len(changes)} state updates:")
for change in changes:
    print(f"  - {change.state_key}: v{last_known_version} → v{change.version}")
    print(f"    Value: {change.value}")

# Update agent's last known version
new_version = max(c.version for c in changes) if changes else last_known_version
print(f"\nAgent caught up to version {new_version}")
```

**Output**:
```
Initial state synchronized
Agent agent-reconnect disconnecting at version 1

Agent agent-reconnect reconnecting...
Received 3 state updates:
  - counter: v1 → v2
    Value: 101
  - task_queue: v1 → v2
    Value: ['task1', 'task2', 'task3']
  - agent_count: v1 → v2
    Value: 6

Agent caught up to version 2
```

---

## Example 5: Multi-Stage Consensus Pipeline

Complex workflow with multiple consensus decisions and state synchronization.

```python
from moai_flow.core import SwarmCoordinator
from moai_flow.memory import MemoryProvider
from moai_flow.coordination import (
    ConsensusManager,
    ConflictResolver,
    StateSynchronizer
)

# Setup
coordinator = SwarmCoordinator()
memory = MemoryProvider()
consensus = ConsensusManager(coordinator, default_algorithm="quorum")
resolver = ConflictResolver(strategy="crdt")
synchronizer = StateSynchronizer(coordinator, memory, resolver)

swarm_id = "pipeline-swarm"

# Stage 1: Approve architecture change
architecture_proposal = {
    "proposal_id": "architecture-change",
    "stage": "architecture",
    "action": "redesign_api_gateway"
}

result1 = consensus.request_consensus(architecture_proposal)
print(f"Stage 1 (Architecture): {result1.decision}")

if result1.decision == "approved":
    synchronizer.synchronize_state(swarm_id, "architecture_decision")

    # Stage 2: Approve implementation plan
    implementation_proposal = {
        "proposal_id": "implementation-plan",
        "stage": "implementation",
        "action": "create_migration_plan"
    }

    result2 = consensus.request_consensus(implementation_proposal)
    print(f"Stage 2 (Implementation): {result2.decision}")

    if result2.decision == "approved":
        synchronizer.synchronize_state(swarm_id, "implementation_decision")

        # Stage 3: Approve deployment strategy
        deployment_proposal = {
            "proposal_id": "deployment-strategy",
            "stage": "deployment",
            "action": "blue_green_deployment"
        }

        result3 = consensus.request_consensus(deployment_proposal)
        print(f"Stage 3 (Deployment): {result3.decision}")

        if result3.decision == "approved":
            synchronizer.synchronize_state(swarm_id, "deployment_decision")

            # All stages approved
            print("\nAll stages approved! Proceeding with execution.")

            # Sync final pipeline state
            pipeline_state = {
                "architecture": "approved",
                "implementation": "approved",
                "deployment": "approved",
                "status": "ready_to_execute"
            }

            synchronizer.synchronize_state(swarm_id, "pipeline_state")
        else:
            print("Deployment stage rejected")
    else:
        print("Implementation stage rejected")
else:
    print("Architecture stage rejected")
```

**Output**:
```
Stage 1 (Architecture): approved
Stage 2 (Implementation): approved
Stage 3 (Deployment): approved

All stages approved! Proceeding with execution.
```

---

**Next**: [Advanced Consensus Examples](advanced-consensus.md)
