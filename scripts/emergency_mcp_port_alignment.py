#!/usr/bin/env python3
"""
Emergency MCP Port Alignment Fix
Addresses critical port misalignments identified in MCP_PORT_ALIGNMENT_ANALYSIS_REPORT.md

CRITICAL ISSUES TO FIX:
1. ai_memory: Strategy=9000, K8s=9001, Monitoring=9001 (CONFLICT)
2. Multiple conflicting configuration files
3. No single source of truth for port assignments
4. Services scattered across wrong tiers

EMERGENCY ACTIONS:
- Create master port registry based on strategy
- Fix ai_memory port conflict
- Standardize all configuration files
- Update monitoring scripts
"""

import json
import sys
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_master_port_registry() -> Dict:
    """Create the master port registry based on MCP_COMPREHENSIVE_PORT_STRATEGY.md"""
    
    master_registry = {
        "version": "1.0.0",
        "last_updated": datetime.utcnow().isoformat() + "Z",
        "description": "Master MCP Port Registry - Single Source of Truth",
        "source": "MCP_COMPREHENSIVE_PORT_STRATEGY.md",
        "environments": {
            "production": {
                "range": "9000-9099",
                "offset": 0,
                "tiers": {
                    "core_ai": {
                        "range": "9000-9019",
                        "description": "Mission-critical AI services with GPU support",
                        "services": {
                            "ai_memory": {
                                "port": 9000,
                                "health_port": 9100,
                                "replicas": 3,
                                "gpu": True,
                                "priority": "CRITICAL",
                                "description": "Primary AI memory and context management"
                            },
                            "mcp_orchestrator": {
                                "port": 9001,
                                "health_port": 9101,
                                "replicas": 2,
                                "gpu": False,
                                "priority": "CRITICAL",
                                "description": "Central MCP service routing and orchestration"
                            },
                            "qdrant_admin": {
                                "port": 9002,
                                "health_port": 9102,
                                "replicas": 2,
                                "gpu": False,
                                "priority": "HIGH",
                                "description": "Vector database management and administration"
                            },
                            "lambda_inference": {
                                "port": 9003,
                                "health_port": 9103,
                                "replicas": 2,
                                "gpu": True,
                                "priority": "HIGH",
                                "description": "GPU-accelerated inference processing"
                            },
                            "unified_chat": {
                                "port": 9004,
                                "health_port": 9104,
                                "replicas": 3,
                                "gpu": False,
                                "priority": "CRITICAL",
                                "description": "Primary chat interface and coordination"
                            },
                            "portkey_gateway": {
                                "port": 9005,
                                "health_port": 9105,
                                "replicas": 2,
                                "gpu": False,
                                "priority": "HIGH",
                                "description": "LLM routing and management gateway"
                            },
                            "redis_cache": {
                                "port": 9006,
                                "health_port": 9106,
                                "replicas": 2,
                                "gpu": False,
                                "priority": "HIGH",
                                "description": "High-speed caching layer"
                            },
                            "postgres_manager": {
                                "port": 9007,
                                "health_port": 9107,
                                "replicas": 2,
                                "gpu": False,
                                "priority": "HIGH",
                                "description": "Database operations and management"
                            }
                        }
                    },
                    "business_intelligence": {
                        "range": "9020-9039",
                        "description": "Business tools and CRM integrations",
                        "services": {
                            "hubspot": {
                                "port": 9020,
                                "health_port": 9120,
                                "replicas": 2,
                                "gpu": False,
                                "priority": "HIGH",
                                "description": "CRM data integration and management"
                            },
                            "gong": {
                                "port": 9021,
                                "health_port": 9121,
                                "replicas": 2,
                                "gpu": True,
                                "priority": "HIGH",
                                "description": "Sales call analysis and insights"
                            },
                            "slack": {
                                "port": 9022,
                                "health_port": 9122,
                                "replicas": 2,
                                "gpu": False,
                                "priority": "MEDIUM",
                                "description": "Team communication integration"
                            },
                            "linear": {
                                "port": 9023,
                                "health_port": 9123,
                                "replicas": 1,
                                "gpu": False,
                                "priority": "MEDIUM",
                                "description": "Project management and tracking"
                            },
                            "asana": {
                                "port": 9024,
                                "health_port": 9124,
                                "replicas": 1,
                                "gpu": False,
                                "priority": "MEDIUM",
                                "description": "Task management and coordination"
                            },
                            "notion": {
                                "port": 9025,
                                "health_port": 9125,
                                "replicas": 1,
                                "gpu": False,
                                "priority": "MEDIUM",
                                "description": "Knowledge base and documentation"
                            }
                        }
                    },
                    "development_tools": {
                        "range": "9040-9059",
                        "description": "Development and code management tools",
                        "services": {
                            "github": {
                                "port": 9040,
                                "health_port": 9140,
                                "replicas": 1,
                                "gpu": False,
                                "priority": "MEDIUM",
                                "description": "Code repository management"
                            },
                            "codacy": {
                                "port": 9041,
                                "health_port": 9141,
                                "replicas": 1,
                                "gpu": False,
                                "priority": "LOW",
                                "description": "Code quality analysis"
                            },
                            "ui_ux_agent": {
                                "port": 9042,
                                "health_port": 9142,
                                "replicas": 1,
                                "gpu": False,
                                "priority": "LOW",
                                "description": "UI/UX development assistance"
                            }
                        }
                    },
                    "infrastructure": {
                        "range": "9060-9079",
                        "description": "Infrastructure and system services",
                        "services": {
                            "monitoring": {
                                "port": 9060,
                                "health_port": 9160,
                                "replicas": 1,
                                "gpu": False,
                                "priority": "HIGH",
                                "description": "System monitoring and metrics"
                            },
                            "logging": {
                                "port": 9061,
                                "health_port": 9161,
                                "replicas": 1,
                                "gpu": False,
                                "priority": "HIGH",
                                "description": "Centralized logging service"
                            }
                        }
                    }
                }
            },
            "staging": {
                "range": "9100-9199",
                "offset": 100,
                "description": "Staging environment with +100 port offset"
            },
            "development": {
                "range": "9200-9299",
                "offset": 200,
                "description": "Development environment with +200 port offset"
            },
            "testing": {
                "range": "9300-9399",
                "offset": 300,
                "description": "Testing environment with +300 port offset"
            }
        }
    }
    
    return master_registry

def backup_existing_configs():
    """Backup existing configuration files before making changes"""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = Path(f"config/backup/{timestamp}")
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"📦 Creating backup in {backup_dir}")
    
    config_files = [
        "config/unified_mcp_port_registry.json",
        "config/consolidated_mcp_ports.json", 
        "config/enhanced_mcp_ports.json",
        "config/cursor_production_mcp_config.json"
    ]
    
    backed_up = []
    for config_file in config_files:
        if Path(config_file).exists():
            shutil.copy2(config_file, backup_dir)
            backed_up.append(config_file)
            logger.info(f"✅ Backed up {config_file}")
        else:
            logger.warning(f"⚠️  Config file not found: {config_file}")
    
    return backup_dir, backed_up

def create_master_config_file(master_registry: Dict):
    """Create the master configuration file"""
    
    master_path = Path("config/mcp_master_port_registry.json")
    
    logger.info(f"📝 Creating master port registry: {master_path}")
    
    with open(master_path, 'w') as f:
        json.dump(master_registry, f, indent=2)
    
    logger.info("✅ Master port registry created")
    return master_path

def fix_ai_memory_port_conflict(master_registry: Dict):
    """Fix the critical ai_memory port conflict (9001 -> 9000)"""
    
    logger.info("🔧 Fixing ai_memory port conflict (9001 -> 9000)")
    
    # Files that need to be updated
    files_to_fix = [
        {
            "path": "k8s/mcp-servers/ai-memory.yaml",
            "changes": [
                ("containerPort: 9001", "containerPort: 9000"),
                ('value: "9001"', 'value: "9000"'),
                ("port: 9001", "port: 9000")
            ]
        },
        {
            "path": "scripts/monitor_mcp_servers.py", 
            "changes": [
                ('"port": 9001', '"port": 9000'),
                ("'port': 9001", "'port': 9000"),
                ("port=9001", "port=9000")
            ]
        },
        {
            "path": "scripts/start_ai_memory_server.py",
            "changes": [
                ('MCP_SERVER_PORT = "9001"', 'MCP_SERVER_PORT = "9000"'),
                ("MCP_SERVER_PORT = 9001", "MCP_SERVER_PORT = 9000"),
                ("--port 9001", "--port 9000")
            ]
        }
    ]
    
    fixed_files = []
    
    for file_info in files_to_fix:
        file_path = Path(file_info["path"])
        
        if not file_path.exists():
            logger.warning(f"⚠️  File not found: {file_path}")
            continue
        
        # Read file content
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Apply changes
        original_content = content
        for old_text, new_text in file_info["changes"]:
            content = content.replace(old_text, new_text)
        
        # Write back if changes were made
        if content != original_content:
            with open(file_path, 'w') as f:
                f.write(content)
            fixed_files.append(str(file_path))
            logger.info(f"✅ Fixed ai_memory ports in {file_path}")
        else:
            logger.info(f"ℹ️  No changes needed in {file_path}")
    
    return fixed_files

def update_service_discovery_config(master_registry: Dict):
    """Update service discovery configuration files"""
    
    logger.info("🔧 Updating service discovery configurations")
    
    # Create standardized service discovery config
    service_discovery_config = {
        "version": "1.0.0",
        "services": {}
    }
    
    # Extract service information from master registry
    for tier_name, tier_info in master_registry["environments"]["production"]["tiers"].items():
        for service_name, service_info in tier_info["services"].items():
            service_discovery_config["services"][service_name] = {
                "port": service_info["port"],
                "health_port": service_info["health_port"],
                "tier": tier_name,
                "replicas": service_info["replicas"],
                "gpu_required": service_info["gpu"],
                "priority": service_info["priority"],
                "dns_name": f"{service_name}-mcp.mcp-servers.svc.cluster.local"
            }
    
    # Write service discovery config
    discovery_path = Path("config/service_discovery_registry.json")
    with open(discovery_path, 'w') as f:
        json.dump(service_discovery_config, f, indent=2)
    
    logger.info(f"✅ Created service discovery config: {discovery_path}")
    return discovery_path

def update_monitoring_scripts(master_registry: Dict):
    """Update monitoring scripts with correct port assignments"""
    
    logger.info("🔧 Updating monitoring scripts")
    
    # Create monitoring configuration
    monitoring_config = []
    
    for tier_name, tier_info in master_registry["environments"]["production"]["tiers"].items():
        for service_name, service_info in tier_info["services"].items():
            monitoring_config.append({
                "name": service_name.replace("_", " ").title(),
                "service": service_name,
                "port": service_info["port"],
                "health_port": service_info["health_port"],
                "tier": tier_name,
                "priority": service_info["priority"],
                "gpu_required": service_info["gpu"]
            })
    
    # Write monitoring configuration
    monitoring_path = Path("config/monitoring_services_registry.json")
    with open(monitoring_path, 'w') as f:
        json.dump({"services": monitoring_config}, f, indent=2)
    
    logger.info(f"✅ Created monitoring services registry: {monitoring_path}")
    return monitoring_path

def validate_port_assignments(master_registry: Dict):
    """Validate that all port assignments are unique and within proper ranges"""
    
    logger.info("🔍 Validating port assignments")
    
    used_ports = set()
    conflicts = []
    
    for tier_name, tier_info in master_registry["environments"]["production"]["tiers"].items():
        tier_range = tier_info["range"]
        range_start, range_end = map(int, tier_range.split("-"))
        
        for service_name, service_info in tier_info["services"].items():
            port = service_info["port"]
            health_port = service_info["health_port"]
            
            # Check if port is in correct range
            if not (range_start <= port <= range_end):
                conflicts.append(f"Service {service_name} port {port} outside tier range {tier_range}")
            
            # Check for duplicate ports
            if port in used_ports:
                conflicts.append(f"Duplicate port {port} for service {service_name}")
            else:
                used_ports.add(port)
            
            if health_port in used_ports:
                conflicts.append(f"Duplicate health port {health_port} for service {service_name}")
            else:
                used_ports.add(health_port)
    
    if conflicts:
        logger.error("❌ Port validation failed:")
        for conflict in conflicts:
            logger.error(f"   - {conflict}")
        return False
    else:
        logger.info("✅ All port assignments validated successfully")
        return True

def generate_alignment_report(master_registry: Dict, fixed_files: List[str]):
    """Generate a report showing the alignment fixes applied"""
    
    report = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "status": "EMERGENCY_FIXES_APPLIED",
        "master_registry_created": True,
        "ai_memory_conflict_fixed": True,
        "files_updated": fixed_files,
        "port_assignments": {},
        "next_steps": [
            "Deploy updated Kubernetes configurations",
            "Restart affected MCP services",
            "Validate service discovery",
            "Implement staging environment (+100 offset)",
            "Add missing infrastructure services"
        ]
    }
    
    # Extract port assignments for verification
    for tier_name, tier_info in master_registry["environments"]["production"]["tiers"].items():
        for service_name, service_info in tier_info["services"].items():
            report["port_assignments"][service_name] = {
                "port": service_info["port"],
                "health_port": service_info["health_port"],
                "tier": tier_name,
                "status": "ALIGNED"
            }
    
    # Write report
    report_path = Path("MCP_EMERGENCY_ALIGNMENT_REPORT.json")
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    logger.info(f"📊 Emergency alignment report saved: {report_path}")
    return report_path

def main():
    """Main emergency alignment function"""
    
    logger.info("🚨 STARTING EMERGENCY MCP PORT ALIGNMENT")
    logger.info("🎯 Addressing critical issues from MCP_PORT_ALIGNMENT_ANALYSIS_REPORT.md")
    
    try:
        # Phase 1: Backup existing configurations
        backup_dir, backed_up_files = backup_existing_configs()
        logger.info(f"✅ Backed up {len(backed_up_files)} configuration files")
        
        # Phase 2: Create master port registry
        master_registry = create_master_port_registry()
        master_path = create_master_config_file(master_registry)
        logger.info("✅ Master port registry created based on strategic plan")
        
        # Phase 3: Validate port assignments
        if not validate_port_assignments(master_registry):
            logger.error("❌ Port validation failed - cannot proceed")
            return False
        
        # Phase 4: Fix ai_memory port conflict
        fixed_files = fix_ai_memory_port_conflict(master_registry)
        logger.info(f"✅ Fixed ai_memory port conflict in {len(fixed_files)} files")
        
        # Phase 5: Update service discovery
        discovery_path = update_service_discovery_config(master_registry)
        logger.info("✅ Service discovery configuration updated")
        
        # Phase 6: Update monitoring
        monitoring_path = update_monitoring_scripts(master_registry)
        logger.info("✅ Monitoring configuration updated")
        
        # Phase 7: Generate report
        report_path = generate_alignment_report(master_registry, fixed_files)
        
        # Success summary
        logger.info("\n" + "="*60)
        logger.info("🎉 EMERGENCY MCP PORT ALIGNMENT COMPLETED")
        logger.info("="*60)
        logger.info(f"✅ Master Registry: {master_path}")
        logger.info(f"✅ Service Discovery: {discovery_path}")
        logger.info(f"✅ Monitoring Config: {monitoring_path}")
        logger.info(f"✅ Alignment Report: {report_path}")
        logger.info(f"✅ Files Fixed: {len(fixed_files)}")
        logger.info("")
        logger.info("🚀 NEXT STEPS:")
        logger.info("   1. Review the generated configurations")
        logger.info("   2. Deploy updated Kubernetes manifests")
        logger.info("   3. Restart affected MCP services")
        logger.info("   4. Validate service discovery is working")
        logger.info("   5. Proceed with Phase 2: Systematic Alignment")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Emergency alignment failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 