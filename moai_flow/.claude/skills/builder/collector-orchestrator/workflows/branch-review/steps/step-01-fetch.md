# Step 01: Fetch Branch Information

## Overview

This step fetches comprehensive branch information from GitHub/Git including metadata, commits, and file changes.

## Inputs

- **branch_name** (string): Name of the branch to fetch information for
- **repository** (string, optional): Repository name (auto-detected if not provided)
- **base_branch** (string, optional): Base branch for comparison (default: "main")

## Process

### 1. Repository Detection

```bash
# Auto-detect repository if not provided
if [ -z "$repository" ]; then
  repository=$(git remote get-url origin | sed -E 's/.*[:/]([^/]+\/[^.]+)(\.git)?$/\1/')
fi
```

### 2. Branch Validation

```bash
# Verify branch exists locally or remotely
git rev-parse --verify "$branch_name" 2>/dev/null || \
  git ls-remote --heads origin "$branch_name" | grep -q "$branch_name"
```

### 3. Fetch Branch Metadata

Using GitHub CLI (gh) or Git commands:

```bash
# Using GitHub CLI
gh api repos/$repository/branches/$branch_name --jq '{
  name: .name,
  protected: .protected,
  commit_sha: .commit.sha,
  commit_url: .commit.url,
  last_commit_date: .commit.commit.author.date,
  author: .commit.commit.author.name,
  author_email: .commit.commit.author.email
}'

# Fallback to Git
git show-ref --verify --quiet refs/heads/$branch_name && \
  git log -1 --format='{"sha": "%H", "author": "%an", "email": "%ae", "date": "%aI", "message": "%s"}' $branch_name
```

### 4. Fetch Commit History

```bash
# Get commits between base_branch and branch_name
git log $base_branch..$branch_name --format='%H|%an|%ae|%aI|%s|%b' --reverse
```

Parse into structured format:

```json
{
  "sha": "abc123...",
  "author": "John Doe",
  "email": "john@example.com",
  "date": "2025-12-04T10:30:00Z",
  "subject": "Add new feature",
  "body": "Detailed commit message..."
}
```

### 5. Fetch File Changes

```bash
# Get list of changed files with stats
git diff --name-status $base_branch...$branch_name
git diff --stat $base_branch...$branch_name
```

Parse into structured format:

```json
{
  "file": "src/api/users.py",
  "status": "modified",
  "additions": 45,
  "deletions": 12,
  "changes": 57
}
```

### 6. Additional Metadata

Collect supplementary information:

```bash
# Branch age
first_commit_date=$(git log $base_branch..$branch_name --format='%aI' --reverse | head -1)
last_commit_date=$(git log $base_branch..$branch_name --format='%aI' | head -1)

# Commit count
commit_count=$(git rev-list --count $base_branch..$branch_name)

# Contributors
contributors=$(git log $base_branch..$branch_name --format='%an|%ae' | sort -u)

# Merge status
is_merged=$(git branch --merged $base_branch | grep -q "^[* ]*$branch_name$" && echo true || echo false)
```

## Outputs

### branch_data (object)

```json
{
  "name": "feature/user-authentication",
  "repository": "myorg/myapp",
  "base_branch": "main",
  "protected": false,
  "current_sha": "abc123def456",
  "created_date": "2025-11-20T09:00:00Z",
  "last_updated": "2025-12-04T10:30:00Z",
  "age_days": 14,
  "is_merged": false,
  "ahead_by": 15,
  "behind_by": 3,
  "contributors": [
    {
      "name": "John Doe",
      "email": "john@example.com",
      "commit_count": 12
    },
    {
      "name": "Jane Smith",
      "email": "jane@example.com",
      "commit_count": 3
    }
  ]
}
```

### commits (array)

```json
[
  {
    "sha": "abc123",
    "short_sha": "abc123",
    "author": "John Doe",
    "email": "john@example.com",
    "date": "2025-11-20T09:15:00Z",
    "subject": "Initial authentication setup",
    "body": "Add OAuth2 provider configuration",
    "files_changed": 5,
    "insertions": 234,
    "deletions": 12
  },
  {
    "sha": "def456",
    "short_sha": "def456",
    "author": "Jane Smith",
    "email": "jane@example.com",
    "date": "2025-11-21T14:30:00Z",
    "subject": "Add user login endpoint",
    "body": "Implement /auth/login with JWT tokens",
    "files_changed": 3,
    "insertions": 156,
    "deletions": 8
  }
]
```

### files_changed (array)

```json
[
  {
    "path": "src/api/auth.py",
    "status": "added",
    "additions": 234,
    "deletions": 0,
    "changes": 234,
    "language": "Python",
    "category": "source"
  },
  {
    "path": "tests/test_auth.py",
    "status": "added",
    "additions": 145,
    "deletions": 0,
    "changes": 145,
    "language": "Python",
    "category": "tests"
  },
  {
    "path": "src/models/user.py",
    "status": "modified",
    "additions": 45,
    "deletions": 12,
    "changes": 57,
    "language": "Python",
    "category": "source"
  },
  {
    "path": "README.md",
    "status": "modified",
    "additions": 23,
    "deletions": 5,
    "changes": 28,
    "language": "Markdown",
    "category": "docs"
  }
]
```

## Error Handling

### Branch Not Found

```json
{
  "error": "branch_not_found",
  "message": "Branch 'feature/nonexistent' not found in repository",
  "suggestions": [
    "Verify branch name spelling",
    "Check if branch exists on remote",
    "Ensure you have access to the repository"
  ]
}
```

### GitHub API Rate Limit

```json
{
  "error": "rate_limit_exceeded",
  "message": "GitHub API rate limit exceeded",
  "retry_after": 3600,
  "suggestions": [
    "Use authenticated GitHub token",
    "Wait 60 minutes before retrying",
    "Use git commands instead of GitHub API"
  ]
}
```

### Authentication Error

```json
{
  "error": "authentication_failed",
  "message": "GitHub authentication failed",
  "suggestions": [
    "Set GITHUB_TOKEN environment variable",
    "Run 'gh auth login' to authenticate",
    "Verify token has repo access permissions"
  ]
}
```

## Implementation Details

### Dependencies

- Git (required)
- GitHub CLI `gh` (optional, preferred)
- jq (for JSON parsing)
- Python 3.9+ (for data processing)

### Performance Considerations

- **Large repositories**: Use `--first-parent` flag for faster history traversal
- **Many commits**: Limit fetch depth with `--max-count=1000`
- **Network latency**: Cache GitHub API responses for 5 minutes

### Caching Strategy

```python
import hashlib
import json
from pathlib import Path
from datetime import datetime, timedelta

CACHE_DIR = Path(".claude/cache/branch-data")
CACHE_TTL = timedelta(minutes=5)

def get_cache_key(branch_name, repository, base_branch):
    return hashlib.md5(f"{repository}:{branch_name}:{base_branch}".encode()).hexdigest()

def get_cached_data(cache_key):
    cache_file = CACHE_DIR / f"{cache_key}.json"
    if cache_file.exists():
        cache_data = json.loads(cache_file.read_text())
        cached_time = datetime.fromisoformat(cache_data["cached_at"])
        if datetime.now() - cached_time < CACHE_TTL:
            return cache_data["data"]
    return None

def save_cache(cache_key, data):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_file = CACHE_DIR / f"{cache_key}.json"
    cache_data = {
        "cached_at": datetime.now().isoformat(),
        "data": data
    }
    cache_file.write_text(json.dumps(cache_data, indent=2))
```

## Validation

### Output Validation Schema

```python
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class Contributor(BaseModel):
    name: str
    email: str
    commit_count: int

class BranchData(BaseModel):
    name: str
    repository: str
    base_branch: str
    protected: bool
    current_sha: str
    created_date: datetime
    last_updated: datetime
    age_days: int
    is_merged: bool
    ahead_by: int
    behind_by: int
    contributors: List[Contributor]

class Commit(BaseModel):
    sha: str
    short_sha: str
    author: str
    email: str
    date: datetime
    subject: str
    body: str
    files_changed: int
    insertions: int
    deletions: int

class FileChange(BaseModel):
    path: str
    status: str
    additions: int
    deletions: int
    changes: int
    language: str
    category: str
```

## Testing

### Unit Tests

```python
def test_fetch_branch_data():
    result = fetch_branch_data(
        branch_name="feature/test",
        repository="test/repo",
        base_branch="main"
    )
    assert result["branch_data"]["name"] == "feature/test"
    assert len(result["commits"]) > 0
    assert len(result["files_changed"]) > 0

def test_branch_not_found():
    with pytest.raises(BranchNotFoundError):
        fetch_branch_data(
            branch_name="nonexistent",
            repository="test/repo",
            base_branch="main"
        )
```

### Integration Tests

```bash
# Test with real repository
./test_step_01.sh feature/actual-branch myorg/myrepo main
```

## Next Step

Data flows to **step-02-analyze** for scoring and analysis.
