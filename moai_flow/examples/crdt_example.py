"""
CRDT Integration Examples

Demonstrates practical usage of Conflict-Free Replicated Data Types (CRDTs)
for distributed agent coordination scenarios.

Example 1: Distributed Counter (Resource Usage Tracking)
Example 2: Last-Write-Wins Configuration (Dynamic Settings)
"""

import time
from moai_flow.coordination.algorithms.crdt import (
    PNCounter,
    LWWRegister,
    GCounter,
    ORSet,
)


def example_1_distributed_counter():
    """
    Example 1: Distributed Counter for Resource Usage Tracking

    Scenario: Multiple agents independently track resource usage
    (API calls, memory, CPU time). Each agent increments/decrements
    their local counter. Counters are periodically merged to get
    global resource usage.

    CRDT Used: PNCounter (supports both increment and decrement)
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

    Scenario: Multiple agents can update shared configuration settings.
    When conflicts occur (two agents update simultaneously), the most
    recent update wins. If timestamps tie, agent ID breaks the tie.

    CRDT Used: LWWRegister (last-write-wins with timestamp)
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

    # Simulate tie-breaking with same timestamp
    print("\n[Tie-Breaking Scenario]")
    print("Two agents update at the exact same timestamp...")

    agent3_config = LWWRegister("agent-gamma")
    agent3_config._value = {"mode": "gamma-mode", "priority": "high"}
    agent3_config._timestamp = 1000.0
    agent3_config._writer_id = "agent-gamma"

    agent4_config = LWWRegister("agent-delta")
    agent4_config._value = {"mode": "delta-mode", "priority": "low"}
    agent4_config._timestamp = 1000.0  # Same timestamp
    agent4_config._writer_id = "agent-delta"

    tie_merged = agent3_config.merge(agent4_config)

    print(f"Agent Gamma timestamp: {agent3_config.timestamp()}")
    print(f"Agent Delta timestamp: {agent4_config.timestamp()}")
    print(f"Timestamps are equal: {agent3_config.timestamp() == agent4_config.timestamp()}")
    print(f"\nWinner (by agent_id): {tie_merged._writer_id}")
    print(f"  Lexicographic order: gamma > delta")
    print(f"  Config: {tie_merged.value()}")

    print("\n" + "=" * 70)


def example_3_distributed_task_queue():
    """
    Example 3: Distributed Task Queue with ORSet

    Scenario: Multiple agents add and remove tasks from a shared queue.
    Concurrent add/remove operations are handled with add-wins semantics.

    CRDT Used: ORSet (Observed-Remove Set)
    """
    print("\n" * 2)
    print("=" * 70)
    print("Example 3: Distributed Task Queue (ORSet)")
    print("=" * 70)

    # Agent 1: Task scheduler
    scheduler = ORSet("scheduler")
    print("\n[Scheduler] Adding tasks to queue...")

    scheduler.add("task-001: process-data")
    scheduler.add("task-002: send-email")
    scheduler.add("task-003: backup-db")

    print(f"  Tasks added: {scheduler.to_set()}")
    print(f"  Queue size: {len(scheduler)}")

    # Agent 2: Worker picks up task
    worker1 = ORSet("worker-1")
    print("\n[Worker 1] Starting fresh...")
    print(f"  Queue size: {len(worker1)}")

    # Merge with scheduler to get tasks
    worker1 = worker1.merge(scheduler)
    print(f"  After sync: {worker1.to_set()}")

    # Worker processes a task
    print("\n[Worker 1] Processing task-001...")
    worker1.remove("task-001: process-data")
    print(f"  Remaining tasks: {worker1.to_set()}")

    # Agent 3: Another worker, also removes a task
    worker2 = ORSet("worker-2")
    worker2 = worker2.merge(scheduler)
    print("\n[Worker 2] Processing task-002...")
    worker2.remove("task-002: send-email")
    print(f"  Remaining tasks: {worker2.to_set()}")

    # Merge all agents to get final state
    print("\n[Merging All Agents]")
    final_queue = scheduler.merge(worker1).merge(worker2)

    print(f"Final queue state:")
    print(f"  Completed: task-001, task-002")
    print(f"  Remaining: {final_queue.to_set()}")
    print(f"  Queue size: {len(final_queue)}")

    # Demonstrate add-wins semantics
    print("\n[Add-Wins Conflict Resolution]")
    print("Scenario: Scheduler adds task while worker removes it...")

    agent_a = ORSet("agent-a")
    agent_a.add("task-conflict")
    agent_a.remove("task-conflict")  # Remove after add

    agent_b = ORSet("agent-b")
    agent_b.add("task-conflict")     # Concurrent add

    conflict_resolved = agent_a.merge(agent_b)

    print(f"Agent A: added then removed")
    print(f"Agent B: added concurrently")
    print(f"Result (add-wins): {'task-conflict' in conflict_resolved}")
    print(f"  Task is present: {conflict_resolved.to_set()}")

    print("\n" + "=" * 70)


def example_4_grow_only_counter():
    """
    Example 4: Grow-Only Counter for Metrics

    Scenario: Multiple monitoring agents track cumulative metrics
    (page views, downloads, sign-ups). Counts can only increase.

    CRDT Used: GCounter (Grow-only Counter)
    """
    print("\n" * 2)
    print("=" * 70)
    print("Example 4: Grow-Only Metrics Counter (GCounter)")
    print("=" * 70)

    # Agent 1: Web server tracking page views
    web_server = GCounter("web-server-1")
    print("\n[Web Server 1]")
    print("Tracking page views...")

    web_server.increment(1500)  # 1500 page views
    print(f"  + 1500 page views")

    web_server.increment(300)   # 300 more
    print(f"  + 300 more page views")

    print(f"Server 1 total: {web_server.value()} views")

    # Agent 2: Another web server
    web_server2 = GCounter("web-server-2")
    print("\n[Web Server 2]")
    print("Tracking page views...")

    web_server2.increment(2000)
    print(f"  + 2000 page views")

    print(f"Server 2 total: {web_server2.value()} views")

    # Agent 3: CDN edge node
    cdn_edge = GCounter("cdn-edge-1")
    print("\n[CDN Edge Node]")
    print("Tracking cached page views...")

    cdn_edge.increment(5000)
    print(f"  + 5000 cached views")

    print(f"CDN total: {cdn_edge.value()} views")

    # Merge for global metrics
    print("\n[Global Metrics Dashboard]")
    global_counter = web_server.merge(web_server2).merge(cdn_edge)

    print(f"\nPage View Summary:")
    print(f"  Web Server 1:  {web_server.value():>6} views")
    print(f"  Web Server 2:  {web_server2.value():>6} views")
    print(f"  CDN Edge:      {cdn_edge.value():>6} views")
    print(f"  " + "-" * 30)
    print(f"  Total Views:   {global_counter.value():>6}")

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
    example_3_distributed_task_queue()
    example_4_grow_only_counter()

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
