#!/usr/bin/env python3
"""
Comprehensive Pulumi ESC Configuration Update Script
Maps all GitHub Organization Secrets to Pulumi ESC environment
Ensures code-wide alignment with existing secret names
"""

import json
import logging
import subprocess
import sys
from typing import Any, Dict, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ComprehensivePulumiESCUpdater:
    """
    Comprehensive Pulumi ESC updater that maps all GitHub Organization Secrets
    to the Pulumi ESC environment for secure credential management
    """
    
    def __init__(self, environment: str = "scoobyjava-org/default/sophia-ai-production"):
        self.environment = environment
        self.github_secrets_mapping = self._get_github_secrets_mapping()
    
    def _get_github_secrets_mapping(self) -> Dict[str, Dict[str, str]]:
        """
        Map GitHub Organization Secrets to Pulumi ESC configuration structure
        Based on discovered secrets from ai-cherry organization
        """
        return {
            "infrastructure": {
                "lambda_labs": {
                    "api_key": "${LAMBDA_API_KEY}",
                    "ip_address": "${LAMBDA_IP_ADDRESS}",
                    "ssh_private_key": "${LAMBDA_SSH_PRIVATE_KEY}"
                },
                "database": {
                    "host": "${DATABASE_HOST}",
                    "url": "${DATABASE_URL}",
                    "ssh_key": "${DATABASE_SSH_KEY}"
                },
                "kubernetes": {
                    "cluster_id": "${KUBERNETES_CLUSTER_ID}",
                    "namespace": "${KUBERNETES_NAMESPACE}"
                },
                "load_balancer": {
                    "host": "${LOAD_BALANCER_HOST}"
                }
            },
            
            "data_pipeline": {
                "estuary_flow": {
                    "access_token": "${ESTUARY_ACCESS_TOKEN}",
                    "refresh_token": "${ESTUARY_REFRESH_TOKEN}"
                },
                "gong": {
                    "access_key": "${GONG_ACCESS_KEY}",
                    "access_key_secret": "${GONG_ACCESS_KEY_SECRET}",
                    "base_url": "${GONG_BASE_URL}",
                    "client_access_key": "${GONG_CLIENT_ACCESS_KEY}",
                    "client_secret": "${GONG_CLIENT_SECRET}"
                },
                "hubspot": {
                    "access_token": "${HUBSPOT_ACCESS_TOKEN}",
                    "client_secret": "${HUBSPOT_CLIENT_SECRET}"
                },
                "estuary": {
                    "access_token": "${ESTUARY_ACCESS_TOKEN}",
                    "client_id": "${ESTUARY_CLIENT_ID}",
                    "client_secret": "${ESTUARY_CLIENT_SECRET}"
                }
            },
            
            "ai_services": {
                "anthropic": {
                    "api_key": "${ANTHROPIC_API_KEY}"
                },
                "groq": {
                    "api_key": "${GROQ_API_KEY}",
                    "virtual_key": "${GROQ_VIRTUAL_KEY}"
                },
                "mistral": {
                    "api_key": "${MISTRAL_API_KEY}",
                    "virtual_key": "${MISTRAL_VIRTUAL_KEY}"
                },
                "cohere": {
                    "api_key": "${COHERE_API_KEY}",
                    "virtual_key": "${COHERE_VIRTUAL_KEY}"
                },
                "codestral": {
                    "api_key": "${CODESTRAL_API_KEY}",
                    "org_id": "${CODESTRAL_ORG_ID}",
                    "org_name": "${CODESTRAL_ORG_NAME}"
                },
                "huggingface": {
                    "api_token": "${HUGGINGFACE_API_TOKEN}"
                },
                "langchain": {
                    "api_key": "${LANGCHAIN_API_KEY}"
                },
                "langsmith": {
                    "api_key": "${LANGSMITH_API_KEY}",
                    "org_id": "${LANGSMITH_ORG_ID}"
                },
                "llama": {
                    "api_key": "${LLAMA_API_KEY}"
                }
            },
            
            "security": {
                "encryption": {
                    "key": "${ENCRYPTION_KEY}",
                    "backup_key": "${BACKUP_ENCRYPTION_KEY}"
                },
                "jwt": {
                    "secret": "${JWT_SECRET}"
                },
                "api": {
                    "secret_key": "${API_SECRET_KEY}"
                }
            },
            
            "development": {
                "github": {
                    "api_token": "${GH_API_TOKEN}",
                    "classic_pat": "${GH_CLASSIC_PAT_TOKEN}",
                    "fine_grained_token": "${GH_FINE_GRAINED_TOKEN}",
                    "ip_address": "${GH_IP_ADDRESS}"
                },
                "docker": {
                    "username": "${DOCKERHUB_USERNAME}",
                    "token": "${DOCKER_TOKEN}",
                    "personal_access_token": "${DOCKER_PERSONAL_ACCESS_TOKEN}",
                    "user_name": "${DOCKER_USER_NAME}"
                },
                "npm": {
                    "api_token": "${NPM_API_TOKEN}"
                }
            },
            
            "monitoring": {
                "grafana": {
                    "url": "${GRAFANA_URL}",
                    "username": "${GRAFANA_USERNAME}",
                    "password": "${GRAFANA_PASSWORD}"
                },
                "kibana": {
                    "url": "${KIBANA_URL}"
                }
            },
            
            "productivity_tools": {
                "notion": {
                    "api_key": "${NOTION_API_KEY}"
                },
                "linear": {
                    "api_key": "${LINEAR_API_KEY}"
                },
                "asana": {
                    "api_token": "${ASANA_API_TOKEN}"
                },
                "figma": {
                    "pat": "${FIGMA_PAT}",
                    "project_id": "${FIGMA_PROJECT_ID}"
                }
            },
            
            "external_services": {
                "apollo": {
                    "api_key": "${APOLLO_API_KEY}"
                },
                "brave": {
                    "api_key": "${BRAVE_API_KEY}"
                },
                "namecheap": {
                    "api_key": "${NAMECHEAP_API_KEY}",
                    "username": "${NAMECHEAP_USERNAME}"
                },
                "ngrok": {
                    "authtoken": "${NGROK_AUTHTOKEN}"
                }
            }
        }
    
    def update_pulumi_esc_environment(self) -> bool:
        """
        Update the complete Pulumi ESC environment with mapped GitHub secrets
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            logger.info(f"Updating Pulumi ESC environment: {self.environment}")
            
            # Create the complete configuration
            esc_config = {
                "values": self.github_secrets_mapping
            }
            
            # Convert to YAML format for Pulumi ESC
            config_yaml = self._dict_to_yaml(esc_config)
            
            # Update Pulumi ESC environment
            result = subprocess.run(
                ["pulumi", "env", "set", self.environment, "--file", "-"],
                input=config_yaml,
                text=True,
                capture_output=True,
                timeout=60
            )
            
            if result.returncode == 0:
                logger.info("Successfully updated Pulumi ESC environment")
                return True
            else:
                logger.error(f"Failed to update Pulumi ESC: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating Pulumi ESC environment: {e}")
            return False
    
    def _dict_to_yaml(self, data: Dict[str, Any], indent: int = 0) -> str:
        """
        Convert dictionary to YAML format
        
        Args:
            data: Dictionary to convert
            indent: Current indentation level
            
        Returns:
            str: YAML formatted string
        """
        yaml_lines = []
        indent_str = "  " * indent
        
        for key, value in data.items():
            if isinstance(value, dict):
                yaml_lines.append(f"{indent_str}{key}:")
                yaml_lines.append(self._dict_to_yaml(value, indent + 1))
            else:
                yaml_lines.append(f"{indent_str}{key}: {value}")
        
        return "\n".join(yaml_lines)
    
    def validate_configuration(self) -> bool:
        """
        Validate the Pulumi ESC configuration
        
        Returns:
            bool: True if valid, False otherwise
        """
        try:
            result = subprocess.run(
                ["pulumi", "env", "get", self.environment],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                logger.info("Pulumi ESC configuration validation successful")
                return True
            else:
                logger.error(f"Pulumi ESC validation failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error validating Pulumi ESC configuration: {e}")
            return False
    
    def sync_from_github_secrets(self) -> bool:
        """
        Sync configuration from GitHub Organization Secrets
        
        Returns:
            bool: True if successful, False otherwise
        """
        logger.info("Syncing configuration from GitHub Organization Secrets...")
        
        # Update the environment with mapped secrets
        if self.update_pulumi_esc_environment():
            # Validate the configuration
            if self.validate_configuration():
                logger.info("GitHub secrets sync completed successfully")
                return True
            else:
                logger.error("Configuration validation failed after sync")
                return False
        else:
            logger.error("Failed to update Pulumi ESC environment")
            return False


def main():
    """Main execution function"""
    updater = ComprehensivePulumiESCUpdater()
    
    logger.info("Starting comprehensive Pulumi ESC update...")
    
    if updater.sync_from_github_secrets():
        logger.info("✅ Pulumi ESC update completed successfully")
        sys.exit(0)
    else:
        logger.error("❌ Pulumi ESC update failed")
        sys.exit(1)


if __name__ == "__main__":
    main()

