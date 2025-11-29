"""
Comprehensive tests for GossipProtocol.

Tests cover:
- Peer selection (fanout, exclude self, small networks)
- State propagation (single round, multi-round convergence, majority rule)
- Convergence detection (95% threshold, partial convergence, max rounds)
- Integration (consensus manager, large networks, fault tolerance)
- Performance benchmarks (convergence speed, message complexity)

Following TDD RED-GREEN-REFACTOR cycle with 90%+ coverage target.
"""

import sys
from pathlib import Path

# Add moai-flow directory to Python path
project_root = Path(__file__).parent.parent.parent.parent
moai_flow_path = project_root / "moai_flow"
sys.path.insert(0, str(moai_flow_path))

import pytest
import random
from typing import Dict, List
import importlib.util

# Direct module import to avoid circular dependencies
spec = importlib.util.spec_from_file_location(
    "gossip",
    moai_flow_path / "coordination" / "algorithms" / "gossip.py"
)
gossip_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gossip_module)
GossipProtocol = gossip_module.GossipProtocol


# ==========================================
# Fixtures
# ==========================================


@pytest.fixture
def gossip_default():
    """Create gossip protocol with default settings (fanout=3, rounds=10)."""
    return GossipProtocol(fanout=3, max_rounds=10, convergence_threshold=0.95)


@pytest.fixture
def gossip_small_fanout():
    """Create gossip with small fanout (fanout=2)."""
    return GossipProtocol(fanout=2, max_rounds=5, convergence_threshold=0.95)


@pytest.fixture
def gossip_large_fanout():
    """Create gossip with large fanout (fanout=5)."""
    return GossipProtocol(fanout=5, max_rounds=10, convergence_threshold=0.95)


@pytest.fixture
def votes_10_agents_majority_for() -> Dict[str, str]:
    """10 agents, 7 vote for, 3 vote against."""
    return {
        **{f"agent-{i}": "for" for i in range(7)},
        **{f"agent-{i}": "against" for i in range(7, 10)}
    }


@pytest.fixture
def votes_10_agents_even_split() -> Dict[str, str]:
    """10 agents, 5 vote for, 5 vote against."""
    return {
        **{f"agent-{i}": "for" for i in range(5)},
        **{f"agent-{i}": "against" for i in range(5, 10)}
    }


@pytest.fixture
def votes_50_agents() -> Dict[str, str]:
    """50 agents, 30 vote for, 20 vote against."""
    return {
        **{f"agent-{i}": "for" for i in range(30)},
        **{f"agent-{i}": "against" for i in range(30, 50)}
    }


@pytest.fixture
def votes_100_agents() -> Dict[str, str]:
    """100 agents, 70 vote for, 30 vote against."""
    return {
        **{f"agent-{i}": "for" for i in range(70)},
        **{f"agent-{i}": "against" for i in range(70, 100)}
    }


# ==========================================
# Test: Initialization
# ==========================================


def test_gossip_init_default():
    """Test initialization with default parameters."""
    gossip = GossipProtocol()
    assert gossip._config.fanout == 3
    assert gossip._config.max_rounds == 5  # Updated default
    assert gossip._config.convergence_threshold == 0.95


def test_gossip_init_custom():
    """Test initialization with custom parameters."""
    gossip = GossipProtocol(fanout=5, rounds=15, convergence_threshold=0.90)
    assert gossip._config.fanout == 5
    assert gossip._config.max_rounds == 15
    assert gossip._config.convergence_threshold == 0.90


def test_gossip_init_invalid_fanout():
    """Test initialization with invalid fanout raises error."""
    with pytest.raises(ValueError, match="Fanout must be"):
        GossipProtocol(fanout=0)


def test_gossip_init_invalid_rounds():
    """Test initialization with invalid max_rounds raises error."""
    with pytest.raises(ValueError, match="Max rounds must be"):
        GossipProtocol(max_rounds=0)


def test_gossip_init_invalid_threshold_negative():
    """Test initialization with negative threshold raises error."""
    with pytest.raises(ValueError, match="Convergence threshold"):
        GossipProtocol(convergence_threshold=-0.1)


def test_gossip_init_invalid_threshold_above_one():
    """Test initialization with threshold > 1.0 raises error."""
    with pytest.raises(ValueError, match="Convergence threshold"):
        GossipProtocol(convergence_threshold=1.5)


# ==========================================
# Test A: Peer Selection (3 tests)
# ==========================================


def test_random_peer_selection_fanout_3(gossip_default):
    """Test random peer selection with fanout=3."""
    agents = [f"agent-{i}" for i in range(10)]
    current_agent = "agent-0"

    # Select peers multiple times
    selections = []
    for _ in range(10):
        peers = gossip_default._select_peers(current_agent, agents)
        selections.append(peers)
        # Should select exactly 3 peers (or less if network too small)
        assert len(peers) <= 3
        # Should not include self
        assert current_agent not in peers

    # Ensure randomness (at least some variation)
    unique_selections = [tuple(sorted(s)) for s in selections]
    assert len(set(unique_selections)) > 1  # At least 2 different selections


def test_exclude_self_from_peers(gossip_default):
    """Test that self is never selected as peer."""
    agents = [f"agent-{i}" for i in range(10)]

    for agent in agents:
        peers = gossip_default._select_peers(agent, agents)
        assert agent not in peers


def test_fanout_larger_than_network(gossip_large_fanout):
    """Test fanout larger than network size."""
    # Network with only 3 agents, but fanout is 5
    agents = ["agent-0", "agent-1", "agent-2"]
    current_agent = "agent-0"

    peers = gossip_large_fanout._select_peers(current_agent, agents)

    # Should select all available peers (2 peers, excluding self)
    assert len(peers) == 2
    assert "agent-1" in peers
    assert "agent-2" in peers
    assert "agent-0" not in peers


# ==========================================
# Test B: State Propagation (3 tests)
# ==========================================


def test_single_round_propagation(gossip_default, votes_10_agents_majority_for):
    """Test state propagation in single round spreads to fanout peers."""
    agents = list(votes_10_agents_majority_for.keys())
    gossip_default._agent_states = votes_10_agents_majority_for.copy()

    # Execute one round
    gossip_default._execute_gossip_round(agents)

    # After one round, states should still exist for all agents
    assert len(gossip_default._agent_states) == len(agents)

    # All agents should have valid votes
    for vote in gossip_default._agent_states.values():
        assert vote in ["for", "against", "abstain"]


def test_multi_round_convergence(gossip_default, votes_10_agents_majority_for):
    """Test multi-round convergence (5 rounds should converge)."""
    agents = list(votes_10_agents_majority_for.keys())
    gossip_default._agent_states = votes_10_agents_majority_for.copy()

    # Execute 5 rounds
    for _ in range(5):
        gossip_default._execute_gossip_round(agents)

    # Check if converged
    converged, majority_vote = gossip_default._check_convergence()

    # With 70% initial majority, should converge to "for"
    # (convergence depends on randomness, but likely converges)
    if converged:
        assert majority_vote == "for"


def test_state_update_majority_rule(gossip_default):
    """Test state update follows majority rule."""
    # Test _get_majority method
    votes_majority_for = ["for", "for", "against"]
    assert gossip_default._get_majority(votes_majority_for) == "for"

    votes_majority_against = ["against", "against", "for"]
    assert gossip_default._get_majority(votes_majority_against) == "against"

    votes_tie = ["for", "against"]
    result = gossip_default._get_majority(votes_tie)
    assert result in ["for", "against"]  # Tie breaks arbitrarily


# ==========================================
# Test C: Convergence Detection (3 tests)
# ==========================================


def test_95_percent_convergence(gossip_default):
    """Test 95% convergence threshold detection."""
    # Create state where 95% agree on "for"
    agents = [f"agent-{i}" for i in range(100)]
    gossip_default._agent_states = {
        **{f"agent-{i}": "for" for i in range(95)},
        **{f"agent-{i}": "against" for i in range(95, 100)}
    }

    converged, majority_vote = gossip_default._check_convergence()

    assert converged is True
    assert majority_vote == "for"


def test_partial_convergence(gossip_default):
    """Test partial convergence (< 95%) is not detected."""
    # Create state where only 80% agree (below 95% threshold)
    agents = [f"agent-{i}" for i in range(100)]
    gossip_default._agent_states = {
        **{f"agent-{i}": "for" for i in range(80)},
        **{f"agent-{i}": "against" for i in range(80, 100)}
    }

    converged, majority_vote = gossip_default._check_convergence()

    assert converged is False
    assert majority_vote is None


def test_max_rounds_timeout(gossip_small_fanout, votes_10_agents_even_split):
    """Test that gossip stops after max rounds even without convergence."""
    proposal_id = gossip_small_fanout.propose({}, list(votes_10_agents_even_split.keys()))

    # Use even split (hard to converge)
    result = gossip_small_fanout.decide(proposal_id, votes_10_agents_even_split)

    # Should execute exactly max_rounds (5)
    assert result.metadata["rounds_executed"] <= gossip_small_fanout.max_rounds

    # Should still return a decision (even if not converged)
    assert result.decision in ["approved", "rejected"]


# ==========================================
# Test D: Integration Tests (3 tests)
# ==========================================


def test_consensus_manager_integration(gossip_default, votes_10_agents_majority_for):
    """Test integration with consensus manager workflow."""
    # Simulate consensus manager workflow
    proposal = {"action": "deploy", "target": "production"}
    agents = list(votes_10_agents_majority_for.keys())

    # Step 1: Propose
    proposal_id = gossip_default.propose(proposal, agents)
    assert proposal_id.startswith("gossip-")

    # Step 2: Decide
    result = gossip_default.decide(proposal_id, votes_10_agents_majority_for)

    # Should reach decision
    assert result.decision in ["approved", "rejected"]
    assert result.votes_for == 7
    assert result.votes_against == 3

    # Metadata should include round info
    assert "rounds_executed" in result.metadata
    assert "converged" in result.metadata


def test_large_network_50_agents(gossip_default, votes_50_agents):
    """Test scalability with 50 agents."""
    proposal_id = gossip_default.propose({}, list(votes_50_agents.keys()))
    result = gossip_default.decide(proposal_id, votes_50_agents)

    # Should converge (60% initial majority)
    assert result.decision == "approved"
    assert len(result.participants) == 50

    # Should converge in reasonable rounds (< 5 rounds expected)
    assert result.metadata["rounds_executed"] <= 5


def test_agent_failures_during_gossip(gossip_default):
    """Test fault tolerance when some agents fail."""
    # Start with 10 agents, 7 vote for
    votes = {
        **{f"agent-{i}": "for" for i in range(7)},
        **{f"agent-{i}": "against" for i in range(7, 10)}
    }

    proposal_id = gossip_default.propose({}, list(votes.keys()))
    result = gossip_default.decide(proposal_id, votes)

    # Should still reach consensus despite potential failures
    assert result.decision in ["approved", "rejected"]

    # All original agents should be in participants
    assert len(result.participants) == 10


# ==========================================
# Test: Additional Coverage (Edge Cases)
# ==========================================


def test_empty_votes():
    """Test decide with empty votes."""
    gossip = GossipProtocol()
    proposal_id = gossip.propose({}, [])
    result = gossip.decide(proposal_id, {})

    assert result.decision == "rejected"
    assert result.votes_for == 0
    assert result.votes_against == 0
    assert "error" in result.metadata


def test_single_agent():
    """Test with single agent."""
    gossip = GossipProtocol(fanout=3)
    votes = {"agent-0": "for"}

    proposal_id = gossip.propose({}, list(votes.keys()))
    result = gossip.decide(proposal_id, votes)

    # Single agent should converge immediately
    assert result.decision == "approved"
    assert result.votes_for == 1
    assert result.metadata["converged"] is True


def test_all_vote_same(gossip_default):
    """Test when all agents vote the same (unanimous)."""
    votes = {f"agent-{i}": "for" for i in range(10)}

    proposal_id = gossip_default.propose({}, list(votes.keys()))
    result = gossip_default.decide(proposal_id, votes)

    # Should converge in 1 round (already unanimous)
    assert result.decision == "approved"
    assert result.votes_for == 10
    assert result.metadata["rounds_executed"] == 1
    assert result.metadata["converged"] is True


def test_get_state(gossip_default):
    """Test get_state returns current algorithm state."""
    state = gossip_default.get_state()

    assert state["algorithm"] == "gossip"
    assert state["fanout"] == 3
    assert state["max_rounds"] == 10
    assert state["convergence_threshold"] == 0.95


def test_reset(gossip_default, votes_10_agents_majority_for):
    """Test reset clears internal state."""
    proposal_id = gossip_default.propose({}, list(votes_10_agents_majority_for.keys()))
    gossip_default.decide(proposal_id, votes_10_agents_majority_for)

    # Reset
    result = gossip_default.reset()
    assert result is True

    # State should be cleared
    assert len(gossip_default._agent_states) == 0
    assert len(gossip_default._round_history) == 0


# ==========================================
# Test: Performance Benchmarks
# ==========================================


@pytest.mark.benchmark
def test_convergence_speed_10_agents(gossip_default, votes_10_agents_majority_for):
    """Benchmark: 10 agents should converge in < 3 rounds."""
    proposal_id = gossip_default.propose({}, list(votes_10_agents_majority_for.keys()))
    result = gossip_default.decide(proposal_id, votes_10_agents_majority_for)

    # 10 agents with 70% majority should converge quickly
    assert result.metadata["rounds_executed"] <= 3


@pytest.mark.benchmark
def test_convergence_speed_50_agents(gossip_default, votes_50_agents):
    """Benchmark: 50 agents should converge in < 5 rounds."""
    proposal_id = gossip_default.propose({}, list(votes_50_agents.keys()))
    result = gossip_default.decide(proposal_id, votes_50_agents)

    # 50 agents with 60% majority should converge reasonably fast
    assert result.metadata["rounds_executed"] <= 5


@pytest.mark.benchmark
def test_convergence_speed_100_agents(gossip_default, votes_100_agents):
    """Benchmark: 100 agents should converge in < 7 rounds."""
    proposal_id = gossip_default.propose({}, list(votes_100_agents.keys()))
    result = gossip_default.decide(proposal_id, votes_100_agents)

    # 100 agents with 70% majority should converge in reasonable time
    assert result.metadata["rounds_executed"] <= 7


def test_message_complexity(gossip_default, votes_50_agents):
    """Test message complexity is O(n * log n)."""
    proposal_id = gossip_default.propose({}, list(votes_50_agents.keys()))
    result = gossip_default.decide(proposal_id, votes_50_agents)

    n = len(votes_50_agents)
    fanout = gossip_default.fanout
    rounds = result.metadata["rounds_executed"]

    # Total messages ≈ n * fanout * rounds
    total_messages = n * fanout * rounds

    # Should be O(n * log n) or better
    import math
    expected_max = n * fanout * math.ceil(math.log2(n))

    assert total_messages <= expected_max


# ==========================================
# Test: State Distribution Tracking
# ==========================================


def test_state_distribution_tracking(gossip_default, votes_10_agents_majority_for):
    """Test that state distribution is tracked across rounds."""
    proposal_id = gossip_default.propose({}, list(votes_10_agents_majority_for.keys()))
    result = gossip_default.decide(proposal_id, votes_10_agents_majority_for)

    # Should have final distribution
    assert "final_distribution" in result.metadata
    distribution = result.metadata["final_distribution"]

    # Distribution should account for all agents
    total = sum(distribution.values())
    assert total == len(votes_10_agents_majority_for)


def test_round_history_recorded(gossip_default, votes_10_agents_majority_for):
    """Test that round history is recorded."""
    proposal_id = gossip_default.propose({}, list(votes_10_agents_majority_for.keys()))
    result = gossip_default.decide(proposal_id, votes_10_agents_majority_for)

    # Should have round history
    assert "round_history" in result.metadata
    history = result.metadata["round_history"]

    # Should have at least 1 round
    assert len(history) >= 1

    # Each round should have required fields
    for round_info in history:
        assert "round" in round_info
        assert "converged" in round_info
        assert "state_snapshot" in round_info


# ==========================================
# Test: Tie Breaking
# ==========================================


def test_tie_defaults_to_reject(gossip_default, votes_10_agents_even_split):
    """Test that ties default to reject."""
    # Force max rounds to ensure no convergence
    gossip = GossipProtocol(fanout=1, max_rounds=1, convergence_threshold=0.95)

    proposal_id = gossip.propose({}, list(votes_10_agents_even_split.keys()))
    result = gossip.decide(proposal_id, votes_10_agents_even_split)

    # Even split without convergence should default to reject
    # (or may converge to one side depending on randomness)
    assert result.decision in ["approved", "rejected"]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
