# PRD-04: MCP vs Task Distinction

> Clarify the roles of MCP tools vs Task() execution

## Overview

| Field | Value |
|-------|-------|
| **Priority** | P1 (Critical) |
| **Effort** | Low (1 day) |
| **Impact** | Medium |
| **Type** | Documentation |

---

## Problem Statement

Users and agents may confuse MCP tool capabilities with agent execution. Claude-Flow explicitly distinguishes these:

- **MCP tools**: Provide CAPABILITIES (documentation, browser, coordination)
- **Task()**: Provides EXECUTION (actual agent work)

MoAI needs to document this distinction clearly to prevent confusion.

### Current Confusion

```
❌ COMMON MISCONCEPTION:

User thinks: "mcp__context7__get-library-docs will spawn an agent"
Reality: It only fetches documentation

User thinks: "Task() and MCP are interchangeable"
Reality: They serve different purposes
```

### Desired Clarity

```
✅ CLEAR UNDERSTANDING:

MCP = Tools that PROVIDE capabilities
  └── context7: Documentation lookup
  └── playwright: Browser automation
  └── sequential-thinking: Complex reasoning
  └── figma: Design access
  └── github: File operations
  └── notion: Workspace access

Task() = EXECUTES agents
  └── Spawns subagent process
  └── Performs actual work
  └── Returns results
```

---

## Solution

### Add Rule 12 to CLAUDE.md

```markdown
### Rule 12: MCP vs Task Distinction

**MCP tools and Task() serve fundamentally different purposes.**

**MCP Tools = CAPABILITIES**

MCP servers provide specific capabilities that agents can USE:

| MCP Server | Purpose | Capabilities |
|------------|---------|--------------|
| `context7` | Documentation | `resolve-library-id`, `get-library-docs` |
| `playwright` | Browser | Navigate, click, screenshot, etc. |
| `sequential-thinking` | Reasoning | Complex multi-step analysis |
| `figma` | Design | Get design context, screenshots |
| `github` | Repository | File operations, push |
| `notion` | Workspace | Page, database operations |

**Example MCP Usage**:
```python
# Get documentation (capability)
mcp__context7__get-library-docs { libraryId: "react", topic: "hooks" }

# Take screenshot (capability)
mcp__playwright__screenshot { url: "http://example.com" }

# Complex reasoning (capability)
mcp__sequential-thinking__analyze { problem: "..." }
```

**Task() = EXECUTION**

Task() spawns agents that DO ACTUAL WORK:

```python
# Spawn agent to implement feature
Task(subagent_type="expert-backend", prompt="Build REST API...")

# Spawn agent to write tests
Task(subagent_type="manager-tdd", prompt="Write tests for...")

# Spawn agent to review code
Task(subagent_type="expert-debug", prompt="Debug the error...")
```

**Key Differences**:

| Aspect | MCP Tools | Task() |
|--------|-----------|--------|
| Purpose | Provide capability | Execute work |
| Spawns agent? | No | Yes |
| Does implementation? | No | Yes |
| Returns | Data/result | Agent report |
| Context | Same context | Separate context |

**NEVER Confuse**:
- ❌ Expecting MCP to do implementation
- ❌ Using Task() for simple lookups
- ❌ Thinking MCP spawns agents

**Correct Usage Pattern**:
```python
# Step 1: Use MCP for capability (documentation)
docs = mcp__context7__get-library-docs { libraryId: "fastapi" }

# Step 2: Use Task() for execution (implementation)
Task(subagent_type="expert-backend",
     prompt="Using FastAPI (see context7 docs), build REST API...")
```
```

---

## Implementation Plan

### Day 1: Documentation Updates

**Task 1.1**: Add Rule 12 to CLAUDE.md

Insert after Rule 11 (Concurrent Batching).

**Task 1.2**: Update MCP Server Documentation

Add clarity to `.claude/servers/README.md`:

```markdown
## MCP Server Purpose

MCP servers provide CAPABILITIES, not agent execution.

Think of MCP tools as:
- Documentation library (context7)
- Browser robot (playwright)
- Thinking assistant (sequential-thinking)
- Design viewer (figma)
- Git helper (github)
- Workspace connector (notion)

For actual implementation work, use Task() to spawn agents.
```

**Task 1.3**: Update Agent Instructions

Add reminder to key agents about MCP vs Task distinction.

---

## Configuration (No Changes Needed)

This PRD is documentation-only. No configuration changes required.

---

## Acceptance Criteria

- [ ] Rule 12 added to CLAUDE.md
- [ ] Clear table differentiating MCP vs Task
- [ ] Examples showing correct usage pattern
- [ ] MCP server README updated
- [ ] Anti-patterns documented

---

## Impact Assessment

### User Understanding

| Aspect | Before | After |
|--------|--------|-------|
| MCP purpose | Unclear | Clear |
| Task purpose | Mixed usage | Proper usage |
| When to use each | Guessing | Documented |

### Error Reduction

Clear documentation should reduce:
- Incorrect MCP expectations
- Misuse of Task() for simple lookups
- Confusion in agent prompts

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Documentation complete | 100% |
| User confusion (reported) | 50% reduction |
| Correct usage patterns (observed) | 80% |

---

## Related Documents

- [MCP vs Claude Code](../mcp/01-claude-vs-mcp.md)
- [MCP Tool Categories](../mcp/02-mcp-tool-categories.md)
- [PRD-00 Overview](PRD-00-overview.md)

---

## Appendix: Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│           MCP vs TASK() QUICK REFERENCE                 │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  MCP TOOLS (Capabilities)        TASK() (Execution)    │
│  ─────────────────────────       ────────────────────  │
│  • Lookup documentation          • Build features       │
│  • Control browser               • Write code           │
│  • Access designs                • Fix bugs             │
│  • Query workspace               • Write tests          │
│  • Complex reasoning             • Review code          │
│                                                         │
│  mcp__context7__*                Task(expert-backend)  │
│  mcp__playwright__*              Task(manager-tdd)     │
│  mcp__sequential-thinking__*     Task(expert-debug)    │
│  mcp__figma__*                   Task(expert-frontend) │
│  mcp__github__*                  Task(manager-docs)    │
│  mcp__notion__*                  Task(builder-agent)   │
│                                                         │
│  NO agent spawning               YES agent spawning    │
│  Returns data                    Returns report        │
│  Same context                    Separate context      │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## Timeline

```
Day 1:
├── Morning: Draft Rule 12
├── Afternoon: Update CLAUDE.md
└── Evening: Update MCP docs, review

Total: 1 day
```
