"""
MoAI-Flow Consensus Algorithms

Consensus algorithm implementations for multi-agent decision making:
- RaftConsensus: Leader-based consensus with log replication
- QuorumConsensus: Threshold-based voting (Phase 6B)
- WeightedConsensus: Expert-weighted voting (Phase 6B)
- Byzantine: Byzantine fault-tolerant consensus (future)
"""

from .base import ConsensusAlgorithm, ConsensusResult, RaftState
from .raft_consensus import RaftConsensus
from .weighted_consensus import WeightedConsensus, EXPERT_WEIGHT_PRESET, create_domain_weights
from .quorum_consensus import QuorumConsensus, QUORUM_PRESETS

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
]
