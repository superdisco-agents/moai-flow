"""
Comprehensive tests for HeartbeatMonitor.

Tests cover:
- Initialization and configuration
- Agent monitoring lifecycle (start/stop)
- Heartbeat recording and health state transitions
- Background monitoring thread functionality
- Alert callbacks and configuration
- Heartbeat history and trend analysis
- Error handling and edge cases

Following TDD RED-GREEN-REFACTOR cycle with 90%+ coverage target.
"""

import pytest
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any

from moai_flow.monitoring import HeartbeatMonitor, HealthState


# ==========================================
# Fixtures
# ==========================================


@pytest.fixture
def monitor():
    """Create HeartbeatMonitor instance for testing."""
    mon = HeartbeatMonitor(
        interval_ms=1000,  # 1 second for faster tests
        failure_threshold=3,
        history_size=100,
        check_interval_ms=100  # Check every 100ms for faster tests
    )
    yield mon
    # Cleanup
    mon.shutdown()


@pytest.fixture
def monitored_agent(monitor):
    """Create monitor with one agent already registered."""
    agent_id = "test-agent-001"
    monitor.start_monitoring(agent_id)
    yield monitor, agent_id
    # Cleanup handled by monitor fixture


# ==========================================
# Initialization Tests
# ==========================================


def test_monitor_initialization():
    """Test HeartbeatMonitor initialization with default values."""
    monitor = HeartbeatMonitor()

    assert monitor.default_interval_ms == 5000
    assert monitor.default_failure_threshold == 3
    assert monitor.history_size == 100
    assert monitor.check_interval_ms == 1000
    assert len(monitor.monitoring_agents) == 0
    assert monitor.monitoring_thread is not None
    assert monitor.monitoring_thread.is_alive()

    monitor.shutdown()


def test_monitor_initialization_custom_values():
    """Test HeartbeatMonitor initialization with custom values."""
    monitor = HeartbeatMonitor(
        interval_ms=10000,
        failure_threshold=5,
        history_size=50,
        check_interval_ms=500
    )

    assert monitor.default_interval_ms == 10000
    assert monitor.default_failure_threshold == 5
    assert monitor.history_size == 50
    assert monitor.check_interval_ms == 500

    monitor.shutdown()


def test_monitor_initialization_invalid_interval():
    """Test initialization fails with invalid interval."""
    with pytest.raises(ValueError, match="interval_ms must be >= 100"):
        HeartbeatMonitor(interval_ms=50)


def test_monitor_initialization_invalid_threshold():
    """Test initialization fails with invalid failure threshold."""
    with pytest.raises(ValueError, match="failure_threshold must be >= 1"):
        HeartbeatMonitor(failure_threshold=0)


def test_monitor_initialization_invalid_history_size():
    """Test initialization fails with invalid history size."""
    with pytest.raises(ValueError, match="history_size must be >= 1"):
        HeartbeatMonitor(history_size=0)


def test_monitor_initialization_invalid_check_interval():
    """Test initialization fails with invalid check interval."""
    with pytest.raises(ValueError, match="check_interval_ms must be >= 100"):
        HeartbeatMonitor(check_interval_ms=50)


# ==========================================
# Start/Stop Monitoring Tests
# ==========================================


def test_start_monitoring_success(monitor):
    """Test starting agent monitoring successfully."""
    agent_id = "agent-001"
    result = monitor.start_monitoring(agent_id)

    assert result is True
    assert agent_id in monitor.monitoring_agents
    assert monitor.monitoring_agents[agent_id]["interval_ms"] == 1000
    assert monitor.monitoring_agents[agent_id]["failure_threshold"] == 3
    assert monitor.monitoring_agents[agent_id]["last_heartbeat"] == 0
    assert monitor.monitoring_agents[agent_id]["last_state"] == HealthState.HEALTHY


def test_start_monitoring_custom_values(monitor):
    """Test starting monitoring with custom interval and threshold."""
    agent_id = "agent-002"
    result = monitor.start_monitoring(
        agent_id,
        interval_ms=5000,
        failure_threshold=10
    )

    assert result is True
    assert monitor.monitoring_agents[agent_id]["interval_ms"] == 5000
    assert monitor.monitoring_agents[agent_id]["failure_threshold"] == 10


def test_start_monitoring_already_monitored(monitor):
    """Test starting monitoring for already monitored agent returns False."""
    agent_id = "agent-003"
    monitor.start_monitoring(agent_id)

    result = monitor.start_monitoring(agent_id)
    assert result is False


def test_stop_monitoring_success(monitor):
    """Test stopping agent monitoring successfully."""
    agent_id = "agent-004"
    monitor.start_monitoring(agent_id)

    result = monitor.stop_monitoring(agent_id)
    assert result is True
    assert agent_id not in monitor.monitoring_agents


def test_stop_monitoring_not_monitored(monitor):
    """Test stopping monitoring for unmonitored agent returns False."""
    agent_id = "agent-005"
    result = monitor.stop_monitoring(agent_id)

    assert result is False


# ==========================================
# Heartbeat Recording Tests
# ==========================================


def test_record_heartbeat_success(monitored_agent):
    """Test recording heartbeat successfully."""
    monitor, agent_id = monitored_agent

    result = monitor.record_heartbeat(agent_id)

    assert result is True
    assert monitor.monitoring_agents[agent_id]["last_heartbeat"] > 0
    assert len(monitor.heartbeat_history[agent_id]) == 1


def test_record_heartbeat_with_metadata(monitored_agent):
    """Test recording heartbeat with metadata."""
    monitor, agent_id = monitored_agent

    metadata = {"cpu_usage": 45.2, "memory_mb": 512}
    result = monitor.record_heartbeat(agent_id, metadata=metadata)

    assert result is True
    assert len(monitor.heartbeat_history[agent_id]) == 1
    assert monitor.heartbeat_history[agent_id][0]["metadata"] == metadata


def test_record_heartbeat_not_monitored(monitor):
    """Test recording heartbeat for unmonitored agent returns False."""
    agent_id = "unmonitored-agent"
    result = monitor.record_heartbeat(agent_id)

    assert result is False


def test_record_heartbeat_history_limit(monitor):
    """Test heartbeat history respects max size limit."""
    agent_id = "agent-history-test"
    monitor.start_monitoring(agent_id)

    # Record more heartbeats than history_size (100)
    for i in range(150):
        monitor.record_heartbeat(agent_id, metadata={"sequence": i})
        time.sleep(0.001)  # Small delay to ensure different timestamps

    # Should keep only last 100
    assert len(monitor.heartbeat_history[agent_id]) == 100
    # Should have latest entries
    assert monitor.heartbeat_history[agent_id][-1]["metadata"]["sequence"] == 149


# ==========================================
# Health State Calculation Tests
# ==========================================


def test_check_agent_health_healthy(monitored_agent):
    """Test health check returns HEALTHY when heartbeat is recent."""
    monitor, agent_id = monitored_agent

    monitor.record_heartbeat(agent_id)
    health = monitor.check_agent_health(agent_id)

    assert health == HealthState.HEALTHY


def test_check_agent_health_degraded(monitor):
    """Test health check returns DEGRADED after 2x interval."""
    agent_id = "agent-degraded"
    monitor.start_monitoring(agent_id, interval_ms=1000)

    # Record heartbeat
    monitor.record_heartbeat(agent_id)

    # Wait for degraded state (> 1000ms but < 2000ms)
    time.sleep(1.2)

    health = monitor.check_agent_health(agent_id)
    assert health == HealthState.DEGRADED


def test_check_agent_health_critical(monitor):
    """Test health check returns CRITICAL after interval but before failure."""
    agent_id = "agent-critical"
    monitor.start_monitoring(agent_id, interval_ms=1000, failure_threshold=3)

    # Record heartbeat
    monitor.record_heartbeat(agent_id)

    # Wait for critical state (> 2000ms but < 3000ms)
    time.sleep(2.2)

    health = monitor.check_agent_health(agent_id)
    assert health == HealthState.CRITICAL


def test_check_agent_health_failed(monitor):
    """Test health check returns FAILED after threshold exceeded."""
    agent_id = "agent-failed"
    monitor.start_monitoring(agent_id, interval_ms=1000, failure_threshold=3)

    # Record heartbeat
    monitor.record_heartbeat(agent_id)

    # Wait for failed state (> 3000ms)
    time.sleep(3.2)

    health = monitor.check_agent_health(agent_id)
    assert health == HealthState.FAILED


def test_check_agent_health_not_monitored(monitor):
    """Test health check raises error for unmonitored agent."""
    agent_id = "unmonitored"

    with pytest.raises(ValueError, match="not being monitored"):
        monitor.check_agent_health(agent_id)


def test_check_agent_health_no_heartbeat_yet(monitored_agent):
    """Test health check returns HEALTHY when no heartbeat recorded yet."""
    monitor, agent_id = monitored_agent

    # No heartbeat recorded
    health = monitor.check_agent_health(agent_id)

    assert health == HealthState.HEALTHY


# ==========================================
# Get Unhealthy Agents Tests
# ==========================================


def test_get_unhealthy_agents_empty(monitor):
    """Test get_unhealthy_agents returns empty list when all healthy."""
    agent_id = "healthy-agent"
    monitor.start_monitoring(agent_id)
    monitor.record_heartbeat(agent_id)

    unhealthy = monitor.get_unhealthy_agents()
    assert unhealthy == []


def test_get_unhealthy_agents_degraded(monitor):
    """Test get_unhealthy_agents finds degraded agents."""
    healthy_id = "healthy-agent"
    degraded_id = "degraded-agent"

    monitor.start_monitoring(healthy_id, interval_ms=1000)
    monitor.start_monitoring(degraded_id, interval_ms=1000)

    # Record heartbeats
    monitor.record_heartbeat(healthy_id)
    monitor.record_heartbeat(degraded_id)

    # Keep healthy agent fresh
    time.sleep(1.2)  # Degraded state
    monitor.record_heartbeat(healthy_id)

    unhealthy = monitor.get_unhealthy_agents(HealthState.DEGRADED)
    assert degraded_id in unhealthy
    assert healthy_id not in unhealthy


def test_get_unhealthy_agents_critical_only(monitor):
    """Test get_unhealthy_agents with CRITICAL minimum state."""
    degraded_id = "degraded-agent"
    critical_id = "critical-agent"

    monitor.start_monitoring(degraded_id, interval_ms=1000)
    monitor.start_monitoring(critical_id, interval_ms=1000)

    monitor.record_heartbeat(degraded_id)
    monitor.record_heartbeat(critical_id)

    # Wait for states
    time.sleep(1.2)  # degraded_id becomes DEGRADED
    monitor.record_heartbeat(degraded_id)  # Keep degraded

    time.sleep(1.1)  # Total 2.3s for critical_id → CRITICAL

    unhealthy = monitor.get_unhealthy_agents(HealthState.CRITICAL)
    assert critical_id in unhealthy
    assert degraded_id not in unhealthy  # Only CRITICAL+, not DEGRADED


# ==========================================
# Heartbeat History Tests
# ==========================================


def test_get_heartbeat_history_all(monitored_agent):
    """Test getting all heartbeat history."""
    monitor, agent_id = monitored_agent

    # Record multiple heartbeats
    for i in range(5):
        monitor.record_heartbeat(agent_id, metadata={"sequence": i})
        time.sleep(0.01)

    history = monitor.get_heartbeat_history(agent_id)

    assert len(history) == 5
    assert history[0]["metadata"]["sequence"] == 0
    assert history[4]["metadata"]["sequence"] == 4


def test_get_heartbeat_history_time_range(monitored_agent):
    """Test getting heartbeat history within time range."""
    monitor, agent_id = monitored_agent

    # Record heartbeats with delays
    start_time = datetime.now()

    for i in range(5):
        monitor.record_heartbeat(agent_id, metadata={"sequence": i})
        time.sleep(0.1)

    end_time = datetime.now()

    # Get history for time range (should exclude some)
    range_start = start_time + timedelta(milliseconds=150)
    range_end = end_time

    history = monitor.get_heartbeat_history(agent_id, (range_start, range_end))

    # Should have fewer records than total (first ones outside range)
    assert len(history) < 5
    assert len(history) >= 2  # At least some in range


def test_get_heartbeat_history_empty(monitor):
    """Test getting history for agent with no history."""
    agent_id = "no-history-agent"
    history = monitor.get_heartbeat_history(agent_id)

    assert history == []


# ==========================================
# Alert Configuration Tests
# ==========================================


def test_configure_alerts_enable_disable(monitor):
    """Test enabling and disabling alerts."""
    monitor.configure_alerts(
        on_degraded=False,
        on_critical=True,
        on_failed=True
    )

    assert monitor.alert_enabled[HealthState.DEGRADED] is False
    assert monitor.alert_enabled[HealthState.CRITICAL] is True
    assert monitor.alert_enabled[HealthState.FAILED] is True


def test_configure_alerts_callbacks(monitor):
    """Test setting alert callbacks."""
    degraded_called = []
    critical_called = []
    failed_called = []

    def on_degraded(agent_id, state, details):
        degraded_called.append((agent_id, state, details))

    def on_critical(agent_id, state, details):
        critical_called.append((agent_id, state, details))

    def on_failed(agent_id, state, details):
        failed_called.append((agent_id, state, details))

    monitor.configure_alerts(
        degraded_callback=on_degraded,
        critical_callback=on_critical,
        failed_callback=on_failed
    )

    assert monitor.alert_callbacks[HealthState.DEGRADED] == on_degraded
    assert monitor.alert_callbacks[HealthState.CRITICAL] == on_critical
    assert monitor.alert_callbacks[HealthState.FAILED] == on_failed


def test_alert_callback_triggered(monitor):
    """Test alert callbacks are triggered on state transitions."""
    alerts_triggered = []

    def on_degraded(agent_id, state, details):
        alerts_triggered.append({
            "agent_id": agent_id,
            "state": state,
            "details": details
        })

    monitor.configure_alerts(
        on_degraded=True,
        degraded_callback=on_degraded
    )

    agent_id = "alert-test-agent"
    monitor.start_monitoring(agent_id, interval_ms=500)
    monitor.record_heartbeat(agent_id)

    # Wait for degraded state and background check
    time.sleep(0.7)  # > 500ms but < 1000ms = DEGRADED

    # Give background thread time to detect and trigger alert
    time.sleep(0.3)

    # Should have triggered degraded alert
    assert len(alerts_triggered) > 0
    assert alerts_triggered[0]["agent_id"] == agent_id
    assert alerts_triggered[0]["state"] == HealthState.DEGRADED


def test_alert_callback_not_triggered_when_disabled(monitor):
    """Test alert callbacks are not triggered when disabled."""
    alerts_triggered = []

    def on_degraded(agent_id, state, details):
        alerts_triggered.append(True)

    monitor.configure_alerts(
        on_degraded=False,  # Disabled
        degraded_callback=on_degraded
    )

    agent_id = "disabled-alert-agent"
    monitor.start_monitoring(agent_id, interval_ms=500)
    monitor.record_heartbeat(agent_id)

    # Wait for degraded state
    time.sleep(0.7)
    time.sleep(0.3)  # Background check time

    # Should NOT have triggered
    assert len(alerts_triggered) == 0


# ==========================================
# Background Monitoring Tests
# ==========================================


def test_background_monitoring_thread_starts(monitor):
    """Test background monitoring thread starts automatically."""
    assert monitor.monitoring_thread is not None
    assert monitor.monitoring_thread.is_alive()
    assert monitor.monitoring_thread.daemon is True


def test_background_monitoring_detects_state_change(monitor):
    """Test background thread detects health state changes."""
    state_changes = []

    def on_critical(agent_id, state, details):
        state_changes.append({
            "agent_id": agent_id,
            "from": details.get("previous_state"),
            "to": state.value
        })

    monitor.configure_alerts(
        on_critical=True,
        critical_callback=on_critical
    )

    agent_id = "state-change-agent"
    monitor.start_monitoring(agent_id, interval_ms=500, failure_threshold=3)
    monitor.record_heartbeat(agent_id)

    # Wait for critical state (> 1000ms)
    time.sleep(1.2)
    time.sleep(0.3)  # Background check

    # Should detect state change to CRITICAL
    assert len(state_changes) > 0
    assert state_changes[-1]["to"] == "critical"


def test_background_monitoring_detects_recovery(monitor):
    """Test background thread detects agent recovery."""
    agent_id = "recovery-agent"
    monitor.start_monitoring(agent_id, interval_ms=1000)
    monitor.record_heartbeat(agent_id)

    # Wait for degraded state (>1000ms but <2000ms)
    time.sleep(1.2)
    time.sleep(0.2)  # Background check

    # Verify degraded or critical (timing can vary)
    health = monitor.check_agent_health(agent_id)
    assert health in [HealthState.DEGRADED, HealthState.CRITICAL]

    # Record new heartbeat (recovery)
    monitor.record_heartbeat(agent_id)
    time.sleep(0.2)  # Background check

    # Should be healthy again
    health = monitor.check_agent_health(agent_id)
    assert health == HealthState.HEALTHY


# ==========================================
# Monitoring Statistics Tests
# ==========================================


def test_get_monitoring_stats_empty(monitor):
    """Test monitoring stats with no agents."""
    stats = monitor.get_monitoring_stats()

    assert stats["total_agents"] == 0
    assert stats["health_distribution"]["healthy"] == 0
    assert stats["total_heartbeats"] == 0
    assert stats["monitoring_thread_alive"] is True


def test_get_monitoring_stats_with_agents(monitor):
    """Test monitoring stats with multiple agents."""
    # Create agents in different states
    healthy_id = "healthy-agent"
    degraded_id = "degraded-agent"

    monitor.start_monitoring(healthy_id, interval_ms=1000)
    monitor.start_monitoring(degraded_id, interval_ms=500)

    monitor.record_heartbeat(healthy_id)
    monitor.record_heartbeat(degraded_id)

    # Make one degraded
    time.sleep(0.7)
    monitor.record_heartbeat(healthy_id)

    stats = monitor.get_monitoring_stats()

    assert stats["total_agents"] == 2
    assert stats["health_distribution"]["healthy"] >= 1
    assert stats["total_heartbeats"] >= 3


# ==========================================
# Shutdown Tests
# ==========================================


def test_shutdown_terminates_thread():
    """Test shutdown terminates monitoring thread."""
    monitor = HeartbeatMonitor()

    assert monitor.monitoring_thread.is_alive()

    monitor.shutdown()
    time.sleep(0.2)  # Give thread time to terminate

    assert not monitor.monitoring_thread.is_alive()


def test_shutdown_idempotent():
    """Test multiple shutdown calls are safe."""
    monitor = HeartbeatMonitor()

    monitor.shutdown()
    monitor.shutdown()  # Second call should not raise error

    # Thread should still be terminated
    assert not monitor.monitoring_thread.is_alive()


# ==========================================
# Edge Cases and Error Handling
# ==========================================


def test_concurrent_heartbeat_recording(monitor):
    """Test thread-safe concurrent heartbeat recording."""
    import threading

    agent_id = "concurrent-agent"
    monitor.start_monitoring(agent_id)

    def record_heartbeats():
        for _ in range(10):
            monitor.record_heartbeat(agent_id)
            time.sleep(0.01)

    threads = [
        threading.Thread(target=record_heartbeats)
        for _ in range(3)
    ]

    for t in threads:
        t.start()

    for t in threads:
        t.join()

    # Should have recorded all heartbeats safely
    history = monitor.get_heartbeat_history(agent_id)
    assert len(history) == 30


def test_alert_callback_exception_handling(monitor):
    """Test monitor continues if alert callback raises exception."""
    def broken_callback(agent_id, state, details):
        raise RuntimeError("Callback error!")

    monitor.configure_alerts(
        on_degraded=True,
        degraded_callback=broken_callback
    )

    agent_id = "exception-test"
    monitor.start_monitoring(agent_id, interval_ms=1000)
    monitor.record_heartbeat(agent_id)

    # Wait for degraded (callback will raise exception)
    time.sleep(1.2)
    time.sleep(0.2)  # Background check

    # Monitor should still work (timing can vary)
    health = monitor.check_agent_health(agent_id)
    assert health in [HealthState.DEGRADED, HealthState.CRITICAL]


def test_multiple_agents_independent_intervals(monitor):
    """Test multiple agents with different intervals work independently."""
    agent1 = "agent-fast"
    agent2 = "agent-slow"

    monitor.start_monitoring(agent1, interval_ms=500)
    monitor.start_monitoring(agent2, interval_ms=2000)

    monitor.record_heartbeat(agent1)
    monitor.record_heartbeat(agent2)

    time.sleep(0.7)  # agent1 should be degraded, agent2 still healthy

    health1 = monitor.check_agent_health(agent1)
    health2 = monitor.check_agent_health(agent2)

    assert health1 == HealthState.DEGRADED
    assert health2 == HealthState.HEALTHY
