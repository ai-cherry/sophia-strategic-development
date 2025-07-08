#!/usr/bin/env python3
"""
Fix class method signatures to use cls instead of self
"""

import re
from pathlib import Path

def fix_cls_in_file(file_path: Path):
    """Fix class method signatures in a single file"""
    content = file_path.read_text()
    original = content
    
    # Fix field_validator methods that use self instead of cls
    content = re.sub(
        r'def (validate_\w+)\(self,',
        r'def \1(cls,',
        content
    )
    
    if content != original:
        file_path.write_text(content)
        print(f"Fixed cls parameters in: {file_path}")
        return True
    return False

def main():
    """Fix cls parameters in all affected files"""
    files_to_fix = [
        "infrastructure/integrations/gong_api_client_enhanced.py",
        "infrastructure/mcp_servers/ai_memory/ai_memory_models.py",
        "infrastructure/mcp_servers/ai_memory/core/config.py",
        "infrastructure/mcp_servers/ai_memory/core/models.py",
    ]
    
    fixed_count = 0
    for file_path in files_to_fix:
        path = Path(file_path)
        if path.exists():
            if fix_cls_in_file(path):
                fixed_count += 1
    
    print(f"\nFixed cls parameters in {fixed_count} files")

if __name__ == "__main__":
    main() 