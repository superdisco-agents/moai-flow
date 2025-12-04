# Step 02: Score and Analyze Branch

## Overview

This step analyzes the branch data to generate quality scores, risk assessments, and actionable recommendations.

## Inputs

- **branch_data** (object): Branch metadata from step-01-fetch
- **commits** (array): Commit history from step-01-fetch
- **files_changed** (array): File changes from step-01-fetch
- **include_diff** (boolean): Whether to perform detailed diff analysis

## Process

### 1. Code Quality Scoring

Evaluate code quality based on multiple factors:

```python
def calculate_code_quality_score(commits, files_changed):
    """Calculate code quality score (0-100)"""

    scores = []

    # Commit message quality (0-100)
    commit_score = analyze_commit_messages(commits)
    scores.append(("commit_messages", commit_score, 0.25))

    # File organization (0-100)
    file_org_score = analyze_file_organization(files_changed)
    scores.append(("file_organization", file_org_score, 0.20))

    # Code churn (0-100, lower churn = higher score)
    churn_score = analyze_code_churn(files_changed)
    scores.append(("code_churn", churn_score, 0.20))

    # Test coverage ratio (0-100)
    test_score = analyze_test_coverage(files_changed)
    scores.append(("test_coverage", test_score, 0.35))

    # Weighted average
    total_score = sum(score * weight for _, score, weight in scores)

    return {
        "overall": round(total_score, 1),
        "breakdown": {name: score for name, score, _ in scores}
    }
```

#### Commit Message Quality Analysis

```python
def analyze_commit_messages(commits):
    """Score commit messages based on conventional commits and clarity"""

    scores = []
    patterns = {
        "conventional": r"^(feat|fix|docs|style|refactor|test|chore)(\(.+\))?:",
        "descriptive": r".{10,}",  # At least 10 chars
        "imperative": r"^(Add|Fix|Update|Remove|Refactor|Implement)"
    }

    for commit in commits:
        subject = commit["subject"]
        score = 0

        # Conventional commit format (+40 points)
        if re.match(patterns["conventional"], subject):
            score += 40

        # Descriptive (+30 points)
        if re.match(patterns["descriptive"], subject):
            score += 30

        # Imperative mood (+30 points)
        if re.match(patterns["imperative"], subject):
            score += 30

        scores.append(score)

    return sum(scores) / len(scores) if scores else 0
```

#### Test Coverage Analysis

```python
def analyze_test_coverage(files_changed):
    """Calculate test-to-source ratio"""

    source_files = [f for f in files_changed if f["category"] == "source"]
    test_files = [f for f in files_changed if f["category"] == "tests"]

    if not source_files:
        return 100  # No source changes

    # Count lines
    source_lines = sum(f["additions"] for f in source_files)
    test_lines = sum(f["additions"] for f in test_files)

    # Calculate ratio (aim for 1:1 or better)
    ratio = test_lines / source_lines if source_lines > 0 else 0

    # Score based on ratio
    if ratio >= 1.0:
        return 100
    elif ratio >= 0.7:
        return 85
    elif ratio >= 0.5:
        return 70
    elif ratio >= 0.3:
        return 50
    elif ratio > 0:
        return 30
    else:
        return 0
```

### 2. Risk Assessment

Identify potential risks and concerns:

```python
def assess_branch_risk(branch_data, commits, files_changed):
    """Assess overall branch risk level"""

    risk_factors = []
    risk_score = 0  # 0-100, higher = more risk

    # Large changeset risk
    total_changes = sum(f["changes"] for f in files_changed)
    if total_changes > 1000:
        risk_factors.append("Large changeset (>1000 lines)")
        risk_score += 25
    elif total_changes > 500:
        risk_factors.append("Moderate changeset (>500 lines)")
        risk_score += 15

    # Multiple file types
    languages = set(f["language"] for f in files_changed)
    if len(languages) > 3:
        risk_factors.append(f"Multiple languages ({len(languages)})")
        risk_score += 10

    # Long-lived branch
    if branch_data["age_days"] > 30:
        risk_factors.append(f"Long-lived branch ({branch_data['age_days']} days)")
        risk_score += 20
    elif branch_data["age_days"] > 14:
        risk_factors.append(f"Moderately aged branch ({branch_data['age_days']} days)")
        risk_score += 10

    # Diverged from base
    if branch_data["behind_by"] > 50:
        risk_factors.append(f"Significantly behind base ({branch_data['behind_by']} commits)")
        risk_score += 20
    elif branch_data["behind_by"] > 20:
        risk_factors.append(f"Behind base ({branch_data['behind_by']} commits)")
        risk_score += 10

    # Multiple contributors (coordination risk)
    if len(branch_data["contributors"]) > 3:
        risk_factors.append(f"Multiple contributors ({len(branch_data['contributors'])})")
        risk_score += 5

    # Determine risk level
    if risk_score >= 50:
        level = "high"
    elif risk_score >= 25:
        level = "medium"
    else:
        level = "low"

    return {
        "level": level,
        "score": risk_score,
        "factors": risk_factors,
        "mitigation": generate_mitigation_strategies(risk_factors)
    }
```

### 3. Pattern Detection

Identify common patterns and anti-patterns:

```python
def detect_patterns(commits, files_changed):
    """Detect development patterns"""

    patterns = {
        "positive": [],
        "negative": []
    }

    # Positive patterns
    if any("test" in f["path"].lower() for f in files_changed):
        patterns["positive"].append("Tests included with changes")

    if any("docs" in f["path"].lower() or f["language"] == "Markdown"
           for f in files_changed):
        patterns["positive"].append("Documentation updated")

    if all(len(c["subject"]) >= 10 for c in commits):
        patterns["positive"].append("Descriptive commit messages")

    # Negative patterns
    if any(f["changes"] > 500 for f in files_changed):
        patterns["negative"].append("Large individual file changes")

    if len(commits) > 50:
        patterns["negative"].append("High commit count (consider squashing)")

    if sum(1 for c in commits if "wip" in c["subject"].lower()) > 3:
        patterns["negative"].append("Multiple WIP commits")

    return patterns
```

### 4. Generate Recommendations

Create actionable recommendations based on analysis:

```python
def generate_recommendations(analysis_scores, risk_assessment, patterns):
    """Generate prioritized recommendations"""

    recommendations = []

    # Code quality recommendations
    if analysis_scores["breakdown"]["test_coverage"] < 50:
        recommendations.append({
            "priority": "high",
            "category": "testing",
            "title": "Add unit tests",
            "description": "Test coverage is below 50%. Add tests for new functionality.",
            "effort": "medium"
        })

    if analysis_scores["breakdown"]["commit_messages"] < 60:
        recommendations.append({
            "priority": "medium",
            "category": "documentation",
            "title": "Improve commit messages",
            "description": "Use conventional commit format (feat:, fix:, etc.)",
            "effort": "low"
        })

    # Risk-based recommendations
    if risk_assessment["level"] == "high":
        recommendations.append({
            "priority": "high",
            "category": "process",
            "title": "Consider breaking into smaller PRs",
            "description": "High risk score detected. Split into focused changes.",
            "effort": "high"
        })

    if "Behind base" in str(risk_assessment["factors"]):
        recommendations.append({
            "priority": "high",
            "category": "maintenance",
            "title": "Merge base branch",
            "description": "Branch is behind base. Merge to avoid conflicts.",
            "effort": "low"
        })

    # Pattern-based recommendations
    for negative in patterns.get("negative", []):
        if "Large individual file changes" in negative:
            recommendations.append({
                "priority": "medium",
                "category": "refactoring",
                "title": "Consider refactoring large files",
                "description": "Some files have >500 line changes. Consider splitting.",
                "effort": "medium"
            })

    # Sort by priority
    priority_order = {"high": 0, "medium": 1, "low": 2}
    recommendations.sort(key=lambda r: priority_order[r["priority"]])

    return recommendations
```

### 5. Detailed Diff Analysis (Optional)

If `include_diff` is true, perform line-by-line analysis:

```python
def analyze_diff_details(branch_data, base_branch, branch_name):
    """Analyze detailed diff for complexity and impact"""

    # Get unified diff
    diff_output = subprocess.run(
        ["git", "diff", f"{base_branch}...{branch_name}"],
        capture_output=True,
        text=True
    ).stdout

    analysis = {
        "complexity_hotspots": [],
        "duplicate_code": [],
        "security_concerns": []
    }

    # Analyze complexity (cyclomatic complexity, nesting depth)
    for file_diff in parse_diff(diff_output):
        complexity = calculate_complexity(file_diff["added_lines"])
        if complexity > 10:
            analysis["complexity_hotspots"].append({
                "file": file_diff["file"],
                "complexity": complexity,
                "suggestion": "Consider simplifying logic"
            })

    # Detect potential security issues
    security_patterns = [
        (r"password\s*=\s*['\"].*['\"]", "Hardcoded password"),
        (r"api[_-]?key\s*=\s*['\"].*['\"]", "Hardcoded API key"),
        (r"eval\(", "Use of eval()"),
        (r"exec\(", "Use of exec()")
    ]

    for pattern, issue in security_patterns:
        matches = re.findall(pattern, diff_output, re.IGNORECASE)
        if matches:
            analysis["security_concerns"].append({
                "issue": issue,
                "matches": len(matches),
                "severity": "high"
            })

    return analysis
```

## Outputs

### analysis_scores (object)

```json
{
  "overall": 78.5,
  "breakdown": {
    "commit_messages": 85,
    "file_organization": 90,
    "code_churn": 70,
    "test_coverage": 65
  },
  "grade": "B",
  "patterns": {
    "positive": [
      "Tests included with changes",
      "Documentation updated",
      "Descriptive commit messages"
    ],
    "negative": [
      "Large individual file changes"
    ]
  }
}
```

### risk_assessment (object)

```json
{
  "level": "medium",
  "score": 35,
  "factors": [
    "Moderate changeset (>500 lines)",
    "Moderately aged branch (18 days)",
    "Behind base (12 commits)"
  ],
  "mitigation": [
    "Incremental code review",
    "Merge base branch before PR",
    "Add integration tests",
    "Document breaking changes"
  ],
  "impact_analysis": {
    "files_affected": 15,
    "modules_affected": ["auth", "api", "models"],
    "breaking_changes": false,
    "migration_required": false
  }
}
```

### recommendations (array)

```json
[
  {
    "priority": "high",
    "category": "testing",
    "title": "Add unit tests",
    "description": "Test coverage is below 50%. Add tests for new authentication endpoints.",
    "effort": "medium",
    "estimated_time": "4-6 hours",
    "files_needing_tests": [
      "src/api/auth.py",
      "src/models/user.py"
    ]
  },
  {
    "priority": "high",
    "category": "maintenance",
    "title": "Merge base branch",
    "description": "Branch is 12 commits behind main. Merge to avoid conflicts.",
    "effort": "low",
    "estimated_time": "30 minutes"
  },
  {
    "priority": "medium",
    "category": "documentation",
    "title": "Improve commit messages",
    "description": "Use conventional commit format (feat:, fix:, etc.) for better changelog generation.",
    "effort": "low",
    "estimated_time": "N/A (future commits)"
  },
  {
    "priority": "medium",
    "category": "refactoring",
    "title": "Consider refactoring large files",
    "description": "src/api/auth.py has 234 line additions. Consider splitting into smaller modules.",
    "effort": "medium",
    "estimated_time": "3-4 hours"
  }
]
```

## Scoring Rubric

### Overall Score Interpretation

- **90-100 (A)**: Excellent - Production ready
- **80-89 (B)**: Good - Minor improvements needed
- **70-79 (C)**: Fair - Moderate improvements needed
- **60-69 (D)**: Poor - Significant improvements needed
- **0-59 (F)**: Critical - Major rework required

### Risk Level Interpretation

- **Low (0-24)**: Safe to merge with standard review
- **Medium (25-49)**: Requires careful review and testing
- **High (50+)**: Consider breaking into smaller changes

## Error Handling

### Insufficient Data

```json
{
  "error": "insufficient_data",
  "message": "Not enough commits or changes to analyze",
  "fallback_scores": {
    "overall": null,
    "breakdown": {}
  }
}
```

### Analysis Timeout

```json
{
  "error": "analysis_timeout",
  "message": "Diff analysis exceeded time limit",
  "partial_results": {
    "analysis_scores": {...},
    "risk_assessment": {...}
  }
}
```

## Performance Optimization

- **Parallel analysis**: Run independent analyses concurrently
- **Caching**: Cache complexity calculations for unchanged files
- **Sampling**: For very large diffs, analyze representative sample
- **Time limits**: Set 30-second timeout for diff analysis

## Next Step

Analysis results flow to **step-03-generate-readme** for documentation generation.
