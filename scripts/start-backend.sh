#!/bin/bash
# Inicia los servicios de backend (Redis + Postgres + FastAPI + Celery Worker)

set -e

echo "=== Iniciando Redis + PostgreSQL ==="
docker compose up -d redis postgres

echo "=== Esperando servicios ==="
sleep 2

echo "=== Iniciando Celery Worker ==="
cd "$(dirname "$0")/../backend"
celery -A app.tasks.worker worker --loglevel=info --concurrency=1 &

echo "=== Iniciando FastAPI ==="
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
