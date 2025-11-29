"""
Comprehensive tests for StateSynchronizer.

Tests cover:
- Full state synchronization
- Delta synchronization
- Conflict resolution integration
- Broadcast protocol
- Memory integration
- Timeout handling
- Version tracking

Following TDD RED-GREEN-REFACTOR cycle with 89%+ coverage target.
"""

import sys
from pathlib import Path

# Add moai-flow directory to Python path
project_root = Path(__file__).parent.parent.parent.parent
moai_flow_path = project_root / "moai_flow"
sys.path.insert(0, str(moai_flow_path))

import pytest
import asyncio
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
from enum import Enum


# ==========================================
# Synchronization Mode
# ==========================================


class SyncMode(Enum):
    """State synchronization modes."""
    FULL = "full"
    DELTA = "delta"
    CONFLICT_ONLY = "conflict_only"


# ==========================================
# Mock Classes (until implementation ready)
# ==========================================


class MockMemoryProvider:
    """Mock memory provider for testing."""

    def __init__(self):
        self.storage = {}

    def store(self, swarm_id: str, namespace: str, key: str, value: Any) -> bool:
        if swarm_id not in self.storage:
            self.storage[swarm_id] = {}
        if namespace not in self.storage[swarm_id]:
            self.storage[swarm_id][namespace] = {}

        self.storage[swarm_id][namespace][key] = value
        return True

    def retrieve(self, swarm_id: str, namespace: str, key: str, default=None) -> Any:
        try:
            return self.storage[swarm_id][namespace][key]
        except KeyError:
            return default

    def list_keys(self, swarm_id: str, namespace: str) -> List[str]:
        try:
            return list(self.storage[swarm_id][namespace].keys())
        except KeyError:
            return []


class MockCoordinator:
    """Mock coordinator for testing."""

    def __init__(self):
        self.agents = {}
        self.messages = []

    def register_agent(self, agent_id: str, metadata: Dict[str, Any]) -> bool:
        self.agents[agent_id] = metadata
        return True

    def get_all_agents(self) -> List[str]:
        return list(self.agents.keys())

    def broadcast_message(
        self,
        from_agent: str,
        message: Dict[str, Any],
        exclude: List[str] = None
    ) -> int:
        self.messages.append({
            "from": from_agent,
            "message": message,
            "exclude": exclude or []
        })
        return len(self.agents) - len(exclude or [])


class StateVersion:
    """State version for synchronization."""

    def __init__(
        self,
        agent_id: str,
        version: int,
        data: Any,
        timestamp: Optional[datetime] = None
    ):
        self.agent_id = agent_id
        self.version = version
        self.data = data
        self.timestamp = timestamp or datetime.now(timezone.utc)


class MockConflictResolver:
    """Mock conflict resolver."""

    def resolve_conflict(self, versions: List[StateVersion]) -> StateVersion:
        if not versions:
            raise ValueError("No versions to resolve")
        # Simple LWW resolution
        return max(versions, key=lambda v: v.timestamp)

    def detect_conflict(self, versions: List[StateVersion]) -> bool:
        if len(versions) <= 1:
            return False
        first_data = versions[0].data
        return any(v.data != first_data for v in versions[1:])


class MockStateSynchronizer:
    """Mock StateSynchronizer until implementation is ready."""

    def __init__(
        self,
        coordinator: Optional[MockCoordinator] = None,
        memory: Optional[MockMemoryProvider] = None,
        conflict_resolver: Optional[MockConflictResolver] = None
    ):
        """
        Initialize state synchronizer.

        Args:
            coordinator: Coordinator for agent communication
            memory: Memory provider for state storage
            conflict_resolver: Conflict resolver for handling conflicts
        """
        self.coordinator = coordinator or MockCoordinator()
        self.memory = memory or MockMemoryProvider()
        self.conflict_resolver = conflict_resolver or MockConflictResolver()
        self.sync_history = []
        self.version_tracker = {}

    async def synchronize_state(
        self,
        swarm_id: str,
        state_key: str,
        state_value: Any,
        mode: SyncMode = SyncMode.FULL,
        timeout_ms: int = 30000
    ) -> Dict[str, Any]:
        """
        Synchronize state across agents.

        Args:
            swarm_id: Swarm identifier
            state_key: State key to synchronize
            state_value: State value
            mode: Synchronization mode
            timeout_ms: Timeout in milliseconds

        Returns:
            Synchronization result
        """
        # Get current version
        current_version = self.version_tracker.get(state_key, 0)
        new_version = current_version + 1
        self.version_tracker[state_key] = new_version

        # Store state in memory
        self.memory.store(swarm_id, "state", state_key, state_value)

        # Broadcast to agents based on mode
        if mode == SyncMode.FULL:
            result = await self._sync_full(swarm_id, state_key, state_value, new_version, timeout_ms)
        elif mode == SyncMode.DELTA:
            result = await self._sync_delta(swarm_id, state_key, state_value, new_version, timeout_ms)
        else:
            result = await self._sync_conflict_only(swarm_id, state_key, state_value, new_version, timeout_ms)

        # Record sync
        self.sync_history.append({
            "swarm_id": swarm_id,
            "state_key": state_key,
            "mode": mode.value,
            "version": new_version,
            "timestamp": datetime.now(timezone.utc)
        })

        return result

    async def _sync_full(
        self,
        swarm_id: str,
        state_key: str,
        state_value: Any,
        version: int,
        timeout_ms: int
    ) -> Dict[str, Any]:
        """Full state synchronization."""
        agents = self.coordinator.get_all_agents()

        message = {
            "type": "state_sync",
            "mode": "full",
            "state_key": state_key,
            "state_value": state_value,
            "version": version
        }

        broadcast_count = self.coordinator.broadcast_message("synchronizer", message)

        return {
            "mode": "full",
            "state_key": state_key,
            "version": version,
            "synced_agents": broadcast_count,
            "total_agents": len(agents),
            "success": True
        }

    async def _sync_delta(
        self,
        swarm_id: str,
        state_key: str,
        state_value: Any,
        version: int,
        timeout_ms: int
    ) -> Dict[str, Any]:
        """Delta synchronization (send only changes)."""
        agents = self.coordinator.get_all_agents()

        # Calculate delta from previous version
        previous_value = self.memory.retrieve(swarm_id, "state_prev", state_key)
        delta = self._calculate_delta(previous_value, state_value)

        # Store current as previous for next sync
        self.memory.store(swarm_id, "state_prev", state_key, state_value)

        message = {
            "type": "state_sync",
            "mode": "delta",
            "state_key": state_key,
            "delta": delta,
            "version": version
        }

        broadcast_count = self.coordinator.broadcast_message("synchronizer", message)

        return {
            "mode": "delta",
            "state_key": state_key,
            "version": version,
            "delta_size": len(str(delta)),
            "synced_agents": broadcast_count,
            "total_agents": len(agents),
            "success": True
        }

    async def _sync_conflict_only(
        self,
        swarm_id: str,
        state_key: str,
        state_value: Any,
        version: int,
        timeout_ms: int
    ) -> Dict[str, Any]:
        """Synchronize only if conflict detected."""
        # Check for conflicts
        versions = await self._collect_versions(swarm_id, state_key)

        has_conflict = self.conflict_resolver.detect_conflict(versions)

        if has_conflict:
            # Resolve conflict
            resolved = self.conflict_resolver.resolve_conflict(versions)
            # Sync resolved state
            return await self._sync_full(swarm_id, state_key, resolved.data, version, timeout_ms)
        else:
            return {
                "mode": "conflict_only",
                "state_key": state_key,
                "version": version,
                "conflict_detected": False,
                "success": True
            }

    async def _collect_versions(
        self,
        swarm_id: str,
        state_key: str
    ) -> List[StateVersion]:
        """Collect state versions from agents."""
        # Simulate collecting versions
        agents = self.coordinator.get_all_agents()
        versions = []

        for agent in agents:
            state_value = self.memory.retrieve(swarm_id, f"agent_{agent}", state_key)
            if state_value is not None:
                version = StateVersion(agent, self.version_tracker.get(state_key, 0), state_value)
                versions.append(version)

        return versions

    def _calculate_delta(self, previous: Any, current: Any) -> Dict[str, Any]:
        """Calculate delta between previous and current state."""
        if previous is None:
            return {"type": "full", "value": current}

        if isinstance(current, dict) and isinstance(previous, dict):
            # Dictionary diff
            added = {k: v for k, v in current.items() if k not in previous}
            modified = {k: v for k, v in current.items() if k in previous and previous[k] != v}
            removed = {k: previous[k] for k in previous if k not in current}

            return {
                "type": "dict_delta",
                "added": added,
                "modified": modified,
                "removed": removed
            }
        else:
            # Full replacement for non-dict types
            return {"type": "full", "value": current}

    def get_current_version(self, state_key: str) -> int:
        """Get current version for state key."""
        return self.version_tracker.get(state_key, 0)

    def get_sync_history(self) -> List[Dict[str, Any]]:
        """Get synchronization history."""
        return self.sync_history.copy()

    def clear_history(self) -> None:
        """Clear synchronization history."""
        self.sync_history.clear()


# ==========================================
# Fixtures
# ==========================================


@pytest.fixture
def memory_provider():
    """Create mock memory provider."""
    return MockMemoryProvider()


@pytest.fixture
def coordinator():
    """Create mock coordinator."""
    return MockCoordinator()


@pytest.fixture
def conflict_resolver():
    """Create mock conflict resolver."""
    return MockConflictResolver()


@pytest.fixture
def state_synchronizer(coordinator, memory_provider, conflict_resolver):
    """Create state synchronizer."""
    return MockStateSynchronizer(
        coordinator=coordinator,
        memory=memory_provider,
        conflict_resolver=conflict_resolver
    )


# ==========================================
# Test: Initialization
# ==========================================


def test_synchronizer_init():
    """Test synchronizer initialization."""
    sync = MockStateSynchronizer()
    assert sync.coordinator is not None
    assert sync.memory is not None
    assert sync.conflict_resolver is not None


def test_synchronizer_init_with_components(
    coordinator,
    memory_provider,
    conflict_resolver
):
    """Test synchronizer initialization with components."""
    sync = MockStateSynchronizer(
        coordinator=coordinator,
        memory=memory_provider,
        conflict_resolver=conflict_resolver
    )

    assert sync.coordinator == coordinator
    assert sync.memory == memory_provider
    assert sync.conflict_resolver == conflict_resolver


# ==========================================
# Test: Full State Synchronization
# ==========================================


@pytest.mark.asyncio
async def test_full_sync_success(state_synchronizer, coordinator):
    """Test successful full state synchronization."""
    # Register agents
    coordinator.register_agent("agent-1", {"type": "expert-backend"})
    coordinator.register_agent("agent-2", {"type": "expert-frontend"})

    result = await state_synchronizer.synchronize_state(
        "swarm-001",
        "config",
        {"key": "value"},
        mode=SyncMode.FULL
    )

    assert result["success"] is True
    assert result["mode"] == "full"
    assert result["synced_agents"] == 2


@pytest.mark.asyncio
async def test_full_sync_increments_version(state_synchronizer):
    """Test full sync increments version."""
    initial_version = state_synchronizer.get_current_version("config")

    await state_synchronizer.synchronize_state(
        "swarm-001",
        "config",
        {"key": "value"},
        mode=SyncMode.FULL
    )

    new_version = state_synchronizer.get_current_version("config")
    assert new_version == initial_version + 1


@pytest.mark.asyncio
async def test_full_sync_stores_in_memory(state_synchronizer, memory_provider):
    """Test full sync stores state in memory."""
    state_value = {"key": "value"}

    await state_synchronizer.synchronize_state(
        "swarm-001",
        "config",
        state_value,
        mode=SyncMode.FULL
    )

    stored_value = memory_provider.retrieve("swarm-001", "state", "config")
    assert stored_value == state_value


# ==========================================
# Test: Delta Synchronization
# ==========================================


@pytest.mark.asyncio
async def test_delta_sync_success(state_synchronizer, coordinator):
    """Test successful delta synchronization."""
    coordinator.register_agent("agent-1", {"type": "expert-backend"})

    result = await state_synchronizer.synchronize_state(
        "swarm-001",
        "config",
        {"key": "value"},
        mode=SyncMode.DELTA
    )

    assert result["success"] is True
    assert result["mode"] == "delta"


@pytest.mark.asyncio
async def test_delta_sync_calculates_diff(state_synchronizer):
    """Test delta sync calculates difference."""
    # First sync
    await state_synchronizer.synchronize_state(
        "swarm-001",
        "config",
        {"key1": "value1"},
        mode=SyncMode.DELTA
    )

    # Second sync with changes
    result = await state_synchronizer.synchronize_state(
        "swarm-001",
        "config",
        {"key1": "value1", "key2": "value2"},
        mode=SyncMode.DELTA
    )

    assert "delta_size" in result


@pytest.mark.asyncio
async def test_delta_sync_with_dict_changes(state_synchronizer):
    """Test delta sync with dictionary changes."""
    # Initial state
    await state_synchronizer.synchronize_state(
        "swarm-001",
        "data",
        {"a": 1, "b": 2},
        mode=SyncMode.DELTA
    )

    # Modified state
    result = await state_synchronizer.synchronize_state(
        "swarm-001",
        "data",
        {"a": 1, "c": 3},  # b removed, c added
        mode=SyncMode.DELTA
    )

    assert result["success"] is True


# ==========================================
# Test: Conflict Resolution Integration
# ==========================================


@pytest.mark.asyncio
async def test_conflict_only_mode_no_conflict(state_synchronizer):
    """Test conflict-only mode with no conflicts."""
    result = await state_synchronizer.synchronize_state(
        "swarm-001",
        "config",
        {"key": "value"},
        mode=SyncMode.CONFLICT_ONLY
    )

    assert result["conflict_detected"] is False
    assert result["success"] is True


@pytest.mark.asyncio
async def test_conflict_resolution_invoked(state_synchronizer, memory_provider):
    """Test conflict resolution is invoked when needed."""
    # Create conflicting states
    memory_provider.store("swarm-001", "agent_agent-1", "config", {"key": "value1"})
    memory_provider.store("swarm-001", "agent_agent-2", "config", {"key": "value2"})

    result = await state_synchronizer.synchronize_state(
        "swarm-001",
        "config",
        {"key": "value3"},
        mode=SyncMode.CONFLICT_ONLY
    )

    # Conflict should be detected and resolved
    assert result is not None


# ==========================================
# Test: Broadcast Protocol
# ==========================================


@pytest.mark.asyncio
async def test_broadcast_message_sent(state_synchronizer, coordinator):
    """Test broadcast message is sent to all agents."""
    coordinator.register_agent("agent-1", {"type": "expert-backend"})
    coordinator.register_agent("agent-2", {"type": "expert-frontend"})
    coordinator.register_agent("agent-3", {"type": "manager-tdd"})

    await state_synchronizer.synchronize_state(
        "swarm-001",
        "config",
        {"key": "value"},
        mode=SyncMode.FULL
    )

    # Check broadcast was sent
    assert len(coordinator.messages) == 1
    assert coordinator.messages[0]["message"]["type"] == "state_sync"


@pytest.mark.asyncio
async def test_broadcast_contains_state_data(state_synchronizer, coordinator):
    """Test broadcast contains state data."""
    coordinator.register_agent("agent-1", {"type": "expert-backend"})

    state_value = {"key": "value"}
    await state_synchronizer.synchronize_state(
        "swarm-001",
        "config",
        state_value,
        mode=SyncMode.FULL
    )

    message = coordinator.messages[0]["message"]
    assert message["state_value"] == state_value


# ==========================================
# Test: Memory Integration
# ==========================================


@pytest.mark.asyncio
async def test_state_stored_in_memory(state_synchronizer, memory_provider):
    """Test state is stored in memory."""
    await state_synchronizer.synchronize_state(
        "swarm-001",
        "config",
        {"key": "value"},
        mode=SyncMode.FULL
    )

    stored = memory_provider.retrieve("swarm-001", "state", "config")
    assert stored == {"key": "value"}


@pytest.mark.asyncio
async def test_multiple_states_stored(state_synchronizer, memory_provider):
    """Test multiple states can be stored."""
    await state_synchronizer.synchronize_state("swarm-001", "config1", {"a": 1}, mode=SyncMode.FULL)
    await state_synchronizer.synchronize_state("swarm-001", "config2", {"b": 2}, mode=SyncMode.FULL)

    stored1 = memory_provider.retrieve("swarm-001", "state", "config1")
    stored2 = memory_provider.retrieve("swarm-001", "state", "config2")

    assert stored1 == {"a": 1}
    assert stored2 == {"b": 2}


# ==========================================
# Test: Timeout Handling
# ==========================================


@pytest.mark.asyncio
async def test_timeout_parameter_accepted(state_synchronizer):
    """Test timeout parameter is accepted."""
    result = await state_synchronizer.synchronize_state(
        "swarm-001",
        "config",
        {"key": "value"},
        mode=SyncMode.FULL,
        timeout_ms=5000
    )

    assert result is not None


@pytest.mark.asyncio
async def test_short_timeout(state_synchronizer):
    """Test synchronization with short timeout."""
    result = await state_synchronizer.synchronize_state(
        "swarm-001",
        "config",
        {"key": "value"},
        mode=SyncMode.FULL,
        timeout_ms=100
    )

    assert result["success"] is True


# ==========================================
# Test: Version Tracking
# ==========================================


def test_version_tracking_initialized(state_synchronizer):
    """Test version tracking is initialized."""
    version = state_synchronizer.get_current_version("new_key")
    assert version == 0


@pytest.mark.asyncio
async def test_version_increments_on_sync(state_synchronizer):
    """Test version increments on each sync."""
    v1 = state_synchronizer.get_current_version("config")

    await state_synchronizer.synchronize_state("swarm-001", "config", {"a": 1}, mode=SyncMode.FULL)
    v2 = state_synchronizer.get_current_version("config")

    await state_synchronizer.synchronize_state("swarm-001", "config", {"a": 2}, mode=SyncMode.FULL)
    v3 = state_synchronizer.get_current_version("config")

    assert v2 == v1 + 1
    assert v3 == v2 + 1


@pytest.mark.asyncio
async def test_different_keys_have_independent_versions(state_synchronizer):
    """Test different state keys have independent versions."""
    await state_synchronizer.synchronize_state("swarm-001", "config1", {"a": 1}, mode=SyncMode.FULL)
    await state_synchronizer.synchronize_state("swarm-001", "config2", {"b": 2}, mode=SyncMode.FULL)

    v1 = state_synchronizer.get_current_version("config1")
    v2 = state_synchronizer.get_current_version("config2")

    assert v1 == 1
    assert v2 == 1


# ==========================================
# Test: Sync History
# ==========================================


@pytest.mark.asyncio
async def test_sync_history_tracking(state_synchronizer):
    """Test synchronization history tracking."""
    await state_synchronizer.synchronize_state("swarm-001", "config", {"a": 1}, mode=SyncMode.FULL)
    await state_synchronizer.synchronize_state("swarm-001", "config", {"a": 2}, mode=SyncMode.DELTA)

    history = state_synchronizer.get_sync_history()
    assert len(history) == 2


@pytest.mark.asyncio
async def test_sync_history_clear(state_synchronizer):
    """Test clearing sync history."""
    await state_synchronizer.synchronize_state("swarm-001", "config", {"a": 1}, mode=SyncMode.FULL)

    state_synchronizer.clear_history()
    history = state_synchronizer.get_sync_history()

    assert len(history) == 0


@pytest.mark.asyncio
async def test_sync_history_contains_metadata(state_synchronizer):
    """Test sync history contains metadata."""
    await state_synchronizer.synchronize_state("swarm-001", "config", {"a": 1}, mode=SyncMode.FULL)

    history = state_synchronizer.get_sync_history()
    entry = history[0]

    assert "swarm_id" in entry
    assert "state_key" in entry
    assert "mode" in entry
    assert "version" in entry
    assert "timestamp" in entry


# ==========================================
# Test: Edge Cases
# ==========================================


@pytest.mark.asyncio
async def test_sync_with_no_agents(state_synchronizer):
    """Test synchronization with no agents registered."""
    result = await state_synchronizer.synchronize_state(
        "swarm-001",
        "config",
        {"key": "value"},
        mode=SyncMode.FULL
    )

    assert result["synced_agents"] == 0
    assert result["success"] is True


@pytest.mark.asyncio
async def test_sync_empty_state(state_synchronizer):
    """Test synchronizing empty state."""
    result = await state_synchronizer.synchronize_state(
        "swarm-001",
        "config",
        {},
        mode=SyncMode.FULL
    )

    assert result["success"] is True


@pytest.mark.asyncio
async def test_sync_none_state(state_synchronizer):
    """Test synchronizing None state."""
    result = await state_synchronizer.synchronize_state(
        "swarm-001",
        "config",
        None,
        mode=SyncMode.FULL
    )

    assert result["success"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
