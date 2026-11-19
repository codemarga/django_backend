#!/bin/sh
set -e

echo "==> Running database migrations..."
python manage.py migrate --noinput

echo "==> Collecting static files..."
python manage.py collectstatic --noinput

if [ "$SEED_DATABASE" = "true" ]; then
    echo "==> Seeding initial problem set..."
    python scripts/populate_all_problems.py || echo "Seed script completed or skipped."
fi

echo "==> Starting Gunicorn server on 0.0.0.0:8000..."
exec gunicorn codeMarga.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers ${GUNICORN_WORKERS:-3} \
    --timeout ${GUNICORN_TIMEOUT:-120} \
    --access-logfile - \
    --error-logfile -
