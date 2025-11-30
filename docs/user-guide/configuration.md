# Configuration Guide

Learn how to configure MoAI Flow for your use case.

## Configuration Overview

MoAI Flow can be configured through:
1. Configuration files
2. Environment variables
3. Runtime parameters

## Configuration File

Create a `moai_flow.yaml` or `moai_flow.json` configuration file:

```yaml
# moai_flow.yaml
swarm:
  max_agents: 100
  heartbeat_interval: 5.0
  timeout: 30.0

consensus:
  type: "weighted_voting"
  quorum: 0.67
  timeout: 10.0

memory:
  type: "crdt"
  sync_interval: 1.0
  persistence: true

monitoring:
  enabled: true
  metrics_interval: 10.0
  health_check_interval: 5.0

github:
  enabled: false
  token: "${GITHUB_TOKEN}"
  organization: "your-org"
```

## Environment Variables

```bash
# Swarm configuration
export MOAI_FLOW_MAX_AGENTS=100
export MOAI_FLOW_HEARTBEAT_INTERVAL=5.0

# Consensus configuration
export MOAI_FLOW_CONSENSUS_TYPE=weighted_voting
export MOAI_FLOW_CONSENSUS_QUORUM=0.67

# GitHub integration
export MOAI_FLOW_GITHUB_ENABLED=true
export MOAI_FLOW_GITHUB_TOKEN=your_token_here
```

## Runtime Configuration

```python
from moai_flow import MoaiFlowConfig

config = MoaiFlowConfig(
    swarm={
        "max_agents": 100,
        "heartbeat_interval": 5.0
    },
    consensus={
        "type": "weighted_voting",
        "quorum": 0.67
    }
)
```

## Configuration Options

### Swarm Configuration

- `max_agents`: Maximum number of agents (default: 100)
- `heartbeat_interval`: Heartbeat check interval in seconds (default: 5.0)
- `timeout`: Agent timeout in seconds (default: 30.0)

### Consensus Configuration

- `type`: Consensus mechanism type (weighted_voting, byzantine, raft)
- `quorum`: Minimum agreement threshold (default: 0.67)
- `timeout`: Consensus timeout in seconds (default: 10.0)

### Memory Configuration

- `type`: Memory system type (crdt, distributed)
- `sync_interval`: Sync interval in seconds (default: 1.0)
- `persistence`: Enable persistence (default: true)

### Monitoring Configuration

- `enabled`: Enable monitoring (default: true)
- `metrics_interval`: Metrics collection interval (default: 10.0)
- `health_check_interval`: Health check interval (default: 5.0)

## Loading Configuration

```python
from moai_flow import load_config

# Load from file
config = load_config("moai_flow.yaml")

# Load from environment
config = load_config.from_env()

# Load with overrides
config = load_config("moai_flow.yaml", overrides={"swarm.max_agents": 200})
```

## Next Steps

- Review [Quick Start Guide](quickstart.md)
- Explore [Architecture](../developer-guide/architecture.md)
- Check [API Reference](../api-reference/README.md)
