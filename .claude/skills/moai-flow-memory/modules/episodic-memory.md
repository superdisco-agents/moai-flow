# Episodic Memory - Event and Decision History

Temporal event storage with outcome tracking, similarity matching, and pattern analysis for learning from past actions.

## Overview

EpisodicMemory provides temporal context and decision history with:

- Event-specific data recording
- Decision point tracking with options and rationale
- Outcome metrics (success, failure, partial)
- Similarity-based episode matching
- Statistical outcome analysis
- Temporal sequence queries

## Event Types

```python
from moai_flow.memory import EventType

EventType.COMMAND_EXECUTED      # /moai:* commands
EventType.AGENT_SPAWNED         # Agent spawned
EventType.AGENT_COMPLETED       # Agent completed
EventType.DECISION_MADE         # Decision point
EventType.ERROR_OCCURRED        # Error occurred
EventType.USER_FEEDBACK         # User feedback
EventType.SPEC_CREATED          # SPEC created
EventType.IMPLEMENTATION_COMPLETE  # Implementation complete
```

## API Reference

### Initialization

```python
from moai_flow.memory import SwarmDB, EpisodicMemory

db = SwarmDB()
memory = EpisodicMemory(db, project_id="moai-adk")
```

### Event Recording

**record_event()**
```python
event_id = memory.record_event(
    event_type=EventType.COMMAND_EXECUTED,
    event_data={
        "command": "/moai:1-plan",
        "description": "Create user authentication SPEC",
        "user": "developer-123"
    },
    session_id="session-123",  # Optional, auto-generates if not provided
    context={
        "active_spec": None,
        "phase": "planning",
        "token_usage": 5000
    }
)
```

**record_decision()**
```python
decision_id = memory.record_decision(
    decision_type="agent_selection",
    options=["expert-backend", "expert-frontend", "expert-database"],
    chosen="expert-backend",
    rationale="Backend API implementation required for REST endpoints",
    session_id="session-123",
    context={
        "active_spec": "SPEC-001",
        "phase": "implementation",
        "task_type": "api_implementation",
        "complexity": "medium"
    }
)
```

**record_outcome()**
```python
memory.record_outcome(
    event_id=decision_id,
    outcome="success",
    metrics={
        "duration_ms": 3000,
        "tests_passed": 10,
        "tests_failed": 0,
        "coverage": 92.5,
        "files_changed": 5
    }
)
```

### Event Retrieval

**get_event()**
```python
# Get single event by ID
event = memory.get_event(event_id)

if event:
    print(f"Event type: {event['event_type']}")
    print(f"Timestamp: {event['timestamp']}")
    print(f"Data: {event['event_data']}")
    print(f"Outcome: {event.get('outcome')}")
```

**get_recent_events()**
```python
# Get recent events (all types)
recent = memory.get_recent_events(limit=50)

# Get recent events for specific session
session_events = memory.get_recent_events(
    limit=100,
    session_id="session-123"
)

for event in recent:
    print(f"{event['timestamp']}: {event['event_type']}")
```

**get_events_by_type()**
```python
# Get all decision events
decisions = memory.get_events_by_type(
    event_type=EventType.DECISION_MADE,
    limit=100
)

# Get decisions for specific session
session_decisions = memory.get_events_by_type(
    event_type=EventType.DECISION_MADE,
    limit=50,
    session_id="session-123"
)
```

### Similarity and Pattern Matching

**find_similar_episodes()**
```python
# Find episodes similar to current context
similar = memory.find_similar_episodes(
    current_context={
        "active_spec": "SPEC-001",
        "phase": "implementation",
        "task_type": "api_implementation"
    },
    limit=5,
    event_type=EventType.DECISION_MADE  # Optional filter
)

for episode in similar:
    print(f"Similar episode: {episode['event_type']}")
    print(f"  Context: {episode.get('context')}")
    print(f"  Outcome: {episode.get('outcome')}")
```

**get_outcome_statistics()**
```python
# Analyze outcomes for specific decision type
stats = memory.get_outcome_statistics("agent_selection")

print(f"Success rate: {stats['success_rate']:.1f}%")
print(f"Total decisions: {stats['total_decisions']}")
print(f"Avg duration: {stats['avg_duration_ms']:.0f}ms")
print(f"Outcome breakdown: {stats['outcome_counts']}")
# {'success': 45, 'failure': 5, 'partial': 3}
```

### Maintenance

**cleanup_old_episodes()**
```python
# Delete episodes older than 90 days
deleted = memory.cleanup_old_episodes(days=90)
print(f"Cleaned up {deleted} old episodes")
```

## Usage Patterns

### Pattern 1: Command Execution Tracking

```python
# Before command execution
cmd_event_id = memory.record_event(
    event_type=EventType.COMMAND_EXECUTED,
    event_data={
        "command": "/moai:2-run",
        "spec_id": "SPEC-001",
        "description": "Implement user authentication"
    },
    context={
        "phase": "implementation",
        "estimated_duration_ms": 10000
    }
)

# After command completion
import time
start = time.time()
# ... execute command ...
duration_ms = (time.time() - start) * 1000

memory.record_outcome(
    cmd_event_id,
    outcome="success",
    metrics={
        "duration_ms": duration_ms,
        "tests_passed": 15,
        "coverage": 95.0
    }
)
```

### Pattern 2: Agent Selection Learning

```python
# Record agent selection decision
decision_id = memory.record_decision(
    decision_type="agent_selection",
    options=["expert-backend", "expert-frontend"],
    chosen="expert-backend",
    rationale="API implementation task",
    context={
        "task_type": "api",
        "complexity": "medium",
        "estimated_duration": "5-10min"
    }
)

# After agent completes
agent_result = execute_agent("expert-backend")

if agent_result.success:
    memory.record_outcome(
        decision_id,
        outcome="success",
        metrics={
            "duration_ms": agent_result.duration,
            "quality_score": 0.95
        }
    )
else:
    memory.record_outcome(
        decision_id,
        outcome="failure",
        metrics={
            "error": agent_result.error,
            "duration_ms": agent_result.duration
        }
    )

# Later: Analyze which agent works best for API tasks
stats = memory.get_outcome_statistics("agent_selection")
```

### Pattern 3: Similar Situation Detection

```python
# Current situation
current_context = {
    "active_spec": "SPEC-003",
    "phase": "implementation",
    "task_type": "database_schema",
    "complexity": "high"
}

# Find similar past episodes
similar = memory.find_similar_episodes(
    current_context=current_context,
    limit=3,
    event_type=EventType.DECISION_MADE
)

if similar:
    print("Found similar past situations:")
    for episode in similar:
        decision_data = episode['event_data']
        outcome = episode.get('outcome', {})

        print(f"\nPast decision: {decision_data.get('chosen')}")
        print(f"Rationale: {decision_data.get('rationale')}")
        print(f"Outcome: {outcome.get('status')}")

        if outcome.get('status') == 'success':
            print("→ Consider using same approach")
```

### Pattern 4: Workflow Pattern Analysis

```python
# Record complete workflow
workflow_events = []

# 1. Planning
plan_id = memory.record_event(
    EventType.SPEC_CREATED,
    {"spec_id": "SPEC-001", "title": "User Auth"}
)
workflow_events.append(plan_id)

# 2. Implementation
impl_id = memory.record_decision(
    "implementation_approach",
    options=["tdd", "implementation-first"],
    chosen="tdd",
    rationale="Test-first approach for critical auth"
)
workflow_events.append(impl_id)

# 3. Completion
complete_id = memory.record_event(
    EventType.IMPLEMENTATION_COMPLETE,
    {"spec_id": "SPEC-001", "tests": 20, "coverage": 95}
)
workflow_events.append(complete_id)

# Analyze workflow success
for event_id in workflow_events:
    event = memory.get_event(event_id)
    if event.get('outcome'):
        print(f"{event['event_type']}: {event['outcome']['status']}")
```

### Pattern 5: Error Pattern Recognition

```python
# Record error occurrence
error_id = memory.record_event(
    event_type=EventType.ERROR_OCCURRED,
    event_data={
        "error_type": "ConnectionError",
        "message": "Database connection pool exhausted",
        "stack_trace": "...",
        "attempted_fix": "Increased pool size"
    },
    context={
        "phase": "implementation",
        "load": "high",
        "concurrent_agents": 5
    }
)

# Record resolution outcome
memory.record_outcome(
    error_id,
    outcome="success",
    metrics={
        "time_to_resolve_ms": 300000,  # 5 minutes
        "fix": "Increased pool_size from 10 to 25"
    }
)

# Later: Search for similar errors
similar_errors = memory.find_similar_episodes(
    current_context={
        "error_type": "ConnectionError",
        "load": "high"
    },
    event_type=EventType.ERROR_OCCURRED
)

for error in similar_errors:
    outcome = error.get('outcome', {})
    if outcome.get('status') == 'success':
        print(f"Past fix: {outcome.get('metrics', {}).get('fix')}")
```

## Advanced Features

### Temporal Sequence Analysis

```python
def analyze_decision_sequence(session_id: str):
    """Analyze decision sequence in a session"""

    events = memory.get_events_by_type(
        EventType.DECISION_MADE,
        session_id=session_id
    )

    sequence = []
    for event in events:
        decision_data = event['event_data']
        outcome = event.get('outcome', {})

        sequence.append({
            'decision': decision_data['chosen'],
            'outcome': outcome.get('status'),
            'timestamp': event['timestamp']
        })

    # Identify patterns
    successful_sequences = [
        s for s in sequence if s['outcome'] == 'success'
    ]

    return {
        'total_decisions': len(sequence),
        'successful': len(successful_sequences),
        'sequence': sequence
    }
```

### Outcome Prediction

```python
def predict_outcome(context: dict) -> dict:
    """Predict outcome based on similar past episodes"""

    similar = memory.find_similar_episodes(
        current_context=context,
        limit=10
    )

    if not similar:
        return {"confidence": 0.0, "prediction": "unknown"}

    # Count outcomes
    outcomes = [
        ep.get('outcome', {}).get('status', 'unknown')
        for ep in similar
    ]

    success_count = outcomes.count('success')
    total = len(outcomes)

    return {
        "prediction": "success" if success_count / total > 0.7 else "uncertain",
        "confidence": success_count / total,
        "sample_size": total
    }
```

### Performance Trending

```python
def get_performance_trend(decision_type: str, days: int = 30):
    """Analyze performance trend over time"""

    from datetime import datetime, timedelta

    cutoff = datetime.now() - timedelta(days=days)
    events = memory.get_events_by_type(EventType.DECISION_MADE)

    # Filter by decision type and date
    filtered = [
        e for e in events
        if (e['event_data'].get('decision_type') == decision_type and
            datetime.fromisoformat(e['timestamp']) > cutoff)
    ]

    # Group by week
    weekly_stats = {}
    for event in filtered:
        week = datetime.fromisoformat(event['timestamp']).isocalendar()[1]
        outcome = event.get('outcome', {}).get('status')

        if week not in weekly_stats:
            weekly_stats[week] = {'success': 0, 'failure': 0}

        if outcome == 'success':
            weekly_stats[week]['success'] += 1
        elif outcome == 'failure':
            weekly_stats[week]['failure'] += 1

    return weekly_stats
```

## Episode Data Structure

```python
@dataclass
class Episode:
    id: str
    event_type: str
    timestamp: str
    session_id: str
    event_data: Dict[str, Any]
    outcome: Optional[Dict[str, Any]] = None
    context: Optional[Dict[str, Any]] = None

# Example episode
{
    "id": "episode-123",
    "event_type": "decision",
    "timestamp": "2025-11-30T10:00:00",
    "session_id": "session-123",
    "event_data": {
        "decision_type": "agent_selection",
        "options": ["expert-backend", "expert-frontend"],
        "chosen": "expert-backend",
        "rationale": "API implementation required"
    },
    "outcome": {
        "status": "success",
        "timestamp": "2025-11-30T10:05:00",
        "metrics": {
            "duration_ms": 3000,
            "tests_passed": 10,
            "coverage": 92.5
        }
    },
    "context": {
        "active_spec": "SPEC-001",
        "phase": "implementation",
        "task_type": "api_implementation"
    }
}
```

## Similarity Calculation

EpisodicMemory uses context-based similarity:

```python
def _calculate_similarity(context1: dict, context2: dict) -> float:
    """
    Calculate similarity between contexts (0.0 - 1.0)

    Similarity = (matching values / common keys) * (common keys / total keys)
    """

    common_keys = set(context1.keys()) & set(context2.keys())
    if not common_keys:
        return 0.0

    # Value match ratio
    matches = sum(1 for k in common_keys if context1[k] == context2[k])
    value_match = matches / len(common_keys)

    # Key overlap ratio
    total_keys = len(set(context1.keys()) | set(context2.keys()))
    key_overlap = len(common_keys) / total_keys

    return value_match * key_overlap
```

## Best Practices

1. **Always record context**
```python
memory.record_decision(..., context={"phase": "...", "task_type": "..."})
```

2. **Record outcomes promptly**
```python
decision_id = memory.record_decision(...)
# ... execute decision ...
memory.record_outcome(decision_id, outcome="success", metrics={...})
```

3. **Use consistent context keys**
```python
# Good: Consistent keys across decisions
context = {"phase": "implementation", "task_type": "api"}

# Bad: Inconsistent keys (reduces similarity matching)
context1 = {"phase": "impl", "type": "api"}
context2 = {"stage": "implementation", "task": "api"}
```

4. **Include outcome metrics**
```python
metrics = {
    "duration_ms": 3000,
    "tests_passed": 10,
    "coverage": 92.5,
    "quality_score": 0.95
}
```

5. **Regular cleanup**
```python
# Monthly cleanup of old episodes
memory.cleanup_old_episodes(days=90)
```

## Integration with Other Components

See [examples/distributed-memory.md](../examples/distributed-memory.md) for patterns integrating EpisodicMemory with SemanticMemory and ContextHints.
