# MetricsCollector Quick Start Guide

**5-Minute Integration Guide for MoAI-Flow Phase 6A**

---

## Step 1: Import

```python
from moai_flow.monitoring import MetricsCollector, TaskResult
```

---

## Step 2: Initialize

```python
# Simple in-memory collector
collector = MetricsCollector(async_mode=True)

# With persistent storage (when available)
storage = MetricsStorage()
collector = MetricsCollector(storage, async_mode=True)
```

---

## Step 3: Record Task Metrics

```python
# After task execution
collector.record_task_metric(
    task_id="task-001",
    agent_id="expert-backend",
    duration_ms=3500,
    result=TaskResult.SUCCESS,
    tokens_used=25000,
    files_changed=3
)
```

---

## Step 4: Get Statistics

```python
# Get task stats
stats = collector.get_task_stats(agent_id="expert-backend")
print(f"Success rate: {stats['success_rate']:.1f}%")

# Get agent performance
perf = collector.get_agent_performance("expert-backend")
print(f"Average duration: {perf['avg_duration_ms']:.0f}ms")
```

---

## Step 5: Shutdown (Optional)

```python
# Gracefully shutdown async worker
collector.shutdown()
```

---

## Complete Example

```python
from moai_flow.monitoring import MetricsCollector, TaskResult
import time

# Initialize
collector = MetricsCollector(async_mode=True)

# Simulate task execution
start_time = time.perf_counter()
# ... do work ...
duration_ms = (time.perf_counter() - start_time) * 1000

# Record metric
collector.record_task_metric(
    task_id="task-001",
    agent_id="expert-backend",
    duration_ms=duration_ms,
    result=TaskResult.SUCCESS,
    tokens_used=25000
)

# Get statistics
stats = collector.get_task_stats()
print(f"Success rate: {stats['success_rate']:.1f}%")
print(f"Average duration: {stats['avg_duration_ms']:.0f}ms")

# Cleanup
collector.shutdown()
```

---

## Integration with SwarmCoordinator

```python
from moai_flow.core.swarm_coordinator import SwarmCoordinator, AgentState
from moai_flow.monitoring import MetricsCollector, TaskResult
import time

# Initialize both
coordinator = SwarmCoordinator(topology_type="mesh")
collector = MetricsCollector(async_mode=True)

# Register agent
coordinator.register_agent("agent-001", {"type": "expert-backend"})

# Execute task with metrics
start_time = time.perf_counter()

# Update state
coordinator.set_agent_state("agent-001", AgentState.BUSY)

# ... task execution ...

# Update state
coordinator.set_agent_state("agent-001", AgentState.ACTIVE)

# Record metric
duration_ms = (time.perf_counter() - start_time) * 1000
collector.record_task_metric(
    task_id="task-001",
    agent_id="agent-001",
    duration_ms=duration_ms,
    result=TaskResult.SUCCESS,
    tokens_used=25000
)
```

---

## Common Patterns

### Pattern 1: Task Execution Wrapper

```python
def execute_with_metrics(task_id, agent_id, task_func, collector):
    start_time = time.perf_counter()

    try:
        result = task_func()
        duration_ms = (time.perf_counter() - start_time) * 1000

        collector.record_task_metric(
            task_id=task_id,
            agent_id=agent_id,
            duration_ms=duration_ms,
            result=TaskResult.SUCCESS,
            tokens_used=result.get("tokens", 0)
        )

        return result
    except Exception as e:
        duration_ms = (time.perf_counter() - start_time) * 1000

        collector.record_task_metric(
            task_id=task_id,
            agent_id=agent_id,
            duration_ms=duration_ms,
            result=TaskResult.FAILURE
        )

        raise
```

### Pattern 2: Agent Performance Monitoring

```python
# Record tasks over time
for task in tasks:
    collector.record_task_metric(...)

# Periodically check performance
perf = collector.get_agent_performance(agent_id)
if perf["error_rate"] > 10.0:
    print(f"Warning: {agent_id} error rate is {perf['error_rate']:.1f}%")
```

### Pattern 3: Swarm Health Monitoring

```python
# Record swarm metrics periodically
def monitor_swarm_health(swarm_id, coordinator, collector):
    topology_info = coordinator.get_topology_info()

    # Record health metric
    health_score = (
        topology_info["active_agents"] / topology_info["agent_count"]
        if topology_info["agent_count"] > 0 else 0.0
    )

    collector.record_swarm_metric(
        swarm_id=swarm_id,
        metric_type="topology_health",
        value=health_score
    )
```

---

## Performance Tips

1. **Use Async Mode**: Enable `async_mode=True` for <1ms overhead
2. **Batch Statistics**: Call `get_task_stats()` periodically, not per-task
3. **Optional Storage**: Start with in-memory, add storage when needed
4. **Graceful Shutdown**: Always call `shutdown()` to flush pending metrics

---

## Troubleshooting

### Q: High collection overhead (>1ms)

**A**: Check async mode is enabled:
```python
collector = MetricsCollector(async_mode=True)  # Should be True
```

### Q: Metrics not persisting

**A**: Verify storage is configured:
```python
storage = MetricsStorage()
collector = MetricsCollector(storage)  # Pass storage instance
```

### Q: Missing metrics

**A**: Check collector is enabled:
```python
collector = MetricsCollector(enabled=True)  # Should be True
```

---

## Next Steps

- Read [MetricsCollector Documentation](./metrics-collector.md)
- Explore [Demo Examples](../../examples/metrics_collector_demo.py)
- Check [PRD-08: Performance Metrics](../../specs/PRD-08-performance-metrics.md)

---

**Last Updated**: 2025-11-29
**Phase**: 6A (Weeks 1-2)
**Status**: Production Ready
