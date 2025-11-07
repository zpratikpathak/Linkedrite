# Quick Fix for Current Deployment Issue

## Immediate Fix (Run on your server)

SSH into your server and run these commands:

```bash
cd ~/linkedrite

# Option 1: Quick fix (install packages in running container)
docker exec linkedrite_web_1 pip install dj-database-url psycopg2-binary redis django-redis asgiref
docker-compose -f docker-compose.prod.yml restart web

# OR Option 2: Force rebuild (more reliable)
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml build --no-cache web
docker-compose -f docker-compose.prod.yml up -d

# Wait a moment, then run migrations
sleep 10
docker-compose -f docker-compose.prod.yml exec -T web python manage.py migrate --noinput
docker-compose -f docker-compose.prod.yml exec -T web python manage.py create_default_admin
docker-compose -f docker-compose.prod.yml exec -T web python manage.py collectstatic --noinput

# Check status
docker-compose -f docker-compose.prod.yml ps
```

## What Happened?

The `dj-database-url` package was missing from requirements.txt when the Docker image was built. This has now been fixed in the code, but your server has the old image.

## Permanent Fix

The next deployment from GitHub Actions will include all the required packages. The requirements.txt has been updated with:
- dj-database-url
- psycopg2-binary  
- redis
- django-redis
- asgiref

## Verify It's Working

```bash
# Test the application
curl -I http://localhost:8000

# Check logs
docker-compose -f docker-compose.prod.yml logs --tail=50 web
```

The application should now be running correctly on port 8000!
