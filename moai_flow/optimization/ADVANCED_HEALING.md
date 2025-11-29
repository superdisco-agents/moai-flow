# Advanced Self-Healing Features

**Phase 7 (Track 3 Week 4-6): PRD-09 Extensions**

This document describes the advanced self-healing capabilities added to MoAI-Flow.

## Overview

The advanced healing system extends Phase 6C's basic self-healing with:

1. **CircuitBreaker Strategy**: Prevent cascading failures
2. **GradualDegradation Strategy**: Graceful service degradation
3. **PredictiveHealing**: Proactive failure prevention
4. **HealingAnalytics**: Performance insights and recommendations

## Components

### 1. CircuitBreaker Strategy

Implements the circuit breaker pattern to prevent cascading failures.

**States**:
- `CLOSED`: Normal operation, requests pass through
- `OPEN`: Failing, reject requests immediately (fail-fast)
- `HALF_OPEN`: Testing recovery, limited requests allowed

**Usage**:
```python
from moai_flow.optimization.strategies.circuit_breaker import (
    CircuitBreakerStrategy,
    CircuitBreakerConfig
)

# Configure circuit breaker
config = CircuitBreakerConfig(
    failure_threshold=5,       # Open after 5 failures
    success_threshold=2,       # Close after 2 successes
    timeout_seconds=60.0,      # Wait 60s before retry
    half_open_max_calls=3      # Allow 3 calls in HALF_OPEN
)

strategy = CircuitBreakerStrategy(config)

# Register with SelfHealer
self_healer.register_strategy("agent_failed", strategy)
```

**Features**:
- Automatic state transitions
- Per-agent/resource circuit tracking
- Thread-safe operations
- Configurable thresholds
- Statistics tracking

**When to use**:
- Repeated agent failures
- Cascading task timeouts
- Service degradation detection
- Preventing thundering herd

### 2. GradualDegradation Strategy

Progressive service quality reduction to maintain core functionality under resource pressure.

**Degradation Levels**:
- `FULL` (100%): All features enabled
- `REDUCED_1` (75%): Minor optimizations
- `REDUCED_2` (50%): Significant optimizations
- `REDUCED_3` (25%): Minimal features
- `MINIMAL` (10%): Emergency mode

**Usage**:
```python
from moai_flow.optimization.strategies.gradual_degradation import (
    GradualDegradationStrategy,
    DegradationConfig
)

# Configure degradation
config = DegradationConfig()  # Use defaults or customize

strategy = GradualDegradationStrategy(config)

# Register with SelfHealer
self_healer.register_strategy("resource_exhaustion", strategy)
```

**Degradation Measures**:
- Timeout reduction (faster failure detection)
- Quality threshold lowering (accept lower quality)
- Feature disabling (non-critical features off)
- Concurrency limiting (reduce parallel operations)

**When to use**:
- Token exhaustion (> 90% usage)
- Memory pressure (> 85% usage)
- Rate limiting (quota approaching)
- High latency (system slowdown)

### 3. PredictiveHealing

Predict and prevent failures BEFORE they occur.

**Prediction Sources**:
1. Pattern matching (via PatternLearner)
2. Resource usage trends
3. Historical failure patterns
4. Agent health degradation
5. Queue depth trends

**Usage**:
```python
from moai_flow.optimization.predictive_healing import PredictiveHealing

# Initialize predictor
predictor = PredictiveHealing(
    pattern_learner=pattern_learner,
    self_healer=self_healer,
    confidence_threshold=0.7  # 70% confidence minimum
)

# Predict failures from recent events
events = [...]  # Recent events from coordinator
predictions = predictor.predict_failures(events)

# Apply preventive healing
for prediction in predictions:
    if prediction.confidence > 0.8:
        predictor.apply_preventive_healing(
            prediction,
            auto_apply=True  # Automatically apply healing
        )
```

**Confidence Calculation**:
- Pattern match similarity: 50%
- Historical accuracy: 30%
- Recency factor: 20%

**When to use**:
- Critical production systems
- High-availability requirements
- Resource trend monitoring
- Proactive maintenance windows

### 4. HealingAnalytics

Comprehensive analytics and insights for healing effectiveness.

**Metrics Provided**:
- Overall success rate
- Strategy-specific effectiveness
- Mean Time To Recovery (MTTR)
- Failure pattern analysis
- Healing time distribution
- Trend analysis

**Usage**:
```python
from moai_flow.optimization.healing_analytics import HealingAnalytics

# Initialize analytics
analytics = HealingAnalytics(self_healer)

# Get overall statistics
stats = analytics.get_overall_stats()
print(f"Success rate: {stats.success_rate:.1%}")
print(f"MTTR: {stats.mttr_ms:.0f}ms")

# Strategy effectiveness
effectiveness = analytics.get_strategy_effectiveness()
for strategy in effectiveness:
    print(f"{strategy.strategy_name}: {strategy.success_rate:.1%}")
    print(f"  Trend: {strategy.trend}")
    print(f"  Recommendation: {strategy.recommendation}")

# Failure patterns
patterns = analytics.analyze_failure_patterns()
print(f"Most common: {patterns['most_common_failures'][0]}")

# Recommendations
recommendations = analytics.generate_recommendations()
for rec in recommendations:
    print(f"- {rec}")

# Export full report
report = analytics.export_report()
```

**When to use**:
- System health monitoring
- Strategy optimization
- Performance tuning
- Capacity planning
- Post-incident analysis

## Integration Example

Complete example integrating all components:

```python
from moai_flow.optimization.self_healer import SelfHealer
from moai_flow.optimization.strategies.circuit_breaker import CircuitBreakerStrategy
from moai_flow.optimization.strategies.gradual_degradation import GradualDegradationStrategy
from moai_flow.optimization.predictive_healing import PredictiveHealing
from moai_flow.optimization.healing_analytics import HealingAnalytics
from moai_flow.optimization.pattern_learner import PatternLearner

# Initialize core components
pattern_learner = PatternLearner()
self_healer = SelfHealer(
    coordinator=coordinator,
    pattern_learner=pattern_learner,
    auto_heal=True
)

# Add advanced strategies
self_healer.register_strategy("agent_failed", CircuitBreakerStrategy())
self_healer.register_strategy("resource_exhaustion", GradualDegradationStrategy())

# Setup predictive healing
predictor = PredictiveHealing(pattern_learner, self_healer)

# Setup analytics
analytics = HealingAnalytics(self_healer)

# Use in production
while True:
    # Reactive healing (automatic)
    event = coordinator.get_next_event()
    failure = self_healer.detect_failure(event)
    if failure:
        result = self_healer.heal(failure)

    # Proactive healing (predictive)
    recent_events = coordinator.get_recent_events()
    predictions = predictor.predict_failures(recent_events)
    for pred in predictions:
        if pred.confidence > 0.8:
            predictor.apply_preventive_healing(pred, auto_apply=True)

    # Monitor and optimize
    if time_to_report():
        stats = analytics.get_overall_stats()
        recommendations = analytics.generate_recommendations()
        send_to_monitoring(stats, recommendations)
```

## Configuration Best Practices

### CircuitBreaker

**Conservative** (low-risk systems):
```python
CircuitBreakerConfig(
    failure_threshold=10,
    success_threshold=3,
    timeout_seconds=300.0
)
```

**Aggressive** (high-availability systems):
```python
CircuitBreakerConfig(
    failure_threshold=3,
    success_threshold=2,
    timeout_seconds=30.0
)
```

### GradualDegradation

**Custom degradation levels**:
```python
DegradationConfig(
    timeout_multipliers={
        DegradationLevel.FULL: 1.0,
        DegradationLevel.REDUCED_1: 0.9,
        DegradationLevel.REDUCED_2: 0.7,
        DegradationLevel.REDUCED_3: 0.5,
        DegradationLevel.MINIMAL: 0.3,
    },
    quality_thresholds={
        DegradationLevel.FULL: 0.95,
        DegradationLevel.REDUCED_1: 0.90,
        # ... customize per level
    }
)
```

### PredictiveHealing

**High-confidence only** (reduce false positives):
```python
PredictiveHealing(
    pattern_learner=pattern_learner,
    self_healer=self_healer,
    confidence_threshold=0.85  # 85% minimum
)
```

**Balanced** (general use):
```python
PredictiveHealing(
    pattern_learner=pattern_learner,
    self_healer=self_healer,
    confidence_threshold=0.7  # 70% minimum
)
```

## Performance Characteristics

| Component | Operation | Time Complexity | Space |
|-----------|-----------|-----------------|-------|
| CircuitBreaker | heal() | O(1) | O(n) resources |
| GradualDegradation | heal() | O(1) | O(n) resources |
| PredictiveHealing | predict() | O(p × e) | O(p + e) |
| HealingAnalytics | stats() | O(h) | O(h) |

Where:
- n = number of tracked resources
- p = number of patterns
- e = number of events
- h = healing history size

## Testing

Run comprehensive tests:

```bash
# All advanced healing tests
pytest tests/moai_flow/optimization/test_circuit_breaker.py -v
pytest tests/moai_flow/optimization/test_gradual_degradation.py -v
pytest tests/moai_flow/optimization/test_predictive_healing.py -v
pytest tests/moai_flow/optimization/test_healing_analytics.py -v

# With coverage
pytest tests/moai_flow/optimization/ --cov=moai_flow.optimization.strategies --cov-report=html
```

## Examples

See `examples/advanced_healing_example.py` for complete workflow demonstration.

## Monitoring

Key metrics to monitor:

1. **Circuit Breaker**:
   - Circuit state transitions
   - Time in OPEN state
   - Half-open success rate

2. **Gradual Degradation**:
   - Current degradation level
   - Time at each level
   - Resource recovery rate

3. **Predictive Healing**:
   - Prediction accuracy
   - False positive rate
   - Preventive actions taken

4. **Overall**:
   - Healing success rate (target: > 85%)
   - MTTR (target: < 5s)
   - Prevention rate (predictions → actual failures)

## Troubleshooting

### Circuit stays OPEN

**Cause**: Timeout too short or underlying issue not resolved

**Solution**:
1. Increase `timeout_seconds`
2. Investigate root cause
3. Manually reset circuit: `strategy.reset("resource-id")`

### Degradation not recovering

**Cause**: Resource usage not decreasing

**Solution**:
1. Check resource monitoring
2. Implement cleanup actions
3. Manually reset: `strategy.reset("resource-type")`

### High false positive rate

**Cause**: Confidence threshold too low

**Solution**:
1. Increase `confidence_threshold`
2. Improve pattern learning
3. Record outcomes: `predictor.record_prediction_outcome()`

## Future Enhancements

Planned improvements:

- [ ] Machine learning integration for pattern prediction
- [ ] Multi-level circuit breakers (partial degradation)
- [ ] Automatic threshold tuning based on analytics
- [ ] Cross-resource correlation in predictions
- [ ] Real-time dashboard integration
- [ ] Custom degradation strategies per resource type

## References

- Phase 6C SelfHealer: `moai_flow/optimization/self_healer.py`
- PatternLearner: `moai_flow/optimization/pattern_learner.py`
- PRD-09 Specification: `moai_flow/specs/PRD-09-advanced-features.md`
- Examples: `moai_flow/optimization/examples/`

## Version

**Version**: 1.0.0
**Phase**: 7 (Track 3 Week 4-6)
**Status**: Complete
**Last Updated**: 2025-11-29
