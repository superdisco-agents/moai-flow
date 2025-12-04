# Module: Compare Versions

## Overview

Logic for comparing two workspace scans to identify differences.

---

## Comparison Categories

### 1. Set Differences (Skills, Agents, Commands)

```
Given: Set A = components from workspace A
       Set B = components from workspace B

Calculate:
- only_in_a = A - B  (items in A but not B)
- only_in_b = B - A  (items in B but not A)
- in_both = A ∩ B    (items in both)
```

### 2. Version Differences (for in_both)

For items that exist in both workspaces:
1. Compare file modification times
2. Compare file sizes
3. Compare content hashes (if needed)

```
if A.modified > B.modified:
    newer = "a"
elif B.modified > A.modified:
    newer = "b"
else:
    newer = "same"
```

### 3. Structural Differences

Compare structure metrics:
- Module count within skills
- File count within directories
- Line count in SKILL.md/AGENT.md

---

## Comparison Algorithm

```python
def compare_workspaces(scan_a, scan_b):
    result = {
        "skills": compare_component_lists(
            scan_a["components"]["skills"]["list"],
            scan_b["components"]["skills"]["list"]
        ),
        "agents": compare_component_lists(
            scan_a["components"]["agents"]["list"],
            scan_b["components"]["agents"]["list"]
        ),
        "commands": compare_component_lists(
            scan_a["components"]["commands"]["list"],
            scan_b["components"]["commands"]["list"]
        ),
        "version": compare_versions(
            scan_a["moai_version"],
            scan_b["moai_version"]
        ),
        "freshness": compare_dates(
            scan_a["git"]["last_commit_date"],
            scan_b["git"]["last_commit_date"]
        )
    }
    return result

def compare_component_lists(list_a, list_b):
    set_a = set(list_a)
    set_b = set(list_b)
    return {
        "only_in_a": sorted(set_a - set_b),
        "only_in_b": sorted(set_b - set_a),
        "in_both": sorted(set_a & set_b)
    }
```

---

## Difference Categories

| Category | Meaning | Action |
|----------|---------|--------|
| `only_in_a` | New in workspace A | Consider adding to B |
| `only_in_b` | New in workspace B | Consider adding to A |
| `in_both_different` | Modified differently | Deep compare needed |
| `in_both_same` | Identical | No action needed |

---

## Output Format

```json
{
  "skills": {
    "only_in_a": ["skill1", "skill2"],
    "only_in_b": ["skill3"],
    "in_both": ["skill4", "skill5"],
    "in_both_different": ["skill6"]
  },
  "summary": {
    "total_differences": 4,
    "a_has_more": true,
    "newer_workspace": "a"
  }
}
```
