#!/usr/bin/env python3
"""
🎯 SOPHIA AI FULL STACK DEPLOYMENT SCRIPT
Complete deployment automation for all components

This script handles:
1. Environment setup
2. Backend deployment
3. Frontend deployment  
4. MCP server deployment
5. K8s deployment (if kubectl configured)
"""

import os
import sys
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Optional
import requests
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class SophiaDeployment:
    """Main deployment orchestrator for Sophia AI"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.env_vars = {}
        self.processes = []
        self.errors = []

    def load_environment(self) -> bool:
        """Load environment variables from local.env"""
        env_file = self.project_root / "local.env"
        if not env_file.exists():
            logger.error("local.env file not found!")
            return False

        logger.info("Loading environment from local.env...")
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    self.env_vars[key] = value
                    os.environ[key] = value

        logger.info(f"Loaded {len(self.env_vars)} environment variables")
        return True

    def check_dependencies(self) -> bool:
        """Check if all required dependencies are installed"""
        logger.info("Checking dependencies...")

        # Check Python dependencies
        required_packages = [
            "fastapi",
            "uvicorn",
            "redis",
            "snowflake-connector-python",
            "aiohttp",
            "prometheus-client",
        ]
        missing = []

        for package in required_packages:
            try:
                __import__(package.replace("-", "_"))
            except ImportError:
                missing.append(package)

        if missing:
            logger.error(f"Missing Python packages: {missing}")
            logger.info("Installing missing packages...")
            subprocess.run(
                [sys.executable, "-m", "pip", "install"] + missing, check=True
            )

        # Check Node.js for frontend
        try:
            result = subprocess.run(
                ["node", "--version"], capture_output=True, text=True
            )
            logger.info(f"Node.js version: {result.stdout.strip()}")
        except FileNotFoundError:
            logger.error("Node.js not found! Please install Node.js")
            return False

        return True

    def start_redis(self) -> bool:
        """Start Redis if not running"""
        logger.info("Checking Redis...")
        try:
            import redis

            r = redis.Redis(host="localhost", port=6379)
            r.ping()
            logger.info("Redis is already running")
            return True
        except:
            logger.info("Starting Redis...")
            try:
                # Try to start Redis in background
                if sys.platform == "darwin":  # macOS
                    subprocess.Popen(
                        ["redis-server"],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                else:
                    subprocess.Popen(["redis-server", "--daemonize", "yes"])
                time.sleep(2)
                return True
            except:
                logger.warning("Could not start Redis. Please start it manually.")
                return True  # Continue anyway

    def kill_port(self, port: int):
        """Kill process on a specific port"""
        try:
            if sys.platform == "darwin":  # macOS
                result = subprocess.run(
                    ["lsof", "-ti", f":{port}"], capture_output=True, text=True
                )
                if result.stdout.strip():
                    pids = result.stdout.strip().split("\n")
                    for pid in pids:
                        subprocess.run(["kill", "-9", pid])
                    logger.info(f"Killed process on port {port}")
        except:
            pass

    def start_backend(self) -> Optional[subprocess.Popen]:
        """Start the backend service"""
        logger.info("Starting backend...")

        # Kill any existing process on port 8001
        self.kill_port(8001)
        time.sleep(1)

        backend_script = (
            self.project_root / "backend" / "app" / "unified_chat_backend.py"
        )
        if not backend_script.exists():
            logger.error(f"Backend script not found: {backend_script}")
            return None

        try:
            process = subprocess.Popen(
                [sys.executable, str(backend_script)],
                cwd=str(self.project_root),
                env=os.environ.copy(),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1,
            )

            # Wait for startup
            logger.info("Waiting for backend to start...")
            for i in range(30):
                try:
                    response = requests.get("http://localhost:8001/health")
                    if response.status_code == 200:
                        logger.info("✅ Backend is running on port 8001")
                        return process
                except:
                    pass
                time.sleep(1)

            logger.error("Backend failed to start within 30 seconds")
            return None

        except Exception as e:
            logger.error(f"Failed to start backend: {e}")
            return None

    def start_frontend(self) -> Optional[subprocess.Popen]:
        """Start the frontend service"""
        logger.info("Starting frontend...")

        # Kill any existing process on port 3000
        self.kill_port(3000)
        time.sleep(1)

        frontend_dir = self.project_root / "frontend"
        if not frontend_dir.exists():
            logger.error(f"Frontend directory not found: {frontend_dir}")
            return None

        try:
            # Install dependencies if needed
            if not (frontend_dir / "node_modules").exists():
                logger.info("Installing frontend dependencies...")
                subprocess.run(["npm", "install"], cwd=str(frontend_dir), check=True)

            # Start frontend
            process = subprocess.Popen(
                ["npm", "run", "dev"],
                cwd=str(frontend_dir),
                env=os.environ.copy(),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1,
            )

            # Wait for startup
            logger.info("Waiting for frontend to start...")
            for i in range(30):
                try:
                    response = requests.get("http://localhost:3000")
                    if response.status_code == 200:
                        logger.info("✅ Frontend is running on port 3000")
                        return process
                except:
                    pass
                time.sleep(1)

            logger.warning("Frontend may still be starting...")
            return process

        except Exception as e:
            logger.error(f"Failed to start frontend: {e}")
            return None

    def start_mcp_servers(self) -> List[subprocess.Popen]:
        """Start MCP servers"""
        logger.info("Starting MCP servers...")
        processes = []

        mcp_servers = [
            ("ai_memory", 9001),
            ("codacy", 3008),
            ("github", 9003),
            ("linear", 9004),
            ("asana", 9006),
            ("notion", 9102),
            ("slack", 9101),
        ]

        for server_name, port in mcp_servers:
            logger.info(f"Starting {server_name} MCP server on port {port}")

            # Kill any existing process
            self.kill_port(port)
            time.sleep(0.5)

            server_file = (
                self.project_root
                / "mcp-servers"
                / server_name
                / f"{server_name}_mcp_server.py"
            )
            if not server_file.exists():
                logger.warning(f"MCP server file not found: {server_file}")
                continue

            try:
                process = subprocess.Popen(
                    [sys.executable, str(server_file)],
                    cwd=str(self.project_root),
                    env=os.environ.copy(),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True,
                    bufsize=1,
                )
                processes.append(process)
                logger.info(f"Started {server_name} MCP server")

            except Exception as e:
                logger.error(f"Failed to start {server_name} MCP server: {e}")

        return processes

    def check_services_health(self) -> Dict[str, bool]:
        """Check health of all services"""
        logger.info("\nChecking service health...")
        health = {}

        # Check backend
        try:
            response = requests.get("http://localhost:8001/health", timeout=5)
            health["backend"] = response.status_code == 200
        except:
            health["backend"] = False

        # Check frontend
        try:
            response = requests.get("http://localhost:3000", timeout=5)
            health["frontend"] = response.status_code == 200
        except:
            health["frontend"] = False

        # Check MCP servers
        mcp_ports = {
            "ai_memory": 9001,
            "codacy": 3008,
            "github": 9003,
            "linear": 9004,
        }

        for name, port in mcp_ports.items():
            try:
                response = requests.get(f"http://localhost:{port}/health", timeout=2)
                health[f"mcp_{name}"] = response.status_code == 200
            except:
                health[f"mcp_{name}"] = False

        return health

    def generate_k8s_manifests(self):
        """Generate Kubernetes manifests for deployment"""
        logger.info("Generating Kubernetes manifests...")

        k8s_dir = self.project_root / "k8s"
        k8s_dir.mkdir(exist_ok=True)

        # Create namespace
        namespace_manifest = {
            "apiVersion": "v1",
            "kind": "Namespace",
            "metadata": {"name": "sophia-ai-prod"},
        }

        with open(k8s_dir / "namespace.yaml", "w") as f:
            import yaml

            yaml.dump(namespace_manifest, f)

        logger.info(f"Generated K8s manifests in {k8s_dir}")

    def deploy(self):
        """Main deployment orchestration"""
        logger.info("🚀 Starting Sophia AI Full Stack Deployment")

        # Step 1: Load environment
        if not self.load_environment():
            logger.error("Failed to load environment")
            return

        # Step 2: Check dependencies
        if not self.check_dependencies():
            logger.error("Dependency check failed")
            return

        # Step 3: Start Redis
        self.start_redis()

        # Step 4: Start backend
        backend_process = self.start_backend()
        if backend_process:
            self.processes.append(backend_process)
        else:
            logger.warning("Backend failed to start, continuing...")

        # Step 5: Start frontend
        frontend_process = self.start_frontend()
        if frontend_process:
            self.processes.append(frontend_process)

        # Step 6: Start MCP servers
        mcp_processes = self.start_mcp_servers()
        self.processes.extend(mcp_processes)

        # Step 7: Check health
        time.sleep(5)
        health = self.check_services_health()

        logger.info("\n=== DEPLOYMENT STATUS ===")
        for service, is_healthy in health.items():
            status = "✅" if is_healthy else "❌"
            logger.info(
                f"{status} {service}: {'Running' if is_healthy else 'Not running'}"
            )

        # Step 8: Generate K8s manifests
        self.generate_k8s_manifests()

        logger.info("\n=== DEPLOYMENT COMPLETE ===")
        logger.info("Frontend: http://localhost:3000")
        logger.info("Backend API: http://localhost:8001")
        logger.info("API Docs: http://localhost:8001/docs")
        logger.info("\nPress Ctrl+C to stop all services")

        # Keep running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("\nShutting down services...")
            for process in self.processes:
                process.terminate()
            logger.info("All services stopped")


if __name__ == "__main__":
    deployer = SophiaDeployment()
    deployer.deploy()
