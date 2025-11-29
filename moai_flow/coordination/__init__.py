"""
MoAI-Flow Coordination Module

Agent coordination mechanisms:
- Consensus: Voting and agreement protocols
- ConflictResolution: Handling conflicting decisions
- StateSynchronization: Distributed state synchronization
- Heartbeat: Agent health monitoring
- TaskAllocation: Task distribution algorithms
"""

# Phase 6B: Consensus mechanisms
from .consensus_manager import (
    ConsensusManager,
    ConsensusAlgorithm,
    ConsensusResult,
    ConsensusDecision,
    QuorumAlgorithm,
    WeightedAlgorithm,
    Vote,
    VoteType,
)

# PRD-07: Advanced consensus algorithms
from .algorithms.gossip import GossipProtocol
from .algorithms.byzantine import ByzantineConsensus

# Phase 6B: Conflict Resolution & State Synchronization
from .conflict_resolver import (
    ConflictResolver,
    StateVersion,
    ResolutionStrategy,
    CRDTType
)
from .state_synchronizer import StateSynchronizer

# Future exports (Phase 6C-6D)
# from .heartbeat import HeartbeatMonitor
# from .task_allocation import TaskAllocator

__all__ = [
    # Phase 6B: Consensus
    "ConsensusManager",
    "ConsensusAlgorithm",
    "ConsensusResult",
    "ConsensusDecision",
    "QuorumAlgorithm",
    "WeightedAlgorithm",
    "Vote",
    "VoteType",
    "GossipProtocol",
    "ByzantineConsensus",
    # Phase 6B: Conflict Resolution & State Sync
    "ConflictResolver",
    "StateVersion",
    "ResolutionStrategy",
    "CRDTType",
    "StateSynchronizer",
    # Future: "HeartbeatMonitor",
    # Future: "TaskAllocator",
]
