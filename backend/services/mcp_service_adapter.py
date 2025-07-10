"""
MCP Service Adapter
Alias for MCPOrchestrationAdapter to fix import issues
Date: July 10, 2025
"""

# Import the actual adapter class
from backend.services.mcp_orchestration_adapter import MCPOrchestrationAdapter

# Create alias for backward compatibility
MCPServiceAdapter = MCPOrchestrationAdapter

__all__ = ["MCPServiceAdapter", "MCPOrchestrationAdapter"]
