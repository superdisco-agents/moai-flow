# Module: Conflict Resolution

## Overview

Strategies for handling situations where both workspaces modified the same component differently.

---

## Conflict Types

### Type 1: Parallel Addition

Both workspaces added different things to the same component.

```
Component: builder-skill
Workspace A: Added workflow/ directory
Workspace B: Added scripts/ with UV templates

Conflict Type: PARALLEL_ADDITION
Resolution: Usually SMART_MERGE
```

### Type 2: Divergent Modification

Both workspaces changed the same file differently.

```
Component: moai-foundation-core
Workspace A: Changed SKILL.md structure
Workspace B: Changed SKILL.md examples

Conflict Type: DIVERGENT_MODIFICATION
Resolution: Analyze changes, may need SMART_MERGE or TAKE_BEST
```

### Type 3: Incompatible Changes

Changes conflict fundamentally and cannot both exist.

```
Component: config-manager
Workspace A: Uses JSON config format
Workspace B: Uses YAML config format

Conflict Type: INCOMPATIBLE_CHANGES
Resolution: TAKE_BEST or CREATE_NEW
```

### Type 4: Delete vs Modify

One workspace deleted something the other modified.

```
Component: deprecated-feature
Workspace A: Deleted the module
Workspace B: Updated the module

Conflict Type: DELETE_VS_MODIFY
Resolution: Investigate intent, usually TAKE_DELETE
```

---

## Resolution Strategies

### Strategy 1: TAKE_A

Use workspace A's version entirely.

**When to Use**:
- A's version is clearly superior (score difference > 15)
- A is the designated source of truth
- B's changes are experimental/incomplete

**Process**:
```
1. Verify A's version works standalone
2. Document why B's changes aren't used
3. Copy A's version to target
```

---

### Strategy 2: TAKE_B

Use workspace B's version entirely.

**When to Use**:
- B's version is clearly superior (score difference > 15)
- A's changes were superseded
- B has production-tested version

**Process**:
```
1. Verify B's version works standalone
2. Document why A's changes aren't used
3. Copy B's version to target
```

---

### Strategy 3: SMART_MERGE

Combine the best of both versions.

**When to Use**:
- Both have unique valuable additions
- Changes are in different areas (parallel addition)
- Combined version would be better than either

**Process**:
```
1. Identify non-overlapping additions from each
2. Identify overlapping changes
3. For overlapping: choose better version with reasoning
4. Combine into merged version
5. Validate merged version works
6. Document merge decisions
```

**Example**:
```markdown
## Smart Merge: builder-skill

### From A:
- workflow/build-skill.md (full workflow)
- workflow/build-agent.md (full workflow)

### From B:
- scripts/uv_create_skill.py (automation)
- scripts/uv_create_agent.py (automation)

### Overlapping (SKILL.md):
- A's structure: More organized (keep)
- B's examples: More complete (keep)
- A's frontmatter: More metadata (keep)
- B's "Works Well With": More entries (keep)

### Merged Result:
- A's structure + B's examples
- A's workflow/ + B's scripts/
- Combined "Works Well With" section
```

---

### Strategy 4: ENHANCE_BOTH

Create a new version better than either.

**When to Use**:
- Both versions have significant limitations
- Merge opportunity to improve substantially
- Clear path to better design

**Process**:
```
1. Analyze limitations in both versions
2. Design improved version
3. Take best elements from each
4. Add improvements neither has
5. Document design decisions
```

---

### Strategy 5: SKIP

Don't merge either version.

**When to Use**:
- Changes conflict fundamentally
- Neither version is production-ready
- More investigation needed
- Component is being deprecated

**Process**:
```
1. Document why skip was chosen
2. Flag for future investigation
3. Note what would unblock
```

---

## Decision Tree

```
Both workspaces changed component?
├─ Changes in different areas?
│   └─ Yes → SMART_MERGE
│   └─ No → Continue
├─ One clearly better? (score diff > 15)
│   └─ Yes → TAKE_BEST
│   └─ No → Continue
├─ Changes compatible?
│   └─ Yes → SMART_MERGE
│   └─ No → Continue
├─ Worth investing in better version?
│   └─ Yes → ENHANCE_BOTH
│   └─ No → SKIP (flag for later)
```

---

## Conflict Analysis Output

```json
{
  "conflicts": [
    {
      "component": "builder-skill",
      "type": "parallel_addition",
      "a_changes": {
        "summary": "Added workflow directory",
        "files_added": ["workflow/build-skill.md"],
        "files_modified": ["SKILL.md"],
        "score": 75
      },
      "b_changes": {
        "summary": "Added UV script templates",
        "files_added": ["scripts/uv_create_skill.py"],
        "files_modified": ["SKILL.md"],
        "score": 72
      },
      "analysis": {
        "overlap": ["SKILL.md"],
        "compatible": true,
        "combined_value": "high"
      },
      "recommendation": {
        "strategy": "smart_merge",
        "confidence": "high",
        "rationale": "Both add value in different areas. Combined skill would be more complete."
      },
      "merge_plan": {
        "take_from_a": ["workflow/"],
        "take_from_b": ["scripts/"],
        "merge_files": [
          {
            "file": "SKILL.md",
            "a_sections": ["structure", "frontmatter"],
            "b_sections": ["examples", "works-well-with"]
          }
        ]
      }
    }
  ]
}
```

---

## Conflict Resolution Checklist

Before resolving:
- [ ] Both versions analyzed with scores
- [ ] Change areas identified
- [ ] Compatibility assessed
- [ ] Resolution strategy chosen with rationale

After resolving:
- [ ] Merged version validated
- [ ] All valuable changes preserved
- [ ] Decision documented
- [ ] No functionality lost unintentionally

---

## Common Pitfalls

| Pitfall | Problem | Prevention |
|---------|---------|------------|
| Recency bias | "Newer = better" | Score on merit, not date |
| Loss aversion | Keep everything | Be willing to discard |
| Over-merging | Frankenstein result | Test merged version |
| Under-documenting | "Why did we do this?" | Document all decisions |
