"""
Unified dependencies for Sophia AI platform
"""

from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from infrastructure.services.enhanced_unified_chat_service import (
    EnhancedSophiaUnifiedOrchestrator,
)
from infrastructure.services.mcp_orchestration_service import MCPOrchestrationService

# Security
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
) -> dict:
    """Get current user from token"""
    if not credentials:
        return {"user_id": "anonymous", "role": "guest"}

    # TODO: [ARCH-001] Implement placeholder functionality actual token validation
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


async def get_chat_service() -> EnhancedSophiaUnifiedOrchestrator:
    """Get chat service singleton"""
    global _chat_service
    if _chat_service is None:
        _chat_service = EnhancedSophiaUnifiedOrchestrator()
        await _chat_service.initialize()
    return _chat_service


# Dependency aliases
CurrentUser = Annotated[dict, Depends(get_current_user)]
MCPService = Annotated[MCPOrchestrationService, Depends(get_mcp_service)]
ChatService = Annotated[EnhancedSophiaUnifiedOrchestrator, Depends(get_chat_service)]
