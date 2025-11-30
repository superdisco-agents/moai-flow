# Troubleshooting Guide

Common issues and solutions for MoAI Flow.

## Installation Issues

### ImportError: No module named 'moai_flow'

**Solution:**
```bash
pip install moai-flow
# Or
pip install -e .
```

### Dependency Conflicts

**Solution:**
```bash
# Create a fresh virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install moai-flow
```

## Runtime Issues

### Agent Connection Timeouts

**Symptoms:**
- Agents fail to connect
- Heartbeat timeouts
- Connection refused errors

**Solutions:**

1. Check network connectivity:
```python
from moai_flow.monitoring import HealthMonitor
monitor = HealthMonitor()
status = await monitor.check_connectivity()
```

2. Increase timeout values:
```yaml
swarm:
  timeout: 60.0  # Increase from 30.0
  heartbeat_interval: 10.0  # Increase from 5.0
```

3. Check firewall settings

### Consensus Failures

**Symptoms:**
- Consensus never reaches agreement
- Timeout errors
- Split-brain scenarios

**Solutions:**

1. Check quorum settings:
```yaml
consensus:
  quorum: 0.51  # Reduce if needed (must be > 0.5)
```

2. Verify agent health:
```python
health_status = await swarm.check_all_agents()
```

3. Check for Byzantine agents:
```python
from moai_flow.coordination.consensus import ByzantineConsensus
consensus = ByzantineConsensus(max_byzantine=1)
```

### Memory Sync Issues

**Symptoms:**
- CRDT states diverge
- Merge conflicts
- Lost updates

**Solutions:**

1. Increase sync interval:
```yaml
memory:
  sync_interval: 0.5  # More frequent syncs
```

2. Enable persistence:
```yaml
memory:
  persistence: true
```

3. Check merge logic:
```python
counter = GCounterCRDT(node_id="node1")
counter.merge(other_counter)
assert counter.value() == expected_value
```

## Performance Issues

### High Memory Usage

**Solutions:**

1. Limit agent count:
```yaml
swarm:
  max_agents: 50
```

2. Enable cleanup:
```python
await swarm.cleanup_inactive_agents()
```

3. Use memory profiling:
```bash
pip install memory-profiler
python -m memory_profiler your_script.py
```

### Slow Consensus

**Solutions:**

1. Optimize consensus type:
```python
# Use weighted voting for faster consensus
consensus = WeightedVotingConsensus(...)
```

2. Reduce timeout:
```yaml
consensus:
  timeout: 5.0
```

3. Check network latency

## Debugging

### Enable Debug Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check System Health

```python
from moai_flow.monitoring import SystemHealthReporter

reporter = SystemHealthReporter()
health_report = await reporter.generate_report()
print(health_report)
```

### Inspect Agent State

```python
# Check agent status
agent_state = agent.get_state()
print(f"Status: {agent_state.status}")
print(f"Health: {agent_state.health}")
print(f"Last heartbeat: {agent_state.last_heartbeat}")
```

## Common Error Messages

### "Quorum not reached"

**Cause:** Not enough agents agreed on the proposal.

**Solution:** Reduce quorum threshold or ensure all agents are healthy.

### "Agent not responding"

**Cause:** Agent failed or network issue.

**Solution:** Check agent health and network connectivity.

### "CRDT merge conflict"

**Cause:** Incompatible CRDT states.

**Solution:** Ensure all nodes use the same CRDT type and version.

## Getting Help

If you're still experiencing issues:

1. Check [GitHub Issues](https://github.com/your-org/moai-flow/issues)
2. Review [API Documentation](../api-reference/README.md)
3. Open a [New Issue](https://github.com/your-org/moai-flow/issues/new)

Include:
- MoAI Flow version
- Python version
- Error messages and stack traces
- Minimal reproducible example
