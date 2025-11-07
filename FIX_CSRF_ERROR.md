# Fix for CSRF Verification Failed Error

## Quick Fix (Add to your .env file on server)

```bash
# Add these lines to your .env file
SITE_URL=http://YOUR-SERVER-IP:8000
CSRF_TRUSTED_ORIGINS=http://YOUR-SERVER-IP:8000,http://localhost:8000

# If using a domain name:
SITE_URL=https://linkedrite.yourdomain.com
CSRF_TRUSTED_ORIGINS=https://linkedrite.yourdomain.com,https://www.linkedrite.yourdomain.com
USE_HTTPS=True
```

## Apply the Fix

### Option 1: Quick Fix (No rebuild needed)
```bash
cd ~/linkedrite

# Edit .env file
nano .env

# Add the SITE_URL and CSRF_TRUSTED_ORIGINS (replace with your actual server IP or domain)
# Example for IP: 
# SITE_URL=http://123.456.789.0:8000
# CSRF_TRUSTED_ORIGINS=http://123.456.789.0:8000

# Restart the web container
docker-compose -f docker-compose.prod.yml restart web
```

### Option 2: If Quick Fix Doesn't Work
```bash
# Rebuild with updated settings
cd ~/linkedrite
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml build --no-cache web
docker-compose -f docker-compose.prod.yml up -d
```

## Examples for Different Scenarios

### 1. Using Server IP Address
```env
SITE_URL=http://192.168.1.100:8000
CSRF_TRUSTED_ORIGINS=http://192.168.1.100:8000
DEBUG=False
```

### 2. Using Domain Name (HTTP)
```env
SITE_URL=http://linkedrite.example.com
CSRF_TRUSTED_ORIGINS=http://linkedrite.example.com,http://www.linkedrite.example.com
DEBUG=False
```

### 3. Using Domain Name (HTTPS)
```env
SITE_URL=https://linkedrite.example.com
CSRF_TRUSTED_ORIGINS=https://linkedrite.example.com,https://www.linkedrite.example.com
USE_HTTPS=True
DEBUG=False
```

### 4. Multiple Domains
```env
SITE_URL=https://linkedrite.com
CSRF_TRUSTED_ORIGINS=https://linkedrite.com,https://www.linkedrite.com,https://app.linkedrite.com
USE_HTTPS=True
DEBUG=False
```

## What Causes This Error?

Django's CSRF protection verifies that POST requests come from trusted origins. When you access your site from a domain/IP that Django doesn't recognize as trusted, it blocks the request for security.

## Complete .env Example

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=*

# IMPORTANT: Replace with your actual server IP or domain
SITE_URL=http://YOUR-SERVER-IP:8000
CSRF_TRUSTED_ORIGINS=http://YOUR-SERVER-IP:8000
USE_HTTPS=False  # Set to True if using HTTPS

# Database
DATABASE_URL=postgres://linkedrite:password@db:5432/linkedrite

# Redis
REDIS_URL=redis://redis:6379/0

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=LinkedRite <noreply@yourdomain.com>

# OpenAI
OPENAI_API_KEY=sk-...
# Or Azure
AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_ENDPOINT=...
AZURE_OPENAI_API_VERSION=2024-02-01
AZURE_OPENAI_DEPLOYMENT_NAME=...

# Admin Account
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=secure-password
ADMIN_FIRST_NAME=Admin
ADMIN_LAST_NAME=User
```

## Verify the Fix

After applying the fix:

1. Try logging in again
2. Check if CSRF error is gone
3. If still having issues, check the logs:
   ```bash
   docker-compose -f docker-compose.prod.yml logs web | grep -i csrf
   ```

## Additional Troubleshooting

If you're still getting CSRF errors:

1. **Clear browser cookies** for your site
2. **Use incognito/private mode** to test
3. **Check DEBUG is False** in production
4. **Ensure consistent URL** (with or without www, trailing slash)
5. **Behind a reverse proxy?** Make sure proxy headers are forwarded correctly

The updated settings.py now handles CSRF properly for production deployments!
