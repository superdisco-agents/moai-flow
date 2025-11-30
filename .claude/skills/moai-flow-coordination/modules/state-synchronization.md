# State Synchronization Module

Distributed state synchronization across agent swarms with full sync, delta sync, and version management.

## Table of Contents

1. [Synchronization Overview](#synchronization-overview)
2. [StateSynchronizer Architecture](#statesynchronizer-architecture)
3. [Full State Synchronization](#full-state-synchronization)
4. [Delta Synchronization](#delta-synchronization)
5. [Version Management](#version-management)
6. [Integration Patterns](#integration-patterns)
7. [Performance Optimization](#performance-optimization)

---

## Synchronization Overview

### The Challenge

Multiple agents maintain independent state copies:

```
Agent-1: task_count = 42, last_update = 10:00:00
Agent-2: task_count = 45, last_update = 10:00:01
Agent-3: task_count = 40, last_update = 09:59:59

How to ensure all agents converge to same state?
```

### Synchronization Modes

| Mode | Description | Bandwidth | Latency | Use Case |
|------|-------------|-----------|---------|----------|
| **Full Sync** | Broadcast all state | High | ~100-500ms | Initial sync, major updates |
| **Delta Sync** | Only changes since version N | Low | ~50-200ms | Incremental updates, reconnects |
| **Version Query** | Check current version | Minimal | ~10-50ms | Change detection |

### Architecture Overview

```python
class StateSynchronizer:
    def __init__(self, coordinator, memory, conflict_resolver, default_timeout_ms=10000):
        self.coordinator = coordinator  # Message broadcasting
        self.memory = memory  # State persistence
        self.conflict_resolver = conflict_resolver  # Conflict resolution
        self._state_versions = {}  # Version tracking
```

---

## StateSynchronizer Architecture

### Core Components

```python
class StateSynchronizer:
    """
    Synchronize state across all agents in a swarm.

    Components:
    - coordinator: ICoordinator for message broadcast
    - memory: IMemoryProvider for state persistence
    - conflict_resolver: ConflictResolver for conflict resolution
    - _state_versions: Dict tracking current versions per (swarm_id, state_key)
    """

    def synchronize_state(self, swarm_id, state_key, timeout_ms=None):
        """Full state synchronization protocol."""

    def delta_sync(self, swarm_id, since_version):
        """Delta synchronization (incremental updates)."""

    def get_state_version(self, swarm_id, state_key):
        """Get current version number."""

    def get_state(self, swarm_id, state_key):
        """Retrieve synchronized state."""

    def clear_state(self, swarm_id, state_key=None):
        """Clear synchronized state."""
```

### Integration Points

```
┌──────────────────────────────────────┐
│   StateSynchronizer                  │
├──────────────────────────────────────┤
│  ↓ Uses                              │
│  ICoordinator (broadcast_message)    │ → Message routing
│  IMemoryProvider (store/retrieve)    │ → State persistence
│  ConflictResolver (resolve)          │ → Conflict resolution
└──────────────────────────────────────┘
```

---

## Full State Synchronization

### Protocol Flow

```
1. Broadcast state_request to all agents
   ↓
2. Wait for responses (with timeout)
   ↓
3. Collect state versions from agents
   ↓
4. Detect conflicts (different values/versions)
   ↓
5. Resolve conflicts using ConflictResolver
   ↓
6. Broadcast resolved state to all agents
   ↓
7. Store in memory provider
   ↓
8. Update version tracking
```

### Implementation

```python
def synchronize_state(
    self,
    swarm_id: str,
    state_key: str,
    timeout_ms: Optional[int] = None
) -> bool:
    """
    Synchronize state across all agents in swarm.

    Args:
        swarm_id: Unique swarm identifier
        state_key: State identifier to synchronize
        timeout_ms: Optional timeout override

    Returns:
        True if synchronized successfully, False otherwise
    """
    timeout = timeout_ms or self.default_timeout_ms
    request_id = self._sync_request_id
    self._sync_request_id += 1

    # Step 1: Broadcast state request
    sync_request = {
        "type": "state_request",
        "state_key": state_key,
        "request_id": request_id,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    recipients = self.coordinator.broadcast_message(
        from_agent="coordinator",
        message=sync_request
    )

    if recipients == 0:
        return False

    # Step 2-3: Collect responses
    responses = self._collect_state_responses(
        swarm_id, state_key, request_id, timeout
    )

    if not responses:
        return False

    # Step 4-5: Detect and resolve conflicts
    conflicts = self._detect_conflicts(responses)

    if not conflicts:
        resolved = responses[0]  # No conflicts, use any version
    else:
        resolved = self.conflict_resolver.resolve(state_key, responses)

    # Step 6: Broadcast resolved state
    sync_update = {
        "type": "state_update",
        "state_key": state_key,
        "value": resolved.value,
        "version": resolved.version + 1,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "metadata": resolved.metadata
    }

    self.coordinator.broadcast_message("coordinator", sync_update)

    # Step 7-8: Store and track version
    self.memory.store(
        swarm_id=swarm_id,
        namespace="synchronized_state",
        key=state_key,
        value={
            "value": resolved.value,
            "version": resolved.version + 1,
            "timestamp": sync_update["timestamp"],
            "metadata": resolved.metadata
        },
        persistent=True
    )

    self._state_versions[(swarm_id, state_key)] = resolved.version + 1

    return True
```

### Usage Example

```python
from moai_flow.coordination import StateSynchronizer, ConflictResolver
from moai_flow.core import SwarmCoordinator
from moai_flow.memory import MemoryProvider

# Setup
coordinator = SwarmCoordinator(topology="mesh")
memory = MemoryProvider()
resolver = ConflictResolver(strategy="crdt")

synchronizer = StateSynchronizer(coordinator, memory, resolver)

# Synchronize state
success = synchronizer.synchronize_state(
    swarm_id="swarm-001",
    state_key="task_queue",
    timeout_ms=10000
)

if success:
    print("State synchronized successfully")
else:
    print("Synchronization failed")
```

### Response Collection

```python
def _collect_state_responses(
    self,
    swarm_id: str,
    state_key: str,
    request_id: int,
    timeout_ms: int
) -> List[StateVersion]:
    """
    Collect state responses from agents with timeout.

    In production:
    1. Listen to message queue for state_response messages
    2. Match responses by request_id
    3. Timeout after specified duration
    4. Handle partial responses gracefully
    """
    # Simulate collection delay
    time.sleep(timeout_ms / 1000.0 * 0.1)

    # Get topology info
    topology_info = self.coordinator.get_topology_info()
    agent_count = topology_info.get("agent_count", 0)

    # In production, collect actual agent responses
    responses = []
    # ... message queue listening logic

    return responses
```

### Conflict Detection

```python
def _detect_conflicts(self, responses: List[StateVersion]) -> bool:
    """
    Detect if responses contain conflicts.

    Args:
        responses: List of state versions from agents

    Returns:
        True if conflicts exist (different values/versions)
    """
    if len(responses) <= 1:
        return False

    first = responses[0]
    for response in responses[1:]:
        if response.value != first.value or response.version != first.version:
            return True

    return False
```

---

## Delta Synchronization

Efficient incremental synchronization for large swarms.

### Concept

Only transmit state changes since a specific version:

```
Agent offline from v5 to v10:
- Full sync: Transmit all state (large)
- Delta sync: Transmit only changes v6-v10 (small)

Bandwidth savings: 60-90% for typical workloads
```

### Implementation

```python
def delta_sync(
    self,
    swarm_id: str,
    since_version: int
) -> List[StateVersion]:
    """
    Get only state changes since specific version.

    Args:
        swarm_id: Unique swarm identifier
        since_version: Only return changes after this version

    Returns:
        List of StateVersion objects with changes since version
    """
    # Retrieve all synchronized state from memory
    all_keys = self.memory.list_keys(
        swarm_id=swarm_id,
        namespace="synchronized_state"
    )

    changes = []

    for state_key in all_keys:
        state_data = self.memory.retrieve(
            swarm_id=swarm_id,
            namespace="synchronized_state",
            key=state_key
        )

        if not state_data:
            continue

        # Check if version is newer than requested
        version = state_data.get("version", 0)
        if version > since_version:
            state_version = StateVersion(
                state_key=state_key,
                value=state_data["value"],
                version=version,
                timestamp=datetime.fromisoformat(state_data["timestamp"]),
                agent_id="coordinator",
                metadata=state_data.get("metadata", {})
            )
            changes.append(state_version)

    return changes
```

### Usage Example

```python
# Agent reconnects after being offline
last_known_version = agent.get_last_known_version()

# Fetch only changes since last known version
changes = synchronizer.delta_sync(
    swarm_id="swarm-001",
    since_version=last_known_version
)

print(f"Received {len(changes)} state updates")

# Apply changes
for change in changes:
    agent.update_state(change.state_key, change.value)
    print(f"Updated {change.state_key} to v{change.version}")
```

### Delta Sync Protocol

```
Agent reconnects:
  ↓
Get last known version (stored locally)
  ↓
Request delta_sync(swarm_id, since_version)
  ↓
Synchronizer queries memory for versions > since_version
  ↓
Return only changed states
  ↓
Agent applies delta updates
```

### Performance Comparison

```python
# Scenario: 100 states, agent offline for 10 updates

# Full sync
full_sync_bandwidth = 100 states * avg_state_size
# Example: 100 * 1KB = 100KB

# Delta sync
delta_sync_bandwidth = 10 changed_states * avg_state_size
# Example: 10 * 1KB = 10KB

# Savings: 90KB (90%)
```

---

## Version Management

Track state versions for delta sync and change detection.

### Version Tracking

```python
# Version storage
self._state_versions: Dict[Tuple[str, str], int] = {}

# Key format: (swarm_id, state_key)
version_key = ("swarm-001", "task_queue")
current_version = self._state_versions[version_key]
```

### Get State Version

```python
def get_state_version(
    self,
    swarm_id: str,
    state_key: str
) -> Optional[int]:
    """
    Get current version number for a state.

    Returns:
        Current version number, or None if state not found
    """
    state_data = self.memory.retrieve(
        swarm_id=swarm_id,
        namespace="synchronized_state",
        key=state_key
    )

    if state_data:
        return state_data.get("version")
    return None

# Usage
version = synchronizer.get_state_version("swarm-001", "counter")
print(f"Current version: {version}")
```

### Get State

```python
def get_state(
    self,
    swarm_id: str,
    state_key: str
) -> Optional[StateVersion]:
    """
    Get current synchronized state.

    Returns:
        StateVersion object or None if not found
    """
    state_data = self.memory.retrieve(
        swarm_id=swarm_id,
        namespace="synchronized_state",
        key=state_key
    )

    if not state_data:
        return None

    return StateVersion(
        state_key=state_key,
        value=state_data["value"],
        version=state_data["version"],
        timestamp=datetime.fromisoformat(state_data["timestamp"]),
        agent_id="coordinator",
        metadata=state_data.get("metadata", {})
    )

# Usage
state = synchronizer.get_state("swarm-001", "task_queue")
if state:
    print(f"Value: {state.value}")
    print(f"Version: {state.version}")
```

### Clear State

```python
def clear_state(
    self,
    swarm_id: str,
    state_key: Optional[str] = None
) -> bool:
    """
    Clear synchronized state.

    Args:
        swarm_id: Unique swarm identifier
        state_key: Optional specific state to clear (clears all if None)

    Returns:
        True if cleared successfully
    """
    if state_key:
        # Clear specific state
        success = self.memory.delete(
            swarm_id=swarm_id,
            namespace="synchronized_state",
            key=state_key
        )

        # Remove version tracking
        version_key = (swarm_id, state_key)
        if version_key in self._state_versions:
            del self._state_versions[version_key]

        return success
    else:
        # Clear all synchronized state
        success = self.memory.clear_namespace(
            swarm_id=swarm_id,
            namespace="synchronized_state"
        )

        # Clear all version tracking for this swarm
        self._state_versions = {
            k: v for k, v in self._state_versions.items()
            if k[0] != swarm_id
        }

        return success

# Usage
synchronizer.clear_state("swarm-001", "temp_data")  # Clear one
synchronizer.clear_state("swarm-001")  # Clear all
```

---

## Integration Patterns

### Complete Coordination Pipeline

```python
from moai_flow.coordination import (
    ConsensusManager,
    ConflictResolver,
    StateSynchronizer
)

# Setup
coordinator = SwarmCoordinator()
memory = MemoryProvider()
consensus = ConsensusManager(coordinator, default_algorithm="quorum")
resolver = ConflictResolver(strategy="crdt")
synchronizer = StateSynchronizer(coordinator, memory, resolver)

# Workflow: Propose → Vote → Sync
proposal = {"action": "update_counter", "value": 100}

# Step 1: Consensus decision
result = consensus.request_consensus(proposal)

if result.decision == "approved":
    # Step 2: Synchronize approved state
    synchronizer.synchronize_state("swarm-001", "counter")
    print("State synchronized across swarm")
```

### Agent Reconnection Pattern

```python
class Agent:
    def reconnect(self, swarm_id):
        """Agent reconnection with delta sync."""
        # Get last known version before disconnect
        last_version = self.get_last_synced_version()

        # Fetch only changes since disconnect
        changes = synchronizer.delta_sync(swarm_id, since_version=last_version)

        # Apply delta updates
        for change in changes:
            self.update_local_state(change.state_key, change.value)
            self.set_last_synced_version(change.version)

        print(f"Caught up with {len(changes)} state changes")
```

### Periodic Synchronization

```python
import asyncio

async def periodic_sync(synchronizer, swarm_id, interval_seconds=60):
    """Periodic state synchronization."""
    while True:
        await asyncio.sleep(interval_seconds)

        # Sync all critical states
        critical_states = ["task_queue", "agent_registry", "metrics"]

        for state_key in critical_states:
            success = synchronizer.synchronize_state(swarm_id, state_key)
            if success:
                print(f"Synced {state_key}")
            else:
                print(f"Failed to sync {state_key}")
```

---

## Performance Optimization

### Batch Synchronization

```python
async def batch_sync(synchronizer, swarm_id, state_keys, timeout_ms=5000):
    """Synchronize multiple states in parallel."""
    tasks = [
        asyncio.create_task(
            asyncio.to_thread(
                synchronizer.synchronize_state,
                swarm_id, state_key, timeout_ms
            )
        )
        for state_key in state_keys
    ]

    results = await asyncio.gather(*tasks)

    successes = sum(1 for r in results if r)
    print(f"Synchronized {successes}/{len(state_keys)} states")

# Usage
await batch_sync(synchronizer, "swarm-001", ["counter", "queue", "registry"])
```

### Compression

```python
import zlib
import json

def compress_state(state_value):
    """Compress state value for transmission."""
    serialized = json.dumps(state_value)
    compressed = zlib.compress(serialized.encode())
    return compressed

def decompress_state(compressed_value):
    """Decompress received state."""
    decompressed = zlib.decompress(compressed_value)
    state_value = json.loads(decompressed.decode())
    return state_value

# Example: 90% bandwidth reduction for large states
```

### Caching

```python
class CachedSynchronizer:
    def __init__(self, synchronizer, cache_ttl_seconds=60):
        self.synchronizer = synchronizer
        self.cache = {}
        self.cache_ttl = cache_ttl_seconds

    def get_state(self, swarm_id, state_key):
        cache_key = (swarm_id, state_key)

        # Check cache
        if cache_key in self.cache:
            state, timestamp = self.cache[cache_key]
            age = (datetime.now(timezone.utc) - timestamp).total_seconds()

            if age < self.cache_ttl:
                return state  # Cache hit

        # Cache miss, fetch from synchronizer
        state = self.synchronizer.get_state(swarm_id, state_key)
        self.cache[cache_key] = (state, datetime.now(timezone.utc))

        return state
```

### Selective Synchronization

```python
def selective_sync(synchronizer, swarm_id, priority_states):
    """Synchronize only high-priority states."""
    for state_key, priority in priority_states.items():
        if priority == "critical":
            timeout_ms = 30000  # Longer timeout
        elif priority == "high":
            timeout_ms = 10000
        else:
            timeout_ms = 5000  # Fast timeout

        synchronizer.synchronize_state(swarm_id, state_key, timeout_ms)

# Usage
priority_states = {
    "task_queue": "critical",
    "agent_registry": "high",
    "metrics": "medium"
}
selective_sync(synchronizer, "swarm-001", priority_states)
```

---

**Next**: [Task Delegation Module](task-delegation.md)
