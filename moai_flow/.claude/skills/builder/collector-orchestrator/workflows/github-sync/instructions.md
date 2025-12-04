# GitHub Sync Workflow Instructions

## Purpose

The `github-sync` workflow orchestrates intelligent, bidirectional synchronization between your local Git repository and GitHub remote. It goes beyond simple git pull/push by:

- **Learning** from code patterns and change history
- **Scoring** changes based on risk, impact, and quality
- **Deciding** which changes to apply based on learned patterns
- **Adapting** sync strategies based on project context

## When to Use

### Automatic Triggers
- **Post-commit**: After local commits to check for remote updates
- **Scheduled**: Periodic sync checks (e.g., every hour during active development)
- **CI/CD Integration**: As part of automated workflows

### Manual Invocation
- Before starting new feature work (pull latest changes)
- After completing a feature (push changes, create PR)
- When resolving merge conflicts
- During code review cycles

## Workflow Modes

### Unidirectional (Default)
```
GitHub → Local
```
- Pulls changes from GitHub to local
- Safest mode for consuming upstream updates
- No local changes pushed to remote
- Ideal for: consuming library updates, syncing team changes

### Bidirectional
```
GitHub ↔ Local
```
- Syncs in both directions
- Pushes approved local changes to GitHub
- Creates pull requests for review
- Ideal for: active development, collaborative workflows

## Expected Inputs

| Input | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `sync_mode` | enum | Yes | `unidirectional` | Direction of sync |
| `branch_filter` | string | No | `"main,develop"` | Branches to sync |
| `auto_approve` | boolean | No | `false` | Auto-approve low-risk changes |
| `create_pr` | boolean | No | `true` | Create PR in bidirectional mode |

### Example Usage

**Basic unidirectional sync:**
```bash
/moai-sync mode=unidirectional
```

**Bidirectional sync with PR:**
```bash
/moai-sync mode=bidirectional create_pr=true
```

**Auto-approve safe changes:**
```bash
/moai-sync mode=unidirectional auto_approve=true branch_filter="main"
```

## Expected Outputs

### Sync Report
```json
{
  "status": "success",
  "mode": "bidirectional",
  "branches_synced": ["main", "develop"],
  "changes_pulled": 15,
  "changes_pushed": 8,
  "conflicts": 0,
  "duration_ms": 2341
}
```

### Changes Applied
```json
[
  {
    "type": "file_update",
    "path": "src/components/Button.tsx",
    "action": "merged",
    "risk_score": 0.2,
    "confidence": 0.95
  },
  {
    "type": "dependency_update",
    "package": "react",
    "version": "18.2.0 → 18.3.0",
    "action": "applied",
    "risk_score": 0.1,
    "confidence": 0.99
  }
]
```

### PR URL
```
https://github.com/org/repo/pull/123
```

### Conflicts Detected
```json
[
  {
    "file": "src/utils/config.ts",
    "type": "merge_conflict",
    "local_version": "abc123",
    "remote_version": "def456",
    "resolution": "manual_required"
  }
]
```

## Integration with Collector Agents

### Git Collector
- **Role**: Executes git operations (fetch, pull, merge, push)
- **Steps Used**: step-01-scan, step-04-merge
- **Responsibilities**:
  - Scan local repository state
  - Fetch remote changes
  - Apply approved merges
  - Handle git conflicts

### GitHub Collector
- **Role**: Interacts with GitHub API
- **Steps Used**: step-01-scan, step-05-publish
- **Responsibilities**:
  - Fetch remote branch metadata
  - Retrieve PR information
  - Create new pull requests
  - Update PR status

### Collector Orchestrator
- **Role**: Decision-making and coordination
- **Steps Used**: step-02-learn, step-03-decide
- **Responsibilities**:
  - Score changes based on learned patterns
  - Decide which changes to apply
  - Present decisions to user
  - Coordinate between collectors

## Workflow Phases

### Phase 1: Discovery (step-01-scan)
- Scan local branches and commits
- Fetch remote branch information
- Identify divergences and conflicts
- Build change graph

### Phase 2: Learning (step-02-learn)
- Analyze change patterns
- Score changes by risk/impact
- Apply learned heuristics
- Generate recommendations

### Phase 3: Decision (step-03-decide)
- Present scored changes to user
- Highlight high-risk changes
- Get user approval/rejection
- Build execution plan

### Phase 4: Execution (step-04-merge)
- Apply approved changes
- Handle merge conflicts
- Validate code quality
- Update local repository

### Phase 5: Publication (step-05-publish)
- Push local changes (if bidirectional)
- Create pull request
- Add context and metadata
- Notify reviewers

## Success Criteria

✅ All approved changes applied successfully
✅ No unresolved merge conflicts
✅ Quality gates passed (tests, linting)
✅ Local and remote in expected state
✅ PR created (if bidirectional mode)

## Error Handling

### Automatic Recovery
- **Network failures**: Retry with exponential backoff
- **Temporary conflicts**: Attempt auto-resolution
- **Quality failures**: Rollback and notify

### Manual Intervention Required
- **Merge conflicts**: Present conflict details, request resolution
- **Breaking changes**: Require explicit approval
- **Test failures**: Block merge, show failure details

## Best Practices

1. **Start with unidirectional** until familiar with workflow
2. **Review high-risk changes** even with auto-approve enabled
3. **Use branch filters** to limit scope during initial testing
4. **Enable create_pr** for all bidirectional syncs
5. **Check sync reports** for patterns and issues
6. **Keep collectors updated** for latest GitHub API features

## Advanced Configuration

### Custom Risk Scoring
Modify collector-orchestrator's learning parameters to adjust risk scoring:
- File criticality weights
- Change type priorities
- Historical failure rates

### Integration Hooks
Add custom hooks for:
- Pre-sync validation
- Post-sync notifications
- Custom conflict resolution
- Quality gate integration

## Troubleshooting

### Common Issues

**"No changes detected"**
- Check branch_filter includes active branches
- Verify remote repository access
- Confirm local repository is up to date

**"Conflicts detected"**
- Review conflict details in output
- Use git tools to resolve manually
- Re-run workflow after resolution

**"PR creation failed"**
- Verify GitHub API token permissions
- Check branch protection rules
- Ensure no existing PR for branch

**"Quality gates failed"**
- Review test/lint output
- Fix issues locally
- Re-run workflow

## Related Workflows

- **code-review-sync**: Sync code review comments and feedback
- **dependency-update**: Automated dependency management
- **release-sync**: Coordinate releases between local and remote

## Support

For issues or questions:
1. Check workflow logs in `.claude/logs/workflows/github-sync/`
2. Review collector agent logs
3. Consult MoAI-Flow documentation
4. Contact development team
