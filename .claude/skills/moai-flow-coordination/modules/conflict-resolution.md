# Conflict Resolution Module

State conflict resolution strategies for distributed multi-agent systems: Last-Write-Wins (LWW), Vector Clocks, and Conflict-free Replicated Data Types (CRDTs).

## Table of Contents

1. [Conflict Resolution Overview](#conflict-resolution-overview)
2. [StateVersion Data Structure](#stateversion-data-structure)
3. [LWW (Last-Write-Wins) Strategy](#lww-last-write-wins-strategy)
4. [Vector Clock Strategy](#vector-clock-strategy)
5. [CRDT Strategy](#crdt-strategy)
6. [Strategy Selection Guide](#strategy-selection-guide)
7. [Advanced Patterns](#advanced-patterns)

---

## Conflict Resolution Overview

### The Problem

When multiple agents concurrently update the same state, conflicts arise:

```
Agent-1: counter = 42 (timestamp: 10:00:00)
Agent-2: counter = 45 (timestamp: 10:00:01)
Agent-3: counter = 40 (timestamp: 09:59:59)

Which value is correct?
```

### Resolution Strategies

| Strategy | Mechanism | Guarantees | Use Case |
|----------|-----------|------------|----------|
| **LWW** | Timestamp-based | Eventual consistency | Simple conflicts, reliable clocks |
| **Vector** | Causality tracking | Preserves happened-before | Distributed updates, causality matters |
| **CRDT** | Semantic merge | Strong eventual consistency | Concurrent updates, no data loss |

### ConflictResolver Architecture

```python
class ConflictResolver:
    def __init__(self, strategy="lww"):
        self.strategy = ResolutionStrategy(strategy)

    def resolve(self, state_key, conflicts):
        """Resolve conflicts using configured strategy."""
        if self.strategy == ResolutionStrategy.LWW:
            return self._resolve_lww(conflicts)
        elif self.strategy == ResolutionStrategy.VECTOR:
            return self._resolve_vector(conflicts)
        elif self.strategy == ResolutionStrategy.CRDT:
            return self._resolve_crdt(conflicts)

    def detect_conflicts(self, states):
        """Detect conflicting state keys across agents."""
        # Returns list of state_keys with conflicts
```

---

## StateVersion Data Structure

Represents a single version of state from an agent.

### Data Model

```python
@dataclass
class StateVersion:
    state_key: str           # Unique state identifier
    value: Any               # Actual state value
    version: int             # Monotonic version number
    timestamp: datetime      # Creation timestamp (UTC timezone-aware)
    agent_id: str            # Agent that created this version
    metadata: Dict[str, Any] # Strategy-specific metadata

    def __post_init__(self):
        # Validate state_key
        if not self.state_key:
            raise ValueError("state_key cannot be empty")

        # Ensure timezone-aware timestamp
        if self.timestamp.tzinfo is None:
            self.timestamp = self.timestamp.replace(tzinfo=timezone.utc)
```

### Usage Example

```python
from moai_flow.coordination import StateVersion
from datetime import datetime, timezone

state = StateVersion(
    state_key="task_count",
    value=42,
    version=5,
    timestamp=datetime.now(timezone.utc),
    agent_id="agent-1",
    metadata={
        "crdt_type": "counter",
        "vector_clock": {"agent-1": 5, "agent-2": 3}
    }
)
```

### Metadata Fields

**Common metadata**:
- `crdt_type`: CRDT type (counter, set, map, register)
- `vector_clock`: Causality tracking dict
- `merge_info`: Information about previous merges
- `resolution_strategy`: Strategy used for resolution

**LWW metadata**:
- `resolved_at`: Resolution timestamp
- `discarded_versions`: Count of discarded versions

**Vector metadata**:
- `vector_clock`: Dict mapping agent_id to version
- `concurrent`: Boolean indicating concurrent updates

**CRDT metadata**:
- `crdt_type`: Type of CRDT (counter, set, map, register)
- `merged_from_agents`: List of agents merged

---

## LWW (Last-Write-Wins) Strategy

Simplest strategy: newest timestamp wins.

### Algorithm

```python
def _resolve_lww(self, conflicts: List[StateVersion]) -> StateVersion:
    # Select version with latest timestamp
    resolved = max(conflicts, key=lambda sv: sv.timestamp)

    # Add metadata
    resolved.metadata["resolution_strategy"] = "lww"
    resolved.metadata["resolved_at"] = datetime.now(timezone.utc).isoformat()
    resolved.metadata["discarded_versions"] = len(conflicts) - 1

    return resolved
```

### Usage

```python
from moai_flow.coordination import ConflictResolver, StateVersion
from datetime import datetime, timezone

resolver = ConflictResolver(strategy="lww")

conflicts = [
    StateVersion("counter", 42, 1, datetime(2025, 1, 1, 10, 0, 0, tzinfo=timezone.utc), "agent-1", {}),
    StateVersion("counter", 45, 2, datetime(2025, 1, 1, 10, 0, 1, tzinfo=timezone.utc), "agent-2", {}),
    StateVersion("counter", 40, 3, datetime(2025, 1, 1, 9, 59, 59, tzinfo=timezone.utc), "agent-3", {})
]

resolved = resolver.resolve("counter", conflicts)
print(resolved.value)  # 45 (newest timestamp: 10:00:01)
print(resolved.agent_id)  # agent-2
```

### Pros and Cons

**Advantages**:
- Fast (O(n) for finding max)
- Simple to understand
- Works well with synchronized clocks
- No additional metadata required

**Disadvantages**:
- Clock skew issues
- Concurrent updates at same timestamp undefined
- Loses all but one update
- No causality tracking

### Best Practices

```python
# Use with NTP-synchronized clocks
# Add millisecond precision
timestamp = datetime.now(timezone.utc)

# Handle clock skew
if abs((ts1 - ts2).total_seconds()) < 0.001:
    # Use secondary criteria (agent_id, version)
    pass

# Audit trail
resolved.metadata["lww_discarded"] = [
    {"agent": sv.agent_id, "value": sv.value, "timestamp": sv.timestamp.isoformat()}
    for sv in conflicts if sv != resolved
]
```

---

## Vector Clock Strategy

Causality-aware resolution using vector clocks.

### Algorithm

```python
def _resolve_vector(self, conflicts: List[StateVersion]) -> StateVersion:
    # Extract vector clocks
    versions_with_clocks = [
        (sv, sv.metadata.get("vector_clock", {sv.agent_id: sv.version}))
        for sv in conflicts
    ]

    # Find causally dominating version
    for sv1, vc1 in versions_with_clocks:
        dominates_all = all(
            sv1 == sv2 or self._vector_dominates(vc1, vc2)
            for sv2, vc2 in versions_with_clocks
        )

        if dominates_all:
            # Causal winner found
            sv1.metadata["resolution_strategy"] = "vector_causal"
            return sv1

    # No causal dominance = concurrent updates
    # Fall back to LWW
    resolved = self._resolve_lww(conflicts)
    resolved.metadata["resolution_strategy"] = "vector_concurrent_lww"
    return resolved
```

### Vector Clock Dominance

```python
def _vector_dominates(self, vc1: Dict[str, int], vc2: Dict[str, int]) -> bool:
    """
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
```

### Usage Example

```python
resolver = ConflictResolver(strategy="vector")

conflicts = [
    StateVersion(
        "document", "Version A", 1, datetime.now(timezone.utc), "agent-1",
        metadata={"vector_clock": {"agent-1": 5, "agent-2": 3}}
    ),
    StateVersion(
        "document", "Version B", 2, datetime.now(timezone.utc), "agent-2",
        metadata={"vector_clock": {"agent-1": 4, "agent-2": 6}}
    )
]

resolved = resolver.resolve("document", conflicts)

# Check resolution strategy
if resolved.metadata["resolution_strategy"] == "vector_causal":
    print("Causal winner found")
elif resolved.metadata["resolution_strategy"] == "vector_concurrent_lww":
    print("Concurrent updates, fell back to LWW")
```

### Vector Clock Scenarios

**Scenario 1: Causal dominance**
```
vc1 = {"agent-1": 5, "agent-2": 3}  # Happened before vc2
vc2 = {"agent-1": 4, "agent-2": 6}  # Neither dominates
→ Concurrent, fall back to LWW

vc1 = {"agent-1": 5, "agent-2": 4}  # Dominates vc2
vc2 = {"agent-1": 4, "agent-2": 3}  # All values <=
→ vc1 wins (causal)
```

**Scenario 2: Concurrent updates**
```
vc1 = {"agent-1": 5, "agent-2": 2}  # agent-1 ahead
vc2 = {"agent-1": 3, "agent-2": 6}  # agent-2 ahead
→ Neither dominates → Concurrent → LWW
```

### Pros and Cons

**Advantages**:
- Preserves happened-before relationships
- Detects concurrent updates
- No clock synchronization needed
- Causal consistency

**Disadvantages**:
- Requires vector clock maintenance
- O(n) space per version (n = number of agents)
- Falls back to LWW for concurrent updates
- Complex to implement correctly

---

## CRDT Strategy

Semantic merge based on data type.

### CRDT Types

```python
class CRDTType(Enum):
    COUNTER = "counter"      # G-Counter (increment-only)
    SET = "set"              # G-Set (grow-only)
    MAP = "map"              # LWW-Map (per-key LWW)
    REGISTER = "register"    # LWW-Register (simple value)
```

### Algorithm

```python
def _resolve_crdt(self, conflicts: List[StateVersion]) -> StateVersion:
    # Detect CRDT type
    crdt_type = self._detect_crdt_type(conflicts[0])

    # Merge based on type
    if crdt_type == CRDTType.COUNTER:
        merged_value = self._merge_counter(conflicts)
    elif crdt_type == CRDTType.SET:
        merged_value = self._merge_set(conflicts)
    elif crdt_type == CRDTType.MAP:
        merged_value = self._merge_map(conflicts)
    else:  # REGISTER
        merged_value = self._merge_register(conflicts)

    # Create merged state version
    merged = StateVersion(
        state_key=conflicts[0].state_key,
        value=merged_value,
        version=max(sv.version for sv in conflicts) + 1,
        timestamp=datetime.now(timezone.utc),
        agent_id="coordinator",
        metadata={
            "resolution_strategy": "crdt",
            "crdt_type": crdt_type.value,
            "merged_from_agents": [sv.agent_id for sv in conflicts]
        }
    )

    return merged
```

### Counter CRDT

**G-Counter** (Grow-only counter): Sum all values

```python
def _merge_counter(self, conflicts: List[StateVersion]) -> Union[int, float]:
    total = sum(sv.value for sv in conflicts)
    return total

# Example
conflicts = [
    StateVersion("counter", 42, 1, datetime.now(timezone.utc), "agent-1",
                 {"crdt_type": "counter"}),
    StateVersion("counter", 45, 2, datetime.now(timezone.utc), "agent-2",
                 {"crdt_type": "counter"})
]

resolved = resolver.resolve("counter", conflicts)
print(resolved.value)  # 87 (42 + 45)
```

### Set CRDT

**G-Set** (Grow-only set): Union of all sets

```python
def _merge_set(self, conflicts: List[StateVersion]) -> List[Any]:
    merged_set = set()
    for sv in conflicts:
        if isinstance(sv.value, set):
            merged_set.update(sv.value)
        elif isinstance(sv.value, list):
            merged_set.update(sv.value)
    return list(merged_set)

# Example
conflicts = [
    StateVersion("tags", ["tag1", "tag2"], 1, datetime.now(timezone.utc), "agent-1",
                 {"crdt_type": "set"}),
    StateVersion("tags", ["tag2", "tag3"], 2, datetime.now(timezone.utc), "agent-2",
                 {"crdt_type": "set"})
]

resolved = resolver.resolve("tags", conflicts)
print(resolved.value)  # ["tag1", "tag2", "tag3"]
```

### Map CRDT

**LWW-Map**: Last-write-wins per key

```python
def _merge_map(self, conflicts: List[StateVersion]) -> Dict[str, Any]:
    merged_map = {}
    key_timestamps = {}

    for sv in conflicts:
        if not isinstance(sv.value, dict):
            continue

        for key, value in sv.value.items():
            # LWW per key
            if key not in key_timestamps or sv.timestamp > key_timestamps[key]:
                merged_map[key] = value
                key_timestamps[key] = sv.timestamp

    return merged_map

# Example
conflicts = [
    StateVersion("config", {"key1": "v1", "key2": "v2"}, 1,
                 datetime(2025, 1, 1, tzinfo=timezone.utc), "agent-1",
                 {"crdt_type": "map"}),
    StateVersion("config", {"key2": "v3", "key3": "v4"}, 2,
                 datetime(2025, 1, 2, tzinfo=timezone.utc), "agent-2",
                 {"crdt_type": "map"})
]

resolved = resolver.resolve("config", conflicts)
print(resolved.value)  # {"key1": "v1", "key2": "v3", "key3": "v4"}
# key2 uses v3 (newer timestamp from agent-2)
```

### Register CRDT

**LWW-Register**: Last-write-wins for simple values

```python
def _merge_register(self, conflicts: List[StateVersion]) -> Any:
    latest = max(conflicts, key=lambda sv: sv.timestamp)
    return latest.value

# Example (falls back to LWW)
conflicts = [
    StateVersion("status", "active", 1, datetime(2025, 1, 1, tzinfo=timezone.utc), "agent-1", {}),
    StateVersion("status", "idle", 2, datetime(2025, 1, 2, tzinfo=timezone.utc), "agent-2", {})
]

resolved = resolver.resolve("status", conflicts)
print(resolved.value)  # "idle" (newest)
```

### CRDT Type Detection

```python
def _detect_crdt_type(self, state_version: StateVersion) -> CRDTType:
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
```

### Pros and Cons

**Advantages**:
- No data loss (semantic merge)
- Strong eventual consistency
- Commutative and associative merges
- Works with any network topology

**Disadvantages**:
- Requires type-specific logic
- Some operations not supported (delete in G-Set)
- Higher complexity
- Potential memory growth (sets)

---

## Strategy Selection Guide

### Decision Matrix

```
Data Type?
  → Counter (increments) → CRDT (Counter)
  → Set (add-only) → CRDT (Set)
  → Map (key-value) → CRDT (Map) or Vector
  → Simple value → LWW or Vector

Causality matters?
  → YES → Vector Clock
  → NO → LWW or CRDT

Data loss acceptable?
  → YES → LWW
  → NO → CRDT

Network conditions?
  → Reliable clocks → LWW
  → Unreliable clocks → Vector or CRDT
```

### Use Case Examples

| Use Case | Strategy | Rationale |
|----------|----------|-----------|
| Counter (task count) | CRDT (Counter) | No data loss, sum all increments |
| Tags/labels | CRDT (Set) | Union preserves all tags |
| Configuration | CRDT (Map) | Per-key LWW |
| Last status | LWW | Newest status wins |
| Causally related edits | Vector | Preserve happened-before |
| Simple timestamp-based | LWW | Fast and simple |

---

## Advanced Patterns

### Hybrid Strategy

```python
class HybridResolver:
    def resolve(self, state_key, conflicts):
        # Choose strategy based on state_key
        if state_key.startswith("counter_"):
            resolver = ConflictResolver("crdt")
        elif state_key.startswith("causal_"):
            resolver = ConflictResolver("vector")
        else:
            resolver = ConflictResolver("lww")

        return resolver.resolve(state_key, conflicts)
```

### Conflict Detection with Threshold

```python
def detect_conflicts_with_threshold(self, states, time_threshold_ms=1000):
    """Detect conflicts within time threshold."""
    conflicts = {}

    for state_key in states.keys():
        versions = [sv for sv in states.values() if sv.state_key == state_key]

        if len(versions) > 1:
            # Check if timestamps within threshold
            timestamps = [sv.timestamp for sv in versions]
            max_ts = max(timestamps)
            min_ts = min(timestamps)

            if (max_ts - min_ts).total_seconds() * 1000 < time_threshold_ms:
                conflicts[state_key] = versions

    return conflicts
```

### Resolution Auditing

```python
def resolve_with_audit(self, state_key, conflicts):
    resolved = self.resolve(state_key, conflicts)

    # Audit trail
    audit_entry = {
        "state_key": state_key,
        "strategy": self.strategy.value,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "input_versions": len(conflicts),
        "winner": {
            "agent_id": resolved.agent_id,
            "value": resolved.value,
            "version": resolved.version
        },
        "discarded": [
            {"agent": sv.agent_id, "value": sv.value}
            for sv in conflicts if sv != resolved
        ]
    }

    # Log or store audit entry
    logger.info(f"Conflict resolution: {audit_entry}")

    return resolved, audit_entry
```

---

**Next**: [State Synchronization Module](state-synchronization.md)
