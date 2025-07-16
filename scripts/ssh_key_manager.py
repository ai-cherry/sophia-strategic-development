#!/usr/bin/env python3
"""
Sophia AI SSH Key Manager - Single Source of Truth
Establishes sophia_correct_key as the unified SSH key for all operations
"""

import sys
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Optional
import argparse

class SophiaSSHKeyManager:
    """Single source of truth for SSH key management"""
    
    # UNIFIED SSH KEY CONFIGURATION
    MASTER_KEY_NAME = "sophia_correct_key"
    MASTER_KEY_PATH = Path.home() / ".ssh" / "sophia_correct_key"
    MASTER_PUB_PATH = Path.home() / ".ssh" / "sophia_correct_key.pub"
    
    # OLD SSH KEY PATTERNS TO REPLACE
    OLD_KEY_PATTERNS = [
        "sophia_final_key",
        "lambda_labs_private_key", 
        "sophia2025.pem",
        "sophia_working_key",
        "pulumi_lambda_key",
        "lambda_rsa",
        "sophia2025_private_key",
        "sophia_lambda_key",
        "lambda_labs_key",
        "sophia-ai-key",
        "lynn-sophia-key"
    ]
    
    # LAMBDA LABS SERVERS
    LAMBDA_SERVERS = {
        "sophia-production": "104.171.202.103",
        "sophia-ai-core": "192.222.58.232", 
        "sophia-mcp-orchestrator": "104.171.202.117",
        "sophia-data-pipeline": "104.171.202.134",
        "sophia-development": "155.248.194.183"
    }
    
    def __init__(self):
        self.ssh_dir = Path.home() / ".ssh"
        self.ssh_dir.mkdir(mode=0o700, exist_ok=True)
        
    def find_working_ssh_key(self) -> Optional[Path]:
        """Find the first working SSH key from existing keys"""
        print("🔍 Searching for working SSH key...")
        
        # Check if sophia_correct_key already exists and works
        if self.MASTER_KEY_PATH.exists():
            if self.test_ssh_key(self.MASTER_KEY_PATH):
                print(f"✅ {self.MASTER_KEY_NAME} already exists and works!")
                return self.MASTER_KEY_PATH
        
        # Search for working keys in order of preference
        key_search_order = [
            self.ssh_dir / "sophia_final_key",
            self.ssh_dir / "lambda_labs_private_key",
            self.ssh_dir / "sophia_working_key",
            self.ssh_dir / "sophia2025.pem",
            self.ssh_dir / "sophia_lambda_key",
            self.ssh_dir / "id_rsa"
        ]
        
        for key_path in key_search_order:
            if key_path.exists():
                print(f"🧪 Testing {key_path.name}...")
                if self.test_ssh_key(key_path):
                    print(f"✅ Found working key: {key_path.name}")
                    return key_path
                else:
                    print(f"❌ {key_path.name} doesn't work")
        
        print("❌ No working SSH key found!")
        return None
    
    def test_ssh_key(self, key_path: Path) -> bool:
        """Test if SSH key works with Lambda Labs servers"""
        if not key_path.exists():
            return False
            
        # Test with primary server
        test_server = self.LAMBDA_SERVERS["sophia-ai-core"]
        
        cmd = [
            "ssh", "-i", str(key_path),
            "-o", "StrictHostKeyChecking=no",
            "-o", "UserKnownHostsFile=/dev/null",
            "-o", "ConnectTimeout=5",
            "-o", "BatchMode=yes",
            f"ubuntu@{test_server}",
            "echo 'SSH_TEST_SUCCESS'"
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            return "SSH_TEST_SUCCESS" in result.stdout
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
            return False
    
    def setup_master_key(self) -> bool:
        """Set up sophia_correct_key as the master SSH key"""
        print("🔧 Setting up sophia_correct_key as master SSH key...")
        
        # Find working key
        working_key = self.find_working_ssh_key()
        if not working_key:
            print("❌ Cannot setup master key - no working key found!")
            return False
        
        # If sophia_correct_key already exists and works, we're done
        if working_key == self.MASTER_KEY_PATH:
            print("✅ sophia_correct_key already configured correctly")
            return True
        
        # Copy working key to sophia_correct_key
        print(f"📋 Copying {working_key.name} to {self.MASTER_KEY_NAME}...")
        
        # Backup existing master key if it exists
        if self.MASTER_KEY_PATH.exists():
            backup_path = self.MASTER_KEY_PATH.with_suffix(".backup")
            shutil.copy2(self.MASTER_KEY_PATH, backup_path)
            print(f"📦 Backed up existing key to {backup_path.name}")
        
        # Copy the working key
        shutil.copy2(working_key, self.MASTER_KEY_PATH)
        self.MASTER_KEY_PATH.chmod(0o600)
        
        # Copy public key if it exists
        working_pub = working_key.with_suffix(".pub")
        if working_pub.exists():
            shutil.copy2(working_pub, self.MASTER_PUB_PATH)
            self.MASTER_PUB_PATH.chmod(0o644)
        
        # Verify the copy works
        if self.test_ssh_key(self.MASTER_KEY_PATH):
            print("✅ sophia_correct_key setup successful!")
            return True
        else:
            print("❌ sophia_correct_key setup failed!")
            return False
    
    def validate_master_key(self) -> bool:
        """Validate that sophia_correct_key exists and works"""
        print("🔍 Validating sophia_correct_key...")
        
        # Check file exists
        if not self.MASTER_KEY_PATH.exists():
            print("❌ sophia_correct_key does not exist")
            return False
        
        # Check permissions
        stat_info = self.MASTER_KEY_PATH.stat()
        if stat_info.st_mode & 0o777 != 0o600:
            print("⚠️  Fixing permissions on sophia_correct_key...")
            self.MASTER_KEY_PATH.chmod(0o600)
        
        # Test connectivity
        print("🧪 Testing connectivity to Lambda Labs servers...")
        working_servers = []
        failed_servers = []
        
        for name, ip in self.LAMBDA_SERVERS.items():
            cmd = [
                "ssh", "-i", str(self.MASTER_KEY_PATH),
                "-o", "StrictHostKeyChecking=no",
                "-o", "UserKnownHostsFile=/dev/null",
                "-o", "ConnectTimeout=5",
                "-o", "BatchMode=yes",
                f"ubuntu@{ip}",
                "echo 'OK'"
            ]
            
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                if "OK" in result.stdout:
                    working_servers.append(f"{name} ({ip})")
                    print(f"✅ {name} ({ip}) - Working")
                else:
                    failed_servers.append(f"{name} ({ip})")
                    print(f"❌ {name} ({ip}) - Failed")
            except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
                failed_servers.append(f"{name} ({ip})")
                print(f"❌ {name} ({ip}) - Timeout/Error")
        
        print(f"\n📊 Results: {len(working_servers)}/{len(self.LAMBDA_SERVERS)} servers accessible")
        
        if len(working_servers) > 0:
            print("✅ sophia_correct_key is functional!")
            return True
        else:
            print("❌ sophia_correct_key is not working with any servers!")
            return False
    
    def scan_ssh_references(self) -> Dict[str, List[str]]:
        """Scan codebase for SSH key references that need updating"""
        print("🔍 Scanning codebase for SSH key references...")
        
        references = {}
        
        # File patterns to scan
        scan_patterns = ["*.py", "*.sh", "*.md", "*.yaml", "*.yml", "*.json"]
        
        # Search patterns
        search_patterns = [
            r'~/.ssh/sophia_correct_key',
            r'~/.ssh/sophia_correct_key',
            r'~/.ssh/sophia2025\.pem',
            r'~/.ssh/sophia_correct_key',
            r'~/.ssh/sophia_correct_key',
            r'~/.ssh/sophia_correct_key',
            r'~/.ssh/sophia_correct_key',
            r'\$HOME/.ssh/sophia_correct_key',
            r'SSH_KEY=.*sophia_final_key',
            r'ssh_key_path.*sophia_final_key'
        ]
        
        import re
        
        for pattern in scan_patterns:
            for file_path in Path(".").rglob(pattern):
                if file_path.is_file() and not file_path.name.startswith('.'):
                    try:
                        content = file_path.read_text()
                        matches = []
                        
                        for search_pattern in search_patterns:
                            if re.search(search_pattern, content):
                                matches.append(search_pattern)
                        
                        if matches:
                            references[str(file_path)] = matches
                    except (UnicodeDecodeError, PermissionError):
                        continue
        
        return references
    
    def update_ssh_references(self, dry_run: bool = False) -> int:
        """Update all SSH key references to use sophia_correct_key"""
        print("🔄 Updating SSH key references...")
        
        references = self.scan_ssh_references()
        
        if not references:
            print("✅ No SSH key references found to update")
            return 0
        
        print(f"📋 Found {len(references)} files with SSH key references")
        
        if dry_run:
            print("🔍 DRY RUN - Would update these files:")
            for file_path, patterns in references.items():
                print(f"  - {file_path}: {patterns}")
            return len(references)
        
        import re
        
        # Replacement patterns
        replacements = [
            (r'~/.ssh/sophia_correct_key', '~/.ssh/sophia_correct_key'),
            (r'~/.ssh/sophia_correct_key', '~/.ssh/sophia_correct_key'),
            (r'~/.ssh/sophia2025\.pem', '~/.ssh/sophia_correct_key'),
            (r'~/.ssh/sophia_correct_key', '~/.ssh/sophia_correct_key'),
            (r'~/.ssh/sophia_correct_key', '~/.ssh/sophia_correct_key'),
            (r'~/.ssh/sophia_correct_key', '~/.ssh/sophia_correct_key'),
            (r'~/.ssh/sophia_correct_key', '~/.ssh/sophia_correct_key'),
            (r'\$HOME/.ssh/sophia_correct_key', '$HOME/.ssh/sophia_correct_key'),
            (r'SSH_KEY="\$HOME/.ssh/sophia_correct_key"', 'SSH_KEY="$HOME/.ssh/sophia_correct_key"'),
            (r'ssh_key_path.*=.*"~/.ssh/sophia_correct_key"', 'ssh_key_path = "~/.ssh/sophia_correct_key"')
        ]
        
        updated_count = 0
        
        for file_path, _ in references.items():
            try:
                content = Path(file_path).read_text()
                original_content = content
                
                for pattern, replacement in replacements:
                    content = re.sub(pattern, replacement, content)
                
                if content != original_content:
                    # Backup original file
                    backup_path = Path(file_path).with_suffix(Path(file_path).suffix + '.ssh_backup')
                    Path(file_path).rename(backup_path)
                    
                    # Write updated content
                    Path(file_path).write_text(content)
                    
                    print(f"✅ Updated {file_path}")
                    updated_count += 1
                
            except Exception as e:
                print(f"❌ Failed to update {file_path}: {e}")
        
        print(f"✅ Updated {updated_count} files")
        return updated_count
    
    def create_deployment_script(self):
        """Create unified deployment script using sophia_correct_key"""
        script_content = '''#!/bin/bash
# Sophia AI Unified Deployment Script
# Uses ONLY sophia_correct_key for all SSH operations

set -euo pipefail

# Configuration
LAMBDA_IP="${LAMBDA_IP:-192.222.58.232}"
SSH_KEY="$HOME/.ssh/sophia_correct_key"
DOCKER_REGISTRY="scoobyjava15"

# Colors
RED='\\033[0;31m'
GREEN='\\033[0;32m'
YELLOW='\\033[1;33m'
NC='\\033[0m'

echo -e "${GREEN}🚀 Sophia AI Unified Deployment${NC}"
echo "================================="
echo "SSH Key: $SSH_KEY"
echo "Target: $LAMBDA_IP"
echo ""

# Validate SSH key exists
if [[ ! -f "$SSH_KEY" ]]; then
    echo -e "${RED}❌ SSH key not found at $SSH_KEY${NC}"
    echo "Run: python scripts/ssh_key_manager.py --setup"
    exit 1
fi

# Test SSH connection
echo -e "${YELLOW}🔗 Testing SSH connection...${NC}"
if ssh -i "$SSH_KEY" -o ConnectTimeout=10 -o BatchMode=yes ubuntu@$LAMBDA_IP exit; then
    echo -e "${GREEN}✅ SSH connection successful${NC}"
else
    echo -e "${RED}❌ SSH connection failed${NC}"
    echo "Run: python scripts/ssh_key_manager.py --validate"
    exit 1
fi

# Deploy Sophia AI
echo -e "${YELLOW}🚀 Deploying Sophia AI...${NC}"
export KUBECONFIG=~/.kube/config-lambda-labs-tunnel
kubectl apply -f k8s/production/

echo -e "${GREEN}✅ Deployment complete!${NC}"
echo "🌐 Access: https://$LAMBDA_IP"
echo "🔑 SSH: ssh -i $SSH_KEY ubuntu@$LAMBDA_IP"
'''
        
        script_path = Path("scripts/deploy_with_sophia_correct_key.sh")
        script_path.write_text(script_content)
        script_path.chmod(0o755)
        
        print(f"✅ Created unified deployment script: {script_path}")
    
    def delete_broken_scripts(self):
        """Delete broken and confusing SSH scripts"""
        broken_scripts = [
            "scripts/setup_lambda_labs_ssh.py",
            "scripts/cleanup_ssh_references.py", 
            "scripts/jupyter_ssh_automation.py",
            "scripts/add_key_via_jupyter.py",
            "scripts/lambda_api_ssh_fix.py",
            "scripts/use_existing_lambda_ssh.py",
            "scripts/setup_ssh_from_esc.py",
            "scripts/setup_correct_ssh_key.py"
        ]
        
        deleted_count = 0
        
        for script_path in broken_scripts:
            path = Path(script_path)
            if path.exists():
                # Move to backup instead of deleting
                backup_path = path.with_suffix(path.suffix + '.ssh_cleanup_backup')
                path.rename(backup_path)
                print(f"🗑️  Moved broken script: {script_path} → {backup_path}")
                deleted_count += 1
        
        print(f"✅ Cleaned up {deleted_count} broken SSH scripts")

def main():
    parser = argparse.ArgumentParser(description="Sophia AI SSH Key Manager")
    parser.add_argument("--setup", action="store_true", help="Setup sophia_correct_key as master key")
    parser.add_argument("--validate", action="store_true", help="Validate sophia_correct_key")
    parser.add_argument("--scan", action="store_true", help="Scan for SSH key references")
    parser.add_argument("--update", action="store_true", help="Update all SSH key references")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be updated without making changes")
    parser.add_argument("--cleanup", action="store_true", help="Delete broken SSH scripts")
    parser.add_argument("--all", action="store_true", help="Run complete SSH key unification")
    
    args = parser.parse_args()
    
    manager = SophiaSSHKeyManager()
    
    if args.setup or args.all:
        if manager.setup_master_key():
            print("✅ SSH key setup complete")
        else:
            print("❌ SSH key setup failed")
            sys.exit(1)
    
    if args.validate or args.all:
        if manager.validate_master_key():
            print("✅ SSH key validation passed")
        else:
            print("❌ SSH key validation failed")
            sys.exit(1)
    
    if args.scan or args.all:
        references = manager.scan_ssh_references()
        print(f"📋 Found {len(references)} files with SSH key references")
        for file_path, patterns in references.items():
            print(f"  - {file_path}")
    
    if args.update or args.all:
        updated = manager.update_ssh_references(dry_run=args.dry_run)
        print(f"✅ Updated {updated} files")
    
    if args.cleanup or args.all:
        manager.delete_broken_scripts()
    
    if args.all:
        manager.create_deployment_script()
        print("\n🎉 SSH Key Unification Complete!")
        print("=" * 50)
        print("✅ sophia_correct_key established as master key")
        print("✅ All SSH references updated")
        print("✅ Broken scripts cleaned up")
        print("✅ Unified deployment script created")
        print("\n🚀 Ready to deploy with: ./scripts/deploy_with_sophia_correct_key.sh")
    
    if not any(vars(args).values()):
        parser.print_help()

if __name__ == "__main__":
    main() 