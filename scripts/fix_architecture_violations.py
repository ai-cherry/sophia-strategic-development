import os
import re
from pathlib import Path

class ArchitectureFixer:
    def __init__(self):
        self.fixes_applied = 0
        
        # Map infrastructure services to core interfaces
        self.interface_mappings = {
            'infrastructure.services.unified_sophia_service': 'core.ports.sophia_service',
            'infrastructure.services.unified_chat_service': 'core.ports.chat_service',
            'infrastructure.services.enhanced_unified_chat_service': 'core.ports.chat_service',
            'infrastructure.services.foundational_knowledge_service': 'core.ports.knowledge_service',
            'infrastructure.services.unified_llm_service': 'core.ports.llm_service',
            'infrastructure.services.mcp_orchestration_service': 'core.ports.mcp_orchestration',
            'infrastructure.services.mem0_integration_service': 'core.ports.memory_service',
            'infrastructure.security.audit_logger': 'core.ports.audit_logger',
            'infrastructure.security.ephemeral_credentials': 'core.ports.credentials',
            'infrastructure.security.rbac': 'core.ports.rbac',
            'infrastructure.mcp_servers.enhanced_ai_memory_mcp_server': 'core.ports.memory_mcp',
            'infrastructure.mcp_servers.base.standardized_mcp_server': 'core.ports.mcp_server',
        }
    
    def create_interface_files(self):
        """Create interface files in core/ports"""
        os.makedirs('core/ports', exist_ok=True)
        
        # Create __init__.py
        with open('core/ports/__init__.py', 'w') as f:
            f.write('"""Port interfaces for dependency inversion"""\n')
        
        # Create interface files
        interfaces = {
            'sophia_service.py': '''from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

class SophiaServiceInterface(ABC):
    """Interface for Sophia service"""
    
    @abstractmethod
    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process a request"""
        pass
''',
            'chat_service.py': '''from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, AsyncIterator

class ChatServiceInterface(ABC):
    """Interface for chat service"""
    
    @abstractmethod
    async def chat(self, message: str, context: Optional[Dict] = None) -> str:
        """Process a chat message"""
        pass
    
    @abstractmethod
    async def stream_chat(self, message: str, context: Optional[Dict] = None) -> AsyncIterator[str]:
        """Stream chat responses"""
        pass
''',
            'knowledge_service.py': '''from abc import ABC, abstractmethod
from typing import Any, Dict, List

class KnowledgeServiceInterface(ABC):
    """Interface for knowledge service"""
    
    @abstractmethod
    async def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search knowledge base"""
        pass
    
    @abstractmethod
    async def add_document(self, document: Dict[str, Any]) -> str:
        """Add document to knowledge base"""
        pass
''',
            'llm_service.py': '''from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

class LLMServiceInterface(ABC):
    """Interface for LLM service"""
    
    @abstractmethod
    async def generate(self, prompt: str, model: Optional[str] = None) -> str:
        """Generate text from prompt"""
        pass
    
    @abstractmethod
    async def embed(self, text: str) -> List[float]:
        """Generate embeddings"""
        pass
''',
            'mcp_orchestration.py': '''from abc import ABC, abstractmethod
from typing import Any, Dict, List

class MCPOrchestrationInterface(ABC):
    """Interface for MCP orchestration"""
    
    @abstractmethod
    async def execute_workflow(self, workflow: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an MCP workflow"""
        pass
    
    @abstractmethod
    async def list_capabilities(self) -> List[Dict[str, Any]]:
        """List available MCP capabilities"""
        pass
''',
            'memory_service.py': '''from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

class MemoryServiceInterface(ABC):
    """Interface for memory service"""
    
    @abstractmethod
    async def store_memory(self, key: str, value: Any, metadata: Optional[Dict] = None) -> None:
        """Store a memory"""
        pass
    
    @abstractmethod
    async def recall_memory(self, key: str) -> Optional[Any]:
        """Recall a memory"""
        pass
    
    @abstractmethod
    async def search_memories(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search memories"""
        pass
''',
            'audit_logger.py': '''from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

class AuditLoggerInterface(ABC):
    """Interface for audit logging"""
    
    @abstractmethod
    async def log_event(self, event_type: str, details: Dict[str, Any], user_id: Optional[str] = None) -> None:
        """Log an audit event"""
        pass
''',
            'credentials.py': '''from abc import ABC, abstractmethod
from typing import Dict, Optional

class CredentialsInterface(ABC):
    """Interface for credential management"""
    
    @abstractmethod
    async def get_credentials(self, service: str) -> Dict[str, str]:
        """Get credentials for a service"""
        pass
    
    @abstractmethod
    async def rotate_credentials(self, service: str) -> None:
        """Rotate credentials for a service"""
        pass
''',
            'rbac.py': '''from abc import ABC, abstractmethod
from typing import List, Optional

class RBACInterface(ABC):
    """Interface for role-based access control"""
    
    @abstractmethod
    async def check_permission(self, user_id: str, resource: str, action: str) -> bool:
        """Check if user has permission"""
        pass
    
    @abstractmethod
    async def get_user_roles(self, user_id: str) -> List[str]:
        """Get user roles"""
        pass
''',
            'memory_mcp.py': '''from abc import ABC, abstractmethod
from typing import Any, Dict, List

class MemoryMCPInterface(ABC):
    """Interface for Memory MCP server"""
    
    @abstractmethod
    async def store(self, data: Dict[str, Any]) -> str:
        """Store data in memory"""
        pass
    
    @abstractmethod
    async def retrieve(self, key: str) -> Dict[str, Any]:
        """Retrieve data from memory"""
        pass
''',
            'mcp_server.py': '''from abc import ABC, abstractmethod
from typing import Any, Dict, List

class MCPServerInterface(ABC):
    """Base interface for MCP servers"""
    
    @abstractmethod
    async def handle_request(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle an MCP request"""
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """Get server capabilities"""
        pass
'''
        }
        
        for filename, content in interfaces.items():
            with open(f'core/ports/{filename}', 'w') as f:
                f.write(content)
        
        print(f"Created {len(interfaces)} interface files in core/ports/")
    
    def fix_imports_in_file(self, file_path):
        """Fix imports in a single file"""
        with open(file_path, 'r') as f:
            content = f.read()
        
        original = content
        
        # Replace infrastructure imports with interface imports
        for infra_import, interface_import in self.interface_mappings.items():
            # Handle 'from X import Y' style
            content = re.sub(
                rf'from\s+{re.escape(infra_import)}(\s+import)',
                f'from {interface_import}\\1',
                content
            )
            
            # Handle 'import X' style
            content = re.sub(
                rf'import\s+{re.escape(infra_import)}',
                f'import {interface_import}',
                content
            )
        
        if content != original:
            with open(file_path, 'w') as f:
                f.write(content)
            self.fixes_applied += 1
            return True
        
        return False
    
    def fix_violations(self):
        """Fix architecture violations in API and Core layers"""
        # Fix files in API layer
        for root, dirs, files in os.walk('api'):
            if '__pycache__' in root:
                continue
                
            for file in files:
                if file.endswith('.py'):
                    file_path = Path(root) / file
                    if self.fix_imports_in_file(file_path):
                        print(f"Fixed imports in: {file_path}")
        
        # Fix files in Core layer
        for root, dirs, files in os.walk('core'):
            if '__pycache__' in root:
                continue
                
            for file in files:
                if file.endswith('.py'):
                    file_path = Path(root) / file
                    if self.fix_imports_in_file(file_path):
                        print(f"Fixed imports in: {file_path}")
    
    def create_adapters(self):
        """Create adapter implementations in infrastructure"""
        os.makedirs('infrastructure/adapters', exist_ok=True)
        
        # Create adapter template
        adapter_template = '''from {interface_module} import {interface_class}
from {implementation_module} import {implementation_class}

class {adapter_class}({interface_class}):
    """Adapter for {service_name}"""
    
    def __init__(self):
        self._impl = {implementation_class}()
    
    # Delegate all methods to implementation
    def __getattr__(self, name):
        return getattr(self._impl, name)
'''
        
        adapters = {
            'sophia_service_adapter.py': {
                'interface_module': 'core.ports.sophia_service',
                'interface_class': 'SophiaServiceInterface',
                'implementation_module': 'infrastructure.services.unified_sophia_service',
                'implementation_class': 'UnifiedSophiaService',
                'adapter_class': 'SophiaServiceAdapter',
                'service_name': 'Sophia Service'
            },
            'chat_service_adapter.py': {
                'interface_module': 'core.ports.chat_service',
                'interface_class': 'ChatServiceInterface',
                'implementation_module': 'infrastructure.services.unified_chat_service',
                'implementation_class': 'UnifiedChatService',
                'adapter_class': 'ChatServiceAdapter',
                'service_name': 'Chat Service'
            },
            # Add more adapters as needed
        }
        
        for filename, config in adapters.items():
            content = adapter_template.format(**config)
            with open(f'infrastructure/adapters/{filename}', 'w') as f:
                f.write(content)
        
        print(f"Created {len(adapters)} adapter files")

def main():
    fixer = ArchitectureFixer()
    
    print("Creating interface files...")
    fixer.create_interface_files()
    
    print("\nFixing architecture violations...")
    fixer.fix_violations()
    
    print("\nCreating adapter implementations...")
    fixer.create_adapters()
    
    print(f"\nFixed {fixer.fixes_applied} import violations")
    print("\nNote: You'll need to update dependency injection to use the adapters")

if __name__ == '__main__':
    main() 