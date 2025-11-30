#!/usr/bin/env python3
"""
TokenBudget Usage Examples

Demonstrates integration with MoAI-ADK's JIT Context Loader
and per-swarm token management.
"""

from moai_flow.resource import TokenBudget, allocate_swarm, consume_tokens, get_budget_status


def example_basic_allocation():
    """Example 1: Basic swarm allocation"""
    print("\n=== Example 1: Basic Allocation ===")

    budget = TokenBudget()

    # Allocate tokens to multiple swarms
    budget.allocate_swarm("swarm-backend", 50000)
    budget.allocate_swarm("swarm-frontend", 40000)
    budget.allocate_swarm("swarm-testing", 30000)

    # Check status
    status = budget.get_global_status()
    print(f"Total allocated: {status['total_allocated']}")
    print(f"Active swarms: {status['active_swarms']}")

    for swarm_id, info in status["swarms"].items():
        print(f"  {swarm_id}: {info['allocated']} tokens allocated")


def example_consumption_tracking():
    """Example 2: Track token consumption"""
    print("\n=== Example 2: Consumption Tracking ===")

    budget = TokenBudget()
    budget.allocate_swarm("swarm-analysis", 30000)

    # Simulate token consumption
    operations = [
        ("Initial context load", 5000),
        ("API documentation fetch", 3000),
        ("Code generation", 8000),
        ("Test generation", 4000),
    ]

    for operation, tokens in operations:
        if budget.consume("swarm-analysis", tokens):
            balance = budget.get_balance("swarm-analysis")
            usage = budget.get_usage_percent("swarm-analysis")
            print(f"{operation}: consumed {tokens} tokens")
            print(f"  Balance: {balance}, Usage: {usage:.1f}%")

            # Check warnings
            should_warn, message = budget.should_warn("swarm-analysis")
            if should_warn:
                print(f"  ⚠️  {message}")


def example_warning_thresholds():
    """Example 3: Warning threshold demonstration"""
    print("\n=== Example 3: Warning Thresholds ===")

    budget = TokenBudget()
    budget.allocate_swarm("swarm-heavy", 20000)

    # Consume tokens gradually to trigger warnings
    budget.consume("swarm-heavy", 10000)  # 50%
    print(f"50% usage: {budget.get_usage_percent('swarm-heavy'):.1f}%")

    budget.consume("swarm-heavy", 5000)  # 75%
    should_warn, message = budget.should_warn("swarm-heavy")
    print(f"75% usage: {message if should_warn else 'No warning'}")

    budget.consume("swarm-heavy", 3000)  # 90%
    should_warn, message = budget.should_warn("swarm-heavy")
    print(f"90% usage: {message if should_warn else 'No warning'}")


def example_global_thresholds():
    """Example 4: Global threshold monitoring"""
    print("\n=== Example 4: Global Thresholds (150K/180K) ===")

    budget = TokenBudget()

    # Allocate and consume to approach global thresholds
    budget.allocate_swarm("swarm-1", 80000)
    budget.allocate_swarm("swarm-2", 80000)

    # Consume 140K total (approaching 150K threshold)
    budget.consume("swarm-1", 70000)
    budget.consume("swarm-2", 70000)

    status = budget.get_global_status()
    print(f"Total consumed: {status['total_consumed']:,} / {status['total_budget']:,}")
    print(f"Global usage: {status['global_usage_percent']:.1f}%")
    print(f"Warning level: {status['warn_level']}")

    # Simulate hitting 150K threshold
    budget.consume("swarm-1", 10000)  # Now at 150K
    status = budget.get_global_status()
    print(f"\nAfter additional consumption:")
    print(f"Total consumed: {status['total_consumed']:,} / {status['total_budget']:,}")
    print(f"Warning level: {status['warn_level']}")


def example_reset_after_clear():
    """Example 5: Reset after /clear command"""
    print("\n=== Example 5: Reset After /clear ===")

    budget = TokenBudget()
    budget.allocate_swarm("swarm-session", 50000)

    # Consume tokens during session
    budget.consume("swarm-session", 30000)
    print(f"Before reset: consumed={budget.allocations['swarm-session'].consumed}")

    # User executes /clear command - reset consumption
    budget.reset("swarm-session")
    print(f"After reset: consumed={budget.allocations['swarm-session'].consumed}")
    print(f"Available tokens: {budget.get_balance('swarm-session')}")


def example_reservation():
    """Example 6: Reserve tokens for planned operations"""
    print("\n=== Example 6: Token Reservation ===")

    budget = TokenBudget()
    budget.allocate_swarm("swarm-planning", 40000)

    # Reserve tokens for upcoming operations
    print("Reserving tokens for planned tasks:")
    budget.reserve("swarm-planning", 5000)  # Large doc generation
    budget.reserve("swarm-planning", 3000)  # API integration

    allocation = budget.allocations["swarm-planning"]
    print(f"Allocated: {allocation.allocated}")
    print(f"Consumed: {allocation.consumed}")
    print(f"Reserved: {allocation.reserved}")
    print(f"Available: {allocation.available}")

    # Execute and release reservation
    budget.consume("swarm-planning", 5000)
    budget.release_reservation("swarm-planning", 5000)
    print(f"\nAfter consuming reserved tokens:")
    print(f"Available: {budget.allocations['swarm-planning'].available}")


def example_rebalancing():
    """Example 7: Automatic rebalancing"""
    print("\n=== Example 7: Automatic Rebalancing ===")

    budget = TokenBudget()
    budget.allocate_swarm("swarm-a", 60000)
    budget.allocate_swarm("swarm-b", 60000)
    budget.allocate_swarm("swarm-c", 60000)

    print("Before rebalancing:")
    for swarm_id in ["swarm-a", "swarm-b", "swarm-c"]:
        print(f"  {swarm_id}: {budget.allocations[swarm_id].allocated} tokens")

    # Consume heavily from swarm-a
    budget.consume("swarm-a", 50000)

    # Rebalance to distribute evenly
    rebalance_plan = budget.rebalance()

    print("\nAfter rebalancing:")
    for swarm_id, new_allocation in rebalance_plan.items():
        print(f"  {swarm_id}: {new_allocation} tokens")


def example_jit_integration():
    """Example 8: Integration with JIT Context Loader"""
    print("\n=== Example 8: JIT Context Loader Integration ===")

    # This demonstrates how TokenBudget integrates with existing JIT system
    budget = TokenBudget()

    # Scenario: Agent working through TDD cycle
    swarm_id = "swarm-tdd-cycle"
    budget.allocate_swarm(swarm_id, 60000)

    phases = [
        ("RED Phase - Test Creation", 15000),
        ("GREEN Phase - Minimal Implementation", 12000),
        ("REFACTOR Phase - Code Cleanup", 10000),
        ("Documentation Sync", 8000),
    ]

    print(f"TDD Cycle for {swarm_id}:")
    for phase_name, estimated_tokens in phases:
        # Check if tokens available
        if budget.get_balance(swarm_id) >= estimated_tokens:
            budget.consume(swarm_id, estimated_tokens)
            usage = budget.get_usage_percent(swarm_id)
            print(f"  ✓ {phase_name}: {estimated_tokens} tokens ({usage:.1f}% total)")
        else:
            balance = budget.get_balance(swarm_id)
            print(f"  ✗ {phase_name}: insufficient tokens (need {estimated_tokens}, have {balance})")

    # Final status
    status = budget.get_global_status()
    print(f"\nFinal global status: {status['total_consumed']:,} / {status['total_budget']:,} tokens")


if __name__ == "__main__":
    print("TokenBudget Usage Examples")
    print("=" * 60)

    example_basic_allocation()
    example_consumption_tracking()
    example_warning_thresholds()
    example_global_thresholds()
    example_reset_after_clear()
    example_reservation()
    example_rebalancing()
    example_jit_integration()

    print("\n" + "=" * 60)
    print("Examples complete!")
