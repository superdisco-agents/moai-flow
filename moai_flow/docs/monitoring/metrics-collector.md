# MetricsCollector - Phase 6A Observability Foundation

**Status**: Implemented (Phase 6A, Weeks 1-2)
**Component**: `moai_flow/monitoring/metrics_collector.py`
**Version**: 1.0.0

---

## Overview

`MetricsCollector` is the core observability component for MoAI-Flow swarm coordination. It provides <1ms overhead async metrics collection for task execution, agent performance, and swarm health.

### Key Features

- ✅ **<1ms Overhead**: Non-blocking async collection via background thread
- ✅ **Three Metric Types**: Task, Agent, and Swarm metrics
- ✅ **Configurable**: Enable/disable via constructor, optional persistence
- ✅ **Graceful Degradation**: Continues if storage fails (in-memory only)
- ✅ **Thread-Safe**: Lock-based concurrent access protection
- ✅ **Statistics**: Automatic aggregation and performance analysis

---

## Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                       MetricsCollector                         │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  Task Metrics         Agent Metrics        Swarm Metrics      │
│  ─────────────       ──────────────        ──────────────      │
│  • duration_ms       • tasks_completed     • topology_health  │
│  • result            • avg_duration        • throughput       │
│  • tokens_used       • error_rate          • latency          │
│  • files_changed                                              │
│                                                                │
├────────────────────────────────────────────────────────────────┤
│                    Async Collection Queue                      │
│                  (Non-blocking, <1ms overhead)                 │
├────────────────────────────────────────────────────────────────┤
│                     MetricsStorage                             │
│                  (Optional persistence layer)                  │
└────────────────────────────────────────────────────────────────┘
```

---

## Usage

### Basic Initialization

```python
from moai_flow.monitoring import MetricsCollector, TaskResult

# In-memory only (no persistence)
collector = MetricsCollector(async_mode=True)

# With persistent storage
storage = MetricsStorage()
collector = MetricsCollector(storage, async_mode=True)

# Disabled metrics (zero overhead)
collector = MetricsCollector(enabled=False)
```

### Recording Task Metrics

```python
# Record task execution
collector.record_task_metric(
    task_id="task-001",
    agent_id="expert-backend",
    duration_ms=3500,
    result=TaskResult.SUCCESS,
    tokens_used=25000,
    files_changed=3,
    metadata={"spec_id": "SPEC-001"}
)
```

### Recording Agent Metrics

```python
# Record agent performance
collector.record_agent_metric(
    agent_id="expert-backend",
    metric_type="tasks_completed",
    value=45,
    metadata={"period": "daily"}
)
```

### Recording Swarm Metrics

```python
# Record swarm health
collector.record_swarm_metric(
    swarm_id="swarm-001",
    metric_type="topology_health",
    value=0.95
)
```

---

## Statistics API

### Task Statistics

```python
# Get task stats for specific agent
stats = collector.get_task_stats(agent_id="expert-backend")

# Get stats for time range
from datetime import datetime, timedelta
time_range = (
    datetime.now() - timedelta(hours=24),
    datetime.now()
)
stats = collector.get_task_stats(time_range=time_range)

# Get stats with specific aggregation
stats = collector.get_task_stats(aggregation="median")

# Returns:
# {
#     "count": 10,
#     "avg_duration_ms": 3500,
#     "median_duration_ms": 3200,
#     "min_duration_ms": 2800,
#     "max_duration_ms": 4500,
#     "success_rate": 90.0,
#     "total_tokens": 250000,
#     "total_files_changed": 15,
#     "results_breakdown": {"success": 9, "failure": 1}
# }
```

### Agent Performance

```python
# Get agent performance summary
perf = collector.get_agent_performance("expert-backend")

# Returns:
# {
#     "agent_id": "expert-backend",
#     "tasks_completed": 45,
#     "success_rate": 89.0,
#     "avg_duration_ms": 3250,
#     "error_rate": 11.0,
#     "total_tokens_used": 1125000
# }
```

### Swarm Health

```python
# Get current swarm health
health = collector.get_swarm_health("swarm-001")

# Get with historical data
health = collector.get_swarm_health("swarm-001", include_history=True)

# Returns:
# {
#     "swarm_id": "swarm-001",
#     "topology_health": 0.95,
#     "message_throughput": 150,
#     "consensus_latency_ms": 45,
#     "last_updated": "2025-11-29T10:00:00Z",
#     "history": [...]  # if include_history=True
# }
```

---

## Performance Monitoring

### Collection Overhead

```python
# Get collection performance metrics
overhead = collector.get_collection_overhead()

# Returns:
# {
#     "avg_collection_time_ms": 0.002,
#     "max_collection_time_ms": 0.011,
#     "total_collections": 100
# }
```

Target: **<1ms average collection overhead**

---

## Integration with SwarmCoordinator

```python
from moai_flow.core.swarm_coordinator import SwarmCoordinator, AgentState
from moai_flow.monitoring import MetricsCollector, TaskResult
import time

# Initialize
coordinator = SwarmCoordinator(topology_type="mesh")
collector = MetricsCollector(async_mode=True)

# Register agent
coordinator.register_agent("agent-001", {"type": "expert-backend"})

# Execute task with metrics
start_time = time.perf_counter()

# Update state
coordinator.set_agent_state("agent-001", AgentState.BUSY)

# Simulate work
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

## Metric Types

### TaskMetric

```python
@dataclass
class TaskMetric:
    task_id: str
    agent_id: str
    duration_ms: float
    result: TaskResult  # SUCCESS, FAILURE, PARTIAL, TIMEOUT
    tokens_used: int = 0
    files_changed: int = 0
    timestamp: str = <auto-generated>
    metadata: Dict[str, Any] = {}
```

### AgentMetric

```python
@dataclass
class AgentMetric:
    agent_id: str
    metric_type: str  # "tasks_completed", "avg_duration", "error_rate"
    value: float
    timestamp: str = <auto-generated>
    metadata: Dict[str, Any] = {}
```

### SwarmMetric

```python
@dataclass
class SwarmMetric:
    swarm_id: str
    metric_type: str  # "topology_health", "message_throughput", "consensus_latency"
    value: float
    timestamp: str = <auto-generated>
    metadata: Dict[str, Any] = {}
```

---

## Configuration Options

```python
MetricsCollector(
    storage=None,           # MetricsStorage instance (optional)
    async_mode=True,        # Enable async collection (default: True)
    enabled=True,           # Enable/disable metrics (default: True)
    queue_size=1000        # Async queue size (default: 1000)
)
```

### Async Mode

- **Enabled** (default): Metrics queued and processed in background thread
- **Disabled**: Metrics recorded synchronously (blocking)

### Enabled Flag

- **True** (default): Metrics collected normally
- **False**: Zero overhead, all recording is no-op

---

## Error Handling

### Graceful Degradation

If storage persistence fails, metrics continue in-memory:

```python
storage = MetricsStorage()
collector = MetricsCollector(storage)

# If storage.save_task_metric() fails:
# - Error logged
# - Metric remains in-memory
# - No exception raised
```

### Queue Overflow

If async queue is full:

```python
# Automatic fallback to synchronous recording
# Warning logged
# Metric still recorded
```

---

## Shutdown

```python
# Graceful shutdown
collector.shutdown()

# Waits for:
# - Async queue to drain
# - Background thread to exit
# - All pending metrics to be processed
```

---

## Performance Characteristics

| Operation | Overhead | Mode |
|-----------|----------|------|
| `record_task_metric()` | <0.01ms | Async |
| `record_agent_metric()` | <0.01ms | Async |
| `record_swarm_metric()` | <0.01ms | Async |
| `get_task_stats()` | ~0.5-2ms | Sync |
| `get_agent_performance()` | ~0.5-2ms | Sync |

**Measured**: Average 0.002ms collection overhead on 100 metrics (well under 1ms target)

---

## Examples

### Example 1: Basic Task Tracking

```python
collector = MetricsCollector()

# Record 3 tasks
collector.record_task_metric("task-001", "agent-001", 3500, TaskResult.SUCCESS, 25000, 3)
collector.record_task_metric("task-002", "agent-001", 2800, TaskResult.SUCCESS, 18000, 2)
collector.record_task_metric("task-003", "agent-002", 4200, TaskResult.FAILURE, 12000, 0)

# Get stats
stats = collector.get_task_stats()
print(f"Success rate: {stats['success_rate']:.1f}%")  # 66.7%
```

### Example 2: Agent Performance Comparison

```python
collector = MetricsCollector()

# Record tasks for multiple agents
# ... (task execution) ...

# Compare performance
for agent_id in ["expert-backend", "expert-frontend", "manager-tdd"]:
    perf = collector.get_agent_performance(agent_id)
    print(f"{agent_id}: {perf['success_rate']:.1f}% success, {perf['avg_duration_ms']:.0f}ms avg")
```

### Example 3: Swarm Health Monitoring

```python
collector = MetricsCollector()

# Record swarm metrics over time
for snapshot in health_snapshots:
    collector.record_swarm_metric("swarm-001", "topology_health", snapshot.health)
    collector.record_swarm_metric("swarm-001", "message_throughput", snapshot.throughput)

# Get current health
health = collector.get_swarm_health("swarm-001")
print(f"Health: {health['topology_health']:.2f}")
```

---

## Related Documentation

- [MetricsStorage](./metrics-storage.md) - Persistent metrics storage
- [HeartbeatMonitor](./heartbeat-monitor.md) - Active health monitoring
- [PRD-08: Performance Metrics](../../specs/PRD-08-performance-metrics.md)
- [SwarmCoordinator Integration](../core/swarm-coordinator.md)

---

## Changelog

- **v1.0.0** (2025-11-29): Initial implementation for Phase 6A
  - Task, Agent, and Swarm metrics collection
  - Async collection with <1ms overhead
  - Statistics and aggregation API
  - SwarmCoordinator integration

---

**Last Updated**: 2025-11-29
**Phase**: 6A (Weeks 1-2) - Observability Foundation
**Status**: ✅ Implemented and Tested
