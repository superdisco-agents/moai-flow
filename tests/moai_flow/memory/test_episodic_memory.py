#!/usr/bin/env python3
"""
Unit Tests for EpisodicMemory

Tests event recording, retrieval, similarity matching, and statistics.
"""

import json
import pytest
import sys
import tempfile
import time
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to path
_test_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(_test_dir))

# Import from moai-flow directory
_moai_flow_dir = _test_dir / "moai-flow"
sys.path.insert(0, str(_moai_flow_dir))

from memory.swarm_db import SwarmDB
from memory.episodic_memory import (
    EpisodicMemory,
    EventType,
    Episode
)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def temp_db():
    """Create temporary database for testing"""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_episodic.db"
        db = SwarmDB(db_path=db_path)
        yield db
        db.close()


@pytest.fixture
def episodic_memory(temp_db):
    """Create EpisodicMemory instance for testing"""
    return EpisodicMemory(temp_db, project_id="test-project")


# ============================================================================
# Episode Data Structure Tests
# ============================================================================

class TestEpisode:
    """Test Episode data structure"""

    def test_episode_creation(self):
        """Test Episode creation"""
        episode = Episode(
            id="test-123",
            event_type=EventType.DECISION_MADE,
            timestamp="2025-11-29T10:00:00",
            session_id="session-1",
            event_data={"decision_type": "agent_selection"},
            context={"phase": "planning"}
        )

        assert episode.id == "test-123"
        assert episode.event_type == EventType.DECISION_MADE
        assert episode.session_id == "session-1"

    def test_episode_to_dict(self):
        """Test Episode to dictionary conversion"""
        episode = Episode(
            id="test-123",
            event_type=EventType.COMMAND_EXECUTED,
            timestamp="2025-11-29T10:00:00",
            session_id="session-1",
            event_data={"command": "/moai:1-plan"},
            outcome={"status": "success"}
        )

        episode_dict = episode.to_dict()
        assert episode_dict["id"] == "test-123"
        assert episode_dict["event_type"] == EventType.COMMAND_EXECUTED
        assert episode_dict["outcome"]["status"] == "success"

    def test_episode_from_dict(self):
        """Test Episode from dictionary creation"""
        data = {
            "id": "test-123",
            "event_type": EventType.AGENT_SPAWNED,
            "timestamp": "2025-11-29T10:00:00",
            "session_id": "session-1",
            "event_data": {"agent_type": "expert-backend"},
            "outcome": None,
            "context": None
        }

        episode = Episode.from_dict(data)
        assert episode.id == "test-123"
        assert episode.event_type == EventType.AGENT_SPAWNED


# ============================================================================
# EpisodicMemory Initialization Tests
# ============================================================================

class TestEpisodicMemoryInit:
    """Test EpisodicMemory initialization"""

    def test_initialization(self, temp_db):
        """Test basic initialization"""
        memory = EpisodicMemory(temp_db, project_id="test-project")
        assert memory.project_id == "test-project"
        assert memory.db is not None

    def test_table_creation(self, temp_db):
        """Test episode tables are created"""
        memory = EpisodicMemory(temp_db, project_id="test-project")

        # Verify table exists
        conn = temp_db._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='episodes'"
        )
        assert cursor.fetchone() is not None


# ============================================================================
# Event Recording Tests
# ============================================================================

class TestEventRecording:
    """Test event recording functionality"""

    def test_record_event(self, episodic_memory):
        """Test basic event recording"""
        event_id = episodic_memory.record_event(
            EventType.COMMAND_EXECUTED,
            {"command": "/moai:1-plan"},
            session_id="session-1"
        )

        assert event_id is not None
        assert len(event_id) > 0

    def test_record_event_with_context(self, episodic_memory):
        """Test event recording with context"""
        event_id = episodic_memory.record_event(
            EventType.SPEC_CREATED,
            {"spec_id": "SPEC-001"},
            context={"phase": "planning", "user": "test"}
        )

        event = episodic_memory.get_event(event_id)
        assert event["context"]["phase"] == "planning"
        assert event["context"]["user"] == "test"

    def test_record_decision(self, episodic_memory):
        """Test decision recording"""
        decision_id = episodic_memory.record_decision(
            decision_type="agent_selection",
            options=["expert-backend", "expert-frontend"],
            chosen="expert-backend",
            rationale="Backend API needed"
        )

        event = episodic_memory.get_event(decision_id)
        assert event["event_type"] == EventType.DECISION_MADE
        assert event["event_data"]["decision_type"] == "agent_selection"
        assert event["event_data"]["chosen"] == "expert-backend"

    def test_record_outcome_success(self, episodic_memory):
        """Test successful outcome recording"""
        decision_id = episodic_memory.record_decision(
            "agent_selection",
            ["expert-backend"],
            "expert-backend",
            "API implementation"
        )

        episodic_memory.record_outcome(
            decision_id,
            "success",
            {"duration_ms": 3000, "tests_passed": 10}
        )

        event = episodic_memory.get_event(decision_id)
        assert event["outcome"]["status"] == "success"
        assert event["outcome"]["metrics"]["tests_passed"] == 10

    def test_record_outcome_failure(self, episodic_memory):
        """Test failure outcome recording"""
        event_id = episodic_memory.record_event(
            EventType.AGENT_SPAWNED,
            {"agent_type": "expert-frontend"}
        )

        episodic_memory.record_outcome(
            event_id,
            "failure",
            {"error": "Missing dependencies"}
        )

        event = episodic_memory.get_event(event_id)
        assert event["outcome"]["status"] == "failure"
        assert "error" in event["outcome"]["metrics"]


# ============================================================================
# Event Retrieval Tests
# ============================================================================

class TestEventRetrieval:
    """Test event retrieval functionality"""

    def test_get_event(self, episodic_memory):
        """Test getting single event"""
        event_id = episodic_memory.record_event(
            EventType.COMMAND_EXECUTED,
            {"command": "/moai:2-run"}
        )

        event = episodic_memory.get_event(event_id)
        assert event is not None
        assert event["id"] == event_id
        assert event["event_data"]["command"] == "/moai:2-run"

    def test_get_event_not_found(self, episodic_memory):
        """Test getting non-existent event"""
        event = episodic_memory.get_event("nonexistent-id")
        assert event is None

    def test_get_recent_events(self, episodic_memory):
        """Test getting recent events"""
        # Record multiple events
        for i in range(5):
            episodic_memory.record_event(
                EventType.COMMAND_EXECUTED,
                {"command": f"/moai:{i}"}
            )
            time.sleep(0.01)  # Ensure different timestamps

        recent = episodic_memory.get_recent_events(limit=3)
        assert len(recent) == 3
        # Should be in reverse chronological order
        assert "/moai:4" in recent[0]["event_data"]["command"]

    def test_get_recent_events_with_session_filter(self, episodic_memory):
        """Test getting recent events filtered by session"""
        episodic_memory.record_event(
            EventType.COMMAND_EXECUTED,
            {"command": "/moai:1"},
            session_id="session-1"
        )
        episodic_memory.record_event(
            EventType.COMMAND_EXECUTED,
            {"command": "/moai:2"},
            session_id="session-2"
        )

        recent = episodic_memory.get_recent_events(session_id="session-1")
        assert len(recent) == 1
        assert recent[0]["session_id"] == "session-1"

    def test_get_events_by_type(self, episodic_memory):
        """Test getting events filtered by type"""
        episodic_memory.record_event(
            EventType.COMMAND_EXECUTED,
            {"command": "/moai:1"}
        )
        episodic_memory.record_decision(
            "agent_selection", ["backend"], "backend", "API"
        )
        episodic_memory.record_event(
            EventType.ERROR_OCCURRED,
            {"error": "Test error"}
        )

        decisions = episodic_memory.get_events_by_type(EventType.DECISION_MADE)
        assert len(decisions) == 1
        assert decisions[0]["event_type"] == EventType.DECISION_MADE

        errors = episodic_memory.get_events_by_type(EventType.ERROR_OCCURRED)
        assert len(errors) == 1


# ============================================================================
# Similarity Matching Tests
# ============================================================================

class TestSimilarityMatching:
    """Test episode similarity matching"""

    def test_find_similar_episodes_exact_match(self, episodic_memory):
        """Test finding episodes with exact context match"""
        context = {
            "active_spec": "SPEC-001",
            "phase": "implementation",
            "task_type": "api"
        }

        # Record episode with matching context
        episodic_memory.record_decision(
            "agent_selection",
            ["backend"],
            "backend",
            "API",
            context=context
        )

        # Find similar
        similar = episodic_memory.find_similar_episodes(context)
        assert len(similar) > 0
        assert similar[0]["context"] == context

    def test_find_similar_episodes_partial_match(self, episodic_memory):
        """Test finding episodes with partial context match"""
        episodic_memory.record_decision(
            "agent_selection",
            ["backend"],
            "backend",
            "API",
            context={"phase": "implementation", "task_type": "api"}
        )

        similar = episodic_memory.find_similar_episodes(
            {"phase": "implementation", "task_type": "database"}
        )
        assert len(similar) > 0

    def test_find_similar_episodes_with_event_type_filter(self, episodic_memory):
        """Test similarity search with event type filter"""
        episodic_memory.record_decision(
            "agent_selection",
            ["backend"],
            "backend",
            "API",
            context={"phase": "implementation"}
        )
        episodic_memory.record_event(
            EventType.COMMAND_EXECUTED,
            {"command": "/moai:1"},
            context={"phase": "implementation"}
        )

        similar = episodic_memory.find_similar_episodes(
            {"phase": "implementation"},
            event_type=EventType.DECISION_MADE
        )
        assert len(similar) == 1
        assert similar[0]["event_type"] == EventType.DECISION_MADE

    def test_similarity_calculation(self, episodic_memory):
        """Test similarity score calculation"""
        context1 = {"a": 1, "b": 2, "c": 3}
        context2 = {"a": 1, "b": 2, "d": 4}

        score = episodic_memory._calculate_similarity(context1, context2)
        assert 0.0 <= score <= 1.0

    def test_similarity_empty_contexts(self, episodic_memory):
        """Test similarity with empty contexts"""
        score = episodic_memory._calculate_similarity({}, {})
        assert score == 0.0


# ============================================================================
# Statistics Tests
# ============================================================================

class TestOutcomeStatistics:
    """Test outcome statistics analysis"""

    def test_get_outcome_statistics_basic(self, episodic_memory):
        """Test basic outcome statistics"""
        # Record decisions with outcomes
        for i in range(5):
            decision_id = episodic_memory.record_decision(
                "agent_selection",
                ["backend"],
                "backend",
                "Test"
            )
            outcome = "success" if i < 3 else "failure"
            episodic_memory.record_outcome(
                decision_id,
                outcome,
                {"duration_ms": 1000 * (i + 1)}
            )

        stats = episodic_memory.get_outcome_statistics("agent_selection")
        assert stats["total_decisions"] == 5
        assert stats["success_rate"] == 60.0  # 3 out of 5
        assert stats["avg_duration_ms"] == 3000.0  # Average of 1000-5000

    def test_get_outcome_statistics_no_decisions(self, episodic_memory):
        """Test statistics when no decisions exist"""
        stats = episodic_memory.get_outcome_statistics("nonexistent_type")
        assert stats["total_decisions"] == 0
        assert stats["success_rate"] == 0.0

    def test_get_outcome_statistics_outcome_counts(self, episodic_memory):
        """Test outcome count breakdown"""
        for outcome in ["success", "success", "failure", "partial"]:
            decision_id = episodic_memory.record_decision(
                "test_decision",
                ["option"],
                "option",
                "test"
            )
            episodic_memory.record_outcome(decision_id, outcome)

        stats = episodic_memory.get_outcome_statistics("test_decision")
        assert stats["outcome_counts"]["success"] == 2
        assert stats["outcome_counts"]["failure"] == 1
        assert stats["outcome_counts"]["partial"] == 1


# ============================================================================
# Maintenance Tests
# ============================================================================

class TestMaintenance:
    """Test maintenance operations"""

    def test_cleanup_old_episodes(self, episodic_memory, temp_db):
        """Test cleanup of old episodes"""
        # Record episode with old timestamp
        with temp_db.transaction() as conn:
            cursor = conn.cursor()
            old_timestamp = (datetime.now() - timedelta(days=100)).isoformat()
            cursor.execute(
                """
                INSERT INTO episodes
                (id, project_id, event_type, timestamp, session_id, event_data)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    "old-episode",
                    "test-project",
                    EventType.COMMAND_EXECUTED,
                    old_timestamp,
                    "session-1",
                    json.dumps({"command": "/moai:1"})
                )
            )

        # Record recent episode
        episodic_memory.record_event(
            EventType.COMMAND_EXECUTED,
            {"command": "/moai:2"}
        )

        # Cleanup old episodes
        deleted = episodic_memory.cleanup_old_episodes(days=90)
        assert deleted == 1

        # Verify old episode is gone
        event = episodic_memory.get_event("old-episode")
        assert event is None


# ============================================================================
# Integration Tests
# ============================================================================

class TestIntegration:
    """Integration tests for complete workflows"""

    def test_complete_decision_workflow(self, episodic_memory):
        """Test complete decision recording and analysis workflow"""
        # Record decision
        decision_id = episodic_memory.record_decision(
            decision_type="agent_selection",
            options=["expert-backend", "expert-frontend"],
            chosen="expert-backend",
            rationale="Backend API implementation",
            context={
                "active_spec": "SPEC-001",
                "phase": "implementation",
                "task_type": "api"
            }
        )

        # Record outcome
        episodic_memory.record_outcome(
            decision_id,
            "success",
            {
                "duration_ms": 3000,
                "tests_passed": 10,
                "coverage": 92.5
            }
        )

        # Retrieve and verify
        event = episodic_memory.get_event(decision_id)
        assert event["event_type"] == EventType.DECISION_MADE
        assert event["outcome"]["status"] == "success"

        # Find similar
        similar = episodic_memory.find_similar_episodes(
            {"active_spec": "SPEC-001", "phase": "implementation"}
        )
        assert len(similar) > 0

        # Get statistics
        stats = episodic_memory.get_outcome_statistics("agent_selection")
        assert stats["total_decisions"] == 1
        assert stats["success_rate"] == 100.0

    def test_multi_session_tracking(self, episodic_memory):
        """Test tracking events across multiple sessions"""
        # Session 1 events
        episodic_memory.record_event(
            EventType.COMMAND_EXECUTED,
            {"command": "/moai:1-plan"},
            session_id="session-1"
        )

        # Session 2 events
        episodic_memory.record_event(
            EventType.COMMAND_EXECUTED,
            {"command": "/moai:2-run"},
            session_id="session-2"
        )

        # Query all events
        all_events = episodic_memory.get_recent_events(limit=10)
        assert len(all_events) == 2

        # Query session-specific
        session1_events = episodic_memory.get_recent_events(session_id="session-1")
        assert len(session1_events) == 1
        assert session1_events[0]["session_id"] == "session-1"


# ============================================================================
# Run Tests
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
