# Comparison Table Formatting

**ANSI table formatting for branch and component comparisons**

> **Version**: 1.0.0
> **Part of**: collector-ui skill
> **Last Updated**: 2025-12-04

---

## Overview

Comparison tables provide clear visual representation of multi-source comparisons in terminal output.

---

## Table Types

### 1. Branch Comparison Matrix

Compare components across multiple branches:

```
Branch Comparison Matrix
========================

+----------------------+-------+------+-------------+-------------+--------+
| Component            | Local | main | SPEC-first  | workspace   | Best   |
+----------------------+-------+------+-------------+-------------+--------+
| collector-scan       | [88]  |  -   |     -       |     -       | LOCAL  |
| foundation-core      |  72   |  75  |    [91]     |     85      | SPEC   |
| decision-framework   | [85]  |  80  |     88      |     -       | MERGE  |
| builder-skill        |  78   | [82] |     80      |     -       | main   |
| tdd-integration      |  70   |  72  |     75      |    [80]     | work   |
+----------------------+-------+------+-------------+-------------+--------+

Legend:
  [N]  = Best score (highlighted)
  -    = Not present in branch
  MERGE = Scores within 10 points, recommend merge
```

### 2. Action Summary Table

Show recommended sync actions:

```
Sync Action Summary
===================

+----------------------+--------------+------------------+-------------+
| Component            | Action       | Source           | Impact      |
+----------------------+--------------+------------------+-------------+
| collector-scan       | PRESERVE     | local            | Keep local  |
| foundation-core      | UPDATE       | SPEC-first       | +19 points  |
| decision-framework   | SMART MERGE  | local + main     | +3 points   |
| builder-skill        | UPDATE       | main             | +4 points   |
| tdd-integration      | UPDATE       | workspace        | +10 points  |
+----------------------+--------------+------------------+-------------+

Summary:
  PRESERVE:    1 component
  UPDATE:      3 components
  SMART MERGE: 1 component
  SKIP:        0 components
```

### 3. Tier Distribution Table

Show branches by priority tier:

```
Branch Tier Distribution
========================

+--------+---------------------------+-------+--------+------------------+
| Tier   | Branch                    | Score | Status | Recommended      |
+--------+---------------------------+-------+--------+------------------+
| 1      | feature/SPEC-first        |  91   | Active | Merge ASAP       |
| 1      | hotfix/security-patch     |  95   | Active | Critical         |
+--------+---------------------------+-------+--------+------------------+
| 2      | feature/workspace         |  82   | Active | This sprint      |
| 2      | feature/tdd-integration   |  78   | Active | This sprint      |
| 2      | feature/refactor          |  76   | Active | This sprint      |
+--------+---------------------------+-------+--------+------------------+
| 3      | docs/readme-updates       |  65   | Active | When convenient  |
+--------+---------------------------+-------+--------+------------------+
| 4      | feature/old-experiment    |  55   | Stale  | Review or close  |
+--------+---------------------------+-------+--------+------------------+
```

### 4. Score Breakdown Table

Detailed scoring for single component:

```
Score Breakdown: foundation-core
================================

+-------------------+-------+--------+-------+-----------+--------+
| Criterion         | Local | main   | SPEC  | workspace | Weight |
+-------------------+-------+--------+-------+-----------+--------+
| Structure         |  15   |   16   | [18]  |    17     |  20%   |
| Documentation     |  12   |   14   | [17]  |    15     |  20%   |
| Functionality     |  20   |   21   | [23]  |    22     |  25%   |
| Quality           |  15   |   14   | [19]  |    18     |  20%   |
| Freshness         |  10   |   10   | [14]  |    13     |  15%   |
+-------------------+-------+--------+-------+-----------+--------+
| TOTAL             |  72   |   75   | [91]  |    85     | 100%   |
+-------------------+-------+--------+-------+-----------+--------+

Best Source: feature/SPEC-first (Score: 91)
Recommendation: UPDATE from SPEC-first
```

### 5. Contribution Summary Table

Local innovations for upstream:

```
Local Innovations Ready for Upstream
====================================

+-------------------+-------+--------+---------+---------------------------+
| Component         | Local | Remote | Delta   | PR Title                  |
+-------------------+-------+--------+---------+---------------------------+
| collector-scan    |  88   |   -    | NEW     | feat: Add collector-scan  |
| collector-learner |  92   |   75   | +17     | feat: Multi-source scoring|
| sync-strategy     |  85   |   -    | NEW     | docs: Sync strategy module|
+-------------------+-------+--------+---------+---------------------------+

Total: 3 contributions ready
  NEW:      2 components
  IMPROVED: 1 component
```

---

## Formatting Guidelines

### Column Alignment

```
| Left-aligned    | Right-aligned |   Centered    |
|-----------------|---------------|:-------------:|
| text here       |           123 |    middle     |
```

### Score Highlighting

- `[N]` = Best score in row (square brackets)
- Plain number = Other scores
- `-` = Not present

### Box Characters

Use ASCII box-drawing for compatibility:

```
+---+---+  Top/bottom borders
|   |   |  Vertical separators
+---+---+  Row separators
```

### Width Guidelines

- Component names: 20-25 chars max
- Score columns: 5-7 chars
- Action columns: 12-15 chars
- Description: remaining space

---

## Dynamic Generation

### Template Pattern

```python
def generate_comparison_table(
    components: List[ComponentData],
    branches: List[str],
    show_best: bool = True
) -> str:
    """
    Generate comparison table from data.

    Args:
        components: List of component comparisons
        branches: Branch names for columns
        show_best: Whether to highlight best scores

    Returns:
        Formatted ASCII table string
    """
    # Calculate column widths
    col_widths = calculate_widths(components, branches)

    # Build header row
    header = build_header(["Component"] + branches + ["Best"], col_widths)

    # Build separator
    separator = build_separator(col_widths)

    # Build data rows
    rows = []
    for comp in components:
        row = build_row(comp, branches, col_widths, show_best)
        rows.append(row)

    # Combine
    return "\n".join([separator, header, separator] + rows + [separator])
```

---

## Responsive Behavior

### Terminal Width Adaptation

```yaml
narrow_mode:
  trigger: terminal_width < 80
  changes:
    - Truncate component names to 15 chars
    - Use abbreviations (PRES, UPD, MRG)
    - Hide less important columns

wide_mode:
  trigger: terminal_width >= 120
  changes:
    - Full component names
    - Full action names
    - Add description column
```

### Column Priority

When space is limited, preserve in order:
1. Component name (always)
2. Local score (always)
3. Best source (always)
4. Action (important)
5. Other branch scores (if space)

---

**Version**: 1.0.0 | **Status**: Production Ready | **Last Updated**: 2025-12-04
