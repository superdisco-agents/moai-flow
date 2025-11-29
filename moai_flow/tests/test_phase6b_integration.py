#!/usr/bin/env python3
"""
Integration tests for Phase 6B SwarmCoordinator integration.

Tests:
1. Consensus integration via request_consensus()
2. Conflict resolution via resolve_conflicts()
3. State synchronization via synchronize_swarm_state()
4. Delta sync via delta_sync()
5. Comprehensive stats via get_coordination_stats()
6. Backward compatibility with existing code
"""

import pytest
from typing import Dict, Any, List
from datetime import datetime, timezone

from moai_flow.core.swarm_coordinator import SwarmCoordinator
from moai_flow.coordination import (
    ConsensusDecision,
    ResolutionStrategy,
    StateVersion,
)


class TestPhase6BIntegration:
    """Test Phase 6B component integration with SwarmCoordinator."""

    def test_initialization_with_phase6b_enabled(self):
        """Test SwarmCoordinator initialization with Phase 6B enabled."""
        coordinator = SwarmCoordinator(
            topology_type="mesh",
            enable_consensus=True,
            default_consensus="quorum",
            enable_conflict_resolution=True
        )

        # Verify Phase 6B components initialized
        assert coordinator._enable_consensus is True
        assert coordinator._enable_conflict_resolution is True
        assert coordinator._consensus_manager is not None
        assert coordinator._conflict_resolver is not None
        # Note: _state_synchronizer is None until memory provider is initialized
        assert coordinator._state_synchronizer is None

    def test_initialization_with_phase6b_disabled(self):
        """Test SwarmCoordinator initialization with Phase 6B disabled."""
        coordinator = SwarmCoordinator(
            topology_type="mesh",
            enable_consensus=False,
            enable_conflict_resolution=False
        )

        # Verify Phase 6B components NOT initialized
        assert coordinator._enable_consensus is False
        assert coordinator._enable_conflict_resolution is False
        assert coordinator._consensus_manager is None
        assert coordinator._conflict_resolver is None
        assert coordinator._state_synchronizer is None

    def test_request_consensus_integration(self):
        """Test consensus integration via request_consensus()."""
        coordinator = SwarmCoordinator(
            topology_type="mesh",
            enable_consensus=True,
            consensus_threshold=0.51
        )

        # Register agents
        coordinator.register_agent("agent-1", {"type": "expert-backend"})
        coordinator.register_agent("agent-2", {"type": "expert-frontend"})
        coordinator.register_agent("agent-3", {"type": "manager-tdd"})

        # Request consensus
        proposal = {
            "proposal_id": "deploy-v2",
            "description": "Deploy version 2.0 to production",
            "action": "deploy"
        }

        result = coordinator.request_consensus(
            proposal=proposal,
            algorithm="quorum",
            timeout_ms=5000
        )

        # Verify result structure
        assert "decision" in result
        assert result["decision"] in ["approved", "rejected", "timeout"]
        assert "votes_for" in result
        assert "votes_against" in result
        assert "threshold" in result
        assert result["threshold"] == 0.51
        assert "participants" in result
        assert "algorithm_used" in result
        assert result["algorithm_used"] == "quorum"
        assert "duration_ms" in result

    def test_request_consensus_with_weighted_algorithm(self):
        """Test consensus with weighted algorithm."""
        coordinator = SwarmCoordinator(
            topology_type="mesh",
            enable_consensus=True,
            default_consensus="weighted"
        )

        # Register agents with weights
        coordinator.register_agent(
            "agent-1",
            {"type": "expert-backend", "weight": 2.0}
        )
        coordinator.register_agent(
            "agent-2",
            {"type": "expert-frontend", "weight": 1.5}
        )

        proposal = {"proposal_id": "refactor", "action": "refactor"}

        result = coordinator.request_consensus(
            proposal=proposal,
            algorithm="weighted",
            timeout_ms=5000
        )

        # Verify weighted algorithm used
        assert result["algorithm_used"] == "weighted"

    def test_consensus_disabled_raises_error(self):
        """Test that consensus request raises error when disabled."""
        coordinator = SwarmCoordinator(
            topology_type="mesh",
            enable_consensus=False
        )

        proposal = {"proposal_id": "test"}

        with pytest.raises(RuntimeError, match="Consensus not enabled"):
            coordinator.request_consensus(proposal)

    def test_get_consensus_stats(self):
        """Test consensus statistics retrieval."""
        coordinator = SwarmCoordinator(
            topology_type="mesh",
            enable_consensus=True,
            default_consensus="quorum"
        )

        # Register agents and request consensus
        coordinator.register_agent("agent-1", {"type": "expert-backend"})
        proposal = {"proposal_id": "test"}
        coordinator.request_consensus(proposal, timeout_ms=2000)

        # Get stats
        stats = coordinator.get_consensus_stats()

        assert stats["consensus_enabled"] is True
        assert stats["default_algorithm"] == "quorum"
        assert "algorithms" in stats
        assert stats["total_requests"] == 1

    def test_get_consensus_stats_when_disabled(self):
        """Test consensus stats when disabled."""
        coordinator = SwarmCoordinator(
            topology_type="mesh",
            enable_consensus=False
        )

        stats = coordinator.get_consensus_stats()

        assert stats == {"consensus_enabled": False}

    def test_resolve_conflicts(self):
        """Test conflict resolution integration."""
        coordinator = SwarmCoordinator(
            topology_type="mesh",
            enable_conflict_resolution=True
        )

        # Create conflicting state versions using StateVersion objects
        t1 = datetime.fromtimestamp(1000, tz=timezone.utc)
        t2 = datetime.fromtimestamp(2000, tz=timezone.utc)
        t3 = datetime.fromtimestamp(1500, tz=timezone.utc)

        conflicts = [
            StateVersion(state_key="config", value="v1", version=1, timestamp=t1, agent_id="agent-1"),
            StateVersion(state_key="config", value="v2", version=2, timestamp=t2, agent_id="agent-2"),
            StateVersion(state_key="config", value="v3", version=3, timestamp=t3, agent_id="agent-3")
        ]

        # Resolve conflicts (LWW strategy should pick v2 with latest timestamp)
        resolved = coordinator.resolve_conflicts("config", conflicts)

        # With LWW, latest timestamp wins (t2 is most recent)
        assert resolved.value == "v2"
        assert resolved.timestamp == t2

    def test_resolve_conflicts_empty_list_raises_error(self):
        """Test that empty conflicts list raises error."""
        coordinator = SwarmCoordinator(
            topology_type="mesh",
            enable_conflict_resolution=True
        )

        with pytest.raises(ValueError, match="Conflicts list cannot be empty"):
            coordinator.resolve_conflicts("config", [])

    def test_conflict_resolution_disabled_raises_error(self):
        """Test that conflict resolution raises error when disabled."""
        coordinator = SwarmCoordinator(
            topology_type="mesh",
            enable_conflict_resolution=False
        )

        conflicts = [{"value": "v1", "timestamp": 1000}]

        with pytest.raises(RuntimeError, match="Conflict resolution not enabled"):
            coordinator.resolve_conflicts("config", conflicts)

    def test_synchronize_swarm_state(self):
        """Test swarm state synchronization requires initialization."""
        coordinator = SwarmCoordinator(
            topology_type="mesh",
            enable_conflict_resolution=True
        )

        # Register agents
        coordinator.register_agent("agent-1", {"type": "expert-backend"})
        coordinator.register_agent("agent-2", {"type": "expert-frontend"})

        # Synchronize state should fail without memory provider initialization
        with pytest.raises(RuntimeError, match="StateSynchronizer not initialized"):
            coordinator.synchronize_swarm_state(
                swarm_id="swarm-001",
                state_key="task_queue"
            )

    def test_state_sync_disabled_raises_error(self):
        """Test that state sync raises error when disabled."""
        coordinator = SwarmCoordinator(
            topology_type="mesh",
            enable_conflict_resolution=False
        )

        with pytest.raises(RuntimeError, match="State synchronization not enabled"):
            coordinator.synchronize_swarm_state("swarm-001", "task_queue")

    def test_delta_sync(self):
        """Test delta synchronization requires initialization."""
        coordinator = SwarmCoordinator(
            topology_type="mesh",
            enable_conflict_resolution=True
        )

        # Delta sync should fail without memory provider initialization
        with pytest.raises(RuntimeError, match="StateSynchronizer not initialized"):
            coordinator.delta_sync(
                swarm_id="swarm-001",
                since_version=10
            )

    def test_delta_sync_disabled_raises_error(self):
        """Test that delta sync raises error when disabled."""
        coordinator = SwarmCoordinator(
            topology_type="mesh",
            enable_conflict_resolution=False
        )

        with pytest.raises(RuntimeError, match="State synchronization not enabled"):
            coordinator.delta_sync("swarm-001", 10)

    def test_get_coordination_stats(self):
        """Test comprehensive coordination statistics."""
        coordinator = SwarmCoordinator(
            topology_type="mesh",
            enable_monitoring=True,
            enable_consensus=True,
            enable_conflict_resolution=True
        )

        # Register agents
        coordinator.register_agent("agent-1", {"type": "expert-backend"})
        coordinator.register_agent("agent-2", {"type": "expert-frontend"})

        # Get comprehensive stats
        stats = coordinator.get_coordination_stats()

        # Verify all sections present
        assert "topology" in stats
        assert "monitoring" in stats
        assert "consensus" in stats

        # Verify topology stats
        assert stats["topology"]["type"] == "mesh"
        assert stats["topology"]["agent_count"] == 2

        # Verify monitoring stats
        assert stats["monitoring"]["monitoring_enabled"] is True

        # Verify consensus stats
        assert stats["consensus"]["consensus_enabled"] is True

    def test_backward_compatibility_with_existing_code(self):
        """Test that Phase 6B integration maintains backward compatibility."""
        # Create coordinator with all defaults (Phase 6B enabled by default)
        coordinator = SwarmCoordinator(topology_type="mesh")

        # Register agents (existing API)
        assert coordinator.register_agent("agent-1", {"type": "expert-backend"})
        assert coordinator.register_agent("agent-2", {"type": "expert-frontend"})

        # Send message (existing API)
        success = coordinator.send_message(
            from_agent="agent-1",
            to_agent="agent-2",
            message={"task": "test"}
        )
        assert success is True

        # Broadcast (existing API)
        sent_count = coordinator.broadcast_message(
            from_agent="agent-1",
            message={"type": "heartbeat"}
        )
        assert sent_count >= 0

        # Get topology info (existing API)
        info = coordinator.get_topology_info()
        assert info["type"] == "mesh"
        assert info["agent_count"] == 2

        # Synchronize state (existing API - still works)
        success = coordinator.synchronize_state(
            state_key="config",
            state_value={"debug": True}
        )
        assert success is True

    def test_consensus_history_maintained(self):
        """Test that consensus history is maintained for backward compatibility."""
        coordinator = SwarmCoordinator(
            topology_type="mesh",
            enable_consensus=True
        )

        coordinator.register_agent("agent-1", {"type": "expert-backend"})

        # Make consensus request
        proposal = {"proposal_id": "test-1"}
        result1 = coordinator.request_consensus(proposal, timeout_ms=2000)

        # Make another request
        proposal2 = {"proposal_id": "test-2"}
        result2 = coordinator.request_consensus(proposal2, timeout_ms=2000)

        # Verify history maintained
        history = coordinator.get_consensus_history(limit=10)
        assert len(history) == 2
        assert history[0]["decision"] in ["approved", "rejected", "timeout"]
        assert history[1]["decision"] in ["approved", "rejected", "timeout"]


class TestPhase6BCompleteWorkflow:
    """Test complete workflow integrating all Phase 6B components."""

    def test_complete_consensus_and_conflict_resolution_workflow(self):
        """Test complete workflow: consensus → conflict detection → resolution."""
        coordinator = SwarmCoordinator(
            topology_type="mesh",
            enable_consensus=True,
            enable_conflict_resolution=True,
            consensus_threshold=0.6
        )

        # Step 1: Register agents
        coordinator.register_agent("agent-1", {"type": "expert-backend", "weight": 1.5})
        coordinator.register_agent("agent-2", {"type": "expert-frontend", "weight": 1.0})
        coordinator.register_agent("agent-3", {"type": "manager-tdd", "weight": 1.0})

        # Step 2: Request consensus on deployment
        proposal = {
            "proposal_id": "deploy-v2",
            "description": "Deploy version 2.0",
            "action": "deploy"
        }

        consensus_result = coordinator.request_consensus(
            proposal=proposal,
            algorithm="weighted",
            timeout_ms=5000
        )

        assert consensus_result["algorithm_used"] == "weighted"

        # Step 3: Simulate conflicting state updates from different agents
        t1 = datetime.fromtimestamp(1000, tz=timezone.utc)
        t2 = datetime.fromtimestamp(2000, tz=timezone.utc)
        t3 = datetime.fromtimestamp(1500, tz=timezone.utc)

        conflicts = [
            StateVersion(state_key="deployment_version", value={"version": "2.0.1"}, version=1, timestamp=t1, agent_id="agent-1"),
            StateVersion(state_key="deployment_version", value={"version": "2.0.2"}, version=2, timestamp=t2, agent_id="agent-2"),
            StateVersion(state_key="deployment_version", value={"version": "2.0.0"}, version=3, timestamp=t3, agent_id="agent-3")
        ]

        # Step 4: Resolve conflicts
        resolved = coordinator.resolve_conflicts("deployment_version", conflicts)

        # LWW should pick latest (2.0.2 with timestamp t2, most recent)
        assert resolved.value["version"] == "2.0.2"

        # Step 5: Note - State synchronization requires memory provider
        # In production, you would call:
        # coordinator.initialize_state_synchronizer(memory_provider)
        # coordinator.synchronize_swarm_state("production-swarm", "deployment_version")

        # Step 6: Get comprehensive stats
        stats = coordinator.get_coordination_stats()

        assert stats["consensus"]["total_requests"] >= 1
        assert stats["topology"]["agent_count"] == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
