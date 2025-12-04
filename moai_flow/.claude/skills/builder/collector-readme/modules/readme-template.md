# README Template Structure

**Standard template for branch README generation**

> **Version**: 1.0.0
> **Part of**: collector-readme skill
> **Last Updated**: 2025-12-04

---

## Complete Template

```markdown
# Branch: {{branch_name}}

> **Status**: {{status}} | **Tier**: {{tier_label}} | **Score**: {{score}}/100

{{description}}

---

## Quick Stats

| Attribute | Value |
|-----------|-------|
| Created | {{created_at}} |
| Last Updated | {{last_updated}} |
| Commits | {{commit_count}} |
| Base Branch | {{base_branch}} |
| Components | {{component_count}} |

---

## Score Evolution

{{score_table}}

{{score_chart}}

---

## Improvements Introduced

{{#each improvements}}
### {{order}}. {{title}}

- **Type**: {{type}}
- **Impact**: {{impact}}
- **Description**: {{description}}

{{/each}}

---

## Components

### Modified Components

{{component_table}}

### Score Breakdown

{{score_breakdown_chart}}

---

## Merge Status

| Criterion | Status |
|-----------|--------|
| Ready for Main | {{ready_for_main}} |
| Conflicts | {{conflicts}} |
| CI Status | {{ci_status}} |
| Reviews | {{review_status}} |

**Recommended Action**: {{recommended_action}}

{{#if merge_command}}
**Merge Command**:
```bash
{{merge_command}}
```
{{/if}}

---

## Timeline

{{timeline_gantt}}

| Phase | Start | End | Duration |
|-------|-------|-----|----------|
{{#each phases}}
| {{name}} | {{start}} | {{end}} | {{duration}} |
{{/each}}

---

## Notes

{{#each notes}}
> **{{date}}** ({{author}}): {{content}}

{{/each}}

---

*Generated: {{generated_at}} | Collector: v{{collector_version}}*
```

---

## Section Templates

### Header Template

```markdown
# Branch: {{branch_name}}

> **Status**: {{status}} | **Tier**: {{tier_label}} | **Score**: {{score}}/100

{{description}}
```

**Variables**:
- `branch_name`: Display name of branch
- `status`: Active, Merged, Stale, Abandoned
- `tier_label`: Tier 1-4 with label
- `score`: Current quality score
- `description`: Brief branch description

### Stats Table Template

```markdown
## Quick Stats

| Attribute | Value |
|-----------|-------|
| Created | {{created_at}} |
| Last Updated | {{last_updated}} |
| Commits | {{commit_count}} |
| Base Branch | {{base_branch}} |
| Components | {{component_count}} |
```

### Score Evolution Template

```markdown
## Score Evolution

| Date | Score | Change | Notes |
|------|-------|--------|-------|
{{#each score_history}}
| {{date}} | {{score}} | {{delta}} | {{notes}} |
{{/each}}

{{score_chart}}
```

### Improvements Template

```markdown
## Improvements Introduced

{{#each improvements}}
### {{order}}. {{title}}

- **Type**: {{type}}
- **Impact**: {{impact}}
- **Description**: {{description}}

{{/each}}
```

### Components Template

```markdown
## Components

| Component | Action | Score | Description |
|-----------|--------|-------|-------------|
{{#each components}}
| {{name}} | {{action}} | {{score}} | {{description}} |
{{/each}}

**Total**: {{total_count}} components ({{new_count}} new, {{modified_count}} modified)
```

### Merge Status Template

```markdown
## Merge Status

| Criterion | Status |
|-----------|--------|
| Ready for Main | {{ready_for_main}} |
| Conflicts | {{conflicts}} |
| CI Status | {{ci_status}} |
| Reviews | {{review_status}} |

**Recommended Action**: {{recommended_action}}
```

### Timeline Template

```markdown
## Timeline

{{timeline_gantt}}

| Phase | Start | End | Duration |
|-------|-------|-----|----------|
{{#each phases}}
| {{name}} | {{start}} | {{end}} | {{duration}} |
{{/each}}
```

---

## Template Variables Reference

### Branch Metadata

| Variable | Type | Description |
|----------|------|-------------|
| `branch_name` | string | Branch display name |
| `branch_id` | string | Branch identifier |
| `status` | string | Current status |
| `tier` | int | Tier number (1-4) |
| `tier_label` | string | Full tier label |
| `score` | int | Current score |
| `description` | string | Branch description |

### Dates

| Variable | Type | Format |
|----------|------|--------|
| `created_at` | date | YYYY-MM-DD |
| `last_updated` | date | YYYY-MM-DD |
| `generated_at` | datetime | ISO 8601 |

### Statistics

| Variable | Type | Description |
|----------|------|-------------|
| `commit_count` | int | Total commits |
| `component_count` | int | Components affected |
| `new_count` | int | New components |
| `modified_count` | int | Modified components |

### Arrays

| Variable | Type | Items |
|----------|------|-------|
| `score_history` | array | {date, score, delta, notes} |
| `improvements` | array | {order, title, type, impact, description} |
| `components` | array | {name, action, score, description} |
| `phases` | array | {name, start, end, duration} |
| `notes` | array | {date, author, content} |

---

## Rendering Engine

### Pseudo-Implementation

```python
def render_readme(template: str, data: BranchData) -> str:
    """
    Render README template with branch data.
    """
    # Simple variable substitution
    for key, value in data.flat_vars().items():
        template = template.replace(f"{{{{key}}}}", str(value))

    # Handle each loops
    template = render_loops(template, data)

    # Handle conditionals
    template = render_conditionals(template, data)

    # Generate charts
    template = insert_charts(template, data)

    return template
```

---

## Conditional Sections

### If Merged

```markdown
{{#if merged}}
## Merge Information

- **Merged At**: {{merged_at}}
- **Merged By**: {{merged_by}}
- **PR**: {{pr_url}}
{{/if}}
```

### If Has Conflicts

```markdown
{{#if has_conflicts}}
## Conflicts

The following conflicts need resolution:

{{#each conflicts}}
- `{{file}}`: {{description}}
{{/each}}
{{/if}}
```

### If Stale

```markdown
{{#if is_stale}}
## Stale Notice

This branch has been inactive for {{days_inactive}} days.

**Options**:
1. Resume development
2. Archive branch
3. Close as abandoned
{{/if}}
```

---

**Version**: 1.0.0 | **Status**: Production Ready | **Last Updated**: 2025-12-04
