# Branch Review Workflow Instructions

## Purpose

The Branch Review workflow generates comprehensive documentation and analysis for Git branches. It automates the process of:

1. Fetching branch metadata from GitHub/Git
2. Analyzing code changes, commits, and impact
3. Generating a structured branch README
4. Providing actionable insights and recommendations

This workflow is designed to work seamlessly with the `collector-readme` skill to maintain up-to-date branch documentation.

## When to Use

### Primary Use Cases

- **Before PR Review**: Generate comprehensive documentation before creating or reviewing pull requests
- **Status Checks**: Regular branch health checks and documentation updates
- **Handoff Documentation**: Creating detailed branch context for team collaboration
- **Release Preparation**: Documenting feature branches before merging to main
- **Audit Trail**: Maintaining historical records of branch evolution

### Specific Scenarios

1. **Daily Standup Prep**: Quick branch status for team updates
2. **Code Review Preparation**: Detailed context for reviewers
3. **Onboarding**: Help new team members understand active branches
4. **Conflict Resolution**: Analyze branch divergence and merge risks
5. **Release Notes**: Extract commit history for changelog generation

## Expected Inputs

### Required Inputs

- **branch_name** (string): Name of the branch to review
  - Example: `"feature/user-authentication"`
  - Must be a valid branch in the repository

### Optional Inputs

- **repository** (string): Repository name
  - Defaults to current repository if not specified
  - Format: `"owner/repo"` or auto-detected from git remote

- **base_branch** (string): Base branch for comparison
  - Default: `"main"`
  - Common alternatives: `"develop"`, `"master"`

- **include_diff** (boolean): Include detailed diff analysis
  - Default: `true`
  - Set to `false` for faster, high-level analysis

### Input Examples

```yaml
# Minimal input
branch_name: "feature/new-dashboard"

# Full input
branch_name: "feature/api-integration"
repository: "myorg/myapp"
base_branch: "develop"
include_diff: true
```

## Expected Outputs

### Primary Outputs

1. **branch_readme** (file): Generated branch README.md
   - Location: `.claude/branch-docs/{branch_name}/README.md`
   - Format: Markdown with sections for overview, changes, commits, analysis
   - Auto-linked to related documentation

2. **analysis_report** (object): Structured analysis data
   ```json
   {
     "scores": {
       "code_quality": 85,
       "test_coverage": 70,
       "documentation": 90,
       "commit_quality": 80
     },
     "risk": {
       "level": "medium",
       "factors": ["large changeset", "multiple file types"],
       "mitigation": ["incremental review", "integration tests"]
     },
     "recommendations": [
       "Add unit tests for new API endpoints",
       "Update integration documentation"
     ]
   }
   ```

3. **summary** (string): Human-readable summary
   - Formatted for terminal/chat display
   - Includes key metrics and actionable items

### Output File Structure

```
.claude/branch-docs/
└── {branch_name}/
    ├── README.md              # Main branch documentation
    ├── analysis.json          # Detailed analysis data
    ├── commits.log            # Commit history
    └── diff-summary.md        # Diff analysis
```

## Integration with collector-readme

### Automatic Integration

The workflow automatically integrates with the `collector-readme` skill:

1. **Template Usage**: Uses README templates from collector-readme
2. **Data Enrichment**: Combines git data with skill analysis
3. **Cross-Referencing**: Links to related project documentation
4. **Format Consistency**: Follows collector-readme formatting standards

### Manual Integration

To manually trigger integration:

```bash
# Generate branch README with collector-readme
/run workflow:branch-review branch_name=feature/my-feature

# Update project README with branch links
/use collector-readme --update-branch-index
```

### Configuration

Configure integration in `.claude/config/workflows/branch-review.json`:

```json
{
  "integration": {
    "collector-readme": {
      "enabled": true,
      "template": "branch-template-v2",
      "auto_update_index": true,
      "include_in_project_docs": true
    }
  }
}
```

## Workflow Execution

### Command Line

```bash
# Basic usage
/run workflow:branch-review branch_name=feature/user-auth

# With options
/run workflow:branch-review branch_name=hotfix/security-patch base_branch=develop include_diff=true

# Batch processing
/run workflow:branch-review branch_name=feature/* --parallel
```

### Programmatic Usage

```python
from moai_flow.workflows import BranchReviewWorkflow

workflow = BranchReviewWorkflow()
result = workflow.execute(
    branch_name="feature/new-api",
    repository="myorg/myapp",
    base_branch="main",
    include_diff=True
)

print(result.summary)
print(f"README generated at: {result.branch_readme}")
```

## Error Handling

### Common Errors

1. **Branch Not Found**: Verify branch name and repository access
2. **GitHub API Limits**: Workflow will retry with exponential backoff
3. **Large Diffs**: Set `include_diff=false` for branches with >1000 files
4. **Permission Errors**: Ensure GitHub token has repo access

### Recovery Actions

- Failed steps automatically retry up to 3 times
- Partial results are saved for manual inspection
- Logs available at `.claude/logs/workflows/branch-review/`

## Best Practices

1. **Run Before PR Creation**: Generate documentation before opening PRs
2. **Schedule Regular Updates**: Update branch docs on significant commits
3. **Use Consistent Base Branches**: Maintain stable comparison baselines
4. **Review Recommendations**: Act on workflow suggestions promptly
5. **Archive Old Branches**: Clean up docs for merged/deleted branches

## Advanced Features

### Custom Templates

Override default README template:

```yaml
workflow:
  config:
    template: ".claude/templates/custom-branch-readme.md"
```

### Webhooks

Trigger workflow on GitHub events:

```yaml
trigger:
  github:
    events: ["push", "pull_request"]
    branches: ["feature/*", "bugfix/*"]
```

### Notifications

Configure notifications for workflow completion:

```yaml
notifications:
  slack:
    channel: "#dev-updates"
    on: ["completion", "error"]
```

## Related Resources

- **collector-readme skill**: Core documentation generation
- **GitHub API Integration**: Branch data fetching
- **Git Analysis Tools**: Diff and commit analysis
- **TOON Workflow Engine**: Workflow orchestration

## Support

For issues or questions:
- Check workflow logs: `.claude/logs/workflows/branch-review/`
- Review error messages in step outputs
- Consult collector-orchestrator documentation
- File issues in the moai-adk repository
