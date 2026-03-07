# Production Dockerfile for ScraperFC API
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Copy requirements
COPY pyproject.toml ./

# Install Python dependencies
RUN pip install --upgrade pip setuptools wheel && \
    pip install -e . && \
    pip install fastapi uvicorn[standard] sqlalchemy psycopg2-binary \
    pydantic-settings apscheduler httpx python-multipart

# Copy application code
COPY src/ ./src/
COPY app/ ./app/

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    rm -rf /usr/local/lib/python3.11/site-packages/botasaurus_requests/bin/temp && \
    chown -R appuser:appuser /app /usr/local/lib/python3.11/site-packages/botasaurus_requests
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

# Start application
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
