#!/usr/bin/env python3
"""
Phase 1 Local Development Setup
Sets up Memory & Learning components for local development
"""

import asyncio
import subprocess
import sys
import time
from pathlib import Path
import json
import logging
from typing import Dict, List, Tuple, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Phase1LocalSetup:
    """Handles Phase 1 setup for local development"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.setup_status = {
            "directories": False,
            "config": False,
            "services": False,
            "integration": False
        }
    
    def create_directories(self) -> bool:
        """Create necessary directories"""
        logger.info("📁 Creating directories...")
        
        directories = [
            self.project_root / "data" / "mem0",
            self.project_root / "logs" / "mem0",
            self.project_root / "config" / "mem0"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.info(f"✅ Created: {directory}")
        
        self.setup_status["directories"] = True
        return True
    
    def update_configurations(self) -> bool:
        """Update configuration files"""
        logger.info("⚙️ Updating configurations...")
        
        # Update unified MCP ports configuration
        mcp_config_path = self.project_root / "config" / "unified_mcp_ports.json"
        
        if mcp_config_path.exists():
            with open(mcp_config_path, 'r') as f:
                mcp_config = json.load(f)
        else:
            logger.error(f"MCP config not found: {mcp_config_path}")
            return False
        
        # Add new servers to active_servers
        new_servers = {
            "prompt_optimizer": 9030,
            "mem0_bridge": 9031
        }
        
        if "active_servers" not in mcp_config:
            mcp_config["active_servers"] = {}
        
        mcp_config["active_servers"].update(new_servers)
        
        # Update server_status
        if "server_status" not in mcp_config:
            mcp_config["server_status"] = {
                "operational": [],
                "development": [],
                "planned": []
            }
        
        # Add prompt_optimizer to development
        if "prompt_optimizer" not in mcp_config["server_status"]["development"]:
            mcp_config["server_status"]["development"].append("prompt_optimizer")
        
        # Add mem0_bridge to planned
        if "mem0_bridge" not in mcp_config["server_status"]["planned"]:
            mcp_config["server_status"]["planned"].append("mem0_bridge")
        
        # Update last_updated
        mcp_config["last_updated"] = time.strftime('%Y-%m-%dT%H:%M:%S')
        
        # Save updated config
        with open(mcp_config_path, 'w') as f:
            json.dump(mcp_config, f, indent=2)
        
        logger.info("✅ MCP configuration updated")
        
        # Create local Mem0 config
        mem0_config = {
            "version": "0.1",
            "llm": {
                "provider": "openai",
                "config": {
                    "model": "gpt-4",
                    "temperature": 0.1
                }
            },
            "embedder": {
                "provider": "openai",
                "config": {
                    "model": "text-embedding-3-large"
                }
            },
            "vector_store": {
                "provider": "local",
                "config": {
                    "path": str(self.project_root / "data" / "mem0" / "vectors")
                }
            },
            "history_db": {
                "provider": "sqlite",
                "config": {
                    "path": str(self.project_root / "data" / "mem0" / "history.db")
                }
            }
        }
        
        mem0_config_path = self.project_root / "config" / "mem0" / "local_config.json"
        mem0_config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(mem0_config_path, 'w') as f:
            json.dump(mem0_config, f, indent=2)
        
        logger.info("✅ Mem0 local configuration created")
        
        self.setup_status["config"] = True
        return True
    
    def create_service_stubs(self) -> bool:
        """Create service stub files for local development"""
        logger.info("🔧 Creating service stubs...")
        
        # Create a simple Mem0 mock service
        mock_service_path = self.project_root / "backend" / "services" / "mem0_mock_service.py"
        
        mock_service_code = '''"""
Mock Mem0 Service for Local Development
Provides in-memory storage for testing without Kubernetes
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

logger = logging.getLogger(__name__)


class MockMem0Service:
    """Mock implementation of Mem0 for local development"""
    
    def __init__(self):
        self.memories: Dict[str, Dict[str, Any]] = {}
        self.user_memories: Dict[str, List[str]] = {}
        logger.info("✅ Mock Mem0 service initialized")
    
    async def store_conversation_memory(
        self,
        user_id: str,
        conversation: List[Dict[str, str]],
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Store conversation in memory"""
        memory_id = str(uuid4())
        
        self.memories[memory_id] = {
            "user_id": user_id,
            "conversation": conversation,
            "metadata": metadata or {},
            "created_at": datetime.now().isoformat()
        }
        
        if user_id not in self.user_memories:
            self.user_memories[user_id] = []
        self.user_memories[user_id].append(memory_id)
        
        logger.info(f"✅ Stored memory {memory_id} for user {user_id}")
        return memory_id
    
    async def recall_memories(
        self,
        user_id: str,
        query: str,
        limit: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Recall memories for a user"""
        if user_id not in self.user_memories:
            return []
        
        # Simple implementation: return most recent memories
        memory_ids = self.user_memories[user_id][-limit:]
        memories = []
        
        for memory_id in memory_ids:
            if memory_id in self.memories:
                memory = self.memories[memory_id].copy()
                memory["memory_id"] = memory_id
                memories.append(memory)
        
        logger.info(f"✅ Recalled {len(memories)} memories for user {user_id}")
        return memories
    
    async def initialize(self):
        """Initialize the service"""
        logger.info("✅ Mock Mem0 service ready")
        self.initialized = True
    
    async def close(self):
        """Close the service"""
        logger.info("✅ Mock Mem0 service closed")


# For local development, use the mock service
def get_mem0_service():
    """Get the Mem0 service instance"""
    return MockMem0Service()
'''
        
        with open(mock_service_path, 'w') as f:
            f.write(mock_service_code)
        
        logger.info(f"✅ Created mock service: {mock_service_path}")
        
        self.setup_status["services"] = True
        return True
    
    def test_integration(self) -> bool:
        """Test the integration"""
        logger.info("🧪 Testing integration...")
        
        try:
            # Test imports
            from backend.services.mem0_integration_service import Mem0IntegrationService
            from backend.workflows.enhanced_langgraph_patterns import LearningOrchestrator
            logger.info("✅ Production imports successful")
        except ImportError as e:
            logger.warning(f"Production import failed: {e}")
            logger.info("Trying mock service...")
            
            try:
                from backend.services.mem0_mock_service import MockMem0Service
                logger.info("✅ Mock service import successful")
            except ImportError as e2:
                logger.error(f"Mock import failed: {e2}")
                return False
        
        self.setup_status["integration"] = True
        return True
    
    def generate_setup_report(self) -> str:
        """Generate setup report"""
        report = [
            "\n" + "="*60,
            "PHASE 1 LOCAL DEVELOPMENT SETUP REPORT",
            "="*60,
            f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "Setup Status:",
            f"  • Directories: {'✅' if self.setup_status['directories'] else '❌'}",
            f"  • Configuration: {'✅' if self.setup_status['config'] else '❌'}",
            f"  • Services: {'✅' if self.setup_status['services'] else '❌'}",
            f"  • Integration: {'✅' if self.setup_status['integration'] else '❌'}",
            "",
            "Next Steps:",
            "  1. Start the Prompt Optimizer MCP server:",
            f"     cd {self.project_root}",
            "     python mcp-servers/prompt_optimizer/prompt_optimizer_mcp_server.py",
            "",
            "  2. Test the mock Mem0 service:",
            "     python -c \"from backend.services.mem0_mock_service import MockMem0Service; print('Success!')\"",
            "",
            "  3. Update your .env to use local development mode:",
            "     ENVIRONMENT=development",
            "     USE_MOCK_MEM0=true",
            "",
            "  4. Run the Snowflake SQL manually when ready:",
            f"     {self.project_root}/backend/snowflake_setup/mem0_integration.sql",
            "",
            "Local Development Benefits:",
            "  • No Kubernetes required",
            "  • In-memory storage for quick testing",
            "  • Fast iteration cycles",
            "  • Easy debugging",
            "="*60
        ]
        return "\n".join(report)
    
    async def setup(self) -> bool:
        """Run the local setup"""
        logger.info("🚀 Starting Phase 1 Local Development Setup")
        
        steps = [
            ("Directories", self.create_directories),
            ("Configuration", self.update_configurations),
            ("Service Stubs", self.create_service_stubs),
            ("Integration Test", self.test_integration)
        ]
        
        for step_name, step_func in steps:
            logger.info(f"\n📍 Step: {step_name}")
            success = step_func()
            
            if not success:
                logger.error(f"❌ {step_name} failed")
                break
            
            logger.info(f"✅ {step_name} completed")
        
        # Generate report
        report = self.generate_setup_report()
        print(report)
        
        # Save report
        report_path = self.project_root / "PHASE1_LOCAL_SETUP_REPORT.md"
        with open(report_path, 'w') as f:
            f.write(report)
        
        logger.info(f"\n📄 Report saved to: {report_path}")
        
        all_success = all(self.setup_status.values())
        if all_success:
            logger.info("\n🎉 Local development setup completed successfully!")
        else:
            logger.warning("\n⚠️  Setup completed with issues")
        
        return all_success


async def main():
    """Main function"""
    setup = Phase1LocalSetup()
    success = await setup.setup()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main()) 