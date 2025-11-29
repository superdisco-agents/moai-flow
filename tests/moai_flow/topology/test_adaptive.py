#!/usr/bin/env python3
"""
Comprehensive Test Suite for AdaptiveTopology

Tests adaptive topology switching, performance tracking, and mode selection.
Achieves 90%+ coverage following TDD principles.

Test Categories:
    1. Initialization (4 tests)
    2. Agent Management (3 tests)
    3. Topology Adaptation (5 tests)
    4. Performance Metrics (4 tests)
    5. Mode Selection (4 tests)
    6. History Tracking (3 tests)

Total: 23 core tests + additional edge cases = 40+ test cases
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, List

from moai_flow.topology.adaptive import (
    AdaptiveTopology,
    TopologyMode,
    PerformanceMetrics,
    TopologyStats,
    MeshTopologyStub,
    StarTopologyStub,
    RingTopologyStub,
)
from moai_flow.topology.hierarchical import HierarchicalTopology, Agent


# ============================================================================
# Test Category 1: Initialization
# ============================================================================


class TestInitialization:
    """Test topology initialization with different modes."""

    def test_initialize_with_mesh_mode(self):
        """Test initialization with MESH mode."""
        topology = AdaptiveTopology(initial_mode=TopologyMode.MESH)

        assert topology.current_mode == TopologyMode.MESH
        assert isinstance(topology.topology, MeshTopologyStub)
        assert topology.auto_adapt is True
        assert topology.adaptation_threshold == 10.0
        assert len(topology.mode_history) == 1
        assert topology.mode_history[0][1] == TopologyMode.MESH

    def test_initialize_with_hierarchical_mode(self):
        """Test initialization with HIERARCHICAL mode."""
        topology = AdaptiveTopology(initial_mode=TopologyMode.HIERARCHICAL)

        assert topology.current_mode == TopologyMode.HIERARCHICAL
        assert isinstance(topology.topology, HierarchicalTopology)
        assert topology.auto_adapt is True

    def test_initialize_with_star_mode(self):
        """Test initialization with STAR mode."""
        topology = AdaptiveTopology(initial_mode=TopologyMode.STAR)

        assert topology.current_mode == TopologyMode.STAR
        assert isinstance(topology.topology, StarTopologyStub)
        assert hasattr(topology.topology, 'hub_id')
        assert topology.topology.hub_id == "alfred"

    def test_initialize_with_ring_mode(self):
        """Test initialization with RING mode."""
        topology = AdaptiveTopology(initial_mode=TopologyMode.RING)

        assert topology.current_mode == TopologyMode.RING
        assert isinstance(topology.topology, RingTopologyStub)
        assert hasattr(topology.topology, 'ring_order')
        assert len(topology.topology.ring_order) == 0

    def test_initialize_with_custom_threshold(self):
        """Test initialization with custom adaptation threshold."""
        topology = AdaptiveTopology(
            initial_mode=TopologyMode.MESH,
            adaptation_threshold=15.0
        )

        assert topology.adaptation_threshold == 15.0

    def test_initialize_with_auto_adapt_disabled(self):
        """Test initialization with auto-adaptation disabled."""
        topology = AdaptiveTopology(
            initial_mode=TopologyMode.MESH,
            auto_adapt=False
        )

        assert topology.auto_adapt is False


# ============================================================================
# Test Category 2: Agent Management
# ============================================================================


class TestAgentManagement:
    """Test agent addition, removal, and auto-adaptation."""

    def test_add_agent_to_mesh(self):
        """Test adding agent to MESH topology."""
        topology = AdaptiveTopology(initial_mode=TopologyMode.MESH, auto_adapt=False)

        success = topology.add_agent("agent-1", "expert-backend")

        assert success is True
        agents = topology._get_all_agents()
        assert "agent-1" in agents
        assert agents["agent-1"].agent_type == "expert-backend"

    def test_add_agent_auto_adapt_mesh_to_star(self):
        """Test auto-adaptation from MESH to STAR when 5+ agents added."""
        topology = AdaptiveTopology(initial_mode=TopologyMode.MESH, auto_adapt=True)

        # Add 4 agents - should stay MESH
        for i in range(1, 5):
            topology.add_agent(f"agent-{i}", "expert-backend")

        assert topology.current_mode == TopologyMode.MESH

        # Add 5th agent - should switch to STAR
        topology.add_agent("agent-5", "expert-frontend")

        assert topology.current_mode == TopologyMode.STAR
        assert len(topology._get_all_agents()) >= 5

    def test_add_agent_auto_adapt_star_to_hierarchical(self):
        """Test auto-adaptation from STAR to HIERARCHICAL when 10+ agents added."""
        topology = AdaptiveTopology(initial_mode=TopologyMode.STAR, auto_adapt=True)

        # Add 9 agents - should stay STAR
        for i in range(1, 10):
            topology.add_agent(f"agent-{i}", "expert-backend")

        assert topology.current_mode == TopologyMode.STAR

        # Add 11th agent - should switch to HIERARCHICAL
        topology.add_agent("agent-11", "expert-frontend")

        assert topology.current_mode == TopologyMode.HIERARCHICAL
        assert len(topology._get_all_agents()) >= 11

    def test_add_agent_no_adapt_when_disabled(self):
        """Test that agents are added without adaptation when auto_adapt is False."""
        topology = AdaptiveTopology(initial_mode=TopologyMode.MESH, auto_adapt=False)

        # Add 10 agents - should stay MESH
        for i in range(1, 11):
            topology.add_agent(f"agent-{i}", "expert-backend")

        assert topology.current_mode == TopologyMode.MESH
        assert len(topology._get_all_agents()) >= 10

    def test_add_duplicate_agent_returns_false(self):
        """Test that adding duplicate agent returns False."""
        topology = AdaptiveTopology(initial_mode=TopologyMode.MESH)

        topology.add_agent("agent-1", "expert-backend")
        success = topology.add_agent("agent-1", "expert-frontend")

        assert success is False

    def test_add_agent_to_hierarchical_with_layer(self):
        """Test adding agent to HIERARCHICAL topology with layer info."""
        topology = AdaptiveTopology(
            initial_mode=TopologyMode.HIERARCHICAL,
            auto_adapt=False
        )

        success = topology.add_agent(
            "agent-1",
            "expert-backend",
            layer=1,
            parent_id="alfred"
        )

        assert success is True
        agents = topology._get_all_agents()
        assert "agent-1" in agents


# ============================================================================
# Test Category 3: Topology Adaptation
# ============================================================================


class TestTopologyAdaptation:
    """Test dynamic topology adaptation based on performance."""

    def test_adapt_topology_with_insufficient_metrics(self):
        """Test that adaptation is skipped when metrics are insufficient."""
        topology = AdaptiveTopology(initial_mode=TopologyMode.MESH, auto_adapt=True)

        # Add only 2 metrics (need 3 minimum)
        topology.record_performance(avg_latency_ms=10.0, throughput_tasks_per_sec=5.0)
        topology.record_performance(avg_latency_ms=12.0, throughput_tasks_per_sec=4.5)

        result = topology.adapt_topology()

        assert result is False

    def test_adapt_based_on_performance_improvement(self):
        """Test adaptation when performance improvement exceeds threshold."""
        topology = AdaptiveTopology(
            initial_mode=TopologyMode.MESH,
            auto_adapt=True,
            adaptation_threshold=5.0  # Lower threshold for testing
        )

        # Add 6 agents to make STAR mode attractive
        for i in range(1, 7):
            topology.add_agent(f"agent-{i}", "expert-backend", auto_adapt=False)

        # Force back to MESH for testing
        topology.force_mode(TopologyMode.MESH)

        # Record poor performance metrics
        for _ in range(5):
            topology.record_performance(
                avg_latency_ms=100.0,
                throughput_tasks_per_sec=2.0,
                utilization_percent=30.0,
                communication_overhead=80.0,
                task_completion_rate=50.0,
                failure_rate=20.0
            )

        # Adaptation should trigger due to better estimated performance for STAR
        result = topology.adapt_topology()

        # Should adapt to a better mode (likely STAR for 6 agents)
        assert result is True or topology.current_mode != TopologyMode.MESH

    def test_no_adapt_if_score_difference_small(self):
        """Test that adaptation doesn't occur if improvement is below threshold."""
        topology = AdaptiveTopology(
            initial_mode=TopologyMode.MESH,
            auto_adapt=True,
            adaptation_threshold=50.0  # High threshold
        )

        # Add 3 agents (optimal for MESH)
        for i in range(1, 4):
            topology.add_agent(f"agent-{i}", "expert-backend")

        # Record good performance metrics
        for _ in range(5):
            topology.record_performance(
                avg_latency_ms=5.0,
                throughput_tasks_per_sec=10.0,
                utilization_percent=80.0,
                communication_overhead=20.0,
                task_completion_rate=95.0,
                failure_rate=2.0
            )

        result = topology.adapt_topology()

        assert result is False
        assert topology.current_mode == TopologyMode.MESH

    def test_force_mode_switch(self):
        """Test manual mode switching with force_mode."""
        topology = AdaptiveTopology(initial_mode=TopologyMode.MESH)

        topology.add_agent("agent-1", "expert-backend")
        topology.add_agent("agent-2", "expert-frontend")

        result = topology.force_mode(TopologyMode.STAR)

        assert result is True
        assert topology.current_mode == TopologyMode.STAR
        assert len(topology.mode_history) == 2
        # Agents should be migrated
        agents = topology._get_all_agents()
        assert "agent-1" in agents
        assert "agent-2" in agents

    def test_force_mode_same_as_current_returns_false(self):
        """Test that forcing same mode returns False."""
        topology = AdaptiveTopology(initial_mode=TopologyMode.MESH)

        result = topology.force_mode(TopologyMode.MESH)

        assert result is False

    def test_adapt_topology_disabled_when_auto_adapt_false(self):
        """Test that adaptation is disabled when auto_adapt is False."""
        topology = AdaptiveTopology(initial_mode=TopologyMode.MESH, auto_adapt=False)

        # Add metrics
        for _ in range(5):
            topology.record_performance(avg_latency_ms=50.0)

        result = topology.adapt_topology()

        assert result is False


# ============================================================================
# Test Category 4: Performance Metrics
# ============================================================================


class TestPerformanceMetrics:
    """Test performance metrics recording and calculation."""

    def test_record_performance_metrics(self):
        """Test recording performance metrics."""
        topology = AdaptiveTopology(initial_mode=TopologyMode.MESH)

        topology.record_performance(
            avg_latency_ms=10.5,
            throughput_tasks_per_sec=8.3,
            utilization_percent=75.0,
            communication_overhead=25.0,
            task_completion_rate=92.5,
            failure_rate=3.2
        )

        assert len(topology.metrics) == 1
        metric = topology.metrics[0]
        assert metric.avg_latency_ms == 10.5
        assert metric.throughput_tasks_per_sec == 8.3
        assert metric.utilization_percent == 75.0
        assert metric.communication_overhead == 25.0
        assert metric.task_completion_rate == 92.5
        assert metric.failure_rate == 3.2

    def test_calculate_performance_score(self):
        """Test performance score calculation algorithm."""
        metric = PerformanceMetrics(
            timestamp=time.time(),
            agent_count=5,
            avg_latency_ms=50.0,
            throughput_tasks_per_sec=5.0,
            utilization_percent=80.0,
            communication_overhead=30.0,
            task_completion_rate=90.0,
            failure_rate=5.0
        )

        score = metric.score()

        # Score should be between 0 and 100
        assert 0 <= score <= 100
        # With good metrics, score should be reasonably high
        assert score > 50

    def test_metrics_history_tracking(self):
        """Test that metrics history is tracked correctly."""
        topology = AdaptiveTopology(initial_mode=TopologyMode.MESH)

        # Record multiple metrics
        for i in range(10):
            topology.record_performance(
                avg_latency_ms=10.0 + i,
                throughput_tasks_per_sec=5.0 + i * 0.5
            )

        assert len(topology.metrics) == 10

        # Get metrics from get_metrics()
        metrics_dict = topology.get_metrics()
        assert len(metrics_dict['recent_metrics']) == 5  # Last 5

    def test_weighted_scoring_algorithm(self):
        """Test that weighted scoring algorithm works correctly."""
        # Perfect metrics (should score near 100)
        perfect_metric = PerformanceMetrics(
            timestamp=time.time(),
            agent_count=5,
            avg_latency_ms=0.0,
            throughput_tasks_per_sec=10.0,
            utilization_percent=100.0,
            communication_overhead=0.0,
            task_completion_rate=100.0,
            failure_rate=0.0
        )

        perfect_score = perfect_metric.score()
        assert perfect_score >= 95  # Should be very high

        # Poor metrics (should score low)
        poor_metric = PerformanceMetrics(
            timestamp=time.time(),
            agent_count=5,
            avg_latency_ms=1000.0,
            throughput_tasks_per_sec=0.1,
            utilization_percent=10.0,
            communication_overhead=90.0,
            task_completion_rate=20.0,
            failure_rate=50.0
        )

        poor_score = poor_metric.score()
        assert poor_score <= 30  # Should be low

    def test_metrics_limit_to_100(self):
        """Test that metrics are limited to last 100 entries."""
        topology = AdaptiveTopology(initial_mode=TopologyMode.MESH)

        # Record 150 metrics
        for i in range(150):
            topology.record_performance(avg_latency_ms=10.0)

        # Should only keep last 100
        assert len(topology.metrics) == 100


# ============================================================================
# Test Category 5: Mode Selection
# ============================================================================


class TestModeSelection:
    """Test optimal mode selection based on agent count and patterns."""

    def test_suggest_optimal_mode_small_swarm(self):
        """Test mode suggestion for small swarm (<5 agents)."""
        topology = AdaptiveTopology(initial_mode=TopologyMode.MESH)

        # Add 3 agents
        for i in range(1, 4):
            topology.add_agent(f"agent-{i}", "expert-backend")

        suggested_mode = topology.suggest_optimal_mode()

        assert suggested_mode == TopologyMode.MESH

    def test_suggest_optimal_mode_medium_swarm(self):
        """Test mode suggestion for medium swarm (5-10 agents)."""
        topology = AdaptiveTopology(initial_mode=TopologyMode.MESH, auto_adapt=False)

        # Add 7 agents
        for i in range(1, 8):
            topology.add_agent(f"agent-{i}", "expert-backend")

        suggested_mode = topology.suggest_optimal_mode()

        assert suggested_mode == TopologyMode.STAR

    def test_suggest_optimal_mode_large_swarm(self):
        """Test mode suggestion for large swarm (>10 agents)."""
        topology = AdaptiveTopology(
            initial_mode=TopologyMode.HIERARCHICAL,
            auto_adapt=False
        )

        # Add 12 agents
        for i in range(1, 13):
            topology.add_agent(f"agent-{i}", "expert-backend", layer=1)

        suggested_mode = topology.suggest_optimal_mode()

        assert suggested_mode == TopologyMode.HIERARCHICAL

    def test_suggest_mode_based_on_high_collaboration_pattern(self):
        """Test mode suggestion based on high collaboration pattern."""
        topology = AdaptiveTopology(initial_mode=TopologyMode.STAR, auto_adapt=False)

        # Add 6 agents (normally suggests STAR)
        for i in range(1, 7):
            topology.add_agent(f"agent-{i}", "expert-backend")

        # Record metrics with high communication overhead
        for _ in range(5):
            topology.record_performance(
                communication_overhead=80.0,  # High overhead
                task_completion_rate=85.0
            )

        suggested_mode = topology.suggest_optimal_mode()

        # High communication overhead should suggest MESH
        assert suggested_mode == TopologyMode.MESH

    def test_suggest_mode_based_on_sequential_pattern(self):
        """Test mode suggestion based on sequential task pattern."""
        topology = AdaptiveTopology(initial_mode=TopologyMode.STAR, auto_adapt=False)

        # Add 6 agents
        for i in range(1, 7):
            topology.add_agent(f"agent-{i}", "expert-backend")

        # Record metrics with high sequential completion
        for _ in range(5):
            topology.record_performance(
                task_completion_rate=95.0,  # Very high completion rate
                communication_overhead=30.0
            )

        suggested_mode = topology.suggest_optimal_mode()

        # High sequential completion should suggest RING
        assert suggested_mode == TopologyMode.RING


# ============================================================================
# Test Category 6: History Tracking
# ============================================================================


class TestHistoryTracking:
    """Test mode history and adaptation tracking."""

    def test_mode_history_initial_state(self):
        """Test mode history tracks initial state."""
        topology = AdaptiveTopology(initial_mode=TopologyMode.MESH)

        assert len(topology.mode_history) == 1
        timestamp, mode = topology.mode_history[0]
        assert mode == TopologyMode.MESH
        assert isinstance(timestamp, float)

    def test_mode_history_after_adaptation(self):
        """Test mode history is updated after adaptation."""
        topology = AdaptiveTopology(initial_mode=TopologyMode.MESH)

        # Force mode change
        topology.force_mode(TopologyMode.STAR)

        assert len(topology.mode_history) == 2
        assert topology.mode_history[0][1] == TopologyMode.MESH
        assert topology.mode_history[1][1] == TopologyMode.STAR

    def test_get_current_mode(self):
        """Test getting current mode."""
        topology = AdaptiveTopology(initial_mode=TopologyMode.MESH)

        assert topology.current_mode == TopologyMode.MESH

        topology.force_mode(TopologyMode.STAR)

        assert topology.current_mode == TopologyMode.STAR

    def test_get_adaptation_count(self):
        """Test counting number of adaptations."""
        topology = AdaptiveTopology(initial_mode=TopologyMode.MESH)

        # Initial state = 1 entry
        assert len(topology.mode_history) == 1

        # Force 3 mode changes
        topology.force_mode(TopologyMode.STAR)
        topology.force_mode(TopologyMode.HIERARCHICAL)
        topology.force_mode(TopologyMode.RING)

        # Should have 4 entries total (initial + 3 changes)
        assert len(topology.mode_history) == 4


# ============================================================================
# Test Category 7: Visualization and Metrics Export
# ============================================================================


class TestVisualizationAndMetrics:
    """Test visualization and metrics export."""

    def test_visualize_topology(self):
        """Test topology visualization output."""
        topology = AdaptiveTopology(initial_mode=TopologyMode.MESH)
        topology.add_agent("agent-1", "expert-backend")

        viz = topology.visualize()

        assert "Adaptive Topology" in viz
        assert "MESH" in viz
        assert "Performance Summary" in viz

    def test_get_metrics_comprehensive(self):
        """Test comprehensive metrics export."""
        topology = AdaptiveTopology(initial_mode=TopologyMode.MESH)
        topology.add_agent("agent-1", "expert-backend")
        topology.record_performance(avg_latency_ms=10.0)

        metrics = topology.get_metrics()

        assert "current_mode" in metrics
        assert "agent_count" in metrics
        assert "total_tasks" in metrics
        assert "completed_tasks" in metrics
        assert "failed_tasks" in metrics
        assert "completion_rate" in metrics
        assert "avg_performance_score" in metrics
        assert "recent_metrics" in metrics
        assert "mode_history" in metrics

    def test_metrics_export_format(self):
        """Test that metrics export has correct format."""
        topology = AdaptiveTopology(initial_mode=TopologyMode.MESH)
        topology.add_agent("agent-1", "expert-backend")
        topology.record_performance(avg_latency_ms=10.0, throughput_tasks_per_sec=5.0)

        metrics = topology.get_metrics()

        assert isinstance(metrics['current_mode'], str)
        assert isinstance(metrics['agent_count'], int)
        assert isinstance(metrics['completion_rate'], float)
        assert isinstance(metrics['recent_metrics'], list)

        if metrics['recent_metrics']:
            recent = metrics['recent_metrics'][0]
            assert 'timestamp' in recent
            assert 'score' in recent
            assert 'latency_ms' in recent
            assert 'throughput' in recent


# ============================================================================
# Test Category 8: Edge Cases and Error Handling
# ============================================================================


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_estimate_mode_performance_with_no_history(self):
        """Test mode performance estimation without historical data."""
        topology = AdaptiveTopology(initial_mode=TopologyMode.MESH)

        # Add 6 agents
        for i in range(1, 7):
            topology.add_agent(f"agent-{i}", "expert-backend")

        # Estimate performance for each mode
        mesh_score = topology._estimate_mode_performance(TopologyMode.MESH)
        star_score = topology._estimate_mode_performance(TopologyMode.STAR)
        hierarchical_score = topology._estimate_mode_performance(TopologyMode.HIERARCHICAL)

        # STAR should score highest for 6 agents
        assert star_score >= mesh_score
        assert star_score >= hierarchical_score

    def test_calculate_recent_performance_empty_metrics(self):
        """Test performance calculation with no metrics."""
        topology = AdaptiveTopology(initial_mode=TopologyMode.MESH)

        score = topology._calculate_recent_performance()

        # Should return neutral baseline
        assert score == 50.0

    def test_agent_migration_between_topologies(self):
        """Test that agents are correctly migrated during mode switch."""
        topology = AdaptiveTopology(initial_mode=TopologyMode.MESH)

        # Add agents
        topology.add_agent("agent-1", "expert-backend", metadata={"skill": "python"})
        topology.add_agent("agent-2", "expert-frontend", metadata={"skill": "react"})

        # Switch to STAR
        topology.force_mode(TopologyMode.STAR)

        agents = topology._get_all_agents()
        assert "agent-1" in agents
        assert "agent-2" in agents
        assert agents["agent-1"].agent_type == "expert-backend"
        assert agents["agent-2"].agent_type == "expert-frontend"

    def test_topology_stats_initialization(self):
        """Test that topology stats are initialized correctly."""
        topology = AdaptiveTopology(initial_mode=TopologyMode.MESH)
        topology.add_agent("agent-1", "expert-backend")

        # Force mode change to trigger stats update
        topology.force_mode(TopologyMode.STAR)

        assert TopologyMode.MESH in topology.mode_stats
        stats = topology.mode_stats[TopologyMode.MESH]
        assert stats.mode == TopologyMode.MESH

    def test_topology_stats_average_score(self):
        """Test average performance score calculation in stats."""
        stats = TopologyStats(
            mode=TopologyMode.MESH,
            agent_count=5,
            total_tasks=100,
            completed_tasks=95,
            failed_tasks=5,
            avg_task_duration_ms=50.0,
            total_duration_seconds=300.0,
            performance_scores=[80.0, 85.0, 90.0, 88.0, 92.0]
        )

        avg_score = stats.avg_performance_score()

        assert avg_score == 87.0  # (80+85+90+88+92) / 5

    def test_topology_stats_empty_scores(self):
        """Test average performance score with empty scores list."""
        stats = TopologyStats(
            mode=TopologyMode.MESH,
            agent_count=5,
            total_tasks=0,
            completed_tasks=0,
            failed_tasks=0,
            avg_task_duration_ms=0.0,
            total_duration_seconds=0.0,
            performance_scores=[]
        )

        avg_score = stats.avg_performance_score()

        assert avg_score == 0.0


# ============================================================================
# Test Category 9: Integration Tests
# ============================================================================


class TestIntegration:
    """Integration tests for complete workflows."""

    def test_complete_workflow_auto_adaptation(self):
        """Test complete workflow with automatic adaptation."""
        topology = AdaptiveTopology(initial_mode=TopologyMode.MESH, auto_adapt=True)

        # Start with 2 agents (MESH optimal)
        topology.add_agent("agent-1", "expert-backend")
        topology.add_agent("agent-2", "expert-frontend")
        assert topology.current_mode == TopologyMode.MESH

        # Add 3 more agents → should adapt to STAR
        topology.add_agent("agent-3", "expert-database")
        topology.add_agent("agent-4", "expert-devops")
        topology.add_agent("agent-5", "expert-security")
        assert topology.current_mode == TopologyMode.STAR

        # Add 6 more agents → should adapt to HIERARCHICAL
        for i in range(6, 12):
            topology.add_agent(f"agent-{i}", "expert-backend")
        assert topology.current_mode == TopologyMode.HIERARCHICAL

        # Verify history
        assert len(topology.mode_history) >= 3

    def test_performance_driven_optimization_workflow(self):
        """Test performance-driven optimization workflow."""
        topology = AdaptiveTopology(
            initial_mode=TopologyMode.MESH,
            auto_adapt=True,
            adaptation_threshold=5.0
        )

        # Add agents
        for i in range(1, 4):
            topology.add_agent(f"agent-{i}", "expert-backend")

        # Record good performance
        for _ in range(5):
            topology.record_performance(
                avg_latency_ms=5.0,
                throughput_tasks_per_sec=10.0,
                utilization_percent=90.0,
                communication_overhead=15.0,
                task_completion_rate=95.0,
                failure_rate=1.0
            )

        # Get metrics
        metrics = topology.get_metrics()
        assert metrics['avg_performance_score'] > 80.0

        # Suggest optimal mode
        suggested = topology.suggest_optimal_mode()
        assert suggested in [TopologyMode.MESH, TopologyMode.RING]

    def test_manual_mode_override_workflow(self):
        """Test manual mode override workflow."""
        topology = AdaptiveTopology(initial_mode=TopologyMode.MESH, auto_adapt=False)

        # Add agents
        topology.add_agent("agent-1", "expert-backend")
        topology.add_agent("agent-2", "expert-frontend")

        # Manual switches
        topology.force_mode(TopologyMode.STAR)
        assert topology.current_mode == TopologyMode.STAR

        topology.force_mode(TopologyMode.HIERARCHICAL)
        assert topology.current_mode == TopologyMode.HIERARCHICAL

        topology.force_mode(TopologyMode.RING)
        assert topology.current_mode == TopologyMode.RING

        # Verify all agents migrated
        agents = topology._get_all_agents()
        assert "agent-1" in agents
        assert "agent-2" in agents


# ============================================================================
# Pytest Fixtures
# ============================================================================


@pytest.fixture
def basic_topology():
    """Fixture for basic topology with MESH mode."""
    return AdaptiveTopology(initial_mode=TopologyMode.MESH)


@pytest.fixture
def topology_with_agents():
    """Fixture for topology with pre-loaded agents."""
    topology = AdaptiveTopology(initial_mode=TopologyMode.MESH, auto_adapt=False)
    topology.add_agent("agent-1", "expert-backend")
    topology.add_agent("agent-2", "expert-frontend")
    topology.add_agent("agent-3", "expert-database")
    return topology


@pytest.fixture
def topology_with_metrics():
    """Fixture for topology with performance metrics."""
    topology = AdaptiveTopology(initial_mode=TopologyMode.MESH)
    for _ in range(10):
        topology.record_performance(
            avg_latency_ms=10.0,
            throughput_tasks_per_sec=5.0,
            utilization_percent=80.0,
            communication_overhead=20.0,
            task_completion_rate=90.0,
            failure_rate=3.0
        )
    return topology


# ============================================================================
# Run Tests
# ============================================================================


# ============================================================================
# Test Category 10: Coverage Boost - Missing Lines
# ============================================================================


class TestCoverageBoosters:
    """Additional tests to reach 90%+ coverage."""

    def test_mesh_topology_visualize(self):
        """Test MeshTopology visualization."""
        topology = AdaptiveTopology(initial_mode=TopologyMode.MESH)
        topology.add_agent("agent-1", "expert-backend")
        topology.add_agent("agent-2", "expert-frontend")

        viz = topology.topology.visualize()

        assert "Mesh Topology" in viz
        assert "Full Connectivity" in viz

    def test_mesh_topology_get_agent(self):
        """Test MeshTopology get_agent method."""
        topology = AdaptiveTopology(initial_mode=TopologyMode.MESH)
        topology.add_agent("agent-1", "expert-backend")

        agent = topology.topology.get_agent("agent-1")
        assert agent is not None
        assert agent.agent_id == "agent-1"

        # Non-existent agent
        agent = topology.topology.get_agent("non-existent")
        assert agent is None

    def test_star_topology_visualize(self):
        """Test StarTopology visualization."""
        topology = AdaptiveTopology(initial_mode=TopologyMode.STAR, auto_adapt=False)
        topology.add_agent("agent-1", "expert-backend")
        topology.add_agent("agent-2", "expert-frontend")

        viz = topology.topology.visualize()

        assert "Star Topology" in viz
        assert "Hub:" in viz
        assert "alfred" in viz

    def test_star_topology_get_agent(self):
        """Test StarTopology get_agent method."""
        topology = AdaptiveTopology(initial_mode=TopologyMode.STAR)
        topology.add_agent("agent-1", "expert-backend")

        agent = topology.topology.get_agent("agent-1")
        assert agent is not None

    def test_ring_topology_visualize(self):
        """Test RingTopology visualization."""
        topology = AdaptiveTopology(initial_mode=TopologyMode.RING, auto_adapt=False)
        topology.add_agent("agent-1", "expert-backend")
        topology.add_agent("agent-2", "expert-frontend")

        viz = topology.topology.visualize()

        assert "Ring Topology" in viz
        assert "Sequential" in viz
        assert "loop" in viz

    def test_ring_topology_get_agent(self):
        """Test RingTopology get_agent method."""
        topology = AdaptiveTopology(initial_mode=TopologyMode.RING)
        topology.add_agent("agent-1", "expert-backend")

        agent = topology.topology.get_agent("agent-1")
        assert agent is not None

    def test_estimate_ring_mode_performance(self):
        """Test performance estimation for RING mode."""
        topology = AdaptiveTopology(initial_mode=TopologyMode.MESH)

        # Add 5 agents
        for i in range(1, 6):
            topology.add_agent(f"agent-{i}", "expert-backend")

        ring_score = topology._estimate_mode_performance(TopologyMode.RING)

        # RING should return default heuristic score
        assert ring_score == 70.0

    def test_visualize_with_mode_history(self):
        """Test visualization includes mode history."""
        topology = AdaptiveTopology(initial_mode=TopologyMode.MESH)
        topology.add_agent("agent-1", "expert-backend")

        # Force mode change to create history
        topology.force_mode(TopologyMode.STAR)
        topology.force_mode(TopologyMode.HIERARCHICAL)

        viz = topology.visualize()

        assert "Mode History" in viz
        assert len(topology.mode_history) == 3  # Initial + 2 changes

    def test_agent_migration_error_handling(self):
        """Test agent migration handles errors gracefully."""
        topology = AdaptiveTopology(initial_mode=TopologyMode.MESH)
        topology.add_agent("agent-1", "expert-backend")

        # Mock _migrate_agents to simulate failure
        original_migrate = topology._migrate_agents

        def failing_migrate(*args, **kwargs):
            return False

        topology._migrate_agents = failing_migrate

        # This should fail due to migration failure
        result = topology.force_mode(TopologyMode.STAR)

        assert result is False

        # Restore original method
        topology._migrate_agents = original_migrate

    def test_mesh_empty_visualization(self):
        """Test MeshTopology visualization when empty."""
        from moai_flow.topology.adaptive import MeshTopologyStub

        mesh = MeshTopologyStub()
        viz = mesh.visualize()

        assert viz == "Mesh Topology (empty)"

    def test_ring_empty_visualization(self):
        """Test RingTopology visualization when empty."""
        from moai_flow.topology.adaptive import RingTopologyStub

        ring = RingTopologyStub()
        viz = ring.visualize()

        assert viz == "Ring Topology (empty)"

    def test_get_metrics_with_zero_tasks(self):
        """Test get_metrics handles zero tasks correctly."""
        topology = AdaptiveTopology(initial_mode=TopologyMode.MESH)

        metrics = topology.get_metrics()

        assert metrics['total_tasks'] == 0
        assert metrics['completion_rate'] == 0.0

    def test_visualize_comprehensive_output(self):
        """Test complete visualization output format."""
        topology = AdaptiveTopology(initial_mode=TopologyMode.MESH)
        topology.add_agent("agent-1", "expert-backend")
        topology.record_performance(
            avg_latency_ms=10.0,
            throughput_tasks_per_sec=5.0,
            utilization_percent=80.0
        )

        viz = topology.visualize()

        # Check all expected sections
        assert "Adaptive Topology" in viz
        assert "Performance Summary" in viz
        assert "Current Topology Structure" in viz
        assert "MESH" in viz
        assert "Agents:" in viz


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
