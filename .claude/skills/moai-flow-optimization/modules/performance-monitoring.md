# Performance Monitoring Module

Real-time system analytics, pattern learning, and healing effectiveness tracking for multi-agent AI systems.

## Overview

Performance monitoring provides comprehensive insights into system behavior through:

1. **Pattern Learning** - Statistical analysis of event sequences
2. **Healing Analytics** - Self-healing effectiveness tracking
3. **Trend Analysis** - Performance degradation detection
4. **Metric Collection** - Real-time performance data

## Components

### 1. Pattern Learner

**Purpose**: Learn recurring patterns from event history without ML libraries.

**Pattern Types**:
- **Sequence patterns**: Repeated event sequences (n-gram analysis)
- **Frequency patterns**: Regular time-based occurrences
- **Correlation patterns**: Events that co-occur frequently
- **Temporal patterns**: Time-window based patterns

**Configuration**:
```python
from moai_flow.optimization import PatternLearner

learner = PatternLearner(
    min_occurrences=5,           # Min pattern occurrences to be valid
    confidence_threshold=0.7,    # Min confidence (0.0-1.0)
    max_history_size=10000       # Max events stored
)
```

**Event Recording**:
```python
# Record events for pattern learning
learner.record_event({
    "type": "task_complete",
    "timestamp": datetime.now(timezone.utc),
    "agent_id": "agent-001",
    "duration_ms": 2500,
    "result": "success",
    "metadata": {"tokens_used": 1500}
})
```

**Pattern Learning**:
```python
# Learn patterns from recorded events
patterns = learner.learn_patterns()

for pattern in patterns:
    print(f"Pattern ID: {pattern.pattern_id}")
    print(f"Type: {pattern.pattern_type}")
    print(f"Confidence: {pattern.confidence:.2f}")
    print(f"Occurrences: {pattern.occurrences}")
    print(f"Description: {pattern.description}")
    print(f"First Seen: {pattern.first_seen}")
    print(f"Last Seen: {pattern.last_seen}")
```

**Pattern Structure**:
```python
@dataclass
class Pattern:
    pattern_id: str              # Unique identifier
    pattern_type: str            # "sequence", "frequency", "correlation", "temporal"
    description: str             # Human-readable description
    events: List[Dict]           # Events in pattern
    confidence: float            # 0.0 to 1.0
    occurrences: int             # Times pattern observed
    first_seen: datetime         # First occurrence
    last_seen: datetime          # Most recent occurrence
    metadata: Dict[str, Any]     # Additional context
```

### 2. Healing Analytics

**Purpose**: Track self-healing effectiveness and generate improvement recommendations.

**Key Metrics**:
- Overall healing success rate
- Strategy-specific effectiveness
- Mean Time To Recovery (MTTR)
- Failure pattern analysis
- Healing time distribution
- Performance trends

**Configuration**:
```python
from moai_flow.optimization.healing_analytics import HealingAnalytics

analytics = HealingAnalytics(self_healer)
```

**Overall Statistics**:
```python
stats = analytics.get_overall_stats(time_range_ms=300000)  # Last 5 minutes

{
    "total_failures": 100,
    "total_healings": 95,
    "success_rate": 0.90,  # 90% success rate
    "avg_healing_time_ms": 250,
    "by_strategy": {
        "AgentRestartStrategy": 40,
        "TaskRetryStrategy": 35,
        "ResourceRebalanceStrategy": 15,
        "QuorumRecoveryStrategy": 5
    },
    "by_failure_type": {
        "agent_down": 40,
        "task_timeout": 35,
        "resource_exhaustion": 15,
        "quorum_loss": 5
    },
    "mttr_ms": 250  # Mean Time To Recovery
}
```

**Strategy Effectiveness**:
```python
effectiveness = analytics.get_strategy_effectiveness()

for strategy in effectiveness:
    print(f"Strategy: {strategy.strategy_name}")
    print(f"Success: {strategy.success_count}")
    print(f"Failures: {strategy.failure_count}")
    print(f"Success Rate: {strategy.success_rate:.1%}")
    print(f"Avg Time: {strategy.avg_healing_time_ms}ms")
    print(f"Trend: {strategy.trend}")  # "improving", "stable", "degrading"
    print(f"Recommendation: {strategy.recommendation}")
```

**Strategy Effectiveness Structure**:
```python
@dataclass
class StrategyEffectiveness:
    strategy_name: str           # Strategy identifier
    success_count: int           # Successful healings
    failure_count: int           # Failed healings
    success_rate: float          # Success rate (0.0-1.0)
    avg_healing_time_ms: float   # Average healing duration
    trend: str                   # "improving", "stable", "degrading"
    recommendation: str          # "keep", "tune", "replace"
```

**Recommendations**:
```python
recommendations = analytics.generate_recommendations()

# Example recommendations:
[
    "Strategy TaskRetryStrategy has low success rate (65%). Consider increasing max_retries.",
    "ResourceRebalanceStrategy showing degrading trend. Review resource allocation logic.",
    "Overall MTTR (250ms) is optimal. Maintain current configuration."
]
```

### 3. Trend Analysis

**Purpose**: Detect performance degradation using statistical methods.

**Trend Detection Algorithm**:
```python
def _analyze_trends(metric_name, time_range_ms):
    # Get metric values over time
    task_metrics = metrics_storage.get_task_metrics(
        time_range=(start_time, now),
        limit=500
    )

    # Extract values based on metric
    if metric_name == "duration_ms":
        values = [m.get("duration_ms", 0) for m in task_metrics]
    elif metric_name == "tokens_used":
        values = [m.get("tokens_used", 0) for m in task_metrics]
    elif metric_name == "success_rate":
        values = [1 if m.get("result") == "success" else 0 for m in task_metrics]

    # Calculate moving average
    moving_avg = _calculate_moving_average(values, window=10)

    # Compare recent vs. historical
    recent_avg = statistics.mean(moving_avg[-5:])
    historical_avg = statistics.mean(moving_avg[:-5])

    change_pct = (recent_avg - historical_avg) / historical_avg

    # Determine trend
    if metric_name == "success_rate":
        # Higher is better
        if change_pct > 0.05:
            return "improving"
        elif change_pct < -0.05:
            return "degrading"
    else:
        # Lower is better (duration, tokens)
        if change_pct < -0.05:
            return "improving"
        elif change_pct > 0.05:
            return "degrading"

    return "stable"
```

**Trend Categories**:
- **Improving**: Performance getting better (>5% improvement)
- **Stable**: No significant change (±5%)
- **Degrading**: Performance declining (>5% degradation)

### 4. Metric Collection

**Purpose**: Real-time performance data collection and storage.

**Collected Metrics**:

| Metric Category | Measurements |
|----------------|--------------|
| **Task Performance** | Duration, throughput, success rate, token usage |
| **Agent Health** | Success rate, response time, heartbeat frequency |
| **Resource Usage** | Token consumption, memory allocation, queue depth |
| **Healing Actions** | Strategy used, duration, success/failure, impact |

**Metric Storage Pattern**:
```python
# Task completion metric
{
    "type": "task_complete",
    "timestamp": datetime.now(timezone.utc),
    "agent_id": "agent-001",
    "task_id": "task-123",
    "duration_ms": 2500,
    "tokens_used": 1500,
    "result": "success",
    "metadata": {
        "complexity": "medium",
        "retry_count": 0
    }
}

# Agent health metric
{
    "type": "agent_health",
    "timestamp": datetime.now(timezone.utc),
    "agent_id": "agent-001",
    "health_state": "HEALTHY",
    "success_rate": 0.95,
    "avg_response_time_ms": 2000,
    "heartbeat_interval_ms": 5000
}

# Resource usage metric
{
    "type": "resource_metric",
    "timestamp": datetime.now(timezone.utc),
    "metadata": {
        "token_usage_percent": 75,
        "memory_usage_percent": 60,
        "queue_depth": 25,
        "active_agents": 8
    }
}
```

## Pattern Learning Algorithms

### Sequence Pattern Detection (N-gram Analysis)

**Purpose**: Identify repeated event sequences.

**Algorithm**:
1. Extract event type sequences from history
2. Generate n-grams (sequences of length n)
3. Count n-gram occurrences
4. Filter by minimum occurrence threshold
5. Calculate confidence based on frequency

**Example**:
```python
# Event sequence
events = [
    {"type": "task_start"},
    {"type": "agent_assigned"},
    {"type": "task_complete"},
    {"type": "task_start"},
    {"type": "agent_assigned"},
    {"type": "task_complete"}
]

# Detected pattern (3-gram)
pattern = {
    "pattern_type": "sequence",
    "events": [
        {"type": "task_start"},
        {"type": "agent_assigned"},
        {"type": "task_complete"}
    ],
    "occurrences": 2,
    "confidence": 0.85,
    "description": "Task start → Agent assigned → Task complete"
}
```

### Frequency Pattern Detection

**Purpose**: Identify events occurring at regular intervals.

**Algorithm**:
1. Extract timestamps for each event type
2. Calculate inter-arrival times
3. Compute mean and standard deviation
4. Identify regular patterns (low stddev)

**Example**:
```python
# Heartbeat events at 5-second intervals
pattern = {
    "pattern_type": "frequency",
    "events": [{"type": "heartbeat"}],
    "occurrences": 100,
    "confidence": 0.95,
    "metadata": {
        "avg_interval_seconds": 5.0,
        "stddev_seconds": 0.2
    },
    "description": "Heartbeat every 5.0s (±0.2s)"
}
```

### Correlation Pattern Detection

**Purpose**: Identify events that frequently co-occur.

**Algorithm**:
1. Group events into time windows
2. Count co-occurrences of event type pairs
3. Calculate correlation coefficient
4. Filter by significance threshold

**Example**:
```python
# High token usage correlates with task failures
pattern = {
    "pattern_type": "correlation",
    "events": [
        {"type": "high_token_usage"},
        {"type": "task_failed"}
    ],
    "occurrences": 25,
    "confidence": 0.80,
    "metadata": {
        "correlation": 0.75,
        "time_window_ms": 10000
    },
    "description": "High token usage → Task failure (75% correlation)"
}
```

## Healing Analytics Algorithms

### Strategy Effectiveness Calculation

**Purpose**: Evaluate healing strategy performance.

**Metrics**:
```python
def calculate_strategy_effectiveness(strategy_name, healing_history):
    # Filter healings for this strategy
    strategy_healings = [
        h for h in healing_history
        if h.strategy_used == strategy_name
    ]

    if not strategy_healings:
        return None

    # Calculate metrics
    success_count = sum(1 for h in strategy_healings if h.success)
    failure_count = len(strategy_healings) - success_count
    success_rate = success_count / len(strategy_healings)

    # Average healing time
    avg_time = statistics.mean([h.duration_ms for h in strategy_healings])

    # Trend analysis (recent vs. historical)
    recent = strategy_healings[-10:]
    historical = strategy_healings[:-10]

    recent_success_rate = sum(1 for h in recent if h.success) / len(recent)
    historical_success_rate = sum(1 for h in historical if h.success) / len(historical)

    if recent_success_rate > historical_success_rate + 0.05:
        trend = "improving"
    elif recent_success_rate < historical_success_rate - 0.05:
        trend = "degrading"
    else:
        trend = "stable"

    return StrategyEffectiveness(
        strategy_name=strategy_name,
        success_count=success_count,
        failure_count=failure_count,
        success_rate=success_rate,
        avg_healing_time_ms=avg_time,
        trend=trend
    )
```

### Mean Time To Recovery (MTTR)

**Purpose**: Measure average time from failure detection to successful healing.

**Calculation**:
```python
def calculate_mttr(healing_history):
    successful_healings = [h for h in healing_history if h.success]

    if not successful_healings:
        return 0.0

    return statistics.mean([h.duration_ms for h in successful_healings])
```

### Recommendation Engine

**Purpose**: Generate actionable improvement recommendations.

**Rules**:
```python
def generate_recommendations(effectiveness_data):
    recommendations = []

    for strategy in effectiveness_data:
        # Low success rate
        if strategy.success_rate < 0.7:
            recommendations.append(
                f"Strategy {strategy.strategy_name} has low success rate "
                f"({strategy.success_rate:.1%}). Consider tuning or replacing."
            )

        # Degrading trend
        if strategy.trend == "degrading":
            recommendations.append(
                f"Strategy {strategy.strategy_name} showing degrading trend. "
                f"Review recent changes and configuration."
            )

        # High healing time
        if strategy.avg_healing_time_ms > 1000:
            recommendations.append(
                f"Strategy {strategy.strategy_name} has high healing time "
                f"({strategy.avg_healing_time_ms}ms). Optimize strategy logic."
            )

    return recommendations
```

## Usage Examples

### Complete Monitoring Setup

```python
from moai_flow.optimization import PatternLearner
from moai_flow.optimization.healing_analytics import HealingAnalytics

# Initialize components
learner = PatternLearner(
    min_occurrences=5,
    confidence_threshold=0.7,
    max_history_size=10000
)

analytics = HealingAnalytics(self_healer)

# Record events continuously
for event in system_events:
    learner.record_event(event)

# Periodic analysis (every 5 minutes)
while monitoring:
    # Learn patterns
    patterns = learner.learn_patterns()

    # Analyze healing effectiveness
    stats = analytics.get_overall_stats(time_range_ms=300000)
    effectiveness = analytics.get_strategy_effectiveness()
    recommendations = analytics.generate_recommendations()

    # Report
    print(f"Patterns Learned: {len(patterns)}")
    print(f"Healing Success Rate: {stats.success_rate:.1%}")
    print(f"MTTR: {stats.mttr_ms}ms")

    for rec in recommendations:
        print(f"Recommendation: {rec}")

    time.sleep(300)  # 5 minutes
```

### Pattern-Based Optimization

```python
# Learn patterns
patterns = learner.learn_patterns()

# Identify high-confidence patterns
high_confidence = [p for p in patterns if p.confidence > 0.85]

# Use patterns for optimization
for pattern in high_confidence:
    if pattern.pattern_type == "sequence":
        # Optimize task sequencing
        optimize_task_sequence(pattern.events)

    elif pattern.pattern_type == "frequency":
        # Adjust polling/heartbeat intervals
        adjust_interval(pattern.metadata["avg_interval_seconds"])

    elif pattern.pattern_type == "correlation":
        # Implement preventive measures
        prevent_correlated_failures(pattern.events)
```

### Healing Effectiveness Dashboard

```python
def generate_healing_dashboard(analytics):
    stats = analytics.get_overall_stats()
    effectiveness = analytics.get_strategy_effectiveness()

    print("=" * 60)
    print("Healing Effectiveness Dashboard")
    print("=" * 60)
    print(f"Total Failures: {stats.total_failures}")
    print(f"Total Healings: {stats.total_healings}")
    print(f"Success Rate: {stats.success_rate:.1%}")
    print(f"MTTR: {stats.mttr_ms}ms")
    print()

    print("Strategy Performance:")
    print("-" * 60)
    for strategy in effectiveness:
        print(f"{strategy.strategy_name}:")
        print(f"  Success Rate: {strategy.success_rate:.1%}")
        print(f"  Avg Time: {strategy.avg_healing_time_ms}ms")
        print(f"  Trend: {strategy.trend}")
        print(f"  Recommendation: {strategy.recommendation}")
        print()

    print("Recommendations:")
    print("-" * 60)
    recommendations = analytics.generate_recommendations()
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec}")
```

## Best Practices

1. **Event Recording**: Record all significant system events for comprehensive analysis
2. **Pattern Review**: Regularly review learned patterns and adjust thresholds
3. **Healing Metrics**: Monitor healing effectiveness and act on recommendations
4. **Trend Monitoring**: Track performance trends to detect degradation early
5. **Threshold Tuning**: Adjust confidence thresholds based on false positive rates
6. **History Management**: Limit history size to prevent memory issues (default: 10,000 events)

## Performance Characteristics

**Pattern Learning**: <500ms for 1000 events
**Healing Analytics**: <100ms for 1000 healing records
**Memory Usage**: O(n) where n = max_history_size
**Thread Safety**: Lock-based synchronization for concurrent access

## Related Documentation

- [Bottleneck Detection](bottleneck-detection.md) - Performance bottleneck analysis
- [Predictive Healing](predictive-healing.md) - Pattern-based failure prediction
- [Resource Allocation](resource-allocation.md) - Dynamic resource optimization
