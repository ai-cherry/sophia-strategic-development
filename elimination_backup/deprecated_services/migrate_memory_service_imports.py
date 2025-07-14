#!/usr/bin/env python3
"""
Migrate all imports from legacy UnifiedMemoryService to UnifiedMemoryService
Part of Phase 1: Legacy Purge
"""

import os
import re
from pathlib import Path

def update_imports_in_file(file_path: Path) -> bool:
    """Update imports in a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Pattern 1: Direct import
        content = re.sub(
            r'from backend\.services\.unified_memory_service import UnifiedMemoryService',
            'from backend.services.unified_memory_service_primary import UnifiedMemoryService',
            content
        )
        
        # Pattern 2: Import with alias
        content = re.sub(
            r'from backend\.services\.unified_memory_service import UnifiedMemoryService as (\w+)',
            r'from backend.services.unified_memory_service_primary import UnifiedMemoryService as \1',
            content
        )
        
        # Pattern 3: Class instantiation
        content = re.sub(
            r'UnifiedMemoryService\(',
            'UnifiedMemoryService(',
            content
        )
        
        # Pattern 4: Type hints
        content = re.sub(
            r': UnifiedMemoryService',
            ': UnifiedMemoryService',
            content
        )
        
        # Pattern 5: Function that returns UnifiedMemoryService
        content = re.sub(
            r'-> UnifiedMemoryService',
            '-> UnifiedMemoryService',
            content
        )
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Main migration function"""
    print("🚀 Starting UnifiedMemoryService → UnifiedMemoryService migration")
    
    # Get repository root
    repo_root = Path(__file__).parent.parent
    
    # Find all Python files
    python_files = list(repo_root.glob("**/*.py"))
    
    # Exclude virtual environment and cache directories
    python_files = [
        f for f in python_files 
        if not any(part in f.parts for part in ['.venv', '__pycache__', 'venv', '.git'])
    ]
    
    updated_files = []
    
    for file_path in python_files:
        if update_imports_in_file(file_path):
            updated_files.append(file_path)
            print(f"✅ Updated: {file_path.relative_to(repo_root)}")
    
    print(f"\n📊 Migration Summary:")
    print(f"Total files scanned: {len(python_files)}")
    print(f"Files updated: {len(updated_files)}")
    
    if updated_files:
        print("\n📝 Updated files:")
        for f in updated_files:
            print(f"  - {f.relative_to(repo_root)}")
    
    print("\n✅ Migration complete!")

if __name__ == "__main__":
    main() 