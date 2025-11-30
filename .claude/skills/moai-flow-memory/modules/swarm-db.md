# SwarmDB - Persistent Storage Foundation

SQLite-based persistent storage for multi-agent coordination with thread-safe operations and observability metrics.

## Overview

SwarmDB provides the foundation layer for MoAI Flow memory management through a zero-dependency SQLite backend with:

- Thread-safe connection pooling
- Automatic schema initialization and migrations
- Transaction support with rollback
- JSON metadata storage for flexibility
- Optimized time-series indexing (Phase 6A)
- 30-day default retention with auto-cleanup

## Database Schema (v2.0.0)

### Core Tables

**agent_events** - Agent lifecycle events
```sql
CREATE TABLE agent_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id TEXT UNIQUE NOT NULL,
    event_type TEXT NOT NULL,  -- 'spawn' | 'complete' | 'error'
    agent_id TEXT NOT NULL,
    agent_type TEXT NOT NULL,
    timestamp TEXT NOT NULL,   -- ISO8601 format
    metadata TEXT,             -- JSON blob
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for fast queries
CREATE INDEX idx_agent_events_agent_id ON agent_events(agent_id);
CREATE INDEX idx_agent_events_event_type ON agent_events(event_type);
CREATE INDEX idx_agent_events_timestamp ON agent_events(timestamp);
```

**agent_registry** - Current agent state
```sql
CREATE TABLE agent_registry (
    agent_id TEXT PRIMARY KEY,
    agent_type TEXT NOT NULL,
    status TEXT NOT NULL,      -- 'spawned' | 'running' | 'complete' | 'error'
    spawn_time REAL NOT NULL,
    complete_time REAL,
    duration_ms INTEGER,
    metadata TEXT,             -- JSON blob
    last_updated TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_agent_registry_status ON agent_registry(status);
CREATE INDEX idx_agent_registry_agent_type ON agent_registry(agent_type);
```

**session_memory** - Cross-session persistence
```sql
CREATE TABLE session_memory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    memory_type TEXT NOT NULL,  -- 'semantic' | 'episodic' | 'context_hint'
    key TEXT NOT NULL,
    value TEXT,                 -- JSON blob
    timestamp TEXT NOT NULL,
    ttl_hours INTEGER,          -- Time-to-live (NULL = permanent)
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_session_memory_session_id ON session_memory(session_id);
CREATE INDEX idx_session_memory_memory_type ON session_memory(memory_type);
CREATE INDEX idx_session_memory_key ON session_memory(key);
```

### Phase 6A Observability Tables

**task_metrics** - Task performance metrics
```sql
CREATE TABLE task_metrics (
    task_id TEXT NOT NULL,
    agent_id TEXT NOT NULL,
    duration_ms INTEGER,
    result TEXT NOT NULL,       -- 'success' | 'failure' | 'timeout' | 'cancelled'
    tokens_used INTEGER DEFAULT 0,
    files_changed INTEGER DEFAULT 0,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (task_id, timestamp)
);

CREATE INDEX idx_task_metrics_agent ON task_metrics(agent_id, timestamp);
CREATE INDEX idx_task_metrics_time ON task_metrics(timestamp);
CREATE INDEX idx_task_metrics_result ON task_metrics(result, timestamp);
```

**agent_metrics** - Agent statistics
```sql
CREATE TABLE agent_metrics (
    metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_id TEXT NOT NULL,
    metric_type TEXT NOT NULL,  -- 'duration' | 'success_rate' | 'error_count'
    value REAL NOT NULL,
    metadata TEXT,              -- JSON blob
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_agent_metrics_agent ON agent_metrics(agent_id, metric_type, timestamp);
CREATE INDEX idx_agent_metrics_type ON agent_metrics(metric_type, timestamp);
```

**swarm_metrics** - Swarm-level health
```sql
CREATE TABLE swarm_metrics (
    metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
    swarm_id TEXT NOT NULL,
    metric_type TEXT NOT NULL,  -- 'health' | 'throughput' | 'latency' | 'resource'
    value REAL NOT NULL,
    metadata TEXT,              -- JSON blob
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_swarm_metrics_swarm ON swarm_metrics(swarm_id, metric_type, timestamp);
CREATE INDEX idx_swarm_metrics_type ON swarm_metrics(metric_type, timestamp);
```

## API Reference

### Initialization

```python
from moai_flow.memory import SwarmDB
from pathlib import Path

# Default location (.moai/memory/swarm.db)
db = SwarmDB()

# Custom location
db = SwarmDB(db_path=Path("/custom/path/swarm.db"))

# Context manager (auto-close)
with SwarmDB() as db:
    db.insert_event(...)
```

### Agent Event Operations

**insert_event()**
```python
event_id = db.insert_event(
    event_data={
        "event_type": "spawn",
        "agent_id": "agent-123",
        "agent_type": "expert-backend",
        "timestamp": "2025-11-30T10:00:00",
        "metadata": {
            "prompt": "Design API",
            "model": "claude-sonnet-4"
        }
    },
    event_id="optional-custom-id"  # Generates UUID if not provided
)
```

**get_events()**
```python
# Get all events
events = db.get_events(limit=100)

# Filter by agent
events = db.get_events(agent_id="agent-123", limit=50)

# Filter by type
events = db.get_events(event_type="spawn", limit=20)

# Combined filters
events = db.get_events(
    agent_id="agent-123",
    event_type="complete",
    limit=10
)
```

### Agent Registry Operations

**register_agent()**
```python
db.register_agent(
    agent_id="agent-123",
    agent_type="expert-backend",
    status="spawned",
    metadata={"prompt": "Design API", "priority": "high"}
)
```

**update_agent_status()**
```python
# Update to running
db.update_agent_status("agent-123", "running")

# Update to complete with duration
db.update_agent_status("agent-123", "complete", duration_ms=3000)

# Update to error
db.update_agent_status("agent-123", "error")
```

**get_agent()**
```python
agent = db.get_agent("agent-123")
if agent:
    print(f"Status: {agent['status']}")
    print(f"Duration: {agent['duration_ms']}ms")
    print(f"Metadata: {agent['metadata']}")
```

**get_active_agents()**
```python
active = db.get_active_agents()
for agent in active:
    print(f"{agent['agent_id']}: {agent['agent_type']} ({agent['status']})")
```

### Session Memory Operations

**store_memory()**
```python
# Permanent memory
db.store_memory(
    session_id="session-123",
    memory_type="context_hint",
    key="user_preference",
    value={"language": "python", "style": "functional"}
)

# Temporary memory with TTL
db.store_memory(
    session_id="session-123",
    memory_type="context_hint",
    key="temp_setting",
    value={"enabled": True},
    ttl_hours=24  # Auto-expires after 24 hours
)
```

**get_memory()**
```python
value = db.get_memory(
    session_id="session-123",
    memory_type="context_hint",
    key="user_preference"
)

if value:
    print(f"Preference: {value}")
```

### Transaction Management

**transaction() context manager**
```python
# Automatic commit/rollback
try:
    with db.transaction() as conn:
        cursor = conn.cursor()

        # Multiple operations
        cursor.execute("INSERT INTO agent_events ...")
        cursor.execute("UPDATE agent_registry ...")
        cursor.execute("INSERT INTO session_memory ...")

        # Auto-commit on success
except Exception as e:
    # Auto-rollback on error
    print(f"Transaction failed: {e}")
```

**Batch operations**
```python
with db.transaction() as conn:
    cursor = conn.cursor()

    # Insert multiple events atomically
    for event in batch_events:
        cursor.execute(
            "INSERT INTO agent_events (event_id, event_type, ...) VALUES (?, ?, ...)",
            (event.id, event.type, ...)
        )
```

### Maintenance Operations

**cleanup_old_events()**
```python
# Delete events older than 30 days
deleted = db.cleanup_old_events(days=30)
print(f"Cleaned up {deleted} old events")

# Custom retention period
deleted = db.cleanup_old_events(days=90)
```

**vacuum()**
```python
# Optimize database storage (reclaim space)
db.vacuum()
```

**close()**
```python
# Close all connections
db.close()
```

## Thread Safety

SwarmDB implements thread-safe connection pooling:

```python
import threading
from moai_flow.memory import SwarmDB

db = SwarmDB()

def worker(agent_id):
    # Each thread gets its own connection
    db.insert_event({
        "event_type": "spawn",
        "agent_id": agent_id,
        "agent_type": "expert-backend",
        "timestamp": datetime.now().isoformat()
    })

# Safe concurrent access
threads = [
    threading.Thread(target=worker, args=(f"agent-{i}",))
    for i in range(10)
]

for t in threads:
    t.start()

for t in threads:
    t.join()
```

## Performance Optimization

### Indexing Strategy

All time-series queries are indexed for fast lookups:
- `timestamp` columns have dedicated indexes
- Foreign keys (agent_id, session_id) are indexed
- Composite indexes for common query patterns

### Batch Operations

Use transactions for batch operations:
```python
# Good: Single transaction
with db.transaction() as conn:
    for i in range(1000):
        cursor.execute("INSERT ...")

# Bad: 1000 individual commits
for i in range(1000):
    db.insert_event(...)  # Each creates transaction
```

### Connection Pooling

Connections are pooled per-thread:
- No connection overhead for repeated operations
- Automatic connection reuse
- Thread-safe isolation

## Error Handling

```python
from moai_flow.memory import SwarmDB

db = SwarmDB()

try:
    with db.transaction() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO agent_events ...")
        cursor.execute("UPDATE agent_registry ...")
except sqlite3.IntegrityError as e:
    # Handle constraint violations
    print(f"Integrity error: {e}")
except sqlite3.OperationalError as e:
    # Handle database locked, disk full, etc.
    print(f"Operational error: {e}")
except Exception as e:
    # Handle all other errors
    print(f"Unexpected error: {e}")
finally:
    db.close()
```

## Migration Strategy

SwarmDB tracks schema version:
```python
# Check current schema version
conn = db._get_connection()
cursor = conn.cursor()
cursor.execute("SELECT value FROM schema_info WHERE key = 'version'")
version = cursor.fetchone()[0]
print(f"Schema version: {version}")
```

Future migrations will be handled automatically during initialization.

## Best Practices

1. **Use context manager for cleanup**
```python
with SwarmDB() as db:
    db.insert_event(...)
# Auto-closes on exit
```

2. **Batch operations in transactions**
```python
with db.transaction() as conn:
    for event in events:
        cursor.execute("INSERT ...")
```

3. **Regular maintenance**
```python
# Daily cleanup
db.cleanup_old_events(days=30)

# Weekly vacuum
db.vacuum()
```

4. **Monitor database size**
```python
import os
db_size = os.path.getsize(db.db_path)
print(f"Database size: {db_size / 1024 / 1024:.2f} MB")
```

5. **Handle errors gracefully**
```python
try:
    db.insert_event(event_data)
except Exception as e:
    logger.error(f"Failed to insert event: {e}")
    # Continue operation with degraded functionality
```

## Integration Examples

See [examples.md](../examples.md) for complete working examples including:
- Basic SwarmDB usage
- Multi-threaded agent coordination
- Transaction patterns
- Maintenance automation
