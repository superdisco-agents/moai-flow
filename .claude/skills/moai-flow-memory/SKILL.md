---
name: moai-flow-memory
description: Enterprise distributed memory management for multi-agent swarms with context persistence, semantic knowledge, and episodic history
version: 1.0.0
updated: 2025-11-30
status: active
tools: Read, Grep, Glob
tags: memory, persistence, distributed-systems, knowledge-management, context-hints
---

# MoAI Flow Memory

Enterprise distributed memory management for multi-agent swarms with context persistence, semantic knowledge, and episodic history.

## Quick Reference (30 seconds)

**What is MoAI Flow Memory?**
Four-layer memory architecture enabling intelligent multi-agent coordination:

1. **SwarmDB** - SQLite-based persistent storage for lifecycle events and metrics
2. **SemanticMemory** - Long-term knowledge patterns with confidence scoring
3. **EpisodicMemory** - Event and decision history with temporal context
4. **ContextHints** - Session-level user preferences and workflow patterns

**Core Capabilities**:
- Distributed memory pools across agent swarms
- Cross-session context persistence with TTL
- Confidence-based knowledge pruning (0.3 threshold, 30 days)
- Pattern learning from last 100 tasks
- SQLite backend with thread-safe operations

**Quick Access**:
- SwarmDB architecture → [SwarmDB Module](modules/swarm-db.md)
- Knowledge management → [Semantic Memory Module](modules/semantic-memory.md)
- Event history → [Episodic Memory Module](modules/episodic-memory.md)
- User preferences → [Context Hints Module](modules/context-hints.md)

**Use Cases**:
- Multi-agent workflow coordination
- Cross-session knowledge sharing
- Pattern recognition and learning
- User preference adaptation
- Distributed state management

---

## Implementation Guide (5 minutes)

### 1. SwarmDB - Persistent Storage Foundation

**Purpose**: Thread-safe SQLite storage for agent lifecycle, events, and metrics.

**Schema Architecture** (v2.0.0):
```python
# Core Tables
agent_events       # Lifecycle events (spawn, complete, error)
agent_registry     # Current agent state
session_memory     # Cross-session persistence
task_metrics       # Task performance (Phase 6A)
agent_metrics      # Agent statistics (Phase 6A)
swarm_metrics      # Swarm health (Phase 6A)
```

**Basic Usage**:
```python
from moai_flow.memory import SwarmDB

# Initialize database
db = SwarmDB()  # Defaults to .moai/memory/swarm.db

# Record agent spawn
event_id = db.insert_event({
    "event_type": "spawn",
    "agent_id": "agent-123",
    "agent_type": "expert-backend",
    "timestamp": "2025-11-30T10:00:00",
    "metadata": {"prompt": "Design API", "model": "claude-sonnet-4"}
})

# Register agent
db.register_agent(
    agent_id="agent-123",
    agent_type="expert-backend",
    status="spawned",
    metadata={"prompt": "Design API"}
)

# Update status
db.update_agent_status("agent-123", "complete", duration_ms=3000)
```

**Transaction Safety**:
```python
# Atomic operations
with db.transaction() as conn:
    cursor = conn.cursor()
    cursor.execute("INSERT INTO agent_events ...")
    cursor.execute("UPDATE agent_registry ...")
    # Auto-commit on success, rollback on error
```

**Detailed Reference**: [SwarmDB Module](modules/swarm-db.md)

---

### 2. SemanticMemory - Knowledge Management

**Purpose**: Long-term knowledge storage with confidence-based pruning.

**Knowledge Categories**:
- `adr` - Architectural decisions
- `best_practice` - Best practices
- `code_pattern` - Reusable code patterns
- `error_resolution` - Error fixes
- `workflow` - Workflow patterns
- `convention` - Project conventions

**Confidence Scoring**:
```
Initial:  0.5 (default)
Success:  +0.1 (max 1.0)
Failure:  -0.2 (min 0.0)
Pruning:  <0.3 after 30 days
```

**Basic Usage**:
```python
from moai_flow.memory import SwarmDB, SemanticMemory

db = SwarmDB()
memory = SemanticMemory(db, project_id="moai-adk")

# Store architectural decision
knowledge_id = memory.store_knowledge(
    topic="api_authentication",
    knowledge={
        "decision": "Use JWT with refresh tokens",
        "rationale": "Stateless, scalable",
        "alternatives": ["Session-based", "OAuth2"]
    },
    confidence=0.9,
    category="adr",
    tags=["authentication", "security"]
)

# Search knowledge
results = memory.search_knowledge(
    query="authentication security",
    min_confidence=0.5,
    category="adr"
)

# Update confidence based on success
memory.record_success(knowledge_id)  # +0.1 confidence

# Prune low-confidence entries
pruned = memory.prune_low_confidence(threshold=0.3, min_age_days=30)
```

**Code Patterns**:
```python
# Store reusable pattern
pattern_id = memory.store_pattern(
    pattern_name="api_error_handler",
    pattern_data={
        "code": "try:\n    ...\nexcept Exception as e:\n    ...",
        "description": "Standard API error handling",
        "usage": "Wrap all API endpoints"
    },
    category="error_handling",
    tags=["decorator", "error", "api"]
)

# Retrieve pattern
pattern = memory.get_pattern("api_error_handler")
print(f"Usage count: {pattern['usage_count']}")
```

**Detailed Reference**: [Semantic Memory Module](modules/semantic-memory.md)

---

### 3. EpisodicMemory - Event History

**Purpose**: Temporal event and decision history with outcome tracking.

**Event Types**:
- `command` - /moai:* commands
- `agent_spawn` - Agent spawned
- `agent_complete` - Agent completed
- `decision` - Decision point
- `error` - Error occurred
- `spec_create` - SPEC created
- `impl_complete` - Implementation complete

**Basic Usage**:
```python
from moai_flow.memory import SwarmDB, EpisodicMemory, EventType

db = SwarmDB()
memory = EpisodicMemory(db, project_id="moai-adk")

# Record decision
decision_id = memory.record_decision(
    decision_type="agent_selection",
    options=["expert-backend", "expert-frontend"],
    chosen="expert-backend",
    rationale="API implementation required",
    context={
        "active_spec": "SPEC-001",
        "phase": "implementation",
        "task_type": "api_implementation"
    }
)

# Record outcome
memory.record_outcome(
    decision_id,
    outcome="success",
    metrics={
        "duration_ms": 3000,
        "tests_passed": 10,
        "coverage": 92.5
    }
)

# Find similar episodes
similar = memory.find_similar_episodes(
    current_context={
        "active_spec": "SPEC-001",
        "phase": "implementation"
    },
    limit=5
)
```

**Outcome Statistics**:
```python
# Analyze decision success rates
stats = memory.get_outcome_statistics("agent_selection")
print(f"Success rate: {stats['success_rate']:.1f}%")
print(f"Total decisions: {stats['total_decisions']}")
print(f"Avg duration: {stats['avg_duration_ms']:.0f}ms")
print(f"Outcomes: {stats['outcome_counts']}")
```

**Detailed Reference**: [Episodic Memory Module](modules/episodic-memory.md)

---

### 4. ContextHints - User Preferences

**Purpose**: Session-level adaptive assistance through preference tracking.

**Preference Categories**:
- `communication` - Verbose, concise, balanced
- `workflow` - TDD, doc-first, impl-first
- `validation` - Strict, moderate, relaxed
- `expertise` - Beginner, intermediate, expert

**Basic Usage**:
```python
from moai_flow.memory import SwarmDB, ContextHints

db = SwarmDB()
hints = ContextHints(db, session_id="session-123")

# Set preferences
hints.set_preference("communication", "concise")
hints.set_preference("workflow", "tdd")
hints.set_expertise_level("expert")

# Record task pattern
hints.record_task_pattern("implementation", {
    "spec_id": "SPEC-001",
    "agents_used": ["expert-backend", "manager-tdd"],
    "success": True,
    "duration_ms": 5000,
    "tools_used": ["expert-backend", "manager-tdd"]
})

# Get suggestions
next_action = hints.suggest_next_action()
# "Run /moai:3-sync to document recent implementation"

# Analyze workflow patterns
analysis = hints.analyze_workflow_patterns()
print(f"Success rates: {analysis['success_rate']}")
print(f"Common sequences: {analysis['common_sequences']}")
```

**Tool Preferences**:
```python
# Track tool usage
hints.record_tool_usage("expert-backend")

# Get most used tools
top_tools = hints.get_most_used_tools(3)
# [('expert-backend', 15), ('manager-tdd', 12), ...]
```

**Detailed Reference**: [Context Hints Module](modules/context-hints.md)

---

## Advanced Implementation (10+ minutes)

### Cross-Module Integration

**Pattern 1: Knowledge-Backed Decision Making**
```python
from moai_flow.memory import SwarmDB, SemanticMemory, EpisodicMemory

db = SwarmDB()
semantic = SemanticMemory(db, project_id="moai-adk")
episodic = EpisodicMemory(db, project_id="moai-adk")

# Check semantic memory for similar decisions
knowledge = semantic.search_knowledge("api authentication", min_confidence=0.7)

# Record decision with semantic context
decision_id = episodic.record_decision(
    decision_type="architecture",
    options=["JWT", "Session", "OAuth2"],
    chosen="JWT",
    rationale=f"Based on ADR: {knowledge[0]['topic']}"
)

# Update confidence on success
if implementation_successful:
    semantic.record_success(knowledge[0]['id'])
    episodic.record_outcome(decision_id, "success")
```

**Pattern 2: Adaptive Workflow**
```python
from moai_flow.memory import SwarmDB, ContextHints, EpisodicMemory

db = SwarmDB()
hints = ContextHints(db, session_id="session-123")
episodic = EpisodicMemory(db, project_id="moai-adk")

# Analyze past workflow patterns
workflow_stats = episodic.get_outcome_statistics("workflow_choice")
tdd_success = workflow_stats['outcome_counts'].get('tdd_success', 0)

# Adapt workflow preference
if tdd_success > 5:
    hints.set_preference("workflow", "tdd")
    print("TDD workflow recommended based on success history")

# Suggest next action
suggestion = hints.suggest_next_action()
```

**Pattern 3: Distributed Memory Pools**
```python
# Multiple agents sharing knowledge
agents = ["agent-001", "agent-002", "agent-003"]
shared_memory = SemanticMemory(db, project_id="shared-pool")

# Agent 001 stores pattern
shared_memory.store_pattern(
    pattern_name="error_handler",
    pattern_data={"code": "...", "usage": "..."}
)

# Agent 002 retrieves pattern
pattern = shared_memory.get_pattern("error_handler")
print(f"Retrieved from shared pool: {pattern['pattern_name']}")

# Agent 003 records success
shared_memory.record_success(pattern['id'])
```

### Performance Optimization

**Pattern 1: TTL-Based Memory**
```python
# Store temporary context with TTL
hints.set_preference(
    "temp_setting",
    {"enabled": True, "mode": "fast"},
    ttl_hours=24  # Auto-expires after 24 hours
)
```

**Pattern 2: Batch Operations**
```python
# Batch insert events
with db.transaction() as conn:
    cursor = conn.cursor()
    for event in batch_events:
        cursor.execute("INSERT INTO agent_events ...")
    # Single commit for all events
```

**Pattern 3: Maintenance Automation**
```python
# Daily cleanup job
def daily_maintenance():
    db = SwarmDB()
    semantic = SemanticMemory(db, project_id="moai-adk")
    episodic = EpisodicMemory(db, project_id="moai-adk")

    # Prune low-confidence knowledge
    pruned_knowledge = semantic.prune_low_confidence(threshold=0.3)

    # Cleanup old episodes
    pruned_episodes = episodic.cleanup_old_episodes(days=90)

    # Cleanup old events
    pruned_events = db.cleanup_old_events(days=30)

    # Vacuum database
    db.vacuum()

    print(f"Maintenance complete: {pruned_knowledge} knowledge, "
          f"{pruned_episodes} episodes, {pruned_events} events pruned")
```

### Error Handling

**Pattern 1: Graceful Degradation**
```python
def get_knowledge_with_fallback(topic: str):
    try:
        knowledge = semantic.retrieve_knowledge(topic)
        if knowledge:
            return knowledge
    except Exception as e:
        logger.error(f"Semantic memory error: {e}")

    # Fallback to default knowledge
    return DEFAULT_KNOWLEDGE.get(topic)
```

**Pattern 2: Transaction Rollback**
```python
try:
    with db.transaction() as conn:
        # Complex multi-step operation
        cursor = conn.cursor()
        cursor.execute("INSERT INTO semantic_knowledge ...")
        cursor.execute("INSERT INTO episodes ...")
        cursor.execute("UPDATE agent_registry ...")
        # Auto-commit on success
except Exception as e:
    # Auto-rollback on error
    logger.error(f"Transaction failed: {e}")
    raise
```

---

## Works Well With

**Skills**:
- **moai-flow-agents** - Agent lifecycle with memory integration
- **moai-flow-orchestration** - Workflow coordination with state persistence
- **moai-foundation-core** - Token optimization with context caching
- **moai-cc-memory** - Claude Code memory patterns

**Agents**:
- **workflow-spec** - SPEC generation with knowledge lookup
- **workflow-tdd** - TDD cycles with pattern reuse
- **core-quality** - Quality validation with historical metrics
- **workflow-docs** - Documentation with semantic references

**Commands**:
- `/moai:1-plan` - Store SPEC decisions in semantic memory
- `/moai:2-run` - Track implementation episodes
- `/moai:3-sync` - Document knowledge patterns
- `/moai:9-feedback` - Learn from feedback history

---

## Configuration

**Database Location**:
```python
# Default: .moai/memory/swarm.db
db = SwarmDB()  # Uses default path

# Custom location
from pathlib import Path
db = SwarmDB(db_path=Path("/custom/path/swarm.db"))
```

**Memory Limits**:
```python
# Task history (ContextHints)
MAX_TASK_HISTORY = 100  # Last 100 tasks

# Confidence threshold (SemanticMemory)
PATTERN_CONFIDENCE_THRESHOLD = 0.7
PRUNE_THRESHOLD = 0.3
MIN_AGE_DAYS = 30

# Suggestion decay (ContextHints)
SUGGESTION_DECAY_HOURS = 24
```

**Maintenance Schedule**:
```bash
# Recommended maintenance intervals
Daily:   Cleanup old events (30 days)
Weekly:  Prune low-confidence knowledge
Monthly: Vacuum database, analyze patterns
```

---

## Quick Decision Matrix

| Scenario | Component | Method |
|----------|-----------|--------|
| Agent lifecycle | SwarmDB | insert_event(), register_agent() |
| Knowledge storage | SemanticMemory | store_knowledge(), store_pattern() |
| Decision tracking | EpisodicMemory | record_decision(), record_outcome() |
| User preferences | ContextHints | set_preference(), record_task_pattern() |
| Pattern lookup | SemanticMemory | search_knowledge(), get_pattern() |
| History analysis | EpisodicMemory | find_similar_episodes(), get_outcome_statistics() |
| Workflow adaptation | ContextHints | suggest_next_action(), analyze_workflow_patterns() |

**Module Deep Dives**:
- [SwarmDB Architecture](modules/swarm-db.md)
- [Semantic Memory Patterns](modules/semantic-memory.md)
- [Episodic Memory Analysis](modules/episodic-memory.md)
- [Context Hints Adaptation](modules/context-hints.md)

**Working Examples**: [examples.md](examples.md)

---

**Version**: 1.0.0
**Last Updated**: 2025-11-30
**Status**: Active (497 lines, within 500-line limit)
