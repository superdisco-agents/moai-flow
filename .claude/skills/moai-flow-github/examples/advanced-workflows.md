# Advanced Workflow Examples

Complex integration scenarios combining PR management, issue triage, and health monitoring.

## Workflow 1: Complete SPEC→TDD→PR→Docs Pipeline

**Full automation from specification to documentation:**

```python
from moai_flow.github import GitHubPRAgent, GitHubIssueAgent, GitHubRepoAgent

class SPECToPRPipeline:
    """Complete automation pipeline."""

    def __init__(self, repo_owner, repo_name):
        self.pr_agent = GitHubPRAgent(repo_owner, repo_name)
        self.issue_agent = GitHubIssueAgent(repo_owner, repo_name)
        self.repo_agent = GitHubRepoAgent(repo_owner, repo_name)

    def execute(self, spec_id, branch_name, test_results):
        """Execute full pipeline."""
        try:
            # Step 1: Create PR
            pr_number = self.pr_agent.create_pr(
                branch_name=branch_name,
                base_branch="main",
                spec_id=spec_id,
                auto_labels=True
            )

            # Step 2: Add test coverage
            self.pr_agent.add_comment(
                pr_number,
                f"✅ Coverage: {test_results['coverage']}%\\n"
                f"All tests passing"
            )

            # Step 3: Request domain-specific reviews
            domain = self._extract_domain(spec_id)
            reviewers = self._get_reviewers(domain)
            self.pr_agent.set_metadata(pr_number, reviewers=reviewers)

            # Step 4: Monitor health after PR creation
            health = self.repo_agent.monitor_health()

            if health.total_score < 70:
                # Alert team about health degradation
                issue_number = self.issue_agent.create_issue_from_failure(
                    task_id="health-check",
                    agent_id="pipeline",
                    error=ValueError(f"Health: {health.total_score}"),
                    context={"health_metrics": health.to_dict()}
                )

            return {
                "pr_number": pr_number,
                "health_score": health.total_score,
                "success": True
            }

        except Exception as error:
            # Create issue for pipeline failure
            issue_number = self.issue_agent.create_issue_from_failure(
                task_id=f"pipeline-{spec_id}",
                agent_id="pipeline",
                error=error,
                context={"spec_id": spec_id, "branch": branch_name}
            )

            return {
                "issue_number": issue_number,
                "success": False
            }
```

## Workflow 2: Production Incident Response

**Automated incident management:**

```python
from moai_flow.github import GitHubIssueAgent, IssuePriority
import requests

class IncidentResponseWorkflow:
    """Automate production incident response."""

    def __init__(self, repo_owner, repo_name):
        self.issue_agent = GitHubIssueAgent(repo_owner, repo_name)

    def handle_production_error(self, error, context):
        """Handle production error with full escalation."""
        # Create critical issue
        issue_number = self.issue_agent.create_issue_from_failure(
            task_id=context['task_id'],
            agent_id=context['agent_id'],
            error=error,
            context={
                **context,
                "environment": "production",
                "user_impact": context.get('affected_users', 0),
                "tags": ["production-incident"]
            }
        )

        # Auto-triage
        metadata = self.issue_agent.auto_triage(error, context)

        # If CRITICAL, escalate
        if metadata.priority == IssuePriority.CRITICAL:
            # Page on-call engineer
            self._page_oncall(issue_number, error)

            # Add SLA tracking
            sla_hours = 4  # CRITICAL SLA
            self.issue_agent.add_comment(
                issue_number,
                f"🚨 **PRODUCTION CRITICAL**\\n\\n"
                f"⏰ SLA: {sla_hours} hours\\n"
                f"Deadline: {self._calculate_deadline(sla_hours)}"
            )

            # Assign incident commander
            self.issue_agent.set_metadata(
                issue_number,
                assignees=["incident-commander", "on-call-engineer"],
                labels=["sev-1", "incident", "production"]
            )

            # Notify Slack
            self._notify_slack(
                f"🚨 CRITICAL incident #{issue_number}\\n"
                f"Error: {str(error)}\\n"
                f"Affected users: {context.get('affected_users', 'unknown')}"
            )

        return issue_number

    def _page_oncall(self, issue_number, error):
        """Page on-call engineer via PagerDuty."""
        requests.post(
            "https://api.pagerduty.com/incidents",
            headers={"Authorization": f"Token {os.getenv('PAGERDUTY_TOKEN')}"},
            json={
                "incident": {
                    "type": "incident",
                    "title": f"GitHub Issue #{issue_number}: {str(error)[:100]}",
                    "body": {"type": "incident_body", "details": str(error)},
                    "urgency": "high"
                }
            }
        )
```

## Workflow 3: Multi-Repository Health Monitoring

**Monitor health across multiple repositories:**

```python
from moai_flow.github import GitHubRepoAgent, HealthCategory
from datetime import datetime

class MultiRepoHealthMonitor:
    """Monitor health across organization repositories."""

    def __init__(self, repos):
        self.repos = repos
        self.agents = {
            repo: GitHubRepoAgent(repo.split("/")[0], repo.split("/")[1])
            for repo in repos
        }

    def daily_health_check(self):
        """Daily health monitoring across all repos."""
        results = []

        for repo, agent in self.agents.items():
            # Calculate health
            health = agent.monitor_health()

            # Get recommendations
            recommendations = agent.get_actionable_recommendations()

            results.append({
                "repo": repo,
                "score": health.total_score,
                "category": health.category.value,
                "critical_recs": [
                    r for r in recommendations
                    if r.priority == "critical"
                ]
            })

            # Alert if critical
            if health.category == HealthCategory.CRITICAL:
                self._send_alert(repo, health, recommendations)

            # Run cleanup
            cleanup_report = agent.cleanup_stale_items(
                warning_days=30,
                close_days=60,
                auto_close_days=90,
                dry_run=False,
                exclude_labels=["keep-open", "security"]
            )

            self._log_cleanup(repo, cleanup_report)

        # Generate dashboard
        self._generate_dashboard(results)

        return results

    def _generate_dashboard(self, results):
        """Generate health dashboard."""
        report = f"""
# Organization Health Dashboard
**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary
- **Total Repositories**: {len(results)}
- **Average Health**: {sum(r['score'] for r in results) / len(results):.1f}/100
- **Critical Repos**: {sum(1 for r in results if r['category'] == 'critical')}

## Repository Scores
| Repository | Score | Category | Critical Recommendations |
|------------|-------|----------|-------------------------|
"""
        for r in sorted(results, key=lambda x: x['score']):
            critical_count = len(r['critical_recs'])
            report += f"| {r['repo']} | {r['score']}/100 | {r['category']} | {critical_count} |\\n"

        # Save dashboard
        with open(".moai/reports/health-dashboard.md", "w") as f:
            f.write(report)
```

## Workflow 4: Automated Code Review Assignment

**Intelligent reviewer assignment based on code changes:**

```python
from moai_flow.github import GitHubPRAgent
import re

class AutoReviewAssignment:
    """Automatically assign reviewers based on code changes."""

    # Code ownership rules
    OWNERSHIP_RULES = {
        r"api/.*": ["backend-team", "api-expert"],
        r"ui/.*": ["frontend-team", "ui-expert"],
        r"database/.*": ["database-admin", "backend-team"],
        r"auth/.*": ["security-expert", "backend-team"],
        r".*\\.test\\..*": ["qa-team"],
        r"docs/.*": ["tech-writer"]
    }

    def __init__(self, repo_owner, repo_name):
        self.pr_agent = GitHubPRAgent(repo_owner, repo_name)

    def assign_reviewers(self, pr_number, file_changes):
        """Assign reviewers based on changed files."""
        reviewers = set()

        for file_change in file_changes:
            path = file_change.path

            # Match against ownership rules
            for pattern, owners in self.OWNERSHIP_RULES.items():
                if re.match(pattern, path):
                    reviewers.update(owners)

        # Always include tech lead for large changes
        total_changes = sum(f.additions + f.deletions for f in file_changes)
        if total_changes > 500:
            reviewers.add("tech-lead")

        # Assign
        if reviewers:
            self.pr_agent.set_metadata(
                pr_number,
                reviewers=list(reviewers)
            )

            self.pr_agent.add_comment(
                pr_number,
                f"🤖 Auto-assigned reviewers based on code changes:\\n" +
                "\\n".join([f"- @{r}" for r in reviewers])
            )

        return list(reviewers)
```

## Workflow 5: Progressive Stale Item Cleanup

**Tiered cleanup with notifications:**

```python
from moai_flow.github import GitHubRepoAgent
from datetime import datetime, timedelta

class ProgressiveCleanupWorkflow:
    """Tiered stale item cleanup with user notifications."""

    def __init__(self, repo_owner, repo_name):
        self.repo_agent = GitHubRepoAgent(repo_owner, repo_name)

    def execute_cleanup(self):
        """Execute three-tier cleanup workflow."""
        # Tier 1: 30-day warning
        tier1_items = self.repo_agent.get_stale_issues(days=30)
        for item in tier1_items:
            if "stale" not in item.labels:
                self._add_stale_label(item)

        # Tier 2: 60-day close warning
        tier2_items = self.repo_agent.get_stale_issues(days=60)
        for item in tier2_items:
            if "close-warning" not in item.labels:
                self._add_close_warning(item)

        # Tier 3: 90-day auto-close
        tier3_items = self.repo_agent.get_stale_issues(days=90)
        closed_count = 0
        for item in tier3_items:
            if "keep-open" not in item.labels:
                success = self.repo_agent.auto_close_stale(
                    item,
                    reason="90 days of inactivity"
                )
                if success:
                    closed_count += 1

        return {
            "tier1_warned": len(tier1_items),
            "tier2_warned": len(tier2_items),
            "tier3_closed": closed_count
        }

    def _add_close_warning(self, item):
        """Add close warning to item."""
        self.repo_agent._add_close_warning(item, close_days=60)
```

## Workflow 6: Security Issue Escalation

**Automated security issue handling:**

```python
from moai_flow.github import GitHubIssueAgent, IssuePriority

class SecurityEscalationWorkflow:
    """Handle security issues with special escalation."""

    SECURITY_KEYWORDS = [
        "xss", "sql injection", "csrf", "authentication bypass",
        "privilege escalation", "data leak", "vulnerability"
    ]

    def __init__(self, repo_owner, repo_name):
        self.issue_agent = GitHubIssueAgent(repo_owner, repo_name)

    def handle_security_issue(self, error, context):
        """Create and escalate security issue."""
        # Create issue
        issue_number = self.issue_agent.create_issue_from_failure(
            task_id=context['task_id'],
            agent_id="security-scanner",
            error=error,
            context={
                **context,
                "tags": ["security"],
                "environment": context.get("environment", "unknown")
            }
        )

        # Check if security-related
        error_text = str(error).lower()
        is_security = any(
            keyword in error_text
            for keyword in self.SECURITY_KEYWORDS
        )

        if is_security or "security" in context.get("tags", []):
            # Escalate to CRITICAL
            self.issue_agent.update_priority(
                issue_number,
                priority=IssuePriority.CRITICAL,
                reason="Security vulnerability detected"
            )

            # Assign security team
            self.issue_agent.set_metadata(
                issue_number,
                assignees=["security-team", "cto"],
                labels=["security", "critical", "immediate-action"]
            )

            # Notify security team
            self._notify_security_team(issue_number, error)

            # Create private security advisory (if GitHub Security Advisories enabled)
            self._create_security_advisory(issue_number, error)

        return issue_number

    def _notify_security_team(self, issue_number, error):
        """Notify security team via secure channel."""
        # Send encrypted notification to security@company.com
        send_encrypted_email(
            to="security@company.com",
            subject=f"[CRITICAL] Security Issue #{issue_number}",
            body=f"Security vulnerability detected:\\n{str(error)}"
        )
```

---

**Related Documentation**:
- [Basic GitHub Usage](basic-github.md)
- [Multi-Agent PR Workflows](multi-agent-pr.md)
- [Integration Patterns Module](../modules/integration-patterns.md)
