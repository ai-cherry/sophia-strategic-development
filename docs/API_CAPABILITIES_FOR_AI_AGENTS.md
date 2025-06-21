# Sophia AI - API Capabilities Guide for AI Agents

## 🤖 Overview for AI Coding Assistants

This document provides a comprehensive overview of all API capabilities available in the Sophia AI system. AI agents should reference this guide when suggesting solutions, building integrations, or solving problems.

**Last Updated**: Auto-generated from GitHub organization secrets validation

## 🎯 Quick Reference for Problem Solving

### When to Use Each Service

| Problem Type | Recommended Services | Use Case |
|-------------|---------------------|----------|
| **Text Generation** | OpenAI, Anthropic | Content creation, code generation, chat responses |
| **Advanced Reasoning** | Anthropic Claude | Complex analysis, code review, strategic planning |
| **Vector Search** | Pinecone, Weaviate | Semantic search, RAG, similarity matching |
| **Business Intelligence** | Gong, HubSpot, Snowflake | Sales analytics, CRM data, revenue insights |
| **Team Communication** | Slack, Discord | Notifications, team updates, bot interactions |
| **Data Processing** | Snowflake, PostgreSQL | Analytics, reporting, data warehousing |
| **Cloud Deployment** | Vercel, Lambda Labs | Frontend hosting, GPU compute, infrastructure |
| **Monitoring** | Datadog, Sentry | Error tracking, performance monitoring, alerting |

## 🔧 Available API Categories

### 🤖 AI & Machine Learning Services

#### OpenAI (Primary LLM)
- **Purpose**: Text generation, embeddings, chat completions
- **Building Use**: Primary LLM for conversational AI, code generation, content creation
- **Capabilities**: `text-generation`, `embeddings`, `chat`, `code-completion`
- **When to Use**: Default choice for text generation, embeddings, and general AI tasks
- **Integration**: `from backend.core.auto_esc_config import config; openai_key = config.openai_api_key`

#### Anthropic Claude (Advanced Reasoning)
- **Purpose**: Advanced reasoning, long-context analysis, safety-focused AI
- **Building Use**: Complex reasoning, code review, analytical tasks requiring nuance
- **Capabilities**: `advanced-reasoning`, `code-analysis`, `long-context`, `safety`
- **When to Use**: Complex analysis, ethical considerations, long document processing
- **Integration**: `anthropic_key = config.anthropic_api_key`

#### Hugging Face (Open Source Models)
- **Purpose**: Access to open-source models, custom fine-tuning
- **Building Use**: Specialized AI tasks, model experimentation, cost optimization
- **Capabilities**: `open-source-models`, `fine-tuning`, `datasets`, `transformers`
- **When to Use**: Custom models, specialized tasks, research and development

#### Cohere (Enterprise AI)
- **Purpose**: Enterprise-grade embeddings, classification, generation
- **Building Use**: Business-focused AI applications with enterprise requirements
- **Capabilities**: `embeddings`, `classification`, `generation`, `enterprise-ai`
- **When to Use**: Enterprise applications requiring high reliability and compliance

#### Replicate (Model Hosting)
- **Purpose**: Hosted open-source models, image/video generation
- **Building Use**: Image generation, video processing, specialized model inference
- **Capabilities**: `model-hosting`, `image-generation`, `video-processing`, `inference`
- **When to Use**: Creative applications, multimedia processing, specialized models

### 🔗 Vector Databases & Search

#### Pinecone (Primary Vector Database)
- **Purpose**: High-performance vector similarity search
- **Building Use**: Primary vector storage for embeddings, semantic search, RAG systems
- **Capabilities**: `vector-search`, `embeddings-storage`, `rag`, `semantic-similarity`
- **When to Use**: Default choice for vector search, knowledge retrieval, semantic applications
- **Integration**: `pinecone_key = config.pinecone_api_key`

#### Weaviate (Hybrid Search)
- **Purpose**: Vector database with GraphQL interface
- **Building Use**: Hybrid search combining vector and traditional search
- **Capabilities**: `hybrid-search`, `graphql`, `vector-storage`, `knowledge-graphs`
- **When to Use**: Complex search requirements, graph-based knowledge systems

#### Qdrant (High-Performance Search)
- **Purpose**: Vector similarity search with advanced filtering
- **Building Use**: High-performance vector search with metadata filtering
- **Capabilities**: `vector-similarity`, `filtering`, `faceting`, `high-performance`
- **When to Use**: Performance-critical applications, complex filtering requirements

### 💼 Business Intelligence & CRM

#### Gong.io (Conversation Analytics)
- **Purpose**: Sales call analysis and conversation intelligence
- **Building Use**: Revenue optimization, sales coaching, conversation insights
- **Capabilities**: `call-analysis`, `conversation-ai`, `sales-intelligence`, `revenue-ops`
- **When to Use**: Sales analytics, call transcription analysis, revenue intelligence
- **Integration**: `gong_key = config.gong_access_key`

#### HubSpot (CRM)
- **Purpose**: Customer relationship management and marketing automation
- **Building Use**: Contact management, deal tracking, marketing workflows
- **Capabilities**: `crm`, `contact-management`, `deal-tracking`, `marketing-automation`
- **When to Use**: CRM operations, contact management, sales pipeline automation
- **Integration**: `hubspot_key = config.hubspot_api_token`

#### Salesforce (Enterprise CRM)
- **Purpose**: Enterprise-grade CRM and business process automation
- **Building Use**: Large-scale CRM operations, complex business workflows
- **Capabilities**: `enterprise-crm`, `opportunity-management`, `forecasting`, `workflow-automation`
- **When to Use**: Enterprise CRM requirements, complex business processes

### 💬 Communication & Collaboration

#### Slack (Team Communication)
- **Purpose**: Team messaging, notifications, bot interactions
- **Building Use**: Automated notifications, team updates, interactive commands
- **Capabilities**: `team-communication`, `notifications`, `bot-commands`, `workflow-automation`
- **When to Use**: Team notifications, status updates, interactive workflows
- **Integration**: `slack_token = config.slack_bot_token`

#### Discord (Community Management)
- **Purpose**: Community engagement and user interaction
- **Building Use**: Community management, user engagement, automated responses
- **Capabilities**: `community-management`, `discord-integration`, `automated-responses`
- **When to Use**: Community building, user engagement, public-facing bots

### 🗄️ Data Infrastructure

#### Snowflake (Data Warehouse)
- **Purpose**: Cloud data warehouse for analytics and business intelligence
- **Building Use**: Primary data warehouse for analytics, reporting, business intelligence
- **Capabilities**: `data-warehousing`, `analytics`, `sql-queries`, `business-intelligence`
- **When to Use**: Data analytics, business reporting, large-scale data processing
- **Integration**: `snowflake_account = config.snowflake_account`

#### PostgreSQL (Operational Database)
- **Purpose**: Relational database for application data
- **Building Use**: Primary operational database for transactional data
- **Capabilities**: `operational-database`, `application-data`, `transactions`
- **When to Use**: Application data storage, transactional operations, relational data

#### Redis (Caching & Sessions)
- **Purpose**: In-memory data structure store for caching
- **Building Use**: High-speed caching, session management, real-time data
- **Capabilities**: `caching`, `session-storage`, `real-time-data`, `pub-sub`
- **When to Use**: Performance optimization, session management, real-time applications

### ☁️ Cloud Infrastructure

#### Lambda Labs (GPU Compute)
- **Purpose**: High-performance GPU instances for AI workloads
- **Building Use**: AI model training, inference, high-performance computing
- **Capabilities**: `gpu-compute`, `model-training`, `ai-inference`, `high-performance`
- **When to Use**: AI model training, GPU-intensive tasks, machine learning workloads
- **Integration**: `lambda_key = config.lambda_labs_api_key`

#### Vercel (Frontend Deployment)
- **Purpose**: Frontend hosting and serverless functions
- **Building Use**: Automated frontend deployment, edge computing, serverless APIs
- **Capabilities**: `frontend-deployment`, `serverless`, `edge-computing`, `ci-cd`
- **When to Use**: Frontend hosting, serverless functions, global edge deployment
- **Integration**: `vercel_token = config.vercel_access_token`

#### AWS (Cloud Services)
- **Purpose**: Comprehensive cloud computing platform
- **Building Use**: Cloud infrastructure, object storage, managed services
- **Capabilities**: `cloud-services`, `object-storage`, `compute`, `managed-services`
- **When to Use**: Cloud infrastructure, file storage, managed cloud services

#### Pulumi (Infrastructure as Code)
- **Purpose**: Infrastructure deployment and secret management
- **Building Use**: Infrastructure automation, secret management, deployment pipelines
- **Capabilities**: `infrastructure-as-code`, `secret-management`, `deployment`, `configuration`
- **When to Use**: Infrastructure automation, deployment pipelines, configuration management

### 🔧 Development Tools

#### GitHub (Repository Management)
- **Purpose**: Code repository management and CI/CD
- **Building Use**: Repository operations, automated workflows, code management
- **Capabilities**: `repository-management`, `ci-cd`, `code-operations`, `api-access`
- **When to Use**: Code management, automated workflows, repository operations
- **Integration**: `github_token = config.github_token`

#### Linear (Project Management)
- **Purpose**: Issue tracking and project management
- **Building Use**: Development workflow, issue tracking, project coordination
- **Capabilities**: `project-management`, `issue-tracking`, `workflow`, `development-ops`
- **When to Use**: Project management, issue tracking, development coordination
- **Integration**: `linear_key = config.linear_api_key`

#### Notion (Documentation)
- **Purpose**: Documentation and knowledge management
- **Building Use**: Team documentation, knowledge base, content management
- **Capabilities**: `documentation`, `knowledge-base`, `collaboration`, `content-management`
- **When to Use**: Documentation systems, knowledge bases, team collaboration

#### Retool (Internal Tools)
- **Purpose**: Custom internal tool and dashboard building
- **Building Use**: Admin dashboards, internal tools, data visualization
- **Capabilities**: `internal-tools`, `dashboards`, `data-visualization`, `admin-interfaces`
- **When to Use**: Custom admin interfaces, internal tools, data dashboards

### 📊 Analytics & Monitoring

#### Datadog (Monitoring)
- **Purpose**: Application monitoring and observability
- **Building Use**: Performance monitoring, alerting, system observability
- **Capabilities**: `monitoring`, `observability`, `performance-tracking`, `alerting`
- **When to Use**: Production monitoring, performance optimization, system health
- **Integration**: `datadog_key = config.datadog_api_key`

#### Sentry (Error Tracking)
- **Purpose**: Error tracking and performance monitoring
- **Building Use**: Bug tracking, error monitoring, performance analysis
- **Capabilities**: `error-tracking`, `performance-monitoring`, `debugging`, `alerting`
- **When to Use**: Error tracking, debugging, performance monitoring

#### Mixpanel (Product Analytics)
- **Purpose**: User behavior and product analytics
- **Building Use**: User behavior analysis, product optimization, conversion tracking
- **Capabilities**: `product-analytics`, `user-behavior`, `conversion-tracking`, `funnel-analysis`
- **When to Use**: Product analytics, user behavior tracking, conversion optimization

### 💳 Payment Processing

#### Stripe (Payment Processing)
- **Purpose**: Payment processing and billing automation
- **Building Use**: Payment flows, subscription billing, financial transactions
- **Capabilities**: `payment-processing`, `billing`, `subscriptions`, `financial-transactions`
- **When to Use**: Payment systems, subscription management, financial transactions
- **Integration**: `stripe_key = config.stripe_api_key`

#### PayPal (Alternative Payments)
- **Purpose**: PayPal payment integration
- **Building Use**: Alternative payment methods, PayPal-specific features
- **Capabilities**: `payment-processing`, `paypal-integration`, `alternative-payments`
- **When to Use**: PayPal payments, alternative payment methods

### 🔄 Data Integration

#### Airbyte (ETL Pipelines)
- **Purpose**: Data integration and ETL pipeline management
- **Building Use**: Data synchronization, ETL operations, data pipeline automation
- **Capabilities**: `data-pipelines`, `etl`, `data-sync`, `integration`
- **When to Use**: Data integration, ETL processes, data synchronization

#### Estuary (Real-time Streaming)
- **Purpose**: Real-time data streaming and change data capture
- **Building Use**: Real-time data flows, CDC, streaming analytics
- **Capabilities**: `real-time-streaming`, `change-data-capture`, `data-flow`
- **When to Use**: Real-time data processing, streaming analytics, CDC

#### Zapier (Workflow Automation)
- **Purpose**: No-code workflow automation and app integration
- **Building Use**: Process automation, app integration, workflow orchestration
- **Capabilities**: `workflow-automation`, `app-integration`, `process-automation`
- **When to Use**: Workflow automation, app integration, process optimization

## 🚀 Integration Patterns for AI Agents

### Automatic Secret Access
All secrets are automatically available via the permanent solution:

```python
# Automatic secret loading
from backend.core.auto_esc_config import config

# Use any API
openai_key = config.openai_api_key
anthropic_key = config.anthropic_api_key
pinecone_key = config.pinecone_api_key
slack_token = config.slack_bot_token
```

### Common Integration Patterns

#### RAG System with Multiple LLMs
```python
# Use OpenAI for embeddings, Anthropic for reasoning
embeddings_client = OpenAI(api_key=config.openai_api_key)
reasoning_client = Anthropic(api_key=config.anthropic_api_key)
vector_db = Pinecone(api_key=config.pinecone_api_key)
```

#### Business Intelligence Pipeline
```python
# Gong → Snowflake → HubSpot workflow
gong_client = GongAPI(access_key=config.gong_access_key)
snowflake_conn = snowflake.connector.connect(
    account=config.snowflake_account,
    user=config.snowflake_user,
    password=config.snowflake_password
)
hubspot_client = HubSpot(token=config.hubspot_api_token)
```

#### Monitoring & Alerting
```python
# Datadog monitoring with Slack notifications
datadog_client = DatadogAPI(api_key=config.datadog_api_key)
slack_client = SlackAPI(token=config.slack_bot_token)
sentry_sdk.init(dsn=config.sentry_dsn)
```

## 🎯 AI Agent Decision Matrix

### For Text Generation Tasks
1. **Primary**: OpenAI GPT models (fast, reliable, cost-effective)
2. **Advanced**: Anthropic Claude (complex reasoning, safety-critical)
3. **Specialized**: Hugging Face (custom models, specific domains)

### For Data Storage & Retrieval
1. **Vector Search**: Pinecone (primary), Weaviate (hybrid search)
2. **Operational Data**: PostgreSQL (transactional), Redis (caching)
3. **Analytics**: Snowflake (data warehouse), Mixpanel (product analytics)

### For Business Operations
1. **CRM**: HubSpot (primary), Salesforce (enterprise)
2. **Communication**: Slack (internal), Discord (community)
3. **Analytics**: Gong (sales), Datadog (technical), Mixpanel (product)

### For Development & Deployment
1. **Code Management**: GitHub (primary repository)
2. **Project Management**: Linear (issues), Notion (documentation)
3. **Deployment**: Vercel (frontend), Lambda Labs (AI workloads)

## 📋 Capability Testing

To validate which APIs are currently available and functional:

```bash
# Test all GitHub organization secrets
python scripts/test_all_github_org_secrets.py

# Sync validated secrets to Pulumi ESC
python scripts/sync_validated_secrets_to_esc.py

# Test the permanent solution
python scripts/test_permanent_solution.py
```

## 🤖 AI Agent Guidelines

### When Suggesting Solutions
1. **Check Available APIs**: Reference `docs/CURRENT_CAPABILITIES.json` for real-time capability status
2. **Use Primary Services**: Default to primary services (OpenAI, Pinecone, Slack, etc.)
3. **Consider Fallbacks**: Always suggest fallback options for critical functionality
4. **Leverage Automation**: Use the permanent secret management solution for all integrations

### When Building Integrations
1. **Use Auto Config**: Always use `backend.core.auto_esc_config` for secret access
2. **Implement Error Handling**: Handle API failures gracefully with fallbacks
3. **Add Monitoring**: Integrate with Datadog/Sentry for observability
4. **Document Capabilities**: Update this guide when adding new integrations

### When Troubleshooting
1. **Check Secret Status**: Validate secrets are available and functional
2. **Monitor API Health**: Use monitoring tools to identify issues
3. **Test Incrementally**: Isolate problems by testing individual components
4. **Update Documentation**: Keep capability documentation current

---

**🎯 AI Agent Success Factors**:
- Always check current capability status before suggesting solutions
- Use the permanent secret management system for all API access
- Implement comprehensive error handling and monitoring
- Keep documentation updated as capabilities evolve

## 🤖 Available Services & Building Purposes

### 🧠 AI & ML Services
- **OPENAI_API_KEY**: Primary LLM for text generation, embeddings, chat completions
- **ANTHROPIC_API_KEY**: Advanced reasoning, code review, long-context analysis
- **HUGGINGFACE_API_KEY**: Open-source models, fine-tuning, specialized AI tasks
- **COHERE_API_KEY**: Enterprise embeddings, classification, generation
- **REPLICATE_API_KEY**: Image/video generation, hosted model inference

### 🔍 Vector Databases
- **PINECONE_API_KEY**: Primary vector search, embeddings storage, RAG systems
- **WEAVIATE_API_KEY**: Hybrid search, GraphQL interface, knowledge graphs
- **QDRANT_API_KEY**: High-performance vector search with filtering

### 💼 Business Intelligence
- **GONG_ACCESS_KEY**: Sales call analysis, conversation AI, revenue intelligence
- **HUBSPOT_API_TOKEN**: CRM operations, contact management, deal tracking
- **SALESFORCE_ACCESS_TOKEN**: Enterprise CRM, opportunity management

### 💬 Communication
- **SLACK_BOT_TOKEN**: Team notifications, bot commands, workflow automation
- **DISCORD_BOT_TOKEN**: Community management, user engagement
- **SLACK_SIGNING_SECRET**: Request verification, webhook security

### 🗄️ Data Infrastructure
- **SNOWFLAKE_ACCOUNT/USER/PASSWORD**: Data warehousing, analytics, BI
- **POSTGRES_PASSWORD**: Operational database, application data
- **REDIS_PASSWORD**: Caching, session storage, real-time data

### ☁️ Cloud Infrastructure
- **LAMBDA_LABS_API_KEY**: GPU compute, AI model training, inference
- **VERCEL_ACCESS_TOKEN**: Frontend deployment, serverless functions
- **AWS_ACCESS_KEY_ID/SECRET**: Cloud services, object storage
- **PULUMI_ACCESS_TOKEN**: Infrastructure as code, secret management

### 🔧 Development Tools
- **GITHUB_TOKEN**: Repository management, CI/CD, code operations
- **LINEAR_API_KEY**: Project management, issue tracking, workflows
- **NOTION_API_KEY**: Documentation, knowledge base, collaboration
- **RETOOL_API_TOKEN**: Internal tools, admin dashboards

### 📊 Monitoring & Analytics
- **DATADOG_API_KEY**: Application monitoring, performance tracking
- **SENTRY_DSN**: Error tracking, debugging, performance monitoring
- **MIXPANEL_API_KEY**: Product analytics, user behavior tracking

### 💳 Payment Processing
- **STRIPE_API_KEY**: Payment processing, billing, subscriptions
- **PAYPAL_CLIENT_ID**: Alternative payments, PayPal integration

### 🔄 Data Integration
- **AIRBYTE_API_KEY**: ETL pipelines, data synchronization
- **ESTUARY_API_KEY**: Real-time streaming, change data capture
- **ZAPIER_API_KEY**: Workflow automation, app integration

## 🚀 Quick Integration Pattern

```python
# All secrets automatically available
from backend.core.auto_esc_config import config

# Use any service
openai_key = config.openai_api_key
pinecone_key = config.pinecone_api_key
slack_token = config.slack_bot_token
```

## 🎯 When to Use What

| Task | Primary Choice | Alternative |
|------|---------------|-------------|
| Text Generation | OpenAI | Anthropic |
| Vector Search | Pinecone | Weaviate |
| Team Notifications | Slack | Discord |
| Data Analytics | Snowflake | PostgreSQL |
| Error Tracking | Sentry | Datadog |
| Payment Processing | Stripe | PayPal |

## 📋 Validation Commands

```bash
# Test all secrets
python scripts/test_all_github_org_secrets.py

# Sync to Pulumi ESC  
python scripts/sync_validated_secrets_to_esc.py

# Validate setup
python scripts/test_permanent_solution.py
``` 