# Sophia AI Immediate Action Plan

**Date:** July 9, 2025  
**Priority:** HIGH  
**Timeline:** Next 48 hours

## Overview

This document outlines immediate, actionable steps to begin improving the Sophia AI orchestrator architecture. These are "quick wins" that can be implemented without major refactoring.

## Phase 0: Immediate Actions (Today)

### 1. Create Deprecation Warnings

```python
# Add to: backend/services/unified_chat_service.py (line 1)
import warnings

warnings.warn(
    "UnifiedChatService is deprecated. Please use SophiaUnifiedOrchestrator instead. "
    "This service will be removed in version 6.0",
    DeprecationWarning,
    stacklevel=2
)
```

### 2. Document Official Entry Point

```python
# Create: backend/services/sophia_unified_orchestrator.py
"""
Sophia Unified Orchestrator - The OFFICIAL entry point for all Sophia AI requests

This is the single, authoritative orchestrator that combines:
- UnifiedChatService capabilities
- SophiaAIOrchestrator intelligence
- EnhancedMultiAgentOrchestrator parallel execution
- SophiaAgentOrchestrator workflow patterns

All other orchestrators are DEPRECATED and will be removed.
"""

from typing import Any, Dict, List, Optional
import asyncio
import logging
from datetime import datetime

from backend.core.date_time_manager import date_manager
from backend.services.unified_memory_service import get_unified_memory_service
from infrastructure.services.mcp_orchestration_service import MCPOrchestrationService

logger = logging.getLogger(__name__)


class SophiaUnifiedOrchestrator:
    """
    The unified orchestrator for all Sophia AI operations.
    
    This replaces:
    - UnifiedChatService
    - SophiaAIOrchestrator  
    - EnhancedMultiAgentOrchestrator
    - SophiaAgentOrchestrator
    """
    
    def __init__(self):
        self.memory_service = get_unified_memory_service()
        self.mcp_orchestrator = MCPOrchestrationService()
        self.current_date = date_manager.now()
        
        logger.info(f"✅ SophiaUnifiedOrchestrator initialized - Date: {self.current_date}")
        
    async def process_request(
        self,
        query: str,
        user_id: str,
        session_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process any request through the unified orchestration pipeline.
        
        This is the ONLY method external services should call.
        """
        # Implementation will be added in phases
        # For now, route to existing services with deprecation tracking
        pass
```

### 3. Consolidate MCP Configuration

```yaml
# Create: config/sophia_mcp_unified.yaml
# SINGLE SOURCE OF TRUTH for all MCP servers

version: "5.0"
last_updated: "2025-07-09"
environment: "prod"

# Official port allocations - NO CONFLICTS
mcp_servers:
  tier_1_primary:
    ai_memory:
      port: 9000
      status: active
      capabilities: [MEMORY, EMBEDDING, SEARCH, ANALYTICS]
      owner: core_team
      
    snowflake_unified:
      port: 9001
      status: active
      capabilities: [ANALYTICS, EMBEDDING, SEARCH, COMPLETION]
      owner: data_team
      
    gong_v2:
      port: 9002
      status: active
      capabilities: [CALLS, TRANSCRIPTS, ANALYTICS]
      owner: sales_team
      
    hubspot_unified:
      port: 9003
      status: active
      capabilities: [CRM, CONTACTS, DEALS, ANALYTICS]
      owner: sales_team
      
    slack_v2:
      port: 9004
      status: active
      capabilities: [MESSAGING, CHANNELS, USERS, SEARCH]
      owner: ops_team

# Mark deprecated servers
deprecated_servers:
  - name: pinecone_server
    reason: "Replaced by Snowflake Cortex"
    removal_date: "2025-08-01"
    
  - name: weaviate_server
    reason: "Replaced by Snowflake Cortex"
    removal_date: "2025-08-01"
```

### 4. Create Configuration Validator

```python
# Create: scripts/validate_sophia_config.py
#!/usr/bin/env python3
"""
Validate Sophia AI configuration for conflicts and issues
"""

import yaml
import json
import sys
from pathlib import Path
from collections import defaultdict


def validate_mcp_ports():
    """Check for port conflicts across all configurations"""
    
    port_usage = defaultdict(list)
    
    # Load new unified config
    with open('config/sophia_mcp_unified.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    # Check all servers
    for tier, servers in config['mcp_servers'].items():
        for server_name, server_config in servers.items():
            port = server_config['port']
            port_usage[port].append(f"{server_name} ({tier})")
    
    # Find conflicts
    conflicts = []
    for port, servers in port_usage.items():
        if len(servers) > 1:
            conflicts.append(f"Port {port} conflict: {', '.join(servers)}")
    
    if conflicts:
        print("❌ Port conflicts found:")
        for conflict in conflicts:
            print(f"  - {conflict}")
        return False
    else:
        print("✅ No port conflicts found")
        return True


def validate_capabilities():
    """Ensure all required capabilities are covered"""
    
    required_capabilities = [
        'MEMORY', 'EMBEDDING', 'SEARCH', 'ANALYTICS',
        'CRM', 'CALLS', 'MESSAGING', 'CODE_ANALYSIS'
    ]
    
    # Load config and check capabilities
    with open('config/sophia_mcp_unified.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    available_capabilities = set()
    
    for tier, servers in config['mcp_servers'].items():
        for server_name, server_config in servers.items():
            if server_config['status'] == 'active':
                available_capabilities.update(server_config['capabilities'])
    
    missing = set(required_capabilities) - available_capabilities
    
    if missing:
        print(f"❌ Missing capabilities: {missing}")
        return False
    else:
        print("✅ All required capabilities are covered")
        return True


if __name__ == "__main__":
    valid = True
    valid &= validate_mcp_ports()
    valid &= validate_capabilities()
    
    sys.exit(0 if valid else 1)
```

### 5. Create Orchestrator Migration Guide

```markdown
# Create: docs/ORCHESTRATOR_MIGRATION_GUIDE.md

# Orchestrator Migration Guide

## For Developers

### Old Way (DEPRECATED)
```python
from backend.services.unified_chat_service import UnifiedChatService

chat_service = UnifiedChatService()
response = await chat_service.process_query(query, user_id, session_id)
```

### New Way (REQUIRED)
```python
from backend.services.sophia_unified_orchestrator import SophiaUnifiedOrchestrator

orchestrator = SophiaUnifiedOrchestrator()
response = await orchestrator.process_request(query, user_id, session_id, context)
```

## Migration Timeline

- **July 9, 2025**: Deprecation warnings added
- **July 16, 2025**: New orchestrator fully functional  
- **August 1, 2025**: Old orchestrators removed

## FAQ

**Q: Why consolidate orchestrators?**
A: To reduce complexity, improve performance, and provide a single, intelligent entry point.

**Q: What happens to my existing code?**
A: It will continue working with deprecation warnings until August 1, 2025.

**Q: How do I report issues?**
A: Create an issue with tag `orchestrator-migration`.
```

## Phase 1: Configuration Cleanup (Tomorrow)

### 1. Move Old Configs to Deprecated Folder

```bash
#!/bin/bash
# Create: scripts/deprecate_old_configs.sh

# Create deprecated folder
mkdir -p config/deprecated

# Move old configs with timestamp
mv config/unified_mcp_config.json config/deprecated/unified_mcp_config_20250709.json
mv config/cursor_enhanced_mcp_config.json config/deprecated/
mv config/consolidated_mcp_ports.json config/deprecated/
mv config/unified_mcp_ports.json config/deprecated/
mv config/mcp_server_inventory.json config/deprecated/

# Create symlink for backward compatibility
ln -s sophia_mcp_unified.yaml config/mcp_config.yaml

echo "✅ Old configurations moved to deprecated folder"
```

### 2. Update Environment Variables

```bash
# Add to: .env.example
# Sophia AI Unified Configuration
SOPHIA_CONFIG_PATH=config/sophia_mcp_unified.yaml
SOPHIA_ORCHESTRATOR=unified  # Options: unified, legacy
SOPHIA_DEPRECATION_WARNINGS=true
```

### 3. Create Health Check Dashboard

```python
# Create: scripts/sophia_health_check.py
#!/usr/bin/env python3
"""
Quick health check for Sophia AI components
"""

import asyncio
import aiohttp
from datetime import datetime
from rich.console import Console
from rich.table import Table


async def check_mcp_server(name: str, port: int) -> dict:
    """Check if MCP server is healthy"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"http://localhost:{port}/health",
                timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                return {
                    "name": name,
                    "port": port,
                    "status": "✅ Healthy" if response.status == 200 else f"⚠️  {response.status}",
                    "response_time": f"{response.headers.get('X-Response-Time', 'N/A')}ms"
                }
    except Exception as e:
        return {
            "name": name,
            "port": port,
            "status": f"❌ Error: {str(e)[:30]}",
            "response_time": "N/A"
        }


async def main():
    console = Console()
    
    # Key servers to check
    servers = [
        ("AI Memory", 9000),
        ("Snowflake Unified", 9001),
        ("Gong v2", 9002),
        ("HubSpot Unified", 9003),
        ("Slack v2", 9004),
        ("GitHub v2", 9005),
        ("Linear v2", 9006),
        ("Codacy", 3008),
    ]
    
    console.print(f"[bold]Sophia AI Health Check[/bold] - {datetime.now()}")
    
    # Check all servers in parallel
    results = await asyncio.gather(*[
        check_mcp_server(name, port) for name, port in servers
    ])
    
    # Display results
    table = Table(title="MCP Server Status")
    table.add_column("Server", style="cyan")
    table.add_column("Port", style="magenta")
    table.add_column("Status", style="green")
    table.add_column("Response Time", style="yellow")
    
    for result in results:
        table.add_row(
            result["name"],
            str(result["port"]),
            result["status"],
            result["response_time"]
        )
    
    console.print(table)


if __name__ == "__main__":
    asyncio.run(main())
```

## Phase 2: Create Unified Entry Point (Day 2)

### 1. Implement Basic Routing

```python
# Update: backend/services/sophia_unified_orchestrator.py

async def process_request(
    self,
    query: str,
    user_id: str,
    session_id: str,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Process any request through the unified orchestration pipeline.
    """
    
    start_time = date_manager.now()
    
    # Log the request
    logger.info(f"Processing request from user {user_id}: {query[:50]}...")
    
    # Step 1: Store in memory for learning
    await self.memory_service.add_conversation(
        user_id=user_id,
        session_id=session_id,
        user_message=query,
        ai_response=None  # Will update after processing
    )
    
    # Step 2: Analyze intent
    intent = await self._analyze_intent(query, context)
    
    # Step 3: Route to appropriate handler
    if intent["type"] == "business_intelligence":
        response = await self._handle_business_intelligence(query, intent, context)
    elif intent["type"] == "code_analysis":
        response = await self._handle_code_analysis(query, intent, context)
    elif intent["type"] == "infrastructure":
        response = await self._handle_infrastructure(query, intent, context)
    else:
        response = await self._handle_general(query, intent, context)
    
    # Step 4: Update memory with response
    await self.memory_service.update_conversation(
        session_id=session_id,
        ai_response=response["response"]
    )
    
    # Step 5: Add metadata
    end_time = date_manager.now()
    response["metadata"] = {
        "processing_time": (end_time - start_time).total_seconds(),
        "intent": intent,
        "orchestrator": "unified",
        "version": "1.0.0",
        "date": self.current_date.isoformat()
    }
    
    return response
```

### 2. Add Telemetry

```python
# Create: backend/services/orchestrator_telemetry.py

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional
import json


@dataclass
class OrchestrationMetrics:
    """Metrics for orchestration performance"""
    
    request_count: int = 0
    error_count: int = 0
    average_response_time: float = 0.0
    active_users: set = None
    mcp_server_usage: Dict[str, int] = None
    
    def __post_init__(self):
        if self.active_users is None:
            self.active_users = set()
        if self.mcp_server_usage is None:
            self.mcp_server_usage = {}
    
    def to_dict(self) -> dict:
        return {
            "request_count": self.request_count,
            "error_count": self.error_count,
            "average_response_time": self.average_response_time,
            "active_users": len(self.active_users),
            "mcp_server_usage": self.mcp_server_usage,
            "health_score": self.calculate_health_score()
        }
    
    def calculate_health_score(self) -> float:
        """Calculate overall health score (0-100)"""
        if self.request_count == 0:
            return 100.0
        
        error_rate = self.error_count / self.request_count
        performance_score = min(100, 100 * (1.0 / max(0.1, self.average_response_time)))
        
        return round((1 - error_rate) * 50 + performance_score * 0.5, 2)
```

## Success Criteria

### Day 1 Success
- [ ] Deprecation warnings added to all old orchestrators
- [ ] Unified configuration file created
- [ ] Configuration validator working
- [ ] Migration guide published

### Day 2 Success  
- [ ] Basic unified orchestrator working
- [ ] Health check dashboard operational
- [ ] Telemetry collecting data
- [ ] Old configs moved to deprecated folder

### Week 1 Success
- [ ] 50% of requests routing through unified orchestrator
- [ ] No new code using deprecated orchestrators
- [ ] All team members aware of migration
- [ ] Performance baseline established

## Command Summary

```bash
# Day 1 Commands
python scripts/validate_sophia_config.py
bash scripts/deprecate_old_configs.sh
python scripts/sophia_health_check.py

# Day 2 Commands
python -m backend.services.sophia_unified_orchestrator
python scripts/monitor_orchestrator_migration.py
```

---

**Remember**: Small, incremental improvements lead to big transformations. Start with these immediate actions and build momentum! 