#!/bin/bash

echo "=== FelchatV2 Startup ==="
echo "Environment variables:"
echo "DATABASE_URL: ${DATABASE_URL:+SET}"
echo "REDIS_URL: ${REDIS_URL:+SET}"
echo "PORT: ${PORT:-8000}"
echo "ENV: ${ENV:-prod}"

echo "Starting application..."
exec uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8000} 