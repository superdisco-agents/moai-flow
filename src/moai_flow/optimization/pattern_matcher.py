"""
MoAI-Flow Pattern Matcher - Phase 6C Adaptive Optimization

Real-time pattern matching and prediction system for identifying learned patterns
and predicting future events based on current execution context.

Features:
- Statistical pattern matching (NO ML)
- Sequence similarity with LCS algorithm
- Temporal pattern recognition
- Event type matching with metadata
- Real-time prediction with probability scoring
- Thread-safe operations

Target: ~280 LOC
Performance: <50ms per match operation
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from threading import Lock

# Import Pattern from pattern_learner for compatibility
try:
    from .pattern_learner import Pattern
except ImportError:
    # Fallback if pattern_learner not available
    @dataclass
    class Pattern:
        """
        Learned pattern from PatternLearner.

        Compatible with pattern_learner.Pattern structure.
        """
        pattern_id: str
        pattern_type: str
        description: str
        events: List[Dict[str, Any]]
        confidence: float  # 0.0 to 1.0
        occurrences: int
        first_seen: datetime
        last_seen: datetime
        metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PatternMatch:
    """
    Result of matching current event against learned pattern.
    """
    pattern: Pattern
    similarity: float  # 0.0 to 1.0
    matched_events: List[Dict[str, Any]]
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Prediction:
    """
    Predicted future event based on pattern analysis.
    """
    predicted_event_type: str
    probability: float  # 0.0 to 1.0
    based_on_pattern: Pattern
    confidence: float  # 0.0 to 1.0
    expected_time_ms: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class PatternMatcher:
    """
    Real-time pattern matching and prediction engine.

    Matches current events against learned patterns and predicts likely future events
    using statistical algorithms (LCS, temporal matching, metadata similarity).

    Thread-safe for concurrent event processing.
    """

    def __init__(self, match_threshold: float = 0.8):
        """
        Initialize pattern matcher.

        Args:
            match_threshold: Minimum similarity score for pattern match (0.0-1.0)
        """
        self._match_threshold = max(0.0, min(1.0, match_threshold))
        self._patterns: List[Pattern] = []
        self._current_sequence: List[Dict[str, Any]] = []
        self._max_sequence_length = 10
        self._lock = Lock()

    def load_patterns(self, patterns: List[Pattern]) -> None:
        """
        Load learned patterns from PatternLearner.

        Thread-safe pattern loading.

        Args:
            patterns: List of learned Pattern objects
        """
        with self._lock:
            self._patterns = patterns.copy()

    def match(self, event: Dict[str, Any]) -> List[PatternMatch]:
        """
        Match current event against all learned patterns.

        Returns patterns matching above threshold, sorted by similarity.

        Args:
            event: Event dict with 'type', 'timestamp', 'metadata', etc.

        Returns:
            List of PatternMatch objects sorted by similarity (highest first)
        """
        with self._lock:
            # Add to current sequence
            self._current_sequence.append(event)
            if len(self._current_sequence) > self._max_sequence_length:
                self._current_sequence.pop(0)

            # Get current sequence types
            current_types = [e.get("type", "unknown") for e in self._current_sequence]

            # Match against all patterns
            matches = []
            for pattern in self._patterns:
                # Get pattern event types from events list
                pattern_types = [e.get("type", "unknown") for e in pattern.events]

                # Calculate similarity
                seq_similarity = self._lcs_similarity(current_types, pattern_types)
                event_similarity = self._match_event_type(event, pattern.metadata)
                temporal_similarity = self._match_temporal(
                    [e.get("timestamp", datetime.now()) for e in self._current_sequence],
                    pattern
                )

                # Combined similarity: 50% sequence, 30% event type, 20% temporal
                combined_similarity = (
                    seq_similarity * 0.5 +
                    event_similarity * 0.3 +
                    temporal_similarity * 0.2
                )

                # Only include if above threshold
                if combined_similarity >= self._match_threshold:
                    matches.append(PatternMatch(
                        pattern=pattern,
                        similarity=combined_similarity,
                        matched_events=self._current_sequence.copy(),
                        metadata={
                            "seq_similarity": seq_similarity,
                            "event_similarity": event_similarity,
                            "temporal_similarity": temporal_similarity
                        }
                    ))

            # Sort by similarity (highest first)
            matches.sort(key=lambda m: m.similarity, reverse=True)
            return matches

    def predict_next(self, current_events: List[Dict[str, Any]]) -> List[Prediction]:
        """
        Predict next likely events based on current sequence.

        Analyzes patterns matching current sequence and returns predictions
        sorted by probability.

        Args:
            current_events: Current event sequence

        Returns:
            List of Prediction objects sorted by probability (highest first)
        """
        with self._lock:
            current_types = [e.get("type", "unknown") for e in current_events]
            predictions = []

            for pattern in self._patterns:
                # Get pattern event types
                pattern_types = [e.get("type", "unknown") for e in pattern.events]

                # Check if current sequence matches start of pattern
                match_length = self._get_match_length(current_types, pattern_types)

                if match_length > 0 and match_length < len(pattern_types):
                    # Predict next event in pattern
                    next_event_type = pattern_types[match_length]

                    # Calculate probability based on:
                    # - Pattern confidence (40%)
                    # - Sequence match quality (40%)
                    # - Occurrence count (20%)
                    match_quality = match_length / len(pattern_types)
                    occurrence_weight = min(pattern.occurrences / 100.0, 1.0)

                    probability = (
                        pattern.confidence * 0.4 +
                        match_quality * 0.4 +
                        occurrence_weight * 0.2
                    )

                    # Predict timing
                    expected_time_ms = self._predict_timing(pattern, current_events)

                    predictions.append(Prediction(
                        predicted_event_type=next_event_type,
                        probability=probability,
                        based_on_pattern=pattern,
                        confidence=pattern.confidence,
                        expected_time_ms=expected_time_ms,
                        metadata={
                            "match_length": match_length,
                            "match_quality": match_quality,
                            "occurrence_weight": occurrence_weight
                        }
                    ))

            # Sort by probability (highest first)
            predictions.sort(key=lambda p: p.probability, reverse=True)
            return predictions

    def get_matching_patterns(self, event_type: str) -> List[Pattern]:
        """
        Get all patterns that include specified event type.

        Args:
            event_type: Event type to search for

        Returns:
            List of Pattern objects containing the event type
        """
        with self._lock:
            matching = []
            for p in self._patterns:
                pattern_types = [e.get("type", "unknown") for e in p.events]
                if event_type in pattern_types:
                    matching.append(p)
            return matching

    def process_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process event in real-time: match patterns and generate predictions.

        Args:
            event: Event dict with type, timestamp, metadata

        Returns:
            Dict with matches, predictions, and timestamp
        """
        matches = self.match(event)
        predictions = self.predict_next(self._current_sequence)

        return {
            "matches": matches,
            "predictions": predictions,
            "timestamp": datetime.now(),
            "current_sequence_length": len(self._current_sequence)
        }

    def _lcs_similarity(self, seq1: List[str], seq2: List[str]) -> float:
        """
        Calculate LCS-based similarity between two sequences.

        Uses Longest Common Subsequence algorithm.
        Pure Python implementation, no external libraries.

        Args:
            seq1: First sequence
            seq2: Second sequence

        Returns:
            Similarity score 0.0-1.0
        """
        if not seq1 or not seq2:
            return 0.0

        # LCS dynamic programming table
        m, n = len(seq1), len(seq2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]

        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if seq1[i - 1] == seq2[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1] + 1
                else:
                    dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

        lcs_length = dp[m][n]
        max_length = max(m, n)

        return lcs_length / max_length if max_length > 0 else 0.0

    def _match_event_type(self, event: Dict[str, Any], pattern_metadata: Dict) -> float:
        """
        Match event type and metadata against pattern.

        Scoring:
        - Exact event type match: +0.5
        - Metadata similarity: +0.5

        Args:
            event: Current event
            pattern_metadata: Pattern metadata

        Returns:
            Similarity score 0.0-1.0
        """
        score = 0.0

        # Event type match (0.5 points)
        event_type = event.get("type", "unknown")
        if event_type in pattern_metadata.get("event_types", []):
            score += 0.5

        # Metadata similarity (0.5 points)
        event_meta = event.get("metadata", {})
        meta_similarity = self._metadata_similarity(event_meta, pattern_metadata)
        score += meta_similarity * 0.5

        return score

    def _match_temporal(self, event_times: List[datetime], pattern: Pattern) -> float:
        """
        Match timing patterns.

        Checks if current event timing matches pattern's temporal characteristics.

        Args:
            event_times: List of event timestamps
            pattern: Pattern with temporal characteristics

        Returns:
            Similarity score 0.0-1.0
        """
        if len(event_times) < 2:
            return 0.5  # Neutral score for insufficient data

        # Calculate current event interval
        intervals = []
        for i in range(1, len(event_times)):
            interval_ms = (event_times[i] - event_times[i - 1]).total_seconds() * 1000
            intervals.append(interval_ms)

        avg_interval = sum(intervals) / len(intervals)

        # Calculate pattern's average duration from first_seen to last_seen
        pattern_duration = (pattern.last_seen - pattern.first_seen).total_seconds() * 1000
        if pattern.occurrences > 1:
            pattern_avg = pattern_duration / pattern.occurrences
        else:
            pattern_avg = pattern_duration

        if pattern_avg == 0:
            return 0.5

        # Calculate similarity based on interval difference
        difference = abs(avg_interval - pattern_avg)
        max_acceptable_diff = pattern_avg * 0.5  # 50% tolerance

        if difference <= max_acceptable_diff:
            similarity = 1.0 - (difference / max_acceptable_diff)
        else:
            similarity = 0.0

        return similarity

    def _metadata_similarity(self, meta1: Dict, meta2: Dict) -> float:
        """
        Calculate metadata similarity.

        For numeric values: 1.0 - abs(v1 - v2) / max(v1, v2)
        For string values: exact match 1.0, else 0.0

        Args:
            meta1: First metadata dict
            meta2: Second metadata dict

        Returns:
            Similarity score 0.0-1.0
        """
        if not meta1 or not meta2:
            return 0.0

        # Get common keys
        common_keys = set(meta1.keys()) & set(meta2.keys())
        if not common_keys:
            return 0.0

        similarity_sum = 0.0
        for key in common_keys:
            v1, v2 = meta1[key], meta2[key]

            # Numeric comparison
            if isinstance(v1, (int, float)) and isinstance(v2, (int, float)):
                if v1 == 0 and v2 == 0:
                    similarity_sum += 1.0
                elif max(abs(v1), abs(v2)) > 0:
                    similarity_sum += 1.0 - min(abs(v1 - v2) / max(abs(v1), abs(v2)), 1.0)
            # String comparison
            elif isinstance(v1, str) and isinstance(v2, str):
                similarity_sum += 1.0 if v1 == v2 else 0.0
            # Other types: exact match only
            else:
                similarity_sum += 1.0 if v1 == v2 else 0.0

        return similarity_sum / len(common_keys)

    def _get_match_length(self, current: List[str], pattern: List[str]) -> int:
        """
        Get length of matching prefix between current and pattern sequences.

        Args:
            current: Current event sequence
            pattern: Pattern event sequence

        Returns:
            Length of matching prefix
        """
        match_length = 0
        min_length = min(len(current), len(pattern))

        for i in range(min_length):
            if current[i] == pattern[i]:
                match_length += 1
            else:
                break

        return match_length

    def _predict_timing(self, pattern: Pattern, current_events: List[Dict[str, Any]]) -> int:
        """
        Predict when next event will occur.

        Based on pattern's temporal characteristics and current timing.

        Args:
            pattern: Pattern with first_seen/last_seen timestamps
            current_events: Current event sequence

        Returns:
            Expected milliseconds until event
        """
        # Calculate pattern's average duration
        pattern_duration = (pattern.last_seen - pattern.first_seen).total_seconds() * 1000
        if pattern.occurrences > 1:
            avg_duration_ms = pattern_duration / pattern.occurrences
        else:
            avg_duration_ms = pattern_duration

        if not current_events:
            return int(avg_duration_ms)

        # Calculate time since last event
        last_event_time = current_events[-1].get("timestamp", datetime.now())
        time_since_last = (datetime.now() - last_event_time).total_seconds() * 1000

        # Estimate remaining time based on pattern duration and current progress
        events_in_pattern = len(pattern.events)
        current_length = len(current_events)

        if current_length >= events_in_pattern:
            return 0  # Pattern should be complete

        # Estimate time per event
        if events_in_pattern > 0:
            time_per_event = avg_duration_ms / events_in_pattern
            remaining_events = events_in_pattern - current_length
            estimated_remaining = int(time_per_event * remaining_events)
        else:
            estimated_remaining = int(avg_duration_ms)

        return max(0, estimated_remaining)
