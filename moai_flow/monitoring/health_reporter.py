"""
HealthReporter - Comprehensive health reporting for MoAI-Flow Phase 6A.

Generates comprehensive health reports combining heartbeat monitoring
and metrics collection data. Provides visualization, alerts, and export
functionality for swarm health analysis.

Key Features:
- Markdown and JSON format report generation
- Agent and swarm uptime calculation
- Automatic alert detection (WARNING/CRITICAL)
- Health distribution visualization with ASCII bars
- Export to file or string
- Time range filtering for historical analysis

Example:
    >>> monitor = HeartbeatMonitor()
    >>> collector = MetricsCollector()
    >>> reporter = HealthReporter(monitor, collector)
    >>>
    >>> report = reporter.generate_health_report("swarm-001", format="markdown")
    >>> print(report)
    ┌─────────────────────────────────────────────────────────┐
    │ SWARM HEALTH REPORT: swarm-001                          │
    ├─────────────────────────────────────────────────────────┤
    │ Timestamp: 2025-11-29T12:00:00Z                         │
    │ Agent Count: 15                                          │
    │                                                          │
    │ Health Distribution:                                     │
    │   HEALTHY:   12 agents (80%)  ████████████████████      │
    │   DEGRADED:   2 agents (13%)  ███                        │
    │   CRITICAL:   1 agent  (7%)   ██                         │
    │                                                          │
    │ Alerts (2):                                              │
    │   [WARN] agent-007: Degraded (15s since last heartbeat) │
    │   [CRIT] agent-012: Critical (22s since last heartbeat) │
    └─────────────────────────────────────────────────────────┘
"""

import json
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


logger = logging.getLogger(__name__)


# ============================================================================
# Data Structures
# ============================================================================

class AlertSeverity(str, Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class Alert:
    """
    Health alert for unhealthy agents.

    Attributes:
        agent_id: Agent identifier
        severity: Alert severity level
        message: Human-readable alert message
        timestamp: When alert was generated
        metadata: Additional alert context
    """
    agent_id: str
    severity: AlertSeverity
    message: str
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert alert to dictionary."""
        return {
            "agent_id": self.agent_id,
            "severity": self.severity.value,
            "message": self.message,
            "timestamp": self.timestamp.isoformat() + "Z" if hasattr(self.timestamp, 'isoformat') else str(self.timestamp),
            "metadata": self.metadata
        }


# ============================================================================
# HealthReporter Implementation
# ============================================================================

class HealthReporter:
    """
    Comprehensive health report generator.

    Combines heartbeat monitoring and metrics collection data to produce
    detailed health reports with alerts, uptime statistics, and visualizations.

    Example:
        >>> reporter = HealthReporter(heartbeat_monitor, metrics_collector)
        >>> report = reporter.generate_health_report("swarm-001")
        >>> alerts = reporter.check_alerts("swarm-001")
        >>> uptime = reporter.get_agent_uptime("agent-001", time_range)
    """

    def __init__(
        self,
        heartbeat_monitor: Any,
        metrics_collector: Any
    ):
        """
        Initialize HealthReporter.

        Args:
            heartbeat_monitor: HeartbeatMonitor instance
            metrics_collector: MetricsCollector instance

        Raises:
            ValueError: If required dependencies not provided
        """
        if heartbeat_monitor is None:
            raise ValueError("heartbeat_monitor is required")
        if metrics_collector is None:
            raise ValueError("metrics_collector is required")

        self.heartbeat_monitor = heartbeat_monitor
        self.metrics_collector = metrics_collector

        logger.info("HealthReporter initialized")

    # ========================================================================
    # Health Report Generation
    # ========================================================================

    def generate_health_report(
        self,
        swarm_id: str,
        format: str = "markdown",
        include_alerts: bool = True
    ) -> str:
        """
        Generate comprehensive health report.

        Args:
            swarm_id: Swarm identifier
            format: Report format ("markdown" or "json")
            include_alerts: Include alerts section

        Returns:
            Formatted health report string

        Raises:
            ValueError: If format is invalid
        """
        if format not in ["markdown", "json"]:
            raise ValueError(f"Invalid format: {format}. Use 'markdown' or 'json'")

        # Gather health data
        agents_health = self.heartbeat_monitor.get_all_agents_health()
        agent_count = len(agents_health)

        # Calculate health distribution
        health_dist = self._calculate_health_distribution(agents_health)

        # Get swarm metrics
        swarm_metrics = self.metrics_collector.get_swarm_health(swarm_id)

        # Generate alerts if requested
        alerts = self.check_alerts(swarm_id) if include_alerts else []

        # Format based on requested format
        if format == "markdown":
            return self._generate_markdown_report(
                swarm_id=swarm_id,
                agent_count=agent_count,
                health_dist=health_dist,
                swarm_metrics=swarm_metrics,
                alerts=alerts
            )
        else:  # json
            return self._generate_json_report(
                swarm_id=swarm_id,
                agent_count=agent_count,
                health_dist=health_dist,
                swarm_metrics=swarm_metrics,
                alerts=alerts
            )

    def _calculate_health_distribution(
        self,
        agents_health: Dict[str, str]
    ) -> Dict[str, int]:
        """Calculate health state distribution."""
        distribution = {
            "healthy": 0,
            "degraded": 0,
            "critical": 0,
            "failed": 0
        }

        for health_state in agents_health.values():
            state = health_state.lower()
            if state in distribution:
                distribution[state] += 1

        return distribution

    def _generate_markdown_report(
        self,
        swarm_id: str,
        agent_count: int,
        health_dist: Dict[str, int],
        swarm_metrics: Dict[str, Any],
        alerts: List[Alert]
    ) -> str:
        """Generate markdown-formatted health report."""
        lines = []
        timestamp = self._format_timestamp(datetime.now())

        # Header
        lines.append("┌─────────────────────────────────────────────────────────┐")
        lines.append(f"│ SWARM HEALTH REPORT: {swarm_id:<34} │")
        lines.append("├─────────────────────────────────────────────────────────┤")
        lines.append(f"│ Timestamp: {timestamp:<44} │")

        # Topology info (if available)
        topology_type = swarm_metrics.get("metadata", {}).get("topology_type", "unknown")
        lines.append(f"│ Topology: {topology_type:<46} │")

        lines.append(f"│ Agent Count: {agent_count:<44} │")
        lines.append("│                                                         │")

        # Health Distribution
        lines.append("│ Health Distribution:                                    │")

        total = agent_count if agent_count > 0 else 1

        # Healthy
        healthy_pct = (health_dist["healthy"] / total) * 100 if total > 0 else 0
        healthy_bar = self._format_health_bar(healthy_pct, total_width=20)
        lines.append(f"│   HEALTHY:   {health_dist['healthy']:2d} agents ({healthy_pct:3.0f}%)  {healthy_bar:<20} │")

        # Degraded
        degraded_pct = (health_dist["degraded"] / total) * 100 if total > 0 else 0
        degraded_bar = self._format_health_bar(degraded_pct, total_width=20)
        lines.append(f"│   DEGRADED:  {health_dist['degraded']:2d} agents ({degraded_pct:3.0f}%)  {degraded_bar:<20} │")

        # Critical
        critical_pct = (health_dist["critical"] / total) * 100 if total > 0 else 0
        critical_bar = self._format_health_bar(critical_pct, total_width=20)
        lines.append(f"│   CRITICAL:  {health_dist['critical']:2d} agent  ({critical_pct:3.0f}%)   {critical_bar:<20} │")

        # Failed
        failed_pct = (health_dist["failed"] / total) * 100 if total > 0 else 0
        failed_bar = self._format_health_bar(failed_pct, total_width=20)
        lines.append(f"│   FAILED:    {health_dist['failed']:2d} agents ({failed_pct:3.0f}%)  {failed_bar:<20} │")

        # Alerts section
        if alerts:
            lines.append("│                                                         │")
            lines.append(f"│ Alerts ({len(alerts)}):                                              │")
            for alert in alerts[:5]:  # Show up to 5 alerts
                formatted_alert = self._format_alert(alert)
                # Truncate if too long
                if len(formatted_alert) > 50:
                    formatted_alert = formatted_alert[:47] + "..."
                lines.append(f"│   {formatted_alert:<52} │")

        # Footer
        lines.append("└─────────────────────────────────────────────────────────┘")

        return "\n".join(lines)

    def _generate_json_report(
        self,
        swarm_id: str,
        agent_count: int,
        health_dist: Dict[str, int],
        swarm_metrics: Dict[str, Any],
        alerts: List[Alert]
    ) -> str:
        """Generate JSON-formatted health report."""
        report = {
            "swarm_id": swarm_id,
            "timestamp": self._format_timestamp(datetime.now()),
            "agent_count": agent_count,
            "health_distribution": health_dist,
            "metrics": swarm_metrics,
            "alerts": [alert.to_dict() for alert in alerts]
        }

        return json.dumps(report, indent=2)

    # ========================================================================
    # Uptime Calculation
    # ========================================================================

    def get_agent_uptime(
        self,
        agent_id: str,
        time_range: Tuple[datetime, datetime]
    ) -> float:
        """
        Calculate agent uptime percentage for time range.

        Args:
            agent_id: Agent identifier
            time_range: (start_time, end_time) tuple

        Returns:
            Uptime percentage (0.0 - 100.0)
        """
        start_time, end_time = time_range

        try:
            uptime = self.heartbeat_monitor.get_uptime_percentage(
                agent_id,
                start_time,
                end_time
            )
            return uptime if uptime is not None else 0.0
        except Exception as e:
            logger.error(f"Error calculating uptime for {agent_id}: {e}")
            return 0.0

    def get_swarm_uptime(
        self,
        swarm_id: str,
        time_range: Tuple[datetime, datetime]
    ) -> Dict[str, float]:
        """
        Calculate uptime for all agents in swarm.

        Args:
            swarm_id: Swarm identifier
            time_range: (start_time, end_time) tuple

        Returns:
            Dict mapping agent_id to uptime percentage
        """
        agents_health = self.heartbeat_monitor.get_all_agents_health()

        uptime_map = {}
        for agent_id in agents_health.keys():
            uptime_map[agent_id] = self.get_agent_uptime(agent_id, time_range)

        return uptime_map

    # ========================================================================
    # Alert Detection
    # ========================================================================

    def check_alerts(self, swarm_id: str) -> List[Alert]:
        """
        Check for health alerts across swarm.

        Args:
            swarm_id: Swarm identifier

        Returns:
            List of active alerts
        """
        alerts = []
        agents_health = self.heartbeat_monitor.get_all_agents_health()

        for agent_id, health_state in agents_health.items():
            state = health_state.lower()

            if state == "degraded":
                alerts.append(Alert(
                    agent_id=agent_id,
                    severity=AlertSeverity.WARNING,
                    message=f"Degraded (heartbeat delayed)",
                    timestamp=datetime.now()
                ))
            elif state == "critical":
                alerts.append(Alert(
                    agent_id=agent_id,
                    severity=AlertSeverity.CRITICAL,
                    message=f"Critical (heartbeat timeout)",
                    timestamp=datetime.now()
                ))
            elif state == "failed":
                alerts.append(Alert(
                    agent_id=agent_id,
                    severity=AlertSeverity.CRITICAL,
                    message=f"Failed (heartbeat lost)",
                    timestamp=datetime.now()
                ))

        return alerts

    # ========================================================================
    # Health Metrics Export
    # ========================================================================

    def export_health_metrics(
        self,
        swarm_id: str,
        format: str = "json",
        output_path: Optional[str] = None
    ) -> str:
        """
        Export health metrics to file or string.

        Args:
            swarm_id: Swarm identifier
            format: Export format ("json" or "markdown")
            output_path: Optional file path for export

        Returns:
            Exported metrics as string

        Raises:
            ValueError: If format is invalid
        """
        if format not in ["json", "markdown"]:
            raise ValueError(f"Invalid format: {format}. Use 'json' or 'markdown'")

        # Gather all health data
        agents_health = self.heartbeat_monitor.get_all_agents_health()
        swarm_metrics = self.metrics_collector.get_swarm_health(swarm_id)

        if format == "json":
            export_data = {
                "swarm_id": swarm_id,
                "timestamp": self._format_timestamp(datetime.now()),
                "agents": agents_health,
                "metrics": swarm_metrics
            }
            content = json.dumps(export_data, indent=2)
        else:  # markdown
            content = f"# Health Metrics Export\n\n"
            content += f"**Swarm ID**: {swarm_id}\n\n"
            content += f"**Timestamp**: {self._format_timestamp(datetime.now())}\n\n"
            content += f"## Agent Health States\n\n"
            for agent_id, state in agents_health.items():
                content += f"- **{agent_id}**: {state}\n"
            content += f"\n## Swarm Metrics\n\n"
            content += f"```json\n{json.dumps(swarm_metrics, indent=2)}\n```\n"

        # Write to file if path provided
        if output_path:
            with open(output_path, 'w') as f:
                f.write(content)
            logger.info(f"Health metrics exported to {output_path}")

        return content

    # ========================================================================
    # Formatting Utilities
    # ========================================================================

    def _format_health_bar(self, percentage: float, total_width: int = 20) -> str:
        """
        Format ASCII health bar visualization.

        Args:
            percentage: Health percentage (0-100)
            total_width: Total width of bar in characters

        Returns:
            ASCII bar string
        """
        filled = int((percentage / 100) * total_width)
        bar = "█" * filled + " " * (total_width - filled)
        return bar

    def _format_timestamp(self, dt: datetime) -> str:
        """
        Format timestamp in ISO8601 format.

        Args:
            dt: Datetime to format

        Returns:
            ISO8601 formatted string with Z suffix
        """
        return dt.isoformat() + "Z"

    def _format_alert(self, alert: Alert) -> str:
        """
        Format alert message for display.

        Args:
            alert: Alert to format

        Returns:
            Formatted alert string
        """
        severity_prefix = {
            AlertSeverity.INFO: "[INFO]",
            AlertSeverity.WARNING: "[WARN]",
            AlertSeverity.CRITICAL: "[CRIT]"
        }

        prefix = severity_prefix.get(alert.severity, "[UNKN]")
        return f"{prefix} {alert.agent_id}: {alert.message}"


__all__ = ["HealthReporter", "Alert", "AlertSeverity"]
