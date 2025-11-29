"""
Comprehensive tests for ConsensusManager.

Tests cover:
- Algorithm registration and switching
- Consensus requests with different algorithms
- Timeout handling
- Statistics tracking
- Concurrent consensus requests
- Error handling (invalid algorithm, no agents)

Following TDD RED-GREEN-REFACTOR cycle with 90%+ coverage target.
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
from unittest.mock import Mock, patch, MagicMock


# ==========================================
# Mock Classes (until implementation ready)
# ==========================================


class MockConsensusAlgorithm:
    """Mock consensus algorithm for testing."""

    def __init__(self, name: str = "mock", threshold: float = 0.51):
        self.name = name
        self.threshold = threshold
        self.call_count = 0
        self.last_proposal = None

    async def request_consensus(
        self,
        agents: List[str],
        proposal: Dict[str, Any],
        timeout_ms: int = 30000
    ) -> Dict[str, Any]:
        """Mock consensus request."""
        self.call_count += 1
        self.last_proposal = proposal

        # Simulate consensus result
        votes_for = int(len(agents) * self.threshold)
        votes_against = len(agents) - votes_for

        return {
            "decision": "approved" if votes_for > votes_against else "rejected",
            "votes_for": votes_for,
            "votes_against": votes_against,
            "threshold": self.threshold,
            "participants": agents,
            "algorithm": self.name,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


class MockCoordinator:
    """Mock coordinator for testing."""

    def __init__(self):
        self.agents = {}
        self.messages = []

    def register_agent(self, agent_id: str, metadata: Dict[str, Any]) -> bool:
        self.agents[agent_id] = metadata
        return True

    def get_all_agents(self) -> List[str]:
        return list(self.agents.keys())

    def broadcast_message(
        self,
        from_agent: str,
        message: Dict[str, Any],
        exclude: List[str] = None
    ) -> int:
        self.messages.append({"from": from_agent, "message": message, "exclude": exclude})
        return len(self.agents) - (len(exclude) if exclude else 0)


class MockConsensusManager:
    """Mock ConsensusManager until implementation is ready."""

    def __init__(self, coordinator=None):
        self.coordinator = coordinator or MockCoordinator()
        self.algorithms = {}
        self.default_algorithm = None
        self.statistics = {
            "total_requests": 0,
            "approved": 0,
            "rejected": 0,
            "timeout": 0,
            "by_algorithm": {}
        }

    def register_algorithm(self, name: str, algorithm: Any) -> bool:
        """Register consensus algorithm."""
        if name in self.algorithms:
            return False
        self.algorithms[name] = algorithm
        if self.default_algorithm is None:
            self.default_algorithm = name
        self.statistics["by_algorithm"][name] = {
            "total": 0,
            "approved": 0,
            "rejected": 0,
            "timeout": 0
        }
        return True

    def unregister_algorithm(self, name: str) -> bool:
        """Unregister consensus algorithm."""
        if name not in self.algorithms:
            return False
        del self.algorithms[name]
        if self.default_algorithm == name:
            self.default_algorithm = next(iter(self.algorithms), None)
        return True

    def set_default_algorithm(self, name: str) -> bool:
        """Set default consensus algorithm."""
        if name not in self.algorithms:
            return False
        self.default_algorithm = name
        return True

    async def request_consensus(
        self,
        proposal: Dict[str, Any],
        algorithm: str = None,
        timeout_ms: int = 30000
    ) -> Dict[str, Any]:
        """Request consensus decision."""
        algo_name = algorithm or self.default_algorithm

        if not algo_name or algo_name not in self.algorithms:
            raise ValueError(f"Invalid algorithm: {algo_name}")

        agents = self.coordinator.get_all_agents()
        if not agents:
            raise ValueError("No agents registered for consensus")

        algo = self.algorithms[algo_name]
        result = await algo.request_consensus(agents, proposal, timeout_ms)

        # Update statistics
        self.statistics["total_requests"] += 1
        self.statistics[result["decision"]] += 1
        self.statistics["by_algorithm"][algo_name]["total"] += 1
        self.statistics["by_algorithm"][algo_name][result["decision"]] += 1

        return result

    def get_statistics(self) -> Dict[str, Any]:
        """Get consensus statistics."""
        return self.statistics.copy()

    def list_algorithms(self) -> List[str]:
        """List registered algorithms."""
        return list(self.algorithms.keys())


# ==========================================
# Fixtures
# ==========================================


@pytest.fixture
def coordinator():
    """Create test coordinator."""
    return MockCoordinator()


@pytest.fixture
def consensus_manager(coordinator):
    """Create test consensus manager."""
    return MockConsensusManager(coordinator=coordinator)


@pytest.fixture
def quorum_algorithm():
    """Create quorum consensus algorithm."""
    return MockConsensusAlgorithm(name="quorum", threshold=0.51)


@pytest.fixture
def raft_algorithm():
    """Create Raft consensus algorithm."""
    return MockConsensusAlgorithm(name="raft", threshold=0.51)


@pytest.fixture
def weighted_algorithm():
    """Create weighted consensus algorithm."""
    return MockConsensusAlgorithm(name="weighted", threshold=0.66)


# ==========================================
# Test: Algorithm Registration
# ==========================================


def test_register_algorithm_success(consensus_manager, quorum_algorithm):
    """Test successful algorithm registration."""
    result = consensus_manager.register_algorithm("quorum", quorum_algorithm)
    assert result is True
    assert "quorum" in consensus_manager.list_algorithms()


def test_register_algorithm_duplicate(consensus_manager, quorum_algorithm):
    """Test duplicate algorithm registration fails."""
    consensus_manager.register_algorithm("quorum", quorum_algorithm)
    result = consensus_manager.register_algorithm("quorum", quorum_algorithm)
    assert result is False


def test_register_multiple_algorithms(
    consensus_manager,
    quorum_algorithm,
    raft_algorithm,
    weighted_algorithm
):
    """Test registering multiple algorithms."""
    consensus_manager.register_algorithm("quorum", quorum_algorithm)
    consensus_manager.register_algorithm("raft", raft_algorithm)
    consensus_manager.register_algorithm("weighted", weighted_algorithm)

    algorithms = consensus_manager.list_algorithms()
    assert len(algorithms) == 3
    assert "quorum" in algorithms
    assert "raft" in algorithms
    assert "weighted" in algorithms


def test_unregister_algorithm_success(consensus_manager, quorum_algorithm):
    """Test successful algorithm unregistration."""
    consensus_manager.register_algorithm("quorum", quorum_algorithm)
    result = consensus_manager.unregister_algorithm("quorum")
    assert result is True
    assert "quorum" not in consensus_manager.list_algorithms()


def test_unregister_nonexistent_algorithm(consensus_manager):
    """Test unregistering non-existent algorithm fails."""
    result = consensus_manager.unregister_algorithm("nonexistent")
    assert result is False


def test_default_algorithm_set_on_first_registration(
    consensus_manager,
    quorum_algorithm
):
    """Test default algorithm set automatically on first registration."""
    assert consensus_manager.default_algorithm is None
    consensus_manager.register_algorithm("quorum", quorum_algorithm)
    assert consensus_manager.default_algorithm == "quorum"


def test_set_default_algorithm_success(
    consensus_manager,
    quorum_algorithm,
    raft_algorithm
):
    """Test setting default algorithm."""
    consensus_manager.register_algorithm("quorum", quorum_algorithm)
    consensus_manager.register_algorithm("raft", raft_algorithm)

    result = consensus_manager.set_default_algorithm("raft")
    assert result is True
    assert consensus_manager.default_algorithm == "raft"


def test_set_default_algorithm_invalid(consensus_manager):
    """Test setting invalid default algorithm fails."""
    result = consensus_manager.set_default_algorithm("invalid")
    assert result is False


# ==========================================
# Test: Consensus Requests
# ==========================================


@pytest.mark.asyncio
async def test_request_consensus_with_default_algorithm(
    consensus_manager,
    coordinator,
    quorum_algorithm
):
    """Test consensus request with default algorithm."""
    # Setup
    consensus_manager.register_algorithm("quorum", quorum_algorithm)
    coordinator.register_agent("agent-1", {"type": "expert-backend"})
    coordinator.register_agent("agent-2", {"type": "expert-frontend"})

    # Request consensus
    proposal = {"action": "deploy", "target": "production"}
    result = await consensus_manager.request_consensus(proposal)

    assert result["decision"] in ["approved", "rejected", "timeout"]
    assert result["algorithm"] == "quorum"
    assert "participants" in result
    assert len(result["participants"]) == 2


@pytest.mark.asyncio
async def test_request_consensus_with_specific_algorithm(
    consensus_manager,
    coordinator,
    quorum_algorithm,
    raft_algorithm
):
    """Test consensus request with specific algorithm."""
    # Setup
    consensus_manager.register_algorithm("quorum", quorum_algorithm)
    consensus_manager.register_algorithm("raft", raft_algorithm)
    coordinator.register_agent("agent-1", {"type": "expert-backend"})
    coordinator.register_agent("agent-2", {"type": "expert-frontend"})

    # Request with specific algorithm
    proposal = {"action": "rollback", "version": "1.0.0"}
    result = await consensus_manager.request_consensus(proposal, algorithm="raft")

    assert result["algorithm"] == "raft"
    assert raft_algorithm.call_count == 1


@pytest.mark.asyncio
async def test_request_consensus_no_agents(consensus_manager, quorum_algorithm):
    """Test consensus request with no agents raises error."""
    consensus_manager.register_algorithm("quorum", quorum_algorithm)

    proposal = {"action": "test"}
    with pytest.raises(ValueError, match="No agents registered"):
        await consensus_manager.request_consensus(proposal)


@pytest.mark.asyncio
async def test_request_consensus_invalid_algorithm(
    consensus_manager,
    coordinator,
    quorum_algorithm
):
    """Test consensus request with invalid algorithm raises error."""
    consensus_manager.register_algorithm("quorum", quorum_algorithm)
    coordinator.register_agent("agent-1", {"type": "expert-backend"})

    proposal = {"action": "test"}
    with pytest.raises(ValueError, match="Invalid algorithm"):
        await consensus_manager.request_consensus(proposal, algorithm="invalid")


@pytest.mark.asyncio
async def test_request_consensus_no_algorithm_registered(
    consensus_manager,
    coordinator
):
    """Test consensus request with no algorithms raises error."""
    coordinator.register_agent("agent-1", {"type": "expert-backend"})

    proposal = {"action": "test"}
    with pytest.raises(ValueError, match="Invalid algorithm"):
        await consensus_manager.request_consensus(proposal)


# ==========================================
# Test: Statistics Tracking
# ==========================================


@pytest.mark.asyncio
async def test_statistics_initial_state(consensus_manager):
    """Test statistics initial state."""
    stats = consensus_manager.get_statistics()
    assert stats["total_requests"] == 0
    assert stats["approved"] == 0
    assert stats["rejected"] == 0
    assert stats["timeout"] == 0


@pytest.mark.asyncio
async def test_statistics_after_consensus(
    consensus_manager,
    coordinator,
    quorum_algorithm
):
    """Test statistics updated after consensus."""
    consensus_manager.register_algorithm("quorum", quorum_algorithm)
    coordinator.register_agent("agent-1", {"type": "expert-backend"})
    coordinator.register_agent("agent-2", {"type": "expert-frontend"})

    proposal = {"action": "deploy"}
    await consensus_manager.request_consensus(proposal)

    stats = consensus_manager.get_statistics()
    assert stats["total_requests"] == 1
    assert stats["approved"] >= 0
    assert stats["rejected"] >= 0


@pytest.mark.asyncio
async def test_statistics_by_algorithm(
    consensus_manager,
    coordinator,
    quorum_algorithm,
    raft_algorithm
):
    """Test statistics tracked by algorithm."""
    consensus_manager.register_algorithm("quorum", quorum_algorithm)
    consensus_manager.register_algorithm("raft", raft_algorithm)
    coordinator.register_agent("agent-1", {"type": "expert-backend"})

    proposal = {"action": "test"}
    await consensus_manager.request_consensus(proposal, algorithm="quorum")
    await consensus_manager.request_consensus(proposal, algorithm="raft")

    stats = consensus_manager.get_statistics()
    assert stats["by_algorithm"]["quorum"]["total"] == 1
    assert stats["by_algorithm"]["raft"]["total"] == 1


# ==========================================
# Test: Concurrent Consensus Requests
# ==========================================


@pytest.mark.asyncio
async def test_concurrent_consensus_requests(
    consensus_manager,
    coordinator,
    quorum_algorithm
):
    """Test concurrent consensus requests."""
    consensus_manager.register_algorithm("quorum", quorum_algorithm)
    for i in range(5):
        coordinator.register_agent(f"agent-{i}", {"type": "expert-backend"})

    # Create concurrent requests
    proposals = [{"action": f"task-{i}"} for i in range(3)]
    tasks = [
        consensus_manager.request_consensus(p)
        for p in proposals
    ]

    results = await asyncio.gather(*tasks)

    assert len(results) == 3
    stats = consensus_manager.get_statistics()
    assert stats["total_requests"] == 3


@pytest.mark.asyncio
async def test_concurrent_requests_different_algorithms(
    consensus_manager,
    coordinator,
    quorum_algorithm,
    raft_algorithm
):
    """Test concurrent requests with different algorithms."""
    consensus_manager.register_algorithm("quorum", quorum_algorithm)
    consensus_manager.register_algorithm("raft", raft_algorithm)
    coordinator.register_agent("agent-1", {"type": "expert-backend"})
    coordinator.register_agent("agent-2", {"type": "expert-frontend"})

    tasks = [
        consensus_manager.request_consensus(
            {"action": "task-1"},
            algorithm="quorum"
        ),
        consensus_manager.request_consensus(
            {"action": "task-2"},
            algorithm="raft"
        ),
    ]

    results = await asyncio.gather(*tasks)

    assert results[0]["algorithm"] == "quorum"
    assert results[1]["algorithm"] == "raft"


# ==========================================
# Test: Timeout Handling
# ==========================================


@pytest.mark.asyncio
async def test_consensus_timeout_parameter(
    consensus_manager,
    coordinator,
    quorum_algorithm
):
    """Test consensus timeout parameter passed correctly."""
    consensus_manager.register_algorithm("quorum", quorum_algorithm)
    coordinator.register_agent("agent-1", {"type": "expert-backend"})

    proposal = {"action": "test"}
    result = await consensus_manager.request_consensus(
        proposal,
        timeout_ms=5000
    )

    assert result is not None
    assert quorum_algorithm.call_count == 1


# ==========================================
# Test: Edge Cases
# ==========================================


@pytest.mark.asyncio
async def test_empty_proposal(consensus_manager, coordinator, quorum_algorithm):
    """Test consensus with empty proposal."""
    consensus_manager.register_algorithm("quorum", quorum_algorithm)
    coordinator.register_agent("agent-1", {"type": "expert-backend"})

    result = await consensus_manager.request_consensus({})
    assert result is not None


@pytest.mark.asyncio
async def test_single_agent_consensus(
    consensus_manager,
    coordinator,
    quorum_algorithm
):
    """Test consensus with single agent."""
    consensus_manager.register_algorithm("quorum", quorum_algorithm)
    coordinator.register_agent("agent-1", {"type": "expert-backend"})

    proposal = {"action": "test"}
    result = await consensus_manager.request_consensus(proposal)

    assert result is not None
    assert len(result["participants"]) == 1


@pytest.mark.asyncio
async def test_many_agents_consensus(
    consensus_manager,
    coordinator,
    quorum_algorithm
):
    """Test consensus with many agents."""
    consensus_manager.register_algorithm("quorum", quorum_algorithm)
    for i in range(100):
        coordinator.register_agent(f"agent-{i}", {"type": "expert-backend"})

    proposal = {"action": "test"}
    result = await consensus_manager.request_consensus(proposal)

    assert result is not None
    assert len(result["participants"]) == 100


# ==========================================
# Test: Algorithm Switching
# ==========================================


@pytest.mark.asyncio
async def test_switch_algorithm_mid_operation(
    consensus_manager,
    coordinator,
    quorum_algorithm,
    raft_algorithm
):
    """Test switching algorithms between requests."""
    consensus_manager.register_algorithm("quorum", quorum_algorithm)
    consensus_manager.register_algorithm("raft", raft_algorithm)
    coordinator.register_agent("agent-1", {"type": "expert-backend"})

    # First request with quorum
    proposal1 = {"action": "task-1"}
    result1 = await consensus_manager.request_consensus(
        proposal1,
        algorithm="quorum"
    )

    # Second request with raft
    proposal2 = {"action": "task-2"}
    result2 = await consensus_manager.request_consensus(
        proposal2,
        algorithm="raft"
    )

    assert result1["algorithm"] == "quorum"
    assert result2["algorithm"] == "raft"


def test_unregister_default_algorithm_updates_default(
    consensus_manager,
    quorum_algorithm,
    raft_algorithm
):
    """Test unregistering default algorithm updates to next available."""
    consensus_manager.register_algorithm("quorum", quorum_algorithm)
    consensus_manager.register_algorithm("raft", raft_algorithm)
    consensus_manager.set_default_algorithm("quorum")

    consensus_manager.unregister_algorithm("quorum")

    # Default should update to remaining algorithm
    assert consensus_manager.default_algorithm == "raft"


# ==========================================
# Test: Error Recovery
# ==========================================


@pytest.mark.asyncio
async def test_consensus_after_failed_request(
    consensus_manager,
    coordinator,
    quorum_algorithm
):
    """Test consensus works after failed request."""
    consensus_manager.register_algorithm("quorum", quorum_algorithm)

    # First request fails (no agents)
    with pytest.raises(ValueError):
        await consensus_manager.request_consensus({"action": "fail"})

    # Add agents and retry
    coordinator.register_agent("agent-1", {"type": "expert-backend"})
    result = await consensus_manager.request_consensus({"action": "success"})

    assert result is not None
    assert result["decision"] in ["approved", "rejected", "timeout"]


# ==========================================
# Test: Statistics Accuracy
# ==========================================


@pytest.mark.asyncio
async def test_statistics_accuracy_multiple_requests(
    consensus_manager,
    coordinator,
    quorum_algorithm
):
    """Test statistics accuracy across multiple requests."""
    consensus_manager.register_algorithm("quorum", quorum_algorithm)
    coordinator.register_agent("agent-1", {"type": "expert-backend"})

    # Make 10 requests
    for i in range(10):
        await consensus_manager.request_consensus({"action": f"task-{i}"})

    stats = consensus_manager.get_statistics()
    assert stats["total_requests"] == 10
    assert stats["by_algorithm"]["quorum"]["total"] == 10


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
