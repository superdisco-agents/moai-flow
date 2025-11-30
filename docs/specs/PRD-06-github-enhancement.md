# PRD-06: GitHub Enhancement

> Expand GitHub integration with specialized agents

## Overview

| Field | Value |
|-------|-------|
| **Priority** | P2 (Important) |
| **Effort** | Medium (4-6 weeks) |
| **Impact** | Medium |
| **Type** | Agent Enhancement |

---

## Problem Statement

MoAI-Flow has 9 specialized GitHub agents. MoAI has 1 (manager-git) plus basic GitHub MCP. This limits automation for PR workflows, issue management, and repository analysis.

### Current MoAI GitHub Capabilities

```
CURRENT:

manager-git
├── Branch operations
├── Commit operations
├── Basic PR creation
└── Git commands via Bash

GitHub MCP (basic)
├── create-or-update-file
└── push-files
```

### MoAI-Flow GitHub Capabilities

```
MOAI-FLOW:

9 Specialized Agents:
├── github_actions     - Workflow management
├── github_issues      - Issue management
├── github_pr          - PR handling
├── repo_analyzer      - Repository analysis
├── commit_historian   - Commit analysis
├── branch_manager     - Branch operations
├── release_manager    - Release management
├── dependabot_handler - Dependency updates
└── security_scanner   - Security analysis

GitHub MCP Tools:
├── repo_analyze
├── pr_enhance
├── issue_triage
├── code_review
└── github_swarm
```

---

## Solution

### Phase 1: PR Enhancement Agent (Week 1-2)

Create `expert-github-pr` agent:

```yaml
# .claude/agents/moai/expert-github-pr.yml
name: expert-github-pr
description: |
  Pull request specialist. Creates PRs with detailed descriptions,
  auto-labels, and reviewer suggestions.

model: sonnet

tools:
  - Bash
  - Read
  - Write
  - Edit
  - Glob
  - Grep

skills:
  - moai-github-pr

capabilities:
  - Generate PR descriptions from changes
  - Auto-assign labels based on files changed
  - Suggest reviewers based on code ownership
  - Create testing checklists
  - Generate changelogs
```

**Skill: moai-github-pr**

```markdown
# GitHub PR Skill

## PR Creation Pattern

1. Analyze changes:
   ```bash
   git diff main...HEAD
   git log main..HEAD --oneline
   ```

2. Generate description:
   - Summary of changes
   - Type: feature/fix/refactor/docs
   - Impact analysis
   - Testing notes

3. Determine labels:
   - By file paths (src/api/* → api)
   - By change type (fix → bug)
   - By scope (tests/* → testing)

4. Create PR:
   ```bash
   gh pr create \
     --title "Type: Brief description" \
     --body "$(cat description.md)" \
     --label "label1,label2"
   ```
```

### Phase 2: Issue Management Agent (Week 3-4)

Create `expert-github-issues` agent:

```yaml
# .claude/agents/moai/expert-github-issues.yml
name: expert-github-issues
description: |
  Issue management specialist. Triages, labels, and manages issues.

model: haiku

tools:
  - Bash
  - Read

capabilities:
  - Triage open issues
  - Auto-label based on content
  - Suggest assignees
  - Link related issues
  - Track issue metrics
```

### Phase 3: Repository Analysis Agent (Week 5-6)

Create `expert-github-repo` agent:

```yaml
# .claude/agents/moai/expert-github-repo.yml
name: expert-github-repo
description: |
  Repository analysis specialist. Analyzes structure, complexity,
  and health metrics.

model: sonnet

tools:
  - Bash
  - Read
  - Glob
  - Grep

capabilities:
  - Analyze repository structure
  - Calculate complexity metrics
  - Identify hotspots
  - Check dependency health
  - Generate repository reports
```

---

## Technical Specification

### PR Description Template

```markdown
## Summary
<!-- Auto-generated summary of changes -->

## Type
- [ ] Feature
- [ ] Bug Fix
- [ ] Refactor
- [ ] Documentation
- [ ] Other

## Changes
<!-- File-by-file summary -->

## Testing
<!-- Testing notes and checklist -->

## Screenshots
<!-- If applicable -->

## Related Issues
<!-- Linked issues -->
```

### Label Mapping Rules

```json
{
  "label_rules": {
    "by_path": {
      "src/api/**": "api",
      "src/ui/**": "frontend",
      "tests/**": "testing",
      "docs/**": "documentation"
    },
    "by_commit_prefix": {
      "feat": "enhancement",
      "fix": "bug",
      "docs": "documentation",
      "refactor": "refactor",
      "test": "testing"
    },
    "by_size": {
      "small": { "max_lines": 50 },
      "medium": { "max_lines": 200 },
      "large": { "min_lines": 200 }
    }
  }
}
```

### Issue Triage Rules

```json
{
  "triage_rules": {
    "by_keywords": {
      "crash|error|exception": "bug",
      "feature|request|want": "enhancement",
      "question|how to|help": "question",
      "security|vulnerability": "security"
    },
    "priority_keywords": {
      "urgent|critical|blocker": "priority:high",
      "important": "priority:medium"
    },
    "assignment_rules": {
      "api": ["backend-team"],
      "ui": ["frontend-team"],
      "security": ["security-team"]
    }
  }
}
```

---

## Configuration

### Add to config.json

```json
{
  "github": {
    "pr_automation": {
      "enabled": true,
      "auto_description": true,
      "auto_labels": true,
      "suggest_reviewers": true,
      "template": ".github/PULL_REQUEST_TEMPLATE.md"
    },
    "issue_management": {
      "enabled": true,
      "auto_triage": false,
      "label_rules": ".moai/config/github-labels.json",
      "assign_rules": ".moai/config/github-assign.json"
    },
    "repository_analysis": {
      "enabled": true,
      "report_location": ".moai/reports/repo/"
    }
  }
}
```

---

## Implementation Plan

### Week 1-2: PR Agent

1. Create `expert-github-pr.yml`
2. Create `moai-github-pr` skill
3. Implement description generation
4. Implement label assignment
5. Test with sample PRs

### Week 3-4: Issue Agent

1. Create `expert-github-issues.yml`
2. Create `moai-github-issues` skill
3. Implement triage logic
4. Implement labeling rules
5. Test with sample issues

### Week 5-6: Repo Analysis Agent

1. Create `expert-github-repo.yml`
2. Create `moai-github-repo` skill
3. Implement analysis scripts
4. Generate sample reports
5. Integration testing

---

## Acceptance Criteria

### Phase 1 (PR Agent)
- [ ] Agent creates PRs with detailed descriptions
- [ ] Auto-labeling works based on rules
- [ ] Reviewer suggestions generated
- [ ] Testing checklist included

### Phase 2 (Issue Agent)
- [ ] Issues can be triaged
- [ ] Labels assigned correctly
- [ ] Assignees suggested

### Phase 3 (Repo Analysis)
- [ ] Repository structure analyzed
- [ ] Complexity metrics calculated
- [ ] Reports generated

---

## Impact Assessment

### Capability Gain

| Feature | Before | After |
|---------|--------|-------|
| PR descriptions | Manual | Auto-generated |
| PR labeling | Manual | Automatic |
| Issue triage | Manual | Semi-automatic |
| Repo analysis | None | Full reports |

### Developer Productivity

- Estimated 30-50% time savings on PR creation
- Faster issue triage
- Better repository insights

---

## Success Metrics

| Metric | Target |
|--------|--------|
| PR description quality | User satisfaction > 80% |
| Label accuracy | > 90% |
| Issue triage accuracy | > 85% |
| Agent adoption | 40% of users |

---

## Related Documents

- [GitHub Integration](../integration/01-github-integration.md)
- [MoAI-Flow GitHub Agents](../agents/06-github-repository.md)
- [PRD-00 Overview](PRD-00-overview.md)

---

## Timeline

```
Week 1-2: PR Agent
Week 3-4: Issue Agent
Week 5-6: Repo Analysis Agent

Total: 6 weeks
```
