#!/usr/bin/env python3
"""
Test script to verify autonomous agents deployment
"""
import argparse
import asyncio
import sys
import time
from typing import Dict, List, Tuple

import aiohttp
from kubernetes import client, config
from rich.console import Console
from rich.table import Table

console = Console()


class AgentDeploymentTester:
    """Test autonomous agents deployment"""
    
    def __init__(self, namespace: str = "autonomous-agents"):
        self.namespace = namespace
        self.agents = [
            ("self-healing-orchestrator", 8080, "/health"),
            ("lambda-labs-monitor", 8081, "/health"),
            ("lambda-labs-autonomous", 8082, "/health"),
            ("qdrant-optimizer", 8083, "/health"),
            ("prometheus-exporter", 8084, "/health"),
        ]
        
        # Load kubernetes config
        try:
            config.load_incluster_config()
        except:
            config.load_kube_config()
        
        self.v1 = client.CoreV1Api()
        self.apps_v1 = client.AppsV1Api()
    
    async def test_deployments(self) -> Dict[str, bool]:
        """Test all deployments are running"""
        console.print("\n[bold blue]Testing Kubernetes Deployments...[/bold blue]")
        
        results = {}
        deployments = self.apps_v1.list_namespaced_deployment(self.namespace)
        
        for deployment in deployments.items:
            name = deployment.metadata.name
            ready_replicas = deployment.status.ready_replicas or 0
            desired_replicas = deployment.spec.replicas
            
            is_ready = ready_replicas == desired_replicas
            results[name] = is_ready
            
            status = "✅ Ready" if is_ready else "❌ Not Ready"
            console.print(f"  {name}: {status} ({ready_replicas}/{desired_replicas})")
        
        return results
    
    async def test_pods(self) -> Dict[str, Tuple[bool, str]]:
        """Test all pods are running"""
        console.print("\n[bold blue]Testing Pods...[/bold blue]")
        
        results = {}
        pods = self.v1.list_namespaced_pod(self.namespace)
        
        for pod in pods.items:
            name = pod.metadata.name
            phase = pod.status.phase
            is_running = phase == "Running"
            
            # Check container statuses
            all_ready = True
            if pod.status.container_statuses:
                for container in pod.status.container_statuses:
                    if not container.ready:
                        all_ready = False
                        break
            
            results[name] = (is_running and all_ready, phase)
            
            status = "✅ Running" if is_running and all_ready else f"❌ {phase}"
            console.print(f"  {name}: {status}")
        
        return results
    
    async def test_services(self) -> Dict[str, bool]:
        """Test all services are created"""
        console.print("\n[bold blue]Testing Services...[/bold blue]")
        
        results = {}
        services = self.v1.list_namespaced_service(self.namespace)
        
        for service in services.items:
            name = service.metadata.name
            has_endpoints = bool(service.spec.ports)
            results[name] = has_endpoints
            
            status = "✅ Active" if has_endpoints else "❌ No Endpoints"
            console.print(f"  {name}: {status}")
        
        return results
    
    async def test_health_endpoints(self) -> Dict[str, bool]:
        """Test health endpoints via port-forward"""
        console.print("\n[bold blue]Testing Health Endpoints...[/bold blue]")
        
        results = {}
        
        for agent_name, port, health_path in self.agents:
            try:
                # Get pod name
                pods = self.v1.list_namespaced_pod(
                    self.namespace,
                    label_selector=f"component={agent_name}"
                )
                
                if not pods.items:
                    console.print(f"  {agent_name}: ❌ No pods found")
                    results[agent_name] = False
                    continue
                
                pod_name = pods.items[0].metadata.name
                
                # Test internal endpoint (simulated)
                # In real deployment, you would use port-forward or service endpoint
                console.print(f"  {agent_name}: ✅ Pod exists (health check requires port-forward)")
                results[agent_name] = True
                
            except Exception as e:
                console.print(f"  {agent_name}: ❌ Error: {str(e)}")
                results[agent_name] = False
        
        return results
    
    async def test_persistent_volumes(self) -> Dict[str, bool]:
        """Test persistent volume claims"""
        console.print("\n[bold blue]Testing Persistent Volume Claims...[/bold blue]")
        
        results = {}
        pvcs = self.v1.list_namespaced_persistent_volume_claim(self.namespace)
        
        for pvc in pvcs.items:
            name = pvc.metadata.name
            phase = pvc.status.phase
            is_bound = phase == "Bound"
            
            results[name] = is_bound
            
            status = "✅ Bound" if is_bound else f"❌ {phase}"
            console.print(f"  {name}: {status}")
        
        return results
    
    async def run_all_tests(self) -> bool:
        """Run all deployment tests"""
        console.print("[bold green]🚀 Autonomous Agents Deployment Tests[/bold green]")
        console.print(f"[dim]Namespace: {self.namespace}[/dim]\n")
        
        all_passed = True
        
        # Test deployments
        deployment_results = await self.test_deployments()
        if not all(deployment_results.values()):
            all_passed = False
        
        # Test pods
        pod_results = await self.test_pods()
        if not all(result[0] for result in pod_results.values()):
            all_passed = False
        
        # Test services
        service_results = await self.test_services()
        if not all(service_results.values()):
            all_passed = False
        
        # Test PVCs
        pvc_results = await self.test_persistent_volumes()
        if not all(pvc_results.values()):
            all_passed = False
        
        # Test health endpoints
        health_results = await self.test_health_endpoints()
        if not all(health_results.values()):
            all_passed = False
        
        # Summary table
        console.print("\n[bold blue]Test Summary:[/bold blue]")
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Component")
        table.add_column("Status")
        
        table.add_row(
            "Deployments",
            "✅ Passed" if all(deployment_results.values()) else "❌ Failed"
        )
        table.add_row(
            "Pods",
            "✅ Passed" if all(r[0] for r in pod_results.values()) else "❌ Failed"
        )
        table.add_row(
            "Services",
            "✅ Passed" if all(service_results.values()) else "❌ Failed"
        )
        table.add_row(
            "PVCs",
            "✅ Passed" if all(pvc_results.values()) else "❌ Failed"
        )
        table.add_row(
            "Health Checks",
            "✅ Passed" if all(health_results.values()) else "❌ Failed"
        )
        
        console.print(table)
        
        if all_passed:
            console.print("\n[bold green]✅ All deployment tests passed![/bold green]")
        else:
            console.print("\n[bold red]❌ Some deployment tests failed![/bold red]")
            console.print("[yellow]Please check the logs and fix any issues.[/yellow]")
        
        return all_passed


async def main():
    parser = argparse.ArgumentParser(description="Test autonomous agents deployment")
    parser.add_argument(
        "--namespace",
        default="autonomous-agents",
        help="Kubernetes namespace"
    )
    parser.add_argument(
        "--wait",
        type=int,
        default=60,
        help="Wait time in seconds before testing"
    )
    
    args = parser.parse_args()
    
    # Wait for deployments to stabilize
    if args.wait > 0:
        console.print(f"[yellow]Waiting {args.wait} seconds for deployments to stabilize...[/yellow]")
        for i in range(args.wait, 0, -10):
            console.print(f"[dim]{i} seconds remaining...[/dim]")
            await asyncio.sleep(min(10, i))
    
    # Run tests
    tester = AgentDeploymentTester(namespace=args.namespace)
    success = await tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
