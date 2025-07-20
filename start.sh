#!/bin/bash

set -e  # Exit on any error

echo "=== FelchatV2 Startup ==="
echo "Current directory: $(pwd)"
echo "Files in current directory:"
ls -la
echo "Environment variables:"
echo "DATABASE_URL: ${DATABASE_URL:+SET}"
echo "DATABASE_URL value: ${DATABASE_URL}"
echo "REDIS_URL: ${REDIS_URL:+SET}"
echo "PORT: ${PORT:-8000}"
echo "ENV: ${ENV:-prod}"

echo "Waiting for database to be ready..."
sleep 10

echo "Running database migrations..."
echo "Alembic version: $(alembic --version)"
echo "Current alembic revision: $(alembic current 2>/dev/null || echo 'No current revision')"
alembic upgrade head
echo "Migrations completed successfully!"

echo "Starting application..."
exec uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8000} 