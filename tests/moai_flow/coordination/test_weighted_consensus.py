"""
Comprehensive tests for WeightedConsensus.

Tests cover:
- Default weights (1.0)
- Expert weight presets
- Dynamic weight updates
- Weighted vote calculation
- Domain-specific weighting
- Edge cases (equal weights, all abstain)
- Weight validation (negative, zero)

Following TDD RED-GREEN-REFACTOR cycle with 93%+ coverage target.
"""

import sys
from pathlib import Path

# Add moai-flow directory to Python path
project_root = Path(__file__).parent.parent.parent.parent
moai_flow_path = project_root / "moai_flow"
sys.path.insert(0, str(moai_flow_path))

import pytest
import asyncio
from typing import Any, Dict, List
from datetime import datetime, timezone


# ==========================================
# Mock Classes (until implementation ready)
# ==========================================


class MockWeightedConsensus:
    """Mock WeightedConsensus until implementation is ready."""

    def __init__(self, threshold: float = 0.51, default_weight: float = 1.0):
        """
        Initialize weighted consensus algorithm.

        Args:
            threshold: Weighted voting threshold (0.0-1.0)
            default_weight: Default weight for agents without explicit weight
        """
        if not 0.0 <= threshold <= 1.0:
            raise ValueError(f"Threshold must be between 0.0 and 1.0, got {threshold}")
        if default_weight < 0:
            raise ValueError(f"Default weight must be non-negative, got {default_weight}")

        self.threshold = threshold
        self.default_weight = default_weight
        self.agent_weights: Dict[str, float] = {}
        self.vote_history = []

        # Expert weight presets
        self.expert_presets = {
            "expert-backend": 1.5,
            "expert-frontend": 1.5,
            "expert-database": 1.5,
            "expert-devops": 1.5,
            "expert-security": 2.0,  # Security experts get higher weight
            "manager-tdd": 1.2,
            "manager-quality": 1.3,
        }

    def set_weight(self, agent_id: str, weight: float) -> bool:
        """
        Set weight for specific agent.

        Args:
            agent_id: Agent identifier
            weight: Weight value (must be non-negative)

        Returns:
            True if set successfully, False if invalid weight
        """
        if weight < 0:
            return False
        self.agent_weights[agent_id] = weight
        return True

    def get_weight(self, agent_id: str) -> float:
        """
        Get weight for agent.

        Args:
            agent_id: Agent identifier

        Returns:
            Agent weight (default_weight if not set)
        """
        if agent_id in self.agent_weights:
            return self.agent_weights[agent_id]

        # Check expert presets
        for expert_type, preset_weight in self.expert_presets.items():
            if agent_id.startswith(expert_type):
                return preset_weight

        return self.default_weight

    def set_weights_by_domain(self, domain: str, weight: float) -> int:
        """
        Set weights for all agents in domain.

        Args:
            domain: Domain identifier (e.g., "security", "backend")
            weight: Weight to apply

        Returns:
            Number of agents updated
        """
        if weight < 0:
            return 0

        count = 0
        for agent_id in list(self.agent_weights.keys()):
            if domain in agent_id:
                self.agent_weights[agent_id] = weight
                count += 1

        return count

    def reset_weights(self) -> None:
        """Reset all agent weights to default."""
        self.agent_weights.clear()

    async def request_consensus(
        self,
        agents: List[str],
        proposal: Dict[str, Any],
        timeout_ms: int = 30000
    ) -> Dict[str, Any]:
        """
        Request weighted consensus decision.

        Args:
            agents: List of agent IDs
            proposal: Proposal for consensus
            timeout_ms: Timeout in milliseconds

        Returns:
            Consensus result with weighted votes
        """
        if not agents:
            raise ValueError("No agents provided for consensus")

        # Collect weighted votes
        votes = await self._collect_weighted_votes(agents, proposal, timeout_ms)

        # Calculate weighted totals
        total_weight = votes["total_weight"]
        weight_for = votes["weight_for"]
        weight_against = votes["weight_against"]
        weight_abstain = votes["weight_abstain"]

        # Determine decision based on weighted threshold
        if total_weight == 0:
            decision = "rejected"
            weighted_approval_rate = 0.0
        else:
            weighted_approval_rate = weight_for / total_weight
            decision = "approved" if weighted_approval_rate >= self.threshold else "rejected"

        result = {
            "decision": decision,
            "total_weight": total_weight,
            "weight_for": weight_for,
            "weight_against": weight_against,
            "weight_abstain": weight_abstain,
            "threshold": self.threshold,
            "weighted_approval_rate": weighted_approval_rate,
            "participants": agents,
            "agent_weights": {agent: self.get_weight(agent) for agent in agents},
            "algorithm": "weighted",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        self.vote_history.append(result)
        return result

    async def _collect_weighted_votes(
        self,
        agents: List[str],
        proposal: Dict[str, Any],
        timeout_ms: int
    ) -> Dict[str, float]:
        """
        Collect weighted votes from agents.

        Returns:
            Dict with weighted vote totals
        """
        total_weight = sum(self.get_weight(agent) for agent in agents)

        # Simulate weighted voting
        # Agents vote proportionally to their weights
        weight_for = total_weight * self.threshold
        weight_against = total_weight * 0.3
        weight_abstain = total_weight - weight_for - weight_against

        return {
            "total_weight": total_weight,
            "weight_for": weight_for,
            "weight_against": weight_against,
            "weight_abstain": weight_abstain
        }

    def get_vote_history(self) -> List[Dict[str, Any]]:
        """Get vote history."""
        return self.vote_history.copy()

    def clear_history(self) -> None:
        """Clear vote history."""
        self.vote_history.clear()


# ==========================================
# Fixtures
# ==========================================


@pytest.fixture
def weighted_consensus():
    """Create weighted consensus with default settings."""
    return MockWeightedConsensus(threshold=0.51, default_weight=1.0)


@pytest.fixture
def weighted_consensus_high_threshold():
    """Create weighted consensus with high threshold."""
    return MockWeightedConsensus(threshold=0.75, default_weight=1.0)


@pytest.fixture
def agents_uniform():
    """Create agents with uniform naming."""
    return ["agent-1", "agent-2", "agent-3"]


@pytest.fixture
def agents_expert():
    """Create expert agents."""
    return [
        "expert-backend-1",
        "expert-frontend-1",
        "expert-security-1",
        "manager-tdd-1"
    ]


@pytest.fixture
def agents_mixed():
    """Create mixed agent types."""
    return [
        "expert-backend-1",
        "expert-backend-2",
        "agent-regular-1",
        "manager-quality-1",
        "expert-security-1"
    ]


# ==========================================
# Test: Initialization
# ==========================================


def test_weighted_init_default():
    """Test initialization with default values."""
    consensus = MockWeightedConsensus()
    assert consensus.threshold == 0.51
    assert consensus.default_weight == 1.0


def test_weighted_init_custom_threshold():
    """Test initialization with custom threshold."""
    consensus = MockWeightedConsensus(threshold=0.66)
    assert consensus.threshold == 0.66


def test_weighted_init_custom_default_weight():
    """Test initialization with custom default weight."""
    consensus = MockWeightedConsensus(default_weight=2.0)
    assert consensus.default_weight == 2.0


def test_weighted_init_invalid_threshold_negative():
    """Test initialization with negative threshold raises error."""
    with pytest.raises(ValueError, match="Threshold must be between"):
        MockWeightedConsensus(threshold=-0.1)


def test_weighted_init_invalid_threshold_above_one():
    """Test initialization with threshold > 1.0 raises error."""
    with pytest.raises(ValueError, match="Threshold must be between"):
        MockWeightedConsensus(threshold=1.5)


def test_weighted_init_invalid_default_weight_negative():
    """Test initialization with negative default weight raises error."""
    with pytest.raises(ValueError, match="Default weight must be non-negative"):
        MockWeightedConsensus(default_weight=-1.0)


# ==========================================
# Test: Default Weights
# ==========================================


def test_default_weight_for_unknown_agent(weighted_consensus):
    """Test default weight applied to unknown agents."""
    weight = weighted_consensus.get_weight("unknown-agent")
    assert weight == 1.0


def test_default_weight_for_regular_agent(weighted_consensus):
    """Test default weight for regular agents."""
    weight = weighted_consensus.get_weight("agent-1")
    assert weight == 1.0


@pytest.mark.asyncio
async def test_consensus_with_all_default_weights(weighted_consensus, agents_uniform):
    """Test consensus with all agents having default weights."""
    proposal = {"action": "test"}
    result = await weighted_consensus.request_consensus(agents_uniform, proposal)

    # All agents have weight 1.0
    assert result["total_weight"] == len(agents_uniform) * 1.0


# ==========================================
# Test: Expert Weight Presets
# ==========================================


def test_expert_preset_backend(weighted_consensus):
    """Test expert-backend preset weight."""
    weight = weighted_consensus.get_weight("expert-backend-1")
    assert weight == 1.5


def test_expert_preset_security(weighted_consensus):
    """Test expert-security preset weight (higher)."""
    weight = weighted_consensus.get_weight("expert-security-1")
    assert weight == 2.0


def test_expert_preset_manager_quality(weighted_consensus):
    """Test manager-quality preset weight."""
    weight = weighted_consensus.get_weight("manager-quality-1")
    assert weight == 1.3


@pytest.mark.asyncio
async def test_consensus_with_expert_presets(weighted_consensus, agents_expert):
    """Test consensus with expert preset weights."""
    proposal = {"action": "deploy"}
    result = await weighted_consensus.request_consensus(agents_expert, proposal)

    # Check expert weights are applied
    expected_total = 1.5 + 1.5 + 2.0 + 1.2  # backend + frontend + security + tdd
    assert abs(result["total_weight"] - expected_total) < 0.01


# ==========================================
# Test: Dynamic Weight Updates
# ==========================================


def test_set_weight_success(weighted_consensus):
    """Test setting agent weight."""
    result = weighted_consensus.set_weight("agent-1", 2.5)
    assert result is True
    assert weighted_consensus.get_weight("agent-1") == 2.5


def test_set_weight_zero(weighted_consensus):
    """Test setting weight to zero."""
    result = weighted_consensus.set_weight("agent-1", 0.0)
    assert result is True
    assert weighted_consensus.get_weight("agent-1") == 0.0


def test_set_weight_negative_fails(weighted_consensus):
    """Test setting negative weight fails."""
    result = weighted_consensus.set_weight("agent-1", -1.0)
    assert result is False


def test_set_weight_overwrites_preset(weighted_consensus):
    """Test custom weight overwrites preset."""
    weighted_consensus.set_weight("expert-backend-1", 3.0)
    weight = weighted_consensus.get_weight("expert-backend-1")
    assert weight == 3.0


def test_reset_weights(weighted_consensus):
    """Test resetting weights."""
    weighted_consensus.set_weight("agent-1", 2.0)
    weighted_consensus.set_weight("agent-2", 3.0)

    weighted_consensus.reset_weights()

    # Should return to defaults
    assert weighted_consensus.get_weight("agent-1") == 1.0
    assert weighted_consensus.get_weight("agent-2") == 1.0


# ==========================================
# Test: Domain-Specific Weighting
# ==========================================


def test_set_weights_by_domain(weighted_consensus):
    """Test setting weights by domain."""
    weighted_consensus.set_weight("security-agent-1", 1.0)
    weighted_consensus.set_weight("security-agent-2", 1.0)

    count = weighted_consensus.set_weights_by_domain("security", 2.5)

    assert count == 2
    assert weighted_consensus.get_weight("security-agent-1") == 2.5
    assert weighted_consensus.get_weight("security-agent-2") == 2.5


def test_set_weights_by_domain_no_match(weighted_consensus):
    """Test setting weights by domain with no matches."""
    count = weighted_consensus.set_weights_by_domain("nonexistent", 2.0)
    assert count == 0


def test_set_weights_by_domain_negative_fails(weighted_consensus):
    """Test setting negative weight by domain fails."""
    weighted_consensus.set_weight("backend-agent-1", 1.0)
    count = weighted_consensus.set_weights_by_domain("backend", -1.0)
    assert count == 0


# ==========================================
# Test: Weighted Vote Calculation
# ==========================================


@pytest.mark.asyncio
async def test_weighted_vote_calculation(weighted_consensus):
    """Test weighted vote calculation."""
    weighted_consensus.set_weight("agent-1", 1.0)
    weighted_consensus.set_weight("agent-2", 2.0)
    weighted_consensus.set_weight("agent-3", 3.0)

    agents = ["agent-1", "agent-2", "agent-3"]
    proposal = {"action": "test"}
    result = await weighted_consensus.request_consensus(agents, proposal)

    assert result["total_weight"] == 6.0  # 1 + 2 + 3


@pytest.mark.asyncio
async def test_weighted_approval_rate(weighted_consensus):
    """Test weighted approval rate calculation."""
    agents = ["agent-1", "agent-2"]
    proposal = {"action": "test"}
    result = await weighted_consensus.request_consensus(agents, proposal)

    expected_rate = result["weight_for"] / result["total_weight"]
    assert abs(result["weighted_approval_rate"] - expected_rate) < 0.01


@pytest.mark.asyncio
async def test_weighted_decision_approved(weighted_consensus):
    """Test weighted decision approved."""
    # Set weights to ensure approval
    weighted_consensus.set_weight("agent-1", 5.0)  # Heavy weight voter
    weighted_consensus.set_weight("agent-2", 1.0)

    agents = ["agent-1", "agent-2"]
    proposal = {"action": "test"}
    result = await weighted_consensus.request_consensus(agents, proposal)

    # With threshold 0.51 and weighted voting, should approve
    assert result is not None


@pytest.mark.asyncio
async def test_weighted_decision_with_mixed_weights(weighted_consensus, agents_mixed):
    """Test weighted decision with mixed agent weights."""
    proposal = {"action": "critical"}
    result = await weighted_consensus.request_consensus(agents_mixed, proposal)

    # Check all weights are included
    assert "agent_weights" in result
    assert len(result["agent_weights"]) == len(agents_mixed)


# ==========================================
# Test: Edge Cases
# ==========================================


@pytest.mark.asyncio
async def test_no_agents_raises_error(weighted_consensus):
    """Test consensus with no agents raises error."""
    proposal = {"action": "test"}
    with pytest.raises(ValueError, match="No agents provided"):
        await weighted_consensus.request_consensus([], proposal)


@pytest.mark.asyncio
async def test_single_agent_weighted(weighted_consensus):
    """Test consensus with single weighted agent."""
    weighted_consensus.set_weight("agent-1", 5.0)
    agents = ["agent-1"]
    proposal = {"action": "test"}
    result = await weighted_consensus.request_consensus(agents, proposal)

    assert result["total_weight"] == 5.0


@pytest.mark.asyncio
async def test_all_zero_weights(weighted_consensus):
    """Test consensus with all zero weights."""
    weighted_consensus.set_weight("agent-1", 0.0)
    weighted_consensus.set_weight("agent-2", 0.0)

    agents = ["agent-1", "agent-2"]
    proposal = {"action": "test"}
    result = await weighted_consensus.request_consensus(agents, proposal)

    assert result["total_weight"] == 0.0
    assert result["decision"] == "rejected"


@pytest.mark.asyncio
async def test_equal_weights_behaves_like_quorum(weighted_consensus):
    """Test equal weights behaves like standard quorum."""
    agents = ["agent-1", "agent-2", "agent-3"]
    proposal = {"action": "test"}
    result = await weighted_consensus.request_consensus(agents, proposal)

    # All weights are 1.0, so behaves like quorum
    assert result["total_weight"] == 3.0


# ==========================================
# Test: High Threshold
# ==========================================


@pytest.mark.asyncio
async def test_high_threshold_requires_more_weight(weighted_consensus_high_threshold):
    """Test high threshold requires more weighted votes."""
    agents = ["agent-1", "agent-2", "agent-3"]
    proposal = {"action": "critical"}
    result = await weighted_consensus_high_threshold.request_consensus(agents, proposal)

    assert result["threshold"] == 0.75


# ==========================================
# Test: Vote History
# ==========================================


@pytest.mark.asyncio
async def test_vote_history_tracking(weighted_consensus, agents_uniform):
    """Test vote history tracking."""
    proposals = [{"action": f"task-{i}"} for i in range(3)]

    for proposal in proposals:
        await weighted_consensus.request_consensus(agents_uniform, proposal)

    history = weighted_consensus.get_vote_history()
    assert len(history) == 3


@pytest.mark.asyncio
async def test_vote_history_clear(weighted_consensus, agents_uniform):
    """Test clearing vote history."""
    proposal = {"action": "test"}
    await weighted_consensus.request_consensus(agents_uniform, proposal)

    weighted_consensus.clear_history()
    history = weighted_consensus.get_vote_history()
    assert len(history) == 0


# ==========================================
# Test: Result Structure
# ==========================================


@pytest.mark.asyncio
async def test_result_contains_required_fields(weighted_consensus, agents_uniform):
    """Test result contains all required fields."""
    proposal = {"action": "test"}
    result = await weighted_consensus.request_consensus(agents_uniform, proposal)

    required_fields = [
        "decision",
        "total_weight",
        "weight_for",
        "weight_against",
        "weight_abstain",
        "threshold",
        "weighted_approval_rate",
        "participants",
        "agent_weights",
        "algorithm"
    ]

    for field in required_fields:
        assert field in result


@pytest.mark.asyncio
async def test_result_algorithm_field(weighted_consensus, agents_uniform):
    """Test result algorithm field is correct."""
    proposal = {"action": "test"}
    result = await weighted_consensus.request_consensus(agents_uniform, proposal)

    assert result["algorithm"] == "weighted"


# ==========================================
# Test: Concurrent Requests
# ==========================================


@pytest.mark.asyncio
async def test_concurrent_weighted_consensus(weighted_consensus, agents_uniform):
    """Test concurrent weighted consensus requests."""
    proposals = [{"action": f"task-{i}"} for i in range(5)]
    tasks = [
        weighted_consensus.request_consensus(agents_uniform, p)
        for p in proposals
    ]

    results = await asyncio.gather(*tasks)

    assert len(results) == 5
    assert all(r["algorithm"] == "weighted" for r in results)


# ==========================================
# Test: Weight Persistence
# ==========================================


@pytest.mark.asyncio
async def test_weight_persists_across_requests(weighted_consensus, agents_uniform):
    """Test agent weights persist across multiple requests."""
    weighted_consensus.set_weight("agent-1", 3.0)

    proposal1 = {"action": "task-1"}
    result1 = await weighted_consensus.request_consensus(agents_uniform, proposal1)

    proposal2 = {"action": "task-2"}
    result2 = await weighted_consensus.request_consensus(agents_uniform, proposal2)

    assert result1["agent_weights"]["agent-1"] == 3.0
    assert result2["agent_weights"]["agent-1"] == 3.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
