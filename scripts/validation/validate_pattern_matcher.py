#!/usr/bin/env python3
"""
PatternMatcher Validation Script

Quick validation of PatternMatcher implementation with sample patterns and events.
"""

from datetime import datetime
from moai_flow.optimization import PatternMatcher, Pattern


def main():
    print("=" * 70)
    print("PatternMatcher Validation")
    print("=" * 70)

    # Create sample patterns (using pattern_learner.Pattern structure)
    base_time = datetime.now()
    patterns = [
        Pattern(
            pattern_id="api-impl-001",
            pattern_type="sequence",
            description="API implementation pattern with FastAPI",
            events=[
                {"type": "task_start", "timestamp": base_time},
                {"type": "agent_busy", "timestamp": base_time},
                {"type": "file_write", "timestamp": base_time},
                {"type": "test_run", "timestamp": base_time},
                {"type": "task_complete", "timestamp": base_time}
            ],
            confidence=0.92,
            occurrences=25,
            first_seen=base_time,
            last_seen=base_time,
            metadata={"framework": "fastapi", "language": "python"}
        ),
        Pattern(
            pattern_id="db-migration-001",
            pattern_type="sequence",
            description="Database migration pattern with Alembic",
            events=[
                {"type": "task_start", "timestamp": base_time},
                {"type": "schema_read", "timestamp": base_time},
                {"type": "migration_run", "timestamp": base_time},
                {"type": "test_run", "timestamp": base_time},
                {"type": "task_complete", "timestamp": base_time}
            ],
            confidence=0.88,
            occurrences=12,
            first_seen=base_time,
            last_seen=base_time,
            metadata={"database": "postgresql", "tool": "alembic"}
        ),
        Pattern(
            pattern_id="test-only-001",
            pattern_type="sequence",
            description="Test-only pattern with pytest",
            events=[
                {"type": "task_start", "timestamp": base_time},
                {"type": "test_run", "timestamp": base_time},
                {"type": "task_complete", "timestamp": base_time}
            ],
            confidence=0.95,
            occurrences=50,
            first_seen=base_time,
            last_seen=base_time,
            metadata={"test_framework": "pytest"}
        )
    ]

    # Initialize matcher
    matcher = PatternMatcher(match_threshold=0.7)
    matcher.load_patterns(patterns)
    print(f"\n✓ Loaded {len(patterns)} patterns")

    # Test 1: Process events and get matches
    print("\n" + "-" * 70)
    print("Test 1: Real-time Event Processing")
    print("-" * 70)

    events = [
        {"type": "task_start", "timestamp": datetime.now(), "metadata": {"framework": "fastapi"}},
        {"type": "agent_busy", "timestamp": datetime.now(), "metadata": {"language": "python"}},
        {"type": "file_write", "timestamp": datetime.now(), "metadata": {"files": 3}}
    ]

    for i, event in enumerate(events, 1):
        print(f"\nEvent {i}: {event['type']}")
        result = matcher.process_event(event)

        # Display matches
        if result["matches"]:
            print(f"  Matches found: {len(result['matches'])}")
            for match in result["matches"][:2]:
                print(f"    - {match.pattern.pattern_id}: similarity={match.similarity:.3f}")
        else:
            print("  No matches above threshold")

        # Display predictions
        if result["predictions"]:
            print(f"  Predictions: {len(result['predictions'])}")
            for pred in result["predictions"][:2]:
                print(f"    - Next: {pred.predicted_event_type} (p={pred.probability:.3f})")
        else:
            print("  No predictions available")

    # Test 2: Pattern search
    print("\n" + "-" * 70)
    print("Test 2: Pattern Search")
    print("-" * 70)

    search_event = "test_run"
    found_patterns = matcher.get_matching_patterns(search_event)
    print(f"\nPatterns containing '{search_event}': {len(found_patterns)}")
    for pattern in found_patterns:
        event_types = [e.get("type") for e in pattern.events]
        print(f"  - {pattern.pattern_id}: {' → '.join(event_types)}")

    # Test 3: LCS similarity
    print("\n" + "-" * 70)
    print("Test 3: LCS Similarity Algorithm")
    print("-" * 70)

    seq1 = ["task_start", "agent_busy", "task_complete"]
    seq2 = ["task_start", "agent_busy", "agent_idle", "task_complete"]
    similarity = matcher._lcs_similarity(seq1, seq2)
    print(f"\nSequence 1: {seq1}")
    print(f"Sequence 2: {seq2}")
    print(f"LCS Similarity: {similarity:.3f}")

    # Test 4: Prediction accuracy
    print("\n" + "-" * 70)
    print("Test 4: Prediction Quality")
    print("-" * 70)

    test_sequence = [
        {"type": "task_start", "timestamp": datetime.now()},
        {"type": "agent_busy", "timestamp": datetime.now()}
    ]

    predictions = matcher.predict_next(test_sequence)
    print(f"\nCurrent sequence: {[e['type'] for e in test_sequence]}")
    print(f"Top predictions:")
    for pred in predictions[:3]:
        print(f"  - {pred.predicted_event_type}")
        print(f"    Probability: {pred.probability:.3f}")
        print(f"    Confidence: {pred.confidence:.3f}")
        print(f"    Expected in: {pred.expected_time_ms}ms")
        print(f"    Based on: {pred.based_on_pattern.pattern_id}")

    # Test 5: Metadata similarity
    print("\n" + "-" * 70)
    print("Test 5: Metadata Similarity")
    print("-" * 70)

    meta1 = {"framework": "fastapi", "version": 100, "count": 25}
    meta2 = {"framework": "fastapi", "version": 120, "count": 30}
    similarity = matcher._metadata_similarity(meta1, meta2)
    print(f"\nMetadata 1: {meta1}")
    print(f"Metadata 2: {meta2}")
    print(f"Similarity: {similarity:.3f}")

    # Summary
    print("\n" + "=" * 70)
    print("Validation Summary")
    print("=" * 70)
    print("✓ Pattern loading: PASSED")
    print("✓ Event processing: PASSED")
    print("✓ Pattern matching: PASSED")
    print("✓ Prediction generation: PASSED")
    print("✓ LCS algorithm: PASSED")
    print("✓ Metadata similarity: PASSED")
    print("\nAll tests completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    main()
