# HeartbeatMonitor Implementation Guide

## Overview

HeartbeatMonitor provides active health monitoring with automatic failure detection for swarm agents in MoAI-Flow Phase 6A. It implements configurable heartbeat intervals, health state transitions, and automatic recovery detection.

## Architecture

```
┌─────────────────────────────────────────┐
│       HeartbeatMonitor                  │
├─────────────────────────────────────────┤
│  Background Monitoring Thread           │
│  • Checks all agents periodically       │
│  • Detects state transitions            │
│  • Triggers alerts                      │
│                                         │
│  Health State Management                │
│  • HEALTHY: Last heartbeat < interval   │
│  • DEGRADED: 1x - 2x interval (warning) │
│  • CRITICAL: 2x - 3x interval (alert)   │
│  • FAILED: > failure threshold          │
│                                         │
│  Heartbeat History                      │
│  • Records last 100 heartbeats/agent    │
│  • Supports time range queries          │
│  • Includes optional metadata           │
└─────────────────────────────────────────┘
```

## Health State Transitions

```
HEALTHY (heartbeat < interval)
   ↓ (no heartbeat for 1x interval)
DEGRADED (1x - 2x interval) [WARNING]
   ↓ (no heartbeat for 2x interval)
CRITICAL (2x - 3x interval) [ALERT]
   ↓ (no heartbeat for 3x interval)
FAILED (> failure threshold) [FAILURE]

RECOVERY PATH:
FAILED/CRITICAL/DEGRADED → (new heartbeat) → HEALTHY
```

## Quick Start

### Basic Usage

```python
from moai_flow.monitoring import HeartbeatMonitor, HealthState

# Initialize monitor
monitor = HeartbeatMonitor(
    interval_ms=5000,      # 5 second heartbeat interval
    failure_threshold=3    # 3 missed beats = 15s = failure
)

# Start monitoring an agent
monitor.start_monitoring("agent-001")

# Record heartbeats
monitor.record_heartbeat("agent-001")
monitor.record_heartbeat("agent-001", metadata={"cpu": 45.2})

# Check health
health = monitor.check_agent_health("agent-001")
if health == HealthState.FAILED:
    print("Agent has failed!")

# Get unhealthy agents
failed_agents = monitor.get_unhealthy_agents(HealthState.FAILED)
critical_agents = monitor.get_unhealthy_agents(HealthState.CRITICAL)
```

### Integration with SwarmCoordinator

```python
from moai_flow.core import SwarmCoordinator
from moai_flow.monitoring import HeartbeatMonitor, HealthState

# Initialize coordinator and monitor
coordinator = SwarmCoordinator(topology_type="mesh")
monitor = HeartbeatMonitor(interval_ms=5000, failure_threshold=3)

# Register agent in both
agent_id = "expert-backend-001"
coordinator.register_agent(agent_id, {"type": "expert-backend"})
monitor.start_monitoring(agent_id)

# Update heartbeat when agent sends messages
coordinator.send_message(agent_id, "agent-002", {"task": "process"})
monitor.record_heartbeat(agent_id)

# Periodic health check
health = monitor.check_agent_health(agent_id)
if health in [HealthState.CRITICAL, HealthState.FAILED]:
    coordinator.broadcast_message(
        "alfred",
        {"alert": f"Agent {agent_id} health: {health.value}"}
    )
```

### Alert Callbacks

```python
def on_agent_failed(agent_id: str, state: HealthState, details: dict):
    """Called when agent enters FAILED state."""
    print(f"CRITICAL: Agent {agent_id} has failed!")
    print(f"Last heartbeat: {details['last_heartbeat']}")
    print(f"Elapsed: {details['elapsed_seconds']}s")

    # Take action
    coordinator.unregister_agent(agent_id)
    restart_agent(agent_id)

def on_agent_degraded(agent_id: str, state: HealthState, details: dict):
    """Called when agent enters DEGRADED state."""
    print(f"WARNING: Agent {agent_id} showing signs of degradation")
    print(f"Previous state: {details['previous_state']}")

# Configure alerts
monitor.configure_alerts(
    on_degraded=True,
    on_critical=True,
    on_failed=True,
    degraded_callback=on_agent_degraded,
    failed_callback=on_agent_failed
)
```

### Custom Intervals per Agent

```python
# Different agents can have different heartbeat requirements

# Fast-paced agents (real-time processing)
monitor.start_monitoring(
    "realtime-agent-001",
    interval_ms=1000,      # 1 second
    failure_threshold=2    # 2 missed = 2s failure
)

# Batch processing agents (slower)
monitor.start_monitoring(
    "batch-agent-001",
    interval_ms=30000,     # 30 seconds
    failure_threshold=5    # 5 missed = 150s failure
)
```

### Heartbeat History Analysis

```python
from datetime import datetime, timedelta

# Get recent heartbeat history
agent_id = "agent-001"
history = monitor.get_heartbeat_history(agent_id)

print(f"Total heartbeats: {len(history)}")
for record in history[-5:]:  # Last 5
    timestamp = datetime.fromtimestamp(record["timestamp"])
    print(f"  {timestamp}: {record['metadata']}")

# Get heartbeats in time range
start = datetime.now() - timedelta(hours=1)
end = datetime.now()
recent_history = monitor.get_heartbeat_history(agent_id, (start, end))

# Calculate average heartbeat interval
if len(recent_history) > 1:
    intervals = []
    for i in range(1, len(recent_history)):
        interval = recent_history[i]["timestamp"] - recent_history[i-1]["timestamp"]
        intervals.append(interval)
    avg_interval = sum(intervals) / len(intervals)
    print(f"Average heartbeat interval: {avg_interval:.2f}s")
```

## Configuration Options

### HeartbeatMonitor Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `interval_ms` | int | 5000 | Default heartbeat interval (milliseconds) |
| `failure_threshold` | int | 3 | Missed heartbeats before failure |
| `history_size` | int | 100 | Max heartbeat records per agent |
| `check_interval_ms` | int | 1000 | Background check frequency |

### Health State Thresholds

| State | Threshold | Description |
|-------|-----------|-------------|
| HEALTHY | < 1x interval | Agent heartbeating normally |
| DEGRADED | 1x - 2x interval | Warning: delayed heartbeat |
| CRITICAL | 2x - 3x interval | Alert: severe delay |
| FAILED | > failure_threshold | Agent unresponsive |

## Best Practices

### 1. Choose Appropriate Intervals

```python
# Real-time agents (< 1s processing time)
monitor.start_monitoring("realtime-agent", interval_ms=1000)

# Standard agents (1-5s processing time)
monitor.start_monitoring("standard-agent", interval_ms=5000)

# Batch/long-running agents (> 10s processing time)
monitor.start_monitoring("batch-agent", interval_ms=30000)
```

### 2. Record Heartbeats at Key Points

```python
# Record heartbeat when agent:
# 1. Starts processing a task
monitor.record_heartbeat(agent_id, {"status": "task_started"})

# 2. Completes a task
monitor.record_heartbeat(agent_id, {"status": "task_completed"})

# 3. Sends a message
coordinator.send_message(agent_id, target, message)
monitor.record_heartbeat(agent_id, {"action": "message_sent"})

# 4. Makes a significant state change
agent_state_changed(agent_id, new_state)
monitor.record_heartbeat(agent_id, {"state": new_state})
```

### 3. Graceful Shutdown

```python
import atexit

# Register shutdown handler
atexit.register(monitor.shutdown)

# Or explicit shutdown
try:
    run_application()
finally:
    monitor.shutdown()
    coordinator.shutdown()
```

### 4. Monitoring Statistics

```python
# Get overall monitoring health
stats = monitor.get_monitoring_stats()

print(f"Total agents monitored: {stats['total_agents']}")
print(f"Health distribution:")
print(f"  Healthy: {stats['health_distribution']['healthy']}")
print(f"  Degraded: {stats['health_distribution']['degraded']}")
print(f"  Critical: {stats['health_distribution']['critical']}")
print(f"  Failed: {stats['health_distribution']['failed']}")
print(f"Total heartbeats recorded: {stats['total_heartbeats']}")
```

## Performance Characteristics

| Operation | Complexity | Thread-Safe | Notes |
|-----------|-----------|-------------|-------|
| `start_monitoring()` | O(1) | ✅ Yes | Fast, no blocking |
| `record_heartbeat()` | O(1) | ✅ Yes | Deque append, very fast |
| `check_agent_health()` | O(1) | ✅ Yes | Simple calculation |
| `get_unhealthy_agents()` | O(n) | ✅ Yes | n = monitored agents |
| `get_heartbeat_history()` | O(m) | ✅ Yes | m = history size |

**Background thread impact**: < 0.1% CPU overhead for 100 monitored agents

## Testing

Comprehensive test suite with 96% coverage:

```bash
# Run tests
pytest tests/moai_flow/monitoring/test_heartbeat_monitor.py -v

# Run with coverage
pytest tests/moai_flow/monitoring/test_heartbeat_monitor.py \
    --cov=moai_flow.monitoring.heartbeat_monitor \
    --cov-report=term-missing
```

## Common Patterns

### Pattern 1: Automatic Agent Recovery

```python
def on_agent_failed(agent_id: str, state: HealthState, details: dict):
    """Automatically restart failed agents."""
    logger.error(f"Agent {agent_id} failed, attempting restart...")

    # Stop monitoring failed agent
    monitor.stop_monitoring(agent_id)
    coordinator.unregister_agent(agent_id)

    # Restart agent
    new_agent = create_agent(agent_id)
    coordinator.register_agent(agent_id, new_agent.metadata)
    monitor.start_monitoring(agent_id)

    logger.info(f"Agent {agent_id} restarted successfully")

monitor.configure_alerts(
    on_failed=True,
    failed_callback=on_agent_failed
)
```

### Pattern 2: Health Dashboard

```python
def print_health_dashboard():
    """Display real-time health dashboard."""
    stats = monitor.get_monitoring_stats()

    print("\n" + "="*50)
    print("AGENT HEALTH DASHBOARD")
    print("="*50)

    for agent_id in coordinator.agent_registry.keys():
        try:
            health = monitor.check_agent_health(agent_id)
            icon = {
                HealthState.HEALTHY: "✅",
                HealthState.DEGRADED: "⚠️",
                HealthState.CRITICAL: "🔴",
                HealthState.FAILED: "❌"
            }[health]

            print(f"{icon} {agent_id}: {health.value.upper()}")
        except ValueError:
            print(f"❓ {agent_id}: NOT MONITORED")

    print("="*50)
    print(f"Total: {stats['total_agents']} agents")
    print(f"Healthy: {stats['health_distribution']['healthy']}")
    print(f"Issues: {stats['health_distribution']['degraded'] + stats['health_distribution']['critical']}")
    print(f"Failed: {stats['health_distribution']['failed']}")
    print("="*50 + "\n")

# Update dashboard every 5 seconds
import time
while True:
    print_health_dashboard()
    time.sleep(5)
```

### Pattern 3: Intelligent Alert Throttling

```python
class ThrottledAlerts:
    """Prevent alert spam by throttling repeated alerts."""

    def __init__(self, cooldown_seconds=60):
        self.last_alert_time = {}
        self.cooldown = cooldown_seconds

    def should_alert(self, agent_id: str, state: HealthState) -> bool:
        """Check if alert should be sent."""
        key = f"{agent_id}:{state.value}"
        current_time = time.time()

        if key not in self.last_alert_time:
            self.last_alert_time[key] = current_time
            return True

        elapsed = current_time - self.last_alert_time[key]
        if elapsed > self.cooldown:
            self.last_alert_time[key] = current_time
            return True

        return False

throttler = ThrottledAlerts(cooldown_seconds=300)  # 5 min cooldown

def on_critical_throttled(agent_id: str, state: HealthState, details: dict):
    """Alert only if not recently alerted."""
    if throttler.should_alert(agent_id, state):
        send_alert_email(agent_id, state, details)
    else:
        logger.debug(f"Skipping throttled alert for {agent_id}")

monitor.configure_alerts(
    on_critical=True,
    critical_callback=on_critical_throttled
)
```

## Troubleshooting

### Issue: Background thread not running

**Symptoms**: Health states not updating automatically

**Solution**:
```python
# Check thread status
stats = monitor.get_monitoring_stats()
if not stats["monitoring_thread_alive"]:
    logger.error("Background monitoring thread died!")
    monitor._start_background_monitoring()
```

### Issue: High memory usage with many agents

**Symptoms**: Memory grows with heartbeat history

**Solution**:
```python
# Reduce history size
monitor = HeartbeatMonitor(
    history_size=50,  # Reduce from default 100
    interval_ms=5000
)

# Or periodically clear history for inactive agents
for agent_id in list(monitor.heartbeat_history.keys()):
    if agent_id not in coordinator.agent_registry:
        del monitor.heartbeat_history[agent_id]
```

### Issue: False positives (agents marked failed incorrectly)

**Symptoms**: Healthy agents showing as DEGRADED/FAILED

**Solution**:
```python
# Increase interval or failure threshold
monitor.start_monitoring(
    agent_id,
    interval_ms=10000,      # Increase from 5000
    failure_threshold=5     # Increase from 3
)

# Or ensure heartbeats are recorded consistently
def process_task(agent_id):
    monitor.record_heartbeat(agent_id)  # Start
    result = do_work()
    monitor.record_heartbeat(agent_id)  # End
    return result
```

## API Reference

See `moai_flow/monitoring/heartbeat_monitor.py` for complete API documentation.

### Key Methods

- `start_monitoring(agent_id, interval_ms, failure_threshold)` - Begin monitoring agent
- `stop_monitoring(agent_id)` - Stop monitoring agent
- `record_heartbeat(agent_id, metadata)` - Record agent heartbeat
- `check_agent_health(agent_id)` - Get current health state
- `get_unhealthy_agents(min_state)` - Find unhealthy agents
- `get_heartbeat_history(agent_id, time_range)` - Get historical heartbeats
- `configure_alerts(on_degraded, on_critical, on_failed, callbacks)` - Configure alerting
- `get_monitoring_stats()` - Get monitoring statistics
- `shutdown()` - Gracefully shutdown monitoring

---

**Last Updated**: 2025-11-29
**Version**: 1.0.0
**Status**: Production Ready
**Test Coverage**: 96%
