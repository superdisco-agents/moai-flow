"""
Swarm Coordination Patterns for MoAI-Flow
==========================================

PRD-02 Phase 7 Track 1 Week 1-2: Reusable Swarm Patterns

Implements 4 common swarm coordination patterns:
1. Master-Worker: 1 master coordinates N workers
2. Pipeline: Sequential agent chain (A → B → C)
3. Broadcast: 1 input → N agents (parallel execution)
4. Reduce: N agents → 1 result (aggregation)

Each pattern includes:
- Pattern class implementation
- Configuration interface
- Usage examples
- Integration with SwarmCoordinator
"""

from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import logging
import time

from ..core.swarm_coordinator import SwarmCoordinator, AgentState

logger = logging.getLogger(__name__)


# ============================================================================
# Base Pattern Interface
# ============================================================================

class PatternType(Enum):
    """Swarm coordination pattern types."""
    MASTER_WORKER = "master_worker"
    PIPELINE = "pipeline"
    BROADCAST = "broadcast"
    REDUCE = "reduce"


@dataclass
class PatternConfig:
    """Base configuration for swarm patterns."""
    pattern_type: PatternType
    coordinator: SwarmCoordinator
    timeout_ms: int = 30000
    retry_on_failure: bool = True
    max_retries: int = 3


@dataclass
class PatternResult:
    """Result from pattern execution."""
    success: bool
    results: Dict[str, Any]
    duration_ms: float
    failed_agents: List[str]
    metadata: Dict[str, Any]


# ============================================================================
# Pattern 1: Master-Worker
# ============================================================================

class MasterWorkerPattern:
    """
    Master-Worker coordination pattern.

    Architecture:
        Master (1) → Workers (N)

    Use Cases:
        - Task distribution with work queue
        - Load balancing across workers
        - Result aggregation from parallel workers

    Example:
        >>> pattern = MasterWorkerPattern(
        ...     coordinator=coordinator,
        ...     master_id="master-001",
        ...     worker_ids=["worker-001", "worker-002", "worker-003"]
        ... )
        >>> result = pattern.execute(
        ...     work_items=[{"task": "process", "data": i} for i in range(10)]
        ... )
    """

    def __init__(
        self,
        coordinator: SwarmCoordinator,
        master_id: str,
        worker_ids: List[str],
        distribution_strategy: str = "round_robin",
        timeout_ms: int = 30000
    ):
        """
        Initialize Master-Worker pattern.

        Args:
            coordinator: SwarmCoordinator instance
            master_id: Master agent identifier
            worker_ids: List of worker agent identifiers
            distribution_strategy: Work distribution strategy
                - "round_robin": Distribute sequentially
                - "least_busy": Assign to least busy worker
                - "random": Random assignment
            timeout_ms: Timeout for work completion
        """
        self.coordinator = coordinator
        self.master_id = master_id
        self.worker_ids = worker_ids
        self.distribution_strategy = distribution_strategy
        self.timeout_ms = timeout_ms

        # Work tracking
        self.work_queue: List[Dict[str, Any]] = []
        self.work_assignments: Dict[str, List[str]] = {wid: [] for wid in worker_ids}
        self.results: Dict[str, Any] = {}

    def execute(
        self,
        work_items: List[Dict[str, Any]],
        aggregation_fn: Optional[Callable] = None
    ) -> PatternResult:
        """
        Execute Master-Worker pattern.

        Args:
            work_items: List of work items to distribute
            aggregation_fn: Optional function to aggregate worker results

        Returns:
            PatternResult with aggregated results
        """
        start_time = time.time()
        logger.info(
            f"Master-Worker: Starting with master={self.master_id}, "
            f"workers={len(self.worker_ids)}, work_items={len(work_items)}"
        )

        # Distribute work
        self.work_queue = work_items.copy()
        self._distribute_work()

        # Simulate work execution (in real implementation, agents would process)
        # For now, we'll track the distribution
        worker_results = {}
        failed_agents = []

        for worker_id in self.worker_ids:
            assigned_work = self.work_assignments[worker_id]
            if assigned_work:
                # Send work to worker
                work_message = {
                    "pattern": "master_worker",
                    "work_items": assigned_work,
                    "master_id": self.master_id
                }
                success = self.coordinator.send_message(
                    self.master_id,
                    worker_id,
                    work_message
                )

                if success:
                    worker_results[worker_id] = {
                        "status": "completed",
                        "work_count": len(assigned_work),
                        "results": assigned_work  # Simplified
                    }
                else:
                    failed_agents.append(worker_id)

        # Aggregate results
        if aggregation_fn:
            aggregated_results = aggregation_fn(worker_results)
        else:
            aggregated_results = worker_results

        duration_ms = (time.time() - start_time) * 1000

        logger.info(
            f"Master-Worker: Completed in {duration_ms:.2f}ms, "
            f"workers={len(worker_results)}, failed={len(failed_agents)}"
        )

        return PatternResult(
            success=(len(failed_agents) == 0),
            results=aggregated_results,
            duration_ms=duration_ms,
            failed_agents=failed_agents,
            metadata={
                "pattern": "master_worker",
                "master_id": self.master_id,
                "worker_count": len(self.worker_ids),
                "work_items": len(work_items),
                "distribution_strategy": self.distribution_strategy
            }
        )

    def _distribute_work(self):
        """Distribute work items to workers based on strategy."""
        if self.distribution_strategy == "round_robin":
            for i, work_item in enumerate(self.work_queue):
                worker_idx = i % len(self.worker_ids)
                worker_id = self.worker_ids[worker_idx]
                self.work_assignments[worker_id].append(work_item)

        elif self.distribution_strategy == "least_busy":
            for work_item in self.work_queue:
                # Find worker with least assignments
                least_busy = min(
                    self.worker_ids,
                    key=lambda wid: len(self.work_assignments[wid])
                )
                self.work_assignments[least_busy].append(work_item)

        elif self.distribution_strategy == "random":
            import random
            for work_item in self.work_queue:
                worker_id = random.choice(self.worker_ids)
                self.work_assignments[worker_id].append(work_item)

        else:
            raise ValueError(f"Unknown distribution strategy: {self.distribution_strategy}")


# ============================================================================
# Pattern 2: Pipeline
# ============================================================================

class PipelinePattern:
    """
    Pipeline coordination pattern.

    Architecture:
        Agent A → Agent B → Agent C → ... → Final Output

    Use Cases:
        - Sequential data transformation
        - Multi-stage processing workflows
        - Data enrichment pipelines

    Example:
        >>> pattern = PipelinePattern(
        ...     coordinator=coordinator,
        ...     stages=[
        ...         {"agent_id": "parser", "transform": parse_data},
        ...         {"agent_id": "validator", "transform": validate_data},
        ...         {"agent_id": "enricher", "transform": enrich_data}
        ...     ]
        ... )
        >>> result = pattern.execute(input_data={"raw": "data"})
    """

    def __init__(
        self,
        coordinator: SwarmCoordinator,
        stages: List[Dict[str, Any]],
        error_handling: str = "stop_on_error",
        timeout_ms: int = 30000
    ):
        """
        Initialize Pipeline pattern.

        Args:
            coordinator: SwarmCoordinator instance
            stages: List of pipeline stages
                Each stage: {"agent_id": str, "transform": callable (optional)}
            error_handling: Error handling strategy
                - "stop_on_error": Stop pipeline on first error
                - "skip_stage": Skip failed stage and continue
                - "retry": Retry failed stage
            timeout_ms: Timeout per stage
        """
        self.coordinator = coordinator
        self.stages = stages
        self.error_handling = error_handling
        self.timeout_ms = timeout_ms

        # Execution tracking
        self.stage_results: List[Dict[str, Any]] = []

    def execute(
        self,
        input_data: Any,
        context: Optional[Dict[str, Any]] = None
    ) -> PatternResult:
        """
        Execute Pipeline pattern.

        Args:
            input_data: Initial input data
            context: Optional context shared across stages

        Returns:
            PatternResult with final output
        """
        start_time = time.time()
        logger.info(f"Pipeline: Starting with {len(self.stages)} stages")

        current_data = input_data
        failed_agents = []
        execution_context = context or {}

        for stage_idx, stage in enumerate(self.stages):
            agent_id = stage["agent_id"]
            transform_fn = stage.get("transform")

            logger.info(f"Pipeline: Stage {stage_idx + 1}/{len(self.stages)} - {agent_id}")

            try:
                # Send data to stage agent
                stage_message = {
                    "pattern": "pipeline",
                    "stage_index": stage_idx,
                    "input_data": current_data,
                    "context": execution_context
                }

                # In real implementation, agent would process
                # For now, apply transform function if provided
                if transform_fn and callable(transform_fn):
                    stage_output = transform_fn(current_data, execution_context)
                else:
                    # Simplified: pass through with metadata
                    stage_output = {
                        "data": current_data,
                        "processed_by": agent_id,
                        "stage": stage_idx
                    }

                # Record stage result
                self.stage_results.append({
                    "stage_index": stage_idx,
                    "agent_id": agent_id,
                    "success": True,
                    "output": stage_output
                })

                # Update current data for next stage
                current_data = stage_output

            except Exception as e:
                logger.error(f"Pipeline: Stage {stage_idx} ({agent_id}) failed: {e}")
                failed_agents.append(agent_id)

                self.stage_results.append({
                    "stage_index": stage_idx,
                    "agent_id": agent_id,
                    "success": False,
                    "error": str(e)
                })

                if self.error_handling == "stop_on_error":
                    break
                elif self.error_handling == "skip_stage":
                    continue
                elif self.error_handling == "retry":
                    # Simplified retry logic
                    logger.info(f"Pipeline: Retrying stage {stage_idx}")
                    # In real implementation, would retry

        duration_ms = (time.time() - start_time) * 1000

        logger.info(
            f"Pipeline: Completed in {duration_ms:.2f}ms, "
            f"stages_executed={len(self.stage_results)}, failed={len(failed_agents)}"
        )

        return PatternResult(
            success=(len(failed_agents) == 0),
            results={
                "final_output": current_data,
                "stage_results": self.stage_results
            },
            duration_ms=duration_ms,
            failed_agents=failed_agents,
            metadata={
                "pattern": "pipeline",
                "total_stages": len(self.stages),
                "completed_stages": len(self.stage_results),
                "error_handling": self.error_handling
            }
        )


# ============================================================================
# Pattern 3: Broadcast
# ============================================================================

class BroadcastPattern:
    """
    Broadcast coordination pattern.

    Architecture:
        Input → Agent 1
              → Agent 2
              → Agent 3
              → ... → Agent N

    Use Cases:
        - Parallel processing of same input
        - Redundant computation for reliability
        - Consensus-based decisions

    Example:
        >>> pattern = BroadcastPattern(
        ...     coordinator=coordinator,
        ...     agent_ids=["agent-001", "agent-002", "agent-003"],
        ...     consensus_threshold=0.66
        ... )
        >>> result = pattern.execute(
        ...     input_data={"query": "process this"},
        ...     consensus_required=True
        ... )
    """

    def __init__(
        self,
        coordinator: SwarmCoordinator,
        agent_ids: List[str],
        consensus_threshold: float = 0.51,
        wait_for_all: bool = False,
        timeout_ms: int = 30000
    ):
        """
        Initialize Broadcast pattern.

        Args:
            coordinator: SwarmCoordinator instance
            agent_ids: List of agent identifiers to broadcast to
            consensus_threshold: Minimum agreement ratio for consensus
            wait_for_all: Wait for all agents or just majority
            timeout_ms: Timeout for agent responses
        """
        self.coordinator = coordinator
        self.agent_ids = agent_ids
        self.consensus_threshold = consensus_threshold
        self.wait_for_all = wait_for_all
        self.timeout_ms = timeout_ms

    def execute(
        self,
        input_data: Any,
        consensus_required: bool = False,
        sender_id: str = "broadcast_controller"
    ) -> PatternResult:
        """
        Execute Broadcast pattern.

        Args:
            input_data: Data to broadcast to all agents
            consensus_required: Whether to require consensus on results
            sender_id: Identifier for broadcast sender

        Returns:
            PatternResult with all agent results or consensus result
        """
        start_time = time.time()
        logger.info(
            f"Broadcast: Starting with {len(self.agent_ids)} agents, "
            f"consensus_required={consensus_required}"
        )

        # Broadcast to all agents
        broadcast_message = {
            "pattern": "broadcast",
            "input_data": input_data,
            "sender_id": sender_id,
            "timestamp": time.time()
        }

        agent_results = {}
        failed_agents = []

        for agent_id in self.agent_ids:
            try:
                # In real implementation, agents would process and return results
                # For now, simulate by sending message
                success = self.coordinator.send_message(
                    sender_id,
                    agent_id,
                    broadcast_message
                )

                if success:
                    # Simulate agent processing result
                    agent_results[agent_id] = {
                        "status": "completed",
                        "result": f"processed_{agent_id}",
                        "input": input_data
                    }
                else:
                    failed_agents.append(agent_id)

            except Exception as e:
                logger.error(f"Broadcast: Agent {agent_id} failed: {e}")
                failed_agents.append(agent_id)

        # Handle consensus if required
        final_results = agent_results
        consensus_achieved = False

        if consensus_required:
            # Determine consensus based on threshold
            successful_count = len(agent_results)
            total_count = len(self.agent_ids)
            consensus_ratio = successful_count / total_count if total_count > 0 else 0

            consensus_achieved = consensus_ratio >= self.consensus_threshold

            final_results = {
                "consensus_achieved": consensus_achieved,
                "consensus_ratio": consensus_ratio,
                "agent_results": agent_results,
                "agreement_count": successful_count,
                "total_agents": total_count
            }

        duration_ms = (time.time() - start_time) * 1000

        logger.info(
            f"Broadcast: Completed in {duration_ms:.2f}ms, "
            f"successful={len(agent_results)}, failed={len(failed_agents)}, "
            f"consensus_achieved={consensus_achieved if consensus_required else 'N/A'}"
        )

        return PatternResult(
            success=(len(failed_agents) == 0 and (not consensus_required or consensus_achieved)),
            results=final_results,
            duration_ms=duration_ms,
            failed_agents=failed_agents,
            metadata={
                "pattern": "broadcast",
                "total_agents": len(self.agent_ids),
                "consensus_required": consensus_required,
                "consensus_achieved": consensus_achieved if consensus_required else None,
                "wait_for_all": self.wait_for_all
            }
        )


# ============================================================================
# Pattern 4: Reduce
# ============================================================================

class ReducePattern:
    """
    Reduce coordination pattern.

    Architecture:
        Agent 1 →
        Agent 2 → Aggregator → Final Result
        Agent 3 →
        ... →
        Agent N →

    Use Cases:
        - Result aggregation from multiple sources
        - Map-reduce style computations
        - Consensus-based decision making

    Example:
        >>> pattern = ReducePattern(
        ...     coordinator=coordinator,
        ...     agent_ids=["agent-001", "agent-002", "agent-003"],
        ...     reduce_fn=lambda results: sum([r["value"] for r in results])
        ... )
        >>> result = pattern.execute(
        ...     distribute_fn=lambda i, total: {"task": f"compute_{i}"}
        ... )
    """

    def __init__(
        self,
        coordinator: SwarmCoordinator,
        agent_ids: List[str],
        reduce_fn: Callable[[List[Any]], Any],
        timeout_ms: int = 30000,
        partial_results_ok: bool = False
    ):
        """
        Initialize Reduce pattern.

        Args:
            coordinator: SwarmCoordinator instance
            agent_ids: List of agent identifiers
            reduce_fn: Function to reduce agent results to single result
                Signature: (List[agent_result]) -> final_result
            timeout_ms: Timeout for agent execution
            partial_results_ok: Accept partial results if some agents fail
        """
        self.coordinator = coordinator
        self.agent_ids = agent_ids
        self.reduce_fn = reduce_fn
        self.timeout_ms = timeout_ms
        self.partial_results_ok = partial_results_ok

    def execute(
        self,
        distribute_fn: Optional[Callable[[int, int], Any]] = None,
        input_data: Optional[Any] = None
    ) -> PatternResult:
        """
        Execute Reduce pattern.

        Args:
            distribute_fn: Function to generate input for each agent
                Signature: (agent_index, total_agents) -> agent_input
            input_data: Alternative: same input data for all agents

        Returns:
            PatternResult with reduced final result
        """
        start_time = time.time()
        logger.info(f"Reduce: Starting with {len(self.agent_ids)} agents")

        agent_results = []
        failed_agents = []

        # Distribute work to agents
        for i, agent_id in enumerate(self.agent_ids):
            try:
                # Determine agent input
                if distribute_fn:
                    agent_input = distribute_fn(i, len(self.agent_ids))
                else:
                    agent_input = input_data

                # Send work to agent
                work_message = {
                    "pattern": "reduce",
                    "agent_index": i,
                    "input_data": agent_input
                }

                success = self.coordinator.send_message(
                    "reduce_controller",
                    agent_id,
                    work_message
                )

                if success:
                    # Simulate agent result
                    agent_result = {
                        "agent_id": agent_id,
                        "agent_index": i,
                        "result": f"result_{i}",  # Simplified
                        "input": agent_input
                    }
                    agent_results.append(agent_result)
                else:
                    failed_agents.append(agent_id)

            except Exception as e:
                logger.error(f"Reduce: Agent {agent_id} failed: {e}")
                failed_agents.append(agent_id)

        # Check if we have enough results
        if not self.partial_results_ok and failed_agents:
            logger.warning(
                f"Reduce: {len(failed_agents)} agents failed, "
                f"partial_results_ok=False"
            )
            duration_ms = (time.time() - start_time) * 1000
            return PatternResult(
                success=False,
                results={"error": "Not all agents completed"},
                duration_ms=duration_ms,
                failed_agents=failed_agents,
                metadata={
                    "pattern": "reduce",
                    "total_agents": len(self.agent_ids),
                    "failed_count": len(failed_agents)
                }
            )

        # Apply reduce function
        try:
            reduced_result = self.reduce_fn(agent_results)
        except Exception as e:
            logger.error(f"Reduce: Reduce function failed: {e}")
            duration_ms = (time.time() - start_time) * 1000
            return PatternResult(
                success=False,
                results={"error": f"Reduce function failed: {e}"},
                duration_ms=duration_ms,
                failed_agents=failed_agents,
                metadata={
                    "pattern": "reduce",
                    "reduce_error": str(e)
                }
            )

        duration_ms = (time.time() - start_time) * 1000

        logger.info(
            f"Reduce: Completed in {duration_ms:.2f}ms, "
            f"successful={len(agent_results)}, failed={len(failed_agents)}"
        )

        return PatternResult(
            success=True,
            results={
                "reduced_result": reduced_result,
                "agent_results": agent_results,
                "successful_count": len(agent_results),
                "failed_count": len(failed_agents)
            },
            duration_ms=duration_ms,
            failed_agents=failed_agents,
            metadata={
                "pattern": "reduce",
                "total_agents": len(self.agent_ids),
                "partial_results": self.partial_results_ok
            }
        )


# ============================================================================
# Pattern Factory
# ============================================================================

class SwarmPatternFactory:
    """Factory for creating swarm coordination patterns."""

    @staticmethod
    def create_pattern(
        pattern_type: PatternType,
        coordinator: SwarmCoordinator,
        **kwargs
    ):
        """
        Create swarm pattern instance.

        Args:
            pattern_type: Type of pattern to create
            coordinator: SwarmCoordinator instance
            **kwargs: Pattern-specific arguments

        Returns:
            Pattern instance

        Example:
            >>> factory = SwarmPatternFactory()
            >>> pattern = factory.create_pattern(
            ...     PatternType.MASTER_WORKER,
            ...     coordinator=coordinator,
            ...     master_id="master",
            ...     worker_ids=["w1", "w2", "w3"]
            ... )
        """
        if pattern_type == PatternType.MASTER_WORKER:
            return MasterWorkerPattern(coordinator=coordinator, **kwargs)

        elif pattern_type == PatternType.PIPELINE:
            return PipelinePattern(coordinator=coordinator, **kwargs)

        elif pattern_type == PatternType.BROADCAST:
            return BroadcastPattern(coordinator=coordinator, **kwargs)

        elif pattern_type == PatternType.REDUCE:
            return ReducePattern(coordinator=coordinator, **kwargs)

        else:
            raise ValueError(f"Unknown pattern type: {pattern_type}")


# ============================================================================
# Exports
# ============================================================================

__all__ = [
    "PatternType",
    "PatternConfig",
    "PatternResult",
    "MasterWorkerPattern",
    "PipelinePattern",
    "BroadcastPattern",
    "ReducePattern",
    "SwarmPatternFactory"
]
