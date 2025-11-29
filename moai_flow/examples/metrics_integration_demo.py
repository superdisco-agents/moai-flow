#!/usr/bin/env python3
"""
Phase 6A Observability Integration Demo

Demonstrates comprehensive integration between:
- SwarmDB (extended schema with metrics tables)
- MetricsStorage (dedicated metrics persistence)

This example shows:
1. Task metrics tracking (duration, result, tokens, files)
2. Agent metrics tracking (success rates, error counts)
3. Swarm metrics tracking (health, throughput, latency)
4. Time-series queries and aggregations
5. Automatic retention management

Use Case: Multi-agent system monitoring with SQLite-backed persistence
"""

import sys
import time
import uuid
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from memory.swarm_db import SwarmDB
from monitoring.metrics_storage import (
    MetricsStorage,
    MetricType,
    AggregationType,
    TaskResult,
)


def demo_basic_integration():
    """Demo 1: Basic integration between SwarmDB and MetricsStorage"""
    print("=" * 70)
    print("Demo 1: Basic Integration")
    print("=" * 70)

    # Initialize both systems
    swarm_db = SwarmDB()
    metrics_storage = MetricsStorage()
    print("✓ SwarmDB and MetricsStorage initialized\n")

    # Simulate agent lifecycle
    agent_id = str(uuid.uuid4())
    task_id = str(uuid.uuid4())

    # 1. Agent spawns (SwarmDB)
    swarm_db.insert_event({
        "event_type": "spawn",
        "agent_id": agent_id,
        "agent_type": "expert-backend",
        "timestamp": datetime.now().isoformat(),
        "metadata": {"prompt": "Implement REST API"}
    })
    swarm_db.register_agent(
        agent_id=agent_id,
        agent_type="expert-backend",
        status="spawned"
    )
    print(f"✓ Agent spawned: {agent_id}")

    # 2. Agent completes task (both systems)
    time.sleep(0.1)  # Simulate work
    duration_ms = 1500

    # Update SwarmDB
    swarm_db.update_agent_status(agent_id, "complete", duration_ms=duration_ms)
    swarm_db.insert_event({
        "event_type": "complete",
        "agent_id": agent_id,
        "agent_type": "expert-backend",
        "timestamp": datetime.now().isoformat(),
        "metadata": {"result": "success"}
    })

    # Store metrics
    metrics_storage.store_task_metric(
        task_id=task_id,
        agent_id=agent_id,
        duration_ms=duration_ms,
        result=TaskResult.SUCCESS,
        tokens_used=500,
        files_changed=3
    )
    print(f"✓ Task completed: {task_id} (1500ms, 500 tokens, 3 files)")

    # 3. Query both systems
    agent = swarm_db.get_agent(agent_id)
    print(f"\nSwarmDB agent data:")
    print(f"  - Status: {agent['status']}")
    print(f"  - Duration: {agent['duration_ms']}ms")

    task_metrics = metrics_storage.get_task_metrics(agent_id=agent_id)
    print(f"\nMetricsStorage task data:")
    print(f"  - Tasks: {len(task_metrics)}")
    print(f"  - Result: {task_metrics[0]['result']}")
    print(f"  - Tokens: {task_metrics[0]['tokens_used']}")

    swarm_db.close()
    metrics_storage.close()


def demo_multi_agent_monitoring():
    """Demo 2: Multi-agent system monitoring"""
    print("\n" + "=" * 70)
    print("Demo 2: Multi-Agent System Monitoring")
    print("=" * 70)

    metrics_storage = MetricsStorage()
    swarm_id = "swarm_production_001"

    # Simulate 10 agents with varying performance
    agents = []
    for i in range(10):
        agent_id = f"agent_{i:03d}"
        agents.append(agent_id)

        # Task metrics (varying success rates)
        for task_num in range(5):
            success = i % 3 != 0  # 66% success rate
            result = TaskResult.SUCCESS if success else TaskResult.FAILURE
            duration = 1000 + (i * 100) + (task_num * 50)

            metrics_storage.store_task_metric(
                task_id=f"task_{i}_{task_num}",
                agent_id=agent_id,
                duration_ms=duration,
                result=result,
                tokens_used=500 + (task_num * 100),
                files_changed=1 + task_num
            )

    print(f"✓ Simulated 10 agents with 5 tasks each (50 total tasks)\n")

    # Agent-level metrics
    for agent_id in agents:
        # Calculate success rate for this agent
        agent_tasks = metrics_storage.get_task_metrics(agent_id=agent_id)
        success_count = sum(1 for t in agent_tasks if t['result'] == 'success')
        success_rate = success_count / len(agent_tasks) if agent_tasks else 0

        metrics_storage.store_agent_metric(
            agent_id=agent_id,
            metric_type=MetricType.AGENT_SUCCESS_RATE,
            value=success_rate,
            metadata={"total_tasks": len(agent_tasks), "successful": success_count}
        )

    print("✓ Stored agent-level success rate metrics\n")

    # Swarm-level metrics
    all_tasks = metrics_storage.get_task_metrics(limit=1000)
    swarm_success_rate = sum(1 for t in all_tasks if t['result'] == 'success') / len(all_tasks)
    swarm_avg_duration = sum(t['duration_ms'] for t in all_tasks) / len(all_tasks)

    metrics_storage.store_swarm_metric(
        swarm_id=swarm_id,
        metric_type=MetricType.SWARM_HEALTH,
        value=swarm_success_rate,
        metadata={
            "total_agents": len(agents),
            "total_tasks": len(all_tasks),
            "avg_duration_ms": swarm_avg_duration
        }
    )

    metrics_storage.store_swarm_metric(
        swarm_id=swarm_id,
        metric_type=MetricType.SWARM_THROUGHPUT,
        value=len(all_tasks) / 60.0,  # tasks per second (simulated)
        metadata={"time_window_seconds": 60}
    )

    print("✓ Stored swarm-level health and throughput metrics\n")

    # Query and analyze
    print("Analysis Results:")
    print("-" * 70)

    # Swarm health
    swarm_metrics = metrics_storage.get_swarm_metrics(swarm_id=swarm_id)
    for metric in swarm_metrics:
        print(f"  {metric['metric_type']}: {metric['value']:.2f}")
        print(f"    Metadata: {metric['metadata']}")

    metrics_storage.close()


def demo_time_series_analysis():
    """Demo 3: Time-series analysis and aggregations"""
    print("\n" + "=" * 70)
    print("Demo 3: Time-Series Analysis and Aggregations")
    print("=" * 70)

    metrics_storage = MetricsStorage()
    agent_id = "agent_timeseries_001"

    # Generate time-series data (last 24 hours)
    now = datetime.now()
    for hour in range(24):
        timestamp = now - timedelta(hours=23 - hour)

        # Generate metrics for this hour (varying patterns)
        for task_num in range(10):
            duration = 1000 + (hour * 50) + (task_num * 100)  # Increasing over time
            result = TaskResult.SUCCESS if task_num % 4 != 0 else TaskResult.FAILURE

            metrics_storage.store_task_metric(
                task_id=f"task_ts_{hour}_{task_num}",
                agent_id=agent_id,
                duration_ms=duration,
                result=result,
                tokens_used=400 + (task_num * 50),
                files_changed=task_num % 5,
                timestamp=timestamp
            )

    print(f"✓ Generated 24 hours of time-series data (240 tasks)\n")

    # Aggregation analysis
    print("Aggregation Analysis:")
    print("-" * 70)

    # Last 24 hours
    time_range = (now - timedelta(hours=24), now)

    # Average duration
    avg_result = metrics_storage.aggregate_metrics(
        metric_type="task",
        aggregation=AggregationType.AVG,
        time_range=time_range,
        filters={"agent_id": agent_id}
    )
    print(f"  Average task duration: {avg_result['result']:.2f}ms")
    print(f"  Sample count: {avg_result['count']}")

    # Total tasks
    count_result = metrics_storage.aggregate_metrics(
        metric_type="task",
        aggregation=AggregationType.COUNT,
        time_range=time_range,
        filters={"agent_id": agent_id}
    )
    print(f"  Total tasks: {count_result['count']}")

    # Min/Max duration
    min_result = metrics_storage.aggregate_metrics(
        metric_type="task",
        aggregation=AggregationType.MIN,
        time_range=time_range,
        filters={"agent_id": agent_id}
    )
    max_result = metrics_storage.aggregate_metrics(
        metric_type="task",
        aggregation=AggregationType.MAX,
        time_range=time_range,
        filters={"agent_id": agent_id}
    )
    print(f"  Min duration: {min_result['result']:.2f}ms")
    print(f"  Max duration: {max_result['result']:.2f}ms")

    # Standard deviation
    stddev_result = metrics_storage.aggregate_metrics(
        metric_type="task",
        aggregation=AggregationType.STDDEV,
        time_range=time_range,
        filters={"agent_id": agent_id}
    )
    print(f"  Standard deviation: {stddev_result['stddev']:.2f}ms")

    # Success rate analysis
    print("\nSuccess Rate Analysis:")
    print("-" * 70)

    success_count = metrics_storage.aggregate_metrics(
        metric_type="task",
        aggregation=AggregationType.COUNT,
        time_range=time_range,
        filters={"agent_id": agent_id, "result": "success"}
    )

    total_count = metrics_storage.aggregate_metrics(
        metric_type="task",
        aggregation=AggregationType.COUNT,
        time_range=time_range,
        filters={"agent_id": agent_id}
    )

    success_rate = success_count['count'] / total_count['count'] * 100
    print(f"  Success rate: {success_rate:.1f}%")
    print(f"  Successful: {success_count['count']} / {total_count['count']}")

    metrics_storage.close()


def demo_retention_cleanup():
    """Demo 4: Automatic retention management"""
    print("\n" + "=" * 70)
    print("Demo 4: Automatic Retention Management")
    print("=" * 70)

    metrics_storage = MetricsStorage()

    # Generate old metrics (45 days ago)
    old_timestamp = datetime.now() - timedelta(days=45)

    for i in range(50):
        metrics_storage.store_task_metric(
            task_id=f"old_task_{i}",
            agent_id="agent_old_001",
            duration_ms=1000 + i * 100,
            result=TaskResult.SUCCESS,
            timestamp=old_timestamp
        )

    print(f"✓ Generated 50 old metrics (45 days ago)\n")

    # Generate recent metrics (5 days ago)
    recent_timestamp = datetime.now() - timedelta(days=5)

    for i in range(30):
        metrics_storage.store_task_metric(
            task_id=f"recent_task_{i}",
            agent_id="agent_recent_001",
            duration_ms=1200 + i * 50,
            result=TaskResult.SUCCESS,
            timestamp=recent_timestamp
        )

    print(f"✓ Generated 30 recent metrics (5 days ago)\n")

    # Query before cleanup
    all_metrics = metrics_storage.get_task_metrics(limit=10000)
    print(f"Total metrics before cleanup: {len(all_metrics)}")

    # Cleanup (30-day retention)
    print("\nRunning cleanup (30-day retention)...")
    deleted = metrics_storage.cleanup_old_metrics(retention_days=30)

    print(f"✓ Cleanup complete:")
    print(f"  - Task metrics deleted: {deleted['task_metrics']}")
    print(f"  - Agent metrics deleted: {deleted['agent_metrics']}")
    print(f"  - Swarm metrics deleted: {deleted['swarm_metrics']}")
    print(f"  - Total deleted: {sum(deleted.values())}")

    # Query after cleanup
    all_metrics_after = metrics_storage.get_task_metrics(limit=10000)
    print(f"\nTotal metrics after cleanup: {len(all_metrics_after)}")

    # Vacuum database
    print("\nOptimizing database...")
    metrics_storage.vacuum()
    print("✓ Database optimized")

    metrics_storage.close()


def main():
    """Run all demos"""
    print("\n" + "=" * 70)
    print("Phase 6A Observability Integration Demo")
    print("=" * 70)
    print("\nThis demo shows comprehensive metrics tracking and analysis")
    print("for multi-agent systems using SQLite-backed persistence.\n")

    try:
        demo_basic_integration()
        demo_multi_agent_monitoring()
        demo_time_series_analysis()
        demo_retention_cleanup()

        print("\n" + "=" * 70)
        print("✅ All demos completed successfully!")
        print("=" * 70)
        print("\nDatabase Locations:")
        print(f"  - SwarmDB: {Path.cwd() / '.moai' / 'memory' / 'swarm.db'}")
        print(f"  - MetricsStorage: {Path.cwd() / '.swarm' / 'metrics.db'}")
        print("\nNext Steps:")
        print("  1. Integrate with SwarmCoordinator for automatic metrics collection")
        print("  2. Add real-time monitoring dashboards")
        print("  3. Set up alerting for performance degradation")
        print("  4. Implement automated performance optimization")
        print()

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
