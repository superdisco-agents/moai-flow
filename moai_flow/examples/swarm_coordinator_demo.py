#!/usr/bin/env python3
"""
SwarmCoordinator Demo

Comprehensive demonstration of SwarmCoordinator capabilities:
- Multi-topology support (Hierarchical, Mesh, Star, Ring, Adaptive)
- Agent registration and management
- Message routing and broadcasting
- Consensus mechanism
- State synchronization
- Dynamic topology switching
- Health monitoring

Run:
    python -m moai_flow.examples.swarm_coordinator_demo
"""

import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from moai_flow.core.swarm_coordinator import (
    SwarmCoordinator,
    AgentState,
    TopologyHealth
)


def print_section(title: str):
    """Print section header."""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def demo_mesh_topology():
    """Demonstrate Mesh topology with full connectivity."""
    print_section("Demo 1: Mesh Topology (Full Connectivity)")

    # Create coordinator with mesh topology
    coordinator = SwarmCoordinator(topology_type="mesh")

    # Register agents
    agents = [
        ("agent-001", {"type": "expert-backend", "capabilities": ["python", "fastapi"]}),
        ("agent-002", {"type": "expert-frontend", "capabilities": ["react", "typescript"]}),
        ("agent-003", {"type": "expert-database", "capabilities": ["postgresql", "sql"]}),
    ]

    for agent_id, metadata in agents:
        success = coordinator.register_agent(agent_id, metadata)
        print(f"✓ Registered {agent_id}: {success}")

    # Get topology info
    info = coordinator.get_topology_info()
    print(f"\nTopology Info:")
    print(f"  Type: {info['type']}")
    print(f"  Agents: {info['agent_count']}")
    print(f"  Connections: {info['connection_count']}")
    print(f"  Health: {info['health']}")

    # Send direct message
    print("\nSending direct message...")
    coordinator.send_message(
        "agent-001",
        "agent-002",
        {"task": "process_data", "priority": "high"}
    )

    # Broadcast message
    print("\nBroadcasting message...")
    sent_count = coordinator.broadcast_message(
        "agent-001",
        {"type": "heartbeat", "status": "alive"}
    )
    print(f"✓ Broadcast sent to {sent_count} agents")

    # Visualize topology
    print("\nTopology Visualization:")
    print(coordinator.visualize_topology())


def demo_hierarchical_topology():
    """Demonstrate Hierarchical topology with Alfred as root."""
    print_section("Demo 2: Hierarchical Topology (Tree Structure)")

    # Create coordinator with hierarchical topology
    coordinator = SwarmCoordinator(
        topology_type="hierarchical",
        root_agent_id="alfred"
    )

    # Register agents in layers
    agents = [
        # Layer 1: Managers
        ("manager-tdd", {
            "type": "manager-tdd",
            "layer": 1,
            "parent_id": "alfred"
        }),
        ("manager-docs", {
            "type": "manager-docs",
            "layer": 1,
            "parent_id": "alfred"
        }),
        # Layer 2: Specialists
        ("expert-backend", {
            "type": "expert-backend",
            "layer": 2,
            "parent_id": "manager-tdd"
        }),
        ("expert-frontend", {
            "type": "expert-frontend",
            "layer": 2,
            "parent_id": "manager-tdd"
        }),
        ("expert-database", {
            "type": "expert-database",
            "layer": 2,
            "parent_id": "manager-docs"
        }),
    ]

    for agent_id, metadata in agents:
        success = coordinator.register_agent(agent_id, metadata)
        print(f"✓ Registered {agent_id} at layer {metadata['layer']}: {success}")

    # Get topology info
    info = coordinator.get_topology_info()
    print(f"\nTopology Info:")
    print(f"  Type: {info['type']}")
    print(f"  Agents: {info['agent_count']}")
    print(f"  Layers: {info['topology_specific']['layers']}")
    print(f"  Health: {info['health']}")

    # Visualize topology
    print("\nTopology Visualization:")
    print(coordinator.visualize_topology())


def demo_consensus_mechanism():
    """Demonstrate consensus voting mechanism."""
    print_section("Demo 3: Consensus Mechanism (Majority Voting)")

    # Create coordinator
    coordinator = SwarmCoordinator(
        topology_type="mesh",
        consensus_threshold=0.6  # 60% threshold
    )

    # Register agents
    for i in range(1, 6):
        agent_id = f"agent-{i:03d}"
        coordinator.register_agent(
            agent_id,
            {"type": f"expert-backend-{i}"}
        )
        # Set some agents as ACTIVE (will vote "approve")
        if i <= 4:
            coordinator.set_agent_state(agent_id, AgentState.ACTIVE)

    print(f"Registered 5 agents (4 ACTIVE, 1 IDLE)")

    # Request consensus
    proposal = {
        "proposal_id": "deploy-v2",
        "description": "Deploy version 2.0 to production",
        "options": ["approve", "reject"]
    }

    result = coordinator.request_consensus(proposal, timeout_ms=5000)

    print(f"\nConsensus Result:")
    print(f"  Decision: {result['decision']}")
    print(f"  Votes For: {result['votes_for']}")
    print(f"  Votes Against: {result['votes_against']}")
    print(f"  Abstain: {result['abstain']}")
    print(f"  Threshold: {result['threshold']}")
    print(f"  Participants: {len(result['participants'])}")

    # Show vote details
    print(f"\nVote Details:")
    for agent_id, vote in result['vote_details'].items():
        print(f"  {agent_id}: {vote}")


def demo_state_synchronization():
    """Demonstrate state synchronization across agents."""
    print_section("Demo 4: State Synchronization")

    # Create coordinator
    coordinator = SwarmCoordinator(topology_type="mesh")

    # Register agents
    for i in range(1, 4):
        coordinator.register_agent(
            f"agent-{i:03d}",
            {"type": f"expert-backend-{i}"}
        )

    # Synchronize state
    print("Synchronizing task queue state...")
    success = coordinator.synchronize_state(
        "task_queue",
        {
            "pending": 5,
            "in_progress": 2,
            "completed": 10,
            "failed": 1
        }
    )
    print(f"✓ State synchronized: {success}")

    # Synchronize configuration
    print("\nSynchronizing configuration state...")
    success = coordinator.synchronize_state(
        "config",
        {
            "max_retries": 3,
            "timeout_ms": 30000,
            "batch_size": 100
        }
    )
    print(f"✓ State synchronized: {success}")

    # Get synchronized state
    print("\nSynchronized States:")
    states = coordinator.get_synchronized_state()
    for key, data in states.items():
        print(f"  {key}: version {data['version']}, updated at {data['timestamp']}")
        print(f"    Value: {data['value']}")


def demo_topology_switching():
    """Demonstrate dynamic topology switching."""
    print_section("Demo 5: Dynamic Topology Switching")

    # Start with mesh topology
    coordinator = SwarmCoordinator(topology_type="mesh")

    # Register agents
    agents = [
        ("agent-001", {"type": "expert-backend"}),
        ("agent-002", {"type": "expert-frontend"}),
        ("agent-003", {"type": "expert-database"}),
    ]

    for agent_id, metadata in agents:
        coordinator.register_agent(agent_id, metadata)

    print(f"Initial Topology: mesh")
    info = coordinator.get_topology_info()
    print(f"  Agents: {info['agent_count']}")
    print(f"  Connections: {info['connection_count']}")

    # Switch to star topology
    print("\nSwitching to star topology...")
    coordinator.switch_topology("star")

    info = coordinator.get_topology_info()
    print(f"✓ Switched to: {info['type']}")
    print(f"  Agents: {info['agent_count']}")
    print(f"  Connections: {info['connection_count']}")

    # Switch to hierarchical topology
    print("\nSwitching to hierarchical topology...")

    # Update agent metadata for hierarchical structure
    for i, (agent_id, _) in enumerate(agents, 1):
        coordinator.agent_registry[agent_id].update({
            "layer": 1 if i == 1 else 2,
            "parent_id": "alfred" if i == 1 else "agent-001"
        })

    coordinator.switch_topology("hierarchical")

    info = coordinator.get_topology_info()
    print(f"✓ Switched to: {info['type']}")
    print(f"  Agents: {info['agent_count']}")
    print(f"  Layers: {info['topology_specific']['layers']}")

    print("\nFinal Topology Visualization:")
    print(coordinator.visualize_topology())


def demo_agent_status_monitoring():
    """Demonstrate agent status tracking and health monitoring."""
    print_section("Demo 6: Agent Status Monitoring")

    # Create coordinator
    coordinator = SwarmCoordinator(topology_type="mesh")

    # Register agents with different states
    agents = [
        ("agent-001", AgentState.ACTIVE),
        ("agent-002", AgentState.BUSY),
        ("agent-003", AgentState.IDLE),
    ]

    for agent_id, state in agents:
        coordinator.register_agent(agent_id, {"type": "expert-backend"})
        coordinator.set_agent_state(agent_id, state)

    print("Agent Status:")
    for agent_id, _ in agents:
        status = coordinator.get_agent_status(agent_id)
        print(f"\n{agent_id}:")
        print(f"  State: {status['state']}")
        print(f"  Heartbeat Age: {status['heartbeat_age_seconds']}s")
        print(f"  Role: {status['topology_role']}")

    # Update heartbeat
    print(f"\nUpdating heartbeat for agent-001...")
    time.sleep(1)
    coordinator.update_agent_heartbeat("agent-001")

    status = coordinator.get_agent_status("agent-001")
    print(f"  New Heartbeat Age: {status['heartbeat_age_seconds']}s")

    # Get overall topology health
    print("\nTopology Health:")
    info = coordinator.get_topology_info()
    print(f"  Health: {info['health']}")
    print(f"  Active Agents: {info['active_agents']}")
    print(f"  Failed Agents: {info['failed_agents']}")


def demo_message_routing():
    """Demonstrate message routing across different topologies."""
    print_section("Demo 7: Message Routing Across Topologies")

    topologies = ["mesh", "star", "hierarchical"]

    for topo_type in topologies:
        print(f"\n--- {topo_type.upper()} Topology ---")

        coordinator = SwarmCoordinator(topology_type=topo_type)

        # Register agents
        if topo_type == "hierarchical":
            coordinator.register_agent(
                "agent-001",
                {"type": "manager-tdd", "layer": 1, "parent_id": "alfred"}
            )
            coordinator.register_agent(
                "agent-002",
                {"type": "expert-backend", "layer": 2, "parent_id": "agent-001"}
            )
        else:
            coordinator.register_agent("agent-001", {"type": "expert-backend"})
            coordinator.register_agent("agent-002", {"type": "expert-frontend"})

        # Send message
        coordinator.send_message(
            "agent-001",
            "agent-002",
            {"task": "test_message"}
        )
        print(f"✓ Direct message sent")

        # Broadcast message
        sent_count = coordinator.broadcast_message(
            "agent-001",
            {"type": "broadcast_test"}
        )
        print(f"✓ Broadcast sent to {sent_count} agents")


def demo_adaptive_topology():
    """Demonstrate adaptive topology with automatic switching."""
    print_section("Demo 8: Adaptive Topology (Auto-Switching)")

    # Create coordinator with adaptive topology
    coordinator = SwarmCoordinator(topology_type="adaptive")

    print("Starting with adaptive topology (initial mode: MESH)")

    # Add agents gradually to trigger topology switches
    print("\nAdding agents...")

    for i in range(1, 8):
        agent_id = f"agent-{i:03d}"
        coordinator.register_agent(agent_id, {"type": f"expert-{i}"})

        info = coordinator.get_topology_info()
        current_mode = info['topology_specific'].get('current_mode', 'unknown')

        print(f"Added {agent_id} (total: {i} agents) - Mode: {current_mode}")

        # Note: Adaptive topology switches automatically based on agent count
        # < 5 agents: mesh
        # 5-10 agents: star
        # > 10 agents: hierarchical


def main():
    """Run all demonstrations."""
    demos = [
        ("Mesh Topology", demo_mesh_topology),
        ("Hierarchical Topology", demo_hierarchical_topology),
        ("Consensus Mechanism", demo_consensus_mechanism),
        ("State Synchronization", demo_state_synchronization),
        ("Topology Switching", demo_topology_switching),
        ("Agent Status Monitoring", demo_agent_status_monitoring),
        ("Message Routing", demo_message_routing),
        ("Adaptive Topology", demo_adaptive_topology),
    ]

    print("\n" + "="*70)
    print("  SwarmCoordinator Comprehensive Demo")
    print("="*70)

    for i, (name, demo_func) in enumerate(demos, 1):
        print(f"\n[{i}/{len(demos)}] Running: {name}")
        try:
            demo_func()
        except Exception as e:
            print(f"\n❌ Error in {name}: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "="*70)
    print("  All Demos Complete!")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
