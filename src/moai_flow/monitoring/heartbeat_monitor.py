#!/usr/bin/env python3
"""
HeartbeatMonitor for MoAI-Flow Phase 6A

Active health monitoring with automatic failure detection for swarm agents.
Provides configurable heartbeat intervals, health state transitions, and
automatic recovery detection.

Key Features:
- Configurable heartbeat intervals (default: 5000ms)
- Automatic failure threshold (default: 3 missed beats = 15s)
- Health state transitions: HEALTHY → DEGRADED → CRITICAL → FAILED
- Recovery detection with automatic state restoration
- Heartbeat history for trend analysis
- Thread-safe operations with background monitoring
- Alert callbacks for health state changes

Example:
    >>> monitor = HeartbeatMonitor(interval_ms=5000, failure_threshold=3)
    >>> monitor.start_monitoring("agent-001")
    >>> monitor.record_heartbeat("agent-001")
    >>> health = monitor.check_agent_health("agent-001")
    >>> print(health)
    HealthState.HEALTHY
"""

from typing import Any, Dict, List, Optional, Callable, Tuple
from datetime import datetime, timedelta
from enum import Enum
import time
import threading
import logging
from collections import deque

logger = logging.getLogger(__name__)


class HealthState(Enum):
    """Agent health states based on heartbeat timing."""
    HEALTHY = "healthy"      # Last heartbeat < interval
    DEGRADED = "degraded"    # Last heartbeat < 2x interval (warning)
    CRITICAL = "critical"    # Last heartbeat < 3x interval (alert)
    FAILED = "failed"        # Missed threshold exceeded


class HeartbeatMonitor:
    """
    Monitor agent health through heartbeat tracking.

    Provides active health monitoring with configurable intervals,
    automatic failure detection, and health state transitions.
    Supports alert callbacks and historical trend analysis.

    Attributes:
        default_interval_ms: Default heartbeat interval (milliseconds)
        default_failure_threshold: Default missed heartbeats before failure
        monitoring_agents: Dict of currently monitored agents
        heartbeat_history: Dict of historical heartbeats per agent
        alert_callbacks: Dict of alert handler callbacks
        monitoring_thread: Background monitoring daemon thread
        shutdown_event: Threading event for graceful shutdown
    """

    def __init__(
        self,
        interval_ms: int = 5000,
        failure_threshold: int = 3,
        history_size: int = 100,
        check_interval_ms: int = 1000
    ):
        """
        Initialize HeartbeatMonitor.

        Args:
            interval_ms: Default heartbeat interval in milliseconds (default: 5000)
            failure_threshold: Number of missed heartbeats before failure (default: 3)
            history_size: Max heartbeat records to keep per agent (default: 100)
            check_interval_ms: How often to check all agents (default: 1000ms)

        Raises:
            ValueError: If interval_ms < 100, failure_threshold < 1, history_size < 1
        """
        if interval_ms < 100:
            raise ValueError("interval_ms must be >= 100")
        if failure_threshold < 1:
            raise ValueError("failure_threshold must be >= 1")
        if history_size < 1:
            raise ValueError("history_size must be >= 1")
        if check_interval_ms < 100:
            raise ValueError("check_interval_ms must be >= 100")

        self.default_interval_ms = interval_ms
        self.default_failure_threshold = failure_threshold
        self.history_size = history_size
        self.check_interval_ms = check_interval_ms

        # Agent monitoring data
        # Format: {agent_id: {interval_ms, failure_threshold, last_heartbeat, last_state}}
        self.monitoring_agents: Dict[str, Dict[str, Any]] = {}

        # Heartbeat history
        # Format: {agent_id: deque([(timestamp, metadata), ...])}
        self.heartbeat_history: Dict[str, deque] = {}

        # Alert configuration
        self.alert_callbacks: Dict[HealthState, Optional[Callable]] = {
            HealthState.DEGRADED: None,
            HealthState.CRITICAL: None,
            HealthState.FAILED: None
        }
        self.alert_enabled: Dict[HealthState, bool] = {
            HealthState.DEGRADED: True,
            HealthState.CRITICAL: True,
            HealthState.FAILED: True
        }

        # Background monitoring
        self.shutdown_event = threading.Event()
        self.monitoring_thread: Optional[threading.Thread] = None
        self._thread_lock = threading.RLock()

        # Start background monitoring thread
        self._start_background_monitoring()

        logger.info(
            f"HeartbeatMonitor initialized "
            f"(interval={interval_ms}ms, threshold={failure_threshold}, "
            f"history={history_size})"
        )

    def _start_background_monitoring(self):
        """Start background daemon thread for continuous agent health checks."""
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            logger.warning("Background monitoring already running")
            return

        self.shutdown_event.clear()
        self.monitoring_thread = threading.Thread(
            target=self._check_all_agents_loop,
            daemon=True,
            name="HeartbeatMonitor-Daemon"
        )
        self.monitoring_thread.start()
        logger.info("Background monitoring thread started")

    def _check_all_agents_loop(self):
        """Background loop that periodically checks all monitored agents."""
        while not self.shutdown_event.is_set():
            try:
                self._check_all_agents()
            except Exception as e:
                logger.error(f"Error in background monitoring loop: {e}")

            # Sleep with interruptible wait
            self.shutdown_event.wait(timeout=self.check_interval_ms / 1000.0)

    def _check_all_agents(self):
        """Check health state of all monitored agents and trigger alerts."""
        with self._thread_lock:
            current_time = time.time()

            for agent_id in list(self.monitoring_agents.keys()):
                agent_data = self.monitoring_agents[agent_id]
                last_heartbeat_time = agent_data.get("last_heartbeat", 0)

                # Calculate current health state
                new_state = self._calculate_health_state(
                    agent_id,
                    last_heartbeat_time,
                    current_time
                )

                # Check for state transition
                last_state = agent_data.get("last_state", HealthState.HEALTHY)

                if new_state != last_state:
                    # State changed - trigger alert if configured
                    agent_data["last_state"] = new_state

                    if new_state in [HealthState.DEGRADED, HealthState.CRITICAL, HealthState.FAILED]:
                        self._trigger_alert(
                            agent_id,
                            new_state,
                            {
                                "previous_state": last_state.value,
                                "current_state": new_state.value,
                                "last_heartbeat": datetime.fromtimestamp(
                                    last_heartbeat_time
                                ).isoformat() if last_heartbeat_time > 0 else None,
                                "elapsed_seconds": round(current_time - last_heartbeat_time, 2)
                            }
                        )

                    # Log recovery if transitioning from FAILED/CRITICAL to better state
                    if last_state in [HealthState.FAILED, HealthState.CRITICAL]:
                        if new_state in [HealthState.HEALTHY, HealthState.DEGRADED]:
                            logger.info(
                                f"Agent {agent_id} recovered: {last_state.value} → {new_state.value}"
                            )

    def _calculate_health_state(
        self,
        agent_id: str,
        last_heartbeat_time: float,
        current_time: Optional[float] = None
    ) -> HealthState:
        """
        Calculate health state based on heartbeat timing.

        Args:
            agent_id: Agent identifier
            last_heartbeat_time: Timestamp of last heartbeat (Unix timestamp)
            current_time: Current time (Unix timestamp), uses time.time() if None

        Returns:
            HealthState based on elapsed time since last heartbeat
        """
        if agent_id not in self.monitoring_agents:
            return HealthState.FAILED

        if current_time is None:
            current_time = time.time()

        agent_data = self.monitoring_agents[agent_id]
        interval_ms = agent_data["interval_ms"]
        failure_threshold = agent_data["failure_threshold"]

        if last_heartbeat_time == 0:
            # No heartbeat recorded yet
            return HealthState.HEALTHY

        elapsed_ms = (current_time - last_heartbeat_time) * 1000

        # State thresholds
        healthy_threshold = interval_ms
        degraded_threshold = interval_ms * 2
        critical_threshold = interval_ms * failure_threshold

        if elapsed_ms < healthy_threshold:
            return HealthState.HEALTHY
        elif elapsed_ms < degraded_threshold:
            return HealthState.DEGRADED
        elif elapsed_ms < critical_threshold:
            return HealthState.CRITICAL
        else:
            return HealthState.FAILED

    def _trigger_alert(
        self,
        agent_id: str,
        health_state: HealthState,
        details: Dict[str, Any]
    ):
        """
        Trigger alert callback for health state change.

        Args:
            agent_id: Agent identifier
            health_state: Current health state
            details: Additional alert details (previous_state, elapsed_seconds, etc.)
        """
        if not self.alert_enabled.get(health_state, False):
            return

        callback = self.alert_callbacks.get(health_state)

        if callback and callable(callback):
            try:
                callback(agent_id, health_state, details)
            except Exception as e:
                logger.error(f"Alert callback failed for {agent_id}: {e}")
        else:
            # Default alert logging
            logger.warning(
                f"Agent {agent_id} health: {details.get('previous_state')} → "
                f"{health_state.value} (elapsed: {details.get('elapsed_seconds', 0)}s)"
            )

    def start_monitoring(
        self,
        agent_id: str,
        interval_ms: Optional[int] = None,
        failure_threshold: Optional[int] = None
    ) -> bool:
        """
        Start monitoring agent heartbeats.

        Args:
            agent_id: Unique agent identifier
            interval_ms: Heartbeat interval override (uses default if None)
            failure_threshold: Failure threshold override (uses default if None)

        Returns:
            True if monitoring started, False if already monitored

        Example:
            >>> monitor.start_monitoring("agent-001", interval_ms=10000)
            True
            >>> monitor.start_monitoring("agent-001")  # Already monitored
            False
        """
        with self._thread_lock:
            if agent_id in self.monitoring_agents:
                logger.warning(f"Agent {agent_id} already being monitored")
                return False

            actual_interval = interval_ms if interval_ms is not None else self.default_interval_ms
            actual_threshold = (
                failure_threshold if failure_threshold is not None
                else self.default_failure_threshold
            )

            self.monitoring_agents[agent_id] = {
                "interval_ms": actual_interval,
                "failure_threshold": actual_threshold,
                "last_heartbeat": 0,  # No heartbeat yet
                "last_state": HealthState.HEALTHY,
                "started_at": time.time()
            }

            self.heartbeat_history[agent_id] = deque(maxlen=self.history_size)

            logger.info(
                f"Started monitoring {agent_id} "
                f"(interval={actual_interval}ms, threshold={actual_threshold})"
            )

            return True

    def stop_monitoring(self, agent_id: str) -> bool:
        """
        Stop monitoring agent heartbeats.

        Args:
            agent_id: Unique agent identifier

        Returns:
            True if monitoring stopped, False if agent not monitored

        Example:
            >>> monitor.stop_monitoring("agent-001")
            True
        """
        with self._thread_lock:
            if agent_id not in self.monitoring_agents:
                logger.warning(f"Agent {agent_id} not being monitored")
                return False

            del self.monitoring_agents[agent_id]

            # Keep history for analysis even after stopping
            # History will be cleared only on explicit request

            logger.info(f"Stopped monitoring {agent_id}")
            return True

    def record_heartbeat(
        self,
        agent_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Record agent heartbeat.

        Args:
            agent_id: Unique agent identifier
            metadata: Optional metadata to attach to heartbeat

        Returns:
            True if recorded successfully, False if agent not monitored

        Example:
            >>> monitor.record_heartbeat(
            ...     "agent-001",
            ...     {"cpu_usage": 45.2, "memory_mb": 512}
            ... )
            True
        """
        with self._thread_lock:
            if agent_id not in self.monitoring_agents:
                logger.warning(f"Agent {agent_id} not being monitored")
                return False

            current_time = time.time()

            # Update last heartbeat
            self.monitoring_agents[agent_id]["last_heartbeat"] = current_time

            # Add to history
            heartbeat_record = {
                "timestamp": current_time,
                "metadata": metadata or {}
            }

            self.heartbeat_history[agent_id].append(heartbeat_record)

            # Check if this recovers agent from failed state
            last_state = self.monitoring_agents[agent_id].get("last_state", HealthState.HEALTHY)
            current_state = self._calculate_health_state(agent_id, current_time)

            if current_state == HealthState.HEALTHY and last_state != HealthState.HEALTHY:
                # Recovery detected
                self.monitoring_agents[agent_id]["last_state"] = HealthState.HEALTHY
                logger.info(f"Agent {agent_id} recovered to HEALTHY state")

            return True

    def check_agent_health(self, agent_id: str) -> HealthState:
        """
        Get current health state of agent.

        Args:
            agent_id: Unique agent identifier

        Returns:
            Current HealthState

        Raises:
            ValueError: If agent not being monitored

        Example:
            >>> health = monitor.check_agent_health("agent-001")
            >>> if health == HealthState.FAILED:
            ...     print("Agent has failed!")
        """
        with self._thread_lock:
            if agent_id not in self.monitoring_agents:
                raise ValueError(f"Agent {agent_id} not being monitored")

            agent_data = self.monitoring_agents[agent_id]
            last_heartbeat_time = agent_data.get("last_heartbeat", 0)

            return self._calculate_health_state(agent_id, last_heartbeat_time)

    def get_unhealthy_agents(
        self,
        min_state: HealthState = HealthState.DEGRADED
    ) -> List[str]:
        """
        Get list of agents at or worse than specified health state.

        Args:
            min_state: Minimum health state to include (default: DEGRADED)

        Returns:
            List of agent IDs matching criteria

        Example:
            >>> failed_agents = monitor.get_unhealthy_agents(HealthState.FAILED)
            >>> critical_plus = monitor.get_unhealthy_agents(HealthState.CRITICAL)
        """
        state_order = {
            HealthState.HEALTHY: 0,
            HealthState.DEGRADED: 1,
            HealthState.CRITICAL: 2,
            HealthState.FAILED: 3
        }

        min_severity = state_order[min_state]
        unhealthy = []

        with self._thread_lock:
            for agent_id in self.monitoring_agents.keys():
                current_state = self.check_agent_health(agent_id)
                if state_order[current_state] >= min_severity:
                    unhealthy.append(agent_id)

        return unhealthy

    def get_heartbeat_history(
        self,
        agent_id: str,
        time_range: Optional[Tuple[datetime, datetime]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get heartbeat history for agent within time range.

        Args:
            agent_id: Unique agent identifier
            time_range: Optional (start_datetime, end_datetime) tuple

        Returns:
            List of heartbeat records within time range

        Example:
            >>> from datetime import datetime, timedelta
            >>> start = datetime.now() - timedelta(hours=1)
            >>> end = datetime.now()
            >>> history = monitor.get_heartbeat_history("agent-001", (start, end))
        """
        with self._thread_lock:
            if agent_id not in self.heartbeat_history:
                return []

            history = list(self.heartbeat_history[agent_id])

            if time_range is None:
                return history

            start_dt, end_dt = time_range
            start_ts = start_dt.timestamp()
            end_ts = end_dt.timestamp()

            filtered = [
                record for record in history
                if start_ts <= record["timestamp"] <= end_ts
            ]

            return filtered

    def configure_alerts(
        self,
        on_degraded: Optional[bool] = None,
        on_critical: Optional[bool] = None,
        on_failed: Optional[bool] = None,
        degraded_callback: Optional[Callable] = None,
        critical_callback: Optional[Callable] = None,
        failed_callback: Optional[Callable] = None
    ):
        """
        Configure alert settings and callbacks.

        Args:
            on_degraded: Enable/disable degraded alerts
            on_critical: Enable/disable critical alerts
            on_failed: Enable/disable failed alerts
            degraded_callback: Callback for degraded state: func(agent_id, state, details)
            critical_callback: Callback for critical state
            failed_callback: Callback for failed state

        Example:
            >>> def on_failure(agent_id, state, details):
            ...     print(f"ALERT: Agent {agent_id} failed!")
            >>> monitor.configure_alerts(
            ...     on_failed=True,
            ...     failed_callback=on_failure
            ... )
        """
        with self._thread_lock:
            if on_degraded is not None:
                self.alert_enabled[HealthState.DEGRADED] = on_degraded
            if on_critical is not None:
                self.alert_enabled[HealthState.CRITICAL] = on_critical
            if on_failed is not None:
                self.alert_enabled[HealthState.FAILED] = on_failed

            if degraded_callback is not None:
                self.alert_callbacks[HealthState.DEGRADED] = degraded_callback
            if critical_callback is not None:
                self.alert_callbacks[HealthState.CRITICAL] = critical_callback
            if failed_callback is not None:
                self.alert_callbacks[HealthState.FAILED] = failed_callback

        logger.info("Alert configuration updated")

    def get_monitoring_stats(self) -> Dict[str, Any]:
        """
        Get overall monitoring statistics.

        Returns:
            Dict with monitoring metrics

        Example:
            >>> stats = monitor.get_monitoring_stats()
            >>> print(f"Monitoring {stats['total_agents']} agents")
        """
        with self._thread_lock:
            health_counts = {
                "healthy": 0,
                "degraded": 0,
                "critical": 0,
                "failed": 0
            }

            for agent_id in self.monitoring_agents.keys():
                state = self.check_agent_health(agent_id)
                health_counts[state.value] += 1

            return {
                "total_agents": len(self.monitoring_agents),
                "health_distribution": health_counts,
                "total_heartbeats": sum(
                    len(history) for history in self.heartbeat_history.values()
                ),
                "monitoring_thread_alive": (
                    self.monitoring_thread.is_alive()
                    if self.monitoring_thread else False
                )
            }

    def shutdown(self):
        """
        Gracefully shutdown monitoring thread.

        Should be called when shutting down the application to ensure
        clean thread termination.

        Example:
            >>> monitor.shutdown()
        """
        logger.info("Shutting down HeartbeatMonitor...")
        self.shutdown_event.set()

        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=5.0)

            if self.monitoring_thread.is_alive():
                logger.warning("Monitoring thread did not terminate within timeout")
            else:
                logger.info("Monitoring thread terminated successfully")


__all__ = [
    "HeartbeatMonitor",
    "HealthState"
]
