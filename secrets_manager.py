#!/usr/bin/env python3
"""
Sophia AI Secrets Manager

This script provides a comprehensive solution for managing secrets and environment variables
across different environments and repositories. It can:

1. Detect missing environment variables
2. Import secrets from various sources (.env files, Pulumi ESC, GitHub)
3. Export secrets to various destinations (.env files, Pulumi ESC, GitHub)
4. Validate secret configurations
5. Generate template .env files
6. Sync secrets across different environments

Usage:
    python secrets_manager.py detect-missing
    python secrets_manager.py import-from-env [--env-file .env]
    python secrets_manager.py export-to-env [--env-file .env.new]
    python secrets_manager.py sync-to-pulumi
    python secrets_manager.py sync-to-github
    python secrets_manager.py validate
    python secrets_manager.py generate-template
    python secrets_manager.py sync-all
"""

import os
import sys
import json
import argparse
import subprocess
import logging
import re
import base64
import hashlib
import getpass
from pathlib import Path
from typing import Dict, List, Set, Optional, Any, Tuple
import configparser
import time
import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Define required environment variables
REQUIRED_ENV_VARS = {
    # Core API Keys
    "ANTHROPIC_API_KEY": "Claude API key for AI capabilities",
    "OPENAI_API_KEY": "OpenAI API key for AI capabilities (optional)",
    "PULUMI_ACCESS_TOKEN": "Pulumi access token for infrastructure management",
    
    # Slack Integration
    "SLACK_BOT_TOKEN": "Slack bot token for Slack integration",
    "SLACK_APP_TOKEN": "Slack app token for Slack integration",
    "SLACK_SIGNING_SECRET": "Slack signing secret for Slack integration",
    
    # Linear Integration
    "LINEAR_API_TOKEN": "Linear API token for project management integration",
    "LINEAR_WORKSPACE_ID": "Linear workspace ID for project management integration",
    
    # Gong Integration
    "GONG_CLIENT_ID": "Gong client ID for call analysis integration",
    "GONG_CLIENT_SECRET": "Gong client secret for call analysis integration",
    
    # Database Credentials
    "POSTGRES_USER": "PostgreSQL username",
    "POSTGRES_PASSWORD": "PostgreSQL password",
    "POSTGRES_DB": "PostgreSQL database name",
    
    # Vercel Integration
    "VERCEL_ACCESS_TOKEN": "Vercel access token for deployment integration",
    "VERCEL_TEAM_ID": "Vercel team ID for deployment integration",
    
    # Lambda Labs Integration
    "LAMBDA_LABS_API_KEY": "Lambda Labs API key for compute resources",
    
    # Vector Database Integration
    "PINECONE_API_KEY": "Pinecone API key for vector database",
    "WEAVIATE_API_KEY": "Weaviate API key for vector database",
    
    # Snowflake Integration
    "SNOWFLAKE_ACCOUNT": "Snowflake account identifier",
    "SNOWFLAKE_USER": "Snowflake username",
    "SNOWFLAKE_PASSWORD": "Snowflake password",
    "SNOWFLAKE_DATABASE": "Snowflake database name",
    
    # Estuary Integration
    "ESTUARY_API_KEY": "Estuary API key for data flow management",
    
    # Airbyte Integration
    "AIRBYTE_API_KEY": "Airbyte API key for data integration",
    
    # Environment Configuration
    "SOPHIA_ENVIRONMENT": "Environment name (development, staging, production)",
    "PULUMI_ORGANIZATION": "Pulumi organization name",
    "PULUMI_PROJECT": "Pulumi project name",
}

# Optional environment variables
OPTIONAL_ENV_VARS = {
    "CLAUDE_MODEL": "Claude model to use (default: claude-3-5-sonnet-20241022)",
    "CLAUDE_MAX_TOKENS": "Maximum tokens for Claude responses (default: 4096)",
    "CLAUDE_ORGANIZATION_ID": "Claude organization ID (default: sophia-ai)",
    "OPENAI_MODEL": "OpenAI model to use (default: gpt-4-turbo)",
    "OPENAI_MAX_TOKENS": "Maximum tokens for OpenAI responses (default: 4096)",
    "REDIS_URL": "Redis URL (default: redis://localhost:6379)",
    "POSTGRES_HOST": "PostgreSQL host (default: localhost)",
    "POSTGRES_PORT": "PostgreSQL port (default: 5432)",
    "LOG_LEVEL": "Logging level (default: INFO)",
    "SSL_CERT_FILE": "SSL certificate file path",
}

# Secret categories for organization
SECRET_CATEGORIES = {
    "api_keys": ["ANTHROPIC_API_KEY", "OPENAI_API_KEY", "PULUMI_ACCESS_TOKEN", 
                "PINECONE_API_KEY", "WEAVIATE_API_KEY", "ESTUARY_API_KEY", 
                "AIRBYTE_API_KEY", "LAMBDA_LABS_API_KEY", "VERCEL_ACCESS_TOKEN"],
    
    "integration_credentials": ["GONG_CLIENT_ID", "GONG_CLIENT_SECRET", 
                               "LINEAR_API_TOKEN", "LINEAR_WORKSPACE_ID",
                               "SLACK_BOT_TOKEN", "SLACK_APP_TOKEN", "SLACK_SIGNING_SECRET",
                               "VERCEL_TEAM_ID"],
    
    "database_credentials": ["POSTGRES_USER", "POSTGRES_PASSWORD", "POSTGRES_DB", 
                            "POSTGRES_HOST", "POSTGRES_PORT", "SNOWFLAKE_ACCOUNT", 
                            "SNOWFLAKE_USER", "SNOWFLAKE_PASSWORD", "SNOWFLAKE_DATABASE"],
    
    "configuration": ["SOPHIA_ENVIRONMENT", "PULUMI_ORGANIZATION", "PULUMI_PROJECT",
                     "CLAUDE_MODEL", "CLAUDE_MAX_TOKENS", "CLAUDE_ORGANIZATION_ID",
                     "OPENAI_MODEL", "OPENAI_MAX_TOKENS", "LOG_LEVEL", "SSL_CERT_FILE"]
}

class SecretsManager:
    def __init__(self):
        self.env_vars = {}
        self.missing_vars = set()
        self.load_current_env_vars()
        
    def load_current_env_vars(self) -> None:
        """Load current environment variables"""
        # First, try to load from .env file if it exists
        if os.path.exists('.env'):
            self.import_from_env_file('.env')
        
        # Then, load from environment variables
        for var in list(REQUIRED_ENV_VARS.keys()) + list(OPTIONAL_ENV_VARS.keys()):
            if var in os.environ:
                self.env_vars[var] = os.environ[var]
                if var in self.missing_vars:
                    self.missing_vars.remove(var)
            elif var not in self.env_vars and var in REQUIRED_ENV_VARS:
                self.missing_vars.add(var)
    
    def detect_missing_env_vars(self) -> Set[str]:
        """Detect missing required environment variables"""
        missing = set()
        for var in REQUIRED_ENV_VARS:
            if var not in os.environ and var not in self.env_vars:
                missing.add(var)
        return missing
    
    def import_from_env_file(self, env_file: str = '.env') -> Tuple[int, int, List[str]]:
        """Import environment variables from .env file"""
        if not os.path.exists(env_file):
            logger.error(f"Environment file {env_file} not found")
            return 0, 0, []
        
        imported = 0
        skipped = 0
        imported_vars = []
        
        with open(env_file, 'r') as f:
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
                    
                    if key in self.env_vars and self.env_vars[key] == value:
                        skipped += 1
                    else:
                        self.env_vars[key] = value
                        imported += 1
                        imported_vars.append(key)
                        if key in self.missing_vars:
                            self.missing_vars.remove(key)
        
        return imported, skipped, imported_vars
    
    def export_to_env_file(self, env_file: str = '.env') -> int:
        """Export environment variables to .env file"""
        exported = 0
        
        # Create categories of variables for organization
        categorized_vars = {category: [] for category in SECRET_CATEGORIES}
        other_vars = []
        
        for key, value in sorted(self.env_vars.items()):
            found_category = False
            for category, vars_list in SECRET_CATEGORIES.items():
                if key in vars_list:
                    categorized_vars[category].append((key, value))
                    found_category = True
                    break
            
            if not found_category:
                other_vars.append((key, value))
        
        with open(env_file, 'w') as f:
            f.write("# Sophia AI Environment Variables\n")
            f.write(f"# Generated by secrets_manager.py on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            for category, vars_list in categorized_vars.items():
                if vars_list:
                    f.write(f"# {category.replace('_', ' ').title()}\n")
                    for key, value in sorted(vars_list):
                        f.write(f"{key}={value}\n")
                        exported += 1
                    f.write("\n")
            
            if other_vars:
                f.write("# Other Variables\n")
                for key, value in sorted(other_vars):
                    f.write(f"{key}={value}\n")
                    exported += 1
        
        return exported
    
    def sync_to_pulumi(self) -> Tuple[int, int, List[str]]:
        """Sync environment variables to Pulumi ESC"""
        if "PULUMI_ACCESS_TOKEN" not in self.env_vars:
            logger.error("PULUMI_ACCESS_TOKEN is required to sync with Pulumi ESC")
            return 0, 0, []
        
        # Set the PULUMI_ACCESS_TOKEN environment variable
        os.environ["PULUMI_ACCESS_TOKEN"] = self.env_vars["PULUMI_ACCESS_TOKEN"]
        
        # Get organization and project from env vars or use defaults
        org = self.env_vars.get("PULUMI_ORGANIZATION", "payready")
        project = self.env_vars.get("PULUMI_PROJECT", "sophia")
        
        # Create a temporary file with the secrets
        temp_file = "temp_secrets.json"
        with open(temp_file, 'w') as f:
            json.dump(self.env_vars, f)
        
        try:
            # Use Pulumi CLI to set the secrets
            result = subprocess.run(
                ["pulumi", "esc", "environment", "set", f"{org}/{project}", "--file", temp_file],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                logger.error(f"Failed to sync with Pulumi ESC: {result.stderr}")
                return 0, 0, []
            
            # Parse the output to get the number of secrets synced
            output = result.stdout
            synced = len(self.env_vars)
            return synced, 0, list(self.env_vars.keys())
            
        except Exception as e:
            logger.error(f"Error syncing with Pulumi ESC: {e}")
            return 0, 0, []
        finally:
            # Remove the temporary file
            if os.path.exists(temp_file):
                os.remove(temp_file)
    
    def sync_to_github(self) -> Tuple[int, int, List[str]]:
        """Sync environment variables to GitHub Secrets"""
        # This requires GitHub CLI (gh) to be installed and authenticated
        try:
            # Check if gh CLI is installed
            result = subprocess.run(["gh", "--version"], capture_output=True, text=True)
            if result.returncode != 0:
                logger.error("GitHub CLI (gh) is not installed or not in PATH")
                return 0, 0, []
            
            # Check if gh CLI is authenticated
            result = subprocess.run(["gh", "auth", "status"], capture_output=True, text=True)
            if result.returncode != 0:
                logger.error("GitHub CLI (gh) is not authenticated")
                return 0, 0, []
            
            # Get the repository from the git config
            result = subprocess.run(
                ["git", "config", "--get", "remote.origin.url"],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                logger.error("Failed to get repository URL from git config")
                return 0, 0, []
            
            repo_url = result.stdout.strip()
            # Extract owner/repo from the URL
            if "github.com" in repo_url:
                if repo_url.startswith("git@github.com:"):
                    # SSH URL format: git@github.com:owner/repo.git
                    repo_path = repo_url.split("git@github.com:")[1].split(".git")[0]
                elif repo_url.startswith("https://github.com/"):
                    # HTTPS URL format: https://github.com/owner/repo.git
                    repo_path = repo_url.split("https://github.com/")[1].split(".git")[0]
                else:
                    logger.error(f"Unsupported GitHub URL format: {repo_url}")
                    return 0, 0, []
            else:
                logger.error(f"Not a GitHub repository: {repo_url}")
                return 0, 0, []
            
            # Set secrets in GitHub
            synced = 0
            synced_vars = []
            
            for key, value in self.env_vars.items():
                # Use gh CLI to set the secret
                result = subprocess.run(
                    ["gh", "secret", "set", key, "-b", value, "-R", repo_path],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode != 0:
                    logger.error(f"Failed to set GitHub secret {key}: {result.stderr}")
                else:
                    synced += 1
                    synced_vars.append(key)
            
            return synced, 0, synced_vars
            
        except Exception as e:
            logger.error(f"Error syncing with GitHub: {e}")
            return 0, 0, []
    
    def validate_configuration(self) -> Tuple[bool, Dict[str, Any]]:
        """Validate the current configuration"""
        validation_results = {
            "missing_required": [],
            "present_required": [],
            "present_optional": [],
            "unknown_vars": [],
            "categories": {},
            "total_vars": len(self.env_vars),
            "required_vars": len(REQUIRED_ENV_VARS),
            "optional_vars": len(OPTIONAL_ENV_VARS),
            "completion_percentage": 0
        }
        
        # Check required variables
        for var in REQUIRED_ENV_VARS:
            if var in self.env_vars:
                validation_results["present_required"].append(var)
            else:
                validation_results["missing_required"].append(var)
        
        # Check optional variables
        for var in OPTIONAL_ENV_VARS:
            if var in self.env_vars:
                validation_results["present_optional"].append(var)
        
        # Check for unknown variables
        all_known_vars = set(REQUIRED_ENV_VARS.keys()) | set(OPTIONAL_ENV_VARS.keys())
        for var in self.env_vars:
            if var not in all_known_vars:
                validation_results["unknown_vars"].append(var)
        
        # Calculate completion percentage
        if len(REQUIRED_ENV_VARS) > 0:
            validation_results["completion_percentage"] = (
                len(validation_results["present_required"]) / len(REQUIRED_ENV_VARS)
            ) * 100
        
        # Check categories
        for category, vars_list in SECRET_CATEGORIES.items():
            category_results = {
                "total": len(vars_list),
                "present": 0,
                "missing": 0,
                "vars_present": [],
                "vars_missing": []
            }
            
            for var in vars_list:
                if var in self.env_vars:
                    category_results["present"] += 1
                    category_results["vars_present"].append(var)
                elif var in REQUIRED_ENV_VARS or var in OPTIONAL_ENV_VARS:
                    category_results["missing"] += 1
                    category_results["vars_missing"].append(var)
            
            validation_results["categories"][category] = category_results
        
        is_valid = len(validation_results["missing_required"]) == 0
        return is_valid, validation_results
    
    def generate_template(self, output_file: str = 'env.template') -> int:
        """Generate a template .env file with all required and optional variables"""
        generated = 0
        
        with open(output_file, 'w') as f:
            f.write("# Sophia AI Environment Variables Template\n")
            f.write(f"# Generated by secrets_manager.py on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("# Fill in the values and rename to .env\n\n")
            
            # Write required variables
            f.write("# Required Variables\n")
            for key, description in sorted(REQUIRED_ENV_VARS.items()):
                value = self.env_vars.get(key, "")
                # Mask sensitive values
                if value and any(sensitive in key.lower() for sensitive in ["key", "secret", "password", "token"]):
                    masked_value = value[0:4] + "..." + value[-4:] if len(value) > 8 else "..."
                    f.write(f"# {description}\n{key}={masked_value} # REPLACE THIS\n\n")
                else:
                    f.write(f"# {description}\n{key}={value}\n\n")
                generated += 1
            
            # Write optional variables
            f.write("# Optional Variables\n")
            for key, description in sorted(OPTIONAL_ENV_VARS.items()):
                value = self.env_vars.get(key, "")
                # Mask sensitive values
                if value and any(sensitive in key.lower() for sensitive in ["key", "secret", "password", "token"]):
                    masked_value = value[0:4] + "..." + value[-4:] if len(value) > 8 else "..."
                    f.write(f"# {description}\n{key}={masked_value} # REPLACE THIS\n\n")
                else:
                    f.write(f"# {description}\n{key}={value}\n\n")
                generated += 1
        
        return generated
    
    def sync_all(self) -> Dict[str, Any]:
        """Sync all secrets to all destinations"""
        results = {
            "env_file": {"exported": 0},
            "pulumi": {"synced": 0, "skipped": 0, "synced_vars": []},
            "github": {"synced": 0, "skipped": 0, "synced_vars": []},
            "template": {"generated": 0}
        }
        
        # Export to .env file
        results["env_file"]["exported"] = self.export_to_env_file()
        
        # Sync to Pulumi ESC
        synced, skipped, synced_vars = self.sync_to_pulumi()
        results["pulumi"]["synced"] = synced
        results["pulumi"]["skipped"] = skipped
        results["pulumi"]["synced_vars"] = synced_vars
        
        # Sync to GitHub
        synced, skipped, synced_vars = self.sync_to_github()
        results["github"]["synced"] = synced
        results["github"]["skipped"] = skipped
        results["github"]["synced_vars"] = synced_vars
        
        # Generate template
        results["template"]["generated"] = self.generate_template()
        
        return results
    
    def print_validation_results(self, validation_results: Dict[str, Any]) -> None:
        """Print validation results in a user-friendly format"""
        print("\n===== Sophia AI Secrets Validation =====")
        print(f"Completion: {validation_results['completion_percentage']:.1f}% ({len(validation_results['present_required'])}/{validation_results['required_vars']} required variables)")
        
        if validation_results["missing_required"]:
            print("\n❌ Missing Required Variables:")
            for var in sorted(validation_results["missing_required"]):
                print(f"  - {var}: {REQUIRED_ENV_VARS[var]}")
        
        print("\n✅ Categories Status:")
        for category, results in validation_results["categories"].items():
            category_name = category.replace('_', ' ').title()
            if results["total"] > 0:
                completion = (results["present"] / results["total"]) * 100
                print(f"  - {category_name}: {completion:.1f}% ({results['present']}/{results['total']})")
                
                if results["vars_missing"]:
                    print(f"    Missing: {', '.join(sorted(results['vars_missing']))}")
        
        if validation_results["unknown_vars"]:
            print("\n⚠️ Unknown Variables:")
            for var in sorted(validation_results["unknown_vars"]):
                print(f"  - {var}")
        
        print("\n=======================================")

def main():
    parser = argparse.ArgumentParser(description="Sophia AI Secrets Manager")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Detect missing environment variables
    detect_parser = subparsers.add_parser("detect-missing", help="Detect missing required environment variables")
    
    # Import from .env file
    import_parser = subparsers.add_parser("import-from-env", help="Import environment variables from .env file")
    import_parser.add_argument("--env-file", default=".env", help="Path to .env file (default: .env)")
    
    # Export to .env file
    export_parser = subparsers.add_parser("export-to-env", help="Export environment variables to .env file")
    export_parser.add_argument("--env-file", default=".env", help="Path to .env file (default: .env)")
    
    # Sync to Pulumi ESC
    sync_pulumi_parser = subparsers.add_parser("sync-to-pulumi", help="Sync environment variables to Pulumi ESC")
    
    # Sync to GitHub
    sync_github_parser = subparsers.add_parser("sync-to-github", help="Sync environment variables to GitHub Secrets")
    
    # Validate configuration
    validate_parser = subparsers.add_parser("validate", help="Validate the current configuration")
    
    # Generate template
    template_parser = subparsers.add_parser("generate-template", help="Generate a template .env file")
    template_parser.add_argument("--output-file", default="env.template", help="Path to output file (default: env.template)")
    
    # Sync all
    sync_all_parser = subparsers.add_parser("sync-all", help="Sync all secrets to all destinations")
    
    args = parser.parse_args()
    
    secrets_manager = SecretsManager()
    
    if args.command == "detect-missing":
        missing = secrets_manager.detect_missing_env_vars()
        if missing:
            print(f"❌ Missing {len(missing)} required environment variables:")
            for var in sorted(missing):
                print(f"  - {var}: {REQUIRED_ENV_VARS[var]}")
        else:
            print("✅ All required environment variables are set")
    
    elif args.command == "import-from-env":
        imported, skipped, imported_vars = secrets_manager.import_from_env_file(args.env_file)
        print(f"✅ Imported {imported} environment variables from {args.env_file}")
        if skipped > 0:
            print(f"⚠️ Skipped {skipped} environment variables (already set with same value)")
        if imported > 0:
            print(f"📋 Imported variables: {', '.join(imported_vars)}")
    
    elif args.command == "export-to-env":
        exported = secrets_manager.export_to_env_file(args.env_file)
        print(f"✅ Exported {exported} environment variables to {args.env_file}")
    
    elif args.command == "sync-to-pulumi":
        synced, skipped, synced_vars = secrets_manager.sync_to_pulumi()
        print(f"✅ Synced {synced} environment variables to Pulumi ESC")
        if skipped > 0:
            print(f"⚠️ Skipped {skipped} environment variables (already set with same value)")
        if synced > 0:
            print(f"📋 Synced variables: {', '.join(synced_vars)}")
    
    elif args.command == "sync-to-github":
        synced, skipped, synced_vars = secrets_manager.sync_to_github()
        print(f"✅ Synced {synced} environment variables to GitHub Secrets")
        if skipped > 0:
            print(f"⚠️ Skipped {skipped} environment variables (already set with same value)")
        if synced > 0:
            print(f"📋 Synced variables: {', '.join(synced_vars)}")
    
    elif args.command == "validate":
        is_valid, validation_results = secrets_manager.validate_configuration()
        secrets_manager.print_validation_results(validation_results)
        if is_valid:
            print("✅ Configuration is valid")
        else:
            print("❌ Configuration is invalid")
    
    elif args.command == "generate-template":
        generated = secrets_manager.generate_template(args.output_file)
        print(f"✅ Generated template with {generated} environment variables to {args.output_file}")
    
    elif args.command == "sync-all":
        results = secrets_manager.sync_all()
        print(f"✅ Exported {results['env_file']['exported']} environment variables to .env")
        print(f"✅ Synced {results['pulumi']['synced']} environment variables to Pulumi ESC")
        print(f"✅ Synced {results['github']['synced']} environment variables to GitHub Secrets")
        print(f"✅ Generated template with {results['template']['generated']} environment variables to env.template")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
