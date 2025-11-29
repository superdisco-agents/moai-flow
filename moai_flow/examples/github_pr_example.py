"""GitHub PR Agent Usage Examples.

This module demonstrates how to use the GitHubPRAgent for automated
PR creation and management.

Examples:
    1. Basic PR creation
    2. PR creation with SPEC integration
    3. Managing PR metadata (labels, reviewers, assignees)
    4. Draft PR workflow
    5. Adding comments and requesting reviews
"""

import os
from moai_flow.github import GitHubPRAgent


def example_basic_pr_creation():
    """Example 1: Basic PR creation from a branch.

    Creates a simple PR with auto-generated description.
    """
    print("\n=== Example 1: Basic PR Creation ===\n")

    # Initialize agent
    agent = GitHubPRAgent(
        repo_owner="your-org",
        repo_name="your-repo",
        github_token=os.getenv("GITHUB_TOKEN"),
    )

    # Create PR
    pr_number = agent.create_pr(
        branch_name="feature/user-authentication",
        base_branch="main",
        title="Add user authentication feature",
        auto_labels=True,
    )

    print(f"✅ Created PR #{pr_number}")
    print(f"   URL: https://github.com/your-org/your-repo/pull/{pr_number}")


def example_pr_with_spec():
    """Example 2: PR creation with SPEC integration.

    Creates a PR with auto-generated description from SPEC file.
    """
    print("\n=== Example 2: PR with SPEC Integration ===\n")

    agent = GitHubPRAgent(
        repo_owner="your-org",
        repo_name="your-repo",
        github_token=os.getenv("GITHUB_TOKEN"),
    )

    # Create PR from SPEC
    pr_number = agent.create_pr(
        branch_name="feature/SPEC-001-auth",
        base_branch="main",
        spec_id="SPEC-001",  # Auto-generates description from .moai/specs/SPEC-001/spec.md
        auto_labels=True,
    )

    print(f"✅ Created PR #{pr_number} from SPEC-001")
    print("   - Auto-generated description from SPEC")
    print("   - Included breaking changes and deployment notes")


def example_pr_metadata_management():
    """Example 3: Managing PR metadata.

    Sets labels, reviewers, and assignees for a PR.
    """
    print("\n=== Example 3: PR Metadata Management ===\n")

    agent = GitHubPRAgent(
        repo_owner="your-org",
        repo_name="your-repo",
        github_token=os.getenv("GITHUB_TOKEN"),
    )

    # Create PR
    pr_number = agent.create_pr(
        branch_name="feature/api-enhancement",
        base_branch="main",
        auto_labels=False,  # Disable auto-labels to set custom ones
    )

    # Set metadata
    agent.set_metadata(
        pr_number=pr_number,
        labels=["enhancement", "api", "backend", "priority:high"],
        reviewers=["senior-dev", "tech-lead"],
        assignees=["developer-1"],
    )

    print(f"✅ Updated PR #{pr_number} metadata")
    print("   Labels: enhancement, api, backend, priority:high")
    print("   Reviewers: senior-dev, tech-lead")
    print("   Assignee: developer-1")


def example_draft_pr_workflow():
    """Example 4: Draft PR workflow.

    Creates a draft PR and converts it to ready when complete.
    """
    print("\n=== Example 4: Draft PR Workflow ===\n")

    agent = GitHubPRAgent(
        repo_owner="your-org",
        repo_name="your-repo",
        github_token=os.getenv("GITHUB_TOKEN"),
    )

    # Create draft PR
    pr_number = agent.create_pr(
        branch_name="feature/work-in-progress",
        base_branch="main",
        is_draft=True,  # Create as draft
    )

    print(f"✅ Created draft PR #{pr_number}")
    print("   - Marked as 'Work in Progress'")

    # Add progress comment
    agent.add_comment(
        pr_number=pr_number,
        comment="## Work Progress\n\n- [x] Implement core functionality\n- [ ] Add tests\n- [ ] Update docs",
    )

    print("   - Added progress checklist")

    # Later: Mark as ready for review
    agent.update_status(pr_number=pr_number, is_draft=False)

    print("   - Marked as ready for review")

    # Request reviews
    agent.request_review(pr_number=pr_number, reviewers=["reviewer-1", "reviewer-2"])

    print("   - Requested reviews from: reviewer-1, reviewer-2")


def example_automated_pr_pipeline():
    """Example 5: Automated PR creation pipeline.

    Complete automation workflow for PR creation from CI/CD or scripts.
    """
    print("\n=== Example 5: Automated PR Pipeline ===\n")

    agent = GitHubPRAgent(
        repo_owner="your-org",
        repo_name="your-repo",
        github_token=os.getenv("GITHUB_TOKEN"),
    )

    # Get current branch and SPEC from environment or git
    current_branch = "feature/SPEC-042-analytics"
    spec_id = "SPEC-042"

    print(f"Creating automated PR for branch: {current_branch}")

    # Step 1: Create PR with SPEC
    pr_number = agent.create_pr(
        branch_name=current_branch,
        base_branch="develop",
        spec_id=spec_id,
        auto_labels=True,
    )

    print(f"✅ Step 1: Created PR #{pr_number}")

    # Step 2: Set team-specific metadata
    agent.set_metadata(
        pr_number=pr_number,
        labels=["analytics", "backend"],
        reviewers=["analytics-team-lead"],
        assignees=["developer-analytics"],
    )

    print("✅ Step 2: Set team metadata")

    # Step 3: Add CI/CD status comment
    agent.add_comment(
        pr_number=pr_number,
        comment="""## CI/CD Status

✅ Build: Passing
✅ Tests: All 127 tests passed
✅ Coverage: 92% (target: 90%)
✅ Linting: No issues

Ready for review!
""",
    )

    print("✅ Step 3: Added CI/CD status")

    # Step 4: Request code review
    agent.request_review(
        pr_number=pr_number,
        reviewers=["code-reviewer-1", "code-reviewer-2"],
    )

    print("✅ Step 4: Requested code reviews")
    print(f"\n🎉 Automated PR pipeline completed for PR #{pr_number}")
    print(f"   View: https://github.com/your-org/your-repo/pull/{pr_number}")


def example_error_handling():
    """Example 6: Error handling and validation.

    Demonstrates proper error handling for common scenarios.
    """
    print("\n=== Example 6: Error Handling ===\n")

    try:
        agent = GitHubPRAgent(
            repo_owner="your-org",
            repo_name="your-repo",
            # Token will be read from GITHUB_TOKEN env var
        )

        # Try to create PR from non-existent branch
        pr_number = agent.create_pr(
            branch_name="feature/non-existent-branch",
            base_branch="main",
        )

    except ValueError as e:
        print(f"❌ Validation Error: {e}")
        print("   Solution: Ensure branch exists and has commits")

    except Exception as e:
        print(f"❌ GitHub API Error: {e}")
        print("   Solution: Check GitHub token permissions and network connectivity")


def example_batch_pr_management():
    """Example 7: Batch PR operations.

    Manage multiple PRs programmatically.
    """
    print("\n=== Example 7: Batch PR Management ===\n")

    agent = GitHubPRAgent(
        repo_owner="your-org",
        repo_name="your-repo",
        github_token=os.getenv("GITHUB_TOKEN"),
    )

    # Batch create PRs for multiple features
    feature_branches = [
        ("feature/SPEC-101-login", "SPEC-101"),
        ("feature/SPEC-102-signup", "SPEC-102"),
        ("feature/SPEC-103-profile", "SPEC-103"),
    ]

    pr_numbers = []

    for branch, spec_id in feature_branches:
        try:
            pr_number = agent.create_pr(
                branch_name=branch,
                base_branch="develop",
                spec_id=spec_id,
                auto_labels=True,
            )

            # Set common metadata
            agent.set_metadata(
                pr_number=pr_number,
                labels=["sprint-42", "user-management"],
                reviewers=["team-lead"],
            )

            pr_numbers.append(pr_number)
            print(f"✅ Created and configured PR #{pr_number} for {spec_id}")

        except Exception as e:
            print(f"❌ Failed to create PR for {branch}: {e}")

    print(f"\n✅ Batch operation completed: {len(pr_numbers)} PRs created")


def main():
    """Run all examples."""
    print("=" * 60)
    print("GitHub PR Agent - Usage Examples")
    print("=" * 60)

    # Note: These examples require a valid GitHub token and repository
    # Set GITHUB_TOKEN environment variable before running

    if not os.getenv("GITHUB_TOKEN"):
        print("\n⚠️  Warning: GITHUB_TOKEN environment variable not set")
        print("   Export your token: export GITHUB_TOKEN='your-token-here'")
        print("\nShowing example code only (not executing API calls):\n")

    # Uncomment the examples you want to run
    # example_basic_pr_creation()
    # example_pr_with_spec()
    # example_pr_metadata_management()
    # example_draft_pr_workflow()
    # example_automated_pr_pipeline()
    # example_error_handling()
    # example_batch_pr_management()

    print("\n" + "=" * 60)
    print("Example code demonstration complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
