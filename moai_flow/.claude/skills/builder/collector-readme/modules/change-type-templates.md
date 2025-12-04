---
name: Change Type Templates
version: 1.0.0
part_of: collector-readme
description: Template definitions for different types of changes detected in the codebase
---

# Change Type Templates

This module defines templates for documenting different types of changes detected during README collection. Each template provides a structured format for presenting changes in a consistent, scannable manner.

## Change Type Detection Rules

The system automatically detects change types based on file patterns and content:

### Agent Changes
- **File Pattern**: `.claude/agents/**/*.md`
- **Content Signal**: YAML frontmatter containing `tools:` key
- **Example Path**: `.claude/agents/moai/backend-expert.md`

### Skill Changes
- **File Pattern**: `.claude/skills/**/SKILL.md`
- **Content Signal**: YAML frontmatter containing `version:` key
- **Example Path**: `.claude/skills/moai-foundation-core/SKILL.md`

### Workflow Changes
- **File Pattern**: `**/workflows/*/instructions.md`
- **Content Signal**: Content containing `Workflow ID:` header
- **Example Path**: `.moai/workflows/spec-first-tdd/instructions.md`

### TOON Changes
- **File Pattern**: Any markdown file
- **Content Signal**: Content containing `TOON-` pattern (e.g., `TOON-001`, `TOON-SPEC-001`)
- **Example Content**: `This implements TOON-AUTH-003 for secure token handling`

### Command Changes
- **File Pattern**: `.claude/commands/**/*.md`
- **Content Signal**: Markdown file in commands directory
- **Example Path**: `.claude/commands/moai/1-plan.md`

### Hook Changes
- **File Pattern**: `.claude/hooks/**/*.py`
- **Content Signal**: Python file in hooks directory
- **Example Path**: `.claude/hooks/moai/session_start__load_memory.py`

## Agent Change Template

Use this template when changes involve Claude Code agents.

### Agent Summary

| Attribute | Value |
|-----------|-------|
| **Agent Name** | `{agent_name}` |
| **Action** | Added / Modified / Removed |
| **Tier** | Core / Domain / Specialized |
| **Skills Affected** | List of skill names or "None" |
| **Impact** | High / Medium / Low |

### Capabilities Changed

| Capability | Before | After | Breaking? |
|------------|--------|-------|-----------|
| `{capability_name}` | Description of old behavior | Description of new behavior | Yes / No |

### Dependencies Affected

**Skills Modified**:
- `skill-name-1`: Reason for modification
- `skill-name-2`: Reason for modification

**Commands Modified**:
- `command-name-1`: Reason for modification

**Other Agents Affected**:
- `agent-name-1`: Nature of dependency
- `agent-name-2`: Nature of dependency

### Invocation Pattern

**Before**:
```markdown
/agent old-agent-name "task description"
```

**After**:
```markdown
/agent new-agent-name "task description" --option value
```

### User Guidance

| Scenario | Action Required |
|----------|-----------------|
| **New Projects** | Use new invocation pattern directly |
| **Existing Projects** | Update agent references in workflows |
| **Migration Needed** | Follow migration steps in [link] |

## Skill Change Template

Use this template when changes involve Claude Code skills.

### Skill Summary

| Attribute | Value |
|-----------|-------|
| **Skill Name** | `{skill_name}` |
| **Action** | Added / Modified / Removed |
| **Version** | Before: `{old_version}` → After: `{new_version}` |
| **Breaking Change** | Yes / No |
| **Impact** | High / Medium / Low |

### Modules Added/Modified

| Module Path | Action | Purpose |
|-------------|--------|---------|
| `modules/{module_name}.md` | Added / Modified / Removed | Brief description |

### API Changes

**New Features**:
```python
# New function or pattern introduced
def new_feature(param1: str, param2: int) -> Result:
    """Description of new capability."""
    pass
```

**Deprecated Features**:
```python
# Old pattern (deprecated)
def old_pattern():
    """Will be removed in version X.X.X."""
    warnings.warn("Use new_feature() instead", DeprecationWarning)
```

**Removed Features**:
- `old_function()`: Removed in this version. Use `new_feature()` instead.
- `deprecated_class`: No replacement. Functionality integrated into core.

### Migration Guide

**If Breaking Change**:

1. **Update imports**:
   ```python
   # Before
   from old_module import OldClass

   # After
   from new_module import NewClass
   ```

2. **Update usage patterns**:
   ```python
   # Before
   result = old_function(param)

   # After
   result = new_function(param, new_required_param)
   ```

3. **Update configuration**:
   ```json
   {
     "old_key": "value",
     "new_key": "value",
     "removed_key": null
   }
   ```

### User Guidance

| Scenario | Action Required |
|----------|-----------------|
| **New Projects** | Include skill in `.claude/settings.json` |
| **Existing Projects (Non-Breaking)** | Update skill version, test functionality |
| **Existing Projects (Breaking)** | Follow migration guide above |
| **Dependent Skills** | Update {list} to latest compatible versions |

## Workflow Change Template

Use this template when changes involve workflow instructions.

### Workflow Summary

| Attribute | Value |
|-----------|-------|
| **Workflow Name** | `{workflow_name}` |
| **Action** | Added / Modified / Removed |
| **Steps Changed** | Added: {n} / Modified: {n} / Removed: {n} |
| **Trigger Changed** | Yes / No |

### Step Sequence

**Before**:
```
1. Initialize context
2. Validate inputs
3. Execute main logic
4. Return results
```

**After**:
```
1. Initialize context
2. Load prerequisites (NEW)
3. Validate inputs (MODIFIED)
4. Execute main logic
5. Post-process results (NEW)
6. Return results
```

### Input/Output Changes

**Inputs**:

| Parameter | Before | After | Required? |
|-----------|--------|-------|-----------|
| `{param_name}` | Type, description | Type, description | Yes / No |

**Outputs**:

| Field | Before | After | Always Present? |
|-------|--------|-------|-----------------|
| `{field_name}` | Type, description | Type, description | Yes / No |

### Integration Points

**Agents Used**:
- Before: `agent-1`, `agent-2`
- After: `agent-1`, `agent-3` (replaced agent-2)

**Skills Required**:
- Before: `skill-a`, `skill-b`
- After: `skill-a`, `skill-b`, `skill-c` (new dependency)

**External Dependencies**:
- API endpoints called
- File system paths accessed
- Environment variables required

### User Guidance

| Scenario | Action Required |
|----------|-----------------|
| **Invoking Workflow** | `moai workflow run {workflow_name} --param value` |
| **Configuration** | Update `.moai/config.json` with new parameters |
| **Prerequisites** | Ensure {list} are installed/configured |

## TOON Change Template

Use this template when changes involve Templated Operational Orchestration Narratives (TOONs).

### TOON Summary

| Attribute | Value |
|-----------|-------|
| **TOON ID** | `TOON-{CATEGORY}-{NUMBER}` |
| **Action** | Added / Modified / Removed |
| **Purpose** | Brief description of what this TOON accomplishes |
| **Steps Changed** | Added: {n} / Modified: {n} / Removed: {n} |

### Step Sequence Changes

| Step | Before | After | Reason |
|------|--------|-------|--------|
| 1 | Description | Description (modified) | Explanation |
| 2 | - | New step added | Explanation |
| 3 | Old step removed | - | Explanation |

### Data Flow

**Before**:
```
Input → Step 1 → Step 2 → Output
         ↓
      Side Effect
```

**After**:
```
Input → Step 1 → Validation (NEW) → Step 2 → Transformation (NEW) → Output
         ↓                           ↓
      Side Effect              Enhanced Side Effect
```

### TOON Variables

| Variable | Type | Description | Default |
|----------|------|-------------|---------|
| `{VAR_NAME}` | string / number / boolean | Purpose | Value |

### Example Usage

**Invoking the TOON**:
```bash
# Command line
moai toon execute TOON-{CATEGORY}-{NUMBER} \
  --var1 "value1" \
  --var2 "value2"
```

**In Agent Context**:
```markdown
To accomplish this task, I'll execute TOON-{CATEGORY}-{NUMBER}:

1. Set VAR_NAME to "{value}"
2. Execute TOON steps
3. Validate results
```

### User Guidance

| Scenario | Action Required |
|----------|-----------------|
| **Direct Execution** | Use command line invocation above |
| **Agent Delegation** | Agent will invoke TOON automatically |
| **Custom Variables** | Override defaults as shown in example |
| **Error Handling** | Review logs at `.moai/logs/toons/{id}.log` |

## Mixed Change Template

Use this template when a commit contains multiple types of changes.

### Change Distribution

| Change Type | Count | Impact Level | Breaking? |
|-------------|-------|--------------|-----------|
| Agents | {n} | High / Medium / Low | Yes / No |
| Skills | {n} | High / Medium / Low | Yes / No |
| Workflows | {n} | High / Medium / Low | Yes / No |
| TOONs | {n} | High / Medium / Low | Yes / No |
| Commands | {n} | High / Medium / Low | Yes / No |
| Hooks | {n} | High / Medium / Low | Yes / No |

### Organized by Impact

#### High Impact Changes

**Agents**:
- `{agent_name}`: {brief_description}
  - See [Agent Change Template](#agent-change-template) for details

**Skills**:
- `{skill_name}`: {brief_description}
  - See [Skill Change Template](#skill-change-template) for details

#### Medium Impact Changes

**Workflows**:
- `{workflow_name}`: {brief_description}
  - See [Workflow Change Template](#workflow-change-template) for details

**TOONs**:
- `TOON-{ID}`: {brief_description}
  - See [TOON Change Template](#toon-change-template) for details

#### Low Impact Changes

**Commands**:
- `{command_name}`: {brief_description}

**Hooks**:
- `{hook_name}`: {brief_description}

### Cumulative User Guidance

| Scenario | Actions Required |
|----------|------------------|
| **New Projects** | Start with latest versions of all components |
| **Existing Projects (No Breaking Changes)** | Update incrementally, test after each update |
| **Existing Projects (Breaking Changes)** | Follow migration guides in order: {list} |
| **CI/CD Integration** | Update pipeline configs to reflect new dependencies |

### Migration Priority Order

When multiple breaking changes exist, follow this order:

1. **Skills**: Update foundational skills first (dependencies of agents)
2. **Agents**: Update agents that depend on modified skills
3. **Workflows**: Update workflows that use modified agents
4. **TOONs**: Update TOONs that reference modified workflows
5. **Commands**: Update command invocations
6. **Hooks**: Update hooks that integrate with modified components

## Template Selection Logic

Use the following logic to select the appropriate template:

```python
def select_template(changes: List[Change]) -> str:
    """Select appropriate template based on change composition."""
    change_types = set(c.type for c in changes)

    if len(change_types) == 1:
        # Single type of change
        return f"{change_types.pop()}_template"

    elif len(change_types) <= 2 and count_breaking(changes) == 0:
        # Two types, non-breaking - can use dominant type
        dominant = max_count_type(changes)
        return f"{dominant}_template"

    else:
        # Multiple types or breaking changes - use mixed template
        return "mixed_template"
```

## Best Practices

### For Template Authors

1. **Be Concise**: Each template section should fit on screen without scrolling
2. **Show Examples**: Include code examples for patterns, not just descriptions
3. **Link Related**: Cross-reference related sections for complex changes
4. **Highlight Breaking**: Use **bold** or `BREAKING:` prefix for breaking changes
5. **Provide Context**: Explain WHY a change was made, not just WHAT changed

### For Template Users

1. **Fill Completely**: Don't skip sections, use "None" or "N/A" if not applicable
2. **Be Specific**: Use actual values, not placeholders
3. **Test Examples**: Verify code examples work before including them
4. **Update Links**: Ensure all cross-references resolve correctly
5. **Validate Markdown**: Use a linter to check formatting before committing

## Validation Checklist

Before finalizing README content generated from these templates:

- [ ] All tables have headers and proper alignment
- [ ] Code blocks specify language for syntax highlighting
- [ ] File paths use absolute or repository-relative notation
- [ ] Breaking changes are clearly marked
- [ ] Migration guides include executable code examples
- [ ] User guidance covers all common scenarios
- [ ] Cross-references use valid section anchors
- [ ] TOON IDs follow naming convention
- [ ] Version numbers follow semantic versioning
- [ ] Impact assessments are justified

## Template Versioning

These templates follow semantic versioning:

- **Major**: Breaking changes to template structure (e.g., removing required sections)
- **Minor**: New template features or sections (e.g., adding optional fields)
- **Patch**: Clarifications, typos, formatting improvements

Current version: **1.0.0**

## Related Documentation

- **Change Detection**: See `modules/change-detection.md` for how changes are identified
- **Content Structuring**: See `modules/content-structuring.md` for how templates are populated
- **README Generation**: See `modules/readme-generation.md` for how templates become README files
