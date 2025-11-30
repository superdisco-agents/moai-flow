# MoAI-Flow Memory Module

Cross-session persistent memory system for multi-agent coordination.

## Overview

The Memory module provides three types of persistent storage:

1. **SemanticMemory**: Long-term knowledge and patterns
2. **EpisodicMemory**: Event and decision history (future)
3. **ContextHints**: Session hints and user preferences (future)

All memory types are backed by **SwarmDB**, a thread-safe SQLite wrapper.

---

## SemanticMemory

Long-term knowledge storage with confidence-based scoring and automatic pruning.

### Features

- **Knowledge Storage**: Store architectural decisions, best practices, conventions
- **Confidence Scoring**: Automatic confidence adjustment based on success/failure
- **Full-Text Search**: Pattern-based search across all knowledge
- **Code Patterns**: Reusable code templates with usage tracking
- **Project Isolation**: Knowledge scoped to specific projects
- **Automatic Pruning**: Remove low-confidence knowledge after 30 days

### Knowledge Categories

```python
from moai_flow.memory.semantic_memory import KnowledgeCategory

KnowledgeCategory.ARCHITECTURAL_DECISION  # ADRs
KnowledgeCategory.BEST_PRACTICE          # Best practices
KnowledgeCategory.CODE_PATTERN           # Reusable code templates
KnowledgeCategory.ERROR_RESOLUTION       # Error solutions
KnowledgeCategory.WORKFLOW_PATTERN       # Workflow templates
KnowledgeCategory.CONVENTION             # Project conventions
KnowledgeCategory.TOOL_USAGE             # Tool usage patterns
KnowledgeCategory.PERFORMANCE_PATTERN    # Performance optimizations
```

### Confidence Scoring System

| Event | Confidence Change | Min | Max |
|-------|-------------------|-----|-----|
| New knowledge | 0.5 (default) | 0.0 | 1.0 |
| Successful use | +0.1 | 0.0 | 1.0 |
| Failed use | -0.2 | 0.0 | 1.0 |
| Pruning threshold | < 0.3 after 30 days | - | - |

### Quick Start

```python
from moai_flow.memory.swarm_db import SwarmDB
from moai_flow.memory.semantic_memory import SemanticMemory, KnowledgeCategory

# Initialize
db = SwarmDB()
memory = SemanticMemory(db, project_id="my-project")

# Store architectural decision
adr_id = memory.store_knowledge(
    topic="api_authentication",
    knowledge={
        "decision": "Use JWT with refresh tokens",
        "rationale": "Stateless, scalable",
        "alternatives": ["Session-based", "OAuth2"]
    },
    confidence=0.9,
    category=KnowledgeCategory.ARCHITECTURAL_DECISION,
    tags=["auth", "security", "api"]
)

# Retrieve knowledge
knowledge = memory.retrieve_knowledge("api_authentication")
print(f"Confidence: {knowledge['confidence']}")

# Search knowledge
results = memory.search_knowledge("authentication security", min_confidence=0.5)
for result in results:
    print(f"{result['topic']}: {result['confidence']}")

# Record success (increases confidence by +0.1)
memory.record_success(adr_id)

# Record failure (decreases confidence by -0.2)
memory.record_failure(adr_id)

# Cleanup
db.close()
```

### API Reference

#### Knowledge Operations

##### `store_knowledge(topic, knowledge, confidence=0.5, category=None, tags=None) -> str`

Store new knowledge with metadata.

**Args:**
- `topic` (str): Knowledge topic/identifier
- `knowledge` (dict): Knowledge data dictionary
- `confidence` (float): Initial confidence score (0.0-1.0)
- `category` (str): Knowledge category (default: BEST_PRACTICE)
- `tags` (list): Optional tags for classification

**Returns:**
- `str`: Knowledge ID

**Example:**
```python
knowledge_id = memory.store_knowledge(
    topic="error_handling_pattern",
    knowledge={
        "pattern": "try-except-log-reraise",
        "usage": "All API endpoints"
    },
    confidence=0.8,
    category=KnowledgeCategory.CODE_PATTERN,
    tags=["error", "api"]
)
```

##### `retrieve_knowledge(topic) -> Optional[Dict]`

Retrieve knowledge by exact topic match.

**Args:**
- `topic` (str): Knowledge topic

**Returns:**
- `dict`: Knowledge dictionary with metadata, or None

**Example:**
```python
knowledge = memory.retrieve_knowledge("error_handling_pattern")
if knowledge:
    print(knowledge['confidence'])
    print(knowledge['knowledge'])
```

##### `search_knowledge(query, limit=10, min_confidence=0.3, category=None) -> List[Dict]`

Search across all knowledge using pattern matching.

**Args:**
- `query` (str): Search query string
- `limit` (int): Maximum results to return
- `min_confidence` (float): Minimum confidence threshold
- `category` (str): Optional category filter

**Returns:**
- `list`: List of matching knowledge dictionaries

**Example:**
```python
results = memory.search_knowledge(
    query="authentication",
    min_confidence=0.5,
    category=KnowledgeCategory.ARCHITECTURAL_DECISION,
    limit=10
)
```

##### `list_knowledge(category=None, min_confidence=0.0, limit=100) -> List[Dict]`

List all knowledge, optionally filtered.

**Args:**
- `category` (str): Optional category filter
- `min_confidence` (float): Minimum confidence threshold
- `limit` (int): Maximum results

**Returns:**
- `list`: List of knowledge dictionaries

##### `update_knowledge(knowledge_id, knowledge=None, confidence=None, tags=None) -> bool`

Update existing knowledge.

**Args:**
- `knowledge_id` (str): Knowledge ID to update
- `knowledge` (dict): Optional new knowledge data
- `confidence` (float): Optional new confidence score
- `tags` (list): Optional new tags

**Returns:**
- `bool`: True if updated, False if not found

#### Confidence Management

##### `update_confidence(knowledge_id, new_confidence) -> None`

Directly update confidence score.

**Args:**
- `knowledge_id` (str): Knowledge ID
- `new_confidence` (float): New confidence score (0.0-1.0)

##### `record_success(knowledge_id) -> None`

Record successful use of knowledge (increases confidence by +0.1).

##### `record_failure(knowledge_id) -> None`

Record failed use of knowledge (decreases confidence by -0.2).

##### `prune_low_confidence(threshold=0.3, min_age_days=30) -> int`

Remove low-confidence knowledge that hasn't been useful.

**Args:**
- `threshold` (float): Confidence threshold below which to prune
- `min_age_days` (int): Minimum age in days before pruning

**Returns:**
- `int`: Number of entries pruned

**Example:**
```python
pruned = memory.prune_low_confidence(threshold=0.3, min_age_days=30)
print(f"Pruned {pruned} low-confidence entries")
```

#### Code Pattern Operations

##### `store_pattern(pattern_name, pattern_data, category=None, confidence=0.5, tags=None) -> str`

Store reusable code pattern.

**Args:**
- `pattern_name` (str): Unique pattern identifier
- `pattern_data` (dict): Pattern data (code, description, usage)
- `category` (str): Pattern category
- `confidence` (float): Initial confidence score
- `tags` (list): Optional tags

**Returns:**
- `str`: Pattern ID

**Example:**
```python
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
```

##### `get_pattern(pattern_name) -> Optional[Dict]`

Retrieve code pattern by name (automatically tracks usage).

##### `list_patterns(category=None, limit=100) -> List[Dict]`

List all code patterns.

#### Statistics

##### `get_statistics() -> Dict`

Get semantic memory statistics.

**Returns:**
- `dict`: Statistics dictionary with knowledge, patterns, and category breakdown

**Example:**
```python
stats = memory.get_statistics()
print(f"Total knowledge: {stats['knowledge']['total_knowledge']}")
print(f"Avg confidence: {stats['knowledge']['avg_confidence']:.2f}")
print(f"Total patterns: {stats['patterns']['total_patterns']}")
print(f"Categories: {stats['categories']}")
```

---

## SwarmDB

Thread-safe SQLite wrapper for persistent storage.

### Features

- **Thread-safe**: Connection pooling per thread
- **Transaction support**: Context manager for ACID transactions
- **Agent lifecycle tracking**: Spawn, complete, error events
- **Agent registry**: Current/active agent tracking
- **Session memory**: Cross-session memory storage
- **Automatic cleanup**: Old event pruning and vacuum

### Quick Start

```python
from moai_flow.memory.swarm_db import SwarmDB
from datetime import datetime

# Initialize
db = SwarmDB()  # Defaults to .moai/memory/swarm.db

# Insert agent event
event_id = db.insert_event({
    "event_type": "spawn",
    "agent_id": "agent-123",
    "agent_type": "expert-backend",
    "timestamp": datetime.now().isoformat(),
    "metadata": {"prompt": "Design REST API"}
})

# Register agent
db.register_agent(
    agent_id="agent-123",
    agent_type="expert-backend",
    status="spawned",
    metadata={"prompt": "Design REST API"}
)

# Query events
events = db.get_events(agent_id="agent-123", limit=10)

# Update agent status
db.update_agent_status("agent-123", "complete", duration_ms=1500)

# Get active agents
active = db.get_active_agents()

# Cleanup
db.cleanup_old_events(days=30)
db.close()
```

---

## Project Structure

```
moai-flow/memory/
├── swarm_db.py          # SQLite wrapper
├── semantic_memory.py   # Long-term knowledge storage
├── episodic_memory.py   # Event history (future)
├── context_hints.py     # Session hints (future)
└── __init__.py
```

---

## Database Schema

### SwarmDB Tables

- `agent_events`: Agent lifecycle events (spawn, complete, error)
- `agent_registry`: Current/active agent tracking
- `session_memory`: Cross-session memory storage
- `schema_info`: Schema version tracking

### SemanticMemory Tables

- `semantic_knowledge`: Long-term knowledge storage
- `code_patterns`: Reusable code patterns
- `semantic_search`: Full-text search index (future enhancement)

---

## Testing

```bash
# Run all tests
python3 -m pytest tests/moai-flow/memory/test_semantic_memory.py -v

# Run specific test class
python3 -m pytest tests/moai-flow/memory/test_semantic_memory.py::TestConfidenceScoring -v

# Run with coverage
python3 -m pytest tests/moai-flow/memory/test_semantic_memory.py --cov=moai_flow.memory
```

---

## Usage Examples

### Example 1: Store and Retrieve ADR

```python
from moai_flow.memory.swarm_db import SwarmDB
from moai_flow.memory.semantic_memory import SemanticMemory, KnowledgeCategory

db = SwarmDB()
memory = SemanticMemory(db, project_id="my-app")

# Store architectural decision
adr_id = memory.store_knowledge(
    topic="database_choice",
    knowledge={
        "decision": "PostgreSQL 16",
        "rationale": "ACID compliance, JSON support, performance",
        "alternatives_considered": ["MySQL", "MongoDB"],
        "trade_offs": {
            "pros": ["Mature", "Feature-rich", "Strong consistency"],
            "cons": ["More complex", "Requires more resources"]
        }
    },
    confidence=0.9,
    category=KnowledgeCategory.ARCHITECTURAL_DECISION,
    tags=["database", "postgresql", "adr"]
)

# Retrieve later
adr = memory.retrieve_knowledge("database_choice")
print(f"Decision: {adr['knowledge']['decision']}")
print(f"Confidence: {adr['confidence']}")
```

### Example 2: Track Knowledge Evolution

```python
# Store initial knowledge with medium confidence
pattern_id = memory.store_knowledge(
    topic="caching_strategy",
    knowledge={"pattern": "Redis with 5-minute TTL"},
    confidence=0.5,
    category=KnowledgeCategory.PERFORMANCE_PATTERN
)

# Use pattern successfully
memory.record_success(pattern_id)  # Confidence: 0.5 -> 0.6

# Use again successfully
memory.record_success(pattern_id)  # Confidence: 0.6 -> 0.7

# Pattern fails in production
memory.record_failure(pattern_id)  # Confidence: 0.7 -> 0.5

# Update pattern based on learnings
memory.update_knowledge(
    pattern_id,
    knowledge={"pattern": "Redis with adaptive TTL (1-10 min)"},
    confidence=0.8
)
```

### Example 3: Search and Filter

```python
# Search for security-related knowledge
security_results = memory.search_knowledge(
    query="security authentication",
    min_confidence=0.6,
    limit=10
)

# List all ADRs
adrs = memory.list_knowledge(
    category=KnowledgeCategory.ARCHITECTURAL_DECISION,
    min_confidence=0.5
)

# Get high-confidence patterns
patterns = memory.list_patterns(
    category=KnowledgeCategory.CODE_PATTERN
)
```

### Example 4: Automatic Pruning

```python
# Prune low-confidence knowledge older than 30 days
pruned = memory.prune_low_confidence(threshold=0.3, min_age_days=30)
print(f"Pruned {pruned} low-confidence entries")

# Get statistics after pruning
stats = memory.get_statistics()
print(f"Remaining knowledge: {stats['knowledge']['total_knowledge']}")
print(f"Average confidence: {stats['knowledge']['avg_confidence']:.2f}")
```

---

## Integration with MoAI-Flow

SemanticMemory integrates with MoAI-Flow agents to provide:

1. **Cross-session learning**: Agents learn from past decisions
2. **Pattern reuse**: Reusable code patterns across sessions
3. **Decision tracking**: ADRs preserved across sessions
4. **Confidence evolution**: Knowledge quality improves over time
5. **Automatic cleanup**: Low-value knowledge removed automatically

---

## Future Enhancements

- **EpisodicMemory**: Store decision history and event sequences
- **ContextHints**: Session-specific user preferences
- **Vector embeddings**: Semantic similarity search
- **Knowledge graphs**: Relationship mapping between knowledge
- **Multi-project knowledge sharing**: Shared patterns across projects
- **Export/import**: Knowledge backup and transfer

---

## Version History

- **1.0.0** (2025-11-29): Initial implementation
  - SemanticMemory with confidence scoring
  - SwarmDB SQLite wrapper
  - Pattern-based search
  - Automatic pruning
  - 28 passing unit tests

---

## License

MIT License - Part of MoAI-ADK
