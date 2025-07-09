#!/usr/bin/env python3
"""
Migrate all MCP servers to use the unified base class.
Updates imports, class inheritance, and configuration patterns.
"""

import os
import shutil
import re
from pathlib import Path
from typing import List, Dict, Any

def get_all_mcp_servers() -> List[Path]:
    """Get all MCP server directories"""
    mcp_servers_dir = Path("mcp-servers")
    servers = []
    
    for item in mcp_servers_dir.iterdir():
        if item.is_dir() and item.name != "base" and not item.name.startswith('.'):
            # Look for main server file
            server_files = list(item.glob("*_mcp_server.py"))
            if server_files:
                servers.append(item)
    
    return servers

def analyze_server_file(file_path: Path) -> Dict[str, Any]:
    """Analyze server file to understand current structure"""
    with open(file_path, 'r') as f:
        content = f.read()
    
    analysis = {
        "has_standalone_import": "standalone_mcp_base" in content,
        "has_enhanced_import": "enhanced_standardized_mcp_server" in content or "StandardizedMCPServer" in content,
        "has_fastapi": "FastAPI" in content,
        "has_mcp_tools": "@" in content and "tool" in content,
        "class_name": None,
        "base_class": None
    }
    
    # Find class definition
    class_match = re.search(r'class (\w+)\(([^)]+)\):', content)
    if class_match:
        analysis["class_name"] = class_match.group(1)
        analysis["base_class"] = class_match.group(2).strip()
    
    return analysis

def migrate_server(server_dir: Path, backup: bool = True):
    """Migrate a single server to use unified base"""
    
    server_files = list(server_dir.glob("*_mcp_server.py"))
    if not server_files:
        print(f"⚠️  No main server file found in {server_dir}")
        return
    
    main_file = server_files[0]
    print(f"\n📦 Migrating {server_dir.name}: {main_file.name}")
    
    # Analyze current structure
    analysis = analyze_server_file(main_file)
    print(f"   Current base: {analysis['base_class']}")
    
    if backup:
        backup_file = main_file.with_suffix('.py.backup')
        shutil.copy2(main_file, backup_file)
        print(f"   📋 Backed up to {backup_file}")
    
    # Read current content
    with open(main_file, 'r') as f:
        content = f.read()
    
    # Update imports - replace all old base imports
    old_import_patterns = [
        r'from backend\.mcp_servers\.base\..*? import .*?\n',
        r'from mcp_servers\.base\.standalone_mcp_base.*? import .*?\n',
        r'from mcp_servers\.base\.enhanced_standardized_mcp_server import .*?\n',
        r'from infrastructure\.mcp_servers\.base\..*? import .*?\n'
    ]
    
    new_import = "from mcp_servers.base.unified_mcp_base import UnifiedMCPServer, MCPServerConfig, ServiceMCPServer, AIEngineMCPServer, InfrastructureMCPServer\n"
    
    # Remove old imports
    for pattern in old_import_patterns:
        content = re.sub(pattern, '', content, flags=re.MULTILINE)
    
    # Add new import at the top after existing imports
    import_section = re.search(r'(import .*?\n)+', content)
    if import_section:
        insert_pos = import_section.end()
        content = content[:insert_pos] + new_import + content[insert_pos:]
    else:
        # Add at the beginning after docstring
        docstring_end = re.search(r'""".*?"""\s*\n', content, re.DOTALL)
        if docstring_end:
            insert_pos = docstring_end.end()
            content = content[:insert_pos] + new_import + content[insert_pos:]
        else:
            content = new_import + content
    
    # Update class inheritance
    if analysis["class_name"] and analysis["base_class"]:
        # Determine appropriate base class
        server_name_lower = server_dir.name.lower()
        if any(term in server_name_lower for term in ["snowflake", "ai", "cortex", "openai", "claude"]):
            new_base = "AIEngineMCPServer"
        elif any(term in server_name_lower for term in ["pulumi", "lambda", "infrastructure"]):
            new_base = "InfrastructureMCPServer"
        else:
            new_base = "ServiceMCPServer"
        
        # Replace class definition
        old_class_def = f"class {analysis['class_name']}({analysis['base_class']}):"
        new_class_def = f"class {analysis['class_name']}({new_base}):"
        content = content.replace(old_class_def, new_class_def)
        print(f"   🔄 Updated inheritance: {analysis['base_class']} → {new_base}")
    
    # Update __init__ method to use MCPServerConfig
    server_name = server_dir.name.replace('_', '-')
    
    # Find existing port number
    port_match = re.search(r'port["\s]*[=:]["\s]*(\d+)', content)
    port = port_match.group(1) if port_match else "9000"
    
    # Replace __init__ method
    init_pattern = r'def __init__\(self.*?\):.*?super\(\).__init__\([^)]*\)'
    new_init = f'''def __init__(self):
        config = MCPServerConfig(
            name="{server_name}",
            port={port},
            version="2.0.0"
        )
        super().__init__(config)'''
    
    content = re.sub(init_pattern, new_init, content, flags=re.DOTALL)
    
    # Update any direct FastAPI references to use self.app
    content = re.sub(r'app\s*=\s*FastAPI\([^)]*\)', '# FastAPI app created by unified base', content)
    
    # Write updated content
    with open(main_file, 'w') as f:
        f.write(content)
    
    print(f"   ✅ Migration complete")

def validate_migration(server_dir: Path) -> bool:
    """Validate that migration was successful"""
    server_files = list(server_dir.glob("*_mcp_server.py"))
    if not server_files:
        return False
    
    with open(server_files[0], 'r') as f:
        content = f.read()
    
    checks = [
        "unified_mcp_base" in content,
        "MCPServerConfig" in content,
        "super().__init__(config)" in content
    ]
    
    return all(checks)

def main():
    """Main migration function"""
    print("🚀 Starting MCP server migration to unified base...")
    
    servers = get_all_mcp_servers()
    print(f"Found {len(servers)} MCP servers to migrate")
    
    successful_migrations = 0
    failed_migrations = []
    
    for server_dir in servers:
        try:
            migrate_server(server_dir, backup=True)
            if validate_migration(server_dir):
                successful_migrations += 1
                print(f"   ✅ Validation passed")
            else:
                print(f"   ⚠️  Validation failed - may need manual review")
                failed_migrations.append(server_dir.name)
        except Exception as e:
            print(f"   ❌ Migration failed: {e}")
            failed_migrations.append(server_dir.name)
    
    print(f"\n📊 Migration Summary:")
    print(f"   ✅ Successful: {successful_migrations}/{len(servers)}")
    print(f"   ❌ Failed: {len(failed_migrations)}")
    
    if failed_migrations:
        print(f"   Failed servers: {', '.join(failed_migrations)}")
        print("   These may require manual review")
    
    if successful_migrations > 0:
        print(f"\n🧪 Next steps:")
        print("   1. Test migrated servers:")
        print("      python scripts/test_migrated_servers.py")
        print("   2. Review any failed migrations manually")
        print("   3. Update port configurations if needed")

if __name__ == "__main__":
    main() 