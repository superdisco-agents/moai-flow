"""
Raft Consensus Algorithm Demo

Demonstrates Raft consensus for multi-agent decision making:
- Leader election
- Proposal submission
- Log replication
- Majority-based decision making
"""

import logging
from moai_flow.core.swarm_coordinator import SwarmCoordinator
from moai_flow.coordination.algorithms import RaftConsensus

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def demo_raft_leader_election():
    """Demonstrate Raft leader election."""
    print("\n" + "=" * 60)
    print("Demo 1: Raft Leader Election")
    print("=" * 60)

    # Create coordinator with mesh topology
    coordinator = SwarmCoordinator(topology="mesh")

    # Register agents
    for i in range(5):
        coordinator.register_agent(
            f"agent-{i}",
            {"type": "worker", "capabilities": ["compute"]}
        )

    # Create Raft consensus
    raft = RaftConsensus(coordinator, election_timeout_ms=5000)

    # Initial state
    print("\nInitial state:")
    state = raft.get_state()
    print(f"  State: {state['state']}")
    print(f"  Term: {state['term']}")
    print(f"  Leader: {state['leader']}")

    # Trigger leader election
    print("\nTriggering leader election...")
    leader = raft.elect_leader()
    print(f"  Elected leader: {leader}")

    # Check state after election
    state = raft.get_state()
    print(f"\nState after election:")
    print(f"  State: {state['state']}")
    print(f"  Term: {state['term']}")
    print(f"  Leader: {state['leader']}")


def demo_raft_proposal_consensus():
    """Demonstrate Raft proposal consensus."""
    print("\n" + "=" * 60)
    print("Demo 2: Raft Proposal Consensus")
    print("=" * 60)

    # Create coordinator with mesh topology
    coordinator = SwarmCoordinator(topology="mesh")

    # Register agents
    for i in range(7):
        coordinator.register_agent(
            f"agent-{i}",
            {"type": "worker", "capabilities": ["compute"]}
        )

    # Create Raft consensus
    raft = RaftConsensus(coordinator, election_timeout_ms=5000)

    # Elect leader first
    print("\nElecting leader...")
    leader = raft.elect_leader()
    print(f"  Leader: {leader}")

    # Submit proposal
    proposal = {
        "proposal_id": "deploy-v2.0",
        "description": "Deploy version 2.0 to production",
        "changes": ["API updates", "Database migration", "UI refresh"]
    }

    print(f"\nSubmitting proposal: {proposal['proposal_id']}")
    result = raft.propose(proposal, timeout_ms=30000)

    # Display results
    print(f"\nConsensus result:")
    print(f"  Decision: {result.decision}")
    print(f"  Votes for: {result.votes_for}")
    print(f"  Votes against: {result.votes_against}")
    print(f"  Participants: {len(result.participants)}")
    print(f"  Term: {result.metadata.get('term')}")
    print(f"  Commit index: {result.metadata.get('commit_index')}")


def demo_raft_log_replication():
    """Demonstrate Raft log replication."""
    print("\n" + "=" * 60)
    print("Demo 3: Raft Log Replication")
    print("=" * 60)

    # Create coordinator
    coordinator = SwarmCoordinator(topology="mesh")

    # Register agents
    for i in range(5):
        coordinator.register_agent(
            f"agent-{i}",
            {"type": "worker", "capabilities": ["compute"]}
        )

    # Create Raft consensus
    raft = RaftConsensus(coordinator)

    # Elect leader
    print("\nElecting leader...")
    raft.elect_leader()

    # Submit multiple proposals
    proposals = [
        {"proposal_id": "task-1", "description": "Implement feature A"},
        {"proposal_id": "task-2", "description": "Fix bug B"},
        {"proposal_id": "task-3", "description": "Refactor module C"}
    ]

    print(f"\nSubmitting {len(proposals)} proposals...")
    results = []
    for proposal in proposals:
        result = raft.propose(proposal, timeout_ms=10000)
        results.append(result)
        print(f"  {proposal['proposal_id']}: {result.decision}")

    # Check log state
    state = raft.get_state()
    print(f"\nLog state:")
    print(f"  Log size: {state['log_size']}")
    print(f"  Commit index: {state['commit_index']}")
    print(f"  Term: {state['term']}")


def demo_raft_leader_failover():
    """Demonstrate Raft leader failover."""
    print("\n" + "=" * 60)
    print("Demo 4: Raft Leader Failover")
    print("=" * 60)

    # Create coordinator
    coordinator = SwarmCoordinator(topology="mesh")

    # Register agents
    for i in range(5):
        coordinator.register_agent(
            f"agent-{i}",
            {"type": "worker", "capabilities": ["compute"]}
        )

    # Create Raft consensus with short election timeout
    raft = RaftConsensus(coordinator, election_timeout_ms=2000)

    # Elect initial leader
    print("\nElecting initial leader...")
    leader1 = raft.elect_leader()
    state1 = raft.get_state()
    print(f"  Leader: {leader1}")
    print(f"  Term: {state1['term']}")

    # Simulate leader failure by resetting
    print("\nSimulating leader failure (reset)...")
    raft.reset()

    # Re-elect leader
    print("\nRe-electing leader after failure...")
    leader2 = raft.elect_leader()
    state2 = raft.get_state()
    print(f"  New leader: {leader2}")
    print(f"  New term: {state2['term']}")

    # Submit proposal with new leader
    proposal = {
        "proposal_id": "recovery-task",
        "description": "Continue after leader failover"
    }

    print(f"\nSubmitting proposal with new leader...")
    result = raft.propose(proposal)
    print(f"  Decision: {result.decision}")
    print(f"  Term: {result.metadata.get('term')}")


def main():
    """Run all Raft consensus demos."""
    print("\n" + "=" * 60)
    print("RAFT CONSENSUS ALGORITHM DEMO")
    print("=" * 60)

    try:
        demo_raft_leader_election()
        demo_raft_proposal_consensus()
        demo_raft_log_replication()
        demo_raft_leader_failover()

        print("\n" + "=" * 60)
        print("All demos completed successfully!")
        print("=" * 60)

    except Exception as e:
        logger.error(f"Demo failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
