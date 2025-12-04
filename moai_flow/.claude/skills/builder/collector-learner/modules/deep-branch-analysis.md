# 🔬 Deep Branch Analysis Module

**Comprehensive branch learning with git history, file diffs, and pattern extraction**

> **Version**: 2.0.0
> **Status**: Production Ready
> **Part of**: collector-learner skill

---

## 📋 Overview

This module enables **deep learning** of branch content through:

| Analysis Type | Description | Output |
|--------------|-------------|--------|
| 🔍 **Git History** | Full commit analysis with messages, authors, dates | Timeline data |
| 📁 **File Changes** | Complete file diff analysis with additions/deletions | Change matrix |
| 🏗️ **Component Detection** | Automatic identification of agents, skills, commands | Component catalog |
| 📊 **Impact Scoring** | Multi-dimensional scoring based on change patterns | Score breakdown |
| 🎯 **Pattern Extraction** | Reusable patterns identified from changes | Pattern catalog |

---

## 🔍 Git History Analysis

### Commit Analysis Schema

```python
def analyze_commits(branch: str) -> CommitAnalysis:
    """
    Deep analyze all commits in a branch.

    Returns:
        CommitAnalysis with:
        - commit_count: Total commits
        - authors: List of contributors
        - date_range: First to last commit dates
        - velocity: Commits per day/week
        - commit_types: Distribution of feat/fix/docs/etc
        - hot_files: Most frequently modified files
    """
```

### Commit Type Classification

| Type | Pattern | Weight |
|------|---------|--------|
| 🆕 **feat** | `feat:`, `feature:`, `add:` | High |
| 🐛 **fix** | `fix:`, `bug:`, `resolve:` | Medium |
| 📚 **docs** | `docs:`, `doc:`, `readme:` | Medium |
| 🔧 **chore** | `chore:`, `build:`, `ci:` | Low |
| ♻️ **refactor** | `refactor:`, `restructure:` | Medium |
| 🧪 **test** | `test:`, `tests:` | Medium |
| 🎨 **style** | `style:`, `format:` | Low |

### Velocity Metrics

```
Commit Velocity Analysis
├── 📅 Daily average: {{DAILY_AVG}} commits/day
├── 📆 Weekly average: {{WEEKLY_AVG}} commits/week
├── 🔥 Peak day: {{PEAK_DATE}} ({{PEAK_COUNT}} commits)
└── 📊 Activity pattern: {{PATTERN}} (burst/steady/tapering)
```

---

## 📁 File Change Analysis

### Change Matrix

| Metric | Calculation | Meaning |
|--------|-------------|---------|
| **Churn** | additions + deletions | Total code movement |
| **Net Growth** | additions - deletions | Code size change |
| **Touch Count** | unique files modified | Spread of changes |
| **Depth** | max directory depth touched | Architecture impact |

### File Classification

```python
def classify_files(changes: List[FileChange]) -> FileClassification:
    """
    Classify changed files by type and category.

    Categories:
    - agents/: Agent definitions (.md)
    - skills/: Skill definitions (SKILL.md + modules/)
    - commands/: Slash command definitions (.md)
    - scripts/: Automation scripts (.py, .sh)
    - workflows/: TOON workflow files (.toon)
    - docs/: Documentation files (.md)
    - config/: Configuration files (.json, .yaml)
    """
```

### Hot File Detection

```
🔥 Hot Files (Most Changed)
├── 1. {{FILE_1}} (+{{ADD_1}}/-{{DEL_1}}) {{TYPE_1}}
├── 2. {{FILE_2}} (+{{ADD_2}}/-{{DEL_2}}) {{TYPE_2}}
├── 3. {{FILE_3}} (+{{ADD_3}}/-{{DEL_3}}) {{TYPE_3}}
└── ... (top 10)
```

---

## 🏗️ Component Detection

### Auto-Detection Rules

| Component | Detection Pattern | Validation |
|-----------|------------------|------------|
| 🤖 **Agent** | `.claude/agents/*.md` with YAML frontmatter | Has `name:`, `description:` |
| 🛠️ **Skill** | `.claude/skills/*/SKILL.md` | Has `name:`, `modularized:` |
| 📜 **Command** | `.claude/commands/*.md` | Has `description:`, `arguments:` |
| 🔧 **Script** | `scripts/*.py` or `scripts/*.sh` | Executable file |
| 🔄 **Workflow** | `workflows/*.toon` | TOON format |
| 🪝 **Hook** | `.claude/hooks/*.py` | Has hook pattern |

### Component Schema

```json
{
  "component": {
    "type": "skill",
    "name": "collector-readme",
    "path": ".claude/skills/builder/collector-readme/",
    "version": "2.0.0",
    "modules": 9,
    "scripts": 1,
    "workflows": 1,
    "dependencies": ["collector-learner", "collector-scan"],
    "tier": 2
  }
}
```

---

## 📊 Impact Scoring

### Multi-Dimensional Scoring

| Dimension | Weight | Criteria |
|-----------|--------|----------|
| 🏗️ **Architecture** | 20% | New components, structural changes |
| 📚 **Documentation** | 20% | README coverage, examples, guides |
| ⚡ **Functionality** | 25% | Features, edge cases, robustness |
| 🔒 **Quality** | 20% | TRUST-5 compliance, best practices |
| 🆕 **Freshness** | 15% | Recency, active maintenance |

### Score Calculation

```python
def calculate_impact_score(analysis: BranchAnalysis) -> ImpactScore:
    """
    Calculate comprehensive impact score.

    Returns score breakdown:
    - architecture_score: 0-20
    - documentation_score: 0-20
    - functionality_score: 0-25
    - quality_score: 0-20
    - freshness_score: 0-15
    - total_score: 0-100
    """

    arch_score = (
        new_components * 3 +
        structural_changes * 2 +
        integration_points * 1
    )

    doc_score = (
        readme_coverage * 0.4 +
        example_count * 0.3 +
        module_docs * 0.3
    )

    func_score = (
        feature_count * 3 +
        edge_case_handling * 2 +
        error_handling * 1
    )

    quality_score = (
        trust5_compliance * 0.5 +
        naming_consistency * 0.2 +
        security_check * 0.3
    )

    fresh_score = (
        days_since_update_penalty +
        active_maintenance_bonus +
        ci_status_modifier
    )

    return ImpactScore(
        architecture=min(arch_score, 20),
        documentation=min(doc_score, 20),
        functionality=min(func_score, 25),
        quality=min(quality_score, 20),
        freshness=min(fresh_score, 15)
    )
```

### Visual Score Representation

```
Impact Score: 91/100 ████████████████████░ EXCELLENT

Breakdown:
├── 🏗️ Architecture:  18/20  █████████░
├── 📚 Documentation: 17/20  ████████░░
├── ⚡ Functionality: 23/25  █████████░
├── 🔒 Quality:       19/20  █████████░
└── 🆕 Freshness:     14/15  █████████░
```

---

## 🎯 Pattern Extraction

### Pattern Categories

| Category | Examples | Reusability |
|----------|----------|-------------|
| 📁 **Structure** | Module nesting, file organization | Cross-project |
| 📝 **Documentation** | Progressive disclosure, examples | Cross-skill |
| 🔄 **Integration** | Works Well With, dependencies | Same domain |
| 🔒 **Quality** | TRUST-5 checklist, validation | Universal |

### Pattern Schema

```json
{
  "pattern": {
    "id": "progressive-disclosure",
    "name": "Progressive Disclosure",
    "category": "documentation",
    "source_component": "moai-foundation-core",
    "description": "Layer information from simple to complex",
    "applicability": [
      "all skills",
      "complex documentation"
    ],
    "example": "Level 1 → Level 2 → Level 3 sections",
    "reusability_score": 95
  }
}
```

---

## 📋 Analysis Output Format

### Complete Analysis Report

```json
{
  "branch_analysis": {
    "branch": "feature/moai-flow-system",
    "analyzed_at": "2025-12-04T00:00:00Z",
    "analyzer": "collector-learner v4.0.0",

    "git_history": {
      "commit_count": 28,
      "authors": ["rdmptv"],
      "date_range": {
        "first": "2025-11-15",
        "last": "2025-12-02"
      },
      "velocity": {
        "daily_avg": 1.5,
        "weekly_avg": 10.5
      },
      "commit_types": {
        "feat": 15,
        "docs": 8,
        "fix": 3,
        "chore": 2
      }
    },

    "file_changes": {
      "files_changed": 28,
      "additions": 6837,
      "deletions": 0,
      "churn": 6837,
      "hot_files": [
        {"path": "SKILL.md", "changes": 450, "type": "skill"}
      ]
    },

    "components": {
      "agents": [
        {"name": "moai-flow", "type": "coordinator"}
      ],
      "skills": [
        {"name": "moai-flow-collector", "modules": 5},
        {"name": "moai-flow-learner", "modules": 4}
      ],
      "commands": [
        {"name": "/moai-flow:compare"},
        {"name": "/moai-flow:learn"}
      ]
    },

    "impact_score": {
      "total": 88,
      "architecture": 18,
      "documentation": 17,
      "functionality": 22,
      "quality": 18,
      "freshness": 13
    },

    "patterns_extracted": [
      "modular-skill-structure",
      "toon-workflow-integration"
    ]
  }
}
```

---

## 🔧 Integration

### With Other Collector Skills

| Skill | Integration | Data Flow |
|-------|-------------|-----------|
| **collector-scan** | Provides raw branch data | scan → learner |
| **collector-readme** | Consumes analysis for README | learner → readme |
| **collector-merge** | Uses scores for merge decisions | learner → merge |

### Commands

```bash
# Analyze single branch
/collector:learn feature/moai-flow-system

# Analyze all branches
/collector:learn --all

# Generate comparison matrix
/collector:learn --compare main feature/*
```

---

**Version**: 2.0.0 | **Status**: Production Ready | **Last Updated**: 2025-12-04
