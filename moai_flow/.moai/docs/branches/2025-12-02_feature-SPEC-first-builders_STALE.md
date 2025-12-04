<div align="center">

# feature/SPEC-first-builders

[![Status](https://img.shields.io/badge/Status-STALE-yellow?style=for-the-badge)]()
[![PR](https://img.shields.io/badge/PR-None-lightgray?style=for-the-badge)]()

**Collector Scope: `.claude/` `.moai/` `src/moai_adk/`**

</div>

---

## MoAI Changes in This Branch

**Commit**: `e2494cb` | **Date**: 2025-12-02 05:37

Only 1 of 5 commits contains MoAI-relevant changes (the others only modified README.md).

---

## .claude/ Changes

### New Skill: moai-localization-bilingual

```
.claude/skills/moai-localization-bilingual/
├── SKILL.md                      (+326 lines)  # Bilingual documentation skill
├── SPEC-REF.md                   (+44 lines)   # Links to SPEC-SKILL-001
└── modules/
    ├── glossary-terms.md         (+209 lines)  # English/Korean term glossary
    └── pattern-translation.md    (+226 lines)  # Translation patterns
```

**Purpose**: Bilingual (English + Korean) document creation with Decision Logic rules

**Decision Logic Rules**:

| Rule ID | Purpose |
|---------|---------|
| DL-LOC-001 | Header: `# English / 한국어` |
| DL-LOC-002 | Description: Korean below English |
| DL-LOC-003 | Table: Add `설명` column |
| DL-LOC-004 | Preserve: agent, skill, workflow, command |
| DL-LOC-005 | Exclude: Don't translate code blocks |

---

## .moai/ Changes

### New SPEC: SPEC-SKILL-001

```
.moai/specs/
├── SPEC-SKILL-001/
│   └── SPEC.md                   (+119 lines)  # First SPEC-created skill
└── index.toon                    (modified)    # Added SPEC reference
```

**Significance**: First skill created using SPEC-First methodology

---

## src/moai_adk/ Changes

### Template Sync

```
src/moai_adk/templates/.claude/skills/moai-localization-bilingual/
├── SKILL.md                      (+326 lines)
├── SPEC-REF.md                   (+44 lines)
└── modules/
    ├── glossary-terms.md         (+209 lines)
    └── pattern-translation.md    (+226 lines)
```

Skill synced to templates for `moai init` distribution.

---

## Summary for Collector

| Directory | Changes | Files |
|-----------|---------|-------|
| `.claude/skills/` | +1 skill (moai-localization-bilingual) | 4 files |
| `.moai/specs/` | +1 SPEC (SPEC-SKILL-001) | 2 files |
| `src/moai_adk/templates/` | Template sync | 4 files |
| **Total** | **+1,733 lines** | **10 files** |

---

## Current Status

```
Commits Ahead:   0 (content already in main)
Commits Behind:  5
PR Created:      No
```

**Recommendation**: Delete branch - content already merged via other PRs

```bash
git push origin --delete feature/SPEC-first-builders
```

---

<div align="center">

**Generated**: 2025-12-04 | **Scope**: `.claude/` `.moai/` `src/moai_adk/` only

</div>
