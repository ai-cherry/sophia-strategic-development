# Clean Architecture Tech Stack Alignment

This document explains how the Clean Architecture implementation aligns with Sophia AI's technology stack.

## Core Technology Stack

### Infrastructure Platform
- **Lambda Labs Servers**: Primary compute infrastructure (NOT AWS)
- **Kubernetes**: Container orchestration for microservices
- **Docker**: Containerization with optimized multi-stage builds

### Data Layer
- **Modern Stack**: Primary data warehouse and analytics engine
  - Lambda GPU for AI/ML capabilities
  - Native vector embeddings support
- **Estuary Flow**: Real-time data integration and ETL

### API Gateway & AI Services
- **Portkey**: Unified LLM gateway for model routing
- **OpenRouter**: Alternative LLM routing service
- **Vercel**: Frontend deployment and edge functions

### Development & Operations
- **Pulumi**: Infrastructure as Code (IaC)
- **GitHub Actions**: CI/CD pipelines
- **Pulumi ESC**: Enterprise Secrets Management

## Clean Architecture Alignment

### 1. Domain Layer
The domain layer is completely technology-agnostic, containing only:
- Pure Python business entities (Call, Deal, Contact, User)
- Value objects (Money, Sentiment, CallParticipant)
- Business rules and logic

**Tech Stack Alignment**: No dependencies on any external technologies

### 2. Application Layer
The application layer defines interfaces (ports) that align with our tech stack:

#### Repository Interfaces
```python
# Designed to work with Modern Stack's specific features
class CallRepository(ABC):
    async def get_high_value_calls(self) -> List[Call]:
        # Can leverage Modern Stack's analytical capabilities
        pass
```

#### Service Interfaces
```python
# Designed for Portkey/OpenRouter integration
class AIService(ABC):
    async def analyze_sentiment(self, text: str) -> Sentiment:
        # Implementation will use Portkey gateway
        pass
```

### 3. Infrastructure Layer

#### Modern Stack Integration
```python
# backend/infrastructure/persistence/repositories/snowflake_call_repository.py
class Modern StackCallRepository(CallRepository):
    def __init__(self, snowflake_service: Modern StackCortexService):
        # Reuses existing Lambda GPU service
        self.snowflake = snowflake_service
```

- Leverages Lambda GPU for AI operations
- Uses native vector embeddings
- Optimized queries for analytical workloads

#### Portkey Integration (To Be Implemented)
```python
# backend/infrastructure/external/portkey_ai_service.py
class PortkeyAIService(AIService):
    def __init__(self, portkey_client: PortkeyClient):
        # Will integrate with existing Portkey configuration
        self.portkey = portkey_client
```

#### Estuary Flow Integration (To Be Implemented)
```python
# backend/infrastructure/external/estuary_data_service.py
class EstuaryDataService(DataStreamService):
    # Real-time data ingestion aligned with Estuary Flow
    pass
```

### 4. Deployment Architecture

#### Lambda Labs + Kubernetes
```yaml
# kubernetes/sophia-clean-arch-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: sophia-api
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: sophia-api
        image: sophia-ai:optimized
        resources:
          requests:
            nvidia.com/gpu: 1  # Lambda Labs GPU support
```

#### Docker Optimization
- Multi-stage builds reduce image size by 56-66%
- ML-specific optimizations for model loading
- GPU support for Lambda Labs infrastructure

#### Pulumi Infrastructure
```typescript
// infrastructure/pulumi/clean-architecture-stack.ts
import * as pulumi from "@pulumi/pulumi";
import * as k8s from "@pulumi/kubernetes";

// Lambda Labs Kubernetes cluster configuration
const cluster = new k8s.Provider("lambda-labs", {
    kubeconfig: config.requireSecret("lambdaLabsKubeconfig"),
});

// Deploy Clean Architecture services
const sophiaDeployment = new k8s.apps.v1.Deployment("sophia-api", {
    // Deployment configuration
}, { provider: cluster });
```

## Technology-Specific Considerations

### 1. Lambda GPU AI
- Repository implementations leverage Cortex functions
- Vector embeddings stored natively in Modern Stack
- Semantic search capabilities built into queries

### 2. Pulumi ESC Integration
- All secrets managed through Pulumi ESC
- No hardcoded credentials in any layer
- Automatic secret rotation support

### 3. Vercel Edge Functions
- Presentation layer can deploy to Vercel edge
- API routes compatible with serverless deployment
- Frontend integration seamless

### 4. Estuary Flow Pipelines
- Repository interfaces support streaming updates
- Event-driven architecture compatibility
- Real-time data synchronization

## Migration Strategy

### Phase 1: Core Implementation (Completed)
- Domain entities and value objects
- Application use cases and interfaces
- Basic infrastructure adapters

### Phase 2: Service Integration (Current)
- Modern Stack repository implementations
- Portkey AI service adapter
- Estuary Flow data streaming

### Phase 3: Deployment Optimization
- Kubernetes manifests for Lambda Labs
- Pulumi stack configuration
- CI/CD pipeline updates

## Benefits of This Approach

1. **Technology Flexibility**: Easy to swap implementations
2. **Testability**: Mock any external service
3. **Scalability**: Deploy on Lambda Labs Kubernetes
4. **Security**: Pulumi ESC integration throughout
5. **Performance**: Optimized for ML workloads

## Avoiding Common Pitfalls

### NOT Using AWS-Specific Services
- No AWS Lambda functions
- No AWS-specific APIs
- Focus on Lambda Labs infrastructure

### Proper Secret Management
- All secrets through Pulumi ESC
- No environment variables in code
- Automated rotation support

### ML Optimization
- GPU support for Lambda Labs
- Optimized Docker images
- Efficient model loading
