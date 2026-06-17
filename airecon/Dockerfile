# =============================================================================
# AIRecon Dockerfile
# Production-grade image for the AIRecon autonomous cybersecurity agent.
# Based on Python 3.11 slim, includes all Python dependencies and the
# application code. The container orchestrates Kali sandbox containers via
# the Docker socket (must be mounted at runtime) and connects to a local
# Ollama instance (host network or referenced by hostname).
# =============================================================================

FROM python:3.11-slim AS base

LABEL maintainer="AIRecon Team <airecon@example.com>" \
      description="AIRecon - Autonomous Cybersecurity Reconnaissance Agent" \
      version="1.0.0" \
      org.opencontainers.image.source="https://github.com/pikpikcu/airecon"

# =============================================================================
# Build-time dependencies
# =============================================================================
RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
        curl \
        gcc \
        python3-dev \
        libffi-dev \
        libssl-dev \
    ; \
    rm -rf /var/lib/apt/lists/*

# =============================================================================
# Create non‑root user and group
# =============================================================================
RUN addgroup --system --gid 1001 airecon \
    && adduser --system --uid 1001 --ingroup airecon --home /app airecon

# =============================================================================
# Install Python dependencies
# =============================================================================
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r /tmp/requirements.txt \
    && rm -f /tmp/requirements.txt

# =============================================================================
# Set up application directory
# =============================================================================
WORKDIR /app

# Copy the entire AIRecon source code
COPY --chown=airecon:airecon . /app

# Grant execute permissions on main entry point (if any)
RUN chmod +x /app/airecon/main.py 2>/dev/null || true

# =============================================================================
# Runtime configuration
# =============================================================================
USER airecon

# Default port – no exposed ports because the UI is a TUI and networking
# is outbound only (Ollama, Docker socket).
# EXPOSE is omitted intentionally.

# Health check (optional) – verifies that the process is alive
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import sys, docker, requests; sys.exit(0)" || exit 1

# =============================================================================
# Entry point
# =============================================================================
# Adjust the CMD below to match the actual main script of AIRecon.
# If the application uses a different entry script, change accordingly.
ENTRYPOINT ["python"]
CMD ["/app/airecon/main.py"]