# Module: Scoring Methodology

## Overview

Detailed scoring criteria and weights for evaluating whether a change is an improvement.

---

## The Five Pillars of Scoring

### 1. Structure (20% weight)

Evaluates how well-organized the component is.

| Aspect | Points | Criteria |
|--------|--------|----------|
| File layout | 0-5 | Follows expected directory structure |
| Module organization | 0-5 | Logical grouping, clear boundaries |
| Naming conventions | 0-5 | Consistent, descriptive names |
| Separation of concerns | 0-5 | Single responsibility per file |

**Structure Questions**:
- Does it follow MoAI conventions?
- Are modules logically organized?
- Can you find what you need quickly?
- Is there unnecessary nesting or flatness?

---

### 2. Documentation (20% weight)

Evaluates clarity and completeness of documentation.

| Aspect | Points | Criteria |
|--------|--------|----------|
| SKILL.md/AGENT.md quality | 0-5 | Proper frontmatter, clear purpose |
| Examples provided | 0-5 | Working examples, edge cases shown |
| Module documentation | 0-5 | Each module has clear purpose |
| Integration guidance | 0-5 | "Works Well With" section complete |

**Documentation Questions**:
- Can someone use this without asking questions?
- Are the examples copy-paste ready?
- Is the purpose clear in 10 seconds?
- Are edge cases documented?

---

### 3. Functionality (25% weight)

Evaluates what the component actually does.

| Aspect | Points | Criteria |
|--------|--------|----------|
| Core features | 0-7 | Primary purpose fulfilled |
| Edge case handling | 0-6 | Graceful failure, validation |
| Completeness | 0-6 | No obvious gaps |
| Robustness | 0-6 | Works in various contexts |

**Functionality Questions**:
- Does it do what it claims?
- What happens with bad input?
- Are there obvious missing features?
- Would this work in production?

---

### 4. Quality (20% weight)

Evaluates adherence to best practices.

| Aspect | Points | Criteria |
|--------|--------|----------|
| TRUST-5 compliance | 0-5 | Meets tiered structure standards |
| Best practices | 0-5 | Follows established patterns |
| Security | 0-5 | No obvious vulnerabilities |
| Maintainability | 0-5 | Easy to update and extend |

**Quality Questions**:
- Does it follow TRUST-5 principles?
- Would you be comfortable maintaining this?
- Are there security concerns?
- Is it over-engineered or under-engineered?

---

### 5. Freshness (15% weight)

Evaluates recency and active development.

| Aspect | Points | Criteria |
|--------|--------|----------|
| Last update date | 0-5 | More recent = more points |
| Active development | 0-5 | Signs of ongoing work |
| Version number | 0-5 | Higher semver = more mature |

**Freshness Calculation**:
```
Days since update:
- 0-7 days: 5 points
- 8-14 days: 4 points
- 15-30 days: 3 points
- 31-60 days: 2 points
- 61-90 days: 1 point
- 90+ days: 0 points
```

---

## Score Calculation

### Formula

```
Total = (Structure × 0.20) + (Documentation × 0.20) +
        (Functionality × 0.25) + (Quality × 0.20) +
        (Freshness × 0.15)
```

### Normalization

Each pillar scored 0-20 (or 0-25 for Functionality, 0-15 for Freshness).
Normalize to 0-100 scale.

### Example Calculation

```
Skill: decision-logic-framework

Structure:     18/20 × 0.20 = 3.6
Documentation: 17/20 × 0.20 = 3.4
Functionality: 23/25 × 0.25 = 5.75
Quality:       18/20 × 0.20 = 3.6
Freshness:     12/15 × 0.15 = 1.2

Raw Total: 17.55
Normalized: (17.55 / 20) × 100 = 87.75 ≈ 88
```

---

## Context Adjustments

### When Freshness Matters More

- Active development projects: Increase to 25%
- Rapidly changing domains: Increase to 20%
- Stable utilities: Decrease to 5%

### When Quality Matters More

- Security-critical components: Increase to 30%
- Production systems: Increase to 25%
- Experimental features: Decrease to 10%

### Adjustment Template

```json
{
  "context": "security-critical",
  "weights": {
    "structure": 0.15,
    "documentation": 0.15,
    "functionality": 0.25,
    "quality": 0.30,
    "freshness": 0.15
  }
}
```

---

## Score Interpretation

| Score | Category | Confidence | Action |
|-------|----------|------------|--------|
| 90-100 | Excellent | Very High | Must merge |
| 80-89 | Good | High | Should merge |
| 70-79 | Solid | Medium-High | Likely merge |
| 60-69 | Acceptable | Medium | Consider carefully |
| 50-59 | Marginal | Low | Optional |
| 40-49 | Weak | Very Low | Probably skip |
| 0-39 | Poor | None | Skip |

---

## Comparative Scoring

When both workspaces have the same component:

```
Score Difference = Score_A - Score_B

If difference > 15: Clear winner
If difference 5-15: Likely winner
If difference < 5: Roughly equal (consider merge)
```
