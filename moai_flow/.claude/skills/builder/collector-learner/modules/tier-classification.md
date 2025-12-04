# Tier Classification System

**Categorize branches and PRs by priority and importance**

> **Version**: 1.0.0
> **Part of**: collector-learner skill
> **Last Updated**: 2025-12-04

---

## Overview

The Tier System provides clear prioritization for branches and PRs:

| Tier | Label | Color | Score Range | Meaning |
|------|-------|-------|-------------|---------|
| **1** | Critical | Gold | 90+ | Merge ASAP |
| **2** | Important | Silver | 75-89 | Merge this sprint |
| **3** | Minor | Bronze | 50-74 | Merge when convenient |
| **4** | Stale | Gray | - | Review or close |

---

## Tier Definitions

### Tier 1: Critical

```yaml
tier_1_critical:
  label: "Critical"
  badge: "gold"
  display: "Tier 1"
  icon: null  # No emoji per style guide

  criteria:
    score_based:
      - score >= 90

    feature_based:
      - introduces_new_capability: true
      - OR: blocks_other_work: true
      - OR: security_fix: true
      - OR: breaking_change_fix: true

  auto_classify_when:
    - ANY score_based criteria met
    - OR: ANY feature_based criteria met

  recommended_action: "Merge ASAP"
  sla: "Within 24 hours"
  review_priority: "Immediate"
```

**Examples**:
- Score 91 branch with SPEC-first integration
- Security vulnerability fix (any score)
- Hotfix for production bug

### Tier 2: Important

```yaml
tier_2_important:
  label: "Important"
  badge: "silver"
  display: "Tier 2"
  icon: null

  criteria:
    score_based:
      - score >= 75 AND score < 90

    feature_based:
      - improves_existing: true
      - OR: adds_tests: true
      - OR: performance_improvement: true

  auto_classify_when:
    - score in range [75, 89]
    - AND: NOT tier_1 criteria met

  recommended_action: "Merge this sprint"
  sla: "Within 1 week"
  review_priority: "High"
```

**Examples**:
- Score 82 with enhanced error handling
- Score 78 with new test coverage
- Performance optimization branch

### Tier 3: Minor

```yaml
tier_3_minor:
  label: "Minor"
  badge: "bronze"
  display: "Tier 3"
  icon: null

  criteria:
    score_based:
      - score >= 50 AND score < 75

    feature_based:
      - cosmetic_only: true
      - OR: documentation_only: true
      - OR: refactoring_only: true

  auto_classify_when:
    - score in range [50, 74]
    - OR: ONLY feature_based criteria met (no functional change)

  recommended_action: "Merge when convenient"
  sla: "Within 2 weeks"
  review_priority: "Normal"
```

**Examples**:
- Score 65 with code cleanup
- Documentation improvements only
- Minor refactoring without behavior change

### Tier 4: Stale

```yaml
tier_4_stale:
  label: "Stale"
  badge: "gray"
  display: "Tier 4"
  icon: null

  criteria:
    time_based:
      - last_updated > 90_days
      - OR: no_commits_for > 60_days

    activity_based:
      - no_recent_commits: true
      - AND: no_recent_pr_activity: true

  auto_classify_when:
    - ANY time_based criteria met
    - AND: branch NOT explicitly marked "keep"

  recommended_action: "Review or close"
  sla: "Archive within 2 weeks"
  review_priority: "Low"
```

**Examples**:
- Branch with no commits for 90+ days
- Abandoned feature branch
- Superseded by another branch

---

## Classification Algorithm

### Auto-Classification Flow

```
Branch Detected
      |
      v
+---------------------+
| Check Score         |
| Score = calculate() |
+----------+----------+
           |
    +------+------+
    |             |
  >=90         <90
    |             |
    v             v
 TIER 1     +--------+
            | >=75?  |
            +---+----+
                |
         +------+------+
         |             |
       >=75          <75
         |             |
         v             v
      TIER 2      +--------+
                  | >=50?  |
                  +---+----+
                      |
               +------+------+
               |             |
             >=50          <50
               |             |
               v             v
            TIER 3       SKIP
                      (not tracked)

After Tier Assigned:
      |
      v
+---------------------+
| Check Staleness     |
| days_inactive > 90? |
+----------+----------+
           |
     +-----+-----+
     |           |
    YES          NO
     |           |
     v           v
  TIER 4     Keep current tier
```

### Override Rules

```yaml
overrides:
  user_override:
    - User can manually set tier
    - Stored in branch.tier.user_override
    - Takes precedence over auto-classification

  upgrade_triggers:
    - Security fix → TIER 1 (immediate)
    - Blocks release → TIER 1 (immediate)
    - Score crosses 90 → TIER 1 (next scan)

  downgrade_protection:
    - TIER 1 cannot auto-downgrade (requires user action)
    - Merged branches maintain tier for history
```

---

## Display Formatting

### Terminal/ANSI Display

```
TIER 1 [Gold]     Critical - Merge ASAP
TIER 2 [Silver]   Important - Merge this sprint
TIER 3 [Bronze]   Minor - Merge when convenient
TIER 4 [Gray]     Stale - Review or close
```

### Markdown Badges

```markdown
| Tier | Badge |
|------|-------|
| 1 | **Tier 1: Critical** |
| 2 | **Tier 2: Important** |
| 3 | **Tier 3: Minor** |
| 4 | **Tier 4: Stale** |
```

### Table Column

```
| Branch                    | Score | Tier        | Action          |
|---------------------------|-------|-------------|-----------------|
| feature/SPEC-first        | 91    | 1: Critical | Merge ASAP      |
| feature/workspace         | 82    | 2: Important| Merge this week |
| bugfix/typo-fix           | 68    | 3: Minor    | When convenient |
| feature/old-experiment    | 55    | 4: Stale    | Review/close    |
```

---

## API Functions

### classify_tier(score, characteristics)

```python
def classify_tier(
    score: int,
    characteristics: BranchCharacteristics
) -> TierClassification:
    """
    Classify branch into tier based on score and characteristics.

    Args:
        score: Branch quality score (0-100)
        characteristics: Branch metadata (is_security_fix, etc.)

    Returns:
        TierClassification with tier, reason, action
    """
    # Check special cases first
    if characteristics.is_security_fix:
        return TierClassification(
            tier=1,
            reason="Security fix",
            action="Merge ASAP"
        )

    if characteristics.blocks_release:
        return TierClassification(
            tier=1,
            reason="Blocks release",
            action="Merge ASAP"
        )

    # Score-based classification
    if score >= 90:
        return TierClassification(
            tier=1,
            reason=f"Score >= 90 ({score})",
            action="Merge ASAP"
        )

    if score >= 75:
        return TierClassification(
            tier=2,
            reason=f"Score in range 75-89 ({score})",
            action="Merge this sprint"
        )

    if score >= 50:
        return TierClassification(
            tier=3,
            reason=f"Score in range 50-74 ({score})",
            action="Merge when convenient"
        )

    return TierClassification(
        tier=0,  # Below threshold
        reason=f"Score below 50 ({score})",
        action="Not recommended for merge"
    )
```

### check_staleness(branch)

```python
def check_staleness(branch: Branch) -> bool:
    """
    Check if branch should be classified as stale.
    """
    days_since_update = (today() - branch.last_commit).days

    if days_since_update > 90:
        return True

    if days_since_update > 60 and not branch.has_open_pr:
        return True

    return False
```

### get_tier_label(tier)

```python
def get_tier_label(tier: int) -> str:
    """
    Get display label for tier.
    """
    labels = {
        1: "Tier 1: Critical",
        2: "Tier 2: Important",
        3: "Tier 3: Minor",
        4: "Tier 4: Stale"
    }
    return labels.get(tier, "Unknown")
```

---

## Integration Points

### collector-scanner

After scanning:
```yaml
post_scan:
  - Calculate score
  - Call classify_tier()
  - Check staleness
  - Update branch database
```

### collector-learner

During analysis:
```yaml
learning_phase:
  - Factor tier into recommendations
  - Higher tiers get detailed analysis
  - Lower tiers get summary only
```

### collector-readme

For README generation:
```yaml
readme_generation:
  - Include tier badge
  - Show tier-appropriate sections
  - Tier 1: Full detail
  - Tier 4: Minimal + archive suggestion
```

### User Interface

For decision menus:
```yaml
ui_display:
  - Sort by tier (1 first)
  - Group by tier in selection
  - Highlight tier 1 for attention
```

---

## Tier Transitions

### Upgrade Paths

```
TIER 4 → TIER 3: New commit pushed
TIER 3 → TIER 2: Score crosses 75
TIER 2 → TIER 1: Score crosses 90 OR flagged critical
```

### Downgrade Paths

```
TIER 1 → TIER 2: Manual downgrade only
TIER 2 → TIER 3: Score drops below 75
TIER 3 → TIER 4: 90 days inactive
```

### Notification Triggers

```yaml
notify_on:
  tier_1_new: "New critical branch detected"
  tier_upgrade: "Branch upgraded to Tier {tier}"
  tier_downgrade_warning: "Branch at risk of downgrade"
  tier_4_warning: "Branch becoming stale"
```

---

## Configuration

```json
{
  "tier_thresholds": {
    "tier_1_min_score": 90,
    "tier_2_min_score": 75,
    "tier_3_min_score": 50,
    "stale_days": 90,
    "abandon_days": 180
  },
  "auto_classify": true,
  "allow_user_override": true,
  "notify_tier_changes": true
}
```

---

## Quick Reference

| Tier | Score | Time | Badge | Action |
|------|-------|------|-------|--------|
| 1 | 90+ | - | Gold | ASAP |
| 2 | 75-89 | - | Silver | This sprint |
| 3 | 50-74 | - | Bronze | Convenient |
| 4 | Any | 90d+ | Gray | Review/close |

---

**Version**: 1.0.0 | **Status**: Production Ready | **Last Updated**: 2025-12-04
