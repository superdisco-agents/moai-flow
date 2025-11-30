#!/usr/bin/env python3
"""
Healing Analytics Dashboard for MoAI-Flow
==========================================

Provides comprehensive analytics and insights for the self-healing system.
Tracks healing effectiveness, strategy performance, and generates recommendations.

Key Metrics:
- Overall healing success rate
- Strategy-specific effectiveness
- Mean Time To Recovery (MTTR)
- Failure pattern analysis
- Healing time distribution
- Trend analysis

Features:
- Real-time statistics
- Historical analysis
- Strategy comparison
- Recommendation engine
- Performance trending

Example:
    >>> analytics = HealingAnalytics(self_healer)
    >>> stats = analytics.get_overall_stats()
    >>> print(f"Success rate: {stats.success_rate:.1%}")
    >>>
    >>> effectiveness = analytics.get_strategy_effectiveness()
    >>> for strategy in effectiveness:
    ...     print(f"{strategy.strategy_name}: {strategy.success_rate:.1%}")
    >>>
    >>> recommendations = analytics.generate_recommendations()

Version: 1.0.0
Phase: 7 (Track 3 Week 4-6)
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timezone, timedelta
import time
import logging
import threading
from collections import defaultdict, Counter

from .self_healer import SelfHealer, HealingResult

logger = logging.getLogger(__name__)


# ============================================================================
# Analytics Data Structures
# ============================================================================

@dataclass
class HealingStats:
    """
    Overall healing statistics.

    Attributes:
        total_failures: Total failures detected
        total_healings: Total healing attempts
        success_rate: Overall success rate (0.0-1.0)
        avg_healing_time_ms: Average healing time (milliseconds)
        by_strategy: Healing counts by strategy name
        by_failure_type: Healing counts by failure type
        mttr_ms: Mean Time To Recovery (milliseconds)
    """
    total_failures: int
    total_healings: int
    success_rate: float
    avg_healing_time_ms: float
    by_strategy: Dict[str, int]
    by_failure_type: Dict[str, int]
    mttr_ms: float


@dataclass
class StrategyEffectiveness:
    """
    Strategy effectiveness metrics.

    Attributes:
        strategy_name: Name of healing strategy
        success_count: Number of successful healings
        failure_count: Number of failed healings
        success_rate: Success rate (0.0-1.0)
        avg_healing_time_ms: Average healing time
        trend: Performance trend (improving/stable/degrading)
        recommendation: Suggested action (keep/tune/replace)
    """
    strategy_name: str
    success_count: int
    failure_count: int
    success_rate: float
    avg_healing_time_ms: float
    trend: str  # "improving", "stable", "degrading"
    recommendation: str = ""


# ============================================================================
# Healing Analytics Implementation
# ============================================================================

class HealingAnalytics:
    """
    Analytics and reporting for self-healing system.

    Provides insights into:
    - Healing effectiveness (success rates, MTTR)
    - Strategy performance (comparison, trends)
    - Failure patterns (common failures, timing)
    - Recommendations (strategy tuning, improvements)

    Thread-safe for concurrent access.
    """

    def __init__(self, self_healer: SelfHealer):
        """
        Initialize healing analytics.

        Args:
            self_healer: SelfHealer instance to analyze
        """
        self.self_healer = self_healer

        # Analytics cache
        self._stats_cache: Optional[HealingStats] = None
        self._cache_timestamp: float = 0
        self._cache_ttl_seconds: float = 60.0  # Cache for 60 seconds

        # Trend tracking
        self._strategy_history: Dict[str, List[Tuple[datetime, bool]]] = defaultdict(list)

        # Thread safety
        self._lock = threading.RLock()

        logger.info("HealingAnalytics initialized")

    def get_overall_stats(
        self,
        time_range_ms: Optional[int] = None
    ) -> HealingStats:
        """
        Get overall healing statistics.

        Args:
            time_range_ms: Optional time range in milliseconds
                          (None for all-time stats)

        Returns:
            HealingStats with overall metrics
        """
        with self._lock:
            # Check cache
            current_time = time.time()
            if (self._stats_cache is not None and
                current_time - self._cache_timestamp < self._cache_ttl_seconds and
                time_range_ms is None):
                return self._stats_cache

            # Get healing history
            history = self.self_healer.get_healing_history(limit=10000)

            # Filter by time range if specified
            if time_range_ms is not None:
                cutoff_time = datetime.now(timezone.utc) - timedelta(
                    milliseconds=time_range_ms
                )
                history = [
                    h for h in history
                    if h.timestamp >= cutoff_time
                ]

            if not history:
                return HealingStats(
                    total_failures=0,
                    total_healings=0,
                    success_rate=0.0,
                    avg_healing_time_ms=0.0,
                    by_strategy={},
                    by_failure_type={},
                    mttr_ms=0.0
                )

            # Calculate statistics
            total_healings = len(history)
            successful = sum(1 for h in history if h.success)
            success_rate = successful / total_healings if total_healings > 0 else 0.0

            # Average healing time
            total_time = sum(h.duration_ms for h in history)
            avg_time = total_time / total_healings if total_healings > 0 else 0.0

            # Count by strategy
            by_strategy = Counter(h.strategy_used for h in history)

            # Count by failure type (from metadata)
            by_failure_type = Counter()
            for h in history:
                failure_type = h.failure_id.split("_")[0] if "_" in h.failure_id else "unknown"
                by_failure_type[failure_type] += 1

            # Calculate MTTR (Mean Time To Recovery)
            mttr = self.calculate_mttr(None)

            stats = HealingStats(
                total_failures=total_healings,
                total_healings=total_healings,
                success_rate=success_rate,
                avg_healing_time_ms=avg_time,
                by_strategy=dict(by_strategy),
                by_failure_type=dict(by_failure_type),
                mttr_ms=mttr
            )

            # Update cache
            if time_range_ms is None:
                self._stats_cache = stats
                self._cache_timestamp = current_time

            return stats

    def get_strategy_effectiveness(self) -> List[StrategyEffectiveness]:
        """
        Analyze effectiveness of each healing strategy.

        Returns:
            List of StrategyEffectiveness sorted by success rate
        """
        with self._lock:
            history = self.self_healer.get_healing_history(limit=10000)

            if not history:
                return []

            # Group by strategy
            by_strategy: Dict[str, List[HealingResult]] = defaultdict(list)
            for result in history:
                by_strategy[result.strategy_used].append(result)

            effectiveness_list = []

            for strategy_name, results in by_strategy.items():
                success_count = sum(1 for r in results if r.success)
                failure_count = len(results) - success_count
                success_rate = success_count / len(results) if results else 0.0

                # Average healing time
                avg_time = (
                    sum(r.duration_ms for r in results) / len(results)
                    if results else 0.0
                )

                # Determine trend
                trend = self._analyze_strategy_trend(strategy_name, results)

                # Generate recommendation
                recommendation = self._generate_strategy_recommendation(
                    strategy_name,
                    success_rate,
                    trend
                )

                effectiveness_list.append(StrategyEffectiveness(
                    strategy_name=strategy_name,
                    success_count=success_count,
                    failure_count=failure_count,
                    success_rate=success_rate,
                    avg_healing_time_ms=avg_time,
                    trend=trend,
                    recommendation=recommendation
                ))

            # Sort by success rate (descending)
            effectiveness_list.sort(key=lambda s: s.success_rate, reverse=True)

            return effectiveness_list

    def _analyze_strategy_trend(
        self,
        strategy_name: str,
        results: List[HealingResult]
    ) -> str:
        """
        Analyze performance trend for strategy.

        Compares recent performance to historical average.

        Args:
            strategy_name: Name of strategy
            results: Historical results

        Returns:
            "improving", "stable", or "degrading"
        """
        if len(results) < 10:
            return "stable"  # Not enough data

        # Split into recent and historical
        recent_count = min(len(results) // 3, 20)
        recent_results = results[-recent_count:]
        historical_results = results[:-recent_count]

        # Calculate success rates
        recent_success_rate = (
            sum(1 for r in recent_results if r.success) / len(recent_results)
        )
        historical_success_rate = (
            sum(1 for r in historical_results if r.success) / len(historical_results)
            if historical_results else 0.0
        )

        # Determine trend
        difference = recent_success_rate - historical_success_rate

        if difference > 0.05:  # 5% improvement
            return "improving"
        elif difference < -0.05:  # 5% degradation
            return "degrading"
        else:
            return "stable"

    def _generate_strategy_recommendation(
        self,
        strategy_name: str,
        success_rate: float,
        trend: str
    ) -> str:
        """
        Generate recommendation for strategy.

        Args:
            strategy_name: Name of strategy
            success_rate: Current success rate
            trend: Performance trend

        Returns:
            Recommendation string
        """
        if success_rate >= 0.9 and trend in ["improving", "stable"]:
            return "keep"
        elif success_rate >= 0.7 and trend == "degrading":
            return "tune"
        elif success_rate < 0.5:
            return "replace"
        elif trend == "degrading":
            return "investigate"
        else:
            return "monitor"

    def calculate_mttr(
        self,
        failure_type: Optional[str] = None
    ) -> float:
        """
        Calculate Mean Time To Recovery.

        MTTR = Average time from failure detection to successful recovery

        Args:
            failure_type: Optional failure type to filter by

        Returns:
            MTTR in milliseconds
        """
        with self._lock:
            history = self.self_healer.get_healing_history(limit=10000)

            # Filter by failure type if specified
            if failure_type:
                history = [
                    h for h in history
                    if failure_type in h.failure_id
                ]

            # Only consider successful healings
            successful = [h for h in history if h.success]

            if not successful:
                return 0.0

            # MTTR is the average healing duration
            total_time = sum(h.duration_ms for h in successful)
            return total_time / len(successful)

    def analyze_failure_patterns(self) -> Dict[str, Any]:
        """
        Analyze failure patterns.

        Returns:
            Dictionary with pattern analysis:
            - most_common_failures: Top failure types
            - failure_frequency: Failures per hour
            - time_of_day_patterns: Hourly distribution
            - agent_patterns: Per-agent failure rates
        """
        with self._lock:
            history = self.self_healer.get_healing_history(limit=10000)

            if not history:
                return {
                    "most_common_failures": [],
                    "failure_frequency": 0.0,
                    "time_of_day_patterns": {},
                    "agent_patterns": {}
                }

            # Most common failures
            failure_types = []
            for h in history:
                failure_type = h.failure_id.split("_")[0] if "_" in h.failure_id else "unknown"
                failure_types.append(failure_type)

            most_common = Counter(failure_types).most_common(5)

            # Failure frequency (failures per hour)
            if len(history) >= 2:
                time_span = (history[0].timestamp - history[-1].timestamp).total_seconds()
                hours = max(time_span / 3600, 1)
                frequency = len(history) / hours
            else:
                frequency = 0.0

            # Time of day patterns
            time_patterns: Dict[int, int] = defaultdict(int)
            for h in history:
                hour = h.timestamp.hour
                time_patterns[hour] += 1

            # Agent-specific patterns
            agent_patterns: Dict[str, int] = defaultdict(int)
            for h in history:
                # Extract agent_id from metadata if available
                agent_id = h.metadata.get("agent_id", "unknown")
                if agent_id and agent_id != "unknown":
                    agent_patterns[agent_id] += 1

            return {
                "most_common_failures": [
                    {"type": ftype, "count": count}
                    for ftype, count in most_common
                ],
                "failure_frequency": frequency,
                "time_of_day_patterns": dict(time_patterns),
                "agent_patterns": dict(agent_patterns)
            }

    def generate_recommendations(self) -> List[str]:
        """
        Generate actionable recommendations.

        Analyzes current performance and suggests improvements:
        - Strategy tuning (adjust thresholds)
        - New strategy suggestions
        - Resource allocation changes
        - Preventive actions

        Returns:
            List of recommendation strings
        """
        recommendations = []

        # Get overall stats
        stats = self.get_overall_stats()

        # Recommendation 1: Overall success rate
        if stats.success_rate < 0.7:
            recommendations.append(
                f"Overall success rate is low ({stats.success_rate:.1%}). "
                f"Consider reviewing strategy configurations."
            )
        elif stats.success_rate > 0.95:
            recommendations.append(
                f"Excellent success rate ({stats.success_rate:.1%}). "
                f"Current strategies are effective."
            )

        # Recommendation 2: Strategy-specific
        effectiveness = self.get_strategy_effectiveness()
        for strategy in effectiveness:
            if strategy.recommendation == "replace":
                recommendations.append(
                    f"Strategy '{strategy.strategy_name}' has low success rate "
                    f"({strategy.success_rate:.1%}). Consider replacing or redesigning."
                )
            elif strategy.recommendation == "tune":
                recommendations.append(
                    f"Strategy '{strategy.strategy_name}' is degrading. "
                    f"Review and tune configuration parameters."
                )

        # Recommendation 3: MTTR optimization
        if stats.mttr_ms > 5000:  # > 5 seconds
            recommendations.append(
                f"MTTR is high ({stats.mttr_ms:.0f}ms). "
                f"Consider optimizing healing strategies for faster recovery."
            )

        # Recommendation 4: Failure patterns
        patterns = self.analyze_failure_patterns()
        if patterns["most_common_failures"]:
            top_failure = patterns["most_common_failures"][0]
            recommendations.append(
                f"Most common failure: {top_failure['type']} ({top_failure['count']} occurrences). "
                f"Implement preventive measures."
            )

        # Recommendation 5: Resource allocation
        if "resource_exhaustion" in stats.by_failure_type:
            count = stats.by_failure_type["resource_exhaustion"]
            recommendations.append(
                f"Resource exhaustion detected {count} times. "
                f"Enable GradualDegradationStrategy."
            )

        # Recommendation 6: Circuit breaker
        if any("timeout" in ft for ft in stats.by_failure_type.keys()):
            recommendations.append(
                "Timeout failures detected. "
                "Enable CircuitBreakerStrategy to prevent cascading failures."
            )

        if not recommendations:
            recommendations.append(
                "System is performing well. Continue monitoring."
            )

        return recommendations

    def get_healing_timeline(
        self,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get recent healing events as timeline.

        Args:
            limit: Maximum events to return

        Returns:
            List of timeline events (most recent first)
        """
        with self._lock:
            history = self.self_healer.get_healing_history(limit=limit)

            timeline = []
            for result in history:
                timeline.append({
                    "timestamp": result.timestamp.isoformat(),
                    "failure_id": result.failure_id,
                    "strategy": result.strategy_used,
                    "success": result.success,
                    "duration_ms": result.duration_ms,
                    "actions": result.actions_taken
                })

            return timeline

    def export_report(self, format: str = "dict") -> Dict[str, Any]:
        """
        Export comprehensive analytics report.

        Args:
            format: Export format ("dict", "json", etc.)

        Returns:
            Complete analytics report
        """
        stats = self.get_overall_stats()
        effectiveness = self.get_strategy_effectiveness()
        patterns = self.analyze_failure_patterns()
        recommendations = self.generate_recommendations()
        timeline = self.get_healing_timeline(limit=20)

        report = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "overall_stats": {
                "total_healings": stats.total_healings,
                "success_rate": stats.success_rate,
                "avg_healing_time_ms": stats.avg_healing_time_ms,
                "mttr_ms": stats.mttr_ms,
                "by_strategy": stats.by_strategy,
                "by_failure_type": stats.by_failure_type
            },
            "strategy_effectiveness": [
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
            "failure_patterns": patterns,
            "recommendations": recommendations,
            "recent_timeline": timeline
        }

        return report


__all__ = [
    "HealingAnalytics",
    "HealingStats",
    "StrategyEffectiveness",
]
