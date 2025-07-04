#!/usr/bin/env python3
"""
Optimize Docker Swarm resource allocation for Sophia AI
Addresses node saturation and resource contention issues
"""

import yaml
import json
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional
import argparse
import sys

# Service type detection patterns
SERVICE_PATTERNS = {
    'backend': ['backend', 'api', 'fastapi', 'web'],
    'mcp-server': ['mcp', 'server', 'agent'],
    'database': ['postgres', 'postgresql', 'mysql', 'mongo'],
    'cache': ['redis', 'memcached', 'cache'],
    'gateway': ['traefik', 'nginx', 'gateway', 'proxy'],
    'monitoring': ['prometheus', 'grafana', 'exporter'],
    'ai-service': ['llm', 'openai', 'anthropic', 'cortex'],
}

# Optimized resource limits by service type
RESOURCE_LIMITS = {
    'backend': {
        'cpus': '2.0',
        'memory': '4G',
        'replicas': 3,
        'placement': ['node.labels.tier == compute']
    },
    'mcp-server': {
        'cpus': '1.0',
        'memory': '2G',
        'replicas': 2,
        'placement': ['node.labels.tier == compute']
    },
    'database': {
        'cpus': '4.0',
        'memory': '8G',
        'replicas': 1,  # Use replication instead
        'placement': ['node.labels.tier == storage', 'node.labels.ssd == true']
    },
    'cache': {
        'cpus': '2.0',
        'memory': '4G',
        'replicas': 3,
        'placement': ['node.labels.tier == memory']
    },
    'gateway': {
        'cpus': '1.0',
        'memory': '1G',
        'replicas': 2,
        'placement': ['node.role == manager']
    },
    'monitoring': {
        'cpus': '0.5',
        'memory': '1G',
        'replicas': 1,
        'placement': []
    },
    'ai-service': {
        'cpus': '4.0',
        'memory': '8G',
        'replicas': 2,
        'placement': ['node.labels.gpu == true']
    },
    'default': {
        'cpus': '1.0',
        'memory': '2G',
        'replicas': 2,
        'placement': []
    }
}

# Health check templates
HEALTH_CHECKS = {
    'http': {
        'test': ["CMD", "curl", "-f", "http://localhost:{port}/health"],
        'interval': '30s',
        'timeout': '10s',
        'retries': 3,
        'start_period': '40s'
    },
    'tcp': {
        'test': ["CMD", "nc", "-z", "localhost", "{port}"],
        'interval': '30s',
        'timeout': '10s',
        'retries': 3,
        'start_period': '40s'
    },
    'postgres': {
        'test': ["CMD-SHELL", "pg_isready -U postgres"],
        'interval': '10s',
        'timeout': '5s',
        'retries': 5,
        'start_period': '30s'
    },
    'redis': {
        'test': ["CMD", "redis-cli", "ping"],
        'interval': '10s',
        'timeout': '5s',
        'retries': 5,
        'start_period': '30s'
    }
}


def detect_service_type(service_name: str) -> str:
    """Detect service type based on name patterns"""
    service_lower = service_name.lower()
    
    for service_type, patterns in SERVICE_PATTERNS.items():
        for pattern in patterns:
            if pattern in service_lower:
                return service_type
    
    return 'default'


def get_service_port(service_config: Dict[str, Any]) -> Optional[int]:
    """Extract service port from configuration"""
    # Check ports configuration
    if 'ports' in service_config:
        for port_mapping in service_config['ports']:
            if isinstance(port_mapping, str):
                # Format: "8000:8000" or "8000"
                parts = port_mapping.split(':')
                return int(parts[-1])
            elif isinstance(port_mapping, dict):
                # Format: {target: 8000, published: 8000}
                return port_mapping.get('target', port_mapping.get('published'))
    
    # Check expose configuration
    if 'expose' in service_config:
        return int(service_config['expose'][0])
    
    return None


def generate_health_check(service_name: str, service_config: Dict[str, Any]) -> Dict[str, Any]:
    """Generate appropriate health check for service"""
    # Skip if health check already exists
    if 'healthcheck' in service_config:
        return service_config['healthcheck']
    
    service_type = detect_service_type(service_name)
    port = get_service_port(service_config)
    
    # Special cases
    if 'postgres' in service_name.lower():
        return HEALTH_CHECKS['postgres']
    elif 'redis' in service_name.lower():
        return HEALTH_CHECKS['redis']
    elif port:
        # Use HTTP health check for services with web ports
        health_check = HEALTH_CHECKS['http'].copy()
        health_check['test'] = [
            cmd.replace('{port}', str(port)) for cmd in health_check['test']
        ]
        return health_check
    
    # Default - return empty dict instead of None
    return {}


def optimize_service(service_name: str, service_config: Dict[str, Any]) -> Dict[str, Any]:
    """Optimize a single service configuration"""
    service_type = detect_service_type(service_name)
    limits = RESOURCE_LIMITS[service_type]
    
    # Initialize deploy section
    if 'deploy' not in service_config:
        service_config['deploy'] = {}
    
    deploy = service_config['deploy']
    
    # Set replicas
    if 'replicas' not in deploy:
        deploy['replicas'] = limits['replicas']
    
    # Set resource limits
    deploy['resources'] = {
        'limits': {
            'cpus': limits['cpus'],
            'memory': limits['memory']
        },
        'reservations': {
            'cpus': str(float(limits['cpus']) / 2),
            'memory': f"{int(limits['memory'][:-1]) // 2}G"
        }
    }
    
    # Set placement constraints
    if limits['placement'] and 'placement' not in deploy:
        deploy['placement'] = {
            'constraints': limits['placement']
        }
    
    # Add update configuration for safe rolling updates
    if 'update_config' not in deploy:
        deploy['update_config'] = {
            'parallelism': 1,
            'delay': '10s',
            'failure_action': 'rollback',
            'monitor': '30s',
            'max_failure_ratio': 0.3
        }
    
    # Add restart policy
    if 'restart_policy' not in deploy:
        deploy['restart_policy'] = {
            'condition': 'on-failure',
            'delay': '5s',
            'max_attempts': 3,
            'window': '120s'
        }
    
    # Generate health check
    health_check = generate_health_check(service_name, service_config)
    if health_check and 'healthcheck' not in service_config:
        service_config['healthcheck'] = health_check
    
    return service_config


def optimize_networks(config: Dict[str, Any]) -> Dict[str, Any]:
    """Optimize network configuration for reduced latency"""
    if 'networks' not in config:
        config['networks'] = {}
    
    # Define optimized network topology
    optimized_networks = {
        'frontend': {
            'driver': 'overlay',
            'attachable': True,
            'driver_opts': {
                'encrypted': 'false'  # Encryption adds latency
            }
        },
        'backend': {
            'driver': 'overlay',
            'internal': True,
            'driver_opts': {
                'encrypted': 'false'
            }
        },
        'data': {
            'driver': 'overlay',
            'internal': True,
            'driver_opts': {
                'encrypted': 'true'  # Encrypt data layer
            }
        }
    }
    
    # Merge with existing networks
    for net_name, net_config in optimized_networks.items():
        if net_name not in config['networks']:
            config['networks'][net_name] = net_config
    
    return config


def assign_service_networks(service_name: str, service_config: Dict[str, Any]) -> Dict[str, Any]:
    """Assign services to appropriate networks"""
    service_type = detect_service_type(service_name)
    
    # Network assignment rules
    network_rules = {
        'gateway': ['frontend', 'backend'],
        'backend': ['backend', 'data'],
        'database': ['data'],
        'cache': ['data'],
        'mcp-server': ['backend'],
        'monitoring': ['backend', 'data'],
        'ai-service': ['backend'],
    }
    
    networks = network_rules.get(service_type, ['backend'])
    
    if 'networks' not in service_config:
        service_config['networks'] = networks
    
    return service_config


def validate_configuration(config: Dict[str, Any]) -> bool:
    """Validate the optimized configuration"""
    print("🔍 Validating configuration...")
    
    issues = []
    
    for service_name, service_config in config.get('services', {}).items():
        # Check for resource limits
        if 'deploy' not in service_config:
            issues.append(f"{service_name}: Missing deploy section")
        elif 'resources' not in service_config['deploy']:
            issues.append(f"{service_name}: Missing resource limits")
        
        # Check for health checks (except volumes)
        if not service_name.endswith('_data') and 'healthcheck' not in service_config:
            print(f"⚠️  {service_name}: No health check defined")
    
    if issues:
        print("\n❌ Validation failed:")
        for issue in issues:
            print(f"   - {issue}")
        return False
    
    print("✅ Configuration validated successfully")
    return True


def main():
    parser = argparse.ArgumentParser(
        description='Optimize Docker Swarm configuration for Sophia AI'
    )
    parser.add_argument(
        'compose_file',
        help='Path to docker-compose file'
    )
    parser.add_argument(
        '-o', '--output',
        help='Output file (default: adds .optimized suffix)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be changed without modifying files'
    )
    parser.add_argument(
        '--validate-only',
        action='store_true',
        help='Only validate the configuration'
    )
    
    args = parser.parse_args()
    
    # Load compose file
    compose_path = Path(args.compose_file)
    if not compose_path.exists():
        print(f"❌ File not found: {compose_path}")
        sys.exit(1)
    
    print(f"📁 Loading {compose_path}...")
    with open(compose_path, 'r') as f:
        config = yaml.safe_load(f)
    
    if args.validate_only:
        validate_configuration(config)
        return
    
    # Optimize configuration
    print("\n🔧 Optimizing configuration...")
    
    # Optimize each service
    for service_name, service_config in config.get('services', {}).items():
        print(f"   Optimizing {service_name}...")
        config['services'][service_name] = optimize_service(service_name, service_config)
        config['services'][service_name] = assign_service_networks(service_name, service_config)
    
    # Optimize networks
    config = optimize_networks(config)
    
    # Validate optimized configuration
    if not validate_configuration(config):
        print("\n⚠️  Configuration has issues but proceeding anyway")
    
    # Save or display results
    if args.dry_run:
        print("\n📋 Optimized configuration (dry run):")
        print(yaml.dump(config, default_flow_style=False))
    else:
        output_path = args.output or str(compose_path) + '.optimized'
        
        # Backup original
        backup_path = str(compose_path) + '.backup'
        print(f"\n💾 Creating backup: {backup_path}")
        compose_path.rename(backup_path)
        
        # Save optimized version
        print(f"💾 Saving optimized configuration: {output_path}")
        with open(output_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)
        
        print("\n✅ Optimization complete!")
        print(f"   Original backed up to: {backup_path}")
        print(f"   Optimized config saved to: {output_path}")
        
        print("\n📝 Next steps:")
        print("   1. Review the optimized configuration")
        print("   2. Test in staging environment first")
        print("   3. Deploy with: docker stack deploy -c {} sophia-ai".format(output_path))


if __name__ == "__main__":
    main() 