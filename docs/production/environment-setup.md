# Production Environment Setup Guide

**Complete guide for setting up production, staging, and development environments**

---

## Table of Contents

- [Environment Overview](#environment-overview)
- [Development Environment](#development-environment)
- [Staging Environment](#staging-environment)
- [Production Environment](#production-environment)
- [Environment Variables](#environment-variables)
- [Infrastructure Requirements](#infrastructure-requirements)

---

## Environment Overview

### Environment Types

| Environment | Purpose | Uptime | Data | Users |
|-------------|---------|--------|------|-------|
| **Development** | Local testing | Variable | Synthetic | Developers only |
| **Staging** | Pre-production | 95% | Sanitized production | Internal team |
| **Production** | Live service | 99.9% | Real data | End users |

### Environment Parity

Maintain parity across environments:
- ✅ Same OS and Python version
- ✅ Same database engine (SQLite or PostgreSQL)
- ✅ Same dependency versions
- ✅ Same configuration structure
- ⚠️ Different resource limits
- ⚠️ Different monitoring settings

---

## Development Environment

### Setup

**1. Install Python 3.13**
```bash
# macOS (using Homebrew)
brew install python@3.13

# Ubuntu
sudo apt-get install python3.13

# Windows (using Chocolatey)
choco install python --version=3.13.0
```

**2. Clone Repository**
```bash
git clone https://github.com/superdisco-agents/moai-flow.git
cd moai-flow
```

**3. Create Virtual Environment**
```bash
python3.13 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

**4. Install Dependencies**
```bash
# Install with development dependencies
pip install -e ".[dev,security]"

# Or using uv (faster)
uv pip install -e ".[dev,security]"
```

**5. Configure Environment**
```bash
# Create .env file
cat <<EOF > .env
MOAI_ENV=development
MOAI_DB_PATH=.moai/memory/swarm.db
MOAI_LOG_LEVEL=DEBUG
MOAI_ENABLE_METRICS=true
EOF
```

**6. Initialize Database**
```bash
python -c "from moai_flow.memory import SwarmDB; SwarmDB()"
```

**7. Verify Setup**
```bash
pytest tests/ -v
```

### Development Tools

**Code Quality**:
```bash
# Linting
ruff check moai_flow/ tests/

# Code formatting
black moai_flow/ tests/

# Type checking
mypy moai_flow/ --ignore-missing-imports
```

**Testing**:
```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=moai_flow --cov-report=html

# Run specific test
pytest tests/moai_flow/memory/test_swarm_db.py::test_insert_event -v
```

**Pre-commit Hooks** (optional):
```bash
# Install pre-commit
pip install pre-commit

# Setup hooks
pre-commit install

# Run hooks manually
pre-commit run --all-files
```

---

## Staging Environment

### Purpose

Staging environment mimics production for:
- Integration testing
- Performance testing
- Security testing
- User acceptance testing (UAT)
- Deployment validation

### Setup

**1. Server Provisioning**

```bash
# AWS EC2 (example)
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \
  --instance-type t3.medium \
  --key-name staging-key \
  --security-group-ids sg-staging \
  --subnet-id subnet-staging \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=moai-flow-staging}]'
```

**2. Install System Dependencies**

```bash
# Connect to server
ssh ubuntu@staging.moai-flow.dev

# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install Python 3.13
sudo apt-get install -y python3.13 python3.13-venv python3.13-dev

# Install system dependencies
sudo apt-get install -y \
  git \
  sqlite3 \
  build-essential \
  libssl-dev \
  libffi-dev
```

**3. Deploy Application**

```bash
# Clone repository
git clone https://github.com/superdisco-agents/moai-flow.git
cd moai-flow
git checkout develop  # or specific tag

# Create virtual environment
python3.13 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e .

# Configure environment
cat <<EOF > .env
MOAI_ENV=staging
MOAI_DB_PATH=/var/lib/moai/staging/swarm.db
MOAI_LOG_LEVEL=INFO
MOAI_ENABLE_METRICS=true
MOAI_METRICS_PORT=9090
EOF

# Create data directory
sudo mkdir -p /var/lib/moai/staging
sudo chown ubuntu:ubuntu /var/lib/moai/staging

# Initialize database
python -c "from moai_flow.memory import SwarmDB; SwarmDB()"
```

**4. Configure System Service**

```bash
# Create systemd service
sudo tee /etc/systemd/system/moai-flow-staging.service <<EOF
[Unit]
Description=MoAI-Flow Staging
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/moai-flow
Environment="PATH=/home/ubuntu/moai-flow/.venv/bin"
EnvironmentFile=/home/ubuntu/moai-flow/.env
ExecStart=/home/ubuntu/moai-flow/.venv/bin/python -m moai_flow.server
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl enable moai-flow-staging
sudo systemctl start moai-flow-staging

# Check status
sudo systemctl status moai-flow-staging
```

**5. Configure Reverse Proxy (Nginx)**

```bash
# Install Nginx
sudo apt-get install -y nginx

# Configure Nginx
sudo tee /etc/nginx/sites-available/moai-flow-staging <<EOF
server {
    listen 80;
    server_name staging.moai-flow.dev;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }

    location /metrics {
        proxy_pass http://localhost:9090;
    }
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/moai-flow-staging /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

**6. Configure TLS (Let's Encrypt)**

```bash
# Install Certbot
sudo apt-get install -y certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d staging.moai-flow.dev

# Auto-renewal is configured automatically
```

---

## Production Environment

### Architecture

**Single Server** (Small scale):
- 1 application server
- SQLite database
- Nginx reverse proxy
- Let's Encrypt TLS

**Multi-Server** (Medium scale):
- 2-3 application servers (load balanced)
- PostgreSQL database (optional)
- Redis cache (optional)
- Nginx load balancer
- Monitoring stack (Prometheus, Grafana)

**Container-based** (Large scale):
- Kubernetes cluster
- Horizontal pod autoscaling
- Persistent volumes for database
- Ingress controller
- Service mesh (optional)

### Setup (Single Server)

**1. Server Provisioning**

```bash
# AWS EC2 Production instance
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \
  --instance-type t3.large \
  --key-name production-key \
  --security-group-ids sg-production \
  --subnet-id subnet-production \
  --iam-instance-profile Name=moai-flow-production \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=moai-flow-production}]'
```

**2. Install System Dependencies**

```bash
# Connect to server
ssh ubuntu@moai-flow.dev

# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install Python 3.13
sudo apt-get install -y python3.13 python3.13-venv python3.13-dev

# Install system dependencies
sudo apt-get install -y \
  git \
  sqlite3 \
  build-essential \
  libssl-dev \
  libffi-dev \
  nginx \
  certbot \
  python3-certbot-nginx
```

**3. Deploy Application**

```bash
# Clone repository
git clone https://github.com/superdisco-agents/moai-flow.git
cd moai-flow
git checkout v1.0.0  # Specific production tag

# Create virtual environment
python3.13 -m venv .venv
source .venv/bin/activate

# Install dependencies (production only)
pip install -e .

# Configure environment
cat <<EOF > .env
MOAI_ENV=production
MOAI_DB_PATH=/var/lib/moai/production/swarm.db
MOAI_LOG_LEVEL=WARNING
MOAI_ENABLE_METRICS=true
MOAI_METRICS_PORT=9090
EOF

# Create data directory
sudo mkdir -p /var/lib/moai/production
sudo chown ubuntu:ubuntu /var/lib/moai/production

# Initialize database
python -c "from moai_flow.memory import SwarmDB; SwarmDB()"

# Optimize database
sqlite3 /var/lib/moai/production/swarm.db "PRAGMA journal_mode=WAL;"
sqlite3 /var/lib/moai/production/swarm.db "PRAGMA cache_size=10000;"
```

**4. Configure System Service**

```bash
# Create systemd service
sudo tee /etc/systemd/system/moai-flow.service <<EOF
[Unit]
Description=MoAI-Flow Production
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/moai-flow
Environment="PATH=/home/ubuntu/moai-flow/.venv/bin"
EnvironmentFile=/home/ubuntu/moai-flow/.env
ExecStart=/home/ubuntu/moai-flow/.venv/bin/python -m moai_flow.server
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl enable moai-flow
sudo systemctl start moai-flow

# Check status
sudo systemctl status moai-flow
```

**5. Configure Nginx**

```bash
# Configure Nginx
sudo tee /etc/nginx/sites-available/moai-flow <<EOF
# Rate limiting
limit_req_zone \$binary_remote_addr zone=api:10m rate=10r/s;

server {
    listen 80;
    server_name moai-flow.dev www.moai-flow.dev;

    # Redirect to HTTPS
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name moai-flow.dev www.moai-flow.dev;

    # TLS configuration
    ssl_certificate /etc/letsencrypt/live/moai-flow.dev/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/moai-flow.dev/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;

        # Rate limiting
        limit_req zone=api burst=20 nodelay;
    }

    location /metrics {
        proxy_pass http://localhost:9090;
        allow 10.0.0.0/8;  # Internal network only
        deny all;
    }

    # Health check endpoint
    location /health {
        proxy_pass http://localhost:8000/health;
        access_log off;
    }
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/moai-flow /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

**6. Configure TLS**

```bash
# Obtain certificate
sudo certbot --nginx -d moai-flow.dev -d www.moai-flow.dev

# Test auto-renewal
sudo certbot renew --dry-run
```

**7. Configure Monitoring**

```bash
# Install Prometheus Node Exporter
wget https://github.com/prometheus/node_exporter/releases/download/v1.7.0/node_exporter-1.7.0.linux-amd64.tar.gz
tar xvfz node_exporter-1.7.0.linux-amd64.tar.gz
sudo mv node_exporter-1.7.0.linux-amd64/node_exporter /usr/local/bin/

# Create systemd service for Node Exporter
sudo tee /etc/systemd/system/node_exporter.service <<EOF
[Unit]
Description=Prometheus Node Exporter
After=network.target

[Service]
Type=simple
User=nobody
ExecStart=/usr/local/bin/node_exporter
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Enable and start
sudo systemctl enable node_exporter
sudo systemctl start node_exporter
```

**8. Configure Backups**

```bash
# Create backup script
cat <<'EOF' > /home/ubuntu/backup-moai-flow.sh
#!/bin/bash
BACKUP_DIR="/var/backups/moai-flow"
BACKUP_NAME="swarm-$(date +%Y%m%d-%H%M%S).db"

mkdir -p $BACKUP_DIR
cp /var/lib/moai/production/swarm.db $BACKUP_DIR/$BACKUP_NAME
gzip $BACKUP_DIR/$BACKUP_NAME

# Keep only last 30 days
find $BACKUP_DIR -name "swarm-*.db.gz" -mtime +30 -delete
EOF

chmod +x /home/ubuntu/backup-moai-flow.sh

# Add to crontab (daily at 2 AM)
(crontab -l 2>/dev/null; echo "0 2 * * * /home/ubuntu/backup-moai-flow.sh") | crontab -
```

---

## Environment Variables

### Development

```bash
# .env (development)
MOAI_ENV=development
MOAI_DB_PATH=.moai/memory/swarm.db
MOAI_LOG_LEVEL=DEBUG
MOAI_ENABLE_METRICS=true
MOAI_METRICS_PORT=9090
MOAI_QUERY_TIMEOUT=20
MOAI_BATCH_SIZE=1000
```

### Staging

```bash
# .env (staging)
MOAI_ENV=staging
MOAI_DB_PATH=/var/lib/moai/staging/swarm.db
MOAI_LOG_LEVEL=INFO
MOAI_ENABLE_METRICS=true
MOAI_METRICS_PORT=9090
MOAI_QUERY_TIMEOUT=20
MOAI_BATCH_SIZE=1000
MOAI_MAX_EVENTS=1000000
```

### Production

```bash
# .env (production)
MOAI_ENV=production
MOAI_DB_PATH=/var/lib/moai/production/swarm.db
MOAI_LOG_LEVEL=WARNING
MOAI_ENABLE_METRICS=true
MOAI_METRICS_PORT=9090
MOAI_QUERY_TIMEOUT=20
MOAI_BATCH_SIZE=1000
MOAI_MAX_EVENTS=10000000
MOAI_ENABLE_AUDIT=true
```

---

## Infrastructure Requirements

### Minimum Requirements

| Component | Development | Staging | Production |
|-----------|-------------|---------|------------|
| **CPU** | 1 core | 2 cores | 2 cores |
| **RAM** | 512 MB | 2 GB | 4 GB |
| **Disk** | 1 GB | 10 GB | 50 GB |
| **Python** | 3.11+ | 3.13 | 3.13 |
| **OS** | Any | Ubuntu 22.04+ | Ubuntu 22.04+ |

### Recommended for Production

| Component | Specification |
|-----------|---------------|
| **CPU** | 4 cores |
| **RAM** | 8 GB |
| **Disk** | 100 GB SSD |
| **Python** | 3.13 |
| **OS** | Ubuntu 22.04 LTS |
| **Network** | 100 Mbps |
| **Backups** | Daily automated |

---

**Last Updated**: 2025-11-29
**Version**: 1.0.0
**Owner**: DevOps Team
