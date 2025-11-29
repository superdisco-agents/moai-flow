#!/usr/bin/env python3
"""
SemanticMemory - Long-term Knowledge and Pattern Storage

Stores and retrieves:
- Learned patterns and best practices
- Project-specific conventions
- Architectural decisions (ADRs)
- Reusable code patterns
- Error resolution strategies

Features:
- Confidence-based scoring (0.0 - 1.0)
- Automatic knowledge pruning
- Category-based organization
- Full-text search support
- Access tracking and metrics

Schema Version: 1.0.0
"""

import json
import logging
import uuid
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .swarm_db import SwarmDB


# ============================================================================
# Knowledge Categories
# ============================================================================

class KnowledgeCategory(str, Enum):
    """Knowledge categories for semantic memory"""
    ARCHITECTURAL_DECISION = "adr"
    BEST_PRACTICE = "best_practice"
    CODE_PATTERN = "code_pattern"
    ERROR_RESOLUTION = "error_resolution"
    WORKFLOW_PATTERN = "workflow"
    CONVENTION = "convention"
    TOOL_USAGE = "tool_usage"
    PERFORMANCE_PATTERN = "performance"


# ============================================================================
# Schema Extension for Semantic Memory
# ============================================================================

SEMANTIC_MEMORY_SCHEMA = [
    # Semantic knowledge storage
    """
    CREATE TABLE IF NOT EXISTS semantic_knowledge (
        id TEXT PRIMARY KEY,
        project_id TEXT NOT NULL,
        topic TEXT NOT NULL,
        category TEXT NOT NULL,
        knowledge TEXT NOT NULL,
        confidence REAL DEFAULT 0.5,
        access_count INTEGER DEFAULT 0,
        success_count INTEGER DEFAULT 0,
        failure_count INTEGER DEFAULT 0,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        last_accessed_at TEXT,
        tags TEXT
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_semantic_knowledge_project_id ON semantic_knowledge(project_id)",
    "CREATE INDEX IF NOT EXISTS idx_semantic_knowledge_topic ON semantic_knowledge(topic)",
    "CREATE INDEX IF NOT EXISTS idx_semantic_knowledge_category ON semantic_knowledge(category)",
    "CREATE INDEX IF NOT EXISTS idx_semantic_knowledge_confidence ON semantic_knowledge(confidence)",

    # Code patterns storage
    """
    CREATE TABLE IF NOT EXISTS code_patterns (
        id TEXT PRIMARY KEY,
        project_id TEXT NOT NULL,
        pattern_name TEXT NOT NULL UNIQUE,
        category TEXT NOT NULL,
        pattern_data TEXT NOT NULL,
        usage_count INTEGER DEFAULT 0,
        confidence REAL DEFAULT 0.5,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        tags TEXT
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_code_patterns_project_id ON code_patterns(project_id)",
    "CREATE INDEX IF NOT EXISTS idx_code_patterns_pattern_name ON code_patterns(pattern_name)",
    "CREATE INDEX IF NOT EXISTS idx_code_patterns_category ON code_patterns(category)",
]


# ============================================================================
# SemanticMemory Implementation
# ============================================================================

class SemanticMemory:
    """
    Long-term knowledge and pattern storage for MoAI agents.

    Manages:
    - Learned patterns and best practices
    - Project-specific conventions
    - Architectural decisions (ADRs)
    - Reusable code patterns
    - Error resolution strategies

    Confidence Scoring:
    - New knowledge starts at 0.5
    - Successful use: +0.1 (max 1.0)
    - Failed use: -0.2 (min 0.0)
    - Knowledge below 0.3 pruned after 30 days

    Example:
        >>> memory = SemanticMemory(swarm_db, project_id="moai-adk")
        >>> memory.store_knowledge("api_design", {
        ...     "pattern": "RESTful",
        ...     "rationale": "Industry standard"
        ... }, confidence=0.9)
        >>> results = memory.search_knowledge("authentication")
    """

    def __init__(self, swarm_db: SwarmDB, project_id: str):
        """
        Initialize SemanticMemory

        Args:
            swarm_db: SwarmDB instance for persistent storage
            project_id: Project identifier for scoped memory
        """
        self.db = swarm_db
        self.project_id = project_id
        self.logger = logging.getLogger(__name__)

        # Initialize semantic memory schema
        self._initialize_schema()

    def _initialize_schema(self) -> None:
        """Initialize semantic memory schema extension"""
        try:
            with self.db.transaction() as conn:
                cursor = conn.cursor()

                # Execute schema statements
                for statement in SEMANTIC_MEMORY_SCHEMA:
                    statement = statement.strip()
                    if statement:
                        cursor.execute(statement)

                self.logger.info("Initialized SemanticMemory schema")

        except Exception as e:
            self.logger.error(f"Failed to initialize SemanticMemory schema: {e}")
            raise

    # ========================================================================
    # Knowledge Storage & Retrieval
    # ========================================================================

    def store_knowledge(
        self,
        topic: str,
        knowledge: Dict[str, Any],
        confidence: float = 0.5,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> str:
        """
        Store knowledge with confidence scoring

        Args:
            topic: Knowledge topic/identifier
            knowledge: Knowledge data dictionary
            confidence: Initial confidence score (0.0 - 1.0)
            category: Knowledge category (defaults to BEST_PRACTICE)
            tags: Optional tags for classification

        Returns:
            Knowledge ID

        Example:
            >>> memory.store_knowledge(
            ...     topic="jwt_authentication",
            ...     knowledge={
            ...         "decision": "Use JWT with refresh tokens",
            ...         "rationale": "Stateless, scalable",
            ...         "alternatives": ["Session-based", "OAuth2"]
            ...     },
            ...     confidence=0.9,
            ...     category="adr"
            ... )
        """
        # Validate confidence
        confidence = max(0.0, min(1.0, confidence))

        knowledge_id = str(uuid.uuid4())
        category = category or KnowledgeCategory.BEST_PRACTICE
        tags_json = json.dumps(tags or [])
        now = datetime.now().isoformat()

        with self.db.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO semantic_knowledge
                (id, project_id, topic, category, knowledge, confidence,
                 created_at, updated_at, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    knowledge_id,
                    self.project_id,
                    topic,
                    category,
                    json.dumps(knowledge),
                    confidence,
                    now,
                    now,
                    tags_json
                )
            )

        self.logger.info(
            f"Stored knowledge: {topic} (confidence={confidence:.2f})"
        )
        return knowledge_id

    def retrieve_knowledge(self, topic: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve knowledge by exact topic match

        Args:
            topic: Knowledge topic to retrieve

        Returns:
            Knowledge dictionary with metadata, or None if not found

        Example:
            >>> knowledge = memory.retrieve_knowledge("jwt_authentication")
            >>> if knowledge:
            ...     print(knowledge["confidence"])
        """
        conn = self.db._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT * FROM semantic_knowledge
            WHERE project_id = ? AND topic = ?
            ORDER BY confidence DESC, updated_at DESC
            LIMIT 1
            """,
            (self.project_id, topic)
        )

        row = cursor.fetchone()
        if row:
            knowledge = dict(row)
            knowledge["knowledge"] = json.loads(knowledge["knowledge"])
            knowledge["tags"] = json.loads(knowledge.get("tags", "[]"))

            # Update access tracking
            self._track_access(knowledge["id"])

            return knowledge

        return None

    def search_knowledge(
        self,
        query: str,
        limit: int = 10,
        min_confidence: float = 0.3,
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search across all knowledge using pattern matching

        Args:
            query: Search query string
            limit: Maximum results to return
            min_confidence: Minimum confidence threshold
            category: Optional category filter

        Returns:
            List of matching knowledge dictionaries, sorted by relevance

        Example:
            >>> results = memory.search_knowledge(
            ...     query="authentication security",
            ...     min_confidence=0.5,
            ...     category="adr"
            ... )
            >>> for result in results:
            ...     print(f"{result['topic']}: {result['confidence']}")
        """
        conn = self.db._get_connection()
        cursor = conn.cursor()

        # Build LIKE pattern for search
        search_pattern = f"%{query}%"

        # Build query with LIKE search across topic, knowledge, and tags
        sql = """
            SELECT * FROM semantic_knowledge
            WHERE project_id = ?
            AND confidence >= ?
            AND (
                topic LIKE ?
                OR knowledge LIKE ?
                OR tags LIKE ?
            )
        """
        params = [
            self.project_id,
            min_confidence,
            search_pattern,
            search_pattern,
            search_pattern
        ]

        if category:
            sql += " AND category = ?"
            params.append(category)

        sql += " ORDER BY confidence DESC, updated_at DESC LIMIT ?"
        params.append(limit)

        cursor.execute(sql, params)

        results = []
        for row in cursor.fetchall():
            knowledge = dict(row)
            knowledge["knowledge"] = json.loads(knowledge["knowledge"])
            knowledge["tags"] = json.loads(knowledge.get("tags", "[]"))
            results.append(knowledge)

        self.logger.debug(
            f"Search '{query}' returned {len(results)} results"
        )
        return results

    def list_knowledge(
        self,
        category: Optional[str] = None,
        min_confidence: float = 0.0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        List all knowledge, optionally filtered by category

        Args:
            category: Optional category filter
            min_confidence: Minimum confidence threshold
            limit: Maximum results to return

        Returns:
            List of knowledge dictionaries
        """
        conn = self.db._get_connection()
        cursor = conn.cursor()

        query = """
            SELECT * FROM semantic_knowledge
            WHERE project_id = ? AND confidence >= ?
        """
        params = [self.project_id, min_confidence]

        if category:
            query += " AND category = ?"
            params.append(category)

        query += " ORDER BY confidence DESC, updated_at DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)

        results = []
        for row in cursor.fetchall():
            knowledge = dict(row)
            knowledge["knowledge"] = json.loads(knowledge["knowledge"])
            knowledge["tags"] = json.loads(knowledge.get("tags", "[]"))
            results.append(knowledge)

        return results

    def update_knowledge(
        self,
        knowledge_id: str,
        knowledge: Optional[Dict[str, Any]] = None,
        confidence: Optional[float] = None,
        tags: Optional[List[str]] = None
    ) -> bool:
        """
        Update existing knowledge

        Args:
            knowledge_id: Knowledge ID to update
            knowledge: Optional new knowledge data
            confidence: Optional new confidence score
            tags: Optional new tags

        Returns:
            True if updated, False if not found
        """
        updates = []
        params = []

        if knowledge is not None:
            updates.append("knowledge = ?")
            params.append(json.dumps(knowledge))

        if confidence is not None:
            updates.append("confidence = ?")
            params.append(max(0.0, min(1.0, confidence)))

        if tags is not None:
            updates.append("tags = ?")
            params.append(json.dumps(tags))

        if not updates:
            return False

        updates.append("updated_at = ?")
        params.append(datetime.now().isoformat())
        params.append(knowledge_id)

        with self.db.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"""
                UPDATE semantic_knowledge
                SET {', '.join(updates)}
                WHERE id = ?
                """,
                params
            )

            return cursor.rowcount > 0

    # ========================================================================
    # Confidence Management
    # ========================================================================

    def update_confidence(
        self,
        knowledge_id: str,
        new_confidence: float
    ) -> None:
        """
        Update confidence score for knowledge

        Args:
            knowledge_id: Knowledge ID
            new_confidence: New confidence score (0.0 - 1.0)
        """
        new_confidence = max(0.0, min(1.0, new_confidence))

        with self.db.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE semantic_knowledge
                SET confidence = ?, updated_at = ?
                WHERE id = ?
                """,
                (new_confidence, datetime.now().isoformat(), knowledge_id)
            )

        self.logger.debug(
            f"Updated confidence: {knowledge_id} -> {new_confidence:.2f}"
        )

    def record_success(self, knowledge_id: str) -> None:
        """
        Record successful use of knowledge (increases confidence)

        Args:
            knowledge_id: Knowledge ID
        """
        with self.db.transaction() as conn:
            cursor = conn.cursor()

            # Get current confidence
            cursor.execute(
                "SELECT confidence FROM semantic_knowledge WHERE id = ?",
                (knowledge_id,)
            )
            row = cursor.fetchone()
            if not row:
                return

            current_confidence = row["confidence"]
            new_confidence = min(1.0, current_confidence + 0.1)

            cursor.execute(
                """
                UPDATE semantic_knowledge
                SET confidence = ?,
                    success_count = success_count + 1,
                    updated_at = ?
                WHERE id = ?
                """,
                (new_confidence, datetime.now().isoformat(), knowledge_id)
            )

        self.logger.debug(
            f"Recorded success: {knowledge_id} "
            f"({current_confidence:.2f} -> {new_confidence:.2f})"
        )

    def record_failure(self, knowledge_id: str) -> None:
        """
        Record failed use of knowledge (decreases confidence)

        Args:
            knowledge_id: Knowledge ID
        """
        with self.db.transaction() as conn:
            cursor = conn.cursor()

            # Get current confidence
            cursor.execute(
                "SELECT confidence FROM semantic_knowledge WHERE id = ?",
                (knowledge_id,)
            )
            row = cursor.fetchone()
            if not row:
                return

            current_confidence = row["confidence"]
            new_confidence = max(0.0, current_confidence - 0.2)

            cursor.execute(
                """
                UPDATE semantic_knowledge
                SET confidence = ?,
                    failure_count = failure_count + 1,
                    updated_at = ?
                WHERE id = ?
                """,
                (new_confidence, datetime.now().isoformat(), knowledge_id)
            )

        self.logger.debug(
            f"Recorded failure: {knowledge_id} "
            f"({current_confidence:.2f} -> {new_confidence:.2f})"
        )

    def prune_low_confidence(
        self,
        threshold: float = 0.3,
        min_age_days: int = 30
    ) -> int:
        """
        Remove low-confidence knowledge that hasn't been useful

        Args:
            threshold: Confidence threshold below which to prune
            min_age_days: Minimum age in days before pruning

        Returns:
            Number of entries pruned

        Example:
            >>> pruned = memory.prune_low_confidence(threshold=0.3)
            >>> print(f"Pruned {pruned} low-confidence entries")
        """
        cutoff_date = (
            datetime.now() - timedelta(days=min_age_days)
        ).isoformat()

        with self.db.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                DELETE FROM semantic_knowledge
                WHERE project_id = ?
                AND confidence < ?
                AND created_at < ?
                """,
                (self.project_id, threshold, cutoff_date)
            )
            pruned = cursor.rowcount

        self.logger.info(
            f"Pruned {pruned} low-confidence entries "
            f"(threshold={threshold}, age>{min_age_days}d)"
        )
        return pruned

    # ========================================================================
    # Code Pattern Operations
    # ========================================================================

    def store_pattern(
        self,
        pattern_name: str,
        pattern_data: Dict[str, Any],
        category: Optional[str] = None,
        confidence: float = 0.5,
        tags: Optional[List[str]] = None
    ) -> str:
        """
        Store reusable code pattern

        Args:
            pattern_name: Unique pattern identifier
            pattern_data: Pattern data (code, description, usage)
            category: Pattern category
            confidence: Initial confidence score
            tags: Optional tags

        Returns:
            Pattern ID

        Example:
            >>> memory.store_pattern(
            ...     pattern_name="api_error_handler",
            ...     pattern_data={
            ...         "code": "try:\n    ...\nexcept Exception as e:\n    ...",
            ...         "description": "Standard API error handling",
            ...         "usage": "Wrap all API endpoints"
            ...     },
            ...     category="error_handling"
            ... )
        """
        pattern_id = str(uuid.uuid4())
        category = category or KnowledgeCategory.CODE_PATTERN
        confidence = max(0.0, min(1.0, confidence))
        tags_json = json.dumps(tags or [])
        now = datetime.now().isoformat()

        with self.db.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO code_patterns
                (id, project_id, pattern_name, category, pattern_data,
                 confidence, created_at, updated_at, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    pattern_id,
                    self.project_id,
                    pattern_name,
                    category,
                    json.dumps(pattern_data),
                    confidence,
                    now,
                    now,
                    tags_json
                )
            )

        self.logger.info(f"Stored pattern: {pattern_name}")
        return pattern_id

    def get_pattern(self, pattern_name: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve code pattern by name

        Args:
            pattern_name: Pattern identifier

        Returns:
            Pattern dictionary, or None if not found
        """
        conn = self.db._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT * FROM code_patterns
            WHERE project_id = ? AND pattern_name = ?
            """,
            (self.project_id, pattern_name)
        )

        row = cursor.fetchone()
        if row:
            pattern = dict(row)
            pattern["pattern_data"] = json.loads(pattern["pattern_data"])
            pattern["tags"] = json.loads(pattern.get("tags", "[]"))

            # Update usage count
            with self.db.transaction() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    UPDATE code_patterns
                    SET usage_count = usage_count + 1,
                        updated_at = ?
                    WHERE id = ?
                    """,
                    (datetime.now().isoformat(), pattern["id"])
                )

            return pattern

        return None

    def list_patterns(
        self,
        category: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        List all code patterns

        Args:
            category: Optional category filter
            limit: Maximum results

        Returns:
            List of pattern dictionaries
        """
        conn = self.db._get_connection()
        cursor = conn.cursor()

        query = """
            SELECT * FROM code_patterns
            WHERE project_id = ?
        """
        params = [self.project_id]

        if category:
            query += " AND category = ?"
            params.append(category)

        query += " ORDER BY confidence DESC, usage_count DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)

        patterns = []
        for row in cursor.fetchall():
            pattern = dict(row)
            pattern["pattern_data"] = json.loads(pattern["pattern_data"])
            pattern["tags"] = json.loads(pattern.get("tags", "[]"))
            patterns.append(pattern)

        return patterns

    # ========================================================================
    # Utility Methods
    # ========================================================================

    def _track_access(self, knowledge_id: str) -> None:
        """Track knowledge access (internal)"""
        with self.db.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE semantic_knowledge
                SET access_count = access_count + 1,
                    last_accessed_at = ?
                WHERE id = ?
                """,
                (datetime.now().isoformat(), knowledge_id)
            )

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get semantic memory statistics

        Returns:
            Statistics dictionary
        """
        conn = self.db._get_connection()
        cursor = conn.cursor()

        # Knowledge stats
        cursor.execute(
            """
            SELECT
                COUNT(*) as total_knowledge,
                AVG(confidence) as avg_confidence,
                SUM(access_count) as total_accesses,
                SUM(success_count) as total_successes,
                SUM(failure_count) as total_failures
            FROM semantic_knowledge
            WHERE project_id = ?
            """,
            (self.project_id,)
        )
        knowledge_stats = dict(cursor.fetchone())

        # Pattern stats
        cursor.execute(
            """
            SELECT
                COUNT(*) as total_patterns,
                AVG(confidence) as avg_confidence,
                SUM(usage_count) as total_usage
            FROM code_patterns
            WHERE project_id = ?
            """,
            (self.project_id,)
        )
        pattern_stats = dict(cursor.fetchone())

        # Category breakdown
        cursor.execute(
            """
            SELECT category, COUNT(*) as count
            FROM semantic_knowledge
            WHERE project_id = ?
            GROUP BY category
            ORDER BY count DESC
            """,
            (self.project_id,)
        )
        category_breakdown = {
            row["category"]: row["count"]
            for row in cursor.fetchall()
        }

        return {
            "knowledge": knowledge_stats,
            "patterns": pattern_stats,
            "categories": category_breakdown,
            "project_id": self.project_id
        }


# ============================================================================
# Example Usage
# ============================================================================

if __name__ == "__main__":
    print("=== SemanticMemory Example Usage ===\n")

    # Initialize
    db = SwarmDB()
    memory = SemanticMemory(db, project_id="moai-adk")
    print("✓ SemanticMemory initialized")

    # Example 1: Store architectural decision
    print("\n--- Example 1: Store ADR ---")
    adr_id = memory.store_knowledge(
        topic="api_authentication",
        knowledge={
            "decision": "Use JWT with refresh tokens",
            "rationale": "Stateless, scalable, industry standard",
            "alternatives": ["Session-based", "OAuth2"],
            "implementation": "FastAPI + PyJWT"
        },
        confidence=0.9,
        category=KnowledgeCategory.ARCHITECTURAL_DECISION,
        tags=["authentication", "security", "api"]
    )
    print(f"✓ Stored ADR: {adr_id}")

    # Example 2: Store best practice
    print("\n--- Example 2: Store Best Practice ---")
    bp_id = memory.store_knowledge(
        topic="error_handling",
        knowledge={
            "practice": "Always use structured error responses",
            "format": {"error": "type", "message": "str", "details": "dict"},
            "rationale": "Consistent client error handling"
        },
        confidence=0.8,
        category=KnowledgeCategory.BEST_PRACTICE,
        tags=["error", "api", "standard"]
    )
    print(f"✓ Stored best practice: {bp_id}")

    # Example 3: Store code pattern
    print("\n--- Example 3: Store Code Pattern ---")
    pattern_id = memory.store_pattern(
        pattern_name="api_error_decorator",
        pattern_data={
            "code": "@handle_api_errors\ndef endpoint():\n    ...",
            "description": "Decorator for consistent API error handling",
            "usage": "Apply to all API endpoints"
        },
        category=KnowledgeCategory.CODE_PATTERN,
        tags=["decorator", "error", "api"]
    )
    print(f"✓ Stored pattern: {pattern_id}")

    # Example 4: Search knowledge
    print("\n--- Example 4: Search Knowledge ---")
    results = memory.search_knowledge("authentication security", limit=5)
    print(f"✓ Found {len(results)} results:")
    for result in results:
        print(f"  - {result['topic']} (confidence: {result['confidence']:.2f})")

    # Example 5: Record success and update confidence
    print("\n--- Example 5: Update Confidence ---")
    memory.record_success(adr_id)
    updated = memory.retrieve_knowledge("api_authentication")
    print(f"✓ Updated confidence: {updated['confidence']:.2f}")

    # Example 6: Get pattern
    print("\n--- Example 6: Retrieve Pattern ---")
    pattern = memory.get_pattern("api_error_decorator")
    if pattern:
        print(f"✓ Retrieved pattern: {pattern['pattern_name']}")
        print(f"  Usage count: {pattern['usage_count']}")

    # Example 7: List by category
    print("\n--- Example 7: List by Category ---")
    adrs = memory.list_knowledge(
        category=KnowledgeCategory.ARCHITECTURAL_DECISION,
        min_confidence=0.5
    )
    print(f"✓ Found {len(adrs)} ADRs with confidence >= 0.5")

    # Example 8: Statistics
    print("\n--- Example 8: Statistics ---")
    stats = memory.get_statistics()
    print(f"✓ Total knowledge: {stats['knowledge']['total_knowledge']}")
    print(f"✓ Avg confidence: {stats['knowledge']['avg_confidence']:.2f}")
    print(f"✓ Total patterns: {stats['patterns']['total_patterns']}")
    print(f"✓ Categories: {stats['categories']}")

    # Cleanup
    db.close()
    print("\n✅ SemanticMemory demonstration complete")
