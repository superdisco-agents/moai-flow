# Semantic Memory - Long-term Knowledge Management

Confidence-scored knowledge storage for architectural decisions, best practices, and reusable code patterns.

## Overview

SemanticMemory provides persistent, queryable knowledge storage with:

- Confidence-based scoring (0.0 - 1.0)
- Automatic knowledge pruning (<0.3 after 30 days)
- Category-based organization
- Full-text search support
- Access tracking and metrics
- Code pattern storage and reuse

## Knowledge Categories

```python
from moai_flow.memory import KnowledgeCategory

KnowledgeCategory.ARCHITECTURAL_DECISION  # "adr"
KnowledgeCategory.BEST_PRACTICE          # "best_practice"
KnowledgeCategory.CODE_PATTERN           # "code_pattern"
KnowledgeCategory.ERROR_RESOLUTION       # "error_resolution"
KnowledgeCategory.WORKFLOW_PATTERN       # "workflow"
KnowledgeCategory.CONVENTION             # "convention"
KnowledgeCategory.TOOL_USAGE             # "tool_usage"
KnowledgeCategory.PERFORMANCE_PATTERN    # "performance"
```

## Confidence Scoring System

**Initial Confidence**: 0.5 (default)
**Success**: +0.1 (max 1.0)
**Failure**: -0.2 (min 0.0)
**Pruning Threshold**: <0.3 after 30 days

```python
# New knowledge starts at 0.5
knowledge_id = memory.store_knowledge(..., confidence=0.5)

# Successful use: 0.5 → 0.6
memory.record_success(knowledge_id)

# Another success: 0.6 → 0.7
memory.record_success(knowledge_id)

# Failure: 0.7 → 0.5
memory.record_failure(knowledge_id)

# Auto-prune after 30 days if confidence < 0.3
memory.prune_low_confidence(threshold=0.3, min_age_days=30)
```

## API Reference

### Initialization

```python
from moai_flow.memory import SwarmDB, SemanticMemory

db = SwarmDB()
memory = SemanticMemory(db, project_id="moai-adk")
```

### Knowledge Storage

**store_knowledge()**
```python
knowledge_id = memory.store_knowledge(
    topic="api_authentication",
    knowledge={
        "decision": "Use JWT with refresh tokens",
        "rationale": "Stateless, scalable, industry standard",
        "alternatives": ["Session-based", "OAuth2"],
        "implementation": "FastAPI + PyJWT",
        "references": ["https://jwt.io/introduction"]
    },
    confidence=0.9,  # High initial confidence
    category="adr",  # Architectural decision
    tags=["authentication", "security", "api"]
)
```

**retrieve_knowledge()**
```python
# Exact topic match
knowledge = memory.retrieve_knowledge("api_authentication")

if knowledge:
    print(f"Topic: {knowledge['topic']}")
    print(f"Confidence: {knowledge['confidence']}")
    print(f"Category: {knowledge['category']}")
    print(f"Knowledge: {knowledge['knowledge']}")
    print(f"Tags: {knowledge['tags']}")
    print(f"Access count: {knowledge['access_count']}")
```

**search_knowledge()**
```python
# Full-text search across topic, knowledge, and tags
results = memory.search_knowledge(
    query="authentication security",
    limit=10,
    min_confidence=0.5,
    category="adr"  # Optional category filter
)

for result in results:
    print(f"{result['topic']}: {result['confidence']:.2f}")
    print(f"  {result['knowledge']['decision']}")
```

**list_knowledge()**
```python
# List all knowledge, optionally filtered
all_adrs = memory.list_knowledge(
    category="adr",
    min_confidence=0.5,
    limit=100
)

for adr in all_adrs:
    print(f"{adr['topic']} (confidence: {adr['confidence']:.2f})")
```

**update_knowledge()**
```python
# Update existing knowledge
updated = memory.update_knowledge(
    knowledge_id="uuid-123",
    knowledge={
        "decision": "Use JWT with refresh tokens and rotation",
        "rationale": "Added token rotation for security"
    },
    confidence=0.95,
    tags=["authentication", "security", "api", "rotation"]
)
```

### Confidence Management

**record_success()**
```python
# Record successful use (increases confidence by 0.1)
memory.record_success(knowledge_id)

# Get updated knowledge
knowledge = memory.retrieve_knowledge("api_authentication")
print(f"New confidence: {knowledge['confidence']}")  # +0.1
print(f"Success count: {knowledge['success_count']}")  # +1
```

**record_failure()**
```python
# Record failed use (decreases confidence by 0.2)
memory.record_failure(knowledge_id)

# Get updated knowledge
knowledge = memory.retrieve_knowledge("api_authentication")
print(f"New confidence: {knowledge['confidence']}")  # -0.2
print(f"Failure count: {knowledge['failure_count']}")  # +1
```

**update_confidence()**
```python
# Manually set confidence
memory.update_confidence(knowledge_id, new_confidence=0.8)
```

**prune_low_confidence()**
```python
# Remove knowledge below threshold after minimum age
pruned = memory.prune_low_confidence(
    threshold=0.3,      # Confidence must be < 0.3
    min_age_days=30     # Must be at least 30 days old
)

print(f"Pruned {pruned} low-confidence entries")
```

### Code Pattern Operations

**store_pattern()**
```python
pattern_id = memory.store_pattern(
    pattern_name="api_error_decorator",
    pattern_data={
        "code": """
@handle_api_errors
async def endpoint(request: Request):
    try:
        result = await process(request)
        return JSONResponse({"data": result})
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
        """,
        "description": "Standard async API error handling decorator",
        "usage": "Apply to all FastAPI endpoints",
        "dependencies": ["fastapi", "pydantic"]
    },
    category="code_pattern",
    confidence=0.8,
    tags=["decorator", "error", "api", "fastapi"]
)
```

**get_pattern()**
```python
# Retrieve pattern by name
pattern = memory.get_pattern("api_error_decorator")

if pattern:
    print(f"Pattern: {pattern['pattern_name']}")
    print(f"Code:\n{pattern['pattern_data']['code']}")
    print(f"Usage count: {pattern['usage_count']}")
    print(f"Confidence: {pattern['confidence']}")
```

**list_patterns()**
```python
# List all patterns
all_patterns = memory.list_patterns(limit=100)

# Filter by category
error_patterns = memory.list_patterns(
    category="code_pattern",
    limit=50
)

for pattern in error_patterns:
    print(f"{pattern['pattern_name']} (used {pattern['usage_count']} times)")
```

### Statistics

**get_statistics()**
```python
stats = memory.get_statistics()

print(f"Total knowledge: {stats['knowledge']['total_knowledge']}")
print(f"Avg confidence: {stats['knowledge']['avg_confidence']:.2f}")
print(f"Total accesses: {stats['knowledge']['total_accesses']}")
print(f"Success rate: {stats['knowledge']['total_successes'] / stats['knowledge']['total_accesses'] * 100:.1f}%")

print(f"\nTotal patterns: {stats['patterns']['total_patterns']}")
print(f"Total usage: {stats['patterns']['total_usage']}")

print(f"\nCategory breakdown:")
for category, count in stats['categories'].items():
    print(f"  {category}: {count}")
```

## Usage Patterns

### Pattern 1: ADR Storage and Retrieval

```python
# Store architectural decision
adr_id = memory.store_knowledge(
    topic="database_choice",
    knowledge={
        "decision": "Use PostgreSQL with TimescaleDB extension",
        "rationale": "Time-series data requirements, ACID compliance",
        "alternatives": ["MongoDB", "InfluxDB", "MySQL"],
        "pros": ["ACID", "Mature", "Extensions", "Query flexibility"],
        "cons": ["Operational complexity", "Scaling challenges"],
        "status": "accepted",
        "date": "2025-11-30"
    },
    confidence=0.9,
    category=KnowledgeCategory.ARCHITECTURAL_DECISION,
    tags=["database", "postgresql", "timescale", "architecture"]
)

# Later: Retrieve when making related decisions
existing_adrs = memory.search_knowledge(
    query="database",
    category="adr",
    min_confidence=0.7
)

for adr in existing_adrs:
    print(f"Existing decision: {adr['topic']}")
    print(f"  Decision: {adr['knowledge']['decision']}")
    print(f"  Confidence: {adr['confidence']:.2f}")
```

### Pattern 2: Best Practice Evolution

```python
# Store initial best practice
bp_id = memory.store_knowledge(
    topic="error_handling",
    knowledge={
        "practice": "Use structured error responses",
        "format": {"error": "type", "message": "str", "details": "dict"},
        "example": '{"error": "ValidationError", "message": "Invalid input"}'
    },
    confidence=0.6,  # Initial moderate confidence
    category="best_practice"
)

# Record successful use
for _ in range(5):
    memory.record_success(bp_id)  # Confidence increases

# Update practice based on learnings
memory.update_knowledge(
    bp_id,
    knowledge={
        "practice": "Use structured error responses with stack traces in dev",
        "format": {
            "error": "type",
            "message": "str",
            "details": "dict",
            "stack_trace": "str (dev only)"
        }
    },
    confidence=0.9  # High confidence after validation
)
```

### Pattern 3: Code Pattern Reuse

```python
# Developer stores proven pattern
pattern_id = memory.store_pattern(
    pattern_name="retry_with_backoff",
    pattern_data={
        "code": """
import asyncio
from functools import wraps

def retry_with_backoff(max_retries=3, base_delay=1):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    delay = base_delay * (2 ** attempt)
                    await asyncio.sleep(delay)
        return wrapper
    return decorator
        """,
        "description": "Exponential backoff retry decorator for async functions",
        "usage": "@retry_with_backoff(max_retries=5, base_delay=2)",
        "use_cases": ["API calls", "Database operations", "External services"]
    },
    category="code_pattern",
    tags=["retry", "backoff", "async", "resilience"]
)

# Another developer retrieves and uses pattern
pattern = memory.get_pattern("retry_with_backoff")
if pattern:
    # Pattern usage automatically tracked
    print(f"Retrieved pattern: {pattern['pattern_name']}")
    print(f"Used {pattern['usage_count']} times")
```

### Pattern 4: Error Resolution Learning

```python
# Record error resolution strategy
error_id = memory.store_knowledge(
    topic="connection_pool_exhaustion",
    knowledge={
        "error": "sqlalchemy.exc.TimeoutError: QueuePool limit exceeded",
        "cause": "Connection pool size too small for concurrent requests",
        "solution": "Increase pool_size and max_overflow parameters",
        "code": """
engine = create_engine(
    DATABASE_URL,
    pool_size=20,        # Increased from 5
    max_overflow=40,     # Increased from 10
    pool_timeout=30
)
        """,
        "prevention": "Monitor connection pool metrics in production"
    },
    confidence=0.7,
    category="error_resolution",
    tags=["sqlalchemy", "connection-pool", "performance"]
)

# When similar error occurs, search resolutions
resolutions = memory.search_knowledge(
    query="connection pool timeout",
    category="error_resolution",
    min_confidence=0.5
)

if resolutions:
    print("Similar errors found:")
    for res in resolutions:
        print(f"  {res['topic']}: {res['knowledge']['solution']}")
        memory.record_success(res['id'])  # Track successful resolution
```

## Advanced Features

### Confidence-Based Decision Making

```python
def get_reliable_knowledge(topic: str, min_confidence=0.7):
    """Only return high-confidence knowledge"""
    knowledge = memory.retrieve_knowledge(topic)

    if knowledge and knowledge['confidence'] >= min_confidence:
        return knowledge

    # Fall back to search if exact match not confident enough
    results = memory.search_knowledge(
        query=topic,
        min_confidence=min_confidence,
        limit=1
    )

    return results[0] if results else None
```

### Pattern Popularity Tracking

```python
# Get most used patterns
all_patterns = memory.list_patterns(limit=100)
sorted_patterns = sorted(
    all_patterns,
    key=lambda p: p['usage_count'],
    reverse=True
)

print("Top 10 most used patterns:")
for i, pattern in enumerate(sorted_patterns[:10], 1):
    print(f"{i}. {pattern['pattern_name']}: {pattern['usage_count']} uses")
```

### Knowledge Maintenance

```python
def maintain_knowledge_base():
    """Regular knowledge base maintenance"""

    # 1. Prune low-confidence old entries
    pruned = memory.prune_low_confidence(threshold=0.3, min_age_days=30)
    print(f"Pruned {pruned} low-confidence entries")

    # 2. Get statistics
    stats = memory.get_statistics()
    print(f"Total knowledge: {stats['knowledge']['total_knowledge']}")
    print(f"Avg confidence: {stats['knowledge']['avg_confidence']:.2f}")

    # 3. Identify rarely accessed knowledge
    all_knowledge = memory.list_knowledge(limit=1000)
    rarely_accessed = [
        k for k in all_knowledge
        if k['access_count'] < 5 and k['confidence'] < 0.5
    ]

    print(f"Rarely accessed low-confidence: {len(rarely_accessed)}")

    # 4. Review and update or prune
    for k in rarely_accessed:
        print(f"Review: {k['topic']} (accessed {k['access_count']} times)")
```

## Best Practices

1. **Start with moderate confidence**
```python
# Let usage prove value
memory.store_knowledge(..., confidence=0.5)  # Not 1.0
```

2. **Always record outcomes**
```python
knowledge = memory.retrieve_knowledge("pattern")
if apply_pattern_successfully():
    memory.record_success(knowledge['id'])
else:
    memory.record_failure(knowledge['id'])
```

3. **Use categories consistently**
```python
# Good: Use enums
category=KnowledgeCategory.ARCHITECTURAL_DECISION

# Avoid: String literals (typo-prone)
category="architecutral_decision"
```

4. **Tag thoroughly for search**
```python
tags=["authentication", "security", "jwt", "api", "stateless"]
```

5. **Regular maintenance**
```python
# Weekly or monthly
memory.prune_low_confidence(threshold=0.3, min_age_days=30)
```

## Integration with Other Memory Components

See [examples/distributed-memory.md](../examples/distributed-memory.md) for integration patterns with EpisodicMemory and ContextHints.
