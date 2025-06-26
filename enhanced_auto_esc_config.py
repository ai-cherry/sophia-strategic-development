"""
Enhanced Sophia AI Configuration with Environment-Aware Secret Management
"""

from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum
import os
import json
import subprocess

class Environment(Enum):
    """Deployment environments."""
    PRODUCTION = "prod"
    STAGING = "stg"  
    DEVELOPMENT = "dev"

class SophiaPlatformSettings(BaseModel):
    """Platform-level settings."""
    name: str = "sophia-ai-platform"
    version: str = "v2.0.0"
    environment: str

class SophiaInfrastructureSettings(BaseModel):
    """Infrastructure service settings."""
    vercel_token: Optional[str] = None
    vercel_team_id: Optional[str] = None
    namecheap_api_key: Optional[str] = None
    namecheap_api_user: Optional[str] = None
    lambda_labs_api_key: Optional[str] = None

class SophiaDataSettings(BaseModel):
    """Data platform settings."""
    snowflake_account: Optional[str] = None
    snowflake_user: Optional[str] = None
    snowflake_password: Optional[str] = None
    snowflake_role: str = "ACCOUNTADMIN"
    snowflake_warehouse: str = "SOPHIA_AI_WH"
    snowflake_database: str = "SOPHIA_AI"
    pinecone_api_key: Optional[str] = None
    pinecone_environment: Optional[str] = None
    weaviate_api_key: Optional[str] = None

class SophiaIntegrationSettings(BaseModel):
    """Integration platform settings."""
    linear_api_key: Optional[str] = None
    asana_api_key: Optional[str] = None
    gong_access_key: Optional[str] = None
    gong_client_secret: Optional[str] = None
    apollo_api_key: Optional[str] = None
    hubspot_access_token: Optional[str] = None

class SophiaAISettings(BaseModel):
    """AI service settings."""
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    portkey_api_key: Optional[str] = None

class SophiaCommunicationSettings(BaseModel):
    """Communication service settings."""
    slack_bot_token: Optional[str] = None
    slack_webhook_url: Optional[str] = None
    discord_bot_token: Optional[str] = None

class SophiaSettings(BaseModel):
    """Complete Sophia AI configuration."""
    platform: SophiaPlatformSettings
    infrastructure: SophiaInfrastructureSettings = Field(default_factory=SophiaInfrastructureSettings)
    data: SophiaDataSettings = Field(default_factory=SophiaDataSettings)
    integration: SophiaIntegrationSettings = Field(default_factory=SophiaIntegrationSettings)
    ai: SophiaAISettings = Field(default_factory=SophiaAISettings)
    communication: SophiaCommunicationSettings = Field(default_factory=SophiaCommunicationSettings)

def load_environment_settings(environment: Environment) -> SophiaSettings:
    """Load settings for specific environment from Pulumi ESC."""
    esc_env = f"scoobyjava-org/sophia-ai-{environment.value}"
    
    try:
        result = subprocess.run([
            "pulumi", "env", "open", esc_env, "--format", "json"
        ], capture_output=True, text=True, check=True)
        
        config_data = json.loads(result.stdout)
        sophia_config = config_data.get("values", {}).get("sophia", {})
        
        return SophiaSettings(
            platform=SophiaPlatformSettings(**sophia_config.get("platform", {})),
            infrastructure=SophiaInfrastructureSettings(**sophia_config.get("infrastructure", {})),
            data=SophiaDataSettings(**sophia_config.get("data", {})),
            integration=SophiaIntegrationSettings(**sophia_config.get("integration", {})),
            ai=SophiaAISettings(**sophia_config.get("ai", {})),
            communication=SophiaCommunicationSettings(**sophia_config.get("communication", {}))
        )
    
    except (subprocess.CalledProcessError, json.JSONDecodeError, KeyError) as e:
        print(f"Failed to load from Pulumi ESC: {e}")
        return load_fallback_settings()

def load_fallback_settings() -> SophiaSettings:
    """Load settings from environment variables as fallback."""
    return SophiaSettings(
        platform=SophiaPlatformSettings(
            environment=os.getenv("ENVIRONMENT", "development")
        ),
        infrastructure=SophiaInfrastructureSettings(
            vercel_token=os.getenv("SOPHIA_VERCEL_TOKEN_PROD"),
            vercel_team_id=os.getenv("SOPHIA_VERCEL_TEAM_ID_PROD"),
            namecheap_api_key=os.getenv("SOPHIA_NAMECHEAP_API_KEY_PROD"),
            lambda_labs_api_key=os.getenv("SOPHIA_LAMBDA_LABS_API_KEY_PROD")
        ),
        data=SophiaDataSettings(
            snowflake_account=os.getenv("SOPHIA_SNOWFLAKE_ACCOUNT_PROD"),
            snowflake_user=os.getenv("SOPHIA_SNOWFLAKE_USER_PROD"),
            snowflake_password=os.getenv("SOPHIA_SNOWFLAKE_PASSWORD_PROD"),
            pinecone_api_key=os.getenv("SOPHIA_PINECONE_API_KEY_PROD")
        ),
        integration=SophiaIntegrationSettings(
            linear_api_key=os.getenv("SOPHIA_LINEAR_API_KEY_PROD"),
            asana_api_key=os.getenv("SOPHIA_ASANA_API_KEY_PROD"),
            gong_access_key=os.getenv("SOPHIA_GONG_ACCESS_KEY_PROD"),
            gong_client_secret=os.getenv("SOPHIA_GONG_CLIENT_SECRET_PROD"),
            hubspot_access_token=os.getenv("SOPHIA_HUBSPOT_ACCESS_TOKEN_PROD")
        ),
        ai=SophiaAISettings(
            openai_api_key=os.getenv("SOPHIA_OPENAI_API_KEY_PROD"),
            anthropic_api_key=os.getenv("SOPHIA_ANTHROPIC_API_KEY_PROD"),
            portkey_api_key=os.getenv("SOPHIA_PORTKEY_API_KEY_PROD")
        ),
        communication=SophiaCommunicationSettings(
            slack_bot_token=os.getenv("SOPHIA_SLACK_BOT_TOKEN_PROD"),
            slack_webhook_url=os.getenv("SOPHIA_SLACK_WEBHOOK_PROD")
        )
    )

# Default configuration
current_env = Environment(os.getenv("ENVIRONMENT", "development"))
config = load_environment_settings(current_env)
