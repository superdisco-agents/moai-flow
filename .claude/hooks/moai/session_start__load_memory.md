# SessionStart Hook: Load Memory and Context Hints

## Overview

This hook loads context hints and recent episodic memory at session start to provide continuity between Claude Code sessions. It integrates with SwarmDB to retrieve user preferences, recent activity, and session state.

## Purpose

- **Memory Continuity**: Load previous session context for seamless continuation
- **User Preferences**: Apply stored communication style, workflow, and expertise level
- **Smart Suggestions**: Recommend next actions based on last session's state
- **Performance**: Fast parallel loading with 2-second timeout
- **Resilience**: Graceful degradation if memory unavailable

## Memory Sources

### 1. Context Hints (User Preferences)

Stored in SwarmDB `session_memory` table with `memory_type='context_hint'`:

```json
{
  "communication": "concise" | "detailed" | "technical",
  "workflow": "tdd" | "agile" | "waterfall",
  "expertise": "beginner" | "intermediate" | "advanced"
}
```

### 2. Episodic Memory (Recent Activity)

Loaded from SwarmDB `agent_events` table (last 24 hours):

```json
{
  "event_type": "spawn" | "complete" | "error",
  "agent_id": "unique-agent-id",
  "agent_type": "expert-backend",
  "timestamp": "2025-11-29T16:00:00",
  "metadata": {
    "prompt": "Design REST API",
    "duration_ms": 5000
  }
}
```

### 3. Semantic Knowledge (Long-term Patterns)

Stored in SwarmDB `session_memory` table with `memory_type='semantic'`:

```json
{
  "topic": "authentication",
  "pattern": "JWT",
  "confidence": 0.9,
  "last_used": "2025-11-29T16:00:00"
}
```

### 4. Session State (Last Session)

Loaded from `.moai/memory/last-session-state.json`:

```json
{
  "last_updated": "2025-11-29T14:49:01.421903",
  "current_branch": "feature/SPEC-001",
  "uncommitted_changes": true,
  "uncommitted_files": 3,
  "specs_in_progress": ["SPEC-001", "SPEC-002"]
}
```

## Output Format

### System Message

The hook generates a user-friendly summary displayed at session start:

```
💡 Your Preferences:
   Communication: concise
   Workflow: tdd
   Expertise: intermediate

📝 Recent Activity: 5 events in last 24h
   Agents spawned: 3
   Tasks completed: 2
   Errors encountered: 0

📌 Last Session:
   Branch: feature/SPEC-001
   Uncommitted changes: 3 files
   In Progress: SPEC-001, SPEC-002

🎯 Suggested Next Steps:
   1. Review and commit uncommitted changes
   2. Continue SPEC-001 implementation
   3. Continue SPEC-002 implementation
```

### Session Context File

Hook saves context to `.moai/memory/session-context.json` for other hooks:

```json
{
  "session_id": "session-20251129-160000",
  "loaded_at": "2025-11-29T16:00:00",
  "context": {
    "user_preferences": {...},
    "recent_episodes": [...],
    "relevant_knowledge": [...],
    "suggested_next_actions": [...]
  }
}
```

## Performance

- **Target**: Complete within 2 seconds
- **Parallel Loading**: Uses ThreadPoolExecutor (4 workers)
- **Timeout**: 2-second hard limit with graceful degradation
- **Cache**: Reuses existing SwarmDB connections

### Benchmark Results

| Operation | Time | Notes |
|-----------|------|-------|
| SwarmDB connection | ~5ms | First connection only |
| Load context hints | ~10ms | Single query |
| Load episodes (24h) | ~15ms | Index-optimized |
| Load semantic knowledge | ~10ms | Top 10 entries |
| Load session state | ~5ms | File read |
| Parallel total | ~50ms | With ThreadPoolExecutor |
| Format output | ~5ms | String concatenation |
| **Total** | **~60ms** | Well under 2s limit |

## Graceful Degradation

The hook handles failures gracefully:

### SwarmDB Unavailable

```python
# Returns empty context, continues session
{
  "continue": True,
  "systemMessage": ""
}
```

### Individual Query Timeout

```python
# Skips failed query, loads other sources
context["recent_episodes"] = []  # Failed query
context["user_preferences"] = {...}  # Succeeded
```

### Timeout (>2s)

```python
# Returns minimal response
{
  "continue": True,
  "systemMessage": "⚠️ Memory load timeout - continuing without context"
}
```

## Integration Points

### With SessionEnd Hook

SessionEnd saves state → SessionStart loads state:

```
SessionEnd: Saves to .moai/memory/last-session-state.json
SessionStart: Loads from .moai/memory/last-session-state.json
```

### With SwarmDB

All agent lifecycle events automatically logged:

```python
# agent_lifecycle.py hooks spawn/complete/error events
db.insert_event({
    "event_type": "spawn",
    "agent_id": agent_id,
    "agent_type": "expert-backend",
    ...
})

# SessionStart loads these events
episodes = load_recent_episodes(db, hours=24)
```

### With Other Hooks

Session context available to all hooks via file:

```python
# Any hook can read session context
context_file = Path(".moai/memory/session-context.json")
context = json.loads(context_file.read_text())
user_prefs = context["context"]["user_preferences"]
```

## Configuration

No direct configuration required. Uses:

- **SwarmDB path**: `.moai/memory/swarm.db` (auto-created)
- **Session state path**: `.moai/memory/last-session-state.json`
- **Context path**: `.moai/memory/session-context.json`

### User Preferences Setup

Preferences can be set via SwarmDB:

```python
from moai_flow.memory.swarm_db import SwarmDB

db = SwarmDB()
db.store_memory(
    session_id="global",
    memory_type="context_hint",
    key="user_preferences",
    value={
        "communication": "detailed",
        "workflow": "agile",
        "expertise": "advanced"
    }
)
```

## Testing

Comprehensive test suite in `tests/hooks/test_session_start_load_memory.py`:

```bash
# Run all tests
python3 -m pytest tests/hooks/test_session_start_load_memory.py -v

# Run specific test
python3 -m pytest tests/hooks/test_session_start_load_memory.py::test_load_context_hints -v

# Test performance
python3 -m pytest tests/hooks/test_session_start_load_memory.py::test_hook_performance_under_2_seconds -v
```

### Test Coverage

- ✅ Context hints loading
- ✅ Episodic memory retrieval
- ✅ Semantic knowledge loading
- ✅ Session state loading
- ✅ Next action suggestions
- ✅ Graceful degradation
- ✅ Timeout handling
- ✅ Invalid JSON handling
- ✅ Performance under 2s
- ✅ Session context file creation

## Troubleshooting

### No Memory Summary Displayed

**Cause**: SwarmDB empty or unavailable

**Solution**: Check if SwarmDB exists and has data:

```bash
sqlite3 .moai/memory/swarm.db "SELECT COUNT(*) FROM agent_events;"
```

### Timeout Warnings

**Cause**: Hook taking longer than 2 seconds

**Solution**: Check SwarmDB performance:

```bash
# Vacuum database to optimize
sqlite3 .moai/memory/swarm.db "VACUUM;"

# Check database size
ls -lh .moai/memory/swarm.db
```

### Missing Preferences

**Cause**: User preferences not set

**Solution**: Initialize preferences:

```python
python3 -c "
from moai_flow.memory.swarm_db import SwarmDB
db = SwarmDB()
db.store_memory(
    session_id='global',
    memory_type='context_hint',
    key='user_preferences',
    value={'communication': 'concise', 'workflow': 'tdd', 'expertise': 'intermediate'}
)
print('Preferences initialized')
"
```

## Future Enhancements

### Planned Features

1. **Semantic Search**: Vector-based knowledge retrieval
2. **Pattern Recognition**: Auto-detect user workflow patterns
3. **Context Ranking**: Prioritize most relevant context
4. **Memory Compression**: Summarize old episodes
5. **Cross-Project Memory**: Share knowledge across projects

### Integration Opportunities

- **Claude Context Protocol**: Integrate with Claude's native context
- **MCP Memory Server**: Use MCP for persistent memory
- **Embeddings**: Add semantic search via embeddings
- **RAG**: Retrieve-augment-generate for context

## Architecture

```
SessionStart Hook
├── SwarmDB Connection
│   ├── Context Hints (user preferences)
│   ├── Episodic Memory (recent events)
│   └── Semantic Knowledge (patterns)
├── Session State File
│   └── Last session's unfinished tasks
├── Parallel Loading (ThreadPoolExecutor)
│   ├── load_context_hints()
│   ├── load_recent_episodes()
│   ├── load_semantic_knowledge()
│   └── load_last_session_state()
├── Context Building
│   ├── Combine all memory sources
│   └── Generate action suggestions
├── Output Formatting
│   ├── User-friendly summary
│   └── Save to session-context.json
└── Graceful Degradation
    ├── Timeout handling
    ├── Missing data handling
    └── Error recovery
```

## Related Documentation

- **SwarmDB**: `moai-flow/memory/swarm_db.py`
- **Agent Lifecycle Hooks**: `moai-flow/hooks/agent_lifecycle.py`
- **SessionEnd Hook**: `.claude/hooks/moai/session_end__save_state.py`
- **Memory Architecture**: `.moai/memory/README.md`

## Version History

- **v1.0.0** (2025-11-29): Initial implementation
  - SwarmDB integration
  - Parallel loading
  - Graceful degradation
  - Comprehensive test suite

---

**Last Updated**: 2025-11-29
**Author**: MoAI-ADK Team
**Status**: Production Ready
