---
name: Quality Gates Module
version: 1.0.0
part_of: collector-readme
description: Validation rules and quality gates for README generation
---

# Quality Gates Module

This module defines the validation rules and quality gates that must be passed before a README can be considered complete and saved to the repository.

## Overview

Quality gates ensure that generated READMEs meet minimum standards for completeness, accuracy, and usefulness. Gates are organized into four levels with different severity levels.

## Gate 1: BLOCKING Requirements

These requirements MUST pass before the README can be saved. Failure to meet any of these requirements should halt the generation process.

### Required Elements

| Element | Requirement | Validation |
|---------|------------|------------|
| Header Badges | Exactly 3 badges in order: Status, Tier, Score | `grep -c "!\[.*\]" README.md` must equal 3 |
| TL;DR Section | Must exist with 20-75 words | Section exists and word count in range |
| Quick Stats Table | Must have 5+ rows with key metrics | Table exists with minimum row count |
| Change Type Badge | Must show one of: [AGENT], [SKILL], [WORKFLOW], [TOON], [MIXED] | Badge matches regex pattern |
| Merge Status | Must include merge readiness guidance | Section exists with clear guidance |

### Header Badge Format

```markdown
![Status](https://img.shields.io/badge/status-{status}-{color})
![Tier](https://img.shields.io/badge/tier-{tier}-{color})
![Score](https://img.shields.io/badge/score-{score}-{color})
```

### Change Type Badge Values

| Badge | Description |
|-------|-------------|
| [AGENT] | Agent-only changes |
| [SKILL] | Skill-only changes |
| [WORKFLOW] | Workflow or command changes |
| [TOON] | Hook changes |
| [MIXED] | Multiple categories affected |

### Merge Status Guidance

Must include one of the following recommendations:

- **READY TO MERGE**: All gates passed, no blockers
- **MERGE WITH CAUTION**: Minor issues present, review recommended
- **DO NOT MERGE**: Blocking issues exist, must fix before merge
- **NEEDS REVIEW**: Manual review required before decision

## Gate 2: WARNING Requirements

These requirements SHOULD pass. Warnings are generated but do not block saving.

### Content Elements

| Element | Target | Warning Threshold |
|---------|--------|------------------|
| Mermaid Charts | 2+ recommended | Less than 1 chart |
| Tables | 4+ recommended | Less than 3 tables |
| Checklists | 2+ recommended | Less than 1 checklist |

### Warning Messages

- **WARN-001**: No Mermaid charts found. Consider adding visual diagrams.
- **WARN-002**: Only {n} tables found. Consider adding more structured data.
- **WARN-003**: No checklists found. Consider adding actionable items.

## Gate 3: Content Quality

These rules validate the quality and completeness of content sections.

### Word Count Requirements

| Section | Minimum | Maximum | Optimal |
|---------|---------|---------|---------|
| TL;DR | 20 | 75 | 40-60 |
| Description | 50 | 500 | 100-300 |
| Section Content | 10 | 1000 | 50-500 |

### Content Quality Checks

| Check | Requirement | Score Impact |
|-------|------------|--------------|
| TL;DR Word Count | 20-75 words | 5 points |
| Description Word Count | 50-500 words | 5 points |
| Minimum Improvements | 1+ items listed | 5 points |
| Minimum Checklist Items | 5+ items per checklist | 5 points |

### Quality Score Calculation

```
CONTENT_QUALITY = (
    (TLDR_VALID ? 5 : 0) +
    (DESC_VALID ? 5 : 0) +
    (IMPROVEMENTS_VALID ? 5 : 0) +
    (CHECKLIST_VALID ? 5 : 0)
) / 20
```

Range: 0.0 to 1.0

## Gate 4: Link Validation

All links must be valid and point to existing resources.

### Internal Link Rules

| Link Type | Validation | Error Code |
|-----------|-----------|------------|
| Section Anchors | Target section must exist in document | LINK-001 |
| File References | Referenced file must exist in repository | LINK-002 |
| Relative Paths | Path must resolve correctly from README location | LINK-003 |

### Link Validation Process

1. Extract all markdown links: `[text](url)`
2. Categorize links:
   - Internal anchors: `#section-name`
   - Relative files: `./path/to/file.md`
   - Repository files: `/path/from/root.md`
   - External URLs: `https://...`
3. Validate each category:
   - Anchors: Check section headers exist
   - Files: Verify file exists on filesystem
   - URLs: Skip validation (external)

### Link Quality Score

```
LINKS_VALID = (VALID_LINKS / TOTAL_INTERNAL_LINKS)
```

Range: 0.0 to 1.0

## Overall Quality Score Formula

The final quality score combines all gate results:

```
SCORE = (SECTIONS_SCORE * 40) +
        (CHARTS_SCORE * 15) +
        (TABLES_SCORE * 15) +
        (CONTENT_QUALITY * 20) +
        (LINKS_VALID * 10)
```

### Component Calculations

#### Sections Score

```
SECTIONS_SCORE = MANDATORY_SECTIONS_PRESENT / MANDATORY_SECTIONS_TOTAL
```

Mandatory sections:
1. Header with badges
2. TL;DR
3. Quick Stats
4. Change Type
5. Merge Status

Range: 0.0 to 1.0

#### Charts Score

```
CHARTS_SCORE = min(MERMAID_CHARTS_COUNT, 3) / 3
```

Range: 0.0 to 1.0 (capped at 3 charts)

#### Tables Score

```
TABLES_SCORE = min(TABLES_COUNT, 3) / 3
```

Range: 0.0 to 1.0 (capped at 3 tables)

### Score Ranges

| Range | Grade | Status |
|-------|-------|--------|
| 90-100 | A | Excellent |
| 80-89 | B | Good |
| 70-79 | C | Acceptable |
| 60-69 | D | Needs Improvement |
| 0-59 | F | Unacceptable |

### Target Score

**Target: 90/100 (Grade A)**

This ensures high-quality, comprehensive READMEs that provide maximum value.

## Validation Implementation

### Pre-Save Checklist

Before saving a generated README, verify:

- [ ] All Gate 1 (BLOCKING) requirements passed
- [ ] Gate 2 (WARNING) requirements checked (warnings logged)
- [ ] Gate 3 (CONTENT QUALITY) score calculated
- [ ] Gate 4 (LINK VALIDATION) completed
- [ ] Overall quality score >= 70 (minimum acceptable)
- [ ] Target score of 90 achieved (recommended)

### Validation Output Format

```markdown
## Quality Gate Results

### Gate 1: BLOCKING (PASS/FAIL)
- Header Badges: PASS
- TL;DR Section: PASS
- Quick Stats Table: PASS
- Change Type Badge: PASS
- Merge Status: PASS

### Gate 2: WARNINGS (0 warnings)
- Mermaid Charts: 2 found (PASS)
- Tables: 5 found (PASS)
- Checklists: 1 found (PASS)

### Gate 3: CONTENT QUALITY (18/20)
- TL;DR Word Count: 45 words (PASS)
- Description Word Count: 150 words (PASS)
- Improvements Listed: 8 items (PASS)
- Checklist Items: 12 items (PASS)

### Gate 4: LINK VALIDATION (10/10)
- Internal Links: 8/8 valid (100%)
- Section Anchors: 5/5 valid (100%)
- File References: 3/3 valid (100%)

### Overall Quality Score: 93/100 (Grade A)
```

## Error Handling

### Blocking Errors

When Gate 1 requirements fail:

1. Log specific failure with error code
2. Provide remediation guidance
3. Halt save process
4. Return to generation phase

### Warning Errors

When Gate 2 requirements fail:

1. Log warning with code
2. Continue with save process
3. Include warnings in output
4. Recommend improvements

### Quality Threshold Errors

When overall score < 70:

1. Log quality score breakdown
2. Identify weakest components
3. Provide improvement suggestions
4. Allow save with warning flag

## Integration Points

### With Analyzer Module

- Receive analyzed branch data
- Validate data completeness
- Check for required metrics

### With Generator Module

- Receive generated README content
- Run validation gates
- Return pass/fail status
- Provide remediation guidance

### With Main Skill

- Report validation results
- Block or allow save operation
- Log quality metrics
- Update status badges

## Best Practices

1. **Run gates in order**: Complete Gate 1 before moving to Gate 2
2. **Log all results**: Keep detailed validation logs for debugging
3. **Provide clear feedback**: Give specific, actionable error messages
4. **Track metrics over time**: Monitor quality trends across branches
5. **Iterate on failures**: Re-run generation with fixes, then re-validate
6. **Document exceptions**: Record any manual overrides with justification

## Examples

### Passing Validation

```markdown
Quality Gate Results: PASS
- Gate 1 (BLOCKING): 5/5 requirements met
- Gate 2 (WARNINGS): 0 warnings
- Gate 3 (CONTENT): 19/20 points
- Gate 4 (LINKS): 10/10 points
- Overall Score: 94/100 (Grade A)

Status: READY TO SAVE
```

### Failing Validation

```markdown
Quality Gate Results: FAIL
- Gate 1 (BLOCKING): 3/5 requirements met
  - FAIL: TL;DR section missing
  - FAIL: Quick Stats table has only 3 rows (minimum 5)
- Gate 2 (WARNINGS): 2 warnings
  - WARN: No Mermaid charts found
  - WARN: Only 2 tables found
- Gate 3 (CONTENT): 12/20 points
- Gate 4 (LINKS): 8/10 points
- Overall Score: 58/100 (Grade F)

Status: CANNOT SAVE - FIX BLOCKING ISSUES
```

## Maintenance

### Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-12-04 | Initial release |

### Future Enhancements

1. Add automated link validation with HTTP checks
2. Implement readability scoring (Flesch-Kincaid)
3. Add spell-check integration
4. Create visual quality dashboard
5. Add historical quality tracking
