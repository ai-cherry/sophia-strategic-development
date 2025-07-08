#!/usr/bin/env python3
"""
Fix unclosed parentheses in Python files
"""

import ast
import re
from pathlib import Path
from typing import List, Tuple


class ParenthesesFixer:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.fixed_count = 0
        
    def fix_unclosed_parentheses(self, file_path: Path) -> bool:
        """Try to fix unclosed parentheses in a file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Track parentheses balance
            paren_stack = []
            modified = False
            
            for i, line in enumerate(lines):
                # Skip comments and strings
                in_string = False
                in_comment = False
                quote_char = None
                
                j = 0
                while j < len(line):
                    char = line[j]
                    
                    # Handle strings
                    if char in ['"', "'"] and not in_comment:
                        if not in_string:
                            in_string = True
                            quote_char = char
                        elif char == quote_char and (j == 0 or line[j-1] != '\\'):
                            in_string = False
                            quote_char = None
                    
                    # Handle comments
                    elif char == '#' and not in_string:
                        in_comment = True
                    
                    # Count parentheses outside strings and comments
                    elif not in_string and not in_comment:
                        if char == '(':
                            paren_stack.append((i, j))
                        elif char == ')':
                            if paren_stack:
                                paren_stack.pop()
                            else:
                                # Extra closing parenthesis - remove it
                                line = line[:j] + line[j+1:]
                                lines[i] = line
                                modified = True
                                j -= 1
                    
                    j += 1
            
            # If we have unclosed parentheses, add closing ones
            if paren_stack:
                # Add closing parentheses at the end of the last non-empty line
                for i in range(len(lines) - 1, -1, -1):
                    if lines[i].strip():
                        lines[i] = lines[i].rstrip() + ')' * len(paren_stack) + '\n'
                        modified = True
                        break
            
            if modified:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
                return True
                
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
        
        return False
    
    def fix_specific_files(self, error_files: List[Tuple[str, str]]):
        """Fix specific files with unclosed parentheses"""
        for file_path, error in error_files:
            if "'(' was never closed" in error:
                print(f"\n🔧 Attempting to fix {file_path}")
                if self.fix_unclosed_parentheses(Path(file_path)):
                    self.fixed_count += 1
                    print(f"   ✅ Fixed unclosed parentheses")
                    
                    # Verify the fix
                    try:
                        with open(file_path, 'r') as f:
                            ast.parse(f.read())
                        print(f"   ✅ Syntax is now valid!")
                    except SyntaxError as e:
                        print(f"   ⚠️  Still has syntax error: {e}")
                else:
                    print(f"   ❌ Could not fix automatically")


def main():
    # List of files with unclosed parentheses from the previous scan
    error_files = [
        ("ui-ux-agent/mcp-servers/langchain-agents/ui_ux_agent.py", "'(' was never closed"),
        ("ui-ux-agent/mcp-servers/figma-dev-mode/figma_mcp_server.py", "'(' was never closed"),
        ("api/main.py", "'(' was never closed"),
        ("mcp-servers/codacy/enhanced_codacy_mcp_server.py", "'(' was never closed"),
        ("mcp-servers/asana/asana_mcp_server.py", "'(' was never closed"),
        ("infrastructure/n8n_bridge/main.py", "'(' was never closed"),
        ("infrastructure/mcp_servers/asana_v2/server.py", "'(' was never closed"),
        ("infrastructure/mcp_servers/perplexity_v2/server.py", "'(' was never closed"),
        ("infrastructure/mcp_servers/linear_v2/server.py", "'(' was never closed"),
        ("infrastructure/mcp_servers/gong_v2/server.py", "'(' was never closed"),
        ("infrastructure/mcp_servers/cortex_aisql/cortex_mcp_server.py", "'(' was never closed"),
        ("infrastructure/mcp_servers/snowflake_v2/server.py", "'(' was never closed"),
        ("infrastructure/mcp_servers/github/server.py", "'(' was never closed"),
        ("infrastructure/mcp_servers/codacy_v2/server.py", "'(' was never closed"),
        ("infrastructure/mcp_servers/slack_v2/server.py", "'(' was never closed"),
        ("infrastructure/mcp_servers/notion_v2/server.py", "'(' was never closed"),
        ("infrastructure/mcp_servers/github_v2/server.py", "'(' was never closed"),
        ("infrastructure/monitoring/security_metrics_exporter.py", "'(' was never closed"),
    ]
    
    fixer = ParenthesesFixer()
    fixer.fix_specific_files(error_files)
    
    print(f"\n✅ Fixed {fixer.fixed_count} files with unclosed parentheses")


if __name__ == "__main__":
    main() 