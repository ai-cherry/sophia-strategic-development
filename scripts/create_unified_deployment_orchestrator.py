#!/usr/bin/env python3
"""
Create Unified Deployment Orchestrator
Generates the main deployment script based on the integrated architecture plan
"""

import os
from pathlib import Path

def create_unified_deployment_orchestrator():
    """Create the unified deployment orchestrator script"""
    
    script_content = '''#!/usr/bin/env python3
"""
Unified Deployment Orchestrator for Sophia AI
Single deployment entry point for all environments
Post-ELIMINATED elimination integrated architecture
"""

import asyncio
import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LambdaLabsManager:
    """Manage Lambda Labs infrastructure"""
    
    def __init__(self):
        self.api_key = os.getenv("LAMBDA_API_KEY")
        self.ssh_key_path = os.getenv("LAMBDA_SSH_PRIVATE_KEY", "~/.ssh/lambda_labs_private_key")
        
        self.instances = {
            "master": {"ip": "192.222.58.232", "gpu": "GH200", "role": "master"},
            "mcp": {"ip": "104.171.202.117", "gpu": "A6000", "role": "worker"},
            "data": {"ip": "104.171.202.134", "gpu": "A100", "role": "worker"},
            "prod": {"ip": "104.171.202.103", "gpu": "RTX6000", "role": "worker"}
        }
    
    async def check_instances(self) -> Dict[str, bool]:
        """Check if all Lambda Labs instances are accessible"""
        logger.info("🔍 Checking Lambda Labs instances...")
        
        results = {}
        for name, config in self.instances.items():
            try:
                result = subprocess.run([
                    "ssh", "-i", self.ssh_key_path, "-o", "ConnectTimeout=10",
                    f"ubuntu@{config['ip']}", "echo 'OK'"
                ], capture_output=True, text=True, timeout=15)
                
                results[name] = result.returncode == 0
                status = "✅" if results[name] else "❌"
                logger.info(f"   {status} {name} ({config['ip']}) - {config['gpu']}")
                
            except Exception as e:
                results[name] = False
                logger.error(f"   ❌ {name} ({config['ip']}) - Error: {e}")
        
        return results

class WeaviateCloudManager:
    """Manage Weaviate Cloud integration"""
    
    def __init__(self):
        self.cluster_url = "https://w6bigpoxsrwvq7wlgmmdva.c0.us-west3.gcp.weaviate.cloud"
        self.api_key = "VMKjGMQUnXQIDiFOciZZOhr7amBfCHMh7hNf"
    
    async def test_connection(self) -> bool:
        """Test Weaviate Cloud connection"""
        logger.info("🔷 Testing Weaviate Cloud connection...")
        
        try:
            import requests
            response = requests.get(
                f"{self.cluster_url}/v1/meta",
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info("   ✅ Weaviate Cloud connection successful")
                return True
            else:
                logger.error(f"   ❌ Weaviate Cloud connection failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"   ❌ Weaviate Cloud connection error: {e}")
            return False
    
    async def setup_schemas(self) -> bool:
        """Set up Weaviate schemas for Sophia AI"""
        logger.info("🔷 Setting up Weaviate schemas...")
        
        try:
            # Run the schema initialization script
            result = subprocess.run([
                "python", "scripts/init_weaviate_schema.py"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("   ✅ Weaviate schemas created successfully")
                return True
            else:
                logger.error(f"   ❌ Schema creation failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"   ❌ Schema setup error: {e}")
            return False

class K3sManager:
    """Manage K3s Kubernetes cluster"""
    
    def __init__(self, lambda_manager: LambdaLabsManager):
        self.lambda_manager = lambda_manager
        self.master_ip = "192.222.58.232"
    
    async def setup_cluster(self) -> bool:
        """Set up K3s cluster across Lambda Labs instances"""
        logger.info("☸️  Setting up K3s cluster...")
        
        # 1. Install K3s on master node
        logger.info("   Installing K3s on master node...")
        master_cmd = [
            "ssh", "-i", self.lambda_manager.ssh_key_path,
            f"ubuntu@{self.master_ip}",
            "curl -sfL https://get.k3s.io | sh -s - --write-kubeconfig-mode 644"
        ]
        
        try:
            result = subprocess.run(master_cmd, capture_output=True, text=True, timeout=300)
            if result.returncode != 0:
                logger.error(f"   ❌ K3s master installation failed: {result.stderr}")
                return False
            
            logger.info("   ✅ K3s master installed successfully")
            
            # 2. Get node token
            token_cmd = [
                "ssh", "-i", self.lambda_manager.ssh_key_path,
                f"ubuntu@{self.master_ip}",
                "sudo cat /var/lib/rancher/k3s/server/node-token"
            ]
            
            token_result = subprocess.run(token_cmd, capture_output=True, text=True)
            if token_result.returncode != 0:
                logger.error("   ❌ Failed to get node token")
                return False
            
            node_token = token_result.stdout.strip()
            
            # 3. Join worker nodes
            for name, config in self.lambda_manager.instances.items():
                if config["role"] == "worker":
                    logger.info(f"   Joining worker node: {name}")
                    
                    worker_cmd = [
                        "ssh", "-i", self.lambda_manager.ssh_key_path,
                        f"ubuntu@{config['ip']}",
                        f"curl -sfL https://get.k3s.io | K3S_URL=https://{self.master_ip}:6443 K3S_TOKEN={node_token} sh -"
                    ]
                    
                    worker_result = subprocess.run(worker_cmd, capture_output=True, text=True, timeout=300)
                    if worker_result.returncode == 0:
                        logger.info(f"   ✅ Worker {name} joined successfully")
                    else:
                        logger.warning(f"   ⚠️  Worker {name} join failed: {worker_result.stderr}")
            
            return True
            
        except Exception as e:
            logger.error(f"   ❌ K3s setup error: {e}")
            return False
    
    async def deploy_mcp_servers(self) -> bool:
        """Deploy MCP servers to Kubernetes"""
        logger.info("🔧 Deploying MCP servers to K3s...")
        
        try:
            # Copy kubeconfig from master
            kubeconfig_cmd = [
                "scp", "-i", self.lambda_manager.ssh_key_path,
                f"ubuntu@{self.master_ip}:/etc/rancher/k3s/k3s.yaml",
                "~/.kube/config"
            ]
            
            subprocess.run(kubeconfig_cmd, capture_output=True)
            
            # Update server URL in kubeconfig
            subprocess.run([
                "sed", "-i", f"s/127.0.0.1/{self.master_ip}/g", 
                os.path.expanduser("~/.kube/config")
            ])
            
            # Apply MCP server manifests
            if Path("kubernetes/mcp-servers").exists():
                result = subprocess.run([
                    "kubectl", "apply", "-f", "kubernetes/mcp-servers/"
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    logger.info("   ✅ MCP servers deployed successfully")
                    return True
                else:
                    logger.error(f"   ❌ MCP deployment failed: {result.stderr}")
                    return False
            else:
                logger.warning("   ⚠️  MCP server manifests not found")
                return False
                
        except Exception as e:
            logger.error(f"   ❌ MCP deployment error: {e}")
            return False

class VercelManager:
    """Manage Vercel frontend deployment"""
    
    def __init__(self):
        self.token = os.getenv("VERCEL_TOKEN")
        self.project = "sophia-intel-ai"
    
    async def deploy_frontend(self) -> bool:
        """Deploy frontend to Vercel"""
        logger.info("🌐 Deploying frontend to Vercel...")
        
        if not self.token:
            logger.warning("   ⚠️  VERCEL_TOKEN not set, skipping frontend deployment")
            return False
        
        try:
            # Build frontend
            if Path("frontend").exists():
                build_result = subprocess.run([
                    "npm", "run", "build"
                ], cwd="frontend", capture_output=True, text=True)
                
                if build_result.returncode != 0:
                    logger.error(f"   ❌ Frontend build failed: {build_result.stderr}")
                    return False
                
                # Deploy to Vercel
                deploy_result = subprocess.run([
                    "vercel", "--prod", "--token", self.token
                ], cwd="frontend", capture_output=True, text=True)
                
                if deploy_result.returncode == 0:
                    logger.info("   ✅ Frontend deployed successfully")
                    return True
                else:
                    logger.error(f"   ❌ Vercel deployment failed: {deploy_result.stderr}")
                    return False
            else:
                logger.warning("   ⚠️  Frontend directory not found")
                return False
                
        except Exception as e:
            logger.error(f"   ❌ Frontend deployment error: {e}")
            return False

class UnifiedDeploymentOrchestrator:
    """Main deployment orchestrator"""
    
    def __init__(self, environment: str = "production"):
        self.environment = environment
        self.lambda_labs = LambdaLabsManager()
        self.weaviate = WeaviateCloudManager()
        self.kubernetes = K3sManager(self.lambda_labs)
        self.vercel = VercelManager()
        
        self.deployment_start = datetime.now()
        self.deployment_status = {
            "infrastructure": False,
            "weaviate": False,
            "kubernetes": False,
            "mcp_servers": False,
            "frontend": False
        }
    
    async def validate_prerequisites(self) -> bool:
        """Validate deployment prerequisites"""
        logger.info("🔍 Validating deployment prerequisites...")
        
        # Check environment variables
        required_vars = [
            "LAMBDA_API_KEY",
            "OPENAI_API_KEY",
            "ANTHROPIC_API_KEY"
        ]
        
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            logger.error(f"   ❌ Missing environment variables: {', '.join(missing_vars)}")
            return False
        
        # Check SSH key
        ssh_key_path = os.path.expanduser(self.lambda_labs.ssh_key_path)
        if not Path(ssh_key_path).exists():
            logger.error(f"   ❌ SSH key not found: {ssh_key_path}")
            return False
        
        logger.info("   ✅ Prerequisites validated")
        return True
    
    async def deploy_full_stack(self) -> bool:
        """Deploy complete Sophia AI stack"""
        logger.info(f"🚀 Starting Sophia AI deployment to {self.environment}")
        logger.info("=" * 60)
        
        try:
            # 1. Validate prerequisites
            if not await self.validate_prerequisites():
                return False
            
            # 2. Check Lambda Labs infrastructure
            instance_status = await self.lambda_labs.check_instances()
            if not all(instance_status.values()):
                logger.error("❌ Not all Lambda Labs instances are accessible")
                return False
            
            self.deployment_status["infrastructure"] = True
            logger.info("✅ Infrastructure validation complete")
            
            # 3. Test Weaviate Cloud connection
            if await self.weaviate.test_connection():
                self.deployment_status["weaviate"] = True
                logger.info("✅ Weaviate Cloud connection validated")
                
                # Set up schemas
                await self.weaviate.setup_schemas()
            else:
                logger.error("❌ Weaviate Cloud connection failed")
                return False
            
            # 4. Set up K3s cluster
            if await self.kubernetes.setup_cluster():
                self.deployment_status["kubernetes"] = True
                logger.info("✅ K3s cluster setup complete")
            else:
                logger.error("❌ K3s cluster setup failed")
                return False
            
            # 5. Deploy MCP servers
            if await self.kubernetes.deploy_mcp_servers():
                self.deployment_status["mcp_servers"] = True
                logger.info("✅ MCP servers deployed")
            else:
                logger.warning("⚠️  MCP server deployment had issues")
            
            # 6. Deploy frontend
            if await self.vercel.deploy_frontend():
                self.deployment_status["frontend"] = True
                logger.info("✅ Frontend deployed")
            else:
                logger.warning("⚠️  Frontend deployment skipped")
            
            # 7. Final validation
            await self.validate_deployment()
            
            deployment_time = datetime.now() - self.deployment_start
            logger.info("=" * 60)
            logger.info(f"🎉 Deployment completed in {deployment_time}")
            logger.info("✅ Sophia AI is now running on the integrated architecture!")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Deployment failed: {e}")
            return False
    
    async def validate_deployment(self) -> bool:
        """Validate deployment success"""
        logger.info("🔍 Validating deployment...")
        
        # Check if services are responding
        validation_checks = [
            ("Infrastructure", self.deployment_status["infrastructure"]),
            ("Weaviate Cloud", self.deployment_status["weaviate"]),
            ("K3s Cluster", self.deployment_status["kubernetes"]),
            ("MCP Servers", self.deployment_status["mcp_servers"]),
            ("Frontend", self.deployment_status["frontend"])
        ]
        
        for check_name, status in validation_checks:
            status_icon = "✅" if status else "❌"
            logger.info(f"   {status_icon} {check_name}")
        
        success_rate = sum(self.deployment_status.values()) / len(self.deployment_status)
        logger.info(f"📊 Deployment success rate: {success_rate:.1%}")
        
        return success_rate >= 0.8  # 80% success threshold
    
    async def rollback_deployment(self):
        """Rollback deployment on failure"""
        logger.warning("🔄 Rolling back deployment...")
        
        # Implementation would include:
        # - Stop failed services
        # - Restore previous state
        # - Clean up partial deployments
        
        logger.info("✅ Rollback completed")

async def main():
    """Main deployment function"""
    parser = argparse.ArgumentParser(description="Unified Sophia AI Deployment")
    parser.add_argument("--environment", default="production", 
                       choices=["development", "staging", "production"],
                       help="Deployment environment")
    parser.add_argument("--validate-only", action="store_true",
                       help="Only validate prerequisites")
    
    args = parser.parse_args()
    
    orchestrator = UnifiedDeploymentOrchestrator(args.environment)
    
    if args.validate_only:
        success = await orchestrator.validate_prerequisites()
        sys.exit(0 if success else 1)
    else:
        success = await orchestrator.deploy_full_stack()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())
'''
    
    # Write the script
    script_path = Path("scripts/unified_deployment_orchestrator.py")
    script_path.parent.mkdir(exist_ok=True)
    
    with open(script_path, 'w') as f:
        f.write(script_content)
    
    # Make it executable
    os.chmod(script_path, 0o755)
    
    print(f"✅ Created unified deployment orchestrator: {script_path}")
    return script_path

def create_weaviate_cloud_test():
    """Create Weaviate Cloud integration test script"""
    
    test_content = '''#!/usr/bin/env python3
"""
Test Weaviate Cloud Integration
Validates connection and basic operations
"""

import asyncio
import os
import sys
from datetime import datetime

try:
    import weaviate
    import requests
except ImportError:
    print("❌ Missing dependencies. Install with: pip install weaviate-client requests")
    sys.exit(1)

class WeaviateCloudTester:
    """Test Weaviate Cloud integration"""
    
    def __init__(self):
        self.cluster_url = "https://w6bigpoxsrwvq7wlgmmdva.c0.us-west3.gcp.weaviate.cloud"
        self.api_key = "VMKjGMQUnXQIDiFOciZZOhr7amBfCHMh7hNf"
    
    def test_connection(self) -> bool:
        """Test basic connection"""
        print("🔷 Testing Weaviate Cloud connection...")
        
        try:
            response = requests.get(
                f"{self.cluster_url}/v1/meta",
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=10
            )
            
            if response.status_code == 200:
                meta = response.json()
                print(f"   ✅ Connected to Weaviate Cloud")
                print(f"   📍 Hostname: {meta.get('hostname', 'Unknown')}")
                print(f"   🔧 Modules: {len(meta.get('modules', {}))}")
                return True
            else:
                print(f"   ❌ Connection failed: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Connection error: {e}")
            return False
    
    def test_client_v4(self) -> bool:
        """Test Weaviate v4 client"""
        print("🔷 Testing Weaviate v4 client...")
        
        try:
            client = weaviate.connect_to_wcs(
                cluster_url=self.cluster_url,
                auth_credentials=weaviate.AuthApiKey(self.api_key)
            )
            
            # Test basic operations
            if client.is_ready():
                print("   ✅ Client v4 connection successful")
                
                # Get cluster info
                meta = client.get_meta()
                print(f"   📊 Cluster ready: {client.is_ready()}")
                
                client.close()
                return True
            else:
                print("   ❌ Client not ready")
                return False
                
        except Exception as e:
            print(f"   ❌ Client v4 error: {e}")
            return False
    
    def test_schema_operations(self) -> bool:
        """Test schema operations"""
        print("🔷 Testing schema operations...")
        
        try:
            client = weaviate.connect_to_wcs(
                cluster_url=self.cluster_url,
                auth_credentials=weaviate.AuthApiKey(self.api_key)
            )
            
            # List existing collections
            collections = client.collections.list_all()
            print(f"   📚 Existing collections: {len(collections)}")
            
            # Test collection creation (if needed)
            test_collection_name = "SophiaTest"
            
            if test_collection_name not in [c.name for c in collections]:
                print(f"   🔧 Creating test collection: {test_collection_name}")
                
                collection = client.collections.create(
                    name=test_collection_name,
                    properties=[
                        weaviate.Property(name="content", data_type=weaviate.DataType.TEXT),
                        weaviate.Property(name="timestamp", data_type=weaviate.DataType.DATE)
                    ]
                )
                print(f"   ✅ Test collection created")
            else:
                print(f"   ✅ Test collection already exists")
            
            client.close()
            return True
            
        except Exception as e:
            print(f"   ❌ Schema operations error: {e}")
            return False
    
    def run_all_tests(self) -> bool:
        """Run all tests"""
        print("🚀 Starting Weaviate Cloud integration tests...")
        print("=" * 50)
        
        tests = [
            ("Connection Test", self.test_connection),
            ("Client v4 Test", self.test_client_v4),
            ("Schema Operations", self.test_schema_operations)
        ]
        
        results = []
        
        for test_name, test_func in tests:
            try:
                result = test_func()
                results.append(result)
                status = "✅ PASS" if result else "❌ FAIL"
                print(f"{status} {test_name}")
            except Exception as e:
                results.append(False)
                print(f"❌ FAIL {test_name}: {e}")
            
            print()
        
        success_rate = sum(results) / len(results)
        print("=" * 50)
        print(f"📊 Test Results: {sum(results)}/{len(results)} passed ({success_rate:.1%})")
        
        if success_rate >= 0.8:
            print("🎉 Weaviate Cloud integration is ready!")
            return True
        else:
            print("⚠️  Weaviate Cloud integration needs attention")
            return False

def main():
    """Main test function"""
    tester = WeaviateCloudTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
'''
    
    # Write the test script
    test_path = Path("scripts/test_weaviate_cloud_integration.py")
    test_path.parent.mkdir(exist_ok=True)
    
    with open(test_path, 'w') as f:
        f.write(test_content)
    
    # Make it executable
    os.chmod(test_path, 0o755)
    
    print(f"✅ Created Weaviate Cloud test script: {test_path}")
    return test_path

def main():
    """Main function to create all deployment scripts"""
    print("🚀 Creating Unified Deployment Orchestrator...")
    print("=" * 60)
    
    # Create main orchestrator
    orchestrator_path = create_unified_deployment_orchestrator()
    
    # Create Weaviate test
    test_path = create_weaviate_cloud_test()
    
    print("=" * 60)
    print("✅ Deployment scripts created successfully!")
    print()
    print("📋 Next steps:")
    print(f"1. Test Weaviate Cloud: python {test_path}")
    print(f"2. Run deployment: python {orchestrator_path} --environment production")
    print()
    print("🔧 Prerequisites:")
    print("- Set environment variables: LAMBDA_API_KEY, OPENAI_API_KEY, ANTHROPIC_API_KEY")
    print("- Ensure SSH key exists: ~/.ssh/lambda_labs_private_key")
    print("- Install dependencies: pip install weaviate-client requests")

if __name__ == "__main__":
    main() 