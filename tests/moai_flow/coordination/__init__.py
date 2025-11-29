"""
Tests for MoAI-Flow Coordination Module (Phase 6B).

Comprehensive test coverage for coordination intelligence components:
- ConsensusManager: Algorithm registration, consensus requests, statistics
- QuorumConsensus: Majority voting with configurable thresholds
- RaftConsensus: Leader election, log replication, failure handling
- WeightedConsensus: Weighted voting with expert presets
- ConflictResolver: LWW, Version Vector, CRDT strategies
- StateSynchronizer: Full/delta sync, conflict resolution integration

Target: 215+ tests with 90%+ coverage across all components.
"""

__all__ = [
    # Test modules will be imported by pytest discovery
]
