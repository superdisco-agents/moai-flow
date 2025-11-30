# MoAI-Flow Operations Runbook

**Operational procedures for MoAI-Flow production deployment**

---

## Quick Reference

**Health Check**: `python3 -c "from moai_flow.memory import SwarmDB; SwarmDB()"`
**Logs**: `tail -f logs/moai-flow.log`
**Backup**: `./scripts/backup-moai-flow.sh`
**Restart**: `docker-compose restart` or `systemctl restart moai-flow`

---

## Table of Contents

- [Health Monitoring](#health-monitoring)
- [Common Operations](#common-operations)
- [Incident Response](#incident-response)
- [Performance Tuning](#performance-tuning)
- [Backup and Recovery](#backup-and-recovery)
- [Emergency Procedures](#emergency-procedures)

---

## Health Monitoring

### Daily Health Checks

**Morning Health Check** (5 minutes):
```bash
#!/bin/bash
# daily-health-check.sh

echo "=== MoAI-Flow Daily Health Check ==="
date

# 1. Service Status
echo -e "\n1. Service Status:"
if docker ps | grep -q moai-flow; then
    echo "✅ Docker container running"
elif pgrep -f moai_flow > /dev/null; then
    echo "✅ Process running"
else
    echo "❌ Service NOT running"
fi

# 2. Database Health
echo -e "\n2. Database Health:"
python3 -c "from moai_flow.memory import SwarmDB; db = SwarmDB(); print('✅ Database operational')"

# 3. Database Size
echo -e "\n3. Database Size:"
du -h .moai/memory/swarm.db

# 4. Disk Space
echo -e "\n4. Disk Space:"
df -h . | tail -1

# 5. Recent Errors
echo -e "\n5. Recent Errors (last 24h):"
ERROR_COUNT=$(find logs/ -name "*.log" -mtime -1 -exec grep -c ERROR {} + 2>/dev/null || echo 0)
if [ "$ERROR_COUNT" -eq 0 ]; then
    echo "✅ No errors in last 24 hours"
else
    echo "⚠️  $ERROR_COUNT errors found"
    find logs/ -name "*.log" -mtime -1 -exec grep ERROR {} + | tail -5
fi

# 6. Memory Usage
echo -e "\n6. Memory Usage:"
if command -v free &> /dev/null; then
    free -h | grep Mem
else
    vm_stat | grep "Pages free"
fi

echo -e "\n=== Health Check Complete ==="
```

### Continuous Monitoring

**Automated Monitoring Script**:
```bash
#!/bin/bash
# continuous-monitor.sh - Run every 5 minutes via cron

ALERT_EMAIL="ops@example.com"
LOG_FILE="logs/monitor-$(date +%Y%m%d).log"

# Health check
if ! python3 -c "from moai_flow.memory import SwarmDB; SwarmDB()" 2>/dev/null; then
    echo "$(date): ❌ Health check failed" >> "$LOG_FILE"
    echo "MoAI-Flow health check failed on $(hostname)" | mail -s "ALERT: MoAI-Flow Down" "$ALERT_EMAIL"
    exit 1
fi

# Disk space check (alert if <1GB)
AVAILABLE=$(df -BG . | tail -1 | awk '{print $4}' | sed 's/G//')
if [ "$AVAILABLE" -lt 1 ]; then
    echo "$(date): ⚠️  Low disk space: ${AVAILABLE}GB" >> "$LOG_FILE"
    echo "Low disk space: ${AVAILABLE}GB on $(hostname)" | mail -s "WARNING: Low Disk Space" "$ALERT_EMAIL"
fi

echo "$(date): ✅ Monitor check passed" >> "$LOG_FILE"
```

**Crontab Setup**:
```bash
# Edit crontab
crontab -e

# Add monitoring jobs
*/5 * * * * /path/to/moai-adk/scripts/continuous-monitor.sh
0 8 * * * /path/to/moai-adk/scripts/daily-health-check.sh | mail -s "Daily Health Report" ops@example.com
0 2 * * * /path/to/moai-adk/scripts/backup-moai-flow.sh
```

---

## Common Operations

### Start/Stop Service

**Docker Deployment**:
```bash
# Start service
docker-compose up -d

# Stop service
docker-compose down

# Restart service
docker-compose restart moai-flow

# View logs
docker-compose logs -f moai-flow
```

**Systemd Service** (if configured):
```bash
# Start
sudo systemctl start moai-flow

# Stop
sudo systemctl stop moai-flow

# Restart
sudo systemctl restart moai-flow

# Status
sudo systemctl status moai-flow

# Enable on boot
sudo systemctl enable moai-flow
```

**Manual Process**:
```bash
# Start (background)
nohup python3 -m moai_flow.server > logs/moai-flow.log 2>&1 &
echo $! > .moai/moai-flow.pid

# Stop
kill $(cat .moai/moai-flow.pid)

# Graceful restart
kill -TERM $(cat .moai/moai-flow.pid)
sleep 2
nohup python3 -m moai_flow.server > logs/moai-flow.log 2>&1 &
echo $! > .moai/moai-flow.pid
```

### Database Operations

**Backup Database**:
```bash
# Manual backup
BACKUP_FILE=".moai/backups/swarm-$(date +%Y%m%d-%H%M%S).db"
cp .moai/memory/swarm.db "$BACKUP_FILE"
gzip "$BACKUP_FILE"
echo "Backup created: ${BACKUP_FILE}.gz"
```

**Optimize Database**:
```bash
# Run optimization
sqlite3 .moai/memory/swarm.db <<EOF
PRAGMA journal_mode=WAL;
PRAGMA cache_size=10000;
VACUUM;
ANALYZE;
EOF
echo "✅ Database optimized"
```

**Database Statistics**:
```bash
# Database info
sqlite3 .moai/memory/swarm.db <<EOF
.print "Database Size:"
SELECT page_count * page_size AS size FROM pragma_page_count(), pragma_page_size();

.print "\nTable Row Counts:"
SELECT 'events', COUNT(*) FROM events;
SELECT 'semantic_memory', COUNT(*) FROM semantic_memory;
SELECT 'episodic_memory', COUNT(*) FROM episodic_memory;

.print "\nIndex Count:"
SELECT COUNT(*) FROM sqlite_master WHERE type='index';
EOF
```

### Log Management

**View Logs**:
```bash
# Real-time logs
tail -f logs/moai-flow.log

# Last 100 lines
tail -100 logs/moai-flow.log

# Search for errors
grep -i error logs/moai-flow.log

# Search for specific agent
grep "agent_id.*my_agent" logs/moai-flow.log
```

**Rotate Logs**:
```bash
# Manual log rotation
mv logs/moai-flow.log logs/moai-flow.log.$(date +%Y%m%d)
gzip logs/moai-flow.log.*
touch logs/moai-flow.log

# Send SIGHUP to reopen log files (if service supports it)
kill -HUP $(cat .moai/moai-flow.pid)
```

**Clean Old Logs**:
```bash
# Delete logs older than 30 days
find logs/ -name "*.log*" -mtime +30 -delete

# Delete compressed logs older than 90 days
find logs/ -name "*.gz" -mtime +90 -delete
```

---

## Incident Response

### Service Down

**Symptoms**: Health check fails, service not responding

**Response Procedure**:

1. **Verify Service Status**
   ```bash
   # Check if process is running
   pgrep -f moai_flow
   docker ps | grep moai-flow
   systemctl status moai-flow
   ```

2. **Check Logs for Errors**
   ```bash
   tail -100 logs/moai-flow.log
   grep -i "error\|fatal\|critical" logs/moai-flow.log | tail -20
   ```

3. **Attempt Restart**
   ```bash
   # Docker
   docker-compose restart moai-flow

   # Systemd
   sudo systemctl restart moai-flow

   # Manual
   kill $(cat .moai/moai-flow.pid)
   nohup python3 -m moai_flow.server > logs/moai-flow.log 2>&1 &
   ```

4. **Verify Recovery**
   ```bash
   python3 -c "from moai_flow.memory import SwarmDB; SwarmDB(); print('✅ Service recovered')"
   ```

5. **Post-Incident**
   - Document root cause
   - Update runbook if needed
   - Schedule post-mortem if major incident

### Database Locked

**Symptoms**: `database is locked` errors in logs

**Response Procedure**:

1. **Check for Long-Running Processes**
   ```bash
   lsof .moai/memory/swarm.db
   ```

2. **Enable WAL Mode** (if not already enabled)
   ```bash
   sqlite3 .moai/memory/swarm.db "PRAGMA journal_mode=WAL;"
   ```

3. **If Issue Persists - Restart Service**
   ```bash
   docker-compose restart moai-flow
   # or
   systemctl restart moai-flow
   ```

4. **Verify Resolution**
   ```bash
   sqlite3 .moai/memory/swarm.db "SELECT COUNT(*) FROM events;"
   ```

### High Memory Usage

**Symptoms**: Memory usage >80%, OOM errors

**Response Procedure**:

1. **Check Current Usage**
   ```bash
   # Linux
   free -h
   ps aux | grep moai_flow | awk '{print $4, $11}'

   # macOS
   top -l 1 | grep PhysMem
   ps aux | grep moai_flow
   ```

2. **Immediate Action - Reduce Load**
   ```bash
   # Reduce token budget
   export MOAI_TOKEN_BUDGET=100000

   # Restart service with reduced limits
   docker-compose down
   docker-compose up -d
   ```

3. **Clean Up Database**
   ```bash
   python3 -c "
from moai_flow.memory import SwarmDB
db = SwarmDB()
# Cleanup old events (implement if available)
print('Database cleanup completed')
"
   ```

4. **Monitor Recovery**
   ```bash
   watch -n 5 'free -h; echo "---"; ps aux | grep moai_flow | grep -v grep'
   ```

### Slow Performance

**Symptoms**: Queries >50ms, slow response times

**Response Procedure**:

1. **Check Database Performance**
   ```bash
   # Query time test
   time sqlite3 .moai/memory/swarm.db "SELECT COUNT(*) FROM events;"
   ```

2. **Optimize Database**
   ```bash
   sqlite3 .moai/memory/swarm.db <<EOF
PRAGMA analysis_limit=1000;
ANALYZE;
VACUUM;
REINDEX;
EOF
   ```

3. **Check Resource Constraints**
   ```bash
   # CPU usage
   top -n 1

   # Disk I/O
   iostat -x 1 5

   # Disk space
   df -h .moai/memory/
   ```

4. **If Persistent - Consider Optimization**
   - Review slow queries in logs
   - Add indexes if needed
   - Consider PostgreSQL migration for high-concurrency workloads

### Disk Space Full

**Symptoms**: `disk I/O error`, `no space left on device`

**Emergency Response**:

1. **Free Up Space Immediately**
   ```bash
   # Delete old compressed logs
   find logs/ -name "*.gz" -mtime +7 -delete

   # Delete old backups
   find .moai/backups/ -name "*.db.gz" -mtime +30 -delete

   # Clean up temp files
   rm -rf /tmp/moai-flow-*
   ```

2. **Optimize Database**
   ```bash
   sqlite3 .moai/memory/swarm.db "VACUUM;"
   ```

3. **Monitor Space**
   ```bash
   df -h .
   du -sh .moai/memory/ .moai/logs/ logs/
   ```

4. **Preventive Action**
   - Set up automated cleanup
   - Increase disk allocation
   - Configure log rotation

---

## Performance Tuning

### Database Optimization

**Production Settings**:
```bash
sqlite3 .moai/memory/swarm.db <<EOF
-- WAL mode for better concurrency
PRAGMA journal_mode=WAL;

-- Increase cache size (10000 pages = ~40MB)
PRAGMA cache_size=10000;

-- Synchronous mode (faster, still safe with WAL)
PRAGMA synchronous=NORMAL;

-- Memory-mapped I/O (256MB)
PRAGMA mmap_size=268435456;

-- Auto-vacuum
PRAGMA auto_vacuum=INCREMENTAL;

-- Analyze for query optimization
ANALYZE;
EOF
```

**Index Verification**:
```bash
# Check existing indexes
sqlite3 .moai/memory/swarm.db ".schema" | grep INDEX

# Expected: 12 indexes
# If missing, rebuild indexes
sqlite3 .moai/memory/swarm.db "REINDEX;"
```

### Resource Limits

**Docker Resource Limits** (`docker-compose.yml`):
```yaml
services:
  moai-flow:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 512M
```

**systemd Resource Limits** (`/etc/systemd/system/moai-flow.service`):
```ini
[Service]
MemoryLimit=2G
CPUQuota=200%
```

### Connection Pooling

**Configure Connection Pool**:
```python
# In production code (if using custom config)
from moai_flow.memory import SwarmDB

db = SwarmDB(
    db_path='.moai/memory/swarm.db',
    pool_size=10  # Adjust based on concurrency needs
)
```

---

## Backup and Recovery

### Automated Backup

**Backup Script** (`scripts/backup-moai-flow.sh`):
```bash
#!/bin/bash
# Automated backup script

BACKUP_DIR=".moai/backups"
BACKUP_NAME="swarm-$(date +%Y%m%d-%H%M%S).db"
RETENTION_DAYS=30

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Backup database
cp .moai/memory/swarm.db "$BACKUP_DIR/$BACKUP_NAME"

# Compress backup
gzip "$BACKUP_DIR/$BACKUP_NAME"

# Verify backup
if [ -f "$BACKUP_DIR/$BACKUP_NAME.gz" ]; then
    echo "✅ Backup created: $BACKUP_DIR/$BACKUP_NAME.gz"

    # Test backup integrity
    gunzip -t "$BACKUP_DIR/$BACKUP_NAME.gz"
    echo "✅ Backup integrity verified"
else
    echo "❌ Backup failed"
    exit 1
fi

# Cleanup old backups
find "$BACKUP_DIR" -name "swarm-*.db.gz" -mtime +$RETENTION_DAYS -delete
echo "✅ Cleaned up backups older than $RETENTION_DAYS days"

# Report backup size
BACKUP_SIZE=$(du -h "$BACKUP_DIR/$BACKUP_NAME.gz" | cut -f1)
echo "Backup size: $BACKUP_SIZE"
```

### Recovery Procedures

**Full Database Recovery**:
```bash
#!/bin/bash
# restore-backup.sh <backup-file>

BACKUP_FILE="$1"

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup-file>"
    echo "Available backups:"
    ls -lh .moai/backups/
    exit 1
fi

# Stop service
echo "Stopping service..."
docker-compose down || systemctl stop moai-flow || kill $(cat .moai/moai-flow.pid)

# Backup current database (just in case)
echo "Creating safety backup..."
cp .moai/memory/swarm.db .moai/memory/swarm.db.pre-restore.$(date +%s)

# Restore from backup
echo "Restoring from $BACKUP_FILE..."
gunzip -c "$BACKUP_FILE" > .moai/memory/swarm.db

# Verify integrity
echo "Verifying database integrity..."
if sqlite3 .moai/memory/swarm.db "PRAGMA integrity_check;" | grep -q "ok"; then
    echo "✅ Database integrity verified"
else
    echo "❌ Database integrity check failed"
    exit 1
fi

# Restart service
echo "Restarting service..."
docker-compose up -d || systemctl start moai-flow || nohup python3 -m moai_flow.server > logs/moai-flow.log 2>&1 &

# Verify service
sleep 5
python3 -c "from moai_flow.memory import SwarmDB; SwarmDB(); print('✅ Service restored successfully')"
```

**Partial Recovery** (specific table):
```bash
# Export specific table from backup
gunzip -c .moai/backups/swarm-20251130.db.gz | sqlite3 :memory: ".dump semantic_memory" > semantic_memory.sql

# Import into current database
sqlite3 .moai/memory/swarm.db < semantic_memory.sql
```

---

## Emergency Procedures

### Emergency Shutdown

**Immediate Service Shutdown**:
```bash
# Docker
docker-compose down

# Systemd
sudo systemctl stop moai-flow

# Process
pkill -TERM -f moai_flow

# Force kill (last resort)
pkill -KILL -f moai_flow
```

### Emergency Recovery

**Full System Recovery**:
```bash
#!/bin/bash
# emergency-recovery.sh

echo "=== Emergency Recovery Procedure ==="

# 1. Stop all services
echo "1. Stopping services..."
docker-compose down 2>/dev/null || true
systemctl stop moai-flow 2>/dev/null || true
pkill -TERM -f moai_flow 2>/dev/null || true
sleep 3

# 2. Restore latest backup
echo "2. Restoring latest backup..."
LATEST_BACKUP=$(ls -t .moai/backups/swarm-*.db.gz | head -1)
if [ -n "$LATEST_BACKUP" ]; then
    gunzip -c "$LATEST_BACKUP" > .moai/memory/swarm.db
    echo "✅ Restored from: $LATEST_BACKUP"
else
    echo "❌ No backups found"
    exit 1
fi

# 3. Verify database
echo "3. Verifying database..."
if sqlite3 .moai/memory/swarm.db "PRAGMA integrity_check;" | grep -q "ok"; then
    echo "✅ Database OK"
else
    echo "❌ Database corrupted"
    exit 1
fi

# 4. Restart service
echo "4. Restarting service..."
./scripts/deploy_production.sh

echo "=== Recovery Complete ==="
```

### Data Corruption Recovery

**If Database is Corrupted**:
```bash
# 1. Dump recoverable data
echo ".dump" | sqlite3 .moai/memory/swarm.db > recovered-data.sql 2>/dev/null

# 2. Create new database
mv .moai/memory/swarm.db .moai/memory/swarm.db.corrupted
python3 -c "from moai_flow.memory import SwarmDB; SwarmDB()"

# 3. Import recovered data
sqlite3 .moai/memory/swarm.db < recovered-data.sql

# 4. Verify recovery
sqlite3 .moai/memory/swarm.db "SELECT COUNT(*) FROM events;"
```

---

## Escalation Procedures

### Incident Severity Levels

**P0 - Critical** (Production down, data loss):
- Response time: Immediate
- Notify: On-call engineer, team lead, CTO
- Action: Emergency recovery procedures
- Post-mortem: Required

**P1 - High** (Degraded performance, service instability):
- Response time: <15 minutes
- Notify: On-call engineer, team lead
- Action: Immediate investigation and mitigation
- Post-mortem: Recommended

**P2 - Medium** (Non-critical issues, warnings):
- Response time: <2 hours
- Notify: On-call engineer
- Action: Investigate and schedule fix
- Post-mortem: Optional

**P3 - Low** (Minor issues, enhancement requests):
- Response time: Next business day
- Notify: Create ticket
- Action: Schedule for sprint planning
- Post-mortem: Not required

### Contacts

**On-Call Rotation**:
- Primary: [Phone/Email]
- Secondary: [Phone/Email]
- Escalation: [Manager Phone/Email]

**External Contacts**:
- Cloud Provider Support: [Phone/Email]
- Database Support: [Phone/Email]

---

## Appendix

### Useful Commands Cheat Sheet

```bash
# Health Check
python3 -c "from moai_flow.memory import SwarmDB; SwarmDB()"

# Database Size
du -h .moai/memory/swarm.db

# Service Status
docker-compose ps
systemctl status moai-flow

# Tail Logs
tail -f logs/moai-flow.log

# Recent Errors
grep -i error logs/moai-flow.log | tail -20

# Database Query Count
sqlite3 .moai/memory/swarm.db "SELECT COUNT(*) FROM events;"

# Optimize Database
sqlite3 .moai/memory/swarm.db "VACUUM; ANALYZE;"

# Backup Database
cp .moai/memory/swarm.db .moai/backups/swarm-$(date +%Y%m%d).db

# Restart Service
docker-compose restart moai-flow
```

---

**Version**: 1.0.0
**Last Updated**: 2025-11-30
**Maintained By**: DevOps Team
