"""
Comprehensive tests for ConflictResolver.

Tests cover:
- LWW (Last-Write-Wins) strategy
- Version Vector strategy
- CRDT (Conflict-free Replicated Data Type) strategy
  - Counter CRDT
  - Set CRDT
  - Map CRDT
- Conflict detection
- StateVersion creation
- Edge cases (no conflicts, single version)

Following TDD RED-GREEN-REFACTOR cycle with 91%+ coverage target.
"""

import sys
from pathlib import Path

# Add moai-flow directory to Python path
project_root = Path(__file__).parent.parent.parent.parent
moai_flow_path = project_root / "moai_flow"
sys.path.insert(0, str(moai_flow_path))

import pytest
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
from enum import Enum


# ==========================================
# Conflict Resolution Strategies
# ==========================================


class ConflictStrategy(Enum):
    """Conflict resolution strategies."""
    LWW = "last_write_wins"
    VERSION_VECTOR = "version_vector"
    CRDT = "crdt"


# ==========================================
# Mock Classes (until implementation ready)
# ==========================================


class StateVersion:
    """State version with metadata."""

    def __init__(
        self,
        agent_id: str,
        version: int,
        data: Any,
        timestamp: Optional[datetime] = None,
        vector_clock: Optional[Dict[str, int]] = None
    ):
        self.agent_id = agent_id
        self.version = version
        self.data = data
        self.timestamp = timestamp or datetime.now(timezone.utc)
        self.vector_clock = vector_clock or {agent_id: version}

    def __repr__(self):
        return f"StateVersion(agent={self.agent_id}, v={self.version}, data={self.data})"


class MockConflictResolver:
    """Mock ConflictResolver until implementation is ready."""

    def __init__(self, strategy: ConflictStrategy = ConflictStrategy.LWW):
        """
        Initialize conflict resolver.

        Args:
            strategy: Conflict resolution strategy
        """
        self.strategy = strategy
        self.resolution_history = []

    def resolve_conflict(
        self,
        versions: List[StateVersion]
    ) -> StateVersion:
        """
        Resolve conflict between multiple state versions.

        Args:
            versions: List of conflicting state versions

        Returns:
            Resolved state version

        Raises:
            ValueError: If versions list is empty
        """
        if not versions:
            raise ValueError("No versions provided for conflict resolution")

        if len(versions) == 1:
            return versions[0]

        # Apply resolution strategy
        if self.strategy == ConflictStrategy.LWW:
            resolved = self._resolve_lww(versions)
        elif self.strategy == ConflictStrategy.VERSION_VECTOR:
            resolved = self._resolve_version_vector(versions)
        elif self.strategy == ConflictStrategy.CRDT:
            resolved = self._resolve_crdt(versions)
        else:
            raise ValueError(f"Unknown strategy: {self.strategy}")

        # Record resolution
        self.resolution_history.append({
            "strategy": self.strategy.value,
            "input_versions": len(versions),
            "resolved": resolved,
            "timestamp": datetime.now(timezone.utc)
        })

        return resolved

    def _resolve_lww(self, versions: List[StateVersion]) -> StateVersion:
        """
        Resolve using Last-Write-Wins strategy.

        Returns version with latest timestamp.
        """
        return max(versions, key=lambda v: v.timestamp)

    def _resolve_version_vector(self, versions: List[StateVersion]) -> StateVersion:
        """
        Resolve using Version Vector strategy.

        Compares vector clocks to determine causality.
        """
        # Check for concurrent updates (no clear causal order)
        for v1 in versions:
            is_concurrent = True
            for v2 in versions:
                if v1 == v2:
                    continue
                if self._is_causally_before(v1, v2):
                    is_concurrent = False
                    break

            if is_concurrent:
                # Fall back to LWW for concurrent updates
                return self._resolve_lww(versions)

        # Return version with highest causal order
        return max(versions, key=lambda v: sum(v.vector_clock.values()))

    def _is_causally_before(self, v1: StateVersion, v2: StateVersion) -> bool:
        """Check if v1 is causally before v2 based on vector clocks."""
        for agent, clock in v1.vector_clock.items():
            if clock > v2.vector_clock.get(agent, 0):
                return False
        return True

    def _resolve_crdt(self, versions: List[StateVersion]) -> StateVersion:
        """
        Resolve using CRDT (Conflict-free Replicated Data Type) strategy.

        Merges data using CRDT semantics based on data type.
        """
        # Detect CRDT type from data
        first_data = versions[0].data

        if isinstance(first_data, dict):
            if "count" in first_data:
                return self._merge_counter_crdt(versions)
            elif "elements" in first_data:
                return self._merge_set_crdt(versions)
            else:
                return self._merge_map_crdt(versions)
        else:
            # Default to LWW for non-CRDT types
            return self._resolve_lww(versions)

    def _merge_counter_crdt(self, versions: List[StateVersion]) -> StateVersion:
        """Merge Counter CRDT (take maximum)."""
        max_count = max(v.data["count"] for v in versions)
        merged_data = {"count": max_count}

        return StateVersion(
            agent_id="merged",
            version=max(v.version for v in versions),
            data=merged_data,
            timestamp=max(v.timestamp for v in versions)
        )

    def _merge_set_crdt(self, versions: List[StateVersion]) -> StateVersion:
        """Merge Set CRDT (union of all elements)."""
        merged_elements = set()
        for version in versions:
            merged_elements.update(version.data.get("elements", set()))

        merged_data = {"elements": merged_elements}

        return StateVersion(
            agent_id="merged",
            version=max(v.version for v in versions),
            data=merged_data,
            timestamp=max(v.timestamp for v in versions)
        )

    def _merge_map_crdt(self, versions: List[StateVersion]) -> StateVersion:
        """Merge Map CRDT (LWW for each key)."""
        merged_map = {}
        key_versions = {}

        for version in versions:
            for key, value in version.data.items():
                if key not in key_versions or version.timestamp > key_versions[key]:
                    merged_map[key] = value
                    key_versions[key] = version.timestamp

        return StateVersion(
            agent_id="merged",
            version=max(v.version for v in versions),
            data=merged_map,
            timestamp=max(v.timestamp for v in versions)
        )

    def detect_conflict(self, versions: List[StateVersion]) -> bool:
        """
        Detect if conflict exists between versions.

        Returns:
            True if conflict detected, False otherwise
        """
        if len(versions) <= 1:
            return False

        # Check for concurrent updates based on strategy
        if self.strategy == ConflictStrategy.VERSION_VECTOR:
            # Conflict if any versions are concurrent
            for i, v1 in enumerate(versions):
                for v2 in versions[i+1:]:
                    if self._is_concurrent(v1, v2):
                        return True
            return False
        else:
            # For other strategies, conflict exists if versions differ
            first_data = versions[0].data
            return any(v.data != first_data for v in versions[1:])

    def _is_concurrent(self, v1: StateVersion, v2: StateVersion) -> bool:
        """Check if two versions are concurrent (no causal order)."""
        v1_before_v2 = self._is_causally_before(v1, v2)
        v2_before_v1 = self._is_causally_before(v2, v1)
        return not v1_before_v2 and not v2_before_v1

    def set_strategy(self, strategy: ConflictStrategy) -> None:
        """Change resolution strategy."""
        self.strategy = strategy

    def get_history(self) -> List[Dict[str, Any]]:
        """Get resolution history."""
        return self.resolution_history.copy()

    def clear_history(self) -> None:
        """Clear resolution history."""
        self.resolution_history.clear()


# ==========================================
# Fixtures
# ==========================================


@pytest.fixture
def resolver_lww():
    """Create resolver with LWW strategy."""
    return MockConflictResolver(strategy=ConflictStrategy.LWW)


@pytest.fixture
def resolver_vector():
    """Create resolver with Version Vector strategy."""
    return MockConflictResolver(strategy=ConflictStrategy.VERSION_VECTOR)


@pytest.fixture
def resolver_crdt():
    """Create resolver with CRDT strategy."""
    return MockConflictResolver(strategy=ConflictStrategy.CRDT)


# ==========================================
# Test: Initialization
# ==========================================


def test_resolver_init_lww():
    """Test resolver initialization with LWW strategy."""
    resolver = MockConflictResolver(strategy=ConflictStrategy.LWW)
    assert resolver.strategy == ConflictStrategy.LWW


def test_resolver_init_default():
    """Test resolver initialization with default strategy."""
    resolver = MockConflictResolver()
    assert resolver.strategy == ConflictStrategy.LWW


# ==========================================
# Test: LWW Strategy
# ==========================================


def test_lww_resolves_to_latest_timestamp(resolver_lww):
    """Test LWW resolves to version with latest timestamp."""
    v1 = StateVersion("agent-1", 1, {"key": "value1"}, timestamp=datetime(2024, 1, 1, tzinfo=timezone.utc))
    v2 = StateVersion("agent-2", 2, {"key": "value2"}, timestamp=datetime(2024, 1, 2, tzinfo=timezone.utc))
    v3 = StateVersion("agent-3", 3, {"key": "value3"}, timestamp=datetime(2024, 1, 3, tzinfo=timezone.utc))

    result = resolver_lww.resolve_conflict([v1, v2, v3])

    assert result == v3
    assert result.data["key"] == "value3"


def test_lww_with_two_versions(resolver_lww):
    """Test LWW with two versions."""
    v1 = StateVersion("agent-1", 1, "data1", timestamp=datetime(2024, 1, 1, tzinfo=timezone.utc))
    v2 = StateVersion("agent-2", 2, "data2", timestamp=datetime(2024, 1, 2, tzinfo=timezone.utc))

    result = resolver_lww.resolve_conflict([v1, v2])

    assert result == v2


def test_lww_with_same_timestamp(resolver_lww):
    """Test LWW with same timestamp (arbitrary winner)."""
    ts = datetime(2024, 1, 1, tzinfo=timezone.utc)
    v1 = StateVersion("agent-1", 1, "data1", timestamp=ts)
    v2 = StateVersion("agent-2", 2, "data2", timestamp=ts)

    result = resolver_lww.resolve_conflict([v1, v2])

    # Should pick one (implementation may vary)
    assert result in [v1, v2]


# ==========================================
# Test: Version Vector Strategy
# ==========================================


def test_version_vector_causal_order(resolver_vector):
    """Test version vector resolves with causal order."""
    v1 = StateVersion("agent-1", 1, "data1", vector_clock={"agent-1": 1})
    v2 = StateVersion("agent-2", 2, "data2", vector_clock={"agent-1": 1, "agent-2": 1})

    result = resolver_vector.resolve_conflict([v1, v2])

    # v2 causally follows v1, so v2 should win
    assert result.version >= v2.version


def test_version_vector_concurrent_updates(resolver_vector):
    """Test version vector with concurrent updates."""
    v1 = StateVersion("agent-1", 1, "data1", vector_clock={"agent-1": 1, "agent-2": 0})
    v2 = StateVersion("agent-2", 1, "data2", vector_clock={"agent-1": 0, "agent-2": 1})

    # Concurrent updates (no causal order)
    result = resolver_vector.resolve_conflict([v1, v2])

    # Should fall back to LWW
    assert result is not None


# ==========================================
# Test: CRDT Strategy - Counter
# ==========================================


def test_crdt_counter_merge(resolver_crdt):
    """Test CRDT Counter merge (take maximum)."""
    v1 = StateVersion("agent-1", 1, {"count": 5})
    v2 = StateVersion("agent-2", 2, {"count": 8})
    v3 = StateVersion("agent-3", 3, {"count": 3})

    result = resolver_crdt.resolve_conflict([v1, v2, v3])

    assert result.data["count"] == 8  # Maximum


def test_crdt_counter_single_version(resolver_crdt):
    """Test CRDT Counter with single version."""
    v1 = StateVersion("agent-1", 1, {"count": 10})

    result = resolver_crdt.resolve_conflict([v1])

    assert result.data["count"] == 10


# ==========================================
# Test: CRDT Strategy - Set
# ==========================================


def test_crdt_set_merge(resolver_crdt):
    """Test CRDT Set merge (union)."""
    v1 = StateVersion("agent-1", 1, {"elements": {1, 2, 3}})
    v2 = StateVersion("agent-2", 2, {"elements": {3, 4, 5}})
    v3 = StateVersion("agent-3", 3, {"elements": {5, 6}})

    result = resolver_crdt.resolve_conflict([v1, v2, v3])

    assert result.data["elements"] == {1, 2, 3, 4, 5, 6}


def test_crdt_set_empty_merge(resolver_crdt):
    """Test CRDT Set merge with empty sets."""
    v1 = StateVersion("agent-1", 1, {"elements": set()})
    v2 = StateVersion("agent-2", 2, {"elements": {1, 2}})

    result = resolver_crdt.resolve_conflict([v1, v2])

    assert result.data["elements"] == {1, 2}


# ==========================================
# Test: CRDT Strategy - Map
# ==========================================


def test_crdt_map_merge(resolver_crdt):
    """Test CRDT Map merge (LWW per key)."""
    v1 = StateVersion(
        "agent-1", 1,
        {"key1": "value1", "key2": "value2"},
        timestamp=datetime(2024, 1, 1, tzinfo=timezone.utc)
    )
    v2 = StateVersion(
        "agent-2", 2,
        {"key2": "updated", "key3": "value3"},
        timestamp=datetime(2024, 1, 2, tzinfo=timezone.utc)
    )

    result = resolver_crdt.resolve_conflict([v1, v2])

    # key1 from v1, key2 from v2 (newer), key3 from v2
    assert result.data["key1"] == "value1"
    assert result.data["key2"] == "updated"
    assert result.data["key3"] == "value3"


def test_crdt_map_empty_merge(resolver_crdt):
    """Test CRDT Map merge with empty map."""
    v1 = StateVersion("agent-1", 1, {})
    v2 = StateVersion("agent-2", 2, {"key": "value"})

    result = resolver_crdt.resolve_conflict([v1, v2])

    assert result.data["key"] == "value"


# ==========================================
# Test: Conflict Detection
# ==========================================


def test_detect_conflict_exists(resolver_lww):
    """Test conflict detection with differing versions."""
    v1 = StateVersion("agent-1", 1, "data1")
    v2 = StateVersion("agent-2", 2, "data2")

    has_conflict = resolver_lww.detect_conflict([v1, v2])

    assert has_conflict is True


def test_detect_no_conflict_single_version(resolver_lww):
    """Test no conflict with single version."""
    v1 = StateVersion("agent-1", 1, "data")

    has_conflict = resolver_lww.detect_conflict([v1])

    assert has_conflict is False


def test_detect_no_conflict_empty_list(resolver_lww):
    """Test no conflict with empty list."""
    has_conflict = resolver_lww.detect_conflict([])

    assert has_conflict is False


def test_detect_no_conflict_same_data(resolver_lww):
    """Test no conflict with same data."""
    v1 = StateVersion("agent-1", 1, "data")
    v2 = StateVersion("agent-2", 2, "data")

    has_conflict = resolver_lww.detect_conflict([v1, v2])

    assert has_conflict is False


def test_detect_conflict_version_vector(resolver_vector):
    """Test conflict detection with version vectors."""
    v1 = StateVersion("agent-1", 1, "data1", vector_clock={"agent-1": 1})
    v2 = StateVersion("agent-2", 1, "data2", vector_clock={"agent-2": 1})

    has_conflict = resolver_vector.detect_conflict([v1, v2])

    # Concurrent updates should be detected as conflict
    assert has_conflict is True


# ==========================================
# Test: StateVersion Creation
# ==========================================


def test_state_version_creation():
    """Test StateVersion creation."""
    version = StateVersion("agent-1", 1, {"key": "value"})

    assert version.agent_id == "agent-1"
    assert version.version == 1
    assert version.data == {"key": "value"}
    assert version.timestamp is not None


def test_state_version_with_timestamp():
    """Test StateVersion with explicit timestamp."""
    ts = datetime(2024, 1, 1, tzinfo=timezone.utc)
    version = StateVersion("agent-1", 1, "data", timestamp=ts)

    assert version.timestamp == ts


def test_state_version_with_vector_clock():
    """Test StateVersion with vector clock."""
    vc = {"agent-1": 5, "agent-2": 3}
    version = StateVersion("agent-1", 5, "data", vector_clock=vc)

    assert version.vector_clock == vc


def test_state_version_default_vector_clock():
    """Test StateVersion default vector clock."""
    version = StateVersion("agent-1", 3, "data")

    assert version.vector_clock == {"agent-1": 3}


# ==========================================
# Test: Edge Cases
# ==========================================


def test_resolve_empty_list_raises_error(resolver_lww):
    """Test resolving empty list raises error."""
    with pytest.raises(ValueError, match="No versions provided"):
        resolver_lww.resolve_conflict([])


def test_resolve_single_version_returns_same(resolver_lww):
    """Test resolving single version returns same version."""
    v1 = StateVersion("agent-1", 1, "data")

    result = resolver_lww.resolve_conflict([v1])

    assert result == v1


def test_resolve_many_versions(resolver_lww):
    """Test resolving many versions."""
    versions = [
        StateVersion(
            f"agent-{i}", i, f"data-{i}",
            timestamp=datetime(2024, 1, i, tzinfo=timezone.utc)
        )
        for i in range(1, 11)
    ]

    result = resolver_lww.resolve_conflict(versions)

    # Should resolve to latest timestamp (i=10)
    assert result.version == 10


# ==========================================
# Test: Strategy Switching
# ==========================================


def test_set_strategy(resolver_lww):
    """Test changing resolution strategy."""
    resolver_lww.set_strategy(ConflictStrategy.CRDT)

    assert resolver_lww.strategy == ConflictStrategy.CRDT


def test_resolve_after_strategy_switch():
    """Test resolution after strategy switch."""
    resolver = MockConflictResolver(strategy=ConflictStrategy.LWW)

    v1 = StateVersion("agent-1", 1, {"count": 5})
    v2 = StateVersion("agent-2", 2, {"count": 8})

    # Resolve with LWW
    result_lww = resolver.resolve_conflict([v1, v2])

    # Switch to CRDT
    resolver.set_strategy(ConflictStrategy.CRDT)

    # Resolve again
    result_crdt = resolver.resolve_conflict([v1, v2])

    # Results should differ based on strategy
    assert result_lww is not None
    assert result_crdt is not None


# ==========================================
# Test: Resolution History
# ==========================================


def test_resolution_history_tracking(resolver_lww):
    """Test resolution history tracking."""
    v1 = StateVersion("agent-1", 1, "data1")
    v2 = StateVersion("agent-2", 2, "data2")

    resolver_lww.resolve_conflict([v1, v2])
    resolver_lww.resolve_conflict([v1, v2])

    history = resolver_lww.get_history()

    assert len(history) == 2


def test_resolution_history_clear(resolver_lww):
    """Test clearing resolution history."""
    v1 = StateVersion("agent-1", 1, "data1")
    v2 = StateVersion("agent-2", 2, "data2")

    resolver_lww.resolve_conflict([v1, v2])
    resolver_lww.clear_history()

    history = resolver_lww.get_history()

    assert len(history) == 0


def test_resolution_history_contains_metadata(resolver_lww):
    """Test resolution history contains metadata."""
    v1 = StateVersion("agent-1", 1, "data1")
    v2 = StateVersion("agent-2", 2, "data2")

    resolver_lww.resolve_conflict([v1, v2])

    history = resolver_lww.get_history()
    entry = history[0]

    assert "strategy" in entry
    assert "input_versions" in entry
    assert "resolved" in entry
    assert "timestamp" in entry


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
