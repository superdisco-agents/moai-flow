#!/usr/bin/env python3
"""
SelfHealer Demo for MoAI-Flow Phase 6C

Demonstrates automatic failure recovery with various healing strategies:
- Agent restart on heartbeat failure
- Task retry on timeout
- Resource rebalancing on exhaustion
- Quorum recovery on consensus failure

Example:
    python moai_flow/examples/self_healer_demo.py
"""

from moai_flow.core.swarm_coordinator import SwarmCoordinator
from moai_flow.optimization import (
    SelfHealer,
    Failure,
    AgentRestartStrategy,
    TaskRetryStrategy,
    ResourceRebalanceStrategy,
    QuorumRecoveryStrategy,
)
from datetime import datetime, timezone


def demo_agent_restart():
    """Demo: Agent restart healing strategy."""
    print("\n" + "="*70)
    print("DEMO 1: Agent Restart Healing")
    print("="*70)

    # Create coordinator
    coordinator = SwarmCoordinator(topology_type="mesh", enable_monitoring=True)

    # Register agents
    coordinator.register_agent("agent-001", {"type": "expert-backend"})
    coordinator.register_agent("agent-002", {"type": "expert-frontend"})

    # Create SelfHealer
    healer = SelfHealer(coordinator=coordinator, auto_heal=True)

    # Simulate heartbeat failure
    failure_event = {
        "type": "heartbeat_failed",
        "agent_id": "agent-001",
        "health_state": "FAILED"
    }

    print(f"\n1. Detecting failure from event: {failure_event}")
    failure = healer.detect_failure(failure_event)

    if failure:
        print(f"\n2. Failure detected:")
        print(f"   - ID: {failure.failure_id}")
        print(f"   - Type: {failure.failure_type}")
        print(f"   - Agent: {failure.agent_id}")
        print(f"   - Severity: {failure.severity}")

        print(f"\n3. Executing healing strategy...")
        result = healer.heal(failure)

        print(f"\n4. Healing result:")
        print(f"   - Success: {result.success}")
        print(f"   - Strategy: {result.strategy_used}")
        print(f"   - Duration: {result.duration_ms}ms")
        print(f"   - Actions taken:")
        for action in result.actions_taken:
            print(f"     • {action}")


def demo_task_retry():
    """Demo: Task retry healing strategy."""
    print("\n" + "="*70)
    print("DEMO 2: Task Retry Healing")
    print("="*70)

    coordinator = SwarmCoordinator(topology_type="mesh")
    healer = SelfHealer(coordinator=coordinator, auto_heal=True)

    # Register custom task retry strategy with max 2 retries
    healer.register_strategy("task_timeout", TaskRetryStrategy(max_retries=2))

    # Simulate task timeout
    failure_event = {
        "type": "task_timeout",
        "task_id": "task-xyz-123",
        "agent_id": "agent-001",
        "timeout_ms": 30000
    }

    print(f"\n1. Task timeout event: {failure_event['task_id']}")
    failure = healer.detect_failure(failure_event)

    if failure:
        print(f"\n2. Healing attempt 1:")
        result1 = healer.heal(failure)
        print(f"   - Success: {result1.success}")
        print(f"   - Retry count: {result1.metadata.get('retry_count', 0)}")

        print(f"\n3. Healing attempt 2 (same task):")
        result2 = healer.heal(failure)
        print(f"   - Success: {result2.success}")
        print(f"   - Retry count: {result2.metadata.get('retry_count', 0)}")

        print(f"\n4. Healing attempt 3 (max retries exceeded):")
        result3 = healer.heal(failure)
        print(f"   - Success: {result3.success}")
        print(f"   - Actions: {result3.actions_taken}")


def demo_resource_rebalance():
    """Demo: Resource rebalancing healing strategy."""
    print("\n" + "="*70)
    print("DEMO 3: Resource Rebalancing")
    print("="*70)

    coordinator = SwarmCoordinator(topology_type="star")
    healer = SelfHealer(coordinator=coordinator, auto_heal=True)

    # Simulate token exhaustion
    failure_event = {
        "type": "resource_exhaustion",
        "resource_type": "tokens",
        "current_usage": 195000,
        "limit": 200000,
        "severity": "critical"
    }

    print(f"\n1. Resource exhaustion detected:")
    print(f"   - Resource: {failure_event['resource_type']}")
    print(f"   - Usage: {failure_event['current_usage']}/{failure_event['limit']}")

    failure = healer.detect_failure(failure_event)

    if failure:
        print(f"\n2. Executing rebalancing strategy...")
        result = healer.heal(failure)

        print(f"\n3. Rebalancing result:")
        print(f"   - Success: {result.success}")
        print(f"   - Actions taken:")
        for action in result.actions_taken:
            print(f"     • {action}")


def demo_quorum_recovery():
    """Demo: Quorum recovery healing strategy."""
    print("\n" + "="*70)
    print("DEMO 4: Quorum Recovery")
    print("="*70)

    coordinator = SwarmCoordinator(topology_type="mesh", enable_consensus=True)

    # Register only 2 agents (below quorum of 3)
    coordinator.register_agent("agent-001", {"type": "expert-backend"})
    coordinator.register_agent("agent-002", {"type": "expert-frontend"})

    healer = SelfHealer(coordinator=coordinator, auto_heal=True)

    # Simulate quorum loss
    failure_event = {
        "type": "quorum_loss",
        "current_agents": 2,
        "required_quorum": 3
    }

    print(f"\n1. Quorum loss detected:")
    print(f"   - Current agents: {failure_event['current_agents']}")
    print(f"   - Required quorum: {failure_event['required_quorum']}")

    failure = healer.detect_failure(failure_event)

    if failure:
        print(f"\n2. Executing quorum recovery...")
        result = healer.heal(failure)

        print(f"\n3. Recovery result:")
        print(f"   - Success: {result.success}")
        print(f"   - Agents needed: {result.metadata.get('agents_needed', 0)}")
        print(f"   - Actions taken:")
        for action in result.actions_taken:
            print(f"     • {action}")


def demo_healing_stats():
    """Demo: Healing statistics and history."""
    print("\n" + "="*70)
    print("DEMO 5: Healing Statistics")
    print("="*70)

    coordinator = SwarmCoordinator(topology_type="mesh")
    healer = SelfHealer(coordinator=coordinator, auto_heal=True)

    # Register agents
    for i in range(3):
        coordinator.register_agent(f"agent-{i:03d}", {"type": "expert-backend"})

    # Simulate multiple failures
    failures = [
        {"type": "heartbeat_failed", "agent_id": "agent-001"},
        {"type": "task_timeout", "task_id": "task-001"},
        {"type": "resource_exhaustion", "resource_type": "tokens"},
        {"type": "heartbeat_failed", "agent_id": "agent-002"},
    ]

    print(f"\n1. Processing {len(failures)} failures...")
    for i, event in enumerate(failures, 1):
        failure = healer.detect_failure(event)
        if failure:
            result = healer.heal(failure)
            print(f"   {i}. {failure.failure_type}: {'✓' if result.success else '✗'}")

    # Get statistics
    print(f"\n2. Healing statistics:")
    stats = healer.get_healing_stats()
    print(f"   - Total failures: {stats['total_failures_detected']}")
    print(f"   - Success rate: {stats['success_rate']:.1%}")
    print(f"   - Average healing time: {stats['average_healing_time_ms']:.2f}ms")

    print(f"\n3. Success rate by type:")
    for failure_type, rate in stats["success_rate_by_type"].items():
        print(f"   - {failure_type}: {rate:.1%}")

    # Get history
    print(f"\n4. Recent healing history:")
    history = healer.get_healing_history(limit=3)
    for result in history:
        print(f"   - {result.failure_id}")
        print(f"     Strategy: {result.strategy_used}")
        print(f"     Success: {result.success}")
        print(f"     Duration: {result.duration_ms}ms")


def main():
    """Run all SelfHealer demos."""
    print("\n" + "="*70)
    print("MoAI-Flow SelfHealer Demo - Phase 6C Adaptive Optimization")
    print("="*70)

    demo_agent_restart()
    demo_task_retry()
    demo_resource_rebalance()
    demo_quorum_recovery()
    demo_healing_stats()

    print("\n" + "="*70)
    print("All demos completed successfully!")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
