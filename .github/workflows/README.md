# LinkedRite GitHub Actions Workflows

## Available Workflows

### 1. Deploy LinkedRite SaaS (`deploy-saas.yml`)
**Trigger**: Push to `master` branch

This is the main deployment workflow that sets up a complete production environment with:
- PostgreSQL database
- Redis cache
- Web application
- Automatic migrations and static file collection
- Health checks for all services

**Port**: Application runs on port `8000`

### 2. Deploy LinkedRite SaaS Simple (`deploy-saas-simple.yml`)
**Trigger**: 
- Manual trigger (workflow_dispatch)
- Push to `simple-deploy` branch

A simplified deployment using a single container with SQLite database. Good for:
- Testing deployments
- Small-scale deployments
- Servers with limited resources

**Port**: Application runs on port `8000`

### 3. Deploy Docker Container - Disabled (`dockerDeploy.yml`)
**Status**: DISABLED
The old deployment workflow. Kept for reference but disabled.

## Required GitHub Secrets

Configure these in your repository settings under Secrets and variables > Actions:

### Server Connection
- `SERVER_HOST`: Your server IP or hostname
- `SERVER_USERNAME`: SSH username for deployment
- `SSH_KEY`: Private SSH key for authentication
- `SSH_PORT`: SSH port (usually 22)

### Application Configuration
- `ENVIRONMENTAL_VARIABLES`: Complete .env file contents including:
  ```
  # Django settings
  SECRET_KEY=your-secret-key
  DEBUG=False
  ALLOWED_HOSTS=your-domain.com,localhost
  
  # Database (for docker-compose deployment)
  POSTGRES_DB=linkedrite
  POSTGRES_USER=linkedrite
  POSTGRES_PASSWORD=secure-password
  
  # Or for external database
  DATABASE_URL=postgres://user:pass@host:5432/dbname
  
  # Redis (optional)
  REDIS_URL=redis://localhost:6379/0
  
  # Email settings
  EMAIL_HOST=smtp.gmail.com
  EMAIL_PORT=587
  EMAIL_HOST_USER=your-email@gmail.com
  EMAIL_HOST_PASSWORD=your-app-password
  EMAIL_USE_TLS=True
  DEFAULT_FROM_EMAIL=LinkedRite <noreply@your-domain.com>
  
  # OpenAI API
  OPENAI_API_KEY=sk-...
  # Or Azure OpenAI
  AZURE_OPENAI_API_KEY=...
  AZURE_OPENAI_ENDPOINT=...
  AZURE_OPENAI_API_VERSION=2024-02-01
  AZURE_OPENAI_DEPLOYMENT_NAME=...
  
  # Admin account (auto-created on first run)
  ADMIN_EMAIL=admin@your-domain.com
  ADMIN_PASSWORD=secure-admin-password
  ADMIN_FIRST_NAME=Admin
  ADMIN_LAST_NAME=User
  ```

## Server Prerequisites

Before running the workflows, ensure your server has:

1. **Docker installed**:
   ```bash
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   sudo usermod -aG docker $USER
   ```

2. **Docker Compose installed** (for main workflow):
   ```bash
   sudo apt-get update
   sudo apt-get install docker-compose-plugin
   ```

3. **Required ports open**:
   - Port 8000 for the web application
   - Port 22 (or custom) for SSH

4. **Sufficient disk space** for Docker images and volumes

## Usage

### Full Deployment (Recommended)
1. Set up all required secrets in GitHub
2. Push to `master` branch
3. Workflow will automatically:
   - Build Docker image
   - Deploy PostgreSQL, Redis, and Web containers
   - Run migrations
   - Create admin account
   - Collect static files
   - Verify deployment

### Simple Deployment
1. Set up all required secrets in GitHub
2. Either:
   - Go to Actions tab and manually trigger "Deploy LinkedRite SaaS (Simple)"
   - Or push to `simple-deploy` branch
3. Uses SQLite and single container

## Monitoring Deployment

Check deployment status:
1. Go to Actions tab in GitHub
2. Click on the running workflow
3. View real-time logs

On your server, check status:
```bash
# For full deployment
cd ~/linkedrite
docker-compose -f docker-compose.prod.yml ps
docker-compose -f docker-compose.prod.yml logs

# For simple deployment
docker ps
docker logs linkedrite
```

## Troubleshooting

### Container won't start
Check logs:
```bash
docker logs linkedrite
# or
docker-compose -f docker-compose.prod.yml logs web
```

### Database connection errors
- Ensure DATABASE_URL or POSTGRES_* variables are correct
- Check if database container is running
- Verify network connectivity between containers

### Port 8000 not accessible
- Check firewall rules: `sudo ufw allow 8000`
- Verify container is running: `docker ps`
- Test locally: `curl http://localhost:8000`

### Static files not loading
- Ensure `STATIC_ROOT` is properly set
- Check if `collectstatic` ran successfully
- Verify volume mounts are correct

## Rollback

If deployment fails:
```bash
# List available images
docker images | grep linkedrite

# Run previous version
docker run -d --name linkedrite -p 8000:8000 --env-file .env linkedrite:previous-tag
```
