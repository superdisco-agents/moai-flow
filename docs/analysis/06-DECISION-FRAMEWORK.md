# MOAI-ADK Decision Framework

## Overview

The MOAI-ADK Decision Framework provides a systematic approach to selecting the optimal agentic architecture pattern for your AI application. This framework helps developers navigate the complexity of choosing between different orchestration methods, coordination strategies, and execution models based on specific project requirements, constraints, and goals.

Rather than prescribing a one-size-fits-all solution, this framework emphasizes decision-making through clear evaluation criteria. It guides you through understanding your application's characteristics—such as task complexity, coordination needs, scalability requirements, and failure tolerance—to arrive at the most suitable architecture pattern. The framework is designed to be practical, actionable, and grounded in real-world use cases.

Use this guide when starting a new AI agent project, refactoring existing agent systems, or evaluating whether to switch architectural patterns. It complements the detailed analysis documents by providing a quick reference for architectural decision-making.

---

## Decision Flowchart

```
START: Define Your Agent Requirements
│
├─→ Single Task, Sequential Flow?
│   ├─ YES → Use Sequential Chain (LangGraph)
│   │         ├─ Need state persistence? → Add checkpointing
│   │         └─ Need human approval? → Add breakpoints
│   │
│   └─ NO → Continue ↓
│
├─→ Multiple Independent Tasks?
│   ├─ YES → Use Parallel Execution
│   │         ├─ Tasks share context? → Use Swarm (claude-flow)
│   │         └─ Tasks isolated? → Use Tool Calling (MCP)
│   │
│   └─ NO → Continue ↓
│
├─→ Dynamic Task Routing Required?
│   ├─ YES → Use Agent Router Pattern
│   │         ├─ Need coordination? → Swarm Router
│   │         └─ Simple dispatch? → LangGraph Router
│   │
│   └─ NO → Continue ↓
│
├─→ Complex Multi-Agent Collaboration?
│   ├─ YES → Use Hierarchical Coordination
│   │         ├─ Need consensus? → Byzantine/Raft (claude-flow)
│   │         ├─ Need memory? → Shared Memory Swarm
│   │         └─ Need autonomy? → Mesh Topology
│   │
│   └─ NO → Continue ↓
│
└─→ Real-Time Adaptation Required?
    ├─ YES → Use Reactive Swarm (claude-flow)
    └─ NO → Re-evaluate requirements or use Hybrid
```

---

## Comparison Matrix

| Criteria | Sequential Chain | Parallel Execution | Agent Router | Hierarchical Swarm | Reactive Swarm |
|----------|------------------|-------------------|--------------|-------------------|----------------|
| **Task Complexity** | Low-Medium | Low-Medium | Medium | High | Very High |
| **Coordination Need** | Minimal | None-Low | Medium | High | Very High |
| **Scalability** | Low | High | Medium | High | Very High |
| **Failure Recovery** | Manual | Manual | Automatic | Self-healing | Self-healing |
| **Learning Capability** | None | None | Limited | Medium | High |
| **Setup Complexity** | Low | Low | Medium | High | Very High |
| **Best For** | Workflows | Batch tasks | Routing | Teams | Adaptive systems |
| **Primary Tool** | LangGraph | MCP/claude-flow | Both | claude-flow | claude-flow |
| **State Management** | Centralized | Distributed | Hybrid | Distributed | Distributed |
| **Performance** | Sequential | Parallel | Mixed | Parallel | Parallel + Learning |

---

## Usage Guide

### 1. Assess Task Characteristics

**Questions to Ask:**
- Is this a single workflow or multiple independent tasks?
- Do tasks need to share context or run in isolation?
- Is the execution order fixed or dynamic?
- Do tasks need to wait for each other's results?

**Decision Points:**
- Single workflow + fixed order → Sequential Chain
- Multiple tasks + no dependencies → Parallel Execution
- Multiple tasks + shared context → Swarm Coordination
- Dynamic dependencies → Agent Router or Hierarchical

---

### 2. Evaluate Coordination Requirements

**Questions to Ask:**
- Do agents need to communicate during execution?
- Is consensus required for decisions?
- Should agents share memory or state?
- Do agents need to know about each other?

**Decision Points:**
- No communication needed → Tool Calling (MCP)
- Simple handoffs → Sequential Chain (LangGraph)
- Active collaboration → Swarm (claude-flow)
- Consensus needed → Byzantine/Raft Swarm

---

### 3. Consider Scalability Needs

**Questions to Ask:**
- How many agents will run concurrently?
- Will the number of agents grow over time?
- Do you need dynamic agent spawning?
- Is load balancing required?

**Decision Points:**
- 1-3 agents, fixed → LangGraph Parallel
- 4-10 agents, dynamic → claude-flow Swarm
- 10+ agents, auto-scaling → Hierarchical Swarm
- Batch processing → Parallel Tool Calling

---

### 4. Determine Failure Tolerance

**Questions to Ask:**
- What happens if one agent fails?
- Is retry logic needed?
- Should the system self-heal?
- Are checkpoints required?

**Decision Points:**
- Manual retry acceptable → Basic patterns
- Need checkpointing → LangGraph with persistence
- Need self-healing → claude-flow with fault tolerance
- Critical reliability → Byzantine Swarm

---

### 5. Plan for Future Evolution

**Questions to Ask:**
- Will requirements change frequently?
- Do you need to add new agent types?
- Should the system learn from usage?
- Is migration to other patterns likely?

**Decision Points:**
- Stable requirements → Simple patterns
- Frequent changes → Modular architecture
- Need learning → Neural patterns (claude-flow)
- Uncertain future → Hybrid approach

---

## Decision Checklist

Use this checklist to validate your architectural choice:

- [ ] **Task Analysis**: I understand whether tasks are sequential, parallel, or mixed
- [ ] **Coordination Level**: I've identified the degree of inter-agent communication needed
- [ ] **Scalability Target**: I know the expected number of concurrent agents (now and future)
- [ ] **Failure Strategy**: I've defined what happens when agents fail or timeout
- [ ] **State Management**: I know where and how agent state will be stored
- [ ] **Performance Goals**: I've set latency and throughput requirements
- [ ] **Tooling Choice**: I've evaluated LangGraph, MCP, and claude-flow capabilities
- [ ] **Learning Needs**: I've determined if the system should adapt over time
- [ ] **Cost Constraints**: I've considered token usage and infrastructure costs
- [ ] **Team Expertise**: I've assessed my team's familiarity with the chosen tools

---

## Real Examples

### Example 1: Content Pipeline (Sequential Chain)

**Use Case**: Blog post creation pipeline with research → writing → editing → publishing

**Decision Rationale:**
- Fixed sequential workflow with clear handoffs
- Each step depends on previous output
- No parallelization possible
- Human review needed before publishing

**Architecture Choice**: LangGraph Sequential Chain with breakpoints

**Implementation:**
```python
# Simple, clear workflow with checkpointing
workflow = StateGraph(BlogState)
workflow.add_node("research", research_agent)
workflow.add_node("write", writing_agent)
workflow.add_node("edit", editing_agent)
workflow.add_edge("research", "write")
workflow.add_edge("write", "edit")
workflow.add_conditional_edges("edit", human_review, {"approve": END})
```

---

### Example 2: Data Analysis Dashboard (Parallel + Swarm)

**Use Case**: Real-time analytics dashboard processing multiple data sources simultaneously

**Decision Rationale:**
- 5+ independent data sources (APIs, databases, files)
- Sources can be processed in parallel
- Results need aggregation with shared context
- Need fault tolerance if one source fails

**Architecture Choice**: Hybrid (MCP for parallel fetching + claude-flow for aggregation)

**Implementation:**
```javascript
// Parallel fetch with MCP, coordinated aggregation with swarm
// Step 1: Parallel data fetching
await Promise.all([
  mcp.invoke("fetch_api_data"),
  mcp.invoke("fetch_db_data"),
  mcp.invoke("fetch_file_data")
]);

// Step 2: Swarm coordination for analysis
await swarm.init({ topology: "mesh", agents: 3 });
await swarm.orchestrate("aggregate_and_analyze");
```

---

### Example 3: Customer Support Router (Agent Router + Hierarchical)

**Use Case**: Intelligent customer support system routing queries to specialized agents

**Decision Rationale:**
- Need dynamic routing based on query type
- 10+ specialized agents (billing, technical, sales, etc.)
- Escalation paths for complex queries
- Learning from resolution patterns

**Architecture Choice**: Agent Router (LangGraph) + Hierarchical Swarm (claude-flow)

**Implementation:**
```python
# Router for initial classification
router = LangGraph.create_router({
  "technical": technical_swarm,
  "billing": billing_swarm,
  "sales": sales_swarm,
  "complex": escalation_swarm
})

# Each swarm is hierarchical with coordinator
technical_swarm = claudeflow.swarm_init({
  topology: "hierarchical",
  coordinator: "technical-lead",
  agents: ["network-expert", "security-expert", "database-expert"]
})
```

**Key Pattern**: Router handles initial dispatch, swarms handle complex collaboration within domains.

---

## Summary

This decision framework emphasizes **pragmatic selection** over dogmatic adherence to any single pattern. The best architecture is the one that:

1. **Meets your current requirements** without over-engineering
2. **Scales with your growth** without complete rewrites
3. **Matches your team's expertise** for maintainability
4. **Balances complexity vs. capability** appropriately

Start simple. Add complexity only when requirements demand it. Use this framework as a guide, not a rulebook.

For detailed implementation guidance, refer to:
- `01-LANGGRAPH.md` - Sequential and parallel workflows
- `02-MCP.md` - Tool-based parallelization
- `03-CLAUDE-FLOW.md` - Swarm coordination and neural features
- `04-INTEGRATION.md` - Hybrid patterns and migrations
- `05-PRODUCTION.md` - Deployment and monitoring

---

**Document Version**: 1.0
**Last Updated**: 2025-11-28
**Part of**: MOAI-ADK Analysis Series
