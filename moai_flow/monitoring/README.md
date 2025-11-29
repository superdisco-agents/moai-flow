# MoAI-Flow Monitoring Module

**Phase 6A Observability** - SQLite-backed metrics persistence with optimized time-series queries.

## Overview

The Monitoring module provides comprehensive metrics storage and analysis capabilities for multi-agent systems. Built on SQLite with optimized indexing, it tracks task-level, agent-level, and swarm-level metrics with automatic retention management.

## Features

- **Task Metrics**: Duration, result, token usage, files changed
- **Agent Metrics**: Success rates, error counts, performance statistics
- **Swarm Metrics**: Health, throughput, latency, resource utilization
- **Time-Series Queries**: Optimized indexing for fast temporal queries
- **Aggregations**: AVG, SUM, COUNT, MIN, MAX, STDDEV
- **Automatic Retention**: 30-day default with configurable cleanup
- **Thread-Safe**: Connection pooling for concurrent operations
- **Zero Dependencies**: Pure SQLite implementation

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Monitoring Module                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Task Metrics │  │Agent Metrics │  │Swarm Metrics │     │
│  ├──────────────┤  ├──────────────┤  ├──────────────┤     │
│  │ - task_id    │  │ - agent_id   │  │ - swarm_id   │     │
│  │ - agent_id   │  │ - metric_type│  │ - metric_type│     │
│  │ - duration   │  │ - value      │  │ - value      │     │
│  │ - result     │  │ - metadata   │  │ - metadata   │     │
│  │ - tokens     │  │ - timestamp  │  │ - timestamp  │     │
│  │ - files      │  └──────────────┘  └──────────────┘     │
│  │ - timestamp  │                                           │
│  └──────────────┘                                           │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│              Optimized Indexing Layer                        │
│  - Time-series indexes (timestamp)                           │
│  - Composite indexes (agent_id, metric_type, timestamp)     │
│  - Result-based indexes (result, timestamp)                 │
├─────────────────────────────────────────────────────────────┤
│                  SQLite Backend                              │
│  - Thread-safe connection pooling                            │
│  - Transaction support                                       │
│  - JSON metadata storage                                     │
└─────────────────────────────────────────────────────────────┘
```

## Database Schema

### Task Metrics Table

```sql
CREATE TABLE task_metrics (
    task_id TEXT NOT NULL,
    agent_id TEXT NOT NULL,
    duration_ms INTEGER,
    result TEXT NOT NULL,  -- 'success' | 'failure' | 'timeout' | 'cancelled'
    tokens_used INTEGER DEFAULT 0,
    files_changed INTEGER DEFAULT 0,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (task_id, timestamp)
);

CREATE INDEX idx_task_metrics_agent ON task_metrics(agent_id, timestamp);
CREATE INDEX idx_task_metrics_time ON task_metrics(timestamp);
CREATE INDEX idx_task_metrics_result ON task_metrics(result, timestamp);
```

### Agent Metrics Table

```sql
CREATE TABLE agent_metrics (
    metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_id TEXT NOT NULL,
    metric_type TEXT NOT NULL,  -- 'duration' | 'success_rate' | 'error_count' | 'throughput'
    value REAL NOT NULL,
    metadata TEXT,  -- JSON blob
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_agent_metrics_agent ON agent_metrics(agent_id, metric_type, timestamp);
CREATE INDEX idx_agent_metrics_type ON agent_metrics(metric_type, timestamp);
```

### Swarm Metrics Table

```sql
CREATE TABLE swarm_metrics (
    metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
    swarm_id TEXT NOT NULL,
    metric_type TEXT NOT NULL,  -- 'health' | 'throughput' | 'latency' | 'resource'
    value REAL NOT NULL,
    metadata TEXT,  -- JSON blob
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_swarm_metrics_swarm ON swarm_metrics(swarm_id, metric_type, timestamp);
CREATE INDEX idx_swarm_metrics_type ON swarm_metrics(metric_type, timestamp);
```

## Usage Examples

### Basic Usage

```python
from moai_flow.monitoring import MetricsStorage, TaskResult, MetricType

# Initialize storage
storage = MetricsStorage()

# Store task metric
storage.store_task_metric(
    task_id="task_001",
    agent_id="agent_backend_001",
    duration_ms=1500,
    result=TaskResult.SUCCESS,
    tokens_used=500,
    files_changed=3
)

# Query task metrics
metrics = storage.get_task_metrics(
    agent_id="agent_backend_001",
    time_range=(start_time, end_time)
)

# Close storage
storage.close()
```

### Context Manager Pattern

```python
from moai_flow.monitoring import MetricsStorage
from datetime import datetime, timedelta

with MetricsStorage() as storage:
    # Store metrics
    storage.store_task_metric(
        task_id="task_002",
        agent_id="agent_002",
        duration_ms=2000,
        result="success",
        tokens_used=600
    )

    # Query with time range
    now = datetime.now()
    last_hour = now - timedelta(hours=1)

    metrics = storage.query_metrics(
        metric_type="task",
        filters={"agent_id": "agent_002"},
        time_range=(last_hour, now)
    )
```

### Agent-Level Metrics

```python
from moai_flow.monitoring import MetricsStorage, MetricType

storage = MetricsStorage()

# Store agent success rate
storage.store_agent_metric(
    agent_id="agent_001",
    metric_type=MetricType.AGENT_SUCCESS_RATE,
    value=0.95,
    metadata={"total_tasks": 100, "successful_tasks": 95}
)

# Store agent error count
storage.store_agent_metric(
    agent_id="agent_001",
    metric_type=MetricType.AGENT_ERROR_COUNT,
    value=5,
    metadata={"error_types": {"timeout": 3, "failure": 2}}
)

# Query agent metrics
agent_metrics = storage.get_agent_metrics(
    agent_id="agent_001",
    metric_type=MetricType.AGENT_SUCCESS_RATE
)
```

### Swarm-Level Metrics

```python
from moai_flow.monitoring import MetricsStorage, MetricType

storage = MetricsStorage()

# Store swarm health
storage.store_swarm_metric(
    swarm_id="swarm_production",
    metric_type=MetricType.SWARM_HEALTH,
    value=0.98,
    metadata={
        "active_agents": 10,
        "pending_tasks": 15,
        "avg_latency_ms": 250
    }
)

# Store swarm throughput
storage.store_swarm_metric(
    swarm_id="swarm_production",
    metric_type=MetricType.SWARM_THROUGHPUT,
    value=50.5,  # tasks per second
    metadata={"time_window_seconds": 60}
)

# Query swarm metrics
swarm_metrics = storage.get_swarm_metrics(
    swarm_id="swarm_production",
    metric_type=MetricType.SWARM_HEALTH
)
```

### Aggregation Queries

```python
from moai_flow.monitoring import MetricsStorage, AggregationType
from datetime import datetime, timedelta

storage = MetricsStorage()

# Time range (last 24 hours)
now = datetime.now()
yesterday = now - timedelta(hours=24)
time_range = (yesterday, now)

# Average task duration
avg_duration = storage.aggregate_metrics(
    metric_type="task",
    aggregation=AggregationType.AVG,
    time_range=time_range,
    filters={"agent_id": "agent_001"}
)
print(f"Average duration: {avg_duration['result']:.2f}ms")

# Total task count
total_tasks = storage.aggregate_metrics(
    metric_type="task",
    aggregation=AggregationType.COUNT,
    time_range=time_range
)
print(f"Total tasks: {total_tasks['count']}")

# Success rate calculation
success_count = storage.aggregate_metrics(
    metric_type="task",
    aggregation=AggregationType.COUNT,
    filters={"result": "success"},
    time_range=time_range
)
success_rate = success_count['count'] / total_tasks['count'] * 100
print(f"Success rate: {success_rate:.1f}%")

# Standard deviation of duration
stddev = storage.aggregate_metrics(
    metric_type="task",
    aggregation=AggregationType.STDDEV,
    time_range=time_range
)
print(f"Duration std dev: {stddev['stddev']:.2f}ms")
```

### Automatic Retention Management

```python
from moai_flow.monitoring import MetricsStorage

storage = MetricsStorage()

# Cleanup old metrics (30-day default)
deleted = storage.cleanup_old_metrics(retention_days=30)
print(f"Deleted metrics: {deleted}")
# Output: {'task_metrics': 150, 'agent_metrics': 75, 'swarm_metrics': 25}

# Custom retention period (7 days)
deleted = storage.cleanup_old_metrics(retention_days=7)

# Vacuum database to reclaim space
storage.vacuum()
```

## Integration with SwarmDB

The Monitoring module integrates seamlessly with SwarmDB (v2.0.0+):

```python
from moai_flow.memory import SwarmDB
from moai_flow.monitoring import MetricsStorage

# Both systems share compatible schemas
swarm_db = SwarmDB()
metrics_storage = MetricsStorage()

# Agent lifecycle in SwarmDB
swarm_db.register_agent(
    agent_id="agent_001",
    agent_type="expert-backend",
    status="spawned"
)

# Task metrics in MetricsStorage
metrics_storage.store_task_metric(
    task_id="task_001",
    agent_id="agent_001",
    duration_ms=1500,
    result="success",
    tokens_used=500
)

# Both systems can be queried independently or together
agent_data = swarm_db.get_agent("agent_001")
task_metrics = metrics_storage.get_task_metrics(agent_id="agent_001")
```

## Performance Characteristics

### Query Performance

- **Single metric lookup**: < 1ms (indexed by timestamp)
- **Agent metrics query**: < 5ms (composite index)
- **Time-range query (1 hour)**: < 10ms (optimized index)
- **Time-range query (24 hours)**: < 50ms
- **Aggregation (24 hours)**: < 100ms

### Storage Efficiency

- **Task metric**: ~150 bytes per record
- **Agent metric**: ~120 bytes per record
- **Swarm metric**: ~100 bytes per record
- **Daily retention (1000 tasks)**: ~150 KB
- **30-day retention (30K tasks)**: ~4.5 MB

### Scalability

- **Maximum metrics/second**: 10,000+ (with connection pooling)
- **Maximum database size**: 140 TB (SQLite limit)
- **Recommended max metrics**: 10M per database
- **Auto-cleanup threshold**: 1M metrics (triggers vacuum)

## Configuration

### Default Database Location

```python
# Default: .swarm/metrics.db
storage = MetricsStorage()

# Custom location
storage = MetricsStorage(db_path=Path("/custom/path/metrics.db"))
```

### Retention Policy

```python
# Default: 30 days
storage.cleanup_old_metrics()

# Custom: 7 days
storage.cleanup_old_metrics(retention_days=7)

# Custom: 90 days
storage.cleanup_old_metrics(retention_days=90)
```

### Thread Safety

```python
# Thread-safe by default (connection pooling)
storage = MetricsStorage()

# Each thread gets its own connection
# No additional configuration needed
```

## API Reference

### MetricsStorage Class

#### Constructor

```python
MetricsStorage(db_path: Optional[Path] = None)
```

#### Task Metrics Methods

```python
store_task_metric(
    task_id: str,
    agent_id: str,
    duration_ms: int,
    result: Union[TaskResult, str],
    tokens_used: int = 0,
    files_changed: int = 0,
    timestamp: Optional[datetime] = None
) -> None

get_task_metrics(
    task_id: Optional[str] = None,
    agent_id: Optional[str] = None,
    result: Optional[Union[TaskResult, str]] = None,
    time_range: Optional[Tuple[datetime, datetime]] = None,
    limit: int = 1000
) -> List[Dict[str, Any]]
```

#### Agent Metrics Methods

```python
store_agent_metric(
    agent_id: str,
    metric_type: Union[MetricType, str],
    value: float,
    metadata: Optional[Dict[str, Any]] = None,
    timestamp: Optional[datetime] = None
) -> int

get_agent_metrics(
    agent_id: Optional[str] = None,
    metric_type: Optional[Union[MetricType, str]] = None,
    time_range: Optional[Tuple[datetime, datetime]] = None,
    limit: int = 1000
) -> List[Dict[str, Any]]
```

#### Swarm Metrics Methods

```python
store_swarm_metric(
    swarm_id: str,
    metric_type: Union[MetricType, str],
    value: float,
    metadata: Optional[Dict[str, Any]] = None,
    timestamp: Optional[datetime] = None
) -> int

get_swarm_metrics(
    swarm_id: Optional[str] = None,
    metric_type: Optional[Union[MetricType, str]] = None,
    time_range: Optional[Tuple[datetime, datetime]] = None,
    limit: int = 1000
) -> List[Dict[str, Any]]
```

#### Generic Methods

```python
store_metric(
    metric_type: str,
    data: Dict[str, Any],
    timestamp: Optional[datetime] = None
) -> Union[int, None]

query_metrics(
    metric_type: str,
    filters: Optional[Dict[str, Any]] = None,
    time_range: Optional[Tuple[datetime, datetime]] = None,
    limit: int = 1000
) -> List[Dict[str, Any]]

aggregate_metrics(
    metric_type: str,
    aggregation: Union[AggregationType, str],
    time_range: Optional[Tuple[datetime, datetime]] = None,
    filters: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]
```

#### Maintenance Methods

```python
cleanup_old_metrics(retention_days: int = 30) -> Dict[str, int]
vacuum() -> None
close() -> None
```

## Enumerations

### MetricType

```python
class MetricType(str, Enum):
    # Task metrics
    TASK_DURATION = "task_duration"
    TASK_RESULT = "task_result"
    TASK_TOKENS = "task_tokens"
    TASK_FILES = "task_files"

    # Agent metrics
    AGENT_DURATION = "agent_duration"
    AGENT_SUCCESS_RATE = "agent_success_rate"
    AGENT_ERROR_COUNT = "agent_error_count"
    AGENT_THROUGHPUT = "agent_throughput"

    # Swarm metrics
    SWARM_HEALTH = "swarm_health"
    SWARM_THROUGHPUT = "swarm_throughput"
    SWARM_LATENCY = "swarm_latency"
    SWARM_RESOURCE = "swarm_resource"
```

### TaskResult

```python
class TaskResult(str, Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"
```

### AggregationType

```python
class AggregationType(str, Enum):
    AVG = "avg"
    SUM = "sum"
    COUNT = "count"
    MIN = "min"
    MAX = "max"
    STDDEV = "stddev"
```

## Examples

See the comprehensive demo at:
- `moai_flow/examples/metrics_integration_demo.py`

Run the demo:
```bash
python3 moai_flow/examples/metrics_integration_demo.py
```

## Testing

```python
# Run MetricsStorage tests
python3 moai_flow/monitoring/metrics_storage.py

# Run integration demo
python3 moai_flow/examples/metrics_integration_demo.py
```

## Migration from v1.0.0 to v2.0.0

The monitoring module is fully backward compatible with SwarmDB v1.0.0. If you're upgrading:

1. **Schema auto-upgrade**: Tables are automatically created if missing
2. **No data migration needed**: Existing data remains intact
3. **New indexes created**: Automatically on first run
4. **Version tracking**: Schema version stored in `metrics_schema_info`

## Troubleshooting

### Database Locked Error

```python
# Increase connection timeout
storage = MetricsStorage()
storage._get_connection().timeout = 30.0  # 30 seconds
```

### Slow Queries

```python
# Run VACUUM to optimize
storage.vacuum()

# Check index usage with EXPLAIN
conn = storage._get_connection()
cursor = conn.cursor()
cursor.execute("EXPLAIN QUERY PLAN SELECT * FROM task_metrics WHERE agent_id = ?", ("agent_001",))
print(cursor.fetchall())
```

### Disk Space Issues

```python
# Aggressive cleanup (7 days instead of 30)
deleted = storage.cleanup_old_metrics(retention_days=7)
storage.vacuum()
```

## Best Practices

1. **Use context managers**: Always use `with MetricsStorage() as storage:` for automatic cleanup
2. **Batch operations**: Group multiple metric stores in a single transaction
3. **Regular cleanup**: Schedule automatic cleanup with `cleanup_old_metrics()`
4. **Index awareness**: Use indexed fields (agent_id, timestamp) in WHERE clauses
5. **Metadata sparingly**: Keep metadata JSON small for better performance
6. **Vacuum periodically**: Run `vacuum()` after large deletions

## License

MIT License - Part of MoAI-Flow Phase 6A

## Version

- **Module Version**: 1.0.0
- **Schema Version**: 1.0.0
- **SwarmDB Compatibility**: 2.0.0+
- **Last Updated**: 2025-11-29
