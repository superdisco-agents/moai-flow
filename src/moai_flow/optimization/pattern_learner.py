#!/usr/bin/env python3
"""
PatternLearner - Phase 6C Adaptive Optimization for MoAI-Flow

Statistical pattern learning system for swarm coordination optimization.
Analyzes event history to identify recurring patterns without ML libraries.

Pattern Types:
- Sequence patterns: Repeated event sequences (n-gram analysis)
- Frequency patterns: Regular time-based occurrences
- Correlation patterns: Events that co-occur frequently
- Temporal patterns: Time-window based patterns

Features:
- Pure statistical methods (NO ML libraries)
- Thread-safe learning operations
- <500ms learning for 1000 events
- Memory-efficient streaming analysis
- Configurable confidence thresholds

Version: 1.0.0
Phase: 6C (Weeks 5-6) - Adaptive Optimization
"""

import logging
import time
from collections import defaultdict, Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from threading import Lock
from typing import Any, Dict, List, Optional, Tuple, Set
from statistics import mean, median, stdev


# ============================================================================
# Pattern Data Structures
# ============================================================================

@dataclass
class Pattern:
    """
    Learned pattern with statistical confidence.

    Represents a discovered pattern in event history with metrics
    for confidence, frequency, and metadata.
    """
    pattern_id: str
    pattern_type: str  # "sequence", "frequency", "correlation", "temporal"
    description: str
    events: List[Dict[str, Any]]
    confidence: float  # 0.0 to 1.0
    occurrences: int
    first_seen: datetime
    last_seen: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert pattern to dictionary"""
        return {
            "pattern_id": self.pattern_id,
            "pattern_type": self.pattern_type,
            "description": self.description,
            "events": self.events,
            "confidence": self.confidence,
            "occurrences": self.occurrences,
            "first_seen": self.first_seen.isoformat() if isinstance(self.first_seen, datetime) else self.first_seen,
            "last_seen": self.last_seen.isoformat() if isinstance(self.last_seen, datetime) else self.last_seen,
            "metadata": self.metadata
        }


# ============================================================================
# PatternLearner Implementation
# ============================================================================

class PatternLearner:
    """
    Statistical pattern learning for swarm coordination optimization.

    Analyzes event history to discover recurring patterns using
    pure statistical methods (no ML libraries required).

    Supports four pattern types:
    1. Sequence patterns: Repeated event sequences (n-gram analysis)
    2. Frequency patterns: Events occurring at regular intervals
    3. Correlation patterns: Events that frequently co-occur
    4. Temporal patterns: Time-window based patterns

    Features:
    - Thread-safe learning operations
    - Configurable confidence thresholds
    - Memory-efficient streaming analysis
    - <500ms learning for 1000 events

    Example:
        >>> learner = PatternLearner(min_occurrences=5, confidence_threshold=0.7)
        >>> learner.record_event({
        ...     "type": "task_complete",
        ...     "timestamp": datetime.now(timezone.utc),
        ...     "agent_id": "agent-001"
        ... })
        >>> patterns = learner.learn_patterns()
        >>> for pattern in patterns:
        ...     print(f"{pattern.pattern_type}: {pattern.description} ({pattern.confidence:.2f})")
    """

    def __init__(
        self,
        min_occurrences: int = 5,
        confidence_threshold: float = 0.7,
        max_history_size: int = 10000
    ):
        """
        Initialize pattern learner with statistical learning configuration.

        Args:
            min_occurrences: Minimum pattern occurrences to consider valid (default: 5)
            confidence_threshold: Minimum confidence for pattern recognition 0.0-1.0 (default: 0.7)
            max_history_size: Maximum event history size for memory efficiency (default: 10000)

        Raises:
            ValueError: If confidence_threshold not in range [0.0, 1.0]
        """
        if not 0.0 <= confidence_threshold <= 1.0:
            raise ValueError(
                f"Confidence threshold must be between 0.0 and 1.0, got {confidence_threshold}"
            )

        self._min_occurrences = min_occurrences
        self._confidence_threshold = confidence_threshold
        self._max_history_size = max_history_size

        # Event storage
        self._event_history: List[Dict[str, Any]] = []

        # Learned patterns
        self._patterns: Dict[str, Pattern] = {}

        # Thread safety
        self._lock = Lock()

        # Logging
        self.logger = logging.getLogger(__name__)

        self.logger.info(
            f"PatternLearner initialized (min_occurrences={min_occurrences}, "
            f"confidence_threshold={confidence_threshold}, "
            f"max_history={max_history_size})"
        )

    def record_event(self, event: Dict[str, Any]) -> None:
        """
        Record event for pattern learning.

        Adds event to history for pattern analysis. Automatically manages
        memory by removing oldest events when max_history_size is reached.

        Args:
            event: Event data with required keys:
                - "type": str (event type identifier)
                - "timestamp": datetime (event timestamp)
                Optional keys:
                - "agent_id": str
                - "metadata": Dict[str, Any]

        Raises:
            ValueError: If event missing required keys

        Example:
            >>> learner.record_event({
            ...     "type": "task_start",
            ...     "timestamp": datetime.now(timezone.utc),
            ...     "agent_id": "agent-001",
            ...     "metadata": {"task_id": "task-001"}
            ... })
        """
        # Validate required keys
        if "type" not in event:
            raise ValueError("Event must have 'type' key")
        if "timestamp" not in event:
            raise ValueError("Event must have 'timestamp' key")

        with self._lock:
            self._event_history.append(event)

            # Memory management: remove oldest events if exceeded limit
            if len(self._event_history) > self._max_history_size:
                # Remove oldest 10% to avoid frequent resizing
                remove_count = self._max_history_size // 10
                self._event_history = self._event_history[remove_count:]
                self.logger.debug(
                    f"Trimmed event history: removed {remove_count} oldest events"
                )

    def learn_patterns(self) -> List[Pattern]:
        """
        Analyze event history and extract patterns.

        Performs comprehensive pattern analysis using all four pattern types:
        - Sequence patterns (n-gram analysis)
        - Frequency patterns (time-series analysis)
        - Correlation patterns (co-occurrence analysis)
        - Temporal patterns (time-window analysis)

        Returns:
            List of discovered patterns sorted by confidence (highest first)

        Performance:
            - Target: <500ms for 1000 events
            - Memory: O(n) where n = event_history size

        Example:
            >>> patterns = learner.learn_patterns()
            >>> high_confidence = [p for p in patterns if p.confidence > 0.8]
            >>> print(f"Found {len(high_confidence)} high-confidence patterns")
        """
        start_time = time.perf_counter()

        with self._lock:
            if len(self._event_history) < self._min_occurrences:
                self.logger.debug(
                    f"Insufficient events for pattern learning: "
                    f"{len(self._event_history)} < {self._min_occurrences}"
                )
                return []

            # Learn all pattern types
            patterns: List[Pattern] = []

            # 1. Sequence patterns (n-gram analysis)
            patterns.extend(self._learn_sequence_patterns())

            # 2. Frequency patterns (time-series)
            patterns.extend(self._learn_frequency_patterns())

            # 3. Correlation patterns (co-occurrence)
            patterns.extend(self._learn_correlation_patterns())

            # 4. Temporal patterns (time-windows)
            patterns.extend(self._learn_temporal_patterns())

            # Filter by confidence threshold
            patterns = [
                p for p in patterns
                if p.confidence >= self._confidence_threshold
            ]

            # Sort by confidence (highest first)
            patterns.sort(key=lambda p: p.confidence, reverse=True)

            # Store in patterns registry
            for pattern in patterns:
                self._patterns[pattern.pattern_id] = pattern

        duration_ms = (time.perf_counter() - start_time) * 1000

        self.logger.info(
            f"Pattern learning complete: {len(patterns)} patterns discovered "
            f"in {duration_ms:.2f}ms (events: {len(self._event_history)})"
        )

        return patterns

    def get_pattern(self, pattern_id: str) -> Optional[Pattern]:
        """
        Get specific learned pattern by ID.

        Args:
            pattern_id: Unique pattern identifier

        Returns:
            Pattern object or None if not found

        Example:
            >>> pattern = learner.get_pattern("seq_task_workflow_001")
            >>> if pattern:
            ...     print(f"Confidence: {pattern.confidence:.2f}")
        """
        with self._lock:
            return self._patterns.get(pattern_id)

    def get_all_patterns(self) -> List[Pattern]:
        """
        Get all learned patterns above confidence threshold.

        Returns:
            List of patterns sorted by confidence (highest first)

        Example:
            >>> all_patterns = learner.get_all_patterns()
            >>> for p in all_patterns[:5]:  # Top 5 patterns
            ...     print(f"{p.pattern_type}: {p.description}")
        """
        with self._lock:
            patterns = list(self._patterns.values())
            patterns.sort(key=lambda p: p.confidence, reverse=True)
            return patterns

    # ========================================================================
    # Sequence Pattern Learning (N-gram Analysis)
    # ========================================================================

    def _learn_sequence_patterns(self) -> List[Pattern]:
        """
        Detect event sequences that repeat.

        Uses n-gram analysis (bigrams and trigrams) to identify
        recurring event sequences in the history.

        Algorithm:
        1. Extract n-grams (sequences of n consecutive event types)
        2. Count occurrences of each n-gram
        3. Filter by min_occurrences threshold
        4. Calculate confidence based on frequency

        Example pattern:
            [agent_start, task_execute, task_complete] repeated 10 times
            → Pattern: "standard_task_workflow"

        Returns:
            List of sequence patterns
        """
        patterns: List[Pattern] = []

        # Extract bigrams (2-event sequences) and trigrams (3-event sequences)
        for n in [2, 3]:
            ngrams = self._extract_ngrams(n)

            for ngram, count in ngrams.items():
                if count < self._min_occurrences:
                    continue

                # Calculate confidence (normalized frequency)
                total_possible = len(self._event_history) - n + 1
                confidence = min(count / max(total_possible, 1), 1.0)

                # Additional confidence boost for consistency
                consistency_score = self._calculate_consistency_score(ngram)
                confidence = (confidence * 0.7) + (consistency_score * 0.3)

                # Create pattern
                pattern_id = f"seq_{hash(ngram)}_{n}"
                description = f"Sequence: {' → '.join(ngram)} (occurs {count} times)"

                # Find first and last occurrence timestamps
                first_seen, last_seen = self._find_ngram_timestamps(ngram)

                # Reconstruct event objects
                events = [{"type": event_type} for event_type in ngram]

                pattern = Pattern(
                    pattern_id=pattern_id,
                    pattern_type="sequence",
                    description=description,
                    events=events,
                    confidence=confidence,
                    occurrences=count,
                    first_seen=first_seen,
                    last_seen=last_seen,
                    metadata={"ngram_size": n, "sequence": list(ngram)}
                )

                patterns.append(pattern)

        return patterns

    def _extract_ngrams(self, n: int) -> Dict[Tuple[str, ...], int]:
        """
        Extract n-grams from event sequence for sequence pattern detection.

        Args:
            n: Size of n-gram (2 for bigram, 3 for trigram)

        Returns:
            Dictionary mapping n-gram tuple to occurrence count
        """
        ngrams: Dict[Tuple[str, ...], int] = defaultdict(int)

        for i in range(len(self._event_history) - n + 1):
            ngram = tuple(
                event["type"]
                for event in self._event_history[i:i+n]
            )
            ngrams[ngram] += 1

        return ngrams

    def _calculate_consistency_score(self, ngram: Tuple[str, ...]) -> float:
        """
        Calculate consistency score for n-gram pattern.

        Higher score if n-gram occurs at regular intervals.

        Args:
            ngram: N-gram tuple of event types

        Returns:
            Consistency score between 0.0 and 1.0
        """
        # Find all occurrence indices
        occurrence_indices = []
        for i in range(len(self._event_history) - len(ngram) + 1):
            current_ngram = tuple(
                event["type"]
                for event in self._event_history[i:i+len(ngram)]
            )
            if current_ngram == ngram:
                occurrence_indices.append(i)

        if len(occurrence_indices) < 2:
            return 0.5  # Neutral score for single occurrence

        # Calculate interval consistency
        intervals = [
            occurrence_indices[i+1] - occurrence_indices[i]
            for i in range(len(occurrence_indices) - 1)
        ]

        # Low standard deviation = high consistency
        if len(intervals) > 1:
            avg_interval = mean(intervals)
            std_interval = stdev(intervals)
            # Normalize: high std = low consistency
            consistency = max(0.0, 1.0 - (std_interval / max(avg_interval, 1)))
        else:
            consistency = 0.5

        return consistency

    def _find_ngram_timestamps(
        self,
        ngram: Tuple[str, ...]
    ) -> Tuple[datetime, datetime]:
        """
        Find first and last occurrence timestamps for n-gram.

        Args:
            ngram: N-gram tuple of event types

        Returns:
            Tuple of (first_seen, last_seen) timestamps
        """
        first_seen = None
        last_seen = None

        for i in range(len(self._event_history) - len(ngram) + 1):
            current_ngram = tuple(
                event["type"]
                for event in self._event_history[i:i+len(ngram)]
            )
            if current_ngram == ngram:
                timestamp = self._event_history[i]["timestamp"]
                if first_seen is None:
                    first_seen = timestamp
                last_seen = timestamp

        # Default to now if not found
        now = datetime.now(timezone.utc)
        return (first_seen or now, last_seen or now)

    # ========================================================================
    # Frequency Pattern Learning (Time-Series Analysis)
    # ========================================================================

    def _learn_frequency_patterns(self) -> List[Pattern]:
        """
        Detect events that occur at regular intervals.

        Algorithm:
        1. Group events by type
        2. Calculate time intervals between consecutive occurrences
        3. Identify regular intervals (low variance)
        4. Create patterns for regular occurrences

        Example pattern:
            heartbeat_fail every ~5 seconds
            → Pattern: "heartbeat_degradation"

        Returns:
            List of frequency patterns
        """
        patterns: List[Pattern] = []

        # Group events by type
        events_by_type: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        for event in self._event_history:
            events_by_type[event["type"]].append(event)

        # Analyze each event type for regular intervals
        for event_type, events in events_by_type.items():
            if len(events) < self._min_occurrences:
                continue

            # Calculate time intervals between consecutive events
            intervals = []
            for i in range(len(events) - 1):
                t1 = events[i]["timestamp"]
                t2 = events[i+1]["timestamp"]

                # Convert to comparable datetime objects
                if not isinstance(t1, datetime):
                    t1 = datetime.fromisoformat(str(t1).replace("Z", "+00:00"))
                if not isinstance(t2, datetime):
                    t2 = datetime.fromisoformat(str(t2).replace("Z", "+00:00"))

                interval_seconds = (t2 - t1).total_seconds()
                intervals.append(interval_seconds)

            if not intervals:
                continue

            # Check for regularity (low variance)
            avg_interval = mean(intervals)

            if len(intervals) > 1:
                std_interval = stdev(intervals)
                regularity = max(0.0, 1.0 - (std_interval / max(avg_interval, 1)))
            else:
                regularity = 0.5

            # Only create pattern if sufficiently regular
            if regularity >= 0.6:  # 60% regularity threshold
                confidence = regularity

                pattern_id = f"freq_{event_type}_{int(avg_interval)}"
                description = (
                    f"Frequency: {event_type} occurs every ~{avg_interval:.1f}s "
                    f"(regularity: {regularity:.2f})"
                )

                first_seen = events[0]["timestamp"]
                last_seen = events[-1]["timestamp"]

                pattern = Pattern(
                    pattern_id=pattern_id,
                    pattern_type="frequency",
                    description=description,
                    events=[{"type": event_type}],
                    confidence=confidence,
                    occurrences=len(events),
                    first_seen=first_seen,
                    last_seen=last_seen,
                    metadata={
                        "avg_interval_seconds": avg_interval,
                        "regularity_score": regularity
                    }
                )

                patterns.append(pattern)

        return patterns

    # ========================================================================
    # Correlation Pattern Learning (Co-occurrence Analysis)
    # ========================================================================

    def _learn_correlation_patterns(self) -> List[Pattern]:
        """
        Detect events that correlate (occur together).

        Algorithm:
        1. Define time window for co-occurrence (e.g., 10 seconds)
        2. Count co-occurrences of event pairs within window
        3. Calculate correlation strength
        4. Create patterns for strong correlations

        Example pattern:
            high_token_usage + slow_response
            → Pattern: "resource_bottleneck"

        Returns:
            List of correlation patterns
        """
        patterns: List[Pattern] = []

        # Time window for co-occurrence (seconds)
        time_window = 10.0

        # Count co-occurrences
        cooccurrences: Dict[Tuple[str, str], int] = defaultdict(int)
        event_counts: Dict[str, int] = defaultdict(int)

        for i, event1 in enumerate(self._event_history):
            event_type1 = event1["type"]
            event_counts[event_type1] += 1

            t1 = event1["timestamp"]
            if not isinstance(t1, datetime):
                t1 = datetime.fromisoformat(str(t1).replace("Z", "+00:00"))

            # Look ahead within time window
            for event2 in self._event_history[i+1:]:
                t2 = event2["timestamp"]
                if not isinstance(t2, datetime):
                    t2 = datetime.fromisoformat(str(t2).replace("Z", "+00:00"))

                time_diff = (t2 - t1).total_seconds()

                if time_diff > time_window:
                    break  # Outside window

                event_type2 = event2["type"]

                # Store pair in sorted order to avoid duplicates
                pair = tuple(sorted([event_type1, event_type2]))
                cooccurrences[pair] += 1

        # Analyze co-occurrences
        total_events = len(self._event_history)

        for (type1, type2), cooccur_count in cooccurrences.items():
            if cooccur_count < self._min_occurrences:
                continue

            # Calculate correlation confidence
            # P(A and B) / (P(A) * P(B))
            p_a = event_counts[type1] / total_events
            p_b = event_counts[type2] / total_events
            p_ab = cooccur_count / total_events

            expected_cooccurrence = p_a * p_b * total_events

            if expected_cooccurrence > 0:
                correlation_strength = min(cooccur_count / expected_cooccurrence, 1.0)
            else:
                correlation_strength = 0.0

            # Only create pattern if correlation is strong
            if correlation_strength >= 1.5:  # 1.5x more than expected
                confidence = min(correlation_strength / 3.0, 1.0)  # Normalize

                pattern_id = f"corr_{hash((type1, type2))}"
                description = (
                    f"Correlation: {type1} + {type2} "
                    f"(co-occur {cooccur_count} times, strength: {correlation_strength:.2f})"
                )

                # Find first and last co-occurrence
                first_seen = datetime.now(timezone.utc)
                last_seen = datetime.now(timezone.utc)

                for i, event1 in enumerate(self._event_history):
                    if event1["type"] != type1:
                        continue

                    t1 = event1["timestamp"]
                    if not isinstance(t1, datetime):
                        t1 = datetime.fromisoformat(str(t1).replace("Z", "+00:00"))

                    # Check if type2 occurs within window
                    for event2 in self._event_history[i+1:]:
                        if event2["type"] != type2:
                            continue

                        t2 = event2["timestamp"]
                        if not isinstance(t2, datetime):
                            t2 = datetime.fromisoformat(str(t2).replace("Z", "+00:00"))

                        if (t2 - t1).total_seconds() <= time_window:
                            first_seen = min(first_seen, t1)
                            last_seen = max(last_seen, t2)
                            break

                pattern = Pattern(
                    pattern_id=pattern_id,
                    pattern_type="correlation",
                    description=description,
                    events=[{"type": type1}, {"type": type2}],
                    confidence=confidence,
                    occurrences=cooccur_count,
                    first_seen=first_seen,
                    last_seen=last_seen,
                    metadata={
                        "correlation_strength": correlation_strength,
                        "time_window_seconds": time_window
                    }
                )

                patterns.append(pattern)

        return patterns

    # ========================================================================
    # Temporal Pattern Learning (Time-Window Analysis)
    # ========================================================================

    def _learn_temporal_patterns(self) -> List[Pattern]:
        """
        Detect time-based patterns.

        Algorithm:
        1. Aggregate events into time windows (e.g., hourly, daily)
        2. Identify spikes or patterns in specific windows
        3. Create patterns for recurring temporal behaviors

        Example pattern:
            errors spike every Monday 9am
            → Pattern: "weekly_load_spike"

        Returns:
            List of temporal patterns
        """
        patterns: List[Pattern] = []

        # Group events by hour of day
        events_by_hour: Dict[int, List[Dict[str, Any]]] = defaultdict(list)

        for event in self._event_history:
            timestamp = event["timestamp"]
            if not isinstance(timestamp, datetime):
                timestamp = datetime.fromisoformat(str(timestamp).replace("Z", "+00:00"))

            hour = timestamp.hour
            events_by_hour[hour].append(event)

        # Find hours with significantly more events (spikes)
        avg_events_per_hour = len(self._event_history) / max(len(events_by_hour), 1)

        for hour, events in events_by_hour.items():
            if len(events) < self._min_occurrences:
                continue

            # Check if this hour has significantly more events
            spike_ratio = len(events) / max(avg_events_per_hour, 1)

            if spike_ratio >= 2.0:  # 2x average = spike
                confidence = min(spike_ratio / 4.0, 1.0)  # Normalize

                # Find dominant event type in this hour
                event_types = Counter(event["type"] for event in events)
                dominant_type, dominant_count = event_types.most_common(1)[0]

                pattern_id = f"temp_hour_{hour}_{dominant_type}"
                description = (
                    f"Temporal: {dominant_type} spikes at hour {hour} "
                    f"({len(events)} events, {spike_ratio:.1f}x average)"
                )

                # Normalize timestamps
                normalized_timestamps = []
                for e in events:
                    ts = e["timestamp"]
                    if not isinstance(ts, datetime):
                        ts = datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
                    normalized_timestamps.append(ts)

                first_seen = min(normalized_timestamps)
                last_seen = max(normalized_timestamps)

                pattern = Pattern(
                    pattern_id=pattern_id,
                    pattern_type="temporal",
                    description=description,
                    events=[{"type": dominant_type}],
                    confidence=confidence,
                    occurrences=len(events),
                    first_seen=first_seen,
                    last_seen=last_seen,
                    metadata={
                        "hour_of_day": hour,
                        "spike_ratio": spike_ratio,
                        "dominant_event_type": dominant_type
                    }
                )

                patterns.append(pattern)

        return patterns


# ============================================================================
# Module Exports
# ============================================================================

__all__ = [
    "PatternLearner",
    "Pattern"
]
