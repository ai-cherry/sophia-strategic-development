#!/usr/bin/env python3
"""Fix all syntax errors in pulumi_agent.py"""

import re

def fix_pulumi_agent():
    """Fix all syntax errors in pulumi_agent.py"""
    
    with open('backend/agents/pulumi_agent.py', 'r') as f:
        content = f.read()
    
    # Fix all the incomplete comments (lines with just '#' and nothing after)
    # These are on lines: 119, 144, 161, 192, 239, 280, 331, 430, 481, 519
    lines = content.split('\n')
    
    # Fix line 119: """Deploy a Pulumi stack"""# Extract stack name from command
    lines[118] = '        """Deploy a Pulumi stack"""'
    lines.insert(119, '        # Extract stack name from command')
    
    # Fix line 144: """List resources in a stack"""
    if len(lines) > 144 and '"""List resources in a stack"""' in lines[143]:
        lines[143] = '        """List resources in a stack"""'
    
    # Fix line 161: """Create a new Pulumi stack"""# Extract stack name from command
    for i in range(160, 165):
        if i < len(lines) and '"""Create a new Pulumi stack"""' in lines[i]:
            lines[i] = '        """Create a new Pulumi stack"""'
            lines.insert(i+1, '        # Extract stack name from command')
            break
    
    # Fix line 192: """Select/switch to a different stack"""# Extract stack name.
    for i in range(190, 195):
        if i < len(lines) and '"""Select/switch to a different stack"""' in lines[i]:
            lines[i] = '        """Select/switch to a different stack"""'
            lines.insert(i+1, '        # Extract stack name')
            break
    
    # Fix line 239: try:.
    for i in range(235, 245):
        if i < len(lines) and lines[i].strip() == 'try:.':
            lines[i] = lines[i].replace('try:.', 'try:')
            break
    
    # Fix line 280: """Update stack configuration"""# Parse config command.
    for i in range(275, 285):
        if i < len(lines) and '"""Update stack configuration"""' in lines[i]:
            lines[i] = '        """Update stack configuration"""'
            lines.insert(i+1, '        # Parse config command')
            break
    
    # Fix line 331: """Generate Pulumi code based on description"""# Extract what to generate.
    for i in range(325, 335):
        if i < len(lines) and '"""Generate Pulumi code based on description"""' in lines[i]:
            lines[i] = '        """Generate Pulumi code based on description"""'
            lines.insert(i+1, '        # Extract what to generate')
            break
    
    # Fix line 430: """Use AI-Copilot to fix errors"""# Extract error message from command or get from context
    for i in range(425, 435):
        if i < len(lines) and '"""Use AI-Copilot to fix errors"""' in lines[i]:
            lines[i] = '        """Use AI-Copilot to fix errors"""'
            lines.insert(i+1, '        # Extract error message from command or get from context')
            break
    
    # Fix line 481: """Execute direct Pulumi command"""# Map common commands.
    for i in range(475, 485):
        if i < len(lines) and '"""Execute direct Pulumi command"""' in lines[i]:
            lines[i] = '        """Execute direct Pulumi command"""'
            lines.insert(i+1, '        # Map common commands')
            break
    
    # Fix line 519: """Get stack name from command or context"""# Try to extract from command
    for i in range(515, 525):
        if i < len(lines) and '"""Get stack name from command or context"""' in lines[i]:
            lines[i] = '        """Get stack name from command or context"""'
            lines.insert(i+1, '        # Try to extract from command')
            break
    
    # Fix line 540: """Process task - required by BaseAgent"""# Delegate to execute method.
    for i in range(535, 545):
        if i < len(lines) and '"""Process task - required by BaseAgent"""' in lines[i]:
            lines[i] = '        """Process task - required by BaseAgent"""'
            lines.insert(i+1, '        # Delegate to execute method')
            break
    
    # Rejoin the content
    content = '\n'.join(lines)
    
    # Fix the multi-line string issues in code_templates dictionary
    # Remove commas after closing triple quotes
    content = re.sub(r'(pulumi\.export\([^)]+\))""",', r'\1"""', content)
    
    # Write back
    with open('backend/agents/pulumi_agent.py', 'w') as f:
        f.write(content)
    
    print("Fixed all syntax errors in backend/agents/pulumi_agent.py")

if __name__ == "__main__":
    fix_pulumi_agent()
