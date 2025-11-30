#!/usr/bin/env python3
"""
MetricsStorage - SQLite-based Metrics Persistence for Phase 6A Observability

Provides comprehensive metrics storage and querying for:
- Task-level metrics (duration, result, token usage, files changed)
- Agent-level metrics (success rates, error counts, performance stats)
- Swarm-level metrics (health, throughput, latency, resource utilization)

Features:
- Optimized indexing for fast time-series queries
- Flexible aggregation support (avg, sum, count, min, max)
- Automatic retention management (30-day default)
- Thread-safe operations with connection pooling
- JSON metadata support for extensibility

Schema Version: 1.0.0
"""

import json
import logging
import sqlite3
import threading
from contextlib import contextmanager
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union


# ============================================================================
# Enums and Constants
# ============================================================================

class MetricType(str, Enum):
    """Metric type enumeration"""
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


class AggregationType(str, Enum):
    """Aggregation function enumeration"""
    AVG = "avg"
    SUM = "sum"
    COUNT = "count"
    MIN = "min"
    MAX = "max"
    STDDEV = "stddev"


class TaskResult(str, Enum):
    """Task result status enumeration"""
    SUCCESS = "success"
    FAILURE = "failure"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


# ============================================================================
# Extended SwarmDB Schema for Metrics
# ============================================================================

METRICS_SCHEMA_VERSION = "1.0.0"

METRICS_SCHEMA_SQL = """
-- Task metrics table
CREATE TABLE IF NOT EXISTS task_metrics (
    task_id TEXT NOT NULL,
    agent_id TEXT NOT NULL,
    duration_ms INTEGER,
    result TEXT NOT NULL,  -- 'success' | 'failure' | 'timeout' | 'cancelled'
    tokens_used INTEGER DEFAULT 0,
    files_changed INTEGER DEFAULT 0,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (task_id, timestamp)
);

CREATE INDEX IF NOT EXISTS idx_task_metrics_agent ON task_metrics(agent_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_task_metrics_time ON task_metrics(timestamp);
CREATE INDEX IF NOT EXISTS idx_task_metrics_result ON task_metrics(result, timestamp);

-- Agent metrics table
CREATE TABLE IF NOT EXISTS agent_metrics (
    metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_id TEXT NOT NULL,
    metric_type TEXT NOT NULL,  -- 'duration' | 'success_rate' | 'error_count' | 'throughput'
    value REAL NOT NULL,
    metadata TEXT,  -- JSON blob for additional data
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_agent_metrics_agent ON agent_metrics(agent_id, metric_type, timestamp);
CREATE INDEX IF NOT EXISTS idx_agent_metrics_type ON agent_metrics(metric_type, timestamp);

-- Swarm metrics table
CREATE TABLE IF NOT EXISTS swarm_metrics (
    metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
    swarm_id TEXT NOT NULL,
    metric_type TEXT NOT NULL,  -- 'health' | 'throughput' | 'latency' | 'resource'
    value REAL NOT NULL,
    metadata TEXT,  -- JSON blob for additional data
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_swarm_metrics_swarm ON swarm_metrics(swarm_id, metric_type, timestamp);
CREATE INDEX IF NOT EXISTS idx_swarm_metrics_type ON swarm_metrics(metric_type, timestamp);

-- Metrics schema version tracking
CREATE TABLE IF NOT EXISTS metrics_schema_info (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

INSERT OR REPLACE INTO metrics_schema_info (key, value) VALUES ('version', ?);
"""


# ============================================================================
# MetricsStorage Implementation
# ============================================================================

class MetricsStorage:
    """
    SQLite-based metrics persistence for Phase 6A observability.

    Provides comprehensive metrics storage and querying capabilities with:
    - Optimized time-series indexing
    - Flexible aggregation support
    - Automatic retention management
    - Thread-safe operations

    Example:
        >>> storage = MetricsStorage()
        >>> storage.store_task_metric(
        ...     task_id="task_001",
        ...     agent_id="agent_001",
        ...     duration_ms=1500,
        ...     result=TaskResult.SUCCESS,
        ...     tokens_used=500
        ... )
        >>> metrics = storage.query_metrics(
        ...     metric_type="task",
        ...     filters={"agent_id": "agent_001"},
        ...     time_range=(start_time, end_time)
        ... )
    """

    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize MetricsStorage.

        Args:
            db_path: Path to SQLite database file (defaults to .swarm/metrics.db)
        """
        self.db_path = db_path or Path.cwd() / ".swarm" / "metrics.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self.logger = logging.getLogger(__name__)
        self._lock = threading.RLock()
        self._connection_pool: Dict[int, sqlite3.Connection] = {}

        # Initialize schema
        self._initialize_schema()

    def _get_connection(self) -> sqlite3.Connection:
        """Get thread-local database connection"""
        thread_id = threading.get_ident()

        if thread_id not in self._connection_pool:
            conn = sqlite3.connect(
                str(self.db_path),
                check_same_thread=False,
                timeout=10.0
            )
            conn.row_factory = sqlite3.Row  # Enable dict-like row access
            self._connection_pool[thread_id] = conn

        return self._connection_pool[thread_id]

    def _initialize_schema(self) -> None:
        """Initialize metrics schema"""
        with self._lock:
            try:
                conn = self._get_connection()
                cursor = conn.cursor()

                # Execute schema with version
                for statement in METRICS_SCHEMA_SQL.split(';'):
                    statement = statement.strip()
                    if statement:
                        # Replace version placeholder
                        statement = statement.replace('?', f"'{METRICS_SCHEMA_VERSION}'")
                        cursor.execute(statement)

                conn.commit()
                self.logger.info(f"Initialized MetricsStorage schema v{METRICS_SCHEMA_VERSION}")

            except Exception as e:
                self.logger.error(f"Failed to initialize metrics schema: {e}")
                raise

    @contextmanager
    def transaction(self):
        """Context manager for database transactions"""
        conn = self._get_connection()
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            self.logger.error(f"Transaction rolled back: {e}")
            raise

    # ========================================================================
    # Task Metrics Operations
    # ========================================================================

    def store_task_metric(
        self,
        task_id: str,
        agent_id: str,
        duration_ms: int,
        result: Union[TaskResult, str],
        tokens_used: int = 0,
        files_changed: int = 0,
        timestamp: Optional[datetime] = None
    ) -> None:
        """
        Store task-level metric.

        Args:
            task_id: Task identifier
            agent_id: Agent identifier
            duration_ms: Task duration in milliseconds
            result: Task result ('success', 'failure', 'timeout', 'cancelled')
            tokens_used: Number of tokens consumed
            files_changed: Number of files modified
            timestamp: Metric timestamp (defaults to now)
        """
        timestamp = timestamp or datetime.now()
        result_str = result.value if isinstance(result, TaskResult) else result

        with self.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO task_metrics
                (task_id, agent_id, duration_ms, result, tokens_used, files_changed, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (task_id, agent_id, duration_ms, result_str, tokens_used, files_changed, timestamp.isoformat())
            )

        self.logger.debug(f"Stored task metric: {task_id} ({result_str}, {duration_ms}ms)")

    def get_task_metrics(
        self,
        task_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        result: Optional[Union[TaskResult, str]] = None,
        time_range: Optional[Tuple[datetime, datetime]] = None,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """
        Query task metrics.

        Args:
            task_id: Filter by task ID
            agent_id: Filter by agent ID
            result: Filter by result status
            time_range: Filter by time range (start, end)
            limit: Maximum number of metrics to return

        Returns:
            List of task metric dictionaries
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM task_metrics WHERE 1=1"
        params = []

        if task_id:
            query += " AND task_id = ?"
            params.append(task_id)

        if agent_id:
            query += " AND agent_id = ?"
            params.append(agent_id)

        if result:
            result_str = result.value if isinstance(result, TaskResult) else result
            query += " AND result = ?"
            params.append(result_str)

        if time_range:
            start_time, end_time = time_range
            query += " AND timestamp BETWEEN ? AND ?"
            params.extend([start_time.isoformat(), end_time.isoformat()])

        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)

        return [dict(row) for row in cursor.fetchall()]

    # ========================================================================
    # Agent Metrics Operations
    # ========================================================================

    def store_agent_metric(
        self,
        agent_id: str,
        metric_type: Union[MetricType, str],
        value: float,
        metadata: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None
    ) -> int:
        """
        Store agent-level metric.

        Args:
            agent_id: Agent identifier
            metric_type: Type of metric
            value: Metric value
            metadata: Additional metadata (JSON serializable)
            timestamp: Metric timestamp (defaults to now)

        Returns:
            Metric ID
        """
        timestamp = timestamp or datetime.now()
        metric_type_str = metric_type.value if isinstance(metric_type, MetricType) else metric_type

        with self.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO agent_metrics
                (agent_id, metric_type, value, metadata, timestamp)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    agent_id,
                    metric_type_str,
                    value,
                    json.dumps(metadata or {}),
                    timestamp.isoformat()
                )
            )
            metric_id = cursor.lastrowid

        self.logger.debug(f"Stored agent metric: {agent_id} ({metric_type_str}={value})")
        return metric_id

    def get_agent_metrics(
        self,
        agent_id: Optional[str] = None,
        metric_type: Optional[Union[MetricType, str]] = None,
        time_range: Optional[Tuple[datetime, datetime]] = None,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """
        Query agent metrics.

        Args:
            agent_id: Filter by agent ID
            metric_type: Filter by metric type
            time_range: Filter by time range (start, end)
            limit: Maximum number of metrics to return

        Returns:
            List of agent metric dictionaries
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM agent_metrics WHERE 1=1"
        params = []

        if agent_id:
            query += " AND agent_id = ?"
            params.append(agent_id)

        if metric_type:
            metric_type_str = metric_type.value if isinstance(metric_type, MetricType) else metric_type
            query += " AND metric_type = ?"
            params.append(metric_type_str)

        if time_range:
            start_time, end_time = time_range
            query += " AND timestamp BETWEEN ? AND ?"
            params.extend([start_time.isoformat(), end_time.isoformat()])

        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)

        metrics = []
        for row in cursor.fetchall():
            metric = dict(row)
            # Parse JSON metadata
            if metric.get("metadata"):
                try:
                    metric["metadata"] = json.loads(metric["metadata"])
                except json.JSONDecodeError:
                    metric["metadata"] = {}
            metrics.append(metric)

        return metrics

    # ========================================================================
    # Swarm Metrics Operations
    # ========================================================================

    def store_swarm_metric(
        self,
        swarm_id: str,
        metric_type: Union[MetricType, str],
        value: float,
        metadata: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None
    ) -> int:
        """
        Store swarm-level metric.

        Args:
            swarm_id: Swarm identifier
            metric_type: Type of metric
            value: Metric value
            metadata: Additional metadata (JSON serializable)
            timestamp: Metric timestamp (defaults to now)

        Returns:
            Metric ID
        """
        timestamp = timestamp or datetime.now()
        metric_type_str = metric_type.value if isinstance(metric_type, MetricType) else metric_type

        with self.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO swarm_metrics
                (swarm_id, metric_type, value, metadata, timestamp)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    swarm_id,
                    metric_type_str,
                    value,
                    json.dumps(metadata or {}),
                    timestamp.isoformat()
                )
            )
            metric_id = cursor.lastrowid

        self.logger.debug(f"Stored swarm metric: {swarm_id} ({metric_type_str}={value})")
        return metric_id

    def get_swarm_metrics(
        self,
        swarm_id: Optional[str] = None,
        metric_type: Optional[Union[MetricType, str]] = None,
        time_range: Optional[Tuple[datetime, datetime]] = None,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """
        Query swarm metrics.

        Args:
            swarm_id: Filter by swarm ID
            metric_type: Filter by metric type
            time_range: Filter by time range (start, end)
            limit: Maximum number of metrics to return

        Returns:
            List of swarm metric dictionaries
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM swarm_metrics WHERE 1=1"
        params = []

        if swarm_id:
            query += " AND swarm_id = ?"
            params.append(swarm_id)

        if metric_type:
            metric_type_str = metric_type.value if isinstance(metric_type, MetricType) else metric_type
            query += " AND metric_type = ?"
            params.append(metric_type_str)

        if time_range:
            start_time, end_time = time_range
            query += " AND timestamp BETWEEN ? AND ?"
            params.extend([start_time.isoformat(), end_time.isoformat()])

        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)

        metrics = []
        for row in cursor.fetchall():
            metric = dict(row)
            # Parse JSON metadata
            if metric.get("metadata"):
                try:
                    metric["metadata"] = json.loads(metric["metadata"])
                except json.JSONDecodeError:
                    metric["metadata"] = {}
            metrics.append(metric)

        return metrics

    # ========================================================================
    # Generic Metrics Operations
    # ========================================================================

    def store_metric(
        self,
        metric_type: str,
        data: Dict[str, Any],
        timestamp: Optional[datetime] = None
    ) -> Union[int, None]:
        """
        Store generic metric (auto-detects table based on metric_type).

        Args:
            metric_type: Type of metric ('task', 'agent', or 'swarm')
            data: Metric data dictionary
            timestamp: Metric timestamp (defaults to now)

        Returns:
            Metric ID (for agent/swarm metrics) or None (for task metrics)
        """
        timestamp = timestamp or datetime.now()

        if metric_type == "task":
            self.store_task_metric(
                task_id=data["task_id"],
                agent_id=data["agent_id"],
                duration_ms=data["duration_ms"],
                result=data["result"],
                tokens_used=data.get("tokens_used", 0),
                files_changed=data.get("files_changed", 0),
                timestamp=timestamp
            )
            return None
        elif metric_type == "agent":
            return self.store_agent_metric(
                agent_id=data["agent_id"],
                metric_type=data["metric_type"],
                value=data["value"],
                metadata=data.get("metadata"),
                timestamp=timestamp
            )
        elif metric_type == "swarm":
            return self.store_swarm_metric(
                swarm_id=data["swarm_id"],
                metric_type=data["metric_type"],
                value=data["value"],
                metadata=data.get("metadata"),
                timestamp=timestamp
            )
        else:
            raise ValueError(f"Unknown metric type: {metric_type}")

    def query_metrics(
        self,
        metric_type: str,
        filters: Optional[Dict[str, Any]] = None,
        time_range: Optional[Tuple[datetime, datetime]] = None,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """
        Query metrics with flexible filtering.

        Args:
            metric_type: Type of metric ('task', 'agent', or 'swarm')
            filters: Filter conditions (e.g., {'agent_id': 'agent_001'})
            time_range: Filter by time range (start, end)
            limit: Maximum number of metrics to return

        Returns:
            List of metric dictionaries
        """
        filters = filters or {}

        if metric_type == "task":
            return self.get_task_metrics(
                task_id=filters.get("task_id"),
                agent_id=filters.get("agent_id"),
                result=filters.get("result"),
                time_range=time_range,
                limit=limit
            )
        elif metric_type == "agent":
            return self.get_agent_metrics(
                agent_id=filters.get("agent_id"),
                metric_type=filters.get("metric_type"),
                time_range=time_range,
                limit=limit
            )
        elif metric_type == "swarm":
            return self.get_swarm_metrics(
                swarm_id=filters.get("swarm_id"),
                metric_type=filters.get("metric_type"),
                time_range=time_range,
                limit=limit
            )
        else:
            raise ValueError(f"Unknown metric type: {metric_type}")

    # ========================================================================
    # Aggregation Operations
    # ========================================================================

    def aggregate_metrics(
        self,
        metric_type: str,
        aggregation: Union[AggregationType, str],
        time_range: Optional[Tuple[datetime, datetime]] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Aggregate metrics over time range.

        Args:
            metric_type: Type of metric ('task', 'agent', or 'swarm')
            aggregation: Aggregation function ('avg', 'sum', 'count', 'min', 'max', 'stddev')
            time_range: Time range for aggregation (start, end)
            filters: Additional filters

        Returns:
            Aggregation result dictionary
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        agg_func = aggregation.value if isinstance(aggregation, AggregationType) else aggregation
        agg_func_upper = agg_func.upper()

        # Build query based on metric type
        if metric_type == "task":
            table_name = "task_metrics"
            value_column = "duration_ms"
        elif metric_type == "agent":
            table_name = "agent_metrics"
            value_column = "value"
        elif metric_type == "swarm":
            table_name = "swarm_metrics"
            value_column = "value"
        else:
            raise ValueError(f"Unknown metric type: {metric_type}")

        # Handle stddev separately (SQLite doesn't have built-in STDDEV)
        if agg_func == "stddev":
            # Calculate standard deviation using AVG and SUM of squares
            query = f"""
                SELECT
                    SQRT(AVG({value_column} * {value_column}) - AVG({value_column}) * AVG({value_column})) as stddev,
                    COUNT(*) as count,
                    AVG({value_column}) as avg
                FROM {table_name} WHERE 1=1
            """
        else:
            query = f"""
                SELECT
                    {agg_func_upper}({value_column}) as result,
                    COUNT(*) as count
                FROM {table_name} WHERE 1=1
            """

        params = []

        # Apply filters
        filters = filters or {}
        if metric_type == "task":
            if filters.get("agent_id"):
                query += " AND agent_id = ?"
                params.append(filters["agent_id"])
            if filters.get("result"):
                query += " AND result = ?"
                params.append(filters["result"])
        else:
            if filters.get("agent_id"):
                query += " AND agent_id = ?"
                params.append(filters["agent_id"])
            if filters.get("swarm_id"):
                query += " AND swarm_id = ?"
                params.append(filters["swarm_id"])
            if filters.get("metric_type"):
                query += " AND metric_type = ?"
                params.append(filters["metric_type"])

        # Apply time range
        if time_range:
            start_time, end_time = time_range
            query += " AND timestamp BETWEEN ? AND ?"
            params.extend([start_time.isoformat(), end_time.isoformat()])

        cursor.execute(query, params)
        result = cursor.fetchone()

        if agg_func == "stddev":
            return {
                "aggregation": agg_func,
                "metric_type": metric_type,
                "stddev": result["stddev"] if result["stddev"] else 0.0,
                "avg": result["avg"] if result["avg"] else 0.0,
                "count": result["count"]
            }
        else:
            return {
                "aggregation": agg_func,
                "metric_type": metric_type,
                "result": result["result"] if result["result"] else 0.0,
                "count": result["count"]
            }

    # ========================================================================
    # Maintenance Operations
    # ========================================================================

    def cleanup_old_metrics(self, retention_days: int = 30) -> Dict[str, int]:
        """
        Delete metrics older than retention period.

        Args:
            retention_days: Retention period in days (default: 30)

        Returns:
            Dictionary with counts of deleted records by table
        """
        cutoff_date = (datetime.now() - timedelta(days=retention_days)).isoformat()

        deleted_counts = {}

        with self.transaction() as conn:
            cursor = conn.cursor()

            # Clean task metrics
            cursor.execute(
                "DELETE FROM task_metrics WHERE timestamp < ?",
                (cutoff_date,)
            )
            deleted_counts["task_metrics"] = cursor.rowcount

            # Clean agent metrics
            cursor.execute(
                "DELETE FROM agent_metrics WHERE timestamp < ?",
                (cutoff_date,)
            )
            deleted_counts["agent_metrics"] = cursor.rowcount

            # Clean swarm metrics
            cursor.execute(
                "DELETE FROM swarm_metrics WHERE timestamp < ?",
                (cutoff_date,)
            )
            deleted_counts["swarm_metrics"] = cursor.rowcount

        total_deleted = sum(deleted_counts.values())
        self.logger.info(
            f"Cleaned up {total_deleted} old metrics (>{retention_days} days): "
            f"task={deleted_counts['task_metrics']}, "
            f"agent={deleted_counts['agent_metrics']}, "
            f"swarm={deleted_counts['swarm_metrics']}"
        )

        return deleted_counts

    def vacuum(self) -> None:
        """Optimize database storage"""
        conn = self._get_connection()
        conn.execute("VACUUM")
        self.logger.info("Metrics database vacuumed")

    def close(self) -> None:
        """Close all database connections"""
        with self._lock:
            for conn in self._connection_pool.values():
                try:
                    conn.close()
                except Exception as e:
                    self.logger.error(f"Error closing connection: {e}")

            self._connection_pool.clear()
            self.logger.debug("All connections closed")

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
        return False


# ============================================================================
# Example Usage
# ============================================================================

if __name__ == "__main__":
    import time
    import uuid

    print("=== MetricsStorage Example Usage ===\n")

    # Initialize storage
    storage = MetricsStorage()
    print("✓ Metrics storage initialized")

    # Example 1: Store task metrics
    print("\n--- Example 1: Task Metrics ---")
    task_id = str(uuid.uuid4())
    agent_id = "agent_backend_001"

    storage.store_task_metric(
        task_id=task_id,
        agent_id=agent_id,
        duration_ms=1500,
        result=TaskResult.SUCCESS,
        tokens_used=500,
        files_changed=3
    )
    print(f"✓ Task metric stored: {task_id}")

    # Query task metrics
    task_metrics = storage.get_task_metrics(agent_id=agent_id, limit=10)
    print(f"✓ Found {len(task_metrics)} task metrics for agent {agent_id}")

    # Example 2: Store agent metrics
    print("\n--- Example 2: Agent Metrics ---")
    storage.store_agent_metric(
        agent_id=agent_id,
        metric_type=MetricType.AGENT_SUCCESS_RATE,
        value=0.95,
        metadata={"total_tasks": 100, "successful_tasks": 95}
    )
    print(f"✓ Agent metric stored: {agent_id} (success_rate=0.95)")

    # Example 3: Store swarm metrics
    print("\n--- Example 3: Swarm Metrics ---")
    swarm_id = "swarm_001"
    storage.store_swarm_metric(
        swarm_id=swarm_id,
        metric_type=MetricType.SWARM_HEALTH,
        value=0.98,
        metadata={"active_agents": 5, "pending_tasks": 10}
    )
    print(f"✓ Swarm metric stored: {swarm_id} (health=0.98)")

    # Example 4: Aggregate metrics
    print("\n--- Example 4: Metric Aggregation ---")
    now = datetime.now()
    one_hour_ago = now - timedelta(hours=1)

    avg_duration = storage.aggregate_metrics(
        metric_type="task",
        aggregation=AggregationType.AVG,
        time_range=(one_hour_ago, now),
        filters={"agent_id": agent_id}
    )
    print(f"✓ Average task duration: {avg_duration}")

    # Example 5: Cleanup old metrics
    print("\n--- Example 5: Cleanup ---")
    deleted = storage.cleanup_old_metrics(retention_days=30)
    print(f"✓ Cleanup complete: {deleted}")

    # Close storage
    storage.close()
    print("\n✅ MetricsStorage demonstration complete")
    print(f"📦 Database location: {storage.db_path}")
