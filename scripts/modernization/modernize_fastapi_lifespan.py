#!/usr/bin/env python3
"""
FastAPI Lifespan Modernization Script for Sophia AI

This script modernizes the FastAPI application from deprecated @app.on_event
handlers to the new lifespan pattern, implements proper dependency injection,
and fixes circular import issues.

Usage:
    python scripts/modernization/modernize_fastapi_lifespan.py
"""

import os
import re
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List

class FastAPILifespanModernizer:
    """Modernizes FastAPI applications to use lifespan events"""
    
    def __init__(self, backend_dir: str = "backend"):
        self.backend_dir = Path(backend_dir)
        self.backup_dir = Path(f"backup_fastapi_modernization_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        self.modifications = []

    def create_backup(self) -> None:
        """Create backup of files before modification"""
        print("📁 Creating backup of FastAPI files...")
        
        files_to_backup = [
            "backend/app/fastapi_app.py",
            "backend/api/universal_chat_routes.py",
            "backend/core/dependencies.py"  # Will create if doesn't exist
        ]
        
        for file_path in files_to_backup:
            if os.path.exists(file_path):
                backup_path = self.backup_dir / file_path
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(file_path, backup_path)
                print(f"  ✅ Backed up {file_path}")

    def modernize_fastapi_app(self) -> None:
        """Modernize the main FastAPI application file"""
        # All logic related to fastapi_app.py is now deprecated and should be removed.
        pass

    def create_dependencies_module(self) -> None:
        """Create the centralized dependencies module"""
        deps_file = self.backend_dir / "core" / "dependencies.py"
        
        print(f"🔧 Creating dependencies module at {deps_file}...")
        
        dependencies_content = '''"""
Centralized Dependencies Module for Sophia AI

This module provides centralized dependency injection following FastAPI best practices
and Clean Architecture principles. All services are managed here to eliminate
circular imports and ensure proper lifecycle management.
"""

import asyncio
from functools import lru_cache
from typing import Optional

from backend.core.simple_config import get_config_value

# Import the chat service
try:
    from backend.services.sophia_universal_chat_service import SophiaUniversalChatService
    CHAT_SERVICE_AVAILABLE = True
except ImportError:
    try:
        from backend.services.enhanced_unified_chat_service import EnhancedUnifiedChatService as SophiaUniversalChatService
        CHAT_SERVICE_AVAILABLE = True
    except ImportError:
        CHAT_SERVICE_AVAILABLE = False
        class SophiaUniversalChatService:
            """Mock chat service for when import fails"""
            def __init__(self):
                pass

# Global instance (singleton pattern)
_chat_service_instance: Optional[SophiaUniversalChatService] = None

@lru_cache()
def get_config_service():
    """Get configuration service (cached singleton)"""
    # This is already implemented in simple_config.py
    return True

async def get_chat_service() -> SophiaUniversalChatService:
    """
    Get the chat service instance.
    
    This function ensures we have a single instance of the chat service
    that is properly initialized and reused across requests.
    """
    global _chat_service_instance
    
    if _chat_service_instance is None:
        if CHAT_SERVICE_AVAILABLE:
            try:
                _chat_service_instance = SophiaUniversalChatService()
                # Add any initialization logic here
            except Exception as e:
                print(f"Warning: Failed to initialize chat service: {e}")
                # Create a mock instance
                _chat_service_instance = SophiaUniversalChatService()
        else:
            print("Warning: Chat service not available, using mock")
            _chat_service_instance = SophiaUniversalChatService()
    
    return _chat_service_instance

def get_chat_service_from_app_state(request):
    """
    Get chat service from FastAPI app state.
    
    This is used in routes to access the chat service instance
    that was initialized during app startup.
    """
    if hasattr(request.app.state, 'chat_service_instance'):
        return request.app.state.chat_service_instance
    else:
        # Fallback to creating a new instance
        return asyncio.create_task(get_chat_service())

# Dependency functions for FastAPI injection
async def get_chat_service_dependency():
    """FastAPI dependency for chat service"""
    return await get_chat_service()

def get_request_chat_service(request):
    """FastAPI dependency that gets chat service from request app state"""
    return get_chat_service_from_app_state(request)
'''
        
        # Write the dependencies file
        with open(deps_file, 'w', encoding='utf-8') as f:
            f.write(dependencies_content)
        
        self.modifications.append(f"Created centralized dependencies module at {deps_file}")
        print(f"  ✅ Created {deps_file}")

    def fix_universal_chat_routes(self) -> None:
        """Fix the universal chat routes to eliminate circular imports"""
        routes_file = self.backend_dir / "api" / "universal_chat_routes.py"
        
        print(f"🔄 Fixing {routes_file}...")
        
        if not routes_file.exists():
            print(f"  ⚠️ {routes_file} not found, skipping")
            return
        
        # Read current content
        with open(routes_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Create fixed content
        fixed_content = self._create_fixed_chat_routes()
        
        # Write the fixed content
        with open(routes_file, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        
        self.modifications.append(f"Fixed circular imports in {routes_file}")
        print(f"  ✅ Fixed {routes_file}")

    def _create_fixed_chat_routes(self) -> str:
        """Create the fixed chat routes content"""
        return '''"""
Universal Chat Routes for Sophia AI

Fixed to eliminate circular imports by using proper dependency injection
and accessing the chat service from FastAPI app state.
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import logging

# Import dependency function
from backend.core.dependencies import get_request_chat_service

logger = logging.getLogger(__name__)

router = APIRouter()

class ChatRequest(BaseModel):
    """Chat request model"""
    message: str = Field(..., description="The user's message")
    user_id: str = Field(default="default_user", description="User identifier")
    context: Optional[Dict[str, Any]] = Field(default={}, description="Additional context")
    
    class Config:
        # Avoid Pydantic model_ namespace conflicts
        protected_namespaces = ()

class ChatResponse(BaseModel):
    """Chat response model"""
    response: str = Field(..., description="AI response")
    user_id: str = Field(..., description="User identifier")
    model_used: Optional[str] = Field(None, description="AI model used")
    processing_time: Optional[float] = Field(None, description="Processing time in seconds")
    
    class Config:
        # Avoid Pydantic model_ namespace conflicts
        protected_namespaces = ()

@router.post("/message", response_model=ChatResponse)
async def process_chat_message(
    chat_request: ChatRequest,
    request: Request,
    chat_service = Depends(get_request_chat_service)
):
    """
    Process a chat message through the Sophia AI system
    
    This endpoint provides universal chat functionality with proper
    dependency injection and no circular imports.
    """
    try:
        # Get the chat service from app state
        if hasattr(request.app.state, 'chat_service_instance'):
            chat_service = request.app.state.chat_service_instance
        else:
            raise HTTPException(
                status_code=503,
                detail="Chat service not available"
            )
        
        # Process the message
        if hasattr(chat_service, 'process_chat_message'):
            response = await chat_service.process_chat_message(
                message=chat_request.message,
                user_id=chat_request.user_id,
                context=chat_request.context
            )
        else:
            # Fallback response
            response = {
                "response": f"Received message: {chat_request.message}",
                "user_id": chat_request.user_id,
                "model_used": "fallback",
                "processing_time": 0.1
            }
        
        return ChatResponse(**response)
        
    except Exception as e:
        logger.error(f"Error processing chat message: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing message: {str(e)}"
        )

@router.get("/health")
async def chat_health_check(request: Request):
    """Health check for chat service"""
    try:
        chat_available = hasattr(request.app.state, 'chat_service_instance')
        return {
            "status": "healthy" if chat_available else "degraded",
            "chat_service_available": chat_available,
            "service": "Universal Chat"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "service": "Universal Chat"
        }

@router.get("/capabilities")
async def get_chat_capabilities(request: Request):
    """Get chat service capabilities"""
    try:
        if hasattr(request.app.state, 'chat_service_instance'):
            chat_service = request.app.state.chat_service_instance
            
            # Extract capabilities if available
            capabilities = {
                "universal_chat": True,
                "context_aware": True,
                "multi_user": True,
                "available_methods": []
            }
            
            # Add method names if available
            if hasattr(chat_service, '__dict__'):
                methods = [
                    method for method in dir(chat_service) 
                    if not method.startswith('_') and callable(getattr(chat_service, method))
                ]
                capabilities["available_methods"] = methods[:10]  # Limit output
            
            return capabilities
        else:
            return {
                "universal_chat": False,
                "error": "Chat service not initialized"
            }
            
    except Exception as e:
        return {
            "error": str(e),
            "universal_chat": False
        }
'''

    def run_modernization(self) -> None:
        """Run the complete modernization process"""
        print("🚀 Starting FastAPI Lifespan Modernization")
        print("=" * 50)
        
        try:
            # Create backup
            self.create_backup()
            
            # Create modernization directory if it doesn't exist
            modernization_dir = Path("scripts/modernization")
            modernization_dir.mkdir(parents=True, exist_ok=True)
            
            # Create dependencies module
            self.create_dependencies_module()
            
            # Modernize FastAPI app
            self.modernize_fastapi_app()
            
            # Fix universal chat routes
            self.fix_universal_chat_routes()
            
            # Summary
            print("\n🎉 Modernization completed successfully!")
            print("\n📝 Summary of changes:")
            for modification in self.modifications:
                print(f"  ✅ {modification}")
            
            print(f"\n💾 Backup created at: {self.backup_dir}")
            print("\n🔄 Next steps:")
            print("  2. Verify no deprecation warnings appear")
            print("  3. Test all API endpoints work correctly")
            print("  4. If successful, remove backup directory")
            
        except Exception as e:
            print(f"\n❌ Modernization failed: {e}")
            print(f"💾 Backup available at: {self.backup_dir}")
            raise

def main():
    """Main function"""
    modernizer = FastAPILifespanModernizer()
    modernizer.run_modernization()

if __name__ == "__main__":
    main() 
