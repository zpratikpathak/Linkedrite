#!/bin/bash
# Test script to verify deployment setup locally

echo "🧪 Testing LinkedRite deployment setup..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found"
    echo "Please create .env file with required variables"
    exit 1
fi

echo "✅ .env file found"

# Test building the Docker image
echo "Building Docker image..."
if docker build . -t linkedrite:test; then
    echo "✅ Docker image built successfully"
else
    echo "❌ Failed to build Docker image"
    exit 1
fi

# Create test docker-compose file
cat > docker-compose.test.yml << 'EOF'
services:
  web:
    image: linkedrite:test
    ports:
      - "8001:8000"
    env_file:
      - .env
    environment:
      - DATABASE_URL=sqlite:///app/db.sqlite3
      - DEBUG=True
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/"]
      interval: 30s
      timeout: 10s
      retries: 3
EOF

echo "Starting test container..."
docker-compose -f docker-compose.test.yml up -d

echo "Waiting for container to start..."
sleep 10

# Check if container is running
if docker-compose -f docker-compose.test.yml ps | grep -q "Up"; then
    echo "✅ Container is running"
    
    # Test if application responds
    if curl -f -s -o /dev/null http://localhost:8001; then
        echo "✅ Application is responding on port 8001"
        echo "🎉 Deployment test successful!"
        echo ""
        echo "Application is running at: http://localhost:8001"
        echo "Admin panel at: http://localhost:8001/admin/"
        echo ""
        echo "To stop the test container, run:"
        echo "docker-compose -f docker-compose.test.yml down"
    else
        echo "❌ Application is not responding"
        echo "Container logs:"
        docker-compose -f docker-compose.test.yml logs
        docker-compose -f docker-compose.test.yml down
        exit 1
    fi
else
    echo "❌ Container failed to start"
    docker-compose -f docker-compose.test.yml logs
    docker-compose -f docker-compose.test.yml down
    exit 1
fi
