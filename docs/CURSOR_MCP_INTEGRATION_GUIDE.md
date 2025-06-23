# 🚀 Cursor IDE MCP Integration Guide
## Enhanced @ai_memory and @codacy Automation

### 🎯 **OVERVIEW**
This guide explains how to leverage the enhanced MCP server integration in Cursor IDE for intelligent, context-aware development with automatic memory management and real-time code analysis.

## 🔧 **SETUP REQUIREMENTS**

### **1. MCP Servers Running**
Ensure all MCP servers are operational:
```bash
# Start the complete Sophia AI system
python start_sophia_complete.py

# Verify services are running
curl http://localhost:9000/health    # AI Memory
curl http://localhost:3008/health    # Codacy
curl http://localhost:3006/health    # Asana
curl http://localhost:3007/health    # Notion
```

### **2. Cursor Configuration**
Your `cursor_mcp_config.json` should include:
- AI Memory MCP Server (port 9000) with auto-triggers
- Codacy MCP Server (port 3008) with real-time analysis
- Auto-workflow triggers enabled
- Context awareness settings activated

### **3. Environment Setup**
```bash
# Required environment variables
export PULUMI_ORG=scoobyjava-org
export OPENAI_API_KEY=your_key      # For AI Memory embeddings
export PINECONE_API_KEY=your_key    # For vector search
```

## 🧠 **AI MEMORY INTEGRATION (@ai_memory)**

### **Automatic Storage Triggers**
The AI Memory MCP server automatically stores conversations when it detects:

#### **Architecture Discussions**
```
User: "Should we use microservices or monolith for the payment system?"
AI: [Automatically stores architectural decision with context]
Storage: Category="architecture", Tags=["payment-system", "microservices", "architecture-decision"]
```

#### **Bug Fixes and Solutions**
```
User: "Fixed the Redis connection timeout issue by increasing pool size"
AI: [Automatically stores bug solution with root cause analysis]
Storage: Category="bug_solution", Tags=["redis", "timeout", "connection-pool"]
```

#### **Code Pattern Explanations**
```
User: "Here's how we implement MCP server authentication..."
AI: [Automatically stores implementation pattern]
Storage: Category="code_decision", Tags=["mcp", "authentication", "implementation"]
```

### **Smart Recall Commands**

#### **Context-Aware Retrieval**
```bash
# In Cursor IDE chat:
@ai_memory "How did we handle database connections in previous MCP servers?"

# Automatic behavior:
# 1. Analyzes current file context
# 2. Searches for relevant patterns
# 3. Returns ranked results with relevance scores
# 4. Includes file-specific context if available
```

#### **File-Specific Memory**
```bash
# When working on backend/mcp/new_server.py:
@ai_memory "Show me MCP server patterns"

# Returns:
# - Previous MCP server implementations
# - Authentication patterns used in this project
# - Error handling approaches from similar files
# - Performance optimizations for MCP servers
```

## 🔍 **CODACY INTEGRATION (@codacy)**

### **Real-time Code Analysis**

#### **Automatic File Analysis**
```bash
# Triggered on file save automatically:
# 1. Security vulnerability scanning
# 2. Code complexity analysis
# 3. Style compliance checking
# 4. Performance pattern detection
```

#### **Manual Analysis Commands**
```bash
# In Cursor IDE:
@codacy "Analyze this function for security issues"
@codacy "Check code quality of current file"
@codacy "Scan for vulnerabilities in this module"
```

## 🔄 **AUTOMATED WORKFLOWS**

### **Workflow 1: Architecture Discussion**
```
Trigger: User discusses system design
Automatic Actions:
1. @ai_memory.auto_store_context (categorized as "architecture")
2. @codacy.analyze_code (if code examples provided)
3. Context linkage to current project files
4. Proactive suggestion of related past decisions
```

### **Workflow 2: Bug Fix Implementation**
```
Trigger: User implements bug fix
Automatic Actions:
1. @codacy.security_scan (check for new vulnerabilities)
2. @ai_memory.store_conversation (category="bug_solution")
3. @ai_memory.recall_memory (similar bug patterns)
4. Code quality analysis with fix suggestions
```

## 🎯 **NATURAL LANGUAGE COMMANDS**

### **Memory Operations**
```bash
# Architecture decisions:
"Remember this database schema decision"
"What did we decide about API versioning?"
"Show me similar architectural patterns"

# Bug fixes:
"Store this Redis timeout solution"
"Find similar connection issues we've solved"
"Remember this performance optimization"
```

### **Code Quality Operations**
```bash
# Security analysis:
"Scan this code for security vulnerabilities"
"Check for SQL injection risks"
"Analyze authentication security"

# Quality assessment:
"Review code quality of this function"
"Check compliance with our coding standards"
"Analyze function complexity"
```

## 📊 **SUCCESS METRICS**

Track your enhanced development experience:

### **Productivity Gains**
- Reduced time to find relevant past decisions
- Faster implementation using proven patterns
- Proactive security issue prevention
- Automated code quality improvements

### **Knowledge Management**
- Comprehensive development context preservation
- Team knowledge sharing through stored memories
- Architectural decision history and rationale
- Bug solution patterns for faster resolution

---

## 🚀 **GETTING STARTED**

1. **Start the System**: `python start_sophia_complete.py`
2. **Verify Health**: Check all MCP servers are running
3. **Open Cursor IDE**: Start with any Python file in the project
4. **Test Integration**: Try `@ai_memory "test recall"` and `@codacy "analyze current file"`
5. **Begin Development**: The system will automatically learn and assist

Your Cursor IDE is now equipped with intelligent memory and real-time code analysis capabilities!
