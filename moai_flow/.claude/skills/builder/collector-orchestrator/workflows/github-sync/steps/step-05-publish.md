# Step 05: Create Pull Request

## Overview
Push approved local changes to GitHub and create a pull request for review. This step only executes in bidirectional mode when there are local changes to publish.

## Agent
**github-collector**

## Inputs

### From step-04-merge
- Merge results
- Quality gate results
- Updated repository state

### From Workflow Configuration
- `create_pr`: Boolean flag to create PR
- `sync_mode`: Must be "bidirectional"

### From step-03-decide
- Decision summary
- User-approved local changes

## Prerequisites
- `sync_mode === 'bidirectional'`
- Local commits ahead of remote
- `create_pr === true`
- Quality gates passed

## Actions

### 1. Validate Prerequisites
```javascript
function validatePublishPrerequisites(state, config) {
  const validations = [];

  // Check sync mode
  if (config.sync_mode !== 'bidirectional') {
    return {
      valid: false,
      reason: 'Publishing only available in bidirectional mode',
      skip: true
    };
  }

  // Check for local changes
  if (state.commits_ahead === 0) {
    return {
      valid: false,
      reason: 'No local changes to publish',
      skip: true
    };
  }

  // Check create_pr flag
  if (!config.create_pr) {
    return {
      valid: false,
      reason: 'PR creation disabled in configuration',
      skip: true
    };
  }

  // Check quality gates
  if (!state.quality_gates_passed) {
    return {
      valid: false,
      reason: 'Quality gates must pass before publishing',
      skip: false,
      blocking: true
    };
  }

  return { valid: true };
}
```

### 2. Prepare Local Changes
```bash
# Ensure we're on the correct branch
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)

# Check if we should create a feature branch for PR
if [ "$CURRENT_BRANCH" = "main" ] || [ "$CURRENT_BRANCH" = "master" ]; then
  # Create feature branch from main
  FEATURE_BRANCH="moai-sync/$(date +%Y%m%d-%H%M%S)"
  git checkout -b "$FEATURE_BRANCH"
  echo "Created feature branch: $FEATURE_BRANCH"
else
  FEATURE_BRANCH="$CURRENT_BRANCH"
fi

# Get list of commits to publish
COMMITS_TO_PUBLISH=$(git log origin/main..HEAD --oneline)
echo "Commits to publish:"
echo "$COMMITS_TO_PUBLISH"
```

### 3. Push to Remote
```javascript
async function pushToRemote(branch, options = {}) {
  const pushOptions = {
    remote: 'origin',
    branch: branch,
    force: options.force || false,
    setUpstream: true
  };

  try {
    console.log(`Pushing ${branch} to remote...`);

    await git.push({
      fs,
      http,
      dir: '/',
      remote: pushOptions.remote,
      ref: pushOptions.branch,
      force: pushOptions.force,
      onAuth: () => getGitHubCredentials()
    });

    console.log('Push successful');

    return {
      success: true,
      branch: pushOptions.branch,
      remote: pushOptions.remote
    };

  } catch (error) {
    console.error('Push failed:', error.message);

    // Handle specific push errors
    if (error.message.includes('rejected')) {
      return {
        success: false,
        error: 'push_rejected',
        message: 'Remote has changes that need to be pulled first',
        suggestion: 'Run sync again to pull remote changes'
      };
    } else if (error.message.includes('authentication')) {
      return {
        success: false,
        error: 'authentication_failed',
        message: 'GitHub authentication failed',
        suggestion: 'Check your GitHub token permissions'
      };
    } else {
      return {
        success: false,
        error: 'push_failed',
        message: error.message
      };
    }
  }
}
```

### 4. Generate PR Content
```javascript
function generatePRContent(mergeResults, commits, config) {
  // Extract commit messages
  const commitMessages = commits.map(c => c.message);

  // Categorize changes
  const changesByType = categorizeCommits(commitMessages);

  // Generate title
  const title = generatePRTitle(changesByType, commits.length);

  // Generate body
  const body = `
## Summary
This PR contains ${commits.length} commit(s) synchronized from local development.

## Changes
${generateChangesList(changesByType)}

## Quality Checks
${generateQualityReport(mergeResults.quality_gates)}

## Files Changed
${generateFilesChangedSummary(commits)}

## Testing
- [x] All tests passing
- [x] Linting passed
- [x] Type checking passed

## Sync Metadata
- **Sync Mode**: ${config.sync_mode}
- **Sync Timestamp**: ${new Date().toISOString()}
- **Changes Applied**: ${commits.length}
- **Quality Gates**: ${Object.keys(mergeResults.quality_gates).join(', ')}

---
🤖 Generated with [Claude Code](https://claude.com/claude-code)

*This PR was automatically created by MoAI-Flow GitHub Sync workflow*
  `.trim();

  return { title, body };
}

function generatePRTitle(changesByType, totalCommits) {
  // Prioritize by change type
  if (changesByType.feature.length > 0) {
    return changesByType.feature.length === 1
      ? changesByType.feature[0]
      : `feat: Multiple feature updates (${totalCommits} commits)`;
  } else if (changesByType.fix.length > 0) {
    return changesByType.fix.length === 1
      ? changesByType.fix[0]
      : `fix: Multiple bug fixes (${totalCommits} commits)`;
  } else if (changesByType.refactor.length > 0) {
    return `refactor: Code improvements (${totalCommits} commits)`;
  } else if (changesByType.docs.length > 0) {
    return `docs: Documentation updates (${totalCommits} commits)`;
  } else {
    return `chore: Multiple updates (${totalCommits} commits)`;
  }
}

function generateChangesList(changesByType) {
  let markdown = '';

  const typeLabels = {
    feature: '✨ Features',
    fix: '🐛 Bug Fixes',
    refactor: '♻️ Refactoring',
    docs: '📝 Documentation',
    test: '✅ Tests',
    chore: '🔧 Chores'
  };

  for (const [type, label] of Object.entries(typeLabels)) {
    if (changesByType[type].length > 0) {
      markdown += `\n### ${label}\n`;
      changesByType[type].forEach(change => {
        markdown += `- ${change}\n`;
      });
    }
  }

  return markdown;
}

function generateQualityReport(qualityGates) {
  let report = '';

  for (const [gate, result] of Object.entries(qualityGates)) {
    const status = result.passed ? '✅' : '❌';
    report += `- ${status} **${gate}**: `;

    if (gate === 'tests') {
      report += `${result.total - result.failed}/${result.total} passed`;
    } else if (gate === 'lint') {
      report += result.errors === 0 ? 'No errors' : `${result.errors} errors`;
    } else {
      report += result.passed ? 'Passed' : 'Failed';
    }

    report += '\n';
  }

  return report;
}
```

### 5. Create Pull Request
```javascript
async function createPullRequest(branch, content, options = {}) {
  const defaultBaseBranch = 'main';
  const baseBranch = options.baseBranch || defaultBaseBranch;

  try {
    // Create PR using GitHub API
    const response = await octokit.rest.pulls.create({
      owner: getRepoOwner(),
      repo: getRepoName(),
      title: content.title,
      body: content.body,
      head: branch,
      base: baseBranch,
      draft: options.draft || false
    });

    const pr = response.data;

    console.log(`Pull request created: #${pr.number}`);
    console.log(`URL: ${pr.html_url}`);

    // Add labels
    if (options.labels && options.labels.length > 0) {
      await octokit.rest.issues.addLabels({
        owner: getRepoOwner(),
        repo: getRepoName(),
        issue_number: pr.number,
        labels: options.labels
      });
    }

    // Request reviewers
    if (options.reviewers && options.reviewers.length > 0) {
      await octokit.rest.pulls.requestReviewers({
        owner: getRepoOwner(),
        repo: getRepoName(),
        pull_number: pr.number,
        reviewers: options.reviewers
      });
    }

    // Add to project board
    if (options.projectId) {
      await addPRToProject(pr.number, options.projectId);
    }

    return {
      success: true,
      pr_number: pr.number,
      pr_url: pr.html_url,
      pr_id: pr.id
    };

  } catch (error) {
    console.error('Failed to create PR:', error.message);

    return {
      success: false,
      error: error.message,
      code: error.status
    };
  }
}
```

### 6. Add PR Metadata
```javascript
async function enrichPR(prNumber, metadata) {
  // Add sync metadata as comment
  const comment = `
### Sync Metadata

| Property | Value |
|----------|-------|
| Workflow | github-sync |
| Version | ${metadata.workflow_version} |
| Session ID | ${metadata.session_id} |
| Total Changes | ${metadata.total_changes} |
| Changes Applied | ${metadata.changes_applied} |
| Conflicts Resolved | ${metadata.conflicts_resolved} |
| Quality Gates | ${metadata.quality_gates.join(', ')} |

<details>
<summary>Detailed Change Log</summary>

\`\`\`json
${JSON.stringify(metadata.changes, null, 2)}
\`\`\`

</details>
  `;

  await octokit.rest.issues.createComment({
    owner: getRepoOwner(),
    repo: getRepoName(),
    issue_number: prNumber,
    body: comment
  });

  // Add labels based on change types
  const labels = inferLabelsFromChanges(metadata.changes);
  if (labels.length > 0) {
    await octokit.rest.issues.addLabels({
      owner: getRepoOwner(),
      repo: getRepoName(),
      issue_number: prNumber,
      labels: labels
    });
  }
}
```

### 7. Notify Stakeholders
```javascript
async function notifyStakeholders(pr, notificationConfig) {
  const notifications = [];

  // Notify on Slack
  if (notificationConfig.slack?.enabled) {
    await sendSlackNotification({
      channel: notificationConfig.slack.channel,
      message: `New PR created: ${pr.title}`,
      url: pr.pr_url,
      author: pr.author
    });
    notifications.push('slack');
  }

  // Notify on Discord
  if (notificationConfig.discord?.enabled) {
    await sendDiscordNotification({
      webhook: notificationConfig.discord.webhook,
      content: `📋 New PR: ${pr.pr_url}`
    });
    notifications.push('discord');
  }

  // Email notification
  if (notificationConfig.email?.enabled) {
    await sendEmailNotification({
      to: notificationConfig.email.recipients,
      subject: `New PR: ${pr.title}`,
      body: generateEmailBody(pr)
    });
    notifications.push('email');
  }

  return notifications;
}
```

## Outputs

### Push Results
```json
{
  "success": true,
  "branch": "moai-sync/20251204-104530",
  "remote": "origin",
  "commits_pushed": 5,
  "push_timestamp": "2025-12-04T10:45:35Z"
}
```

### Pull Request Details
```json
{
  "success": true,
  "pr_number": 123,
  "pr_url": "https://github.com/org/repo/pull/123",
  "pr_id": 987654321,
  "title": "feat: Multiple feature updates (5 commits)",
  "branch": {
    "head": "moai-sync/20251204-104530",
    "base": "main"
  },
  "status": "open",
  "draft": false,
  "created_at": "2025-12-04T10:45:40Z"
}
```

### PR Metadata
```json
{
  "workflow_version": "1.0.0",
  "session_id": "sync_20251204_1045",
  "total_changes": 18,
  "changes_applied": 10,
  "conflicts_resolved": 2,
  "quality_gates": ["tests", "lint", "type_check"],
  "labels_applied": ["feature", "sync", "automated"],
  "reviewers_requested": ["tech-lead", "senior-dev"],
  "notifications_sent": ["slack", "email"]
}
```

### Notification Results
```json
{
  "notifications_sent": ["slack", "email"],
  "slack": {
    "success": true,
    "channel": "#engineering",
    "message_ts": "1733312740.123456"
  },
  "email": {
    "success": true,
    "recipients": 2,
    "message_id": "abc123def456"
  }
}
```

## Error Handling

### Push Rejected
- Remote has conflicting changes
- Pull remote changes first
- Re-run workflow

### PR Creation Failed
- Branch protection rules violated
- Check permissions
- Verify base branch exists

### Authentication Failed
- Invalid GitHub token
- Insufficient permissions
- Update credentials

### Network Errors
- Retry with exponential backoff
- Cache push results
- Notify user of partial completion

## Success Criteria
✅ Local changes pushed to remote
✅ Pull request created successfully
✅ PR metadata added
✅ Labels and reviewers assigned
✅ Stakeholders notified

## Workflow Complete
All steps finished successfully. Final outputs:
- Sync report
- Changes applied
- PR URL
- Conflict resolution report (if any)
