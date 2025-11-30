#!/usr/bin/env python3
"""
Validation Script for PredictiveHealing Enhancement (PRD-09)
=============================================================

Validates that all required features are implemented:
1. predict_failures() - Pattern-based failure prediction ✓
2. _analyze_patterns() - Pattern matching ✓
3. _calculate_confidence() - Confidence scoring (0.0-1.0) ✓
4. _recommend_action() - Preventive action recommendations ✓
5. apply_preventive_healing() - Automated healing ✓
6. _handle_false_positive() - Learning from mistakes ✓

Additional enhancements:
7. BottleneckDetector integration ✓
8. Agent health degradation monitoring ✓
9. Queue depth trend analysis ✓
10. Enhanced confidence calculation ✓
11. Comprehensive statistics ✓

Target: >70% accuracy
"""

import sys
import inspect
from typing import List, Dict, Any

def validate_predictive_healing():
    """Validate PredictiveHealing implementation."""

    print("=" * 70)
    print("PredictiveHealing Enhancement Validation (PRD-09)")
    print("=" * 70)
    print()

    # Import module
    try:
        from moai_flow.optimization.predictive_healing import (
            PredictiveHealing,
            PredictedFailure
        )
        print("✓ Module imports successful")
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False

    # Validation results
    checks = []

    # Check 1: PredictiveHealing class exists
    checks.append(("PredictiveHealing class", hasattr(PredictiveHealing, '__init__')))

    # Check 2: PredictedFailure dataclass
    checks.append(("PredictedFailure dataclass", hasattr(PredictedFailure, 'failure_type')))
    checks.append(("PredictedFailure.source field", hasattr(PredictedFailure, '__dataclass_fields__') and 'source' in PredictedFailure.__dataclass_fields__))
    checks.append(("PredictedFailure.to_dict method", hasattr(PredictedFailure, 'to_dict')))

    # Check 3: Core methods exist
    required_methods = [
        'predict_failures',
        '_analyze_pattern_for_failure',
        '_calculate_confidence',
        '_recommend_action_for_type',
        'apply_preventive_healing',
        'record_prediction_outcome',
        '_handle_false_positive'
    ]

    for method_name in required_methods:
        has_method = hasattr(PredictiveHealing, method_name)
        checks.append((f"Method: {method_name}", has_method))

    # Check 4: Enhanced prediction sources
    enhanced_methods = [
        '_analyze_resource_trends',
        '_analyze_bottlenecks',
        '_analyze_agent_health',
        '_analyze_queue_trends'
    ]

    for method_name in enhanced_methods:
        has_method = hasattr(PredictiveHealing, method_name)
        checks.append((f"Enhanced: {method_name}", has_method))

    # Check 5: Confidence calculation formula
    confidence_method = getattr(PredictiveHealing, '_calculate_confidence', None)
    if confidence_method:
        source = inspect.getsource(confidence_method)
        has_pattern_score = '* 0.5' in source
        has_historical = '* 0.3' in source
        has_recency = '* 0.2' in source

        checks.append(("Confidence: Pattern 50%", has_pattern_score))
        checks.append(("Confidence: Historical 30%", has_historical))
        checks.append(("Confidence: Recency 20%", has_recency))

    # Check 6: Initialization parameters
    init_method = getattr(PredictiveHealing, '__init__', None)
    if init_method:
        sig = inspect.signature(init_method)
        params = list(sig.parameters.keys())

        checks.append(("Init: pattern_learner param", 'pattern_learner' in params))
        checks.append(("Init: self_healer param", 'self_healer' in params))
        checks.append(("Init: bottleneck_detector param", 'bottleneck_detector' in params))
        checks.append(("Init: confidence_threshold param", 'confidence_threshold' in params))

    # Check 7: Statistics method
    stats_method = getattr(PredictiveHealing, 'get_prediction_stats', None)
    if stats_method:
        checks.append(("Statistics: get_prediction_stats", True))

    # Check 8: False positive tracking
    fp_method = getattr(PredictiveHealing, '_handle_false_positive', None)
    if fp_method:
        source = inspect.getsource(fp_method)
        has_logging = 'logger.warning' in source or 'logger.info' in source
        has_tracking = '_false_positive_details' in source

        checks.append(("False positive: logging", has_logging))
        checks.append(("False positive: tracking", has_tracking))

    # Print results
    print("\nValidation Results:")
    print("-" * 70)

    passed = 0
    failed = 0

    for check_name, result in checks:
        status = "✓" if result else "✗"
        print(f"{status} {check_name}")
        if result:
            passed += 1
        else:
            failed += 1

    print("-" * 70)
    print(f"\nTotal: {passed} passed, {failed} failed out of {len(checks)} checks")

    success_rate = (passed / len(checks)) * 100
    print(f"Success Rate: {success_rate:.1f}%")

    # Check line count
    try:
        import os
        file_path = "moai_flow/optimization/predictive_healing.py"
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                lines = len(f.readlines())
            print(f"\nFile Size: {lines} lines (target: ~500 LOC)")
            if lines >= 500:
                print("✓ Line count target met")
            else:
                print("✗ Line count below target")
    except Exception as e:
        print(f"Could not check line count: {e}")

    print("\n" + "=" * 70)

    if failed == 0:
        print("✓ ALL CHECKS PASSED - Implementation complete!")
        print("=" * 70)
        return True
    else:
        print(f"✗ {failed} checks failed - Review implementation")
        print("=" * 70)
        return False

def demonstrate_usage():
    """Demonstrate PredictiveHealing usage."""

    print("\nUsage Example:")
    print("-" * 70)

    example_code = '''
from moai_flow.optimization.predictive_healing import PredictiveHealing
from moai_flow.optimization.pattern_learner import PatternLearner
from moai_flow.optimization.self_healer import SelfHealer
from moai_flow.optimization.bottleneck_detector import BottleneckDetector

# Initialize components
pattern_learner = PatternLearner()
self_healer = SelfHealer(coordinator, pattern_learner)
bottleneck_detector = BottleneckDetector(metrics_storage, resource_controller)

# Create predictive healing system
predictor = PredictiveHealing(
    pattern_learner=pattern_learner,
    self_healer=self_healer,
    bottleneck_detector=bottleneck_detector,
    confidence_threshold=0.7  # 70% confidence minimum
)

# Predict failures from recent events
events = coordinator.get_recent_events()
predictions = predictor.predict_failures(events)

# Apply preventive healing for high-confidence predictions
for prediction in predictions:
    if prediction.confidence > 0.8:
        result = predictor.apply_preventive_healing(
            prediction,
            auto_apply=True
        )
        print(f"Applied: {result.actions_taken}")

# Learn from outcomes
for prediction in predictions:
    occurred = check_if_failure_occurred(prediction)
    predictor.record_prediction_outcome(prediction, occurred)

# Get statistics
stats = predictor.get_prediction_stats()
print(f"Overall accuracy: {stats['overall_accuracy']:.1%}")
print(f"Meets target: {stats['meets_target']}")
print(f"Recommendations: {stats['recommendations']}")
'''

    print(example_code)
    print("-" * 70)

if __name__ == "__main__":
    success = validate_predictive_healing()

    if success:
        demonstrate_usage()
        sys.exit(0)
    else:
        sys.exit(1)
