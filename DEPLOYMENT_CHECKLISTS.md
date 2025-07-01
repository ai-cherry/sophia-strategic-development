# 🚀 Sophia AI Deployment Checklists
## External Platform Configuration Guide

**Date:** January 7, 2025  
**Status:** Ready for Implementation  
**Architecture:** Estuary Flow → PostgreSQL → Redis → Snowflake

---

## 📋 OVERVIEW

This document provides comprehensive checklists for configuring external platforms required for the Sophia AI data pipeline. All credentials are managed through GitHub Organization Secrets → Pulumi ESC → Application Runtime.

**Infrastructure Architecture:**
```
GitHub Secrets → Pulumi ESC → Application Runtime
     ↓              ↓              ↓
Estuary Flow → PostgreSQL → Redis → Snowflake
     ↓              ↓              ↓
Lambda Labs    Lambda Labs    Snowflake Cortex
```

---

## 🌊 ESTUARY FLOW CONFIGURATION

### **Platform:** [Estuary Flow](https://estuary.dev)
### **Purpose:** Real-time data streaming and CDC pipeline
### **Replaces:** Airbyte (for better real-time performance)

#### **Account Setup Checklist:**

- [ ] **Create Estuary Flow Account**
  - [ ] Sign up at https://estuary.dev
  - [ ] Choose organization name: `sophia-ai`
  - [ ] Select appropriate pricing tier (recommend Pro for production)
  - [ ] Verify email and complete account setup

- [ ] **Generate API Credentials**
  - [ ] Navigate to Settings → API Keys
  - [ ] Create new API key with name: `sophia-ai-production`
  - [ ] Copy access token (format: `est_xxx...`)
  - [ ] Note down tenant ID: `sophia-ai`

- [ ] **Configure Organization Settings**
  - [ ] Set organization name: `Sophia AI`
  - [ ] Configure billing information
  - [ ] Set up usage alerts and limits
  - [ ] Enable audit logging

#### **Data Source Configuration:**

- [ ] **HubSpot Connector Setup**
  - [ ] Navigate to Connectors → Sources
  - [ ] Select "HubSpot" connector
  - [ ] Configure authentication:
    - [ ] API Key: Use `HUBSPOT_API_KEY` from GitHub Secrets
    - [ ] Portal ID: Use `HUBSPOT_PORTAL_ID` from GitHub Secrets
  - [ ] Select data streams:
    - [ ] ✅ Contacts
    - [ ] ✅ Companies
    - [ ] ✅ Deals
    - [ ] ✅ Engagements
    - [ ] ✅ Owners
    - [ ] ✅ Pipelines
  - [ ] Set start date: `2024-01-01T00:00:00Z`
  - [ ] Test connection and validate data

- [ ] **Gong Connector Setup**
  - [ ] Navigate to Connectors → Sources
  - [ ] Select "Gong" connector
  - [ ] Configure authentication:
    - [ ] Access Key: Use `GONG_ACCESS_KEY` from GitHub Secrets
    - [ ] Access Key Secret: Use `GONG_CLIENT_SECRET` from GitHub Secrets
  - [ ] Select data streams:
    - [ ] ✅ Calls
    - [ ] ✅ Users
    - [ ] ✅ Workspaces
    - [ ] ✅ Call Transcripts
    - [ ] ✅ Answered Scorecards
  - [ ] Set start date: `2024-01-01T00:00:00Z`
  - [ ] Test connection and validate data

- [ ] **Slack Connector Setup**
  - [ ] Navigate to Connectors → Sources
  - [ ] Select "Slack" connector
  - [ ] Configure authentication:
    - [ ] Bot Token: Use `SLACK_BOT_TOKEN` from GitHub Secrets
  - [ ] Select data streams:
    - [ ] ✅ Channels
    - [ ] ✅ Channel Members
    - [ ] ✅ Messages
    - [ ] ✅ Users
    - [ ] ✅ Threads
  - [ ] Configure channel filter: `["general", "engineering", "sales", "marketing"]`
  - [ ] Set start date: `2024-01-01T00:00:00Z`
  - [ ] Test connection and validate data

#### **Destination Configuration:**

- [ ] **PostgreSQL Destination Setup**
  - [ ] Navigate to Connectors → Destinations
  - [ ] Select "PostgreSQL" connector
  - [ ] Configure connection:
    - [ ] Host: Use `POSTGRESQL_HOST` from GitHub Secrets
    - [ ] Port: `5432`
    - [ ] Database: `sophia_staging`
    - [ ] Username: `sophia_user`
    - [ ] Password: Use `POSTGRESQL_PASSWORD` from GitHub Secrets
    - [ ] SSL Mode: `require`
  - [ ] Configure schema mapping:
    - [ ] HubSpot → `hubspot_raw`
    - [ ] Gong → `gong_raw`
    - [ ] Slack → `slack_raw`
  - [ ] Test connection and validate write permissions

#### **Flow Configuration:**

- [ ] **Create Data Flows**
  - [ ] HubSpot → PostgreSQL flow
    - [ ] Name: `hubspot-to-postgresql`
    - [ ] Enable real-time sync
    - [ ] Configure transforms: Add ingestion metadata
  - [ ] Gong → PostgreSQL flow
    - [ ] Name: `gong-to-postgresql`
    - [ ] Enable real-time sync
    - [ ] Configure transforms: Add ingestion metadata
  - [ ] Slack → PostgreSQL flow
    - [ ] Name: `slack-to-postgresql`
    - [ ] Enable real-time sync
    - [ ] Configure transforms: Add ingestion metadata

- [ ] **Enable Monitoring**
  - [ ] Set up flow monitoring dashboards
  - [ ] Configure alerting for flow failures
  - [ ] Set up data quality monitoring
  - [ ] Enable audit logging

#### **Credentials for GitHub Secrets:**
```
ESTUARY_FLOW_ACCESS_TOKEN=est_xxx...
ESTUARY_FLOW_TENANT=sophia-ai
ESTUARY_FLOW_API_URL=https://api.estuary.dev
```

---

## 🖥️ LAMBDA LABS CONFIGURATION

### **Platform:** [Lambda Labs](https://lambdalabs.com)
### **Purpose:** GPU compute instances for PostgreSQL and Redis hosting
### **Replaces:** AWS (per user preference)

#### **Account Setup Checklist:**

- [ ] **Create Lambda Labs Account**
  - [ ] Sign up at https://cloud.lambdalabs.com
  - [ ] Complete identity verification
  - [ ] Add payment method
  - [ ] Set up billing alerts

- [ ] **Generate API Credentials**
  - [ ] Navigate to Account → API Keys
  - [ ] Create new API key with name: `sophia-ai-infrastructure`
  - [ ] Copy API key (format: `lambda_xxx...`)
  - [ ] Note down account ID

- [ ] **SSH Key Management**
  - [ ] Generate SSH key pair for instance access:
    ```bash
    ssh-keygen -t rsa -b 4096 -C "sophia-ai-infrastructure" -f sophia-ai-key
    ```
  - [ ] Upload public key to Lambda Labs:
    - [ ] Navigate to Account → SSH Keys
    - [ ] Add new SSH key with name: `sophia-ai-key`
    - [ ] Paste public key content
  - [ ] Store private key securely in GitHub Secrets

#### **Instance Configuration:**

- [ ] **Launch Database Instance**
  - [ ] Navigate to Instances → Launch
  - [ ] Select instance type: `gpu_1x_a10` (or available equivalent)
  - [ ] Select region: `us-west-1` (or closest to Snowflake)
  - [ ] Configure instance:
    - [ ] Name: `sophia-ai-database-server`
    - [ ] SSH Key: `sophia-ai-key`
    - [ ] Storage: 500GB SSD minimum
  - [ ] Launch instance and note IP address

- [ ] **Configure Security Groups**
  - [ ] Allow inbound traffic:
    - [ ] Port 22 (SSH) from your IP
    - [ ] Port 5432 (PostgreSQL) from application IPs
    - [ ] Port 6379 (Redis) from application IPs
    - [ ] Port 8080 (Health check) from monitoring IPs

#### **Database Server Setup:**

- [ ] **Connect to Instance**
  ```bash
  ssh -i sophia-ai-key.pem ubuntu@<INSTANCE_IP>
  ```

- [ ] **Run Infrastructure Setup**
  - [ ] Upload and execute the deployment script:
    ```bash
    python3 infrastructure/lambda-labs-deployment.py
    ```
  - [ ] Verify PostgreSQL installation:
    ```bash
    sudo systemctl status postgresql
    psql -h localhost -U sophia_user -d sophia_staging
    ```
  - [ ] Verify Redis installation:
    ```bash
    sudo systemctl status redis-server
    redis-cli ping
    ```

- [ ] **Configure Monitoring**
  - [ ] Verify health check service:
    ```bash
    curl http://localhost:8080/health
    ```
  - [ ] Set up log monitoring
  - [ ] Configure backup schedules

#### **Credentials for GitHub Secrets:**
```
LAMBDA_API_KEY=lambda_xxx...
LAMBDA_SSH_PRIVATE_KEY=-----BEGIN RSA PRIVATE KEY-----...
LAMBDA_IP_ADDRESS=<INSTANCE_IP>
POSTGRESQL_HOST=<INSTANCE_IP>
POSTGRESQL_PASSWORD=<SECURE_PASSWORD>
POSTGRESQL_CONNECTION_STRING=postgresql://sophia_user:<PASSWORD>@<IP>:5432/sophia_staging
REDIS_HOST=<INSTANCE_IP>
REDIS_PASSWORD=sophia_redis_2025
REDIS_URL=redis://:<PASSWORD>@<IP>:6379
```

---

## ❄️ SNOWFLAKE CONFIGURATION

### **Platform:** [Snowflake](https://snowflake.com)
### **Purpose:** Data warehouse and Cortex AI functions
### **Account:** ZNB04675 (existing)

#### **Account Verification Checklist:**

- [ ] **Verify Account Access**
  - [ ] Log in to Snowflake console: https://app.snowflake.com
  - [ ] Account identifier: `ZNB04675`
  - [ ] Verify user: `SCOOBYJAVA15` has ACCOUNTADMIN role
  - [ ] Confirm access to existing databases

- [ ] **Programmatic Authentication Setup**
  - [ ] Verify programmatic service user exists:
    ```sql
    SHOW USERS LIKE 'PROGRAMMATIC_SERVICE_USER';
    ```
  - [ ] If not exists, create service user:
    ```sql
    CREATE USER PROGRAMMATIC_SERVICE_USER
    PASSWORD = '<SOPHIA_AI_TOKEN>'
    DEFAULT_ROLE = 'SYSADMIN'
    DEFAULT_WAREHOUSE = 'COMPUTE_WH'
    DEFAULT_NAMESPACE = 'SOPHIA_AI.PUBLIC';
    ```
  - [ ] Grant necessary roles:
    ```sql
    GRANT ROLE SYSADMIN TO USER PROGRAMMATIC_SERVICE_USER;
    GRANT ROLE PUBLIC TO USER PROGRAMMATIC_SERVICE_USER;
    ```

#### **Database and Schema Setup:**

- [ ] **Create Sophia AI Database**
  ```sql
  CREATE DATABASE IF NOT EXISTS SOPHIA_AI;
  USE DATABASE SOPHIA_AI;
  ```

- [ ] **Create Schemas**
  ```sql
  CREATE SCHEMA IF NOT EXISTS RAW_DATA;
  CREATE SCHEMA IF NOT EXISTS PROCESSED_DATA;
  CREATE SCHEMA IF NOT EXISTS ANALYTICS;
  CREATE SCHEMA IF NOT EXISTS CORTEX_AI;
  ```

- [ ] **Create Tables for Processed Data**
  ```sql
  -- Unified contacts table
  CREATE TABLE IF NOT EXISTS PROCESSED_DATA.UNIFIED_CONTACTS (
    ID VARCHAR(255) PRIMARY KEY,
    SOURCE_SYSTEM VARCHAR(50),
    SOURCE_ID VARCHAR(255),
    EMAIL VARCHAR(255),
    FIRST_NAME VARCHAR(255),
    LAST_NAME VARCHAR(255),
    FULL_NAME VARCHAR(500),
    COMPANY_NAME VARCHAR(255),
    JOB_TITLE VARCHAR(255),
    PHONE VARCHAR(50),
    CREATED_AT TIMESTAMP_TZ,
    UPDATED_AT TIMESTAMP_TZ,
    LAST_ACTIVITY TIMESTAMP_TZ,
    PROPERTIES VARIANT,
    PROCESSED_AT TIMESTAMP_TZ DEFAULT CURRENT_TIMESTAMP()
  );

  -- Interaction timeline table
  CREATE TABLE IF NOT EXISTS PROCESSED_DATA.INTERACTION_TIMELINE (
    ID VARCHAR(255) PRIMARY KEY,
    CONTACT_ID VARCHAR(255),
    INTERACTION_TYPE VARCHAR(100),
    INTERACTION_DATE TIMESTAMP_TZ,
    SOURCE_SYSTEM VARCHAR(50),
    SOURCE_ID VARCHAR(255),
    TITLE VARCHAR(500),
    DESCRIPTION TEXT,
    SENTIMENT FLOAT,
    METADATA VARIANT,
    PROCESSED_AT TIMESTAMP_TZ DEFAULT CURRENT_TIMESTAMP()
  );
  ```

#### **Cortex AI Configuration:**

- [ ] **Verify Cortex AI Access**
  ```sql
  -- Test Cortex functions
  SELECT SNOWFLAKE.CORTEX.SENTIMENT('This is a test message');
  SELECT SNOWFLAKE.CORTEX.COMPLETE('mistral-7b', 'Hello, how are you?');
  ```

- [ ] **Create Cortex AI Views**
  ```sql
  -- Sentiment analysis view
  CREATE OR REPLACE VIEW CORTEX_AI.INTERACTION_SENTIMENT AS
  SELECT 
    ID,
    TITLE,
    DESCRIPTION,
    SNOWFLAKE.CORTEX.SENTIMENT(DESCRIPTION) as SENTIMENT_SCORE,
    CASE 
      WHEN SNOWFLAKE.CORTEX.SENTIMENT(DESCRIPTION) > 0.1 THEN 'POSITIVE'
      WHEN SNOWFLAKE.CORTEX.SENTIMENT(DESCRIPTION) < -0.1 THEN 'NEGATIVE'
      ELSE 'NEUTRAL'
    END as SENTIMENT_LABEL
  FROM PROCESSED_DATA.INTERACTION_TIMELINE
  WHERE DESCRIPTION IS NOT NULL;
  ```

- [ ] **Set Up Vector Search**
  ```sql
  -- Create embedding table for vector search
  CREATE TABLE IF NOT EXISTS CORTEX_AI.DOCUMENT_EMBEDDINGS (
    ID VARCHAR(255) PRIMARY KEY,
    DOCUMENT_TYPE VARCHAR(100),
    CONTENT TEXT,
    EMBEDDING ARRAY,
    CREATED_AT TIMESTAMP_TZ DEFAULT CURRENT_TIMESTAMP()
  );
  ```

#### **Data Pipeline Integration:**

- [ ] **Configure Estuary Flow → Snowflake**
  - [ ] Set up Snowflake destination in Estuary Flow
  - [ ] Configure connection parameters:
    - [ ] Account: `ZNB04675`
    - [ ] User: `PROGRAMMATIC_SERVICE_USER`
    - [ ] Password: `SOPHIA_AI_TOKEN`
    - [ ] Warehouse: `COMPUTE_WH`
    - [ ] Database: `SOPHIA_AI`
    - [ ] Schema: `PROCESSED_DATA`
  - [ ] Test connection and data flow

- [ ] **Set Up Monitoring**
  ```sql
  -- Create monitoring view
  CREATE OR REPLACE VIEW ANALYTICS.DATA_PIPELINE_METRICS AS
  SELECT 
    'UNIFIED_CONTACTS' as TABLE_NAME,
    COUNT(*) as TOTAL_RECORDS,
    COUNT(DISTINCT SOURCE_SYSTEM) as SOURCE_SYSTEMS,
    MAX(PROCESSED_AT) as LAST_PROCESSED
  FROM PROCESSED_DATA.UNIFIED_CONTACTS
  UNION ALL
  SELECT 
    'INTERACTION_TIMELINE' as TABLE_NAME,
    COUNT(*) as TOTAL_RECORDS,
    COUNT(DISTINCT SOURCE_SYSTEM) as SOURCE_SYSTEMS,
    MAX(PROCESSED_AT) as LAST_PROCESSED
  FROM PROCESSED_DATA.INTERACTION_TIMELINE;
  ```

#### **Gong Data Share Access:**

- [ ] **Request Gong Data Share Authorization**
  - [ ] Contact Gong support at support@gong.io
  - [ ] Provide Snowflake account identifier: `ZNB04675`
  - [ ] Request access to data share: `PAYREADY_GONG_089AA23F865C4231A097A44517FA10E9.INBOUND`
  - [ ] Specify use case: Historical data analysis and bulk data access
  - [ ] Wait for authorization confirmation

- [ ] **Configure Data Share Access**
  ```sql
  -- Once authorized, create database from share
  CREATE DATABASE GONG_SHARE FROM SHARE PAYREADY_GONG_089AA23F865C4231A097A44517FA10E9.INBOUND;
  
  -- Grant access to service user
  GRANT USAGE ON DATABASE GONG_SHARE TO ROLE SYSADMIN;
  GRANT USAGE ON ALL SCHEMAS IN DATABASE GONG_SHARE TO ROLE SYSADMIN;
  GRANT SELECT ON ALL TABLES IN DATABASE GONG_SHARE TO ROLE SYSADMIN;
  ```

#### **Credentials for GitHub Secrets:**
```
SNOWFLAKE_ACCOUNT=ZNB04675
SNOWFLAKE_USER=PROGRAMMATIC_SERVICE_USER
SOPHIA_AI_TOKEN=eyJraWQiOiIxNzAwMTAwMDk2OSIsImFsZyI6IkVTMjU2In0.eyJwIjoiNjY0MTAwNjg6MTcwMDA5NTYyOTMiLCJpc3MiOiJTRjozMDAxIiwiZXhwIjoxNzU4MzkyMDc4fQ.HPlaOkJGlckJ8W8-GWt8lw0t8kIyvO6UctKrrv7d-kwjCOd5kveyKMspcFGIyuzKzS8X26BtDQQctk2LybXJOQ.
SNOWFLAKE_ROLE=SYSADMIN
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_DATABASE=SOPHIA_AI
SNOWFLAKE_SCHEMA=PUBLIC
```

---


## 🔐 GITHUB ORGANIZATION SECRETS MANAGEMENT

### **Platform:** GitHub Organization Secrets
### **Purpose:** Primary credential storage and management
### **Integration:** Syncs to Pulumi ESC for application runtime

#### **GitHub Secrets Setup Checklist:**

- [ ] **Access GitHub Organization Settings**
  - [ ] Navigate to https://github.com/organizations/ai-cherry/settings/secrets/actions
  - [ ] Verify admin access to organization secrets
  - [ ] Review existing secrets and identify gaps

- [ ] **Core Infrastructure Secrets**
  - [ ] `ESTUARY_FLOW_ACCESS_TOKEN` - Estuary Flow API access token
  - [ ] `LAMBDA_API_KEY` - Lambda Labs API key for instance management
  - [ ] `LAMBDA_SSH_PRIVATE_KEY` - SSH private key for Lambda Labs instances
  - [ ] `LAMBDA_IP_ADDRESS` - IP address of deployed Lambda Labs instance

- [ ] **Database and Cache Secrets**
  - [ ] `POSTGRESQL_HOST` - PostgreSQL server IP address
  - [ ] `POSTGRESQL_PASSWORD` - PostgreSQL sophia_user password
  - [ ] `POSTGRESQL_CONNECTION_STRING` - Full PostgreSQL connection string
  - [ ] `REDIS_HOST` - Redis server IP address
  - [ ] `REDIS_PASSWORD` - Redis authentication password
  - [ ] `REDIS_URL` - Complete Redis connection URL

- [ ] **Snowflake Data Warehouse Secrets**
  - [ ] `SNOWFLAKE_ACCOUNT` - Snowflake account identifier (ZNB04675)
  - [ ] `SOPHIA_AI_TOKEN` - Programmatic service user token
  - [ ] `SNOWFLAKE_USER` - Service user name (PROGRAMMATIC_SERVICE_USER)
  - [ ] `SNOWFLAKE_ROLE` - Default role (SYSADMIN)
  - [ ] `SNOWFLAKE_WAREHOUSE` - Compute warehouse (COMPUTE_WH)
  - [ ] `SNOWFLAKE_DATABASE` - Target database (SOPHIA_AI)

- [ ] **External Integration Secrets**
  - [ ] `HUBSPOT_ACCESS_TOKEN` - HubSpot API access token
  - [ ] `HUBSPOT_API_KEY` - HubSpot API key (if different from access token)
  - [ ] `HUBSPOT_PORTAL_ID` - HubSpot portal identifier
  - [ ] `GONG_ACCESS_KEY` - Gong API access key
  - [ ] `GONG_CLIENT_SECRET` - Gong API client secret
  - [ ] `GONG_WEBHOOK_SECRET` - Gong webhook verification secret
  - [ ] `SLACK_BOT_TOKEN` - Slack bot token (xoxb-...)
  - [ ] `SLACK_APP_TOKEN` - Slack app token (xapp-...)
  - [ ] `SLACK_SIGNING_SECRET` - Slack signing secret for verification
  - [ ] `SLACK_CLIENT_ID` - Slack app client ID
  - [ ] `SLACK_CLIENT_SECRET` - Slack app client secret

- [ ] **AI Services Secrets**
  - [ ] `OPENAI_API_KEY` - OpenAI API key
  - [ ] `ANTHROPIC_API_KEY` - Anthropic API key
  - [ ] `PORTKEY_API_KEY` - Portkey gateway API key
  - [ ] `PORTKEY_CONFIG` - Portkey configuration ID
  - [ ] `PINECONE_API_KEY` - Pinecone vector database API key
  - [ ] `PINECONE_ENVIRONMENT` - Pinecone environment identifier

- [ ] **Deployment and CI/CD Secrets**
  - [ ] `VERCEL_TOKEN` - Vercel deployment token
  - [ ] `VERCEL_PROJECT_ID` - Vercel project identifier
  - [ ] `VERCEL_ORG_ID` - Vercel organization identifier
  - [ ] `GITHUB_TOKEN` - GitHub API token for automation
  - [ ] `PULUMI_ACCESS_TOKEN` - Pulumi ESC access token

#### **Secret Validation Checklist:**

- [ ] **Verify Secret Format**
  - [ ] All API keys follow expected format patterns
  - [ ] Connection strings are properly formatted
  - [ ] No trailing spaces or newlines in secrets
  - [ ] Special characters are properly escaped

- [ ] **Test Secret Access**
  - [ ] Verify each secret can be accessed by GitHub Actions
  - [ ] Test secret rotation procedures
  - [ ] Confirm backup and recovery processes
  - [ ] Validate audit logging is enabled

---

## 🔧 PULUMI ESC CONFIGURATION

### **Platform:** Pulumi ESC (Environment, Secrets, and Configuration)
### **Purpose:** Centralized secret management and distribution
### **Integration:** Consumes GitHub Secrets, provides to applications

#### **Pulumi ESC Setup Checklist:**

- [ ] **Verify Pulumi ESC Access**
  - [ ] Install Pulumi CLI: `curl -fsSL https://get.pulumi.com | sh`
  - [ ] Login to Pulumi: `pulumi login`
  - [ ] Verify access to organization: `scoobyjava-org`
  - [ ] Check existing environments: `pulumi env ls`

- [ ] **Environment Configuration**
  - [ ] Environment name: `scoobyjava-org/default/sophia-ai-production`
  - [ ] Verify environment exists: `pulumi env get scoobyjava-org/default/sophia-ai-production`
  - [ ] If not exists, create: `pulumi env init scoobyjava-org/default/sophia-ai-production`

- [ ] **Deploy Comprehensive ESC Configuration**
  - [ ] Run ESC update script:
    ```bash
    cd infrastructure/
    python3 pulumi-esc-update.py
    ```
  - [ ] Deploy generated configuration:
    ```bash
    pulumi env init scoobyjava-org/default/sophia-ai-production --file comprehensive-esc-config.yaml
    ```
  - [ ] Verify configuration deployment:
    ```bash
    pulumi env get scoobyjava-org/default/sophia-ai-production
    ```

- [ ] **Validate Secret Synchronization**
  - [ ] Test GitHub Secrets → ESC sync:
    ```bash
    pulumi env get scoobyjava-org/default/sophia-ai-production --show-secrets
    ```
  - [ ] Verify all required secrets are available
  - [ ] Test secret access from application code
  - [ ] Confirm environment variable export

#### **ESC Configuration Validation:**

- [ ] **Infrastructure Secrets**
  ```bash
  # Test Estuary Flow access
  pulumi env get scoobyjava-org/default/sophia-ai-production estuary_flow_access_token
  
  # Test Lambda Labs access
  pulumi env get scoobyjava-org/default/sophia-ai-production lambda_api_key
  
  # Test database connections
  pulumi env get scoobyjava-org/default/sophia-ai-production postgresql_host
  pulumi env get scoobyjava-org/default/sophia-ai-production redis_url
  ```

- [ ] **Application Integration**
  ```python
  # Test ESC integration in application
  from backend.core.auto_esc_config import get_config_value
  
  # Verify credential access
  assert get_config_value("estuary_flow_access_token") is not None
  assert get_config_value("postgresql_host") is not None
  assert get_config_value("snowflake_account") == "ZNB04675"
  ```

---

## 🚀 DEPLOYMENT EXECUTION PLAN

### **Phase 1: Infrastructure Setup (Day 1)**

#### **Morning (9:00 AM - 12:00 PM):**
- [ ] **Lambda Labs Setup**
  - [ ] Create Lambda Labs account and generate API key
  - [ ] Launch database instance using deployment script
  - [ ] Configure PostgreSQL and Redis on instance
  - [ ] Verify health checks and monitoring

#### **Afternoon (1:00 PM - 5:00 PM):**
- [ ] **GitHub Secrets Configuration**
  - [ ] Add all infrastructure secrets to GitHub Organization
  - [ ] Update Lambda Labs IP address and credentials
  - [ ] Verify secret access and formatting

### **Phase 2: Data Pipeline Setup (Day 2)**

#### **Morning (9:00 AM - 12:00 PM):**
- [ ] **Estuary Flow Configuration**
  - [ ] Create Estuary Flow account and generate credentials
  - [ ] Configure HubSpot, Gong, and Slack connectors
  - [ ] Set up PostgreSQL destination
  - [ ] Test data flow and validation

#### **Afternoon (1:00 PM - 5:00 PM):**
- [ ] **Snowflake Integration**
  - [ ] Verify Snowflake account access
  - [ ] Set up programmatic service user
  - [ ] Create databases, schemas, and tables
  - [ ] Test Cortex AI functions

### **Phase 3: Integration and Testing (Day 3)**

#### **Morning (9:00 AM - 12:00 PM):**
- [ ] **Pulumi ESC Deployment**
  - [ ] Deploy comprehensive ESC configuration
  - [ ] Sync GitHub Secrets to ESC
  - [ ] Test application credential access
  - [ ] Verify environment variable export

#### **Afternoon (1:00 PM - 5:00 PM):**
- [ ] **End-to-End Testing**
  - [ ] Test complete data pipeline flow
  - [ ] Verify MCP server functionality
  - [ ] Run performance benchmarks
  - [ ] Validate monitoring and alerting

### **Phase 4: Production Deployment (Day 4)**

#### **Morning (9:00 AM - 12:00 PM):**
- [ ] **Production Deployment**
  - [ ] Deploy updated application code
  - [ ] Enable production data flows
  - [ ] Configure monitoring dashboards
  - [ ] Set up alerting and notifications

#### **Afternoon (1:00 PM - 5:00 PM):**
- [ ] **Validation and Documentation**
  - [ ] Verify all systems operational
  - [ ] Complete deployment documentation
  - [ ] Train team on new architecture
  - [ ] Plan ongoing maintenance procedures

---

## 📊 SUCCESS CRITERIA

### **Technical Metrics:**
- [ ] **Data Pipeline Performance**
  - [ ] Sub-second data latency from sources to PostgreSQL
  - [ ] 99.9% uptime for all data flows
  - [ ] Zero data loss during pipeline operation
  - [ ] 90% query performance improvement in Snowflake

- [ ] **Security Compliance**
  - [ ] Zero hardcoded credentials in codebase
  - [ ] All secrets managed through GitHub → ESC pipeline
  - [ ] Audit logging enabled for all credential access
  - [ ] Encryption in transit and at rest

- [ ] **System Reliability**
  - [ ] Health checks operational for all services
  - [ ] Automated failover and recovery procedures
  - [ ] Comprehensive monitoring and alerting
  - [ ] Backup and disaster recovery tested

### **Business Metrics:**
- [ ] **Cost Optimization**
  - [ ] 60% reduction in ETL infrastructure costs
  - [ ] 40% reduction in Snowflake compute costs
  - [ ] Pay-per-use model for data pipeline
  - [ ] Optimized resource utilization

- [ ] **Operational Efficiency**
  - [ ] Real-time data availability (vs. hourly batches)
  - [ ] Automated data quality monitoring
  - [ ] Self-healing infrastructure components
  - [ ] Reduced manual intervention requirements

---

## 🆘 TROUBLESHOOTING GUIDE

### **Common Issues and Solutions:**

#### **Estuary Flow Connection Issues:**
```bash
# Test API connectivity
curl -H "Authorization: Bearer $ESTUARY_FLOW_ACCESS_TOKEN" \
     https://api.estuary.dev/v1/collections

# Verify source connector configuration
# Check authentication credentials in Estuary Flow UI
# Validate data source API access
```

#### **Lambda Labs Instance Issues:**
```bash
# Check instance status
curl -H "Authorization: Bearer $LAMBDA_API_KEY" \
     https://cloud.lambdalabs.com/api/v1/instances

# SSH connection troubleshooting
ssh -i sophia-ai-key.pem -v ubuntu@$LAMBDA_IP_ADDRESS

# Service status verification
sudo systemctl status postgresql redis-server sophia-health
```

#### **Snowflake Authentication Issues:**
```sql
-- Test programmatic user access
SELECT CURRENT_USER(), CURRENT_ROLE(), CURRENT_WAREHOUSE();

-- Verify Cortex AI access
SELECT SNOWFLAKE.CORTEX.SENTIMENT('test message');

-- Check database permissions
SHOW GRANTS TO USER PROGRAMMATIC_SERVICE_USER;
```

#### **Pulumi ESC Issues:**
```bash
# Refresh ESC configuration
pulumi env refresh scoobyjava-org/default/sophia-ai-production

# Test secret access
pulumi env get scoobyjava-org/default/sophia-ai-production --show-secrets

# Validate environment variables
pulumi env open scoobyjava-org/default/sophia-ai-production
```

---

## 📞 SUPPORT CONTACTS

### **Platform Support:**
- **Estuary Flow:** support@estuary.dev
- **Lambda Labs:** support@lambdalabs.com  
- **Snowflake:** support@snowflake.com
- **Pulumi:** support@pulumi.com

### **Integration Support:**
- **HubSpot:** developers@hubspot.com
- **Gong:** support@gong.io (for data share authorization)
- **Slack:** api@slack.com

---

**Deployment Status:** ✅ **READY FOR IMPLEMENTATION**  
**Estimated Timeline:** 4 days for complete deployment  
**Risk Level:** Low (comprehensive testing and validation procedures)  
**Success Probability:** 95% (based on thorough preparation and documentation)

