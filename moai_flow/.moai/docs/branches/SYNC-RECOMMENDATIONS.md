# Bidirectional Sync Recommendations

> **Generated**: 2025-12-04 | **Repository**: superdisco-agents/moai-adk

## Current Branch Status (CORRECTED)

IMPORTANT: Previous analysis incorrectly showed branches as MERGED. Actual status:

| Branch | Status | PR | CI Status | Action Needed |
|--------|--------|-----|-----------|---------------|
| feature/macos-optimizer | ACTIVE | None | - | Create PR |
| feature/domain-adb | PR Open | #3 | 1/8 failing | Fix CI, rebase |
| feature/workspace-consolidation | PR Open | #2 | 1/8 failing | Fix CI, rebase |
| feature/moai-flow-system | PR Open | #1 | 1/8 failing | Fix CI, rebase (5 behind) |
| feature/SPEC-first-builders | STALE | None | 0/8 | Close or rebase |

Priority Actions:
1. Fix CI failures on PRs #1, #2, #3
2. Rebase all branches (especially #1 which is 5 commits behind)
3. Create PR for feature/macos-optimizer
4. Decide fate of feature/SPEC-first-builders (close or continue)

## Gap Analysis Summary

### Missing in Local (24 skills to pull from GitHub)

| Category | Skill | Action |
|----------|-------|--------|
| Domain | moai-domain-adb | PULL |
| Domain | moai-domain-backend | PULL |
| Domain | moai-domain-cli-tool | PULL |
| Domain | moai-domain-cloud | PULL |
| Domain | moai-domain-data-science | PULL |
| Domain | moai-domain-database | PULL |
| Domain | moai-domain-devops | PULL |
| Domain | moai-domain-figma | PULL |
| Domain | moai-domain-frontend | PULL |
| Domain | moai-domain-ml | PULL |
| Domain | moai-domain-ml-ops | PULL |
| Domain | moai-domain-mobile-app | PULL |
| Domain | moai-domain-monitoring | PULL |
| Domain | moai-domain-notion | PULL |
| Domain | moai-domain-security | PULL |
| Domain | moai-domain-testing | PULL |
| Domain | moai-domain-web-api | PULL |
| Builder | builder-skill-uvscript | PULL |
| Builder | builder-workflow | PULL |
| Builder | decision-logic-framework | PULL |
| System | macos-resource-optimizer | PULL |
| Common | moai-builder-common | PULL |
| Localization | moai-localization-bilingual | PULL |
| Localization | moai-localization-korean | PULL |

### Local Innovations (to push to GitHub)

| Category | Component | Action |
|----------|-----------|--------|
| Collector | collector-ui skill | CONTRIBUTE |
| Collector | collector-readme skill | CONTRIBUTE |
| Collector | collector-merge skill | CONTRIBUTE |
| Collector | TOON workflows | CONTRIBUTE |
| Collector | Tier classification system | CONTRIBUTE |
| Core | moai_flow package refactor | CONTRIBUTE |
| Core | Python src/ layout migration | CONTRIBUTE |
| Flow | Multi-agent coordination patterns | CONTRIBUTE |
| Flow | Swarm topology system | CONTRIBUTE |
| Flow | Consensus algorithms | CONTRIBUTE |

## Recommended Commands

### Pull from GitHub

```bash
# Clone from GitHub main
git fetch origin main

# Create sync branch
git checkout -b feature/sync-skills

# Cherry-pick or merge missing skills
# Review changes before merging
git merge origin/main --no-commit

# Alternative: Cherry-pick specific commits
# git cherry-pick <commit-hash>
```

### Push to GitHub

```bash
# Create feature branch for collector v4.0
git checkout -b feature/collector-v4

# Stage new skills
git add moai_flow/.moai/skills/moai-collector-*
git add moai_flow/.moai/docs/collectors/

# Commit with descriptive message
git commit -m "feat: Add Collector v4.0 System

- Add collector-ui skill for interface collection
- Add collector-readme skill for documentation
- Add collector-merge skill for consolidation
- Add TOON workflows for orchestration
- Implement tier classification system"

# Push to origin
git push -u origin feature/collector-v4

# Create pull request
gh pr create --title "Add Collector v4.0 System" \
  --body "## Overview
This PR introduces the Collector v4.0 system with enhanced capabilities for UI collection, documentation gathering, and intelligent merging.

## Key Features
- **collector-ui**: Interface and component collection
- **collector-readme**: Documentation aggregation
- **collector-merge**: Intelligent consolidation
- **TOON workflows**: Orchestration patterns
- **Tier system**: Classification framework

## Testing
- Validated on local moai-adk repository
- Successfully collected and merged components
- Compatible with existing MoAI-Flow infrastructure"
```

### Sync Core Infrastructure

```bash
# Create branch for core refactoring
git checkout -b feature/core-infrastructure

# Stage core changes
git add moai_flow/src/
git add moai_flow/tests/

# Commit core changes
git commit -m "refactor: Apply Python src/ layout to moai_flow

- Migrate to official Python project structure
- Add src/moai_flow/ package layout
- Update imports and references
- Maintain backward compatibility"

# Push and create PR
git push -u origin feature/core-infrastructure
gh pr create --title "Core Infrastructure Refactor"
```

## Priority Order

### Phase 1: Pull Critical Domain Skills (High Impact)

**Priority**: HIGH | **Timeline**: Immediate

1. **moai-domain-backend** - Backend development patterns
2. **moai-domain-frontend** - Frontend development patterns
3. **moai-domain-database** - Database design and optimization
4. **moai-domain-web-api** - API design and implementation
5. **moai-domain-testing** - Testing strategies and frameworks

**Rationale**: These domain skills provide essential development capabilities that are currently missing from the local environment.

### Phase 2: Push Collector v4.0 (Innovation)

**Priority**: HIGH | **Timeline**: Week 1

1. Create feature branch
2. Package collector skills and documentation
3. Write comprehensive PR description
4. Request review from maintainers
5. Address feedback and merge

**Rationale**: The Collector v4.0 system represents significant innovation that would benefit the broader MoAI-Flow community.

### Phase 3: Pull Builder Skills

**Priority**: MEDIUM | **Timeline**: Week 2

1. **builder-skill-uvscript** - UV-based scripting patterns
2. **builder-workflow** - Workflow orchestration
3. **decision-logic-framework** - Decision-making patterns
4. **moai-builder-common** - Common builder utilities

**Rationale**: Builder skills enhance development automation and workflow efficiency.

### Phase 4: Merge feature/SPEC-first-builders

**Priority**: MEDIUM | **Timeline**: Week 2-3

1. Review SPEC-first-builders branch
2. Resolve merge conflicts
3. Test integrated functionality
4. Merge to main

**Rationale**: Align with upstream SPEC-first development patterns.

### Phase 5: Pull Remaining Domain Skills

**Priority**: LOW | **Timeline**: Week 3-4

1. Cloud, DevOps, ML/MLOps skills
2. Mobile app, CLI tool skills
3. Security, monitoring skills
4. Specialized domain skills (ADB, Figma, Notion)

**Rationale**: These provide additional capabilities but are lower priority than core development skills.

### Phase 6: Push Core Infrastructure Changes

**Priority**: LOW | **Timeline**: Week 4+

1. Python src/ layout migration
2. Multi-agent coordination patterns
3. Swarm topology improvements
4. Consensus algorithms

**Rationale**: These are architectural improvements that require careful review and may need broader discussion.

## Conflict Resolution Strategy

### Expected Conflicts

1. **Skill naming conventions** - Local uses different naming than GitHub
2. **Directory structure** - GitHub may have reorganized skill locations
3. **Documentation format** - Potential markdown style differences
4. **Hook implementations** - Different Python versions or APIs

### Resolution Approach

```bash
# For each conflict, use merge strategy:
git checkout --ours <file>   # Keep local version
git checkout --theirs <file>  # Keep GitHub version
git checkout -m <file>        # Merge manually

# Review and test after resolution
git diff HEAD
```

### Merge Guidelines

1. **Prefer GitHub versions** for standard skills
2. **Prefer local versions** for innovations (Collector v4.0)
3. **Manual merge** for documentation conflicts
4. **Test thoroughly** after resolving conflicts

## Validation Checklist

Before pushing to GitHub:

- [ ] All skills follow official Claude Code skill format
- [ ] Documentation is complete and well-formatted
- [ ] No local-specific paths or credentials
- [ ] Tests pass (if applicable)
- [ ] CHANGELOG updated
- [ ] Version bumped appropriately
- [ ] PR description is comprehensive
- [ ] Code review requested from maintainers

After pulling from GitHub:

- [ ] Skills load correctly in local environment
- [ ] No breaking changes to existing workflows
- [ ] Documentation is accessible
- [ ] Integration tests pass
- [ ] Hooks function as expected
- [ ] Backward compatibility maintained

## Communication Plan

### Internal Team

1. Share sync plan in team meeting
2. Assign owners for each phase
3. Set up progress tracking
4. Schedule checkpoints

### GitHub Community

1. Open discussion issue for Collector v4.0
2. Gather feedback before PR
3. Respond to PR comments promptly
4. Document lessons learned

## Risk Assessment

### High Risk

- **Breaking changes** from GitHub main branch
- **Merge conflicts** in core infrastructure
- **API incompatibilities** between versions

**Mitigation**: Create backup branch, test in isolated environment, incremental merging

### Medium Risk

- **Skill duplication** between local and GitHub
- **Documentation inconsistencies**
- **Version mismatches**

**Mitigation**: Clear naming conventions, documentation review, version pinning

### Low Risk

- **Minor formatting differences**
- **Comment style variations**
- **Non-critical file differences**

**Mitigation**: Accept GitHub conventions, use linters, standardize formatting

## Success Metrics

- **Pull Success**: All 24 skills integrated without breaking existing workflows
- **Push Success**: Collector v4.0 PR approved and merged to main
- **Test Coverage**: 95%+ of new functionality covered
- **Documentation**: 100% of new skills documented
- **Community**: Positive feedback on contributions

## Timeline

| Week | Phase | Deliverable |
|------|-------|-------------|
| 1 | Pull Phase 1 | 5 critical domain skills integrated |
| 1 | Push Phase 2 | Collector v4.0 PR submitted |
| 2 | Pull Phase 3 | Builder skills integrated |
| 2-3 | Merge Phase 4 | SPEC-first-builders merged |
| 3-4 | Pull Phase 5 | Remaining domain skills integrated |
| 4+ | Push Phase 6 | Core infrastructure PR submitted |

## Next Steps

1. **Immediate**: Fetch latest from GitHub main
2. **Day 1**: Pull 5 critical domain skills
3. **Day 2-3**: Test and validate integration
4. **Day 4-5**: Prepare Collector v4.0 PR
5. **Week 2**: Submit PR and continue with builder skills

## Notes

- This document is a living guide and should be updated as sync progresses
- Priorities may shift based on team needs and GitHub activity
- Regular communication with GitHub maintainers is essential
- Document all decisions and rationale for future reference

---

**Last Updated**: 2025-12-04
**Status**: Ready for execution
**Owner**: Development Team
**Reviewers**: Architecture Team, GitHub Maintainers
