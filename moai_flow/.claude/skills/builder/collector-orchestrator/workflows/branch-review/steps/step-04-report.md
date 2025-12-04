# Step 04: Display Summary

## Overview

This step generates and displays a user-friendly summary of the branch review workflow results.

## Inputs

- **branch_data** (object): Branch metadata from step-01-fetch
- **analysis_scores** (object): Quality scores from step-02-analyze
- **risk_assessment** (object): Risk analysis from step-02-analyze
- **readme_path** (string): Path to generated README from step-03-generate-readme

## Process

### 1. Generate Summary Header

```python
def generate_summary_header(branch_data, analysis_scores):
    """Create colorful summary header"""

    # Determine overall status icon
    score = analysis_scores["overall"]
    if score >= 90:
        status = "🟢 Excellent"
    elif score >= 80:
        status = "🟡 Good"
    elif score >= 70:
        status = "🟠 Fair"
    else:
        status = "🔴 Needs Work"

    return f"""
╔═══════════════════════════════════════════════════════════════╗
║           BRANCH REVIEW COMPLETE: {branch_data['name'][:30]:<30} ║
╚═══════════════════════════════════════════════════════════════╝

Status: {status}
Quality Score: {score}/100 ({analysis_scores['grade']})
Risk Level: {risk_assessment['level'].upper()}
"""
```

### 2. Format Key Metrics

```python
def format_key_metrics(branch_data, files_changed):
    """Format key metrics in a table"""

    total_additions = sum(f["additions"] for f in files_changed)
    total_deletions = sum(f["deletions"] for f in files_changed)

    return f"""
┌─────────────────────────────────────────────────────────────┐
│ KEY METRICS                                                  │
├─────────────────────────────────────────────────────────────┤
│ Commits:          {branch_data['ahead_by']:>4} commits ahead of {branch_data['base_branch']}  │
│ Files Changed:    {len(files_changed):>4} files                                 │
│ Lines Added:      {total_additions:>6} (+)                                │
│ Lines Deleted:    {total_deletions:>6} (-)                                │
│ Age:              {branch_data['age_days']:>4} days                                │
│ Contributors:     {len(branch_data['contributors']):>4}                                      │
└─────────────────────────────────────────────────────────────┘
"""
```

### 3. Format Quality Breakdown

```python
def format_quality_breakdown(analysis_scores):
    """Format quality score breakdown with progress bars"""

    def score_bar(score):
        """Generate visual progress bar"""
        filled = int(score / 10)
        empty = 10 - filled

        if score >= 80:
            color = "🟢"
        elif score >= 60:
            color = "🟡"
        else:
            color = "🔴"

        return f"{color} {'█' * filled}{'░' * empty} {score}/100"

    breakdown = analysis_scores["breakdown"]

    return f"""
┌─────────────────────────────────────────────────────────────┐
│ QUALITY BREAKDOWN                                            │
├─────────────────────────────────────────────────────────────┤
│ Commit Messages:  {score_bar(breakdown['commit_messages'])}          │
│ File Organization:{score_bar(breakdown['file_organization'])}       │
│ Code Churn:       {score_bar(breakdown['code_churn'])}              │
│ Test Coverage:    {score_bar(breakdown['test_coverage'])}           │
└─────────────────────────────────────────────────────────────┘
"""
```

### 4. Format Risk Summary

```python
def format_risk_summary(risk_assessment):
    """Format risk assessment summary"""

    level_icon = {
        "low": "🟢",
        "medium": "🟡",
        "high": "🔴"
    }[risk_assessment["level"]]

    output = [f"""
┌─────────────────────────────────────────────────────────────┐
│ RISK ASSESSMENT: {level_icon} {risk_assessment['level'].upper():<43} │
├─────────────────────────────────────────────────────────────┤
"""]

    # Risk factors
    if risk_assessment["factors"]:
        output.append("│ Risk Factors:                                                │\n")
        for factor in risk_assessment["factors"][:3]:  # Top 3
            output.append(f"│   • {factor:<55} │\n")

    output.append("└─────────────────────────────────────────────────────────────┘\n")

    return "".join(output)
```

### 5. Format Top Recommendations

```python
def format_top_recommendations(recommendations):
    """Format top 3 priority recommendations"""

    if not recommendations:
        return ""

    output = ["""
┌─────────────────────────────────────────────────────────────┐
│ TOP RECOMMENDATIONS                                          │
├─────────────────────────────────────────────────────────────┤
"""]

    priority_icons = {
        "high": "🔴",
        "medium": "🟡",
        "low": "🟢"
    }

    for i, rec in enumerate(recommendations[:3], 1):
        icon = priority_icons[rec["priority"]]
        output.append(f"│ {i}. {icon} {rec['title']:<52} │\n")

        # Wrap description to fit
        desc_lines = wrap_text(rec["description"], 55)
        for line in desc_lines:
            output.append(f"│    {line:<56} │\n")

        output.append(f"│    Effort: {rec['effort']:<48} │\n")

        if i < min(3, len(recommendations)):
            output.append("│                                                              │\n")

    output.append("└─────────────────────────────────────────────────────────────┘\n")

    return "".join(output)
```

### 6. Format Next Actions

```python
def format_next_actions(recommendations, readme_path):
    """Format immediate next actions"""

    high_priority = [r for r in recommendations if r["priority"] == "high"]

    output = ["""
┌─────────────────────────────────────────────────────────────┐
│ NEXT ACTIONS                                                 │
├─────────────────────────────────────────────────────────────┤
"""]

    if high_priority:
        output.append("│ Before creating PR:                                          │\n")
        for rec in high_priority[:2]:
            output.append(f"│   [ ] {rec['title']:<52} │\n")
        output.append("│                                                              │\n")

    output.append(f"│ 📄 View detailed report:                                     │\n")
    output.append(f"│    {readme_path:<56} │\n")

    output.append("└─────────────────────────────────────────────────────────────┘\n")

    return "".join(output)
```

### 7. Assemble Complete Summary

```python
def assemble_summary(branch_data, analysis_scores, risk_assessment,
                     recommendations, readme_path, files_changed):
    """Assemble complete summary for display"""

    summary_parts = [
        generate_summary_header(branch_data, analysis_scores),
        format_key_metrics(branch_data, files_changed),
        format_quality_breakdown(analysis_scores),
        format_risk_summary(risk_assessment),
        format_top_recommendations(recommendations),
        format_next_actions(recommendations, readme_path)
    ]

    return "\n".join(summary_parts)
```

### 8. Display to User

```python
def display_summary(summary):
    """Display summary to user with proper formatting"""

    # Print to stdout
    print(summary)

    # Also save to file for reference
    summary_path = Path(".claude/logs/workflows/branch-review/latest-summary.txt")
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(summary)

    # Return for workflow output
    return summary
```

### 9. Generate Additional Outputs

```python
def generate_additional_outputs(analysis_scores, risk_assessment,
                                recommendations, readme_path):
    """Generate machine-readable outputs for automation"""

    # JSON summary for CI/CD
    json_summary = {
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "quality_score": analysis_scores["overall"],
        "grade": analysis_scores["grade"],
        "risk_level": risk_assessment["level"],
        "pass_threshold": analysis_scores["overall"] >= 70,
        "high_priority_count": len([r for r in recommendations if r["priority"] == "high"]),
        "readme_path": readme_path
    }

    json_path = Path(".claude/logs/workflows/branch-review/latest-summary.json")
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(json_summary, indent=2))

    # Badge for GitHub README
    badge_url = generate_quality_badge(analysis_scores["overall"])

    return {
        "json_path": str(json_path),
        "badge_url": badge_url
    }
```

## Outputs

### summary (string)

Complete formatted summary for terminal display:

```
╔═══════════════════════════════════════════════════════════════╗
║           BRANCH REVIEW COMPLETE: feature/user-authentication  ║
╚═══════════════════════════════════════════════════════════════╝

Status: 🟡 Good
Quality Score: 78.5/100 (B)
Risk Level: MEDIUM

┌─────────────────────────────────────────────────────────────┐
│ KEY METRICS                                                  │
├─────────────────────────────────────────────────────────────┤
│ Commits:            15 commits ahead of main                 │
│ Files Changed:      12 files                                 │
│ Lines Added:       567 (+)                                   │
│ Lines Deleted:      89 (-)                                   │
│ Age:                14 days                                  │
│ Contributors:        2                                       │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ QUALITY BREAKDOWN                                            │
├─────────────────────────────────────────────────────────────┤
│ Commit Messages:  🟢 ████████░░ 85/100                       │
│ File Organization:🟢 █████████░ 90/100                       │
│ Code Churn:       🟡 ███████░░░ 70/100                       │
│ Test Coverage:    🟡 ██████░░░░ 65/100                       │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ RISK ASSESSMENT: 🟡 MEDIUM                                   │
├─────────────────────────────────────────────────────────────┤
│ Risk Factors:                                                │
│   • Moderate changeset (>500 lines)                          │
│   • Moderately aged branch (14 days)                         │
│   • Behind base (12 commits)                                 │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ TOP RECOMMENDATIONS                                          │
├─────────────────────────────────────────────────────────────┤
│ 1. 🔴 Add unit tests                                         │
│    Test coverage is below 50%. Add tests for new             │
│    authentication endpoints.                                 │
│    Effort: medium                                            │
│                                                              │
│ 2. 🔴 Merge base branch                                      │
│    Branch is 12 commits behind main. Merge to avoid          │
│    conflicts.                                                │
│    Effort: low                                               │
│                                                              │
│ 3. 🟡 Improve commit messages                                │
│    Use conventional commit format (feat:, fix:, etc.)        │
│    Effort: low                                               │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ NEXT ACTIONS                                                 │
├─────────────────────────────────────────────────────────────┤
│ Before creating PR:                                          │
│   [ ] Add unit tests                                         │
│   [ ] Merge base branch                                      │
│                                                              │
│ 📄 View detailed report:                                     │
│    .claude/branch-docs/feature-user-authentication/README.md │
└─────────────────────────────────────────────────────────────┘
```

## Display Modes

### Compact Mode

For CI/CD or quick checks:

```
Branch Review: feature/user-authentication
Score: 78.5/100 (B) | Risk: MEDIUM
📄 README: .claude/branch-docs/feature-user-authentication/README.md
⚠️  2 high-priority recommendations
```

### Detailed Mode

Full summary as shown above (default).

### JSON Mode

For programmatic consumption:

```json
{
  "branch": "feature/user-authentication",
  "score": 78.5,
  "grade": "B",
  "risk": "medium",
  "recommendations_count": 4,
  "high_priority_count": 2,
  "readme_path": ".claude/branch-docs/feature-user-authentication/README.md"
}
```

## Integration Points

### Terminal Display

```python
# ANSI color codes for terminal
COLORS = {
    "green": "\033[92m",
    "yellow": "\033[93m",
    "red": "\033[91m",
    "reset": "\033[0m"
}

def colorize(text, color):
    return f"{COLORS[color]}{text}{COLORS['reset']}"
```

### Slack/Discord Notification

```python
def format_for_slack(summary_data):
    """Format summary for Slack notification"""

    return {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"Branch Review: {summary_data['branch']}"
                }
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Score:* {summary_data['score']}/100"},
                    {"type": "mrkdwn", "text": f"*Risk:* {summary_data['risk'].upper()}"}
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"<{summary_data['readme_path']}|View Full Report>"
                }
            }
        ]
    }
```

### GitHub Comment

```python
def format_for_github(summary_data, recommendations):
    """Format summary as GitHub comment"""

    return f"""## Branch Review Results

**Quality Score:** {summary_data['score']}/100 ({summary_data['grade']})
**Risk Level:** {summary_data['risk'].upper()}

### Top Recommendations

{format_recommendations_markdown(recommendations[:3])}

[View full report]({summary_data['readme_path']})
"""
```

## Error Handling

All errors are non-fatal in this step (configured with `on_error: "warn"`):

```python
def safe_display(summary):
    """Display summary with fallback"""

    try:
        display_summary(summary)
    except Exception as e:
        # Fallback to basic text
        print(f"Branch review completed. Error formatting summary: {e}")
        print(f"View report at: {readme_path}")
```

## Workflow Completion

This is the final step. After execution:

1. Summary displayed to user
2. README saved to `.claude/branch-docs/`
3. JSON summary saved to `.claude/logs/workflows/branch-review/`
4. Workflow outputs populated for external use

## Testing

```python
def test_summary_generation():
    """Test summary formatting"""

    summary = assemble_summary(
        branch_data=mock_branch_data(),
        analysis_scores=mock_scores(),
        risk_assessment=mock_risk(),
        recommendations=mock_recommendations(),
        readme_path="test/README.md",
        files_changed=mock_files()
    )

    assert "BRANCH REVIEW COMPLETE" in summary
    assert "QUALITY BREAKDOWN" in summary
    assert "TOP RECOMMENDATIONS" in summary
```

## Performance

- Summary generation: <100ms
- Terminal rendering: <50ms
- Total step execution: <200ms

## Future Enhancements

1. **Interactive mode**: Let user drill down into details
2. **Trend analysis**: Compare with previous reviews
3. **Team metrics**: Aggregate across branches
4. **Custom themes**: Different ASCII art styles
5. **Export formats**: PDF, HTML, Markdown
