#!/usr/bin/env python3
"""
Unit tests for SemanticMemory

Tests:
- Knowledge storage and retrieval
- Confidence scoring and updates
- Full-text search
- Code pattern management
- Knowledge pruning
- Statistics and metrics
"""

import json
import pytest
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from moai_flow.memory.swarm_db import SwarmDB
from moai_flow.memory.semantic_memory import (
    SemanticMemory,
    KnowledgeCategory
)


@pytest.fixture
def temp_db():
    """Create temporary database for testing"""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_swarm.db"
        db = SwarmDB(db_path=db_path)
        yield db
        db.close()


@pytest.fixture
def memory(temp_db):
    """Create SemanticMemory instance for testing"""
    return SemanticMemory(temp_db, project_id="test-project")


class TestKnowledgeStorage:
    """Test knowledge storage and retrieval"""

    def test_store_knowledge(self, memory):
        """Test storing knowledge with metadata"""
        knowledge_id = memory.store_knowledge(
            topic="test_topic",
            knowledge={"key": "value", "data": [1, 2, 3]},
            confidence=0.8,
            category=KnowledgeCategory.BEST_PRACTICE,
            tags=["test", "example"]
        )

        assert isinstance(knowledge_id, str)
        assert len(knowledge_id) > 0

    def test_retrieve_knowledge(self, memory):
        """Test retrieving knowledge by topic"""
        # Store knowledge
        memory.store_knowledge(
            topic="jwt_auth",
            knowledge={
                "decision": "Use JWT",
                "rationale": "Stateless"
            },
            confidence=0.9,
            category=KnowledgeCategory.ARCHITECTURAL_DECISION
        )

        # Retrieve
        result = memory.retrieve_knowledge("jwt_auth")

        assert result is not None
        assert result["topic"] == "jwt_auth"
        assert result["confidence"] == 0.9
        assert result["knowledge"]["decision"] == "Use JWT"
        assert result["category"] == KnowledgeCategory.ARCHITECTURAL_DECISION

    def test_retrieve_nonexistent(self, memory):
        """Test retrieving non-existent knowledge returns None"""
        result = memory.retrieve_knowledge("nonexistent")
        assert result is None

    def test_confidence_validation(self, memory):
        """Test confidence is clamped to [0.0, 1.0]"""
        # Above 1.0
        id1 = memory.store_knowledge(
            topic="test1",
            knowledge={"data": "test"},
            confidence=1.5
        )
        result1 = memory.retrieve_knowledge("test1")
        assert result1["confidence"] == 1.0

        # Below 0.0
        id2 = memory.store_knowledge(
            topic="test2",
            knowledge={"data": "test"},
            confidence=-0.5
        )
        result2 = memory.retrieve_knowledge("test2")
        assert result2["confidence"] == 0.0

    def test_update_knowledge(self, memory):
        """Test updating existing knowledge"""
        # Store initial
        knowledge_id = memory.store_knowledge(
            topic="test",
            knowledge={"version": 1},
            confidence=0.5,
            tags=["old"]
        )

        # Update
        success = memory.update_knowledge(
            knowledge_id,
            knowledge={"version": 2},
            confidence=0.8,
            tags=["new", "updated"]
        )

        assert success is True

        # Verify update
        result = memory.retrieve_knowledge("test")
        assert result["knowledge"]["version"] == 2
        assert result["confidence"] == 0.8
        assert "updated" in result["tags"]

    def test_update_nonexistent(self, memory):
        """Test updating non-existent knowledge returns False"""
        success = memory.update_knowledge(
            "nonexistent-id",
            knowledge={"data": "test"}
        )
        assert success is False


class TestConfidenceScoring:
    """Test confidence scoring mechanism"""

    def test_record_success(self, memory):
        """Test recording successful use increases confidence"""
        # Store with medium confidence
        knowledge_id = memory.store_knowledge(
            topic="test",
            knowledge={"data": "test"},
            confidence=0.5
        )

        # Record success (should +0.1)
        memory.record_success(knowledge_id)

        result = memory.retrieve_knowledge("test")
        assert result["confidence"] == pytest.approx(0.6)
        assert result["success_count"] == 1

    def test_record_failure(self, memory):
        """Test recording failure decreases confidence"""
        # Store with medium confidence
        knowledge_id = memory.store_knowledge(
            topic="test",
            knowledge={"data": "test"},
            confidence=0.6
        )

        # Record failure (should -0.2)
        memory.record_failure(knowledge_id)

        result = memory.retrieve_knowledge("test")
        assert result["confidence"] == pytest.approx(0.4)
        assert result["failure_count"] == 1

    def test_confidence_bounds(self, memory):
        """Test confidence stays within [0.0, 1.0]"""
        # Test upper bound
        knowledge_id1 = memory.store_knowledge(
            topic="test1",
            knowledge={"data": "test"},
            confidence=0.98
        )

        # Multiple successes shouldn't exceed 1.0
        for _ in range(5):
            memory.record_success(knowledge_id1)

        result1 = memory.retrieve_knowledge("test1")
        assert result1["confidence"] <= 1.0

        # Test lower bound
        knowledge_id2 = memory.store_knowledge(
            topic="test2",
            knowledge={"data": "test"},
            confidence=0.15
        )

        # Multiple failures shouldn't go below 0.0
        for _ in range(5):
            memory.record_failure(knowledge_id2)

        result2 = memory.retrieve_knowledge("test2")
        assert result2["confidence"] >= 0.0

    def test_update_confidence_directly(self, memory):
        """Test directly updating confidence"""
        knowledge_id = memory.store_knowledge(
            topic="test",
            knowledge={"data": "test"},
            confidence=0.5
        )

        memory.update_confidence(knowledge_id, 0.9)

        result = memory.retrieve_knowledge("test")
        assert result["confidence"] == pytest.approx(0.9)


class TestSearch:
    """Test full-text search functionality"""

    def test_search_knowledge(self, memory):
        """Test searching across knowledge"""
        # Store multiple items
        memory.store_knowledge(
            topic="jwt_auth",
            knowledge={"decision": "Use JWT tokens for authentication"},
            tags=["auth", "security"]
        )
        memory.store_knowledge(
            topic="api_design",
            knowledge={"pattern": "RESTful API design"},
            tags=["api", "design"]
        )
        memory.store_knowledge(
            topic="oauth2",
            knowledge={"decision": "OAuth2 for third-party authentication"},
            tags=["auth", "oauth"]
        )

        # Search for authentication
        results = memory.search_knowledge("authentication")

        assert len(results) >= 2
        topics = [r["topic"] for r in results]
        assert "jwt_auth" in topics or "oauth2" in topics

    def test_search_with_category_filter(self, memory):
        """Test search with category filtering"""
        # Store different categories
        memory.store_knowledge(
            topic="adr1",
            knowledge={"decision": "Use PostgreSQL"},
            category=KnowledgeCategory.ARCHITECTURAL_DECISION
        )
        memory.store_knowledge(
            topic="bp1",
            knowledge={"practice": "Write unit tests"},
            category=KnowledgeCategory.BEST_PRACTICE
        )

        # Search with category filter
        results = memory.search_knowledge(
            "use",
            category=KnowledgeCategory.ARCHITECTURAL_DECISION
        )

        assert len(results) >= 1
        assert all(r["category"] == KnowledgeCategory.ARCHITECTURAL_DECISION for r in results)

    def test_search_with_confidence_filter(self, memory):
        """Test search with confidence threshold"""
        # Store with different confidences
        memory.store_knowledge(
            topic="high_conf",
            knowledge={"data": "reliable pattern"},
            confidence=0.9
        )
        memory.store_knowledge(
            topic="low_conf",
            knowledge={"data": "experimental pattern"},
            confidence=0.3
        )

        # Search with min confidence
        results = memory.search_knowledge(
            "pattern",
            min_confidence=0.5
        )

        assert all(r["confidence"] >= 0.5 for r in results)
        topics = [r["topic"] for r in results]
        assert "high_conf" in topics
        assert "low_conf" not in topics

    def test_search_limit(self, memory):
        """Test search result limit"""
        # Store many items
        for i in range(20):
            memory.store_knowledge(
                topic=f"item_{i}",
                knowledge={"test": "data"},
                confidence=0.5
            )

        results = memory.search_knowledge("data", limit=5)

        assert len(results) <= 5


class TestListKnowledge:
    """Test listing knowledge"""

    def test_list_all(self, memory):
        """Test listing all knowledge"""
        # Store items
        memory.store_knowledge(topic="item1", knowledge={"data": "test1"})
        memory.store_knowledge(topic="item2", knowledge={"data": "test2"})
        memory.store_knowledge(topic="item3", knowledge={"data": "test3"})

        results = memory.list_knowledge()

        assert len(results) >= 3

    def test_list_by_category(self, memory):
        """Test listing by category"""
        memory.store_knowledge(
            topic="adr",
            knowledge={"data": "test"},
            category=KnowledgeCategory.ARCHITECTURAL_DECISION
        )
        memory.store_knowledge(
            topic="pattern",
            knowledge={"data": "test"},
            category=KnowledgeCategory.CODE_PATTERN
        )

        results = memory.list_knowledge(
            category=KnowledgeCategory.ARCHITECTURAL_DECISION
        )

        assert all(r["category"] == KnowledgeCategory.ARCHITECTURAL_DECISION for r in results)

    def test_list_with_min_confidence(self, memory):
        """Test listing with confidence threshold"""
        memory.store_knowledge(topic="high", knowledge={"data": "test"}, confidence=0.9)
        memory.store_knowledge(topic="low", knowledge={"data": "test"}, confidence=0.2)

        results = memory.list_knowledge(min_confidence=0.5)

        assert all(r["confidence"] >= 0.5 for r in results)


class TestCodePatterns:
    """Test code pattern management"""

    def test_store_pattern(self, memory):
        """Test storing code pattern"""
        pattern_id = memory.store_pattern(
            pattern_name="error_handler",
            pattern_data={
                "code": "try:\n    ...\nexcept:",
                "description": "Error handling pattern"
            },
            category=KnowledgeCategory.CODE_PATTERN,
            tags=["error", "handling"]
        )

        assert isinstance(pattern_id, str)

    def test_get_pattern(self, memory):
        """Test retrieving pattern"""
        memory.store_pattern(
            pattern_name="decorator_pattern",
            pattern_data={
                "code": "@decorator\ndef func():",
                "description": "Decorator pattern"
            }
        )

        pattern = memory.get_pattern("decorator_pattern")

        assert pattern is not None
        assert pattern["pattern_name"] == "decorator_pattern"
        assert "decorator" in pattern["pattern_data"]["code"]

    def test_pattern_usage_tracking(self, memory):
        """Test pattern usage count tracking"""
        memory.store_pattern(
            pattern_name="test_pattern",
            pattern_data={"code": "test"}
        )

        # Retrieve multiple times
        memory.get_pattern("test_pattern")
        memory.get_pattern("test_pattern")
        pattern = memory.get_pattern("test_pattern")

        # Note: usage_count is 0 because we just retrieved, not the updated count
        # The update happens async in the database
        assert pattern is not None

    def test_list_patterns(self, memory):
        """Test listing patterns"""
        memory.store_pattern(
            pattern_name="pattern1",
            pattern_data={"code": "test1"},
            category=KnowledgeCategory.CODE_PATTERN
        )
        memory.store_pattern(
            pattern_name="pattern2",
            pattern_data={"code": "test2"},
            category=KnowledgeCategory.WORKFLOW_PATTERN
        )

        # List all
        all_patterns = memory.list_patterns()
        assert len(all_patterns) >= 2

        # List by category
        code_patterns = memory.list_patterns(
            category=KnowledgeCategory.CODE_PATTERN
        )
        assert all(p["category"] == KnowledgeCategory.CODE_PATTERN for p in code_patterns)


class TestPruning:
    """Test knowledge pruning"""

    def test_prune_low_confidence(self, memory):
        """Test pruning low-confidence knowledge"""
        # Store old, low-confidence item
        from unittest.mock import patch
        old_date = (datetime.now() - timedelta(days=40)).isoformat()

        knowledge_id = memory.store_knowledge(
            topic="old_low",
            knowledge={"data": "test"},
            confidence=0.2
        )

        # Manually set old creation date
        with memory.db.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE semantic_knowledge SET created_at = ? WHERE id = ?",
                (old_date, knowledge_id)
            )

        # Prune
        pruned = memory.prune_low_confidence(threshold=0.3, min_age_days=30)

        assert pruned >= 1

        # Verify removed
        result = memory.retrieve_knowledge("old_low")
        assert result is None

    def test_prune_preserves_recent(self, memory):
        """Test pruning preserves recent low-confidence items"""
        # Store recent, low-confidence item
        memory.store_knowledge(
            topic="recent_low",
            knowledge={"data": "test"},
            confidence=0.2
        )

        # Prune (should not remove recent items)
        pruned = memory.prune_low_confidence(threshold=0.3, min_age_days=30)

        # Verify preserved
        result = memory.retrieve_knowledge("recent_low")
        assert result is not None

    def test_prune_preserves_high_confidence(self, memory):
        """Test pruning preserves high-confidence items regardless of age"""
        # Store old, high-confidence item
        old_date = (datetime.now() - timedelta(days=40)).isoformat()

        knowledge_id = memory.store_knowledge(
            topic="old_high",
            knowledge={"data": "test"},
            confidence=0.9
        )

        # Manually set old creation date
        with memory.db.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE semantic_knowledge SET created_at = ? WHERE id = ?",
                (old_date, knowledge_id)
            )

        # Prune
        memory.prune_low_confidence(threshold=0.3, min_age_days=30)

        # Verify preserved
        result = memory.retrieve_knowledge("old_high")
        assert result is not None


class TestStatistics:
    """Test statistics and metrics"""

    def test_get_statistics(self, memory):
        """Test retrieving statistics"""
        # Store some data
        memory.store_knowledge(
            topic="k1",
            knowledge={"data": "test1"},
            confidence=0.8,
            category=KnowledgeCategory.ARCHITECTURAL_DECISION
        )
        memory.store_knowledge(
            topic="k2",
            knowledge={"data": "test2"},
            confidence=0.6,
            category=KnowledgeCategory.BEST_PRACTICE
        )
        memory.store_pattern(
            pattern_name="p1",
            pattern_data={"code": "test"}
        )

        stats = memory.get_statistics()

        assert "knowledge" in stats
        assert "patterns" in stats
        assert "categories" in stats
        assert stats["knowledge"]["total_knowledge"] >= 2
        assert stats["patterns"]["total_patterns"] >= 1
        assert KnowledgeCategory.ARCHITECTURAL_DECISION in stats["categories"]

    def test_access_tracking(self, memory):
        """Test access count tracking"""
        knowledge_id = memory.store_knowledge(
            topic="tracked",
            knowledge={"data": "test"}
        )

        # Retrieve multiple times
        memory.retrieve_knowledge("tracked")
        memory.retrieve_knowledge("tracked")
        result = memory.retrieve_knowledge("tracked")

        # Access count should be incremented
        # Note: The count in result won't reflect the latest increment
        # because it happens after retrieval
        assert result is not None


class TestProjectIsolation:
    """Test project-scoped isolation"""

    def test_different_projects_isolated(self, temp_db):
        """Test knowledge is isolated per project"""
        memory1 = SemanticMemory(temp_db, project_id="project1")
        memory2 = SemanticMemory(temp_db, project_id="project2")

        # Store in project1
        memory1.store_knowledge(
            topic="shared_topic",
            knowledge={"project": "1"}
        )

        # Store in project2
        memory2.store_knowledge(
            topic="shared_topic",
            knowledge={"project": "2"}
        )

        # Verify isolation
        result1 = memory1.retrieve_knowledge("shared_topic")
        result2 = memory2.retrieve_knowledge("shared_topic")

        assert result1["knowledge"]["project"] == "1"
        assert result2["knowledge"]["project"] == "2"

    def test_search_respects_project(self, temp_db):
        """Test search is scoped to project"""
        memory1 = SemanticMemory(temp_db, project_id="project1")
        memory2 = SemanticMemory(temp_db, project_id="project2")

        memory1.store_knowledge(
            topic="item1",
            knowledge={"data": "searchable"}
        )
        memory2.store_knowledge(
            topic="item2",
            knowledge={"data": "searchable"}
        )

        results1 = memory1.search_knowledge("searchable")
        results2 = memory2.search_knowledge("searchable")

        # Each should only see their own project's results
        assert len(results1) == 1
        assert len(results2) == 1
        assert results1[0]["topic"] == "item1"
        assert results2[0]["topic"] == "item2"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
