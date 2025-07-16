#!/usr/bin/env python3
"""
Start Discovered MCP Services
Based on the service discovery results, start the services that actually exist on each instance

Discovered Services by Instance:
- Core (192.222.58.232): sophia-vector_search_mcp, sophia-real_time_chat_mcp, sophia-ai_memory_mcp
- Orchestrator (104.171.202.117): sophia-asana_mcp, sophia-gong_mcp, sophia-hubspot_mcp, sophia-linear_mcp  
- Pipeline (104.171.202.134): sophia-github_mcp, sophia-notion_mcp, sophia-postgres_mcp, sophia-slack_mcp
- Dev (155.248.194.183): sophia-brave_search_mcp, sophia-everything_mcp, sophia-filesystem_mcp
- Production (104.171.202.103): sophia-legacy_support_mcp
"""

import subprocess
import sys
import logging
from typing import Dict

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Services that actually exist on each instance (discovered from previous run)
DISCOVERED_SERVICES = {
    "192.222.58.232": {  # Core
        "name": "sophia-ai-core",
        "services": ["sophia-vector_search_mcp", "sophia-real_time_chat_mcp", "sophia-ai_memory_mcp"]
    },
    "104.171.202.117": {  # Orchestrator
        "name": "sophia-mcp-orchestrator", 
        "services": ["sophia-asana_mcp", "sophia-gong_mcp", "sophia-hubspot_mcp", "sophia-linear_mcp"]
    },
    "104.171.202.134": {  # Pipeline
        "name": "sophia-data-pipeline",
        "services": ["sophia-github_mcp", "sophia-notion_mcp", "sophia-postgres_mcp", "sophia-slack_mcp"]
    },
    "155.248.194.183": {  # Dev
        "name": "sophia-development",
        "services": ["sophia-brave_search_mcp", "sophia-everything_mcp", "sophia-filesystem_mcp"]
    },
    "104.171.202.103": {  # Production
        "name": "sophia-production-instance",
        "services": ["sophia-legacy_support_mcp"]
    }
}

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

def start_service(ip: str, service_name: str) -> bool:
    """Start a specific systemd service"""
    logger.info(f"🚀 Starting {service_name} on {ip}")
    
    success, stdout, stderr = run_ssh_command(
        ip,
        f"sudo systemctl start {service_name}.service"
    )
    
    if success:
        logger.info(f"✅ Started {service_name}")
        return True
    else:
        logger.error(f"❌ Failed to start {service_name}: {stderr}")
        return False

def enable_service(ip: str, service_name: str) -> bool:
    """Enable a service to start on boot"""
    logger.info(f"🔧 Enabling {service_name} on {ip}")
    
    success, stdout, stderr = run_ssh_command(
        ip,
        f"sudo systemctl enable {service_name}.service"
    )
    
    if success:
        logger.info(f"✅ Enabled {service_name}")
        return True
    else:
        logger.warning(f"⚠️  Failed to enable {service_name}: {stderr}")
        return False

def check_service_status(ip: str, service_name: str) -> str:
    """Check if service is active"""
    success, stdout, stderr = run_ssh_command(
        ip,
        f"sudo systemctl is-active {service_name}.service"
    )
    
    return stdout.strip() if success else "inactive"

def test_port_connectivity(ip: str, port: int) -> bool:
    """Test if port is responding"""
    try:
        result = subprocess.run(
            ["nc", "-z", "-w", "3", ip, str(port)],
            capture_output=True,
            timeout=5
        )
        return result.returncode == 0
    except:
        return False

def start_instance_services(ip: str) -> Dict:
    """Start all services for an instance"""
    instance_info = DISCOVERED_SERVICES[ip]
    instance_name = instance_info["name"]
    services = instance_info["services"]
    
    logger.info(f"\n{'='*60}")
    logger.info(f"🔧 Starting services on {instance_name} ({ip})")
    logger.info(f"{'='*60}")
    
    results = {
        "instance": instance_name,
        "ip": ip,
        "services": services,
        "started": [],
        "failed": [],
        "status": {}
    }
    
    for service in services:
        # Enable service first
        enable_service(ip, service)
        
        # Start service
        if start_service(ip, service):
            results["started"].append(service)
        else:
            results["failed"].append(service)
        
        # Check status
        status = check_service_status(ip, service)
        results["status"][service] = status
        
        logger.info(f"   {service}: {status}")
    
    return results

def test_connectivity() -> Dict:
    """Test connectivity to all instances"""
    logger.info(f"\n{'='*60}")
    logger.info("🔗 Testing Service Connectivity")
    logger.info(f"{'='*60}")
    
    # Port mappings for each instance
    port_mappings = {
        "192.222.58.232": [8001, 8002, 8101],      # Core
        "104.171.202.117": [8110, 8111, 8112, 8113],  # Orchestrator
        "104.171.202.134": [8210, 8211, 8212, 8213],  # Pipeline
        "155.248.194.183": [8310, 8311, 8312],        # Dev
        "104.171.202.103": [8410]                     # Production
    }
    
    connectivity_results = {}
    
    for ip, ports in port_mappings.items():
        instance_name = DISCOVERED_SERVICES[ip]["name"]
        logger.info(f"🔗 Testing {instance_name} ({ip})")
        
        instance_connectivity = {}
        for port in ports:
            connected = test_port_connectivity(ip, port)
            instance_connectivity[port] = connected
            status = "✅" if connected else "❌"
            logger.info(f"   Port {port}: {status}")
        
        connectivity_results[ip] = instance_connectivity
    
    return connectivity_results

def main():
    """Main function to start all discovered services"""
    logger.info("🚀 Starting All Discovered Sophia AI MCP Services")
    
    all_results = {}
    total_started = 0
    total_failed = 0
    
    # Start services on each instance
    for ip in DISCOVERED_SERVICES.keys():
        try:
            result = start_instance_services(ip)
            all_results[ip] = result
            
            started = len(result["started"])
            failed = len(result["failed"])
            total_started += started
            total_failed += failed
            
            logger.info(f"📊 {result['instance']}: {started}/{started + failed} services started")
            
        except Exception as e:
            logger.error(f"❌ Error processing {ip}: {e}")
            all_results[ip] = {"error": str(e)}
    
    # Test connectivity after starting services
    test_connectivity()
    
    # Final summary
    logger.info(f"\n{'='*60}")
    logger.info("📊 FINAL SERVICE ACTIVATION SUMMARY")
    logger.info(f"{'='*60}")
    
    logger.info(f"✅ Total Services Started: {total_started}")
    logger.info(f"❌ Total Services Failed: {total_failed}")
    
    if total_started + total_failed > 0:
        success_rate = (total_started / (total_started + total_failed)) * 100
        logger.info(f"📈 Success Rate: {success_rate:.1f}%")
    else:
        success_rate = 0
        logger.info("📈 Success Rate: 0.0%")
    
    # Show detailed status
    for ip, result in all_results.items():
        if "error" not in result:
            instance_name = result["instance"]
            logger.info(f"\n🏭 {instance_name}:")
            for service, status in result["status"].items():
                status_icon = "✅" if status == "active" else "❌"
                logger.info(f"   {service}: {status_icon} {status}")
    
    # Test nginx load balancer
    logger.info("\n🔧 Testing nginx Load Balancer")
    try:
        result = subprocess.run(
            ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", "http://192.222.58.232/health"],
            capture_output=True,
            text=True,
            timeout=10
        )
        status_code = result.stdout.strip()
        if status_code == "200":
            logger.info("✅ nginx Load Balancer: Healthy (200)")
        else:
            logger.info(f"🔧 nginx Load Balancer: {status_code} (may improve as services start)")
    except Exception as e:
        logger.warning(f"⚠️  nginx test failed: {e}")
    
    if success_rate >= 70:
        logger.info("\n🎉 MCP SERVICE ACTIVATION SUCCESSFUL!")
        logger.info("🚀 Sophia AI infrastructure is now operational!")
        return True
    else:
        logger.warning("\n⚠️  Some services need attention, but infrastructure is partially operational")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 