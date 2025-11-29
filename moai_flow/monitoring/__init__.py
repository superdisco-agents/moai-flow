"""
Monitoring module for MoAI-Flow Phase 6A Observability.

This module provides comprehensive observability infrastructure for swarm coordination:
- MetricsCollector: <1ms overhead async metrics collection
- MetricsStorage: SQLite-backed metrics persistence with optimized querying
- HeartbeatMonitor: Active heartbeat monitoring with failure detection
- HealthReporter: Comprehensive health report generation and export

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

Example:
    >>> from moai_flow.monitoring import MetricsCollector, TaskResult, HealthReporter
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
"""

from .metrics_storage import MetricsStorage, MetricType, AggregationType
from .heartbeat_monitor import HeartbeatMonitor, HealthState
from .metrics_collector import (
    MetricsCollector,
    TaskMetric,
    AgentMetric,
    SwarmMetric,
    TaskResult
)
from .health_reporter import HealthReporter, Alert, AlertSeverity

__all__ = [
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
    "TaskResult"
]
