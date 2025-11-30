# Integration Patterns

Multi-agent coordination patterns for GitHub workflows, MoAI-ADK integration, and enterprise automation.

## Overview

This module provides proven integration patterns for coordinating GitHub operations across multi-agent systems, connecting with MoAI-ADK workflows, and implementing enterprise-grade automation.

## MoAI-ADK Integration Patterns

### Pattern 1: SPEC→TDD→PR Workflow

**Full automation from specification to pull request:**

```python
from moai_flow.github import GitHubPRAgent

def on_spec_complete(spec_id):
    """Phase 1: SPEC completed by manager-spec."""
    return spec_id

def on_tdd_complete(spec_id, branch_name, test_coverage):
    """Phase 2: TDD cycle completed by manager-tdd."""
    pr_agent = GitHubPRAgent("org", "repo")

    # Create PR with SPEC integration
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
        f"## Test Coverage\\n\\n✅ Coverage: {test_coverage}%\\nTarget: >= 90%"
    )

    # Request reviews based on SPEC domain
    domain = extract_domain_from_spec(spec_id)
    if domain == "backend":
        reviewers = ["backend-expert", "security-expert"]
    elif domain == "frontend":
        reviewers = ["frontend-expert", "ui-expert"]
    else:
        reviewers = ["tech-lead"]

    pr_agent.set_metadata(pr_number, reviewers=reviewers)

    return pr_number
```

### Pattern 2: Task Failure → Issue Creation

**Automatic issue reporting from agent failures:**

```python
from moai_flow.github import GitHubIssueAgent

def on_agent_task_failure(task_result):
    """Triggered when any agent task fails."""
    issue_agent = GitHubIssueAgent("org", "repo")

    # Extract error details
    error = task_result.error
    context = {
        "task_id": task_result.task_id,
        "agent_id": task_result.agent_id,
        "component": task_result.metadata.get("component"),
        "environment": task_result.metadata.get("environment", "development"),
        "frequency": count_similar_failures(error)
    }

    # Create issue with auto-triage
    issue_number = issue_agent.create_issue_from_failure(
        task_id=context["task_id"],
        agent_id=context["agent_id"],
        error=error,
        context=context,
        spec_id=task_result.metadata.get("spec_id")
    )

    # Check for similar issues
    similar = issue_agent.get_similar_issues(error, limit=3)
    if similar:
        issue_agent.add_comment(
            issue_number,
            f"⚠️ Possibly related to: {', '.join([f'#{n}' for n in similar])}"
        )

    return issue_number
```

### Pattern 3: Multi-Agent PR Coordination

**Backend + Frontend + Database changes:**

```python
from moai_flow.github import GitHubPRAgent

def create_coordinated_prs(spec_id, components):
    """Create coordinated PRs for multi-component features."""
    pr_agent = GitHubPRAgent("org", "repo")

    prs = {}

    # Backend PR
    if "backend" in components:
        prs["backend"] = pr_agent.create_pr(
            branch_name=f"feature/{spec_id}-backend",
            spec_id=spec_id,
            auto_labels=True
        )

    # Frontend PR
    if "frontend" in components:
        prs["frontend"] = pr_agent.create_pr(
            branch_name=f"feature/{spec_id}-frontend",
            spec_id=spec_id,
            auto_labels=True
        )

    # Database PR
    if "database" in components:
        prs["database"] = pr_agent.create_pr(
            branch_name=f"feature/{spec_id}-database",
            spec_id=spec_id,
            auto_labels=True
        )

    # Cross-reference all PRs
    for component, pr_number in prs.items():
        other_prs = [f"#{n} ({c})" for c, n in prs.items() if c != component]
        pr_agent.add_comment(
            pr_number,
            f"🔗 **Related PRs**: {', '.join(other_prs)}\\n\\n"
            f"**Merge Order**: {get_merge_order(prs)}"
        )

    return prs
```

## GitHub Actions Integration

### Pattern 4: CI/CD Triggered by PR Creation

**GitHub Actions workflow triggered by PR Agent:**

```yaml
# .github/workflows/pr-validation.yml
name: PR Validation
on:
  pull_request:
    types: [opened, synchronize]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Extract SPEC ID
        id: spec
        run: |
          SPEC_ID=$(grep -oP 'Implements: \K\S+' <<< "${{ github.event.pull_request.body }}")
          echo "spec_id=$SPEC_ID" >> $GITHUB_OUTPUT

      - name: Run TRUST 5 Validation
        run: |
          # Test coverage (T)
          pytest --cov=. --cov-report=term-missing

          # Readability (R)
          ruff check .

          # Unified formatting (U)
          black --check .

          # Security (S)
          bandit -r .

          # Trackable (T)
          git log --oneline -n 10
```

### Pattern 5: Issue Triage Trigger

**Automated testing triggered by critical issues:**

```yaml
# .github/workflows/issue-triage.yml
name: Issue Triage
on:
  issues:
    types: [labeled]

jobs:
  handle-critical:
    if: contains(github.event.issue.labels.*.name, 'priority:critical')
    runs-on: ubuntu-latest
    steps:
      - name: Notify On-Call
        run: |
          curl -X POST https://api.pagerduty.com/incidents \
            -H "Authorization: Token ${{ secrets.PAGERDUTY_TOKEN }}" \
            -d '{"incident": {"type": "incident", "title": "${{ github.event.issue.title }}"}}'

      - name: Run Emergency Tests
        run: |
          pytest tests/critical/
```

## Enterprise Automation Patterns

### Pattern 6: Scheduled Health Monitoring

**Daily health check with alerting:**

```python
# cron: 0 9 * * *  # Every day at 9 AM
from moai_flow.github import GitHubRepoAgent, HealthCategory

def daily_health_check():
    """Daily repository health monitoring."""
    repos = ["org/repo1", "org/repo2", "org/repo3"]

    results = []
    for repo_full_name in repos:
        owner, name = repo_full_name.split("/")
        agent = GitHubRepoAgent(owner, name)

        health = agent.monitor_health()
        results.append({
            "repo": repo_full_name,
            "score": health.total_score,
            "category": health.category.value,
            "trend": health.trend.value
        })

        # Alert if critical
        if health.category == HealthCategory.CRITICAL:
            send_slack_alert(
                f"🚨 {repo_full_name} health: {health.total_score}/100 (CRITICAL)"
            )

            # Get recommendations
            recommendations = agent.get_actionable_recommendations()
            critical_recs = [r for r in recommendations if r.priority == "critical"]

            if critical_recs:
                send_slack_message(
                    f"**Critical Actions for {repo_full_name}**:\\n" +
                    "\\n".join([f"- {r.action}" for r in critical_recs])
                )

    # Generate daily report
    generate_health_dashboard(results)
    return results
```

### Pattern 7: Auto-Cleanup Workflow

**Weekly stale item cleanup:**

```python
# cron: 0 0 * * 0  # Every Sunday at midnight
from moai_flow.github import GitHubRepoAgent

def weekly_cleanup():
    """Weekly stale item cleanup across repositories."""
    repos = get_all_repositories()

    for repo in repos:
        agent = GitHubRepoAgent(repo.owner, repo.name)

        # Component-specific rules
        if repo.type == "core":
            # More aggressive cleanup for core repos
            cleanup_report = agent.cleanup_stale_items(
                warning_days=14,
                close_days=30,
                auto_close_days=60,
                dry_run=False,
                exclude_labels=["keep-open", "security"]
            )
        else:
            # Standard cleanup for other repos
            cleanup_report = agent.cleanup_stale_items(
                warning_days=30,
                close_days=60,
                auto_close_days=90,
                dry_run=False,
                exclude_labels=["keep-open", "pinned", "security"]
            )

        # Log results
        log_cleanup(repo.full_name, cleanup_report)

        # Notify if significant cleanup occurred
        if cleanup_report['summary']['closed_items'] > 20:
            notify_team(
                f"Weekly cleanup for {repo.full_name}: "
                f"Closed {cleanup_report['summary']['closed_items']} stale items"
            )
```

### Pattern 8: Intelligent Escalation

**Auto-escalate critical production issues:**

```python
from moai_flow.github import GitHubIssueAgent, IssuePriority

def escalate_if_critical(issue_number):
    """Automatically escalate critical issues."""
    issue_agent = GitHubIssueAgent("org", "repo")

    # Get issue details
    issue = repo.get_issue(issue_number)

    # Check priority label
    priority_labels = [l.name for l in issue.labels if "priority:" in l.name]

    if "priority:critical" in priority_labels:
        # Production critical escalation
        if "production" in [l.name for l in issue.labels]:
            # Page on-call engineer
            page_oncall_engineer(issue_number)

            # Add escalation comment
            issue_agent.add_comment(
                issue_number,
                "🚨 **ESCALATION**: Production critical issue. On-call engineer paged."
            )

            # Update SLA tracking
            sla_hours = 4  # CRITICAL SLA = 4 hours
            issue_agent.add_comment(
                issue_number,
                f"⏰ **SLA**: Must be resolved within {sla_hours} hours\\n"
                f"Deadline: {calculate_deadline(sla_hours)}"
            )

            # Assign to incident commander
            issue_agent.set_metadata(
                issue_number,
                assignees=["incident-commander", "on-call-engineer"],
                labels=["incident", "sev-1"]
            )
```

## External Service Integration

### Pattern 9: Slack Integration

**Post PR and issue notifications to Slack:**

```python
import requests

def notify_slack_pr_created(pr_number, spec_id):
    """Notify Slack channel when PR is created."""
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")

    message = {
        "text": f"🔔 New Pull Request",
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*New PR Created*\\n"
                            f"PR: <https://github.com/org/repo/pull/{pr_number}|#{pr_number}>\\n"
                            f"SPEC: {spec_id}"
                }
            }
        ]
    }

    requests.post(webhook_url, json=message)
```

### Pattern 10: Jira Integration

**Sync GitHub issues with Jira tickets:**

```python
from jira import JIRA

def sync_issue_to_jira(github_issue_number):
    """Create Jira ticket from GitHub issue."""
    # Get GitHub issue details
    issue_agent = GitHubIssueAgent("org", "repo")
    github_issue = repo.get_issue(github_issue_number)

    # Get priority from labels
    priority = extract_priority_from_labels(github_issue.labels)

    # Create Jira ticket
    jira = JIRA(server="https://company.atlassian.net", token=os.getenv("JIRA_TOKEN"))

    jira_issue = jira.create_issue(
        project="PROJ",
        summary=github_issue.title,
        description=github_issue.body,
        issuetype={"name": "Bug"},
        priority={"name": map_priority_to_jira(priority)}
    )

    # Link back to GitHub
    issue_agent.add_comment(
        github_issue_number,
        f"🔗 Jira ticket created: [{jira_issue.key}](https://company.atlassian.net/browse/{jira_issue.key})"
    )

    return jira_issue.key
```

## Monitoring & Observability

### Pattern 11: Metrics Collection

**Collect GitHub metrics for dashboards:**

```python
from moai_flow.github import HealthMetricsAnalyzer

def collect_metrics():
    """Collect metrics for monitoring dashboard."""
    repos = get_all_repositories()

    metrics = []
    for repo in repos:
        analyzer = HealthMetricsAnalyzer(repo.owner, repo.name)

        health = analyzer.calculate_health_metrics(
            lookback_weeks=4,
            include_detailed=True
        )

        metrics.append({
            "timestamp": datetime.now().isoformat(),
            "repo": f"{repo.owner}/{repo.name}",
            "health_score": health.total_score,
            "issue_velocity": health.issue_velocity,
            "pr_merge_time": health.pr_merge_time,
            "stale_count": health.stale_count,
            "contributor_activity": health.contributor_activity,
            "test_coverage_trend": health.test_coverage_trend
        })

    # Store in time-series database
    store_metrics_in_influxdb(metrics)

    # Update Grafana dashboard
    update_grafana_dashboard(metrics)

    return metrics
```

### Pattern 12: Alerting Rules

**Define alerting thresholds:**

```python
ALERT_RULES = {
    "health_score": {
        "critical": 40,   # Alert if score < 40
        "warning": 60     # Warn if score < 60
    },
    "stale_items": {
        "critical": 50,   # Alert if > 50 stale items
        "warning": 30     # Warn if > 30 stale items
    },
    "pr_merge_time": {
        "critical": 10,   # Alert if avg > 10 days
        "warning": 7      # Warn if avg > 7 days
    }
}

def check_alert_conditions(health):
    """Check if health metrics trigger alerts."""
    alerts = []

    if health.total_score < ALERT_RULES["health_score"]["critical"]:
        alerts.append({
            "severity": "critical",
            "metric": "health_score",
            "value": health.total_score,
            "threshold": ALERT_RULES["health_score"]["critical"]
        })

    if health.stale_count > ALERT_RULES["stale_items"]["critical"]:
        alerts.append({
            "severity": "critical",
            "metric": "stale_items",
            "value": health.stale_count,
            "threshold": ALERT_RULES["stale_items"]["critical"]
        })

    return alerts
```

---

**Related Documentation**:
- [Multi-Agent PR Module](multi-agent-pr.md)
- [Collaborative Review Module](collaborative-review.md)
- [Workflow Automation Module](workflow-automation.md)
