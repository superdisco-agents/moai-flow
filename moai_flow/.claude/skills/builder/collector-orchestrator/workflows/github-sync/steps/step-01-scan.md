# Step 01: Scan Repositories

## Overview
Scan both local and remote repositories to identify current state, detect changes, and build a comprehensive view of divergences between local and GitHub.

## Agent
**git-collector** (primary)
**github-collector** (secondary)

## Inputs

### From Workflow
- `branch_filter`: List of branches to scan
- `sync_mode`: Determines depth of scan

### From Context
- Local repository path
- GitHub repository URL
- Authentication credentials

## Actions

### 1. Scan Local Repository
```bash
# Get current branch
git rev-parse --abbrev-ref HEAD

# Get local branches
git branch --list

# Get local commits (for each branch)
git log --oneline --no-merges -n 100

# Get uncommitted changes
git status --porcelain

# Get local tags
git tag --list
```

### 2. Fetch Remote Information
```bash
# Fetch from remote without merging
git fetch origin --prune --tags

# Get remote branches
git branch -r

# Get remote commits (for each branch)
git log origin/main --oneline --no-merges -n 100

# Check divergence
git rev-list --left-right --count main...origin/main
```

### 3. Query GitHub API
```javascript
// Get repository metadata
GET /repos/{owner}/{repo}

// Get branches
GET /repos/{owner}/{repo}/branches

// Get recent commits
GET /repos/{owner}/{repo}/commits?per_page=100

// Get pull requests
GET /repos/{owner}/{repo}/pulls?state=open

// Get branch protection rules
GET /repos/{owner}/{repo}/branches/{branch}/protection
```

### 4. Build Change Graph
```javascript
{
  local: {
    branches: [
      {
        name: "main",
        commit: "abc123",
        ahead: 5,
        behind: 3,
        uncommitted: true
      }
    ],
    uncommitted_files: [
      "src/components/Button.tsx",
      "src/utils/helpers.ts"
    ]
  },
  remote: {
    branches: [
      {
        name: "main",
        commit: "def456",
        protection: {
          required_reviews: 1,
          require_code_owner_reviews: true
        }
      }
    ],
    open_prs: [
      {
        number: 123,
        title: "Add feature X",
        branch: "feature/x"
      }
    ]
  },
  divergences: [
    {
      branch: "main",
      local_ahead: 5,
      local_behind: 3,
      conflict_potential: "medium"
    }
  ]
}
```

### 5. Detect Conflicts
- Compare file changes in divergent commits
- Identify overlapping modifications
- Calculate conflict probability
- Flag high-risk files (e.g., config, migrations)

### 6. Analyze Commit Metadata
```javascript
// For each divergent commit
{
  sha: "abc123",
  author: "user@example.com",
  timestamp: "2025-12-04T10:30:00Z",
  message: "Add new feature",
  files_changed: [
    {
      path: "src/feature.ts",
      additions: 45,
      deletions: 12,
      status: "modified"
    }
  ],
  risk_indicators: {
    files_critical: false,
    breaking_change_keywords: false,
    test_coverage_impact: false
  }
}
```

## Outputs

### Repository State
```json
{
  "local_state": {
    "current_branch": "main",
    "branches_count": 5,
    "uncommitted_changes": true,
    "uncommitted_files_count": 2,
    "last_commit": {
      "sha": "abc123",
      "message": "Latest local commit",
      "timestamp": "2025-12-04T09:00:00Z"
    }
  },
  "remote_state": {
    "default_branch": "main",
    "branches_count": 7,
    "open_prs_count": 3,
    "last_commit": {
      "sha": "def456",
      "message": "Latest remote commit",
      "timestamp": "2025-12-04T10:00:00Z"
    }
  }
}
```

### Divergence Report
```json
{
  "divergences": [
    {
      "branch": "main",
      "status": "diverged",
      "local_ahead": 5,
      "local_behind": 3,
      "local_commits": ["abc123", "abc124", "abc125", "abc126", "abc127"],
      "remote_commits": ["def456", "def457", "def458"],
      "conflict_potential": "medium",
      "conflict_files": ["src/config.ts"]
    }
  ],
  "branches_only_local": ["feature/experimental"],
  "branches_only_remote": ["hotfix/security-patch"],
  "total_files_affected": 23
}
```

### Change Graph
- Structured representation of all changes
- Relationships between commits
- File-level change tracking
- Metadata for decision-making

### Conflict Analysis
```json
{
  "potential_conflicts": [
    {
      "file": "src/config.ts",
      "local_commit": "abc123",
      "remote_commit": "def456",
      "conflict_type": "overlapping_changes",
      "severity": "high",
      "auto_resolvable": false
    }
  ],
  "safe_merges": [
    {
      "file": "README.md",
      "type": "non_overlapping",
      "confidence": 0.99
    }
  ]
}
```

## Error Handling

### Network Errors
- Retry fetch operations with exponential backoff
- Cache partial results
- Continue with local-only scan if remote unavailable

### Authentication Errors
- Prompt for credentials
- Validate token permissions
- Fall back to public API if applicable

### Repository Errors
- Validate git repository structure
- Check for corrupted refs
- Repair if possible, otherwise abort

## Success Criteria
✅ Local repository state captured
✅ Remote repository state fetched
✅ Divergences identified
✅ Conflict potential assessed
✅ Change graph built

## Next Step
Proceed to **step-02-learn** with:
- Repository state
- Divergence report
- Change graph
- Conflict analysis
