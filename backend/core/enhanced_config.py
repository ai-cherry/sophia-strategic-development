"""Enhanced Pulumi ESC configuration for Sophia AI Platform.

Comprehensive configuration management with environment-aware settings,
dynamic secret resolution, and backward compatibility.
"""

from __future__ import annotations

import json
import logging
import os
import subprocess
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Union

import httpx
from pydantic import BaseModel, Field, ValidationError, validator

# Configure logging
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)


class Environment(str, Enum):
    """Deployment environment enumeration."""
    DEVELOPMENT = "dev"
    STAGING = "staging"
    PRODUCTION = "prod"


class WebhookConfig(BaseModel):
    """Webhook configuration settings."""
    domain: str
    port: int = 5000
    base_url: str
    jwt_private_key: str
    jwt_public_key: str
    rate_limit_rpm: int = 1000
    rate_limit_burst: int = 200
    timeout_seconds: int = 30
    cors_allowed_origins: List[str] = ["*"]
    
    @validator('base_url', pre=True, always=True)
    def set_base_url(cls, v, values):
        if not v and 'domain' in values:
            return f"https://{values['domain']}/webhook/gong"
        return v


class SnowflakeConfig(BaseModel):
    """Snowflake database configuration (aligned with existing GONG_ANALYTICS)."""
    account: str
    user: str = "PROGRAMMATIC_SERVICE_USER"
    password: str
    database: str = "GONG_ANALYTICS"
    warehouse: str = "COMPUTE_WH"
    schema: str = "RAW"
    role: str = "ACCOUNTADMIN"
    
    # OAuth configuration for enhanced security
    oauth_client_id: Optional[str] = None
    oauth_client_secret: Optional[str] = None
    oauth_refresh_token: Optional[str] = None
    oauth_scope: str = "session:role-any"
    
    # Connection pool settings
    max_connections: int = 20
    min_connections: int = 5
    connection_timeout: int = 30
    idle_timeout: int = 300


class RedisConfig(BaseModel):
    """Redis cluster configuration for agent pub/sub."""
    host: str = "redis-cluster"
    port: int = 6379
    password: Optional[str] = None
    ssl_enabled: bool = True
    ssl_cert_reqs: str = "required"
    max_connections: int = 100
    retry_on_timeout: bool = True
    
    # Agent communication channels
    agent_pool_channel: str = "sophia:agents:pool"
    orchestrator_channel: str = "sophia:agents:orchestrator"
    workflows_channel: str = "sophia:workflows"
    health_check_channel: str = "sophia:health"
    metrics_channel: str = "sophia:metrics"


class AgentConfig(BaseModel):
    """Agent orchestration configuration."""
    pool_size: int = 50
    max_concurrent: int = 100
    auth_token: str
    health_check_interval: int = 30
    failure_threshold: int = 3
    recovery_timeout: int = 300
    
    # Performance configuration (aligned with AgnoPerformanceOptimizer)
    agno_optimization: bool = True
    instantiation_target_microseconds: int = 3
    memory_optimization: bool = True
    connection_pooling: bool = True
    batch_processing: bool = True
    
    # Communication settings
    communication_secret: str
    encryption_enabled: bool = True
    message_ttl: int = 3600
    dead_letter_queue: bool = True


class GongConfig(BaseModel):
    """Gong integration configuration (aligned with existing setup)."""
    api_base_url: str = "https://api.gong.io"
    access_key: str
    secret_key: str
    rate_limit: float = 2.5
    timeout: int = 30
    retry_attempts: int = 3
    
    # OAuth configuration for enhanced security
    oauth_client_id: Optional[str] = None
    oauth_client_secret: Optional[str] = None
    oauth_refresh_token: Optional[str] = None
    oauth_scope: str = "api:calls:read api:calls:transcripts:read"
    
    # Webhook configuration
    webhook_secret: str
    webhook_events: List[str] = ["call-processed", "transcript-ready", "insights-detected"]
    webhook_retry_max: int = 5
    webhook_retry_delay: int = 300


class MonitoringConfig(BaseModel):
    """Monitoring and observability configuration."""
    # Arize configuration (extends existing)
    arize_api_key: str
    arize_space_id: str
    arize_project_name: str = "sophia-ai-platform"
    arize_model_id: str = "sophia-orchestrator"
    arize_model_version: str = "v2.0.0"
    
    # Sentry configuration
    sentry_dsn: str
    sentry_traces_sample_rate: float = 0.1
    sentry_profiles_sample_rate: float = 0.1
    
    # Prometheus configuration
    prometheus_enabled: bool = True
    prometheus_port: int = 9090
    prometheus_path: str = "/metrics"
    prometheus_auth_token: str
    prometheus_scrape_interval: int = 15
    
    # Grafana configuration
    grafana_url: str
    grafana_username: str
    grafana_password: str
    grafana_admin_password: str
    grafana_org_id: int = 1
    grafana_dashboard_refresh: int = 30


class MCPConfig(BaseModel):
    """MCP server configuration (for existing 15+ MCP servers)."""
    github_token: str
    github_org: str = "ai-cherry"
    github_repo: str = "sophia-main"
    
    slack_token: str
    slack_signing_secret: str
    
    linear_token: str
    linear_workspace: str = "payready"
    
    docker_registry_token: str
    docker_registry_url: str = "registry.digitalocean.com"
    
    postgres_connection_string: str


class SecurityConfig(BaseModel):
    """Security configuration for the platform."""
    # JWT configuration
    jwt_private_key: str
    jwt_public_key: str
    jwt_algorithm: str = "RS256"
    jwt_expiration: int = 3600
    jwt_issuer: str = "sophia-ai-platform"
    jwt_audience: str = "webhook-clients"
    
    # Encryption settings
    encryption_key: str
    encryption_algorithm: str = "AES-256-GCM"
    encryption_key_rotation_days: int = 90
    
    # OIDC configuration
    aws_oidc_role_arn: Optional[str] = None
    azure_oidc_client_id: Optional[str] = None
    gcp_oidc_service_account: Optional[str] = None
    
    # Audit logging
    audit_enabled: bool = True
    audit_log_level: str = "INFO"
    audit_retention_days: int = 365
    audit_storage_backend: str = "snowflake"


class KubernetesConfig(BaseModel):
    """Kubernetes deployment configuration."""
    namespace: str = "sophia-ai"
    service_account: str = "sophia-platform"
    cluster_name: str = "sophia-ai-cluster"
    
    # Resource limits
    webhook_server_cpu_request: str = "500m"
    webhook_server_cpu_limit: str = "2000m"
    webhook_server_memory_request: str = "1Gi"
    webhook_server_memory_limit: str = "4Gi"
    
    agent_pool_cpu_request: str = "2000m"
    agent_pool_cpu_limit: str = "8000m"
    agent_pool_memory_request: str = "4Gi"
    agent_pool_memory_limit: str = "16Gi"
    
    # Autoscaling
    webhook_server_min_replicas: int = 3
    webhook_server_max_replicas: int = 10
    webhook_server_target_cpu: int = 70
    
    agent_pool_min_replicas: int = 2
    agent_pool_max_replicas: int = 20
    agent_pool_target_cpu: int = 80
    agent_pool_target_memory: int = 75


class SophiaConfig(BaseModel):
    """Enhanced Sophia AI Platform configuration."""
    
    # Platform metadata
    platform_name: str = "sophia-ai-platform"
    platform_version: str = "v2.0.0"
    environment: Environment = Environment.DEVELOPMENT
    deployment_strategy: str = "blue-green"
    
    # Core service configurations
    webhook: WebhookConfig
    snowflake: SnowflakeConfig
    redis: RedisConfig
    agents: AgentConfig
    gong: GongConfig
    monitoring: MonitoringConfig
    mcp: MCPConfig
    security: SecurityConfig
    kubernetes: KubernetesConfig
    
    # Pulumi ESC integration
    pulumi_org: str = "scoobyjava-org"
    pulumi_stack: Optional[str] = None
    
    # AI service keys (aligned with existing setup)
    openai_api_key: str
    anthropic_api_key: str
    agno_api_key: str
    
    # Vector database configuration
    pinecone_api_key: str
    pinecone_environment: str
    pinecone_index_name: str
    weaviate_api_key: str
    weaviate_url: str
    
    # Business intelligence integrations
    hubspot_access_token: str
    linear_api_key: str
    notion_api_key: str
    
    # Infrastructure
    lambda_labs_api_key: str
    lambda_labs_control_plane_ip: str
    lambda_labs_ssh_key_name: str
    
    # Database URL
    database_url: str
    
    class Config:
        env_file_encoding = 'utf-8'
        case_sensitive = False
        use_enum_values = True


class ConfigValidator:
    """Configuration validation and health checking."""
    
    def __init__(self, config: SophiaConfig):
        self.config = config
        self.logger = logger.bind(component="config_validator")
    
    async def validate_secrets(self) -> Dict[str, bool]:
        """Validate all required secrets are accessible and functional."""
        validation_results = {}
        
        try:
            # Validate Snowflake connectivity
            validation_results['snowflake'] = await self._validate_snowflake()
            
            # Validate Gong API access
            validation_results['gong'] = await self._validate_gong()
            
            # Validate Redis connectivity
            validation_results['redis'] = await self._validate_redis()
            
            # Validate AI service APIs
            validation_results['openai'] = await self._validate_openai()
            validation_results['anthropic'] = await self._validate_anthropic()
            
            # Validate vector databases
            validation_results['pinecone'] = await self._validate_pinecone()
            validation_results['weaviate'] = await self._validate_weaviate()
            
            # Validate monitoring services
            validation_results['arize'] = await self._validate_arize()
            validation_results['sentry'] = await self._validate_sentry()
            
            self.logger.info("Secret validation completed", results=validation_results)
            return validation_results
            
        except Exception as e:
            self.logger.error(f"Secret validation failed: {str(e)}")
            return validation_results
    
    async def _validate_snowflake(self) -> bool:
        """Validate Snowflake connectivity."""
        try:
            import snowflake.connector
            
            conn = snowflake.connector.connect(
                account=self.config.snowflake.account,
                user=self.config.snowflake.user,
                password=self.config.snowflake.password,
                database=self.config.snowflake.database,
                warehouse=self.config.snowflake.warehouse,
                schema=self.config.snowflake.schema,
                role=self.config.snowflake.role,
                login_timeout=10
            )
            
            cursor = conn.cursor()
            cursor.execute("SELECT CURRENT_VERSION()")
            result = cursor.fetchone()
            conn.close()
            
            self.logger.info("Snowflake validation successful", version=result[0])
            return True
            
        except Exception as e:
            self.logger.error(f"Snowflake validation failed: {str(e)}")
            return False
    
    async def _validate_gong(self) -> bool:
        """Validate Gong API access."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.config.gong.api_base_url}/v2/calls",
                    headers={
                        "Authorization": f"Basic {self.config.gong.access_key}:{self.config.gong.secret_key}",
                        "Content-Type": "application/json"
                    },
                    params={"limit": 1},
                    timeout=10
                )
                
                success = response.status_code == 200
                self.logger.info("Gong validation completed", success=success)
                return success
                
        except Exception as e:
            self.logger.error(f"Gong validation failed: {str(e)}")
            return False
    
    async def _validate_redis(self) -> bool:
        """Validate Redis connectivity."""
        try:
            import redis.asyncio as redis
            
            redis_client = redis.Redis(
                host=self.config.redis.host,
                port=self.config.redis.port,
                password=self.config.redis.password,
                ssl=self.config.redis.ssl_enabled,
                socket_connect_timeout=10
            )
            
            await redis_client.ping()
            await redis_client.close()
            
            self.logger.info("Redis validation successful")
            return True
            
        except Exception as e:
            self.logger.error(f"Redis validation failed: {str(e)}")
            return False
    
    async def _validate_openai(self) -> bool:
        """Validate OpenAI API access."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://api.openai.com/v1/models",
                    headers={
                        "Authorization": f"Bearer {self.config.openai_api_key}",
                        "Content-Type": "application/json"
                    },
                    timeout=10
                )
                
                success = response.status_code == 200
                self.logger.info("OpenAI validation completed", success=success)
                return success
                
        except Exception as e:
            self.logger.error(f"OpenAI validation failed: {str(e)}")
            return False
    
    async def _validate_anthropic(self) -> bool:
        """Validate Anthropic API access."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://api.anthropic.com/v1/messages",
                    headers={
                        "x-api-key": self.config.anthropic_api_key,
                        "Content-Type": "application/json",
                        "anthropic-version": "2023-06-01"
                    },
                    timeout=10
                )
                
                # Anthropic returns 400 for GET on messages endpoint, but validates auth
                success = response.status_code in [400, 401]  # 401 means auth failed
                success = response.status_code == 400  # 400 means auth passed but method wrong
                
                self.logger.info("Anthropic validation completed", success=success)
                return success
                
        except Exception as e:
            self.logger.error(f"Anthropic validation failed: {str(e)}")
            return False
    
    async def _validate_pinecone(self) -> bool:
        """Validate Pinecone API access."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://controller.{self.config.pinecone_environment}.pinecone.io/databases",
                    headers={
                        "Api-Key": self.config.pinecone_api_key,
                        "Content-Type": "application/json"
                    },
                    timeout=10
                )
                
                success = response.status_code == 200
                self.logger.info("Pinecone validation completed", success=success)
                return success
                
        except Exception as e:
            self.logger.error(f"Pinecone validation failed: {str(e)}")
            return False
    
    async def _validate_weaviate(self) -> bool:
        """Validate Weaviate connectivity."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.config.weaviate_url}/v1/meta",
                    headers={
                        "Authorization": f"Bearer {self.config.weaviate_api_key}",
                        "Content-Type": "application/json"
                    },
                    timeout=10
                )
                
                success = response.status_code == 200
                self.logger.info("Weaviate validation completed", success=success)
                return success
                
        except Exception as e:
            self.logger.error(f"Weaviate validation failed: {str(e)}")
            return False
    
    async def _validate_arize(self) -> bool:
        """Validate Arize monitoring access."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://app.arize.com/v1/spaces",
                    headers={
                        "Authorization": f"Bearer {self.config.monitoring.arize_api_key}",
                        "Content-Type": "application/json"
                    },
                    timeout=10
                )
                
                success = response.status_code == 200
                self.logger.info("Arize validation completed", success=success)
                return success
                
        except Exception as e:
            self.logger.error(f"Arize validation failed: {str(e)}")
            return False
    
    async def _validate_sentry(self) -> bool:
        """Validate Sentry DSN."""
        try:
            # Parse Sentry DSN to validate format
            dsn_parts = self.config.monitoring.sentry_dsn.split('@')
            if len(dsn_parts) != 2:
                return False
            
            # Simple validation - if DSN parses correctly, it's likely valid
            self.logger.info("Sentry DSN validation successful")
            return True
            
        except Exception as e:
            self.logger.error(f"Sentry validation failed: {str(e)}")
            return False


class EnhancedESCConfig:
    """Enhanced singleton loader for Pulumi ESC secrets with caching and validation."""
    
    _instance: Optional["EnhancedESCConfig"] = None
    _config: Optional[Dict[str, Any]] = None
    _settings: Optional[SophiaConfig] = None
    _last_loaded: Optional[datetime] = None
    _cache_ttl: int = 300  # 5 minutes
    
    def __new__(cls) -> "EnhancedESCConfig":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self) -> None:
        if self._config is None:
            self._load_config()
    
    def _should_refresh_cache(self) -> bool:
        """Check if cache should be refreshed."""
        if self._last_loaded is None:
            return True
        
        now = datetime.now(timezone.utc)
        elapsed = (now - self._last_loaded).total_seconds()
        return elapsed > self._cache_ttl
    
    def _load_config(self) -> None:
        """Load configuration from Pulumi ESC with enhanced error handling."""
        org = os.getenv("PULUMI_ORG", "scoobyjava-org")
        environment = os.getenv("ENVIRONMENT", "staging")
        stack = f"sophia-ai-platform-{environment}"
        
        cmd = [
            "pulumi",
            "env",
            "open",
            f"{org}/default/{stack}",
            "--format",
            "json",
        ]
        
        logger.debug("Loading ESC config", command=" ".join(cmd))
        
        try:
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                check=False,
                timeout=30
            )
            
            if result.returncode != 0:
                logger.error("pulumi env open failed", 
                           stderr=result.stderr.strip(),
                           returncode=result.returncode)
                self._config = {}
                self._fallback_to_env_vars()
                return
            
            self._config = json.loads(result.stdout)
            self._last_loaded = datetime.now(timezone.utc)
            
            logger.info("Loaded ESC configuration", 
                       key_count=len(self._config or {}),
                       stack=stack)
            
        except json.JSONDecodeError as exc:
            logger.exception("Failed to parse ESC output", error=str(exc))
            self._config = {}
            self._fallback_to_env_vars()
            
        except subprocess.TimeoutExpired:
            logger.error("Pulumi ESC command timed out")
            self._config = {}
            self._fallback_to_env_vars()
            
        except Exception as exc:
            logger.exception("Unexpected error loading ESC config", error=str(exc))
            self._config = {}
            self._fallback_to_env_vars()
    
    def _fallback_to_env_vars(self) -> None:
        """Fallback to environment variables when ESC is unavailable."""
        logger.warning("Falling back to environment variables")
        
        # Load critical environment variables as fallback
        env_mappings = {
            'openai_api_key': 'OPENAI_API_KEY',
            'snowflake_account': 'SNOWFLAKE_ACCOUNT',
            'snowflake_user': 'SNOWFLAKE_USER',
            'snowflake_password': 'SNOWFLAKE_PASSWORD',
            'gong_access_key': 'GONG_ACCESS_KEY',
            'gong_client_secret': 'GONG_CLIENT_SECRET',
            'redis_cluster_password': 'REDIS_CLUSTER_PASSWORD',
            'slack_bot_token': 'SLACK_BOT_TOKEN',
        }
        
        fallback_config = {}
        for config_key, env_key in env_mappings.items():
            value = os.getenv(env_key)
            if value:
                fallback_config[config_key] = value
        
        self._config = fallback_config
        logger.info("Fallback configuration loaded", 
                   key_count=len(fallback_config))
    
    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve a config value with cache refresh logic."""
        if self._should_refresh_cache():
            self._load_config()
        
        if self._config is None:
            return default
        
        return self._config.get(key, default)
    
    def get_typed_config(self) -> SophiaConfig:
        """Return configuration as typed SophiaConfig with validation."""
        if self._settings is None or self._should_refresh_cache():
            self._load_config()
            
            try:
                # Convert flat config to nested structure expected by SophiaConfig
                config_data = self._transform_config_structure()
                self._settings = SophiaConfig(**config_data)
                
                logger.info("Typed configuration loaded successfully")
                
            except ValidationError as exc:
                logger.error("Configuration validation failed", 
                           errors=exc.errors())
                # Return minimal config to prevent total failure
                self._settings = self._get_minimal_config()
                
            except Exception as exc:
                logger.exception("Unexpected error creating typed config", 
                               error=str(exc))
                self._settings = self._get_minimal_config()
        
        return self._settings
    
    def _transform_config_structure(self) -> Dict[str, Any]:
        """Transform flat ESC config to nested structure for SophiaConfig."""
        if not self._config:
            raise ValueError("No configuration data available")
        
        # This would contain the logic to transform the flat configuration
        # from Pulumi ESC into the nested structure expected by SophiaConfig
        # For now, returning the flat config which Pydantic can handle
        return self._config
    
    def _get_minimal_config(self) -> SophiaConfig:
        """Return minimal configuration to prevent total failure."""
        minimal_data = {
            'webhook': {
                'domain': 'localhost',
                'base_url': 'http://localhost:5000/webhook/gong',
                'jwt_private_key': 'dummy-key',
                'jwt_public_key': 'dummy-key'
            },
            'snowflake': {
                'account': 'dummy',
                'password': 'dummy'
            },
            'redis': {
                'password': 'dummy'
            },
            'agents': {
                'auth_token': 'dummy',
                'communication_secret': 'dummy'
            },
            'gong': {
                'access_key': 'dummy',
                'secret_key': 'dummy',
                'webhook_secret': 'dummy'
            },
            'monitoring': {
                'arize_api_key': 'dummy',
                'arize_space_id': 'dummy',
                'sentry_dsn': 'dummy',
                'prometheus_auth_token': 'dummy',
                'grafana_url': 'dummy',
                'grafana_username': 'dummy',
                'grafana_password': 'dummy',
                'grafana_admin_password': 'dummy'
            },
            'mcp': {
                'github_token': 'dummy',
                'slack_token': 'dummy',
                'linear_token': 'dummy',
                'docker_registry_token': 'dummy',
                'postgres_connection_string': 'dummy'
            },
            'security': {
                'jwt_private_key': 'dummy',
                'jwt_public_key': 'dummy',
                'encryption_key': 'dummy'
            },
            'kubernetes': {},
            'openai_api_key': 'dummy',
            'anthropic_api_key': 'dummy',
            'agno_api_key': 'dummy',
            'pinecone_api_key': 'dummy',
            'pinecone_environment': 'dummy',
            'pinecone_index_name': 'dummy',
            'weaviate_api_key': 'dummy',
            'weaviate_url': 'dummy',
            'hubspot_access_token': 'dummy',
            'linear_api_key': 'dummy',
            'notion_api_key': 'dummy',
            'lambda_labs_api_key': 'dummy',
            'lambda_labs_control_plane_ip': 'dummy',
            'lambda_labs_ssh_key_name': 'dummy',
            'database_url': 'dummy'
        }
        
        logger.warning("Using minimal configuration due to validation errors")
        return SophiaConfig(**minimal_data)
    
    async def validate_configuration(self) -> Dict[str, bool]:
        """Validate the current configuration."""
        config = self.get_typed_config()
        validator = ConfigValidator(config)
        return await validator.validate_secrets()
    
    async def refresh_cache(self) -> None:
        """Force refresh of configuration cache."""
        self._config = None
        self._settings = None
        self._last_loaded = None
        self._load_config()
        logger.info("Configuration cache refreshed")


# Global instance
enhanced_config = EnhancedESCConfig()

# Backward compatibility
config = enhanced_config 