# GitHub Integration

> Deep GitHub integration for repository management

## Overview

MoAI-Flow includes extensive GitHub integration with 9 specialized agents and dedicated MCP tools. **MoAI has basic GitHub support** through the standard GitHub MCP server.

---

## MoAI-Flow GitHub Agents

### Agent Catalog (9 Agents)

| Agent | Purpose |
|-------|---------|
| `github_actions` | Workflow management |
| `github_issues` | Issue management |
| `github_pr` | Pull request handling |
| `repo_analyzer` | Repository analysis |
| `commit_historian` | Commit analysis |
| `branch_manager` | Branch operations |
| `release_manager` | Release management |
| `dependabot_handler` | Dependency updates |
| `security_scanner` | Security analysis |

### Agent Capabilities

```
┌─────────────────────────────────────────────────────────┐
│              GITHUB AGENT ECOSYSTEM                     │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Repository Analysis:                                   │
│  ├── repo_analyzer     - Structure, complexity         │
│  ├── commit_historian  - History, patterns             │
│  └── security_scanner  - Vulnerabilities               │
│                                                         │
│  Development Workflow:                                  │
│  ├── github_pr        - Create, review, merge PRs      │
│  ├── github_issues    - Create, triage, close issues   │
│  └── branch_manager   - Create, protect, cleanup       │
│                                                         │
│  Automation:                                            │
│  ├── github_actions   - CI/CD workflows                │
│  ├── release_manager  - Version, changelog, publish    │
│  └── dependabot_handler - Dependency updates           │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## GitHub MCP Tools

### Repository Analysis

```javascript
mcp__moai-flow__repo_analyze {
  repo: "owner/repo",
  analysis: ["structure", "complexity", "dependencies", "activity"]
}

// Returns:
{
  "repo": "owner/repo",
  "structure": {
    "languages": {"Python": 65, "TypeScript": 30, "Other": 5},
    "files": 234,
    "directories": 45
  },
  "complexity": {
    "score": 7.2,
    "hotspots": ["src/core/engine.py", "src/api/handlers.ts"]
  },
  "dependencies": {
    "total": 45,
    "outdated": 3,
    "vulnerable": 1
  },
  "activity": {
    "commits_30d": 87,
    "contributors": 5,
    "open_prs": 3,
    "open_issues": 12
  }
}
```

### Pull Request Enhancement

```javascript
mcp__moai-flow__pr_enhance {
  pr: 123,
  enhancements: ["description", "labels", "reviewers", "checklist"]
}

// Actions:
// - Generate detailed description from changes
// - Auto-assign labels based on files changed
// - Suggest reviewers based on code ownership
// - Create testing checklist
```

### Issue Triage

```javascript
mcp__moai-flow__issue_triage {
  repo: "owner/repo",
  labels: ["bug", "feature", "enhancement"],
  assignRules: {
    "bug": ["developer-1", "developer-2"],
    "feature": ["product-owner"],
    "enhancement": ["any"]
  }
}
```

### Code Review

```javascript
mcp__moai-flow__code_review {
  pr: 123,
  reviewType: "comprehensive",
  focus: ["security", "performance", "style", "tests"]
}

// Returns detailed review with:
// - Security issues
// - Performance concerns
// - Style violations
// - Test coverage gaps
// - Suggested improvements
```

### GitHub Swarm

```javascript
mcp__moai-flow__github_swarm {
  repo: "owner/repo",
  task: "implement_feature",
  featureSpec: "Add user authentication with OAuth2",
  agents: ["repo_analyzer", "github_pr", "github_actions"]
}
```

---

## MoAI GitHub Current State

### GitHub MCP Server

MoAI uses standard GitHub MCP:

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "..."
      }
    }
  }
}
```

### Available Tools

MoAI GitHub tools:

| Tool | Purpose |
|------|---------|
| `create-or-update-file` | File operations |
| `push-files` | Push multiple files |

### Git Strategy Configuration

MoAI has Git strategy in config:

```json
{
  "git_strategy": {
    "mode": "manual",
    "environment": "local",
    "github_integration": false,
    "automation": {
      "auto_branch": false,
      "auto_commit": true,
      "auto_pr": false,
      "auto_push": false
    }
  }
}
```

### manager-git Agent

MoAI has one Git-focused agent:

```yaml
name: manager-git
description: Git operations, branching, PR management
tools:
  - Bash (git commands)
  - Read, Write, Edit
  - Glob, Grep
```

---

## Gap Analysis

| Feature | MoAI-Flow | MoAI |
|---------|-------------|------|
| GitHub Agents | 9 specialized | 1 (manager-git) |
| Repository Analysis | Deep analysis | Basic |
| PR Enhancement | Auto-generate | Manual |
| Issue Triage | Automatic | Manual |
| Code Review Agent | Yes | No |
| Security Scanning | Yes | No |
| Release Management | Yes | Manual |
| GitHub Actions | Workflow management | None |
| Dependabot | Handler agent | None |

---

## MoAI GitHub Enhancement Options

### Option 1: Add MoAI-Flow GitHub Tools

```json
{
  "mcpServers": {
    "moai-flow": {
      "command": "npx",
      "args": ["-y", "moai-flow@alpha", "mcp", "start"]
    }
  }
}
```

Access MoAI-Flow's GitHub tools alongside MoAI.

### Option 2: Create Specialized GitHub Agents

Add MoAI-native GitHub agents:

```yaml
# .claude/agents/moai/expert-github-pr.yml
name: expert-github-pr
description: Pull request specialist
tools:
  - Bash (gh commands)
  - Read, Write, Edit

capabilities:
  - Create PRs with detailed descriptions
  - Auto-label based on changes
  - Suggest reviewers
  - Generate changelogs
```

### Option 3: Enhance manager-git

Expand existing manager-git capabilities:

```yaml
name: manager-git
description: Comprehensive Git and GitHub operations

capabilities:
  - Basic: branch, commit, push, pull
  - PR: create, review, merge
  - Issues: create, label, assign
  - Analysis: repo structure, commit history
  - Automation: release, changelog
```

---

## Proposed MoAI GitHub Enhancement

### New Agents

```yaml
# expert-github-pr.yml
name: expert-github-pr
description: Pull request automation
skills:
  - moai-github-pr

# expert-github-issues.yml
name: expert-github-issues
description: Issue management
skills:
  - moai-github-issues

# expert-github-security.yml
name: expert-github-security
description: Security scanning
skills:
  - moai-github-security
```

### Enhanced Configuration

```json
{
  "github": {
    "pr_automation": {
      "auto_description": true,
      "auto_labels": true,
      "suggest_reviewers": true,
      "template": ".github/PULL_REQUEST_TEMPLATE.md"
    },
    "issue_management": {
      "auto_triage": false,
      "label_rules": {},
      "assign_rules": {}
    },
    "security": {
      "scan_on_pr": false,
      "vulnerability_alerts": true
    }
  }
}
```

### GitHub Commands

```bash
# MoAI GitHub commands
/moai:github-pr create       # Create PR with AI description
/moai:github-pr review 123   # AI code review
/moai:github-issue triage    # Triage open issues
/moai:github-release         # Create release with changelog
```

---

## Implementation Roadmap

### Phase 1: PR Enhancement (Week 1-2)

1. Create `expert-github-pr` agent
2. Auto-generate PR descriptions
3. Add PR templates

### Phase 2: Issue Management (Week 3-4)

1. Create `expert-github-issues` agent
2. Issue labeling rules
3. Assignment automation

### Phase 3: Security & Analysis (Month 2)

1. Create `expert-github-security` agent
2. Vulnerability scanning integration
3. Repository analysis tools

### Phase 4: Automation (Month 3)

1. Release management automation
2. GitHub Actions integration
3. Dependabot handling

---

## Recommendation

### Priority: P2 (Medium)

GitHub enhancement improves developer workflow.

### Immediate (No Development)

Use `gh` CLI through manager-git:

```bash
# manager-git can use gh CLI
gh pr create --title "Feature" --body "Description"
gh issue create --title "Bug" --body "Details"
gh release create v1.0.0 --notes "Release notes"
```

### Short-term (1 month)

Create `expert-github-pr` agent for PR automation.

### Long-term (3+ months)

Full GitHub agent ecosystem matching MoAI-Flow.

---

## Summary

MoAI-Flow has comprehensive GitHub integration with 9 specialized agents. MoAI has basic GitHub support through the standard MCP server and manager-git agent. Adding PR automation would be the highest-impact improvement. Full GitHub agent ecosystem is a larger undertaking but would significantly enhance MoAI's GitHub capabilities.
