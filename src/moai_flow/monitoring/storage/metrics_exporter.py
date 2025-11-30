#!/usr/bin/env python3
"""
MetricsExporter - Multi-Format Metrics Export for Phase 7

Provides comprehensive metrics export in 3 formats:
- JSON: Full metric dump with nested structure
- CSV: Flat table format (Excel/Google Sheets compatible)
- Prometheus: Prometheus metric format for monitoring

Features:
- Configurable time range export
- Nested JSON structure (task → agent → swarm)
- CSV headers and type conversion
- Prometheus labels and timestamps
- Optional Grafana JSON data source support
- Streaming export for large datasets

Export Formats:
1. JSON: Complete metric dump with metadata
2. CSV: Flat table with all fields
3. Prometheus: Time-series format with labels

LOC: ~300
"""

import csv
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from io import StringIO
from pathlib import Path
from typing import Any, Dict, List, Optional, TextIO, Union

from moai_flow.monitoring.storage.metrics_query import (
    MetricsQuery,
    QueryFilter,
)


# ============================================================================
# Export Configuration Classes
# ============================================================================


class ExportFormat(str, Enum):
    """Export format types."""

    JSON = "json"
    CSV = "csv"
    PROMETHEUS = "prometheus"
    GRAFANA = "grafana"  # Grafana JSON data source format


@dataclass
class ExportConfig:
    """
    Export configuration.

    Attributes:
        format: Export format
        output_path: Output file path (None for string output)
        time_range_hours: Time range in hours (None for all data)
        include_metadata: Include metadata fields
        pretty_print: Pretty print JSON output
        compression: Enable gzip compression for output
    """

    format: ExportFormat = ExportFormat.JSON
    output_path: Optional[Path] = None
    time_range_hours: Optional[int] = None
    include_metadata: bool = True
    pretty_print: bool = True
    compression: bool = False


# ============================================================================
# MetricsExporter Implementation
# ============================================================================


class MetricsExporter:
    """
    Multi-format metrics exporter.

    Supports 3 export formats:
    - JSON: Full nested structure with all metrics
    - CSV: Flat table format for spreadsheet import
    - Prometheus: Prometheus metric format
    - Grafana: Grafana JSON data source format (optional)

    Example:
        >>> exporter = MetricsExporter()
        >>> config = ExportConfig(
        ...     format=ExportFormat.JSON,
        ...     output_path=Path("metrics_export.json"),
        ...     time_range_hours=24
        ... )
        >>> exporter.export(config)
        >>> # Export to CSV
        >>> csv_config = ExportConfig(format=ExportFormat.CSV)
        >>> csv_output = exporter.export_to_string(csv_config)
    """

    def __init__(self, query: Optional[MetricsQuery] = None):
        """
        Initialize metrics exporter.

        Args:
            query: MetricsQuery instance (creates new if None)
        """
        self.query = query or MetricsQuery()
        self.logger = logging.getLogger(__name__)

    # ========================================================================
    # Main Export Methods
    # ========================================================================

    def export(self, config: ExportConfig) -> str:
        """
        Export metrics to file or string.

        Args:
            config: Export configuration

        Returns:
            Export result (file path or exported string)
        """
        # Export to string
        output = self.export_to_string(config)

        # Write to file if path specified
        if config.output_path:
            mode = "w"
            if config.compression:
                import gzip

                with gzip.open(str(config.output_path) + ".gz", "wt") as f:
                    f.write(output)
                self.logger.info(
                    f"Exported metrics to {config.output_path}.gz "
                    f"({len(output)} chars)"
                )
                return str(config.output_path) + ".gz"
            else:
                config.output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(config.output_path, mode) as f:
                    f.write(output)
                self.logger.info(
                    f"Exported metrics to {config.output_path} " f"({len(output)} chars)"
                )
                return str(config.output_path)

        return output

    def export_to_string(self, config: ExportConfig) -> str:
        """
        Export metrics to string.

        Args:
            config: Export configuration

        Returns:
            Exported metrics as string
        """
        # Get time range filter
        filter = self._get_time_filter(config)

        # Export based on format
        if config.format == ExportFormat.JSON:
            return self._export_json(filter, config)
        elif config.format == ExportFormat.CSV:
            return self._export_csv(filter, config)
        elif config.format == ExportFormat.PROMETHEUS:
            return self._export_prometheus(filter, config)
        elif config.format == ExportFormat.GRAFANA:
            return self._export_grafana(filter, config)
        else:
            raise ValueError(f"Unsupported export format: {config.format}")

    # ========================================================================
    # JSON Export
    # ========================================================================

    def _export_json(self, filter: QueryFilter, config: ExportConfig) -> str:
        """
        Export metrics in JSON format.

        JSON Structure:
        {
            "export_info": {...},
            "task_metrics": [...],
            "agent_metrics": [...],
            "swarm_metrics": [...],
            "summary": {...}
        }
        """
        # Get all metrics
        task_metrics = self.query.get_task_metrics(filter)
        agent_metrics = self.query.get_agent_metrics(filter)
        swarm_metrics = self.query.get_swarm_metrics(filter)
        summary = self.query.get_summary_stats(filter)

        # Remove metadata if not requested
        if not config.include_metadata:
            for metric in task_metrics + agent_metrics + swarm_metrics:
                metric.pop("metadata", None)

        # Build export structure
        export_data = {
            "export_info": {
                "format": "json",
                "exported_at": datetime.now().isoformat(),
                "time_range": {
                    "start": filter.start_time.isoformat()
                    if filter.start_time
                    else None,
                    "end": filter.end_time.isoformat() if filter.end_time else None,
                },
                "record_counts": {
                    "task_metrics": len(task_metrics),
                    "agent_metrics": len(agent_metrics),
                    "swarm_metrics": len(swarm_metrics),
                },
            },
            "task_metrics": task_metrics,
            "agent_metrics": agent_metrics,
            "swarm_metrics": swarm_metrics,
            "summary": summary,
        }

        # Serialize to JSON
        indent = 2 if config.pretty_print else None
        return json.dumps(export_data, indent=indent, default=str)

    # ========================================================================
    # CSV Export
    # ========================================================================

    def _export_csv(self, filter: QueryFilter, config: ExportConfig) -> str:
        """
        Export metrics in CSV format.

        CSV Format:
        metric_type,timestamp,agent_id,task_id,duration_ms,tokens_used,success,...
        task,2025-11-29T10:00:00,agent_001,task_001,1500,500,1,...
        """
        output = StringIO()
        writer = csv.writer(output)

        # Get all metrics
        task_metrics = self.query.get_task_metrics(filter)
        agent_metrics = self.query.get_agent_metrics(filter)
        swarm_metrics = self.query.get_swarm_metrics(filter)

        # Define CSV headers
        headers = [
            "metric_type",
            "timestamp",
            "timestamp_iso",
            "agent_id",
            "task_id",
            "swarm_id",
            "duration_ms",
            "tokens_used",
            "success",
            "metric_name",
            "value",
        ]

        if config.include_metadata:
            headers.append("metadata")

        writer.writerow(headers)

        # Write task metrics
        for metric in task_metrics:
            row = [
                "task",
                metric.get("timestamp"),
                datetime.fromtimestamp(metric["timestamp"]).isoformat()
                if metric.get("timestamp")
                else "",
                metric.get("agent_id", ""),
                metric.get("task_id", ""),
                "",  # swarm_id
                metric.get("duration_ms", ""),
                metric.get("tokens_used", ""),
                metric.get("success", ""),
                "",  # metric_name
                "",  # value
            ]

            if config.include_metadata:
                row.append(json.dumps(metric.get("metadata", {})))

            writer.writerow(row)

        # Write agent metrics
        for metric in agent_metrics:
            row = [
                "agent",
                metric.get("timestamp"),
                datetime.fromtimestamp(metric["timestamp"]).isoformat()
                if metric.get("timestamp")
                else "",
                metric.get("agent_id", ""),
                "",  # task_id
                "",  # swarm_id
                "",  # duration_ms
                "",  # tokens_used
                "",  # success
                metric.get("metric_type", ""),
                metric.get("value", ""),
            ]

            if config.include_metadata:
                row.append(json.dumps(metric.get("metadata", {})))

            writer.writerow(row)

        # Write swarm metrics
        for metric in swarm_metrics:
            row = [
                "swarm",
                metric.get("timestamp"),
                datetime.fromtimestamp(metric["timestamp"]).isoformat()
                if metric.get("timestamp")
                else "",
                "",  # agent_id
                "",  # task_id
                metric.get("swarm_id", ""),
                "",  # duration_ms
                "",  # tokens_used
                "",  # success
                metric.get("metric_type", ""),
                metric.get("value", ""),
            ]

            if config.include_metadata:
                row.append(json.dumps(metric.get("metadata", {})))

            writer.writerow(row)

        return output.getvalue()

    # ========================================================================
    # Prometheus Export
    # ========================================================================

    def _export_prometheus(self, filter: QueryFilter, config: ExportConfig) -> str:
        """
        Export metrics in Prometheus format.

        Prometheus Format:
        # TYPE moai_task_duration_ms gauge
        moai_task_duration_ms{agent_id="agent_001",task_id="task_001"} 1500 1732876800000
        """
        output = StringIO()

        # Get all metrics
        task_metrics = self.query.get_task_metrics(filter)
        agent_metrics = self.query.get_agent_metrics(filter)
        swarm_metrics = self.query.get_swarm_metrics(filter)

        # Export task metrics
        output.write("# TYPE moai_task_duration_ms gauge\n")
        for metric in task_metrics:
            labels = self._format_prometheus_labels(
                {
                    "agent_id": metric.get("agent_id", ""),
                    "task_id": metric.get("task_id", ""),
                    "success": str(metric.get("success", 0)),
                }
            )
            timestamp_ms = metric.get("timestamp", 0) * 1000
            output.write(
                f"moai_task_duration_ms{labels} "
                f"{metric.get('duration_ms', 0)} {timestamp_ms}\n"
            )

        output.write("\n# TYPE moai_task_tokens_used gauge\n")
        for metric in task_metrics:
            labels = self._format_prometheus_labels(
                {
                    "agent_id": metric.get("agent_id", ""),
                    "task_id": metric.get("task_id", ""),
                }
            )
            timestamp_ms = metric.get("timestamp", 0) * 1000
            output.write(
                f"moai_task_tokens_used{labels} "
                f"{metric.get('tokens_used', 0)} {timestamp_ms}\n"
            )

        # Export agent metrics
        output.write("\n# TYPE moai_agent_metric gauge\n")
        for metric in agent_metrics:
            labels = self._format_prometheus_labels(
                {
                    "agent_id": metric.get("agent_id", ""),
                    "metric_type": metric.get("metric_type", ""),
                }
            )
            timestamp_ms = metric.get("timestamp", 0) * 1000
            output.write(
                f"moai_agent_metric{labels} "
                f"{metric.get('value', 0)} {timestamp_ms}\n"
            )

        # Export swarm metrics
        output.write("\n# TYPE moai_swarm_metric gauge\n")
        for metric in swarm_metrics:
            labels = self._format_prometheus_labels(
                {
                    "swarm_id": metric.get("swarm_id", ""),
                    "metric_type": metric.get("metric_type", ""),
                }
            )
            timestamp_ms = metric.get("timestamp", 0) * 1000
            output.write(
                f"moai_swarm_metric{labels} "
                f"{metric.get('value', 0)} {timestamp_ms}\n"
            )

        return output.getvalue()

    def _format_prometheus_labels(self, labels: Dict[str, str]) -> str:
        """Format Prometheus labels."""
        if not labels:
            return ""

        label_str = ",".join(
            f'{key}="{value}"' for key, value in labels.items() if value
        )
        return f"{{{label_str}}}"

    # ========================================================================
    # Grafana Export (Optional)
    # ========================================================================

    def _export_grafana(self, filter: QueryFilter, config: ExportConfig) -> str:
        """
        Export metrics in Grafana JSON data source format.

        Grafana Format:
        [
          {
            "target": "agent_001.duration",
            "datapoints": [[1500, 1732876800000], ...]
          }
        ]
        """
        # Get all metrics
        task_metrics = self.query.get_task_metrics(filter)

        # Group by agent_id
        agent_datapoints: Dict[str, List[List[Union[int, float]]]] = {}

        for metric in task_metrics:
            agent_id = metric.get("agent_id", "unknown")
            duration_ms = metric.get("duration_ms", 0)
            timestamp_ms = metric.get("timestamp", 0) * 1000

            target = f"{agent_id}.duration_ms"

            if target not in agent_datapoints:
                agent_datapoints[target] = []

            agent_datapoints[target].append([duration_ms, timestamp_ms])

        # Build Grafana response
        grafana_data = [
            {"target": target, "datapoints": datapoints}
            for target, datapoints in agent_datapoints.items()
        ]

        return json.dumps(grafana_data, indent=2 if config.pretty_print else None)

    # ========================================================================
    # Utility Methods
    # ========================================================================

    def _get_time_filter(self, config: ExportConfig) -> QueryFilter:
        """Get query filter from export config."""
        filter = QueryFilter()

        if config.time_range_hours:
            filter.end_time = datetime.now()
            filter.start_time = filter.end_time - timedelta(
                hours=config.time_range_hours
            )

        return filter

    def close(self) -> None:
        """Close query interface."""
        if self.query:
            self.query.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
        return False


# ============================================================================
# Example Usage
# ============================================================================

if __name__ == "__main__":
    print("=== MetricsExporter Example Usage ===\n")

    # Initialize exporter
    exporter = MetricsExporter()
    print("✓ Exporter initialized")

    # Example 1: Export to JSON
    print("\n--- Example 1: Export to JSON ---")
    json_config = ExportConfig(
        format=ExportFormat.JSON,
        output_path=Path(".swarm/exports/metrics_export.json"),
        time_range_hours=24,
        pretty_print=True,
    )
    json_output = exporter.export(json_config)
    print(f"✓ Exported to: {json_output}")

    # Example 2: Export to CSV
    print("\n--- Example 2: Export to CSV ---")
    csv_config = ExportConfig(
        format=ExportFormat.CSV,
        output_path=Path(".swarm/exports/metrics_export.csv"),
        time_range_hours=24,
    )
    csv_output = exporter.export(csv_config)
    print(f"✓ Exported to: {csv_output}")

    # Example 3: Export to Prometheus
    print("\n--- Example 3: Export to Prometheus ---")
    prom_config = ExportConfig(
        format=ExportFormat.PROMETHEUS,
        output_path=Path(".swarm/exports/metrics_export.prom"),
        time_range_hours=1,
    )
    prom_output = exporter.export(prom_config)
    print(f"✓ Exported to: {prom_output}")

    # Example 4: Export to string (no file)
    print("\n--- Example 4: Export to String ---")
    string_config = ExportConfig(format=ExportFormat.JSON, time_range_hours=1)
    json_string = exporter.export_to_string(string_config)
    print(f"✓ Generated JSON string ({len(json_string)} chars)")

    # Example 5: Grafana format
    print("\n--- Example 5: Grafana Format ---")
    grafana_config = ExportConfig(
        format=ExportFormat.GRAFANA,
        output_path=Path(".swarm/exports/metrics_grafana.json"),
        time_range_hours=24,
    )
    grafana_output = exporter.export(grafana_config)
    print(f"✓ Exported Grafana format to: {grafana_output}")

    # Example 6: Compressed export
    print("\n--- Example 6: Compressed Export ---")
    compressed_config = ExportConfig(
        format=ExportFormat.JSON,
        output_path=Path(".swarm/exports/metrics_compressed.json"),
        time_range_hours=24,
        compression=True,
    )
    compressed_output = exporter.export(compressed_config)
    print(f"✓ Exported compressed to: {compressed_output}")

    # Close
    exporter.close()
    print("\n✅ MetricsExporter demonstration complete")
