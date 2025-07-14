#!/usr/bin/env python3
"""
Systematic Qdrant Elimination Script
Replaces all Qdrant references with Qdrant-based equivalents
"""

import os
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple

class QdrantEliminator:
    def __init__(self):
        self.replacement_patterns = [
            # Import statement replacements
            ('from backend.services.qdrant_unified_memory_service import', 
             'from backend.services.qdrant_unified_memory_service import'),
            ('from backend.services.qdrant_unified_memory_service import', 
             'from backend.services.qdrant_unified_memory_service import'),
            ('from backend.integrations.gong_api_client import', 
             'from backend.integrations.gong_api_client import'),
            ('from backend.integrations.hubspot_client import', 
             'from backend.integrations.hubspot_client import'),
            
            # Class name replacements
            ('QdrantUnifiedMemoryServiceV2', 'QdrantUnifiedMemoryServiceV2'),
            ('EnhancedQdrantUnifiedMemoryServiceV2', 'QdrantUnifiedMemoryServiceV2'),
            ('GongAPIClient', 'GongAPIClient'),
            ('HubSpotClient', 'HubSpotClient'),
            
            # Method and attribute replacements
            ('qdrant_memory_service', 'qdrant_memory_service'),
            ('qdrant_service', 'qdrant_service'),
            ('qdrant_serviceection', 'qdrant_connection'),
            ('self.qdrant_service', 'self.qdrant_service'),
            
            # Configuration replacements
            ('get_qdrant_config', 'get_qdrant_config'),
            ('QDRANT_', 'QDRANT_'),
            ('qdrant_', 'qdrant_'),
            
            # Database operation replacements
            ('qdrant_service.search_knowledge', 'qdrant_service.search_knowledge'),
            ('qdrant_service.add_knowledge', 'qdrant_service.add_knowledge'),
            ('qdrant_service.add_knowledge', 'qdrant_service.add_knowledge'),
            ('qdrant_service.search_knowledge', 'qdrant_service.search_knowledge'),
            
            # Comment and documentation replacements
            ('Qdrant persistent memory', 'Qdrant persistent memory'),
            ('Qdrant knowledge graph', 'Qdrant knowledge graph'),
            ('Qdrant workflow memory', 'Qdrant workflow memory'),
            ('Qdrant + GPU', 'Qdrant + GPU'),
            ('Qdrant Vector', 'Qdrant Vector'),
            ('Qdrant Long-term', 'Qdrant Long-term'),
            
            # SQL and query replacements
            ('SELECT self.qdrant_service.await', 'SELECT qdrant_service.await'),
            ('Qdrant collection', 'Qdrant collection'),
            ('qdrant database', 'qdrant database'),
        ]
        
        self.files_processed = 0
        self.replacements_made = 0
        self.broken_imports = []
    
    def process_file(self, file_path: Path) -> bool:
        """Process a single Python file for Qdrant replacements"""
        try:
            content = file_path.read_text(encoding='utf-8')
            original_content = content
            
            # Apply all replacement patterns
            for old_pattern, new_pattern in self.replacement_patterns:
                if old_pattern in content:
                    content = content.replace(old_pattern, new_pattern)
                    self.replacements_made += 1
            
            # Handle broken imports specifically
            broken_import_patterns = [
                r'from shared\.utils\.enhanced_qdrant_memory_service.*',
                r'from shared\.utils\.qdrant_memory_service.*',
                r'from shared\.utils\.qdrant_gong_connector.*',
                r'from shared\.utils\.qdrant_hubspot_connector.*',
                r'# REMOVED: from.*ELIMINATED.*import.*
            ]
            
            for pattern in broken_import_patterns:
                matches = re.findall(pattern, content)
                if matches:
                    self.broken_imports.extend([(str(file_path), match) for match in matches])
                    # Comment out broken imports
                    content = re.sub(pattern, f'# REMOVED: {pattern}', content)
            
            # Write back if changes were made
            if content != original_content:
                file_path.write_text(content, encoding='utf-8')
                self.files_processed += 1
                return True
            
            return False
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            return False
    
    def eliminate_ELIMINATED_references(self) -> None:
        """Systematically eliminate all Qdrant references"""
        print("🔄 Starting systematic Qdrant elimination...")
        
        # Find all Python files
        python_files = list(Path(".").rglob("*.py"))
        total_files = len(python_files)
        
        print(f"Found {total_files} Python files to process")
        
        # Process each file
        for i, py_file in enumerate(python_files, 1):
            if self.process_file(py_file):
                print(f"[{i}/{total_files}] Processed: {py_file}")
            
            # Progress indicator
            if i % 100 == 0:
                print(f"Progress: {i}/{total_files} files processed")
        
        print(f"\n✅ Qdrant elimination complete!")
        print(f"Files processed: {self.files_processed}")
        print(f"Replacements made: {self.replacements_made}")
        print(f"Broken imports found: {len(self.broken_imports)}")
    
    def fix_broken_imports(self) -> None:
        """Fix the most common broken import patterns"""
        print("\n🔧 Fixing broken imports...")
        
        import_fixes = {
            # Replace common broken imports with working ones
            'from shared.utils.enhanced_qdrant_memory_service': 
                'from backend.services.qdrant_unified_memory_service',
            'from shared.utils.qdrant_memory_service': 
                'from backend.services.qdrant_unified_memory_service',
            'from shared.utils.qdrant_gong_connector': 
                'from backend.integrations.gong_api_client',
            'from shared.utils.qdrant_hubspot_connector': 
                'from backend.integrations.hubspot_client',
        }
        
        for py_file in Path(".").rglob("*.py"):
            try:
                content = py_file.read_text(encoding='utf-8')
                original_content = content
                
                for old_import, new_import in import_fixes.items():
                    if old_import in content:
                        content = content.replace(old_import, new_import)
                
                if content != original_content:
                    py_file.write_text(content, encoding='utf-8')
                    print(f"Fixed imports in: {py_file}")
            except Exception as e:
                print(f"Error fixing imports in {py_file}: {e}")
    
    def generate_report(self) -> None:
        """Generate a comprehensive elimination report"""
        print("\n📊 Generating elimination report...")
        
        # Count remaining Qdrant references
        result = subprocess.run(
            ["grep", "-r", "qdrant\\|Qdrant", ".", "--include=*.py"],
            capture_output=True, text=True
        )
        remaining_refs = len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0
        
        report = f"""
# Qdrant Elimination Report
================================

## Summary
- Files processed: {self.files_processed}
- Replacements made: {self.replacements_made}
- Broken imports found: {len(self.broken_imports)}
- Remaining references: {remaining_refs}

## Broken Imports Found
"""
        for file_path, import_line in self.broken_imports[:20]:  # Show first 20
            report += f"- {file_path}: {import_line}\n"
        
        if len(self.broken_imports) > 20:
            report += f"... and {len(self.broken_imports) - 20} more\n"
        
        report += f"""
## Replacement Patterns Applied
"""
        for old, new in self.replacement_patterns:
            report += f"- '{old}' → '{new}'\n"
        
        # Save report
        with open("ELIMINATED_elimination_report.md", "w") as f:
            f.write(report)
        
        print("✅ Report saved to: ELIMINATED_elimination_report.md")
        print(f"📈 Remaining Qdrant references: {remaining_refs}")

def main():
    """Main execution function"""
    eliminator = QdrantEliminator()
    
    # Execute elimination phases
    eliminator.eliminate_ELIMINATED_references()
    eliminator.fix_broken_imports()
    eliminator.generate_report()
    
    print("\n🎉 Qdrant elimination completed successfully!")
    print("\nNext steps:")
    print("1. Review the elimination report")
    print("2. Fix any remaining syntax errors")
    print("3. Test the QdrantUnifiedMemoryServiceV2 integration")
    print("4. Run comprehensive tests")

if __name__ == "__main__":
    main() 