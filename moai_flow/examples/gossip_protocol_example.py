"""
Gossip Protocol Usage Examples

Demonstrates epidemic-style consensus for scalable agent networks.
Shows basic usage, large-scale scenarios, and performance characteristics.
"""

import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def example_1_basic_gossip():
    """Example 1: Basic Gossip Protocol with 10 Agents."""
    from moai_flow.coordination.algorithms.gossip import GossipProtocol

    print("\n" + "=" * 60)
    print("Example 1: Basic Gossip (10 agents, fanout=3)")
    print("=" * 60)

    # Create gossip protocol with standard settings
    gossip = GossipProtocol(fanout=3, rounds=5, convergence_threshold=0.95)

    # Initial votes: 7 for, 3 against (70% majority)
    votes = {
        **{f"agent-{i}": "for" for i in range(7)},
        **{f"agent-{i}": "against" for i in range(7, 10)}
    }

    print(f"\nInitial votes:")
    print(f"  For: 7 agents (70%)")
    print(f"  Against: 3 agents (30%)")

    # Execute consensus
    proposal = {
        "proposal_id": "deploy-v2",
        "votes": votes,
        "threshold": 0.66
    }

    result = gossip.propose(proposal)

    print(f"\nGossip Result:")
    print(f"  Decision: {result.decision}")
    print(f"  Rounds: {result.metadata['rounds_executed']}")
    print(f"  Converged: {result.metadata['converged']}")
    print(f"  Final votes for: {result.votes_for}")
    print(f"  Final votes against: {result.votes_against}")
    print(f"  Final distribution: {result.metadata['final_distribution']}")


def example_2_large_scale():
    """Example 2: Large Scale Gossip with 100 Agents."""
    from moai_flow.coordination.algorithms.gossip import GossipProtocol

    print("\n" + "=" * 60)
    print("Example 2: Large Scale Gossip (100 agents, fanout=5)")
    print("=" * 60)

    # Create gossip with larger fanout for bigger network
    gossip = GossipProtocol(fanout=5, rounds=10, convergence_threshold=0.95)

    # Initial votes: 70 for, 30 against (70% majority)
    votes = {
        **{f"agent-{i}": "for" for i in range(70)},
        **{f"agent-{i}": "against" for i in range(70, 100)}
    }

    print(f"\nInitial votes:")
    print(f"  For: 70 agents (70%)")
    print(f"  Against: 30 agents (30%)")

    # Execute consensus
    proposal = {
        "proposal_id": "scale-test",
        "votes": votes,
        "threshold": 0.66
    }

    result = gossip.propose(proposal)

    print(f"\nGossip Result:")
    print(f"  Decision: {result.decision}")
    print(f"  Rounds: {result.metadata['rounds_executed']}")
    print(f"  Converged: {result.metadata['converged']}")
    print(f"  Convergence threshold: {result.metadata['convergence_threshold']:.0%}")
    print(f"  Fanout: {result.metadata['fanout']}")

    # Performance analysis
    n = len(votes)
    fanout = gossip._config.fanout
    rounds = result.metadata['rounds_executed']
    total_messages = n * fanout * rounds

    print(f"\nPerformance Analysis:")
    print(f"  Total messages: {total_messages}")
    print(f"  Messages per agent: {fanout * rounds}")
    print(f"  Theoretical O(n log n): {n * fanout * 7}  # log2(100) ≈ 7")
    print(f"  Efficiency: {(n * fanout * 7) / total_messages:.2f}x optimal")


if __name__ == "__main__":
    example_1_basic_gossip()
    example_2_large_scale()

    print("\n" + "=" * 60)
    print("Examples completed successfully!")
    print("=" * 60)
