# Performance Tuning - Advanced Optimization Patterns

Advanced techniques for maximizing multi-agent system performance through intelligent optimization strategies.

## Overview

This guide covers:
1. **Predictive Healing** - Prevent failures before they occur
2. **Dynamic Scaling** - Adaptive agent provisioning
3. **Token Optimization** - Maximize efficiency within budget
4. **Load Balancing** - Intelligent task distribution

## 1. Predictive Healing Implementation

### Basic Prediction Setup

```python
from moai_flow.optimization.predictive_healing import PredictiveHealing

# Initialize predictive healing
predictor = PredictiveHealing(
    pattern_learner=learner,
    self_healer=healer,
    bottleneck_detector=detector,
    confidence_threshold=0.7  # 70% confidence minimum
)

print("✓ Predictive healing initialized")
```

### Collecting Events for Prediction

```python
def collect_system_events(time_window_ms=60000):
    """Collect recent events for prediction analysis"""
    current_events = []

    # Resource metrics
    usage = resource_controller.get_resource_usage()
    current_events.append({
        "type": "resource_metric",
        "timestamp": datetime.now(timezone.utc),
        "metadata": {
            "token_usage_percent": (
                usage["tokens"]["consumed"] / usage["tokens"]["total_budget"] * 100
            ),
            "memory_usage_percent": usage.get("memory_usage_percent", 0),
            "queue_depth": usage["queue"]["pending_tasks"]
        }
    })

    # Task metrics
    recent_tasks = metrics_storage.get_task_metrics(
        time_range_ms=time_window_ms,
        limit=100
    )

    for task in recent_tasks:
        current_events.append({
            "type": "task_complete" if task["result"] == "success" else "task_failed",
            "timestamp": task["timestamp"],
            "agent_id": task["agent_id"],
            "duration_ms": task["duration_ms"],
            "result": task["result"]
        })

    return current_events
```

### Running Predictions

```python
# Collect recent events
current_events = collect_system_events(time_window_ms=60000)

# Predict failures
predictions = predictor.predict_failures(current_events)

print(f"\n🔮 Failure Predictions: {len(predictions)}")
print("=" * 60)

for pred in predictions:
    print(f"\nFailure Type: {pred.failure_type}")
    print(f"Confidence: {pred.confidence:.1%}")
    print(f"Expected in: {pred.expected_time_ms / 1000:.1f}s")
    print(f"Source: {pred.source}")
    print(f"Reasoning: {pred.reasoning}")
    print(f"Action: {pred.recommended_action}")
```

### Preventive Healing with Learning

```python
def preventive_healing_workflow(predictor, current_events):
    """
    Complete preventive healing workflow with outcome learning.

    Returns:
        dict: Healing results and statistics
    """
    # Predict failures
    predictions = predictor.predict_failures(current_events)

    results = {
        "total_predictions": len(predictions),
        "healings_applied": 0,
        "healings_successful": 0,
        "prevented_failures": 0
    }

    # Apply healing for high-confidence predictions
    for prediction in predictions:
        if prediction.confidence > 0.8:  # High confidence threshold
            # Apply preventive healing
            result = predictor.apply_preventive_healing(
                prediction,
                auto_apply=True
            )

            results["healings_applied"] += 1

            if result.success:
                results["healings_successful"] += 1
                logger.info(
                    f"✅ Prevented {prediction.failure_type} "
                    f"(confidence: {prediction.confidence:.1%})"
                )

            # Monitor for actual failure occurrence
            failure_occurred = monitor_for_failure(
                failure_type=prediction.failure_type,
                agent_id=prediction.agent_id,
                time_window_ms=prediction.expected_time_ms + 60000  # Add buffer
            )

            # Learn from outcome
            predictor.record_prediction_outcome(
                prediction,
                occurred=failure_occurred
            )

            if not failure_occurred:
                results["prevented_failures"] += 1

    return results
```

### Monitoring Prediction Accuracy

```python
# Get prediction statistics
stats = predictor.get_prediction_stats()

print(f"\n📊 Prediction Statistics")
print(f"=" * 60)
print(f"Total Predictions: {stats['total_predictions']}")
print(f"Outcomes Tracked: {stats['total_outcomes_tracked']}")
print(f"Overall Accuracy: {stats['overall_accuracy']:.1%}")
print(f"False Positive Rate: {stats['false_positive_rate']:.1%}")
print(f"Meets Target (>70%): {'✅' if stats['meets_target'] else '❌'}")

print(f"\nAccuracy Breakdown:")
for category, count in stats['accuracy_breakdown'].items():
    print(f"  {category.capitalize()}: {count} patterns")

if stats['recommendations']:
    print(f"\nRecommendations:")
    for rec in stats['recommendations']:
        print(f"  • {rec}")
```

## 2. Dynamic Agent Scaling

### Adaptive Scaling Implementation

```python
def adaptive_scaling_loop(
    detector,
    coordinator,
    config=None
):
    """
    Continuous adaptive scaling based on system load.

    Args:
        detector: BottleneckDetector instance
        coordinator: SwarmCoordinator instance
        config: Scaling configuration (optional)
    """
    # Default configuration
    if config is None:
        config = {
            "target_queue_depth": 30,
            "min_queue_depth": 10,
            "scale_up_threshold": 30,
            "scale_down_threshold": 10,
            "agents_per_threshold": 20,  # 1 agent per 20 tasks
            "cooldown_ms": 20000,        # 20s cooldown
            "max_agents": 50             # Maximum agents
        }

    last_scale_time = 0

    while True:
        try:
            # Check cooldown
            current_time = time.time() * 1000
            if current_time - last_scale_time < config["cooldown_ms"]:
                time.sleep(5)
                continue

            # Get current state
            usage = resource_controller.get_resource_usage()
            queue_depth = usage["queue"]["pending_tasks"]
            active_agents = usage["agents"]["active_agents"]

            # Scaling decision
            if queue_depth > config["scale_up_threshold"]:
                # Scale up
                overflow = queue_depth - config["target_queue_depth"]
                agents_needed = max(1, overflow // config["agents_per_threshold"])

                # Check max limit
                if active_agents + agents_needed <= config["max_agents"]:
                    logger.info(
                        f"📈 Scaling up: Adding {agents_needed} agents "
                        f"(queue: {queue_depth}, active: {active_agents})"
                    )

                    for i in range(agents_needed):
                        agent_id = f"dynamic-{int(time.time())}-{i}"
                        coordinator.register_agent(agent_id, {
                            "type": "dynamic",
                            "reason": "scale_up",
                            "queue_depth": queue_depth
                        })

                    last_scale_time = current_time

            elif queue_depth < config["scale_down_threshold"]:
                # Scale down
                topology = coordinator.get_topology_info()
                dynamic_agents = [
                    agent for agent in topology.get("agents", [])
                    if agent.get("metadata", {}).get("type") == "dynamic"
                    and agent.get("current_task") is None  # Idle only
                ]

                if dynamic_agents:
                    # Keep at least 1 dynamic agent
                    agents_to_remove = max(0, len(dynamic_agents) - 1)

                    if agents_to_remove > 0:
                        logger.info(
                            f"📉 Scaling down: Removing {agents_to_remove} idle agents "
                            f"(queue: {queue_depth})"
                        )

                        for agent in dynamic_agents[:agents_to_remove]:
                            coordinator.unregister_agent(agent["agent_id"])

                        last_scale_time = current_time

        except Exception as e:
            logger.error(f"Scaling error: {e}")

        time.sleep(10)  # Check every 10 seconds
```

## 3. Token Budget Optimization

### Token-Aware Task Prioritization

```python
def optimize_task_queue_for_tokens(
    detector,
    task_queue,
    aggressive_mode=False
):
    """
    Optimize task queue to maximize completion within token budget.

    Args:
        detector: BottleneckDetector instance
        task_queue: List of pending tasks
        aggressive_mode: If True, defer more aggressively

    Returns:
        dict: Optimization results
    """
    # Detect token exhaustion
    bottlenecks = detector.detect_bottlenecks()
    token_bottleneck = next(
        (b for b in bottlenecks if b.bottleneck_type == "token_exhaustion"),
        None
    )

    if not token_bottleneck:
        return {"status": "no_optimization_needed"}

    usage_ratio = token_bottleneck.metrics["usage_ratio"]
    remaining = token_bottleneck.metrics["remaining"]

    # Calculate efficiency scores
    for task in task_queue:
        priority = task.get("priority", "MEDIUM")
        estimated_tokens = task.get("estimated_tokens", 1000)

        # Priority weights
        weights = {
            "CRITICAL": 10,
            "HIGH": 5,
            "MEDIUM": 2,
            "LOW": 1
        }

        # Efficiency = Value / Cost
        efficiency = weights.get(priority, 1) / estimated_tokens
        task["efficiency_score"] = efficiency

    # Sort by efficiency (highest first)
    task_queue.sort(key=lambda t: t["efficiency_score"], reverse=True)

    # Calculate feasible tasks
    active_tasks = []
    deferred_tasks = []
    cumulative_tokens = 0

    threshold = 0.95 if aggressive_mode else 0.90  # Use 90-95% of remaining

    for task in task_queue:
        estimated_tokens = task.get("estimated_tokens", 1000)

        if cumulative_tokens + estimated_tokens <= remaining * threshold:
            active_tasks.append(task)
            cumulative_tokens += estimated_tokens
        else:
            deferred_tasks.append(task)
            task["deferred_reason"] = "insufficient_tokens"

    return {
        "status": "optimized",
        "usage_ratio": usage_ratio,
        "remaining_tokens": remaining,
        "active_tasks": len(active_tasks),
        "deferred_tasks": len(deferred_tasks),
        "estimated_consumption": cumulative_tokens,
        "utilization": cumulative_tokens / remaining if remaining > 0 else 0
    }
```

### Token Budget Monitoring

```python
def monitor_token_consumption(
    detector,
    alert_threshold=0.8,
    critical_threshold=0.9
):
    """Monitor token consumption and send alerts"""
    usage = resource_controller.get_resource_usage()
    tokens = usage["tokens"]

    total = tokens["total_budget"]
    consumed = tokens["consumed"]
    remaining = tokens["remaining"]
    ratio = consumed / total

    status = {
        "total_budget": total,
        "consumed": consumed,
        "remaining": remaining,
        "usage_ratio": ratio,
        "status": "normal"
    }

    if ratio >= critical_threshold:
        status["status"] = "critical"
        logger.error(
            f"🚨 CRITICAL: Token usage at {ratio:.1%} "
            f"({remaining} tokens remaining)"
        )

        # Trigger aggressive optimization
        optimize_task_queue_for_tokens(
            detector,
            task_queue,
            aggressive_mode=True
        )

    elif ratio >= alert_threshold:
        status["status"] = "warning"
        logger.warning(
            f"⚠️  WARNING: Token usage at {ratio:.1%} "
            f"({remaining} tokens remaining)"
        )

        # Trigger normal optimization
        optimize_task_queue_for_tokens(
            detector,
            task_queue,
            aggressive_mode=False
        )

    return status
```

## 4. Intelligent Load Balancing

### Health-Based Agent Selection

```python
def select_optimal_agent(
    task,
    available_agents,
    metrics_storage
):
    """
    Select best agent for task using health scoring.

    Scoring factors:
    - Success rate (40%)
    - Response time (30%)
    - Current load (20%)
    - Task affinity (10%)
    """
    if not available_agents:
        return None

    agent_scores = {}

    for agent_id in available_agents:
        # Get recent performance
        recent_tasks = metrics_storage.get_task_metrics_by_agent(
            agent_id=agent_id,
            time_range_ms=60000,
            limit=50
        )

        if not recent_tasks:
            agent_scores[agent_id] = 0.5  # Neutral for new agents
            continue

        # Success rate (40%)
        success_count = sum(
            1 for t in recent_tasks
            if t.get("result") == "success"
        )
        success_rate = success_count / len(recent_tasks)
        success_score = success_rate * 0.4

        # Response time (30%)
        avg_duration = statistics.mean([
            t.get("duration_ms", 0)
            for t in recent_tasks
        ])
        target_duration = 3000  # 3s target
        time_score = max(0, 1 - (avg_duration / target_duration)) * 0.3

        # Current load (20%)
        current_load = get_agent_current_load(agent_id)
        max_load = 3  # Max concurrent tasks
        load_ratio = current_load / max_load
        load_score = max(0, 1 - load_ratio) * 0.2

        # Task affinity (10%) - agent specialization
        affinity_score = calculate_task_affinity(
            task,
            agent_id,
            recent_tasks
        ) * 0.1

        # Total score
        total_score = (
            success_score +
            time_score +
            load_score +
            affinity_score
        )

        agent_scores[agent_id] = total_score

    # Select agent with highest score
    best_agent = max(agent_scores, key=agent_scores.get)

    logger.info(
        f"Selected {best_agent} for task "
        f"(score: {agent_scores[best_agent]:.2f})"
    )

    return best_agent

def calculate_task_affinity(task, agent_id, recent_tasks):
    """Calculate agent's affinity for task type"""
    task_type = task.get("type", "unknown")

    # Count similar tasks completed successfully
    similar_tasks = [
        t for t in recent_tasks
        if t.get("type") == task_type
        and t.get("result") == "success"
    ]

    if not recent_tasks:
        return 0.5  # Neutral

    # Affinity = proportion of similar successful tasks
    return len(similar_tasks) / len(recent_tasks)
```

## 5. Complete Performance Tuning Example

```python
#!/usr/bin/env python3
"""Advanced Performance Tuning Example"""

import threading
import time
from moai_flow.optimization import (
    BottleneckDetector,
    PatternLearner,
    SelfHealer,
)
from moai_flow.optimization.predictive_healing import PredictiveHealing

class PerformanceTuner:
    def __init__(
        self,
        detector,
        predictor,
        coordinator,
        resource_controller
    ):
        self.detector = detector
        self.predictor = predictor
        self.coordinator = coordinator
        self.resource_controller = resource_controller
        self.running = False

    def start(self):
        """Start all optimization loops"""
        self.running = True

        # Start loops in separate threads
        threading.Thread(
            target=self._predictive_healing_loop,
            daemon=True
        ).start()

        threading.Thread(
            target=self._scaling_loop,
            daemon=True
        ).start()

        threading.Thread(
            target=self._token_monitoring_loop,
            daemon=True
        ).start()

        logger.info("✓ Performance tuning started")

    def _predictive_healing_loop(self):
        """Continuous predictive healing"""
        while self.running:
            try:
                events = collect_system_events(60000)
                results = preventive_healing_workflow(
                    self.predictor,
                    events
                )

                if results["healings_applied"] > 0:
                    logger.info(
                        f"Preventive: {results['healings_successful']}/"
                        f"{results['healings_applied']} successful"
                    )

            except Exception as e:
                logger.error(f"Predictive healing error: {e}")

            time.sleep(30)

    def _scaling_loop(self):
        """Continuous adaptive scaling"""
        adaptive_scaling_loop(
            self.detector,
            self.coordinator
        )

    def _token_monitoring_loop(self):
        """Continuous token monitoring"""
        while self.running:
            try:
                status = monitor_token_consumption(
                    self.detector,
                    alert_threshold=0.8,
                    critical_threshold=0.9
                )

                if status["status"] != "normal":
                    logger.warning(
                        f"Token status: {status['status']} "
                        f"({status['usage_ratio']:.1%})"
                    )

            except Exception as e:
                logger.error(f"Token monitoring error: {e}")

            time.sleep(15)

    def stop(self):
        """Stop all loops"""
        self.running = False

# Usage
tuner = PerformanceTuner(
    detector=detector,
    predictor=predictor,
    coordinator=coordinator,
    resource_controller=resource_controller
)

tuner.start()

# System runs with automatic optimization
# ...

# Later, stop tuning
tuner.stop()
```

## Best Practices

1. **Set appropriate thresholds**: Balance sensitivity vs. stability
2. **Monitor prediction accuracy**: Track and improve over time
3. **Use aggressive mode carefully**: Only when token exhaustion imminent
4. **Scale gradually**: Avoid rapid scaling oscillations
5. **Review metrics regularly**: Weekly analysis of effectiveness
6. **Tune for your workload**: Adjust based on observed patterns

## Performance Metrics

**Target Performance**:
- Prediction accuracy: >70%
- Healing success rate: >85%
- Token utilization: 80-90%
- Agent utilization: 70-80%
- Queue depth: <30 tasks

## Next Steps

- [Advanced Healing](advanced-healing.md) - Custom strategies and analytics
- [Resource Allocation Module](../modules/resource-allocation.md) - Detailed scaling algorithms
