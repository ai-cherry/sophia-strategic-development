# V2 MCP Deployment Manifest

**Deployment Date:** January 14, 2025
**Target Infrastructure:** Lambda Labs (192.222.58.232)
**Deployment Method:** Docker Swarm via GitHub Actions

## 🚀 10 V2 MCP Servers Being Deployed

### 1. AI Memory V2 (Port 9010)
- **Purpose:** Enhanced memory system with Redis L1 cache + Snowflake L2 persistence
- **Key Features:**
  - 5 memory types: Chat, Event, Insight, Context, Decision
  - Redis for sub-millisecond access
  - Snowflake for long-term storage with vector embeddings
  - Memory associations and semantic search
- **Tools:** `store_memory`, `recall_memory`, `search_memories`
- **Resources:** 2 CPU, 4GB RAM, 2 replicas

### 2. Gong V2 (Port 9011)
- **Purpose:** Call intelligence and conversation analysis
- **Key Features:**
  - Direct Gong API integration
  - Call transcript analysis with AI
  - Automatic insight extraction
  - Integration with AI Memory for persistence
- **Tools:** `get_calls`, `analyze_call`, `get_call_insights`
- **Resources:** 2 CPU, 4GB RAM, 2 replicas

### 3. Snowflake V2 (Port 9012)
- **Purpose:** Data warehouse operations with Cortex AI
- **Key Features:**
  - Snowflake Cortex AI integration
  - SQL query execution with AI enhancement
  - Automatic query optimization
  - Schema discovery and analysis
- **Tools:** `execute_query`, `get_tables`, `analyze_data`
- **Resources:** 2 CPU, 4GB RAM, 2 replicas

### 4. Slack V2 (Port 9013)
- **Purpose:** Slack conversation analysis and insights
- **Key Features:**
  - Real-time message analysis
  - Sentiment analysis
  - Decision tracking
  - Action item extraction
- **Tools:** `get_messages`, `analyze_sentiment`, `find_decisions`
- **Resources:** 2 CPU, 4GB RAM, 2 replicas

### 5. Notion V2 (Port 9014)
- **Purpose:** Knowledge management and documentation
- **Key Features:**
  - Page search and retrieval
  - Content creation and updates
  - Knowledge graph integration
  - Foundational knowledge support
- **Tools:** `search_pages`, `create_page`, `update_page`
- **Resources:** 2 CPU, 4GB RAM, 2 replicas

### 6. Linear V2 (Port 9015)
- **Purpose:** Project management and issue tracking
- **Key Features:**
  - Issue creation and updates
  - Project health monitoring
  - Team performance analytics
  - Sprint tracking
- **Tools:** `get_issues`, `create_issue`, `update_issue`
- **Resources:** 2 CPU, 4GB RAM, 2 replicas

### 7. GitHub V2 (Port 9016)
- **Purpose:** Repository and code management
- **Key Features:**
  - Repository analysis
  - Issue and PR management
  - Code search capabilities
  - Development metrics
- **Tools:** `get_repos`, `get_issues`, `create_pr`
- **Resources:** 2 CPU, 4GB RAM, 2 replicas

### 8. Codacy V2 (Port 9017)
- **Purpose:** Code quality and security analysis
- **Key Features:**
  - Real-time code analysis
  - Security vulnerability detection
  - Code complexity metrics
  - Sophia AI-specific patterns
- **Tools:** `analyze_code`, `get_issues`, `security_scan`
- **Resources:** 2 CPU, 4GB RAM, 2 replicas

### 9. Asana V2 (Port 9018)
- **Purpose:** Task and project management
- **Key Features:**
  - Task creation and tracking
  - Project timeline management
  - Team collaboration features
  - Workflow automation
- **Tools:** `get_tasks`, `create_task`, `update_task`
- **Resources:** 2 CPU, 4GB RAM, 2 replicas

### 10. Perplexity V2 (Port 9019)
- **Purpose:** AI-powered search and research
- **Key Features:**
  - Web search with AI analysis
  - Source verification
  - Topic deep-dives
  - Real-time information retrieval
- **Tools:** `search`, `get_sources`, `analyze_topic`
- **Resources:** 2 CPU, 4GB RAM, 2 replicas

## 🏗️ Supporting Infrastructure

### Redis Cache
- **Purpose:** L1 cache for AI Memory V2
- **Configuration:**
  - Single instance on manager node
  - Persistent volume with AOF
  - Used by AI Memory for fast access

### MCP Gateway
- **Purpose:** Unified routing to all MCP servers
- **Configuration:**
  - 3 replicas for high availability
  - Load balancing across servers
  - Health check monitoring
  - Traefik integration for external access

### Docker Networks
- **mcp-net:** Encrypted overlay network for MCP communication
- **monitoring:** External network for Prometheus/Grafana

## 📊 Monitoring Stack

### Prometheus
- Metrics collection from all services
- 30-day retention
- Service discovery via Docker labels

### Grafana
- Pre-configured dashboards for:
  - MCP server health
  - Performance metrics
  - Resource utilization
  - Business KPIs

### Loki + Promtail
- Log aggregation from all containers
- 7-day retention
- Searchable logs interface

### AlertManager
- Alerts for:
  - Service down > 2 minutes
  - High latency (p95 > 250ms)
  - Resource exhaustion
  - Error rate > 1%

## 🔒 Security & Secrets

### Docker Secrets (via Pulumi ESC)
- `snowflake_creds` - Snowflake authentication
- `openai_key` - OpenAI API access
- `gong_api_key` - Gong.io integration
- `slack_token` - Slack workspace access
- `notion_api_key` - Notion integration
- `linear_api_key` - Linear API access
- `github_token` - GitHub API access
- `codacy_api_token` - Codacy integration
- `asana_access_token` - Asana API access
- `perplexity_api_key` - Perplexity search

## 🌐 External Integrations

### Snowflake
- New warehouse: `SOPHIA_AI_V2_WH` (Medium)
- Schema: `SOPHIA_AI_PROD.MCP_V2`
- Roles and permissions via Pulumi

### Estuary Flow
- Data pipeline configurations
- Real-time CDC from source systems
- Automated data flows to Snowflake

### Vercel (Frontend)
- Updated environment variables
- MCP Gateway URL configuration
- V2 features enabled

## 📈 Performance Targets

- **Response Time:** p95 < 200ms
- **Availability:** 99.9% uptime
- **CPU Usage:** < 60% average
- **Memory Usage:** < 70% average
- **Error Rate:** < 0.1%

## 🔄 Deployment Configuration

- **Replicas:** 2 per service (20 containers total)
- **Update Strategy:** Rolling updates with 30s delay
- **Rollback:** Automatic on failure
- **Health Checks:** Every 30s with 3 retries
- **Resource Limits:** 2 CPU, 4GB RAM per container
- **Total Resources:** 40 CPUs, 80GB RAM allocated

This deployment represents a major upgrade to Sophia AI's capabilities, providing:
- Enhanced AI memory with multi-tier caching
- Comprehensive business tool integrations
- Real-time monitoring and alerting
- Enterprise-grade reliability and performance
- Unified access through MCP Gateway

All services are containerized, orchestrated via Docker Swarm, and deployed with zero downtime.
