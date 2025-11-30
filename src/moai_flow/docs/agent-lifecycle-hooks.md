# AgentLifecycle Hooks - Documentation

## Overview

AgentLifecycle hooks provide comprehensive tracking of agent spawn, completion, and error events within the MoAI-ADK multi-agent system. This infrastructure integrates with `.claude/hooks/moai/` state tracking and provides persistent storage via SwarmDB.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Agent Task Execution                      │
│                     (via Task() calls)                       │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              AgentLifecycle Hook Functions                   │
│  ┌──────────────┬──────────────────┬────────────────────┐  │
│  │ on_agent_    │ on_agent_        │ on_agent_error()   │  │
│  │ spawn()      │ complete()       │                    │  │
│  └──────┬───────┴─────────┬────────┴──────────┬─────────┘  │
└─────────┼─────────────────┼───────────────────┼────────────┘
          │                 │                   │
          ▼                 ▼                   ▼
┌─────────────────────────────────────────────────────────────┐
│                  AgentRegistry (In-Memory)                   │
│            Thread-safe agent state tracking                  │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
        ▼                         ▼
┌───────────────────┐   ┌──────────────────────────┐
│  SwarmDB (SQLite) │   │ File Logger (.moai/logs) │
│  - agent_events   │   │ - agent_lifecycle.log    │
│  - agent_registry │   │ - agent_lifecycle_*.jsonl│
│  - session_memory │   └──────────────────────────┘
└───────────────────┘
        │
        ▼
┌───────────────────────────────────────────────────────────┐
│      HookStateManager Integration (Optional)               │
│      (.claude/hooks/moai/lib/state_tracking.py)           │
└───────────────────────────────────────────────────────────┘
```

## Components

### 1. Hook Functions (Public API)

#### `on_agent_spawn(agent_id, agent_type, metadata)`

Called when a new agent is spawned via `Task()`.

**Parameters:**
- `agent_id` (str): Unique agent identifier (UUID)
- `agent_type` (str): Agent subagent_type (e.g., "expert-backend", "manager-tdd")
- `metadata` (dict, optional): Additional spawn metadata
  - `prompt`: Task prompt string
  - `model`: Model name (e.g., "claude-sonnet-4")
  - `parent_agent_id`: Parent agent ID for nested spawns
  - `priority`: Task priority level
  - Custom fields as needed

**Example:**
```python
from moai_flow.hooks.agent_lifecycle import on_agent_spawn

on_agent_spawn(
    agent_id="a1b2c3d4-e5f6-7890",
    agent_type="expert-backend",
    metadata={
        "prompt": "Design REST API for authentication",
        "model": "claude-sonnet-4",
        "parent_agent_id": None,
        "priority": 1
    }
)
```

#### `on_agent_complete(agent_id, result, duration_ms)`

Called when an agent completes its task.

**Parameters:**
- `agent_id` (str): Agent identifier
- `result` (Any): Agent result/report (dict, str, or any serializable type)
- `duration_ms` (int): Execution time in milliseconds

**Example:**
```python
from moai_flow.hooks.agent_lifecycle import on_agent_complete

on_agent_complete(
    agent_id="a1b2c3d4-e5f6-7890",
    result={
        "status": "success",
        "files_created": ["routes.py", "models.py"],
        "endpoints_designed": 5
    },
    duration_ms=15230
)
```

#### `on_agent_error(agent_id, error)`

Called when an agent encounters an error.

**Parameters:**
- `agent_id` (str): Agent identifier
- `error` (Exception): Exception that occurred

**Example:**
```python
from moai_flow.hooks.agent_lifecycle import on_agent_error

try:
    # Agent task execution
    result = execute_agent_task()
except Exception as e:
    on_agent_error(agent_id="a1b2c3d4-e5f6-7890", error=e)
    raise
```

### 2. Event Schema

All lifecycle events follow a consistent schema:

```python
{
    "event_type": "spawn" | "complete" | "error",
    "agent_id": str,              # UUID
    "agent_type": str,            # e.g., "expert-backend"
    "timestamp": str,             # ISO8601 format
    "metadata": {                 # Event-specific metadata
        # For spawn:
        "prompt": str,
        "model": str,
        "parent_agent_id": str,
        "priority": int,

        # For complete:
        "duration_ms": int,
        "result_type": str,
        "result_summary": str,

        # For error:
        "error_type": str,
        "error_message": str,
        "traceback_preview": str
    }
}
```

### 3. AgentRegistry

In-memory thread-safe registry tracking active agents.

**Methods:**
- `register_spawn(agent_id, agent_type, metadata)`: Register agent spawn
- `update_complete(agent_id, result, duration_ms)`: Update to complete status
- `update_error(agent_id, error)`: Update to error status
- `get_agent(agent_id)`: Get agent information
- `get_active_agents()`: Get list of active agents
- `cleanup_old_agents(max_age_hours)`: Remove old agents

**Example:**
```python
from moai_flow.hooks.agent_lifecycle import get_agent_registry

registry = get_agent_registry()
active_agents = registry.get_active_agents()

for agent in active_agents:
    print(f"Agent: {agent['agent_id']} ({agent['agent_type']}) - {agent['status']}")
```

### 4. SwarmDB Integration

SQLite-based persistent storage for agent events and registry.

**Tables:**
- `agent_events`: All lifecycle events (spawn, complete, error)
- `agent_registry`: Current agent state and metadata
- `session_memory`: Cross-session memory (future integration)

**Example:**
```python
from moai_flow.memory.swarm_db import SwarmDB

db = SwarmDB()

# Insert event
event_id = db.insert_event({
    "event_type": "spawn",
    "agent_id": "a1b2c3d4",
    "agent_type": "expert-backend",
    "timestamp": "2025-01-01T00:00:00",
    "metadata": {"prompt": "Design API"}
})

# Query events
events = db.get_events(agent_id="a1b2c3d4", limit=10)

# Get active agents
active = db.get_active_agents()

db.close()
```

### 5. File Logging

Events are logged to `.moai/logs/agent-transcripts/` with rotation:

**Files:**
- `agent_lifecycle.log`: Rotating log file (10MB per file, 5 backups)
  - Format: `timestamp | level | event_type | agent_id | agent_type | details`
- `agent_lifecycle_YYYY-MM-DD.jsonl`: Daily JSON Lines log
  - Format: One JSON event per entry (multi-line JSON objects)

**Example Log Entry:**
```
2025-11-29 16:05:24 | INFO | SPAWN | a1b2c3d4 | expert-backend | metadata={'prompt': 'Design API'}
2025-11-29 16:05:39 | INFO | COMPLETE | a1b2c3d4 | expert-backend | duration=15230ms
```

## Integration Patterns

### Pattern 1: Basic Agent Lifecycle Tracking

```python
from moai_flow.hooks.agent_lifecycle import (
    generate_agent_id,
    on_agent_spawn,
    on_agent_complete,
    on_agent_error
)
import time

# Generate unique agent ID
agent_id = generate_agent_id()

# Track spawn
on_agent_spawn(
    agent_id=agent_id,
    agent_type="expert-backend",
    metadata={"prompt": "Design REST API"}
)

# Execute agent task
start_time = time.time()
try:
    result = execute_backend_design_task()
    duration_ms = int((time.time() - start_time) * 1000)

    # Track completion
    on_agent_complete(
        agent_id=agent_id,
        result=result,
        duration_ms=duration_ms
    )
except Exception as e:
    # Track error
    on_agent_error(agent_id=agent_id, error=e)
    raise
```

### Pattern 2: Integration with Claude Code Task()

```python
from moai_flow.hooks.agent_lifecycle import (
    generate_agent_id,
    on_agent_spawn,
    on_agent_complete
)

# Before Task() call
agent_id = generate_agent_id()
prompt = "Design backend architecture for user authentication"

on_agent_spawn(
    agent_id=agent_id,
    agent_type="expert-backend",
    metadata={
        "prompt": prompt,
        "model": "claude-sonnet-4"
    }
)

# Execute Task()
import time
start_time = time.time()

result = Task(
    subagent_type="expert-backend",
    prompt=f"Agent ID: {agent_id}\n\n{prompt}"
)

duration_ms = int((time.time() - start_time) * 1000)

# After Task() completes
on_agent_complete(
    agent_id=agent_id,
    result=result,
    duration_ms=duration_ms
)
```

### Pattern 3: Multi-Agent Coordination

```python
from moai_flow.hooks.agent_lifecycle import (
    generate_agent_id,
    on_agent_spawn,
    on_agent_complete,
    get_active_agents
)

# Spawn multiple agents
agent_ids = []
for agent_type in ["expert-backend", "expert-frontend", "expert-database"]:
    agent_id = generate_agent_id()
    agent_ids.append(agent_id)

    on_agent_spawn(
        agent_id=agent_id,
        agent_type=agent_type,
        metadata={"batch_id": "auth_system_001"}
    )

# Monitor active agents
active = get_active_agents()
print(f"Active agents: {len(active)}")

# Complete agents as tasks finish
for agent_id, result in zip(agent_ids, task_results):
    on_agent_complete(
        agent_id=agent_id,
        result=result,
        duration_ms=result.get("duration_ms", 0)
    )
```

## Configuration

No explicit configuration required. The hooks automatically:

1. Create log directory: `.moai/logs/agent-transcripts/`
2. Create database file: `.moai/memory/swarm.db`
3. Initialize schema and tables
4. Set up log rotation (10MB per file, 5 backups)

## Performance Considerations

### Thread Safety
- All operations are thread-safe using `threading.RLock()`
- Safe for concurrent agent spawns and completions

### Storage
- In-memory registry for fast access
- SQLite for persistent storage (thread-safe)
- Log rotation prevents disk bloat (10MB limit per file)

### Cleanup
```python
from moai_flow.hooks.agent_lifecycle import cleanup_old_agents

# Remove agents older than 24 hours
removed_count = cleanup_old_agents(max_age_hours=24)
```

## Testing

Run the test suite to verify installation:

```bash
python3 moai-flow/hooks/test_agent_lifecycle.py
```

**Expected Output:**
```
============================================================
TEST SUMMARY
============================================================
Total tests: 6
Passed: 6 ✅
Failed: 0 ❌
Duration: 0.63s

📝 Logs location: .moai/logs/agent-transcripts/

🎉 ALL TESTS PASSED!
```

## Future Enhancements

### Phase 2: Real-time Monitoring
- WebSocket streaming of agent events
- Live dashboard for active agents
- Performance metrics and analytics

### Phase 3: Advanced Analytics
- Agent performance profiling
- Resource utilization tracking
- Error pattern analysis

### Phase 4: Cross-Session Memory
- SemanticMemory integration
- EpisodicMemory for decision history
- ContextHints for session continuity

## Troubleshooting

### Issue: Events not logged

**Solution:** Ensure log directory exists and has write permissions:
```bash
mkdir -p .moai/logs/agent-transcripts
chmod 755 .moai/logs/agent-transcripts
```

### Issue: SwarmDB connection errors

**Solution:** Verify database file permissions:
```bash
mkdir -p .moai/memory
chmod 755 .moai/memory
rm -f .moai/memory/swarm.db  # Reset if corrupted
```

### Issue: Missing HookStateManager integration

**Solution:** This is optional. If `.claude/hooks/moai/lib/state_tracking.py` is not available, hooks will still function without it.

## API Reference

### Utility Functions

#### `generate_agent_id() -> str`
Generate unique agent ID (UUID4).

#### `get_agent_registry() -> AgentRegistry`
Get global agent registry instance.

#### `get_active_agents() -> List[Dict[str, Any]]`
Get list of currently active agents.

#### `cleanup_old_agents(max_age_hours: int = 24) -> int`
Cleanup agents older than specified hours. Returns count of removed agents.

### Event Classes

- `AgentLifecycleEvent`: Base event class
- `AgentSpawnEvent`: Spawn event (extends base)
- `AgentCompleteEvent`: Completion event (extends base)
- `AgentErrorEvent`: Error event (extends base)

## License

Part of MoAI-ADK - MIT License

## Contributing

For improvements or bug reports, use `/moai:9-feedback`:
```
/moai:9-feedback "agent-lifecycle: [description]"
```

---

**Version:** 1.0.0
**Last Updated:** 2025-11-29
**Status:** Production Ready ✅
