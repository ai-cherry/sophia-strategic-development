# 🚀 **Sophia AI - AI Coder Quick Start**

> **Get coding with Sophia AI in under 5 minutes!** This guide gets you from zero to productive AI-assisted development immediately.

## **⚡ 30-Second Setup**

```bash
# 1. Connect to Lambda Labs deployment
# Services are already running on 137.131.6.213

# 2. Verify Sophia AI is accessible
# Check with your team for the service endpoints

# 3. Start coding!
# In Cursor IDE, just type:
@sophia help me create a REST API
```

## **🎯 Essential MCP Servers for Coding**

| Server | Port | Purpose | Quick Command |
|--------|------|---------|---------------|
| **Sophia AI Intelligence** | 8092 | Primary AI coding assistant | `@sophia generate code` |
| **Codacy** | 3008 | Code quality & security | `@codacy analyze this` |
| **AI Memory** | 9000 | Remember decisions & patterns | `@memory what did we decide?` |
| **GitHub** | 3002 | Repository operations | `@github create PR` |
| **Docker** | 3003 | Container management | `@docker build and test` |

## **💬 Natural Language Commands**

### **Code Generation**
```bash
# Generate a complete feature
@sophia create a user authentication system with JWT

# Generate specific functions
@sophia write a Python function to validate email addresses

# Generate tests
@sophia create pytest tests for the UserService class

# Generate API endpoints
@sophia create REST endpoints for CRUD operations on products
```

### **Code Analysis & Improvement**
```bash
# Analyze code quality
@codacy check this file for issues

# Get improvement suggestions
@sophia how can I optimize this function?

# Security analysis
@sophia check this code for security vulnerabilities

# Architecture review
@sophia analyze the architecture of this module
```

### **Debugging & Problem Solving**
```bash
# Debug errors
@sophia help me fix this error: [paste error]

# Find similar issues
@memory have we seen this error before?

# Get explanations
@sophia explain how this algorithm works

# Performance optimization
@sophia optimize this code for better performance
```

## **🔄 Common Development Workflows**

### **1. Feature Development Workflow**
```bash
# Step 1: Generate initial code
@sophia create a notification service that sends emails and SMS

# Step 2: Analyze quality
@codacy analyze the notification service

# Step 3: Store the decision
@memory remember we chose SendGrid for email delivery

# Step 4: Create tests
@sophia generate comprehensive tests for NotificationService

# Step 5: Create PR
@github create pull request for notification feature
```

### **2. Bug Fixing Workflow**
```bash
# Step 1: Check if we've seen this before
@memory search for "connection timeout" errors

# Step 2: Get debugging help
@sophia debug: PostgreSQL connection keeps timing out

# Step 3: Implement fix
@sophia show me how to implement connection pooling

# Step 4: Verify fix
@codacy verify the connection pooling implementation
```

### **3. Code Review Workflow**
```bash
# Step 1: Get overview
@sophia summarize the changes in this PR

# Step 2: Security check
@codacy security scan for the new endpoints

# Step 3: Architecture review
@sophia does this follow our established patterns?

# Step 4: Suggest improvements
@sophia suggest improvements for this code
```

## **🧩 Integration Patterns**

### **Sophia + Codacy Integration**
```python
# Sophia generates code, Codacy validates it
# Example: Generate secure API endpoint

# 1. Generate with Sophia
"""
@sophia create a secure API endpoint for user profile updates
with input validation and rate limiting
"""

# 2. Auto-analyze with Codacy
"""
@codacy analyze security of the new endpoint
"""

# 3. Apply fixes if needed
"""
@sophia apply Codacy's security recommendations
"""
```

### **Sophia + AI Memory Integration**
```python
# Remember architectural decisions and patterns

# 1. Make a decision
"""
@sophia should we use Redis or Memcached for caching?
"""

# 2. Store the decision
"""
@memory remember: We chose Redis for caching because it supports
data persistence and has better data structure support
"""

# 3. Recall later
"""
@memory what caching solution did we choose and why?
"""
```

## **⚙️ Configuration Tips**

### **Cursor IDE Settings**
```json
// .cursor/settings.json
{
  "sophia.autoComplete": true,
  "sophia.contextAwareness": "high",
  "codacy.autoAnalyze": true,
  "codacy.fixOnSave": false,
  "aiMemory.autoStore": true
}
```

### **Performance Optimization**
```yaml
# For faster responses, use these model preferences:
fast_tasks:
  - code_completion: "claude-3-haiku"
  - simple_queries: "gpt-3.5-turbo"

quality_tasks:
  - architecture_design: "claude-3-sonnet"
  - complex_debugging: "gpt-4"
```

## **🚨 Troubleshooting**

### **Common Issues**

**Sophia not responding?**
```bash
# Check with team for service status
# Services run on Lambda Labs cloud infrastructure

# Contact DevOps if services are down
# All services are managed via Docker Swarm
```

**Codacy not analyzing?**
```bash
# Verify Codacy integration in Cursor settings
# Token is managed via Pulumi ESC (no local tokens)

# Check MCP server configuration
cat cursor_enhanced_mcp_config.json | grep codacy
```

**Memory not storing?**
```bash
# AI Memory runs on cloud infrastructure
# Check MCP configuration for correct endpoints

# Verify connection in Cursor logs
# View > Output > MCP Logs
```

## **📚 Quick Reference**

### **Most Used Commands**
| Task | Command |
|------|---------|
| Generate code | `@sophia generate [description]` |
| Fix error | `@sophia debug [error message]` |
| Analyze code | `@codacy analyze` |
| Remember decision | `@memory store [decision]` |
| Create PR | `@github create PR [title]` |

### **Keyboard Shortcuts**
| Action | Shortcut |
|--------|----------|
| Trigger Sophia | `Cmd+Shift+S` |
| Run Codacy analysis | `Cmd+Shift+C` |
| Search memories | `Cmd+Shift+M` |
| Quick fix | `Cmd+.` |

## **🎉 You're Ready!**

You now have everything you need to start AI-assisted development with Sophia. Remember:

1. **Natural language is key** - Just describe what you want
2. **Context matters** - Sophia understands your project
3. **Iterate quickly** - Generate, analyze, improve
4. **Learn patterns** - Sophia remembers what works

**Need more help?** Type `@sophia help` for context-aware assistance.

---

**Pro tip:** The more specific you are in your requests, the better Sophia's responses. Instead of "create a function", try "create a Python async function that fetches user data from PostgreSQL with error handling and caching".
