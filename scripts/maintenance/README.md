# Maintenance Scripts

Scripts for system maintenance, cleanup, and health monitoring.

## Available Scripts

### cleanup_logs.py
Clean up old log files.

```bash
python scripts/maintenance/cleanup_logs.py
python scripts/maintenance/cleanup_logs.py --days 30
python scripts/maintenance/cleanup_logs.py --dry-run
```

### manage_cache.py
Manage cache files and directories.

```bash
python scripts/maintenance/manage_cache.py clear
python scripts/maintenance/manage_cache.py stats
python scripts/maintenance/manage_cache.py optimize
```

### backup_data.py
Backup critical data and configurations.

```bash
python scripts/maintenance/backup_data.py
python scripts/maintenance/backup_data.py --destination /backups
```

### health_check.py
Perform system health checks.

```bash
python scripts/maintenance/health_check.py
python scripts/maintenance/health_check.py --verbose
```

### optimize_database.py
Optimize database files and indexes.

```bash
python scripts/maintenance/optimize_database.py
python scripts/maintenance/optimize_database.py --vacuum
```

## Usage Examples

### Daily Maintenance

```bash
# Clean old logs (keep 7 days)
python scripts/maintenance/cleanup_logs.py --days 7

# Clear cache
python scripts/maintenance/manage_cache.py clear

# Health check
python scripts/maintenance/health_check.py
```

### Weekly Maintenance

```bash
# Backup data
python scripts/maintenance/backup_data.py

# Optimize database
python scripts/maintenance/optimize_database.py

# Cache stats
python scripts/maintenance/manage_cache.py stats
```

### Automated Scheduling

```bash
# Cron example (daily at 2 AM)
0 2 * * * cd /path/to/moai-flow && python scripts/maintenance/cleanup_logs.py --days 7

# Cron example (weekly on Sunday at 3 AM)
0 3 * * 0 cd /path/to/moai-flow && python scripts/maintenance/backup_data.py
```
