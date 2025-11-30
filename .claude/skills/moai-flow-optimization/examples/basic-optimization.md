# Basic Optimization - Getting Started Guide

Step-by-step guide to implementing basic performance optimization for multi-agent AI systems.

## Prerequisites

**Required Components**:
```python
from moai_flow.optimization import (
    BottleneckDetector,
    PatternLearner,
    SelfHealer,
)
from moai_flow.core.interfaces import ICoordinator, IResourceController
from moai_flow.monitoring.metrics_storage import MetricsStorage
```

**System Requirements**:
- Active SwarmCoordinator instance
- MetricsStorage for performance data
- ResourceController for quota/budget management

## Step 1: Initialize Bottleneck Detector

**Purpose**: Real-time performance bottleneck detection.

```python
# Initialize metrics storage
metrics_storage = MetricsStorage()

# Initialize resource controller (from your system)
resource_controller = get_resource_controller()

# Create bottleneck detector
detector = BottleneckDetector(
    metrics_storage=metrics_storage,
    resource_controller=resource_controller,
    detection_window_ms=60000  # 1-minute analysis window
)

print("✓ Bottleneck detector initialized")
```

**What it does**:
- Monitors token usage (>80% threshold)
- Tracks agent quotas (90% capacity)
- Identifies slow agents (>2x average)
- Detects queue backlogs (>50 tasks)

## Step 2: Detect Current Bottlenecks

**Purpose**: Identify immediate performance issues.

```python
# Run detection
bottlenecks = detector.detect_bottlenecks()

# Display results
if bottlenecks:
    print(f"\n⚠️  Found {len(bottlenecks)} bottleneck(s):")

    for bottleneck in bottlenecks:
        print(f"\nType: {bottleneck.bottleneck_type}")
        print(f"Severity: {bottleneck.severity}")
        print(f"Affected: {bottleneck.affected_resources}")

        print(f"\nRecommendations:")
        for rec in bottleneck.recommendations:
            print(f"  • {rec}")
else:
    print("\n✓ No bottlenecks detected - system healthy")
```

**Expected Output**:
```
⚠️  Found 2 bottleneck(s):

Type: token_exhaustion
Severity: high
Affected: ['global']

Recommendations:
  • Increase token budget in .moai/config/config.json
  • Optimize prompts to reduce token usage
  • Implement token-aware task prioritization

Type: task_queue_backlog
Severity: medium
Affected: ['task_queue']

Recommendations:
  • Increase agent quota to process queue faster
  • Prioritize critical tasks
```

## Step 3: Generate Performance Report

**Purpose**: Comprehensive performance analysis over time.

```python
# Generate 5-minute performance report
report = detector.analyze_performance(time_range_ms=300000)

print(f"\n📊 Performance Report (Last 5 minutes)")
print(f"=" * 60)

# Metrics summary
metrics = report.metrics_summary
print(f"\nTask Metrics:")
print(f"  Tasks Analyzed: {metrics['task_count']}")
print(f"  Avg Duration: {metrics['avg_duration_ms']:.0f}ms")
print(f"  P95 Duration: {metrics['p95_duration_ms']:.0f}ms")
print(f"  P99 Duration: {metrics['p99_duration_ms']:.0f}ms")
print(f"  Success Rate: {metrics['success_rate']:.1%}")

# Trends
print(f"\nTrends:")
for metric_name, trend in report.trends.items():
    icon = "📈" if trend == "improving" else "📉" if trend == "degrading" else "➡️"
    print(f"  {icon} {metric_name}: {trend}")

# Bottlenecks
print(f"\nBottlenecks Detected: {len(report.bottlenecks_detected)}")
for bottleneck in report.bottlenecks_detected:
    print(f"  • {bottleneck.bottleneck_type} ({bottleneck.severity})")
```

**Expected Output**:
```
📊 Performance Report (Last 5 minutes)
============================================================

Task Metrics:
  Tasks Analyzed: 1,234
  Avg Duration: 2,500ms
  P95 Duration: 5,000ms
  P99 Duration: 8,000ms
  Success Rate: 95.2%

Trends:
  📈 task_duration: improving
  ➡️  token_usage: stable
  📈 success_rate: improving

Bottlenecks Detected: 2
  • token_exhaustion (high)
  • task_queue_backlog (medium)
```

## Step 4: Initialize Self-Healing

**Purpose**: Automatic failure recovery.

```python
from moai_flow.optimization import SelfHealer

# Get coordinator instance
coordinator = get_coordinator()

# Create self-healer
healer = SelfHealer(
    coordinator=coordinator,
    auto_heal=True  # Enable automatic healing
)

print("\n✓ Self-healing initialized with 4 built-in strategies:")
print("  • AgentRestartStrategy (agent failures)")
print("  • TaskRetryStrategy (task timeouts)")
print("  • ResourceRebalanceStrategy (resource exhaustion)")
print("  • QuorumRecoveryStrategy (consensus failures)")
```

## Step 5: Simulate and Handle Failures

**Purpose**: Test automatic failure recovery.

```python
# Simulate agent failure
failure_event = {
    "type": "heartbeat_failed",
    "agent_id": "agent-001",
    "timestamp": datetime.now(timezone.utc).isoformat()
}

# Detect failure
failure = healer.detect_failure(failure_event)

if failure:
    print(f"\n⚠️  Failure detected: {failure.failure_type}")
    print(f"Agent: {failure.agent_id}")
    print(f"Severity: {failure.severity}")

    # Automatically heal
    result = healer.heal(failure)

    if result.success:
        print(f"\n✅ Healing successful!")
        print(f"Strategy: {result.strategy_used}")
        print(f"Duration: {result.duration_ms}ms")
        print(f"\nActions taken:")
        for action in result.actions_taken:
            print(f"  • {action}")
    else:
        print(f"\n❌ Healing failed")
        print(f"Reason: {result.metadata.get('error', 'Unknown')}")
```

**Expected Output**:
```
⚠️  Failure detected: agent_down
Agent: agent-001
Severity: high

✅ Healing successful!
Strategy: AgentRestartStrategy
Duration: 250ms

Actions taken:
  • Saved metadata for agent-001
  • Unregistered agent-001
  • Re-registered agent-001
```

## Step 6: Monitor Healing Effectiveness

**Purpose**: Track healing success rate and performance.

```python
# Get healing statistics
stats = healer.get_healing_stats()

print(f"\n📈 Healing Statistics")
print(f"=" * 60)
print(f"Total Failures: {stats['total_failures_detected']}")
print(f"Total Healings: {stats['total_healing_attempts']}")
print(f"Success Rate: {stats['success_rate']:.1%}")
print(f"Avg Healing Time: {stats['average_healing_time_ms']:.0f}ms")

print(f"\nSuccess Rate by Type:")
for failure_type, rate in stats['success_rate_by_type'].items():
    print(f"  {failure_type}: {rate:.1%}")
```

**Expected Output**:
```
📈 Healing Statistics
============================================================
Total Failures: 100
Total Healings: 95
Success Rate: 90.5%
Avg Healing Time: 250ms

Success Rate by Type:
  agent_down: 95.0%
  task_timeout: 88.0%
  resource_exhaustion: 85.0%
```

## Step 7: Initialize Pattern Learning

**Purpose**: Learn from system behavior to predict issues.

```python
from moai_flow.optimization import PatternLearner

# Create pattern learner
learner = PatternLearner(
    min_occurrences=5,         # Min pattern occurrences
    confidence_threshold=0.7,  # Min confidence (70%)
    max_history_size=10000     # Max events stored
)

print("\n✓ Pattern learner initialized")

# Record events
events = [
    {
        "type": "task_complete",
        "timestamp": datetime.now(timezone.utc),
        "agent_id": "agent-001",
        "duration_ms": 2500,
        "result": "success"
    },
    {
        "type": "heartbeat",
        "timestamp": datetime.now(timezone.utc),
        "agent_id": "agent-001"
    },
    # ... more events
]

for event in events:
    learner.record_event(event)

print(f"✓ Recorded {len(events)} events")
```

## Step 8: Learn and Display Patterns

**Purpose**: Identify recurring behavioral patterns.

```python
# Learn patterns from recorded events
patterns = learner.learn_patterns()

print(f"\n🔍 Learned Patterns: {len(patterns)}")
print(f"=" * 60)

for i, pattern in enumerate(patterns, 1):
    print(f"\nPattern {i}:")
    print(f"  Type: {pattern.pattern_type}")
    print(f"  Confidence: {pattern.confidence:.2f}")
    print(f"  Occurrences: {pattern.occurrences}")
    print(f"  Description: {pattern.description}")

    # Display pattern events
    print(f"  Events:")
    for event in pattern.events[:3]:  # First 3 events
        print(f"    • {event.get('type', 'unknown')}")
```

**Expected Output**:
```
🔍 Learned Patterns: 3
============================================================

Pattern 1:
  Type: sequence
  Confidence: 0.85
  Occurrences: 15
  Description: Task start → Agent assigned → Task complete
  Events:
    • task_start
    • agent_assigned
    • task_complete

Pattern 2:
  Type: frequency
  Confidence: 0.92
  Occurrences: 120
  Description: Heartbeat every 5.0s (±0.2s)
  Events:
    • heartbeat

Pattern 3:
  Type: correlation
  Confidence: 0.78
  Occurrences: 8
  Description: High token usage → Task failure (75% correlation)
  Events:
    • high_token_usage
    • task_failed
```

## Step 9: Continuous Monitoring Setup

**Purpose**: Background monitoring for proactive optimization.

```python
import threading
import time

def continuous_monitoring(interval_seconds=30):
    """Run continuous bottleneck detection"""
    while True:
        try:
            # Detect bottlenecks
            bottlenecks = detector.detect_bottlenecks()

            if bottlenecks:
                print(f"\n[{datetime.now().strftime('%H:%M:%S')}] "
                      f"⚠️  {len(bottlenecks)} bottleneck(s) detected")

                for bottleneck in bottlenecks:
                    print(f"  • {bottleneck.bottleneck_type} ({bottleneck.severity})")

        except Exception as e:
            print(f"Monitoring error: {e}")

        time.sleep(interval_seconds)

# Start monitoring in background thread
monitor_thread = threading.Thread(
    target=continuous_monitoring,
    args=(30,),  # 30-second interval
    daemon=True
)
monitor_thread.start()

print("\n✓ Continuous monitoring started (30s interval)")
```

## Complete Basic Example

**Full integration script**:

```python
#!/usr/bin/env python3
"""Basic MoAI Flow Optimization Example"""

from datetime import datetime, timezone
from moai_flow.optimization import (
    BottleneckDetector,
    PatternLearner,
    SelfHealer,
)

def main():
    # 1. Initialize components
    print("Initializing MoAI Flow Optimization...")

    detector = BottleneckDetector(
        metrics_storage=metrics_storage,
        resource_controller=resource_controller,
        detection_window_ms=60000
    )

    healer = SelfHealer(
        coordinator=coordinator,
        auto_heal=True
    )

    learner = PatternLearner(
        min_occurrences=5,
        confidence_threshold=0.7
    )

    print("✓ All components initialized\n")

    # 2. Detect bottlenecks
    print("Analyzing system performance...")
    bottlenecks = detector.detect_bottlenecks()

    if bottlenecks:
        print(f"⚠️  Found {len(bottlenecks)} bottleneck(s)")
        for b in bottlenecks:
            print(f"  • {b.bottleneck_type} ({b.severity})")
    else:
        print("✓ No bottlenecks - system healthy")

    # 3. Generate report
    print("\nGenerating performance report...")
    report = detector.analyze_performance(time_range_ms=300000)

    print(f"Tasks: {report.metrics_summary['task_count']}")
    print(f"Success Rate: {report.metrics_summary['success_rate']:.1%}")
    print(f"Avg Duration: {report.metrics_summary['avg_duration_ms']:.0f}ms")

    # 4. Get healing stats
    print("\nHealing statistics...")
    stats = healer.get_healing_stats()

    print(f"Success Rate: {stats['success_rate']:.1%}")
    print(f"Avg Time: {stats['average_healing_time_ms']:.0f}ms")

    # 5. Learn patterns
    print("\nLearning patterns...")
    patterns = learner.learn_patterns()

    print(f"Patterns learned: {len(patterns)}")

    print("\n✓ Basic optimization complete!")

if __name__ == "__main__":
    main()
```

## Next Steps

**Advanced Topics**:
1. [Performance Tuning](performance-tuning.md) - Advanced optimization strategies
2. [Advanced Healing](advanced-healing.md) - Custom strategies and analytics
3. [Resource Allocation](../modules/resource-allocation.md) - Dynamic scaling

**Best Practices**:
- Run detection every 30-60 seconds
- Monitor healing success rate (target: >85%)
- Review patterns weekly
- Act on high/critical severity bottlenecks immediately
- Track trends to detect degradation early

## Common Issues

**Issue**: No bottlenecks detected but system slow
**Solution**: Check detection window (may be too short), verify metrics are being recorded

**Issue**: Healing success rate < 70%
**Solution**: Review healing strategies, check for recurring failure types, consider custom strategies

**Issue**: Too many patterns learned
**Solution**: Increase min_occurrences threshold, raise confidence_threshold

**Issue**: High false positive rate in predictions
**Solution**: Increase confidence_threshold to 0.8, review pattern quality

## Resources

- [Bottleneck Detection Module](../modules/bottleneck-detection.md)
- [Self-Healing Documentation](../SKILL.md#3-self-healing---automatic-failure-recovery)
- [Pattern Learning Guide](../modules/performance-monitoring.md#1-pattern-learner)
