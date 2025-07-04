#!/usr/bin/env python3
"""
Documentation Outdatedness Scanner
Inventories all documentation files and identifies outdated content
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Tuple
import argparse

# Patterns to detect outdated content
DEPRECATED_TOOLS = {
    r'\.env': 'Use Pulumi ESC instead of .env files',
    r'\bpip\s+install': 'Use uv instead of pip',
    r'SonarQube': 'Use Codacy instead of SonarQube',
    r'Airflow|Dagster|Prefect': 'Use Estuary instead of Airflow/Dagster/Prefect',
    r'requirements\.txt': 'Use pyproject.toml with uv',
    r'docker-compose\s+up': 'Use docker stack deploy for production',
}

# Structure patterns
OLD_STRUCTURE_PATTERNS = [
    r'backend/',
    r'frontend/',
    r'mcp-servers/',
]

NEW_STRUCTURE_PATTERNS = [
    r'apps/',
    r'libs/',
    r'config/',
]

# Keywords indicating outdated content
OUTDATED_KEYWORDS = [
    'TODO', 'FIXME', 'DEPRECATED', 'LEGACY', 'OBSOLETE',
    'migration', 'transition', 'temporary', 'old', 'backup'
]

# Date patterns that might indicate old content
OLD_DATE_PATTERNS = [
    r'2023', r'2024',
    r'Q[1-4]\s+2023', r'Q[1-4]\s+2024',
    r'January|February|March|April|May|June|July|August|September|October|November|December\s+2023',
    r'January|February|March|April|May|June|July|August|September|October|November|December\s+2024',
]


class DocumentationScanner:
    def __init__(self, root_dir: str = '.'):
        self.root_dir = Path(root_dir)
        self.results = []
        
    def scan_file(self, file_path: Path) -> Dict:
        """Scan a single documentation file for outdated content"""
        result = {
            'file': str(file_path.relative_to(self.root_dir)),
            'size': file_path.stat().st_size,
            'modified': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
            'deprecated_tools': {},
            'structure_refs': {
                'old': [],
                'new': []
            },
            'outdated_keywords': [],
            'old_dates': [],
            'todos': 0,
            'category': 'current',  # Will be updated based on findings
            'priority': 'low',  # Will be updated based on file importance
            'issues': []
        }
        
        try:
            content = file_path.read_text()
            lines = content.split('\n')
            
            # Check for deprecated tools
            for pattern, message in DEPRECATED_TOOLS.items():
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    result['deprecated_tools'][pattern] = {
                        'count': len(matches),
                        'message': message
                    }
                    result['issues'].append(f"References deprecated tool: {pattern}")
            
            # Check structure references
            for pattern in OLD_STRUCTURE_PATTERNS:
                if re.search(pattern, content):
                    result['structure_refs']['old'].append(pattern)
                    
            for pattern in NEW_STRUCTURE_PATTERNS:
                if re.search(pattern, content):
                    result['structure_refs']['new'].append(pattern)
                    
            if result['structure_refs']['old'] and result['structure_refs']['new']:
                result['issues'].append("Mixed old/new structure references")
            
            # Check for outdated keywords
            for keyword in OUTDATED_KEYWORDS:
                if re.search(rf'\b{keyword}\b', content, re.IGNORECASE):
                    result['outdated_keywords'].append(keyword)
            
            # Count TODOs/FIXMEs
            result['todos'] = len(re.findall(r'\b(TODO|FIXME)\b', content))
            
            # Check for old dates
            for pattern in OLD_DATE_PATTERNS:
                if re.search(pattern, content):
                    result['old_dates'].append(pattern)
                    
            # Categorize the file
            result['category'] = self._categorize_file(result)
            
            # Prioritize the file
            result['priority'] = self._prioritize_file(file_path, result)
            
        except Exception as e:
            result['error'] = str(e)
            result['category'] = 'error'
            
        return result
    
    def _categorize_file(self, result: Dict) -> str:
        """Categorize file based on scan results"""
        issues_count = (
            len(result['deprecated_tools']) +
            len(result['outdated_keywords']) +
            len(result['old_dates']) +
            result['todos']
        )
        
        has_structure_conflict = (
            len(result['structure_refs']['old']) > 0 and 
            len(result['structure_refs']['new']) > 0
        )
        
        if issues_count == 0 and not has_structure_conflict:
            return 'current'
        elif issues_count > 10 or len(result['deprecated_tools']) > 3:
            return 'fully_outdated'
        elif 'migration' in result['file'] or 'transition' in result['file']:
            return 'migration'
        else:
            return 'partially_outdated'
    
    def _prioritize_file(self, file_path: Path, result: Dict) -> str:
        """Prioritize file based on importance and issues"""
        high_priority_files = [
            'README.md', '.cursorrules', 'DEVELOPMENT.md',
            'system_handbook', 'DEVELOPER_GUIDE', 'CURRENT_TOOLING_STACK'
        ]
        
        file_str = str(file_path)
        
        # Check if it's a high-priority file
        for hp_file in high_priority_files:
            if hp_file in file_str:
                return 'high'
        
        # System handbook is always high priority
        if 'system_handbook' in file_str:
            return 'high'
            
        # Files with many issues are medium priority
        if result['category'] in ['partially_outdated', 'fully_outdated']:
            return 'medium'
            
        return 'low'
    
    def scan_directory(self, directory: Path = None) -> List[Dict]:
        """Scan all documentation files in directory"""
        if directory is None:
            directory = self.root_dir / 'docs'
            
        doc_extensions = ['.md', '.txt', '.rst']
        
        for file_path in directory.rglob('*'):
            if file_path.is_file() and file_path.suffix in doc_extensions:
                print(f"Scanning: {file_path.relative_to(self.root_dir)}")
                result = self.scan_file(file_path)
                self.results.append(result)
                
        # Also scan root-level docs
        for file_path in self.root_dir.glob('*.md'):
            print(f"Scanning: {file_path.relative_to(self.root_dir)}")
            result = self.scan_file(file_path)
            self.results.append(result)
            
        # And .cursorrules
        cursorrules = self.root_dir / '.cursorrules'
        if cursorrules.exists():
            print(f"Scanning: {cursorrules.relative_to(self.root_dir)}")
            result = self.scan_file(cursorrules)
            self.results.append(result)
            
        return self.results
    
    def generate_report(self) -> Dict:
        """Generate summary report of scan results"""
        report = {
            'scan_date': datetime.now().isoformat(),
            'total_files': len(self.results),
            'categories': {},
            'priorities': {},
            'deprecated_tools_summary': {},
            'structure_conflicts': 0,
            'total_todos': 0,
            'files_with_old_dates': 0,
            'top_issues': []
        }
        
        # Count by category and priority
        for result in self.results:
            cat = result['category']
            report['categories'][cat] = report['categories'].get(cat, 0) + 1
            
            pri = result['priority']
            report['priorities'][pri] = report['priorities'].get(pri, 0) + 1
            
            # Count deprecated tools
            for tool in result['deprecated_tools']:
                report['deprecated_tools_summary'][tool] = \
                    report['deprecated_tools_summary'].get(tool, 0) + 1
            
            # Count structure conflicts
            if (result['structure_refs']['old'] and 
                result['structure_refs']['new']):
                report['structure_conflicts'] += 1
                
            # Count TODOs
            report['total_todos'] += result['todos']
            
            # Count files with old dates
            if result['old_dates']:
                report['files_with_old_dates'] += 1
        
        # Identify top issues
        high_priority_issues = [
            r for r in self.results 
            if r['priority'] == 'high' and r['category'] != 'current'
        ]
        report['high_priority_files'] = [
            {
                'file': r['file'],
                'category': r['category'],
                'issues': r['issues']
            }
            for r in sorted(high_priority_issues, 
                          key=lambda x: len(x['issues']), 
                          reverse=True)[:10]
        ]
        
        return report
    
    def save_results(self, output_dir: str = 'docs/documentation_audit'):
        """Save scan results to files"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save detailed results
        with open(output_path / 'scan_results.json', 'w') as f:
            json.dump(self.results, f, indent=2)
            
        # Save summary report
        report = self.generate_report()
        with open(output_path / 'scan_report.json', 'w') as f:
            json.dump(report, f, indent=2)
            
        # Generate markdown report
        self._generate_markdown_report(report, output_path / 'SCAN_REPORT.md')
        
        print(f"\n✅ Results saved to {output_path}")
        
    def _generate_markdown_report(self, report: Dict, output_file: Path):
        """Generate a markdown report"""
        with open(output_file, 'w') as f:
            f.write("# Documentation Scan Report\n\n")
            f.write(f"**Scan Date**: {report['scan_date']}\n\n")
            
            f.write("## Summary\n\n")
            f.write(f"- **Total Files Scanned**: {report['total_files']}\n")
            f.write(f"- **Files Needing Updates**: {report['categories'].get('partially_outdated', 0) + report['categories'].get('fully_outdated', 0)}\n")
            f.write(f"- **High Priority Files**: {report['priorities'].get('high', 0)}\n")
            f.write(f"- **Total TODOs/FIXMEs**: {report['total_todos']}\n")
            f.write(f"- **Files with Old Dates**: {report['files_with_old_dates']}\n")
            f.write(f"- **Structure Conflicts**: {report['structure_conflicts']}\n\n")
            
            f.write("## Categories\n\n")
            for cat, count in report['categories'].items():
                f.write(f"- **{cat}**: {count} files\n")
            f.write("\n")
            
            f.write("## Deprecated Tools Found\n\n")
            for tool, count in report['deprecated_tools_summary'].items():
                f.write(f"- `{tool}`: found in {count} files\n")
            f.write("\n")
            
            f.write("## High Priority Files Needing Updates\n\n")
            for file_info in report['high_priority_files']:
                f.write(f"### {file_info['file']}\n")
                f.write(f"- Category: {file_info['category']}\n")
                f.write("- Issues:\n")
                for issue in file_info['issues']:
                    f.write(f"  - {issue}\n")
                f.write("\n")


def main():
    parser = argparse.ArgumentParser(
        description='Scan documentation for outdated content'
    )
    parser.add_argument(
        '--root', 
        default='.', 
        help='Root directory of the project'
    )
    parser.add_argument(
        '--output', 
        default='docs/documentation_audit',
        help='Output directory for results'
    )
    
    args = parser.parse_args()
    
    print("🔍 Scanning documentation for outdated content...\n")
    
    scanner = DocumentationScanner(args.root)
    scanner.scan_directory()
    scanner.save_results(args.output)
    
    # Print summary
    report = scanner.generate_report()
    print("\n📊 Scan Summary:")
    print(f"   Total files: {report['total_files']}")
    print(f"   Current: {report['categories'].get('current', 0)}")
    print(f"   Partially outdated: {report['categories'].get('partially_outdated', 0)}")
    print(f"   Fully outdated: {report['categories'].get('fully_outdated', 0)}")
    print(f"   High priority: {report['priorities'].get('high', 0)}")
    
    print("\n🎯 Next steps:")
    print("   1. Review docs/documentation_audit/SCAN_REPORT.md")
    print("   2. Prioritize high-priority files for updates")
    print("   3. Run cleanup_deprecated_tool_references.py for quick fixes")
    print("   4. Create update plan for partially outdated files")


if __name__ == "__main__":
    main() 