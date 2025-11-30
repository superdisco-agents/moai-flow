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

---

## Implementation Status (Phase 7)

### Phase 7 Track 3 Week 1-3: Persistent Metrics Storage
**Status**: ✅ **COMPLETE (100%)**
**Completion Date**: 2025-11-29

#### Deliverables

1. ✅ **MetricsPersistence** (`moai_flow/monitoring/storage/metrics_persistence.py`)
   - SQLite backend with optimized schema and indexes
   - Write buffering (batch writes every 5s or 100 metrics)
   - Data compression for historical metrics (>7 days old)
   - Retention policies (7-day detailed, 30-day hourly, 90-day daily)
   - Connection pooling for concurrent access
   - Auto-cleanup jobs
   - **LOC**: ~600

2. ✅ **MetricsQuery** (`moai_flow/monitoring/storage/metrics_query.py`)
   - 10 comprehensive query methods
   - Filtering and pagination support
   - Aggregation functions (avg, sum, count, min, max, percentile)
   - Time-series aggregation (hour, day, week, month)
   - Top/bottom queries (top agents, slowest tasks)
   - Summary statistics
   - **LOC**: ~400

3. ✅ **MetricsExporter** (`moai_flow/monitoring/storage/metrics_exporter.py`)
   - JSON export (full nested structure)
   - CSV export (Excel/Google Sheets compatible)
   - Prometheus export (monitoring integration)
   - Grafana JSON data source format (optional)
   - Gzip compression support
   - **LOC**: ~300

4. ✅ **Metrics Dashboard** (`moai_flow/examples/metrics_dashboard.py`)
   - Real-time CLI dashboard with rich terminal UI
   - 5 dashboard sections (Summary, Agents, Queue, Resources, Trends)
   - Performance alerts (success rate, latency, tokens, queue)
   - Color-coded status indicators (green/yellow/red)
   - 5-second refresh rate
   - **LOC**: ~200

5. ✅ **Comprehensive Tests**
   - `tests/moai_flow/monitoring/storage/test_metrics_persistence.py`
   - `tests/moai_flow/monitoring/storage/test_metrics_query.py`
   - `tests/moai_flow/monitoring/storage/test_metrics_exporter.py`
   - **Coverage**: 90%+ (target achieved)

#### Performance Metrics

- **Write Performance**: <50ms (buffered), <2ms per metric average
- **Read Performance**: <100ms for 1M metrics
- **Query Latency**: <100ms for aggregation queries
- **Compression Ratio**: 50%+ reduction for historical data
- **Test Coverage**: 90%+ across all components

#### Success Criteria Met

- ✅ SQLite persistence working (write buffer, compression, retention)
- ✅ Query interface functional (10 methods, all tested)
- ✅ 3 export formats working (JSON, CSV, Prometheus)
- ✅ CLI dashboard functional (real-time, 5 sections, alerts)
- ✅ Tests passing (90%+ coverage)
- ✅ PRD-08 Phase 7 Track 3 Week 1-3 marked as 100% complete

#### Documentation

- ✅ Comprehensive README: `moai_flow/monitoring/storage/README.md`
- ✅ Usage examples for all components
- ✅ Migration guide from Phase 6A
- ✅ Configuration examples
- ✅ Performance benchmarks

#### Next Steps

**Phase 7 Track 3 Week 4-6**: PRD-09 Self-Healing Extensions
- Auto-remediation engine
- Predictive failure detection
- Dynamic resource allocation
- Self-tuning performance optimization

---

**Implementation**: MoAI-Flow Core Team
**Review Status**: Ready for Review
**Ready for**: Phase 7 Track 3 Week 4-6 (PRD-09)
