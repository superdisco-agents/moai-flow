"""Example usage of GitHub Health Metrics System (PRD-06).

This example demonstrates:
1. Calculating repository health metrics
2. Analyzing health trends over time
3. Generating health reports
4. Tracking specific metrics (issue velocity, PR merge time, etc.)
"""

import os
from datetime import datetime, timedelta
from moai_flow.github.health_metrics import (
    HealthMetricsAnalyzer,
    HealthMetrics,
    HealthTrend,
    HealthComparison,
)


def example_basic_health_metrics():
    """Example: Calculate basic repository health metrics."""
    print("=" * 80)
    print("EXAMPLE 1: Basic Health Metrics")
    print("=" * 80)

    # Initialize analyzer
    analyzer = HealthMetricsAnalyzer(
        repo_owner="moai-adk",
        repo_name="agent-os-v2",
        github_token=os.getenv("GITHUB_TOKEN"),
        stale_days=60,
    )

    # Calculate current health metrics
    print("\nCalculating health metrics for last 4 weeks...")
    metrics = analyzer.calculate_health_metrics(lookback_weeks=4)

    # Display results
    print(f"\n{'=' * 80}")
    print("HEALTH METRICS REPORT")
    print(f"{'=' * 80}")
    print(f"Timestamp: {metrics.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\nOverall Health Score: {metrics.health_score}/100")
    print(f"Trend: {metrics.trend.value.upper()}")
    print(f"\n{'Individual Metrics:':^80}")
    print(f"{'-' * 80}")
    print(f"  Issue Velocity:        {metrics.issue_velocity:.2f} issues/week")
    print(f"  PR Merge Time:         {metrics.pr_merge_time:.2f} days")
    print(f"  Stale Count:           {metrics.stale_count} items")
    print(f"  Active Contributors:   {metrics.contributor_activity} contributors")
    print(f"  Coverage Trend:        {metrics.test_coverage_trend:+.2f}%")
    print(f"{'=' * 80}\n")

    return metrics


def example_detailed_metrics():
    """Example: Get detailed metrics breakdowns."""
    print("=" * 80)
    print("EXAMPLE 2: Detailed Metrics Breakdown")
    print("=" * 80)

    analyzer = HealthMetricsAnalyzer(
        repo_owner="moai-adk",
        repo_name="agent-os-v2",
        github_token=os.getenv("GITHUB_TOKEN"),
    )

    metrics = analyzer.calculate_health_metrics(lookback_weeks=4, include_detailed=True)

    # Display detailed issue metrics
    print("\n" + "=" * 80)
    print("ISSUE METRICS")
    print("=" * 80)
    if metrics.issue_metrics:
        for key, value in metrics.issue_metrics.items():
            print(f"  {key:30s}: {value}")

    # Display detailed PR metrics
    print("\n" + "=" * 80)
    print("PULL REQUEST METRICS")
    print("=" * 80)
    if metrics.pr_metrics:
        for key, value in metrics.pr_metrics.items():
            print(f"  {key:30s}: {value}")

    # Display detailed contributor metrics
    print("\n" + "=" * 80)
    print("CONTRIBUTOR METRICS")
    print("=" * 80)
    if metrics.contributor_metrics:
        for key, value in metrics.contributor_metrics.items():
            print(f"  {key:30s}: {value}")

    print("=" * 80 + "\n")


def example_individual_calculators():
    """Example: Use individual metric calculators."""
    print("=" * 80)
    print("EXAMPLE 3: Individual Metric Calculators")
    print("=" * 80)

    analyzer = HealthMetricsAnalyzer(
        repo_owner="moai-adk",
        repo_name="agent-os-v2",
        github_token=os.getenv("GITHUB_TOKEN"),
    )

    # Calculate issue velocity
    print("\n1. Issue Velocity (issues closed per week)")
    velocity = analyzer.calculate_issue_velocity(lookback_weeks=4)
    print(f"   Result: {velocity:.2f} issues/week")

    # Calculate PR merge time
    print("\n2. PR Merge Time (average days to merge)")
    merge_time = analyzer.calculate_pr_merge_time(lookback_weeks=4)
    print(f"   Result: {merge_time:.2f} days")

    # Calculate stale count
    print("\n3. Stale Count (items not updated in 60+ days)")
    stale_count = analyzer.calculate_stale_count()
    print(f"   Result: {stale_count} stale items")

    # Calculate contributor activity
    print("\n4. Contributor Activity (unique contributors)")
    activity = analyzer.calculate_contributor_activity(lookback_weeks=4)
    print(f"   Result: {activity} active contributors")

    # Calculate test coverage trend
    print("\n5. Test Coverage Trend")
    coverage = analyzer.calculate_test_coverage_trend(lookback_weeks=4)
    print(f"   Result: {coverage:+.2f}% change")

    print("\n" + "=" * 80 + "\n")


def example_trend_analysis():
    """Example: Analyze health trends over time."""
    print("=" * 80)
    print("EXAMPLE 4: Health Trend Analysis")
    print("=" * 80)

    analyzer = HealthMetricsAnalyzer(
        repo_owner="moai-adk",
        repo_name="agent-os-v2",
        github_token=os.getenv("GITHUB_TOKEN"),
    )

    # Calculate current metrics
    current = analyzer.calculate_health_metrics(lookback_weeks=4)

    # Simulate previous metrics (in production, load from storage)
    previous = HealthMetrics(
        timestamp=datetime.now() - timedelta(weeks=4),
        issue_velocity=8.5,
        pr_merge_time=3.2,
        stale_count=15,
        contributor_activity=7,
        test_coverage_trend=0.0,
        health_score=65,
        trend=HealthTrend.STABLE,
    )

    # Analyze trend
    comparison = analyzer.analyze_trend(current, [previous])

    # Display comparison
    print("\n" + "=" * 80)
    print("HEALTH TREND COMPARISON")
    print("=" * 80)
    print(f"\nOverall Trend: {comparison.trend.value.upper()}")
    print(f"Health Score Change: {comparison.change_percentage:+.2f}%")
    print(f"  Previous: {comparison.previous.health_score}/100")
    print(f"  Current:  {comparison.current.health_score}/100")

    print(f"\nImprovements ({len(comparison.improvements)}):")
    for metric in comparison.improvements:
        print(f"  ✓ {metric}")

    print(f"\nDegradations ({len(comparison.degradations)}):")
    for metric in comparison.degradations:
        print(f"  ✗ {metric}")

    print("=" * 80 + "\n")


def example_export_metrics():
    """Example: Export metrics to dictionary for storage."""
    print("=" * 80)
    print("EXAMPLE 5: Export Metrics to Dictionary")
    print("=" * 80)

    analyzer = HealthMetricsAnalyzer(
        repo_owner="moai-adk",
        repo_name="agent-os-v2",
        github_token=os.getenv("GITHUB_TOKEN"),
    )

    metrics = analyzer.calculate_health_metrics(lookback_weeks=4)

    # Export to dictionary
    metrics_dict = metrics.to_dict()

    print("\nMetrics exported to dictionary:")
    print("-" * 80)
    import json
    print(json.dumps(metrics_dict, indent=2))
    print("-" * 80)

    print("\nThis can be saved to:")
    print("  - JSON file (.moai/reports/repo/health-metrics.json)")
    print("  - Database (PostgreSQL, MongoDB)")
    print("  - Time-series DB (InfluxDB, Prometheus)")
    print("=" * 80 + "\n")


def example_custom_stale_threshold():
    """Example: Use custom stale threshold."""
    print("=" * 80)
    print("EXAMPLE 6: Custom Stale Threshold")
    print("=" * 80)

    # 30-day threshold (more aggressive)
    analyzer_30 = HealthMetricsAnalyzer(
        repo_owner="moai-adk",
        repo_name="agent-os-v2",
        github_token=os.getenv("GITHUB_TOKEN"),
        stale_days=30,
    )

    # 90-day threshold (more lenient)
    analyzer_90 = HealthMetricsAnalyzer(
        repo_owner="moai-adk",
        repo_name="agent-os-v2",
        github_token=os.getenv("GITHUB_TOKEN"),
        stale_days=90,
    )

    stale_30 = analyzer_30.calculate_stale_count()
    stale_90 = analyzer_90.calculate_stale_count()

    print(f"\nStale items (30-day threshold): {stale_30}")
    print(f"Stale items (90-day threshold): {stale_90}")
    print(f"Difference: {stale_30 - stale_90} items")
    print("\n" + "=" * 80 + "\n")


def main():
    """Run all examples."""
    print("\n" + "=" * 80)
    print("GITHUB HEALTH METRICS SYSTEM - PRD-06")
    print("=" * 80 + "\n")

    try:
        # Example 1: Basic health metrics
        metrics = example_basic_health_metrics()

        # Example 2: Detailed metrics breakdown
        example_detailed_metrics()

        # Example 3: Individual calculators
        example_individual_calculators()

        # Example 4: Trend analysis
        example_trend_analysis()

        # Example 5: Export metrics
        example_export_metrics()

        # Example 6: Custom stale threshold
        example_custom_stale_threshold()

        print("\n" + "=" * 80)
        print("ALL EXAMPLES COMPLETED SUCCESSFULLY")
        print("=" * 80 + "\n")

    except ImportError as e:
        print(f"\nError: {e}")
        print("Please install PyGithub: pip install PyGithub")
    except ValueError as e:
        print(f"\nError: {e}")
        print("Please set GITHUB_TOKEN environment variable")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
