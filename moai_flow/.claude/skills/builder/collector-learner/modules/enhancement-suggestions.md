# Module: Enhancement Suggestions

## Overview

Guidelines for suggesting improvements beyond simple copying. The learner doesn't just recommend merging—it identifies opportunities to make components even better.

---

## The Enhancement Mindset

```
NOT: "A has X, B doesn't. Copy X to B."
BUT: "A has X. Here's how X could be even better,
      and here's what B could add while merging."
```

---

## Enhancement Types

### 1. Add Module

**When**: Gap in documentation or functionality.

```markdown
## Enhancement: Add Module

**Target**: moai-connector-github
**Type**: Add Module
**Suggested Module**: `error-handling.md`

**Rationale**:
Current skill documents happy paths well but lacks:
- Rate limiting recovery
- Auth failure handling
- Network timeout patterns

**Implementation**:
Create `modules/error-handling.md` with:
- Common error codes and meanings
- Recovery strategies for each
- Retry patterns with backoff
```

---

### 2. Add Script

**When**: Repetitive manual task could be automated.

```markdown
## Enhancement: Add Script

**Target**: moai-flow-collector
**Type**: Add Script
**Suggested Script**: `scripts/flow_quick_scan.py`

**Rationale**:
Current scanning requires reading SKILL.md instructions
and running multiple commands manually. A script could:
- Accept workspace path as argument
- Output JSON directly
- Handle errors gracefully

**Implementation**:
```python
#!/usr/bin/env python3
"""Quick scan a MoAI workspace and output JSON."""

import json
import subprocess
from pathlib import Path

def scan_workspace(path: str) -> dict:
    # ... implementation
    pass
```
```

---

### 3. Add Workflow

**When**: Multi-step process needs orchestration.

```markdown
## Enhancement: Add Workflow

**Target**: moai-flow-consolidator
**Type**: Add Workflow
**Suggested Workflow**: `workflow/auto-merge.md`

**Rationale**:
Currently merging requires manual:
1. Review collection report
2. Decide what to merge
3. Copy files
4. Update references

A workflow could automate steps 3-4 after human
approves step 2.

**TOON Specification**:
```yaml
trigger: learning_report_approved
steps:
  - copy_approved_components
  - update_cross_references
  - validate_result
  - generate_summary
```
```

---

### 4. Restructure

**When**: Organization is poor or inconsistent.

```markdown
## Enhancement: Restructure

**Target**: legacy-skill-x
**Type**: Restructure
**Current Structure**:
```
legacy-skill-x/
├── README.md (1200 lines, everything in one file)
└── helper.py
```

**Suggested Structure**:
```
legacy-skill-x/
├── SKILL.md (overview, 200 lines)
├── modules/
│   ├── core-concepts.md
│   ├── advanced-usage.md
│   └── troubleshooting.md
└── scripts/
    └── helper.py
```

**Rationale**:
- Follows TRUST-5 tier 3 patterns
- Easier to navigate
- Each module has single focus
```

---

### 5. Merge Ideas

**When**: Both versions have unique value.

```markdown
## Enhancement: Merge Ideas

**Target**: builder-skill
**Versions**: A (workflow support) + B (UV templates)

**Current State**:
- A added: `workflow/` with TOON automation
- B added: `scripts/` with UV script templates

**Suggested Merge**:
1. Take A's `workflow/` directory entirely
2. Take B's `scripts/` directory entirely
3. Merge SKILL.md:
   - Use A's structure (more recent)
   - Add B's script examples section
4. Add cross-references between workflow and scripts

**Result**: Combined skill more complete than either
```

---

## Enhancement Quality Criteria

Before suggesting an enhancement, verify:

| Criterion | Question | Required |
|-----------|----------|----------|
| Value | Does this measurably improve the component? | Yes |
| Feasibility | Can this be implemented reasonably? | Yes |
| Consistency | Does it follow MoAI patterns? | Yes |
| Scope | Is it appropriately sized? | Yes |
| Clarity | Is the suggestion actionable? | Yes |

---

## Enhancement Effort Estimation

| Level | Definition | Examples |
|-------|------------|----------|
| **Low** | < 30 min, no new patterns | Add missing example |
| **Medium** | 30-120 min, follows patterns | Add new module |
| **High** | 2-8 hours, some research | Add workflow system |
| **Very High** | 1+ days, significant design | Major restructure |

---

## Enhancement Output Format

```json
{
  "enhancements": [
    {
      "id": "enh-001",
      "target": "moai-connector-github",
      "type": "add_module",
      "title": "Add error handling module",
      "description": "Document error codes and recovery patterns",
      "rationale": "Current skill lacks error guidance",
      "effort": "medium",
      "priority": "high",
      "implementation": {
        "files_to_create": ["modules/error-handling.md"],
        "files_to_modify": ["SKILL.md"],
        "outline": "1. Common errors\n2. Recovery patterns\n3. Examples"
      },
      "dependencies": [],
      "confidence": "high"
    }
  ]
}
```

---

## Enhancement Prioritization

### Priority Matrix

| Impact / Effort | Low Effort | Medium Effort | High Effort |
|-----------------|------------|---------------|-------------|
| **High Impact** | Do First | Do Second | Plan Carefully |
| **Medium Impact** | Do Second | Consider | Defer |
| **Low Impact** | Maybe | Probably Not | No |

### Auto-Priority Rules

```
IF effort = "low" AND value = "high":
    priority = "critical"
ELIF effort = "low" AND value = "medium":
    priority = "high"
ELIF effort = "medium" AND value = "high":
    priority = "high"
ELIF effort = "high" AND value = "high":
    priority = "medium"
ELSE:
    priority = "low"
```

---

## When NOT to Suggest Enhancements

- Component is deprecated or being replaced
- Enhancement conflicts with established patterns
- Effort greatly exceeds value
- Enhancement requires external dependencies
- Component owner has different vision
