#!/bin/bash
# Production Deployment Script for MoAI-Flow
# Version: 1.0.0
# Last Updated: 2025-11-30

set -euo pipefail  # Exit on error, undefined variables, pipe failures

# ============================================================================
# Configuration
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DEPLOYMENT_ENV="${MOAI_ENV:-production}"
DEPLOYMENT_DATE=$(date +%Y%m%d-%H%M%S)
LOG_FILE="${PROJECT_ROOT}/logs/deployment-${DEPLOYMENT_DATE}.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ============================================================================
# Logging Functions
# ============================================================================

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $*" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $*" | tee -a "$LOG_FILE" >&2
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $*" | tee -a "$LOG_FILE"
}

log_info() {
    echo -e "${BLUE}[INFO]${NC} $*" | tee -a "$LOG_FILE"
}

# ============================================================================
# Pre-Deployment Checks
# ============================================================================

check_prerequisites() {
    log "Checking prerequisites..."

    # Check Python version
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        log_info "Python version: $PYTHON_VERSION"

        # Verify Python 3.11+
        if [[ $(python3 -c "import sys; print(sys.version_info >= (3, 11))") != "True" ]]; then
            log_error "Python 3.11+ required, found $PYTHON_VERSION"
            return 1
        fi
    else
        log_error "Python 3 not found"
        return 1
    fi

    # Check required directories
    for dir in .moai/memory .moai/logs logs; do
        if [[ ! -d "${PROJECT_ROOT}/${dir}" ]]; then
            log_info "Creating directory: $dir"
            mkdir -p "${PROJECT_ROOT}/${dir}"
        fi
    done

    # Check SQLite
    if ! command -v sqlite3 &> /dev/null; then
        log_warning "sqlite3 CLI not found (optional)"
    else
        log_info "SQLite version: $(sqlite3 --version | cut -d' ' -f1)"
    fi

    # Check disk space
    AVAILABLE_SPACE=$(df -h "${PROJECT_ROOT}" | awk 'NR==2 {print $4}')
    log_info "Available disk space: $AVAILABLE_SPACE"

    log "✅ Prerequisites check passed"
}

# ============================================================================
# Database Setup
# ============================================================================

setup_database() {
    log "Setting up production database..."

    cd "$PROJECT_ROOT"

    # Initialize database
    python3 -c "
from moai_flow.memory.swarm_db import SwarmDB
db = SwarmDB()
print('✅ Database initialized')
"

    # Optimize database for production
    if command -v sqlite3 &> /dev/null && [[ -f .moai/memory/swarm.db ]]; then
        log_info "Optimizing database..."

        # Enable WAL mode for better concurrency
        sqlite3 .moai/memory/swarm.db "PRAGMA journal_mode=WAL;"

        # Increase cache size
        sqlite3 .moai/memory/swarm.db "PRAGMA cache_size=10000;"

        # Run VACUUM to optimize
        sqlite3 .moai/memory/swarm.db "VACUUM;"

        log "✅ Database optimized"
    else
        log_warning "sqlite3 not available, skipping optimization"
    fi

    # Set file permissions
    chmod 600 .moai/memory/swarm.db 2>/dev/null || true
    chmod 700 .moai/memory/ 2>/dev/null || true

    log "✅ Database setup complete"
}

# ============================================================================
# Health Checks
# ============================================================================

run_health_checks() {
    log "Running health checks..."

    cd "$PROJECT_ROOT"

    # Test database connection
    python3 -c "
from moai_flow.memory.swarm_db import SwarmDB
db = SwarmDB()
print('✅ Database connection healthy')
" || {
        log_error "Database health check failed"
        return 1
    }

    # Check Python imports
    python3 -c "
import moai_flow
from moai_flow.memory import SwarmDB
from moai_flow.memory.semantic_memory import SemanticMemory
from moai_flow.memory.episodic_memory import EpisodicMemory
print('✅ All imports successful')
" || {
        log_error "Import health check failed"
        return 1
    }

    log "✅ Health checks passed"
}

# ============================================================================
# Backup
# ============================================================================

create_backup() {
    log "Creating pre-deployment backup..."

    BACKUP_DIR="${PROJECT_ROOT}/.moai/backups"
    mkdir -p "$BACKUP_DIR"

    if [[ -f "${PROJECT_ROOT}/.moai/memory/swarm.db" ]]; then
        BACKUP_FILE="${BACKUP_DIR}/swarm-${DEPLOYMENT_DATE}.db"
        cp "${PROJECT_ROOT}/.moai/memory/swarm.db" "$BACKUP_FILE"

        # Compress backup
        gzip "$BACKUP_FILE"

        log "✅ Backup created: ${BACKUP_FILE}.gz"

        # Cleanup old backups (keep last 7 days)
        find "$BACKUP_DIR" -name "swarm-*.db.gz" -mtime +7 -delete 2>/dev/null || true
    else
        log_info "No existing database to backup"
    fi
}

# ============================================================================
# Deployment
# ============================================================================

deploy_application() {
    log "Deploying MoAI-Flow ${DEPLOYMENT_ENV}..."

    cd "$PROJECT_ROOT"

    # Set environment variables
    export MOAI_ENV="$DEPLOYMENT_ENV"
    export MOAI_DB_PATH=".moai/memory/swarm.db"
    export MOAI_LOG_LEVEL="INFO"

    # For Docker deployment
    if command -v docker &> /dev/null && [[ -f docker-compose.yml ]]; then
        log_info "Docker available, checking Docker deployment..."

        if docker info &> /dev/null; then
            log_info "Deploying with Docker Compose..."
            docker-compose down || true
            docker-compose build
            docker-compose up -d

            # Wait for services
            sleep 5

            # Check service health
            docker-compose ps

            log "✅ Docker deployment complete"
        else
            log_warning "Docker daemon not running, skipping Docker deployment"
        fi
    else
        log_info "Docker not available, using local deployment"
    fi

    log "✅ Application deployed"
}

# ============================================================================
# Post-Deployment Validation
# ============================================================================

validate_deployment() {
    log "Validating deployment..."

    cd "$PROJECT_ROOT"

    # Test core functionality
    python3 -c "
from moai_flow.memory.swarm_db import SwarmDB
from datetime import datetime, UTC

db = SwarmDB()

# Test insert
test_event = {
    'event_type': 'deployment_test',
    'timestamp': datetime.now(UTC).isoformat(),
    'agent_id': 'deployment_validator',
    'metadata': {'deployment_date': '$DEPLOYMENT_DATE'}
}
db.insert_event(test_event)

# Test query
recent_events = db.get_events_by_type('deployment_test', limit=1)
assert len(recent_events) > 0, 'Failed to retrieve test event'

print('✅ Deployment validation passed')
"

    if [[ $? -eq 0 ]]; then
        log "✅ Deployment validation successful"
        return 0
    else
        log_error "Deployment validation failed"
        return 1
    fi
}

# ============================================================================
# Monitoring Setup
# ============================================================================

setup_monitoring() {
    log "Setting up monitoring..."

    # Create monitoring log
    MONITOR_LOG="${PROJECT_ROOT}/logs/monitor-${DEPLOYMENT_DATE}.log"

    cat > "$MONITOR_LOG" <<EOF
MoAI-Flow Deployment Monitoring
================================
Deployment Date: $(date)
Environment: ${DEPLOYMENT_ENV}

Monitor these metrics:
- Database size: du -h .moai/memory/swarm.db
- Active processes: ps aux | grep moai
- Memory usage: free -h (Linux) or vm_stat (macOS)
- Disk space: df -h
- Logs: tail -f logs/moai-flow.log

Health Check Command:
python3 -c "from moai_flow.memory.swarm_db import SwarmDB; print('✅ Healthy')"
EOF

    log_info "Monitoring log created: $MONITOR_LOG"
    log "✅ Monitoring setup complete"
}

# ============================================================================
# Rollback
# ============================================================================

rollback_deployment() {
    log_error "Deployment failed, initiating rollback..."

    # Stop services
    if command -v docker &> /dev/null && [[ -f docker-compose.yml ]]; then
        docker-compose down 2>/dev/null || true
    fi

    # Restore from backup
    LATEST_BACKUP=$(ls -t "${PROJECT_ROOT}/.moai/backups/swarm-*.db.gz" 2>/dev/null | head -1)

    if [[ -n "$LATEST_BACKUP" ]]; then
        log_info "Restoring from backup: $LATEST_BACKUP"
        gunzip -c "$LATEST_BACKUP" > "${PROJECT_ROOT}/.moai/memory/swarm.db"
        log "✅ Rollback complete"
    else
        log_warning "No backup found for rollback"
    fi
}

# ============================================================================
# Main Deployment Flow
# ============================================================================

main() {
    echo "════════════════════════════════════════════════════════════"
    echo "  MoAI-Flow Production Deployment"
    echo "  Environment: ${DEPLOYMENT_ENV}"
    echo "  Date: $(date)"
    echo "════════════════════════════════════════════════════════════"
    echo ""

    # Create log directory
    mkdir -p "$(dirname "$LOG_FILE")"
    log "Starting deployment process..."

    # Deployment steps
    if ! check_prerequisites; then
        log_error "Prerequisites check failed"
        exit 1
    fi

    if ! create_backup; then
        log_error "Backup creation failed"
        exit 1
    fi

    if ! setup_database; then
        log_error "Database setup failed"
        rollback_deployment
        exit 1
    fi

    if ! run_health_checks; then
        log_error "Health checks failed"
        rollback_deployment
        exit 1
    fi

    if ! deploy_application; then
        log_error "Application deployment failed"
        rollback_deployment
        exit 1
    fi

    if ! validate_deployment; then
        log_error "Deployment validation failed"
        rollback_deployment
        exit 1
    fi

    setup_monitoring

    echo ""
    echo "════════════════════════════════════════════════════════════"
    log "✅ Deployment completed successfully!"
    echo "════════════════════════════════════════════════════════════"
    echo ""
    log_info "Deployment log: $LOG_FILE"
    log_info "Monitor with: tail -f $LOG_FILE"
    echo ""
    log_info "Next steps:"
    echo "  1. Monitor logs for 24 hours"
    echo "  2. Run load tests: pytest tests/load/ -v"
    echo "  3. Check health: python3 -c 'from moai_flow.memory import SwarmDB; SwarmDB()'"
    echo ""
}

# ============================================================================
# Error Handling
# ============================================================================

trap 'log_error "Deployment interrupted"; rollback_deployment; exit 1' INT TERM

# ============================================================================
# Execute
# ============================================================================

main "$@"
