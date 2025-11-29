"""
Comprehensive tests for MoAI-Flow Core Interfaces.

Tests cover:
- IMemoryProvider: Namespace-based memory with persistence
- ICoordinator: Multi-topology agent coordination
- IResourceController: Token budgets, agent quotas, task priority

Following TDD RED-GREEN-REFACTOR cycle with 90%+ coverage target.
All tests use mock implementations to validate interface contracts.
"""

import sys
from pathlib import Path

# Add moai-flow directory to Python path
project_root = Path(__file__).parent.parent.parent.parent
moai_flow_path = project_root / "moai-flow"
sys.path.insert(0, str(moai_flow_path))

import pytest
from typing import Any, Dict, List, Optional
from datetime import datetime

from core.interfaces import (
    IMemoryProvider,
    ICoordinator,
    IResourceController,
    Priority,
)


# ==========================================
# Mock Implementations
# ==========================================


class MockMemoryProvider(IMemoryProvider):
    """Mock implementation of IMemoryProvider for testing."""

    def __init__(self):
        """Initialize mock memory provider with in-memory storage."""
        # Format: {swarm_id: {namespace: {key: (value, persistent)}}}
        self._memory: Dict[str, Dict[str, Dict[str, tuple]]] = {}
        self._db: Dict[str, Dict[str, Dict[str, Any]]] = {}  # Persistent storage

    def store(
        self,
        swarm_id: str,
        namespace: str,
        key: str,
        value: Any,
        persistent: bool = True
    ) -> bool:
        """Store value in namespace-scoped memory."""
        if swarm_id not in self._memory:
            self._memory[swarm_id] = {}
        if namespace not in self._memory[swarm_id]:
            self._memory[swarm_id][namespace] = {}

        self._memory[swarm_id][namespace][key] = (value, persistent)

        # Store in persistent layer if requested
        if persistent:
            if swarm_id not in self._db:
                self._db[swarm_id] = {}
            if namespace not in self._db[swarm_id]:
                self._db[swarm_id][namespace] = {}
            self._db[swarm_id][namespace][key] = value

        return True

    def retrieve(
        self,
        swarm_id: str,
        namespace: str,
        key: str,
        default: Any = None
    ) -> Any:
        """Retrieve value from namespace-scoped memory."""
        try:
            value, _ = self._memory[swarm_id][namespace][key]
            return value
        except KeyError:
            # Try persistent storage
            try:
                return self._db[swarm_id][namespace][key]
            except KeyError:
                return default

    def delete(
        self,
        swarm_id: str,
        namespace: str,
        key: str
    ) -> bool:
        """Delete value from memory."""
        deleted = False

        # Delete from volatile memory
        try:
            del self._memory[swarm_id][namespace][key]
            deleted = True
        except KeyError:
            pass

        # Delete from persistent storage
        try:
            del self._db[swarm_id][namespace][key]
            deleted = True
        except KeyError:
            pass

        return deleted

    def list_keys(
        self,
        swarm_id: str,
        namespace: str,
        pattern: Optional[str] = None
    ) -> List[str]:
        """List all keys in namespace matching optional pattern."""
        try:
            keys = list(self._memory[swarm_id][namespace].keys())
            if pattern:
                # Simple glob pattern matching
                import fnmatch
                keys = [k for k in keys if fnmatch.fnmatch(k, pattern)]
            return sorted(keys)
        except KeyError:
            return []

    def clear_namespace(
        self,
        swarm_id: str,
        namespace: str
    ) -> bool:
        """Clear all keys in namespace."""
        cleared = False

        # Clear volatile
        try:
            self._memory[swarm_id][namespace].clear()
            cleared = True
        except KeyError:
            pass

        # Clear persistent
        try:
            self._db[swarm_id][namespace].clear()
            cleared = True
        except KeyError:
            pass

        return cleared

    def get_memory_stats(self, swarm_id: str) -> Dict[str, Any]:
        """Get memory usage statistics."""
        stats = {
            "total_keys": 0,
            "namespaces": [],
            "size_bytes": 0,
            "persistent_count": 0,
            "volatile_count": 0
        }

        if swarm_id in self._memory:
            for namespace, keys_dict in self._memory[swarm_id].items():
                stats["namespaces"].append(namespace)
                stats["total_keys"] += len(keys_dict)
                for value, persistent in keys_dict.values():
                    if persistent:
                        stats["persistent_count"] += 1
                    else:
                        stats["volatile_count"] += 1
                    # Rough size estimate
                    stats["size_bytes"] += len(str(value).encode('utf-8'))

        return stats


class MockCoordinator(ICoordinator):
    """Mock implementation of ICoordinator for testing."""

    def __init__(self):
        """Initialize mock coordinator."""
        self._agents: Dict[str, Dict[str, Any]] = {}
        self._messages: Dict[str, List[Dict[str, Any]]] = {}
        self._topology_type = "mesh"

    def register_agent(
        self,
        agent_id: str,
        agent_metadata: Dict[str, Any]
    ) -> bool:
        """Register agent in coordination topology."""
        if agent_id in self._agents:
            return False

        self._agents[agent_id] = {
            "metadata": agent_metadata,
            "registered_at": datetime.utcnow().isoformat(),
            "last_heartbeat": datetime.utcnow().isoformat(),
            "state": "active"
        }
        self._messages[agent_id] = []
        return True

    def unregister_agent(self, agent_id: str) -> bool:
        """Unregister agent from coordination topology."""
        if agent_id not in self._agents:
            return False

        del self._agents[agent_id]
        del self._messages[agent_id]
        return True

    def send_message(
        self,
        from_agent: str,
        to_agent: str,
        message: Dict[str, Any]
    ) -> bool:
        """Send message from one agent to another."""
        if to_agent not in self._agents:
            return False

        msg = {
            "from": from_agent,
            "to": to_agent,
            "payload": message,
            "timestamp": datetime.utcnow().isoformat()
        }
        self._messages[to_agent].append(msg)
        return True

    def broadcast_message(
        self,
        from_agent: str,
        message: Dict[str, Any],
        exclude: Optional[List[str]] = None
    ) -> int:
        """Broadcast message to all agents in topology."""
        exclude = exclude or []
        count = 0

        for agent_id in self._agents.keys():
            if agent_id != from_agent and agent_id not in exclude:
                if self.send_message(from_agent, agent_id, message):
                    count += 1

        return count

    def get_agent_status(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of specific agent."""
        if agent_id not in self._agents:
            return None

        return {
            "state": self._agents[agent_id]["state"],
            "last_heartbeat": self._agents[agent_id]["last_heartbeat"],
            "current_task": None,
            "metadata": self._agents[agent_id]["metadata"]
        }

    def get_topology_info(self) -> Dict[str, Any]:
        """Get information about current coordination topology."""
        return {
            "type": self._topology_type,
            "agent_count": len(self._agents),
            "connection_count": len(self._agents) * (len(self._agents) - 1) if self._topology_type == "mesh" else len(self._agents),
            "health": "healthy" if len(self._agents) > 0 else "degraded"
        }

    def request_consensus(
        self,
        proposal: Dict[str, Any],
        timeout_ms: int = 30000
    ) -> Dict[str, Any]:
        """Request consensus decision from agents."""
        # Simple majority voting mock
        agent_count = len(self._agents)
        votes_for = int(agent_count * 0.7)  # 70% approval
        votes_against = agent_count - votes_for

        return {
            "decision": "approved" if votes_for > votes_against else "rejected",
            "votes_for": votes_for,
            "votes_against": votes_against,
            "threshold": 0.66,
            "participants": list(self._agents.keys())
        }

    def synchronize_state(
        self,
        state_key: str,
        state_value: Any
    ) -> bool:
        """Synchronize state across all agents."""
        if not self._agents:
            return False

        # In mock, just store in each agent's state
        for agent_id in self._agents.keys():
            if "sync_state" not in self._agents[agent_id]:
                self._agents[agent_id]["sync_state"] = {}
            self._agents[agent_id]["sync_state"][state_key] = state_value

        return True


class MockResourceController(IResourceController):
    """Mock implementation of IResourceController for testing."""

    def __init__(self, total_budget: int = 200000):
        """Initialize mock resource controller."""
        self._total_budget = total_budget
        self._swarm_budgets: Dict[str, Dict[str, int]] = {}  # {swarm_id: {allocated, consumed}}
        self._agent_quotas: Dict[str, int] = {}  # {agent_type: max_concurrent}
        self._active_slots: Dict[str, List[str]] = {}  # {agent_type: [slot_ids]}
        self._task_queue: List[Dict[str, Any]] = []

    def allocate_tokens(self, swarm_id: str, amount: int) -> bool:
        """Allocate token budget to swarm."""
        if amount < 0:
            raise ValueError("Amount must be non-negative")

        if swarm_id not in self._swarm_budgets:
            self._swarm_budgets[swarm_id] = {"allocated": 0, "consumed": 0}

        # Check if total allocation exceeds budget
        total_allocated = sum(b["allocated"] for b in self._swarm_budgets.values()) + amount
        if total_allocated > self._total_budget:
            return False

        self._swarm_budgets[swarm_id]["allocated"] += amount
        return True

    def consume_tokens(self, swarm_id: str, amount: int) -> bool:
        """Consume tokens from swarm's allocated budget."""
        if amount < 0:
            raise ValueError("Amount must be non-negative")

        if swarm_id not in self._swarm_budgets:
            return False

        budget = self._swarm_budgets[swarm_id]
        remaining = budget["allocated"] - budget["consumed"]

        if amount > remaining:
            return False

        budget["consumed"] += amount
        return True

    def get_token_balance(self, swarm_id: str) -> int:
        """Get remaining token balance for swarm."""
        if swarm_id not in self._swarm_budgets:
            return 0

        budget = self._swarm_budgets[swarm_id]
        return budget["allocated"] - budget["consumed"]

    def reset_budget(self, swarm_id: str) -> bool:
        """Reset swarm's token budget to initial allocation."""
        if swarm_id not in self._swarm_budgets:
            return False

        self._swarm_budgets[swarm_id]["consumed"] = 0
        return True

    def set_agent_quota(self, agent_type: str, max_concurrent: int) -> bool:
        """Set maximum concurrent agent quota for agent type."""
        if max_concurrent < 0:
            raise ValueError("max_concurrent must be non-negative")

        self._agent_quotas[agent_type] = max_concurrent
        if agent_type not in self._active_slots:
            self._active_slots[agent_type] = []
        return True

    def request_agent_slot(self, agent_type: str) -> Optional[str]:
        """Request slot for agent execution."""
        if agent_type not in self._agent_quotas:
            return None

        if agent_type not in self._active_slots:
            self._active_slots[agent_type] = []

        max_concurrent = self._agent_quotas[agent_type]
        if len(self._active_slots[agent_type]) >= max_concurrent:
            return None

        # Generate slot ID
        slot_id = f"{agent_type}-slot-{len(self._active_slots[agent_type])}"
        self._active_slots[agent_type].append(slot_id)
        return slot_id

    def release_agent_slot(self, agent_type: str, slot_id: str) -> bool:
        """Release agent slot after execution."""
        if agent_type not in self._active_slots:
            return False

        try:
            self._active_slots[agent_type].remove(slot_id)
            return True
        except ValueError:
            return False

    def get_quota_status(self, agent_type: str) -> Dict[str, int]:
        """Get quota status for agent type."""
        if agent_type not in self._agent_quotas:
            return {"max_concurrent": 0, "active_slots": 0, "available_slots": 0}

        max_concurrent = self._agent_quotas[agent_type]
        active = len(self._active_slots.get(agent_type, []))

        return {
            "max_concurrent": max_concurrent,
            "active_slots": active,
            "available_slots": max_concurrent - active
        }

    def enqueue_task(
        self,
        task_id: str,
        priority: int,
        task_data: Dict[str, Any]
    ) -> bool:
        """Add task to priority queue."""
        # Check if task already exists
        if any(t["task_id"] == task_id for t in self._task_queue):
            return False

        task = {
            "task_id": task_id,
            "priority": priority,
            "task_data": task_data,
            "enqueued_at": datetime.utcnow().isoformat()
        }
        self._task_queue.append(task)
        # Sort by priority (lower number = higher priority)
        self._task_queue.sort(key=lambda t: t["priority"])
        return True

    def dequeue_task(self) -> Optional[Dict[str, Any]]:
        """Remove and return highest priority task from queue."""
        if not self._task_queue:
            return None
        return self._task_queue.pop(0)

    def peek_next_task(self) -> Optional[Dict[str, Any]]:
        """View highest priority task without removing."""
        if not self._task_queue:
            return None
        return self._task_queue[0].copy()

    def update_priority(self, task_id: str, new_priority: int) -> bool:
        """Update priority of existing task in queue."""
        for task in self._task_queue:
            if task["task_id"] == task_id:
                task["priority"] = new_priority
                # Re-sort queue
                self._task_queue.sort(key=lambda t: t["priority"])
                return True
        return False

    def cancel_task(self, task_id: str) -> bool:
        """Remove task from queue."""
        for i, task in enumerate(self._task_queue):
            if task["task_id"] == task_id:
                del self._task_queue[i]
                return True
        return False

    def get_resource_usage(self) -> Dict[str, Any]:
        """Get overall resource usage statistics."""
        allocated = sum(b["allocated"] for b in self._swarm_budgets.values())
        consumed = sum(b["consumed"] for b in self._swarm_budgets.values())

        # Count tasks by priority
        priority_counts = {
            "CRITICAL": 0,
            "HIGH": 0,
            "MEDIUM": 0,
            "LOW": 0,
            "BACKGROUND": 0
        }
        priority_names = ["CRITICAL", "HIGH", "MEDIUM", "LOW", "BACKGROUND"]
        for task in self._task_queue:
            priority_idx = task["priority"]
            if 0 <= priority_idx < len(priority_names):
                priority_counts[priority_names[priority_idx]] += 1

        return {
            "tokens": {
                "total_budget": self._total_budget,
                "allocated": allocated,
                "consumed": consumed,
                "remaining": self._total_budget - allocated
            },
            "agents": {
                "total_quotas": sum(self._agent_quotas.values()),
                "active_agents": sum(len(slots) for slots in self._active_slots.values()),
                "available_slots": sum(
                    quota - len(self._active_slots.get(agent_type, []))
                    for agent_type, quota in self._agent_quotas.items()
                )
            },
            "queue": {
                "pending_tasks": len(self._task_queue),
                "by_priority": priority_counts
            }
        }

    def get_bottlenecks(self) -> List[Dict[str, Any]]:
        """Identify current resource bottlenecks."""
        bottlenecks = []
        usage = self.get_resource_usage()

        # Token exhaustion
        token_util = usage["tokens"]["consumed"] / usage["tokens"]["total_budget"] if usage["tokens"]["total_budget"] > 0 else 0
        if token_util > 0.9:
            bottlenecks.append({
                "type": "token_exhaustion",
                "severity": "critical" if token_util > 0.95 else "warning",
                "details": {"utilization": token_util},
                "recommendation": "Increase total token budget or reset consumed budgets"
            })

        # Quota exceeded
        if usage["agents"]["available_slots"] == 0 and usage["queue"]["pending_tasks"] > 0:
            bottlenecks.append({
                "type": "quota_exceeded",
                "severity": "warning",
                "details": {"pending_tasks": usage["queue"]["pending_tasks"]},
                "recommendation": "Increase agent quotas or wait for slots to free up"
            })

        # Queue backlog
        if usage["queue"]["pending_tasks"] > 10:
            bottlenecks.append({
                "type": "queue_backlog",
                "severity": "warning" if usage["queue"]["pending_tasks"] < 50 else "critical",
                "details": {"pending_tasks": usage["queue"]["pending_tasks"]},
                "recommendation": "Scale up agent capacity or prioritize critical tasks"
            })

        return bottlenecks

    @property
    def total_token_budget(self) -> int:
        """Get total token budget across all swarms."""
        return self._total_budget

    @property
    def active_slots(self) -> Dict[str, int]:
        """Get active agent slots by type."""
        return {
            agent_type: len(slots)
            for agent_type, slots in self._active_slots.items()
        }


# ==========================================
# Test IMemoryProvider
# ==========================================


class TestIMemoryProvider:
    """Test suite for IMemoryProvider interface."""

    @pytest.fixture
    def provider(self):
        """Create a mock memory provider instance."""
        return MockMemoryProvider()

    def test_store_retrieve_basic(self, provider):
        """Test basic store and retrieve operations."""
        # Store a value
        result = provider.store("swarm-001", "context", "test_key", {"data": "value"})
        assert result is True

        # Retrieve the value
        value = provider.retrieve("swarm-001", "context", "test_key")
        assert value == {"data": "value"}

    def test_store_retrieve_with_default(self, provider):
        """Test retrieve with default value for missing keys."""
        value = provider.retrieve("swarm-001", "context", "missing_key", default="default_value")
        assert value == "default_value"

    def test_store_persistent_vs_volatile(self, provider):
        """Test persistent vs volatile storage."""
        # Store persistent
        provider.store("swarm-001", "context", "persistent_key", "persistent_value", persistent=True)

        # Store volatile
        provider.store("swarm-001", "context", "volatile_key", "volatile_value", persistent=False)

        # Check stats
        stats = provider.get_memory_stats("swarm-001")
        assert stats["persistent_count"] == 1
        assert stats["volatile_count"] == 1

    def test_delete_operation(self, provider):
        """Test delete operation."""
        # Store a value
        provider.store("swarm-001", "context", "delete_key", "value")

        # Delete it
        result = provider.delete("swarm-001", "context", "delete_key")
        assert result is True

        # Verify deletion
        value = provider.retrieve("swarm-001", "context", "delete_key")
        assert value is None

    def test_delete_nonexistent_key(self, provider):
        """Test deleting a key that doesn't exist."""
        result = provider.delete("swarm-001", "context", "nonexistent")
        assert result is False

    def test_list_keys(self, provider):
        """Test listing keys in a namespace."""
        # Store multiple keys
        provider.store("swarm-001", "context", "key1", "value1")
        provider.store("swarm-001", "context", "key2", "value2")
        provider.store("swarm-001", "context", "key3", "value3")

        # List keys
        keys = provider.list_keys("swarm-001", "context")
        assert sorted(keys) == ["key1", "key2", "key3"]

    def test_list_keys_with_pattern(self, provider):
        """Test listing keys with glob pattern."""
        # Store multiple keys
        provider.store("swarm-001", "context", "task_001", "value1")
        provider.store("swarm-001", "context", "task_002", "value2")
        provider.store("swarm-001", "context", "result_001", "value3")

        # List with pattern
        keys = provider.list_keys("swarm-001", "context", pattern="task_*")
        assert sorted(keys) == ["task_001", "task_002"]

    def test_clear_namespace(self, provider):
        """Test clearing all keys in a namespace."""
        # Store multiple keys
        provider.store("swarm-001", "context", "key1", "value1")
        provider.store("swarm-001", "context", "key2", "value2")

        # Clear namespace
        result = provider.clear_namespace("swarm-001", "context")
        assert result is True

        # Verify cleared
        keys = provider.list_keys("swarm-001", "context")
        assert len(keys) == 0

    def test_namespace_isolation(self, provider):
        """Test that namespaces are isolated from each other."""
        # Store in different namespaces
        provider.store("swarm-001", "namespace1", "key", "value1")
        provider.store("swarm-001", "namespace2", "key", "value2")

        # Retrieve from each
        value1 = provider.retrieve("swarm-001", "namespace1", "key")
        value2 = provider.retrieve("swarm-001", "namespace2", "key")

        assert value1 == "value1"
        assert value2 == "value2"

    def test_swarm_isolation(self, provider):
        """Test that swarms are isolated from each other."""
        # Store in different swarms
        provider.store("swarm-001", "context", "key", "value1")
        provider.store("swarm-002", "context", "key", "value2")

        # Retrieve from each
        value1 = provider.retrieve("swarm-001", "context", "key")
        value2 = provider.retrieve("swarm-002", "context", "key")

        assert value1 == "value1"
        assert value2 == "value2"

    def test_get_memory_stats(self, provider):
        """Test memory statistics retrieval."""
        # Store some data
        provider.store("swarm-001", "context", "key1", "value1", persistent=True)
        provider.store("swarm-001", "context", "key2", "value2", persistent=False)
        provider.store("swarm-001", "results", "key3", "value3", persistent=True)

        # Get stats
        stats = provider.get_memory_stats("swarm-001")

        assert stats["total_keys"] == 3
        assert set(stats["namespaces"]) == {"context", "results"}
        assert stats["persistent_count"] == 2
        assert stats["volatile_count"] == 1
        assert stats["size_bytes"] > 0

    def test_empty_stats(self, provider):
        """Test stats for non-existent swarm."""
        stats = provider.get_memory_stats("nonexistent-swarm")
        assert stats["total_keys"] == 0
        assert stats["namespaces"] == []


# ==========================================
# Test ICoordinator
# ==========================================


class TestICoordinator:
    """Test suite for ICoordinator interface."""

    @pytest.fixture
    def coordinator(self):
        """Create a mock coordinator instance."""
        return MockCoordinator()

    def test_register_agent(self, coordinator):
        """Test agent registration."""
        metadata = {
            "type": "expert-backend",
            "capabilities": ["python", "fastapi"]
        }

        result = coordinator.register_agent("agent-001", metadata)
        assert result is True

    def test_register_duplicate_agent(self, coordinator):
        """Test registering an agent twice."""
        metadata = {"type": "expert-backend"}

        coordinator.register_agent("agent-001", metadata)
        result = coordinator.register_agent("agent-001", metadata)

        assert result is False

    def test_unregister_agent(self, coordinator):
        """Test agent unregistration."""
        coordinator.register_agent("agent-001", {"type": "expert-backend"})

        result = coordinator.unregister_agent("agent-001")
        assert result is True

    def test_unregister_nonexistent_agent(self, coordinator):
        """Test unregistering an agent that doesn't exist."""
        result = coordinator.unregister_agent("nonexistent")
        assert result is False

    def test_send_message(self, coordinator):
        """Test sending a message between agents."""
        coordinator.register_agent("agent-001", {"type": "sender"})
        coordinator.register_agent("agent-002", {"type": "receiver"})

        message = {"type": "request", "content": "Hello"}
        result = coordinator.send_message("agent-001", "agent-002", message)

        assert result is True

    def test_send_message_to_nonexistent_agent(self, coordinator):
        """Test sending message to non-existent agent."""
        coordinator.register_agent("agent-001", {"type": "sender"})

        message = {"type": "request"}
        result = coordinator.send_message("agent-001", "nonexistent", message)

        assert result is False

    def test_broadcast_message(self, coordinator):
        """Test broadcasting a message to all agents."""
        coordinator.register_agent("agent-001", {"type": "sender"})
        coordinator.register_agent("agent-002", {"type": "receiver"})
        coordinator.register_agent("agent-003", {"type": "receiver"})

        message = {"type": "broadcast", "content": "Announcement"}
        count = coordinator.broadcast_message("agent-001", message)

        assert count == 2  # All agents except sender

    def test_broadcast_message_with_exclusion(self, coordinator):
        """Test broadcasting with exclusion list."""
        coordinator.register_agent("agent-001", {"type": "sender"})
        coordinator.register_agent("agent-002", {"type": "receiver"})
        coordinator.register_agent("agent-003", {"type": "receiver"})

        message = {"type": "broadcast"}
        count = coordinator.broadcast_message("agent-001", message, exclude=["agent-002"])

        assert count == 1  # Only agent-003 receives

    def test_get_agent_status(self, coordinator):
        """Test getting agent status."""
        metadata = {"type": "expert-backend"}
        coordinator.register_agent("agent-001", metadata)

        status = coordinator.get_agent_status("agent-001")

        assert status is not None
        assert status["state"] == "active"
        assert status["metadata"] == metadata
        assert "last_heartbeat" in status

    def test_get_nonexistent_agent_status(self, coordinator):
        """Test getting status of non-existent agent."""
        status = coordinator.get_agent_status("nonexistent")
        assert status is None

    def test_get_topology_info(self, coordinator):
        """Test getting topology information."""
        coordinator.register_agent("agent-001", {"type": "backend"})
        coordinator.register_agent("agent-002", {"type": "frontend"})

        info = coordinator.get_topology_info()

        assert info["type"] == "mesh"
        assert info["agent_count"] == 2
        assert info["health"] in ["healthy", "degraded", "critical"]

    def test_request_consensus(self, coordinator):
        """Test requesting consensus from agents."""
        coordinator.register_agent("agent-001", {"type": "voter"})
        coordinator.register_agent("agent-002", {"type": "voter"})
        coordinator.register_agent("agent-003", {"type": "voter"})

        proposal = {"action": "deploy", "target": "production"}
        result = coordinator.request_consensus(proposal)

        assert result["decision"] in ["approved", "rejected", "timeout"]
        assert "votes_for" in result
        assert "votes_against" in result
        assert result["threshold"] == 0.66

    def test_synchronize_state(self, coordinator):
        """Test state synchronization across agents."""
        coordinator.register_agent("agent-001", {"type": "worker"})
        coordinator.register_agent("agent-002", {"type": "worker"})

        result = coordinator.synchronize_state("current_phase", "implementation")
        assert result is True

    def test_synchronize_state_no_agents(self, coordinator):
        """Test state synchronization with no agents."""
        result = coordinator.synchronize_state("state_key", "value")
        assert result is False


# ==========================================
# Test IResourceController
# ==========================================


class TestIResourceController:
    """Test suite for IResourceController interface."""

    @pytest.fixture
    def controller(self):
        """Create a mock resource controller instance."""
        return MockResourceController(total_budget=200000)

    def test_allocate_tokens(self, controller):
        """Test token budget allocation."""
        result = controller.allocate_tokens("swarm-001", 50000)
        assert result is True

        balance = controller.get_token_balance("swarm-001")
        assert balance == 50000

    def test_allocate_tokens_exceeds_budget(self, controller):
        """Test allocation that exceeds total budget."""
        controller.allocate_tokens("swarm-001", 150000)
        result = controller.allocate_tokens("swarm-002", 100000)

        assert result is False  # Total would be 250000 > 200000

    def test_allocate_negative_tokens(self, controller):
        """Test that negative allocation raises error."""
        with pytest.raises(ValueError):
            controller.allocate_tokens("swarm-001", -1000)

    def test_consume_tokens(self, controller):
        """Test token consumption."""
        controller.allocate_tokens("swarm-001", 50000)

        result = controller.consume_tokens("swarm-001", 10000)
        assert result is True

        balance = controller.get_token_balance("swarm-001")
        assert balance == 40000

    def test_consume_tokens_exceeds_balance(self, controller):
        """Test consuming more tokens than available."""
        controller.allocate_tokens("swarm-001", 10000)

        result = controller.consume_tokens("swarm-001", 20000)
        assert result is False

    def test_consume_negative_tokens(self, controller):
        """Test that negative consumption raises error."""
        controller.allocate_tokens("swarm-001", 10000)

        with pytest.raises(ValueError):
            controller.consume_tokens("swarm-001", -500)

    def test_reset_budget(self, controller):
        """Test budget reset."""
        controller.allocate_tokens("swarm-001", 50000)
        controller.consume_tokens("swarm-001", 30000)

        result = controller.reset_budget("swarm-001")
        assert result is True

        balance = controller.get_token_balance("swarm-001")
        assert balance == 50000  # Back to allocated amount

    def test_reset_nonexistent_budget(self, controller):
        """Test resetting budget for non-existent swarm."""
        result = controller.reset_budget("nonexistent")
        assert result is False

    def test_set_agent_quota(self, controller):
        """Test setting agent quota."""
        result = controller.set_agent_quota("expert-backend", 3)
        assert result is True

        status = controller.get_quota_status("expert-backend")
        assert status["max_concurrent"] == 3

    def test_set_negative_quota(self, controller):
        """Test that negative quota raises error."""
        with pytest.raises(ValueError):
            controller.set_agent_quota("expert-backend", -1)

    def test_request_agent_slot(self, controller):
        """Test requesting agent slot."""
        controller.set_agent_quota("expert-backend", 2)

        slot_id = controller.request_agent_slot("expert-backend")
        assert slot_id is not None
        assert "expert-backend" in slot_id

    def test_request_slot_quota_exceeded(self, controller):
        """Test requesting slot when quota exceeded."""
        controller.set_agent_quota("expert-backend", 1)

        # Request first slot (should succeed)
        slot1 = controller.request_agent_slot("expert-backend")
        assert slot1 is not None

        # Request second slot (should fail)
        slot2 = controller.request_agent_slot("expert-backend")
        assert slot2 is None

    def test_release_agent_slot(self, controller):
        """Test releasing agent slot."""
        controller.set_agent_quota("expert-backend", 2)

        slot_id = controller.request_agent_slot("expert-backend")
        result = controller.release_agent_slot("expert-backend", slot_id)

        assert result is True

    def test_release_nonexistent_slot(self, controller):
        """Test releasing slot that doesn't exist."""
        controller.set_agent_quota("expert-backend", 2)

        result = controller.release_agent_slot("expert-backend", "nonexistent-slot")
        assert result is False

    def test_get_quota_status(self, controller):
        """Test getting quota status."""
        controller.set_agent_quota("expert-backend", 3)
        controller.request_agent_slot("expert-backend")

        status = controller.get_quota_status("expert-backend")

        assert status["max_concurrent"] == 3
        assert status["active_slots"] == 1
        assert status["available_slots"] == 2

    def test_enqueue_task(self, controller):
        """Test enqueueing a task."""
        task_data = {"spec_id": "SPEC-001", "agent_type": "expert-backend"}

        result = controller.enqueue_task("task-001", Priority.HIGH, task_data)
        assert result is True

    def test_enqueue_duplicate_task(self, controller):
        """Test enqueueing duplicate task."""
        task_data = {"spec_id": "SPEC-001"}

        controller.enqueue_task("task-001", Priority.HIGH, task_data)
        result = controller.enqueue_task("task-001", Priority.MEDIUM, task_data)

        assert result is False

    def test_dequeue_task(self, controller):
        """Test dequeueing a task."""
        controller.enqueue_task("task-001", Priority.HIGH, {"data": "test"})

        task = controller.dequeue_task()

        assert task is not None
        assert task["task_id"] == "task-001"
        assert task["priority"] == Priority.HIGH

    def test_dequeue_respects_priority(self, controller):
        """Test that dequeue returns highest priority task."""
        controller.enqueue_task("task-low", Priority.LOW, {"data": "low"})
        controller.enqueue_task("task-critical", Priority.CRITICAL, {"data": "critical"})
        controller.enqueue_task("task-medium", Priority.MEDIUM, {"data": "medium"})

        task = controller.dequeue_task()
        assert task["task_id"] == "task-critical"

    def test_peek_next_task(self, controller):
        """Test peeking at next task without removing."""
        controller.enqueue_task("task-001", Priority.HIGH, {"data": "test"})

        task1 = controller.peek_next_task()
        task2 = controller.peek_next_task()

        assert task1 == task2
        assert task1["task_id"] == "task-001"

    def test_update_priority(self, controller):
        """Test updating task priority."""
        controller.enqueue_task("task-001", Priority.LOW, {"data": "test"})

        result = controller.update_priority("task-001", Priority.CRITICAL)
        assert result is True

        task = controller.peek_next_task()
        assert task["priority"] == Priority.CRITICAL

    def test_cancel_task(self, controller):
        """Test cancelling a task."""
        controller.enqueue_task("task-001", Priority.HIGH, {"data": "test"})

        result = controller.cancel_task("task-001")
        assert result is True

        task = controller.dequeue_task()
        assert task is None

    def test_get_resource_usage(self, controller):
        """Test getting resource usage statistics."""
        controller.allocate_tokens("swarm-001", 100000)
        controller.consume_tokens("swarm-001", 30000)
        controller.set_agent_quota("expert-backend", 3)
        controller.request_agent_slot("expert-backend")
        controller.enqueue_task("task-001", Priority.HIGH, {})
        controller.enqueue_task("task-002", Priority.CRITICAL, {})

        usage = controller.get_resource_usage()

        assert usage["tokens"]["total_budget"] == 200000
        assert usage["tokens"]["allocated"] == 100000
        assert usage["tokens"]["consumed"] == 30000
        assert usage["agents"]["active_agents"] == 1
        assert usage["queue"]["pending_tasks"] == 2
        assert usage["queue"]["by_priority"]["HIGH"] == 1
        assert usage["queue"]["by_priority"]["CRITICAL"] == 1

    def test_get_bottlenecks_token_exhaustion(self, controller):
        """Test bottleneck detection for token exhaustion."""
        # Allocate and consume most of budget
        controller.allocate_tokens("swarm-001", 200000)
        controller.consume_tokens("swarm-001", 191000)  # 95.5% utilization

        bottlenecks = controller.get_bottlenecks()

        assert len(bottlenecks) > 0
        assert any(b["type"] == "token_exhaustion" for b in bottlenecks)
        token_bottleneck = next(b for b in bottlenecks if b["type"] == "token_exhaustion")
        assert token_bottleneck["severity"] == "critical"

    def test_get_bottlenecks_quota_exceeded(self, controller):
        """Test bottleneck detection for quota exceeded."""
        # Set quota and fill all slots
        controller.set_agent_quota("expert-backend", 1)
        controller.request_agent_slot("expert-backend")

        # Enqueue tasks that need slots
        controller.enqueue_task("task-001", Priority.HIGH, {})

        bottlenecks = controller.get_bottlenecks()

        assert any(b["type"] == "quota_exceeded" for b in bottlenecks)

    def test_get_bottlenecks_queue_backlog(self, controller):
        """Test bottleneck detection for queue backlog."""
        # Enqueue many tasks
        for i in range(15):
            controller.enqueue_task(f"task-{i}", Priority.MEDIUM, {})

        bottlenecks = controller.get_bottlenecks()

        assert any(b["type"] == "queue_backlog" for b in bottlenecks)

    def test_total_token_budget_property(self, controller):
        """Test total_token_budget property."""
        assert controller.total_token_budget == 200000

    def test_active_slots_property(self, controller):
        """Test active_slots property."""
        controller.set_agent_quota("expert-backend", 2)
        controller.set_agent_quota("expert-frontend", 3)

        controller.request_agent_slot("expert-backend")
        controller.request_agent_slot("expert-frontend")
        controller.request_agent_slot("expert-frontend")

        active = controller.active_slots

        assert active["expert-backend"] == 1
        assert active["expert-frontend"] == 2


# ==========================================
# Edge Cases and Integration Tests
# ==========================================


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_memory_provider_empty_values(self):
        """Test storing empty or None values."""
        provider = MockMemoryProvider()

        # Store empty string
        provider.store("swarm-001", "test", "empty", "")
        assert provider.retrieve("swarm-001", "test", "empty") == ""

        # Store None
        provider.store("swarm-001", "test", "none", None)
        assert provider.retrieve("swarm-001", "test", "none") is None

        # Store empty dict
        provider.store("swarm-001", "test", "empty_dict", {})
        assert provider.retrieve("swarm-001", "test", "empty_dict") == {}

    def test_coordinator_single_agent_broadcast(self):
        """Test broadcasting with only one agent (sender)."""
        coordinator = MockCoordinator()
        coordinator.register_agent("agent-001", {"type": "solo"})

        count = coordinator.broadcast_message("agent-001", {"msg": "test"})
        assert count == 0  # No other agents to broadcast to

    def test_resource_controller_zero_budget(self):
        """Test resource controller with zero budget."""
        controller = MockResourceController(total_budget=0)

        result = controller.allocate_tokens("swarm-001", 1000)
        assert result is False

    def test_resource_controller_empty_queue_operations(self):
        """Test queue operations on empty queue."""
        controller = MockResourceController()

        task = controller.dequeue_task()
        assert task is None

        task = controller.peek_next_task()
        assert task is None

        result = controller.update_priority("nonexistent", Priority.HIGH)
        assert result is False

        result = controller.cancel_task("nonexistent")
        assert result is False


class TestIntegrationScenarios:
    """Integration tests combining multiple interfaces."""

    def test_multi_agent_workflow_with_memory(self):
        """Test complete workflow using coordinator and memory."""
        coordinator = MockCoordinator()
        memory = MockMemoryProvider()

        # Register agents
        coordinator.register_agent("agent-001", {"type": "backend"})
        coordinator.register_agent("agent-002", {"type": "frontend"})

        # Store shared context
        memory.store("swarm-001", "workflow", "phase", "implementation")

        # Agent-001 stores its result
        memory.store("swarm-001", "results", "backend", {"status": "complete"})

        # Agent-002 retrieves backend result
        backend_result = memory.retrieve("swarm-001", "results", "backend")

        assert backend_result["status"] == "complete"

    def test_resource_constrained_coordination(self):
        """Test coordination under resource constraints."""
        controller = MockResourceController(total_budget=100000)
        coordinator = MockCoordinator()

        # Allocate budgets to two swarms
        controller.allocate_tokens("swarm-001", 60000)
        controller.allocate_tokens("swarm-002", 40000)

        # Register agents in coordinator
        coordinator.register_agent("agent-001", {"swarm": "swarm-001"})
        coordinator.register_agent("agent-002", {"swarm": "swarm-002"})

        # Consume tokens
        controller.consume_tokens("swarm-001", 50000)

        # Check remaining budget
        balance = controller.get_token_balance("swarm-001")
        assert balance == 10000

        # Verify coordinator has both agents
        info = coordinator.get_topology_info()
        assert info["agent_count"] == 2
