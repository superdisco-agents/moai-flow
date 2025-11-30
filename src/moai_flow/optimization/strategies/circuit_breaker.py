#!/usr/bin/env python3
"""
Circuit Breaker Strategy for Self-Healing
==========================================

Implements the circuit breaker pattern to prevent cascading failures
and provide fail-fast behavior when a component is consistently failing.

Circuit States:
- CLOSED: Normal operation, requests pass through
- OPEN: Failing, reject requests immediately (fail-fast)
- HALF_OPEN: Testing recovery, limited requests allowed

Key Features:
- Automatic state transitions based on failure/success thresholds
- Configurable timeout before retry attempts
- Limited request allowance in HALF_OPEN state
- Thread-safe state management
- Per-agent circuit tracking

Example:
    >>> config = CircuitBreakerConfig(
    ...     failure_threshold=5,
    ...     success_threshold=2,
    ...     timeout_seconds=60.0
    ... )
    >>> strategy = CircuitBreakerStrategy(config)
    >>> failure = Failure(
    ...     failure_id="f1",
    ...     failure_type="agent_failed",
    ...     agent_id="agent-001",
    ...     severity="high",
    ...     detected_at=datetime.now(timezone.utc),
    ...     event={"type": "agent_failed"}
    ... )
    >>> result = strategy.heal(failure, coordinator)

Version: 1.0.0
Phase: 7 (Track 3 Week 4-6)
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, Optional, Any
from datetime import datetime, timezone
import time
import logging
import threading

from ..self_healer import Failure, HealingResult

logger = logging.getLogger(__name__)


# ============================================================================
# Circuit Breaker State and Configuration
# ============================================================================

class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"        # Normal operation
    OPEN = "open"            # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing recovery


@dataclass
class CircuitBreakerConfig:
    """
    Circuit breaker configuration.

    Attributes:
        failure_threshold: Number of consecutive failures before opening circuit
        success_threshold: Number of consecutive successes to close from half-open
        timeout_seconds: Time to wait before transitioning OPEN → HALF_OPEN
        half_open_max_calls: Maximum calls allowed in HALF_OPEN state
    """
    failure_threshold: int = 5
    success_threshold: int = 2
    timeout_seconds: float = 60.0
    half_open_max_calls: int = 3


# ============================================================================
# Circuit Breaker Strategy Implementation
# ============================================================================

class CircuitBreakerStrategy:
    """
    Circuit breaker pattern for failing agents/tasks.

    Prevents cascading failures by:
    1. Detecting repeated failures
    2. Opening circuit (fail-fast mode)
    3. Attempting recovery after timeout
    4. Closing circuit on successful recovery

    State Machine:
        CLOSED --[failures >= threshold]--> OPEN
        OPEN --[timeout elapsed]--> HALF_OPEN
        HALF_OPEN --[successes >= threshold]--> CLOSED
        HALF_OPEN --[any failure]--> OPEN

    Thread-safe for concurrent access.
    """

    def __init__(self, config: Optional[CircuitBreakerConfig] = None):
        """
        Initialize circuit breaker strategy.

        Args:
            config: Circuit breaker configuration (uses defaults if None)
        """
        self.config = config or CircuitBreakerConfig()

        # Circuit state per agent/resource
        self._circuits: Dict[str, CircuitState] = {}
        self._failure_counts: Dict[str, int] = {}
        self._success_counts: Dict[str, int] = {}
        self._last_failure_time: Dict[str, float] = {}
        self._half_open_calls: Dict[str, int] = {}

        # Thread safety
        self._lock = threading.RLock()

        logger.info(
            f"CircuitBreakerStrategy initialized "
            f"(failure_threshold={self.config.failure_threshold}, "
            f"success_threshold={self.config.success_threshold}, "
            f"timeout={self.config.timeout_seconds}s)"
        )

    def can_heal(self, failure: Failure) -> bool:
        """
        Check if this strategy can handle the failure.

        Handles repeated failures that indicate a systemic problem:
        - agent_failed (repeated agent failures)
        - task_timeout (repeated task timeouts)
        - execution_error (repeated execution errors)
        - agent_down (agent health failures)

        Args:
            failure: Failure to check

        Returns:
            True if strategy is applicable
        """
        return failure.failure_type in [
            "agent_failed",
            "task_timeout",
            "execution_error",
            "agent_down",
            "heartbeat_failed"
        ]

    def heal(self, failure: Failure, coordinator) -> HealingResult:
        """
        Apply circuit breaker logic.

        State-based behavior:
        1. CLOSED state:
           - Allow request
           - Increment failure count on error
           - Open circuit if threshold exceeded

        2. OPEN state:
           - Reject request (fail-fast)
           - Check if timeout elapsed → HALF_OPEN

        3. HALF_OPEN state:
           - Allow limited requests
           - Increment success count on success
           - Close circuit if success threshold reached
           - Re-open on any failure

        Args:
            failure: Failure to heal
            coordinator: SwarmCoordinator for agent management

        Returns:
            HealingResult with outcome
        """
        start_time = time.time()
        actions = []

        # Get resource identifier (agent_id or generic)
        resource_id = failure.agent_id or f"resource_{failure.failure_type}"

        with self._lock:
            # Get current circuit state
            current_state = self._get_or_create_circuit(resource_id)
            actions.append(f"Circuit state: {current_state.value}")

            # State machine logic
            if current_state == CircuitState.CLOSED:
                result = self._handle_closed_state(
                    resource_id, failure, coordinator, actions, start_time
                )
            elif current_state == CircuitState.OPEN:
                result = self._handle_open_state(
                    resource_id, failure, actions, start_time
                )
            elif current_state == CircuitState.HALF_OPEN:
                result = self._handle_half_open_state(
                    resource_id, failure, coordinator, actions, start_time
                )
            else:
                # Unknown state, reset to closed
                self._transition_to_closed(resource_id)
                result = HealingResult(
                    success=False,
                    failure_id=failure.failure_id,
                    strategy_used="CircuitBreakerStrategy",
                    actions_taken=actions + ["Unknown state, reset to CLOSED"],
                    duration_ms=int((time.time() - start_time) * 1000),
                    timestamp=datetime.now(timezone.utc),
                    metadata={"circuit_state": "reset"}
                )

        return result

    def _get_or_create_circuit(self, resource_id: str) -> CircuitState:
        """
        Get circuit state, creating if needed.

        Args:
            resource_id: Resource identifier

        Returns:
            Current circuit state
        """
        if resource_id not in self._circuits:
            self._circuits[resource_id] = CircuitState.CLOSED
            self._failure_counts[resource_id] = 0
            self._success_counts[resource_id] = 0
            self._half_open_calls[resource_id] = 0
            logger.debug(f"Created new circuit for {resource_id}")

        return self._circuits[resource_id]

    def _handle_closed_state(
        self,
        resource_id: str,
        failure: Failure,
        coordinator,
        actions: list,
        start_time: float
    ) -> HealingResult:
        """
        Handle failure in CLOSED state.

        Logic:
        1. Allow request (record failure)
        2. Increment failure count
        3. If threshold exceeded, transition to OPEN

        Args:
            resource_id: Resource identifier
            failure: Failure to handle
            coordinator: SwarmCoordinator
            actions: Action log
            start_time: Timing start

        Returns:
            HealingResult
        """
        # Record failure
        self.record_failure(resource_id)
        actions.append(
            f"Recorded failure {self._failure_counts[resource_id]}/"
            f"{self.config.failure_threshold}"
        )

        # Check if threshold exceeded
        if self._failure_counts[resource_id] >= self.config.failure_threshold:
            self._transition_to_open(resource_id)
            actions.append(
                f"Threshold exceeded, opened circuit for {resource_id}"
            )

            return HealingResult(
                success=False,
                failure_id=failure.failure_id,
                strategy_used="CircuitBreakerStrategy",
                actions_taken=actions,
                duration_ms=int((time.time() - start_time) * 1000),
                timestamp=datetime.now(timezone.utc),
                metadata={
                    "circuit_state": "opened",
                    "failure_count": self._failure_counts[resource_id],
                    "resource_id": resource_id
                }
            )
        else:
            # Still in CLOSED, allow through
            actions.append("Circuit still closed, allowing request")
            return HealingResult(
                success=True,
                failure_id=failure.failure_id,
                strategy_used="CircuitBreakerStrategy",
                actions_taken=actions,
                duration_ms=int((time.time() - start_time) * 1000),
                timestamp=datetime.now(timezone.utc),
                metadata={
                    "circuit_state": "closed",
                    "failure_count": self._failure_counts[resource_id],
                    "resource_id": resource_id
                }
            )

    def _handle_open_state(
        self,
        resource_id: str,
        failure: Failure,
        actions: list,
        start_time: float
    ) -> HealingResult:
        """
        Handle failure in OPEN state.

        Logic:
        1. Check if timeout elapsed
        2. If elapsed → transition to HALF_OPEN
        3. If not elapsed → reject request (fail-fast)

        Args:
            resource_id: Resource identifier
            failure: Failure to handle
            actions: Action log
            start_time: Timing start

        Returns:
            HealingResult
        """
        current_time = time.time()
        last_failure = self._last_failure_time.get(resource_id, 0)
        elapsed = current_time - last_failure

        # Check if timeout elapsed
        if elapsed >= self.config.timeout_seconds:
            self._transition_to_half_open(resource_id)
            actions.append(
                f"Timeout elapsed ({elapsed:.1f}s), "
                f"transitioning to HALF_OPEN"
            )

            return HealingResult(
                success=True,
                failure_id=failure.failure_id,
                strategy_used="CircuitBreakerStrategy",
                actions_taken=actions,
                duration_ms=int((time.time() - start_time) * 1000),
                timestamp=datetime.now(timezone.utc),
                metadata={
                    "circuit_state": "half_open",
                    "elapsed_seconds": elapsed,
                    "resource_id": resource_id
                }
            )
        else:
            # Reject request (fail-fast)
            remaining = self.config.timeout_seconds - elapsed
            actions.append(
                f"Circuit OPEN, rejecting request "
                f"(retry in {remaining:.1f}s)"
            )

            return HealingResult(
                success=False,
                failure_id=failure.failure_id,
                strategy_used="CircuitBreakerStrategy",
                actions_taken=actions,
                duration_ms=int((time.time() - start_time) * 1000),
                timestamp=datetime.now(timezone.utc),
                metadata={
                    "circuit_state": "open",
                    "remaining_timeout_seconds": remaining,
                    "resource_id": resource_id,
                    "fail_fast": True
                }
            )

    def _handle_half_open_state(
        self,
        resource_id: str,
        failure: Failure,
        coordinator,
        actions: list,
        start_time: float
    ) -> HealingResult:
        """
        Handle failure in HALF_OPEN state.

        Logic:
        1. Check if max calls exceeded
        2. If exceeded → back to OPEN
        3. Allow limited requests
        4. On success → increment success count
        5. If success threshold reached → transition to CLOSED
        6. On any failure → back to OPEN

        Args:
            resource_id: Resource identifier
            failure: Failure to handle
            coordinator: SwarmCoordinator
            actions: Action log
            start_time: Timing start

        Returns:
            HealingResult
        """
        # Check if max calls exceeded
        if self._half_open_calls[resource_id] >= self.config.half_open_max_calls:
            self._transition_to_open(resource_id)
            actions.append(
                f"Max calls exceeded in HALF_OPEN, "
                f"reopening circuit"
            )

            return HealingResult(
                success=False,
                failure_id=failure.failure_id,
                strategy_used="CircuitBreakerStrategy",
                actions_taken=actions,
                duration_ms=int((time.time() - start_time) * 1000),
                timestamp=datetime.now(timezone.utc),
                metadata={
                    "circuit_state": "reopened",
                    "resource_id": resource_id,
                    "reason": "max_calls_exceeded"
                }
            )

        # Allow limited request
        self._half_open_calls[resource_id] += 1
        actions.append(
            f"HALF_OPEN call {self._half_open_calls[resource_id]}/"
            f"{self.config.half_open_max_calls}"
        )

        # Failure in HALF_OPEN → back to OPEN
        self.record_failure(resource_id)
        self._transition_to_open(resource_id)
        actions.append("Failure in HALF_OPEN, reopening circuit")

        return HealingResult(
            success=False,
            failure_id=failure.failure_id,
            strategy_used="CircuitBreakerStrategy",
            actions_taken=actions,
            duration_ms=int((time.time() - start_time) * 1000),
            timestamp=datetime.now(timezone.utc),
            metadata={
                "circuit_state": "reopened",
                "resource_id": resource_id,
                "reason": "failure_in_half_open"
            }
        )

    def _transition_to_open(self, resource_id: str) -> None:
        """
        Transition circuit to OPEN state.

        Args:
            resource_id: Resource identifier
        """
        self._circuits[resource_id] = CircuitState.OPEN
        self._last_failure_time[resource_id] = time.time()
        self._half_open_calls[resource_id] = 0
        self._success_counts[resource_id] = 0
        logger.warning(f"Circuit OPENED for {resource_id}")

    def _transition_to_half_open(self, resource_id: str) -> None:
        """
        Transition circuit to HALF_OPEN state.

        Args:
            resource_id: Resource identifier
        """
        self._circuits[resource_id] = CircuitState.HALF_OPEN
        self._half_open_calls[resource_id] = 0
        self._failure_counts[resource_id] = 0
        logger.info(f"Circuit HALF_OPEN for {resource_id}")

    def _transition_to_closed(self, resource_id: str) -> None:
        """
        Transition circuit to CLOSED state.

        Args:
            resource_id: Resource identifier
        """
        self._circuits[resource_id] = CircuitState.CLOSED
        self._failure_counts[resource_id] = 0
        self._success_counts[resource_id] = 0
        self._half_open_calls[resource_id] = 0
        logger.info(f"Circuit CLOSED for {resource_id}")

    def record_success(self, resource_id: str) -> None:
        """
        Record successful execution.

        Used to transition HALF_OPEN → CLOSED after success threshold.

        Args:
            resource_id: Resource identifier
        """
        with self._lock:
            if self._circuits.get(resource_id) == CircuitState.HALF_OPEN:
                self._success_counts[resource_id] += 1
                logger.debug(
                    f"Success recorded for {resource_id}: "
                    f"{self._success_counts[resource_id]}/"
                    f"{self.config.success_threshold}"
                )

                if self._success_counts[resource_id] >= self.config.success_threshold:
                    self._transition_to_closed(resource_id)

    def record_failure(self, resource_id: str) -> None:
        """
        Record failed execution.

        Args:
            resource_id: Resource identifier
        """
        with self._lock:
            self._failure_counts[resource_id] += 1
            self._last_failure_time[resource_id] = time.time()

    def get_circuit_state(self, resource_id: str) -> CircuitState:
        """
        Get current circuit state.

        Args:
            resource_id: Resource identifier

        Returns:
            Current circuit state (CLOSED if not tracked)
        """
        with self._lock:
            return self._circuits.get(resource_id, CircuitState.CLOSED)

    def get_stats(self, resource_id: str) -> Dict[str, Any]:
        """
        Get circuit statistics.

        Args:
            resource_id: Resource identifier

        Returns:
            Dictionary with circuit stats
        """
        with self._lock:
            return {
                "circuit_state": self._circuits.get(resource_id, CircuitState.CLOSED).value,
                "failure_count": self._failure_counts.get(resource_id, 0),
                "success_count": self._success_counts.get(resource_id, 0),
                "half_open_calls": self._half_open_calls.get(resource_id, 0),
                "last_failure_time": self._last_failure_time.get(resource_id, 0)
            }


__all__ = [
    "CircuitBreakerStrategy",
    "CircuitState",
    "CircuitBreakerConfig",
]
