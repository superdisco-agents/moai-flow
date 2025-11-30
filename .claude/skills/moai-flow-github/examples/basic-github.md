# Basic GitHub Usage Examples

Quick start examples for PR Agent, Issue Agent, and Repo Agent.

## Prerequisites

```bash
pip install PyGithub
export GITHUB_TOKEN="ghp_your_token_here"
```

## Example 1: Create PR from Branch

**Scenario**: You've completed a feature on a branch and want to create a PR.

```python
from moai_flow.github import GitHubPRAgent

# Initialize
agent = GitHubPRAgent(
    repo_owner="your-org",
    repo_name="your-repo",
    github_token="ghp_token"  # or use GITHUB_TOKEN env var
)

# Create PR
pr_number = agent.create_pr(
    branch_name="feature/user-authentication",
    base_branch="main",
    spec_id="SPEC-001",  # Optional: auto-generates description
    auto_labels=True,    # Auto-assign labels
    is_draft=False
)

print(f"Created PR #{pr_number}")
```

**Output**:
```
Created PR #42
```

## Example 2: Create PR with Custom Metadata

**Scenario**: Create PR with specific reviewers and labels.

```python
from moai_flow.github import GitHubPRAgent

agent = GitHubPRAgent("org", "repo")

# Create PR
pr_number = agent.create_pr(
    branch_name="feature/api-optimization",
    base_branch="main",
    auto_labels=True
)

# Set metadata
agent.set_metadata(
    pr_number=pr_number,
    labels=["performance", "high-priority", "backend"],
    reviewers=["tech-lead", "backend-expert"],
    assignees=["feature-author"]
)

# Add deployment notes
agent.add_comment(
    pr_number,
    """
    ## Deployment Notes
    - Requires database migration
    - Environment variables updated
    - Feature flag: `api_optimization_v2`
    """
)

print(f"PR #{pr_number} configured")
```

## Example 3: Create Issue from Exception

**Scenario**: Catch an exception and create a GitHub issue.

```python
from moai_flow.github import GitHubIssueAgent

agent = GitHubIssueAgent("org", "repo")

try:
    # Task that fails
    response = requests.get(api_url, timeout=30)
    response.raise_for_status()
except TimeoutError as error:
    # Create issue automatically
    issue_number = agent.create_issue_from_failure(
        task_id="api-call-001",
        agent_id="backend-agent",
        error=error,
        context={
            "component": "api",
            "environment": "production",
            "url": api_url,
            "frequency": 5  # Occurred 5 times
        },
        spec_id="SPEC-001"
    )

    print(f"Created issue #{issue_number}")
```

**Output**:
```
Created issue #123
```

## Example 4: Monitor Repository Health

**Scenario**: Check overall repository health.

```python
from moai_flow.github import GitHubRepoAgent

agent = GitHubRepoAgent("org", "repo")

# Calculate health
health = agent.monitor_health()

print(f"Health Score: {health.total_score}/100 ({health.category.value})")
print(f"\\nComponent Scores:")
print(f"  Issue Velocity:      {health.issue_velocity_score}/20")
print(f"  PR Merge Time:       {health.pr_merge_time_score}/20")
print(f"  Stale Items:         {health.stale_item_score}/20")
print(f"  Test Coverage:       {health.test_coverage_score}/20")
print(f"  Contributor Activity: {health.contributor_activity_score}/20")
```

**Output**:
```
Health Score: 78/100 (good)

Component Scores:
  Issue Velocity:      16/20
  PR Merge Time:       14/20
  Stale Items:         18/20
  Test Coverage:       15/20
  Contributor Activity: 15/20
```

## Example 5: Find and Close Stale Issues

**Scenario**: Find issues stale for 60+ days and close them.

```python
from moai_flow.github import GitHubRepoAgent

agent = GitHubRepoAgent("org", "repo")

# Find stale issues
stale_issues = agent.get_stale_issues(days=60)

print(f"Found {len(stale_issues)} stale issues\\n")

# Display top 5
for issue in stale_issues[:5]:
    print(f"#{issue.number}: {issue.title}")
    print(f"  Last updated: {issue.days_stale} days ago")
    print(f"  URL: {issue.url}\\n")

# Close them (dry run first)
cleanup_report = agent.cleanup_stale_items(
    warning_days=30,
    close_days=60,
    auto_close_days=90,
    dry_run=True  # Preview mode
)

print(f"Would close: {cleanup_report['summary']['would_close_items']} items")
```

## Example 6: Get Actionable Recommendations

**Scenario**: Get prioritized recommendations for improving repository health.

```python
from moai_flow.github import GitHubRepoAgent

agent = GitHubRepoAgent("org", "repo")

# Get recommendations
recommendations = agent.get_actionable_recommendations()

print(f"Generated {len(recommendations)} recommendations:\\n")

for rec in recommendations:
    print(f"[{rec.priority.value.upper()}] {rec.action}")
    print(f"  Impact: {rec.impact}")
    if rec.details:
        print(f"  Details: {rec.details}")
    print()
```

**Output**:
```
Generated 4 recommendations:

[CRITICAL] Address 15 stale pull requests (30+ days inactive)
  Impact: Improve PR merge time and contributor satisfaction
  Details: Stale PRs block contributors and hurt project momentum

[HIGH] Address 25 stale issues (30+ days inactive)
  Impact: Improve issue velocity score and reduce clutter
  Details: Consider triaging, closing, or updating these issues

[MEDIUM] Improve test coverage
  Impact: Increase health score and code quality
  Details: Target: 80%+ test coverage across the project

[MEDIUM] Increase contributor engagement
  Impact: Improve project sustainability
  Details: Consider good-first-issue labels, documentation improvements
```

## Example 7: Check for Similar Issues

**Scenario**: Before creating a new issue, check for duplicates.

```python
from moai_flow.github import GitHubIssueAgent

agent = GitHubIssueAgent("org", "repo")

error = TimeoutError("API request timeout after 30s")

# Search for similar issues
similar = agent.get_similar_issues(error, limit=5)

if similar:
    print(f"Found {len(similar)} similar issues:")
    for issue_num in similar:
        print(f"  - #{issue_num}")

    # Option 1: Add comment to existing issue
    agent.add_context(
        issue_number=similar[0],
        environment={"recurrence": "2025-11-30"}
    )
    print(f"\\nAdded context to existing issue #{similar[0]}")
else:
    # Option 2: Create new issue
    issue_number = agent.create_issue_from_failure(
        task_id="api-001",
        agent_id="backend",
        error=error,
        context={"component": "api"}
    )
    print(f"\\nCreated new issue #{issue_number}")
```

## Example 8: Update Issue Priority

**Scenario**: Manually escalate an issue to CRITICAL.

```python
from moai_flow.github import GitHubIssueAgent, IssuePriority

agent = GitHubIssueAgent("org", "repo")

# Update priority
agent.update_priority(
    issue_number=42,
    priority=IssuePriority.CRITICAL,
    reason="Production down, affecting 10k+ users. Revenue impact $50k/hour."
)

print("Priority updated to CRITICAL")
```

## Example 9: Draft PR Workflow

**Scenario**: Create draft PR, get feedback, then mark ready.

```python
from moai_flow.github import GitHubPRAgent

agent = GitHubPRAgent("org", "repo")

# Create as draft
pr_number = agent.create_pr(
    branch_name="feature/experimental",
    base_branch="main",
    is_draft=True  # Created as draft
)

print(f"Created draft PR #{pr_number}")

# ... development and feedback cycle ...

# Mark ready for review
agent.update_status(pr_number, is_draft=False)
agent.set_metadata(
    pr_number,
    reviewers=["tech-lead", "backend-expert"]
)
agent.add_comment(
    pr_number,
    "✅ Ready for review. All feedback addressed."
)

print(f"PR #{pr_number} marked ready for review")
```

## Example 10: Complete Workflow

**Scenario**: Full workflow from branch to PR to issue tracking.

```python
from moai_flow.github import GitHubPRAgent, GitHubIssueAgent, GitHubRepoAgent

# Step 1: Create PR
pr_agent = GitHubPRAgent("org", "repo")
pr_number = pr_agent.create_pr(
    branch_name="feature/SPEC-001",
    spec_id="SPEC-001",
    auto_labels=True
)
print(f"✅ PR #{pr_number} created")

# Step 2: Request reviews
pr_agent.set_metadata(
    pr_number,
    reviewers=["backend-expert"],
    assignees=["author"]
)
print(f"✅ Reviewers assigned")

# Step 3: Monitor health
repo_agent = GitHubRepoAgent("org", "repo")
health = repo_agent.monitor_health()
print(f"✅ Health Score: {health.total_score}/100")

# Step 4: If issues found, create issue
if health.total_score < 60:
    issue_agent = GitHubIssueAgent("org", "repo")
    issue_number = issue_agent.create_issue_from_failure(
        task_id="health-check",
        agent_id="monitoring",
        error=ValueError(f"Health degraded to {health.total_score}"),
        context={"component": "repository-health"}
    )
    print(f"⚠️  Health issue #{issue_number} created")

print("\\n✅ Workflow complete")
```

---

**Next Steps**:
- [Advanced PR Workflows](multi-agent-pr.md)
- [Complex Integration Scenarios](advanced-workflows.md)
