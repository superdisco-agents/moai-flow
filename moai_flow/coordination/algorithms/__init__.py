"""
MoAI-Flow Consensus Algorithms

Consensus algorithm implementations for multi-agent decision making:
- RaftConsensus: Leader-based consensus with log replication
- QuorumConsensus: Threshold-based voting (Phase 6B)
- WeightedConsensus: Expert-weighted voting (Phase 6B)
- GossipProtocol: Epidemic-style consensus (PRD-07)
- ByzantineConsensus: Byzantine fault-tolerant consensus (PRD-07)

CRDT implementations for conflict-free distributed state:
- GCounter: Grow-only counter
- PNCounter: Positive-negative counter
- LWWRegister: Last-write-wins register
- ORSet: Observed-remove set
"""

from .base import ConsensusAlgorithm, ConsensusResult, RaftState
from .raft_consensus import RaftConsensus
from .weighted_consensus import WeightedConsensus, EXPERT_WEIGHT_PRESET, create_domain_weights
from .quorum_consensus import QuorumConsensus, QUORUM_PRESETS
from .gossip import GossipProtocol, GossipConfig
from .crdt import CRDT, GCounter, PNCounter, LWWRegister, ORSet, CRDTConsensus
from .byzantine import ByzantineConsensus

__all__ = [
    "ConsensusAlgorithm",
    "ConsensusResult",
    "RaftState",
    "RaftConsensus",
    "WeightedConsensus",
    "EXPERT_WEIGHT_PRESET",
    "create_domain_weights",
    "QuorumConsensus",
    "QUORUM_PRESETS",
    "GossipProtocol",
    "GossipConfig",
    "ByzantineConsensus",
    "CRDT",
    "GCounter",
    "PNCounter",
    "LWWRegister",
    "ORSet",
    "CRDTConsensus",
]
