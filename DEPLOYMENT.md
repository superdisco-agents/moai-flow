# MoAI-Flow Production Deployment Guide

**Complete guide for deploying MoAI-Flow to production environments**

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation Methods](#installation-methods)
- [Configuration](#configuration)
- [Deployment Options](#deployment-options)
- [Database Setup](#database-setup)
- [Monitoring](#monitoring)
- [Health Checks](#health-checks)
- [Troubleshooting](#troubleshooting)
- [Security](#security)
- [Performance Tuning](#performance-tuning)

---

## Prerequisites

### System Requirements

**Minimum Requirements**:
- Python 3.11+ (Recommended: Python 3.13)
- 512 MB RAM
- 100 MB disk space
- SQLite 3.8.0+

**Recommended for Production**:
- Python 3.13
- 2 GB RAM
- 1 GB disk space
- PostgreSQL 16+ (optional, for advanced use cases)

### Dependencies

All dependencies are automatically installed via `pip install -e .` or `uv pip install -e .`

**Core Dependencies**:
- click>=8.1.0
- rich>=13.0.0
- pyfiglet>=1.0.2
- questionary>=2.0.0
- gitpython>=3.1.45
- packaging>=21.0
- pyyaml>=6.0
- jinja2>=3.0.0
- requests>=2.28.0
- psutil>=7.1.3
- aiohttp>=3.13.2
- pytest-asyncio>=1.2.0
- pytest-cov>=7.0.0

**Development Dependencies** (optional):
- pytest>=8.4.2
- pytest-cov>=7.0.0
- pytest-xdist>=3.8.0
- ruff>=0.1.0
- mypy>=1.7.0
- types-PyYAML>=6.0.0
- black>=24.0.0

**Security Tools** (optional):
- pip-audit>=2.7.0
- bandit>=1.8.0

---

## Installation Methods

### Method 1: pip (Standard Installation)

```bash
# Clone repository
git clone https://github.com/superdisco-agents/moai-flow.git
cd moai-flow

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install package
pip install -e .

# Verify installation
python -c "from moai_flow.memory.swarm_db import SwarmDB; print('✅ MoAI-Flow installed')"
```

### Method 2: uv (Faster Installation)

```bash
# Clone repository
git clone https://github.com/superdisco-agents/moai-flow.git
cd moai-flow

# Create virtual environment and install with uv
uv pip install -e .

# Verify installation
python -c "from moai_flow.memory.swarm_db import SwarmDB; print('✅ MoAI-Flow installed')"
```

### Method 3: Docker (Containerized Deployment)

```bash
# Build Docker image
docker build -t moai-flow:latest .

# Run container
docker run -d \
  --name moai-flow \
  -v $(pwd)/.moai:/app/.moai \
  -e MOAI_ENV=production \
  -e MOAI_DB_PATH=/app/.moai/memory/swarm.db \
  moai-flow:latest

# Verify deployment
docker logs moai-flow
```

### Method 4: Docker Compose (Full Stack)

```bash
# Start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f moai-flow
```

---

## Configuration

### Environment Variables

Create a `.env` file or set environment variables:

```bash
# Environment Mode
MOAI_ENV=production  # Options: development, staging, production

# Database Configuration
MOAI_DB_PATH=.moai/memory/swarm.db  # SQLite database path

# Logging Configuration
MOAI_LOG_LEVEL=INFO  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL

# Performance Settings
MOAI_QUERY_TIMEOUT=20  # Query timeout in milliseconds
MOAI_BATCH_SIZE=1000  # Batch insert size

# Security Settings
MOAI_ENABLE_AUDIT=true  # Enable audit logging
MOAI_MAX_EVENTS=1000000  # Maximum events before auto-cleanup
```

### Configuration File (.moai/config.json)

Example production configuration:

```json
{
  "environment": "production",
  "database": {
    "path": ".moai/memory/swarm.db",
    "auto_vacuum": true,
    "journal_mode": "WAL",
    "cache_size": 10000
  },
  "memory": {
    "semantic_memory_ttl_days": 90,
    "episodic_memory_ttl_days": 30,
    "context_hints_ttl_days": 365
  },
  "resource": {
    "token_budget": 200000,
    "max_agents_per_type": 10
  },
  "logging": {
    "level": "INFO",
    "file": ".moai/logs/moai-flow.log",
    "max_size_mb": 100,
    "backup_count": 5
  },
  "monitoring": {
    "enabled": true,
    "health_check_interval_seconds": 60,
    "metrics_collection_interval_seconds": 300
  }
}
```

---

## Deployment Options

### Option 1: Local Development

**Best for**: Testing, development, local experimentation

```bash
# Install dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Start development server (if applicable)
python -m moai_flow.server --env development
```

### Option 2: Staging Environment

**Best for**: Pre-production testing, QA validation

```bash
# Set environment
export MOAI_ENV=staging
export MOAI_DB_PATH=/var/lib/moai/staging/swarm.db

# Install production dependencies only
pip install -e .

# Initialize database
python -c "from moai_flow.memory import SwarmDB; SwarmDB()"

# Run health checks
python -m moai_flow.health
```

### Option 3: Production Environment

**Best for**: Live deployment, production workloads

```bash
# Set environment
export MOAI_ENV=production
export MOAI_DB_PATH=/var/lib/moai/production/swarm.db
export MOAI_LOG_LEVEL=WARNING

# Install production dependencies
pip install -e .

# Initialize database
python -c "from moai_flow.memory import SwarmDB; SwarmDB()"

# Enable monitoring
export MOAI_ENABLE_METRICS=true
export MOAI_METRICS_PORT=9090

# Run production server
python -m moai_flow.server --env production --port 8000
```

### Option 4: Docker Deployment

**Best for**: Containerized environments, Kubernetes, cloud platforms

See [Dockerfile](#dockerfile) and [docker-compose.yml](#docker-composeyml) sections below.

---

## Database Setup

### SQLite (Default)

**Automatic Setup**:
```python
from moai_flow.memory import SwarmDB

# Database auto-created at .moai/memory/swarm.db
db = SwarmDB()
```

**Manual Setup**:
```bash
# Create database directory
mkdir -p .moai/memory

# Initialize database
python -c "from moai_flow.memory import SwarmDB; SwarmDB(db_path='.moai/memory/swarm.db')"
```

**Performance Optimization**:
```bash
# Enable WAL mode for better concurrency
sqlite3 .moai/memory/swarm.db "PRAGMA journal_mode=WAL;"

# Increase cache size
sqlite3 .moai/memory/swarm.db "PRAGMA cache_size=10000;"

# Optimize database
sqlite3 .moai/memory/swarm.db "VACUUM;"
```

### PostgreSQL (Optional, Advanced)

**When to use PostgreSQL**:
- Multi-instance deployments
- High-concurrency workloads
- Advanced replication needs

**Setup** (Future implementation):
```python
from moai_flow.memory import SwarmDB

# PostgreSQL connection
db = SwarmDB(
    db_type="postgresql",
    connection_string="postgresql://user:pass@localhost:5432/moai_flow"
)
```

---

## Monitoring

### Health Check Endpoint

```python
from moai_flow.health import HealthChecker

checker = HealthChecker()
status = checker.check_all()

if status['overall'] == "healthy":
    print("✅ All systems operational")
else:
    print(f"⚠️ Issues: {status['issues']}")
```

**Health Check Components**:
- Database connectivity
- Disk space availability
- Memory usage
- Active agent count
- Query performance

### Logging

**Configure logging in production**:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('.moai/logs/moai-flow.log'),
        logging.StreamHandler()
    ]
)
```

**Log Rotation**:
```bash
# Install logrotate (Linux)
sudo apt-get install logrotate

# Configure logrotate
cat <<EOF | sudo tee /etc/logrotate.d/moai-flow
/var/log/moai-flow/*.log {
    daily
    rotate 7
    compress
    delaycompress
    notifempty
    create 0644 moai moai
    sharedscripts
}
EOF
```

### Metrics Collection

**Prometheus Metrics** (Future implementation):

```python
from moai_flow.monitoring import PrometheusExporter

exporter = PrometheusExporter(port=9090)
exporter.start()

# Metrics exposed at http://localhost:9090/metrics
```

**Key Metrics**:
- `moai_flow_events_total` - Total events processed
- `moai_flow_agents_active` - Active agents count
- `moai_flow_query_duration_seconds` - Query latency
- `moai_flow_db_size_bytes` - Database size

---

## Health Checks

### Basic Health Check

```bash
# Simple health check
python -c "from moai_flow.memory import SwarmDB; db = SwarmDB(); print('✅ Healthy' if db.get_database_size() > 0 else '❌ Unhealthy')"
```

### Comprehensive Health Check

```python
#!/usr/bin/env python3
"""Comprehensive health check script"""

from moai_flow.memory import SwarmDB
from moai_flow.monitoring import HealthChecker
import sys

def main():
    checker = HealthChecker()

    # Run all health checks
    checks = {
        "database": checker.check_database(),
        "disk": checker.check_disk_space(),
        "memory": checker.check_memory(),
        "agents": checker.check_agents(),
        "performance": checker.check_query_performance()
    }

    # Print results
    for name, status in checks.items():
        symbol = "✅" if status["healthy"] else "❌"
        print(f"{symbol} {name}: {status['message']}")

    # Exit with error if any check fails
    if not all(check["healthy"] for check in checks.values()):
        sys.exit(1)

    print("\n✅ All health checks passed")
    sys.exit(0)

if __name__ == "__main__":
    main()
```

### Kubernetes Health Checks

**Liveness Probe**:
```yaml
livenessProbe:
  exec:
    command:
    - python
    - -c
    - "from moai_flow.memory import SwarmDB; SwarmDB()"
  initialDelaySeconds: 30
  periodSeconds: 60
```

**Readiness Probe**:
```yaml
readinessProbe:
  exec:
    command:
    - python
    - -m
    - moai_flow.health
  initialDelaySeconds: 10
  periodSeconds: 30
```

---

## Troubleshooting

### Common Issues

**Issue 1: Database Lock Errors**
```
Error: database is locked
```

**Solution**:
```bash
# Enable WAL mode for better concurrency
sqlite3 .moai/memory/swarm.db "PRAGMA journal_mode=WAL;"

# Check for long-running queries
sqlite3 .moai/memory/swarm.db "SELECT * FROM sqlite_master WHERE type='table';"
```

**Issue 2: Slow Queries**
```
Warning: Query took 150ms (expected <20ms)
```

**Solution**:
```bash
# Run VACUUM to optimize database
sqlite3 .moai/memory/swarm.db "VACUUM;"

# Rebuild indexes
python -m moai_flow.maintenance.rebuild_indexes
```

**Issue 3: Disk Space Full**
```
Error: disk I/O error
```

**Solution**:
```bash
# Clean up old events (keep last 30 days)
python -c "from moai_flow.memory import SwarmDB; SwarmDB().cleanup_old_events(days=30)"

# Check database size
ls -lh .moai/memory/swarm.db
```

**Issue 4: High Memory Usage**
```
Warning: Memory usage 85%
```

**Solution**:
```bash
# Reduce token budget
export MOAI_TOKEN_BUDGET=100000

# Limit concurrent agents
export MOAI_MAX_AGENTS=5

# Restart application
```

### Debug Mode

```bash
# Enable debug logging
export MOAI_LOG_LEVEL=DEBUG

# Run with verbose output
python -m moai_flow.server --debug --verbose
```

---

## Security

### Security Best Practices

**1. Database Security**:
```bash
# Set restrictive file permissions
chmod 600 .moai/memory/swarm.db

# Regular backups
cp .moai/memory/swarm.db .moai/backups/swarm-$(date +%Y%m%d).db
```

**2. Environment Variables**:
```bash
# Never commit .env files
echo ".env" >> .gitignore

# Use secret management tools
export MOAI_DB_PASSWORD=$(vault kv get -field=password secret/moai/db)
```

**3. Network Security**:
```bash
# Bind to localhost only
python -m moai_flow.server --host 127.0.0.1 --port 8000

# Use reverse proxy (nginx, traefik)
```

**4. Audit Logging**:
```bash
# Enable audit logs
export MOAI_ENABLE_AUDIT=true

# Review audit logs
cat .moai/logs/audit.log
```

### Security Scanning

**Run security checks**:
```bash
# Install security tools
pip install pip-audit bandit

# Scan dependencies
pip-audit

# Scan code
bandit -r moai_flow/ -ll
```

---

## Performance Tuning

### Database Performance

**Optimize SQLite**:
```bash
# WAL mode (Write-Ahead Logging)
sqlite3 .moai/memory/swarm.db "PRAGMA journal_mode=WAL;"

# Increase cache size
sqlite3 .moai/memory/swarm.db "PRAGMA cache_size=10000;"

# Synchronous mode (faster but less safe)
sqlite3 .moai/memory/swarm.db "PRAGMA synchronous=NORMAL;"

# Memory-mapped I/O
sqlite3 .moai/memory/swarm.db "PRAGMA mmap_size=268435456;"  # 256MB
```

### Query Optimization

**Use batch operations**:
```python
from moai_flow.memory import SwarmDB

db = SwarmDB()

# Bad: Individual inserts
for event in events:
    db.insert_event(event)

# Good: Batch insert
with db.transaction():
    for event in events:
        db.insert_event(event)
```

**Use indexes**:
```python
# All necessary indexes are auto-created by SwarmDB
# 12 indexes for optimal query performance
```

### Memory Optimization

**Token Budget Tuning**:
```python
from moai_flow.resource.token_budget import TokenBudget

# Reduce budget for lower memory usage
budget = TokenBudget(total_budget=100000)  # Default: 200K
```

**Cleanup Old Data**:
```python
from moai_flow.memory import SwarmDB

db = SwarmDB()

# Clean up events older than 30 days
db.cleanup_old_events(days=30)

# Vacuum database
db.vacuum()
```

---

## Backup and Recovery

### Automated Backup

**Backup Script**:
```bash
#!/bin/bash
# backup-moai-flow.sh

BACKUP_DIR=".moai/backups"
BACKUP_NAME="swarm-$(date +%Y%m%d-%H%M%S).db"

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
cp .moai/memory/swarm.db $BACKUP_DIR/$BACKUP_NAME

# Compress backup
gzip $BACKUP_DIR/$BACKUP_NAME

# Keep only last 7 days
find $BACKUP_DIR -name "swarm-*.db.gz" -mtime +7 -delete

echo "✅ Backup completed: $BACKUP_DIR/$BACKUP_NAME.gz"
```

**Automated Backup (cron)**:
```bash
# Run daily at 2 AM
0 2 * * * /path/to/backup-moai-flow.sh
```

### Recovery

**Restore from Backup**:
```bash
# Stop application
systemctl stop moai-flow  # or docker-compose stop

# Restore database
gunzip -c .moai/backups/swarm-20251129.db.gz > .moai/memory/swarm.db

# Verify database
sqlite3 .moai/memory/swarm.db "PRAGMA integrity_check;"

# Restart application
systemctl start moai-flow  # or docker-compose up -d
```

---

## CI/CD Integration

See `.github/workflows/cd.yml` for automated deployment pipeline.

**Key Features**:
- Automated testing on all PRs
- Security scanning (pip-audit, bandit)
- Code quality checks (ruff, black, mypy)
- Coverage enforcement (90%+)
- Auto-deployment to staging/production

---

## Additional Resources

**Documentation**:
- [README.md](README.md) - Project overview
- [Production Checklist](docs/production/production-checklist.md) - Pre-deployment checklist
- [Environment Setup](docs/production/environment-setup.md) - Environment configuration
- [Monitoring Guide](docs/production/monitoring-guide.md) - Monitoring setup
- [Security Guide](docs/production/security-guide.md) - Security best practices

**Support**:
- GitHub Issues: https://github.com/superdisco-agents/moai-flow/issues
- Discussions: https://github.com/superdisco-agents/moai-flow/discussions
- Email: support@moai-flow.dev

---

**Last Updated**: 2025-11-29
**Version**: 1.0.0
**Status**: Production Ready
