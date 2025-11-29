# SemanticMemory Quick Start Guide

Get started with SemanticMemory in 5 minutes.

---

## Installation

No installation required! SemanticMemory is included in MoAI-Flow.

**Dependencies:**
- Python 3.8+
- SQLite3 (built-in)
- No external packages required

---

## Basic Usage (30 seconds)

```python
from moai_flow.memory.swarm_db import SwarmDB
from moai_flow.memory.semantic_memory import SemanticMemory

# 1. Initialize
db = SwarmDB()
memory = SemanticMemory(db, project_id="my-project")

# 2. Store knowledge
knowledge_id = memory.store_knowledge(
    topic="api_design",
    knowledge={"pattern": "RESTful", "rationale": "Industry standard"},
    confidence=0.9
)

# 3. Retrieve knowledge
knowledge = memory.retrieve_knowledge("api_design")
print(knowledge['knowledge']['pattern'])  # Output: RESTful

# 4. Cleanup
db.close()
```

---

## Common Use Cases

### 1. Store Architectural Decision (ADR)

```python
from moai_flow.memory.semantic_memory import KnowledgeCategory

adr_id = memory.store_knowledge(
    topic="database_choice",
    knowledge={
        "decision": "PostgreSQL 16",
        "rationale": "ACID compliance, JSON support",
        "alternatives": ["MySQL", "MongoDB"],
        "trade_offs": {
            "pros": ["Mature", "Feature-rich"],
            "cons": ["More complex"]
        }
    },
    confidence=0.9,
    category=KnowledgeCategory.ARCHITECTURAL_DECISION,
    tags=["database", "postgresql"]
)
```

### 2. Store Code Pattern

```python
pattern_id = memory.store_pattern(
    pattern_name="error_handler_decorator",
    pattern_data={
        "code": "@handle_errors\ndef endpoint():\n    ...",
        "description": "Standard error handling",
        "usage": "All API endpoints"
    },
    category=KnowledgeCategory.CODE_PATTERN,
    tags=["error", "decorator"]
)

# Retrieve pattern later
pattern = memory.get_pattern("error_handler_decorator")
print(pattern['pattern_data']['code'])
```

### 3. Search Knowledge

```python
# Search across all knowledge
results = memory.search_knowledge("authentication", min_confidence=0.5)

# Search within category
security_results = memory.search_knowledge(
    query="security",
    category=KnowledgeCategory.ARCHITECTURAL_DECISION,
    min_confidence=0.6,
    limit=10
)

for result in results:
    print(f"{result['topic']}: {result['confidence']}")
```

### 4. Track Knowledge Quality

```python
# Store knowledge with medium confidence
pattern_id = memory.store_knowledge(
    topic="caching_strategy",
    knowledge={"strategy": "Redis 5-min TTL"},
    confidence=0.5
)

# Use successfully → confidence increases
memory.record_success(pattern_id)  # 0.5 → 0.6

# Use again successfully
memory.record_success(pattern_id)  # 0.6 → 0.7

# Fails in production → confidence decreases
memory.record_failure(pattern_id)  # 0.7 → 0.5

# Update based on learnings
memory.update_knowledge(
    pattern_id,
    knowledge={"strategy": "Redis adaptive TTL"},
    confidence=0.8
)
```

### 5. List and Filter Knowledge

```python
# List all ADRs
adrs = memory.list_knowledge(
    category=KnowledgeCategory.ARCHITECTURAL_DECISION,
    min_confidence=0.5
)

# List all high-confidence knowledge
high_quality = memory.list_knowledge(min_confidence=0.8)

# Get statistics
stats = memory.get_statistics()
print(f"Total knowledge: {stats['knowledge']['total_knowledge']}")
print(f"Avg confidence: {stats['knowledge']['avg_confidence']:.2f}")
```

### 6. Automatic Cleanup

```python
# Prune low-confidence knowledge older than 30 days
pruned = memory.prune_low_confidence(threshold=0.3, min_age_days=30)
print(f"Pruned {pruned} entries")
```

---

## Knowledge Categories

```python
from moai_flow.memory.semantic_memory import KnowledgeCategory

# Available categories
KnowledgeCategory.ARCHITECTURAL_DECISION  # ADRs
KnowledgeCategory.BEST_PRACTICE          # Best practices
KnowledgeCategory.CODE_PATTERN           # Code templates
KnowledgeCategory.ERROR_RESOLUTION       # Error solutions
KnowledgeCategory.WORKFLOW_PATTERN       # Workflows
KnowledgeCategory.CONVENTION             # Conventions
KnowledgeCategory.TOOL_USAGE             # Tool patterns
KnowledgeCategory.PERFORMANCE_PATTERN    # Optimizations
```

---

## Confidence Scoring

| Event | Change | Example |
|-------|--------|---------|
| New knowledge | 0.5 (default) | Initial storage |
| Success | +0.1 | Pattern worked well |
| Failure | -0.2 | Pattern caused issues |
| Manual update | Set value | Expert review |

**Bounds:** All confidence scores clamped to [0.0, 1.0]

**Pruning:** Knowledge with confidence < 0.3 older than 30 days auto-pruned

---

## Best Practices

### 1. Descriptive Topics

```python
# ✅ Good: Specific, searchable
memory.store_knowledge(
    topic="jwt_authentication_strategy",
    knowledge={...}
)

# ❌ Bad: Too generic
memory.store_knowledge(
    topic="auth",
    knowledge={...}
)
```

### 2. Use Tags Liberally

```python
# ✅ Good: Multiple relevant tags
memory.store_knowledge(
    topic="api_rate_limiting",
    knowledge={...},
    tags=["api", "security", "performance", "redis"]
)

# ❌ Bad: No tags
memory.store_knowledge(
    topic="api_rate_limiting",
    knowledge={...}
)
```

### 3. Track Success/Failure

```python
# Store pattern
pattern_id = memory.store_knowledge(topic="pattern", knowledge={...})

# Use pattern
try:
    # ... apply pattern ...
    memory.record_success(pattern_id)  # It worked!
except Exception:
    memory.record_failure(pattern_id)  # It failed!
```

### 4. Regular Cleanup

```python
# Schedule periodic pruning (e.g., weekly)
def weekly_cleanup():
    pruned = memory.prune_low_confidence(threshold=0.3, min_age_days=30)
    print(f"Weekly cleanup: pruned {pruned} entries")
```

### 5. Project Isolation

```python
# Different projects, different memory instances
backend_memory = SemanticMemory(db, project_id="backend-api")
frontend_memory = SemanticMemory(db, project_id="frontend-app")

# Each has isolated knowledge
backend_memory.store_knowledge(topic="auth", knowledge={"type": "JWT"})
frontend_memory.store_knowledge(topic="auth", knowledge={"type": "OAuth2"})
```

---

## Integration with Agents

```python
class ExpertBackend:
    def __init__(self, swarm_db):
        self.memory = SemanticMemory(swarm_db, project_id="backend-api")

    def design_api(self, requirements):
        # Search for existing patterns
        patterns = self.memory.search_knowledge("api design")

        # Apply pattern
        design = self.apply_pattern(patterns)

        # Store new knowledge if successful
        if design.successful:
            self.memory.store_knowledge(
                topic=f"api_design_{design.id}",
                knowledge=design.details,
                confidence=0.7,
                category=KnowledgeCategory.ARCHITECTURAL_DECISION
            )
```

---

## Troubleshooting

### Database locked error

```python
# Ensure proper cleanup
try:
    memory = SemanticMemory(db, project_id="my-project")
    # ... use memory ...
finally:
    db.close()  # Always close!
```

### Search returns no results

```python
# Check confidence threshold
results = memory.search_knowledge("query", min_confidence=0.0)

# Check project_id
memory = SemanticMemory(db, project_id="correct-project-id")
```

### Confidence not updating

```python
# Verify knowledge_id is correct
knowledge = memory.retrieve_knowledge("topic")
memory.record_success(knowledge['id'])  # Use ID from retrieval
```

---

## Next Steps

- **Read full documentation**: [README.md](README.md)
- **View architecture**: [ARCHITECTURE.txt](ARCHITECTURE.txt)
- **Run tests**: `python3 -m pytest tests/moai-flow/memory/test_semantic_memory.py -v`
- **Explore examples**: Run `python3 -m moai_flow.memory.semantic_memory`

---

## Quick Reference

```python
# Initialize
db = SwarmDB()
memory = SemanticMemory(db, project_id="project")

# Store
id = memory.store_knowledge(topic, knowledge, confidence=0.5)

# Retrieve
knowledge = memory.retrieve_knowledge(topic)

# Search
results = memory.search_knowledge(query, min_confidence=0.3)

# Update confidence
memory.record_success(id)      # +0.1
memory.record_failure(id)      # -0.2
memory.update_confidence(id, 0.9)  # Direct

# Patterns
id = memory.store_pattern(name, pattern_data)
pattern = memory.get_pattern(name)

# Cleanup
pruned = memory.prune_low_confidence(threshold=0.3)
db.close()
```

---

**That's it!** You're ready to use SemanticMemory for persistent knowledge storage.

For questions or issues, see [README.md](README.md) or run the test suite for examples.
