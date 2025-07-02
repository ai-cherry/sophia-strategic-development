# GitHub Organization Secrets Mapping

## Discovered Secrets (ai-cherry organization)

### Core Infrastructure & Authentication
- `AGNO_API_KEY` - 2 months ago
- `ANTHROPIC_API_KEY` - 2 months ago
- `API_SECRET_KEY` - last month
- `BACKUP_ENCRYPTION_KEY` - last month
- `ENCRYPTION_KEY` - last month

### Data Pipeline & ETL
- `ESTUARY_ACCESS_TOKEN` - 4 days ago
- `ESTUARY_CLIENT_ID` - last week
- `ESTUARY_CLIENT_SECRET` - last week
- `ESTUARY_ACCESS_TOKEN` - 2 weeks ago ✅ FOUND
- `ESTUARY_REFRESH_TOKEN` - 4 days ago ✅ FOUND

### Conversation Intelligence
- `GONG_ACCESS_KEY` - last week ✅ FOUND

### Database & Infrastructure
- `DATABASE_HOST` - last month
- `DATABASE_SSH_KEY` - last month
- `DATABASE_URL` - last month

### Development & CI/CD
- `GH_API_TOKEN` - 4 months ago
- `GH_CLASSIC_PAT_TOKEN` - 2 months ago
- `GH_FINE_GRAINED_TOKEN` - 2 months ago
- `GH_IP_ADDRESS` - last week

### Docker & Containerization
- `DOCKERHUB_USERNAME` - 2 months ago
- `DOCKER_PERSONAL_ACCESS_TOKEN` - last week
- `DOCKER_TOKEN` - 4 months ago
- `DOCKER_USER_NAME` - last week

### AI & ML Services
- `CODESTRAL_API_KEY` - 3 months ago
- `CODESTRAL_ORG_ID` - 3 months ago
- `CODESTRAL_ORG_NAME` - 3 months ago
- `COHERE_API_KEY` - last week
- `COHERE_VIRTUAL_KEY` - last week
- `CONTINUE_API_KEY` - 3 months ago
- `DEEPSEEK_API_KEY` - 2 months ago
- `ELEVENLABS_API_KEY` - last month
- `ELEVEN_LABS_API_KEY` - 2 weeks ago

### Other Services
- `APIFY_API_TOKEN` - last week
- `APOLLO_API_KEY` - 3 months ago
- `ARIZE_API_KEY` - last week
- `ARIZE_SPACE_ID` - last week
- `ASANA_API_TOKEN` - last week
- `BARDEEN_ID` - 2 weeks ago
- `BRAVE_API_KEY` - 4 months ago
- `BROWSER_USE_API_KEY` - 2 months ago
- `CODACY_API_TOKEN` - 5 days ago
- `CREW_API_TOKEN` - 2 weeks ago
- `EDEN_API_KEY` - 3 months ago
- `EXA_API_KEY` - 4 months ago
- `FIGMA_PAT` - 3 months ago
- `FIGMA_PROJECT_ID` - 3 months ago

## Missing Secrets (Need to Continue Scrolling)
- `HUBSPOT_*` secrets (not found yet)
- `LAMBDA_LABS_*` secrets (not found yet)
- `SNOWFLAKE_*` secrets (not found yet)
- `GONG_ACCESS_KEY_SECRET` (companion to GONG_ACCESS_KEY)

## Mapping Strategy
1. Continue scrolling to find all relevant secrets
2. Map existing secret names to infrastructure implementation
3. Update Pulumi ESC configurations with correct secret references
4. Align GitHub Actions workflows with existing secret names



## Additional Discovered Secrets

### Gong Integration (COMPLETE SET FOUND) ✅
- `GONG_ACCESS_KEY` - last week ✅ FOUND
- `GONG_ACCESS_KEY_SECRET` - last week ✅ FOUND
- `GONG_BASE_URL` - 2 weeks ago ✅ FOUND
- `GONG_CLIENT_ACCESS_KEY` - 2 weeks ago ✅ FOUND
- `GONG_CLIENT_SECRET` - 2 weeks ago ✅ FOUND

### HubSpot Integration (COMPLETE SET FOUND) ✅
- `HUBSPOT_ACCESS_TOKEN` - 3 months ago ✅ FOUND
- `HUBSPOT_CLIENT_SECRET` - 3 months ago ✅ FOUND

### Lambda Labs Infrastructure (COMPLETE SET FOUND) ✅
- `LAMBDA_API_KEY` - last month ✅ FOUND
- `LAMBDA_IP_ADDRESS` - last week ✅ FOUND
- `LAMBDA_SSH_PRIVATE_KEY` - last week ✅ FOUND

### Monitoring & Infrastructure
- `GRAFANA_PASSWORD` - last month
- `GRAFANA_URL` - last month
- `GRAFANA_USERNAME` - last month
- `KIBANA_URL` - last month
- `LOAD_BALANCER_HOST` - last month

### Kubernetes & Container Orchestration
- `KUBERNETES_CLUSTER_ID` - last month
- `KUBERNETES_NAMESPACE` - last month
- `KONG_ACCESS_TOKEN` - 2 weeks ago
- `KONG_ORG_ID` - 2 weeks ago

### Additional AI/ML Services
- `GROQ_API_KEY` - last week
- `GROQ_VIRTUAL_KEY` - last week
- `HUGGINGFACE_API_TOKEN` - last week
- `LANGCHAIN_API_KEY` - 2 months ago
- `LANGSMITH_API_KEY` - 4 months ago
- `LANGSMITH_ORG_ID` - 4 months ago
- `LLAMA_API_KEY` - 2 weeks ago
- `MISTRAL_API_KEY` - last week
- `MISTRAL_VIRTUAL_KEY` - last week

### Development Tools
- `LINEAR_API_KEY` - 2 weeks ago
- `NOTION_API_KEY` - 3 weeks ago
- `N8N_API_KEY` - 2 months ago
- `NPM_API_TOKEN` - 4 months ago

### Infrastructure & Networking
- `NAMECHEAP_API_KEY` - last week
- `NAMECHEAP_USERNAME` - last week
- `NGROK_AUTHTOKEN` - 4 months ago
- `NORDVPN_PASSWORD` - 4 months ago
- `NORDVPN_USERNAME` - 4 months ago

### Security & Authentication
- `JWT_SECRET` - last month

### Other Services
- `LATTICE_API_KEY` - 3 months ago
- `MIDJOURNEY_ID` - last month
- `MUREKA_API_KEY` - last month

## CRITICAL FINDINGS ✅

### ALL REQUIRED SECRETS FOUND:
1. **Estuary Flow**: `ESTUARY_ACCESS_TOKEN`, `ESTUARY_REFRESH_TOKEN`
2. **Gong**: Complete set of 5 secrets including access key and secret
3. **HubSpot**: `HUBSPOT_ACCESS_TOKEN`, `HUBSPOT_CLIENT_SECRET`
4. **Lambda Labs**: `LAMBDA_API_KEY`, `LAMBDA_IP_ADDRESS`, `LAMBDA_SSH_PRIVATE_KEY`

### MISSING SECRETS (Need to check if they exist):
- `SNOWFLAKE_*` secrets (continue scrolling to verify)
- `VERCEL_*` secrets (for deployment)
- `PULUMI_*` secrets (for ESC integration)

## NEXT STEPS:
1. Continue scrolling to find any remaining secrets
2. Map all found secrets to infrastructure code
3. Update Pulumi ESC configurations with correct secret names
4. Align GitHub Actions workflows with existing secret names

