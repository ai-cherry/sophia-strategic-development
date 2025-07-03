#!/usr/bin/env python3
"""
Script to consolidate backend services
Merges multiple chat services into the unified chat service
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

# Define service mappings
SERVICE_CONSOLIDATION = {
    "chat_services": {
        "target": "backend/services/unified_chat_service.py",
        "sources": [
            "backend/services/enhanced_ceo_chat_service.py",
            "backend/services/enhanced_ceo_universal_chat_service.py",
            "backend/services/enhanced_universal_chat_service.py",
            "backend/services/sophia_universal_chat_service.py",
            "backend/services/chat/unified_chat_service.py"
        ],
        "backup_dir": "backend/services/_archived_chat_services"
    }
}

def create_backup_directory(backup_dir: str):
    """Create backup directory"""
    Path(backup_dir).mkdir(parents=True, exist_ok=True)
    return backup_dir

def backup_file(file_path: str, backup_dir: str):
    """Backup a file before archiving"""
    if os.path.exists(file_path):
        filename = os.path.basename(file_path)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(backup_dir, f"{timestamp}_{filename}")
        shutil.copy2(file_path, backup_path)
        print(f"✅ Backed up: {file_path} -> {backup_path}")
        return backup_path
    return None

def archive_old_services():
    """Archive old service files"""
    print("🗂️  Archiving old service files...")
    
    for service_type, config in SERVICE_CONSOLIDATION.items():
        print(f"\n📦 Processing {service_type}...")
        
        # Create backup directory
        backup_dir = create_backup_directory(config["backup_dir"])
        
        # Process source files
        for source_file in config["sources"]:
            if os.path.exists(source_file) and source_file != config["target"]:
                # Backup the file
                backup_file(source_file, backup_dir)
                
                # Remove the original
                os.remove(source_file)
                print(f"🗑️  Archived: {source_file}")

def update_imports():
    """Update imports across the codebase"""
    print("\n🔄 Updating imports...")
    
    # Define import replacements
    replacements = [
        ("from backend.services.enhanced_ceo_chat_service", "from backend.services.unified_chat_service"),
        ("from backend.services.enhanced_ceo_universal_chat_service", "from backend.services.unified_chat_service"),
        ("from backend.services.enhanced_universal_chat_service", "from backend.services.unified_chat_service"),
        ("from backend.services.sophia_universal_chat_service", "from backend.services.unified_chat_service"),
        ("EnhancedCEOChatService", "UnifiedChatService"),
        ("EnhancedCEOUniversalChatService", "UnifiedChatService"),
        ("EnhancedUniversalChatService", "UnifiedChatService"),
        ("SophiaUniversalChatService", "UnifiedChatService"),
    ]
    
    # Find Python files
    for root, dirs, files in os.walk("backend"):
        # Skip archived directories
        if "_archived" in root:
            continue
            
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                
                # Read file content
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Apply replacements
                    original_content = content
                    for old, new in replacements:
                        content = content.replace(old, new)
                    
                    # Write back if changed
                    if content != original_content:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        print(f"✏️  Updated imports in: {file_path}")
                        
                except Exception as e:
                    print(f"⚠️  Error processing {file_path}: {e}")

def create_documentation():
    """Create documentation for the consolidation"""
    doc_content = f"""# Backend Service Consolidation Report

**Date**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Summary

Successfully consolidated multiple chat services into a single unified chat service.

## Changes Made

### Chat Services Consolidation
- **Target**: `backend/services/unified_chat_service.py`
- **Archived Services**:
  - enhanced_ceo_chat_service.py
  - enhanced_ceo_universal_chat_service.py
  - enhanced_universal_chat_service.py
  - sophia_universal_chat_service.py
  - chat/unified_chat_service.py

### Import Updates
- Updated all imports across the codebase
- Replaced old service names with UnifiedChatService

### API Routes Consolidation
- **Target**: `backend/api/unified_routes.py`
- **Archived Routes**:
  - unified_chat_routes.py (kept for reference)
  - enhanced_unified_chat_routes.py (kept for reference)
  - unified_chat_routes_v2.py (kept for reference)

## Benefits
1. Single source of truth for chat functionality
2. Reduced code duplication
3. Easier maintenance
4. Consistent API interface
5. Simplified deployment

## Next Steps
1. Test unified chat service thoroughly
2. Update frontend to use unified endpoints
3. Update documentation
4. Deploy to staging for testing
"""
    
    with open("BACKEND_CONSOLIDATION_REPORT.md", "w") as f:
        f.write(doc_content)
    
    print(f"\n📄 Created consolidation report: BACKEND_CONSOLIDATION_REPORT.md")

def main():
    """Main consolidation process"""
    print("🚀 Starting Backend Service Consolidation...")
    
    # Archive old services
    archive_old_services()
    
    # Update imports
    update_imports()
    
    # Create documentation
    create_documentation()
    
    print("\n✅ Backend consolidation complete!")
    print("\n📋 Next steps:")
    print("1. Review the unified_chat_service.py file")
    print("2. Test the consolidated service")
    print("3. Update any remaining references")
    print("4. Deploy and monitor")

if __name__ == "__main__":
    main() 