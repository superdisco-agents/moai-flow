#!/usr/bin/env python3
"""
PostTask Pattern Hook - Automatic Pattern Collection

Integrates pattern collection with Phase 7 hooks system.
Automatically collects patterns after each task completion.

Features:
- PostTask hook for task completion patterns
- Error hook for error occurrence patterns
- Graceful degradation on errors
- Hook registration helper

Example:
    >>> from moai_flow.hooks import HookRegistry
    >>> from moai_flow.hooks.post_task_pattern import register_pattern_hooks
    >>>
    >>> registry = HookRegistry()
    >>> register_pattern_hooks(registry)
    >>>
    >>> # Hooks will automatically collect patterns on task completion
"""

import logging
from typing import Optional

from ..patterns.pattern_collector import PatternCollector
from .hook_executor import HookContext, HookResult, HookPhase

logger = logging.getLogger(__name__)


class PostTaskPatternHook:
    """
    PostTask hook for automatic pattern collection.

    Collects task completion patterns after each task execution.
    Integrates seamlessly with Phase 7 hook system.

    Example:
        >>> from moai_flow.patterns.pattern_collector import PatternCollector
        >>> collector = PatternCollector()
        >>> hook = PostTaskPatternHook(collector)
        >>> result = hook(context)
        >>> print(result.success)
        True
    """

    def __init__(
        self,
        collector: Optional[PatternCollector] = None,
        enabled: bool = True
    ):
        """
        Initialize PostTask pattern hook.

        Args:
            collector: PatternCollector instance (creates default if None)
            enabled: Enable/disable pattern collection
        """
        self.collector = collector or PatternCollector()
        self.enabled = enabled

        logger.debug(
            f"PostTaskPatternHook initialized: enabled={self.enabled}"
        )

    def __call__(self, context: HookContext) -> HookResult:
        """
        Execute PostTask pattern collection.

        Args:
            context: Hook execution context containing:
                - event_type: "task_complete"
                - data: {task_id, agent_id, duration_ms, success, ...}
                - metadata: Additional context

        Returns:
            HookResult with pattern_id in metadata

        Example:
            >>> context = HookContext(
            ...     phase=HookPhase.POST,
            ...     event_type="task_complete",
            ...     data={
            ...         "task_type": "api_implementation",
            ...         "agent_id": "expert-backend",
            ...         "duration_ms": 45000,
            ...         "success": True,
            ...         "files_created": 3,
            ...         "tests_passed": 12
            ...     },
            ...     metadata={"framework": "fastapi"}
            ... )
            >>> result = hook(context)
            >>> print(result.metadata["pattern_id"])
            task-abc123
        """
        if not self.enabled:
            logger.debug("PostTaskPatternHook disabled, skipping")
            return HookResult(
                success=True,
                data=None,
                metadata={"skipped": True}
            )

        try:
            # Extract task data
            task_data = context.data

            # Collect pattern
            pattern_id = self.collector.collect_task_completion(
                task_type=task_data.get("task_type", "unknown"),
                agent=task_data.get("agent_id", "unknown"),
                duration_ms=task_data.get("duration_ms", 0),
                success=task_data.get("success", False),
                files_created=task_data.get("files_created", 0),
                tests_passed=task_data.get("tests_passed", 0),
                context=context.metadata
            )

            logger.debug(f"Pattern collected: {pattern_id}")

            return HookResult(
                success=True,
                data=None,
                metadata={"pattern_id": pattern_id}
            )

        except Exception as e:
            # Graceful degradation - don't fail task on pattern error
            logger.warning(f"Pattern collection failed: {e}")
            return HookResult(
                success=False,
                error=e,
                metadata={"error": str(e)}
            )


class ErrorPatternHook:
    """
    Error hook for collecting error patterns.

    Collects error occurrence patterns when tasks fail.
    Integrates with Phase 7 ERROR phase hooks.

    Example:
        >>> collector = PatternCollector()
        >>> hook = ErrorPatternHook(collector)
        >>> result = hook(error_context)
        >>> print(result.metadata["pattern_id"])
        error-xyz789
    """

    def __init__(
        self,
        collector: Optional[PatternCollector] = None,
        enabled: bool = True
    ):
        """
        Initialize error pattern hook.

        Args:
            collector: PatternCollector instance (creates default if None)
            enabled: Enable/disable pattern collection
        """
        self.collector = collector or PatternCollector()
        self.enabled = enabled

        logger.debug(
            f"ErrorPatternHook initialized: enabled={self.enabled}"
        )

    def __call__(self, context: HookContext) -> HookResult:
        """
        Execute error pattern collection.

        Args:
            context: Hook execution context containing:
                - event_type: "task_failed"
                - data: {error_type, error_message, ...}
                - metadata: Additional context

        Returns:
            HookResult with pattern_id in metadata

        Example:
            >>> context = HookContext(
            ...     phase=HookPhase.ERROR,
            ...     event_type="task_failed",
            ...     data={
            ...         "error_type": "ValidationError",
            ...         "error_message": "Invalid API key",
            ...         "resolution": "Added validation"
            ...     },
            ...     metadata={"endpoint": "/api/v1/users"}
            ... )
            >>> result = hook(context)
            >>> print(result.metadata["pattern_id"])
            error-xyz789
        """
        if not self.enabled:
            logger.debug("ErrorPatternHook disabled, skipping")
            return HookResult(
                success=True,
                data=None,
                metadata={"skipped": True}
            )

        try:
            # Extract error data
            error_data = context.data

            # Collect error pattern
            pattern_id = self.collector.collect_error_occurrence(
                error_type=error_data.get("error_type", "unknown"),
                error_message=error_data.get("error_message", ""),
                context=context.metadata,
                resolution=error_data.get("resolution")
            )

            logger.debug(f"Error pattern collected: {pattern_id}")

            return HookResult(
                success=True,
                data=None,
                metadata={"pattern_id": pattern_id}
            )

        except Exception as e:
            # Graceful degradation
            logger.warning(f"Error pattern collection failed: {e}")
            return HookResult(
                success=False,
                error=e,
                metadata={"error": str(e)}
            )


def register_pattern_hooks(
    hook_registry,
    collector: Optional[PatternCollector] = None,
    enabled: bool = True
) -> None:
    """
    Register pattern collection hooks with HookRegistry.

    Registers both PostTask and Error pattern hooks with appropriate
    priorities and phases.

    Args:
        hook_registry: HookRegistry instance from Phase 7
        collector: PatternCollector instance (creates default if None)
        enabled: Enable/disable pattern collection hooks

    Example:
        >>> from moai_flow.hooks import HookRegistry
        >>> from moai_flow.hooks.post_task_pattern import register_pattern_hooks
        >>>
        >>> registry = HookRegistry()
        >>> register_pattern_hooks(registry)
        >>>
        >>> # Hooks are now registered and will collect patterns automatically
    """
    from .hook_registry import HookPriority

    if not enabled:
        logger.info("Pattern hooks registration skipped (disabled)")
        return

    # Initialize collector if not provided
    if collector is None:
        collector = PatternCollector()

    # Register PostTask hook
    try:
        hook_registry.register_hook(
            name="post_task_pattern_collection",
            hook=PostTaskPatternHook(collector, enabled=enabled),
            event_type="task_complete",
            phase=HookPhase.POST,
            priority=HookPriority.LOW  # Run after other hooks
        )
        logger.info("Registered PostTask pattern collection hook")

    except Exception as e:
        logger.error(f"Failed to register PostTask pattern hook: {e}")

    # Register error hook
    try:
        hook_registry.register_hook(
            name="error_pattern_collection",
            hook=ErrorPatternHook(collector, enabled=enabled),
            event_type="task_failed",
            phase=HookPhase.ERROR,
            priority=HookPriority.LOW  # Run after other error hooks
        )
        logger.info("Registered error pattern collection hook")

    except Exception as e:
        logger.error(f"Failed to register error pattern hook: {e}")


__all__ = [
    "PostTaskPatternHook",
    "ErrorPatternHook",
    "register_pattern_hooks",
]
