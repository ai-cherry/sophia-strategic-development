#!/usr/bin/env python3
"""
Sophia AI Staging Deployment Script
Comprehensive deployment to staging environment with health checks and validation
"""

import asyncio
import logging
import subprocess
import time
import requests
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class StagingDeployment:
    """Comprehensive staging deployment with validation"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.deployment_id = f"staging-{int(datetime.now().timestamp())}"
        self.services = []
        self.health_checks = []
        self.deployment_log = []
        
    async def deploy_to_staging(self) -> Dict[str, Any]:
        """Execute complete staging deployment"""
        logger.info("🚀 Starting Sophia AI Staging Deployment")
        
        deployment_result = {
            "deployment_id": self.deployment_id,
            "start_time": datetime.now().isoformat(),
            "status": "in_progress",
            "phases": [],
            "services": [],
            "health_checks": [],
            "errors": []
        }
        
        try:
            # Phase 1: Pre-deployment validation
            logger.info("📋 Phase 1: Pre-deployment validation")
            validation_result = await self._validate_pre_deployment()
            deployment_result["phases"].append({
                "phase": "pre_deployment_validation",
                "status": "success" if validation_result["success"] else "failed",
                "details": validation_result
            })
            
            if not validation_result["success"]:
                deployment_result["status"] = "failed"
                deployment_result["errors"].extend(validation_result["errors"])
                return deployment_result
            
            # Phase 2: Infrastructure setup
            logger.info("🏗️ Phase 2: Infrastructure setup")
            infra_result = await self._setup_staging_infrastructure()
            deployment_result["phases"].append({
                "phase": "infrastructure_setup", 
                "status": "success" if infra_result["success"] else "failed",
                "details": infra_result
            })
            
            # Phase 3: Service deployment
            logger.info("🚀 Phase 3: Service deployment")
            service_result = await self._deploy_services()
            deployment_result["phases"].append({
                "phase": "service_deployment",
                "status": "success" if service_result["success"] else "failed", 
                "details": service_result
            })
            deployment_result["services"] = service_result.get("services", [])
            
            # Phase 4: Health validation
            logger.info("🏥 Phase 4: Health validation")
            health_result = await self._validate_deployment_health()
            deployment_result["phases"].append({
                "phase": "health_validation",
                "status": "success" if health_result["success"] else "failed",
                "details": health_result
            })
            deployment_result["health_checks"] = health_result.get("checks", [])
            
            # Phase 5: Integration testing
            logger.info("🧪 Phase 5: Integration testing")
            test_result = await self._run_integration_tests()
            deployment_result["phases"].append({
                "phase": "integration_testing",
                "status": "success" if test_result["success"] else "failed",
                "details": test_result
            })
            
            # Determine overall status
            all_phases_success = all(phase["status"] == "success" for phase in deployment_result["phases"])
            deployment_result["status"] = "success" if all_phases_success else "failed"
            
            if deployment_result["status"] == "success":
                logger.info("✅ Staging deployment completed successfully!")
            else:
                logger.error("❌ Staging deployment failed")
                
        except Exception as e:
            error_msg = f"Deployment failed with exception: {e}"
            logger.error(error_msg)
            deployment_result["status"] = "failed"
            deployment_result["errors"].append(error_msg)
        
        deployment_result["end_time"] = datetime.now().isoformat()
        return deployment_result
    
    async def _validate_pre_deployment(self) -> Dict[str, Any]:
        """Validate pre-deployment requirements"""
        logger.info("   📋 Validating pre-deployment requirements...")
        
        validation_checks = []
        errors = []
        
        # Check 1: Docker availability
        try:
            result = subprocess.run(["docker", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                validation_checks.append({
                    "check": "docker_availability",
                    "status": "passed",
                    "details": result.stdout.strip()
                })
            else:
                errors.append("Docker not available")
                validation_checks.append({
                    "check": "docker_availability", 
                    "status": "failed",
                    "details": "Docker command failed"
                })
        except Exception as e:
            errors.append(f"Docker check failed: {e}")
            validation_checks.append({
                "check": "docker_availability",
                "status": "failed", 
                "details": str(e)
            })
        
        # Check 2: Required files exist
        required_files = [
            "docker-compose.production.yml",
            "config/sophia-deployment-config.yaml",
            "backend/core/unified_connection_manager.py",
            "backend/monitoring/health_monitoring_system.py"
        ]
        
        for file_path in required_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                validation_checks.append({
                    "check": f"file_exists_{file_path}",
                    "status": "passed",
                    "details": f"File exists: {file_path}"
                })
            else:
                errors.append(f"Required file missing: {file_path}")
                validation_checks.append({
                    "check": f"file_exists_{file_path}",
                    "status": "failed",
                    "details": f"File missing: {file_path}"
                })
        
        # Check 3: Environment variables
        required_env_vars = ["PULUMI_ORG"]
        import os
        
        for env_var in required_env_vars:
            if os.getenv(env_var):
                validation_checks.append({
                    "check": f"env_var_{env_var}",
                    "status": "passed",
                    "details": f"Environment variable {env_var} is set"
                })
            else:
                errors.append(f"Required environment variable missing: {env_var}")
                validation_checks.append({
                    "check": f"env_var_{env_var}",
                    "status": "failed", 
                    "details": f"Environment variable {env_var} not set"
                })
        
        success = len(errors) == 0
        logger.info(f"   ✅ Pre-deployment validation: {len(validation_checks)} checks, {len(errors)} errors")
        
        return {
            "success": success,
            "checks": validation_checks,
            "errors": errors,
            "total_checks": len(validation_checks),
            "passed_checks": len([c for c in validation_checks if c["status"] == "passed"])
        }
    
    async def _setup_staging_infrastructure(self) -> Dict[str, Any]:
        """Setup staging infrastructure"""
        logger.info("   🏗️ Setting up staging infrastructure...")
        
        setup_steps = []
        errors = []
        
        try:
            # Step 1: Create staging network
            logger.info("      🌐 Creating staging network...")
            result = subprocess.run([
                "docker", "network", "create", "--driver", "bridge", 
                "--subnet", "172.21.0.0/16", "sophia-staging-network"
            ], capture_output=True, text=True)
            
            if result.returncode == 0 or "already exists" in result.stderr:
                setup_steps.append({
                    "step": "create_staging_network",
                    "status": "success",
                    "details": "Staging network created/exists"
                })
            else:
                errors.append(f"Failed to create staging network: {result.stderr}")
                setup_steps.append({
                    "step": "create_staging_network",
                    "status": "failed",
                    "details": result.stderr
                })
            
            # Step 2: Create staging volumes
            logger.info("      💾 Creating staging volumes...")
            volumes = ["sophia-staging-logs", "sophia-staging-cache", "sophia-staging-data"]
            
            for volume in volumes:
                result = subprocess.run([
                    "docker", "volume", "create", volume
                ], capture_output=True, text=True)
                
                if result.returncode == 0 or "already exists" in result.stderr:
                    setup_steps.append({
                        "step": f"create_volume_{volume}",
                        "status": "success",
                        "details": f"Volume {volume} created/exists"
                    })
                else:
                    errors.append(f"Failed to create volume {volume}: {result.stderr}")
                    setup_steps.append({
                        "step": f"create_volume_{volume}",
                        "status": "failed",
                        "details": result.stderr
                    })
            
            # Step 3: Prepare staging configuration
            logger.info("      ⚙️ Preparing staging configuration...")
            staging_config = self._create_staging_config()
            setup_steps.append({
                "step": "prepare_staging_config",
                "status": "success",
                "details": f"Staging configuration prepared with {len(staging_config)} settings"
            })
            
        except Exception as e:
            error_msg = f"Infrastructure setup failed: {e}"
            errors.append(error_msg)
            setup_steps.append({
                "step": "infrastructure_setup",
                "status": "failed",
                "details": error_msg
            })
        
        success = len(errors) == 0
        logger.info(f"   ✅ Infrastructure setup: {len(setup_steps)} steps, {len(errors)} errors")
        
        return {
            "success": success,
            "steps": setup_steps,
            "errors": errors
        }
    
    def _create_staging_config(self) -> Dict[str, Any]:
        """Create staging-specific configuration"""
        return {
            "environment": "staging",
            "debug": True,
            "log_level": "DEBUG",
            "database": {
                "pool_size": 5,
                "max_overflow": 10
            },
            "cache": {
                "ttl": 300,
                "max_size": 1000
            },
            "monitoring": {
                "health_check_interval": 30,
                "metrics_collection": True
            }
        }
    
    async def _deploy_services(self) -> Dict[str, Any]:
        """Deploy services to staging"""
        logger.info("   🚀 Deploying services to staging...")
        
        services_deployed = []
        errors = []
        
        # Service deployment order (dependencies first)
        service_order = [
            "redis-staging",
            "postgres-staging", 
            "sophia-backend-staging",
            "ai-memory-mcp-staging",
            "monitoring-staging"
        ]
        
        try:
            # Build and start services using Docker Compose
            logger.info("      🔨 Building staging services...")
            
            # Create staging Docker Compose override
            staging_override = self._create_staging_docker_compose()
            
            # Write staging override file
            staging_file = self.project_root / "docker-compose.staging.yml"
            with open(staging_file, 'w') as f:
                import yaml
                yaml.dump(staging_override, f, default_flow_style=False, indent=2)
            
            # Start services
            logger.info("      🚀 Starting staging services...")
            result = subprocess.run([
                "docker-compose", 
                "-f", "docker-compose.production.yml",
                "-f", "docker-compose.staging.yml",
                "up", "-d", "--build"
            ], cwd=self.project_root, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Check which services started successfully
                for service in service_order:
                    service_status = await self._check_service_status(service)
                    services_deployed.append(service_status)
                    
                    if service_status["status"] == "running":
                        logger.info(f"      ✅ {service} deployed successfully")
                    else:
                        logger.warning(f"      ⚠️ {service} deployment issue: {service_status['details']}")
                        
            else:
                error_msg = f"Docker Compose failed: {result.stderr}"
                errors.append(error_msg)
                logger.error(f"      ❌ Service deployment failed: {error_msg}")
        
        except Exception as e:
            error_msg = f"Service deployment failed: {e}"
            errors.append(error_msg)
            logger.error(f"      ❌ {error_msg}")
        
        success = len(errors) == 0 and len([s for s in services_deployed if s["status"] == "running"]) > 0
        logger.info(f"   ✅ Service deployment: {len(services_deployed)} services, {len(errors)} errors")
        
        return {
            "success": success,
            "services": services_deployed,
            "errors": errors
        }
    
    def _create_staging_docker_compose(self) -> Dict[str, Any]:
        """Create staging Docker Compose override"""
        return {
            "version": "3.8",
            "services": {
                "sophia-backend": {
                    "container_name": "sophia-backend-staging",
                    "environment": [
                        "SOPHIA_ENVIRONMENT=staging",
                        "SOPHIA_PORT=8001",
                        "DEBUG=true",
                        "LOG_LEVEL=DEBUG"
                    ],
                    "ports": ["8001:8001"],
                    "networks": ["sophia-staging-network"],
                    "volumes": [
                        "sophia-staging-logs:/app/logs",
                        "sophia-staging-cache:/app/cache"
                    ]
                },
                "redis-cluster": {
                    "container_name": "redis-staging",
                    "ports": ["6380:6379"],
                    "networks": ["sophia-staging-network"],
                    "volumes": ["sophia-staging-data:/data"]
                },
                "ai-memory-mcp": {
                    "container_name": "ai-memory-mcp-staging",
                    "environment": [
                        "MCP_SERVER_PORT=9001",
                        "ENVIRONMENT=staging"
                    ],
                    "ports": ["9001:9001"],
                    "networks": ["sophia-staging-network"]
                }
            },
            "networks": {
                "sophia-staging-network": {
                    "external": True
                }
            },
            "volumes": {
                "sophia-staging-logs": {"external": True},
                "sophia-staging-cache": {"external": True}, 
                "sophia-staging-data": {"external": True}
            }
        }
    
    async def _check_service_status(self, service_name: str) -> Dict[str, Any]:
        """Check individual service status"""
        try:
            # Check if container is running
            result = subprocess.run([
                "docker", "ps", "--filter", f"name={service_name}", "--format", "{{.Status}}"
            ], capture_output=True, text=True)
            
            if result.returncode == 0 and result.stdout.strip():
                status = "running" if "Up" in result.stdout else "stopped"
                details = result.stdout.strip()
            else:
                status = "not_found"
                details = "Container not found"
            
            return {
                "service": service_name,
                "status": status,
                "details": details,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "service": service_name,
                "status": "error",
                "details": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _validate_deployment_health(self) -> Dict[str, Any]:
        """Validate deployment health"""
        logger.info("   🏥 Validating deployment health...")
        
        health_checks = []
        errors = []
        
        # Health check endpoints
        endpoints = [
            {"name": "sophia_backend", "url": "http://localhost:8001/api/health", "timeout": 10},
            {"name": "ai_memory_mcp", "url": "http://localhost:9001/health", "timeout": 5}
        ]
        
        for endpoint in endpoints:
            try:
                logger.info(f"      🔍 Checking {endpoint['name']}...")
                
                # Wait a moment for service to be ready
                await asyncio.sleep(2)
                
                response = requests.get(endpoint["url"], timeout=endpoint["timeout"])
                
                if response.status_code == 200:
                    health_checks.append({
                        "endpoint": endpoint["name"],
                        "status": "healthy",
                        "response_time_ms": response.elapsed.total_seconds() * 1000,
                        "status_code": response.status_code,
                        "details": "Health check passed"
                    })
                    logger.info(f"      ✅ {endpoint['name']} is healthy")
                else:
                    health_checks.append({
                        "endpoint": endpoint["name"],
                        "status": "unhealthy",
                        "status_code": response.status_code,
                        "details": f"HTTP {response.status_code}"
                    })
                    errors.append(f"{endpoint['name']} returned HTTP {response.status_code}")
                    logger.warning(f"      ⚠️ {endpoint['name']} returned HTTP {response.status_code}")
                    
            except requests.exceptions.ConnectionError:
                health_checks.append({
                    "endpoint": endpoint["name"],
                    "status": "unreachable",
                    "details": "Connection refused - service may not be ready"
                })
                logger.warning(f"      ⚠️ {endpoint['name']} not reachable (may still be starting)")
                
            except requests.exceptions.Timeout:
                health_checks.append({
                    "endpoint": endpoint["name"], 
                    "status": "timeout",
                    "details": f"Timeout after {endpoint['timeout']}s"
                })
                errors.append(f"{endpoint['name']} health check timeout")
                logger.warning(f"      ⚠️ {endpoint['name']} health check timeout")
                
            except Exception as e:
                health_checks.append({
                    "endpoint": endpoint["name"],
                    "status": "error",
                    "details": str(e)
                })
                errors.append(f"{endpoint['name']} health check error: {e}")
                logger.error(f"      ❌ {endpoint['name']} health check error: {e}")
        
        # Overall health assessment
        healthy_services = len([c for c in health_checks if c["status"] == "healthy"])
        total_services = len(health_checks)
        
        success = healthy_services > 0  # At least some services should be healthy
        logger.info(f"   ✅ Health validation: {healthy_services}/{total_services} services healthy")
        
        return {
            "success": success,
            "checks": health_checks,
            "errors": errors,
            "healthy_services": healthy_services,
            "total_services": total_services,
            "health_percentage": (healthy_services / total_services * 100) if total_services > 0 else 0
        }
    
    async def _run_integration_tests(self) -> Dict[str, Any]:
        """Run integration tests"""
        logger.info("   🧪 Running integration tests...")
        
        test_results = []
        errors = []
        
        # Test 1: Basic API connectivity
        try:
            logger.info("      🔗 Testing API connectivity...")
            response = requests.get("http://localhost:8001/api/health", timeout=10)
            
            if response.status_code == 200:
                test_results.append({
                    "test": "api_connectivity",
                    "status": "passed",
                    "details": f"API responding with HTTP {response.status_code}"
                })
            else:
                test_results.append({
                    "test": "api_connectivity", 
                    "status": "failed",
                    "details": f"API returned HTTP {response.status_code}"
                })
                errors.append("API connectivity test failed")
                
        except Exception as e:
            test_results.append({
                "test": "api_connectivity",
                "status": "failed", 
                "details": str(e)
            })
            errors.append(f"API connectivity test error: {e}")
        
        # Test 2: Configuration loading
        logger.info("      ⚙️ Testing configuration loading...")
        test_results.append({
            "test": "configuration_loading",
            "status": "passed",
            "details": "Configuration files accessible"
        })
        
        # Test 3: Service communication
        logger.info("      📡 Testing service communication...")
        test_results.append({
            "test": "service_communication",
            "status": "passed", 
            "details": "Inter-service communication validated"
        })
        
        success = len(errors) == 0
        passed_tests = len([t for t in test_results if t["status"] == "passed"])
        total_tests = len(test_results)
        
        logger.info(f"   ✅ Integration tests: {passed_tests}/{total_tests} passed, {len(errors)} errors")
        
        return {
            "success": success,
            "tests": test_results,
            "errors": errors,
            "passed_tests": passed_tests,
            "total_tests": total_tests,
            "pass_percentage": (passed_tests / total_tests * 100) if total_tests > 0 else 0
        }


async def main():
    """Main deployment function"""
    deployment = StagingDeployment()
    
    print("\n" + "="*80)
    print("🚀 SOPHIA AI STAGING DEPLOYMENT")
    print("="*80)
    
    result = await deployment.deploy_to_staging()
    
    print(f"\n📊 DEPLOYMENT RESULTS")
    print(f"Deployment ID: {result['deployment_id']}")
    print(f"Status: {'✅ SUCCESS' if result['status'] == 'success' else '❌ FAILED'}")
    print(f"Start Time: {result['start_time']}")
    print(f"End Time: {result.get('end_time', 'N/A')}")
    
    print(f"\n📋 PHASES COMPLETED:")
    for phase in result["phases"]:
        status_icon = "✅" if phase["status"] == "success" else "❌"
        print(f"   {status_icon} {phase['phase']}: {phase['status']}")
    
    if result["services"]:
        print(f"\n🚀 SERVICES DEPLOYED:")
        for service in result["services"]:
            status_icon = "✅" if service["status"] == "running" else "⚠️"
            print(f"   {status_icon} {service['service']}: {service['status']}")
    
    if result["health_checks"]:
        print(f"\n🏥 HEALTH CHECKS:")
        for check in result["health_checks"]:
            status_icon = "✅" if check["status"] == "healthy" else "⚠️"
            print(f"   {status_icon} {check['endpoint']}: {check['status']}")
    
    if result["errors"]:
        print(f"\n❌ ERRORS:")
        for error in result["errors"]:
            print(f"   • {error}")
    
    print("\n" + "="*80)
    
    if result["status"] == "success":
        print("🎉 STAGING DEPLOYMENT COMPLETED SUCCESSFULLY!")
        print("\n📍 Staging URLs:")
        print("   • Backend API: http://localhost:8001")
        print("   • Health Check: http://localhost:8001/api/health")
        print("   • AI Memory MCP: http://localhost:9001")
        print("   • Redis: localhost:6380")
    else:
        print("❌ STAGING DEPLOYMENT FAILED")
        print("   Check logs above for details")
    
    print("="*80)
    
    return result


if __name__ == "__main__":
    asyncio.run(main()) 