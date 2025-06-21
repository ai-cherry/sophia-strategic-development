#!/usr/bin/env python3
"""Fix specific docstring merge issues where docstrings are merged with field declarations."""

import re
from pathlib import Path
from typing import List, Tuple


def fix_docstring_merge(content: str) -> str:
    """Fix docstring merge issues in Python code."""
    lines = content.split('\n')
    fixed_lines = []
    
    for i, line in enumerate(lines):
        # Fix pattern like: """Registration info for an agent"""name: str
        # This regex looks for a docstring ending with """ followed by a field declaration
        match = re.match(r'^(\s*)("""[^"]+""")([\w_]+:\s*\w+.*)$', line)
        if match:
            indent = match.group(1)
            docstring = match.group(2)
            field_decl = match.group(3)
            # Split into two lines with proper indentation
            fixed_lines.append(f"{indent}{docstring}")
            fixed_lines.append(f"{indent}{field_decl}")
            continue
            
        # Fix pattern like: """def __init__(self):
        match = re.match(r'^(\s*)(""")(def\s+\w+\([^)]*\):.*)$', line)
        if match:
            indent = match.group(1)
            docstring_start = match.group(2)
            method_decl = match.group(3)
            # Split into two lines
            fixed_lines.append(f"{indent}{docstring_start}")
            fixed_lines.append(f"{indent}{method_decl}")
            continue
            
        # Fix pattern like: """start_time = datetime.utcnow().
        match = re.match(r'^(\s*)(""")([\w_]+\s*=.*)$', line)
        if match:
            indent = match.group(1)
            docstring_start = match.group(2)
            assignment = match.group(3)
            # Split into two lines
            fixed_lines.append(f"{indent}{docstring_start}")
            fixed_lines.append(f"{indent}{assignment}")
            continue
            
        # Fix pattern like: """self.agents[registration.name] = registration.
        match = re.match(r'^(\s*)(""")(self\..*)$', line)
        if match:
            indent = match.group(1)
            docstring_start = match.group(2)
            code = match.group(3)
            # Split into two lines
            fixed_lines.append(f"{indent}{docstring_start}")
            fixed_lines.append(f"{indent}{code}")
            continue
            
        # Fix pattern like: """command_lower = command.lower().
        match = re.match(r'^(\s*)(""")([\w_]+\.[\w_]+\(\).*)$', line)
        if match:
            indent = match.group(1)
            docstring_start = match.group(2)
            code = match.group(3)
            # Split into two lines
            fixed_lines.append(f"{indent}{docstring_start}")
            fixed_lines.append(f"{indent}{code}")
            continue
            
        # Fix pattern like: """agent_name = intent_analysis.get("agent").
        match = re.match(r'^(\s*)(""")([\w_]+\s*=\s*[\w_]+\.get.*)$', line)
        if match:
            indent = match.group(1)
            docstring_start = match.group(2)
            code = match.group(3)
            # Split into two lines
            fixed_lines.append(f"{indent}{docstring_start}")
            fixed_lines.append(f"{indent}{code}")
            continue
            
        # Fix pattern like: """if not context:.
        match = re.match(r'^(\s*)(""")(if\s+.*)$', line)
        if match:
            indent = match.group(1)
            docstring_start = match.group(2)
            code = match.group(3)
            # Split into two lines
            fixed_lines.append(f"{indent}{docstring_start}")
            fixed_lines.append(f"{indent}{code}")
            continue
            
        # Fix pattern like: """return self.routing_history[-limit:]
        match = re.match(r'^(\s*)(""")(return\s+.*)$', line)
        if match:
            indent = match.group(1)
            docstring_start = match.group(2)
            code = match.group(3)
            # Split into two lines
            fixed_lines.append(f"{indent}{docstring_start}")
            fixed_lines.append(f"{indent}{code}")
            continue
            
        # Otherwise, keep the line as is
        fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)


def fix_file(filepath: Path) -> Tuple[bool, str]:
    """Fix docstring merge issues in a single file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        fixed_content = fix_docstring_merge(content)
        
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
    
    print("Fixing docstring merge issues in priority files...")
    
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
