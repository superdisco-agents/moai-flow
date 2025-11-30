# Workflow Automation & Repository Health Monitoring

Comprehensive repository health tracking, stale item detection, automated cleanup, and actionable recommendations for proactive maintenance.

## Overview

The GitHubRepoAgent provides enterprise-grade repository health monitoring with automated cleanup workflows, health scoring, and prioritized recommendations for improvement.

## Core Capabilities

### 1. Health Metrics Calculation

**Five-Metric System** (100 points total):

| Metric | Weight | Target | Measurement |
|--------|--------|--------|-------------|
| Issue Velocity | 20% | 10+ closed/week | Issues closed per week in last 4 weeks |
| PR Merge Time | 20% | ≤ 2 days | Average days from creation to merge |
| Stale Items | 20% | 0 items | Issues/PRs inactive for 60+ days |
| Contributor Activity | 20% | 5+ contributors | Unique contributors in last 4 weeks |
| Test Coverage Trend | 20% | Positive trend | Change in coverage percentage |

**Scoring Formulas**:

```python
# Issue Velocity (20 points max)
# Target: 10 issues/week = 20 points
velocity_score = min(issues_per_week / 10 * 20, 20)

# PR Merge Time (20 points max)
# Target: ≤2 days = 20 points, >10 days = 0 points
if avg_days <= 2:
    merge_score = 20
elif avg_days >= 10:
    merge_score = 0
else:
    merge_score = 20 * (1 - (avg_days - 2) / 8)

# Stale Items (20 points max)
# Target: 0 stale = 20 points, 50+ stale = 0 points
stale_score = max(0, 20 * (1 - stale_count / 50))

# Contributor Activity (20 points max)
# Target: 5 contributors = 20 points
activity_score = min(contributor_count / 5 * 20, 20)

# Test Coverage Trend (20 points max)
# Positive trend = 20, stable = 10, negative = 0
if trend > 0: coverage_score = 20
elif trend == 0: coverage_score = 10
else: coverage_score = 0
```

**Health Categories**:

| Score Range | Category | Meaning |
|-------------|----------|---------|
| 90-100 | EXCELLENT | Outstanding repository health |
| 75-89 | GOOD | Healthy, minor improvements needed |
| 60-74 | FAIR | Moderate issues, action recommended |
| 40-59 | POOR | Significant issues, urgent action needed |
| 0-39 | CRITICAL | Severe issues, immediate intervention required |

### 2. Stale Item Detection

**Definition**: Items (issues or PRs) with no activity for specified threshold (default: 60 days).

**Detection Algorithm**:

```python
def get_stale_issues(days=30):
    """Find issues stale for N+ days."""
    cutoff_date = datetime.now() - timedelta(days=days)

    stale_items = []
    for issue in repo.get_issues(state="open"):
        if not issue.pull_request and issue.updated_at < cutoff_date:
            days_stale = (datetime.now() - issue.updated_at).days
            stale_items.append(StaleItem(
                number=issue.number,
                title=issue.title,
                days_stale=days_stale,
                ...
            ))

    return sorted(stale_items, key=lambda x: x.days_stale, reverse=True)
```

**Filtering Options**:

```python
# Filter by labels
stale_issues = agent.get_stale_issues(
    days=30,
    labels=["bug", "enhancement"],  # Only these labels
    exclude_labels=["keep-open", "pinned"]  # Exclude these
)
```

### 3. Three-Tier Cleanup Workflow

**Progressive Warning System**:

```
30 days → Add "stale" label
60 days → Add close warning comment
90 days → Auto-close with comment
```

**Implementation**:

```python
cleanup_report = agent.cleanup_stale_items(
    warning_days=30,      # Tier 1: Warning label
    close_days=60,        # Tier 2: Close warning comment
    auto_close_days=90,   # Tier 3: Auto-close
    dry_run=True,         # Preview mode (recommended)
    exclude_labels=["keep-open", "pinned", "security"]
)

# Review dry run results
print(f"Would add warnings: {cleanup_report['summary']['warning_labels']}")
print(f"Would warn close: {cleanup_report['summary']['close_warnings']}")
print(f"Would close: {cleanup_report['summary']['would_close_items']}")

# Execute if acceptable
if user_approved:
    cleanup_report = agent.cleanup_stale_items(
        warning_days=30,
        close_days=60,
        auto_close_days=90,
        dry_run=False  # Execute
    )
```

**Generated Comments**:

**Tier 1 (Warning Label)**:
- Adds `stale` label to issue/PR
- No comment (silent warning)

**Tier 2 (Close Warning)**:
```markdown
⚠️ **Stale Item Warning**

This issue has been inactive for 60 days and will be automatically closed if there is no activity within the next 30 days.

If this is still relevant, please:
- Add a comment to keep it active
- Update the description or add new information
- Add the `keep-open` label to prevent auto-closure

Last activity: 2025-09-30
```

**Tier 3 (Auto-Close)**:
```markdown
This issue has been automatically closed due to inactivity.

**Reason:** 90 days of inactivity
**Last activity:** 2025-08-30 (90 days ago)

If this issue is still relevant, please reopen it with updated information.
```

### 4. Actionable Recommendations

**Prioritized Recommendation System**:

```python
recommendations = agent.get_actionable_recommendations()

# Returns prioritized list:
# CRITICAL > HIGH > MEDIUM > LOW
```

**Recommendation Categories**:

| Category | Trigger | Example |
|----------|---------|---------|
| Stale Management | 20+ stale issues | "Address 25 stale issues (30+ days inactive)" |
| Issue Velocity | Score < 10 | "Improve issue resolution rate" |
| PR Merge Time | Score < 10 | "Reduce pull request merge time" |
| Test Coverage | Score < 15 | "Improve test coverage" |
| Contributor Activity | Score < 10 | "Increase contributor engagement" |

**Recommendation Structure**:

```python
@dataclass
class Recommendation:
    priority: RecommendationPriority  # CRITICAL, HIGH, MEDIUM, LOW
    category: str                     # stale_management, issue_velocity, etc.
    action: str                       # What to do
    impact: str                       # Expected improvement
    metrics: Dict[str, Any]           # Supporting data
    details: Optional[str]            # Additional context
```

**Example Output**:

```
[CRITICAL] Address 15 stale pull requests (30+ days inactive)
  Impact: Improve PR merge time and contributor satisfaction
  Details: Stale PRs block contributors and hurt project momentum

[HIGH] Address 25 stale issues (30+ days inactive)
  Impact: Improve issue velocity score and reduce clutter
  Details: Consider triaging, closing, or updating these issues

[HIGH] Improve issue resolution rate
  Impact: Increase health score by up to 10 points
  Details: Target: Close 80%+ of new issues within 30 days

[MEDIUM] Improve test coverage
  Impact: Increase health score and code quality
  Details: Target: 80%+ test coverage across the project
```

### 5. Health Trend Analysis

**Comparison Mechanism**:

```python
# Calculate current metrics
current_metrics = analyzer.calculate_health_metrics()

# Load historical metrics
historical_metrics = load_historical_metrics()

# Analyze trend
comparison = analyzer.analyze_trend(current_metrics, historical_metrics)

print(f"Trend: {comparison.trend.value}")  # improving, stable, degrading
print(f"Change: {comparison.change_percentage}%")
print(f"Improvements: {comparison.improvements}")
print(f"Degradations: {comparison.degradations}")
```

**Trend Detection**:

```python
# Change > 5% → IMPROVING
# Change < -5% → DEGRADING
# -5% ≤ Change ≤ 5% → STABLE
```

### 6. Manual Stale Item Closure

**Individual Item Control**:

```python
# Get stale items
stale_items = agent.get_stale_issues(days=90)

# Manually close specific item
for item in stale_items:
    if should_close(item):  # Custom logic
        success = agent.auto_close_stale(
            item,
            reason="Closing due to 90+ days of inactivity",
            label="auto-closed"
        )
```

## Advanced Patterns

### Pattern 1: Scheduled Health Monitoring

**Daily Cron Job**:

```python
def daily_health_check():
    """Daily repository health monitoring."""
    repo_agent = GitHubRepoAgent("org", "repo")

    # Calculate metrics
    health = repo_agent.monitor_health()

    # Log metrics
    save_health_metrics(health)

    # Alert if critical
    if health.category in [HealthCategory.POOR, HealthCategory.CRITICAL]:
        send_alert(f"⚠️ Repository health: {health.total_score}/100")

        # Get recommendations
        recommendations = repo_agent.get_actionable_recommendations()
        critical_recs = [r for r in recommendations if r.priority == RecommendationPriority.CRITICAL]

        if critical_recs:
            notify_team(critical_recs)

    # Run automated cleanup
    cleanup_report = repo_agent.cleanup_stale_items(
        warning_days=30,
        close_days=60,
        auto_close_days=90,
        dry_run=False,
        exclude_labels=["keep-open", "security", "pinned"]
    )

    log_cleanup_results(cleanup_report)
```

### Pattern 2: Health Dashboard Generation

**Markdown Report**:

```python
def generate_health_dashboard():
    """Generate comprehensive health dashboard."""
    repo_agent = GitHubRepoAgent("org", "repo")

    # Get all metrics
    health = repo_agent.monitor_health()
    stale_issues = repo_agent.get_stale_issues(days=30)
    stale_prs = repo_agent.get_stale_prs(days=14)
    recommendations = repo_agent.get_actionable_recommendations()

    # Generate markdown
    report = f"""
# Repository Health Report
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Overall Health: {health.total_score}/100 ({health.category.value})

### Component Scores
| Component | Score | Status |
|-----------|-------|--------|
| Issue Velocity | {health.issue_velocity_score}/20 | {"✅" if health.issue_velocity_score >= 15 else "⚠️"} |
| PR Merge Time | {health.pr_merge_time_score}/20 | {"✅" if health.pr_merge_time_score >= 15 else "⚠️"} |
| Stale Items | {health.stale_item_score}/20 | {"✅" if health.stale_item_score >= 15 else "⚠️"} |
| Test Coverage | {health.test_coverage_score}/20 | {"✅" if health.test_coverage_score >= 15 else "⚠️"} |
| Contributor Activity | {health.contributor_activity_score}/20 | {"✅" if health.contributor_activity_score >= 15 else "⚠️"} |

### Stale Items Summary
- **Stale Issues (30+ days):** {len(stale_issues)}
- **Stale PRs (14+ days):** {len(stale_prs)}

### Top Recommendations
"""

    for i, rec in enumerate(recommendations[:5], 1):
        report += f"{i}. [{rec.priority.value.upper()}] {rec.action}\n"

    # Save or publish report
    save_report(report)
    return report
```

### Pattern 3: Proactive Issue Creation

**Auto-Create Health Issue**:

```python
def check_and_report_health_degradation():
    """Automatically create issue if health degrades."""
    repo_agent = GitHubRepoAgent("org", "repo")
    issue_agent = GitHubIssueAgent("org", "repo")

    # Load historical metrics
    historical = load_historical_metrics()

    # Calculate current
    current = repo_agent.monitor_health()

    # Analyze trend
    analyzer = HealthMetricsAnalyzer("org", "repo")
    comparison = analyzer.analyze_trend(current, historical)

    # Create issue if degrading significantly
    if comparison.trend == HealthTrend.DEGRADING and comparison.change_percentage < -10:
        # Create health degradation issue
        issue_number = issue_agent.create_issue_from_failure(
            task_id="health-monitoring",
            agent_id="repo-health-agent",
            error=ValueError(f"Health degraded by {abs(comparison.change_percentage)}%"),
            context={
                "component": "repository-health",
                "environment": "production",
                "degradations": comparison.degradations,
                "current_score": current.total_score,
                "previous_score": comparison.previous.total_score
            }
        )

        # Add detailed analysis
        issue_agent.add_context(
            issue_number,
            environment={
                "degraded_metrics": comparison.degradations,
                "current_scores": {
                    "issue_velocity": current.issue_velocity_score,
                    "pr_merge_time": current.pr_merge_time_score,
                    "stale_items": current.stale_item_score
                }
            }
        )

        return issue_number
```

### Pattern 4: Custom Stale Rules

**Component-Specific Thresholds**:

```python
def cleanup_with_custom_rules():
    """Apply different stale thresholds based on component."""
    repo_agent = GitHubRepoAgent("org", "repo")

    # Security issues: Never auto-close
    security_issues = repo_agent.get_stale_issues(
        days=180,
        labels=["security"]
    )
    # Manual review only for security

    # Documentation: Aggressive cleanup
    doc_issues = repo_agent.get_stale_issues(
        days=30,
        labels=["documentation"]
    )
    for item in doc_issues:
        repo_agent.auto_close_stale(item, reason="Documentation issue stale for 30+ days")

    # Feature requests: Medium timeline
    feature_requests = repo_agent.get_stale_issues(
        days=60,
        labels=["enhancement"]
    )
    cleanup_report = repo_agent.cleanup_stale_items(
        warning_days=60,
        close_days=90,
        auto_close_days=120,
        dry_run=False,
        exclude_labels=["security", "pinned"]
    )
```

## API Reference

### GitHubRepoAgent

**Constructor**:

```python
def __init__(
    self,
    repo_owner: str,
    repo_name: str,
    github_token: Optional[str] = None,
    stale_days: int = 60
)
```

**Methods**:

#### monitor_health()

```python
def monitor_health() -> HealthMetrics
```

Returns comprehensive health metrics with 5-component scoring.

#### calculate_health_score()

```python
def calculate_health_score() -> float
```

Returns overall health score (0-100).

#### get_stale_issues()

```python
def get_stale_issues(
    days: int = 30,
    labels: Optional[List[str]] = None,
    exclude_labels: Optional[List[str]] = None
) -> List[StaleItem]
```

#### get_stale_prs()

```python
def get_stale_prs(
    days: int = 30,
    labels: Optional[List[str]] = None,
    exclude_labels: Optional[List[str]] = None
) -> List[StaleItem]
```

#### cleanup_stale_items()

```python
def cleanup_stale_items(
    warning_days: int = 30,
    close_days: int = 60,
    auto_close_days: int = 90,
    dry_run: bool = True,
    exclude_labels: Optional[List[str]] = None
) -> Dict[str, Any]
```

#### get_actionable_recommendations()

```python
def get_actionable_recommendations() -> List[Recommendation]
```

#### auto_close_stale()

```python
def auto_close_stale(
    item: StaleItem,
    reason: str = "Automatically closed due to inactivity",
    label: str = "stale"
) -> bool
```

### HealthMetricsAnalyzer

**Constructor**:

```python
def __init__(
    self,
    repo_owner: str,
    repo_name: str,
    github_token: Optional[str] = None,
    stale_days: int = 60
)
```

**Methods**:

#### calculate_health_metrics()

```python
def calculate_health_metrics(
    lookback_weeks: int = 4,
    include_detailed: bool = True
) -> HealthMetrics
```

#### analyze_trend()

```python
def analyze_trend(
    current_metrics: HealthMetrics,
    historical_metrics: List[HealthMetrics]
) -> HealthComparison
```

---

**Related Documentation**:
- [Multi-Agent PR Module](multi-agent-pr.md)
- [Collaborative Review Module](collaborative-review.md)
- [Integration Patterns Module](integration-patterns.md)
