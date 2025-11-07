# LinkedRite Deployment Guide

## Quick Start

### Prerequisites
- Ubuntu/Debian server with Docker installed
- Port 8000 available for the application
- GitHub repository secrets configured
- Domain pointed to server IP (optional)

### Automated Deployment via GitHub Actions

1. **Push to master branch**:
   ```bash
   git add .
   git commit -m "Deploy LinkedRite"
   git push origin master
   ```

2. **Monitor deployment**:
   - Go to GitHub repository → Actions tab
   - Watch the deployment progress in real-time
   - Check for any errors in the logs

3. **Verify deployment**:
   ```bash
   # On your server
   curl http://localhost:8000
   # Should return HTML or redirect
   ```

## Manual Deployment

### Option 1: Using Docker Compose (Recommended)

```bash
# Clone repository
git clone https://github.com/yourusername/linkedrite.git
cd linkedrite

# Create .env file
cp .env.example .env
# Edit .env with your configuration

# Build and run
docker-compose up -d

# Check status
docker-compose ps
docker-compose logs -f
```

### Option 2: Single Container

```bash
# Build image
docker build -t linkedrite:latest .

# Run container
docker run -d \
  --name linkedrite \
  -p 8000:8000 \
  --env-file .env \
  --restart always \
  linkedrite:latest
```

## Common Issues and Solutions

### 1. Port 8000 Already in Use

**Error**: `Bind for 0.0.0.0:8000 failed: port is already allocated`

**Solution**:
```bash
# Option 1: Use the fix script
wget https://raw.githubusercontent.com/yourusername/linkedrite/master/scripts/fix-port-8000.sh
chmod +x fix-port-8000.sh
./fix-port-8000.sh

# Option 2: Manual fix
# Find what's using port 8000
sudo lsof -i:8000
sudo netstat -tulpn | grep :8000

# Kill the process (replace PID with actual process ID)
sudo kill -9 PID

# Stop Docker containers using port 8000
docker ps --filter "publish=8000" --format "table {{.ID}}\t{{.Names}}"
docker stop CONTAINER_ID
```

### 2. Database Connection Failed

**Error**: `could not connect to server: Connection refused`

**Solution**:
```bash
# Check if database container is running
docker-compose ps db
docker-compose logs db

# Restart database
docker-compose restart db

# Wait for database to be ready
docker-compose exec db pg_isready
```

### 3. Static Files Not Loading

**Error**: 404 errors for CSS/JS files

**Solution**:
```bash
# Collect static files manually
docker-compose exec web python manage.py collectstatic --noinput

# Check static files volume
docker volume ls | grep static
docker volume inspect linkedrite_static_volume
```

### 4. Admin Login Not Working

**Error**: Invalid credentials for admin

**Solution**:
```bash
# Recreate admin account
docker-compose exec web python manage.py create_default_admin

# Or create new superuser
docker-compose exec web python manage.py createsuperuser
```

### 5. ModuleNotFoundError: No module named 'dj_database_url'

**Error**: Missing Python dependencies in container

**Solution**:
```bash
# Option 1: Quick fix (temporary)
docker exec linkedrite_web_1 pip install dj-database-url psycopg2-binary redis django-redis asgiref
docker-compose restart web

# Option 2: Run fix script
chmod +x scripts/fix-missing-dependencies.sh
./scripts/fix-missing-dependencies.sh

# Option 3: Rebuild image (permanent fix)
docker-compose build --no-cache web
docker-compose up -d
```

## Server Maintenance

### Viewing Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f web
docker-compose logs -f db
docker-compose logs -f redis

# Last 100 lines
docker-compose logs --tail=100 web
```

### Restarting Services
```bash
# Restart all services
docker-compose restart

# Restart specific service
docker-compose restart web

# Stop and start
docker-compose down
docker-compose up -d
```

### Backup Database
```bash
# Backup PostgreSQL
docker-compose exec db pg_dump -U linkedrite linkedrite > backup_$(date +%Y%m%d_%H%M%S).sql

# Backup with compression
docker-compose exec db pg_dump -U linkedrite linkedrite | gzip > backup_$(date +%Y%m%d_%H%M%S).sql.gz
```

### Update Application
```bash
# Pull latest changes
git pull origin master

# Rebuild and restart
docker-compose build
docker-compose up -d

# Run migrations
docker-compose exec web python manage.py migrate
```

## SSL/HTTPS Setup

### Using Let's Encrypt
```bash
# Install certbot
sudo apt-get update
sudo apt-get install certbot

# Get certificate
sudo certbot certonly --standalone -d yourdomain.com

# Update docker-compose.yml to include nginx
# See docker-compose.prod.yml for example
```

### Using Cloudflare
1. Add your domain to Cloudflare
2. Enable SSL/TLS → Full (strict)
3. Create origin certificate
4. Mount certificates in nginx container

## Performance Optimization

### 1. Enable Redis Caching
Ensure these are in your .env:
```env
REDIS_URL=redis://redis:6379/0
CACHE_TTL=300
REDIS_SESSION_BACKEND=True
```

### 2. Configure Gunicorn Workers
```bash
# In Dockerfile or docker-compose.yml
CMD ["gunicorn", "Linkedrite.wsgi:application", "--workers", "4", "--threads", "2"]
```

### 3. Database Connection Pooling
```env
# In .env
DATABASE_CONN_MAX_AGE=600
```

## Monitoring

### Health Checks
```bash
# Check application health
curl -f http://localhost:8000/health/ || echo "Health check failed"

# Check all services
docker-compose ps
for service in web db redis; do
  if docker-compose ps $service | grep -q "Up"; then
    echo "✅ $service is healthy"
  else
    echo "❌ $service is down"
  fi
done
```

### Resource Usage
```bash
# Container stats
docker stats

# Disk usage
df -h
docker system df

# Clean up unused resources
docker system prune -a
```

## Security Best Practices

1. **Use strong passwords** in .env file
2. **Limit port exposure**: Only expose necessary ports
3. **Regular updates**: Keep Docker images updated
4. **Firewall rules**: 
   ```bash
   sudo ufw allow 22
   sudo ufw allow 80
   sudo ufw allow 443
   sudo ufw allow 8000
   sudo ufw enable
   ```
5. **Backup regularly**: Automate database backups

## Emergency Procedures

### Application Crash
```bash
# Check logs
docker-compose logs --tail=200 web

# Restart application
docker-compose restart web

# Full restart if needed
docker-compose down
docker-compose up -d
```

### Rollback Deployment
```bash
# List available images
docker images | grep linkedrite

# Run previous version
docker stop linkedrite
docker run -d --name linkedrite-rollback \
  -p 8000:8000 \
  --env-file .env \
  linkedrite:previous_tag
```

### Database Recovery
```bash
# Restore from backup
docker-compose exec -T db psql -U linkedrite linkedrite < backup.sql

# Reset database (WARNING: Deletes all data)
docker-compose exec web python manage.py flush --noinput
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py create_default_admin
```

## Support

For issues:
1. Check logs: `docker-compose logs`
2. Review this guide
3. Check GitHub Issues
4. Contact support

Remember to always test deployments in a staging environment first!
