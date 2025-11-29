"""
MoAI-Flow Resource Module

Resource control and allocation:
- TokenBudget: Per-swarm token allocation
- AgentQuota: Execution quotas per agent type
- PriorityQueue: Task priority management
"""

from .token_budget import (
    TokenBudget,
    BudgetConfig,
    SwarmAllocation,
    allocate_swarm,
    consume_tokens,
    get_swarm_balance,
    reset_swarm,
    get_budget_status,
)

# Future exports (Phase 3)
# from .agent_quota import AgentQuota
# from .priority_queue import PriorityQueue

__all__ = [
    "TokenBudget",
    "BudgetConfig",
    "SwarmAllocation",
    "allocate_swarm",
    "consume_tokens",
    "get_swarm_balance",
    "reset_swarm",
    "get_budget_status",
    # Future: "AgentQuota",
    # Future: "PriorityQueue",
]
