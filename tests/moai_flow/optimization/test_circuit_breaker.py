#!/usr/bin/env python3
"""
Tests for CircuitBreakerStrategy

Coverage:
- Circuit state transitions (CLOSED → OPEN → HALF_OPEN → CLOSED)
- Failure threshold detection
- Success threshold detection
- Timeout behavior
- Thread safety
- Stats tracking

Target: 90%+ coverage
"""

import pytest
import time
from datetime import datetime, timezone
from unittest.mock import Mock

from moai_flow.optimization.strategies.circuit_breaker import (
    CircuitBreakerStrategy,
    CircuitState,
    CircuitBreakerConfig
)
from moai_flow.optimization.self_healer import Failure, HealingResult


class TestCircuitBreakerConfig:
    """Test configuration dataclass"""

    def test_default_config(self):
        """Test default configuration values"""
        config = CircuitBreakerConfig()

        assert config.failure_threshold == 5
        assert config.success_threshold == 2
        assert config.timeout_seconds == 60.0
        assert config.half_open_max_calls == 3

    def test_custom_config(self):
        """Test custom configuration"""
        config = CircuitBreakerConfig(
            failure_threshold=3,
            success_threshold=1,
            timeout_seconds=30.0,
            half_open_max_calls=2
        )

        assert config.failure_threshold == 3
        assert config.success_threshold == 1
        assert config.timeout_seconds == 30.0
        assert config.half_open_max_calls == 2


class TestCircuitBreakerStrategy:
    """Test CircuitBreakerStrategy implementation"""

    @pytest.fixture
    def config(self):
        """Create test configuration"""
        return CircuitBreakerConfig(
            failure_threshold=3,
            success_threshold=2,
            timeout_seconds=1.0,  # Short timeout for testing
            half_open_max_calls=2
        )

    @pytest.fixture
    def strategy(self, config):
        """Create strategy instance"""
        return CircuitBreakerStrategy(config)

    @pytest.fixture
    def coordinator(self):
        """Create mock coordinator"""
        return Mock()

    @pytest.fixture
    def failure(self):
        """Create test failure"""
        return Failure(
            failure_id="test-failure-001",
            failure_type="agent_failed",
            agent_id="agent-001",
            severity="high",
            detected_at=datetime.now(timezone.utc),
            event={"type": "agent_failed"}
        )

    def test_initialization(self, strategy, config):
        """Test strategy initialization"""
        assert strategy.config == config
        assert len(strategy._circuits) == 0
        assert len(strategy._failure_counts) == 0

    def test_can_heal_applicable_failures(self, strategy):
        """Test can_heal returns True for applicable failures"""
        applicable_types = [
            "agent_failed",
            "task_timeout",
            "execution_error",
            "agent_down",
            "heartbeat_failed"
        ]

        for failure_type in applicable_types:
            failure = Failure(
                failure_id="f1",
                failure_type=failure_type,
                agent_id="agent-001",
                severity="high",
                detected_at=datetime.now(timezone.utc),
                event={"type": failure_type}
            )
            assert strategy.can_heal(failure) is True

    def test_can_heal_not_applicable(self, strategy):
        """Test can_heal returns False for non-applicable failures"""
        failure = Failure(
            failure_id="f1",
            failure_type="resource_exhaustion",
            agent_id=None,
            severity="medium",
            detected_at=datetime.now(timezone.utc),
            event={"type": "resource_exhaustion"}
        )

        assert strategy.can_heal(failure) is False

    def test_closed_state_below_threshold(self, strategy, coordinator, failure):
        """Test CLOSED state behavior below failure threshold"""
        # First two failures should keep circuit closed
        for i in range(2):
            result = strategy.heal(failure, coordinator)

            assert result.success is True
            assert "closed" in result.metadata.get("circuit_state", "")

        # Verify circuit state
        state = strategy.get_circuit_state("agent-001")
        assert state == CircuitState.CLOSED

    def test_closed_to_open_transition(self, strategy, coordinator, failure):
        """Test CLOSED → OPEN transition at threshold"""
        # Cause 3 failures to reach threshold
        for i in range(3):
            result = strategy.heal(failure, coordinator)

        # Last result should show circuit opened
        assert result.success is False
        assert result.metadata.get("circuit_state") == "opened"

        # Verify circuit state
        state = strategy.get_circuit_state("agent-001")
        assert state == CircuitState.OPEN

    def test_open_state_fail_fast(self, strategy, coordinator, failure):
        """Test OPEN state fail-fast behavior"""
        # Open the circuit
        for i in range(3):
            strategy.heal(failure, coordinator)

        # Next attempt should fail fast
        result = strategy.heal(failure, coordinator)

        assert result.success is False
        assert result.metadata.get("fail_fast") is True
        assert "remaining_timeout_seconds" in result.metadata

    def test_open_to_half_open_transition(self, strategy, coordinator, failure):
        """Test OPEN → HALF_OPEN transition after timeout"""
        # Open the circuit
        for i in range(3):
            strategy.heal(failure, coordinator)

        # Wait for timeout
        time.sleep(1.1)

        # Next attempt should transition to HALF_OPEN
        result = strategy.heal(failure, coordinator)

        assert result.metadata.get("circuit_state") == "half_open"

        # Verify state
        state = strategy.get_circuit_state("agent-001")
        assert state == CircuitState.HALF_OPEN

    def test_half_open_max_calls_exceeded(self, strategy, coordinator, failure):
        """Test HALF_OPEN max calls exceeded"""
        # Open the circuit and wait
        for i in range(3):
            strategy.heal(failure, coordinator)

        time.sleep(1.1)

        # Transition to HALF_OPEN
        strategy.heal(failure, coordinator)

        # Exceed max calls (2 in config)
        for i in range(2):
            result = strategy.heal(failure, coordinator)

        # Should reopen circuit
        assert result.metadata.get("circuit_state") == "reopened"
        assert result.metadata.get("reason") == "max_calls_exceeded"

    def test_record_success(self, strategy):
        """Test success recording"""
        resource_id = "agent-001"

        # Set circuit to HALF_OPEN
        strategy._circuits[resource_id] = CircuitState.HALF_OPEN
        strategy._success_counts[resource_id] = 0

        # Record success
        strategy.record_success(resource_id)

        assert strategy._success_counts[resource_id] == 1

    def test_record_failure(self, strategy):
        """Test failure recording"""
        resource_id = "agent-001"

        # Record failure
        strategy.record_failure(resource_id)

        assert strategy._failure_counts[resource_id] == 1
        assert strategy._last_failure_time[resource_id] > 0

    def test_get_stats(self, strategy, coordinator, failure):
        """Test stats retrieval"""
        # Open the circuit
        for i in range(3):
            strategy.heal(failure, coordinator)

        stats = strategy.get_stats("agent-001")

        assert stats["circuit_state"] == "open"
        assert stats["failure_count"] >= 3
        assert "last_failure_time" in stats

    def test_multiple_resources(self, strategy, coordinator):
        """Test circuit breaker with multiple resources"""
        failure1 = Failure(
            failure_id="f1",
            failure_type="agent_failed",
            agent_id="agent-001",
            severity="high",
            detected_at=datetime.now(timezone.utc),
            event={"type": "agent_failed"}
        )

        failure2 = Failure(
            failure_id="f2",
            failure_type="agent_failed",
            agent_id="agent-002",
            severity="high",
            detected_at=datetime.now(timezone.utc),
            event={"type": "agent_failed"}
        )

        # Open circuit for agent-001
        for i in range(3):
            strategy.heal(failure1, coordinator)

        # agent-002 should still be closed
        result = strategy.heal(failure2, coordinator)

        assert result.success is True
        assert strategy.get_circuit_state("agent-001") == CircuitState.OPEN
        assert strategy.get_circuit_state("agent-002") == CircuitState.CLOSED

    def test_thread_safety(self, strategy, coordinator, failure):
        """Test thread-safe operations"""
        import threading

        results = []

        def heal_multiple():
            for i in range(10):
                result = strategy.heal(failure, coordinator)
                results.append(result)

        threads = [threading.Thread(target=heal_multiple) for _ in range(3)]

        for t in threads:
            t.start()

        for t in threads:
            t.join()

        # All operations should complete successfully
        assert len(results) == 30


class TestCircuitBreakerEdgeCases:
    """Test edge cases and error handling"""

    def test_failure_without_agent_id(self):
        """Test handling failure without agent_id"""
        strategy = CircuitBreakerStrategy()
        coordinator = Mock()

        failure = Failure(
            failure_id="f1",
            failure_type="task_timeout",
            agent_id=None,
            severity="medium",
            detected_at=datetime.now(timezone.utc),
            event={"type": "task_timeout"}
        )

        result = strategy.heal(failure, coordinator)

        # Should still work with resource_id based on failure_type
        assert result is not None
        assert isinstance(result, HealingResult)

    def test_default_config(self):
        """Test strategy with default configuration"""
        strategy = CircuitBreakerStrategy()

        assert strategy.config.failure_threshold == 5
        assert strategy.config.timeout_seconds == 60.0

    def test_get_circuit_state_unknown_resource(self):
        """Test getting state for unknown resource"""
        strategy = CircuitBreakerStrategy()

        state = strategy.get_circuit_state("unknown-resource")

        assert state == CircuitState.CLOSED

    def test_stats_for_unknown_resource(self):
        """Test getting stats for unknown resource"""
        strategy = CircuitBreakerStrategy()

        stats = strategy.get_stats("unknown-resource")

        assert stats["circuit_state"] == "closed"
        assert stats["failure_count"] == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=moai_flow.optimization.strategies.circuit_breaker"])
