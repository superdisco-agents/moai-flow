# Module: Commit Messages

## Overview

Templates and guidelines for creating meaningful commit messages in MoAI Flow publications.

---

## Commit Message Format

### Structure

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types for Flow

| Type | Usage |
|------|-------|
| `feat` | New skills, agents, commands added |
| `fix` | Bug fixes in existing components |
| `docs` | Documentation updates only |
| `refactor` | Restructuring without new features |
| `chore` | Maintenance, sync operations |

### Scope

Always use `flow` for MoAI Flow commits:
```
feat(flow): ...
fix(flow): ...
```

---

## Template: Full Consolidation

```markdown
feat(flow): consolidate improvements from workspace comparison

## Summary
- Consolidated: {n} skills, {n} agents, {n} commands
- Enhanced: {n} components with new modules
- Source: {workspace_name}
- Target: moai-adk (GitHub)

## Changes

### Skills Added
{for each skill}
- {skill_name} (score: {score}/100)
{end for}

### Skills Merged
{for each merged}
- {skill_name} ({strategy}: {details})
{end for}

### Skills Enhanced
{for each enhanced}
- {skill_name}: {enhancement_description}
{end for}

### Agents Added/Modified
{list or "None"}

### Commands Added/Modified
{list or "None"}

## Consolidation Details
- Collection ID: {collection_id}
- Consolidation ID: {consolidation_id}
- Learning Report: {summary}

## Patterns Learned
{for each pattern}
- {pattern_name}: {brief_description}
{end for}

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

---

## Template: Simple Sync

```markdown
chore(flow): sync {component_type} from {source_workspace}

Synced without full learning analysis:
- {component_1}
- {component_2}

Reason: {why simple sync was used}

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

---

## Template: Hotfix

```markdown
fix(flow): {brief description of fix}

## Issue
{what was wrong}

## Fix
{what was changed to fix it}

## Affected Components
- {component_1}
- {component_2}

## Testing
- {how it was verified}

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

---

## Generating Commit Messages

### From Consolidation Report

```python
def generate_commit_message(consolidation_report: dict) -> str:
    """Generate commit message from consolidation report."""

    summary = consolidation_report['summary']
    changes = consolidation_report['changes']

    # Count by type
    skills_added = [c for c in changes if c['action'] == 'copy' and c['type'] == 'skill']
    skills_merged = [c for c in changes if c['action'] == 'merge' and c['type'] == 'skill']
    skills_enhanced = [c for c in changes if c['action'] == 'enhance' and c['type'] == 'skill']

    msg = f"""feat(flow): consolidate improvements from workspace comparison

## Summary
- Consolidated: {len(skills_added)} skills added, {len(skills_merged)} merged
- Enhanced: {len(skills_enhanced)} components
- Source: {consolidation_report['source_workspace']}
- Target: moai-adk (GitHub)

## Changes

### Skills Added
"""

    for change in skills_added:
        msg += f"- {change['component']} (score: {change['score']}/100)\n"

    if skills_merged:
        msg += "\n### Skills Merged\n"
        for change in skills_merged:
            msg += f"- {change['component']} ({change['merge_strategy']})\n"

    if skills_enhanced:
        msg += "\n### Skills Enhanced\n"
        for change in skills_enhanced:
            msg += f"- {change['component']}: {change['enhancement']}\n"

    msg += f"""
## Consolidation Details
- Collection ID: {consolidation_report['collection_id']}
- Consolidation ID: {consolidation_report['consolidation_id']}

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
"""

    return msg
```

---

## Commit Message Best Practices

### DO

- Start with type(scope): format
- Use imperative mood ("add" not "added")
- Include consolidation IDs for traceability
- List what was changed and why
- Keep subject line under 72 characters
- Include Claude Code attribution

### DON'T

- Use vague messages like "update files"
- Include sensitive information
- Write essays in the subject line
- Forget the footer with attribution
- Skip the body for significant changes

---

## Example Real Commit

```markdown
feat(flow): consolidate improvements from workspace comparison

## Summary
- Consolidated: 2 skills, 0 agents, 0 commands
- Enhanced: 1 component with new modules
- Source: beyond-mcp
- Target: moai-adk (GitHub)

## Changes

### Skills Added
- decision-logic-framework (score: 88/100)

### Skills Merged
- builder (smart merge: workflow/ from beyond-mcp + scripts/ from moai-ir-deck)

### Skills Enhanced
- moai-connector-github: added error-handling module

## Consolidation Details
- Collection ID: flow-2025-12-02-001
- Consolidation ID: cons-2025-12-02-001
- Learning Report: 1 must_merge, 1 should_merge, 1 enhancement

## Patterns Learned
- visual-decision-tree: Document decisions as flowcharts

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```
