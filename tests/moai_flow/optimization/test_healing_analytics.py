#!/usr/bin/env python3
"""
Tests for HealingAnalytics
Target: 90%+ coverage
"""

import pytest
from datetime import datetime, timezone
from unittest.mock import Mock

from moai_flow.optimization.healing_analytics import (
    HealingAnalytics,
    HealingStats,
    StrategyEffectiveness
)
from moai_flow.optimization.self_healer import HealingResult


class TestHealingAnalytics:
    """Test HealingAnalytics"""

    @pytest.fixture
    def self_healer(self):
        healer = Mock()
        healer.get_healing_history.return_value = [
            HealingResult(
                success=True,
                failure_id="agent_failure_001",
                strategy_used="AgentRestartStrategy",
                actions_taken=["Restarted agent"],
                duration_ms=150,
                timestamp=datetime.now(timezone.utc),
                metadata={"agent_id": "agent-001"}
            ),
            HealingResult(
                success=False,
                failure_id="task_timeout_002",
                strategy_used="TaskRetryStrategy",
                actions_taken=["Max retries exceeded"],
                duration_ms=250,
                timestamp=datetime.now(timezone.utc),
                metadata={}
            ),
            HealingResult(
                success=True,
                failure_id="agent_failure_003",
                strategy_used="AgentRestartStrategy",
                actions_taken=["Restarted agent"],
                duration_ms=175,
                timestamp=datetime.now(timezone.utc),
                metadata={"agent_id": "agent-002"}
            )
        ]
        return healer

    @pytest.fixture
    def analytics(self, self_healer):
        return HealingAnalytics(self_healer)

    def test_initialization(self, analytics):
        """Test analytics initialization"""
        assert analytics.self_healer is not None
        assert analytics._stats_cache is None

    def test_get_overall_stats(self, analytics):
        """Test overall statistics"""
        stats = analytics.get_overall_stats()

        assert isinstance(stats, HealingStats)
        assert stats.total_healings == 3
        assert stats.success_rate > 0.5
        assert stats.avg_healing_time_ms > 0

    def test_get_strategy_effectiveness(self, analytics):
        """Test strategy effectiveness analysis"""
        effectiveness = analytics.get_strategy_effectiveness()

        assert len(effectiveness) > 0
        assert all(isinstance(e, StrategyEffectiveness) for e in effectiveness)

        # Check AgentRestartStrategy
        agent_restart = next(
            e for e in effectiveness
            if e.strategy_name == "AgentRestartStrategy"
        )
        assert agent_restart.success_count == 2
        assert agent_restart.success_rate == 1.0

    def test_calculate_mttr(self, analytics):
        """Test MTTR calculation"""
        mttr = analytics.calculate_mttr()

        assert mttr > 0
        # MTTR should be average of successful healings (150 + 175) / 2
        assert 160 <= mttr <= 165

    def test_analyze_failure_patterns(self, analytics):
        """Test failure pattern analysis"""
        patterns = analytics.analyze_failure_patterns()

        assert "most_common_failures" in patterns
        assert "failure_frequency" in patterns
        assert "time_of_day_patterns" in patterns
        assert "agent_patterns" in patterns

    def test_generate_recommendations(self, analytics):
        """Test recommendation generation"""
        recommendations = analytics.generate_recommendations()

        assert len(recommendations) > 0
        assert all(isinstance(r, str) for r in recommendations)

    def test_get_healing_timeline(self, analytics):
        """Test timeline generation"""
        timeline = analytics.get_healing_timeline(limit=10)

        assert len(timeline) <= 10
        assert all("timestamp" in event for event in timeline)

    def test_export_report(self, analytics):
        """Test report export"""
        report = analytics.export_report()

        assert "generated_at" in report
        assert "overall_stats" in report
        assert "strategy_effectiveness" in report
        assert "failure_patterns" in report
        assert "recommendations" in report

    def test_stats_caching(self, analytics):
        """Test statistics caching"""
        # First call
        stats1 = analytics.get_overall_stats()

        # Second call (should use cache)
        stats2 = analytics.get_overall_stats()

        assert stats1.total_healings == stats2.total_healings
        assert stats1.success_rate == stats2.success_rate


class TestHealingStatsDataclass:
    """Test HealingStats dataclass"""

    def test_creation(self):
        """Test creating HealingStats"""
        stats = HealingStats(
            total_failures=10,
            total_healings=10,
            success_rate=0.8,
            avg_healing_time_ms=200.0,
            by_strategy={"Strategy1": 5, "Strategy2": 5},
            by_failure_type={"type1": 6, "type2": 4},
            mttr_ms=180.0
        )

        assert stats.total_healings == 10
        assert stats.success_rate == 0.8


class TestStrategyEffectivenessDataclass:
    """Test StrategyEffectiveness dataclass"""

    def test_creation(self):
        """Test creating StrategyEffectiveness"""
        effectiveness = StrategyEffectiveness(
            strategy_name="TestStrategy",
            success_count=8,
            failure_count=2,
            success_rate=0.8,
            avg_healing_time_ms=150.0,
            trend="improving",
            recommendation="keep"
        )

        assert effectiveness.strategy_name == "TestStrategy"
        assert effectiveness.success_rate == 0.8


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
