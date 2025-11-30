"""
MoAI-Flow Hooks Module

Enhanced hook system with multiple executors, priorities, and dependencies.

Core Components:
- HookExecutor: Abstract interface for hook execution
- StandardHookExecutor: Synchronous execution with timeout
- AsyncHookExecutor: Asynchronous execution with concurrency
- HookRegistry: Central registry with priorities and dependencies
- AgentLifecycle: Agent spawn/complete events (existing)

Example:
    >>> from moai_flow.hooks import HookRegistry, HookPriority, HookPhase
    >>> registry = HookRegistry()
    >>> def my_hook(context):
    ...     return {"status": "success"}
    >>> registry.register_hook("my_hook", my_hook, "task_start", priority=HookPriority.HIGH)
"""

# Phase 7 Track 1: Enhanced Hook System
from .hook_executor import (
    HookContext,
    HookPhase,
    HookResult,
    IHookExecutor,
    HookFunction,
    AsyncHookFunction,
)
from .standard_executor import StandardHookExecutor, TimeoutException
from .async_executor import AsyncHookExecutor
from .hook_registry import (
    HookRegistry,
    HookPriority,
    HookRegistration,
)

# Agent lifecycle hooks (existing)
from .agent_lifecycle import (
    on_agent_spawn,
    on_agent_complete,
    on_agent_error,
    get_active_agents,
    generate_agent_id,
)

# Pattern collection hooks
from .post_task_pattern import (
    PostTaskPatternHook,
    ErrorPatternHook,
    register_pattern_hooks,
)

__all__ = [
    # Phase 7: Enhanced Hook System
    "HookContext",
    "HookPhase",
    "HookResult",
    "IHookExecutor",
    "HookFunction",
    "AsyncHookFunction",
    "StandardHookExecutor",
    "TimeoutException",
    "AsyncHookExecutor",
    "HookRegistry",
    "HookPriority",
    "HookRegistration",
    # Agent Lifecycle (existing)
    "on_agent_spawn",
    "on_agent_complete",
    "on_agent_error",
    "get_active_agents",
    "generate_agent_id",
    # Pattern Collection Hooks
    "PostTaskPatternHook",
    "ErrorPatternHook",
    "register_pattern_hooks",
]
