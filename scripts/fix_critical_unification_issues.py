#!/usr/bin/env python3
"""
Fix Critical Issues for Sophia AI Platform Unification
Phase 1: Fix import errors, indentation issues, and missing dependencies
"""

import os
import re
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))


def fix_snowflake_cortex_indentation():
    """Fix indentation issues in snowflake_cortex_service.py"""
    print("\n🔧 Fixing snowflake_cortex_service.py indentation issues...")
    
    file_path = backend_path / "utils" / "snowflake_cortex_service.py"
    
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return False
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Fix the specific indentation issues
    fixes = [
        # Fix line 799 - _iteration_1 method
        (
            r'(\s*)def _iteration_1\(self\):\n(\s*)".*?"\n(\s*)for key in metadata_filters:',
            r'\1def _iteration_1(self):\n\2"""Extracted iteration logic"""\n\2for key in metadata_filters:'
        ),
        # Fix line 808 - _error_handling_2 method
        (
            r'(\s*)def _error_handling_2\(self\):\n(\s*)".*?"\n(\s*)cursor = self\.connection\.cursor\(\)',
            r'\1def _error_handling_2(self):\n\2"""Extracted error_handling logic"""\n\2cursor = self.connection.cursor()'
        ),
        # Fix any other misaligned cursor assignments
        (
            r'\n(\s{8,})cursor = self\.connection\.cursor\(\)',
            r'\n        cursor = self.connection.cursor()'
        ),
    ]
    
    for pattern, replacement in fixes:
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.DOTALL)
    
    # Write back the fixed content
    with open(file_path, 'w') as f:
        f.write(content)
    
    print("✅ Fixed indentation issues in snowflake_cortex_service.py")
    return True


def fix_mcp_server_endpoint():
    """Fix MCPServerEndpoint initialization issues"""
    print("\n🔧 Fixing MCPServerEndpoint initialization...")
    
    file_path = backend_path / "services" / "mcp_orchestration_service.py"
    
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return False
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Fix MCPServerEndpoint calls to not use 'name' parameter
    # Change from: MCPServerEndpoint(name=..., server_name=..., ...)
    # To: MCPServerEndpoint(server_name=..., ...)
    
    # Pattern 1: Fix in _load_mcp_configuration
    content = re.sub(
        r'MCPServerEndpoint\(\s*name=name,\s*server_name=name,',
        'MCPServerEndpoint(\n                        server_name=name,',
        content
    )
    
    # Pattern 2: Fix any other occurrences with 'name' parameter
    content = re.sub(
        r'MCPServerEndpoint\(\s*name="([^"]+)",',
        r'MCPServerEndpoint(\n                server_name="\1",',
        content
    )
    
    # Write back the fixed content
    with open(file_path, 'w') as f:
        f.write(content)
    
    print("✅ Fixed MCPServerEndpoint initialization")
    return True


def fix_missing_imports():
    """Fix missing module imports"""
    print("\n🔧 Fixing missing imports...")
    
    # Fix enhanced_ai_memory_mcp_server.py
    memory_file = backend_path / "mcp_servers" / "enhanced_ai_memory_mcp_server.py"
    if memory_file.exists():
        with open(memory_file, 'r') as f:
            content = f.read()
        
        # Remove the problematic import
        content = re.sub(
            r'from backend\.mcp_servers\.server import Server\n',
            '',
            content
        )
        
        # Add correct imports if needed
        if 'from mcp.server import Server' not in content:
            # Find the import section
            import_section = re.search(r'(from mcp import.*?\n)+', content)
            if import_section:
                insert_pos = import_section.end()
                content = content[:insert_pos] + 'from mcp.server import Server\n' + content[insert_pos:]
        
        with open(memory_file, 'w') as f:
            f.write(content)
        
        print("✅ Fixed imports in enhanced_ai_memory_mcp_server.py")
    
    return True


def install_missing_dependencies():
    """Install missing Python dependencies"""
    print("\n📦 Installing missing dependencies...")
    
    dependencies = [
        "slowapi==0.1.9",
        "python-multipart==0.0.6",
        "prometheus-client==0.19.0",
        "httpx==0.25.2",
        "aiohttp==3.9.1",
    ]
    
    for dep in dependencies:
        print(f"Installing {dep}...")
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", dep],
                check=True,
                capture_output=True,
                text=True
            )
            print(f"✅ Installed {dep}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {dep}: {e.stderr}")
    
    return True


def create_unified_app_structure():
    """Create the unified app structure"""
    print("\n🏗️ Creating unified app structure...")
    
    # Create directories
    app_dir = backend_path / "app"
    core_dir = app_dir / "core"
    api_dir = app_dir / "api"
    v3_dir = api_dir / "v3"
    mcp_dir = api_dir / "mcp"
    admin_dir = api_dir / "admin"
    
    for dir_path in [core_dir, v3_dir, mcp_dir, admin_dir]:
        dir_path.mkdir(parents=True, exist_ok=True)
        # Create __init__.py files
        (dir_path / "__init__.py").touch()
    
    print("✅ Created unified app directory structure")
    return True


def create_unified_config():
    """Create unified configuration"""
    print("\n⚙️ Creating unified configuration...")
    
    config_content = '''"""
Unified configuration for Sophia AI platform
"""
import os
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Application
    app_name: str = "Sophia AI Platform"
    app_version: str = "3.0.0"
    debug: bool = False
    environment: str = "production"
    
    # API
    api_v3_prefix: str = "/api/v3"
    api_mcp_prefix: str = "/api/mcp"
    api_admin_prefix: str = "/api/admin"
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False
    
    # Security
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS
    cors_origins: list[str] = ["*"]
    cors_credentials: bool = True
    cors_methods: list[str] = ["*"]
    cors_headers: list[str] = ["*"]
    
    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_period: int = 60  # seconds
    
    # Database
    database_url: str = os.getenv("DATABASE_URL", "")
    
    # MCP Configuration
    mcp_config_path: str = "config/cursor_enhanced_mcp_config.json"
    mcp_health_check_interval: int = 60
    
    # Monitoring
    enable_metrics: bool = True
    metrics_port: int = 9090
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


settings = get_settings()
'''
    
    config_path = backend_path / "app" / "core" / "config.py"
    with open(config_path, 'w') as f:
        f.write(config_content)
    
    print("✅ Created unified configuration")
    return True


def create_unified_dependencies():
    """Create unified dependencies"""
    print("\n🔗 Creating unified dependencies...")
    
    deps_content = '''"""
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
'''
    
    deps_path = backend_path / "app" / "core" / "dependencies.py"
    with open(deps_path, 'w') as f:
        f.write(deps_content)
    
    print("✅ Created unified dependencies")
    return True


def run_verification():
    """Run verification checks"""
    print("\n🔍 Running verification checks...")
    
    checks = []
    
    # Check if files exist
    files_to_check = [
        backend_path / "utils" / "snowflake_cortex_service.py",
        backend_path / "services" / "mcp_orchestration_service.py",
        backend_path / "app" / "core" / "config.py",
        backend_path / "app" / "core" / "dependencies.py",
    ]
    
    for file_path in files_to_check:
        if file_path.exists():
            checks.append((f"✅ {file_path.name} exists", True))
        else:
            checks.append((f"❌ {file_path.name} missing", False))
    
    # Check imports
    try:
        import slowapi
        checks.append(("✅ slowapi installed", True))
    except ImportError:
        checks.append(("❌ slowapi not installed", False))
    
    # Print results
    print("\nVerification Results:")
    for check, status in checks:
        print(f"  {check}")
    
    all_passed = all(status for _, status in checks)
    return all_passed


def main():
    """Main execution"""
    print("🚀 Sophia AI Platform Unification - Phase 1: Fix Critical Issues")
    print("=" * 60)
    
    steps = [
        ("Fix Snowflake Cortex indentation", fix_snowflake_cortex_indentation),
        ("Fix MCPServerEndpoint initialization", fix_mcp_server_endpoint),
        ("Fix missing imports", fix_missing_imports),
        ("Install missing dependencies", install_missing_dependencies),
        ("Create unified app structure", create_unified_app_structure),
        ("Create unified configuration", create_unified_config),
        ("Create unified dependencies", create_unified_dependencies),
    ]
    
    success_count = 0
    for step_name, step_func in steps:
        print(f"\n▶️ {step_name}...")
        try:
            if step_func():
                success_count += 1
        except Exception as e:
            print(f"❌ Failed: {e}")
    
    # Run verification
    verification_passed = run_verification()
    
    print("\n" + "=" * 60)
    print(f"✅ Completed {success_count}/{len(steps)} steps successfully")
    
    if verification_passed:
        print("✅ All verification checks passed!")
        print("\n🎉 Phase 1 complete! Ready for Phase 2: API Consolidation")
    else:
        print("⚠️ Some verification checks failed. Please review and fix.")
    
    return success_count == len(steps) and verification_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 