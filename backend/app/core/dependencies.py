"""
Unified dependencies for Sophia AI platform
"""
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from backend.app.core.config import settings
from backend.services.mcp_orchestration_service import MCPOrchestrationService
from backend.services.enhanced_unified_chat_service import EnhancedUnifiedChatService


# Security
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)]
) -> dict:
    """Get current user from token"""
    if not credentials:
        return {"user_id": "anonymous", "role": "guest"}
    
    # TODO: Implement actual token validation
    return {"user_id": "user123", "role": "user"}


# Services
_mcp_service = None
_chat_service = None


def get_mcp_service() -> MCPOrchestrationService:
    """Get MCP orchestration service singleton"""
    global _mcp_service
    if _mcp_service is None:
        _mcp_service = MCPOrchestrationService()
    return _mcp_service


async def get_chat_service() -> EnhancedUnifiedChatService:
    """Get chat service singleton"""
    global _chat_service
    if _chat_service is None:
        from backend.core.config_manager import ConfigManager
        config_manager = ConfigManager()
        _chat_service = EnhancedUnifiedChatService(config_manager)
        await _chat_service.initialize()
    return _chat_service


# Dependency aliases
CurrentUser = Annotated[dict, Depends(get_current_user)]
MCPService = Annotated[MCPOrchestrationService, Depends(get_mcp_service)]
ChatService = Annotated[EnhancedUnifiedChatService, Depends(get_chat_service)]
