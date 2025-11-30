#!/usr/bin/env python3
"""
SwarmDB - SQLite-based Persistent Storage for Multi-Agent Coordination

Provides persistent storage for:
- Agent lifecycle events (spawn, complete, error)
- Cross-session memory and context
- Agent communication logs
- Resource utilization metrics
- Phase 6A Observability metrics (task, agent, swarm-level)

Phase 6A Observability Extensions:
- Task metrics: duration, result, token usage, files changed
- Agent metrics: success rates, error counts, performance stats
- Swarm metrics: health, throughput, latency, resource utilization
- Optimized time-series indexing for fast queries
- 30-day default retention with auto-cleanup

Integration Points:
- SemanticMemory: Long-term knowledge patterns
- EpisodicMemory: Event and decision history
- ContextHints: Session hints and user preferences
- MetricsStorage: Dedicated metrics persistence (Phase 6A)

Architecture:
- SQLite backend for simplicity and zero-dependency deployment
- Thread-safe operations with connection pooling
- Schema migrations for version compatibility
- JSON storage for flexible event metadata
- Optimized indexing for time-series queries

Schema Version: 2.0.0 (Phase 6A Extended)
"""

import json
import logging
import sqlite3
import threading
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# ============================================================================
# Database Schema
# ============================================================================

SCHEMA_VERSION = "2.0.0"

SCHEMA_SQL = """
-- Agent lifecycle events table
CREATE TABLE IF NOT EXISTS agent_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id TEXT UNIQUE NOT NULL,
    event_type TEXT NOT NULL,  -- 'spawn' | 'complete' | 'error'
    agent_id TEXT NOT NULL,
    agent_type TEXT NOT NULL,
    timestamp TEXT NOT NULL,  -- ISO8601 format
    metadata TEXT,  -- JSON blob
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_agent_events_agent_id ON agent_events(agent_id);
CREATE INDEX IF NOT EXISTS idx_agent_events_event_type ON agent_events(event_type);
CREATE INDEX IF NOT EXISTS idx_agent_events_timestamp ON agent_events(timestamp);

-- Agent state registry (current/active agents)
CREATE TABLE IF NOT EXISTS agent_registry (
    agent_id TEXT PRIMARY KEY,
    agent_type TEXT NOT NULL,
    status TEXT NOT NULL,  -- 'spawned' | 'running' | 'complete' | 'error'
    spawn_time REAL NOT NULL,
    complete_time REAL,
    duration_ms INTEGER,
    metadata TEXT,  -- JSON blob
    last_updated TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_agent_registry_status ON agent_registry(status);
CREATE INDEX IF NOT EXISTS idx_agent_registry_agent_type ON agent_registry(agent_type);

-- Cross-session memory (future integration)
CREATE TABLE IF NOT EXISTS session_memory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    memory_type TEXT NOT NULL,  -- 'semantic' | 'episodic' | 'context_hint'
    key TEXT NOT NULL,
    value TEXT,  -- JSON blob
    timestamp TEXT NOT NULL,
    ttl_hours INTEGER,  -- Time-to-live in hours (NULL = permanent)
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_session_memory_session_id ON session_memory(session_id);
CREATE INDEX IF NOT EXISTS idx_session_memory_memory_type ON session_memory(memory_type);
CREATE INDEX IF NOT EXISTS idx_session_memory_key ON session_memory(key);

-- Task metrics table (Phase 6A Observability)
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

-- Agent metrics table (Phase 6A Observability)
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

-- Swarm metrics table (Phase 6A Observability)
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

-- Schema version tracking
CREATE TABLE IF NOT EXISTS schema_info (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

INSERT OR REPLACE INTO schema_info (key, value) VALUES ('version', ?);
"""


# ============================================================================
# SwarmDB Implementation
# ============================================================================

class SwarmDB:
    """
    SQLite-based persistent storage for multi-agent coordination.

    Features:
    - Thread-safe connection pooling
    - Automatic schema initialization
    - Transaction support
    - JSON metadata storage
    - Query helpers for common operations

    Example:
        >>> db = SwarmDB()
        >>> db.insert_event({
        ...     "event_type": "spawn",
        ...     "agent_id": "a1b2c3",
        ...     "agent_type": "expert-backend",
        ...     "timestamp": "2025-01-01T00:00:00",
        ...     "metadata": {"prompt": "Design API"}
        ... })
    """

    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize SwarmDB

        Args:
            db_path: Path to SQLite database file (defaults to .moai/memory/swarm.db)
        """
        self.db_path = db_path or Path.cwd() / ".moai" / "memory" / "swarm.db"
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
        """Initialize database schema"""
        with self._lock:
            try:
                conn = self._get_connection()
                cursor = conn.cursor()

                # Execute schema with version
                for statement in SCHEMA_SQL.split(';'):
                    statement = statement.strip()
                    if statement:
                        # Replace version placeholder
                        statement = statement.replace('?', f"'{SCHEMA_VERSION}'")
                        cursor.execute(statement)

                conn.commit()
                self.logger.info(f"Initialized SwarmDB schema v{SCHEMA_VERSION}")

            except Exception as e:
                self.logger.error(f"Failed to initialize schema: {e}")
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
    # Agent Event Operations
    # ========================================================================

    def insert_event(
        self,
        event_data: Dict[str, Any],
        event_id: Optional[str] = None
    ) -> str:
        """
        Insert agent lifecycle event

        Args:
            event_data: Event data dictionary with keys:
                - event_type: 'spawn' | 'complete' | 'error'
                - agent_id: Agent identifier
                - agent_type: Agent type (e.g., 'expert-backend')
                - timestamp: ISO8601 timestamp
                - metadata: Additional metadata dict
            event_id: Optional event ID (generates UUID if not provided)

        Returns:
            event_id of inserted event
        """
        import uuid

        event_id = event_id or str(uuid.uuid4())

        with self.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO agent_events
                (event_id, event_type, agent_id, agent_type, timestamp, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    event_id,
                    event_data["event_type"],
                    event_data["agent_id"],
                    event_data["agent_type"],
                    event_data["timestamp"],
                    json.dumps(event_data.get("metadata", {}))
                )
            )

        self.logger.debug(f"Inserted event: {event_id} ({event_data['event_type']})")
        return event_id

    def get_events(
        self,
        agent_id: Optional[str] = None,
        event_type: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Query agent events

        Args:
            agent_id: Filter by agent ID
            event_type: Filter by event type
            limit: Maximum number of events to return

        Returns:
            List of event dictionaries
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM agent_events WHERE 1=1"
        params = []

        if agent_id:
            query += " AND agent_id = ?"
            params.append(agent_id)

        if event_type:
            query += " AND event_type = ?"
            params.append(event_type)

        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)

        events = []
        for row in cursor.fetchall():
            event = dict(row)
            # Parse JSON metadata
            if event.get("metadata"):
                try:
                    event["metadata"] = json.loads(event["metadata"])
                except json.JSONDecodeError:
                    event["metadata"] = {}
            events.append(event)

        return events

    # ========================================================================
    # Agent Registry Operations
    # ========================================================================

    def register_agent(
        self,
        agent_id: str,
        agent_type: str,
        status: str = "spawned",
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Register agent in registry"""
        import time

        with self.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO agent_registry
                (agent_id, agent_type, status, spawn_time, metadata, last_updated)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    agent_id,
                    agent_type,
                    status,
                    time.time(),
                    json.dumps(metadata or {}),
                    datetime.now().isoformat()
                )
            )

        self.logger.debug(f"Registered agent: {agent_id} ({agent_type})")

    def update_agent_status(
        self,
        agent_id: str,
        status: str,
        duration_ms: Optional[int] = None
    ) -> None:
        """Update agent status"""
        import time

        with self.transaction() as conn:
            cursor = conn.cursor()

            update_fields = ["status = ?", "last_updated = ?"]
            params = [status, datetime.now().isoformat()]

            if status in ("complete", "error"):
                update_fields.append("complete_time = ?")
                params.append(time.time())

            if duration_ms is not None:
                update_fields.append("duration_ms = ?")
                params.append(duration_ms)

            params.append(agent_id)

            cursor.execute(
                f"""
                UPDATE agent_registry
                SET {', '.join(update_fields)}
                WHERE agent_id = ?
                """,
                params
            )

        self.logger.debug(f"Updated agent status: {agent_id} -> {status}")

    def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get agent from registry"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM agent_registry WHERE agent_id = ?",
            (agent_id,)
        )

        row = cursor.fetchone()
        if row:
            agent = dict(row)
            if agent.get("metadata"):
                try:
                    agent["metadata"] = json.loads(agent["metadata"])
                except json.JSONDecodeError:
                    agent["metadata"] = {}
            return agent

        return None

    def get_active_agents(self) -> List[Dict[str, Any]]:
        """Get all active (spawned/running) agents"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT * FROM agent_registry
            WHERE status IN ('spawned', 'running')
            ORDER BY spawn_time DESC
            """
        )

        agents = []
        for row in cursor.fetchall():
            agent = dict(row)
            if agent.get("metadata"):
                try:
                    agent["metadata"] = json.loads(agent["metadata"])
                except json.JSONDecodeError:
                    agent["metadata"] = {}
            agents.append(agent)

        return agents

    # ========================================================================
    # Session Memory Operations (Future Integration)
    # ========================================================================

    def store_memory(
        self,
        session_id: str,
        memory_type: str,
        key: str,
        value: Any,
        ttl_hours: Optional[int] = None
    ) -> None:
        """Store session memory (future integration with SemanticMemory/EpisodicMemory)"""
        with self.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO session_memory
                (session_id, memory_type, key, value, timestamp, ttl_hours)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    session_id,
                    memory_type,
                    key,
                    json.dumps(value),
                    datetime.now().isoformat(),
                    ttl_hours
                )
            )

        self.logger.debug(f"Stored memory: {session_id}/{memory_type}/{key}")

    def get_memory(
        self,
        session_id: str,
        memory_type: str,
        key: str
    ) -> Optional[Any]:
        """Retrieve session memory"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT value FROM session_memory
            WHERE session_id = ? AND memory_type = ? AND key = ?
            ORDER BY timestamp DESC
            LIMIT 1
            """,
            (session_id, memory_type, key)
        )

        row = cursor.fetchone()
        if row:
            try:
                return json.loads(row["value"])
            except json.JSONDecodeError:
                return None

        return None

    # ========================================================================
    # Maintenance Operations
    # ========================================================================

    def cleanup_old_events(self, days: int = 30) -> int:
        """Delete events older than specified days"""
        from datetime import timedelta

        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()

        with self.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM agent_events WHERE timestamp < ?",
                (cutoff_date,)
            )
            deleted_count = cursor.rowcount

        self.logger.info(f"Cleaned up {deleted_count} old events (>{days} days)")
        return deleted_count

    def persist_session_state(self, session_id: Optional[str] = None) -> str:
        """
        Persist current session state to .moai/memory/moai-flow/

        Args:
            session_id: Session ID to persist (defaults to current session)

        Returns:
            Path to persisted state file
        """
        from uuid import uuid4

        state_file = Path(".moai/memory/moai-flow/session-state.json")
        state_file.parent.mkdir(parents=True, exist_ok=True)

        # Collect current session state
        conn = self._get_connection()
        cursor = conn.cursor()

        # Get active agents
        cursor.execute("""
            SELECT agent_id, agent_type, status, spawn_time, metadata
            FROM agent_registry
            WHERE status IN ('spawned', 'running')
        """)
        active_agents = [
            {
                "agent_id": row[0],
                "agent_type": row[1],
                "status": row[2],
                "spawn_time": row[3],
                "metadata": json.loads(row[4]) if row[4] else {}
            }
            for row in cursor.fetchall()
        ]

        # Get recent events (last 100)
        cursor.execute("""
            SELECT event_id, event_type, agent_id, timestamp, metadata
            FROM agent_events
            ORDER BY timestamp DESC
            LIMIT 100
        """)
        recent_events = [
            {
                "event_id": row[0],
                "event_type": row[1],
                "agent_id": row[2],
                "timestamp": row[3],
                "metadata": json.loads(row[4]) if row[4] else {}
            }
            for row in cursor.fetchall()
        ]

        # Build state object
        state = {
            "session_id": session_id or str(uuid4()),
            "timestamp": datetime.now().isoformat(),
            "active_agents": active_agents,
            "recent_events": recent_events,
            "database_path": str(self.db_path)
        }

        # Write to file
        with state_file.open("w") as f:
            json.dump(state, f, indent=2)

        return str(state_file)

    def cleanup(self, days: int = 30) -> Dict[str, int]:
        """
        Cleanup old data and prepare for session end.
        Alias to cleanup_old_events with additional housekeeping.

        Args:
            days: Delete events older than this many days

        Returns:
            Dictionary with cleanup statistics
        """
        deleted_events = self.cleanup_old_events(days)

        # Additional cleanup: mark stale agents as error
        with self.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE agent_registry
                SET status = 'error', last_updated = ?
                WHERE status IN ('spawned', 'running')
                AND datetime(last_updated) < datetime('now', '-1 hour')
            """, (datetime.now().isoformat(),))
            stale_agents = cursor.rowcount

        return {
            "deleted_events": deleted_events,
            "cleaned_stale_agents": stale_agents
        }

    def vacuum(self) -> None:
        """Optimize database storage"""
        conn = self._get_connection()
        conn.execute("VACUUM")
        self.logger.info("Database vacuumed")

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

    print("=== SwarmDB Example Usage ===\n")

    # Initialize database
    db = SwarmDB()
    print("✓ Database initialized")

    # Example 1: Insert agent spawn event
    print("\n--- Example 1: Insert Spawn Event ---")
    agent_id = str(uuid.uuid4())
    event_id = db.insert_event({
        "event_type": "spawn",
        "agent_id": agent_id,
        "agent_type": "expert-backend",
        "timestamp": datetime.now().isoformat(),
        "metadata": {
            "prompt": "Design REST API",
            "model": "claude-sonnet-4"
        }
    })
    print(f"✓ Event inserted: {event_id}")

    # Register agent
    db.register_agent(
        agent_id=agent_id,
        agent_type="expert-backend",
        status="spawned",
        metadata={"prompt": "Design REST API"}
    )
    print(f"✓ Agent registered: {agent_id}")

    # Example 2: Update agent to complete
    print("\n--- Example 2: Update to Complete ---")
    time.sleep(0.1)
    db.insert_event({
        "event_type": "complete",
        "agent_id": agent_id,
        "agent_type": "expert-backend",
        "timestamp": datetime.now().isoformat(),
        "metadata": {"duration_ms": 100, "result": "success"}
    })
    db.update_agent_status(agent_id, "complete", duration_ms=100)
    print(f"✓ Agent completed: {agent_id}")

    # Example 3: Query events
    print("\n--- Example 3: Query Events ---")
    events = db.get_events(agent_id=agent_id, limit=10)
    print(f"✓ Found {len(events)} events for agent {agent_id}")
    for event in events:
        print(f"  - {event['event_type']} @ {event['timestamp']}")

    # Example 4: Get active agents
    print("\n--- Example 4: Active Agents ---")
    active_agents = db.get_active_agents()
    print(f"✓ Active agents: {len(active_agents)}")

    # Example 5: Session memory
    print("\n--- Example 5: Session Memory ---")
    db.store_memory(
        session_id="session123",
        memory_type="context_hint",
        key="user_preference",
        value={"language": "python", "style": "functional"}
    )
    memory = db.get_memory("session123", "context_hint", "user_preference")
    print(f"✓ Retrieved memory: {memory}")

    # Cleanup
    db.close()
    print("\n✅ SwarmDB demonstration complete")
    print(f"📦 Database location: {db.db_path}")
