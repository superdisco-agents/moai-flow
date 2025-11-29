# PRD-02: Swarm Coordination

> Multi-agent swarm infrastructure for MoAI

## Status

| Field | Value |
|-------|-------|
| **Current Status** | In Progress |
| **Phase** | Phase 3 - Core Infrastructure |
| **Progress** | 40% (Core interfaces and SwarmDB complete) |
| **Last Updated** | 2025-11-29 |

---

## Overview

| Field | Value |
|-------|-------|
| **Priority** | P1 (Critical) |
| **Effort** | High (2-3 months) |
| **Impact** | High |
| **Type** | Infrastructure |

---

## Implementation Progress

### Phase 3: Core Infrastructure ✅

- [x] IMemoryProvider interface designed
- [x] ICoordinator interface designed
- [x] IResourceController interface designed
- [x] SwarmDB SQLite wrapper implemented
- [x] TokenBudget allocator implemented
- [x] AgentLifecycle hooks implemented
- [x] Interface tests created (90%+ coverage)
- [x] SwarmDB tests created (90%+ coverage)
- [ ] Integration testing complete
- [ ] Performance benchmarks complete

### Phase 4: Memory System (Pending)

- [ ] ContextHints implementation
- [ ] SemanticMemory implementation
- [ ] EpisodicMemory implementation
- [ ] SessionStart/End integration

### Phase 5: Topology Implementation (Pending)

- [ ] Hierarchical topology
- [ ] Mesh topology
- [ ] Star topology
- [ ] Ring topology
- [ ] Adaptive topology
- [ ] SwarmCoordinator main engine

---

## Problem Statement

MoAI executes agents independently via Task() without coordination infrastructure. MoAI-Flow's swarm system enables sophisticated multi-agent coordination with topologies, consensus, and collective intelligence.

### Current MoAI State

```
CURRENT: Independent Agent Execution

User Request
    │
    ▼
┌─────────┐
│ Alfred  │
└────┬────┘
     │
     ├──► Task(agent-1) ──► Result
     ├──► Task(agent-2) ──► Result
     └──► Task(agent-3) ──► Result

No coordination between agents
No shared state
No collective decision-making
```

### Desired State

```
DESIRED: Coordinated Swarm Execution

User Request
    │
    ▼
┌─────────┐
│ Alfred  │
└────┬────┘
     │
     ▼
┌──────────────────────────────────┐
│         SWARM COORDINATOR        │
├──────────────────────────────────┤
│ • Topology: mesh                 │
│ • Consensus: enabled             │
│ • Shared Memory: active          │
└────────────┬─────────────────────┘
             │
     ┌───────┼───────┐
     │       │       │
     ▼       ▼       ▼
  Agent1 ◄─► Agent2 ◄─► Agent3
     │       │       │
     └───────┴───────┘
           │
           ▼
    Coordinated Result
```

---

## Solution Options

### Option A: Add MoAI-Flow (native)

**Approach**: Use MoAI-Flow's existing MCP server for coordination.

```json
{
  "mcpServers": {
    "moai-flow": {
      "command": "npx",
      "args": ["-y", "moai-flow@alpha", "mcp", "start"]
    }
  }
}
```

**Usage Pattern**:
```javascript
// Setup coordination
mcp__moai-flow__swarm_init { topology: "mesh", maxAgents: 6 }

// Agents coordinate through swarm
Task(subagent_type="expert-backend", prompt="Build API...")
Task(subagent_type="expert-frontend", prompt="Build UI...")

// Monitor coordination
mcp__moai-flow__swarm_status {}
```

**Pros**:
- Immediate availability
- Proven implementation
- Full feature set

**Cons**:
- External dependency
- Potential conflicts with MoAI patterns
- Less control

### Option B: Native MoAI Swarm

**Approach**: Build swarm coordination natively in MoAI.

```yaml
# New agents
swarm-coordinator:
  description: Manages swarm topology and coordination

swarm-consensus:
  description: Handles multi-agent consensus

swarm-memory:
  description: Manages shared swarm state
```

**Pros**:
- Full integration with MoAI
- No external dependencies
- Custom to MoAI needs

**Cons**:
- Significant development effort
- Longer timeline
- Need to build from scratch

### Option C: Hybrid Approach (Recommended)

**Approach**: Use MoAI-Flow (native) for coordination, MoAI agents for execution.

```
MoAI-Flow (native):  Coordination, topology, consensus
MoAI Task():      Agent execution
MoAI Hooks:       Integration points
```

**Pros**:
- Quick capability gain
- MoAI agents preserved
- Gradual native migration path

**Cons**:
- Two systems to manage
- Some complexity

---

## Recommended Solution: Option C (Hybrid)

### Phase 1: Add MoAI-Flow (native) (Month 1)

**Task 1.1**: MCP Configuration

```json
{
  "mcpServers": {
    "moai-flow": {
      "command": "npx",
      "args": ["-y", "moai-flow@alpha", "mcp", "start"]
    }
  }
}
```

**Task 1.2**: Permission Configuration

```json
{
  "permissions": {
    "allow": [
      "mcp__moai-flow__swarm_init",
      "mcp__moai-flow__agent_spawn",
      "mcp__moai-flow__swarm_status",
      "mcp__moai-flow__task_orchestrate"
    ]
  }
}
```

**Task 1.3**: Document Integration

Update CLAUDE.md with swarm usage patterns.

### Phase 2: Integration Hooks (Month 2)

**Task 2.1**: Add Coordination Hooks

```json
{
  "hooks": {
    "OnSwarmInit": { "command": ".moai/hooks/swarm-init.sh" },
    "OnAgentJoin": { "command": ".moai/hooks/agent-join.sh" },
    "OnConsensus": { "command": ".moai/hooks/consensus.sh" }
  }
}
```

**Task 2.2**: Create Swarm Manager Agent

```yaml
name: manager-swarm
description: MoAI swarm coordination manager

responsibilities:
  - Initialize swarm via MoAI-Flow (native)
  - Coordinate agent tasks
  - Monitor swarm health
  - Handle consensus events
```

### Phase 3: Evaluate Native (Month 3+)

**Task 3.1**: Evaluate MoAI-Flow (native) usage
- Track coordination patterns
- Identify MoAI-specific needs
- Assess native development effort

**Task 3.2**: Decision Point
- Continue with hybrid OR
- Build native swarm OR
- Full MoAI-Flow adoption

---

## Technical Specification

### Swarm Configuration

```json
{
  "swarm": {
    "enabled": true,
    "provider": "moai-flow",  // or "native" in future
    "default_topology": "mesh",
    "max_agents": 10,
    "consensus": {
      "enabled": true,
      "threshold": 0.66,
      "timeout_ms": 30000
    },
    "coordination": {
      "heartbeat_interval_ms": 5000,
      "failure_threshold": 3
    }
  }
}
```

### Usage Pattern in CLAUDE.md

```markdown
### Swarm Coordination Usage

For complex multi-agent tasks requiring coordination:

1. Initialize swarm:
   ```javascript
   mcp__moai-flow__swarm_init {
     topology: "mesh",
     maxAgents: 6
   }
   ```

2. Execute coordinated agents:
   ```python
   Task(subagent_type="expert-backend", prompt="...")
   Task(subagent_type="expert-frontend", prompt="...")
   ```

3. Monitor status:
   ```javascript
   mcp__moai-flow__swarm_status {}
   ```

Use swarm when:
- Multiple agents need to collaborate
- Consensus decisions required
- Shared state needed
- Complex multi-step workflows
```

---

## Phase 3 Architecture Decisions

### Interface Design

**IMemoryProvider**: Namespace-based memory with persistence support
- Enables agents to access shared memory with semantic namespace organization
- Supports both volatile and persistent memory layers
- Integrated with SwarmDB for durability

**ICoordinator**: Multi-topology agent coordination
- Abstracts topology management and agent communication
- Supports multiple topology patterns (hierarchical, mesh, star, ring, adaptive)
- Provides consensus and state synchronization mechanisms

**IResourceController**: Token budget and agent quota management
- Allocates token budgets across swarm members
- Tracks resource consumption in real-time
- Enforces quota limits and prevents resource exhaustion

### Implementation Details

**SwarmDB**: SQLite-based storage at `.swarm/memory.db`
- Provides durable memory persistence for swarm state
- Supports structured query access to agent memory
- Enables temporal queries for episodic memory

**TokenBudget**: Integrated with `.moai/config/config.json`
- Reads budget allocations from project configuration
- Tracks per-agent and per-swarm token consumption
- Provides allocation and rebalancing mechanisms

**AgentLifecycle**: Hooks into `.claude/hooks/moai/lib/`
- Manages agent initialization and teardown
- Handles graceful shutdown and state preservation
- Integrates with MoAI hook system for extensibility

### Test Coverage

- Interface tests: 90%+ coverage per TRUST 5 standards
- SwarmDB tests: 90%+ coverage including edge cases
- Integration tests: In progress
- Performance benchmarks: Pending

---

## Acceptance Criteria

### Phase 1
- [ ] MoAI-Flow (native) configured and functional
- [ ] Permissions properly set
- [ ] Basic swarm init/status working
- [ ] Documentation updated

### Phase 2
- [ ] Coordination hooks implemented
- [ ] manager-swarm agent created
- [ ] Integration tested with multi-agent workflow

### Phase 3
- [ ] Usage evaluation completed
- [ ] Native vs hybrid decision documented
- [ ] Roadmap updated based on findings

---

## Impact Assessment

### Capability Gain

| Capability | Before | After |
|------------|--------|-------|
| Multi-agent coordination | None | Full |
| Swarm topologies | None | 5 types |
| Consensus | None | Multiple algorithms |
| Shared state | None | Available |
| Health monitoring | None | Heartbeat-based |

### Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| MCP conflicts | Medium | Medium | Namespace isolation |
| Performance overhead | Low | Medium | Monitor, optimize |
| Learning curve | Medium | Low | Documentation |
| Dependency issues | Low | High | Pin version, fallback plan |

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Swarm init success rate | > 95% |
| Multi-agent workflow completion | > 90% |
| Performance overhead | < 10% |
| User adoption | 30% within 3 months |

---

## Related Documents

- [Swarm Topologies](../advanced/01-swarm-topologies.md)
- [Consensus Mechanisms](../agents/04-consensus-distributed.md)
- [MCP Setup](../mcp/04-mcp-setup.md)
- [PRD-00 Overview](PRD-00-overview.md)

---

## Timeline

```
Week 1-2:   MCP setup, basic testing
Week 3-4:   Permission config, documentation
Week 5-6:   Hook implementation
Week 7-8:   manager-swarm agent
Week 9-10:  Integration testing
Week 11-12: Evaluation, decision
```

Total: ~3 months for Phase 1-3
