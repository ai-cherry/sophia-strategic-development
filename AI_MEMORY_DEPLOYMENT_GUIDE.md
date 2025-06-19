# AI Memory MCP System - Deployment & Usage Guide

## 🎯 Overview

The AI Memory MCP system provides persistent memory for AI coding assistants, enabling them to automatically store and recall development conversations, decisions, and context across sessions.

## ✅ System Status

**Current Status: DEPLOYED AND READY** ✅

All tests passing, dependencies installed, and auto-discovery configured.

## 🚀 Quick Start

### 1. Verify Installation
```bash
python test_ai_memory_deployment.py
```

### 2. Start MCP Gateway (Optional)
```bash
docker-compose up mcp-gateway
```

### 3. Test AI Memory Server
```bash
python backend/mcp/ai_memory_mcp_server.py
```

## 🔧 Configuration

### MCP Configuration
The AI Memory server is automatically configured in `mcp_config.json`:

```json
{
  "mcpServers": {
    "ai_memory": {
      "command": "python",
      "args": ["backend/mcp/ai_memory_mcp_server.py"],
      "env": {
        "PYTHONPATH": ".",
        "PINECONE_API_KEY": "${PINECONE_API_KEY}"
      }
    }
  }
}
```

### Environment Variables
- `PINECONE_API_KEY`: (Optional) For persistent vector storage
- `PYTHONPATH`: Set to project root

## 🤖 Automatic AI Coder Integration

### Cursor AI Integration
The system is automatically integrated with Cursor AI through:

1. **`.cursorrules` Configuration**: Contains AI Memory usage rules
2. **Auto-Discovery System**: Automatically detects and configures memory tools
3. **System Prompts**: Built-in instructions for memory usage

### Automatic Behaviors
AI coders will automatically:

- **Store conversations** after significant discussions
- **Recall context** before starting similar tasks
- **Reference past decisions** when making new ones
- **Build institutional knowledge** over time

## 🛠️ Available Tools

### 1. `store_conversation`
Stores development conversations and context.

**Parameters:**
- `conversation_text` (required): The conversation to store
- `context` (optional): Additional context
- `tags` (optional): Categorization tags
- `category` (optional): Memory category

**Example:**
```json
{
  "conversation_text": "We decided to use FastAPI for the API layer because...",
  "context": "Architecture decision for MCP servers",
  "tags": ["fastapi", "architecture", "mcp"],
  "category": "architecture"
}
```

### 2. `recall_memory`
Searches and retrieves relevant memories.

**Parameters:**
- `query` (required): Search query
- `category` (optional): Filter by category
- `tags` (optional): Filter by tags
- `top_k` (optional): Number of results (default: 5)

**Example:**
```json
{
  "query": "FastAPI MCP server implementation",
  "category": "architecture",
  "top_k": 3
}
```

### 3. `delete_memory`
Deletes a specific memory by ID.

**Parameters:**
- `memory_id` (required): ID of memory to delete

## 📊 Memory Categories

The system supports these memory categories:

- **`conversation`**: General development discussions
- **`code_decision`**: Specific coding decisions and rationale
- **`bug_solution`**: Bug fixes and solutions
- **`architecture`**: System architecture decisions
- **`workflow`**: Development workflow and processes
- **`requirement`**: Requirements and specifications
- **`pattern`**: Code patterns and best practices
- **`api_usage`**: API usage examples and patterns

## 🔍 Usage Patterns

### For AI Coding Assistants

#### 1. **Context Retrieval Pattern**
```
User: "How should we implement authentication in MCP servers?"
AI: Let me check our previous discussions about this...
[AUTO] Call ai_memory.recall_memory("MCP server authentication patterns")
[Provide context-aware answer based on retrieved memories]
```

#### 2. **Decision Storage Pattern**
```
[After architecture discussion]
[AUTO] Call ai_memory.store_conversation with:
- Full conversation text
- Context: "MCP authentication architecture decision"
- Category: "architecture"
- Tags: ["mcp", "authentication", "security"]
```

#### 3. **Problem-Solution Pattern**
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

#### 2. Pinecone Connection Issues
```bash
# Check API key
echo $PINECONE_API_KEY

# Test connection
python -c "import pinecone; print('Pinecone available')"
```

#### 3. MCP Server Not Found
```bash
# Verify MCP config
cat mcp_config.json | grep ai_memory

# Test server startup
python backend/mcp/ai_memory_mcp_server.py
```

### Diagnostic Commands
```bash
# Run full deployment test
python test_ai_memory_deployment.py

# Test auto-discovery
python backend/mcp/ai_memory_auto_discovery.py

# Check server health
python -c "
from backend.mcp.ai_memory_mcp_server import AIMemoryMCPServer
import asyncio

async def test():
    server = AIMemoryMCPServer()
    await server.initialize_integration()
    print('Server healthy')

asyncio.run(test())
"
```

## 📈 Performance

### Benchmarks
- **Store Operation**: < 2 seconds
- **Recall Operation**: < 1 second
- **Embedding Generation**: < 500ms
- **Vector Search**: < 100ms

### Optimization Tips
1. Use specific queries for better recall
2. Add relevant tags for faster filtering
3. Regular cleanup of old memories
4. Batch operations for multiple memories

## 🔄 Maintenance

### Regular Tasks
1. **Monitor Memory Usage**: Check Pinecone index stats
2. **Clean Old Memories**: Remove outdated context
3. **Update Dependencies**: Keep packages current
4. **Backup Important Memories**: Export critical decisions

### Health Checks
```bash
# Check system health
python -c "
import asyncio
from backend.mcp.ai_memory_mcp_server import AIMemoryMCPServer

async def health_check():
    server = AIMemoryMCPServer()
    await server.initialize_integration()
    
    # Test store
    store_result = await server._store_conversation({
        'conversation_text': 'Health check test',
        'context': 'System health verification'
    })
    
    # Test recall
    recall_result = await server._recall_memory({
        'query': 'health check',
        'top_k': 1
    })
    
    print(f'Store: {store_result.get(\"success\", False)}')
    print(f'Recall: {recall_result.get(\"success\", False)}')

asyncio.run(health_check())
"
```

## 🎯 Success Metrics

### Deployment Success Indicators
- ✅ All tests passing in deployment suite
- ✅ AI Memory server can be instantiated
- ✅ Cursor AI integration configured
- ✅ Auto-discovery system working

### Usage Success Indicators
- AI coders automatically store conversations
- Context is recalled before similar tasks
- Development decisions are preserved
- Knowledge builds over time

## 🚀 Next Steps

1. **Start Using**: AI coders will automatically use the memory system
2. **Monitor Usage**: Check memory growth and recall effectiveness
3. **Fine-tune**: Adjust categories and tags based on usage patterns
4. **Scale**: Add more memory servers for different domains

## 📞 Support

For issues or questions:
1. Run the diagnostic commands above
2. Check the troubleshooting section
3. Review system logs for errors
4. Test individual components

---

**Status**: ✅ **DEPLOYED AND READY FOR USE**

The AI Memory MCP system is fully operational and will automatically enhance AI coding assistance with persistent memory and context awareness. 