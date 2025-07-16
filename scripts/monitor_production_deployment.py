#!/usr/bin/env python3
"""
🔍 PRODUCTION DEPLOYMENT MONITORING SCRIPT
==========================================
Monitor and validate Sophia AI distributed systemd infrastructure.

This script monitors the ACTUAL production infrastructure:
- 5 Lambda Labs instances with direct Python processes
- systemd service management and health monitoring
- nginx load balancing with upstream configuration
- Direct inter-instance HTTP communication on ports 8000-8499

USAGE:
    python scripts/monitor_production_deployment.py                    # Full monitoring
    python scripts/monitor_production_deployment.py --instance ai_core # Monitor specific instance
    python scripts/monitor_production_deployment.py --services-only    # Monitor services only
    python scripts/monitor_production_deployment.py --continuous       # Continuous monitoring
"""

import asyncio
import asyncssh
import aiohttp
import sys
import os
import json
import time
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import logging
from datetime import datetime

# Add project root to path for imports
sys.path.append(str(Path(__file__).parent.parent))
from infrastructure.config.production import (
    PRODUCTION_INFRASTRUCTURE,
    get_all_service_endpoints
)

# 🔧 LOGGING CONFIGURATION
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class ServiceHealth:
    """Health status of a service"""
    name: str
    endpoint: str
    status: str  # healthy, unhealthy, unreachable
    response_time_ms: Optional[float]
    status_code: Optional[int]
    error_message: Optional[str]
    timestamp: str

@dataclass
class InstanceHealth:
    """Health status of an instance"""
    name: str
    ip: str
    ssh_accessible: bool
    systemd_services: Dict[str, str]  # service_name -> status
    load_average: Optional[Tuple[float, float, float]]
    disk_usage: Optional[float]
    memory_usage: Optional[float]
    uptime: Optional[str]
    timestamp: str

@dataclass
class MonitoringReport:
    """Complete monitoring report"""
    timestamp: str
    overall_health: str
    service_health: List[ServiceHealth]
    instance_health: List[InstanceHealth]
    nginx_status: Optional[Dict]
    summary: Dict[str, any]

class ProductionMonitor:
    """Monitor distributed systemd production infrastructure"""
    
    def __init__(self, ssh_key_path: str = "~/.ssh/lambda_labs_key"):
        self.ssh_key_path = os.path.expanduser(ssh_key_path)
        self.monitoring_start = time.time()
        
        logger.info("🔍 Initializing Production Infrastructure Monitor")
        logger.info(f"📊 Monitoring {len(PRODUCTION_INFRASTRUCTURE.instances)} instances")
        logger.info(f"🔑 SSH Key: {self.ssh_key_path}")
    
    async def monitor_all(self) -> MonitoringReport:
        """Perform complete monitoring of all infrastructure"""
        logger.info("🌐 Starting comprehensive infrastructure monitoring...")
        
        # Monitor services via HTTP health checks
        service_health = await self.monitor_services()
        
        # Monitor instances via SSH
        instance_health = await self.monitor_instances()
        
        # Monitor nginx load balancer
        nginx_status = await self.monitor_nginx_load_balancer()
        
        # Generate overall health assessment
        overall_health = self.assess_overall_health(service_health, instance_health)
        
        # Create summary
        summary = self.generate_summary(service_health, instance_health, nginx_status)
        
        report = MonitoringReport(
            timestamp=datetime.now().isoformat(),
            overall_health=overall_health,
            service_health=service_health,
            instance_health=instance_health,
            nginx_status=nginx_status,
            summary=summary
        )
        
        return report
    
    async def monitor_services(self) -> List[ServiceHealth]:
        """Monitor all service health endpoints"""
        logger.info("🔍 Monitoring service health endpoints...")
        
        service_health = []
        endpoints = get_all_service_endpoints()
        
        # Create HTTP session for health checks
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            
            # Create tasks for parallel health checks
            tasks = []
            for service_name, endpoint in endpoints.items():
                task = self.check_service_health(session, service_name, endpoint)
                tasks.append(task)
            
            # Execute all health checks in parallel
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"❌ Service monitoring error: {result}")
                else:
                    service_health.append(result)
        
        # Log service health summary
        healthy_services = len([s for s in service_health if s.status == "healthy"])
        total_services = len(service_health)
        logger.info(f"📊 Service Health: {healthy_services}/{total_services} healthy")
        
        return service_health
    
    async def check_service_health(self, session: aiohttp.ClientSession, 
                                 service_name: str, endpoint: str) -> ServiceHealth:
        """Check health of a specific service"""
        health_url = f"{endpoint}/health"
        start_time = time.time()
        
        try:
            async with session.get(health_url) as response:
                response_time_ms = (time.time() - start_time) * 1000
                
                if response.status == 200:
                    status = "healthy"
                    error_message = None
                    logger.info(f"✅ {service_name}: {endpoint} - Healthy ({response_time_ms:.1f}ms)")
                else:
                    status = "unhealthy"
                    error_message = f"HTTP {response.status}"
                    logger.warning(f"⚠️ {service_name}: {endpoint} - Status {response.status}")
                
                return ServiceHealth(
                    name=service_name,
                    endpoint=endpoint,
                    status=status,
                    response_time_ms=response_time_ms,
                    status_code=response.status,
                    error_message=error_message,
                    timestamp=datetime.now().isoformat()
                )
                
        except Exception as e:
            response_time_ms = (time.time() - start_time) * 1000
            logger.error(f"❌ {service_name}: {endpoint} - Error: {e}")
            
            return ServiceHealth(
                name=service_name,
                endpoint=endpoint,
                status="unreachable",
                response_time_ms=response_time_ms,
                status_code=None,
                error_message=str(e),
                timestamp=datetime.now().isoformat()
            )
    
    async def monitor_instances(self) -> List[InstanceHealth]:
        """Monitor all Lambda Labs instances via SSH"""
        logger.info("🔍 Monitoring Lambda Labs instances via SSH...")
        
        instance_health = []
        
        # Create tasks for parallel instance monitoring
        tasks = []
        for instance_name, instance_config in PRODUCTION_INFRASTRUCTURE.instances.items():
            task = self.monitor_instance(instance_name, instance_config)
            tasks.append(task)
        
        # Execute all instance monitoring in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"❌ Instance monitoring error: {result}")
            else:
                instance_health.append(result)
        
        # Log instance health summary
        accessible_instances = len([i for i in instance_health if i.ssh_accessible])
        total_instances = len(instance_health)
        logger.info(f"📊 Instance Health: {accessible_instances}/{total_instances} accessible")
        
        return instance_health
    
    async def monitor_instance(self, instance_name: str, instance_config) -> InstanceHealth:
        """Monitor a specific Lambda Labs instance"""
        logger.info(f"🔍 Monitoring {instance_name} ({instance_config.ip})...")
        
        try:
            async with asyncssh.connect(
                instance_config.ip,
                username=instance_config.ssh_user,
                client_keys=[self.ssh_key_path],
                known_hosts=None,
                connect_timeout=15
            ) as conn:
                
                # Check systemd services
                systemd_services = await self.check_systemd_services(conn, instance_config.services)
                
                # Get system metrics
                load_average = await self.get_load_average(conn)
                disk_usage = await self.get_disk_usage(conn)
                memory_usage = await self.get_memory_usage(conn)
                uptime = await self.get_uptime(conn)
                
                logger.info(f"✅ {instance_name}: SSH accessible, {len(systemd_services)} services checked")
                
                return InstanceHealth(
                    name=instance_name,
                    ip=instance_config.ip,
                    ssh_accessible=True,
                    systemd_services=systemd_services,
                    load_average=load_average,
                    disk_usage=disk_usage,
                    memory_usage=memory_usage,
                    uptime=uptime,
                    timestamp=datetime.now().isoformat()
                )
                
        except Exception as e:
            logger.error(f"❌ {instance_name}: SSH connection failed - {e}")
            
            return InstanceHealth(
                name=instance_name,
                ip=instance_config.ip,
                ssh_accessible=False,
                systemd_services={},
                load_average=None,
                disk_usage=None,
                memory_usage=None,
                uptime=None,
                timestamp=datetime.now().isoformat()
            )
    
    async def check_systemd_services(self, conn, services: List[str]) -> Dict[str, str]:
        """Check status of systemd services on an instance"""
        systemd_services = {}
        
        for service_name in services:
            systemd_service_name = f"sophia-{service_name}"
            
            try:
                # Check if service exists and its status
                result = await conn.run(f"sudo systemctl is-active {systemd_service_name}")
                status = result.stdout.strip()
                systemd_services[service_name] = status
                
                if status == "active":
                    logger.info(f"  ✅ {systemd_service_name}: active")
                else:
                    logger.warning(f"  ⚠️ {systemd_service_name}: {status}")
                    
            except Exception as e:
                systemd_services[service_name] = "error"
                logger.error(f"  ❌ {systemd_service_name}: {e}")
        
        return systemd_services
    
    async def get_load_average(self, conn) -> Optional[Tuple[float, float, float]]:
        """Get system load average"""
        try:
            result = await conn.run("cat /proc/loadavg")
            load_parts = result.stdout.strip().split()
            return (float(load_parts[0]), float(load_parts[1]), float(load_parts[2]))
        except Exception:
            return None
    
    async def get_disk_usage(self, conn) -> Optional[float]:
        """Get disk usage percentage"""
        try:
            result = await conn.run("df / | tail -1 | awk '{print $5}' | sed 's/%//'")
            return float(result.stdout.strip())
        except Exception:
            return None
    
    async def get_memory_usage(self, conn) -> Optional[float]:
        """Get memory usage percentage"""
        try:
            result = await conn.run("free | grep Mem | awk '{printf \"%.1f\", $3/$2 * 100.0}'")
            return float(result.stdout.strip())
        except Exception:
            return None
    
    async def get_uptime(self, conn) -> Optional[str]:
        """Get system uptime"""
        try:
            result = await conn.run("uptime -p")
            return result.stdout.strip()
        except Exception:
            return None
    
    async def monitor_nginx_load_balancer(self) -> Optional[Dict]:
        """Monitor nginx load balancer on primary instance"""
        logger.info("🌐 Monitoring nginx load balancer...")
        
        primary_ip = PRODUCTION_INFRASTRUCTURE.nginx_primary
        
        try:
            timeout = aiohttp.ClientTimeout(total=10)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                
                # Test nginx health endpoint
                health_url = f"http://{primary_ip}/health"
                start_time = time.time()
                
                async with session.get(health_url) as response:
                    response_time_ms = (time.time() - start_time) * 1000
                    
                    nginx_status = {
                        "endpoint": health_url,
                        "status_code": response.status,
                        "response_time_ms": response_time_ms,
                        "healthy": response.status == 200,
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    if response.status == 200:
                        logger.info(f"✅ nginx load balancer: Healthy ({response_time_ms:.1f}ms)")
                    else:
                        logger.warning(f"⚠️ nginx load balancer: Status {response.status}")
                    
                    return nginx_status
                    
        except Exception as e:
            logger.error(f"❌ nginx load balancer: Error - {e}")
            
            return {
                "endpoint": f"http://{primary_ip}/health",
                "status_code": None,
                "response_time_ms": None,
                "healthy": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def assess_overall_health(self, service_health: List[ServiceHealth], 
                            instance_health: List[InstanceHealth]) -> str:
        """Assess overall infrastructure health"""
        
        # Service health metrics
        total_services = len(service_health)
        healthy_services = len([s for s in service_health if s.status == "healthy"])
        service_health_rate = (healthy_services / total_services) * 100 if total_services > 0 else 0
        
        # Instance health metrics
        total_instances = len(instance_health)
        accessible_instances = len([i for i in instance_health if i.ssh_accessible])
        instance_health_rate = (accessible_instances / total_instances) * 100 if total_instances > 0 else 0
        
        # systemd service metrics
        total_systemd_services = 0
        active_systemd_services = 0
        
        for instance in instance_health:
            for service_name, status in instance.systemd_services.items():
                total_systemd_services += 1
                if status == "active":
                    active_systemd_services += 1
        
        systemd_health_rate = (active_systemd_services / total_systemd_services) * 100 if total_systemd_services > 0 else 0
        
        # Overall assessment
        overall_score = (service_health_rate + instance_health_rate + systemd_health_rate) / 3
        
        if overall_score >= 90:
            return "excellent"
        elif overall_score >= 75:
            return "good"
        elif overall_score >= 60:
            return "fair"
        elif overall_score >= 40:
            return "poor"
        else:
            return "critical"
    
    def generate_summary(self, service_health: List[ServiceHealth], 
                        instance_health: List[InstanceHealth],
                        nginx_status: Optional[Dict]) -> Dict[str, any]:
        """Generate monitoring summary"""
        
        # Service metrics
        total_services = len(service_health)
        healthy_services = len([s for s in service_health if s.status == "healthy"])
        avg_response_time = sum(s.response_time_ms for s in service_health if s.response_time_ms) / len([s for s in service_health if s.response_time_ms]) if service_health else 0
        
        # Instance metrics
        total_instances = len(instance_health)
        accessible_instances = len([i for i in instance_health if i.ssh_accessible])
        
        # systemd metrics
        systemd_summary = {}
        for instance in instance_health:
            systemd_summary[instance.name] = {
                "total": len(instance.systemd_services),
                "active": len([s for s in instance.systemd_services.values() if s == "active"]),
                "inactive": len([s for s in instance.systemd_services.values() if s != "active"])
            }
        
        return {
            "service_metrics": {
                "total": total_services,
                "healthy": healthy_services,
                "unhealthy": total_services - healthy_services,
                "health_rate": round((healthy_services / total_services) * 100, 1) if total_services > 0 else 0,
                "avg_response_time_ms": round(avg_response_time, 1)
            },
            "instance_metrics": {
                "total": total_instances,
                "accessible": accessible_instances,
                "inaccessible": total_instances - accessible_instances,
                "accessibility_rate": round((accessible_instances / total_instances) * 100, 1) if total_instances > 0 else 0
            },
            "systemd_metrics": systemd_summary,
            "nginx_status": nginx_status,
            "monitoring_duration_seconds": round(time.time() - self.monitoring_start, 2)
        }
    
    def print_report(self, report: MonitoringReport):
        """Print formatted monitoring report"""
        print("\n" + "="*70)
        print("🔍 SOPHIA AI PRODUCTION INFRASTRUCTURE MONITORING REPORT")
        print("="*70)
        print(f"📅 Timestamp: {report.timestamp}")
        print(f"🎯 Overall Health: {report.overall_health.upper()}")
        print(f"⏱️  Monitoring Duration: {report.summary['monitoring_duration_seconds']}s")
        
        # Service Health Summary
        print("\n📊 SERVICE HEALTH SUMMARY")
        print(f"  Total Services: {report.summary['service_metrics']['total']}")
        print(f"  Healthy: {report.summary['service_metrics']['healthy']}")
        print(f"  Unhealthy: {report.summary['service_metrics']['unhealthy']}")
        print(f"  Health Rate: {report.summary['service_metrics']['health_rate']}%")
        print(f"  Avg Response: {report.summary['service_metrics']['avg_response_time_ms']}ms")
        
        # Instance Health Summary
        print("\n🖥️  INSTANCE HEALTH SUMMARY")
        print(f"  Total Instances: {report.summary['instance_metrics']['total']}")
        print(f"  Accessible: {report.summary['instance_metrics']['accessible']}")
        print(f"  Inaccessible: {report.summary['instance_metrics']['inaccessible']}")
        print(f"  Accessibility Rate: {report.summary['instance_metrics']['accessibility_rate']}%")
        
        # Service Details
        print("\n🔍 SERVICE HEALTH DETAILS")
        for service in report.service_health:
            status_icon = "✅" if service.status == "healthy" else "❌" if service.status == "unhealthy" else "⚠️"
            response_time = f"({service.response_time_ms:.1f}ms)" if service.response_time_ms else ""
            print(f"  {status_icon} {service.name}: {service.status} {response_time}")
            if service.error_message:
                print(f"    Error: {service.error_message}")
        
        # Instance Details
        print("\n🖥️  INSTANCE HEALTH DETAILS")
        for instance in report.instance_health:
            ssh_icon = "✅" if instance.ssh_accessible else "❌"
            print(f"  {ssh_icon} {instance.name} ({instance.ip})")
            
            if instance.ssh_accessible:
                if instance.load_average:
                    print(f"    Load: {instance.load_average[0]:.2f}, {instance.load_average[1]:.2f}, {instance.load_average[2]:.2f}")
                if instance.memory_usage:
                    print(f"    Memory: {instance.memory_usage:.1f}%")
                if instance.disk_usage:
                    print(f"    Disk: {instance.disk_usage:.1f}%")
                if instance.uptime:
                    print(f"    Uptime: {instance.uptime}")
                
                # systemd services
                active_services = len([s for s in instance.systemd_services.values() if s == "active"])
                total_services = len(instance.systemd_services)
                print(f"    systemd Services: {active_services}/{total_services} active")
                
                for service_name, status in instance.systemd_services.items():
                    service_icon = "✅" if status == "active" else "❌"
                    print(f"      {service_icon} sophia-{service_name}: {status}")
        
        # nginx Status
        print("\n🌐 NGINX LOAD BALANCER")
        if report.nginx_status:
            nginx_icon = "✅" if report.nginx_status.get("healthy") else "❌"
            response_time = f"({report.nginx_status.get('response_time_ms', 0):.1f}ms)" if report.nginx_status.get('response_time_ms') else ""
            print(f"  {nginx_icon} Load Balancer: {'Healthy' if report.nginx_status.get('healthy') else 'Unhealthy'} {response_time}")
            if not report.nginx_status.get("healthy") and report.nginx_status.get("error"):
                print(f"    Error: {report.nginx_status['error']}")
        else:
            print("  ❌ Load Balancer: Not monitored")
        
        print("="*70)
    
    def save_report(self, report: MonitoringReport, filename: Optional[str] = None):
        """Save monitoring report to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"monitoring_report_{timestamp}.json"
        
        report_dict = asdict(report)
        
        with open(filename, 'w') as f:
            json.dump(report_dict, f, indent=2)
        
        logger.info(f"📋 Monitoring report saved: {filename}")

async def main():
    """Main monitoring function"""
    parser = argparse.ArgumentParser(description="Monitor Sophia AI production infrastructure")
    parser.add_argument("--instance", help="Monitor specific instance only")
    parser.add_argument("--services-only", action="store_true", help="Monitor services only (no SSH)")
    parser.add_argument("--continuous", action="store_true", help="Continuous monitoring")
    parser.add_argument("--interval", type=int, default=60, help="Monitoring interval in seconds (for continuous mode)")
    parser.add_argument("--output", help="Save report to file")
    parser.add_argument("--ssh-key", default="~/.ssh/lambda_labs_key", help="SSH key path")
    
    args = parser.parse_args()
    
    monitor = ProductionMonitor(ssh_key_path=args.ssh_key)
    
    try:
        if args.continuous:
            logger.info(f"🔄 Starting continuous monitoring (interval: {args.interval}s)")
            while True:
                report = await monitor.monitor_all()
                monitor.print_report(report)
                
                if args.output:
                    monitor.save_report(report, args.output)
                
                logger.info(f"⏱️  Next check in {args.interval} seconds...")
                await asyncio.sleep(args.interval)
        else:
            # Single monitoring run
            if args.services_only:
                logger.info("🔍 Monitoring services only...")
                service_health = await monitor.monitor_services()
                
                print("\n📊 SERVICE HEALTH SUMMARY")
                for service in service_health:
                    status_icon = "✅" if service.status == "healthy" else "❌"
                    response_time = f"({service.response_time_ms:.1f}ms)" if service.response_time_ms else ""
                    print(f"  {status_icon} {service.name}: {service.status} {response_time}")
            
            elif args.instance:
                if args.instance not in PRODUCTION_INFRASTRUCTURE.instances:
                    logger.error(f"❌ Unknown instance: {args.instance}")
                    sys.exit(1)
                
                logger.info(f"🎯 Monitoring specific instance: {args.instance}")
                instance_config = PRODUCTION_INFRASTRUCTURE.instances[args.instance]
                instance_health = await monitor.monitor_instance(args.instance, instance_config)
                
                print(f"\n🖥️  INSTANCE HEALTH: {args.instance}")
                ssh_icon = "✅" if instance_health.ssh_accessible else "❌"
                print(f"  {ssh_icon} SSH: {'Accessible' if instance_health.ssh_accessible else 'Not accessible'}")
                
                if instance_health.ssh_accessible:
                    for service_name, status in instance_health.systemd_services.items():
                        service_icon = "✅" if status == "active" else "❌"
                        print(f"    {service_icon} sophia-{service_name}: {status}")
            
            else:
                # Full monitoring
                report = await monitor.monitor_all()
                monitor.print_report(report)
                
                if args.output:
                    monitor.save_report(report, args.output)
                
                # Exit with appropriate code based on health
                if report.overall_health in ["excellent", "good"]:
                    sys.exit(0)
                elif report.overall_health == "fair":
                    sys.exit(1)
                else:
                    sys.exit(2)
    
    except KeyboardInterrupt:
        logger.info("🛑 Monitoring interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Monitoring failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 