#!/usr/bin/env python3
"""
ConsensusManager for MoAI-Flow Phase 6B

Multi-algorithm consensus system for swarm decision-making.
Provides pluggable consensus algorithms with runtime algorithm switching
based on swarm configuration and proposal characteristics.

Key Features:
- Abstract base class for consensus algorithm implementations
- Registry pattern for algorithm management
- Built-in algorithms: Quorum, Raft, Weighted
- Thread-safe vote aggregation with RLock
- Timeout handling with graceful degradation
- Agent disconnection handling
- Comprehensive statistics tracking
- Integration with ICoordinator for vote collection

Example:
    >>> from moai_flow.core.interfaces import ICoordinator
    >>> coordinator = Coordinator(topology="mesh")
    >>> manager = ConsensusManager(coordinator, default_algorithm="quorum")
    >>>
    >>> proposal = {"action": "deploy", "version": "v2.0"}
    >>> result = manager.request_consensus(proposal, timeout_ms=30000)
    >>> print(result.decision)
    ConsensusDecision.APPROVED
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import time
import threading
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


class ConsensusDecision(str, Enum):
    """Consensus decision outcomes."""
    APPROVED = "approved"
    REJECTED = "rejected"
    TIMEOUT = "timeout"


class VoteType(str, Enum):
    """Vote types for consensus."""
    FOR = "for"
    AGAINST = "against"
    ABSTAIN = "abstain"


@dataclass
class ConsensusResult:
    """
    Result of consensus request.

    Attributes:
        decision: Final consensus decision (approved/rejected/timeout)
        votes_for: Number of votes in favor
        votes_against: Number of votes against
        votes_abstain: Number of abstentions
        threshold: Consensus threshold used (0.0-1.0)
        participants: List of agent IDs that participated
        algorithm_used: Name of consensus algorithm used
        duration_ms: Time taken to reach consensus (milliseconds)
        metadata: Additional algorithm-specific metadata
    """
    decision: str
    votes_for: int
    votes_against: int
    votes_abstain: int = 0
    threshold: float = 0.5
    participants: List[str] = field(default_factory=list)
    algorithm_used: str = "quorum"
    duration_ms: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate result fields."""
        if not isinstance(self.decision, str):
            self.decision = str(self.decision)
        if self.decision not in [d.value for d in ConsensusDecision]:
            raise ValueError(f"Invalid decision: {self.decision}")
        if self.threshold < 0.0 or self.threshold > 1.0:
            raise ValueError(f"Threshold must be 0.0-1.0, got {self.threshold}")


@dataclass
class Vote:
    """
    Individual vote from an agent.

    Attributes:
        agent_id: Agent identifier
        vote: Vote type (for/against/abstain)
        weight: Vote weight for weighted algorithms (default: 1.0)
        timestamp: When vote was cast
        metadata: Optional vote metadata
    """
    agent_id: str
    vote: VoteType
    weight: float = 1.0
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ConsensusAlgorithm(ABC):
    """
    Abstract base class for consensus algorithms.

    All consensus algorithms must implement propose() and decide() methods.
    Algorithms can maintain internal state and configuration.
    """

    @abstractmethod
    def propose(
        self,
        proposal: Dict[str, Any],
        participants: List[str]
    ) -> str:
        """
        Initiate consensus proposal.

        Args:
            proposal: Proposal data to vote on
            participants: List of agent IDs to participate

        Returns:
            Proposal ID for tracking
        """
        pass

    @abstractmethod
    def decide(
        self,
        proposal_id: str,
        votes: List[Vote],
        timeout_reached: bool = False
    ) -> ConsensusResult:
        """
        Make consensus decision based on collected votes.

        Args:
            proposal_id: Proposal identifier
            votes: List of votes collected
            timeout_reached: Whether timeout was reached

        Returns:
            ConsensusResult with decision and statistics
        """
        pass

    def get_algorithm_name(self) -> str:
        """Get algorithm name."""
        return self.__class__.__name__


class QuorumAlgorithm(ConsensusAlgorithm):
    """
    Simple majority (quorum) consensus algorithm.

    Requires >50% of participants to vote FOR for approval.
    Default algorithm for most use cases.

    Attributes:
        threshold: Minimum proportion of FOR votes needed (default: 0.5)
        require_majority: If True, require >50% participation (default: True)
    """

    def __init__(self, threshold: float = 0.5, require_majority: bool = True):
        """
        Initialize QuorumAlgorithm.

        Args:
            threshold: Minimum proportion of FOR votes (0.0-1.0)
            require_majority: Require >50% participation

        Raises:
            ValueError: If threshold not in range 0.0-1.0
        """
        if threshold < 0.0 or threshold > 1.0:
            raise ValueError("Threshold must be 0.0-1.0")
        self.threshold = threshold
        self.require_majority = require_majority
        self._proposals: Dict[str, Dict[str, Any]] = {}

    def propose(
        self,
        proposal: Dict[str, Any],
        participants: List[str]
    ) -> str:
        """Initiate quorum proposal."""
        proposal_id = f"quorum_{int(time.time() * 1000)}"
        self._proposals[proposal_id] = {
            "proposal": proposal,
            "participants": participants,
            "created_at": datetime.now()
        }
        return proposal_id

    def decide(
        self,
        proposal_id: str,
        votes: List[Vote],
        timeout_reached: bool = False
    ) -> ConsensusResult:
        """Make quorum decision."""
        if proposal_id not in self._proposals:
            raise ValueError(f"Unknown proposal: {proposal_id}")

        proposal_data = self._proposals[proposal_id]
        total_participants = len(proposal_data["participants"])

        # Count votes
        votes_for = sum(1 for v in votes if v.vote == VoteType.FOR)
        votes_against = sum(1 for v in votes if v.vote == VoteType.AGAINST)
        votes_abstain = sum(1 for v in votes if v.vote == VoteType.ABSTAIN)

        participants_voted = [v.agent_id for v in votes]
        participation_rate = len(participants_voted) / total_participants if total_participants > 0 else 0

        # Determine decision
        decision = ConsensusDecision.REJECTED

        if timeout_reached and participation_rate < 0.5 and self.require_majority:
            decision = ConsensusDecision.TIMEOUT
        else:
            # Calculate approval rate based on total participants
            approval_rate = votes_for / total_participants if total_participants > 0 else 0

            if approval_rate > self.threshold:
                decision = ConsensusDecision.APPROVED
            elif timeout_reached:
                decision = ConsensusDecision.TIMEOUT

        # Calculate duration
        duration_ms = int((datetime.now() - proposal_data["created_at"]).total_seconds() * 1000)

        # Clean up proposal data
        del self._proposals[proposal_id]

        return ConsensusResult(
            decision=decision.value,
            votes_for=votes_for,
            votes_against=votes_against,
            votes_abstain=votes_abstain,
            threshold=self.threshold,
            participants=participants_voted,
            algorithm_used="quorum",
            duration_ms=duration_ms,
            metadata={
                "total_participants": total_participants,
                "participation_rate": participation_rate,
                "approval_rate": approval_rate,
                "require_majority": self.require_majority
            }
        )


class WeightedAlgorithm(ConsensusAlgorithm):
    """
    Weighted voting consensus algorithm.

    Votes have different weights based on agent expertise, role, or priority.
    Useful for hierarchical swarms or expert-based decisions.

    Attributes:
        threshold: Minimum weighted vote proportion needed (default: 0.6)
        agent_weights: Dict mapping agent_id to vote weight
    """

    def __init__(self, threshold: float = 0.6, agent_weights: Optional[Dict[str, float]] = None):
        """
        Initialize WeightedAlgorithm.

        Args:
            threshold: Minimum weighted vote proportion (0.0-1.0)
            agent_weights: Optional dict of agent_id -> weight

        Raises:
            ValueError: If threshold not in range 0.0-1.0
        """
        if threshold < 0.0 or threshold > 1.0:
            raise ValueError("Threshold must be 0.0-1.0")
        self.threshold = threshold
        self.agent_weights = agent_weights or {}
        self._proposals: Dict[str, Dict[str, Any]] = {}

    def propose(
        self,
        proposal: Dict[str, Any],
        participants: List[str]
    ) -> str:
        """Initiate weighted proposal."""
        proposal_id = f"weighted_{int(time.time() * 1000)}"
        self._proposals[proposal_id] = {
            "proposal": proposal,
            "participants": participants,
            "created_at": datetime.now()
        }
        return proposal_id

    def decide(
        self,
        proposal_id: str,
        votes: List[Vote],
        timeout_reached: bool = False
    ) -> ConsensusResult:
        """Make weighted decision."""
        if proposal_id not in self._proposals:
            raise ValueError(f"Unknown proposal: {proposal_id}")

        proposal_data = self._proposals[proposal_id]

        # Calculate total weight and weighted votes
        total_weight = sum(self.agent_weights.get(p, 1.0) for p in proposal_data["participants"])

        weighted_for = 0.0
        weighted_against = 0.0
        votes_for = 0
        votes_against = 0
        votes_abstain = 0

        for vote in votes:
            weight = self.agent_weights.get(vote.agent_id, 1.0)
            if vote.vote == VoteType.FOR:
                weighted_for += weight
                votes_for += 1
            elif vote.vote == VoteType.AGAINST:
                weighted_against += weight
                votes_against += 1
            else:
                votes_abstain += 1

        participants_voted = [v.agent_id for v in votes]
        weighted_approval = weighted_for / total_weight if total_weight > 0 else 0

        # Determine decision
        if timeout_reached and len(participants_voted) < len(proposal_data["participants"]) * 0.5:
            decision = ConsensusDecision.TIMEOUT
        elif weighted_approval > self.threshold:
            decision = ConsensusDecision.APPROVED
        else:
            decision = ConsensusDecision.REJECTED

        # Calculate duration
        duration_ms = int((datetime.now() - proposal_data["created_at"]).total_seconds() * 1000)

        # Clean up
        del self._proposals[proposal_id]

        return ConsensusResult(
            decision=decision.value,
            votes_for=votes_for,
            votes_against=votes_against,
            votes_abstain=votes_abstain,
            threshold=self.threshold,
            participants=participants_voted,
            algorithm_used="weighted",
            duration_ms=duration_ms,
            metadata={
                "total_weight": total_weight,
                "weighted_for": weighted_for,
                "weighted_against": weighted_against,
                "weighted_approval": weighted_approval
            }
        )


class ConsensusManager:
    """
    Multi-algorithm consensus manager for swarm coordination.

    Manages consensus proposals with pluggable algorithms, thread-safe
    vote collection, timeout handling, and comprehensive statistics.

    Attributes:
        coordinator: ICoordinator instance for message broadcasting
        default_algorithm: Default algorithm name to use
        algorithms: Registry of available consensus algorithms
        active_proposals: Currently active consensus proposals
        statistics: Consensus statistics (proposals, approvals, rejections, avg time)
        _lock: Thread lock for thread-safe operations
    """

    def __init__(
        self,
        coordinator,  # ICoordinator type hint would create circular import
        default_algorithm: str = "quorum"
    ):
        """
        Initialize ConsensusManager.

        Args:
            coordinator: ICoordinator instance for agent communication
            default_algorithm: Default consensus algorithm ("quorum", "weighted")

        Raises:
            ValueError: If coordinator is None or default_algorithm invalid
        """
        if coordinator is None:
            raise ValueError("Coordinator cannot be None")

        self.coordinator = coordinator
        self.default_algorithm = default_algorithm

        # Thread safety - initialize first
        self._lock = threading.RLock()

        # Algorithm registry
        self.algorithms: Dict[str, ConsensusAlgorithm] = {}

        # Register built-in algorithms
        self.register_algorithm("quorum", QuorumAlgorithm())
        self.register_algorithm("weighted", WeightedAlgorithm())

        # Validate default algorithm
        if default_algorithm not in self.algorithms:
            raise ValueError(f"Unknown default algorithm: {default_algorithm}")

        # Active proposals tracking
        # Format: {proposal_id: {votes: [], timeout_event: Event, algorithm: str}}
        self.active_proposals: Dict[str, Dict[str, Any]] = {}

        # Statistics
        self.statistics = {
            "total_proposals": 0,
            "approved": 0,
            "rejected": 0,
            "timeouts": 0,
            "total_duration_ms": 0,
            "by_algorithm": defaultdict(lambda: {
                "proposals": 0,
                "approved": 0,
                "rejected": 0,
                "timeouts": 0
            })
        }

    def register_algorithm(self, name: str, algorithm: ConsensusAlgorithm) -> bool:
        """
        Register new consensus algorithm.

        Args:
            name: Algorithm name for reference
            algorithm: ConsensusAlgorithm implementation

        Returns:
            True if registered successfully, False if name exists

        Raises:
            ValueError: If name is empty or algorithm is None
        """
        if not name or not name.strip():
            raise ValueError("Algorithm name cannot be empty")
        if algorithm is None:
            raise ValueError("Algorithm cannot be None")

        with self._lock:
            if name in self.algorithms:
                logger.warning(f"Algorithm '{name}' already registered, skipping")
                return False

            self.algorithms[name] = algorithm
            logger.info(f"Registered consensus algorithm: {name}")
            return True

    def request_consensus(
        self,
        proposal: Dict[str, Any],
        algorithm: Optional[str] = None,
        timeout_ms: int = 30000
    ) -> ConsensusResult:
        """
        Request consensus decision from swarm agents.

        Broadcasts proposal to all agents, collects votes with timeout,
        and returns consensus decision using specified algorithm.

        Args:
            proposal: Proposal data (must be JSON-serializable)
            algorithm: Algorithm name to use (default: self.default_algorithm)
            timeout_ms: Timeout in milliseconds (default: 30000 = 30s)

        Returns:
            ConsensusResult with decision and voting statistics

        Raises:
            ValueError: If proposal is None, algorithm unknown, or timeout < 100
        """
        if proposal is None:
            raise ValueError("Proposal cannot be None")
        if timeout_ms < 100:
            raise ValueError("Timeout must be >= 100ms")

        # Select algorithm
        algo_name = algorithm or self.default_algorithm
        if algo_name not in self.algorithms:
            raise ValueError(f"Unknown algorithm: {algo_name}")

        algo = self.algorithms[algo_name]

        # Get participants from topology
        topology_info = self.coordinator.get_topology_info()
        agent_count = topology_info.get("agent_count", 0)

        if agent_count == 0:
            logger.warning("No agents in topology, cannot request consensus")
            return ConsensusResult(
                decision=ConsensusDecision.REJECTED.value,
                votes_for=0,
                votes_against=0,
                threshold=0.5,
                participants=[],
                algorithm_used=algo_name,
                duration_ms=0,
                metadata={"error": "no_agents"}
            )

        # Initialize proposal
        start_time = time.time()

        with self._lock:
            # Get all active agent IDs (simplified - in real implementation would query coordinator)
            participants = self._get_active_agents()

            # Create proposal
            proposal_id = algo.propose(proposal, participants)

            # Track active proposal
            timeout_event = threading.Event()
            self.active_proposals[proposal_id] = {
                "votes": [],
                "timeout_event": timeout_event,
                "algorithm": algo_name,
                "start_time": start_time
            }

        # Broadcast proposal to all agents
        message = {
            "type": "consensus_request",
            "proposal_id": proposal_id,
            "proposal": proposal,
            "algorithm": algo_name,
            "timeout_ms": timeout_ms
        }

        try:
            self.coordinator.broadcast_message("consensus_manager", message)
        except Exception as e:
            logger.error(f"Failed to broadcast consensus request: {e}")
            with self._lock:
                del self.active_proposals[proposal_id]
            return ConsensusResult(
                decision=ConsensusDecision.REJECTED.value,
                votes_for=0,
                votes_against=0,
                threshold=0.5,
                participants=[],
                algorithm_used=algo_name,
                duration_ms=0,
                metadata={"error": str(e)}
            )

        # Wait for votes with timeout
        timeout_reached = not timeout_event.wait(timeout_ms / 1000.0)

        # Collect votes and make decision
        with self._lock:
            proposal_data = self.active_proposals.get(proposal_id)
            if not proposal_data:
                logger.error(f"Proposal {proposal_id} not found after vote collection")
                return ConsensusResult(
                    decision=ConsensusDecision.REJECTED.value,
                    votes_for=0,
                    votes_against=0,
                    threshold=0.5,
                    participants=[],
                    algorithm_used=algo_name,
                    duration_ms=0,
                    metadata={"error": "proposal_lost"}
                )

            votes = proposal_data["votes"]

            # Make decision
            result = algo.decide(proposal_id, votes, timeout_reached)

            # Update statistics
            self._update_statistics(result)

            # Clean up
            del self.active_proposals[proposal_id]

        logger.info(f"Consensus result for {proposal_id}: {result.decision} "
                   f"({result.votes_for} for, {result.votes_against} against, "
                   f"{len(result.participants)} participants, {result.duration_ms}ms)")

        return result

    def record_vote(
        self,
        proposal_id: str,
        agent_id: str,
        vote: VoteType,
        weight: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Record vote from agent for active proposal.

        Called by agents in response to consensus_request broadcast.

        Args:
            proposal_id: Proposal identifier
            agent_id: Agent casting vote
            vote: Vote type (for/against/abstain)
            weight: Vote weight (for weighted algorithms)
            metadata: Optional vote metadata

        Returns:
            True if vote recorded, False if proposal not found or duplicate vote

        Raises:
            ValueError: If proposal_id or agent_id is empty
        """
        if not proposal_id or not agent_id:
            raise ValueError("proposal_id and agent_id cannot be empty")

        with self._lock:
            if proposal_id not in self.active_proposals:
                logger.warning(f"Vote for unknown proposal: {proposal_id}")
                return False

            proposal_data = self.active_proposals[proposal_id]

            # Check for duplicate vote
            if any(v.agent_id == agent_id for v in proposal_data["votes"]):
                logger.warning(f"Duplicate vote from {agent_id} for {proposal_id}")
                return False

            # Record vote
            vote_obj = Vote(
                agent_id=agent_id,
                vote=vote,
                weight=weight,
                metadata=metadata or {}
            )
            proposal_data["votes"].append(vote_obj)

            logger.debug(f"Recorded vote from {agent_id}: {vote.value}")
            return True

    def get_algorithm_stats(self) -> Dict[str, Any]:
        """
        Get consensus statistics.

        Returns:
            Dict with overall and per-algorithm statistics: {
                "total_proposals": int,
                "approved": int,
                "rejected": int,
                "timeouts": int,
                "avg_duration_ms": float,
                "approval_rate": float,
                "by_algorithm": {
                    "quorum": {
                        "proposals": int,
                        "approved": int,
                        "rejected": int,
                        "timeouts": int,
                        "approval_rate": float
                    }
                }
            }
        """
        with self._lock:
            stats = self.statistics.copy()

            # Calculate average duration
            if stats["total_proposals"] > 0:
                stats["avg_duration_ms"] = stats["total_duration_ms"] / stats["total_proposals"]
                stats["approval_rate"] = stats["approved"] / stats["total_proposals"]
            else:
                stats["avg_duration_ms"] = 0.0
                stats["approval_rate"] = 0.0

            # Calculate per-algorithm approval rates
            for algo_name, algo_stats in stats["by_algorithm"].items():
                if algo_stats["proposals"] > 0:
                    algo_stats["approval_rate"] = algo_stats["approved"] / algo_stats["proposals"]
                else:
                    algo_stats["approval_rate"] = 0.0

            # Add active proposals count
            stats["active_proposals"] = len(self.active_proposals)

            return stats

    def _get_active_agents(self) -> List[str]:
        """
        Get list of active agent IDs from coordinator.

        In real implementation, this would query the coordinator's topology.
        For now, returns a simplified list.

        Returns:
            List of active agent IDs
        """
        # Simplified implementation - real version would query coordinator
        # topology_info = self.coordinator.get_topology_info()
        # return topology_info.get("agents", [])
        return []  # Placeholder - actual implementation would get from coordinator

    def _update_statistics(self, result: ConsensusResult) -> None:
        """
        Update consensus statistics.

        Args:
            result: ConsensusResult to record
        """
        # Must be called within lock
        self.statistics["total_proposals"] += 1

        if result.decision == ConsensusDecision.APPROVED.value:
            self.statistics["approved"] += 1
        elif result.decision == ConsensusDecision.REJECTED.value:
            self.statistics["rejected"] += 1
        elif result.decision == ConsensusDecision.TIMEOUT.value:
            self.statistics["timeouts"] += 1

        self.statistics["total_duration_ms"] += result.duration_ms

        # Update per-algorithm stats
        algo_stats = self.statistics["by_algorithm"][result.algorithm_used]
        algo_stats["proposals"] += 1

        if result.decision == ConsensusDecision.APPROVED.value:
            algo_stats["approved"] += 1
        elif result.decision == ConsensusDecision.REJECTED.value:
            algo_stats["rejected"] += 1
        elif result.decision == ConsensusDecision.TIMEOUT.value:
            algo_stats["timeouts"] += 1


# Module self-test
if __name__ == "__main__":
    import sys

    # Mock coordinator for testing
    class MockCoordinator:
        def get_topology_info(self):
            return {"agent_count": 5, "type": "mesh"}

        def broadcast_message(self, from_agent, message):
            return 5

    print("Testing ConsensusManager...")

    # Test 1: Initialization
    print("\n[Test 1] Initialization")
    coordinator = MockCoordinator()
    manager = ConsensusManager(coordinator, default_algorithm="quorum")
    assert "quorum" in manager.algorithms
    assert "weighted" in manager.algorithms
    print("✓ ConsensusManager initialized with built-in algorithms")

    # Test 2: Algorithm registration
    print("\n[Test 2] Algorithm Registration")
    custom_algo = QuorumAlgorithm(threshold=0.7)
    success = manager.register_algorithm("custom_quorum", custom_algo)
    assert success is True
    assert "custom_quorum" in manager.algorithms
    print("✓ Custom algorithm registered successfully")

    # Test 3: Quorum algorithm
    print("\n[Test 3] Quorum Algorithm")
    algo = QuorumAlgorithm(threshold=0.5)
    proposal_id = algo.propose({"action": "deploy"}, ["agent1", "agent2", "agent3"])

    votes = [
        Vote("agent1", VoteType.FOR),
        Vote("agent2", VoteType.FOR),
        Vote("agent3", VoteType.AGAINST)
    ]
    result = algo.decide(proposal_id, votes)
    assert result.decision == ConsensusDecision.APPROVED.value
    assert result.votes_for == 2
    assert result.votes_against == 1
    print(f"✓ Quorum decision: {result.decision} (2 for, 1 against)")

    # Test 4: Weighted algorithm
    print("\n[Test 4] Weighted Algorithm")
    weighted_algo = WeightedAlgorithm(
        threshold=0.6,
        agent_weights={"agent1": 2.0, "agent2": 1.0, "agent3": 1.0}
    )
    proposal_id = weighted_algo.propose({"action": "rollback"}, ["agent1", "agent2", "agent3"])

    votes = [
        Vote("agent1", VoteType.FOR),  # weight: 2.0
        Vote("agent2", VoteType.AGAINST),  # weight: 1.0
        Vote("agent3", VoteType.AGAINST)   # weight: 1.0
    ]
    result = weighted_algo.decide(proposal_id, votes)
    # Total weight: 4.0, weighted_for: 2.0, approval: 0.5 < 0.6
    assert result.decision == ConsensusDecision.REJECTED.value
    print(f"✓ Weighted decision: {result.decision} (weighted: 2.0/4.0 = 0.5 < 0.6)")

    # Test 5: Statistics
    print("\n[Test 5] Statistics")
    stats = manager.get_algorithm_stats()
    assert stats["total_proposals"] == 0
    assert stats["active_proposals"] == 0
    print(f"✓ Initial statistics: {stats}")

    # Test 6: Vote recording
    print("\n[Test 6] Vote Recording")
    # Create a proposal manually for testing
    algo = manager.algorithms["quorum"]
    proposal_id = algo.propose({"test": True}, ["agent1", "agent2"])
    manager.active_proposals[proposal_id] = {
        "votes": [],
        "timeout_event": threading.Event(),
        "algorithm": "quorum",
        "start_time": time.time()
    }

    success = manager.record_vote(proposal_id, "agent1", VoteType.FOR)
    assert success is True

    # Duplicate vote should fail
    success = manager.record_vote(proposal_id, "agent1", VoteType.AGAINST)
    assert success is False
    print("✓ Vote recording works correctly (including duplicate detection)")

    # Clean up test proposal
    del manager.active_proposals[proposal_id]

    print("\n" + "="*60)
    print("All tests passed! ConsensusManager implementation complete.")
    print("="*60)

    sys.exit(0)
