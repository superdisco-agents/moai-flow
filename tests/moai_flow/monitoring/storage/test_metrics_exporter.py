#!/usr/bin/env python3
"""
Tests for MetricsExporter - Multi-Format Metrics Export

Comprehensive test coverage (target: 90%+):
- JSON export format
- CSV export format
- Prometheus export format
- Grafana export format (optional)
- File output and string output
- Compression support

Test Categories:
1. JSON Export
2. CSV Export
3. Prometheus Export
4. Grafana Export
5. File Operations
6. Compression
7. Edge Cases
"""

import json
import csv
import pytest
import tempfile
from datetime import datetime, timedelta
from io import StringIO
from pathlib import Path

from moai_flow.monitoring.storage.metrics_persistence import MetricsPersistence
from moai_flow.monitoring.storage.metrics_exporter import (
    MetricsExporter,
    ExportFormat,
    ExportConfig,
)


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def temp_dir():
    """Create temporary directory for export files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def populated_db(temp_dir):
    """Create and populate database with test data."""
    db_path = temp_dir / "test_metrics.db"
    persistence = MetricsPersistence(db_path=db_path)

    # Write test data
    now = datetime.now()
    for i in range(20):
        persistence.write_task_metric(
            task_id=f"task_{i:03d}",
            agent_id=f"agent_{i % 3}",
            duration_ms=1000 + i * 100,
            tokens_used=500 + i * 50,
            success=i % 5 != 0,
            timestamp=now - timedelta(minutes=20 - i),
        )

    persistence.flush()
    persistence.close()

    return db_path


@pytest.fixture
def exporter(populated_db):
    """Create MetricsExporter instance for testing."""
    exporter = MetricsExporter()
    # Override query to use test database
    from moai_flow.monitoring.storage.metrics_query import MetricsQuery

    exporter.query = MetricsQuery(db_path=populated_db)

    yield exporter

    exporter.close()


# ============================================================================
# Test Category 1: JSON Export
# ============================================================================


class TestJSONExport:
    """Test JSON export format."""

    def test_json_export_to_string(self, exporter):
        """Test JSON export to string."""
        config = ExportConfig(format=ExportFormat.JSON, pretty_print=True)

        output = exporter.export_to_string(config)

        # Verify valid JSON
        data = json.loads(output)

        # Verify structure
        assert "export_info" in data
        assert "task_metrics" in data
        assert "agent_metrics" in data
        assert "swarm_metrics" in data
        assert "summary" in data

        # Verify export info
        assert data["export_info"]["format"] == "json"
        assert "exported_at" in data["export_info"]
        assert "time_range" in data["export_info"]
        assert "record_counts" in data["export_info"]

    def test_json_export_with_metadata(self, exporter):
        """Test JSON export with metadata."""
        config = ExportConfig(
            format=ExportFormat.JSON, include_metadata=True, pretty_print=True
        )

        output = exporter.export_to_string(config)
        data = json.loads(output)

        # Metadata should be included
        if data["task_metrics"]:
            first_metric = data["task_metrics"][0]
            assert "metadata" in first_metric

    def test_json_export_without_metadata(self, exporter):
        """Test JSON export without metadata."""
        config = ExportConfig(
            format=ExportFormat.JSON, include_metadata=False, pretty_print=True
        )

        output = exporter.export_to_string(config)
        data = json.loads(output)

        # Metadata should NOT be included
        if data["task_metrics"]:
            first_metric = data["task_metrics"][0]
            assert "metadata" not in first_metric

    def test_json_export_with_time_range(self, exporter):
        """Test JSON export with time range filter."""
        config = ExportConfig(
            format=ExportFormat.JSON, time_range_hours=1, pretty_print=True
        )

        output = exporter.export_to_string(config)
        data = json.loads(output)

        # Verify time range in export info
        assert data["export_info"]["time_range"]["start"] is not None
        assert data["export_info"]["time_range"]["end"] is not None

    def test_json_pretty_print(self, exporter):
        """Test JSON pretty print."""
        # With pretty print
        config_pretty = ExportConfig(format=ExportFormat.JSON, pretty_print=True)
        output_pretty = exporter.export_to_string(config_pretty)

        # Without pretty print
        config_compact = ExportConfig(format=ExportFormat.JSON, pretty_print=False)
        output_compact = exporter.export_to_string(config_compact)

        # Pretty print should be longer (has indentation)
        assert len(output_pretty) > len(output_compact)


# ============================================================================
# Test Category 2: CSV Export
# ============================================================================


class TestCSVExport:
    """Test CSV export format."""

    def test_csv_export_to_string(self, exporter):
        """Test CSV export to string."""
        config = ExportConfig(format=ExportFormat.CSV)

        output = exporter.export_to_string(config)

        # Verify valid CSV
        csv_reader = csv.reader(StringIO(output))
        rows = list(csv_reader)

        # Should have header row
        assert len(rows) > 0
        headers = rows[0]

        # Verify headers
        assert "metric_type" in headers
        assert "timestamp" in headers
        assert "agent_id" in headers
        assert "task_id" in headers

    def test_csv_export_with_metadata(self, exporter):
        """Test CSV export with metadata."""
        config = ExportConfig(format=ExportFormat.CSV, include_metadata=True)

        output = exporter.export_to_string(config)

        csv_reader = csv.reader(StringIO(output))
        rows = list(csv_reader)

        headers = rows[0]

        # Metadata column should be present
        assert "metadata" in headers

    def test_csv_export_without_metadata(self, exporter):
        """Test CSV export without metadata."""
        config = ExportConfig(format=ExportFormat.CSV, include_metadata=False)

        output = exporter.export_to_string(config)

        csv_reader = csv.reader(StringIO(output))
        rows = list(csv_reader)

        headers = rows[0]

        # Metadata column should NOT be present
        assert "metadata" not in headers

    def test_csv_export_data_rows(self, exporter):
        """Test CSV export data rows."""
        config = ExportConfig(format=ExportFormat.CSV)

        output = exporter.export_to_string(config)

        csv_reader = csv.reader(StringIO(output))
        rows = list(csv_reader)

        # Should have header + data rows
        assert len(rows) > 1

        # Verify first data row structure
        if len(rows) > 1:
            data_row = rows[1]
            assert len(data_row) > 0


# ============================================================================
# Test Category 3: Prometheus Export
# ============================================================================


class TestPrometheusExport:
    """Test Prometheus export format."""

    def test_prometheus_export_to_string(self, exporter):
        """Test Prometheus export to string."""
        config = ExportConfig(format=ExportFormat.PROMETHEUS)

        output = exporter.export_to_string(config)

        # Verify Prometheus format
        lines = output.split("\n")

        # Should have TYPE comments
        type_lines = [line for line in lines if line.startswith("# TYPE")]
        assert len(type_lines) > 0

        # Should have metric lines
        metric_lines = [line for line in lines if line and not line.startswith("#")]
        assert len(metric_lines) > 0

    def test_prometheus_export_metric_format(self, exporter):
        """Test Prometheus metric format."""
        config = ExportConfig(format=ExportFormat.PROMETHEUS)

        output = exporter.export_to_string(config)

        # Find a metric line
        lines = output.split("\n")
        metric_lines = [line for line in lines if "moai_task_duration_ms" in line]

        if metric_lines:
            metric_line = metric_lines[0]

            # Should have format: metric_name{labels} value timestamp
            assert "{" in metric_line
            assert "}" in metric_line

            # Verify labels
            assert "agent_id=" in metric_line
            assert "task_id=" in metric_line

    def test_prometheus_export_types(self, exporter):
        """Test Prometheus export includes all metric types."""
        config = ExportConfig(format=ExportFormat.PROMETHEUS)

        output = exporter.export_to_string(config)

        # Should include task metrics
        assert "moai_task_duration_ms" in output
        assert "moai_task_tokens_used" in output

        # Should include agent metrics
        assert "moai_agent_metric" in output

        # Should include swarm metrics
        assert "moai_swarm_metric" in output


# ============================================================================
# Test Category 4: Grafana Export
# ============================================================================


class TestGrafanaExport:
    """Test Grafana JSON data source format."""

    def test_grafana_export_to_string(self, exporter):
        """Test Grafana export to string."""
        config = ExportConfig(format=ExportFormat.GRAFANA, pretty_print=True)

        output = exporter.export_to_string(config)

        # Verify valid JSON
        data = json.loads(output)

        # Should be list of series
        assert isinstance(data, list)

        if data:
            # Verify series structure
            series = data[0]
            assert "target" in series
            assert "datapoints" in series

            # Verify datapoints format
            if series["datapoints"]:
                datapoint = series["datapoints"][0]
                assert isinstance(datapoint, list)
                assert len(datapoint) == 2  # [value, timestamp]


# ============================================================================
# Test Category 5: File Operations
# ============================================================================


class TestFileOperations:
    """Test file output operations."""

    def test_export_to_json_file(self, exporter, temp_dir):
        """Test exporting to JSON file."""
        output_path = temp_dir / "export.json"

        config = ExportConfig(format=ExportFormat.JSON, output_path=output_path)

        result = exporter.export(config)

        # Verify file created
        assert output_path.exists()
        assert str(output_path) == result

        # Verify file content
        with open(output_path) as f:
            data = json.load(f)
            assert "export_info" in data

    def test_export_to_csv_file(self, exporter, temp_dir):
        """Test exporting to CSV file."""
        output_path = temp_dir / "export.csv"

        config = ExportConfig(format=ExportFormat.CSV, output_path=output_path)

        result = exporter.export(config)

        # Verify file created
        assert output_path.exists()

    def test_export_to_prometheus_file(self, exporter, temp_dir):
        """Test exporting to Prometheus file."""
        output_path = temp_dir / "export.prom"

        config = ExportConfig(format=ExportFormat.PROMETHEUS, output_path=output_path)

        result = exporter.export(config)

        # Verify file created
        assert output_path.exists()

    def test_export_creates_parent_directory(self, exporter, temp_dir):
        """Test that export creates parent directory if needed."""
        output_path = temp_dir / "subdir" / "export.json"

        config = ExportConfig(format=ExportFormat.JSON, output_path=output_path)

        result = exporter.export(config)

        # Verify parent directory created
        assert output_path.parent.exists()
        assert output_path.exists()


# ============================================================================
# Test Category 6: Compression
# ============================================================================


class TestCompression:
    """Test compression support."""

    def test_export_with_compression(self, exporter, temp_dir):
        """Test exporting with gzip compression."""
        output_path = temp_dir / "export.json"

        config = ExportConfig(
            format=ExportFormat.JSON, output_path=output_path, compression=True
        )

        result = exporter.export(config)

        # Verify compressed file created
        compressed_path = Path(str(output_path) + ".gz")
        assert compressed_path.exists()
        assert result == str(compressed_path)

        # Verify can decompress
        import gzip

        with gzip.open(compressed_path, "rt") as f:
            data = json.load(f)
            assert "export_info" in data

    def test_compressed_smaller_than_uncompressed(self, exporter, temp_dir):
        """Test that compressed file is smaller."""
        # Export uncompressed
        uncompressed_path = temp_dir / "export_uncompressed.json"
        config_uncompressed = ExportConfig(
            format=ExportFormat.JSON, output_path=uncompressed_path, compression=False
        )
        exporter.export(config_uncompressed)

        # Export compressed
        compressed_path = temp_dir / "export_compressed.json"
        config_compressed = ExportConfig(
            format=ExportFormat.JSON, output_path=compressed_path, compression=True
        )
        exporter.export(config_compressed)

        # Compare sizes
        uncompressed_size = uncompressed_path.stat().st_size
        compressed_size = Path(str(compressed_path) + ".gz").stat().st_size

        # Compressed should be smaller
        assert compressed_size < uncompressed_size


# ============================================================================
# Test Category 7: Edge Cases and Error Handling
# ============================================================================


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_export_empty_database(self, temp_dir):
        """Test export from empty database."""
        # Create empty database
        db_path = temp_dir / "empty.db"
        persistence = MetricsPersistence(db_path=db_path)
        persistence.close()

        # Export
        exporter = MetricsExporter()
        from moai_flow.monitoring.storage.metrics_query import MetricsQuery

        exporter.query = MetricsQuery(db_path=db_path)

        config = ExportConfig(format=ExportFormat.JSON)
        output = exporter.export_to_string(config)

        # Should return valid JSON with empty metrics
        data = json.loads(output)
        assert len(data["task_metrics"]) == 0

        exporter.close()

    def test_export_with_zero_time_range(self, exporter):
        """Test export with zero time range."""
        config = ExportConfig(format=ExportFormat.JSON, time_range_hours=0)

        output = exporter.export_to_string(config)

        # Should return valid JSON
        data = json.loads(output)
        assert "export_info" in data

    def test_export_with_large_time_range(self, exporter):
        """Test export with large time range."""
        config = ExportConfig(format=ExportFormat.JSON, time_range_hours=1000)

        output = exporter.export_to_string(config)

        # Should return valid JSON
        data = json.loads(output)
        assert "export_info" in data

    def test_export_unsupported_format(self, exporter):
        """Test export with unsupported format."""
        # This should raise ValueError
        with pytest.raises(ValueError):
            # Create config with invalid format by mocking
            config = ExportConfig(format="invalid_format")
            config.format = "invalid_format"  # Override enum validation
            exporter.export_to_string(config)

    def test_context_manager(self, populated_db):
        """Test context manager usage."""
        with MetricsExporter() as exporter:
            from moai_flow.monitoring.storage.metrics_query import MetricsQuery

            exporter.query = MetricsQuery(db_path=populated_db)

            config = ExportConfig(format=ExportFormat.JSON)
            output = exporter.export_to_string(config)
            assert len(output) > 0

        # Connection should be closed after exit


# ============================================================================
# Integration Tests
# ============================================================================


class TestIntegration:
    """Integration tests with real export workflows."""

    def test_full_export_workflow(self, exporter, temp_dir):
        """Test complete export workflow."""
        # 1. Export to JSON
        json_path = temp_dir / "metrics.json"
        json_config = ExportConfig(
            format=ExportFormat.JSON,
            output_path=json_path,
            time_range_hours=24,
            pretty_print=True,
        )
        exporter.export(json_config)

        # 2. Export to CSV
        csv_path = temp_dir / "metrics.csv"
        csv_config = ExportConfig(
            format=ExportFormat.CSV, output_path=csv_path, time_range_hours=24
        )
        exporter.export(csv_config)

        # 3. Export to Prometheus
        prom_path = temp_dir / "metrics.prom"
        prom_config = ExportConfig(
            format=ExportFormat.PROMETHEUS, output_path=prom_path, time_range_hours=1
        )
        exporter.export(prom_config)

        # Verify all files created
        assert json_path.exists()
        assert csv_path.exists()
        assert prom_path.exists()

        # Verify file sizes > 0
        assert json_path.stat().st_size > 0
        assert csv_path.stat().st_size > 0
        assert prom_path.stat().st_size > 0
