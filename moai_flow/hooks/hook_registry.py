#!/usr/bin/env python3
"""
HookRegistry - Enhanced Hook Registration and Execution

Centralized registry for managing hooks with priorities, dependencies,
conditional execution, and multiple executor support.

Features:
- Priority-based ordering (5 levels: CRITICAL → DEFERRED)
- Multiple executor support (standard, async, custom)
- Conditional execution (predicate functions)
- Hook dependencies (execution order)
- Enable/disable hooks dynamically
- Topological sorting for dependencies

Example:
    >>> from hook_registry import HookRegistry, HookPriority
    >>> from hook_executor import HookPhase
    >>> from standard_executor import StandardHookExecutor
    >>>
    >>> registry = HookRegistry()
    >>>
    >>> # Register hook with priority
    >>> def validate_input(context):
    ...     return {"valid": True}
    >>>
    >>> registry.register_hook(
    ...     name="validate_critical",
    ...     hook=validate_input,
    ...     event_type="task_start",
    ...     phase=HookPhase.PRE,
    ...     priority=HookPriority.CRITICAL
    ... )
    >>>
    >>> # Execute all hooks for event
    >>> context = HookContext(...)
    >>> results = registry.execute_hooks("task_start", HookPhase.PRE, context)
"""

import logging
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from .hook_executor import HookContext, HookPhase, HookResult, IHookExecutor
from .standard_executor import StandardHookExecutor
from .async_executor import AsyncHookExecutor

logger = logging.getLogger(__name__)


class HookPriority(Enum):
    """
    Hook execution priority levels.

    Hooks are executed in order:
    CRITICAL → HIGH → NORMAL → LOW → DEFERRED
    """
    CRITICAL = 0  # Execute first (validation, auth)
    HIGH = 1      # High priority (metrics, logging)
    NORMAL = 2    # Normal priority (default)
    LOW = 3       # Low priority (cleanup, notifications)
    DEFERRED = 4  # Execute last (analytics, aggregation)


@dataclass
class HookRegistration:
    """
    Hook registration metadata.

    Contains all information needed to execute a hook, including
    priority, conditions, dependencies, and executor configuration.

    Attributes:
        name: Unique hook identifier
        hook: Callable hook function
        event_type: Event type to trigger on (e.g., "task_start")
        phase: Lifecycle phase (PRE, POST, ERROR)
        priority: Execution priority (CRITICAL to DEFERRED)
        executor_type: Executor name ("standard", "async", or custom)
        conditions: List of predicate functions (all must return True)
        dependencies: List of hook names that must execute first
        enabled: Whether hook is currently enabled

    Example:
        >>> registration = HookRegistration(
        ...     name="validate_input",
        ...     hook=validate_function,
        ...     event_type="task_start",
        ...     phase=HookPhase.PRE,
        ...     priority=HookPriority.CRITICAL,
        ...     executor_type="standard",
        ...     conditions=[lambda ctx: ctx.data.get("validate", True)],
        ...     dependencies=[],
        ...     enabled=True
        ... )
    """
    name: str
    hook: Callable
    event_type: str
    phase: HookPhase
    priority: HookPriority = HookPriority.NORMAL
    executor_type: str = "standard"
    conditions: List[Callable] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    enabled: bool = True

    def __hash__(self):
        """Make HookRegistration hashable for set operations"""
        return hash((self.name, self.event_type, self.phase.value))

    def __eq__(self, other):
        """Equality check for HookRegistration"""
        if not isinstance(other, HookRegistration):
            return False
        return (
            self.name == other.name
            and self.event_type == other.event_type
            and self.phase == other.phase
        )


class HookRegistry:
    """
    Enhanced hook registry with priorities and executors.

    Central registry for managing hook lifecycle:
    - Register hooks with metadata
    - Execute hooks with proper ordering
    - Support multiple executor types
    - Handle conditions and dependencies

    Example:
        >>> registry = HookRegistry()
        >>>
        >>> # Register custom executor
        >>> custom_executor = CustomExecutor()
        >>> registry.register_executor("custom", custom_executor)
        >>>
        >>> # Register hook
        >>> registry.register_hook(
        ...     name="my_hook",
        ...     hook=my_function,
        ...     event_type="task_start",
        ...     priority=HookPriority.HIGH
        ... )
        >>>
        >>> # Execute hooks
        >>> results = registry.execute_hooks("task_start", HookPhase.PRE, context)
    """

    def __init__(self):
        """Initialize hook registry with default executors"""
        # Hook storage: {event_type: {phase: [HookRegistration]}}
        self._hooks: Dict[str, Dict[HookPhase, List[HookRegistration]]] = defaultdict(
            lambda: defaultdict(list)
        )

        # Executor storage: {name: IHookExecutor}
        self._executors: Dict[str, IHookExecutor] = {}

        # Execution statistics
        self._execution_counts: Dict[str, int] = defaultdict(int)
        self._success_counts: Dict[str, int] = defaultdict(int)
        self._failure_counts: Dict[str, int] = defaultdict(int)

        # Register default executors
        self._register_default_executors()

        logger.debug("HookRegistry initialized with default executors")

    def _register_default_executors(self):
        """Register built-in executors"""
        self._executors["standard"] = StandardHookExecutor(
            timeout_ms=2000,
            graceful_degradation=True,
            max_retries=0
        )

        self._executors["async"] = AsyncHookExecutor(
            timeout_ms=5000,
            concurrent_limit=10
        )

        logger.debug("Default executors registered: standard, async")

    def register_executor(self, name: str, executor: IHookExecutor):
        """
        Register custom executor.

        Args:
            name: Executor identifier
            executor: IHookExecutor implementation

        Raises:
            TypeError: If executor doesn't implement IHookExecutor
            ValueError: If name already registered

        Example:
            >>> custom_executor = CustomExecutor()
            >>> registry.register_executor("custom", custom_executor)
        """
        if not isinstance(executor, IHookExecutor):
            raise TypeError(f"Executor must implement IHookExecutor, got {type(executor)}")

        if name in self._executors:
            raise ValueError(f"Executor '{name}' already registered")

        self._executors[name] = executor
        logger.info(f"Registered custom executor: {name}")

    def register_hook(
        self,
        name: str,
        hook: Callable,
        event_type: str,
        phase: HookPhase = HookPhase.PRE,
        priority: HookPriority = HookPriority.NORMAL,
        executor_type: str = "standard",
        conditions: Optional[List[Callable]] = None,
        dependencies: Optional[List[str]] = None
    ) -> None:
        """
        Register hook with metadata.

        Args:
            name: Unique hook identifier
            hook: Callable hook function
            event_type: Event type (e.g., "task_start", "agent_spawn")
            phase: Lifecycle phase (default: PRE)
            priority: Execution priority (default: NORMAL)
            executor_type: Executor name (default: "standard")
            conditions: Predicate functions (all must return True)
            dependencies: Hook names that must execute first

        Raises:
            ValueError: If hook name already registered for event/phase
            ValueError: If executor_type not found

        Example:
            >>> def my_hook(context):
            ...     return {"status": "success"}
            >>>
            >>> registry.register_hook(
            ...     name="my_hook",
            ...     hook=my_hook,
            ...     event_type="task_start",
            ...     phase=HookPhase.PRE,
            ...     priority=HookPriority.HIGH,
            ...     conditions=[lambda ctx: ctx.data.get("enable_hook", True)]
            ... )
        """
        # Validate executor exists
        if executor_type not in self._executors:
            raise ValueError(
                f"Executor '{executor_type}' not registered. "
                f"Available: {list(self._executors.keys())}"
            )

        # Check if hook already registered
        existing_hooks = self._hooks[event_type][phase]
        if any(h.name == name for h in existing_hooks):
            raise ValueError(
                f"Hook '{name}' already registered for {event_type}/{phase.value}"
            )

        # Create registration
        registration = HookRegistration(
            name=name,
            hook=hook,
            event_type=event_type,
            phase=phase,
            priority=priority,
            executor_type=executor_type,
            conditions=conditions or [],
            dependencies=dependencies or [],
            enabled=True
        )

        # Add to registry
        self._hooks[event_type][phase].append(registration)

        logger.info(
            f"Registered hook: {name} for {event_type}/{phase.value} "
            f"(priority: {priority.name}, executor: {executor_type})"
        )

    def unregister_hook(self, name: str, event_type: str, phase: HookPhase) -> bool:
        """
        Unregister hook.

        Args:
            name: Hook identifier
            event_type: Event type
            phase: Lifecycle phase

        Returns:
            True if hook was removed, False if not found

        Example:
            >>> registry.unregister_hook("my_hook", "task_start", HookPhase.PRE)
            True
        """
        hooks = self._hooks[event_type][phase]
        original_count = len(hooks)

        self._hooks[event_type][phase] = [h for h in hooks if h.name != name]

        removed = len(self._hooks[event_type][phase]) < original_count

        if removed:
            logger.info(f"Unregistered hook: {name} from {event_type}/{phase.value}")

        return removed

    def execute_hooks(
        self,
        event_type: str,
        phase: HookPhase,
        context: HookContext
    ) -> List[HookResult]:
        """
        Execute all registered hooks for event/phase.

        Execution order:
        1. Sort by priority (CRITICAL first)
        2. Check conditions (skip if any fail)
        3. Resolve dependencies (topological sort)
        4. Execute with appropriate executor

        Args:
            event_type: Event type
            phase: Lifecycle phase
            context: HookContext with event data

        Returns:
            List of HookResults (in execution order)

        Example:
            >>> context = HookContext(
            ...     phase=HookPhase.PRE,
            ...     event_type="task_start",
            ...     data={"task_id": "task-001"},
            ...     metadata={},
            ...     timestamp=time.time()
            ... )
            >>> results = registry.execute_hooks("task_start", HookPhase.PRE, context)
            >>> for result in results:
            ...     print(f"{result.success}: {result.data}")
        """
        hooks = self._hooks.get(event_type, {}).get(phase, [])

        if not hooks:
            logger.debug(f"No hooks registered for {event_type}/{phase.value}")
            return []

        logger.debug(
            f"Executing hooks for {event_type}/{phase.value}: {len(hooks)} registered"
        )

        # Filter enabled hooks
        enabled_hooks = [h for h in hooks if h.enabled]

        # Check conditions
        executable_hooks = [
            h for h in enabled_hooks
            if self._check_conditions(h, context)
        ]

        # Resolve dependencies (topological sort)
        sorted_hooks = self._resolve_dependencies(executable_hooks)

        # Execute hooks
        results = []
        for hook_reg in sorted_hooks:
            result = self._execute_single_hook(hook_reg, context)
            results.append(result)

            # Update statistics
            self._execution_counts[hook_reg.name] += 1
            if result.success:
                self._success_counts[hook_reg.name] += 1
            else:
                self._failure_counts[hook_reg.name] += 1

        successful = sum(1 for r in results if r.success)
        logger.info(
            f"Hook execution complete: {len(results)} hooks, "
            f"{successful} successful"
        )

        return results

    def _check_conditions(self, registration: HookRegistration, context: HookContext) -> bool:
        """
        Check if all conditions are met.

        Args:
            registration: HookRegistration
            context: HookContext

        Returns:
            True if all conditions pass, False otherwise
        """
        if not registration.conditions:
            return True

        try:
            for condition in registration.conditions:
                if not condition(context):
                    logger.debug(
                        f"Condition failed for hook: {registration.name}"
                    )
                    return False
            return True

        except Exception as e:
            logger.error(
                f"Condition check failed for {registration.name}: {e}"
            )
            return False

    def _resolve_dependencies(
        self,
        hooks: List[HookRegistration]
    ) -> List[HookRegistration]:
        """
        Topological sort by dependencies.

        Ensures hooks execute in correct order based on dependencies.
        Also maintains priority order within dependency groups.

        Args:
            hooks: List of HookRegistrations

        Returns:
            Sorted list of HookRegistrations

        Raises:
            ValueError: If circular dependency detected
        """
        if not hooks:
            return []

        # Create name → registration mapping
        hook_map = {h.name: h for h in hooks}

        # Build dependency graph
        graph = {h.name: h.dependencies for h in hooks}

        # Topological sort with cycle detection
        visited = set()
        temp_mark = set()
        sorted_names = []

        def visit(name: str):
            """DFS visit for topological sort"""
            if name in temp_mark:
                raise ValueError(f"Circular dependency detected: {name}")

            if name not in visited:
                temp_mark.add(name)

                # Visit dependencies first
                if name in graph:
                    for dep in graph[name]:
                        if dep in hook_map:  # Only visit if dependency is registered
                            visit(dep)

                temp_mark.remove(name)
                visited.add(name)
                sorted_names.append(name)

        # Visit all hooks
        for hook_name in hook_map.keys():
            if hook_name not in visited:
                visit(hook_name)

        # Convert names back to registrations
        sorted_hooks = [hook_map[name] for name in sorted_names if name in hook_map]

        # Sort by priority within dependency order
        # (stable sort preserves topological order)
        sorted_hooks.sort(key=lambda h: h.priority.value)

        return sorted_hooks

    def _execute_single_hook(
        self,
        registration: HookRegistration,
        context: HookContext
    ) -> HookResult:
        """
        Execute single hook with appropriate executor.

        Args:
            registration: HookRegistration
            context: HookContext

        Returns:
            HookResult
        """
        executor = self._executors.get(registration.executor_type)

        if not executor:
            logger.error(
                f"Executor not found: {registration.executor_type} for hook {registration.name}"
            )
            return HookResult(
                success=False,
                data=None,
                error=ValueError(f"Executor not found: {registration.executor_type}"),
                execution_time_ms=0.0,
                metadata={"hook_name": registration.name}
            )

        logger.debug(
            f"Executing hook: {registration.name} with {registration.executor_type}"
        )

        return executor.execute(registration.hook, context)

    def get_hook_stats(self, hook_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get hook execution statistics.

        Args:
            hook_name: Specific hook name (None for all hooks)

        Returns:
            Dict with execution statistics

        Example:
            >>> stats = registry.get_hook_stats("my_hook")
            >>> print(stats["total_executions"])
            42
        """
        if hook_name:
            executions = self._execution_counts.get(hook_name, 0)
            successes = self._success_counts.get(hook_name, 0)
            failures = self._failure_counts.get(hook_name, 0)

            return {
                "hook_name": hook_name,
                "total_executions": executions,
                "successful_executions": successes,
                "failed_executions": failures,
                "success_rate": round(successes / executions * 100, 2) if executions > 0 else 0.0
            }
        else:
            # Aggregate statistics for all hooks
            total_hooks = len(set(self._execution_counts.keys()))
            total_executions = sum(self._execution_counts.values())
            total_successes = sum(self._success_counts.values())
            total_failures = sum(self._failure_counts.values())

            return {
                "total_hooks": total_hooks,
                "total_executions": total_executions,
                "successful_executions": total_successes,
                "failed_executions": total_failures,
                "success_rate": round(total_successes / total_executions * 100, 2) if total_executions > 0 else 0.0,
                "per_hook_stats": {
                    name: self.get_hook_stats(name)
                    for name in self._execution_counts.keys()
                }
            }

    def get_registered_hooks(
        self,
        event_type: Optional[str] = None,
        phase: Optional[HookPhase] = None
    ) -> List[HookRegistration]:
        """
        Get list of registered hooks.

        Args:
            event_type: Filter by event type (None for all)
            phase: Filter by phase (None for all)

        Returns:
            List of HookRegistrations

        Example:
            >>> hooks = registry.get_registered_hooks("task_start", HookPhase.PRE)
            >>> for hook in hooks:
            ...     print(f"{hook.name}: {hook.priority.name}")
        """
        if event_type and phase:
            return self._hooks.get(event_type, {}).get(phase, []).copy()
        elif event_type:
            # All phases for event type
            result = []
            for phase_hooks in self._hooks.get(event_type, {}).values():
                result.extend(phase_hooks)
            return result
        else:
            # All hooks
            result = []
            for event_hooks in self._hooks.values():
                for phase_hooks in event_hooks.values():
                    result.extend(phase_hooks)
            return result

    def enable_hook(self, hook_name: str) -> int:
        """
        Enable hook by name.

        Args:
            hook_name: Hook identifier

        Returns:
            Number of hooks enabled

        Example:
            >>> count = registry.enable_hook("my_hook")
            >>> print(f"Enabled {count} hooks")
        """
        count = 0
        for event_hooks in self._hooks.values():
            for phase_hooks in event_hooks.values():
                for hook in phase_hooks:
                    if hook.name == hook_name:
                        hook.enabled = True
                        count += 1

        if count > 0:
            logger.info(f"Enabled {count} hooks with name: {hook_name}")

        return count

    def disable_hook(self, hook_name: str) -> int:
        """
        Disable hook by name.

        Args:
            hook_name: Hook identifier

        Returns:
            Number of hooks disabled

        Example:
            >>> count = registry.disable_hook("my_hook")
            >>> print(f"Disabled {count} hooks")
        """
        count = 0
        for event_hooks in self._hooks.values():
            for phase_hooks in event_hooks.values():
                for hook in phase_hooks:
                    if hook.name == hook_name:
                        hook.enabled = False
                        count += 1

        if count > 0:
            logger.info(f"Disabled {count} hooks with name: {hook_name}")

        return count


__all__ = [
    "HookRegistry",
    "HookPriority",
    "HookRegistration",
]
