# 🧠 AI Memory MCP Server - Deployment Guide

## 🔐 **PERMANENT SECRET MANAGEMENT INTEGRATION**

**IMPORTANT**: The AI Memory MCP Server now uses Sophia AI's **PERMANENT GitHub Organization Secrets → Pulumi ESC** solution. No manual secret configuration is required.

### **✅ Automatic Configuration**
- ✅ All API keys automatically loaded from Pulumi ESC
- ✅ Pinecone credentials managed via GitHub organization
- ✅ Zero manual configuration required
- ✅ Enterprise-grade security

### **🔑 Secret Access Pattern**
```python
# AI Memory automatically accesses secrets
from backend.core.auto_esc_config import config

# All secrets automatically available
pinecone_key = config.pinecone_api_key
openai_key = config.openai_api_key
```

## 🚀 **Quick Deployment**

### **1. One-Time Setup**
```bash
# Clone and setup permanent solution
git clone https://github.com/ai-cherry/sophia-main.git
cd sophia-main
export PULUMI_ORG=scoobyjava-org
python scripts/setup_permanent_secrets_solution.py
```

### **2. Deploy AI Memory MCP Server**
```bash
# Test the permanent solution
python scripts/test_permanent_solution.py

# Start AI Memory MCP Server (automatically loads secrets)
python backend/mcp/ai_memory_mcp_server.py

# All integrations work immediately!
```

## Overview

The AI Memory MCP Server provides persistent memory capabilities for AI coding assistants, enabling them to remember previous conversations, decisions, and solutions across sessions.

## 🎯 Features

### Core Capabilities
- **Persistent Memory**: Store and retrieve conversation history
- **Semantic Search**: Find relevant past discussions using vector similarity
- **Auto-Discovery**: Automatically discover and register memory tools
- **Category Organization**: Organize memories by type (architecture, bug_solution, etc.)
- **Context Preservation**: Maintain rich context for better AI responses

### Integration Benefits
- **Cursor AI Integration**: Seamless integration with Cursor IDE
- **MCP Protocol**: Standard Model Context Protocol implementation
- **Vector Storage**: Pinecone-powered semantic search
- **Automatic Embedding**: SentenceTransformers for text encoding

## 🏗️ **Architecture with Permanent Secrets**

```
GitHub Organization Secrets (ai-cherry)
           ↓
    Pulumi ESC (automatic sync)
           ↓
    AI Memory MCP Server (automatic loading)
           ↓
    Pinecone Vector Database
           ↓
    Cursor AI (persistent memory)
```

### **Automatic Secret Loading**
```python
# backend/mcp/ai_memory_mcp_server.py
from backend.core.auto_esc_config import config

class AIMemoryMCPServer:
    def __init__(self):
        # Secrets automatically loaded from ESC
        self.pinecone_key = config.pinecone_api_key
        self.openai_key = config.openai_api_key
        # No manual configuration needed!
```

## 🛠️ Installation & Setup

### **Prerequisites (Automatically Handled)**
- ✅ Pinecone API key (automatically from GitHub org)
- ✅ Python 3.11+ (standard requirement)
- ✅ Required packages (auto-installed)

### **Installation Steps**
```bash
# 1. Install dependencies (if not already done)
pip install pinecone sentence-transformers mcp backoff

# 2. Initialize AI Memory MCP Server (automatic secret loading)
python backend/mcp/ai_memory_mcp_server.py --initialize

# 3. Test the integration
python scripts/test_ai_memory_deployment.py
```

### **MCP Configuration**
The AI Memory server is automatically configured in `mcp_config.json`:

```json
{
  "mcpServers": {
    "ai-memory": {
      "command": "python",
      "args": ["backend/mcp/ai_memory_mcp_server.py"],
      "env": {
        "PYTHONPATH": ".",
        "PULUMI_ORG": "scoobyjava-org"
      }
    }
  }
}
```

## 🎮 Usage

### **For AI Coders (Automatic)**
The AI Memory system works automatically with Cursor AI:

```
User: "I'm getting this error with Pinecone..."
AI: Let me check if we've solved similar issues before...
[AUTO] Call ai_memory.recall_memory("Pinecone error solutions")
[Reference past solutions and provide enhanced answer]
```

### For Developers

#### Manual Memory Management
```python
from backend.mcp.ai_memory_mcp_server import AIMemoryMCPServer

server = AIMemoryMCPServer()
await server.initialize_integration()

# Store a memory
result = await server._store_conversation({
    "conversation_text": "Important architectural decision...",
    "context": "API design discussion",
    "category": "architecture"
})

# Recall memories
memories = await server._recall_memory({
    "query": "API design patterns",
    "top_k": 5
})
```

## 🏗️ Architecture

### Components
1. **AI Memory MCP Server**: Core memory management
2. **Auto-Discovery System**: Automatic tool discovery
3. **Vector Storage**: Pinecone for semantic search
4. **Embedding Model**: SentenceTransformers for text encoding

### Data Flow
```
AI Coder → MCP Client → AI Memory Server → Pinecone → Search Results → AI Coder
```

### Storage Structure
- **Vector Index**: `sophia-ai-memory` in Pinecone
- **Embedding Dimension**: 384 (all-MiniLM-L6-v2)
- **Metadata**: Context, tags, category, timestamp

## 🔒 Security & Privacy

### Data Security
- All memories stored with metadata for context
- No sensitive credentials stored in memory
- Optional local-only mode (without Pinecone)

### Privacy Controls
- Memories can be deleted by ID
- Category and tag filtering for access control
- Automatic cleanup of old memories (configurable)

## 🚨 Troubleshooting

### Common Issues

#### 1. Import Errors
```bash
# Install missing dependencies
pip install pinecone sentence-transformers mcp backoff
```

#### 2. Pinecone Connection Issues (Automatic Resolution)
```bash
# Check automatic secret loading
python -c "from backend.core.auto_esc_config import config; print('Pinecone API Key loaded:', bool(config.pinecone_api_key))"

# Test connection
python -c "import pinecone; print('Pinecone available')"
```

#### 3. MCP Server Not Found
```bash
# Check MCP configuration
cat mcp_config.json | grep -A 10 "ai-memory"

# Restart MCP server
python backend/mcp/ai_memory_mcp_server.py --restart
```

#### 4. Secret Access Issues (NEW)
```bash
# Run permanent solution test
python scripts/test_permanent_solution.py

# Check ESC access
export PULUMI_ORG=scoobyjava-org
pulumi env open scoobyjava-org/default/sophia-ai-production

# Verify GitHub organization secrets
# Go to: https://github.com/ai-cherry/settings/secrets/actions
```

### Diagnostic Commands
```bash
# Test AI Memory deployment
python scripts/test_ai_memory_deployment.py

# Check MCP server health
curl http://localhost:8000/ai-memory/health

# Validate permanent solution
python scripts/test_permanent_solution.py
```

## 🔧 Advanced Configuration

### Custom Memory Categories
```python
MEMORY_CATEGORIES = [
    "architecture",
    "bug_solution", 
    "code_decision",
    "workflow",
    "performance",
    "security"
]
```

### Memory Retention Policy
```python
MEMORY_CONFIG = {
    "max_memories": 10000,
    "retention_days": 365,
    "auto_cleanup": True,
    "embedding_model": "all-MiniLM-L6-v2"
}
```

## 📊 Monitoring

### Health Checks
```bash
# Check AI Memory server status
curl http://localhost:8000/ai-memory/health

# Validate memory storage
python -c "
from backend.mcp.ai_memory_mcp_server import AIMemoryMCPServer
import asyncio
server = AIMemoryMCPServer()
print('Health:', asyncio.run(server.health_check()))
"
```

### Performance Metrics
- Memory storage latency
- Search query response time
- Vector index size
- Memory retrieval accuracy

## 🎯 **Success Indicators**

When AI Memory is working correctly:
- ✅ MCP server starts without credential errors
- ✅ Pinecone connection established automatically
- ✅ Memory storage and retrieval work seamlessly
- ✅ Cursor AI can access persistent memory
- ✅ No manual secret management required
- ✅ All tests pass: `python scripts/test_permanent_solution.py`

## 🔒 **Security Guarantee**

The permanent solution ensures:
- **Zero exposed credentials** in AI Memory configuration
- **Automatic secret synchronization** for Pinecone access
- **Enterprise-grade security** with encrypted storage
- **Comprehensive audit trail** for all memory operations
- **Zero manual intervention** required for secret management

**🎯 RESULT: AI MEMORY WITH PERMANENT SECRET MANAGEMENT - PERSISTENT INTELLIGENCE WITHOUT CREDENTIAL HASSLES!** 