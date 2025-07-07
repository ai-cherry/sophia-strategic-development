import os
import re
from pathlib import Path
import ast
from typing import Dict, Set, Tuple

class ImportUpdater:
    def __init__(self):
        self.import_mappings = self.create_import_mappings()
        self.circular_dependencies = set()
        
    def create_import_mappings(self) -> Dict[str, str]:
        """Create comprehensive import mappings"""
        return {
            # Direct mappings
            'backend.api': 'api',
            'backend.core': 'core',
            'backend.domain': 'domain',
            
            # Agent mappings
            'backend.agents.core': 'core.agents',
            'backend.agents.specialized': 'core.use_cases',
            
            # Orchestration mappings
            'backend.orchestration': 'core.workflows',
            'backend.workflows': 'core.workflows',
            
            # Application mappings
            'backend.application': 'core.application',
            
            # Model mappings
            'backend.models': 'domain.models',
            'backend.core.models': 'domain.models',
            
            # Infrastructure mappings
            'backend.integrations': 'infrastructure.integrations',
            'backend.mcp_servers': 'infrastructure.mcp_servers',
            'backend.etl': 'infrastructure.etl',
            'backend.monitoring': 'infrastructure.monitoring',
            'backend.security': 'infrastructure.security',
            'backend.database': 'infrastructure.database',
            
            # Service mappings (note: services are split between core and infrastructure)
            'backend.services': 'core.services',  # Default, but may be overridden
            
            # Utility mappings
            'backend.utils': 'shared.utils',
            'backend.prompts': 'shared.prompts',
            'backend.core.constants': 'shared.constants',
            'backend.core.config': 'shared.config',
            'backend.rag': 'shared.rag',
            
            # Presentation mappings
            'backend.presentation': 'api.serializers',
            
            # Main app mapping
            'backend.fastapi_main': 'api.main',
            'backend.app': 'api',
        }
    
    def update_file_imports(self, file_path: Path) -> bool:
        """Update imports in a single file"""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            original = content
            
            # Update imports using regex - more comprehensive patterns
            for old_import, new_import in self.import_mappings.items():
                # Handle 'from X import Y' style
                content = re.sub(
                    rf'from\s+{re.escape(old_import)}(\s+import|\.|$)',
                    rf'from {new_import}\1',
                    content
                )
                
                # Handle 'import X' style
                content = re.sub(
                    rf'import\s+{re.escape(old_import)}(\s|$|\.|,)',
                    rf'import {new_import}\1',
                    content
                )
            
            # Special handling for services that went to infrastructure
            infra_services = [
                'enhanced_unified_chat_service', 'snowflake_intelligence_service',
                'advanced_llm_service', 'enhanced_cortex_agent_service',
                'intelligent_query_router', 'mem0_integration_service',
                'payready_business_intelligence', 'enhanced_chat_context_service',
                'enhanced_knowledge_base_service', 'mcp_capability_router',
                'enhanced_portkey_llm_gateway', 'mcp_orchestration_service',
                'enhanced_cortex_service', 'foundational_knowledge_service',
                'enhanced_sentiment_analyzer', 'secure_action_service',
                'chimera_monitoring_service', 'unified_ai_orchestration_service',
                'data_source_manager', 'enhanced_ingestion_service',
                'unified_llm_service', 'unified_sophia_service',
                'sophia_ai_orchestrator', 'gptcache_service',
                'code_modification_service', 'unified_chat_service',
                'cortex_agent_service', 'cost_engineering_service',
                'semantic_layer_service', 'comprehensive_memory_service',
                'enhanced_snowflake_cortex_service', 'unified_service_registry',
                'enhanced_unified_intelligence_service', 'advanced_ui_ux_agent_service',
                'secure_credential_service', 'ui_generation_intent_handler',
                'vector_indexing_service', 'documentation_loader_service',
                'event_driven_ingestion_service', 'migration_orchestrator_client',
                'dynamic_orchestration_service', 'memory_preservation_service',
                'predictive_automation_service', 'sophia_agent_orchestrator',
                'unified_intelligence_service'
            ]
            
            # Update specific service imports that went to infrastructure
            for service in infra_services:
                content = re.sub(
                    rf'from\s+backend\.services\.{service}',
                    f'from infrastructure.services.{service}',
                    content
                )
                content = re.sub(
                    rf'from\s+core\.services\.{service}',
                    f'from infrastructure.services.{service}',
                    content
                )
            
            # Update relative imports to absolute
            content = self.convert_relative_imports(file_path, content)
            
            if content != original:
                with open(file_path, 'w') as f:
                    f.write(content)
                return True
            
            return False
            
        except Exception as e:
            print(f"Error updating {file_path}: {e}")
            return False
    
    def convert_relative_imports(self, file_path: Path, content: str) -> str:
        """Convert relative imports to absolute imports"""
        # Determine the module path
        module_parts = file_path.parts
        
        # Find which layer this file belongs to
        if 'api' in module_parts:
            base_module = 'api'
        elif 'core' in module_parts:
            base_module = 'core'
        elif 'domain' in module_parts:
            base_module = 'domain'
        elif 'infrastructure' in module_parts:
            base_module = 'infrastructure'
        elif 'shared' in module_parts:
            base_module = 'shared'
        else:
            return content
        
        # Don't convert relative imports for now - it's safer
        # This could be enhanced later if needed
        
        return content
    
    def run(self):
        """Run the import update process"""
        updated_files = 0
        
        # Update files in new structure
        for layer in ['api', 'core', 'domain', 'infrastructure', 'shared']:
            if not os.path.exists(layer):
                continue
                
            for root, dirs, files in os.walk(layer):
                if '__pycache__' in root:
                    continue
                    
                for file in files:
                    if file.endswith('.py'):
                        file_path = Path(root) / file
                        if self.update_file_imports(file_path):
                            updated_files += 1
                            print(f"Updated: {file_path}")
        
        # Also update any remaining files in backend directory
        if os.path.exists('backend'):
            for root, dirs, files in os.walk('backend'):
                if '__pycache__' in root:
                    continue
                    
                for file in files:
                    if file.endswith('.py'):
                        file_path = Path(root) / file
                        if self.update_file_imports(file_path):
                            updated_files += 1
                            print(f"Updated: {file_path}")
        
        # Update test files
        if os.path.exists('tests'):
            for root, dirs, files in os.walk('tests'):
                if '__pycache__' in root:
                    continue
                    
                for file in files:
                    if file.endswith('.py'):
                        file_path = Path(root) / file
                        if self.update_file_imports(file_path):
                            updated_files += 1
                            print(f"Updated: {file_path}")
        
        print(f"\nUpdated {updated_files} files")

if __name__ == '__main__':
    updater = ImportUpdater()
    updater.run() 