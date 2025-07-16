# Sophia AI Deployment - Comprehensive Technical Summary & Troubleshooting Prompt

## Project Overview
I'm deploying Sophia AI, an executive intelligence assistant platform with multi-agent orchestration capabilities. The system consists of a React/TypeScript frontend, Python FastAPI backend, multiple MCP (Model Context Protocol) servers, and integrations with Modern Stack, various business tools, and AI services.

## Deployment Goals
1. **MCP Servers**: Deploy all MCP servers on Lambda Labs server at IP 104.171.202.117 (sophia-mcp-orchestrator)
2. **Frontend**: Deploy frontend on Lambda Labs serverless infrastructure with custom domain sophia-intel.ai
3. **Backend**: Deploy backend API on Lambda Labs with proper connectivity
4. **Kubernetes-Centric**: Use K3s (lightweight Kubernetes) for orchestration
5. **Automation**: Enable Cursor AI to use provided API keys to automate entire deployment

## Available Infrastructure

### Lambda Labs Servers
- **sophia-production-instance**: 104.171.202.103 (main production server)
- **sophia-ai-core**: 192.222.58.232 (AI core services)
- **sophia-mcp-orchestrator**: 104.171.202.117 (dedicated MCP server deployment target)
- **SSH Access**: Available via ~/.ssh/sophia_correct_key for all servers
- **OS**: Ubuntu on all servers

### API Keys & Credentials Available
1. **Lambda Labs API Keys**:
   - Cloud API: `secret_sophiacloudapi_17cf7f3cedca48f18b4b8ea46cbb258f.EsLXt0lkGlhZ1Nd369Ld5DMSuhJg9O9y`
   - Instance API: `secret_sophia5apikey_a404a99d985d41828d7020f0b9a122a2.PjbWZb0lLubKu1nmyWYLy9Ycl3vyL18o`
   - Endpoint: https://cloud.lambda.ai/api/v1/instances

2. **Modern Stack Credentials**:
   - Account: UHDECNO-CVB64222
   - User: SCOOBYJAVA15
   - Database: SOPHIA_AI_PRODUCTION
   - Warehouse: SOPHIA_AI_COMPUTE_WH_MAIN
   - Schema: PAYREADY_SALESIQ
   - Authentication: Password/PAT token based

3. **Lambda Labs**: Pro account under lynn-musils-projects
4. **Namecheap**: Domain sophia-intel.ai registered and ready for DNS configuration

## Tech Stack

### Frontend
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **UI**: Custom glassmorphism design with executive dashboard
- **State Management**: React Context API
- **Styling**: TailwindCSS
- **Components**: UnifiedChatDashboard, ExecutiveKPICard, various dashboard components
- **Environment Variables**: VITE_API_URL (critical for backend connection)

### Backend
- **Framework**: FastAPI (Python 3.12)
- **File**: backend/app/unified_chat_backend.py
- **Port**: 8001
- **Features**: 
  - Unified chat orchestration
  - Modern Stack integration
  - Multi-agent coordination
  - WebSocket support
  - Health endpoints
  - API documentation at /docs

### MCP Servers (Model Context Protocol)
- **ai_memory**: Port 9001 - Memory and context management
- **codacy**: Port 3008 - Code quality analysis
- **github**: Port 9003 - GitHub integration
- **linear**: Port 9004 - Project management
- **asana**: Port 9006 - Task management
- **notion**: Port 9102 - Knowledge base
- **slack**: Port 9101 - Team communication
- **Architecture**: StandardizedMCPServer base class pattern

### Database & Storage
- **Primary**: Modern Stack (L3/L4/L5 in unified memory architecture)
- **Cache**: Redis (L1 layer)
- **Vector Search**: Lambda GPU AI (replacing Pinecone/Qdrant)
- **Memory Service**: UnifiedMemoryService handling all memory operations

### Infrastructure & Deployment
- **Container**: Docker with multi-stage builds
- **Orchestration**: K3s (lightweight Kubernetes)
- **CI/CD**: GitHub Actions
- **Secrets**: Pulumi ESC for secret management
- **Monitoring**: Prometheus + Grafana
- **Current Deployment**: Mix of Lambda Labs (frontend) and local/ngrok (backend)

## Current Issues & Blockers

### 1. Frontend-Backend Connection Issues
- **Problem**: Frontend shows "Failed to process your request" when trying to communicate with backend
- **Root Cause**: VITE_API_URL environment variable not properly set in Lambda Labs deployment
- **Symptoms**: 
  - Chat interface loads but can't send messages
  - System status shows as undefined causing `toUpperCase()` errors
  - Mock data appears instead of real data

### 2. Blank Screen Issues
- **Problem**: Occasionally frontend shows completely blank screen
- **Attempted Fixes**:
  - Added error boundaries
  - Fixed import paths
  - Added loading states
  - Implemented fallback UI
- **Status**: Partially resolved but still occurs intermittently

### 3. Environment Variable Configuration
- **Problem**: Complex environment variable setup across local, Lambda Labs, and Lambda Labs
- **Specific Issues**:
  - VITE_API_URL not persisting in Lambda Labs deployments
  - Modern Stack credentials not loading correctly ("User is empty" errors)
  - Different variable prefixes (REACT_APP_ vs VITE_) causing confusion

### 4. MCP Server Deployment
- **Problem**: MCP servers not successfully deployed to Lambda Labs
- **Issues**:
  - Missing build dependencies (g++ compiler)
  - asyncpg build failures
  - Port conflicts and networking issues
  - File path mismatches

### 5. Kubernetes Migration
- **Status**: PR #184 merged with K3s configurations but not fully implemented
- **Challenges**:
  - Need to deploy K3s cluster on Lambda Labs
  - Convert Docker deployments to K8s manifests
  - Set up proper ingress and service discovery

## Deployment Attempts Summary

### Successful Elements:
- Frontend deploys to Lambda Labs successfully
- Backend runs locally on port 8001
- Modern Stack connection works when environment is configured correctly
- SSH access to all Lambda Labs servers confirmed
- ngrok tunnel successfully exposes local backend

### Failed Attempts:
1. **Direct Docker deployment to Lambda Labs**: Build failures, port conflicts
2. **K3s deployment**: Not yet attempted due to setup complexity
3. **MCP server deployment**: Missing dependencies, build failures
4. **Frontend-backend connection**: Environment variable issues

## Desired End State

1. **MCP Servers**: All 7 MCP servers running on 104.171.202.117 in K3s pods
2. **Backend API**: Running on Lambda Labs with public endpoint
3. **Frontend**: Deployed on Lambda Labs with sophia-intel.ai domain pointing to it
4. **Data Flow**: Frontend → Backend API → MCP Servers → Modern Stack/Redis
5. **Monitoring**: Full observability with Prometheus/Grafana
6. **Automation**: GitHub Actions deploying on push to main

## Key Questions for Troubleshooting

1. Should we use K3s on Lambda Labs or stick with Docker Compose initially?
2. How can we ensure VITE_API_URL persists in Lambda Labs deployments?
3. What's the best way to expose backend API (nginx, Traefik, ngrok permanent)?
4. Should MCP servers be containerized individually or as a monolithic service?
5. How to handle Modern Stack authentication in production (PAT token vs password)?
6. Best practice for managing secrets across Lambda Labs, Lambda Labs, and GitHub Actions?

## Deployment Script Requirements

The deployment automation should:
1. Use provided API keys to provision/configure Lambda Labs resources
2. Set up K3s cluster on designated servers
3. Deploy all services with proper networking
4. Configure DNS for sophia-intel.ai
5. Set up SSL certificates
6. Ensure zero-downtime deployments
7. Provide rollback capabilities

Please help me create a robust, production-ready deployment strategy that addresses these issues and achieves our Kubernetes-centric deployment goals. 