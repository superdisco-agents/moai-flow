#!/usr/bin/env python3
"""
Pattern Analysis Script - PRD-05 Phase 2

Analyze collected patterns and generate reports WITHOUT ML.

Features:
- Analyze agent performance over time
- Identify error patterns
- Detect common task patterns
- Generate actionable recommendations
- Create JSON and Markdown reports
- Scheduled analysis support

Usage:
    python -m moai_flow.scripts.analyze_patterns
    python -m moai_flow.scripts.analyze_patterns --days 30
    python -m moai_flow.scripts.analyze_patterns --format markdown
    python -m moai_flow.scripts.analyze_patterns --output .moai/reports/patterns/

Version: 1.0.0
Phase: PRD-05 Phase 2
"""

import argparse
import json
import logging
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from statistics import mean, median

from moai_flow.monitoring.metrics_collector import (
    MetricsCollector,
    MetricsStorage,
    TaskResult
)


# ============================================================================
# Pattern Analyzer Class
# ============================================================================

class PatternAnalyzer:
    """
    Analyze collected patterns and generate reports.

    No ML - pure statistical analysis.
    """

    def __init__(self, collector: MetricsCollector):
        """
        Initialize PatternAnalyzer

        Args:
            collector: MetricsCollector instance with metrics data
        """
        self.collector = collector
        self.logger = logging.getLogger(__name__)

    def analyze_agent_performance(
        self,
        days: int = 7
    ) -> Dict[str, Dict[str, Any]]:
        """
        Analyze agent performance over time period.

        Args:
            days: Number of days to analyze (default: 7)

        Returns:
            Dictionary with agent performance data:
            {
                "expert-backend": {
                    "tasks": 45,
                    "success_rate": 0.89,
                    "avg_duration_ms": 55000,
                    "total_files_created": 135
                },
                "manager-tdd": {
                    "tasks": 32,
                    "success_rate": 1.0,
                    "avg_duration_ms": 38000
                }
            }
        """
        self.logger.info(f"Analyzing agent performance for last {days} days")

        # Calculate time range
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)

        # Collect all unique agent IDs from task metrics
        with self.collector._lock:
            all_metrics = list(self.collector._task_metrics)

        # Filter by time range
        metrics_in_range = [
            m for m in all_metrics
            if start_time <= datetime.fromisoformat(m.timestamp.replace("Z", "")) <= end_time
        ]

        # Group by agent
        agent_metrics = defaultdict(list)
        for metric in metrics_in_range:
            agent_metrics[metric.agent_id].append(metric)

        # Analyze each agent
        agent_performance = {}
        for agent_id, metrics in agent_metrics.items():
            if not metrics:
                continue

            # Calculate statistics
            total_tasks = len(metrics)
            successful_tasks = sum(1 for m in metrics if m.result == TaskResult.SUCCESS)
            success_rate = successful_tasks / total_tasks if total_tasks > 0 else 0.0

            durations = [m.duration_ms for m in metrics]
            avg_duration_ms = mean(durations) if durations else 0.0

            total_files_created = sum(m.files_changed for m in metrics)
            total_tokens = sum(m.tokens_used for m in metrics)

            agent_performance[agent_id] = {
                "tasks": total_tasks,
                "success_rate": success_rate,
                "avg_duration_ms": avg_duration_ms,
                "median_duration_ms": median(durations) if durations else 0.0,
                "total_files_created": total_files_created,
                "total_tokens_used": total_tokens
            }

        self.logger.info(f"Analyzed {len(agent_performance)} agents")
        return agent_performance

    def analyze_error_patterns(
        self,
        days: int = 7
    ) -> Dict[str, int]:
        """
        Analyze error frequency.

        Args:
            days: Number of days to analyze (default: 7)

        Returns:
            Dictionary with error types and counts:
            {
                "TypeError": 12,
                "ImportError": 5,
                "NetworkError": 3
            }
        """
        self.logger.info(f"Analyzing error patterns for last {days} days")

        # Calculate time range
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)

        # Get failed tasks
        with self.collector._lock:
            all_metrics = list(self.collector._task_metrics)

        # Filter by time and failures
        failed_tasks = [
            m for m in all_metrics
            if (start_time <= datetime.fromisoformat(m.timestamp.replace("Z", "")) <= end_time
                and m.result in [TaskResult.FAILURE, TaskResult.TIMEOUT])
        ]

        # Extract error types from metadata
        error_counts = defaultdict(int)
        for task in failed_tasks:
            error_type = task.metadata.get("error_type", "UnknownError")
            error_counts[error_type] += 1

        # Sort by frequency
        sorted_errors = dict(sorted(error_counts.items(), key=lambda x: x[1], reverse=True))

        self.logger.info(f"Found {len(sorted_errors)} unique error types")
        return sorted_errors

    def analyze_task_patterns(
        self,
        days: int = 7
    ) -> List[Dict[str, Any]]:
        """
        Identify common task patterns.

        Args:
            days: Number of days to analyze (default: 7)

        Returns:
            List of task patterns:
            [
                {
                    "pattern": "api_implementation",
                    "occurrences": 12,
                    "avg_duration_ms": 45000,
                    "success_rate": 0.92
                }
            ]
        """
        self.logger.info(f"Analyzing task patterns for last {days} days")

        # Calculate time range
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)

        # Get all tasks in range
        with self.collector._lock:
            all_metrics = list(self.collector._task_metrics)

        metrics_in_range = [
            m for m in all_metrics
            if start_time <= datetime.fromisoformat(m.timestamp.replace("Z", "")) <= end_time
        ]

        # Group by pattern (extracted from metadata)
        pattern_groups = defaultdict(list)
        for metric in metrics_in_range:
            pattern_name = metric.metadata.get("pattern", "unknown")
            pattern_groups[pattern_name].append(metric)

        # Analyze each pattern
        pattern_analysis = []
        for pattern_name, metrics in pattern_groups.items():
            if not metrics:
                continue

            occurrences = len(metrics)
            successful = sum(1 for m in metrics if m.result == TaskResult.SUCCESS)
            success_rate = successful / occurrences if occurrences > 0 else 0.0

            durations = [m.duration_ms for m in metrics]
            avg_duration_ms = mean(durations) if durations else 0.0

            pattern_analysis.append({
                "pattern": pattern_name,
                "occurrences": occurrences,
                "avg_duration_ms": avg_duration_ms,
                "success_rate": success_rate
            })

        # Sort by occurrences
        pattern_analysis.sort(key=lambda x: x["occurrences"], reverse=True)

        self.logger.info(f"Identified {len(pattern_analysis)} task patterns")
        return pattern_analysis

    def generate_recommendations(
        self,
        analysis: Dict[str, Any]
    ) -> List[str]:
        """
        Generate actionable recommendations.

        Args:
            analysis: Combined analysis results with keys:
                - agent_performance
                - errors
                - tasks

        Returns:
            List of recommendation strings:
            [
                "expert-backend tasks taking 45% longer than average",
                "Consider breaking API tasks into smaller units",
                "TypeError errors increasing - review type hints"
            ]
        """
        self.logger.info("Generating recommendations")

        recommendations = []

        # Agent performance recommendations
        agent_perf = analysis.get("agent_performance", {})
        if agent_perf:
            # Calculate overall average duration
            all_durations = [data["avg_duration_ms"] for data in agent_perf.values()]
            if all_durations:
                overall_avg = mean(all_durations)

                # Find slow agents
                for agent_id, data in agent_perf.items():
                    if data["avg_duration_ms"] > overall_avg * 1.3:
                        pct_slower = ((data["avg_duration_ms"] / overall_avg) - 1) * 100
                        recommendations.append(
                            f"{agent_id} tasks taking {pct_slower:.0f}% longer than average "
                            f"({data['avg_duration_ms']:.0f}ms vs {overall_avg:.0f}ms)"
                        )

                # Find low success rate agents
                for agent_id, data in agent_perf.items():
                    if data["success_rate"] < 0.85:
                        recommendations.append(
                            f"{agent_id} has low success rate ({data['success_rate']:.1%}) - "
                            f"review error handling and test coverage"
                        )

        # Error pattern recommendations
        errors = analysis.get("errors", {})
        if errors:
            # Top errors
            sorted_errors = sorted(errors.items(), key=lambda x: x[1], reverse=True)
            top_errors = sorted_errors[:3]

            for error_type, count in top_errors:
                if count > 5:
                    recommendations.append(
                        f"{error_type} errors frequent ({count} occurrences) - "
                        f"implement specific handling or prevention"
                    )

        # Task pattern recommendations
        tasks = analysis.get("tasks", [])
        if tasks:
            # Find patterns with low success rate
            for pattern in tasks:
                if pattern["success_rate"] < 0.8 and pattern["occurrences"] > 3:
                    recommendations.append(
                        f"{pattern['pattern']} pattern has low success rate "
                        f"({pattern['success_rate']:.1%}) - review implementation"
                    )

                # Find long-running patterns
                if pattern["avg_duration_ms"] > 60000 and pattern["occurrences"] > 3:
                    recommendations.append(
                        f"{pattern['pattern']} pattern takes {pattern['avg_duration_ms']/1000:.1f}s avg - "
                        f"consider breaking into smaller tasks"
                    )

        # General recommendations
        if not recommendations:
            recommendations.append("No critical issues detected - system performance is healthy")

        self.logger.info(f"Generated {len(recommendations)} recommendations")
        return recommendations


# ============================================================================
# Report Generator Class
# ============================================================================

class ReportGenerator:
    """Generate pattern analysis reports"""

    def __init__(self, analyzer: PatternAnalyzer):
        """
        Initialize ReportGenerator

        Args:
            analyzer: PatternAnalyzer instance
        """
        self.analyzer = analyzer
        self.logger = logging.getLogger(__name__)

    def generate_weekly_report(self) -> Dict[str, Any]:
        """
        Generate weekly pattern report.

        Returns:
            Complete report dictionary:
            {
                "period": "weekly",
                "date_range": "2025-11-24 to 2025-11-30",
                "summary": {
                    "total_tasks": 156,
                    "success_rate": 0.92,
                    "avg_duration_ms": 42000
                },
                "by_agent": {...},
                "patterns_observed": [...],
                "recommendations": [...]
            }
        """
        self.logger.info("Generating weekly report")

        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)

        # Analyze
        agent_perf = self.analyzer.analyze_agent_performance(days=7)
        error_patterns = self.analyzer.analyze_error_patterns(days=7)
        task_patterns = self.analyzer.analyze_task_patterns(days=7)

        # Generate summary
        if agent_perf:
            total_tasks = sum(data["tasks"] for data in agent_perf.values())
            if total_tasks > 0:
                avg_success = sum(
                    data["success_rate"] * data["tasks"]
                    for data in agent_perf.values()
                ) / total_tasks
                avg_duration = sum(
                    data["avg_duration_ms"] * data["tasks"]
                    for data in agent_perf.values()
                ) / total_tasks
            else:
                avg_success = 0.0
                avg_duration = 0.0
        else:
            total_tasks = 0
            avg_success = 0.0
            avg_duration = 0.0

        # Recommendations
        recommendations = self.analyzer.generate_recommendations({
            "agent_performance": agent_perf,
            "errors": error_patterns,
            "tasks": task_patterns
        })

        report = {
            "period": "weekly",
            "date_range": f"{start_date.date()} to {end_date.date()}",
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total_tasks": total_tasks,
                "success_rate": avg_success,
                "avg_duration_ms": avg_duration
            },
            "by_agent": agent_perf,
            "errors": error_patterns,
            "patterns_observed": task_patterns,
            "recommendations": recommendations
        }

        self.logger.info("Weekly report generated successfully")
        return report

    def save_report(
        self,
        report: Dict[str, Any],
        output_path: str = ".moai/reports/patterns/",
        format: str = "json"
    ) -> str:
        """
        Save report to file (JSON + Markdown)

        Args:
            report: Report dictionary
            output_path: Output directory path
            format: Output format ("json", "markdown", or "both")

        Returns:
            Path to saved report file(s)
        """
        self.logger.info(f"Saving report to {output_path} (format: {format})")

        # Create output directory
        output_dir = Path(output_path)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"pattern-analysis-{timestamp}"

        saved_files = []

        # Save JSON format
        if format in ["json", "both"]:
            json_file = output_dir / f"{base_filename}.json"
            with open(json_file, 'w') as f:
                json.dump(report, f, indent=2)
            saved_files.append(str(json_file))
            self.logger.info(f"JSON report saved to {json_file}")

        # Save Markdown format
        if format in ["markdown", "both"]:
            md_file = output_dir / f"{base_filename}.md"
            markdown_content = self._generate_markdown(report)
            with open(md_file, 'w') as f:
                f.write(markdown_content)
            saved_files.append(str(md_file))
            self.logger.info(f"Markdown report saved to {md_file}")

        return ", ".join(saved_files)

    def _generate_markdown(self, report: Dict[str, Any]) -> str:
        """
        Generate Markdown report from report dictionary

        Args:
            report: Report dictionary

        Returns:
            Markdown formatted string
        """
        md_lines = [
            f"# Pattern Analysis Report",
            f"",
            f"**Period**: {report['period']}  ",
            f"**Date Range**: {report['date_range']}  ",
            f"**Generated**: {report['generated_at']}",
            f"",
            f"## Summary",
            f"",
            f"- **Total Tasks**: {report['summary']['total_tasks']}",
            f"- **Success Rate**: {report['summary']['success_rate']:.1%}",
            f"- **Average Duration**: {report['summary']['avg_duration_ms']/1000:.1f}s",
            f"",
            f"## Agent Performance",
            f""
        ]

        # Agent performance table
        if report['by_agent']:
            md_lines.extend([
                f"| Agent ID | Tasks | Success Rate | Avg Duration | Files Created |",
                f"|----------|-------|--------------|--------------|---------------|"
            ])

            for agent_id, data in report['by_agent'].items():
                md_lines.append(
                    f"| {agent_id} | {data['tasks']} | "
                    f"{data['success_rate']:.1%} | "
                    f"{data['avg_duration_ms']/1000:.1f}s | "
                    f"{data['total_files_created']} |"
                )
            md_lines.append("")

        # Error patterns
        if report['errors']:
            md_lines.extend([
                f"## Error Patterns",
                f""
            ])
            for error_type, count in report['errors'].items():
                md_lines.append(f"- **{error_type}**: {count} occurrences")
            md_lines.append("")

        # Task patterns
        if report['patterns_observed']:
            md_lines.extend([
                f"## Task Patterns",
                f"",
                f"| Pattern | Occurrences | Avg Duration | Success Rate |",
                f"|---------|-------------|--------------|--------------|"
            ])

            for pattern in report['patterns_observed']:
                md_lines.append(
                    f"| {pattern['pattern']} | {pattern['occurrences']} | "
                    f"{pattern['avg_duration_ms']/1000:.1f}s | "
                    f"{pattern['success_rate']:.1%} |"
                )
            md_lines.append("")

        # Recommendations
        md_lines.extend([
            f"## Recommendations",
            f""
        ])

        for i, rec in enumerate(report['recommendations'], 1):
            md_lines.append(f"{i}. {rec}")

        md_lines.append("")

        return "\n".join(md_lines)


# ============================================================================
# CLI Script
# ============================================================================

def main():
    """
    Pattern Analysis CLI

    Usage:
        python -m moai_flow.scripts.analyze_patterns
        python -m moai_flow.scripts.analyze_patterns --days 30
        python -m moai_flow.scripts.analyze_patterns --format markdown
    """
    parser = argparse.ArgumentParser(
        description="Analyze MoAI patterns",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--days",
        type=int,
        default=7,
        help="Analysis period in days (default: 7)"
    )
    parser.add_argument(
        "--format",
        choices=["json", "markdown", "both"],
        default="both",
        help="Report format (default: both)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default=".moai/reports/patterns/",
        help="Output directory (default: .moai/reports/patterns/)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )

    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    logger = logging.getLogger(__name__)

    logger.info("=" * 60)
    logger.info("Pattern Analysis Script - PRD-05 Phase 2")
    logger.info("=" * 60)

    # Initialize
    logger.info("Initializing metrics collector...")
    storage = MetricsStorage()
    collector = MetricsCollector(storage, async_mode=False)

    logger.info("Initializing pattern analyzer...")
    analyzer = PatternAnalyzer(collector)

    logger.info("Initializing report generator...")
    reporter = ReportGenerator(analyzer)

    # Generate report
    logger.info(f"Generating {args.days}-day analysis report...")
    report = reporter.generate_weekly_report()

    # Save report
    logger.info(f"Saving report to {args.output}...")
    output_file = reporter.save_report(report, args.output, args.format)

    logger.info("=" * 60)
    logger.info(f"Report generated: {output_file}")
    logger.info("=" * 60)

    # Print summary
    print(f"\nSummary ({args.days} days):")
    print(f"  Total tasks: {report['summary']['total_tasks']}")
    print(f"  Success rate: {report['summary']['success_rate']:.1%}")
    print(f"  Avg duration: {report['summary']['avg_duration_ms']/1000:.1f}s")

    print(f"\nTop recommendations:")
    for i, rec in enumerate(report['recommendations'][:3], 1):
        print(f"  {i}. {rec}")

    print(f"\nFull report saved to: {output_file}")

    logger.info("Analysis complete")


if __name__ == "__main__":
    main()


# ============================================================================
# Module Exports
# ============================================================================

__all__ = [
    "PatternAnalyzer",
    "ReportGenerator",
    "main"
]
