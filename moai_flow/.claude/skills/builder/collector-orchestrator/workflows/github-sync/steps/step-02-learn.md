# Step 02: Score and Analyze

## Overview
Apply machine learning and heuristics to score changes, analyze patterns, and generate intelligent recommendations for synchronization decisions.

## Agent
**collector-orchestrator**

## Inputs

### From step-01-scan
- Repository state (local + remote)
- Divergence report
- Change graph
- Conflict analysis

### From Historical Data
- Past sync outcomes
- Failed merge history
- User preferences
- Project-specific patterns

## Actions

### 1. Score Changes by Risk
Apply multi-factor risk scoring algorithm:

```javascript
function calculateRiskScore(change) {
  const factors = {
    // File criticality
    file_criticality: assessFileCriticality(change.file),

    // Change magnitude
    change_size: (change.additions + change.deletions) / 1000,

    // Historical stability
    file_stability: getFileStabilityScore(change.file),

    // Test coverage impact
    test_impact: assessTestImpact(change),

    // Breaking change indicators
    breaking_keywords: detectBreakingKeywords(change.message),

    // Conflict probability
    conflict_prob: change.conflict_potential || 0,

    // Author reputation
    author_score: getAuthorReliability(change.author)
  };

  // Weighted average
  const weights = {
    file_criticality: 0.25,
    change_size: 0.15,
    file_stability: 0.15,
    test_impact: 0.20,
    breaking_keywords: 0.15,
    conflict_prob: 0.05,
    author_score: 0.05
  };

  return Object.keys(factors).reduce((score, key) => {
    return score + (factors[key] * weights[key]);
  }, 0);
}
```

### 2. Assess File Criticality
```javascript
const criticalityMap = {
  // Critical files (score: 1.0)
  critical: [
    /package\.json$/,
    /package-lock\.json$/,
    /yarn\.lock$/,
    /migrations?\//,
    /\.env/,
    /config\.(ts|js|json)$/,
    /schema\.(ts|js|sql)$/
  ],

  // High priority (score: 0.7)
  high: [
    /src\/core\//,
    /src\/lib\//,
    /src\/utils\//,
    /\.github\/workflows\//
  ],

  // Medium priority (score: 0.4)
  medium: [
    /src\/components\//,
    /src\/pages\//,
    /tests?\//
  ],

  // Low priority (score: 0.1)
  low: [
    /README\.md$/,
    /docs?\//,
    /\.md$/,
    /examples?\//
  ]
};
```

### 3. Detect Breaking Changes
```javascript
const breakingChangePatterns = [
  // Semantic version indicators
  /BREAKING CHANGE:/i,
  /breaking:/i,

  // API changes
  /remove\s+\w+\s+(function|method|class)/i,
  /delete\s+\w+\s+(api|endpoint)/i,
  /deprecate/i,

  // Database changes
  /drop\s+(table|column|index)/i,
  /alter\s+table/i,
  /migration/i,

  // Configuration changes
  /change\s+config/i,
  /update\s+env/i,
  /new\s+required/i
];
```

### 4. Analyze Change Patterns
```javascript
// Group changes by type
const changesByType = {
  feature: [],
  fix: [],
  refactor: [],
  docs: [],
  test: [],
  chore: [],
  breaking: []
};

// Identify trends
const trends = {
  frequent_files: getMostChangedFiles(),
  active_authors: getMostActiveAuthors(),
  change_velocity: getChangeVelocity(),
  quality_trend: getQualityTrend()
};

// Detect anomalies
const anomalies = {
  unusual_change_size: detectUnusualChangeSize(),
  unexpected_files: detectUnexpectedFileChanges(),
  off_hours_commits: detectOffHoursCommits()
};
```

### 5. Generate Recommendations
```javascript
function generateRecommendations(scoredChanges) {
  const recommendations = [];

  for (const change of scoredChanges) {
    if (change.risk_score < 0.3) {
      recommendations.push({
        change,
        action: 'auto_approve',
        confidence: 0.95,
        reason: 'Low risk, safe to apply automatically'
      });
    } else if (change.risk_score < 0.6) {
      recommendations.push({
        change,
        action: 'review_recommended',
        confidence: 0.75,
        reason: 'Medium risk, quick review suggested'
      });
    } else {
      recommendations.push({
        change,
        action: 'manual_review_required',
        confidence: 0.95,
        reason: 'High risk, detailed review necessary'
      });
    }
  }

  return recommendations;
}
```

### 6. Learn from History
```javascript
// Update learning model based on past outcomes
function updateLearningModel(historicalData) {
  // Adjust file criticality weights
  const fileSuccessRates = calculateFileSuccessRates(historicalData);
  updateFileCriticalityWeights(fileSuccessRates);

  // Refine author reliability scores
  const authorMetrics = calculateAuthorMetrics(historicalData);
  updateAuthorReliability(authorMetrics);

  // Tune risk thresholds
  const optimalThresholds = optimizeRiskThresholds(historicalData);
  updateRiskThresholds(optimalThresholds);

  // Save updated model
  persistLearningModel();
}
```

## Outputs

### Scored Changes
```json
{
  "changes": [
    {
      "id": "change_001",
      "type": "file_update",
      "file": "src/components/Button.tsx",
      "commit": "abc123",
      "author": "dev@example.com",
      "risk_score": 0.25,
      "risk_factors": {
        "file_criticality": 0.4,
        "change_size": 0.05,
        "file_stability": 0.9,
        "test_impact": 0.1,
        "breaking_keywords": 0.0,
        "conflict_prob": 0.0,
        "author_score": 0.95
      },
      "impact_assessment": {
        "files_affected": 1,
        "tests_affected": 2,
        "dependencies_affected": 0,
        "breaking_change": false
      }
    },
    {
      "id": "change_002",
      "type": "dependency_update",
      "file": "package.json",
      "commit": "def456",
      "author": "maintainer@example.com",
      "risk_score": 0.75,
      "risk_factors": {
        "file_criticality": 1.0,
        "change_size": 0.02,
        "file_stability": 0.6,
        "test_impact": 0.5,
        "breaking_keywords": 0.0,
        "conflict_prob": 0.2,
        "author_score": 0.99
      },
      "impact_assessment": {
        "files_affected": 1,
        "tests_affected": "unknown",
        "dependencies_affected": 5,
        "breaking_change": "potential"
      }
    }
  ],
  "total_changes": 18,
  "avg_risk_score": 0.42
}
```

### Recommendations
```json
{
  "auto_approve": [
    {
      "change_id": "change_001",
      "confidence": 0.95,
      "reason": "Low-risk component update with good test coverage"
    },
    {
      "change_id": "change_003",
      "confidence": 0.92,
      "reason": "Documentation update, no code impact"
    }
  ],
  "review_recommended": [
    {
      "change_id": "change_005",
      "confidence": 0.75,
      "reason": "Medium-risk refactor, quick review suggested",
      "review_points": [
        "Check backward compatibility",
        "Verify test coverage"
      ]
    }
  ],
  "manual_review_required": [
    {
      "change_id": "change_002",
      "confidence": 0.95,
      "reason": "Critical file (package.json) with dependency updates",
      "review_points": [
        "Review breaking changes in dependencies",
        "Check for security vulnerabilities",
        "Verify compatibility with current codebase"
      ]
    }
  ]
}
```

### Pattern Analysis
```json
{
  "trends": {
    "most_active_files": [
      {
        "path": "src/components/Button.tsx",
        "changes": 12,
        "trend": "stable"
      }
    ],
    "change_velocity": {
      "last_7_days": 23,
      "last_30_days": 87,
      "trend": "increasing"
    },
    "quality_metrics": {
      "test_coverage_trend": "improving",
      "merge_conflict_rate": 0.05,
      "rollback_rate": 0.02
    }
  },
  "anomalies": [
    {
      "type": "unusual_change_size",
      "change_id": "change_010",
      "details": "1500 lines changed vs. avg 150"
    }
  ]
}
```

### Learning Insights
```json
{
  "model_version": "2.1.0",
  "last_updated": "2025-12-04T10:30:00Z",
  "insights": [
    "Files in src/core/ have 95% successful merge rate",
    "Author dev@example.com has 99% successful commit rate",
    "Changes under 100 lines rarely cause conflicts",
    "Dependency updates require 2x review time on average"
  ],
  "weight_adjustments": {
    "file_criticality": "+0.05",
    "test_impact": "+0.03",
    "author_score": "-0.02"
  }
}
```

## Error Handling

### Insufficient Historical Data
- Use default weights
- Flag recommendations as "low confidence"
- Gather more data for future iterations

### Scoring Failures
- Fall back to conservative scoring
- Flag changes as "requires review"
- Log for model improvement

### Anomaly Detection Errors
- Continue without anomaly detection
- Log errors for debugging
- Notify for manual review

## Success Criteria
✅ All changes scored successfully
✅ Recommendations generated
✅ Pattern analysis complete
✅ Learning model updated
✅ High-confidence recommendations identified

## Next Step
Proceed to **step-03-decide** with:
- Scored changes
- Recommendations
- Pattern analysis
- Learning insights
