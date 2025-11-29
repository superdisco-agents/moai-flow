#!/usr/bin/env python3
"""
StandardHookExecutor - Synchronous Hook Executor

Default synchronous executor with timeout management, retry logic,
and graceful degradation. Suitable for most non-async hooks.

Features:
- Timeout management using threading
- Configurable retry logic (0-3 retries)
- Graceful degradation (continue on failure vs raise)
- Execution time tracking
- Thread-safe execution

Example:
    >>> from standard_executor import StandardHookExecutor
    >>> from hook_executor import HookContext, HookPhase
    >>>
    >>> executor = StandardHookExecutor(
    ...     timeout_ms=2000,
    ...     graceful_degradation=True,
    ...     max_retries=2
    ... )
    >>>
    >>> def my_hook(context: HookContext):
    ...     print(f"Processing {context.event_type}")
    ...     return {"status": "success"}
    >>>
    >>> context = HookContext(
    ...     phase=HookPhase.PRE,
    ...     event_type="task_start",
    ...     data={"task_id": "task-001"},
    ...     metadata={},
    ...     timestamp=time.time()
    ... )
    >>>
    >>> result = executor.execute(my_hook, context)
    >>> print(result.success)
    True
"""

import logging
import queue
import threading
import time
from typing import Any, Callable, Optional

from .hook_executor import HookContext, HookResult, IHookExecutor

logger = logging.getLogger(__name__)


class TimeoutException(Exception):
    """Exception raised when hook execution times out"""
    pass


class StandardHookExecutor(IHookExecutor):
    """
    Default synchronous hook executor.

    Executes hooks synchronously with timeout protection, retry logic,
    and graceful degradation. Uses threading for timeout management.

    Attributes:
        timeout_ms: Hook execution timeout in milliseconds
        graceful_degradation: Continue on failure (True) vs raise (False)
        max_retries: Number of retries on failure (0-3)

    Example:
        >>> executor = StandardHookExecutor(
        ...     timeout_ms=2000,
        ...     graceful_degradation=True,
        ...     max_retries=1
        ... )
        >>> result = executor.execute(my_hook, context)
    """

    def __init__(
        self,
        timeout_ms: int = 2000,
        graceful_degradation: bool = True,
        max_retries: int = 0
    ):
        """
        Initialize executor.

        Args:
            timeout_ms: Hook execution timeout (default: 2000ms)
            graceful_degradation: Continue on failure vs raise (default: True)
            max_retries: Number of retries on failure (default: 0, max: 3)

        Raises:
            ValueError: If max_retries > 3 or timeout_ms < 0
        """
        if timeout_ms < 0:
            raise ValueError(f"timeout_ms must be >= 0, got {timeout_ms}")

        if max_retries < 0 or max_retries > 3:
            raise ValueError(f"max_retries must be 0-3, got {max_retries}")

        self.timeout_ms = timeout_ms
        self.graceful_degradation = graceful_degradation
        self.max_retries = max_retries

        # Execution statistics
        self._total_executions = 0
        self._successful_executions = 0
        self._failed_executions = 0
        self._timeout_count = 0
        self._retry_count = 0

        logger.debug(
            f"StandardHookExecutor initialized: timeout={timeout_ms}ms, "
            f"graceful={graceful_degradation}, retries={max_retries}"
        )

    def execute(self, hook: Callable, context: HookContext) -> HookResult:
        """
        Execute hook synchronously with timeout.

        Args:
            hook: Callable hook function
            context: HookContext with event data

        Returns:
            HookResult with execution outcome

        Raises:
            TimeoutException: If hook times out and graceful_degradation=False
            Exception: If hook fails and graceful_degradation=False
        """
        self._total_executions += 1
        start_time = time.time()

        try:
            # Execute with retries if configured
            if self.max_retries > 0:
                result = self._retry_on_failure(hook, context)
            else:
                result = self._execute_with_timeout(hook, context)

            execution_time_ms = (time.time() - start_time) * 1000

            self._successful_executions += 1

            return HookResult(
                success=True,
                data=result,
                error=None,
                execution_time_ms=execution_time_ms,
                metadata={
                    "executor": "standard",
                    "timeout_ms": self.timeout_ms,
                    "retries_used": 0
                }
            )

        except TimeoutException as e:
            self._timeout_count += 1
            self._failed_executions += 1
            execution_time_ms = (time.time() - start_time) * 1000

            logger.warning(
                f"Hook timeout: {context.event_type} ({execution_time_ms:.2f}ms)"
            )

            if not self.graceful_degradation:
                raise

            return HookResult(
                success=False,
                data=None,
                error=e,
                execution_time_ms=execution_time_ms,
                metadata={
                    "executor": "standard",
                    "timeout_ms": self.timeout_ms,
                    "error_type": "timeout"
                }
            )

        except Exception as e:
            self._failed_executions += 1
            execution_time_ms = (time.time() - start_time) * 1000

            logger.error(
                f"Hook execution failed: {context.event_type} - {type(e).__name__}: {e}"
            )

            if not self.graceful_degradation:
                raise

            return HookResult(
                success=False,
                data=None,
                error=e,
                execution_time_ms=execution_time_ms,
                metadata={
                    "executor": "standard",
                    "error_type": type(e).__name__
                }
            )

    def _execute_with_timeout(self, hook: Callable, context: HookContext) -> Any:
        """
        Execute hook with timeout using threading.

        Args:
            hook: Callable hook function
            context: HookContext

        Returns:
            Hook result

        Raises:
            TimeoutException: If execution exceeds timeout
            Exception: If hook raises exception
        """
        result_queue = queue.Queue()
        exception_queue = queue.Queue()

        def target():
            """Worker thread function"""
            try:
                result = hook(context)
                result_queue.put(result)
            except Exception as e:
                exception_queue.put(e)

        # Start worker thread
        thread = threading.Thread(target=target, daemon=True)
        thread.start()

        # Wait for completion or timeout
        timeout_seconds = self.timeout_ms / 1000.0
        thread.join(timeout=timeout_seconds)

        # Check if thread completed
        if thread.is_alive():
            # Thread still running - timeout
            raise TimeoutException(
                f"Hook execution exceeded timeout of {self.timeout_ms}ms"
            )

        # Check for exception
        if not exception_queue.empty():
            raise exception_queue.get()

        # Get result
        if not result_queue.empty():
            return result_queue.get()

        # No result and no exception - hook returned None
        return None

    def _retry_on_failure(self, hook: Callable, context: HookContext) -> Any:
        """
        Execute hook with retry logic.

        Args:
            hook: Callable hook function
            context: HookContext

        Returns:
            Hook result

        Raises:
            Exception: If all retries exhausted
        """
        last_exception = None

        for attempt in range(self.max_retries + 1):
            try:
                if attempt > 0:
                    self._retry_count += 1
                    logger.debug(
                        f"Retrying hook {context.event_type} (attempt {attempt + 1})"
                    )

                result = self._execute_with_timeout(hook, context)
                return result

            except Exception as e:
                last_exception = e

                if attempt < self.max_retries:
                    # Exponential backoff: 100ms, 200ms, 400ms
                    backoff_ms = 100 * (2 ** attempt)
                    time.sleep(backoff_ms / 1000.0)
                else:
                    # All retries exhausted
                    logger.error(
                        f"Hook {context.event_type} failed after {attempt + 1} attempts"
                    )
                    raise last_exception

        # Should never reach here
        if last_exception:
            raise last_exception

        return None

    def supports_async(self) -> bool:
        """
        Check if executor supports async hooks.

        Returns:
            False (synchronous executor only)
        """
        return False

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
            "retry_count": self._retry_count,
            "success_rate": round(success_rate, 2),
            "timeout_ms": self.timeout_ms,
            "max_retries": self.max_retries,
            "graceful_degradation": self.graceful_degradation
        }


__all__ = ["StandardHookExecutor", "TimeoutException"]
