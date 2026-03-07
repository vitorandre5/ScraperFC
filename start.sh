#!/bin/bash
# Startup script for production deployment

set -e

echo "Starting ScraperFC API..."

# Wait for database to be ready
echo "Waiting for database connection..."
python -c "
import time
import sys
from app.core.database import check_db_connection

max_retries = 30
retry_count = 0

while retry_count < max_retries:
    if check_db_connection():
        print('Database connection successful')
        sys.exit(0)
    retry_count += 1
    print(f'Waiting for database... ({retry_count}/{max_retries})')
    time.sleep(2)

print('Failed to connect to database')
sys.exit(1)
"

# Run database migrations if alembic is configured
if [ -f "alembic.ini" ]; then
    echo "Running database migrations..."
    alembic upgrade head || echo "Warning: Migration failed or not configured"
fi

# Start the application
echo "Starting application..."
exec python -m uvicorn app.main:app \
    --host 0.0.0.0 \
    --port ${PORT:-8000} \
    --workers ${WORKERS:-1} \
    --log-level ${LOG_LEVEL:-info}
