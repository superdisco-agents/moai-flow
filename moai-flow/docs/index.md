# MoAI-Flow Documentation

> Comprehensive reverse-engineering of MoAI-Flow concepts for MoAI-ADK ecosystem integration

---

## Quick Navigation

| Directory | Files | Purpose |
|-----------|-------|---------|
| [Core](#core-concepts) | 3 | Fundamental execution rules and concurrent patterns |
| [Methodology](#methodology-framework) | 4 | SPARC workflow analysis and comparison |
| [Agents](#agents-reference) | 9 | 54-agent catalog and MoAI mapping |
| [MCP](#mcp-integration) | 5 | Model Context Protocol vs Claude distinction |
| [Hooks](#hooks-lifecycle) | 6 | Pre/Post/Session hook integration patterns |
| [Advanced](#advanced-features) | 6 | Neural, swarm, self-healing, and analytics |
| [Integration](#integration-platform) | 2 | GitHub and Flow Nexus platform integration |

**Total Documentation**: 35 files

---

## Core Concepts

Fundamental MoAI-Flow principles and execution patterns.

### Files

1. **[01-concurrent-execution.md](./core/01-concurrent-execution.md)**
   - MoAI-Flow's "Golden Rule": 1 MESSAGE = ALL RELATED OPERATIONS
   - Mandatory batching patterns for TodoWrite, Task, and Bash
   - 32.3% token reduction through concurrent batching
   - Compliance verification patterns

2. **[02-file-organization.md](./core/02-file-organization.md)**
   - Directory structure requirements for MoAI projects
   - File naming conventions and standards
   - Organization best practices for codebase structure
   - Comparison with MoAI-ADK file organization

3. **[03-code-style.md](./core/03-code-style.md)**
   - Coding standards and style guidelines
   - Documentation patterns and formatting
   - Code quality expectations
   - Integration with MoAI-ADK standards

### Key Concepts

- **Concurrent Execution**: Strict enforcement of operation batching in single messages
- **Golden Rule**: All related operations must run together, never sequentially when avoidable
- **Token Efficiency**: Structured patterns reducing token usage by ~32%

---

## Methodology Framework

SPARC development methodology and workflow analysis.

### Files

1. **[01-sparc-overview.md](./methodology/01-sparc-overview.md)**
   - SPARC methodology: Specification → Pseudocode → Architecture → Refinement → Completion
   - 5-phase development cycle overview
   - Phase objectives and success criteria
   - Comparison with MoAI's `/moai:1-plan`, `2-run`, `3-sync` commands

2. **[02-sparc-commands.md](./methodology/02-sparc-commands.md)**
   - Command execution patterns within SPARC phases
   - Task delegation and agent selection
   - Output validation and phase transitions
   - Error handling and recovery procedures

3. **[03-workflow-phases.md](./methodology/03-workflow-phases.md)**
   - Detailed breakdown of each SPARC phase
   - Phase-specific agent involvement
   - Deliverables and validation gates
   - Integration points with MoAI workflow

4. **[04-moai-comparison.md](./methodology/04-moai-comparison.md)**
   - Direct comparison: SPARC vs MoAI workflow
   - Alignment analysis and gap identification
   - Hybrid approach opportunities
   - Migration path considerations

### Key Concepts

- **SPARC**: Systematic development framework with 5 distinct phases
- **Phase Gates**: Validation checkpoints between phases
- **Methodology Alignment**: Compatibility with MoAI's SPEC and TDD approach

---

## Agents Reference

Comprehensive agent catalog and multi-agent orchestration.

### Files

1. **[01-agent-catalog.md](./agents/01-agent-catalog.md)**
   - Complete 54-agent catalog organized by category
   - Core Development (5), Swarm Coordination (5), Consensus (7)
   - Performance Optimization (5), GitHub (9), SPARC (6), Specialized (8)
   - Testing (2), Migration (2)

2. **[02-core-development.md](./agents/02-core-development.md)**
   - Core Development agents: Research, Implementation, Testing, Integration, Automation
   - Role definitions and responsibilities
   - Interaction patterns with other agent categories
   - Integration with MoAI's expert-* tier

3. **[03-swarm-coordination.md](./agents/03-swarm-coordination.md)**
   - Swarm Coordination agents: Orchestrator, Sync Manager, State Manager, Monitor, Adaptive Coordinator
   - Multi-agent coordination patterns
   - Communication protocols and state management
   - Swarm intelligence implementation

4. **[04-consensus-distributed.md](./agents/04-consensus-distributed.md)**
   - Consensus mechanisms: Byzantine Fault Tolerance, Raft, Gossip, Voting
   - Distributed decision-making patterns
   - Conflict resolution strategies
   - Fallback and recovery mechanisms

5. **[05-performance-optimization.md](./agents/05-performance-optimization.md)**
   - Performance monitoring and optimization agents
   - Bottleneck analysis and profiling
   - Resource allocation strategies
   - Metrics collection and reporting

6. **[06-github-repository.md](./agents/06-github-repository.md)**
   - GitHub integration agents (9 specialized agents)
   - Repository management and branching strategies
   - Pull request and code review workflows
   - Issue management and project coordination

7. **[07-sparc-methodology.md](./agents/07-sparc-methodology.md)**
   - SPARC phase execution agents (6 agents)
   - Specification analyst, Pseudocoder, Architect, Implementer, Tester, Delivery manager
   - Phase-specific responsibilities and outputs
   - Cross-phase coordination

8. **[08-specialized-development.md](./agents/08-specialized-development.md)**
   - Specialized development agents (8 agents)
   - Domain-specific expertise: Backend, Frontend, Database, DevOps, Security, Documentation, Debugging
   - Integration with MoAI's expert-* hierarchy
   - Role mapping and capability alignment

9. **[09-moai-mapping.md](./agents/09-moai-mapping.md)**
   - Direct mapping of MoAI-Flow agents to MoAI-ADK architecture
   - 54-agent → 56-agent alignment analysis
   - Gap identification and integration opportunities
   - Hybrid agent orchestration strategy

### Key Concepts

- **Agent Taxonomy**: 9 categories, 54 specialized agents
- **Swarm Intelligence**: Adaptive multi-agent orchestration
- **Expert Mapping**: Alignment with MoAI's 5-tier hierarchy
- **Specialization**: Domain-specific agent teams

---

## MCP Integration

Model Context Protocol and external tool integration.

### Files

1. **[01-claude-vs-mcp.md](./mcp/01-claude-vs-mcp.md)**
   - Distinction between Claude execution and MCP coordination
   - MCP's role as coordinator, Claude as executor
   - Tool categories and classification
   - Integration patterns and protocols

2. **[02-mcp-tool-categories.md](./mcp/02-mcp-tool-categories.md)**
   - Tool categorization framework
   - Information retrieval tools (documentation, APIs, research)
   - Development tools (IDE, Git, build systems)
   - Monitoring tools (metrics, logs, alerts)
   - Decision tools (analysis, planning, optimization)

3. **[03-flow-nexus-tools.md](./mcp/03-flow-nexus-tools.md)**
   - Flow Nexus platform-specific MCP tools
   - Integration with external development ecosystems
   - Tool availability and provisioning
   - Custom tool development patterns

4. **[04-mcp-setup.md](./mcp/04-mcp-setup.md)**
   - MCP configuration and initialization
   - Tool registration and discovery
   - Security and permission management
   - Troubleshooting and debugging MCP connections

5. **[05-moai-mcp-comparison.md](./mcp/05-moai-mcp-comparison.md)**
   - MoAI-Flow MCP integration vs MoAI-ADK approach
   - Available MCP servers in both systems
   - Integration depth and extensibility
   - Migration and compatibility considerations

### Key Concepts

- **MCP Coordinator**: MCP orchestrates external tools and data sources
- **Claude Executor**: Claude executes decisions and code
- **Tool Categories**: Information, development, monitoring, decision tools
- **Integration Depth**: Seamless ecosystem connectivity

---

## Hooks Lifecycle

Pre/Post/Session operation lifecycle management.

### Files

1. **[01-hook-overview.md](./hooks/01-hook-overview.md)**
   - Hook system architecture and purposes
   - Hook lifecycle: Pre-Operation, During-Operation, Post-Operation, Session hooks
   - Hook invocation patterns and event triggers
   - Error handling and hook failures

2. **[02-pre-operation.md](./hooks/02-pre-operation.md)**
   - Pre-operation hooks: validation, dependency checking, resource allocation
   - Pre-Bash, Pre-Task, Pre-Agent hooks
   - Validation rules and constraint checking
   - State preparation and setup procedures

3. **[03-post-operation.md](./hooks/03-post-operation.md)**
   - Post-operation hooks: result processing, state updates, reporting
   - Post-Bash, Post-Task, Post-Agent hooks
   - Output validation and transformation
   - Cleanup and resource deallocation

4. **[04-session-management.md](./hooks/04-session-management.md)**
   - Session lifecycle hooks: Start, Progress, End
   - Session state initialization and persistence
   - Progress tracking and metrics collection
   - Session completion and cleanup

5. **[05-coordination-protocol.md](./hooks/05-coordination-protocol.md)**
   - Hook coordination between multiple agents
   - Distributed hook execution patterns
   - State synchronization across agents
   - Conflict resolution and consensus

6. **[06-moai-hooks-comparison.md](./hooks/06-moai-hooks-comparison.md)**
   - MoAI-Flow hooks vs MoAI-ADK hook system
   - Missing "During-Operation" hooks in MoAI
   - Hook integration opportunities
   - Migration and hybrid approach

### Key Concepts

- **Hook Lifecycle**: Pre → During → Post → Session phases
- **Event-Driven**: Automatic trigger on operation boundaries
- **State Management**: Hook coordination and state persistence
- **Extensibility**: Custom hook registration and plugin system

---

## Advanced Features

Neural training, swarm topologies, and advanced analytics.

### Files

1. **[01-swarm-topologies.md](./advanced/01-swarm-topologies.md)**
   - Swarm topology patterns: Mesh, Hierarchical, Adaptive, Ring, Star
   - Topology selection criteria and trade-offs
   - Dynamic topology switching
   - Performance implications and optimization

2. **[02-neural-training.md](./advanced/02-neural-training.md)**
   - Neural network training for agent optimization
   - 27+ model architectures and configurations
   - Training data collection and preparation
   - Model evaluation and continuous improvement

3. **[03-cross-session-memory.md](./advanced/03-cross-session-memory.md)**
   - Persistent memory across sessions
   - Knowledge base and learning from history
   - Context continuity and resumption patterns
   - Memory management and garbage collection

4. **[04-self-healing.md](./advanced/04-self-healing.md)**
   - Automatic failure detection and recovery
   - Distributed healing protocols
   - Fault tolerance and redundancy
   - Self-diagnosis and repair mechanisms

5. **[05-performance-metrics.md](./advanced/05-performance-metrics.md)**
   - Comprehensive metrics collection framework
   - 84.8% SWE-Bench performance benchmarking
   - Real-time monitoring and alerting
   - Performance visualization and reporting

6. **[06-bottleneck-analysis.md](./advanced/06-bottleneck-analysis.md)**
   - Automatic bottleneck detection
   - Performance profiling and analysis
   - Resource utilization tracking
   - Optimization recommendations and implementation

### Key Concepts

- **Adaptive Swarms**: Dynamic topology selection and optimization
- **Neural Enhancement**: Machine learning for agent improvement
- **Persistent Learning**: Cross-session knowledge accumulation
- **Self-Healing**: Automatic fault tolerance and recovery
- **Performance Excellence**: 84.8% SWE-Bench benchmark

---

## Integration Platform

GitHub and Flow Nexus platform integration.

### Files

1. **[01-github-integration.md](./integration/01-github-integration.md)**
   - GitHub API integration patterns
   - Repository, branch, and pull request management
   - Issue tracking and automation
   - GitHub Actions and CI/CD pipeline integration
   - Swarm-based GitHub agent coordination

2. **[02-flow-nexus-platform.md](./integration/02-flow-nexus-platform.md)**
   - Flow Nexus platform overview and architecture
   - MCP server provisioning and management
   - Cross-project resource coordination
   - Team collaboration features
   - Platform integration with MoAI-ADK

### Key Concepts

- **GitHub Automation**: 9-agent swarm for repository management
- **Platform Integration**: Seamless Flow Nexus connectivity
- **Multi-Project**: Resource sharing and coordination
- **Team Collaboration**: Built-in team workflow support

---

## Component Mapping: MoAI-Flow → MoAI-ADK

| Feature | MoAI-Flow | MoAI-ADK | Gap | Priority |
|---------|-----------|----------|-----|----------|
| Concurrent Batching | Strict enforcement | Partial | Need enforcement rules | P1 |
| Swarm Coordination | Full (9 categories) | Partial (5-tier) | Different architecture | P1 |
| SPARC Methodology | Complete | Similar (/moai:*) | Nomenclature difference | P2 |
| MCP/Claude Separation | Explicit | Implicit | Clarify distinction | P2 |
| Hook System | Full lifecycle | Session hooks only | Add During hooks | P1 |
| Neural Training | 27+ models | Not implemented | New feature | P3 |
| Cross-Session Memory | Full support | Partial (.moai/memory/) | Expand system | P2 |
| Self-Healing | Full implementation | Not implemented | New feature | P3 |
| Performance Metrics | 84.8% benchmark | Basic logging | Advanced metrics | P2 |
| GitHub Integration | 9-agent swarm | 1 manager | Enhanced swarm | P2 |

---

## Implementation Roadmap

### Phase 1: Foundation (High Priority)

1. Enforce concurrent batching rules from [core/01-concurrent-execution.md](./core/01-concurrent-execution.md)
2. Implement During-Operation hooks from [hooks/04-session-management.md](./hooks/04-session-management.md)
3. Map agents using [agents/09-moai-mapping.md](./agents/09-moai-mapping.md)
4. Document swarm patterns from [agents/03-swarm-coordination.md](./agents/03-swarm-coordination.md)

### Phase 2: Enhancement (Medium Priority)

5. Integrate MCP best practices from [mcp/01-claude-vs-mcp.md](./mcp/01-claude-vs-mcp.md)
6. Expand performance metrics from [advanced/05-performance-metrics.md](./advanced/05-performance-metrics.md)
7. Implement GitHub swarm from [integration/01-github-integration.md](./integration/01-github-integration.md)
8. Build cross-session memory from [advanced/03-cross-session-memory.md](./advanced/03-cross-session-memory.md)

### Phase 3: Advanced (Future)

9. Neural training system from [advanced/02-neural-training.md](./advanced/02-neural-training.md)
10. Self-healing framework from [advanced/04-self-healing.md](./advanced/04-self-healing.md)
11. Swarm topology optimization from [advanced/01-swarm-topologies.md](./advanced/01-swarm-topologies.md)
12. Flow Nexus platform integration from [integration/02-flow-nexus-platform.md](./integration/02-flow-nexus-platform.md)

---

## Usage Guide

### For Project Developers

1. Start with [Core Concepts](#core-concepts) to understand MoAI-Flow principles
2. Review [Methodology Framework](#methodology-framework) for workflow patterns
3. Reference [Agents Reference](#agents-reference) for agent taxonomy
4. Check [Hooks Lifecycle](#hooks-lifecycle) for event-driven patterns

### For Architecture Review

1. Study [agents/09-moai-mapping.md](./agents/09-moai-mapping.md) for integration points
2. Analyze [Component Mapping](#component-mapping-moai-flow--moai-adk) for gaps
3. Review [Implementation Roadmap](#implementation-roadmap) for prioritization
4. Plan phased integration using priority levels

### For Feature Implementation

1. Identify target feature in roadmap
2. Read relevant documentation section
3. Check MoAI-ADK comparison documents (04-moai-comparison.md, 06-moai-hooks-comparison.md, etc.)
4. Follow implementation patterns from methodology files
5. Reference agent coordination from swarm-coordination.md

---

## Related Documentation

**Source Analysis**: `_config/MOAI-ADK/MOAI-FLOW.md`
**Target Integration**: `/CLAUDE.md` (MoAI Alfred Directive)
**Agent Repository**: `.claude/agents/moai/` (56 agents)
**Configuration**: `.moai/config/config.json`
**Implementation**: `.moai/specs/` (SPEC documents)

---

## Version Information

| Item | Value |
|------|-------|
| Documentation Created | 2025-11-29 |
| Last Updated | 2025-11-29 |
| MoAI-Flow Version | v2.0.0 |
| MoAI-ADK Version | 0.30.2 |
| Total Documentation Files | 35 |
| Analysis Scope | Comprehensive |
| Status | Current |
