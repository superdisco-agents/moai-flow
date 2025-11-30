# Multi-Agent PR Workflows

Advanced pull request workflows for coordinated multi-agent development.

## Pattern 1: Full-Stack Feature PRs

**Scenario**: Backend and frontend agents both implement parts of a feature.

```python
from moai_flow.github import GitHubPRAgent

pr_agent = GitHubPRAgent("org", "repo")

# Backend agent creates backend PR
backend_pr = pr_agent.create_pr(
    branch_name="feature/SPEC-001-backend",
    base_branch="main",
    spec_id="SPEC-001",
    auto_labels=True
)

# Frontend agent creates frontend PR
frontend_pr = pr_agent.create_pr(
    branch_name="feature/SPEC-001-frontend",
    base_branch="main",
    spec_id="SPEC-001",
    auto_labels=True
)

# Cross-reference PRs
pr_agent.add_comment(
    backend_pr,
    f"🔗 Related frontend PR: #{frontend_pr}\\n\\n"
    f"**Merge Order**: Backend must be merged and deployed first."
)

pr_agent.add_comment(
    frontend_pr,
    f"🔗 Related backend PR: #{backend_pr}\\n\\n"
    f"**Dependencies**: Requires backend API endpoints from PR #{backend_pr}"
)

print(f"Created coordinated PRs: Backend #{backend_pr}, Frontend #{frontend_pr}")
```

## Pattern 2: Progressive Review Workflow

**Scenario**: Large refactoring requires multi-stage reviews.

```python
from moai_flow.github import GitHubPRAgent

agent = GitHubPRAgent("org", "repo")

# Create draft PR
pr_number = agent.create_pr(
    branch_name="refactor/database-layer",
    spec_id="SPEC-002",
    is_draft=True  # Start as draft
)

# Stage 1: Architecture Review
agent.request_review(pr_number, reviewers=["tech-architect"])
agent.add_comment(
    pr_number,
    "## Stage 1: Architecture Review\\n\\n"
    "@tech-architect Please review overall architecture and design patterns."
)

# After architecture approval...
# Stage 2: Security Review
agent.request_review(pr_number, reviewers=["security-expert"])
agent.add_comment(
    pr_number,
    "## Stage 2: Security Review\\n\\n"
    "@security-expert Please review security implications of database changes."
)

# After security approval...
# Stage 3: Performance Review
agent.request_review(pr_number, reviewers=["performance-expert"])
agent.add_comment(
    pr_number,
    "## Stage 3: Performance Review\\n\\n"
    "@performance-expert Please review query performance and indexing strategy."
)

# After all approvals...
agent.update_status(pr_number, is_draft=False)
agent.add_comment(
    pr_number,
    "✅ All review stages complete. Ready for merge."
)
```

## Pattern 3: Automated PR from TDD Completion

**Scenario**: manager-tdd completes implementation, automatically creates PR.

```python
from moai_flow.github import GitHubPRAgent

def on_tdd_complete(spec_id, branch_name, test_results):
    """Triggered when TDD cycle completes successfully."""
    pr_agent = GitHubPRAgent("org", "repo")

    # Create PR with test results
    pr_number = pr_agent.create_pr(
        branch_name=branch_name,
        base_branch="main",
        spec_id=spec_id,
        auto_labels=True,
        is_draft=False
    )

    # Add test results comment
    pr_agent.add_comment(
        pr_number,
        f"""
        ## Test Results

        ✅ All tests passing

        ### Coverage
        - **Line Coverage**: {test_results['line_coverage']}%
        - **Branch Coverage**: {test_results['branch_coverage']}%
        - **Target**: >= 90%

        ### Test Summary
        - **Unit Tests**: {test_results['unit_tests']} passed
        - **Integration Tests**: {test_results['integration_tests']} passed
        - **Total Duration**: {test_results['duration']}s

        ### Quality Gates
        - ✅ TRUST 5 validation passed
        - ✅ Coverage target met
        - ✅ No code smells detected
        """
    )

    # Request reviews based on domain
    domain = extract_domain_from_spec(spec_id)
    reviewers = get_reviewers_for_domain(domain)

    pr_agent.set_metadata(
        pr_number,
        reviewers=reviewers,
        labels=["auto-generated", "tdd-complete"]
    )

    return pr_number
```

## Pattern 4: Component-Based PR Creation

**Scenario**: Microservices architecture with multiple service PRs.

```python
from moai_flow.github import GitHubPRAgent

def create_microservice_prs(spec_id, services):
    """Create PRs for multiple microservices."""
    pr_agent = GitHubPRAgent("org", "repo")

    prs = {}

    for service in services:
        branch_name = f"feature/{spec_id}-{service}"

        pr_number = pr_agent.create_pr(
            branch_name=branch_name,
            base_branch="main",
            spec_id=spec_id,
            auto_labels=True
        )

        # Service-specific labels
        pr_agent.set_metadata(
            pr_number,
            labels=[f"service:{service}", "microservice"],
            assignees=[f"{service}-team"]
        )

        prs[service] = pr_number

    # Add deployment order comment to all PRs
    deployment_order = ["auth-service", "user-service", "api-gateway"]

    for service, pr_number in prs.items():
        other_services = [f"#{prs[s]} ({s})" for s in services if s != service]

        pr_agent.add_comment(
            pr_number,
            f"""
            ## Related Service PRs
            {chr(10).join([f"- {s}" for s in other_services])}

            ## Deployment Order
            {chr(10).join([f"{i+1}. {s} (PR #{prs[s]})" for i, s in enumerate(deployment_order) if s in prs])}
            """
        )

    return prs
```

## Pattern 5: Incremental PR Updates

**Scenario**: Add context to PR as implementation progresses.

```python
from moai_flow.github import GitHubPRAgent

agent = GitHubPRAgent("org", "repo")

# Initial PR creation
pr_number = agent.create_pr(
    branch_name="feature/payment-gateway",
    spec_id="SPEC-003",
    is_draft=True
)

# Update 1: Core logic complete
agent.add_comment(
    pr_number,
    """
    ## Update 1: Core Logic Complete

    ✅ Implemented:
    - Payment processor interface
    - Stripe integration
    - PayPal integration
    - Transaction validation

    🔄 In Progress:
    - Unit tests
    - Integration tests
    - Error handling
    """
)

# Update 2: Tests added
agent.add_comment(
    pr_number,
    """
    ## Update 2: Tests Added

    ✅ Test Coverage: 95%

    Added Tests:
    - Unit tests: 45 tests
    - Integration tests: 12 scenarios
    - Edge cases: 8 tests

    All tests passing ✅
    """
)

# Update 3: Ready for review
agent.update_status(pr_number, is_draft=False)
agent.set_metadata(
    pr_number,
    reviewers=["security-expert", "payment-team-lead"],
    labels=["critical", "payment"]
)
agent.add_comment(
    pr_number,
    """
    ## Update 3: Ready for Review

    ✅ Implementation complete
    ✅ Tests passing (95% coverage)
    ✅ Security considerations documented

    **Critical Review Points**:
    - Payment data encryption
    - PCI compliance
    - Error handling for failed transactions
    """
)
```

## Pattern 6: Breaking Change Management

**Scenario**: PR contains breaking changes requiring special handling.

```python
from moai_flow.github import GitHubPRAgent

agent = GitHubPRAgent("org", "repo")

pr_number = agent.create_pr(
    branch_name="breaking/api-v2-migration",
    spec_id="SPEC-004",
    auto_labels=True
)

# Add breaking change warning
agent.set_metadata(
    pr_number,
    labels=["breaking-change", "major-version", "requires-migration"]
)

# Add detailed migration guide
agent.add_comment(
    pr_number,
    """
    ## ⚠️ BREAKING CHANGES

    This PR introduces breaking changes that require API consumers to migrate.

    ### Changes
    1. **Authentication**: JWT token format changed
    2. **Endpoints**: `/api/v1/users` → `/api/v2/users`
    3. **Response Format**: Envelope structure added

    ### Migration Guide
    See [MIGRATION.md](./docs/MIGRATION.md) for detailed migration steps.

    ### Backward Compatibility
    - API v1 deprecated (supported until 2026-01-01)
    - Feature flag: `api_v2_enabled`
    - Gradual rollout plan included

    ### Required Actions
    - [ ] Update client SDKs
    - [ ] Update documentation
    - [ ] Notify API consumers
    - [ ] Create deprecation timeline
    """
)

# Request executive review for breaking changes
agent.request_review(pr_number, reviewers=["cto", "tech-lead", "api-team-lead"])
```

## Pattern 7: Dependency Chain PRs

**Scenario**: PR depends on another PR being merged first.

```python
from moai_flow.github import GitHubPRAgent

agent = GitHubPRAgent("org", "repo")

# PR 1: Foundation
foundation_pr = agent.create_pr(
    branch_name="feature/auth-foundation",
    spec_id="SPEC-005-A",
    auto_labels=True
)

# PR 2: Depends on PR 1
dependent_pr = agent.create_pr(
    branch_name="feature/auth-ui",
    spec_id="SPEC-005-B",
    auto_labels=True,
    is_draft=True  # Keep as draft until foundation merges
)

# Add dependency note
agent.add_comment(
    dependent_pr,
    f"""
    ## ⚠️ Dependency Notice

    This PR depends on #{foundation_pr} being merged first.

    **Dependency Chain**:
    1. PR #{foundation_pr}: Auth Foundation (MUST merge first)
    2. PR #{dependent_pr}: Auth UI (THIS PR)

    This PR will remain in draft until #{foundation_pr} is merged.
    """
)

# Add note to foundation PR
agent.add_comment(
    foundation_pr,
    f"""
    ## Dependent PRs

    The following PRs depend on this one:
    - PR #{dependent_pr}: Auth UI

    These will be updated and marked ready after this PR merges.
    """
)
```

## Pattern 8: Performance Optimization PR

**Scenario**: PR focused on performance improvements with benchmarks.

```python
from moai_flow.github import GitHubPRAgent

agent = GitHubPRAgent("org", "repo")

pr_number = agent.create_pr(
    branch_name="perf/database-query-optimization",
    spec_id="SPEC-006",
    auto_labels=True
)

# Add performance benchmark results
agent.add_comment(
    pr_number,
    """
    ## Performance Improvements

    ### Before vs After

    | Operation | Before | After | Improvement |
    |-----------|--------|-------|-------------|
    | User query | 850ms | 45ms | **94.7%** ⬇️ |
    | Search query | 1.2s | 120ms | **90.0%** ⬇️ |
    | Bulk insert | 5.5s | 800ms | **85.5%** ⬇️ |

    ### Changes
    - ✅ Added database indexes on frequently queried columns
    - ✅ Implemented query result caching
    - ✅ Optimized N+1 query patterns
    - ✅ Added connection pooling

    ### Benchmarks
    - Load test: 1000 concurrent users
    - Duration: 5 minutes
    - Success rate: 99.9%

    ### Resource Usage
    - CPU: Reduced by 40%
    - Memory: Reduced by 25%
    - Database connections: Reduced by 60%
    """
)

agent.set_metadata(
    pr_number,
    reviewers=["performance-expert", "database-admin"],
    labels=["performance", "optimization"]
)
```

---

**Related Documentation**:
- [Basic GitHub Usage](basic-github.md)
- [Advanced Workflows](advanced-workflows.md)
