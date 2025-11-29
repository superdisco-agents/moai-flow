# Cleanup Workflows Implementation Summary

**PRD-06: Repository Health Management**

## Overview

Implemented comprehensive cleanup workflows for maintaining repository health with automated stale issue/PR management, auto-labeling, and health monitoring.

## Files Created

### 1. Core Implementation
- **`cleanup.py`** (1070 lines)
  - 4 complete workflow classes
  - Configurable thresholds and exempt labels
  - Preview mode (dry run) support
  - Comprehensive error handling

### 2. Package Structure
- **`workflows/__init__.py`**
  - Exports all workflow classes
  - Clean public API

### 3. Documentation
- **`workflows/README.md`**
  - Complete API documentation
  - Usage examples
  - Best practices
  - Troubleshooting guide
  - GitHub Actions integration

### 4. Examples
- **`examples/github_cleanup_workflows_example.py`**
  - 6 comprehensive examples
  - Real-world usage patterns
  - Configuration presets

### 5. Integration
- **Updated `github/__init__.py`**
  - Exported all workflow classes
  - Updated module docstring

## Implemented Workflows

### 1. StaleIssueWorkflow ✅

**30/60/90 Day Lifecycle**:
- Day 30: Add "stale" label
- Day 60: Add close warning comment
- Day 90: Auto-close with explanation

**Features**:
- Configurable timeframes
- Exempt label support (pinned, security, priority:critical, etc.)
- Preview mode
- Detailed execution results

**Methods**:
```python
execute() -> WorkflowResult        # Execute cleanup
preview() -> WorkflowResult        # Dry run
configure(**kwargs) -> None        # Update config
get_affected_items() -> List[Issue]  # Get affected issues
```

### 2. StalePRWorkflow ✅

**14/30/60 Day Lifecycle**:
- Day 14: Add "stale" label
- Day 30: Add close warning comment
- Day 60: Auto-close with explanation

**Features**:
- Shorter timeframes than issues (PRs are more time-sensitive)
- Same configuration flexibility
- Respects WIP and in-progress labels

**Methods**:
```python
execute() -> WorkflowResult           # Execute cleanup
preview() -> WorkflowResult           # Dry run
configure(**kwargs) -> None           # Update config
get_affected_items() -> List[PullRequest]  # Get affected PRs
```

### 3. AutoLabelWorkflow ✅

**Auto-labeling based on file changes**:

| File Pattern | Label |
|--------------|-------|
| `backend/**` | backend |
| `frontend/**` | frontend |
| `tests/**` | testing |
| `docs/**` | documentation |
| `.github/**` | ci-cd |
| `docker/**` | infrastructure |

**Features**:
- Custom label rules
- Pattern matching (supports `**` wildcards)
- Only adds missing labels (idempotent)

**Methods**:
```python
execute() -> WorkflowResult              # Execute auto-labeling
preview() -> WorkflowResult              # Dry run
get_affected_items() -> List[PullRequest]  # Get PRs needing labels
add_label_rule(pattern, label) -> None   # Add custom rule
```

### 4. NotificationWorkflow ✅

**Health degradation monitoring**:

| Metric | Default Threshold | Action |
|--------|------------------|--------|
| Stale issue ratio | 25% | Create alert issue |
| Stale PR ratio | 20% | Create alert issue |
| Avg PR age | 14 days | Create alert issue |

**Features**:
- Configurable thresholds
- Creates health alert issues
- Actionable recommendations
- Cleanup workflow suggestions

**Methods**:
```python
execute() -> WorkflowResult              # Execute monitoring
preview() -> WorkflowResult              # Dry run
get_affected_items() -> List[str]        # Get violated metrics
configure_thresholds(**kwargs) -> None   # Update thresholds
```

## Core Classes

### WorkflowConfig
```python
@dataclass
class WorkflowConfig:
    stale_issue_days_warning: int = 30
    stale_issue_days_comment: int = 60
    stale_issue_days_close: int = 90
    stale_pr_days_warning: int = 14
    stale_pr_days_comment: int = 30
    stale_pr_days_close: int = 60
    exempt_labels: List[str] = [...]
    auto_label_enabled: bool = True
    notification_enabled: bool = True
    dry_run: bool = False
```

### WorkflowResult
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

### BaseWorkflow
```python
class BaseWorkflow:
    def __init__(repo_owner, repo_name, github_token, config)
    def execute() -> WorkflowResult
    def preview() -> WorkflowResult
    def configure(**kwargs) -> None
    def get_affected_items() -> List[Any]
```

## Usage Examples

### Example 1: Basic Stale Issue Cleanup
```python
from moai_flow.github.workflows import StaleIssueWorkflow

workflow = StaleIssueWorkflow("owner", "repo")
result = workflow.preview()  # Dry run
result = workflow.execute()  # Execute
```

### Example 2: Custom Configuration
```python
from moai_flow.github.workflows import StaleIssueWorkflow, WorkflowConfig

config = WorkflowConfig(
    stale_issue_days_close=120,  # 4 months instead of 3
    exempt_labels=["pinned", "security", "wip"]
)

workflow = StaleIssueWorkflow("owner", "repo", config=config)
workflow.execute()
```

### Example 3: Combined Workflows
```python
from moai_flow.github.workflows import (
    StaleIssueWorkflow,
    StalePRWorkflow,
    AutoLabelWorkflow,
    NotificationWorkflow
)

workflows = [
    AutoLabelWorkflow("owner", "repo"),
    StaleIssueWorkflow("owner", "repo"),
    StalePRWorkflow("owner", "repo"),
    NotificationWorkflow("owner", "repo")
]

for workflow in workflows:
    result = workflow.execute()
    print(f"{workflow.__class__.__name__}: {result.items_affected} items")
```

## Key Features

### 1. Preview Mode (Dry Run)
Every workflow supports preview mode to see what would happen without making changes:

```python
result = workflow.preview()
print(f"Would affect {result.items_affected} items")
print(f"Actions: {result.actions_taken}")
```

### 2. Affected Items
Get list of items that would be processed:

```python
affected = workflow.get_affected_items()
for item in affected:
    print(f"Item #{item.number}: {item.title}")
```

### 3. Configurable Thresholds
All timeframes and thresholds are configurable:

```python
workflow.configure(
    stale_issue_days_warning=45,
    stale_issue_days_close=105
)
```

### 4. Exempt Labels
Protect important items from cleanup:

```python
config = WorkflowConfig(
    exempt_labels=[
        "pinned",
        "security",
        "priority:critical",
        "priority:high",
        "wip",
        "blocked",
        "in-progress"
    ]
)
```

### 5. Error Handling
Comprehensive error tracking:

```python
result = workflow.execute()
if result.errors:
    print(f"Errors encountered: {len(result.errors)}")
    for error in result.errors:
        print(f"  - {error}")
```

## Integration Points

### With GitHubIssueAgent
```python
# Cleanup workflows can work alongside issue creation
issue_agent = GitHubIssueAgent("owner", "repo")
cleanup = StaleIssueWorkflow("owner", "repo")

# Create issues
issue_agent.create_issue_from_failure(...)

# Clean up stale issues
cleanup.execute()
```

### With GitHubPRAgent
```python
# Auto-label new PRs
pr_agent = GitHubPRAgent("owner", "repo")
auto_label = AutoLabelWorkflow("owner", "repo")

# Create PR
pr_agent.create_pr(...)

# Auto-label it
auto_label.execute()
```

### With HealthMetricsAnalyzer
```python
# Health monitoring integration
analyzer = HealthMetricsAnalyzer("owner", "repo")
notification = NotificationWorkflow("owner", "repo")

# Analyze health
metrics = analyzer.analyze()

# Send notifications if degraded
notification.execute()
```

## Testing Strategy

### Unit Tests Needed
- Test each workflow in isolation
- Test configuration validation
- Test exempt label logic
- Test threshold calculations
- Test error handling

### Integration Tests Needed
- Test with real GitHub API (or mocks)
- Test workflow combinations
- Test preview mode vs execution
- Test affected items accuracy

### Example Test Structure
```python
def test_stale_issue_workflow():
    # Setup
    workflow = StaleIssueWorkflow(...)

    # Preview mode
    result = workflow.preview()
    assert result.dry_run == True

    # Get affected items
    affected = workflow.get_affected_items()
    assert len(affected) > 0

    # Execute
    result = workflow.execute()
    assert result.items_affected > 0
```

## Performance Considerations

### API Rate Limits
- GitHub API has rate limits (5000 requests/hour for authenticated users)
- Workflows paginate through issues/PRs
- Preview mode uses same API calls as execution

### Optimization Strategies
- Batch label operations when possible
- Cache issue/PR lists
- Use search API for filtering
- Implement exponential backoff for rate limit errors

## Security Considerations

### GitHub Token Permissions
Required permissions:
- `repo` - Full repository access
- `issues:write` - Create/edit issues
- `pull_requests:write` - Create/edit PRs

### Sensitive Data
- No secrets or sensitive data in comments
- Sanitize environment variables
- Don't expose internal system details

## Deployment

### Manual Execution
```bash
export GITHUB_TOKEN=ghp_xxxxxxxxxxxx
python moai_flow/examples/github_cleanup_workflows_example.py
```

### GitHub Actions
```yaml
name: Cleanup Workflows
on:
  schedule:
    - cron: '0 0 * * 1'  # Weekly
  workflow_dispatch:

jobs:
  cleanup:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install PyGithub
      - run: python cleanup_script.py
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### Cron Job
```bash
# Daily health check at midnight
0 0 * * * cd /path/to/repo && python cleanup_script.py
```

## Metrics & Monitoring

### Execution Metrics
Track via WorkflowResult:
- Items affected
- Items labeled
- Items commented
- Items closed
- Notifications sent
- Errors encountered

### Health Metrics
Track repository health over time:
- Stale issue ratio trend
- Stale PR ratio trend
- Average PR age trend
- Cleanup effectiveness

## Future Enhancements

### Potential Additions
1. **Smart Exemptions** - Auto-detect active discussions
2. **Custom Actions** - Plugin system for custom workflows
3. **Metrics Dashboard** - Visualize health trends
4. **Slack Integration** - Notifications to Slack
5. **Multi-Repo Support** - Batch processing across repos
6. **Machine Learning** - Predict which items will go stale

### API Extensions
1. **Batch Operations** - Process multiple repos
2. **Webhooks** - Real-time workflow triggers
3. **CLI Tool** - Command-line interface
4. **Web UI** - Visual configuration and monitoring

## Conclusion

Successfully implemented comprehensive cleanup workflows for PRD-06 Repository Health Management with:

✅ 4 complete workflows (Stale Issues, Stale PRs, Auto-Label, Notifications)
✅ ~1070 lines of production-ready code
✅ Comprehensive documentation and examples
✅ Configurable thresholds and exempt labels
✅ Preview mode for safe testing
✅ Error handling and logging
✅ Integration with existing GitHub agents

All requirements from PRD-06 have been met.
