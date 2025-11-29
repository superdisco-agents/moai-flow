"""GitHub Issue Agent Usage Examples.

This module demonstrates how to use the GitHubIssueAgent for automated
issue creation, triage, and management.

Examples:
    Basic usage:
        >>> from moai_flow.github import GitHubIssueAgent
        >>> agent = GitHubIssueAgent("owner", "repo", token)
        >>> issue_num = agent.create_issue_from_failure(...)

    Advanced triage:
        >>> from moai_flow.github import IssueTriage, IssuePriority
        >>> triage = IssueTriage()
        >>> metadata = triage.classify(error, context)
"""

import os
from moai_flow.github.issue_agent import GitHubIssueAgent
from moai_flow.github.triage import IssueTriage, IssuePriority, TriageRule


def example_1_basic_issue_creation():
    """Example 1: Create issue from task failure.

    Demonstrates basic issue creation with minimal configuration.
    """
    print("Example 1: Basic Issue Creation")
    print("-" * 50)

    # Initialize agent
    agent = GitHubIssueAgent(
        repo_owner="your-org",
        repo_name="your-repo",
        github_token=os.getenv("GITHUB_TOKEN"),
    )

    # Simulate a task failure
    try:
        # Some task that fails
        raise TimeoutError("API request timeout after 30 seconds")
    except Exception as error:
        # Create issue from failure
        context = {
            "component": "api",
            "environment": "production",
            "endpoint": "/api/v1/users",
        }

        issue_number = agent.create_issue_from_failure(
            task_id="task-001",
            agent_id="agent-backend",
            error=error,
            context=context,
            spec_id="SPEC-001",  # Optional
        )

        print(f"✅ Created issue #{issue_number}")
        print(f"   URL: https://github.com/your-org/your-repo/issues/{issue_number}")


def example_2_auto_triage():
    """Example 2: Automatic issue triage.

    Demonstrates how auto-triage classifies errors and assigns metadata.
    """
    print("\nExample 2: Auto-Triage")
    print("-" * 50)

    # Initialize agent
    agent = GitHubIssueAgent(
        repo_owner="your-org", repo_name="your-repo", github_token=os.getenv("GITHUB_TOKEN")
    )

    # Different error scenarios
    errors_and_contexts = [
        (TimeoutError("Request timeout"), {"component": "api"}),
        (PermissionError("Access denied"), {"component": "auth"}),
        (ValueError("Invalid value"), {"environment": "staging"}),
        (MemoryError("Out of memory"), {"environment": "production"}),
    ]

    for error, context in errors_and_contexts:
        metadata = agent.auto_triage(error, context)

        print(f"\nError: {error}")
        print(f"  Priority: {metadata.priority.value}")
        print(f"  Labels: {', '.join(metadata.labels)}")
        print(f"  Assignees: {', '.join(metadata.assignees) if metadata.assignees else 'None'}")


def example_3_custom_triage_rules():
    """Example 3: Custom triage rules.

    Demonstrates how to add custom classification rules for domain-specific errors.
    """
    print("\nExample 3: Custom Triage Rules")
    print("-" * 50)

    # Define custom rule for domain-specific errors
    custom_rules = [
        TriageRule(
            error_patterns=[r"payment.*failed", r"transaction.*error"],
            labels=["payment", "revenue-impact"],
            priority=IssuePriority.CRITICAL,
            assignees=["payment-team", "on-call"],
        ),
        TriageRule(
            error_patterns=[r"cache.*miss", r"redis.*error"],
            labels=["cache", "performance"],
            priority=IssuePriority.MEDIUM,
            assignees=["infrastructure-team"],
        ),
    ]

    # Initialize triage with custom rules
    triage = IssueTriage(custom_rules=custom_rules)

    # Test custom rule matching
    payment_error = Exception("Payment processing failed for transaction #12345")
    metadata = triage.classify(payment_error, {"component": "billing"})

    print(f"Payment Error Classification:")
    print(f"  Priority: {metadata.priority.value}")
    print(f"  Labels: {', '.join(metadata.labels)}")
    print(f"  Assignees: {', '.join(metadata.assignees)}")


def example_4_add_context_to_issue():
    """Example 4: Add additional context to existing issue.

    Demonstrates enriching issues with stack traces, environment info, and commit history.
    """
    print("\nExample 4: Add Context to Existing Issue")
    print("-" * 50)

    agent = GitHubIssueAgent(
        repo_owner="your-org", repo_name="your-repo", github_token=os.getenv("GITHUB_TOKEN")
    )

    # Get stack trace
    stack_trace = """
Traceback (most recent call last):
  File "api/views.py", line 42, in process_request
    result = await fetch_data(user_id)
  File "api/client.py", line 18, in fetch_data
    response = await session.get(url, timeout=30)
asyncio.TimeoutError: Request timeout after 30s
"""

    # Environment information
    environment = {
        "python_version": "3.11.5",
        "os": "Linux 5.15.0-ubuntu",
        "memory_available": "2GB",
        "cpu_usage": "85%",
    }

    # Recent changes
    recent_changes = [
        "abc1234 - Increase API timeout to 30s",
        "def5678 - Add retry logic to client",
        "ghi9012 - Update dependencies",
    ]

    # Add context to issue #42
    agent.add_context(
        issue_number=42,
        stack_trace=stack_trace,
        environment=environment,
        recent_changes=recent_changes,
    )

    print("✅ Added detailed context to issue #42")


def example_5_link_to_spec():
    """Example 5: Link issue to SPEC document.

    Demonstrates creating bidirectional links between issues and SPEC documents.
    """
    print("\nExample 5: Link Issue to SPEC")
    print("-" * 50)

    agent = GitHubIssueAgent(
        repo_owner="your-org", repo_name="your-repo", github_token=os.getenv("GITHUB_TOKEN")
    )

    # Link issue to SPEC
    agent.link_to_spec(issue_number=42, spec_id="SPEC-001")

    print("✅ Linked issue #42 to SPEC-001")
    print("   - Added SPEC reference to issue")
    print("   - Added spec:spec-001 label")
    print("   - Added issue link to SPEC file (if exists)")


def example_6_update_priority():
    """Example 6: Update issue priority.

    Demonstrates dynamic priority updates based on impact assessment.
    """
    print("\nExample 6: Update Issue Priority")
    print("-" * 50)

    agent = GitHubIssueAgent(
        repo_owner="your-org", repo_name="your-repo", github_token=os.getenv("GITHUB_TOKEN")
    )

    # Update priority with justification
    agent.update_priority(
        issue_number=42,
        priority=IssuePriority.CRITICAL,
        reason="Production outage affecting 1000+ users. Revenue impact estimated at $10k/hour.",
    )

    print("✅ Updated issue #42 priority to CRITICAL")
    print("   - Removed old priority labels")
    print("   - Added priority:critical label")
    print("   - Added comment with justification")


def example_7_find_similar_issues():
    """Example 7: Find similar existing issues.

    Demonstrates duplicate detection and related issue discovery.
    """
    print("\nExample 7: Find Similar Issues")
    print("-" * 50)

    agent = GitHubIssueAgent(
        repo_owner="your-org", repo_name="your-repo", github_token=os.getenv("GITHUB_TOKEN")
    )

    # Find similar issues
    error = TimeoutError("API request timeout")
    similar_issues = agent.get_similar_issues(error, limit=5)

    print(f"Found {len(similar_issues)} similar issues:")
    for issue_num in similar_issues:
        print(f"  - Issue #{issue_num}")

    if similar_issues:
        print("\n💡 Tip: Check these issues before creating a duplicate!")


def example_8_complete_workflow():
    """Example 8: Complete workflow from error to issue.

    Demonstrates end-to-end workflow with all features.
    """
    print("\nExample 8: Complete Workflow")
    print("-" * 50)

    # Initialize agent
    agent = GitHubIssueAgent(
        repo_owner="your-org", repo_name="your-repo", github_token=os.getenv("GITHUB_TOKEN")
    )

    # Simulate task execution with error
    try:
        # Task execution
        raise PermissionError("Database access denied for user 'api-user'")

    except Exception as error:
        # 1. Check for similar issues
        similar = agent.get_similar_issues(error, limit=3)
        if similar:
            print(f"⚠️  Found {len(similar)} similar issues: {similar}")
            print("   Consider updating existing issue instead of creating new one")
            return

        # 2. Auto-triage to get metadata
        context = {
            "component": "database",
            "environment": "production",
            "affected_tables": ["users", "orders"],
        }

        metadata = agent.auto_triage(error, context)
        print(f"Triage Results:")
        print(f"  Priority: {metadata.priority.value}")
        print(f"  Labels: {metadata.labels}")

        # 3. Create issue
        issue_number = agent.create_issue_from_failure(
            task_id="task-db-001",
            agent_id="agent-database",
            error=error,
            context=context,
            spec_id="SPEC-042",
        )

        print(f"\n✅ Created issue #{issue_number}")

        # 4. Add additional context
        environment = {
            "database_version": "PostgreSQL 15.3",
            "connection_pool_size": "20",
            "active_connections": "18",
        }

        agent.add_context(
            issue_number=issue_number,
            environment=environment,
        )

        # 5. Link to SPEC
        agent.link_to_spec(issue_number=issue_number, spec_id="SPEC-042")

        # 6. Update priority if needed
        if metadata.priority == IssuePriority.CRITICAL:
            agent.update_priority(
                issue_number=issue_number,
                priority=IssuePriority.CRITICAL,
                reason="Production database access issues affecting all users",
            )

        print(f"\n🎉 Complete! Issue #{issue_number} fully configured")
        print(f"   URL: https://github.com/your-org/your-repo/issues/{issue_number}")


def example_9_batch_issue_creation():
    """Example 9: Batch issue creation from multiple failures.

    Demonstrates handling multiple task failures efficiently.
    """
    print("\nExample 9: Batch Issue Creation")
    print("-" * 50)

    agent = GitHubIssueAgent(
        repo_owner="your-org", repo_name="your-repo", github_token=os.getenv("GITHUB_TOKEN")
    )

    # Multiple task failures
    failures = [
        {
            "task_id": "task-001",
            "agent_id": "agent-api",
            "error": TimeoutError("Request timeout"),
            "context": {"component": "api"},
        },
        {
            "task_id": "task-002",
            "agent_id": "agent-db",
            "error": ValueError("Invalid query"),
            "context": {"component": "database"},
        },
        {
            "task_id": "task-003",
            "agent_id": "agent-cache",
            "error": ConnectionError("Redis connection lost"),
            "context": {"component": "cache"},
        },
    ]

    created_issues = []

    for failure in failures:
        issue_num = agent.create_issue_from_failure(
            task_id=failure["task_id"],
            agent_id=failure["agent_id"],
            error=failure["error"],
            context=failure["context"],
        )
        created_issues.append(issue_num)
        print(f"✅ Created issue #{issue_num} for {failure['task_id']}")

    print(f"\n🎉 Created {len(created_issues)} issues: {created_issues}")


def main():
    """Run all examples.

    Note: Examples require GITHUB_TOKEN environment variable and valid repo access.
    """
    print("=" * 60)
    print("GitHub Issue Agent - Usage Examples")
    print("=" * 60)

    # Check for GitHub token
    if not os.getenv("GITHUB_TOKEN"):
        print("\n⚠️  Warning: GITHUB_TOKEN environment variable not set")
        print("   Examples will demonstrate API calls but won't execute")
        print("   Set GITHUB_TOKEN to run examples against real repository")
        return

    # Run examples (comment out to skip specific examples)
    try:
        example_1_basic_issue_creation()
        example_2_auto_triage()
        example_3_custom_triage_rules()
        # example_4_add_context_to_issue()  # Requires existing issue
        # example_5_link_to_spec()  # Requires existing issue
        # example_6_update_priority()  # Requires existing issue
        example_7_find_similar_issues()
        example_8_complete_workflow()
        # example_9_batch_issue_creation()  # Creates multiple issues

    except Exception as e:
        print(f"\n❌ Error running examples: {str(e)}")
        print("   Make sure GITHUB_TOKEN is valid and repository exists")


if __name__ == "__main__":
    main()
