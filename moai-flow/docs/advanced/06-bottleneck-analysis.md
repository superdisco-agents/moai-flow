# Bottleneck Analysis

> Identifying and resolving performance bottlenecks

## Overview

MoAI-Flow includes automatic bottleneck detection and analysis. **MoAI lacks this capability**, relying on manual observation for performance issues.

---

## Bottleneck Categories

### 1. Token Bottlenecks

Context window limitations:

```
┌─────────────────────────────────────────────────────────┐
│               TOKEN BOTTLENECK                          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Context Window: 200K tokens                            │
│                                                         │
│  ██████████████████████████████████░░░░░░ 85% used     │
│                                                         │
│  Breakdown:                                             │
│  ├── System Prompt:    15K (7.5%)                      │
│  ├── Conversation:     120K (60%)                      │
│  ├── File Contents:    30K (15%)                       │
│  └── Available:        35K (17.5%)                     │
│                                                         │
│  ⚠️ WARNING: Approaching context limit                 │
│  💡 Recommendation: Execute /clear                     │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 2. Execution Bottlenecks

Serial execution when parallel is possible:

```
Serial Execution (Bottleneck):
Task A ───────────►
                   Task B ───────────►
                                      Task C ───────────►
Total: 30 seconds

Parallel Execution (Optimized):
Task A ───────────►
Task B ───────────►
Task C ───────────►
Total: 10 seconds
```

### 3. Agent Bottlenecks

Agent capacity limitations:

```
┌─────────────────────────────────────────────────────────┐
│               AGENT BOTTLENECK                          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Active Agents: 5/5 (capacity reached)                  │
│                                                         │
│  Agent Queue:                                           │
│  ├── Waiting: 3 tasks                                  │
│  ├── Avg Wait: 45s                                     │
│  └── Est. Clear: 2min                                  │
│                                                         │
│  💡 Recommendation: Increase maxAgents or optimize     │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 4. I/O Bottlenecks

File and network operations:

```
I/O Analysis:
├── File Reads:  250 operations (2.3s total)
├── File Writes: 45 operations (1.1s total)
├── Network:     12 requests (8.5s total)  ← Bottleneck
└── Total I/O:   11.9s (40% of task time)
```

### 5. Memory Bottlenecks

Resource constraints:

```
Memory Analysis:
├── Heap Used:    1.2GB / 2GB (60%)
├── Peak:         1.8GB
├── GC Frequency: High (every 30s)
└── Recommendation: Reduce batch sizes
```

---

## Detection Methods

### 1. Profiling

```javascript
// Enable profiling
mcp__moai-flow__benchmark_run {
  type: "profile",
  target: "current_session",
  metrics: ["time", "tokens", "io", "memory"]
}
```

### 2. Threshold Alerts

```json
{
  "bottleneck_detection": {
    "enabled": true,
    "thresholds": {
      "token_usage": 0.80,
      "queue_length": 5,
      "wait_time_ms": 30000,
      "io_time_percent": 0.40,
      "memory_percent": 0.75
    },
    "alert_on_breach": true
  }
}
```

### 3. Pattern Analysis

```javascript
// Analyze execution patterns
patterns = analyze_execution_history({
  period: "last_hour",
  focus: ["serial_chains", "idle_time", "retries"]
})

// Returns:
{
  "bottlenecks": [
    {
      "type": "serial_execution",
      "location": "test_generation",
      "impact": "high",
      "suggestion": "parallelize_independent_tests"
    }
  ]
}
```

---

## MoAI Current State

### Token Management

MoAI has basic token awareness:

```json
// From CLAUDE.md Rule 4
{
  "token_management": {
    "context_threshold": 180000,
    "action": "guide_user_to_clear"
  }
}
```

### What MoAI Has

| Feature | Status |
|---------|--------|
| Token threshold warning | ✅ Manual |
| Context /clear guidance | ✅ Yes |
| Daily analysis | ✅ Basic |

### What MoAI Lacks

| Feature | Status |
|---------|--------|
| Automatic bottleneck detection | ❌ No |
| Parallel execution analysis | ❌ No |
| Agent queue monitoring | ❌ No |
| I/O profiling | ❌ No |
| Memory analysis | ❌ No |
| Optimization suggestions | ❌ No |

---

## Gap Analysis

| Capability | MoAI-Flow | MoAI |
|------------|-------------|------|
| Token monitoring | Automatic | Manual threshold |
| Execution profiling | Yes | No |
| Queue analysis | Yes | No |
| I/O profiling | Yes | No |
| Memory monitoring | Yes | No |
| Auto-suggestions | Yes | No |
| Bottleneck alerts | Yes | No |

---

## Proposed MoAI Bottleneck Detection

### Configuration

```json
{
  "bottleneck_detection": {
    "enabled": true,

    "token_monitoring": {
      "enabled": true,
      "warn_threshold": 0.75,
      "critical_threshold": 0.90,
      "auto_suggest_clear": true
    },

    "execution_analysis": {
      "enabled": true,
      "detect_serial_chains": true,
      "suggest_parallelization": true
    },

    "agent_queue": {
      "enabled": true,
      "warn_queue_length": 3,
      "track_wait_times": true
    },

    "reporting": {
      "log_bottlenecks": true,
      "include_in_daily_report": true
    }
  }
}
```

### Detection Implementation

```python
def detect_bottlenecks(session_data):
    bottlenecks = []

    # Token bottleneck
    if session_data.token_usage > WARN_THRESHOLD:
        bottlenecks.append({
            "type": "token",
            "severity": "warning" if usage < CRITICAL else "critical",
            "current": session_data.token_usage,
            "threshold": WARN_THRESHOLD,
            "suggestion": "Execute /clear to free context"
        })

    # Serial execution bottleneck
    serial_chains = find_serial_chains(session_data.tasks)
    for chain in serial_chains:
        if chain.parallelizable:
            bottlenecks.append({
                "type": "execution",
                "severity": "info",
                "location": chain.tasks,
                "suggestion": f"Tasks {chain.tasks} can run in parallel"
            })

    # Agent queue bottleneck
    if len(session_data.agent_queue) > QUEUE_WARN:
        bottlenecks.append({
            "type": "agent_queue",
            "severity": "warning",
            "queue_length": len(session_data.agent_queue),
            "suggestion": "Consider batching tasks or increasing agent limit"
        })

    return bottlenecks
```

### Alert Format

```
┌─────────────────────────────────────────────────────────┐
│ ⚠️ BOTTLENECK DETECTED                                 │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ Type: Token Usage                                       │
│ Severity: Warning                                       │
│ Current: 82% (164K / 200K tokens)                      │
│                                                         │
│ Suggestion:                                             │
│ Execute /clear to free context window.                  │
│ This will preserve work state in .moai/memory/          │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## Optimization Strategies

### 1. Token Optimization

```
Strategies:
├── Use /clear after major completions
├── Load files selectively (not entire codebase)
├── Use Explore agent for searches
├── Summarize large outputs
└── Delegate to agents (separate contexts)
```

### 2. Parallel Execution

```python
# Instead of:
Task(agent="backend", task="Build API")
# wait...
Task(agent="frontend", task="Build UI")
# wait...
Task(agent="tester", task="Write tests")

# Use parallel:
[Single message with all three Tasks]
Task(agent="backend", task="Build API")
Task(agent="frontend", task="Build UI")
Task(agent="tester", task="Write tests")
```

### 3. Agent Batching

```python
# Instead of many small tasks:
for file in files:
    Task(agent="reviewer", task=f"Review {file}")

# Batch into one:
Task(agent="reviewer", task=f"Review files: {', '.join(files)}")
```

---

## Recommendation

### Priority: P3 (Lower)

Bottleneck analysis is valuable but not critical.

### Phase 1: Token Monitoring (Week 1)

```json
{
  "bottleneck_detection": {
    "token_monitoring": {
      "enabled": true,
      "auto_suggest_clear": true
    }
  }
}
```

### Phase 2: Execution Analysis (Week 2-3)

```json
{
  "bottleneck_detection": {
    "execution_analysis": {
      "detect_serial_chains": true
    }
  }
}
```

### Phase 3: Full Analysis (Month 2+)

Complete bottleneck detection with all features.

---

## Summary

Bottleneck analysis helps identify performance issues proactively. MoAI-Flow has comprehensive bottleneck detection. MoAI has basic token awareness but lacks automatic detection. Adding token monitoring with auto-suggestions would be a valuable first step. Full bottleneck analysis is a longer-term enhancement that would help optimize MoAI workflows.
