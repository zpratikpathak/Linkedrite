#!/bin/sh
set -e

# Function to check if database is ready
check_database() {
    if [ -n "$DATABASE_URL" ] || [ "$DB_ENGINE" != "django.db.backends.sqlite3" ]; then
        echo "Checking database connection..."
        python -c "
import os
import sys
import time
import django
from django.db import connection
from django.core.exceptions import ImproperlyConfigured

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Linkedrite.settings')

try:
    django.setup()
    with connection.cursor() as cursor:
        cursor.execute('SELECT 1')
    print('Database is ready!')
    sys.exit(0)
except Exception as e:
    print(f'Database not ready: {e}')
    sys.exit(1)
"
        return $?
    else
        echo "Using SQLite, skipping database check"
        return 0
    fi
}

# Only run setup tasks if this is the first run
INIT_FLAG="/app/.initialized"

if [ ! -f "$INIT_FLAG" ]; then
    echo "First run detected, running initialization..."
    
    # Wait for database
    if [ -n "$DATABASE_URL" ] || [ "$DB_ENGINE" != "django.db.backends.sqlite3" ]; then
        echo "Waiting for database to be ready..."
        MAX_RETRIES=30
        RETRY_COUNT=0
        
        while ! check_database; do
            RETRY_COUNT=$((RETRY_COUNT + 1))
            if [ $RETRY_COUNT -gt $MAX_RETRIES ]; then
                echo "ERROR: Database not available after $MAX_RETRIES attempts"
                exit 1
            fi
            echo "Database is unavailable - sleeping (attempt $RETRY_COUNT/$MAX_RETRIES)"
            sleep 2
        done
    fi
    
    # Run migrations
    echo "Running migrations..."
    python manage.py migrate --noinput
    
    # Create default admin if configured
    if [ -n "$ADMIN_EMAIL" ] && [ -n "$ADMIN_PASSWORD" ]; then
        echo "Creating/updating default admin..."
        python manage.py create_default_admin || true
    fi
    
    # Collect static files
    echo "Collecting static files..."
    python manage.py collectstatic --noinput
    
    # Mark as initialized
    touch "$INIT_FLAG"
    echo "Initialization complete!"
else
    echo "Container already initialized, checking database connection..."
    
    # Quick database check with timeout
    if [ -n "$DATABASE_URL" ] || [ "$DB_ENGINE" != "django.db.backends.sqlite3" ]; then
        MAX_RETRIES=5
        RETRY_COUNT=0
        
        while ! check_database; do
            RETRY_COUNT=$((RETRY_COUNT + 1))
            if [ $RETRY_COUNT -gt $MAX_RETRIES ]; then
                echo "WARNING: Database check failed, but continuing anyway..."
                break
            fi
            echo "Waiting for database (attempt $RETRY_COUNT/$MAX_RETRIES)..."
            sleep 1
        done
    fi
fi

# Start the application
echo "Starting Gunicorn..."
exec gunicorn Linkedrite.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers ${GUNICORN_WORKERS:-3} \
    --timeout ${GUNICORN_TIMEOUT:-120} \
    --access-logfile - \
    --error-logfile - \
    --log-level ${LOG_LEVEL:-info}
