# Predictive Healing Module

Prevent failures before they occur using pattern analysis, resource trend monitoring, and historical data (>70% accuracy target).

## Overview

PredictiveHealing analyzes system behavior to predict failures BEFORE they happen, enabling proactive intervention and prevention.

**Key Features**:
- Pattern-based failure prediction
- Resource trend analysis
- Agent health degradation monitoring
- Queue depth trend analysis
- Confidence-based predictions (0.0-1.0)
- Learning from prediction outcomes
- False positive mitigation

## Architecture

```
PredictiveHealing
├── Prediction Sources (5 types)
│   ├── Pattern Analysis (_analyze_pattern_for_failure)
│   ├── Resource Trends (_analyze_resource_trends)
│   ├── Bottleneck Integration (_analyze_bottlenecks)
│   ├── Agent Health (_analyze_agent_health)
│   └── Queue Trends (_analyze_queue_trends)
├── Confidence Calculation
│   ├── _calculate_confidence()
│   ├── _calculate_recency_score()
│   └── Pattern accuracy tracking
├── Preventive Healing
│   ├── apply_preventive_healing()
│   └── SelfHealer integration
└── Learning System
    ├── record_prediction_outcome()
    ├── _handle_false_positive()
    └── get_prediction_stats()
```

## Prediction Sources

### 1. Pattern-Based Prediction

**Purpose**: Identify failure patterns from historical event sequences.

**Pattern Types**:
- **Sequence patterns**: Event chains leading to failures
- **Frequency patterns**: Regular failure occurrences
- **Correlation patterns**: Co-occurring failure events
- **Temporal patterns**: Time-based failure patterns

**Failure Indicators**:
```python
failure_indicators = {
    "heartbeat_failed": "agent_down",
    "task_timeout": "task_failed",
    "high_latency": "resource_exhaustion",
    "memory_pressure": "memory_exhaustion",
    "token_warning": "token_exhaustion"
}
```

**Algorithm**:
```python
def _analyze_pattern_for_failure(pattern, current_events):
    # Check pattern events for failure indicators
    for event in pattern.events:
        event_type = event.get("type", "")

        if event_type in failure_indicators:
            failure_type = failure_indicators[event_type]

            # Estimate time to failure based on pattern frequency
            expected_time_ms = _estimate_time_to_failure(pattern)

            return PredictedFailure(
                failure_type=failure_type,
                confidence=0.0,  # Calculated later
                expected_time_ms=expected_time_ms,
                reasoning=f"Pattern '{pattern.description}' indicates {failure_type}",
                recommended_action=_recommend_action_for_type(failure_type),
                source="pattern"
            )
```

### 2. Resource Trend Analysis

**Purpose**: Predict resource exhaustion from usage trends.

**Monitored Resources**:
- **Token usage**: Consumption rate and remaining budget
- **Memory usage**: Allocation trends
- **Queue depth**: Task accumulation rate
- **Response time**: Latency trends

**Token Exhaustion Prediction**:
```python
def _analyze_resource_trends(current_events):
    # Collect token usage from events
    token_usage = []
    for event in current_events:
        if event.get("type") == "resource_metric":
            metadata = event.get("metadata", {})
            token_usage.append(metadata.get("token_usage_percent", 0))

    # Analyze trend
    if len(token_usage) >= 3:
        trend = _calculate_trend(token_usage)  # Average change per measurement
        current = token_usage[-1]

        if trend > 0 and current > 80:  # Increasing and high
            # Estimate time to exhaustion
            remaining = 100.0 - current
            measurements_until_exhaustion = remaining / trend
            time_to_exhaustion = int(measurements_until_exhaustion * 10000)  # 10s per measurement

            return PredictedFailure(
                failure_type="token_exhaustion",
                confidence=min(current / 100.0, 1.0),
                expected_time_ms=time_to_exhaustion,
                reasoning=f"Token usage trending upward: {current:.1f}% (trend: +{trend:.1f}%)",
                recommended_action="Reduce task load or clear context",
                source="trend"
            )
```

### 3. Bottleneck Integration

**Purpose**: Convert detected bottlenecks into failure predictions.

**Severity to Confidence Mapping**:
- **Critical**: 0.95 confidence
- **High**: 0.85 confidence
- **Medium**: 0.75 confidence
- **Low**: 0.65 confidence

**Time to Failure Estimation**:
- **Critical**: 60,000ms (1 minute)
- **High**: 180,000ms (3 minutes)
- **Medium**: 300,000ms (5 minutes)
- **Low**: 600,000ms (10 minutes)

```python
def _analyze_bottlenecks():
    bottlenecks = self.bottleneck_detector.detect_bottlenecks()

    predictions = []
    for bottleneck in bottlenecks:
        # Map severity to confidence
        confidence = {
            "critical": 0.95,
            "high": 0.85,
            "medium": 0.75,
            "low": 0.65
        }[bottleneck.severity]

        # Map bottleneck type to failure type
        failure_type = {
            "token_exhaustion": "token_exhaustion",
            "quota_exceeded": "resource_exhaustion",
            "slow_agent": "agent_down",
            "task_queue_backlog": "task_timeout"
        }[bottleneck.bottleneck_type]

        predictions.append(PredictedFailure(
            failure_type=failure_type,
            confidence=confidence,
            expected_time_ms=time_to_failure[bottleneck.severity],
            reasoning=f"Bottleneck: {bottleneck.bottleneck_type} ({bottleneck.severity})",
            recommended_action=bottleneck.recommendations[0],
            source="bottleneck"
        ))

    return predictions
```

### 4. Agent Health Degradation

**Purpose**: Detect agents showing signs of impending failure.

**Monitored Metrics**:
- Success rate trends
- Response time trends
- Heartbeat regularity
- Error frequency

**Degrading Agent Detection**:
```python
def _analyze_agent_health(current_events):
    # Collect agent health metrics
    agent_metrics = defaultdict(lambda: {
        "success_count": 0,
        "failure_count": 0,
        "response_times": []
    })

    for event in current_events:
        event_type = event.get("type", "")
        agent_id = event.get("agent_id")

        if event_type == "task_complete":
            agent_metrics[agent_id]["success_count"] += 1
            agent_metrics[agent_id]["response_times"].append(event["duration_ms"])
        elif event_type == "task_failed":
            agent_metrics[agent_id]["failure_count"] += 1

    # Analyze each agent
    predictions = []
    for agent_id, metrics in agent_metrics.items():
        total_tasks = metrics["success_count"] + metrics["failure_count"]
        success_rate = metrics["success_count"] / total_tasks

        # Degrading agent (success rate < 70%)
        if success_rate < 0.7:
            confidence = 1.0 - success_rate  # Lower success = higher confidence

            predictions.append(PredictedFailure(
                failure_type="agent_down",
                agent_id=agent_id,
                confidence=min(confidence, 1.0),
                expected_time_ms=120000,  # 2 minutes
                reasoning=f"Agent {agent_id} degrading: {success_rate:.1%} success rate",
                recommended_action="Proactively restart agent",
                source="health"
            ))

    return predictions
```

### 5. Queue Depth Analysis

**Purpose**: Predict task timeouts from queue backlog growth.

**Monitored Metrics**:
- Queue depth growth rate
- High-priority task accumulation
- Processing rate vs. submission rate

```python
def _analyze_queue_trends(current_events):
    # Collect queue metrics
    queue_depths = []
    for event in current_events:
        if event.get("type") == "queue_metric":
            queue_depths.append(event["metadata"]["queue_depth"])

    # Analyze trend
    if len(queue_depths) >= 3:
        trend = _calculate_trend(queue_depths)
        current_depth = queue_depths[-1]

        if trend > 0 and current_depth > 50:
            # Estimate time to critical backlog (200 tasks)
            remaining = 200 - current_depth
            time_to_critical = (remaining / max(trend, 1)) * 10000

            confidence = min((current_depth / 100.0) + (trend / 20.0), 1.0)

            return PredictedFailure(
                failure_type="task_timeout",
                confidence=confidence,
                expected_time_ms=int(time_to_critical),
                reasoning=f"Queue backlog growing: {current_depth} tasks (trend: +{trend:.1f})",
                recommended_action="Increase agent quota to process queue faster",
                source="queue"
            )
```

## Confidence Calculation

### Multi-Factor Confidence Score

**Formula**:
```
Total Confidence = (Pattern Match × 0.5) + (Historical Accuracy × 0.3) + (Recency × 0.2)
```

**Components**:

1. **Pattern Match Similarity** (50%):
   - Based on pattern confidence from PatternLearner
   - Measures how closely current events match learned pattern

2. **Historical Accuracy** (30%):
   - Tracks correct predictions vs. false positives
   - Weighted by pattern performance history

3. **Recency Factor** (20%):
   - Recent patterns score higher
   - Scores: <1min (1.0), <5min (0.8), <10min (0.6), <30min (0.4), else (0.2)

**Implementation**:
```python
def _calculate_confidence(pattern, current_events):
    # Pattern match similarity (50%)
    pattern_score = pattern.confidence * 0.5

    # Historical accuracy (30%)
    accuracy_stats = self._pattern_accuracy.get(pattern.pattern_id, {})
    correct = accuracy_stats.get("correct", 0)
    false_positive = accuracy_stats.get("false_positive", 0)
    total = correct + false_positive

    if total > 0:
        historical_accuracy = (correct / total) * 0.3
    else:
        historical_accuracy = 0.15  # Neutral for new patterns

    # Recency factor (20%)
    recency_score = _calculate_recency_score(pattern) * 0.2

    return min(pattern_score + historical_accuracy + recency_score, 1.0)
```

### Confidence Threshold

**Default**: 0.7 (70%)

Predictions below threshold are filtered out to reduce false positives.

**Threshold Tuning**:
- **Lower (0.6)**: More predictions, higher false positive rate
- **Higher (0.8)**: Fewer predictions, lower false positive rate
- **Optimal**: Balance accuracy vs. coverage

## Preventive Healing

### Automatic Healing Application

**Purpose**: Apply healing BEFORE failure occurs.

**Modes**:
1. **Auto-apply**: Automatically execute healing for high-confidence predictions
2. **Manual approval**: Queue predictions for user review

**Implementation**:
```python
def apply_preventive_healing(prediction, auto_apply=False):
    # Create synthetic failure for preventive healing
    failure = Failure(
        failure_id=f"predicted_{prediction.failure_type}_{timestamp}",
        failure_type=prediction.failure_type,
        agent_id=prediction.agent_id,
        severity="medium",
        detected_at=datetime.now(timezone.utc),
        event={"type": "predicted_failure"},
        metadata={
            "predicted": True,
            "confidence": prediction.confidence,
            "expected_time_ms": prediction.expected_time_ms,
            "auto_applied": auto_apply
        }
    )

    if auto_apply:
        # Execute healing immediately
        result = self.self_healer.heal(failure)
    else:
        # Queue for manual approval
        result = HealingResult(
            success=False,
            failure_id=failure.failure_id,
            strategy_used="PredictiveHealing",
            actions_taken=["Queued for manual approval"],
            metadata={"manual_approval_required": True}
        )

    return result
```

**Usage Example**:
```python
predictions = predictor.predict_failures(current_events)

for pred in predictions:
    if pred.confidence > 0.8:  # High confidence
        # Automatically apply healing
        result = predictor.apply_preventive_healing(pred, auto_apply=True)

        if result.success:
            logger.info(f"Preventive healing successful: {pred.failure_type}")
```

## Learning System

### Prediction Outcome Recording

**Purpose**: Track prediction accuracy to improve future predictions.

**Process**:
1. Make prediction
2. Monitor for actual failure occurrence
3. Record outcome (occurred or false positive)
4. Update pattern accuracy statistics
5. Adjust confidence calculations

**Implementation**:
```python
def record_prediction_outcome(prediction, occurred):
    # Update pattern accuracy tracking
    for pattern_id in prediction.pattern_indicators:
        self._pattern_accuracy[pattern_id]["total"] += 1

        if occurred:
            # Correct prediction
            self._pattern_accuracy[pattern_id]["correct"] += 1
        else:
            # False positive
            self._pattern_accuracy[pattern_id]["false_positive"] += 1
            self._false_positive_count += 1

            # Handle false positive
            _handle_false_positive(prediction, pattern_id)
```

### False Positive Handling

**Purpose**: Learn from incorrect predictions to reduce future false positives.

**Actions**:
1. Lower pattern confidence in accuracy tracking
2. Increase confidence threshold for pattern type
3. Log pattern characteristics for analysis
4. Suggest pattern refinement if FP rate > 30%

**Implementation**:
```python
def _handle_false_positive(prediction, pattern_id):
    stats = self._pattern_accuracy[pattern_id]
    total = stats["total"]
    false_positives = stats["false_positive"]

    if total > 0:
        fp_rate = false_positives / total

        # High false positive rate (>30%)
        if fp_rate > 0.3:
            logger.warning(
                f"High false positive rate for pattern {pattern_id}: "
                f"{fp_rate:.1%} ({false_positives}/{total})"
            )

            logger.info(
                f"Consider refining pattern {pattern_id} or "
                f"increasing confidence threshold"
            )

    # Store for future analysis
    self._false_positive_details.append({
        "prediction_id": prediction.prediction_id,
        "pattern_id": pattern_id,
        "failure_type": prediction.failure_type,
        "confidence": prediction.confidence,
        "reasoning": prediction.reasoning
    })
```

### Prediction Statistics

**Purpose**: Monitor prediction system performance.

**Metrics**:
- Overall accuracy (correct / total)
- False positive rate
- Per-pattern accuracy
- Per-source accuracy (pattern/trend/health/queue/bottleneck)
- Recommendations for improvement

**Example**:
```python
stats = predictor.get_prediction_stats()

{
    "total_predictions": 1234,
    "total_outcomes_tracked": 1000,
    "overall_accuracy": 0.75,  # 75% accuracy
    "false_positive_rate": 0.15,  # 15% FP rate
    "target_accuracy": 0.7,
    "meets_target": True,
    "pattern_accuracy": {
        "pattern-001": {
            "correct": 45,
            "false_positive": 5,
            "total": 50,
            "accuracy": 0.90,
            "fp_rate": 0.10
        }
    },
    "recommendations": [
        "Overall accuracy (75%) above target (70%)",
        "Pattern pattern-002 has low accuracy (55%). Consider removing or refining."
    ]
}
```

## Usage Examples

### Basic Prediction

```python
from moai_flow.optimization.predictive_healing import PredictiveHealing

predictor = PredictiveHealing(
    pattern_learner=pattern_learner,
    self_healer=self_healer,
    bottleneck_detector=bottleneck_detector,
    confidence_threshold=0.7
)

# Collect recent events
current_events = [
    {"type": "resource_metric", "metadata": {"token_usage_percent": 85}},
    {"type": "task_complete", "duration_ms": 8000, "result": "success"},
    {"type": "heartbeat", "agent_id": "agent-001"}
]

# Predict failures
predictions = predictor.predict_failures(current_events)

for pred in predictions:
    print(f"Failure Type: {pred.failure_type}")
    print(f"Confidence: {pred.confidence:.1%}")
    print(f"Expected in: {pred.expected_time_ms}ms")
    print(f"Source: {pred.source}")
    print(f"Action: {pred.recommended_action}")
```

### Preventive Healing Workflow

```python
# Predict failures
predictions = predictor.predict_failures(current_events)

# Apply preventive healing for high-confidence predictions
for prediction in predictions:
    if prediction.confidence > 0.8:
        # Auto-apply healing
        result = predictor.apply_preventive_healing(prediction, auto_apply=True)

        if result.success:
            logger.info(f"Prevented {prediction.failure_type}")

        # Monitor for actual failure
        failure_occurred = monitor_system(prediction.expected_time_ms)

        # Learn from outcome
        predictor.record_prediction_outcome(prediction, occurred=failure_occurred)
```

### Accuracy Monitoring

```python
# Get prediction statistics
stats = predictor.get_prediction_stats()

print(f"Overall Accuracy: {stats['overall_accuracy']:.1%}")
print(f"False Positive Rate: {stats['false_positive_rate']:.1%}")
print(f"Meets Target (>70%): {stats['meets_target']}")

# Per-pattern analysis
for pattern_id, pattern_stats in stats['pattern_accuracy'].items():
    print(f"Pattern {pattern_id}:")
    print(f"  Accuracy: {pattern_stats['accuracy']:.1%}")
    print(f"  FP Rate: {pattern_stats['fp_rate']:.1%}")

# Recommendations
for rec in stats['recommendations']:
    print(f"Recommendation: {rec}")
```

## Best Practices

1. **Set appropriate confidence threshold**: 0.7 balances accuracy vs. coverage
2. **Record all outcomes**: Essential for learning and improvement
3. **Monitor false positive rate**: Should be <30% for production use
4. **Use multiple sources**: Combine pattern/trend/health analysis
5. **Integrate with SelfHealer**: Automatic preventive healing for high confidence
6. **Review statistics regularly**: Track accuracy and refine patterns

## Performance Characteristics

**Prediction Time**: <1s for 100 events
**Accuracy Target**: >70% (configurable)
**False Positive Rate**: <30% (with learning)
**Memory**: O(n) where n = prediction history size (max 1000)
**Thread Safety**: RLock for concurrent access

## Related Documentation

- [Bottleneck Detection Module](bottleneck-detection.md) - Bottleneck integration
- [Performance Monitoring Module](performance-monitoring.md) - Pattern learning
- [Self-Healing Module](../SKILL.md#3-self-healing---automatic-failure-recovery) - Healing application
