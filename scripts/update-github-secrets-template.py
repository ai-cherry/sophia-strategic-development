#!/usr/bin/env python3
"""
GitHub Organization Secrets Management Template
Secure credential management for Sophia AI Platform
"""

import os
import requests
import base64
import json
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GitHubSecretsManager:
    """Manage GitHub organization secrets securely"""
    
    def __init__(self, org: str, token: str):
        self.org = org
        self.token = token
        self.base_url = f"https://api.github.com/orgs/{org}"
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
    
    def get_public_key(self):
        """Get organization public key for encryption"""
        response = requests.get(f"{self.base_url}/actions/secrets/public-key", headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def encrypt_secret(self, public_key: str, secret_value: str) -> str:
        """Encrypt secret using organization public key"""
        public_key_bytes = base64.b64decode(public_key)
        public_key_obj = serialization.load_der_public_key(public_key_bytes)
        
        encrypted_bytes = public_key_obj.encrypt(
            secret_value.encode('utf-8'),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        return base64.b64encode(encrypted_bytes).decode('utf-8')
    
    def create_or_update_secret(self, secret_name: str, secret_value: str):
        """Create or update organization secret"""
        public_key_data = self.get_public_key()
        encrypted_value = self.encrypt_secret(public_key_data['key'], secret_value)
        
        payload = {
            "encrypted_value": encrypted_value,
            "key_id": public_key_data['key_id'],
            "visibility": "all"
        }
        
        response = requests.put(
            f"{self.base_url}/actions/secrets/{secret_name}",
            headers=self.headers,
            json=payload
        )
        
        if response.status_code in [201, 204]:
            logger.info(f"Successfully updated secret: {secret_name}")
        else:
            logger.error(f"Failed to update secret {secret_name}: {response.text}")
            response.raise_for_status()
    
    def update_all_secrets(self):
        """Update all required secrets for Sophia AI project"""
        
        # Template secrets - replace with actual values from environment
        secrets = {
            # Estuary Flow Credentials
            "ESTUARY_API_TOKEN": os.getenv('ESTUARY_API_TOKEN', 'your-estuary-api-token'),
            "ESTUARY_ACCESS_TOKEN": os.getenv('ESTUARY_ACCESS_TOKEN', 'your-estuary-access-token'),
            
            # Gong API Credentials
            "GONG_ACCESS_KEY": os.getenv('GONG_ACCESS_KEY', 'your-gong-access-key'),
            "GONG_ACCESS_KEY_SECRET": os.getenv('GONG_ACCESS_KEY_SECRET', 'your-gong-access-key-secret'),
            
            # HubSpot API Credentials
            "HUBSPOT_API_TOKEN": os.getenv('HUBSPOT_API_TOKEN', 'your-hubspot-api-token'),
            "HUBSPOT_CLIENT_SECRET": os.getenv('HUBSPOT_CLIENT_SECRET', 'your-hubspot-client-secret'),
            
            # Vercel Deployment
            "VERCEL_ACCESS_TOKEN": os.getenv('VERCEL_ACCESS_TOKEN', 'your-vercel-access-token'),
            
            # GitHub Personal Access Token
            "GITHUB_PAT": os.getenv('GITHUB_PAT', 'your-github-personal-access-token'),
            
            # Pulumi ESC Configuration
            "PULUMI_ESC_ENVIRONMENT": "scoobyjava-org/default/sophia-ai-production",
            "PULUMI_ACCESS_TOKEN": os.getenv('PULUMI_ACCESS_TOKEN', 'your-pulumi-access-token'),
            
            # Infrastructure Credentials
            "LAMBDA_LABS_API_KEY": os.getenv('LAMBDA_LABS_API_KEY', 'your-lambda-labs-api-key'),
            "LAMBDA_LABS_SSH_KEY": os.getenv('LAMBDA_LABS_SSH_KEY', 'your-lambda-labs-ssh-key'),
            
            # Database Configuration
            "POSTGRESQL_CONNECTION_STRING": os.getenv('POSTGRESQL_CONNECTION_STRING', 'postgresql://user:pass@host:5432/sophia_staging'),
            "REDIS_CONNECTION_STRING": os.getenv('REDIS_CONNECTION_STRING', 'redis://host:6379/0'),
            
            # Snowflake Configuration
            "SNOWFLAKE_ACCOUNT": os.getenv('SNOWFLAKE_ACCOUNT', 'your-snowflake-account'),
            "SNOWFLAKE_USER": os.getenv('SNOWFLAKE_USER', 'PROGRAMMATIC_SERVICE_USER'),
            "SNOWFLAKE_PASSWORD": os.getenv('SNOWFLAKE_PASSWORD', 'your-snowflake-password'),
            "SNOWFLAKE_WAREHOUSE": os.getenv('SNOWFLAKE_WAREHOUSE', 'SOPHIA_WH'),
            "SNOWFLAKE_DATABASE": os.getenv('SNOWFLAKE_DATABASE', 'SOPHIA_AI'),
            "SNOWFLAKE_SCHEMA": os.getenv('SNOWFLAKE_SCHEMA', 'CONVERSATION_INTELLIGENCE'),
            
            # Webhook Configuration
            "GONG_WEBHOOK_BASE_URL": os.getenv('GONG_WEBHOOK_BASE_URL', 'https://your-sophia-platform.com'),
            "GONG_WEBHOOK_JWT_PUBLIC_KEY": os.getenv('GONG_WEBHOOK_JWT_PUBLIC_KEY', 'your-jwt-public-key'),
            
            # Monitoring and Alerting
            "SLACK_WEBHOOK_URL": os.getenv('SLACK_WEBHOOK_URL', 'your-slack-webhook-url'),
            "DATADOG_API_KEY": os.getenv('DATADOG_API_KEY', 'your-datadog-api-key'),
        }
        
        logger.info(f"Updating {len(secrets)} organization secrets...")
        
        for secret_name, secret_value in secrets.items():
            if secret_value and not secret_value.startswith('your-'):
                self.create_or_update_secret(secret_name, secret_value)
            else:
                logger.warning(f"Skipping {secret_name} - no value provided or using template value")
        
        logger.info("Secret update process completed")

def main():
    """Main execution function"""
    github_token = os.getenv('GITHUB_PAT')
    organization = "ai-cherry"
    
    if not github_token:
        logger.error("GITHUB_PAT environment variable not set")
        return
    
    if github_token.startswith('your-'):
        logger.error("Please set actual GitHub PAT, not template value")
        return
    
    try:
        manager = GitHubSecretsManager(organization, github_token)
        manager.update_all_secrets()
        logger.info("✅ GitHub secrets update completed successfully")
        
    except Exception as e:
        logger.error(f"❌ Failed to update GitHub secrets: {e}")
        raise

if __name__ == "__main__":
    main()

