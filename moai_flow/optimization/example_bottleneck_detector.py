#!/usr/bin/env python3
"""
Example usage of BottleneckDetector for Phase 6C adaptive optimization.

Demonstrates:
- Bottleneck detection across 5 types
- Performance analysis and reporting
- Trend analysis
- Recommendation generation
- Real-time monitoring
"""

import logging
import time
from datetime import datetime, timedelta
from pathlib import Path

from moai_flow.monitoring.metrics_storage import MetricsStorage, TaskResult
from moai_flow.resource.resource_controller import ResourceController
from moai_flow.optimization.bottleneck_detector import BottleneckDetector


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def example_1_basic_detection():
    """Example 1: Basic bottleneck detection"""
    print("\n" + "=" * 60)
    print("Example 1: Basic Bottleneck Detection")
    print("=" * 60)

    # Initialize components
    metrics = MetricsStorage(db_path=Path(".swarm/example_metrics.db"))
    resources = ResourceController(total_token_budget=100000)

    # Create detector
    detector = BottleneckDetector(
        metrics_storage=metrics,
        resource_controller=resources,
        detection_window_ms=60000  # 60 seconds
    )

    # Simulate some metrics
    print("\n📊 Simulating task metrics...")
    for i in range(20):
        metrics.store_task_metric(
            task_id=f"task_{i:03d}",
            agent_id=f"agent_{i % 5:03d}",
            duration_ms=1000 + (i * 100),
            result=TaskResult.SUCCESS if i % 10 != 0 else TaskResult.FAILURE,
            tokens_used=500 + (i * 50),
            files_changed=i % 3
        )

    # Simulate high token consumption
    resources.allocate_tokens("swarm_001", 100000)
    resources.consume_tokens("swarm_001", 85000)  # 85% usage

    # Detect bottlenecks
    print("\n🔍 Detecting bottlenecks...")
    bottlenecks = detector.detect_bottlenecks()

    print(f"\n✅ Found {len(bottlenecks)} bottleneck(s):")
    for bottleneck in bottlenecks:
        print(f"\n  Type: {bottleneck.bottleneck_type}")
        print(f"  Severity: {bottleneck.severity}")
        print(f"  Affected Resources: {bottleneck.affected_resources}")
        print(f"  Metrics: {bottleneck.metrics}")
        print(f"  Recommendations:")
        for rec in bottleneck.recommendations:
            print(f"    - {rec}")

    # Cleanup
    metrics.close()


def example_2_performance_analysis():
    """Example 2: Comprehensive performance analysis"""
    print("\n" + "=" * 60)
    print("Example 2: Performance Analysis & Trend Detection")
    print("=" * 60)

    # Initialize components
    metrics = MetricsStorage(db_path=Path(".swarm/example_metrics.db"))
    resources = ResourceController(total_token_budget=200000)

    # Create detector
    detector = BottleneckDetector(
        metrics_storage=metrics,
        resource_controller=resources
    )

    # Simulate metrics over time with improving trend
    print("\n📊 Simulating task metrics over 5 minutes...")
    base_time = datetime.now() - timedelta(minutes=5)

    for i in range(50):
        # Create improving trend (decreasing duration, increasing success rate)
        duration_ms = 2000 - (i * 20)  # Getting faster
        result = TaskResult.SUCCESS if i % 20 != 0 else TaskResult.FAILURE  # Improving success rate

        metrics.store_task_metric(
            task_id=f"task_{i:03d}",
            agent_id=f"agent_{i % 3:03d}",
            duration_ms=max(duration_ms, 500),
            result=result,
            tokens_used=400 + (i % 10) * 20,
            files_changed=i % 4,
            timestamp=base_time + timedelta(seconds=i*6)
        )

    # Analyze performance
    print("\n📈 Analyzing performance over 5 minutes...")
    report = detector.analyze_performance(time_range_ms=300000)

    print(f"\n✅ Performance Report ID: {report.report_id}")
    print(f"   Time Range: {report.time_range_ms}ms ({report.time_range_ms/1000/60:.1f} minutes)")
    print(f"   Generated: {report.generated_at}")

    print("\n📊 Metrics Summary:")
    for key, value in report.metrics_summary.items():
        if isinstance(value, float):
            print(f"   {key}: {value:.2f}")
        else:
            print(f"   {key}: {value}")

    print("\n📈 Trends:")
    for metric, trend in report.trends.items():
        emoji = "📈" if trend == "improving" else ("📉" if trend == "degrading" else "➡️")
        print(f"   {emoji} {metric}: {trend}")

    print(f"\n🚨 Bottlenecks Detected: {len(report.bottlenecks_detected)}")
    for bottleneck in report.bottlenecks_detected:
        print(f"   - {bottleneck.bottleneck_type} ({bottleneck.severity})")

    # Cleanup
    metrics.close()


def example_3_slow_agent_detection():
    """Example 3: Slow agent detection"""
    print("\n" + "=" * 60)
    print("Example 3: Slow Agent Detection")
    print("=" * 60)

    # Initialize components
    metrics = MetricsStorage(db_path=Path(".swarm/example_metrics.db"))
    resources = ResourceController(total_token_budget=200000)

    # Create detector
    detector = BottleneckDetector(
        metrics_storage=metrics,
        resource_controller=resources
    )

    # Simulate normal and slow agents
    print("\n📊 Simulating agent performance...")
    print("   - agent_001: Normal (avg 1000ms)")
    print("   - agent_002: Normal (avg 1200ms)")
    print("   - agent_003: SLOW (avg 3000ms)")

    for i in range(30):
        if i % 3 == 0:
            # agent_001: Normal
            metrics.store_task_metric(
                task_id=f"task_{i:03d}",
                agent_id="agent_001",
                duration_ms=1000 + (i % 10) * 20,
                result=TaskResult.SUCCESS,
                tokens_used=500
            )
        elif i % 3 == 1:
            # agent_002: Normal
            metrics.store_task_metric(
                task_id=f"task_{i:03d}",
                agent_id="agent_002",
                duration_ms=1200 + (i % 10) * 15,
                result=TaskResult.SUCCESS,
                tokens_used=500
            )
        else:
            # agent_003: SLOW (>2x average)
            metrics.store_task_metric(
                task_id=f"task_{i:03d}",
                agent_id="agent_003",
                duration_ms=3000 + (i % 10) * 50,
                result=TaskResult.SUCCESS if i % 5 != 0 else TaskResult.FAILURE,
                tokens_used=500
            )

    # Detect bottlenecks
    print("\n🔍 Detecting slow agents...")
    bottlenecks = detector.detect_bottlenecks()

    # Find slow_agent bottleneck
    slow_agent_bottleneck = next(
        (b for b in bottlenecks if b.bottleneck_type == "slow_agent"),
        None
    )

    if slow_agent_bottleneck:
        print(f"\n✅ Slow agent bottleneck detected!")
        print(f"   Severity: {slow_agent_bottleneck.severity}")
        print(f"   Affected Agents: {slow_agent_bottleneck.affected_resources}")
        print(f"\n   Slow Agent Details:")
        for agent in slow_agent_bottleneck.metrics.get("slow_agents", []):
            print(f"     - {agent['agent_id']}: {agent['avg_duration_ms']:.0f}ms "
                  f"(success rate: {agent['success_rate']*100:.1f}%)")

        print(f"\n   Recommendations:")
        for rec in slow_agent_bottleneck.recommendations:
            print(f"     - {rec}")
    else:
        print("\n❌ No slow agent bottleneck detected")

    # Cleanup
    metrics.close()


def example_4_queue_backlog_detection():
    """Example 4: Queue backlog detection"""
    print("\n" + "=" * 60)
    print("Example 4: Task Queue Backlog Detection")
    print("=" * 60)

    # Initialize components
    metrics = MetricsStorage(db_path=Path(".swarm/example_metrics.db"))
    resources = ResourceController(total_token_budget=200000)

    # Create detector
    detector = BottleneckDetector(
        metrics_storage=metrics,
        resource_controller=resources
    )

    # Simulate large queue backlog
    print("\n📊 Simulating task queue backlog...")
    from moai_flow.core.interfaces import Priority

    for i in range(60):
        priority = Priority.CRITICAL if i < 10 else (
            Priority.HIGH if i < 30 else Priority.MEDIUM
        )
        resources.enqueue_task(
            task_id=f"queued_task_{i:03d}",
            priority=priority,
            task_data={"description": f"Task {i}"}
        )

    print(f"   Enqueued 60 tasks (10 CRITICAL, 20 HIGH, 30 MEDIUM)")

    # Detect bottlenecks
    print("\n🔍 Detecting queue backlog...")
    bottlenecks = detector.detect_bottlenecks()

    # Find queue_backlog bottleneck
    queue_bottleneck = next(
        (b for b in bottlenecks if b.bottleneck_type == "task_queue_backlog"),
        None
    )

    if queue_bottleneck:
        print(f"\n✅ Queue backlog bottleneck detected!")
        print(f"   Severity: {queue_bottleneck.severity}")
        metrics_data = queue_bottleneck.metrics
        print(f"   Pending Tasks: {metrics_data['pending_tasks']}")
        print(f"   High Priority Tasks: {metrics_data['high_priority_count']}")
        print(f"\n   Priority Distribution:")
        for priority, count in metrics_data['by_priority'].items():
            print(f"     {priority}: {count}")

        print(f"\n   Recommendations:")
        for rec in queue_bottleneck.recommendations:
            print(f"     - {rec}")
    else:
        print("\n❌ No queue backlog bottleneck detected")

    # Cleanup
    metrics.close()


def example_5_real_time_monitoring():
    """Example 5: Real-time continuous monitoring"""
    print("\n" + "=" * 60)
    print("Example 5: Real-Time Continuous Monitoring")
    print("=" * 60)

    # Initialize components
    metrics = MetricsStorage(db_path=Path(".swarm/example_metrics.db"))
    resources = ResourceController(total_token_budget=200000)

    # Create detector
    detector = BottleneckDetector(
        metrics_storage=metrics,
        resource_controller=resources,
        detection_window_ms=10000  # 10 seconds
    )

    # Start continuous monitoring
    print("\n🔄 Starting continuous monitoring (10-second intervals)...")
    print("   Monitoring for 30 seconds...")
    detector.monitor_continuously(interval_ms=10000)

    # Simulate ongoing activity
    for i in range(3):
        time.sleep(10)
        print(f"\n   [{i+1}/3] Simulating activity...")

        # Create some metrics
        metrics.store_task_metric(
            task_id=f"monitor_task_{i:03d}",
            agent_id="monitor_agent_001",
            duration_ms=1000 + (i * 500),
            result=TaskResult.SUCCESS,
            tokens_used=600
        )

        # Increase token consumption
        resources.consume_tokens("swarm_001", 5000)

    # Stop monitoring
    print("\n🛑 Stopping continuous monitoring...")
    detector.stop_monitoring()

    print("\n✅ Monitoring stopped")

    # Cleanup
    metrics.close()


if __name__ == "__main__":
    print("\n🚀 BottleneckDetector Examples - Phase 6C Adaptive Optimization")
    print("=" * 60)

    try:
        # Run all examples
        example_1_basic_detection()
        example_2_performance_analysis()
        example_3_slow_agent_detection()
        example_4_queue_backlog_detection()
        example_5_real_time_monitoring()

        print("\n" + "=" * 60)
        print("✅ All examples completed successfully!")
        print("=" * 60)

    except KeyboardInterrupt:
        print("\n\n⚠️  Examples interrupted by user")
    except Exception as e:
        logger.error(f"Example failed: {e}", exc_info=True)
        raise

    # Cleanup example database
    db_path = Path(".swarm/example_metrics.db")
    if db_path.exists():
        db_path.unlink()
        print(f"\n🧹 Cleaned up example database: {db_path}")
