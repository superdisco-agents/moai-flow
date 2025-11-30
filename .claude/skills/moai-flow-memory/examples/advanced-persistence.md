# Advanced Persistence Examples

Production-ready patterns for memory persistence, maintenance, and performance optimization.

## Example 1: Automatic Maintenance Scheduler

```python
from moai_flow.memory import SwarmDB, SemanticMemory, EpisodicMemory
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)

class MemoryMaintenanceScheduler:
    """Automated memory maintenance and optimization"""

    def __init__(self, db: SwarmDB, project_id: str):
        self.db = db
        self.project_id = project_id
        self.semantic = SemanticMemory(db, project_id=project_id)
        self.episodic = EpisodicMemory(db, project_id=project_id)
        self.logger = logging.getLogger(__name__)

    def run_daily_maintenance(self):
        """Daily cleanup and optimization"""

        self.logger.info("=== Daily Maintenance Started ===")

        # 1. Cleanup old events (30 days)
        events_pruned = self.db.cleanup_old_events(days=30)
        self.logger.info(f"Pruned {events_pruned} old events (>30 days)")

        # 2. Cleanup old episodes (90 days)
        episodes_pruned = self.episodic.cleanup_old_episodes(days=90)
        self.logger.info(f"Pruned {episodes_pruned} old episodes (>90 days)")

        # 3. Get statistics before pruning knowledge
        stats_before = self.semantic.get_statistics()
        self.logger.info(f"Knowledge before pruning: {stats_before['knowledge']['total_knowledge']}")

        # 4. Prune low-confidence knowledge
        knowledge_pruned = self.semantic.prune_low_confidence(
            threshold=0.3,
            min_age_days=30
        )
        self.logger.info(f"Pruned {knowledge_pruned} low-confidence knowledge")

        # 5. Get statistics after pruning
        stats_after = self.semantic.get_statistics()
        self.logger.info(f"Knowledge after pruning: {stats_after['knowledge']['total_knowledge']}")

        # 6. Optimize database
        self.db.vacuum()
        self.logger.info("Database vacuumed")

        return {
            'events_pruned': events_pruned,
            'episodes_pruned': episodes_pruned,
            'knowledge_pruned': knowledge_pruned,
            'knowledge_remaining': stats_after['knowledge']['total_knowledge']
        }

    def run_weekly_optimization(self):
        """Weekly pattern analysis and optimization"""

        self.logger.info("=== Weekly Optimization Started ===")

        # 1. Analyze knowledge quality
        all_knowledge = self.semantic.list_knowledge(limit=1000)

        rarely_accessed = [
            k for k in all_knowledge
            if k['access_count'] < 5 and k['confidence'] < 0.6
        ]
        self.logger.info(f"Found {len(rarely_accessed)} rarely accessed low-confidence items")

        # 2. Analyze patterns
        all_patterns = self.semantic.list_patterns(limit=100)

        unused_patterns = [
            p for p in all_patterns
            if p['usage_count'] == 0 and
            (datetime.now() - datetime.fromisoformat(p['created_at'])).days > 30
        ]
        self.logger.info(f"Found {len(unused_patterns)} unused patterns (>30 days old)")

        # 3. Generate recommendations
        recommendations = []

        if len(rarely_accessed) > 10:
            recommendations.append(f"Review {len(rarely_accessed)} rarely accessed knowledge items")

        if len(unused_patterns) > 5:
            recommendations.append(f"Consider removing {len(unused_patterns)} unused patterns")

        avg_confidence = self.semantic.get_statistics()['knowledge']['avg_confidence']
        if avg_confidence < 0.6:
            recommendations.append("Average knowledge confidence is low - review and update")

        return {
            'rarely_accessed': len(rarely_accessed),
            'unused_patterns': len(unused_patterns),
            'recommendations': recommendations
        }

    def run_monthly_analysis(self):
        """Monthly comprehensive analysis"""

        self.logger.info("=== Monthly Analysis Started ===")

        # 1. Knowledge statistics
        stats = self.semantic.get_statistics()

        # 2. Category breakdown
        categories = stats['categories']
        most_common_category = max(categories.items(), key=lambda x: x[1]) if categories else None

        # 3. Pattern usage analysis
        patterns = self.semantic.list_patterns(limit=100)
        total_pattern_usage = sum(p['usage_count'] for p in patterns)

        # 4. Episode analysis
        recent_episodes = self.episodic.get_recent_events(limit=1000)
        decision_episodes = [ep for ep in recent_episodes if ep['event_type'] == 'decision']

        # 5. Success rate analysis
        successful = sum(
            1 for ep in decision_episodes
            if ep.get('outcome', {}).get('status') == 'success'
        )
        success_rate = (successful / len(decision_episodes) * 100) if decision_episodes else 0

        report = {
            'total_knowledge': stats['knowledge']['total_knowledge'],
            'avg_confidence': stats['knowledge']['avg_confidence'],
            'total_patterns': stats['patterns']['total_patterns'],
            'pattern_usage': total_pattern_usage,
            'most_common_category': most_common_category,
            'total_decisions': len(decision_episodes),
            'decision_success_rate': success_rate
        }

        self.logger.info(f"Monthly Report: {report}")
        return report


# Usage Example
db = SwarmDB()
scheduler = MemoryMaintenanceScheduler(db, project_id="moai-adk")

# Populate with test data
semantic = SemanticMemory(db, project_id="moai-adk")
for i in range(10):
    semantic.store_knowledge(
        topic=f"knowledge_{i}",
        knowledge={"data": f"test_{i}"},
        confidence=0.5 - (i * 0.05),  # Decreasing confidence
        category="best_practice"
    )

# Run maintenance
print("\n--- Daily Maintenance ---")
daily_result = scheduler.run_daily_maintenance()
print(f"Results: {daily_result}")

print("\n--- Weekly Optimization ---")
weekly_result = scheduler.run_weekly_optimization()
print(f"Results: {weekly_result}")

print("\n--- Monthly Analysis ---")
monthly_result = scheduler.run_monthly_analysis()
print(f"Results: {monthly_result}")

db.close()
print("\n✅ Example 1 complete")
```

## Example 2: Transaction Patterns

```python
from moai_flow.memory import SwarmDB, SemanticMemory, EpisodicMemory
import logging

logging.basicConfig(level=logging.INFO)

class TransactionalMemoryManager:
    """Manage complex multi-component operations atomically"""

    def __init__(self, db: SwarmDB, project_id: str):
        self.db = db
        self.project_id = project_id
        self.semantic = SemanticMemory(db, project_id=project_id)
        self.episodic = EpisodicMemory(db, project_id=project_id)
        self.logger = logging.getLogger(__name__)

    def atomic_decision_with_knowledge(
        self,
        decision_type: str,
        options: list,
        chosen: str,
        rationale: str,
        knowledge_data: dict
    ):
        """
        Atomically store decision and related knowledge.
        Either both succeed or both fail.
        """

        try:
            with self.db.transaction() as conn:
                cursor = conn.cursor()

                # 1. Store knowledge
                knowledge_id = self.semantic.store_knowledge(
                    topic=f"{decision_type}_knowledge",
                    knowledge=knowledge_data,
                    confidence=0.7,
                    category="best_practice"
                )

                # 2. Record decision
                decision_id = self.episodic.record_decision(
                    decision_type=decision_type,
                    options=options,
                    chosen=chosen,
                    rationale=rationale,
                    context={"knowledge_id": knowledge_id}
                )

                # 3. Record agent event
                event_id = self.db.insert_event({
                    "event_type": "decision",
                    "agent_id": "decision-manager",
                    "agent_type": "manager",
                    "timestamp": datetime.now().isoformat(),
                    "metadata": {
                        "decision_id": decision_id,
                        "knowledge_id": knowledge_id
                    }
                })

                self.logger.info(
                    f"Atomic operation complete: "
                    f"knowledge={knowledge_id}, decision={decision_id}, event={event_id}"
                )

                return {
                    'knowledge_id': knowledge_id,
                    'decision_id': decision_id,
                    'event_id': event_id
                }

        except Exception as e:
            self.logger.error(f"Atomic operation failed: {e}")
            # Transaction automatically rolled back
            raise

    def batch_knowledge_import(self, knowledge_items: list):
        """Import multiple knowledge items atomically"""

        try:
            with self.db.transaction() as conn:
                imported_ids = []

                for item in knowledge_items:
                    knowledge_id = self.semantic.store_knowledge(
                        topic=item['topic'],
                        knowledge=item['knowledge'],
                        confidence=item.get('confidence', 0.5),
                        category=item.get('category', 'best_practice'),
                        tags=item.get('tags', [])
                    )
                    imported_ids.append(knowledge_id)

                self.logger.info(f"Batch imported {len(imported_ids)} knowledge items")
                return imported_ids

        except Exception as e:
            self.logger.error(f"Batch import failed: {e}")
            raise

    def consistent_update(self, knowledge_id: str, decision_id: str, success: bool):
        """Update both knowledge and decision consistently"""

        try:
            with self.db.transaction() as conn:
                # Update knowledge confidence
                if success:
                    self.semantic.record_success(knowledge_id)
                else:
                    self.semantic.record_failure(knowledge_id)

                # Update decision outcome
                self.episodic.record_outcome(
                    decision_id,
                    outcome="success" if success else "failure",
                    metrics={"synchronized": True}
                )

                self.logger.info(
                    f"Consistent update: knowledge={knowledge_id}, "
                    f"decision={decision_id}, success={success}"
                )

        except Exception as e:
            self.logger.error(f"Consistent update failed: {e}")
            raise


# Usage Example
from datetime import datetime

db = SwarmDB()
manager = TransactionalMemoryManager(db, project_id="moai-adk")

# Example 1: Atomic decision with knowledge
print("\n--- Atomic Operation ---")
result = manager.atomic_decision_with_knowledge(
    decision_type="architecture",
    options=["PostgreSQL", "MongoDB", "MySQL"],
    chosen="PostgreSQL",
    rationale="ACID compliance required",
    knowledge_data={
        "decision": "PostgreSQL for transactional data",
        "pros": ["ACID", "Mature", "Extensions"],
        "cons": ["Scaling complexity"]
    }
)
print(f"Atomic result: {result}")

# Example 2: Batch import
print("\n--- Batch Import ---")
batch_items = [
    {
        "topic": "api_versioning",
        "knowledge": {"strategy": "URL versioning", "format": "/api/v1/"},
        "confidence": 0.8,
        "category": "best_practice"
    },
    {
        "topic": "error_logging",
        "knowledge": {"level": "ERROR", "format": "JSON"},
        "confidence": 0.9,
        "category": "best_practice"
    },
    {
        "topic": "rate_limiting",
        "knowledge": {"strategy": "Token bucket", "rate": "100/min"},
        "confidence": 0.7,
        "category": "best_practice"
    }
]

imported = manager.batch_knowledge_import(batch_items)
print(f"Imported {len(imported)} items: {imported}")

# Example 3: Consistent update
print("\n--- Consistent Update ---")
manager.consistent_update(
    knowledge_id=result['knowledge_id'],
    decision_id=result['decision_id'],
    success=True
)

db.close()
print("\n✅ Example 2 complete")
```

## Example 3: Performance Optimization

```python
from moai_flow.memory import SwarmDB, SemanticMemory
import time
import logging

logging.basicConfig(level=logging.INFO)

class PerformanceOptimizedMemory:
    """Demonstrate performance optimization techniques"""

    def __init__(self, db: SwarmDB, project_id: str):
        self.db = db
        self.project_id = project_id
        self.memory = SemanticMemory(db, project_id=project_id)
        self.logger = logging.getLogger(__name__)

    def benchmark_batch_vs_individual(self, count: int = 100):
        """Compare batch vs individual operations"""

        # Individual inserts
        start = time.time()
        for i in range(count):
            self.memory.store_knowledge(
                topic=f"individual_{i}",
                knowledge={"data": f"test_{i}"},
                confidence=0.5,
                category="test"
            )
        individual_time = time.time() - start

        # Batch inserts
        start = time.time()
        with self.db.transaction() as conn:
            for i in range(count):
                self.memory.store_knowledge(
                    topic=f"batch_{i}",
                    knowledge={"data": f"test_{i}"},
                    confidence=0.5,
                    category="test"
                )
        batch_time = time.time() - start

        speedup = individual_time / batch_time

        self.logger.info(f"\n--- Batch vs Individual ({count} items) ---")
        self.logger.info(f"Individual: {individual_time:.3f}s")
        self.logger.info(f"Batch: {batch_time:.3f}s")
        self.logger.info(f"Speedup: {speedup:.2f}x")

        return {
            'individual_time': individual_time,
            'batch_time': batch_time,
            'speedup': speedup
        }

    def benchmark_search_performance(self, knowledge_count: int = 1000):
        """Test search performance with different query strategies"""

        # Populate data
        self.logger.info(f"Populating {knowledge_count} knowledge items...")
        with self.db.transaction() as conn:
            for i in range(knowledge_count):
                self.memory.store_knowledge(
                    topic=f"search_test_{i}",
                    knowledge={
                        "type": "api" if i % 2 == 0 else "database",
                        "priority": "high" if i % 3 == 0 else "low",
                        "data": f"content_{i}"
                    },
                    confidence=0.5 + (i % 50) / 100,
                    category="test",
                    tags=["test", f"category_{i % 10}"]
                )

        # Benchmark exact match
        start = time.time()
        exact = self.memory.retrieve_knowledge("search_test_500")
        exact_time = time.time() - start

        # Benchmark full-text search
        start = time.time()
        search_results = self.memory.search_knowledge(
            query="api high priority",
            min_confidence=0.5,
            limit=10
        )
        search_time = time.time() - start

        # Benchmark category filter
        start = time.time()
        category_results = self.memory.list_knowledge(
            category="test",
            min_confidence=0.7,
            limit=50
        )
        category_time = time.time() - start

        self.logger.info(f"\n--- Search Performance ({knowledge_count} items) ---")
        self.logger.info(f"Exact match: {exact_time*1000:.2f}ms")
        self.logger.info(f"Full-text search: {search_time*1000:.2f}ms ({len(search_results)} results)")
        self.logger.info(f"Category filter: {category_time*1000:.2f}ms ({len(category_results)} results)")

        return {
            'exact_time_ms': exact_time * 1000,
            'search_time_ms': search_time * 1000,
            'category_time_ms': category_time * 1000
        }

    def demonstrate_caching_pattern(self):
        """Demonstrate local caching for frequently accessed knowledge"""

        cache = {}

        def get_knowledge_cached(topic: str):
            """Get knowledge with local cache"""
            if topic in cache:
                return cache[topic]

            knowledge = self.memory.retrieve_knowledge(topic)
            if knowledge:
                cache[topic] = knowledge
            return knowledge

        # Benchmark without cache
        topic = "cached_knowledge"
        self.memory.store_knowledge(
            topic=topic,
            knowledge={"data": "frequently accessed"},
            confidence=0.9,
            category="test"
        )

        start = time.time()
        for _ in range(100):
            self.memory.retrieve_knowledge(topic)
        no_cache_time = time.time() - start

        # Benchmark with cache
        start = time.time()
        for _ in range(100):
            get_knowledge_cached(topic)
        cache_time = time.time() - start

        speedup = no_cache_time / cache_time

        self.logger.info(f"\n--- Caching Pattern (100 accesses) ---")
        self.logger.info(f"Without cache: {no_cache_time*1000:.2f}ms")
        self.logger.info(f"With cache: {cache_time*1000:.2f}ms")
        self.logger.info(f"Speedup: {speedup:.2f}x")

        return {
            'no_cache_time_ms': no_cache_time * 1000,
            'cache_time_ms': cache_time * 1000,
            'speedup': speedup
        }


# Usage Example
db = SwarmDB()
optimizer = PerformanceOptimizedMemory(db, project_id="moai-adk")

# Benchmark 1: Batch vs Individual
batch_result = optimizer.benchmark_batch_vs_individual(count=50)

# Benchmark 2: Search Performance
search_result = optimizer.benchmark_search_performance(knowledge_count=500)

# Benchmark 3: Caching Pattern
cache_result = optimizer.demonstrate_caching_pattern()

db.close()
print("\n✅ Example 3 complete")
```

## Example 4: Production Error Handling

```python
from moai_flow.memory import SwarmDB, SemanticMemory, EpisodicMemory
import logging
import sqlite3

logging.basicConfig(level=logging.INFO)

class ResilientMemoryManager:
    """Production-grade error handling and recovery"""

    def __init__(self, db: SwarmDB, project_id: str):
        self.db = db
        self.project_id = project_id
        self.semantic = SemanticMemory(db, project_id=project_id)
        self.episodic = EpisodicMemory(db, project_id=project_id)
        self.logger = logging.getLogger(__name__)

    def safe_knowledge_store(self, topic: str, knowledge: dict, **kwargs):
        """Store knowledge with comprehensive error handling"""

        try:
            knowledge_id = self.semantic.store_knowledge(
                topic=topic,
                knowledge=knowledge,
                **kwargs
            )
            self.logger.info(f"Successfully stored knowledge: {topic}")
            return {'success': True, 'knowledge_id': knowledge_id}

        except sqlite3.IntegrityError as e:
            self.logger.error(f"Integrity error storing {topic}: {e}")
            # Handle duplicate or constraint violation
            existing = self.semantic.retrieve_knowledge(topic)
            if existing:
                self.logger.info(f"Knowledge already exists, updating: {topic}")
                updated = self.semantic.update_knowledge(
                    existing['id'],
                    knowledge=knowledge
                )
                return {'success': True, 'knowledge_id': existing['id'], 'updated': True}
            return {'success': False, 'error': str(e)}

        except sqlite3.OperationalError as e:
            self.logger.error(f"Operational error: {e}")
            # Handle database locked, disk full, etc.
            return {'success': False, 'error': str(e), 'retryable': True}

        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            return {'success': False, 'error': str(e)}

    def safe_decision_record(self, decision_type: str, **kwargs):
        """Record decision with retry logic"""

        max_retries = 3
        retry_delay = 0.1

        for attempt in range(max_retries):
            try:
                decision_id = self.episodic.record_decision(
                    decision_type=decision_type,
                    **kwargs
                )
                self.logger.info(f"Successfully recorded decision: {decision_type}")
                return {'success': True, 'decision_id': decision_id}

            except sqlite3.OperationalError as e:
                if attempt < max_retries - 1:
                    self.logger.warning(f"Retry {attempt + 1}/{max_retries}: {e}")
                    import time
                    time.sleep(retry_delay * (2 ** attempt))  # Exponential backoff
                else:
                    self.logger.error(f"Failed after {max_retries} retries: {e}")
                    return {'success': False, 'error': str(e)}

            except Exception as e:
                self.logger.error(f"Non-retryable error: {e}")
                return {'success': False, 'error': str(e)}

    def graceful_degradation(self, topic: str, default_knowledge: dict):
        """Provide fallback when memory unavailable"""

        try:
            knowledge = self.semantic.retrieve_knowledge(topic)
            if knowledge:
                return {'source': 'memory', 'knowledge': knowledge}

        except Exception as e:
            self.logger.warning(f"Memory unavailable, using default: {e}")

        return {'source': 'default', 'knowledge': default_knowledge}


# Usage Example
db = SwarmDB()
manager = ResilientMemoryManager(db, project_id="moai-adk")

# Example 1: Safe storage with error handling
print("\n--- Safe Knowledge Storage ---")
result1 = manager.safe_knowledge_store(
    topic="production_config",
    knowledge={"setting": "value"},
    confidence=0.9,
    category="convention"
)
print(f"Result: {result1}")

# Try duplicate storage
result2 = manager.safe_knowledge_store(
    topic="production_config",
    knowledge={"setting": "updated_value"},
    confidence=0.95,
    category="convention"
)
print(f"Duplicate result: {result2}")

# Example 2: Safe decision recording with retry
print("\n--- Safe Decision Recording ---")
result3 = manager.safe_decision_record(
    decision_type="deployment",
    options=["canary", "blue-green", "rolling"],
    chosen="canary",
    rationale="Gradual rollout preferred"
)
print(f"Result: {result3}")

# Example 3: Graceful degradation
print("\n--- Graceful Degradation ---")
result4 = manager.graceful_degradation(
    topic="default_config",
    default_knowledge={"timeout": 30, "retries": 3}
)
print(f"Result: {result4}")

db.close()
print("\n✅ Example 4 complete")
```

## Production Deployment Checklist

```bash
# 1. Database backup before deployment
cp .moai/memory/swarm.db .moai/backups/swarm_$(date +%Y%m%d).db

# 2. Run maintenance
python -m moai_flow.memory.maintenance --daily

# 3. Monitor database size
du -h .moai/memory/swarm.db

# 4. Check database integrity
sqlite3 .moai/memory/swarm.db "PRAGMA integrity_check;"

# 5. Optimize performance
sqlite3 .moai/memory/swarm.db "ANALYZE;"

# 6. Set up automated maintenance cron job
# 0 2 * * * /path/to/maintenance.py --daily
# 0 3 * * 0 /path/to/maintenance.py --weekly
# 0 4 1 * * /path/to/maintenance.py --monthly
```

## Performance Benchmarks

Expected performance on modern hardware:
- Individual insert: ~1-2ms
- Batch insert (100 items): ~50-100ms (20x faster)
- Exact match query: <1ms
- Full-text search (1000 items): ~5-10ms
- Category filter: ~2-5ms
- Transaction overhead: ~0.1ms

## Running Advanced Examples

```bash
python examples/advanced-persistence.py
```

All examples demonstrate production-ready patterns for real-world usage.
