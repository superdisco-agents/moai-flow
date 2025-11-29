#!/usr/bin/env python3
"""
MetricsCollector Integration Demo for MoAI-Flow

Demonstrates metrics collection integrated with SwarmCoordinator
for Phase 6A observability foundation.

Shows:
- Task metric collection
- Agent performance tracking
- Swarm health monitoring
- Integration with SwarmCoordinator
- Statistics and aggregation
- Performance overhead measurement

Run:
    python moai_flow/examples/metrics_collector_demo.py
"""

import time
from pathlib import Path

# Import SwarmCoordinator
from moai_flow.core.swarm_coordinator import SwarmCoordinator, AgentState

# Import MetricsCollector
from moai_flow.monitoring import (
    MetricsCollector,
    MetricsStorage,
    TaskResult
)


def demo_basic_metrics_collection():
    """Demo 1: Basic metrics collection without storage"""
    print("=== Demo 1: Basic Metrics Collection ===\n")

    # Initialize collector without storage (in-memory only)
    collector = MetricsCollector(async_mode=False)
    print("✓ MetricsCollector initialized (in-memory mode)")

    # Record task metrics
    print("\nRecording task metrics...")
    collector.record_task_metric(
        task_id="task-001",
        agent_id="expert-backend",
        duration_ms=3500,
        result=TaskResult.SUCCESS,
        tokens_used=25000,
        files_changed=3
    )
    print("  ✓ Task 1: SUCCESS (3500ms, 25K tokens, 3 files)")

    collector.record_task_metric(
        task_id="task-002",
        agent_id="expert-backend",
        duration_ms=2800,
        result=TaskResult.SUCCESS,
        tokens_used=18000,
        files_changed=2
    )
    print("  ✓ Task 2: SUCCESS (2800ms, 18K tokens, 2 files)")

    collector.record_task_metric(
        task_id="task-003",
        agent_id="expert-frontend",
        duration_ms=4200,
        result=TaskResult.FAILURE,
        tokens_used=12000,
        files_changed=0
    )
    print("  ✓ Task 3: FAILURE (4200ms, 12K tokens, 0 files)")

    # Get statistics
    print("\n--- Statistics ---")
    backend_stats = collector.get_task_stats(agent_id="expert-backend")
    print(f"Backend Agent:")
    print(f"  - Tasks: {backend_stats['count']}")
    print(f"  - Success rate: {backend_stats['success_rate']:.1f}%")
    print(f"  - Avg duration: {backend_stats['avg_duration_ms']:.0f}ms")
    print(f"  - Total tokens: {backend_stats['total_tokens']:,}")

    all_stats = collector.get_task_stats()
    print(f"\nOverall:")
    print(f"  - Tasks: {all_stats['count']}")
    print(f"  - Success rate: {all_stats['success_rate']:.1f}%")
    print(f"  - Avg duration: {all_stats['avg_duration_ms']:.0f}ms")


def demo_async_collection():
    """Demo 2: Async metrics collection with performance tracking"""
    print("\n\n=== Demo 2: Async Metrics Collection ===\n")

    # Initialize with async mode
    collector = MetricsCollector(async_mode=True)
    print("✓ MetricsCollector initialized (async mode)")

    # Record metrics rapidly
    print("\nRecording 100 metrics asynchronously...")
    start_time = time.perf_counter()

    for i in range(100):
        collector.record_task_metric(
            task_id=f"task-{i:03d}",
            agent_id=f"agent-{i % 5}",
            duration_ms=2000 + (i * 10),
            result=TaskResult.SUCCESS if i % 10 != 0 else TaskResult.FAILURE,
            tokens_used=15000 + (i * 100)
        )

    collection_time = (time.perf_counter() - start_time) * 1000
    print(f"✓ 100 metrics recorded in {collection_time:.2f}ms")

    # Check collection overhead
    overhead = collector.get_collection_overhead()
    print(f"\nCollection Performance:")
    print(f"  - Avg overhead: {overhead['avg_collection_time_ms']:.3f}ms")
    print(f"  - Max overhead: {overhead['max_collection_time_ms']:.3f}ms")
    print(f"  - Total collections: {overhead['total_collections']}")

    # Wait for async processing
    print("\nWaiting for async processing...")
    time.sleep(0.5)

    # Get statistics
    stats = collector.get_task_stats()
    print(f"\nStatistics:")
    print(f"  - Total tasks: {stats['count']}")
    print(f"  - Success rate: {stats['success_rate']:.1f}%")
    print(f"  - Avg duration: {stats['avg_duration_ms']:.0f}ms")

    # Cleanup
    collector.shutdown()
    print("✓ Collector shutdown")


def demo_agent_performance():
    """Demo 3: Agent performance tracking"""
    print("\n\n=== Demo 3: Agent Performance Tracking ===\n")

    collector = MetricsCollector(async_mode=False)
    print("✓ MetricsCollector initialized")

    # Simulate different agent performance
    agents = {
        "expert-backend": (10, 0.9, 3000),    # 10 tasks, 90% success, 3000ms avg
        "expert-frontend": (8, 0.875, 3500),  # 8 tasks, 87.5% success, 3500ms avg
        "manager-tdd": (15, 1.0, 2500),       # 15 tasks, 100% success, 2500ms avg
    }

    print("\nSimulating agent tasks...")
    for agent_id, (task_count, success_rate, avg_duration) in agents.items():
        for i in range(task_count):
            # Determine if this task succeeds
            is_success = i < int(task_count * success_rate)

            collector.record_task_metric(
                task_id=f"{agent_id}-task-{i:03d}",
                agent_id=agent_id,
                duration_ms=avg_duration + (i * 100) - 200,
                result=TaskResult.SUCCESS if is_success else TaskResult.FAILURE,
                tokens_used=20000 + (i * 500)
            )

        print(f"  ✓ {agent_id}: {task_count} tasks")

    # Get agent performance
    print("\n--- Agent Performance ---")
    for agent_id in agents.keys():
        perf = collector.get_agent_performance(agent_id)
        print(f"{agent_id}:")
        print(f"  - Tasks completed: {perf['tasks_completed']}")
        print(f"  - Success rate: {perf['success_rate']:.1f}%")
        print(f"  - Error rate: {perf['error_rate']:.1f}%")
        print(f"  - Avg duration: {perf['avg_duration_ms']:.0f}ms")
        print(f"  - Total tokens: {perf['total_tokens_used']:,}")


def demo_swarm_health():
    """Demo 4: Swarm health monitoring"""
    print("\n\n=== Demo 4: Swarm Health Monitoring ===\n")

    collector = MetricsCollector(async_mode=False)
    print("✓ MetricsCollector initialized")

    swarm_id = "swarm-001"

    # Record swarm health metrics over time
    print("\nRecording swarm health metrics...")
    health_values = [0.95, 0.93, 0.97, 0.98, 0.96]
    throughput_values = [150, 165, 155, 170, 160]
    latency_values = [45, 42, 48, 40, 43]

    for i, (health, throughput, latency) in enumerate(zip(health_values, throughput_values, latency_values)):
        collector.record_swarm_metric(
            swarm_id=swarm_id,
            metric_type="topology_health",
            value=health
        )

        collector.record_swarm_metric(
            swarm_id=swarm_id,
            metric_type="message_throughput",
            value=throughput
        )

        collector.record_swarm_metric(
            swarm_id=swarm_id,
            metric_type="consensus_latency",
            value=latency
        )

        print(f"  ✓ Snapshot {i+1}: health={health:.2f}, throughput={throughput}, latency={latency}ms")

    # Get swarm health
    print("\n--- Swarm Health Status ---")
    health = collector.get_swarm_health(swarm_id)
    print(f"Swarm: {health['swarm_id']}")
    print(f"  - Topology health: {health['topology_health']:.2f}")
    print(f"  - Message throughput: {health['message_throughput']:.0f} msg/s")
    print(f"  - Consensus latency: {health['consensus_latency_ms']:.0f}ms")
    print(f"  - Last updated: {health['last_updated']}")

    # Get with history
    health_with_history = collector.get_swarm_health(swarm_id, include_history=True)
    print(f"\n  - Historical snapshots: {len(health_with_history['history'])}")


def demo_swarm_coordinator_integration():
    """Demo 5: Integration with SwarmCoordinator"""
    print("\n\n=== Demo 5: SwarmCoordinator Integration ===\n")

    # Initialize coordinator
    coordinator = SwarmCoordinator(topology_type="mesh")
    print("✓ SwarmCoordinator initialized (mesh topology)")

    # Initialize metrics collector
    collector = MetricsCollector(async_mode=False)
    print("✓ MetricsCollector initialized")

    # Register agents
    agents = [
        ("agent-001", "expert-backend"),
        ("agent-002", "expert-frontend"),
        ("agent-003", "manager-tdd"),
    ]

    print("\nRegistering agents...")
    for agent_id, agent_type in agents:
        coordinator.register_agent(
            agent_id=agent_id,
            agent_metadata={"type": agent_type}
        )
        print(f"  ✓ {agent_id} ({agent_type})")

    # Simulate task execution with metrics
    print("\nSimulating task execution with metrics...")
    for i, (agent_id, agent_type) in enumerate(agents):
        # Simulate task execution
        start_time = time.perf_counter()

        # Update agent state
        coordinator.set_agent_state(agent_id, AgentState.BUSY)

        # Simulate work
        time.sleep(0.01)

        # Calculate duration
        duration_ms = (time.perf_counter() - start_time) * 1000

        # Update agent state
        coordinator.set_agent_state(agent_id, AgentState.ACTIVE)

        # Record metric
        collector.record_task_metric(
            task_id=f"integrated-task-{i:03d}",
            agent_id=agent_id,
            duration_ms=duration_ms,
            result=TaskResult.SUCCESS,
            tokens_used=15000 + (i * 1000),
            files_changed=i + 1
        )

        print(f"  ✓ Task {i+1}: {agent_id} completed in {duration_ms:.2f}ms")

    # Get topology info
    print("\n--- Topology Info ---")
    topo_info = coordinator.get_topology_info()
    print(f"Type: {topo_info['type']}")
    print(f"Agents: {topo_info['agent_count']}")
    print(f"Health: {topo_info['health']}")
    print(f"Active agents: {topo_info['active_agents']}")

    # Get metrics stats
    print("\n--- Metrics Stats ---")
    stats = collector.get_task_stats()
    print(f"Tasks completed: {stats['count']}")
    print(f"Success rate: {stats['success_rate']:.1f}%")
    print(f"Avg duration: {stats['avg_duration_ms']:.2f}ms")
    print(f"Total tokens: {stats['total_tokens']:,}")
    print(f"Total files changed: {stats['total_files_changed']}")


def main():
    """Run all demos"""
    print("=" * 70)
    print("MetricsCollector Integration Demo for MoAI-Flow Phase 6A")
    print("=" * 70)

    try:
        demo_basic_metrics_collection()
        demo_async_collection()
        demo_agent_performance()
        demo_swarm_health()
        demo_swarm_coordinator_integration()

        print("\n" + "=" * 70)
        print("✅ All demos completed successfully!")
        print("=" * 70)

    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
