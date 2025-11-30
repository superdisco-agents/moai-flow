# GitHubRepoAgent Implementation Summary

## Overview

Comprehensive GitHub Repository Health Agent implementation for PRD-06 Repo Health monitoring and automation.

**File**: `moai_flow/github/repo_agent.py` (991 LOC)
**Tests**: `tests/github/test_repo_agent.py` (604 LOC)
**Example**: `moai_flow/github/examples/repo_health_monitoring.py` (258 LOC)

---

## Implementation Status

✅ **COMPLETE** - All 8 core methods implemented and tested (25/25 tests passing)

### Core Methods Implemented

1. ✅ `monitor_health()` - Calculate comprehensive repo health score (0-100)
2. ✅ `get_stale_issues()` - Find stale issues with configurable thresholds
3. ✅ `get_stale_prs()` - Find stale pull requests
4. ✅ `auto_close_stale()` - Close stale items with comment
5. ✅ `calculate_health_score()` - Quick health score access
6. ✅ `get_actionable_recommendations()` - Prioritized improvement actions
7. ✅ `cleanup_stale_items()` - Batch cleanup with progressive warnings
8. ✅ `get_health_trends()` - Historical trend analysis

---

## Health Score Calculation (0-100)

### Score Components

| Component | Points | Calculation |
|-----------|--------|-------------|
| **Issue Velocity** | 20 | Close rate (target: 80%+ in 30 days) |
| **PR Merge Time** | 20 | Avg merge time (target: <7 days) |
| **Stale Items** | 20 | Stale count (target: <10 items) |
| **Test Coverage** | 20 | Coverage % (target: 80%+) |
| **Contributor Activity** | 20 | Active contributors (target: 5+ in 30 days) |

### Health Categories

| Score Range | Category | Description |
|-------------|----------|-------------|
| 90-100 | EXCELLENT | Optimal repository health |
| 75-89 | GOOD | Good health, minor improvements |
| 60-74 | FAIR | Needs attention |
| 40-59 | POOR | Significant issues |
| 0-39 | CRITICAL | Immediate action required |

---

## Stale Item Detection System

### Three-Tier Stale Detection

**Progressive Warning System:**

1. **30 days**: Add `stale` label warning
2. **60 days**: Add close warning comment
3. **90 days**: Auto-close with detailed comment

### Configurable Thresholds

```python
agent = GitHubRepoAgent("owner", "repo")

# Find stale issues with custom threshold
stale_issues = agent.get_stale_issues(
    days=30,
    labels=["bug"],              # Filter by labels
    exclude_labels=["keep-open"]  # Exclude specific labels
)

# Batch cleanup with custom thresholds
cleanup_report = agent.cleanup_stale_items(
    warning_days=30,      # First warning
    close_days=60,        # Close warning
    auto_close_days=90,   # Auto-close
    dry_run=True,         # Preview mode
    exclude_labels=["keep-open", "pinned"]
)
```

---

## Actionable Recommendations

### Priority Levels

| Priority | When Triggered | Example |
|----------|---------------|---------|
| CRITICAL | 10+ stale PRs, health <40 | "Address 15 stale PRs blocking contributors" |
| HIGH | 20+ stale issues, component score <10 | "Improve issue velocity (current: 5/20)" |
| MEDIUM | 10-20 stale issues, score 10-15 | "Review 12 stale issues" |
| LOW | Minor improvements | "Improve documentation" |

### Recommendation Categories

- `stale_management` - Stale issues/PRs to address
- `issue_velocity` - Issue resolution rate improvements
- `pr_merge_time` - PR review speed improvements
- `test_coverage` - Test coverage improvements
- `contributor_activity` - Contributor engagement

---

## API Reference

### GitHubRepoAgent Class

```python
from moai_flow.github import GitHubRepoAgent

agent = GitHubRepoAgent(
    repo_owner="your-org",
    repo_name="your-repo",
    github_token="ghp_xxx"  # Optional, uses GITHUB_TOKEN env var
)
```

### Core Methods

#### 1. monitor_health()

Calculate comprehensive repository health.

```python
health = agent.monitor_health()

print(f"Health: {health.total_score}/100 ({health.category.value})")
print(f"Issue Velocity: {health.issue_velocity_score}/20")
print(f"PR Merge Time: {health.pr_merge_time_score}/20")
print(f"Stale Items: {health.stale_item_score}/20")
print(f"Test Coverage: {health.test_coverage_score}/20")
print(f"Contributor Activity: {health.contributor_activity_score}/20")
```

#### 2. get_stale_issues()

Find stale issues with filtering.

```python
stale = agent.get_stale_issues(
    days=30,
    labels=["bug", "enhancement"],  # Optional
    exclude_labels=["keep-open"]    # Optional
)

for issue in stale:
    print(f"#{issue.number}: {issue.title} ({issue.days_stale} days)")
```

#### 3. get_stale_prs()

Find stale pull requests.

```python
stale_prs = agent.get_stale_prs(days=14)

for pr in stale_prs:
    print(f"PR #{pr.number}: {pr.title} ({pr.days_stale} days)")
```

#### 4. auto_close_stale()

Close a stale item with comment.

```python
from moai_flow.github import StaleItem

stale_item = StaleItem(
    number=123,
    title="Old issue",
    url="https://github.com/org/repo/issues/123",
    state="open",
    created_at=datetime.now(),
    updated_at=datetime.now(),
    days_stale=95,
    type="issue"
)

success = agent.auto_close_stale(
    stale_item,
    reason="90 days of inactivity",
    label="auto-closed"
)
```

#### 5. calculate_health_score()

Quick health score access.

```python
score = agent.calculate_health_score()
print(f"Health: {score}/100")
```

#### 6. get_actionable_recommendations()

Get prioritized recommendations.

```python
recommendations = agent.get_actionable_recommendations()

for rec in recommendations:
    print(f"[{rec.priority.value}] {rec.action}")
    print(f"Impact: {rec.impact}")
```

#### 7. cleanup_stale_items()

Batch cleanup with dry run support.

```python
# Dry run first
report = agent.cleanup_stale_items(
    warning_days=30,
    close_days=60,
    auto_close_days=90,
    dry_run=True
)

print(f"Would close: {report['summary']['would_close_items']} items")

# Execute cleanup
report = agent.cleanup_stale_items(dry_run=False)
print(f"Closed: {report['summary']['closed_items']} items")
```

#### 8. get_health_trends()

Analyze health trends.

```python
trends = agent.get_health_trends(days=30)

for metric, data in trends.items():
    print(f"{metric}: {data[0]['value']}")
```

---

## Test Coverage

**25 tests, 100% passing** ✅

### Test Suites

| Suite | Tests | Coverage |
|-------|-------|----------|
| Stale Issue Detection | 4 | Label filtering, exclusion, sorting |
| Stale PR Detection | 1 | PR stale detection |
| Auto-Close Stale | 3 | Issue/PR closing, label addition |
| Health Score Calculation | 7 | All components, categories |
| Actionable Recommendations | 3 | Priority levels, sorting |
| Cleanup Stale Items | 2 | Dry run, execution |
| Health Trends | 1 | Trend data structure |
| Initialization | 4 | Token handling, error cases |

### Test Execution

```bash
# Run all repo agent tests
python3 -m pytest tests/github/test_repo_agent.py -v

# Run with coverage
python3 -m pytest tests/github/test_repo_agent.py --cov=moai_flow.github.repo_agent

# Run specific test suite
python3 -m pytest tests/github/test_repo_agent.py::TestStaleIssueDetection -v
```

---

## Data Classes

### StaleItem

```python
@dataclass
class StaleItem:
    number: int              # Issue/PR number
    title: str               # Title
    url: str                 # GitHub URL
    state: str               # open/closed
    created_at: datetime     # Creation timestamp
    updated_at: datetime     # Last update timestamp
    days_stale: int          # Days since last update
    labels: List[str]        # Label names
    assignees: List[str]     # Assignee usernames
    type: str                # "issue" or "pull_request"
```

### HealthMetrics

```python
@dataclass
class HealthMetrics:
    total_score: float                    # Overall score (0-100)
    issue_velocity_score: float           # Issue velocity (0-20)
    pr_merge_time_score: float            # PR merge time (0-20)
    stale_item_score: float               # Stale items (0-20)
    test_coverage_score: float            # Test coverage (0-20)
    contributor_activity_score: float     # Contributors (0-20)
    category: HealthCategory              # Health category
    metrics: Dict[str, Any]               # Raw metrics
```

### Recommendation

```python
@dataclass
class Recommendation:
    priority: RecommendationPriority  # CRITICAL/HIGH/MEDIUM/LOW
    category: str                     # Recommendation category
    action: str                       # Recommended action
    impact: str                       # Expected impact
    metrics: Dict[str, Any]           # Related metrics
    details: Optional[str]            # Additional details
```

---

## Usage Examples

### Example 1: Daily Health Monitoring

```python
agent = GitHubRepoAgent("org", "repo")

# Check health
health = agent.monitor_health()

if health.category == HealthCategory.CRITICAL:
    print(f"⚠️ CRITICAL: Health is {health.total_score}/100")

    # Get critical recommendations
    recs = agent.get_actionable_recommendations()
    for rec in recs:
        if rec.priority == RecommendationPriority.CRITICAL:
            print(f"  - {rec.action}")
```

### Example 2: Automated Cleanup

```python
agent = GitHubRepoAgent("org", "repo")

# Run cleanup
report = agent.cleanup_stale_items(
    warning_days=30,
    close_days=60,
    auto_close_days=90,
    dry_run=False,
    exclude_labels=["keep-open", "pinned"]
)

print(f"Cleaned up {report['summary']['closed_items']} stale items")
```

### Example 3: Health Dashboard

```python
agent = GitHubRepoAgent("org", "repo")

health = agent.monitor_health()
stale_issues = agent.get_stale_issues(days=30)
stale_prs = agent.get_stale_prs(days=14)
recommendations = agent.get_actionable_recommendations()

print(f"""
Repository Health Report
========================
Health Score: {health.total_score}/100 ({health.category.value})

Stale Items:
  - Issues (30+ days): {len(stale_issues)}
  - PRs (14+ days): {len(stale_prs)}

Top 3 Recommendations:
""")

for i, rec in enumerate(recommendations[:3], 1):
    print(f"  {i}. [{rec.priority.value}] {rec.action}")
```

---

## Integration with Existing GitHub Agents

GitHubRepoAgent works seamlessly with other GitHub agents:

```python
from moai_flow.github import (
    GitHubRepoAgent,
    GitHubIssueAgent,
    GitHubPRAgent,
)

# Repository health monitoring
repo_agent = GitHubRepoAgent("org", "repo")

# Issue creation and triage
issue_agent = GitHubIssueAgent("org", "repo")

# PR management
pr_agent = GitHubPRAgent("org", "repo")

# Workflow: Monitor health → Create issue if critical
health = repo_agent.monitor_health()

if health.category == HealthCategory.CRITICAL:
    # Create tracking issue
    issue_number = issue_agent.create_issue_from_failure(
        task_id="health-monitoring",
        agent_id="repo-health",
        error=Exception(f"Repository health is critical: {health.total_score}/100"),
        context={"health_metrics": health.metrics}
    )
```

---

## Dependencies

### Required

- **PyGithub**: GitHub API client
  ```bash
  pip install PyGithub
  ```

### Environment Variables

- `GITHUB_TOKEN`: GitHub personal access token with repo permissions

---

## Implementation Notes

### Performance Considerations

1. **API Rate Limits**: GitHub API has rate limits (5000 requests/hour for authenticated users)
2. **Pagination**: Large repositories may require pagination for issue/PR listings
3. **Caching**: Consider caching health metrics for frequently accessed data

### Security

1. **Token Security**: Store GitHub token securely (environment variable, secrets manager)
2. **Permissions**: Requires `repo` scope for read/write access
3. **Audit Trail**: All auto-close actions add detailed comments with timestamps

### Best Practices

1. **Dry Run First**: Always test with `dry_run=True` before executing cleanup
2. **Exclude Critical Labels**: Use `exclude_labels` to protect important items
3. **Progressive Warnings**: Follow 30/60/90 day pattern to give maintainers time
4. **Monitor Impact**: Track cleanup statistics to avoid over-aggressive cleanup

---

## Future Enhancements

### Potential Additions

1. **Historical Metrics Storage**: Store health metrics in time-series database
2. **Trend Analysis**: Advanced trend detection and forecasting
3. **Custom Health Formulas**: Configurable health score calculation
4. **Notification Integration**: Slack/Email alerts for health degradation
5. **Automated Issue Creation**: Auto-create tracking issues for health problems
6. **Team Performance Metrics**: Per-team health scores and recommendations

### Integration Opportunities

1. **CI/CD Integration**: Run health checks in GitHub Actions
2. **Dashboard Integration**: Export metrics to Grafana/DataDog
3. **Project Management**: Sync with Jira/Linear for issue tracking
4. **SLA Monitoring**: Track SLA compliance for issue resolution

---

## Changelog

### v1.0.0 (2025-11-29)

- ✅ Initial implementation of GitHubRepoAgent
- ✅ 8 core methods implemented
- ✅ 25 comprehensive tests (100% passing)
- ✅ Health score calculation (5 components)
- ✅ Stale detection system (30/60/90 days)
- ✅ Actionable recommendations (4 priority levels)
- ✅ Batch cleanup with dry run support
- ✅ Complete documentation and examples

---

## License

Part of MoAI-ADK GitHub automation module.

---

## Support

For issues, questions, or feature requests:
1. Check existing documentation
2. Review test cases for usage examples
3. Submit issues via GitHub issue tracker
