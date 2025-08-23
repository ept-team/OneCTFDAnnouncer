FROM python:3.13-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DB_PATH=/app/data/state.db

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker layer caching
COPY pyproject.toml requirements.txt ./

# Install Python dependencies
RUN pip install uv && uv pip install --system .

# Copy application code
COPY . .

# Create data directory and non-root user for security
RUN mkdir -p /app/data && \
    useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import onectfdannouncer; print('OK')" || exit 1

CMD ["python", "-m", "onectfdannouncer.bot"]
