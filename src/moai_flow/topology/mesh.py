#!/usr/bin/env python3
"""
Mesh Topology for MoAI-Flow

Full peer-to-peer connectivity where all agents can communicate directly.
No hierarchy - all agents are equal peers in the network.

Topology Structure:
    Agent A ←→ Agent B
       ↕          ↕
    Agent C ←→ Agent D
    (All agents connected to all others)

Use Cases:
- Collaborative tasks requiring full visibility
- Brainstorming and consensus-building
- Parallel processing with peer coordination
- Distributed decision-making without central authority

Example:
    >>> mesh = MeshTopology()
    >>> mesh.add_agent("agent-1", "expert-backend")
    >>> mesh.add_agent("agent-2", "expert-frontend")
    >>> mesh.add_agent("agent-3", "expert-database")
    >>> mesh.broadcast("agent-1", {"type": "status", "message": "Ready"})
    >>> print(mesh.visualize())
    Mesh Network (3 agents, 3 connections)
    agent-1 ←→ agent-2
    agent-1 ←→ agent-3
    agent-2 ←→ agent-3
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class Agent:
    """Agent node in mesh network."""
    agent_id: str
    agent_type: str  # e.g., "expert-backend", "expert-frontend"
    status: str = "idle"  # idle, working, completed, failed
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __hash__(self):
        """Make Agent hashable for set operations."""
        return hash(self.agent_id)

    def __eq__(self, other):
        """Agent equality based on agent_id."""
        if not isinstance(other, Agent):
            return False
        return self.agent_id == other.agent_id


@dataclass
class Message:
    """Message passed between agents in mesh."""
    from_agent: str
    to_agent: str
    message_type: str  # "direct", "broadcast", "query", "response"
    content: Dict[str, Any]
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    message_id: Optional[str] = None

    def __post_init__(self):
        """Generate message ID if not provided."""
        if not self.message_id:
            import uuid
            self.message_id = str(uuid.uuid4())


class MeshTopology:
    """
    Mesh (fully connected) topology for peer-to-peer coordination.
    All agents can communicate directly with any other agent.

    Key Features:
    - Full connectivity: N agents = N*(N-1)/2 bidirectional connections
    - No hierarchy: All agents are equal peers
    - Direct messaging: Any agent can message any other
    - Broadcast support: Send to all connected agents
    - Consensus building: Query all agents and aggregate responses
    """

    def __init__(self):
        """Initialize empty mesh network."""
        self.agents: Dict[str, Agent] = {}
        self.connections: Dict[str, Set[str]] = {}  # agent_id -> connected_ids
        self.message_history: List[Message] = []
        self._message_handlers: Dict[str, callable] = {}

        logger.info("Initialized mesh topology")

    def add_agent(
        self,
        agent_id: str,
        agent_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Add agent and connect to all existing agents.

        Creates full mesh connectivity automatically.

        Args:
            agent_id: Unique agent identifier
            agent_type: Agent type (e.g., "expert-backend", "expert-frontend")
            metadata: Additional agent metadata

        Returns:
            True if added successfully, False if agent_id already exists

        Example:
            >>> mesh.add_agent("agent-1", "expert-backend")
            True
            >>> mesh.add_agent("agent-2", "expert-frontend")
            True
            # Now agent-1 and agent-2 are automatically connected
        """
        if agent_id in self.agents:
            logger.warning(f"Agent {agent_id} already exists in mesh")
            return False

        # Create new agent
        agent = Agent(
            agent_id=agent_id,
            agent_type=agent_type,
            metadata=metadata or {}
        )

        self.agents[agent_id] = agent

        # Initialize connections for this agent
        self.connections[agent_id] = set()

        # Connect to all existing agents (full mesh)
        for existing_id in self.agents.keys():
            if existing_id != agent_id:
                # Bidirectional connection
                self.connections[agent_id].add(existing_id)
                self.connections[existing_id].add(agent_id)

        connection_count = len(self.connections[agent_id])
        logger.info(
            f"Added agent {agent_id} (type: {agent_type}) "
            f"with {connection_count} connections"
        )

        return True

    def remove_agent(self, agent_id: str) -> bool:
        """
        Remove agent and update all connections.

        Disconnects agent from all peers and removes from network.

        Args:
            agent_id: Agent identifier to remove

        Returns:
            True if removed successfully, False if agent not found

        Example:
            >>> mesh.remove_agent("agent-1")
            True
        """
        if agent_id not in self.agents:
            logger.warning(f"Agent {agent_id} not found in mesh")
            return False

        # Remove connections to this agent from all other agents
        connected_agents = self.connections.get(agent_id, set())
        for connected_id in connected_agents:
            if connected_id in self.connections:
                self.connections[connected_id].discard(agent_id)

        # Remove agent's own connections
        if agent_id in self.connections:
            del self.connections[agent_id]

        # Remove agent
        del self.agents[agent_id]

        logger.info(f"Removed agent {agent_id} and {len(connected_agents)} connections")
        return True

    def send_message(
        self,
        from_agent: str,
        to_agent: str,
        message: Dict[str, Any],
        message_type: str = "direct"
    ) -> bool:
        """
        Send direct message between any two agents.

        Args:
            from_agent: Sender agent ID
            to_agent: Receiver agent ID
            message: Message content (must be JSON-serializable)
            message_type: Type of message (default: "direct")

        Returns:
            True if sent successfully, False otherwise

        Raises:
            ValueError: If from_agent or to_agent not found or not connected

        Example:
            >>> mesh.send_message("agent-1", "agent-2", {"task": "process_data"})
            True
        """
        # Validate agents exist
        if from_agent not in self.agents:
            raise ValueError(f"Sender agent {from_agent} not found")
        if to_agent not in self.agents:
            raise ValueError(f"Receiver agent {to_agent} not found")

        # Verify connection exists (should always be true in full mesh)
        if to_agent not in self.connections.get(from_agent, set()):
            raise ValueError(
                f"No connection between {from_agent} and {to_agent}"
            )

        # Create message
        msg = Message(
            from_agent=from_agent,
            to_agent=to_agent,
            message_type=message_type,
            content=message
        )

        # Store in history
        self.message_history.append(msg)

        # Deliver message (store in receiver's metadata)
        receiver = self.agents[to_agent]
        if "messages" not in receiver.metadata:
            receiver.metadata["messages"] = []
        receiver.metadata["messages"].append({
            "from": from_agent,
            "type": message_type,
            "content": message,
            "timestamp": msg.timestamp,
            "message_id": msg.message_id
        })

        logger.info(
            f"Message sent: {from_agent} → {to_agent} "
            f"(type: {message_type}, id: {msg.message_id})"
        )

        # Call message handler if registered
        handler = self._message_handlers.get(message_type)
        if handler:
            handler(msg)

        return True

    def broadcast(
        self,
        from_agent: str,
        message: Dict[str, Any],
        exclude_agents: Optional[Set[str]] = None
    ) -> int:
        """
        Broadcast message to all connected agents.

        Args:
            from_agent: Agent broadcasting the message
            message: Message content
            exclude_agents: Optional set of agent IDs to exclude from broadcast

        Returns:
            Number of agents that received the broadcast

        Raises:
            ValueError: If from_agent not found

        Example:
            >>> mesh.broadcast("agent-1", {"status": "ready"})
            2  # Sent to 2 other agents
        """
        if from_agent not in self.agents:
            raise ValueError(f"Agent {from_agent} not found")

        exclude_agents = exclude_agents or set()
        sent_count = 0

        # Send to all connected agents except excluded ones
        for connected_id in self.connections.get(from_agent, set()):
            if connected_id not in exclude_agents:
                self.send_message(
                    from_agent=from_agent,
                    to_agent=connected_id,
                    message=message,
                    message_type="broadcast"
                )
                sent_count += 1

        logger.info(
            f"Broadcast from {from_agent} sent to {sent_count} agents "
            f"(excluded: {len(exclude_agents)})"
        )

        return sent_count

    def query_all(
        self,
        from_agent: str,
        query: Dict[str, Any],
        timeout_seconds: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Query all agents and collect responses.

        Useful for consensus building and distributed decision-making.

        Args:
            from_agent: Agent initiating the query
            query: Query content
            timeout_seconds: Optional timeout (not implemented yet)

        Returns:
            Dict mapping agent_id to response: {
                "queried_agents": int,
                "responses": Dict[str, Any],
                "timestamp": str
            }

        Raises:
            ValueError: If from_agent not found

        Example:
            >>> results = mesh.query_all("agent-1", {"question": "Ready?"})
            >>> results["responses"]["agent-2"]
            {"answer": "yes"}
        """
        if from_agent not in self.agents:
            raise ValueError(f"Agent {from_agent} not found")

        # Broadcast query
        queried_count = self.broadcast(from_agent, query)

        # Collect responses (simplified - just return metadata)
        responses = {}
        for agent_id in self.connections.get(from_agent, set()):
            agent = self.agents[agent_id]
            # In real implementation, would wait for actual responses
            # For now, return agent status as response
            responses[agent_id] = {
                "status": agent.status,
                "agent_type": agent.agent_type,
                "response_time": self._get_timestamp()
            }

        result = {
            "queried_agents": queried_count,
            "responses": responses,
            "timestamp": self._get_timestamp()
        }

        logger.info(
            f"Query from {from_agent} completed: "
            f"{len(responses)} responses collected"
        )

        return result

    def get_connections(self, agent_id: str) -> Set[str]:
        """
        Get all agents connected to specified agent.

        Args:
            agent_id: Agent identifier

        Returns:
            Set of connected agent IDs (empty if agent not found)

        Example:
            >>> mesh.get_connections("agent-1")
            {"agent-2", "agent-3"}
        """
        if agent_id not in self.agents:
            logger.warning(f"Agent {agent_id} not found")
            return set()

        return self.connections.get(agent_id, set()).copy()

    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """
        Get agent by ID.

        Args:
            agent_id: Agent identifier

        Returns:
            Agent object or None if not found
        """
        return self.agents.get(agent_id)

    def update_agent_status(self, agent_id: str, status: str) -> bool:
        """
        Update agent status.

        Args:
            agent_id: Agent identifier
            status: New status (idle, working, completed, failed)

        Returns:
            True if updated successfully, False if agent not found
        """
        if agent_id not in self.agents:
            logger.warning(f"Agent {agent_id} not found")
            return False

        self.agents[agent_id].status = status
        logger.info(f"Updated {agent_id} status to {status}")
        return True

    def register_message_handler(
        self,
        message_type: str,
        handler: callable
    ):
        """
        Register custom message handler.

        Args:
            message_type: Type of message to handle
            handler: Callable that takes Message object

        Example:
            >>> def handle_query(msg):
            ...     print(f"Query received: {msg.content}")
            >>> mesh.register_message_handler("query", handle_query)
        """
        self._message_handlers[message_type] = handler
        logger.info(f"Registered handler for message type: {message_type}")

    def get_message_history(
        self,
        agent_id: Optional[str] = None,
        message_type: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get message history with optional filters.

        Args:
            agent_id: Filter by sender or receiver (optional)
            message_type: Filter by message type (optional)
            limit: Maximum number of messages to return

        Returns:
            List of message dictionaries (most recent first)

        Example:
            >>> history = mesh.get_message_history(agent_id="agent-1", limit=10)
        """
        filtered = []

        for msg in reversed(self.message_history):
            # Apply filters
            if agent_id and (msg.from_agent != agent_id and msg.to_agent != agent_id):
                continue
            if message_type and msg.message_type != message_type:
                continue

            filtered.append({
                "from": msg.from_agent,
                "to": msg.to_agent,
                "type": msg.message_type,
                "content": msg.content,
                "timestamp": msg.timestamp,
                "id": msg.message_id
            })

            if len(filtered) >= limit:
                break

        return filtered

    def visualize(self) -> str:
        """
        ASCII visualization of mesh connections.

        Returns:
            String representation of mesh network

        Example:
            Mesh Network (3 agents, 3 connections)
            agent-1 ←→ agent-2
            agent-1 ←→ agent-3
            agent-2 ←→ agent-3

            Agents:
            • agent-1 (expert-backend) - idle
            • agent-2 (expert-frontend) - working
            • agent-3 (expert-database) - idle
        """
        lines = []
        agent_count = len(self.agents)

        # Calculate total unique connections
        # In full mesh: N * (N-1) / 2
        total_connections = agent_count * (agent_count - 1) // 2

        # Header
        lines.append(
            f"Mesh Network ({agent_count} agents, "
            f"{total_connections} connections)"
        )
        lines.append("")

        # Show all connections (avoid duplicates)
        shown_connections = set()
        for agent_id in sorted(self.agents.keys()):
            for connected_id in sorted(self.connections.get(agent_id, set())):
                # Create canonical connection pair (alphabetically sorted)
                conn_pair = tuple(sorted([agent_id, connected_id]))
                if conn_pair not in shown_connections:
                    lines.append(f"{conn_pair[0]} ←→ {conn_pair[1]}")
                    shown_connections.add(conn_pair)

        # Agent details
        lines.append("")
        lines.append("Agents:")
        for agent_id in sorted(self.agents.keys()):
            agent = self.agents[agent_id]
            lines.append(
                f"• {agent_id} ({agent.agent_type}) - {agent.status}"
            )

        return "\n".join(lines)

    def get_topology_stats(self) -> Dict[str, Any]:
        """
        Get mesh topology statistics.

        Returns:
            Dict with topology info: {
                "total_agents": int,
                "total_connections": int,
                "connectivity": float,  # 1.0 = full mesh
                "status_distribution": Dict[str, int],
                "message_count": int
            }
        """
        agent_count = len(self.agents)

        # Calculate actual connections
        actual_connections = sum(
            len(conns) for conns in self.connections.values()
        ) // 2  # Divide by 2 for bidirectional

        # Max possible connections in full mesh
        max_connections = agent_count * (agent_count - 1) // 2 if agent_count > 1 else 0

        # Connectivity ratio (1.0 = full mesh)
        connectivity = (
            actual_connections / max_connections if max_connections > 0 else 0.0
        )

        # Status distribution
        status_dist = {}
        for agent in self.agents.values():
            status_dist[agent.status] = status_dist.get(agent.status, 0) + 1

        return {
            "total_agents": agent_count,
            "total_connections": actual_connections,
            "max_connections": max_connections,
            "connectivity": connectivity,
            "status_distribution": status_dist,
            "message_count": len(self.message_history)
        }

    def reset_messages(self):
        """Clear all message history and agent message metadata."""
        self.message_history.clear()

        for agent in self.agents.values():
            if "messages" in agent.metadata:
                agent.metadata["messages"] = []

        logger.info("Reset all messages in mesh network")

    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO8601 format."""
        return datetime.utcnow().isoformat() + "Z"


__all__ = ["MeshTopology", "Agent", "Message"]
