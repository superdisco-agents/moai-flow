"""
Comprehensive tests for EpisodicMemory - Event and decision history tracking.

Test Coverage Requirements:
- Framework: pytest with in-memory SwarmDB fixtures
- Coverage Target: 90%+ (per config)
- Test Database: Use :memory: SQLite for testing

Test Areas:
1. Event recording and retrieval
2. Decision tracking and outcomes
3. Outcome recording and analysis
4. Event retrieval by type and time
5. Similar episode finding
6. Outcome statistics
7. Temporal sequence analysis
8. Context matching
"""

import json
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from unittest.mock import Mock, patch

import pytest

from moai_flow.memory.swarm_db import SwarmDB


class EpisodicMemory:
    """
    Event and decision history tracking system.

    Features:
    - Event recording with timestamps
    - Decision tracking with outcomes
    - Episode similarity matching
    - Temporal analysis
    - Context-based retrieval
    - Statistical outcome analysis
    """

    def __init__(self, db: SwarmDB, namespace: str = "episodic_memory"):
        """Initialize EpisodicMemory with database."""
        self.db = db
        self.namespace = namespace

    def record_event(
        self,
        event_type: str,
        context: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Record an event with context."""
        if not event_type:
            raise ValueError("Event type cannot be empty")

        import uuid
        event_id = str(uuid.uuid4())

        events = self.db.get(self.namespace, "events") or []
        events.append({
            "event_id": event_id,
            "event_type": event_type,
            "context": context,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat()
        })

        self.db.set(self.namespace, "events", events)
        return event_id

    def get_event(self, event_id: str) -> Optional[Dict[str, Any]]:
        """Get event by ID."""
        events = self.db.get(self.namespace, "events") or []
        for event in events:
            if event["event_id"] == event_id:
                return event
        return None

    def get_events(
        self,
        event_type: Optional[str] = None,
        limit: int = 100,
        reverse: bool = True
    ) -> List[Dict[str, Any]]:
        """Get events, optionally filtered by type."""
        events = self.db.get(self.namespace, "events") or []

        if event_type:
            events = [e for e in events if e["event_type"] == event_type]

        if reverse:
            events.reverse()

        return events[:limit]

    def get_events_by_timerange(
        self,
        start_time: datetime,
        end_time: datetime,
        event_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get events within a time range."""
        events = self.db.get(self.namespace, "events") or []

        start_iso = start_time.isoformat()
        end_iso = end_time.isoformat()

        filtered = [
            e for e in events
            if start_iso <= e["timestamp"] <= end_iso
        ]

        if event_type:
            filtered = [e for e in filtered if e["event_type"] == event_type]

        return filtered

    def record_decision(
        self,
        decision: str,
        context: Dict[str, Any],
        rationale: Optional[str] = None
    ) -> str:
        """Record a decision with context and rationale."""
        if not decision:
            raise ValueError("Decision cannot be empty")

        import uuid
        decision_id = str(uuid.uuid4())

        decisions = self.db.get(self.namespace, "decisions") or []
        decisions.append({
            "decision_id": decision_id,
            "decision": decision,
            "context": context,
            "rationale": rationale,
            "outcome": None,
            "timestamp": datetime.now().isoformat()
        })

        self.db.set(self.namespace, "decisions", decisions)
        return decision_id

    def get_decision(self, decision_id: str) -> Optional[Dict[str, Any]]:
        """Get decision by ID."""
        decisions = self.db.get(self.namespace, "decisions") or []
        for decision in decisions:
            if decision["decision_id"] == decision_id:
                return decision
        return None

    def record_outcome(
        self,
        decision_id: str,
        outcome: str,
        success: bool,
        metrics: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Record outcome for a decision."""
        decisions = self.db.get(self.namespace, "decisions") or []

        for decision in decisions:
            if decision["decision_id"] == decision_id:
                decision["outcome"] = {
                    "result": outcome,
                    "success": success,
                    "metrics": metrics or {},
                    "recorded_at": datetime.now().isoformat()
                }
                self.db.set(self.namespace, "decisions", decisions)
                return True

        return False

    def get_decisions(
        self,
        with_outcomes: Optional[bool] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get decisions, optionally filtered by outcome presence."""
        decisions = self.db.get(self.namespace, "decisions") or []

        if with_outcomes is True:
            decisions = [d for d in decisions if d["outcome"] is not None]
        elif with_outcomes is False:
            decisions = [d for d in decisions if d["outcome"] is None]

        decisions.reverse()
        return decisions[:limit]

    def find_similar_episodes(
        self,
        context: Dict[str, Any],
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Find similar past episodes based on context."""
        events = self.db.get(self.namespace, "events") or []

        # Simple similarity: count matching context keys
        scored_events = []
        for event in events:
            similarity_score = self._calculate_similarity(context, event["context"])
            if similarity_score > 0:
                scored_events.append({
                    **event,
                    "similarity_score": similarity_score
                })

        scored_events.sort(key=lambda x: x["similarity_score"], reverse=True)
        return scored_events[:limit]

    def _calculate_similarity(self, ctx1: Dict[str, Any], ctx2: Dict[str, Any]) -> float:
        """Calculate similarity score between two contexts."""
        if not ctx1 or not ctx2:
            return 0.0

        keys1 = set(ctx1.keys())
        keys2 = set(ctx2.keys())

        common_keys = keys1 & keys2
        if not common_keys:
            return 0.0

        matching_values = sum(
            1 for key in common_keys
            if ctx1[key] == ctx2[key]
        )

        # Jaccard similarity with value matching
        total_keys = len(keys1 | keys2)
        return matching_values / total_keys

    def get_outcome_statistics(self) -> Dict[str, Any]:
        """Get statistics about decision outcomes."""
        decisions = self.db.get(self.namespace, "decisions") or []

        with_outcomes = [d for d in decisions if d["outcome"] is not None]

        if not with_outcomes:
            return {
                "total_decisions": len(decisions),
                "decisions_with_outcomes": 0,
                "success_rate": 0.0,
                "pending_decisions": len(decisions)
            }

        successful = sum(1 for d in with_outcomes if d["outcome"]["success"])

        return {
            "total_decisions": len(decisions),
            "decisions_with_outcomes": len(with_outcomes),
            "pending_decisions": len(decisions) - len(with_outcomes),
            "success_rate": successful / len(with_outcomes),
            "successful_count": successful,
            "failed_count": len(with_outcomes) - successful
        }

    def analyze_temporal_sequence(
        self,
        event_types: List[str],
        time_window_hours: int = 24
    ) -> List[Dict[str, Any]]:
        """Analyze sequences of event types within a time window."""
        events = self.db.get(self.namespace, "events") or []

        # Filter by event types
        filtered = [e for e in events if e["event_type"] in event_types]

        # Sort by timestamp
        filtered.sort(key=lambda x: x["timestamp"])

        sequences = []
        for i in range(len(filtered) - 1):
            current = filtered[i]
            next_event = filtered[i + 1]

            current_time = datetime.fromisoformat(current["timestamp"])
            next_time = datetime.fromisoformat(next_event["timestamp"])

            time_diff = (next_time - current_time).total_seconds() / 3600

            if time_diff <= time_window_hours:
                sequences.append({
                    "from_event": current["event_type"],
                    "to_event": next_event["event_type"],
                    "time_diff_hours": time_diff,
                    "from_id": current["event_id"],
                    "to_id": next_event["event_id"]
                })

        return sequences

    def find_context_matches(
        self,
        context_query: Dict[str, Any],
        match_type: str = "partial"
    ) -> List[Dict[str, Any]]:
        """Find events with matching context."""
        events = self.db.get(self.namespace, "events") or []

        matches = []
        for event in events:
            if match_type == "exact":
                if event["context"] == context_query:
                    matches.append(event)
            elif match_type == "partial":
                if all(
                    key in event["context"] and event["context"][key] == value
                    for key, value in context_query.items()
                ):
                    matches.append(event)

        return matches

    def get_event_types(self) -> List[str]:
        """Get all unique event types."""
        events = self.db.get(self.namespace, "events") or []
        event_types = set(e["event_type"] for e in events)
        return sorted(list(event_types))

    def count_events_by_type(self) -> Dict[str, int]:
        """Count events grouped by type."""
        events = self.db.get(self.namespace, "events") or []

        counts = {}
        for event in events:
            event_type = event["event_type"]
            counts[event_type] = counts.get(event_type, 0) + 1

        return counts

    def get_recent_events(self, hours: int = 24, limit: int = 100) -> List[Dict[str, Any]]:
        """Get events from the last N hours."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        events = self.db.get(self.namespace, "events") or []

        recent = [
            e for e in events
            if datetime.fromisoformat(e["timestamp"]) >= cutoff_time
        ]

        recent.reverse()
        return recent[:limit]


@pytest.fixture
def memory_db():
    """Create in-memory SwarmDB for testing."""
    return SwarmDB(db_path=":memory:")


@pytest.fixture
def episodic_memory(memory_db):
    """Create EpisodicMemory instance for testing."""
    return EpisodicMemory(memory_db)


class TestEpisodicMemoryInitialization:
    """Test suite for EpisodicMemory initialization."""

    def test_initialization(self, memory_db):
        """Test EpisodicMemory initialization."""
        memory = EpisodicMemory(memory_db, namespace="test_namespace")

        assert memory.db is memory_db
        assert memory.namespace == "test_namespace"

    def test_default_namespace(self, memory_db):
        """Test default namespace."""
        memory = EpisodicMemory(memory_db)

        assert memory.namespace == "episodic_memory"


class TestEventRecording:
    """Test suite for event recording."""

    def test_record_event(self, episodic_memory):
        """Test recording an event."""
        event_id = episodic_memory.record_event(
            event_type="user_login",
            context={"user_id": "123", "ip": "192.168.1.1"}
        )

        assert event_id is not None
        assert isinstance(event_id, str)

    def test_record_event_with_metadata(self, episodic_memory):
        """Test recording event with metadata."""
        event_id = episodic_memory.record_event(
            event_type="api_call",
            context={"endpoint": "/users"},
            metadata={"latency_ms": 150}
        )

        event = episodic_memory.get_event(event_id)

        assert event["metadata"]["latency_ms"] == 150

    def test_record_empty_event_type_raises_error(self, episodic_memory):
        """Test that empty event type raises ValueError."""
        with pytest.raises(ValueError, match="Event type cannot be empty"):
            episodic_memory.record_event("", {})

    def test_get_event(self, episodic_memory):
        """Test retrieving event by ID."""
        event_id = episodic_memory.record_event("test_event", {"key": "value"})

        event = episodic_memory.get_event(event_id)

        assert event is not None
        assert event["event_type"] == "test_event"
        assert event["context"]["key"] == "value"

    def test_get_nonexistent_event(self, episodic_memory):
        """Test getting non-existent event returns None."""
        event = episodic_memory.get_event("nonexistent_id")

        assert event is None

    def test_record_multiple_events(self, episodic_memory):
        """Test recording multiple events."""
        ids = []
        for i in range(5):
            event_id = episodic_memory.record_event(f"event_{i}", {"index": i})
            ids.append(event_id)

        events = episodic_memory.get_events()

        assert len(events) == 5


class TestEventRetrieval:
    """Test suite for event retrieval."""

    def test_get_events(self, episodic_memory):
        """Test getting all events."""
        for i in range(3):
            episodic_memory.record_event("test", {"index": i})

        events = episodic_memory.get_events()

        assert len(events) == 3

    def test_get_events_by_type(self, episodic_memory):
        """Test getting events filtered by type."""
        episodic_memory.record_event("type_a", {})
        episodic_memory.record_event("type_b", {})
        episodic_memory.record_event("type_a", {})

        events = episodic_memory.get_events(event_type="type_a")

        assert len(events) == 2
        assert all(e["event_type"] == "type_a" for e in events)

    def test_get_events_with_limit(self, episodic_memory):
        """Test getting events with limit."""
        for i in range(10):
            episodic_memory.record_event("test", {"index": i})

        events = episodic_memory.get_events(limit=5)

        assert len(events) == 5

    def test_get_events_reverse_order(self, episodic_memory):
        """Test that events are returned in reverse order by default."""
        for i in range(3):
            episodic_memory.record_event("test", {"index": i})
            time.sleep(0.01)

        events = episodic_memory.get_events()

        # Most recent first
        assert events[0]["context"]["index"] == 2
        assert events[1]["context"]["index"] == 1
        assert events[2]["context"]["index"] == 0

    def test_get_events_forward_order(self, episodic_memory):
        """Test getting events in forward order."""
        for i in range(3):
            episodic_memory.record_event("test", {"index": i})

        events = episodic_memory.get_events(reverse=False)

        assert events[0]["context"]["index"] == 0
        assert events[1]["context"]["index"] == 1
        assert events[2]["context"]["index"] == 2


class TestTimeRangeRetrieval:
    """Test suite for time-based event retrieval."""

    def test_get_events_by_timerange(self, episodic_memory):
        """Test getting events within a time range."""
        # Record events with time delays
        episodic_memory.record_event("event1", {"time_index": 0})
        time.sleep(0.01)
        episodic_memory.record_event("event2", {"time_index": 1})
        time.sleep(0.01)
        episodic_memory.record_event("event3", {"time_index": 2})

        # Query for middle event
        start = datetime.now() - timedelta(seconds=0.015)
        end = datetime.now() - timedelta(seconds=0.005)

        events = episodic_memory.get_events_by_timerange(start, end)

        assert len(events) >= 1  # At least one event should be in range

    def test_get_events_by_timerange_with_type_filter(self, episodic_memory):
        """Test time range retrieval with event type filter."""
        # Record events of different types
        episodic_memory.record_event("type_a", {})
        time.sleep(0.01)
        episodic_memory.record_event("type_b", {})
        time.sleep(0.01)
        episodic_memory.record_event("type_a", {})

        start = datetime.now() - timedelta(hours=1)
        end = datetime.now() + timedelta(hours=1)

        events = episodic_memory.get_events_by_timerange(start, end, event_type="type_a")

        assert len(events) == 2


class TestDecisionTracking:
    """Test suite for decision tracking."""

    def test_record_decision(self, episodic_memory):
        """Test recording a decision."""
        decision_id = episodic_memory.record_decision(
            decision="use_fastapi",
            context={"project": "api_service"},
            rationale="Better async support"
        )

        assert decision_id is not None
        assert isinstance(decision_id, str)

    def test_get_decision(self, episodic_memory):
        """Test retrieving decision by ID."""
        decision_id = episodic_memory.record_decision(
            "decision", {"key": "value"}, "rationale"
        )

        decision = episodic_memory.get_decision(decision_id)

        assert decision is not None
        assert decision["decision"] == "decision"
        assert decision["rationale"] == "rationale"
        assert decision["outcome"] is None

    def test_get_nonexistent_decision(self, episodic_memory):
        """Test getting non-existent decision returns None."""
        decision = episodic_memory.get_decision("nonexistent")

        assert decision is None

    def test_record_empty_decision_raises_error(self, episodic_memory):
        """Test that empty decision raises ValueError."""
        with pytest.raises(ValueError, match="Decision cannot be empty"):
            episodic_memory.record_decision("", {})

    def test_record_decision_without_rationale(self, episodic_memory):
        """Test recording decision without rationale."""
        decision_id = episodic_memory.record_decision("decision", {})

        decision = episodic_memory.get_decision(decision_id)

        assert decision["rationale"] is None


class TestOutcomeRecording:
    """Test suite for outcome recording."""

    def test_record_outcome(self, episodic_memory):
        """Test recording outcome for a decision."""
        decision_id = episodic_memory.record_decision("test_decision", {})

        success = episodic_memory.record_outcome(
            decision_id,
            outcome="implemented_successfully",
            success=True,
            metrics={"time_saved": "20%"}
        )

        assert success is True

        decision = episodic_memory.get_decision(decision_id)
        assert decision["outcome"]["result"] == "implemented_successfully"
        assert decision["outcome"]["success"] is True
        assert decision["outcome"]["metrics"]["time_saved"] == "20%"

    def test_record_outcome_for_nonexistent_decision(self, episodic_memory):
        """Test recording outcome for non-existent decision returns False."""
        success = episodic_memory.record_outcome(
            "nonexistent",
            "outcome",
            success=True
        )

        assert success is False

    def test_record_outcome_without_metrics(self, episodic_memory):
        """Test recording outcome without metrics."""
        decision_id = episodic_memory.record_decision("decision", {})

        episodic_memory.record_outcome(decision_id, "outcome", success=True)

        decision = episodic_memory.get_decision(decision_id)
        assert decision["outcome"]["metrics"] == {}

    def test_update_outcome(self, episodic_memory):
        """Test updating outcome for a decision."""
        decision_id = episodic_memory.record_decision("decision", {})

        episodic_memory.record_outcome(decision_id, "first_outcome", success=True)
        episodic_memory.record_outcome(decision_id, "updated_outcome", success=False)

        decision = episodic_memory.get_decision(decision_id)
        assert decision["outcome"]["result"] == "updated_outcome"
        assert decision["outcome"]["success"] is False


class TestDecisionRetrieval:
    """Test suite for decision retrieval."""

    def test_get_all_decisions(self, episodic_memory):
        """Test getting all decisions."""
        for i in range(3):
            episodic_memory.record_decision(f"decision_{i}", {})

        decisions = episodic_memory.get_decisions()

        assert len(decisions) == 3

    def test_get_decisions_with_outcomes(self, episodic_memory):
        """Test getting only decisions with outcomes."""
        d1 = episodic_memory.record_decision("d1", {})
        d2 = episodic_memory.record_decision("d2", {})
        d3 = episodic_memory.record_decision("d3", {})

        episodic_memory.record_outcome(d1, "outcome", success=True)
        episodic_memory.record_outcome(d3, "outcome", success=False)

        decisions = episodic_memory.get_decisions(with_outcomes=True)

        assert len(decisions) == 2

    def test_get_decisions_without_outcomes(self, episodic_memory):
        """Test getting only decisions without outcomes."""
        d1 = episodic_memory.record_decision("d1", {})
        d2 = episodic_memory.record_decision("d2", {})
        d3 = episodic_memory.record_decision("d3", {})

        episodic_memory.record_outcome(d1, "outcome", success=True)

        decisions = episodic_memory.get_decisions(with_outcomes=False)

        assert len(decisions) == 2

    def test_get_decisions_with_limit(self, episodic_memory):
        """Test getting decisions with limit."""
        for i in range(10):
            episodic_memory.record_decision(f"decision_{i}", {})

        decisions = episodic_memory.get_decisions(limit=5)

        assert len(decisions) == 5


class TestSimilarEpisodes:
    """Test suite for finding similar episodes."""

    def test_find_similar_episodes(self, episodic_memory):
        """Test finding similar episodes based on context."""
        episodic_memory.record_event("event1", {"lang": "python", "task": "api"})
        episodic_memory.record_event("event2", {"lang": "python", "task": "cli"})
        episodic_memory.record_event("event3", {"lang": "javascript", "task": "api"})

        similar = episodic_memory.find_similar_episodes(
            context={"lang": "python", "task": "api"}
        )

        assert len(similar) > 0
        assert similar[0]["event_type"] == "event1"
        assert similar[0]["similarity_score"] > 0

    def test_find_similar_episodes_with_limit(self, episodic_memory):
        """Test finding similar episodes with limit."""
        for i in range(10):
            episodic_memory.record_event(f"event_{i}", {"common": "value"})

        similar = episodic_memory.find_similar_episodes(
            context={"common": "value"},
            limit=3
        )

        assert len(similar) == 3

    def test_find_similar_episodes_no_matches(self, episodic_memory):
        """Test finding similar episodes with no matches."""
        episodic_memory.record_event("event", {"key": "value"})

        similar = episodic_memory.find_similar_episodes(
            context={"different": "context"}
        )

        assert len(similar) == 0

    def test_similarity_calculation(self, episodic_memory):
        """Test similarity score calculation."""
        memory = episodic_memory

        # Exact match
        score = memory._calculate_similarity(
            {"a": 1, "b": 2},
            {"a": 1, "b": 2}
        )
        assert score == 1.0

        # Partial match
        score = memory._calculate_similarity(
            {"a": 1, "b": 2},
            {"a": 1, "c": 3}
        )
        assert 0 < score < 1

        # No match
        score = memory._calculate_similarity(
            {"a": 1},
            {"b": 2}
        )
        assert score == 0.0


class TestOutcomeStatistics:
    """Test suite for outcome statistics."""

    def test_get_outcome_statistics(self, episodic_memory):
        """Test getting outcome statistics."""
        # Record decisions with outcomes
        for i in range(10):
            decision_id = episodic_memory.record_decision(f"decision_{i}", {})
            if i < 7:  # 7 with outcomes
                success = i < 5  # 5 successful, 2 failed
                episodic_memory.record_outcome(decision_id, "outcome", success=success)

        stats = episodic_memory.get_outcome_statistics()

        assert stats["total_decisions"] == 10
        assert stats["decisions_with_outcomes"] == 7
        assert stats["pending_decisions"] == 3
        assert abs(stats["success_rate"] - (5/7)) < 0.01
        assert stats["successful_count"] == 5
        assert stats["failed_count"] == 2

    def test_get_outcome_statistics_empty(self, episodic_memory):
        """Test statistics with no decisions."""
        stats = episodic_memory.get_outcome_statistics()

        assert stats["total_decisions"] == 0
        assert stats["success_rate"] == 0.0

    def test_get_outcome_statistics_no_outcomes(self, episodic_memory):
        """Test statistics with decisions but no outcomes."""
        for i in range(5):
            episodic_memory.record_decision(f"decision_{i}", {})

        stats = episodic_memory.get_outcome_statistics()

        assert stats["total_decisions"] == 5
        assert stats["decisions_with_outcomes"] == 0
        assert stats["pending_decisions"] == 5


class TestTemporalSequenceAnalysis:
    """Test suite for temporal sequence analysis."""

    def test_analyze_temporal_sequence(self, episodic_memory):
        """Test analyzing temporal sequences of events."""
        # Record sequence with small delays
        episodic_memory.record_event("event_a", {})
        time.sleep(0.01)
        episodic_memory.record_event("event_b", {})
        time.sleep(0.01)
        episodic_memory.record_event("event_c", {})

        sequences = episodic_memory.analyze_temporal_sequence(
            event_types=["event_a", "event_b", "event_c"],
            time_window_hours=24
        )

        assert len(sequences) == 2
        assert sequences[0]["from_event"] == "event_a"
        assert sequences[0]["to_event"] == "event_b"

    def test_analyze_temporal_sequence_with_window(self, episodic_memory):
        """Test temporal sequence with time window constraint."""
        # Record events with varying time gaps
        episodic_memory.record_event("event_a", {})
        time.sleep(0.01)
        episodic_memory.record_event("event_b", {})

        # Use very small time window
        sequences = episodic_memory.analyze_temporal_sequence(
            event_types=["event_a", "event_b"],
            time_window_hours=0.001  # Very small window
        )

        # Should find no sequences due to small window
        assert len(sequences) == 0


class TestContextMatching:
    """Test suite for context matching."""

    def test_find_context_matches_exact(self, episodic_memory):
        """Test finding exact context matches."""
        episodic_memory.record_event("event1", {"a": 1, "b": 2})
        episodic_memory.record_event("event2", {"a": 1, "b": 2})
        episodic_memory.record_event("event3", {"a": 1, "b": 3})

        matches = episodic_memory.find_context_matches(
            context_query={"a": 1, "b": 2},
            match_type="exact"
        )

        assert len(matches) == 2

    def test_find_context_matches_partial(self, episodic_memory):
        """Test finding partial context matches."""
        episodic_memory.record_event("event1", {"a": 1, "b": 2, "c": 3})
        episodic_memory.record_event("event2", {"a": 1, "b": 2})
        episodic_memory.record_event("event3", {"a": 1, "x": 9})

        matches = episodic_memory.find_context_matches(
            context_query={"a": 1, "b": 2},
            match_type="partial"
        )

        assert len(matches) == 2

    def test_find_context_matches_no_results(self, episodic_memory):
        """Test context matching with no results."""
        episodic_memory.record_event("event", {"a": 1})

        matches = episodic_memory.find_context_matches(
            context_query={"b": 2},
            match_type="exact"
        )

        assert len(matches) == 0


class TestEventTypeOperations:
    """Test suite for event type operations."""

    def test_get_event_types(self, episodic_memory):
        """Test getting all unique event types."""
        episodic_memory.record_event("type_a", {})
        episodic_memory.record_event("type_b", {})
        episodic_memory.record_event("type_a", {})
        episodic_memory.record_event("type_c", {})

        event_types = episodic_memory.get_event_types()

        assert len(event_types) == 3
        assert "type_a" in event_types
        assert "type_b" in event_types
        assert "type_c" in event_types

    def test_get_event_types_sorted(self, episodic_memory):
        """Test that event types are returned sorted."""
        episodic_memory.record_event("zebra", {})
        episodic_memory.record_event("apple", {})
        episodic_memory.record_event("monkey", {})

        event_types = episodic_memory.get_event_types()

        assert event_types == ["apple", "monkey", "zebra"]

    def test_count_events_by_type(self, episodic_memory):
        """Test counting events by type."""
        episodic_memory.record_event("type_a", {})
        episodic_memory.record_event("type_a", {})
        episodic_memory.record_event("type_b", {})
        episodic_memory.record_event("type_a", {})

        counts = episodic_memory.count_events_by_type()

        assert counts["type_a"] == 3
        assert counts["type_b"] == 1


class TestRecentEvents:
    """Test suite for recent events retrieval."""

    def test_get_recent_events(self, episodic_memory):
        """Test getting recent events."""
        episodic_memory.record_event("recent", {})

        recent = episodic_memory.get_recent_events(hours=24)

        assert len(recent) == 1

    def test_get_recent_events_with_limit(self, episodic_memory):
        """Test getting recent events with limit."""
        for i in range(10):
            episodic_memory.record_event(f"event_{i}", {})

        recent = episodic_memory.get_recent_events(hours=24, limit=5)

        assert len(recent) == 5


class TestEdgeCases:
    """Test suite for edge cases."""

    def test_unicode_in_events(self, episodic_memory):
        """Test unicode support in events."""
        event_id = episodic_memory.record_event(
            "unicode_event",
            {"message": "안녕하세요 🚀"}
        )

        event = episodic_memory.get_event(event_id)

        assert event["context"]["message"] == "안녕하세요 🚀"

    def test_large_context_in_event(self, episodic_memory):
        """Test recording event with large context."""
        large_context = {"data": "x" * 100000}

        event_id = episodic_memory.record_event("large_event", large_context)

        event = episodic_memory.get_event(event_id)

        assert len(event["context"]["data"]) == 100000

    def test_empty_context_in_event(self, episodic_memory):
        """Test recording event with empty context."""
        event_id = episodic_memory.record_event("empty_context", {})

        event = episodic_memory.get_event(event_id)

        assert event["context"] == {}

    def test_none_values_in_context(self, episodic_memory):
        """Test None values in event context."""
        event_id = episodic_memory.record_event("event", {"nullable": None})

        event = episodic_memory.get_event(event_id)

        assert event["context"]["nullable"] is None
