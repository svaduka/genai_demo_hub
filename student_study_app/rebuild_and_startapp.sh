#!/bin/bash
set +x

# Check if Docker is installed
if ! command -v docker &> /dev/null
then
    echo "Docker could not be found. Please install Docker first."
    exit 1
fi

echo "Docker is installed."

# Define the target port
PORT=7777

# Find any Docker container using the port
echo "Checking if any Docker container is using port $PORT..."
CONTAINER_ID=$(docker ps --filter "publish=$PORT" --format "{{.ID}}")

if [ -n "$CONTAINER_ID" ]; then
    echo "Stopping and removing Docker container $CONTAINER_ID using port $PORT..."
    docker stop $CONTAINER_ID
    docker rm $CONTAINER_ID
else
    echo "No Docker container is using port $PORT."
fi

# Kill any process using the port (if applicable)
echo "Checking if any other process is using port $PORT..."
PID=$(lsof -t -i:$PORT)

if [ -n "$PID" ]; then
    echo "Killing process $PID using port $PORT..."
    kill -9 $PID
else
    echo "No other process is using port $PORT."
fi

# Stop all running containers
echo "Stopping all running Docker containers..."
docker stop $(docker ps -q) 2>/dev/null || echo "No running containers to stop."

# Remove all containers
echo "Removing all Docker containers..."
docker rm $(docker ps -a -q) 2>/dev/null || echo "No containers to remove."

# Remove all images
echo "Removing all Docker images..."
docker rmi $(docker images -q) -f 2>/dev/null || echo "No images to remove."

# Remove all dangling volumes (optional)
echo "Removing unused Docker volumes..."
docker volume prune -f

# Run docker-compose build and start in detached mode
echo "Building and starting containers using docker-compose..."
docker-compose up --build -d

echo "All done!"