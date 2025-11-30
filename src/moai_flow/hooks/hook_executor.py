#!/usr/bin/env python3
"""
Hook Executor Interface and Supporting Types

Abstract base class for hook execution with different execution strategies.
Supports synchronous, asynchronous, and custom executor implementations.

Key Concepts:
- HookPhase: Pre/Post/Error lifecycle phases
- HookContext: Contextual data passed to hooks
- HookResult: Standardized execution result
- IHookExecutor: Abstract executor interface

Example:
    >>> from hook_executor import StandardHookExecutor, HookContext, HookPhase
    >>> executor = StandardHookExecutor(timeout_ms=2000)
    >>> context = HookContext(
    ...     phase=HookPhase.PRE,
    ...     event_type="task_start",
    ...     data={"task_id": "task-001"},
    ...     metadata={},
    ...     timestamp=time.time()
    ... )
    >>> result = executor.execute(my_hook_function, context)
    >>> print(result.success)
    True
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, Optional
import time


class HookPhase(Enum):
    """Hook execution phase in lifecycle."""
    PRE = "pre"      # Before operation
    POST = "post"    # After operation
    ERROR = "error"  # On error/exception


@dataclass
class HookContext:
    """
    Context passed to hooks during execution.

    Contains all relevant information about the event being processed,
    including phase, event type, data, metadata, and timing.

    Attributes:
        phase: Lifecycle phase (PRE, POST, ERROR)
        event_type: Type of event (e.g., "task_start", "agent_spawn")
        data: Event-specific data payload
        metadata: Additional metadata (user-defined)
        timestamp: Event timestamp (Unix time)

    Example:
        >>> context = HookContext(
        ...     phase=HookPhase.PRE,
        ...     event_type="task_start",
        ...     data={"task_id": "task-001", "agent_type": "expert-backend"},
        ...     metadata={"priority": 1},
        ...     timestamp=time.time()
        ... )
    """
    phase: HookPhase
    event_type: str
    data: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

    def __post_init__(self):
        """Ensure phase is HookPhase enum"""
        if isinstance(self.phase, str):
            self.phase = HookPhase(self.phase.lower())


@dataclass
class HookResult:
    """
    Result from hook execution.

    Standardized result format for all hook executions, including
    success status, data, errors, execution time, and metadata.

    Attributes:
        success: Whether hook executed successfully
        data: Hook result data (can be None)
        error: Exception if hook failed (None on success)
        execution_time_ms: Execution duration in milliseconds
        metadata: Additional result metadata

    Example:
        >>> result = HookResult(
        ...     success=True,
        ...     data={"validation": "passed"},
        ...     error=None,
        ...     execution_time_ms=125.5,
        ...     metadata={"retries": 0}
        ... )
    """
    success: bool
    data: Optional[Any] = None
    error: Optional[Exception] = None
    execution_time_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary for serialization"""
        return {
            "success": self.success,
            "data": self.data,
            "error": str(self.error) if self.error else None,
            "error_type": type(self.error).__name__ if self.error else None,
            "execution_time_ms": self.execution_time_ms,
            "metadata": self.metadata
        }


class IHookExecutor(ABC):
    """
    Abstract base class for hook executors.

    Defines interface for executing hooks with different strategies:
    - Synchronous execution (StandardHookExecutor)
    - Asynchronous execution (AsyncHookExecutor)
    - Custom execution (user-defined)

    All executors must implement:
    - execute(): Execute hook with given context
    - supports_async(): Whether executor supports async hooks
    - get_timeout_ms(): Default timeout in milliseconds

    Example:
        >>> class CustomExecutor(IHookExecutor):
        ...     def execute(self, hook: Callable, context: HookContext) -> HookResult:
        ...         # Custom execution logic
        ...         pass
        ...
        ...     def supports_async(self) -> bool:
        ...         return False
        ...
        ...     def get_timeout_ms(self) -> Optional[int]:
        ...         return 5000
    """

    @abstractmethod
    def execute(self, hook: Callable, context: HookContext) -> HookResult:
        """
        Execute hook with given context.

        Args:
            hook: Callable hook function to execute
            context: HookContext with event data

        Returns:
            HookResult with execution outcome

        Raises:
            Implementation-specific exceptions
        """
        pass

    @abstractmethod
    def supports_async(self) -> bool:
        """
        Check if executor supports async hooks.

        Returns:
            True if async hooks supported, False otherwise
        """
        pass

    @abstractmethod
    def get_timeout_ms(self) -> Optional[int]:
        """
        Get default timeout in milliseconds.

        Returns:
            Timeout in ms, or None for no timeout
        """
        pass


# Convenience type aliases
HookFunction = Callable[[HookContext], Any]
AsyncHookFunction = Callable[[HookContext], Any]  # Can be async or sync


__all__ = [
    "HookPhase",
    "HookContext",
    "HookResult",
    "IHookExecutor",
    "HookFunction",
    "AsyncHookFunction",
]
