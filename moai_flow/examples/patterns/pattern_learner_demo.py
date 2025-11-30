#!/usr/bin/env python3
"""
PatternLearner Demo - Phase 6C Adaptive Optimization

Demonstrates statistical pattern learning for MoAI-Flow swarm coordination.

Shows:
- Event recording
- Pattern learning (sequence, frequency, correlation, temporal)
- Pattern retrieval and confidence scoring
- Performance characteristics

Usage:
    python moai_flow/examples/pattern_learner_demo.py
"""

import logging
import time
from datetime import datetime, timezone, timedelta

from moai_flow.optimization import PatternLearner, Pattern

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def demo_pattern_learner():
    """Demonstrate PatternLearner capabilities"""

    print("=" * 80)
    print("PatternLearner Demo - Phase 6C Adaptive Optimization")
    print("=" * 80)
    print()

    # Initialize pattern learner
    print("1. Initializing PatternLearner...")
    learner = PatternLearner(
        min_occurrences=3,  # Lower threshold for demo
        confidence_threshold=0.6  # 60% confidence
    )
    print(f"   ✓ Configured with min_occurrences=3, confidence_threshold=0.6")
    print()

    # Record sample events (simulating real swarm activity)
    print("2. Recording events (simulating swarm activity)...")

    # Sequence pattern: task workflow
    base_time = datetime.now(timezone.utc)
    for i in range(10):
        # Standard workflow: start → execute → complete
        offset = timedelta(minutes=i * 5)

        learner.record_event({
            "type": "task_start",
            "timestamp": base_time + offset,
            "agent_id": f"agent-{i % 3}"
        })

        learner.record_event({
            "type": "task_execute",
            "timestamp": base_time + offset + timedelta(seconds=30),
            "agent_id": f"agent-{i % 3}"
        })

        learner.record_event({
            "type": "task_complete",
            "timestamp": base_time + offset + timedelta(seconds=60),
            "agent_id": f"agent-{i % 3}"
        })

    # Frequency pattern: regular heartbeat
    for i in range(20):
        learner.record_event({
            "type": "heartbeat",
            "timestamp": base_time + timedelta(seconds=i * 5),
            "agent_id": "monitor"
        })

    # Correlation pattern: high token usage + slow response
    for i in range(8):
        offset = timedelta(minutes=i * 2)

        learner.record_event({
            "type": "high_token_usage",
            "timestamp": base_time + offset,
            "agent_id": f"agent-{i % 2}"
        })

        learner.record_event({
            "type": "slow_response",
            "timestamp": base_time + offset + timedelta(seconds=2),
            "agent_id": f"agent-{i % 2}"
        })

    # Temporal pattern: errors at specific hour
    error_time = base_time.replace(hour=9, minute=0, second=0)
    for i in range(5):
        learner.record_event({
            "type": "error_spike",
            "timestamp": error_time + timedelta(days=i),
            "agent_id": "system"
        })

    total_events = len(learner._event_history)
    print(f"   ✓ Recorded {total_events} events")
    print()

    # Learn patterns
    print("3. Learning patterns from event history...")
    start_time = time.perf_counter()

    patterns = learner.learn_patterns()

    duration_ms = (time.perf_counter() - start_time) * 1000

    print(f"   ✓ Discovered {len(patterns)} patterns in {duration_ms:.2f}ms")
    print(f"   Performance: {duration_ms / total_events:.2f}ms per event")
    print()

    # Display patterns by type
    print("4. Discovered Patterns:")
    print()

    pattern_types = ["sequence", "frequency", "correlation", "temporal"]

    for pattern_type in pattern_types:
        type_patterns = [p for p in patterns if p.pattern_type == pattern_type]

        if type_patterns:
            print(f"   {pattern_type.upper()} Patterns ({len(type_patterns)}):")

            for pattern in type_patterns[:3]:  # Show top 3 per type
                print(f"   • {pattern.description}")
                print(f"     Confidence: {pattern.confidence:.2%}")
                print(f"     Occurrences: {pattern.occurrences}")
                print(f"     ID: {pattern.pattern_id}")
                print()

    # Get specific pattern
    print("5. Retrieving specific pattern...")
    if patterns:
        pattern_id = patterns[0].pattern_id
        retrieved = learner.get_pattern(pattern_id)

        if retrieved:
            print(f"   ✓ Retrieved pattern: {retrieved.pattern_type}")
            print(f"     Description: {retrieved.description}")
            print(f"     Confidence: {retrieved.confidence:.2%}")
        print()

    # Get all patterns
    print("6. Getting all patterns...")
    all_patterns = learner.get_all_patterns()
    print(f"   ✓ Total patterns: {len(all_patterns)}")
    print(f"   High confidence (>80%): {len([p for p in all_patterns if p.confidence > 0.8])}")
    print(f"   Medium confidence (60-80%): {len([p for p in all_patterns if 0.6 <= p.confidence <= 0.8])}")
    print()

    # Performance summary
    print("7. Performance Summary:")
    print(f"   Events processed: {total_events}")
    print(f"   Patterns discovered: {len(patterns)}")
    print(f"   Learning time: {duration_ms:.2f}ms")
    print(f"   Throughput: {total_events / (duration_ms / 1000):.0f} events/sec")
    print(f"   Target: <500ms for 1000 events ({'✓ PASS' if duration_ms < 500 else '✗ FAIL'})")
    print()

    print("=" * 80)
    print("Demo Complete!")
    print("=" * 80)


if __name__ == "__main__":
    demo_pattern_learner()
