# MCP Remaining Servers Implementation Plan

**Date:** July 10, 2025  
**Status:** Ready for Implementation  
**Total Servers to Implement:** 9

## Executive Summary

This plan outlines the implementation of the remaining 9 MCP servers needed to complete the Sophia AI platform. All servers will follow the official Anthropic SDK pattern established in Phase 1.

## 🎯 Implementation Priority

### Tier 1 - Business Critical (Week 1)
1. **gong_v2** - Sales call analytics
2. **hubspot_unified** - CRM integration
3. **linear_v2** - Project management

### Tier 2 - Productivity Enhancement (Week 2)
4. **notion_v2** - Knowledge base
5. **postgres** - Database operations
6. **portkey_admin** - LLM routing & cost management

### Tier 3 - Advanced Features (Week 3)
7. **figma_context** - Design integration
8. **lambda_labs_cli** - Infrastructure management
9. **openrouter_search** - Model marketplace access

## 📋 Server Specifications

### 1. Gong V2 Server
**Port:** 9002  
**Capabilities:** CALLS, TRANSCRIPTS, ANALYTICS  
**Priority:** HIGH - Sales team dependency

**Key Tools:**
- `list_calls` - List recent calls with filters
- `get_call_transcript` - Retrieve call transcript
- `get_call_insights` - Get AI-generated insights
- `search_calls` - Search across all calls
- `get_speaker_stats` - Speaker talk time analytics
- `get_deal_intelligence` - Deal-specific insights

**Integration Points:**
- Gong API v2
- Webhook support for real-time updates
- Snowflake materialization for analytics

### 2. HubSpot Unified Server
**Port:** 9003  
**Capabilities:** CRM, CONTACTS, DEALS, ANALYTICS  
**Priority:** HIGH - Core CRM system

**Key Tools:**
- `list_contacts` - Get contacts with filters
- `create_contact` - Create new contact
- `update_contact` - Update contact properties
- `list_deals` - Get deals pipeline
- `create_deal` - Create new deal
- `update_deal_stage` - Move deal through pipeline
- `get_analytics` - CRM analytics data

**Integration Points:**
- HubSpot API v3
- Custom properties support
- Bulk operations capability

### 3. Linear V2 Server
**Port:** 9006  
**Capabilities:** PROJECTS, ISSUES, TEAMS, ANALYTICS  
**Priority:** HIGH - Development workflow

**Key Tools:**
- `list_issues` - Get issues with filters
- `create_issue` - Create new issue
- `update_issue` - Update issue status
- `list_projects` - Get all projects
- `get_team_velocity` - Team performance metrics
- `create_project_update` - Post project updates

**Integration Points:**
- Linear GraphQL API
- Webhook subscriptions
- GitHub integration sync

### 4. Notion V2 Server
**Port:** 9008  
**Capabilities:** DOCS, KNOWLEDGE_BASE, SEARCH  
**Priority:** MEDIUM - Documentation platform

**Key Tools:**
- `search_pages` - Search across workspace
- `get_page_content` - Retrieve page content
- `create_page` - Create new page
- `update_page` - Update existing page
- `list_databases` - Get all databases
- `query_database` - Query database with filters

**Integration Points:**
- Notion API v2
- Block-based content handling
- Database operations

### 5. Postgres Server
**Port:** 9009  
**Capabilities:** SQL, ANALYTICS, STORAGE  
**Priority:** MEDIUM - Database operations

**Key Tools:**
- `execute_query` - Run SQL queries
- `list_tables` - Get database schema
- `get_table_info` - Table structure details
- `execute_transaction` - Transactional operations
- `backup_database` - Create backups
- `analyze_performance` - Query performance analysis

**Integration Points:**
- PostgreSQL 15.3
- Connection pooling
- Transaction management

### 6. Portkey Admin Server
**Port:** 9013  
**Capabilities:** LLM_ROUTING, COST_TRACKING, ANALYTICS  
**Priority:** MEDIUM - Cost optimization

**Key Tools:**
- `get_usage_stats` - LLM usage statistics
- `list_models` - Available models and pricing
- `set_routing_rules` - Configure model routing
- `get_cost_breakdown` - Detailed cost analysis
- `set_budget_alerts` - Budget monitoring
- `optimize_routing` - Cost-optimized routing

**Integration Points:**
- Portkey API
- Real-time usage tracking
- Multi-provider support

### 7. Figma Context Server
**Port:** 9010  
**Capabilities:** DESIGN, WORKFLOW, ANALYTICS  
**Priority:** LOW - Design integration

**Key Tools:**
- `list_files` - Get design files
- `get_file_content` - Retrieve design details
- `export_assets` - Export design assets
- `get_comments` - Design feedback
- `get_version_history` - Design versions
- `analyze_components` - Component usage

**Integration Points:**
- Figma API
- Asset export pipeline
- Version control integration

### 8. Lambda Labs CLI Server
**Port:** 9011  
**Capabilities:** INFRASTRUCTURE, ANALYTICS  
**Priority:** LOW - Infrastructure automation

**Key Tools:**
- `list_instances` - Get all instances
- `create_instance` - Provision new instance
- `stop_instance` - Stop running instance
- `get_instance_metrics` - Resource usage
- `execute_command` - Remote command execution
- `manage_storage` - Storage operations

**Integration Points:**
- Lambda Labs API
- SSH integration
- Monitoring metrics

### 9. OpenRouter Search Server
**Port:** 9014  
**Capabilities:** LLM_ACCESS, MODEL_SELECTION  
**Priority:** LOW - Model marketplace

**Key Tools:**
- `search_models` - Search available models
- `get_model_info` - Model specifications
- `compare_models` - Model comparison
- `test_model` - Test model performance
- `get_pricing` - Model pricing info
- `route_request` - Route to optimal model

**Integration Points:**
- OpenRouter API
- Model metadata caching
- Performance benchmarking

## 🏗️ Implementation Guidelines

### Standard Structure
Each server must follow the established pattern:

```python
"""
Sophia AI [Service] MCP Server
Using official Anthropic MCP SDK

Date: July 10, 2025
"""

import asyncio
import sys
from pathlib import Path
from typing import Any, Dict, List

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp.types import Tool, TextContent
from base.unified_standardized_base import StandardizedMCPServer, ServerConfig
from backend.core.auto_esc_config import get_config_value

class [Service]MCPServer(StandardizedMCPServer):
    """[Service] MCP Server using official SDK"""
    
    def __init__(self):
        config = ServerConfig(
            name="[service_name]",
            version="1.0.0",
            description="[Service description]"
        )
        super().__init__(config)
        
        # Service configuration
        self.api_key = get_config_value("[service]_api_key")
        
    async def get_custom_tools(self) -> List[Tool]:
        """Define custom tools for [Service] operations"""
        return [
            # Tool definitions
        ]
    
    async def handle_custom_tool(self, name: str, arguments: dict) -> Dict[str, Any]:
        """Handle custom tool calls"""
        # Tool handling logic
```

### Testing Requirements
- Unit tests for each tool
- Integration tests with mock APIs
- Error handling validation
- Performance benchmarks

### Documentation Requirements
- README.md for each server
- Tool usage examples
- API credential setup guide
- Troubleshooting section

## 📅 Implementation Schedule

### Week 1 (July 10-16)
- Day 1-2: Gong V2 Server
- Day 3-4: HubSpot Unified Server
- Day 5: Linear V2 Server

### Week 2 (July 17-23)
- Day 1-2: Notion V2 Server
- Day 3-4: Postgres Server
- Day 5: Portkey Admin Server

### Week 3 (July 24-30)
- Day 1-2: Figma Context Server
- Day 3-4: Lambda Labs CLI Server
- Day 5: OpenRouter Search Server

## ✅ Success Metrics

- All 9 servers implemented and tested
- 100% adherence to official SDK pattern
- Zero custom shim dependencies
- Complete tool coverage for each service
- Comprehensive documentation
- Integration tests passing
- Performance benchmarks met

## 🚀 Next Steps

1. Begin with Tier 1 servers (business critical)
2. Use the established pattern from Phase 1
3. Ensure proper Pulumi ESC integration
4. Create comprehensive tests
5. Document all tools and usage patterns

---

**The completion of these 9 servers will bring the total to 16 fully standardized MCP servers, providing comprehensive coverage for all Sophia AI platform needs.** 