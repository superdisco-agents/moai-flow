#!/usr/bin/env python3
"""
AsyncHookExecutor - Asynchronous Hook Executor

Asynchronous executor supporting concurrent hook execution with
asyncio. Enables batch processing and Promise-style results.

Features:
- Async/await support
- Concurrent hook execution (asyncio.gather)
- Semaphore for concurrent limit
- Timeout handling (asyncio.wait_for)
- Promise-style results
- Batch execution

Example:
    >>> import asyncio
    >>> from async_executor import AsyncHookExecutor
    >>> from hook_executor import HookContext, HookPhase
    >>>
    >>> executor = AsyncHookExecutor(
    ...     timeout_ms=5000,
    ...     concurrent_limit=10
    ... )
    >>>
    >>> async def my_async_hook(context: HookContext):
    ...     await asyncio.sleep(0.1)
    ...     return {"status": "success"}
    >>>
    >>> context = HookContext(
    ...     phase=HookPhase.POST,
    ...     event_type="task_complete",
    ...     data={"task_id": "task-001"},
    ...     metadata={},
    ...     timestamp=time.time()
    ... )
    >>>
    >>> # Synchronous wrapper
    >>> result = executor.execute(my_async_hook, context)
    >>>
    >>> # Or use async directly
    >>> async def main():
    ...     result = await executor.execute_async(my_async_hook, context)
    ...     print(result.success)
    >>>
    >>> asyncio.run(main())
"""

import asyncio
import inspect
import logging
import time
from typing import Any, Callable, List, Optional

from .hook_executor import HookContext, HookResult, IHookExecutor

logger = logging.getLogger(__name__)


class AsyncHookExecutor(IHookExecutor):
    """
    Asynchronous hook executor.

    Executes hooks asynchronously using asyncio, supporting concurrent
    execution with semaphore-based limiting and timeout handling.

    Attributes:
        timeout_ms: Async operation timeout in milliseconds
        concurrent_limit: Max concurrent hooks (default: 10)
        event_loop: Custom event loop (or create new)

    Example:
        >>> executor = AsyncHookExecutor(
        ...     timeout_ms=5000,
        ...     concurrent_limit=10
        ... )
        >>>
        >>> async def hook(ctx):
        ...     await asyncio.sleep(0.1)
        ...     return "done"
        >>>
        >>> result = await executor.execute_async(hook, context)
    """

    def __init__(
        self,
        timeout_ms: int = 5000,
        concurrent_limit: int = 10,
        event_loop: Optional[asyncio.AbstractEventLoop] = None
    ):
        """
        Initialize async executor.

        Args:
            timeout_ms: Async operation timeout (default: 5000ms)
            concurrent_limit: Max concurrent hooks (default: 10)
            event_loop: Custom event loop (or create new)

        Raises:
            ValueError: If timeout_ms < 0 or concurrent_limit < 1
        """
        if timeout_ms < 0:
            raise ValueError(f"timeout_ms must be >= 0, got {timeout_ms}")

        if concurrent_limit < 1:
            raise ValueError(f"concurrent_limit must be >= 1, got {concurrent_limit}")

        self.timeout_ms = timeout_ms
        self.concurrent_limit = concurrent_limit

        # Event loop management
        self._loop = event_loop
        self._owns_loop = event_loop is None

        # Semaphore for concurrent limit (created when loop is available)
        self._semaphore: Optional[asyncio.Semaphore] = None

        # Execution statistics
        self._total_executions = 0
        self._successful_executions = 0
        self._failed_executions = 0
        self._timeout_count = 0
        self._concurrent_peak = 0
        self._current_concurrent = 0

        logger.debug(
            f"AsyncHookExecutor initialized: timeout={timeout_ms}ms, "
            f"concurrent_limit={concurrent_limit}"
        )

    def _get_or_create_loop(self) -> asyncio.AbstractEventLoop:
        """Get or create event loop"""
        if self._loop is None:
            try:
                # Try to get running loop
                self._loop = asyncio.get_running_loop()
            except RuntimeError:
                # No running loop - create new one
                self._loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self._loop)

        # Create semaphore if not exists
        if self._semaphore is None:
            self._semaphore = asyncio.Semaphore(self.concurrent_limit)

        return self._loop

    def execute(self, hook: Callable, context: HookContext) -> HookResult:
        """
        Execute async hook (blocks until complete).

        Synchronous wrapper that runs async hook in event loop.
        Creates new event loop if none exists.

        Args:
            hook: Callable hook function (can be async or sync)
            context: HookContext with event data

        Returns:
            HookResult with execution outcome
        """
        loop = self._get_or_create_loop()

        # Check if loop is already running
        try:
            asyncio.get_running_loop()
            # Loop is running - use create_task
            task = asyncio.create_task(self.execute_async(hook, context))
            # Wait for task to complete (this will work in async context)
            return loop.run_until_complete(task)
        except RuntimeError:
            # No running loop - use run_until_complete
            return loop.run_until_complete(self.execute_async(hook, context))

    async def execute_async(self, hook: Callable, context: HookContext) -> HookResult:
        """
        Execute async hook asynchronously.

        Executes hook with timeout and concurrent limit protection.

        Args:
            hook: Callable hook function (can be async or sync)
            context: HookContext with event data

        Returns:
            HookResult with execution outcome
        """
        self._total_executions += 1
        start_time = time.time()

        # Ensure semaphore exists
        if self._semaphore is None:
            self._semaphore = asyncio.Semaphore(self.concurrent_limit)

        async with self._semaphore:
            # Track concurrent executions
            self._current_concurrent += 1
            if self._current_concurrent > self._concurrent_peak:
                self._concurrent_peak = self._current_concurrent

            try:
                # Convert sync function to async if needed
                if inspect.iscoroutinefunction(hook):
                    coro = hook(context)
                else:
                    # Wrap sync function in coroutine
                    async def _wrapper():
                        return hook(context)
                    coro = _wrapper()

                # Execute with timeout
                timeout_seconds = self.timeout_ms / 1000.0
                result = await asyncio.wait_for(coro, timeout=timeout_seconds)

                execution_time_ms = (time.time() - start_time) * 1000

                self._successful_executions += 1

                return HookResult(
                    success=True,
                    data=result,
                    error=None,
                    execution_time_ms=execution_time_ms,
                    metadata={
                        "executor": "async",
                        "timeout_ms": self.timeout_ms,
                        "concurrent_limit": self.concurrent_limit
                    }
                )

            except asyncio.TimeoutError as e:
                self._timeout_count += 1
                self._failed_executions += 1
                execution_time_ms = (time.time() - start_time) * 1000

                logger.warning(
                    f"Async hook timeout: {context.event_type} ({execution_time_ms:.2f}ms)"
                )

                return HookResult(
                    success=False,
                    data=None,
                    error=e,
                    execution_time_ms=execution_time_ms,
                    metadata={
                        "executor": "async",
                        "timeout_ms": self.timeout_ms,
                        "error_type": "timeout"
                    }
                )

            except Exception as e:
                self._failed_executions += 1
                execution_time_ms = (time.time() - start_time) * 1000

                logger.error(
                    f"Async hook execution failed: {context.event_type} - "
                    f"{type(e).__name__}: {e}"
                )

                return HookResult(
                    success=False,
                    data=None,
                    error=e,
                    execution_time_ms=execution_time_ms,
                    metadata={
                        "executor": "async",
                        "error_type": type(e).__name__
                    }
                )

            finally:
                self._current_concurrent -= 1

    async def execute_batch(
        self,
        hooks: List[Callable],
        context: HookContext
    ) -> List[HookResult]:
        """
        Execute multiple hooks concurrently.

        Runs all hooks in parallel (up to concurrent_limit) and returns
        results in same order as input.

        Args:
            hooks: List of callable hook functions
            context: HookContext (shared across all hooks)

        Returns:
            List of HookResults (same order as input)

        Example:
            >>> hooks = [hook1, hook2, hook3]
            >>> results = await executor.execute_batch(hooks, context)
            >>> for result in results:
            ...     print(result.success)
        """
        if not hooks:
            return []

        logger.debug(f"Executing batch of {len(hooks)} hooks")

        # Execute all hooks concurrently
        tasks = [self.execute_async(hook, context) for hook in hooks]

        # Gather results (preserves order)
        results = await asyncio.gather(*tasks, return_exceptions=False)

        logger.debug(
            f"Batch execution complete: {len(results)} results, "
            f"success: {sum(1 for r in results if r.success)}"
        )

        return results

    def supports_async(self) -> bool:
        """
        Check if executor supports async hooks.

        Returns:
            True (async executor)
        """
        return True

    def get_timeout_ms(self) -> Optional[int]:
        """
        Get default timeout in milliseconds.

        Returns:
            Timeout in ms
        """
        return self.timeout_ms

    def get_stats(self) -> dict:
        """
        Get executor statistics.

        Returns:
            Dict with execution statistics
        """
        success_rate = (
            self._successful_executions / self._total_executions * 100
            if self._total_executions > 0
            else 0.0
        )

        return {
            "total_executions": self._total_executions,
            "successful_executions": self._successful_executions,
            "failed_executions": self._failed_executions,
            "timeout_count": self._timeout_count,
            "success_rate": round(success_rate, 2),
            "concurrent_peak": self._concurrent_peak,
            "current_concurrent": self._current_concurrent,
            "timeout_ms": self.timeout_ms,
            "concurrent_limit": self.concurrent_limit
        }

    async def close(self):
        """Close executor and cleanup resources"""
        if self._owns_loop and self._loop and not self._loop.is_closed():
            self._loop.close()
            logger.debug("AsyncHookExecutor event loop closed")


__all__ = ["AsyncHookExecutor"]
