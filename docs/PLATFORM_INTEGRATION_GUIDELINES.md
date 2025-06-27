# 🔌 SOPHIA AI PLATFORM INTEGRATION GUIDELINES
**Complete Guide for Integrating External Platforms with Sophia AI**

---

## 📋 **INTEGRATION OVERVIEW**

### **Sophia AI Integration Philosophy**
Sophia AI follows a **unified integration architecture** that standardizes how external platforms connect to the system:

1. **MCP-First Approach**: All integrations use Model Context Protocol (MCP) servers
2. **Centralized Authentication**: Pulumi ESC manages all credentials securely
3. **Standardized Data Flow**: Consistent patterns for data ingestion and processing
4. **Real-time + Batch**: Support for both real-time events and batch processing
5. **Semantic Integration**: All data flows through semantic search and memory systems

### **Integration Layers**
```
External Platform → MCP Server → Agent Layer → Memory Service → Business Intelligence
```

---

## 🏗️ **INTEGRATION ARCHITECTURE**

### **Core Integration Components**

#### **1. MCP Server Layer**
- **Purpose**: Standardized interface for external platform communication
- **Port Range**: 9000-9020 (assigned via `config/mcp_ports.json`)
- **Base Class**: `StandardizedMCPServer`
- **Health Monitoring**: Built-in health checks and monitoring

#### **2. Authentication Layer**
- **Credential Management**: Pulumi ESC + GitHub Organization Secrets
- **Token Refresh**: Automated token refresh and rotation
- **Security**: SOC2 compliant credential handling

#### **3. Data Processing Layer**
- **Ingestion**: Real-time and batch data processing
- **Transformation**: Standardized data models and schemas
- **Storage**: Snowflake (structured) + Pinecone (vectors)

#### **4. Intelligence Layer**
- **Semantic Search**: Vector-based content discovery
- **Agent Processing**: AI-powered data analysis and insights
- **Memory Integration**: Persistent context and learning

---

## 📊 **PLATFORM INTEGRATION MATRIX**

### **Data Stack Platforms**

#### **Snowflake (Data Warehouse)**
```yaml
Integration Type: Direct Connection + MCP Server
MCP Server: snowflake_admin (Port 9012)
Authentication: PAT Token via Pulumi ESC
Data Flow: Direct SQL queries + semantic layer
Real-time: Yes (via streams)
Batch: Yes (via scheduled queries)

Key Capabilities:
- Schema management and optimization
- Query execution and performance monitoring
- Data pipeline orchestration
- Cost optimization and resource management

Environment Variables:
- SNOWFLAKE_ACCOUNT
- SNOWFLAKE_USER  
- SNOWFLAKE_PASSWORD (PAT Token)
- SNOWFLAKE_ROLE
```

#### **Airbyte (Data Integration)**
```yaml
Integration Type: API + Webhook
MCP Server: airbyte_integration (Port 9013)
Authentication: Client ID/Secret + Access Token
Data Flow: Source → Airbyte → Snowflake → Sophia AI
Real-time: Yes (via webhooks)
Batch: Yes (via scheduled syncs)

Key Capabilities:
- Source/destination configuration
- Sync monitoring and management
- Schema evolution handling
- Error handling and retry logic

Environment Variables:
- AIRBYTE_CLIENT_ID
- AIRBYTE_CLIENT_SECRET
- AIRBYTE_ACCESS_TOKEN
- AIRBYTE_WORKSPACE_ID
```

#### **Gong (Sales Intelligence)**
```yaml
Integration Type: API + Webhook + Data Share
MCP Server: gong_intelligence (Port 9001)
Authentication: Access Key + Client Secret
Data Flow: Gong API → MCP → Memory Service
Real-time: Yes (via webhooks)
Batch: Yes (via data share)

Key Capabilities:
- Call recording analysis
- Conversation intelligence
- Sales coaching insights
- Competitive analysis

Environment Variables:
- GONG_ACCESS_KEY
- GONG_CLIENT_SECRET
- GONG_WEBHOOK_JWT_PUBLIC_KEY
- GONG_WEBHOOK_BASE_URL
```

#### **Slack (Team Communication)**
```yaml
Integration Type: Bot API + Events API + Webhook
MCP Server: slack_integration (Port 9003)
Authentication: Bot Token + App Token + Signing Secret
Data Flow: Slack Events → MCP → Memory Service
Real-time: Yes (via Events API)
Batch: Yes (via history API)

Key Capabilities:
- Message processing and analysis
- Channel monitoring
- User interaction tracking
- Automated responses

Environment Variables:
- SLACK_BOT_TOKEN
- SLACK_APP_TOKEN
- SLACK_SIGNING_SECRET
- SLACK_WEBHOOK_URL
```

#### **HubSpot (CRM)**
```yaml
Integration Type: API + Webhook
MCP Server: hubspot_crm (Port 9002)
Authentication: Access Token (OAuth)
Data Flow: HubSpot API → MCP → Memory Service
Real-time: Yes (via webhooks)
Batch: Yes (via API pagination)

Key Capabilities:
- Contact and company management
- Deal pipeline tracking
- Marketing automation
- Customer journey analysis

Environment Variables:
- HUBSPOT_ACCESS_TOKEN
- HUBSPOT_CLIENT_ID
- HUBSPOT_CLIENT_SECRET
- HUBSPOT_WEBHOOK_URL
```

### **Development Stack Platforms**

#### **Vercel (Frontend Deployment)**
```yaml
Integration Type: API + Webhook
MCP Server: vercel_deployment (Port 9014)
Authentication: Token
Data Flow: Vercel API → MCP → Infrastructure Service
Real-time: Yes (via webhooks)
Batch: Yes (via API)

Key Capabilities:
- Deployment monitoring
- Performance analytics
- Domain management
- Build optimization

Environment Variables:
- VERCEL_TOKEN
- VERCEL_TEAM_ID
- VERCEL_PROJECT_ID
```

#### **Lambda Labs (Compute)**
```yaml
Integration Type: API
MCP Server: lambda_labs_compute (Port 9015)
Authentication: API Key
Data Flow: Lambda Labs API → MCP → Infrastructure Service
Real-time: Yes (via polling)
Batch: Yes (via API)

Key Capabilities:
- Instance management
- Resource monitoring
- Cost optimization
- Performance tracking

Environment Variables:
- LAMBDA_LABS_API_KEY
- LAMBDA_LABS_SSH_KEY
```

#### **Figma (Design System)**
```yaml
Integration Type: API + Webhook
MCP Server: figma_design (Port 9006)
Authentication: Access Token
Data Flow: Figma API → MCP → Design Service
Real-time: Yes (via webhooks)
Batch: Yes (via API)

Key Capabilities:
- Design file monitoring
- Component tracking
- Version management
- Design-to-code automation

Environment Variables:
- FIGMA_ACCESS_TOKEN
- FIGMA_WEBHOOK_URL
```

### **AI Stack Platforms**

#### **Portkey (LLM Gateway)**
```yaml
Integration Type: API
MCP Server: portkey_gateway (Port 9016)
Authentication: API Key + Config
Data Flow: Sophia AI → Portkey → LLM Providers
Real-time: Yes (via API)
Batch: Yes (via analytics API)

Key Capabilities:
- LLM routing and optimization
- Cost monitoring
- Performance analytics
- Model fallback handling

Environment Variables:
- PORTKEY_API_KEY
- PORTKEY_CONFIG
- PORTKEY_WORKSPACE_ID
```

#### **OpenRouter (LLM Access)**
```yaml
Integration Type: API
MCP Server: openrouter_llm (Port 9017)
Authentication: API Key
Data Flow: Sophia AI → OpenRouter → LLM Models
Real-time: Yes (via API)
Batch: Yes (via usage API)

Key Capabilities:
- Multi-model access
- Cost optimization
- Performance monitoring
- Model selection

Environment Variables:
- OPENROUTER_API_KEY
- OPENROUTER_APP_NAME
- OPENROUTER_SITE_URL
```

### **Operations Stack Platforms**

#### **Linear (Project Management)**
```yaml
Integration Type: API + Webhook
MCP Server: linear_projects (Port 9004)
Authentication: API Key
Data Flow: Linear API → MCP → Memory Service
Real-time: Yes (via webhooks)
Batch: Yes (via API)

Key Capabilities:
- Issue tracking
- Project progress monitoring
- Team productivity analytics
- Automated workflow management

Environment Variables:
- LINEAR_API_KEY
- LINEAR_WEBHOOK_URL
- LINEAR_TEAM_ID
```

#### **Asana (Task Management)**
```yaml
Integration Type: API + Webhook
MCP Server: asana_tasks (Port 9018)
Authentication: Access Token
Data Flow: Asana API → MCP → Memory Service
Real-time: Yes (via webhooks)
Batch: Yes (via API)

Key Capabilities:
- Task tracking
- Project management
- Team collaboration
- Progress reporting

Environment Variables:
- ASANA_ACCESS_TOKEN
- ASANA_WEBHOOK_URL
- ASANA_WORKSPACE_ID
```

### **Additional Platforms**

#### **UserGems (Contact Intelligence)**
```yaml
Integration Type: API
MCP Server: usergems_intelligence (Port 9019)
Authentication: API Key
Data Flow: UserGems API → MCP → Memory Service
Real-time: No
Batch: Yes (via API)

Key Capabilities:
- Contact tracking
- Job change monitoring
- Lead scoring
- Relationship mapping

Environment Variables:
- USERGEMS_API_KEY
```

#### **Apollo.io (Sales Intelligence)**
```yaml
Integration Type: API
MCP Server: apollo_sales (Port 9020)
Authentication: API Key
Data Flow: Apollo API → MCP → Memory Service
Real-time: No
Batch: Yes (via API)

Key Capabilities:
- Prospect research
- Contact enrichment
- Sales sequence automation
- Lead generation

Environment Variables:
- APOLLO_API_KEY
```

---

## 🔧 **INTEGRATION IMPLEMENTATION PATTERNS**

### **1. MCP Server Implementation Template**

```python
# Template for new platform MCP server
from backend.mcp.base.standardized_mcp_server import StandardizedMCPServer
from typing import Dict, List, Any, Optional
import aiohttp
import os

class PlatformMCPServer(StandardizedMCPServer):
    def __init__(self):
        super().__init__(
            server_name="platform_name",
            port=9XXX,  # Assign from mcp_ports.json
            tools=["tool1", "tool2", "tool3"]
        )
        self._client = None
        self._authenticated = False
    
    async def _initialize_server(self):
        """Initialize platform-specific client"""
        # Load credentials from environment
        api_key = os.getenv("PLATFORM_API_KEY")
        if not api_key:
            raise ValueError("PLATFORM_API_KEY environment variable required")
        
        # Initialize client
        self._client = PlatformClient(api_key)
        
        # Test authentication
        await self._authenticate()
        
        self.logger.info(f"Platform MCP server initialized successfully")
    
    async def _authenticate(self):
        """Authenticate with platform"""
        try:
            # Test API connection
            await self._client.test_connection()
            self._authenticated = True
            self.logger.info("Platform authentication successful")
        except Exception as e:
            self.logger.error(f"Platform authentication failed: {e}")
            raise
    
    async def handle_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming tool calls"""
        try:
            # Ensure authenticated
            if not self._authenticated:
                await self._authenticate()
            
            # Route to appropriate handler
            if tool_name == "tool1":
                return await self._handle_tool1(arguments)
            elif tool_name == "tool2":
                return await self._handle_tool2(arguments)
            else:
                raise ValueError(f"Unknown tool: {tool_name}")
                
        except Exception as e:
            self.logger.error(f"Tool call failed: {e}")
            return {
                "status": "error",
                "message": str(e),
                "tool": tool_name
            }
    
    async def _handle_tool1(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle specific tool implementation"""
        # Validate arguments
        required_args = ["param1", "param2"]
        for arg in required_args:
            if arg not in arguments:
                raise ValueError(f"Missing required argument: {arg}")
        
        # Call platform API
        result = await self._client.api_call(
            endpoint="/api/endpoint",
            params=arguments
        )
        
        return {
            "status": "success",
            "data": result,
            "tool": "tool1"
        }
    
    def _get_tool_schema_impl(self, tool_name: str) -> Dict[str, Any]:
        """Define tool schemas"""
        schemas = {
            "tool1": {
                "description": "Description of tool1",
                "parameters": {
                    "param1": {"type": "string", "description": "Parameter 1"},
                    "param2": {"type": "integer", "description": "Parameter 2"}
                }
            }
        }
        return schemas.get(tool_name, {})

class PlatformClient:
    """Platform-specific API client"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.platform.com"
        self.session = None
    
    async def test_connection(self):
        """Test API connection"""
        async with aiohttp.ClientSession() as session:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            async with session.get(f"{self.base_url}/health", headers=headers) as response:
                response.raise_for_status()
    
    async def api_call(self, endpoint: str, params: Dict = None) -> Dict[str, Any]:
        """Make API call to platform"""
        async with aiohttp.ClientSession() as session:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            async with session.get(f"{self.base_url}{endpoint}", headers=headers, params=params) as response:
                response.raise_for_status()
                return await response.json()
```

### **2. Webhook Integration Pattern**

```python
# Webhook handler implementation
from fastapi import APIRouter, HTTPException, Request, Depends
from typing import Dict, Any
import hmac
import hashlib
import os

router = APIRouter(prefix="/webhook/platform", tags=["webhooks"])

async def verify_webhook_signature(request: Request) -> bool:
    """Verify webhook signature"""
    signature = request.headers.get("X-Platform-Signature")
    if not signature:
        raise HTTPException(status_code=401, detail="Missing signature")
    
    # Get webhook secret
    webhook_secret = os.getenv("PLATFORM_WEBHOOK_SECRET")
    if not webhook_secret:
        raise HTTPException(status_code=500, detail="Webhook secret not configured")
    
    # Verify signature
    body = await request.body()
    expected_signature = hmac.new(
        webhook_secret.encode(),
        body,
        hashlib.sha256
    ).hexdigest()
    
    if not hmac.compare_digest(signature, f"sha256={expected_signature}"):
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    return True

@router.post("/events")
async def handle_platform_webhook(
    request: Request,
    verified: bool = Depends(verify_webhook_signature)
):
    """Handle platform webhook events"""
    try:
        # Parse webhook payload
        payload = await request.json()
        event_type = payload.get("type")
        
        # Route to appropriate handler
        if event_type == "event1":
            await handle_event1(payload)
        elif event_type == "event2":
            await handle_event2(payload)
        else:
            logger.warning(f"Unknown event type: {event_type}")
        
        return {"status": "success"}
        
    except Exception as e:
        logger.error(f"Webhook processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def handle_event1(payload: Dict[str, Any]):
    """Handle specific event type"""
    # Extract relevant data
    data = payload.get("data", {})
    
    # Process through memory service
    from backend.services.comprehensive_memory_service import ComprehensiveMemoryService
    memory_service = ComprehensiveMemoryService()
    
    # Store in memory with metadata
    await memory_service.store_memory(
        content=f"Platform event: {data}",
        metadata={
            "source": "platform_webhook",
            "event_type": "event1",
            "timestamp": payload.get("timestamp"),
            "structured_data": data
        }
    )
```

### **3. Data Processing Pattern**

```python
# Data processing and transformation
from typing import Dict, List, Any, Optional
from datetime import datetime
import asyncio

class PlatformDataProcessor:
    """Process and transform platform data"""
    
    def __init__(self):
        from backend.services.comprehensive_memory_service import ComprehensiveMemoryService
        self.memory_service = ComprehensiveMemoryService()
        self.logger = logging.getLogger("sophia.processors.platform")
    
    async def process_batch_data(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process batch data from platform"""
        try:
            processed_count = 0
            error_count = 0
            
            # Process in chunks to avoid memory issues
            chunk_size = 100
            for i in range(0, len(data), chunk_size):
                chunk = data[i:i + chunk_size]
                
                # Process chunk
                results = await self._process_chunk(chunk)
                processed_count += results["processed"]
                error_count += results["errors"]
            
            return {
                "status": "success",
                "total_records": len(data),
                "processed": processed_count,
                "errors": error_count
            }
            
        except Exception as e:
            self.logger.error(f"Batch processing failed: {e}")
            raise
    
    async def _process_chunk(self, chunk: List[Dict[str, Any]]) -> Dict[str, int]:
        """Process a chunk of data"""
        processed = 0
        errors = 0
        
        # Create processing tasks
        tasks = []
        for record in chunk:
            task = self._process_single_record(record)
            tasks.append(task)
        
        # Execute tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Count results
        for result in results:
            if isinstance(result, Exception):
                errors += 1
                self.logger.error(f"Record processing failed: {result}")
            else:
                processed += 1
        
        return {"processed": processed, "errors": errors}
    
    async def _process_single_record(self, record: Dict[str, Any]) -> str:
        """Process a single record"""
        # Transform data
        transformed_data = await self._transform_record(record)
        
        # Generate content for semantic search
        content = self._generate_searchable_content(transformed_data)
        
        # Store in memory service
        memory_id = await self.memory_service.store_memory(
            content=content,
            metadata={
                "source": "platform_batch",
                "record_type": transformed_data.get("type"),
                "timestamp": datetime.utcnow().isoformat(),
                "structured_data": transformed_data
            }
        )
        
        return memory_id
    
    async def _transform_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Transform platform-specific record to standard format"""
        # Implement platform-specific transformation logic
        return {
            "id": record.get("id"),
            "type": "platform_record",
            "title": record.get("name", ""),
            "description": record.get("description", ""),
            "created_at": record.get("created_at"),
            "metadata": record.get("metadata", {}),
            "raw_data": record
        }
    
    def _generate_searchable_content(self, data: Dict[str, Any]) -> str:
        """Generate searchable content from structured data"""
        content_parts = []
        
        if data.get("title"):
            content_parts.append(f"Title: {data['title']}")
        
        if data.get("description"):
            content_parts.append(f"Description: {data['description']}")
        
        # Add other relevant fields
        for key, value in data.get("metadata", {}).items():
            if isinstance(value, str) and value:
                content_parts.append(f"{key}: {value}")
        
        return " | ".join(content_parts)
```

---

## 🔐 **AUTHENTICATION & SECURITY**

### **1. Credential Management Pattern**

```python
# Secure credential management
import os
from typing import Dict, Optional
import logging

class PlatformCredentialManager:
    """Manage platform credentials securely"""
    
    def __init__(self, platform_name: str):
        self.platform_name = platform_name.upper()
        self.logger = logging.getLogger(f"sophia.credentials.{platform_name}")
        self._credentials = None
    
    def get_credentials(self) -> Dict[str, str]:
        """Get platform credentials from environment"""
        if self._credentials is None:
            self._credentials = self._load_credentials()
        return self._credentials
    
    def _load_credentials(self) -> Dict[str, str]:
        """Load credentials from environment variables"""
        # Define required credentials per platform
        credential_map = {
            "GONG": ["GONG_ACCESS_KEY", "GONG_CLIENT_SECRET"],
            "SLACK": ["SLACK_BOT_TOKEN", "SLACK_APP_TOKEN", "SLACK_SIGNING_SECRET"],
            "HUBSPOT": ["HUBSPOT_ACCESS_TOKEN"],
            "LINEAR": ["LINEAR_API_KEY"],
            "OPENROUTER": ["OPENROUTER_API_KEY"]
        }
        
        required_vars = credential_map.get(self.platform_name, [])
        credentials = {}
        
        for var in required_vars:
            value = os.getenv(var)
            if not value:
                raise ValueError(f"Missing required environment variable: {var}")
            credentials[var] = value
        
        self.logger.info(f"Loaded {len(credentials)} credentials for {self.platform_name}")
        return credentials
    
    def validate_credentials(self) -> bool:
        """Validate that all required credentials are present"""
        try:
            self.get_credentials()
            return True
        except ValueError as e:
            self.logger.error(f"Credential validation failed: {e}")
            return False
```

### **2. Token Refresh Pattern**

```python
# Automated token refresh
import asyncio
from datetime import datetime, timedelta
from typing import Optional

class TokenManager:
    """Manage OAuth token refresh"""
    
    def __init__(self, platform_name: str):
        self.platform_name = platform_name
        self.logger = logging.getLogger(f"sophia.tokens.{platform_name}")
        self._access_token = None
        self._refresh_token = None
        self._expires_at = None
        self._refresh_task = None
    
    async def get_valid_token(self) -> str:
        """Get a valid access token, refreshing if necessary"""
        if self._needs_refresh():
            await self._refresh_token_if_needed()
        
        if not self._access_token:
            raise ValueError("No valid access token available")
        
        return self._access_token
    
    def _needs_refresh(self) -> bool:
        """Check if token needs refresh"""
        if not self._access_token or not self._expires_at:
            return True
        
        # Refresh 5 minutes before expiry
        refresh_threshold = self._expires_at - timedelta(minutes=5)
        return datetime.utcnow() >= refresh_threshold
    
    async def _refresh_token_if_needed(self):
        """Refresh token if needed"""
        try:
            # Call platform-specific refresh endpoint
            response = await self._call_refresh_endpoint()
            
            # Update token information
            self._access_token = response["access_token"]
            self._refresh_token = response.get("refresh_token", self._refresh_token)
            
            # Calculate expiry time
            expires_in = response.get("expires_in", 3600)
            self._expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
            
            self.logger.info(f"Token refreshed successfully, expires at {self._expires_at}")
            
        except Exception as e:
            self.logger.error(f"Token refresh failed: {e}")
            raise
    
    async def _call_refresh_endpoint(self) -> Dict[str, Any]:
        """Call platform-specific token refresh endpoint"""
        # Implement platform-specific refresh logic
        pass
```

---

## 📊 **MONITORING & OBSERVABILITY**

### **1. Integration Health Monitoring**

```python
# Comprehensive integration health monitoring
from typing import Dict, List, Any
import asyncio
from datetime import datetime, timedelta

class IntegrationHealthMonitor:
    """Monitor health of all platform integrations"""
    
    def __init__(self):
        self.logger = logging.getLogger("sophia.monitoring.integrations")
        self.health_checks = {}
        self.alert_thresholds = {
            "response_time_ms": 5000,
            "error_rate_percent": 5.0,
            "uptime_percent": 99.0
        }
    
    def register_integration(self, platform_name: str, health_check_func):
        """Register an integration for monitoring"""
        self.health_checks[platform_name] = {
            "health_check": health_check_func,
            "last_check": None,
            "status": "unknown",
            "metrics": {
                "response_times": [],
                "error_count": 0,
                "success_count": 0,
                "uptime_start": datetime.utcnow()
            }
        }
    
    async def run_health_checks(self) -> Dict[str, Any]:
        """Run health checks for all registered integrations"""
        results = {}
        overall_healthy = True
        
        for platform_name, config in self.health_checks.items():
            try:
                # Run health check with timing
                start_time = datetime.utcnow()
                health_result = await config["health_check"]()
                end_time = datetime.utcnow()
                
                # Calculate response time
                response_time = (end_time - start_time).total_seconds() * 1000
                
                # Update metrics
                self._update_metrics(platform_name, response_time, True)
                
                # Store result
                results[platform_name] = {
                    "status": health_result.get("status", "unknown"),
                    "response_time_ms": response_time,
                    "details": health_result,
                    "last_check": end_time.isoformat()
                }
                
                if health_result.get("status") != "healthy":
                    overall_healthy = False
                    
            except Exception as e:
                # Update metrics for failure
                self._update_metrics(platform_name, 0, False)
                
                results[platform_name] = {
                    "status": "error",
                    "error": str(e),
                    "last_check": datetime.utcnow().isoformat()
                }
                overall_healthy = False
        
        return {
            "overall_status": "healthy" if overall_healthy else "degraded",
            "integrations": results,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _update_metrics(self, platform_name: str, response_time: float, success: bool):
        """Update metrics for a platform"""
        metrics = self.health_checks[platform_name]["metrics"]
        
        # Update response times (keep last 100)
        metrics["response_times"].append(response_time)
        if len(metrics["response_times"]) > 100:
            metrics["response_times"].pop(0)
        
        # Update counters
        if success:
            metrics["success_count"] += 1
        else:
            metrics["error_count"] += 1
    
    def get_platform_metrics(self, platform_name: str) -> Dict[str, Any]:
        """Get detailed metrics for a platform"""
        if platform_name not in self.health_checks:
            return {"error": "Platform not found"}
        
        metrics = self.health_checks[platform_name]["metrics"]
        
        # Calculate statistics
        response_times = metrics["response_times"]
        total_requests = metrics["success_count"] + metrics["error_count"]
        
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        error_rate = (metrics["error_count"] / total_requests * 100) if total_requests > 0 else 0
        
        uptime_duration = datetime.utcnow() - metrics["uptime_start"]
        uptime_percent = (metrics["success_count"] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "platform": platform_name,
            "avg_response_time_ms": avg_response_time,
            "error_rate_percent": error_rate,
            "uptime_percent": uptime_percent,
            "total_requests": total_requests,
            "uptime_duration_hours": uptime_duration.total_seconds() / 3600,
            "alerts": self._check_alerts(avg_response_time, error_rate, uptime_percent)
        }
    
    def _check_alerts(self, response_time: float, error_rate: float, uptime: float) -> List[str]:
        """Check for alert conditions"""
        alerts = []
        
        if response_time > self.alert_thresholds["response_time_ms"]:
            alerts.append(f"High response time: {response_time:.0f}ms")
        
        if error_rate > self.alert_thresholds["error_rate_percent"]:
            alerts.append(f"High error rate: {error_rate:.1f}%")
        
        if uptime < self.alert_thresholds["uptime_percent"]:
            alerts.append(f"Low uptime: {uptime:.1f}%")
        
        return alerts
```

### **2. Performance Monitoring**

```python
# Integration performance monitoring
import time
from functools import wraps
from typing import Callable, Any

def monitor_performance(operation_name: str):
    """Decorator to monitor operation performance"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            start_time = time.perf_counter()
            
            try:
                result = await func(*args, **kwargs)
                
                # Log successful operation
                end_time = time.perf_counter()
                duration = (end_time - start_time) * 1000  # milliseconds
                
                logger.info(f"Operation {operation_name} completed in {duration:.2f}ms")
                
                # Store metrics
                await store_performance_metric(operation_name, duration, "success")
                
                return result
                
            except Exception as e:
                # Log failed operation
                end_time = time.perf_counter()
                duration = (end_time - start_time) * 1000
                
                logger.error(f"Operation {operation_name} failed after {duration:.2f}ms: {e}")
                
                # Store metrics
                await store_performance_metric(operation_name, duration, "error")
                
                raise
        
        return wrapper
    return decorator

async def store_performance_metric(operation: str, duration: float, status: str):
    """Store performance metric"""
    # Store in time-series database or metrics system
    metric_data = {
        "operation": operation,
        "duration_ms": duration,
        "status": status,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Example: Store in Snowflake metrics table
    from backend.services.comprehensive_memory_service import ComprehensiveMemoryService
    memory_service = ComprehensiveMemoryService()
    
    await memory_service.execute_query(
        """
        INSERT INTO SOPHIA_AI_CORE.METRICS.PERFORMANCE_METRICS 
        (operation, duration_ms, status, timestamp)
        VALUES (%s, %s, %s, %s)
        """,
        [operation, duration, status, metric_data["timestamp"]]
    )
```

---

## 🚀 **DEPLOYMENT & CONFIGURATION**

### **1. Environment Configuration**

```yaml
# config/integrations.yaml
integrations:
  gong:
    enabled: true
    mcp_server_port: 9001
    webhook_path: "/webhook/gong"
    batch_sync_interval: "0 */6 * * *"  # Every 6 hours
    rate_limits:
      api_calls_per_minute: 100
      webhook_events_per_minute: 1000
  
  slack:
    enabled: true
    mcp_server_port: 9003
    webhook_path: "/webhook/slack"
    event_subscriptions:
      - "message.channels"
      - "app_mention"
      - "reaction_added"
    rate_limits:
      api_calls_per_minute: 50
  
  hubspot:
    enabled: true
    mcp_server_port: 9002
    webhook_path: "/webhook/hubspot"
    sync_objects:
      - "contacts"
      - "companies"
      - "deals"
    rate_limits:
      api_calls_per_minute: 100

monitoring:
  health_check_interval: 60  # seconds
  alert_thresholds:
    response_time_ms: 5000
    error_rate_percent: 5.0
    uptime_percent: 99.0
  
  metrics_retention_days: 30
```

### **2. Automated Deployment Script**

```python
# scripts/deploy_integrations.py
import asyncio
import yaml
from pathlib import Path
from typing import Dict, List

class IntegrationDeployment:
    """Deploy and configure all platform integrations"""
    
    def __init__(self):
        self.config = self._load_config()
        self.logger = logging.getLogger("sophia.deployment.integrations")
    
    def _load_config(self) -> Dict:
        """Load integration configuration"""
        config_path = Path(__file__).parent.parent / "config" / "integrations.yaml"
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    async def deploy_all_integrations(self):
        """Deploy all enabled integrations"""
        self.logger.info("Starting integration deployment")
        
        # Deploy MCP servers
        await self._deploy_mcp_servers()
        
        # Configure webhooks
        await self._configure_webhooks()
        
        # Set up monitoring
        await self._setup_monitoring()
        
        # Validate deployment
        await self._validate_deployment()
        
        self.logger.info("Integration deployment completed successfully")
    
    async def _deploy_mcp_servers(self):
        """Deploy all MCP servers"""
        for platform, config in self.config["integrations"].items():
            if not config.get("enabled", False):
                continue
            
            try:
                # Start MCP server
                await self._start_mcp_server(platform, config)
                self.logger.info(f"MCP server for {platform} started successfully")
                
            except Exception as e:
                self.logger.error(f"Failed to start MCP server for {platform}: {e}")
                raise
    
    async def _configure_webhooks(self):
        """Configure webhook endpoints"""
        for platform, config in self.config["integrations"].items():
            if not config.get("enabled", False) or not config.get("webhook_path"):
                continue
            
            try:
                # Configure webhook endpoint
                await self._configure_platform_webhook(platform, config)
                self.logger.info(f"Webhook for {platform} configured successfully")
                
            except Exception as e:
                self.logger.error(f"Failed to configure webhook for {platform}: {e}")
                raise
    
    async def _setup_monitoring(self):
        """Set up monitoring for all integrations"""
        from backend.monitoring.integration_health_monitor import IntegrationHealthMonitor
        
        monitor = IntegrationHealthMonitor()
        
        # Register health checks for each integration
        for platform, config in self.config["integrations"].items():
            if config.get("enabled", False):
                health_check_func = self._create_health_check(platform)
                monitor.register_integration(platform, health_check_func)
        
        # Start monitoring loop
        asyncio.create_task(self._monitoring_loop(monitor))
        
        self.logger.info("Integration monitoring started")
    
    async def _validate_deployment(self):
        """Validate that all integrations are working"""
        validation_results = {}
        
        for platform, config in self.config["integrations"].items():
            if not config.get("enabled", False):
                continue
            
            try:
                # Test MCP server
                mcp_health = await self._test_mcp_server(platform, config["mcp_server_port"])
                
                # Test webhook if configured
                webhook_health = True
                if config.get("webhook_path"):
                    webhook_health = await self._test_webhook(platform, config["webhook_path"])
                
                validation_results[platform] = {
                    "mcp_server": mcp_health,
                    "webhook": webhook_health,
                    "overall": mcp_health and webhook_health
                }
                
            except Exception as e:
                validation_results[platform] = {
                    "error": str(e),
                    "overall": False
                }
        
        # Check if all validations passed
        failed_integrations = [
            platform for platform, result in validation_results.items()
            if not result.get("overall", False)
        ]
        
        if failed_integrations:
            raise RuntimeError(f"Integration validation failed for: {failed_integrations}")
        
        self.logger.info("All integration validations passed")

if __name__ == "__main__":
    deployment = IntegrationDeployment()
    asyncio.run(deployment.deploy_all_integrations())
```

---

## 📚 **INTEGRATION CHECKLIST**

### **New Platform Integration Checklist**

#### **Planning Phase**
- [ ] Define integration requirements and scope
- [ ] Identify data sources and API capabilities
- [ ] Plan authentication and security approach
- [ ] Design data flow and transformation logic
- [ ] Assign MCP server port from available range

#### **Implementation Phase**
- [ ] Create MCP server using `StandardizedMCPServer` base class
- [ ] Implement platform-specific API client
- [ ] Add webhook handlers if supported
- [ ] Create data processing and transformation logic
- [ ] Implement health checks and monitoring

#### **Security Phase**
- [ ] Add required environment variables to Pulumi ESC
- [ ] Implement secure credential management
- [ ] Add webhook signature verification
- [ ] Test authentication and token refresh

#### **Testing Phase**
- [ ] Unit tests for MCP server tools
- [ ] Integration tests with platform API
- [ ] Webhook event processing tests
- [ ] Performance and load testing
- [ ] Security vulnerability testing

#### **Deployment Phase**
- [ ] Update integration configuration
- [ ] Deploy MCP server to production
- [ ] Configure webhook endpoints
- [ ] Set up monitoring and alerting
- [ ] Validate end-to-end functionality

#### **Documentation Phase**
- [ ] Update platform integration matrix
- [ ] Document API usage and limitations
- [ ] Create troubleshooting guide
- [ ] Update monitoring runbooks

---

**This comprehensive guide ensures consistent, secure, and maintainable platform integrations across the entire Sophia AI ecosystem.**

---

*Last Updated: June 27, 2025*  
*Version: 1.0*  
*Status: Production Standard*

