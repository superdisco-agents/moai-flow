#!/usr/bin/env python3
"""
Ring Topology for MoAI-Flow

Sequential chain of agents arranged in circular pattern.
Each agent connects to exactly 2 neighbors (previous, next).

Topology Structure:
    A → B → C → D → E → A (circular)

Use Cases:
- Sequential processing workflows with round-robin execution
- Token-passing coordination patterns
- Pipeline processing with circular feedback
- Load balancing through rotation

Example:
    >>> ring = RingTopology()
    >>> ring.add_agent("agent-1", "expert-backend")
    >>> ring.add_agent("agent-2", "expert-frontend")
    >>> ring.add_agent("agent-3", "expert-database")
    >>> ring.pass_token("agent-1")  # Start token at agent-1
    >>> next_agent = ring.get_token_holder()  # agent-1
    >>> ring.pass_token("agent-1")  # Pass to agent-2
    >>> print(ring.visualize())
    ┌───────┐   ┌───────┐   ┌───────┐
    │ A-1   │ → │ A-2   │ → │ A-3   │
    └───────┘   └───────┘   └───────┘
       ↑                         │
       └─────────────────────────┘
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


@dataclass
class RingAgent:
    """Agent node in ring topology."""
    agent_id: str
    agent_type: str  # e.g., "expert-backend", "manager-tdd"
    position: int  # Position in ring (0, 1, 2, ...)
    status: str = "idle"  # idle, working, completed, failed
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __hash__(self):
        """Make RingAgent hashable for set operations."""
        return hash(self.agent_id)


class RingTopology:
    """
    Ring topology for sequential processing.

    Agents arranged in circular chain, each connected to 2 neighbors.
    Supports clockwise/counterclockwise message flow and token-passing.
    """

    def __init__(self):
        """Initialize empty ring topology."""
        self.agents: List[RingAgent] = []  # Ordered list maintaining ring order
        self.agent_index: Dict[str, int] = {}  # agent_id -> position in list
        self.current_token_holder: Optional[str] = None
        self.message_log: List[Dict[str, Any]] = []  # Message routing history

        logger.info("Initialized ring topology")

    def add_agent(
        self,
        agent_id: str,
        agent_type: str,
        position: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Add agent to ring at specified position (or append to end).

        Args:
            agent_id: Unique agent identifier
            agent_type: Agent type (e.g., "expert-backend")
            position: Insert position (None = append to end)
            metadata: Additional agent metadata

        Returns:
            True if added successfully, False if agent_id already exists

        Example:
            >>> ring.add_agent("agent-1", "expert-backend")
            True
            >>> ring.add_agent("agent-2", "expert-frontend", position=0)
            True  # Inserted at beginning
        """
        if agent_id in self.agent_index:
            logger.warning(f"Agent {agent_id} already exists in ring")
            return False

        # Create new agent
        new_agent = RingAgent(
            agent_id=agent_id,
            agent_type=agent_type,
            position=0,  # Will be updated after insertion
            metadata=metadata or {}
        )

        # Insert at specified position or append
        if position is None or position >= len(self.agents):
            # Append to end
            insert_pos = len(self.agents)
            self.agents.append(new_agent)
        else:
            # Insert at specific position
            insert_pos = max(0, position)
            self.agents.insert(insert_pos, new_agent)

        # Update all positions and index
        self._rebuild_index()

        # If first agent, set as token holder
        if len(self.agents) == 1:
            self.current_token_holder = agent_id

        logger.info(
            f"Added agent {agent_id} ({agent_type}) at position {insert_pos}. "
            f"Ring size: {len(self.agents)}"
        )
        return True

    def remove_agent(self, agent_id: str) -> bool:
        """
        Remove agent from ring and reconnect.

        Args:
            agent_id: Agent to remove

        Returns:
            True if removed successfully, False if not found

        Example:
            >>> ring.add_agent("agent-1", "expert-backend")
            >>> ring.add_agent("agent-2", "expert-frontend")
            >>> ring.remove_agent("agent-1")
            True
        """
        if agent_id not in self.agent_index:
            logger.warning(f"Agent {agent_id} not found in ring")
            return False

        position = self.agent_index[agent_id]
        removed_agent = self.agents.pop(position)

        # If removed agent held token, pass to next
        if self.current_token_holder == agent_id:
            if len(self.agents) > 0:
                # Pass to next agent in ring (wraps around)
                next_pos = position % len(self.agents)
                self.current_token_holder = self.agents[next_pos].agent_id
            else:
                self.current_token_holder = None

        # Update positions and index
        self._rebuild_index()

        logger.info(
            f"Removed agent {agent_id} from position {position}. "
            f"Ring size: {len(self.agents)}"
        )
        return True

    def pass_token(
        self,
        from_agent: str,
        to_next: bool = True,
        steps: int = 1
    ) -> Optional[str]:
        """
        Pass execution token to next/previous agent in ring.

        Args:
            from_agent: Current token holder
            to_next: True for clockwise, False for counterclockwise
            steps: Number of positions to move (default: 1)

        Returns:
            New token holder agent_id, or None if operation failed

        Example:
            >>> ring.pass_token("agent-1")  # Clockwise
            'agent-2'
            >>> ring.pass_token("agent-2", to_next=False)  # Counterclockwise
            'agent-1'
            >>> ring.pass_token("agent-1", steps=2)  # Skip one agent
            'agent-3'
        """
        if from_agent not in self.agent_index:
            logger.error(f"Agent {from_agent} not found in ring")
            return None

        if self.current_token_holder != from_agent:
            logger.warning(
                f"Token holder mismatch: {from_agent} tried to pass token, "
                f"but {self.current_token_holder} holds it"
            )
            return None

        if len(self.agents) == 0:
            logger.error("Cannot pass token in empty ring")
            return None

        # Calculate new position
        current_pos = self.agent_index[from_agent]
        ring_size = len(self.agents)

        if to_next:
            new_pos = (current_pos + steps) % ring_size
        else:
            new_pos = (current_pos - steps) % ring_size

        new_holder = self.agents[new_pos].agent_id
        self.current_token_holder = new_holder

        logger.info(
            f"Token passed from {from_agent} to {new_holder} "
            f"({'clockwise' if to_next else 'counterclockwise'}, {steps} step(s))"
        )
        return new_holder

    def send_message(
        self,
        from_agent: str,
        to_agent: str,
        message: Dict[str, Any],
        clockwise: bool = True
    ) -> Optional[List[str]]:
        """
        Send message through ring from one agent to another.

        Args:
            from_agent: Sender agent ID
            to_agent: Recipient agent ID
            message: Message payload
            clockwise: True for clockwise routing, False for counterclockwise

        Returns:
            List of agent IDs representing message path, or None if failed

        Example:
            >>> path = ring.send_message(
            ...     "agent-1",
            ...     "agent-3",
            ...     {"task": "process_data"}
            ... )
            ['agent-1', 'agent-2', 'agent-3']
        """
        if from_agent not in self.agent_index:
            logger.error(f"Sender {from_agent} not found in ring")
            return None

        if to_agent not in self.agent_index:
            logger.error(f"Recipient {to_agent} not found in ring")
            return None

        if len(self.agents) == 0:
            logger.error("Cannot route message in empty ring")
            return None

        # Calculate path
        from_pos = self.agent_index[from_agent]
        to_pos = self.agent_index[to_agent]
        ring_size = len(self.agents)

        path = []
        current_pos = from_pos

        # Build path
        if clockwise:
            # Clockwise path
            while True:
                path.append(self.agents[current_pos].agent_id)
                if current_pos == to_pos:
                    break
                current_pos = (current_pos + 1) % ring_size
        else:
            # Counterclockwise path
            while True:
                path.append(self.agents[current_pos].agent_id)
                if current_pos == to_pos:
                    break
                current_pos = (current_pos - 1) % ring_size

        # Log message
        message_record = {
            "from": from_agent,
            "to": to_agent,
            "path": path,
            "direction": "clockwise" if clockwise else "counterclockwise",
            "message": message
        }
        self.message_log.append(message_record)

        logger.info(
            f"Message routed from {from_agent} to {to_agent} "
            f"({'clockwise' if clockwise else 'counterclockwise'}). "
            f"Path length: {len(path)}"
        )
        return path

    def get_neighbors(self, agent_id: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Get previous and next neighbors in ring.

        Args:
            agent_id: Agent to query

        Returns:
            Tuple of (previous_agent_id, next_agent_id)

        Example:
            >>> ring.add_agent("agent-1", "type-1")
            >>> ring.add_agent("agent-2", "type-2")
            >>> ring.add_agent("agent-3", "type-3")
            >>> ring.get_neighbors("agent-2")
            ('agent-1', 'agent-3')
        """
        if agent_id not in self.agent_index:
            logger.warning(f"Agent {agent_id} not found in ring")
            return (None, None)

        if len(self.agents) == 0:
            return (None, None)

        pos = self.agent_index[agent_id]
        ring_size = len(self.agents)

        if ring_size == 1:
            # Only one agent - neighbors are itself
            return (agent_id, agent_id)

        prev_pos = (pos - 1) % ring_size
        next_pos = (pos + 1) % ring_size

        prev_agent = self.agents[prev_pos].agent_id
        next_agent = self.agents[next_pos].agent_id

        return (prev_agent, next_agent)

    def rotate_ring(self, positions: int = 1) -> None:
        """
        Rotate ring by N positions (shifts all agents).

        Args:
            positions: Number of positions to rotate (positive=clockwise)

        Example:
            >>> ring.add_agent("agent-1", "type-1")
            >>> ring.add_agent("agent-2", "type-2")
            >>> ring.add_agent("agent-3", "type-3")
            >>> ring.rotate_ring(1)  # agent-2 becomes first
        """
        if len(self.agents) == 0:
            logger.warning("Cannot rotate empty ring")
            return

        ring_size = len(self.agents)
        # Normalize rotation amount
        normalized_rotation = positions % ring_size

        # Rotate the list
        self.agents = (
            self.agents[normalized_rotation:] +
            self.agents[:normalized_rotation]
        )

        # Rebuild index with new positions
        self._rebuild_index()

        logger.info(f"Ring rotated by {normalized_rotation} positions")

    def get_token_holder(self) -> Optional[str]:
        """
        Get current token holder.

        Returns:
            Agent ID holding token, or None if ring is empty

        Example:
            >>> ring.add_agent("agent-1", "type-1")
            >>> ring.get_token_holder()
            'agent-1'
        """
        return self.current_token_holder

    def get_ring_size(self) -> int:
        """
        Get number of agents in ring.

        Returns:
            Number of agents

        Example:
            >>> ring.add_agent("agent-1", "type-1")
            >>> ring.get_ring_size()
            1
        """
        return len(self.agents)

    def get_agent_status(self, agent_id: str) -> Optional[str]:
        """
        Get agent status.

        Args:
            agent_id: Agent to query

        Returns:
            Agent status or None if not found

        Example:
            >>> ring.add_agent("agent-1", "type-1")
            >>> ring.get_agent_status("agent-1")
            'idle'
        """
        if agent_id not in self.agent_index:
            return None

        pos = self.agent_index[agent_id]
        return self.agents[pos].status

    def set_agent_status(self, agent_id: str, status: str) -> bool:
        """
        Set agent status.

        Args:
            agent_id: Agent to update
            status: New status (idle, working, completed, failed)

        Returns:
            True if updated, False if agent not found

        Example:
            >>> ring.set_agent_status("agent-1", "working")
            True
        """
        if agent_id not in self.agent_index:
            logger.warning(f"Agent {agent_id} not found in ring")
            return False

        pos = self.agent_index[agent_id]
        self.agents[pos].status = status

        logger.debug(f"Agent {agent_id} status updated to {status}")
        return True

    def visualize(self, max_width: int = 80) -> str:
        """
        Generate ASCII circular ring visualization.

        Args:
            max_width: Maximum width for ASCII art

        Returns:
            ASCII art representation of ring

        Example:
            >>> print(ring.visualize())
            ┌─────────┐   ┌─────────┐   ┌─────────┐
            │ agent-1 │ → │ agent-2 │ → │ agent-3 │
            │ [TOKEN] │   │  idle   │   │  idle   │
            └─────────┘   └─────────┘   └─────────┘
               ↑                             │
               └─────────────────────────────┘
        """
        if len(self.agents) == 0:
            return "Empty ring"

        lines = []

        # Header
        lines.append("Ring Topology Visualization")
        lines.append("=" * 40)
        lines.append(f"Agents: {len(self.agents)}")
        lines.append(f"Token Holder: {self.current_token_holder or 'None'}")
        lines.append("")

        # Build agent boxes
        agent_boxes = []
        max_id_len = max(len(agent.agent_id) for agent in self.agents)
        box_width = max(max_id_len + 2, 10)

        for agent in self.agents:
            # Top border
            box = ["┌" + "─" * box_width + "┐"]

            # Agent ID
            id_text = agent.agent_id.center(box_width)
            box.append("│" + id_text + "│")

            # Token indicator or status
            if agent.agent_id == self.current_token_holder:
                status_text = "[TOKEN]".center(box_width)
            else:
                status_text = agent.status.center(box_width)
            box.append("│" + status_text + "│")

            # Bottom border
            box.append("└" + "─" * box_width + "┘")

            agent_boxes.append(box)

        # Layout agents in circular pattern
        if len(self.agents) <= 4:
            # Small ring - show in single line
            for row_idx in range(4):
                row_parts = []
                for box_idx, box in enumerate(agent_boxes):
                    row_parts.append(box[row_idx])
                    if box_idx < len(agent_boxes) - 1:
                        if row_idx == 1:  # Arrow on middle row
                            row_parts.append(" → ")
                        else:
                            row_parts.append("   ")
                lines.append("".join(row_parts))

            # Add circular connection
            if len(self.agents) > 1:
                lines.append("   ↑" + " " * (box_width * len(self.agents) + 3 * (len(self.agents) - 1) - 6) + "│")
                lines.append("   └" + "─" * (box_width * len(self.agents) + 3 * (len(self.agents) - 1) - 6) + "┘")
        else:
            # Large ring - show summary
            lines.append("Large Ring (showing first 3 agents):")
            lines.append("")

            for i in range(min(3, len(self.agents))):
                agent = self.agents[i]
                token_mark = "[TOKEN] " if agent.agent_id == self.current_token_holder else ""
                lines.append(f"  {i}: {token_mark}{agent.agent_id} ({agent.status})")

            if len(self.agents) > 3:
                lines.append(f"  ... ({len(self.agents) - 3} more agents)")

            lines.append("")
            lines.append("Ring connection: (last) → (first)")

        # Message log summary
        if self.message_log:
            lines.append("")
            lines.append(f"Recent Messages: {len(self.message_log)}")
            for msg in self.message_log[-3:]:  # Last 3 messages
                path_str = " → ".join(msg["path"][:3])
                if len(msg["path"]) > 3:
                    path_str += " → ..."
                lines.append(f"  {msg['from']} → {msg['to']}: {path_str}")

        return "\n".join(lines)

    def _rebuild_index(self):
        """
        Rebuild agent_index and update positions after changes.

        Internal method called after add/remove/rotate operations.
        """
        self.agent_index.clear()
        for pos, agent in enumerate(self.agents):
            agent.position = pos
            self.agent_index[agent.agent_id] = pos

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get ring topology statistics.

        Returns:
            Dictionary with statistics

        Example:
            >>> stats = ring.get_statistics()
            >>> stats["ring_size"]
            3
        """
        status_counts = {}
        for agent in self.agents:
            status_counts[agent.status] = status_counts.get(agent.status, 0) + 1

        return {
            "ring_size": len(self.agents),
            "token_holder": self.current_token_holder,
            "agent_types": list(set(agent.agent_type for agent in self.agents)),
            "status_distribution": status_counts,
            "message_count": len(self.message_log)
        }


# Convenience functions

def create_ring_from_agents(agent_configs: List[Dict[str, Any]]) -> RingTopology:
    """
    Create ring topology from agent configurations.

    Args:
        agent_configs: List of dicts with 'agent_id', 'agent_type', 'metadata'

    Returns:
        Configured RingTopology

    Example:
        >>> configs = [
        ...     {"agent_id": "agent-1", "agent_type": "expert-backend"},
        ...     {"agent_id": "agent-2", "agent_type": "expert-frontend"},
        ... ]
        >>> ring = create_ring_from_agents(configs)
    """
    ring = RingTopology()

    for config in agent_configs:
        ring.add_agent(
            agent_id=config["agent_id"],
            agent_type=config["agent_type"],
            metadata=config.get("metadata")
        )

    return ring
