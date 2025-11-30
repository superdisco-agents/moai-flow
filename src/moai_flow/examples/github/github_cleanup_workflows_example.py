"""Examples for GitHub Cleanup Workflows.

This module demonstrates how to use the cleanup workflows for repository health management.

Requirements:
    - GitHub token with repo access
    - PyGithub installed: pip install PyGithub

Examples:
    1. Stale Issue Cleanup (30/60/90 day workflow)
    2. Stale PR Cleanup (14/30/60 day workflow)
    3. Auto-Label PRs based on file changes
    4. Health Monitoring and Notifications
    5. Combined Workflow Execution
    6. Custom Configuration
"""

import os
from moai_flow.github.workflows import (
    StaleIssueWorkflow,
    StalePRWorkflow,
    AutoLabelWorkflow,
    NotificationWorkflow,
    WorkflowConfig,
)


def example_1_stale_issue_cleanup():
    """Example 1: Stale Issue Cleanup (30/60/90 day workflow)."""
    print("=== Example 1: Stale Issue Cleanup ===\n")

    # Initialize workflow
    workflow = StaleIssueWorkflow(
        repo_owner="moai-adk",
        repo_name="core",
        github_token=os.getenv("GITHUB_TOKEN")
    )

    # Preview mode (dry run) - see what would happen
    print("Preview mode: Checking for stale issues...")
    result = workflow.preview()

    print(f"Workflow: {result.workflow_name}")
    print(f"Items affected: {result.items_affected}")
    print(f"Actions that would be taken:")
    for action in result.actions_taken:
        print(f"  - {action}")

    # Get list of affected items
    print("\nAffected issues:")
    affected = workflow.get_affected_items()
    for issue in affected:
        print(f"  - Issue #{issue.number}: {issue.title}")

    # Execute workflow (uncomment to actually run)
    # result = workflow.execute()
    # print(f"\nExecuted: {result.items_labeled} labeled, {result.items_commented} commented, {result.items_closed} closed")


def example_2_stale_pr_cleanup():
    """Example 2: Stale PR Cleanup (14/30/60 day workflow)."""
    print("\n=== Example 2: Stale PR Cleanup ===\n")

    # Initialize workflow
    workflow = StalePRWorkflow(
        repo_owner="moai-adk",
        repo_name="core",
        github_token=os.getenv("GITHUB_TOKEN")
    )

    # Configure custom thresholds
    workflow.configure(
        stale_pr_days_warning=21,  # Label at 21 days instead of 14
        stale_pr_days_comment=45,  # Comment at 45 days instead of 30
        stale_pr_days_close=90     # Close at 90 days instead of 60
    )

    # Preview and execute
    print("Preview mode: Checking for stale PRs...")
    result = workflow.preview()

    print(f"Items affected: {result.items_affected}")
    print(f"Actions that would be taken: {len(result.actions_taken)}")

    # Show affected PRs
    affected_prs = workflow.get_affected_items()
    print(f"\nFound {len(affected_prs)} stale PRs")
    for pr in affected_prs[:5]:  # Show first 5
        print(f"  - PR #{pr.number}: {pr.title}")


def example_3_auto_label_workflow():
    """Example 3: Auto-Label PRs based on file changes."""
    print("\n=== Example 3: Auto-Label Workflow ===\n")

    # Initialize workflow
    workflow = AutoLabelWorkflow(
        repo_owner="moai-adk",
        repo_name="core",
        github_token=os.getenv("GITHUB_TOKEN")
    )

    # Add custom label rules
    workflow.add_label_rule("moai_flow/github/**", "github-integration")
    workflow.add_label_rule("moai_flow/core/**", "core")
    workflow.add_label_rule("**/*.md", "documentation")

    # Preview
    print("Preview mode: Checking PRs for auto-labeling...")
    result = workflow.preview()

    print(f"Items that would be labeled: {result.items_labeled}")
    print(f"Actions:")
    for action in result.actions_taken[:10]:  # Show first 10
        print(f"  - {action}")

    # Get affected PRs
    affected_prs = workflow.get_affected_items()
    print(f"\nFound {len(affected_prs)} PRs that need labels")


def example_4_health_monitoring():
    """Example 4: Health Monitoring and Notifications."""
    print("\n=== Example 4: Health Monitoring ===\n")

    # Initialize workflow
    workflow = NotificationWorkflow(
        repo_owner="moai-adk",
        repo_name="core",
        github_token=os.getenv("GITHUB_TOKEN")
    )

    # Configure custom thresholds
    workflow.configure_thresholds(
        stale_issue_ratio=0.20,  # Alert if >20% issues are stale
        stale_pr_ratio=0.15,     # Alert if >15% PRs are stale
        avg_pr_age_days=10       # Alert if avg PR age >10 days
    )

    # Check health metrics
    print("Checking repository health metrics...")
    violations = workflow.get_affected_items()

    if violations:
        print(f"⚠️  Health violations detected: {violations}")
        result = workflow.preview()
        print(f"Notifications that would be sent: {result.notifications_sent}")
    else:
        print("✅ Repository health is good!")


def example_5_combined_workflow():
    """Example 5: Combined Workflow Execution."""
    print("\n=== Example 5: Combined Workflow Execution ===\n")

    repo_owner = "moai-adk"
    repo_name = "core"
    token = os.getenv("GITHUB_TOKEN")

    # Custom configuration
    config = WorkflowConfig(
        stale_issue_days_warning=45,
        stale_issue_days_comment=75,
        stale_issue_days_close=105,
        stale_pr_days_warning=21,
        stale_pr_days_comment=42,
        stale_pr_days_close=84,
        exempt_labels=["pinned", "security", "priority:critical", "wip"],
        auto_label_enabled=True,
        notification_enabled=True,
        dry_run=False  # Set to True for preview mode
    )

    workflows = [
        AutoLabelWorkflow(repo_owner, repo_name, token, config),
        StaleIssueWorkflow(repo_owner, repo_name, token, config),
        StalePRWorkflow(repo_owner, repo_name, token, config),
        NotificationWorkflow(repo_owner, repo_name, token, config),
    ]

    print("Executing all workflows in preview mode...\n")

    for workflow in workflows:
        result = workflow.preview()
        print(f"Workflow: {result.workflow_name}")
        print(f"  Items affected: {result.items_affected}")
        print(f"  Labeled: {result.items_labeled}")
        print(f"  Commented: {result.items_commented}")
        print(f"  Closed: {result.items_closed}")
        print(f"  Notifications: {result.notifications_sent}")
        if result.errors:
            print(f"  Errors: {len(result.errors)}")
        print()

    # Uncomment to execute all workflows
    # for workflow in workflows:
    #     print(f"Executing {workflow.__class__.__name__}...")
    #     result = workflow.execute()
    #     print(f"  Completed: {result.items_affected} items processed")


def example_6_custom_configuration():
    """Example 6: Advanced Custom Configuration."""
    print("\n=== Example 6: Advanced Custom Configuration ===\n")

    # Conservative configuration (longer timeframes)
    conservative_config = WorkflowConfig(
        stale_issue_days_warning=60,   # 2 months
        stale_issue_days_comment=120,  # 4 months
        stale_issue_days_close=180,    # 6 months
        stale_pr_days_warning=30,      # 1 month
        stale_pr_days_comment=60,      # 2 months
        stale_pr_days_close=90,        # 3 months
        exempt_labels=["pinned", "security", "priority:critical", "priority:high", "wip", "blocked"],
        auto_label_enabled=True,
        notification_enabled=True,
    )

    # Aggressive configuration (shorter timeframes)
    aggressive_config = WorkflowConfig(
        stale_issue_days_warning=14,  # 2 weeks
        stale_issue_days_comment=28,  # 4 weeks
        stale_issue_days_close=42,    # 6 weeks
        stale_pr_days_warning=7,      # 1 week
        stale_pr_days_comment=14,     # 2 weeks
        stale_pr_days_close=21,       # 3 weeks
        exempt_labels=["pinned", "security"],  # Minimal exemptions
        auto_label_enabled=True,
        notification_enabled=True,
    )

    print("Conservative configuration:")
    print(f"  Issue lifecycle: {conservative_config.stale_issue_days_warning}/"
          f"{conservative_config.stale_issue_days_comment}/"
          f"{conservative_config.stale_issue_days_close} days")
    print(f"  PR lifecycle: {conservative_config.stale_pr_days_warning}/"
          f"{conservative_config.stale_pr_days_comment}/"
          f"{conservative_config.stale_pr_days_close} days")

    print("\nAggressive configuration:")
    print(f"  Issue lifecycle: {aggressive_config.stale_issue_days_warning}/"
          f"{aggressive_config.stale_issue_days_comment}/"
          f"{aggressive_config.stale_issue_days_close} days")
    print(f"  PR lifecycle: {aggressive_config.stale_pr_days_warning}/"
          f"{aggressive_config.stale_pr_days_comment}/"
          f"{aggressive_config.stale_pr_days_close} days")

    # Use conservative config for production
    workflow = StaleIssueWorkflow(
        repo_owner="moai-adk",
        repo_name="core",
        github_token=os.getenv("GITHUB_TOKEN"),
        config=conservative_config
    )

    print("\nUsing conservative configuration...")
    result = workflow.preview()
    print(f"Items that would be affected: {result.items_affected}")


def main():
    """Run all examples."""
    # Check for GitHub token
    if not os.getenv("GITHUB_TOKEN"):
        print("Error: GITHUB_TOKEN environment variable not set")
        print("Set it with: export GITHUB_TOKEN=your_github_token")
        return

    # Run examples
    example_1_stale_issue_cleanup()
    example_2_stale_pr_cleanup()
    example_3_auto_label_workflow()
    example_4_health_monitoring()
    example_5_combined_workflow()
    example_6_custom_configuration()

    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60)
    print("\nTo execute workflows (not just preview):")
    print("1. Set dry_run=False in WorkflowConfig")
    print("2. Call workflow.execute() instead of workflow.preview()")
    print("3. Monitor the results and adjust thresholds as needed")


if __name__ == "__main__":
    main()
