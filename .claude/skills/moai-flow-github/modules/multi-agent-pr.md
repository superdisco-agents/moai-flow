# Multi-Agent PR Management

Advanced pull request workflows for multi-agent systems with SPEC integration, automated description generation, and intelligent labeling.

## Overview

The GitHubPRAgent automates pull request creation and management, integrating seamlessly with MoAI-ADK's SPEC-first development workflow. It automatically generates PR descriptions from SPEC documents, assigns appropriate labels based on file changes, and manages metadata.

## Core Capabilities

### 1. SPEC-Based Description Generation

**Automatic Extraction**:

The PR agent reads `.moai/specs/SPEC-{id}/spec.md` and extracts:

```markdown
# Feature Title ← Extracted as PR title
## Summary ← Extracted for PR body
Breaking changes list ← Extracted for warning section
## Deployment ← Extracted for deployment notes
```

**Template Variables**:

```markdown
## SPEC
Implements: {{SPEC_ID}}

## Summary
{{SUMMARY}}

## Changes
{{CHANGES}}  ← Auto-generated from file diff

## Test Plan
{{TEST_PLAN}}  ← Auto-generated from file types

## Breaking Changes
{{BREAKING_CHANGES}}

## Deployment Notes
{{DEPLOYMENT_NOTES}}
```

### 2. Intelligent Auto-Labeling

**Path-Based Labels**:

```python
label_rules = {
    "api": ["api/", "endpoints/", "routes/"],
    "frontend": ["ui/", "components/", "pages/"],
    "backend": ["core/", "services/", "models/"],
    "testing": ["tests/", "test_", "_test"],
    "documentation": ["docs/", "README", ".md"],
    "configuration": ["config/", ".yaml", ".json", ".toml"],
}
```

**Size-Based Labels**:

```python
total_changes = sum(c.additions + c.deletions for c in file_changes)

if total_changes < 50:
    labels.add("size:small")
elif total_changes < 200:
    labels.add("size:medium")
else:
    labels.add("size:large")
```

**Example**:

```python
# PR modifying api/endpoints/auth.py (25 lines) + tests/test_auth.py (30 lines)
# Labels: ["api", "testing", "size:small"]
```

### 3. Draft PR Workflow

**Use Cases**:
- Work-in-progress features
- Experimental changes requiring feedback
- Long-running development branches

**Workflow**:

```python
# Create as draft
pr_number = agent.create_pr(
    branch_name="feature/experimental",
    base_branch="main",
    spec_id="SPEC-001",
    is_draft=True  # Created as draft
)

# Development and feedback cycle...

# Mark ready for review
agent.update_status(pr_number, is_draft=False)
```

**GraphQL Implementation**:

```graphql
# Convert to draft
mutation($pullRequestId: ID!) {
    convertPullRequestToDraft(input: {pullRequestId: $pullRequestId}) {
        pullRequest { isDraft }
    }
}

# Mark ready for review
mutation($pullRequestId: ID!) {
    markPullRequestReadyForReview(input: {pullRequestId: $pullRequestId}) {
        pullRequest { isDraft }
    }
}
```

### 4. Metadata Management

**Labels**:

```python
agent.set_metadata(
    pr_number=pr_number,
    labels=["enhancement", "high-priority", "backend"]
)
```

**Reviewers**:

```python
agent.set_metadata(
    pr_number=pr_number,
    reviewers=["senior-dev1", "senior-dev2", "tech-lead"]
)
```

**Assignees**:

```python
agent.set_metadata(
    pr_number=pr_number,
    assignees=["feature-author", "qa-engineer"]
)
```

**Combined**:

```python
agent.set_metadata(
    pr_number=pr_number,
    labels=["feature", "api"],
    reviewers=["backend-expert"],
    assignees=["author"]
)
```

### 5. Comment Management

**Add Comments**:

```python
# Add deployment notes
agent.add_comment(
    pr_number,
    """
    ## Deployment Checklist
    - [ ] Database migrations ready
    - [ ] Environment variables configured
    - [ ] Feature flags enabled
    """
)
```

**Request Reviews**:

```python
# Request additional reviews
agent.request_review(
    pr_number,
    reviewers=["security-expert", "performance-expert"]
)
```

## Advanced Patterns

### Pattern 1: Coordinated Multi-Agent PR Creation

**Scenario**: Full-stack feature requires coordinated frontend and backend PRs.

```python
from moai_flow.github import GitHubPRAgent

pr_agent = GitHubPRAgent("org", "repo")

# Backend agent completes backend implementation
backend_pr = pr_agent.create_pr(
    branch_name="feature/SPEC-001-backend",
    base_branch="main",
    spec_id="SPEC-001",
    auto_labels=True
)

# Frontend agent completes frontend implementation
frontend_pr = pr_agent.create_pr(
    branch_name="feature/SPEC-001-frontend",
    base_branch="main",
    spec_id="SPEC-001",
    auto_labels=True
)

# Cross-reference PRs
pr_agent.add_comment(
    backend_pr,
    f"🔗 Related frontend PR: #{frontend_pr}\n\n"
    f"Both PRs must be merged for complete feature deployment."
)

pr_agent.add_comment(
    frontend_pr,
    f"🔗 Related backend PR: #{backend_pr}\n\n"
    f"Backend API must be deployed first."
)
```

### Pattern 2: Progressive PR Review

**Scenario**: Large PR requires multi-stage review (architecture → security → performance).

```python
# Create draft PR
pr_number = agent.create_pr(
    branch_name="feature/large-refactor",
    spec_id="SPEC-001",
    is_draft=True
)

# Stage 1: Architecture review
agent.request_review(pr_number, reviewers=["architect"])
agent.add_comment(pr_number, "## Stage 1: Architecture Review\n@architect please review design")

# After architecture approval, stage 2: Security review
agent.request_review(pr_number, reviewers=["security-expert"])
agent.add_comment(pr_number, "## Stage 2: Security Review\n@security-expert please review")

# After security approval, stage 3: Performance review
agent.request_review(pr_number, reviewers=["performance-expert"])
agent.add_comment(pr_number, "## Stage 3: Performance Review\n@performance-expert please review")

# After all approvals, mark ready for merge
agent.update_status(pr_number, is_draft=False)
agent.add_comment(pr_number, "✅ All reviews complete. Ready for merge.")
```

### Pattern 3: Automated PR from SPEC Completion

**Scenario**: Automatically create PR when TDD implementation completes.

```python
def on_tdd_complete(spec_id, branch_name, test_coverage):
    """Triggered by manager-tdd when implementation passes."""
    pr_agent = GitHubPRAgent("org", "repo")

    # Create PR
    pr_number = pr_agent.create_pr(
        branch_name=branch_name,
        base_branch="main",
        spec_id=spec_id,
        auto_labels=True,
        is_draft=False
    )

    # Add test coverage comment
    pr_agent.add_comment(
        pr_number,
        f"## Test Coverage\n\n"
        f"✅ Coverage: {test_coverage}%\n"
        f"Target: >= 90%\n\n"
        f"All tests passing. Ready for review."
    )

    # Request reviews based on SPEC domain
    domain = get_domain_from_spec(spec_id)
    reviewers = get_reviewers_for_domain(domain)
    pr_agent.set_metadata(
        pr_number,
        reviewers=reviewers
    )

    return pr_number
```

### Pattern 4: Incremental PR Updates

**Scenario**: Add context and updates to existing PR as implementation progresses.

```python
# Initial PR creation
pr_number = agent.create_pr(
    branch_name="feature/auth",
    spec_id="SPEC-001",
    is_draft=True
)

# Update 1: Backend complete
agent.add_comment(
    pr_number,
    "✅ Backend implementation complete\n"
    "- Authentication service\n"
    "- JWT token generation\n"
    "- User session management"
)

# Update 2: Tests added
agent.add_comment(
    pr_number,
    "✅ Tests added\n"
    "- Unit tests: 95% coverage\n"
    "- Integration tests: 12 scenarios\n"
    "- All tests passing"
)

# Update 3: Ready for review
agent.update_status(pr_number, is_draft=False)
agent.set_metadata(
    pr_number,
    reviewers=["security-expert", "backend-lead"]
)
agent.add_comment(
    pr_number,
    "✅ Implementation complete. Ready for review.\n\n"
    "Please review security implications of JWT implementation."
)
```

## API Reference

### GitHubPRAgent

**Constructor**:

```python
def __init__(
    self,
    repo_owner: str,
    repo_name: str,
    github_token: Optional[str] = None
)
```

**Methods**:

#### create_pr()

```python
def create_pr(
    self,
    branch_name: str,
    base_branch: str = "main",
    spec_id: Optional[str] = None,
    title: Optional[str] = None,
    auto_labels: bool = True,
    is_draft: bool = False
) -> int
```

**Returns**: PR number

**Raises**:
- `ValueError`: Branch not found or no changes
- `GithubException`: API error

#### generate_description()

```python
def generate_description(
    self,
    spec_id: Optional[str],
    file_changes: List[FileChange]
) -> str
```

**Returns**: Formatted PR description in markdown

#### set_metadata()

```python
def set_metadata(
    self,
    pr_number: int,
    labels: Optional[List[str]] = None,
    reviewers: Optional[List[str]] = None,
    assignees: Optional[List[str]] = None
) -> None
```

#### update_status()

```python
def update_status(
    self,
    pr_number: int,
    is_draft: bool
) -> None
```

#### add_comment()

```python
def add_comment(
    self,
    pr_number: int,
    comment: str
) -> None
```

#### request_review()

```python
def request_review(
    self,
    pr_number: int,
    reviewers: List[str]
) -> None
```

## Best Practices

**DO**:
- ✅ Use SPEC integration for automatic description generation
- ✅ Enable auto-labels to save time
- ✅ Use draft PRs for work-in-progress
- ✅ Request reviews early
- ✅ Add meaningful comments for context

**DON'T**:
- ❌ Create PRs without SPEC documentation
- ❌ Skip auto-labeling (manual labeling is error-prone)
- ❌ Force-push to PR branches (breaks review history)
- ❌ Create oversized PRs (>500 lines = hard to review)
- ❌ Forget to link related PRs

## Integration Points

**SPEC-First Workflow**:
```
SPEC Generation → TDD Implementation → PR Creation (auto) → Review → Merge
```

**Multi-Agent Coordination**:
```
Backend Agent → Backend PR
Frontend Agent → Frontend PR
↓
Cross-reference PRs → Coordinated merge
```

**CI/CD Integration**:
```
PR Created → GitHub Actions triggered → Tests run → Coverage report → Review required
```

---

**Related Documentation**:
- [Collaborative Review Module](collaborative-review.md)
- [Workflow Automation Module](workflow-automation.md)
- [Integration Patterns Module](integration-patterns.md)
