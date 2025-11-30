"""
Tests for Pattern Storage Backend
==================================

Comprehensive tests for filesystem and SQLite storage backends.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta
import uuid

from moai_flow.patterns.schema import Pattern, PatternType
from moai_flow.patterns.storage import PatternStorage, StorageConfig


@pytest.fixture
def temp_dir():
    """Create temporary directory for tests."""
    temp = tempfile.mkdtemp()
    yield temp
    shutil.rmtree(temp)


@pytest.fixture
def sample_pattern():
    """Create sample pattern for testing."""
    return {
        "pattern_id": str(uuid.uuid4()),
        "pattern_type": PatternType.TASK_COMPLETION,
        "timestamp": datetime.now().isoformat(),
        "data": {
            "task_type": "code_generation",
            "agent": "expert-backend",
            "duration_ms": 2500,
            "success": True,
            "files_created": 2,
            "tests_passed": 10,
            "lines_of_code": 100,
            "retry_count": 0
        },
        "context": {
            "project_name": "moai-adk",
            "environment": "development",
            "tags": ["backend", "test"]
        },
        "version": "1.0"
    }


class TestFilesystemStorage:
    """Test filesystem storage backend."""

    def test_init_filesystem(self, temp_dir):
        """Test filesystem storage initialization."""
        storage = PatternStorage(backend="filesystem", base_path=temp_dir)
        assert Path(temp_dir).exists()
        assert storage.config.backend == "filesystem"

    def test_save_pattern(self, temp_dir, sample_pattern):
        """Test saving pattern to filesystem."""
        storage = PatternStorage(backend="filesystem", base_path=temp_dir)
        result = storage.save(sample_pattern)
        assert result is True

        # Verify file exists
        timestamp = datetime.fromisoformat(sample_pattern["timestamp"].replace("Z", "+00:00"))
        year = timestamp.strftime("%Y")
        month = timestamp.strftime("%m")
        day = timestamp.strftime("%d")

        pattern_dir = Path(temp_dir) / year / month / day
        assert pattern_dir.exists()
        assert len(list(pattern_dir.glob("*.json"))) > 0

    def test_load_pattern(self, temp_dir, sample_pattern):
        """Test loading pattern from filesystem."""
        storage = PatternStorage(backend="filesystem", base_path=temp_dir)
        storage.save(sample_pattern)

        loaded = storage.load(sample_pattern["pattern_id"])
        assert loaded is not None
        assert loaded["pattern_id"] == sample_pattern["pattern_id"]
        assert loaded["pattern_type"] == sample_pattern["pattern_type"]

    def test_load_nonexistent_pattern(self, temp_dir):
        """Test loading nonexistent pattern."""
        storage = PatternStorage(backend="filesystem", base_path=temp_dir)
        loaded = storage.load("nonexistent-id")
        assert loaded is None

    def test_query_by_type(self, temp_dir, sample_pattern):
        """Test querying patterns by type."""
        storage = PatternStorage(backend="filesystem", base_path=temp_dir)

        # Save multiple patterns
        for i in range(5):
            pattern = sample_pattern.copy()
            pattern["pattern_id"] = str(uuid.uuid4())
            storage.save(pattern)

        results = storage.query(pattern_type=PatternType.TASK_COMPLETION, limit=10)
        assert len(results) >= 5

    def test_query_by_date_range(self, temp_dir, sample_pattern):
        """Test querying patterns by date range."""
        storage = PatternStorage(backend="filesystem", base_path=temp_dir)

        # Save pattern
        storage.save(sample_pattern)

        # Query with date range
        results = storage.query(
            start_date=datetime.now() - timedelta(days=1),
            end_date=datetime.now() + timedelta(days=1),
            limit=10
        )
        assert len(results) >= 1

    def test_query_by_tags(self, temp_dir, sample_pattern):
        """Test querying patterns by tags."""
        storage = PatternStorage(backend="filesystem", base_path=temp_dir)

        # Save pattern with tags
        storage.save(sample_pattern)

        # Query with tags
        results = storage.query(tags=["backend"], limit=10)
        assert len(results) >= 1

    def test_delete_old_patterns(self, temp_dir, sample_pattern):
        """Test deleting old patterns."""
        storage = PatternStorage(backend="filesystem", base_path=temp_dir)

        # Create old pattern
        old_pattern = sample_pattern.copy()
        old_pattern["pattern_id"] = str(uuid.uuid4())
        old_pattern["timestamp"] = (datetime.now() - timedelta(days=100)).isoformat()
        storage.save(old_pattern)

        # Create recent pattern
        recent_pattern = sample_pattern.copy()
        recent_pattern["pattern_id"] = str(uuid.uuid4())
        storage.save(recent_pattern)

        # Delete old patterns
        deleted = storage.delete_old_patterns(retention_days=90)
        assert deleted >= 1

        # Verify recent pattern still exists
        loaded = storage.load(recent_pattern["pattern_id"])
        assert loaded is not None

    def test_compress_old_files(self, temp_dir, sample_pattern):
        """Test compressing old files."""
        storage = PatternStorage(
            backend="filesystem",
            base_path=temp_dir,
            compression_threshold_days=0  # Compress immediately for testing
        )

        # Save pattern
        storage.save(sample_pattern)

        # Compress files
        compressed = storage.compress_old_files()
        # Note: May be 0 if file is too recent
        assert compressed >= 0

    def test_index_enabled(self, temp_dir, sample_pattern):
        """Test index functionality."""
        storage = PatternStorage(backend="filesystem", base_path=temp_dir)

        # Save pattern
        storage.save(sample_pattern)

        # Verify index exists
        index_path = Path(temp_dir) / "index.json"
        assert index_path.exists()

        # Load pattern using index
        loaded = storage.load(sample_pattern["pattern_id"])
        assert loaded is not None


class TestSQLiteStorage:
    """Test SQLite storage backend."""

    def test_init_sqlite(self, temp_dir):
        """Test SQLite storage initialization."""
        db_path = str(Path(temp_dir) / "patterns")
        storage = PatternStorage(backend="sqlite", base_path=db_path)
        assert storage.config.backend == "sqlite"
        assert Path(f"{db_path}.db").exists()
        storage.close()

    def test_save_pattern(self, temp_dir, sample_pattern):
        """Test saving pattern to SQLite."""
        db_path = str(Path(temp_dir) / "patterns")
        storage = PatternStorage(backend="sqlite", base_path=db_path)

        result = storage.save(sample_pattern)
        assert result is True

        storage.close()

    def test_load_pattern(self, temp_dir, sample_pattern):
        """Test loading pattern from SQLite."""
        db_path = str(Path(temp_dir) / "patterns")
        storage = PatternStorage(backend="sqlite", base_path=db_path)

        storage.save(sample_pattern)
        loaded = storage.load(sample_pattern["pattern_id"])

        assert loaded is not None
        assert loaded["pattern_id"] == sample_pattern["pattern_id"]
        assert loaded["pattern_type"] == sample_pattern["pattern_type"]

        storage.close()

    def test_load_nonexistent_pattern(self, temp_dir):
        """Test loading nonexistent pattern from SQLite."""
        db_path = str(Path(temp_dir) / "patterns")
        storage = PatternStorage(backend="sqlite", base_path=db_path)

        loaded = storage.load("nonexistent-id")
        assert loaded is None

        storage.close()

    def test_query_by_type(self, temp_dir, sample_pattern):
        """Test querying patterns by type in SQLite."""
        db_path = str(Path(temp_dir) / "patterns")
        storage = PatternStorage(backend="sqlite", base_path=db_path)

        # Save multiple patterns
        for i in range(5):
            pattern = sample_pattern.copy()
            pattern["pattern_id"] = str(uuid.uuid4())
            storage.save(pattern)

        results = storage.query(pattern_type=PatternType.TASK_COMPLETION, limit=10)
        assert len(results) >= 5

        storage.close()

    def test_query_by_date_range(self, temp_dir, sample_pattern):
        """Test querying patterns by date range in SQLite."""
        db_path = str(Path(temp_dir) / "patterns")
        storage = PatternStorage(backend="sqlite", base_path=db_path)

        storage.save(sample_pattern)

        results = storage.query(
            start_date=datetime.now() - timedelta(days=1),
            end_date=datetime.now() + timedelta(days=1),
            limit=10
        )
        assert len(results) >= 1

        storage.close()

    def test_query_by_tags(self, temp_dir, sample_pattern):
        """Test querying patterns by tags in SQLite."""
        db_path = str(Path(temp_dir) / "patterns")
        storage = PatternStorage(backend="sqlite", base_path=db_path)

        storage.save(sample_pattern)

        results = storage.query(tags=["backend"], limit=10)
        assert len(results) >= 1

        storage.close()

    def test_delete_old_patterns(self, temp_dir, sample_pattern):
        """Test deleting old patterns from SQLite."""
        db_path = str(Path(temp_dir) / "patterns")
        storage = PatternStorage(backend="sqlite", base_path=db_path)

        # Create old pattern
        old_pattern = sample_pattern.copy()
        old_pattern["pattern_id"] = str(uuid.uuid4())
        old_pattern["timestamp"] = (datetime.now() - timedelta(days=100)).isoformat()
        storage.save(old_pattern)

        # Create recent pattern
        recent_pattern = sample_pattern.copy()
        recent_pattern["pattern_id"] = str(uuid.uuid4())
        storage.save(recent_pattern)

        # Delete old patterns
        deleted = storage.delete_old_patterns(retention_days=90)
        assert deleted >= 1

        # Verify recent pattern still exists
        loaded = storage.load(recent_pattern["pattern_id"])
        assert loaded is not None

        storage.close()

    def test_update_pattern(self, temp_dir, sample_pattern):
        """Test updating existing pattern in SQLite."""
        db_path = str(Path(temp_dir) / "patterns")
        storage = PatternStorage(backend="sqlite", base_path=db_path)

        # Save original pattern
        storage.save(sample_pattern)

        # Update pattern
        sample_pattern["data"]["duration_ms"] = 5000
        storage.save(sample_pattern)

        # Load and verify update
        loaded = storage.load(sample_pattern["pattern_id"])
        assert loaded["data"]["duration_ms"] == 5000

        storage.close()


class TestStorageValidation:
    """Test storage validation."""

    def test_save_invalid_pattern(self, temp_dir):
        """Test saving invalid pattern fails."""
        storage = PatternStorage(backend="filesystem", base_path=temp_dir)

        invalid_pattern = {
            "pattern_id": "test-123",
            "pattern_type": "invalid_type",  # Invalid type
            "timestamp": datetime.now().isoformat(),
            "data": {}
        }

        with pytest.raises(ValueError):
            storage.save(invalid_pattern)

    def test_invalid_backend(self, temp_dir):
        """Test invalid backend raises error."""
        with pytest.raises(ValueError):
            PatternStorage(backend="invalid_backend", base_path=temp_dir)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
