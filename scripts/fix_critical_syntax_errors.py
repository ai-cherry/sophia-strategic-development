#!/usr/bin/env python3
"""
Critical Syntax Error Fix for Core Backend Files

Focuses on fixing the most critical files needed for backend startup.
"""

import os
import re
import logging
from pathlib import Path
from typing import List, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CriticalSyntaxFixer:
    """Fixes critical syntax errors in core backend files."""
    
    def __init__(self):
        # Order matters - these are the core files needed for backend startup
        self.critical_files = [
            "backend/main.py",
            "backend/core/auto_esc_config.py", 
            "backend/agents/core/agent_framework.py",
            "backend/agents/core/base_agent.py",
            "backend/agents/specialized/pay_ready_agents.py",
            "backend/agents/specialized/client_health_agent.py",
            "backend/integrations/snowflake_integration.py",
        ]
        
        self.advanced_patterns = [
            # Fix import statement corruption  
            (r'(import\s+\w+)\s*\.\s*$', r'\1'),
            
            # Fix malformed class definitions
            (r'^(\s*class\s+\w+.*?):\s*"""([^"]+)"""\s*(\w)', r'\1:\n\2    """\3"""'),
            
            # Fix malformed method definitions
            (r'^(\s*)(async\s+)?def\s+(\w+)\([^)]*\)\s*\.\s*"""([^"]+)"""', r'\1\2def \3():\n\1    """\4"""'),
            
            # Fix try-except blocks that lost their colon
            (r'(\s+)(try)\s*\.\s*$', r'\1\2:'),
            (r'(\s+)(except\s+[^:]+)\s*\.\s*$', r'\1\2:'),
            (r'(\s+)(finally)\s*\.\s*$', r'\1\2:'),
            
            # Fix if statements that lost their colon
            (r'(\s+)(if\s+[^:]+)\s*\.\s*$', r'\1\2:'),
            (r'(\s+)(elif\s+[^:]+)\s*\.\s*$', r'\1\2:'),
            (r'(\s+)(else)\s*\.\s*$', r'\1\2:'),
            
            # Fix for/while loops that lost their colon
            (r'(\s+)(for\s+[^:]+)\s*\.\s*$', r'\1\2:'),
            (r'(\s+)(while\s+[^:]+)\s*\.\s*$', r'\1\2:'),
            
            # Fix with statements that lost their colon
            (r'(\s+)(with\s+[^:]+)\s*\.\s*$', r'\1\2:'),
            
            # Fix malformed return statements
            (r'(\s+)(return\s+[^.]+)\s*\.\s*$', r'\1\2'),
            
            # Fix malformed assignments
            (r'^(\s*)(\w+\s*=\s*[^.]+)\s*\.\s*$', r'\1\2'),
            
            # Fix unterminated string literals
            (r'(\s+)"""([^"]+)$', r'\1"""\2"""'),
            
            # Fix broken indentation after docstrings
            (r'("""[^"]*"""\s*\n)(\S)', r'\1        \2'),
        ]

    def fix_critical_file(self, file_path: str) -> bool:
        """Fix syntax errors in a critical file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            logger.error(f"Error reading {file_path}: {e}")
            return False

        original_content = content
        
        # Apply advanced patterns
        for pattern, replacement in self.advanced_patterns:
            content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
        
        # File-specific fixes
        content = self._apply_file_specific_fixes(file_path, content)
        
        if content != original_content:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                logger.info(f"Applied critical fixes to {file_path}")
                return True
            except Exception as e:
                logger.error(f"Error writing {file_path}: {e}")
                return False
        
        return False

    def _apply_file_specific_fixes(self, file_path: str, content: str) -> str:
        """Apply file-specific syntax fixes."""
        
        if "main.py" in file_path:
            # Fix main.py specific issues
            content = re.sub(r'(\s+)yield\s*\.\s*$', r'\1yield', content, flags=re.MULTILINE)
            
        elif "auto_esc_config.py" in file_path:
            # Fix auto_esc_config specific issues
            content = re.sub(r'(\s+)self\._initialized = False\s*\.\s*$', r'\1self._initialized = False', content, flags=re.MULTILINE)
            
        elif "agent_framework.py" in file_path:
            # Fix agent framework specific issues
            content = re.sub(r'("""[^"]*""")(\s*\n\s*)([A-Z]\w+)', r'\1\2    \3', content)
            
        elif "base_agent.py" in file_path:
            # Fix base agent specific issues  
            content = re.sub(r'(\s+)raise NotImplementedError\([^)]+\)\s*\.\s*$', r'\1raise NotImplementedError("Method must be implemented")', content, flags=re.MULTILINE)
            
        elif "pay_ready_agents.py" in file_path:
            # Fix specific issues in pay ready agents
            content = re.sub(r'(\s+)logger\.info\([^)]+\)\s*\.\s*$', r'\1logger.info("Agent initialized")', content, flags=re.MULTILINE)
        
        return content

    def validate_syntax(self, file_path: str) -> bool:
        """Validate Python syntax of a file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            compile(content, file_path, 'exec')
            return True
        except SyntaxError as e:
            logger.warning(f"Syntax error in {file_path}: {e}")
            return False
        except Exception as e:
            logger.error(f"Error validating {file_path}: {e}")
            return False

    def fix_all_critical_files(self) -> Dict[str, bool]:
        """Fix all critical files needed for backend startup."""
        results = {}
        
        for file_path in self.critical_files:
            if os.path.exists(file_path):
                logger.info(f"Processing critical file: {file_path}")
                fixed = self.fix_critical_file(file_path)
                valid = self.validate_syntax(file_path)
                results[file_path] = valid
                
                if valid:
                    logger.info(f"✅ {file_path} - syntax valid")
                else:
                    logger.warning(f"❌ {file_path} - syntax errors remain")
            else:
                logger.warning(f"File not found: {file_path}")
                results[file_path] = False
        
        return results


def main():
    """Main function to fix critical syntax errors."""
    fixer = CriticalSyntaxFixer()
    results = fixer.fix_all_critical_files()
    
    print("\n" + "="*60)
    print("CRITICAL SYNTAX FIX RESULTS")
    print("="*60)
    
    valid_files = sum(1 for valid in results.values() if valid)
    total_files = len(results)
    
    print(f"Valid files: {valid_files}/{total_files}")
    
    for file_path, valid in results.items():
        status = "✅ VALID" if valid else "❌ ERRORS"
        print(f"  {status} - {file_path}")
    
    if valid_files == total_files:
        print("\n🎉 All critical files have valid syntax!")
        print("You can now try starting the backend.")
        return True
    else:
        print(f"\n⚠️  {total_files - valid_files} files still have syntax errors.")
        print("Manual intervention may be required.")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 