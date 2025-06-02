#!/bin/bash

# Script untuk men-deploy dan mengetes API endpoint ruangan

echo "===== Deploying and Testing Room API Endpoints ====="

# Check if API container is running
API_CONTAINER=$(docker ps --filter name=api --format "{{.Names}}")

if [ -z "$API_CONTAINER" ]; then
    echo "API container not found. Starting API container..."
    
    # Start API container with docker-compose
    docker-compose up -d api
    
    # Wait for API to start
    echo "Waiting for API to start..."
    sleep 5
else
    echo "API container is running: $API_CONTAINER"
    
    # Restart API to load new code
    echo "Restarting API container to load new code..."
    docker-compose restart api
    
    # Wait for API to restart
    echo "Waiting for API to restart..."
    sleep 5
fi

# Run the test script
echo "Running test script..."
python test_room_api.py

echo "===== Test Complete ====="
