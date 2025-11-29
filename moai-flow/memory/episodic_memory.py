#!/usr/bin/env python3
"""
EpisodicMemory - Event and Decision History Storage with Temporal Context

Stores and retrieves:
- Session events (user commands, agent executions)
- Decision points (agent selections, approach choices)
- Outcomes (success, failure, partial)
- Temporal sequences (what happened after what)

Enables learning from past actions by:
- Finding similar past episodes
- Analyzing outcome statistics
- Identifying successful patterns
- Learning from failures

Integration with SwarmDB for persistent storage.

Version: 1.0.0
"""

import json
import logging
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

try:
    from .swarm_db import SwarmDB
except ImportError:
    # Allow standalone execution
    from swarm_db import SwarmDB


# ============================================================================
# Event Type Definitions
# ============================================================================

class EventType:
    """Enumeration of episode event types"""
    COMMAND_EXECUTED = "command"          # /moai:* commands
    AGENT_SPAWNED = "agent_spawn"         # Agent spawned
    AGENT_COMPLETED = "agent_complete"    # Agent completed
    DECISION_MADE = "decision"            # Decision point
    ERROR_OCCURRED = "error"              # Error occurred
    USER_FEEDBACK = "feedback"            # User feedback
    SPEC_CREATED = "spec_create"          # SPEC created
    IMPLEMENTATION_COMPLETE = "impl_complete"  # Implementation complete


# ============================================================================
# Episode Data Structures
# ============================================================================

@dataclass
class Episode:
    """
    Episode data structure

    Represents a single event or decision with:
    - Unique identifier
    - Event type classification
    - Temporal context
    - Event-specific data
    - Outcome (if recorded)
    - Context snapshot
    """
    id: str
    event_type: str
    timestamp: str
    session_id: str
    event_data: Dict[str, Any]
    outcome: Optional[Dict[str, Any]] = None
    context: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert episode to dictionary"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Episode':
        """Create episode from dictionary"""
        return cls(**data)


# ============================================================================
# EpisodicMemory Implementation
# ============================================================================

class EpisodicMemory:
    """
    Event and decision history storage with temporal context.

    Stores:
    - Session events (user commands, agent executions)
    - Decision points (agent selections, approach choices)
    - Outcomes (success, failure, partial)
    - Temporal sequences (what happened after what)

    Features:
    - Episode similarity matching
    - Outcome statistics analysis
    - Temporal sequence queries
    - Pattern learning from history

    Example:
        >>> memory = EpisodicMemory(swarm_db, project_id="moai-adk")
        >>> decision_id = memory.record_decision(
        ...     "agent_selection",
        ...     options=["backend", "frontend"],
        ...     chosen="backend",
        ...     rationale="API implementation needed"
        ... )
        >>> memory.record_outcome(decision_id, "success", {
        ...     "duration_ms": 3000,
        ...     "tests_passed": 10
        ... })
    """

    def __init__(self, swarm_db: SwarmDB, project_id: str):
        """
        Initialize EpisodicMemory

        Args:
            swarm_db: SwarmDB instance for persistent storage
            project_id: Project identifier for memory scoping
        """
        self.db = swarm_db
        self.project_id = project_id
        self.logger = logging.getLogger(__name__)

        # Ensure episode tables exist
        self._initialize_episode_tables()

    def _initialize_episode_tables(self) -> None:
        """Initialize episode-specific database tables"""
        with self.db.transaction() as conn:
            cursor = conn.cursor()

            # Episodes table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS episodes (
                    id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    event_data TEXT,  -- JSON blob
                    outcome TEXT,  -- JSON blob
                    context TEXT,  -- JSON blob
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Indexes for efficient querying
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_episodes_project_id
                ON episodes(project_id)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_episodes_event_type
                ON episodes(event_type)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_episodes_timestamp
                ON episodes(timestamp)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_episodes_session_id
                ON episodes(session_id)
            """)

        self.logger.debug("Episode tables initialized")

    # ========================================================================
    # Event Recording
    # ========================================================================

    def record_event(
        self,
        event_type: str,
        event_data: Dict[str, Any],
        session_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Record a session event

        Args:
            event_type: Type of event (use EventType constants)
            event_data: Event-specific data
            session_id: Session identifier (generates if not provided)
            context: Current context snapshot

        Returns:
            event_id of recorded event
        """
        event_id = str(uuid.uuid4())
        session_id = session_id or self._get_current_session_id()
        timestamp = datetime.now().isoformat()

        episode = Episode(
            id=event_id,
            event_type=event_type,
            timestamp=timestamp,
            session_id=session_id,
            event_data=event_data,
            context=context
        )

        with self.db.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO episodes
                (id, project_id, event_type, timestamp, session_id, event_data, context)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    episode.id,
                    self.project_id,
                    episode.event_type,
                    episode.timestamp,
                    episode.session_id,
                    json.dumps(episode.event_data),
                    json.dumps(episode.context) if episode.context else None
                )
            )

        self.logger.debug(f"Recorded event: {event_type} ({event_id})")
        return event_id

    def record_decision(
        self,
        decision_type: str,
        options: List[str],
        chosen: str,
        rationale: str,
        session_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Record a decision point

        Args:
            decision_type: Type of decision (e.g., "agent_selection")
            options: Available options
            chosen: Chosen option
            rationale: Reason for choice
            session_id: Session identifier
            context: Current context snapshot

        Returns:
            decision_id
        """
        decision_data = {
            "decision_type": decision_type,
            "options": options,
            "chosen": chosen,
            "rationale": rationale
        }

        return self.record_event(
            EventType.DECISION_MADE,
            decision_data,
            session_id=session_id,
            context=context
        )

    def record_outcome(
        self,
        event_id: str,
        outcome: str,
        metrics: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Record outcome for a previously recorded event

        Args:
            event_id: Event identifier to attach outcome to
            outcome: Outcome status (e.g., "success", "failure", "partial")
            metrics: Outcome metrics (duration, tests passed, etc.)
        """
        outcome_data = {
            "status": outcome,
            "timestamp": datetime.now().isoformat(),
            "metrics": metrics or {}
        }

        with self.db.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE episodes
                SET outcome = ?
                WHERE id = ?
                """,
                (json.dumps(outcome_data), event_id)
            )

        self.logger.debug(f"Recorded outcome for {event_id}: {outcome}")

    # ========================================================================
    # Event Retrieval
    # ========================================================================

    def get_event(self, event_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a single event by ID

        Args:
            event_id: Event identifier

        Returns:
            Event dictionary or None if not found
        """
        conn = self.db._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT * FROM episodes
            WHERE id = ? AND project_id = ?
            """,
            (event_id, self.project_id)
        )

        row = cursor.fetchone()
        if row:
            return self._row_to_episode_dict(row)

        return None

    def get_recent_events(
        self,
        limit: int = 50,
        session_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get recent events

        Args:
            limit: Maximum number of events to return
            session_id: Filter by session (optional)

        Returns:
            List of event dictionaries
        """
        conn = self.db._get_connection()
        cursor = conn.cursor()

        query = """
            SELECT * FROM episodes
            WHERE project_id = ?
        """
        params = [self.project_id]

        if session_id:
            query += " AND session_id = ?"
            params.append(session_id)

        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)

        return [self._row_to_episode_dict(row) for row in cursor.fetchall()]

    def get_events_by_type(
        self,
        event_type: str,
        limit: int = 100,
        session_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get events filtered by type

        Args:
            event_type: Event type to filter
            limit: Maximum number of events to return
            session_id: Filter by session (optional)

        Returns:
            List of event dictionaries
        """
        conn = self.db._get_connection()
        cursor = conn.cursor()

        query = """
            SELECT * FROM episodes
            WHERE project_id = ? AND event_type = ?
        """
        params = [self.project_id, event_type]

        if session_id:
            query += " AND session_id = ?"
            params.append(session_id)

        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)

        return [self._row_to_episode_dict(row) for row in cursor.fetchall()]

    # ========================================================================
    # Similarity and Pattern Matching
    # ========================================================================

    def find_similar_episodes(
        self,
        current_context: Dict[str, Any],
        limit: int = 5,
        event_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Find similar past episodes based on context

        Args:
            current_context: Current context to match against
            limit: Maximum number of similar episodes to return
            event_type: Filter by event type (optional)

        Returns:
            List of similar episodes, ranked by similarity
        """
        conn = self.db._get_connection()
        cursor = conn.cursor()

        query = """
            SELECT * FROM episodes
            WHERE project_id = ? AND context IS NOT NULL
        """
        params = [self.project_id]

        if event_type:
            query += " AND event_type = ?"
            params.append(event_type)

        query += " ORDER BY timestamp DESC LIMIT 100"

        cursor.execute(query, params)

        # Score episodes by similarity
        episodes_with_scores = []
        for row in cursor.fetchall():
            episode = self._row_to_episode_dict(row)
            similarity_score = self._calculate_similarity(
                current_context,
                episode.get("context", {})
            )
            episodes_with_scores.append((similarity_score, episode))

        # Sort by similarity score (descending) and return top matches
        episodes_with_scores.sort(key=lambda x: x[0], reverse=True)
        return [episode for _, episode in episodes_with_scores[:limit]]

    def get_outcome_statistics(
        self,
        decision_type: str
    ) -> Dict[str, float]:
        """
        Get outcome statistics for a decision type

        Args:
            decision_type: Type of decision to analyze

        Returns:
            Dictionary with statistics:
            - success_rate: Percentage of successful outcomes
            - total_decisions: Total number of decisions
            - avg_duration_ms: Average duration
            - outcome_counts: Breakdown by outcome status
        """
        conn = self.db._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT event_data, outcome FROM episodes
            WHERE project_id = ?
              AND event_type = ?
              AND outcome IS NOT NULL
            """,
            (self.project_id, EventType.DECISION_MADE)
        )

        decisions = []
        for row in cursor.fetchall():
            event_data = json.loads(row["event_data"]) if row["event_data"] else {}
            if event_data.get("decision_type") == decision_type:
                outcome_data = json.loads(row["outcome"]) if row["outcome"] else {}
                decisions.append(outcome_data)

        if not decisions:
            return {
                "success_rate": 0.0,
                "total_decisions": 0,
                "avg_duration_ms": 0.0,
                "outcome_counts": {}
            }

        # Calculate statistics
        total = len(decisions)
        success_count = sum(1 for d in decisions if d.get("status") == "success")

        durations = [
            d.get("metrics", {}).get("duration_ms", 0)
            for d in decisions
            if d.get("metrics", {}).get("duration_ms")
        ]
        avg_duration = sum(durations) / len(durations) if durations else 0.0

        outcome_counts = {}
        for decision in decisions:
            status = decision.get("status", "unknown")
            outcome_counts[status] = outcome_counts.get(status, 0) + 1

        return {
            "success_rate": (success_count / total) * 100,
            "total_decisions": total,
            "avg_duration_ms": avg_duration,
            "outcome_counts": outcome_counts
        }

    # ========================================================================
    # Helper Methods
    # ========================================================================

    def _row_to_episode_dict(self, row) -> Dict[str, Any]:
        """Convert database row to episode dictionary"""
        episode = dict(row)

        # Parse JSON fields
        if episode.get("event_data"):
            try:
                episode["event_data"] = json.loads(episode["event_data"])
            except json.JSONDecodeError:
                episode["event_data"] = {}

        if episode.get("outcome"):
            try:
                episode["outcome"] = json.loads(episode["outcome"])
            except json.JSONDecodeError:
                episode["outcome"] = None

        if episode.get("context"):
            try:
                episode["context"] = json.loads(episode["context"])
            except json.JSONDecodeError:
                episode["context"] = None

        return episode

    def _calculate_similarity(
        self,
        context1: Dict[str, Any],
        context2: Dict[str, Any]
    ) -> float:
        """
        Calculate similarity score between two contexts

        Uses simple key overlap and value matching.
        Returns score between 0.0 and 1.0.
        """
        if not context1 or not context2:
            return 0.0

        # Get common keys
        keys1 = set(context1.keys())
        keys2 = set(context2.keys())
        common_keys = keys1 & keys2

        if not common_keys:
            return 0.0

        # Calculate match score
        matches = 0
        for key in common_keys:
            if context1[key] == context2[key]:
                matches += 1

        # Similarity = (matching values / common keys) * (common keys / total keys)
        value_match_ratio = matches / len(common_keys)
        key_overlap_ratio = len(common_keys) / len(keys1 | keys2)

        return value_match_ratio * key_overlap_ratio

    def _get_current_session_id(self) -> str:
        """Get or generate current session ID"""
        # Try to get from environment or generate new
        import os
        return os.environ.get("MOAI_SESSION_ID", str(uuid.uuid4()))

    # ========================================================================
    # Maintenance Operations
    # ========================================================================

    def cleanup_old_episodes(self, days: int = 90) -> int:
        """
        Delete episodes older than specified days

        Args:
            days: Age threshold in days

        Returns:
            Number of deleted episodes
        """
        from datetime import timedelta

        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()

        with self.db.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                DELETE FROM episodes
                WHERE project_id = ? AND timestamp < ?
                """,
                (self.project_id, cutoff_date)
            )
            deleted_count = cursor.rowcount

        self.logger.info(f"Cleaned up {deleted_count} old episodes (>{days} days)")
        return deleted_count


# ============================================================================
# Example Usage
# ============================================================================

if __name__ == "__main__":
    from pathlib import Path
    import time

    print("=== EpisodicMemory Example Usage ===\n")

    # Initialize with SwarmDB
    db_path = Path(".moai/memory/test_episodic.db")
    db_path.parent.mkdir(parents=True, exist_ok=True)

    db = SwarmDB(db_path=db_path)
    memory = EpisodicMemory(db, project_id="moai-adk")
    print("✓ EpisodicMemory initialized")

    # Example 1: Record command execution
    print("\n--- Example 1: Record Command Execution ---")
    cmd_id = memory.record_event(
        EventType.COMMAND_EXECUTED,
        {
            "command": "/moai:1-plan",
            "description": "Create user authentication SPEC"
        },
        context={
            "active_spec": None,
            "phase": "planning"
        }
    )
    print(f"✓ Command event recorded: {cmd_id}")

    # Example 2: Record decision
    print("\n--- Example 2: Record Agent Selection Decision ---")
    decision_id = memory.record_decision(
        decision_type="agent_selection",
        options=["expert-backend", "expert-frontend", "expert-database"],
        chosen="expert-backend",
        rationale="Backend API implementation required",
        context={
            "active_spec": "SPEC-001",
            "phase": "implementation",
            "task_type": "api_implementation"
        }
    )
    print(f"✓ Decision recorded: {decision_id}")

    # Example 3: Record outcome
    print("\n--- Example 3: Record Successful Outcome ---")
    time.sleep(0.1)
    memory.record_outcome(
        decision_id,
        outcome="success",
        metrics={
            "duration_ms": 3000,
            "tests_passed": 10,
            "coverage": 92.5
        }
    )
    print(f"✓ Outcome recorded for decision {decision_id}")

    # Example 4: Record another decision with failure
    print("\n--- Example 4: Record Failed Decision ---")
    decision_id2 = memory.record_decision(
        decision_type="agent_selection",
        options=["expert-frontend", "expert-uiux"],
        chosen="expert-frontend",
        rationale="UI component implementation"
    )
    memory.record_outcome(
        decision_id2,
        outcome="failure",
        metrics={
            "duration_ms": 1500,
            "error": "Missing dependencies"
        }
    )
    print(f"✓ Failed decision recorded: {decision_id2}")

    # Example 5: Get recent events
    print("\n--- Example 5: Get Recent Events ---")
    recent = memory.get_recent_events(limit=10)
    print(f"✓ Found {len(recent)} recent events:")
    for event in recent:
        print(f"  - {event['event_type']} @ {event['timestamp']}")

    # Example 6: Get events by type
    print("\n--- Example 6: Get Decision Events ---")
    decisions = memory.get_events_by_type(EventType.DECISION_MADE)
    print(f"✓ Found {len(decisions)} decision events")

    # Example 7: Find similar episodes
    print("\n--- Example 7: Find Similar Episodes ---")
    similar = memory.find_similar_episodes(
        current_context={
            "active_spec": "SPEC-001",
            "phase": "implementation",
            "task_type": "api_implementation"
        },
        limit=3
    )
    print(f"✓ Found {len(similar)} similar episodes:")
    for episode in similar:
        context = episode.get("context", {})
        print(f"  - {episode['event_type']} (context: {context})")

    # Example 8: Get outcome statistics
    print("\n--- Example 8: Get Outcome Statistics ---")
    stats = memory.get_outcome_statistics("agent_selection")
    print(f"✓ Agent selection statistics:")
    print(f"  - Total decisions: {stats['total_decisions']}")
    print(f"  - Success rate: {stats['success_rate']:.1f}%")
    print(f"  - Avg duration: {stats['avg_duration_ms']:.0f}ms")
    print(f"  - Outcome breakdown: {stats['outcome_counts']}")

    # Cleanup
    db.close()
    print("\n✅ EpisodicMemory demonstration complete")
    print(f"📦 Database location: {db_path}")
