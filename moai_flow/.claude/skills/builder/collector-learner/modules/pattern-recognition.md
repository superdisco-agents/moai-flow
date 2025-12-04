# Module: Pattern Recognition

## Overview

How to identify reusable patterns from analyzed improvements and extract them for broader application.

---

## What Is a Pattern?

A pattern is a **reusable idea** that:
1. Solved a problem effectively in one place
2. Could solve similar problems elsewhere
3. Can be described independently of its source

### Pattern vs Implementation

```
Implementation: "decision-logic-framework has a 4-tier decision tree"
Pattern: "Document decisions as flowcharts with clear branching logic"
```

---

## Pattern Categories

### 1. Structure Patterns

How to organize files and directories.

| Pattern Name | Description | Example |
|--------------|-------------|---------|
| `modular-skill` | Break skills into modules/ directory | builder-skill pattern |
| `workflow-scripts` | Separate workflow/ from scripts/ | moai-flow-* pattern |
| `progressive-depth` | L1 overview → L5 details | SKILL.md structure |
| `companion-files` | SKILL.md + modules/ + scripts/ | Tier 3 standard |

**Recognition Signals**:
- Clear directory boundaries
- Consistent file naming
- Predictable locations

---

### 2. Documentation Patterns

How to document effectively.

| Pattern Name | Description | Example |
|--------------|-------------|---------|
| `decision-tree` | Flowchart for decisions | decision-logic-framework |
| `quick-reference` | TL;DR at top | Most SKILL.md files |
| `works-well-with` | Integration guidance | Standard section |
| `example-driven` | Learn by example | Code blocks throughout |

**Recognition Signals**:
- Scannable in 10 seconds
- Copy-paste ready examples
- Clear "why" explanations

---

### 3. Integration Patterns

How components connect.

| Pattern Name | Description | Example |
|--------------|-------------|---------|
| `skill-agent-link` | Skills reference agents | "Works Well With" |
| `command-workflow` | Commands trigger workflows | /moai-flow:* |
| `output-input-chain` | Output of A feeds B | collector → learner |
| `shared-schema` | Common data formats | JSON report schema |

**Recognition Signals**:
- Explicit dependencies
- Data flow documentation
- Interface contracts

---

### 4. Quality Patterns

How to ensure quality.

| Pattern Name | Description | Example |
|--------------|-------------|---------|
| `trust-compliance` | Follow TRUST-5 tiers | All MoAI skills |
| `checklist-driven` | Pre/post checklists | SKILL.md sections |
| `version-tracking` | Semver + changelog | Frontmatter metadata |
| `error-handling` | Graceful failures | Module documentation |

**Recognition Signals**:
- Consistent standards
- Validation steps
- Version numbers

---

## Pattern Extraction Process

### Step 1: Identify the Win

```
What made this component better?
- More organized? → Structure pattern
- Clearer docs? → Documentation pattern
- Better connected? → Integration pattern
- More reliable? → Quality pattern
```

### Step 2: Abstract the Idea

Remove specific details, keep the principle:

```
Specific: "decision-logic-framework uses ASCII flowcharts
          to show when to create skills vs agents"

Abstract: "Use visual decision trees to guide complex
          choices with multiple factors"
```

### Step 3: Name the Pattern

Good pattern names are:
- Descriptive (tells you what it does)
- Memorable (easy to reference)
- Action-oriented (implies how to use)

```
Bad: "the-thing-dlf-does"
Good: "visual-decision-tree"
```

### Step 4: Document Applicability

Where else could this pattern help?

```json
{
  "pattern": "visual-decision-tree",
  "found_in": "decision-logic-framework",
  "could_apply_to": [
    "moai-foundation-core (delegation decisions)",
    "builder-skill (creation type decisions)",
    "expert-* agents (routing decisions)"
  ]
}
```

---

## Pattern Documentation Format

```markdown
## Pattern: {pattern-name}

**Category**: Structure | Documentation | Integration | Quality
**Found In**: {source component}
**Confidence**: High | Medium | Low

### Description
{What this pattern does and why it works}

### Example
{Concrete example from source}

### How to Apply
{Steps to use this pattern elsewhere}

### Applicable To
- {component 1}: {why it would help}
- {component 2}: {why it would help}

### Caveats
{When NOT to use this pattern}
```

---

## Pattern Quality Thresholds

Only extract patterns that meet these criteria:

| Criterion | Threshold |
|-----------|-----------|
| Clarity | Can explain in 1 sentence |
| Applicability | Useful in 2+ other places |
| Independence | Works without source context |
| Value | Measurably improves target |

---

## Pattern Output Schema

```json
{
  "patterns": [
    {
      "id": "visual-decision-tree",
      "name": "Visual Decision Tree",
      "category": "documentation",
      "description": "Document complex decisions as ASCII flowcharts",
      "source": {
        "component": "decision-logic-framework",
        "location": "SKILL.md:L45-L60"
      },
      "applicability": [
        {
          "target": "moai-foundation-core",
          "reason": "Has complex delegation decisions",
          "effort": "low"
        }
      ],
      "confidence": "high",
      "example": "```\nShould this be a skill?\n├─ Reusable? → Yes\n└─ One-off? → No\n```"
    }
  ]
}
```
