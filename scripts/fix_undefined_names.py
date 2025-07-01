#!/usr/bin/env python3
"""
Fix Undefined Names in Sophia AI Core Code
Addresses F821 errors by adding missing imports and definitions
"""

import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent

# Mapping of undefined names to their imports
UNDEFINED_NAME_FIXES = {
    "MemoryCategory": {
        "import": "from backend.mcp_servers.base.memory_categories import MemoryCategory",
        "alternative": "category='SALES_CALL_INSIGHT'",  # Use string literal instead
    },
    "get_config_value": {
        "import": "from backend.core.auto_esc_config import get_config_value",
    },
    "connection_manager": {
        "import": "from backend.core.unified_connection_manager import UnifiedConnectionManager",
        "fix": "self.connection_manager",  # Usually it's a class attribute
    },
    "cache_manager": {
        "import": "from backend.core.cache_manager import CacheManager",
        "fix": "self.cache_manager",  # Usually it's a class attribute
    },
    "StreamingService": {
        "import": "from backend.services.streaming_service import StreamingService",
    },
    "IntegratedConversationRecord": {
        "import": "from backend.models.conversation import IntegratedConversationRecord",
    },
    "Cortex": {
        "import": "from snowflake.cortex import Cortex",
    },
    "gc": {
        "import": "import gc",
    },
    "datetime": {
        "import": "from datetime import datetime",
    },
    "shlex": {
        "import": "import shlex",
    },
}

def fix_undefined_names():
    """Fix undefined names in Python files."""
    print("🔍 Fixing undefined names in Sophia AI core code...")

    files_to_fix = {
        "backend/agents/specialized/snowflake_admin_agent.py": ["connection_manager"],
        "backend/api/foundational_knowledge_routes.py": ["cache_manager"],
        "backend/app/working_app.py": ["StreamingService"],
        "backend/integrations/portkey_gateway_service.py": ["title"],
        "backend/mcp_servers/enhanced_ai_memory_mcp_server.py": ["MemoryCategory"],
        "backend/mcp_servers/optimized_mcp_server.py": ["gc"],
        "backend/scripts/batch_embed_data.py": ["query_params"],
        "backend/services/comprehensive_memory_service.py": ["IntegratedConversationRecord"],
        "backend/services/cortex_agent_service.py": ["Cortex", "model", "text_content", "query_embedding", "similarity_threshold", "top_k"],
        "implement_phase1b_services.py": ["datetime"],
        "scripts/security_fixes_examples.py": ["shlex"],
        "ui-ux-agent/mcp-servers/langchain-agents/ui_ux_agent.py": ["get_config_value"],
        "ui-ux-agent/start_ui_ux_agent_system.py": ["get_config_value"],
    }

    fixed_count = 0

    for filepath, undefined_names in files_to_fix.items():
        full_path = PROJECT_ROOT / filepath

        if not full_path.exists():
            print(f"⚠️  File not found: {filepath}")
            continue

        print(f"\n📝 Fixing {filepath}...")

        try:
            with open(full_path, encoding='utf-8') as f:
                content = f.read()

            original_content = content

            # Add missing imports at the top of the file
            imports_to_add = []

            for name in undefined_names:
                if name in UNDEFINED_NAME_FIXES:
                    fix_info = UNDEFINED_NAME_FIXES[name]

                    # Check if we need to add an import
                    if "import" in fix_info and fix_info["import"] not in content:
                        imports_to_add.append(fix_info["import"])

                    # Apply specific fixes
                    if name == "connection_manager" and "self.connection_manager" not in content:
                        # Replace connection_manager with self.connection_manager
                        content = re.sub(r'\bconnection_manager\b', 'self.connection_manager', content)
                        print(f"  ✓ Fixed {name} -> self.{name}")

                    elif name == "cache_manager" and "self.cache_manager" not in content:
                        # Replace cache_manager with self.cache_manager
                        content = re.sub(r'\bcache_manager\b', 'self.cache_manager', content)
                        print(f"  ✓ Fixed {name} -> self.{name}")

                    elif name == "MemoryCategory":
                        # Replace MemoryCategory.SALES_CALL_INSIGHT with string literal
                        content = re.sub(r'MemoryCategory\.SALES_CALL_INSIGHT', "'SALES_CALL_INSIGHT'", content)
                        print(f"  ✓ Fixed {name} enum to string literal")

                    elif name == "query_params":
                        # Fix the conditional expression
                        content = re.sub(
                            r'query_params if "query_params" in locals\(\) else \(\)',
                            '()',
                            content
                        )
                        print(f"  ✓ Fixed {name} conditional")

                    elif name in ["model", "text_content", "query_embedding", "similarity_threshold", "top_k"]:
                        # These are likely function parameters that need to be defined
                        print(f"  ⚠️  {name} needs manual review - likely missing function parameter")

            # Add imports after the shebang and module docstring
            if imports_to_add:
                lines = content.split('\n')
                insert_pos = 0

                # Skip shebang
                if lines[0].startswith('#!'):
                    insert_pos = 1

                # Skip module docstring
                if insert_pos < len(lines) and lines[insert_pos].strip().startswith('"""'):
                    for i in range(insert_pos + 1, len(lines)):
                        if lines[i].strip().endswith('"""'):
                            insert_pos = i + 1
                            break

                # Find the first import statement
                for i in range(insert_pos, len(lines)):
                    if lines[i].strip().startswith(('import ', 'from ')):
                        insert_pos = i
                        break
                    elif lines[i].strip() and not lines[i].strip().startswith('#'):
                        # If we hit non-import code, insert before it
                        insert_pos = i
                        break

                # Insert the new imports
                for imp in imports_to_add:
                    lines.insert(insert_pos, imp)
                    print(f"  ✓ Added import: {imp}")
                    insert_pos += 1

                content = '\n'.join(lines)

            # Write back if changed
            if content != original_content:
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                fixed_count += 1
                print(f"  ✅ Fixed {filepath}")
            else:
                print(f"  ℹ️  No changes needed for {filepath}")

        except Exception as e:
            print(f"  ❌ Error fixing {filepath}: {e}")

    print(f"\n✅ Fixed {fixed_count} files")
    return fixed_count

if __name__ == "__main__":
    fix_undefined_names()
