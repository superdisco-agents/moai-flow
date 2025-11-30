# Basic Memory Examples

Complete working examples demonstrating individual memory components.

## Example 1: SwarmDB Basics

```python
from moai_flow.memory import SwarmDB
from datetime import datetime
import uuid

# Initialize database
db = SwarmDB()  # Creates .moai/memory/swarm.db
print("✓ Database initialized")

# Example 1.1: Record agent lifecycle
agent_id = str(uuid.uuid4())

# Spawn event
spawn_event_id = db.insert_event({
    "event_type": "spawn",
    "agent_id": agent_id,
    "agent_type": "expert-backend",
    "timestamp": datetime.now().isoformat(),
    "metadata": {
        "prompt": "Design REST API for user authentication",
        "model": "claude-sonnet-4",
        "priority": "high"
    }
})
print(f"✓ Spawn event: {spawn_event_id}")

# Register agent
db.register_agent(
    agent_id=agent_id,
    agent_type="expert-backend",
    status="spawned",
    metadata={"prompt": "Design REST API"}
)
print(f"✓ Agent registered: {agent_id}")

# Update to running
db.update_agent_status(agent_id, "running")
print("✓ Agent status: running")

# Complete event
import time
time.sleep(0.1)  # Simulate work

complete_event_id = db.insert_event({
    "event_type": "complete",
    "agent_id": agent_id,
    "agent_type": "expert-backend",
    "timestamp": datetime.now().isoformat(),
    "metadata": {
        "duration_ms": 3000,
        "result": "success",
        "tests_passed": 10
    }
})
db.update_agent_status(agent_id, "complete", duration_ms=3000)
print(f"✓ Complete event: {complete_event_id}")

# Example 1.2: Query events
print("\n--- Query Events ---")
events = db.get_events(agent_id=agent_id, limit=10)
print(f"✓ Found {len(events)} events for agent {agent_id}")
for event in events:
    print(f"  {event['event_type']} @ {event['timestamp']}")

# Example 1.3: Get active agents
print("\n--- Active Agents ---")
active = db.get_active_agents()
print(f"✓ Active agents: {len(active)}")
for agent in active:
    print(f"  {agent['agent_id']}: {agent['status']}")

# Example 1.4: Session memory
print("\n--- Session Memory ---")
db.store_memory(
    session_id="session-123",
    memory_type="context_hint",
    key="user_preference",
    value={
        "language": "python",
        "style": "functional",
        "framework": "fastapi"
    }
)

preference = db.get_memory("session-123", "context_hint", "user_preference")
print(f"✓ Retrieved preference: {preference}")

# Cleanup
db.close()
print("\n✅ Example 1 complete")
```

## Example 2: SemanticMemory Knowledge Storage

```python
from moai_flow.memory import SwarmDB, SemanticMemory, KnowledgeCategory

db = SwarmDB()
memory = SemanticMemory(db, project_id="moai-adk")
print("✓ SemanticMemory initialized")

# Example 2.1: Store architectural decision
print("\n--- Store ADR ---")
adr_id = memory.store_knowledge(
    topic="api_authentication",
    knowledge={
        "decision": "Use JWT with refresh tokens",
        "rationale": "Stateless authentication, horizontally scalable, industry standard",
        "alternatives": [
            {"name": "Session-based", "rejected_reason": "State management complexity"},
            {"name": "OAuth2", "rejected_reason": "Overkill for MVP"}
        ],
        "implementation": {
            "library": "PyJWT",
            "access_token_ttl": "15 minutes",
            "refresh_token_ttl": "7 days"
        },
        "security_considerations": [
            "Store refresh tokens securely",
            "Implement token rotation",
            "Use HTTPS only"
        ]
    },
    confidence=0.9,
    category=KnowledgeCategory.ARCHITECTURAL_DECISION,
    tags=["authentication", "security", "jwt", "api"]
)
print(f"✓ Stored ADR: {adr_id}")

# Example 2.2: Store best practice
print("\n--- Store Best Practice ---")
bp_id = memory.store_knowledge(
    topic="error_handling_api",
    knowledge={
        "practice": "Always use structured error responses",
        "format": {
            "error": "Error type string",
            "message": "Human-readable message",
            "details": "Additional context dict",
            "timestamp": "ISO8601 timestamp"
        },
        "example": {
            "error": "ValidationError",
            "message": "Invalid email format",
            "details": {"field": "email", "value": "invalid"},
            "timestamp": "2025-11-30T10:00:00Z"
        },
        "rationale": "Consistent client error handling, easier debugging"
    },
    confidence=0.8,
    category=KnowledgeCategory.BEST_PRACTICE,
    tags=["error", "api", "standard", "json"]
)
print(f"✓ Stored best practice: {bp_id}")

# Example 2.3: Store code pattern
print("\n--- Store Code Pattern ---")
pattern_id = memory.store_pattern(
    pattern_name="async_retry_decorator",
    pattern_data={
        "code": """
import asyncio
from functools import wraps

def async_retry(max_attempts=3, delay=1, backoff=2):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    wait = delay * (backoff ** attempt)
                    await asyncio.sleep(wait)
        return wrapper
    return decorator

# Usage:
@async_retry(max_attempts=5, delay=2)
async def fetch_data():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.example.com/data")
        return response.json()
        """,
        "description": "Async retry decorator with exponential backoff",
        "usage": "Apply to async functions that may fail transiently",
        "dependencies": ["asyncio"],
        "test_example": """
async def test_retry():
    call_count = 0

    @async_retry(max_attempts=3)
    async def flaky_function():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise ConnectionError()
        return "success"

    result = await flaky_function()
    assert result == "success"
    assert call_count == 3
        """
    },
    category=KnowledgeCategory.CODE_PATTERN,
    confidence=0.85,
    tags=["async", "retry", "resilience", "decorator"]
)
print(f"✓ Stored pattern: {pattern_id}")

# Example 2.4: Search knowledge
print("\n--- Search Knowledge ---")
results = memory.search_knowledge(
    query="authentication security",
    min_confidence=0.5,
    limit=10
)
print(f"✓ Found {len(results)} results:")
for result in results:
    print(f"  {result['topic']} (confidence: {result['confidence']:.2f})")
    print(f"    Category: {result['category']}")

# Example 2.5: Update confidence
print("\n--- Update Confidence ---")
memory.record_success(adr_id)
updated = memory.retrieve_knowledge("api_authentication")
print(f"✓ Updated confidence: {updated['confidence']:.2f}")
print(f"  Success count: {updated['success_count']}")

# Example 2.6: Get pattern
print("\n--- Retrieve Pattern ---")
pattern = memory.get_pattern("async_retry_decorator")
if pattern:
    print(f"✓ Retrieved pattern: {pattern['pattern_name']}")
    print(f"  Usage count: {pattern['usage_count']}")
    print(f"  Confidence: {pattern['confidence']:.2f}")

# Example 2.7: Statistics
print("\n--- Statistics ---")
stats = memory.get_statistics()
print(f"✓ Total knowledge: {stats['knowledge']['total_knowledge']}")
print(f"✓ Avg confidence: {stats['knowledge']['avg_confidence']:.2f}")
print(f"✓ Total patterns: {stats['patterns']['total_patterns']}")
print(f"✓ Category breakdown:")
for category, count in stats['categories'].items():
    print(f"  {category}: {count}")

# Cleanup
db.close()
print("\n✅ Example 2 complete")
```

## Example 3: EpisodicMemory Event Tracking

```python
from moai_flow.memory import SwarmDB, EpisodicMemory, EventType
import time

db = SwarmDB()
memory = EpisodicMemory(db, project_id="moai-adk")
print("✓ EpisodicMemory initialized")

# Example 3.1: Record command execution
print("\n--- Record Command ---")
cmd_id = memory.record_event(
    EventType.COMMAND_EXECUTED,
    event_data={
        "command": "/moai:1-plan",
        "description": "Create user authentication SPEC",
        "user": "developer-123"
    },
    context={
        "active_spec": None,
        "phase": "planning",
        "estimated_tokens": 5000
    }
)
print(f"✓ Command recorded: {cmd_id}")

# Example 3.2: Record agent selection decision
print("\n--- Record Decision ---")
decision_id = memory.record_decision(
    decision_type="agent_selection",
    options=["expert-backend", "expert-frontend", "expert-database"],
    chosen="expert-backend",
    rationale="Backend API implementation required for user authentication endpoints",
    context={
        "active_spec": "SPEC-001",
        "phase": "implementation",
        "task_type": "api_implementation",
        "complexity": "medium"
    }
)
print(f"✓ Decision recorded: {decision_id}")

# Example 3.3: Record successful outcome
print("\n--- Record Outcome ---")
time.sleep(0.1)  # Simulate work

memory.record_outcome(
    decision_id,
    outcome="success",
    metrics={
        "duration_ms": 3000,
        "tests_passed": 10,
        "tests_failed": 0,
        "coverage": 92.5,
        "files_changed": 5,
        "lines_added": 250
    }
)
print(f"✓ Outcome recorded: success")

# Example 3.4: Record another decision with failure
print("\n--- Record Failed Decision ---")
decision_id2 = memory.record_decision(
    decision_type="agent_selection",
    options=["expert-frontend", "expert-uiux"],
    chosen="expert-frontend",
    rationale="UI component implementation needed"
)

memory.record_outcome(
    decision_id2,
    outcome="failure",
    metrics={
        "duration_ms": 1500,
        "error": "Missing React component dependencies",
        "attempted_fix": "Install missing packages"
    }
)
print(f"✓ Failed decision recorded")

# Example 3.5: Get recent events
print("\n--- Recent Events ---")
recent = memory.get_recent_events(limit=10)
print(f"✓ Found {len(recent)} recent events:")
for event in recent:
    print(f"  {event['event_type']} @ {event['timestamp']}")

# Example 3.6: Get decisions
print("\n--- Decision Events ---")
decisions = memory.get_events_by_type(EventType.DECISION_MADE)
print(f"✓ Found {len(decisions)} decision events")
for decision in decisions:
    data = decision['event_data']
    outcome = decision.get('outcome', {})
    print(f"  Chose: {data.get('chosen')}")
    print(f"  Outcome: {outcome.get('status', 'pending')}")

# Example 3.7: Find similar episodes
print("\n--- Similar Episodes ---")
similar = memory.find_similar_episodes(
    current_context={
        "active_spec": "SPEC-001",
        "phase": "implementation",
        "task_type": "api_implementation"
    },
    limit=3
)
print(f"✓ Found {len(similar)} similar episodes:")
for episode in similar:
    print(f"  {episode['event_type']} - Context: {episode.get('context')}")

# Example 3.8: Outcome statistics
print("\n--- Outcome Statistics ---")
stats = memory.get_outcome_statistics("agent_selection")
print(f"✓ Agent selection statistics:")
print(f"  Total decisions: {stats['total_decisions']}")
print(f"  Success rate: {stats['success_rate']:.1f}%")
print(f"  Avg duration: {stats['avg_duration_ms']:.0f}ms")
print(f"  Outcome breakdown: {stats['outcome_counts']}")

# Cleanup
db.close()
print("\n✅ Example 3 complete")
```

## Example 4: ContextHints User Preferences

```python
from moai_flow.memory import (
    SwarmDB,
    ContextHints,
    PreferenceCategory,
    ExpertiseLevel,
    WorkflowPreference,
    CommunicationStyle
)

db = SwarmDB()
hints = ContextHints(db, session_id="session-123")
print("✓ ContextHints initialized")

# Example 4.1: Set preferences
print("\n--- Set Preferences ---")
hints.set_preference(PreferenceCategory.COMMUNICATION, CommunicationStyle.CONCISE)
hints.set_preference(PreferenceCategory.WORKFLOW, WorkflowPreference.TDD)
hints.set_expertise_level(ExpertiseLevel.EXPERT)
print("✓ Preferences set")

# Get preferences
prefs = hints.get_all_preferences()
print(f"  Communication: {prefs.get(PreferenceCategory.COMMUNICATION)}")
print(f"  Workflow: {prefs.get(PreferenceCategory.WORKFLOW)}")
print(f"  Expertise: {hints.get_expertise_level()}")

# Example 4.2: Record task patterns
print("\n--- Record Task Patterns ---")

# Planning task
hints.record_task_pattern("planning", {
    "spec_id": "SPEC-001",
    "agents_used": ["manager-spec"],
    "success": True,
    "duration_ms": 2000,
    "workflow": "tdd"
})

# Implementation task
hints.record_task_pattern("implementation", {
    "spec_id": "SPEC-001",
    "agents_used": ["expert-backend", "manager-tdd"],
    "success": True,
    "duration_ms": 5000,
    "tools_used": ["expert-backend", "manager-tdd"],
    "workflow": "tdd"
})

# Testing task
hints.record_task_pattern("testing", {
    "spec_id": "SPEC-001",
    "agents_used": ["manager-quality"],
    "success": True,
    "duration_ms": 1500,
    "tools_used": ["manager-quality"]
})

print("✓ Task patterns recorded")

# Example 4.3: Get task patterns
print("\n--- Task Patterns ---")
patterns = hints.get_task_patterns(limit=10)
print(f"✓ Retrieved {len(patterns)} task patterns:")
for pattern in patterns:
    print(f"  {pattern['task_type']} @ {pattern['timestamp']}")
    print(f"    Success: {pattern.get('success')}")
    print(f"    Duration: {pattern.get('duration_ms')}ms")

# Example 4.4: Tool preferences
print("\n--- Tool Preferences ---")
tool_prefs = hints.get_tool_preferences()
print(f"✓ Tool usage statistics:")
for tool, count in tool_prefs.items():
    print(f"  {tool}: {count} times")

most_used = hints.get_most_used_tools(3)
print(f"✓ Top 3 tools: {most_used}")

# Example 4.5: Next action suggestion
print("\n--- Next Action Suggestion ---")
suggestion = hints.suggest_next_action()
if suggestion:
    print(f"✓ Suggested: {suggestion}")
else:
    print("  No suggestion available")

# Example 4.6: Workflow analysis
print("\n--- Workflow Analysis ---")
analysis = hints.analyze_workflow_patterns()
print(f"✓ Analysis:")
print(f"  Total tasks: {analysis.get('total_tasks', 0)}")
print(f"  Success rates: {analysis.get('success_rate', {})}")
print(f"  Common sequences: {analysis.get('common_sequences', [])[:2]}")
print(f"  Preferred agents: {analysis.get('preferred_agents', [])[:3]}")

# Example 4.7: Context adaptation
print("\n--- Context Adaptation ---")
print(f"✓ Show verbose: {hints.should_show_verbose_output()}")
print(f"✓ Strict validation: {hints.should_enforce_strict_validation()}")
print(f"✓ Recommended workflow: {hints.get_recommended_workflow()}")

# Cleanup
db.close()
print("\n✅ Example 4 complete")
```

## Running the Examples

```bash
# Install dependencies (if not already installed)
cd /path/to/moai-adk
pip install -e .

# Run individual examples
python -c "$(cat examples/basic-memory.md | sed -n '/Example 1:/,/Example 2:/p')"
python -c "$(cat examples/basic-memory.md | sed -n '/Example 2:/,/Example 3:/p')"
python -c "$(cat examples/basic-memory.md | sed -n '/Example 3:/,/Example 4:/p')"
python -c "$(cat examples/basic-memory.md | sed -n '/Example 4:/,/Running/p')"

# Or use the Python files directly in moai_flow/memory/
python moai_flow/memory/swarm_db.py
python moai_flow/memory/semantic_memory.py
python moai_flow/memory/episodic_memory.py
python moai_flow/memory/context_hints.py
```

## Expected Output

Each example produces verbose output showing:
- ✓ Successful operations
- Stored IDs and timestamps
- Retrieved data and statistics
- Pattern analysis results
- Suggestions and recommendations

All examples use `.moai/memory/swarm.db` as the default database location.
