# Task Delegation Module

Work distribution and load balancing patterns for multi-agent swarms with intelligent task allocation strategies.

## Table of Contents

1. [Task Delegation Overview](#task-delegation-overview)
2. [Allocation Strategies](#allocation-strategies)
3. [Load Balancing](#load-balancing)
4. [Priority Queues](#priority-queues)
5. [Work Stealing](#work-stealing)
6. [Agent Selection](#agent-selection)

---

## Task Delegation Overview

**Note**: Full TaskAllocator implementation is planned for Phase 6C-6D. This module describes delegation patterns using existing coordination components.

### Current Capabilities (Phase 6B)

Using existing coordination components:

```python
# Consensus-based delegation
manager = ConsensusManager(coordinator)
result = manager.request_consensus({"action": "delegate", "task_id": "task-001"})

# State-based work distribution
synchronizer = StateSynchronizer(coordinator, memory, resolver)
synchronizer.synchronize_state("swarm-001", "task_queue")
```

### Future Capabilities (Phase 6C-6D)

```python
# Planned TaskAllocator
allocator = TaskAllocator(
    coordinator=coordinator,
    strategy="load_balanced"
)

assignment = allocator.assign_task(
    task={"id": "task-001", "type": "compute"},
    agents=available_agents
)
```

---

## Allocation Strategies

### Round-Robin (Phase 6C)

```python
class RoundRobinAllocator:
    """Distribute tasks evenly across agents."""

    def __init__(self):
        self.current_index = 0

    def assign(self, task, agents):
        agent = agents[self.current_index % len(agents)]
        self.current_index += 1
        return agent
```

### Load-Based (Phase 6C)

```python
class LoadBasedAllocator:
    """Assign to least loaded agent."""

    def assign(self, task, agents):
        agent_loads = [self.get_agent_load(a) for a in agents]
        min_load_index = agent_loads.index(min(agent_loads))
        return agents[min_load_index]

    def get_agent_load(self, agent):
        # Query agent's current task count or CPU usage
        return agent.get_current_load()
```

### Capability-Based (Phase 6D)

```python
class CapabilityAllocator:
    """Match task requirements to agent capabilities."""

    def assign(self, task, agents):
        required_capabilities = task.get("capabilities", [])

        # Filter agents by capabilities
        capable_agents = [
            a for a in agents
            if all(cap in a.capabilities for cap in required_capabilities)
        ]

        if not capable_agents:
            raise ValueError("No capable agents available")

        # Select least loaded capable agent
        return min(capable_agents, key=lambda a: a.get_current_load())
```

---

## Load Balancing

### Current Pattern (Phase 6B)

```python
def distribute_tasks_consensus(tasks, coordinator):
    """Distribute tasks using consensus voting."""
    manager = ConsensusManager(coordinator, algorithm="weighted")

    # Set agent weights based on current load (inverse)
    agent_weights = {}
    for agent_id in coordinator.get_all_agents():
        load = get_agent_load(agent_id)
        agent_weights[agent_id] = 1.0 / (load + 0.1)  # Avoid division by zero

    # Register weighted algorithm
    weighted = WeightedAlgorithm(threshold=0.5, agent_weights=agent_weights)
    manager.register_algorithm("load_balanced", weighted)

    # Assign tasks via consensus
    for task in tasks:
        proposal = {
            "proposal_id": f"task_{task['id']}",
            "task": task
        }
        result = manager.request_consensus(proposal, algorithm="load_balanced")

        if result.decision == "approved":
            # Task assigned to agent with highest weight (lowest load)
            pass
```

### Future Pattern (Phase 6C)

```python
class LoadBalancer:
    def distribute_tasks(self, tasks, agents):
        """Evenly distribute tasks across agents."""
        agent_queues = {agent.id: [] for agent in agents}

        # Sort tasks by priority
        sorted_tasks = sorted(tasks, key=lambda t: t.get("priority", 0), reverse=True)

        # Assign to least loaded agent
        for task in sorted_tasks:
            least_loaded_agent = min(
                agent_queues.items(),
                key=lambda item: len(item[1])
            )[0]

            agent_queues[least_loaded_agent].append(task)

        return agent_queues
```

---

## Priority Queues

### Current Implementation

```python
from moai_flow.coordination import StateSynchronizer, ConflictResolver

# Priority queue as synchronized state
def add_task_to_queue(synchronizer, swarm_id, task):
    """Add task to priority queue using state sync."""

    # Get current queue
    queue_state = synchronizer.get_state(swarm_id, "priority_queue")

    if queue_state:
        queue = queue_state.value
    else:
        queue = []

    # Add task with priority
    queue.append({
        "id": task["id"],
        "priority": task.get("priority", 0),
        "data": task
    })

    # Sort by priority (highest first)
    queue.sort(key=lambda t: t["priority"], reverse=True)

    # Synchronize updated queue
    resolver = ConflictResolver(strategy="crdt")
    synchronizer.conflict_resolver = resolver
    synchronizer.synchronize_state(swarm_id, "priority_queue")

# Agent pulls from queue
def get_next_task(synchronizer, swarm_id):
    """Get highest priority task."""
    queue_state = synchronizer.get_state(swarm_id, "priority_queue")

    if not queue_state or not queue_state.value:
        return None

    # Get highest priority task
    task = queue_state.value[0]
    return task
```

---

## Work Stealing

### Concept

Idle agents steal work from busy agents:

```
Agent-1 (busy): [task1, task2, task3, task4, task5]
Agent-2 (idle):  []

Work stealing:
Agent-2 steals task5 from Agent-1

Result:
Agent-1: [task1, task2, task3, task4]
Agent-2: [task5]
```

### Current Pattern

```python
def work_stealing_via_state_sync(synchronizer, swarm_id, idle_agent_id):
    """Idle agent steals work from busy agents."""

    # Get all agent task queues
    all_agents = synchronizer.memory.list_keys(swarm_id, "agent_queues")

    # Find busiest agent
    busiest_agent = None
    max_queue_size = 0

    for agent_id in all_agents:
        queue_state = synchronizer.get_state(swarm_id, f"queue_{agent_id}")
        if queue_state:
            queue_size = len(queue_state.value)
            if queue_size > max_queue_size:
                max_queue_size = queue_size
                busiest_agent = agent_id

    # Steal task if busiest agent has > 1 task
    if busiest_agent and max_queue_size > 1:
        busy_queue = synchronizer.get_state(swarm_id, f"queue_{busiest_agent}")
        stolen_task = busy_queue.value.pop()  # Take from end

        # Add to idle agent's queue
        idle_queue = synchronizer.get_state(swarm_id, f"queue_{idle_agent_id}")
        if idle_queue:
            idle_queue.value.append(stolen_task)
        else:
            idle_queue = [stolen_task]

        # Synchronize both queues
        synchronizer.synchronize_state(swarm_id, f"queue_{busiest_agent}")
        synchronizer.synchronize_state(swarm_id, f"queue_{idle_agent_id}")

        return stolen_task

    return None  # No work to steal
```

---

## Agent Selection

### Consensus-Based Selection

```python
def select_agent_consensus(coordinator, task, available_agents):
    """Use consensus to select best agent for task."""

    manager = ConsensusManager(coordinator, algorithm="weighted")

    # Set weights based on agent suitability
    agent_weights = {}
    for agent_id in available_agents:
        agent = coordinator.get_agent(agent_id)

        # Calculate suitability score
        capability_match = calculate_capability_match(agent, task)
        load_factor = 1.0 / (agent.get_current_load() + 0.1)
        location_factor = calculate_location_proximity(agent, task)

        suitability = capability_match * load_factor * location_factor
        agent_weights[agent_id] = suitability

    # Weighted consensus
    weighted = WeightedAlgorithm(threshold=0.5, agent_weights=agent_weights)
    manager.register_algorithm("agent_selection", weighted)

    proposal = {
        "proposal_id": f"select_agent_{task['id']}",
        "task": task,
        "candidates": available_agents
    }

    result = manager.request_consensus(proposal, algorithm="agent_selection")

    # Return agent with highest weight
    if result.decision == "approved":
        selected_agent = max(agent_weights, key=agent_weights.get)
        return selected_agent

    return None
```

### State-Based Selection

```python
def select_agent_state_based(synchronizer, swarm_id, task):
    """Select agent based on synchronized state."""

    # Get agent registry
    registry_state = synchronizer.get_state(swarm_id, "agent_registry")

    if not registry_state:
        return None

    agents = registry_state.value

    # Filter by capabilities
    capable_agents = [
        a for a in agents
        if all(cap in a.get("capabilities", []) for cap in task.get("required_capabilities", []))
    ]

    if not capable_agents:
        return None

    # Select least loaded
    agent_loads = []
    for agent in capable_agents:
        load_state = synchronizer.get_state(swarm_id, f"load_{agent['id']}")
        load = load_state.value if load_state else 0
        agent_loads.append((agent, load))

    # Return agent with minimum load
    selected_agent = min(agent_loads, key=lambda x: x[1])[0]
    return selected_agent
```

---

## Future Enhancements (Phase 6C-6D)

### TaskAllocator Class

```python
class TaskAllocator:
    """
    Intelligent task allocation for swarms.

    Strategies:
    - round_robin: Even distribution
    - load_balanced: Based on agent load
    - capability_based: Match task to agent capabilities
    - priority_based: High-priority tasks first
    - locality_aware: Minimize data transfer
    """

    def __init__(self, coordinator, strategy="load_balanced"):
        self.coordinator = coordinator
        self.strategy = strategy
        self.allocation_history = []

    def assign_task(self, task, agents):
        """Assign task to best agent."""
        if self.strategy == "round_robin":
            return self._round_robin(task, agents)
        elif self.strategy == "load_balanced":
            return self._load_balanced(task, agents)
        elif self.strategy == "capability_based":
            return self._capability_based(task, agents)

    def get_allocation_stats(self):
        """Get allocation statistics."""
        return {
            "total_allocations": len(self.allocation_history),
            "by_agent": self._count_by_agent(),
            "avg_load_balance": self._calculate_load_balance()
        }
```

### HeartbeatMonitor Integration

```python
class HeartbeatMonitor:
    """Monitor agent health for allocation decisions."""

    def get_healthy_agents(self):
        """Return list of healthy agents."""
        healthy = []
        for agent_id, heartbeat in self.heartbeats.items():
            if self.is_healthy(heartbeat):
                healthy.append(agent_id)
        return healthy

# Integration with TaskAllocator
allocator = TaskAllocator(coordinator)
healthy_agents = heartbeat_monitor.get_healthy_agents()
assignment = allocator.assign_task(task, agents=healthy_agents)
```

---

**Next**: [Examples](../examples/basic-coordination.md)
