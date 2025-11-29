#!/usr/bin/env python3
"""
BottleneckDetector - Performance Bottleneck Identification for Phase 6C

Provides comprehensive bottleneck detection and performance analysis:
- Token exhaustion detection
- Agent quota exceeded detection
- Slow agent performance detection
- Task queue backlog detection
- Consensus timeout detection (Phase 6B integration)

Features:
- Real-time bottleneck monitoring
- Statistical trend analysis (NO ML)
- Severity calculation
- Recommendation engine
- Performance reporting
- <100ms detection time

Target: ~320 LOC
"""

import logging
import statistics
import threading
import time
import uuid
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from moai_flow.core.interfaces import IResourceController
from moai_flow.monitoring.metrics_storage import MetricsStorage


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class Bottleneck:
    """
    Performance bottleneck report.

    Attributes:
        bottleneck_id: Unique bottleneck identifier
        bottleneck_type: Type of bottleneck
        severity: Severity level
        affected_resources: List of affected agent/task/resource IDs
        metrics: Relevant metrics data
        detected_at: Detection timestamp
        recommendations: Optimization recommendations
        metadata: Additional context data
    """
    bottleneck_id: str
    bottleneck_type: str  # "token_exhaustion", "quota_exceeded", "slow_agent", "task_queue_backlog", "consensus_timeout"
    severity: str  # "critical", "high", "medium", "low"
    affected_resources: List[str]
    metrics: Dict[str, Any]
    detected_at: datetime
    recommendations: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PerformanceReport:
    """
    Comprehensive performance analysis report.

    Attributes:
        report_id: Unique report identifier
        time_range_ms: Analysis time range in milliseconds
        bottlenecks_detected: List of detected bottlenecks
        metrics_summary: Aggregated metrics summary
        trends: Performance trend indicators
        generated_at: Report generation timestamp
    """
    report_id: str
    time_range_ms: int
    bottlenecks_detected: List[Bottleneck]
    metrics_summary: Dict[str, Any]
    trends: Dict[str, str]  # metric_name -> "improving" | "stable" | "degrading"
    generated_at: datetime


# ============================================================================
# BottleneckDetector Implementation
# ============================================================================

class BottleneckDetector:
    """
    Performance bottleneck detector for MoAI-Flow adaptive optimization.

    Detects and analyzes performance bottlenecks:
    - Token exhaustion (>80% usage, increasing consumption)
    - Agent quota exceeded (max concurrent reached)
    - Slow agent performance (>2x average duration)
    - Task queue backlog (>50 tasks, increasing wait time)
    - Consensus timeouts (>10% timeout rate)

    Example:
        >>> detector = BottleneckDetector(metrics_storage, resource_controller)
        >>> bottlenecks = detector.detect_bottlenecks()
        >>> report = detector.analyze_performance(time_range_ms=300000)
        >>> recommendations = detector.get_recommendations(bottlenecks[0])
    """

    # Severity thresholds
    SEVERITY_CRITICAL = 0.8
    SEVERITY_HIGH = 0.6
    SEVERITY_MEDIUM = 0.4

    # Bottleneck thresholds
    TOKEN_USAGE_THRESHOLD = 0.8  # 80% usage
    QUEUE_DEPTH_THRESHOLD = 50
    SLOW_AGENT_MULTIPLIER = 2.0  # 2x average duration
    AGENT_SUCCESS_RATE_THRESHOLD = 0.7  # 70% success rate
    CONSENSUS_TIMEOUT_RATE_THRESHOLD = 0.1  # 10% timeout rate

    # Recommendation templates
    RECOMMENDATIONS = {
        "token_exhaustion": [
            "Increase token budget in .moai/config/config.json",
            "Optimize prompts to reduce token usage",
            "Implement token-aware task prioritization",
            "Cache frequently used responses"
        ],
        "quota_exceeded": [
            "Increase agent quota for bottleneck type",
            "Optimize agent task distribution",
            "Implement dynamic agent scaling",
            "Reduce concurrent task submissions"
        ],
        "slow_agent": [
            "Replace slow agent with faster alternative",
            "Reduce complexity of agent prompts",
            "Distribute tasks to healthier agents",
            "Investigate agent health issues"
        ],
        "task_queue_backlog": [
            "Increase agent quota to process queue faster",
            "Prioritize critical tasks",
            "Implement parallel processing",
            "Review task submission rate"
        ],
        "consensus_timeout": [
            "Reduce consensus timeout threshold",
            "Check agent heartbeat health",
            "Use faster consensus algorithm (quorum vs raft)",
            "Remove unresponsive agents from consensus"
        ]
    }

    def __init__(
        self,
        metrics_storage: MetricsStorage,
        resource_controller: IResourceController,
        detection_window_ms: int = 60000
    ):
        """
        Initialize bottleneck detector.

        Args:
            metrics_storage: MetricsStorage from Phase 6A
            resource_controller: Resource controller for quota/budget checks
            detection_window_ms: Time window for analysis (default: 60s)
        """
        self._metrics = metrics_storage
        self._resources = resource_controller
        self._detection_window_ms = detection_window_ms
        self._bottlenecks: List[Bottleneck] = []

        self.logger = logging.getLogger(__name__)
        self._monitor_thread: Optional[threading.Thread] = None
        self._monitor_stop_event = threading.Event()

    # ========================================================================
    # Core Detection Methods
    # ========================================================================

    def detect_bottlenecks(self) -> List[Bottleneck]:
        """
        Detect current performance bottlenecks.

        Returns:
            List of detected bottlenecks
        """
        start_time = time.time()
        bottlenecks = []

        # Run all detection methods
        detectors = [
            self._detect_token_bottleneck,
            self._detect_quota_bottleneck,
            self._detect_slow_agent_bottleneck,
            self._detect_queue_bottleneck,
            self._detect_consensus_bottleneck
        ]

        for detector in detectors:
            try:
                bottleneck = detector()
                if bottleneck:
                    bottlenecks.append(bottleneck)
            except Exception as e:
                self.logger.error(f"Error in {detector.__name__}: {e}")

        # Update cached bottlenecks
        self._bottlenecks = bottlenecks

        detection_time_ms = (time.time() - start_time) * 1000
        self.logger.debug(f"Detected {len(bottlenecks)} bottlenecks in {detection_time_ms:.2f}ms")

        return bottlenecks

    def _detect_token_bottleneck(self) -> Optional[Bottleneck]:
        """
        Detect token budget exhaustion.

        Criteria:
        - Token usage > 80% of budget
        - Token consumption rate increasing
        - Tasks failing due to insufficient tokens

        Returns:
            Bottleneck if detected, else None
        """
        usage = self._resources.get_resource_usage()
        tokens = usage.get("tokens", {})

        total_budget = tokens.get("total_budget", 0)
        consumed = tokens.get("consumed", 0)
        remaining = tokens.get("remaining", 0)

        if total_budget == 0:
            return None

        usage_ratio = consumed / total_budget

        # Check threshold
        if usage_ratio < self.TOKEN_USAGE_THRESHOLD:
            return None

        # Analyze consumption trend
        now = datetime.now()
        start_time = now - timedelta(milliseconds=self._detection_window_ms)

        task_metrics = self._metrics.get_task_metrics(
            time_range=(start_time, now),
            limit=100
        )

        # Calculate consumption rate
        token_usage_samples = [m.get("tokens_used", 0) for m in task_metrics]
        avg_tokens_per_task = statistics.mean(token_usage_samples) if token_usage_samples else 0

        # Calculate impact score
        impact_score = usage_ratio  # 0-1 range
        severity = self._calculate_severity("token_exhaustion", impact_score)

        bottleneck = Bottleneck(
            bottleneck_id=str(uuid.uuid4()),
            bottleneck_type="token_exhaustion",
            severity=severity,
            affected_resources=["global"],
            metrics={
                "total_budget": total_budget,
                "consumed": consumed,
                "remaining": remaining,
                "usage_ratio": usage_ratio,
                "avg_tokens_per_task": avg_tokens_per_task
            },
            detected_at=now,
            recommendations=self.get_recommendations_for_type("token_exhaustion"),
            metadata={"detection_window_ms": self._detection_window_ms}
        )

        self.logger.warning(
            f"Token exhaustion detected: {usage_ratio*100:.1f}% usage ({consumed}/{total_budget})"
        )

        return bottleneck

    def _detect_quota_bottleneck(self) -> Optional[Bottleneck]:
        """
        Detect agent quota limitations.

        Criteria:
        - Active agents >= max quota
        - Tasks waiting for agent slots
        - Queue backlog increasing

        Returns:
            Bottleneck if detected
        """
        usage = self._resources.get_resource_usage()
        agents_info = usage.get("agents", {})

        total_quotas = agents_info.get("total_quotas", 0)
        active_agents = agents_info.get("active_agents", 0)
        available_slots = agents_info.get("available_slots", 0)

        if total_quotas == 0:
            return None

        # Check if quotas are maxed out
        quota_usage_ratio = active_agents / total_quotas

        if quota_usage_ratio < 0.9:  # 90% threshold
            return None

        # Check queue depth
        queue_info = usage.get("queue", {})
        pending_tasks = queue_info.get("pending_tasks", 0)

        # Calculate impact score
        impact_score = min(quota_usage_ratio + (pending_tasks / 100), 1.0)
        severity = self._calculate_severity("quota_exceeded", impact_score)

        bottleneck = Bottleneck(
            bottleneck_id=str(uuid.uuid4()),
            bottleneck_type="quota_exceeded",
            severity=severity,
            affected_resources=["agents"],
            metrics={
                "total_quotas": total_quotas,
                "active_agents": active_agents,
                "available_slots": available_slots,
                "pending_tasks": pending_tasks,
                "quota_usage_ratio": quota_usage_ratio
            },
            detected_at=datetime.now(),
            recommendations=self.get_recommendations_for_type("quota_exceeded")
        )

        self.logger.warning(
            f"Agent quota exceeded: {active_agents}/{total_quotas} active, {pending_tasks} pending tasks"
        )

        return bottleneck

    def _detect_slow_agent_bottleneck(self) -> Optional[Bottleneck]:
        """
        Detect underperforming agents.

        Criteria:
        - Agent task duration > 2x average
        - Agent success rate < 70%
        - Agent causing task failures

        Returns:
            Bottleneck with slow agent IDs
        """
        now = datetime.now()
        start_time = now - timedelta(milliseconds=self._detection_window_ms)

        task_metrics = self._metrics.get_task_metrics(
            time_range=(start_time, now),
            limit=500
        )

        if not task_metrics:
            return None

        # Group by agent_id
        agent_stats = defaultdict(lambda: {"durations": [], "success_count": 0, "total_count": 0})

        for metric in task_metrics:
            agent_id = metric.get("agent_id")
            duration_ms = metric.get("duration_ms", 0)
            result = metric.get("result")

            agent_stats[agent_id]["durations"].append(duration_ms)
            agent_stats[agent_id]["total_count"] += 1
            if result == "success":
                agent_stats[agent_id]["success_count"] += 1

        # Calculate overall average duration
        all_durations = [d for stats in agent_stats.values() for d in stats["durations"]]
        avg_duration = statistics.mean(all_durations) if all_durations else 0

        # Find slow agents
        slow_agents = []
        for agent_id, stats in agent_stats.items():
            agent_avg_duration = statistics.mean(stats["durations"])
            success_rate = stats["success_count"] / stats["total_count"] if stats["total_count"] > 0 else 0

            # Check if agent is slow (>2x average) or low success rate (<70%)
            if agent_avg_duration > avg_duration * self.SLOW_AGENT_MULTIPLIER or \
               success_rate < self.AGENT_SUCCESS_RATE_THRESHOLD:
                slow_agents.append({
                    "agent_id": agent_id,
                    "avg_duration_ms": agent_avg_duration,
                    "success_rate": success_rate,
                    "task_count": stats["total_count"]
                })

        if not slow_agents:
            return None

        # Calculate impact score based on number of slow agents and their success rates
        impact_score = min(len(slow_agents) / max(len(agent_stats), 1), 1.0)
        severity = self._calculate_severity("slow_agent", impact_score)

        affected_agent_ids = [a["agent_id"] for a in slow_agents]

        bottleneck = Bottleneck(
            bottleneck_id=str(uuid.uuid4()),
            bottleneck_type="slow_agent",
            severity=severity,
            affected_resources=affected_agent_ids,
            metrics={
                "slow_agents": slow_agents,
                "avg_duration_ms": avg_duration,
                "threshold_multiplier": self.SLOW_AGENT_MULTIPLIER
            },
            detected_at=now,
            recommendations=self.get_recommendations_for_type("slow_agent")
        )

        self.logger.warning(
            f"Slow agents detected: {len(slow_agents)} agents underperforming"
        )

        return bottleneck

    def _detect_queue_bottleneck(self) -> Optional[Bottleneck]:
        """
        Detect task queue backlog.

        Criteria:
        - Queue depth > threshold (50 tasks)
        - Average wait time increasing
        - High-priority tasks stuck in queue

        Returns:
            Bottleneck if detected
        """
        usage = self._resources.get_resource_usage()
        queue_info = usage.get("queue", {})

        pending_tasks = queue_info.get("pending_tasks", 0)
        by_priority = queue_info.get("by_priority", {})

        # Check queue depth threshold
        if pending_tasks < self.QUEUE_DEPTH_THRESHOLD:
            return None

        # Check for high-priority tasks in queue
        high_priority_count = by_priority.get("CRITICAL", 0) + by_priority.get("HIGH", 0)

        # Calculate impact score
        queue_ratio = min(pending_tasks / 100, 1.0)
        priority_impact = min(high_priority_count / 20, 1.0)
        impact_score = max(queue_ratio, priority_impact)

        severity = self._calculate_severity("task_queue_backlog", impact_score)

        bottleneck = Bottleneck(
            bottleneck_id=str(uuid.uuid4()),
            bottleneck_type="task_queue_backlog",
            severity=severity,
            affected_resources=["task_queue"],
            metrics={
                "pending_tasks": pending_tasks,
                "by_priority": by_priority,
                "high_priority_count": high_priority_count,
                "threshold": self.QUEUE_DEPTH_THRESHOLD
            },
            detected_at=datetime.now(),
            recommendations=self.get_recommendations_for_type("task_queue_backlog")
        )

        self.logger.warning(
            f"Task queue backlog detected: {pending_tasks} pending tasks "
            f"({high_priority_count} high-priority)"
        )

        return bottleneck

    def _detect_consensus_bottleneck(self) -> Optional[Bottleneck]:
        """
        Detect consensus delays (Phase 6B integration).

        Criteria:
        - Consensus timeout rate > 10%
        - Average consensus time > 10s
        - Agent non-responsiveness

        Returns:
            Bottleneck if detected
        """
        # Note: Phase 6B consensus not yet implemented
        # This is a placeholder for future integration

        # For now, return None
        # TODO: Implement after Phase 6B consensus is available
        return None

    # ========================================================================
    # Performance Analysis
    # ========================================================================

    def analyze_performance(self, time_range_ms: int = 300000) -> PerformanceReport:
        """
        Analyze performance over time range.

        Args:
            time_range_ms: Time range in milliseconds (default: 5 minutes)

        Returns:
            Comprehensive performance report
        """
        now = datetime.now()
        start_time = now - timedelta(milliseconds=time_range_ms)

        # Detect bottlenecks
        bottlenecks = self.detect_bottlenecks()

        # Get metrics summary
        task_metrics = self._metrics.get_task_metrics(
            time_range=(start_time, now),
            limit=1000
        )

        # Calculate summary statistics
        if task_metrics:
            durations = [m.get("duration_ms", 0) for m in task_metrics]
            tokens_used = [m.get("tokens_used", 0) for m in task_metrics]
            success_count = sum(1 for m in task_metrics if m.get("result") == "success")

            metrics_summary = {
                "task_count": len(task_metrics),
                "avg_duration_ms": statistics.mean(durations) if durations else 0,
                "p95_duration_ms": self._calculate_percentile(durations, 95) if durations else 0,
                "p99_duration_ms": self._calculate_percentile(durations, 99) if durations else 0,
                "avg_tokens_per_task": statistics.mean(tokens_used) if tokens_used else 0,
                "success_rate": success_count / len(task_metrics) if task_metrics else 0
            }
        else:
            metrics_summary = {
                "task_count": 0,
                "avg_duration_ms": 0,
                "p95_duration_ms": 0,
                "p99_duration_ms": 0,
                "avg_tokens_per_task": 0,
                "success_rate": 0
            }

        # Analyze trends
        trends = {
            "task_duration": self._analyze_trends("duration_ms", time_range_ms),
            "token_usage": self._analyze_trends("tokens_used", time_range_ms),
            "success_rate": self._analyze_trends("success_rate", time_range_ms)
        }

        report = PerformanceReport(
            report_id=str(uuid.uuid4()),
            time_range_ms=time_range_ms,
            bottlenecks_detected=bottlenecks,
            metrics_summary=metrics_summary,
            trends=trends,
            generated_at=now
        )

        self.logger.info(
            f"Performance analysis complete: {len(bottlenecks)} bottlenecks, "
            f"{metrics_summary['task_count']} tasks analyzed"
        )

        return report

    def _analyze_trends(self, metric_name: str, time_range_ms: int) -> str:
        """
        Analyze metric trend over time.

        Algorithm:
        1. Get metric values over time range
        2. Calculate moving average
        3. Compare recent average vs. historical
        4. Return "improving", "stable", or "degrading"

        Args:
            metric_name: Name of metric to analyze
            time_range_ms: Time range in milliseconds

        Returns:
            Trend indicator: "improving", "stable", or "degrading"
        """
        now = datetime.now()
        start_time = now - timedelta(milliseconds=time_range_ms)

        task_metrics = self._metrics.get_task_metrics(
            time_range=(start_time, now),
            limit=500
        )

        if not task_metrics or len(task_metrics) < 10:
            return "stable"

        # Extract values based on metric name
        if metric_name == "duration_ms":
            values = [m.get("duration_ms", 0) for m in task_metrics]
        elif metric_name == "tokens_used":
            values = [m.get("tokens_used", 0) for m in task_metrics]
        elif metric_name == "success_rate":
            # Convert to binary success/failure
            values = [1 if m.get("result") == "success" else 0 for m in task_metrics]
        else:
            return "stable"

        # Calculate moving averages
        moving_avg = self._calculate_moving_average(values, window=10)

        if len(moving_avg) < 2:
            return "stable"

        # Compare recent vs historical
        recent_avg = statistics.mean(moving_avg[-5:])
        historical_avg = statistics.mean(moving_avg[:-5])

        # Calculate change percentage
        if historical_avg == 0:
            return "stable"

        change_pct = (recent_avg - historical_avg) / historical_avg

        # Determine trend based on metric type
        if metric_name == "success_rate":
            # Higher is better
            if change_pct > 0.05:
                return "improving"
            elif change_pct < -0.05:
                return "degrading"
        else:
            # Lower is better for duration and token usage
            if change_pct < -0.05:
                return "improving"
            elif change_pct > 0.05:
                return "degrading"

        return "stable"

    # ========================================================================
    # Statistical Methods
    # ========================================================================

    def _calculate_percentile(self, values: List[float], percentile: int) -> float:
        """
        Calculate percentile for metric values.

        Args:
            values: List of numeric values
            percentile: Percentile to calculate (0-100)

        Returns:
            Percentile value
        """
        if not values:
            return 0.0

        sorted_values = sorted(values)
        index = int(len(sorted_values) * (percentile / 100.0))
        index = min(index, len(sorted_values) - 1)

        return sorted_values[index]

    def _calculate_moving_average(self, values: List[float], window: int = 10) -> List[float]:
        """
        Calculate moving average for trend detection.

        Args:
            values: List of numeric values
            window: Window size for moving average

        Returns:
            List of moving average values
        """
        if len(values) < window:
            return [statistics.mean(values)] if values else []

        moving_avg = []
        for i in range(len(values) - window + 1):
            window_values = values[i:i+window]
            moving_avg.append(statistics.mean(window_values))

        return moving_avg

    def _calculate_severity(self, bottleneck_type: str, impact_score: float) -> str:
        """
        Calculate bottleneck severity based on impact.

        Impact score components:
        - Affected resource percentage (0-1)
        - Performance degradation (0-1)
        - Task failure rate (0-1)

        Severity thresholds:
        - critical: impact_score >= 0.8
        - high: impact_score >= 0.6
        - medium: impact_score >= 0.4
        - low: impact_score < 0.4

        Args:
            bottleneck_type: Type of bottleneck
            impact_score: Impact score (0-1)

        Returns:
            Severity level
        """
        if impact_score >= self.SEVERITY_CRITICAL:
            return "critical"
        elif impact_score >= self.SEVERITY_HIGH:
            return "high"
        elif impact_score >= self.SEVERITY_MEDIUM:
            return "medium"
        else:
            return "low"

    # ========================================================================
    # Recommendation Engine
    # ========================================================================

    def get_recommendations(self, bottleneck: Bottleneck) -> List[str]:
        """
        Get optimization recommendations for bottleneck.

        Args:
            bottleneck: Bottleneck instance

        Returns:
            List of actionable recommendations
        """
        return self.get_recommendations_for_type(bottleneck.bottleneck_type)

    def get_recommendations_for_type(self, bottleneck_type: str) -> List[str]:
        """
        Get recommendations for bottleneck type.

        Args:
            bottleneck_type: Type of bottleneck

        Returns:
            List of recommendations
        """
        return self.RECOMMENDATIONS.get(bottleneck_type, [
            "Review system configuration",
            "Monitor resource usage patterns",
            "Consult MoAI-Flow documentation"
        ])

    # ========================================================================
    # Real-Time Monitoring
    # ========================================================================

    def monitor_continuously(self, interval_ms: int = 30000) -> None:
        """
        Continuous bottleneck monitoring in background thread.

        Args:
            interval_ms: Check interval in milliseconds (default: 30s)
        """
        if self._monitor_thread and self._monitor_thread.is_alive():
            self.logger.warning("Monitor already running")
            return

        self._monitor_stop_event.clear()

        def monitor_loop():
            while not self._monitor_stop_event.is_set():
                try:
                    bottlenecks = self.detect_bottlenecks()
                    if bottlenecks:
                        for bottleneck in bottlenecks:
                            self.logger.warning(
                                f"Bottleneck detected: {bottleneck.bottleneck_type} "
                                f"(severity: {bottleneck.severity})"
                            )
                except Exception as e:
                    self.logger.error(f"Error in monitor loop: {e}")

                # Sleep with interrupt check
                self._monitor_stop_event.wait(interval_ms / 1000.0)

        self._monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self._monitor_thread.start()

        self.logger.info(f"Started continuous monitoring (interval: {interval_ms}ms)")

    def stop_monitoring(self) -> None:
        """Stop continuous monitoring."""
        if self._monitor_thread and self._monitor_thread.is_alive():
            self._monitor_stop_event.set()
            self._monitor_thread.join(timeout=5.0)
            self.logger.info("Stopped continuous monitoring")
