# Integration Patterns & Best Practices

**MOAI-ADK System Integration Guide**
*Commands → Agents → Skills → MCP Orchestration*

---

## 1. Overview: Integration Flow

```ansi
[0;36m┌─────────────────────────────────────────────────────────────┐[0m
[0;36m│[0m  [1;33mCommands[0m  →  [1;32mAgents[0m  →  [1;35mSkills[0m  →  [1;34mMCP Tools[0m  [0;36m│[0m
[0;36m└─────────────────────────────────────────────────────────────┘[0m

[1;33m/moai:1-plan[0m
    ↓
[1;32m/src/commands/plan-phase.ts[0m → Invokes [1;32mmanager-spec[0m agent
    ↓
[1;35m/skills/planning/[0m → Auto-loaded by agent manifest
    ↓
[1;34mmcp__serena-*__*[0m → Code analysis & file operations

**Key Principle**: Commands orchestrate high-level flows, agents execute domain logic, skills provide reusable modules, MCP tools handle low-level operations.

---

## 2. Core Integration Patterns

### Pattern 1: Command → Agent → Skills Chain

```ansi
[0;32m┌──────────────────────────────────────────────────────────┐[0m
[0;32m│[0m [1mPattern: /moai:1-plan Execution Chain[0m                [0;32m│[0m
[0;32m└──────────────────────────────────────────────────────────┘[0m

[1;33m1. Command Invocation[0m
   /moai:1-plan "Build REST API"
   ↓
[1;32m2. Agent Selection[0m (plan-phase.ts)
   agent: "manager-spec"
   task: "Analyze requirements, create S.P.E.C."
   ↓
[1;35m3. Skills Auto-Load[0m (agent manifest)
   - /skills/planning/requirement-analyzer.md
   - /skills/planning/spec-writer.md
   ↓
[1;34m4. MCP Tool Execution[0m
   mcp__serena-1__find_symbol → Code analysis
   mcp__serena-1__search_for_pattern → Find patterns
   ↓
[1;32m5. Output[0m
   /docs/01-SPEC.md created
```

**Implementation**:
```typescript
// /src/commands/plan-phase.ts
export const planPhase = {
  async execute(task: string) {
    // 1. Invoke agent
    const agent = await Task("manager-spec", task, "analyst");

    // 2. Skills auto-loaded via manifest
    // 3. Agent uses MCP tools internally
    // 4. Returns structured output
    return agent.result;
  }
};
```

---

### Pattern 2: MCP Resume Chain (Context Preservation)

```ansi
[0;36m┌──────────────────────────────────────────────────────────┐[0m
[0;36m│[0m [1mPattern: Multi-Step Agent Coordination[0m               [0;36m│[0m
[0;36m└──────────────────────────────────────────────────────────┘[0m

[1;33mStep 1: Planning Agent[0m
   agent_id: "agent_001"
   task: "Create specification"
   output: Store in memory
   ↓
[1;32mStep 2: Coding Agent[0m (Resumes context)
   agent_id: "agent_002"
   resume_from: "agent_001"  ← [1;31mCRITICAL[0m
   input: Read memory from agent_001
   ↓
[1;35mStep 3: Testing Agent[0m
   agent_id: "agent_003"
   resume_from: "agent_002"
   validates: Code from agent_002
```

**Implementation**:
```typescript
// Phase 1: Planning
const planAgent = await Task(
  "manager-spec",
  "Analyze requirements",
  "analyst",
  { agent_id: "plan_001" }
);

// Phase 2: Coding (resume context)
const codeAgent = await Task(
  "manager-code",
  "Implement based on plan_001",
  "coder",
  {
    agent_id: "code_002",
    resume_from: "plan_001"  // Links context
  }
);
```

---

### Pattern 3: Task Delegation (NEVER Direct File Ops)

```ansi
[0;31m┌──────────────────────────────────────────────────────────┐[0m
[0;31m│[0m [1m❌ ANTI-PATTERN: Direct File Operations[0m             [0;31m│[0m
[0;31m└──────────────────────────────────────────────────────────┘[0m

❌ WRONG:
   Command → Read("/src/file.ts")
   Command → Write("/docs/spec.md")

[0;32m┌──────────────────────────────────────────────────────────┐[0m
[0;32m│[0m [1m✅ CORRECT: Delegate to Agents[0m                       [0;32m│[0m
[0;32m└──────────────────────────────────────────────────────────┘[0m

✅ CORRECT:
   Command → Task("agent", "Analyze /src/file.ts")
             ↓
             Agent → MCP tools (Read, Write)
```

**Why?**
- Agents coordinate MCP tools
- Skills provide reusable logic
- Commands stay high-level
- Better error handling

---

### Pattern 4: Git 3-Mode Integration

```ansi
[0;35m┌──────────────────────────────────────────────────────────┐[0m
[0;35m│[0m [1mPattern: Git Mode Selection[0m                          [0;35m│[0m
[0;35m└──────────────────────────────────────────────────────────┘[0m

[1;33m/moai:git[0m → Prompts user:
   [1] Manual: You handle git commands
   [2] Personal: Auto-commit to feature branch
   [3] Team: Create PR for review

[1;32mManual Mode[0m:
   - No auto-commits
   - User runs: git add, git commit, git push

[1;34mPersonal Mode[0m:
   - Auto: git checkout -b feature/moai-<task>
   - Auto: git commit -am "feat: <description>"
   - Auto: git push origin feature/moai-<task>

[1;35mTeam Mode[0m:
   - All Personal mode actions
   - Auto: gh pr create --title "..." --body "..."
   - Waits for PR review
```

**Implementation**:
```typescript
// /src/commands/git-command.ts
export const gitCommand = {
  async execute(mode: "manual" | "personal" | "team") {
    if (mode === "manual") {
      return "Git commands ready. You control workflow.";
    }

    if (mode === "personal") {
      await Bash("git checkout -b feature/moai-$(date +%s)");
      await Bash("git commit -am 'feat: automated commit'");
      await Bash("git push origin HEAD");
    }

    if (mode === "team") {
      // ... personal mode steps ...
      await Bash("gh pr create --fill");
    }
  }
};
```

---

## 3. Best Practices

| Practice | Description | Example |
|----------|-------------|---------|
| **1. Single Responsibility** | Each command does ONE thing | `/moai:1-plan` → Only planning |
| **2. Agent Composition** | Use multiple agents for complex tasks | Plan → Code → Test chain |
| **3. Skills as Modules** | Reusable logic in `/skills` | `requirement-analyzer.md` |
| **4. MCP Abstraction** | Agents wrap MCP tools | Agent → `find_symbol()` not Command → `find_symbol()` |
| **5. Error Boundaries** | Try/catch at command level | Commands catch agent errors |
| **6. Context Passing** | Use `agent_id` and `resume_from` | Multi-step workflows |
| **7. Parallel Execution** | Batch independent operations | TodoWrite all todos at once |
| **8. File Organization** | NEVER save to root | Use `/docs`, `/src`, `/tests` |
| **9. Memory Management** | Store agent state in MCP memory | Share context between phases |
| **10. Idempotency** | Commands can run multiple times | Re-running `/moai:1-plan` is safe |
| **11. Progressive Enhancement** | Commands build on each other | 1-plan → 2-code → 3-test |
| **12. Documentation First** | Skills self-document | Markdown-based skills |

---

## 4. Common Anti-Patterns

### ❌ Anti-Pattern 1: Command Bloat
```typescript
// ❌ WRONG: Command does everything
export const megaCommand = {
  async execute() {
    await Read("/src/file.ts");
    await Write("/docs/spec.md");
    await Bash("npm test");
    await Task("agent", "...");
  }
};

// ✅ CORRECT: Command orchestrates agents
export const smartCommand = {
  async execute() {
    await Task("spec-agent", "Analyze and document");
    await Task("test-agent", "Run validation");
  }
};
```

### ❌ Anti-Pattern 2: Skill Duplication
```typescript
// ❌ WRONG: Same logic in multiple skills
/skills/planning/analyzer-v1.md
/skills/planning/analyzer-v2.md
/skills/coding/analyzer.md

// ✅ CORRECT: Shared skill module
/skills/shared/code-analyzer.md → Used by all agents
```

### ❌ Anti-Pattern 3: Broken Resume Chain
```typescript
// ❌ WRONG: No context linking
const agent1 = await Task("plan", "...");
const agent2 = await Task("code", "..."); // Lost context!

// ✅ CORRECT: Context preserved
const agent1 = await Task("plan", "...", { agent_id: "p1" });
const agent2 = await Task("code", "...", { resume_from: "p1" });
```

### ❌ Anti-Pattern 4: Direct MCP in Commands
```typescript
// ❌ WRONG: Command uses MCP directly
await mcp__serena_1__find_symbol({ name_path: "MyClass" });

// ✅ CORRECT: Agent uses MCP
await Task("analyzer", "Find MyClass symbol");
```

### ❌ Anti-Pattern 5: Root File Pollution
```typescript
// ❌ WRONG: Files in root
/test-file.md
/my-notes.txt
/temp-analysis.json

// ✅ CORRECT: Organized structure
/docs/analysis.md
/tests/integration.test.ts
/_config/temp-notes.txt
```

### ❌ Anti-Pattern 6: Sequential Operations (Should be Parallel)
```typescript
// ❌ WRONG: Sequential execution
await Task("agent1", "...");
await Task("agent2", "...");
await TodoWrite({ todos: [todo1] });
await TodoWrite({ todos: [todo2] });

// ✅ CORRECT: Parallel execution
await Promise.all([
  Task("agent1", "..."),
  Task("agent2", "..."),
  TodoWrite({ todos: [todo1, todo2] })
]);
```

---

## 5. Real-World Examples

### Example 1: Full SPARC Workflow

```typescript
// /moai:full-stack "Build user authentication"

// Step 1: Planning (/moai:1-plan)
const spec = await Task(
  "manager-spec",
  "Analyze auth requirements, create S.P.E.C.",
  "analyst",
  {
    agent_id: "auth_spec_001",
    skills: ["requirement-analyzer", "spec-writer"]
  }
);
// Output: /docs/01-SPEC.md

// Step 2: Pseudocode (/moai:2-pseudo)
const pseudo = await Task(
  "manager-pseudo",
  "Design auth algorithms based on auth_spec_001",
  "architect",
  {
    agent_id: "auth_pseudo_002",
    resume_from: "auth_spec_001"
  }
);
// Output: /docs/02-PSEUDOCODE.md

// Step 3: Architecture (/moai:3-arch)
const arch = await Task(
  "manager-arch",
  "Design auth system architecture",
  "system-architect",
  {
    agent_id: "auth_arch_003",
    resume_from: "auth_pseudo_002"
  }
);
// Output: /docs/03-ARCHITECTURE.md

// Step 4: Refinement (/moai:4-refine)
const code = await Task(
  "manager-code",
  "Implement auth based on architecture",
  "coder",
  {
    agent_id: "auth_code_004",
    resume_from: "auth_arch_003"
  }
);
// Output: /src/auth/login.ts, /src/auth/register.ts

// Step 5: Completion (/moai:5-complete)
const tests = await Task(
  "manager-test",
  "Validate auth implementation",
  "tester",
  {
    agent_id: "auth_test_005",
    resume_from: "auth_code_004"
  }
);
// Output: /tests/auth.test.ts
```

**Key Features**:
- Each phase resumes previous context
- Skills auto-loaded per agent manifest
- Files organized in proper directories
- MCP tools abstracted behind agents

---

### Example 2: Parallel Agent Coordination

```typescript
// /moai:parallel-dev "Build API + Frontend + Tests"

// All agents execute concurrently
await Promise.all([
  Task(
    "backend-dev",
    "Build REST API with authentication hooks",
    "coder",
    { agent_id: "api_001" }
  ),

  Task(
    "frontend-dev",
    "Create React UI (resume from api_001 for contracts)",
    "coder",
    { agent_id: "ui_002", resume_from: "api_001" }
  ),

  Task(
    "test-engineer",
    "Write integration tests (watch api_001 + ui_002)",
    "tester",
    {
      agent_id: "tests_003",
      resume_from: ["api_001", "ui_002"]
    }
  ),

  TodoWrite({
    todos: [
      { id: "1", content: "API endpoints", status: "in_progress" },
      { id: "2", content: "React components", status: "in_progress" },
      { id: "3", content: "Integration tests", status: "in_progress" },
      { id: "4", content: "API documentation", status: "pending" }
    ]
  })
]);
```

**Benefits**:
- 3x faster than sequential
- Agents coordinate via `resume_from`
- Todos batched in single call
- Real-time progress tracking

---

### Example 3: Git Team Workflow

```typescript
// /moai:git team

// Workflow:
// 1. Create feature branch
await Bash("git checkout -b feature/moai-auth-$(date +%s)");

// 2. Agent makes changes
await Task(
  "manager-code",
  "Implement user authentication",
  "coder"
);

// 3. Auto-commit
await Bash("git add .");
await Bash("git commit -m 'feat: add user authentication with JWT'");

// 4. Push to remote
await Bash("git push origin HEAD");

// 5. Create PR
await Bash(`
  gh pr create \
    --title "feat: User Authentication System" \
    --body "Implements JWT-based auth with login/register endpoints" \
    --label "enhancement"
`);

// 6. Notify user
console.log("✅ PR created! Waiting for team review...");
```

---

## 6. Integration Checklist

Before deploying a new command/agent/skill:

- [ ] Command delegates to agents (not direct MCP calls)
- [ ] Agents load skills from `/skills` directory
- [ ] Skills are modular and reusable
- [ ] MCP tools wrapped by agent logic
- [ ] Files organized in `/src`, `/docs`, `/tests` (NOT root)
- [ ] Resume chain uses `agent_id` + `resume_from`
- [ ] Parallel operations batched in single message
- [ ] Error handling at command level
- [ ] Documentation updated in `/docs`
- [ ] Git mode selected (manual/personal/team)

---

## 7. Performance Optimization

### Optimization 1: Batch MCP Calls
```typescript
// ❌ SLOW: Sequential MCP calls
await mcp__serena_1__find_symbol({ name_path: "Class1" });
await mcp__serena_1__find_symbol({ name_path: "Class2" });

// ✅ FAST: Single agent call batches internally
await Task("analyzer", "Find Class1, Class2, Class3 symbols");
```

### Optimization 2: Parallel Agent Execution
```typescript
// ❌ SLOW: 12 seconds (4s × 3 agents)
await Task("agent1", "...");
await Task("agent2", "...");
await Task("agent3", "...");

// ✅ FAST: 4 seconds (parallel execution)
await Promise.all([
  Task("agent1", "..."),
  Task("agent2", "..."),
  Task("agent3", "...")
]);
```

### Optimization 3: Skill Caching
```typescript
// Skills loaded once per agent session
// Subsequent calls reuse loaded skills
const agent = await Task("manager-spec", "...");
// Skills: requirement-analyzer.md, spec-writer.md loaded

// Next call reuses same skills
const agent2 = await Task("manager-spec", "...");
// No re-loading needed
```

---

**Last Updated**: November 28, 2025
**Status**: Production Ready ✅
**Token Count**: ~5,800 tokens
