# PRD-08: Performance Metrics

> Comprehensive performance measurement for MoAI

## Overview

| Field | Value |
|-------|-------|
| **Priority** | P2 (Important) |
| **Effort** | Medium (4-6 weeks) |
| **Impact** | Medium |
| **Type** | Observability Enhancement |

---

## Problem Statement

MoAI-Flow has comprehensive performance metrics including 84.8% SWE-Bench score. MoAI has basic session metrics but lacks detailed performance tracking for tasks, agents, and operations.

### Current MoAI Metrics

```
CURRENT:

Session Metrics (basic):
├── Session duration
├── Tool usage counts
└── Error occurrences

Missing:
├── Token usage per task
├── Agent performance
├── Task duration
├── Success rates
└── Benchmark scores
```

### Desired Metrics

```
DESIRED:

Comprehensive Metrics:
├── Session
│   ├── Duration
│   ├── Token usage
│   └── Tool usage
├── Task
│   ├── Duration per task
│   ├── Success rate
│   └── Token usage
├── Agent
│   ├── Tasks completed
│   ├── Success rate
│   └── Average duration
├── Quality
│   ├── Test coverage
│   └── Lint scores
└── Trends
    ├── Daily reports
    └── Weekly summaries
```

---

## Solution

### Phase 1: Token Tracking (Week 1-2)

**Task 1.1**: Add Token Collection

```json
{
  "metrics": {
    "token_tracking": {
      "enabled": true,
      "track_per_task": true,
      "track_per_session": true
    }
  }
}
```

**Task 1.2**: Token Metrics Format

```json
{
  "token_usage": {
    "session_id": "sess-001",
    "total_tokens": 150000,
    "by_category": {
      "prompt": 45000,
      "completion": 105000
    },
    "by_task": {
      "task-001": 25000,
      "task-002": 35000
    }
  }
}
```

### Phase 2: Task Metrics (Week 3-4)

**Task 2.1**: Task Metrics Collection

```json
{
  "metrics": {
    "tasks": {
      "enabled": true,
      "track_duration": true,
      "track_result": true,
      "track_agent": true
    }
  }
}
```

**Task 2.2**: Task Metrics Format

```json
{
  "task_metrics": {
    "task_id": "task-001",
    "agent": "expert-backend",
    "started_at": "2025-11-29T10:00:00Z",
    "ended_at": "2025-11-29T10:01:30Z",
    "duration_ms": 90000,
    "result": "success",
    "tokens_used": 25000,
    "files_created": 2,
    "files_modified": 3
  }
}
```

### Phase 3: Agent Metrics (Week 5)

**Task 3.1**: Per-Agent Tracking

```json
{
  "metrics": {
    "agents": {
      "enabled": true,
      "aggregate_by_type": true
    }
  }
}
```

**Task 3.2**: Agent Metrics Format

```json
{
  "agent_metrics": {
    "expert-backend": {
      "tasks_completed": 45,
      "success_rate": 0.89,
      "avg_duration_ms": 55000,
      "total_tokens": 1125000,
      "period": "2025-11-01 to 2025-11-30"
    }
  }
}
```

### Phase 4: Reporting (Week 6)

**Task 4.1**: Daily Report Generation

```python
# .moai/scripts/generate_daily_report.py

def generate_daily_report():
    metrics = load_daily_metrics()

    report = {
        "date": today(),
        "summary": {
            "sessions": count_sessions(metrics),
            "tasks": count_tasks(metrics),
            "success_rate": calculate_success_rate(metrics),
            "tokens_used": sum_tokens(metrics)
        },
        "by_agent": aggregate_by_agent(metrics),
        "trends": compare_with_previous(metrics)
    }

    save_report(report)
```

**Task 4.2**: Report Format

```json
{
  "daily_report": {
    "date": "2025-11-29",
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
      "success_rate_change": "+5%",
      "efficiency_change": "+12%"
    }
  }
}
```

---

## Technical Specification

### Configuration Schema

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

    "tokens": {
      "track_usage": true,
      "track_per_task": true,
      "warn_threshold": 150000
    },

    "tasks": {
      "track_duration": true,
      "track_result": true,
      "track_files": true
    },

    "agents": {
      "track_per_agent": true,
      "aggregate_daily": true
    },

    "quality": {
      "test_coverage": false,
      "lint_scores": false
    },

    "reporting": {
      "daily_summary": true,
      "weekly_report": true,
      "export_format": "json"
    }
  }
}
```

### Metrics Collection Points

```
Session Start → Initialize metrics
    │
Task Start → Record task begin
    │
    └─► Track tokens
    └─► Track duration
    │
Task End → Record task result
    │
    └─► Update agent stats
    └─► Calculate metrics
    │
Session End → Aggregate metrics
    │
    └─► Generate reports
    └─► Save to storage
```

### Hook Integration

```bash
# PostTask hook for metrics
#!/bin/bash
# .moai/hooks/metrics-post-task.sh

TASK_ID="$1"
AGENT="$2"
RESULT="$3"
DURATION="$4"
TOKENS="$5"

# Append to daily metrics
METRICS_FILE=".moai/metrics/$(date +%Y-%m-%d).json"

jq ".tasks += [{
  \"task_id\": \"$TASK_ID\",
  \"agent\": \"$AGENT\",
  \"result\": \"$RESULT\",
  \"duration_ms\": $DURATION,
  \"tokens\": $TOKENS,
  \"timestamp\": \"$(date -u +"%Y-%m-%dT%H:%M:%SZ")\"
}]" "$METRICS_FILE" > "${METRICS_FILE}.tmp"
mv "${METRICS_FILE}.tmp" "$METRICS_FILE"
```

---

## Dashboard Concept (Future)

```
┌─────────────────────────────────────────────────────────────┐
│                  MOAI METRICS DASHBOARD                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ Success Rate │  │ Avg Duration │  │ Token Usage  │       │
│  │    92.4%     │  │    68.3s     │  │   425K/day   │       │
│  │    ▲ 3.1%    │  │    ▼ 15%     │  │    ▲ 8%      │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
│                                                              │
│  Agent Performance (Last 7 Days):                           │
│  ──────────────────────────────────────────────────────     │
│  expert-backend   ████████████████████ 89% (45 tasks)       │
│  manager-tdd      █████████████████████████ 100% (32 tasks) │
│  expert-frontend  ██████████████████ 85% (28 tasks)         │
│  expert-debug     ████████████████████████ 94% (18 tasks)   │
│                                                              │
│  Token Usage Trend:                                          │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ 500K ┤                    ╭──────                   │    │
│  │      │           ╭────────╯                         │    │
│  │ 250K ┤ ──────────╯                                  │    │
│  │      └──────────────────────────────────────────    │    │
│  │       Mon  Tue  Wed  Thu  Fri  Sat  Sun            │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Acceptance Criteria

### Phase 1 (Tokens)
- [ ] Token tracking enabled
- [ ] Per-task token tracking
- [ ] Token warning at threshold

### Phase 2 (Tasks)
- [ ] Task duration tracked
- [ ] Task results recorded
- [ ] Files modified tracked

### Phase 3 (Agents)
- [ ] Per-agent metrics
- [ ] Success rates calculated
- [ ] Average durations tracked

### Phase 4 (Reporting)
- [ ] Daily reports generated
- [ ] Weekly summaries available
- [ ] Export to JSON working

---

## Impact Assessment

### Visibility Gain

| Metric | Before | After |
|--------|--------|-------|
| Token usage | None | Full tracking |
| Task performance | None | Per-task metrics |
| Agent efficiency | None | Per-agent stats |
| Trends | None | Daily/weekly |

### Optimization Opportunities

With metrics, users can:
- Identify slow agents
- Optimize token usage
- Track improvement over time
- Make data-driven decisions

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Metrics collection | > 99% accuracy |
| Report generation | 100% automated |
| Performance overhead | < 2% |
| User adoption | 50% enable metrics |

---

## Related Documents

- [Performance Metrics](../advanced/05-performance-metrics.md)
- [Bottleneck Analysis](../advanced/06-bottleneck-analysis.md)
- [PRD-00 Overview](PRD-00-overview.md)

---

## Timeline

```
Week 1-2: Token tracking
Week 3-4: Task metrics
Week 5:   Agent metrics
Week 6:   Reporting

Total: 6 weeks
```
