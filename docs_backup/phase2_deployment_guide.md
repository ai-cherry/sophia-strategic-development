# Sophia AI Phase 2 Deployment Guide

## Overview

This guide provides comprehensive instructions for deploying the Phase 2 enhancements to the Sophia AI system. The deployment includes enhanced LangGraph orchestration, universal chat service, cost engineering, and enhanced Snowflake Cortex integration.

## Prerequisites

### Infrastructure Requirements

#### Compute Resources
- **Primary Instance**: Lambda Labs GPU instance (minimum 32GB RAM, 8 vCPUs)
- **Database**: PostgreSQL 14+ with vector extensions
- **Cache**: Redis 7+ with persistence enabled
- **Vector Stores**: Pinecone and Weaviate instances
- **AI Services**: Snowflake Cortex access with appropriate permissions

#### Software Dependencies
- **Python**: 3.11+ with pip
- **Node.js**: 20+ with npm/yarn
- **Docker**: Latest stable version
- **Git**: Latest version
- **Pulumi**: Latest CLI version

#### Access Requirements
- **GitHub**: Organization access with secrets management permissions
- **Snowflake**: Account with Cortex AI features enabled
- **Pulumi ESC**: Environment access for secret management
- **Cloud Provider**: AWS/GCP/Azure access for infrastructure deployment

### Environment Setup

#### 1. Clone Repository
```bash
git clone https://github.com/ai-cherry/sophia-main.git
cd sophia-main
```

#### 2. Install Dependencies
```bash
# Python dependencies
pip install -r requirements.txt

# Node.js dependencies (if applicable)
npm install

# Install additional Phase 2 dependencies
pip install -r backend/requirements-phase2.txt
```

#### 3. Environment Configuration
```bash
# Copy environment template
cp .env.example .env

# Configure environment variables
# (See Environment Variables section below)
```

## Environment Variables

### Core Configuration
```bash
# Application Settings
SOPHIA_ENV=production
SOPHIA_VERSION=2.0.0
DEBUG=false
LOG_LEVEL=INFO

# Database Configuration
DATABASE_URL=postgresql://user:password@host:port/database
REDIS_URL=redis://host:port/database

# Vector Store Configuration
PINECONE_API_KEY=${PINECONE_API_KEY}
PINECONE_ENVIRONMENT=${PINECONE_ENVIRONMENT}
WEAVIATE_URL=${WEAVIATE_URL}
WEAVIATE_API_KEY=${WEAVIATE_API_KEY}

# Snowflake Configuration
SNOWFLAKE_ACCOUNT=${SNOWFLAKE_ACCOUNT}
SNOWFLAKE_USER=PROGRAMMATIC_SERVICE_USER
SNOWFLAKE_PASSWORD=${SOPHIA_AI_TOKEN}
SNOWFLAKE_WAREHOUSE=${SNOWFLAKE_WAREHOUSE}
SNOWFLAKE_DATABASE=${SNOWFLAKE_DATABASE}
SNOWFLAKE_SCHEMA=${SNOWFLAKE_SCHEMA}

# AI Service Configuration
OPENAI_API_KEY=${OPENAI_API_KEY}
ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
TOGETHER_AI_API_KEY=${TOGETHER_AI_API_KEY}

# Security Configuration
SECRET_KEY=${SECRET_KEY}
JWT_SECRET=${JWT_SECRET}
ENCRYPTION_KEY=${ENCRYPTION_KEY}

# Monitoring Configuration
ARIZE_SPACE_ID=${ARIZE_SPACE_ID}
ARIZE_API_KEY=${ARIZE_API_KEY}
```

### Phase 2 Specific Configuration
```bash
# Enhanced LangGraph Configuration
LANGGRAPH_MAX_PARALLEL_TASKS=10
LANGGRAPH_CHECKPOINT_TIMEOUT=1800
LANGGRAPH_WORKFLOW_TTL=86400

# Universal Chat Configuration
CHAT_SESSION_TTL=3600
CHAT_MAX_CONTEXT_LENGTH=10000
CHAT_INTENT_CONFIDENCE_THRESHOLD=0.8

# Cost Engineering Configuration
COST_OPTIMIZATION_STRATEGY=balanced
COST_BUDGET_DAILY=100.00
COST_BUDGET_MONTHLY=3000.00
COST_CACHE_TTL=86400

# Enhanced Cortex Configuration
CORTEX_SEARCH_SIMILARITY_THRESHOLD=0.7
CORTEX_PIPELINE_BATCH_SIZE=1000
CORTEX_QUALITY_CHECK_ENABLED=true
```

## Deployment Steps

### Step 1: Infrastructure Deployment

#### Using Pulumi (Recommended)
```bash
# Navigate to infrastructure directory
cd infrastructure

# Initialize Pulumi stack
pulumi stack init sophia-prod-phase2

# Configure Pulumi ESC environment
pulumi config set-all --path sophia-prod-phase2.yaml

# Deploy infrastructure
pulumi up
```

#### Manual Infrastructure Setup
If not using Pulumi, manually provision:
1. Database instances (PostgreSQL, Redis)
2. Vector store services (Pinecone, Weaviate)
3. Compute instances with GPU support
4. Load balancers and networking
5. Monitoring and logging services

### Step 2: Database Setup

#### PostgreSQL Setup
```sql
-- Create database and extensions
CREATE DATABASE sophia_ai_phase2;
\c sophia_ai_phase2;

-- Install required extensions
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS btree_gin;

-- Run migration scripts
\i backend/database/migrations/phase2_schema.sql
```

#### Redis Setup
```bash
# Configure Redis for persistence
redis-cli CONFIG SET save "900 1 300 10 60 10000"
redis-cli CONFIG SET appendonly yes
redis-cli CONFIG REWRITE
```

### Step 3: Application Deployment

#### Backend Services
```bash
# Deploy enhanced LangGraph orchestration
python -m backend.workflows.enhanced_langgraph_orchestration &

# Deploy universal chat service
python -m backend.services.sophia_universal_chat_service &

# Deploy cost engineering service
python -m backend.services.cost_engineering_service &

# Deploy enhanced Cortex service
python -m backend.services.enhanced_snowflake_cortex_service &

# Deploy main application
python -m backend.app.main
```

#### Using Docker (Recommended)
```bash
# Build Phase 2 image
docker build -t sophia-ai:phase2 -f Dockerfile.phase2 .

# Run with docker-compose
docker-compose -f docker-compose.phase2.yml up -d
```

#### Using Kubernetes
```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/phase2/

# Verify deployment
kubectl get pods -n sophia-ai
kubectl get services -n sophia-ai
```

### Step 4: Service Configuration

#### Snowflake Cortex Setup
```sql
-- Create custom AI functions
CREATE OR REPLACE FUNCTION SOPHIA_AI_SUMMARIZE(text STRING, max_length INT)
RETURNS STRING
LANGUAGE SQL
AS
$$
    SELECT SNOWFLAKE.CORTEX.SUMMARIZE(text, max_length)
$$;

-- Create Cortex Search services
CREATE CORTEX SEARCH SERVICE sophia_knowledge_base
ON content, metadata
ATTRIBUTES source, category, timestamp
WAREHOUSE = SOPHIA_WAREHOUSE
TARGET_LAG = '1 minute'
AS (
    SELECT content, metadata, source, category, timestamp
    FROM knowledge_base
);
```

#### Vector Store Initialization
```python
# Initialize Pinecone indexes
import pinecone

pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_ENVIRONMENT)

# Create indexes for Phase 2
pinecone.create_index(
    name="sophia-workflows",
    dimension=1536,
    metric="cosine"
)

pinecone.create_index(
    name="sophia-conversations",
    dimension=1536,
    metric="cosine"
)
```

### Step 5: Testing and Validation

#### Health Checks
```bash
# Check service health
curl http://localhost:8000/health
curl http://localhost:8000/api/v2/health

# Check database connectivity
python -c "from backend.core.database import test_connection; test_connection()"

# Check AI service connectivity
python -c "from backend.utils.snowflake_cortex_service import test_cortex; test_cortex()"
```

#### Integration Tests
```bash
# Run Phase 2 integration tests
pytest tests/test_phase2_integration.py -v

# Run performance tests
pytest tests/test_phase2_performance.py -v

# Run security tests
pytest tests/test_phase2_security.py -v
```

#### Functional Validation
```bash
# Test workflow creation via chat
curl -X POST http://localhost:8000/api/v2/chat/message \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "session_id": "test_session",
    "message": "Create a workflow to analyze customer feedback"
  }'

# Test cost engineering
curl -X POST http://localhost:8000/api/v2/cost/task \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "analysis",
    "prompt": "Analyze this data",
    "user_id": "test_user"
  }'
```

## Configuration Management

### Pulumi ESC Integration

#### Environment Configuration
```yaml
# pulumi/environments/sophia-prod-phase2.yaml
values:
  sophia:
    database:
      url: ${DATABASE_URL}
      pool_size: 20
      max_overflow: 30
    
    ai_services:
      snowflake:
        account: ${SNOWFLAKE_ACCOUNT}
        user: PROGRAMMATIC_SERVICE_USER
        password: ${SOPHIA_AI_TOKEN}
      
    cost_engineering:
      strategy: balanced
      daily_budget: 100.00
      monthly_budget: 3000.00
    
    monitoring:
      arize:
        space_id: ${ARIZE_SPACE_ID}
        api_key: ${ARIZE_API_KEY}
```

#### Secret Management
```bash
# Set secrets in Pulumi ESC
pulumi env set sophia-prod-phase2 --secret DATABASE_URL "postgresql://..."
pulumi env set sophia-prod-phase2 --secret SOPHIA_AI_TOKEN "eyJraWQi..."
pulumi env set sophia-prod-phase2 --secret SECRET_KEY "your-secret-key"
```

### GitHub Secrets Integration
```bash
# Required GitHub Organization Secrets
SNOWFLAKE_ACCOUNT
SOPHIA_AI_TOKEN
DATABASE_URL
REDIS_URL
PINECONE_API_KEY
WEAVIATE_API_KEY
SECRET_KEY
JWT_SECRET
ARIZE_SPACE_ID
ARIZE_API_KEY
```

## Monitoring and Observability

### Application Monitoring
```python
# Configure monitoring endpoints
from backend.core.monitoring import setup_monitoring

setup_monitoring(
    arize_space_id=ARIZE_SPACE_ID,
    arize_api_key=ARIZE_API_KEY,
    enable_performance_tracking=True,
    enable_cost_tracking=True
)
```

### Logging Configuration
```python
# Configure structured logging
import logging
from backend.core.logger import setup_logging

setup_logging(
    level=LOG_LEVEL,
    format="json",
    include_trace_id=True,
    enable_audit_logging=True
)
```

### Metrics Collection
```bash
# Prometheus metrics endpoint
curl http://localhost:8000/metrics

# Custom Phase 2 metrics
curl http://localhost:8000/api/v2/metrics/workflows
curl http://localhost:8000/api/v2/metrics/cost
curl http://localhost:8000/api/v2/metrics/chat
```

## Security Configuration

### Authentication Setup
```python
# Configure RBAC
from backend.security.rbac import setup_rbac

setup_rbac(
    enable_role_based_access=True,
    default_role="user",
    admin_users=["admin@company.com"]
)
```

### Audit Logging
```python
# Enable comprehensive audit logging
from backend.security.audit_logger import setup_audit_logging

setup_audit_logging(
    log_all_operations=True,
    log_ai_operations=True,
    log_data_access=True,
    retention_days=90
)
```

### Encryption Configuration
```python
# Configure encryption for sensitive data
from backend.security.encryption import setup_encryption

setup_encryption(
    encryption_key=ENCRYPTION_KEY,
    encrypt_at_rest=True,
    encrypt_in_transit=True
)
```

## Performance Optimization

### Database Optimization
```sql
-- Create indexes for Phase 2 tables
CREATE INDEX CONCURRENTLY idx_workflows_user_id ON workflows(user_id);
CREATE INDEX CONCURRENTLY idx_chat_sessions_user_id ON chat_sessions(user_id);
CREATE INDEX CONCURRENTLY idx_cost_metrics_user_id ON cost_metrics(user_id);

-- Configure connection pooling
ALTER SYSTEM SET max_connections = 200;
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
```

### Cache Configuration
```python
# Configure Redis for optimal performance
redis_config = {
    'maxmemory': '2gb',
    'maxmemory-policy': 'allkeys-lru',
    'timeout': 300,
    'tcp-keepalive': 60
}
```

### AI Service Optimization
```python
# Configure model routing for optimal performance
cost_engineering_config = {
    'model_selection_strategy': 'balanced',
    'cache_similarity_threshold': 0.85,
    'parallel_processing_limit': 10,
    'timeout_seconds': 30
}
```

## Troubleshooting

### Common Issues

#### Service Startup Failures
```bash
# Check logs
docker logs sophia-ai-phase2
kubectl logs -f deployment/sophia-ai -n sophia-ai

# Check dependencies
python -c "import backend.workflows.enhanced_langgraph_orchestration"
python -c "import backend.services.sophia_universal_chat_service"
```

#### Database Connection Issues
```bash
# Test database connectivity
psql $DATABASE_URL -c "SELECT 1;"
redis-cli -u $REDIS_URL ping

# Check connection pool status
curl http://localhost:8000/api/v2/health/database
```

#### AI Service Issues
```bash
# Test Snowflake Cortex connectivity
python -c "
from backend.utils.snowflake_cortex_service import SnowflakeCortexService
service = SnowflakeCortexService()
print(service.test_connection())
"

# Check model availability
curl http://localhost:8000/api/v2/models/available
```

### Performance Issues
```bash
# Monitor resource usage
docker stats sophia-ai-phase2
kubectl top pods -n sophia-ai

# Check cache hit rates
curl http://localhost:8000/api/v2/metrics/cache

# Monitor cost metrics
curl http://localhost:8000/api/v2/cost/report
```

### Debug Mode
```bash
# Enable debug mode
export DEBUG=true
export LOG_LEVEL=DEBUG

# Restart services with debug logging
docker-compose -f docker-compose.phase2.yml restart
```

## Rollback Procedures

### Application Rollback
```bash
# Rollback to previous version
docker tag sophia-ai:phase1 sophia-ai:current
docker-compose -f docker-compose.yml up -d

# Or using Kubernetes
kubectl rollout undo deployment/sophia-ai -n sophia-ai
```

### Database Rollback
```sql
-- Rollback database schema
\i backend/database/migrations/rollback_phase2.sql

-- Restore from backup if needed
pg_restore -d sophia_ai_phase2 backup_pre_phase2.dump
```

### Configuration Rollback
```bash
# Revert Pulumi stack
pulumi stack select sophia-prod-phase1
pulumi up

# Revert environment variables
cp .env.phase1 .env
```

## Maintenance

### Regular Maintenance Tasks
```bash
# Database maintenance
psql $DATABASE_URL -c "VACUUM ANALYZE;"
psql $DATABASE_URL -c "REINDEX DATABASE sophia_ai_phase2;"

# Cache cleanup
redis-cli FLUSHDB

# Log rotation
logrotate /etc/logrotate.d/sophia-ai
```

### Backup Procedures
```bash
# Database backup
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d_%H%M%S).sql

# Configuration backup
tar -czf config_backup_$(date +%Y%m%d).tar.gz .env pulumi/

# Application backup
docker save sophia-ai:phase2 | gzip > sophia-ai-phase2_$(date +%Y%m%d).tar.gz
```

### Update Procedures
```bash
# Update application
git pull origin main
docker build -t sophia-ai:phase2-latest .
docker-compose -f docker-compose.phase2.yml up -d

# Update dependencies
pip install -r requirements.txt --upgrade
npm update
```

## Support and Documentation

### Additional Resources
- **API Documentation**: `/docs/api/phase2/`
- **Architecture Guide**: `/docs/architecture/phase2/`
- **User Manual**: `/docs/user-guide/phase2/`
- **Troubleshooting Guide**: `/docs/troubleshooting/phase2/`

### Support Contacts
- **Technical Support**: tech-support@sophia-ai.com
- **Emergency Contact**: emergency@sophia-ai.com
- **Documentation Issues**: docs@sophia-ai.com

---

*This deployment guide provides comprehensive instructions for Phase 2 deployment. For specific environment configurations or custom requirements, please consult the technical team or refer to the detailed architecture documentation.*

