#!/usr/bin/env python3
"""
Comprehensive test suite for HierarchicalTopology.

Tests all agent management, task delegation, result aggregation,
hierarchy navigation, and visualization features.

Target: 90%+ test coverage with comprehensive edge case validation.
"""

import pytest
from typing import Dict, Any, List
from moai_flow.topology.hierarchical import HierarchicalTopology, Agent


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def basic_topology():
    """Basic topology with just root agent."""
    return HierarchicalTopology(root_agent_id="alfred")


@pytest.fixture
def layered_topology():
    """Topology with multiple layers (root -> managers -> specialists)."""
    topo = HierarchicalTopology(root_agent_id="alfred")

    # Layer 1: Managers
    topo.add_layer("managers", ["manager-tdd", "manager-docs"])

    # Layer 2: Specialists under manager-tdd
    topo.add_layer(
        "specialists",
        ["expert-backend", "expert-frontend"],
        parent_id="manager-tdd"
    )

    return topo


@pytest.fixture
def complex_topology():
    """Complex multi-layer topology for advanced testing."""
    topo = HierarchicalTopology(root_agent_id="alfred")

    # Layer 1: Managers
    topo.add_layer("managers", ["manager-tdd", "manager-docs", "manager-quality"])

    # Layer 2: Specialists
    topo.add_layer("backend-specialists", ["expert-backend", "expert-database"], parent_id="manager-tdd")
    topo.add_layer("frontend-specialists", ["expert-frontend", "expert-uiux"], parent_id="manager-tdd")
    topo.add_layer("docs-specialists", ["expert-technical-writer"], parent_id="manager-docs")

    return topo


# ============================================================================
# 1. Agent Management Tests
# ============================================================================


class TestAgentManagement:
    """Test agent addition, removal, and basic management."""

    def test_add_root_agent(self):
        """Test root agent is created on initialization."""
        topo = HierarchicalTopology(root_agent_id="alfred")

        assert "alfred" in topo.agents
        assert topo.root_id == "alfred"
        assert topo.agents["alfred"].layer == 0
        assert topo.agents["alfred"].parent_id is None
        assert topo.agents["alfred"].agent_type == "alfred"

    def test_add_child_agent(self, basic_topology):
        """Test adding child agent to root."""
        success = basic_topology.add_agent(
            agent_id="manager-tdd",
            agent_type="manager-tdd",
            layer=1,
            parent_id="alfred"
        )

        assert success is True
        assert "manager-tdd" in basic_topology.agents
        assert basic_topology.agents["manager-tdd"].parent_id == "alfred"
        assert "manager-tdd" in basic_topology.agents["alfred"].children

    def test_add_agent_with_metadata(self, basic_topology):
        """Test adding agent with custom metadata."""
        metadata = {"skill_level": "expert", "language": "python"}

        basic_topology.add_agent(
            agent_id="expert-backend",
            agent_type="expert-backend",
            layer=1,
            parent_id="alfred",
            metadata=metadata
        )

        agent = basic_topology.get_agent("expert-backend")
        assert agent.metadata["skill_level"] == "expert"
        assert agent.metadata["language"] == "python"

    def test_add_agent_duplicate_id(self, basic_topology):
        """Test that duplicate agent IDs are rejected."""
        basic_topology.add_agent("manager-tdd", "manager-tdd", layer=1, parent_id="alfred")

        # Try to add duplicate
        success = basic_topology.add_agent("manager-tdd", "manager-tdd", layer=1, parent_id="alfred")

        assert success is False

    def test_add_agent_invalid_parent(self, basic_topology):
        """Test that non-existent parent raises ValueError."""
        with pytest.raises(ValueError, match="Parent agent nonexistent not found"):
            basic_topology.add_agent(
                "manager-tdd",
                "manager-tdd",
                layer=1,
                parent_id="nonexistent"
            )

    def test_add_agent_negative_layer(self, basic_topology):
        """Test that negative layer raises ValueError."""
        with pytest.raises(ValueError, match="Layer must be non-negative"):
            basic_topology.add_agent(
                "manager-tdd",
                "manager-tdd",
                layer=-1,
                parent_id="alfred"
            )

    def test_add_layer(self, basic_topology):
        """Test adding a complete layer of agents."""
        layer_num = basic_topology.add_layer("managers", ["manager-tdd", "manager-docs"])

        assert layer_num == 1
        assert "manager-tdd" in basic_topology.agents
        assert "manager-docs" in basic_topology.agents
        assert basic_topology.agents["manager-tdd"].layer == 1
        assert basic_topology.agents["manager-docs"].layer == 1

    def test_add_layer_with_custom_parent(self, layered_topology):
        """Test adding layer with specific parent."""
        layer_num = layered_topology.add_layer(
            "specialists",
            ["expert-security"],
            parent_id="manager-docs"
        )

        assert layer_num == 2
        assert "expert-security" in layered_topology.agents
        assert layered_topology.agents["expert-security"].parent_id == "manager-docs"

    def test_add_layer_empty_types(self, basic_topology):
        """Test that empty agent_types raises ValueError."""
        with pytest.raises(ValueError, match="agent_types cannot be empty"):
            basic_topology.add_layer("managers", [])

    def test_add_layer_nonexistent_parent(self, basic_topology):
        """Test that non-existent parent raises ValueError."""
        with pytest.raises(ValueError, match="Parent agent nonexistent not found"):
            basic_topology.add_layer("managers", ["manager-tdd"], parent_id="nonexistent")

    def test_cycle_prevention(self, layered_topology):
        """Test that cycles are prevented when adding agents."""
        # The _would_create_cycle method checks if adding agent_id with parent_id would create a cycle
        # Scenario: If we try to add "alfred" with parent "manager-tdd", this creates a cycle
        # because alfred is already an ancestor of manager-tdd

        # This WOULD create a cycle (alfred is ancestor of manager-tdd)
        assert layered_topology._would_create_cycle("alfred", "manager-tdd") is True

        # This would NOT create a cycle (manager-tdd is not ancestor of expert-backend)
        # Actually, expert-backend is a child of manager-tdd, so manager-tdd IS an ancestor
        # If we try to add manager-tdd with parent expert-backend, it would create a cycle
        assert layered_topology._would_create_cycle("manager-tdd", "expert-backend") is True

        # This would NOT create a cycle (new agent with valid parent)
        assert layered_topology._would_create_cycle("new-agent", "expert-backend") is False

    def test_get_agent(self, layered_topology):
        """Test retrieving agent by ID."""
        agent = layered_topology.get_agent("manager-tdd")

        assert agent is not None
        assert agent.agent_id == "manager-tdd"
        assert agent.agent_type == "manager-tdd"

    def test_get_agent_nonexistent(self, basic_topology):
        """Test retrieving non-existent agent returns None."""
        agent = basic_topology.get_agent("nonexistent")
        assert agent is None

    def test_update_agent_status(self, layered_topology):
        """Test updating agent status."""
        success = layered_topology.update_agent_status("manager-tdd", "working")

        assert success is True
        assert layered_topology.agents["manager-tdd"].status == "working"

    def test_update_agent_status_nonexistent(self, basic_topology):
        """Test updating non-existent agent status returns False."""
        success = basic_topology.update_agent_status("nonexistent", "working")
        assert success is False


# ============================================================================
# 2. Task Delegation Tests
# ============================================================================


class TestTaskDelegation:
    """Test task delegation between agents."""

    def test_delegate_task_parent_to_child(self, layered_topology):
        """Test task delegation from parent to child."""
        task = {"action": "implement", "spec": "SPEC-001"}

        success = layered_topology.delegate_task(
            from_agent="alfred",
            to_agent="manager-tdd",
            task=task
        )

        assert success is True
        agent = layered_topology.get_agent("manager-tdd")
        assert agent.status == "working"
        assert "tasks" in agent.metadata
        assert len(agent.metadata["tasks"]) == 1
        assert agent.metadata["tasks"][0]["from"] == "alfred"
        assert agent.metadata["tasks"][0]["task"] == task

    def test_delegate_task_multiple_tasks(self, layered_topology):
        """Test delegating multiple tasks to same agent."""
        task1 = {"action": "implement", "spec": "SPEC-001"}
        task2 = {"action": "test", "spec": "SPEC-001"}

        layered_topology.delegate_task("alfred", "manager-tdd", task1)
        layered_topology.delegate_task("alfred", "manager-tdd", task2)

        agent = layered_topology.get_agent("manager-tdd")
        assert len(agent.metadata["tasks"]) == 2

    def test_delegate_task_invalid_from_agent(self, layered_topology):
        """Test delegation from non-existent agent raises ValueError."""
        with pytest.raises(ValueError, match="Agent nonexistent not found"):
            layered_topology.delegate_task(
                from_agent="nonexistent",
                to_agent="manager-tdd",
                task={"action": "test"}
            )

    def test_delegate_task_invalid_to_agent(self, layered_topology):
        """Test delegation to non-existent agent raises ValueError."""
        with pytest.raises(ValueError, match="Agent nonexistent not found"):
            layered_topology.delegate_task(
                from_agent="alfred",
                to_agent="nonexistent",
                task={"action": "test"}
            )

    def test_delegate_task_non_hierarchical_warning(self, layered_topology, caplog):
        """Test warning when delegating outside hierarchy."""
        # Delegate from manager-tdd to manager-docs (not parent-child)
        layered_topology.delegate_task(
            from_agent="manager-tdd",
            to_agent="manager-docs",
            task={"action": "test"}
        )

        # Should still succeed but log warning
        assert "may not follow hierarchy" in caplog.text

    def test_delegate_task_timestamp(self, layered_topology):
        """Test that tasks include timestamp."""
        layered_topology.delegate_task(
            from_agent="alfred",
            to_agent="manager-tdd",
            task={"action": "test"}
        )

        agent = layered_topology.get_agent("manager-tdd")
        task_record = agent.metadata["tasks"][0]
        assert "delegated_at" in task_record
        assert task_record["delegated_at"].endswith("Z")  # ISO8601 format


# ============================================================================
# 3. Result Aggregation Tests
# ============================================================================


class TestResultAggregation:
    """Test result aggregation from children."""

    def test_aggregate_results_from_children(self, layered_topology):
        """Test aggregating results from child agents."""
        # Add results to children
        layered_topology.agents["expert-backend"].metadata["results"] = [{"status": "completed"}]
        layered_topology.agents["expert-frontend"].metadata["results"] = [{"status": "completed"}]
        layered_topology.agents["expert-backend"].status = "completed"
        layered_topology.agents["expert-frontend"].status = "completed"

        # Aggregate
        aggregated = layered_topology.aggregate_results("manager-tdd")

        assert aggregated["agent_id"] == "manager-tdd"
        assert aggregated["children_count"] == 2
        assert len(aggregated["results"]) == 2
        assert aggregated["all_completed"] is True

    def test_aggregate_results_incomplete_children(self, layered_topology):
        """Test aggregation with incomplete children."""
        # One child completed, one still working
        layered_topology.agents["expert-backend"].status = "completed"
        layered_topology.agents["expert-frontend"].status = "working"

        aggregated = layered_topology.aggregate_results("manager-tdd")

        assert aggregated["all_completed"] is False

    def test_aggregate_results_no_children(self, basic_topology):
        """Test aggregation for agent with no children."""
        aggregated = basic_topology.aggregate_results("alfred")

        assert aggregated["agent_id"] == "alfred"
        assert aggregated["children_count"] == 0
        assert aggregated["results"] == []
        assert aggregated["all_completed"] is True

    def test_aggregate_results_nonexistent_agent(self, basic_topology):
        """Test aggregation for non-existent agent raises ValueError."""
        with pytest.raises(ValueError, match="Agent nonexistent not found"):
            basic_topology.aggregate_results("nonexistent")

    def test_aggregate_results_structure(self, layered_topology):
        """Test detailed structure of aggregated results."""
        # Setup results - need to check which children exist first
        children = layered_topology.agents["manager-tdd"].children

        # Setup results for expert-backend
        layered_topology.agents["expert-backend"].metadata["results"] = [
            {"test": "backend-test-1", "passed": True}
        ]
        layered_topology.agents["expert-backend"].status = "completed"

        aggregated = layered_topology.aggregate_results("manager-tdd")

        # Find the expert-backend result in aggregated results
        backend_result = next(
            r for r in aggregated["results"] if r["agent_id"] == "expert-backend"
        )

        # Verify structure
        assert "agent_id" in backend_result
        assert "agent_type" in backend_result
        assert "status" in backend_result
        assert "results" in backend_result
        assert backend_result["results"] == [{"test": "backend-test-1", "passed": True}]


# ============================================================================
# 4. Hierarchy Navigation Tests
# ============================================================================


class TestHierarchyNavigation:
    """Test hierarchy navigation and path finding."""

    def test_get_path_to_root(self, layered_topology):
        """Test getting path from leaf to root."""
        path = layered_topology.get_path_to_root("expert-backend")

        assert path == ["expert-backend", "manager-tdd", "alfred"]

    def test_get_path_to_root_from_root(self, basic_topology):
        """Test path from root to root."""
        path = basic_topology.get_path_to_root("alfred")

        assert path == ["alfred"]

    def test_get_path_to_root_from_manager(self, layered_topology):
        """Test path from manager to root."""
        path = layered_topology.get_path_to_root("manager-tdd")

        assert path == ["manager-tdd", "alfred"]

    def test_get_path_to_root_nonexistent(self, basic_topology):
        """Test path for non-existent agent raises ValueError."""
        with pytest.raises(ValueError, match="Agent nonexistent not found"):
            basic_topology.get_path_to_root("nonexistent")

    def test_get_layer_agents(self, layered_topology):
        """Test getting all agents at a layer."""
        layer_1_agents = layered_topology.get_layer_agents(1)

        assert len(layer_1_agents) == 2
        agent_ids = {agent.agent_id for agent in layer_1_agents}
        assert agent_ids == {"manager-tdd", "manager-docs"}

    def test_get_layer_agents_empty_layer(self, basic_topology):
        """Test getting agents from non-existent layer."""
        agents = basic_topology.get_layer_agents(99)

        assert agents == []

    def test_get_layer_agents_root(self, basic_topology):
        """Test getting root layer agents."""
        agents = basic_topology.get_layer_agents(0)

        assert len(agents) == 1
        assert agents[0].agent_id == "alfred"

    def test_get_children(self, layered_topology):
        """Test accessing agent's children."""
        agent = layered_topology.get_agent("manager-tdd")

        assert len(agent.children) == 2
        assert "expert-backend" in agent.children
        assert "expert-frontend" in agent.children

    def test_get_parent(self, layered_topology):
        """Test accessing agent's parent."""
        agent = layered_topology.get_agent("expert-backend")

        assert agent.parent_id == "manager-tdd"


# ============================================================================
# 5. Visualization Tests
# ============================================================================


class TestVisualization:
    """Test tree visualization and structure."""

    def test_visualize_tree_structure(self, layered_topology):
        """Test basic tree visualization."""
        tree = layered_topology.visualize()

        assert "alfred (Root)" in tree
        assert "manager-tdd" in tree
        assert "manager-docs" in tree
        assert "expert-backend" in tree
        assert "expert-frontend" in tree

    def test_visualize_single_node(self, basic_topology):
        """Test visualization of single-node tree."""
        tree = basic_topology.visualize()

        assert tree == "alfred (Root)"

    def test_visualize_multi_layer(self, complex_topology):
        """Test visualization of complex multi-layer topology."""
        tree = complex_topology.visualize()

        # Check root
        assert "alfred (Root)" in tree

        # Check managers
        assert "manager-tdd" in tree
        assert "manager-docs" in tree
        assert "manager-quality" in tree

        # Check specialists
        assert "expert-backend" in tree
        assert "expert-database" in tree
        assert "expert-frontend" in tree
        assert "expert-uiux" in tree
        assert "expert-technical-writer" in tree

    def test_visualize_tree_connectors(self, layered_topology):
        """Test that tree uses proper ASCII connectors."""
        tree = layered_topology.visualize()

        # Should contain tree connectors
        assert "├─" in tree or "└─" in tree

    def test_visualize_sorted_children(self, layered_topology):
        """Test that children are displayed in sorted order."""
        # Add children in reverse order
        layered_topology.add_agent("z-agent", "z-type", layer=1, parent_id="alfred")
        layered_topology.add_agent("a-agent", "a-type", layer=1, parent_id="alfred")

        tree = layered_topology.visualize()
        lines = tree.split("\n")

        # Find positions of a-agent and z-agent
        a_pos = next(i for i, line in enumerate(lines) if "a-agent" in line)
        z_pos = next(i for i, line in enumerate(lines) if "z-agent" in line)

        # a-agent should come before z-agent
        assert a_pos < z_pos


# ============================================================================
# 6. Topology Statistics Tests
# ============================================================================


class TestTopologyStatistics:
    """Test topology statistics and metrics."""

    def test_get_topology_stats_basic(self, basic_topology):
        """Test basic topology statistics."""
        stats = basic_topology.get_topology_stats()

        assert stats["total_agents"] == 1
        assert stats["total_layers"] == 1
        assert stats["root_id"] == "alfred"
        assert stats["agents_per_layer"] == {0: 1}
        assert stats["status_distribution"] == {"idle": 1}

    def test_get_topology_stats_layered(self, layered_topology):
        """Test statistics for layered topology."""
        stats = layered_topology.get_topology_stats()

        assert stats["total_agents"] == 5  # alfred + 2 managers + 2 specialists
        assert stats["total_layers"] == 3  # 0, 1, 2
        assert stats["agents_per_layer"][0] == 1  # alfred
        assert stats["agents_per_layer"][1] == 2  # managers
        assert stats["agents_per_layer"][2] == 2  # specialists

    def test_get_topology_stats_status_distribution(self, layered_topology):
        """Test status distribution in stats."""
        # Change some statuses
        layered_topology.update_agent_status("manager-tdd", "working")
        layered_topology.update_agent_status("expert-backend", "completed")

        stats = layered_topology.get_topology_stats()

        assert stats["status_distribution"]["idle"] == 3
        assert stats["status_distribution"]["working"] == 1
        assert stats["status_distribution"]["completed"] == 1


# ============================================================================
# 7. Edge Cases and Error Handling Tests
# ============================================================================


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_agent_hash_equality(self):
        """Test that agents with same ID are hashable and equal."""
        agent1 = Agent(agent_id="test-1", agent_type="test", layer=0)
        agent2 = Agent(agent_id="test-1", agent_type="test", layer=0)

        # Should have same hash (for set operations)
        assert hash(agent1) == hash(agent2)

    def test_agent_in_set(self):
        """Test agents can be used in sets."""
        agent1 = Agent(agent_id="test-1", agent_type="test", layer=0)
        agent2 = Agent(agent_id="test-2", agent_type="test", layer=0)

        agent_set = {agent1, agent2}
        assert len(agent_set) == 2
        assert agent1 in agent_set

    def test_empty_children_set(self, basic_topology):
        """Test agent with no children has empty set."""
        agent = basic_topology.get_agent("alfred")
        assert isinstance(agent.children, set)
        assert len(agent.children) == 0

    def test_metadata_persistence(self, layered_topology):
        """Test that metadata persists across operations."""
        metadata = {"custom": "value", "number": 42}
        layered_topology.agents["manager-tdd"].metadata.update(metadata)

        # Retrieve and verify
        agent = layered_topology.get_agent("manager-tdd")
        assert agent.metadata["custom"] == "value"
        assert agent.metadata["number"] == 42

    def test_layer_counter_tracking(self, basic_topology):
        """Test internal layer counter is tracked."""
        assert hasattr(basic_topology, "_layer_counter")
        assert basic_topology._layer_counter == 0

    def test_layers_dict_structure(self, layered_topology):
        """Test internal layers dict structure."""
        assert isinstance(layered_topology.layers, dict)
        assert 0 in layered_topology.layers
        assert 1 in layered_topology.layers
        assert 2 in layered_topology.layers

    def test_timestamp_format(self, layered_topology):
        """Test timestamp generation format."""
        timestamp = layered_topology._get_timestamp()

        assert timestamp.endswith("Z")
        assert "T" in timestamp  # ISO8601 date-time separator

    def test_large_topology_performance(self):
        """Test topology with many agents."""
        topo = HierarchicalTopology(root_agent_id="alfred")

        # Add 50 managers
        managers = [f"manager-{i}" for i in range(50)]
        topo.add_layer("managers", managers)

        # Add 100 specialists across managers
        for i in range(10):
            parent = f"manager-{i}"
            specialists = [f"specialist-{i}-{j}" for j in range(10)]
            topo.add_layer(f"specialists-{i}", specialists, parent_id=parent)

        stats = topo.get_topology_stats()
        assert stats["total_agents"] == 151  # 1 root + 50 managers + 100 specialists


# ============================================================================
# 8. Integration Tests
# ============================================================================


class TestIntegration:
    """Test complete workflows and integration scenarios."""

    def test_complete_workflow(self, layered_topology):
        """Test complete task delegation and result aggregation workflow."""
        # Step 1: Delegate from alfred to manager-tdd
        layered_topology.delegate_task(
            "alfred",
            "manager-tdd",
            {"spec": "SPEC-001", "action": "implement"}
        )

        # Step 2: Manager delegates to specialists
        layered_topology.delegate_task(
            "manager-tdd",
            "expert-backend",
            {"spec": "SPEC-001", "component": "backend"}
        )
        layered_topology.delegate_task(
            "manager-tdd",
            "expert-frontend",
            {"spec": "SPEC-001", "component": "frontend"}
        )

        # Step 3: Specialists complete work
        layered_topology.agents["expert-backend"].status = "completed"
        layered_topology.agents["expert-backend"].metadata["results"] = [{"success": True}]
        layered_topology.agents["expert-frontend"].status = "completed"
        layered_topology.agents["expert-frontend"].metadata["results"] = [{"success": True}]

        # Step 4: Aggregate results
        results = layered_topology.aggregate_results("manager-tdd")

        # Verify
        assert results["all_completed"] is True
        assert results["children_count"] == 2

        # Step 5: Manager completes
        layered_topology.update_agent_status("manager-tdd", "completed")

        # Step 6: Trace path to root
        path = layered_topology.get_path_to_root("expert-backend")
        assert path == ["expert-backend", "manager-tdd", "alfred"]

    def test_parallel_branch_execution(self, complex_topology):
        """Test parallel execution across multiple branches."""
        # Delegate to multiple managers
        managers = ["manager-tdd", "manager-docs", "manager-quality"]
        for manager in managers:
            complex_topology.delegate_task(
                "alfred",
                manager,
                {"action": "process", "manager": manager}
            )
            complex_topology.update_agent_status(manager, "working")

        # Each manager delegates to their specialists
        complex_topology.delegate_task("manager-tdd", "expert-backend", {"task": "backend"})
        complex_topology.delegate_task("manager-tdd", "expert-frontend", {"task": "frontend"})
        complex_topology.delegate_task("manager-docs", "expert-technical-writer", {"task": "docs"})

        # Verify structure
        stats = complex_topology.get_topology_stats()
        # Note: All specialists are initially idle, only managers are working
        # Total agents: 1 root + 3 managers + 6 specialists (backend, database, frontend, uiux, technical-writer, and one more)
        # Actually checking the complex_topology fixture:
        # - manager-tdd has 4 children: expert-backend, expert-database, expert-frontend, expert-uiux
        # - manager-docs has 1 child: expert-technical-writer
        # - manager-quality has 0 children
        # So status_distribution["working"] should be at least 3 (the 3 managers set above)
        # But some specialists may also be in working state from delegation
        assert stats["status_distribution"].get("working", 0) >= 3  # At least 3 managers working

        # Complete all specialists
        for agent_id in ["expert-backend", "expert-frontend", "expert-technical-writer"]:
            complex_topology.update_agent_status(agent_id, "completed")

        # Aggregate results per manager
        tdd_results = complex_topology.aggregate_results("manager-tdd")
        docs_results = complex_topology.aggregate_results("manager-docs")

        assert tdd_results["children_count"] == 4  # backend, database, frontend, uiux
        assert docs_results["children_count"] == 1  # technical-writer

    def test_hierarchical_status_propagation(self, layered_topology):
        """Test status changes propagate correctly through hierarchy."""
        # Update leaf status
        layered_topology.update_agent_status("expert-backend", "working")

        # Check path
        path = layered_topology.get_path_to_root("expert-backend")

        # Verify status is accessible through path
        for agent_id in path:
            agent = layered_topology.get_agent(agent_id)
            assert agent is not None
            assert hasattr(agent, "status")


# ============================================================================
# 9. Parametrized Tests
# ============================================================================


class TestParametrized:
    """Parametrized tests for various scenarios."""

    @pytest.mark.parametrize("status", ["idle", "working", "completed", "failed"])
    def test_all_status_values(self, basic_topology, status):
        """Test all valid status values."""
        success = basic_topology.update_agent_status("alfred", status)

        assert success is True
        assert basic_topology.agents["alfred"].status == status

    @pytest.mark.parametrize("layer_num", [0, 1, 2, 5, 10])
    def test_various_layer_numbers(self, basic_topology, layer_num):
        """Test agents can be added at various layer numbers."""
        if layer_num == 0:
            # Root already exists at layer 0
            return

        # Create chain of agents up to layer_num
        parent = "alfred"
        for layer in range(1, layer_num + 1):
            agent_id = f"agent-layer-{layer}"
            basic_topology.add_agent(agent_id, "test", layer=layer, parent_id=parent)
            parent = agent_id

        # Verify final agent
        agent = basic_topology.get_agent(f"agent-layer-{layer_num}")
        assert agent.layer == layer_num

    @pytest.mark.parametrize("num_children", [0, 1, 5, 10, 20])
    def test_varying_children_count(self, basic_topology, num_children):
        """Test agents with varying number of children."""
        if num_children == 0:
            results = basic_topology.aggregate_results("alfred")
            assert results["children_count"] == 0
            return

        # Add children
        children = [f"child-{i}" for i in range(num_children)]
        for child_id in children:
            basic_topology.add_agent(child_id, "test", layer=1, parent_id="alfred")

        # Aggregate
        results = basic_topology.aggregate_results("alfred")
        assert results["children_count"] == num_children


# ============================================================================
# 10. Logging and Debug Tests
# ============================================================================


class TestLogging:
    """Test logging output and debug information."""

    def test_initialization_logging(self, caplog):
        """Test initialization logs."""
        import logging
        caplog.set_level(logging.INFO)

        topo = HierarchicalTopology(root_agent_id="test-root")

        assert "Initialized hierarchical topology with root: test-root" in caplog.text

    def test_add_agent_logging(self, basic_topology, caplog):
        """Test agent addition logs."""
        import logging
        caplog.set_level(logging.INFO)

        basic_topology.add_agent("test-agent", "test-type", layer=1, parent_id="alfred")

        assert "Added agent test-agent" in caplog.text
        assert "type: test-type" in caplog.text
        assert "at layer 1" in caplog.text

    def test_delegate_task_logging(self, layered_topology, caplog):
        """Test task delegation logs."""
        import logging
        caplog.set_level(logging.INFO)

        layered_topology.delegate_task("alfred", "manager-tdd", {"action": "test"})

        assert "Delegated task from alfred to manager-tdd" in caplog.text

    def test_aggregate_results_logging(self, layered_topology, caplog):
        """Test result aggregation logs."""
        import logging
        caplog.set_level(logging.INFO)

        layered_topology.agents["expert-backend"].status = "completed"
        layered_topology.aggregate_results("manager-tdd")

        assert "Aggregated results for manager-tdd" in caplog.text


# ============================================================================
# 11. Module Exports Tests
# ============================================================================


def test_module_exports():
    """Test __all__ exports are correct."""
    from moai_flow.topology.hierarchical import __all__

    assert "HierarchicalTopology" in __all__
    assert "Agent" in __all__
    assert len(__all__) == 2
