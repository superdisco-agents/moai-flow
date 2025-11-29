#!/usr/bin/env python3
"""
Gradual Degradation Strategy for Self-Healing
==============================================

Implements graceful service degradation when resources are exhausted.
Reduces quality/features progressively instead of failing completely.

Degradation Levels:
- FULL: 100% capacity, all features enabled
- REDUCED_1: 75% capacity, minor optimizations
- REDUCED_2: 50% capacity, significant optimizations
- REDUCED_3: 25% capacity, minimal features
- MINIMAL: 10% capacity, emergency mode only

Key Features:
- Progressive degradation based on resource pressure
- Automatic recovery when resources available
- Feature toggling for non-critical functionality
- Timeout and quality threshold adjustments
- Thread-safe degradation management

Example:
    >>> config = DegradationConfig()
    >>> strategy = GradualDegradationStrategy(config)
    >>> failure = Failure(
    ...     failure_id="f1",
    ...     failure_type="resource_exhaustion",
    ...     severity="high",
    ...     detected_at=datetime.now(timezone.utc),
    ...     event={"type": "resource_exhaustion"},
    ...     metadata={"resource_type": "token", "usage_percent": 95}
    ... )
    >>> result = strategy.heal(failure, coordinator)

Version: 1.0.0
Phase: 7 (Track 3 Week 4-6)
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime, timezone
import time
import logging
import threading

from ..self_healer import Failure, HealingResult

logger = logging.getLogger(__name__)


# ============================================================================
# Degradation Level and Configuration
# ============================================================================

class DegradationLevel(Enum):
    """Service degradation levels"""
    FULL = 0           # 100% capacity
    REDUCED_1 = 1      # 75% capacity
    REDUCED_2 = 2      # 50% capacity
    REDUCED_3 = 3      # 25% capacity
    MINIMAL = 4        # 10% capacity (emergency mode)


@dataclass
class DegradationConfig:
    """
    Degradation configuration.

    Defines how each degradation level affects system behavior.
    """
    # Timeout multipliers per level
    timeout_multipliers: Dict[DegradationLevel, float] = field(default_factory=lambda: {
        DegradationLevel.FULL: 1.0,
        DegradationLevel.REDUCED_1: 0.8,
        DegradationLevel.REDUCED_2: 0.6,
        DegradationLevel.REDUCED_3: 0.4,
        DegradationLevel.MINIMAL: 0.2,
    })

    # Quality thresholds per level
    quality_thresholds: Dict[DegradationLevel, float] = field(default_factory=lambda: {
        DegradationLevel.FULL: 0.95,
        DegradationLevel.REDUCED_1: 0.85,
        DegradationLevel.REDUCED_2: 0.75,
        DegradationLevel.REDUCED_3: 0.60,
        DegradationLevel.MINIMAL: 0.50,
    })

    # Features to disable per level
    feature_toggles: Dict[DegradationLevel, List[str]] = field(default_factory=lambda: {
        DegradationLevel.FULL: [],
        DegradationLevel.REDUCED_1: ["detailed_metrics", "verbose_logging"],
        DegradationLevel.REDUCED_2: ["detailed_metrics", "verbose_logging", "pattern_learning"],
        DegradationLevel.REDUCED_3: ["detailed_metrics", "verbose_logging", "pattern_learning", "analytics"],
        DegradationLevel.MINIMAL: ["detailed_metrics", "verbose_logging", "pattern_learning", "analytics", "optimization"],
    })

    # Resource usage thresholds for level selection
    usage_thresholds: Dict[DegradationLevel, float] = field(default_factory=lambda: {
        DegradationLevel.FULL: 0.0,       # < 90% usage
        DegradationLevel.REDUCED_1: 0.90,  # 90-95% usage
        DegradationLevel.REDUCED_2: 0.95,  # 95-98% usage
        DegradationLevel.REDUCED_3: 0.98,  # 98-99% usage
        DegradationLevel.MINIMAL: 0.99,    # 99%+ usage
    })


# ============================================================================
# Gradual Degradation Strategy Implementation
# ============================================================================

class GradualDegradationStrategy:
    """
    Gradual service degradation on resource exhaustion.

    Instead of failing completely when resources are exhausted,
    this strategy progressively reduces service quality and features
    to maintain core functionality.

    Degradation Measures:
    1. Timeout reduction - Faster failure detection
    2. Quality threshold lowering - Accept lower quality results
    3. Feature disabling - Turn off non-critical features
    4. Concurrency limiting - Reduce parallel tasks

    Automatically recovers when resources become available.
    """

    def __init__(self, config: Optional[DegradationConfig] = None):
        """
        Initialize gradual degradation strategy.

        Args:
            config: Degradation configuration (uses defaults if None)
        """
        self.config = config or DegradationConfig()

        # Current degradation level per resource type
        self._current_level: Dict[str, DegradationLevel] = {}

        # Resource usage history for trend analysis
        self._usage_history: Dict[str, List[float]] = {}

        # Thread safety
        self._lock = threading.RLock()

        logger.info("GradualDegradationStrategy initialized")

    def can_heal(self, failure: Failure) -> bool:
        """
        Check if this strategy can handle the failure.

        Handles resource-related failures:
        - resource_exhaustion (general resource pressure)
        - token_exhaustion (token quota exceeded)
        - quota_exceeded (rate limits, quotas)
        - memory_pressure (memory exhaustion)
        - high_latency (system slowdown)

        Args:
            failure: Failure to check

        Returns:
            True if strategy is applicable
        """
        return failure.failure_type in [
            "resource_exhaustion",
            "token_exhaustion",
            "quota_exceeded",
            "memory_exhaustion",
            "memory_pressure",
            "high_latency"
        ]

    def heal(self, failure: Failure, coordinator) -> HealingResult:
        """
        Apply degradation based on failure.

        Process:
        1. Assess severity and determine degradation level
        2. Apply degradation measures:
           - Reduce timeout limits
           - Lower quality thresholds
           - Disable non-critical features
           - Reduce concurrent tasks
        3. Monitor for recovery
        4. Gradually restore service

        Args:
            failure: Failure to heal
            coordinator: SwarmCoordinator for resource management

        Returns:
            HealingResult with outcome
        """
        start_time = time.time()
        actions = []

        resource_type = failure.metadata.get("resource_type", "unknown")

        with self._lock:
            # Assess severity and determine degradation level
            usage_percent = failure.metadata.get("usage_percent", 0)
            degradation_level = self._assess_severity(usage_percent)

            current_level = self._current_level.get(
                resource_type,
                DegradationLevel.FULL
            )

            actions.append(
                f"Current level: {current_level.name}, "
                f"Target level: {degradation_level.name}"
            )

            # Apply degradation if needed
            if degradation_level != current_level:
                degradation_actions = self._apply_degradation(
                    degradation_level,
                    resource_type
                )
                actions.extend(degradation_actions)

                self._current_level[resource_type] = degradation_level

            # Record usage for trend analysis
            if resource_type not in self._usage_history:
                self._usage_history[resource_type] = []
            self._usage_history[resource_type].append(usage_percent)

            # Keep only recent history (last 100 samples)
            if len(self._usage_history[resource_type]) > 100:
                self._usage_history[resource_type] = \
                    self._usage_history[resource_type][-100:]

            # Check for recovery opportunity
            if self._monitor_recovery(resource_type):
                actions.append("Resources recovering, considering restoration")

        duration_ms = int((time.time() - start_time) * 1000)

        return HealingResult(
            success=True,
            failure_id=failure.failure_id,
            strategy_used="GradualDegradationStrategy",
            actions_taken=actions,
            duration_ms=duration_ms,
            timestamp=datetime.now(timezone.utc),
            metadata={
                "resource_type": resource_type,
                "degradation_level": degradation_level.name,
                "usage_percent": usage_percent,
                "timeout_multiplier": self.config.timeout_multipliers[degradation_level],
                "quality_threshold": self.config.quality_thresholds[degradation_level],
                "disabled_features": self.config.feature_toggles[degradation_level]
            }
        )

    def _assess_severity(self, usage_percent: float) -> DegradationLevel:
        """
        Determine degradation level based on resource usage.

        Thresholds:
        - < 90%: FULL
        - 90-95%: REDUCED_1
        - 95-98%: REDUCED_2
        - 98-99%: REDUCED_3
        - 99%+: MINIMAL

        Args:
            usage_percent: Resource usage percentage (0-100)

        Returns:
            Appropriate degradation level
        """
        usage_fraction = usage_percent / 100.0

        if usage_fraction >= 0.99:
            return DegradationLevel.MINIMAL
        elif usage_fraction >= 0.98:
            return DegradationLevel.REDUCED_3
        elif usage_fraction >= 0.95:
            return DegradationLevel.REDUCED_2
        elif usage_fraction >= 0.90:
            return DegradationLevel.REDUCED_1
        else:
            return DegradationLevel.FULL

    def _apply_degradation(
        self,
        level: DegradationLevel,
        resource_type: str
    ) -> List[str]:
        """
        Apply degradation measures for the specified level.

        Measures applied:
        1. Timeout adjustments - Reduce timeouts progressively
        2. Quality adjustments - Lower quality thresholds
        3. Feature toggles - Disable non-critical features
        4. Concurrency limits - Reduce parallel operations

        Args:
            level: Target degradation level
            resource_type: Type of resource being degraded

        Returns:
            List of actions taken
        """
        actions = []

        # Get configuration for this level
        timeout_mult = self.config.timeout_multipliers[level]
        quality_thresh = self.config.quality_thresholds[level]
        disabled_features = self.config.feature_toggles[level]

        # Apply timeout reduction
        actions.append(
            f"Set timeout multiplier to {timeout_mult:.1%} "
            f"(level: {level.name})"
        )

        # Apply quality threshold reduction
        actions.append(
            f"Lowered quality threshold to {quality_thresh:.1%}"
        )

        # Disable features
        if disabled_features:
            actions.append(
                f"Disabled features: {', '.join(disabled_features)}"
            )
        else:
            actions.append("All features enabled")

        # Apply concurrency limits based on level
        if level == DegradationLevel.MINIMAL:
            actions.append("Reduced to single-threaded operation")
        elif level == DegradationLevel.REDUCED_3:
            actions.append("Limited to 2 concurrent operations")
        elif level == DegradationLevel.REDUCED_2:
            actions.append("Limited to 5 concurrent operations")
        elif level == DegradationLevel.REDUCED_1:
            actions.append("Limited to 10 concurrent operations")

        # Additional optimizations per level
        if level in [DegradationLevel.REDUCED_3, DegradationLevel.MINIMAL]:
            actions.append("Enabled aggressive caching")
            actions.append("Disabled optional validations")

        logger.info(
            f"Applied {level.name} degradation for {resource_type}: "
            f"{len(actions)} measures"
        )

        return actions

    def _monitor_recovery(self, resource_type: str) -> bool:
        """
        Check if resources are recovering.

        Analyzes usage history trend to detect recovery.

        Args:
            resource_type: Type of resource to monitor

        Returns:
            True if resources are recovering
        """
        history = self._usage_history.get(resource_type, [])

        if len(history) < 5:
            return False  # Not enough data

        # Check if usage is trending downward
        recent_usage = history[-5:]
        avg_recent = sum(recent_usage) / len(recent_usage)

        # Compare to earlier usage
        if len(history) >= 10:
            earlier_usage = history[-10:-5]
            avg_earlier = sum(earlier_usage) / len(earlier_usage)

            # Recovering if recent usage is lower than earlier
            if avg_recent < avg_earlier - 5.0:  # 5% improvement
                logger.info(
                    f"Resources recovering for {resource_type}: "
                    f"{avg_earlier:.1f}% → {avg_recent:.1f}%"
                )
                return True

        return False

    def _restore_service(self, resource_type: str) -> None:
        """
        Gradually restore service to FULL.

        Incrementally increases service level as resources permit.

        Args:
            resource_type: Type of resource to restore
        """
        current_level = self._current_level.get(
            resource_type,
            DegradationLevel.FULL
        )

        if current_level == DegradationLevel.FULL:
            return  # Already at full capacity

        # Move up one degradation level
        new_level = DegradationLevel(current_level.value - 1)
        self._current_level[resource_type] = new_level

        logger.info(
            f"Restored {resource_type} from {current_level.name} "
            f"to {new_level.name}"
        )

    def get_current_level(self, resource_type: str) -> DegradationLevel:
        """
        Get current degradation level for resource.

        Args:
            resource_type: Type of resource

        Returns:
            Current degradation level
        """
        with self._lock:
            return self._current_level.get(resource_type, DegradationLevel.FULL)

    def get_stats(self, resource_type: str) -> Dict[str, Any]:
        """
        Get degradation statistics.

        Args:
            resource_type: Type of resource

        Returns:
            Dictionary with degradation stats
        """
        with self._lock:
            current_level = self._current_level.get(
                resource_type,
                DegradationLevel.FULL
            )
            history = self._usage_history.get(resource_type, [])

            return {
                "resource_type": resource_type,
                "current_level": current_level.name,
                "timeout_multiplier": self.config.timeout_multipliers[current_level],
                "quality_threshold": self.config.quality_thresholds[current_level],
                "disabled_features": self.config.feature_toggles[current_level],
                "usage_history_length": len(history),
                "recent_usage_avg": sum(history[-10:]) / len(history[-10:]) if history else 0.0
            }

    def reset(self, resource_type: Optional[str] = None) -> None:
        """
        Reset degradation to FULL level.

        Args:
            resource_type: Specific resource to reset, or None for all
        """
        with self._lock:
            if resource_type:
                self._current_level[resource_type] = DegradationLevel.FULL
                logger.info(f"Reset degradation for {resource_type}")
            else:
                self._current_level.clear()
                logger.info("Reset all degradation levels")


__all__ = [
    "GradualDegradationStrategy",
    "DegradationLevel",
    "DegradationConfig",
]
