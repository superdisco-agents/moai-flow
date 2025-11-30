# Advanced Healing - Custom Strategies and Analytics

Advanced self-healing techniques including custom strategy development, healing analytics, and optimization.

## Overview

This guide covers:
1. **Custom Healing Strategies** - Implementing domain-specific recovery
2. **Healing Analytics** - Performance tracking and optimization
3. **Strategy Composition** - Combining multiple strategies
4. **Advanced Pattern Detection** - Proactive failure prevention

## 1. Custom Healing Strategies

### Strategy Protocol

All healing strategies must implement the HealingStrategy protocol:

```python
from typing import Protocol
from moai_flow.optimization import Failure, HealingResult, ICoordinator

class HealingStrategy(Protocol):
    """Protocol for healing strategies"""

    def can_heal(self, failure: Failure) -> bool:
        """Check if strategy can heal this failure"""
        ...

    def heal(
        self,
        failure: Failure,
        coordinator: ICoordinator
    ) -> HealingResult:
        """Execute healing action"""
        ...
```

### Example 1: Circuit Breaker Strategy

Prevents cascading failures by temporarily disabling problematic agents:

```python
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from collections import defaultdict
import time

@dataclass
class CircuitState:
    """Circuit breaker state"""
    state: str  # "closed", "open", "half_open"
    failure_count: int
    last_failure_time: datetime
    opened_at: datetime = None

class CircuitBreakerStrategy:
    """
    Circuit breaker for failing agents.

    States:
    - Closed: Normal operation
    - Open: Agent disabled (too many failures)
    - Half-Open: Testing if agent recovered
    """

    def __init__(
        self,
        failure_threshold=5,
        timeout_ms=60000,  # 1 minute
        half_open_attempts=3
    ):
        self.failure_threshold = failure_threshold
        self.timeout_ms = timeout_ms
        self.half_open_attempts = half_open_attempts

        # Track circuit state per agent
        self._circuits = defaultdict(lambda: CircuitState(
            state="closed",
            failure_count=0,
            last_failure_time=datetime.now(timezone.utc)
        ))

    def can_heal(self, failure: Failure) -> bool:
        """Can heal repeated agent failures"""
        return (
            failure.failure_type in ["agent_down", "task_failed"]
            and failure.agent_id is not None
        )

    def heal(
        self,
        failure: Failure,
        coordinator: ICoordinator
    ) -> HealingResult:
        """
        Execute circuit breaker logic:
        1. Track failure count
        2. Open circuit if threshold exceeded
        3. Test recovery after timeout
        4. Close circuit if recovered
        """
        start_time = time.time()
        actions = []
        agent_id = failure.agent_id

        circuit = self._circuits[agent_id]

        # Update failure count
        circuit.failure_count += 1
        circuit.last_failure_time = datetime.now(timezone.utc)
        actions.append(
            f"Failure count for {agent_id}: {circuit.failure_count}"
        )

        # State machine
        if circuit.state == "closed":
            if circuit.failure_count >= self.failure_threshold:
                # Open circuit
                circuit.state = "open"
                circuit.opened_at = datetime.now(timezone.utc)

                # Disable agent (unregister temporarily)
                coordinator.unregister_agent(agent_id)

                actions.append(
                    f"Circuit opened: {agent_id} disabled "
                    f"({circuit.failure_count} failures)"
                )

                return HealingResult(
                    success=True,
                    failure_id=failure.failure_id,
                    strategy_used="CircuitBreakerStrategy",
                    actions_taken=actions,
                    duration_ms=int((time.time() - start_time) * 1000),
                    timestamp=datetime.now(timezone.utc),
                    metadata={
                        "circuit_state": "open",
                        "agent_id": agent_id
                    }
                )

        elif circuit.state == "open":
            # Check if timeout elapsed
            now = datetime.now(timezone.utc)
            elapsed_ms = (now - circuit.opened_at).total_seconds() * 1000

            if elapsed_ms >= self.timeout_ms:
                # Transition to half-open
                circuit.state = "half_open"
                circuit.failure_count = 0

                actions.append(
                    f"Circuit half-open: Testing {agent_id} recovery"
                )

                # Re-register agent for testing
                coordinator.register_agent(agent_id, {
                    "circuit_state": "half_open",
                    "test_mode": True
                })

        elif circuit.state == "half_open":
            if circuit.failure_count >= self.half_open_attempts:
                # Failed recovery, re-open circuit
                circuit.state = "open"
                circuit.opened_at = datetime.now(timezone.utc)

                coordinator.unregister_agent(agent_id)

                actions.append(
                    f"Circuit re-opened: {agent_id} still failing"
                )
            else:
                # Successful recovery, close circuit
                circuit.state = "closed"
                circuit.failure_count = 0

                actions.append(
                    f"Circuit closed: {agent_id} recovered"
                )

        return HealingResult(
            success=True,
            failure_id=failure.failure_id,
            strategy_used="CircuitBreakerStrategy",
            actions_taken=actions,
            duration_ms=int((time.time() - start_time) * 1000),
            timestamp=datetime.now(timezone.utc),
            metadata={
                "circuit_state": circuit.state,
                "failure_count": circuit.failure_count,
                "agent_id": agent_id
            }
        )

# Register with SelfHealer
healer.register_strategy("agent_down", CircuitBreakerStrategy())
healer.register_strategy("task_failed", CircuitBreakerStrategy())
```

### Example 2: Gradual Degradation Strategy

Reduces system load gracefully under resource pressure:

```python
class GradualDegradationStrategy:
    """
    Gracefully degrade service under resource pressure.

    Actions:
    1. Pause low-priority tasks
    2. Reduce agent concurrency
    3. Enable response caching
    4. Simplify prompts
    """

    def __init__(self, degradation_levels=None):
        if degradation_levels is None:
            self.degradation_levels = [
                {
                    "threshold": 0.8,  # 80% resource usage
                    "actions": ["pause_low_priority"]
                },
                {
                    "threshold": 0.9,  # 90% usage
                    "actions": ["pause_low_priority", "reduce_concurrency"]
                },
                {
                    "threshold": 0.95,  # 95% usage
                    "actions": [
                        "pause_low_priority",
                        "reduce_concurrency",
                        "enable_caching",
                        "simplify_prompts"
                    ]
                }
            ]

    def can_heal(self, failure: Failure) -> bool:
        """Can heal resource exhaustion"""
        return failure.failure_type in [
            "resource_exhaustion",
            "token_exhaustion",
            "memory_exhaustion"
        ]

    def heal(
        self,
        failure: Failure,
        coordinator: ICoordinator
    ) -> HealingResult:
        """Apply degradation actions based on severity"""
        start_time = time.time()
        actions = []

        # Determine degradation level
        resource_usage = failure.metadata.get("current_usage", 0)
        resource_limit = failure.metadata.get("limit", 100)
        usage_ratio = resource_usage / resource_limit

        # Select appropriate degradation level
        degradation_level = None
        for level in sorted(
            self.degradation_levels,
            key=lambda l: l["threshold"],
            reverse=True
        ):
            if usage_ratio >= level["threshold"]:
                degradation_level = level
                break

        if not degradation_level:
            return HealingResult(
                success=False,
                failure_id=failure.failure_id,
                strategy_used="GradualDegradationStrategy",
                actions_taken=["No degradation needed"],
                duration_ms=int((time.time() - start_time) * 1000),
                timestamp=datetime.now(timezone.utc)
            )

        # Apply degradation actions
        for action in degradation_level["actions"]:
            if action == "pause_low_priority":
                # Pause LOW priority tasks
                paused = pause_tasks_by_priority(["LOW"])
                actions.append(f"Paused {paused} low-priority tasks")

            elif action == "reduce_concurrency":
                # Reduce max concurrent tasks per agent
                reduce_agent_concurrency(max_concurrent=2)
                actions.append("Reduced agent concurrency to 2")

            elif action == "enable_caching":
                # Enable response caching
                enable_response_cache()
                actions.append("Enabled response caching")

            elif action == "simplify_prompts":
                # Use simplified prompts
                enable_prompt_simplification()
                actions.append("Enabled prompt simplification")

        return HealingResult(
            success=True,
            failure_id=failure.failure_id,
            strategy_used="GradualDegradationStrategy",
            actions_taken=actions,
            duration_ms=int((time.time() - start_time) * 1000),
            timestamp=datetime.now(timezone.utc),
            metadata={
                "usage_ratio": usage_ratio,
                "degradation_level": degradation_level["threshold"],
                "actions_applied": degradation_level["actions"]
            }
        )
```

## 2. Healing Analytics

### Comprehensive Analytics Setup

```python
from moai_flow.optimization.healing_analytics import HealingAnalytics

analytics = HealingAnalytics(healer)

# Get overall statistics
stats = analytics.get_overall_stats(time_range_ms=3600000)  # Last hour

print(f"Healing Analytics (Last Hour)")
print(f"=" * 60)
print(f"Total Failures: {stats.total_failures}")
print(f"Total Healings: {stats.total_healings}")
print(f"Success Rate: {stats.success_rate:.1%}")
print(f"Avg Healing Time: {stats.avg_healing_time_ms:.0f}ms")
print(f"MTTR: {stats.mttr_ms:.0f}ms")  # Mean Time To Recovery

print(f"\nBy Strategy:")
for strategy, count in stats.by_strategy.items():
    print(f"  {strategy}: {count}")

print(f"\nBy Failure Type:")
for failure_type, count in stats.by_failure_type.items():
    print(f"  {failure_type}: {count}")
```

### Strategy Effectiveness Analysis

```python
effectiveness = analytics.get_strategy_effectiveness()

print(f"\nStrategy Effectiveness Analysis")
print(f"=" * 60)

for strategy in effectiveness:
    print(f"\n{strategy.strategy_name}:")
    print(f"  Success: {strategy.success_count}")
    print(f"  Failures: {strategy.failure_count}")
    print(f"  Success Rate: {strategy.success_rate:.1%}")
    print(f"  Avg Time: {strategy.avg_healing_time_ms:.0f}ms")
    print(f"  Trend: {strategy.trend}")

    # Visual indicator
    if strategy.success_rate >= 0.9:
        indicator = "✅ Excellent"
    elif strategy.success_rate >= 0.7:
        indicator = "✓ Good"
    elif strategy.success_rate >= 0.5:
        indicator = "⚠️  Needs improvement"
    else:
        indicator = "❌ Poor"

    print(f"  Status: {indicator}")
```

### Automated Recommendations

```python
recommendations = analytics.generate_recommendations()

print(f"\nAutomated Recommendations")
print(f"=" * 60)

if recommendations:
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec}")
else:
    print("✓ No recommendations - system performing optimally")
```

### Custom Analytics Dashboard

```python
def generate_healing_dashboard(analytics, time_range_ms=3600000):
    """Generate comprehensive healing dashboard"""
    stats = analytics.get_overall_stats(time_range_ms)
    effectiveness = analytics.get_strategy_effectiveness()
    recommendations = analytics.generate_recommendations()

    dashboard = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "time_range_ms": time_range_ms,
        "overall": {
            "total_failures": stats.total_failures,
            "total_healings": stats.total_healings,
            "success_rate": stats.success_rate,
            "avg_healing_time_ms": stats.avg_healing_time_ms,
            "mttr_ms": stats.mttr_ms
        },
        "strategies": [
            {
                "name": s.strategy_name,
                "success_rate": s.success_rate,
                "success_count": s.success_count,
                "failure_count": s.failure_count,
                "avg_time_ms": s.avg_healing_time_ms,
                "trend": s.trend,
                "recommendation": s.recommendation
            }
            for s in effectiveness
        ],
        "by_failure_type": stats.by_failure_type,
        "recommendations": recommendations,
        "health_score": calculate_system_health_score(stats, effectiveness)
    }

    return dashboard

def calculate_system_health_score(stats, effectiveness):
    """Calculate overall system health (0-100)"""
    # Success rate weight: 50%
    success_score = stats.success_rate * 50

    # MTTR weight: 30% (lower is better, target: 500ms)
    target_mttr = 500
    mttr_score = max(0, (1 - (stats.mttr_ms / target_mttr))) * 30

    # Strategy health weight: 20%
    strategy_scores = [s.success_rate for s in effectiveness]
    strategy_score = (
        (sum(strategy_scores) / len(strategy_scores))
        if strategy_scores else 0.5
    ) * 20

    total_score = min(100, success_score + mttr_score + strategy_score)

    return round(total_score, 1)
```

## 3. Strategy Composition

### Combining Multiple Strategies

```python
class CompositeHealingStrategy:
    """
    Combine multiple strategies with fallback logic.

    Tries strategies in priority order until one succeeds.
    """

    def __init__(self, strategies):
        """
        Args:
            strategies: List of (priority, strategy) tuples
        """
        self.strategies = sorted(strategies, key=lambda x: x[0])

    def can_heal(self, failure: Failure) -> bool:
        """Can heal if any sub-strategy can"""
        return any(
            strategy.can_heal(failure)
            for _, strategy in self.strategies
        )

    def heal(
        self,
        failure: Failure,
        coordinator: ICoordinator
    ) -> HealingResult:
        """Try strategies in priority order"""
        start_time = time.time()
        all_actions = []

        for priority, strategy in self.strategies:
            if not strategy.can_heal(failure):
                continue

            result = strategy.heal(failure, coordinator)
            all_actions.extend(result.actions_taken)

            if result.success:
                return HealingResult(
                    success=True,
                    failure_id=failure.failure_id,
                    strategy_used=f"Composite[{result.strategy_used}]",
                    actions_taken=all_actions,
                    duration_ms=int((time.time() - start_time) * 1000),
                    timestamp=datetime.now(timezone.utc),
                    metadata={
                        "primary_strategy": result.strategy_used,
                        "attempts": len(all_actions)
                    }
                )

        # All strategies failed
        return HealingResult(
            success=False,
            failure_id=failure.failure_id,
            strategy_used="CompositeHealingStrategy",
            actions_taken=all_actions + ["All strategies failed"],
            duration_ms=int((time.time() - start_time) * 1000),
            timestamp=datetime.now(timezone.utc)
        )

# Usage
composite_strategy = CompositeHealingStrategy([
    (1, CircuitBreakerStrategy()),      # Highest priority
    (2, AgentRestartStrategy()),
    (3, GradualDegradationStrategy())
])

healer.register_strategy("agent_down", composite_strategy)
```

## 4. Advanced Pattern Detection

### Failure Pattern Learning

```python
def learn_failure_patterns(pattern_learner, healing_history):
    """
    Learn patterns from healing history.

    Identifies:
    - Recurring failure sequences
    - Temporal patterns (time-based failures)
    - Correlation patterns (related failures)
    """
    # Convert healing history to events
    events = []
    for healing in healing_history:
        # Failure event
        events.append({
            "type": "failure_detected",
            "timestamp": healing.timestamp,
            "failure_type": healing.metadata.get("failure_type"),
            "agent_id": healing.metadata.get("agent_id")
        })

        # Healing event
        events.append({
            "type": "healing_attempted",
            "timestamp": healing.timestamp,
            "strategy": healing.strategy_used,
            "success": healing.success
        })

    # Record events for learning
    for event in events:
        pattern_learner.record_event(event)

    # Learn patterns
    patterns = pattern_learner.learn_patterns()

    # Analyze failure patterns
    failure_patterns = [
        p for p in patterns
        if any(e.get("type") == "failure_detected" for e in p.events)
    ]

    return failure_patterns
```

## 5. Complete Advanced Example

```python
#!/usr/bin/env python3
"""Complete Advanced Healing Example"""

from moai_flow.optimization import SelfHealer
from moai_flow.optimization.healing_analytics import HealingAnalytics

def main():
    # 1. Initialize self-healer
    healer = SelfHealer(
        coordinator=coordinator,
        auto_heal=True
    )

    # 2. Register custom strategies
    healer.register_strategy(
        "agent_down",
        CircuitBreakerStrategy(failure_threshold=5)
    )

    healer.register_strategy(
        "resource_exhaustion",
        GradualDegradationStrategy()
    )

    # 3. Initialize analytics
    analytics = HealingAnalytics(healer)

    # 4. Continuous monitoring
    while True:
        # Detect and heal failures
        for event in system_events:
            failure = healer.detect_failure(event)
            if failure:
                result = healer.heal(failure)
                logger.info(
                    f"Healing: {result.strategy_used} - "
                    f"{'✅' if result.success else '❌'}"
                )

        # Generate dashboard every 5 minutes
        dashboard = generate_healing_dashboard(
            analytics,
            time_range_ms=300000
        )

        print(f"\nSystem Health Score: {dashboard['health_score']}/100")

        # Act on recommendations
        for rec in dashboard['recommendations']:
            logger.warning(f"Recommendation: {rec}")

        time.sleep(300)

if __name__ == "__main__":
    main()
```

## Best Practices

1. **Strategy Design**: Keep strategies focused on single failure types
2. **Analytics Review**: Monitor weekly for degrading trends
3. **Custom Strategies**: Implement domain-specific recovery logic
4. **Composition**: Use fallback chains for robustness
5. **Pattern Learning**: Continuously improve from failure history
6. **Health Scoring**: Track overall system health proactively

## Performance Targets

- Healing success rate: >85%
- MTTR (Mean Time To Recovery): <500ms
- Strategy effectiveness: >70% per strategy
- System health score: >80/100

## Related Documentation

- [Predictive Healing Module](../modules/predictive-healing.md)
- [Performance Monitoring Module](../modules/performance-monitoring.md)
- [Self-Healing Documentation](../SKILL.md#3-self-healing---automatic-failure-recovery)
