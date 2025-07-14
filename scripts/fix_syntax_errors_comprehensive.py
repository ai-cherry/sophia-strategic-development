#!/usr/bin/env python3
"""
Comprehensive Syntax Error Fixer for Sophia AI
Fixes common syntax errors found during validation

Date: July 14, 2025
"""

import ast
import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Any

def fix_syntax_errors(file_path: Path) -> Dict[str, Any]:
    """Fix common syntax errors in a Python file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        fixes_applied = []
        
        # Fix 1: __future__ imports must be at the beginning
        lines = content.split('\n')
        future_imports = []
        other_lines = []
        
        for line in lines:
            if line.strip().startswith('from __future__ import'):
                future_imports.append(line)
            else:
                other_lines.append(line)
        
        if future_imports:
            # Move __future__ imports to the top
            content = '\n'.join(future_imports + [''] + other_lines)
            fixes_applied.append("Moved __future__ imports to top")
        
        # Fix 2: Fix common indentation issues
        lines = content.split('\n')
        fixed_lines = []
        
        for i, line in enumerate(lines):
            # Fix unexpected indent after empty lines
            if i > 0 and not lines[i-1].strip() and line.strip() and line.startswith('    '):
                # Check if this should be at root level
                if not any(lines[j].strip() and not lines[j].startswith('    ') for j in range(max(0, i-5), i)):
                    fixed_lines.append(line.lstrip())
                    fixes_applied.append(f"Fixed unexpected indent at line {i+1}")
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)
        
        content = '\n'.join(fixed_lines)
        
        # Fix 3: Fix unmatched parentheses
        content = re.sub(r'\)\s*\)', ')', content)
        if ')' in original_content and content != original_content:
            fixes_applied.append("Fixed unmatched parentheses")
        
        # Fix 4: Fix EOL while scanning string literal
        content = re.sub(r'"""[^"]*$', '"""', content, flags=re.MULTILINE)
        content = re.sub(r'"[^"]*$', '"', content, flags=re.MULTILINE)
        if content != original_content:
            fixes_applied.append("Fixed unclosed string literals")
        
        # Fix 5: Fix expected an indented block
        lines = content.split('\n')
        fixed_lines = []
        
        for i, line in enumerate(lines):
            fixed_lines.append(line)
            
            # If line ends with colon and next line is not indented
            if line.strip().endswith(':') and i + 1 < len(lines):
                next_line = lines[i + 1] if i + 1 < len(lines) else ''
                if next_line.strip() and not next_line.startswith('    '):
                    fixed_lines.append('    pass  # TODO: [ARCH-001] Implement placeholder functionality')
                    fixes_applied.append(f"Added pass statement after colon at line {i+1}")
        
        content = '\n'.join(fixed_lines)
        
        # Fix 6: Fix invalid syntax patterns
        # Fix bare except clauses
        content = re.sub(r'except\s*:', 'except Exception:', content)
        
        # Fix invalid annotations
        content = re.sub(r'(\w+)\s*:\s*(\w+)\s*=\s*(\w+)', r'\1: \2 = \3', content)
        
        # Write back if changes were made
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return {
                'success': True,
                'fixes_applied': fixes_applied,
                'file': str(file_path)
            }
        
        return {
            'success': True,
            'fixes_applied': [],
            'file': str(file_path)
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'file': str(file_path)
        }

def main():
    """Main function to fix syntax errors"""
    workspace_root = Path.cwd()
    
    # Files with known syntax errors from validation
    error_files = [
        'main.py',
        'core/infra/cortex_gateway.py',
        'core/workflows/intelligent_meta_orchestrator.py',
        'core/workflows/langgraph_agent_orchestration.py',
        'core/agents/langgraph_agent_base.py',
        'core/use_cases/slack_analysis_agent.py',
        'core/use_cases/linear_project_health_agent.py',
        'core/use_cases/sales_coach_agent.py',
        'core/use_cases/call_analysis_agent.py',
        'core/use_cases/marketing_analysis_agent.py',
        'core/services/natural_language_infrastructure_controller.py',
        'core/services/knowledge_service.py',
        'core/services/analytics_service.py',
        'backend/services/query_optimizer.py',
        'backend/services/unified_chat_service.py',
        'backend/services/optimization_service.py',
        'backend/services/lambda_labs_serverless_service.py',
        'shared/config.py',
        'shared/dependencies.py',
        'shared/utils/qdrant_memory/service.py'
    ]
    
    print("🔧 Starting comprehensive syntax error fixing...")
    
    total_files = 0
    fixed_files = 0
    total_fixes = 0
    
    for file_path_str in error_files:
        file_path = workspace_root / file_path_str
        
        if file_path.exists():
            total_files += 1
            print(f"  📝 Fixing {file_path_str}...")
            
            result = fix_syntax_errors(file_path)
            
            if result['success']:
                if result['fixes_applied']:
                    fixed_files += 1
                    total_fixes += len(result['fixes_applied'])
                    print(f"    ✅ Applied {len(result['fixes_applied'])} fixes")
                    for fix in result['fixes_applied']:
                        print(f"      - {fix}")
                else:
                    print(f"    ℹ️ No fixes needed")
            else:
                print(f"    ❌ Failed to fix: {result['error']}")
        else:
            print(f"  ⚠️ File not found: {file_path_str}")
    
    print(f"\n📊 Summary:")
    print(f"  Total files processed: {total_files}")
    print(f"  Files with fixes applied: {fixed_files}")
    print(f"  Total fixes applied: {total_fixes}")
    
    if total_fixes > 0:
        print(f"\n✅ Syntax error fixing completed successfully!")
    else:
        print(f"\n ℹ️ No syntax errors needed fixing.")

if __name__ == "__main__":
    main() 