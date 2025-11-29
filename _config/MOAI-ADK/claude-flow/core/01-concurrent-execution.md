# Concurrent Execution Rules

> Claude-Flow's "Golden Rule": 1 MESSAGE = ALL RELATED OPERATIONS

## Overview

Claude-Flow enforces strict concurrent execution patterns to maximize efficiency and reduce token usage by 32.3%.

## The Golden Rule

```
⚡ "1 MESSAGE = ALL RELATED OPERATIONS"
```

All related operations MUST be batched in a single message. This is MANDATORY, not optional.

---

## Mandatory Batching Patterns

### 1. TodoWrite Batching

**Claude-Flow Rule**: ALWAYS batch ALL todos in ONE call (5-10+ todos minimum)

```javascript
// ✅ CORRECT: Single TodoWrite with all items
TodoWrite { todos: [
  {id: "1", content: "Research API patterns", status: "in_progress"},
  {id: "2", content: "Design database schema", status: "in_progress"},
  {id: "3", content: "Implement authentication", status: "pending"},
  {id: "4", content: "Build REST endpoints", status: "pending"},
  {id: "5", content: "Write unit tests", status: "pending"},
  {id: "6", content: "Integration tests", status: "pending"},
  {id: "7", content: "API documentation", status: "pending"},
  {id: "8", content: "Performance optimization", status: "pending"}
]}

// ❌ WRONG: Multiple separate TodoWrite calls
Message 1: TodoWrite { todos: [{id: "1", ...}] }
Message 2: TodoWrite { todos: [{id: "2", ...}] }
Message 3: TodoWrite { todos: [{id: "3", ...}] }
```

### 2. Task Tool (Agent Spawning) Batching

**Claude-Flow Rule**: ALWAYS spawn ALL agents in ONE message with full instructions

```javascript
// ✅ CORRECT: All agents in single message
[Single Message]:
  Task("Research agent", "Analyze requirements...", "researcher")
  Task("Coder agent", "Implement core features...", "coder")
  Task("Tester agent", "Create comprehensive tests...", "tester")
  Task("Reviewer agent", "Review code quality...", "reviewer")
  Task("Architect agent", "Design system architecture...", "system-architect")

// ❌ WRONG: Sequential agent spawning
Message 1: Task("Research agent", ...)
Message 2: Task("Coder agent", ...)
Message 3: Task("Tester agent", ...)
```

### 3. File Operations Batching

**Claude-Flow Rule**: ALWAYS batch ALL reads/writes/edits in ONE message

```javascript
// ✅ CORRECT: Parallel file operations
[Single Message]:
  Write "app/package.json"
  Write "app/src/server.js"
  Write "app/tests/server.test.js"
  Write "app/docs/API.md"
  Bash "mkdir -p app/{src,tests,docs,config}"

// ❌ WRONG: Sequential file operations
Message 1: Write "app/package.json"
Message 2: Write "app/src/server.js"
Message 3: Write "app/tests/server.test.js"
```

### 4. Bash Commands Batching

**Claude-Flow Rule**: ALWAYS batch ALL terminal operations in ONE message

```javascript
// ✅ CORRECT: All bash in one message
[Single Message]:
  Bash "npm install"
  Bash "npm run build"
  Bash "npm test"
  Bash "npm run lint"

// ❌ WRONG: Sequential bash calls
Message 1: Bash "npm install"
Message 2: Bash "npm run build"
```

### 5. Memory Operations Batching

**Claude-Flow Rule**: ALWAYS batch ALL memory store/retrieve in ONE message

```javascript
// ✅ CORRECT: All memory ops together
[Single Message]:
  mcp__claude-flow__memory_store { key: "api/schema", value: {...} }
  mcp__claude-flow__memory_store { key: "api/endpoints", value: {...} }
  mcp__claude-flow__memory_retrieve { key: "api/config" }
```

---

## MoAI Current State

### What MoAI Has
- Rule 7 in CLAUDE.md allows parallel Task() calls
- File operations can be batched
- No explicit batching enforcement

### What's Missing
- **No "Golden Rule" enforcement**: Operations can still be sequential
- **No minimum todo count**: TodoWrite accepts single items
- **No batching validation**: No checks for single-message compliance

---

## Implementation Gap

| Aspect | Claude-Flow | MoAI |
|--------|-------------|------|
| Batching Rule | MANDATORY | Optional |
| Min Todos | 5-10+ | 1 |
| Validation | Enforced | None |
| Token Savings | 32.3% | Unknown |

## Recommendation

Add to MoAI CLAUDE.md Rule 11:

```markdown
### Rule 11: Concurrent Execution (Golden Rule)

Alfred MUST batch all related operations in a SINGLE message:

**MANDATORY patterns:**
- TodoWrite: Batch ALL todos (minimum 5 items)
- Task(): Spawn ALL independent agents together
- File operations: Batch ALL reads/writes/edits
- Bash commands: Batch ALL terminal operations

**Violation**: Multiple messages for related operations = inefficient execution
```

---

## Benefits

| Metric | Improvement |
|--------|-------------|
| Token Usage | -32.3% |
| Speed | 2.8-4.4x faster |
| Context Efficiency | Reduced message overhead |
| Coordination | Better parallel execution |
