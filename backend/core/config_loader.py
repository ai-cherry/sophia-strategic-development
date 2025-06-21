"""Configuration Loader with Validation and Hot-Reload
Centralized configuration management for Sophia AI Platform
"""

import asyncio
import hashlib
import json
import logging
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from pydantic import BaseModel, Field, validator
from watchdog.events import FileModifiedEvent, FileSystemEventHandler
from watchdog.observers import Observer

logger = logging.getLogger(__name__)


class ServiceTarget(BaseModel):
    """Performance and cost targets for a service"""

    response_time_ms: Optional[int] = None
    uptime_percentage: Optional[float] = None
    query_time_ms: Optional[int] = None
    cache_hit_rate: Optional[float] = None
    monthly_budget_usd: Optional[float] = None
    cost_per_request: Optional[float] = None
    cost_per_prediction: Optional[float] = None

    @validator("uptime_percentage", "cache_hit_rate")
    def validate_percentage(cls, v):
        if v is not None and not 0 <= v <= 100:
            raise ValueError("Percentage must be between 0 and 100")
        return v


class ServiceConfig(BaseModel):
    """Configuration for a single service"""

    optimization_level: str = Field(..., regex="^(standard|moderate|aggressive)$")
    performance_targets: Optional[ServiceTarget] = None
    cost_targets: Optional[ServiceTarget] = None
    features: Optional[List[str]] = None
    enabled: bool = True

    class Config:
        extra = "allow"  # Allow additional fields


class GlobalSettings(BaseModel):
    """Global optimization settings"""

    cost_optimization: Dict[str, Any]
    performance_optimization: Dict[str, Any]
    caching_strategy: Dict[str, Any]
    monitoring: Dict[str, Any]


class ConfigurationSchema(BaseModel):
    """Complete configuration schema"""

    ai_services: Dict[str, ServiceConfig]
    data_services: Dict[str, ServiceConfig]
    infrastructure_services: Dict[str, ServiceConfig]
    business_services: Dict[str, ServiceConfig]
    global_settings: GlobalSettings
    routing_rules: Dict[str, List[Dict[str, Any]]]
    feature_flags: Dict[str, bool]
    version: str
    last_updated: str


class ConfigFileHandler(FileSystemEventHandler):
    """Handle configuration file changes for hot-reload"""

    def __init__(self, config_loader: "ConfigurationLoader"):
        self.config_loader = config_loader

    def on_modified(self, event):
        if isinstance(event, FileModifiedEvent) and event.src_path.endswith(".yaml"):
            logger.info(f"Configuration file modified: {event.src_path}")
            asyncio.create_task(self.config_loader.reload_config())


class ConfigurationLoader:
    """Centralized configuration loader with validation and hot-reload"""

    def __init__(self, config_dir: str = "config/services"):
        self.config_dir = Path(config_dir)
        self.config_cache: Dict[str, Any] = {}
        self.config_hash: Dict[str, str] = {}
        self.observer = Observer()
        self.callbacks: List[callable] = []
        self._lock = asyncio.Lock()

    async def initialize(self):
        """Initialize configuration loader"""
        await self.load_all_configs()
        self._start_file_watcher()

    def _start_file_watcher(self):
        """Start watching configuration files for changes"""
        event_handler = ConfigFileHandler(self)
        self.observer.schedule(event_handler, str(self.config_dir), recursive=True)
        self.observer.start()
        logger.info(f"Started configuration file watcher for {self.config_dir}")

    async def load_all_configs(self):
        """Load all configuration files"""
        async with self._lock:
            for config_file in self.config_dir.glob("*.yaml"):
                await self._load_config_file(config_file)

    async def _load_config_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Load and validate a single configuration file"""
        try:
            # Calculate file hash
            with open(file_path, "rb") as f:
                file_hash = hashlib.md5(f.read()).hexdigest()

            # Check if file has changed
            if self.config_hash.get(str(file_path)) == file_hash:
                logger.debug(f"Configuration file unchanged: {file_path}")
                return self.config_cache.get(file_path.stem)

            # Load YAML content
            with open(file_path, "r") as f:
                config_data = yaml.safe_load(f)

            # Validate configuration
            if file_path.stem == "optimization":
                validated_config = ConfigurationSchema(**config_data)
                config_data = validated_config.dict()

            # Update cache
            self.config_cache[file_path.stem] = config_data
            self.config_hash[str(file_path)] = file_hash

            logger.info(f"Loaded configuration: {file_path.stem}")
            return config_data

        except Exception as e:
            logger.error(f"Failed to load configuration {file_path}: {e}")
            return None

    async def reload_config(self):
        """Reload all configurations and notify callbacks"""
        logger.info("Reloading configurations...")
        await self.load_all_configs()

        # Notify all registered callbacks
        for callback in self.callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(self.config_cache)
                else:
                    callback(self.config_cache)
            except Exception as e:
                logger.error(f"Error in configuration reload callback: {e}")

    def register_reload_callback(self, callback: callable):
        """Register a callback to be called on configuration reload"""
        self.callbacks.append(callback)
        logger.info(f"Registered configuration reload callback: {callback.__name__}")

    @lru_cache(maxsize=128)
    def get_service_config(
        self, service_type: str, service_name: str
    ) -> Optional[ServiceConfig]:
        """Get configuration for a specific service"""
        optimization_config = self.config_cache.get("optimization", {})
        service_group = optimization_config.get(f"{service_type}_services", {})
        service_data = service_group.get(service_name)

        if service_data:
            return ServiceConfig(**service_data)
        return None

    def get_global_settings(self) -> Optional[GlobalSettings]:
        """Get global optimization settings"""
        optimization_config = self.config_cache.get("optimization", {})
        global_data = optimization_config.get("global_settings")

        if global_data:
            return GlobalSettings(**global_data)
        return None

    def get_feature_flag(self, flag_name: str, default: bool = False) -> bool:
        """Get feature flag value"""
        optimization_config = self.config_cache.get("optimization", {})
        feature_flags = optimization_config.get("feature_flags", {})
        return feature_flags.get(flag_name, default)

    def get_routing_rules(self, rule_type: str) -> List[Dict[str, Any]]:
        """Get routing rules for a specific type"""
        optimization_config = self.config_cache.get("optimization", {})
        routing_rules = optimization_config.get("routing_rules", {})
        return routing_rules.get(rule_type, [])

    def evaluate_routing_rule(
        self, rule_type: str, context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Evaluate routing rules and return the first matching rule"""
        rules = self.get_routing_rules(rule_type)

        for rule in rules:
            condition = rule.get("condition", "")
            try:
                # Simple condition evaluation (can be enhanced)
                if self._evaluate_condition(condition, context):
                    return rule
            except Exception as e:
                logger.error(f"Error evaluating routing rule: {e}")

        return None

    def _evaluate_condition(self, condition: str, context: Dict[str, Any]) -> bool:
        """Evaluate a simple condition string"""
        # This is a simplified implementation
        # In production, use a proper expression evaluator
        try:
            # Replace context variables in condition
            for key, value in context.items():
                condition = condition.replace(key, str(value))

            # Evaluate the condition
            return eval(condition)
        except:
            return False

    def get_service_budget(
        self, service_type: str, service_name: str
    ) -> Optional[float]:
        """Get monthly budget for a service"""
        service_config = self.get_service_config(service_type, service_name)
        if service_config and service_config.cost_targets:
            return service_config.cost_targets.monthly_budget_usd
        return None

    def get_total_budget(self) -> float:
        """Get total monthly budget across all services"""
        global_settings = self.get_global_settings()
        if global_settings:
            return global_settings.cost_optimization.get("total_monthly_budget_usd", 0)
        return 0

    def export_config(self, format: str = "json") -> str:
        """Export current configuration in specified format"""
        if format == "json":
            return json.dumps(self.config_cache, indent=2, default=str)
        elif format == "yaml":
            return yaml.dump(self.config_cache, default_flow_style=False)
        else:
            raise ValueError(f"Unsupported export format: {format}")

    def validate_all_configs(self) -> Dict[str, List[str]]:
        """Validate all loaded configurations and return errors"""
        errors = {}

        for config_name, config_data in self.config_cache.items():
            config_errors = []

            # Validate optimization config
            if config_name == "optimization":
                try:
                    ConfigurationSchema(**config_data)
                except Exception as e:
                    config_errors.append(str(e))

            if config_errors:
                errors[config_name] = config_errors

        return errors

    def __del__(self):
        """Cleanup file watcher on deletion"""
        if hasattr(self, "observer") and self.observer.is_alive():
            self.observer.stop()
            self.observer.join()


# Global configuration loader instance
_config_loader: Optional[ConfigurationLoader] = None


async def get_config_loader() -> ConfigurationLoader:
    """Get or create the global configuration loader"""
    global _config_loader

    if _config_loader is None:
        _config_loader = ConfigurationLoader()
        await _config_loader.initialize()

    return _config_loader


# Convenience functions
async def get_service_config(
    service_type: str, service_name: str
) -> Optional[ServiceConfig]:
    """Get configuration for a specific service"""
    loader = await get_config_loader()
    return loader.get_service_config(service_type, service_name)


async def get_feature_flag(flag_name: str, default: bool = False) -> bool:
    """Get feature flag value"""
    loader = await get_config_loader()
    return loader.get_feature_flag(flag_name, default)


async def reload_configs():
    """Manually trigger configuration reload"""
    loader = await get_config_loader()
    await loader.reload_config()
