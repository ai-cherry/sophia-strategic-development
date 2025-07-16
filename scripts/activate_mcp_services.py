#!/usr/bin/env python3
"""
Activate Sophia AI MCP Services
Properly starts all MCP services across Lambda Labs instances with specific service names

This script:
1. Lists available systemd services on each instance
2. Starts specific MCP services (not glob patterns)
3. Validates service health and connectivity
4. Provides detailed status reporting

Usage: python scripts/activate_mcp_services.py [--instance=all|core|orchestrator|pipeline|dev|production]
"""

import subprocess
import sys
import json
import logging
from typing import Dict, List
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Instance configuration
INSTANCES = {
    "core": {
        "ip": "192.222.58.232",
        "name": "sophia-ai-core",
        "services": ["sophia-vector-search-mcp", "sophia-real-time-chat-mcp", "sophia-ai-memory-mcp"]
    },
    "orchestrator": {
        "ip": "104.171.202.117", 
        "name": "sophia-mcp-orchestrator",
        "services": ["sophia-gong-mcp", "sophia-hubspot-mcp", "sophia-linear-mcp", "sophia-asana-mcp"]
    },
    "pipeline": {
        "ip": "104.171.202.134",
        "name": "sophia-data-pipeline", 
        "services": ["sophia-github-mcp", "sophia-notion-mcp", "sophia-slack-mcp", "sophia-postgres-mcp"]
    },
    "dev": {
        "ip": "155.248.194.183",
        "name": "sophia-development",
        "services": ["sophia-filesystem-mcp", "sophia-brave-search-mcp", "sophia-everything-mcp"]
    },
    "production": {
        "ip": "104.171.202.103",
        "name": "sophia-production-instance", 
        "services": ["sophia-legacy-support-mcp"]
    }
}

def run_ssh_command(ip: str, command: str, timeout: int = 30) -> tuple[bool, str, str]:
    """Execute SSH command on remote instance"""
    ssh_cmd = [
        "ssh", "-o", "StrictHostKeyChecking=no",
        "-o", "ConnectTimeout=10",
        "-o", "ServerAliveInterval=10",
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

def list_available_services(ip: str) -> List[str]:
    """List all available sophia systemd services on an instance"""
    logger.info(f"🔍 Discovering services on {ip}")
    
    success, stdout, stderr = run_ssh_command(
        ip, 
        "sudo systemctl list-unit-files | grep sophia | grep .service"
    )
    
    if not success:
        logger.warning(f"Failed to list services on {ip}: {stderr}")
        return []
    
    services = []
    for line in stdout.strip().split('\n'):
        if line and 'sophia' in line and '.service' in line:
            service_name = line.split()[0].replace('.service', '')
            services.append(service_name)
    
    logger.info(f"📋 Found {len(services)} services on {ip}: {services}")
    return services

def start_service(ip: str, service_name: str) -> bool:
    """Start a specific systemd service"""
    logger.info(f"🚀 Starting {service_name} on {ip}")
    
    # First check if service exists
    success, stdout, stderr = run_ssh_command(
        ip,
        f"sudo systemctl list-unit-files {service_name}.service"
    )
    
    if not success or service_name not in stdout:
        logger.warning(f"⚠️  Service {service_name} not found on {ip}")
        return False
    
    # Start the service
    success, stdout, stderr = run_ssh_command(
        ip,
        f"sudo systemctl start {service_name}.service"
    )
    
    if success:
        logger.info(f"✅ Started {service_name} on {ip}")
        return True
    else:
        logger.error(f"❌ Failed to start {service_name} on {ip}: {stderr}")
        return False

def check_service_status(ip: str, service_name: str) -> Dict:
    """Check the status of a specific service"""
    success, stdout, stderr = run_ssh_command(
        ip,
        f"sudo systemctl is-active {service_name}.service"
    )
    
    active = stdout.strip() == "active"
    
    # Get detailed status
    success2, stdout2, stderr2 = run_ssh_command(
        ip,
        f"sudo systemctl status {service_name}.service --no-pager -l"
    )
    
    return {
        "name": service_name,
        "active": active,
        "status": stdout.strip(),
        "details": stdout2 if success2 else stderr2
    }

def check_port_connectivity(ip: str, port: int) -> bool:
    """Check if a port is responding on an instance"""
    try:
        result = subprocess.run(
            ["nc", "-z", "-w", "5", ip, str(port)],
            capture_output=True,
            timeout=10
        )
        return result.returncode == 0
    except:
        return False

def activate_instance_services(instance_key: str) -> Dict:
    """Activate all services for a specific instance"""
    instance = INSTANCES[instance_key]
    ip = instance["ip"]
    name = instance["name"]
    expected_services = instance["services"]
    
    logger.info(f"🔧 Activating services on {name} ({ip})")
    
    # Discover available services
    available_services = list_available_services(ip)
    
    # Start services
    results = {
        "instance": name,
        "ip": ip,
        "expected_services": expected_services,
        "available_services": available_services,
        "started_services": [],
        "failed_services": [],
        "service_status": []
    }
    
    for service in expected_services:
        if service in available_services:
            if start_service(ip, service):
                results["started_services"].append(service)
            else:
                results["failed_services"].append(service)
        else:
            logger.warning(f"⚠️  Expected service {service} not available on {ip}")
            results["failed_services"].append(service)
    
    # Check status of all services
    for service in available_services:
        if 'sophia' in service:
            status = check_service_status(ip, service)
            results["service_status"].append(status)
    
    return results

def test_service_endpoints(instance_key: str) -> Dict:
    """Test connectivity to service endpoints"""
    instance = INSTANCES[instance_key]
    ip = instance["ip"]
    
    # Define port ranges for each instance
    port_ranges = {
        "core": [8001, 8002, 8101],
        "orchestrator": [8110, 8111, 8112, 8113],
        "pipeline": [8210, 8211, 8212, 8213],
        "dev": [8310, 8311, 8312],
        "production": [8410]
    }
    
    ports = port_ranges.get(instance_key, [])
    connectivity_results = {}
    
    logger.info(f"🔗 Testing connectivity to {ip}")
    
    for port in ports:
        connected = check_port_connectivity(ip, port)
        connectivity_results[port] = connected
        status = "✅" if connected else "❌"
        logger.info(f"   Port {port}: {status}")
    
    return connectivity_results

def validate_qdrant_connection() -> bool:
    """Validate Qdrant connectivity"""
    logger.info("🔍 Testing Qdrant connectivity")
    
    try:
        result = subprocess.run(
            [sys.executable, "scripts/validate_qdrant_connection.py"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        success = "Connection successful" in result.stdout
        if success:
            logger.info("✅ Qdrant connection successful")
        else:
            logger.warning(f"⚠️  Qdrant connection issues: {result.stdout}")
        
        return success
    except Exception as e:
        logger.error(f"❌ Qdrant validation error: {e}")
        return False

def main():
    """Main activation function"""
    logger.info("🚀 Starting Sophia AI MCP Services Activation")
    
    activation_results = {}
    connectivity_results = {}
    
    # Activate services on all instances
    for instance_key in INSTANCES.keys():
        try:
            logger.info(f"\n{'='*50}")
            logger.info(f"🔧 Processing {instance_key.upper()} instance")
            logger.info(f"{'='*50}")
            
            # Activate services
            result = activate_instance_services(instance_key)
            activation_results[instance_key] = result
            
            # Test connectivity
            connectivity = test_service_endpoints(instance_key)
            connectivity_results[instance_key] = connectivity
            
            # Summary for this instance
            started = len(result["started_services"])
            failed = len(result["failed_services"])
            logger.info(f"📊 {instance_key.upper()} Summary: {started} started, {failed} failed")
            
        except Exception as e:
            logger.error(f"❌ Error processing {instance_key}: {e}")
            activation_results[instance_key] = {"error": str(e)}
    
    # Test Qdrant connectivity
    logger.info(f"\n{'='*50}")
    logger.info("🔍 Testing External Services")
    logger.info(f"{'='*50}")
    
    qdrant_ok = validate_qdrant_connection()
    
    # Generate final report
    logger.info(f"\n{'='*50}")
    logger.info("📊 FINAL ACTIVATION REPORT")
    logger.info(f"{'='*50}")
    
    total_started = 0
    total_failed = 0
    
    for instance_key, result in activation_results.items():
        if "error" not in result:
            started = len(result["started_services"])
            failed = len(result["failed_services"])
            total_started += started
            total_failed += failed
            
            logger.info(f"🏭 {instance_key.upper()}: {started}/{started + failed} services active")
        else:
            logger.error(f"❌ {instance_key.upper()}: {result['error']}")
    
    logger.info("\n🎯 OVERALL STATUS:")
    logger.info(f"   ✅ Services Started: {total_started}")
    logger.info(f"   ❌ Services Failed: {total_failed}")
    logger.info(f"   🔗 Qdrant Connection: {'✅' if qdrant_ok else '❌'}")
    
    success_rate = (total_started / (total_started + total_failed) * 100) if (total_started + total_failed) > 0 else 0
    logger.info(f"   📈 Success Rate: {success_rate:.1f}%")
    
    # Save detailed report
    report = {
        "timestamp": datetime.now().isoformat(),
        "activation_results": activation_results,
        "connectivity_results": connectivity_results,
        "qdrant_connection": qdrant_ok,
        "summary": {
            "total_started": total_started,
            "total_failed": total_failed,
            "success_rate": success_rate
        }
    }
    
    report_path = "mcp_activation_report.json"
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    logger.info(f"📄 Detailed report saved to {report_path}")
    
    if success_rate >= 80:
        logger.info("🎉 MCP ACTIVATION SUCCESSFUL!")
        return True
    else:
        logger.warning("⚠️  MCP activation needs attention")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 