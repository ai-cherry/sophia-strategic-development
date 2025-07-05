# Sophia AI System Architecture

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend Layer                        │
│  ┌─────────────────────────────────────────────────────┐   │
│  │            UnifiedDashboard.tsx                      │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │   │
│  │  │ Enhanced     │  │  Citation    │  │  Focus    │ │   │
│  │  │ Unified Chat │  │  Sidebar     │  │  Modes    │ │   │
│  │  └──────────────┘  └──────────────┘  └───────────┘ │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                         API Layer                            │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              FastAPI Backend                         │   │
│  │  ┌──────────┐  ┌──────────┐  ┌─────────────────┐  │   │
│  │  │  Chat    │  │ Citation │  │    Cortex       │  │   │
│  │  │  Routes  │  │  Service │  │    Router       │  │   │
│  │  └──────────┘  └──────────┘  └─────────────────┘  │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                    Orchestration Layer                       │
│  ┌─────────────────────────────────────────────────────┐   │
│  │            LangGraph Orchestrator                    │   │
│  │  ┌──────────┐  ┌──────────┐  ┌─────────────────┐  │   │
│  │  │ Business │  │   Code   │  │      Data       │  │   │
│  │  │  Agent   │  │  Agent   │  │     Agent       │  │   │
│  │  └──────────┘  └──────────┘  └─────────────────┘  │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                      Data Layer                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │Snowflake │  │   Mem0   │  │  Redis   │  │PostgreSQL│   │
│  │ Cortex   │  │  Memory  │  │Event Bus │  │Metadata  │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Component Details

### Frontend Layer

#### EnhancedUnifiedChat
- **Purpose**: Primary user interface for AI interactions
- **Key Features**:
  - Natural language input
  - Citation display ([1], [2] inline markers)
  - Ice breaker prompts
  - Follow-up suggestions
  - Focus mode selector

#### Citation Sidebar
- **Purpose**: Display source information for transparency
- **Features**:
  - Collapsible panel
  - Source previews
  - Link to original content
  - Confidence scores

### API Layer

#### Chat Routes (`/api/chat/*`)
- **Endpoints**:
  - `POST /api/chat/message` - Send user message
  - `GET /api/chat/history` - Retrieve conversation history
  - `POST /api/chat/feedback` - User feedback on responses

#### Citation Service
- **Responsibilities**:
  - Extract citations from LLM responses
  - Verify source validity
  - Format citations consistently
  - Track citation usage

#### Cortex Router
- **Model Selection Logic**:
  ```python
  if intent == "classification":
      return "mistral-7b"  # Fastest, cheapest
  elif complexity < 0.3:
      return "llama3-8b"   # Balanced
  elif intent == "code":
      return "llama3-70b"  # Powerful
  else:
      return "snowflake-arctic"  # Most capable
  ```

### Orchestration Layer

#### LangGraph Orchestrator
- **Architecture**: Directed Acyclic Graph (DAG)
- **Node Types**:
  - Intent Classification
  - Agent Selection
  - Execution
  - Response Synthesis
  - Memory Storage

#### Specialized Agents

**Business Intelligence Agent**:
- Revenue analysis
- Customer insights
- Sales performance
- Market trends

**Code Generation Agent**:
- Natural language to code
- Code explanation
- Bug fixing
- Refactoring suggestions

**Data Analysis Agent**:
- SQL generation
- Data visualization
- Statistical analysis
- Trend detection

### Data Layer

#### Snowflake Integration
- **Cortex Functions**:
  - `COMPLETE()` - LLM completions
  - `SUMMARIZE()` - Text summarization
  - `CLASSIFY_TEXT()` - Intent classification
  - `SENTIMENT()` - Sentiment analysis

#### Mem0 Memory System
- **Storage**: PostgreSQL with pgvector
- **Embedding**: Snowflake Arctic Embed
- **Features**:
  - Conversation history
  - Decision tracking
  - Insight extraction
  - Context persistence

#### Redis Event Bus
- **Purpose**: Asynchronous communication
- **Patterns**:
  - Pub/Sub for real-time updates
  - Task queues for background jobs
  - Caching for performance

## Data Flow

### Request Flow
1. User enters query in UnifiedChat
2. Frontend sends to `/api/chat/message`
3. API validates and enriches request
4. Cortex Router selects appropriate model
5. LangGraph orchestrates agent execution
6. Agents query data sources
7. Response synthesized with citations
8. Memory system stores conversation
9. Frontend displays response with citations

### Citation Flow
1. LLM generates response with sources
2. Citation Service extracts references
3. Sources verified against data
4. Citations formatted as [1], [2], etc.
5. Sidebar populated with source details
6. User can click for full source

## Security Architecture

### Authentication & Authorization
- OAuth2 via Snowflake
- Role-based access control
- Session management in Redis

### Data Security
- All data encrypted at rest
- TLS for data in transit
- No data leaves Snowflake perimeter
- Audit logging for compliance

### AI Safety
- Input validation and sanitization
- Output filtering with Cortex Guard
- Prompt injection detection
- Rate limiting per user

## Performance Considerations

### Optimization Strategies
1. **Model Routing**: Use smallest effective model
2. **Caching**: Redis for frequent queries
3. **Parallel Processing**: Concurrent agent execution
4. **Connection Pooling**: Reuse database connections
5. **Async Operations**: Non-blocking I/O throughout

### Monitoring Points
- Response time per endpoint
- Model usage and costs
- Memory hit/miss rates
- Citation accuracy scores
- User satisfaction metrics

## Deployment Architecture

### Current (Docker Swarm)
```yaml
services:
  frontend:
    image: sophia-frontend
    replicas: 2

  backend:
    image: sophia-backend
    replicas: 3

  redis:
    image: redis:alpine

  postgres:
    image: postgres:15
```

### Future (Kubernetes)
- Horizontal pod autoscaling
- Service mesh for observability
- Persistent volume claims
- ConfigMaps for configuration
