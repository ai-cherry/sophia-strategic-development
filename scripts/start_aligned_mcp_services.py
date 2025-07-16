#!/usr/bin/env python3
"""
Start Strategically Aligned MCP Services
Uses the master port registry to start MCP services with the correct strategic port assignments

This script addresses the critical port misalignments by:
1. Loading port assignments from the master registry (single source of truth)
2. Starting services with their strategic ports
3. Configuring proper health check endpoints
4. Validating tier-based service organization
"""

import json
import subprocess
import sys
import logging
from pathlib import Path
from typing import Dict
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_master_port_registry() -> Dict:
    """Load the master port registry (single source of truth)"""
    
    registry_path = Path("config/mcp_master_port_registry.json")
    
    if not registry_path.exists():
        logger.error(f"❌ Master port registry not found: {registry_path}")
        logger.error("Run scripts/emergency_mcp_port_alignment.py first")
        sys.exit(1)
    
    with open(registry_path, 'r') as f:
        registry = json.load(f)
    
    logger.info(f"✅ Loaded master port registry v{registry['version']}")
    logger.info(f"📅 Last updated: {registry['last_updated']}")
    
    return registry

def map_discovered_services_to_strategic_ports(registry: Dict) -> Dict:
    """Map the actual discovered services to their strategic port assignments"""
    
    # Services that actually exist on instances (from discovery)
    discovered_services = {
        "192.222.58.232": {  # Core Instance
            "name": "sophia-ai-core",
            "discovered": ["sophia-vector_search_mcp", "sophia-real_time_chat_mcp", "sophia-ai_memory_mcp"],
            "strategic_services": []
        },
        "104.171.202.117": {  # Orchestrator Instance
            "name": "sophia-mcp-orchestrator",
            "discovered": ["sophia-asana_mcp", "sophia-gong_mcp", "sophia-hubspot_mcp", "sophia-linear_mcp"],
            "strategic_services": []
        },
        "104.171.202.134": {  # Pipeline Instance
            "name": "sophia-data-pipeline",
            "discovered": ["sophia-github_mcp", "sophia-notion_mcp", "sophia-postgres_mcp", "sophia-slack_mcp"],
            "strategic_services": []
        },
        "155.248.194.183": {  # Dev Instance
            "name": "sophia-development",
            "discovered": ["sophia-brave_search_mcp", "sophia-everything_mcp", "sophia-filesystem_mcp"],
            "strategic_services": []
        },
        "104.171.202.103": {  # Production Instance
            "name": "sophia-production-instance",
            "discovered": ["sophia-legacy_support_mcp"],
            "strategic_services": []
        }
    }
    
    # Mapping from discovered service names to strategic service names
    service_mapping = {
        "sophia-ai_memory_mcp": "ai_memory",
        "sophia-vector_search_mcp": "qdrant_admin",  # Maps to vector DB management
        "sophia-real_time_chat_mcp": "unified_chat",
        "sophia-hubspot_mcp": "hubspot",
        "sophia-gong_mcp": "gong",
        "sophia-slack_mcp": "slack",
        "sophia-linear_mcp": "linear",
        "sophia-asana_mcp": "asana",
        "sophia-notion_mcp": "notion",
        "sophia-github_mcp": "github",
        "sophia-postgres_mcp": "postgres_manager",
        "sophia-brave_search_mcp": "search_tools",  # Development tier
        "sophia-everything_mcp": "utility_tools",   # Development tier
        "sophia-filesystem_mcp": "file_manager",    # Development tier
        "sophia-legacy_support_mcp": "legacy_support"  # Infrastructure tier
    }
    
    # Extract strategic service info from registry
    strategic_services = {}
    for tier_name, tier_info in registry["environments"]["production"]["tiers"].items():
        for service_name, service_info in tier_info["services"].items():
            strategic_services[service_name] = {
                **service_info,
                "tier": tier_name,
                "strategic_name": service_name
            }
    
    # Map discovered services to strategic assignments
    for ip, instance_info in discovered_services.items():
        for discovered_service in instance_info["discovered"]:
            if discovered_service in service_mapping:
                strategic_name = service_mapping[discovered_service]
                if strategic_name in strategic_services:
                    service_config = strategic_services[strategic_name].copy()
                    service_config["discovered_name"] = discovered_service
                    instance_info["strategic_services"].append(service_config)
                    logger.info(f"📋 Mapped {discovered_service} → {strategic_name} (port {service_config['port']})")
                else:
                    logger.warning(f"⚠️  Strategic service {strategic_name} not found in registry")
            else:
                logger.warning(f"⚠️  No mapping for discovered service: {discovered_service}")
    
    return discovered_services

def run_ssh_command(ip: str, command: str, timeout: int = 30) -> tuple[bool, str, str]:
    """Execute SSH command on remote instance"""
    ssh_cmd = [
        "ssh", "-o", "StrictHostKeyChecking=no",
        "-o", "ConnectTimeout=10",
        f"ubuntu@{ip}",
        command
    ]
    
    try:
        result = subprocess.run(
            ssh_cmd, 
            capture_output=True, 
            text=True, 
            timeout=timeout
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "SSH timeout"
    except Exception as e:
        return False, "", str(e)

def configure_service_port(ip: str, service_name: str, strategic_port: int, health_port: int) -> bool:
    """Configure a service to use its strategic port assignment"""
    
    logger.info(f"🔧 Configuring {service_name} for strategic port {strategic_port}")
    
    # Commands to configure the service with strategic ports
    config_commands = [
        f"sudo mkdir -p /etc/sophia/mcp-services/{service_name}",
        f"echo 'MCP_PORT={strategic_port}' | sudo tee /etc/sophia/mcp-services/{service_name}/port.conf",
        f"echo 'HEALTH_PORT={health_port}' | sudo tee -a /etc/sophia/mcp-services/{service_name}/port.conf",
        f"sudo systemctl set-environment MCP_PORT_{service_name.upper().replace('-', '_')}={strategic_port}"
    ]
    
    for cmd in config_commands:
        success, stdout, stderr = run_ssh_command(ip, cmd)
        if not success:
            logger.warning(f"⚠️  Config command failed: {cmd}")
            logger.warning(f"   Error: {stderr}")
    
    logger.info(f"✅ Configured {service_name} for port {strategic_port}")
    return True

def start_strategic_service(ip: str, service_config: Dict) -> bool:
    """Start a service with its strategic configuration"""
    
    service_name = service_config["discovered_name"]
    strategic_port = service_config["port"]
    health_port = service_config["health_port"]
    tier = service_config["tier"]
    priority = service_config["priority"]
    
    logger.info(f"🚀 Starting {service_name} ({tier} tier, {priority} priority)")
    logger.info(f"   Strategic port: {strategic_port}, Health port: {health_port}")
    
    # Configure service ports first
    configure_service_port(ip, service_name, strategic_port, health_port)
    
    # Enable and start the service
    commands = [
        f"sudo systemctl enable {service_name}.service",
        f"sudo systemctl start {service_name}.service"
    ]
    
    for cmd in commands:
        success, stdout, stderr = run_ssh_command(ip, cmd)
        if success:
            logger.info(f"✅ {cmd.split()[-1].title()}: {service_name}")
        else:
            logger.error(f"❌ Failed {cmd.split()[-1]}: {service_name}")
            logger.error(f"   Error: {stderr}")
            return False
    
    return True

def check_strategic_service_status(ip: str, service_config: Dict) -> Dict:
    """Check service status using strategic port assignments"""
    
    service_name = service_config["discovered_name"]
    strategic_port = service_config["port"]
    health_port = service_config["health_port"]
    
    # Check systemd service status
    success, stdout, stderr = run_ssh_command(ip, f"sudo systemctl is-active {service_name}.service")
    systemd_status = stdout.strip() if success else "inactive"
    
    # Check if strategic port is listening
    success, stdout, stderr = run_ssh_command(ip, f"ss -tuln | grep :{strategic_port}")
    port_listening = success and str(strategic_port) in stdout
    
    # Check health endpoint if available
    health_responding = False
    try:
        import requests
        health_url = f"http://{ip}:{health_port}/health"
        response = requests.get(health_url, timeout=5)
        health_responding = response.status_code == 200
    except:
        health_responding = False
    
    status = {
        "service": service_name,
        "strategic_port": strategic_port,
        "health_port": health_port,
        "systemd_status": systemd_status,
        "port_listening": port_listening,
        "health_responding": health_responding,
        "overall_status": "HEALTHY" if (systemd_status == "active" and port_listening) else "DEGRADED"
    }
    
    return status

def test_strategic_connectivity(service_map: Dict) -> Dict:
    """Test connectivity using strategic port assignments"""
    
    logger.info(f"\n{'='*60}")
    logger.info("🔗 Testing Strategic Port Connectivity")
    logger.info(f"{'='*60}")
    
    connectivity_results = {}
    
    for ip, instance_info in service_map.items():
        instance_name = instance_info["name"]
        logger.info(f"🔗 Testing {instance_name} ({ip})")
        
        instance_results = []
        for service_config in instance_info["strategic_services"]:
            status = check_strategic_service_status(ip, service_config)
            instance_results.append(status)
            
            # Log status
            service_name = status["service"]
            strategic_port = status["strategic_port"]
            overall_status = status["overall_status"]
            status_icon = "✅" if overall_status == "HEALTHY" else "⚠️"
            
            logger.info(f"   {service_name}: {status_icon} {overall_status} (port {strategic_port})")
        
        connectivity_results[ip] = instance_results
    
    return connectivity_results

def generate_strategic_activation_report(service_map: Dict, connectivity_results: Dict):
    """Generate comprehensive activation report with strategic alignment details"""
    
    report = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "status": "STRATEGIC_ALIGNMENT_DEPLOYMENT",
        "master_registry_version": "1.0.0",
        "instances": {},
        "summary": {
            "total_services": 0,
            "healthy_services": 0,
            "degraded_services": 0,
            "success_rate": 0
        },
        "strategic_alignment": {
            "core_ai_tier": {"services": 0, "healthy": 0},
            "business_intelligence_tier": {"services": 0, "healthy": 0},
            "development_tools_tier": {"services": 0, "healthy": 0},
            "infrastructure_tier": {"services": 0, "healthy": 0}
        }
    }
    
    # Process results by instance
    for ip, instance_info in service_map.items():
        instance_name = instance_info["name"]
        instance_results = connectivity_results.get(ip, [])
        
        instance_summary = {
            "name": instance_name,
            "ip": ip,
            "services": len(instance_info["strategic_services"]),
            "healthy": 0,
            "degraded": 0,
            "service_details": []
        }
        
        for service_config in instance_info["strategic_services"]:
            # Find corresponding status
            service_status = None
            for status in instance_results:
                if status["service"] == service_config["discovered_name"]:
                    service_status = status
                    break
            
            if service_status:
                detail = {
                    "strategic_name": service_config["strategic_name"],
                    "discovered_name": service_config["discovered_name"],
                    "strategic_port": service_config["port"],
                    "health_port": service_config["health_port"],
                    "tier": service_config["tier"],
                    "priority": service_config["priority"],
                    "status": service_status["overall_status"]
                }
                
                instance_summary["service_details"].append(detail)
                
                if service_status["overall_status"] == "HEALTHY":
                    instance_summary["healthy"] += 1
                    report["strategic_alignment"][service_config["tier"] + "_tier"]["healthy"] += 1
                else:
                    instance_summary["degraded"] += 1
                
                report["strategic_alignment"][service_config["tier"] + "_tier"]["services"] += 1
        
        report["instances"][ip] = instance_summary
        report["summary"]["total_services"] += instance_summary["services"]
        report["summary"]["healthy_services"] += instance_summary["healthy"]
        report["summary"]["degraded_services"] += instance_summary["degraded"]
    
    # Calculate success rate
    if report["summary"]["total_services"] > 0:
        report["summary"]["success_rate"] = (
            report["summary"]["healthy_services"] / report["summary"]["total_services"] * 100
        )
    
    # Save report
    report_path = Path("STRATEGIC_MCP_ACTIVATION_REPORT.json")
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    logger.info(f"📊 Strategic activation report saved: {report_path}")
    return report

def main():
    """Main strategic service activation function"""
    
    logger.info("🚀 Starting Strategic MCP Service Activation")
    logger.info("🎯 Using strategically aligned port assignments")
    
    # Load master port registry
    registry = load_master_port_registry()
    
    # Map discovered services to strategic ports
    service_map = map_discovered_services_to_strategic_ports(registry)
    
    # Start services with strategic configuration
    total_started = 0
    total_failed = 0
    
    for ip, instance_info in service_map.items():
        instance_name = instance_info["name"]
        strategic_services = instance_info["strategic_services"]
        
        logger.info(f"\n{'='*60}")
        logger.info(f"🔧 Configuring {instance_name} ({ip})")
        logger.info(f"   Services: {len(strategic_services)}")
        logger.info(f"{'='*60}")
        
        for service_config in strategic_services:
            if start_strategic_service(ip, service_config):
                total_started += 1
            else:
                total_failed += 1
    
    # Test strategic connectivity
    connectivity_results = test_strategic_connectivity(service_map)
    
    # Generate comprehensive report
    report = generate_strategic_activation_report(service_map, connectivity_results)
    
    # Final summary
    success_rate = report["summary"]["success_rate"]
    
    logger.info(f"\n{'='*60}")
    logger.info("📊 STRATEGIC MCP ACTIVATION SUMMARY")
    logger.info(f"{'='*60}")
    logger.info(f"✅ Services Started: {total_started}")
    logger.info(f"❌ Services Failed: {total_failed}")
    logger.info(f"📈 Success Rate: {success_rate:.1f}%")
    
    # Tier-wise summary
    for tier_name, tier_stats in report["strategic_alignment"].items():
        if tier_stats["services"] > 0:
            tier_success = (tier_stats["healthy"] / tier_stats["services"] * 100)
            logger.info(f"🏭 {tier_name.replace('_', ' ').title()}: {tier_stats['healthy']}/{tier_stats['services']} ({tier_success:.1f}%)")
    
    if success_rate >= 70:
        logger.info("\n🎉 STRATEGIC MCP ACTIVATION SUCCESSFUL!")
        logger.info("🚀 Sophia AI is now strategically aligned and operational!")
        return True
    else:
        logger.warning("\n⚠️  Some services need attention, proceeding with Phase 2 alignment")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 