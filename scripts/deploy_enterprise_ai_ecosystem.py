#!/usr/bin/env python3
"""
Enterprise AI Ecosystem Deployment Orchestrator (Phoenix 1.4)
Orchestrates the deployment of the entire Sophia AI ecosystem to Kubernetes
using Pulumi and Helm.
"""

import asyncio
import logging
import json
from pathlib import Path
from typing import Dict, Any, List
import subprocess

logger = logging.getLogger(__name__)

class EnterpriseAIEcosystemDeployer:
    """
    Deploys and manages the Phoenix 1.4 ecosystem on Kubernetes.
    This orchestrator is responsible for applying infrastructure-as-code
    definitions and ensuring all components are running and healthy.
    """
    
    def __init__(self, environment: str = "production"):
        self.environment = environment
        self.pulumi_stack = f"scoobyjava-org/sophia-ai-{environment}"
        self.kubeconfig_path = f"~/.kube/config_{environment}"
        
        self.deployment_phases = [
            "validate_prerequisites",
            "deploy_core_infrastructure",
            "deploy_mcp_servers",
            "validate_deployment",
            "run_integration_tests"
        ]

    async def deploy_ecosystem(self) -> Dict[str, Any]:
        """Deploy the complete Enterprise AI Ecosystem."""
        logger.info(f"🚀 Starting Enterprise AI Ecosystem Deployment to '{self.environment}'")
        results = {}
        
        for phase in self.deployment_phases:
            logger.info(f"📋 Executing Phase: {phase}")
            try:
                result = await self._execute_phase(phase)
                results[phase] = {"status": "success", "details": result}
                logger.info(f"✅ Phase '{phase}' completed successfully.")
            except Exception as e:
                logger.error(f"❌ Phase '{phase}' failed: {e}", exc_info=True)
                results[phase] = {"status": "failed", "error": str(e)}
                # Stop deployment on failure
                break
                
        return results

    async def _execute_phase(self, phase: str) -> Any:
        """Execute a specific deployment phase."""
        if phase == "validate_prerequisites":
            return await self._validate_prerequisites()
        elif phase == "deploy_core_infrastructure":
            return await self._run_pulumi_update("infrastructure/core")
        elif phase == "deploy_mcp_servers":
            return await self._deploy_all_mcp_servers()
        elif phase == "validate_deployment":
            return await self._validate_k8s_deployment()
        elif phase == "run_integration_tests":
            return await self._run_integration_tests()
        else:
            raise ValueError(f"Unknown deployment phase: {phase}")

    async def _validate_prerequisites(self) -> Dict[str, bool]:
        """Check for necessary tools like pulumi, helm, kubectl."""
        tools = ["pulumi", "helm", "kubectl", "gh"]
        checks = {}
        for tool in tools:
            try:
                await self._run_command(f"which {tool}")
                checks[tool] = True
            except subprocess.CalledProcessError:
                checks[tool] = False
                raise EnvironmentError(f"Prerequisite '{tool}' not found in PATH.")
        
        # Check Pulumi login status
        try:
            await self._run_command("pulumi whoami")
        except subprocess.CalledProcessError:
            raise EnvironmentError("Not logged into Pulumi. Please run 'pulumi login'.")
            
        return checks

    async def _run_pulumi_update(self, path: str) -> str:
        """Run 'pulumi up' for a specific infrastructure component."""
        logger.info(f"Running Pulumi update for: {path}")
        command = f"pulumi up -C {path} -s {self.pulumi_stack} --yes --skip-preview"
        return await self._run_command(command)

    async def _deploy_all_mcp_servers(self) -> Dict[str, str]:
        """Use Helm to deploy all MCP servers defined in our infrastructure."""
        logger.info("Deploying all MCP servers via Helm chart...")
        # This assumes a single parent Helm chart that manages all MCP servers as sub-charts
        # or an application-of-applications pattern.
        path = "infrastructure/kubernetes/helm/sophia-ecosystem"
        command = f"helm upgrade --install sophia-ecosystem {path} -n sophia-ai --create-namespace -f {path}/values-{self.environment}.yaml"
        await self._run_command(command)
        return {"status": "Helm deployment command executed for all MCP servers."}

    async def _validate_k8s_deployment(self) -> List[Dict[str, str]]:
        """Check the status of all pods in the 'sophia-ai' namespace."""
        logger.info("Validating Kubernetes deployment...")
        command = f"kubectl get pods -n sophia-ai -o json"
        result_json = await self._run_command(command)
        pods = json.loads(result_json).get("items", [])
        
        pod_statuses = []
        for pod in pods:
            pod_statuses.append({
                "name": pod["metadata"]["name"],
                "status": pod["status"]["phase"],
                "ready": all(c["ready"] for c in pod["status"].get("containerStatuses", [])),
            })
        
        if not all(p["status"] == "Running" and p["ready"] for p in pod_statuses):
            logger.warning("Some pods are not in a healthy state.")
        
        return pod_statuses

    async def _run_integration_tests(self) -> str:
        """Trigger integration tests, potentially as a K8s Job."""
        logger.info("Triggering integration test suite...")
        command = "kubectl apply -f infrastructure/kubernetes/tests/integration-test-job.yaml"
        return await self._run_command(command)

    async def _run_command(self, command: str) -> str:
        """Execute a shell command asynchronously and capture output."""
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            return_code = process.returncode if process.returncode is not None else -1
            error_message = f"Command '{command}' failed with exit code {return_code}:\n{stderr.decode()}"
            raise subprocess.CalledProcessError(return_code, command, output=stdout, stderr=stderr)
        
        return stdout.decode()

async def main():
    """Main deployment entrypoint."""
    deployer = EnterpriseAIEcosystemDeployer()
    results = await deployer.deploy_ecosystem()
    
    print("\n🎉 Enterprise AI Ecosystem Deployment Complete!")
    print(f"============== PHOENIX 1.4 DEPLOYMENT REPORT ==============")
    print(json.dumps(results, indent=2))
    print("==========================================================")
    
    if any(phase["status"] == "failed" for phase in results.values()):
        print("\n❌ Deployment finished with errors.")
    else:
        print("\n✅ Deployment completed successfully.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    asyncio.run(main()) 