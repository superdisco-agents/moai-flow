"""
MoAI-Flow Core Interfaces

Abstract protocol definitions for:
- IMemoryProvider: Namespace-based memory with persistence
- ICoordinator: Multi-topology agent coordination
- IResourceController: Token budgets, agent quotas, task priority

These interfaces define the contract for swarm coordination components.
All implementations must satisfy these protocols for system integration.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from enum import IntEnum


class Priority(IntEnum):
    """Task priority levels for resource queue management."""
    CRITICAL = 0
    HIGH = 1
    MEDIUM = 2
    LOW = 3
    BACKGROUND = 4


class IMemoryProvider(ABC):
    """
    Memory provider interface for swarm-wide memory management.

    Enables agents to access shared memory with semantic namespace organization.
    Supports both volatile (in-memory) and persistent (database) layers.
    Integrated with SwarmDB for durability.

    Example:
        >>> memory = MemoryProvider()
        >>> memory.store("swarm-001", "context", "task_history", {...})
        >>> data = memory.retrieve("swarm-001", "context", "task_history")
    """

    @abstractmethod
    def store(
        self,
        swarm_id: str,
        namespace: str,
        key: str,
        value: Any,
        persistent: bool = True
    ) -> bool:
        """
        Store value in namespace-scoped memory.

        Args:
            swarm_id: Unique swarm identifier
            namespace: Logical grouping (e.g., "context", "results", "state")
            key: Unique key within namespace
            value: Data to store (must be JSON-serializable)
            persistent: If True, persist to SwarmDB; else keep in-memory only

        Returns:
            True if stored successfully, False otherwise
        """
        pass

    @abstractmethod
    def retrieve(
        self,
        swarm_id: str,
        namespace: str,
        key: str,
        default: Any = None
    ) -> Any:
        """
        Retrieve value from namespace-scoped memory.

        Args:
            swarm_id: Unique swarm identifier
            namespace: Logical grouping
            key: Unique key within namespace
            default: Value to return if key not found

        Returns:
            Stored value or default if not found
        """
        pass

    @abstractmethod
    def delete(
        self,
        swarm_id: str,
        namespace: str,
        key: str
    ) -> bool:
        """
        Delete value from memory.

        Args:
            swarm_id: Unique swarm identifier
            namespace: Logical grouping
            key: Unique key within namespace

        Returns:
            True if deleted successfully, False otherwise
        """
        pass

    @abstractmethod
    def list_keys(
        self,
        swarm_id: str,
        namespace: str,
        pattern: Optional[str] = None
    ) -> List[str]:
        """
        List all keys in namespace matching optional pattern.

        Args:
            swarm_id: Unique swarm identifier
            namespace: Logical grouping
            pattern: Optional glob pattern (e.g., "task_*")

        Returns:
            List of matching keys
        """
        pass

    @abstractmethod
    def clear_namespace(
        self,
        swarm_id: str,
        namespace: str
    ) -> bool:
        """
        Clear all keys in namespace.

        Args:
            swarm_id: Unique swarm identifier
            namespace: Logical grouping

        Returns:
            True if cleared successfully, False otherwise
        """
        pass

    @abstractmethod
    def get_memory_stats(self, swarm_id: str) -> Dict[str, Any]:
        """
        Get memory usage statistics.

        Args:
            swarm_id: Unique swarm identifier

        Returns:
            Dict with stats: {
                "total_keys": int,
                "namespaces": List[str],
                "size_bytes": int,
                "persistent_count": int,
                "volatile_count": int
            }
        """
        pass


class ICoordinator(ABC):
    """
    Coordinator interface for multi-topology agent coordination.

    Abstracts topology management and agent communication.
    Supports multiple topology patterns: hierarchical, mesh, star, ring, adaptive.
    Provides consensus and state synchronization mechanisms.

    Example:
        >>> coordinator = Coordinator(topology="mesh")
        >>> coordinator.register_agent("agent-001", {...})
        >>> coordinator.broadcast_message("agent-001", {"type": "heartbeat"})
    """

    @abstractmethod
    def register_agent(
        self,
        agent_id: str,
        agent_metadata: Dict[str, Any]
    ) -> bool:
        """
        Register agent in coordination topology.

        Args:
            agent_id: Unique agent identifier
            agent_metadata: Agent info (type, capabilities, etc.)

        Returns:
            True if registered successfully, False otherwise
        """
        pass

    @abstractmethod
    def unregister_agent(self, agent_id: str) -> bool:
        """
        Unregister agent from coordination topology.

        Args:
            agent_id: Unique agent identifier

        Returns:
            True if unregistered successfully, False otherwise
        """
        pass

    @abstractmethod
    def send_message(
        self,
        from_agent: str,
        to_agent: str,
        message: Dict[str, Any]
    ) -> bool:
        """
        Send message from one agent to another.

        Args:
            from_agent: Source agent identifier
            to_agent: Destination agent identifier
            message: Message payload (must be JSON-serializable)

        Returns:
            True if sent successfully, False otherwise
        """
        pass

    @abstractmethod
    def broadcast_message(
        self,
        from_agent: str,
        message: Dict[str, Any],
        exclude: Optional[List[str]] = None
    ) -> int:
        """
        Broadcast message to all agents in topology.

        Args:
            from_agent: Source agent identifier
            message: Message payload (must be JSON-serializable)
            exclude: Optional list of agent IDs to exclude

        Returns:
            Number of agents that received the message
        """
        pass

    @abstractmethod
    def get_agent_status(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        Get current status of specific agent.

        Args:
            agent_id: Unique agent identifier

        Returns:
            Status dict or None if agent not found: {
                "state": "active" | "idle" | "busy" | "failed",
                "last_heartbeat": timestamp,
                "current_task": task_id or None,
                "metadata": {...}
            }
        """
        pass

    @abstractmethod
    def get_topology_info(self) -> Dict[str, Any]:
        """
        Get information about current coordination topology.

        Returns:
            Dict with topology info: {
                "type": "mesh" | "hierarchical" | "star" | "ring" | "adaptive",
                "agent_count": int,
                "connection_count": int,
                "health": "healthy" | "degraded" | "critical"
            }
        """
        pass

    @abstractmethod
    def request_consensus(
        self,
        proposal: Dict[str, Any],
        timeout_ms: int = 30000
    ) -> Dict[str, Any]:
        """
        Request consensus decision from agents.

        Args:
            proposal: Proposal for consensus (must be JSON-serializable)
            timeout_ms: Timeout in milliseconds

        Returns:
            Consensus result: {
                "decision": "approved" | "rejected" | "timeout",
                "votes_for": int,
                "votes_against": int,
                "threshold": float,
                "participants": List[str]
            }
        """
        pass

    @abstractmethod
    def synchronize_state(
        self,
        state_key: str,
        state_value: Any
    ) -> bool:
        """
        Synchronize state across all agents.

        Args:
            state_key: State identifier
            state_value: State value to synchronize

        Returns:
            True if synchronized successfully, False otherwise
        """
        pass


class IResourceController(ABC):
    """
    Resource controller interface for token budgets, agent quotas, and task priority.

    Manages resource allocation across swarm members:
    - Token budgets: Allocate and track token consumption
    - Agent quotas: Limit concurrent agents by type
    - Priority queue: Schedule tasks based on priority

    Integrated with .moai/config/config.json for budget configuration.
    Prevents resource exhaustion through quota enforcement.

    Example:
        >>> controller = ResourceController(total_budget=200000)
        >>> controller.allocate_tokens("swarm-001", 50000)
        >>> controller.set_agent_quota("expert-backend", max_concurrent=3)
        >>> controller.enqueue_task("task-001", Priority.HIGH, {...})
    """

    @abstractmethod
    def allocate_tokens(self, swarm_id: str, amount: int) -> bool:
        """
        Allocate token budget to swarm.

        Args:
            swarm_id: Unique swarm identifier
            amount: Number of tokens to allocate

        Returns:
            True if allocated successfully, False if insufficient budget

        Raises:
            ValueError: If amount is negative
        """
        pass

    @abstractmethod
    def consume_tokens(self, swarm_id: str, amount: int) -> bool:
        """
        Consume tokens from swarm's allocated budget.

        Args:
            swarm_id: Unique swarm identifier
            amount: Number of tokens to consume

        Returns:
            True if consumed successfully, False if insufficient balance

        Raises:
            ValueError: If amount is negative
        """
        pass

    @abstractmethod
    def get_token_balance(self, swarm_id: str) -> int:
        """
        Get remaining token balance for swarm.

        Args:
            swarm_id: Unique swarm identifier

        Returns:
            Remaining token balance (0 if swarm not found)
        """
        pass

    @abstractmethod
    def reset_budget(self, swarm_id: str) -> bool:
        """
        Reset swarm's token budget to initial allocation.

        Args:
            swarm_id: Unique swarm identifier

        Returns:
            True if reset successfully, False if swarm not found
        """
        pass

    @abstractmethod
    def set_agent_quota(self, agent_type: str, max_concurrent: int) -> bool:
        """
        Set maximum concurrent agent quota for agent type.

        Args:
            agent_type: Agent type (e.g., "expert-backend", "manager-tdd")
            max_concurrent: Maximum concurrent agents allowed

        Returns:
            True if set successfully, False otherwise

        Raises:
            ValueError: If max_concurrent is negative
        """
        pass

    @abstractmethod
    def request_agent_slot(self, agent_type: str) -> Optional[str]:
        """
        Request slot for agent execution.

        Args:
            agent_type: Agent type (e.g., "expert-backend")

        Returns:
            Slot ID if available, None if quota exceeded

        Example:
            >>> slot_id = controller.request_agent_slot("expert-backend")
            >>> if slot_id:
            ...     # Execute agent work
            ...     controller.release_agent_slot("expert-backend", slot_id)
        """
        pass

    @abstractmethod
    def release_agent_slot(self, agent_type: str, slot_id: str) -> bool:
        """
        Release agent slot after execution.

        Args:
            agent_type: Agent type
            slot_id: Slot ID from request_agent_slot()

        Returns:
            True if released successfully, False if slot not found
        """
        pass

    @abstractmethod
    def get_quota_status(self, agent_type: str) -> Dict[str, int]:
        """
        Get quota status for agent type.

        Args:
            agent_type: Agent type

        Returns:
            Status dict: {
                "max_concurrent": int,
                "active_slots": int,
                "available_slots": int
            }
        """
        pass

    @abstractmethod
    def enqueue_task(
        self,
        task_id: str,
        priority: int,
        task_data: Dict[str, Any]
    ) -> bool:
        """
        Add task to priority queue.

        Args:
            task_id: Unique task identifier
            priority: Priority level (0=CRITICAL, 1=HIGH, 2=MEDIUM, 3=LOW, 4=BACKGROUND)
            task_data: Task metadata and configuration

        Returns:
            True if enqueued successfully, False if task_id exists

        Example:
            >>> controller.enqueue_task(
            ...     "task-001",
            ...     Priority.HIGH,
            ...     {"agent_type": "expert-backend", "spec_id": "SPEC-001"}
            ... )
        """
        pass

    @abstractmethod
    def dequeue_task(self) -> Optional[Dict[str, Any]]:
        """
        Remove and return highest priority task from queue.

        Returns:
            Task dict or None if queue empty: {
                "task_id": str,
                "priority": int,
                "task_data": {...},
                "enqueued_at": timestamp
            }
        """
        pass

    @abstractmethod
    def peek_next_task(self) -> Optional[Dict[str, Any]]:
        """
        View highest priority task without removing.

        Returns:
            Task dict or None if queue empty (same format as dequeue_task)
        """
        pass

    @abstractmethod
    def update_priority(self, task_id: str, new_priority: int) -> bool:
        """
        Update priority of existing task in queue.

        Args:
            task_id: Unique task identifier
            new_priority: New priority level

        Returns:
            True if updated successfully, False if task not found
        """
        pass

    @abstractmethod
    def cancel_task(self, task_id: str) -> bool:
        """
        Remove task from queue.

        Args:
            task_id: Unique task identifier

        Returns:
            True if cancelled successfully, False if task not found
        """
        pass

    @abstractmethod
    def get_resource_usage(self) -> Dict[str, Any]:
        """
        Get overall resource usage statistics.

        Returns:
            Usage dict: {
                "tokens": {
                    "total_budget": int,
                    "allocated": int,
                    "consumed": int,
                    "remaining": int
                },
                "agents": {
                    "total_quotas": int,
                    "active_agents": int,
                    "available_slots": int
                },
                "queue": {
                    "pending_tasks": int,
                    "by_priority": {
                        "CRITICAL": int,
                        "HIGH": int,
                        "MEDIUM": int,
                        "LOW": int,
                        "BACKGROUND": int
                    }
                }
            }
        """
        pass

    @abstractmethod
    def get_bottlenecks(self) -> List[Dict[str, Any]]:
        """
        Identify current resource bottlenecks.

        Returns:
            List of bottleneck reports: [
                {
                    "type": "token_exhaustion" | "quota_exceeded" | "queue_backlog",
                    "severity": "critical" | "warning" | "info",
                    "details": {...},
                    "recommendation": str
                }
            ]

        Example:
            >>> bottlenecks = controller.get_bottlenecks()
            >>> for b in bottlenecks:
            ...     if b["severity"] == "critical":
            ...         print(f"CRITICAL: {b['type']} - {b['recommendation']}")
        """
        pass

    @property
    @abstractmethod
    def total_token_budget(self) -> int:
        """
        Get total token budget across all swarms.

        Returns:
            Total token budget configured
        """
        pass

    @property
    @abstractmethod
    def active_slots(self) -> Dict[str, int]:
        """
        Get active agent slots by type.

        Returns:
            Dict mapping agent_type to active slot count: {
                "expert-backend": 2,
                "manager-tdd": 1,
                ...
            }
        """
        pass


__all__ = [
    "IMemoryProvider",
    "ICoordinator",
    "IResourceController",
    "Priority",
]
