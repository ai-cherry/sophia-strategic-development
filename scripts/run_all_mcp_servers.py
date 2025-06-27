# File: scripts/run_all_mcp_servers.py

import json
import subprocess
import time
import psutil
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_process_by_port(port):
    """Find a process using a specific port."""
    for proc in psutil.process_iter(['pid', 'name', 'connections']):
        try:
            for conn in proc.connections(kind='inet'):
                if conn.laddr.port == port:
                    return proc
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return None

def kill_process_by_port(port):
    """Kills any process currently using the specified port."""
    proc = get_process_by_port(port)
    if proc:
        logger.info(f"Killing process {proc.name()} (PID: {proc.pid}) using port {port}.")
        proc.kill()
        proc.wait(timeout=3)

def main():
    """Starts all MCP servers defined in the port configuration."""
    ports_config_path = Path.cwd() / "config" / "mcp_ports.json"
    if not ports_config_path.exists():
        logger.error("Port configuration file not found at config/mcp_ports.json")
        return

    with open(ports_config_path, 'r') as f:
        ports_config = json.load(f)

    servers_to_run = ports_config.get("servers", {})
    processes = {}

    logger.info("--- Starting All MCP Servers ---")

    for server_name, port in servers_to_run.items():
        logger.info(f"--- Preparing to start {server_name} on port {port} ---")
        kill_process_by_port(port)
        
        # This assumes a convention where the server's main script is in mcp-servers/{server_name}/
        # and is runnable. This is a simplification. A real script might read this
        # command from another config file.
        # For now, we only start the servers we have implemented.
        implemented_servers = ["codacy", "snowflake_admin"]
        if server_name in implemented_servers:
            cmd = ["python", "-m", f"mcp-servers.{server_name}.{server_name}_mcp_server"]
            try:
                proc = subprocess.Popen(cmd)
                processes[server_name] = proc
                logger.info(f"Started {server_name} with PID: {proc.pid}")
            except FileNotFoundError:
                logger.error(f"Could not find the script for server: {server_name}. Skipping.")
        else:
            logger.info(f"Server '{server_name}' is not implemented yet. Skipping.")

    logger.info("\n--- All implemented MCP servers have been started. ---")
    logger.info("Press Ctrl+C to stop all servers.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("\n--- Shutting down all MCP servers ---")
        for server_name, proc in processes.items():
            logger.info(f"Stopping {server_name}...")
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
        logger.info("--- All servers stopped. ---")

if __name__ == "__main__":
    main() 