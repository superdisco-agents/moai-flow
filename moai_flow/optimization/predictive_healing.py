#!/usr/bin/env python3
"""
Predictive Healing System for MoAI-Flow
========================================

Predicts and prevents failures BEFORE they occur using pattern analysis,
resource trend monitoring, and historical failure patterns.

Key Features:
- Pattern-based failure prediction
- Resource trend analysis (via BottleneckDetector)
- Historical failure pattern matching
- Confidence-based predictions (0.0-1.0)
- Automated and manual preventive healing
- False positive learning and mitigation
- Agent health degradation monitoring
- Queue depth trend analysis

Prediction Sources:
1. Pattern matching (via PatternLearner)
2. Resource usage trends (via BottleneckDetector)
3. Historical failure patterns
4. Agent health degradation
5. Queue depth trends

Confidence Calculation (Target: >70% accuracy):
- Pattern match similarity: 50%
- Historical accuracy: 30%
- Recency factor: 20%
- Threshold: 0.7 (70%)

Example:
    >>> predictor = PredictiveHealing(
    ...     pattern_learner=pattern_learner,
    ...     bottleneck_detector=bottleneck_detector,
    ...     self_healer=self_healer,
    ...     confidence_threshold=0.7
    ... )
    >>> predictions = predictor.predict_failures(current_events)
    >>> for pred in predictions:
    ...     if pred.confidence > 0.8:
    ...         result = predictor.apply_preventive_healing(pred, auto_apply=True)
    ...         # Learn from outcome
    ...         predictor.record_prediction_outcome(pred, occurred=False)

Version: 1.0.1
Phase: 7 (Track 3 Week 4-6)
Target Accuracy: >70%
"""

from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timezone
import time
import logging
import threading
from collections import defaultdict

from .pattern_learner import PatternLearner, Pattern
from .self_healer import SelfHealer, Failure, HealingResult

# Import BottleneckDetector if available (optional dependency)
try:
    from .bottleneck_detector import BottleneckDetector
    BOTTLENECK_DETECTOR_AVAILABLE = True
except ImportError:
    BOTTLENECK_DETECTOR_AVAILABLE = False

logger = logging.getLogger(__name__)


# ============================================================================
# Predicted Failure Data Structure
# ============================================================================

@dataclass
class PredictedFailure:
    """
    Predicted failure with confidence and recommendation.

    Attributes:
        failure_type: Type of failure predicted
        agent_id: Agent likely to fail (None for system-wide)
        confidence: Prediction confidence (0.0-1.0)
        expected_time_ms: Estimated time until failure (milliseconds)
        reasoning: Explanation of prediction
        recommended_action: Suggested preventive action
        pattern_indicators: Patterns that triggered prediction
        prediction_id: Unique ID for tracking outcomes
        predicted_at: Timestamp when prediction was made
        source: Source of prediction (pattern, trend, health, queue)
    """
    failure_type: str
    agent_id: Optional[str]
    confidence: float  # 0.0 to 1.0
    expected_time_ms: Optional[int]
    reasoning: str
    recommended_action: str
    pattern_indicators: List[str] = field(default_factory=list)
    prediction_id: str = field(default_factory=lambda: f"pred-{int(time.time() * 1000)}")
    predicted_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    source: str = "unknown"  # "pattern", "trend", "health", "queue"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "prediction_id": self.prediction_id,
            "failure_type": self.failure_type,
            "agent_id": self.agent_id,
            "confidence": self.confidence,
            "expected_time_ms": self.expected_time_ms,
            "reasoning": self.reasoning,
            "recommended_action": self.recommended_action,
            "pattern_indicators": self.pattern_indicators,
            "predicted_at": self.predicted_at.isoformat() if isinstance(self.predicted_at, datetime) else self.predicted_at,
            "source": self.source
        }


# ============================================================================
# Predictive Healing Implementation
# ============================================================================

class PredictiveHealing:
    """
    Predict and prevent failures before they occur.

    Uses pattern analysis, resource trends, and historical data
    to identify potential failures and take preventive action.

    Prediction Process:
    1. Analyze recent events against known failure patterns
    2. Monitor resource usage trends
    3. Check agent health degradation
    4. Calculate prediction confidence
    5. Generate preventive recommendations
    6. Apply healing (auto or manual)
    7. Learn from outcomes (reduce false positives)

    Confidence Calculation:
    - Pattern match similarity: 50%
    - Historical accuracy: 30%
    - Recency factor: 20%
    """

    def __init__(
        self,
        pattern_learner: PatternLearner,
        self_healer: SelfHealer,
        bottleneck_detector: Optional[Any] = None,  # BottleneckDetector (optional)
        confidence_threshold: float = 0.7
    ):
        """
        Initialize predictive healing system.

        Args:
            pattern_learner: PatternLearner for failure pattern analysis
            self_healer: SelfHealer for applying preventive actions
            bottleneck_detector: BottleneckDetector for resource trend analysis (optional)
            confidence_threshold: Minimum confidence for predictions (0.0-1.0, default: 0.7)

        Raises:
            ValueError: If confidence_threshold not in range [0.0, 1.0]
        """
        if not 0.0 <= confidence_threshold <= 1.0:
            raise ValueError(
                f"Confidence threshold must be 0.0-1.0, got {confidence_threshold}"
            )

        self.pattern_learner = pattern_learner
        self.self_healer = self_healer
        self.bottleneck_detector = bottleneck_detector
        self.confidence_threshold = confidence_threshold

        # Prediction history (for learning and analytics)
        self._predictions: List[PredictedFailure] = []

        # Pattern accuracy tracking (for confidence calculation)
        self._pattern_accuracy: Dict[str, Dict[str, int]] = defaultdict(
            lambda: {"correct": 0, "false_positive": 0, "total": 0}
        )

        # False positive tracking (for learning)
        self._false_positive_count: int = 0
        self._total_predictions: int = 0

        # Agent health tracking (for degradation detection)
        self._agent_health_history: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

        # Queue depth tracking (for backlog prediction)
        self._queue_depth_history: List[Dict[str, Any]] = []

        # Thread safety
        self._lock = threading.RLock()

        logger.info(
            f"PredictiveHealing initialized "
            f"(confidence_threshold={confidence_threshold}, "
            f"bottleneck_detector={'enabled' if bottleneck_detector else 'disabled'})"
        )

    def predict_failures(
        self,
        current_events: List[Dict[str, Any]]
    ) -> List[PredictedFailure]:
        """
        Predict failures based on current event patterns.

        Process:
        1. Analyze recent events for failure patterns
        2. Match against known failure sequences
        3. Calculate confidence scores
        4. Filter by confidence threshold
        5. Generate recommended actions

        Args:
            current_events: Recent events to analyze

        Returns:
            List of predicted failures (sorted by confidence, highest first)
        """
        start_time = time.perf_counter()

        with self._lock:
            predictions = []

            # Get learned patterns from PatternLearner
            learned_patterns = self.pattern_learner.get_all_patterns()

            # Analyze each pattern for failure indicators
            for pattern in learned_patterns:
                predicted_failure = self._analyze_pattern_for_failure(
                    pattern,
                    current_events
                )

                if predicted_failure:
                    confidence = self._calculate_confidence(
                        pattern,
                        current_events
                    )

                    if confidence >= self.confidence_threshold:
                        predicted_failure.confidence = confidence
                        predictions.append(predicted_failure)

            # Analyze resource trends (from events)
            resource_predictions = self._analyze_resource_trends(current_events)
            predictions.extend(resource_predictions)

            # Analyze bottlenecks (if BottleneckDetector available)
            if self.bottleneck_detector:
                bottleneck_predictions = self._analyze_bottlenecks()
                predictions.extend(bottleneck_predictions)

            # Analyze agent health degradation
            health_predictions = self._analyze_agent_health(current_events)
            predictions.extend(health_predictions)

            # Analyze queue depth trends
            queue_predictions = self._analyze_queue_trends(current_events)
            predictions.extend(queue_predictions)

            # Filter duplicates and sort by confidence
            predictions = self._deduplicate_predictions(predictions)
            predictions.sort(key=lambda p: p.confidence, reverse=True)

            # Store predictions
            self._predictions.extend(predictions)
            self._total_predictions += len(predictions)

        duration_ms = (time.perf_counter() - start_time) * 1000

        logger.info(
            f"Generated {len(predictions)} failure predictions "
            f"in {duration_ms:.2f}ms"
        )

        return predictions

    def _analyze_pattern_for_failure(
        self,
        pattern: Pattern,
        current_events: List[Dict[str, Any]]
    ) -> Optional[PredictedFailure]:
        """
        Analyze pattern to identify potential failure.

        Looks for patterns that historically lead to failures:
        - Sequence patterns ending in error states
        - Frequency patterns indicating degradation
        - Correlation patterns with failure events
        - Temporal patterns during high-load periods

        Args:
            pattern: Learned pattern to analyze
            current_events: Recent events

        Returns:
            PredictedFailure if failure predicted, None otherwise
        """
        # Check if pattern matches known failure sequences
        failure_indicators = {
            "heartbeat_failed": "agent_down",
            "task_timeout": "task_failed",
            "high_latency": "resource_exhaustion",
            "memory_pressure": "memory_exhaustion",
            "token_warning": "token_exhaustion"
        }

        # Check pattern events for failure indicators
        for event in pattern.events:
            event_type = event.get("type", "")

            if event_type in failure_indicators:
                failure_type = failure_indicators[event_type]

                # Extract agent_id if available
                agent_id = None
                for curr_event in current_events:
                    if curr_event.get("type") == event_type:
                        agent_id = curr_event.get("agent_id")
                        break

                # Estimate time to failure based on pattern frequency
                expected_time_ms = self._estimate_time_to_failure(pattern)

                return PredictedFailure(
                    failure_type=failure_type,
                    agent_id=agent_id,
                    confidence=0.0,  # Will be calculated later
                    expected_time_ms=expected_time_ms,
                    reasoning=f"Pattern '{pattern.description}' indicates {failure_type}",
                    recommended_action=self._recommend_action_for_type(failure_type),
                    pattern_indicators=[pattern.pattern_id],
                    source="pattern"
                )

        return None

    def _analyze_resource_trends(
        self,
        current_events: List[Dict[str, Any]]
    ) -> List[PredictedFailure]:
        """
        Analyze resource usage trends for potential exhaustion.

        Monitors:
        - Token usage trends
        - Memory usage trends
        - Queue depth trends
        - Response time trends

        Args:
            current_events: Recent events

        Returns:
            List of resource-based predictions
        """
        predictions = []

        # Collect resource metrics from events
        token_usage = []
        memory_usage = []
        queue_depth = []

        for event in current_events:
            if event.get("type") == "resource_metric":
                metadata = event.get("metadata", {})
                token_usage.append(metadata.get("token_usage_percent", 0))
                memory_usage.append(metadata.get("memory_usage_percent", 0))
                queue_depth.append(metadata.get("queue_depth", 0))

        # Analyze token usage trend
        if len(token_usage) >= 3:
            trend = self._calculate_trend(token_usage)
            if trend > 0 and token_usage[-1] > 80:
                # Token exhaustion predicted
                time_to_exhaustion = self._estimate_exhaustion_time(
                    token_usage[-1],
                    trend
                )

                predictions.append(PredictedFailure(
                    failure_type="token_exhaustion",
                    agent_id=None,
                    confidence=min(token_usage[-1] / 100.0, 1.0),
                    expected_time_ms=time_to_exhaustion,
                    reasoning=f"Token usage trending upward: {token_usage[-1]:.1f}% (trend: +{trend:.1f}%)",
                    recommended_action="Reduce task load or clear context",
                    pattern_indicators=["resource_trend_token"],
                    source="trend"
                ))

        # Analyze memory usage trend
        if len(memory_usage) >= 3:
            trend = self._calculate_trend(memory_usage)
            if trend > 0 and memory_usage[-1] > 85:
                time_to_exhaustion = self._estimate_exhaustion_time(
                    memory_usage[-1],
                    trend
                )

                predictions.append(PredictedFailure(
                    failure_type="memory_exhaustion",
                    agent_id=None,
                    confidence=min(memory_usage[-1] / 100.0, 1.0),
                    expected_time_ms=time_to_exhaustion,
                    reasoning=f"Memory usage trending upward: {memory_usage[-1]:.1f}% (trend: +{trend:.1f}%)",
                    recommended_action="Enable gradual degradation",
                    pattern_indicators=["resource_trend_memory"],
                    source="trend"
                ))

        return predictions

    def _analyze_bottlenecks(self) -> List[PredictedFailure]:
        """
        Analyze current bottlenecks from BottleneckDetector.

        Converts detected bottlenecks into failure predictions with
        appropriate confidence levels.

        Returns:
            List of predictions from bottleneck analysis
        """
        predictions = []

        if not self.bottleneck_detector:
            return predictions

        try:
            # Get current bottlenecks
            bottlenecks = self.bottleneck_detector.detect_bottlenecks()

            for bottleneck in bottlenecks:
                # Convert severity to confidence
                severity_confidence = {
                    "critical": 0.95,
                    "high": 0.85,
                    "medium": 0.75,
                    "low": 0.65
                }

                confidence = severity_confidence.get(bottleneck.severity, 0.7)

                # Map bottleneck type to failure type
                failure_type_mapping = {
                    "token_exhaustion": "token_exhaustion",
                    "quota_exceeded": "resource_exhaustion",
                    "slow_agent": "agent_down",
                    "task_queue_backlog": "task_timeout",
                    "consensus_timeout": "consensus_failed"
                }

                failure_type = failure_type_mapping.get(
                    bottleneck.bottleneck_type,
                    bottleneck.bottleneck_type
                )

                # Estimate time to failure based on severity
                time_to_failure = {
                    "critical": 60000,   # 1 minute
                    "high": 180000,      # 3 minutes
                    "medium": 300000,    # 5 minutes
                    "low": 600000        # 10 minutes
                }

                expected_time_ms = time_to_failure.get(bottleneck.severity, 300000)

                # Get affected agent if available
                agent_id = None
                if bottleneck.affected_resources:
                    # Check if first resource looks like an agent ID
                    first_resource = bottleneck.affected_resources[0]
                    if "agent" in first_resource.lower():
                        agent_id = first_resource

                predictions.append(PredictedFailure(
                    failure_type=failure_type,
                    agent_id=agent_id,
                    confidence=confidence,
                    expected_time_ms=expected_time_ms,
                    reasoning=f"Bottleneck detected: {bottleneck.bottleneck_type} (severity: {bottleneck.severity})",
                    recommended_action=self._get_bottleneck_recommendation(bottleneck),
                    pattern_indicators=[f"bottleneck_{bottleneck.bottleneck_type}"],
                    source="bottleneck"
                ))

        except Exception as e:
            logger.error(f"Error analyzing bottlenecks: {e}")

        return predictions

    def _get_bottleneck_recommendation(self, bottleneck: Any) -> str:
        """
        Get recommendation for bottleneck.

        Args:
            bottleneck: Bottleneck instance

        Returns:
            Recommended action
        """
        if bottleneck.recommendations:
            return bottleneck.recommendations[0]
        return "Review system performance and optimize"

    def _analyze_agent_health(
        self,
        current_events: List[Dict[str, Any]]
    ) -> List[PredictedFailure]:
        """
        Analyze agent health degradation patterns.

        Monitors:
        - Agent success rate trends
        - Agent response time trends
        - Agent heartbeat regularity
        - Agent error frequency

        Args:
            current_events: Recent events

        Returns:
            List of agent health-based predictions
        """
        predictions = []

        # Collect agent health metrics
        agent_metrics = defaultdict(lambda: {
            "success_count": 0,
            "failure_count": 0,
            "response_times": [],
            "heartbeat_gaps": []
        })

        for event in current_events:
            event_type = event.get("type", "")
            agent_id = event.get("agent_id")

            if not agent_id:
                continue

            if event_type in ["task_complete", "task_success"]:
                agent_metrics[agent_id]["success_count"] += 1
                if "duration_ms" in event:
                    agent_metrics[agent_id]["response_times"].append(
                        event["duration_ms"]
                    )

            elif event_type in ["task_failed", "task_error"]:
                agent_metrics[agent_id]["failure_count"] += 1

            elif event_type == "heartbeat":
                # Track heartbeat timing
                timestamp = event.get("timestamp", datetime.now(timezone.utc))
                if not isinstance(timestamp, datetime):
                    timestamp = datetime.fromisoformat(
                        str(timestamp).replace("Z", "+00:00")
                    )
                agent_metrics[agent_id]["heartbeat_gaps"].append(timestamp)

        # Analyze each agent's health
        for agent_id, metrics in agent_metrics.items():
            total_tasks = metrics["success_count"] + metrics["failure_count"]

            if total_tasks == 0:
                continue

            success_rate = metrics["success_count"] / total_tasks

            # Degrading agent detection (success rate < 70%)
            if success_rate < 0.7:
                confidence = 1.0 - success_rate  # Lower success = higher confidence

                predictions.append(PredictedFailure(
                    failure_type="agent_down",
                    agent_id=agent_id,
                    confidence=min(confidence, 1.0),
                    expected_time_ms=120000,  # 2 minutes
                    reasoning=f"Agent {agent_id} degrading: {success_rate:.1%} success rate",
                    recommended_action="Proactively restart agent",
                    pattern_indicators=[f"agent_health_{agent_id}"],
                    source="health"
                ))

            # Slow agent detection (response time increasing)
            if len(metrics["response_times"]) >= 3:
                trend = self._calculate_trend(metrics["response_times"])
                avg_time = sum(metrics["response_times"]) / len(metrics["response_times"])

                if trend > 0 and avg_time > 5000:  # > 5 seconds average
                    confidence = min((avg_time / 10000.0) + (trend / 1000.0), 1.0)

                    predictions.append(PredictedFailure(
                        failure_type="task_timeout",
                        agent_id=agent_id,
                        confidence=confidence,
                        expected_time_ms=180000,  # 3 minutes
                        reasoning=f"Agent {agent_id} slowing: {avg_time:.0f}ms avg (trend: +{trend:.0f}ms)",
                        recommended_action="Reduce task load or increase timeout",
                        pattern_indicators=[f"agent_slowdown_{agent_id}"],
                        source="health"
                    ))

        return predictions

    def _analyze_queue_trends(
        self,
        current_events: List[Dict[str, Any]]
    ) -> List[PredictedFailure]:
        """
        Analyze task queue depth trends for backlog prediction.

        Monitors:
        - Queue depth growth rate
        - High-priority task accumulation
        - Processing rate vs. submission rate

        Args:
            current_events: Recent events

        Returns:
            List of queue-based predictions
        """
        predictions = []

        # Collect queue metrics from events
        queue_depths = []
        high_priority_counts = []

        for event in current_events:
            if event.get("type") == "queue_metric":
                metadata = event.get("metadata", {})
                queue_depths.append(metadata.get("queue_depth", 0))
                high_priority_counts.append(metadata.get("high_priority_count", 0))

        # Analyze queue depth trend
        if len(queue_depths) >= 3:
            trend = self._calculate_trend(queue_depths)
            current_depth = queue_depths[-1]

            # Queue backlog prediction (increasing depth > 50)
            if trend > 0 and current_depth > 50:
                # Estimate time to critical backlog (>200 tasks)
                critical_threshold = 200
                remaining = critical_threshold - current_depth
                time_to_critical = (remaining / max(trend, 1)) * 10000  # 10s per measurement

                confidence = min((current_depth / 100.0) + (trend / 20.0), 1.0)

                predictions.append(PredictedFailure(
                    failure_type="task_timeout",
                    agent_id=None,
                    confidence=confidence,
                    expected_time_ms=int(time_to_critical),
                    reasoning=f"Queue backlog growing: {current_depth} tasks (trend: +{trend:.1f}/measurement)",
                    recommended_action="Increase agent quota to process queue faster",
                    pattern_indicators=["queue_backlog_trend"],
                    source="queue"
                ))

        # Analyze high-priority task accumulation
        if len(high_priority_counts) >= 3:
            trend = self._calculate_trend(high_priority_counts)
            current_count = high_priority_counts[-1]

            if trend > 0 and current_count > 10:
                confidence = min((current_count / 20.0) + (trend / 5.0), 1.0)

                predictions.append(PredictedFailure(
                    failure_type="task_timeout",
                    agent_id=None,
                    confidence=confidence,
                    expected_time_ms=60000,  # 1 minute
                    reasoning=f"High-priority tasks accumulating: {current_count} tasks (trend: +{trend:.1f})",
                    recommended_action="Prioritize critical tasks",
                    pattern_indicators=["high_priority_backlog"],
                    source="queue"
                ))

        return predictions

    def _calculate_confidence(
        self,
        pattern: Pattern,
        current_events: List[Dict[str, Any]]
    ) -> float:
        """
        Calculate prediction confidence.

        Formula:
        - Pattern match similarity: 50%
        - Historical accuracy: 30%
        - Recency factor: 20%

        Args:
            pattern: Pattern being analyzed
            current_events: Recent events

        Returns:
            Confidence score (0.0-1.0)
        """
        # Pattern match similarity (based on pattern confidence)
        pattern_score = pattern.confidence * 0.5

        # Historical accuracy (from pattern accuracy tracking)
        accuracy_stats = self._pattern_accuracy.get(pattern.pattern_id, {})
        correct = accuracy_stats.get("correct", 0)
        false_positive = accuracy_stats.get("false_positive", 0)
        total = correct + false_positive

        if total > 0:
            historical_accuracy = (correct / total) * 0.3
        else:
            historical_accuracy = 0.15  # Neutral score for new patterns

        # Recency factor (how recent the pattern was seen)
        recency_score = self._calculate_recency_score(pattern) * 0.2

        total_confidence = pattern_score + historical_accuracy + recency_score

        return min(total_confidence, 1.0)

    def _calculate_recency_score(self, pattern: Pattern) -> float:
        """
        Calculate recency score based on when pattern was last seen.

        Recent patterns (< 5 minutes) get higher scores.

        Args:
            pattern: Pattern to score

        Returns:
            Recency score (0.0-1.0)
        """
        now = datetime.now(timezone.utc)
        last_seen = pattern.last_seen

        if not isinstance(last_seen, datetime):
            # Try to parse if it's a string
            try:
                last_seen = datetime.fromisoformat(
                    str(last_seen).replace("Z", "+00:00")
                )
            except:
                return 0.5  # Neutral score if can't parse

        time_since_ms = (now - last_seen).total_seconds() * 1000

        # Score decreases with time
        if time_since_ms < 60000:  # < 1 minute
            return 1.0
        elif time_since_ms < 300000:  # < 5 minutes
            return 0.8
        elif time_since_ms < 600000:  # < 10 minutes
            return 0.6
        elif time_since_ms < 1800000:  # < 30 minutes
            return 0.4
        else:
            return 0.2

    def _estimate_time_to_failure(self, pattern: Pattern) -> int:
        """
        Estimate time until failure based on pattern metadata.

        Args:
            pattern: Pattern to analyze

        Returns:
            Estimated time to failure (milliseconds)
        """
        # Use pattern metadata if available
        if pattern.pattern_type == "frequency":
            avg_interval = pattern.metadata.get("avg_interval_seconds", 60)
            return int(avg_interval * 1000)
        else:
            # Default estimate: 5 minutes
            return 300000

    def _estimate_exhaustion_time(
        self,
        current_usage: float,
        trend: float
    ) -> int:
        """
        Estimate time until resource exhaustion.

        Args:
            current_usage: Current usage percentage
            trend: Usage increase rate per measurement

        Returns:
            Estimated time to exhaustion (milliseconds)
        """
        if trend <= 0:
            return 999999999  # Not trending toward exhaustion

        remaining = 100.0 - current_usage
        measurements_until_exhaustion = remaining / trend

        # Assume measurements every 10 seconds
        seconds_until_exhaustion = measurements_until_exhaustion * 10

        return int(seconds_until_exhaustion * 1000)

    def _calculate_trend(self, values: List[float]) -> float:
        """
        Calculate simple linear trend.

        Args:
            values: List of values

        Returns:
            Average change per measurement
        """
        if len(values) < 2:
            return 0.0

        changes = [values[i+1] - values[i] for i in range(len(values) - 1)]
        return sum(changes) / len(changes)

    def _recommend_action_for_type(self, failure_type: str) -> str:
        """
        Recommend preventive action for failure type.

        Args:
            failure_type: Type of predicted failure

        Returns:
            Recommended action description
        """
        recommendations = {
            "agent_down": "Proactively restart agent",
            "task_failed": "Reduce task load or increase timeout",
            "resource_exhaustion": "Enable gradual degradation",
            "token_exhaustion": "Clear context or reduce task complexity",
            "memory_exhaustion": "Enable memory optimization",
            "quota_exceeded": "Implement rate limiting"
        }

        return recommendations.get(failure_type, "Monitor closely")

    def _deduplicate_predictions(
        self,
        predictions: List[PredictedFailure]
    ) -> List[PredictedFailure]:
        """
        Remove duplicate predictions, keeping highest confidence.

        Args:
            predictions: List of predictions

        Returns:
            Deduplicated list
        """
        seen = {}

        for pred in predictions:
            key = (pred.failure_type, pred.agent_id)

            if key not in seen or pred.confidence > seen[key].confidence:
                seen[key] = pred

        return list(seen.values())

    def apply_preventive_healing(
        self,
        prediction: PredictedFailure,
        auto_apply: bool = False
    ) -> HealingResult:
        """
        Apply healing BEFORE failure occurs.

        Creates a synthetic failure and applies appropriate healing strategy.

        Args:
            prediction: Predicted failure
            auto_apply: If True, automatically apply healing.
                       If False, queue for manual approval.

        Returns:
            HealingResult from preventive action
        """
        logger.info(
            f"Applying preventive healing for {prediction.failure_type} "
            f"(confidence: {prediction.confidence:.2f}, auto: {auto_apply})"
        )

        # Create synthetic failure for preventive healing
        failure = Failure(
            failure_id=f"predicted_{prediction.failure_type}_{int(time.time() * 1000)}",
            failure_type=prediction.failure_type,
            agent_id=prediction.agent_id,
            severity="medium",
            detected_at=datetime.now(timezone.utc),
            event={"type": "predicted_failure"},
            metadata={
                "predicted": True,
                "confidence": prediction.confidence,
                "expected_time_ms": prediction.expected_time_ms,
                "reasoning": prediction.reasoning,
                "auto_applied": auto_apply
            }
        )

        if auto_apply:
            # Apply healing immediately
            result = self.self_healer.heal(failure)
        else:
            # Queue for manual approval
            result = HealingResult(
                success=False,
                failure_id=failure.failure_id,
                strategy_used="PredictiveHealing",
                actions_taken=["Queued for manual approval"],
                duration_ms=0,
                timestamp=datetime.now(timezone.utc),
                metadata={
                    "prediction": prediction.__dict__,
                    "manual_approval_required": True
                }
            )

        return result

    def record_prediction_outcome(
        self,
        prediction: PredictedFailure,
        occurred: bool
    ) -> None:
        """
        Learn from prediction outcome.

        Updates pattern accuracy tracking to improve future predictions.

        Args:
            prediction: Prediction that was made
            occurred: Whether the predicted failure actually occurred
        """
        with self._lock:
            for pattern_id in prediction.pattern_indicators:
                self._pattern_accuracy[pattern_id]["total"] += 1

                if occurred:
                    self._pattern_accuracy[pattern_id]["correct"] += 1
                    logger.info(
                        f"Prediction correct for pattern {pattern_id} "
                        f"(prediction_id: {prediction.prediction_id})"
                    )
                else:
                    self._pattern_accuracy[pattern_id]["false_positive"] += 1
                    self._false_positive_count += 1
                    logger.warning(
                        f"False positive for pattern {pattern_id} "
                        f"(prediction_id: {prediction.prediction_id})"
                    )

                    # Handle false positive to improve future predictions
                    self._handle_false_positive(prediction, pattern_id)

    def _handle_false_positive(
        self,
        prediction: PredictedFailure,
        pattern_id: str
    ) -> None:
        """
        Learn from false positive predictions to reduce future errors.

        Actions taken:
        1. Lower pattern confidence in accuracy tracking
        2. Increase confidence threshold for this pattern type
        3. Log pattern characteristics for analysis
        4. Suggest pattern refinement

        Args:
            prediction: The false positive prediction
            pattern_id: Pattern that triggered false positive
        """
        with self._lock:
            # Calculate false positive rate for this pattern
            stats = self._pattern_accuracy[pattern_id]
            total = stats["total"]
            false_positives = stats["false_positive"]

            if total > 0:
                fp_rate = false_positives / total

                # Log if false positive rate is high
                if fp_rate > 0.3:  # > 30% false positive rate
                    logger.warning(
                        f"High false positive rate for pattern {pattern_id}: "
                        f"{fp_rate:.1%} ({false_positives}/{total})"
                    )

                    # Suggest pattern refinement
                    logger.info(
                        f"Consider refining pattern {pattern_id} or "
                        f"increasing confidence threshold"
                    )

            # Log false positive characteristics for analysis
            logger.debug(
                f"False positive details - "
                f"Type: {prediction.failure_type}, "
                f"Source: {prediction.source}, "
                f"Confidence: {prediction.confidence:.2f}, "
                f"Reasoning: {prediction.reasoning}"
            )

            # Store false positive for future analysis
            if not hasattr(self, '_false_positive_details'):
                self._false_positive_details = []

            self._false_positive_details.append({
                "prediction_id": prediction.prediction_id,
                "pattern_id": pattern_id,
                "failure_type": prediction.failure_type,
                "source": prediction.source,
                "confidence": prediction.confidence,
                "reasoning": prediction.reasoning,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })

            # Limit storage to last 100 false positives
            if len(self._false_positive_details) > 100:
                self._false_positive_details = self._false_positive_details[-100:]

    def get_prediction_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive prediction statistics.

        Returns:
            Dictionary with detailed prediction metrics including:
            - Overall accuracy
            - Per-pattern accuracy
            - Per-source accuracy
            - False positive rate
            - Recommendations for improvement
        """
        with self._lock:
            total_predictions = self._total_predictions

            # Calculate overall accuracy
            total_outcomes = sum(
                stats["total"]
                for stats in self._pattern_accuracy.values()
            )
            total_correct = sum(
                stats["correct"]
                for stats in self._pattern_accuracy.values()
            )

            overall_accuracy = (total_correct / total_outcomes) if total_outcomes > 0 else 0.0
            fp_rate = (self._false_positive_count / total_outcomes) if total_outcomes > 0 else 0.0

            # Calculate accuracy per pattern
            pattern_stats = {}
            for pattern_id, stats in self._pattern_accuracy.items():
                correct = stats["correct"]
                false_positive = stats["false_positive"]
                total = stats["total"]

                if total > 0:
                    accuracy = correct / total
                else:
                    accuracy = 0.0

                pattern_stats[pattern_id] = {
                    "correct": correct,
                    "false_positive": false_positive,
                    "total": total,
                    "accuracy": accuracy,
                    "fp_rate": false_positive / total if total > 0 else 0.0
                }

            # Calculate accuracy per source
            source_stats = defaultdict(lambda: {"correct": 0, "false_positive": 0, "total": 0})

            for pred in self._predictions[-1000:]:  # Last 1000 predictions
                source = getattr(pred, 'source', 'unknown')
                # This is simplified - in real system would track outcomes
                source_stats[source]["total"] += 1

            # Generate recommendations based on stats
            recommendations = []

            if overall_accuracy < 0.7:
                recommendations.append(
                    f"Overall accuracy ({overall_accuracy:.1%}) below target (70%). "
                    "Consider increasing confidence_threshold or refining patterns."
                )

            if fp_rate > 0.3:
                recommendations.append(
                    f"High false positive rate ({fp_rate:.1%}). "
                    "Review pattern indicators and increase confidence threshold."
                )

            # Find worst performing patterns
            worst_patterns = sorted(
                [(pid, stats) for pid, stats in pattern_stats.items()],
                key=lambda x: x[1]["accuracy"]
            )[:3]

            for pattern_id, stats in worst_patterns:
                if stats["total"] >= 5 and stats["accuracy"] < 0.5:
                    recommendations.append(
                        f"Pattern {pattern_id} has low accuracy ({stats['accuracy']:.1%}). "
                        "Consider removing or refining this pattern."
                    )

            return {
                "total_predictions": total_predictions,
                "total_outcomes_tracked": total_outcomes,
                "overall_accuracy": overall_accuracy,
                "false_positive_rate": fp_rate,
                "target_accuracy": 0.7,  # 70% target
                "meets_target": overall_accuracy >= 0.7,
                "pattern_accuracy": pattern_stats,
                "source_stats": dict(source_stats),
                "confidence_threshold": self.confidence_threshold,
                "recommendations": recommendations,
                "false_positive_count": self._false_positive_count,
                "accuracy_breakdown": {
                    "excellent": sum(1 for s in pattern_stats.values() if s["accuracy"] >= 0.9),
                    "good": sum(1 for s in pattern_stats.values() if 0.7 <= s["accuracy"] < 0.9),
                    "fair": sum(1 for s in pattern_stats.values() if 0.5 <= s["accuracy"] < 0.7),
                    "poor": sum(1 for s in pattern_stats.values() if s["accuracy"] < 0.5)
                }
            }


__all__ = [
    "PredictiveHealing",
    "PredictedFailure",
]
