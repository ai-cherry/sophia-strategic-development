# 🤖 SOPHIA AI CODER REFERENCE
**Essential Documentation for Every AI Coder Working on Sophia AI**

---

## 📋 **QUICK REFERENCE CHECKLIST**

**Before writing any code, ensure you understand:**
- ✅ [Architecture Patterns](#🏗️-architecture-patterns)
- ✅ [Secret Management Rules](#🔐-secret-management-rules)
- ✅ [MCP Server Integration](#🔌-mcp-server-integration)
- ✅ [Agent Development Standards](#🤖-agent-development-standards)
- ✅ [Database Access Patterns](#🗄️-database-access-patterns)
- ✅ [Error Handling Requirements](#⚠️-error-handling-requirements)

---

## 🎯 **SOPHIA AI CONTEXT & MISSION**

### **What is Sophia AI?**
Sophia AI is Pay Ready's **central business intelligence nervous system** - a unified platform that transforms every piece of business data into actionable insights through advanced AI orchestration.

### **Core Architecture Philosophy**
- **Infrastructure as Code (IaC)**: Everything managed centrally via Pulumi ESC
- **Production-First**: No sandbox environments - direct production deployment
- **MCP-Driven**: Model Context Protocol servers for all integrations
- **Agent-Centric**: Specialized AI agents for different business functions
- **Security-First**: SOC2 compliant with comprehensive audit trails

### **Key Business Context**
- **Primary User**: Pay Ready executive team and operations
- **Data Sources**: Gong, HubSpot, Slack, Linear, GitHub, CoStar, Apollo.io
- **Output**: Executive dashboards, conversational intelligence, automated insights
- **Performance Requirements**: <200ms query response, 99.9% uptime

---

## 🏗️ **ARCHITECTURE PATTERNS**

### **1. Directory Structure (CRITICAL)**
```
sophia-main/
├── backend/
│   ├── agents/                    # AI agent implementations
│   │   ├── enhanced/             # Core business intelligence agents
│   │   └── specialized/          # Domain-specific agents
│   ├── api/                      # FastAPI route definitions
│   ├── core/                     # Core utilities and configuration
│   ├── infrastructure/           # IaC orchestration and adapters
│   ├── mcp/                      # MCP server implementations
│   ├── services/                 # Business logic services
│   └── workflows/                # LangGraph orchestration
├── frontend/                     # React dashboards
├── mcp-servers/                  # Standardized MCP servers
├── scripts/                      # Automation and deployment scripts
├── docs/                         # Comprehensive documentation
└── config/                       # Configuration files
```

### **2. Agent Inheritance Pattern (MANDATORY)**
```python
# CORRECT: Use standardized agent base class
from backend.agents.enhanced.base_agent import EnhancedAgent

class YourAgent(EnhancedAgent):
    def __init__(self):
        super().__init__(
            agent_name="your_agent",
            agent_type="business_intelligence",  # or specialized, infrastructure
            capabilities=["data_analysis", "insight_generation"]
        )

    async def process_request(self, request: dict) -> dict:
        # Your implementation here
        pass

# INCORRECT: Don't create agents from scratch
class BadAgent:  # ❌ Missing inheritance
    pass
```

### **3. MCP Server Pattern (REQUIRED)**
```python
# CORRECT: Use standardized MCP server base
from backend.mcp.base.standardized_mcp_server import StandardizedMCPServer

class YourMCPServer(StandardizedMCPServer):
    def __init__(self):
        super().__init__(
            server_name="your_service",
            port=9000,  # Use assigned port from mcp_ports.json
            tools=["tool1", "tool2"]
        )

    async def handle_tool_call(self, tool_name: str, arguments: dict):
        # Implementation here
        pass

# INCORRECT: Don't create MCP servers without base class
```

### **4. Database Access Pattern (CRITICAL)**
```python
# CORRECT: Use centralized database service
from backend.services.comprehensive_memory_service import ComprehensiveMemoryService

class YourService:
    def __init__(self):
        self.memory_service = ComprehensiveMemoryService()

    async def query_data(self, query: str):
        return await self.memory_service.semantic_search(query)

# INCORRECT: Don't create direct database connections
import snowflake.connector  # ❌ Don't do this
```

---

## 🔐 **SECRET MANAGEMENT RULES**

### **CRITICAL: Secret Management Flow**
```
GitHub Organization Secrets → Pulumi ESC → Environment Variables → Application Code
```

### **1. Reading Secrets (CORRECT)**
```python
import os

# CORRECT: Always use environment variables
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
SNOWFLAKE_ACCOUNT = os.getenv("SNOWFLAKE_ACCOUNT")
GONG_ACCESS_KEY = os.getenv("GONG_ACCESS_KEY")

# Validate secrets exist
if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY environment variable required")
```

### **2. Secret Management (INCORRECT)**
```python
# ❌ NEVER hardcode secrets
API_KEY = "sk-1234567890abcdef"  # NEVER DO THIS

# ❌ NEVER create alternative secret management
def load_secrets_from_file():  # DON'T CREATE THIS
    pass

# ❌ NEVER bypass Pulumi ESC
secrets = boto3.client('secretsmanager')  # DON'T DO THIS
```

### **3. Required Environment Variables**
```bash
# Core Platform
OPENROUTER_API_KEY=          # Primary LLM gateway
SNOWFLAKE_ACCOUNT=           # Data warehouse
SNOWFLAKE_USER=              # Database user
SNOWFLAKE_PASSWORD=          # Database password

# Data Sources
GONG_ACCESS_KEY=             # Sales call intelligence
GONG_CLIENT_SECRET=          # Gong authentication
SLACK_BOT_TOKEN=             # Slack integration
HUBSPOT_ACCESS_TOKEN=        # CRM integration
LINEAR_API_KEY=              # Project management

# Infrastructure
PULUMI_ACCESS_TOKEN=         # Infrastructure management
VERCEL_TOKEN=                # Frontend deployment
LAMBDA_LABS_API_KEY=         # Compute resources
```

---

## 🔌 **MCP SERVER INTEGRATION**

### **1. Available MCP Servers**
```json
{
  "ai_memory": "port 9000 - AI memory and vector search",
  "snowflake_admin": "port 9012 - Database administration",
  "gong_intelligence": "port 9001 - Sales call analysis",
  "hubspot_crm": "port 9002 - CRM data access",
  "slack_integration": "port 9003 - Team communication",
  "linear_projects": "port 9004 - Project management",
  "github_code": "port 9005 - Code repository access",
  "figma_design": "port 9006 - Design system integration"
}
```

### **2. MCP Client Usage Pattern**
```python
# CORRECT: Use centralized MCP client
from backend.mcp.mcp_client import MCPClient

class YourService:
    def __init__(self):
        self.mcp_client = MCPClient()

    async def get_sales_data(self):
        return await self.mcp_client.call_tool(
            server="gong_intelligence",
            tool="get_recent_calls",
            arguments={"days": 7}
        )

# INCORRECT: Don't create direct MCP connections
```

### **3. MCP Server Health Monitoring**
```python
# CORRECT: Always check server health
async def ensure_mcp_health(self):
    health_status = await self.mcp_client.health_check("ai_memory")
    if not health_status.get("healthy"):
        raise RuntimeError("AI Memory MCP server unavailable")
```

---

## 🤖 **AGENT DEVELOPMENT STANDARDS**

### **1. Agent Categories**
- **Enhanced Agents** (`backend/agents/enhanced/`): Core business intelligence
- **Specialized Agents** (`backend/agents/specialized/`): Domain-specific functionality
- **Infrastructure Agents** (`backend/infrastructure/`): System management

### **2. Agent Performance Requirements**
```python
# CRITICAL: Maintain <3μs instantiation time
class PerformantAgent(EnhancedAgent):
    def __init__(self):
        # Minimize initialization work
        super().__init__(agent_name="fast_agent")
        # Defer heavy operations to first use
        self._heavy_resource = None

    @property
    def heavy_resource(self):
        if self._heavy_resource is None:
            self._heavy_resource = self._initialize_heavy_resource()
        return self._heavy_resource
```

### **3. Agent Communication Pattern**
```python
# CORRECT: Use async/await for all agent operations
class YourAgent(EnhancedAgent):
    async def process_request(self, request: dict) -> dict:
        # Validate input
        if not self._validate_request(request):
            raise ValueError("Invalid request format")

        # Process with error handling
        try:
            result = await self._process_business_logic(request)
            return {"status": "success", "data": result}
        except Exception as e:
            self.logger.error(f"Processing failed: {e}")
            return {"status": "error", "message": str(e)}
```

---

## 🗄️ **DATABASE ACCESS PATTERNS**

### **1. Snowflake Access (CORRECT)**
```python
# CORRECT: Use ComprehensiveMemoryService
from backend.services.comprehensive_memory_service import ComprehensiveMemoryService

class DataService:
    def __init__(self):
        self.memory_service = ComprehensiveMemoryService()

    async def query_sales_data(self, filters: dict):
        query = """
        SELECT call_date, prospect_name, outcome
        FROM SOPHIA_AI_CORE.GONG_DATA.CALLS
        WHERE call_date >= %s
        """
        return await self.memory_service.execute_query(query, [filters['start_date']])
```

### **2. Vector Search Pattern**
```python
# CORRECT: Use semantic search capabilities
async def find_similar_content(self, query: str):
    return await self.memory_service.semantic_search(
        query=query,
        top_k=10,
        filters={"source": "gong_calls"}
    )
```

### **3. Data Ingestion Pattern**
```python
# CORRECT: Use standardized ingestion service
from backend.etl.enhanced_ingestion_service import EnhancedIngestionService

class DataIngestion:
    def __init__(self):
        self.ingestion_service = EnhancedIngestionService()

    async def ingest_new_data(self, source: str, data: list):
        return await self.ingestion_service.process_batch(source, data)
```

---

## ⚠️ **ERROR HANDLING REQUIREMENTS**

### **1. Standardized Error Handling**
```python
# CORRECT: Use consistent error handling
import logging
from typing import Optional

class YourService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    async def risky_operation(self) -> Optional[dict]:
        try:
            result = await self._perform_operation()
            return result
        except ConnectionError as e:
            self.logger.error(f"Connection failed: {e}")
            # Attempt retry logic
            return await self._retry_operation()
        except ValueError as e:
            self.logger.warning(f"Invalid input: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            raise  # Re-raise unexpected errors
```

### **2. Health Check Implementation**
```python
# REQUIRED: All services must implement health checks
async def health_check(self) -> dict:
    try:
        # Test critical dependencies
        await self._test_database_connection()
        await self._test_mcp_servers()

        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "dependencies": {
                "database": "connected",
                "mcp_servers": "operational"
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
```

---

## 🚀 **DEPLOYMENT & TESTING**

### **1. Local Development**
```bash
# Start all MCP servers
python scripts/run_all_mcp_servers.py

# Start backend API
uvicorn backend.app.fastapi_app:app --reload --port 8000

# Run health checks
python scripts/comprehensive_health_check.py
```

### **2. Testing Requirements**
```python
# REQUIRED: Unit tests for all new code
import pytest
from unittest.mock import AsyncMock

class TestYourService:
    @pytest.fixture
    async def service(self):
        return YourService()

    async def test_process_request_success(self, service):
        # Mock dependencies
        service.memory_service.semantic_search = AsyncMock(return_value=[])

        # Test functionality
        result = await service.process_request({"query": "test"})
        assert result["status"] == "success"
```

### **3. Performance Testing**
```python
# REQUIRED: Performance validation
import time

async def test_agent_instantiation_speed():
    start_time = time.perf_counter()
    agent = YourAgent()
    end_time = time.perf_counter()

    instantiation_time = (end_time - start_time) * 1_000_000  # microseconds
    assert instantiation_time < 3, f"Agent instantiation took {instantiation_time}μs (max: 3μs)"
```

---

## 📚 **ESSENTIAL DOCUMENTATION REFERENCES**

### **Must-Read Documents**
1. **[SOPHIA_AI_BEST_PRACTICES_GUIDE.md](SOPHIA_AI_BEST_PRACTICES_GUIDE.md)** - Development workflow
2. **[SECRET_MANAGEMENT_GUIDE.md](SECRET_MANAGEMENT_GUIDE.md)** - Pulumi ESC integration
3. **[MCP_AGENT_ARCHITECTURE_GUIDE.md](MCP_AGENT_ARCHITECTURE_GUIDE.md)** - MCP patterns
4. **[SOPHIA_AI_DATA_FLOW_ARCHITECTURE.md](SOPHIA_AI_DATA_FLOW_ARCHITECTURE.md)** - Data patterns

### **Architecture References**
- **[INFRASTRUCTURE_MANAGEMENT_ARCHITECTURE.md](INFRASTRUCTURE_MANAGEMENT_ARCHITECTURE.md)** - IaC patterns
- **[ENHANCED_ARCHITECTURE_RECOMMENDATIONS.md](ENHANCED_ARCHITECTURE_RECOMMENDATIONS.md)** - Best practices

### **Integration Guides**
- **[ESTUARY_INTEGRATION_GUIDE.md](ESTUARY_INTEGRATION_GUIDE.md)** - Data ingestion
- **[CURSOR_MCP_INTEGRATION_GUIDE.md](CURSOR_MCP_INTEGRATION_GUIDE.md)** - IDE integration

---

## 🔍 **CODE REVIEW CHECKLIST**

### **Before Submitting Code**
- [ ] Follows agent inheritance patterns
- [ ] Uses environment variables for secrets
- [ ] Implements proper error handling
- [ ] Includes health check endpoints
- [ ] Maintains <3μs agent instantiation
- [ ] Uses ComprehensiveMemoryService for database access
- [ ] Follows MCP server patterns
- [ ] Includes unit tests
- [ ] Updates documentation if needed
- [ ] Validates against performance requirements

### **Security Checklist**
- [ ] No hardcoded secrets or credentials
- [ ] Uses Pulumi ESC secret management flow
- [ ] Implements proper input validation
- [ ] Includes audit logging for sensitive operations
- [ ] Follows SOC2 compliance requirements

---

## 🎯 **COMMON MISTAKES TO AVOID**

### **❌ Architecture Violations**
```python
# DON'T: Create agents without inheritance
class BadAgent:  # Missing EnhancedAgent inheritance
    pass

# DON'T: Direct database connections
import snowflake.connector
conn = snowflake.connector.connect(...)  # Use ComprehensiveMemoryService instead

# DON'T: Hardcode configuration
API_URL = "https://api.example.com"  # Use environment variables
```

### **❌ Secret Management Violations**
```python
# DON'T: Hardcode secrets
API_KEY = "sk-1234567890"  # Use os.getenv()

# DON'T: Alternative secret management
with open('secrets.json') as f:  # Use Pulumi ESC flow
    secrets = json.load(f)
```

### **❌ Performance Violations**
```python
# DON'T: Heavy initialization
class SlowAgent(EnhancedAgent):
    def __init__(self):
        super().__init__()
        self.heavy_model = load_large_model()  # Defer to first use
```

### **❌ Tool Proliferation Violations**

**Key Principle:**
> **Only add new tools when there's a clear gap that existing tools cannot fill.**

```bash
# DON'T: Add redundant tools
"Let's add Airflow for ETL"  # We have Estuary
"Install LangChain"  # We use LangGraph
"Switch to pip"  # UV is 6x faster

# DON'T: Add tools for minor conveniences
"Add this logging framework"  # Python logging works fine
"Install this ORM"  # We have established patterns

# DO: Document clear gaps before adding
"Dependabot for security updates"  # Clear gap: automated security
"Grafana for visualization"  # Clear gap: no dashboards
```

**Before Adding Any Tool:**
1. Check if existing tools can solve it
2. Document the specific gap
3. Consider maintenance cost
4. Get approval for significant additions

---

## 🏆 **SUCCESS PATTERNS**

### **✅ Excellent Agent Implementation**
```python
from backend.agents.enhanced.base_agent import EnhancedAgent
from backend.services.comprehensive_memory_service import ComprehensiveMemoryService
import os
import logging

class SalesIntelligenceAgent(EnhancedAgent):
    def __init__(self):
        super().__init__(
            agent_name="sales_intelligence",
            agent_type="business_intelligence",
            capabilities=["call_analysis", "pipeline_insights"]
        )
        self.memory_service = ComprehensiveMemoryService()
        self.logger = logging.getLogger(__name__)

    async def process_request(self, request: dict) -> dict:
        try:
            # Validate input
            if not request.get("query"):
                raise ValueError("Query parameter required")

            # Process with semantic search
            results = await self.memory_service.semantic_search(
                query=request["query"],
                filters={"source": "gong_calls"}
            )

            return {
                "status": "success",
                "data": results,
                "agent": self.agent_name
            }

        except Exception as e:
            self.logger.error(f"Processing failed: {e}")
            return {
                "status": "error",
                "message": str(e),
                "agent": self.agent_name
            }

    async def health_check(self) -> dict:
        try:
            await self.memory_service.health_check()
            return {"status": "healthy", "agent": self.agent_name}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
```

---

## 📞 **GETTING HELP**

### **Documentation Issues**
- Check existing docs in `/docs/` directory
- Reference architecture guides for patterns
- Review best practices guide for workflows

### **Code Issues**
- Run comprehensive health checks
- Check MCP server status
- Validate environment variables
- Review error logs

### **Performance Issues**
- Profile agent instantiation time
- Check database query performance
- Monitor MCP server response times
- Validate memory usage patterns

---

**Remember: Sophia AI is a production-first, high-performance system. Every line of code should contribute to business intelligence and maintain our strict performance and security standards.**

---

*Last Updated: June 27, 2025*
*Version: 2.0*
*Status: Production Reference*
