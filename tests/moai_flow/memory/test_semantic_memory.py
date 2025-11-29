"""
Comprehensive tests for SemanticMemory - Knowledge storage and pattern management.

Test Coverage Requirements:
- Framework: pytest with in-memory SwarmDB fixtures
- Coverage Target: 90%+ (per config)
- Test Database: Use :memory: SQLite for testing

Test Areas:
1. Knowledge storage and retrieval
2. Pattern management and learning
3. Confidence scoring and updates
4. Knowledge search and filtering
5. Category-based organization
6. Pruning low-confidence knowledge
7. Access count tracking
8. Knowledge updates and versioning
"""

import json
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from unittest.mock import Mock, patch

import pytest

from moai_flow.memory.swarm_db import SwarmDB


class SemanticMemory:
    """
    Long-term knowledge and pattern storage system.

    Features:
    - Knowledge storage with confidence scores
    - Pattern learning and matching
    - Category-based organization
    - Access tracking
    - Confidence-based pruning
    - Knowledge search
    """

    def __init__(self, db: SwarmDB, namespace: str = "semantic_memory"):
        """Initialize SemanticMemory with database."""
        self.db = db
        self.namespace = namespace

    def store_knowledge(
        self,
        key: str,
        content: Any,
        category: str,
        confidence: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Store knowledge with confidence score."""
        if not key:
            raise ValueError("Knowledge key cannot be empty")
        if not category:
            raise ValueError("Category cannot be empty")
        if not 0.0 <= confidence <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")

        knowledge_store = self.db.get(self.namespace, "knowledge") or {}

        knowledge_store[key] = {
            "content": content,
            "category": category,
            "confidence": confidence,
            "metadata": metadata or {},
            "access_count": 0,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }

        self.db.set(self.namespace, "knowledge", knowledge_store)

    def get_knowledge(self, key: str, increment_access: bool = True) -> Optional[Dict[str, Any]]:
        """Retrieve knowledge by key."""
        knowledge_store = self.db.get(self.namespace, "knowledge") or {}
        knowledge = knowledge_store.get(key)

        if knowledge and increment_access:
            knowledge["access_count"] += 1
            knowledge["last_accessed"] = datetime.now().isoformat()
            self.db.set(self.namespace, "knowledge", knowledge_store)

        return knowledge

    def update_knowledge(
        self,
        key: str,
        content: Optional[Any] = None,
        confidence: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Update existing knowledge."""
        knowledge_store = self.db.get(self.namespace, "knowledge") or {}

        if key not in knowledge_store:
            return False

        if content is not None:
            knowledge_store[key]["content"] = content

        if confidence is not None:
            if not 0.0 <= confidence <= 1.0:
                raise ValueError("Confidence must be between 0.0 and 1.0")
            knowledge_store[key]["confidence"] = confidence

        if metadata is not None:
            knowledge_store[key]["metadata"].update(metadata)

        knowledge_store[key]["updated_at"] = datetime.now().isoformat()
        self.db.set(self.namespace, "knowledge", knowledge_store)

        return True

    def delete_knowledge(self, key: str) -> bool:
        """Delete knowledge by key."""
        knowledge_store = self.db.get(self.namespace, "knowledge") or {}

        if key in knowledge_store:
            del knowledge_store[key]
            self.db.set(self.namespace, "knowledge", knowledge_store)
            return True

        return False

    def search_knowledge(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        min_confidence: float = 0.0
    ) -> List[Dict[str, Any]]:
        """Search knowledge by query, category, or confidence."""
        knowledge_store = self.db.get(self.namespace, "knowledge") or {}

        results = []
        for key, knowledge in knowledge_store.items():
            # Filter by confidence
            if knowledge["confidence"] < min_confidence:
                continue

            # Filter by category
            if category and knowledge["category"] != category:
                continue

            # Filter by query (simple substring match)
            if query:
                content_str = str(knowledge["content"]).lower()
                if query.lower() not in content_str and query.lower() not in key.lower():
                    continue

            results.append({
                "key": key,
                **knowledge
            })

        # Sort by confidence descending
        results.sort(key=lambda x: x["confidence"], reverse=True)
        return results

    def get_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get all knowledge in a category."""
        return self.search_knowledge(category=category)

    def get_categories(self) -> List[str]:
        """Get all unique categories."""
        knowledge_store = self.db.get(self.namespace, "knowledge") or {}
        categories = set(k["category"] for k in knowledge_store.values())
        return sorted(list(categories))

    def prune_low_confidence(self, threshold: float = 0.3) -> int:
        """Remove knowledge below confidence threshold."""
        knowledge_store = self.db.get(self.namespace, "knowledge") or {}

        keys_to_remove = [
            key for key, knowledge in knowledge_store.items()
            if knowledge["confidence"] < threshold
        ]

        for key in keys_to_remove:
            del knowledge_store[key]

        if keys_to_remove:
            self.db.set(self.namespace, "knowledge", knowledge_store)

        return len(keys_to_remove)

    def boost_confidence(self, key: str, boost: float = 0.1) -> bool:
        """Increase confidence score for knowledge."""
        knowledge_store = self.db.get(self.namespace, "knowledge") or {}

        if key not in knowledge_store:
            return False

        current = knowledge_store[key]["confidence"]
        new_confidence = min(1.0, current + boost)
        knowledge_store[key]["confidence"] = new_confidence
        knowledge_store[key]["updated_at"] = datetime.now().isoformat()

        self.db.set(self.namespace, "knowledge", knowledge_store)
        return True

    def decay_confidence(self, key: str, decay: float = 0.1) -> bool:
        """Decrease confidence score for knowledge."""
        knowledge_store = self.db.get(self.namespace, "knowledge") or {}

        if key not in knowledge_store:
            return False

        current = knowledge_store[key]["confidence"]
        new_confidence = max(0.0, current - decay)
        knowledge_store[key]["confidence"] = new_confidence
        knowledge_store[key]["updated_at"] = datetime.now().isoformat()

        self.db.set(self.namespace, "knowledge", knowledge_store)
        return True

    def get_most_accessed(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most frequently accessed knowledge."""
        knowledge_store = self.db.get(self.namespace, "knowledge") or {}

        knowledge_list = [
            {"key": key, **knowledge}
            for key, knowledge in knowledge_store.items()
        ]

        knowledge_list.sort(key=lambda x: x["access_count"], reverse=True)
        return knowledge_list[:limit]

    def store_pattern(
        self,
        pattern_id: str,
        pattern: Dict[str, Any],
        confidence: float = 1.0
    ) -> None:
        """Store learned pattern."""
        if not pattern_id:
            raise ValueError("Pattern ID cannot be empty")
        if not 0.0 <= confidence <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")

        patterns = self.db.get(self.namespace, "patterns") or {}

        patterns[pattern_id] = {
            "pattern": pattern,
            "confidence": confidence,
            "match_count": 0,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }

        self.db.set(self.namespace, "patterns", patterns)

    def get_pattern(self, pattern_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve pattern by ID."""
        patterns = self.db.get(self.namespace, "patterns") or {}
        return patterns.get(pattern_id)

    def match_pattern(self, pattern_id: str) -> bool:
        """Record pattern match (increases confidence)."""
        patterns = self.db.get(self.namespace, "patterns") or {}

        if pattern_id not in patterns:
            return False

        patterns[pattern_id]["match_count"] += 1
        current_confidence = patterns[pattern_id]["confidence"]
        patterns[pattern_id]["confidence"] = min(1.0, current_confidence + 0.05)
        patterns[pattern_id]["updated_at"] = datetime.now().isoformat()

        self.db.set(self.namespace, "patterns", patterns)
        return True

    def get_patterns(self, min_confidence: float = 0.0) -> List[Dict[str, Any]]:
        """Get all patterns above confidence threshold."""
        patterns = self.db.get(self.namespace, "patterns") or {}

        pattern_list = [
            {"pattern_id": pattern_id, **pattern_data}
            for pattern_id, pattern_data in patterns.items()
            if pattern_data["confidence"] >= min_confidence
        ]

        pattern_list.sort(key=lambda x: x["confidence"], reverse=True)
        return pattern_list

    def get_statistics(self) -> Dict[str, Any]:
        """Get semantic memory statistics."""
        knowledge_store = self.db.get(self.namespace, "knowledge") or {}
        patterns = self.db.get(self.namespace, "patterns") or {}

        if not knowledge_store:
            return {
                "total_knowledge": 0,
                "total_patterns": len(patterns),
                "categories": [],
                "avg_confidence": 0.0,
                "total_accesses": 0
            }

        confidences = [k["confidence"] for k in knowledge_store.values()]
        accesses = [k["access_count"] for k in knowledge_store.values()]

        return {
            "total_knowledge": len(knowledge_store),
            "total_patterns": len(patterns),
            "categories": self.get_categories(),
            "avg_confidence": sum(confidences) / len(confidences),
            "total_accesses": sum(accesses),
            "high_confidence_count": sum(1 for c in confidences if c >= 0.8),
            "low_confidence_count": sum(1 for c in confidences if c < 0.5)
        }


@pytest.fixture
def memory_db():
    """Create in-memory SwarmDB for testing."""
    return SwarmDB(db_path=":memory:")


@pytest.fixture
def semantic_memory(memory_db):
    """Create SemanticMemory instance for testing."""
    return SemanticMemory(memory_db)


class TestSemanticMemoryInitialization:
    """Test suite for SemanticMemory initialization."""

    def test_initialization(self, memory_db):
        """Test SemanticMemory initialization."""
        memory = SemanticMemory(memory_db, namespace="test_namespace")

        assert memory.db is memory_db
        assert memory.namespace == "test_namespace"

    def test_default_namespace(self, memory_db):
        """Test default namespace."""
        memory = SemanticMemory(memory_db)

        assert memory.namespace == "semantic_memory"


class TestKnowledgeStorage:
    """Test suite for knowledge storage operations."""

    def test_store_knowledge(self, semantic_memory):
        """Test storing knowledge."""
        semantic_memory.store_knowledge(
            key="python_best_practice",
            content="Use list comprehensions for simple transformations",
            category="programming",
            confidence=0.9
        )

        knowledge = semantic_memory.get_knowledge("python_best_practice", increment_access=False)

        assert knowledge is not None
        assert knowledge["content"] == "Use list comprehensions for simple transformations"
        assert knowledge["category"] == "programming"
        assert knowledge["confidence"] == 0.9

    def test_store_complex_knowledge(self, semantic_memory):
        """Test storing complex nested knowledge."""
        complex_data = {
            "concept": "SOLID principles",
            "details": {
                "S": "Single Responsibility",
                "O": "Open/Closed",
                "L": "Liskov Substitution"
            }
        }

        semantic_memory.store_knowledge(
            key="solid",
            content=complex_data,
            category="architecture",
            metadata={"source": "design_patterns"}
        )

        knowledge = semantic_memory.get_knowledge("solid", increment_access=False)

        assert knowledge["content"]["details"]["S"] == "Single Responsibility"
        assert knowledge["metadata"]["source"] == "design_patterns"

    def test_store_empty_key_raises_error(self, semantic_memory):
        """Test that empty key raises ValueError."""
        with pytest.raises(ValueError, match="Knowledge key cannot be empty"):
            semantic_memory.store_knowledge("", "content", "category")

    def test_store_empty_category_raises_error(self, semantic_memory):
        """Test that empty category raises ValueError."""
        with pytest.raises(ValueError, match="Category cannot be empty"):
            semantic_memory.store_knowledge("key", "content", "")

    def test_store_invalid_confidence_raises_error(self, semantic_memory):
        """Test that invalid confidence raises ValueError."""
        with pytest.raises(ValueError, match="Confidence must be between 0.0 and 1.0"):
            semantic_memory.store_knowledge("key", "content", "cat", confidence=1.5)

    def test_store_negative_confidence_raises_error(self, semantic_memory):
        """Test that negative confidence raises ValueError."""
        with pytest.raises(ValueError, match="Confidence must be between 0.0 and 1.0"):
            semantic_memory.store_knowledge("key", "content", "cat", confidence=-0.1)

    def test_store_default_confidence(self, semantic_memory):
        """Test storing knowledge with default confidence."""
        semantic_memory.store_knowledge("key", "content", "category")

        knowledge = semantic_memory.get_knowledge("key", increment_access=False)

        assert knowledge["confidence"] == 1.0


class TestKnowledgeRetrieval:
    """Test suite for knowledge retrieval."""

    def test_get_knowledge(self, semantic_memory):
        """Test retrieving knowledge."""
        semantic_memory.store_knowledge("test_key", "test_content", "test_cat")

        knowledge = semantic_memory.get_knowledge("test_key", increment_access=False)

        assert knowledge is not None
        assert knowledge["content"] == "test_content"

    def test_get_nonexistent_knowledge(self, semantic_memory):
        """Test retrieving non-existent knowledge returns None."""
        knowledge = semantic_memory.get_knowledge("nonexistent")

        assert knowledge is None

    def test_get_knowledge_increments_access_count(self, semantic_memory):
        """Test that getting knowledge increments access count."""
        semantic_memory.store_knowledge("key", "content", "cat")

        knowledge1 = semantic_memory.get_knowledge("key")
        knowledge2 = semantic_memory.get_knowledge("key")

        assert knowledge2["access_count"] == 2

    def test_get_knowledge_without_increment(self, semantic_memory):
        """Test getting knowledge without incrementing access count."""
        semantic_memory.store_knowledge("key", "content", "cat")

        knowledge1 = semantic_memory.get_knowledge("key", increment_access=False)
        knowledge2 = semantic_memory.get_knowledge("key", increment_access=False)

        assert knowledge2["access_count"] == 0


class TestKnowledgeUpdates:
    """Test suite for knowledge updates."""

    def test_update_knowledge_content(self, semantic_memory):
        """Test updating knowledge content."""
        semantic_memory.store_knowledge("key", "old_content", "cat")

        success = semantic_memory.update_knowledge("key", content="new_content")

        assert success is True
        knowledge = semantic_memory.get_knowledge("key", increment_access=False)
        assert knowledge["content"] == "new_content"

    def test_update_knowledge_confidence(self, semantic_memory):
        """Test updating knowledge confidence."""
        semantic_memory.store_knowledge("key", "content", "cat", confidence=0.5)

        success = semantic_memory.update_knowledge("key", confidence=0.9)

        assert success is True
        knowledge = semantic_memory.get_knowledge("key", increment_access=False)
        assert knowledge["confidence"] == 0.9

    def test_update_knowledge_metadata(self, semantic_memory):
        """Test updating knowledge metadata."""
        semantic_memory.store_knowledge("key", "content", "cat", metadata={"v": 1})

        success = semantic_memory.update_knowledge("key", metadata={"v": 2, "new": "field"})

        assert success is True
        knowledge = semantic_memory.get_knowledge("key", increment_access=False)
        assert knowledge["metadata"]["v"] == 2
        assert knowledge["metadata"]["new"] == "field"

    def test_update_nonexistent_knowledge_returns_false(self, semantic_memory):
        """Test updating non-existent knowledge returns False."""
        success = semantic_memory.update_knowledge("nonexistent", content="new")

        assert success is False

    def test_update_invalid_confidence_raises_error(self, semantic_memory):
        """Test that invalid confidence update raises ValueError."""
        semantic_memory.store_knowledge("key", "content", "cat")

        with pytest.raises(ValueError, match="Confidence must be between 0.0 and 1.0"):
            semantic_memory.update_knowledge("key", confidence=2.0)


class TestKnowledgeDeletion:
    """Test suite for knowledge deletion."""

    def test_delete_knowledge(self, semantic_memory):
        """Test deleting knowledge."""
        semantic_memory.store_knowledge("key", "content", "cat")

        success = semantic_memory.delete_knowledge("key")

        assert success is True
        assert semantic_memory.get_knowledge("key") is None

    def test_delete_nonexistent_knowledge_returns_false(self, semantic_memory):
        """Test deleting non-existent knowledge returns False."""
        success = semantic_memory.delete_knowledge("nonexistent")

        assert success is False


class TestKnowledgeSearch:
    """Test suite for knowledge search."""

    def test_search_by_query(self, semantic_memory):
        """Test searching knowledge by query."""
        semantic_memory.store_knowledge("k1", "Python is great", "lang")
        semantic_memory.store_knowledge("k2", "JavaScript is awesome", "lang")
        semantic_memory.store_knowledge("k3", "Python for data science", "lang")

        results = semantic_memory.search_knowledge(query="Python")

        assert len(results) == 2
        assert all("python" in r["content"].lower() or "python" in r["key"].lower() for r in results)

    def test_search_by_category(self, semantic_memory):
        """Test searching knowledge by category."""
        semantic_memory.store_knowledge("k1", "content1", "cat_a")
        semantic_memory.store_knowledge("k2", "content2", "cat_b")
        semantic_memory.store_knowledge("k3", "content3", "cat_a")

        results = semantic_memory.search_knowledge(category="cat_a")

        assert len(results) == 2
        assert all(r["category"] == "cat_a" for r in results)

    def test_search_by_min_confidence(self, semantic_memory):
        """Test searching knowledge by minimum confidence."""
        semantic_memory.store_knowledge("k1", "c1", "cat", confidence=0.9)
        semantic_memory.store_knowledge("k2", "c2", "cat", confidence=0.5)
        semantic_memory.store_knowledge("k3", "c3", "cat", confidence=0.3)

        results = semantic_memory.search_knowledge(min_confidence=0.6)

        assert len(results) == 1
        assert results[0]["key"] == "k1"

    def test_search_combined_filters(self, semantic_memory):
        """Test searching with combined filters."""
        semantic_memory.store_knowledge("k1", "Python data", "lang", confidence=0.9)
        semantic_memory.store_knowledge("k2", "Python web", "lang", confidence=0.4)
        semantic_memory.store_knowledge("k3", "JavaScript web", "lang", confidence=0.9)

        results = semantic_memory.search_knowledge(
            query="Python",
            category="lang",
            min_confidence=0.5
        )

        assert len(results) == 1
        assert results[0]["key"] == "k1"

    def test_search_returns_sorted_by_confidence(self, semantic_memory):
        """Test that search results are sorted by confidence."""
        semantic_memory.store_knowledge("k1", "content", "cat", confidence=0.5)
        semantic_memory.store_knowledge("k2", "content", "cat", confidence=0.9)
        semantic_memory.store_knowledge("k3", "content", "cat", confidence=0.7)

        results = semantic_memory.search_knowledge()

        assert results[0]["confidence"] == 0.9
        assert results[1]["confidence"] == 0.7
        assert results[2]["confidence"] == 0.5


class TestCategoryManagement:
    """Test suite for category management."""

    def test_get_by_category(self, semantic_memory):
        """Test getting all knowledge in a category."""
        semantic_memory.store_knowledge("k1", "c1", "programming")
        semantic_memory.store_knowledge("k2", "c2", "architecture")
        semantic_memory.store_knowledge("k3", "c3", "programming")

        results = semantic_memory.get_by_category("programming")

        assert len(results) == 2

    def test_get_categories(self, semantic_memory):
        """Test getting all unique categories."""
        semantic_memory.store_knowledge("k1", "c1", "cat_a")
        semantic_memory.store_knowledge("k2", "c2", "cat_b")
        semantic_memory.store_knowledge("k3", "c3", "cat_a")
        semantic_memory.store_knowledge("k4", "c4", "cat_c")

        categories = semantic_memory.get_categories()

        assert len(categories) == 3
        assert "cat_a" in categories
        assert "cat_b" in categories
        assert "cat_c" in categories

    def test_get_categories_sorted(self, semantic_memory):
        """Test that categories are returned sorted."""
        semantic_memory.store_knowledge("k1", "c1", "zebra")
        semantic_memory.store_knowledge("k2", "c2", "apple")
        semantic_memory.store_knowledge("k3", "c3", "monkey")

        categories = semantic_memory.get_categories()

        assert categories == ["apple", "monkey", "zebra"]


class TestConfidenceManagement:
    """Test suite for confidence management."""

    def test_prune_low_confidence(self, semantic_memory):
        """Test pruning low confidence knowledge."""
        semantic_memory.store_knowledge("k1", "c1", "cat", confidence=0.9)
        semantic_memory.store_knowledge("k2", "c2", "cat", confidence=0.2)
        semantic_memory.store_knowledge("k3", "c3", "cat", confidence=0.1)

        removed = semantic_memory.prune_low_confidence(threshold=0.3)

        assert removed == 2
        assert semantic_memory.get_knowledge("k1") is not None
        assert semantic_memory.get_knowledge("k2") is None
        assert semantic_memory.get_knowledge("k3") is None

    def test_boost_confidence(self, semantic_memory):
        """Test boosting confidence score."""
        semantic_memory.store_knowledge("key", "content", "cat", confidence=0.5)

        success = semantic_memory.boost_confidence("key", boost=0.2)

        assert success is True
        knowledge = semantic_memory.get_knowledge("key", increment_access=False)
        assert knowledge["confidence"] == 0.7

    def test_boost_confidence_caps_at_one(self, semantic_memory):
        """Test that boosting confidence caps at 1.0."""
        semantic_memory.store_knowledge("key", "content", "cat", confidence=0.95)

        semantic_memory.boost_confidence("key", boost=0.2)

        knowledge = semantic_memory.get_knowledge("key", increment_access=False)
        assert knowledge["confidence"] == 1.0

    def test_decay_confidence(self, semantic_memory):
        """Test decaying confidence score."""
        semantic_memory.store_knowledge("key", "content", "cat", confidence=0.8)

        success = semantic_memory.decay_confidence("key", decay=0.3)

        assert success is True
        knowledge = semantic_memory.get_knowledge("key", increment_access=False)
        assert knowledge["confidence"] == 0.5

    def test_decay_confidence_floors_at_zero(self, semantic_memory):
        """Test that decaying confidence floors at 0.0."""
        semantic_memory.store_knowledge("key", "content", "cat", confidence=0.1)

        semantic_memory.decay_confidence("key", decay=0.2)

        knowledge = semantic_memory.get_knowledge("key", increment_access=False)
        assert knowledge["confidence"] == 0.0

    def test_boost_nonexistent_returns_false(self, semantic_memory):
        """Test boosting non-existent knowledge returns False."""
        success = semantic_memory.boost_confidence("nonexistent")

        assert success is False

    def test_decay_nonexistent_returns_false(self, semantic_memory):
        """Test decaying non-existent knowledge returns False."""
        success = semantic_memory.decay_confidence("nonexistent")

        assert success is False


class TestAccessTracking:
    """Test suite for access tracking."""

    def test_get_most_accessed(self, semantic_memory):
        """Test getting most accessed knowledge."""
        semantic_memory.store_knowledge("k1", "c1", "cat")
        semantic_memory.store_knowledge("k2", "c2", "cat")
        semantic_memory.store_knowledge("k3", "c3", "cat")

        # Access k2 three times, k1 once
        semantic_memory.get_knowledge("k2")
        semantic_memory.get_knowledge("k2")
        semantic_memory.get_knowledge("k2")
        semantic_memory.get_knowledge("k1")

        most_accessed = semantic_memory.get_most_accessed()

        assert most_accessed[0]["key"] == "k2"
        assert most_accessed[0]["access_count"] == 3
        assert most_accessed[1]["key"] == "k1"
        assert most_accessed[1]["access_count"] == 1

    def test_get_most_accessed_with_limit(self, semantic_memory):
        """Test getting most accessed with limit."""
        for i in range(10):
            semantic_memory.store_knowledge(f"k{i}", "content", "cat")
            for _ in range(i):
                semantic_memory.get_knowledge(f"k{i}")

        most_accessed = semantic_memory.get_most_accessed(limit=3)

        assert len(most_accessed) == 3
        assert most_accessed[0]["key"] == "k9"


class TestPatternManagement:
    """Test suite for pattern management."""

    def test_store_pattern(self, semantic_memory):
        """Test storing pattern."""
        pattern = {"type": "code_smell", "indicators": ["long_method", "god_class"]}

        semantic_memory.store_pattern("smell_001", pattern, confidence=0.8)

        stored = semantic_memory.get_pattern("smell_001")

        assert stored is not None
        assert stored["pattern"] == pattern
        assert stored["confidence"] == 0.8

    def test_get_nonexistent_pattern(self, semantic_memory):
        """Test getting non-existent pattern returns None."""
        pattern = semantic_memory.get_pattern("nonexistent")

        assert pattern is None

    def test_match_pattern_increases_confidence(self, semantic_memory):
        """Test that matching pattern increases confidence."""
        semantic_memory.store_pattern("p1", {"type": "test"}, confidence=0.5)

        semantic_memory.match_pattern("p1")

        pattern = semantic_memory.get_pattern("p1")
        assert pattern["confidence"] == 0.55
        assert pattern["match_count"] == 1

    def test_match_pattern_multiple_times(self, semantic_memory):
        """Test matching pattern multiple times."""
        semantic_memory.store_pattern("p1", {"type": "test"}, confidence=0.5)

        for _ in range(5):
            semantic_memory.match_pattern("p1")

        pattern = semantic_memory.get_pattern("p1")
        assert pattern["match_count"] == 5
        assert pattern["confidence"] == 0.75  # 0.5 + (5 * 0.05)

    def test_match_pattern_caps_confidence_at_one(self, semantic_memory):
        """Test that pattern confidence caps at 1.0."""
        semantic_memory.store_pattern("p1", {"type": "test"}, confidence=0.95)

        for _ in range(10):
            semantic_memory.match_pattern("p1")

        pattern = semantic_memory.get_pattern("p1")
        assert pattern["confidence"] == 1.0

    def test_match_nonexistent_pattern_returns_false(self, semantic_memory):
        """Test matching non-existent pattern returns False."""
        success = semantic_memory.match_pattern("nonexistent")

        assert success is False

    def test_get_patterns(self, semantic_memory):
        """Test getting all patterns."""
        semantic_memory.store_pattern("p1", {"type": "a"}, confidence=0.9)
        semantic_memory.store_pattern("p2", {"type": "b"}, confidence=0.5)
        semantic_memory.store_pattern("p3", {"type": "c"}, confidence=0.7)

        patterns = semantic_memory.get_patterns()

        assert len(patterns) == 3

    def test_get_patterns_with_min_confidence(self, semantic_memory):
        """Test getting patterns with minimum confidence."""
        semantic_memory.store_pattern("p1", {"type": "a"}, confidence=0.9)
        semantic_memory.store_pattern("p2", {"type": "b"}, confidence=0.5)
        semantic_memory.store_pattern("p3", {"type": "c"}, confidence=0.3)

        patterns = semantic_memory.get_patterns(min_confidence=0.6)

        assert len(patterns) == 1
        assert patterns[0]["pattern_id"] == "p1"

    def test_get_patterns_sorted_by_confidence(self, semantic_memory):
        """Test that patterns are sorted by confidence."""
        semantic_memory.store_pattern("p1", {"type": "a"}, confidence=0.5)
        semantic_memory.store_pattern("p2", {"type": "b"}, confidence=0.9)
        semantic_memory.store_pattern("p3", {"type": "c"}, confidence=0.7)

        patterns = semantic_memory.get_patterns()

        assert patterns[0]["confidence"] == 0.9
        assert patterns[1]["confidence"] == 0.7
        assert patterns[2]["confidence"] == 0.5


class TestStatistics:
    """Test suite for statistics."""

    def test_get_statistics(self, semantic_memory):
        """Test getting comprehensive statistics."""
        semantic_memory.store_knowledge("k1", "c1", "cat_a", confidence=0.9)
        semantic_memory.store_knowledge("k2", "c2", "cat_b", confidence=0.5)
        semantic_memory.store_knowledge("k3", "c3", "cat_a", confidence=0.3)

        semantic_memory.get_knowledge("k1")
        semantic_memory.get_knowledge("k2")

        stats = semantic_memory.get_statistics()

        assert stats["total_knowledge"] == 3
        assert stats["avg_confidence"] == pytest.approx(0.5667, rel=0.01)
        assert stats["total_accesses"] == 2
        assert stats["high_confidence_count"] == 1
        assert stats["low_confidence_count"] == 2

    def test_get_statistics_empty(self, semantic_memory):
        """Test statistics with empty memory."""
        stats = semantic_memory.get_statistics()

        assert stats["total_knowledge"] == 0
        assert stats["avg_confidence"] == 0.0
        assert stats["total_accesses"] == 0


class TestEdgeCases:
    """Test suite for edge cases."""

    def test_unicode_in_knowledge(self, semantic_memory):
        """Test unicode support in knowledge."""
        semantic_memory.store_knowledge("unicode", "안녕하세요 🚀", "greetings")

        knowledge = semantic_memory.get_knowledge("unicode", increment_access=False)

        assert knowledge["content"] == "안녕하세요 🚀"

    def test_large_knowledge_content(self, semantic_memory):
        """Test storing large knowledge content."""
        large_content = "x" * 100000

        semantic_memory.store_knowledge("large", large_content, "test")

        knowledge = semantic_memory.get_knowledge("large", increment_access=False)

        assert len(knowledge["content"]) == 100000

    def test_special_characters_in_keys(self, semantic_memory):
        """Test special characters in keys."""
        semantic_memory.store_knowledge("key:with:colons/and/slashes", "content", "cat")

        knowledge = semantic_memory.get_knowledge("key:with:colons/and/slashes", increment_access=False)

        assert knowledge is not None
