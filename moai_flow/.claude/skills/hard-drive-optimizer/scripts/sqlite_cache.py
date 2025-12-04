#!/usr/bin/env python3
"""
SQLite cache management for three-layer caching system.

L1: In-memory (< 1s access, process lifetime)
L2: SQLite database (< 100ms access, 24h TTL)
L3: Filesystem metadata (always fresh, mtime-based)

Performance characteristics:
- L1 hit (90%+ repeated queries): < 1 second
- L2 hit (70-80% unchanged projects): 5-15 seconds
- L3 miss (first run or stale cache): 3-5 minutes
"""

import sqlite3
import json
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Optional, Dict
from datetime import datetime, timedelta


@dataclass
class ProjectRecord:
    """SQLite project record."""
    id: Optional[int]
    project_path: str
    size_bytes: int
    file_count: int
    last_modified_time: float
    cached_at: float
    cy4_score: Optional[float] = None
    cleanup_priority: Optional[float] = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return asdict(self)


class SQLiteCache:
    """
    SQLite cache manager with three-layer architecture.

    Provides persistent storage with TTL support and
    indexed queries for fast lookups.
    """

    # Cache TTL in hours
    CACHE_TTL_HOURS = 24

    def __init__(self, db_path: Path, verbose: bool = True):
        """Initialize cache manager."""
        self.db_path = Path(db_path)
        self.verbose = verbose
        self._memory_cache: Optional[List[ProjectRecord]] = None
        self._memory_cache_time: float = 0.0

        # Ensure parent directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize database
        self._init_db()

    def _init_db(self):
        """Initialize SQLite database with schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("PRAGMA journal_mode = WAL")
            conn.execute("PRAGMA cache_size = 10000")

            # Create projects table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_path TEXT UNIQUE NOT NULL,
                    size_bytes INTEGER NOT NULL,
                    file_count INTEGER NOT NULL,
                    last_modified_time REAL NOT NULL,
                    cached_at REAL NOT NULL,
                    cy4_score REAL DEFAULT NULL,
                    cleanup_priority REAL DEFAULT 0.0
                )
            """)

            # Create indexes for performance
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_projects_size
                ON projects(size_bytes DESC)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_projects_priority
                ON projects(cleanup_priority DESC)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_projects_modified
                ON projects(last_modified_time DESC)
            """)

            # Create dependencies table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS dependencies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER NOT NULL,
                    dependency_type TEXT NOT NULL,
                    path TEXT NOT NULL,
                    size_bytes INTEGER NOT NULL,
                    can_delete BOOLEAN DEFAULT 1,
                    FOREIGN KEY (project_id) REFERENCES projects(id)
                )
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_deps_size
                ON dependencies(size_bytes DESC)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_deps_deletable
                ON dependencies(can_delete, size_bytes DESC)
            """)

            conn.commit()

    def get_all_projects(self, force_refresh: bool = False) -> List[ProjectRecord]:
        """
        Get all projects with cascading cache lookup.

        Attempts L2 cache first, falls back to L1 memory cache if valid.

        Args:
            force_refresh: Force database read (skip memory cache)

        Returns:
            List of ProjectRecord objects
        """
        # L1: Memory cache (if still valid)
        if not force_refresh and self._memory_cache:
            if time.time() - self._memory_cache_time < 60:  # Valid for 60s
                return self._memory_cache

        # L2: SQLite database
        projects = self._read_projects_from_db()

        # Update L1 cache
        self._memory_cache = projects
        self._memory_cache_time = time.time()

        return projects

    def bulk_update_projects(self, projects: List) -> None:
        """
        Bulk insert/update projects in database.

        Args:
            projects: List of ProjectMetadata from scanner
        """
        now = time.time()

        # Convert to database records
        records = []
        for project in projects:
            record = ProjectRecord(
                id=None,
                project_path=project.path,
                size_bytes=project.size_bytes,
                file_count=project.file_count,
                last_modified_time=project.last_modified_time,
                cached_at=now
            )
            records.append(record)

        # Bulk insert/update
        with sqlite3.connect(self.db_path) as conn:
            for record in records:
                conn.execute("""
                    INSERT OR REPLACE INTO projects
                    (project_path, size_bytes, file_count, last_modified_time, cached_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    record.project_path,
                    record.size_bytes,
                    record.file_count,
                    record.last_modified_time,
                    record.cached_at
                ))

            conn.commit()

        # Invalidate memory cache
        self._memory_cache = None

        if self.verbose:
            print(f"   💾 Cached {len(records)} projects to SQLite")

    def update_cy4_scores(self, scores: Dict[str, float]) -> None:
        """
        Update cy4 scores for projects.

        Args:
            scores: Dict mapping project_path -> cy4_score
        """
        with sqlite3.connect(self.db_path) as conn:
            for path, score in scores.items():
                conn.execute("""
                    UPDATE projects SET cy4_score = ? WHERE project_path = ?
                """, (score, path))

            conn.commit()

        # Invalidate memory cache
        self._memory_cache = None

    def update_cleanup_priority(self, priorities: Dict[str, float]) -> None:
        """
        Update cleanup priority scores.

        Args:
            priorities: Dict mapping project_path -> priority
        """
        with sqlite3.connect(self.db_path) as conn:
            for path, priority in priorities.items():
                conn.execute("""
                    UPDATE projects SET cleanup_priority = ? WHERE project_path = ?
                """, (priority, path))

            conn.commit()

        # Invalidate memory cache
        self._memory_cache = None

    def get_largest_projects(self, limit: int = 10) -> List[ProjectRecord]:
        """
        Get largest projects by size.

        Args:
            limit: Number of projects to return

        Returns:
            List of ProjectRecord objects, sorted by size DESC
        """
        projects = self.get_all_projects()
        return sorted(projects, key=lambda p: p.size_bytes, reverse=True)[:limit]

    def get_projects_by_priority(self, limit: int = 50) -> List[ProjectRecord]:
        """
        Get projects by cleanup priority.

        Args:
            limit: Number of projects to return

        Returns:
            List of ProjectRecord objects, sorted by priority DESC
        """
        projects = self.get_all_projects()
        return sorted(projects, key=lambda p: p.cleanup_priority or 0, reverse=True)[:limit]

    def is_cache_valid(self, threshold_hours: float = CACHE_TTL_HOURS) -> bool:
        """
        Check if cache is still valid.

        Args:
            threshold_hours: Cache TTL in hours

        Returns:
            True if cache is fresh, False if stale
        """
        if not self.db_path.exists():
            return False

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT MAX(cached_at) FROM projects
                """)
                result = cursor.fetchone()

                if result and result[0]:
                    max_cached_at = result[0]
                    age_hours = (time.time() - max_cached_at) / 3600
                    return age_hours < threshold_hours

            return False
        except sqlite3.DatabaseError:
            return False

    def clear(self) -> None:
        """Clear all cache data."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM dependencies")
            conn.execute("DELETE FROM projects")
            conn.commit()

        self._memory_cache = None

        if self.verbose:
            print("   🗑️  Cache cleared")

    def _read_projects_from_db(self) -> List[ProjectRecord]:
        """Read all projects from database."""
        projects = []

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT id, project_path, size_bytes, file_count,
                           last_modified_time, cached_at, cy4_score, cleanup_priority
                    FROM projects
                    ORDER BY size_bytes DESC
                """)

                for row in cursor.fetchall():
                    record = ProjectRecord(
                        id=row[0],
                        project_path=row[1],
                        size_bytes=row[2],
                        file_count=row[3],
                        last_modified_time=row[4],
                        cached_at=row[5],
                        cy4_score=row[6],
                        cleanup_priority=row[7]
                    )
                    projects.append(record)
        except sqlite3.DatabaseError as e:
            if self.verbose:
                print(f"   ⚠️  Database error: {e}")

        return projects

    def _format_size(self, bytes_size: int) -> str:
        """Format bytes to human-readable size."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.1f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.1f} PB"

    def print_stats(self) -> None:
        """Print cache statistics."""
        projects = self.get_all_projects()

        if not projects:
            print("No projects in cache")
            return

        total_size = sum(p.size_bytes for p in projects)
        avg_size = total_size // len(projects) if projects else 0
        max_modified = max(p.last_modified_time for p in projects) if projects else 0
        min_modified = min(p.last_modified_time for p in projects) if projects else 0

        print(f"\n📊 Cache Statistics:")
        print(f"   Projects: {len(projects)}")
        print(f"   Total size: {self._format_size(total_size)}")
        print(f"   Average size: {self._format_size(avg_size)}")
        print(f"   Age: {self._format_age(max_modified)} - {self._format_age(min_modified)}")

    @staticmethod
    def _format_age(timestamp: float) -> str:
        """Format timestamp as days ago."""
        days = (time.time() - timestamp) / 86400
        if days < 1:
            return "today"
        elif days < 7:
            return f"{int(days)} days ago"
        elif days < 30:
            return f"{int(days/7)} weeks ago"
        else:
            return f"{int(days/30)} months ago"


def main():
    """Test the SQLite cache."""
    cache_path = Path("/tmp/test-cache.db")
    cache = SQLiteCache(cache_path, verbose=True)

    # Test: Clear and print stats
    cache.clear()
    cache.print_stats()


if __name__ == "__main__":
    main()
