#!/usr/bin/env python3
"""
Test script for Pattern Analysis

Demonstrates analyze_patterns.py functionality with sample data.

Usage:
    python moai_flow/scripts/test_analyze_patterns.py
"""

import logging
from datetime import datetime, timedelta

from moai_flow.monitoring.metrics_collector import (
    MetricsCollector,
    MetricsStorage,
    TaskResult
)
from moai_flow.scripts.analyze_patterns import (
    PatternAnalyzer,
    ReportGenerator
)


def populate_sample_data(collector: MetricsCollector):
    """Populate collector with sample metrics data"""

    # Sample agent IDs
    agents = [
        "expert-backend",
        "expert-frontend",
        "manager-tdd",
        "expert-database",
        "expert-devops"
    ]

    # Sample patterns
    patterns = [
        "api_implementation",
        "database_migration",
        "test_creation",
        "frontend_component",
        "deployment_script"
    ]

    # Error types
    error_types = [
        "TypeError",
        "ImportError",
        "NetworkError",
        "ValidationError"
    ]

    # Generate sample task metrics for the last 7 days
    now = datetime.now()

    for day in range(7):
        task_date = now - timedelta(days=day)

        for i in range(20):  # 20 tasks per day
            agent_id = agents[i % len(agents)]
            pattern = patterns[i % len(patterns)]

            # Vary success rate and duration by agent
            if agent_id == "expert-backend":
                # Backend slower but reliable
                duration = 45000 + (i * 1000)
                success = i % 10 != 0  # 90% success
            elif agent_id == "manager-tdd":
                # TDD fast and reliable
                duration = 25000 + (i * 500)
                success = True  # 100% success
            elif agent_id == "expert-frontend":
                # Frontend fast but occasional failures
                duration = 30000 + (i * 800)
                success = i % 8 != 0  # 87.5% success
            elif agent_id == "expert-database":
                # Database medium speed, very reliable
                duration = 35000 + (i * 700)
                success = i % 15 != 0  # 93% success
            else:
                # DevOps variable
                duration = 40000 + (i * 1200)
                success = i % 12 != 0  # 91% success

            result = TaskResult.SUCCESS if success else TaskResult.FAILURE

            # Add error type for failures
            metadata = {"pattern": pattern}
            if not success:
                metadata["error_type"] = error_types[i % len(error_types)]

            # Record metric
            collector.record_task_metric(
                task_id=f"task-{day}-{i}",
                agent_id=agent_id,
                duration_ms=duration,
                result=result,
                tokens_used=15000 + (i * 1000),
                files_changed=1 + (i % 5),
                metadata=metadata
            )

    print(f"✓ Populated {20 * 7} sample metrics across 7 days")


def main():
    """Test pattern analysis with sample data"""

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    print("=" * 60)
    print("Pattern Analysis Test Script")
    print("=" * 60)

    # Initialize
    print("\n1. Initializing metrics collector...")
    storage = MetricsStorage()
    collector = MetricsCollector(storage, async_mode=False)

    # Populate sample data
    print("\n2. Populating sample data...")
    populate_sample_data(collector)

    # Initialize analyzer
    print("\n3. Initializing pattern analyzer...")
    analyzer = PatternAnalyzer(collector)

    # Test agent performance analysis
    print("\n4. Analyzing agent performance...")
    agent_perf = analyzer.analyze_agent_performance(days=7)

    print("\n   Agent Performance Results:")
    for agent_id, data in agent_perf.items():
        print(f"   - {agent_id}:")
        print(f"     Tasks: {data['tasks']}")
        print(f"     Success Rate: {data['success_rate']:.1%}")
        print(f"     Avg Duration: {data['avg_duration_ms']/1000:.1f}s")

    # Test error pattern analysis
    print("\n5. Analyzing error patterns...")
    error_patterns = analyzer.analyze_error_patterns(days=7)

    print("\n   Error Pattern Results:")
    for error_type, count in error_patterns.items():
        print(f"   - {error_type}: {count} occurrences")

    # Test task pattern analysis
    print("\n6. Analyzing task patterns...")
    task_patterns = analyzer.analyze_task_patterns(days=7)

    print("\n   Task Pattern Results:")
    for pattern in task_patterns[:5]:  # Top 5
        print(f"   - {pattern['pattern']}:")
        print(f"     Occurrences: {pattern['occurrences']}")
        print(f"     Success Rate: {pattern['success_rate']:.1%}")
        print(f"     Avg Duration: {pattern['avg_duration_ms']/1000:.1f}s")

    # Test recommendations
    print("\n7. Generating recommendations...")
    recommendations = analyzer.generate_recommendations({
        "agent_performance": agent_perf,
        "errors": error_patterns,
        "tasks": task_patterns
    })

    print("\n   Recommendations:")
    for i, rec in enumerate(recommendations, 1):
        print(f"   {i}. {rec}")

    # Test report generation
    print("\n8. Generating full report...")
    reporter = ReportGenerator(analyzer)
    report = reporter.generate_weekly_report()

    print(f"\n   Report Summary:")
    print(f"   - Total Tasks: {report['summary']['total_tasks']}")
    print(f"   - Success Rate: {report['summary']['success_rate']:.1%}")
    print(f"   - Avg Duration: {report['summary']['avg_duration_ms']/1000:.1f}s")

    # Save report
    print("\n9. Saving report...")
    output_file = reporter.save_report(
        report,
        output_path=".moai/reports/patterns/",
        format="both"
    )
    print(f"   Report saved to: {output_file}")

    print("\n" + "=" * 60)
    print("Test Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
