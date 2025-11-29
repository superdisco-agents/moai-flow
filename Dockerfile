# Multi-stage Dockerfile for MoAI-Flow
# Production-ready with security best practices

# Build stage
FROM python:3.13-slim AS builder

# Build arguments
ARG PYTHON_VERSION=3.13
ARG VERSION=latest

# Set working directory
WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy only dependency files first (for better caching)
COPY pyproject.toml README.md ./
COPY src/ ./src/

# Install dependencies to user site
RUN pip install --user --no-cache-dir --upgrade pip && \
    pip install --user --no-cache-dir -e .

# Runtime stage
FROM python:3.13-slim

# Metadata
LABEL maintainer="MoAI Team <support@moduai.kr>" \
      description="MoAI-Flow - Native Multi-Agent Swarm Coordination" \
      version="${VERSION}"

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    MOAI_ENV=production \
    MOAI_DB_PATH=/app/.moai/memory/swarm.db \
    MOAI_LOG_LEVEL=INFO

# Set working directory
WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY src/ ./src/
COPY pyproject.toml README.md ./

# Create non-root user
RUN groupadd -r moai && useradd -r -g moai moai && \
    mkdir -p /app/.moai/memory /app/.moai/logs && \
    chown -R moai:moai /app

# Make Python packages available
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONPATH=/app/src:$PYTHONPATH

# Switch to non-root user
USER moai

# Initialize database
RUN python -c "from moai_flow.memory import SwarmDB; SwarmDB()" || true

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD python -c "from moai_flow.memory import SwarmDB; SwarmDB().get_database_size()" || exit 1

# Expose port (if running server)
EXPOSE 8000

# Default command (can be overridden)
CMD ["python", "-m", "moai_flow"]
