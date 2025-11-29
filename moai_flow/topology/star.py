#!/usr/bin/env python3
"""
Star Topology for MoAI-Flow

Hub-and-spoke network pattern for centralized coordination.
All communication flows through a central hub (typically Alfred),
with spoke agents isolated from direct communication with each other.

Topology Structure:
              Hub (Alfred)
            /  |  |  \  \
           /   |  |   \  \
        S1    S2 S3   S4  S5
    (Spokes don't communicate directly)

Use Cases:
- Centralized orchestration with single point of control
- Hub-based load balancing and task distribution
- Isolated spoke execution with hub coordination
- Reduced communication complexity (n vs n²)

Example:
    >>> topo = StarTopology(hub_agent_id="alfred")
    >>> topo.add_spoke("expert-backend", "expert-backend")
    >>> topo.add_spoke("expert-frontend", "expert-frontend")
    >>> topo.hub_broadcast({"type": "status_check"})
    2  # Broadcasted to 2 spokes
    >>> print(topo.visualize())
          Hub: alfred
        /  |  |  \
    expert-backend expert-frontend
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set
import logging
from datetime import datetime
from collections import defaultdict, deque

logger = logging.getLogger(__name__)


@dataclass
class Agent:
    """Agent node in star topology."""
    agent_id: str
    agent_type: str  # e.g., "alfred", "expert-backend", "expert-frontend"
    role: str  # "hub" or "spoke"
    status: str = "idle"  # idle, working, completed, failed
    message_queue: deque = field(default_factory=deque)  # Message inbox
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __hash__(self):
        """Make Agent hashable for set operations."""
        return hash(self.agent_id)

    def add_message(self, message: Dict[str, Any]) -> None:
        """Add message to agent's inbox."""
        self.message_queue.append({
            **message,
            "received_at": datetime.utcnow().isoformat() + "Z"
        })

    def get_messages(self, count: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get messages from inbox.

        Args:
            count: Number of messages to retrieve (None = all)

        Returns:
            List of messages (FIFO order)
        """
        if count is None:
            messages = list(self.message_queue)
            self.message_queue.clear()
            return messages

        messages = []
        for _ in range(min(count, len(self.message_queue))):
            messages.append(self.message_queue.popleft())
        return messages

    def peek_messages(self, count: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        View messages without removing them.

        Args:
            count: Number of messages to view (None = all)

        Returns:
            List of messages (does not modify queue)
        """
        if count is None:
            return list(self.message_queue)
        return list(self.message_queue)[:count]


class StarTopology:
    """
    Star (hub-and-spoke) topology for centralized coordination.

    All communication flows through the central hub.
    Spokes are isolated from each other and can only communicate via hub.
    Hub can broadcast to all spokes or send to specific spoke.

    Features:
    - Hub-centric message routing
    - Spoke isolation (no direct spoke-to-spoke communication)
    - Hub load monitoring and tracking
    - Message queue per agent
    - Broadcast and unicast messaging patterns
    """

    def __init__(self, hub_agent_id: str = "alfred"):
        """
        Initialize star topology with central hub.

        Args:
            hub_agent_id: Unique identifier for hub agent (default: "alfred")
        """
        self.hub_id = hub_agent_id
        self.hub_agent: Optional[Agent] = None
        self.spoke_agents: Dict[str, Agent] = {}

        # Message tracking
        self.message_log: List[Dict[str, Any]] = []
        self.hub_stats = {
            "messages_sent": 0,
            "messages_received": 0,
            "broadcasts": 0,
            "active_tasks": 0
        }

        # Create hub agent
        self.hub_agent = Agent(
            agent_id=hub_agent_id,
            agent_type="alfred",
            role="hub",
            metadata={"created_at": self._get_timestamp()}
        )

        logger.info(f"Initialized star topology with hub: {hub_agent_id}")

    def add_spoke(self, agent_id: str, agent_type: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Add spoke agent connected to hub.

        Args:
            agent_id: Unique agent identifier
            agent_type: Agent type (e.g., "expert-backend", "expert-frontend")
            metadata: Optional agent metadata

        Returns:
            True if added successfully, False if agent_id already exists

        Example:
            >>> topo.add_spoke("expert-backend", "expert-backend")
            True
            >>> topo.add_spoke("expert-frontend", "expert-frontend", {"priority": "high"})
            True
        """
        if agent_id in self.spoke_agents:
            logger.warning(f"Spoke agent {agent_id} already exists in topology")
            return False

        if agent_id == self.hub_id:
            logger.error(f"Cannot add hub {self.hub_id} as spoke")
            return False

        # Create spoke agent
        spoke = Agent(
            agent_id=agent_id,
            agent_type=agent_type,
            role="spoke",
            metadata=metadata or {}
        )
        spoke.metadata["created_at"] = self._get_timestamp()
        spoke.metadata["connected_to_hub"] = self.hub_id

        self.spoke_agents[agent_id] = spoke
        logger.info(f"Added spoke agent {agent_id} (type: {agent_type})")
        return True

    def remove_spoke(self, agent_id: str) -> bool:
        """
        Remove spoke agent from topology.

        Args:
            agent_id: Unique agent identifier

        Returns:
            True if removed successfully, False if agent not found

        Example:
            >>> topo.remove_spoke("expert-backend")
            True
        """
        if agent_id not in self.spoke_agents:
            logger.warning(f"Spoke agent {agent_id} not found in topology")
            return False

        # Clear any pending messages
        spoke = self.spoke_agents[agent_id]
        undelivered = len(spoke.message_queue)
        if undelivered > 0:
            logger.warning(f"Removing spoke {agent_id} with {undelivered} undelivered messages")

        del self.spoke_agents[agent_id]
        logger.info(f"Removed spoke agent {agent_id}")
        return True

    def hub_to_spoke(self, spoke_id: str, message: Dict[str, Any]) -> bool:
        """
        Send message from hub to specific spoke.

        Args:
            spoke_id: Target spoke agent ID
            message: Message payload (must be JSON-serializable)

        Returns:
            True if sent successfully, False if spoke not found

        Raises:
            ValueError: If message is not a dict

        Example:
            >>> topo.hub_to_spoke("expert-backend", {
            ...     "type": "task",
            ...     "spec_id": "SPEC-001",
            ...     "action": "implement"
            ... })
            True
        """
        if not isinstance(message, dict):
            raise ValueError("Message must be a dictionary")

        if spoke_id not in self.spoke_agents:
            logger.error(f"Spoke agent {spoke_id} not found")
            return False

        spoke = self.spoke_agents[spoke_id]

        # Create message envelope
        envelope = {
            "from": self.hub_id,
            "to": spoke_id,
            "message": message,
            "sent_at": self._get_timestamp(),
            "type": "hub_to_spoke"
        }

        # Deliver message to spoke's queue
        spoke.add_message(envelope)

        # Log message
        self.message_log.append(envelope)
        self.hub_stats["messages_sent"] += 1

        logger.info(f"Hub sent message to spoke {spoke_id}")
        return True

    def spoke_to_hub(self, spoke_id: str, message: Dict[str, Any]) -> bool:
        """
        Send message from spoke to hub.

        Args:
            spoke_id: Source spoke agent ID
            message: Message payload (must be JSON-serializable)

        Returns:
            True if sent successfully, False if spoke not found

        Raises:
            ValueError: If message is not a dict or spoke_id is hub

        Example:
            >>> topo.spoke_to_hub("expert-backend", {
            ...     "type": "result",
            ...     "status": "completed",
            ...     "data": {...}
            ... })
            True
        """
        if not isinstance(message, dict):
            raise ValueError("Message must be a dictionary")

        if spoke_id == self.hub_id:
            raise ValueError("Hub cannot send spoke_to_hub message")

        if spoke_id not in self.spoke_agents:
            logger.error(f"Spoke agent {spoke_id} not found")
            return False

        # Create message envelope
        envelope = {
            "from": spoke_id,
            "to": self.hub_id,
            "message": message,
            "sent_at": self._get_timestamp(),
            "type": "spoke_to_hub"
        }

        # Deliver message to hub's queue
        self.hub_agent.add_message(envelope)

        # Log message
        self.message_log.append(envelope)
        self.hub_stats["messages_received"] += 1

        logger.info(f"Spoke {spoke_id} sent message to hub")
        return True

    def hub_broadcast(self, message: Dict[str, Any], exclude: Optional[List[str]] = None) -> int:
        """
        Hub broadcasts message to all spokes.

        Args:
            message: Message payload (must be JSON-serializable)
            exclude: Optional list of spoke IDs to exclude from broadcast

        Returns:
            Number of spokes that received the message

        Raises:
            ValueError: If message is not a dict

        Example:
            >>> topo.hub_broadcast({"type": "status_check"})
            5  # Broadcasted to 5 spokes
            >>> topo.hub_broadcast({"type": "shutdown"}, exclude=["expert-backend"])
            4  # Broadcasted to 4 spokes (excluded 1)
        """
        if not isinstance(message, dict):
            raise ValueError("Message must be a dictionary")

        exclude = exclude or []
        exclude_set = set(exclude)

        # Get target spokes
        target_spokes = [
            spoke_id for spoke_id in self.spoke_agents.keys()
            if spoke_id not in exclude_set
        ]

        if not target_spokes:
            logger.warning("No spokes to broadcast to")
            return 0

        # Send to each spoke
        sent_count = 0
        timestamp = self._get_timestamp()

        for spoke_id in target_spokes:
            spoke = self.spoke_agents[spoke_id]

            # Create broadcast envelope
            envelope = {
                "from": self.hub_id,
                "to": spoke_id,
                "message": message,
                "sent_at": timestamp,
                "type": "broadcast",
                "total_recipients": len(target_spokes)
            }

            # Deliver to spoke
            spoke.add_message(envelope)
            sent_count += 1

        # Update stats
        self.hub_stats["broadcasts"] += 1
        self.hub_stats["messages_sent"] += sent_count

        logger.info(f"Hub broadcasted to {sent_count} spokes")
        return sent_count

    def get_hub_load(self) -> Dict[str, Any]:
        """
        Get current load on hub (message queue, active tasks, stats).

        Returns:
            Dict with hub load metrics: {
                "hub_id": str,
                "pending_messages": int,
                "message_queue_size": int,
                "active_tasks": int,
                "total_spokes": int,
                "stats": {
                    "messages_sent": int,
                    "messages_received": int,
                    "broadcasts": int
                },
                "load_level": "low" | "medium" | "high" | "critical"
            }

        Example:
            >>> load = topo.get_hub_load()
            >>> print(f"Hub load: {load['load_level']}")
            Hub load: medium
        """
        pending_messages = len(self.hub_agent.message_queue)

        # Calculate load level
        if pending_messages < 10:
            load_level = "low"
        elif pending_messages < 50:
            load_level = "medium"
        elif pending_messages < 100:
            load_level = "high"
        else:
            load_level = "critical"

        return {
            "hub_id": self.hub_id,
            "pending_messages": pending_messages,
            "message_queue_size": pending_messages,
            "active_tasks": self.hub_stats["active_tasks"],
            "total_spokes": len(self.spoke_agents),
            "stats": self.hub_stats.copy(),
            "load_level": load_level,
            "measured_at": self._get_timestamp()
        }

    def get_spoke(self, agent_id: str) -> Optional[Agent]:
        """
        Get spoke agent by ID.

        Args:
            agent_id: Unique agent identifier

        Returns:
            Agent object or None if not found
        """
        return self.spoke_agents.get(agent_id)

    def get_hub(self) -> Agent:
        """
        Get hub agent.

        Returns:
            Hub Agent object
        """
        return self.hub_agent

    def update_agent_status(self, agent_id: str, status: str) -> bool:
        """
        Update agent status.

        Args:
            agent_id: Agent identifier (hub or spoke)
            status: New status (idle, working, completed, failed)

        Returns:
            True if updated successfully, False if agent not found
        """
        if agent_id == self.hub_id:
            self.hub_agent.status = status
            logger.info(f"Updated hub {agent_id} status to {status}")
            return True

        if agent_id in self.spoke_agents:
            self.spoke_agents[agent_id].status = status
            logger.info(f"Updated spoke {agent_id} status to {status}")
            return True

        logger.warning(f"Agent {agent_id} not found")
        return False

    def get_topology_stats(self) -> Dict[str, Any]:
        """
        Get topology statistics.

        Returns:
            Dict with topology info: {
                "hub_id": str,
                "total_spokes": int,
                "hub_status": str,
                "spoke_status_distribution": Dict[str, int],
                "total_messages_logged": int,
                "hub_load": {...}
            }
        """
        # Spoke status distribution
        status_dist = defaultdict(int)
        for spoke in self.spoke_agents.values():
            status_dist[spoke.status] += 1

        return {
            "hub_id": self.hub_id,
            "total_spokes": len(self.spoke_agents),
            "hub_status": self.hub_agent.status,
            "spoke_status_distribution": dict(status_dist),
            "total_messages_logged": len(self.message_log),
            "hub_load": self.get_hub_load()
        }

    def visualize(self) -> str:
        """
        Return ASCII star pattern visualization.

        Returns:
            String representation of star topology

        Example:
                  Hub: alfred
                /  |  |  \
            expert-backend expert-frontend
            manager-tdd manager-docs
        """
        lines = []

        # Hub (center)
        lines.append(f"      Hub: {self.hub_id} ({self.hub_agent.status})")

        if not self.spoke_agents:
            lines.append("      (No spokes)")
            return "\n".join(lines)

        # Spokes arranged around hub
        spoke_list = sorted(self.spoke_agents.keys())
        spoke_count = len(spoke_list)

        # Visual connector line
        if spoke_count > 0:
            connector = "    " + "/ " * min(spoke_count, 4) + "|" * max(0, spoke_count - 4)
            lines.append(connector)

        # Spoke names with status
        spoke_lines = []
        for spoke_id in spoke_list:
            spoke = self.spoke_agents[spoke_id]
            spoke_lines.append(f"{spoke_id}({spoke.status})")

        # Group spokes into rows for better readability
        row_size = 3
        for i in range(0, len(spoke_lines), row_size):
            row = spoke_lines[i:i+row_size]
            lines.append("  " + " ".join(row))

        return "\n".join(lines)

    def get_message_log(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get message log history.

        Args:
            limit: Maximum number of messages to return (None = all)

        Returns:
            List of logged messages (newest first)
        """
        if limit is None:
            return list(reversed(self.message_log))
        return list(reversed(self.message_log[-limit:]))

    def clear_message_log(self) -> int:
        """
        Clear message log history.

        Returns:
            Number of messages cleared
        """
        count = len(self.message_log)
        self.message_log.clear()
        logger.info(f"Cleared {count} messages from log")
        return count

    def increment_active_tasks(self, delta: int = 1) -> None:
        """
        Increment active task counter.

        Args:
            delta: Amount to increment (can be negative to decrement)
        """
        self.hub_stats["active_tasks"] = max(0, self.hub_stats["active_tasks"] + delta)

    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO8601 format."""
        return datetime.utcnow().isoformat() + "Z"


__all__ = ["StarTopology", "Agent"]
