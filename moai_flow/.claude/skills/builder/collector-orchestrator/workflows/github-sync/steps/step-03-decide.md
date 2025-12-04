# Step 03: Present Decisions

## Overview
Present scored changes and recommendations to the user in a clear, actionable format. Gather user approval/rejection for changes and build an execution plan.

## Agent
**collector-orchestrator**

## Inputs

### From step-02-learn
- Scored changes
- Recommendations
- Pattern analysis
- Learning insights

### From Workflow Configuration
- `auto_approve`: Boolean flag for automatic approval
- `sync_mode`: Unidirectional or bidirectional

## Actions

### 1. Categorize Changes
```javascript
function categorizeChanges(scoredChanges, recommendations) {
  return {
    auto_approved: recommendations.auto_approve
      .filter(r => workflow.auto_approve === true)
      .map(r => r.change_id),

    needs_review: recommendations.review_recommended
      .concat(
        workflow.auto_approve === false
          ? recommendations.auto_approve
          : []
      ),

    requires_attention: recommendations.manual_review_required,

    blocked: scoredChanges.filter(c =>
      c.conflict_prob > 0.8 || c.risk_score > 0.9
    )
  };
}
```

### 2. Format User Presentation
Generate human-readable summary:

```markdown
# GitHub Sync Decision Summary

## Overview
- **Total Changes**: 18
- **Auto-Approved**: 8 (low risk)
- **Review Recommended**: 7 (medium risk)
- **Requires Attention**: 3 (high risk)
- **Blocked**: 0

---

## Auto-Approved Changes (8)
These changes will be applied automatically (low risk, high confidence):

✅ **src/components/Button.tsx**
   - Type: Component update
   - Risk: 0.25 (Low)
   - Reason: Minor styling changes, well-tested

✅ **README.md**
   - Type: Documentation
   - Risk: 0.10 (Very Low)
   - Reason: Documentation update

✅ **src/utils/formatDate.ts**
   - Type: Utility function
   - Risk: 0.28 (Low)
   - Reason: Helper function with full test coverage

[... 5 more auto-approved changes]

---

## Review Recommended (7)
Quick review suggested for these medium-risk changes:

⚠️ **src/api/endpoints.ts**
   - Type: API changes
   - Risk: 0.52 (Medium)
   - Review Points:
     * Verify endpoint compatibility
     * Check for breaking changes
   - Estimated Review Time: 3 minutes
   - **[Approve / Reject]**

⚠️ **src/hooks/useAuth.ts**
   - Type: Authentication logic
   - Risk: 0.48 (Medium)
   - Review Points:
     * Review security implications
     * Verify token handling
   - Estimated Review Time: 5 minutes
   - **[Approve / Reject]**

[... 5 more changes for review]

---

## Requires Attention (3)
High-risk changes requiring careful review:

🚨 **package.json**
   - Type: Dependency update
   - Risk: 0.75 (High)
   - Critical Considerations:
     * React 18.2.0 → 18.3.0
     * Next.js 14.0.0 → 14.1.0
     * 5 transitive dependencies affected
   - Review Points:
     * Check breaking changes in React 18.3
     * Verify Next.js compatibility
     * Review security advisories
   - Estimated Review Time: 15 minutes
   - **[Approve / Reject]**

🚨 **src/core/database/schema.ts**
   - Type: Schema migration
   - Risk: 0.82 (High)
   - Critical Considerations:
     * Adds new required column
     * Affects 3 existing tables
     * Requires migration script
   - Review Points:
     * Verify migration safety
     * Check backward compatibility
     * Review rollback strategy
   - Estimated Review Time: 20 minutes
   - **[Approve / Reject]**

[... 1 more high-risk change]

---

## Decision Options

1. **Approve All Low/Medium Risk** (recommended)
   - Apply 15 changes automatically
   - Manual review for 3 high-risk changes

2. **Approve All**
   - Apply all 18 changes
   - ⚠️ Not recommended for high-risk changes

3. **Custom Selection**
   - Choose specific changes to apply
   - Defer others for later review

4. **Defer All**
   - Review all changes manually
   - No automatic application

**What would you like to do?**
```

### 3. Interactive Decision Gathering
```javascript
async function gatherDecisions(categorizedChanges) {
  const decisions = {
    approved: [],
    rejected: [],
    deferred: []
  };

  // Auto-approved (if enabled)
  if (workflow.auto_approve) {
    decisions.approved.push(...categorizedChanges.auto_approved);
  }

  // Interactive review
  for (const change of categorizedChanges.needs_review) {
    const decision = await promptUser({
      type: 'confirm',
      message: `Apply ${change.file}?`,
      details: formatChangeDetails(change),
      default: true
    });

    if (decision) {
      decisions.approved.push(change.id);
    } else {
      decisions.deferred.push(change.id);
    }
  }

  // High-risk changes
  for (const change of categorizedChanges.requires_attention) {
    const decision = await promptUser({
      type: 'expand',
      message: `High-risk change: ${change.file}`,
      details: formatChangeDetails(change),
      choices: [
        { key: 'a', name: 'Approve', value: 'approve' },
        { key: 'r', name: 'Reject', value: 'reject' },
        { key: 'd', name: 'Defer', value: 'defer' },
        { key: 'v', name: 'View diff', value: 'view' }
      ]
    });

    if (decision === 'approve') {
      decisions.approved.push(change.id);
    } else if (decision === 'reject') {
      decisions.rejected.push(change.id);
    } else {
      decisions.deferred.push(change.id);
    }
  }

  return decisions;
}
```

### 4. Build Execution Plan
```javascript
function buildExecutionPlan(decisions, scoredChanges) {
  const plan = {
    phases: [],
    rollback_points: [],
    estimated_duration: 0
  };

  // Phase 1: Safe changes (docs, tests)
  const safeChanges = decisions.approved.filter(id =>
    scoredChanges[id].risk_score < 0.3
  );

  plan.phases.push({
    name: 'safe_changes',
    changes: safeChanges,
    parallel: true,
    rollback_on_error: false
  });

  // Phase 2: Medium-risk changes
  const mediumChanges = decisions.approved.filter(id =>
    scoredChanges[id].risk_score >= 0.3 &&
    scoredChanges[id].risk_score < 0.6
  );

  plan.phases.push({
    name: 'medium_risk_changes',
    changes: mediumChanges,
    parallel: false,
    rollback_on_error: true,
    checkpoint: true
  });

  // Phase 3: High-risk changes
  const highRiskChanges = decisions.approved.filter(id =>
    scoredChanges[id].risk_score >= 0.6
  );

  plan.phases.push({
    name: 'high_risk_changes',
    changes: highRiskChanges,
    parallel: false,
    rollback_on_error: true,
    checkpoint: true,
    quality_gates: ['tests', 'lint', 'type_check']
  });

  return plan;
}
```

### 5. Validate Decisions
```javascript
function validateDecisions(decisions, scoredChanges) {
  const validations = [];

  // Check for dependency conflicts
  const dependencies = analyzeDependencies(decisions.approved);
  if (dependencies.conflicts.length > 0) {
    validations.push({
      type: 'warning',
      message: 'Dependency conflicts detected',
      details: dependencies.conflicts
    });
  }

  // Check for required changes
  const missing = findMissingRequiredChanges(decisions.approved);
  if (missing.length > 0) {
    validations.push({
      type: 'error',
      message: 'Some approved changes require other changes',
      details: missing
    });
  }

  // Check for breaking change order
  const ordering = validateChangeOrdering(decisions.approved);
  if (!ordering.valid) {
    validations.push({
      type: 'warning',
      message: 'Changes should be applied in different order',
      suggestion: ordering.suggested_order
    });
  }

  return validations;
}
```

### 6. Generate Decision Summary
```javascript
function generateDecisionSummary(decisions, executionPlan) {
  return {
    timestamp: new Date().toISOString(),
    total_changes: decisions.approved.length +
                   decisions.rejected.length +
                   decisions.deferred.length,
    approved: decisions.approved.length,
    rejected: decisions.rejected.length,
    deferred: decisions.deferred.length,
    execution_phases: executionPlan.phases.length,
    estimated_duration: executionPlan.estimated_duration,
    quality_gates: executionPlan.phases
      .flatMap(p => p.quality_gates || []),
    rollback_points: executionPlan.rollback_points.length
  };
}
```

## Outputs

### User Decisions
```json
{
  "approved": [
    "change_001",
    "change_003",
    "change_004",
    "change_005",
    "change_007",
    "change_008",
    "change_009",
    "change_011",
    "change_012",
    "change_015"
  ],
  "rejected": [
    "change_013"
  ],
  "deferred": [
    "change_002",
    "change_006",
    "change_010",
    "change_014",
    "change_016",
    "change_017",
    "change_018"
  ]
}
```

### Execution Plan
```json
{
  "phases": [
    {
      "name": "safe_changes",
      "order": 1,
      "changes": ["change_001", "change_003", "change_004"],
      "parallel": true,
      "rollback_on_error": false,
      "estimated_duration_ms": 2000
    },
    {
      "name": "medium_risk_changes",
      "order": 2,
      "changes": ["change_005", "change_007", "change_008", "change_009"],
      "parallel": false,
      "rollback_on_error": true,
      "checkpoint": true,
      "estimated_duration_ms": 5000
    },
    {
      "name": "high_risk_changes",
      "order": 3,
      "changes": ["change_011", "change_012", "change_015"],
      "parallel": false,
      "rollback_on_error": true,
      "checkpoint": true,
      "quality_gates": ["tests", "lint", "type_check"],
      "estimated_duration_ms": 15000
    }
  ],
  "total_estimated_duration_ms": 22000,
  "rollback_points": [
    "after_phase_2",
    "after_phase_3"
  ]
}
```

### Decision Summary
```json
{
  "timestamp": "2025-12-04T10:45:00Z",
  "session_id": "sync_20251204_1045",
  "total_changes": 18,
  "breakdown": {
    "approved": 10,
    "rejected": 1,
    "deferred": 7
  },
  "execution_phases": 3,
  "estimated_duration_ms": 22000,
  "quality_gates": ["tests", "lint", "type_check"],
  "rollback_points": 2,
  "user_interaction": {
    "auto_approved": 3,
    "manually_reviewed": 7,
    "time_spent_reviewing_ms": 180000
  }
}
```

### Validation Results
```json
{
  "valid": true,
  "warnings": [
    {
      "type": "dependency_order",
      "message": "Change 'change_012' should be applied before 'change_015'",
      "severity": "low",
      "auto_resolved": true
    }
  ],
  "errors": []
}
```

## Error Handling

### User Cancellation
- Save partial decisions
- Allow resume later
- Clean up temporary state

### Invalid Selections
- Highlight conflicts
- Suggest corrections
- Allow re-selection

### Timeout
- Auto-defer pending decisions
- Save progress
- Notify user

## Success Criteria
✅ User decisions collected for all changes
✅ Execution plan generated and validated
✅ No blocking conflicts
✅ Rollback points established
✅ Quality gates defined

## Next Step
Proceed to **step-04-merge** with:
- User decisions
- Execution plan
- Decision summary
- Validation results
