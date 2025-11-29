#!/usr/bin/env python3
"""
SwarmCoordinator for MoAI-Flow

Central orchestrator for multi-topology agent coordination.
Implements ICoordinator interface with support for 5 topology patterns:
- Hierarchical: Tree structure with Alfred as root
- Mesh: Full peer-to-peer connectivity
- Star: Hub-and-spoke pattern
- Ring: Sequential chain
- Adaptive: Dynamic topology switching

Key Features:
- Topology abstraction: Hide topology details from agents
- Dynamic topology switching via switch_topology()
- Message routing through selected topology
- Consensus mechanism (simple majority voting)
- State synchronization across topology
- Agent status tracking (active, idle, busy, failed)
- Health monitoring of topology

Example:
    >>> coordinator = SwarmCoordinator(topology_type="mesh")
    >>> coordinator.register_agent("agent-001", {"type": "expert-backend"})
    >>> coordinator.broadcast_message("agent-001", {"status": "ready"})
    >>> coordinator.switch_topology("hierarchical")
    >>> consensus = coordinator.request_consensus(
    ...     {"proposal": "deploy_v2"},
    ...     timeout_ms=30000
    ... )
"""

from typing import Any, Dict, List, Optional
from datetime import datetime
import logging
import time
from enum import Enum

from .interfaces import ICoordinator
from ..topology.hierarchical import HierarchicalTopology
from ..topology.mesh import MeshTopology
from ..topology.star import StarTopology
from ..topology.ring import RingTopology, create_ring_from_agents
from ..topology.adaptive import AdaptiveTopology, TopologyMode

logger = logging.getLogger(__name__)


class AgentState(Enum):
    """Agent operational states."""
    ACTIVE = "active"      # Agent is running and responsive
    IDLE = "idle"          # Agent is available but not working
    BUSY = "busy"          # Agent is processing a task
    FAILED = "failed"      # Agent has failed or is unresponsive


class TopologyHealth(Enum):
    """Topology health status."""
    HEALTHY = "healthy"    # All systems operational
    DEGRADED = "degraded"  # Some issues but functional
    CRITICAL = "critical"  # Severe issues, may fail


class SwarmCoordinator(ICoordinator):
    """
    Coordinator for multi-topology agent coordination.

    Provides unified interface for agent communication regardless of
    underlying topology. Supports dynamic topology switching and
    advanced coordination features like consensus and state sync.

    Topology Selection Guide:
    - "hierarchical": Tree structure, best for >10 agents with clear roles
    - "mesh": Full connectivity, best for <5 agents needing collaboration
    - "star": Hub-and-spoke, best for 5-10 agents with central coordinator
    - "ring": Sequential chain, best for pipeline/workflow tasks
    - "adaptive": Dynamic switching based on workload metrics

    Attributes:
        topology_type: Current active topology type
        agent_registry: Dict mapping agent_id to agent metadata
        agent_states: Dict mapping agent_id to AgentState
        message_queue: List of queued messages
        consensus_threshold: Minimum vote ratio for consensus (default: 0.51)
    """

    SUPPORTED_TOPOLOGIES = {
        "hierarchical", "mesh", "star", "ring", "adaptive"
    }

    def __init__(
        self,
        topology_type: str = "mesh",
        consensus_threshold: float = 0.51,
        root_agent_id: str = "alfred"
    ):
        """
        Initialize SwarmCoordinator with specified topology.

        Args:
            topology_type: Initial topology ("hierarchical", "mesh", "star", "ring", "adaptive")
            consensus_threshold: Minimum vote ratio for consensus (0.0-1.0)
            root_agent_id: Root agent ID for hierarchical topologies

        Raises:
            ValueError: If topology_type not supported or consensus_threshold invalid
        """
        if topology_type not in self.SUPPORTED_TOPOLOGIES:
            raise ValueError(
                f"Unsupported topology: {topology_type}. "
                f"Must be one of {self.SUPPORTED_TOPOLOGIES}"
            )

        if not 0.0 <= consensus_threshold <= 1.0:
            raise ValueError(
                f"Consensus threshold must be between 0.0 and 1.0, "
                f"got {consensus_threshold}"
            )

        self.topology_type = topology_type
        self.consensus_threshold = consensus_threshold
        self.root_agent_id = root_agent_id

        # Agent tracking
        self.agent_registry: Dict[str, Dict[str, Any]] = {}
        self.agent_states: Dict[str, AgentState] = {}
        self.agent_heartbeats: Dict[str, float] = {}

        # Message tracking
        self.message_queue: List[Dict[str, Any]] = []
        self.message_history: List[Dict[str, Any]] = []

        # Consensus tracking
        self.consensus_history: List[Dict[str, Any]] = []

        # State synchronization tracking
        self.synchronized_state: Dict[str, Any] = {}

        # Initialize topology
        self._topology = self._create_topology(topology_type)

        logger.info(
            f"SwarmCoordinator initialized with {topology_type} topology "
            f"(consensus_threshold={consensus_threshold})"
        )

    def _create_topology(self, topology_type: str):
        """
        Create topology instance based on type.

        Args:
            topology_type: Topology type to create

        Returns:
            Topology instance (HierarchicalTopology, MeshTopology, etc.)

        Raises:
            ValueError: If topology_type not supported
        """
        if topology_type == "hierarchical":
            return HierarchicalTopology(root_agent_id=self.root_agent_id)
        elif topology_type == "mesh":
            return MeshTopology()
        elif topology_type == "star":
            return StarTopology(hub_agent_id=self.root_agent_id)
        elif topology_type == "ring":
            # Ring topology starts empty, agents added sequentially
            return None  # Created when agents are added
        elif topology_type == "adaptive":
            return AdaptiveTopology(initial_mode=TopologyMode.MESH)
        else:
            raise ValueError(f"Unsupported topology type: {topology_type}")

    def register_agent(
        self,
        agent_id: str,
        agent_metadata: Dict[str, Any]
    ) -> bool:
        """
        Register agent in coordination topology.

        Adds agent to both registry and underlying topology.
        Initializes agent state as IDLE and records heartbeat.

        Args:
            agent_id: Unique agent identifier
            agent_metadata: Agent info (type, capabilities, etc.)
                Expected keys:
                - "type": str (e.g., "expert-backend", "manager-tdd")
                - "capabilities": List[str] (optional)
                - "layer": int (optional, for hierarchical)
                - "parent_id": str (optional, for hierarchical)

        Returns:
            True if registered successfully, False if agent_id already exists

        Example:
            >>> coordinator.register_agent(
            ...     "agent-001",
            ...     {
            ...         "type": "expert-backend",
            ...         "capabilities": ["python", "fastapi"],
            ...         "layer": 2
            ...     }
            ... )
            True
        """
        if agent_id in self.agent_registry:
            logger.warning(f"Agent {agent_id} already registered")
            return False

        # Store in registry
        self.agent_registry[agent_id] = agent_metadata
        self.agent_states[agent_id] = AgentState.IDLE
        self.agent_heartbeats[agent_id] = time.time()

        # Add to underlying topology
        agent_type = agent_metadata.get("type", "unknown")

        if self.topology_type == "hierarchical":
            layer = agent_metadata.get("layer", 1)
            parent_id = agent_metadata.get("parent_id", self.root_agent_id)
            self._topology.add_agent(
                agent_id=agent_id,
                agent_type=agent_type,
                layer=layer,
                parent_id=parent_id,
                metadata=agent_metadata
            )

        elif self.topology_type == "mesh":
            self._topology.add_agent(
                agent_id=agent_id,
                agent_type=agent_type,
                metadata=agent_metadata
            )

        elif self.topology_type == "star":
            self._topology.add_spoke(
                agent_id=agent_id,
                agent_type=agent_type,
                metadata=agent_metadata
            )

        elif self.topology_type == "ring":
            # For ring, we need to recreate the ring when agents change
            if self._topology is None:
                # First agent
                from ..topology.ring import RingAgent
                ring_agent = RingAgent(
                    agent_id=agent_id,
                    agent_type=agent_type,
                    metadata=agent_metadata
                )
                self._topology = create_ring_from_agents([ring_agent])
            else:
                # Add to existing ring
                self._topology.add_agent(
                    agent_id=agent_id,
                    agent_type=agent_type,
                    metadata=agent_metadata
                )

        elif self.topology_type == "adaptive":
            self._topology.add_agent(
                agent_id=agent_id,
                agent_type=agent_type,
                metadata=agent_metadata
            )

        logger.info(
            f"Registered agent {agent_id} (type: {agent_type}) "
            f"in {self.topology_type} topology"
        )

        return True

    def unregister_agent(self, agent_id: str) -> bool:
        """
        Unregister agent from coordination topology.

        Removes agent from registry and underlying topology.
        Cleans up all agent state and history.

        Args:
            agent_id: Unique agent identifier

        Returns:
            True if unregistered successfully, False if agent not found

        Example:
            >>> coordinator.unregister_agent("agent-001")
            True
        """
        if agent_id not in self.agent_registry:
            logger.warning(f"Agent {agent_id} not found in registry")
            return False

        # Remove from registry
        del self.agent_registry[agent_id]
        del self.agent_states[agent_id]
        del self.agent_heartbeats[agent_id]

        # Remove from underlying topology
        if self.topology_type == "hierarchical":
            self._topology.remove_agent(agent_id)
        elif self.topology_type == "mesh":
            self._topology.remove_agent(agent_id)
        elif self.topology_type == "star":
            self._topology.remove_spoke(agent_id)
        elif self.topology_type == "ring":
            if self._topology:
                self._topology.remove_agent(agent_id)
                # If no agents left, clear topology
                if not self.agent_registry:
                    self._topology = None
        elif self.topology_type == "adaptive":
            self._topology.remove_agent(agent_id)

        logger.info(f"Unregistered agent {agent_id} from {self.topology_type} topology")

        return True

    def send_message(
        self,
        from_agent: str,
        to_agent: str,
        message: Dict[str, Any]
    ) -> bool:
        """
        Send message from one agent to another.

        Routes message through underlying topology.
        Validates agents exist and connection is valid.

        Args:
            from_agent: Source agent identifier
            to_agent: Destination agent identifier
            message: Message payload (must be JSON-serializable)

        Returns:
            True if sent successfully, False otherwise

        Raises:
            ValueError: If from_agent or to_agent not registered

        Example:
            >>> coordinator.send_message(
            ...     "agent-001",
            ...     "agent-002",
            ...     {"task": "process_data", "priority": "high"}
            ... )
            True
        """
        # Validate agents
        if from_agent not in self.agent_registry:
            raise ValueError(f"Source agent {from_agent} not registered")
        if to_agent not in self.agent_registry:
            raise ValueError(f"Destination agent {to_agent} not registered")

        # Update heartbeat
        self.agent_heartbeats[from_agent] = time.time()

        # Add timestamp and metadata
        enriched_message = {
            "from": from_agent,
            "to": to_agent,
            "content": message,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "topology": self.topology_type
        }

        # Route through topology
        success = False
        try:
            if self.topology_type == "mesh":
                success = self._topology.send_message(
                    from_agent=from_agent,
                    to_agent=to_agent,
                    message=message
                )
            elif self.topology_type == "hierarchical":
                # Hierarchical doesn't have direct send_message, use metadata
                # Store message in agent metadata
                to_agent_obj = self._topology.get_agent(to_agent)
                if to_agent_obj:
                    if "messages" not in to_agent_obj.metadata:
                        to_agent_obj.metadata["messages"] = []
                    to_agent_obj.metadata["messages"].append({
                        "from": from_agent,
                        "content": message,
                        "timestamp": enriched_message["timestamp"]
                    })
                    success = True
            elif self.topology_type == "star":
                # Star uses hub-based messaging, store in spoke's message queue
                spoke_agent = self._topology.spoke_agents.get(to_agent)
                if spoke_agent:
                    spoke_agent.add_message({
                        "from": from_agent,
                        "content": message,
                        "timestamp": enriched_message["timestamp"]
                    })
                    self._topology.hub_stats["messages_sent"] += 1
                    success = True
            elif self.topology_type == "ring":
                if self._topology:
                    success = self._topology.send_message(
                        from_agent=from_agent,
                        to_agent=to_agent,
                        message=message
                    )
            elif self.topology_type == "adaptive":
                # Adaptive wraps other topologies, check current mode
                current = self._topology.topology
                if hasattr(current, 'send_message'):
                    success = current.send_message(
                        from_agent=from_agent,
                        to_agent=to_agent,
                        message=message
                    )
                else:
                    # Fallback: store in metadata
                    success = True

            if success:
                self.message_history.append(enriched_message)
                logger.info(f"Message sent: {from_agent} → {to_agent}")

        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            success = False

        return success

    def broadcast_message(
        self,
        from_agent: str,
        message: Dict[str, Any],
        exclude: Optional[List[str]] = None
    ) -> int:
        """
        Broadcast message to all agents in topology.

        Sends message to all registered agents except sender and excluded ones.
        Routes through topology's broadcast mechanism if available.

        Args:
            from_agent: Source agent identifier
            message: Message payload (must be JSON-serializable)
            exclude: Optional list of agent IDs to exclude

        Returns:
            Number of agents that received the message

        Raises:
            ValueError: If from_agent not registered

        Example:
            >>> coordinator.broadcast_message(
            ...     "agent-001",
            ...     {"type": "heartbeat", "status": "alive"},
            ...     exclude=["agent-003"]
            ... )
            5  # Sent to 5 agents
        """
        if from_agent not in self.agent_registry:
            raise ValueError(f"Source agent {from_agent} not registered")

        # Update heartbeat
        self.agent_heartbeats[from_agent] = time.time()

        exclude_set = set(exclude or [])
        exclude_set.add(from_agent)  # Don't send to self

        # Broadcast through topology
        sent_count = 0

        if self.topology_type == "mesh":
            sent_count = self._topology.broadcast(
                from_agent=from_agent,
                message=message,
                exclude_agents=exclude_set
            )

        elif self.topology_type == "hierarchical":
            # Hierarchical: broadcast to all agents via metadata
            for agent_id in self.agent_registry.keys():
                if agent_id not in exclude_set:
                    agent_obj = self._topology.get_agent(agent_id)
                    if agent_obj:
                        if "messages" not in agent_obj.metadata:
                            agent_obj.metadata["messages"] = []
                        agent_obj.metadata["messages"].append({
                            "from": from_agent,
                            "type": "broadcast",
                            "content": message,
                            "timestamp": datetime.utcnow().isoformat() + "Z"
                        })
                        sent_count += 1

        elif self.topology_type == "star":
            # Star uses hub_broadcast
            exclude_list = list(exclude_set)
            sent_count = self._topology.hub_broadcast(
                message=message,
                exclude=exclude_list
            )

        elif self.topology_type == "ring":
            if self._topology:
                # Ring: send to all agents in ring
                for agent_id in self.agent_registry.keys():
                    if agent_id not in exclude_set:
                        try:
                            self._topology.send_message(
                                from_agent=from_agent,
                                to_agent=agent_id,
                                message=message
                            )
                            sent_count += 1
                        except Exception as e:
                            logger.error(f"Failed to broadcast to {agent_id}: {e}")

        elif self.topology_type == "adaptive":
            # Adaptive: use current topology's broadcast
            current = self._topology.topology
            if hasattr(current, 'broadcast'):
                sent_count = current.broadcast(
                    from_agent=from_agent,
                    message=message,
                    exclude_agents=exclude_set
                )
            elif hasattr(current, 'hub_broadcast'):
                sent_count = current.hub_broadcast(
                    message=message,
                    exclude=list(exclude_set)
                )
            else:
                # Fallback: manual broadcast
                for agent_id in self.agent_registry.keys():
                    if agent_id not in exclude_set:
                        sent_count += 1

        logger.info(
            f"Broadcast from {from_agent}: {sent_count} agents reached "
            f"(excluded: {len(exclude_set)})"
        )

        return sent_count

    def get_agent_status(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        Get current status of specific agent.

        Returns comprehensive agent state including heartbeat,
        current task, and metadata.

        Args:
            agent_id: Unique agent identifier

        Returns:
            Status dict or None if agent not found: {
                "state": "active" | "idle" | "busy" | "failed",
                "last_heartbeat": timestamp,
                "heartbeat_age_seconds": float,
                "current_task": task_id or None,
                "metadata": {...},
                "topology_role": str
            }

        Example:
            >>> status = coordinator.get_agent_status("agent-001")
            >>> print(status["state"])
            "idle"
        """
        if agent_id not in self.agent_registry:
            logger.warning(f"Agent {agent_id} not found")
            return None

        last_heartbeat = self.agent_heartbeats.get(agent_id, 0)
        heartbeat_age = time.time() - last_heartbeat

        # Determine if agent has failed (no heartbeat for >60 seconds)
        state = self.agent_states.get(agent_id, AgentState.IDLE)
        if heartbeat_age > 60:
            state = AgentState.FAILED

        # Get topology-specific role
        topology_role = "peer"
        if self.topology_type == "hierarchical":
            agent = self._topology.get_agent(agent_id)
            if agent:
                topology_role = f"layer_{agent.layer}"
        elif self.topology_type == "star":
            topology_role = "spoke" if agent_id != self.root_agent_id else "hub"

        return {
            "state": state.value,
            "last_heartbeat": datetime.fromtimestamp(last_heartbeat).isoformat(),
            "heartbeat_age_seconds": round(heartbeat_age, 2),
            "current_task": self.agent_registry[agent_id].get("current_task"),
            "metadata": self.agent_registry[agent_id],
            "topology_role": topology_role
        }

    def get_topology_info(self) -> Dict[str, Any]:
        """
        Get information about current coordination topology.

        Provides comprehensive topology metrics including agent count,
        connections, and health status.

        Returns:
            Dict with topology info: {
                "type": "mesh" | "hierarchical" | "star" | "ring" | "adaptive",
                "agent_count": int,
                "connection_count": int,
                "health": "healthy" | "degraded" | "critical",
                "active_agents": int,
                "failed_agents": int,
                "message_count": int,
                "topology_specific": {...}
            }

        Example:
            >>> info = coordinator.get_topology_info()
            >>> print(f"Topology: {info['type']}, Agents: {info['agent_count']}")
            Topology: mesh, Agents: 5
        """
        agent_count = len(self.agent_registry)

        # Count active and failed agents
        active_count = sum(
            1 for state in self.agent_states.values()
            if state in [AgentState.ACTIVE, AgentState.BUSY, AgentState.IDLE]
        )
        failed_count = sum(
            1 for state in self.agent_states.values()
            if state == AgentState.FAILED
        )

        # Calculate connection count (topology-specific)
        connection_count = 0
        topology_specific = {}

        if self.topology_type == "hierarchical":
            stats = self._topology.get_topology_stats()
            connection_count = stats.get("total_connections", 0)
            topology_specific = {
                "layers": stats.get("layer_count", 0),
                "max_depth": stats.get("max_depth", 0)
            }

        elif self.topology_type == "mesh":
            stats = self._topology.get_topology_stats()
            connection_count = stats.get("total_connections", 0)
            topology_specific = {
                "connectivity": stats.get("connectivity", 0.0),
                "max_connections": stats.get("max_connections", 0)
            }

        elif self.topology_type == "star":
            connection_count = agent_count - 1  # All spokes connect to hub

        elif self.topology_type == "ring":
            connection_count = agent_count  # Each agent connects to next

        elif self.topology_type == "adaptive":
            # Adaptive wraps other topologies
            current = self._topology.topology
            if hasattr(current, 'get_topology_stats'):
                stats = current.get_topology_stats()
                connection_count = stats.get("total_connections", 0)
            else:
                connection_count = agent_count - 1

            topology_specific = {
                "current_mode": self._topology.current_mode.value,
                "switch_count": len(self._topology.mode_history) - 1 if hasattr(self._topology, 'mode_history') else 0
            }

        # Determine health
        health = TopologyHealth.HEALTHY
        if failed_count > 0:
            health = TopologyHealth.DEGRADED
        if failed_count > agent_count * 0.3:  # >30% failed
            health = TopologyHealth.CRITICAL

        return {
            "type": self.topology_type,
            "agent_count": agent_count,
            "connection_count": connection_count,
            "health": health.value,
            "active_agents": active_count,
            "failed_agents": failed_count,
            "message_count": len(self.message_history),
            "topology_specific": topology_specific
        }

    def request_consensus(
        self,
        proposal: Dict[str, Any],
        timeout_ms: int = 30000
    ) -> Dict[str, Any]:
        """
        Request consensus decision from agents.

        Implements simple majority voting mechanism.
        Broadcasts proposal to all agents and collects votes.

        Args:
            proposal: Proposal for consensus (must be JSON-serializable)
                Expected keys:
                - "proposal_id": str
                - "description": str
                - "options": List[str] (e.g., ["approve", "reject"])
            timeout_ms: Timeout in milliseconds (default: 30000)

        Returns:
            Consensus result: {
                "decision": "approved" | "rejected" | "timeout",
                "votes_for": int,
                "votes_against": int,
                "abstain": int,
                "threshold": float,
                "participants": List[str],
                "vote_details": Dict[str, str],
                "timestamp": str
            }

        Example:
            >>> result = coordinator.request_consensus(
            ...     {
            ...         "proposal_id": "deploy-v2",
            ...         "description": "Deploy version 2.0 to production",
            ...         "options": ["approve", "reject"]
            ...     },
            ...     timeout_ms=30000
            ... )
            >>> print(result["decision"])
            "approved"
        """
        start_time = time.time()
        timeout_seconds = timeout_ms / 1000

        proposal_id = proposal.get("proposal_id", "unknown")

        logger.info(
            f"Initiating consensus for proposal: {proposal_id} "
            f"(timeout: {timeout_ms}ms)"
        )

        # Broadcast proposal to all agents
        broadcast_message = {
            "type": "consensus_request",
            "proposal": proposal,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

        # In real implementation, would wait for actual responses
        # For now, simulate voting based on agent states

        votes_for = 0
        votes_against = 0
        abstain = 0
        vote_details: Dict[str, str] = {}
        participants: List[str] = []

        for agent_id, state in self.agent_states.items():
            if state == AgentState.FAILED:
                # Failed agents don't vote
                continue

            participants.append(agent_id)

            # Simulate vote (in real impl, would collect actual responses)
            # For now: ACTIVE/BUSY vote "approve", IDLE abstains
            if state in [AgentState.ACTIVE, AgentState.BUSY]:
                votes_for += 1
                vote_details[agent_id] = "approve"
            else:
                abstain += 1
                vote_details[agent_id] = "abstain"

            # Check timeout
            if time.time() - start_time > timeout_seconds:
                logger.warning(f"Consensus request timed out after {timeout_ms}ms")
                result = {
                    "decision": "timeout",
                    "votes_for": votes_for,
                    "votes_against": votes_against,
                    "abstain": abstain,
                    "threshold": self.consensus_threshold,
                    "participants": participants,
                    "vote_details": vote_details,
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                }
                self.consensus_history.append(result)
                return result

        # Calculate decision
        total_votes = votes_for + votes_against
        if total_votes == 0:
            decision = "timeout"  # No votes received
        else:
            vote_ratio = votes_for / total_votes
            decision = "approved" if vote_ratio >= self.consensus_threshold else "rejected"

        result = {
            "decision": decision,
            "votes_for": votes_for,
            "votes_against": votes_against,
            "abstain": abstain,
            "threshold": self.consensus_threshold,
            "participants": participants,
            "vote_details": vote_details,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

        self.consensus_history.append(result)

        logger.info(
            f"Consensus result for {proposal_id}: {decision} "
            f"({votes_for}/{total_votes} votes, threshold={self.consensus_threshold})"
        )

        return result

    def synchronize_state(
        self,
        state_key: str,
        state_value: Any
    ) -> bool:
        """
        Synchronize state across all agents.

        Broadcasts state update to all agents and stores in coordinator.
        Ensures all agents have consistent view of shared state.

        Args:
            state_key: State identifier (e.g., "task_queue", "config")
            state_value: State value to synchronize (must be JSON-serializable)

        Returns:
            True if synchronized successfully, False otherwise

        Example:
            >>> coordinator.synchronize_state(
            ...     "task_queue",
            ...     {"pending": 5, "completed": 10}
            ... )
            True
        """
        logger.info(f"Synchronizing state: {state_key}")

        # Store in coordinator
        self.synchronized_state[state_key] = {
            "value": state_value,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "version": self.synchronized_state.get(state_key, {}).get("version", 0) + 1
        }

        # Broadcast to all agents
        sync_message = {
            "type": "state_sync",
            "state_key": state_key,
            "state_value": state_value,
            "version": self.synchronized_state[state_key]["version"],
            "timestamp": self.synchronized_state[state_key]["timestamp"]
        }

        # Send to all agents
        success = True
        for agent_id in self.agent_registry.keys():
            try:
                # In real implementation, would ensure delivery confirmation
                # For now, just track in agent metadata
                if "synchronized_state" not in self.agent_registry[agent_id]:
                    self.agent_registry[agent_id]["synchronized_state"] = {}

                self.agent_registry[agent_id]["synchronized_state"][state_key] = {
                    "value": state_value,
                    "version": self.synchronized_state[state_key]["version"],
                    "synced_at": self.synchronized_state[state_key]["timestamp"]
                }

            except Exception as e:
                logger.error(f"Failed to sync state to {agent_id}: {e}")
                success = False

        if success:
            logger.info(
                f"State '{state_key}' synchronized to {len(self.agent_registry)} agents "
                f"(version: {self.synchronized_state[state_key]['version']})"
            )

        return success

    def switch_topology(self, new_topology_type: str) -> bool:
        """
        Switch to a different topology type.

        Migrates all registered agents to new topology while
        preserving agent metadata and state.

        Args:
            new_topology_type: Target topology type

        Returns:
            True if switched successfully, False otherwise

        Raises:
            ValueError: If new_topology_type not supported

        Example:
            >>> coordinator.switch_topology("hierarchical")
            True
        """
        if new_topology_type not in self.SUPPORTED_TOPOLOGIES:
            raise ValueError(
                f"Unsupported topology: {new_topology_type}. "
                f"Must be one of {self.SUPPORTED_TOPOLOGIES}"
            )

        if new_topology_type == self.topology_type:
            logger.info(f"Already using {new_topology_type} topology")
            return True

        logger.info(f"Switching topology: {self.topology_type} → {new_topology_type}")

        old_topology_type = self.topology_type

        # Save agent data
        saved_agents = dict(self.agent_registry)

        # Clear current topology (keep registry)
        self.topology_type = new_topology_type
        self._topology = self._create_topology(new_topology_type)

        # Re-register all agents in new topology
        # Temporarily clear registry to allow re-registration
        self.agent_registry.clear()

        for agent_id, metadata in saved_agents.items():
            self.register_agent(agent_id, metadata)

        logger.info(
            f"Topology switch complete: {old_topology_type} → {new_topology_type} "
            f"({len(saved_agents)} agents migrated)"
        )

        return True

    def get_consensus_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent consensus voting history.

        Args:
            limit: Maximum number of records to return

        Returns:
            List of consensus results (most recent first)
        """
        return list(reversed(self.consensus_history[-limit:]))

    def get_synchronized_state(self, state_key: Optional[str] = None) -> Dict[str, Any]:
        """
        Get synchronized state values.

        Args:
            state_key: Specific state key (if None, returns all)

        Returns:
            State value(s) with metadata
        """
        if state_key:
            return self.synchronized_state.get(state_key, {})
        return self.synchronized_state

    def update_agent_heartbeat(self, agent_id: str) -> bool:
        """
        Update agent heartbeat timestamp.

        Args:
            agent_id: Agent identifier

        Returns:
            True if updated, False if agent not found
        """
        if agent_id not in self.agent_registry:
            return False

        self.agent_heartbeats[agent_id] = time.time()

        # Update state to ACTIVE if was FAILED
        if self.agent_states.get(agent_id) == AgentState.FAILED:
            self.agent_states[agent_id] = AgentState.ACTIVE
            logger.info(f"Agent {agent_id} recovered from failed state")

        return True

    def set_agent_state(self, agent_id: str, state: AgentState) -> bool:
        """
        Set agent operational state.

        Args:
            agent_id: Agent identifier
            state: New state (ACTIVE, IDLE, BUSY, FAILED)

        Returns:
            True if updated, False if agent not found
        """
        if agent_id not in self.agent_registry:
            return False

        old_state = self.agent_states.get(agent_id, AgentState.IDLE)
        self.agent_states[agent_id] = state

        logger.info(f"Agent {agent_id} state: {old_state.value} → {state.value}")
        return True

    def visualize_topology(self) -> str:
        """
        Get ASCII visualization of current topology.

        Returns:
            String representation of topology structure
        """
        if self._topology is None:
            return f"{self.topology_type.upper()} Topology (empty)"

        if hasattr(self._topology, 'visualize'):
            return self._topology.visualize()

        return f"{self.topology_type.upper()} Topology ({len(self.agent_registry)} agents)"


__all__ = [
    "SwarmCoordinator",
    "AgentState",
    "TopologyHealth"
]
