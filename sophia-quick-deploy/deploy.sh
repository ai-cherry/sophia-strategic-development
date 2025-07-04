#!/bin/bash
set -euo pipefail

echo "=== Deploying Sophia AI to Docker Swarm ==="

# Initialize Swarm if needed
if ! docker info 2>/dev/null | grep -q "Swarm: active"; then
    echo "Initializing Docker Swarm..."
    docker swarm init --advertise-addr $(hostname -I | awk '{print $1}')
fi

# Deploy the stack
echo "Deploying services..."
docker stack deploy -c docker-compose.yml sophia-ai

# Wait and check
sleep 15
echo ""
echo "=== Services Status ==="
docker service ls | grep sophia-ai || echo "Services starting..."

echo ""
echo "=== Access Points ==="
echo "Backend API: http://$(hostname -I | awk '{print $1}'):8000"
echo "Frontend: http://$(hostname -I | awk '{print $1}'):3000"
echo "PostgreSQL: $(hostname -I | awk '{print $1}'):5432"
echo "Redis: $(hostname -I | awk '{print $1}'):6379"
echo ""
echo "Check status: docker service ls"
echo "View logs: docker service logs sophia-ai_backend"
