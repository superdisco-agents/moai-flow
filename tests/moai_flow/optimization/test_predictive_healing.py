#!/usr/bin/env python3
"""
Tests for PredictiveHealing
Target: 90%+ coverage
"""

import pytest
from datetime import datetime, timezone
from unittest.mock import Mock

from moai_flow.optimization.predictive_healing import (
    PredictiveHealing,
    PredictedFailure
)
from moai_flow.optimization.pattern_learner import Pattern


class TestPredictiveHealing:
    """Test PredictiveHealing"""

    @pytest.fixture
    def pattern_learner(self):
        learner = Mock()
        learner.get_all_patterns.return_value = []
        return learner

    @pytest.fixture
    def self_healer(self):
        return Mock()

    @pytest.fixture
    def predictor(self, pattern_learner, self_healer):
        return PredictiveHealing(
            pattern_learner=pattern_learner,
            self_healer=self_healer,
            confidence_threshold=0.7
        )

    def test_initialization(self, predictor):
        """Test initialization"""
        assert predictor.confidence_threshold == 0.7
        assert len(predictor._predictions) == 0

    def test_predict_failures_empty_events(self, predictor):
        """Test prediction with no events"""
        predictions = predictor.predict_failures([])

        assert len(predictions) == 0

    def test_predict_failures_with_resource_trends(self, predictor):
        """Test prediction with resource trends"""
        events = [
            {
                "type": "resource_metric",
                "timestamp": datetime.now(timezone.utc),
                "metadata": {"token_usage_percent": 85}
            },
            {
                "type": "resource_metric",
                "timestamp": datetime.now(timezone.utc),
                "metadata": {"token_usage_percent": 88}
            },
            {
                "type": "resource_metric",
                "timestamp": datetime.now(timezone.utc),
                "metadata": {"token_usage_percent": 91}
            }
        ]

        predictions = predictor.predict_failures(events)

        # Should predict token exhaustion
        assert len(predictions) >= 1
        assert any(p.failure_type == "token_exhaustion" for p in predictions)

    def test_record_prediction_outcome(self, predictor):
        """Test recording prediction outcomes"""
        prediction = PredictedFailure(
            failure_type="agent_down",
            agent_id="agent-001",
            confidence=0.8,
            expected_time_ms=5000,
            reasoning="Test",
            recommended_action="Restart",
            pattern_indicators=["pattern-1"]
        )

        predictor.record_prediction_outcome(prediction, occurred=True)

        stats = predictor.get_prediction_stats()
        assert "pattern-1" in stats["pattern_accuracy"]
        assert stats["pattern_accuracy"]["pattern-1"]["correct"] == 1

    def test_get_prediction_stats(self, predictor):
        """Test stats retrieval"""
        stats = predictor.get_prediction_stats()

        assert "total_predictions" in stats
        assert "pattern_accuracy" in stats
        assert stats["confidence_threshold"] == 0.7


class TestPredictedFailure:
    """Test PredictedFailure dataclass"""

    def test_creation(self):
        """Test creating predicted failure"""
        pred = PredictedFailure(
            failure_type="task_timeout",
            agent_id="agent-001",
            confidence=0.85,
            expected_time_ms=10000,
            reasoning="Pattern match",
            recommended_action="Retry task"
        )

        assert pred.failure_type == "task_timeout"
        assert pred.confidence == 0.85
        assert len(pred.pattern_indicators) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
