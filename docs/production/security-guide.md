# Security Guide

**Comprehensive security best practices for MoAI-Flow production environments**

---

## Table of Contents

- [Security Overview](#security-overview)
- [Application Security](#application-security)
- [Database Security](#database-security)
- [Infrastructure Security](#infrastructure-security)
- [Monitoring & Incident Response](#monitoring--incident-response)
- [Compliance](#compliance)

---

## Security Overview

### Security Principles

1. **Defense in Depth**: Multiple layers of security
2. **Least Privilege**: Minimal permissions required
3. **Zero Trust**: Never trust, always verify
4. **Security by Default**: Secure defaults, opt-out not opt-in
5. **Audit Everything**: Comprehensive logging and monitoring

### Security Checklist

- [ ] Dependencies scanned for vulnerabilities
- [ ] Code scanned for security issues
- [ ] Secrets never committed to version control
- [ ] Database secured with proper permissions
- [ ] Network traffic encrypted (TLS)
- [ ] Authentication and authorization implemented
- [ ] Audit logging enabled
- [ ] Security monitoring configured
- [ ] Incident response plan documented
- [ ] Regular security audits scheduled

---

## Application Security

### Dependency Scanning

**Automated Scanning**:

```bash
# Install security tools
pip install pip-audit bandit safety

# Scan dependencies for known vulnerabilities
pip-audit --strict

# Scan code for security issues
bandit -r moai_flow/ -ll

# Check with Safety (alternative)
safety check
```

**GitHub Actions** (automated):

```yaml
# .github/workflows/security.yml
name: Security Scan

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 0 * * 0'  # Weekly

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.13'

    - name: Install dependencies
      run: |
        pip install -e ".[security]"

    - name: Run pip-audit
      run: pip-audit --strict

    - name: Run bandit
      run: bandit -r moai_flow/ -ll
```

### Secret Management

**Environment Variables**:

```bash
# NEVER commit secrets to version control
echo ".env" >> .gitignore

# Use environment variables for secrets
export DATABASE_PASSWORD=$(vault kv get -field=password secret/moai/db)
export API_KEY=$(vault kv get -field=key secret/moai/api)
```

**Secrets in Docker**:

```yaml
# docker-compose.yml
services:
  moai-flow:
    environment:
      - DATABASE_PASSWORD_FILE=/run/secrets/db_password
    secrets:
      - db_password

secrets:
  db_password:
    external: true
```

**Secrets in Kubernetes**:

```yaml
# Create secret
kubectl create secret generic moai-secrets \
  --from-literal=database-password=secret123

# Use in deployment
apiVersion: apps/v1
kind: Deployment
spec:
  template:
    spec:
      containers:
      - name: moai-flow
        env:
        - name: DATABASE_PASSWORD
          valueFrom:
            secretKeyRef:
              name: moai-secrets
              key: database-password
```

### Input Validation

**Always validate input**:

```python
from pydantic import BaseModel, Field, validator
from typing import Optional

class AgentConfig(BaseModel):
    """Validated agent configuration"""

    agent_id: str = Field(..., min_length=1, max_length=100)
    agent_type: str = Field(..., regex=r'^[a-z-]+$')
    priority: int = Field(5, ge=1, le=10)
    metadata: Optional[dict] = Field(default_factory=dict)

    @validator('metadata')
    def validate_metadata(cls, v):
        # Limit metadata size to prevent DoS
        if len(str(v)) > 10000:
            raise ValueError("Metadata too large")
        return v

# Usage
try:
    config = AgentConfig(
        agent_id="backend-001",
        agent_type="expert-backend",
        priority=5
    )
except ValidationError as e:
    logger.error(f"Invalid input: {e}")
```

### SQL Injection Prevention

**Always use parameterized queries**:

```python
# Good: Parameterized query (safe)
cursor.execute(
    "SELECT * FROM agent_events WHERE agent_id = ?",
    (agent_id,)
)

# Bad: String concatenation (vulnerable)
cursor.execute(
    f"SELECT * FROM agent_events WHERE agent_id = '{agent_id}'"
)
```

### XSS Prevention

**Escape output**:

```python
import html

# Escape HTML special characters
safe_output = html.escape(user_input)

# Or use templating engine that auto-escapes
from jinja2 import Template, escape
template = Template("Hello {{ name }}", autoescape=True)
```

---

## Database Security

### File Permissions

```bash
# Set restrictive file permissions
chmod 600 .moai/memory/swarm.db
chmod 700 .moai/memory/

# Verify permissions
ls -la .moai/memory/
```

### Encryption at Rest

**SQLite Encryption** (using SQLCipher):

```python
from sqlcipher3 import dbapi2 as sqlite3

# Connect with encryption
conn = sqlite3.connect('.moai/memory/swarm.db')
conn.execute("PRAGMA key = 'your-encryption-key'")
```

### Backup Security

```bash
# Encrypt backups
tar czf - .moai/memory/swarm.db | \
  gpg --symmetric --cipher-algo AES256 \
  > swarm-backup-$(date +%Y%m%d).tar.gz.gpg

# Decrypt backup
gpg --decrypt swarm-backup-20251129.tar.gz.gpg | \
  tar xzf -
```

### Database Auditing

```python
import logging

class AuditLogger:
    """Database audit logger"""

    def __init__(self):
        self.logger = logging.getLogger("moai_flow.audit")

    def log_query(self, query: str, params: tuple, user: str):
        """Log database query for audit"""
        self.logger.info(
            "Database query",
            extra={
                "query": query,
                "params": params,
                "user": user,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

# Usage
audit = AuditLogger()
audit.log_query(
    "INSERT INTO agent_events VALUES (?, ?, ?)",
    ("event-001", "spawn", "backend-001"),
    "admin"
)
```

---

## Infrastructure Security

### Network Security

**Firewall Configuration** (UFW):

```bash
# Default deny
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow SSH (restrict to specific IP if possible)
sudo ufw allow from 203.0.113.0/24 to any port 22

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Allow metrics (internal only)
sudo ufw allow from 10.0.0.0/8 to any port 9090

# Enable firewall
sudo ufw enable
sudo ufw status
```

**Security Groups** (AWS):

```bash
# Create security group
aws ec2 create-security-group \
  --group-name moai-flow-sg \
  --description "MoAI-Flow security group"

# Allow HTTPS only
aws ec2 authorize-security-group-ingress \
  --group-id sg-xxx \
  --protocol tcp \
  --port 443 \
  --cidr 0.0.0.0/0

# Allow SSH from specific IP
aws ec2 authorize-security-group-ingress \
  --group-id sg-xxx \
  --protocol tcp \
  --port 22 \
  --cidr 203.0.113.0/32
```

### TLS/SSL Configuration

**Nginx TLS Best Practices**:

```nginx
server {
    listen 443 ssl http2;
    server_name moai-flow.dev;

    # TLS certificates
    ssl_certificate /etc/letsencrypt/live/moai-flow.dev/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/moai-flow.dev/privkey.pem;

    # TLS protocols (disable old versions)
    ssl_protocols TLSv1.2 TLSv1.3;

    # Strong ciphers
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384';
    ssl_prefer_server_ciphers on;

    # HSTS (force HTTPS)
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # Content Security Policy
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'" always;
}
```

### Rate Limiting

**Nginx Rate Limiting**:

```nginx
# Define rate limit zone
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;

server {
    location /api/ {
        # Apply rate limit
        limit_req zone=api burst=20 nodelay;

        # Return 429 on rate limit
        limit_req_status 429;

        proxy_pass http://localhost:8000;
    }
}
```

**Application-Level Rate Limiting**:

```python
from functools import wraps
from flask import request, abort
import time

# Simple in-memory rate limiter
rate_limits = {}

def rate_limit(max_requests=10, window=60):
    """Rate limit decorator"""

    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            ip = request.remote_addr
            now = time.time()

            # Initialize or clean old entries
            if ip not in rate_limits:
                rate_limits[ip] = []

            rate_limits[ip] = [
                req_time for req_time in rate_limits[ip]
                if req_time > now - window
            ]

            # Check limit
            if len(rate_limits[ip]) >= max_requests:
                abort(429, "Rate limit exceeded")

            # Add request
            rate_limits[ip].append(now)

            return f(*args, **kwargs)

        return wrapper
    return decorator

# Usage
@app.route('/api/agents')
@rate_limit(max_requests=100, window=60)
def list_agents():
    return {"agents": [...]}
```

---

## Monitoring & Incident Response

### Security Monitoring

**Security Event Logging**:

```python
import logging

security_logger = logging.getLogger("security")

# Log security events
def log_security_event(event_type: str, details: dict):
    """Log security-relevant event"""
    security_logger.warning(
        f"Security event: {event_type}",
        extra={
            "event_type": event_type,
            "details": details,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

# Examples
log_security_event("failed_auth", {
    "user": "admin",
    "ip": "203.0.113.1",
    "attempts": 5
})

log_security_event("suspicious_query", {
    "query": "SELECT * FROM users WHERE ...",
    "user": "anonymous"
})
```

**Failed Login Monitoring**:

```python
from collections import defaultdict
from datetime import datetime, timedelta

failed_logins = defaultdict(list)

def track_failed_login(user: str, ip: str):
    """Track failed login attempts"""
    now = datetime.utcnow()

    # Clean old attempts
    failed_logins[user] = [
        attempt for attempt in failed_logins[user]
        if attempt > now - timedelta(minutes=10)
    ]

    # Add new attempt
    failed_logins[user].append(now)

    # Alert if too many attempts
    if len(failed_logins[user]) >= 5:
        log_security_event("brute_force_attempt", {
            "user": user,
            "ip": ip,
            "attempts": len(failed_logins[user])
        })

        # Lock account or block IP
        block_ip(ip)
```

### Incident Response Plan

**1. Detection**:
- Automated alerts (Alertmanager)
- Security monitoring (SIEM)
- User reports

**2. Assessment**:
- Determine severity (Critical, High, Medium, Low)
- Identify affected systems
- Estimate impact

**3. Containment**:
```bash
# Block malicious IP
sudo ufw deny from 203.0.113.1

# Revoke access token
python -m moai_flow.admin revoke-token <token-id>

# Isolate affected service
kubectl scale deployment moai-flow --replicas=0
```

**4. Eradication**:
- Remove malware/backdoors
- Patch vulnerabilities
- Update credentials

**5. Recovery**:
```bash
# Restore from backup
./restore-backup.sh 2025-11-29-02-00

# Verify integrity
./verify-integrity.sh

# Gradually restore service
kubectl scale deployment moai-flow --replicas=1
# Monitor for 30 minutes
kubectl scale deployment moai-flow --replicas=3
```

**6. Post-Incident**:
- Root cause analysis
- Update security controls
- Document lessons learned

---

## Compliance

### GDPR Compliance

**Data Protection**:

```python
class DataProtection:
    """GDPR-compliant data protection"""

    def anonymize_data(self, data: dict) -> dict:
        """Anonymize personal data"""
        # Remove or hash PII
        anonymized = data.copy()
        if "email" in anonymized:
            anonymized["email"] = self.hash_email(data["email"])
        if "ip_address" in anonymized:
            anonymized["ip_address"] = self.anonymize_ip(data["ip_address"])
        return anonymized

    def delete_user_data(self, user_id: str):
        """Right to erasure (GDPR Article 17)"""
        db = SwarmDB()
        # Delete all user data
        db.execute(
            "DELETE FROM agent_events WHERE user_id = ?",
            (user_id,)
        )
        db.execute(
            "DELETE FROM session_memory WHERE user_id = ?",
            (user_id,)
        )

    def export_user_data(self, user_id: str) -> dict:
        """Right to data portability (GDPR Article 20)"""
        db = SwarmDB()
        # Export all user data
        events = db.execute(
            "SELECT * FROM agent_events WHERE user_id = ?",
            (user_id,)
        ).fetchall()

        return {
            "user_id": user_id,
            "events": [dict(event) for event in events],
            "exported_at": datetime.utcnow().isoformat()
        }
```

### Audit Logging

**Comprehensive Audit Trail**:

```python
class AuditTrail:
    """Audit trail for compliance"""

    def log_action(
        self,
        action: str,
        user: str,
        resource: str,
        details: dict
    ):
        """Log action for audit"""
        self.logger.info(
            f"Audit: {action}",
            extra={
                "action": action,
                "user": user,
                "resource": resource,
                "details": details,
                "timestamp": datetime.utcnow().isoformat(),
                "ip_address": request.remote_addr
            }
        )

# Usage
audit = AuditTrail()

# Log data access
audit.log_action(
    action="data_access",
    user="admin",
    resource="agent_events",
    details={"query": "SELECT * FROM agent_events LIMIT 10"}
)

# Log data modification
audit.log_action(
    action="data_modification",
    user="admin",
    resource="agent_events",
    details={"event_id": "evt-001", "operation": "delete"}
)
```

### Data Retention

**Automated Data Retention**:

```python
class DataRetentionPolicy:
    """Enforce data retention policies"""

    def __init__(self):
        self.retention_days = {
            "agent_events": 90,  # 90 days
            "session_memory": 30,  # 30 days
            "audit_logs": 365  # 1 year
        }

    def apply_retention(self):
        """Apply retention policies"""
        db = SwarmDB()
        for table, days in self.retention_days.items():
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            db.execute(
                f"DELETE FROM {table} WHERE created_at < ?",
                (cutoff_date.isoformat(),)
            )
            logger.info(f"Applied {days}-day retention to {table}")

# Schedule retention policy
# Run daily via cron: 0 2 * * *
retention = DataRetentionPolicy()
retention.apply_retention()
```

---

## Security Checklist

### Pre-Deployment Security Audit

- [ ] **Dependencies**
  - [ ] No known vulnerabilities (pip-audit)
  - [ ] All dependencies up to date
  - [ ] Minimal dependencies (reduce attack surface)

- [ ] **Code Security**
  - [ ] No security issues (bandit)
  - [ ] Input validation implemented
  - [ ] Output escaping implemented
  - [ ] SQL injection prevention

- [ ] **Secrets Management**
  - [ ] No secrets in code
  - [ ] No secrets in version control
  - [ ] Environment variables secured
  - [ ] Secret rotation implemented

- [ ] **Database Security**
  - [ ] File permissions restricted (600)
  - [ ] Encryption at rest (optional)
  - [ ] Backup encryption enabled
  - [ ] Audit logging enabled

- [ ] **Network Security**
  - [ ] Firewall configured
  - [ ] TLS/SSL enabled
  - [ ] Security headers set
  - [ ] Rate limiting enabled

- [ ] **Monitoring**
  - [ ] Security event logging
  - [ ] Failed login tracking
  - [ ] Intrusion detection configured
  - [ ] Incident response plan documented

- [ ] **Compliance**
  - [ ] Data protection measures
  - [ ] Audit trail complete
  - [ ] Data retention policy enforced
  - [ ] Privacy policy published

---

**Last Updated**: 2025-11-29
**Version**: 1.0.0
**Owner**: Security Team
