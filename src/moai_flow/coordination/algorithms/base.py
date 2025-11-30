"""
Base Consensus Algorithm Protocol

Defines the interface for all consensus algorithms in MoAI-Flow.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, Optional
from dataclasses import dataclass


class RaftState(Enum):
    """Raft node states."""
    FOLLOWER = "follower"
    CANDIDATE = "candidate"
    LEADER = "leader"


@dataclass
class ConsensusResult:
    """
    Consensus decision result.

    Attributes:
        decision: Consensus outcome ("approved", "rejected", or "timeout")
        votes_for: Number of votes in favor
        votes_against: Number of votes against
        abstain: Number of abstentions
        threshold: Required threshold for approval
        participants: List of participating agent IDs
        vote_details: Dict mapping agent_id to vote
        metadata: Additional algorithm-specific metadata
    """
    decision: str  # "approved", "rejected", or "timeout"
    votes_for: int
    votes_against: int
    abstain: int = 0
    threshold: float = 0.5
    participants: list = None
    vote_details: Dict[str, str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.participants is None:
            self.participants = []
        if self.vote_details is None:
            self.vote_details = {}
        if self.metadata is None:
            self.metadata = {}


class ConsensusAlgorithm(ABC):
    """
    Abstract base class for consensus algorithms.

    All consensus algorithms must implement this interface to integrate
    with the MoAI-Flow coordination system.
    """

    @abstractmethod
    def propose(
        self,
        proposal: Dict[str, Any],
        timeout_ms: int = 30000
    ) -> ConsensusResult:
        """
        Propose a decision for consensus.

        Args:
            proposal: Proposal data (must be JSON-serializable)
            timeout_ms: Timeout in milliseconds

        Returns:
            ConsensusResult with decision outcome
        """
        pass

    @abstractmethod
    def get_state(self) -> Dict[str, Any]:
        """
        Get current algorithm state.

        Returns:
            Dict with algorithm-specific state information
        """
        pass

    @abstractmethod
    def reset(self) -> bool:
        """
        Reset algorithm to initial state.

        Returns:
            True if reset successfully, False otherwise
        """
        pass
