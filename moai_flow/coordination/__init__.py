"""
MoAI-Flow Coordination Module

Agent coordination mechanisms:
- Consensus: Voting and agreement protocols
- ConflictResolution: Handling conflicting decisions
- StateSynchronization: Distributed state synchronization
- Heartbeat: Agent health monitoring
- TaskAllocation: Task distribution algorithms
"""

# Phase 6B: Coordination Managers
from .consensus_manager import (
    ConsensusManager,
    ConsensusAlgorithm,
    ConsensusResult,
    ConsensusDecision,
    Vote,
    VoteType,
    QuorumAlgorithm,
    WeightedAlgorithm,
)
from .conflict_resolver import (
    ConflictResolver,
    StateVersion,
    ResolutionStrategy,
    CRDTType,
)
from .state_synchronizer import StateSynchronizer

# Phase 6B: Consensus Algorithms (from algorithms/ module)
from .algorithms import (
    # Base classes
    RaftState,
    # Consensus implementations
    RaftConsensus,
    QuorumConsensus,
    WeightedConsensus,
    GossipProtocol,
    ByzantineConsensus,
    # Presets and utilities
    QUORUM_PRESETS,
    EXPERT_WEIGHT_PRESET,
    create_domain_weights,
    # CRDT implementations
    CRDT,
    GCounter,
    PNCounter,
    LWWRegister,
    ORSet,
    CRDTConsensus,
    GossipConfig,
)

# Future exports (Phase 6C-6D)
# from .heartbeat import HeartbeatMonitor
# from .task_allocation import TaskAllocator

__all__ = [
    # Coordination Managers (Wave 2)
    "ConsensusManager",
    "ConflictResolver",
    "StateSynchronizer",
    # Base classes and results
    "ConsensusAlgorithm",
    "ConsensusResult",
    "ConsensusDecision",
    "Vote",
    "VoteType",
    "StateVersion",
    "ResolutionStrategy",
    "CRDTType",
    # Built-in algorithms from consensus_manager
    "QuorumAlgorithm",
    "WeightedAlgorithm",
    # Consensus Algorithms (Wave 1)
    "RaftState",
    "RaftConsensus",
    "QuorumConsensus",
    "WeightedConsensus",
    "GossipProtocol",
    "ByzantineConsensus",
    # Presets and utilities
    "QUORUM_PRESETS",
    "EXPERT_WEIGHT_PRESET",
    "create_domain_weights",
    # CRDT implementations
    "CRDT",
    "GCounter",
    "PNCounter",
    "LWWRegister",
    "ORSet",
    "CRDTConsensus",
    "GossipConfig",
    # Future: "HeartbeatMonitor",
    # Future: "TaskAllocator",
]
