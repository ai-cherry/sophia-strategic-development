# AI Memory V2 MCP Server

Production-ready semantic memory storage and retrieval system for the Sophia AI platform.

## 🚀 Features

- ✅ **Semantic Search**: Vector-based similarity search using OpenAI embeddings
- ✅ **Auto-Categorization**: Intelligent categorization of memories
- ✅ **Duplicate Detection**: Prevent storing duplicate memories
- ✅ **Bulk Operations**: Store multiple memories efficiently
- ✅ **Advanced Filtering**: Search by category, tags, user, and date range
- ✅ **PostgreSQL + pgvector**: Scalable vector storage
- ✅ **Prometheus Metrics**: Production monitoring
- ✅ **Health Checks**: Comprehensive health monitoring
- ✅ **Async/Await**: High-performance architecture

## 📋 Prerequisites

- PostgreSQL 15+ with pgvector extension
- Python 3.11+
- OpenAI API key (for embeddings)
- Docker (optional)

## 🔧 Configuration

### Environment Variables

```bash
# Server Configuration
AI_MEMORY_V2_PORT=9001
AI_MEMORY_V2_LOG_LEVEL=INFO

# Database Configuration
AI_MEMORY_V2_DB_DSN=postgresql+asyncpg://user:pass@localhost:5432/ai_memory
AI_MEMORY_V2_DB_POOL_MIN=1
AI_MEMORY_V2_DB_POOL_MAX=5

# OpenAI Configuration
OPENAI_API_KEY=sk-your-openai-key
AI_MEMORY_V2_EMBEDDING_MODEL=text-embedding-ada-002
AI_MEMORY_V2_EMBEDDING_DIMENSION=1536

# Memory Settings
AI_MEMORY_V2_DEFAULT_SEARCH_LIMIT=10
AI_MEMORY_V2_SIMILARITY_THRESHOLD=0.7
AI_MEMORY_V2_MAX_MEMORY_SIZE=10000

# Feature Flags
AI_MEMORY_V2_ENABLE_AUTO_CATEGORIZATION=true
AI_MEMORY_V2_ENABLE_DUPLICATE_DETECTION=true
AI_MEMORY_V2_ENABLE_METRICS=true
```

## 🚀 Quick Start

### Local Development

1. **Install dependencies**:
```bash
cd infrastructure/mcp_servers/ai_memory_v2
pip install -r requirements.txt
```

2. **Set up PostgreSQL with pgvector**:
```sql
CREATE DATABASE ai_memory;
\c ai_memory;
CREATE EXTENSION vector;
```

3. **Configure environment**:
```bash
cp .env.example .env
# Edit .env with your settings
```

4. **Run the server**:
```bash
python -m infrastructure.mcp_servers.ai_memory_v2.server
```

### Docker Deployment

```bash
# Build and run with docker-compose
docker-compose up --build

# Server will be available at http://localhost:9001
```

## 📚 API Documentation

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check endpoint |
| GET | `/capabilities` | Server capabilities and settings |
| GET | `/metrics` | Prometheus metrics |
| POST | `/api/memory` | Store a new memory |
| POST | `/api/memory/bulk` | Store multiple memories |
| POST | `/api/search` | Search memories |
| GET | `/api/memory/{id}` | Get specific memory |
| PUT | `/api/memory/{id}` | Update memory |
| DELETE | `/api/memory/{id}` | Delete memory |
| GET | `/api/stats` | Memory statistics |
| GET | `/docs` | OpenAPI documentation |

### Example Usage

#### Store a Memory
```bash
curl -X POST http://localhost:9001/api/memory \
  -H "Content-Type: application/json" \
  -d '{
    "content": "The Sophia AI platform uses pgvector for semantic search",
    "category": "technical",
    "tags": ["sophia", "pgvector", "search"],
    "metadata": {"importance": "high"}
  }'
```

#### Search Memories
```bash
curl -X POST http://localhost:9001/api/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How does Sophia handle semantic search?",
    "limit": 5,
    "threshold": 0.7,
    "categories": ["technical"]
  }'
```

#### Bulk Store
```bash
curl -X POST http://localhost:9001/api/memory/bulk \
  -H "Content-Type: application/json" \
  -d '{
    "memories": [
      {"content": "Memory 1", "category": "general"},
      {"content": "Memory 2", "category": "technical"}
    ],
    "skip_duplicates": true
  }'
```

## 🏗️ Architecture

### Data Flow
```
User Request → FastAPI → Handler → OpenAI Embeddings
                ↓                          ↓
            PostgreSQL ← pgvector ← Vector Storage
```

### Memory Categories
- `general` - General purpose memories
- `technical` - Technical documentation and code
- `business` - Business insights and metrics
- `personal` - Personal notes and preferences
- `project` - Project-specific information
- `learning` - Learning resources and notes

### Database Schema
```sql
CREATE TABLE memory_entries (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    embedding vector(1536),
    category VARCHAR(50) DEFAULT 'general',
    metadata JSONB DEFAULT '{}',
    tags TEXT[] DEFAULT '{}',
    source VARCHAR(100),
    user_id VARCHAR(100),
    content_hash VARCHAR(64),
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);

-- Indexes for performance
CREATE INDEX idx_memory_embedding ON memory_entries 
USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX idx_memory_category ON memory_entries (category);
CREATE INDEX idx_memory_user ON memory_entries (user_id);
CREATE INDEX idx_memory_created ON memory_entries (created_at);
CREATE INDEX idx_memory_hash ON memory_entries (content_hash);
```

## 🧪 Testing

```bash
# Run unit tests
pytest tests/unit -v

# Run integration tests
pytest tests/integration -v

# Generate coverage report
pytest --cov=. --cov-report=html
open htmlcov/index.html
```

## 📊 Monitoring

### Prometheus Metrics

- `ai_memory_operations_total{operation}` - Total operations by type
- `ai_memory_search_duration_seconds` - Search latency histogram
- `ai_memory_embedding_duration_seconds` - Embedding generation time
- `ai_memory_storage_size_bytes` - Total storage size

### Health Check Response
```json
{
  "status": "healthy",
  "server": "ai_memory_v2",
  "version": "2.0.0",
  "embedding_enabled": true,
  "database": "connected",
  "total_memories": 1234
}
```

## 🚀 Production Deployment

### Lambda Labs Deployment

```bash
# Build and push image
docker build -t scoobyjava15/ai-memory-v2:latest .
docker push scoobyjava15/ai-memory-v2:latest

# Deploy with Docker Swarm
docker stack deploy -c docker-compose.production.yml ai-memory-v2
```

### Performance Tuning

1. **PostgreSQL Configuration**:
```sql
-- Increase work_mem for vector operations
ALTER SYSTEM SET work_mem = '256MB';

-- Configure shared_buffers
ALTER SYSTEM SET shared_buffers = '2GB';

-- Optimize for SSD
ALTER SYSTEM SET random_page_cost = 1.1;
```

2. **pgvector Optimization**:
```sql
-- Adjust IVFFlat lists based on data size
-- For 1M vectors, use ~1000 lists
CREATE INDEX idx_memory_embedding ON memory_entries 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 1000);
```

3. **Connection Pooling**:
- Adjust `AI_MEMORY_V2_DB_POOL_MIN` and `AI_MEMORY_V2_DB_POOL_MAX`
- Monitor connection usage via metrics

## 🔒 Security

- API key authentication (implement as needed)
- Input validation and sanitization
- SQL injection prevention via parameterized queries
- Rate limiting ready (implement as needed)

## 📝 License

Proprietary - Sophia AI Platform
