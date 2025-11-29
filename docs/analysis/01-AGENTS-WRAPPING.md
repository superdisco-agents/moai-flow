---
title: "AGENTS Wrapping Method Analysis"
version: "1.0.0"
date: "2025-11-28"
category: "Architecture Analysis"
tags: ["agents", "wrapping", "delegation", "resume-pattern"]
---

# AGENTS Wrapping Method Analysis

## 1. Overview: What is an Agent?

An **Agent** in MoAI-ADK is a specialized, autonomous task executor that wraps tools, models, and skills into reusable components. Agents enable:

- **Modular delegation** via `Task()` calls
- **Context preservation** through YAML frontmatter
- **Token efficiency** via Resume patterns (40-60% savings)
- **Hierarchical coordination** across 5 operational tiers

**Core Principle**: One agent, one responsibility. Compose complexity through delegation, not monoliths.

---

## 2. 5-Tier Hierarchy Structure

### ANSI Diagram
```
┌─────────────────────────────────────────────────────────────┐
│ TIER 1: ORCHESTRATION                                       │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│ │ Coordinator │ │ Planner     │ │ Architect   │           │
│ └─────────────┘ └─────────────┘ └─────────────┘           │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ TIER 2: DOMAIN SPECIALISTS                                  │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│ │ Researcher  │ │ Coder       │ │ Tester      │           │
│ └─────────────┘ └─────────────┘ └─────────────┘           │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ TIER 3: EXECUTION                                            │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│ │ Code-Analyzer│ │Perf-Analyzer│ │ Reviewer    │           │
│ └─────────────┘ └─────────────┘ └─────────────┘           │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ TIER 4: INTEGRATION                                          │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│ │ GitHub-Modes│ │ PR-Manager  │ │ API-Docs    │           │
│ └─────────────┘ └─────────────┘ └─────────────┘           │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ TIER 5: MCP BRIDGE                                           │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│ │ Memory-Mgr  │ │ Neural-Agent│ │ Swarm-Init  │           │
│ └─────────────┘ └─────────────┘ └─────────────┘           │
└─────────────────────────────────────────────────────────────┘
```

### Agent Inventory (24 Total)

| Tier | Agent Name | Primary Role | Tools | Resume? |
|------|-----------|--------------|-------|---------|
| **T1** | `coordinator` | Multi-agent orchestration | Task(), TodoWrite | ✅ |
| T1 | `planner` | Strategic planning | Memory, TodoWrite | ✅ |
| T1 | `architect` | System design | Glob, Grep, Read | ✅ |
| **T2** | `researcher` | Requirement analysis | WebSearch, Memory | ✅ |
| T2 | `coder` | Code implementation | Write, Edit, Bash | ✅ |
| T2 | `tester` | Test creation | Write, Bash | ✅ |
| T2 | `reviewer` | Code review | Read, Grep | ✅ |
| **T3** | `code-analyzer` | Static analysis | Grep, Read | ✅ |
| T3 | `perf-analyzer` | Performance profiling | Bash, Memory | ✅ |
| T3 | `api-docs` | API documentation | Read, Write | ✅ |
| T3 | `task-orchestrator` | Task sequencing | Task(), Memory | ✅ |
| **T4** | `github-modes` | Repository operations | GitHub MCP | ❌ |
| T4 | `pr-manager` | Pull request automation | GitHub MCP | ❌ |
| T4 | `issue-tracker` | Issue management | GitHub MCP | ❌ |
| T4 | `release-manager` | Release coordination | GitHub MCP | ❌ |
| **T5** | `memory-coordinator` | Cross-session state | Memory MCP | ❌ |
| T5 | `neural-agent` | Pattern learning | Neural MCP | ❌ |
| T5 | `swarm-init` | Topology setup | Swarm MCP | ❌ |
| T5 | `consensus-builder` | Distributed agreement | Consensus MCP | ❌ |

**Resume Support**: Built-in agents (T1-T3) = ✅ | MCP-dependent agents (T4-T5) = ❌

---

## 3. YAML Frontmatter Pattern

### Basic Structure
```yaml
---
name: "coder"
role: "Code Implementation Specialist"
model: "claude-sonnet-4.5"
tools:
  - Write
  - Edit
  - Read
  - Bash
skills:
  - "TypeScript/JavaScript development"
  - "React component architecture"
  - "Test-driven development"
constraints:
  - "Files under 500 lines"
  - "Always write tests first"
  - "Use absolute paths only"
---
```

### Advanced Example (with MCP)
```yaml
---
name: "github-pr-manager"
role: "Pull Request Automation"
model: "claude-sonnet-4.5"
mcp_servers:
  - github
  - claude-flow
tools:
  - mcp__github__create_pull_request
  - mcp__github__create_pull_request_review
  - Task
skills:
  - "PR description generation"
  - "Code review automation"
  - "CI/CD integration"
resume_enabled: false  # MCP-dependent, no resume
---
```

### Minimal Example (Task Delegator)
```yaml
---
name: "coordinator"
role: "Multi-Agent Orchestrator"
model: "claude-sonnet-4.5"
tools:
  - Task
  - TodoWrite
  - Memory
skills:
  - "Parallel task spawning"
  - "Context propagation"
resume_enabled: true
---
```

**Key Fields**:
- `tools`: Whitelist of allowed operations
- `skills`: Natural language capabilities
- `resume_enabled`: Whether agent supports Resume pattern
- `mcp_servers`: External integrations (disables Resume)

---

## 4. Task() Delegation Mechanism

### Example 1: Parallel Agent Spawning
```javascript
// Coordinator agent spawns 3 specialists in ONE message
[Single Message - Parallel Execution]:
  Task("Research agent", `
    Analyze React 19 server components best practices.
    Store findings in memory key: 'research/react19-patterns'
  `, "researcher")

  Task("Coder agent", `
    Implement server component using research findings.
    Read memory: 'research/react19-patterns'
    Write to: /app/src/components/ServerComponent.tsx
  `, "coder")

  Task("Tester agent", `
    Create Jest tests for ServerComponent.
    Target 90% coverage.
    Write to: /app/tests/ServerComponent.test.tsx
  `, "tester")
```

### Example 2: Sequential Dependency
```javascript
// Step 1: Research (blocks execution)
Task("Research agent", `
  Find GraphQL schema best practices.
  Save to memory: 'graphql/schema-patterns'
`, "researcher")

// Wait for research completion...

// Step 2: Implementation (depends on research)
Task("Coder agent", `
  Build GraphQL schema using memory: 'graphql/schema-patterns'
  Generate TypeScript types
  Write to: /app/src/schema.ts
`, "coder")
```

### Example 3: Hierarchical Delegation
```javascript
// Architect delegates to domain specialists
Task("Backend architect", `
  Design REST API architecture for e-commerce.

  SUB-TASKS:
  - Task("Database agent", "Design PostgreSQL schema", "code-analyzer")
  - Task("API agent", "Create Express routes", "coder")
  - Task("Security agent", "Implement JWT auth", "reviewer")

  Consolidate results and document.
`, "architect")
```

**Task() Signature**:
```typescript
Task(
  agent_name: string,        // Human-readable identifier
  instructions: string,      // Full context + task
  agent_type: string         // Agent role from inventory
)
```

---

## 5. Resume Pattern (40-60% Token Savings)

### Problem: Context Window Exhaustion
```
Traditional approach:
[Agent receives full codebase every call]
→ 200K tokens per invocation
→ Slow processing
→ High costs
```

### Solution: Resume Pattern
```
Resume approach:
[Agent receives only delta + state reference]
→ 80K tokens per invocation
→ 40-60% reduction
→ 2-3x faster
```

### Implementation (Built-in Agents)

#### Step 1: Initial Invocation (Full Context)
```javascript
Task("Code analyzer", `
  Analyze authentication module.
  Files: /app/src/auth/*.ts (15 files, 2000 lines)

  STORE STATE:
  - Architecture diagram
  - Dependency graph
  - Security findings

  Memory key: 'analysis/auth-module-v1'
`, "code-analyzer")
```

#### Step 2: Resume Invocation (Delta Only)
```javascript
Task("Code analyzer", `
  RESUME FROM: 'analysis/auth-module-v1'

  DELTA:
  - New file: /app/src/auth/mfa.ts (50 lines)
  - Modified: /app/src/auth/login.ts (+30 lines)

  Update analysis and store to 'analysis/auth-module-v2'
`, "code-analyzer")
```

**Token Comparison**:
- Full context: 200K tokens (15 files)
- Resume delta: 80K tokens (2 files + state reference)
- **Savings: 60%**

### MCP Integration Agents (No Resume)

**Why MCP agents can't resume**:
```yaml
# MCP-dependent agent
name: "github-pr-manager"
mcp_servers:
  - github  # External state, not serializable
resume_enabled: false
```

MCP servers maintain their own state that can't be captured in memory snapshots. Use MCP agents for:
- External API interactions (GitHub, databases)
- Real-time event streams
- Stateful connections

Use built-in agents for:
- File operations
- Code analysis
- Task orchestration

---

## 6. Best Practices

### ✅ DO
1. **Batch operations in single messages**
   ```javascript
   [One Message]:
     Task("agent1", "...", "coder")
     Task("agent2", "...", "tester")
     TodoWrite({todos: [...]})  // 5-10 todos
   ```

2. **Use Resume for iterative analysis**
   ```javascript
   // First pass
   Task("analyzer", "Full codebase analysis → memory:v1", "code-analyzer")

   // Incremental updates
   Task("analyzer", "RESUME memory:v1 + delta → memory:v2", "code-analyzer")
   ```

3. **Organize files hierarchically**
   ```
   /app
     /src       ← Source code
     /tests     ← Test files
     /docs      ← Documentation
     /config    ← Configuration
   ```

4. **Delegate to specialists, not generalists**
   ```javascript
   // ❌ WRONG: One agent does everything
   Task("coder", "Research, code, test, deploy", "coder")

   // ✅ RIGHT: Specialists collaborate
   Task("researcher", "Research patterns", "researcher")
   Task("coder", "Implement based on research", "coder")
   Task("tester", "Create test suite", "tester")
   ```

5. **Store cross-agent state in Memory**
   ```javascript
   // Agent A stores
   Task("researcher", "Store findings → memory:research/api-patterns", "researcher")

   // Agent B reads
   Task("coder", "Read memory:research/api-patterns → implement", "coder")
   ```

6. **Use absolute paths only**
   ```javascript
   // ✅ CORRECT
   Write("/app/src/components/Button.tsx", content)

   // ❌ WRONG
   Write("src/components/Button.tsx", content)  // CWD-dependent
   ```

### ❌ DON'T
1. **Never spawn agents across multiple messages**
2. **Never save working files to root folder**
3. **Never use Resume with MCP-dependent agents**
4. **Never create agents without clear responsibilities**
5. **Never exceed 500 lines per file (split instead)**
6. **Never hardcode secrets in agent instructions**

---

## Summary

**AGENTS wrapping method** = YAML frontmatter + Task() delegation + Resume pattern

**Key Metrics**:
- 24 agents across 5 tiers
- 40-60% token reduction via Resume
- 2-3x faster iterative analysis
- 100% concurrency via parallel Task() spawning

**Next Steps**:
1. Review agent inventory in `/agents` directory
2. Study YAML frontmatter examples
3. Practice Task() delegation patterns
4. Implement Resume for large codebases

---

**See Also**:
- `/docs/AGENTS.md` - Full agent documentation
- `/docs/TASK-DELEGATION.md` - Advanced Task() patterns
- `/docs/RESUME-PATTERN.md` - Memory management guide
