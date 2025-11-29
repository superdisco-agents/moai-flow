#!/usr/bin/env python3
"""
Hierarchical Topology for MoAI-Flow

Tree-structured agent coordination with Alfred as root.
Delegates tasks down the hierarchy and aggregates results upward.

Topology Structure:
    Alfred (Root)
      ├─ Manager Layer (e.g., manager-tdd, manager-docs)
      │   ├─ Specialist Layer (e.g., expert-backend, expert-frontend)
      │   └─ ...
      └─ ...

Use Cases:
- Complex multi-step projects requiring orchestration
- Clear command chain with accountability
- Coordinated parallel execution across teams

Example:
    >>> topo = HierarchicalTopology(root_agent_id="alfred")
    >>> topo.add_layer("managers", ["manager-tdd", "manager-docs"])
    >>> topo.add_layer("specialists", ["expert-backend", "expert-frontend"])
    >>> print(topo.visualize())
    Alfred (Root)
    ├─ manager-tdd
    │   ├─ expert-backend
    │   └─ expert-frontend
    └─ manager-docs
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set
import logging

logger = logging.getLogger(__name__)


@dataclass
class Agent:
    """Agent node in hierarchy."""
    agent_id: str
    agent_type: str  # e.g., "alfred", "manager-tdd", "expert-backend"
    layer: int  # 0 = root, 1 = managers, 2 = specialists
    parent_id: Optional[str] = None
    children: Set[str] = field(default_factory=set)
    status: str = "idle"  # idle, working, completed, failed
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __hash__(self):
        """Make Agent hashable for set operations."""
        return hash(self.agent_id)


class HierarchicalTopology:
    """
    Hierarchical (tree) topology for swarm coordination.

    Alfred acts as root coordinator, delegating to managers,
    who delegate to specialists. Results aggregate upward.
    """

    def __init__(self, root_agent_id: str = "alfred"):
        """
        Initialize hierarchical topology with root agent.

        Args:
            root_agent_id: Unique identifier for root agent (default: "alfred")
        """
        self.root_id = root_agent_id
        self.agents: Dict[str, Agent] = {}
        self.layers: Dict[int, Set[str]] = {}  # layer_num -> agent_ids
        self._layer_counter = 0

        # Add root agent
        self.add_agent(root_agent_id, "alfred", layer=0)
        logger.info(f"Initialized hierarchical topology with root: {root_agent_id}")

    def add_agent(
        self,
        agent_id: str,
        agent_type: str,
        layer: int,
        parent_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Add agent to hierarchy at specified layer.

        Args:
            agent_id: Unique agent identifier
            agent_type: Agent type (e.g., "manager-tdd", "expert-backend")
            layer: Layer number (0=root, 1=managers, 2=specialists, etc.)
            parent_id: Parent agent ID (optional, inferred if not provided)
            metadata: Additional agent metadata

        Returns:
            True if added successfully, False if agent_id already exists

        Raises:
            ValueError: If layer is negative or parent_id not found
        """
        if agent_id in self.agents:
            logger.warning(f"Agent {agent_id} already exists in topology")
            return False

        if layer < 0:
            raise ValueError(f"Layer must be non-negative, got: {layer}")

        # Validate parent exists if provided
        if parent_id and parent_id not in self.agents:
            raise ValueError(f"Parent agent {parent_id} not found in topology")

        # Prevent cycles: ensure we're not making a cycle
        if parent_id and self._would_create_cycle(agent_id, parent_id):
            raise ValueError(f"Adding agent {agent_id} with parent {parent_id} would create a cycle")

        # Create new agent
        agent = Agent(
            agent_id=agent_id,
            agent_type=agent_type,
            layer=layer,
            parent_id=parent_id,
            metadata=metadata or {}
        )

        self.agents[agent_id] = agent

        # Update layers mapping
        if layer not in self.layers:
            self.layers[layer] = set()
        self.layers[layer].add(agent_id)

        # Update parent's children if parent exists
        if parent_id:
            parent = self.agents[parent_id]
            parent.children.add(agent_id)

        logger.info(f"Added agent {agent_id} (type: {agent_type}) at layer {layer}")
        return True

    def _would_create_cycle(self, agent_id: str, parent_id: str) -> bool:
        """
        Check if adding this parent-child relationship would create a cycle.

        Args:
            agent_id: ID of agent being added
            parent_id: ID of proposed parent

        Returns:
            True if cycle would be created, False otherwise
        """
        # Walk up from parent_id to root
        # If we encounter agent_id, it's a cycle
        visited = set()
        current = parent_id

        while current:
            if current == agent_id:
                return True
            if current in visited:
                # Existing cycle (shouldn't happen in valid tree)
                return True
            visited.add(current)
            current = self.agents[current].parent_id if current in self.agents else None

        return False

    def add_layer(
        self,
        layer_name: str,
        agent_types: List[str],
        parent_id: Optional[str] = None
    ) -> int:
        """
        Add a new layer of agents (e.g., managers, specialists).

        Args:
            layer_name: Descriptive layer name (for metadata)
            agent_types: List of agent types to add (e.g., ["manager-tdd", "manager-docs"])
            parent_id: Parent agent ID (if None, uses root)

        Returns:
            Layer number assigned

        Raises:
            ValueError: If parent_id not found or agent_types is empty

        Example:
            >>> topo.add_layer("managers", ["manager-tdd", "manager-docs"])
            1
            >>> topo.add_layer("specialists", ["expert-backend", "expert-frontend"], parent_id="manager-tdd")
            2
        """
        if not agent_types:
            raise ValueError("agent_types cannot be empty")

        # Determine parent (default to root)
        parent_id = parent_id or self.root_id
        if parent_id not in self.agents:
            raise ValueError(f"Parent agent {parent_id} not found")

        # Calculate layer number (parent layer + 1)
        parent_layer = self.agents[parent_id].layer
        layer_num = parent_layer + 1

        # Add all agents in this layer
        added_count = 0
        for agent_type in agent_types:
            # Generate unique agent_id
            agent_id = agent_type  # Simple approach: use agent_type as ID

            # Check if agent_id already exists
            if agent_id in self.agents:
                logger.warning(f"Agent {agent_id} already exists, skipping")
                continue

            success = self.add_agent(
                agent_id=agent_id,
                agent_type=agent_type,
                layer=layer_num,
                parent_id=parent_id,
                metadata={"layer_name": layer_name}
            )

            if success:
                added_count += 1

        logger.info(f"Added {added_count}/{len(agent_types)} agents to layer {layer_num} ({layer_name})")
        return layer_num

    def delegate_task(
        self,
        from_agent: str,
        to_agent: str,
        task: Dict[str, Any]
    ) -> bool:
        """
        Delegate task from parent to child in hierarchy.

        Args:
            from_agent: Parent agent ID
            to_agent: Child agent ID
            task: Task data (must be JSON-serializable)

        Returns:
            True if delegated successfully, False otherwise

        Raises:
            ValueError: If from_agent or to_agent not found
        """
        if from_agent not in self.agents:
            raise ValueError(f"Agent {from_agent} not found")
        if to_agent not in self.agents:
            raise ValueError(f"Agent {to_agent} not found")

        parent = self.agents[from_agent]
        child = self.agents[to_agent]

        # Verify delegation is valid (parent → child)
        if to_agent not in parent.children:
            logger.warning(f"{to_agent} is not a child of {from_agent}, delegation may not follow hierarchy")

        # Update statuses
        child.status = "working"

        # Store task in child's metadata
        if "tasks" not in child.metadata:
            child.metadata["tasks"] = []
        child.metadata["tasks"].append({
            "from": from_agent,
            "task": task,
            "delegated_at": self._get_timestamp()
        })

        logger.info(f"Delegated task from {from_agent} to {to_agent}")
        return True

    def aggregate_results(
        self,
        agent_id: str
    ) -> Dict[str, Any]:
        """
        Aggregate results from all children of an agent.

        Args:
            agent_id: Agent ID to aggregate results for

        Returns:
            Dict with aggregated results: {
                "agent_id": str,
                "children_count": int,
                "results": List[Dict],
                "all_completed": bool
            }

        Raises:
            ValueError: If agent_id not found
        """
        if agent_id not in self.agents:
            raise ValueError(f"Agent {agent_id} not found")

        agent = self.agents[agent_id]

        # Collect results from all children
        results = []
        all_completed = True

        for child_id in agent.children:
            child = self.agents[child_id]

            # Check if child completed
            if child.status != "completed":
                all_completed = False

            # Extract results from child's metadata
            child_results = child.metadata.get("results", [])
            results.append({
                "agent_id": child_id,
                "agent_type": child.agent_type,
                "status": child.status,
                "results": child_results
            })

        aggregated = {
            "agent_id": agent_id,
            "children_count": len(agent.children),
            "results": results,
            "all_completed": all_completed
        }

        logger.info(f"Aggregated results for {agent_id}: {len(results)} children, all_completed={all_completed}")
        return aggregated

    def get_path_to_root(self, agent_id: str) -> List[str]:
        """
        Get path from agent to root (for result bubbling).

        Args:
            agent_id: Agent ID to find path for

        Returns:
            List of agent IDs from agent to root (inclusive)

        Raises:
            ValueError: If agent_id not found

        Example:
            >>> topo.get_path_to_root("expert-backend")
            ["expert-backend", "manager-tdd", "alfred"]
        """
        if agent_id not in self.agents:
            raise ValueError(f"Agent {agent_id} not found")

        path = []
        current = agent_id
        visited = set()

        while current:
            if current in visited:
                # Cycle detected (shouldn't happen in valid tree)
                logger.error(f"Cycle detected while traversing from {agent_id}")
                break

            path.append(current)
            visited.add(current)

            # Move to parent
            agent = self.agents[current]
            current = agent.parent_id

        return path

    def get_layer_agents(self, layer: int) -> List[Agent]:
        """
        Get all agents at a specific layer.

        Args:
            layer: Layer number (0=root, 1=managers, etc.)

        Returns:
            List of Agent objects at that layer
        """
        if layer not in self.layers:
            return []

        agent_ids = self.layers[layer]
        return [self.agents[aid] for aid in agent_ids]

    def visualize(self) -> str:
        """
        Return ASCII tree visualization of hierarchy.

        Returns:
            String representation of tree structure

        Example:
            Alfred (Root)
            ├─ manager-tdd
            │   ├─ expert-backend
            │   └─ expert-frontend
            └─ manager-docs
        """
        lines = []

        def build_tree(agent_id: str, prefix: str = "", is_last: bool = True):
            """Recursively build tree visualization."""
            agent = self.agents[agent_id]

            # Current node
            connector = "└─ " if is_last else "├─ "
            if agent.layer == 0:
                lines.append(f"{agent.agent_id} (Root)")
            else:
                lines.append(f"{prefix}{connector}{agent.agent_id}")

            # Children
            children = sorted(agent.children)  # Sort for consistent output
            for i, child_id in enumerate(children):
                is_last_child = (i == len(children) - 1)
                new_prefix = prefix + ("    " if is_last else "│   ")
                build_tree(child_id, new_prefix, is_last_child)

        build_tree(self.root_id)
        return "\n".join(lines)

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

    def get_topology_stats(self) -> Dict[str, Any]:
        """
        Get topology statistics.

        Returns:
            Dict with topology info: {
                "total_agents": int,
                "total_layers": int,
                "root_id": str,
                "agents_per_layer": Dict[int, int],
                "status_distribution": Dict[str, int]
            }
        """
        status_dist = {}
        for agent in self.agents.values():
            status_dist[agent.status] = status_dist.get(agent.status, 0) + 1

        agents_per_layer = {
            layer: len(agent_ids) for layer, agent_ids in self.layers.items()
        }

        return {
            "total_agents": len(self.agents),
            "total_layers": len(self.layers),
            "root_id": self.root_id,
            "agents_per_layer": agents_per_layer,
            "status_distribution": status_dist
        }

    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO8601 format."""
        from datetime import datetime
        return datetime.utcnow().isoformat() + "Z"


__all__ = ["HierarchicalTopology", "Agent"]
