#!/usr/bin/env python3
"""
MetricsCollector - Phase 6A Observability Foundation for MoAI-Flow

Collects performance metrics for swarm coordination:
- Task metrics: duration_ms, success/failure, tokens_used, files_changed
- Agent metrics: tasks_completed, avg_duration, error_rate, agent_type
- Swarm metrics: topology_health, message_throughput, consensus_latency

Features:
- Async collection (non-blocking, <1ms overhead)
- Configurable enable/disable
- Integration with SwarmCoordinator
- MetricsStorage persistence layer
- Graceful degradation on storage failures

Version: 1.0.0
Phase: 6A (Weeks 1-2) - Observability Infrastructure
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from queue import Queue, Empty
from threading import Thread, Lock
from typing import Any, Dict, List, Optional, Tuple
from statistics import mean, median


# ============================================================================
# Metric Type Definitions
# ============================================================================

class MetricType(Enum):
    """Metric type enumeration"""
    TASK = "task"
    AGENT = "agent"
    SWARM = "swarm"


class TaskResult(Enum):
    """Task execution result"""
    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL = "partial"
    TIMEOUT = "timeout"


# ============================================================================
# Metric Data Structures
# ============================================================================

@dataclass
class TaskMetric:
    """
    Task execution metric

    Tracks individual task performance including duration,
    token usage, and file modifications.
    """
    task_id: str
    agent_id: str
    duration_ms: float
    result: TaskResult
    tokens_used: int = 0
    files_changed: int = 0
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data["result"] = self.result.value
        return data


@dataclass
class AgentMetric:
    """
    Agent performance metric

    Aggregates agent performance over time including
    task completion rates and average durations.
    """
    agent_id: str
    metric_type: str  # "tasks_completed", "avg_duration", "error_rate"
    value: float
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class SwarmMetric:
    """
    Swarm coordination metric

    Tracks swarm-level coordination health including
    topology status and message throughput.
    """
    swarm_id: str
    metric_type: str  # "topology_health", "message_throughput", "consensus_latency"
    value: float
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


# ============================================================================
# MetricsCollector Implementation
# ============================================================================

class MetricsCollector:
    """
    Performance metrics collection for MoAI-Flow swarm coordination.

    Collects three types of metrics:
    1. Task metrics: Individual task execution performance
    2. Agent metrics: Per-agent performance aggregates
    3. Swarm metrics: Coordination topology health

    Features:
    - Async collection via background thread (<1ms overhead)
    - Configurable enable/disable via constructor
    - Automatic aggregation and statistics calculation
    - Graceful degradation if storage fails
    - Thread-safe metric recording

    Example:
        >>> storage = MetricsStorage()
        >>> collector = MetricsCollector(storage, async_mode=True)
        >>> collector.record_task_metric(
        ...     task_id="task-001",
        ...     agent_id="expert-backend",
        ...     duration_ms=3500,
        ...     result=TaskResult.SUCCESS,
        ...     tokens_used=25000,
        ...     files_changed=3
        ... )
        >>> stats = collector.get_task_stats(agent_id="expert-backend")
        >>> print(stats["avg_duration_ms"])
        3500
    """

    def __init__(
        self,
        storage: Optional[Any] = None,
        async_mode: bool = True,
        enabled: bool = True,
        queue_size: int = 1000
    ):
        """
        Initialize MetricsCollector

        Args:
            storage: MetricsStorage instance for persistence (optional)
            async_mode: Enable async background collection (default: True)
            enabled: Enable/disable metrics collection (default: True)
            queue_size: Maximum async queue size (default: 1000)
        """
        self.storage = storage
        self.async_mode = async_mode
        self.enabled = enabled
        self.logger = logging.getLogger(__name__)

        # In-memory metric storage
        self._task_metrics: List[TaskMetric] = []
        self._agent_metrics: List[AgentMetric] = []
        self._swarm_metrics: List[SwarmMetric] = []

        # Thread-safe access
        self._lock = Lock()

        # Async collection queue
        if self.async_mode:
            self._queue: Queue = Queue(maxsize=queue_size)
            self._worker_thread: Optional[Thread] = None
            self._shutdown = False
            self._start_async_worker()

        # Performance tracking
        self._collection_times: List[float] = []

        self.logger.info(
            f"MetricsCollector initialized "
            f"(async={async_mode}, enabled={enabled})"
        )

    # ========================================================================
    # Task Metrics
    # ========================================================================

    def record_task_metric(
        self,
        task_id: str,
        agent_id: str,
        duration_ms: float,
        result: TaskResult,
        tokens_used: int = 0,
        files_changed: int = 0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Record task execution metric

        Args:
            task_id: Unique task identifier
            agent_id: Agent that executed the task
            duration_ms: Task duration in milliseconds
            result: Task execution result (SUCCESS, FAILURE, PARTIAL, TIMEOUT)
            tokens_used: Total tokens consumed (default: 0)
            files_changed: Number of files modified (default: 0)
            metadata: Additional task metadata (optional)

        Example:
            >>> collector.record_task_metric(
            ...     task_id="task-001",
            ...     agent_id="expert-backend",
            ...     duration_ms=3500,
            ...     result=TaskResult.SUCCESS,
            ...     tokens_used=25000,
            ...     files_changed=3,
            ...     metadata={"spec_id": "SPEC-001"}
            ... )
        """
        if not self.enabled:
            return

        start_time = time.perf_counter()

        metric = TaskMetric(
            task_id=task_id,
            agent_id=agent_id,
            duration_ms=duration_ms,
            result=result,
            tokens_used=tokens_used,
            files_changed=files_changed,
            metadata=metadata or {}
        )

        if self.async_mode:
            # Queue for async processing
            try:
                self._queue.put_nowait((MetricType.TASK, metric))
            except Exception as e:
                self.logger.warning(f"Async queue full, recording synchronously: {e}")
                self._record_task_sync(metric)
        else:
            # Synchronous recording
            self._record_task_sync(metric)

        # Track collection overhead
        collection_time = (time.perf_counter() - start_time) * 1000  # ms
        self._collection_times.append(collection_time)

        if collection_time > 1.0:
            self.logger.warning(
                f"Metric collection took {collection_time:.2f}ms (target: <1ms)"
            )

    def _record_task_sync(self, metric: TaskMetric) -> None:
        """Record task metric synchronously (internal)"""
        with self._lock:
            self._task_metrics.append(metric)

        # Persist to storage if available
        if self.storage:
            try:
                self.storage.save_task_metric(metric.to_dict())
            except Exception as e:
                self.logger.error(f"Failed to persist task metric: {e}")
                # Graceful degradation: continue with in-memory only

    # ========================================================================
    # Agent Metrics
    # ========================================================================

    def record_agent_metric(
        self,
        agent_id: str,
        metric_type: str,
        value: float,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Record agent performance metric

        Args:
            agent_id: Unique agent identifier
            metric_type: Type of metric ("tasks_completed", "avg_duration", "error_rate")
            value: Metric value
            metadata: Additional metadata (optional)

        Example:
            >>> collector.record_agent_metric(
            ...     agent_id="expert-backend",
            ...     metric_type="tasks_completed",
            ...     value=45
            ... )
        """
        if not self.enabled:
            return

        metric = AgentMetric(
            agent_id=agent_id,
            metric_type=metric_type,
            value=value,
            metadata=metadata or {}
        )

        if self.async_mode:
            try:
                self._queue.put_nowait((MetricType.AGENT, metric))
            except Exception as e:
                self.logger.warning(f"Async queue full, recording synchronously: {e}")
                self._record_agent_sync(metric)
        else:
            self._record_agent_sync(metric)

    def _record_agent_sync(self, metric: AgentMetric) -> None:
        """Record agent metric synchronously (internal)"""
        with self._lock:
            self._agent_metrics.append(metric)

        if self.storage:
            try:
                self.storage.save_agent_metric(metric.to_dict())
            except Exception as e:
                self.logger.error(f"Failed to persist agent metric: {e}")

    # ========================================================================
    # Swarm Metrics
    # ========================================================================

    def record_swarm_metric(
        self,
        swarm_id: str,
        metric_type: str,
        value: float,
        timestamp: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Record swarm coordination metric

        Args:
            swarm_id: Unique swarm identifier
            metric_type: Type of metric ("topology_health", "message_throughput", "consensus_latency")
            value: Metric value
            timestamp: Metric timestamp (ISO format, optional)
            metadata: Additional metadata (optional)

        Example:
            >>> collector.record_swarm_metric(
            ...     swarm_id="swarm-001",
            ...     metric_type="topology_health",
            ...     value=0.95
            ... )
        """
        if not self.enabled:
            return

        metric = SwarmMetric(
            swarm_id=swarm_id,
            metric_type=metric_type,
            value=value,
            timestamp=timestamp or datetime.utcnow().isoformat() + "Z",
            metadata=metadata or {}
        )

        if self.async_mode:
            try:
                self._queue.put_nowait((MetricType.SWARM, metric))
            except Exception as e:
                self.logger.warning(f"Async queue full, recording synchronously: {e}")
                self._record_swarm_sync(metric)
        else:
            self._record_swarm_sync(metric)

    def _record_swarm_sync(self, metric: SwarmMetric) -> None:
        """Record swarm metric synchronously (internal)"""
        with self._lock:
            self._swarm_metrics.append(metric)

        if self.storage:
            try:
                self.storage.save_swarm_metric(metric.to_dict())
            except Exception as e:
                self.logger.error(f"Failed to persist swarm metric: {e}")

    # ========================================================================
    # Statistics and Aggregation
    # ========================================================================

    def get_task_stats(
        self,
        agent_id: Optional[str] = None,
        time_range: Optional[Tuple[datetime, datetime]] = None,
        aggregation: str = "avg"
    ) -> Dict[str, Any]:
        """
        Get task statistics with optional filtering

        Args:
            agent_id: Filter by agent (optional)
            time_range: Time range (start_time, end_time) (optional)
            aggregation: Aggregation method ("avg", "median", "min", "max") (default: "avg")

        Returns:
            Dictionary with statistics:
            {
                "count": int,
                "avg_duration_ms": float,
                "median_duration_ms": float,
                "min_duration_ms": float,
                "max_duration_ms": float,
                "success_rate": float,
                "total_tokens": int,
                "total_files_changed": int,
                "results_breakdown": {"success": int, "failure": int, ...}
            }

        Example:
            >>> stats = collector.get_task_stats(agent_id="expert-backend")
            >>> print(f"Average duration: {stats['avg_duration_ms']:.0f}ms")
            Average duration: 3500ms
        """
        with self._lock:
            metrics = list(self._task_metrics)

        # Filter by agent_id
        if agent_id:
            metrics = [m for m in metrics if m.agent_id == agent_id]

        # Filter by time_range
        if time_range:
            start_time, end_time = time_range
            metrics = [
                m for m in metrics
                if start_time <= datetime.fromisoformat(m.timestamp.replace("Z", "")) <= end_time
            ]

        if not metrics:
            return {
                "count": 0,
                "avg_duration_ms": 0.0,
                "median_duration_ms": 0.0,
                "min_duration_ms": 0.0,
                "max_duration_ms": 0.0,
                "success_rate": 0.0,
                "total_tokens": 0,
                "total_files_changed": 0,
                "results_breakdown": {}
            }

        # Calculate statistics
        durations = [m.duration_ms for m in metrics]

        success_count = sum(1 for m in metrics if m.result == TaskResult.SUCCESS)

        results_breakdown: Dict[str, int] = {}
        for m in metrics:
            result_key = m.result.value
            results_breakdown[result_key] = results_breakdown.get(result_key, 0) + 1

        return {
            "count": len(metrics),
            "avg_duration_ms": mean(durations),
            "median_duration_ms": median(durations),
            "min_duration_ms": min(durations),
            "max_duration_ms": max(durations),
            "success_rate": (success_count / len(metrics)) * 100 if metrics else 0.0,
            "total_tokens": sum(m.tokens_used for m in metrics),
            "total_files_changed": sum(m.files_changed for m in metrics),
            "results_breakdown": results_breakdown
        }

    def get_agent_performance(
        self,
        agent_id: str,
        metrics: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Get agent performance summary

        Args:
            agent_id: Agent identifier
            metrics: List of metric types to include (default: ["duration", "success_rate"])

        Returns:
            Dictionary with agent performance:
            {
                "agent_id": str,
                "tasks_completed": int,
                "success_rate": float,
                "avg_duration_ms": float,
                "error_rate": float,
                "total_tokens_used": int
            }

        Example:
            >>> perf = collector.get_agent_performance("expert-backend")
            >>> print(f"Success rate: {perf['success_rate']:.1f}%")
            Success rate: 89.0%
        """
        metrics_filter = metrics or ["duration", "success_rate"]

        # Get task stats for this agent
        task_stats = self.get_task_stats(agent_id=agent_id)

        # Calculate error rate
        error_count = task_stats.get("results_breakdown", {}).get("failure", 0)
        total_tasks = task_stats.get("count", 0)
        error_rate = (error_count / total_tasks * 100) if total_tasks > 0 else 0.0

        return {
            "agent_id": agent_id,
            "tasks_completed": total_tasks,
            "success_rate": task_stats.get("success_rate", 0.0),
            "avg_duration_ms": task_stats.get("avg_duration_ms", 0.0),
            "error_rate": error_rate,
            "total_tokens_used": task_stats.get("total_tokens", 0)
        }

    def get_swarm_health(
        self,
        swarm_id: str,
        include_history: bool = False
    ) -> Dict[str, Any]:
        """
        Get swarm coordination health status

        Args:
            swarm_id: Swarm identifier
            include_history: Include historical metrics (default: False)

        Returns:
            Dictionary with swarm health:
            {
                "swarm_id": str,
                "topology_health": float,
                "message_throughput": float,
                "consensus_latency_ms": float,
                "last_updated": str,
                "history": List[Dict] (if include_history=True)
            }

        Example:
            >>> health = collector.get_swarm_health("swarm-001")
            >>> print(f"Topology health: {health['topology_health']:.2f}")
            Topology health: 0.95
        """
        with self._lock:
            metrics = [m for m in self._swarm_metrics if m.swarm_id == swarm_id]

        if not metrics:
            return {
                "swarm_id": swarm_id,
                "topology_health": 0.0,
                "message_throughput": 0.0,
                "consensus_latency_ms": 0.0,
                "last_updated": None,
                "history": [] if include_history else None
            }

        # Get latest value for each metric type
        latest_metrics: Dict[str, SwarmMetric] = {}
        for metric in sorted(metrics, key=lambda m: m.timestamp):
            latest_metrics[metric.metric_type] = metric

        result = {
            "swarm_id": swarm_id,
            "topology_health": latest_metrics.get("topology_health", SwarmMetric(swarm_id, "topology_health", 0.0)).value,
            "message_throughput": latest_metrics.get("message_throughput", SwarmMetric(swarm_id, "message_throughput", 0.0)).value,
            "consensus_latency_ms": latest_metrics.get("consensus_latency", SwarmMetric(swarm_id, "consensus_latency", 0.0)).value,
            "last_updated": max((m.timestamp for m in metrics), default=None)
        }

        if include_history:
            result["history"] = [m.to_dict() for m in metrics]

        return result

    # ========================================================================
    # Async Worker Thread
    # ========================================================================

    def _start_async_worker(self) -> None:
        """Start background worker thread for async collection"""
        self._worker_thread = Thread(
            target=self._async_worker,
            name="MetricsCollector-Worker",
            daemon=True
        )
        self._worker_thread.start()
        self.logger.debug("Async worker thread started")

    def _async_worker(self) -> None:
        """Background worker thread that processes metric queue"""
        while not self._shutdown:
            try:
                # Get metric from queue with timeout
                metric_type, metric = self._queue.get(timeout=0.1)

                # Process based on type
                if metric_type == MetricType.TASK:
                    self._record_task_sync(metric)
                elif metric_type == MetricType.AGENT:
                    self._record_agent_sync(metric)
                elif metric_type == MetricType.SWARM:
                    self._record_swarm_sync(metric)

                self._queue.task_done()

            except Empty:
                # Timeout, continue loop
                continue
            except Exception as e:
                self.logger.error(f"Error in async worker: {e}")

    def shutdown(self) -> None:
        """
        Shutdown metrics collector and flush pending metrics

        Waits for async queue to drain before shutting down.
        """
        if self.async_mode:
            self.logger.info("Shutting down async worker...")

            # Wait for queue to drain
            self._queue.join()

            # Signal shutdown
            self._shutdown = True

            # Wait for worker thread
            if self._worker_thread:
                self._worker_thread.join(timeout=5.0)

            self.logger.info("Async worker shutdown complete")

    # ========================================================================
    # Performance Monitoring
    # ========================================================================

    def get_collection_overhead(self) -> Dict[str, float]:
        """
        Get metric collection performance overhead

        Returns:
            Dictionary with overhead statistics:
            {
                "avg_collection_time_ms": float,
                "max_collection_time_ms": float,
                "total_collections": int
            }
        """
        if not self._collection_times:
            return {
                "avg_collection_time_ms": 0.0,
                "max_collection_time_ms": 0.0,
                "total_collections": 0
            }

        return {
            "avg_collection_time_ms": mean(self._collection_times),
            "max_collection_time_ms": max(self._collection_times),
            "total_collections": len(self._collection_times)
        }

    def __del__(self):
        """Cleanup on object destruction"""
        try:
            self.shutdown()
        except Exception:
            pass


# ============================================================================
# Mock MetricsStorage (Placeholder)
# ============================================================================

class MetricsStorage:
    """
    Mock MetricsStorage implementation (placeholder)

    Will be implemented by parallel agent in Phase 6A.
    This class ensures MetricsCollector can function independently.
    """

    def save_task_metric(self, metric: Dict[str, Any]) -> None:
        """Save task metric to persistent storage"""
        pass

    def save_agent_metric(self, metric: Dict[str, Any]) -> None:
        """Save agent metric to persistent storage"""
        pass

    def save_swarm_metric(self, metric: Dict[str, Any]) -> None:
        """Save swarm metric to persistent storage"""
        pass


# ============================================================================
# Module Exports
# ============================================================================

__all__ = [
    "MetricsCollector",
    "MetricsStorage",
    "TaskMetric",
    "AgentMetric",
    "SwarmMetric",
    "MetricType",
    "TaskResult"
]
