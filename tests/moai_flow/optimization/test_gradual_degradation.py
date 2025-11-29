#!/usr/bin/env python3
"""
Tests for GradualDegradationStrategy
Target: 90%+ coverage
"""

import pytest
from datetime import datetime, timezone
from unittest.mock import Mock

from moai_flow.optimization.strategies.gradual_degradation import (
    GradualDegradationStrategy,
    DegradationLevel,
    DegradationConfig
)
from moai_flow.optimization.self_healer import Failure


class TestGradualDegradationStrategy:
    """Test GradualDegradationStrategy"""

    @pytest.fixture
    def strategy(self):
        return GradualDegradationStrategy()

    @pytest.fixture
    def coordinator(self):
        return Mock()

    def test_can_heal_resource_failures(self, strategy):
        """Test can_heal for resource failures"""
        types = [
            "resource_exhaustion",
            "token_exhaustion",
            "quota_exceeded",
            "memory_exhaustion",
            "memory_pressure",
            "high_latency"
        ]

        for ftype in types:
            failure = Failure(
                failure_id="f1",
                failure_type=ftype,
                agent_id=None,
                severity="high",
                detected_at=datetime.now(timezone.utc),
                event={"type": ftype},
                metadata={"resource_type": "token"}
            )
            assert strategy.can_heal(failure) is True

    def test_assess_severity_levels(self, strategy):
        """Test severity assessment for different usage levels"""
        test_cases = [
            (85, DegradationLevel.FULL),
            (92, DegradationLevel.REDUCED_1),
            (96, DegradationLevel.REDUCED_2),
            (98.5, DegradationLevel.REDUCED_3),
            (99.5, DegradationLevel.MINIMAL),
        ]

        for usage, expected_level in test_cases:
            level = strategy._assess_severity(usage)
            assert level == expected_level

    def test_heal_applies_degradation(self, strategy, coordinator):
        """Test healing applies degradation"""
        failure = Failure(
            failure_id="f1",
            failure_type="token_exhaustion",
            agent_id=None,
            severity="high",
            detected_at=datetime.now(timezone.utc),
            event={"type": "token_exhaustion"},
            metadata={"resource_type": "token", "usage_percent": 95}
        )

        result = strategy.heal(failure, coordinator)

        assert result.success is True
        assert "degradation_level" in result.metadata
        assert result.metadata["degradation_level"] == "REDUCED_2"

    def test_get_current_level(self, strategy):
        """Test getting current degradation level"""
        strategy._current_level["token"] = DegradationLevel.REDUCED_2

        level = strategy.get_current_level("token")
        assert level == DegradationLevel.REDUCED_2

    def test_reset_degradation(self, strategy):
        """Test reset to FULL level"""
        strategy._current_level["token"] = DegradationLevel.REDUCED_3

        strategy.reset("token")

        assert strategy.get_current_level("token") == DegradationLevel.FULL

    def test_get_stats(self, strategy, coordinator):
        """Test stats retrieval"""
        failure = Failure(
            failure_id="f1",
            failure_type="token_exhaustion",
            agent_id=None,
            severity="high",
            detected_at=datetime.now(timezone.utc),
            event={"type": "token_exhaustion"},
            metadata={"resource_type": "token", "usage_percent": 98}
        )

        strategy.heal(failure, coordinator)
        stats = strategy.get_stats("token")

        assert stats["resource_type"] == "token"
        assert "current_level" in stats
        assert "timeout_multiplier" in stats


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
