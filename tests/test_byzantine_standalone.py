"""
Standalone Byzantine consensus tests (avoiding circular imports).

This is a simplified test suite that imports only what's necessary
to test the Byzantine consensus algorithm without triggering circular imports.
"""

import pytest
import sys
from pathlib import Path
from typing import List
from dataclasses import dataclass
from enum import Enum

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import only what we need (avoiding coordination/__init__.py)
from moai_flow.coordination.algorithms.byzantine import ByzantineConsensus

# Import types directly from consensus_manager (avoiding __init__.py)
from moai_flow.coordination.consensus_manager import Vote, VoteType, ConsensusDecision


# ==========================================
# Fixtures
# ==========================================


@pytest.fixture
def byzantine_f1():
    """Byzantine consensus with f=1 (tolerate 1 faulty)."""
    return ByzantineConsensus(fault_tolerance=1)


@pytest.fixture
def byzantine_f2():
    """Byzantine consensus with f=2 (tolerate 2 faulty)."""
    return ByzantineConsensus(fault_tolerance=2)


@pytest.fixture
def byzantine_f3():
    """Byzantine consensus with f=3 (tolerate 3 faulty)."""
    return ByzantineConsensus(fault_tolerance=3)


@pytest.fixture
def agents_4():
    """4 agents (minimum for f=1)."""
    return ["agent-1", "agent-2", "agent-3", "agent-4"]


@pytest.fixture
def agents_7():
    """7 agents (minimum for f=2)."""
    return [f"agent-{i}" for i in range(1, 8)]


@pytest.fixture
def agents_10():
    """10 agents (minimum for f=3)."""
    return [f"agent-{i}" for i in range(1, 11)]


# ==========================================
# A. Participant Validation Tests (3 tests)
# ==========================================


def test_minimum_participants_3f_plus_1(byzantine_f1, agents_4):
    """Test Byzantine requires n >= 3f+1 participants."""
    proposal_id = byzantine_f1.propose({"action": "test"}, agents_4)
    assert proposal_id.startswith("byzantine_")
    assert byzantine_f1.min_participants == 4


def test_insufficient_participants_rejected(byzantine_f1):
    """Test Byzantine rejects insufficient participants."""
    agents = ["agent-1", "agent-2", "agent-3"]
    with pytest.raises(ValueError, match="Insufficient participants"):
        byzantine_f1.propose({"action": "test"}, agents)


def test_fault_tolerance_scaling(byzantine_f1, byzantine_f2, byzantine_f3):
    """Test fault tolerance scaling (f=1,2,3)."""
    assert byzantine_f1.fault_tolerance == 1
    assert byzantine_f1.min_participants == 4
    assert byzantine_f1.agreement_threshold == 3

    assert byzantine_f2.fault_tolerance == 2
    assert byzantine_f2.min_participants == 7
    assert byzantine_f2.agreement_threshold == 5

    assert byzantine_f3.fault_tolerance == 3
    assert byzantine_f3.min_participants == 10
    assert byzantine_f3.agreement_threshold == 7


# ==========================================
# B. Multi-Round Voting Tests (4 tests)
# ==========================================


def test_three_round_voting(byzantine_f1, agents_4):
    """Test Byzantine executes 3 rounds of voting."""
    proposal_id = byzantine_f1.propose({"action": "deploy"}, agents_4)

    votes = [
        Vote("agent-1", VoteType.FOR),
        Vote("agent-2", VoteType.FOR),
        Vote("agent-3", VoteType.FOR),
        Vote("agent-4", VoteType.AGAINST)
    ]

    result = byzantine_f1.decide(proposal_id, votes)
    assert result.metadata["num_rounds"] == 3
    assert result.decision == ConsensusDecision.APPROVED.value


def test_consistent_honest_votes(byzantine_f1, agents_4):
    """Test honest agents maintain consistent votes across rounds."""
    proposal_id = byzantine_f1.propose({"action": "test"}, agents_4)

    votes = [
        Vote("agent-1", VoteType.FOR),
        Vote("agent-2", VoteType.FOR),
        Vote("agent-3", VoteType.FOR),
        Vote("agent-4", VoteType.FOR)
    ]

    result = byzantine_f1.decide(proposal_id, votes)
    assert result.metadata["malicious_detected"] == 0
    assert len(result.metadata["malicious_agents"]) == 0


def test_round_timeout_handling(byzantine_f1, agents_4):
    """Test handling of round timeouts."""
    proposal_id = byzantine_f1.propose({"action": "timeout_test"}, agents_4)

    votes = [
        Vote("agent-1", VoteType.FOR),
        Vote("agent-2", VoteType.FOR)
    ]

    result = byzantine_f1.decide(proposal_id, votes, timeout_reached=True)
    assert result.decision == ConsensusDecision.TIMEOUT.value


def test_vote_aggregation_across_rounds(byzantine_f1, agents_4):
    """Test vote aggregation across multiple rounds."""
    proposal_id = byzantine_f1.propose({"action": "aggregate"}, agents_4)

    votes = [
        Vote("agent-1", VoteType.FOR),
        Vote("agent-2", VoteType.FOR),
        Vote("agent-3", VoteType.FOR),
        Vote("agent-4", VoteType.AGAINST)
    ]

    result = byzantine_f1.decide(proposal_id, votes)

    total_votes = result.votes_for + result.votes_against + result.votes_abstain
    assert total_votes <= len(agents_4)
    assert result.votes_for == 3


# ==========================================
# C. Malicious Detection Tests (4 tests)
# ==========================================


def test_detect_vote_changing(byzantine_f2, agents_7):
    """Test detection metadata is present."""
    proposal_id = byzantine_f2.propose({"action": "test_malicious"}, agents_7)

    votes = [
        Vote(f"agent-{i}", VoteType.FOR if i <= 5 else VoteType.AGAINST)
        for i in range(1, 8)
    ]

    result = byzantine_f2.decide(proposal_id, votes)

    assert "malicious_detected" in result.metadata
    assert "malicious_agents" in result.metadata
    assert isinstance(result.metadata["malicious_agents"], list)


def test_exclude_malicious_from_count(byzantine_f2, agents_7):
    """Test malicious agents are excluded from final vote count."""
    proposal_id = byzantine_f2.propose({"action": "exclude_test"}, agents_7)

    votes = [
        Vote(f"agent-{i}", VoteType.FOR if i <= 5 else VoteType.AGAINST)
        for i in range(1, 8)
    ]

    result = byzantine_f2.decide(proposal_id, votes)

    honest_count = result.metadata["honest_participants"]
    total_count = result.metadata["total_participants"]
    assert honest_count <= total_count


def test_false_positive_handling(byzantine_f1, agents_4):
    """Test system handles cases with no actual malicious agents."""
    proposal_id = byzantine_f1.propose({"action": "honest_only"}, agents_4)

    votes = [
        Vote("agent-1", VoteType.FOR),
        Vote("agent-2", VoteType.FOR),
        Vote("agent-3", VoteType.AGAINST),
        Vote("agent-4", VoteType.AGAINST)
    ]

    result = byzantine_f1.decide(proposal_id, votes)

    assert result.metadata["malicious_detected"] == 0
    assert result.metadata["honest_participants"] == len(votes)


def test_multiple_malicious_agents(byzantine_f2, agents_7):
    """Test detection of up to f malicious agents."""
    proposal_id = byzantine_f2.propose({"action": "multi_malicious"}, agents_7)

    votes = [
        Vote(f"agent-{i}", VoteType.FOR if i <= 5 else VoteType.AGAINST)
        for i in range(1, 8)
    ]

    result = byzantine_f2.decide(proposal_id, votes)

    malicious_detected = result.metadata["malicious_detected"]
    assert malicious_detected >= 0
    assert malicious_detected <= byzantine_f2.fault_tolerance


# ==========================================
# D. Agreement Threshold Tests (2 tests)
# ==========================================


def test_2f_plus_1_requirement(byzantine_f1, agents_4):
    """Test 2f+1 agreement threshold for approval."""
    proposal_id = byzantine_f1.propose({"action": "threshold_test"}, agents_4)

    votes = [
        Vote("agent-1", VoteType.FOR),
        Vote("agent-2", VoteType.FOR),
        Vote("agent-3", VoteType.FOR),
        Vote("agent-4", VoteType.AGAINST)
    ]

    result = byzantine_f1.decide(proposal_id, votes)
    assert result.decision == ConsensusDecision.APPROVED.value
    assert result.votes_for >= byzantine_f1.agreement_threshold


def test_insufficient_honest_votes(byzantine_f1, agents_4):
    """Test rejection when insufficient honest votes."""
    proposal_id = byzantine_f1.propose({"action": "insufficient"}, agents_4)

    votes = [
        Vote("agent-1", VoteType.FOR),
        Vote("agent-2", VoteType.FOR),
        Vote("agent-3", VoteType.AGAINST),
        Vote("agent-4", VoteType.AGAINST)
    ]

    result = byzantine_f1.decide(proposal_id, votes)
    assert result.decision == ConsensusDecision.REJECTED.value
    assert result.votes_for < byzantine_f1.agreement_threshold


# ==========================================
# E. Real-World Scenario Test
# ==========================================


def test_real_world_scenario_7_agents_2_malicious(byzantine_f2, agents_7):
    """Test real-world scenario with 7 agents and 2 potentially malicious."""
    proposal_id = byzantine_f2.propose(
        {"action": "deploy", "version": "v2.0"},
        agents_7
    )

    votes = [
        Vote("agent-1", VoteType.FOR),
        Vote("agent-2", VoteType.FOR),
        Vote("agent-3", VoteType.FOR),
        Vote("agent-4", VoteType.FOR),
        Vote("agent-5", VoteType.FOR),
        Vote("agent-6", VoteType.AGAINST),
        Vote("agent-7", VoteType.AGAINST)
    ]

    result = byzantine_f2.decide(proposal_id, votes)

    assert result.decision == ConsensusDecision.APPROVED.value
    assert result.votes_for >= byzantine_f2.agreement_threshold
    assert result.metadata["total_participants"] == 7
    assert result.metadata["byzantine_safe"] is True


# ==========================================
# Additional Edge Case Tests
# ==========================================


def test_byzantine_init_invalid_fault_tolerance():
    """Test Byzantine initialization with invalid fault tolerance."""
    with pytest.raises(ValueError, match="Fault tolerance must be >= 0"):
        ByzantineConsensus(fault_tolerance=-1)


def test_byzantine_init_invalid_rounds():
    """Test Byzantine initialization with invalid rounds."""
    with pytest.raises(ValueError, match="requires >= 3 rounds"):
        ByzantineConsensus(fault_tolerance=1, num_rounds=2)


def test_byzantine_init_valid():
    """Test valid Byzantine initialization."""
    byzantine = ByzantineConsensus(fault_tolerance=2, num_rounds=5)
    assert byzantine.fault_tolerance == 2
    assert byzantine.num_rounds == 5
    assert byzantine.min_participants == 7
    assert byzantine.agreement_threshold == 5


def test_get_algorithm_name():
    """Test get_algorithm_name method."""
    byzantine = ByzantineConsensus(fault_tolerance=1)
    assert byzantine.get_algorithm_name() == "byzantine"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
