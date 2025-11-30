"""
Byzantine Consensus Algorithm Examples

Demonstrates Byzantine Fault Tolerance (BFT) consensus for multi-agent coordination:
- Basic Byzantine consensus with 4 agents
- Malicious agent detection
- Integration with ConsensusManager
- Real-world scenario with 7 agents and 2 malicious agents
"""

import logging
from moai_flow.core.swarm_coordinator import SwarmCoordinator
from moai_flow.coordination.algorithms.byzantine import ByzantineConsensus
from moai_flow.coordination import ConsensusManager, Vote, VoteType

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def example_1_basic_byzantine():
    """Example 1: Basic Byzantine consensus with 4 agents (f=1)."""
    print("\n" + "=" * 70)
    print("Example 1: Basic Byzantine Consensus (4 agents, tolerate 1 faulty)")
    print("=" * 70)

    # Create Byzantine consensus (tolerate 1 faulty agent)
    byzantine = ByzantineConsensus(fault_tolerance=1)

    print(f"\nByzantine Configuration:")
    print(f"  Fault tolerance (f): {byzantine.fault_tolerance}")
    print(f"  Min participants (3f+1): {byzantine.min_participants}")
    print(f"  Agreement threshold (2f+1): {byzantine.agreement_threshold}")

    # Define participants
    participants = ["agent-1", "agent-2", "agent-3", "agent-4"]

    # Create proposal
    proposal = {
        "action": "deploy",
        "version": "v2.0",
        "description": "Deploy new version to production"
    }

    print(f"\nProposal: {proposal}")
    proposal_id = byzantine.propose(proposal, participants)
    print(f"Proposal ID: {proposal_id}")

    # Collect votes (3 FOR, 1 AGAINST)
    votes = [
        Vote("agent-1", VoteType.FOR),
        Vote("agent-2", VoteType.FOR),
        Vote("agent-3", VoteType.FOR),
        Vote("agent-4", VoteType.AGAINST)
    ]

    print(f"\nVotes collected:")
    for vote in votes:
        print(f"  {vote.agent_id}: {vote.vote.value}")

    # Make decision
    result = byzantine.decide(proposal_id, votes)

    print(f"\nConsensus Result:")
    print(f"  Decision: {result.decision}")
    print(f"  Votes FOR: {result.votes_for}")
    print(f"  Votes AGAINST: {result.votes_against}")
    print(f"  Votes ABSTAIN: {result.votes_abstain}")
    print(f"  Byzantine Safe: {result.metadata['byzantine_safe']}")
    print(f"  Malicious Detected: {result.metadata['malicious_detected']}")


def example_2_malicious_detection():
    """Example 2: Detect malicious agents changing votes."""
    print("\n" + "=" * 70)
    print("Example 2: Malicious Agent Detection (7 agents, 2 malicious)")
    print("=" * 70)

    # Create Byzantine consensus (tolerate 2 faulty agents)
    byzantine = ByzantineConsensus(fault_tolerance=2)

    print(f"\nByzantine Configuration:")
    print(f"  Fault tolerance (f): {byzantine.fault_tolerance}")
    print(f"  Min participants (3f+1): {byzantine.min_participants}")
    print(f"  Agreement threshold (2f+1): {byzantine.agreement_threshold}")

    # Define participants
    participants = [f"agent-{i}" for i in range(1, 8)]

    # Create proposal
    proposal = {
        "action": "upgrade",
        "component": "database",
        "description": "Upgrade database to PostgreSQL 16"
    }

    print(f"\nProposal: {proposal}")
    proposal_id = byzantine.propose(proposal, participants)

    # Collect votes (5 FOR, 2 AGAINST - simulating malicious agents)
    votes = [
        Vote("agent-1", VoteType.FOR),   # Honest
        Vote("agent-2", VoteType.FOR),   # Honest
        Vote("agent-3", VoteType.FOR),   # Honest
        Vote("agent-4", VoteType.FOR),   # Honest
        Vote("agent-5", VoteType.FOR),   # Honest
        Vote("agent-6", VoteType.AGAINST),  # Potentially malicious
        Vote("agent-7", VoteType.AGAINST)   # Potentially malicious
    ]

    print(f"\nVotes collected:")
    for vote in votes:
        vote_label = "HONEST" if vote.vote == VoteType.FOR else "SUSPECT"
        print(f"  {vote.agent_id}: {vote.vote.value} ({vote_label})")

    # Make decision
    result = byzantine.decide(proposal_id, votes)

    print(f"\nConsensus Result:")
    print(f"  Decision: {result.decision}")
    print(f"  Votes FOR: {result.votes_for}")
    print(f"  Votes AGAINST: {result.votes_against}")
    print(f"  Honest participants: {result.metadata['honest_participants']}")
    print(f"  Malicious detected: {result.metadata['malicious_detected']}")
    print(f"  Malicious agents: {result.metadata['malicious_agents']}")
    print(f"  Byzantine safe: {result.metadata['byzantine_safe']}")


def example_3_consensus_manager_integration():
    """Example 3: Integration with ConsensusManager."""
    print("\n" + "=" * 70)
    print("Example 3: Byzantine Integration with ConsensusManager")
    print("=" * 70)

    # Create coordinator
    coordinator = SwarmCoordinator(topology_type="mesh")

    # Register agents
    for i in range(1, 8):
        coordinator.register_agent(
            f"agent-{i}",
            {"type": "worker", "capabilities": ["compute"]}
        )

    print(f"\nRegistered {coordinator.get_topology_info()['agent_count']} agents")

    # Create ConsensusManager
    manager = ConsensusManager(coordinator, default_algorithm="quorum")

    # Register Byzantine algorithm
    byzantine = ByzantineConsensus(fault_tolerance=2)
    success = manager.register_algorithm("byzantine", byzantine)

    print(f"\nAlgorithms registered:")
    for algo_name in manager.algorithms.keys():
        print(f"  - {algo_name}")

    print(f"\nByzantine algorithm registered: {success}")
    print(f"Byzantine can now be used with: manager.request_consensus(proposal, algorithm='byzantine')")


def example_4_real_world_scenario():
    """Example 4: Real-world deployment scenario."""
    print("\n" + "=" * 70)
    print("Example 4: Real-World Deployment Scenario")
    print("=" * 70)

    scenario = """
    Scenario: Production Deployment Decision
    - 7 microservices voting on deployment
    - 2 services may have network issues (Byzantine faults)
    - Need consensus despite potential failures
    - Requires 5/7 agreements (2f+1 where f=2)
    """
    print(scenario)

    # Create Byzantine consensus
    byzantine = ByzantineConsensus(fault_tolerance=2, num_rounds=3)

    # Define participants (microservices)
    services = [
        "api-gateway",
        "auth-service",
        "user-service",
        "order-service",
        "payment-service",
        "notification-service",
        "analytics-service"
    ]

    print(f"\nParticipating services: {len(services)}")
    for service in services:
        print(f"  - {service}")

    # Create deployment proposal
    proposal = {
        "action": "deploy",
        "version": "v3.0.0",
        "environment": "production",
        "rollback_enabled": True,
        "changes": [
            "New authentication flow",
            "Payment gateway upgrade",
            "Analytics dashboard v2"
        ]
    }

    print(f"\nDeployment Proposal:")
    print(f"  Version: {proposal['version']}")
    print(f"  Environment: {proposal['environment']}")
    print(f"  Changes: {len(proposal['changes'])} major updates")

    proposal_id = byzantine.propose(proposal, services)

    # Simulate voting
    # 5 services approve (healthy)
    # 2 services have issues (network fault/malicious)
    votes = [
        Vote("api-gateway", VoteType.FOR),
        Vote("auth-service", VoteType.FOR),
        Vote("user-service", VoteType.FOR),
        Vote("order-service", VoteType.FOR),
        Vote("payment-service", VoteType.FOR),
        Vote("notification-service", VoteType.AGAINST),  # Network issue
        Vote("analytics-service", VoteType.AGAINST)      # Malicious/faulty
    ]

    print(f"\nService votes:")
    for vote in votes:
        status = "✓ APPROVED" if vote.vote == VoteType.FOR else "✗ REJECTED"
        print(f"  {vote.agent_id:25s} {status}")

    # Make decision
    result = byzantine.decide(proposal_id, votes)

    print(f"\nDeployment Decision:")
    print(f"  Decision: {result.decision.upper()}")
    print(f"  Approvals: {result.votes_for}/{len(services)} (required: {byzantine.agreement_threshold})")
    print(f"  Rejections: {result.votes_against}/{len(services)}")
    print(f"  Honest services: {result.metadata['honest_participants']}")
    print(f"  Faulty detected: {result.metadata['malicious_detected']}")
    print(f"  Duration: {result.duration_ms}ms")
    print(f"  Byzantine safe: {'YES' if result.metadata['byzantine_safe'] else 'NO'}")

    if result.decision == "approved":
        print(f"\n✓ Deployment APPROVED despite {byzantine.fault_tolerance} potential failures")
    else:
        print(f"\n✗ Deployment REJECTED - insufficient consensus")


def main():
    """Run all Byzantine consensus examples."""
    print("\n" + "=" * 70)
    print("BYZANTINE CONSENSUS ALGORITHM EXAMPLES")
    print("=" * 70)

    try:
        example_1_basic_byzantine()
        example_2_malicious_detection()
        example_3_consensus_manager_integration()
        example_4_real_world_scenario()

        print("\n" + "=" * 70)
        print("All examples completed successfully!")
        print("=" * 70)

        print("\nKey Takeaways:")
        print("  1. Byzantine consensus tolerates f malicious/faulty agents")
        print("  2. Requires n >= 3f+1 participants")
        print("  3. Needs 2f+1 agreements for approval")
        print("  4. Multi-round voting detects malicious behavior")
        print("  5. Ideal for distributed systems with untrusted agents")

    except Exception as e:
        logger.error(f"Example failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
