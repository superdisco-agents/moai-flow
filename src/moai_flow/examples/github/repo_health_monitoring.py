"""Example usage of GitHubRepoAgent for repository health monitoring.

This example demonstrates how to use GitHubRepoAgent to:
- Monitor repository health scores
- Detect and manage stale issues and PRs
- Auto-close stale items with progressive warnings
- Get actionable recommendations for improvement
- Track health trends over time

Requirements:
    - PyGithub: pip install PyGithub
    - GitHub token with repo access (read/write)

Environment Variables:
    GITHUB_TOKEN: Your GitHub personal access token
"""

import os
from datetime import datetime
from moai_flow.github import (
    GitHubRepoAgent,
    HealthCategory,
    RecommendationPriority,
)


def main():
    """Main example demonstrating GitHubRepoAgent usage."""

    # Initialize agent (uses GITHUB_TOKEN environment variable)
    agent = GitHubRepoAgent(
        repo_owner="your-org",
        repo_name="your-repo"
    )

    print("=" * 80)
    print("GitHub Repository Health Monitoring Example")
    print("=" * 80)
    print()

    # Example 1: Monitor overall repository health
    print("Example 1: Repository Health Score")
    print("-" * 80)

    health = agent.monitor_health()
    print(f"Overall Health: {health.total_score}/100 ({health.category.value})")
    print()
    print("Component Scores:")
    print(f"  - Issue Velocity:        {health.issue_velocity_score}/20")
    print(f"  - PR Merge Time:         {health.pr_merge_time_score}/20")
    print(f"  - Stale Items:           {health.stale_item_score}/20")
    print(f"  - Test Coverage:         {health.test_coverage_score}/20")
    print(f"  - Contributor Activity:  {health.contributor_activity_score}/20")
    print()

    # Example 2: Find stale issues
    print("Example 2: Stale Issue Detection")
    print("-" * 80)

    # Find issues stale for 30+ days
    stale_issues = agent.get_stale_issues(days=30)
    print(f"Found {len(stale_issues)} stale issues (30+ days inactive)")

    if stale_issues:
        print("\nTop 5 stalest issues:")
        for issue in stale_issues[:5]:
            print(f"  #{issue.number}: {issue.title}")
            print(f"    Last updated: {issue.updated_at.strftime('%Y-%m-%d')} ({issue.days_stale} days ago)")
            print(f"    URL: {issue.url}")
            print()

    # Example 3: Find stale PRs (more aggressive timeline)
    print("Example 3: Stale Pull Request Detection")
    print("-" * 80)

    # Find PRs stale for 14+ days
    stale_prs = agent.get_stale_prs(days=14)
    print(f"Found {len(stale_prs)} stale pull requests (14+ days inactive)")

    if stale_prs:
        print("\nTop 5 stalest PRs:")
        for pr in stale_prs[:5]:
            print(f"  PR #{pr.number}: {pr.title}")
            print(f"    Last updated: {pr.updated_at.strftime('%Y-%m-%d')} ({pr.days_stale} days ago)")
            print(f"    Assignees: {', '.join(pr.assignees) if pr.assignees else 'None'}")
            print(f"    URL: {pr.url}")
            print()

    # Example 4: Get actionable recommendations
    print("Example 4: Actionable Recommendations")
    print("-" * 80)

    recommendations = agent.get_actionable_recommendations()
    print(f"Generated {len(recommendations)} recommendations:")
    print()

    for i, rec in enumerate(recommendations, 1):
        priority_emoji = {
            RecommendationPriority.CRITICAL: "🔴",
            RecommendationPriority.HIGH: "🟠",
            RecommendationPriority.MEDIUM: "🟡",
            RecommendationPriority.LOW: "🟢",
        }

        print(f"{i}. {priority_emoji[rec.priority]} [{rec.priority.value.upper()}] {rec.action}")
        print(f"   Impact: {rec.impact}")
        if rec.details:
            print(f"   Details: {rec.details}")
        print()

    # Example 5: Dry run cleanup (see what would be closed)
    print("Example 5: Cleanup Stale Items (Dry Run)")
    print("-" * 80)

    cleanup_report = agent.cleanup_stale_items(
        warning_days=30,      # Add warning label at 30 days
        close_days=60,        # Add close warning comment at 60 days
        auto_close_days=90,   # Auto-close at 90 days
        dry_run=True,         # DRY RUN - don't actually close anything
        exclude_labels=["keep-open", "pinned"]  # Don't touch these
    )

    print("Cleanup Summary (DRY RUN):")
    print(f"  - Would add warning labels:   {cleanup_report['summary']['warning_labels']}")
    print(f"  - Would add close warnings:   {cleanup_report['summary']['close_warnings']}")
    print(f"  - Would auto-close:           {cleanup_report['summary']['would_close_items']}")
    print(f"  - Errors:                     {cleanup_report['summary']['errors']}")
    print()

    if cleanup_report["would_close"]:
        print("Items that would be closed:")
        for item_num in cleanup_report["would_close"][:10]:
            print(f"  - #{item_num}")
        if len(cleanup_report["would_close"]) > 10:
            print(f"  ... and {len(cleanup_report['would_close']) - 10} more")
        print()

    # Example 6: Execute cleanup (commented out for safety)
    print("Example 6: Execute Cleanup (Commented Out)")
    print("-" * 80)
    print("To execute cleanup, uncomment the following code:")
    print()
    print("# cleanup_report = agent.cleanup_stale_items(")
    print("#     warning_days=30,")
    print("#     close_days=60,")
    print("#     auto_close_days=90,")
    print("#     dry_run=False,  # EXECUTE CLEANUP")
    print("#     exclude_labels=['keep-open', 'pinned']")
    print("# )")
    print()

    # Example 7: Health trends (basic version)
    print("Example 7: Health Trends")
    print("-" * 80)

    trends = agent.get_health_trends(days=30)
    print("Health Trends (Current Snapshot):")
    for metric, data in trends.items():
        if data:
            latest = data[0]
            print(f"  - {metric}: {latest['value']:.2f}")
    print()
    print("Note: For historical trends, integrate with a time-series database")
    print()

    # Example 8: Manual stale item closure
    print("Example 8: Manual Stale Item Closure")
    print("-" * 80)
    print("To manually close a specific stale item:")
    print()
    print("# from moai_flow.github import StaleItem")
    print("# stale_item = StaleItem(")
    print("#     number=123,")
    print("#     title='Old issue',")
    print("#     url='https://github.com/org/repo/issues/123',")
    print("#     state='open',")
    print("#     created_at=datetime.now(),")
    print("#     updated_at=datetime.now(),")
    print("#     days_stale=95,")
    print("#     type='issue'")
    print("# )")
    print("#")
    print("# success = agent.auto_close_stale(")
    print("#     stale_item,")
    print("#     reason='Closing due to 90+ days of inactivity',")
    print("#     label='auto-closed'")
    print("# )")
    print()

    print("=" * 80)
    print("Example Complete!")
    print("=" * 80)


def example_scheduled_health_monitoring():
    """Example of scheduled health monitoring (e.g., daily cron job)."""

    agent = GitHubRepoAgent("your-org", "your-repo")

    # Calculate health score
    health = agent.monitor_health()

    # Alert if health is critical
    if health.category == HealthCategory.CRITICAL:
        print(f"⚠️ CRITICAL: Repository health is {health.total_score}/100")
        print("Immediate action required!")

        # Get top recommendations
        recommendations = agent.get_actionable_recommendations()
        critical_recs = [
            r for r in recommendations
            if r.priority == RecommendationPriority.CRITICAL
        ]

        if critical_recs:
            print("\nCritical Actions:")
            for rec in critical_recs:
                print(f"  - {rec.action}")

    # Run automated cleanup
    cleanup_report = agent.cleanup_stale_items(
        warning_days=30,
        close_days=60,
        auto_close_days=90,
        dry_run=False,
        exclude_labels=["keep-open", "pinned", "security"]
    )

    print(f"\nCleanup Summary:")
    print(f"  - Closed items: {cleanup_report['summary']['closed_items']}")
    print(f"  - Warnings added: {cleanup_report['summary']['warning_labels']}")


def example_health_dashboard():
    """Example of generating a health dashboard report."""

    agent = GitHubRepoAgent("your-org", "your-repo")

    # Get all metrics
    health = agent.monitor_health()
    stale_issues = agent.get_stale_issues(days=30)
    stale_prs = agent.get_stale_prs(days=14)
    recommendations = agent.get_actionable_recommendations()

    # Generate markdown report
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

    print(report)
    return report


if __name__ == "__main__":
    # Run main example
    main()

    # Uncomment to run other examples
    # example_scheduled_health_monitoring()
    # example_health_dashboard()
