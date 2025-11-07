# LinkedRite SaaS Application

## Overview

LinkedRite has been transformed into a full-featured SaaS application with user authentication, subscription plans, and usage tracking. The application now supports Free and Premium plans with timezone-aware daily limits.

## Key Features

### Authentication System
- Email-based user registration with verification
- Login/logout functionality  
- Password reset via email
- User profile management with timezone settings

### Subscription Plans
- **Free Plan**: 20 rewrites per day
- **Premium Plan**: Unlimited rewrites (currently $0 during launch)
- Timezone-aware daily limit resets
- Usage tracking and history

### User Dashboard
- Real-time usage statistics
- Subscription status and upgrade options
- 7-day usage history
- Account settings

### Admin Panel
- User management
- Subscription management with bulk actions
- Usage statistics and monitoring
- Manual plan upgrades

## Setup Instructions

### 1. Environment Variables
Copy `.env.example` to `.env` and update with your configuration:

```bash
cp .env.example .env
```

Then edit `.env` with your actual values. Key settings include:

- **Azure OpenAI**: API key, endpoint, and deployment model
- **Email (SMTP)**: Required for user registration and password reset
- **Django**: Debug mode and secret key
- **Stripe**: Payment gateway keys (optional, currently $0 pricing)

See `.env.example` for detailed descriptions of each variable.

### 2. Database Configuration

LinkedRite supports multiple database backends. By default, it uses SQLite if no database configuration is provided.

#### Option 1: Using DATABASE_URL (Recommended)
```env
# PostgreSQL
DATABASE_URL=postgresql://username:password@localhost:5432/linkedrite

# MySQL
DATABASE_URL=mysql://username:password@localhost:3306/linkedrite

# SQLite
DATABASE_URL=sqlite:///path/to/db.sqlite3
```

#### Option 2: Individual Database Settings
```env
# For PostgreSQL
DB_ENGINE=django.db.backends.postgresql
DB_NAME=linkedrite
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432

# For MySQL
DB_ENGINE=django.db.backends.mysql
DB_NAME=linkedrite
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=3306

# For SQLite (default if not specified)
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3
```

### 3. Redis Configuration (Optional)

LinkedRite supports Redis for caching and session storage. Redis can significantly improve performance.

#### Option 1: Using REDIS_URL
```env
REDIS_URL=redis://localhost:6379/0
# With authentication:
REDIS_URL=redis://:password@localhost:6379/0
```

#### Option 2: Individual Redis Settings
```env
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=your-redis-password  # Optional
```

#### Additional Redis Options
```env
# Cache timeout in seconds (default: 300)
CACHE_TTL=300

# Use Redis for Django sessions (default: False)
REDIS_SESSION_BACKEND=True
```

### 4. Default Admin Account (Optional)

You can set default admin credentials in your `.env` file:

```env
ADMIN_EMAIL=admin@linkedrite.com
ADMIN_PASSWORD=your-secure-password
ADMIN_FIRST_NAME=Admin
ADMIN_LAST_NAME=User
```

The admin account is **automatically created/updated when the server starts**! 

Just set these in your `.env` file:
```env
ADMIN_EMAIL=admin@linkedrite.com
ADMIN_PASSWORD=your-secure-password
```

And restart your server:
```bash
python manage.py runserver
```

The system will:
- Create a new admin account if it doesn't exist
- Update existing admin account details
- **Always update the password** to match what's in .env
- Automatically give the admin a PREMIUM subscription
- Set email as verified

**No manual command needed!** When you change credentials in `.env` and restart the server, the admin account is automatically synced on the first request (no warnings, no delays).

**If you change the admin email in .env**:
```bash
# Update existing admin to new email
python manage.py create_default_admin --update-existing old-admin@example.com
```

**Security Notes:**
- Use strong passwords in production
- Never commit `.env` files with credentials to version control
- Consider using a password manager or secrets management service

**For Development Only:**
```bash
# Quick development admin setup (creates admin@localhost / admin123)
python scripts/setup_dev_admin.py
```

Alternatively, create an admin manually:
```bash
python manage.py createsuperuser
```

### 5. Run the Development Server
```bash
python manage.py runserver
```

## Application URLs

- **Homepage**: http://localhost:8000/
- **Login**: http://localhost:8000/accounts/login/
- **Sign Up**: http://localhost:8000/accounts/signup/
- **Dashboard**: http://localhost:8000/dashboard/
- **Pricing**: http://localhost:8000/pricing/
- **Admin Panel**: http://localhost:8000/admin/

## Testing the Application

### 1. User Registration Flow
1. Visit the signup page
2. Fill in the registration form (email, name, password, timezone)
3. Check your email for the verification link
4. Click the link to verify your account

### 2. Using the Rewriter
1. Login to your account
2. You'll see your daily usage counter
3. Write or paste LinkedIn content
4. Click "Rewrite with AI"
5. Usage counter updates in real-time

### 3. Admin Features
1. Login to admin panel with superuser account
2. Manage users, subscriptions, and usage
3. Use bulk actions to upgrade/downgrade plans
4. Monitor system-wide usage statistics

## Important Notes

### Email Configuration
- Gmail users: Use App Passwords instead of regular passwords
- Other providers: Update EMAIL_HOST and EMAIL_PORT accordingly
- For development: Can use console backend by setting `EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"`

### Timezone Handling
- Users select their timezone during registration
- Daily limits reset at midnight in the user's timezone
- Usage history displays in user's local time

### Security Considerations
- CSRF protection enabled on all forms
- Session-based authentication
- Email verification required
- Secure password requirements enforced

### Future Enhancements
- Payment integration is prepared but currently set to $0
- Stripe/PayPal can be enabled by updating views
- API authentication can be added for external integrations

## Docker Deployment

The application includes Docker support for easy deployment with multiple database options:

### Using Docker Compose with PostgreSQL
```bash
# Build and run with PostgreSQL database
docker-compose up --build
```

### Using Docker with SQLite
```bash
# Build the image
docker build -t linkedrite .

# Run with SQLite (default)
docker run -p 8000:8000 --env-file .env linkedrite
```

### Using Docker with External Database
```bash
# Set DATABASE_URL in your .env file
docker run -p 8000:8000 --env-file .env linkedrite
```

The Dockerfile includes:
- Non-root user for security
- Database connection waiting logic
- Automatic migrations
- Default admin account creation (if configured in .env)
- Static file collection
- Health checks

### With Redis
When Redis is configured, the application uses it for:
- **Caching**: Speeds up repeated database queries and API responses
- **Session Storage**: More scalable than database-backed sessions
- **Rate Limiting**: Can be extended to use Redis for API throttling

To use Redis with Docker Compose:
```bash
# All services including Redis
docker-compose up --build

# Without Redis (comment out redis service in docker-compose.yml)
docker-compose up --build web db
```

## Troubleshooting

### Common Issues

1. **Port 8000 Already in Use (Deployment Error)**:
   - Error: `Bind for 0.0.0.0:8000 failed: port is already allocated`
   - The deployment scripts now automatically free port 8000
   - Manual fix: `sudo lsof -t -i:8000 | xargs -r sudo kill -9`
   - Or run: `bash scripts/fix-port-8000.sh`
   - See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed solutions

2. **Email not sending**: Check EMAIL_HOST_PASSWORD and EMAIL_USE_TLS settings

3. **Migration errors**: Run `python manage.py migrate --run-syncdb`

4. **Static files not loading**: Run `python manage.py collectstatic`

5. **Import errors**: Ensure all packages in requirements.txt are installed

6. **Database connection issues**: 
   - For PostgreSQL/MySQL, ensure the database server is running
   - Check credentials in `.env` file
   - For Docker, ensure containers can communicate

### Database Reset (if needed)
```bash
# Delete the database
rm db.sqlite3

# Create new migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser again
python manage.py createsuperuser
```

## Support

For issues or questions, please check:
- Django logs in the console
- Email backend configuration
- Database migrations status
- Browser console for JavaScript errors
