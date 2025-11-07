#!/bin/bash
# Quick fix for missing Python dependencies in Docker container

echo "🔧 LinkedRite Missing Dependencies Fix"
echo "====================================="

# Check if running in the right directory
if [ ! -f "docker-compose.prod.yml" ] && [ ! -f "docker-compose.yml" ]; then
    echo "❌ Error: No docker-compose file found. Please run from LinkedRite directory."
    exit 1
fi

# Determine which compose file to use
if [ -f "docker-compose.prod.yml" ]; then
    COMPOSE_FILE="docker-compose.prod.yml"
else
    COMPOSE_FILE="docker-compose.yml"
fi

echo "Using compose file: $COMPOSE_FILE"

# Option 1: Quick fix - Install missing packages directly in running container
echo ""
echo "Option 1: Quick fix (install in running container)"
echo "This will install missing packages but won't persist after container restart."
read -p "Do you want to apply quick fix? (y/N) " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Installing missing packages in web container..."
    
    # Get the web container name
    WEB_CONTAINER=$(docker-compose -f $COMPOSE_FILE ps -q web)
    
    if [ -z "$WEB_CONTAINER" ]; then
        echo "❌ Web container is not running"
    else
        # Install missing packages
        docker exec $WEB_CONTAINER pip install \
            dj-database-url \
            psycopg2-binary \
            redis \
            django-redis \
            asgiref
        
        echo "✅ Packages installed. Restarting web container..."
        docker-compose -f $COMPOSE_FILE restart web
        
        echo "⚠️  Note: This is a temporary fix. Rebuild the image for a permanent solution."
    fi
fi

# Option 2: Rebuild image
echo ""
echo "Option 2: Permanent fix (rebuild Docker image)"
echo "This will rebuild the image with all dependencies."
read -p "Do you want to rebuild the image? (y/N) " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Stopping containers..."
    docker-compose -f $COMPOSE_FILE down
    
    echo "Rebuilding image without cache..."
    docker-compose -f $COMPOSE_FILE build --no-cache web
    
    echo "Starting containers..."
    docker-compose -f $COMPOSE_FILE up -d
    
    echo "Waiting for services to be ready..."
    sleep 10
    
    echo "Running migrations..."
    docker-compose -f $COMPOSE_FILE exec -T web python manage.py migrate --noinput
    
    echo "✅ Image rebuilt with all dependencies"
fi

# Check status
echo ""
echo "Checking container status..."
docker-compose -f $COMPOSE_FILE ps

# Test if application is working
echo ""
echo "Testing application..."
if curl -f -s -o /dev/null http://localhost:8000; then
    echo "✅ Application is responding!"
else
    echo "❌ Application is not responding. Check logs:"
    echo "docker-compose -f $COMPOSE_FILE logs web"
fi

echo ""
echo "🎉 Fix process completed!"
