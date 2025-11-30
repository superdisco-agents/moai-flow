# Resource Allocation Module

Dynamic resource optimization, adaptive agent scaling, and intelligent task prioritization for multi-agent AI systems.

## Overview

Resource allocation optimizes system performance through:

1. **Dynamic Agent Scaling** - Automatic agent count adjustment based on load
2. **Token-Aware Prioritization** - Intelligent task ordering to conserve tokens
3. **Load Balancing** - Even distribution across healthy agents
4. **Capacity Planning** - Proactive resource provisioning

## Resource Types

### 1. Agent Quotas

**Definition**: Maximum concurrent agents allowed per agent type.

**Quota Management**:
```python
# Current quota usage
usage = resource_controller.get_resource_usage()
agents_info = usage.get("agents", {})

{
    "total_quotas": 20,        # Maximum agents allowed
    "active_agents": 15,       # Currently active
    "available_slots": 5,      # Remaining capacity
    "by_type": {
        "backend": {"quota": 10, "active": 7},
        "frontend": {"quota": 10, "active": 8}
    }
}
```

**Scaling Strategy**:
- **Scale Up**: When queue depth > target AND quota available
- **Scale Down**: When idle agents > threshold AND queue depth < minimum
- **Hold**: When system balanced

### 2. Token Budget

**Definition**: Total tokens available for AI model interactions.

**Token Management**:
```python
tokens = usage.get("tokens", {})

{
    "total_budget": 200000,    # Total available
    "consumed": 150000,        # Used so far
    "remaining": 50000,        # Still available
    "usage_ratio": 0.75,       # 75% consumed
    "avg_per_task": 1500       # Average consumption
}
```

**Conservation Strategies**:
- **Task Prioritization**: High-value, low-cost tasks first
- **Context Optimization**: Clear context when usage > 80%
- **Prompt Optimization**: Reduce token-heavy prompts
- **Caching**: Reuse responses for similar queries

### 3. Task Queue

**Definition**: Pending tasks awaiting agent assignment.

**Queue Management**:
```python
queue_info = usage.get("queue", {})

{
    "pending_tasks": 45,       # Total waiting
    "by_priority": {
        "CRITICAL": 5,
        "HIGH": 15,
        "MEDIUM": 20,
        "LOW": 5
    },
    "avg_wait_time_ms": 2000,  # Average wait
    "oldest_task_age_ms": 8000 # Oldest task wait time
}
```

**Optimization Strategies**:
- **Priority-Based**: Process critical tasks first
- **FIFO**: First-in-first-out for same priority
- **Deadline-Aware**: Prioritize tasks near deadline
- **Batch Processing**: Group similar tasks

## Dynamic Agent Scaling

### Adaptive Scaling Algorithm

**Purpose**: Automatically adjust agent count based on system load.

**Scaling Criteria**:

| Metric | Scale Up Threshold | Scale Down Threshold |
|--------|-------------------|---------------------|
| Queue Depth | >30 tasks | <10 tasks |
| Wait Time | >5 seconds | <1 second |
| Agent Utilization | >80% | <20% |
| Quota Available | Yes | N/A |

**Implementation**:
```python
def adaptive_agent_scaling(
    detector,
    coordinator,
    target_queue_depth=30,
    min_queue_depth=10
):
    """
    Automatically scale agent count based on queue depth.

    Args:
        detector: BottleneckDetector for system analysis
        coordinator: SwarmCoordinator for agent management
        target_queue_depth: Desired queue depth (scale up if exceeded)
        min_queue_depth: Minimum queue depth (scale down if below)
    """
    bottlenecks = detector.detect_bottlenecks()

    for bottleneck in bottlenecks:
        if bottleneck.bottleneck_type == "task_queue_backlog":
            current_depth = bottleneck.metrics.get("pending_tasks", 0)

            # Scale up if queue too large
            if current_depth > target_queue_depth:
                overflow = current_depth - target_queue_depth
                additional_agents = max(1, overflow // 10)  # 1 agent per 10 tasks

                logger.info(f"Scaling up: Adding {additional_agents} agents")

                for i in range(additional_agents):
                    agent_id = f"dynamic-agent-{int(time.time())}-{i}"
                    coordinator.register_agent(agent_id, {
                        "type": "dynamic",
                        "spawned_at": datetime.now(timezone.utc).isoformat(),
                        "reason": "queue_backlog"
                    })

    # Scale down if queue too small
    usage = detector._resources.get_resource_usage()
    queue_depth = usage.get("queue", {}).get("pending_tasks", 0)

    if queue_depth < min_queue_depth:
        # Identify idle dynamic agents
        topology = coordinator.get_topology_info()
        dynamic_agents = [
            agent for agent in topology.get("agents", [])
            if agent.get("metadata", {}).get("type") == "dynamic"
            and agent.get("current_task") is None
        ]

        # Remove excess idle agents (keep at least 1)
        excess_count = max(0, len(dynamic_agents) - 1)

        for agent in dynamic_agents[:excess_count]:
            logger.info(f"Scaling down: Removing idle agent {agent['agent_id']}")
            coordinator.unregister_agent(agent["agent_id"])
```

### Scaling Policies

**Aggressive Scaling** (High throughput):
```python
policy = {
    "scale_up_threshold": 20,    # Queue depth
    "scale_down_threshold": 5,
    "agents_per_threshold": 15,  # 1 agent per 15 tasks
    "cooldown_ms": 10000         # 10s cooldown
}
```

**Conservative Scaling** (Resource optimization):
```python
policy = {
    "scale_up_threshold": 50,
    "scale_down_threshold": 15,
    "agents_per_threshold": 25,
    "cooldown_ms": 30000
}
```

**Balanced Scaling** (Default):
```python
policy = {
    "scale_up_threshold": 30,
    "scale_down_threshold": 10,
    "agents_per_threshold": 20,
    "cooldown_ms": 20000
}
```

## Token-Aware Prioritization

### Efficiency-Based Task Ordering

**Purpose**: Maximize task completion within token budget constraints.

**Efficiency Score Calculation**:
```python
def calculate_task_efficiency(task):
    """
    Calculate task efficiency score.

    Efficiency = Priority Weight / Estimated Token Cost

    Higher efficiency = more value per token
    """
    priority_weights = {
        "CRITICAL": 10,
        "HIGH": 5,
        "MEDIUM": 2,
        "LOW": 1
    }

    priority = task.get("priority", "MEDIUM")
    estimated_tokens = task.get("estimated_tokens", 1000)

    weight = priority_weights.get(priority, 1)
    efficiency = weight / estimated_tokens

    return efficiency
```

**Optimization Algorithm**:
```python
def optimize_token_allocation(
    detector,
    task_queue,
    token_budget
):
    """
    Prioritize tasks based on token efficiency.

    Strategy:
    1. Identify token exhaustion risk
    2. Calculate efficiency score for each task
    3. Re-order queue by efficiency (high → low)
    4. Defer low-priority, high-cost tasks
    """
    bottlenecks = detector.detect_bottlenecks()

    for bottleneck in bottlenecks:
        if bottleneck.bottleneck_type == "token_exhaustion":
            usage_ratio = bottleneck.metrics.get("usage_ratio", 0)
            remaining = bottleneck.metrics.get("remaining", 0)

            if usage_ratio > 0.8:  # Critical token usage
                logger.warning(f"Token conservation mode: {remaining} tokens remaining")

                # Calculate efficiency for all tasks
                for task in task_queue:
                    task["efficiency_score"] = calculate_task_efficiency(task)

                # Re-prioritize queue
                task_queue.sort(
                    key=lambda t: t.get("efficiency_score", 0),
                    reverse=True  # Highest efficiency first
                )

                # Defer low-efficiency tasks
                deferred = []
                cumulative_tokens = 0

                for task in task_queue:
                    estimated_tokens = task.get("estimated_tokens", 1000)

                    if cumulative_tokens + estimated_tokens <= remaining:
                        cumulative_tokens += estimated_tokens
                    else:
                        # Defer task (insufficient tokens)
                        deferred.append(task)
                        task["deferred_reason"] = "insufficient_tokens"

                logger.info(
                    f"Optimized queue: {len(task_queue) - len(deferred)} tasks, "
                    f"{len(deferred)} deferred"
                )

                return {
                    "active_tasks": len(task_queue) - len(deferred),
                    "deferred_tasks": len(deferred),
                    "estimated_tokens": cumulative_tokens,
                    "remaining_tokens": remaining
                }
```

### Token Budget Planning

**Purpose**: Estimate token requirements and plan allocation.

**Estimation Model**:
```python
def estimate_task_tokens(task):
    """
    Estimate token usage for task.

    Factors:
    - Task complexity (simple/medium/complex)
    - Input size (characters)
    - Expected output size
    - Historical average for similar tasks
    """
    complexity_multipliers = {
        "simple": 0.5,
        "medium": 1.0,
        "complex": 2.0
    }

    base_tokens = 1000  # Base estimate
    complexity = task.get("complexity", "medium")
    input_length = len(task.get("input", ""))

    # Calculate estimate
    multiplier = complexity_multipliers.get(complexity, 1.0)
    input_factor = input_length / 100  # 100 chars ≈ 75 tokens

    estimated = int(base_tokens * multiplier + input_factor * 75)

    return estimated
```

## Load Balancing

### Weighted Distribution

**Purpose**: Distribute tasks across agents based on health and capacity.

**Health Score Calculation**:
```python
def calculate_agent_health_score(agent_id, metrics_storage):
    """
    Calculate agent health score (0.0-1.0).

    Factors:
    - Success rate (40%)
    - Average response time (30%)
    - Current load (20%)
    - Heartbeat regularity (10%)
    """
    # Get recent metrics
    task_metrics = metrics_storage.get_task_metrics_by_agent(
        agent_id=agent_id,
        time_range_ms=60000,  # Last minute
        limit=100
    )

    if not task_metrics:
        return 0.5  # Neutral score for new agents

    # Success rate (40%)
    success_count = sum(1 for m in task_metrics if m.get("result") == "success")
    success_rate = success_count / len(task_metrics)
    success_score = success_rate * 0.4

    # Response time (30%)
    durations = [m.get("duration_ms", 0) for m in task_metrics]
    avg_duration = statistics.mean(durations)
    target_duration = 3000  # 3 seconds
    time_score = max(0, 1 - (avg_duration / target_duration)) * 0.3

    # Current load (20%)
    current_tasks = get_agent_current_tasks(agent_id)
    max_concurrent = 3
    load_ratio = len(current_tasks) / max_concurrent
    load_score = max(0, 1 - load_ratio) * 0.2

    # Heartbeat regularity (10%)
    heartbeat_score = 0.1  # Simplified

    total_score = success_score + time_score + load_score + heartbeat_score

    return min(total_score, 1.0)
```

**Weighted Task Assignment**:
```python
def assign_task_to_agent(task, available_agents, metrics_storage):
    """
    Assign task to best available agent using weighted selection.

    Higher health score = higher selection probability
    """
    # Calculate health scores
    agent_scores = {
        agent_id: calculate_agent_health_score(agent_id, metrics_storage)
        for agent_id in available_agents
    }

    # Weight by health score
    total_weight = sum(agent_scores.values())

    if total_weight == 0:
        # All agents unhealthy, use random selection
        return random.choice(available_agents)

    # Weighted random selection
    rand = random.uniform(0, total_weight)
    cumulative = 0

    for agent_id, score in agent_scores.items():
        cumulative += score
        if rand <= cumulative:
            return agent_id

    # Fallback
    return max(agent_scores, key=agent_scores.get)
```

## Capacity Planning

### Predictive Scaling

**Purpose**: Proactively provision resources based on predicted demand.

**Demand Prediction**:
```python
def predict_future_demand(pattern_learner, time_window_ms=300000):
    """
    Predict future task submission rate.

    Uses pattern learning to forecast demand.
    """
    patterns = pattern_learner.get_all_patterns()

    # Find temporal patterns (time-based)
    temporal_patterns = [
        p for p in patterns
        if p.pattern_type == "temporal"
    ]

    if not temporal_patterns:
        return None

    # Analyze submission rate patterns
    for pattern in temporal_patterns:
        if "submission_rate" in pattern.metadata:
            current_rate = pattern.metadata.get("current_rate_per_minute", 0)
            trend = pattern.metadata.get("trend", "stable")

            # Predict future rate
            if trend == "increasing":
                predicted_rate = current_rate * 1.2  # 20% increase
            elif trend == "decreasing":
                predicted_rate = current_rate * 0.8  # 20% decrease
            else:
                predicted_rate = current_rate

            return {
                "current_rate_per_minute": current_rate,
                "predicted_rate_per_minute": predicted_rate,
                "trend": trend,
                "confidence": pattern.confidence
            }
```

**Proactive Provisioning**:
```python
def proactive_capacity_planning(
    predictor,
    coordinator,
    target_agent_utilization=0.7
):
    """
    Provision agents based on predicted demand.

    Target: 70% agent utilization (30% headroom)
    """
    demand = predict_future_demand(predictor.pattern_learner)

    if not demand or demand["confidence"] < 0.7:
        return  # Insufficient confidence

    predicted_rate = demand["predicted_rate_per_minute"]

    # Calculate required agents
    avg_task_duration_s = 3.0  # Average 3 seconds per task
    tasks_per_agent_per_minute = 60.0 / avg_task_duration_s  # 20 tasks/agent/min

    required_agents = math.ceil(
        predicted_rate / tasks_per_agent_per_minute / target_agent_utilization
    )

    # Get current agent count
    topology = coordinator.get_topology_info()
    current_agents = topology.get("agent_count", 0)

    # Provision if needed
    if required_agents > current_agents:
        agents_to_add = required_agents - current_agents
        logger.info(
            f"Proactive scaling: Adding {agents_to_add} agents "
            f"for predicted rate {predicted_rate:.1f} tasks/min"
        )

        for i in range(agents_to_add):
            agent_id = f"proactive-agent-{int(time.time())}-{i}"
            coordinator.register_agent(agent_id, {
                "type": "proactive",
                "predicted_rate": predicted_rate
            })
```

## Usage Examples

### Complete Resource Optimization

```python
from moai_flow.optimization import BottleneckDetector, PatternLearner

# Initialize components
detector = BottleneckDetector(metrics_storage, resource_controller)
learner = PatternLearner()

# Continuous optimization loop
while True:
    # 1. Dynamic agent scaling
    adaptive_agent_scaling(
        detector,
        coordinator,
        target_queue_depth=30
    )

    # 2. Token-aware prioritization
    optimize_token_allocation(
        detector,
        task_queue,
        token_budget
    )

    # 3. Load balancing
    for task in new_tasks:
        available_agents = get_available_agents(coordinator)
        selected_agent = assign_task_to_agent(
            task,
            available_agents,
            metrics_storage
        )
        assign_task(task, selected_agent)

    # 4. Capacity planning
    proactive_capacity_planning(
        predictor,
        coordinator,
        target_agent_utilization=0.7
    )

    time.sleep(30)  # Every 30 seconds
```

## Best Practices

1. **Set appropriate thresholds**: Balance responsiveness vs. stability
2. **Monitor utilization**: Track agent utilization (target: 70-80%)
3. **Use predictive scaling**: Provision ahead of demand spikes
4. **Optimize token usage**: Prioritize high-value, low-cost tasks
5. **Load balance**: Distribute work to healthiest agents
6. **Regular review**: Adjust policies based on observed patterns

## Performance Characteristics

**Scaling Decision**: <50ms
**Task Prioritization**: <10ms for 1000 tasks
**Load Balancing**: <5ms per assignment
**Memory**: O(n) where n = number of agents

## Related Documentation

- [Bottleneck Detection](bottleneck-detection.md) - Identify scaling triggers
- [Predictive Healing](predictive-healing.md) - Predict capacity needs
- [Performance Monitoring](performance-monitoring.md) - Track utilization metrics
