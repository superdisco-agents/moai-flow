#!/usr/bin/env python3
"""
Standalone CRDT examples runner to bypass circular import issues.

This script directly loads and demonstrates CRDT usage without
going through the package hierarchy that has circular dependencies.
"""

import importlib.util
import time

# Load crdt module directly
spec = importlib.util.spec_from_file_location(
    'crdt',
    'moai_flow/coordination/algorithms/crdt.py'
)
crdt_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(crdt_module)

# Import CRDT classes
PNCounter = crdt_module.PNCounter
LWWRegister = crdt_module.LWWRegister
GCounter = crdt_module.GCounter
ORSet = crdt_module.ORSet


def example_1_distributed_counter():
    """
    Example 1: Distributed Counter for Resource Usage Tracking
    """
    print("=" * 70)
    print("Example 1: Distributed Resource Counter")
    print("=" * 70)

    # Agent 1: API gateway tracking requests
    agent1_counter = PNCounter("api-gateway")
    print("\n[Agent 1: API Gateway]")
    print("Processing requests...")

    agent1_counter.increment(100)  # 100 successful requests
    print(f"  + 100 successful requests")

    agent1_counter.decrement(5)    # 5 failed requests
    print(f"  - 5 failed requests")

    agent1_counter.increment(50)   # 50 more successful
    print(f"  + 50 more successful requests")

    print(f"Agent 1 total: {agent1_counter.value()} requests")

    # Agent 2: Background worker tracking tasks
    agent2_counter = PNCounter("background-worker")
    print("\n[Agent 2: Background Worker]")
    print("Processing tasks...")

    agent2_counter.increment(75)   # 75 tasks completed
    print(f"  + 75 tasks completed")

    agent2_counter.decrement(3)    # 3 tasks failed
    print(f"  - 3 tasks failed")

    print(f"Agent 2 total: {agent2_counter.value()} tasks")

    # Agent 3: Data processor tracking records
    agent3_counter = PNCounter("data-processor")
    print("\n[Agent 3: Data Processor]")
    print("Processing records...")

    agent3_counter.increment(200)  # 200 records processed
    print(f"  + 200 records processed")

    agent3_counter.decrement(10)   # 10 invalid records
    print(f"  - 10 invalid records")

    print(f"Agent 3 total: {agent3_counter.value()} records")

    # Merge all counters for global view
    print("\n[Merging Counters]")
    print("Combining all agent metrics...")

    merged = agent1_counter.merge(agent2_counter).merge(agent3_counter)

    print(f"\nGlobal Resource Usage Summary:")
    print(f"  Agent 1 (API Gateway):     {agent1_counter.value():>4} operations")
    print(f"  Agent 2 (Worker):          {agent2_counter.value():>4} operations")
    print(f"  Agent 3 (Data Processor):  {agent3_counter.value():>4} operations")
    print(f"  " + "-" * 40)
    print(f"  Total Operations:          {merged.value():>4}")

    # Demonstrate commutativity (order doesn't matter)
    print("\n[Verification: Commutativity]")
    alternative_merge = agent3_counter.merge(agent1_counter).merge(agent2_counter)
    print(f"Merge order 1: {merged.value()}")
    print(f"Merge order 2: {alternative_merge.value()}")
    print(f"Results match: {merged.value() == alternative_merge.value()} ✓")

    print("\n" + "=" * 70)


def example_2_lww_configuration():
    """
    Example 2: Last-Write-Wins Configuration Management
    """
    print("\n" * 2)
    print("=" * 70)
    print("Example 2: Dynamic Configuration with Last-Write-Wins")
    print("=" * 70)

    # Agent 1: Sets initial configuration
    agent1_config = LWWRegister("agent-alpha")
    print("\n[Agent Alpha] Setting initial configuration...")
    agent1_config.set({
        "mode": "development",
        "debug": True,
        "max_workers": 4
    })
    print(f"  Timestamp: {agent1_config.timestamp():.3f}")
    print(f"  Config: {agent1_config.value()}")

    # Simulate network delay
    time.sleep(0.1)

    # Agent 2: Updates configuration (later timestamp)
    agent2_config = LWWRegister("agent-beta")
    print("\n[Agent Beta] Updating configuration (0.1s later)...")
    agent2_config.set({
        "mode": "production",
        "debug": False,
        "max_workers": 8
    })
    print(f"  Timestamp: {agent2_config.timestamp():.3f}")
    print(f"  Config: {agent2_config.value()}")

    # Merge: Agent 2's update should win (later timestamp)
    print("\n[Merging Configurations]")
    print("Resolving conflict...")

    merged = agent1_config.merge(agent2_config)

    print(f"\nMerged Configuration (Winner: Agent {merged._writer_id}):")
    print(f"  {merged.value()}")
    print(f"  Reason: Latest timestamp ({merged.timestamp():.3f})")

    # Demonstrate commutativity (same result regardless of merge order)
    print("\n[Verification: Commutativity]")
    reverse_merge = agent2_config.merge(agent1_config)
    print(f"Merge 1 (alpha.merge(beta)): {merged.value()}")
    print(f"Merge 2 (beta.merge(alpha)): {reverse_merge.value()}")
    print(f"Results match: {merged.value() == reverse_merge.value()} ✓")

    print("\n" + "=" * 70)


def main():
    """Run all CRDT examples."""
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 15 + "CRDT Integration Examples" + " " * 28 + "║")
    print("║" + " " * 10 + "Conflict-Free Distributed Coordination" + " " * 19 + "║")
    print("╚" + "═" * 68 + "╝")

    # Run examples
    example_1_distributed_counter()
    example_2_lww_configuration()

    # Summary
    print("\n" * 2)
    print("=" * 70)
    print("Summary: CRDT Benefits")
    print("=" * 70)
    print("""
✓ No Coordination Required: Agents merge states without locks or consensus
✓ Commutative: Merge order doesn't matter (A.merge(B) == B.merge(A))
✓ Associative: Grouping doesn't matter ((A⊕B)⊕C == A⊕(B⊕C))
✓ Idempotent: Merging multiple times is safe (A.merge(A) == A)
✓ Eventually Consistent: All replicas converge to same state
✓ Partition Tolerant: Works during network partitions

Use Cases:
  • Distributed counters (metrics, quotas, resource tracking)
  • Configuration management (feature flags, settings)
  • Collaborative editing (shared documents, task lists)
  • Cache synchronization (distributed caches)
  • Event sourcing (append-only logs)
    """)
    print("=" * 70)


if __name__ == "__main__":
    main()
