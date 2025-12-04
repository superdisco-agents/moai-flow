# Step 04: Apply Changes

## Overview
Execute the approved changes according to the execution plan, handle merge conflicts, validate quality gates, and update the local repository.

## Agent
**git-collector**

## Inputs

### From step-03-decide
- User decisions (approved/rejected/deferred)
- Execution plan
- Decision summary
- Validation results

### From step-02-learn
- Scored changes with metadata

### From step-01-scan
- Repository state
- Change graph

## Actions

### 1. Prepare Workspace
```bash
# Create checkpoint for rollback
git stash push -u -m "Pre-sync checkpoint $(date +%s)"

# Record current state
CHECKPOINT_SHA=$(git rev-parse HEAD)
echo $CHECKPOINT_SHA > .git/sync-checkpoint

# Ensure working directory is clean
git status --porcelain | wc -l  # Should be 0

# Verify remote connectivity
git fetch origin --dry-run
```

### 2. Execute Phase 1: Safe Changes
```javascript
async function executeSafeChanges(phase) {
  const results = [];

  // Safe changes can be applied in parallel
  await Promise.all(phase.changes.map(async (changeId) => {
    const change = getChangeById(changeId);

    try {
      if (change.source === 'remote') {
        // Pull from remote
        await git.merge(change.commit, {
          strategy: 'ours',
          ff_only: true
        });
      } else {
        // Apply local change
        await git.cherry_pick(change.commit);
      }

      results.push({
        change_id: changeId,
        status: 'success',
        timestamp: new Date().toISOString()
      });
    } catch (error) {
      results.push({
        change_id: changeId,
        status: 'failed',
        error: error.message,
        timestamp: new Date().toISOString()
      });
    }
  }));

  return results;
}
```

### 3. Execute Phase 2: Medium-Risk Changes
```bash
# Apply changes sequentially with validation
for change_id in "${MEDIUM_RISK_CHANGES[@]}"; do
  echo "Applying change: $change_id"

  # Get change details
  COMMIT_SHA=$(get_commit_sha "$change_id")

  # Try merge
  git merge "$COMMIT_SHA" --no-ff -m "Merge: $change_id"

  if [ $? -ne 0 ]; then
    echo "Merge conflict detected for $change_id"

    # Attempt auto-resolution
    if auto_resolve_conflict "$change_id"; then
      echo "Conflict auto-resolved"
      git add .
      git commit -m "Auto-resolve conflict for $change_id"
    else
      echo "Manual resolution required"
      # Save conflict state
      save_conflict_state "$change_id"

      # Abort merge
      git merge --abort

      # Continue to next or stop based on plan
      if [ "$ROLLBACK_ON_ERROR" = true ]; then
        echo "Rolling back to checkpoint"
        rollback_to_checkpoint
        exit 1
      fi
    fi
  fi

  # Create checkpoint after successful merge
  git tag "sync-checkpoint-$change_id"
done
```

### 4. Execute Phase 3: High-Risk Changes
```javascript
async function executeHighRiskChanges(phase) {
  const results = [];

  for (const changeId of phase.changes) {
    const change = getChangeById(changeId);

    // Apply change
    try {
      await applyChange(change);

      // Run quality gates
      console.log('Running quality gates...');
      const qualityResults = await runQualityGates(phase.quality_gates);

      if (!qualityResults.passed) {
        console.error('Quality gates failed:', qualityResults.failures);

        // Rollback this change
        await rollbackChange(change);

        results.push({
          change_id: changeId,
          status: 'failed',
          reason: 'quality_gates_failed',
          details: qualityResults.failures
        });

        // Decide whether to continue
        if (phase.rollback_on_error) {
          throw new Error('Quality gates failed, rolling back all changes');
        }

        continue;
      }

      // Create checkpoint
      await createCheckpoint(changeId);

      results.push({
        change_id: changeId,
        status: 'success',
        quality_gates: qualityResults
      });

    } catch (error) {
      results.push({
        change_id: changeId,
        status: 'failed',
        error: error.message
      });

      if (phase.rollback_on_error) {
        throw error;
      }
    }
  }

  return results;
}
```

### 5. Handle Merge Conflicts
```javascript
async function handleConflicts(change) {
  // Detect conflict type
  const conflicts = await git.status({ fs, dir: '/' });
  const conflictedFiles = conflicts.filter(f =>
    f.status.includes('conflict')
  );

  for (const file of conflictedFiles) {
    const resolution = await attemptAutoResolution(file);

    if (resolution.success) {
      console.log(`Auto-resolved: ${file.path}`);
      await git.add({ fs, dir: '/', filepath: file.path });
    } else {
      console.log(`Manual resolution required: ${file.path}`);

      // Present conflict to user
      const userResolution = await promptConflictResolution({
        file: file.path,
        local_version: resolution.local,
        remote_version: resolution.remote,
        base_version: resolution.base
      });

      if (userResolution.action === 'use_local') {
        await git.checkout({
          fs,
          dir: '/',
          filepath: file.path,
          ours: true
        });
      } else if (userResolution.action === 'use_remote') {
        await git.checkout({
          fs,
          dir: '/',
          filepath: file.path,
          theirs: true
        });
      } else if (userResolution.action === 'manual') {
        // Open editor for manual resolution
        await openEditorForResolution(file.path);

        // Wait for user to resolve
        await waitForResolution(file.path);
      } else if (userResolution.action === 'skip') {
        // Skip this change
        return { skipped: true, file: file.path };
      }

      await git.add({ fs, dir: '/', filepath: file.path });
    }
  }

  // Commit resolved conflicts
  await git.commit({
    fs,
    dir: '/',
    message: `Resolve conflicts for ${change.id}`,
    author: {
      name: 'MoAI Sync',
      email: 'sync@moai.local'
    }
  });

  return { resolved: true };
}
```

### 6. Run Quality Gates
```bash
#!/bin/bash
# quality-gates.sh

run_quality_gates() {
  local gates=("$@")
  local failed=0

  for gate in "${gates[@]}"; do
    echo "Running quality gate: $gate"

    case "$gate" in
      tests)
        if ! npm test; then
          echo "❌ Tests failed"
          failed=$((failed + 1))
        else
          echo "✅ Tests passed"
        fi
        ;;

      lint)
        if ! npm run lint; then
          echo "❌ Linting failed"
          failed=$((failed + 1))
        else
          echo "✅ Linting passed"
        fi
        ;;

      type_check)
        if ! npm run type-check; then
          echo "❌ Type checking failed"
          failed=$((failed + 1))
        else
          echo "✅ Type checking passed"
        fi
        ;;

      build)
        if ! npm run build; then
          echo "❌ Build failed"
          failed=$((failed + 1))
        else
          echo "✅ Build successful"
        fi
        ;;

      *)
        echo "⚠️  Unknown quality gate: $gate"
        ;;
    esac
  done

  if [ $failed -gt 0 ]; then
    echo "Quality gates failed: $failed"
    return 1
  else
    echo "All quality gates passed"
    return 0
  fi
}
```

### 7. Create Checkpoints
```bash
create_checkpoint() {
  local checkpoint_id=$1
  local timestamp=$(date +%s)

  # Create git tag
  git tag "sync-checkpoint-${checkpoint_id}-${timestamp}"

  # Save checkpoint metadata
  cat > ".git/sync-checkpoints/${checkpoint_id}.json" <<EOF
{
  "id": "${checkpoint_id}",
  "timestamp": ${timestamp},
  "commit": "$(git rev-parse HEAD)",
  "branch": "$(git rev-parse --abbrev-ref HEAD)",
  "changes_applied": $(get_changes_applied_count),
  "quality_gates_passed": true
}
EOF

  echo "Checkpoint created: ${checkpoint_id}"
}
```

### 8. Rollback on Failure
```bash
rollback_to_checkpoint() {
  local checkpoint_sha=$(cat .git/sync-checkpoint)

  echo "Rolling back to checkpoint: ${checkpoint_sha}"

  # Reset to checkpoint
  git reset --hard "${checkpoint_sha}"

  # Restore stashed changes if any
  if git stash list | grep -q "Pre-sync checkpoint"; then
    git stash pop
  fi

  echo "Rollback complete"
}
```

## Outputs

### Merge Results
```json
{
  "phases_completed": 3,
  "total_changes_applied": 10,
  "results_by_phase": {
    "safe_changes": {
      "attempted": 3,
      "succeeded": 3,
      "failed": 0,
      "duration_ms": 1847
    },
    "medium_risk_changes": {
      "attempted": 4,
      "succeeded": 4,
      "failed": 0,
      "conflicts_resolved": 1,
      "duration_ms": 4932
    },
    "high_risk_changes": {
      "attempted": 3,
      "succeeded": 3,
      "failed": 0,
      "quality_gates_run": 3,
      "duration_ms": 14205
    }
  },
  "total_duration_ms": 20984
}
```

### Conflict Resolution Report
```json
{
  "conflicts_detected": 2,
  "conflicts_resolved": 2,
  "resolution_methods": [
    {
      "file": "src/config.ts",
      "method": "auto",
      "strategy": "prefer_remote",
      "confidence": 0.85
    },
    {
      "file": "package.json",
      "method": "manual",
      "resolution_time_ms": 45000
    }
  ],
  "unresolved_conflicts": []
}
```

### Quality Gate Results
```json
{
  "gates_run": ["tests", "lint", "type_check"],
  "results": {
    "tests": {
      "passed": true,
      "total": 234,
      "failed": 0,
      "skipped": 3,
      "duration_ms": 8923
    },
    "lint": {
      "passed": true,
      "warnings": 2,
      "errors": 0,
      "duration_ms": 1234
    },
    "type_check": {
      "passed": true,
      "errors": 0,
      "duration_ms": 3456
    }
  },
  "overall_passed": true
}
```

### Repository State
```json
{
  "before": {
    "commit": "abc123",
    "branch": "main",
    "uncommitted_changes": 0
  },
  "after": {
    "commit": "xyz789",
    "branch": "main",
    "uncommitted_changes": 0,
    "commits_ahead": 10,
    "commits_behind": 0
  },
  "checkpoints_created": [
    "sync-checkpoint-safe-changes-1733312400",
    "sync-checkpoint-medium-risk-1733312405",
    "sync-checkpoint-high-risk-1733312420"
  ]
}
```

## Error Handling

### Merge Conflicts
- Attempt automatic resolution
- Present to user if auto-resolution fails
- Allow skip/retry/abort options
- Save conflict state for later resolution

### Quality Gate Failures
- Rollback failing change
- Report specific failures
- Allow user to fix and retry
- Continue or abort based on plan

### Network Errors
- Retry with exponential backoff
- Cache partial results
- Continue with local operations
- Report sync incomplete

### Git Errors
- Validate git state
- Attempt repair if possible
- Rollback to checkpoint
- Preserve user data

## Success Criteria
✅ All approved changes applied
✅ Conflicts resolved (auto or manual)
✅ Quality gates passed
✅ Repository in clean state
✅ Checkpoints created successfully

## Next Step
Proceed to **step-05-publish** with:
- Merge results
- Conflict resolution report
- Quality gate results
- Updated repository state

(Only if sync_mode=bidirectional and has local changes)
