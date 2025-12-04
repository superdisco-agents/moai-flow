# MoAI-Flow Hooks Usage and Customization Guide

This document provides comprehensive guidance on using and customizing MoAI-Flow hooks for seamless integration with Claude Code.

---

## Table of Contents

1. [Hook Architecture](#hook-architecture)
2. [Available Hooks](#available-hooks)
3. [Hook Context Reference](#hook-context-reference)
4. [Customization Guide](#customization-guide)
5. [Configuration Integration](#configuration-integration)
6. [Error Handling](#error-handling)
7. [Testing Hooks](#testing-hooks)
8. [Best Practices](#best-practices)

---

## Hook Architecture

### Hook Design Pattern

MoAI-Flow hooks follow a consistent architecture pattern:

```python
"""Hook description and purpose."""

import sys
from pathlib import Path

# Add moai_flow to Python path
moai_flow_path = Path(__file__).parent.parent.parent.parent / "moai_flow"
if moai_flow_path.exists():
    sys.path.insert(0, str(moai_flow_path.parent))

def execute(context):
    """
    Execute hook logic.

    Args:
        context: Dict containing hook context and metadata

    Returns:
        dict: Hook execution result with success status
    """
    try:
        # Hook implementation
        return {"success": True, "result": data}
    except Exception as e:
        return {"success": False, "error": str(e)}
```

### Hook Lifecycle

```
┌─────────────────────────────────────────────┐
│         Claude Code Session Start           │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│     swarm_lifecycle.py (session_start)      │
│  • Initialize SwarmCoordinator              │
│  • Create session ID                        │
│  • Return session metadata                  │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│          Normal Task Execution              │
└─────────────────┬───────────────────────────┘
                  │
        ┌─────────┴─────────┐
        │                   │
        ▼                   ▼
┌───────────────┐   ┌───────────────┐
│ pre_swarm_    │   │ post_swarm_   │
│ task.py       │   │ task.py       │
│               │   │               │
│ • Init coord  │   │ • Collect     │
│ • Setup DB    │   │   metrics     │
│ • Return ctx  │   │ • Apply heal  │
└───────────────┘   └───────────────┘
        │                   │
        └─────────┬─────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│          Claude Code Session End            │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│     swarm_lifecycle.py (session_end)        │
│  • Persist session state                    │
│  • Save to SwarmDB                          │
│  • Cleanup resources                        │
└─────────────────────────────────────────────┘
```

### Directory Structure

```
.claude/hooks/moai-flow/
├── config.json              # Hook configuration
├── pre_swarm_task.py       # Pre-task coordination hook
├── post_swarm_task.py      # Post-task metrics and healing hook
├── swarm_lifecycle.py      # Session lifecycle hook
└── lib/                    # Shared utilities
    ├── __init__.py
    ├── coordination_utils.py
    └── metrics_utils.py
```

---

## Available Hooks

### 1. pre_swarm_task.py

**Trigger**: Before each task execution

**Purpose**: Initialize swarm coordination context before task processing

**Location**: `.claude/hooks/moai-flow/pre_swarm_task.py`

#### Full Implementation

```python
"""
Pre-task hook for moai-flow swarm coordination.
Initializes coordination context before task execution.
"""

import sys
from pathlib import Path

# Add moai_flow to path
moai_flow_path = Path(__file__).parent.parent.parent.parent / "moai_flow"
if moai_flow_path.exists():
    sys.path.insert(0, str(moai_flow_path.parent))

def execute(context):
    """
    Execute pre-task coordination setup.

    Args:
        context: Task context with metadata

    Returns:
        dict: Updated context with coordination state
    """
    try:
        from moai_flow.core.swarm_coordinator import SwarmCoordinator
        from moai_flow.memory.swarm_db import SwarmDB

        # Initialize coordination if not already active
        if not context.get("swarm_active"):
            coordinator = SwarmCoordinator()
            db = SwarmDB()

            context["swarm_active"] = True
            context["coordinator"] = coordinator
            context["swarm_db"] = db

        return {"success": True, "context": context}

    except Exception as e:
        return {"success": False, "error": str(e)}
```

#### Input Context

```python
{
    "task_id": "task_001",
    "agent_id": "agent_001",
    "task_type": "code_review",
    "swarm_active": False  # Or True if already initialized
}
```

#### Output

```python
{
    "success": True,
    "context": {
        "task_id": "task_001",
        "agent_id": "agent_001",
        "task_type": "code_review",
        "swarm_active": True,
        "coordinator": <SwarmCoordinator instance>,
        "swarm_db": <SwarmDB instance>
    }
}
```

#### Use Cases

- Initialize swarm coordination for distributed tasks
- Set up shared memory context
- Prepare agent communication channels
- Load session state

---

### 2. post_swarm_task.py

**Trigger**: After each task execution

**Purpose**: Collect metrics and apply self-healing after task completion

**Location**: `.claude/hooks/moai-flow/post_swarm_task.py`

#### Full Implementation

```python
"""
Post-task hook for moai-flow swarm coordination.
Collects metrics and applies self-healing after task execution.
"""

import sys
from pathlib import Path

moai_flow_path = Path(__file__).parent.parent.parent.parent / "moai_flow"
if moai_flow_path.exists():
    sys.path.insert(0, str(moai_flow_path.parent))

def execute(context):
    """
    Execute post-task metrics collection and healing.

    Args:
        context: Task context with metadata and results

    Returns:
        dict: Metrics and healing status
    """
    try:
        from moai_flow.optimization.auto_healer import AutoHealer
        from moai_flow.monitoring.metrics_collector import MetricsCollector

        # Collect task metrics
        if context.get("swarm_active"):
            collector = MetricsCollector()
            metrics = collector.collect_task_metrics(context)

            # Check for anomalies and apply healing
            healer = AutoHealer()
            healing_result = healer.check_and_heal(metrics)

            return {
                "success": True,
                "metrics": metrics,
                "healing": healing_result
            }

        return {"success": True, "skipped": "swarm not active"}

    except Exception as e:
        return {"success": False, "error": str(e)}
```

#### Input Context

```python
{
    "swarm_active": True,
    "task_id": "task_001",
    "agent_id": "agent_001",
    "duration_ms": 1250,
    "result": "success",
    "errors": []
}
```

#### Output

```python
{
    "success": True,
    "metrics": {
        "task_id": "task_001",
        "duration_ms": 1250,
        "throughput": 12.3,
        "latency_p95": 580,
        "latency_p99": 920
    },
    "healing": {
        "anomalies_detected": 0,
        "healing_applied": False,
        "status": "healthy"
    }
}
```

#### Use Cases

- Track task performance metrics
- Detect performance degradation
- Apply auto-healing for slow agents
- Persist metrics to database

---

### 3. swarm_lifecycle.py

**Trigger**: Session start and session end

**Purpose**: Manage swarm initialization on session start and cleanup on session end

**Location**: `.claude/hooks/moai-flow/swarm_lifecycle.py`

#### Full Implementation

```python
"""
Session lifecycle hook for moai-flow swarm coordination.
Manages swarm initialization and cleanup.
"""

import sys
from pathlib import Path

moai_flow_path = Path(__file__).parent.parent.parent.parent / "moai_flow"
if moai_flow_path.exists():
    sys.path.insert(0, str(moai_flow_path.parent))

def execute(context):
    """
    Execute session lifecycle management.

    Args:
        context: Session context with event type (session_start/session_end)

    Returns:
        dict: Lifecycle operation status
    """
    try:
        event = context.get("event", "session_start")

        if event == "session_start":
            from moai_flow.core.swarm_coordinator import SwarmCoordinator

            # Initialize swarm session
            coordinator = SwarmCoordinator()
            session_id = coordinator.initialize_session()

            return {
                "success": True,
                "event": "session_start",
                "session_id": session_id
            }

        elif event == "session_end":
            from moai_flow.memory.swarm_db import SwarmDB

            # Cleanup and persist state
            db = SwarmDB()
            db.persist_session_state()
            db.cleanup()

            return {
                "success": True,
                "event": "session_end",
                "persisted": True
            }

        return {"success": True, "skipped": f"unknown event: {event}"}

    except Exception as e:
        return {"success": False, "error": str(e)}
```

#### Input Context (Session Start)

```python
{
    "event": "session_start",
    "user_id": "user_001",
    "timestamp": "2025-11-30T14:30:22Z"
}
```

#### Output (Session Start)

```python
{
    "success": True,
    "event": "session_start",
    "session_id": "swarm_001_20251130_143022"
}
```

#### Input Context (Session End)

```python
{
    "event": "session_end",
    "session_id": "swarm_001_20251130_143022",
    "timestamp": "2025-11-30T16:45:12Z"
}
```

#### Output (Session End)

```python
{
    "success": True,
    "event": "session_end",
    "persisted": True
}
```

#### Use Cases

- Initialize swarm on Claude Code session start
- Clean up resources on session end
- Persist session history to database
- Generate session summary

---

## Hook Context Reference

### Context Input Schema

Each hook receives a context dictionary with the following possible fields:

#### Pre-Task Hook Context

```python
{
    # Task identification
    "task_id": str,           # Unique task identifier
    "agent_id": str,          # Agent executing the task
    "task_type": str,         # Type of task (e.g., "code_review")

    # Swarm state
    "swarm_active": bool,     # Whether swarm is active
    "session_id": str,        # Current session ID (if exists)

    # Optional metadata
    "timestamp": str,         # ISO 8601 timestamp
    "user_id": str,           # User identifier
    "context_data": dict      # Additional context data
}
```

#### Post-Task Hook Context

```python
{
    # Task identification
    "task_id": str,           # Unique task identifier
    "agent_id": str,          # Agent that executed the task

    # Swarm state
    "swarm_active": bool,     # Whether swarm is active
    "session_id": str,        # Current session ID

    # Task results
    "duration_ms": int,       # Task execution time
    "result": str,            # Result status ("success", "failure")
    "errors": list,           # List of error messages
    "output": dict,           # Task output data

    # Optional metadata
    "timestamp": str,         # ISO 8601 timestamp
    "metrics": dict           # Pre-collected metrics (if any)
}
```

#### Lifecycle Hook Context

```python
{
    # Event type
    "event": str,             # "session_start" or "session_end"

    # Session identification
    "session_id": str,        # Session ID (for session_end)
    "user_id": str,           # User identifier

    # Timestamp
    "timestamp": str,         # ISO 8601 timestamp

    # Optional metadata
    "config": dict,           # Session configuration
    "state": dict             # Session state data
}
```

### Context Output Schema

Hooks must return a dictionary with the following structure:

#### Success Response

```python
{
    "success": True,
    "context": dict,          # Updated context (pre-task hook)
    "metrics": dict,          # Metrics data (post-task hook)
    "healing": dict,          # Healing result (post-task hook)
    "session_id": str,        # Session ID (lifecycle hook)
    "event": str,             # Event type (lifecycle hook)
    "persisted": bool,        # Persistence status (lifecycle hook)
    # ... other hook-specific fields
}
```

#### Failure Response

```python
{
    "success": False,
    "error": str              # Error message
}
```

---

## Customization Guide

### Customizing pre_swarm_task.py

#### Example: Add Custom Validation

```python
def execute(context):
    """Execute pre-task coordination setup with validation."""
    try:
        from moai_flow.core.swarm_coordinator import SwarmCoordinator
        from moai_flow.memory.swarm_db import SwarmDB

        # CUSTOM: Validate task requirements
        if not context.get("task_id"):
            return {
                "success": False,
                "error": "task_id is required in context"
            }

        # CUSTOM: Check swarm capacity
        coordinator = SwarmCoordinator()
        if coordinator.get_active_agent_count() >= coordinator.max_agents:
            return {
                "success": False,
                "error": "Swarm at maximum capacity"
            }

        # Initialize coordination if not already active
        if not context.get("swarm_active"):
            db = SwarmDB()

            context["swarm_active"] = True
            context["coordinator"] = coordinator
            context["swarm_db"] = db

            # CUSTOM: Log initialization
            db.log_event("swarm_init", context["task_id"])

        return {"success": True, "context": context}

    except Exception as e:
        return {"success": False, "error": str(e)}
```

#### Example: Initialize with Custom Topology

```python
def execute(context):
    """Execute pre-task coordination with custom topology."""
    try:
        from moai_flow.core.swarm_coordinator import SwarmCoordinator
        from moai_flow.memory.swarm_db import SwarmDB

        if not context.get("swarm_active"):
            # CUSTOM: Determine topology based on task type
            task_type = context.get("task_type", "default")
            topology_map = {
                "code_review": "mesh",
                "testing": "hierarchical",
                "deployment": "star",
                "default": "adaptive"
            }
            topology = topology_map.get(task_type, "adaptive")

            # Initialize with custom topology
            coordinator = SwarmCoordinator(topology=topology)
            db = SwarmDB()

            context["swarm_active"] = True
            context["coordinator"] = coordinator
            context["swarm_db"] = db
            context["topology"] = topology

        return {"success": True, "context": context}

    except Exception as e:
        return {"success": False, "error": str(e)}
```

---

### Customizing post_swarm_task.py

#### Example: Custom Metric Collection

```python
def execute(context):
    """Execute post-task with custom metrics."""
    try:
        from moai_flow.optimization.auto_healer import AutoHealer
        from moai_flow.monitoring.metrics_collector import MetricsCollector

        if context.get("swarm_active"):
            collector = MetricsCollector()

            # Standard metrics
            metrics = collector.collect_task_metrics(context)

            # CUSTOM: Add application-specific metrics
            metrics["custom_metric_1"] = calculate_custom_metric(context)
            metrics["custom_metric_2"] = analyze_task_complexity(context)

            # CUSTOM: Store metrics in custom database
            store_metrics_to_influxdb(metrics)

            # Check for anomalies and apply healing
            healer = AutoHealer()
            healing_result = healer.check_and_heal(metrics)

            # CUSTOM: Send alert if healing failed
            if not healing_result.get("success"):
                send_alert("Healing failed", healing_result)

            return {
                "success": True,
                "metrics": metrics,
                "healing": healing_result
            }

        return {"success": True, "skipped": "swarm not active"}

    except Exception as e:
        return {"success": False, "error": str(e)}

def calculate_custom_metric(context):
    """Calculate custom metric based on task context."""
    # Custom metric logic
    return context.get("duration_ms", 0) / 1000

def analyze_task_complexity(context):
    """Analyze task complexity score."""
    # Complexity analysis logic
    return len(context.get("output", {}))

def store_metrics_to_influxdb(metrics):
    """Store metrics to InfluxDB."""
    # InfluxDB integration logic
    pass

def send_alert(title, details):
    """Send alert notification."""
    # Alert integration logic
    pass
```

#### Example: Conditional Healing

```python
def execute(context):
    """Execute post-task with conditional healing."""
    try:
        from moai_flow.optimization.auto_healer import AutoHealer
        from moai_flow.monitoring.metrics_collector import MetricsCollector

        if context.get("swarm_active"):
            collector = MetricsCollector()
            metrics = collector.collect_task_metrics(context)

            # CUSTOM: Only apply healing if threshold exceeded
            healing_result = {"applied": False}

            if metrics.get("duration_ms", 0) > 5000:
                # Task took too long, apply healing
                healer = AutoHealer()
                healing_result = healer.check_and_heal(metrics)

            elif metrics.get("error_count", 0) > 3:
                # Too many errors, apply healing
                healer = AutoHealer()
                healing_result = healer.check_and_heal(metrics)

            else:
                healing_result = {
                    "applied": False,
                    "reason": "metrics within threshold"
                }

            return {
                "success": True,
                "metrics": metrics,
                "healing": healing_result
            }

        return {"success": True, "skipped": "swarm not active"}

    except Exception as e:
        return {"success": False, "error": str(e)}
```

---

### Customizing swarm_lifecycle.py

#### Example: Custom Session Initialization

```python
def execute(context):
    """Execute lifecycle with custom initialization."""
    try:
        event = context.get("event", "session_start")

        if event == "session_start":
            from moai_flow.core.swarm_coordinator import SwarmCoordinator
            from moai_flow.memory.swarm_db import SwarmDB

            # CUSTOM: Load configuration from context
            config = context.get("config", {})
            topology = config.get("topology", "adaptive")
            agent_count = config.get("agent_count", 3)

            # Initialize with custom configuration
            coordinator = SwarmCoordinator(
                topology=topology,
                agent_count=agent_count
            )
            session_id = coordinator.initialize_session()

            # CUSTOM: Store session metadata
            db = SwarmDB()
            db.save_session_metadata(session_id, {
                "user_id": context.get("user_id"),
                "config": config,
                "started_at": context.get("timestamp")
            })

            return {
                "success": True,
                "event": "session_start",
                "session_id": session_id,
                "topology": topology,
                "agent_count": agent_count
            }

        elif event == "session_end":
            from moai_flow.memory.swarm_db import SwarmDB

            db = SwarmDB()

            # CUSTOM: Generate session summary
            session_id = context.get("session_id")
            summary = db.generate_session_summary(session_id)

            # Persist state
            db.persist_session_state()

            # CUSTOM: Export session data
            export_session_data(session_id, summary)

            # Cleanup
            db.cleanup()

            return {
                "success": True,
                "event": "session_end",
                "persisted": True,
                "summary": summary
            }

        return {"success": True, "skipped": f"unknown event: {event}"}

    except Exception as e:
        return {"success": False, "error": str(e)}

def export_session_data(session_id, summary):
    """Export session data to external system."""
    # Export logic
    pass
```

---

## Configuration Integration

### Hook Configuration File

**Location**: `.claude/hooks/moai-flow/config.json`

```json
{
  "moai_flow": {
    "enabled": true,
    "default_topology": "adaptive",
    "default_agent_count": 3,
    "auto_healing": true,
    "metrics_collection": true,
    "consensus_timeout_ms": 5000
  }
}
```

### Loading Configuration in Hooks

```python
import json
from pathlib import Path

def load_hook_config():
    """Load hook configuration."""
    config_path = Path(__file__).parent / "config.json"
    with open(config_path) as f:
        return json.load(f)

def execute(context):
    """Execute hook with configuration."""
    try:
        # Load configuration
        config = load_hook_config()
        moai_config = config.get("moai_flow", {})

        # Check if moai-flow is enabled
        if not moai_config.get("enabled", True):
            return {"success": True, "skipped": "moai-flow disabled"}

        # Use configuration values
        topology = moai_config.get("default_topology", "adaptive")
        auto_healing = moai_config.get("auto_healing", True)

        # Hook logic here...

        return {"success": True}

    except Exception as e:
        return {"success": False, "error": str(e)}
```

### Main Configuration Integration

Hooks can also load the main MoAI-Flow configuration:

```python
import json
from pathlib import Path

def load_main_config():
    """Load main moai-flow configuration."""
    # Navigate to .moai/config/moai-flow.json
    config_path = (
        Path(__file__).parent.parent.parent.parent
        / ".moai" / "config" / "moai-flow.json"
    )
    with open(config_path) as f:
        return json.load(f)

def execute(context):
    """Execute hook with main configuration."""
    try:
        config = load_main_config()
        swarm_config = config["moai_flow"]["swarm"]

        # Use main configuration
        max_agents = swarm_config["max_agents"]
        consensus = swarm_config["consensus_algorithm"]

        # Hook logic...

        return {"success": True}

    except Exception as e:
        return {"success": False, "error": str(e)}
```

---

## Error Handling

### Error Handling Pattern

All hooks should follow this error handling pattern:

```python
def execute(context):
    """Execute hook with comprehensive error handling."""
    try:
        # Validate context
        if not isinstance(context, dict):
            raise ValueError("context must be a dictionary")

        # Hook logic
        result = perform_hook_logic(context)

        return {"success": True, "result": result}

    except ImportError as e:
        # Module import failed
        return {
            "success": False,
            "error": f"Import failed: {str(e)}",
            "error_type": "ImportError"
        }

    except ValueError as e:
        # Validation error
        return {
            "success": False,
            "error": f"Validation failed: {str(e)}",
            "error_type": "ValueError"
        }

    except Exception as e:
        # Catch-all for unexpected errors
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "error_type": type(e).__name__
        }
```

### Graceful Degradation

Hooks should degrade gracefully when moai_flow is unavailable:

```python
def execute(context):
    """Execute hook with graceful degradation."""
    try:
        # Try to import moai_flow
        from moai_flow.core.swarm_coordinator import SwarmCoordinator

        # Normal hook logic
        coordinator = SwarmCoordinator()
        # ...

        return {"success": True}

    except ImportError:
        # moai_flow not available, skip gracefully
        return {
            "success": True,
            "skipped": "moai_flow module not available",
            "degraded": True
        }

    except Exception as e:
        return {"success": False, "error": str(e)}
```

---

## Testing Hooks

### Unit Testing Hooks

```python
"""Test pre_swarm_task hook."""

import sys
from pathlib import Path

# Add hook directory to path
hook_dir = Path(__file__).parent.parent / "hooks" / "moai-flow"
sys.path.insert(0, str(hook_dir))

import pre_swarm_task

def test_pre_swarm_task_initialization():
    """Test swarm initialization in pre-task hook."""
    context = {
        "task_id": "task_001",
        "agent_id": "agent_001",
        "swarm_active": False
    }

    result = pre_swarm_task.execute(context)

    assert result["success"] == True
    assert "context" in result
    assert result["context"]["swarm_active"] == True

def test_pre_swarm_task_already_active():
    """Test hook when swarm already active."""
    context = {
        "task_id": "task_002",
        "agent_id": "agent_002",
        "swarm_active": True
    }

    result = pre_swarm_task.execute(context)

    assert result["success"] == True
    assert result["context"]["swarm_active"] == True

def test_pre_swarm_task_error_handling():
    """Test hook error handling."""
    # Invalid context
    context = None

    result = pre_swarm_task.execute(context)

    assert result["success"] == False
    assert "error" in result
```

### Integration Testing

```bash
#!/bin/bash
# Test hooks in realistic scenario

# 1. Test session start
echo "Testing session_start..."
python -c "
import sys
sys.path.insert(0, '.claude/hooks/moai-flow')
import swarm_lifecycle
result = swarm_lifecycle.execute({'event': 'session_start'})
print(result)
"

# 2. Test pre-task
echo "Testing pre_swarm_task..."
python -c "
import sys
sys.path.insert(0, '.claude/hooks/moai-flow')
import pre_swarm_task
result = pre_swarm_task.execute({'task_id': 'test_001', 'swarm_active': False})
print(result)
"

# 3. Test post-task
echo "Testing post_swarm_task..."
python -c "
import sys
sys.path.insert(0, '.claude/hooks/moai-flow')
import post_swarm_task
result = post_swarm_task.execute({
    'task_id': 'test_001',
    'swarm_active': True,
    'duration_ms': 1250
})
print(result)
"

# 4. Test session end
echo "Testing session_end..."
python -c "
import sys
sys.path.insert(0, '.claude/hooks/moai-flow')
import swarm_lifecycle
result = swarm_lifecycle.execute({'event': 'session_end'})
print(result)
"
```

---

## Best Practices

### 1. Keep Hooks Lightweight

Hooks should execute quickly to avoid delaying task execution:

```python
# ✅ Good: Fast initialization
def execute(context):
    try:
        if not context.get("swarm_active"):
            coordinator = SwarmCoordinator()
            context["swarm_active"] = True
        return {"success": True, "context": context}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ❌ Bad: Slow initialization
def execute(context):
    try:
        # Don't perform heavy computation in hooks
        analyze_entire_codebase()  # Slow!
        train_ml_model()  # Very slow!

        coordinator = SwarmCoordinator()
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}
```

### 2. Always Return Success Status

Every hook must return a dictionary with a `success` field:

```python
# ✅ Good: Always return success status
def execute(context):
    try:
        result = perform_operation()
        return {"success": True, "result": result}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ❌ Bad: Missing success status
def execute(context):
    try:
        return {"result": "some data"}  # Missing "success" field
    except Exception as e:
        raise  # Don't raise, return error dict
```

### 3. Use Type Hints

Use type hints for better code clarity:

```python
from typing import Dict, Any

def execute(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute hook logic.

    Args:
        context: Hook context dictionary

    Returns:
        dict: Hook execution result
    """
    try:
        # Hook logic
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}
```

### 4. Log Important Events

Use logging for debugging and monitoring:

```python
import logging
from pathlib import Path

# Set up logging
log_dir = Path(__file__).parent.parent.parent.parent / ".moai" / "logs" / "moai-flow"
log_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    filename=log_dir / "hooks.log",
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

def execute(context):
    """Execute hook with logging."""
    try:
        logger.info(f"Pre-task hook started for task {context.get('task_id')}")

        # Hook logic

        logger.info("Pre-task hook completed successfully")
        return {"success": True}

    except Exception as e:
        logger.error(f"Pre-task hook failed: {str(e)}")
        return {"success": False, "error": str(e)}
```

### 5. Handle Missing Dependencies

Gracefully handle missing moai_flow module:

```python
def execute(context):
    """Execute hook with dependency check."""
    try:
        from moai_flow.core.swarm_coordinator import SwarmCoordinator
    except ImportError:
        # moai_flow not installed, skip gracefully
        return {
            "success": True,
            "skipped": "moai_flow not available"
        }

    try:
        # Normal hook logic
        coordinator = SwarmCoordinator()
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}
```

### 6. Validate Context Input

Always validate context before processing:

```python
def execute(context):
    """Execute hook with validation."""
    try:
        # Validate context type
        if not isinstance(context, dict):
            return {
                "success": False,
                "error": "context must be a dictionary"
            }

        # Validate required fields
        required_fields = ["task_id", "agent_id"]
        for field in required_fields:
            if field not in context:
                return {
                    "success": False,
                    "error": f"Missing required field: {field}"
                }

        # Hook logic
        return {"success": True}

    except Exception as e:
        return {"success": False, "error": str(e)}
```

### 7. Document Hook Behavior

Provide clear docstrings and comments:

```python
def execute(context):
    """
    Execute pre-task coordination setup.

    This hook initializes the swarm coordination context before task execution.
    It sets up the SwarmCoordinator and SwarmDB if not already active.

    Args:
        context (dict): Task context with the following fields:
            - task_id (str): Unique task identifier
            - agent_id (str): Agent executing the task
            - swarm_active (bool): Whether swarm is already active

    Returns:
        dict: Hook execution result with the following structure:
            - success (bool): Whether hook executed successfully
            - context (dict): Updated context with swarm state (if success=True)
            - error (str): Error message (if success=False)

    Example:
        >>> context = {"task_id": "task_001", "swarm_active": False}
        >>> result = execute(context)
        >>> print(result["success"])
        True
    """
    try:
        # Hook logic
        return {"success": True, "context": context}
    except Exception as e:
        return {"success": False, "error": str(e)}
```

---

## Version

**Current Version**: 1.0.0

**Last Updated**: 2025-11-30

**Related Documentation**:
- [README.md](./README.md) - MoAI-Flow integration overview
- [INTEGRATION.md](./INTEGRATION.md) - Detailed integration guide
