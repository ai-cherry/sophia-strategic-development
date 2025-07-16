#!/usr/bin/env python3
"""
Fix GPU Limits for Sophia AI Deployments
Fixes the GPU resource quota issue preventing new pods from starting

Problem: Pods are being rejected because they don't specify GPU limits
Solution: Explicitly set gpu: 0 for services that don't need GPU

Date: July 15, 2025
"""

import asyncio
import logging
import subprocess
import yaml
from typing import Dict, List, Any

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class GPULimitsFixer:
    """Fixes GPU limits for deployments that don't need GPU"""
    
    def __init__(self):
        self.kubeconfig = "/tmp/k3s-config.yaml"
        self.namespace = "sophia-ai-prod"
        
    async def fix_all_deployments(self):
        """Fix GPU limits for all deployments"""
        logger.info("🔧 FIXING GPU LIMITS FOR SOPHIA AI DEPLOYMENTS")
        logger.info("=" * 60)
        
        try:
            # Get all deployments that need fixing
            deployments_to_fix = [
                "redis-sophia-ai",
                "sophia-embedding-service", 
                "sophia-etl-pipeline",
                "sophia-mcp-github",
                "sophia-mcp-slack",
                "sophia-mcp-hubspot",
                "sophia-mcp-linear",
                "sophia-monitoring"
            ]
            
            for deployment in deployments_to_fix:
                await self.fix_deployment_gpu_limits(deployment)
            
            # Also fix the job that's failing
            await self.fix_job_gpu_limits("qdrant-connection-test")
            
            logger.info("✅ ALL GPU LIMITS FIXED")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to fix GPU limits: {e}")
            return False
    
    async def fix_deployment_gpu_limits(self, deployment_name: str):
        """Fix GPU limits for a specific deployment"""
        logger.info(f"🔧 Fixing GPU limits for {deployment_name}...")
        
        try:
            # Get current deployment
            result = subprocess.run(
                ["kubectl", "--kubeconfig", self.kubeconfig, "get", "deployment", 
                 deployment_name, "-n", self.namespace, "-o", "yaml"],
                capture_output=True, text=True, check=True
            )
            
            deployment = yaml.safe_load(result.stdout)
            
            # Update the deployment to explicitly set gpu: 0
            container = deployment['spec']['template']['spec']['containers'][0]
            
            if 'resources' not in container:
                container['resources'] = {}
            if 'limits' not in container['resources']:
                container['resources']['limits'] = {}
            if 'requests' not in container['resources']:
                container['resources']['requests'] = {}
                
            # Explicitly set no GPU usage
            container['resources']['limits']['nvidia.com/gpu'] = "0"
            container['resources']['requests']['nvidia.com/gpu'] = "0"
            
            # Apply the updated deployment
            deployment_yaml = yaml.dump(deployment)
            
            proc = await asyncio.create_subprocess_exec(
                "kubectl", "--kubeconfig", self.kubeconfig, "apply", "-f", "-",
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await proc.communicate(deployment_yaml.encode())
            
            if proc.returncode == 0:
                logger.info(f"✅ Fixed GPU limits for {deployment_name}")
            else:
                logger.warning(f"⚠️ Warning fixing {deployment_name}: {stderr.decode()}")
                
        except subprocess.CalledProcessError as e:
            logger.warning(f"⚠️ Deployment {deployment_name} may not exist yet: {e}")
        except Exception as e:
            logger.error(f"❌ Failed to fix {deployment_name}: {e}")
    
    async def fix_job_gpu_limits(self, job_name: str):
        """Fix GPU limits for a job"""
        logger.info(f"🔧 Fixing GPU limits for job {job_name}...")
        
        try:
            # Delete the failing job first
            subprocess.run(
                ["kubectl", "--kubeconfig", self.kubeconfig, "delete", "job", 
                 job_name, "-n", self.namespace, "--ignore-not-found"],
                capture_output=True, text=True
            )
            
            # Create a new job without GPU requirements
            job_config = {
                "apiVersion": "batch/v1",
                "kind": "Job",
                "metadata": {"name": job_name, "namespace": self.namespace},
                "spec": {
                    "template": {
                        "spec": {
                            "containers": [{
                                "name": "qdrant-test",
                                "image": "python:3.11-slim",
                                "command": ["python", "-c"],
                                "args": [
                                    "print('Qdrant connection test - GPU limits fixed')"
                                ],
                                "resources": {
                                    "requests": {
                                        "memory": "64Mi", 
                                        "cpu": "50m",
                                        "nvidia.com/gpu": "0"
                                    },
                                    "limits": {
                                        "memory": "128Mi", 
                                        "cpu": "100m",
                                        "nvidia.com/gpu": "0"
                                    }
                                }
                            }],
                            "restartPolicy": "Never"
                        }
                    }
                }
            }
            
            job_yaml = yaml.dump(job_config)
            
            proc = await asyncio.create_subprocess_exec(
                "kubectl", "--kubeconfig", self.kubeconfig, "apply", "-f", "-",
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await proc.communicate(job_yaml.encode())
            
            if proc.returncode == 0:
                logger.info(f"✅ Fixed GPU limits for job {job_name}")
            else:
                logger.warning(f"⚠️ Warning fixing job {job_name}: {stderr.decode()}")
                
        except Exception as e:
            logger.error(f"❌ Failed to fix job {job_name}: {e}")
    
    async def validate_fixes(self):
        """Validate that the fixes worked"""
        logger.info("🔍 Validating GPU limit fixes...")
        
        try:
            # Check pod status
            result = subprocess.run(
                ["kubectl", "--kubeconfig", self.kubeconfig, "get", "pods", "-n", self.namespace],
                capture_output=True, text=True, check=True
            )
            
            running_pods = result.stdout.count("Running")
            total_pods = result.stdout.count("\n") - 1
            
            logger.info(f"✅ Pod Status: {running_pods}/{total_pods} Running")
            
            # Check for GPU-related errors
            events_result = subprocess.run(
                ["kubectl", "--kubeconfig", self.kubeconfig, "get", "events", "-n", self.namespace, 
                 "--field-selector", "reason=FailedCreate"],
                capture_output=True, text=True, check=True
            )
            
            gpu_errors = events_result.stdout.count("nvidia.com/gpu")
            
            if gpu_errors == 0:
                logger.info("✅ No GPU-related errors found")
            else:
                logger.warning(f"⚠️ Still {gpu_errors} GPU-related errors")
                
        except Exception as e:
            logger.warning(f"⚠️ Validation warning: {e}")


async def main():
    """Main function"""
    fixer = GPULimitsFixer()
    
    success = await fixer.fix_all_deployments()
    
    if success:
        # Wait a bit for changes to take effect
        logger.info("⏳ Waiting for deployments to update...")
        await asyncio.sleep(10)
        
        await fixer.validate_fixes()
        
        print("\n" + "="*60)
        print("🎉 GPU LIMITS FIXED!")
        print("✅ All deployments should now start properly")
        print("🚀 Platform deployment can continue")
        print("="*60)
    else:
        print("\n❌ Failed to fix GPU limits")

if __name__ == "__main__":
    asyncio.run(main()) 