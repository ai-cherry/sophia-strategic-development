#!/usr/bin/env python3
"""Fix specific syntax errors in Python files."""

import re
from pathlib import Path
from typing import List, Tuple


def fix_syntax_errors(content: str) -> str:
    """Fix various syntax errors in Python code."""
    lines = content.split('\n')
    fixed_lines = []
    
    for i, line in enumerate(lines):
        # Fix patterns like "name: str." -> "name: str"
        line = re.sub(r'(\w+:\s*\w+)\.\s*$', r'\1', line)
        
        # Fix patterns like "def __init__(self):." -> "def __init__(self):"
        line = re.sub(r'(def\s+\w+\([^)]*\)):\.\s*$', r'\1:', line)
        
        # Fix patterns like "class ClassName:." -> "class ClassName:"
        line = re.sub(r'(class\s+\w+[^:]*?):\.\s*$', r'\1:', line)
        
        # Fix docstrings that end with period before quotes
        line = re.sub(r'(\s+)"""(.+?)\."""', r'\1"""\2"""', line)
        line = re.sub(r"(\s+)'''(.+?)\.'''", r"\1'''\2'''", line)
        
        # Fix standalone periods on their own line after docstrings
        if line.strip() == '.' and i > 0:
            prev_line = lines[i-1].strip()
            if prev_line.endswith('"""') or prev_line.endswith("'''"):
                continue  # Skip this line
        
        # Fix patterns like "return something." -> "return something"
        line = re.sub(r'(return\s+.+?)\.\s*$', r'\1', line)
        
        # Fix patterns like "import something." -> "import something"
        line = re.sub(r'(import\s+.+?)\.\s*$', r'\1', line)
        line = re.sub(r'(from\s+.+?)\.\s*$', r'\1', line)
        
        fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)


def fix_file(filepath: Path) -> Tuple[bool, str]:
    """Fix syntax errors in a single file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        fixed_content = fix_syntax_errors(content)
        
        if fixed_content != content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            return True, "Fixed"
        
        return False, "No changes needed"
        
    except Exception as e:
        return False, f"Error: {str(e)}"


def main():
    """Main function to fix priority files."""
    # Priority files that need fixing
    files_to_fix = [
        'backend/agents/core/agent_router.py',
        'backend/agents/docker_agent.py',
        'backend/agents/pulumi_agent.py',
        'backend/core/context_manager.py',
        'backend/integrations/pulumi_mcp_client.py',
        'backend/integrations/portkey_client.py',
        'backend/core/config_loader.py',
        'backend/integrations/base_integration.py',
        'backend/mcp/unified_mcp_servers.py',
        'backend/core/contextual_memory_intelligence.py',
        'backend/core/hierarchical_cache.py',
        'backend/core/real_time_streaming.py',
        'backend/app/websocket_manager.py',
        'backend/vector/vector_integration.py',
        'backend/core/enhanced_embedding_manager.py',
        'backend/pipeline/data_pipeline_architecture.py',
        'backend/agents/core/persistent_memory.py',
        'backend/core/comprehensive_memory_manager.py',
    ]
    
    print("Fixing syntax errors in priority files...")
    
    for filepath in files_to_fix:
        path = Path(filepath)
        if path.exists():
            print(f"Processing {filepath}...")
            fixed, message = fix_file(path)
            if fixed:
                print(f"  ✓ {message}")
            else:
                print(f"  ✗ {message}")
        else:
            print(f"  ✗ File not found: {filepath}")
    
    print("\nDone!")


if __name__ == "__main__":
    main()
