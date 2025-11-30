#!/usr/bin/env python3
"""
HeartbeatMonitor Integration Example with SwarmCoordinator

Demonstrates how to integrate HeartbeatMonitor with SwarmCoordinator
for comprehensive agent health monitoring.

Example shows:
- Initializing both monitor and coordinator
- Registering agents in both systems
- Recording heartbeats on agent activity
- Detecting and handling failed agents
- Alert callbacks for health state changes
- Health dashboard display

Usage:
    python moai_flow/examples/heartbeat_monitor_integration.py
"""

import time
from datetime import datetime
from typing import Dict, Any

from moai_flow.core import SwarmCoordinator
from moai_flow.monitoring import HeartbeatMonitor, HealthState


class SwarmWithHealthMonitoring:
    """
    Swarm coordinator with integrated health monitoring.

    Combines SwarmCoordinator and HeartbeatMonitor to provide
    comprehensive agent coordination with health tracking.
    """

    def __init__(
        self,
        topology_type: str = "mesh",
        heartbeat_interval_ms: int = 5000,
        failure_threshold: int = 3
    ):
        """
        Initialize swarm with health monitoring.

        Args:
            topology_type: Coordination topology
            heartbeat_interval_ms: Default heartbeat interval
            failure_threshold: Missed heartbeats before failure
        """
        self.coordinator = SwarmCoordinator(topology_type=topology_type)
        self.monitor = HeartbeatMonitor(
            interval_ms=heartbeat_interval_ms,
            failure_threshold=failure_threshold
        )

        # Configure alert callbacks
        self.monitor.configure_alerts(
            on_degraded=True,
            on_critical=True,
            on_failed=True,
            degraded_callback=self._on_agent_degraded,
            critical_callback=self._on_agent_critical,
            failed_callback=self._on_agent_failed
        )

        print(f"Swarm initialized with {topology_type} topology")
        print(f"Health monitoring: {heartbeat_interval_ms}ms interval, "
              f"{failure_threshold} failure threshold\n")

    def register_agent(
        self,
        agent_id: str,
        agent_metadata: Dict[str, Any],
        custom_interval_ms: int = None
    ) -> bool:
        """
        Register agent in both coordinator and health monitor.

        Args:
            agent_id: Unique agent identifier
            agent_metadata: Agent metadata
            custom_interval_ms: Optional custom heartbeat interval

        Returns:
            True if registered successfully
        """
        # Register in coordinator
        coord_success = self.coordinator.register_agent(agent_id, agent_metadata)

        if not coord_success:
            return False

        # Register in health monitor
        monitor_success = self.monitor.start_monitoring(
            agent_id,
            interval_ms=custom_interval_ms
        )

        if monitor_success:
            # Record initial heartbeat
            self.monitor.record_heartbeat(agent_id, metadata={"event": "registered"})
            print(f"✅ Registered {agent_id} (type: {agent_metadata.get('type')})")

        return monitor_success

    def unregister_agent(self, agent_id: str) -> bool:
        """
        Unregister agent from both coordinator and monitor.

        Args:
            agent_id: Agent identifier

        Returns:
            True if unregistered successfully
        """
        # Stop monitoring
        monitor_success = self.monitor.stop_monitoring(agent_id)

        # Unregister from coordinator
        coord_success = self.coordinator.unregister_agent(agent_id)

        if coord_success:
            print(f"❌ Unregistered {agent_id}")

        return coord_success and monitor_success

    def send_message(
        self,
        from_agent: str,
        to_agent: str,
        message: Dict[str, Any]
    ) -> bool:
        """
        Send message and update heartbeat.

        Args:
            from_agent: Source agent
            to_agent: Destination agent
            message: Message payload

        Returns:
            True if sent successfully
        """
        # Send message through coordinator
        success = self.coordinator.send_message(from_agent, to_agent, message)

        if success:
            # Update sender's heartbeat
            self.monitor.record_heartbeat(
                from_agent,
                metadata={"action": "message_sent", "to": to_agent}
            )

        return success

    def broadcast_message(
        self,
        from_agent: str,
        message: Dict[str, Any]
    ) -> int:
        """
        Broadcast message and update heartbeat.

        Args:
            from_agent: Source agent
            message: Message payload

        Returns:
            Number of agents that received message
        """
        # Broadcast through coordinator
        count = self.coordinator.broadcast_message(from_agent, message)

        # Update heartbeat
        self.monitor.record_heartbeat(
            from_agent,
            metadata={"action": "broadcast", "recipients": count}
        )

        return count

    def check_agent_health(self, agent_id: str) -> HealthState:
        """
        Check agent health state.

        Args:
            agent_id: Agent identifier

        Returns:
            Current health state
        """
        return self.monitor.check_agent_health(agent_id)

    def get_unhealthy_agents(self) -> Dict[str, HealthState]:
        """
        Get all unhealthy agents with their states.

        Returns:
            Dict mapping agent_id to health state
        """
        unhealthy = {}

        for agent_id in self.coordinator.agent_registry.keys():
            health = self.monitor.check_agent_health(agent_id)
            if health != HealthState.HEALTHY:
                unhealthy[agent_id] = health

        return unhealthy

    def display_health_dashboard(self):
        """Display real-time health dashboard."""
        print("\n" + "="*60)
        print("SWARM HEALTH DASHBOARD")
        print("="*60)

        # Get monitoring stats
        stats = self.monitor.get_monitoring_stats()

        # Display per-agent health
        for agent_id in self.coordinator.agent_registry.keys():
            try:
                health = self.monitor.check_agent_health(agent_id)
                agent_type = self.coordinator.agent_registry[agent_id].get("type", "unknown")

                icon = {
                    HealthState.HEALTHY: "✅",
                    HealthState.DEGRADED: "⚠️ ",
                    HealthState.CRITICAL: "🔴",
                    HealthState.FAILED: "❌"
                }[health]

                print(f"{icon} {agent_id:20s} ({agent_type:15s}) {health.value.upper()}")
            except ValueError:
                print(f"❓ {agent_id:20s} NOT MONITORED")

        # Display summary
        print("-"*60)
        print(f"Total Agents: {stats['total_agents']}")
        print(f"  Healthy:    {stats['health_distribution']['healthy']}")
        print(f"  Degraded:   {stats['health_distribution']['degraded']}")
        print(f"  Critical:   {stats['health_distribution']['critical']}")
        print(f"  Failed:     {stats['health_distribution']['failed']}")
        print(f"Total Heartbeats: {stats['total_heartbeats']}")

        # Topology info
        topo_info = self.coordinator.get_topology_info()
        print(f"Topology: {topo_info['type']} ({topo_info['connection_count']} connections)")
        print("="*60 + "\n")

    def _on_agent_degraded(self, agent_id: str, state: HealthState, details: Dict):
        """Handle degraded agent state."""
        print(f"⚠️  WARNING: Agent {agent_id} is DEGRADED")
        print(f"   Previous state: {details['previous_state']}")
        print(f"   Elapsed: {details['elapsed_seconds']}s")

    def _on_agent_critical(self, agent_id: str, state: HealthState, details: Dict):
        """Handle critical agent state."""
        print(f"🔴 CRITICAL: Agent {agent_id} is CRITICAL")
        print(f"   Previous state: {details['previous_state']}")
        print(f"   Elapsed: {details['elapsed_seconds']}s")
        print(f"   Consider intervention!")

    def _on_agent_failed(self, agent_id: str, state: HealthState, details: Dict):
        """Handle failed agent state."""
        print(f"❌ FAILED: Agent {agent_id} has FAILED")
        print(f"   Last heartbeat: {details['last_heartbeat']}")
        print(f"   Elapsed: {details['elapsed_seconds']}s")
        print(f"   Auto-restart initiated...")

        # Auto-restart failed agent
        metadata = self.coordinator.agent_registry.get(agent_id)
        if metadata:
            self.unregister_agent(agent_id)
            time.sleep(0.5)
            self.register_agent(agent_id, metadata)
            print(f"   ✅ Agent {agent_id} restarted")

    def shutdown(self):
        """Gracefully shutdown swarm and monitor."""
        print("\nShutting down swarm...")
        self.monitor.shutdown()
        print("✅ Swarm shutdown complete")


def example_basic_usage():
    """Basic usage example."""
    print("\n" + "="*60)
    print("EXAMPLE 1: Basic Usage")
    print("="*60 + "\n")

    # Initialize swarm with health monitoring
    swarm = SwarmWithHealthMonitoring(
        topology_type="mesh",
        heartbeat_interval_ms=2000,  # 2 seconds
        failure_threshold=3
    )

    # Register agents
    swarm.register_agent(
        "agent-001",
        {"type": "expert-backend", "capabilities": ["python", "fastapi"]}
    )

    swarm.register_agent(
        "agent-002",
        {"type": "expert-frontend", "capabilities": ["react", "typescript"]}
    )

    swarm.register_agent(
        "agent-003",
        {"type": "manager-tdd", "capabilities": ["testing", "quality"]}
    )

    # Display initial health
    time.sleep(0.5)
    swarm.display_health_dashboard()

    # Simulate agent activity
    print("Simulating agent activity...")
    swarm.send_message("agent-001", "agent-002", {"task": "process_request"})
    swarm.broadcast_message("agent-003", {"type": "status_update"})

    time.sleep(1)
    swarm.display_health_dashboard()

    # Cleanup
    swarm.shutdown()


def example_failure_detection():
    """Failure detection example."""
    print("\n" + "="*60)
    print("EXAMPLE 2: Failure Detection")
    print("="*60 + "\n")

    # Create swarm with fast heartbeat for demo
    swarm = SwarmWithHealthMonitoring(
        topology_type="star",
        heartbeat_interval_ms=1000,  # 1 second
        failure_threshold=3  # 3 seconds to failure
    )

    # Register agents
    swarm.register_agent("healthy-agent", {"type": "expert-backend"})
    swarm.register_agent("failing-agent", {"type": "expert-frontend"})

    # Keep healthy agent alive
    print("\nSimulating normal operation...")
    for i in range(5):
        swarm.monitor.record_heartbeat("healthy-agent")
        time.sleep(1)
        print(f"  Tick {i+1}: healthy-agent heartbeat")

    # Display health (failing-agent should be failed by now)
    time.sleep(1)
    swarm.display_health_dashboard()

    # Cleanup
    swarm.shutdown()


def example_recovery():
    """Agent recovery example."""
    print("\n" + "="*60)
    print("EXAMPLE 3: Agent Recovery")
    print("="*60 + "\n")

    swarm = SwarmWithHealthMonitoring(
        topology_type="mesh",
        heartbeat_interval_ms=1000,
        failure_threshold=3
    )

    # Register agent
    swarm.register_agent("recovery-agent", {"type": "expert-backend"})

    # Let it go degraded
    print("\nAgent going degraded...")
    time.sleep(1.5)
    swarm.display_health_dashboard()

    # Recover agent
    print("Recovering agent...")
    swarm.monitor.record_heartbeat("recovery-agent", metadata={"recovered": True})
    time.sleep(0.5)
    swarm.display_health_dashboard()

    # Cleanup
    swarm.shutdown()


if __name__ == "__main__":
    """Run all examples."""
    try:
        example_basic_usage()
        time.sleep(2)

        example_failure_detection()
        time.sleep(2)

        example_recovery()

    except KeyboardInterrupt:
        print("\n\n❌ Interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
