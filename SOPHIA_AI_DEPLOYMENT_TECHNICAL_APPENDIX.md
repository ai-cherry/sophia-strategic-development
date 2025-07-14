# Sophia AI Deployment - Technical Appendix

## Deployment Commands & Configurations Attempted

### 1. Backend Deployment Attempts

#### Local Backend Startup
```bash
# Successfully starts on port 8001
cd /Users/lynnmusil/sophia-main
source local.env
python backend/app/unified_chat_backend.py

# Output shows:
# ✅ Sophia AI Unified Chat Backend initialized
# Environment: prod
# Modern Stack connection successful
# Running on http://127.0.0.1:8001
```

#### Docker Deployment to Lambda Labs
```bash
# Attempted but failed due to build issues
ssh -i ~/.ssh/sophia2025.pem ubuntu@192.222.58.232
docker build -f Dockerfile.backend -t sophia-backend .
# ERROR: g++ compiler missing, asyncpg build fails
```

### 2. Frontend Deployment to Vercel

#### Successful Vercel Deployment Commands
```bash
cd frontend
vercel --prod --yes

# Creates deployment at:
# https://frontend-[hash]-lynn-musils-projects.vercel.app
```

#### Environment Variable Issues
```javascript
// frontend/.env.production
VITE_API_URL=http://192.222.58.232:8001  // Doesn't work - not public
VITE_API_URL=http://localhost:8001       // Doesn't work - wrong context
VITE_API_URL=https://[ngrok-url].app     // Works but temporary
```

### 3. ngrok Configuration for Backend Exposure
```bash
# Temporary solution that works
ngrok http 8001
# Provides URL like: https://44d334838362.ngrok.app
```

### 4. MCP Server Configuration

#### Current MCP Server Mapping
```json
{
  "ai_memory": {"port": 9001, "file": "mcp-servers/ai_memory/ai_memory_mcp_server.py"},
  "codacy": {"port": 3008, "file": "mcp-servers/codacy/codacy_mcp_server.py"},
  "github": {"port": 9003, "file": "mcp-servers/github/github_mcp_server.py"},
  "linear": {"port": 9004, "file": "mcp-servers/linear/linear_mcp_server.py"},
  "asana": {"port": 9006, "file": "mcp-servers/asana/asana_mcp_server.py"},
  "notion": {"port": 9102, "file": "mcp-servers/notion/notion_mcp_server.py"},
  "slack": {"port": 9101, "file": "mcp-servers/slack/slack_mcp_server.py"}
}
```

### 5. K3s Configuration from PR #184

#### Deployment Manifests Structure
```
k3s-manifests/
├── kustomization.yaml
├── mcp-asana.yaml
├── mcp-codacy.yaml
├── mcp-github.yaml
├── mcp-linear.yaml
├── mcp-notion.yaml
└── namespace.yaml
```

#### Sample K3s Deployment (mcp-asana.yaml)
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mcp-asana
  namespace: sophia-ai
spec:
  replicas: 1
  selector:
    matchLabels:
      app: mcp-asana
  template:
    metadata:
      labels:
        app: mcp-asana
    spec:
      nodeSelector:
        node-role.kubernetes.io/mcp: "true"
      containers:
      - name: mcp-asana
        image: scoobyjava15/mcp-asana:latest
        ports:
        - containerPort: 9006
```

### 6. Error Messages & Diagnostics

#### Modern Stack Connection Error
```
snowflake.connector.errors.ProgrammingError: 251005: 251005: User is empty
```

#### Frontend TypeError
```
TypeError: Cannot read properties of undefined (reading 'toUpperCase')
# Occurs in UnifiedChatDashboard.tsx when systemStatus is undefined
```

#### MCP Server Build Failures
```
ERROR: Missing Python packages: ['asyncpg']
# When g++ compiler is missing:
error: Microsoft Visual C++ 14.0 or greater is required
```

### 7. Environment Variables Required

#### Backend (.env)
```bash
ENVIRONMENT=prod
SNOWFLAKE_ACCOUNT=UHDECNO-CVB64222
SNOWFLAKE_USER=SCOOBYJAVA15
SNOWFLAKE_PASSWORD=[encrypted]
SNOWFLAKE_DATABASE=SOPHIA_AI_PRODUCTION
SNOWFLAKE_WAREHOUSE=SOPHIA_AI_COMPUTE_WH_MAIN
SNOWFLAKE_SCHEMA=PAYREADY_SALESIQ
REDIS_HOST=localhost
REDIS_PORT=6379
```

#### Frontend (Vercel Environment Variables)
```bash
VITE_API_URL=https://[backend-public-url]
VITE_APP_NAME=Sophia AI
VITE_ENVIRONMENT=production
```

### 8. DNS Configuration Needed for sophia-intel.ai

#### Namecheap DNS Settings Required
```
Type    Host    Value
A       @       76.76.21.21         (Vercel's IP)
CNAME   www     cname.vercel-dns.com
```

### 9. Lambda Labs Server Status

#### Current Process Status
```bash
# On 192.222.58.232
ps aux | grep python
# Shows: python /home/ubuntu/sophia-ai/backend/app/unified_chat_backend.py

# Port usage
sudo netstat -tlnp | grep 8001
# Shows: tcp 0.0.0.0:8001 LISTEN [python process]
```

### 10. GitHub Actions Workflow Considerations

#### Secrets Needed in GitHub
```yaml
LAMBDA_API_KEY
LAMBDA_SSH_KEY
SNOWFLAKE_PASSWORD
DOCKER_HUB_USERNAME
DOCKER_HUB_ACCESS_TOKEN
VERCEL_TOKEN
```

## Key Technical Decisions Needed

1. **Service Mesh**: Should we use Istio/Linkerd for K3s?
2. **Ingress Controller**: Traefik (K3s default) vs nginx-ingress?
3. **Certificate Management**: cert-manager vs Lambda Labs SSL?
4. **Service Discovery**: CoreDNS configuration for MCP servers?
5. **Storage**: Persistent volumes for MCP server state?
6. **Monitoring Stack**: Prometheus operator vs manual setup? 