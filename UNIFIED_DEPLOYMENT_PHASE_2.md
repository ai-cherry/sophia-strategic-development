# PHASE 2: BACKEND CONTAINERIZATION & DEPLOYMENT (4 Hours)

## Overview
Deploy the FastAPI backend to Lambda Labs with WebSocket support, establishing the API at api.sophia-intel.ai.

## Prerequisites from Phase 1
- [ ] Frontend configuration fixed and tested
- [ ] Environment variables properly set
- [ ] CI/CD pipelines ready

## 2.1 Create Production Dockerfile (30 minutes)

### A. Multi-Stage Dockerfile
```dockerfile
# Dockerfile (root directory)
# Build stage
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.11-slim

# Security: Run as non-root user
RUN useradd -m -u 1000 sophia && \
    mkdir -p /app && \
    chown -R sophia:sophia /app

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /root/.local /home/sophia/.local

# Copy application code
COPY --chown=sophia:sophia backend/ ./backend/
COPY --chown=sophia:sophia infrastructure/ ./infrastructure/
COPY --chown=sophia:sophia core/ ./core/
COPY --chown=sophia:sophia api/ ./api/

# Switch to non-root user
USER sophia

# Add local bin to PATH
ENV PATH=/home/sophia/.local/bin:$PATH
ENV PYTHONPATH=/app:$PYTHONPATH

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/health').raise_for_status()"

EXPOSE 8000

# Run with proper module path
CMD ["uvicorn", "backend.app.fastapi_main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### B. Docker Ignore File
```
# .dockerignore
__pycache__
*.pyc
*.pyo
*.pyd
.Python
pip-log.txt
pip-delete-this-directory.txt
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.log
.git
.gitignore
.mypy_cache
.pytest_cache
.hypothesis
.env*
!.env.template
frontend/
docs/
tests/
scripts/
*.md
.vscode/
.idea/
```

### C. Update requirements.txt for WebSocket
```txt
# Add to requirements.txt
websockets==12.0
python-multipart==0.0.6
aiofiles==23.2.1
```

## 2.2 Add WebSocket Support (45 minutes)

### A. Create WebSocket Handler
```python
# backend/app/websocket_handler.py
import json
import logging
from typing import Dict, Set
from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime

from backend.services.unified_chat_service import UnifiedChatService
from backend.models.chat_models import ChatRequest, ChatContext, AccessLevel

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_contexts: Dict[str, dict] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        self.user_contexts[user_id] = {
            "connected_at": datetime.utcnow(),
            "message_count": 0
        }
        logger.info(f"WebSocket connected: {user_id}")

    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
            del self.user_contexts[user_id]
            logger.info(f"WebSocket disconnected: {user_id}")

    async def send_personal_message(self, message: str, user_id: str):
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_text(message)

    async def broadcast(self, message: str, exclude_user: str = None):
        for user_id, connection in self.active_connections.items():
            if user_id != exclude_user:
                await connection.send_text(message)

manager = ConnectionManager()

async def websocket_endpoint(websocket: WebSocket, user_id: str, chat_service: UnifiedChatService):
    await manager.connect(websocket, user_id)

    try:
        while True:
            # Receive message
            data = await websocket.receive_text()
            message_data = json.loads(data)

            # Update context
            if user_id in manager.user_contexts:
                manager.user_contexts[user_id]["message_count"] += 1

            # Create chat request
            chat_request = ChatRequest(
                message=message_data["message"],
                user_id=user_id,
                context=ChatContext(message_data.get("search_context", "business_intelligence")),
                access_level=AccessLevel(message_data.get("access_level", "employee"))
            )

            # Process through unified service
            response = await chat_service.process_chat(chat_request)

            # Send response
            await websocket.send_text(json.dumps({
                "type": "response",
                "data": {
                    "response": response.response,
                    "sources": response.sources,
                    "suggestions": response.suggestions,
                    "timestamp": response.timestamp.isoformat()
                }
            }))

    except WebSocketDisconnect:
        manager.disconnect(user_id)
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {e}")
        await websocket.send_text(json.dumps({
            "type": "error",
            "message": "An error occurred processing your message"
        }))
        manager.disconnect(user_id)
```

### B. Update FastAPI Main
```python
# Add to backend/app/fastapi_main.py
from backend.app.websocket_handler import websocket_endpoint, manager

# Add WebSocket route
@app.websocket("/ws/{user_id}")
async def websocket_route(websocket: WebSocket, user_id: str):
    await websocket_endpoint(websocket, user_id, chat_service)

# Add connection status endpoint
@app.get("/api/v1/ws/connections")
async def get_active_connections():
    return {
        "active_connections": len(manager.active_connections),
        "users": list(manager.active_connections.keys())
    }
```

## 2.3 Lambda Labs Deployment Setup (1 hour)

### A. Create Deployment Script
```bash
#!/bin/bash
# scripts/deploy-backend-lambda.sh

set -e

# Configuration
LAMBDA_HOST="${LAMBDA_LABS_HOST:-146.235.200.1}"
LAMBDA_USER="${LAMBDA_LABS_USER:-ubuntu}"
IMAGE_NAME="sophia-ai-backend"
CONTAINER_NAME="sophia-backend"

echo "🚀 Deploying Backend to Lambda Labs"
echo "===================================="

# Build Docker image
echo "📦 Building Docker image..."
docker build -t ${IMAGE_NAME}:latest .

# Save image
echo "💾 Saving Docker image..."
docker save ${IMAGE_NAME}:latest | gzip > /tmp/sophia-backend.tar.gz

# Copy to Lambda Labs
echo "📤 Copying to Lambda Labs..."
scp /tmp/sophia-backend.tar.gz ${LAMBDA_USER}@${LAMBDA_HOST}:~/

# Deploy on Lambda Labs
echo "🚀 Deploying on Lambda Labs..."
ssh ${LAMBDA_USER}@${LAMBDA_HOST} << 'EOF'
    # Load image
    echo "📥 Loading Docker image..."
    docker load < ~/sophia-backend.tar.gz

    # Stop existing container
    echo "🛑 Stopping existing container..."
    docker stop sophia-backend || true
    docker rm sophia-backend || true

    # Run new container
    echo "▶️ Starting new container..."
    docker run -d \
        --name sophia-backend \
        --restart unless-stopped \
        -p 8000:8000 \
        -e ENVIRONMENT=production \
        -e PULUMI_ORG=scoobyjava-org \
        --health-cmd="curl -f http://localhost:8000/health || exit 1" \
        --health-interval=30s \
        --health-timeout=10s \
        --health-retries=3 \
        sophia-ai-backend:latest

    # Wait for health
    echo "⏳ Waiting for container to be healthy..."
    for i in {1..30}; do
        if docker inspect --format='{{.State.Health.Status}}' sophia-backend | grep -q healthy; then
            echo "✅ Container is healthy!"
            break
        fi
        sleep 2
    done

    # Show status
    docker ps | grep sophia-backend
EOF

echo "✅ Backend deployment complete!"
```

### B. GitHub Actions Deployment
```yaml
# .github/workflows/deploy-backend.yml
name: Deploy Backend to Lambda Labs

on:
  push:
    branches: [main]
    paths:
      - 'backend/**'
      - 'infrastructure/**'
      - 'core/**'
      - 'api/**'
      - 'Dockerfile'
      - 'requirements.txt'

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production

    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Build Docker image
        run: |
          docker build -t sophia-ai-backend:${{ github.sha }} .
          docker tag sophia-ai-backend:${{ github.sha }} sophia-ai-backend:latest

      - name: Save Docker image
        run: |
          docker save sophia-ai-backend:latest | gzip > sophia-backend.tar.gz

      - name: Copy to Lambda Labs
        uses: appleboy/scp-action@v0.1.5
        with:
          host: ${{ secrets.LAMBDA_LABS_HOST }}
          username: ubuntu
          key: ${{ secrets.LAMBDA_LABS_SSH_KEY }}
          source: "sophia-backend.tar.gz"
          target: "~/"

      - name: Deploy on Lambda Labs
        uses: appleboy/ssh-action@v0.1.7
        with:
          host: ${{ secrets.LAMBDA_LABS_HOST }}
          username: ubuntu
          key: ${{ secrets.LAMBDA_LABS_SSH_KEY }}
          script: |
            # Load and deploy
            docker load < ~/sophia-backend.tar.gz
            docker stop sophia-backend || true
            docker rm sophia-backend || true

            # Run with environment variables from Pulumi ESC
            docker run -d \
              --name sophia-backend \
              --restart unless-stopped \
              -p 8000:8000 \
              -e ENVIRONMENT=production \
              -e PULUMI_ORG=scoobyjava-org \
              sophia-ai-backend:latest

            # Health check
            sleep 30
            curl -f http://localhost:8000/health || exit 1
```

## 2.4 Nginx Configuration (45 minutes)

### A. Create Nginx Configuration
```nginx
# /etc/nginx/sites-available/sophia-api.conf
upstream sophia_backend {
    server 127.0.0.1:8000;
    keepalive 64;
}

server {
    listen 80;
    server_name api.sophia-intel.ai;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.sophia-intel.ai;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/api.sophia-intel.ai/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.sophia-intel.ai/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # API Routes
    location / {
        proxy_pass http://sophia_backend;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # WebSocket Support
    location ~ ^/ws/ {
        proxy_pass http://sophia_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket timeouts
        proxy_connect_timeout 7d;
        proxy_send_timeout 7d;
        proxy_read_timeout 7d;
    }

    # Health check endpoint
    location /health {
        proxy_pass http://sophia_backend/health;
        access_log off;
    }
}
```

### B. SSL Certificate Setup
```bash
# Install Certbot
sudo apt-get update
sudo apt-get install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d api.sophia-intel.ai \
  --non-interactive \
  --agree-tos \
  --email admin@sophia-intel.ai

# Auto-renewal
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

## 2.5 Health Monitoring (30 minutes)

### A. Create Health Check Script
```python
# scripts/health-check-backend.py
import requests
import websocket
import json
import sys
from datetime import datetime

API_URL = "https://api.sophia-intel.ai"
WS_URL = "wss://api.sophia-intel.ai/ws/health-check"

def check_health():
    results = {
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {}
    }

    # Check HTTP health
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        results["checks"]["http_health"] = {
            "status": "pass" if response.status_code == 200 else "fail",
            "status_code": response.status_code,
            "response": response.json()
        }
    except Exception as e:
        results["checks"]["http_health"] = {
            "status": "fail",
            "error": str(e)
        }

    # Check WebSocket
    try:
        ws = websocket.create_connection(WS_URL, timeout=5)
        ws.send(json.dumps({"type": "ping"}))
        response = ws.recv()
        ws.close()
        results["checks"]["websocket"] = {
            "status": "pass",
            "response": response
        }
    except Exception as e:
        results["checks"]["websocket"] = {
            "status": "fail",
            "error": str(e)
        }

    # Check API endpoints
    endpoints = [
        "/api/v1/dashboard/main",
        "/api/v1/chat/contexts",
        "/api/v1/ws/connections"
    ]

    for endpoint in endpoints:
        try:
            response = requests.get(f"{API_URL}{endpoint}", timeout=5)
            results["checks"][endpoint] = {
                "status": "pass" if response.status_code == 200 else "fail",
                "status_code": response.status_code
            }
        except Exception as e:
            results["checks"][endpoint] = {
                "status": "fail",
                "error": str(e)
            }

    return results

if __name__ == "__main__":
    results = check_health()
    print(json.dumps(results, indent=2))

    # Exit with error if any check failed
    if any(check["status"] == "fail" for check in results["checks"].values()):
        sys.exit(1)
```

### B. GitHub Actions Health Monitor
```yaml
# .github/workflows/backend-health-monitor.yml
name: Backend Health Monitor

on:
  schedule:
    - cron: '*/5 * * * *'  # Every 5 minutes
  workflow_dispatch:

jobs:
  health-check:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install requests websocket-client

      - name: Run health check
        run: python scripts/health-check-backend.py

      - name: Notify on failure
        if: failure()
        uses: 8398a7/action-slack@v3
        with:
          status: ${{ job.status }}
          text: '🚨 Backend health check failed!'
          webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

## Success Criteria ✅
- [ ] Docker image builds successfully (< 350MB)
- [ ] Backend accessible at https://api.sophia-intel.ai/health
- [ ] WebSocket connections establish at wss://api.sophia-intel.ai/ws/{user_id}
- [ ] All API endpoints return expected responses
- [ ] SSL certificate valid and auto-renewing
- [ ] Health monitoring active

## Rollback Plan 🔄
```bash
# SSH to Lambda Labs
ssh ubuntu@146.235.200.1

# Rollback to previous container
docker stop sophia-backend
docker run -d --name sophia-backend-old sophia-ai-backend:previous-tag

# Rollback Nginx if needed
sudo cp /etc/nginx/sites-available/sophia-api.conf.backup /etc/nginx/sites-available/sophia-api.conf
sudo nginx -t && sudo systemctl reload nginx
```

## Phase 2 Completion Checklist
- [ ] Dockerfile created and optimized
- [ ] WebSocket support implemented
- [ ] Backend deployed to Lambda Labs
- [ ] Nginx configured with SSL
- [ ] Health monitoring active
- [ ] All endpoints tested
- [ ] Ready for Phase 3: MCP Server Deployment

## Time Tracking
- Start Time: ___________
- End Time: ___________
- Total Duration: ___________
- Issues Encountered: ___________

## Notes
_Document any deviations from the plan or additional fixes required_
