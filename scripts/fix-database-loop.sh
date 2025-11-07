#!/bin/bash
# Fix for database connection loop issue

echo "🔧 Fixing LinkedRite Database Connection Issue"
echo "============================================"

cd ~/linkedrite

# Option 1: Quick fix - Remove the initialization flag and restart
echo "Option 1: Reset initialization flag"
read -p "Do you want to reset the container initialization? (y/N) " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Removing initialization flag from web container..."
    docker-compose -f docker-compose.prod.yml exec web rm -f /app/.initialized || true
    
    echo "Restarting web container..."
    docker-compose -f docker-compose.prod.yml restart web
    
    echo "Waiting for initialization..."
    sleep 20
    
    echo "Checking status..."
    docker-compose -f docker-compose.prod.yml ps
    docker-compose -f docker-compose.prod.yml logs --tail=30 web
fi

# Option 2: Complete rebuild
echo ""
echo "Option 2: Complete rebuild with new entrypoint"
read -p "Do you want to rebuild with the fixed entrypoint? (y/N) " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Create the new entrypoint script
    cat > docker-entrypoint.sh << 'EOF'
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
EOF

    # Copy the new entrypoint to the container
    echo "Copying new entrypoint to container..."
    docker cp docker-entrypoint.sh linkedrite_web_1:/app/entrypoint.sh
    docker-compose -f docker-compose.prod.yml exec web chmod +x /app/entrypoint.sh
    
    # Restart the container
    echo "Restarting web container with new entrypoint..."
    docker-compose -f docker-compose.prod.yml restart web
    
    echo "Waiting for restart..."
    sleep 20
    
    echo "Checking status..."
    docker-compose -f docker-compose.prod.yml ps
fi

# Final check
echo ""
echo "Testing application..."
if curl -f -s -o /dev/null http://localhost:8000; then
    echo "✅ Application is responding on port 8000!"
else
    echo "❌ Application is not responding. Showing recent logs:"
    docker-compose -f docker-compose.prod.yml logs --tail=50 web
fi

echo ""
echo "Current container status:"
docker-compose -f docker-compose.prod.yml ps
