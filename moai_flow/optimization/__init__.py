"""
MoAI-Flow Optimization Module

Adaptive optimization components for Phase 6C:
- BottleneckDetector: Performance bottleneck identification
- PatternLearner: Behavioral pattern recognition
- PatternMatcher: Pattern-based optimization
- SelfHealer: Automatic issue resolution
- PredictiveHealing: Proactive failure prediction
- HealingAnalytics: Self-healing performance analytics

Advanced Strategies (strategies/):
- CircuitBreakerStrategy: Prevent cascading failures
- GradualDegradationStrategy: Graceful service degradation
"""

# Core Pattern Learning
from .pattern_learner import (
    PatternLearner,
    Pattern,
)

# Pattern Matching and Prediction
from .pattern_matcher import (
    PatternMatcher,
    PatternMatch,
    Prediction,
)

# Self-Healing System
from .self_healer import (
    SelfHealer,
    Failure,
    HealingResult,
    PredictedFailure,
    HealingStrategy,
    AgentRestartStrategy,
    TaskRetryStrategy,
    ResourceRebalanceStrategy,
    QuorumRecoveryStrategy,
)

# Performance Bottleneck Detection
from .bottleneck_detector import (
    BottleneckDetector,
    Bottleneck,
    PerformanceReport,
)

# Predictive Healing (Phase 7)
from .predictive_healing import (
    PredictiveHealing,
    PredictedFailure as PredictedFailureEnhanced,
)

# Healing Analytics (Phase 7)
from .healing_analytics import (
    HealingAnalytics,
    HealingStats,
    StrategyEffectiveness,
)

# Advanced Healing Strategies (Phase 7)
from .strategies import (
    CircuitBreakerStrategy,
    CircuitState,
    CircuitBreakerConfig,
    GradualDegradationStrategy,
    DegradationLevel,
    DegradationConfig,
)

__all__ = [
    # Pattern Learning
    "PatternLearner",
    "Pattern",

    # Pattern Matching
    "PatternMatcher",
    "PatternMatch",
    "Prediction",

    # Self-Healing Core
    "SelfHealer",
    "Failure",
    "HealingResult",
    "PredictedFailure",
    "HealingStrategy",

    # Built-in Healing Strategies
    "AgentRestartStrategy",
    "TaskRetryStrategy",
    "ResourceRebalanceStrategy",
    "QuorumRecoveryStrategy",

    # Performance Detection
    "BottleneckDetector",
    "Bottleneck",
    "PerformanceReport",

    # Predictive Healing (Phase 7)
    "PredictiveHealing",
    "PredictedFailureEnhanced",

    # Healing Analytics (Phase 7)
    "HealingAnalytics",
    "HealingStats",
    "StrategyEffectiveness",

    # Advanced Strategies (Phase 7)
    "CircuitBreakerStrategy",
    "CircuitState",
    "CircuitBreakerConfig",
    "GradualDegradationStrategy",
    "DegradationLevel",
    "DegradationConfig",
]
