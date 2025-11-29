# Claude-Flow to MoAI Agent Mapping

> Complete mapping between 54 Claude-Flow agents and 56 MoAI agents

## Overview

This document provides a comprehensive mapping to help translate Claude-Flow patterns to MoAI equivalents.

---

## Mapping Summary

| Status | Count | Description |
|--------|-------|-------------|
| Strong Match | 12 | Direct equivalent exists |
| Partial Match | 18 | Similar functionality |
| No Match (CF→MoAI) | 24 | Claude-Flow unique |
| No Match (MoAI→CF) | 20 | MoAI unique |

---

## Strong Matches (12)

| Claude-Flow | MoAI | Confidence |
|-------------|------|------------|
| `coder` | `expert-backend` / `expert-frontend` | 95% |
| `tester` | `manager-tdd` | 90% |
| `reviewer` | `manager-quality` | 85% |
| `planner` | `manager-strategy` | 85% |
| `researcher` | `Explore` (built-in) | 90% |
| `backend-dev` | `expert-backend` | 95% |
| `cicd-engineer` | `expert-devops` | 90% |
| `security-manager` | `expert-security` | 85% |
| `specification` | `manager-spec` | 90% |
| `refinement` | `manager-tdd` | 95% |
| `sparc-coord` | Alfred | 80% |
| `base-template-generator` | `builder-*` | 75% |

---

## Partial Matches (18)

| Claude-Flow | MoAI | Gap |
|-------------|------|-----|
| `github-modes` | `manager-git` | Less comprehensive |
| `pr-manager` | `manager-git` | PR-specific missing |
| `issue-tracker` | - | No issue management |
| `release-manager` | - | No release automation |
| `api-docs` | `manager-docs` | API-specific missing |
| `system-architect` | `manager-strategy` | Architecture focus |
| `code-analyzer` | `manager-quality` | Static analysis |
| `architecture` | `manager-strategy` | Phase-specific |
| `pseudocode` | (in SPEC) | No dedicated agent |
| `perf-analyzer` | `expert-debug` | Performance specific |
| `task-orchestrator` | Alfred | Optimization |
| `smart-agent` | - | Adaptive behavior |
| `memory-coordinator` | - | Memory management |
| `production-validator` | `manager-quality` | Production specific |
| `migration-planner` | - | Migration specific |
| `swarm-init` | - | Swarm initialization |
| `workflow-automation` | - | Actions specific |
| `repo-architect` | - | Repo structure |

---

## Claude-Flow Unique (24) - No MoAI Equivalent

### Swarm Coordination (5)
- `hierarchical-coordinator`
- `mesh-coordinator`
- `adaptive-coordinator`
- `collective-intelligence-coordinator`
- `swarm-memory-manager`

### Consensus & Distributed (7)
- `byzantine-coordinator`
- `raft-manager`
- `gossip-coordinator`
- `consensus-builder`
- `crdt-synchronizer`
- `quorum-manager`
- (Note: `security-manager` has partial match)

### GitHub Advanced (6)
- `code-review-swarm`
- `project-board-sync`
- `multi-repo-swarm`
- `issue-tracker`
- `release-manager`
- `workflow-automation`

### Specialized (6)
- `mobile-dev`
- `ml-developer`
- `performance-benchmarker`
- `sparc-coder`
- `tdd-london-swarm`
- `smart-agent`

---

## MoAI Unique (20) - No Claude-Flow Equivalent

### Expert Tier (4)
- `expert-frontend` (dedicated frontend)
- `expert-database` (dedicated database)
- `expert-uiux` (UI/UX design)
- `expert-debug` (debugging focus)

### Manager Tier (6)
- `manager-project` (project init)
- `manager-docs` (dedicated docs)
- `manager-claude-code` (CC management)
- (Note: Others have partial matches)

### Builder Tier (3)
- `builder-agent` (agent creation)
- `builder-skill` (skill creation)
- `builder-command` (command creation)

### MCP Tier (5)
- `mcp-context7` (documentation)
- `mcp-figma` (design)
- `mcp-notion` (workspace)
- `mcp-playwright` (testing)
- `mcp-sequential-thinking` (reasoning)

### AI Tier (1)
- `ai-nano-banana` (AI integration)

### Built-in (1)
- `Plan` (planning mode)

---

## Translation Guide

### When to Use Which

| Task | Claude-Flow | MoAI |
|------|-------------|------|
| Write backend code | `coder` / `backend-dev` | `expert-backend` |
| Write frontend code | `coder` | `expert-frontend` |
| Write tests | `tester` | `manager-tdd` |
| Review code | `reviewer` | `manager-quality` |
| Design architecture | `system-architect` | `manager-strategy` |
| Create SPEC | `specification` | `manager-spec` |
| Run TDD | `refinement` / `tdd-london-swarm` | `manager-tdd` |
| Manage Git | `github-modes` / `pr-manager` | `manager-git` |
| Research docs | `researcher` | `mcp-context7` |
| Debug issues | `code-analyzer` | `expert-debug` |
| Security review | `security-manager` | `expert-security` |
| DevOps/CI | `cicd-engineer` | `expert-devops` |
| UI/UX design | - | `expert-uiux` |
| Database design | `backend-dev` | `expert-database` |

---

## Gap Summary

### High Priority Gaps (Should Add to MoAI)

| Gap | Agents | Impact |
|-----|--------|--------|
| Swarm Coordination | 5 agents | High |
| GitHub Enhancement | 6 agents | Medium-High |
| Mobile Development | 1 agent | Medium |
| ML Development | 1 agent | Medium |

### Claude-Flow Should Consider (From MoAI)

| Gap | Agents | Value |
|-----|--------|-------|
| Dedicated Frontend | 1 agent | High |
| Dedicated Database | 1 agent | High |
| UI/UX Design | 1 agent | Medium |
| Debugging Focus | 1 agent | Medium |
| MCP Integration | 5 agents | High |
| Builder/Meta | 3 agents | Medium |

---

## Recommendation

### For MoAI Migration
1. Map existing Claude-Flow workflows to MoAI commands
2. Identify swarm requirements (may need addition)
3. Use MoAI's specialized experts for better domain coverage
4. Leverage Skills system for knowledge capsules

### For MoAI Enhancement
1. Add swarm coordination tier
2. Enhance GitHub integration
3. Add mobile and ML experts
4. Add performance benchmarking
