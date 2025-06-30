#!/usr/bin/env python3
"""
Fix Critical Syntax Errors Script
Addresses syntax errors and missing imports introduced by comprehensive secret update
"""

import re
import logging
from pathlib import Path
from typing import List

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CriticalSyntaxFixer:
    def __init__(self):
        self.root_path = Path(__file__).parent.parent
        self.fixed_files = []

    def fix_syntax_errors(self) -> None:
        """Fix critical syntax errors in the codebase"""
        
        # Fix the invalid assignment syntax errors
        syntax_error_files = [
            "start_mcp_servers.py",
            "start_enhanced_mcp_servers.py"
        ]
        
        for filename in syntax_error_files:
            file_path = self.root_path / filename
            if file_path.exists():
                self.fix_invalid_assignments(file_path)
                
        # Fix missing imports
        self.fix_missing_imports()
        
        # Fix specific files with issues
        self.fix_specific_files()

    def fix_invalid_assignments(self, file_path: Path) -> None:
        """Fix invalid assignment statements"""
        logger.info(f"🔧 Fixing invalid assignments in {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Fix the invalid syntax: get_config_value("key") = get_config_value("key")
            # Should be: os.environ["KEY"] = get_config_value("key") or ""
            patterns = [
                (r'get_config_value\("openai_api_key"\) = get_config_value\("openai_api_key"\)',
                 'os.environ["OPENAI_API_KEY"] = get_config_value("openai_api_key") or ""'),
                (r'get_config_value\("pinecone_api_key"\) = get_config_value\("pinecone_api_key"\)',
                 'os.environ["PINECONE_API_KEY"] = get_config_value("pinecone_api_key") or ""'),
            ]
            
            original_content = content
            for pattern, replacement in patterns:
                content = re.sub(pattern, replacement, content)
                
            # Add missing imports if get_config_value is used
            if "get_config_value" in content and "from backend.core.auto_esc_config import get_config_value" not in content:
                # Insert import after existing imports
                lines = content.split('\n')
                import_inserted = False
                for i, line in enumerate(lines):
                    if line.startswith('import os') or line.startswith('from pathlib'):
                        lines.insert(i + 1, "from backend.core.auto_esc_config import get_config_value")
                        import_inserted = True
                        break
                        
                if not import_inserted:
                    # Insert at the beginning after shebang/docstring
                    for i, line in enumerate(lines):
                        if not line.startswith('#') and not line.startswith('"""') and not line.startswith("'''") and line.strip():
                            lines.insert(i, "from backend.core.auto_esc_config import get_config_value")
                            break
                            
                content = '\n'.join(lines)
                
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.fixed_files.append(str(file_path))
                logger.info(f"✅ Fixed {file_path}")
                
        except Exception as e:
            logger.error(f"❌ Error fixing {file_path}: {e}")

    def fix_missing_imports(self) -> None:
        """Fix missing imports throughout the codebase"""
        logger.info("🔧 Fixing missing imports...")
        
        # Files that need get_config_value import
        files_needing_get_config_value = [
            "scripts/vercel_optimization.py",
            "ui-ux-agent/mcp-servers/langchain-agents/ui_ux_agent.py",
            "ui-ux-agent/start_ui_ux_agent_system.py",
            "sophia_standalone_server.py"
        ]
        
        for filename in files_needing_get_config_value:
            file_path = self.root_path / filename
            if file_path.exists():
                self.add_import_if_missing(file_path, "from backend.core.auto_esc_config import get_config_value")
                
        # Files that need UTC import
        utc_files = [
            "ui-ux-agent/dashboard_deployment_automation.py",
            "ui-ux-agent/dashboard_takeover_implementation.py", 
            "ui-ux-agent/mcp-servers/figma-dev-mode/figma_mcp_server.py",
            "ui-ux-agent/mcp-servers/langchain-agents/ui_ux_agent.py",
            "ui-ux-agent/phase2_enhancements.py"
        ]
        
        for filename in utc_files:
            file_path = self.root_path / filename
            if file_path.exists():
                self.add_import_if_missing(file_path, "from datetime import UTC")
                
        # Files that need os import
        os_files = [
            "sophia_standalone_server.py"
        ]
        
        for filename in os_files:
            file_path = self.root_path / filename
            if file_path.exists():
                self.add_import_if_missing(file_path, "import os")

    def add_import_if_missing(self, file_path: Path, import_statement: str) -> None:
        """Add import statement if not already present"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            if import_statement in content:
                return
                
            # Insert import at appropriate location
            lines = content.split('\n')
            import_inserted = False
            
            # Find the right place to insert the import
            for i, line in enumerate(lines):
                if (line.startswith('import ') or line.startswith('from ')) and 'datetime' in line:
                    if 'UTC' in import_statement:
                        # Replace existing datetime import with extended one
                        if line.startswith('from datetime import'):
                            if 'UTC' not in line:
                                lines[i] = line.rstrip() + ', UTC'
                                import_inserted = True
                                break
                elif line.startswith('import os') and 'import os' in import_statement:
                    return  # os already imported
                elif line.startswith('from backend.core.auto_esc_config') and 'get_config_value' in import_statement:
                    return  # get_config_value already imported
                    
            if not import_inserted:
                # Find last import line and insert after it
                last_import_idx = -1
                for i, line in enumerate(lines):
                    if line.startswith('import ') or line.startswith('from '):
                        last_import_idx = i
                        
                if last_import_idx >= 0:
                    lines.insert(last_import_idx + 1, import_statement)
                else:
                    # Insert at the beginning
                    lines.insert(0, import_statement)
                    
                import_inserted = True
                
            if import_inserted:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(lines))
                self.fixed_files.append(str(file_path))
                logger.info(f"✅ Added import to {file_path}")
                
        except Exception as e:
            logger.error(f"❌ Error adding import to {file_path}: {e}")

    def fix_specific_files(self) -> None:
        """Fix specific known issues in files"""
        
        # Fix f-string escape sequence issue in demo_dashboard_integration.py
        demo_file = self.root_path / "ui-ux-agent/demo_dashboard_integration.py"
        if demo_file.exists():
            try:
                with open(demo_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Fix the f-string escape sequence
                old_pattern = r"f\"      \.\.\. \(\{len\(component\['component_code'\]\.split\('\\n'\)\) - 10\} more lines\)\""
                new_pattern = 'f"      ... ({len(component[\'component_code\'].split(chr(10))) - 10} more lines)"'
                
                content = content.replace(
                    "f\"      ... ({len(component['component_code'].split('\\n')) - 10} more lines)\"",
                    'f"      ... ({len(component[\'component_code\'].split(chr(10))) - 10} more lines)"'
                )
                
                with open(demo_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                    
                self.fixed_files.append(str(demo_file))
                logger.info(f"✅ Fixed f-string issue in {demo_file}")
                
            except Exception as e:
                logger.error(f"❌ Error fixing {demo_file}: {e}")

    def run(self) -> None:
        """Run the critical syntax fixes"""
        logger.info("🚀 Starting critical syntax error fixes...")
        
        self.fix_syntax_errors()
        
        logger.info(f"\n{'='*60}")
        logger.info("📈 CRITICAL FIXES SUMMARY")
        logger.info(f"{'='*60}")
        logger.info(f"Files Fixed: {len(self.fixed_files)}")
        
        if self.fixed_files:
            logger.info("\n✅ Fixed Files:")
            for file_path in self.fixed_files:
                logger.info(f"  - {file_path}")
                
            logger.info(f"\n🎯 SUCCESS: Fixed {len(self.fixed_files)} critical issues")
            logger.info("🔄 Next: Re-run ruff check to verify fixes")
        else:
            logger.info("\n📍 No critical fixes needed")

if __name__ == "__main__":
    fixer = CriticalSyntaxFixer()
    fixer.run() 