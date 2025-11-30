# Context Hints - Adaptive User Preferences

Session-level user preference tracking with workflow pattern learning and intelligent next-action suggestions.

## Overview

ContextHints provides adaptive assistance through:

- User expertise level tracking (beginner, intermediate, expert)
- Preferred workflow patterns (TDD, documentation-first, implementation-first)
- Communication preferences (verbose, concise, balanced)
- Recent task pattern recognition (last 100 tasks)
- Tool usage preference tracking
- Intelligent next-action suggestions based on patterns

## Preference Categories

```python
from moai_flow.memory import (
    PreferenceCategory,
    ExpertiseLevel,
    WorkflowPreference,
    CommunicationStyle,
    ValidationStrictness
)

# Preference categories
PreferenceCategory.COMMUNICATION  # verbose, concise, balanced
PreferenceCategory.WORKFLOW      # tdd, doc-first, impl-first
PreferenceCategory.VALIDATION    # strict, moderate, relaxed
PreferenceCategory.EXPERTISE     # beginner, intermediate, expert
PreferenceCategory.TOOLS         # tool usage patterns

# Expertise levels
ExpertiseLevel.BEGINNER
ExpertiseLevel.INTERMEDIATE
ExpertiseLevel.EXPERT

# Workflow preferences
WorkflowPreference.TDD
WorkflowPreference.DOC_FIRST
WorkflowPreference.IMPL_FIRST
WorkflowPreference.ITERATIVE

# Communication styles
CommunicationStyle.VERBOSE
CommunicationStyle.CONCISE
CommunicationStyle.BALANCED

# Validation strictness
ValidationStrictness.STRICT
ValidationStrictness.MODERATE
ValidationStrictness.RELAXED
```

## API Reference

### Initialization

```python
from moai_flow.memory import SwarmDB, ContextHints

db = SwarmDB()
hints = ContextHints(db, session_id="session-123")
```

### Preference Management

**set_preference()**
```python
# Set standard preferences
hints.set_preference(
    PreferenceCategory.COMMUNICATION,
    CommunicationStyle.CONCISE
)

hints.set_preference(
    PreferenceCategory.WORKFLOW,
    WorkflowPreference.TDD
)

# Set custom preference
hints.set_preference(
    "custom_setting",
    {"enabled": True, "mode": "fast"}
)

# Set temporary preference with TTL
hints.set_preference(
    "temp_mode",
    "debug",
    ttl_hours=24  # Expires after 24 hours
)
```

**get_preference()**
```python
# Get standard preference
style = hints.get_preference(
    PreferenceCategory.COMMUNICATION,
    default=CommunicationStyle.BALANCED
)

# Get custom preference
setting = hints.get_preference("custom_setting", default={})
```

**get_all_preferences()**
```python
prefs = hints.get_all_preferences()
print(f"Communication: {prefs.get(PreferenceCategory.COMMUNICATION)}")
print(f"Workflow: {prefs.get(PreferenceCategory.WORKFLOW)}")
print(f"Expertise: {prefs.get(PreferenceCategory.EXPERTISE)}")
```

### Expertise Level Management

**set_expertise_level()**
```python
hints.set_expertise_level(ExpertiseLevel.EXPERT)
```

**get_expertise_level()**
```python
level = hints.get_expertise_level()
print(f"User expertise: {level}")  # 'expert'
```

### Task Pattern Recording

**record_task_pattern()**
```python
hints.record_task_pattern(
    task_type="implementation",
    metadata={
        "spec_id": "SPEC-001",
        "agents_used": ["expert-backend", "manager-tdd"],
        "success": True,
        "duration_ms": 5000,
        "tools_used": ["expert-backend", "manager-tdd"],
        "workflow": "tdd"
    }
)
```

**get_task_patterns()**
```python
# Get recent task patterns
recent_patterns = hints.get_task_patterns(limit=10)

for pattern in recent_patterns:
    print(f"Task: {pattern['task_type']}")
    print(f"  Timestamp: {pattern['timestamp']}")
    print(f"  Success: {pattern.get('success')}")
    print(f"  Duration: {pattern.get('duration_ms')}ms")
```

### Tool Usage Tracking

**record_tool_usage()**
```python
# Automatically tracked when recording task patterns with 'tools_used'
hints.record_tool_usage("expert-backend")
hints.record_tool_usage("manager-tdd")
```

**get_tool_preferences()**
```python
tool_prefs = hints.get_tool_preferences()
print(f"Tool usage: {tool_prefs}")
# {'expert-backend': 15, 'manager-tdd': 12, ...}
```

**get_most_used_tools()**
```python
top_tools = hints.get_most_used_tools(limit=5)
print("Most used tools:")
for tool, count in top_tools:
    print(f"  {tool}: {count} times")
# [('expert-backend', 15), ('manager-tdd', 12), ...]
```

### Pattern Analysis and Suggestions

**suggest_next_action()**
```python
# Get intelligent next action suggestion
suggestion = hints.suggest_next_action()

if suggestion:
    print(f"Suggested next: {suggestion}")
    # "Run /moai:3-sync to document recent implementation"
```

**analyze_workflow_patterns()**
```python
analysis = hints.analyze_workflow_patterns()

print(f"Total tasks: {analysis['total_tasks']}")
print(f"Success rates: {analysis['success_rate']}")
print(f"Common sequences: {analysis['common_sequences']}")
print(f"Preferred agents: {analysis['preferred_agents']}")
print(f"Average durations: {analysis['average_duration']}")
```

### Context Adaptation

**should_show_verbose_output()**
```python
if hints.should_show_verbose_output():
    print("Detailed explanation...")
else:
    print("Concise summary")
```

**should_enforce_strict_validation()**
```python
if hints.should_enforce_strict_validation():
    # Run all validation checks
    validate_strict()
else:
    # Run basic validation only
    validate_basic()
```

**get_recommended_workflow()**
```python
workflow = hints.get_recommended_workflow()
print(f"Recommended workflow: {workflow}")
# Based on preferences and historical patterns
```

## Usage Patterns

### Pattern 1: Initial User Profiling

```python
def initialize_user_profile(session_id: str):
    """Set up initial user preferences"""

    hints = ContextHints(db, session_id=session_id)

    # Ask user for preferences
    expertise = ask_user("Your expertise level?", ["beginner", "intermediate", "expert"])
    workflow = ask_user("Preferred workflow?", ["tdd", "doc-first", "impl-first"])
    style = ask_user("Communication style?", ["verbose", "concise", "balanced"])

    # Store preferences
    hints.set_expertise_level(expertise)
    hints.set_preference(PreferenceCategory.WORKFLOW, workflow)
    hints.set_preference(PreferenceCategory.COMMUNICATION, style)

    return hints
```

### Pattern 2: Task-Based Learning

```python
def execute_task_with_learning(task_type: str, spec_id: str):
    """Execute task and learn from results"""

    hints = ContextHints(db, session_id=current_session_id)

    # Get agent recommendations
    top_agents = hints.get_most_used_tools(3)
    recommended_agent = top_agents[0][0] if top_agents else "expert-backend"

    # Execute task
    start_time = time.time()
    agents_used = [recommended_agent, "manager-quality"]

    result = execute_with_agents(task_type, spec_id, agents_used)

    duration_ms = (time.time() - start_time) * 1000

    # Record pattern
    hints.record_task_pattern(
        task_type=task_type,
        metadata={
            "spec_id": spec_id,
            "agents_used": agents_used,
            "success": result.success,
            "duration_ms": duration_ms,
            "tools_used": agents_used
        }
    )

    return result
```

### Pattern 3: Adaptive Suggestion Engine

```python
def get_context_aware_suggestion(current_state: dict):
    """Get suggestion based on context and history"""

    hints = ContextHints(db, session_id=current_session_id)

    # Analyze patterns
    analysis = hints.analyze_workflow_patterns()

    # Get base suggestion
    suggestion = hints.suggest_next_action()

    # Enhance with workflow analysis
    if current_state["phase"] == "implementation":
        if analysis['success_rate'].get('testing', 0) > 0.8:
            return "Run tests first (high historical success rate)"

    # Check for common sequences
    common_seqs = analysis.get('common_sequences', [])
    if common_seqs:
        last_task = get_last_task_type()
        for (prev, next_task), count in common_seqs:
            if prev == last_task and count > 3:
                return f"Typically followed by: {next_task}"

    return suggestion or "No specific suggestion"
```

### Pattern 4: Workflow Optimization

```python
def optimize_workflow_based_on_history():
    """Adjust workflow based on success patterns"""

    hints = ContextHints(db, session_id=current_session_id)

    analysis = hints.analyze_workflow_patterns()
    patterns = hints.get_task_patterns(limit=50)

    # Analyze TDD success rate
    tdd_tasks = [p for p in patterns if p.get('workflow') == 'tdd']
    tdd_success = sum(1 for t in tdd_tasks if t.get('success')) / len(tdd_tasks) if tdd_tasks else 0

    # Analyze impl-first success rate
    impl_tasks = [p for p in patterns if p.get('workflow') == 'impl-first']
    impl_success = sum(1 for t in impl_tasks if t.get('success')) / len(impl_tasks) if impl_tasks else 0

    # Update workflow preference
    if tdd_success > impl_success + 0.2:  # 20% better
        hints.set_preference(PreferenceCategory.WORKFLOW, WorkflowPreference.TDD)
        print("Switched to TDD workflow (better historical success)")
    elif impl_success > tdd_success + 0.2:
        hints.set_preference(PreferenceCategory.WORKFLOW, WorkflowPreference.IMPL_FIRST)
        print("Switched to impl-first workflow (better historical success)")
```

### Pattern 5: Expertise-Based Adaptation

```python
def adapt_to_expertise_level():
    """Adjust behavior based on user expertise"""

    hints = ContextHints(db, session_id=current_session_id)
    level = hints.get_expertise_level()

    if level == ExpertiseLevel.BEGINNER:
        # Verbose explanations, strict validation
        hints.set_preference(PreferenceCategory.COMMUNICATION, CommunicationStyle.VERBOSE)
        hints.set_preference(PreferenceCategory.VALIDATION, ValidationStrictness.STRICT)
        return {
            "show_tips": True,
            "show_warnings": True,
            "auto_suggest": True
        }

    elif level == ExpertiseLevel.INTERMEDIATE:
        # Balanced, moderate validation
        hints.set_preference(PreferenceCategory.COMMUNICATION, CommunicationStyle.BALANCED)
        hints.set_preference(PreferenceCategory.VALIDATION, ValidationStrictness.MODERATE)
        return {
            "show_tips": False,
            "show_warnings": True,
            "auto_suggest": True
        }

    else:  # EXPERT
        # Concise, relaxed validation
        hints.set_preference(PreferenceCategory.COMMUNICATION, CommunicationStyle.CONCISE)
        hints.set_preference(PreferenceCategory.VALIDATION, ValidationStrictness.RELAXED)
        return {
            "show_tips": False,
            "show_warnings": False,
            "auto_suggest": False
        }
```

## Advanced Features

### Next-Action Suggestion Logic

```python
def suggest_next_action(self) -> Optional[str]:
    """
    Intelligent next-action suggestion based on:
    - Recent task history (last 24 hours)
    - Task type patterns
    - Success/failure outcomes
    - Workflow preferences
    """

    # Get recent tasks (last 24 hours)
    history = self._get_task_history()
    recent_cutoff = datetime.now() - timedelta(hours=24)
    recent_tasks = [
        task for task in history
        if datetime.fromisoformat(task["timestamp"]) > recent_cutoff
    ]

    if not recent_tasks:
        return None

    last_task = recent_tasks[-1]
    task_type = last_task.get("task_type")

    # Pattern-based suggestions
    if task_type == "implementation":
        if last_task.get("success"):
            return "Run /moai:3-sync to document recent implementation"
        else:
            return "Debug implementation issues or run tests"

    elif task_type == "planning":
        spec_id = last_task.get("spec_id")
        if spec_id:
            return f"Run /moai:2-run {spec_id} to start implementation"
        return "Start implementation phase"

    elif task_type == "testing":
        if last_task.get("success"):
            return "All tests passing - consider documentation or next feature"
        return "Fix failing tests"

    # Workflow-based suggestion
    workflow = self.get_preference(PreferenceCategory.WORKFLOW)
    if workflow == WorkflowPreference.TDD:
        return "Write tests first, then implement"

    return None
```

### Workflow Pattern Analysis

```python
def analyze_workflow_patterns(self) -> dict:
    """
    Comprehensive workflow analysis:
    - Success rates by task type
    - Common task sequences
    - Preferred agents
    - Average durations
    """

    history = self._get_task_history()

    # Success rates by task type
    success_by_type = defaultdict(list)
    for task in history:
        if "success" in task:
            success_by_type[task["task_type"]].append(task["success"])

    success_rate = {
        task_type: sum(successes) / len(successes)
        for task_type, successes in success_by_type.items()
    }

    # Common task sequences
    sequences = []
    for i in range(len(history) - 1):
        sequence = (history[i]["task_type"], history[i + 1]["task_type"])
        sequences.append(sequence)

    common_sequences = Counter(sequences).most_common(5)

    # Preferred agents
    all_agents = []
    for task in history:
        agents = task.get("agents_used", [])
        all_agents.extend(agents)

    preferred_agents = Counter(all_agents).most_common(5)

    # Average durations
    durations_by_type = defaultdict(list)
    for task in history:
        if "duration_ms" in task:
            durations_by_type[task["task_type"]].append(task["duration_ms"])

    average_duration = {
        task_type: sum(durations) / len(durations)
        for task_type, durations in durations_by_type.items()
    }

    return {
        "common_sequences": common_sequences,
        "success_rate": success_rate,
        "preferred_agents": preferred_agents,
        "average_duration": average_duration,
        "total_tasks": len(history)
    }
```

## Configuration

**Default Preferences**:
```python
DEFAULT_PREFERENCES = {
    PreferenceCategory.COMMUNICATION: CommunicationStyle.BALANCED,
    PreferenceCategory.WORKFLOW: WorkflowPreference.TDD,
    PreferenceCategory.VALIDATION: ValidationStrictness.MODERATE,
    PreferenceCategory.EXPERTISE: ExpertiseLevel.INTERMEDIATE,
}
```

**Pattern Learning Constants**:
```python
MAX_TASK_HISTORY = 100              # Last 100 tasks
PATTERN_CONFIDENCE_THRESHOLD = 0.7  # Pattern reliability
SUGGESTION_DECAY_HOURS = 24         # Suggestion relevance window
```

## Best Practices

1. **Initialize preferences early**
```python
hints = ContextHints(db, session_id=session_id)
# Preferences auto-initialize with defaults if not set
```

2. **Record all task outcomes**
```python
hints.record_task_pattern("implementation", {
    "success": True,  # Always include success/failure
    "duration_ms": 5000,
    "agents_used": [...],
    "tools_used": [...]
})
```

3. **Use TTL for temporary preferences**
```python
# Temporary debug mode
hints.set_preference("debug_mode", True, ttl_hours=1)
```

4. **Analyze patterns regularly**
```python
# Weekly pattern review
analysis = hints.analyze_workflow_patterns()
optimize_based_on_patterns(analysis)
```

5. **Combine with episodic memory**
```python
# Cross-reference preferences with actual outcomes
episodic = EpisodicMemory(db, project_id="moai-adk")
stats = episodic.get_outcome_statistics("agent_selection")

# Update tool preferences based on real success rates
if stats['success_rate'] > 80:
    hints.record_tool_usage(preferred_agent)
```

## Integration with Other Components

See [examples/distributed-memory.md](../examples/distributed-memory.md) for complete integration examples with SemanticMemory and EpisodicMemory.
