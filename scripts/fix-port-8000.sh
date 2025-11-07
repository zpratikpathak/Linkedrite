#!/bin/bash
# Script to free up port 8000 for LinkedRite deployment

echo "🔧 LinkedRite Port 8000 Cleanup Script"
echo "======================================"

# Function to free port 8000
free_port_8000() {
  echo "Checking if port 8000 is in use..."
  
  # Find process using port 8000
  PORT_PID=$(sudo lsof -t -i:8000 || true)
  
  if [ ! -z "$PORT_PID" ]; then
    echo "⚠️  Port 8000 is in use by PID: $PORT_PID"
    
    # Try to identify the process
    PROCESS_INFO=$(ps -p $PORT_PID -o comm= 2>/dev/null || echo "unknown")
    echo "Process: $PROCESS_INFO"
    
    # Show more details about the process
    echo "Process details:"
    ps -fp $PORT_PID || true
    
    # Ask for confirmation
    read -p "Do you want to stop this process? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
      echo "Stopping process using port 8000..."
      sudo kill -9 $PORT_PID || true
      sleep 2
      echo "✅ Process stopped"
    else
      echo "❌ Aborted. Port 8000 is still in use."
      return 1
    fi
  else
    echo "✅ No process found using port 8000"
  fi
  
  # Check for Docker containers using port 8000
  echo ""
  echo "Checking for Docker containers using port 8000..."
  
  CONTAINERS=$(docker ps --format "table {{.ID}}\t{{.Names}}\t{{.Ports}}" | grep -E "0\.0\.0\.0:8000|:::8000" || true)
  
  if [ ! -z "$CONTAINERS" ]; then
    echo "⚠️  Found Docker containers using port 8000:"
    echo "$CONTAINERS"
    
    # Extract container IDs
    CONTAINER_IDS=$(echo "$CONTAINERS" | grep -v "CONTAINER" | awk '{print $1}')
    
    for CONTAINER in $CONTAINER_IDS; do
      if [ ! -z "$CONTAINER" ]; then
        CONTAINER_NAME=$(docker ps --format "{{.Names}}" -f "id=$CONTAINER")
        echo ""
        echo "Container: $CONTAINER_NAME (ID: $CONTAINER)"
        
        # Ask for confirmation
        read -p "Do you want to stop this container? (y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
          echo "Stopping container: $CONTAINER_NAME"
          docker stop $CONTAINER || true
          docker rm $CONTAINER || true
          echo "✅ Container stopped and removed"
        else
          echo "⏩ Skipped container: $CONTAINER_NAME"
        fi
      fi
    done
  else
    echo "✅ No Docker containers found using port 8000"
  fi
  
  # Final check
  echo ""
  echo "Final check..."
  
  STILL_IN_USE=$(sudo lsof -t -i:8000 || true)
  CONTAINERS_STILL=$(docker ps --format "table {{.ID}}\t{{.Names}}\t{{.Ports}}" | grep -E "0\.0\.0\.0:8000|:::8000" || true)
  
  if [ -z "$STILL_IN_USE" ] && [ -z "$CONTAINERS_STILL" ]; then
    echo "✅ Port 8000 is now free and available for LinkedRite!"
    return 0
  else
    echo "❌ Port 8000 is still in use. Please check manually."
    return 1
  fi
}

# Run the function
free_port_8000

# Exit with appropriate code
exit $?
