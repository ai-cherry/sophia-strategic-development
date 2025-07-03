#!/usr/bin/env python3
"""
Enterprise AI Ecosystem Live Monitor (Phoenix 1.4)
Connects to Kubernetes to provide a real-time dashboard of all MCP server statuses,
performance metrics, and health checks.
"""

import asyncio
import json
import logging
import curses
from typing import Dict, Any, List
import aiohttp
import time

logger = logging.getLogger(__name__)

class EcosystemMonitor:
    """
    Monitors the health and performance of the Sophia AI ecosystem in Kubernetes.
    """
    
    def __init__(self, namespace: str = "sophia-ai"):
        self.namespace = namespace
        self.pod_ports = {}

    async def _run_command(self, command: str) -> str:
        """Execute a shell command asynchronously."""
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        if process.returncode != 0:
            raise RuntimeError(f"Command failed: {stderr.decode().strip()}")
        return stdout.decode()

    async def find_mcp_pods(self) -> List[Dict[str, Any]]:
        """Find all MCP server pods in the namespace."""
        try:
            result_json = await self._run_command(f"kubectl get pods -n {self.namespace} -l app.kubernetes.io/component=mcp-server -o json")
            pods = json.loads(result_json).get("items", [])
            
            pod_info = []
            for pod in pods:
                pod_info.append({
                    "name": pod["metadata"]["name"],
                    "status": pod["status"]["phase"],
                    "ip": pod["status"].get("podIP"),
                    "port": 80 # Assuming all pods expose on port 80 internally
                })
            return pod_info
        except (json.JSONDecodeError, RuntimeError) as e:
            logger.error(f"Error finding MCP pods: {e}")
            return []

    async def scrape_metrics(self, pod_ip: str, port: int) -> str:
        """Scrape the /metrics endpoint of a pod."""
        url = f"http://{pod_ip}:{port}/metrics"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=2) as response:
                    return await response.text()
        except Exception:
            return "Error: Could not connect to metrics endpoint."

    async def get_health(self, pod_ip: str, port: int) -> Dict[str, Any]:
        """Get the /health endpoint of a pod."""
        url = f"http://{pod_ip}:{port}/health"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=2) as response:
                    return await response.json()
        except Exception:
            return {"healthy": False, "error": "Connection failed"}

    def parse_prometheus_metrics(self, text: str) -> Dict[str, float]:
        """A simple parser for Prometheus text format."""
        metrics = {}
        for line in text.splitlines():
            if line.startswith('#') or not line.strip():
                continue
            parts = line.split()
            if len(parts) >= 2:
                metric_name = parts[0]
                value = float(parts[1])
                metrics[metric_name] = value
        return metrics

    async def monitor_loop(self, stdscr):
        """The main monitoring loop to run with curses."""
        curses.curs_set(0)
        stdscr.nodelay(1)
        stdscr.timeout(1000)

        while True:
            key = stdscr.getch()
            if key == ord('q'):
                break

            stdscr.clear()
            height, width = stdscr.getmaxyx()
            
            try:
                pods = await self.find_mcp_pods()
                
                stdscr.addstr(0, 1, f"Phoenix 1.4 Ecosystem Monitor - Namespace: {self.namespace} (Press 'q' to quit)", curses.A_BOLD)
                
                if not pods:
                    stdscr.addstr(2, 1, "No MCP server pods found in the namespace.")
                else:
                    y = 2
                    for pod in pods:
                        if y >= height -1: break
                        
                        health_data = await self.get_health(pod["ip"], pod["port"])
                        metrics_text = await self.scrape_metrics(pod["ip"], pod["port"])
                        metrics = self.parse_prometheus_metrics(metrics_text)

                        status_char = "✅" if health_data.get("healthy") else "❌"
                        
                        health_str = f"{status_char} {pod['name']} ({pod['status']})"
                        stdscr.addstr(y, 1, health_str, curses.A_BOLD)
                        y += 1

                        req_total = metrics.get(f"sophia_mcp_{pod['name'].split('-')[0]}_requests_total", 0)
                        latency_avg = metrics.get(f"sophia_mcp_{pod['name'].split('-')[0]}_request_duration_seconds_avg", 0)
                        
                        metrics_str = f"    Requests: {req_total:.0f} | Avg Latency: {latency_avg*1000:.2f}ms"
                        if y < height -1 : stdscr.addstr(y, 1, metrics_str) ; y+=1
                        
            except Exception as e:
                stdscr.addstr(2, 1, f"An error occurred: {str(e)[:width-2]}")
                
            stdscr.refresh()
            await asyncio.sleep(1)

def main():
    monitor = EcosystemMonitor()
    curses.wrapper(lambda stdscr: asyncio.run(monitor.monitor_loop(stdscr)))

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    main() 