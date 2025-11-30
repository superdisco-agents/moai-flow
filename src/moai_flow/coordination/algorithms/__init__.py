"""
MoAI-Flow Consensus Algorithms

Consensus algorithm implementations for multi-agent decision making:
- BaseConsensus: Abstract base class for all consensus algorithms
- RaftConsensus: Leader-based consensus with log replication
- QuorumConsensus: Threshold-based voting (Phase 6B)
- WeightedConsensus: Expert-weighted voting (Phase 6B)
- GossipProtocol: Epidemic-style consensus (PRD-07)
- ByzantineConsensus: Byzantine fault-tolerant consensus (PRD-07)

CRDT implementations for conflict-free distributed state:
- CRDT: Abstract base class for all CRDTs
- GCounter: Grow-only counter
- PNCounter: Positive-negative counter
- LWWRegister: Last-write-wins register
- ORSet: Observed-remove set
- CRDTConsensus: CRDT-based consensus adapter

Module Structure:
- Phase 3 Wave 2 reorganization
- Internal cohesion: All algorithms import only from within coordination/ or from core/interfaces
- Self-contained consensus implementations for distributed agent coordination
"""

# Base classes and data structures
from .base import ConsensusAlgorithm, ConsensusResult, RaftState

# Consensus algorithm implementations
from .raft_consensus import RaftConsensus
from .quorum_consensus import QuorumConsensus, QUORUM_PRESETS
from .weighted_consensus import WeightedConsensus, EXPERT_WEIGHT_PRESET, create_domain_weights
from .gossip import GossipProtocol, GossipConfig
from .byzantine import ByzantineConsensus

# CRDT implementations
from .crdt import (
    CRDT,
    GCounter,
    PNCounter,
    LWWRegister,
    ORSet,
    CRDTConsensus,
)

__all__ = [
    # Base classes
    "ConsensusAlgorithm",
    "ConsensusResult",
    "RaftState",

    # Consensus algorithms
    "RaftConsensus",
    "QuorumConsensus",
    "QUORUM_PRESETS",
    "WeightedConsensus",
    "EXPERT_WEIGHT_PRESET",
    "create_domain_weights",
    "GossipProtocol",
    "GossipConfig",
    "ByzantineConsensus",

    # CRDT implementations
    "CRDT",
    "GCounter",
    "PNCounter",
    "LWWRegister",
    "ORSet",
    "CRDTConsensus",
]
