# Immediate Fix for Database Loop Issue

## Quick Fix (Run on Server)

SSH into your server and run these commands:

```bash
cd ~/linkedrite

# Option 1: Override the entrypoint (fastest fix)
docker-compose -f docker-compose.prod.yml exec -d web gunicorn Linkedrite.wsgi:application --bind 0.0.0.0:8000 --workers 3 --access-logfile - --error-logfile -

# Check if it's running
sleep 5
curl -I http://localhost:8000
```

## Alternative Fix: Create Override

```bash
cd ~/linkedrite

# Create override entrypoint
cat > entrypoint-override.sh << 'EOF'
#!/bin/sh
echo "Starting Gunicorn directly..."
exec gunicorn Linkedrite.wsgi:application --bind 0.0.0.0:8000 --workers 3 --access-logfile - --error-logfile -
EOF

# Copy to container and use it
docker cp entrypoint-override.sh linkedrite_web_1:/app/entrypoint-override.sh
docker-compose -f docker-compose.prod.yml exec web chmod +x /app/entrypoint-override.sh

# Update docker-compose to use override
cat > docker-compose.override.yml << 'EOF'
services:
  web:
    entrypoint: ["/app/entrypoint-override.sh"]
EOF

# Restart
docker-compose -f docker-compose.prod.yml restart web

# Check logs
docker-compose -f docker-compose.prod.yml logs --tail=20 web
```

## Root Cause

The container's entrypoint script is stuck in a database connection check loop. The database is actually running fine (migrations succeeded), but the repeated database check is failing.

## Permanent Solution

The next deployment will include a fixed entrypoint script that:
1. Only runs initialization once
2. Has timeout limits on database checks
3. Continues even if secondary checks fail

## Verify It's Working

```bash
# Check if responding
curl -I http://localhost:8000

# Check container status
docker-compose -f docker-compose.prod.yml ps

# View application logs (not the startup logs)
docker-compose -f docker-compose.prod.yml exec web tail -f /var/log/gunicorn/access.log
```

The application should now be accessible at http://your-server:8000!
