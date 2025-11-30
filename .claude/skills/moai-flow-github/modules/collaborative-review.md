# Collaborative Code Review & Issue Triage

Intelligent issue creation, automatic triage, priority assignment, and similarity detection for multi-agent task failure reporting.

## Overview

The GitHubIssueAgent automates GitHub issue creation from task failures with intelligent triage, context enrichment, and SPEC linking. The integrated triage system assigns priorities based on error severity, environment, frequency, and business impact.

## Core Capabilities

### 1. Automatic Issue Creation from Failures

**Exception-to-Issue Workflow**:

```python
try:
    # Task execution
    result = execute_task()
except Exception as error:
    # Automatic issue creation
    issue_number = issue_agent.create_issue_from_failure(
        task_id="task-001",
        agent_id="agent-backend",
        error=error,
        context={
            "component": "api",
            "environment": "production",
            "frequency": 5
        },
        spec_id="SPEC-001"
    )
```

**Generated Issue Components**:

1. **Title**: `[component] ErrorType: message`
2. **Body**: Error details, stack trace, environment info
3. **Labels**: Auto-assigned based on error type and context
4. **Priority**: Calculated by triage system
5. **Assignees**: Suggested by component ownership
6. **SPEC Link**: Bidirectional reference if spec_id provided

### 2. Intelligent Triage System

**Priority Calculation Formula**:

```python
# Weighted scoring (0-100)
score = (
    error_severity_score * 0.4 +      # 40% weight
    environment_score * 0.3 +          # 30% weight
    frequency_score * 0.2 +            # 20% weight
    business_impact_score * 0.1        # 10% weight
)

# Priority mapping
if score >= 80: CRITICAL
elif score >= 60: HIGH
elif score >= 30: MEDIUM
else: LOW
```

**Error Severity Scores**:

| Error Type | Score | Priority Impact |
|------------|-------|-----------------|
| MemoryError, PermissionError, data loss | 100 | CRITICAL |
| TimeoutError, DatabaseError, ConnectionError | 75 | HIGH |
| TypeError, ValueError, KeyError | 50 | MEDIUM |
| AttributeError, FileNotFoundError | 25 | LOW |

**Environment Scores**:

| Environment | Score | Priority Impact |
|-------------|-------|-----------------|
| production | 100 | CRITICAL if combined with high severity |
| staging | 60 | Medium impact |
| development | 30 | Low impact |
| test | 30 | Low impact |

**Frequency Scores**:

| Occurrences | Score | Priority Impact |
|-------------|-------|-----------------|
| 20+ | 100 | Persistent issue |
| 10-19 | 75 | Recurring issue |
| 5-9 | 50 | Multiple occurrences |
| 2-4 | 25 | Occasional |
| 1 | 10 | First occurrence |

**Business Impact Scores**:

| Impact Factor | Score | Examples |
|---------------|-------|----------|
| Revenue/payment errors | 100 | Payment gateway failures |
| User impact > 1000 | 100 | Widespread user-facing issues |
| Security issues | 100 | Authentication bypass, data leaks |
| User impact 100-1000 | 75 | Moderate user impact |
| User impact < 100 | 50 | Limited user impact |

**Practical Examples**:

```python
# Example 1: Production timeout with high frequency
error = TimeoutError("API timeout after 30s")
context = {
    "environment": "production",
    "frequency": 15,
    "component": "api"
}

# Calculation:
# Severity: 75 * 0.4 = 30
# Environment: 100 * 0.3 = 30
# Frequency: 75 * 0.2 = 15
# Business: 10 * 0.1 = 1
# Total: 76 → Priority: HIGH

# Example 2: Development type error
error = TypeError("Expected str, got int")
context = {
    "environment": "development",
    "frequency": 1
}

# Calculation:
# Severity: 50 * 0.4 = 20
# Environment: 30 * 0.3 = 9
# Frequency: 10 * 0.2 = 2
# Business: 10 * 0.1 = 1
# Total: 32 → Priority: MEDIUM
```

### 3. Auto-Labeling Rules

**Error Type Labels**:

```python
error_type_labels = {
    "TimeoutError": ["timeout", "performance"],
    "PermissionError": ["security", "access-control"],
    "TypeError": ["bug", "type-safety"],
    "ValueError": ["bug", "validation"],
    "DatabaseError": ["database", "backend"],
    "ConnectionError": ["infrastructure", "network"],
    "MemoryError": ["performance", "memory"],
    "ImportError": ["dependency", "build"],
    "FileNotFoundError": ["bug", "filesystem"],
    "KeyError": ["bug", "data"],
    "AssertionError": ["test", "bug"]
}
```

**Context-Based Labels**:

```python
# Component labels
{"component": "api"} → "api"
{"component": "auth"} → "auth"
{"component": "database"} → "database"

# Environment labels
{"environment": "production"} → "production"
{"environment": "staging"} → "staging"

# Tag labels (from context)
{"tags": ["revenue", "payment"]} → "revenue", "payment"
```

### 4. Context Enrichment

**Automatic Context Addition**:

1. **Stack Trace**: Full traceback with syntax highlighting
2. **Environment Variables**: System info (sanitized, no secrets)
3. **Recent Git Commits**: Last 5 commits
4. **Related Files**: Files involved in stack trace
5. **SPEC Link**: Reference to related SPEC document

**Example Enriched Issue**:

```markdown
## Error Report

**Task ID**: task-001
**Agent ID**: agent-backend
**Timestamp**: 2025-11-30T10:30:00Z

## Error

```
TimeoutError: API request timeout after 30s
```

## Stack Trace

```python
Traceback (most recent call last):
  File "api/endpoints/auth.py", line 42, in authenticate
    response = await http_client.post(url, timeout=30)
TimeoutError: API request timeout after 30s
```

## Environment

- **Python**: 3.11.5
- **OS**: ubuntu-22.04
- **MoAI-Flow**: 0.30.2
- **Environment**: production
- **Component**: api

## Recent Changes

- `abc1234` Fix timeout logic
- `def5678` Add retry mechanism
- `ghi9012` Update API endpoint

## Related SPEC

[SPEC-001](.moai/specs/SPEC-001/spec.md)

## Steps to Reproduce

1. <!-- Add steps -->

## Expected Behavior

<!-- Describe expected -->

## Actual Behavior

<!-- Describe actual -->
```

### 5. Similar Issue Detection

**Duplicate Prevention**:

```python
# Before creating new issue, search for similar
similar = agent.get_similar_issues(error, limit=5)

if similar:
    print(f"Found {len(similar)} similar issues:")
    for issue_num in similar:
        print(f"  - #{issue_num}")

    # Option 1: Add comment to existing issue
    agent.add_context(
        issue_number=similar[0],
        stack_trace=new_stack_trace,
        environment={"occurrence": "2025-11-30"}
    )

    # Option 2: Create new issue with cross-reference
    issue_number = agent.create_issue_from_failure(...)
    agent.add_comment(
        issue_number,
        f"Possibly related to: {', '.join([f'#{num}' for num in similar])}"
    )
```

**Search Algorithm**:

```python
# Search query construction
query_parts = [
    f'repo:{org}/{repo}',
    f'"{error_type}"',  # Exact error type match
    f'"{key_terms[0]}"',  # Key terms from error message
    "is:issue"
]

# GitHub API search
issues = github_client.search_issues(
    query=" ".join(query_parts),
    sort="created",
    order="desc"
)
```

### 6. SPEC Linking

**Bidirectional References**:

```python
# Link issue to SPEC
agent.link_to_spec(issue_number=42, spec_id="SPEC-001")

# This creates:
# 1. Comment in issue with SPEC reference
# 2. Entry in SPEC file's "Related Issues" section
```

**SPEC File Update**:

```markdown
# Feature Title

## Summary
Feature description...

## Related Issues

- #42
- #51
```

### 7. Priority Updates

**Manual Priority Escalation**:

```python
from moai_flow.github import IssuePriority

# Update priority with justification
agent.update_priority(
    issue_number=42,
    priority=IssuePriority.CRITICAL,
    reason="Production down, affecting 10k+ users. Revenue impact estimated at $50k/hour."
)
```

**Generated Comment**:

```markdown
## Priority Update

**New Priority**: CRITICAL

**Reason**: Production down, affecting 10k+ users. Revenue impact estimated at $50k/hour.

**Updated**: 2025-11-30 10:45:00
```

### 8. Assignee Suggestions

**Component-Based Assignment**:

```python
component_map = {
    "api": ["backend-team"],
    "backend": ["backend-team"],
    "frontend": ["frontend-team"],
    "ui": ["frontend-team"],
    "database": ["database-team", "backend-team"],
    "ci-cd": ["devops-team"],
    "infrastructure": ["devops-team"],
    "security": ["security-team"],
    "monitoring": ["devops-team", "backend-team"]
}
```

**Usage**:

```python
# Automatic assignee suggestion based on component
context = {"component": "database"}
metadata = agent.auto_triage(error, context)

# metadata.assignees = ["database-team", "backend-team"]
```

## Advanced Patterns

### Pattern 1: Intelligent Issue Escalation

```python
def on_agent_failure(task_id, agent_id, error, context):
    """Auto-escalate critical issues."""
    issue_agent = GitHubIssueAgent("org", "repo")

    # Create issue with auto-triage
    issue_number = issue_agent.create_issue_from_failure(
        task_id=task_id,
        agent_id=agent_id,
        error=error,
        context=context
    )

    # Check priority
    metadata = issue_agent.auto_triage(error, context)

    # Escalate if CRITICAL
    if metadata.priority == IssuePriority.CRITICAL:
        # Add urgent labels
        issue_agent.set_metadata(
            issue_number,
            labels=["urgent", "on-call", "p0"],
            assignees=["on-call-engineer", "tech-lead"]
        )

        # Send external notifications
        notify_slack(f"🚨 CRITICAL issue #{issue_number}")
        notify_pagerduty(issue_number)
        notify_email(["engineering-leads@company.com"])

    return issue_number
```

### Pattern 2: Issue Deduplication

```python
def create_or_update_issue(error, context, spec_id=None):
    """Create new issue or update existing similar issue."""
    issue_agent = GitHubIssueAgent("org", "repo")

    # Check for similar issues
    similar = issue_agent.get_similar_issues(error, limit=3)

    if similar:
        # Update existing issue with new occurrence
        existing_issue = similar[0]
        issue_agent.add_context(
            issue_number=existing_issue,
            stack_trace=format_stack_trace(error),
            environment=context,
            recent_changes=get_recent_commits()
        )

        # Update frequency in context
        issue_agent.add_comment(
            existing_issue,
            f"⚠️ Issue recurred at {datetime.now()}\n"
            f"Frequency: {context.get('frequency', 'unknown')}\n"
            f"Environment: {context.get('environment', 'unknown')}"
        )

        return existing_issue
    else:
        # Create new issue
        return issue_agent.create_issue_from_failure(
            task_id=context.get("task_id"),
            agent_id=context.get("agent_id"),
            error=error,
            context=context,
            spec_id=spec_id
        )
```

### Pattern 3: Contextual Triage Rules

```python
from moai_flow.github import IssueTriage, TriageRule, IssuePriority

# Custom triage rules for specific components
custom_rules = [
    TriageRule(
        error_patterns=[r"payment", r"billing", r"checkout"],
        labels=["revenue-critical", "payment"],
        priority=IssuePriority.CRITICAL,
        assignees=["payment-team", "on-call"]
    ),
    TriageRule(
        error_patterns=[r"login", r"authentication", r"oauth"],
        labels=["auth", "security"],
        priority=IssuePriority.HIGH,
        assignees=["security-team", "auth-team"]
    )
]

# Initialize triage with custom rules
triage = IssueTriage(custom_rules=custom_rules)
issue_agent = GitHubIssueAgent("org", "repo")
issue_agent.triage = triage

# Triage will now apply custom rules in addition to defaults
```

## SLA Calculation

**Service Level Agreement Targets**:

```python
sla_map = {
    IssuePriority.CRITICAL: 4,    # 4 hours
    IssuePriority.HIGH: 24,       # 24 hours (next business day)
    IssuePriority.MEDIUM: 72,     # 3 business days
    IssuePriority.LOW: 168        # 1 week
}

# Calculate SLA for issue
sla_hours = triage.calculate_sla(priority)
```

**SLA Monitoring**:

```python
def check_sla_violations():
    """Monitor issues approaching SLA deadline."""
    issue_agent = GitHubIssueAgent("org", "repo")

    # Get all open issues
    open_issues = repo.get_issues(state="open")

    violations = []
    for issue in open_issues:
        # Get priority from labels
        priority = extract_priority_from_labels(issue.labels)

        # Calculate time since creation
        hours_open = (datetime.now() - issue.created_at).total_seconds() / 3600

        # Get SLA target
        sla_target = triage.calculate_sla(priority)

        # Check for violations
        if hours_open > sla_target:
            violations.append({
                "issue": issue.number,
                "priority": priority,
                "hours_over_sla": hours_open - sla_target
            })

    return violations
```

## API Reference

### GitHubIssueAgent

**Constructor**:

```python
def __init__(
    self,
    repo_owner: str,
    repo_name: str,
    github_token: Optional[str] = None
)
```

**Methods**:

#### create_issue_from_failure()

```python
def create_issue_from_failure(
    self,
    task_id: str,
    agent_id: str,
    error: Exception,
    context: Dict[str, Any],
    spec_id: Optional[str] = None
) -> int
```

#### auto_triage()

```python
def auto_triage(
    self,
    error: Exception,
    context: Dict[str, Any]
) -> IssueMetadata
```

#### add_context()

```python
def add_context(
    self,
    issue_number: int,
    stack_trace: Optional[str] = None,
    environment: Optional[Dict[str, Any]] = None,
    recent_changes: Optional[List[str]] = None
) -> None
```

#### link_to_spec()

```python
def link_to_spec(
    self,
    issue_number: int,
    spec_id: str
) -> None
```

#### update_priority()

```python
def update_priority(
    self,
    issue_number: int,
    priority: IssuePriority,
    reason: str
) -> None
```

#### get_similar_issues()

```python
def get_similar_issues(
    self,
    error: Exception,
    limit: int = 5
) -> List[int]
```

---

**Related Documentation**:
- [Multi-Agent PR Module](multi-agent-pr.md)
- [Workflow Automation Module](workflow-automation.md)
- [Integration Patterns Module](integration-patterns.md)
