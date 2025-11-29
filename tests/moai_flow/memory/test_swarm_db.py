"""
Comprehensive tests for SwarmDB - SQLite wrapper for persistent storage.

Test Coverage Requirements:
- Framework: pytest with temporary database fixtures
- Coverage Target: 90%+ (per config)
- Test Database: Use :memory: SQLite for testing

Test Areas:
1. Schema initialization and validation
2. CRUD operations (Create, Read, Update, Delete)
3. Namespace isolation
4. JSON serialization/deserialization
5. Context save/load operations
6. Thread safety and concurrent access
7. Error handling and edge cases
8. Statistics and metrics accuracy
"""

import json
import sqlite3
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Dict, List

import pytest

from moai_flow.memory.swarm_db import SwarmDB


@pytest.fixture
def temp_db():
    """
    Create temporary in-memory database for testing.

    Yields:
        SwarmDB: Temporary database instance

    Note:
        Cleanup is handled automatically by in-memory database
    """
    db = SwarmDB(db_path=":memory:")
    yield db
    # In-memory database is automatically cleaned up


@pytest.fixture
def temp_file_db(tmp_path: Path):
    """
    Create temporary file-based database for testing persistence.

    Args:
        tmp_path: pytest temporary directory fixture

    Yields:
        tuple: (SwarmDB instance, database file path)
    """
    db_file = tmp_path / "test_swarm.db"
    db = SwarmDB(db_path=str(db_file))
    yield db, db_file
    # File cleanup handled by pytest tmp_path


class TestSwarmDBInitialization:
    """Test suite for SwarmDB initialization and schema creation."""

    def test_initialization_creates_schema(self, temp_db: SwarmDB):
        """Test that database initialization creates the required schema."""
        # Verify database is initialized
        assert temp_db is not None

        # Verify tables exist
        tables = temp_db.get_table_names()
        assert "key_value_store" in tables
        assert "contexts" in tables

    def test_initialization_with_file_path(self, tmp_path: Path):
        """Test database initialization with file path."""
        db_file = tmp_path / "swarm.db"
        db = SwarmDB(db_path=str(db_file))

        assert db_file.exists()
        assert db_file.is_file()

    def test_initialization_with_memory(self):
        """Test database initialization with in-memory mode."""
        db = SwarmDB(db_path=":memory:")

        # Should work without creating files
        assert db is not None
        tables = db.get_table_names()
        assert len(tables) > 0

    def test_schema_structure(self, temp_db: SwarmDB):
        """Test that schema has correct structure."""
        schema = temp_db.get_schema()

        # Verify key_value_store table structure
        kv_columns = schema["key_value_store"]
        assert "namespace" in kv_columns
        assert "key" in kv_columns
        assert "value" in kv_columns
        assert "created_at" in kv_columns
        assert "updated_at" in kv_columns

        # Verify contexts table structure
        ctx_columns = schema["contexts"]
        assert "context_id" in ctx_columns
        assert "namespace" in ctx_columns
        assert "data" in ctx_columns
        assert "created_at" in ctx_columns

    def test_initialization_idempotent(self, tmp_path: Path):
        """Test that multiple initializations don't break schema."""
        db_file = tmp_path / "idempotent.db"

        # First initialization
        db1 = SwarmDB(db_path=str(db_file))
        db1.set("test", "key", "value")

        # Second initialization (should reuse existing)
        db2 = SwarmDB(db_path=str(db_file))
        value = db2.get("test", "key")

        assert value == "value"


class TestSwarmDBCRUDOperations:
    """Test suite for basic CRUD operations."""

    def test_set_and_get_simple_value(self, temp_db: SwarmDB):
        """Test storing and retrieving a simple string value."""
        temp_db.set(namespace="test", key="greeting", value="Hello World")
        result = temp_db.get(namespace="test", key="greeting")

        assert result == "Hello World"

    def test_set_overwrites_existing_value(self, temp_db: SwarmDB):
        """Test that setting same key overwrites previous value."""
        temp_db.set("test", "counter", "1")
        temp_db.set("test", "counter", "2")

        result = temp_db.get("test", "counter")
        assert result == "2"

    def test_get_nonexistent_key_returns_none(self, temp_db: SwarmDB):
        """Test that getting non-existent key returns None."""
        result = temp_db.get("test", "nonexistent")

        assert result is None

    def test_get_with_default_value(self, temp_db: SwarmDB):
        """Test get operation with default value."""
        result = temp_db.get("test", "missing", default="default_value")

        assert result == "default_value"

    def test_delete_existing_key(self, temp_db: SwarmDB):
        """Test deleting an existing key."""
        temp_db.set("test", "deleteme", "value")
        deleted = temp_db.delete("test", "deleteme")

        assert deleted is True
        assert temp_db.get("test", "deleteme") is None

    def test_delete_nonexistent_key(self, temp_db: SwarmDB):
        """Test deleting a non-existent key returns False."""
        deleted = temp_db.delete("test", "nonexistent")

        assert deleted is False

    def test_exists_method(self, temp_db: SwarmDB):
        """Test the exists method for key checking."""
        temp_db.set("test", "existing", "value")

        assert temp_db.exists("test", "existing") is True
        assert temp_db.exists("test", "nonexistent") is False

    def test_update_value(self, temp_db: SwarmDB):
        """Test updating an existing value."""
        temp_db.set("test", "counter", "10")
        temp_db.update("test", "counter", "20")

        assert temp_db.get("test", "counter") == "20"

    def test_update_nonexistent_creates_new(self, temp_db: SwarmDB):
        """Test that update creates new entry if key doesn't exist."""
        temp_db.update("test", "new_key", "new_value")

        assert temp_db.get("test", "new_key") == "new_value"


class TestSwarmDBNamespaceIsolation:
    """Test suite for namespace isolation."""

    def test_same_key_different_namespaces(self, temp_db: SwarmDB):
        """Test that same key in different namespaces are isolated."""
        temp_db.set("ns1", "key", "value1")
        temp_db.set("ns2", "key", "value2")

        assert temp_db.get("ns1", "key") == "value1"
        assert temp_db.get("ns2", "key") == "value2"

    def test_delete_in_one_namespace_preserves_others(self, temp_db: SwarmDB):
        """Test that deleting from one namespace doesn't affect others."""
        temp_db.set("ns1", "key", "value1")
        temp_db.set("ns2", "key", "value2")

        temp_db.delete("ns1", "key")

        assert temp_db.get("ns1", "key") is None
        assert temp_db.get("ns2", "key") == "value2"

    def test_list_keys_by_namespace(self, temp_db: SwarmDB):
        """Test listing all keys in a specific namespace."""
        temp_db.set("ns1", "key1", "value1")
        temp_db.set("ns1", "key2", "value2")
        temp_db.set("ns2", "key3", "value3")

        ns1_keys = temp_db.list_keys("ns1")

        assert len(ns1_keys) == 2
        assert "key1" in ns1_keys
        assert "key2" in ns1_keys
        assert "key3" not in ns1_keys

    def test_clear_namespace(self, temp_db: SwarmDB):
        """Test clearing all entries in a namespace."""
        temp_db.set("ns1", "key1", "value1")
        temp_db.set("ns1", "key2", "value2")
        temp_db.set("ns2", "key3", "value3")

        cleared = temp_db.clear_namespace("ns1")

        assert cleared == 2
        assert len(temp_db.list_keys("ns1")) == 0
        assert len(temp_db.list_keys("ns2")) == 1

    def test_get_all_namespaces(self, temp_db: SwarmDB):
        """Test retrieving list of all namespaces."""
        temp_db.set("alpha", "key", "value")
        temp_db.set("beta", "key", "value")
        temp_db.set("gamma", "key", "value")

        namespaces = temp_db.get_namespaces()

        assert len(namespaces) == 3
        assert "alpha" in namespaces
        assert "beta" in namespaces
        assert "gamma" in namespaces


class TestSwarmDBJSONSerialization:
    """Test suite for JSON serialization and deserialization."""

    def test_store_dict(self, temp_db: SwarmDB):
        """Test storing and retrieving dictionary."""
        data = {"name": "Alice", "age": 30, "active": True}
        temp_db.set("test", "user", data)

        result = temp_db.get("test", "user")

        assert result == data
        assert isinstance(result, dict)

    def test_store_list(self, temp_db: SwarmDB):
        """Test storing and retrieving list."""
        data = [1, 2, 3, "four", {"five": 5}]
        temp_db.set("test", "items", data)

        result = temp_db.get("test", "items")

        assert result == data
        assert isinstance(result, list)

    def test_store_nested_structure(self, temp_db: SwarmDB):
        """Test storing and retrieving nested JSON structure."""
        data = {
            "users": [
                {"id": 1, "name": "Alice", "tags": ["admin", "user"]},
                {"id": 2, "name": "Bob", "tags": ["user"]},
            ],
            "metadata": {"version": "1.0", "count": 2},
        }
        temp_db.set("test", "complex", data)

        result = temp_db.get("test", "complex")

        assert result == data
        assert result["users"][0]["name"] == "Alice"
        assert result["metadata"]["version"] == "1.0"

    def test_store_primitives(self, temp_db: SwarmDB):
        """Test storing primitive types."""
        temp_db.set("test", "string", "hello")
        temp_db.set("test", "int", 42)
        temp_db.set("test", "float", 3.14)
        temp_db.set("test", "bool", True)
        temp_db.set("test", "none", None)

        assert temp_db.get("test", "string") == "hello"
        assert temp_db.get("test", "int") == 42
        assert temp_db.get("test", "float") == 3.14
        assert temp_db.get("test", "bool") is True
        assert temp_db.get("test", "none") is None

    def test_unicode_handling(self, temp_db: SwarmDB):
        """Test handling of unicode characters."""
        data = {"greeting": "안녕하세요", "emoji": "🚀", "chinese": "你好"}
        temp_db.set("test", "unicode", data)

        result = temp_db.get("test", "unicode")

        assert result == data
        assert result["greeting"] == "안녕하세요"

    def test_special_characters(self, temp_db: SwarmDB):
        """Test handling of special characters in keys and values."""
        special_key = "key:with:colons/and/slashes"
        special_value = {"data": "value\nwith\ttabs\nand\"quotes\""}

        temp_db.set("test", special_key, special_value)
        result = temp_db.get("test", special_key)

        assert result == special_value

    def test_invalid_json_handling(self, temp_db: SwarmDB):
        """Test handling of non-JSON-serializable objects."""
        # Custom object that can't be JSON serialized
        class CustomObject:
            pass

        with pytest.raises((TypeError, ValueError)):
            temp_db.set("test", "invalid", CustomObject())


class TestSwarmDBContextOperations:
    """Test suite for context save/load operations."""

    def test_save_context(self, temp_db: SwarmDB):
        """Test saving a context."""
        context_data = {
            "session_id": "sess_123",
            "user": "alice",
            "preferences": {"theme": "dark", "lang": "en"},
        }

        context_id = temp_db.save_context(
            namespace="sessions", context_data=context_data
        )

        assert context_id is not None
        assert isinstance(context_id, str)

    def test_load_context(self, temp_db: SwarmDB):
        """Test loading a saved context."""
        context_data = {"key": "value", "count": 42}

        context_id = temp_db.save_context("test", context_data)
        loaded = temp_db.load_context("test", context_id)

        assert loaded == context_data

    def test_load_nonexistent_context(self, temp_db: SwarmDB):
        """Test loading non-existent context returns None."""
        result = temp_db.load_context("test", "nonexistent_id")

        assert result is None

    def test_list_contexts(self, temp_db: SwarmDB):
        """Test listing all contexts in a namespace."""
        temp_db.save_context("test", {"data": "ctx1"})
        temp_db.save_context("test", {"data": "ctx2"})
        temp_db.save_context("other", {"data": "ctx3"})

        contexts = temp_db.list_contexts("test")

        assert len(contexts) == 2

    def test_delete_context(self, temp_db: SwarmDB):
        """Test deleting a context."""
        context_id = temp_db.save_context("test", {"data": "delete_me"})

        deleted = temp_db.delete_context("test", context_id)

        assert deleted is True
        assert temp_db.load_context("test", context_id) is None

    def test_update_context(self, temp_db: SwarmDB):
        """Test updating an existing context."""
        context_id = temp_db.save_context("test", {"version": 1})

        updated = temp_db.update_context(
            "test", context_id, {"version": 2, "new_field": "added"}
        )

        assert updated is True
        loaded = temp_db.load_context("test", context_id)
        assert loaded["version"] == 2
        assert loaded["new_field"] == "added"


class TestSwarmDBConcurrentAccess:
    """Test suite for thread safety and concurrent access."""

    def test_concurrent_writes(self, temp_db: SwarmDB):
        """Test concurrent write operations from multiple threads."""

        def write_value(thread_id: int):
            for i in range(10):
                temp_db.set("concurrent", f"key_{thread_id}_{i}", f"value_{i}")

        threads = []
        for i in range(5):
            thread = threading.Thread(target=write_value, args=(i,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # Verify all writes succeeded
        keys = temp_db.list_keys("concurrent")
        assert len(keys) == 50  # 5 threads * 10 writes each

    def test_concurrent_reads(self, temp_db: SwarmDB):
        """Test concurrent read operations."""
        # Prepare data
        for i in range(100):
            temp_db.set("concurrent", f"key_{i}", f"value_{i}")

        results = []

        def read_value(key_id: int):
            value = temp_db.get("concurrent", f"key_{key_id}")
            results.append(value)

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(read_value, i) for i in range(100)]
            for future in futures:
                future.result()

        assert len(results) == 100
        assert all(r is not None for r in results)

    def test_concurrent_read_write(self, temp_db: SwarmDB):
        """Test mixed concurrent read and write operations."""
        temp_db.set("concurrent", "counter", 0)

        def increment():
            for _ in range(10):
                current = temp_db.get("concurrent", "counter")
                temp_db.set("concurrent", "counter", current + 1)

        threads = [threading.Thread(target=increment) for _ in range(5)]

        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        # Note: Without proper locking, final value may be less than 50
        # This test verifies no corruption occurs
        final_value = temp_db.get("concurrent", "counter")
        assert isinstance(final_value, int)
        assert final_value > 0

    def test_transaction_isolation(self, temp_file_db):
        """Test transaction isolation between connections."""
        db1, db_file = temp_file_db
        db2 = SwarmDB(db_path=str(db_file))

        db1.set("test", "key", "value1")
        value_from_db2 = db2.get("test", "key")

        # Should see the committed value
        assert value_from_db2 == "value1"


class TestSwarmDBErrorHandling:
    """Test suite for error handling and edge cases."""

    def test_empty_namespace(self, temp_db: SwarmDB):
        """Test operations with empty namespace."""
        with pytest.raises(ValueError):
            temp_db.set("", "key", "value")

    def test_empty_key(self, temp_db: SwarmDB):
        """Test operations with empty key."""
        with pytest.raises(ValueError):
            temp_db.set("test", "", "value")

    def test_none_namespace(self, temp_db: SwarmDB):
        """Test operations with None namespace."""
        with pytest.raises((ValueError, TypeError)):
            temp_db.set(None, "key", "value")

    def test_none_key(self, temp_db: SwarmDB):
        """Test operations with None key."""
        with pytest.raises((ValueError, TypeError)):
            temp_db.set("test", None, "value")

    def test_very_large_value(self, temp_db: SwarmDB):
        """Test storing very large values."""
        large_data = {"data": "x" * 1_000_000}  # 1MB string

        temp_db.set("test", "large", large_data)
        result = temp_db.get("test", "large")

        assert result == large_data

    def test_corrupted_json_recovery(self, temp_db: SwarmDB):
        """Test recovery from corrupted JSON data."""
        # Manually insert corrupted JSON
        conn = temp_db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO key_value_store (namespace, key, value) VALUES (?, ?, ?)",
            ("test", "corrupted", "invalid json {{{"),
        )
        conn.commit()

        # Should handle gracefully
        result = temp_db.get("test", "corrupted")
        assert result is None or isinstance(result, str)

    def test_database_path_invalid(self):
        """Test initialization with invalid database path."""
        with pytest.raises((OSError, sqlite3.Error)):
            SwarmDB(db_path="/invalid/path/to/db.sqlite")

    def test_max_key_length(self, temp_db: SwarmDB):
        """Test handling of maximum key length."""
        long_key = "k" * 1000

        temp_db.set("test", long_key, "value")
        result = temp_db.get("test", long_key)

        assert result == "value"

    def test_special_sqlite_characters(self, temp_db: SwarmDB):
        """Test handling SQL injection attempts."""
        malicious_key = "key'; DROP TABLE key_value_store; --"

        temp_db.set("test", malicious_key, "safe_value")
        result = temp_db.get("test", malicious_key)

        assert result == "safe_value"
        # Verify table still exists
        assert "key_value_store" in temp_db.get_table_names()


class TestSwarmDBStatistics:
    """Test suite for statistics and metrics."""

    def test_count_keys_in_namespace(self, temp_db: SwarmDB):
        """Test counting keys in a namespace."""
        temp_db.set("test", "key1", "value1")
        temp_db.set("test", "key2", "value2")
        temp_db.set("other", "key3", "value3")

        count = temp_db.count_keys("test")

        assert count == 2

    def test_get_database_size(self, temp_file_db):
        """Test getting database file size."""
        db, db_file = temp_file_db

        # Add some data
        for i in range(100):
            db.set("test", f"key_{i}", {"data": "x" * 100})

        size = db.get_database_size()

        assert size > 0
        assert isinstance(size, int)

    def test_get_statistics(self, temp_db: SwarmDB):
        """Test getting comprehensive database statistics."""
        temp_db.set("ns1", "key1", "value1")
        temp_db.set("ns1", "key2", "value2")
        temp_db.set("ns2", "key3", "value3")
        temp_db.save_context("ctx", {"data": "context"})

        stats = temp_db.get_statistics()

        assert stats["total_keys"] == 3
        assert stats["total_namespaces"] == 2
        assert stats["total_contexts"] >= 1
        assert "ns1" in stats["keys_per_namespace"]
        assert stats["keys_per_namespace"]["ns1"] == 2

    def test_vacuum_database(self, temp_file_db):
        """Test database vacuum operation."""
        db, db_file = temp_file_db

        # Add and delete data to create fragmentation
        for i in range(100):
            db.set("test", f"key_{i}", "value" * 100)
        for i in range(50):
            db.delete("test", f"key_{i}")

        size_before = db_file.stat().st_size
        db.vacuum()
        size_after = db_file.stat().st_size

        # Size should be reduced or equal after vacuum
        assert size_after <= size_before


class TestSwarmDBPersistence:
    """Test suite for data persistence across sessions."""

    def test_data_persists_across_connections(self, tmp_path: Path):
        """Test that data persists when reopening database."""
        db_file = tmp_path / "persist.db"

        # First session
        db1 = SwarmDB(db_path=str(db_file))
        db1.set("test", "persistent", "value")
        del db1  # Close connection

        # Second session
        db2 = SwarmDB(db_path=str(db_file))
        result = db2.get("test", "persistent")

        assert result == "value"

    def test_contexts_persist(self, tmp_path: Path):
        """Test that contexts persist across sessions."""
        db_file = tmp_path / "contexts.db"

        db1 = SwarmDB(db_path=str(db_file))
        ctx_id = db1.save_context("test", {"session": "data"})
        del db1

        db2 = SwarmDB(db_path=str(db_file))
        loaded = db2.load_context("test", ctx_id)

        assert loaded == {"session": "data"}

    def test_timestamps_preserved(self, tmp_path: Path):
        """Test that timestamps are preserved across sessions."""
        db_file = tmp_path / "timestamps.db"

        db1 = SwarmDB(db_path=str(db_file))
        db1.set("test", "key", "value")
        ts1 = db1.get_timestamp("test", "key")
        del db1

        db2 = SwarmDB(db_path=str(db_file))
        ts2 = db2.get_timestamp("test", "key")

        assert ts1 == ts2


class TestSwarmDBAdvancedFeatures:
    """Test suite for advanced features and utilities."""

    def test_bulk_insert(self, temp_db: SwarmDB):
        """Test bulk insertion of multiple key-value pairs."""
        data = {f"key_{i}": f"value_{i}" for i in range(100)}

        temp_db.bulk_set("test", data)

        assert temp_db.count_keys("test") == 100
        assert temp_db.get("test", "key_50") == "value_50"

    def test_bulk_get(self, temp_db: SwarmDB):
        """Test bulk retrieval of multiple keys."""
        for i in range(10):
            temp_db.set("test", f"key_{i}", f"value_{i}")

        keys = [f"key_{i}" for i in range(0, 10, 2)]
        results = temp_db.bulk_get("test", keys)

        assert len(results) == 5
        assert results["key_0"] == "value_0"
        assert results["key_8"] == "value_8"

    def test_search_keys_by_pattern(self, temp_db: SwarmDB):
        """Test searching keys by pattern."""
        temp_db.set("test", "user_alice", "data1")
        temp_db.set("test", "user_bob", "data2")
        temp_db.set("test", "admin_charlie", "data3")

        user_keys = temp_db.search_keys("test", pattern="user_*")

        assert len(user_keys) == 2
        assert "user_alice" in user_keys
        assert "user_bob" in user_keys

    def test_export_namespace(self, temp_db: SwarmDB):
        """Test exporting namespace to dict."""
        temp_db.set("test", "key1", "value1")
        temp_db.set("test", "key2", {"nested": "data"})

        exported = temp_db.export_namespace("test")

        assert exported == {"key1": "value1", "key2": {"nested": "data"}}

    def test_import_namespace(self, temp_db: SwarmDB):
        """Test importing dict as namespace."""
        data = {
            "key1": "value1",
            "key2": [1, 2, 3],
            "key3": {"nested": "object"},
        }

        temp_db.import_namespace("test", data)

        assert temp_db.get("test", "key1") == "value1"
        assert temp_db.get("test", "key2") == [1, 2, 3]
        assert temp_db.get("test", "key3") == {"nested": "object"}

    def test_clone_namespace(self, temp_db: SwarmDB):
        """Test cloning a namespace."""
        temp_db.set("source", "key1", "value1")
        temp_db.set("source", "key2", "value2")

        temp_db.clone_namespace("source", "destination")

        assert temp_db.get("destination", "key1") == "value1"
        assert temp_db.get("destination", "key2") == "value2"
        # Original should still exist
        assert temp_db.get("source", "key1") == "value1"


# Performance and stress tests
class TestSwarmDBPerformance:
    """Performance and stress tests."""

    @pytest.mark.slow
    def test_large_volume_operations(self, temp_db: SwarmDB):
        """Test performance with large number of operations."""
        import time

        start = time.time()

        # Insert 10,000 records
        for i in range(10_000):
            temp_db.set("perf", f"key_{i}", f"value_{i}")

        elapsed = time.time() - start

        # Should complete in reasonable time (adjust threshold as needed)
        assert elapsed < 10.0  # 10 seconds for 10k inserts
        assert temp_db.count_keys("perf") == 10_000

    @pytest.mark.slow
    def test_query_performance(self, temp_db: SwarmDB):
        """Test query performance with large dataset."""
        # Prepare large dataset
        for i in range(1_000):
            temp_db.set("perf", f"key_{i}", {"data": "x" * 100})

        import time

        start = time.time()

        # Perform 1000 queries
        for i in range(1_000):
            temp_db.get("perf", f"key_{i % 1000}")

        elapsed = time.time() - start

        # Should handle queries efficiently
        assert elapsed < 2.0  # 2 seconds for 1k queries
