#!/usr/bin/env python3
"""
Tests for MetricsPersistence - SQLite-based Persistent Metrics Storage

Comprehensive test coverage (target: 90%+):
- Write operations (buffered and direct)
- Read operations (queries and filters)
- Compression and archival
- Retention policies and cleanup
- Connection pooling and transactions
- Performance benchmarks

Test Categories:
1. Basic Operations (write, flush, read)
2. Buffering and Performance
3. Compression and Archival
4. Retention and Cleanup
5. Concurrency and Thread Safety
6. Error Handling and Edge Cases
"""

import pytest
import tempfile
import time
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch

from moai_flow.monitoring.storage.metrics_persistence import (
    MetricsPersistence,
    RetentionPolicy,
    CompressionConfig,
    WriteBufferConfig,
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
def persistence(temp_db_path):
    """Create MetricsPersistence instance for testing."""
    # Disable auto-threads for predictable testing
    retention = RetentionPolicy(auto_cleanup=False)
    write_buffer = WriteBufferConfig(enabled=False)

    persistence = MetricsPersistence(
        db_path=temp_db_path,
        retention_policy=retention,
        write_buffer_config=write_buffer,
    )

    yield persistence

    persistence.close()


@pytest.fixture
def buffered_persistence(temp_db_path):
    """Create buffered MetricsPersistence instance for testing."""
    write_buffer = WriteBufferConfig(
        enabled=True, max_size=10, flush_interval_seconds=1.0
    )

    persistence = MetricsPersistence(
        db_path=temp_db_path, write_buffer_config=write_buffer
    )

    yield persistence

    persistence.close()


# ============================================================================
# Test Category 1: Basic Operations
# ============================================================================


class TestBasicOperations:
    """Test basic write and read operations."""

    def test_write_task_metric(self, persistence):
        """Test writing a single task metric."""
        persistence.write_task_metric(
            task_id="task_001",
            agent_id="agent_001",
            duration_ms=1500,
            tokens_used=500,
            success=True,
            metadata={"test": "data"},
        )

        # Flush to ensure write
        persistence.flush()

        # Verify write (requires query interface)
        conn = persistence._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM task_metrics WHERE task_id = ?", ("task_001",))
        result = cursor.fetchone()

        assert result is not None
        assert result["agent_id"] == "agent_001"
        assert result["duration_ms"] == 1500
        assert result["tokens_used"] == 500
        assert result["success"] == 1

    def test_write_agent_metric(self, persistence):
        """Test writing an agent metric."""
        persistence.write_agent_metric(
            agent_id="agent_001",
            metric_type="success_rate",
            value=0.95,
            metadata={"total_tasks": 100},
        )

        persistence.flush()

        # Verify
        conn = persistence._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM agent_metrics WHERE agent_id = ?", ("agent_001",))
        result = cursor.fetchone()

        assert result is not None
        assert result["metric_type"] == "success_rate"
        assert result["value"] == 0.95

    def test_write_swarm_metric(self, persistence):
        """Test writing a swarm metric."""
        persistence.write_swarm_metric(
            swarm_id="swarm_001",
            metric_type="health",
            value=0.98,
            metadata={"active_agents": 5},
        )

        persistence.flush()

        # Verify
        conn = persistence._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM swarm_metrics WHERE swarm_id = ?", ("swarm_001",))
        result = cursor.fetchone()

        assert result is not None
        assert result["metric_type"] == "health"
        assert result["value"] == 0.98


# ============================================================================
# Test Category 2: Buffering and Performance
# ============================================================================


class TestBuffering:
    """Test write buffering functionality."""

    def test_buffered_writes(self, buffered_persistence):
        """Test that writes are buffered."""
        # Write without flush
        for i in range(5):
            buffered_persistence.write_task_metric(
                task_id=f"task_{i:03d}",
                agent_id="agent_001",
                duration_ms=1000 + i * 100,
                tokens_used=500,
                success=True,
            )

        # Verify buffer has data (not yet in DB)
        assert len(buffered_persistence._write_buffer["task_metrics"]) == 5

        # Flush
        buffered_persistence.flush()

        # Verify buffer is empty
        assert len(buffered_persistence._write_buffer["task_metrics"]) == 0

    def test_auto_flush_on_buffer_full(self, buffered_persistence):
        """Test that buffer flushes automatically when full."""
        # Write more than buffer size (10)
        for i in range(12):
            buffered_persistence.write_task_metric(
                task_id=f"task_{i:03d}",
                agent_id="agent_001",
                duration_ms=1000,
                tokens_used=500,
                success=True,
            )

        # Buffer should have auto-flushed at 10, so only 2 remaining
        assert len(buffered_persistence._write_buffer["task_metrics"]) == 2

    def test_performance_batch_write(self, persistence):
        """Test performance of batch writes."""
        # Write 100 metrics
        start_time = time.time()

        for i in range(100):
            persistence.write_task_metric(
                task_id=f"task_{i:03d}",
                agent_id=f"agent_{i % 5}",
                duration_ms=1000 + i * 10,
                tokens_used=500,
                success=i % 10 != 0,
            )

        persistence.flush()

        elapsed_ms = (time.time() - start_time) * 1000

        # Should complete in < 500ms
        assert elapsed_ms < 500

        # Verify all writes
        conn = persistence._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM task_metrics")
        result = cursor.fetchone()

        assert result["count"] == 100


# ============================================================================
# Test Category 3: Compression and Archival
# ============================================================================


class TestCompression:
    """Test data compression functionality."""

    def test_compress_historical_data(self, persistence):
        """Test compression of historical data."""
        # Write old data (8 days ago)
        old_date = datetime.now() - timedelta(days=8)

        for i in range(10):
            persistence.write_task_metric(
                task_id=f"old_task_{i}",
                agent_id="agent_old",
                duration_ms=2000,
                tokens_used=800,
                success=True,
                timestamp=old_date,
            )

        persistence.flush()

        # Compress
        stats = persistence.compress_historical_data()

        # Verify compression
        assert stats["compressed_records"] == 10
        assert stats["archived_records"] == 1

        # Verify records removed from task_metrics
        conn = persistence._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM task_metrics")
        result = cursor.fetchone()
        assert result["count"] == 0

        # Verify archive exists
        cursor.execute("SELECT COUNT(*) as count FROM metrics_archive")
        result = cursor.fetchone()
        assert result["count"] == 1

    def test_compression_disabled(self, temp_db_path):
        """Test that compression can be disabled."""
        compression_config = CompressionConfig(enabled=False)

        persistence = MetricsPersistence(
            db_path=temp_db_path, compression_config=compression_config
        )

        old_date = datetime.now() - timedelta(days=8)

        persistence.write_task_metric(
            task_id="old_task",
            agent_id="agent_old",
            duration_ms=2000,
            tokens_used=800,
            success=True,
            timestamp=old_date,
        )

        persistence.flush()

        # Compress (should do nothing)
        stats = persistence.compress_historical_data()

        assert stats["compressed_records"] == 0
        assert stats["archived_records"] == 0

        persistence.close()


# ============================================================================
# Test Category 4: Retention and Cleanup
# ============================================================================


class TestRetention:
    """Test retention policies and cleanup."""

    def test_cleanup_old_data(self, persistence):
        """Test cleanup of old data."""
        # Write data at different ages
        now = datetime.now()

        # Write recent data (5 days ago)
        for i in range(5):
            persistence.write_task_metric(
                task_id=f"recent_{i}",
                agent_id="agent_001",
                duration_ms=1000,
                tokens_used=500,
                success=True,
                timestamp=now - timedelta(days=5),
            )

        # Write old data (10 days ago)
        for i in range(5):
            persistence.write_task_metric(
                task_id=f"old_{i}",
                agent_id="agent_001",
                duration_ms=1000,
                tokens_used=500,
                success=True,
                timestamp=now - timedelta(days=10),
            )

        persistence.flush()

        # Cleanup with 7-day retention
        stats = persistence.cleanup_old_data()

        # Verify compression of old data
        assert stats["detailed_deleted"] == 5  # 5 old records compressed

        # Verify recent data still exists
        conn = persistence._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM task_metrics")
        result = cursor.fetchone()
        assert result["count"] == 5  # Only recent data remains


# ============================================================================
# Test Category 5: Concurrency and Thread Safety
# ============================================================================


class TestConcurrency:
    """Test concurrency and thread safety."""

    def test_connection_pooling(self, persistence):
        """Test that connection pooling works correctly."""
        import threading

        results = []

        def write_metrics(thread_id):
            for i in range(10):
                persistence.write_task_metric(
                    task_id=f"thread_{thread_id}_task_{i}",
                    agent_id=f"agent_{thread_id}",
                    duration_ms=1000,
                    tokens_used=500,
                    success=True,
                )
            persistence.flush()
            results.append(thread_id)

        # Create multiple threads
        threads = []
        for i in range(3):
            thread = threading.Thread(target=write_metrics, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads
        for thread in threads:
            thread.join()

        # Verify all threads completed
        assert len(results) == 3

        # Verify all writes (30 total)
        conn = persistence._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM task_metrics")
        result = cursor.fetchone()
        assert result["count"] == 30

    def test_transaction_rollback(self, persistence):
        """Test transaction rollback on error."""
        # Write initial data
        persistence.write_task_metric(
            task_id="task_001",
            agent_id="agent_001",
            duration_ms=1000,
            tokens_used=500,
            success=True,
        )
        persistence.flush()

        # Try to write invalid data within transaction
        with pytest.raises(Exception):
            with persistence.transaction() as conn:
                cursor = conn.cursor()
                # This should fail (invalid SQL)
                cursor.execute("INSERT INTO task_metrics (invalid_column) VALUES (?)", ("test",))

        # Verify original data still exists
        conn = persistence._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM task_metrics")
        result = cursor.fetchone()
        assert result["count"] == 1  # Only original record


# ============================================================================
# Test Category 6: Database Maintenance
# ============================================================================


class TestMaintenance:
    """Test database maintenance operations."""

    def test_vacuum(self, persistence):
        """Test VACUUM operation."""
        # Write and delete data
        for i in range(10):
            persistence.write_task_metric(
                task_id=f"task_{i}",
                agent_id="agent_001",
                duration_ms=1000,
                tokens_used=500,
                success=True,
            )

        persistence.flush()

        # Delete half
        conn = persistence._get_connection()
        conn.execute("DELETE FROM task_metrics WHERE task_id LIKE 'task_%' LIMIT 5")
        conn.commit()

        # VACUUM should not raise error
        persistence.vacuum()

    def test_analyze(self, persistence):
        """Test ANALYZE operation."""
        # Write data
        for i in range(10):
            persistence.write_task_metric(
                task_id=f"task_{i}",
                agent_id="agent_001",
                duration_ms=1000,
                tokens_used=500,
                success=True,
            )

        persistence.flush()

        # ANALYZE should not raise error
        persistence.analyze()


# ============================================================================
# Test Category 7: Edge Cases and Error Handling
# ============================================================================


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_database(self, persistence):
        """Test operations on empty database."""
        # Cleanup should work on empty database
        stats = persistence.cleanup_old_data()
        assert stats["detailed_deleted"] == 0

        # Compression should work on empty database
        stats = persistence.compress_historical_data()
        assert stats["compressed_records"] == 0

    def test_null_metadata(self, persistence):
        """Test handling of null metadata."""
        persistence.write_task_metric(
            task_id="task_001",
            agent_id="agent_001",
            duration_ms=1000,
            tokens_used=500,
            success=True,
            metadata=None,
        )

        persistence.flush()

        # Should not raise error
        conn = persistence._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM task_metrics WHERE task_id = ?", ("task_001",))
        result = cursor.fetchone()

        assert result is not None

    def test_large_metadata(self, persistence):
        """Test handling of large metadata."""
        large_metadata = {"data": "x" * 10000}  # 10KB metadata

        persistence.write_task_metric(
            task_id="task_001",
            agent_id="agent_001",
            duration_ms=1000,
            tokens_used=500,
            success=True,
            metadata=large_metadata,
        )

        persistence.flush()

        # Should not raise error
        conn = persistence._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM task_metrics WHERE task_id = ?", ("task_001",))
        result = cursor.fetchone()

        assert result is not None

    def test_context_manager(self, temp_db_path):
        """Test context manager usage."""
        with MetricsPersistence(db_path=temp_db_path) as persistence:
            persistence.write_task_metric(
                task_id="task_001",
                agent_id="agent_001",
                duration_ms=1000,
                tokens_used=500,
                success=True,
            )
            persistence.flush()

        # Connection should be closed after exit


# ============================================================================
# Performance Benchmarks
# ============================================================================


class TestPerformance:
    """Performance benchmarks."""

    def test_write_performance_1000_metrics(self, persistence):
        """Benchmark: Write 1000 metrics."""
        start_time = time.time()

        for i in range(1000):
            persistence.write_task_metric(
                task_id=f"task_{i:04d}",
                agent_id=f"agent_{i % 10}",
                duration_ms=1000 + i,
                tokens_used=500,
                success=i % 10 != 0,
            )

        persistence.flush()

        elapsed_ms = (time.time() - start_time) * 1000

        # Should complete in < 2000ms
        assert elapsed_ms < 2000

        print(f"\n✓ 1000 metrics written in {elapsed_ms:.2f}ms")
        print(f"  Average: {elapsed_ms/1000:.2f}ms per metric")
