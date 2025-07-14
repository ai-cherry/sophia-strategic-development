#!/usr/bin/env python3
"""
Clean up all sophia2025.pem SSH key references and update with Lambda Labs configuration
"""

import os
import re
from pathlib import Path

def clean_ssh_references():
    """Clean up all sophia2025.pem references in the codebase"""
    
    # Files to update
    files_to_update = [
        "scripts/find_working_server.sh",
        "scripts/deploy_sophia_robust.sh", 
        "scripts/deploy_sophia_production_complete.sh",
        "scripts/quick_frontend_deploy.sh",
        "scripts/deploy_frontend_production.sh",
        "scripts/check_deployment_status.sh",
        "scripts/deploy_sophia_production_real.sh",
        "scripts/quick_backend_deploy.sh",
        "scripts/create_unified_deployment_orchestrator.py",
        "backend/integrations/lambda_labs_client.py",
        ".github/workflows/deploy-lambda-labs-aligned.yml"
    ]
    
    # Replacement patterns
    replacements = [
        # SSH key file references
        (r'SSH_KEY="\$HOME/\.ssh/sophia2025\.pem"', 'SSH_KEY="$HOME/.ssh/lambda_labs_private_key"'),
        (r'ssh_key_path = os\.path\.expanduser\("~/.ssh/sophia2025\.pem"\)', 'ssh_key_path = os.path.expanduser("~/.ssh/lambda_labs_private_key")'),
        (r'~/.ssh/sophia2025\.pem', '~/.ssh/lambda_labs_private_key'),
        (r'sophia2025\.pem', 'lambda_labs_private_key'),
        
        # SSH command updates
        (r'ssh -i ~/.ssh/sophia2025\.pem', 'ssh -i ~/.ssh/lambda_labs_private_key -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null'),
        (r'scp -i ~/.ssh/sophia2025\.pem', 'scp -i ~/.ssh/lambda_labs_private_key -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null'),
    ]
    
    # Process each file
    for file_path in files_to_update:
        if os.path.exists(file_path):
            print(f"Updating {file_path}...")
            
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                
                # Apply replacements
                for pattern, replacement in replacements:
                    content = re.sub(pattern, replacement, content)
                
                # Write back
                with open(file_path, 'w') as f:
                    f.write(content)
                    
                print(f"  ✅ Updated {file_path}")
                
            except Exception as e:
                print(f"  ❌ Error updating {file_path}: {e}")
        else:
            print(f"  ⚠️  File not found: {file_path}")
    
    print("\n🧹 SSH reference cleanup complete!")
    print("📝 Note: Documentation files were left unchanged as they are reference materials")

if __name__ == "__main__":
    clean_ssh_references() 