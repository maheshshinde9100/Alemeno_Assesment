#!/bin/bash
# Worker startup configuration

echo "Starting Celery worker..."
celery -A app.core.celery_app worker --loglevel=info
