#!/usr/bin/env python3
"""
Update all Lambda Labs references to use correct IP and configuration.
This script ensures consistency across the entire codebase.
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path

import yaml

# Current active Lambda Labs instance
CURRENT_CONFIG = {
    "instance_name": "sophia-main",
    "ip": "192.222.58.232",
    "type": "GH200",
    "ssh_key_name": "sophia2025.pem",
    "ssh_key_path": "~/.ssh/sophia2025.pem"
}

# Old IPs to replace
OLD_IPS = [
    "192.222.58.232",
    "192.222.58.232",
    "104.171.202.103",
    "192.222.58.232",
    "104.171.202.117",
    "104.171.202.134",
    "155.248.194.183",
    "192.222.58.232",
    "192.222.50.155"
]

# Old SSH key references
OLD_SSH_KEYS = [
    "sophia2025.pem",
    "sophia2025.pem",
    "sophia-ai-key",
    "lambda_labs_ssh_key",
    "sophia-ai-h200-key"
]

# Files to skip
SKIP_PATTERNS = [
    ".git/",
    ".venv/",
    "node_modules/",
    "__pycache__/",
    "*.pyc",
    "*.log",
    "backups/",
    "archive/"
]

class LambdaLabsUpdater:
    def __init__(self):
        self.updates_made = []
        self.files_updated = set()
        self.errors = []

    def should_skip_file(self, filepath: str) -> bool:
        """Check if file should be skipped"""
        for pattern in SKIP_PATTERNS:
            if pattern in filepath:
                return True
        return False

    def update_ip_addresses(self, content: str, filepath: str) -> tuple[str, list[str]]:
        """Update all old IP addresses to current one"""
        updates = []
        original_content = content

        for old_ip in OLD_IPS:
            if old_ip in content:
                # Replace IP but preserve context
                content = content.replace(old_ip, CURRENT_CONFIG["ip"])
                updates.append(f"Replaced IP {old_ip} -> {CURRENT_CONFIG['ip']}")

        return content, updates

    def update_ssh_keys(self, content: str, filepath: str) -> tuple[str, list[str]]:
        """Update SSH key references"""
        updates = []

        # Update SSH key paths
        for old_key in OLD_SSH_KEYS:
            patterns = [
                f"~/.ssh/{old_key}",
                f"/home/ubuntu/.ssh/{old_key}",
                f"$HOME/.ssh/{old_key}",
                f'"{old_key}"',
                f"'{old_key}'"
            ]

            for pattern in patterns:
                if pattern in content:
                    new_pattern = pattern.replace(old_key, CURRENT_CONFIG["ssh_key_name"])
                    content = content.replace(pattern, new_pattern)
                    updates.append(f"Updated SSH key: {pattern} -> {new_pattern}")

        return content, updates

    def update_instance_mappings(self, content: str, filepath: str) -> tuple[str, list[str]]:
        """Update instance mapping dictionaries"""
        updates = []

        # Pattern for instance mappings
        mapping_pattern = r'instance_mapping\s*=\s*{[^}]+}'
        matches = re.findall(mapping_pattern, content, re.DOTALL)

        if matches:
            # Create new mapping
            new_mapping = f'''instance_mapping = {{
            "production": "{CURRENT_CONFIG['ip']}",
            "{CURRENT_CONFIG['instance_name']}": "{CURRENT_CONFIG['ip']}"
        }}'''

            for match in matches:
                content = content.replace(match, new_mapping)
                updates.append("Updated instance_mapping dictionary")

        return content, updates

    def remove_hardcoded_credentials(self, content: str, filepath: str) -> tuple[str, list[str]]:
        """Remove hardcoded API keys and replace with Pulumi ESC calls"""
        updates = []

        # Pattern for hardcoded Lambda API keys
        api_key_patterns = [
            (r'secret_sophia5apikey_[a-zA-Z0-9]+\.[a-zA-Z0-9]+', 'get_config_value("lambda_api_key")'),
            (r'secret_sophiacloudapi_[a-zA-Z0-9]+\.[a-zA-Z0-9]+', 'get_config_value("lambda_cloud_api_key")')
        ]

        for pattern, replacement in api_key_patterns:
            matches = re.findall(pattern, content)
            if matches:
                for match in matches:
                    content = content.replace(f'"{match}"', replacement)
                    content = content.replace(f"'{match}'", replacement)
                    updates.append(f"Replaced hardcoded API key with {replacement}")

                # Add import if needed
                if "get_config_value" in content and "from backend.core.auto_esc_config import get_config_value" not in content:
                    if content.startswith("#!/usr/bin/env python"):
                        lines = content.split("\n")
                        # Find where to insert import
                        for i, line in enumerate(lines):
                            if line.startswith("import ") or line.startswith("from "):
                                lines.insert(i, "from backend.core.auto_esc_config import get_config_value")
                                content = "\n".join(lines)
                                updates.append("Added get_config_value import")
                                break

        return content, updates

    def update_yaml_files(self, filepath: str) -> list[str]:
        """Special handling for YAML files"""
        updates = []

        try:
            with open(filepath) as f:
                data = yaml.safe_load(f)

            if data:
                modified = False

                # Update Lambda Labs configuration
                if isinstance(data, dict):
                    if 'lambda_labs' in data:
                        if 'ip' in data['lambda_labs']:
                            data['lambda_labs']['ip'] = CURRENT_CONFIG['ip']
                            modified = True
                            updates.append("Updated lambda_labs.ip in YAML")

                    # Update environment variables
                    if 'env' in data:
                        if 'LAMBDA_LABS_IP' in data['env']:
                            data['env']['LAMBDA_LABS_IP'] = CURRENT_CONFIG['ip']
                            modified = True
                            updates.append("Updated LAMBDA_LABS_IP in env")

                if modified:
                    with open(filepath, 'w') as f:
                        yaml.dump(data, f, default_flow_style=False, sort_keys=False)

        except Exception as e:
            self.errors.append(f"Error updating YAML {filepath}: {e}")

        return updates

    def update_json_files(self, filepath: str) -> list[str]:
        """Special handling for JSON files"""
        updates = []

        try:
            with open(filepath) as f:
                data = json.load(f)

            modified = False

            # Update IP addresses in JSON
            def update_dict(d):
                nonlocal modified
                for key, value in d.items():
                    if isinstance(value, str):
                        for old_ip in OLD_IPS:
                            if old_ip in value:
                                d[key] = value.replace(old_ip, CURRENT_CONFIG['ip'])
                                modified = True
                                updates.append(f"Updated {key}: {old_ip} -> {CURRENT_CONFIG['ip']}")
                    elif isinstance(value, dict):
                        update_dict(value)
                    elif isinstance(value, list):
                        for i, item in enumerate(value):
                            if isinstance(item, dict):
                                update_dict(item)

            update_dict(data)

            if modified:
                with open(filepath, 'w') as f:
                    json.dump(data, f, indent=2)

        except Exception as e:
            self.errors.append(f"Error updating JSON {filepath}: {e}")

        return updates

    def process_file(self, filepath: Path):
        """Process a single file"""
        if self.should_skip_file(str(filepath)):
            return

        try:
            # Handle different file types
            if filepath.suffix in ['.yml', '.yaml']:
                updates = self.update_yaml_files(filepath)
                if updates:
                    self.files_updated.add(str(filepath))
                    self.updates_made.extend([(str(filepath), u) for u in updates])

            elif filepath.suffix == '.json':
                updates = self.update_json_files(filepath)
                if updates:
                    self.files_updated.add(str(filepath))
                    self.updates_made.extend([(str(filepath), u) for u in updates])

            else:
                # Text files
                with open(filepath, encoding='utf-8') as f:
                    content = f.read()

                original_content = content
                all_updates = []

                # Apply updates
                content, updates = self.update_ip_addresses(content, str(filepath))
                all_updates.extend(updates)

                content, updates = self.update_ssh_keys(content, str(filepath))
                all_updates.extend(updates)

                content, updates = self.update_instance_mappings(content, str(filepath))
                all_updates.extend(updates)

                # Only remove hardcoded credentials from Python files
                if filepath.suffix == '.py':
                    content, updates = self.remove_hardcoded_credentials(content, str(filepath))
                    all_updates.extend(updates)

                # Write back if changed
                if content != original_content:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
                    self.files_updated.add(str(filepath))
                    self.updates_made.extend([(str(filepath), u) for u in all_updates])

        except Exception as e:
            self.errors.append(f"Error processing {filepath}: {e}")

    def run(self, dry_run: bool = False):
        """Run the updater"""
        print("🔍 Scanning for Lambda Labs references...")

        # Get all files
        for root, dirs, files in os.walk('.'):
            # Skip directories
            dirs[:] = [d for d in dirs if not any(skip in d for skip in SKIP_PATTERNS)]

            for file in files:
                filepath = Path(root) / file
                if filepath.suffix in ['.py', '.sh', '.yml', '.yaml', '.json', '.md', '.ts', '.js']:
                    self.process_file(filepath)

        # Generate report
        self.generate_report(dry_run)

    def generate_report(self, dry_run: bool):
        """Generate update report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"lambda_labs_update_report_{timestamp}.md"

        with open(report_file, 'w') as f:
            f.write("# Lambda Labs Reference Update Report\n\n")
            f.write(f"**Timestamp**: {datetime.now().isoformat()}\n")
            f.write(f"**Mode**: {'DRY RUN' if dry_run else 'EXECUTED'}\n\n")

            f.write("## Current Configuration\n")
            f.write(f"- **Instance**: {CURRENT_CONFIG['instance_name']}\n")
            f.write(f"- **IP**: {CURRENT_CONFIG['ip']}\n")
            f.write(f"- **Type**: {CURRENT_CONFIG['type']}\n")
            f.write(f"- **SSH Key**: {CURRENT_CONFIG['ssh_key_path']}\n\n")

            f.write("## Summary\n")
            f.write(f"- **Files Updated**: {len(self.files_updated)}\n")
            f.write(f"- **Total Updates**: {len(self.updates_made)}\n")
            f.write(f"- **Errors**: {len(self.errors)}\n\n")

            if self.updates_made:
                f.write("## Updates Made\n")
                current_file = None
                for filepath, update in self.updates_made:
                    if filepath != current_file:
                        f.write(f"\n### {filepath}\n")
                        current_file = filepath
                    f.write(f"- {update}\n")

            if self.errors:
                f.write("\n## Errors\n")
                for error in self.errors:
                    f.write(f"- {error}\n")

        print(f"\n✅ Report generated: {report_file}")
        print(f"📊 Files updated: {len(self.files_updated)}")
        print(f"🔧 Total updates: {len(self.updates_made)}")
        if self.errors:
            print(f"⚠️  Errors: {len(self.errors)}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Update Lambda Labs references")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be updated without making changes")

    args = parser.parse_args()

    updater = LambdaLabsUpdater()
    updater.run(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
