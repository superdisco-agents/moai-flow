# MoAI-Flow Production Deployment Guide

**Comprehensive deployment guide for production environments**

---

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Deployment Methods](#deployment-methods)
- [Step-by-Step Deployment](#step-by-step-deployment)
- [Configuration](#configuration)
- [Monitoring](#monitoring)
- [Troubleshooting](#troubleshooting)
- [Rollback Procedures](#rollback-procedures)

---

## Overview

MoAI-Flow is production-ready with:
- ✅ **97%+ test coverage** (318+ tests)
- ✅ **Zero security vulnerabilities** (pip-audit, bandit)
- ✅ **Optimized SQLite database** with 12 indexes
- ✅ **Docker containerization** ready
- ✅ **CI/CD pipeline** configured
- ✅ **Comprehensive monitoring** and health checks

**Deployment Options**:
1. **Local Production** - Python virtual environment
2. **Docker Compose** - Containerized full stack
3. **Kubernetes** - Enterprise orchestration
4. **Cloud Platforms** - AWS, GCP, Azure

---

## Prerequisites

### System Requirements

**Minimum** (Testing/Staging):
- Python 3.11+
- 512 MB RAM
- 100 MB disk space
- SQLite 3.8.0+

**Recommended** (Production):
- **Python 3.13** (latest stable)
- **2 GB RAM** minimum
- **1 GB disk space** (with logs/backups)
- **PostgreSQL 16+** (optional, for advanced use cases)

### Required Software

```bash
# Python 3.13
python3 --version  # Should be 3.13.x

# SQLite 3
sqlite3 --version  # Should be 3.8.0+

# Git (for deployment tracking)
git --version

# Optional: Docker
docker --version
docker-compose --version
```

### Network Requirements

- **Outbound HTTPS** - For dependency installation
- **Port 8000** (optional) - Application API
- **Port 9090** (optional) - Metrics endpoint

---

## Deployment Methods

### Method 1: Automated Deployment Script ⭐ RECOMMENDED

**Fastest and safest deployment method**

```bash
# Navigate to project directory
cd /path/to/moai-adk

# Run automated deployment script
./scripts/deploy_production.sh
```

**What it does**:
1. ✅ Checks prerequisites
2. ✅ Creates backup of existing database
3. ✅ Initializes and optimizes database
4. ✅ Runs health checks
5. ✅ Deploys application
6. ✅ Validates deployment
7. ✅ Sets up monitoring
8. ✅ Automatic rollback on failure

**Output**:
```
════════════════════════════════════════════════════════════
  MoAI-Flow Production Deployment
  Environment: production
  Date: 2025-11-30 00:00:00
════════════════════════════════════════════════════════════

[2025-11-30 00:00:00] Checking prerequisites...
[INFO] Python version: 3.13.6
[INFO] SQLite version: 3.45.0
[2025-11-30 00:00:01] ✅ Prerequisites check passed

[2025-11-30 00:00:01] Creating pre-deployment backup...
[2025-11-30 00:00:02] ✅ Backup created: .moai/backups/swarm-20251130-000002.db.gz

[2025-11-30 00:00:02] Setting up production database...
[INFO] Optimizing database...
[2025-11-30 00:00:03] ✅ Database setup complete

[2025-11-30 00:00:03] Running health checks...
[2025-11-30 00:00:04] ✅ Health checks passed

[2025-11-30 00:00:04] Deploying MoAI-Flow production...
[2025-11-30 00:00:05] ✅ Application deployed

[2025-11-30 00:00:05] Validating deployment...
[2025-11-30 00:00:06] ✅ Deployment validation successful

════════════════════════════════════════════════════════════
[2025-11-30 00:00:06] ✅ Deployment completed successfully!
════════════════════════════════════════════════════════════

Next steps:
  1. Monitor logs for 24 hours
  2. Run load tests: pytest tests/load/ -v
  3. Check health: python3 -c 'from moai_flow.memory import SwarmDB; SwarmDB()'
```

---

### Method 2: Manual Deployment

**For custom deployment scenarios**

#### Step 1: Environment Setup

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install production dependencies
pip install -e .

# Verify installation
python3 -c "from moai_flow.memory import SwarmDB; print('✅ Installed')"
```

#### Step 2: Configuration

```bash
# Set environment variables
export MOAI_ENV=production
export MOAI_DB_PATH=.moai/memory/swarm.db
export MOAI_LOG_LEVEL=INFO

# Create required directories
mkdir -p .moai/memory .moai/logs logs
```

#### Step 3: Database Initialization

```bash
# Initialize database
python3 -c "from moai_flow.memory.swarm_db import SwarmDB; SwarmDB()"

# Optimize for production
sqlite3 .moai/memory/swarm.db <<EOF
PRAGMA journal_mode=WAL;
PRAGMA cache_size=10000;
VACUUM;
EOF

# Set file permissions
chmod 600 .moai/memory/swarm.db
chmod 700 .moai/memory/
```

#### Step 4: Validation

```bash
# Run health checks
python3 -c "
from moai_flow.memory.swarm_db import SwarmDB
db = SwarmDB()
print('✅ Database healthy')
"

# Run tests
pytest tests/ -v --maxfail=5
```

---

### Method 3: Docker Deployment

**For containerized environments**

#### Step 1: Build Docker Image

```bash
# Build image
docker build -t moai-flow:1.0.0 .

# Tag as latest
docker tag moai-flow:1.0.0 moai-flow:latest
```

#### Step 2: Run Container

```bash
# Create volumes
docker volume create moai-data

# Run container
docker run -d \
  --name moai-flow \
  --restart unless-stopped \
  -v moai-data:/app/.moai \
  -e MOAI_ENV=production \
  -e MOAI_LOG_LEVEL=INFO \
  -p 8000:8000 \
  -p 9090:9090 \
  moai-flow:latest

# Check health
docker exec moai-flow python3 -c "from moai_flow.memory import SwarmDB; SwarmDB()"
```

#### Step 3: Docker Compose (Full Stack)

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f moai-flow

# Stop services
docker-compose down
```

**Services included**:
- `moai-flow` - Main application
- `postgres` (optional) - PostgreSQL database
- `prometheus` (optional) - Metrics collection
- `grafana` (optional) - Metrics visualization

---

### Method 4: Kubernetes Deployment

**For enterprise orchestration**

#### Step 1: Create Namespace

```bash
kubectl create namespace moai-flow
kubectl config set-context --current --namespace=moai-flow
```

#### Step 2: Deploy Application

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: moai-flow
  namespace: moai-flow
spec:
  replicas: 3
  selector:
    matchLabels:
      app: moai-flow
  template:
    metadata:
      labels:
        app: moai-flow
    spec:
      containers:
      - name: moai-flow
        image: moai-flow:latest
        env:
        - name: MOAI_ENV
          value: "production"
        - name: MOAI_LOG_LEVEL
          value: "INFO"
        resources:
          limits:
            cpu: "2"
            memory: "2Gi"
          requests:
            cpu: "1"
            memory: "512Mi"
        livenessProbe:
          exec:
            command:
            - python3
            - -c
            - "from moai_flow.memory import SwarmDB; SwarmDB()"
          initialDelaySeconds: 30
          periodSeconds: 60
        readinessProbe:
          exec:
            command:
            - python3
            - -c
            - "from moai_flow.memory import SwarmDB; SwarmDB()"
          initialDelaySeconds: 10
          periodSeconds: 30
```

```bash
# Apply deployment
kubectl apply -f deployment.yaml

# Check status
kubectl get pods
kubectl describe pod moai-flow-xxx

# View logs
kubectl logs -f deployment/moai-flow
```

---

## Configuration

### Environment Variables

**Production Configuration** (`.env` or environment):

```bash
# Environment Mode
MOAI_ENV=production

# Database Configuration
MOAI_DB_PATH=.moai/memory/swarm.db

# Logging
MOAI_LOG_LEVEL=INFO  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL

# Performance
MOAI_QUERY_TIMEOUT=20  # milliseconds
MOAI_BATCH_SIZE=1000

# Monitoring
MOAI_ENABLE_METRICS=true
MOAI_METRICS_PORT=9090

# Security
MOAI_ENABLE_AUDIT=true
MOAI_MAX_EVENTS=1000000  # Auto-cleanup threshold
```

### Configuration File

**`.moai/config/production.json`**:

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

## Monitoring

### Health Check Commands

**Quick Health Check**:
```bash
python3 -c "from moai_flow.memory import SwarmDB; SwarmDB(); print('✅ Healthy')"
```

**Comprehensive Health Check**:
```bash
python3 <<EOF
from moai_flow.memory.swarm_db import SwarmDB
import os

db = SwarmDB()

# Check database file exists
db_path = '.moai/memory/swarm.db'
assert os.path.exists(db_path), f"Database file missing: {db_path}"

# Check database size
db_size = os.path.getsize(db_path)
print(f"Database size: {db_size / (1024*1024):.2f} MB")

# Check connection pool
print(f"Connection pool size: {db.pool_size}")

# Test query
events = db.get_events_by_type('agent_spawned', limit=1)
print(f"✅ Database queries working")

print("✅ All health checks passed")
EOF
```

### Log Monitoring

```bash
# Application logs
tail -f logs/moai-flow.log

# Deployment logs
tail -f logs/deployment-*.log

# Docker logs (if using Docker)
docker logs -f moai-flow
```

### Metrics Monitoring

**Prometheus Metrics** (if enabled):
```bash
# Access metrics endpoint
curl http://localhost:9090/metrics

# Key metrics:
# - moai_flow_events_total
# - moai_flow_agents_active
# - moai_flow_query_duration_seconds
# - moai_flow_db_size_bytes
```

**Database Metrics**:
```bash
# Database size
du -h .moai/memory/swarm.db

# Event count
sqlite3 .moai/memory/swarm.db "SELECT COUNT(*) FROM events;"

# Active agents
sqlite3 .moai/memory/swarm.db "SELECT COUNT(DISTINCT agent_id) FROM events WHERE event_type='agent_spawned';"
```

---

## Troubleshooting

### Common Issues

#### Issue 1: Database Lock Errors

**Symptoms**:
```
Error: database is locked
```

**Solution**:
```bash
# Enable WAL mode for better concurrency
sqlite3 .moai/memory/swarm.db "PRAGMA journal_mode=WAL;"

# Check for long-running transactions
lsof .moai/memory/swarm.db
```

#### Issue 2: Slow Queries

**Symptoms**:
```
Warning: Query took 150ms (expected <20ms)
```

**Solution**:
```bash
# Optimize database
sqlite3 .moai/memory/swarm.db "VACUUM;"

# Rebuild indexes
sqlite3 .moai/memory/swarm.db "REINDEX;"

# Check index usage
sqlite3 .moai/memory/swarm.db ".schema" | grep INDEX
```

#### Issue 3: High Memory Usage

**Symptoms**:
```
Warning: Memory usage 85%
```

**Solution**:
```bash
# Reduce token budget
export MOAI_TOKEN_BUDGET=100000

# Limit concurrent agents
export MOAI_MAX_AGENTS=5

# Clean up old events
python3 -c "
from moai_flow.memory import SwarmDB
db = SwarmDB()
# Cleanup events older than 30 days
"
```

#### Issue 4: Import Errors

**Symptoms**:
```
ImportError: No module named 'moai_flow'
```

**Solution**:
```bash
# Reinstall package
pip uninstall moai-flow -y
pip install -e .

# Verify installation
pip list | grep moai-flow
python3 -c "import moai_flow; print(moai_flow.__version__)"
```

### Debug Mode

```bash
# Enable debug logging
export MOAI_LOG_LEVEL=DEBUG

# Run with verbose output
python3 -m moai_flow.server --debug --verbose

# Check Python path
python3 -c "import sys; print('\n'.join(sys.path))"
```

---

## Rollback Procedures

### Automatic Rollback

**The deployment script automatically rolls back on failure**:
- Stops services
- Restores from latest backup
- Logs rollback actions

### Manual Rollback

#### Step 1: Stop Services

```bash
# Docker
docker-compose down

# Or Kubernetes
kubectl delete deployment moai-flow

# Or local process
pkill -f moai_flow
```

#### Step 2: Restore Database

```bash
# List backups
ls -lah .moai/backups/

# Restore from backup
gunzip -c .moai/backups/swarm-20251130-000000.db.gz > .moai/memory/swarm.db

# Verify integrity
sqlite3 .moai/memory/swarm.db "PRAGMA integrity_check;"
```

#### Step 3: Restart Services

```bash
# Docker
docker-compose up -d

# Or Kubernetes
kubectl apply -f deployment.yaml

# Or local
./scripts/deploy_production.sh
```

#### Step 4: Validate Rollback

```bash
# Health check
python3 -c "from moai_flow.memory import SwarmDB; SwarmDB(); print('✅ Rollback successful')"

# Check logs
tail -f logs/moai-flow.log
```

---

## Post-Deployment Checklist

### Immediate Validation (0-1 hour)

- [ ] **Health checks passing**
  ```bash
  ./scripts/deploy_production.sh  # Should show ✅
  ```

- [ ] **Database operational**
  ```bash
  python3 -c "from moai_flow.memory import SwarmDB; SwarmDB()"
  ```

- [ ] **Logs clean** (no critical errors)
  ```bash
  grep -i error logs/moai-flow.log
  ```

- [ ] **Metrics collecting** (if enabled)
  ```bash
  curl http://localhost:9090/metrics
  ```

### Short-Term Monitoring (1-24 hours)

- [ ] **Monitor resource usage**
  ```bash
  # CPU, memory, disk
  top -p $(pgrep -f moai_flow)
  df -h
  ```

- [ ] **Monitor database growth**
  ```bash
  watch -n 300 'du -h .moai/memory/swarm.db'
  ```

- [ ] **Monitor error rate**
  ```bash
  grep -c ERROR logs/moai-flow.log
  ```

- [ ] **Run load tests**
  ```bash
  pytest tests/load/test_load_performance.py -v
  ```

### Long-Term Validation (24-48 hours)

- [ ] **Uptime verification**
  ```bash
  # Check if service has been running continuously
  ps -p $(pgrep -f moai_flow) -o etime=
  ```

- [ ] **Performance benchmarks**
  ```bash
  # Query performance <20ms
  # Memory usage <2GB for 100 agents
  # Error rate <0.1%
  ```

- [ ] **Backup verification**
  ```bash
  ls -lah .moai/backups/
  # Should have automated backups
  ```

- [ ] **Documentation updated**
  - Deployment date recorded
  - Configuration changes documented
  - Known issues logged

---

## Production Best Practices

### Security

1. **File Permissions**
   ```bash
   chmod 600 .moai/memory/swarm.db
   chmod 700 .moai/memory/
   chmod 600 .env
   ```

2. **Environment Variables**
   - Use `.env` files (never commit to git)
   - Use secret management tools (Vault, AWS Secrets Manager)

3. **Network Security**
   - Bind to localhost only (if not using reverse proxy)
   - Use HTTPS for external access
   - Configure firewall rules

### Performance

1. **Database Optimization**
   - WAL mode enabled
   - Regular VACUUM operations
   - Index maintenance

2. **Resource Limits**
   - Set memory limits (Docker/Kubernetes)
   - Configure connection pooling
   - Monitor query performance

### Maintenance

1. **Regular Backups**
   ```bash
   # Daily automated backups
   0 2 * * * /path/to/backup-script.sh
   ```

2. **Log Rotation**
   ```bash
   # Configure logrotate
   /var/log/moai-flow/*.log {
       daily
       rotate 7
       compress
       delaycompress
       notifempty
   }
   ```

3. **Monitoring**
   - Set up alerts for critical errors
   - Monitor resource usage trends
   - Track performance metrics

---

## Support

**Documentation**:
- [README.md](../../README.md) - Project overview
- [DEPLOYMENT.md](../../DEPLOYMENT.md) - Detailed deployment guide
- [PRODUCTION-READINESS-CHECKLIST.md](../../PRODUCTION-READINESS-CHECKLIST.md) - Pre-deployment checklist

**Community**:
- GitHub Issues: https://github.com/superdisco-agents/moai-flow/issues
- Discussions: https://github.com/superdisco-agents/moai-flow/discussions

---

**Version**: 1.0.0
**Last Updated**: 2025-11-30
**Status**: Production Ready
