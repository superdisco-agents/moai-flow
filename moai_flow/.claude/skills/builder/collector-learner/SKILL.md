---
name: collector-learner
description: AI-enhanced multi-source analysis to learn what's an improvement across local and GitHub branches
version: 4.0.0
modularized: true
tier: 3
category: builder
last_updated: 2025-12-04
compliance_score: 95
auto_trigger_keywords:
  - analyze improvement
  - learn difference
  - score improvement
  - collector learn
  - collector
  - branch comparison
  - find best version
color: yellow
---

# Collector: Learner

**AI-enhanced analysis to understand WHY something is an improvement**

> **Version**: 1.0.0
> **Status**: Production Ready
> **Part of**: MoAI Flow System

## Quick Reference

### Purpose
Don't just identify differences - LEARN from them:
- Analyze WHY a change is an improvement
- Score improvements with reasoning
- Extract reusable patterns
- Suggest enhancements beyond simple merging

### Quick Invocation
```python
Skill("moai-flow-learner")
```

### Core Philosophy
```
NOT: "A is newer, so A is better"
BUT: "A has better module organization because..."
```

---

## Level 1: AI-Enhanced Analysis

### Analysis Types

| Type | Question Answered | Output |
|------|-------------------|--------|
| **Quality Analysis** | Is this better quality? | Score + reasoning |
| **Pattern Analysis** | What pattern makes this work? | Extractable pattern |
| **Enhancement Analysis** | How could this be even better? | Improvement suggestions |
| **Conflict Analysis** | Both changed - which wins? | Merge recommendation |

### Analysis Workflow

```
Collection Report
       │
       ▼
┌──────────────────┐
│  For each diff:  │
│  1. Read both    │
│  2. Reason about │
│  3. Score        │
│  4. Document WHY │
└────────┬─────────┘
         │
         ▼
   Learning Report
   (with reasoning)
```

---

## Level 2: Scoring Methodology

### Improvement Score (0-100)

| Score Range | Meaning | Action |
|-------------|---------|--------|
| **90-100** | Significantly better | Must merge |
| **70-89** | Clearly better | Should merge |
| **50-69** | Marginally better | Consider merging |
| **30-49** | Roughly equal | Optional |
| **0-29** | Worse or no value | Skip |

### Scoring Criteria

Each criterion contributes to the final score:

| Criterion | Weight | What to Evaluate |
|-----------|--------|------------------|
| **Structure** | 20% | Module organization, file layout |
| **Documentation** | 20% | README, examples, comments |
| **Functionality** | 25% | Features, edge cases, robustness |
| **Quality** | 20% | TRUST-5 compliance, best practices |
| **Freshness** | 15% | Recency (context-dependent) |

### Scoring Process

```markdown
## Analyze: decision-logic-framework (in A, not in B)

### 1. Structure Analysis (Score: 18/20)
The skill has:
- Clear SKILL.md with proper frontmatter
- 4 well-organized modules
- Follows tier-3 patterns

### 2. Documentation Analysis (Score: 17/20)
- Comprehensive examples
- Decision trees documented
- Missing: edge case examples

### 3. Functionality Analysis (Score: 23/25)
- Covers 4-tier decision system
- Handles skill creation decisions
- Handles agent creation decisions
- Could add: command creation decisions

### 4. Quality Analysis (Score: 18/20)
- Follows TRUST-5 principles
- Consistent naming
- No security concerns

### 5. Freshness Analysis (Score: 12/15)
- Created 2025-12-02
- Actively maintained

**TOTAL SCORE: 88/100**
**RECOMMENDATION: Should merge (clearly better)**

**WHY**: This skill provides structured decision-making
that prevents ad-hoc choices. The 4-tier system aligns
with MoAI's quality principles.
```

---

## Level 3: Pattern Extraction

### What Are Patterns?

Patterns are reusable ideas that could improve other skills:

```markdown
## Pattern: Decision Tree Documentation

**Found in**: decision-logic-framework
**Pattern**: Document decisions as flowcharts, not prose

**Example**:
```
Should this be a script or module?
├─ External package required? → Script
├─ Just reference docs? → Module
└─ Both? → Script + Module
```

**Could Apply To**:
- moai-foundation-core (delegation decisions)
- builder-skill (creation decisions)
- moai-workflow-* (workflow decisions)
```

### Pattern Categories

| Category | Description | Example |
|----------|-------------|---------|
| **Structure** | How to organize files | Module nesting rules |
| **Documentation** | How to document | Progressive disclosure |
| **Integration** | How to connect | Works Well With pattern |
| **Quality** | How to ensure quality | TRUST-5 checklist |

---

## Level 4: Enhancement Suggestions

### Beyond Copying

The learner doesn't just recommend "copy A to B" - it suggests improvements:

```markdown
## Enhancement Opportunity: moai-connector-github

**Current State (in A)**:
- Good gh CLI documentation
- Basic API patterns
- 3 modules

**Suggested Enhancement**:
1. Add `workflow/` with TOON automation
2. Add rate limiting guidance
3. Add error handling patterns
4. Create `scripts/flow_github_*.py` for automation

**Rationale**: This skill is used frequently. Adding
automation would reduce manual work by 60%.
```

### Enhancement Types

| Type | When to Suggest |
|------|-----------------|
| **Add Module** | Gap in documentation |
| **Add Script** | Repetitive manual task |
| **Add Workflow** | Multi-step process |
| **Restructure** | Poor organization |
| **Merge Ideas** | Both versions have value |

---

## Level 5: Conflict Resolution

### When Both Changed

Sometimes both workspaces modified the same skill:

```markdown
## Conflict: builder skill

**In A**: Added workflow support
**In B**: Added UV script templates

**Analysis**:
- A's changes: Better orchestration (score: 75)
- B's changes: Better automation (score: 72)

**Recommendation**: SMART MERGE
- Take A's workflow/ directory
- Take B's scripts/ templates
- Merge SKILL.md (A's structure + B's examples)

**Rationale**: Both changes add value in different areas.
Combined skill would be more complete than either alone.
```

### Conflict Strategies

| Strategy | When to Use |
|----------|-------------|
| **Take A** | A is clearly superior |
| **Take B** | B is clearly superior |
| **Smart Merge** | Both have unique value |
| **Enhance Both** | Create new version combining best |
| **Skip** | Changes conflict fundamentally |

---

## Output Format

### Learning Report Schema

```json
{
  "collection_id": "flow-2025-12-02-001",
  "analyzed_at": "2025-12-02T15:00:00Z",
  "analyzer": "moai-flow-learner v1.0.0",

  "analyses": [
    {
      "component": "decision-logic-framework",
      "type": "skill",
      "location": "only_in_a",
      "score": 88,
      "reasoning": "Provides structured decision-making...",
      "recommendation": "should_merge",
      "patterns_extracted": ["decision-tree-documentation"],
      "enhancements_suggested": ["add-command-decisions"]
    }
  ],

  "patterns": [
    {
      "id": "decision-tree-documentation",
      "name": "Decision Tree Documentation",
      "description": "Document decisions as flowcharts",
      "source": "decision-logic-framework",
      "applicability": ["moai-foundation-core", "builder-skill"]
    }
  ],

  "summary": {
    "total_analyzed": 6,
    "must_merge": 2,
    "should_merge": 2,
    "optional": 1,
    "skip": 1,
    "patterns_found": 3,
    "enhancements_suggested": 5
  }
}
```

---

## Works Well With

**Skills**:
- `moai-flow-collector` - Provides comparison data
- `moai-flow-consolidator` - Consumes learning output
- `decision-logic-framework` - Quality criteria

**Agents**:
- `moai-flow` - Orchestrates analysis

**Commands**:
- `/moai-flow:learn` - Triggers learning workflow

---

## Modules

| Module | Description |
|--------|-------------|
| `scoring-methodology.md` | Detailed scoring criteria and weights |
| `pattern-recognition.md` | How to identify and extract patterns |
| `enhancement-suggestions.md` | Guidelines for suggesting improvements |
| `conflict-resolution.md` | Strategies for handling conflicts |

---

## Quick Checklist

Before analyzing:
- [ ] Collection report exists and is valid
- [ ] Source files are accessible for deep analysis
- [ ] TRUST-5 framework available for quality scoring

After analyzing:
- [ ] Each difference has a score with reasoning
- [ ] Patterns documented with applicability
- [ ] Enhancements suggested where valuable
- [ ] Conflicts have clear resolution strategy
- [ ] Next steps interface displayed to user

---

## Post-Analysis Workflow (Mandatory)

**CRITICAL**: After learning completes, ALWAYS show the next steps interface.

### Required Output Sequence

```yaml
post_learn_workflow:
  1_display_summary:
    - Show scoring table with all components
    - Show extracted patterns
    - Show enhancement suggestions
    - Show conflicts (if any)

  2_show_next_steps_menu:
    type: AskUserQuestion
    required: true
    skip: never
    question: "Learning 분석이 완료되었습니다. 다음 단계를 선택해 주세요."
    header: "다음 단계"
    options:
      - label: "Consolidate 실행"
        description: "모든 must_merge + should_merge 컴포넌트를 대상 워크스페이스에 적용"
      - label: "상세 리포트 확인"
        description: "각 컴포넌트의 점수 breakdown과 reasoning을 상세 확인"
      - label: "선택적 병합"
        description: "병합할 컴포넌트를 직접 선택 (일부만 병합)"
      - label: "작업 종료"
        description: "현재 상태로 저장하고 나중에 계속"

  3_wait_for_selection:
    auto_proceed: never
    reason: "User must explicitly choose next action"
```

### Why Mandatory?

1. **User Agency**: Users control the workflow, not automation
2. **Review Opportunity**: Time to review scores before action
3. **Selective Merge**: Users may want only specific components
4. **State Preservation**: Users may need to pause and return later

---

## Level 6: Multi-Source Analysis (GitHub + Branches)

### Find Best Version Across All Sources

When comparing local vs multiple GitHub branches, find the BEST version:

```
Component: moai-foundation-core
  │
  ├─ Local:            v2.5.0, score: 85
  ├─ main:             v2.3.0, score: 72
  ├─ feature/SPEC-first: v2.4.0, score: 78
  └─ feature/workspace:  v2.6.0, score: 91 ← BEST

Recommendation: UPDATE from feature/workspace
```

### Multi-Source Scoring Matrix

For each component, score across ALL sources:

| Component | Local | main | feature/SPEC | feature/workspace | Best |
|-----------|-------|------|--------------|-------------------|------|
| foundation-core | 85 | 72 | 78 | **91** | workspace |
| decision-framework | **92** | 80 | 85 | - | **local** |
| collector-scan | **88** | - | - | - | **local** |
| builder-workflow | 65 | 70 | **82** | 75 | SPEC |

### Branch Context Scoring

Add context modifiers based on branch characteristics:

| Branch Characteristic | Modifier | Reason |
|----------------------|----------|--------|
| Is default branch (main) | +5 | Tested, stable |
| Recently updated (< 7 days) | +3 | Active development |
| Has CI passing | +5 | Quality verified |
| Merged to main | +10 | Approved changes |
| Stale (> 90 days) | -10 | May be abandoned |

### Multi-Source Decision Rules

```
FOR each component:
  1. Score component in ALL sources (local + each branch)
  2. Apply branch context modifiers
  3. Calculate adjusted scores
  4. Determine best source:
     - If LOCAL has highest: → PRESERVE (don't update)
     - If REMOTE has highest: → UPDATE from that branch
     - If scores within 10 points: → SMART MERGE
```

### Sync Strategy Output

```json
{
  "component": "moai-foundation-core",
  "multi_source_analysis": {
    "local": { "score": 85, "adjusted": 85, "unique": ["collector-integration"] },
    "main": { "score": 72, "adjusted": 77, "unique": [] },
    "feature/SPEC-first-builders": { "score": 78, "adjusted": 81, "unique": ["spec-fields"] },
    "feature/workspace-consolidation": { "score": 91, "adjusted": 91, "unique": ["flow-hooks"] }
  },
  "best_source": "feature/workspace-consolidation",
  "action": "UPDATE",
  "strategy": {
    "primary": "feature/workspace-consolidation",
    "merge_from_local": ["collector-integration"],
    "ignore_branches": ["main"]
  },
  "reasoning": "Branch 'workspace-consolidation' has the highest score (91). Merge local's unique collector-integration. Main is superseded by feature branches."
}
```

---

## Level 7: Selective Sync Logic

### Don't Overwrite Better Code

**Core Principle**: NEVER assume remote is better. Always score both sides.

```
IF local.score > remote.best_score + 10:
  → PRESERVE local
  → PROPOSE: Contribute local improvements to upstream

IF remote.best_score > local.score + 10:
  → UPDATE from remote.best_branch
  → PRESERVE: local unique features if any

IF |local.score - remote.best_score| <= 10:
  → SMART MERGE
  → COMBINE: best of both sources
```

### Unique Feature Detection

Identify features that exist in one source but not others:

```python
# Pseudo-algorithm
local_features = extract_features(local_component)
remote_features = extract_features(remote_component)

unique_to_local = local_features - remote_features
unique_to_remote = remote_features - local_features

if unique_to_local:
    # Preserve these when updating from remote
    merge_strategy.preserve(unique_to_local)

if unique_to_remote:
    # Add these when keeping local
    merge_strategy.enhance(unique_to_remote)
```

### Feature Extraction Signals

| Feature Type | Detection Method |
|--------------|-----------------|
| Modules | Count `modules/*.md` files |
| Scripts | Count `scripts/*.py` files |
| Workflows | Check for `workflows/` directory |
| Examples | Count examples in SKILL.md |
| Integrations | Check "Works Well With" section |
| Version | Compare semver from frontmatter |

---

## Level 8: Bidirectional Sync

### Detect Local Innovations

When local is SIGNIFICANTLY better:

```
IF local.score > 90 AND remote.best_score < 70:
  → Flag as "LOCAL INNOVATION"
  → Suggest: "Create PR to upstream"
  → Generate: PR description with improvements
```

### Upstream Contribution Report

```json
{
  "innovations": [
    {
      "component": "collector-scan",
      "local_score": 88,
      "remote_exists": false,
      "action": "CONTRIBUTE_NEW",
      "pr_title": "feat: Add collector-scan skill for workspace comparison",
      "pr_body": "Adds intelligent workspace scanning with GitHub API integration..."
    },
    {
      "component": "collector-learner",
      "local_score": 92,
      "remote_score": 75,
      "improvement_delta": 17,
      "action": "CONTRIBUTE_UPDATE",
      "pr_title": "feat: Enhance collector-learner with multi-source scoring",
      "pr_body": "Adds branch-aware scoring and selective sync strategy..."
    }
  ]
}
```

---

## Level 9: Tier & History Integration

### Context-Aware Scoring with Branch History

The learner integrates branch database and tier classification to provide intelligent, context-aware scoring:

```
Component: moai-foundation-core
  │
  ├─ Tier Classification: Tier 2 (High priority)
  ├─ Branch History:
  │    └─ feature/workspace: 15 commits, 3 contributors, merged to main
  │    └─ feature/SPEC-first: 8 commits, 1 contributor, active
  │    └─ main: stable, CI passing
  │
  └─ Context Adjustments:
       ├─ Tier 2 = Critical path → +10 to quality weight
       ├─ Branch merged to main → +10 stability bonus
       └─ Active development → +5 freshness boost
```

### Tier-Based Scoring Adjustments

Different tiers receive different scoring emphasis:

| Tier | Priority | Weight Adjustments | Rationale |
|------|----------|-------------------|-----------|
| **Tier 1** | Critical Infrastructure | Quality +15%, Structure +10% | Foundation must be rock-solid |
| **Tier 2** | Core Features | Quality +10%, Functionality +10% | Balance quality with features |
| **Tier 3** | Extended Features | Functionality +10%, Documentation +5% | Feature completeness matters |
| **Tier 4** | Specialized Tools | Documentation +10%, Freshness +5% | Usability and currency |
| **Tier 5** | Experimental | Freshness +15%, Enhancement potential +10% | Innovation and potential |

### Branch History Context Modifiers

Historical branch data informs scoring decisions:

| History Signal | Modifier | Applied When |
|---------------|----------|--------------|
| **Merged to main** | +10 | Branch successfully merged upstream |
| **CI passing** | +5 | Latest commit passed all checks |
| **Active development** | +5 | Commit within last 7 days |
| **Multiple contributors** | +3 | 2+ contributors on branch |
| **Stale branch** | -10 | No commits in 90+ days |
| **Failed CI** | -5 | Latest commit failed checks |
| **Force-pushed** | -3 | Force push detected in history |

### Tier-Aware Recommendations

Recommendations adapt based on component tier:

```markdown
## Analysis: moai-foundation-core (Tier 1)

### Tier Context
- **Classification**: Tier 1 - Critical Infrastructure
- **Impact**: System-wide, affects all dependent components
- **Quality Standard**: Must meet 95+ compliance score

### Branch Analysis
- **Best Source**: feature/workspace-consolidation
  - Branch history: 15 commits, merged to main, CI passing
  - Contributors: 3 developers
  - Last activity: 2 days ago

### Adjusted Score: 94/100
- Base score: 88
- Tier 1 quality bonus: +3
- Merged to main bonus: +2
- Active development bonus: +1

### Recommendation: MUST UPDATE (Tier 1 Critical)
- **Action**: Update from feature/workspace-consolidation
- **Rationale**: Tier 1 component with improved architecture (91 vs 85)
- **Risk**: Low - branch merged to main, CI passing
- **Testing Required**: Full integration test suite before deployment
```

### Integration with Modules

The learner now consults:

**From `branch-database.md`**:
- Branch metadata (commits, contributors, status)
- Merge history and CI results
- Branch relationships and dependencies
- Activity timeline and staleness detection

**From `tier-classification.md`**:
- Component tier assignment (1-5)
- Priority levels and quality standards
- Weight adjustments per tier
- Testing requirements per tier

### Context-Aware Decision Rules

```python
# Pseudo-algorithm for tier-aware scoring
def score_with_context(component, tier, branch_history):
    base_score = calculate_base_score(component)

    # Apply tier-specific weight adjustments
    tier_weights = get_tier_weights(tier)
    adjusted_score = apply_weights(base_score, tier_weights)

    # Apply branch history modifiers
    history_bonus = calculate_history_bonus(branch_history)
    final_score = adjusted_score + history_bonus

    # Tier-specific quality gates
    if tier <= 2 and final_score < 90:
        flag_as_critical_quality_issue()

    return final_score, recommendation_with_tier_context()
```

### Enhanced Output Format

Learning reports now include tier and history context:

```json
{
  "component": "moai-foundation-core",
  "tier": 1,
  "tier_label": "Critical Infrastructure",
  "score": 94,
  "base_score": 88,
  "tier_adjustment": 3,
  "history_adjustment": 3,
  "branch_context": {
    "best_source": "feature/workspace-consolidation",
    "commits": 15,
    "contributors": 3,
    "merged_to_main": true,
    "ci_status": "passing",
    "last_commit": "2 days ago"
  },
  "recommendation": "must_update",
  "tier_based_rationale": "Tier 1 component requires immediate update due to architectural improvements and proven stability (merged to main with passing CI)"
}
```

---

## Modules

| Module | Description |
|--------|-------------|
| `deep-branch-analysis.md` | 🔬 **NEW v5.0**: Git history, file changes, component detection, impact scoring |
| `scoring-methodology.md` | Detailed scoring criteria and weights |
| `pattern-recognition.md` | How to identify and extract patterns |
| `enhancement-suggestions.md` | Guidelines for suggesting improvements |
| `conflict-resolution.md` | Strategies for handling conflicts |
| `sync-strategy.md` | Multi-source sync decision rules |
| `branch-database.md` | Branch history and metadata analysis |
| `tier-classification.md` | Component tier classification and priority rules |

---

**Version**: 5.0.0 | **Status**: Production Ready | **Last Updated**: 2025-12-04
