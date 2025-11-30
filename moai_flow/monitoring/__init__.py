"""
Monitoring module for MoAI-Flow Phase 6A & 7 Observability.

This module provides comprehensive observability infrastructure for swarm coordination:

Core Components:
- MetricsCollector: <1ms overhead async metrics collection
- MetricsStorage: SQLite-backed metrics persistence with optimized querying
- HeartbeatMonitor: Active heartbeat monitoring with failure detection
- HealthReporter: Comprehensive health report generation and export

Storage Components (Phase 7):
- MetricsPersistence: Advanced SQLite persistence with compression & retention
- MetricsQuery: Query interface with aggregation support (10 methods)
- MetricsExporter: Multi-format export (JSON, CSV, Prometheus, Grafana)

Key Features:
- Task metrics tracking (duration, result, token usage)
- Agent metrics tracking (success rates, error counts)
- Swarm metrics tracking (health, throughput, latency)
- Active heartbeat monitoring with failure detection
- Health state transitions (HEALTHY → DEGRADED → CRITICAL → FAILED)
- Comprehensive health reports (markdown/JSON formats)
- Alert detection and notification
- Uptime calculation (agent and swarm level)
- Optimized indexing for fast queries
- Automatic retention management (30-day default)
- Thread-safe operations
- Write buffering and batch operations
- Data compression for historical metrics
- Multi-format export capabilities

Example:
    >>> from moai_flow.monitoring import (
    ...     MetricsCollector, MetricsStorage, TaskResult,
    ...     HeartbeatMonitor, HealthReporter, HealthState
    ... )
    >>> storage = MetricsStorage()
    >>> collector = MetricsCollector(storage, async_mode=True)
    >>> collector.record_task_metric(
    ...     task_id="task-001",
    ...     agent_id="expert-backend",
    ...     duration_ms=3500,
    ...     result=TaskResult.SUCCESS,
    ...     tokens_used=25000
    ... )
    >>>
    >>> # Generate health report
    >>> monitor = HeartbeatMonitor()
    >>> reporter = HealthReporter(monitor, collector)
    >>> report = reporter.generate_health_report("swarm-001", format="markdown")
    >>> print(report)

Phase 7 Storage Example:
    >>> from moai_flow.monitoring.storage import (
    ...     MetricsPersistence, MetricsQuery, MetricsExporter,
    ...     ExportFormat, QueryFilter
    ... )
    >>> persistence = MetricsPersistence()
    >>> persistence.write_task_metric(
    ...     task_id="task_001", agent_id="agent_001",
    ...     duration_ms=1500, tokens_used=500, success=True
    ... )
    >>> query = MetricsQuery()
    >>> filter = QueryFilter(agent_id="agent_001", limit=100)
    >>> metrics = query.get_task_metrics(filter)
"""

# Core monitoring components
from .metrics_storage import MetricsStorage, MetricType, AggregationType, TaskResult as StorageTaskResult
from .heartbeat_monitor import HeartbeatMonitor, HealthState
from .metrics_collector import (
    MetricsCollector,
    TaskMetric,
    AgentMetric,
    SwarmMetric,
    TaskResult,
    MetricType as CollectorMetricType
)
from .health_reporter import HealthReporter, Alert, AlertSeverity

# Storage package (Phase 7) - re-exported for convenience
from .storage import (
    MetricsPersistence,
    RetentionPolicy,
    CompressionConfig,
    MetricsQuery,
    QueryFilter,
    AggregationFunc,
    MetricsExporter,
    ExportFormat,
)

__all__ = [
    # Core monitoring
    "MetricsCollector",
    "MetricsStorage",
    "MetricType",
    "AggregationType",
    "HeartbeatMonitor",
    "HealthState",
    "HealthReporter",
    "Alert",
    "AlertSeverity",
    "TaskMetric",
    "AgentMetric",
    "SwarmMetric",
    "TaskResult",
    "CollectorMetricType",
    "StorageTaskResult",

    # Storage package (Phase 7)
    "MetricsPersistence",
    "RetentionPolicy",
    "CompressionConfig",
    "MetricsQuery",
    "QueryFilter",
    "AggregationFunc",
    "MetricsExporter",
    "ExportFormat",
]
