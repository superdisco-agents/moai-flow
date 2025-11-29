# GitHub Cleanup Workflows

Automated cleanup workflows for maintaining repository health as part of PRD-06 Repo Health initiative.

## Overview

This module provides four automated workflows for repository health management:

1. **StaleIssueWorkflow** - 30/60/90 day stale issue cleanup
2. **StalePRWorkflow** - 14/30/60 day stale PR cleanup
3. **AutoLabelWorkflow** - Auto-label PRs based on file changes
4. **NotificationWorkflow** - Health degradation notifications

## Features

### Core Capabilities

✅ **Preview Mode (Dry Run)** - See what would happen before executing
✅ **Configurable Thresholds** - Customize timeframes and exempt labels
✅ **Affected Items** - Get list of items that would be processed
✅ **Execution Results** - Detailed results with action counts
✅ **Error Handling** - Comprehensive error tracking and logging

### Workflow-Specific Features

#### StaleIssueWorkflow
- **Day 30**: Add "stale" label
- **Day 60**: Add comment "Will close in 30 days"
- **Day 90**: Auto-close with explanation comment
- Respects exempt labels (pinned, security, priority:critical, etc.)

#### StalePRWorkflow
- **Day 14**: Add "stale" label
- **Day 30**: Add comment "Will close in 30 days"
- **Day 60**: Auto-close with explanation comment
- Respects exempt labels (wip, in-progress, etc.)

#### AutoLabelWorkflow
- `backend/**` → `backend` label
- `frontend/**` → `frontend` label
- `tests/**` → `testing` label
- `docs/**` → `documentation` label
- Custom rules supported

#### NotificationWorkflow
- Monitors stale issue ratio (default: 25%)
- Monitors stale PR ratio (default: 20%)
- Monitors average PR age (default: 14 days)
- Creates health alert issues when thresholds exceeded

## Installation

```bash
pip install PyGithub
```

## Quick Start

### 1. Basic Usage

```python
from moai_flow.github.workflows import StaleIssueWorkflow

# Initialize workflow
workflow = StaleIssueWorkflow(
    repo_owner="your-org",
    repo_name="your-repo",
    github_token="ghp_xxxxxxxxxxxx"
)

# Preview (dry run)
result = workflow.preview()
print(f"Would affect {result.items_affected} issues")

# Execute
result = workflow.execute()
print(f"Processed {result.items_affected} issues")
```

### 2. Custom Configuration

```python
from moai_flow.github.workflows import StaleIssueWorkflow, WorkflowConfig

# Custom configuration
config = WorkflowConfig(
    stale_issue_days_warning=45,   # Label at 45 days
    stale_issue_days_comment=75,   # Comment at 75 days
    stale_issue_days_close=105,    # Close at 105 days
    exempt_labels=["pinned", "security", "wip"],
    dry_run=False
)

workflow = StaleIssueWorkflow("owner", "repo", config=config)
workflow.execute()
```

### 3. Get Affected Items

```python
# Get list of items that would be processed
affected_issues = workflow.get_affected_items()

for issue in affected_issues:
    print(f"Issue #{issue.number}: {issue.title}")
    print(f"  Last updated: {issue.updated_at}")
    print(f"  Labels: {[l.name for l in issue.labels]}")
```

## API Reference

### WorkflowConfig

Configuration for cleanup workflows.

```python
@dataclass
class WorkflowConfig:
    # Stale issue thresholds
    stale_issue_days_warning: int = 30
    stale_issue_days_comment: int = 60
    stale_issue_days_close: int = 90

    # Stale PR thresholds
    stale_pr_days_warning: int = 14
    stale_pr_days_comment: int = 30
    stale_pr_days_close: int = 60

    # General settings
    exempt_labels: List[str] = ["pinned", "security", "priority:critical", ...]
    auto_label_enabled: bool = True
    notification_enabled: bool = True
    dry_run: bool = False
```

### WorkflowResult

Result of workflow execution.

```python
@dataclass
class WorkflowResult:
    workflow_name: str
    actions_taken: List[str]
    items_affected: int = 0
    items_labeled: int = 0
    items_commented: int = 0
    items_closed: int = 0
    notifications_sent: int = 0
    errors: List[str] = []
    dry_run: bool = False
```

### BaseWorkflow Methods

All workflows inherit these methods:

```python
class BaseWorkflow:
    def execute() -> WorkflowResult:
        """Execute workflow (make actual changes)."""

    def preview() -> WorkflowResult:
        """Preview workflow (dry run, no changes)."""

    def configure(**kwargs) -> None:
        """Update workflow configuration."""

    def get_affected_items() -> List[Any]:
        """Get list of items that would be affected."""
```

## Examples

### Example 1: Stale Issue Cleanup

```python
from moai_flow.github.workflows import StaleIssueWorkflow

workflow = StaleIssueWorkflow("owner", "repo")

# Preview
result = workflow.preview()
print(f"Would process {result.items_affected} issues:")
print(f"  - Label: {result.items_labeled}")
print(f"  - Comment: {result.items_commented}")
print(f"  - Close: {result.items_closed}")

# Execute
if input("Execute? (y/n): ").lower() == 'y':
    result = workflow.execute()
    print("Completed!")
```

### Example 2: Stale PR Cleanup

```python
from moai_flow.github.workflows import StalePRWorkflow

workflow = StalePRWorkflow("owner", "repo")

# Custom thresholds
workflow.configure(
    stale_pr_days_warning=21,
    stale_pr_days_comment=45,
    stale_pr_days_close=90
)

# Get affected PRs
affected = workflow.get_affected_items()
print(f"Found {len(affected)} stale PRs")

# Execute
result = workflow.execute()
```

### Example 3: Auto-Label Workflow

```python
from moai_flow.github.workflows import AutoLabelWorkflow

workflow = AutoLabelWorkflow("owner", "repo")

# Add custom label rules
workflow.add_label_rule("src/api/**", "api")
workflow.add_label_rule("src/ui/**", "ui")
workflow.add_label_rule("*.test.js", "testing")

# Preview
result = workflow.preview()
print(f"Would add {result.items_labeled} labels")

# Execute
result = workflow.execute()
```

### Example 4: Health Monitoring

```python
from moai_flow.github.workflows import NotificationWorkflow

workflow = NotificationWorkflow("owner", "repo")

# Configure thresholds
workflow.configure_thresholds(
    stale_issue_ratio=0.20,  # Alert if >20% issues stale
    stale_pr_ratio=0.15,     # Alert if >15% PRs stale
    avg_pr_age_days=10       # Alert if avg PR age >10 days
)

# Check health
violations = workflow.get_affected_items()
if violations:
    print(f"⚠️  Health violations: {violations}")
    workflow.execute()  # Send notification
else:
    print("✅ Repository health is good!")
```

### Example 5: Combined Workflow

```python
from moai_flow.github.workflows import (
    StaleIssueWorkflow,
    StalePRWorkflow,
    AutoLabelWorkflow,
    NotificationWorkflow,
    WorkflowConfig
)

# Shared configuration
config = WorkflowConfig(
    stale_issue_days_close=120,
    stale_pr_days_close=90,
    exempt_labels=["pinned", "security", "wip"]
)

workflows = [
    AutoLabelWorkflow("owner", "repo", config=config),
    StaleIssueWorkflow("owner", "repo", config=config),
    StalePRWorkflow("owner", "repo", config=config),
    NotificationWorkflow("owner", "repo", config=config),
]

# Execute all workflows
for workflow in workflows:
    print(f"Executing {workflow.__class__.__name__}...")
    result = workflow.execute()
    print(f"  Processed: {result.items_affected} items")
```

## Configuration Presets

### Conservative (Long Timeframes)

```python
conservative_config = WorkflowConfig(
    stale_issue_days_warning=60,   # 2 months
    stale_issue_days_comment=120,  # 4 months
    stale_issue_days_close=180,    # 6 months
    stale_pr_days_warning=30,      # 1 month
    stale_pr_days_comment=60,      # 2 months
    stale_pr_days_close=90,        # 3 months
    exempt_labels=["pinned", "security", "priority:critical", "priority:high", "wip", "blocked"]
)
```

### Moderate (Default Timeframes)

```python
moderate_config = WorkflowConfig()  # Use defaults
```

### Aggressive (Short Timeframes)

```python
aggressive_config = WorkflowConfig(
    stale_issue_days_warning=14,  # 2 weeks
    stale_issue_days_comment=28,  # 4 weeks
    stale_issue_days_close=42,    # 6 weeks
    stale_pr_days_warning=7,      # 1 week
    stale_pr_days_comment=14,     # 2 weeks
    stale_pr_days_close=21,       # 3 weeks
    exempt_labels=["pinned", "security"]
)
```

## Best Practices

### 1. Start with Preview Mode

Always preview workflows before executing:

```python
# Preview first
result = workflow.preview()
print(f"Would affect {result.items_affected} items")

# Review results, then execute
if result.items_affected > 0:
    workflow.execute()
```

### 2. Use Exempt Labels

Protect important items from cleanup:

```python
config = WorkflowConfig(
    exempt_labels=[
        "pinned",           # Permanently important
        "security",         # Security issues
        "priority:critical", # Critical priority
        "priority:high",    # High priority
        "wip",              # Work in progress
        "blocked",          # Blocked on external factors
        "in-progress"       # Currently being worked on
    ]
)
```

### 3. Monitor Health Regularly

Set up automated health checks:

```python
# Daily health check
health = NotificationWorkflow("owner", "repo")
violations = health.get_affected_items()

if violations:
    health.execute()  # Send alert
```

### 4. Adjust Thresholds Based on Activity

High-activity repos may need shorter timeframes:

```python
# High-activity repo
high_activity_config = WorkflowConfig(
    stale_issue_days_close=60,  # Faster cleanup
    stale_pr_days_close=30
)

# Low-activity repo
low_activity_config = WorkflowConfig(
    stale_issue_days_close=180,  # Longer timeframes
    stale_pr_days_close=120
)
```

## Troubleshooting

### Issue: Too Many Items Being Closed

**Solution**: Increase thresholds or add exempt labels

```python
workflow.configure(
    stale_issue_days_close=120,  # Increase from 90
    exempt_labels=["feature-request", "enhancement"]  # Add more exemptions
)
```

### Issue: Workflow Not Catching Stale Items

**Solution**: Decrease thresholds

```python
workflow.configure(
    stale_issue_days_warning=14,  # Decrease from 30
    stale_pr_days_warning=7       # Decrease from 14
)
```

### Issue: False Positives in Health Alerts

**Solution**: Adjust notification thresholds

```python
workflow.configure_thresholds(
    stale_issue_ratio=0.35,  # Increase from 0.25
    stale_pr_ratio=0.30      # Increase from 0.20
)
```

## Automation Setup

### GitHub Actions

Create `.github/workflows/cleanup.yml`:

```yaml
name: Repository Cleanup

on:
  schedule:
    - cron: '0 0 * * 1'  # Weekly on Monday
  workflow_dispatch:  # Manual trigger

jobs:
  cleanup:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install PyGithub

      - name: Run cleanup workflows
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          python moai_flow/examples/github_cleanup_workflows_example.py
```

## Related Modules

- **GitHubIssueAgent** - Automated issue creation and triage
- **GitHubPRAgent** - Automated PR creation and management
- **HealthMetricsAnalyzer** - Repository health metrics analysis
- **IssueTriage** - Issue classification and priority assignment

## Contributing

To add new workflows:

1. Inherit from `BaseWorkflow`
2. Implement `execute()` and `get_affected_items()`
3. Add to `workflows/__init__.py`
4. Create examples in `examples/github_cleanup_workflows_example.py`

## License

Part of MoAI-Flow - See LICENSE for details.

## Support

For issues or questions:
- GitHub Issues: https://github.com/moai-adk/core/issues
- Documentation: https://docs.moai-adk.dev
