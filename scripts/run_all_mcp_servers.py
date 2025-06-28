# File: scripts/run_all_mcp_servers.py

import json
import subprocess
import time
import psutil
from pathlib import Path
import logging
import sys
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add project root to path to allow for module imports
project_root = Path.cwd()
sys.path.insert(0, str(project_root))

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
        
        server_script_path = Path.cwd() / "mcp-servers" / server_name / f"{server_name}_mcp_server.py"
        
        if server_script_path.exists():
            env = os.environ.copy()
            env["PYTHONPATH"] = str(project_root) + os.pathsep + env.get("PYTHONPATH", "")
            cmd = ["python", "-m", server_script_path]
            try:
                # We can add logging to a file to see the output of each server
                log_file = Path.cwd() / "logs" / f"{server_name}.log"
                log_file.parent.mkdir(exist_ok=True)
                with open(log_file, 'w') as lf:
                    proc = subprocess.Popen(cmd, env=env, stdout=lf, stderr=lf)
                processes[server_name] = proc
                logger.info(f"Started {server_name} with PID: {proc.pid}")
            except Exception as e:
                logger.error(f"Could not start server {server_name}: {e}")
        else:
            logger.info(f"Server script for '{server_name}' not found at {server_script_path}. Skipping.")

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
