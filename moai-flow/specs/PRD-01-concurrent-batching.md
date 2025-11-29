# PRD-01: Concurrent Batching

> Implement MoAI-Flow's concurrent execution patterns in MoAI

## Overview

| Field | Value |
|-------|-------|
| **Priority** | P1 (Critical) |
| **Effort** | Low (1-2 days) |
| **Impact** | High |
| **Type** | Documentation + Best Practice |
| **Status** | In Progress |
| **Status Reason** | Rule 11 placeholder replaced with full content. Testing in progress. |
| **Notes** | Rule 11 content completed in CLAUDE.md |

---

## Problem Statement

MoAI users often execute operations sequentially when parallel execution would be more efficient. MoAI-Flow's "Golden Rule" of concurrent batching significantly improves performance.

### Current State

```
❌ CURRENT MOAI PATTERN (Inefficient):

Message 1: Task("Research API patterns")
[Wait for response]
Message 2: Task("Research database patterns")
[Wait for response]
Message 3: Task("Research frontend patterns")
[Wait for response]

Total time: ~3x single task
```

### Desired State

```
✅ CONCURRENT PATTERN (Efficient):

Single Message:
  Task("Research API patterns")
  Task("Research database patterns")
  Task("Research frontend patterns")

Total time: ~1x single task (parallel execution)
```

---

## Solution

### 1. Document Golden Rule

Add to CLAUDE.md Rule 11:

```markdown
### Rule 11: Concurrent Batching (Golden Rule)

**1 MESSAGE = ALL RELATED OPERATIONS**

Alfred and all agents MUST batch related operations in a single message for parallel execution.

**Batch These Operations**:

1. **Multiple Task() calls** (independent agents):
   ```python
   # SINGLE MESSAGE with all three:
   Task(subagent_type="expert-backend", prompt="Build REST API")
   Task(subagent_type="expert-frontend", prompt="Build React UI")
   Task(subagent_type="manager-tdd", prompt="Write tests")
   ```

2. **Multiple file operations**:
   ```python
   # SINGLE MESSAGE:
   Read("src/main.py")
   Read("src/utils.py")
   Read("src/config.py")
   ```

3. **Multiple search operations**:
   ```python
   # SINGLE MESSAGE:
   Grep(pattern="TODO")
   Grep(pattern="FIXME")
   Glob(pattern="**/*.test.ts")
   ```

4. **TodoWrite items**:
   ```python
   # SINGLE MESSAGE with all todos:
   TodoWrite([
     {"content": "Task 1", "status": "pending"},
     {"content": "Task 2", "status": "pending"},
     {"content": "Task 3", "status": "pending"}
   ])
   ```

**Exceptions** (Sequential Required):
- Operations with dependencies
- Operations where output affects next input
- Iterative refinement loops

**Anti-Patterns to Avoid**:
- ❌ One Task() per message
- ❌ Reading files one at a time
- ❌ Adding todos individually
- ❌ Sequential searches when parallel possible
```

### 2. Update CLAUDE.md

Add Rule 11 after existing rules.

### 3. Agent Instructions

Update agent prompts to include batching guidance.

---

## Implementation Plan

### Phase 1: Documentation (Day 1)

**Task 1.1**: Add Rule 11 to CLAUDE.md
- Insert new rule section
- Add examples and anti-patterns
- Document exceptions

**Task 1.2**: Update Alfred guidance
- Add batching checks to Rule 1 (8-step process)
- Reference Rule 11 in delegation

### Phase 2: Agent Updates (Day 2)

**Task 2.1**: Update agent templates
- Add concurrent batching reminder to agent definitions
- Include in skill patterns

**Task 2.2**: Add validation
- Optionally add hook to detect sequential patterns
- Log warnings for inefficient patterns

---

## Acceptance Criteria

- [x] Rule 11 content completed in CLAUDE.md
- [ ] Examples cover Task(), Read, Grep, Glob, TodoWrite batching
- [ ] Exceptions are clearly documented
- [ ] Anti-patterns are identified
- [ ] Agent templates reference batching best practice
- [ ] Testing concurrent batching in production workflows
- [ ] Performance metrics validation

---

## Impact Assessment

### Performance Improvement

| Scenario | Before | After | Improvement |
|----------|--------|-------|-------------|
| 3 parallel agents | 3x time | 1x time | 66% faster |
| 5 file reads | 5x time | 1x time | 80% faster |
| 3 search operations | 3x time | 1x time | 66% faster |

### Token Efficiency

Batched operations reduce context overhead:
- Fewer message boundaries
- Less repetitive context
- More efficient token usage

---

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Users ignore guidance | Medium | Low | Add to onboarding, highlight in docs |
| Over-batching unrelated ops | Low | Low | Document exceptions clearly |
| Tool limitations | Low | Low | Test batch limits |

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Documentation complete | 100% |
| Agent templates updated | 100% |
| User adoption (observed) | 50% within 1 month |

---

## Related Documents

- [MoAI-Flow Concurrent Execution](../core/01-concurrent-execution.md)
- [MoAI CLAUDE.md](/CLAUDE.md)
- [PRD-00 Overview](PRD-00-overview.md)

---

## Appendix: Full Rule 11 Text

```markdown
### Rule 11: Concurrent Batching (Golden Rule)

**1 MESSAGE = ALL RELATED OPERATIONS**

Alfred and all agents MUST execute related operations concurrently by batching them in a single message.

**Why Batching Matters**:
- Parallel execution reduces total time
- Fewer message round-trips
- More efficient token usage
- Better resource utilization

**Always Batch**:

1. **Independent Agent Tasks**:
   ```python
   # ✅ CORRECT: Single message
   Task(subagent_type="expert-backend", prompt="...")
   Task(subagent_type="expert-frontend", prompt="...")
   Task(subagent_type="manager-tdd", prompt="...")
   ```

2. **File Operations**:
   ```python
   # ✅ CORRECT: Single message
   Read("file1.py")
   Read("file2.py")
   Read("file3.py")
   ```

3. **Search Operations**:
   ```python
   # ✅ CORRECT: Single message
   Grep(pattern="pattern1")
   Grep(pattern="pattern2")
   Glob(pattern="**/*.ts")
   ```

4. **Todo Items**:
   ```python
   # ✅ CORRECT: Single call with all items
   TodoWrite([
     {"content": "Task 1", "status": "pending"},
     {"content": "Task 2", "status": "pending"},
     {"content": "Task 3", "status": "pending"}
   ])
   ```

**Never Batch** (Use Sequential):
- Operations with output dependencies
- Iterative refinement
- Conditional operations based on previous results

**Anti-Patterns**:
- ❌ One operation per message when parallelizable
- ❌ Sequential file reads for independent files
- ❌ Individual todo additions
- ❌ Separate searches that could run together
```

---

## Implementation Status

**Status**: ✅ Implemented
**Date**: 2025-11-29
**Location**: `/CLAUDE.md` Rule 11
**Documentation**: Rule 11 (Concurrent Batching) added to CLAUDE.md with full examples and anti-patterns.
