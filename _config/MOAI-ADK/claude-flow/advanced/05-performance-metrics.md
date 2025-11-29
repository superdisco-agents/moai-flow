# Performance Metrics

> Benchmarking and performance measurement

## Overview

Claude-Flow includes comprehensive performance measurement, including 84.8% SWE-Bench score. **MoAI has basic session metrics** but lacks benchmark integration and detailed performance tracking.

---

## Claude-Flow Performance System

### Benchmark Results

```
┌─────────────────────────────────────────────────────────┐
│              CLAUDE-FLOW BENCHMARKS                     │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  SWE-Bench Verified:     84.8%                         │
│  Task Completion Rate:   94.2%                         │
│  Avg Task Duration:      45.3s                         │
│  Token Efficiency:       87.5%                         │
│  Error Recovery Rate:    91.0%                         │
│                                                         │
│  Agent Performance:                                     │
│  ├── Researcher:  92.1% accuracy                       │
│  ├── Coder:       88.5% first-pass success             │
│  ├── Tester:      95.3% coverage achievement           │
│  └── Reviewer:    89.7% issue detection                │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Metric Categories

| Category | Metrics |
|----------|---------|
| **Completion** | Success rate, partial completions, failures |
| **Efficiency** | Token usage, time per task, parallel factor |
| **Quality** | Test coverage, bug density, code review scores |
| **Reliability** | Error rate, recovery rate, uptime |
| **Scalability** | Agent count, concurrent tasks, memory usage |

---

## MCP Tools for Metrics

### Run Benchmark

```javascript
mcp__claude-flow__benchmark_run {
  type: "swe-bench",
  iterations: 100,
  config: {
    warmup: 10,
    timeout_per_task: 300000,
    parallel: true
  }
}
```

### Get Agent Metrics

```javascript
mcp__claude-flow__agent_metrics {
  agentId: "coder-1",
  period: "last_24h"
}

// Returns:
{
  "agent_id": "coder-1",
  "metrics": {
    "tasks_completed": 47,
    "success_rate": 0.89,
    "avg_duration_ms": 32400,
    "tokens_used": 245000,
    "files_created": 23,
    "files_modified": 89,
    "lines_of_code": 2340,
    "test_coverage": 0.87
  }
}
```

### Get Swarm Metrics

```javascript
mcp__claude-flow__swarm_monitor {
  swarmId: "swarm-123",
  metrics: ["throughput", "latency", "efficiency"]
}

// Returns:
{
  "swarm_id": "swarm-123",
  "metrics": {
    "throughput": {
      "tasks_per_minute": 12.5,
      "peak": 18.2
    },
    "latency": {
      "avg_ms": 2340,
      "p95_ms": 5600,
      "p99_ms": 12000
    },
    "efficiency": {
      "token_utilization": 0.78,
      "parallel_factor": 3.2,
      "idle_time_percent": 8.5
    }
  }
}
```

### Get Task Metrics

```javascript
mcp__claude-flow__task_status {
  taskId: "task-456",
  includeMetrics: true
}

// Returns:
{
  "task_id": "task-456",
  "status": "completed",
  "metrics": {
    "duration_ms": 45000,
    "tokens_used": 12500,
    "steps_completed": 5,
    "retries": 0,
    "agent_switches": 2
  }
}
```

---

## Performance Dashboard Concept

```
┌─────────────────────────────────────────────────────────────┐
│                  PERFORMANCE DASHBOARD                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ Success Rate │  │ Avg Duration │  │ Token Usage  │       │
│  │    94.2%     │  │    45.3s     │  │   87.5%      │       │
│  │    ▲ 2.1%    │  │    ▼ 12%     │  │    ▲ 5%      │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                 Task Completion Trend                │    │
│  │  100% ┤                                              │    │
│  │       │     ╭───────────╮                           │    │
│  │   75% ┤   ╭─╯           ╰──╮    ╭──────            │    │
│  │       │ ╭─╯                ╰────╯                   │    │
│  │   50% ┤─╯                                           │    │
│  │       └──────────────────────────────────────────   │    │
│  │        Mon  Tue  Wed  Thu  Fri  Sat  Sun           │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  Top Agents by Performance:                                  │
│  1. tester-1      ████████████████████ 95.3%                │
│  2. researcher-2  ██████████████████   92.1%                │
│  3. reviewer-1    █████████████████    89.7%                │
│  4. coder-1       ████████████████     88.5%                │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## MoAI Current Metrics

### Session Metrics

MoAI collects basic session metrics:

```json
{
  "session_end": {
    "metrics": {
      "enabled": true,
      "save_location": ".moai/logs/sessions/"
    }
  }
}
```

### Daily Analysis

```json
{
  "daily_analysis": {
    "enabled": true,
    "analyze_sessions": true,
    "analyze_tools": true,
    "analyze_errors": true,
    "report_location": ".moai/reports/daily-"
  }
}
```

### Current Metric Types

| Metric | MoAI Status |
|--------|-------------|
| Session duration | ✅ Tracked |
| Tool usage counts | ✅ Tracked |
| Error occurrences | ✅ Tracked |
| Files modified | ⚠️ Partial |
| Token usage | ❌ Not tracked |
| Agent performance | ❌ Not tracked |
| Test coverage | ❌ Not tracked |
| Benchmark scores | ❌ Not tracked |

---

## Gap Analysis

| Feature | Claude-Flow | MoAI |
|---------|-------------|------|
| Session Metrics | Yes | Yes |
| Tool Usage | Yes | Yes |
| Error Tracking | Yes | Yes |
| Token Metrics | Yes | No |
| Agent Metrics | Yes | No |
| Swarm Metrics | Yes | No |
| Benchmarks | Yes (SWE-Bench) | No |
| Dashboard | Yes | No |
| Trend Analysis | Yes | Partial |

---

## Proposed MoAI Metrics

### Enhanced Configuration

```json
{
  "metrics": {
    "enabled": true,
    "storage": ".moai/metrics/",

    "session": {
      "duration": true,
      "tools_used": true,
      "files_modified": true,
      "tasks_completed": true
    },

    "performance": {
      "token_usage": true,
      "task_duration": true,
      "success_rate": true,
      "error_rate": true
    },

    "agents": {
      "track_per_agent": true,
      "metrics": ["tasks", "duration", "success_rate"]
    },

    "quality": {
      "test_coverage": true,
      "lint_scores": true,
      "code_complexity": false
    },

    "reporting": {
      "daily_summary": true,
      "weekly_report": true,
      "export_format": "json"
    }
  }
}
```

### Metric Collection Points

```python
# Task start
metrics.record("task_start", {
    "task_id": task.id,
    "type": task.type,
    "agent": task.agent
})

# Task end
metrics.record("task_end", {
    "task_id": task.id,
    "duration_ms": duration,
    "success": result.success,
    "tokens_used": result.tokens
})

# Agent spawn
metrics.record("agent_spawn", {
    "agent_id": agent.id,
    "type": agent.type
})

# Agent complete
metrics.record("agent_complete", {
    "agent_id": agent.id,
    "tasks_completed": count,
    "success_rate": rate
})
```

### Report Format

```json
{
  "report_date": "2025-11-29",
  "period": "daily",
  "summary": {
    "sessions": 3,
    "total_duration_hours": 4.5,
    "tasks_completed": 24,
    "success_rate": 0.92,
    "tokens_used": 450000
  },
  "by_agent": {
    "expert-backend": {
      "tasks": 8,
      "success_rate": 0.88,
      "avg_duration_s": 120
    },
    "manager-tdd": {
      "tasks": 6,
      "success_rate": 1.0,
      "avg_duration_s": 180
    }
  },
  "trends": {
    "success_rate": "+5% vs last week",
    "efficiency": "+12% token savings"
  }
}
```

---

## Benchmark Integration

### SWE-Bench Compatibility

To measure against SWE-Bench:

```json
{
  "benchmarks": {
    "swe_bench": {
      "enabled": false,
      "test_set": "verified",
      "report_path": ".moai/benchmarks/"
    }
  }
}
```

### Custom Benchmarks

```json
{
  "benchmarks": {
    "custom": {
      "enabled": true,
      "tests": [
        {
          "name": "api_implementation",
          "description": "Build REST API from spec",
          "timeout_s": 300,
          "success_criteria": ["tests_pass", "coverage > 80%"]
        }
      ]
    }
  }
}
```

---

## Recommendation

### Priority: P2 (Medium)

Metrics improve visibility but aren't blocking.

### Phase 1: Token Tracking (Week 1)

```json
{
  "metrics": {
    "performance": {
      "token_usage": true
    }
  }
}
```

### Phase 2: Agent Metrics (Week 2)

```json
{
  "metrics": {
    "agents": {
      "track_per_agent": true
    }
  }
}
```

### Phase 3: Reports (Week 3-4)

```json
{
  "metrics": {
    "reporting": {
      "daily_summary": true,
      "weekly_report": true
    }
  }
}
```

---

## Summary

Claude-Flow has comprehensive performance metrics including benchmark scores. MoAI has basic session metrics but lacks detailed performance tracking. Adding token usage tracking and per-agent metrics would provide valuable insights. Benchmark integration is lower priority but valuable for measuring improvements over time.
