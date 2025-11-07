# Test script to verify deployment setup locally on Windows

Write-Host "🧪 Testing LinkedRite deployment setup..." -ForegroundColor Cyan

# Check if .env exists
if (-not (Test-Path .env)) {
    Write-Host "❌ .env file not found" -ForegroundColor Red
    Write-Host "Please create .env file with required variables"
    exit 1
}

Write-Host "✅ .env file found" -ForegroundColor Green

# Test building the Docker image
Write-Host "Building Docker image..." -ForegroundColor Yellow
$buildResult = docker build . -t linkedrite:test 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Docker image built successfully" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to build Docker image" -ForegroundColor Red
    Write-Host $buildResult
    exit 1
}

# Create test docker-compose file
@"
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
"@ | Out-File -FilePath docker-compose.test.yml -Encoding UTF8

Write-Host "Starting test container..." -ForegroundColor Yellow
docker-compose -f docker-compose.test.yml up -d

Write-Host "Waiting for container to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Check if container is running
$psResult = docker-compose -f docker-compose.test.yml ps
if ($psResult -match "Up") {
    Write-Host "✅ Container is running" -ForegroundColor Green
    
    # Test if application responds
    try {
        $response = Invoke-WebRequest -Uri http://localhost:8001 -UseBasicParsing -TimeoutSec 5
        Write-Host "✅ Application is responding on port 8001" -ForegroundColor Green
        Write-Host "🎉 Deployment test successful!" -ForegroundColor Magenta
        Write-Host ""
        Write-Host "Application is running at: http://localhost:8001" -ForegroundColor Cyan
        Write-Host "Admin panel at: http://localhost:8001/admin/" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "To stop the test container, run:" -ForegroundColor Yellow
        Write-Host "docker-compose -f docker-compose.test.yml down" -ForegroundColor White
    } catch {
        Write-Host "❌ Application is not responding" -ForegroundColor Red
        Write-Host "Container logs:" -ForegroundColor Yellow
        docker-compose -f docker-compose.test.yml logs
        docker-compose -f docker-compose.test.yml down
        exit 1
    }
} else {
    Write-Host "❌ Container failed to start" -ForegroundColor Red
    Write-Host "Container logs:" -ForegroundColor Yellow
    docker-compose -f docker-compose.test.yml logs
    docker-compose -f docker-compose.test.yml down
    exit 1
}
