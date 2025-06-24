# 🏔️ **Snowflake Admin Agent**
## Natural Language Interface for Snowflake Administration

The Snowflake Admin Agent provides a sophisticated natural language interface for Snowflake database administration tasks, powered by LangChain's SQL Agent and integrated into Sophia AI's unified chat system.

---

## **🎯 Overview**

This agent enables users to perform Snowflake administration tasks using natural language commands through the Sophia AI chat interface. It supports multi-environment operations (DEV/STG/PROD) with appropriate security safeguards and confirmation workflows for potentially destructive operations.

### **Key Features**

- **Natural Language Processing**: Convert plain English requests into Snowflake SQL commands
- **Multi-Environment Support**: Target DEV, STG, or PROD environments with environment-specific security controls
- **Safety First**: Automatic detection of dangerous operations with mandatory confirmation workflows
- **LangChain Integration**: Powered by LangChain's create_sql_agent for robust SQL generation
- **Audit Trail**: Complete logging of all operations for compliance and debugging
- **Chat Integration**: Seamlessly integrated into Sophia AI's unified chat interface

---

## **🏗️ Architecture**

```
User Query → Intent Classifier → Snowflake Admin Agent → LangChain SQL Agent → Snowflake
     ↓              ↓                    ↓                     ↓               ↓
Natural Language  Admin Intent     Environment Router    SQL Generation   Execution
Processing        Detection        & Security Check     & Validation      & Results
```

### **Core Components**

1. **SnowflakeAdminAgent**: Main agent class with LangChain SQL agent integration
2. **SnowflakeAdminChatIntegration**: Chat interface integration layer
3. **SnowflakeAdminMCPServer**: MCP server for hosting the agent
4. **Intent Classification**: Smart detection of admin-related queries
5. **Security Framework**: Multi-layer security with confirmation workflows

---

## **🚀 Quick Start**

### **1. Installation**

```bash
# Install required dependencies
pip install langchain langchain-community snowflake-connector-python openai

# Or use the requirements file
pip install -r mcp-servers/snowflake_admin/requirements.txt
```

### **2. Configuration**

Set up environment variables in Pulumi ESC:

```bash
# Development Environment
export SNOWFLAKE_DEV_ACCOUNT="your-dev-account"
export SNOWFLAKE_DEV_USER="SOPHIA_SNOWFLAKE_ADMIN_BOT_USER"
export SNOWFLAKE_DEV_PAT="your-dev-pat"
export SNOWFLAKE_DEV_WAREHOUSE="DEV_ADMIN_WH"
export SNOWFLAKE_DEV_DATABASE="SOPHIA_AI_DEV"
export SNOWFLAKE_DEV_SCHEMA="ADMIN"
export SNOWFLAKE_DEV_ROLE="ROLE_SOPHIA_SNOWFLAKE_ADMIN_BOT_DEV"

# Staging Environment
export SNOWFLAKE_STG_ACCOUNT="your-stg-account"
export SNOWFLAKE_STG_USER="SOPHIA_SNOWFLAKE_ADMIN_BOT_USER"
export SNOWFLAKE_STG_PAT="your-stg-pat"
# ... similar for STG

# Production Environment (read-only recommended)
export SNOWFLAKE_PROD_ACCOUNT="your-prod-account"
export SNOWFLAKE_PROD_USER="SOPHIA_SNOWFLAKE_ADMIN_BOT_USER"
export SNOWFLAKE_PROD_PAT="your-prod-pat"
# ... similar for PROD
```

### **3. Basic Usage**

```python
from backend.agents.specialized.snowflake_admin_agent import execute_snowflake_admin_task

# Execute a simple admin task
response = await execute_snowflake_admin_task(
    "Create a new schema called MARKETING_STAGE",
    target_environment="dev"
)

print(response.message)
```

### **4. Chat Integration**

```python
from backend.services.snowflake_admin_chat_integration import process_snowflake_admin_query

# Process through chat interface
response = await process_snowflake_admin_query(
    "Show all warehouses in development environment",
    user_id="admin_user"
)
```

---

## **💬 Natural Language Examples**

### **Schema Management**
```
✅ "Create a new schema called MARKETING_STAGE"
✅ "Show all schemas in the current database"
✅ "Describe the schema SALES_DATA"
✅ "Grant USAGE on schema ANALYTICS to role DATA_ANALYST"
```

### **Warehouse Management**
```
✅ "Create a warehouse called DEV_WH with size XSMALL"
✅ "Show all warehouses and their status"
✅ "Alter warehouse COMPUTE_WH to auto suspend after 60 seconds"
✅ "Grant USAGE on warehouse ANALYTICS_WH to role ANALYST"
```

### **Role and User Management**
```
✅ "Create a new role called DATA_SCIENTIST"
✅ "Show all roles in the account"
✅ "Grant role DEVELOPER to user john.doe@company.com"
✅ "Show grants for role ANALYST"
```

### **Object Inspection**
```
✅ "Show all tables in schema SALES_DATA"
✅ "Describe table CUSTOMERS"
✅ "Show the DDL for table ORDERS"
✅ "List all columns in table PRODUCTS with their data types"
```

### **Environment Targeting**
```
✅ "Create schema TESTING in dev environment"
✅ "Show warehouses in production"
✅ "List roles in staging environment"
```

---

## **🛡️ Security Framework**

### **Multi-Layer Security**

1. **Environment Isolation**: Separate credentials and permissions per environment
2. **PAT Authentication**: Secure token-based authentication (preferred over passwords)
3. **Dangerous Operation Detection**: Automatic identification of risky SQL commands
4. **Confirmation Workflows**: Mandatory confirmation for destructive operations
5. **Audit Logging**: Complete operation logging for compliance

### **Dangerous Operations Requiring Confirmation**

- `DROP` statements (tables, schemas, databases, warehouses, users, roles)
- `TRUNCATE TABLE` operations
- `ALTER ACCOUNT` commands
- `DELETE` and `UPDATE` statements
- Granting `ACCOUNTADMIN` or `SECURITYADMIN` roles
- Password changes for users

### **Environment-Specific Restrictions**

| Environment | Destructive Ops | Confirmation Required | Max Execution Time |
|-------------|----------------|----------------------|-------------------|
| **DEV**     | ✅ Allowed     | ✅ Required          | 60 seconds        |
| **STG**     | ⚠️ Limited     | ✅ Required          | 30 seconds        |
| **PROD**    | ❌ Blocked     | ✅ Required          | 15 seconds        |

---

## **🔧 Configuration**

### **Service User Setup**

Create a dedicated service user in Snowflake:

```sql
-- Create service user
CREATE USER SOPHIA_SNOWFLAKE_ADMIN_BOT_USER
  PASSWORD = 'secure_password'
  DEFAULT_ROLE = 'ROLE_SOPHIA_SNOWFLAKE_ADMIN_BOT_DEV'
  DEFAULT_WAREHOUSE = 'DEV_ADMIN_WH'
  COMMENT = 'Service user for Sophia AI Snowflake administration';

-- Create roles per environment
CREATE ROLE ROLE_SOPHIA_SNOWFLAKE_ADMIN_BOT_DEV;
CREATE ROLE ROLE_SOPHIA_SNOWFLAKE_ADMIN_BOT_STG;
CREATE ROLE ROLE_SOPHIA_SNOWFLAKE_ADMIN_BOT_PROD;

-- Grant roles to service user
GRANT ROLE ROLE_SOPHIA_SNOWFLAKE_ADMIN_BOT_DEV TO USER SOPHIA_SNOWFLAKE_ADMIN_BOT_USER;
GRANT ROLE ROLE_SOPHIA_SNOWFLAKE_ADMIN_BOT_STG TO USER SOPHIA_SNOWFLAKE_ADMIN_BOT_USER;
GRANT ROLE ROLE_SOPHIA_SNOWFLAKE_ADMIN_BOT_PROD TO USER SOPHIA_SNOWFLAKE_ADMIN_BOT_USER;
```

### **PAT (Programmatic Access Token) Setup**

1. **Generate PAT in Snowflake UI**:
   - Go to Account → Security → API Authentication
   - Create new token for `SOPHIA_SNOWFLAKE_ADMIN_BOT_USER`
   - Set appropriate expiration and scope

2. **Store PAT in Pulumi ESC**:
   ```bash
   pulumi config set --secret snowflake_dev_pat "your-dev-pat-token"
   ```

### **Permission Configuration**

```sql
-- DEV Environment Permissions
USE ROLE ACCOUNTADMIN;

GRANT USAGE ON WAREHOUSE DEV_ADMIN_WH TO ROLE ROLE_SOPHIA_SNOWFLAKE_ADMIN_BOT_DEV;
GRANT USAGE ON DATABASE SOPHIA_AI_DEV TO ROLE ROLE_SOPHIA_SNOWFLAKE_ADMIN_BOT_DEV;
GRANT CREATE SCHEMA ON DATABASE SOPHIA_AI_DEV TO ROLE ROLE_SOPHIA_SNOWFLAKE_ADMIN_BOT_DEV;
GRANT ALL ON SCHEMA SOPHIA_AI_DEV.* TO ROLE ROLE_SOPHIA_SNOWFLAKE_ADMIN_BOT_DEV;
GRANT MONITOR ON ACCOUNT TO ROLE ROLE_SOPHIA_SNOWFLAKE_ADMIN_BOT_DEV;

-- STG Environment Permissions (more restricted)
GRANT USAGE ON WAREHOUSE STG_ADMIN_WH TO ROLE ROLE_SOPHIA_SNOWFLAKE_ADMIN_BOT_STG;
GRANT USAGE ON DATABASE SOPHIA_AI_STG TO ROLE ROLE_SOPHIA_SNOWFLAKE_ADMIN_BOT_STG;
GRANT USAGE ON SCHEMA SOPHIA_AI_STG.* TO ROLE ROLE_SOPHIA_SNOWFLAKE_ADMIN_BOT_STG;
GRANT CREATE ON SCHEMA SOPHIA_AI_STG.* TO ROLE ROLE_SOPHIA_SNOWFLAKE_ADMIN_BOT_STG;

-- PROD Environment Permissions (read-only)
GRANT USAGE ON WAREHOUSE PROD_READ_ONLY TO ROLE ROLE_SOPHIA_SNOWFLAKE_ADMIN_BOT_PROD;
GRANT USAGE ON DATABASE SOPHIA_AI_PROD TO ROLE ROLE_SOPHIA_SNOWFLAKE_ADMIN_BOT_PROD;
GRANT USAGE ON SCHEMA SOPHIA_AI_PROD.* TO ROLE ROLE_SOPHIA_SNOWFLAKE_ADMIN_BOT_PROD;
GRANT MONITOR ON ACCOUNT TO ROLE ROLE_SOPHIA_SNOWFLAKE_ADMIN_BOT_PROD;
```

---

## **🔌 Integration Points**

### **MCP Server Integration**

```bash
# Start Snowflake Admin MCP Server
cd mcp-servers/snowflake_admin
python snowflake_admin_mcp_server.py

# Test MCP server health
curl http://localhost:8085/health
```

### **Chat Interface Integration**

The agent integrates seamlessly with Sophia AI's Enhanced Unified Chat Service:

```python
# In enhanced_unified_chat_service.py
from backend.services.snowflake_admin_chat_integration import (
    is_snowflake_admin_query,
    process_snowflake_admin_query
)

# Check if query is admin-related
if is_snowflake_admin_query(user_query):
    response = await process_snowflake_admin_query(user_query, user_id)
    return format_admin_response(response)
```

### **Docker Deployment**

```bash
# Build and run Docker container
cd mcp-servers/snowflake_admin
docker build -t sophia-snowflake-admin .
docker run -p 8085:8085 sophia-snowflake-admin
```

---

## **📊 Monitoring and Logging**

### **Audit Trail**

All operations are logged with:
- User ID and timestamp
- Original natural language request
- Generated SQL commands
- Execution results
- Environment and permissions used

### **Metrics Tracked**

- Query execution count by environment
- Average execution time
- Error rate and types
- Confirmation workflow usage
- Most common admin tasks

### **Health Monitoring**

```python
# Check agent health
health = await snowflake_admin_agent.health_check()
print(health)

# Example response:
{
  "initialized": true,
  "langchain_available": true,
  "snowflake_available": true,
  "environments": {
    "dev": {"status": "healthy", "current_user": "SOPHIA_SNOWFLAKE_ADMIN_BOT_USER"},
    "stg": {"status": "healthy", "current_role": "ROLE_SOPHIA_SNOWFLAKE_ADMIN_BOT_STG"},
    "prod": {"status": "healthy", "current_warehouse": "PROD_READ_ONLY"}
  }
}
```

---

## **🔄 Confirmation Workflow**

### **How Confirmations Work**

1. **Detection**: Agent detects potentially dangerous SQL
2. **Pause**: Execution is paused, SQL is shown to user
3. **Confirmation**: User must explicitly confirm the operation
4. **Execution**: Only after confirmation is the SQL executed

### **Example Confirmation Flow**

```
User: "Drop schema OLD_DATA"

Agent: "⚠️ CONFIRMATION REQUIRED: This operation contains potentially destructive SQL.

Proposed SQL: DROP SCHEMA OLD_DATA;
Environment: dev
Confirmation ID: confirm_123

To proceed, type: 'confirm confirm_123'"

User: "confirm confirm_123"

Agent: "✅ Successfully executed SQL in dev environment.
Execution time: 0.45s"
```

---

## **🧪 Testing**

### **Unit Tests**

```bash
# Run agent tests
python -m pytest tests/backend/test_snowflake_admin_agent.py

# Run integration tests
python -m pytest tests/backend/test_snowflake_admin_integration.py
```

### **Manual Testing**

```python
# Test basic functionality
from backend.agents.specialized.snowflake_admin_agent import execute_snowflake_admin_task

async def test_basic_operations():
    # Test schema listing
    response = await execute_snowflake_admin_task(
        "Show all schemas in the current database",
        target_environment="dev"
    )
    assert response.success
    
    # Test safe creation
    response = await execute_snowflake_admin_task(
        "Create schema TEST_SCHEMA if it doesn't exist",
        target_environment="dev"
    )
    assert response.success
```

---

## **🚨 Troubleshooting**

### **Common Issues**

#### **Authentication Errors**
```
Error: Authentication failed
Solution: Check PAT token validity and user permissions
```

#### **Permission Denied**
```
Error: SQL access control error: Insufficient privileges
Solution: Verify role permissions for target environment
```

#### **Connection Timeout**
```
Error: Connection timeout
Solution: Check network connectivity and Snowflake account status
```

### **Debug Mode**

Enable verbose logging for troubleshooting:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Agent will now log all LangChain thoughts and SQL generation
```

---

## **🔮 Future Enhancements**

### **Planned Features**

1. **REST API Integration**: Custom LangChain tools for Snowflake REST API operations
2. **Advanced Analytics**: Query performance analysis and optimization suggestions
3. **Batch Operations**: Support for multi-statement operations with rollback
4. **Template System**: Pre-built templates for common admin scenarios
5. **Role-Based Access**: User-specific permission validation
6. **Integration with Other Tools**: dbt, Airflow, and other data tools

### **Custom Tools Development**

```python
# Example custom tool for network policy management
from langchain.tools import BaseTool

class CreateNetworkPolicyTool(BaseTool):
    name = "create_network_policy"
    description = "Create a Snowflake network policy using REST API"
    
    def _run(self, policy_name: str, allowed_ip_list: List[str]) -> str:
        # Implementation using Snowflake REST API
        pass
```

---

## **📚 Additional Resources**

- [Snowflake SQL Reference](https://docs.snowflake.com/en/sql-reference)
- [LangChain SQL Agent Documentation](https://python.langchain.com/docs/integrations/toolkits/sql_database)
- [Snowflake Security Best Practices](https://docs.snowflake.com/en/user-guide/security)
- [Sophia AI Architecture Documentation](../../../docs/architecture/)

---

## **🤝 Contributing**

### **Development Workflow**

1. **Setup Development Environment**:
   ```bash
   git clone https://github.com/ai-cherry/sophia-main.git
   cd sophia-main
   pip install -r requirements.txt
   ```

2. **Create Feature Branch**:
   ```bash
   git checkout -b feature/snowflake-admin-enhancement
   ```

3. **Test Changes**:
   ```bash
   python -m pytest tests/backend/test_snowflake_admin_agent.py
   ```

4. **Submit Pull Request**: Include tests and documentation updates

### **Code Standards**

- Follow PEP 8 for Python code style
- Include comprehensive docstrings
- Add type hints for all functions
- Write unit tests for new functionality
- Update documentation for API changes

---

**The Snowflake Admin Agent represents a significant advancement in database administration automation, bringing natural language interfaces to complex Snowflake operations while maintaining enterprise-grade security and auditability.** 🚀 