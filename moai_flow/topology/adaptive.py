#!/usr/bin/env python3
"""
Adaptive Topology for MoAI-Flow

Dynamic topology switching based on workload and performance metrics.
Starts as one pattern, morphs to another based on real-time analysis.

Supported Topologies:
    - HIERARCHICAL: Tree structure (scalable, >10 agents)
    - MESH: Full connectivity (collaborative, <5 agents)
    - STAR: Hub-and-spoke (centralized, 5-10 agents)
    - RING: Sequential chain (pipeline tasks)

Decision Criteria:
    - Agent count < 5: Mesh (full connectivity for collaboration)
    - Agent count 5-10: Star (centralized coordination)
    - Agent count > 10: Hierarchical (scalable tree structure)
    - Sequential task pattern: Ring (pipeline optimization)
    - High collaboration need: Mesh (regardless of count)

Example:
    >>> topology = AdaptiveTopology(initial_mode=TopologyMode.MESH)
    >>> topology.add_agent("agent-1", "expert-backend")
    >>> topology.add_agent("agent-2", "expert-frontend")
    >>> # Automatically switches to Star when 6th agent added
    >>> topology.add_agent("agent-6", "expert-database")
    >>> print(topology.current_mode)  # TopologyMode.STAR
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union
import logging
import time

from .hierarchical import HierarchicalTopology, Agent

logger = logging.getLogger(__name__)


class TopologyMode(Enum):
    """Supported topology patterns."""
    HIERARCHICAL = "hierarchical"
    MESH = "mesh"
    STAR = "star"
    RING = "ring"


@dataclass
class PerformanceMetrics:
    """Performance metrics for topology optimization."""
    timestamp: float
    agent_count: int
    avg_latency_ms: float
    throughput_tasks_per_sec: float
    utilization_percent: float
    communication_overhead: float
    task_completion_rate: float
    failure_rate: float

    def score(self) -> float:
        """
        Calculate overall performance score (0-100).

        Higher is better. Weighted combination of metrics.
        """
        # Normalize and weight metrics
        latency_score = max(0, 100 - (self.avg_latency_ms / 10))  # Lower latency = higher score
        throughput_score = min(100, self.throughput_tasks_per_sec * 10)  # Higher throughput = higher score
        utilization_score = self.utilization_percent  # Already 0-100
        overhead_score = max(0, 100 - self.communication_overhead)  # Lower overhead = higher score
        completion_score = self.task_completion_rate  # Already 0-100
        failure_score = max(0, 100 - self.failure_rate)  # Lower failure = higher score

        # Weighted average
        total_score = (
            latency_score * 0.20 +
            throughput_score * 0.25 +
            utilization_score * 0.15 +
            overhead_score * 0.15 +
            completion_score * 0.20 +
            failure_score * 0.05
        )

        return round(total_score, 2)


@dataclass
class TopologyStats:
    """Statistics for a specific topology configuration."""
    mode: TopologyMode
    agent_count: int
    total_tasks: int
    completed_tasks: int
    failed_tasks: int
    avg_task_duration_ms: float
    total_duration_seconds: float
    performance_scores: List[float] = field(default_factory=list)

    def avg_performance_score(self) -> float:
        """Calculate average performance score."""
        if not self.performance_scores:
            return 0.0
        return sum(self.performance_scores) / len(self.performance_scores)


class MeshTopologyStub:
    """
    Stub implementation of Mesh Topology.
    Full implementation in mesh.py (Phase 5, Task 1).
    """

    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        logger.info("MeshTopology stub initialized")

    def add_agent(self, agent_id: str, agent_type: str, **kwargs) -> bool:
        """Add agent with full connectivity to all others."""
        if agent_id in self.agents:
            return False

        agent = Agent(
            agent_id=agent_id,
            agent_type=agent_type,
            layer=0,  # Mesh has no layers
            metadata=kwargs.get("metadata", {})
        )
        self.agents[agent_id] = agent
        logger.info(f"Added agent {agent_id} to mesh topology")
        return True

    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """Get agent by ID."""
        return self.agents.get(agent_id)

    def visualize(self) -> str:
        """Visualize mesh topology."""
        if not self.agents:
            return "Mesh Topology (empty)"

        agent_list = list(self.agents.keys())
        lines = ["Mesh Topology (Full Connectivity)"]
        for agent_id in agent_list:
            connections = [a for a in agent_list if a != agent_id]
            lines.append(f"  {agent_id} <-> {', '.join(connections[:3])}{'...' if len(connections) > 3 else ''}")
        return "\n".join(lines)


class StarTopologyStub:
    """
    Stub implementation of Star Topology.
    Full implementation in star.py (Phase 5, Task 3).
    """

    def __init__(self, hub_agent_id: str = "alfred"):
        self.hub_id = hub_agent_id
        self.agents: Dict[str, Agent] = {}

        # Add hub agent
        hub = Agent(agent_id=hub_agent_id, agent_type="alfred", layer=0)
        self.agents[hub_agent_id] = hub
        logger.info(f"StarTopology stub initialized with hub: {hub_agent_id}")

    def add_agent(self, agent_id: str, agent_type: str, **kwargs) -> bool:
        """Add spoke agent connected to hub."""
        if agent_id in self.agents:
            return False

        agent = Agent(
            agent_id=agent_id,
            agent_type=agent_type,
            layer=1,  # All spokes at layer 1
            parent_id=self.hub_id,
            metadata=kwargs.get("metadata", {})
        )
        self.agents[agent_id] = agent

        # Add to hub's children
        hub = self.agents[self.hub_id]
        hub.children.add(agent_id)

        logger.info(f"Added agent {agent_id} to star topology")
        return True

    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """Get agent by ID."""
        return self.agents.get(agent_id)

    def visualize(self) -> str:
        """Visualize star topology."""
        hub = self.agents[self.hub_id]
        spokes = [aid for aid in self.agents.keys() if aid != self.hub_id]

        lines = [f"Star Topology (Hub: {self.hub_id})"]
        for spoke in spokes:
            lines.append(f"  {self.hub_id} <-> {spoke}")
        return "\n".join(lines)


class RingTopologyStub:
    """
    Stub implementation of Ring Topology.
    Full implementation in ring.py (Phase 5, Task 4).
    """

    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self.ring_order: List[str] = []  # Ordered list of agent IDs
        logger.info("RingTopology stub initialized")

    def add_agent(self, agent_id: str, agent_type: str, **kwargs) -> bool:
        """Add agent to ring (appends to end)."""
        if agent_id in self.agents:
            return False

        agent = Agent(
            agent_id=agent_id,
            agent_type=agent_type,
            layer=len(self.ring_order),  # Position in ring
            metadata=kwargs.get("metadata", {})
        )
        self.agents[agent_id] = agent
        self.ring_order.append(agent_id)

        logger.info(f"Added agent {agent_id} to ring topology at position {len(self.ring_order)-1}")
        return True

    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """Get agent by ID."""
        return self.agents.get(agent_id)

    def visualize(self) -> str:
        """Visualize ring topology."""
        if not self.ring_order:
            return "Ring Topology (empty)"

        lines = ["Ring Topology (Sequential)"]
        ring_str = " -> ".join(self.ring_order)
        if len(self.ring_order) > 1:
            ring_str += f" -> {self.ring_order[0]} (loop)"
        lines.append(f"  {ring_str}")
        return "\n".join(lines)


class AdaptiveTopology:
    """
    Adaptive topology that dynamically switches patterns based on workload.

    Automatically optimizes agent coordination by selecting the best topology
    mode based on agent count, task patterns, and performance metrics.

    Key Features:
        - Automatic mode selection based on agent count
        - Performance-driven optimization
        - Manual mode override support
        - Detailed metrics tracking
        - Visualization with mode indicator
    """

    def __init__(
        self,
        initial_mode: TopologyMode = TopologyMode.MESH,
        auto_adapt: bool = True,
        adaptation_threshold: float = 10.0  # Minimum performance improvement to switch (%)
    ):
        """
        Initialize adaptive topology.

        Args:
            initial_mode: Starting topology mode
            auto_adapt: Enable automatic topology switching
            adaptation_threshold: Minimum performance improvement % to trigger switch
        """
        self.current_mode = initial_mode
        self.auto_adapt = auto_adapt
        self.adaptation_threshold = adaptation_threshold

        # Current topology instance
        self.topology: Union[
            HierarchicalTopology,
            MeshTopologyStub,
            StarTopologyStub,
            RingTopologyStub
        ] = self._create_topology(initial_mode)

        # Metrics tracking
        self.metrics: List[PerformanceMetrics] = []
        self.mode_history: List[Tuple[float, TopologyMode]] = [
            (time.time(), initial_mode)
        ]

        # Statistics per mode
        self.mode_stats: Dict[TopologyMode, TopologyStats] = {}

        # Task tracking
        self.total_tasks = 0
        self.completed_tasks = 0
        self.failed_tasks = 0
        self.task_start_times: Dict[str, float] = {}

        logger.info(
            f"AdaptiveTopology initialized with mode={initial_mode.value}, "
            f"auto_adapt={auto_adapt}"
        )

    def _create_topology(
        self,
        mode: TopologyMode
    ) -> Union[HierarchicalTopology, MeshTopologyStub, StarTopologyStub, RingTopologyStub]:
        """
        Create topology instance for specified mode.

        Args:
            mode: Topology mode to create

        Returns:
            Topology instance
        """
        if mode == TopologyMode.HIERARCHICAL:
            return HierarchicalTopology(root_agent_id="alfred")
        elif mode == TopologyMode.MESH:
            return MeshTopologyStub()
        elif mode == TopologyMode.STAR:
            return StarTopologyStub(hub_agent_id="alfred")
        elif mode == TopologyMode.RING:
            return RingTopologyStub()
        else:
            raise ValueError(f"Unsupported topology mode: {mode}")

    def add_agent(
        self,
        agent_id: str,
        agent_type: str,
        **kwargs
    ) -> bool:
        """
        Add agent and trigger adaptation if needed.

        Args:
            agent_id: Unique agent identifier
            agent_type: Agent type (e.g., "expert-backend")
            **kwargs: Additional arguments passed to underlying topology

        Returns:
            True if agent added successfully, False otherwise
        """
        # Add agent to current topology
        success = False

        if self.current_mode == TopologyMode.HIERARCHICAL:
            # HierarchicalTopology requires layer parameter
            layer = kwargs.pop("layer", 1)  # Default to layer 1
            parent_id = kwargs.pop("parent_id", "alfred")
            success = self.topology.add_agent(
                agent_id=agent_id,
                agent_type=agent_type,
                layer=layer,
                parent_id=parent_id,
                metadata=kwargs.get("metadata")
            )
        else:
            # Other topologies have simpler add_agent
            success = self.topology.add_agent(agent_id, agent_type, **kwargs)

        if not success:
            return False

        # Check if we should adapt topology based on new agent count
        if self.auto_adapt:
            agent_count = len(self._get_all_agents())
            suggested_mode = self._suggest_mode_by_count(agent_count)

            if suggested_mode != self.current_mode:
                logger.info(
                    f"Agent count {agent_count} suggests topology switch: "
                    f"{self.current_mode.value} -> {suggested_mode.value}"
                )
                self.force_mode(suggested_mode)

        return True

    def _get_all_agents(self) -> Dict[str, Agent]:
        """Get all agents from current topology."""
        if hasattr(self.topology, 'agents'):
            return self.topology.agents
        return {}

    def _suggest_mode_by_count(self, agent_count: int) -> TopologyMode:
        """
        Suggest optimal topology mode based on agent count.

        Decision Rules:
            - < 5 agents: Mesh (full collaboration)
            - 5-10 agents: Star (centralized coordination)
            - > 10 agents: Hierarchical (scalable tree)

        Args:
            agent_count: Number of agents in topology

        Returns:
            Suggested TopologyMode
        """
        if agent_count < 5:
            return TopologyMode.MESH
        elif agent_count <= 10:
            return TopologyMode.STAR
        else:
            return TopologyMode.HIERARCHICAL

    def adapt_topology(self) -> bool:
        """
        Analyze current performance and switch topology if beneficial.

        Uses recent performance metrics to determine if a different topology
        would provide better performance.

        Returns:
            True if topology was changed, False if no change made
        """
        if not self.auto_adapt:
            logger.info("Auto-adaptation disabled, skipping topology analysis")
            return False

        # Need at least 3 metrics to analyze trend
        if len(self.metrics) < 3:
            logger.info("Insufficient metrics for adaptation analysis")
            return False

        # Get current performance baseline
        current_score = self._calculate_recent_performance()

        # Evaluate potential improvement for each mode
        best_mode = self.current_mode
        best_score = current_score

        for mode in TopologyMode:
            if mode == self.current_mode:
                continue

            # Estimate performance for this mode
            estimated_score = self._estimate_mode_performance(mode)

            # Check if improvement exceeds threshold
            improvement_pct = ((estimated_score - current_score) / current_score) * 100

            if improvement_pct > self.adaptation_threshold:
                if estimated_score > best_score:
                    best_mode = mode
                    best_score = estimated_score
                    logger.info(
                        f"Found better topology: {mode.value} "
                        f"(estimated improvement: {improvement_pct:.1f}%)"
                    )

        # Switch to best mode if different from current
        if best_mode != self.current_mode:
            logger.info(
                f"Adapting topology: {self.current_mode.value} -> {best_mode.value} "
                f"(performance improvement: {((best_score - current_score) / current_score) * 100:.1f}%)"
            )
            return self.force_mode(best_mode)

        logger.info("No beneficial topology switch found, maintaining current mode")
        return False

    def _calculate_recent_performance(self, window: int = 5) -> float:
        """
        Calculate average performance score from recent metrics.

        Args:
            window: Number of recent metrics to consider

        Returns:
            Average performance score (0-100)
        """
        if not self.metrics:
            return 50.0  # Neutral baseline

        recent_metrics = self.metrics[-window:]
        scores = [m.score() for m in recent_metrics]
        return sum(scores) / len(scores)

    def _estimate_mode_performance(self, mode: TopologyMode) -> float:
        """
        Estimate performance score for a given topology mode.

        Uses historical data if available, otherwise uses heuristics.

        Args:
            mode: Topology mode to estimate

        Returns:
            Estimated performance score (0-100)
        """
        # If we have historical data for this mode, use it
        if mode in self.mode_stats:
            stats = self.mode_stats[mode]
            if stats.performance_scores:
                return stats.avg_performance_score()

        # Otherwise use heuristics based on current context
        agent_count = len(self._get_all_agents())

        # Score each mode based on agent count and characteristics
        if mode == TopologyMode.MESH:
            # Mesh works best with small teams (< 5)
            if agent_count < 5:
                return 85.0
            elif agent_count < 10:
                return 60.0
            else:
                return 40.0  # Poor for large teams

        elif mode == TopologyMode.STAR:
            # Star works well for medium teams (5-10)
            if agent_count < 5:
                return 70.0
            elif agent_count <= 10:
                return 90.0
            else:
                return 65.0

        elif mode == TopologyMode.HIERARCHICAL:
            # Hierarchical scales well with large teams (> 10)
            if agent_count < 5:
                return 60.0
            elif agent_count <= 10:
                return 75.0
            else:
                return 95.0

        elif mode == TopologyMode.RING:
            # Ring works best for sequential/pipeline tasks
            # Heuristic: assume moderate performance
            return 70.0

        return 50.0  # Default neutral score

    def get_metrics(self) -> Dict[str, Any]:
        """
        Get current performance metrics.

        Returns:
            Dict with comprehensive performance metrics including:
                - current_mode: Active topology mode
                - agent_count: Number of agents
                - total_tasks: Total tasks tracked
                - completed_tasks: Successfully completed tasks
                - failed_tasks: Failed tasks
                - completion_rate: Task completion percentage
                - avg_performance_score: Average recent performance
                - recent_metrics: Last 5 performance measurements
                - mode_history: History of topology switches
        """
        agents = self._get_all_agents()
        recent_score = self._calculate_recent_performance()

        return {
            "current_mode": self.current_mode.value,
            "agent_count": len(agents),
            "total_tasks": self.total_tasks,
            "completed_tasks": self.completed_tasks,
            "failed_tasks": self.failed_tasks,
            "completion_rate": (
                (self.completed_tasks / self.total_tasks * 100)
                if self.total_tasks > 0 else 0.0
            ),
            "avg_performance_score": recent_score,
            "recent_metrics": [
                {
                    "timestamp": m.timestamp,
                    "score": m.score(),
                    "latency_ms": m.avg_latency_ms,
                    "throughput": m.throughput_tasks_per_sec
                }
                for m in self.metrics[-5:]
            ],
            "mode_history": [
                {"timestamp": ts, "mode": mode.value}
                for ts, mode in self.mode_history
            ]
        }

    def force_mode(self, mode: TopologyMode) -> bool:
        """
        Manually switch to specified topology mode.

        Migrates all agents from current topology to new topology.

        Args:
            mode: Target topology mode

        Returns:
            True if mode switched successfully, False otherwise
        """
        if mode == self.current_mode:
            logger.info(f"Already in {mode.value} mode, no change needed")
            return False

        old_mode = self.current_mode

        # Save current agents
        current_agents = self._get_all_agents()

        # Update mode stats before switching
        self._update_mode_stats()

        # Create new topology
        new_topology = self._create_topology(mode)

        # Migrate agents to new topology
        migration_success = self._migrate_agents(current_agents, new_topology, mode)

        if not migration_success:
            logger.error(f"Failed to migrate agents to {mode.value} topology")
            return False

        # Switch to new topology
        self.topology = new_topology
        self.current_mode = mode

        # Record mode change
        self.mode_history.append((time.time(), mode))

        logger.info(f"Topology switched: {old_mode.value} -> {mode.value}")
        return True

    def _migrate_agents(
        self,
        agents: Dict[str, Agent],
        new_topology: Any,
        target_mode: TopologyMode
    ) -> bool:
        """
        Migrate agents from old topology to new topology.

        Args:
            agents: Dictionary of agents to migrate
            new_topology: Target topology instance
            target_mode: Target topology mode

        Returns:
            True if all agents migrated successfully
        """
        # Skip alfred/root as it's already created
        agents_to_migrate = {
            aid: agent for aid, agent in agents.items()
            if aid not in ["alfred", new_topology.hub_id if hasattr(new_topology, 'hub_id') else None]
        }

        for agent_id, agent in agents_to_migrate.items():
            try:
                if target_mode == TopologyMode.HIERARCHICAL:
                    # Hierarchical needs layer info
                    new_topology.add_agent(
                        agent_id=agent_id,
                        agent_type=agent.agent_type,
                        layer=1,  # Default all to layer 1
                        parent_id="alfred",
                        metadata=agent.metadata
                    )
                else:
                    # Other modes have simpler interface
                    new_topology.add_agent(
                        agent_id=agent_id,
                        agent_type=agent.agent_type,
                        metadata=agent.metadata
                    )
            except Exception as e:
                logger.error(f"Failed to migrate agent {agent_id}: {e}")
                return False

        logger.info(f"Successfully migrated {len(agents_to_migrate)} agents to {target_mode.value}")
        return True

    def _update_mode_stats(self):
        """Update statistics for current mode before switching."""
        if self.current_mode not in self.mode_stats:
            self.mode_stats[self.current_mode] = TopologyStats(
                mode=self.current_mode,
                agent_count=len(self._get_all_agents()),
                total_tasks=self.total_tasks,
                completed_tasks=self.completed_tasks,
                failed_tasks=self.failed_tasks,
                avg_task_duration_ms=0.0,
                total_duration_seconds=0.0
            )

        stats = self.mode_stats[self.current_mode]

        # Update task counts
        stats.total_tasks = self.total_tasks
        stats.completed_tasks = self.completed_tasks
        stats.failed_tasks = self.failed_tasks

        # Add recent performance score
        if self.metrics:
            recent_score = self._calculate_recent_performance()
            stats.performance_scores.append(recent_score)

    def suggest_optimal_mode(self) -> TopologyMode:
        """
        AI-based suggestion for optimal topology mode.

        Analyzes current context (agent count, task patterns, performance)
        and suggests the best topology mode.

        Returns:
            Suggested TopologyMode
        """
        agent_count = len(self._get_all_agents())

        # Primary decision based on agent count
        suggested_mode = self._suggest_mode_by_count(agent_count)

        # Adjust based on task patterns if we have metrics
        if self.metrics:
            recent_metrics = self.metrics[-5:]

            # Check for high collaboration needs (low latency, high communication)
            avg_overhead = sum(m.communication_overhead for m in recent_metrics) / len(recent_metrics)

            if avg_overhead > 70 and agent_count < 10:
                # High communication overhead suggests mesh might be better
                suggested_mode = TopologyMode.MESH
                logger.info("High communication overhead detected, suggesting MESH topology")

            # Check for sequential task pattern
            # If tasks tend to complete in order, ring might be optimal
            # (This is a simplified heuristic)
            avg_completion_rate = sum(m.task_completion_rate for m in recent_metrics) / len(recent_metrics)

            if avg_completion_rate > 90 and agent_count <= 8:
                # High sequential completion suggests ring
                suggested_mode = TopologyMode.RING
                logger.info("Sequential task pattern detected, suggesting RING topology")

        logger.info(
            f"Suggested optimal mode for {agent_count} agents: {suggested_mode.value}"
        )
        return suggested_mode

    def record_performance(
        self,
        avg_latency_ms: float = 0.0,
        throughput_tasks_per_sec: float = 0.0,
        utilization_percent: float = 0.0,
        communication_overhead: float = 0.0,
        task_completion_rate: float = 0.0,
        failure_rate: float = 0.0
    ) -> None:
        """
        Record performance metrics for current topology.

        Args:
            avg_latency_ms: Average task latency in milliseconds
            throughput_tasks_per_sec: Tasks completed per second
            utilization_percent: Agent utilization percentage (0-100)
            communication_overhead: Communication overhead percentage (0-100)
            task_completion_rate: Task completion rate percentage (0-100)
            failure_rate: Task failure rate percentage (0-100)
        """
        metric = PerformanceMetrics(
            timestamp=time.time(),
            agent_count=len(self._get_all_agents()),
            avg_latency_ms=avg_latency_ms,
            throughput_tasks_per_sec=throughput_tasks_per_sec,
            utilization_percent=utilization_percent,
            communication_overhead=communication_overhead,
            task_completion_rate=task_completion_rate,
            failure_rate=failure_rate
        )

        self.metrics.append(metric)

        # Keep only last 100 metrics to prevent memory growth
        if len(self.metrics) > 100:
            self.metrics = self.metrics[-100:]

        logger.info(
            f"Recorded performance: score={metric.score():.1f}, "
            f"latency={avg_latency_ms:.1f}ms, throughput={throughput_tasks_per_sec:.2f} tasks/s"
        )

    def visualize(self) -> str:
        """
        Visualize current topology with mode indicator.

        Returns:
            String representation of topology with performance info
        """
        lines = [
            "=" * 60,
            f"Adaptive Topology - Current Mode: {self.current_mode.value.upper()}",
            "=" * 60,
            ""
        ]

        # Add performance summary
        metrics = self.get_metrics()
        lines.extend([
            "Performance Summary:",
            f"  Agents: {metrics['agent_count']}",
            f"  Tasks: {metrics['completed_tasks']}/{metrics['total_tasks']} "
            f"({metrics['completion_rate']:.1f}% completion)",
            f"  Avg Performance Score: {metrics['avg_performance_score']:.1f}/100",
            ""
        ])

        # Add mode history
        if len(self.mode_history) > 1:
            lines.append("Mode History:")
            for ts, mode in self.mode_history[-5:]:  # Last 5 changes
                dt = datetime.fromtimestamp(ts)
                lines.append(f"  {dt.strftime('%Y-%m-%d %H:%M:%S')} - {mode.value}")
            lines.append("")

        # Add current topology visualization
        lines.extend([
            "Current Topology Structure:",
            "-" * 60
        ])

        topology_viz = self.topology.visualize()
        lines.append(topology_viz)

        lines.append("=" * 60)

        return "\n".join(lines)


__all__ = ["AdaptiveTopology", "TopologyMode", "PerformanceMetrics", "TopologyStats"]
