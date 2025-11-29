"""
Comprehensive tests for HealthReporter - Health report generation and export.

Test Coverage Requirements:
- Framework: pytest
- Coverage Target: 90%+ (per config)
- Mock Strategy: Mock HeartbeatMonitor and MetricsCollector

Test Areas:
1. Initialization and Configuration
2. Health Report Generation (markdown format)
3. Uptime Calculation (agent and swarm)
4. Alert Checking and Detection
5. Health Metrics Export (JSON, markdown)
6. Time Range Filtering
7. Report Formatting and Visualization
"""

import pytest
import json
from datetime import datetime, timedelta
from typing import Dict, Any
from unittest.mock import Mock, MagicMock, call

from moai_flow.monitoring.health_reporter import HealthReporter, Alert, AlertSeverity


# ===== Fixtures =====

@pytest.fixture
def mock_heartbeat_monitor():
    """
    Create mock HeartbeatMonitor.

    Returns:
        Mock: HeartbeatMonitor mock
    """
    monitor = Mock()
    monitor.get_agent_health = Mock(return_value="healthy")
    monitor.get_all_agents_health = Mock(return_value={})
    monitor.get_heartbeat_history = Mock(return_value=[])
    monitor.get_uptime_percentage = Mock(return_value=99.5)
    return monitor


@pytest.fixture
def mock_metrics_collector():
    """
    Create mock MetricsCollector.

    Returns:
        Mock: MetricsCollector mock
    """
    collector = Mock()
    collector.get_swarm_health = Mock(return_value={
        "swarm_id": "swarm-001",
        "topology_health": 0.95,
        "message_throughput": 120.5,
        "consensus_latency_ms": 45.2
    })
    collector.get_agent_performance = Mock(return_value={
        "agent_id": "agent-001",
        "tasks_completed": 100,
        "success_rate": 95.0,
        "avg_duration_ms": 1500.0
    })
    return collector


@pytest.fixture
def reporter(mock_heartbeat_monitor, mock_metrics_collector):
    """
    Create HealthReporter with mocks.

    Returns:
        HealthReporter: Reporter instance
    """
    return HealthReporter(
        heartbeat_monitor=mock_heartbeat_monitor,
        metrics_collector=mock_metrics_collector
    )


# ===== Test Group 1: Initialization =====

class TestHealthReporterInitialization:
    """Test HealthReporter initialization and configuration."""

    def test_initialize_with_dependencies(self, mock_heartbeat_monitor, mock_metrics_collector):
        """Test initialization with heartbeat monitor and metrics collector."""
        reporter = HealthReporter(
            heartbeat_monitor=mock_heartbeat_monitor,
            metrics_collector=mock_metrics_collector
        )

        assert reporter.heartbeat_monitor == mock_heartbeat_monitor
        assert reporter.metrics_collector == mock_metrics_collector

    def test_initialize_without_heartbeat_monitor(self, mock_metrics_collector):
        """Test initialization without heartbeat monitor raises error."""
        with pytest.raises(ValueError, match="heartbeat_monitor is required"):
            HealthReporter(
                heartbeat_monitor=None,
                metrics_collector=mock_metrics_collector
            )

    def test_initialize_without_metrics_collector(self, mock_heartbeat_monitor):
        """Test initialization without metrics collector raises error."""
        with pytest.raises(ValueError, match="metrics_collector is required"):
            HealthReporter(
                heartbeat_monitor=mock_heartbeat_monitor,
                metrics_collector=None
            )


# ===== Test Group 2: Health Report Generation =====

class TestHealthReportGeneration:
    """Test health report generation in various formats."""

    def test_generate_report_markdown_basic(self, reporter, mock_heartbeat_monitor):
        """Test generating basic markdown health report."""
        mock_heartbeat_monitor.get_all_agents_health.return_value = {
            "agent-001": "healthy",
            "agent-002": "healthy",
            "agent-003": "degraded"
        }

        report = reporter.generate_health_report(swarm_id="swarm-001", format="markdown")

        assert report is not None
        assert "SWARM HEALTH REPORT" in report
        assert "swarm-001" in report
        assert "HEALTHY" in report
        assert "DEGRADED" in report

    def test_generate_report_includes_timestamp(self, reporter):
        """Test report includes generation timestamp."""
        report = reporter.generate_health_report(swarm_id="swarm-001")

        assert "Timestamp:" in report
        # Verify ISO format timestamp present
        assert datetime.now().strftime("%Y-%m-%d") in report

    def test_generate_report_includes_topology_info(self, reporter, mock_metrics_collector):
        """Test report includes topology information."""
        mock_metrics_collector.get_swarm_health.return_value = {
            "swarm_id": "swarm-001",
            "topology_health": 0.95,
            "message_throughput": 150.5
        }

        report = reporter.generate_health_report(swarm_id="swarm-001")

        assert "Topology:" in report or "topology" in report.lower()

    def test_generate_report_agent_count(self, reporter, mock_heartbeat_monitor):
        """Test report includes agent count."""
        mock_heartbeat_monitor.get_all_agents_health.return_value = {
            f"agent-{i:03d}": "healthy" for i in range(15)
        }

        report = reporter.generate_health_report(swarm_id="swarm-001")

        assert "15" in report  # Agent count
        assert "Agent Count:" in report or "agent" in report.lower()

    def test_generate_report_health_distribution(self, reporter, mock_heartbeat_monitor):
        """Test report includes health state distribution."""
        mock_heartbeat_monitor.get_all_agents_health.return_value = {
            "agent-001": "healthy",
            "agent-002": "healthy",
            "agent-003": "healthy",
            "agent-004": "degraded",
            "agent-005": "critical"
        }

        report = reporter.generate_health_report(swarm_id="swarm-001")

        # Verify distribution
        assert "60%" in report or "3" in report  # 3/5 healthy
        assert "20%" in report or "1" in report  # 1/5 degraded

    def test_generate_report_with_alerts(self, reporter, mock_heartbeat_monitor):
        """Test report includes alerts for unhealthy agents."""
        mock_heartbeat_monitor.get_all_agents_health.return_value = {
            "agent-001": "healthy",
            "agent-002": "degraded",
            "agent-003": "critical"
        }

        report = reporter.generate_health_report(swarm_id="swarm-001")

        assert "Alerts" in report or "alert" in report.lower()
        assert "agent-002" in report  # Degraded agent
        assert "agent-003" in report  # Critical agent

    def test_generate_report_json_format(self, reporter, mock_heartbeat_monitor):
        """Test generating JSON format health report."""
        mock_heartbeat_monitor.get_all_agents_health.return_value = {
            "agent-001": "healthy",
            "agent-002": "degraded"
        }

        report = reporter.generate_health_report(swarm_id="swarm-001", format="json")

        # Should be valid JSON
        data = json.loads(report)
        assert data["swarm_id"] == "swarm-001"
        assert "agent_count" in data
        assert "health_distribution" in data


# ===== Test Group 3: Uptime Calculation =====

class TestUptimeCalculation:
    """Test uptime calculation for agents and swarms."""

    def test_get_agent_uptime(self, reporter, mock_heartbeat_monitor):
        """Test calculating agent uptime for time range."""
        now = datetime.now()
        time_range = (now - timedelta(hours=24), now)

        mock_heartbeat_monitor.get_uptime_percentage.return_value = 99.5

        uptime = reporter.get_agent_uptime("agent-001", time_range)

        assert uptime == 99.5
        mock_heartbeat_monitor.get_uptime_percentage.assert_called_once_with(
            "agent-001",
            time_range[0],
            time_range[1]
        )

    def test_get_swarm_uptime(self, reporter, mock_heartbeat_monitor):
        """Test calculating swarm-wide uptime."""
        now = datetime.now()
        time_range = (now - timedelta(hours=24), now)

        mock_heartbeat_monitor.get_all_agents_health.return_value = {
            "agent-001": "healthy",
            "agent-002": "healthy",
            "agent-003": "degraded"
        }

        mock_heartbeat_monitor.get_uptime_percentage.side_effect = [99.5, 98.0, 95.0]

        uptime_map = reporter.get_swarm_uptime("swarm-001", time_range)

        assert len(uptime_map) == 3
        assert uptime_map["agent-001"] == 99.5
        assert uptime_map["agent-002"] == 98.0
        assert uptime_map["agent-003"] == 95.0

    def test_get_agent_uptime_not_found(self, reporter, mock_heartbeat_monitor):
        """Test agent uptime when agent not found."""
        mock_heartbeat_monitor.get_uptime_percentage.return_value = None

        now = datetime.now()
        time_range = (now - timedelta(hours=1), now)

        uptime = reporter.get_agent_uptime("agent-999", time_range)

        assert uptime == 0.0  # Not found returns 0


# ===== Test Group 4: Alert Checking =====

class TestAlertChecking:
    """Test alert detection and generation."""

    def test_check_alerts_no_issues(self, reporter, mock_heartbeat_monitor):
        """Test alert checking when all agents healthy."""
        mock_heartbeat_monitor.get_all_agents_health.return_value = {
            "agent-001": "healthy",
            "agent-002": "healthy"
        }

        alerts = reporter.check_alerts("swarm-001")

        assert len(alerts) == 0

    def test_check_alerts_degraded_agent(self, reporter, mock_heartbeat_monitor):
        """Test alert for degraded agent."""
        mock_heartbeat_monitor.get_all_agents_health.return_value = {
            "agent-001": "healthy",
            "agent-002": "degraded"
        }

        alerts = reporter.check_alerts("swarm-001")

        assert len(alerts) == 1
        assert alerts[0].agent_id == "agent-002"
        assert alerts[0].severity == AlertSeverity.WARNING
        assert "degraded" in alerts[0].message.lower()

    def test_check_alerts_critical_agent(self, reporter, mock_heartbeat_monitor):
        """Test alert for critical agent."""
        mock_heartbeat_monitor.get_all_agents_health.return_value = {
            "agent-001": "healthy",
            "agent-002": "critical"
        }

        alerts = reporter.check_alerts("swarm-001")

        assert len(alerts) == 1
        assert alerts[0].agent_id == "agent-002"
        assert alerts[0].severity == AlertSeverity.CRITICAL
        assert "critical" in alerts[0].message.lower()

    def test_check_alerts_failed_agent(self, reporter, mock_heartbeat_monitor):
        """Test alert for failed agent."""
        mock_heartbeat_monitor.get_all_agents_health.return_value = {
            "agent-001": "healthy",
            "agent-002": "failed"
        }

        alerts = reporter.check_alerts("swarm-001")

        assert len(alerts) == 1
        assert alerts[0].agent_id == "agent-002"
        assert alerts[0].severity == AlertSeverity.CRITICAL
        assert "failed" in alerts[0].message.lower()

    def test_check_alerts_multiple_issues(self, reporter, mock_heartbeat_monitor):
        """Test multiple alerts from different agents."""
        mock_heartbeat_monitor.get_all_agents_health.return_value = {
            "agent-001": "degraded",
            "agent-002": "critical",
            "agent-003": "healthy"
        }

        alerts = reporter.check_alerts("swarm-001")

        assert len(alerts) == 2
        # Verify alert severities
        severities = [a.severity for a in alerts]
        assert AlertSeverity.WARNING in severities
        assert AlertSeverity.CRITICAL in severities


# ===== Test Group 5: Health Metrics Export =====

class TestHealthMetricsExport:
    """Test health metrics export in various formats."""

    def test_export_json_format(self, reporter, mock_heartbeat_monitor, mock_metrics_collector):
        """Test exporting health metrics as JSON."""
        mock_heartbeat_monitor.get_all_agents_health.return_value = {
            "agent-001": "healthy",
            "agent-002": "degraded"
        }

        result = reporter.export_health_metrics("swarm-001", format="json")

        data = json.loads(result)
        assert data["swarm_id"] == "swarm-001"
        assert "agents" in data
        assert "metrics" in data

    def test_export_markdown_format(self, reporter):
        """Test exporting health metrics as markdown."""
        result = reporter.export_health_metrics("swarm-001", format="markdown")

        assert "# Health Metrics" in result or "Health Metrics" in result
        assert "swarm-001" in result

    def test_export_to_file(self, reporter, tmp_path):
        """Test exporting health metrics to file."""
        output_file = tmp_path / "health_report.json"

        reporter.export_health_metrics(
            "swarm-001",
            format="json",
            output_path=str(output_file)
        )

        assert output_file.exists()

        # Verify file content
        content = output_file.read_text()
        data = json.loads(content)
        assert data["swarm_id"] == "swarm-001"

    def test_export_invalid_format_rejected(self, reporter):
        """Test exporting with invalid format raises error."""
        with pytest.raises(ValueError, match="Invalid format"):
            reporter.export_health_metrics("swarm-001", format="xml")


# ===== Test Group 6: Report Formatting =====

class TestReportFormatting:
    """Test report formatting and visualization."""

    def test_format_health_bar_100_percent(self, reporter):
        """Test formatting health bar for 100% healthy."""
        bar = reporter._format_health_bar(100, total_width=20)

        assert len(bar) <= 20
        assert "█" in bar  # Should contain filled blocks

    def test_format_health_bar_50_percent(self, reporter):
        """Test formatting health bar for 50%."""
        bar = reporter._format_health_bar(50, total_width=20)

        assert len(bar) <= 20

    def test_format_health_bar_0_percent(self, reporter):
        """Test formatting health bar for 0%."""
        bar = reporter._format_health_bar(0, total_width=20)

        # Should still have valid length
        assert len(bar) <= 20

    def test_format_timestamp_iso8601(self, reporter):
        """Test formatting timestamp in ISO8601 format."""
        now = datetime.now()

        formatted = reporter._format_timestamp(now)

        # Should be ISO format with Z suffix
        assert formatted.endswith("Z")
        assert "T" in formatted

    def test_format_alert_message_warning(self, reporter):
        """Test formatting warning alert message."""
        alert = Alert(
            agent_id="agent-001",
            severity=AlertSeverity.WARNING,
            message="Degraded (15s since last heartbeat)",
            timestamp=datetime.now()
        )

        formatted = reporter._format_alert(alert)

        assert "[WARN]" in formatted
        assert "agent-001" in formatted
        assert "Degraded" in formatted

    def test_format_alert_message_critical(self, reporter):
        """Test formatting critical alert message."""
        alert = Alert(
            agent_id="agent-002",
            severity=AlertSeverity.CRITICAL,
            message="Critical (22s since last heartbeat)",
            timestamp=datetime.now()
        )

        formatted = reporter._format_alert(alert)

        assert "[CRIT]" in formatted
        assert "agent-002" in formatted
        assert "Critical" in formatted
