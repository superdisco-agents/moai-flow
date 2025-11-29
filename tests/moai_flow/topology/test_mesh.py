#!/usr/bin/env python3
"""
Comprehensive test suite for MeshTopology.

Tests all aspects of mesh topology including:
- Agent management (add, remove, connections)
- Direct messaging
- Broadcast messaging
- Query operations
- Message history
- Connection verification
- Edge cases and error handling

Target Coverage: 90%+
Test Framework: pytest
"""

import pytest
from datetime import datetime
from moai_flow.topology.mesh import MeshTopology, Agent, Message


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def empty_mesh():
    """Create empty mesh topology."""
    return MeshTopology()


@pytest.fixture
def mesh_with_agents():
    """Create mesh with 3 agents pre-configured."""
    mesh = MeshTopology()
    mesh.add_agent("agent-1", "expert-backend")
    mesh.add_agent("agent-2", "expert-frontend")
    mesh.add_agent("agent-3", "expert-database")
    return mesh


@pytest.fixture
def mesh_with_5_agents():
    """Create mesh with 5 agents for scalability testing."""
    mesh = MeshTopology()
    for i in range(1, 6):
        mesh.add_agent(f"agent-{i}", f"expert-type-{i}")
    return mesh


@pytest.fixture
def mesh_with_10_agents():
    """Create mesh with 10 agents for large-scale testing."""
    mesh = MeshTopology()
    for i in range(1, 11):
        mesh.add_agent(f"agent-{i}", f"expert-type-{i}")
    return mesh


# ============================================================================
# Agent Management Tests
# ============================================================================


class TestAgentManagement:
    """Test agent addition, removal, and management."""

    def test_add_first_agent(self, empty_mesh):
        """Test adding first agent to empty mesh."""
        result = empty_mesh.add_agent("agent-1", "expert-backend")

        assert result is True
        assert "agent-1" in empty_mesh.agents
        assert empty_mesh.agents["agent-1"].agent_type == "expert-backend"
        assert len(empty_mesh.connections["agent-1"]) == 0  # No other agents

    def test_add_agent_auto_connect(self, empty_mesh):
        """Test automatic connection when adding agents."""
        # Add first agent
        empty_mesh.add_agent("agent-1", "expert-backend")

        # Add second agent - should auto-connect
        result = empty_mesh.add_agent("agent-2", "expert-frontend")

        assert result is True
        assert "agent-2" in empty_mesh.agents

        # Verify bidirectional connection
        assert "agent-2" in empty_mesh.connections["agent-1"]
        assert "agent-1" in empty_mesh.connections["agent-2"]

        # Verify connection count
        assert len(empty_mesh.connections["agent-1"]) == 1
        assert len(empty_mesh.connections["agent-2"]) == 1

    def test_add_duplicate_agent(self, empty_mesh):
        """Test adding agent with duplicate ID."""
        empty_mesh.add_agent("agent-1", "expert-backend")

        # Try to add duplicate
        result = empty_mesh.add_agent("agent-1", "expert-frontend")

        assert result is False
        assert empty_mesh.agents["agent-1"].agent_type == "expert-backend"  # Original

    def test_add_agent_with_metadata(self, empty_mesh):
        """Test adding agent with custom metadata."""
        metadata = {"region": "us-west", "priority": "high"}
        result = empty_mesh.add_agent("agent-1", "expert-backend", metadata=metadata)

        assert result is True
        assert empty_mesh.agents["agent-1"].metadata == metadata

    def test_remove_agent(self, mesh_with_agents):
        """Test removing agent from mesh."""
        # Verify initial state
        assert "agent-2" in mesh_with_agents.agents
        initial_count = len(mesh_with_agents.agents)

        # Remove agent
        result = mesh_with_agents.remove_agent("agent-2")

        assert result is True
        assert "agent-2" not in mesh_with_agents.agents
        assert len(mesh_with_agents.agents) == initial_count - 1

        # Verify connections removed from other agents
        assert "agent-2" not in mesh_with_agents.connections.get("agent-1", set())
        assert "agent-2" not in mesh_with_agents.connections.get("agent-3", set())

    def test_remove_nonexistent_agent(self, mesh_with_agents):
        """Test removing agent that doesn't exist."""
        result = mesh_with_agents.remove_agent("agent-999")

        assert result is False
        assert len(mesh_with_agents.agents) == 3  # No change

    def test_connection_count_formula(self, empty_mesh):
        """Test connection count follows N*(N-1)/2 formula."""
        # Add agents and verify connection formula
        test_cases = [
            (1, 0, 0.0),   # 1 agent: 1*(1-1)/2 = 0 connections, 0.0 connectivity
            (2, 1, 1.0),   # 2 agents: 2*(2-1)/2 = 1 connection, 1.0 connectivity
            (3, 3, 1.0),   # 3 agents: 3*(3-1)/2 = 3 connections, 1.0 connectivity
            (4, 6, 1.0),   # 4 agents: 4*(4-1)/2 = 6 connections, 1.0 connectivity
            (5, 10, 1.0),  # 5 agents: 5*(5-1)/2 = 10 connections, 1.0 connectivity
        ]

        for num_agents, expected_connections, expected_connectivity in test_cases:
            mesh = MeshTopology()
            for i in range(1, num_agents + 1):
                mesh.add_agent(f"agent-{i}", f"type-{i}")

            stats = mesh.get_topology_stats()
            assert stats["total_agents"] == num_agents
            assert stats["total_connections"] == expected_connections
            assert stats["connectivity"] == expected_connectivity  # Full mesh (or 0.0 for single agent)

    def test_get_connections(self, mesh_with_agents):
        """Test retrieving agent connections."""
        connections = mesh_with_agents.get_connections("agent-1")

        assert isinstance(connections, set)
        assert "agent-2" in connections
        assert "agent-3" in connections
        assert len(connections) == 2

    def test_get_connections_nonexistent_agent(self, mesh_with_agents):
        """Test getting connections for nonexistent agent."""
        connections = mesh_with_agents.get_connections("agent-999")

        assert connections == set()

    def test_get_agent(self, mesh_with_agents):
        """Test retrieving agent by ID."""
        agent = mesh_with_agents.get_agent("agent-1")

        assert agent is not None
        assert isinstance(agent, Agent)
        assert agent.agent_id == "agent-1"
        assert agent.agent_type == "expert-backend"

    def test_get_nonexistent_agent(self, mesh_with_agents):
        """Test retrieving nonexistent agent."""
        agent = mesh_with_agents.get_agent("agent-999")

        assert agent is None

    def test_update_agent_status(self, mesh_with_agents):
        """Test updating agent status."""
        result = mesh_with_agents.update_agent_status("agent-1", "working")

        assert result is True
        assert mesh_with_agents.agents["agent-1"].status == "working"

    def test_update_status_nonexistent_agent(self, mesh_with_agents):
        """Test updating status of nonexistent agent."""
        result = mesh_with_agents.update_agent_status("agent-999", "working")

        assert result is False


# ============================================================================
# Direct Messaging Tests
# ============================================================================


class TestDirectMessaging:
    """Test direct message sending between agents."""

    def test_send_message_direct(self, mesh_with_agents):
        """Test sending direct message between two agents."""
        message_content = {"task": "process_data", "priority": "high"}

        result = mesh_with_agents.send_message(
            "agent-1", "agent-2", message_content
        )

        assert result is True

        # Verify message delivered to receiver
        receiver = mesh_with_agents.agents["agent-2"]
        assert "messages" in receiver.metadata
        assert len(receiver.metadata["messages"]) == 1

        received_msg = receiver.metadata["messages"][0]
        assert received_msg["from"] == "agent-1"
        assert received_msg["content"] == message_content
        assert received_msg["type"] == "direct"

    def test_send_message_to_nonexistent_agent(self, mesh_with_agents):
        """Test sending message to nonexistent agent raises error."""
        with pytest.raises(ValueError, match="Receiver agent agent-999 not found"):
            mesh_with_agents.send_message(
                "agent-1", "agent-999", {"test": "data"}
            )

    def test_send_message_from_nonexistent_agent(self, mesh_with_agents):
        """Test sending message from nonexistent agent raises error."""
        with pytest.raises(ValueError, match="Sender agent agent-999 not found"):
            mesh_with_agents.send_message(
                "agent-999", "agent-1", {"test": "data"}
            )

    def test_message_uuid_tracking(self, mesh_with_agents):
        """Test that each message gets unique ID."""
        mesh_with_agents.send_message("agent-1", "agent-2", {"msg": "1"})
        mesh_with_agents.send_message("agent-1", "agent-2", {"msg": "2"})

        receiver = mesh_with_agents.agents["agent-2"]
        messages = receiver.metadata["messages"]

        assert len(messages) == 2
        assert messages[0]["message_id"] != messages[1]["message_id"]
        assert isinstance(messages[0]["message_id"], str)

    def test_message_timestamp(self, mesh_with_agents):
        """Test message includes timestamp."""
        mesh_with_agents.send_message("agent-1", "agent-2", {"test": "data"})

        receiver = mesh_with_agents.agents["agent-2"]
        msg = receiver.metadata["messages"][0]

        assert "timestamp" in msg
        # Verify ISO8601 format with Z suffix
        assert msg["timestamp"].endswith("Z")

        # Parse timestamp to verify validity
        timestamp = datetime.fromisoformat(msg["timestamp"].rstrip("Z"))
        assert isinstance(timestamp, datetime)

    def test_message_history_tracking(self, mesh_with_agents):
        """Test messages are tracked in history."""
        initial_count = len(mesh_with_agents.message_history)

        mesh_with_agents.send_message("agent-1", "agent-2", {"msg": "1"})
        mesh_with_agents.send_message("agent-2", "agent-3", {"msg": "2"})

        assert len(mesh_with_agents.message_history) == initial_count + 2


# ============================================================================
# Broadcast Messaging Tests
# ============================================================================


class TestBroadcastMessaging:
    """Test broadcast messaging to all connected agents."""

    def test_broadcast_message(self, mesh_with_agents):
        """Test broadcasting message to all agents."""
        broadcast_content = {"status": "ready", "version": "1.0"}

        sent_count = mesh_with_agents.broadcast("agent-1", broadcast_content)

        # Should send to 2 other agents (agent-2, agent-3)
        assert sent_count == 2

        # Verify both agents received broadcast
        for agent_id in ["agent-2", "agent-3"]:
            agent = mesh_with_agents.agents[agent_id]
            assert "messages" in agent.metadata
            assert len(agent.metadata["messages"]) == 1

            msg = agent.metadata["messages"][0]
            assert msg["from"] == "agent-1"
            assert msg["type"] == "broadcast"
            assert msg["content"] == broadcast_content

    def test_broadcast_with_exclusions(self, mesh_with_agents):
        """Test broadcasting with agent exclusions."""
        exclude_set = {"agent-2"}

        sent_count = mesh_with_agents.broadcast(
            "agent-1", {"msg": "selective"}, exclude_agents=exclude_set
        )

        # Should send to only agent-3 (agent-2 excluded)
        assert sent_count == 1

        # Verify agent-3 received, agent-2 did not
        assert len(mesh_with_agents.agents["agent-3"].metadata["messages"]) == 1
        assert "messages" not in mesh_with_agents.agents["agent-2"].metadata

    def test_broadcast_from_nonexistent_agent(self, mesh_with_agents):
        """Test broadcasting from nonexistent agent raises error."""
        with pytest.raises(ValueError, match="Agent agent-999 not found"):
            mesh_with_agents.broadcast("agent-999", {"msg": "test"})

    def test_broadcast_to_empty_mesh(self, empty_mesh):
        """Test broadcasting from single agent (no recipients)."""
        empty_mesh.add_agent("agent-1", "expert-backend")

        sent_count = empty_mesh.broadcast("agent-1", {"msg": "alone"})

        # No other agents to broadcast to
        assert sent_count == 0


# ============================================================================
# Query Operations Tests
# ============================================================================


class TestQueryOperations:
    """Test query operations for consensus building."""

    def test_query_all_agents(self, mesh_with_agents):
        """Test querying all agents in mesh."""
        query_content = {"question": "Ready for deployment?"}

        result = mesh_with_agents.query_all("agent-1", query_content)

        assert "queried_agents" in result
        assert "responses" in result
        assert "timestamp" in result

        # Should query 2 other agents
        assert result["queried_agents"] == 2
        assert len(result["responses"]) == 2

    def test_query_response_collection(self, mesh_with_agents):
        """Test response structure from query."""
        result = mesh_with_agents.query_all("agent-1", {"q": "status"})

        responses = result["responses"]

        # Verify responses contain required fields
        for agent_id, response in responses.items():
            assert "status" in response
            assert "agent_type" in response
            assert "response_time" in response
            assert agent_id in ["agent-2", "agent-3"]

    def test_query_with_no_agents(self, empty_mesh):
        """Test query from single agent (no others to query)."""
        empty_mesh.add_agent("agent-1", "expert-backend")

        result = empty_mesh.query_all("agent-1", {"q": "anyone?"})

        assert result["queried_agents"] == 0
        assert len(result["responses"]) == 0

    def test_query_from_nonexistent_agent(self, mesh_with_agents):
        """Test querying from nonexistent agent raises error."""
        with pytest.raises(ValueError, match="Agent agent-999 not found"):
            mesh_with_agents.query_all("agent-999", {"q": "test"})


# ============================================================================
# Message History Tests
# ============================================================================


class TestMessageHistory:
    """Test message history retrieval and filtering."""

    def test_message_log(self, mesh_with_agents):
        """Test message logging in history."""
        initial_count = len(mesh_with_agents.message_history)

        mesh_with_agents.send_message("agent-1", "agent-2", {"msg": "1"})
        mesh_with_agents.send_message("agent-2", "agent-3", {"msg": "2"})
        mesh_with_agents.broadcast("agent-3", {"msg": "3"})

        # Broadcast sends to 2 agents, so total = 4 messages
        expected_count = initial_count + 4
        assert len(mesh_with_agents.message_history) == expected_count

    def test_get_agent_messages(self, mesh_with_agents):
        """Test filtering messages by agent."""
        # Send various messages
        mesh_with_agents.send_message("agent-1", "agent-2", {"msg": "1"})
        mesh_with_agents.send_message("agent-2", "agent-3", {"msg": "2"})
        mesh_with_agents.send_message("agent-3", "agent-1", {"msg": "3"})

        # Get messages involving agent-1 (sent or received)
        history = mesh_with_agents.get_message_history(agent_id="agent-1")

        # Should include messages where agent-1 is sender or receiver
        assert len(history) >= 2
        for msg in history:
            assert msg["from"] == "agent-1" or msg["to"] == "agent-1"

    def test_filter_by_message_type(self, mesh_with_agents):
        """Test filtering messages by type."""
        mesh_with_agents.send_message("agent-1", "agent-2", {"msg": "direct"})
        mesh_with_agents.broadcast("agent-1", {"msg": "broadcast"})

        # Filter for broadcast messages only
        broadcasts = mesh_with_agents.get_message_history(message_type="broadcast")

        assert len(broadcasts) >= 2  # Broadcast to 2 agents
        for msg in broadcasts:
            assert msg["type"] == "broadcast"

    def test_message_history_limit(self, mesh_with_agents):
        """Test message history respects limit parameter."""
        # Send many messages
        for i in range(20):
            mesh_with_agents.send_message("agent-1", "agent-2", {"msg": f"{i}"})

        # Get limited history
        history = mesh_with_agents.get_message_history(limit=5)

        assert len(history) == 5

    def test_message_history_most_recent_first(self, mesh_with_agents):
        """Test message history returns most recent first."""
        mesh_with_agents.send_message("agent-1", "agent-2", {"msg": "first"})
        mesh_with_agents.send_message("agent-1", "agent-2", {"msg": "second"})
        mesh_with_agents.send_message("agent-1", "agent-2", {"msg": "third"})

        history = mesh_with_agents.get_message_history(limit=3)

        # Most recent should be "third"
        assert history[0]["content"]["msg"] == "third"
        assert history[2]["content"]["msg"] == "first"

    def test_reset_messages(self, mesh_with_agents):
        """Test resetting all messages."""
        # Send messages
        mesh_with_agents.send_message("agent-1", "agent-2", {"msg": "test"})
        mesh_with_agents.broadcast("agent-1", {"msg": "broadcast"})

        # Verify messages exist
        assert len(mesh_with_agents.message_history) > 0

        # Reset
        mesh_with_agents.reset_messages()

        # Verify all cleared
        assert len(mesh_with_agents.message_history) == 0
        for agent in mesh_with_agents.agents.values():
            messages = agent.metadata.get("messages", [])
            assert len(messages) == 0


# ============================================================================
# Full Connectivity Tests
# ============================================================================


class TestFullConnectivity:
    """Test mesh maintains full connectivity."""

    def test_mesh_connectivity_5_agents(self, mesh_with_5_agents):
        """Test full connectivity with 5 agents."""
        stats = mesh_with_5_agents.get_topology_stats()

        assert stats["total_agents"] == 5
        assert stats["total_connections"] == 10  # 5*(5-1)/2
        assert stats["connectivity"] == 1.0  # Full mesh

    def test_mesh_connectivity_10_agents(self, mesh_with_10_agents):
        """Test full connectivity with 10 agents."""
        stats = mesh_with_10_agents.get_topology_stats()

        assert stats["total_agents"] == 10
        assert stats["total_connections"] == 45  # 10*(10-1)/2
        assert stats["connectivity"] == 1.0  # Full mesh

    def test_connections_after_removal(self, mesh_with_5_agents):
        """Test connectivity after removing agents."""
        # Remove one agent
        mesh_with_5_agents.remove_agent("agent-3")

        stats = mesh_with_5_agents.get_topology_stats()

        # 4 agents should have 6 connections
        assert stats["total_agents"] == 4
        assert stats["total_connections"] == 6  # 4*(4-1)/2
        assert stats["connectivity"] == 1.0  # Still full mesh

    def test_all_agents_connected(self, mesh_with_agents):
        """Test that all agents are connected to all others."""
        for agent_id in mesh_with_agents.agents.keys():
            connections = mesh_with_agents.get_connections(agent_id)

            # Should be connected to all other agents
            expected_connections = set(mesh_with_agents.agents.keys()) - {agent_id}
            assert connections == expected_connections


# ============================================================================
# Topology Statistics Tests
# ============================================================================


class TestTopologyStatistics:
    """Test topology statistics and metrics."""

    def test_get_topology_stats(self, mesh_with_agents):
        """Test retrieving topology statistics."""
        stats = mesh_with_agents.get_topology_stats()

        assert "total_agents" in stats
        assert "total_connections" in stats
        assert "max_connections" in stats
        assert "connectivity" in stats
        assert "status_distribution" in stats
        assert "message_count" in stats

        assert stats["total_agents"] == 3
        assert stats["total_connections"] == 3
        assert stats["max_connections"] == 3
        assert stats["connectivity"] == 1.0

    def test_status_distribution(self, mesh_with_agents):
        """Test status distribution in stats."""
        # Update statuses
        mesh_with_agents.update_agent_status("agent-1", "working")
        mesh_with_agents.update_agent_status("agent-2", "working")
        mesh_with_agents.update_agent_status("agent-3", "idle")

        stats = mesh_with_agents.get_topology_stats()
        status_dist = stats["status_distribution"]

        assert status_dist["working"] == 2
        assert status_dist["idle"] == 1

    def test_empty_mesh_stats(self, empty_mesh):
        """Test stats for empty mesh."""
        stats = empty_mesh.get_topology_stats()

        assert stats["total_agents"] == 0
        assert stats["total_connections"] == 0
        assert stats["connectivity"] == 0.0


# ============================================================================
# Message Handler Tests
# ============================================================================


class TestMessageHandlers:
    """Test custom message handler registration."""

    def test_register_message_handler(self, mesh_with_agents):
        """Test registering custom message handler."""
        handler_called = []

        def custom_handler(msg):
            handler_called.append(msg.message_id)

        mesh_with_agents.register_message_handler("custom", custom_handler)

        # Send message with custom type
        mesh_with_agents.send_message(
            "agent-1", "agent-2", {"test": "data"}, message_type="custom"
        )

        # Verify handler was called
        assert len(handler_called) == 1

    def test_multiple_handlers(self, mesh_with_agents):
        """Test registering multiple handlers for different types."""
        query_calls = []
        response_calls = []

        mesh_with_agents.register_message_handler(
            "query", lambda msg: query_calls.append(msg.message_id)
        )
        mesh_with_agents.register_message_handler(
            "response", lambda msg: response_calls.append(msg.message_id)
        )

        mesh_with_agents.send_message(
            "agent-1", "agent-2", {}, message_type="query"
        )
        mesh_with_agents.send_message(
            "agent-2", "agent-1", {}, message_type="response"
        )

        assert len(query_calls) == 1
        assert len(response_calls) == 1


# ============================================================================
# Visualization Tests
# ============================================================================


class TestVisualization:
    """Test mesh visualization."""

    def test_visualize_mesh(self, mesh_with_agents):
        """Test ASCII visualization output."""
        viz = mesh_with_agents.visualize()

        assert "Mesh Network" in viz
        assert "3 agents" in viz
        assert "3 connections" in viz

        # Check connections shown
        assert "agent-1 ←→ agent-2" in viz
        assert "agent-1 ←→ agent-3" in viz
        assert "agent-2 ←→ agent-3" in viz

        # Check agent details
        assert "agent-1 (expert-backend)" in viz
        assert "agent-2 (expert-frontend)" in viz
        assert "agent-3 (expert-database)" in viz

    def test_visualize_empty_mesh(self, empty_mesh):
        """Test visualization of empty mesh."""
        viz = empty_mesh.visualize()

        assert "Mesh Network" in viz
        assert "0 agents" in viz
        assert "0 connections" in viz


# ============================================================================
# Edge Cases and Error Handling
# ============================================================================


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_agent_hash_equality(self):
        """Test Agent hash and equality methods."""
        agent1 = Agent("agent-1", "expert-backend")
        agent2 = Agent("agent-1", "expert-frontend")
        agent3 = Agent("agent-2", "expert-backend")

        # Same ID should be equal
        assert agent1 == agent2
        assert hash(agent1) == hash(agent2)

        # Different ID should not be equal
        assert agent1 != agent3

        # Can use in sets
        agent_set = {agent1, agent2, agent3}
        assert len(agent_set) == 2  # agent1 and agent2 are same

    def test_agent_equality_with_non_agent(self):
        """Test Agent equality with non-Agent object."""
        agent = Agent("agent-1", "expert-backend")

        assert agent != "agent-1"
        assert agent != 123
        assert agent != None

    def test_message_auto_id_generation(self):
        """Test Message generates UUID if not provided."""
        msg = Message(
            from_agent="agent-1",
            to_agent="agent-2",
            message_type="direct",
            content={"test": "data"}
        )

        assert msg.message_id is not None
        assert isinstance(msg.message_id, str)
        assert len(msg.message_id) > 0

    def test_message_custom_id(self):
        """Test Message with custom ID."""
        custom_id = "custom-msg-123"
        msg = Message(
            from_agent="agent-1",
            to_agent="agent-2",
            message_type="direct",
            content={"test": "data"},
            message_id=custom_id
        )

        assert msg.message_id == custom_id

    def test_message_timestamp_format(self):
        """Test Message timestamp is ISO8601 with Z."""
        msg = Message(
            from_agent="agent-1",
            to_agent="agent-2",
            message_type="direct",
            content={}
        )

        assert msg.timestamp.endswith("Z")
        # Verify parseable
        timestamp = datetime.fromisoformat(msg.timestamp.rstrip("Z"))
        assert isinstance(timestamp, datetime)

    def test_send_to_disconnected_agents_impossible(self, mesh_with_agents):
        """Test that in full mesh, all agents are always connected."""
        # In full mesh, this should never happen, but test the check exists
        # Remove agent first
        mesh_with_agents.remove_agent("agent-2")

        # Try to send to removed agent
        with pytest.raises(ValueError, match="Receiver agent agent-2 not found"):
            mesh_with_agents.send_message("agent-1", "agent-2", {"msg": "test"})

    def test_empty_metadata_default(self, empty_mesh):
        """Test agent created without metadata has empty dict."""
        empty_mesh.add_agent("agent-1", "expert-backend")
        agent = empty_mesh.agents["agent-1"]

        assert agent.metadata == {}

    def test_concurrent_broadcasts(self, mesh_with_5_agents):
        """Test multiple agents broadcasting simultaneously."""
        # Simulate concurrent broadcasts
        counts = []
        for i in range(1, 6):
            count = mesh_with_5_agents.broadcast(
                f"agent-{i}", {"from": f"agent-{i}"}
            )
            counts.append(count)

        # Each agent broadcasts to 4 others
        assert all(count == 4 for count in counts)

        # Verify all agents received 4 messages (one from each other agent)
        for agent_id in mesh_with_5_agents.agents.keys():
            agent = mesh_with_5_agents.agents[agent_id]
            messages = agent.metadata.get("messages", [])
            assert len(messages) == 4


# ============================================================================
# Integration Tests
# ============================================================================


class TestIntegration:
    """Integration tests for complete workflows."""

    def test_full_workflow_add_message_remove(self, empty_mesh):
        """Test complete workflow: add agents, message, remove."""
        # Add agents
        empty_mesh.add_agent("agent-1", "expert-backend")
        empty_mesh.add_agent("agent-2", "expert-frontend")
        empty_mesh.add_agent("agent-3", "expert-database")

        # Send messages
        empty_mesh.send_message("agent-1", "agent-2", {"task": "process"})
        empty_mesh.broadcast("agent-2", {"status": "ready"})

        # Query
        result = empty_mesh.query_all("agent-1", {"q": "status"})
        assert result["queried_agents"] == 2

        # Remove agent
        empty_mesh.remove_agent("agent-3")

        # Verify connectivity maintained
        stats = empty_mesh.get_topology_stats()
        assert stats["total_agents"] == 2
        assert stats["connectivity"] == 1.0

    def test_scalability_large_mesh(self):
        """Test mesh scales to larger agent counts."""
        mesh = MeshTopology()

        # Add 20 agents
        for i in range(1, 21):
            mesh.add_agent(f"agent-{i}", f"type-{i}")

        stats = mesh.get_topology_stats()

        # 20 agents = 20*19/2 = 190 connections
        assert stats["total_agents"] == 20
        assert stats["total_connections"] == 190
        assert stats["connectivity"] == 1.0

        # Test messaging still works
        mesh.broadcast("agent-1", {"msg": "test"})

        # Should send to 19 other agents
        agent1_history = mesh.get_message_history(agent_id="agent-1", limit=100)
        broadcast_messages = [m for m in agent1_history if m["type"] == "broadcast"]
        assert len(broadcast_messages) == 19

    def test_message_flow_verification(self, mesh_with_agents):
        """Test complete message flow from send to receive."""
        # Send message
        content = {"task": "verify", "data": [1, 2, 3]}
        mesh_with_agents.send_message("agent-1", "agent-2", content)

        # Verify in history
        history = mesh_with_agents.get_message_history(limit=1)
        assert len(history) == 1
        assert history[0]["from"] == "agent-1"
        assert history[0]["to"] == "agent-2"
        assert history[0]["content"] == content

        # Verify received by agent
        agent2 = mesh_with_agents.agents["agent-2"]
        received = agent2.metadata["messages"][0]
        assert received["content"] == content
        assert received["from"] == "agent-1"
