# Quick Start Guide

Get started with MoAI Flow in minutes.

## Overview

MoAI Flow is a distributed agent coordination system that enables multiple agents to work together efficiently using advanced coordination mechanisms, consensus protocols, and distributed memory systems.

## Installation

```bash
# Install from PyPI
pip install moai-flow

# Or install from source
git clone https://github.com/your-org/moai-flow
cd moai-flow
pip install -e .
```

## Basic Usage

### 1. Create a Simple Swarm

```python
from moai_flow.core import AgentNode
from moai_flow.topology import StarTopology
from moai_flow.coordination import SwarmCoordinator

# Create agents
coordinator = AgentNode(node_id="coordinator", role="coordinator")
worker1 = AgentNode(node_id="worker1", role="worker")
worker2 = AgentNode(node_id="worker2", role="worker")

# Create topology
topology = StarTopology(hub=coordinator)
topology.add_spoke(worker1)
topology.add_spoke(worker2)

# Create swarm coordinator
swarm = SwarmCoordinator(topology)

# Execute coordinated task
result = await swarm.coordinate_task(task="process_data")
```

### 2. Use Consensus Mechanisms

```python
from moai_flow.coordination.consensus import WeightedVotingConsensus

# Create consensus mechanism
consensus = WeightedVotingConsensus(
    agents=[coordinator, worker1, worker2],
    weights={"coordinator": 2.0, "worker1": 1.0, "worker2": 1.0}
)

# Reach consensus on a decision
decision = await consensus.decide(proposal="upgrade_system")
```

### 3. Use Distributed Memory

```python
from moai_flow.memory import GCounterCRDT

# Create CRDT counter
counter = GCounterCRDT(node_id="node1")

# Increment counter
counter.increment(5)

# Merge with another counter
other_counter = GCounterCRDT(node_id="node2")
counter.merge(other_counter)

# Get value
total = counter.value()
```

## Next Steps

- Read the [Architecture Guide](../developer-guide/architecture.md)
- Explore [Examples](../../examples/)
- Check [API Reference](../api-reference/README.md)
- Learn about [Consensus Mechanisms](../concepts/consensus-mechanisms.md)

## Common Patterns

### Health Monitoring

```python
from moai_flow.monitoring import HealthMonitor

# Create health monitor
monitor = HealthMonitor()

# Monitor agent health
health_status = await monitor.check_health(agent)
```

### Self-Healing

```python
from moai_flow.patterns import SelfHealingPattern

# Create self-healing system
healing = SelfHealingPattern(topology)

# Detect and recover from failures
await healing.detect_and_heal()
```

## Support

- Check [Troubleshooting Guide](troubleshooting.md)
- Review [Configuration Guide](configuration.md)
- Open an [Issue](https://github.com/your-org/moai-flow/issues)
