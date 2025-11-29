# MoAI-Flow

> Native Multi-Agent Swarm Coordination for MoAI-ADK

MoAI-Flow is the native swarm coordination infrastructure for MoAI-ADK. It provides multi-agent orchestration, cross-session memory, network topologies, and resource control - all built natively without external dependencies.

---

## Quick Links

| Area | Description |
|------|-------------|
| [Documentation](docs/) | Complete technical documentation |
| [Specifications](specs/) | PRD documents for implementation |
| [Schemas](schemas/) | JSON configuration schemas |

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        MoAI-Flow                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │    Core     │  │  Topology   │  │   Memory    │            │
│  │ Coordinator │  │   Manager   │  │   System    │            │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘            │
│         │                │                │                    │
│         └────────────────┼────────────────┘                    │
│                          │                                     │
│  ┌─────────────┐  ┌──────┴──────┐  ┌─────────────┐            │
│  │ Coordination│  │   Swarm     │  │  Resource   │            │
│  │   Engine    │  │ Coordinator │  │  Control    │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    Hooks System                          │   │
│  │   PreTask  →  AgentLifecycle  →  PostTask               │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Module Structure

### Core (`core/`)

| Module | Description |
|--------|-------------|
| `swarm.py` | SwarmCoordinator - Main orchestration |
| `agent_registry.py` | Agent discovery and registration |
| `message_bus.py` | Inter-agent messaging |
| `interfaces.py` | IMemoryProvider, ICoordinator, IResourceController |

### Topology (`topology/`)

| Module | Description |
|--------|-------------|
| `base.py` | Abstract topology interface |
| `mesh.py` | Full mesh - all agents connected |
| `hierarchical.py` | Tree structure (Alfred as root) |
| `star.py` | Hub-and-spoke pattern |
| `ring.py` | Sequential chain |
| `adaptive.py` | Dynamic topology switching |

### Memory (`memory/`)

| Module | Description |
|--------|-------------|
| `swarm_db.py` | SQLite wrapper for `.swarm/memory.db` |
| `semantic_memory.py` | Long-term knowledge storage |
| `episodic_memory.py` | Event and decision history |
| `context_hints.py` | Session hints and preferences |

### Coordination (`coordination/`)

| Module | Description |
|--------|-------------|
| `consensus.py` | Voting and agreement mechanisms |
| `conflict_resolution.py` | Conflict handling strategies |
| `heartbeat.py` | Agent health monitoring |
| `task_allocation.py` | Task distribution algorithms |

### Resource (`resource/`)

| Module | Description |
|--------|-------------|
| `token_budget.py` | Per-swarm token allocation |
| `agent_quota.py` | Execution quotas per agent |
| `priority_queue.py` | Task priority management |

### Hooks (`hooks/`)

| Module | Description |
|--------|-------------|
| `pre_task.py` | Pre-task coordination hooks |
| `post_task.py` | Post-task aggregation hooks |
| `agent_lifecycle.py` | Agent spawn/complete events |

---

## Documentation Index

### Core Concepts (`docs/core/`)

- [01-concurrent-execution.md](docs/core/01-concurrent-execution.md) - Parallel task execution
- [02-file-organization.md](docs/core/02-file-organization.md) - Project structure
- [03-code-style.md](docs/core/03-code-style.md) - Coding standards

### Methodology (`docs/methodology/`)

- [01-sparc-overview.md](docs/methodology/01-sparc-overview.md) - SPARC methodology
- [02-sparc-commands.md](docs/methodology/02-sparc-commands.md) - Command patterns
- [03-workflow-phases.md](docs/methodology/03-workflow-phases.md) - Workflow phases
- [04-moai-comparison.md](docs/methodology/04-moai-comparison.md) - MoAI integration

### Agents (`docs/agents/`)

- [01-agent-catalog.md](docs/agents/01-agent-catalog.md) - Agent reference
- [02-core-development.md](docs/agents/02-core-development.md) - Core agents
- [03-swarm-coordination.md](docs/agents/03-swarm-coordination.md) - Swarm agents
- [04-consensus-distributed.md](docs/agents/04-consensus-distributed.md) - Consensus
- [05-performance-optimization.md](docs/agents/05-performance-optimization.md) - Performance
- [06-github-repository.md](docs/agents/06-github-repository.md) - GitHub agents
- [07-sparc-methodology.md](docs/agents/07-sparc-methodology.md) - SPARC agents
- [08-specialized-development.md](docs/agents/08-specialized-development.md) - Specialized
- [09-moai-mapping.md](docs/agents/09-moai-mapping.md) - MoAI agent mapping

### MCP Integration (`docs/mcp/`)

- [01-claude-vs-mcp.md](docs/mcp/01-claude-vs-mcp.md) - Native vs MCP
- [02-mcp-tool-categories.md](docs/mcp/02-mcp-tool-categories.md) - Tool categories
- [03-flow-nexus-tools.md](docs/mcp/03-flow-nexus-tools.md) - Platform tools
- [04-mcp-setup.md](docs/mcp/04-mcp-setup.md) - Setup guide
- [05-moai-mcp-comparison.md](docs/mcp/05-moai-mcp-comparison.md) - MoAI comparison

### Hooks (`docs/hooks/`)

- [01-hook-overview.md](docs/hooks/01-hook-overview.md) - Hook system overview
- [02-pre-operation.md](docs/hooks/02-pre-operation.md) - Pre-operation hooks
- [03-post-operation.md](docs/hooks/03-post-operation.md) - Post-operation hooks
- [04-session-management.md](docs/hooks/04-session-management.md) - Session hooks
- [05-coordination-protocol.md](docs/hooks/05-coordination-protocol.md) - Coordination
- [06-moai-hooks-comparison.md](docs/hooks/06-moai-hooks-comparison.md) - MoAI hooks

### Advanced Features (`docs/advanced/`)

- [01-swarm-topologies.md](docs/advanced/01-swarm-topologies.md) - Network topologies
- [02-neural-training.md](docs/advanced/02-neural-training.md) - Pattern learning
- [03-cross-session-memory.md](docs/advanced/03-cross-session-memory.md) - Memory system
- [04-self-healing.md](docs/advanced/04-self-healing.md) - Error recovery
- [05-performance-metrics.md](docs/advanced/05-performance-metrics.md) - Metrics
- [06-bottleneck-analysis.md](docs/advanced/06-bottleneck-analysis.md) - Optimization

### Integration (`docs/integration/`)

- [01-github-integration.md](docs/integration/01-github-integration.md) - GitHub
- [02-flow-nexus-platform.md](docs/integration/02-flow-nexus-platform.md) - Platform

---

## PRD Specifications

### Priority 1 (Ready for SPEC)

| PRD | Description | SPEC ID |
|-----|-------------|---------|
| [PRD-01](specs/PRD-01-concurrent-batching.md) | Concurrent Batching | SPEC-MOAI-FLOW-001 |
| [PRD-04](specs/PRD-04-mcp-distinction.md) | MCP/Task Distinction | SPEC-MOAI-FLOW-002 |
| [PRD-03](specs/PRD-03-hooks-enhancement.md) | Hooks Enhancement | SPEC-MOAI-FLOW-003 |
| [PRD-02](specs/PRD-02-swarm-coordination.md) | Swarm Coordination | SPEC-MOAI-FLOW-004 |

### Priority 2 (Important)

| PRD | Description | SPEC ID |
|-----|-------------|---------|
| [PRD-08](specs/PRD-08-performance-metrics.md) | Performance Metrics | SPEC-MOAI-FLOW-005 |
| [PRD-06](specs/PRD-06-github-enhancement.md) | GitHub Enhancement | SPEC-MOAI-FLOW-006 |
| [PRD-05](specs/PRD-05-neural-training.md) | Pattern Learning | SPEC-MOAI-FLOW-007 |

### Priority 3 (Future)

| PRD | Description |
|-----|-------------|
| [PRD-07](specs/PRD-07-consensus-mechanisms.md) | Consensus Mechanisms |
| [PRD-09](specs/PRD-09-advanced-features.md) | Advanced Features |

### Overview

| PRD | Description |
|-----|-------------|
| [PRD-00](specs/PRD-00-overview.md) | Roadmap and Overview |

---

## Existing Infrastructure

MoAI-Flow leverages existing MoAI-ADK infrastructure:

| Component | Location | Purpose |
|-----------|----------|---------|
| SQLite DB | `.swarm/memory.db` | Swarm state storage |
| Hook System | `.claude/hooks/moai/lib/` | Coordination hooks |
| Session Manager | `moai-adk/src/moai_adk/core/` | Session tracking |
| Token Budget | `moai-adk/src/moai_adk/core/` | Resource allocation |
| State Tracking | `.claude/hooks/moai/lib/state_tracking.py` | Singleton pattern |

---

## Implementation Timeline

| Phase | Duration | Deliverables |
|-------|----------|--------------|
| Phase 1 | 2 days | Directory + docs migration |
| Phase 2 | 1 day | CLAUDE.md Rules 11 & 12 |
| Phase 3 | 2 weeks | Core Python infrastructure |
| Phase 4 | 1 week | Cross-session memory |
| Phase 5 | 2 weeks | Topology & coordination |
| Phase 6 | 4+ weeks | Consensus, metrics |

**Total: 8-10 weeks**

---

## Quick Start

```python
# Future API (Phase 3+)
from moai_flow import SwarmCoordinator
from moai_flow.topology import HierarchicalTopology
from moai_flow.memory import ContextHints

# Initialize swarm with Alfred as root
swarm = SwarmCoordinator(
    topology=HierarchicalTopology(root="alfred"),
    memory_provider="sqlite"
)

# Spawn agents with coordination
async with swarm.session() as session:
    results = await session.spawn_parallel([
        ("expert-backend", "Implement API"),
        ("expert-frontend", "Create UI"),
        ("manager-tdd", "Validate tests")
    ])
```

---

## License

MIT License - Part of MoAI-ADK

---

*Last Updated: 2025-11-29*
