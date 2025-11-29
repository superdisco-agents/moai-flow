#!/usr/bin/env python3
"""
Comprehensive Test Suite for RingTopology

Tests circular ring topology with sequential agent chains,
token passing, message routing, and ring manipulation operations.

Coverage Requirements:
- Ring Management: add/remove agents, size tracking, position tracking
- Token Passing: clockwise/counterclockwise, rotation, holder tracking
- Message Routing: path tracking, circular routes, shortest paths
- Ring Manipulation: rotation, neighbor queries, reordering
- Helper Functions: factory functions, position lookup

Target: 90%+ coverage with 35+ test cases
"""

import pytest
from typing import Dict, Any, List

from moai_flow.topology.ring import (
    RingTopology,
    RingAgent,
    create_ring_from_agents
)


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def empty_ring():
    """Create empty ring topology."""
    return RingTopology()


@pytest.fixture
def small_ring():
    """Create ring with 3 agents."""
    ring = RingTopology()
    ring.add_agent("agent-1", "expert-backend")
    ring.add_agent("agent-2", "expert-frontend")
    ring.add_agent("agent-3", "expert-database")
    return ring


@pytest.fixture
def large_ring():
    """Create ring with 10 agents for complex routing tests."""
    ring = RingTopology()
    for i in range(1, 11):
        ring.add_agent(f"agent-{i}", f"expert-type-{i % 3}")
    return ring


@pytest.fixture
def agent_configs():
    """Sample agent configurations for factory function tests."""
    return [
        {"agent_id": "backend-1", "agent_type": "expert-backend", "metadata": {"priority": 1}},
        {"agent_id": "frontend-1", "agent_type": "expert-frontend", "metadata": {"priority": 2}},
        {"agent_id": "database-1", "agent_type": "expert-database", "metadata": {"priority": 3}},
    ]


# ============================================================================
# 1. Ring Management Tests
# ============================================================================

class TestRingManagement:
    """Test ring creation, agent addition/removal, and size tracking."""

    def test_add_agent_to_ring(self, empty_ring):
        """Test adding single agent to empty ring."""
        # Act
        result = empty_ring.add_agent("agent-1", "expert-backend")

        # Assert
        assert result is True
        assert empty_ring.get_ring_size() == 1
        assert "agent-1" in empty_ring.agent_index
        assert empty_ring.agents[0].agent_id == "agent-1"
        assert empty_ring.agents[0].agent_type == "expert-backend"
        assert empty_ring.agents[0].position == 0

    def test_add_agent_with_metadata(self, empty_ring):
        """Test adding agent with metadata."""
        # Arrange
        metadata = {"priority": 5, "region": "us-west"}

        # Act
        empty_ring.add_agent("agent-1", "expert-backend", metadata=metadata)

        # Assert
        assert empty_ring.agents[0].metadata == metadata

    def test_add_agent_at_specific_position(self, small_ring):
        """Test inserting agent at specific position."""
        # Act
        result = small_ring.add_agent("agent-0", "expert-devops", position=0)

        # Assert
        assert result is True
        assert small_ring.get_ring_size() == 4
        assert small_ring.agents[0].agent_id == "agent-0"
        assert small_ring.agents[1].agent_id == "agent-1"

    def test_add_agent_at_middle_position(self, small_ring):
        """Test inserting agent at middle position."""
        # Act
        result = small_ring.add_agent("agent-mid", "expert-security", position=1)

        # Assert
        assert result is True
        assert small_ring.agents[0].agent_id == "agent-1"
        assert small_ring.agents[1].agent_id == "agent-mid"
        assert small_ring.agents[2].agent_id == "agent-2"

    def test_add_duplicate_agent_fails(self, small_ring):
        """Test adding agent with duplicate ID fails."""
        # Act
        result = small_ring.add_agent("agent-1", "expert-backend")

        # Assert
        assert result is False
        assert small_ring.get_ring_size() == 3

    def test_add_agent_sets_token_holder_for_first_agent(self, empty_ring):
        """Test first agent becomes token holder."""
        # Act
        empty_ring.add_agent("agent-1", "expert-backend")

        # Assert
        assert empty_ring.get_token_holder() == "agent-1"

    def test_remove_agent_from_ring(self, small_ring):
        """Test removing agent from ring."""
        # Act
        result = small_ring.remove_agent("agent-2")

        # Assert
        assert result is True
        assert small_ring.get_ring_size() == 2
        assert "agent-2" not in small_ring.agent_index
        assert small_ring.agents[0].agent_id == "agent-1"
        assert small_ring.agents[1].agent_id == "agent-3"

    def test_remove_nonexistent_agent_fails(self, small_ring):
        """Test removing non-existent agent fails."""
        # Act
        result = small_ring.remove_agent("agent-99")

        # Assert
        assert result is False
        assert small_ring.get_ring_size() == 3

    def test_remove_agent_transfers_token(self, small_ring):
        """Test removing token holder transfers token to next agent."""
        # Arrange
        assert small_ring.get_token_holder() == "agent-1"

        # Act
        small_ring.remove_agent("agent-1")

        # Assert
        assert small_ring.get_token_holder() == "agent-2"

    def test_remove_last_agent_clears_token(self, empty_ring):
        """Test removing last agent clears token holder."""
        # Arrange
        empty_ring.add_agent("agent-1", "expert-backend")

        # Act
        empty_ring.remove_agent("agent-1")

        # Assert
        assert empty_ring.get_token_holder() is None
        assert empty_ring.get_ring_size() == 0

    def test_get_ring_size(self, small_ring):
        """Test getting ring size."""
        # Assert
        assert small_ring.get_ring_size() == 3

        # Act
        small_ring.add_agent("agent-4", "expert-devops")

        # Assert
        assert small_ring.get_ring_size() == 4

    def test_agent_position_tracking(self, small_ring):
        """Test agent positions are tracked correctly."""
        # Assert
        assert small_ring.agent_index["agent-1"] == 0
        assert small_ring.agent_index["agent-2"] == 1
        assert small_ring.agent_index["agent-3"] == 2

        # Verify position attribute
        assert small_ring.agents[0].position == 0
        assert small_ring.agents[1].position == 1
        assert small_ring.agents[2].position == 2


# ============================================================================
# 2. Token Passing Tests
# ============================================================================

class TestTokenPassing:
    """Test token passing mechanisms and rotation."""

    def test_pass_token_clockwise(self, small_ring):
        """Test passing token clockwise to next agent."""
        # Act
        next_holder = small_ring.pass_token("agent-1", to_next=True)

        # Assert
        assert next_holder == "agent-2"
        assert small_ring.get_token_holder() == "agent-2"

    def test_pass_token_counterclockwise(self, small_ring):
        """Test passing token counterclockwise to previous agent."""
        # Act
        next_holder = small_ring.pass_token("agent-1", to_next=False)

        # Assert
        assert next_holder == "agent-3"  # Wraps around to last agent
        assert small_ring.get_token_holder() == "agent-3"

    def test_pass_token_multiple_steps(self, small_ring):
        """Test passing token multiple steps."""
        # Act
        next_holder = small_ring.pass_token("agent-1", to_next=True, steps=2)

        # Assert
        assert next_holder == "agent-3"
        assert small_ring.get_token_holder() == "agent-3"

    def test_pass_token_wraps_around(self, small_ring):
        """Test token passing wraps around ring."""
        # Arrange
        small_ring.pass_token("agent-1")  # → agent-2
        small_ring.pass_token("agent-2")  # → agent-3

        # Act
        next_holder = small_ring.pass_token("agent-3")  # Should wrap to agent-1

        # Assert
        assert next_holder == "agent-1"
        assert small_ring.get_token_holder() == "agent-1"

    def test_pass_token_full_rotation(self, small_ring):
        """Test token completes full rotation around ring."""
        # Act & Assert - Complete one full rotation
        holders = ["agent-1"]  # Start position

        next_holder = small_ring.pass_token("agent-1")
        assert next_holder == "agent-2"
        holders.append(next_holder)

        next_holder = small_ring.pass_token("agent-2")
        assert next_holder == "agent-3"
        holders.append(next_holder)

        next_holder = small_ring.pass_token("agent-3")
        assert next_holder == "agent-1"  # Back to start
        holders.append(next_holder)

        # Verify full rotation
        assert holders == ["agent-1", "agent-2", "agent-3", "agent-1"]

    def test_pass_token_from_wrong_holder_fails(self, small_ring):
        """Test passing token from non-holder fails."""
        # Arrange
        assert small_ring.get_token_holder() == "agent-1"

        # Act
        result = small_ring.pass_token("agent-2")  # agent-2 doesn't hold token

        # Assert
        assert result is None
        assert small_ring.get_token_holder() == "agent-1"  # Token unchanged

    def test_pass_token_from_nonexistent_agent_fails(self, small_ring):
        """Test passing token from non-existent agent fails."""
        # Act
        result = small_ring.pass_token("agent-99")

        # Assert
        assert result is None

    def test_pass_token_in_empty_ring_fails(self, empty_ring):
        """Test passing token in empty ring fails."""
        # Act
        result = empty_ring.pass_token("agent-1")

        # Assert
        assert result is None

    def test_get_current_token_holder(self, small_ring):
        """Test getting current token holder."""
        # Assert
        assert small_ring.get_token_holder() == "agent-1"

        # Act
        small_ring.pass_token("agent-1")

        # Assert
        assert small_ring.get_token_holder() == "agent-2"


# ============================================================================
# 3. Message Routing Tests
# ============================================================================

class TestMessageRouting:
    """Test message routing and path tracking."""

    def test_send_message_along_ring(self, small_ring):
        """Test sending message from one agent to another."""
        # Arrange
        message = {"task": "process_data", "priority": 1}

        # Act
        path = small_ring.send_message("agent-1", "agent-3", message, clockwise=True)

        # Assert
        assert path == ["agent-1", "agent-2", "agent-3"]

    def test_send_message_clockwise(self, small_ring):
        """Test message routing clockwise."""
        # Arrange
        message = {"type": "request"}

        # Act
        path = small_ring.send_message("agent-1", "agent-2", message, clockwise=True)

        # Assert
        assert path == ["agent-1", "agent-2"]

    def test_send_message_counterclockwise(self, small_ring):
        """Test message routing counterclockwise."""
        # Arrange
        message = {"type": "response"}

        # Act
        path = small_ring.send_message("agent-1", "agent-3", message, clockwise=False)

        # Assert
        assert path == ["agent-1", "agent-3"]  # Direct path counterclockwise

    def test_message_path_tracking(self, small_ring):
        """Test message paths are logged."""
        # Arrange
        message = {"data": "test"}

        # Act
        small_ring.send_message("agent-1", "agent-3", message, clockwise=True)

        # Assert
        assert len(small_ring.message_log) == 1
        log_entry = small_ring.message_log[0]
        assert log_entry["from"] == "agent-1"
        assert log_entry["to"] == "agent-3"
        assert log_entry["path"] == ["agent-1", "agent-2", "agent-3"]
        assert log_entry["direction"] == "clockwise"
        assert log_entry["message"] == message

    def test_send_message_to_self(self, small_ring):
        """Test sending message to same agent."""
        # Arrange
        message = {"type": "self-message"}

        # Act
        path = small_ring.send_message("agent-2", "agent-2", message, clockwise=True)

        # Assert
        assert path == ["agent-2"]

    def test_send_message_full_circle(self, small_ring):
        """Test message sent full circle around ring."""
        # Arrange
        message = {"broadcast": True}

        # Act
        path = small_ring.send_message("agent-2", "agent-1", message, clockwise=True)

        # Assert
        assert path == ["agent-2", "agent-3", "agent-1"]

    def test_send_message_from_nonexistent_sender_fails(self, small_ring):
        """Test sending message from non-existent sender fails."""
        # Act
        path = small_ring.send_message("agent-99", "agent-1", {})

        # Assert
        assert path is None

    def test_send_message_to_nonexistent_recipient_fails(self, small_ring):
        """Test sending message to non-existent recipient fails."""
        # Act
        path = small_ring.send_message("agent-1", "agent-99", {})

        # Assert
        assert path is None

    def test_send_message_shortest_path_selection(self, large_ring):
        """Test message routing uses specified direction."""
        # Arrange
        message = {"data": "test"}

        # Act - Clockwise from agent-1 to agent-5
        clockwise_path = large_ring.send_message("agent-1", "agent-5", message, clockwise=True)

        # Act - Counterclockwise from agent-1 to agent-5
        counterclockwise_path = large_ring.send_message("agent-1", "agent-5", message, clockwise=False)

        # Assert
        assert len(clockwise_path) == 5  # agent-1 → agent-2 → agent-3 → agent-4 → agent-5
        assert len(counterclockwise_path) == 7  # Longer path going backwards


# ============================================================================
# 4. Ring Manipulation Tests
# ============================================================================

class TestRingManipulation:
    """Test ring rotation, reordering, and neighbor queries."""

    def test_rotate_ring_positive(self, small_ring):
        """Test rotating ring clockwise."""
        # Arrange
        original_first = small_ring.agents[0].agent_id

        # Act
        small_ring.rotate_ring(positions=1)

        # Assert
        assert small_ring.agents[0].agent_id == "agent-2"
        assert small_ring.agents[1].agent_id == "agent-3"
        assert small_ring.agents[2].agent_id == "agent-1"

    def test_rotate_ring_negative(self, small_ring):
        """Test rotating ring counterclockwise."""
        # Act
        small_ring.rotate_ring(positions=-1)

        # Assert
        assert small_ring.agents[0].agent_id == "agent-3"
        assert small_ring.agents[1].agent_id == "agent-1"
        assert small_ring.agents[2].agent_id == "agent-2"

    def test_rotate_ring_multiple_positions(self, small_ring):
        """Test rotating ring multiple positions."""
        # Act
        small_ring.rotate_ring(positions=2)

        # Assert
        assert small_ring.agents[0].agent_id == "agent-3"

    def test_rotate_ring_full_rotation(self, small_ring):
        """Test rotating ring by full ring size returns to original."""
        # Arrange
        original_order = [agent.agent_id for agent in small_ring.agents]

        # Act
        small_ring.rotate_ring(positions=3)  # Full rotation for 3 agents

        # Assert
        current_order = [agent.agent_id for agent in small_ring.agents]
        assert current_order == original_order

    def test_rotate_empty_ring(self, empty_ring):
        """Test rotating empty ring does nothing."""
        # Act
        empty_ring.rotate_ring(positions=1)

        # Assert
        assert empty_ring.get_ring_size() == 0

    def test_get_neighbors(self, small_ring):
        """Test getting previous and next neighbors."""
        # Act
        prev, next_agent = small_ring.get_neighbors("agent-2")

        # Assert
        assert prev == "agent-1"
        assert next_agent == "agent-3"

    def test_get_neighbors_first_agent(self, small_ring):
        """Test neighbors of first agent wrap around."""
        # Act
        prev, next_agent = small_ring.get_neighbors("agent-1")

        # Assert
        assert prev == "agent-3"  # Wraps to last
        assert next_agent == "agent-2"

    def test_get_neighbors_last_agent(self, small_ring):
        """Test neighbors of last agent wrap around."""
        # Act
        prev, next_agent = small_ring.get_neighbors("agent-3")

        # Assert
        assert prev == "agent-2"
        assert next_agent == "agent-1"  # Wraps to first

    def test_get_neighbors_single_agent_ring(self, empty_ring):
        """Test neighbors of single agent in ring are itself."""
        # Arrange
        empty_ring.add_agent("agent-1", "expert-backend")

        # Act
        prev, next_agent = empty_ring.get_neighbors("agent-1")

        # Assert
        assert prev == "agent-1"
        assert next_agent == "agent-1"

    def test_get_neighbors_nonexistent_agent(self, small_ring):
        """Test getting neighbors of non-existent agent returns None."""
        # Act
        prev, next_agent = small_ring.get_neighbors("agent-99")

        # Assert
        assert prev is None
        assert next_agent is None

    def test_reorder_ring_via_rotation(self, small_ring):
        """Test reordering ring by combining rotation and add/remove."""
        # Arrange
        original_size = small_ring.get_ring_size()

        # Act - Remove agent, rotate, re-add
        small_ring.remove_agent("agent-2")
        small_ring.rotate_ring(1)
        small_ring.add_agent("agent-2", "expert-frontend")

        # Assert
        assert small_ring.get_ring_size() == original_size


# ============================================================================
# 5. Helper Functions Tests
# ============================================================================

class TestHelperFunctions:
    """Test utility and helper functions."""

    def test_create_ring_from_agents(self, agent_configs):
        """Test creating ring from agent configurations."""
        # Act
        ring = create_ring_from_agents(agent_configs)

        # Assert
        assert ring.get_ring_size() == 3
        assert ring.agents[0].agent_id == "backend-1"
        assert ring.agents[1].agent_id == "frontend-1"
        assert ring.agents[2].agent_id == "database-1"

    def test_create_ring_from_agents_preserves_metadata(self, agent_configs):
        """Test factory function preserves agent metadata."""
        # Act
        ring = create_ring_from_agents(agent_configs)

        # Assert
        assert ring.agents[0].metadata["priority"] == 1
        assert ring.agents[1].metadata["priority"] == 2
        assert ring.agents[2].metadata["priority"] == 3

    def test_create_ring_from_empty_configs(self):
        """Test creating ring from empty configuration list."""
        # Act
        ring = create_ring_from_agents([])

        # Assert
        assert ring.get_ring_size() == 0

    def test_find_agent_position(self, small_ring):
        """Test finding agent position in ring."""
        # Act
        position = small_ring.agent_index.get("agent-2")

        # Assert
        assert position == 1

    def test_find_nonexistent_agent_position(self, small_ring):
        """Test finding non-existent agent returns None."""
        # Act
        position = small_ring.agent_index.get("agent-99")

        # Assert
        assert position is None


# ============================================================================
# 6. Agent Status Management Tests
# ============================================================================

class TestAgentStatus:
    """Test agent status tracking and management."""

    def test_get_agent_status(self, small_ring):
        """Test getting agent status."""
        # Act
        status = small_ring.get_agent_status("agent-1")

        # Assert
        assert status == "idle"

    def test_set_agent_status(self, small_ring):
        """Test setting agent status."""
        # Act
        result = small_ring.set_agent_status("agent-1", "working")

        # Assert
        assert result is True
        assert small_ring.get_agent_status("agent-1") == "working"

    def test_set_agent_status_nonexistent_agent(self, small_ring):
        """Test setting status for non-existent agent fails."""
        # Act
        result = small_ring.set_agent_status("agent-99", "working")

        # Assert
        assert result is False

    def test_get_agent_status_nonexistent_agent(self, small_ring):
        """Test getting status of non-existent agent returns None."""
        # Act
        status = small_ring.get_agent_status("agent-99")

        # Assert
        assert status is None


# ============================================================================
# 7. Statistics and Visualization Tests
# ============================================================================

class TestStatisticsAndVisualization:
    """Test statistics gathering and visualization."""

    def test_get_statistics(self, small_ring):
        """Test getting ring statistics."""
        # Act
        stats = small_ring.get_statistics()

        # Assert
        assert stats["ring_size"] == 3
        assert stats["token_holder"] == "agent-1"
        assert stats["message_count"] == 0
        assert "idle" in stats["status_distribution"]

    def test_get_statistics_with_messages(self, small_ring):
        """Test statistics include message count."""
        # Arrange
        small_ring.send_message("agent-1", "agent-2", {"test": "msg"})
        small_ring.send_message("agent-2", "agent-3", {"test": "msg2"})

        # Act
        stats = small_ring.get_statistics()

        # Assert
        assert stats["message_count"] == 2

    def test_visualize_small_ring(self, small_ring):
        """Test visualization of small ring."""
        # Act
        viz = small_ring.visualize()

        # Assert
        assert "Ring Topology Visualization" in viz
        assert "agent-1" in viz
        assert "agent-2" in viz
        assert "agent-3" in viz
        assert "[TOKEN]" in viz  # Token holder indicator

    def test_visualize_empty_ring(self, empty_ring):
        """Test visualization of empty ring."""
        # Act
        viz = empty_ring.visualize()

        # Assert
        assert viz == "Empty ring"

    def test_visualize_large_ring(self, large_ring):
        """Test visualization of large ring shows summary."""
        # Act
        viz = large_ring.visualize()

        # Assert
        assert "Large Ring" in viz or "agent-1" in viz


# ============================================================================
# 8. Ring Agent Data Class Tests
# ============================================================================

class TestRingAgentDataClass:
    """Test RingAgent dataclass functionality."""

    def test_ring_agent_creation(self):
        """Test creating RingAgent instance."""
        # Act
        agent = RingAgent(
            agent_id="test-1",
            agent_type="expert-backend",
            position=0,
            status="working",
            metadata={"key": "value"}
        )

        # Assert
        assert agent.agent_id == "test-1"
        assert agent.agent_type == "expert-backend"
        assert agent.position == 0
        assert agent.status == "working"
        assert agent.metadata == {"key": "value"}

    def test_ring_agent_hashable(self):
        """Test RingAgent is hashable for set operations."""
        # Arrange
        agent1 = RingAgent(agent_id="agent-1", agent_type="type-1", position=0)
        agent2 = RingAgent(agent_id="agent-2", agent_type="type-2", position=1)

        # Act
        agent_set = {agent1, agent2}

        # Assert
        assert len(agent_set) == 2
        assert agent1 in agent_set

    def test_ring_agent_default_values(self):
        """Test RingAgent default values."""
        # Act
        agent = RingAgent(
            agent_id="test-1",
            agent_type="expert-backend",
            position=0
        )

        # Assert
        assert agent.status == "idle"
        assert agent.metadata == {}


# ============================================================================
# 9. Edge Cases and Error Handling Tests
# ============================================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_pass_token_with_zero_steps(self, small_ring):
        """Test passing token with zero steps keeps current holder."""
        # Act
        result = small_ring.pass_token("agent-1", steps=0)

        # Assert
        assert result == "agent-1"
        assert small_ring.get_token_holder() == "agent-1"

    def test_add_agent_with_large_position(self, small_ring):
        """Test adding agent with position > ring size appends to end."""
        # Act
        small_ring.add_agent("agent-4", "expert-devops", position=100)

        # Assert
        assert small_ring.agents[-1].agent_id == "agent-4"

    def test_send_message_in_single_agent_ring(self, empty_ring):
        """Test sending message in single-agent ring."""
        # Arrange
        empty_ring.add_agent("agent-1", "expert-backend")

        # Act
        path = empty_ring.send_message("agent-1", "agent-1", {"msg": "test"})

        # Assert
        assert path == ["agent-1"]

    def test_circular_invariant_maintained(self, small_ring):
        """Test ring maintains circular invariant after operations."""
        # Act - Perform various operations
        small_ring.add_agent("agent-4", "expert-devops")
        small_ring.remove_agent("agent-2")
        small_ring.rotate_ring(1)

        # Assert - Verify circular invariant
        for agent_id in [agent.agent_id for agent in small_ring.agents]:
            prev, next_agent = small_ring.get_neighbors(agent_id)
            assert prev is not None
            assert next_agent is not None
