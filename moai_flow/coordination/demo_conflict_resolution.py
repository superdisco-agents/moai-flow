#!/usr/bin/env python3
"""
Demo script for ConflictResolver and StateSynchronizer

Demonstrates:
1. ConflictResolver with all 3 strategies (LWW, Vector, CRDT)
2. StateSynchronizer integration patterns
3. Real-world conflict scenarios

Run: python3 -m moai_flow.coordination.demo_conflict_resolution
"""

from datetime import datetime, timezone, timedelta
from conflict_resolver import ConflictResolver, StateVersion, ResolutionStrategy
from state_synchronizer import StateSynchronizer


def demo_lww_resolution():
    """Demonstrate Last-Write-Wins conflict resolution."""
    print("\n" + "=" * 70)
    print("DEMO 1: Last-Write-Wins (LWW) Resolution")
    print("=" * 70)

    resolver = ConflictResolver(strategy="lww")

    # Create conflicting versions
    now = datetime.now(timezone.utc)
    conflicts = [
        StateVersion(
            state_key="counter",
            value=42,
            version=1,
            timestamp=now - timedelta(seconds=10),
            agent_id="agent-1",
            metadata={}
        ),
        StateVersion(
            state_key="counter",
            value=45,
            version=2,
            timestamp=now,  # Most recent
            agent_id="agent-2",
            metadata={}
        ),
        StateVersion(
            state_key="counter",
            value=40,
            version=1,
            timestamp=now - timedelta(seconds=20),
            agent_id="agent-3",
            metadata={}
        ),
    ]

    print(f"\nConflicting versions:")
    for sv in conflicts:
        print(f"  - Agent {sv.agent_id}: value={sv.value}, version={sv.version}, "
              f"timestamp={sv.timestamp.isoformat()}")

    resolved = resolver.resolve("counter", conflicts)

    print(f"\nResolved version:")
    print(f"  - Agent {resolved.agent_id}: value={resolved.value}, "
          f"version={resolved.version}")
    print(f"  - Strategy: {resolved.metadata.get('resolution_strategy')}")
    print(f"  - Discarded: {resolved.metadata.get('discarded_versions')} versions")


def demo_vector_resolution():
    """Demonstrate Vector Clock conflict resolution."""
    print("\n" + "=" * 70)
    print("DEMO 2: Vector Clock Resolution")
    print("=" * 70)

    resolver = ConflictResolver(strategy="vector")

    now = datetime.now(timezone.utc)

    # Scenario 1: Causal dominance (agent-2 has seen agent-1's updates)
    print("\nScenario 1: Causal Dominance")
    conflicts = [
        StateVersion(
            state_key="task_queue",
            value=["task-1", "task-2"],
            version=2,
            timestamp=now - timedelta(seconds=5),
            agent_id="agent-1",
            metadata={"vector_clock": {"agent-1": 2, "agent-2": 0}}
        ),
        StateVersion(
            state_key="task_queue",
            value=["task-1", "task-2", "task-3"],
            version=3,
            timestamp=now,
            agent_id="agent-2",
            metadata={"vector_clock": {"agent-1": 2, "agent-2": 1}}  # Dominates
        ),
    ]

    print("Vector clocks:")
    for sv in conflicts:
        print(f"  - {sv.agent_id}: {sv.metadata['vector_clock']}")

    resolved = resolver.resolve("task_queue", conflicts)
    print(f"\nResolved: {len(resolved.value)} tasks from {resolved.agent_id}")
    print(f"Strategy: {resolved.metadata.get('resolution_strategy')}")

    # Scenario 2: Concurrent updates (no causal dominance)
    print("\n\nScenario 2: Concurrent Updates")
    conflicts = [
        StateVersion(
            state_key="config",
            value={"timeout": 30},
            version=1,
            timestamp=now - timedelta(seconds=5),
            agent_id="agent-1",
            metadata={"vector_clock": {"agent-1": 1, "agent-2": 0}}
        ),
        StateVersion(
            state_key="config",
            value={"timeout": 60},
            version=1,
            timestamp=now,
            agent_id="agent-2",
            metadata={"vector_clock": {"agent-1": 0, "agent-2": 1}}  # Concurrent
        ),
    ]

    print("Vector clocks (concurrent):")
    for sv in conflicts:
        print(f"  - {sv.agent_id}: {sv.metadata['vector_clock']}")

    resolved = resolver.resolve("config", conflicts)
    print(f"\nResolved: {resolved.value} from {resolved.agent_id}")
    print(f"Strategy: {resolved.metadata.get('resolution_strategy')} (fallback to LWW)")


def demo_crdt_resolution():
    """Demonstrate CRDT conflict resolution."""
    print("\n" + "=" * 70)
    print("DEMO 3: CRDT Resolution")
    print("=" * 70)

    resolver = ConflictResolver(strategy="crdt")
    now = datetime.now(timezone.utc)

    # Counter CRDT (sum all values)
    print("\nCounter CRDT (sum values):")
    conflicts = [
        StateVersion(
            state_key="request_count",
            value=100,
            version=1,
            timestamp=now,
            agent_id="agent-1",
            metadata={"crdt_type": "counter"}
        ),
        StateVersion(
            state_key="request_count",
            value=150,
            version=1,
            timestamp=now,
            agent_id="agent-2",
            metadata={"crdt_type": "counter"}
        ),
        StateVersion(
            state_key="request_count",
            value=75,
            version=1,
            timestamp=now,
            agent_id="agent-3",
            metadata={"crdt_type": "counter"}
        ),
    ]

    print(f"Values: {[sv.value for sv in conflicts]}")
    resolved = resolver.resolve("request_count", conflicts)
    print(f"Merged value: {resolved.value} (sum)")

    # Set CRDT (union)
    print("\n\nSet CRDT (union):")
    conflicts = [
        StateVersion(
            state_key="active_users",
            value=["user-1", "user-2"],
            version=1,
            timestamp=now,
            agent_id="agent-1",
            metadata={"crdt_type": "set"}
        ),
        StateVersion(
            state_key="active_users",
            value=["user-2", "user-3"],
            version=1,
            timestamp=now,
            agent_id="agent-2",
            metadata={"crdt_type": "set"}
        ),
    ]

    print(f"Sets: {[sv.value for sv in conflicts]}")
    resolved = resolver.resolve("active_users", conflicts)
    print(f"Merged set: {resolved.value} (union)")

    # Map CRDT (LWW per key)
    print("\n\nMap CRDT (LWW per key):")
    conflicts = [
        StateVersion(
            state_key="config",
            value={"timeout": 30, "retries": 3},
            version=1,
            timestamp=now - timedelta(seconds=5),
            agent_id="agent-1",
            metadata={"crdt_type": "map"}
        ),
        StateVersion(
            state_key="config",
            value={"timeout": 60, "max_connections": 100},
            version=1,
            timestamp=now,  # Newer timestamp
            agent_id="agent-2",
            metadata={"crdt_type": "map"}
        ),
    ]

    print(f"Maps:")
    for sv in conflicts:
        print(f"  - {sv.agent_id}: {sv.value}")
    resolved = resolver.resolve("config", conflicts)
    print(f"Merged map: {resolved.value}")
    print(f"  - timeout: {resolved.value['timeout']} (from agent-2, newer)")
    print(f"  - retries: {resolved.value.get('retries', 'N/A')} (from agent-1)")
    print(f"  - max_connections: {resolved.value.get('max_connections', 'N/A')} (from agent-2)")


def demo_conflict_detection():
    """Demonstrate conflict detection."""
    print("\n" + "=" * 70)
    print("DEMO 4: Conflict Detection")
    print("=" * 70)

    resolver = ConflictResolver(strategy="lww")
    now = datetime.now(timezone.utc)

    # Scenario 1: No conflicts (all agents agree)
    print("\nScenario 1: No conflicts")
    states = {
        "agent-1": StateVersion("counter", 42, 1, now, "agent-1", {}),
        "agent-2": StateVersion("status", "active", 1, now, "agent-2", {}),
    }

    conflicts = resolver.detect_conflicts(states)
    print(f"Conflicting keys: {conflicts}")

    # Scenario 2: Conflicts detected
    print("\nScenario 2: Conflicts detected")
    states = {
        "agent-1": StateVersion("counter", 42, 1, now, "agent-1", {}),
        "agent-2": StateVersion("counter", 45, 2, now, "agent-2", {}),
        "agent-3": StateVersion("counter", 40, 1, now, "agent-3", {}),
    }

    conflicts = resolver.detect_conflicts(states)
    print(f"Conflicting keys: {conflicts}")
    print(f"Values: {[states[agent].value for agent in states]}")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("ConflictResolver & StateSynchronizer Demo")
    print("=" * 70)

    demo_lww_resolution()
    demo_vector_resolution()
    demo_crdt_resolution()
    demo_conflict_detection()

    print("\n" + "=" * 70)
    print("Demo complete!")
    print("=" * 70)
