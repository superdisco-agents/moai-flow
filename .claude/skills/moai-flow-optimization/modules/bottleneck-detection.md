# Bottleneck Detection Module

Real-time performance bottleneck identification with <100ms detection time and actionable recommendations.

## Overview

The BottleneckDetector analyzes system metrics to identify five types of performance bottlenecks:

1. **Token Exhaustion** - Token budget depletion
2. **Quota Exceeded** - Agent capacity limits reached
3. **Slow Agent** - Underperforming agents
4. **Task Queue Backlog** - Task accumulation
5. **Consensus Timeout** - Consensus coordination delays

## Architecture

```
BottleneckDetector
├── Detection Methods (5 types)
│   ├── _detect_token_bottleneck()
│   ├── _detect_quota_bottleneck()
│   ├── _detect_slow_agent_bottleneck()
│   ├── _detect_queue_bottleneck()
│   └── _detect_consensus_bottleneck()
├── Performance Analysis
│   ├── analyze_performance()
│   └── _analyze_trends()
├── Statistical Methods
│   ├── _calculate_percentile()
│   ├── _calculate_moving_average()
│   └── _calculate_severity()
└── Recommendation Engine
    ├── get_recommendations()
    └── get_recommendations_for_type()
```

## Detection Algorithms

### 1. Token Exhaustion Detection

**Criteria**:
- Token usage > 80% of budget
- Token consumption rate increasing
- Tasks failing due to insufficient tokens

**Algorithm**:
```python
def _detect_token_bottleneck(self):
    usage = self._resources.get_resource_usage()
    tokens = usage.get("tokens", {})

    total_budget = tokens.get("total_budget", 0)
    consumed = tokens.get("consumed", 0)
    usage_ratio = consumed / total_budget

    if usage_ratio < 0.8:  # Threshold
        return None

    # Calculate impact score (0-1)
    impact_score = usage_ratio

    # Determine severity
    severity = self._calculate_severity("token_exhaustion", impact_score)

    return Bottleneck(
        bottleneck_type="token_exhaustion",
        severity=severity,
        metrics={"usage_ratio": usage_ratio, "remaining": total_budget - consumed},
        recommendations=self.RECOMMENDATIONS["token_exhaustion"]
    )
```

**Recommendations**:
- Increase token budget in config.json
- Optimize prompts to reduce token usage
- Implement token-aware task prioritization
- Cache frequently used responses

### 2. Quota Exceeded Detection

**Criteria**:
- Active agents ≥ max quota (90% threshold)
- Tasks waiting for agent slots
- Queue backlog increasing

**Algorithm**:
```python
def _detect_quota_bottleneck(self):
    usage = self._resources.get_resource_usage()
    agents_info = usage.get("agents", {})

    total_quotas = agents_info.get("total_quotas", 0)
    active_agents = agents_info.get("active_agents", 0)
    quota_usage_ratio = active_agents / total_quotas

    if quota_usage_ratio < 0.9:  # 90% threshold
        return None

    queue_info = usage.get("queue", {})
    pending_tasks = queue_info.get("pending_tasks", 0)

    # Impact score includes queue pressure
    impact_score = min(quota_usage_ratio + (pending_tasks / 100), 1.0)

    return Bottleneck(
        bottleneck_type="quota_exceeded",
        severity=self._calculate_severity("quota_exceeded", impact_score),
        metrics={
            "quota_usage_ratio": quota_usage_ratio,
            "pending_tasks": pending_tasks
        },
        recommendations=self.RECOMMENDATIONS["quota_exceeded"]
    )
```

**Recommendations**:
- Increase agent quota for bottleneck type
- Optimize agent task distribution
- Implement dynamic agent scaling
- Reduce concurrent task submissions

### 3. Slow Agent Detection

**Criteria**:
- Agent task duration > 2x average
- Agent success rate < 70%
- Agent causing task failures

**Algorithm**:
```python
def _detect_slow_agent_bottleneck(self):
    # Get task metrics from detection window
    task_metrics = self._metrics.get_task_metrics(
        time_range=(start_time, now),
        limit=500
    )

    # Group by agent_id
    agent_stats = defaultdict(lambda: {
        "durations": [],
        "success_count": 0,
        "total_count": 0
    })

    for metric in task_metrics:
        agent_id = metric.get("agent_id")
        duration_ms = metric.get("duration_ms", 0)
        result = metric.get("result")

        agent_stats[agent_id]["durations"].append(duration_ms)
        agent_stats[agent_id]["total_count"] += 1
        if result == "success":
            agent_stats[agent_id]["success_count"] += 1

    # Calculate overall average duration
    all_durations = [d for stats in agent_stats.values() for d in stats["durations"]]
    avg_duration = statistics.mean(all_durations)

    # Find slow agents (>2x average OR <70% success rate)
    slow_agents = []
    for agent_id, stats in agent_stats.items():
        agent_avg_duration = statistics.mean(stats["durations"])
        success_rate = stats["success_count"] / stats["total_count"]

        if (agent_avg_duration > avg_duration * 2.0 or success_rate < 0.7):
            slow_agents.append({
                "agent_id": agent_id,
                "avg_duration_ms": agent_avg_duration,
                "success_rate": success_rate
            })

    if not slow_agents:
        return None

    return Bottleneck(
        bottleneck_type="slow_agent",
        affected_resources=[a["agent_id"] for a in slow_agents],
        metrics={"slow_agents": slow_agents},
        recommendations=self.RECOMMENDATIONS["slow_agent"]
    )
```

**Recommendations**:
- Replace slow agent with faster alternative
- Reduce complexity of agent prompts
- Distribute tasks to healthier agents
- Investigate agent health issues

### 4. Queue Backlog Detection

**Criteria**:
- Queue depth > 50 tasks
- Average wait time increasing
- High-priority tasks stuck in queue

**Algorithm**:
```python
def _detect_queue_bottleneck(self):
    usage = self._resources.get_resource_usage()
    queue_info = usage.get("queue", {})

    pending_tasks = queue_info.get("pending_tasks", 0)
    by_priority = queue_info.get("by_priority", {})

    if pending_tasks < 50:  # Threshold
        return None

    # Check for high-priority tasks in queue
    high_priority_count = by_priority.get("CRITICAL", 0) + by_priority.get("HIGH", 0)

    # Calculate impact score
    queue_ratio = min(pending_tasks / 100, 1.0)
    priority_impact = min(high_priority_count / 20, 1.0)
    impact_score = max(queue_ratio, priority_impact)

    return Bottleneck(
        bottleneck_type="task_queue_backlog",
        metrics={
            "pending_tasks": pending_tasks,
            "by_priority": by_priority,
            "high_priority_count": high_priority_count
        },
        recommendations=self.RECOMMENDATIONS["task_queue_backlog"]
    )
```

**Recommendations**:
- Increase agent quota to process queue faster
- Prioritize critical tasks
- Implement parallel processing
- Review task submission rate

### 5. Consensus Timeout Detection

**Criteria**:
- Consensus timeout rate > 10%
- Average consensus time > 10s
- Agent non-responsiveness

**Status**: Placeholder for Phase 6B integration

## Performance Analysis

### Comprehensive Performance Report

**Purpose**: Analyze system performance over time range with trend detection.

**Metrics Collected**:
- Task count and throughput
- Average duration (mean)
- P95 and P99 latency percentiles
- Average tokens per task
- Success rate

**Trend Analysis**:
- **Improving**: Recent average < historical (for duration/tokens)
- **Stable**: Change < 5%
- **Degrading**: Recent average > historical

**Example**:
```python
report = detector.analyze_performance(time_range_ms=300000)  # 5 minutes

# Report structure
{
    "report_id": "report-uuid",
    "time_range_ms": 300000,
    "bottlenecks_detected": [Bottleneck, ...],
    "metrics_summary": {
        "task_count": 1234,
        "avg_duration_ms": 2500,
        "p95_duration_ms": 5000,
        "p99_duration_ms": 8000,
        "avg_tokens_per_task": 1500,
        "success_rate": 0.95
    },
    "trends": {
        "task_duration": "stable",
        "token_usage": "improving",
        "success_rate": "improving"
    }
}
```

## Statistical Methods

### Percentile Calculation

**Purpose**: Calculate P95/P99 latency for performance analysis.

```python
def _calculate_percentile(values: List[float], percentile: int) -> float:
    if not values:
        return 0.0

    sorted_values = sorted(values)
    index = int(len(sorted_values) * (percentile / 100.0))
    index = min(index, len(sorted_values) - 1)

    return sorted_values[index]
```

### Moving Average

**Purpose**: Calculate moving average for trend detection.

```python
def _calculate_moving_average(values: List[float], window: int = 10) -> List[float]:
    if len(values) < window:
        return [statistics.mean(values)] if values else []

    moving_avg = []
    for i in range(len(values) - window + 1):
        window_values = values[i:i+window]
        moving_avg.append(statistics.mean(window_values))

    return moving_avg
```

### Severity Calculation

**Purpose**: Calculate bottleneck severity based on impact score.

**Thresholds**:
- **Critical**: impact_score ≥ 0.8
- **High**: impact_score ≥ 0.6
- **Medium**: impact_score ≥ 0.4
- **Low**: impact_score < 0.4

```python
def _calculate_severity(bottleneck_type: str, impact_score: float) -> str:
    if impact_score >= 0.8:
        return "critical"
    elif impact_score >= 0.6:
        return "high"
    elif impact_score >= 0.4:
        return "medium"
    else:
        return "low"
```

## Recommendation Engine

### Built-in Recommendations

**Token Exhaustion**:
1. Increase token budget in .moai/config/config.json
2. Optimize prompts to reduce token usage
3. Implement token-aware task prioritization
4. Cache frequently used responses

**Quota Exceeded**:
1. Increase agent quota for bottleneck type
2. Optimize agent task distribution
3. Implement dynamic agent scaling
4. Reduce concurrent task submissions

**Slow Agent**:
1. Replace slow agent with faster alternative
2. Reduce complexity of agent prompts
3. Distribute tasks to healthier agents
4. Investigate agent health issues

**Queue Backlog**:
1. Increase agent quota to process queue faster
2. Prioritize critical tasks
3. Implement parallel processing
4. Review task submission rate

**Consensus Timeout**:
1. Reduce consensus timeout threshold
2. Check agent heartbeat health
3. Use faster consensus algorithm (quorum vs raft)
4. Remove unresponsive agents from consensus

## Real-Time Monitoring

### Continuous Monitoring

**Purpose**: Background thread for continuous bottleneck detection.

```python
detector.monitor_continuously(interval_ms=30000)  # Check every 30s

# Monitor loop automatically:
# 1. Detects bottlenecks
# 2. Logs warnings for detected issues
# 3. Runs at specified interval
# 4. Handles exceptions gracefully

# Stop monitoring
detector.stop_monitoring()
```

## Performance Characteristics

**Detection Time**: <100ms for all bottleneck types
**Throughput**: 1000+ events analyzed per detection cycle
**Memory**: O(n) where n = detection window size
**Thread Safety**: Lock-free read operations, synchronized writes

## Usage Examples

### Basic Bottleneck Detection

```python
from moai_flow.optimization import BottleneckDetector

detector = BottleneckDetector(
    metrics_storage=metrics_storage,
    resource_controller=resource_controller,
    detection_window_ms=60000
)

bottlenecks = detector.detect_bottlenecks()

for bottleneck in bottlenecks:
    print(f"Type: {bottleneck.bottleneck_type}")
    print(f"Severity: {bottleneck.severity}")
    print(f"Resources: {bottleneck.affected_resources}")
    for rec in bottleneck.recommendations:
        print(f"  - {rec}")
```

### Performance Report Generation

```python
report = detector.analyze_performance(time_range_ms=300000)

print(f"Analysis Period: {report.time_range_ms / 1000}s")
print(f"Bottlenecks: {len(report.bottlenecks_detected)}")
print(f"Tasks Analyzed: {report.metrics_summary['task_count']}")
print(f"Avg Duration: {report.metrics_summary['avg_duration_ms']}ms")
print(f"P95 Duration: {report.metrics_summary['p95_duration_ms']}ms")
print(f"Success Rate: {report.metrics_summary['success_rate']:.1%}")
print(f"Trends: {report.trends}")
```

### Continuous Monitoring

```python
# Start monitoring
detector.monitor_continuously(interval_ms=30000)

# Monitoring runs in background thread
# Logs warnings when bottlenecks detected

# Later, stop monitoring
detector.stop_monitoring()
```

## Integration Points

**MetricsStorage**: Task metrics for performance analysis
**ResourceController**: Current resource usage (tokens, agents, queue)
**Logger**: Warning/info messages for bottleneck events

## Best Practices

1. **Set appropriate detection window**: 60s for real-time, 300s for trends
2. **Monitor continuously**: Use background monitoring for proactive detection
3. **Act on recommendations**: Prioritize critical and high severity bottlenecks
4. **Track trends**: Use `analyze_performance()` for historical analysis
5. **Combine with healing**: Integrate with SelfHealer for automatic recovery

## Related Documentation

- [Predictive Healing Module](predictive-healing.md) - Use bottleneck data for predictions
- [Performance Monitoring Module](performance-monitoring.md) - Metrics collection
- [Resource Allocation Module](resource-allocation.md) - Dynamic scaling based on bottlenecks
