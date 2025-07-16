# 🏗️ PRODUCTION INFRASTRUCTURE CONFIGURATION
# Single Source of Truth for Sophia AI Distributed Infrastructure

"""
Production Infrastructure Configuration
=====================================
This is the authoritative configuration for Sophia AI's distributed
infrastructure across 5 Lambda Labs instances.

DO NOT modify without validating against actual production setup.
All deployment scripts must use this as the single source of truth.
"""

import os
from typing import Dict, List, Any
from dataclasses import dataclass

@dataclass
class InstanceConfig:
    """Configuration for a Lambda Labs instance"""
    ip: str
    gpu: str
    role: str
    services: List[str]
    ports: Dict[str, int]
    ssh_user: str = "ubuntu"
    ssh_key_path: str = "~/.ssh/lambda_labs_key"

@dataclass 
class ProductionInfrastructure:
    """Complete production infrastructure configuration"""
    instances: Dict[str, InstanceConfig]
    nginx_primary: str
    port_ranges: Dict[str, tuple]
    health_check_interval: int = 30

# 🎯 PRODUCTION INFRASTRUCTURE DEFINITION
PRODUCTION_INFRASTRUCTURE = ProductionInfrastructure(
    instances={
        "ai_core": InstanceConfig(
            ip="192.222.58.232",
            gpu="GH200 96GB", 
            role="Primary/Master - AI Core Services",
            services=["vector_search_mcp", "real_time_chat_mcp", "ai_memory_mcp", "unified_memory_service"],
            ports={
                "vector_search_mcp": 8000,
                "real_time_chat_mcp": 8001,
                "ai_memory_mcp": 8002,
                "unified_memory_service": 9000,  # Strategic port
                "health_monitor": 9100,
                "nginx": 80,
                "nginx_ssl": 443
            }
        ),
        
        "business_tools": InstanceConfig(
            ip="104.171.202.117",
            gpu="A6000 48GB",
            role="Business Intelligence Hub",
            services=["gong_mcp", "hubspot_mcp", "linear_mcp", "asana_mcp", "slack_mcp"],
            ports={
                "gong_mcp": 8100,
                "hubspot_mcp": 8101, 
                "linear_mcp": 8102,
                "asana_mcp": 8103,
                "slack_mcp": 8104
            }
        ),
        
        "data_pipeline": InstanceConfig(
            ip="104.171.202.134",
            gpu="A100 80GB",
            role="Data Processing Pipeline",
            services=["github_mcp", "notion_mcp", "postgres_mcp", "snowflake_mcp"],
            ports={
                "github_mcp": 8200,
                "notion_mcp": 8201,
                "postgres_mcp": 8202,
                "snowflake_mcp": 8203
            }
        ),
        
        "production_services": InstanceConfig(
            ip="104.171.202.103",
            gpu="RTX6000 48GB",
            role="Production Services",
            services=["codacy_mcp", "portkey_admin", "ui_ux_agent"],
            ports={
                "codacy_mcp": 8300,
                "portkey_admin": 8301,
                "ui_ux_agent": 8302
            }
        ),
        
        "development": InstanceConfig(
            ip="155.248.194.183", 
            gpu="A10 24GB",
            role="Development & Testing",
            services=["test_mcp", "backup_services"],
            ports={
                "test_mcp": 8400,
                "backup_services": 8401
            }
        )
    },
    
    nginx_primary="192.222.58.232",
    
    port_ranges={
        "ai_core": (8000, 8099),
        "business_tools": (8100, 8199), 
        "data_pipeline": (8200, 8299),
        "production_services": (8300, 8399),
        "development": (8400, 8499),
        "strategic_services": (9000, 9099),  # Unified Memory Architecture
        "health_monitoring": (9100, 9199)
    },
    
    health_check_interval=30
)

# 🔍 UTILITY FUNCTIONS

def get_instance_by_ip(ip: str) -> InstanceConfig:
    """Get instance configuration by IP address"""
    for instance in PRODUCTION_INFRASTRUCTURE.instances.values():
        if instance.ip == ip:
            return instance
    raise ValueError(f"No instance found with IP: {ip}")

def get_service_instance(service_name: str) -> tuple[str, InstanceConfig]:
    """Get instance that hosts a specific service"""
    for instance_name, instance in PRODUCTION_INFRASTRUCTURE.instances.items():
        if service_name in instance.services:
            return instance_name, instance
    raise ValueError(f"No instance found hosting service: {service_name}")

def get_service_port(service_name: str) -> int:
    """Get port number for a specific service"""
    for instance in PRODUCTION_INFRASTRUCTURE.instances.values():
        if service_name in instance.ports:
            return instance.ports[service_name]
    raise ValueError(f"No port configured for service: {service_name}")

def get_all_service_endpoints() -> Dict[str, str]:
    """Get all service endpoints in format service_name: http://ip:port"""
    endpoints = {}
    for instance in PRODUCTION_INFRASTRUCTURE.instances.values():
        for service_name, port in instance.ports.items():
            if service_name not in ["nginx", "nginx_ssl", "health_monitor"]:
                endpoints[service_name] = f"http://{instance.ip}:{port}"
    return endpoints

def generate_nginx_upstream_config() -> str:
    """Generate nginx upstream configuration for load balancing"""
    config_lines = []
    
    # Group services by tier for upstream blocks
    for tier_name, (start_port, end_port) in PRODUCTION_INFRASTRUCTURE.port_ranges.items():
        if tier_name == "strategic_services" or tier_name == "health_monitoring":
            continue
            
        config_lines.append(f"upstream {tier_name}_services {{")
        
        for instance in PRODUCTION_INFRASTRUCTURE.instances.values():
            for service_name, port in instance.ports.items():
                if start_port <= port <= end_port:
                    config_lines.append(f"    server {instance.ip}:{port};")
        
        config_lines.append("}")
        config_lines.append("")
    
    return "\n".join(config_lines)

def validate_port_ranges() -> bool:
    """Validate that all service ports are within their assigned ranges"""
    for instance in PRODUCTION_INFRASTRUCTURE.instances.values():
        for service_name, port in instance.ports.items():
            # Skip special ports
            if service_name in ["nginx", "nginx_ssl", "health_monitor"]:
                continue
                
            # Find appropriate range
            port_in_range = False
            for tier_name, (start_port, end_port) in PRODUCTION_INFRASTRUCTURE.port_ranges.items():
                if start_port <= port <= end_port:
                    port_in_range = True
                    break
            
            if not port_in_range:
                print(f"WARNING: Service {service_name} port {port} not in any defined range")
                return False
    
    return True

# 🚀 DEPLOYMENT CONFIGURATION

DEPLOYMENT_CONFIG = {
    "ssh_timeout": 30,
    "service_restart_timeout": 60,
    "health_check_retries": 5,
    "deployment_batch_size": 3,  # Deploy to max 3 instances simultaneously
    "rollback_enabled": True,
    "backup_before_deploy": True
}

# 🔐 SECURITY CONFIGURATION

SECURITY_CONFIG = {
    "ssh_key_required": True,
    "firewall_enabled": True,
    "ssl_required": True,
    "allowed_ssh_users": ["ubuntu"],
    "service_users": ["sophia", "ubuntu"],
    "log_retention_days": 30
}

if __name__ == "__main__":
    # Validation on import
    print("🔍 Validating Production Infrastructure Configuration...")
    
    if validate_port_ranges():
        print("✅ All service ports within assigned ranges")
    else:
        print("❌ Port range validation failed")
    
    print(f"📊 Total instances: {len(PRODUCTION_INFRASTRUCTURE.instances)}")
    print(f"📊 Total services: {sum(len(instance.services) for instance in PRODUCTION_INFRASTRUCTURE.instances.values())}")
    print(f"🌐 Primary nginx: {PRODUCTION_INFRASTRUCTURE.nginx_primary}")
    print("✅ Production infrastructure configuration loaded successfully") 