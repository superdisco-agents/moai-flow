#!/usr/bin/env python3
"""
Tests for MetricsQuery - Query Interface for Persistent Metrics Storage

Comprehensive test coverage (target: 90%+):
- 10 query methods
- Filtering and pagination
- Aggregation functions
- Time-series queries
- Performance benchmarks

Test Categories:
1. Basic Query Operations
2. Filtering and Pagination
3. Aggregation Functions
4. Time-Series Queries
5. Top/Bottom Queries
6. Summary Statistics
7. Performance Benchmarks
"""

import pytest
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

from moai_flow.monitoring.storage.metrics_persistence import MetricsPersistence
from moai_flow.monitoring.storage.metrics_query import (
    MetricsQuery,
    QueryFilter,
    AggregationFunc,
    TimeInterval,
)


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def temp_db_path():
    """Create temporary database path for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir) / "test_metrics.db"


@pytest.fixture
def populated_db(temp_db_path):
    """Create and populate database with test data."""
    # Create persistence and write test data
    persistence = MetricsPersistence(db_path=temp_db_path)

    # Write task metrics (100 records)
    now = datetime.now()
    for i in range(100):
        persistence.write_task_metric(
            task_id=f"task_{i:03d}",
            agent_id=f"agent_{i % 5}",  # 5 different agents
            duration_ms=1000 + i * 50,
            tokens_used=500 + i * 10,
            success=i % 10 != 0,  # 90% success rate
            timestamp=now - timedelta(minutes=100 - i),
        )

    # Write agent metrics (50 records)
    for i in range(50):
        persistence.write_agent_metric(
            agent_id=f"agent_{i % 5}",
            metric_type="throughput",
            value=10.0 + i * 0.5,
            timestamp=now - timedelta(minutes=50 - i),
        )

    # Write swarm metrics (20 records)
    for i in range(20):
        persistence.write_swarm_metric(
            swarm_id="swarm_001",
            metric_type="health",
            value=0.95 + (i * 0.001),
            timestamp=now - timedelta(minutes=20 - i),
        )

    persistence.flush()
    persistence.close()

    yield temp_db_path


@pytest.fixture
def query(populated_db):
    """Create MetricsQuery instance for testing."""
    query = MetricsQuery(db_path=populated_db)
    yield query
    query.close()


# ============================================================================
# Test Category 1: Basic Query Operations
# ============================================================================


class TestBasicQueries:
    """Test basic query methods."""

    def test_get_task_metrics(self, query):
        """Test getting task metrics."""
        metrics = query.get_task_metrics()

        assert len(metrics) > 0
        assert all("task_id" in m for m in metrics)
        assert all("agent_id" in m for m in metrics)
        assert all("duration_ms" in m for m in metrics)

    def test_get_agent_metrics(self, query):
        """Test getting agent metrics."""
        metrics = query.get_agent_metrics()

        assert len(metrics) > 0
        assert all("agent_id" in m for m in metrics)
        assert all("metric_type" in m for m in metrics)
        assert all("value" in m for m in metrics)

    def test_get_swarm_metrics(self, query):
        """Test getting swarm metrics."""
        metrics = query.get_swarm_metrics()

        assert len(metrics) > 0
        assert all("swarm_id" in m for m in metrics)
        assert all("metric_type" in m for m in metrics)
        assert all("value" in m for m in metrics)


# ============================================================================
# Test Category 2: Filtering and Pagination
# ============================================================================


class TestFiltering:
    """Test filtering and pagination."""

    def test_filter_by_agent_id(self, query):
        """Test filtering by agent_id."""
        filter = QueryFilter(agent_id="agent_0")
        metrics = query.get_task_metrics(filter)

        assert len(metrics) > 0
        assert all(m["agent_id"] == "agent_0" for m in metrics)

    def test_filter_by_time_range(self, query):
        """Test filtering by time range."""
        now = datetime.now()
        start_time = now - timedelta(minutes=30)
        end_time = now

        filter = QueryFilter(start_time=start_time, end_time=end_time)
        metrics = query.get_task_metrics(filter)

        # All metrics should be within time range
        assert len(metrics) > 0
        for metric in metrics:
            timestamp = metric["timestamp"]
            assert timestamp >= int(start_time.timestamp())
            assert timestamp <= int(end_time.timestamp())

    def test_filter_by_success(self, query):
        """Test filtering by success status."""
        # Filter for successful tasks
        filter_success = QueryFilter(success=True)
        success_metrics = query.get_task_metrics(filter_success)

        assert len(success_metrics) > 0
        assert all(m["success"] == 1 for m in success_metrics)

        # Filter for failed tasks
        filter_failure = QueryFilter(success=False)
        failure_metrics = query.get_task_metrics(filter_failure)

        assert len(failure_metrics) > 0
        assert all(m["success"] == 0 for m in failure_metrics)

    def test_pagination(self, query):
        """Test pagination with limit and offset."""
        # First page (limit 10)
        filter_page1 = QueryFilter(limit=10, offset=0)
        page1 = query.get_task_metrics(filter_page1)

        assert len(page1) == 10

        # Second page (limit 10, offset 10)
        filter_page2 = QueryFilter(limit=10, offset=10)
        page2 = query.get_task_metrics(filter_page2)

        assert len(page2) == 10

        # Ensure different results
        page1_ids = {m["task_id"] for m in page1}
        page2_ids = {m["task_id"] for m in page2}
        assert page1_ids != page2_ids

    def test_combined_filters(self, query):
        """Test combining multiple filters."""
        now = datetime.now()

        filter = QueryFilter(
            agent_id="agent_1",
            start_time=now - timedelta(minutes=60),
            end_time=now,
            success=True,
            limit=20,
        )

        metrics = query.get_task_metrics(filter)

        # Verify all filters applied
        assert all(m["agent_id"] == "agent_1" for m in metrics)
        assert all(m["success"] == 1 for m in metrics)
        assert len(metrics) <= 20


# ============================================================================
# Test Category 3: Aggregation Functions
# ============================================================================


class TestAggregation:
    """Test aggregation methods."""

    def test_calculate_average(self, query):
        """Test calculating average."""
        avg_duration = query.calculate_average("task_metrics", "duration_ms")

        assert avg_duration > 0
        assert isinstance(avg_duration, float)

    def test_calculate_average_with_filter(self, query):
        """Test average with filter."""
        filter = QueryFilter(agent_id="agent_0")
        avg_duration = query.calculate_average("task_metrics", "duration_ms", filter)

        assert avg_duration > 0

    def test_calculate_percentile(self, query):
        """Test calculating percentile."""
        # p95
        p95_duration = query.calculate_percentile("task_metrics", "duration_ms", 0.95)

        assert p95_duration > 0
        assert isinstance(p95_duration, (int, float))

        # p99
        p99_duration = query.calculate_percentile("task_metrics", "duration_ms", 0.99)

        assert p99_duration >= p95_duration  # p99 should be >= p95


# ============================================================================
# Test Category 4: Time-Series Queries
# ============================================================================


class TestTimeSeries:
    """Test time-series aggregation."""

    def test_aggregate_by_hour(self, query):
        """Test hourly aggregation."""
        filter = QueryFilter(start_time=datetime.now() - timedelta(hours=2))

        hourly_stats = query.aggregate_by_time(
            "task_metrics",
            "duration_ms",
            TimeInterval.HOUR,
            AggregationFunc.AVG,
            filter,
        )

        assert len(hourly_stats) > 0
        assert all("time_bucket" in s for s in hourly_stats)
        assert all("value" in s for s in hourly_stats)
        assert all("count" in s for s in hourly_stats)

    def test_aggregate_by_day(self, query):
        """Test daily aggregation."""
        filter = QueryFilter(start_time=datetime.now() - timedelta(days=2))

        daily_stats = query.aggregate_by_time(
            "task_metrics",
            "duration_ms",
            TimeInterval.DAY,
            AggregationFunc.SUM,
            filter,
        )

        assert len(daily_stats) > 0

    def test_aggregate_different_functions(self, query):
        """Test different aggregation functions."""
        filter = QueryFilter(start_time=datetime.now() - timedelta(hours=2))

        # AVG
        avg_stats = query.aggregate_by_time(
            "task_metrics", "duration_ms", TimeInterval.HOUR, AggregationFunc.AVG, filter
        )
        assert len(avg_stats) > 0

        # SUM
        sum_stats = query.aggregate_by_time(
            "task_metrics", "duration_ms", TimeInterval.HOUR, AggregationFunc.SUM, filter
        )
        assert len(sum_stats) > 0

        # COUNT
        count_stats = query.aggregate_by_time(
            "task_metrics", "duration_ms", TimeInterval.HOUR, AggregationFunc.COUNT, filter
        )
        assert len(count_stats) > 0


# ============================================================================
# Test Category 5: Top/Bottom Queries
# ============================================================================


class TestTopBottom:
    """Test top/bottom queries."""

    def test_get_top_agents(self, query):
        """Test getting top agents."""
        top_agents = query.get_top_agents(metric_type="avg_duration_ms", order="asc", limit=5)

        assert len(top_agents) > 0
        assert len(top_agents) <= 5

        # Verify sorted order (ascending by avg_duration_ms)
        durations = [a["avg_duration_ms"] for a in top_agents]
        assert durations == sorted(durations)

        # Verify required fields
        assert all("agent_id" in a for a in top_agents)
        assert all("task_count" in a for a in top_agents)
        assert all("avg_duration_ms" in a for a in top_agents)
        assert all("success_rate" in a for a in top_agents)

    def test_get_slowest_tasks(self, query):
        """Test getting slowest tasks."""
        slowest_tasks = query.get_slowest_tasks(limit=10)

        assert len(slowest_tasks) > 0
        assert len(slowest_tasks) <= 10

        # Verify sorted order (descending by duration_ms)
        durations = [t["duration_ms"] for t in slowest_tasks]
        assert durations == sorted(durations, reverse=True)

        # Verify required fields
        assert all("task_id" in t for t in slowest_tasks)
        assert all("agent_id" in t for t in slowest_tasks)
        assert all("duration_ms" in t for t in slowest_tasks)


# ============================================================================
# Test Category 6: Summary Statistics
# ============================================================================


class TestSummary:
    """Test summary statistics."""

    def test_get_summary_stats(self, query):
        """Test getting summary statistics."""
        summary = query.get_summary_stats()

        # Verify all required fields
        assert "total_tasks" in summary
        assert "successful_tasks" in summary
        assert "success_rate" in summary
        assert "avg_duration_ms" in summary
        assert "p95_duration_ms" in summary
        assert "p99_duration_ms" in summary
        assert "avg_tokens_per_task" in summary
        assert "total_tokens_used" in summary
        assert "unique_agents" in summary

        # Verify values make sense
        assert summary["total_tasks"] > 0
        assert 0 <= summary["success_rate"] <= 1
        assert summary["avg_duration_ms"] > 0
        assert summary["p95_duration_ms"] >= summary["avg_duration_ms"]
        assert summary["p99_duration_ms"] >= summary["p95_duration_ms"]

    def test_summary_stats_with_filter(self, query):
        """Test summary statistics with filter."""
        filter = QueryFilter(
            agent_id="agent_0", start_time=datetime.now() - timedelta(hours=1)
        )

        summary = query.get_summary_stats(filter)

        # Should only include agent_0 tasks
        assert summary["unique_agents"] <= 1


# ============================================================================
# Test Category 7: Edge Cases and Error Handling
# ============================================================================


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_query_empty_result(self, query):
        """Test query with no matching results."""
        # Query for non-existent agent
        filter = QueryFilter(agent_id="non_existent_agent")
        metrics = query.get_task_metrics(filter)

        assert len(metrics) == 0

    def test_query_future_time_range(self, query):
        """Test query with future time range."""
        future_start = datetime.now() + timedelta(days=1)
        future_end = datetime.now() + timedelta(days=2)

        filter = QueryFilter(start_time=future_start, end_time=future_end)
        metrics = query.get_task_metrics(filter)

        # Should return empty result
        assert len(metrics) == 0

    def test_summary_stats_empty_db(self, temp_db_path):
        """Test summary statistics on empty database."""
        # Create empty database
        persistence = MetricsPersistence(db_path=temp_db_path)
        persistence.close()

        query = MetricsQuery(db_path=temp_db_path)
        summary = query.get_summary_stats()

        # Should return zeros
        assert summary["total_tasks"] == 0
        assert summary["success_rate"] == 0.0
        assert summary["avg_duration_ms"] == 0.0

        query.close()

    def test_percentile_empty_result(self, query):
        """Test percentile calculation with empty result."""
        filter = QueryFilter(agent_id="non_existent")

        p95 = query.calculate_percentile("task_metrics", "duration_ms", 0.95, filter)

        # Should return 0.0
        assert p95 == 0.0

    def test_context_manager(self, populated_db):
        """Test context manager usage."""
        with MetricsQuery(db_path=populated_db) as query:
            metrics = query.get_task_metrics()
            assert len(metrics) > 0

        # Connection should be closed after exit


# ============================================================================
# Performance Benchmarks
# ============================================================================


class TestPerformance:
    """Performance benchmarks."""

    def test_query_performance_1000_records(self, query):
        """Benchmark: Query 1000 records."""
        import time

        filter = QueryFilter(limit=1000)

        start_time = time.time()
        metrics = query.get_task_metrics(filter)
        elapsed_ms = (time.time() - start_time) * 1000

        # Should complete in < 100ms
        assert elapsed_ms < 100

        print(f"\n✓ Queried {len(metrics)} records in {elapsed_ms:.2f}ms")

    def test_aggregation_performance(self, query):
        """Benchmark: Aggregation query."""
        import time

        filter = QueryFilter(start_time=datetime.now() - timedelta(hours=1))

        start_time = time.time()
        summary = query.get_summary_stats(filter)
        elapsed_ms = (time.time() - start_time) * 1000

        # Should complete in < 100ms
        assert elapsed_ms < 100

        print(f"\n✓ Aggregation completed in {elapsed_ms:.2f}ms")
