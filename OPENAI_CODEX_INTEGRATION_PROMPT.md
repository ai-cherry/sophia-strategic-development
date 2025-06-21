# Comprehensive OpenAI Codex Prompt for Sophia AI MCP Service Integration

## Context and Objective

You are an expert AI software architect tasked with implementing a comprehensive service integration for the Sophia AI platform. Your goal is to integrate 19 AI and data services into the existing Model Context Protocol (MCP) architecture while maintaining production-ready code quality, optimal performance, and cost efficiency.

## Project Overview

**Platform**: Sophia AI - Business Intelligence AI Platform
**Architecture**: MCP-based microservices on Lambda Labs GPU infrastructure
**Deployment**: Direct to production (no sandbox environments)
**Infrastructure**: Infrastructure as Code with Pulumi
**Secret Management**: GitHub Organization Secrets → Pulumi ESC → Runtime

## Current Architecture Analysis

### Existing MCP Structure
```
sophia-main/
├── mcp-servers/
│   ├── snowflake/ (existing - data warehouse)
│   └── pulumi/ (existing - infrastructure)
├── backend/mcp/
│   ├── sophia_mcp_server.py (central orchestrator)
│   └── mcp_client.py (client interface)
└── backend/agents/core/
    └── mcp_crew_orchestrator.py (CrewAI integration)
```

### Services to Integrate
**AI Services**: Arize (monitoring), OpenRouter (gateway), Portkey (caching), HuggingFace (models), Together AI (inference)
**Data Services**: Apify (scraping), PhantomBuster (automation), Twingly (news), Tavily (AI search), ZenRows (scraping)
**Infrastructure**: Lambda Labs (compute), Docker (containers), GitHub (CI/CD)

## Implementation Requirements

### 1. MCP Server Architecture Requirements
- **Inherit from existing base class**: Use `mcp-servers/snowflake/mcp_base.py` as foundation
- **Domain-based organization**: Group related services into unified MCP servers
- **Consistent tool registration**: Follow existing pattern for tool and resource registration
- **Error handling**: Implement comprehensive error handling and logging
- **HTTP and stdin interfaces**: Support both communication methods

### 2. Service Integration Patterns
```python
# Required MCP Server Structure
class ServiceMCPServer(MCPServer):
    def __init__(self):
        super().__init__("service_name")
        # Initialize service clients

    async def setup(self):
        # Register tools following this pattern
        self.register_tool(Tool(
            name="tool_name",
            description="Clear description",
            parameters={
                "param": {"type": "string", "required": True, "description": "..."}
            },
            handler=self.tool_handler
        ))

    async def tool_handler(self, **kwargs):
        # Implement tool logic with error handling
        try:
            result = await self.service_client.operation(**kwargs)
            return {"success": True, "result": result}
        except Exception as e:
            self.logger.error(f"Error: {e}")
            return {"error": str(e)}
```

### 3. Optimization Integration Requirements
- **Cost tracking**: Implement cost monitoring for all service calls
- **Performance monitoring**: Log execution times and success rates
- **Intelligent routing**: Route requests to optimal services based on cost/performance
- **Caching**: Implement semantic caching where appropriate
- **Rate limiting**: Respect API limits and implement backoff strategies

### 4. Data Pipeline Integration
- **Unified data flow**: All services feed into Airbyte → PostgreSQL → Redis → Vector DBs
- **Real-time processing**: Support both batch and real-time data processing
- **Schema adaptation**: Dynamic schema updates for new data sources
- **Vector embeddings**: Generate and store embeddings for semantic search

## Specific Implementation Tasks

### Task 1: Create AI Intelligence MCP Server
**File**: `mcp-servers/ai_intelligence/ai_intelligence_mcp_server.py`
**Services**: Arize, OpenRouter, Portkey, HuggingFace, Together AI
**Key Tools**:
- `intelligent_generate`: Smart text generation with optimal model routing
- `get_embeddings`: Generate embeddings using best available model
- `monitor_ai_usage`: Log AI interactions to Arize for monitoring
- `optimize_routing`: Analyze and optimize model routing decisions

### Task 2: Create Data Intelligence MCP Server
**File**: `mcp-servers/data_intelligence/data_intelligence_mcp_server.py`
**Services**: Apify, PhantomBuster, Twingly, Tavily, ZenRows
**Key Tools**:
- `intelligent_research`: Multi-source research with AI-powered synthesis
- `scrape_website`: Intelligent web scraping with fallback options
- `monitor_news`: Real-time news monitoring and analysis
- `extract_leads`: Lead generation and contact discovery

### Task 3: Create Infrastructure Intelligence MCP Server
**File**: `mcp-servers/infrastructure_intelligence/infrastructure_intelligence_mcp_server.py`
**Services**: Lambda Labs, Docker, GitHub (enhanced existing Pulumi server)
**Key Tools**:
- `optimize_infrastructure`: Analyze and optimize resource usage
- `manage_deployments`: Handle container deployments and scaling
- `monitor_costs`: Track and optimize infrastructure costs
- `automate_scaling`: Implement intelligent auto-scaling

### Task 4: Enhance Central Orchestrator
**File**: `backend/mcp/sophia_mcp_server.py`
**Enhancements**:
- Service discovery and health monitoring
- Intelligent request routing across MCP servers
- Cross-service optimization and coordination
- Unified monitoring and alerting

### Task 5: Update Integration Registry
**File**: `infrastructure/integration_registry.json`
**Updates**:
- Add all new service configurations
- Include optimization parameters
- Define service dependencies and priorities
- Set monitoring and alerting thresholds

## Code Quality Requirements

### 1. Production Standards
- **Type hints**: Use comprehensive type annotations
- **Error handling**: Implement try-catch blocks with specific error types
- **Logging**: Use structured logging with appropriate levels
- **Documentation**: Include docstrings for all classes and methods
- **Testing**: Include unit tests for critical functionality

### 2. Performance Optimization
- **Async/await**: Use async programming for all I/O operations
- **Connection pooling**: Implement connection reuse for external services
- **Caching**: Add intelligent caching layers where beneficial
- **Rate limiting**: Implement proper rate limiting and backoff

### 3. Security Best Practices
- **Secret management**: Use environment variables and Pulumi ESC
- **Input validation**: Validate all input parameters
- **Error sanitization**: Don't expose sensitive information in errors
- **Authentication**: Implement proper API authentication

## Intelligent Review Criteria

### Code Review Checklist
1. **Architecture Compliance**
   - [ ] Follows existing MCP server patterns
   - [ ] Properly inherits from base classes
   - [ ] Implements required interfaces
   - [ ] Maintains consistent error handling

2. **Service Integration Quality**
   - [ ] All 19 services properly integrated
   - [ ] Service clients properly initialized
   - [ ] API calls handle rate limits and errors
   - [ ] Fallback mechanisms implemented

3. **Optimization Implementation**
   - [ ] Cost tracking implemented for all services
   - [ ] Performance monitoring in place
   - [ ] Intelligent routing logic implemented
   - [ ] Caching strategies applied appropriately

4. **Data Pipeline Integration**
   - [ ] Data flows into unified pipeline
   - [ ] Schema adaptation implemented
   - [ ] Vector embeddings generated where appropriate
   - [ ] Real-time processing supported

5. **Production Readiness**
   - [ ] Comprehensive error handling
   - [ ] Proper logging and monitoring
   - [ ] Security best practices followed
   - [ ] Performance optimized

### Optimization Review Criteria
1. **Cost Efficiency**
   - [ ] Intelligent model routing reduces AI costs by 25-30%
   - [ ] Caching reduces redundant API calls by 20-40%
   - [ ] Resource optimization saves 15-25% on infrastructure
   - [ ] Rate limiting prevents cost overruns

2. **Performance Excellence**
   - [ ] Response times under 2 seconds for AI operations
   - [ ] Data collection jobs complete within target timeframes
   - [ ] Cache hit rates above 30% where implemented
   - [ ] Concurrent operations properly handled

3. **Reliability Standards**
   - [ ] Error rates below 1% for critical operations
   - [ ] Proper fallback mechanisms in place
   - [ ] Circuit breakers prevent cascade failures
   - [ ] Health checks and monitoring implemented

## Implementation Strategy

### Phase 1: Core AI Services (Priority 1)
1. Implement AI Intelligence MCP Server
2. Integrate Arize monitoring
3. Set up intelligent routing with OpenRouter/Portkey
4. Add HuggingFace and Together AI model access

### Phase 2: Data Collection Services (Priority 2)
1. Implement Data Intelligence MCP Server
2. Integrate all data collection services
3. Set up unified data pipeline
4. Implement intelligent research capabilities

### Phase 3: Infrastructure Enhancement (Priority 3)
1. Implement Infrastructure Intelligence MCP Server
2. Enhance existing Pulumi integration
3. Add Lambda Labs and Docker management
4. Implement cost optimization features

### Phase 4: Integration and Optimization (Priority 4)
1. Enhance central orchestrator
2. Implement cross-service optimization
3. Add comprehensive monitoring
4. Optimize performance and costs

## Expected Deliverables

### Code Files
1. `mcp-servers/ai_intelligence/ai_intelligence_mcp_server.py`
2. `mcp-servers/data_intelligence/data_intelligence_mcp_server.py`
3. `mcp-servers/infrastructure_intelligence/infrastructure_intelligence_mcp_server.py`
4. Enhanced `backend/mcp/sophia_mcp_server.py`
5. Updated `infrastructure/integration_registry.json`
6. Service client implementations for all 19 services
7. Optimization engine implementations
8. Data pipeline integration code

### Configuration Files
1. Docker configurations for each MCP server
2. Pulumi deployment configurations
3. Environment variable templates
4. Monitoring and alerting configurations

### Documentation
1. API documentation for all new tools
2. Deployment and configuration guides
3. Optimization and monitoring documentation
4. Troubleshooting and maintenance guides

## Success Metrics

### Technical Metrics
- All 19 services successfully integrated and operational
- Response times meet performance targets (<2s for AI, <30s for data collection)
- Error rates below 1% for critical operations
- Cost optimization targets achieved (25-30% AI cost reduction)

### Business Metrics
- Unified interface for all AI and data operations
- Real-time business intelligence capabilities
- Scalable architecture supporting 10x growth
- Production-ready deployment with comprehensive monitoring

## Final Instructions

Implement this integration with the highest standards of software engineering. Focus on production readiness, optimal performance, and cost efficiency. Ensure all code follows the existing patterns while introducing the necessary optimizations and enhancements. The result should be a robust, scalable, and cost-effective AI platform that serves as the foundation for Sophia AI's business intelligence capabilities.

Remember: This is a production deployment with no sandbox environments. Every line of code must be production-ready and thoroughly tested. The integration should enhance the existing architecture while maintaining backward compatibility and operational stability.
