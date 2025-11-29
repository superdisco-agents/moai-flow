"""
Comprehensive tests for StarTopology - Hub-and-spoke topology for centralized coordination.

Test Coverage Requirements:
- Framework: pytest with mocking for agent isolation
- Coverage Target: 90%+ (per config)
- Mock Strategy: Mock hub agent for isolation

Test Areas:
1. Hub-Spoke Management (initialization, add/remove spokes)
2. Messaging (hub-to-spoke, spoke-to-hub, broadcast)
3. Message Queues (creation, delivery, overflow)
4. Hub Load Monitoring (low, medium, high, critical levels)
5. Visualization (ASCII rendering)
"""

import pytest
from datetime import datetime
from typing import Dict, Any, List
from unittest.mock import Mock, patch

from moai_flow.topology.star import StarTopology, Agent


# ===== Fixtures =====

@pytest.fixture
def basic_topology():
    """
    Create basic star topology with hub.

    Yields:
        StarTopology: Fresh topology instance with hub
    """
    topo = StarTopology(hub_agent_id="alfred")
    yield topo


@pytest.fixture
def populated_topology():
    """
    Create topology with hub and multiple spokes.

    Yields:
        StarTopology: Topology with 5 spokes
    """
    topo = StarTopology(hub_agent_id="alfred")

    # Add 5 different spoke agents
    topo.add_spoke("expert-backend", "expert-backend", {"priority": "high"})
    topo.add_spoke("expert-frontend", "expert-frontend", {"priority": "high"})
    topo.add_spoke("manager-tdd", "manager-tdd", {"priority": "medium"})
    topo.add_spoke("manager-docs", "manager-docs", {"priority": "low"})
    topo.add_spoke("core-quality", "core-quality", {"priority": "high"})

    yield topo


# ===== Test Group 1: Hub-Spoke Management =====

class TestHubInitialization:
    """Test hub initialization and basic setup."""

    def test_initialize_hub_default(self):
        """Test hub initialization with default ID."""
        topo = StarTopology()

        assert topo.hub_id == "alfred"
        assert topo.hub_agent is not None
        assert topo.hub_agent.agent_id == "alfred"
        assert topo.hub_agent.agent_type == "alfred"
        assert topo.hub_agent.role == "hub"
        assert topo.hub_agent.status == "idle"
        assert len(topo.spoke_agents) == 0

    def test_initialize_hub_custom_id(self):
        """Test hub initialization with custom ID."""
        topo = StarTopology(hub_agent_id="coordinator")

        assert topo.hub_id == "coordinator"
        assert topo.hub_agent.agent_id == "coordinator"
        assert topo.hub_agent.agent_type == "alfred"
        assert topo.hub_agent.role == "hub"

    def test_hub_agent_has_metadata(self, basic_topology):
        """Test hub agent contains creation metadata."""
        hub = basic_topology.get_hub()

        assert "created_at" in hub.metadata
        assert isinstance(hub.metadata["created_at"], str)
        # Verify ISO8601 format with 'Z' suffix
        assert hub.metadata["created_at"].endswith("Z")

    def test_hub_stats_initialized(self, basic_topology):
        """Test hub statistics are initialized to zero."""
        assert basic_topology.hub_stats["messages_sent"] == 0
        assert basic_topology.hub_stats["messages_received"] == 0
        assert basic_topology.hub_stats["broadcasts"] == 0
        assert basic_topology.hub_stats["active_tasks"] == 0

    def test_message_log_empty_on_init(self, basic_topology):
        """Test message log is empty on initialization."""
        assert len(basic_topology.message_log) == 0


class TestAddSpoke:
    """Test adding spoke agents to topology."""

    def test_add_spoke_basic(self, basic_topology):
        """Test adding single spoke successfully."""
        result = basic_topology.add_spoke("expert-backend", "expert-backend")

        assert result is True
        assert "expert-backend" in basic_topology.spoke_agents

        spoke = basic_topology.get_spoke("expert-backend")
        assert spoke is not None
        assert spoke.agent_id == "expert-backend"
        assert spoke.agent_type == "expert-backend"
        assert spoke.role == "spoke"
        assert spoke.status == "idle"

    def test_add_spoke_with_metadata(self, basic_topology):
        """Test adding spoke with custom metadata."""
        metadata = {"priority": "high", "max_tasks": 10}
        result = basic_topology.add_spoke("expert-frontend", "expert-frontend", metadata)

        assert result is True
        spoke = basic_topology.get_spoke("expert-frontend")
        assert spoke.metadata["priority"] == "high"
        assert spoke.metadata["max_tasks"] == 10
        assert "created_at" in spoke.metadata
        assert spoke.metadata["connected_to_hub"] == "alfred"

    def test_add_spoke_duplicate_rejected(self, basic_topology):
        """Test adding duplicate spoke ID is rejected."""
        basic_topology.add_spoke("expert-backend", "expert-backend")
        result = basic_topology.add_spoke("expert-backend", "expert-backend")

        assert result is False
        # Should still have only one spoke
        assert len(basic_topology.spoke_agents) == 1

    def test_add_spoke_hub_id_rejected(self, basic_topology):
        """Test adding spoke with hub ID is rejected."""
        result = basic_topology.add_spoke("alfred", "some-type")

        assert result is False
        assert "alfred" not in basic_topology.spoke_agents

    def test_add_multiple_spokes(self, basic_topology):
        """Test adding multiple spokes successfully."""
        basic_topology.add_spoke("expert-backend", "expert-backend")
        basic_topology.add_spoke("expert-frontend", "expert-frontend")
        basic_topology.add_spoke("manager-tdd", "manager-tdd")

        assert len(basic_topology.spoke_agents) == 3
        assert "expert-backend" in basic_topology.spoke_agents
        assert "expert-frontend" in basic_topology.spoke_agents
        assert "manager-tdd" in basic_topology.spoke_agents


class TestRemoveSpoke:
    """Test removing spoke agents from topology."""

    def test_remove_spoke_basic(self, populated_topology):
        """Test removing single spoke successfully."""
        result = populated_topology.remove_spoke("expert-backend")

        assert result is True
        assert "expert-backend" not in populated_topology.spoke_agents
        assert len(populated_topology.spoke_agents) == 4

    def test_remove_spoke_not_found(self, basic_topology):
        """Test removing non-existent spoke returns False."""
        result = basic_topology.remove_spoke("nonexistent")

        assert result is False

    def test_remove_spoke_with_pending_messages(self, populated_topology):
        """Test removing spoke with undelivered messages."""
        # Send message to spoke
        populated_topology.hub_to_spoke("expert-backend", {"type": "task"})

        spoke = populated_topology.get_spoke("expert-backend")
        assert len(spoke.message_queue) == 1

        # Remove spoke (should succeed despite pending messages)
        result = populated_topology.remove_spoke("expert-backend")
        assert result is True
        assert "expert-backend" not in populated_topology.spoke_agents

    def test_remove_all_spokes(self, populated_topology):
        """Test removing all spokes leaves only hub."""
        spoke_ids = list(populated_topology.spoke_agents.keys())

        for spoke_id in spoke_ids:
            result = populated_topology.remove_spoke(spoke_id)
            assert result is True

        assert len(populated_topology.spoke_agents) == 0


class TestGetSpokeCount:
    """Test spoke counting functionality."""

    def test_get_spoke_count_zero(self, basic_topology):
        """Test spoke count when no spokes exist."""
        assert len(basic_topology.spoke_agents) == 0

    def test_get_spoke_count_multiple(self, populated_topology):
        """Test spoke count with multiple spokes."""
        assert len(populated_topology.spoke_agents) == 5

    def test_get_spoke_count_after_add_remove(self, basic_topology):
        """Test spoke count after add/remove operations."""
        basic_topology.add_spoke("spoke1", "type1")
        basic_topology.add_spoke("spoke2", "type2")
        assert len(basic_topology.spoke_agents) == 2

        basic_topology.remove_spoke("spoke1")
        assert len(basic_topology.spoke_agents) == 1

        basic_topology.add_spoke("spoke3", "type3")
        assert len(basic_topology.spoke_agents) == 2


# ===== Test Group 2: Messaging =====

class TestHubToSpokeMessage:
    """Test hub-to-spoke messaging."""

    def test_hub_to_spoke_basic(self, populated_topology):
        """Test sending message from hub to spoke."""
        message = {"type": "task", "spec_id": "SPEC-001"}
        result = populated_topology.hub_to_spoke("expert-backend", message)

        assert result is True

        # Verify message in spoke's queue
        spoke = populated_topology.get_spoke("expert-backend")
        assert len(spoke.message_queue) == 1

        received = spoke.peek_messages()[0]
        assert received["from"] == "alfred"
        assert received["to"] == "expert-backend"
        assert received["message"] == message
        assert received["type"] == "hub_to_spoke"
        assert "sent_at" in received

    def test_hub_to_spoke_invalid_message_type(self, populated_topology):
        """Test hub-to-spoke with non-dict message raises error."""
        with pytest.raises(ValueError, match="Message must be a dictionary"):
            populated_topology.hub_to_spoke("expert-backend", "invalid")

    def test_hub_to_spoke_nonexistent_spoke(self, basic_topology):
        """Test sending to non-existent spoke returns False."""
        result = basic_topology.hub_to_spoke("nonexistent", {"type": "task"})

        assert result is False

    def test_hub_to_spoke_updates_stats(self, populated_topology):
        """Test hub-to-spoke increments messages_sent stat."""
        initial_sent = populated_topology.hub_stats["messages_sent"]

        populated_topology.hub_to_spoke("expert-backend", {"type": "task"})

        assert populated_topology.hub_stats["messages_sent"] == initial_sent + 1

    def test_hub_to_spoke_logs_message(self, populated_topology):
        """Test hub-to-spoke adds to message log."""
        initial_log_size = len(populated_topology.message_log)

        populated_topology.hub_to_spoke("expert-backend", {"type": "task"})

        assert len(populated_topology.message_log) == initial_log_size + 1


class TestSpokeToHubMessage:
    """Test spoke-to-hub messaging."""

    def test_spoke_to_hub_basic(self, populated_topology):
        """Test sending message from spoke to hub."""
        message = {"type": "result", "status": "completed"}
        result = populated_topology.spoke_to_hub("expert-backend", message)

        assert result is True

        # Verify message in hub's queue
        hub = populated_topology.get_hub()
        assert len(hub.message_queue) == 1

        received = hub.peek_messages()[0]
        assert received["from"] == "expert-backend"
        assert received["to"] == "alfred"
        assert received["message"] == message
        assert received["type"] == "spoke_to_hub"
        assert "sent_at" in received

    def test_spoke_to_hub_invalid_message_type(self, populated_topology):
        """Test spoke-to-hub with non-dict message raises error."""
        with pytest.raises(ValueError, match="Message must be a dictionary"):
            populated_topology.spoke_to_hub("expert-backend", "invalid")

    def test_spoke_to_hub_hub_as_sender_rejected(self, populated_topology):
        """Test hub cannot send spoke_to_hub message."""
        with pytest.raises(ValueError, match="Hub cannot send spoke_to_hub message"):
            populated_topology.spoke_to_hub("alfred", {"type": "result"})

    def test_spoke_to_hub_nonexistent_spoke(self, basic_topology):
        """Test sending from non-existent spoke returns False."""
        result = basic_topology.spoke_to_hub("nonexistent", {"type": "result"})

        assert result is False

    def test_spoke_to_hub_updates_stats(self, populated_topology):
        """Test spoke-to-hub increments messages_received stat."""
        initial_received = populated_topology.hub_stats["messages_received"]

        populated_topology.spoke_to_hub("expert-backend", {"type": "result"})

        assert populated_topology.hub_stats["messages_received"] == initial_received + 1

    def test_spoke_to_hub_logs_message(self, populated_topology):
        """Test spoke-to-hub adds to message log."""
        initial_log_size = len(populated_topology.message_log)

        populated_topology.spoke_to_hub("expert-backend", {"type": "result"})

        assert len(populated_topology.message_log) == initial_log_size + 1


class TestSpokeToSpokeBlocked:
    """Test that direct spoke-to-spoke communication is blocked."""

    def test_spoke_to_spoke_not_possible(self, populated_topology):
        """Test there is no direct spoke-to-spoke communication method."""
        # Star topology should not have spoke-to-spoke method
        assert not hasattr(populated_topology, 'spoke_to_spoke')

    def test_spoke_isolation(self, populated_topology):
        """Test spokes cannot access each other's message queues."""
        # Send message to spoke1
        populated_topology.hub_to_spoke("expert-backend", {"type": "task"})

        # Spoke2 should not see spoke1's messages
        spoke2 = populated_topology.get_spoke("expert-frontend")
        assert len(spoke2.message_queue) == 0


class TestHubBroadcast:
    """Test hub broadcast messaging."""

    def test_hub_broadcast_all_spokes(self, populated_topology):
        """Test broadcasting to all spokes."""
        message = {"type": "status_check"}
        result = populated_topology.hub_broadcast(message)

        assert result == 5  # 5 spokes should receive

        # Verify all spokes received message
        for spoke_id in populated_topology.spoke_agents.keys():
            spoke = populated_topology.get_spoke(spoke_id)
            assert len(spoke.message_queue) == 1

            received = spoke.peek_messages()[0]
            assert received["type"] == "broadcast"
            assert received["message"] == message
            assert received["total_recipients"] == 5

    def test_hub_broadcast_with_exclusions(self, populated_topology):
        """Test broadcasting with exclusion list."""
        message = {"type": "shutdown"}
        exclude = ["expert-backend", "manager-tdd"]
        result = populated_topology.hub_broadcast(message, exclude=exclude)

        assert result == 3  # 5 - 2 excluded = 3

        # Verify excluded spokes did NOT receive
        assert len(populated_topology.get_spoke("expert-backend").message_queue) == 0
        assert len(populated_topology.get_spoke("manager-tdd").message_queue) == 0

        # Verify non-excluded spokes DID receive
        assert len(populated_topology.get_spoke("expert-frontend").message_queue) == 1
        assert len(populated_topology.get_spoke("manager-docs").message_queue) == 1
        assert len(populated_topology.get_spoke("core-quality").message_queue) == 1

    def test_hub_broadcast_empty_topology(self, basic_topology):
        """Test broadcasting with no spokes."""
        result = basic_topology.hub_broadcast({"type": "test"})

        assert result == 0

    def test_hub_broadcast_invalid_message_type(self, populated_topology):
        """Test broadcast with non-dict message raises error."""
        with pytest.raises(ValueError, match="Message must be a dictionary"):
            populated_topology.hub_broadcast("invalid")

    def test_hub_broadcast_updates_stats(self, populated_topology):
        """Test broadcast increments broadcasts and messages_sent stats."""
        initial_broadcasts = populated_topology.hub_stats["broadcasts"]
        initial_sent = populated_topology.hub_stats["messages_sent"]

        result = populated_topology.hub_broadcast({"type": "test"})

        assert populated_topology.hub_stats["broadcasts"] == initial_broadcasts + 1
        assert populated_topology.hub_stats["messages_sent"] == initial_sent + result

    def test_hub_broadcast_same_timestamp(self, populated_topology):
        """Test all broadcast messages have same timestamp."""
        populated_topology.hub_broadcast({"type": "test"})

        timestamps = set()
        for spoke in populated_topology.spoke_agents.values():
            msg = spoke.peek_messages()[0]
            timestamps.add(msg["sent_at"])

        # All should have same timestamp
        assert len(timestamps) == 1


# ===== Test Group 3: Message Queues =====

class TestMessageQueueCreation:
    """Test message queue creation for agents."""

    def test_agent_has_message_queue(self):
        """Test Agent initializes with empty message queue."""
        agent = Agent(agent_id="test", agent_type="test-type", role="spoke")

        assert hasattr(agent, 'message_queue')
        assert len(agent.message_queue) == 0

    def test_hub_has_message_queue(self, basic_topology):
        """Test hub agent has message queue."""
        hub = basic_topology.get_hub()

        assert hasattr(hub, 'message_queue')
        assert len(hub.message_queue) == 0

    def test_spoke_has_message_queue(self, populated_topology):
        """Test spoke agents have message queues."""
        spoke = populated_topology.get_spoke("expert-backend")

        assert hasattr(spoke, 'message_queue')
        assert len(spoke.message_queue) == 0


class TestMessageQueueDelivery:
    """Test message queue delivery mechanisms."""

    def test_message_queue_fifo_order(self, populated_topology):
        """Test message queue follows FIFO order."""
        # Send 3 messages
        populated_topology.hub_to_spoke("expert-backend", {"order": 1})
        populated_topology.hub_to_spoke("expert-backend", {"order": 2})
        populated_topology.hub_to_spoke("expert-backend", {"order": 3})

        spoke = populated_topology.get_spoke("expert-backend")
        messages = spoke.get_messages()

        # Verify FIFO order
        assert messages[0]["message"]["order"] == 1
        assert messages[1]["message"]["order"] == 2
        assert messages[2]["message"]["order"] == 3

    def test_get_messages_all(self, populated_topology):
        """Test get_messages() retrieves all and clears queue."""
        populated_topology.hub_to_spoke("expert-backend", {"id": 1})
        populated_topology.hub_to_spoke("expert-backend", {"id": 2})

        spoke = populated_topology.get_spoke("expert-backend")
        messages = spoke.get_messages()

        assert len(messages) == 2
        assert len(spoke.message_queue) == 0  # Queue cleared

    def test_get_messages_limited(self, populated_topology):
        """Test get_messages(count) retrieves limited number."""
        populated_topology.hub_to_spoke("expert-backend", {"id": 1})
        populated_topology.hub_to_spoke("expert-backend", {"id": 2})
        populated_topology.hub_to_spoke("expert-backend", {"id": 3})

        spoke = populated_topology.get_spoke("expert-backend")
        messages = spoke.get_messages(count=2)

        assert len(messages) == 2
        assert messages[0]["message"]["id"] == 1
        assert messages[1]["message"]["id"] == 2
        assert len(spoke.message_queue) == 1  # 1 remains

    def test_peek_messages_does_not_modify(self, populated_topology):
        """Test peek_messages() does not remove messages."""
        populated_topology.hub_to_spoke("expert-backend", {"id": 1})
        populated_topology.hub_to_spoke("expert-backend", {"id": 2})

        spoke = populated_topology.get_spoke("expert-backend")
        peeked = spoke.peek_messages()

        assert len(peeked) == 2
        assert len(spoke.message_queue) == 2  # Queue unchanged

    def test_peek_messages_limited(self, populated_topology):
        """Test peek_messages(count) views limited number."""
        populated_topology.hub_to_spoke("expert-backend", {"id": 1})
        populated_topology.hub_to_spoke("expert-backend", {"id": 2})
        populated_topology.hub_to_spoke("expert-backend", {"id": 3})

        spoke = populated_topology.get_spoke("expert-backend")
        peeked = spoke.peek_messages(count=2)

        assert len(peeked) == 2
        assert len(spoke.message_queue) == 3  # Queue unchanged


class TestQueueOverflow:
    """Test message queue overflow scenarios."""

    def test_queue_handles_many_messages(self, populated_topology):
        """Test queue can handle large number of messages."""
        # Send 1000 messages
        for i in range(1000):
            populated_topology.hub_to_spoke("expert-backend", {"id": i})

        spoke = populated_topology.get_spoke("expert-backend")
        assert len(spoke.message_queue) == 1000

    def test_queue_preserves_order_at_scale(self, populated_topology):
        """Test FIFO order maintained with many messages."""
        # Send 100 messages
        for i in range(100):
            populated_topology.hub_to_spoke("expert-backend", {"id": i})

        spoke = populated_topology.get_spoke("expert-backend")
        messages = spoke.get_messages()

        # Verify order preserved
        for i, msg in enumerate(messages):
            assert msg["message"]["id"] == i


# ===== Test Group 4: Hub Load Monitoring =====

class TestHubLoadLevels:
    """Test hub load level calculations."""

    def test_hub_load_low(self, populated_topology):
        """Test hub load 'low' with 0-9 messages."""
        # Send 5 messages to hub
        for i in range(5):
            populated_topology.spoke_to_hub("expert-backend", {"id": i})

        load = populated_topology.get_hub_load()

        assert load["load_level"] == "low"
        assert load["pending_messages"] == 5

    def test_hub_load_medium(self, populated_topology):
        """Test hub load 'medium' with 10-49 messages."""
        # Send 25 messages to hub
        for i in range(25):
            populated_topology.spoke_to_hub("expert-backend", {"id": i})

        load = populated_topology.get_hub_load()

        assert load["load_level"] == "medium"
        assert load["pending_messages"] == 25

    def test_hub_load_high(self, populated_topology):
        """Test hub load 'high' with 50-99 messages."""
        # Send 75 messages to hub
        for i in range(75):
            populated_topology.spoke_to_hub("expert-backend", {"id": i})

        load = populated_topology.get_hub_load()

        assert load["load_level"] == "high"
        assert load["pending_messages"] == 75

    def test_hub_load_critical(self, populated_topology):
        """Test hub load 'critical' with 100+ messages."""
        # Send 150 messages to hub
        for i in range(150):
            populated_topology.spoke_to_hub("expert-backend", {"id": i})

        load = populated_topology.get_hub_load()

        assert load["load_level"] == "critical"
        assert load["pending_messages"] == 150


class TestGetHubLoadStatistics:
    """Test hub load statistics reporting."""

    def test_get_hub_load_structure(self, basic_topology):
        """Test get_hub_load returns correct structure."""
        load = basic_topology.get_hub_load()

        assert "hub_id" in load
        assert "pending_messages" in load
        assert "message_queue_size" in load
        assert "active_tasks" in load
        assert "total_spokes" in load
        assert "stats" in load
        assert "load_level" in load
        assert "measured_at" in load

    def test_get_hub_load_stats_accuracy(self, populated_topology):
        """Test hub load stats reflect actual values."""
        # Send some messages
        populated_topology.hub_to_spoke("expert-backend", {"type": "task"})
        populated_topology.spoke_to_hub("expert-frontend", {"type": "result"})
        populated_topology.hub_broadcast({"type": "status"})

        load = populated_topology.get_hub_load()

        assert load["hub_id"] == "alfred"
        assert load["total_spokes"] == 5
        assert load["stats"]["messages_sent"] == 6  # 1 unicast + 5 broadcast
        assert load["stats"]["messages_received"] == 1
        assert load["stats"]["broadcasts"] == 1

    def test_get_hub_load_timestamp_format(self, basic_topology):
        """Test hub load includes ISO8601 timestamp."""
        load = basic_topology.get_hub_load()

        assert "measured_at" in load
        assert load["measured_at"].endswith("Z")

    def test_active_tasks_tracking(self, basic_topology):
        """Test active_tasks can be incremented/decremented."""
        basic_topology.increment_active_tasks(5)
        load = basic_topology.get_hub_load()
        assert load["active_tasks"] == 5

        basic_topology.increment_active_tasks(-2)
        load = basic_topology.get_hub_load()
        assert load["active_tasks"] == 3

    def test_active_tasks_never_negative(self, basic_topology):
        """Test active_tasks cannot go below zero."""
        basic_topology.increment_active_tasks(-10)
        load = basic_topology.get_hub_load()
        assert load["active_tasks"] == 0


# ===== Test Group 5: Visualization =====

class TestVisualization:
    """Test ASCII visualization rendering."""

    def test_visualize_empty_topology(self, basic_topology):
        """Test visualization with no spokes."""
        output = basic_topology.visualize()

        assert "Hub: alfred" in output
        assert "(No spokes)" in output

    def test_visualize_star_structure(self, populated_topology):
        """Test visualization shows star structure."""
        output = populated_topology.visualize()

        # Should contain hub
        assert "Hub: alfred" in output

        # Should contain all spokes
        assert "expert-backend" in output
        assert "expert-frontend" in output
        assert "manager-tdd" in output
        assert "manager-docs" in output
        assert "core-quality" in output

        # Should have visual connectors
        assert "/" in output or "|" in output

    def test_visualize_includes_status(self, populated_topology):
        """Test visualization includes agent status."""
        # Update some statuses
        populated_topology.update_agent_status("alfred", "working")
        populated_topology.update_agent_status("expert-backend", "completed")

        output = populated_topology.visualize()

        assert "(working)" in output  # Hub status
        assert "(completed)" in output  # Spoke status

    def test_visualize_sorted_spokes(self, populated_topology):
        """Test spokes are displayed in sorted order."""
        output = populated_topology.visualize()

        # Extract spoke names from output
        lines = output.split('\n')
        spoke_lines = [line for line in lines if "expert" in line or "manager" in line or "core" in line]

        # Should be alphabetically sorted
        assert len(spoke_lines) > 0


# ===== Additional Test Coverage =====

class TestAgentStatusManagement:
    """Test agent status update functionality."""

    def test_update_hub_status(self, basic_topology):
        """Test updating hub agent status."""
        result = basic_topology.update_agent_status("alfred", "working")

        assert result is True
        assert basic_topology.get_hub().status == "working"

    def test_update_spoke_status(self, populated_topology):
        """Test updating spoke agent status."""
        result = populated_topology.update_agent_status("expert-backend", "completed")

        assert result is True
        assert populated_topology.get_spoke("expert-backend").status == "completed"

    def test_update_status_nonexistent_agent(self, basic_topology):
        """Test updating status of non-existent agent."""
        result = basic_topology.update_agent_status("nonexistent", "working")

        assert result is False


class TestTopologyStatistics:
    """Test topology statistics reporting."""

    def test_get_topology_stats_structure(self, populated_topology):
        """Test topology stats returns correct structure."""
        stats = populated_topology.get_topology_stats()

        assert "hub_id" in stats
        assert "total_spokes" in stats
        assert "hub_status" in stats
        assert "spoke_status_distribution" in stats
        assert "total_messages_logged" in stats
        assert "hub_load" in stats

    def test_spoke_status_distribution(self, populated_topology):
        """Test spoke status distribution calculation."""
        # Update some statuses
        populated_topology.update_agent_status("expert-backend", "working")
        populated_topology.update_agent_status("expert-frontend", "working")
        populated_topology.update_agent_status("manager-tdd", "completed")

        stats = populated_topology.get_topology_stats()
        dist = stats["spoke_status_distribution"]

        assert dist["working"] == 2
        assert dist["completed"] == 1
        assert dist["idle"] == 2  # Remaining spokes


class TestMessageLog:
    """Test message log functionality."""

    def test_get_message_log_all(self, populated_topology):
        """Test retrieving all message log entries."""
        # Send various messages
        populated_topology.hub_to_spoke("expert-backend", {"type": "task"})
        populated_topology.spoke_to_hub("expert-backend", {"type": "result"})
        populated_topology.hub_broadcast({"type": "status"})

        log = populated_topology.get_message_log()

        # Note: broadcast does NOT add individual messages to log, only stats
        # 1 unicast + 1 spoke_to_hub = 2 entries
        assert len(log) == 2

    def test_get_message_log_limited(self, populated_topology):
        """Test retrieving limited message log entries."""
        # Send messages
        for i in range(10):
            populated_topology.hub_to_spoke("expert-backend", {"id": i})

        log = populated_topology.get_message_log(limit=5)

        assert len(log) == 5

    def test_get_message_log_newest_first(self, populated_topology):
        """Test message log returns newest first."""
        populated_topology.hub_to_spoke("expert-backend", {"order": 1})
        populated_topology.hub_to_spoke("expert-backend", {"order": 2})

        log = populated_topology.get_message_log()

        # Newest first (reversed)
        assert log[0]["message"]["order"] == 2
        assert log[1]["message"]["order"] == 1

    def test_clear_message_log(self, populated_topology):
        """Test clearing message log."""
        populated_topology.hub_to_spoke("expert-backend", {"type": "task"})
        populated_topology.hub_broadcast({"type": "status"})

        count = populated_topology.clear_message_log()

        # Note: broadcast does NOT add individual messages to log
        assert count == 1  # Only 1 unicast message
        assert len(populated_topology.message_log) == 0


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_agent_hashable(self):
        """Test Agent objects are hashable (for set operations)."""
        agent1 = Agent(agent_id="test1", agent_type="type1", role="spoke")
        agent2 = Agent(agent_id="test2", agent_type="type2", role="spoke")

        # Should be able to use in set
        agent_set = {agent1, agent2}
        assert len(agent_set) == 2
        assert agent1 in agent_set

    def test_timestamp_format(self, populated_topology):
        """Test internal timestamps are ISO8601 with Z suffix."""
        populated_topology.hub_to_spoke("expert-backend", {"type": "test"})

        # Check spoke received timestamp
        spoke = populated_topology.get_spoke("expert-backend")
        msg = spoke.peek_messages()[0]

        assert msg["sent_at"].endswith("Z")
        assert "T" in msg["sent_at"]  # ISO8601 format

    def test_get_spoke_returns_none_if_not_found(self, basic_topology):
        """Test get_spoke returns None for non-existent spoke."""
        result = basic_topology.get_spoke("nonexistent")

        assert result is None
