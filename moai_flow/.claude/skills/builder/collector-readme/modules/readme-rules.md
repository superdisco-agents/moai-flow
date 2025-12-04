---
name: README Rules Module
version: 1.0.0
part_of: collector-readme
description: Foundation document defining mandatory/optional sections and ordering standards for README generation
updated: 2025-12-04
---

# README Rules Module

## Overview

This module defines the structural requirements, ordering standards, and content guidelines for all generated README documents. It serves as the authoritative reference for README generation rules.

## Section Requirements

### Mandatory Sections

All README documents MUST include these sections in the specified order:

| Section | Order | Required | Description |
|---------|-------|----------|-------------|
| Header Block | 1 | Yes | Title, branch info, tier, status badges |
| TL;DR | 2 | Yes | 20-75 word executive summary |
| Navigation | 3 | Yes | Quick links to key sections |
| At-a-Glance Dashboard | 4 | Yes | Metrics table with key indicators |
| Executive Summary | 5 | Yes | 50-500 word comprehensive overview |
| Change Categories | 6 | Yes | Categorized list of all changes |
| Impact Analysis | 7 | Yes | Scope and affected areas |
| Timeline | 8 | Yes | Chronological change history |
| Action Guide | 9 | Yes | Next steps and recommendations |
| Validation Checklist | 10 | Yes | Quality gates and review items |

### Conditional Sections

These sections are included based on specific conditions:

| Section | Order | Condition | Description |
|---------|-------|-----------|-------------|
| Table of Contents | 2.5 | File > 500 lines | Anchor links to all major sections |
| Dependencies | 6.5 | Has external deps | Required packages and versions |
| Risk Assessment | 7.5 | Tier 1-2 branches | Security, performance, breaking changes |
| Related Documentation | 11 | Has doc links | Cross-references to other docs |
| Score Evolution | 12 | 3+ history points | Quality score trends over time |

## Section Ordering Standard

The complete ordering sequence for README sections:

```
1.  Header Block (mandatory)
2.  TL;DR (mandatory)
2.5 Table of Contents (conditional: file > 500 lines)
3.  Navigation (mandatory)
4.  At-a-Glance Dashboard (mandatory)
5.  Executive Summary (mandatory)
6.  Change Categories (mandatory)
6.5 Dependencies (conditional: external dependencies exist)
7.  Impact Analysis (mandatory)
7.5 Risk Assessment (conditional: Tier 1-2 branches)
8.  Timeline (mandatory)
9.  Action Guide (mandatory)
10. Validation Checklist (mandatory)
11. Related Documentation (conditional: documentation links exist)
12. Score Evolution (conditional: 3+ historical data points)
```

## Merge Status Guidance Rules

README content varies based on branch merge status. Apply these rules:

### ACTIVE Branch State

**Characteristics:**
- Branch exists locally and remotely
- Not yet merged to main
- Active development in progress

**Required Guidance:**
```markdown
## Next Steps

### Create Pull Request
1. Review all changes in this branch
2. Ensure validation checklist is complete
3. Create PR against main branch:
   ```bash
   gh pr create --title "feature/branch-name" --body-file README.md
   ```
4. Request review from relevant team members
5. Address any CI/CD feedback

### Pre-PR Checklist
- [ ] All tests passing locally
- [ ] Documentation updated
- [ ] Breaking changes documented
- [ ] Security review complete (if Tier 1-2)
```

### PR_OPEN Branch State

**Characteristics:**
- Pull request exists and is open
- Under review process
- May have review comments

**Required Guidance:**
```markdown
## Next Steps

### Review and Merge
1. **Review Status**: PR #<number> is open and awaiting review
2. **Required Actions**:
   - [ ] Address review comments
   - [ ] Resolve merge conflicts (if any)
   - [ ] Ensure all CI checks pass
   - [ ] Obtain required approvals

3. **Merge Process**:
   ```bash
   # After approval, merge via GitHub UI or:
   gh pr merge <number> --squash --delete-branch
   ```

### Current PR Information
- **PR Number**: #<number>
- **Status**: Open
- **Reviews**: <count> pending
- **CI Status**: <status>
```

### MERGED Branch State

**Characteristics:**
- Changes successfully merged to main
- Branch may still exist or be deleted
- Historical record of what was added

**Required Guidance:**
```markdown
## Merge Summary

### What Was Added
This branch was successfully merged to main on <date>.

**Key Additions:**
- <list major features/changes added>
- <impact on main codebase>
- <new capabilities enabled>

**Integration Points:**
- <how changes integrate with existing code>
- <new dependencies introduced>
- <configuration changes required>

**Post-Merge Actions Completed:**
- [x] Branch merged to main
- [x] CI/CD pipeline updated
- [x] Documentation deployed
- [x] Team notified

### Archive Notice
This README represents the final state of the branch at merge time.
For current status, see main branch documentation.
```

### STALE Branch State

**Characteristics:**
- No commits in 30+ days
- May be abandoned or low priority
- Requires decision on continuation

**Required Guidance:**
```markdown
## Branch Status: STALE

### Decision Required

This branch has had no activity for 30+ days. Choose an action:

#### Option 1: Close Branch
If changes are no longer needed:
```bash
# Delete local branch
git branch -D <branch-name>

# Delete remote branch
git push origin --delete <branch-name>
```

#### Option 2: Continue Development
If work should resume:
1. Review current main branch for conflicts
2. Rebase on latest main:
   ```bash
   git checkout <branch-name>
   git fetch origin
   git rebase origin/main
   ```
3. Update dependencies and resolve conflicts
4. Resume development with fresh context

### Stale Branch Analysis
- **Last Activity**: <date>
- **Days Inactive**: <count>
- **Divergence from Main**: <commit count>
- **Conflicts Likely**: <yes/no>

**Recommendation**: <close or continue based on context>
```

## Content Length Requirements

### TL;DR Section
- **Minimum**: 20 words
- **Maximum**: 75 words
- **Purpose**: One-paragraph summary for quick scanning
- **Must Include**: Branch purpose, key changes, current status

**Example:**
```markdown
## TL;DR

This branch implements user authentication with OAuth2 support, adding
secure login flows and session management. Includes 12 new components,
3 API endpoints, and comprehensive test coverage. Currently in PR review
with 2 minor comments to address.
```

### Executive Summary Section
- **Minimum**: 50 words
- **Maximum**: 500 words
- **Purpose**: Detailed overview for stakeholders
- **Must Include**: Context, approach, key decisions, outcomes

**Example Structure:**
```markdown
## Executive Summary

**Context**: <why this work was needed>

**Approach**: <technical strategy and methodology>

**Key Decisions**:
- <major architectural choices>
- <trade-offs considered>
- <alternatives rejected>

**Outcomes**:
- <what was delivered>
- <quality metrics>
- <next steps>
```

### Change Categories Section
- **No word limit**: Comprehensive listing required
- **Format**: Bullet lists organized by category
- **Categories**: Features, Enhancements, Fixes, Refactoring, Tests, Docs

### Impact Analysis Section
- **Minimum**: 100 words
- **Format**: Structured breakdown by area
- **Must Include**: Scope, affected systems, integration points

### Timeline Section
- **Format**: Chronological table or list
- **Granularity**: Daily for active branches, weekly for historical

### Action Guide Section
- **Format**: Numbered steps with code blocks
- **Requirements**: Clear, executable instructions
- **Must Include**: Commands, validation steps, rollback procedures

### Validation Checklist Section
- **Format**: Markdown checklist items
- **Minimum Items**: 8
- **Categories**: Code quality, testing, security, documentation

## Anti-patterns to Avoid

### Content Anti-patterns

**DO NOT:**

1. **Use Vague Language**
   - Bad: "Made some improvements to the system"
   - Good: "Optimized database queries reducing response time by 40%"

2. **Skip Context**
   - Bad: "Fixed the bug"
   - Good: "Fixed authentication timeout bug affecting mobile users"

3. **Omit Metrics**
   - Bad: "Improved performance"
   - Good: "Reduced load time from 3.2s to 0.8s (75% improvement)"

4. **List Without Categorization**
   - Bad: Random list of 50+ changes
   - Good: Changes organized by Features, Fixes, etc.

5. **Provide Incomplete Commands**
   - Bad: "Run the tests"
   - Good: "Run tests: `npm test -- --coverage`"

### Structural Anti-patterns

**DO NOT:**

1. **Mix Section Order**
   - Always follow the standard ordering sequence
   - Conditional sections go in their designated positions

2. **Duplicate Information**
   - Each fact appears in exactly one section
   - Use cross-references for related content

3. **Create Deep Nesting**
   - Maximum 3 heading levels (h1, h2, h3)
   - Use tables for complex hierarchies

4. **Omit Status Information**
   - Always include current branch state
   - Always provide next steps guidance

5. **Use Inconsistent Formatting**
   - Code blocks must have language tags
   - Tables must have headers
   - Lists must use consistent markers

### Language Anti-patterns

**DO NOT:**

1. **Use Emojis**
   - Professional documentation only
   - Use words to convey meaning

2. **Write in First Person**
   - Bad: "I implemented..."
   - Good: "Implementation includes..."

3. **Use Jargon Without Definition**
   - Define acronyms on first use
   - Link to glossary for technical terms

4. **Create Ambiguous Instructions**
   - Bad: "Update the config"
   - Good: "Update `config.json` with the following settings:"

5. **Leave Decisions Open**
   - Bad: "Maybe we should..."
   - Good: "Recommendation: Implement X because Y"

## Validation Rules

Before finalizing any README, verify:

### Structure Validation
- [ ] All mandatory sections present
- [ ] Sections in correct order
- [ ] Conditional sections evaluated correctly
- [ ] No duplicate sections

### Content Validation
- [ ] TL;DR within 20-75 words
- [ ] Executive Summary within 50-500 words
- [ ] All commands tested and accurate
- [ ] All links valid and accessible

### Quality Validation
- [ ] No emojis present
- [ ] No spelling errors
- [ ] Consistent formatting throughout
- [ ] Clear action items identified

### Completeness Validation
- [ ] Status-specific guidance included
- [ ] All anti-patterns avoided
- [ ] Metrics and numbers provided
- [ ] Next steps clearly defined

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-12-04 | Initial release with complete rule set |
