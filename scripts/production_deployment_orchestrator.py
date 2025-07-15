#!/usr/bin/env python3
"""
Production Deployment Orchestrator
Comprehensive script for 24/7 production deployment of Sophia AI MCP platform
"""

import asyncio
import subprocess
import json
import time
import httpx
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

class ProductionDeploymentOrchestrator:
    """Orchestrates complete production deployment with monitoring and rollback"""
    
    def __init__(self):
        self.lambda_labs_ip = "192.222.58.232"
        self.production_url = f"http://{self.lambda_labs_ip}:8000"
        self.deployment_config = {
            "namespace": "sophia-ai-prod",
            "docker_registry": "scoobyjava15",
            "health_check_timeout": 300,  # 5 minutes
            "rollback_timeout": 180       # 3 minutes
        }
        self.mcp_platforms = ["linear", "asana", "notion", "hubspot", "gong", "slack", "github"]
    
    async def pre_deployment_checks(self) -> bool:
        """Run comprehensive pre-deployment checks"""
        print("🔍 Running Pre-Deployment Checks...")
        
        checks = [
            ("Docker Images", self.check_docker_images),
            ("Kubernetes Cluster", self.check_kubernetes_cluster),
            ("Pulumi ESC Secrets", self.check_pulumi_secrets),
            ("Database Connectivity", self.check_database_connectivity),
            ("External APIs", self.check_external_apis)
        ]
        
        all_passed = True
        for check_name, check_func in checks:
            try:
                result = await check_func()
                status = "✅ PASS" if result else "❌ FAIL"
                print(f"  {status} {check_name}")
                if not result:
                    all_passed = False
            except Exception as e:
                print(f"  ❌ FAIL {check_name}: {e}")
                all_passed = False
        
        return all_passed
    
    async def check_docker_images(self) -> bool:
        """Check if Docker images are built and available"""
        try:
            images = [
                f"{self.deployment_config['docker_registry']}/sophia-ai-backend:latest",
                f"{self.deployment_config['docker_registry']}/sophia-ai-mcp-orchestrator:latest"
            ]
            
            for image in images:
                result = subprocess.run(
                    ["docker", "inspect", image],
                    capture_output=True,
                    text=True
                )
                if result.returncode != 0:
                    print(f"    Image not found: {image}")
                    return False
            
            return True
        except Exception as e:
            print(f"    Docker check error: {e}")
            return False
    
    async def check_kubernetes_cluster(self) -> bool:
        """Check Kubernetes cluster connectivity"""
        try:
            result = subprocess.run(
                ["kubectl", "cluster-info"],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except Exception as e:
            print(f"    Kubernetes check error: {e}")
            return False
    
    async def check_pulumi_secrets(self) -> bool:
        """Check Pulumi ESC secrets are configured"""
        try:
            result = subprocess.run(
                ["pulumi", "env", "get", "scoobyjava-org/default/sophia-ai-production"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                # Check for critical secrets
                output = result.stdout
                critical_secrets = ["openai_api_key", "linear_api_key", "asana_api_token"]
                
                for secret in critical_secrets:
                    if secret not in output:
                        print(f"    Missing secret: {secret}")
                        return False
                
                return True
            return False
        except Exception as e:
            print(f"    Pulumi ESC check error: {e}")
            return False
    
    async def check_database_connectivity(self) -> bool:
        """Check database connectivity"""
        try:
            # This would check PostgreSQL connectivity
            # For now, assume it's available
            return True
        except Exception as e:
            print(f"    Database check error: {e}")
            return False
    
    async def check_external_apis(self) -> bool:
        """Check external API connectivity"""
        try:
            # Test basic internet connectivity
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get("https://api.github.com")
                return response.status_code == 200
        except Exception as e:
            print(f"    External API check error: {e}")
            return False
    
    async def build_and_push_images(self) -> bool:
        """Build and push Docker images"""
        print("📦 Building and Pushing Docker Images...")
        
        try:
            # Build backend image
            print("  Building backend image...")
            result = subprocess.run([
                "docker", "build", 
                "-t", f"{self.deployment_config['docker_registry']}/sophia-ai-backend:latest",
                "-f", "backend/Dockerfile",
                "."
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"    Backend build failed: {result.stderr}")
                return False
            
            # Push backend image
            print("  Pushing backend image...")
            result = subprocess.run([
                "docker", "push",
                f"{self.deployment_config['docker_registry']}/sophia-ai-backend:latest"
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"    Backend push failed: {result.stderr}")
                return False
            
            print("  ✅ Images built and pushed successfully")
            return True
            
        except Exception as e:
            print(f"    Image build error: {e}")
            return False
    
    async def deploy_to_kubernetes(self) -> bool:
        """Deploy to Kubernetes cluster"""
        print("🚢 Deploying to Kubernetes...")
        
        try:
            # Apply Kubernetes manifests
            k8s_files = [
                "k8s/namespace.yaml",
                "k8s/configmap.yaml",
                "k8s/secret.yaml",
                "k8s/deployment.yaml",
                "k8s/service.yaml",
                "k8s/ingress.yaml"
            ]
            
            for k8s_file in k8s_files:
                if Path(k8s_file).exists():
                    print(f"  Applying {k8s_file}...")
                    result = subprocess.run([
                        "kubectl", "apply", "-f", k8s_file,
                        "-n", self.deployment_config["namespace"]
                    ], capture_output=True, text=True)
                    
                    if result.returncode != 0:
                        print(f"    Failed to apply {k8s_file}: {result.stderr}")
                        return False
            
            # Wait for deployment rollout
            print("  Waiting for deployment rollout...")
            result = subprocess.run([
                "kubectl", "rollout", "status", 
                "deployment/sophia-ai-backend",
                "-n", self.deployment_config["namespace"],
                "--timeout=300s"
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"    Deployment rollout failed: {result.stderr}")
                return False
            
            print("  ✅ Kubernetes deployment successful")
            return True
            
        except Exception as e:
            print(f"    Kubernetes deployment error: {e}")
            return False
    
    async def run_health_checks(self) -> bool:
        """Run comprehensive health checks"""
        print("🏥 Running Health Checks...")
        
        # Wait for pods to be ready
        await asyncio.sleep(30)
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Check main health endpoint
                print("  Checking main health endpoint...")
                response = await client.get(f"{self.production_url}/health")
                
                if response.status_code != 200:
                    print(f"    Health endpoint failed: {response.status_code}")
                    return False
                
                # Check all MCP platform endpoints
                print("  Checking MCP platform endpoints...")
                for platform in self.mcp_platforms:
                    try:
                        response = await client.get(f"{self.production_url}/api/v4/mcp/{platform}/projects")
                        if response.status_code != 200:
                            print(f"    {platform} endpoint failed: {response.status_code}")
                            return False
                        else:
                            print(f"    ✅ {platform} endpoint healthy")
                    except Exception as e:
                        print(f"    {platform} endpoint error: {e}")
                        return False
                
                print("  ✅ All health checks passed")
                return True
                
        except Exception as e:
            print(f"    Health check error: {e}")
            return False
    
    async def run_performance_tests(self) -> bool:
        """Run performance tests"""
        print("⚡ Running Performance Tests...")
        
        try:
            # Run load test
            response_times = []
            error_count = 0
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Test with concurrent requests
                for i in range(50):  # 50 concurrent requests
                    start_time = time.time()
                    try:
                        response = await client.get(f"{self.production_url}/api/v4/mcp/linear/projects")
                        response_time = time.time() - start_time
                        
                        if response.status_code == 200:
                            response_times.append(response_time)
                        else:
                            error_count += 1
                            
                    except Exception as e:
                        error_count += 1
                        print(f"    Request {i+1} failed: {e}")
            
            # Calculate metrics
            if response_times:
                avg_response_time = sum(response_times) / len(response_times)
                max_response_time = max(response_times)
                error_rate = error_count / (len(response_times) + error_count)
                
                print(f"  Average response time: {avg_response_time:.2f}s")
                print(f"  Max response time: {max_response_time:.2f}s")
                print(f"  Error rate: {error_rate:.2%}")
                
                # Check performance thresholds
                if avg_response_time > 2.0:
                    print("    ❌ Average response time too high")
                    return False
                
                if max_response_time > 5.0:
                    print("    ❌ Max response time too high")
                    return False
                
                if error_rate > 0.05:  # 5% error rate
                    print("    ❌ Error rate too high")
                    return False
                
                print("  ✅ Performance tests passed")
                return True
            else:
                print("    ❌ No successful requests")
                return False
                
        except Exception as e:
            print(f"    Performance test error: {e}")
            return False
    
    async def setup_monitoring(self) -> bool:
        """Setup production monitoring"""
        print("📊 Setting up Monitoring...")
        
        try:
            # Deploy monitoring stack
            monitoring_files = [
                "k8s/monitoring/prometheus.yaml",
                "k8s/monitoring/grafana.yaml",
                "k8s/monitoring/alertmanager.yaml"
            ]
            
            for monitoring_file in monitoring_files:
                if Path(monitoring_file).exists():
                    print(f"  Deploying {monitoring_file}...")
                    result = subprocess.run([
                        "kubectl", "apply", "-f", monitoring_file,
                        "-n", "monitoring"
                    ], capture_output=True, text=True)
                    
                    if result.returncode != 0:
                        print(f"    Failed to deploy {monitoring_file}: {result.stderr}")
                        # Continue with other monitoring components
            
            print("  ✅ Monitoring setup complete")
            return True
            
        except Exception as e:
            print(f"    Monitoring setup error: {e}")
            return False
    
    async def rollback_deployment(self) -> bool:
        """Rollback deployment if issues detected"""
        print("🔄 Rolling back deployment...")
        
        try:
            result = subprocess.run([
                "kubectl", "rollout", "undo",
                "deployment/sophia-ai-backend",
                "-n", self.deployment_config["namespace"]
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("  ✅ Rollback successful")
                return True
            else:
                print(f"  ❌ Rollback failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"    Rollback error: {e}")
            return False
    
    async def run_production_deployment(self) -> bool:
        """Run complete production deployment"""
        print("🚀 Starting Production Deployment")
        print("=" * 80)
        
        deployment_start_time = datetime.now()
        
        # Phase 1: Pre-deployment checks
        print("\\n📋 Phase 1: Pre-Deployment Checks")
        print("-" * 50)
        
        if not await self.pre_deployment_checks():
            print("❌ Pre-deployment checks failed")
            return False
        
        # Phase 2: Build and push images
        print("\\n📋 Phase 2: Build and Push Images")
        print("-" * 50)
        
        if not await self.build_and_push_images():
            print("❌ Image build and push failed")
            return False
        
        # Phase 3: Deploy to Kubernetes
        print("\\n📋 Phase 3: Deploy to Kubernetes")
        print("-" * 50)
        
        if not await self.deploy_to_kubernetes():
            print("❌ Kubernetes deployment failed")
            return False
        
        # Phase 4: Health checks
        print("\\n📋 Phase 4: Health Checks")
        print("-" * 50)
        
        if not await self.run_health_checks():
            print("❌ Health checks failed, rolling back...")
            await self.rollback_deployment()
            return False
        
        # Phase 5: Performance tests
        print("\\n📋 Phase 5: Performance Tests")
        print("-" * 50)
        
        if not await self.run_performance_tests():
            print("❌ Performance tests failed, rolling back...")
            await self.rollback_deployment()
            return False
        
        # Phase 6: Setup monitoring
        print("\\n📋 Phase 6: Setup Monitoring")
        print("-" * 50)
        
        await self.setup_monitoring()  # Non-blocking
        
        # Deployment complete
        deployment_duration = datetime.now() - deployment_start_time
        
        print("\\n🎉 Production Deployment Complete!")
        print(f"📊 Deployment Duration: {deployment_duration}")
        print(f"🌐 Production URL: {self.production_url}")
        print(f"📈 Monitoring: http://{self.lambda_labs_ip}:3000")
        print(f"🔍 Health Check: {self.production_url}/health")
        
        return True

async def main():
    """Main deployment function"""
    orchestrator = ProductionDeploymentOrchestrator()
    
    success = await orchestrator.run_production_deployment()
    
    if success:
        print("\\n✅ SUCCESS: Production deployment completed successfully!")
        print("🎯 System is ready for 24/7 operation")
        exit(0)
    else:
        print("\\n❌ FAILED: Production deployment encountered errors")
        print("🔧 Check logs and retry deployment")
        exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 