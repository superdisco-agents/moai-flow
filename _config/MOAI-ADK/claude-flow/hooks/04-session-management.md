# Session Management Hooks

> Lifecycle hooks for session state management

## Overview

Session hooks manage the lifecycle of Claude Code sessions, handling initialization, state persistence, and cleanup.

---

## Hook Types

### 1. SessionStart Hook

Triggered when a new session begins.

```javascript
// Hook configuration
{
  "SessionStart": {
    "enabled": true,
    "timeout_ms": 5000,
    "actions": [
      "load_state",
      "initialize_context",
      "setup_environment"
    ]
  }
}
```

**Responsibilities**:
- Load previous session state
- Initialize context memory
- Setup working environment
- Display welcome message
- Load user preferences

### 2. SessionEnd Hook

Triggered when a session ends.

```javascript
// Hook configuration
{
  "SessionEnd": {
    "enabled": true,
    "timeout_ms": 10000,
    "actions": [
      "save_state",
      "collect_metrics",
      "cleanup",
      "generate_summary"
    ]
  }
}
```

**Responsibilities**:
- Save session state
- Collect usage metrics
- Cleanup temporary files
- Generate session summary
- Check uncommitted changes

### 3. SessionResume Hook

Triggered when resuming a previous session.

```javascript
// Hook configuration
{
  "SessionResume": {
    "enabled": true,
    "timeout_ms": 5000,
    "actions": [
      "restore_context",
      "validate_state",
      "refresh_tokens"
    ]
  }
}
```

**Responsibilities**:
- Restore previous context
- Validate saved state
- Refresh API tokens
- Resume pending tasks

### 4. SessionPause Hook

Triggered when session is paused (idle timeout).

```javascript
// Hook configuration
{
  "SessionPause": {
    "enabled": true,
    "timeout_ms": 3000,
    "actions": [
      "checkpoint_state",
      "release_resources"
    ]
  }
}
```

**Responsibilities**:
- Create state checkpoint
- Release held resources
- Pause background tasks

---

## Implementation Patterns

### Pattern 1: Session Start

```bash
#!/bin/bash
# session-start.sh

SESSION_ID="$1"
USER_ID="$2"

# Create session directory
SESSION_DIR=".moai/sessions/$SESSION_ID"
mkdir -p "$SESSION_DIR"

# Load previous state (if exists)
LAST_STATE=".moai/memory/last-session-state.json"
if [[ -f "$LAST_STATE" ]]; then
    cp "$LAST_STATE" "$SESSION_DIR/inherited-state.json"
    echo "Previous state loaded"
fi

# Load user preferences
CONFIG=".moai/config/config.json"
if [[ -f "$CONFIG" ]]; then
    LANGUAGE=$(jq -r '.language.conversation_language' "$CONFIG")
    USER_NAME=$(jq -r '.user.name' "$CONFIG")

    export MOAI_LANGUAGE="$LANGUAGE"
    export MOAI_USER_NAME="$USER_NAME"
fi

# Initialize session log
LOG_FILE="$SESSION_DIR/session.log"
echo "Session started: $(date -u +"%Y-%m-%dT%H:%M:%SZ")" > "$LOG_FILE"

exit 0
```

### Pattern 2: Session End

```bash
#!/bin/bash
# session-end.sh

SESSION_ID="$1"
DURATION="$2"

SESSION_DIR=".moai/sessions/$SESSION_ID"

# Save session state
STATE_FILE=".moai/memory/last-session-state.json"
cat > "$STATE_FILE" << EOF
{
  "session_id": "$SESSION_ID",
  "ended_at": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "duration_seconds": $DURATION,
  "working_directory": "$(pwd)",
  "last_files": $(git diff --name-only 2>/dev/null | head -10 | jq -R -s 'split("\n") | map(select(. != ""))')
}
EOF

# Collect metrics
METRICS_FILE=".moai/logs/sessions/session-$SESSION_ID.json"
mkdir -p "$(dirname "$METRICS_FILE")"

cat > "$METRICS_FILE" << EOF
{
  "session_id": "$SESSION_ID",
  "duration_seconds": $DURATION,
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "tools_used": {},
  "files_modified": [],
  "tasks_completed": 0
}
EOF

# Cleanup temp files
find .moai/temp -type f -mtime +1 -delete 2>/dev/null

# Check uncommitted changes
if [[ -n "$(git status --porcelain 2>/dev/null)" ]]; then
    echo "WARNING: Uncommitted changes detected"
fi

echo "Session ended: $SESSION_ID"
exit 0
```

### Pattern 3: Session Resume

```bash
#!/bin/bash
# session-resume.sh

SESSION_ID="$1"
PREVIOUS_SESSION_ID="$2"

# Load previous state
PREV_STATE=".moai/memory/last-session-state.json"
if [[ -f "$PREV_STATE" ]]; then
    PREV_DIR=$(jq -r '.working_directory' "$PREV_STATE")
    PREV_FILES=$(jq -r '.last_files | join(", ")' "$PREV_STATE")

    echo "Resuming from: $PREV_DIR"
    echo "Last files: $PREV_FILES"

    # Change to previous directory if different
    if [[ "$PREV_DIR" != "$(pwd)" && -d "$PREV_DIR" ]]; then
        cd "$PREV_DIR"
    fi
fi

# Restore context hints
CONTEXT_FILE=".moai/memory/context-hints.json"
if [[ -f "$CONTEXT_FILE" ]]; then
    # Context hints available for agent use
    export MOAI_CONTEXT_HINTS="$CONTEXT_FILE"
fi

exit 0
```

---

## State Persistence

### State Structure

```json
{
  "session_id": "abc123",
  "started_at": "2025-11-29T10:00:00Z",
  "ended_at": "2025-11-29T12:00:00Z",
  "duration_seconds": 7200,
  "working_directory": "/path/to/project",
  "context": {
    "last_files": ["src/main.py", "tests/test_main.py"],
    "last_tasks": ["SPEC-001", "SPEC-002"],
    "pending_todos": []
  },
  "metrics": {
    "tools_used": {
      "Read": 45,
      "Write": 12,
      "Edit": 23,
      "Task": 8
    },
    "tokens_used": 150000,
    "agents_spawned": 5
  }
}
```

### Cross-Session Memory

```json
{
  "memory": {
    "user_preferences": {
      "code_style": "explicit",
      "test_framework": "pytest",
      "commit_style": "conventional"
    },
    "project_patterns": {
      "architecture": "layered",
      "naming": "snake_case"
    },
    "learned_corrections": [
      {
        "pattern": "import order",
        "correction": "stdlib, third-party, local"
      }
    ]
  }
}
```

---

## MoAI Current State

### Existing Session Management

MoAI has comprehensive session hooks:

```json
{
  "session_end": {
    "enabled": true,
    "metrics": {
      "enabled": true,
      "save_location": ".moai/logs/sessions/"
    },
    "work_state": {
      "enabled": true,
      "save_location": ".moai/memory/last-session-state.json"
    },
    "cleanup": {
      "enabled": true,
      "temp_files": true,
      "cache_files": true
    },
    "warnings": {
      "uncommitted_changes": true
    },
    "summary": {
      "enabled": true,
      "max_lines": 5
    }
  }
}
```

### Comparison

| Feature | Claude-Flow | MoAI |
|---------|-------------|------|
| SessionStart | Yes | Yes |
| SessionEnd | Yes | Yes |
| SessionResume | Yes | Partial |
| SessionPause | Yes | No |
| State Persistence | Yes | Yes |
| Cross-Session Memory | Yes | Partial |
| Metrics Collection | Yes | Yes |

---

## Gap Analysis

### MoAI Strengths

1. **Comprehensive SessionEnd**: Full metrics, cleanup, warnings
2. **Configuration-driven**: JSON-based setup
3. **Graceful degradation**: Continues on hook failure

### MoAI Gaps

1. **SessionResume**: Limited context restoration
2. **SessionPause**: No idle timeout handling
3. **Cross-Session Learning**: No pattern learning persistence

---

## Recommendation

### Enhance MoAI Session Hooks

```json
{
  "session": {
    "start": {
      "enabled": true,
      "load_previous_state": true,
      "display_welcome": true
    },
    "resume": {
      "enabled": true,
      "restore_context": true,
      "validate_state": true
    },
    "pause": {
      "enabled": true,
      "idle_timeout_ms": 300000,
      "checkpoint_state": true
    },
    "end": {
      "enabled": true,
      "save_state": true,
      "collect_metrics": true,
      "cleanup": true
    }
  }
}
```

### Benefits

1. **Continuity**: Seamless session transitions
2. **Context preservation**: No lost work
3. **Resource efficiency**: Pause releases resources
4. **Learning**: Cross-session improvements
