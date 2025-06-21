# 🤖 CLAUDE MCP INTEGRATION COMMANDS FOR CURSOR IDE

## 🎯 **CLAUDE MCP SERVER ARCHITECTURE**

Your Sophia AI system includes multiple Claude MCP servers that enable natural language coding within Cursor IDE:

```
backend/mcp/
├── claude_mcp_server.py      # Core Claude AI integration
├── sophia_mcp_server.py      # Sophia AI orchestration
├── gong_mcp_server.py        # Gong.io business intelligence
├── vercel_mcp_server.py      # Frontend deployment
├── lambda_labs_mcp_server.py # Cloud compute management
└── slack_mcp_server.py       # Team notifications
```

## 🔧 **CLAUDE MCP ACTIVATION IN CURSOR**

### **1. MCP Configuration**

**File**: `mcp_config.json`
```json
{
  "mcpServers": {
    "claude-ai": {
      "command": "python",
      "args": ["backend/mcp/claude_mcp_server.py"],
      "env": {
        "ANTHROPIC_API_KEY": "${ANTHROPIC_API_KEY}"
      }
    },
    "sophia-orchestrator": {
      "command": "python", 
      "args": ["backend/mcp/sophia_mcp_server.py"],
      "env": {
        "ANTHROPIC_API_KEY": "${ANTHROPIC_API_KEY}",
        "PULUMI_ACCESS_TOKEN": "${PULUMI_ACCESS_TOKEN}",
        "LAMBDA_LABS_API_KEY": "${LAMBDA_LABS_API_KEY}"
      }
    }
  }
}
```

### **2. Cursor IDE Integration**

**File**: `.cursorrules`
```
# Claude MCP Integration Rules
- Use @claude for AI-powered code generation
- Use @sophia for infrastructure and deployment commands
- Prefer natural language over complex syntax
- Always validate generated code before execution
- Use context-aware suggestions for better results
```

## 💬 **CLAUDE MCP COMMAND CATEGORIES**

### **🔨 CODE GENERATION COMMANDS**

#### **Application Development:**
```bash
# FastAPI applications
@claude "Create FastAPI app with PostgreSQL, authentication, and CRUD operations"
@claude "Add rate limiting and security middleware to existing FastAPI app"
@claude "Generate OpenAPI documentation with examples"

# React frontend development
@claude "Build React dashboard with charts, tables, and real-time updates"
@claude "Create responsive navigation component with dark mode"
@claude "Add form validation with React Hook Form and Zod"

# Database operations
@claude "Design PostgreSQL schema for e-commerce platform"
@claude "Create SQLAlchemy models with relationships and validation"
@claude "Generate database migration scripts for schema changes"
```

#### **AI and ML Integration:**
```bash
# Claude AI integration
@claude "Add Claude AI chat interface to React application"
@claude "Create streaming response handler for Claude API"
@claude "Implement function calling with Claude for tool use"

# Vector databases and search
@claude "Integrate Pinecone vector search with embeddings"
@claude "Create semantic search with Weaviate and transformers"
@claude "Build RAG system with document chunking and retrieval"

# Data processing
@claude "Create ETL pipeline for processing CSV files"
@claude "Build real-time data streaming with WebSockets"
@claude "Generate data validation schemas with Pydantic"
```

### **🏗️ INFRASTRUCTURE AS CODE COMMANDS**

#### **Pulumi Infrastructure:**
```bash
# Cloud resource management
@claude "Generate Pulumi code for Lambda Labs GPU instances"
@claude "Create Pulumi stack for PostgreSQL with backups"
@claude "Build Pulumi program for Vercel deployment"

# Networking and security
@claude "Create VPC configuration with private subnets"
@claude "Generate security group rules for web application"
@claude "Build load balancer configuration with SSL"

# Monitoring and logging
@claude "Create Prometheus monitoring setup with Pulumi"
@claude "Generate log aggregation configuration"
@claude "Build alerting rules for infrastructure health"
```

#### **Secret Management:**
```bash
# Pulumi ESC integration
@claude "Create Pulumi ESC environment configuration"
@claude "Generate secret rotation automation scripts"
@claude "Build secret validation and health checks"

# GitHub integration
@claude "Sync GitHub organization secrets to Pulumi ESC"
@claude "Create GitHub Actions workflow for secret management"
@claude "Generate secret audit and compliance reports"
```

### **🔍 CODE ANALYSIS AND OPTIMIZATION**

#### **Security Analysis:**
```bash
# Vulnerability scanning
@claude "Analyze this code for security vulnerabilities"
@claude "Generate security headers for FastAPI application"
@claude "Create input validation and sanitization functions"

# Authentication and authorization
@claude "Add JWT authentication with refresh tokens"
@claude "Implement role-based access control (RBAC)"
@claude "Create OAuth2 integration with multiple providers"

# Data protection
@claude "Add encryption for sensitive data fields"
@claude "Implement secure password hashing with bcrypt"
@claude "Create data anonymization functions for GDPR"
```

#### **Performance Optimization:**
```bash
# Database optimization
@claude "Optimize database queries with proper indexing"
@claude "Add connection pooling and query caching"
@claude "Create database performance monitoring"

# API optimization
@claude "Add response caching with Redis"
@claude "Implement API rate limiting and throttling"
@claude "Create async processing with background tasks"

# Frontend optimization
@claude "Add code splitting and lazy loading to React app"
@claude "Optimize bundle size with tree shaking"
@claude "Implement service worker for offline functionality"
```

### **🧪 TESTING AND VALIDATION**

#### **Test Generation:**
```bash
# Unit testing
@claude "Generate comprehensive unit tests for this module"
@claude "Create test fixtures and mock data"
@claude "Add property-based testing with Hypothesis"

# Integration testing
@claude "Create API integration tests with pytest"
@claude "Generate database integration tests"
@claude "Build end-to-end tests with Playwright"

# Load testing
@claude "Create load testing scripts with Locust"
@claude "Generate performance benchmarks"
@claude "Build stress testing scenarios"
```

#### **Code Quality:**
```bash
# Code review automation
@claude "Analyze code quality and suggest improvements"
@claude "Generate linting configuration for Python/TypeScript"
@claude "Create pre-commit hooks for code quality"

# Documentation generation
@claude "Generate API documentation from code"
@claude "Create README with setup and usage instructions"
@claude "Build developer documentation with examples"
```

## 🎮 **ADVANCED CLAUDE MCP WORKFLOWS**

### **🚀 FULL-STACK DEVELOPMENT**

#### **Complete Application Generation:**
```bash
@claude "Create complete task management application with:
- FastAPI backend with PostgreSQL
- React frontend with TypeScript
- User authentication and authorization
- Real-time updates with WebSockets
- File upload and storage
- Email notifications
- Comprehensive testing suite
- Docker containerization
- CI/CD pipeline configuration"
```

#### **Microservices Architecture:**
```bash
@claude "Design microservices architecture for e-commerce:
- User service with authentication
- Product catalog service
- Order processing service
- Payment service with Stripe
- Notification service with email/SMS
- API gateway with rate limiting
- Service discovery and health checks
- Distributed logging and monitoring"
```

### **🤖 AI-POWERED DEVELOPMENT**

#### **Intelligent Code Generation:**
```bash
@claude "Analyze existing codebase and generate:
- Missing error handling for all functions
- Comprehensive logging throughout application
- Input validation for all API endpoints
- Database transaction management
- Caching strategies for performance
- Security improvements and hardening
- Documentation and type hints
- Automated testing coverage"
```

#### **Smart Refactoring:**
```bash
@claude "Refactor legacy application for modern standards:
- Convert to async/await patterns
- Implement dependency injection
- Add proper error handling
- Improve code organization and structure
- Update to latest framework versions
- Add type safety with TypeScript/mypy
- Implement design patterns
- Optimize for performance and scalability"
```

### **📊 BUSINESS INTELLIGENCE INTEGRATION**

#### **Data Pipeline Creation:**
```bash
@claude "Build comprehensive data pipeline:
- Extract data from Gong.io, HubSpot, Slack
- Transform and clean data with Pandas
- Load into Snowflake data warehouse
- Create real-time streaming with Estuary Flow
- Build analytics dashboard with Plotly
- Add automated reporting and alerts
- Implement data quality monitoring
- Create ML models for predictions"
```

#### **CRM and Sales Automation:**
```bash
@claude "Create sales automation system:
- Integrate Gong.io call analysis
- Sync with HubSpot CRM data
- Analyze call sentiment and outcomes
- Generate lead scoring algorithms
- Create automated follow-up workflows
- Build sales performance dashboards
- Add predictive analytics for deals
- Implement Slack notifications for alerts"
```

## 🔧 **CLAUDE MCP CONFIGURATION EXAMPLES**

### **Custom Tool Integration:**
```python
# backend/mcp/claude_mcp_server.py
@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="generate_fastapi_app",
            description="Generate complete FastAPI application",
            inputSchema={
                "type": "object",
                "properties": {
                    "app_name": {"type": "string"},
                    "features": {"type": "array", "items": {"type": "string"}},
                    "database": {"type": "string", "enum": ["postgresql", "mysql", "sqlite"]}
                }
            }
        ),
        types.Tool(
            name="create_react_component",
            description="Generate React component with TypeScript",
            inputSchema={
                "type": "object", 
                "properties": {
                    "component_name": {"type": "string"},
                    "props": {"type": "object"},
                    "styling": {"type": "string", "enum": ["css", "tailwind", "styled-components"]}
                }
            }
        )
    ]
```

### **Context-Aware Code Generation:**
```python
@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    if name == "generate_fastapi_app":
        # Analyze existing project structure
        project_context = analyze_project_structure()
        
        # Generate code based on context
        code = generate_fastapi_application(
            name=arguments["app_name"],
            features=arguments["features"],
            database=arguments["database"],
            context=project_context
        )
        
        return [types.TextContent(type="text", text=code)]
```

## 🎯 **CURSOR IDE INTEGRATION PATTERNS**

### **Chat Interface Commands:**
```bash
# Direct code generation
@claude "Create user authentication system"
@claude "Add error handling to this function"
@claude "Generate tests for this module"

# Context-aware suggestions
@claude "Based on the current file, suggest improvements"
@claude "Analyze this function and optimize performance"
@claude "Add proper typing to this Python code"

# Multi-file operations
@claude "Refactor this module across multiple files"
@claude "Create consistent error handling throughout project"
@claude "Add logging to all API endpoints"
```

### **Command Palette Integration:**
```bash
# Quick actions (Cmd+Shift+P)
"Claude: Generate Code"
"Claude: Analyze Security"
"Claude: Optimize Performance"
"Claude: Add Tests"
"Claude: Generate Documentation"
"Claude: Refactor Code"
```

### **Inline Code Assistance:**
```bash
# Highlight code and use commands
"Claude: Explain this code"
"Claude: Add error handling"
"Claude: Optimize this function"
"Claude: Generate tests for selection"
"Claude: Add type hints"
"Claude: Convert to async"
```

## 🚀 **GETTING STARTED WITH CLAUDE MCP**

### **1. Verify Claude MCP Setup:**
```bash
# Test Claude MCP server
python backend/mcp/claude_mcp_server.py --test

# Check Cursor IDE integration
# In Cursor: Cmd+Shift+P -> "MCP: List Servers"
```

### **2. Basic Command Testing:**
```bash
# In Cursor IDE chat
@claude "Generate a simple FastAPI hello world app"
@claude "Create a React component for user profile"
@claude "Add error handling to the current function"
```

### **3. Advanced Workflow Testing:**
```bash
# Complex multi-step generation
@claude "Create complete CRUD API with authentication, validation, and tests"
```

## 🎉 **CLAUDE MCP MASTERY**

You now have **AI-powered coding assistance** integrated directly into Cursor IDE:

- **🤖 Intelligent Code Generation**: Context-aware application development
- **🔍 Smart Analysis**: Security, performance, and quality optimization
- **🧪 Automated Testing**: Comprehensive test suite generation
- **📚 Documentation**: Automatic documentation and type hints
- **🔧 Refactoring**: Intelligent code improvement and modernization
- **🏗️ Architecture**: Full-stack application and microservices design

**Start with simple commands and build up to complex AI-assisted development workflows!**

