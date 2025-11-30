"""
Pattern Storage Backend for MoAI-Flow
======================================

Flexible storage backend supporting filesystem and SQLite.
Provides pattern persistence, querying, and lifecycle management.
"""

import json
import gzip
import sqlite3
from pathlib import Path
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime, timedelta
from dataclasses import dataclass

from .schema import Pattern, PatternType, PatternSchema


@dataclass
class StorageConfig:
    """Storage configuration."""
    backend: Literal["filesystem", "sqlite"]
    base_path: str
    compression_threshold_days: int = 30
    retention_days: int = 90
    index_enabled: bool = True


class PatternStorage:
    """
    Pattern storage backend.

    Supports multiple storage backends:
    - File system (default) - Date-based hierarchy with optional compression
    - SQLite (optional) - Relational database with indexing
    """

    def __init__(
        self,
        backend: Literal["filesystem", "sqlite"] = "filesystem",
        base_path: str = ".moai/patterns",
        compression_threshold_days: int = 30,
        retention_days: int = 90
    ):
        """
        Initialize pattern storage.

        Args:
            backend: Storage backend type ("filesystem" or "sqlite")
            base_path: Base directory/database path for storage
            compression_threshold_days: Compress files older than this
            retention_days: Delete patterns older than this
        """
        self.config = StorageConfig(
            backend=backend,
            base_path=base_path,
            compression_threshold_days=compression_threshold_days,
            retention_days=retention_days
        )
        self.base_path = Path(base_path)

        if backend == "filesystem":
            self._init_filesystem()
        elif backend == "sqlite":
            self._init_sqlite()
        else:
            raise ValueError(f"Unsupported backend: {backend}")

    def _init_filesystem(self) -> None:
        """Initialize filesystem backend."""
        self.base_path.mkdir(parents=True, exist_ok=True)

        # Create index file if enabled
        if self.config.index_enabled:
            self.index_path = self.base_path / "index.json"
            if not self.index_path.exists():
                self._save_index({})

    def _init_sqlite(self) -> None:
        """Initialize SQLite backend."""
        self.base_path.parent.mkdir(parents=True, exist_ok=True)
        db_path = str(self.base_path.with_suffix(".db"))

        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row

        # Create tables
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS patterns (
                pattern_id TEXT PRIMARY KEY,
                pattern_type TEXT NOT NULL,
                timestamp INTEGER NOT NULL,
                data TEXT NOT NULL,
                context TEXT,
                version TEXT DEFAULT '1.0',
                created_at INTEGER DEFAULT (strftime('%s', 'now'))
            )
        """)

        # Create indexes
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_type_timestamp
            ON patterns(pattern_type, timestamp)
        """)
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_created_at
            ON patterns(created_at)
        """)

        self.conn.commit()

    def save(self, pattern: Pattern) -> bool:
        """
        Save pattern to storage.

        Args:
            pattern: Pattern to save

        Returns:
            True if saved successfully, False otherwise
        """
        # Validate pattern
        if not PatternSchema.validate_pattern(pattern):
            raise ValueError("Invalid pattern schema")

        if self.config.backend == "filesystem":
            return self._save_filesystem(pattern)
        elif self.config.backend == "sqlite":
            return self._save_sqlite(pattern)

        return False

    def _save_filesystem(self, pattern: Pattern) -> bool:
        """Save pattern to filesystem."""
        # Create date-based hierarchy
        timestamp = datetime.fromisoformat(pattern["timestamp"].replace("Z", "+00:00"))
        year = timestamp.strftime("%Y")
        month = timestamp.strftime("%m")
        day = timestamp.strftime("%d")

        dir_path = self.base_path / year / month / day
        dir_path.mkdir(parents=True, exist_ok=True)

        # Generate filename
        pattern_type = pattern["pattern_type"]
        timestamp_str = timestamp.strftime("%Y%m%d_%H%M%S")
        filename = f"{pattern_type}_{timestamp_str}_{pattern['pattern_id'][:8]}.json"
        file_path = dir_path / filename

        # Save pattern
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(pattern, f, indent=2, ensure_ascii=False)

        # Update index
        if self.config.index_enabled:
            self._update_index(pattern, str(file_path.relative_to(self.base_path)))

        return True

    def _save_sqlite(self, pattern: Pattern) -> bool:
        """Save pattern to SQLite."""
        timestamp = datetime.fromisoformat(pattern["timestamp"].replace("Z", "+00:00"))

        try:
            self.conn.execute("""
                INSERT OR REPLACE INTO patterns
                (pattern_id, pattern_type, timestamp, data, context, version)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                pattern["pattern_id"],
                pattern["pattern_type"],
                int(timestamp.timestamp()),
                json.dumps(pattern["data"]),
                json.dumps(pattern.get("context", {})),
                pattern.get("version", "1.0")
            ))
            self.conn.commit()
            return True
        except sqlite3.Error:
            return False

    def load(self, pattern_id: str) -> Optional[Pattern]:
        """
        Load pattern by ID.

        Args:
            pattern_id: Pattern identifier

        Returns:
            Pattern if found, None otherwise
        """
        if self.config.backend == "filesystem":
            return self._load_filesystem(pattern_id)
        elif self.config.backend == "sqlite":
            return self._load_sqlite(pattern_id)

        return None

    def _load_filesystem(self, pattern_id: str) -> Optional[Pattern]:
        """Load pattern from filesystem."""
        # Check index first
        if self.config.index_enabled:
            index = self._load_index()
            if pattern_id in index:
                file_path = self.base_path / index[pattern_id]["path"]
                return self._read_pattern_file(file_path)

        # Fallback: scan all files
        for file_path in self.base_path.rglob("*.json"):
            if file_path.name == "index.json":
                continue

            pattern = self._read_pattern_file(file_path)
            if pattern and pattern["pattern_id"] == pattern_id:
                return pattern

        # Try compressed files
        for file_path in self.base_path.rglob("*.json.gz"):
            pattern = self._read_pattern_file(file_path)
            if pattern and pattern["pattern_id"] == pattern_id:
                return pattern

        return None

    def _load_sqlite(self, pattern_id: str) -> Optional[Pattern]:
        """Load pattern from SQLite."""
        cursor = self.conn.execute(
            "SELECT * FROM patterns WHERE pattern_id = ?",
            (pattern_id,)
        )
        row = cursor.fetchone()

        if row:
            return self._row_to_pattern(row)

        return None

    def query(
        self,
        pattern_type: Optional[PatternType] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        tags: Optional[List[str]] = None
    ) -> List[Pattern]:
        """
        Query patterns with filters.

        Args:
            pattern_type: Filter by pattern type
            start_date: Filter patterns after this date
            end_date: Filter patterns before this date
            limit: Maximum number of results
            tags: Filter by context tags

        Returns:
            List of matching patterns
        """
        if self.config.backend == "filesystem":
            return self._query_filesystem(pattern_type, start_date, end_date, limit, tags)
        elif self.config.backend == "sqlite":
            return self._query_sqlite(pattern_type, start_date, end_date, limit, tags)

        return []

    def _query_filesystem(
        self,
        pattern_type: Optional[PatternType],
        start_date: Optional[datetime],
        end_date: Optional[datetime],
        limit: int,
        tags: Optional[List[str]]
    ) -> List[Pattern]:
        """Query patterns from filesystem."""
        results = []

        # Use index if available
        if self.config.index_enabled and pattern_type:
            index = self._load_index()
            for pattern_id, entry in index.items():
                if entry.get("type") == pattern_type:
                    file_path = self.base_path / entry["path"]
                    pattern = self._read_pattern_file(file_path)
                    if pattern and self._matches_filters(pattern, start_date, end_date, tags):
                        results.append(pattern)
                        if len(results) >= limit:
                            break
            return results

        # Fallback: scan files
        for file_path in sorted(self.base_path.rglob("*.json"), reverse=True):
            if file_path.name == "index.json":
                continue

            pattern = self._read_pattern_file(file_path)
            if pattern and self._matches_filters(pattern, start_date, end_date, tags):
                if not pattern_type or pattern["pattern_type"] == pattern_type:
                    results.append(pattern)
                    if len(results) >= limit:
                        break

        return results

    def _query_sqlite(
        self,
        pattern_type: Optional[PatternType],
        start_date: Optional[datetime],
        end_date: Optional[datetime],
        limit: int,
        tags: Optional[List[str]]
    ) -> List[Pattern]:
        """Query patterns from SQLite."""
        query = "SELECT * FROM patterns WHERE 1=1"
        params = []

        if pattern_type:
            query += " AND pattern_type = ?"
            params.append(pattern_type)

        if start_date:
            query += " AND timestamp >= ?"
            params.append(int(start_date.timestamp()))

        if end_date:
            query += " AND timestamp <= ?"
            params.append(int(end_date.timestamp()))

        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        cursor = self.conn.execute(query, params)
        results = [self._row_to_pattern(row) for row in cursor.fetchall()]

        # Filter by tags if specified
        if tags:
            results = [
                p for p in results
                if self._pattern_has_tags(p, tags)
            ]

        return results

    def delete_old_patterns(self, retention_days: int) -> int:
        """
        Delete patterns older than retention period.

        Args:
            retention_days: Delete patterns older than this

        Returns:
            Number of patterns deleted
        """
        cutoff_date = datetime.now() - timedelta(days=retention_days)

        if self.config.backend == "filesystem":
            return self._delete_old_filesystem(cutoff_date)
        elif self.config.backend == "sqlite":
            return self._delete_old_sqlite(cutoff_date)

        return 0

    def _delete_old_filesystem(self, cutoff_date: datetime) -> int:
        """Delete old patterns from filesystem."""
        deleted = 0

        for file_path in self.base_path.rglob("*.json"):
            if file_path.name == "index.json":
                continue

            pattern = self._read_pattern_file(file_path)
            if pattern:
                timestamp = datetime.fromisoformat(pattern["timestamp"].replace("Z", "+00:00"))
                if timestamp < cutoff_date:
                    file_path.unlink()
                    deleted += 1

                    # Update index
                    if self.config.index_enabled:
                        self._remove_from_index(pattern["pattern_id"])

        # Also delete compressed files
        for file_path in self.base_path.rglob("*.json.gz"):
            pattern = self._read_pattern_file(file_path)
            if pattern:
                timestamp = datetime.fromisoformat(pattern["timestamp"].replace("Z", "+00:00"))
                if timestamp < cutoff_date:
                    file_path.unlink()
                    deleted += 1

        return deleted

    def _delete_old_sqlite(self, cutoff_date: datetime) -> int:
        """Delete old patterns from SQLite."""
        cursor = self.conn.execute(
            "DELETE FROM patterns WHERE timestamp < ?",
            (int(cutoff_date.timestamp()),)
        )
        self.conn.commit()
        return cursor.rowcount

    def compress_old_files(self) -> int:
        """
        Compress files older than compression threshold.

        Returns:
            Number of files compressed
        """
        if self.config.backend != "filesystem":
            return 0

        compressed = 0
        cutoff_date = datetime.now() - timedelta(days=self.config.compression_threshold_days)

        for file_path in self.base_path.rglob("*.json"):
            if file_path.name == "index.json":
                continue

            # Check file modification time
            mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
            if mtime < cutoff_date:
                # Compress file
                gz_path = file_path.with_suffix(".json.gz")
                with open(file_path, 'rb') as f_in:
                    with gzip.open(gz_path, 'wb') as f_out:
                        f_out.writelines(f_in)

                # Remove original
                file_path.unlink()
                compressed += 1

        return compressed

    # Helper methods

    def _read_pattern_file(self, file_path: Path) -> Optional[Pattern]:
        """Read pattern from file (handles both plain and gzipped)."""
        try:
            if file_path.suffix == ".gz":
                with gzip.open(file_path, 'rt', encoding='utf-8') as f:
                    return json.load(f)
            else:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None

    def _row_to_pattern(self, row: sqlite3.Row) -> Pattern:
        """Convert SQLite row to Pattern."""
        timestamp = datetime.fromtimestamp(row["timestamp"]).isoformat()

        return {
            "pattern_id": row["pattern_id"],
            "pattern_type": row["pattern_type"],
            "timestamp": timestamp,
            "data": json.loads(row["data"]),
            "context": json.loads(row["context"]) if row["context"] else {},
            "version": row["version"]
        }

    def _matches_filters(
        self,
        pattern: Pattern,
        start_date: Optional[datetime],
        end_date: Optional[datetime],
        tags: Optional[List[str]]
    ) -> bool:
        """Check if pattern matches query filters."""
        timestamp = datetime.fromisoformat(pattern["timestamp"].replace("Z", "+00:00"))

        if start_date and timestamp < start_date:
            return False

        if end_date and timestamp > end_date:
            return False

        if tags and not self._pattern_has_tags(pattern, tags):
            return False

        return True

    def _pattern_has_tags(self, pattern: Pattern, tags: List[str]) -> bool:
        """Check if pattern has all specified tags."""
        pattern_tags = pattern.get("context", {}).get("tags", [])
        return all(tag in pattern_tags for tag in tags)

    def _load_index(self) -> Dict[str, Any]:
        """Load filesystem index."""
        if not self.index_path.exists():
            return {}

        with open(self.index_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _save_index(self, index: Dict[str, Any]) -> None:
        """Save filesystem index."""
        with open(self.index_path, 'w', encoding='utf-8') as f:
            json.dump(index, f, indent=2)

    def _update_index(self, pattern: Pattern, file_path: str) -> None:
        """Update filesystem index with new pattern."""
        index = self._load_index()
        index[pattern["pattern_id"]] = {
            "path": file_path,
            "type": pattern["pattern_type"],
            "timestamp": pattern["timestamp"]
        }
        self._save_index(index)

    def _remove_from_index(self, pattern_id: str) -> None:
        """Remove pattern from filesystem index."""
        index = self._load_index()
        if pattern_id in index:
            del index[pattern_id]
            self._save_index(index)

    def close(self) -> None:
        """Close storage backend."""
        if self.config.backend == "sqlite" and hasattr(self, "conn"):
            self.conn.close()


__all__ = [
    "StorageConfig",
    "PatternStorage"
]
