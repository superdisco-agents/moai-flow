# Monitoring Guide

**Comprehensive monitoring setup for MoAI-Flow production environments**

---

## Table of Contents

- [Overview](#overview)
- [Health Checks](#health-checks)
- [Logging](#logging)
- [Metrics](#metrics)
- [Alerting](#alerting)
- [Dashboards](#dashboards)
- [Troubleshooting](#troubleshooting)

---

## Overview

### Monitoring Stack

**Components**:
- **Health Checks**: Liveness, readiness, startup probes
- **Logging**: Structured logging with centralized aggregation
- **Metrics**: Prometheus metrics collection
- **Dashboards**: Grafana visualization
- **Alerting**: Alertmanager for critical alerts

### Key Metrics

| Metric | Target | Critical Threshold |
|--------|--------|-------------------|
| **Uptime** | 99.9% | <99% |
| **Response Time** | <100ms (p95) | >500ms |
| **Error Rate** | <0.1% | >1% |
| **CPU Usage** | <70% | >90% |
| **Memory Usage** | <80% | >95% |
| **Disk Usage** | <80% | >90% |
| **Database Size** | Monitored | >10GB |

---

## Health Checks

### Basic Health Check

```python
#!/usr/bin/env python3
"""Basic health check script"""

from moai_flow.memory import SwarmDB
import sys

def health_check():
    try:
        # Check database connectivity
        db = SwarmDB()
        db.get_database_size()

        # Check active agents
        active_agents = db.get_active_agents()

        print(f"✅ Healthy - {len(active_agents)} active agents")
        return 0

    except Exception as e:
        print(f"❌ Unhealthy - {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(health_check())
```

### Comprehensive Health Check

```python
#!/usr/bin/env python3
"""Comprehensive health check with detailed diagnostics"""

from moai_flow.memory import SwarmDB
from moai_flow.monitoring import HealthChecker
import sys
import time

def comprehensive_health_check():
    checker = HealthChecker()

    # Run all health checks
    checks = {
        "database": checker.check_database(),
        "disk_space": checker.check_disk_space(),
        "memory": checker.check_memory(),
        "query_performance": checker.check_query_performance(),
        "agents": checker.check_agents()
    }

    # Print results
    all_healthy = True
    for name, result in checks.items():
        status = "✅" if result["healthy"] else "❌"
        print(f"{status} {name}: {result['message']}")
        if not result["healthy"]:
            all_healthy = False
            if "details" in result:
                print(f"   Details: {result['details']}")

    # Overall status
    if all_healthy:
        print("\n✅ All health checks passed")
        return 0
    else:
        print("\n❌ Some health checks failed")
        return 1

if __name__ == "__main__":
    sys.exit(comprehensive_health_check())
```

### Kubernetes Health Checks

**Deployment YAML**:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: moai-flow
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: moai-flow
        image: moai-flow:latest

        # Liveness probe - restart if unhealthy
        livenessProbe:
          exec:
            command:
            - python
            - -c
            - "from moai_flow.memory import SwarmDB; SwarmDB()"
          initialDelaySeconds: 30
          periodSeconds: 60
          timeoutSeconds: 10
          failureThreshold: 3

        # Readiness probe - remove from load balancer if not ready
        readinessProbe:
          exec:
            command:
            - python
            - /app/health_check.py
          initialDelaySeconds: 10
          periodSeconds: 30
          timeoutSeconds: 5
          failureThreshold: 3

        # Startup probe - give time to initialize
        startupProbe:
          exec:
            command:
            - python
            - -c
            - "from moai_flow.memory import SwarmDB; SwarmDB()"
          initialDelaySeconds: 0
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 30
```

---

## Logging

### Logging Configuration

**Python Logging Setup**:

```python
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    """JSON log formatter for structured logging"""

    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra fields
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id
        if hasattr(record, "agent_id"):
            log_data["agent_id"] = record.agent_id

        return json.dumps(log_data)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(".moai/logs/moai-flow.log")
    ]
)

# Use JSON formatter for production
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger = logging.getLogger("moai_flow")
logger.addHandler(handler)
```

### Log Levels

| Level | When to Use | Example |
|-------|-------------|---------|
| **DEBUG** | Development only | "Processing event: {...}" |
| **INFO** | Normal operations | "Agent spawned successfully" |
| **WARNING** | Recoverable issues | "Query took 150ms (expected <100ms)" |
| **ERROR** | Errors requiring attention | "Failed to insert event: ..." |
| **CRITICAL** | System-wide failures | "Database connection lost" |

### Log Rotation

**Logrotate Configuration** (Linux):

```bash
# /etc/logrotate.d/moai-flow
/var/log/moai-flow/*.log {
    daily
    rotate 7
    compress
    delaycompress
    notifempty
    create 0644 ubuntu ubuntu
    sharedscripts
    postrotate
        systemctl reload moai-flow
    endscript
}
```

### Centralized Logging

**ELK Stack** (Elasticsearch, Logstash, Kibana):

```yaml
# filebeat.yml
filebeat.inputs:
- type: log
  enabled: true
  paths:
    - /var/log/moai-flow/*.log
  json.keys_under_root: true
  json.add_error_key: true

output.elasticsearch:
  hosts: ["elasticsearch:9200"]
  index: "moai-flow-%{+yyyy.MM.dd}"

setup.kibana:
  host: "kibana:5601"
```

---

## Metrics

### Prometheus Metrics

**Metrics Exporter**:

```python
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from flask import Flask, Response

app = Flask(__name__)

# Metrics
events_total = Counter(
    'moai_flow_events_total',
    'Total number of events processed',
    ['event_type']
)

agents_active = Gauge(
    'moai_flow_agents_active',
    'Number of active agents'
)

query_duration = Histogram(
    'moai_flow_query_duration_seconds',
    'Query duration in seconds',
    ['query_type']
)

db_size_bytes = Gauge(
    'moai_flow_db_size_bytes',
    'Database size in bytes'
)

# Update metrics
def update_metrics():
    db = SwarmDB()

    # Update gauges
    active_agents = db.get_active_agents()
    agents_active.set(len(active_agents))

    db_size = db.get_database_size()
    db_size_bytes.set(db_size)

@app.route('/metrics')
def metrics():
    update_metrics()
    return Response(generate_latest(), mimetype='text/plain')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9090)
```

### Prometheus Configuration

```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'moai-flow'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['localhost:9100']

  - job_name: 'postgresql'
    static_configs:
      - targets: ['localhost:9187']
```

---

## Alerting

### Alertmanager Configuration

```yaml
# alertmanager.yml
global:
  resolve_timeout: 5m

route:
  group_by: ['alertname', 'severity']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 12h
  receiver: 'team-email'

receivers:
- name: 'team-email'
  email_configs:
  - to: 'devops@moai-flow.dev'
    from: 'alerts@moai-flow.dev'
    smarthost: 'smtp.gmail.com:587'
    auth_username: 'alerts@moai-flow.dev'
    auth_password: 'secret'

- name: 'slack'
  slack_configs:
  - api_url: 'https://hooks.slack.com/services/XXX'
    channel: '#alerts'
    title: 'MoAI-Flow Alert'
    text: '{{ range .Alerts }}{{ .Annotations.description }}{{ end }}'
```

### Alert Rules

```yaml
# alert_rules.yml
groups:
- name: moai-flow
  interval: 30s
  rules:
  # High error rate
  - alert: HighErrorRate
    expr: rate(moai_flow_errors_total[5m]) > 0.01
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "High error rate detected"
      description: "Error rate is {{ $value }} errors/second"

  # Database size growing
  - alert: DatabaseSizeGrowing
    expr: moai_flow_db_size_bytes > 10737418240  # 10GB
    for: 1h
    labels:
      severity: warning
    annotations:
      summary: "Database size exceeds 10GB"
      description: "Database size is {{ $value | humanize }}B"

  # High query latency
  - alert: HighQueryLatency
    expr: moai_flow_query_duration_seconds{quantile="0.95"} > 0.1
    for: 10m
    labels:
      severity: warning
    annotations:
      summary: "High query latency detected"
      description: "P95 query latency is {{ $value }}s"

  # Service down
  - alert: ServiceDown
    expr: up{job="moai-flow"} == 0
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "MoAI-Flow service is down"
      description: "Service has been down for 1 minute"

  # High CPU usage
  - alert: HighCPUUsage
    expr: rate(process_cpu_seconds_total[5m]) > 0.9
    for: 10m
    labels:
      severity: warning
    annotations:
      summary: "High CPU usage"
      description: "CPU usage is {{ $value | humanizePercentage }}"

  # High memory usage
  - alert: HighMemoryUsage
    expr: process_resident_memory_bytes / node_memory_MemTotal_bytes > 0.9
    for: 10m
    labels:
      severity: critical
    annotations:
      summary: "High memory usage"
      description: "Memory usage is {{ $value | humanizePercentage }}"

  # Disk space low
  - alert: DiskSpaceLow
    expr: (node_filesystem_avail_bytes / node_filesystem_size_bytes) < 0.2
    for: 10m
    labels:
      severity: warning
    annotations:
      summary: "Disk space low"
      description: "Only {{ $value | humanizePercentage }} disk space remaining"
```

---

## Dashboards

### Grafana Dashboard

**Import Dashboard JSON**:

```json
{
  "dashboard": {
    "title": "MoAI-Flow Monitoring",
    "panels": [
      {
        "title": "Active Agents",
        "targets": [{
          "expr": "moai_flow_agents_active"
        }],
        "type": "graph"
      },
      {
        "title": "Event Rate",
        "targets": [{
          "expr": "rate(moai_flow_events_total[5m])"
        }],
        "type": "graph"
      },
      {
        "title": "Query Latency (P95)",
        "targets": [{
          "expr": "moai_flow_query_duration_seconds{quantile=\"0.95\"}"
        }],
        "type": "graph"
      },
      {
        "title": "Database Size",
        "targets": [{
          "expr": "moai_flow_db_size_bytes"
        }],
        "type": "graph"
      },
      {
        "title": "Error Rate",
        "targets": [{
          "expr": "rate(moai_flow_errors_total[5m])"
        }],
        "type": "graph"
      },
      {
        "title": "CPU Usage",
        "targets": [{
          "expr": "rate(process_cpu_seconds_total[5m])"
        }],
        "type": "gauge"
      },
      {
        "title": "Memory Usage",
        "targets": [{
          "expr": "process_resident_memory_bytes"
        }],
        "type": "gauge"
      }
    ]
  }
}
```

---

## Troubleshooting

### Common Monitoring Issues

**Issue 1: Metrics not appearing**

```bash
# Check Prometheus targets
curl http://localhost:9091/api/v1/targets

# Check metrics endpoint
curl http://localhost:9090/metrics

# Restart Prometheus
systemctl restart prometheus
```

**Issue 2: Alerts not firing**

```bash
# Check alert rules
curl http://localhost:9091/api/v1/rules

# Check Alertmanager
curl http://localhost:9093/api/v2/alerts

# Restart Alertmanager
systemctl restart alertmanager
```

**Issue 3: Dashboard not loading**

```bash
# Check Grafana logs
journalctl -u grafana-server -f

# Verify Prometheus datasource
curl http://localhost:3000/api/datasources

# Restart Grafana
systemctl restart grafana-server
```

---

**Last Updated**: 2025-11-29
**Version**: 1.0.0
**Owner**: DevOps Team
