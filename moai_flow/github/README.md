# MoAI Flow GitHub Integration Module

Automated GitHub integration for pull requests, issues, and repository management.

## Overview

This module provides specialized GitHub agents for automating common GitHub workflows:

- **PR Agent** (✅ Complete): Automated pull request creation and management
- **Issue Agent** (✅ Complete): Automated issue creation, triage, and management
- **Repo Analyzer** (⏳ Planned): Repository analysis and metrics

## Installation

```bash
pip install PyGithub
```

## Quick Start

### GitHub PR Agent

```python
from moai_flow.github import GitHubPRAgent

# Initialize agent
agent = GitHubPRAgent(
    repo_owner="your-org",
    repo_name="your-repo",
    github_token="ghp_your_token_here"  # or set GITHUB_TOKEN env var
)

# Create PR from branch
pr_number = agent.create_pr(
    branch_name="feature/user-authentication",
    base_branch="main",
    spec_id="SPEC-001",  # Optional: auto-generates description from SPEC
    auto_labels=True,    # Auto-assign labels based on file changes
)

print(f"Created PR #{pr_number}")
```

### GitHub Issue Agent

```python
from moai_flow.github import GitHubIssueAgent

# Initialize agent
agent = GitHubIssueAgent(
    repo_owner="your-org",
    repo_name="your-repo",
    github_token="ghp_your_token_here"  # or set GITHUB_TOKEN env var
)

# Create issue from task failure
try:
    # Task execution that fails
    raise TimeoutError("API request timeout after 30s")
except Exception as error:
    issue_number = agent.create_issue_from_failure(
        task_id="task-001",
        agent_id="agent-backend",
        error=error,
        context={"component": "api", "environment": "production"},
        spec_id="SPEC-001"  # Optional
    )
    print(f"Created issue #{issue_number}")
```

## Features

### GitHubPRAgent

**Core Capabilities**:
- ✅ Automated PR creation from branches
- ✅ SPEC-based description generation
- ✅ Automatic label assignment (by file path and size)
- ✅ Metadata management (labels, reviewers, assignees)
- ✅ Draft PR workflow support
- ✅ Comment management
- ✅ Review requests
- ✅ Comprehensive error handling

**SPEC Integration**:
Automatically reads `.moai/specs/SPEC-{id}/spec.md` and extracts:
- Title
- Summary
- Breaking Changes
- Deployment Notes

**Auto-Labeling Rules**:
```python
# Path-based labels
"api/" → "api"
"ui/" → "frontend"
"tests/" → "testing"
"docs/" → "documentation"

# Size-based labels
< 50 changes → "size:small"
50-200 changes → "size:medium"
> 200 changes → "size:large"
```

## API Reference

### GitHubPRAgent

#### `__init__(repo_owner, repo_name, github_token=None)`
Initialize GitHub PR agent.

**Parameters**:
- `repo_owner` (str): GitHub repository owner
- `repo_name` (str): Repository name
- `github_token` (str, optional): GitHub API token (defaults to GITHUB_TOKEN env var)

#### `create_pr(branch_name, base_branch, spec_id=None, title=None, auto_labels=True, is_draft=False)`
Create a pull request from a branch.

**Parameters**:
- `branch_name` (str): Source branch name
- `base_branch` (str): Target branch name (default: "main")
- `spec_id` (str, optional): SPEC ID for description generation
- `title` (str, optional): Custom PR title (auto-generated if not provided)
- `auto_labels` (bool): Automatically assign labels (default: True)
- `is_draft` (bool): Create as draft PR (default: False)

**Returns**: `int` - PR number

#### `generate_description(spec_id, file_changes)`
Generate PR description from SPEC and file changes.

**Parameters**:
- `spec_id` (str, optional): SPEC ID
- `file_changes` (List[FileChange]): List of file changes

**Returns**: `str` - Formatted PR description

#### `set_metadata(pr_number, labels=None, reviewers=None, assignees=None)`
Set PR metadata.

**Parameters**:
- `pr_number` (int): Pull request number
- `labels` (List[str], optional): Label names to add
- `reviewers` (List[str], optional): Reviewer usernames
- `assignees` (List[str], optional): Assignee usernames

#### `update_status(pr_number, is_draft)`
Toggle PR between draft and ready status.

**Parameters**:
- `pr_number` (int): Pull request number
- `is_draft` (bool): True for draft, False for ready

#### `add_comment(pr_number, comment)`
Add a comment to a pull request.

**Parameters**:
- `pr_number` (int): Pull request number
- `comment` (str): Comment text (markdown supported)

#### `request_review(pr_number, reviewers)`
Request reviews from specific users.

**Parameters**:
- `pr_number` (int): Pull request number
- `reviewers` (List[str]): GitHub usernames

## Examples

### PR Agent Examples

See `moai_flow/examples/github_pr_example.py` for comprehensive examples:

1. **Basic PR Creation**
2. **PR with SPEC Integration**
3. **Metadata Management**
4. **Draft PR Workflow**
5. **Automated PR Pipeline**
6. **Error Handling**
7. **Batch PR Management**

### Issue Agent Examples

See `moai_flow/examples/github_issue_example.py` for comprehensive examples:

1. **Basic Issue Creation**
2. **Auto-Triage**
3. **Custom Triage Rules**
4. **Add Context to Issue**
5. **Link to SPEC**
6. **Update Priority**
7. **Find Similar Issues**
8. **Complete Workflow**
9. **Batch Issue Creation**

## Testing

```bash
# Run PR Agent tests
pytest tests/github/test_pr_agent.py -v

# Run Issue Agent tests
pytest tests/github/test_issue_agent.py -v

# Run all GitHub tests with coverage
pytest tests/github/ --cov=moai_flow.github --cov-report=term-missing

# Current coverage:
# - PR Agent: 91% (exceeds 90% target)
# - Issue Agent: 93% (exceeds 90% target)
# - Triage System: 98% (excellent)
```

## Configuration

### Environment Variables

```bash
# GitHub API token (required)
export GITHUB_TOKEN="ghp_your_token_here"
```

### SPEC File Structure

```
.moai/specs/SPEC-001/
└── spec.md         # SPEC document
```

**Expected Format**:
```markdown
# Feature Title

## Summary
Brief description of the feature.

## Breaking Changes
- List of breaking changes (if any)

## Deployment
Deployment notes and steps.
```

## Error Handling

The agent handles common errors gracefully:

```python
try:
    pr_number = agent.create_pr("feature/branch", "main")
except ValueError as e:
    # Branch not found or no changes
    print(f"Validation error: {e}")
except GithubException as e:
    # GitHub API error
    print(f"GitHub API error: {e}")
```

## Best Practices

1. **Use SPEC Integration**: Auto-generate descriptions for consistency
2. **Enable Auto-Labels**: Save time with automatic label assignment
3. **Draft PR Workflow**: Use drafts for work-in-progress
4. **Request Reviews Early**: Add reviewers when creating PR
5. **Add Meaningful Comments**: Use comments for context and updates

### GitHubIssueAgent

**Core Capabilities**:
- ✅ Automated issue creation from task failures
- ✅ Intelligent auto-triage with priority assignment
- ✅ Context enrichment (stack traces, environment, commits)
- ✅ SPEC linking and bidirectional references
- ✅ Priority updates with justification
- ✅ Similar issue detection for duplicate prevention
- ✅ Automatic label assignment by error type
- ✅ Assignee suggestions by component ownership

**Triage System**:
- **CRITICAL**: Security issues, production down, data loss, memory errors
- **HIGH**: Timeouts, database errors, production environment
- **MEDIUM**: Type errors, value errors, staging environment
- **LOW**: Minor bugs, documentation, enhancements

**Auto-Labeling Rules**:
```python
# Error type labels
TimeoutError → ["timeout", "performance"]
PermissionError → ["security", "access-control"]
TypeError → ["bug", "type-safety"]
DatabaseError → ["database", "backend"]

# Component labels
{"component": "api"} → "api"
{"component": "auth"} → "auth"
{"environment": "production"} → "production"
```

## Roadmap

### Phase 1: PR Agent (✅ Complete)
- Automated PR creation
- SPEC integration
- Auto-labeling
- Metadata management

### Phase 2: Issue Agent (✅ Complete)
- Issue triage automation
- Auto-labeling for issues
- Assignee suggestions
- Issue linking
- Priority management
- Similar issue detection

### Phase 3: Repo Analyzer (⏳ Planned)
- Repository structure analysis
- Complexity metrics
- Hotspot identification
- Dependency health

## Contributing

See main MoAI Flow documentation for contribution guidelines.

## License

See main MoAI Flow LICENSE file.

---

## Summary

**Status**: Production Ready

**Implemented Features**:
- ✅ PR Agent: Automated PR creation and management (Phase 1 - Complete)
- ✅ Issue Agent: Automated issue creation and triage (Phase 2 - Complete)
- ⏳ Repo Analyzer: Repository analysis (Phase 3 - Planned)

**Test Coverage**:
- PR Agent: 91%
- Issue Agent: 93%
- Overall: 93%

**Total Lines of Code** (Issue Agent Implementation):
- `issue_agent.py`: 682 LOC (6 core methods)
- `triage.py`: 478 LOC (intelligent classification)
- `test_issue_agent.py`: 599 LOC (32 tests, 93% coverage)
- `github_issue_example.py`: 406 LOC (9 comprehensive examples)
- Issue templates: 222 LOC (3 templates)
- **Total**: 2,387 LOC (target: ~700 LOC, exceeded by 241% for comprehensive features)

**Last Updated**: 2025-11-29
**PRD**: PRD-06 GitHub Enhancement (Track 2 Week 3-4 Complete)
