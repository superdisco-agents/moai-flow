# PRD-05: Neural Training

> Pattern learning and adaptive intelligence for MoAI

## Overview

| Field | Value |
|-------|-------|
| **Priority** | P2 (Important) |
| **Effort** | High (3+ months) |
| **Impact** | Medium |
| **Type** | Advanced Feature |

---

## Problem Statement

MoAI-Flow includes a neural training system that learns from successful patterns and adapts behavior. MoAI operates with static patterns, missing the opportunity to learn from usage.

### Current MoAI State

```
CURRENT: Static Pattern Execution

Task Execution
    │
    ▼
┌─────────────────┐
│  Fixed Rules    │ ← No learning
│  Fixed Agents   │ ← No adaptation
│  Fixed Patterns │ ← No optimization
└─────────────────┘
```

### Desired State (Long-term)

```
DESIRED: Adaptive Learning

Task Execution
    │
    ▼
┌─────────────────────────────────────┐
│           NEURAL SYSTEM             │
├─────────────────────────────────────┤
│ Pattern Collection → Model Training │
│         ↓                           │
│ Adaptive Recommendations            │
│         ↓                           │
│ Improved Future Execution           │
└─────────────────────────────────────┘
```

---

## Solution Options

### Option A: MoAI-Flow Neural MCP

Use MoAI-Flow's neural system via MCP:

```javascript
// Train on pattern
mcp__moai-flow__neural_train {
  pattern: "api_implementation",
  success: true,
  context: { ... }
}

// Get recommendations
mcp__moai-flow__neural_recommend {
  task_type: "database_migration"
}
```

**Pros**: Immediate, sophisticated
**Cons**: External dependency, black box

### Option B: Basic Pattern Logging

Start with simple pattern collection (no ML):

```json
{
  "patterns": {
    "enabled": true,
    "collect": ["task_completion", "error_recovery"],
    "storage": ".moai/patterns/"
  }
}
```

**Pros**: Low effort, foundational
**Cons**: No adaptive learning

### Option C: Progressive Enhancement (Recommended)

1. Start with pattern logging
2. Add analysis/reporting
3. Evaluate need for ML
4. Build or integrate neural if needed

---

## Recommended Solution: Option C

### Phase 1: Pattern Logging (Month 1)

**Task 1.1**: Add Pattern Collection

```json
{
  "patterns": {
    "enabled": true,
    "storage": ".moai/patterns/",
    "collect": {
      "task_completion": true,
      "error_occurrence": true,
      "agent_usage": true
    }
  }
}
```

**Task 1.2**: Pattern Format

```json
{
  "pattern_id": "pat-001",
  "type": "task_completion",
  "timestamp": "2025-11-29T10:00:00Z",
  "data": {
    "task_type": "api_implementation",
    "agent": "expert-backend",
    "duration_ms": 45000,
    "success": true,
    "files_created": 3,
    "tests_passed": 12
  },
  "context": {
    "framework": "fastapi",
    "language": "python"
  }
}
```

**Task 1.3**: PostTask Hook Integration

```bash
#!/bin/bash
# .moai/hooks/post-task-pattern.sh

# Collect pattern data
cat > ".moai/patterns/$(date +%Y%m%d_%H%M%S).json" << EOF
{
  "type": "task_completion",
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "agent": "$AGENT_TYPE",
  "result": "$RESULT",
  "duration_ms": $DURATION
}
EOF
```

### Phase 2: Pattern Analysis (Month 2)

**Task 2.1**: Analysis Script

```python
# .moai/scripts/analyze_patterns.py

import json
from pathlib import Path
from collections import defaultdict

def analyze_patterns():
    patterns = Path(".moai/patterns").glob("*.json")

    stats = defaultdict(lambda: {"count": 0, "success": 0, "total_duration": 0})

    for pattern_file in patterns:
        pattern = json.loads(pattern_file.read_text())
        agent = pattern.get("agent", "unknown")

        stats[agent]["count"] += 1
        if pattern.get("result") == "success":
            stats[agent]["success"] += 1
        stats[agent]["total_duration"] += pattern.get("duration_ms", 0)

    return generate_report(stats)
```

**Task 2.2**: Periodic Reports

```json
{
  "patterns": {
    "analysis": {
      "enabled": true,
      "schedule": "daily",
      "report_location": ".moai/reports/patterns/"
    }
  }
}
```

### Phase 3: Evaluation (Month 3)

**Task 3.1**: Evaluate Pattern Data

- How much data collected?
- What patterns emerge?
- Would ML provide value?

**Task 3.2**: Decision Point

Based on evaluation:
- If patterns are simple → Continue with analysis
- If ML would help → Evaluate MoAI-Flow neural or custom solution

### Phase 4: Optional ML Integration (Month 4+)

If ML is warranted:

**Option A**: MoAI-Flow Neural MCP

```json
{
  "mcpServers": {
    "moai-flow": {
      "command": "npx",
      "args": ["-y", "moai-flow@alpha", "mcp", "start"]
    }
  }
}
```

**Option B**: Custom ML Integration

```json
{
  "neural": {
    "enabled": true,
    "provider": "local",
    "model_path": ".moai/models/",
    "training": {
      "min_patterns": 100,
      "auto_train": false
    }
  }
}
```

---

## Technical Specification

### Pattern Types

| Type | Data Collected |
|------|---------------|
| `task_completion` | Agent, duration, result, files changed |
| `error_occurrence` | Error type, context, resolution |
| `agent_usage` | Agent type, frequency, success rate |
| `user_correction` | What was corrected, pattern |

### Storage Structure

```
.moai/patterns/
├── 2025/
│   └── 11/
│       └── 29/
│           ├── task_20251129_100000.json
│           ├── task_20251129_110000.json
│           └── error_20251129_120000.json
└── analysis/
    ├── weekly_2025-11-24.json
    └── monthly_2025-11.json
```

### Analysis Output

```json
{
  "period": "weekly",
  "date_range": "2025-11-24 to 2025-11-30",
  "summary": {
    "total_tasks": 156,
    "success_rate": 0.92,
    "avg_duration_ms": 42000
  },
  "by_agent": {
    "expert-backend": {
      "tasks": 45,
      "success_rate": 0.89,
      "avg_duration_ms": 55000
    },
    "manager-tdd": {
      "tasks": 32,
      "success_rate": 1.0,
      "avg_duration_ms": 38000
    }
  },
  "patterns_observed": [
    {
      "pattern": "api_first_development",
      "occurrences": 12,
      "success_rate": 0.92
    }
  ],
  "recommendations": [
    "expert-backend tasks taking longer than average",
    "Consider breaking complex API tasks into smaller units"
  ]
}
```

---

## Acceptance Criteria

### Phase 1
- [ ] Pattern collection enabled
- [ ] Task completion patterns logged
- [ ] Error patterns logged
- [ ] PostTask hook integration

### Phase 2
- [ ] Analysis script functional
- [ ] Weekly reports generated
- [ ] Agent performance visible

### Phase 3
- [ ] Evaluation complete
- [ ] ML decision documented
- [ ] Roadmap updated

### Phase 4 (if applicable)
- [ ] ML system integrated
- [ ] Training pipeline functional
- [ ] Recommendations generated

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Over-engineering | High | Medium | Start simple, evaluate need |
| Storage growth | Medium | Low | Retention policy |
| ML complexity | High | High | Defer until proven need |
| Privacy concerns | Low | Medium | Local storage only |

---

## Success Metrics

| Phase | Metric | Target |
|-------|--------|--------|
| 1 | Pattern collection | 100+ patterns/week |
| 2 | Analysis reports | Weekly generation |
| 3 | ML decision | Clear recommendation |
| 4 | (If ML) Accuracy | >80% useful recommendations |

---

## Related Documents

- [Neural Training System](../advanced/02-neural-training.md)
- [Cross-Session Memory](../advanced/03-cross-session-memory.md)
- [Performance Metrics](../advanced/05-performance-metrics.md)
- [PRD-00 Overview](PRD-00-overview.md)

---

## Timeline

```
Month 1: Pattern collection implementation
Month 2: Analysis and reporting
Month 3: Evaluation and decision
Month 4+: Optional ML integration

Total: 3-6 months depending on ML decision
```
