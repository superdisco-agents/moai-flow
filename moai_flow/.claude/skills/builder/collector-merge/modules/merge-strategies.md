# Module: Merge Strategies

## Overview

Detailed algorithms for merging components when both workspaces have modifications.

---

## Merge Strategy Selection

```
Input: Conflict analysis from learner

IF conflict.type == "parallel_addition":
    strategy = DIRECTORY_MERGE
ELIF conflict.type == "divergent_modification":
    strategy = FILE_MERGE
ELIF conflict.type == "incompatible_changes":
    strategy = TAKE_BEST
ELSE:
    strategy = MANUAL_REVIEW
```

---

## Strategy 1: Directory Merge

When both workspaces added different directories to the same component.

### Algorithm

```
1. Identify base version (higher scored)
2. Copy base version to working directory
3. Identify unique directories in other version
4. Copy unique directories to working directory
5. Handle any file overlaps in root
6. Validate and move to target
```

### Example

```
Workspace A:                 Workspace B:
builder/                     builder/
├── SKILL.md                 ├── SKILL.md (different)
├── modules/                 ├── modules/ (same)
└── workflow/    ← unique    └── scripts/    ← unique

Merge Result:
builder/
├── SKILL.md     ← from A (higher score)
├── modules/     ← same in both
├── workflow/    ← from A
└── scripts/     ← from B
```

### Implementation

```bash
merge_directories() {
  local a_path=$1
  local b_path=$2
  local work_dir=$3
  local base=$4  # "a" or "b"

  # Copy base
  if [ "$base" == "a" ]; then
    cp -r "$a_path" "$work_dir"
  else
    cp -r "$b_path" "$work_dir"
  fi

  # Get unique directories from other
  local other_path=$( [ "$base" == "a" ] && echo "$b_path" || echo "$a_path" )

  for dir in "$other_path"/*/; do
    dir_name=$(basename "$dir")
    if [ ! -d "$work_dir/$dir_name" ]; then
      cp -r "$dir" "$work_dir/"
    fi
  done
}
```

---

## Strategy 2: File Merge

When both workspaces modified the same file differently.

### Section-Based Merge

For structured files like SKILL.md:

```
1. Parse both files into sections
2. For each section, determine winner:
   - If only in A: take from A
   - If only in B: take from B
   - If in both: use scoring to decide
3. Reassemble file from winning sections
```

### Section Detection

```python
def parse_sections(content):
    """Parse markdown into sections by ## headers."""
    sections = {}
    current_section = "preamble"
    current_content = []

    for line in content.split('\n'):
        if line.startswith('## '):
            if current_content:
                sections[current_section] = '\n'.join(current_content)
            current_section = line[3:].strip()
            current_content = [line]
        else:
            current_content.append(line)

    if current_content:
        sections[current_section] = '\n'.join(current_content)

    return sections
```

### Merge Decision Matrix

| A Has | B Has | Decision |
|-------|-------|----------|
| Section | Missing | Take A |
| Missing | Section | Take B |
| Same | Same | Take either |
| Different | Different | Score-based |

### Score-Based Section Selection

```python
def score_section(section_content):
    """Score a section based on quality indicators."""
    score = 0

    # Length (more comprehensive)
    lines = section_content.count('\n')
    score += min(lines * 2, 20)  # Cap at 20

    # Examples (has code blocks)
    code_blocks = section_content.count('```')
    score += code_blocks * 5

    # Tables (structured info)
    tables = section_content.count('|')
    score += min(tables, 15)

    # Links (cross-references)
    links = section_content.count('](')
    score += links * 3

    return score
```

---

## Strategy 3: Line-Level Merge

For configuration files or when section merge isn't applicable.

### Three-Way Merge Concept

```
     Common Ancestor (if available)
           /          \
          /            \
    Version A      Version B
          \            /
           \          /
         Merged Result
```

### Without Common Ancestor

When no common ancestor is available:

```
1. Find longest common subsequence (LCS)
2. Additions in A that aren't in LCS → include
3. Additions in B that aren't in LCS → include
4. Conflicts (same line, different content) → flag for review
```

### Conflict Markers

```markdown
<<<<<<< A (beyond-mcp)
This line was changed in workspace A
=======
This line was changed in workspace B
>>>>>>> B (moai-ir-deck)
```

---

## Strategy 4: Take Best

When changes are incompatible, take the better version entirely.

### Decision Criteria

```
IF score_a - score_b > 15:
    take = "a"
ELIF score_b - score_a > 15:
    take = "b"
ELSE:
    # Similar scores - use secondary criteria
    IF a.freshness > b.freshness:
        take = "a"
    ELIF b.freshness > a.freshness:
        take = "b"
    ELSE:
        take = "manual_review"
```

---

## Merge Validation

### Post-Merge Checks

```bash
validate_merge() {
  local merged_path=$1

  # Syntax check (for YAML frontmatter)
  head -30 "$merged_path/SKILL.md" | python3 -c "
import sys, yaml
content = sys.stdin.read()
parts = content.split('---')
if len(parts) >= 3:
    yaml.safe_load(parts[1])
    print('YAML OK')
"

  # Check all expected sections exist
  for section in "Quick Reference" "Works Well With" "Modules"; do
    grep -q "## $section" "$merged_path/SKILL.md" || {
      echo "WARNING: Missing section: $section"
    }
  done

  # Check no conflict markers remain
  grep -r "<<<<<<" "$merged_path" && {
    echo "ERROR: Unresolved conflicts"
    return 1
  }

  return 0
}
```

---

## Merge Output

### Merge Report

```json
{
  "component": "builder",
  "strategy": "directory_merge",
  "base": "a",
  "from_a": {
    "directories": ["workflow"],
    "files": ["SKILL.md"]
  },
  "from_b": {
    "directories": ["scripts"],
    "files": []
  },
  "merged_files": [
    {
      "file": "SKILL.md",
      "sections_from_a": ["frontmatter", "Level 1", "Level 2"],
      "sections_from_b": ["Quick Reference examples"],
      "conflicts_resolved": 0
    }
  ],
  "validation": "passed"
}
```
