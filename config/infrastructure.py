"""
Sophia AI Infrastructure Configuration Module

Manages distributed Lambda Labs deployment with comprehensive configuration
for 4 GPU instances, service discovery, and instance-specific settings.

This module provides:
- Centralized instance configuration management
- Service endpoint resolution
- Instance role-based routing
- Health check configuration
- Port management and allocation

Architecture:
- Primary K3s Cluster (GH200 96GB): Main orchestration and database
- MCP Orchestrator (A6000 48GB): AI orchestration and MCP servers
- Data Pipeline (A100 40GB): Data processing and ML training
- Development Instance (A10 24GB): Testing and development

Author: Sophia AI Team
Date: July 2025
"""

import os
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)

class InstanceRole(Enum):
    """Enumeration of instance roles in the distributed architecture."""
    PRIMARY = "primary"
    MCP_ORCHESTRATOR = "mcp_orchestrator"
    DATA_PIPELINE = "data_pipeline"
    DEVELOPMENT = "development"

class ServiceType(Enum):
    """Enumeration of service types across the infrastructure."""
    BACKEND = "backend"
    DATABASE = "database"
    REDIS = "redis"
    K3S = "k3s"
    MCP_SERVERS = "mcp_servers"
    AI_ORCHESTRATION = "ai_orchestration"
    DATA_PROCESSING = "data_processing"
    ML_TRAINING = "ml_training"
    EMBEDDINGS = "embeddings"
    TESTING = "testing"
    DEVELOPMENT = "development"

@dataclass
class PortAllocation:
    """Port allocation configuration for services."""
    start: int
    end: int
    reserved: List[int] = field(default_factory=list)
    
    def get_next_available(self) -> int:
        """Get the next available port in the range."""
        for port in range(self.start, self.end + 1):
            if port not in self.reserved:
                self.reserved.append(port)
                return port
        raise RuntimeError(f"No available ports in range {self.start}-{self.end}")
    
    def is_available(self, port: int) -> bool:
        """Check if a port is available."""
        return self.start <= port <= self.end and port not in self.reserved

@dataclass
class LambdaInstance:
    """Configuration for a Lambda Labs GPU instance."""
    name: str
    ip: str
    gpu: str
    role: InstanceRole
    region: str
    port_allocation: PortAllocation
    services: List[ServiceType]
    max_connections: int = 1000
    timeout_seconds: int = 30
    health_check_path: str = "/health"
    
    @property
    def primary_port(self) -> int:
        """Get the primary port for this instance."""
        return self.port_allocation.start
    
    @property
    def endpoint(self) -> str:
        """Get the primary HTTP endpoint for this instance."""
        return f"http://{self.ip}:{self.primary_port}"
    
    @property
    def health_endpoint(self) -> str:
        """Get the health check endpoint for this instance."""
        return f"{self.endpoint}{self.health_check_path}"
    
    def has_service(self, service: ServiceType) -> bool:
        """Check if this instance provides a specific service."""
        return service in self.services
    
    def get_service_port(self, service: ServiceType) -> Optional[int]:
        """Get the port for a specific service on this instance."""
        if not self.has_service(service):
            return None
        
        # Primary service gets the primary port
        if service == self.services[0]:
            return self.primary_port
        
        # Other services get allocated ports
        service_index = self.services.index(service)
        return self.port_allocation.start + service_index

class InfrastructureConfig:
    """
    Centralized infrastructure configuration for Sophia AI distributed deployment.
    
    This class manages the configuration of all Lambda Labs instances,
    service discovery, and routing logic for the distributed architecture.
    """
    
    # Instance definitions with comprehensive configuration
    INSTANCES: Dict[str, LambdaInstance] = {
        "sophia-ai-core": LambdaInstance(
            name="sophia-ai-core",
            ip="192.222.58.232",
            gpu="GH200 96GB",
            role=InstanceRole.PRIMARY,
            region="us-east-3",
            port_allocation=PortAllocation(start=8000, end=8099),
            services=[
                ServiceType.BACKEND,
                ServiceType.DATABASE,
                ServiceType.REDIS,
                ServiceType.K3S
            ],
            max_connections=2000,
            timeout_seconds=60
        ),
        
        "sophia-mcp-orchestrator": LambdaInstance(
            name="sophia-mcp-orchestrator",
            ip="104.171.202.117",
            gpu="A6000 48GB",
            role=InstanceRole.MCP_ORCHESTRATOR,
            region="us-south-1",
            port_allocation=PortAllocation(start=8100, end=8199),
            services=[
                ServiceType.MCP_SERVERS,
                ServiceType.AI_ORCHESTRATION
            ],
            max_connections=1500,
            timeout_seconds=45
        ),
        
        "sophia-data-pipeline": LambdaInstance(
            name="sophia-data-pipeline",
            ip="104.171.202.134",
            gpu="A100 40GB",
            role=InstanceRole.DATA_PIPELINE,
            region="us-south-1",
            port_allocation=PortAllocation(start=8200, end=8299),
            services=[
                ServiceType.DATA_PROCESSING,
                ServiceType.ML_TRAINING,
                ServiceType.EMBEDDINGS
            ],
            max_connections=1000,
            timeout_seconds=120  # Longer timeout for ML operations
        ),
        
        "sophia-development": LambdaInstance(
            name="sophia-development",
            ip="155.248.194.183",
            gpu="A10 24GB",
            role=InstanceRole.DEVELOPMENT,
            region="us-west-1",
            port_allocation=PortAllocation(start=8300, end=8399),
            services=[
                ServiceType.TESTING,
                ServiceType.DEVELOPMENT
            ],
            max_connections=500,
            timeout_seconds=30
        )
    }
    
    @classmethod
    def get_instance_by_role(cls, role: InstanceRole) -> Optional[LambdaInstance]:
        """
        Get instance configuration by role.
        
        Args:
            role: The instance role to search for
            
        Returns:
            LambdaInstance if found, None otherwise
        """
        for instance in cls.INSTANCES.values():
            if instance.role == role:
                return instance
        return None
    
    @classmethod
    def get_instance_by_name(cls, name: str) -> Optional[LambdaInstance]:
        """
        Get instance configuration by name.
        
        Args:
            name: The instance name to search for
            
        Returns:
            LambdaInstance if found, None otherwise
        """
        return cls.INSTANCES.get(name)
    
    @classmethod
    def get_instance_by_ip(cls, ip: str) -> Optional[LambdaInstance]:
        """
        Get instance configuration by IP address.
        
        Args:
            ip: The IP address to search for
            
        Returns:
            LambdaInstance if found, None otherwise
        """
        for instance in cls.INSTANCES.values():
            if instance.ip == ip:
                return instance
        return None
    
    @classmethod
    def get_service_endpoint(cls, service: ServiceType) -> Optional[str]:
        """
        Get endpoint URL for a specific service.
        
        Args:
            service: The service type to find
            
        Returns:
            Service endpoint URL if found, None otherwise
        """
        for instance in cls.INSTANCES.values():
            if instance.has_service(service):
                port = instance.get_service_port(service)
                if port:
                    return f"http://{instance.ip}:{port}"
        return None
    
    @classmethod
    def get_instances_with_service(cls, service: ServiceType) -> List[LambdaInstance]:
        """
        Get all instances that provide a specific service.
        
        Args:
            service: The service type to search for
            
        Returns:
            List of instances providing the service
        """
        return [
            instance for instance in cls.INSTANCES.values()
            if instance.has_service(service)
        ]
    
    @classmethod
    def get_all_ips(cls) -> List[str]:
        """
        Get all instance IP addresses.
        
        Returns:
            List of all IP addresses in the infrastructure
        """
        return [instance.ip for instance in cls.INSTANCES.values()]
    
    @classmethod
    def get_all_endpoints(cls) -> Dict[str, str]:
        """
        Get all instance endpoints.
        
        Returns:
            Dictionary mapping instance names to their endpoints
        """
        return {
            name: instance.endpoint
            for name, instance in cls.INSTANCES.items()
        }
    
    @classmethod
    def validate_configuration(cls) -> List[str]:
        """
        Validate the infrastructure configuration.
        
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Check for duplicate IPs
        ips = [instance.ip for instance in cls.INSTANCES.values()]
        if len(ips) != len(set(ips)):
            errors.append("Duplicate IP addresses found in configuration")
        
        # Check for overlapping port ranges
        port_ranges = [
            (instance.name, instance.port_allocation.start, instance.port_allocation.end)
            for instance in cls.INSTANCES.values()
        ]
        
        for i, (name1, start1, end1) in enumerate(port_ranges):
            for name2, start2, end2 in port_ranges[i+1:]:
                if not (end1 < start2 or end2 < start1):
                    errors.append(
                        f"Overlapping port ranges: {name1} ({start1}-{end1}) "
                        f"and {name2} ({start2}-{end2})"
                    )
        
        # Check for unique roles
        roles = [instance.role for instance in cls.INSTANCES.values()]
        if len(roles) != len(set(roles)):
            errors.append("Duplicate instance roles found in configuration")
        
        return errors
    
    @classmethod
    def get_current_instance(cls) -> Optional[LambdaInstance]:
        """
        Get the current instance configuration based on environment variables.
        
        Returns:
            Current instance configuration if determinable, None otherwise
        """
        # Try to determine from environment variables
        current_ip = os.getenv('CURRENT_INSTANCE_IP')
        instance_name = os.getenv('INSTANCE_NAME')
        
        if current_ip:
            return cls.get_instance_by_ip(current_ip)
        elif instance_name:
            return cls.get_instance_by_name(instance_name)
        
        # Fallback to localhost detection (for development)
        if current_ip in ['localhost', '127.0.0.1', '0.0.0.0']:
            return cls.get_instance_by_role(InstanceRole.DEVELOPMENT)
        
        return None
    
    @classmethod
    def get_service_discovery_config(cls) -> Dict:
        """
        Get configuration for service discovery.
        
        Returns:
            Service discovery configuration dictionary
        """
        return {
            'enabled': os.getenv('SERVICE_DISCOVERY_ENABLED', 'true').lower() == 'true',
            'health_check_interval': int(os.getenv('HEALTH_CHECK_INTERVAL', '30')),
            'service_timeout': int(os.getenv('SERVICE_TIMEOUT', '5')),
            'retry_attempts': 3,
            'retry_delay': 2.0,
            'circuit_breaker_threshold': 5
        }

# Global configuration validation on module import
_validation_errors = InfrastructureConfig.validate_configuration()
if _validation_errors:
    logger.error("Infrastructure configuration validation errors:")
    for error in _validation_errors:
        logger.error(f"  - {error}")
    raise ValueError(f"Invalid infrastructure configuration: {'; '.join(_validation_errors)}")

logger.info("Infrastructure configuration loaded and validated successfully")
