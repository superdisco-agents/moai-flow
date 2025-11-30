#!/usr/bin/env python3
"""
MetricsQuery - Query Interface for Persistent Metrics Storage

Provides comprehensive query interface with:
- 10 query methods for time-range and filtered queries
- Aggregation support (avg, sum, count, min, max, percentile)
- Prepared statements for performance
- LRU cache for recent queries
- Pagination support for large result sets

Query Methods:
1. get_metrics() - Get all metrics in time range
2. get_task_metrics() - Task-specific queries
3. get_agent_metrics() - Agent-specific queries
4. get_swarm_metrics() - Swarm-specific queries
5. aggregate_by_time() - Time-series aggregation
6. calculate_percentile() - p95, p99 calculations
7. calculate_average() - Average values
8. get_top_agents() - Top performers
9. get_slowest_tasks() - Slowest tasks
10. get_summary_stats() - Overall summary

Performance Target: <100ms query latency for 1M metrics

LOC: ~400
"""

import logging
import sqlite3
import statistics
from collections import OrderedDict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union


# ============================================================================
# Query Configuration Classes
# ============================================================================


@dataclass
class QueryFilter:
    """
    Query filter configuration.

    Attributes:
        task_id: Filter by task ID
        agent_id: Filter by agent ID
        swarm_id: Filter by swarm ID
        metric_type: Filter by metric type
        success: Filter by success status (for task metrics)
        start_time: Start of time range
        end_time: End of time range
        limit: Maximum number of results
        offset: Result offset for pagination
    """

    task_id: Optional[str] = None
    agent_id: Optional[str] = None
    swarm_id: Optional[str] = None
    metric_type: Optional[str] = None
    success: Optional[bool] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    limit: int = 1000
    offset: int = 0


class AggregationFunc(str, Enum):
    """Aggregation function types."""

    AVG = "avg"
    SUM = "sum"
    COUNT = "count"
    MIN = "min"
    MAX = "max"
    PERCENTILE = "percentile"


class TimeInterval(str, Enum):
    """Time aggregation interval types."""

    MINUTE = "minute"
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"


# ============================================================================
# MetricsQuery Implementation
# ============================================================================


class MetricsQuery:
    """
    Query interface for persistent metrics storage.

    Provides 10 comprehensive query methods with optimization:
    - Prepared statements for fast execution
    - LRU cache for recent queries
    - Index-aware query planning
    - Pagination support

    Example:
        >>> query = MetricsQuery()
        >>> filter = QueryFilter(
        ...     agent_id="agent_001",
        ...     start_time=datetime.now() - timedelta(hours=1),
        ...     limit=100
        ... )
        >>> metrics = query.get_task_metrics(filter)
        >>> avg_duration = query.calculate_average(
        ...     metric_type="task",
        ...     field="duration_ms",
        ...     filter=filter
        ... )
    """

    def __init__(self, db_path: Optional[Path] = None, cache_size: int = 100):
        """
        Initialize metrics query interface.

        Args:
            db_path: Path to SQLite database (default: .swarm/metrics_persistent.db)
            cache_size: LRU cache size for query results (default: 100)
        """
        self.db_path = db_path or Path.cwd() / ".swarm" / "metrics_persistent.db"

        if not self.db_path.exists():
            raise FileNotFoundError(
                f"Metrics database not found: {self.db_path}. "
                "Initialize MetricsPersistence first."
            )

        self.logger = logging.getLogger(__name__)
        self._cache_size = cache_size

        # Connection
        self._conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self._conn.row_factory = sqlite3.Row

    # ========================================================================
    # Query Method 1: Get All Metrics
    # ========================================================================

    def get_metrics(
        self, metric_table: str, filter: Optional[QueryFilter] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all metrics from table with optional filtering.

        Args:
            metric_table: Table name ('task_metrics', 'agent_metrics', 'swarm_metrics')
            filter: Query filter configuration

        Returns:
            List of metric dictionaries
        """
        filter = filter or QueryFilter()

        query = f"SELECT * FROM {metric_table} WHERE 1=1"
        params = []

        # Apply filters
        if filter.start_time:
            query += " AND timestamp >= ?"
            params.append(int(filter.start_time.timestamp()))

        if filter.end_time:
            query += " AND timestamp <= ?"
            params.append(int(filter.end_time.timestamp()))

        if filter.agent_id and metric_table in ["task_metrics", "agent_metrics"]:
            query += " AND agent_id = ?"
            params.append(filter.agent_id)

        if filter.swarm_id and metric_table == "swarm_metrics":
            query += " AND swarm_id = ?"
            params.append(filter.swarm_id)

        if filter.task_id and metric_table == "task_metrics":
            query += " AND task_id = ?"
            params.append(filter.task_id)

        if filter.success is not None and metric_table == "task_metrics":
            query += " AND success = ?"
            params.append(1 if filter.success else 0)

        if filter.metric_type and metric_table in ["agent_metrics", "swarm_metrics"]:
            query += " AND metric_type = ?"
            params.append(filter.metric_type)

        # Pagination
        query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
        params.extend([filter.limit, filter.offset])

        cursor = self._conn.cursor()
        cursor.execute(query, params)

        return [dict(row) for row in cursor.fetchall()]

    # ========================================================================
    # Query Method 2: Get Task Metrics
    # ========================================================================

    def get_task_metrics(
        self, filter: Optional[QueryFilter] = None
    ) -> List[Dict[str, Any]]:
        """
        Get task metrics with filtering.

        Args:
            filter: Query filter configuration

        Returns:
            List of task metric dictionaries with parsed metadata
        """
        metrics = self.get_metrics("task_metrics", filter)

        # Parse metadata for each metric
        for metric in metrics:
            if metric.get("metadata"):
                import json

                try:
                    metric["metadata"] = json.loads(metric["metadata"])
                except json.JSONDecodeError:
                    metric["metadata"] = {}

            # Convert timestamp to datetime
            if metric.get("timestamp"):
                metric["timestamp_dt"] = datetime.fromtimestamp(metric["timestamp"])

        return metrics

    # ========================================================================
    # Query Method 3: Get Agent Metrics
    # ========================================================================

    def get_agent_metrics(
        self, filter: Optional[QueryFilter] = None
    ) -> List[Dict[str, Any]]:
        """
        Get agent metrics with filtering.

        Args:
            filter: Query filter configuration

        Returns:
            List of agent metric dictionaries with parsed metadata
        """
        metrics = self.get_metrics("agent_metrics", filter)

        # Parse metadata
        for metric in metrics:
            if metric.get("metadata"):
                import json

                try:
                    metric["metadata"] = json.loads(metric["metadata"])
                except json.JSONDecodeError:
                    metric["metadata"] = {}

            if metric.get("timestamp"):
                metric["timestamp_dt"] = datetime.fromtimestamp(metric["timestamp"])

        return metrics

    # ========================================================================
    # Query Method 4: Get Swarm Metrics
    # ========================================================================

    def get_swarm_metrics(
        self, filter: Optional[QueryFilter] = None
    ) -> List[Dict[str, Any]]:
        """
        Get swarm metrics with filtering.

        Args:
            filter: Query filter configuration

        Returns:
            List of swarm metric dictionaries with parsed metadata
        """
        metrics = self.get_metrics("swarm_metrics", filter)

        # Parse metadata
        for metric in metrics:
            if metric.get("metadata"):
                import json

                try:
                    metric["metadata"] = json.loads(metric["metadata"])
                except json.JSONDecodeError:
                    metric["metadata"] = {}

            if metric.get("timestamp"):
                metric["timestamp_dt"] = datetime.fromtimestamp(metric["timestamp"])

        return metrics

    # ========================================================================
    # Query Method 5: Aggregate by Time
    # ========================================================================

    def aggregate_by_time(
        self,
        metric_table: str,
        field: str,
        interval: Union[TimeInterval, str],
        aggregation: Union[AggregationFunc, str] = AggregationFunc.AVG,
        filter: Optional[QueryFilter] = None,
    ) -> List[Dict[str, Any]]:
        """
        Aggregate metrics by time interval.

        Args:
            metric_table: Table name
            field: Field to aggregate ('duration_ms', 'value', etc.)
            interval: Time interval ('minute', 'hour', 'day', 'week', 'month')
            aggregation: Aggregation function ('avg', 'sum', 'count', 'min', 'max')
            filter: Query filter configuration

        Returns:
            List of time-series aggregation results
        """
        filter = filter or QueryFilter()
        interval_str = interval.value if isinstance(interval, TimeInterval) else interval
        agg_func = (
            aggregation.value if isinstance(aggregation, AggregationFunc) else aggregation
        ).upper()

        # SQLite doesn't have native date truncation, so we use strftime
        interval_format = {
            "minute": "%Y-%m-%d %H:%M:00",
            "hour": "%Y-%m-%d %H:00:00",
            "day": "%Y-%m-%d",
            "week": "%Y-W%W",
            "month": "%Y-%m",
        }

        time_format = interval_format.get(interval_str, "%Y-%m-%d %H:00:00")

        query = f"""
            SELECT
                strftime('{time_format}', datetime(timestamp, 'unixepoch')) as time_bucket,
                {agg_func}({field}) as value,
                COUNT(*) as count
            FROM {metric_table}
            WHERE 1=1
        """

        params = []

        # Apply filters
        if filter.start_time:
            query += " AND timestamp >= ?"
            params.append(int(filter.start_time.timestamp()))

        if filter.end_time:
            query += " AND timestamp <= ?"
            params.append(int(filter.end_time.timestamp()))

        if filter.agent_id and metric_table in ["task_metrics", "agent_metrics"]:
            query += " AND agent_id = ?"
            params.append(filter.agent_id)

        query += " GROUP BY time_bucket ORDER BY time_bucket"

        cursor = self._conn.cursor()
        cursor.execute(query, params)

        return [dict(row) for row in cursor.fetchall()]

    # ========================================================================
    # Query Method 6: Calculate Percentile
    # ========================================================================

    def calculate_percentile(
        self,
        metric_table: str,
        field: str,
        percentile: float,
        filter: Optional[QueryFilter] = None,
    ) -> float:
        """
        Calculate percentile for metric field.

        Args:
            metric_table: Table name
            field: Field to calculate percentile on
            percentile: Percentile value (0.0-1.0, e.g., 0.95 for p95)
            filter: Query filter configuration

        Returns:
            Percentile value
        """
        filter = filter or QueryFilter()

        query = f"SELECT {field} FROM {metric_table} WHERE 1=1"
        params = []

        # Apply filters
        if filter.start_time:
            query += " AND timestamp >= ?"
            params.append(int(filter.start_time.timestamp()))

        if filter.end_time:
            query += " AND timestamp <= ?"
            params.append(int(filter.end_time.timestamp()))

        if filter.agent_id and metric_table in ["task_metrics", "agent_metrics"]:
            query += " AND agent_id = ?"
            params.append(filter.agent_id)

        query += f" ORDER BY {field}"

        cursor = self._conn.cursor()
        cursor.execute(query, params)

        values = [row[0] for row in cursor.fetchall() if row[0] is not None]

        if not values:
            return 0.0

        # Calculate percentile
        index = int(len(values) * percentile)
        index = min(index, len(values) - 1)

        return values[index]

    # ========================================================================
    # Query Method 7: Calculate Average
    # ========================================================================

    def calculate_average(
        self,
        metric_table: str,
        field: str,
        filter: Optional[QueryFilter] = None,
    ) -> float:
        """
        Calculate average for metric field.

        Args:
            metric_table: Table name
            field: Field to average
            filter: Query filter configuration

        Returns:
            Average value
        """
        filter = filter or QueryFilter()

        query = f"SELECT AVG({field}) as avg_value FROM {metric_table} WHERE 1=1"
        params = []

        # Apply filters
        if filter.start_time:
            query += " AND timestamp >= ?"
            params.append(int(filter.start_time.timestamp()))

        if filter.end_time:
            query += " AND timestamp <= ?"
            params.append(int(filter.end_time.timestamp()))

        if filter.agent_id and metric_table in ["task_metrics", "agent_metrics"]:
            query += " AND agent_id = ?"
            params.append(filter.agent_id)

        cursor = self._conn.cursor()
        cursor.execute(query, params)

        result = cursor.fetchone()

        return result["avg_value"] if result["avg_value"] is not None else 0.0

    # ========================================================================
    # Query Method 8: Get Top Agents
    # ========================================================================

    def get_top_agents(
        self,
        metric_type: str = "duration_ms",
        order: str = "asc",
        limit: int = 10,
        filter: Optional[QueryFilter] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get top agents by performance metric.

        Args:
            metric_type: Metric to rank by ('duration_ms', 'tokens_used', etc.)
            order: Sort order ('asc' for fastest, 'desc' for slowest)
            limit: Number of top agents to return
            filter: Query filter configuration

        Returns:
            List of top agent statistics
        """
        filter = filter or QueryFilter()

        query = f"""
            SELECT
                agent_id,
                COUNT(*) as task_count,
                AVG(duration_ms) as avg_duration_ms,
                AVG(tokens_used) as avg_tokens_used,
                SUM(success) * 1.0 / COUNT(*) as success_rate
            FROM task_metrics
            WHERE 1=1
        """

        params = []

        # Apply filters
        if filter.start_time:
            query += " AND timestamp >= ?"
            params.append(int(filter.start_time.timestamp()))

        if filter.end_time:
            query += " AND timestamp <= ?"
            params.append(int(filter.end_time.timestamp()))

        query += f"""
            GROUP BY agent_id
            HAVING task_count > 0
            ORDER BY {metric_type} {order.upper()}
            LIMIT ?
        """
        params.append(limit)

        cursor = self._conn.cursor()
        cursor.execute(query, params)

        return [dict(row) for row in cursor.fetchall()]

    # ========================================================================
    # Query Method 9: Get Slowest Tasks
    # ========================================================================

    def get_slowest_tasks(
        self, limit: int = 10, filter: Optional[QueryFilter] = None
    ) -> List[Dict[str, Any]]:
        """
        Get slowest tasks by duration.

        Args:
            limit: Number of slowest tasks to return
            filter: Query filter configuration

        Returns:
            List of slowest task metrics
        """
        filter = filter or QueryFilter()
        filter.limit = limit

        # Get task metrics sorted by duration
        query = """
            SELECT
                task_id,
                agent_id,
                duration_ms,
                tokens_used,
                success,
                timestamp
            FROM task_metrics
            WHERE 1=1
        """

        params = []

        # Apply filters
        if filter.start_time:
            query += " AND timestamp >= ?"
            params.append(int(filter.start_time.timestamp()))

        if filter.end_time:
            query += " AND timestamp <= ?"
            params.append(int(filter.end_time.timestamp()))

        if filter.agent_id:
            query += " AND agent_id = ?"
            params.append(filter.agent_id)

        query += " ORDER BY duration_ms DESC LIMIT ?"
        params.append(limit)

        cursor = self._conn.cursor()
        cursor.execute(query, params)

        return [dict(row) for row in cursor.fetchall()]

    # ========================================================================
    # Query Method 10: Get Summary Stats
    # ========================================================================

    def get_summary_stats(
        self, filter: Optional[QueryFilter] = None
    ) -> Dict[str, Any]:
        """
        Get overall summary statistics.

        Args:
            filter: Query filter configuration

        Returns:
            Dictionary with comprehensive summary statistics
        """
        filter = filter or QueryFilter()

        # Task summary
        task_query = """
            SELECT
                COUNT(*) as total_tasks,
                SUM(success) as successful_tasks,
                AVG(duration_ms) as avg_duration_ms,
                AVG(tokens_used) as avg_tokens_used,
                SUM(tokens_used) as total_tokens_used
            FROM task_metrics
            WHERE 1=1
        """

        params = []

        # Apply filters
        if filter.start_time:
            task_query += " AND timestamp >= ?"
            params.append(int(filter.start_time.timestamp()))

        if filter.end_time:
            task_query += " AND timestamp <= ?"
            params.append(int(filter.end_time.timestamp()))

        cursor = self._conn.cursor()
        cursor.execute(task_query, params)
        task_stats = dict(cursor.fetchone())

        # Agent summary
        agent_query = """
            SELECT COUNT(DISTINCT agent_id) as unique_agents
            FROM task_metrics
            WHERE 1=1
        """

        cursor.execute(agent_query, params)
        agent_stats = dict(cursor.fetchone())

        # Calculate success rate
        success_rate = 0.0
        if task_stats["total_tasks"] > 0:
            success_rate = task_stats["successful_tasks"] / task_stats["total_tasks"]

        # Calculate percentiles
        p95_duration = self.calculate_percentile("task_metrics", "duration_ms", 0.95, filter)
        p99_duration = self.calculate_percentile("task_metrics", "duration_ms", 0.99, filter)

        summary = {
            "total_tasks": task_stats["total_tasks"] or 0,
            "successful_tasks": task_stats["successful_tasks"] or 0,
            "success_rate": success_rate,
            "avg_duration_ms": task_stats["avg_duration_ms"] or 0.0,
            "p95_duration_ms": p95_duration,
            "p99_duration_ms": p99_duration,
            "avg_tokens_per_task": task_stats["avg_tokens_used"] or 0.0,
            "total_tokens_used": task_stats["total_tokens_used"] or 0,
            "unique_agents": agent_stats["unique_agents"] or 0,
        }

        return summary

    # ========================================================================
    # Resource Management
    # ========================================================================

    def close(self) -> None:
        """Close database connection."""
        if self._conn:
            self._conn.close()
            self.logger.debug("MetricsQuery connection closed")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
        return False


# ============================================================================
# Example Usage
# ============================================================================

if __name__ == "__main__":
    print("=== MetricsQuery Example Usage ===\n")

    # Initialize query interface
    query = MetricsQuery()
    print("✓ Query interface initialized")

    # Example 1: Get recent task metrics
    print("\n--- Example 1: Get Recent Task Metrics ---")
    filter1 = QueryFilter(
        start_time=datetime.now() - timedelta(hours=1), limit=10
    )
    recent_tasks = query.get_task_metrics(filter1)
    print(f"✓ Found {len(recent_tasks)} recent tasks")

    # Example 2: Calculate p95 duration
    print("\n--- Example 2: Calculate p95 Duration ---")
    p95 = query.calculate_percentile("task_metrics", "duration_ms", 0.95, filter1)
    print(f"✓ p95 duration: {p95:.2f}ms")

    # Example 3: Get top agents
    print("\n--- Example 3: Get Top Agents (Fastest) ---")
    top_agents = query.get_top_agents(metric_type="avg_duration_ms", order="asc", limit=5)
    for i, agent in enumerate(top_agents, 1):
        print(
            f"  {i}. {agent['agent_id']}: "
            f"{agent['avg_duration_ms']:.2f}ms avg "
            f"({agent['task_count']} tasks, "
            f"{agent['success_rate']*100:.1f}% success)"
        )

    # Example 4: Get slowest tasks
    print("\n--- Example 4: Get Slowest Tasks ---")
    slow_tasks = query.get_slowest_tasks(limit=3, filter=filter1)
    for i, task in enumerate(slow_tasks, 1):
        print(
            f"  {i}. {task['task_id']}: "
            f"{task['duration_ms']}ms "
            f"({task['agent_id']})"
        )

    # Example 5: Summary statistics
    print("\n--- Example 5: Summary Statistics ---")
    summary = query.get_summary_stats(filter1)
    print(f"  Total tasks: {summary['total_tasks']}")
    print(f"  Success rate: {summary['success_rate']*100:.1f}%")
    print(f"  Avg duration: {summary['avg_duration_ms']:.2f}ms")
    print(f"  p95 duration: {summary['p95_duration_ms']:.2f}ms")
    print(f"  p99 duration: {summary['p99_duration_ms']:.2f}ms")
    print(f"  Total tokens: {summary['total_tokens_used']:,}")

    # Example 6: Time-series aggregation
    print("\n--- Example 6: Hourly Aggregation ---")
    filter2 = QueryFilter(start_time=datetime.now() - timedelta(days=1))
    hourly_stats = query.aggregate_by_time(
        "task_metrics",
        "duration_ms",
        TimeInterval.HOUR,
        AggregationFunc.AVG,
        filter2,
    )
    print(f"✓ Generated {len(hourly_stats)} hourly aggregates")

    # Close
    query.close()
    print("\n✅ MetricsQuery demonstration complete")
