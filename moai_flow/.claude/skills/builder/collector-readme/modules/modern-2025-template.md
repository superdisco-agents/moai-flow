# 🎨 Modern 2025 Hyper-Detailed README Template

**The ultimate branch documentation template with visual excellence**

> **Version**: 2.0.0
> **Status**: Production Ready
> **Style**: Modern 2025 with Emojis, Charts, Diagrams
> **Last Updated**: 2025-12-04

---

## 📋 Template Overview

This template creates **hyper-detailed** branch READMEs with:

| Feature | Description |
|---------|-------------|
| 🎯 **Hero Header** | Emoji-rich header with status badges and quick stats |
| 📊 **Visual Charts** | Mermaid pie charts, line charts, gantt timelines |
| 🏗️ **ASCII Architecture** | Visual diagrams of component relationships |
| 📈 **Progress Indicators** | Visual progress bars and completion tracking |
| 🔍 **Deep Analysis** | Comprehensive impact assessment and scoring |
| 🎬 **Timeline Visualization** | Gantt charts with milestones |
| 🧭 **Navigation** | Quick links and table of contents |

---

## 🎯 Complete Template

```markdown
<div align="center">

# {{EMOJI}} {{BRANCH_NAME}}

[![Status](https://img.shields.io/badge/Status-{{STATUS}}-{{STATUS_COLOR}}?style=for-the-badge)]()
[![Tier](https://img.shields.io/badge/Tier-{{TIER}}-{{TIER_COLOR}}?style=for-the-badge)]()
[![Score](https://img.shields.io/badge/Score-{{SCORE}}%2F100-{{SCORE_COLOR}}?style=for-the-badge)]()

**{{DESCRIPTION}}**

[📖 Overview](#-overview) • [📊 Impact](#-impact-analysis) • [🎯 Components](#-components) • [📈 Timeline](#-timeline) • [🚀 Next Steps](#-next-steps)

</div>

---

## 📋 TL;DR

> {{TLDR_SUMMARY}}

| Metric | Value | Status |
|--------|-------|--------|
| 📅 **Created** | {{CREATED_DATE}} | {{CREATED_AGO}} |
| 🔄 **Last Updated** | {{UPDATED_DATE}} | {{UPDATED_AGO}} |
| 📝 **Commits** | {{COMMIT_COUNT}} | {{COMMIT_VELOCITY}} |
| 📁 **Files Changed** | {{FILES_CHANGED}} | {{FILES_CHART}} |
| ➕ **Lines Added** | {{LINES_ADDED}} | 🟢 |
| ➖ **Lines Deleted** | {{LINES_DELETED}} | 🔴 |
| 👥 **Contributors** | {{CONTRIBUTORS}} | - |

---

## 🔍 Merge Status

{{#if IS_MERGED}}
### ✅ MERGED

> **Successfully merged** into `main` on {{MERGE_DATE}}

| Detail | Value |
|--------|-------|
| 🔗 **PR Number** | [#{{PR_NUMBER}}]({{PR_URL}}) |
| 📅 **Merged Date** | {{MERGE_DATE}} |
| 👤 **Merged By** | @{{MERGED_BY}} |
| ✅ **CI Status** | Passed |
| 🔍 **Reviews** | {{REVIEW_COUNT}} approved |

```
╔═══════════════════════════════════════════════════════════════╗
║                    🎉 MERGE COMPLETE 🎉                       ║
╠═══════════════════════════════════════════════════════════════╣
║  Branch: {{BRANCH_NAME}}                                      ║
║  Target: main                                                 ║
║  Status: ✅ Successfully Merged                               ║
║  Date:   {{MERGE_DATE}}                                       ║
╚═══════════════════════════════════════════════════════════════╝
```
{{/if}}

{{#if IS_STALE}}
### ⚠️ STALE

> **Never merged** - No unique commits, work not implemented

| Detail | Value |
|--------|-------|
| 📋 **PR Status** | None |
| 📊 **Commits Ahead** | 0 |
| 📉 **Commits Behind** | {{COMMITS_BEHIND}} |
| ⏰ **Days Inactive** | {{DAYS_INACTIVE}} |

```
╔═══════════════════════════════════════════════════════════════╗
║                    ⚠️ STALE BRANCH ⚠️                         ║
╠═══════════════════════════════════════════════════════════════╣
║  Branch: {{BRANCH_NAME}}                                      ║
║  Status: Never implemented                                    ║
║  Action: Archive or Delete                                    ║
╚═══════════════════════════════════════════════════════════════╝
```
{{/if}}

---

## 📊 Impact Analysis

### 🎯 Impact Score: {{IMPACT_SCORE}}/100

```
Impact Breakdown
├── 🏗️ Architecture:  {{ARCH_SCORE}}/20   {{ARCH_BAR}}
├── 📝 Documentation: {{DOC_SCORE}}/20    {{DOC_BAR}}
├── ⚡ Functionality: {{FUNC_SCORE}}/25   {{FUNC_BAR}}
├── 🔒 Quality:       {{QUAL_SCORE}}/20   {{QUAL_BAR}}
└── 🆕 Freshness:     {{FRESH_SCORE}}/15  {{FRESH_BAR}}
```

### 📈 Visual Score Chart

```mermaid
pie title Impact Distribution
    "Architecture" : {{ARCH_SCORE}}
    "Documentation" : {{DOC_SCORE}}
    "Functionality" : {{FUNC_SCORE}}
    "Quality" : {{QUAL_SCORE}}
    "Freshness" : {{FRESH_SCORE}}
```

---

## 🏗️ Architecture Overview

```
{{ARCHITECTURE_DIAGRAM}}
```

---

## 🎯 Components Added

### 📊 Component Summary

| Category | Count | Components |
|----------|-------|------------|
| 🤖 **Agents** | {{AGENT_COUNT}} | {{AGENT_LIST}} |
| 🛠️ **Skills** | {{SKILL_COUNT}} | {{SKILL_LIST}} |
| 📜 **Commands** | {{COMMAND_COUNT}} | {{COMMAND_LIST}} |
| 🔧 **Scripts** | {{SCRIPT_COUNT}} | {{SCRIPT_LIST}} |
| 📚 **Docs** | {{DOC_COUNT}} | {{DOC_LIST}} |

### 🤖 Agents Detail

{{#each AGENTS}}
#### {{EMOJI}} {{NAME}}

| Attribute | Value |
|-----------|-------|
| **Purpose** | {{PURPOSE}} |
| **Type** | {{TYPE}} |
| **Tier** | {{TIER}} |
| **Skills** | {{SKILLS}} |

{{/each}}

### 🛠️ Skills Detail

{{#each SKILLS}}
#### {{EMOJI}} {{NAME}}

| Attribute | Value |
|-----------|-------|
| **Purpose** | {{PURPOSE}} |
| **Modules** | {{MODULE_COUNT}} |
| **Scripts** | {{SCRIPT_COUNT}} |
| **Category** | {{CATEGORY}} |

{{/each}}

### 📜 Commands Detail

{{#each COMMANDS}}
| Command | Purpose |
|---------|---------|
| `{{NAME}}` | {{PURPOSE}} |

{{/each}}

---

## 📈 Timeline

### 🗓️ Development Timeline

```mermaid
gantt
    title {{BRANCH_NAME}} Timeline
    dateFormat YYYY-MM-DD

    section Development
    {{GANTT_DEVELOPMENT}}

    section Testing
    {{GANTT_TESTING}}

    section Review
    {{GANTT_REVIEW}}

    section Merge
    {{GANTT_MERGE}}
```

### 📊 Commit Activity

```mermaid
xychart-beta
    title "Commit Activity Over Time"
    x-axis {{COMMIT_DATES}}
    y-axis "Commits" 0 --> {{MAX_COMMITS}}
    bar {{COMMIT_COUNTS}}
```

---

## 🔄 What Changed

### 📁 Files Modified by Category

```mermaid
pie title Files by Category
    "Agents" : {{AGENT_FILES}}
    "Skills" : {{SKILL_FILES}}
    "Commands" : {{COMMAND_FILES}}
    "Scripts" : {{SCRIPT_FILES}}
    "Docs" : {{DOC_FILES}}
    "Config" : {{CONFIG_FILES}}
```

### 🔥 Hot Files (Most Changes)

| File | Changes | Type |
|------|---------|------|
{{#each HOT_FILES}}
| `{{PATH}}` | +{{ADDITIONS}}/-{{DELETIONS}} | {{TYPE}} |
{{/each}}

---

## 🏆 Key Improvements

{{#each IMPROVEMENTS}}
### {{ORDER}}. {{EMOJI}} {{TITLE}}

| Attribute | Value |
|-----------|-------|
| **Type** | {{TYPE}} |
| **Impact** | {{IMPACT}} |
| **Description** | {{DESCRIPTION}} |

{{#if BEFORE_AFTER}}
**Before → After:**
```
{{BEFORE}} → {{AFTER}}
```
{{/if}}

{{/each}}

---

## 🚀 Next Steps

{{#if IS_MERGED}}
### ✅ Branch Cleanup (Merged)

Since this branch has been **successfully merged**, you can safely delete it:

#### 🗑️ Delete Local Branch
```bash
git branch -d {{BRANCH_NAME}}
```

#### 🗑️ Delete Remote Branch
```bash
git push origin --delete {{BRANCH_NAME}}
```

#### ✅ Verify Merge
```bash
git log main --grep="{{SEARCH_TERM}}" --oneline
```

#### 📦 Archive README
```bash
mv .moai/docs/branches/{{README_FILENAME}} \
   .moai/docs/branches/archive/
```
{{/if}}

{{#if IS_STALE}}
### ⚠️ Stale Branch Options

| Option | Action | When to Choose |
|--------|--------|----------------|
| 🗑️ **Delete** | Remove branch entirely | No unique value |
| 🔄 **Rebase** | Update from main and continue | Want to resume work |
| 📦 **Archive** | Keep README, delete branch | Historical reference |

#### Option A: Delete (Recommended)
```bash
git branch -D {{BRANCH_NAME}}
git push origin --delete {{BRANCH_NAME}} 2>/dev/null || true
```

#### Option B: Rebase and Continue
```bash
git checkout main && git pull
git checkout {{BRANCH_NAME}}
git rebase main
```
{{/if}}

---

## 📚 Related Documentation

| Document | Description |
|----------|-------------|
| [Branch Index](./index.md) | Overview of all branches |
| [README Rules](../../.claude/skills/builder/collector-readme/modules/readme-rules.md) | Generation guidelines |
| [Quality Gates](../../.claude/skills/builder/collector-readme/modules/quality-gates.md) | Validation criteria |

---

## 📊 Quality Metrics

### 🎯 Compliance Score

```
Quality Gate Results
├── ✅ Structure:    PASS  (Has all required sections)
├── ✅ Visual:       PASS  (Charts and diagrams included)
├── ✅ Content:      PASS  (Comprehensive documentation)
└── ✅ Navigation:   PASS  (Quick links functional)

Overall: {{QUALITY_SCORE}}/100
```

### 📈 Score Evolution

| Date | Score | Change | Notes |
|------|-------|--------|-------|
{{#each SCORE_HISTORY}}
| {{DATE}} | {{SCORE}} | {{DELTA}} | {{NOTES}} |
{{/each}}

---

<div align="center">

**Generated**: {{GENERATED_AT}}
**Format Version**: 2.0
**Quality Score**: {{QUALITY_SCORE}}/100
**Collector**: moai-flow-branch-collector v2.0

---

*🤖 Generated by MoAI Flow Collector System*

</div>
```

---

## 🎨 Visual Component Library

### Status Badges

| Status | Emoji | Color | Badge |
|--------|-------|-------|-------|
| MERGED | ✅ | green | `[![Status](https://img.shields.io/badge/Status-MERGED-success)]()` |
| ACTIVE | 🔄 | blue | `[![Status](https://img.shields.io/badge/Status-ACTIVE-blue)]()` |
| STALE | ⚠️ | yellow | `[![Status](https://img.shields.io/badge/Status-STALE-yellow)]()` |
| PR_OPEN | 📋 | orange | `[![Status](https://img.shields.io/badge/Status-PR_OPEN-orange)]()` |

### Tier Badges

| Tier | Emoji | Color | Label |
|------|-------|-------|-------|
| 1 | 🔴 | red | Critical |
| 2 | 🟠 | orange | Important |
| 3 | 🟡 | yellow | Standard |
| 4 | ⚪ | gray | Stale |

### Progress Bars

```
Full:    ████████████████████ 100%
High:    ████████████████░░░░  80%
Medium:  ████████████░░░░░░░░  60%
Low:     ████████░░░░░░░░░░░░  40%
None:    ████░░░░░░░░░░░░░░░░  20%
```

### Category Emojis

| Category | Emoji | Example |
|----------|-------|---------|
| Agent | 🤖 | `🤖 expert-backend` |
| Skill | 🛠️ | `🛠️ moai-foundation-core` |
| Command | 📜 | `📜 /moai:1-plan` |
| Script | 🔧 | `🔧 branch_status.py` |
| Workflow | 🔄 | `🔄 readme-generation.toon` |
| Hook | 🪝 | `🪝 session_start` |
| Config | ⚙️ | `⚙️ settings.json` |
| Docs | 📚 | `📚 README.md` |

---

## 🏗️ Architecture Diagram Templates

### Simple Architecture

```
┌─────────────────────────────────────────────┐
│                 {{PROJECT}}                  │
├─────────────────────────────────────────────┤
│  ┌─────────┐  ┌─────────┐  ┌─────────┐     │
│  │ Agent 1 │  │ Agent 2 │  │ Agent 3 │     │
│  └────┬────┘  └────┬────┘  └────┬────┘     │
│       │            │            │           │
│       └────────────┼────────────┘           │
│                    ▼                        │
│              ┌──────────┐                   │
│              │   Core   │                   │
│              └──────────┘                   │
└─────────────────────────────────────────────┘
```

### Complex Architecture

```
╔═══════════════════════════════════════════════════════════════════╗
║                     🏗️ {{PROJECT}} Architecture                   ║
╠═══════════════════════════════════════════════════════════════════╣
║                                                                   ║
║  ┌─────────────────────────────────────────────────────────────┐  ║
║  │                    🎯 ORCHESTRATION LAYER                    │  ║
║  │  ┌───────────┐  ┌───────────┐  ┌───────────┐              │  ║
║  │  │  Coord 1  │  │  Coord 2  │  │  Coord 3  │              │  ║
║  │  └─────┬─────┘  └─────┬─────┘  └─────┬─────┘              │  ║
║  └────────┼──────────────┼──────────────┼────────────────────┘  ║
║           │              │              │                        ║
║           ▼              ▼              ▼                        ║
║  ┌─────────────────────────────────────────────────────────────┐  ║
║  │                    🛠️ EXECUTION LAYER                        │  ║
║  │  ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐        │  ║
║  │  │ A1 │ │ A2 │ │ A3 │ │ A4 │ │ A5 │ │ A6 │ │ A7 │        │  ║
║  │  └────┘ └────┘ └────┘ └────┘ └────┘ └────┘ └────┘        │  ║
║  └─────────────────────────────────────────────────────────────┘  ║
║           │              │              │                        ║
║           ▼              ▼              ▼                        ║
║  ┌─────────────────────────────────────────────────────────────┐  ║
║  │                    💾 PERSISTENCE LAYER                       │  ║
║  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐       │  ║
║  │  │ Memory  │  │  State  │  │  Logs   │  │ Config  │       │  ║
║  │  └─────────┘  └─────────┘  └─────────┘  └─────────┘       │  ║
║  └─────────────────────────────────────────────────────────────┘  ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
```

### Flow Diagram

```
┌─────┐    ┌─────┐    ┌─────┐    ┌─────┐    ┌─────┐
│ 1️⃣  │───▶│ 2️⃣  │───▶│ 3️⃣  │───▶│ 4️⃣  │───▶│ 5️⃣  │
│Init │    │Scan │    │Learn│    │Merge│    │Done │
└─────┘    └─────┘    └─────┘    └─────┘    └─────┘
```

---

## 📋 Checklist Generator

### Pre-Merge Checklist

```markdown
## ✅ Pre-Merge Checklist

### Code Quality
- [ ] All tests passing
- [ ] Code review approved
- [ ] No security vulnerabilities
- [ ] Documentation updated

### Integration
- [ ] CI/CD pipeline green
- [ ] No merge conflicts
- [ ] Dependencies updated
- [ ] Breaking changes documented

### Documentation
- [ ] README updated
- [ ] CHANGELOG entry added
- [ ] API docs current
- [ ] Migration guide (if needed)
```

### Post-Merge Checklist

```markdown
## ✅ Post-Merge Checklist

- [ ] Local branch deleted
- [ ] Remote branch deleted (if applicable)
- [ ] README archived
- [ ] Changelog updated
- [ ] Team notified
```

---

## 🔧 Template Variables Reference

### Core Variables

| Variable | Type | Description |
|----------|------|-------------|
| `BRANCH_NAME` | string | Full branch name |
| `STATUS` | enum | MERGED, ACTIVE, STALE, PR_OPEN |
| `TIER` | int | 1-4 tier classification |
| `SCORE` | int | Quality score 0-100 |
| `DESCRIPTION` | string | Brief description |

### Dates

| Variable | Format | Description |
|----------|--------|-------------|
| `CREATED_DATE` | YYYY-MM-DD | Branch creation date |
| `UPDATED_DATE` | YYYY-MM-DD | Last update date |
| `MERGE_DATE` | YYYY-MM-DD | Merge date (if merged) |
| `GENERATED_AT` | ISO 8601 | README generation timestamp |

### Statistics

| Variable | Type | Description |
|----------|------|-------------|
| `COMMIT_COUNT` | int | Total commits |
| `FILES_CHANGED` | int | Files modified |
| `LINES_ADDED` | int | Lines added |
| `LINES_DELETED` | int | Lines removed |
| `CONTRIBUTORS` | int | Number of contributors |

### Component Counts

| Variable | Type | Description |
|----------|------|-------------|
| `AGENT_COUNT` | int | Agents added |
| `SKILL_COUNT` | int | Skills added |
| `COMMAND_COUNT` | int | Commands added |
| `SCRIPT_COUNT` | int | Scripts added |
| `DOC_COUNT` | int | Docs added |

---

**Version**: 2.0.0 | **Style**: Modern 2025 | **Last Updated**: 2025-12-04
