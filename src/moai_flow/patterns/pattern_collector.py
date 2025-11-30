"""
Pattern Collection System for MoAI Flow

PRD-05 Phase 1: Pattern Logging
Collects execution patterns WITHOUT ML (simple data collection).

This module provides a comprehensive pattern collection system that logs:
- Task completions (agent usage, duration, success/failure)
- Error occurrences (type, context, resolution)
- Agent usage patterns (frequency, performance)
- User corrections (manual interventions)

Author: MoAI-ADK
Version: 1.0.0
Status: Production Ready

Example:
    >>> from moai_flow.patterns.pattern_collector import PatternCollector, PatternType
    >>> collector = PatternCollector()
    >>> pattern_id = collector.collect_task_completion(
    ...     task_type="api_implementation",
    ...     agent="expert-backend",
    ...     duration_ms=45000,
    ...     success=True,
    ...     files_created=3,
    ...     tests_passed=12,
    ...     context={"framework": "fastapi", "language": "python", "spec_id": "SPEC-001"}
    ... )
"""

import json
import threading
import gzip
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4


class PatternType(str, Enum):
    """Pattern collection types."""

    TASK_COMPLETION = "task_completion"
    ERROR_OCCURRENCE = "error_occurrence"
    AGENT_USAGE = "agent_usage"
    USER_CORRECTION = "user_correction"


@dataclass
class Pattern:
    """
    Pattern data structure.

    Attributes:
        pattern_id: Unique pattern identifier (pat-YYYYMMDD-HHMMSS-nnn)
        pattern_type: Type of pattern (task, error, agent, correction)
        timestamp: When pattern was collected
        data: Pattern-specific data
        context: Additional context information
    """

    pattern_id: str
    pattern_type: PatternType
    timestamp: datetime
    data: Dict[str, Any]
    context: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert pattern to dictionary for JSON serialization."""
        return {
            "pattern_id": self.pattern_id,
            "type": self.pattern_type.value,
            "timestamp": self.timestamp.isoformat(),
            "data": self.data,
            "context": self.context
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Pattern":
        """Create pattern from dictionary."""
        return cls(
            pattern_id=data["pattern_id"],
            pattern_type=PatternType(data["type"]),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            data=data["data"],
            context=data["context"]
        )


class PatternCollector:
    """
    Collect execution patterns for analysis.

    Patterns collected:
    - Task completions (agent, duration, result)
    - Error occurrences (error type, context, resolution)
    - Agent usage (frequency, success rate)
    - User corrections (what was corrected, pattern)

    Features:
    - Thread-safe concurrent writes
    - Auto-cleanup based on retention policy
    - Date-based directory hierarchy
    - Optional gzip compression for old patterns
    - Pattern querying and statistics
    - Config integration (.moai/config/config.json)

    Storage Structure:
        .moai/patterns/
        └── 2025/
            └── 11/
                └── 29/
                    ├── task_completion_20251129_100000.json
                    ├── error_occurrence_20251129_120000.json
                    └── agent_usage_20251129_150000.json

    Example:
        >>> collector = PatternCollector()
        >>> pattern_id = collector.collect_task_completion(
        ...     task_type="api_implementation",
        ...     agent="expert-backend",
        ...     duration_ms=45000,
        ...     success=True,
        ...     files_created=3,
        ...     tests_passed=12,
        ...     context={"framework": "fastapi", "language": "python"}
        ... )
        >>> print(f"Collected pattern: {pattern_id}")
    """

    def __init__(
        self,
        storage_path: str = ".moai/patterns",
        config_path: Optional[str] = None,
        enable_compression: bool = True
    ):
        """
        Initialize pattern collector.

        Args:
            storage_path: Directory to store patterns
            config_path: Path to config.json for loading settings
            enable_compression: Enable gzip compression for old patterns
        """
        self.storage_path = Path(storage_path)
        self.enable_compression = enable_compression
        self._lock = threading.Lock()
        self._pattern_counter = 0

        # Load configuration
        self.config = self._load_config(config_path)

        # Initialize storage
        self._init_storage()

    def _load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Load configuration from config.json.

        Args:
            config_path: Path to config.json (optional)

        Returns:
            Configuration dictionary
        """
        default_config = {
            "enabled": True,
            "storage": ".moai/patterns/",
            "collect": {
                "task_completion": True,
                "error_occurrence": True,
                "agent_usage": True,
                "user_correction": False
            },
            "retention_days": 90
        }

        if config_path:
            try:
                config_file = Path(config_path)
                if config_file.exists():
                    with open(config_file, 'r') as f:
                        full_config = json.load(f)
                        return full_config.get("patterns", default_config)
            except Exception as e:
                print(f"Warning: Could not load config from {config_path}: {e}")

        # Try default config location
        default_path = Path(".moai/config/config.json")
        if default_path.exists():
            try:
                with open(default_path, 'r') as f:
                    full_config = json.load(f)
                    return full_config.get("patterns", default_config)
            except Exception:
                pass

        return default_config

    def _init_storage(self) -> None:
        """Initialize storage directory structure."""
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Create current year/month directories
        now = datetime.now()
        year_path = self.storage_path / str(now.year)
        month_path = year_path / f"{now.month:02d}"
        day_path = month_path / f"{now.day:02d}"

        year_path.mkdir(exist_ok=True)
        month_path.mkdir(exist_ok=True)
        day_path.mkdir(exist_ok=True)

    def _generate_pattern_id(self) -> str:
        """
        Generate unique pattern ID.

        Format: pat-YYYYMMDD-HHMMSS-nnn

        Returns:
            Unique pattern identifier
        """
        with self._lock:
            self._pattern_counter += 1
            now = datetime.now()
            return f"pat-{now.strftime('%Y%m%d-%H%M%S')}-{self._pattern_counter:03d}"

    def _get_pattern_path(self, timestamp: datetime, pattern_type: PatternType) -> Path:
        """
        Get file path for pattern storage.

        Structure:
        .moai/patterns/
        └── 2025/
            └── 11/
                └── 29/
                    ├── task_completion_20251129_100000.json
                    └── error_occurrence_20251129_120000.json

        Args:
            timestamp: Pattern timestamp
            pattern_type: Type of pattern

        Returns:
            Path to pattern file
        """
        year = timestamp.year
        month = f"{timestamp.month:02d}"
        day = f"{timestamp.day:02d}"

        dir_path = self.storage_path / str(year) / month / day
        dir_path.mkdir(parents=True, exist_ok=True)

        # Include microseconds to prevent filename collisions
        filename = f"{pattern_type.value}_{timestamp.strftime('%Y%m%d_%H%M%S')}_{timestamp.microsecond:06d}.json"
        return dir_path / filename

    def _save_pattern(self, pattern: Pattern) -> None:
        """
        Save pattern to file system.

        Thread-safe pattern storage with automatic directory creation.

        Args:
            pattern: Pattern to save
        """
        if not self.config.get("enabled", True):
            return

        # Check if this pattern type should be collected
        collect_config = self.config.get("collect", {})
        if not collect_config.get(pattern.pattern_type.value, True):
            return

        file_path = self._get_pattern_path(pattern.timestamp, pattern.pattern_type)

        with self._lock:
            try:
                # Write pattern to file
                with open(file_path, 'w') as f:
                    json.dump(pattern.to_dict(), f, indent=2)
            except Exception as e:
                print(f"Error saving pattern {pattern.pattern_id}: {e}")

    def collect_task_completion(
        self,
        task_type: str,
        agent: str,
        duration_ms: int,
        success: bool,
        files_created: int = 0,
        tests_passed: int = 0,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Collect task completion pattern.

        Args:
            task_type: Type of task (e.g., "api_implementation", "test_generation")
            agent: Agent that executed the task (e.g., "expert-backend", "manager-tdd")
            duration_ms: Task duration in milliseconds
            success: Whether task completed successfully
            files_created: Number of files created
            tests_passed: Number of tests that passed
            context: Additional context (framework, language, spec_id, etc.)

        Returns:
            pattern_id: Unique pattern identifier

        Example:
            >>> pattern_id = collector.collect_task_completion(
            ...     task_type="api_implementation",
            ...     agent="expert-backend",
            ...     duration_ms=45000,
            ...     success=True,
            ...     files_created=3,
            ...     tests_passed=12,
            ...     context={"framework": "fastapi", "language": "python", "spec_id": "SPEC-001"}
            ... )
        """
        pattern_id = self._generate_pattern_id()
        timestamp = datetime.now()

        pattern = Pattern(
            pattern_id=pattern_id,
            pattern_type=PatternType.TASK_COMPLETION,
            timestamp=timestamp,
            data={
                "task_type": task_type,
                "agent": agent,
                "duration_ms": duration_ms,
                "success": success,
                "files_created": files_created,
                "tests_passed": tests_passed
            },
            context=context or {}
        )

        self._save_pattern(pattern)
        return pattern_id

    def collect_error_occurrence(
        self,
        error_type: str,
        error_message: str,
        context: Dict[str, Any],
        resolution: Optional[str] = None
    ) -> str:
        """
        Collect error occurrence pattern.

        Args:
            error_type: Type of error (e.g., "ImportError", "ValidationError", "RuntimeError")
            error_message: Detailed error message
            context: Context when error occurred (file, function, line, etc.)
            resolution: How error was resolved (if applicable)

        Returns:
            pattern_id: Unique pattern identifier

        Example:
            >>> pattern_id = collector.collect_error_occurrence(
            ...     error_type="ValidationError",
            ...     error_message="Invalid API key format",
            ...     context={"file": "api/auth.py", "function": "validate_api_key", "line": 42},
            ...     resolution="Added regex validation for API key format"
            ... )
        """
        pattern_id = self._generate_pattern_id()
        timestamp = datetime.now()

        pattern = Pattern(
            pattern_id=pattern_id,
            pattern_type=PatternType.ERROR_OCCURRENCE,
            timestamp=timestamp,
            data={
                "error_type": error_type,
                "error_message": error_message,
                "resolution": resolution
            },
            context=context
        )

        self._save_pattern(pattern)
        return pattern_id

    def collect_agent_usage(
        self,
        agent_type: str,
        task_type: str,
        success: bool,
        duration_ms: int
    ) -> str:
        """
        Collect agent usage pattern.

        Args:
            agent_type: Type of agent (e.g., "expert-backend", "manager-tdd")
            task_type: Type of task executed
            success: Whether task was successful
            duration_ms: Task duration in milliseconds

        Returns:
            pattern_id: Unique pattern identifier

        Example:
            >>> pattern_id = collector.collect_agent_usage(
            ...     agent_type="expert-backend",
            ...     task_type="api_implementation",
            ...     success=True,
            ...     duration_ms=45000
            ... )
        """
        pattern_id = self._generate_pattern_id()
        timestamp = datetime.now()

        pattern = Pattern(
            pattern_id=pattern_id,
            pattern_type=PatternType.AGENT_USAGE,
            timestamp=timestamp,
            data={
                "agent_type": agent_type,
                "task_type": task_type,
                "success": success,
                "duration_ms": duration_ms
            },
            context={}
        )

        self._save_pattern(pattern)
        return pattern_id

    def collect_user_correction(
        self,
        original_output: str,
        corrected_output: str,
        correction_type: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Collect user correction pattern.

        Args:
            original_output: Original agent output
            corrected_output: User's corrected version
            correction_type: Type of correction (e.g., "logic_error", "style_improvement")
            context: Additional context

        Returns:
            pattern_id: Unique pattern identifier

        Example:
            >>> pattern_id = collector.collect_user_correction(
            ...     original_output="def add(a, b): return a + b",
            ...     corrected_output="def add(a: int, b: int) -> int: return a + b",
            ...     correction_type="type_hints_missing",
            ...     context={"file": "utils.py", "agent": "expert-backend"}
            ... )
        """
        pattern_id = self._generate_pattern_id()
        timestamp = datetime.now()

        pattern = Pattern(
            pattern_id=pattern_id,
            pattern_type=PatternType.USER_CORRECTION,
            timestamp=timestamp,
            data={
                "original_output": original_output,
                "corrected_output": corrected_output,
                "correction_type": correction_type
            },
            context=context or {}
        )

        self._save_pattern(pattern)
        return pattern_id

    def get_patterns(
        self,
        pattern_type: Optional[PatternType] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Pattern]:
        """
        Query patterns by type and date range.

        Args:
            pattern_type: Filter by pattern type (optional)
            start_date: Start date for query (optional)
            end_date: End date for query (optional)
            limit: Maximum number of patterns to return

        Returns:
            List of patterns matching criteria

        Example:
            >>> patterns = collector.get_patterns(
            ...     pattern_type=PatternType.TASK_COMPLETION,
            ...     start_date=datetime(2025, 11, 1),
            ...     end_date=datetime(2025, 11, 30),
            ...     limit=50
            ... )
            >>> print(f"Found {len(patterns)} task completion patterns")
        """
        patterns = []

        # Determine date range
        if not start_date:
            start_date = datetime.now() - timedelta(days=self.config.get("retention_days", 90))
        if not end_date:
            end_date = datetime.now()

        # Iterate through date hierarchy
        current_date = start_date.date()
        end = end_date.date()

        while current_date <= end and len(patterns) < limit:
            year_path = self.storage_path / str(current_date.year)
            month_path = year_path / f"{current_date.month:02d}"
            day_path = month_path / f"{current_date.day:02d}"

            if day_path.exists():
                # Read all pattern files for this day
                pattern_files = list(day_path.glob("*.json"))

                for file_path in pattern_files:
                    if len(patterns) >= limit:
                        break

                    # Filter by pattern type if specified
                    if pattern_type:
                        if not file_path.name.startswith(pattern_type.value):
                            continue

                    try:
                        with open(file_path, 'r') as f:
                            pattern_data = json.load(f)
                            pattern = Pattern.from_dict(pattern_data)
                            patterns.append(pattern)
                    except Exception as e:
                        print(f"Error reading pattern {file_path}: {e}")

            current_date += timedelta(days=1)

        return patterns[:limit]

    def get_pattern_count(
        self,
        pattern_type: Optional[PatternType] = None
    ) -> int:
        """
        Get total pattern count.

        Args:
            pattern_type: Filter by pattern type (optional)

        Returns:
            Total number of patterns

        Example:
            >>> total = collector.get_pattern_count()
            >>> task_count = collector.get_pattern_count(PatternType.TASK_COMPLETION)
            >>> print(f"Total patterns: {total}, Task patterns: {task_count}")
        """
        count = 0

        # Traverse storage directory
        for year_dir in self.storage_path.glob("*"):
            if not year_dir.is_dir():
                continue

            for month_dir in year_dir.glob("*"):
                if not month_dir.is_dir():
                    continue

                for day_dir in month_dir.glob("*"):
                    if not day_dir.is_dir():
                        continue

                    if pattern_type:
                        count += len(list(day_dir.glob(f"{pattern_type.value}_*.json")))
                    else:
                        count += len(list(day_dir.glob("*.json")))

        return count

    def cleanup_old_patterns(self) -> int:
        """
        Delete patterns older than retention_days.

        Returns:
            Number of patterns deleted

        Example:
            >>> deleted = collector.cleanup_old_patterns()
            >>> print(f"Deleted {deleted} old patterns")
        """
        retention_days = self.config.get("retention_days", 90)
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        deleted_count = 0

        with self._lock:
            # Traverse storage directory
            for year_dir in self.storage_path.glob("*"):
                if not year_dir.is_dir():
                    continue

                for month_dir in year_dir.glob("*"):
                    if not month_dir.is_dir():
                        continue

                    for day_dir in month_dir.glob("*"):
                        if not day_dir.is_dir():
                            continue

                        # Parse directory date
                        try:
                            year = int(year_dir.name)
                            month = int(month_dir.name)
                            day = int(day_dir.name)
                            dir_date = datetime(year, month, day)

                            if dir_date < cutoff_date:
                                # Delete all patterns in this day
                                pattern_files = list(day_dir.glob("*.json"))
                                for file_path in pattern_files:
                                    file_path.unlink()
                                    deleted_count += 1

                                # Remove empty directory
                                if not list(day_dir.iterdir()):
                                    day_dir.rmdir()
                        except (ValueError, OSError) as e:
                            print(f"Error processing directory {day_dir}: {e}")

                    # Remove empty month directories
                    if month_dir.exists() and not list(month_dir.iterdir()):
                        month_dir.rmdir()

                # Remove empty year directories
                if year_dir.exists() and not list(year_dir.iterdir()):
                    year_dir.rmdir()

        return deleted_count

    def compress_old_patterns(self, days_old: int = 30) -> int:
        """
        Compress patterns older than specified days using gzip.

        Args:
            days_old: Compress patterns older than this many days

        Returns:
            Number of patterns compressed

        Example:
            >>> compressed = collector.compress_old_patterns(days_old=30)
            >>> print(f"Compressed {compressed} patterns")
        """
        if not self.enable_compression:
            return 0

        cutoff_date = datetime.now() - timedelta(days=days_old)
        compressed_count = 0

        with self._lock:
            for year_dir in self.storage_path.glob("*"):
                if not year_dir.is_dir():
                    continue

                for month_dir in year_dir.glob("*"):
                    if not month_dir.is_dir():
                        continue

                    for day_dir in month_dir.glob("*"):
                        if not day_dir.is_dir():
                            continue

                        try:
                            year = int(year_dir.name)
                            month = int(month_dir.name)
                            day = int(day_dir.name)
                            dir_date = datetime(year, month, day)

                            if dir_date < cutoff_date:
                                # Compress uncompressed JSON files
                                pattern_files = list(day_dir.glob("*.json"))

                                for file_path in pattern_files:
                                    if not file_path.name.endswith('.gz'):
                                        # Read original file
                                        with open(file_path, 'rb') as f_in:
                                            # Write compressed file
                                            gz_path = file_path.with_suffix('.json.gz')
                                            with gzip.open(gz_path, 'wb') as f_out:
                                                f_out.write(f_in.read())

                                        # Delete original
                                        file_path.unlink()
                                        compressed_count += 1
                        except Exception as e:
                            print(f"Error compressing patterns in {day_dir}: {e}")

        return compressed_count

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get pattern collection statistics.

        Returns:
            Dictionary with statistics for each pattern type

        Example:
            >>> stats = collector.get_statistics()
            >>> print(json.dumps(stats, indent=2))
            {
              "total_patterns": 156,
              "by_type": {
                "task_completion": 98,
                "error_occurrence": 32,
                "agent_usage": 26,
                "user_correction": 0
              },
              "storage_path": ".moai/patterns",
              "retention_days": 90,
              "collection_enabled": true
            }
        """
        stats = {
            "total_patterns": self.get_pattern_count(),
            "by_type": {},
            "storage_path": str(self.storage_path),
            "retention_days": self.config.get("retention_days", 90),
            "collection_enabled": self.config.get("enabled", True)
        }

        for pattern_type in PatternType:
            count = self.get_pattern_count(pattern_type)
            stats["by_type"][pattern_type.value] = count

        return stats


__all__ = [
    "PatternCollector",
    "Pattern",
    "PatternType",
]
