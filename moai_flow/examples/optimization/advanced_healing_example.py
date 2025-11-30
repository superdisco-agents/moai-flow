#!/usr/bin/env python3
"""
Advanced Self-Healing Example
==============================

Demonstrates the complete self-healing system with:
- CircuitBreaker strategy
- GradualDegradation strategy
- PredictiveHealing
- HealingAnalytics

This example shows a complete workflow:
1. Initialize self-healing system with advanced strategies
2. Simulate various failure scenarios
3. Apply predictive healing
4. Analyze healing effectiveness
5. Generate recommendations

Usage:
    python advanced_healing_example.py
"""

import time
from datetime import datetime, timezone

from moai_flow.optimization.self_healer import SelfHealer, Failure
from moai_flow.optimization.strategies.circuit_breaker import (
    CircuitBreakerStrategy,
    CircuitBreakerConfig
)
from moai_flow.optimization.strategies.gradual_degradation import (
    GradualDegradationStrategy,
    DegradationConfig
)
from moai_flow.optimization.predictive_healing import PredictiveHealing
from moai_flow.optimization.healing_analytics import HealingAnalytics
from moai_flow.optimization.pattern_learner import PatternLearner


def create_failure(failure_type: str, agent_id: str = None, **metadata) -> Failure:
    """Helper to create test failures"""
    return Failure(
        failure_id=f"{failure_type}_{int(time.time() * 1000)}",
        failure_type=failure_type,
        agent_id=agent_id,
        severity=metadata.get("severity", "medium"),
        detected_at=datetime.now(timezone.utc),
        event={"type": failure_type},
        metadata=metadata
    )


def main():
    """Main example workflow"""
    print("=" * 70)
    print("Advanced Self-Healing System Example")
    print("=" * 70)
    print()

    # ========================================================================
    # Step 1: Initialize Components
    # ========================================================================
    print("1. Initializing self-healing system...")
    print()

    # Mock coordinator (in real use, this would be SwarmCoordinator)
    class MockCoordinator:
        def get_agent_status(self, agent_id):
            return {"status": "active", "metadata": {}}

        def unregister_agent(self, agent_id):
            return True

        def register_agent(self, agent_id, metadata):
            return True

        def get_topology_info(self):
            return {"agent_count": 5}

    coordinator = MockCoordinator()

    # Initialize SelfHealer
    pattern_learner = PatternLearner(min_occurrences=3, confidence_threshold=0.7)
    self_healer = SelfHealer(
        coordinator=coordinator,
        pattern_learner=pattern_learner,
        auto_heal=True
    )

    # Add advanced strategies
    circuit_breaker = CircuitBreakerStrategy(
        CircuitBreakerConfig(
            failure_threshold=3,
            success_threshold=2,
            timeout_seconds=30.0
        )
    )
    gradual_degradation = GradualDegradationStrategy()

    self_healer.register_strategy("agent_failed", circuit_breaker)
    self_healer.register_strategy("resource_exhaustion", gradual_degradation)

    print("✓ SelfHealer initialized with advanced strategies")
    print("  - CircuitBreaker for cascading failure prevention")
    print("  - GradualDegradation for resource exhaustion")
    print()

    # Initialize PredictiveHealing
    predictor = PredictiveHealing(
        pattern_learner=pattern_learner,
        self_healer=self_healer,
        confidence_threshold=0.7
    )

    print("✓ PredictiveHealing initialized")
    print()

    # Initialize Analytics
    analytics = HealingAnalytics(self_healer)

    print("✓ HealingAnalytics initialized")
    print()

    # ========================================================================
    # Step 2: Simulate Failure Scenarios
    # ========================================================================
    print("2. Simulating failure scenarios...")
    print()

    # Scenario 1: Agent failures (Circuit Breaker)
    print("Scenario 1: Repeated agent failures")
    for i in range(5):
        failure = create_failure(
            "agent_failed",
            agent_id="agent-001",
            severity="high"
        )

        result = self_healer.heal(failure)

        print(f"  Attempt {i+1}: {'✓ Success' if result.success else '✗ Failed'} "
              f"({result.strategy_used}) - {result.duration_ms}ms")

        if not result.success and "circuit" in str(result.actions_taken).lower():
            print(f"    → Circuit breaker activated!")
            break

    print()

    # Scenario 2: Resource exhaustion (Gradual Degradation)
    print("Scenario 2: Token exhaustion")
    for usage in [85, 92, 96, 98]:
        failure = create_failure(
            "token_exhaustion",
            resource_type="token",
            usage_percent=usage
        )

        result = self_healer.heal(failure)

        degradation_level = result.metadata.get("degradation_level", "FULL")
        print(f"  Usage: {usage}% → Degradation: {degradation_level} "
              f"({result.duration_ms}ms)")

    print()

    # Scenario 3: Task timeouts
    print("Scenario 3: Task timeouts")
    for i in range(3):
        failure = create_failure(
            "task_timeout",
            agent_id=f"agent-00{i+2}",
            task_id=f"task-{i+1}"
        )

        result = self_healer.heal(failure)

        print(f"  Task {i+1}: {'✓ Retried' if result.success else '✗ Failed'} "
              f"({result.duration_ms}ms)")

    print()

    # ========================================================================
    # Step 3: Predictive Healing
    # ========================================================================
    print("3. Predictive healing demonstration...")
    print()

    # Simulate resource trend
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
            "metadata": {"token_usage_percent": 92}
        }
    ]

    predictions = predictor.predict_failures(events)

    print(f"Generated {len(predictions)} predictions:")
    for pred in predictions:
        print(f"  • {pred.failure_type} (confidence: {pred.confidence:.1%})")
        print(f"    → {pred.reasoning}")
        print(f"    → Recommended: {pred.recommended_action}")
        print()

    print()

    # ========================================================================
    # Step 4: Analytics and Insights
    # ========================================================================
    print("4. Healing analytics and insights...")
    print()

    # Overall statistics
    stats = analytics.get_overall_stats()

    print("Overall Statistics:")
    print(f"  Total healings: {stats.total_healings}")
    print(f"  Success rate: {stats.success_rate:.1%}")
    print(f"  Average healing time: {stats.avg_healing_time_ms:.0f}ms")
    print(f"  MTTR: {stats.mttr_ms:.0f}ms")
    print()

    # Strategy effectiveness
    effectiveness = analytics.get_strategy_effectiveness()

    print("Strategy Effectiveness:")
    for strategy in effectiveness:
        print(f"  {strategy.strategy_name}:")
        print(f"    Success rate: {strategy.success_rate:.1%}")
        print(f"    Successes: {strategy.success_count}")
        print(f"    Failures: {strategy.failure_count}")
        print(f"    Avg time: {strategy.avg_healing_time_ms:.0f}ms")
        print(f"    Trend: {strategy.trend}")
        print(f"    Recommendation: {strategy.recommendation}")
        print()

    # Failure patterns
    patterns = analytics.analyze_failure_patterns()

    print("Failure Patterns:")
    if patterns["most_common_failures"]:
        print("  Most common:")
        for failure_info in patterns["most_common_failures"][:3]:
            print(f"    • {failure_info['type']}: {failure_info['count']} times")
    print()

    # ========================================================================
    # Step 5: Recommendations
    # ========================================================================
    print("5. System recommendations...")
    print()

    recommendations = analytics.generate_recommendations()

    print("Recommendations:")
    for i, rec in enumerate(recommendations, 1):
        print(f"  {i}. {rec}")

    print()

    # ========================================================================
    # Step 6: Export Report
    # ========================================================================
    print("6. Generating analytics report...")
    print()

    report = analytics.export_report()

    print("Report generated:")
    print(f"  Generated at: {report['generated_at']}")
    print(f"  Total healings: {report['overall_stats']['total_healings']}")
    print(f"  Strategies analyzed: {len(report['strategy_effectiveness'])}")
    print(f"  Recommendations: {len(report['recommendations'])}")
    print()

    # ========================================================================
    # Summary
    # ========================================================================
    print("=" * 70)
    print("Example completed successfully!")
    print("=" * 70)
    print()
    print("Key takeaways:")
    print("  1. CircuitBreaker prevents cascading failures")
    print("  2. GradualDegradation maintains service under resource pressure")
    print("  3. PredictiveHealing enables proactive failure prevention")
    print("  4. HealingAnalytics provides actionable insights")
    print()
    print("For production use:")
    print("  - Configure thresholds based on your workload")
    print("  - Enable auto_heal for automated recovery")
    print("  - Monitor analytics for optimization opportunities")
    print("  - Use predictive healing for critical systems")
    print()


if __name__ == "__main__":
    main()
