#!/usr/bin/env python3
"""
Architecture Validation Script
Validates current state of Weaviate vs Qdrant usage
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

class ArchitectureValidator:
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "weaviate_references": 0,
            "qdrant_references": 0,
            "architecture_conflicts": [],
            "files_with_weaviate": [],
            "files_with_qdrant": [],
            "critical_issues": [],
            "recommendations": []
        }
    
    def scan_codebase(self) -> None:
        """Scan entire codebase for architecture references"""
        print("🔍 Scanning codebase for architecture references...")
        
        excluded_dirs = {'.git', 'node_modules', '__pycache__', '.venv', 'venv', 'backup', 'weaviate_elimination_backup_20250714_145747'}
        
        for root, dirs, files in os.walk("."):
            dirs[:] = [d for d in dirs if d not in excluded_dirs]
            
            for file in files:
                if file.endswith(('.py', '.ts', '.tsx', '.js', '.yaml', '.yml', '.json', '.md')):
                    file_path = os.path.join(root, file)
                    self.analyze_file(file_path)
    
    def analyze_file(self, file_path: str) -> None:
        """Analyze individual file for architecture references"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            content_lower = content.lower()
            
            # Count references
            weaviate_count = content_lower.count('weaviate')
            qdrant_count = content_lower.count('qdrant')
            
            if weaviate_count > 0:
                self.results["weaviate_references"] += weaviate_count
                self.results["files_with_weaviate"].append({
                    "file": file_path,
                    "count": weaviate_count,
                    "lines": self.find_reference_lines(content, 'weaviate')
                })
            
            if qdrant_count > 0:
                self.results["qdrant_references"] += qdrant_count
                self.results["files_with_qdrant"].append({
                    "file": file_path,
                    "count": qdrant_count,
                    "lines": self.find_reference_lines(content, 'qdrant')
                })
            
            # Check for architecture conflicts
            if weaviate_count > 0 and qdrant_count > 0:
                self.results["architecture_conflicts"].append({
                    "file": file_path,
                    "weaviate_count": weaviate_count,
                    "qdrant_count": qdrant_count,
                    "severity": "HIGH"
                })
            
        except Exception as e:
            print(f"⚠️  Error analyzing {file_path}: {e}")
    
    def find_reference_lines(self, content: str, term: str) -> List[int]:
        """Find line numbers containing the term"""
        lines = content.split('\n')
        return [i + 1 for i, line in enumerate(lines) if term.lower() in line.lower()]
    
    def generate_recommendations(self) -> None:
        """Generate recommendations based on analysis"""
        print("💡 Generating recommendations...")
        
        weaviate_files = len(self.results["files_with_weaviate"])
        qdrant_files = len(self.results["files_with_qdrant"])
        
        if weaviate_files > 0:
            self.results["recommendations"].append({
                "priority": "MEDIUM",
                "action": "Review remaining Weaviate references",
                "description": f"Found {weaviate_files} files with Weaviate references (may be documentation or backups)"
            })
        
        if weaviate_files == 0 and qdrant_files > 0:
            self.results["recommendations"].append({
                "priority": "LOW",
                "action": "Architecture validation complete",
                "description": "Pure Qdrant architecture achieved"
            })
    
    def print_summary(self) -> None:
        """Print validation summary"""
        print("\n" + "="*60)
        print("📊 ARCHITECTURE VALIDATION SUMMARY")
        print("="*60)
        
        print(f"🔍 Total Weaviate references: {self.results['weaviate_references']}")
        print(f"🔍 Total Qdrant references: {self.results['qdrant_references']}")
        print(f"📁 Files with Weaviate: {len(self.results['files_with_weaviate'])}")
        print(f"📁 Files with Qdrant: {len(self.results['files_with_qdrant'])}")
        print(f"⚠️  Architecture conflicts: {len(self.results['architecture_conflicts'])}")
        
        # Architecture status
        if self.results['weaviate_references'] == 0:
            print("\n✅ ARCHITECTURE STATUS: Pure Qdrant (EXCELLENT)")
        elif self.results['weaviate_references'] < 50:
            print("\n⚠️  ARCHITECTURE STATUS: Mostly Qdrant (GOOD - minor cleanup needed)")
        else:
            print("\n❌ ARCHITECTURE STATUS: Mixed architecture (NEEDS CLEANUP)")
        
        # Top Weaviate files (if any)
        if self.results['files_with_weaviate']:
            print("\n🔍 REMAINING WEAVIATE FILES:")
            sorted_files = sorted(self.results['files_with_weaviate'], key=lambda x: x['count'], reverse=True)
            for file_info in sorted_files[:5]:
                print(f"  {file_info['count']:3d} refs - {file_info['file']}")
        
        # Recommendations
        if self.results['recommendations']:
            print("\n💡 RECOMMENDATIONS:")
            for rec in self.results['recommendations']:
                print(f"  {rec['priority']} - {rec['action']}")
                print(f"    {rec['description']}")
        
        print("\n" + "="*60)
    
    def save_report(self) -> None:
        """Save detailed report to JSON"""
        with open("architecture_validation_report_post_elimination.json", 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"📋 Detailed report saved: architecture_validation_report_post_elimination.json")
    
    def validate(self) -> Dict[str, Any]:
        """Execute complete validation"""
        print("🚀 Starting Post-Elimination Architecture Validation...")
        
        self.scan_codebase()
        self.generate_recommendations()
        self.print_summary()
        self.save_report()
        
        return self.results

if __name__ == "__main__":
    validator = ArchitectureValidator()
    results = validator.validate()
    
    # Exit with appropriate code
    if results['weaviate_references'] > 100:
        print("\n❌ Validation failed - Too many Weaviate references remain")
        exit(1)
    elif results['weaviate_references'] > 0:
        print("\n⚠️  Validation warning - Some Weaviate references remain (likely documentation)")
        exit(0)
    else:
        print("\n✅ Validation passed - Pure Qdrant architecture achieved")
        exit(0) 