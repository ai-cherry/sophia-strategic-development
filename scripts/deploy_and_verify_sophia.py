#!/usr/bin/env python3
"""
Comprehensive Sophia AI deployment script with verification
"""
import os
import sys
import time
import subprocess
import requests
import psutil
from pathlib import Path
from typing import Dict, Optional

# Base paths
BASE_DIR = Path(__file__).parent.parent
BACKEND_DIR = BASE_DIR / "backend"
FRONTEND_DIR = BASE_DIR / "frontend"
MCP_SERVERS_DIR = BASE_DIR / "mcp-servers"

# Service configuration
SERVICES = {
    "backend": {
        "name": "Backend API",
        "port": 8001,
        "health_url": "http://localhost:8001/health",
        "start_cmd": ["python", "backend/app/unified_chat_backend.py"],
        "cwd": BASE_DIR,
        "env_file": "local.env",
    },
    "frontend": {
        "name": "Frontend Dashboard",
        "port": 5173,
        "health_url": "http://localhost:5173",
        "start_cmd": ["npm", "run", "dev"],
        "cwd": FRONTEND_DIR,
        "skip_health_check": True,  # Frontend might not have a health endpoint
    },
}

# MCP Server mapping (actual file names)
MCP_SERVERS = {
    "ai_memory": {"port": 9001, "file": "server.py", "name": "AI Memory"},
    "codacy": {"port": 3008, "file": "server.py", "name": "Codacy"},
    "github": {"port": 9003, "file": "server.py", "name": "GitHub"},
    "linear": {"port": 9004, "file": "server.py", "name": "Linear"},
    "asana": {"port": 9006, "file": "server.py", "name": "Asana"},
    "notion": {"port": 9102, "file": "server.py", "name": "Notion"},
    "slack": {"port": 9101, "file": "server.py", "name": "Slack"},
}

# Track running processes
running_processes = {}


def print_status(message: str, status: str = "INFO"):
    """Print formatted status message"""
    colors = {
        "INFO": "\033[94m",
        "SUCCESS": "\033[92m",
        "WARNING": "\033[93m",
        "ERROR": "\033[91m",
        "HEADER": "\033[95m",
    }
    color = colors.get(status, "")
    reset = "\033[0m"
    print(f"{color}[{status}] {message}{reset}")


def check_port(port: int) -> bool:
    """Check if a port is in use"""
    for conn in psutil.net_connections():
        if conn.laddr.port == port and conn.status == "LISTEN":
            return True
    return False


def kill_port(port: int):
    """Kill process on a specific port"""
    for proc in psutil.process_iter(["pid", "name"]):
        try:
            for conn in proc.connections():
                if conn.laddr.port == port:
                    print_status(
                        f"Killing process {proc.info['name']} (PID: {proc.info['pid']}) on port {port}",
                        "WARNING",
                    )
                    proc.kill()
                    time.sleep(1)
                    return
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue


def check_redis() -> bool:
    """Check if Redis is running"""
    try:
        import redis

        r = redis.Redis(host="localhost", port=6379)
        r.ping()
        return True
    except:
        return False


def start_redis():
    """Start Redis if not running"""
    if not check_redis():
        print_status("Starting Redis...", "INFO")
        subprocess.Popen(
            ["redis-server"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        time.sleep(2)
        if check_redis():
            print_status("Redis started successfully", "SUCCESS")
        else:
            print_status("Failed to start Redis", "ERROR")
            return False
    else:
        print_status("Redis is already running", "SUCCESS")
    return True


def load_env_file(env_file: str) -> Dict[str, str]:
    """Load environment variables from file"""
    env_vars = os.environ.copy()
    env_path = BASE_DIR / env_file
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    # Remove quotes if present
                    value = value.strip('"').strip("'")
                    env_vars[key] = value
        print_status(f"Loaded environment from {env_file}", "SUCCESS")
    return env_vars


def verify_service_health(url: str, timeout: int = 30) -> bool:
    """Verify a service is healthy by checking its health endpoint"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return True
        except requests.exceptions.RequestException:
            pass
        time.sleep(1)
    return False


def start_service(service_id: str, config: Dict) -> Optional[subprocess.Popen]:
    """Start a service and return the process"""
    print_status(f"Starting {config['name']}...", "INFO")

    # Kill any existing process on the port
    if config.get("port"):
        kill_port(config["port"])

    # Prepare environment
    env = os.environ.copy()
    if config.get("env_file"):
        env.update(load_env_file(config["env_file"]))

    # Start the process
    try:
        process = subprocess.Popen(
            config["start_cmd"],
            cwd=config.get("cwd", BASE_DIR),
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        # Give it time to start
        time.sleep(3)

        # Check if process is still running
        if process.poll() is None:
            # Verify health if endpoint is available
            if not config.get("skip_health_check") and config.get("health_url"):
                if verify_service_health(config["health_url"]):
                    print_status(
                        f"{config['name']} is healthy on port {config.get('port', 'N/A')}",
                        "SUCCESS",
                    )
                    return process
                else:
                    print_status(
                        f"{config['name']} started but health check failed", "WARNING"
                    )
                    return process
            else:
                # Just check if port is listening
                if config.get("port") and check_port(config["port"]):
                    print_status(
                        f"{config['name']} is running on port {config['port']}",
                        "SUCCESS",
                    )
                    return process
                else:
                    print_status(f"{config['name']} process started", "SUCCESS")
                    return process
        else:
            # Process died, get error output
            _, stderr = process.communicate()
            print_status(f"{config['name']} failed to start: {stderr[:200]}", "ERROR")
            return None

    except Exception as e:
        print_status(f"Failed to start {config['name']}: {str(e)}", "ERROR")
        return None


def start_mcp_server(server_id: str, config: Dict) -> Optional[subprocess.Popen]:
    """Start an MCP server"""
    server_path = MCP_SERVERS_DIR / server_id / config["file"]
    if not server_path.exists():
        print_status(f"MCP server file not found: {server_path}", "WARNING")
        return None

    server_config = {
        "name": f"{config['name']} MCP Server",
        "port": config["port"],
        "start_cmd": ["python", str(server_path)],
        "cwd": MCP_SERVERS_DIR / server_id,
        "env_file": "local.env",
    }

    # Set MCP server port in environment
    os.environ[f"MCP_{server_id.upper()}_PORT"] = str(config["port"])

    return start_service(f"mcp_{server_id}", server_config)


def verify_deployment() -> Dict[str, bool]:
    """Verify all services are running"""
    print_status("\n=== VERIFYING DEPLOYMENT ===", "HEADER")

    status = {}

    # Check main services
    for service_id, config in SERVICES.items():
        if config.get("port"):
            is_running = check_port(config["port"])
            status[service_id] = is_running

            # Additional health check
            if (
                is_running
                and config.get("health_url")
                and not config.get("skip_health_check")
            ):
                is_healthy = verify_service_health(config["health_url"], timeout=5)
                if is_healthy:
                    print_status(
                        f"✅ {config['name']}: Running and healthy on port {config['port']}",
                        "SUCCESS",
                    )
                else:
                    print_status(
                        f"⚠️  {config['name']}: Running on port {config['port']} but health check failed",
                        "WARNING",
                    )
            elif is_running:
                print_status(
                    f"✅ {config['name']}: Running on port {config['port']}", "SUCCESS"
                )
            else:
                print_status(f"❌ {config['name']}: Not running", "ERROR")

    # Check MCP servers
    for server_id, config in MCP_SERVERS.items():
        is_running = check_port(config["port"])
        status[f"mcp_{server_id}"] = is_running
        if is_running:
            print_status(
                f"✅ {config['name']} MCP: Running on port {config['port']}", "SUCCESS"
            )
        else:
            print_status(f"❌ {config['name']} MCP: Not running", "ERROR")

    # Check Redis
    redis_running = check_redis()
    status["redis"] = redis_running
    if redis_running:
        print_status("✅ Redis: Running", "SUCCESS")
    else:
        print_status("❌ Redis: Not running", "ERROR")

    return status


def main():
    print_status(
        "🚀 Starting Sophia AI Full Stack Deployment with Verification", "HEADER"
    )

    # Change to project directory
    os.chdir(BASE_DIR)

    # Check dependencies
    print_status("Checking dependencies...", "INFO")

    # Start Redis
    if not start_redis():
        print_status("Redis is required. Please install Redis and try again.", "ERROR")
        sys.exit(1)

    # Start main services
    for service_id, config in SERVICES.items():
        process = start_service(service_id, config)
        if process:
            running_processes[service_id] = process
        else:
            print_status(f"Failed to start {config['name']}", "ERROR")

    # Start MCP servers
    print_status("\nStarting MCP servers...", "INFO")
    for server_id, config in MCP_SERVERS.items():
        process = start_mcp_server(server_id, config)
        if process:
            running_processes[f"mcp_{server_id}"] = process

    # Wait a bit for everything to stabilize
    time.sleep(5)

    # Verify deployment
    status = verify_deployment()

    # Summary
    total_services = len(status)
    running_services = sum(1 for v in status.values() if v)

    print_status("\n=== DEPLOYMENT SUMMARY ===", "HEADER")
    print_status(f"Services running: {running_services}/{total_services}", "INFO")

    if running_services == total_services:
        print_status("🎉 All services are running successfully!", "SUCCESS")
    elif running_services > 0:
        print_status(
            f"⚠️  {running_services} services are running, {total_services - running_services} failed",
            "WARNING",
        )
    else:
        print_status("❌ No services are running", "ERROR")

    # Print access URLs
    if status.get("frontend"):
        print_status(
            f"\nFrontend: http://localhost:{SERVICES['frontend']['port']}", "INFO"
        )
    if status.get("backend"):
        print_status(
            f"Backend API: http://localhost:{SERVICES['backend']['port']}", "INFO"
        )
        print_status(
            f"API Docs: http://localhost:{SERVICES['backend']['port']}/docs", "INFO"
        )

    # Wait for Ctrl+C
    if running_services > 0:
        print_status("\nPress Ctrl+C to stop all services", "INFO")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print_status("\nShutting down services...", "WARNING")
            for process_id, process in running_processes.items():
                if process.poll() is None:
                    process.terminate()
                    print_status(f"Stopped {process_id}", "INFO")


if __name__ == "__main__":
    main()
