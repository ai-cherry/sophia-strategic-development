# File: scripts/monitor_all_mcp_servers.py
import asyncio
import json
import logging
import os
import shlex
import subprocess
import sys
import time
from pathlib import Path

import aiohttp
from rich.console import Console
from rich.table import Table

# Add project root to path
project_root = Path.cwd()
sys.path.insert(0, str(project_root))

from backend.utils.logging import get_logger

console = Console()

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = get_logger(__name__)


async def get_server_health(session, server_name, port):
    """Fetches the health status of a single server."""
    url = f"http://localhost:{port}/health"
    logger.info(f"Checking health for {server_name} at {url}...")
    try:
        async with session.get(url, timeout=2) as response:
            logger.info(f"Received status {response.status} from {server_name}")
            if response.status == 200:
                data = await response.json()
                return {
                    "name": server_name,
                    "port": port,
                    "status": "✅ Online",
                    "details": data,
                }
            else:
                return {
                    "name": server_name,
                    "port": port,
                    "status": "❌ Unhealthy",
                    "details": {"status_code": response.status},
                }
    except TimeoutError:
        logger.warning(f"Timeout connecting to {server_name} at {url}")
        return {
            "name": server_name,
            "port": port,
            "status": "🔥 OFFLINE (Timeout)",
            "details": {},
        }
    except aiohttp.ClientError as e:
        logger.error(f"Client error connecting to {server_name} at {url}: {e}")
        return {
            "name": server_name,
            "port": port,
            "status": "🔥 OFFLINE (Error)",
            "details": {},
        }


def display_dashboard(server_statuses):
    """Displays the monitoring dashboard in the terminal."""
    subprocess.run(shlex.split("clear" if os.name == "posix" else "cls"), check=True)  # SECURITY FIX: Replaced os.system

    table = Table(
        title=f"MCP Server Monitoring Dashboard - Last Updated: {time.strftime('%Y-%m-%d %H:%M:%S')}"
    )
    table.add_column("Server Name", style="cyan", no_wrap=True)
    table.add_column("Port", style="magenta")
    table.add_column("Status", style="green")
    table.add_column("Details", style="yellow")

    for server in sorted(server_statuses, key=lambda x: x["name"]):
        status_style = "green"
        if "Unhealthy" in server["status"]:
            status_style = "yellow"
        if "OFFLINE" in server["status"]:
            status_style = "red"

        details_str = json.dumps(server["details"], indent=2)
        table.add_row(
            server["name"],
            str(server["port"]),
            f"[{status_style}]{server['status']}[/{status_style}]",
            details_str,
        )

    console.print(table)


async def main():
    """Main monitoring loop."""
    ports_config_path = Path.cwd() / "config" / "mcp_ports.json"
    if not ports_config_path.exists():
        console.print("[bold red]Port configuration file not found.[/bold red]")
        return

    with open(ports_config_path) as f:
        ports_config = json.load(f)

    servers_to_monitor = list(ports_config.get("servers", {}).items())

    async with aiohttp.ClientSession() as session:
        while True:
            try:
                tasks = [
                    get_server_health(session, name, port)
                    for name, port in servers_to_monitor
                ]
                results = await asyncio.gather(*tasks)
                display_dashboard(results)
                await asyncio.sleep(5)  # Refresh every 5 seconds
            except KeyboardInterrupt:
                console.print("\n[bold]Monitoring stopped.[/bold]")
                break


if __name__ == "__main__":
    asyncio.run(main())
