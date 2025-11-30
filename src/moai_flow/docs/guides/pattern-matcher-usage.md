# PatternMatcher Usage Guide

## Overview

PatternMatcher is a real-time pattern matching and prediction engine for MoAI-Flow Phase 6C adaptive optimization. It uses statistical algorithms (NO ML) to match current events against learned patterns and predict future events.

## Quick Start

```python
from moai_flow.optimization import PatternMatcher, Pattern
from datetime import datetime

# Initialize matcher
matcher = PatternMatcher(match_threshold=0.8)

# Load learned patterns
patterns = [
    Pattern(
        pattern_id="api-impl-001",
        event_sequence=["task_start", "agent_busy", "file_write", "task_complete"],
        occurrence_count=25,
        confidence=0.92,
        avg_duration_ms=45000,
        metadata={"framework": "fastapi", "language": "python"}
    ),
    Pattern(
        pattern_id="db-migration-001",
        event_sequence=["task_start", "schema_read", "migration_run", "task_complete"],
        occurrence_count=12,
        confidence=0.88,
        avg_duration_ms=30000,
        metadata={"database": "postgresql", "tool": "alembic"}
    )
]

matcher.load_patterns(patterns)
```

## Real-Time Event Processing

```python
# Process event and get matches + predictions
event = {
    "type": "task_start",
    "timestamp": datetime.now(),
    "metadata": {"framework": "fastapi", "language": "python"}
}

result = matcher.process_event(event)

# Access matches
for match in result["matches"]:
    print(f"Pattern: {match.pattern.pattern_id}")
    print(f"Similarity: {match.similarity:.2f}")
    print(f"Confidence: {match.pattern.confidence:.2f}")

# Access predictions
for prediction in result["predictions"]:
    print(f"Next event: {prediction.predicted_event_type}")
    print(f"Probability: {prediction.probability:.2f}")
    print(f"Expected in: {prediction.expected_time_ms}ms")
```

## Individual Matching

```python
# Match single event
event = {"type": "agent_busy", "timestamp": datetime.now()}
matches = matcher.match(event)

# Get top match
if matches:
    top_match = matches[0]
    print(f"Best match: {top_match.pattern.pattern_id}")
    print(f"Similarity: {top_match.similarity:.2f}")
```

## Prediction

```python
# Predict next events based on current sequence
current_events = [
    {"type": "task_start", "timestamp": datetime.now()},
    {"type": "agent_busy", "timestamp": datetime.now()}
]

predictions = matcher.predict_next(current_events)

for pred in predictions[:3]:  # Top 3 predictions
    print(f"Predicted: {pred.predicted_event_type}")
    print(f"Probability: {pred.probability:.2f}")
    print(f"Based on: {pred.based_on_pattern.pattern_id}")
    print(f"Expected in: {pred.expected_time_ms}ms")
```

## Pattern Search

```python
# Find all patterns containing specific event type
patterns = matcher.get_matching_patterns("file_write")

for pattern in patterns:
    print(f"Pattern: {pattern.pattern_id}")
    print(f"Sequence: {' → '.join(pattern.event_sequence)}")
    print(f"Occurrences: {pattern.occurrence_count}")
```

## Algorithm Details

### 1. Sequence Matching (LCS)

PatternMatcher uses Longest Common Subsequence (LCS) algorithm for sequence similarity:

```python
# Example:
current = ["task_start", "agent_busy", "task_complete"]
pattern = ["task_start", "agent_busy", "agent_idle", "task_complete"]

# LCS = ["task_start", "agent_busy", "task_complete"] (length 3)
# Similarity = 3 / 4 = 0.75
```

### 2. Event Type Matching

Scores event similarity based on:
- Event type exact match: 50%
- Metadata similarity: 50%

```python
# Numeric metadata comparison
v1, v2 = 100, 120
similarity = 1.0 - abs(v1 - v2) / max(v1, v2)  # 0.83

# String metadata comparison
similarity = 1.0 if str1 == str2 else 0.0
```

### 3. Temporal Matching

Compares event timing patterns:

```python
# Current interval: 15000ms
# Pattern average: 18000ms
# Tolerance: 50% (9000ms)
# Difference: 3000ms (within tolerance)
# Similarity: 1.0 - (3000 / 9000) = 0.67
```

### 4. Combined Scoring

Final similarity = weighted combination:
- 50% Sequence similarity (LCS)
- 30% Event type match
- 20% Temporal match

### 5. Prediction Probability

Prediction probability calculation:
- 40% Pattern confidence
- 40% Sequence match quality
- 20% Occurrence count (normalized)

## Performance Characteristics

- **Match Operation**: <50ms per event
- **Thread Safety**: Full lock-based synchronization
- **Memory**: O(n) where n = number of patterns
- **Sequence Window**: 10 events maximum
- **No ML Dependencies**: Pure statistical algorithms

## Integration with PatternLearner

```python
from moai_flow.optimization import PatternLearner, PatternMatcher

# Learn patterns from historical data
learner = PatternLearner()
learner.add_event({"type": "task_start", ...})
learner.add_event({"type": "agent_busy", ...})
# ... more events
patterns = learner.extract_patterns(min_occurrences=5, min_confidence=0.7)

# Use patterns in matcher
matcher = PatternMatcher(match_threshold=0.8)
matcher.load_patterns(patterns)

# Real-time matching
result = matcher.process_event(new_event)
```

## Thread Safety

PatternMatcher is fully thread-safe:

```python
from threading import Thread

def process_events():
    for event in event_stream:
        result = matcher.process_event(event)
        handle_result(result)

# Multiple threads safe
threads = [Thread(target=process_events) for _ in range(4)]
for t in threads:
    t.start()
```

## Configuration Options

```python
# Adjust match threshold (default 0.8)
matcher = PatternMatcher(match_threshold=0.7)  # More permissive

# Access internal configuration
matcher._max_sequence_length = 15  # Longer sequence window
```

## Best Practices

1. **Pattern Quality**: Load high-confidence patterns (>0.7)
2. **Threshold Tuning**: Start with 0.8, adjust based on precision/recall
3. **Sequence Length**: Keep ≤10 events for real-time performance
4. **Pattern Updates**: Reload patterns periodically as learner improves
5. **Prediction Filtering**: Use top 3-5 predictions to avoid noise

## Example: Complete Workflow

```python
from moai_flow.optimization import PatternMatcher, Pattern
from datetime import datetime

# 1. Initialize
matcher = PatternMatcher(match_threshold=0.8)

# 2. Load patterns (from PatternLearner or storage)
patterns = load_patterns_from_storage()
matcher.load_patterns(patterns)

# 3. Process real-time events
def handle_event(event):
    # Match and predict
    result = matcher.process_event(event)

    # Log matches
    for match in result["matches"]:
        if match.similarity > 0.9:
            print(f"High-confidence match: {match.pattern.pattern_id}")

    # Act on predictions
    for pred in result["predictions"]:
        if pred.probability > 0.85:
            prepare_for_event(pred.predicted_event_type)
            schedule_action(delay_ms=pred.expected_time_ms)

# 4. Event loop
for event in event_stream:
    handle_event(event)
```

## Troubleshooting

**Low match rates**:
- Lower match_threshold
- Check pattern quality (confidence scores)
- Verify event type consistency

**Slow performance**:
- Reduce number of loaded patterns
- Decrease sequence window size
- Profile with cProfile

**Poor predictions**:
- Increase min_occurrences when learning patterns
- Filter low-confidence patterns
- Ensure diverse training data

## API Reference

### PatternMatcher

```python
class PatternMatcher:
    def __init__(self, match_threshold: float = 0.8) -> None
    def load_patterns(self, patterns: List[Pattern]) -> None
    def match(self, event: Dict[str, Any]) -> List[PatternMatch]
    def predict_next(self, current_events: List[Dict[str, Any]]) -> List[Prediction]
    def get_matching_patterns(self, event_type: str) -> List[Pattern]
    def process_event(self, event: Dict[str, Any]) -> Dict[str, Any]
```

### Pattern

```python
@dataclass
class Pattern:
    pattern_id: str
    event_sequence: List[str]
    occurrence_count: int
    confidence: float
    avg_duration_ms: int
    metadata: Dict[str, Any]
    temporal_characteristics: Dict[str, Any]
    created_at: datetime
    last_seen: datetime
```

### PatternMatch

```python
@dataclass
class PatternMatch:
    pattern: Pattern
    similarity: float
    matched_events: List[Dict[str, Any]]
    timestamp: datetime
    metadata: Dict[str, Any]
```

### Prediction

```python
@dataclass
class Prediction:
    predicted_event_type: str
    probability: float
    based_on_pattern: Pattern
    confidence: float
    expected_time_ms: Optional[int]
    metadata: Dict[str, Any]
```

---

**Status**: Production Ready
**Version**: 1.0.0 (Phase 6C)
**Performance**: <50ms per match, thread-safe
**Dependencies**: Python 3.11+, dataclasses, threading
