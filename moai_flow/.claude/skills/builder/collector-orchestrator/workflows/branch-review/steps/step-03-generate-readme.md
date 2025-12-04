# Step 03: Generate Branch README

## Overview

This step generates a comprehensive branch README using the `collector-readme` skill, incorporating all analysis data and metadata.

## Inputs

- **branch_data** (object): Branch metadata from step-01-fetch
- **commits** (array): Commit history from step-01-fetch
- **files_changed** (array): File changes from step-01-fetch
- **analysis_scores** (object): Quality scores from step-02-analyze
- **risk_assessment** (object): Risk analysis from step-02-analyze
- **recommendations** (array): Recommendations from step-02-analyze

## Process

### 1. Template Selection

Select appropriate README template based on branch type and complexity:

```python
def select_template(branch_data, files_changed):
    """Select README template based on branch characteristics"""

    branch_name = branch_data["name"]
    total_changes = sum(f["changes"] for f in files_changed)

    if branch_name.startswith("feature/"):
        if total_changes > 500:
            return "templates/branch-feature-detailed.md"
        else:
            return "templates/branch-feature-simple.md"
    elif branch_name.startswith("bugfix/") or branch_name.startswith("hotfix/"):
        return "templates/branch-bugfix.md"
    elif branch_name.startswith("release/"):
        return "templates/branch-release.md"
    else:
        return "templates/branch-generic.md"
```

### 2. Generate README Sections

#### Header Section

```markdown
# {branch_name}

**Status**: {status_badge}
**Type**: {branch_type}
**Quality Score**: {score}/100 ({grade})
**Risk Level**: {risk_level}

---

## Quick Stats

| Metric | Value |
|--------|-------|
| Created | {created_date} |
| Last Updated | {last_updated} |
| Age | {age_days} days |
| Commits | {commit_count} |
| Files Changed | {files_changed_count} |
| Lines Added | {total_additions} |
| Lines Deleted | {total_deletions} |
| Contributors | {contributor_count} |
```

#### Overview Section

```python
def generate_overview(branch_data, commits):
    """Generate branch overview from commit messages"""

    # Extract main purpose from first commit
    first_commit = commits[0] if commits else None

    # Aggregate common themes from all commits
    themes = extract_themes_from_commits(commits)

    return f"""## Overview

This branch implements {themes[0]}. It includes {len(commits)} commits
spanning {branch_data['age_days']} days of development.

### Primary Changes

{generate_change_summary(commits, files_changed)}

### Impact

{generate_impact_summary(files_changed)}
"""
```

#### Changes Section

```python
def generate_changes_section(files_changed):
    """Generate detailed changes section"""

    # Group files by category
    by_category = {}
    for file in files_changed:
        category = file["category"]
        by_category.setdefault(category, []).append(file)

    sections = []

    for category, files in sorted(by_category.items()):
        sections.append(f"### {category.title()}\n")

        for file in files:
            status_icon = {
                "added": "➕",
                "modified": "✏️",
                "deleted": "➖",
                "renamed": "📝"
            }.get(file["status"], "•")

            sections.append(
                f"{status_icon} `{file['path']}` "
                f"(+{file['additions']} / -{file['deletions']})\n"
            )

    return "\n".join(sections)
```

#### Commits Section

```python
def generate_commits_section(commits):
    """Generate formatted commit history"""

    output = ["## Commit History\n"]

    # Group by date
    by_date = {}
    for commit in commits:
        date = commit["date"][:10]  # YYYY-MM-DD
        by_date.setdefault(date, []).append(commit)

    for date, commits_on_date in sorted(by_date.items(), reverse=True):
        output.append(f"### {date}\n")

        for commit in commits_on_date:
            output.append(
                f"- **{commit['short_sha']}** {commit['subject']} "
                f"*({commit['author']})*\n"
            )
            if commit.get("body"):
                output.append(f"  {commit['body'][:100]}...\n")

    return "".join(output)
```

#### Analysis Section

```python
def generate_analysis_section(analysis_scores, risk_assessment):
    """Generate quality and risk analysis section"""

    return f"""## Quality Analysis

### Overall Score: {analysis_scores['overall']}/100 ({analysis_scores['grade']})

#### Breakdown

| Category | Score | Status |
|----------|-------|--------|
| Commit Messages | {analysis_scores['breakdown']['commit_messages']}/100 | {score_status(analysis_scores['breakdown']['commit_messages'])} |
| File Organization | {analysis_scores['breakdown']['file_organization']}/100 | {score_status(analysis_scores['breakdown']['file_organization'])} |
| Code Churn | {analysis_scores['breakdown']['code_churn']}/100 | {score_status(analysis_scores['breakdown']['code_churn'])} |
| Test Coverage | {analysis_scores['breakdown']['test_coverage']}/100 | {score_status(analysis_scores['breakdown']['test_coverage'])} |

### Risk Assessment: {risk_assessment['level'].upper()}

**Risk Score**: {risk_assessment['score']}/100

#### Risk Factors

{format_list(risk_assessment['factors'])}

#### Mitigation Strategies

{format_list(risk_assessment['mitigation'])}
"""
```

#### Recommendations Section

```python
def generate_recommendations_section(recommendations):
    """Generate actionable recommendations"""

    output = ["## Recommendations\n"]

    # Group by priority
    by_priority = {"high": [], "medium": [], "low": []}
    for rec in recommendations:
        by_priority[rec["priority"]].append(rec)

    for priority in ["high", "medium", "low"]:
        if by_priority[priority]:
            icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}[priority]
            output.append(f"### {icon} {priority.title()} Priority\n")

            for rec in by_priority[priority]:
                output.append(f"#### {rec['title']}\n")
                output.append(f"{rec['description']}\n\n")
                output.append(f"**Effort**: {rec['effort']}")
                if rec.get("estimated_time"):
                    output.append(f" (~{rec['estimated_time']})")
                output.append("\n\n")

    return "".join(output)
```

#### Contributors Section

```python
def generate_contributors_section(branch_data):
    """Generate contributors section"""

    output = ["## Contributors\n"]

    for contributor in branch_data["contributors"]:
        output.append(
            f"- **{contributor['name']}** ({contributor['email']}) - "
            f"{contributor['commit_count']} commits\n"
        )

    return "".join(output)
```

#### Next Steps Section

```python
def generate_next_steps(recommendations, risk_assessment):
    """Generate actionable next steps checklist"""

    output = ["## Next Steps\n"]

    # Priority actions from recommendations
    high_priority = [r for r in recommendations if r["priority"] == "high"]

    if high_priority:
        output.append("### Before PR Creation\n\n")
        for i, rec in enumerate(high_priority[:3], 1):
            output.append(f"{i}. [ ] {rec['title']}\n")

    # Standard checklist
    output.append("\n### PR Checklist\n\n")
    checklist = [
        "All tests passing",
        "Code reviewed by at least one team member",
        "Documentation updated",
        "CHANGELOG.md updated",
        "No merge conflicts with base branch",
        "CI/CD pipeline green"
    ]

    for item in checklist:
        output.append(f"- [ ] {item}\n")

    return "".join(output)
```

### 3. Assemble README

```python
def assemble_readme(sections):
    """Combine all sections into final README"""

    readme_content = []

    # Header with metadata
    readme_content.append(sections["header"])
    readme_content.append("\n---\n\n")

    # Table of contents (auto-generated)
    readme_content.append(generate_toc(sections))
    readme_content.append("\n---\n\n")

    # Main content sections
    readme_content.append(sections["overview"])
    readme_content.append("\n\n")
    readme_content.append(sections["changes"])
    readme_content.append("\n\n")
    readme_content.append(sections["commits"])
    readme_content.append("\n\n")
    readme_content.append(sections["analysis"])
    readme_content.append("\n\n")
    readme_content.append(sections["recommendations"])
    readme_content.append("\n\n")
    readme_content.append(sections["contributors"])
    readme_content.append("\n\n")
    readme_content.append(sections["next_steps"])

    # Footer with metadata
    readme_content.append("\n---\n\n")
    readme_content.append(generate_footer())

    return "".join(readme_content)
```

### 4. Save README File

```python
def save_branch_readme(branch_name, readme_content):
    """Save README to appropriate location"""

    # Create branch docs directory
    branch_docs_dir = Path(".claude/branch-docs") / sanitize_branch_name(branch_name)
    branch_docs_dir.mkdir(parents=True, exist_ok=True)

    # Save README
    readme_path = branch_docs_dir / "README.md"
    readme_path.write_text(readme_content)

    # Save metadata
    metadata_path = branch_docs_dir / "metadata.json"
    metadata = {
        "generated_at": datetime.now().isoformat(),
        "workflow_version": "1.0.0",
        "branch_name": branch_name
    }
    metadata_path.write_text(json.dumps(metadata, indent=2))

    return str(readme_path)
```

### 5. Update Branch Index

```python
def update_branch_index(branch_name, readme_path, analysis_scores):
    """Update master index of all branch READMEs"""

    index_path = Path(".claude/branch-docs/INDEX.md")

    # Read existing index
    if index_path.exists():
        index_content = index_path.read_text()
    else:
        index_content = "# Branch Documentation Index\n\n"

    # Add/update entry
    entry = (
        f"- [{branch_name}]({readme_path}) - "
        f"Score: {analysis_scores['overall']}/100 - "
        f"Updated: {datetime.now().strftime('%Y-%m-%d')}\n"
    )

    # Replace or append
    if branch_name in index_content:
        # Update existing entry
        index_content = re.sub(
            rf"- \[{re.escape(branch_name)}\].*\n",
            entry,
            index_content
        )
    else:
        # Append new entry
        index_content += entry

    index_path.write_text(index_content)
```

## Outputs

### readme_path (string)

```
.claude/branch-docs/feature-user-authentication/README.md
```

### readme_content (string)

Full README content (example excerpt):

```markdown
# feature/user-authentication

**Status**: 🟢 Active
**Type**: Feature
**Quality Score**: 78.5/100 (B)
**Risk Level**: Medium

---

## Quick Stats

| Metric | Value |
|--------|-------|
| Created | 2025-11-20 |
| Last Updated | 2025-12-04 |
| Age | 14 days |
| Commits | 15 |
| Files Changed | 12 |
| Lines Added | 567 |
| Lines Deleted | 89 |
| Contributors | 2 |

---

## Overview

This branch implements OAuth2 authentication and JWT token management.
It includes 15 commits spanning 14 days of development.

### Primary Changes

- New authentication API endpoints
- User model extensions for OAuth
- JWT token generation and validation
- Login/logout functionality
- Session management

...
```

## Integration with collector-readme

### Template Inheritance

```python
from collector_readme import TemplateManager

template_mgr = TemplateManager()
base_template = template_mgr.load("branch-template-v2")

# Customize for specific branch
customized = template_mgr.customize(
    base_template,
    branch_type=detect_branch_type(branch_name),
    complexity=calculate_complexity(files_changed)
)
```

### Cross-Referencing

```python
def add_cross_references(readme_content, branch_data):
    """Add links to related documentation"""

    references = []

    # Link to related specs
    if spec_files := find_related_specs(branch_data):
        references.append("## Related Specifications\n\n")
        for spec in spec_files:
            references.append(f"- [{spec['name']}]({spec['path']})\n")

    # Link to related branches
    if related := find_related_branches(branch_data):
        references.append("\n## Related Branches\n\n")
        for branch in related:
            references.append(f"- [{branch}](./{branch}/README.md)\n")

    return readme_content + "\n" + "".join(references)
```

## Error Handling

### Template Not Found

```json
{
  "error": "template_not_found",
  "message": "README template not found",
  "fallback": "Using generic template",
  "readme_path": ".claude/branch-docs/feature-x/README.md"
}
```

### Write Permission Error

```json
{
  "error": "write_permission_denied",
  "message": "Cannot write to .claude/branch-docs/",
  "suggestion": "Check directory permissions"
}
```

## Validation

### README Quality Checks

```python
def validate_readme(readme_content):
    """Validate generated README quality"""

    checks = []

    # Has minimum sections
    required_sections = ["Overview", "Changes", "Commits", "Analysis"]
    for section in required_sections:
        if f"## {section}" not in readme_content:
            checks.append(f"Missing section: {section}")

    # Has proper markdown formatting
    if not re.match(r"^# ", readme_content):
        checks.append("Missing H1 header")

    # Not too short
    if len(readme_content) < 500:
        checks.append("README too short (<500 chars)")

    return {
        "valid": len(checks) == 0,
        "issues": checks
    }
```

## Next Step

README path and content flow to **step-04-report** for user display.
