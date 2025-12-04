---
name: collector-orchestrator
description: TOON workflow definitions for the collector-orchestrator agent
version: 1.0.0
modularized: true
tier: 3
category: builder
last_updated: 2025-12-04
compliance_score: 95
auto_trigger_keywords:
  - collector workflow
  - branch review workflow
  - github sync workflow
color: rainbow
---

# Collector Orchestrator Skill

**TOON workflow definitions for intelligent workspace consolidation**

> **Version**: 1.0.0
> **Status**: Production Ready
> **Part of**: MoAI Collector System

---

## Purpose

This skill contains **TOON workflow definitions** used by the `collector-orchestrator` agent. Workflows define step-by-step execution paths for complex multi-agent operations.

**Note**: The agent definition is at `.claude/agents/moai/moai-builder/collector-orchestrator.md`. This skill provides the supporting workflow files.

---

## Workflows

| Workflow | Description | Steps |
|----------|-------------|-------|
| `github-sync` | Synchronize local workspace with GitHub remote | 5 steps |
| `branch-review` | Comprehensive branch analysis and README generation | 4 steps |

---

## Workflow: github-sync

**Full pipeline for workspace consolidation**

```
Step 1: Scan     → Compare local vs GitHub
Step 2: Learn    → Score improvements with AI
Step 3: Decide   → User approves changes
Step 4: Merge    → Apply improvements
Step 5: Publish  → Create PR on GitHub
```

### Files
- `workflows/github-sync/WORKFLOW.toon` - Visual workflow definition
- `workflows/github-sync/instructions.md` - Detailed instructions
- `workflows/github-sync/steps/step-01-scan.md`
- `workflows/github-sync/steps/step-02-learn.md`
- `workflows/github-sync/steps/step-03-decide.md`
- `workflows/github-sync/steps/step-04-merge.md`
- `workflows/github-sync/steps/step-05-publish.md`

---

## Workflow: branch-review

**Generate comprehensive branch documentation**

```
Step 1: Fetch    → Get branch information
Step 2: Analyze  → Analyze branch contents
Step 3: Generate → Create README documentation
Step 4: Report   → Output final report
```

### Files
- `workflows/branch-review/WORKFLOW.toon` - Visual workflow definition
- `workflows/branch-review/instructions.md` - Detailed instructions
- `workflows/branch-review/steps/step-01-fetch.md`
- `workflows/branch-review/steps/step-02-analyze.md`
- `workflows/branch-review/steps/step-03-generate-readme.md`
- `workflows/branch-review/steps/step-04-report.md`

---

## Related Components

| Type | Name | Description |
|------|------|-------------|
| Agent | `collector-orchestrator.md` | Main orchestrator agent |
| Skill | `collector-scan` | Workspace scanning |
| Skill | `collector-learner` | AI-powered analysis |
| Skill | `collector-merge` | Intelligent consolidation |
| Skill | `collector-publish` | GitHub publishing |
| Command | `collector:github-sync` | Trigger github-sync workflow |
| Command | `collector:branch-status` | Trigger branch-review workflow |

---

## Structure Compliance

This skill was created to maintain proper Claude Code structure:

| Location | Content Type |
|----------|-------------|
| `.claude/agents/` | **Markdown files ONLY** |
| `.claude/skills/` | **Markdown + modules/ + workflows/** |

Workflows MUST be in skills, NOT in agents.

---

**Version**: 1.0.0 | **Last Updated**: 2025-12-04
