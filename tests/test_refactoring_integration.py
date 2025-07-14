"""
Comprehensive Integration Tests
Tests all refactored services and improvements
"""

import pytest
import asyncio
from typing import Dict, Any
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent))

class TestServiceIntegration:
    """Test integration of refactored services"""
    
    @pytest.mark.asyncio
    async def test_consolidated_services_import(self):
        """Test that consolidated services can be imported"""
        try:
            # Test chat services
            from backend.services.unified_chat_service import UnifiedChatService
            
            # Test memory services  
            from backend.services.unified_memory_service_primary import UnifiedMemoryService
            
            # Test orchestrator
            from backend.services.sophia_ai_unified_orchestrator import SophiaAIUnifiedOrchestrator
            
            # Test monitoring
            from backend.services.performance_monitoring_service import PerformanceMonitoringService
            
            assert True, "All consolidated services imported successfully"
            
        except ImportError as e:
            pytest.fail(f"Failed to import consolidated services: {e}")
    
    @pytest.mark.asyncio
    async def test_performance_monitoring(self):
        """Test performance monitoring functionality"""
        try:
            from backend.services.performance_monitoring_service import performance_monitor
            
            # Test tracking a request
            import time
            start_time = time.time()
            
            result = await performance_monitor.track_request("test_service", start_time, True)
            
            assert result["service"] == "test_service"
            assert result["success"] == True
            assert "response_time_ms" in result
            
        except Exception as e:
            pytest.fail(f"Performance monitoring test failed: {e}")
    
    @pytest.mark.asyncio  
    async def test_business_logic_validator(self):
        """Test business logic validation"""
        try:
            from backend.services.business_logic_validator import business_logic_validator
            
            # Test data validation
            test_data = {"amount": 100, "quantity": 5}
            result = await business_logic_validator.validate_service_logic(
                "test_service", "data_validation", test_data
            )
            
            assert result["valid"] == True
            assert result["service"] == "test_service"
            
        except Exception as e:
            pytest.fail(f"Business logic validator test failed: {e}")
    
    def test_portkey_gateway_import(self):
        """Test that Portkey gateway imports correctly"""
        try:
            from backend.services.portkey_gateway import PortkeyGateway
            gateway = PortkeyGateway()
            assert gateway is not None
            
        except Exception as e:
            pytest.fail(f"Portkey gateway test failed: {e}")
    
    def test_syntax_fixes(self):
        """Test that syntax errors are fixed"""
        import subprocess
        
        # Test personality engine
        result = subprocess.run([
            "python", "-m", "py_compile", "backend/services/personality_engine.py"
        ], capture_output=True)
        assert result.returncode == 0, "Personality engine has syntax errors"
        
        # Test qdrant connector
        result = subprocess.run([
            "python", "-m", "py_compile", "shared/utils/qdrant_gong_connector.py"  
        ], capture_output=True)
        assert result.returncode == 0, "Qdrant connector has syntax errors"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
