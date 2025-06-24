"""
Snowflake Configuration Manager for Sophia AI

This module provides a centralized configuration management system that integrates
with the Snowflake CONFIG schema, providing dynamic configuration loading,
feature flag evaluation, and environment-specific settings.

Features:
- Dynamic configuration loading from Snowflake CONFIG schema
- Feature flag evaluation with targeting and rollout support
- Environment-specific configuration management
- Configuration caching with TTL
- Configuration validation and type conversion
- Integration with Pulumi ESC for sensitive settings
"""

from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union, Type, TypeVar
from dataclasses import dataclass, field
from enum import Enum
import hashlib
from functools import wraps

import snowflake.connector
from backend.core.auto_esc_config import config as esc_config

logger = logging.getLogger(__name__)

T = TypeVar('T')


class ConfigDataType(Enum):
    """Configuration data types"""
    STRING = "STRING"
    NUMBER = "NUMBER"
    BOOLEAN = "BOOLEAN"
    JSON = "JSON"
    ARRAY = "ARRAY"


class FeatureFlagType(Enum):
    """Feature flag types"""
    BOOLEAN = "BOOLEAN"
    PERCENTAGE = "PERCENTAGE"
    WHITELIST = "WHITELIST"
    EXPERIMENT = "EXPERIMENT"


@dataclass
class ConfigValue:
    """Configuration value with metadata"""
    name: str
    value: Any
    data_type: ConfigDataType
    environment: str
    application_name: str
    service_name: Optional[str] = None
    component_name: Optional[str] = None
    description: Optional[str] = None
    is_sensitive: bool = False
    version: int = 1
    updated_at: Optional[datetime] = None
    
    def get_typed_value(self, target_type: Type[T] = None) -> T:
        """Get the value converted to the specified type"""
        if target_type is None:
            return self.value
        
        try:
            if self.data_type == ConfigDataType.NUMBER:
                if target_type == int:
                    return int(float(self.value))
                elif target_type == float:
                    return float(self.value)
            elif self.data_type == ConfigDataType.BOOLEAN:
                if target_type == bool:
                    return str(self.value).lower() in ('true', '1', 'yes', 'on')
            elif self.data_type == ConfigDataType.JSON:
                if target_type == dict or target_type == list:
                    return json.loads(self.value) if isinstance(self.value, str) else self.value
            elif self.data_type == ConfigDataType.ARRAY:
                if target_type == list:
                    return json.loads(self.value) if isinstance(self.value, str) else self.value
            
            return target_type(self.value)
        except (ValueError, TypeError, json.JSONDecodeError) as e:
            logger.warning(f"Failed to convert config value {self.name} to {target_type}: {e}")
            return self.value


@dataclass
class FeatureFlag:
    """Feature flag with evaluation logic"""
    name: str
    is_enabled: bool
    flag_type: FeatureFlagType
    environment: str
    application_name: str
    service_name: Optional[str] = None
    rollout_percentage: float = 0.0
    target_users: List[str] = field(default_factory=list)
    target_groups: List[str] = field(default_factory=list)
    target_conditions: Dict[str, Any] = field(default_factory=dict)
    experiment_variants: Dict[str, Any] = field(default_factory=dict)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    
    def evaluate(
        self, 
        user_id: Optional[str] = None, 
        user_properties: Optional[Dict[str, Any]] = None
    ) -> Any:
        """Evaluate the feature flag for a given user"""
        
        # Check if flag is enabled and within date range
        if not self.is_enabled:
            return False
        
        now = datetime.now()
        if self.start_date and now < self.start_date:
            return False
        if self.end_date and now > self.end_date:
            return False
        
        # Evaluate based on flag type
        if self.flag_type == FeatureFlagType.BOOLEAN:
            return self.is_enabled
        
        elif self.flag_type == FeatureFlagType.PERCENTAGE:
            if not user_id:
                return False
            
            # Use hash of user_id for consistent percentage-based rollout
            user_hash = int(hashlib.md5(user_id.encode()).hexdigest(), 16)
            user_percentage = (user_hash % 100) + 1
            return user_percentage <= self.rollout_percentage
        
        elif self.flag_type == FeatureFlagType.WHITELIST:
            if not user_id:
                return False
            
            # Check if user is in target users or groups
            if user_id in self.target_users:
                return True
            
            if user_properties:
                user_groups = user_properties.get('groups', [])
                if any(group in self.target_groups for group in user_groups):
                    return True
            
            return False
        
        elif self.flag_type == FeatureFlagType.EXPERIMENT:
            if not user_id or not self.experiment_variants:
                return False
            
            # Assign user to experiment variant based on hash
            variant_names = list(self.experiment_variants.keys())
            if not variant_names:
                return False
            
            user_hash = int(hashlib.md5(user_id.encode()).hexdigest(), 16)
            variant_index = user_hash % len(variant_names)
            selected_variant = variant_names[variant_index]
            
            return self.experiment_variants[selected_variant]
        
        return False


@dataclass
class ConfigCache:
    """Configuration cache with TTL"""
    data: Dict[str, Any]
    cached_at: datetime
    ttl_seconds: int = 300  # 5 minutes default
    
    @property
    def is_expired(self) -> bool:
        """Check if cache has expired"""
        return datetime.now() > self.cached_at + timedelta(seconds=self.ttl_seconds)


class SnowflakeConfigManager:
    """
    Snowflake-based configuration manager for Sophia AI
    
    Provides centralized configuration management with support for:
    - Dynamic configuration loading from Snowflake CONFIG schema
    - Feature flag evaluation with advanced targeting
    - Environment-specific settings
    - Configuration caching and validation
    """
    
    def __init__(
        self, 
        environment: str = "DEV",
        application_name: str = "SOPHIA_AI",
        cache_ttl: int = 300
    ):
        self.environment = environment
        self.application_name = application_name
        self.cache_ttl = cache_ttl
        
        # Connection details
        self.connection = None
        self.database = esc_config.get("snowflake_database", "SOPHIA_AI_DEV")
        self.warehouse = esc_config.get("snowflake_warehouse", "WH_SOPHIA_AGENT_QUERY")
        
        # Caches
        self._config_cache: Optional[ConfigCache] = None
        self._feature_flag_cache: Optional[ConfigCache] = None
        
        self.initialized = False
    
    async def initialize(self) -> None:
        """Initialize the configuration manager"""
        if self.initialized:
            return
        
        try:
            self.connection = snowflake.connector.connect(
                user=esc_config.get("snowflake_user"),
                password=esc_config.get("snowflake_password"),
                account=esc_config.get("snowflake_account"),
                warehouse=self.warehouse,
                database=self.database,
                schema="CONFIG",
                role=esc_config.get("snowflake_role", "ROLE_SOPHIA_AI_AGENT_SERVICE")
            )
            
            self.initialized = True
            logger.info("✅ Snowflake Configuration Manager initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize Snowflake Configuration Manager: {e}")
            raise
    
    async def close(self) -> None:
        """Close the configuration manager"""
        if self.connection:
            self.connection.close()
            self.initialized = False
            logger.info("Snowflake Configuration Manager closed")
    
    async def get_config_value(
        self,
        setting_name: str,
        service_name: Optional[str] = None,
        component_name: Optional[str] = None,
        default_value: Any = None,
        target_type: Type[T] = None
    ) -> T:
        """
        Get a configuration value with type conversion and fallback
        
        Args:
            setting_name: Name of the setting
            service_name: Optional service name for service-specific settings
            component_name: Optional component name for component-specific settings
            default_value: Default value if setting not found
            target_type: Target type for conversion
            
        Returns:
            Configuration value converted to target type
        """
        if not self.initialized:
            await self.initialize()
        
        try:
            # Check cache first
            if self._config_cache and not self._config_cache.is_expired:
                cache_key = f"{setting_name}_{service_name}_{component_name}"
                if cache_key in self._config_cache.data:
                    config_value = self._config_cache.data[cache_key]
                    return config_value.get_typed_value(target_type)
            
            # Query from database
            query = """
            SELECT 
                SETTING_NAME,
                SETTING_VALUE,
                DATA_TYPE,
                DESCRIPTION,
                IS_SENSITIVE,
                VERSION,
                UPDATED_AT,
                SERVICE_NAME,
                COMPONENT_NAME
            FROM APPLICATION_SETTINGS
            WHERE SETTING_NAME = %s
            AND ENVIRONMENT = %s
            AND APPLICATION_NAME = %s
            AND (SERVICE_NAME = %s OR (SERVICE_NAME IS NULL AND %s IS NULL))
            AND (COMPONENT_NAME = %s OR (COMPONENT_NAME IS NULL AND %s IS NULL))
            AND IS_ACTIVE = TRUE
            ORDER BY 
                CASE WHEN SERVICE_NAME IS NOT NULL THEN 1 ELSE 2 END,
                CASE WHEN COMPONENT_NAME IS NOT NULL THEN 1 ELSE 2 END,
                VERSION DESC
            LIMIT 1
            """
            
            cursor = self.connection.cursor()
            cursor.execute(query, (
                setting_name, self.environment, self.application_name,
                service_name, service_name,
                component_name, component_name
            ))
            
            result = cursor.fetchone()
            cursor.close()
            
            if result:
                config_value = ConfigValue(
                    name=result[0],
                    value=result[1],
                    data_type=ConfigDataType(result[2]),
                    environment=self.environment,
                    application_name=self.application_name,
                    service_name=result[7],
                    component_name=result[8],
                    description=result[3],
                    is_sensitive=result[4],
                    version=result[5],
                    updated_at=result[6]
                )
                
                # Update cache
                self._update_config_cache(
                    f"{setting_name}_{service_name}_{component_name}",
                    config_value
                )
                
                return config_value.get_typed_value(target_type)
            
            else:
                logger.warning(f"Configuration setting not found: {setting_name}")
                return default_value if target_type is None else target_type(default_value) if default_value is not None else None
                
        except Exception as e:
            logger.error(f"Error getting configuration value {setting_name}: {e}")
            return default_value if target_type is None else target_type(default_value) if default_value is not None else None
    
    async def evaluate_feature_flag(
        self,
        flag_name: str,
        user_id: Optional[str] = None,
        service_name: Optional[str] = None,
        user_properties: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Evaluate a feature flag for the given user and context
        
        Args:
            flag_name: Name of the feature flag
            user_id: User ID for percentage-based and whitelist flags
            service_name: Optional service name for service-specific flags
            user_properties: Additional user properties for targeting
            
        Returns:
            Feature flag evaluation result
        """
        if not self.initialized:
            await self.initialize()
        
        try:
            # Check cache first
            if self._feature_flag_cache and not self._feature_flag_cache.is_expired:
                cache_key = f"{flag_name}_{service_name}"
                if cache_key in self._feature_flag_cache.data:
                    feature_flag = self._feature_flag_cache.data[cache_key]
                    result = feature_flag.evaluate(user_id, user_properties)
                    
                    # Log evaluation for analytics
                    await self._log_feature_flag_evaluation(
                        feature_flag, user_id, user_properties, result
                    )
                    
                    return result
            
            # Query from database
            query = """
            SELECT 
                FLAG_NAME,
                IS_ENABLED,
                FLAG_TYPE,
                ROLLOUT_PERCENTAGE,
                TARGET_USERS,
                TARGET_GROUPS,
                TARGET_CONDITIONS,
                EXPERIMENT_VARIANTS,
                START_DATE,
                END_DATE
            FROM FEATURE_FLAGS
            WHERE FLAG_NAME = %s
            AND ENVIRONMENT = %s
            AND APPLICATION_NAME = %s
            AND (SERVICE_NAME = %s OR (SERVICE_NAME IS NULL AND %s IS NULL))
            ORDER BY 
                CASE WHEN SERVICE_NAME IS NOT NULL THEN 1 ELSE 2 END
            LIMIT 1
            """
            
            cursor = self.connection.cursor()
            cursor.execute(query, (
                flag_name, self.environment, self.application_name,
                service_name, service_name
            ))
            
            result = cursor.fetchone()
            cursor.close()
            
            if result:
                feature_flag = FeatureFlag(
                    name=result[0],
                    is_enabled=result[1],
                    flag_type=FeatureFlagType(result[2]),
                    environment=self.environment,
                    application_name=self.application_name,
                    service_name=service_name,
                    rollout_percentage=result[3] or 0.0,
                    target_users=json.loads(result[4]) if result[4] else [],
                    target_groups=json.loads(result[5]) if result[5] else [],
                    target_conditions=json.loads(result[6]) if result[6] else {},
                    experiment_variants=json.loads(result[7]) if result[7] else {},
                    start_date=result[8],
                    end_date=result[9]
                )
                
                # Update cache
                self._update_feature_flag_cache(
                    f"{flag_name}_{service_name}",
                    feature_flag
                )
                
                evaluation_result = feature_flag.evaluate(user_id, user_properties)
                
                # Log evaluation
                await self._log_feature_flag_evaluation(
                    feature_flag, user_id, user_properties, evaluation_result
                )
                
                return evaluation_result
            
            else:
                logger.warning(f"Feature flag not found: {flag_name}")
                return False
                
        except Exception as e:
            logger.error(f"Error evaluating feature flag {flag_name}: {e}")
            return False
    
    async def update_config_setting(
        self,
        setting_name: str,
        new_value: Any,
        service_name: Optional[str] = None,
        component_name: Optional[str] = None,
        changed_by: str = "SYSTEM",
        change_reason: Optional[str] = None
    ) -> bool:
        """
        Update a configuration setting
        
        Args:
            setting_name: Name of the setting to update
            new_value: New value for the setting
            service_name: Optional service name
            component_name: Optional component name
            changed_by: User or system making the change
            change_reason: Reason for the change
            
        Returns:
            True if update was successful
        """
        if not self.initialized:
            await self.initialize()
        
        try:
            # Call stored procedure
            query = """
            CALL UPDATE_CONFIG_SETTING(
                %s, %s, %s, %s, %s, %s, %s, %s
            )
            """
            
            cursor = self.connection.cursor()
            cursor.execute(query, (
                setting_name, str(new_value), self.environment, self.application_name,
                service_name, component_name, changed_by, change_reason
            ))
            
            result = cursor.fetchone()
            cursor.close()
            
            # Invalidate cache
            self._invalidate_config_cache()
            
            logger.info(f"Updated configuration setting {setting_name}: {result[0] if result else 'Success'}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating configuration setting {setting_name}: {e}")
            return False
    
    async def get_all_config_values(
        self,
        category: Optional[str] = None,
        service_name: Optional[str] = None
    ) -> Dict[str, ConfigValue]:
        """
        Get all configuration values for the application
        
        Args:
            category: Optional category filter
            service_name: Optional service name filter
            
        Returns:
            Dictionary of configuration values
        """
        if not self.initialized:
            await self.initialize()
        
        try:
            query = """
            SELECT 
                SETTING_NAME,
                SETTING_VALUE,
                DATA_TYPE,
                DESCRIPTION,
                CATEGORY,
                IS_SENSITIVE,
                VERSION,
                UPDATED_AT,
                SERVICE_NAME,
                COMPONENT_NAME
            FROM APPLICATION_SETTINGS
            WHERE ENVIRONMENT = %s
            AND APPLICATION_NAME = %s
            AND IS_ACTIVE = TRUE
            """
            
            params = [self.environment, self.application_name]
            
            if category:
                query += " AND CATEGORY = %s"
                params.append(category)
            
            if service_name:
                query += " AND (SERVICE_NAME = %s OR SERVICE_NAME IS NULL)"
                params.append(service_name)
            
            query += " ORDER BY CATEGORY, SETTING_NAME"
            
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            
            results = cursor.fetchall()
            cursor.close()
            
            config_values = {}
            for result in results:
                config_value = ConfigValue(
                    name=result[0],
                    value=result[1],
                    data_type=ConfigDataType(result[2]),
                    environment=self.environment,
                    application_name=self.application_name,
                    service_name=result[8],
                    component_name=result[9],
                    description=result[3],
                    is_sensitive=result[5],
                    version=result[6],
                    updated_at=result[7]
                )
                config_values[result[0]] = config_value
            
            return config_values
            
        except Exception as e:
            logger.error(f"Error getting all configuration values: {e}")
            return {}
    
    async def get_system_health(self) -> Dict[str, Any]:
        """Get system health information including configuration status"""
        if not self.initialized:
            await self.initialize()
        
        try:
            # Check configuration health
            config_health_query = """
            SELECT 
                COUNT(*) as total_settings,
                COUNT(CASE WHEN SETTING_VALUE IS NOT NULL THEN 1 END) as valid_settings,
                COUNT(CASE WHEN IS_SENSITIVE = TRUE THEN 1 END) as sensitive_settings,
                MAX(UPDATED_AT) as last_update
            FROM APPLICATION_SETTINGS
            WHERE ENVIRONMENT = %s
            AND APPLICATION_NAME = %s
            AND IS_ACTIVE = TRUE
            """
            
            # Check feature flag health
            flag_health_query = """
            SELECT 
                COUNT(*) as total_flags,
                COUNT(CASE WHEN IS_ENABLED = TRUE THEN 1 END) as enabled_flags,
                COUNT(CASE WHEN START_DATE <= CURRENT_TIMESTAMP() AND 
                              (END_DATE IS NULL OR END_DATE > CURRENT_TIMESTAMP()) THEN 1 END) as active_flags
            FROM FEATURE_FLAGS
            WHERE ENVIRONMENT = %s
            AND APPLICATION_NAME = %s
            """
            
            cursor = self.connection.cursor()
            
            # Get configuration health
            cursor.execute(config_health_query, (self.environment, self.application_name))
            config_result = cursor.fetchone()
            
            # Get feature flag health
            cursor.execute(flag_health_query, (self.environment, self.application_name))
            flag_result = cursor.fetchone()
            
            cursor.close()
            
            return {
                "status": "healthy",
                "environment": self.environment,
                "application": self.application_name,
                "configuration": {
                    "total_settings": config_result[0],
                    "valid_settings": config_result[1],
                    "sensitive_settings": config_result[2],
                    "last_update": config_result[3],
                    "health_score": (config_result[1] / config_result[0]) * 100 if config_result[0] > 0 else 0
                },
                "feature_flags": {
                    "total_flags": flag_result[0],
                    "enabled_flags": flag_result[1],
                    "active_flags": flag_result[2],
                    "health_score": (flag_result[2] / flag_result[0]) * 100 if flag_result[0] > 0 else 0
                },
                "cache": {
                    "config_cached": self._config_cache is not None and not self._config_cache.is_expired,
                    "flags_cached": self._feature_flag_cache is not None and not self._feature_flag_cache.is_expired
                },
                "checked_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting system health: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "checked_at": datetime.now().isoformat()
            }
    
    def _update_config_cache(self, key: str, config_value: ConfigValue) -> None:
        """Update configuration cache"""
        if not self._config_cache or self._config_cache.is_expired:
            self._config_cache = ConfigCache(
                data={key: config_value},
                cached_at=datetime.now(),
                ttl_seconds=self.cache_ttl
            )
        else:
            self._config_cache.data[key] = config_value
    
    def _update_feature_flag_cache(self, key: str, feature_flag: FeatureFlag) -> None:
        """Update feature flag cache"""
        if not self._feature_flag_cache or self._feature_flag_cache.is_expired:
            self._feature_flag_cache = ConfigCache(
                data={key: feature_flag},
                cached_at=datetime.now(),
                ttl_seconds=self.cache_ttl
            )
        else:
            self._feature_flag_cache.data[key] = feature_flag
    
    def _invalidate_config_cache(self) -> None:
        """Invalidate configuration cache"""
        self._config_cache = None
    
    def _invalidate_feature_flag_cache(self) -> None:
        """Invalidate feature flag cache"""
        self._feature_flag_cache = None
    
    async def _log_feature_flag_evaluation(
        self,
        feature_flag: FeatureFlag,
        user_id: Optional[str],
        user_properties: Optional[Dict[str, Any]],
        result: Any
    ) -> None:
        """Log feature flag evaluation for analytics"""
        try:
            # This would typically be done asynchronously to avoid impacting performance
            # For now, we'll just log it
            logger.debug(
                f"Feature flag evaluation: {feature_flag.name} = {result} "
                f"(user: {user_id}, type: {feature_flag.flag_type.value})"
            )
        except Exception as e:
            logger.warning(f"Failed to log feature flag evaluation: {e}")


# Convenience functions for common use cases
_config_manager: Optional[SnowflakeConfigManager] = None


async def get_config_manager() -> SnowflakeConfigManager:
    """Get the global configuration manager instance"""
    global _config_manager
    if _config_manager is None:
        _config_manager = SnowflakeConfigManager()
        await _config_manager.initialize()
    return _config_manager


async def get_config(
    setting_name: str,
    default_value: Any = None,
    target_type: Type[T] = None,
    service_name: Optional[str] = None
) -> T:
    """Get a configuration value (convenience function)"""
    manager = await get_config_manager()
    return await manager.get_config_value(
        setting_name, service_name=service_name, 
        default_value=default_value, target_type=target_type
    )


async def is_feature_enabled(
    flag_name: str,
    user_id: Optional[str] = None,
    service_name: Optional[str] = None,
    user_properties: Optional[Dict[str, Any]] = None
) -> bool:
    """Check if a feature flag is enabled (convenience function)"""
    manager = await get_config_manager()
    result = await manager.evaluate_feature_flag(
        flag_name, user_id=user_id, service_name=service_name, 
        user_properties=user_properties
    )
    return bool(result)


def config_cached(ttl: int = 300):
    """Decorator to cache function results based on configuration"""
    def decorator(func):
        cache = {}
        
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Create cache key from function arguments
            cache_key = f"{func.__name__}_{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # Check cache
            if cache_key in cache:
                cached_result, cached_at = cache[cache_key]
                if datetime.now() - cached_at < timedelta(seconds=ttl):
                    return cached_result
            
            # Call function and cache result
            result = await func(*args, **kwargs)
            cache[cache_key] = (result, datetime.now())
            
            return result
        
        return wrapper
    return decorator


# Example usage and integration patterns
async def example_usage():
    """Example usage of the Snowflake Configuration Manager"""
    
    # Initialize configuration manager
    config_manager = SnowflakeConfigManager(
        environment="DEV",
        application_name="SOPHIA_AI"
    )
    await config_manager.initialize()
    
    try:
        # Get configuration values
        db_pool_size = await config_manager.get_config_value(
            "database.connection_pool_size", 
            default_value=10, 
            target_type=int
        )
        
        similarity_threshold = await config_manager.get_config_value(
            "ai_memory.similarity_threshold",
            default_value=0.7,
            target_type=float
        )
        
        # Evaluate feature flags
        enhanced_memory_enabled = await config_manager.evaluate_feature_flag(
            "enhanced_ai_memory",
            user_id="user_123"
        )
        
        experimental_features = await config_manager.evaluate_feature_flag(
            "experimental_langgraph",
            user_id="user_123",
            user_properties={"role": "developer", "groups": ["beta_testers"]}
        )
        
        # Get all configuration for a service
        ai_memory_config = await config_manager.get_all_config_values(
            category="AI_MEMORY",
            service_name="AI_MEMORY_MCP"
        )
        
        # Update configuration
        success = await config_manager.update_config_setting(
            "api.rate_limit_per_minute",
            2000,
            changed_by="admin",
            change_reason="Increased for load testing"
        )
        
        # Check system health
        health = await config_manager.get_system_health()
        
        print(f"DB Pool Size: {db_pool_size}")
        print(f"Similarity Threshold: {similarity_threshold}")
        print(f"Enhanced Memory Enabled: {enhanced_memory_enabled}")
        print(f"Experimental Features: {experimental_features}")
        print(f"AI Memory Config: {len(ai_memory_config)} settings")
        print(f"Update Success: {success}")
        print(f"System Health: {health['status']}")
        
    finally:
        await config_manager.close()


if __name__ == "__main__":
    # Run example
    asyncio.run(example_usage()) 