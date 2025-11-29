# Post-Operation Hooks

> Cleanup, logging, and verification after operations

## Overview

Post-operation hooks execute AFTER an operation completes, providing opportunities for logging, cleanup, verification, and metrics collection.

---

## Hook Types

### 1. PostTask Hook

Triggered after task completion.

```javascript
// Hook configuration
{
  "PostTask": {
    "enabled": true,
    "timeout_ms": 5000,
    "actions": ["log_result", "metrics", "cleanup"]
  }
}
```

**Use Cases**:
- Log task results
- Collect metrics
- Trigger dependent tasks
- Send notifications

### 2. PostAgent Hook

Triggered after agent terminates.

```javascript
// Hook configuration
{
  "PostAgent": {
    "enabled": true,
    "timeout_ms": 3000,
    "actions": ["cleanup", "metrics", "resource_release"]
  }
}
```

**Use Cases**:
- Release resources
- Save agent state
- Log performance metrics
- Cleanup temporary files

### 3. PostFile Hook

Triggered after file operations.

```javascript
// Hook configuration
{
  "PostFile": {
    "enabled": true,
    "timeout_ms": 2000,
    "actions": ["verify", "backup", "notify"]
  }
}
```

**Use Cases**:
- Verify file integrity
- Update file index
- Trigger sync
- Notify watchers

### 4. PostSwarm Hook

Triggered after swarm shutdown.

```javascript
// Hook configuration
{
  "PostSwarm": {
    "enabled": true,
    "timeout_ms": 10000,
    "actions": ["metrics", "cleanup", "report"]
  }
}
```

**Use Cases**:
- Collect swarm metrics
- Generate performance report
- Cleanup shared resources
- Archive swarm state

---

## Implementation Patterns

### Pattern 1: Logging Hook

```bash
#!/bin/bash
# post-task-log.sh

TASK_ID="$1"
RESULT="$2"
DURATION="$3"

# Log to file
LOG_FILE=".moai/logs/tasks.log"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

echo "{\"timestamp\":\"$TIMESTAMP\",\"task_id\":\"$TASK_ID\",\"result\":\"$RESULT\",\"duration_ms\":$DURATION}" >> "$LOG_FILE"

# Log to metrics system (optional)
if command -v metrics-cli &> /dev/null; then
    metrics-cli record task_completion \
        --task_id="$TASK_ID" \
        --result="$RESULT" \
        --duration="$DURATION"
fi

exit 0
```

### Pattern 2: Cleanup Hook

```bash
#!/bin/bash
# post-agent-cleanup.sh

AGENT_ID="$1"
AGENT_TYPE="$2"

# Remove temporary files
TEMP_DIR=".moai/temp/agents/$AGENT_ID"
if [[ -d "$TEMP_DIR" ]]; then
    rm -rf "$TEMP_DIR"
fi

# Release locks
LOCK_FILE=".moai/locks/$AGENT_ID.lock"
if [[ -f "$LOCK_FILE" ]]; then
    rm "$LOCK_FILE"
fi

# Update agent registry
REGISTRY=".moai/cache/agent-registry.json"
if [[ -f "$REGISTRY" ]]; then
    jq "del(.agents[\"$AGENT_ID\"])" "$REGISTRY" > "${REGISTRY}.tmp"
    mv "${REGISTRY}.tmp" "$REGISTRY"
fi

echo "Cleanup completed for agent: $AGENT_ID"
exit 0
```

### Pattern 3: Verification Hook

```bash
#!/bin/bash
# post-file-verify.sh

FILE_PATH="$1"
OPERATION="$2"
EXPECTED_HASH="$3"

if [[ "$OPERATION" == "write" || "$OPERATION" == "edit" ]]; then
    # Verify file exists
    if [[ ! -f "$FILE_PATH" ]]; then
        echo "ERROR: File not found after operation"
        exit 1
    fi

    # Verify integrity (if hash provided)
    if [[ -n "$EXPECTED_HASH" ]]; then
        ACTUAL_HASH=$(sha256sum "$FILE_PATH" | cut -d' ' -f1)
        if [[ "$ACTUAL_HASH" != "$EXPECTED_HASH" ]]; then
            echo "ERROR: Hash mismatch"
            exit 1
        fi
    fi

    # Verify syntax (for code files)
    case "$FILE_PATH" in
        *.py)
            python -m py_compile "$FILE_PATH" 2>/dev/null || {
                echo "WARNING: Python syntax error"
            }
            ;;
        *.js|*.ts)
            if command -v eslint &> /dev/null; then
                eslint "$FILE_PATH" 2>/dev/null || {
                    echo "WARNING: JavaScript lint warning"
                }
            fi
            ;;
    esac
fi

echo "Verification passed"
exit 0
```

### Pattern 4: Metrics Collection Hook

```bash
#!/bin/bash
# post-swarm-metrics.sh

SWARM_ID="$1"
TOPOLOGY="$2"
DURATION="$3"
AGENT_COUNT="$4"

# Collect metrics
METRICS_FILE=".moai/reports/swarm-metrics-$SWARM_ID.json"

cat > "$METRICS_FILE" << EOF
{
  "swarm_id": "$SWARM_ID",
  "topology": "$TOPOLOGY",
  "duration_ms": $DURATION,
  "agent_count": $AGENT_COUNT,
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "memory_peak_mb": $(ps -o rss= -p $$ | awk '{print int($1/1024)}'),
  "cpu_avg_percent": $(top -l 1 | grep "CPU usage" | awk '{print $3}' | tr -d '%')
}
EOF

echo "Metrics saved to: $METRICS_FILE"
exit 0
```

---

## Hook Flow Diagram

```
[Operation Completed]
         │
         ▼
┌─────────────────────────────────┐
│        POST-OPERATION           │
├─────────────────────────────────┤
│                                 │
│  1. PostTask Hook               │
│     ├── Log results             │
│     ├── Collect metrics         │
│     └── Trigger dependents      │
│                                 │
│  2. PostAgent Hook              │
│     ├── Release resources       │
│     ├── Save state              │
│     └── Cleanup temps           │
│                                 │
│  3. PostFile Hook               │
│     ├── Verify integrity        │
│     ├── Update index            │
│     └── Trigger sync            │
│                                 │
│  4. PostSwarm Hook              │
│     ├── Generate report         │
│     ├── Archive state           │
│     └── Cleanup shared          │
│                                 │
└─────────────────────────────────┘
```

---

## Error Handling

### Non-Blocking Pattern

Post hooks should NOT block the success response:

```json
{
  "PostTask": {
    "enabled": true,
    "blocking": false,
    "on_error": "log_only",
    "retry": {
      "enabled": true,
      "max_attempts": 3,
      "delay_ms": 1000
    }
  }
}
```

### Async Execution

```javascript
// Post hooks can run async
{
  "PostTask": {
    "async": true,
    "queue": "post-operation-queue"
  }
}
```

---

## MoAI Current State

### Existing Post-Hooks

MoAI has `SessionEnd` with post-operation features:

```json
{
  "session_end": {
    "enabled": true,
    "metrics": { "enabled": true },
    "work_state": { "enabled": true },
    "cleanup": { "enabled": true },
    "summary": { "enabled": true }
  }
}
```

### Gap Analysis

| Post-Hook | Claude-Flow | MoAI |
|-----------|-------------|------|
| PostTask | Yes | No |
| PostAgent | Yes | No |
| PostFile | Yes | No |
| PostSwarm | Yes | No |
| SessionEnd | Yes | Yes |

---

## Recommendation

### Add to MoAI

```json
{
  "hooks": {
    "PostTask": {
      "enabled": true,
      "timeout_ms": 3000,
      "blocking": false,
      "command": ".moai/hooks/post-task.sh"
    },
    "PostAgent": {
      "enabled": true,
      "timeout_ms": 3000,
      "blocking": false,
      "command": ".moai/hooks/post-agent.sh"
    }
  }
}
```

### Benefits

1. **Observability**: Track all operations
2. **Cleanup**: Prevent resource leaks
3. **Verification**: Ensure operation success
4. **Metrics**: Performance insights
