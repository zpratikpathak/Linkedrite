#!/bin/bash
# Verify LinkedRite deployment status

echo "🔍 LinkedRite Deployment Verification"
echo "===================================="

cd ~/linkedrite 2>/dev/null || cd /root/linkedrite 2>/dev/null || { echo "Error: LinkedRite directory not found"; exit 1; }

# Check Docker containers
echo ""
echo "1️⃣ Checking Docker containers..."
if command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
else
    COMPOSE_CMD="docker compose"
fi

if [ -f docker-compose.prod.yml ]; then
    COMPOSE_FILE="docker-compose.prod.yml"
else
    COMPOSE_FILE="docker-compose.yml"
fi

$COMPOSE_CMD -f $COMPOSE_FILE ps

# Check web container specifically
echo ""
echo "2️⃣ Checking web container health..."
WEB_STATUS=$($COMPOSE_CMD -f $COMPOSE_FILE ps web 2>/dev/null | grep -E "Up|running" || echo "Not running")
echo "Web container: $WEB_STATUS"

# Check if Gunicorn is running inside container
echo ""
echo "3️⃣ Checking Gunicorn process..."
$COMPOSE_CMD -f $COMPOSE_FILE exec -T web ps aux | grep gunicorn | grep -v grep || echo "Gunicorn not found"

# Test HTTP response
echo ""
echo "4️⃣ Testing HTTP response..."
for port in 8000 8001 80; do
    echo -n "Port $port: "
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -m 5 http://localhost:$port 2>/dev/null || echo "timeout")
    if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "302" ] || [ "$HTTP_CODE" = "301" ]; then
        echo "✅ Responding (HTTP $HTTP_CODE)"
        WORKING_PORT=$port
        break
    else
        echo "❌ Not responding ($HTTP_CODE)"
    fi
done

# Check recent logs
echo ""
echo "5️⃣ Recent application logs..."
$COMPOSE_CMD -f $COMPOSE_FILE logs --tail=10 web 2>/dev/null | grep -E "(Starting|Listening|worker|GET|POST)" || echo "No recent activity"

# Database connectivity
echo ""
echo "6️⃣ Database status..."
$COMPOSE_CMD -f $COMPOSE_FILE exec -T web python -c "
from django.db import connection
try:
    with connection.cursor() as cursor:
        cursor.execute('SELECT COUNT(*) FROM django_migrations')
        count = cursor.fetchone()[0]
        print(f'✅ Database connected: {count} migrations applied')
except Exception as e:
    print(f'❌ Database error: {e}')
" 2>/dev/null || echo "Could not check database"

# Admin account
echo ""
echo "7️⃣ Admin account..."
$COMPOSE_CMD -f $COMPOSE_FILE exec -T web python -c "
from accounts.models import CustomUser
try:
    admin = CustomUser.objects.filter(is_superuser=True).first()
    if admin:
        print(f'✅ Admin exists: {admin.email}')
    else:
        print('❌ No admin account found')
except Exception as e:
    print(f'Error: {e}')
" 2>/dev/null || echo "Could not check admin"

# Summary
echo ""
echo "📊 SUMMARY"
echo "=========="
if [ -n "$WORKING_PORT" ]; then
    echo "✅ LinkedRite is RUNNING on port $WORKING_PORT"
    echo ""
    echo "🌐 Access your application at:"
    echo "   Local: http://localhost:$WORKING_PORT"
    echo "   External: http://$(hostname -I | awk '{print $1}'):$WORKING_PORT"
    echo ""
    echo "👨‍💼 Admin panel: http://$(hostname -I | awk '{print $1}'):$WORKING_PORT/admin/"
else
    echo "❌ LinkedRite is NOT ACCESSIBLE via HTTP"
    echo ""
    echo "🔧 Troubleshooting steps:"
    echo "1. Check container logs: $COMPOSE_CMD -f $COMPOSE_FILE logs web"
    echo "2. Restart containers: $COMPOSE_CMD -f $COMPOSE_FILE restart"
    echo "3. Check firewall: sudo ufw allow 8000"
fi

echo ""
echo "📝 For more details, check the logs:"
echo "   $COMPOSE_CMD -f $COMPOSE_FILE logs -f web"
