#!/usr/bin/env python3
"""
ConflictResolver - State Conflict Resolution System

Resolves conflicts between multiple state versions from different agents
using configurable resolution strategies:
- LWW (Last-Write-Wins): Timestamp-based simple resolution
- Vector Clocks: Causality-based version tracking
- CRDT (Conflict-free Replicated Data Type): Semantic merge strategies

Key Features:
- Three resolution strategies for different use cases
- Automatic conflict detection across agent states
- Metadata preservation for audit trails
- Type-aware CRDT merging (counters, sets, maps)
- Causal ordering detection with vector clocks
- Production-ready with comprehensive error handling

Usage:
    >>> resolver = ConflictResolver(strategy="lww")
    >>> conflicts = [
    ...     StateVersion("counter", 42, 1, datetime.now(), "agent-1", {}),
    ...     StateVersion("counter", 45, 2, datetime.now(), "agent-2", {})
    ... ]
    >>> resolved = resolver.resolve("counter", conflicts)
    >>> print(resolved.value)  # 45 (newer version)

Version: 1.0.0
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Union
from enum import Enum

logger = logging.getLogger(__name__)


# ============================================================================
# Data Structures
# ============================================================================

@dataclass
class StateVersion:
    """
    Represents a single version of state from an agent.

    Attributes:
        state_key: Unique identifier for this state
        value: The actual state value (can be any JSON-serializable type)
        version: Integer version number (monotonically increasing)
        timestamp: When this version was created (UTC timezone-aware)
        agent_id: Agent that created this version
        metadata: Additional context (e.g., vector_clock, merge_info)
    """
    state_key: str
    value: Any
    version: int
    timestamp: datetime
    agent_id: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate and normalize fields."""
        if not self.state_key:
            raise ValueError("state_key cannot be empty")
        if self.version < 0:
            raise ValueError(f"version must be >= 0, got {self.version}")

        # Ensure timezone-aware timestamp
        if self.timestamp.tzinfo is None:
            self.timestamp = self.timestamp.replace(tzinfo=timezone.utc)


class ResolutionStrategy(Enum):
    """Supported conflict resolution strategies."""
    LWW = "lww"              # Last-Write-Wins (timestamp-based)
    VECTOR = "vector"        # Vector clocks (causality-based)
    CRDT = "crdt"            # CRDT semantic merge


class CRDTType(Enum):
    """CRDT data structure types."""
    COUNTER = "counter"      # G-Counter (increment-only)
    SET = "set"              # G-Set (grow-only set)
    MAP = "map"              # LWW-Map (last-write-wins per key)
    REGISTER = "register"    # LWW-Register (simple value)


# ============================================================================
# ConflictResolver Implementation
# ============================================================================

class ConflictResolver:
    """
    Resolves conflicts between multiple state versions using
    configurable resolution strategies.

    Strategies:
        LWW: Simple timestamp-based resolution (fastest)
        Vector: Causality detection via vector clocks (medium complexity)
        CRDT: Semantic merge based on data type (most sophisticated)

    Example:
        >>> resolver = ConflictResolver(strategy="vector")
        >>> conflicts = detect_conflicts(agent_states)
        >>> for state_key in conflicts:
        ...     resolved = resolver.resolve(state_key, conflicts[state_key])
        ...     broadcast_resolved_state(state_key, resolved)
    """

    def __init__(self, strategy: str = "lww"):
        """
        Initialize conflict resolver with specified strategy.

        Args:
            strategy: Resolution strategy ("lww", "vector", "crdt")

        Raises:
            ValueError: If strategy is not supported
        """
        if strategy not in [s.value for s in ResolutionStrategy]:
            raise ValueError(
                f"Invalid strategy '{strategy}'. "
                f"Supported: {[s.value for s in ResolutionStrategy]}"
            )

        self.strategy = ResolutionStrategy(strategy)
        logger.info(f"ConflictResolver initialized with strategy: {self.strategy.value}")

    def resolve(
        self,
        state_key: str,
        conflicts: List[StateVersion]
    ) -> StateVersion:
        """
        Resolve conflicts between multiple state versions.

        Args:
            state_key: State identifier being resolved
            conflicts: List of conflicting state versions from different agents

        Returns:
            Resolved state version

        Raises:
            ValueError: If conflicts list is empty or state_key mismatch
        """
        if not conflicts:
            raise ValueError("conflicts list cannot be empty")

        # Validate all state_keys match
        for sv in conflicts:
            if sv.state_key != state_key:
                raise ValueError(
                    f"state_key mismatch: expected '{state_key}', "
                    f"got '{sv.state_key}'"
                )

        # Single version = no conflict
        if len(conflicts) == 1:
            logger.debug(f"No conflict for '{state_key}': single version")
            return conflicts[0]

        # Route to appropriate resolution strategy
        if self.strategy == ResolutionStrategy.LWW:
            resolved = self._resolve_lww(conflicts)
        elif self.strategy == ResolutionStrategy.VECTOR:
            resolved = self._resolve_vector(conflicts)
        elif self.strategy == ResolutionStrategy.CRDT:
            resolved = self._resolve_crdt(conflicts)
        else:
            raise RuntimeError(f"Unexpected strategy: {self.strategy}")

        logger.info(
            f"Resolved conflict for '{state_key}': "
            f"{len(conflicts)} versions → agent {resolved.agent_id}"
        )
        return resolved

    def detect_conflicts(
        self,
        states: Dict[str, StateVersion]
    ) -> List[str]:
        """
        Detect which state keys have conflicts across agents.

        Args:
            states: Dict mapping agent_id to StateVersion

        Returns:
            List of state_keys that have conflicts (appear in multiple agents)

        Example:
            >>> states = {
            ...     "agent-1": StateVersion("counter", 10, 1, ...),
            ...     "agent-2": StateVersion("counter", 12, 2, ...)
            ... }
            >>> conflicts = resolver.detect_conflicts(states)
            >>> print(conflicts)  # ["counter"]
        """
        # Group states by state_key
        state_groups: Dict[str, List[str]] = {}
        for agent_id, state_version in states.items():
            state_key = state_version.state_key
            if state_key not in state_groups:
                state_groups[state_key] = []
            state_groups[state_key].append(agent_id)

        # Find state_keys with multiple agents (conflicts)
        conflicts = [
            state_key
            for state_key, agent_ids in state_groups.items()
            if len(agent_ids) > 1
        ]

        logger.debug(f"Detected {len(conflicts)} conflicts: {conflicts}")
        return conflicts

    # ========================================================================
    # Resolution Strategy Implementations
    # ========================================================================

    def _resolve_lww(self, conflicts: List[StateVersion]) -> StateVersion:
        """
        Last-Write-Wins: Select version with latest timestamp.

        Simplest strategy, works well when:
        - Timestamps are reliable
        - Concurrent writes are rare
        - Losing some updates is acceptable

        Args:
            conflicts: List of conflicting state versions

        Returns:
            StateVersion with latest timestamp
        """
        resolved = max(conflicts, key=lambda sv: sv.timestamp)

        # Add metadata about resolution
        resolved.metadata["resolution_strategy"] = "lww"
        resolved.metadata["resolved_at"] = datetime.now(timezone.utc).isoformat()
        resolved.metadata["discarded_versions"] = len(conflicts) - 1

        logger.debug(
            f"LWW resolution: selected version {resolved.version} "
            f"from agent {resolved.agent_id}"
        )
        return resolved

    def _resolve_vector(self, conflicts: List[StateVersion]) -> StateVersion:
        """
        Vector Clock resolution: Detect causality and merge accordingly.

        Uses vector clocks to determine if one version causally dominates others.
        If concurrent updates detected, falls back to LWW.

        Vector Clock Format:
            metadata["vector_clock"] = {"agent-1": 5, "agent-2": 3}

        Args:
            conflicts: List of conflicting state versions

        Returns:
            StateVersion that causally dominates, or LWW if concurrent
        """
        # Extract vector clocks
        versions_with_clocks = []
        for sv in conflicts:
            vector_clock = sv.metadata.get("vector_clock", {})
            if not vector_clock:
                # No vector clock = treat as new version
                vector_clock = {sv.agent_id: sv.version}
            versions_with_clocks.append((sv, vector_clock))

        # Find causally dominating version (if exists)
        for sv1, vc1 in versions_with_clocks:
            dominates_all = True
            for sv2, vc2 in versions_with_clocks:
                if sv1 == sv2:
                    continue
                if not self._vector_dominates(vc1, vc2):
                    dominates_all = False
                    break

            if dominates_all:
                # Found causal winner
                sv1.metadata["resolution_strategy"] = "vector_causal"
                sv1.metadata["resolved_at"] = datetime.now(timezone.utc).isoformat()
                logger.debug(
                    f"Vector resolution: causal winner from agent {sv1.agent_id}"
                )
                return sv1

        # No causal dominance = concurrent updates
        # Fall back to LWW
        logger.debug("Vector resolution: concurrent updates, falling back to LWW")
        resolved = self._resolve_lww(conflicts)
        resolved.metadata["resolution_strategy"] = "vector_concurrent_lww"
        return resolved

    def _resolve_crdt(self, conflicts: List[StateVersion]) -> StateVersion:
        """
        CRDT resolution: Semantic merge based on data type.

        Merges values using CRDT semantics:
        - Counter: Sum all values
        - Set: Union of all sets
        - Map: Merge keys with LWW per key
        - Register: LWW for simple values

        Args:
            conflicts: List of conflicting state versions

        Returns:
            StateVersion with merged value
        """
        # Detect CRDT type from metadata or infer from value
        crdt_type = self._detect_crdt_type(conflicts[0])

        if crdt_type == CRDTType.COUNTER:
            merged_value = self._merge_counter(conflicts)
        elif crdt_type == CRDTType.SET:
            merged_value = self._merge_set(conflicts)
        elif crdt_type == CRDTType.MAP:
            merged_value = self._merge_map(conflicts)
        else:  # REGISTER
            merged_value = self._merge_register(conflicts)

        # Create merged state version
        latest = max(conflicts, key=lambda sv: sv.timestamp)
        merged = StateVersion(
            state_key=conflicts[0].state_key,
            value=merged_value,
            version=max(sv.version for sv in conflicts) + 1,
            timestamp=datetime.now(timezone.utc),
            agent_id="coordinator",  # Merged by coordinator
            metadata={
                "resolution_strategy": "crdt",
                "crdt_type": crdt_type.value,
                "merged_from_agents": [sv.agent_id for sv in conflicts],
                "resolved_at": datetime.now(timezone.utc).isoformat()
            }
        )

        logger.debug(
            f"CRDT resolution: merged {len(conflicts)} versions "
            f"using {crdt_type.value} semantics"
        )
        return merged

    # ========================================================================
    # Helper Methods
    # ========================================================================

    def _vector_dominates(
        self,
        vc1: Dict[str, int],
        vc2: Dict[str, int]
    ) -> bool:
        """
        Check if vector clock vc1 causally dominates vc2.

        vc1 dominates vc2 if:
        - For all agents A: vc1[A] >= vc2[A]
        - For at least one agent: vc1[A] > vc2[A]
        """
        all_agents = set(vc1.keys()) | set(vc2.keys())

        at_least_one_greater = False
        for agent in all_agents:
            v1 = vc1.get(agent, 0)
            v2 = vc2.get(agent, 0)

            if v1 < v2:
                return False  # vc1 doesn't dominate
            if v1 > v2:
                at_least_one_greater = True

        return at_least_one_greater

    def _detect_crdt_type(self, state_version: StateVersion) -> CRDTType:
        """Detect CRDT type from metadata or infer from value type."""
        # Explicit type in metadata
        if "crdt_type" in state_version.metadata:
            return CRDTType(state_version.metadata["crdt_type"])

        # Infer from value type
        value = state_version.value
        if isinstance(value, (int, float)):
            return CRDTType.COUNTER
        elif isinstance(value, (set, list)):
            return CRDTType.SET
        elif isinstance(value, dict):
            return CRDTType.MAP
        else:
            return CRDTType.REGISTER

    def _merge_counter(self, conflicts: List[StateVersion]) -> Union[int, float]:
        """Sum all counter values."""
        total = sum(sv.value for sv in conflicts)
        logger.debug(f"Counter merge: {len(conflicts)} values → {total}")
        return total

    def _merge_set(self, conflicts: List[StateVersion]) -> List[Any]:
        """Union of all sets."""
        merged_set: Set[Any] = set()
        for sv in conflicts:
            if isinstance(sv.value, set):
                merged_set.update(sv.value)
            elif isinstance(sv.value, list):
                merged_set.update(sv.value)

        result = list(merged_set)
        logger.debug(
            f"Set merge: {len(conflicts)} sets → {len(result)} unique items"
        )
        return result

    def _merge_map(self, conflicts: List[StateVersion]) -> Dict[str, Any]:
        """Merge maps with LWW per key."""
        merged_map: Dict[str, Any] = {}
        key_timestamps: Dict[str, datetime] = {}

        for sv in conflicts:
            if not isinstance(sv.value, dict):
                continue

            for key, value in sv.value.items():
                # LWW per key
                if key not in key_timestamps or sv.timestamp > key_timestamps[key]:
                    merged_map[key] = value
                    key_timestamps[key] = sv.timestamp

        logger.debug(
            f"Map merge: {len(conflicts)} maps → {len(merged_map)} keys"
        )
        return merged_map

    def _merge_register(self, conflicts: List[StateVersion]) -> Any:
        """LWW for simple register values."""
        latest = max(conflicts, key=lambda sv: sv.timestamp)
        logger.debug(f"Register merge: LWW from agent {latest.agent_id}")
        return latest.value


# ============================================================================
# Module Exports
# ============================================================================

__all__ = [
    "ConflictResolver",
    "StateVersion",
    "ResolutionStrategy",
    "CRDTType",
]
