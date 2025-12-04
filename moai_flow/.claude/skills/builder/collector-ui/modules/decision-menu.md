# Decision Menu Patterns

**AskUserQuestion patterns for collector decisions**

> **Version**: 1.0.0
> **Part of**: collector-ui skill
> **Last Updated**: 2025-12-04

---

## Overview

Decision menus use Claude Code's AskUserQuestion tool to present choices to users in a structured, accessible format.

---

## Standard Patterns

### Pattern 1: Post-Learning Decision

After analysis completes:

```python
AskUserQuestion({
    "questions": [{
        "header": "Next Steps",
        "question": "Analysis complete. How would you like to proceed?",
        "multiSelect": false,
        "options": [
            {
                "label": "Apply All",
                "description": "Apply all MUST_MERGE and SHOULD_MERGE recommendations automatically"
            },
            {
                "label": "Select Items",
                "description": "Choose specific components to sync from the list"
            },
            {
                "label": "View Details",
                "description": "See detailed breakdown for each component before deciding"
            },
            {
                "label": "Skip",
                "description": "Save analysis results and exit without making changes"
            }
        ]
    }]
})
```

### Pattern 2: Component Selection

For selective sync:

```python
AskUserQuestion({
    "questions": [{
        "header": "Components",
        "question": "Select components to sync (you can select multiple)",
        "multiSelect": true,
        "options": [
            {
                "label": "foundation-core",
                "description": "UPDATE from SPEC-first branch (Score: 72 -> 91, +19)"
            },
            {
                "label": "decision-framework",
                "description": "SMART MERGE local + main (Local: 85, Main: 88)"
            },
            {
                "label": "builder-skill",
                "description": "UPDATE from main branch (Score: 78 -> 82, +4)"
            }
        ]
    }]
})
```

### Pattern 3: Sync Strategy

Choose sync approach:

```python
AskUserQuestion({
    "questions": [{
        "header": "Strategy",
        "question": "How should conflicts between sources be handled?",
        "multiSelect": false,
        "options": [
            {
                "label": "Best Score Wins",
                "description": "Always use version with highest quality score"
            },
            {
                "label": "Smart Merge",
                "description": "Combine unique features from both sources"
            },
            {
                "label": "Ask Each",
                "description": "Prompt for decision on each conflict"
            }
        ]
    }]
})
```

### Pattern 4: Confirmation

Before applying changes:

```python
AskUserQuestion({
    "questions": [{
        "header": "Confirm",
        "question": "Ready to apply 3 changes to your workspace. Proceed?",
        "multiSelect": false,
        "options": [
            {
                "label": "Apply Now",
                "description": "Execute sync operations with backup creation"
            },
            {
                "label": "Dry Run",
                "description": "Show what would change without modifying files"
            },
            {
                "label": "Cancel",
                "description": "Abort operation, no changes will be made"
            }
        ]
    }]
})
```

### Pattern 5: Tier-Based Priority

For batch operations:

```python
AskUserQuestion({
    "questions": [{
        "header": "Priority",
        "question": "Which priority branches should be processed?",
        "multiSelect": true,
        "options": [
            {
                "label": "Tier 1: Critical",
                "description": "2 branches with score 90+ (SPEC-first, security-patch)"
            },
            {
                "label": "Tier 2: Important",
                "description": "3 branches with score 75-89 (workspace, tdd, refactor)"
            },
            {
                "label": "Tier 3: Minor",
                "description": "1 branch with score 50-74 (docs-update)"
            }
        ]
    }]
})
```

### Pattern 6: Contribution Selection

For upstream PRs:

```python
AskUserQuestion({
    "questions": [{
        "header": "Contribute",
        "question": "Select local innovations to contribute upstream",
        "multiSelect": true,
        "options": [
            {
                "label": "collector-scan (NEW)",
                "description": "New skill for workspace comparison (Score: 88)"
            },
            {
                "label": "collector-learner (IMPROVED)",
                "description": "Enhanced with multi-source scoring (+17 vs remote)"
            },
            {
                "label": "sync-strategy (NEW)",
                "description": "New module for selective sync decisions (Score: 85)"
            }
        ]
    }]
})
```

---

## Multi-Question Patterns

### Combined Strategy + Selection

```python
AskUserQuestion({
    "questions": [
        {
            "header": "Sync Mode",
            "question": "What type of sync would you like to perform?",
            "multiSelect": false,
            "options": [
                {
                    "label": "Pull Only",
                    "description": "Only update local with remote improvements"
                },
                {
                    "label": "Bidirectional",
                    "description": "Also propose PRs for local innovations"
                }
            ]
        },
        {
            "header": "Branches",
            "question": "Which branches should be compared?",
            "multiSelect": true,
            "options": [
                {
                    "label": "main",
                    "description": "Default branch, most stable"
                },
                {
                    "label": "feature/SPEC-first",
                    "description": "Active feature branch (Score: 91)"
                },
                {
                    "label": "feature/workspace",
                    "description": "Active feature branch (Score: 82)"
                }
            ]
        }
    ]
})
```

---

## Language Support

Menus should use conversation_language from config:

### Korean Example

```python
AskUserQuestion({
    "questions": [{
        "header": "Next Steps",
        "question": "Analysis complete. Select next action.",
        "multiSelect": false,
        "options": [
            {
                "label": "Apply All",
                "description": "Apply all MUST_MERGE and SHOULD_MERGE recommendations"
            },
            {
                "label": "Select Components",
                "description": "Choose specific components to sync"
            },
            {
                "label": "View Details",
                "description": "Check detailed analysis for each component"
            },
            {
                "label": "Exit",
                "description": "Save current state and end"
            }
        ]
    }]
})
```

---

## Styling Rules

1. **No Emojis**: Avoid emojis in label and description
2. **Concise Labels**: 1-5 words maximum
3. **Clear Descriptions**: Explain implications or next steps
4. **Consistent Order**: Most common action first

---

## Error Handling

When user selects "Other":

```yaml
handle_other:
  prompt: "Please describe your preferred action:"
  then:
    - Parse user input
    - Map to closest available action
    - OR: Create custom action if valid
```

---

**Version**: 1.0.0 | **Status**: Production Ready | **Last Updated**: 2025-12-04
