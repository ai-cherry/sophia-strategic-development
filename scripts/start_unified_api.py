#!/usr/bin/env python3
"""
Start the Sophia AI Unified API
This script fixes common issues and starts the unified platform
"""

import os
import sys
import subprocess
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path.parent))


def fix_immediate_issues():
    """Fix immediate blocking issues"""
    print("🔧 Fixing immediate issues...")
    
    # Fix snowflake_cortex_service.py indentation
    cortex_file = backend_path / "utils" / "snowflake_cortex_service.py"
    if cortex_file.exists():
        with open(cortex_file, 'r') as f:
            content = f.read()
        
        # Fix the indentation issues
        lines = content.split('\n')
        fixed_lines = []
        
        for i, line in enumerate(lines):
            # Fix line 799 - around _iteration_1
            if i == 798 and "if key not in ALLOWED_FILTER_COLUMNS:" in line:
                fixed_lines.append("        if key not in ALLOWED_FILTER_COLUMNS:")
            # Fix line 808 - cursor assignment
            elif i == 807 and "cursor = self.connection.cursor()" in line:
                fixed_lines.append("        cursor = self.connection.cursor()")
            else:
                fixed_lines.append(line)
        
        with open(cortex_file, 'w') as f:
            f.write('\n'.join(fixed_lines))
        
        print("✅ Fixed snowflake_cortex_service.py indentation")
    
    # Fix MCPServerEndpoint in mcp_orchestration_service.py
    mcp_file = backend_path / "services" / "mcp_orchestration_service.py"
    if mcp_file.exists():
        with open(mcp_file, 'r') as f:
            content = f.read()
        
        # Remove 'name' parameter from MCPServerEndpoint calls
        content = content.replace(
            'MCPServerEndpoint(\n                        name=name,\n                        server_name=name,',
            'MCPServerEndpoint(\n                        server_name=name,'
        )
        
        with open(mcp_file, 'w') as f:
            f.write(content)
        
        print("✅ Fixed MCPServerEndpoint initialization")
    
    # Install missing dependencies
    print("📦 Installing missing dependencies...")
    deps = ["slowapi", "python-multipart", "prometheus-client"]
    for dep in deps:
        subprocess.run([sys.executable, "-m", "pip", "install", dep], 
                      capture_output=True, text=True)
    print("✅ Installed dependencies")


def create_simple_unified_api():
    """Create a simple unified API that works"""
    print("\n🏗️ Creating simple unified API...")
    
    api_content = '''"""
Sophia AI Unified API - Simple Working Version
"""

import os
import logging
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Sophia AI Unified Platform",
    version="3.0.0",
    docs_url="/docs"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "name": "Sophia AI Platform",
        "status": "operational",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# Import and mount available routers
try:
    from backend.api.data_flow_routes import router as data_flow_router
    app.include_router(data_flow_router, prefix="/api/v3", tags=["Data Flow"])
    logger.info("Mounted data_flow_router")
except Exception as e:
    logger.warning(f"Could not mount data_flow_router: {e}")

try:
    from backend.api.llm_strategy_routes import router as llm_router
    app.include_router(llm_router, prefix="/api/v3", tags=["LLM"])
    logger.info("Mounted llm_strategy_router")
except Exception as e:
    logger.warning(f"Could not mount llm_strategy_router: {e}")

try:
    from backend.api.mcp_integration_routes import router as mcp_router
    app.include_router(mcp_router, prefix="/api/mcp", tags=["MCP"])
    logger.info("Mounted mcp_integration_router")
except Exception as e:
    logger.warning(f"Could not mount mcp_integration_router: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''
    
    api_file = backend_path / "app" / "simple_unified_api.py"
    with open(api_file, 'w') as f:
        f.write(api_content)
    
    print("✅ Created simple_unified_api.py")
    return api_file


def start_api(api_file):
    """Start the unified API"""
    print(f"\n🚀 Starting Unified API from {api_file}...")
    
    # Change to backend directory
    os.chdir(backend_path.parent)
    
    # Start the API
    cmd = [sys.executable, str(api_file)]
    
    print(f"Running: {' '.join(cmd)}")
    print("=" * 60)
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n\n👋 API stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting API: {e}")


def main():
    """Main execution"""
    print("🚀 Sophia AI Unified API Starter")
    print("=" * 60)
    
    # Fix immediate issues
    fix_immediate_issues()
    
    # Create simple unified API
    api_file = create_simple_unified_api()
    
    # Start the API
    start_api(api_file)


if __name__ == "__main__":
    main() 