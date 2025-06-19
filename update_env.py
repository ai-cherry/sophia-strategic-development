#!/usr/bin/env python3
"""
Sophia AI Environment Updater

This script automatically updates the .env file with the values from the current environment.
It reads the existing .env file, extracts the values, and then updates the env.template file
with those values to create a new .env file.

Usage:
    python update_env.py [--input-env .env] [--template env.template] [--output-env .env.new]
"""

import os
import sys
import argparse
import logging
from typing import Dict, List, Set, Optional, Any, Tuple

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def read_env_file(file_path: str) -> Dict[str, str]:
    """Read environment variables from a .env file"""
    env_vars = {}
    
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return env_vars
    
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                # Remove quotes if present
                if (value.startswith('"') and value.endswith('"')) or \
                   (value.startswith("'") and value.endswith("'")):
                    value = value[1:-1]
                
                # Remove comments
                if '#' in value:
                    value = value.split('#', 1)[0].strip()
                
                env_vars[key] = value
    
    return env_vars

def update_template_with_values(template_path: str, env_vars: Dict[str, str], output_path: str) -> int:
    """Update the template file with values from env_vars and write to output_path"""
    if not os.path.exists(template_path):
        logger.error(f"Template file not found: {template_path}")
        return 0
    
    updated = 0
    output_lines = []
    
    with open(template_path, 'r') as f:
        for line in f:
            if '=' in line and not line.strip().startswith('#'):
                key = line.split('=', 1)[0].strip()
                if key in env_vars:
                    output_lines.append(f"{key}={env_vars[key]}\n")
                    updated += 1
                else:
                    output_lines.append(line)
            else:
                output_lines.append(line)
    
    with open(output_path, 'w') as f:
        f.writelines(output_lines)
    
    return updated

def main():
    parser = argparse.ArgumentParser(description="Sophia AI Environment Updater")
    parser.add_argument("--input-env", default=".env", help="Path to input .env file (default: .env)")
    parser.add_argument("--template", default="env.template", help="Path to template file (default: env.template)")
    parser.add_argument("--output-env", default=".env.new", help="Path to output .env file (default: .env.new)")
    
    args = parser.parse_args()
    
    # Read environment variables from input .env file
    env_vars = read_env_file(args.input_env)
    logger.info(f"Read {len(env_vars)} environment variables from {args.input_env}")
    
    # Update template with values from env_vars
    updated = update_template_with_values(args.template, env_vars, args.output_env)
    logger.info(f"Updated {updated} environment variables in {args.output_env}")
    
    print(f"\n✅ Updated {updated} environment variables in {args.output_env}")
    print(f"\nNext steps:")
    print(f"1. Review the updated .env file: {args.output_env}")
    print(f"2. Replace the existing .env file: mv {args.output_env} {args.input_env}")
    print(f"3. Validate the configuration: ./secrets_manager.py validate")

if __name__ == "__main__":
    main()
