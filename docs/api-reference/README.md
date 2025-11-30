# API Reference

Complete API documentation for MoAI Flow.

## Core API

- [Core Components](core.md) - Base classes and types
  - AgentNode
  - Edge
  - NodeState
  - EdgeType

## Topology API

- [Network Topology](topology.md) - Network topology implementations
  - StarTopology
  - MeshTopology
  - RingTopology
  - TreeTopology
  - HybridTopology

## Coordination API

- [Coordination Mechanisms](coordination.md) - Coordination and consensus
  - SwarmCoordinator
  - WeightedVotingConsensus
  - ByzantineConsensus
  - RaftConsensus
  - GossipProtocol

## Memory API

- [Memory Systems](memory.md) - Distributed memory and CRDT
  - GCounterCRDT
  - PNCounterCRDT
  - GSetCRDT
  - ORSetCRDT
  - LWWRegisterCRDT

## Resource API

- [Resource Management](resource.md) - Resource allocation
  - ResourceManager
  - ResourcePool
  - ResourceAllocator

## Optimization API

- [Optimization](optimization.md) - Optimization algorithms
  - LoadBalancer
  - TaskScheduler
  - PathOptimizer

## Monitoring API

- [Monitoring](monitoring.md) - Health and metrics
  - HealthMonitor
  - MetricsCollector
  - SystemHealthReporter

## Hooks API

- [Lifecycle Hooks](hooks.md) - Event handling
  - HookManager
  - LifecycleHooks
  - EventDispatcher

## GitHub API

- [GitHub Integration](github.md) - Repository integration
  - GitHubRepoAgent
  - PullRequestCoordinator
  - IssueTracker

## Patterns API

- [Design Patterns](patterns.md) - Common patterns
  - SelfHealingPattern
  - RetryPattern
  - CircuitBreaker
  - BulkheadPattern

## Quick Reference

### Import Paths

```python
# Core
from moai_flow.core import AgentNode, Edge, NodeState

# Topology
from moai_flow.topology import StarTopology, MeshTopology

# Coordination
from moai_flow.coordination import SwarmCoordinator
from moai_flow.coordination.consensus import WeightedVotingConsensus

# Memory
from moai_flow.memory import GCounterCRDT, GSetCRDT

# Monitoring
from moai_flow.monitoring import HealthMonitor, SystemHealthReporter

# GitHub
from moai_flow.github import GitHubRepoAgent

# Patterns
from moai_flow.patterns import SelfHealingPattern
```

## See Also

- [User Guide](../user-guide/quickstart.md)
- [Developer Guide](../developer-guide/architecture.md)
- [Examples](../../examples/)
