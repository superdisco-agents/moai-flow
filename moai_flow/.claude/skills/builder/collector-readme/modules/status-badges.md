# Status Badges

**Badge formatting and status indicators for branch READMEs**

> **Version**: 1.0.0
> **Part of**: collector-readme skill
> **Last Updated**: 2025-12-04

---

## Badge Types

### Tier Badges

Display branch priority tier:

| Tier | Markdown | Display |
|------|----------|---------|
| 1 | `**Tier 1: Critical**` | **Tier 1: Critical** |
| 2 | `**Tier 2: Important**` | **Tier 2: Important** |
| 3 | `**Tier 3: Minor**` | **Tier 3: Minor** |
| 4 | `**Tier 4: Stale**` | **Tier 4: Stale** |

### Status Badges

Display branch lifecycle status:

| Status | Markdown | Display |
|--------|----------|---------|
| Active | `**Active**` | **Active** |
| Merged | `**Merged**` | **Merged** |
| Stale | `**Stale**` | **Stale** |
| Abandoned | `**Abandoned**` | **Abandoned** |
| In Review | `**In Review**` | **In Review** |

### Score Badges

Display quality score with context:

| Range | Markdown | Display |
|-------|----------|---------|
| 90+ | `**Score: 91/100**` | **Score: 91/100** |
| 75-89 | `**Score: 82/100**` | **Score: 82/100** |
| 50-74 | `**Score: 65/100**` | **Score: 65/100** |
| <50 | `**Score: 45/100**` | **Score: 45/100** |

---

## Header Badge Line

Standard format for README header:

```markdown
> **Status**: Active | **Tier**: Tier 1: Critical | **Score**: 91/100
```

### Generation Function

```python
def generate_header_badges(branch: BranchData) -> str:
    """
    Generate the header badge line.
    """
    status = f"**Status**: {branch.status}"
    tier = f"**Tier**: {get_tier_label(branch.tier)}"
    score = f"**Score**: {branch.score}/100"

    return f"> {status} | {tier} | {score}"
```

---

## Table Cell Badges

For use in markdown tables:

### Ready Status

| Value | Display |
|-------|---------|
| Ready | **Yes** |
| Not Ready | No |
| Blocked | **Blocked** |

### Conflict Status

| Value | Display |
|-------|---------|
| None | None |
| Minor | 1 minor |
| Major | **3 conflicts** |

### CI Status

| Value | Display |
|-------|---------|
| Passing | **Passing** |
| Failing | **Failing** |
| Pending | Pending |
| Unknown | - |

---

## Score Change Indicators

Show score trends:

| Change | Indicator | Example |
|--------|-----------|---------|
| Increase | `+N` | +13 |
| Decrease | `-N` | -5 |
| No change | `0` | 0 |
| First scan | `-` | - |

### In Tables

```markdown
| Date | Score | Change |
|------|-------|--------|
| Nov 15 | 65 | - |
| Nov 22 | 72 | +7 |
| Nov 29 | 85 | +13 |
| Dec 04 | 91 | +6 |
```

---

## Action Badges

For recommended actions:

| Action | Badge |
|--------|-------|
| Merge ASAP | **Merge ASAP** |
| Merge This Sprint | Merge this sprint |
| Merge When Convenient | Merge when convenient |
| Review or Close | Review or close |
| Needs Work | **Needs work** |

---

## Component Action Badges

| Action | Display |
|--------|---------|
| Added | **Added** |
| Enhanced | Enhanced |
| Modified | Modified |
| Unchanged | - |
| Removed | Removed |

---

## Badge Generation Functions

### get_tier_badge(tier)

```python
def get_tier_badge(tier: int) -> str:
    """
    Get markdown badge for tier.
    """
    labels = {
        1: "**Tier 1: Critical**",
        2: "**Tier 2: Important**",
        3: "**Tier 3: Minor**",
        4: "**Tier 4: Stale**"
    }
    return labels.get(tier, "Unknown")
```

### get_status_badge(status)

```python
def get_status_badge(status: str) -> str:
    """
    Get markdown badge for status.
    """
    if status in ["Active", "Merged"]:
        return f"**{status}**"
    return status
```

### get_score_badge(score)

```python
def get_score_badge(score: int) -> str:
    """
    Get markdown badge for score.
    """
    return f"**Score: {score}/100**"
```

### get_change_indicator(current, previous)

```python
def get_change_indicator(current: int, previous: int | None) -> str:
    """
    Get score change indicator.
    """
    if previous is None:
        return "-"

    delta = current - previous
    if delta > 0:
        return f"+{delta}"
    elif delta < 0:
        return str(delta)
    else:
        return "0"
```

---

## Compact Badge Lines

For space-constrained displays:

### Single Line Summary

```markdown
Active | Tier 1 | 91/100 | Ready
```

### Minimal Header

```markdown
**feature/SPEC-first** | T1 | 91 | Active
```

---

## Badge Styling Guidelines

1. **Consistency**: Use same format throughout document
2. **Bold for Emphasis**: Use `**bold**` for important values
3. **No Emojis**: Per style guide, avoid emojis
4. **Clear Labels**: Always include context (e.g., "/100" for scores)
5. **Table Alignment**: Right-align numeric values

---

## Examples

### Full Header

```markdown
# Branch: feature/SPEC-first-builders

> **Status**: Active | **Tier**: Tier 1: Critical | **Score**: 91/100

Implements SPEC-first development workflow for all builder agents.
```

### Merge Status Table

```markdown
| Criterion | Status |
|-----------|--------|
| Ready for Main | **Yes** |
| Conflicts | None |
| CI Status | **Passing** |
| Reviews | 1 approved |
```

### Component Table

```markdown
| Component | Action | Score | Change |
|-----------|--------|-------|--------|
| builder-skill | Enhanced | 88 | +12 |
| decision-framework | **Added** | 91 | - |
| foundation-core | Modified | 85 | +5 |
```

---

**Version**: 1.0.0 | **Status**: Production Ready | **Last Updated**: 2025-12-04
