#!/usr/bin/env python3
"""
Final Lambda Labs cleanup - removes all incorrect references and updates to working configuration.
"""

import os
import re
import json
import yaml
from pathlib import Path

# CORRECT WORKING CONFIGURATION
CORRECT_CONFIG = {
    "instances": {
        "sophia-production-instance": "104.171.202.103",  # RTX 6000
        "sophia-ai-core": "192.222.58.232",  # GH200 - PRIMARY
        "sophia-mcp-orchestrator": "104.171.202.117",  # A6000
        "sophia-data-pipeline": "104.171.202.134",  # A100
        "sophia-development": "155.248.194.183"  # A10
    },
    "primary_ip": "192.222.58.232",  # GH200 instance
    "ssh_key": "sophia2025.pem",
    "ssh_key_path": "~/.ssh/sophia2025.pem"
}

# WRONG CONFIGURATIONS TO REMOVE
WRONG_IPS = ["192.222.58.232", "192.222.58.232", "192.222.58.232", "192.222.58.232"]
WRONG_SSH_KEYS = ["sophia2025.pem", "sophia2025.pem", "sophia2025.pem"]

def cleanup_file(filepath):
    """Clean up a single file"""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        original = content
        
        # Replace wrong IPs with correct primary IP
        for wrong_ip in WRONG_IPS:
            content = content.replace(wrong_ip, CORRECT_CONFIG["primary_ip"])
        
        # Replace wrong SSH key references
        for wrong_key in WRONG_SSH_KEYS:
            content = content.replace(f"~/.ssh/{wrong_key}", CORRECT_CONFIG["ssh_key_path"])
            content = content.replace(f'"{wrong_key}"', f'"{CORRECT_CONFIG["ssh_key"]}"')
            content = content.replace(f"'{wrong_key}'", f"'{CORRECT_CONFIG['ssh_key']}'")
            content = content.replace(wrong_key, CORRECT_CONFIG["ssh_key"].replace(".pem", ""))
        
        if content != original:
            with open(filepath, 'w') as f:
                f.write(content)
            return True
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
    return False

def update_yaml_files():
    """Update YAML configuration files"""
    yaml_files = [
        "infrastructure/lambda-labs-config.yaml",
        ".github/workflows/main-deployment.yml"
    ]
    
    for yaml_file in yaml_files:
        if Path(yaml_file).exists():
            try:
                with open(yaml_file, 'r') as f:
                    data = yaml.safe_load(f)
                
                # Update lambda-labs-config.yaml
                if "lambda-labs-config" in yaml_file:
                    if "production" in data:
                        data["production"]["instance"]["ip"] = CORRECT_CONFIG["primary_ip"]
                        data["production"]["ssh"]["key_name"] = "sophia2025"
                        data["production"]["ssh"]["key_path"] = CORRECT_CONFIG["ssh_key_path"]
                        
                        # Update URLs
                        if "urls" in data:
                            for key in data["urls"]:
                                data["urls"][key] = data["urls"][key].replace("192.222.58.232", CORRECT_CONFIG["primary_ip"])
                
                # Update GitHub workflows
                elif "workflows" in yaml_file:
                    if "env" in data:
                        data["env"]["LAMBDA_LABS_IP"] = CORRECT_CONFIG["primary_ip"]
                        data["env"]["LAMBDA_SSH_KEY_NAME"] = "sophia2025"
                
                with open(yaml_file, 'w') as f:
                    yaml.dump(data, f, default_flow_style=False, sort_keys=False)
                print(f"✅ Updated {yaml_file}")
            except Exception as e:
                print(f"❌ Error updating {yaml_file}: {e}")

def update_json_files():
    """Update JSON configuration files"""
    json_files = ["sophia_cluster_config.json", "active_instance_ips.txt"]
    
    # Update sophia_cluster_config.json
    if Path("sophia_cluster_config.json").exists():
        try:
            with open("sophia_cluster_config.json", 'r') as f:
                data = json.load(f)
            data["master"]["ip"] = CORRECT_CONFIG["primary_ip"]
            with open("sophia_cluster_config.json", 'w') as f:
                json.dump(data, f, indent=2)
            print("✅ Updated sophia_cluster_config.json")
        except Exception as e:
            print(f"❌ Error updating sophia_cluster_config.json: {e}")
    
    # Update active_instance_ips.txt
    with open("active_instance_ips.txt", 'w') as f:
        f.write(CORRECT_CONFIG["primary_ip"] + "\n")
    print("✅ Updated active_instance_ips.txt")

def remove_old_ssh_keys():
    """Remove old SSH keys that don't work"""
    ssh_dir = Path.home() / ".ssh"
    for wrong_key in WRONG_SSH_KEYS:
        for ext in ["", ".pub"]:
            key_path = ssh_dir / f"{wrong_key}{ext}"
            if key_path.exists():
                key_path.unlink()
                print(f"🗑️  Removed {key_path}")

def update_pulumi_esc():
    """Update Pulumi ESC configuration"""
    commands = [
        f'pulumi env set scoobyjava-org/default/sophia-ai-production lambda_labs_production_ip "{CORRECT_CONFIG["primary_ip"]}"',
        f'pulumi env set scoobyjava-org/default/sophia-ai-production lambda_ssh_key_path "{CORRECT_CONFIG["ssh_key_path"]}"',
        f'pulumi env set scoobyjava-org/default/sophia-ai-production lambda_ssh_key_name "sophia2025"'
    ]
    
    for cmd in commands:
        os.system(cmd)
    print("✅ Updated Pulumi ESC configuration")

def main():
    print("🧹 Lambda Labs Final Cleanup")
    print("=" * 50)
    print(f"✅ Correct IP: {CORRECT_CONFIG['primary_ip']}")
    print(f"✅ Correct SSH Key: {CORRECT_CONFIG['ssh_key_path']}")
    print()
    
    # Update all files
    updated_count = 0
    for root, dirs, files in os.walk('.'):
        # Skip directories
        if any(skip in root for skip in ['.git', 'node_modules', '__pycache__', '.venv']):
            continue
        
        for file in files:
            if file.endswith(('.py', '.sh', '.yml', '.yaml', '.md', '.json')):
                filepath = Path(root) / file
                if cleanup_file(filepath):
                    updated_count += 1
                    print(f"📝 Updated {filepath}")
    
    print(f"\n📊 Updated {updated_count} files")
    
    # Update specific configuration files
    print("\n🔧 Updating configuration files...")
    update_yaml_files()
    update_json_files()
    
    # Remove old SSH keys
    print("\n🗑️  Removing old SSH keys...")
    remove_old_ssh_keys()
    
    # Update Pulumi ESC
    print("\n☁️  Updating Pulumi ESC...")
    update_pulumi_esc()
    
    print("\n✅ Cleanup complete!")
    print("\n📌 Next steps:")
    print("1. Commit these changes: git add -A && git commit -m 'fix: update Lambda Labs to correct working configuration'")
    print("2. Push to GitHub: git push")
    print(f"3. Deploy using: ssh -i {CORRECT_CONFIG['ssh_key_path']} ubuntu@{CORRECT_CONFIG['primary_ip']}")

if __name__ == "__main__":
    main() 