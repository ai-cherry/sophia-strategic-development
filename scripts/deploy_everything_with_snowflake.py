#!/usr/bin/env python3
"""
Deploy Everything with Snowflake Integration
Ensures all services start with proper Snowflake credentials

PERMANENT SCRIPT - DO NOT DELETE
This is a reusable deployment tool for the full Sophia AI stack
"""

import os
import sys
import subprocess
import time
from pathlib import Path
import requests

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class FullDeployment:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.processes = []

        # Snowflake credentials
        self.snowflake_pat = "eyJraWQiOiI1MDg3NDc2OTQxMyIsImFsZyI6IkVTMjU2In0.eyJwIjoiMTk4NzI5NDc2OjUwODc0NzQ1NDc3IiwiaXNzIjoiU0Y6MTA0OSIsImV4cCI6MTc4MjI4MDQ3OH0.8m-fWI5rvCs6b8bvw1quiM-UzW9uPRxMUmE6VAgOFFylAhRkCzch7ojh7CRLeMdii6DD1Owqap0KoOmyxsW77A"

        # Set environment variables
        self.setup_environment()

    def setup_environment(self):
        """Set up all environment variables"""
        env_vars = {
            "SNOWFLAKE_PAT": self.snowflake_pat,
            "SNOWFLAKE_ACCOUNT": "UHDECNO-CVB64222",
            "SNOWFLAKE_USER": "SCOOBYJAVA15",
            "SNOWFLAKE_PASSWORD": self.snowflake_pat,  # Use PAT as password
            "SNOWFLAKE_WAREHOUSE": "SOPHIA_AI_COMPUTE_WH",
            "SNOWFLAKE_DATABASE": "AI_MEMORY",
            "SNOWFLAKE_SCHEMA": "VECTORS",
            "SNOWFLAKE_ROLE": "ACCOUNTADMIN",
            "PYTHONPATH": str(self.project_root),
            "ENVIRONMENT": "prod",
        }

        # Update environment
        for key, value in env_vars.items():
            os.environ[key] = value

        print("✅ Environment configured with Snowflake credentials")

    def kill_existing_processes(self):
        """Kill any existing processes on our ports"""
        ports = [8001, 9001, 3008, 9003, 9004, 9006, 9101, 9102, 5173]

        for port in ports:
            try:
                result = subprocess.run(
                    f"lsof -ti:{port} | xargs kill -9 2>/dev/null || true",
                    shell=True,
                    capture_output=True,
                )
            except:
                pass

        print("✅ Cleaned up existing processes")
        time.sleep(2)

    def start_backend(self):
        """Start the backend API"""
        print("\n🚀 Starting Backend API...")

        backend_cmd = [
            sys.executable,
            str(self.project_root / "backend" / "app" / "unified_chat_backend.py"),
        ]

        process = subprocess.Popen(
            backend_cmd,
            env=os.environ.copy(),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
        )

        self.processes.append(process)

        # Wait for backend to start
        for i in range(30):
            try:
                response = requests.get("http://localhost:8001/health")
                if response.status_code == 200:
                    print("✅ Backend API running on port 8001")
                    return True
            except:
                pass
            time.sleep(1)

        print("❌ Backend failed to start")
        return False

    def start_frontend(self):
        """Start the frontend"""
        print("\n🚀 Starting Frontend...")

        frontend_dir = self.project_root / "frontend"
        if not frontend_dir.exists():
            print("❌ Frontend directory not found")
            return False

        # Change to frontend directory and run npm
        os.chdir(frontend_dir)

        process = subprocess.Popen(
            ["npm", "run", "dev"],
            env=os.environ.copy(),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
        )

        self.processes.append(process)
        print("✅ Frontend starting on port 5173")

        # Change back to project root
        os.chdir(self.project_root)
        return True

    def start_mcp_servers(self):
        """Start all MCP servers with proper environment"""
        print("\n🚀 Starting MCP Servers...")

        mcp_servers = [
            {"name": "ai_memory", "file": "server.py", "port": 9001},
            {"name": "codacy", "file": "server.py", "port": 3008},
            {"name": "github", "file": "server.py", "port": 9003},
            {"name": "asana", "file": "server.py", "port": 9006},
            {"name": "slack", "file": "server.py", "port": 9101},
        ]

        for server in mcp_servers:
            server_path = (
                self.project_root / "mcp-servers" / server["name"] / server["file"]
            )

            if not server_path.exists():
                print(f"⚠️  {server['name']} server file not found")
                continue

            print(f"Starting {server['name']} on port {server['port']}...")

            env = os.environ.copy()
            env["MCP_SERVER_PORT"] = str(server["port"])

            # Ensure logs directory exists
            logs_dir = self.project_root / "logs"
            logs_dir.mkdir(exist_ok=True)

            # Start server
            with open(logs_dir / f"{server['name']}.log", "w") as log_file:
                process = subprocess.Popen(
                    [sys.executable, str(server_path)],
                    env=env,
                    stdout=log_file,
                    stderr=subprocess.STDOUT,
                )

                self.processes.append(process)

        print("✅ MCP servers started")

    def test_snowflake_connection(self):
        """Test Snowflake connection through the API"""
        print("\n🧪 Testing Snowflake Connection...")

        try:
            # Test through the API
            response = requests.post(
                "http://localhost:8001/api/v3/chat",
                json={
                    "message": "Test Snowflake connection and store: Deployment successful on July 10, 2025",
                    "user_id": "test_deployment",
                },
                timeout=30,
            )

            if response.status_code == 200:
                print("✅ Snowflake connection test successful!")
                print(f"   Response: {response.json()}")
                return True
            else:
                print(f"❌ Snowflake test failed: {response.status_code}")
                return False

        except Exception as e:
            print(f"❌ Snowflake test error: {e}")
            return False

    def check_deployment_status(self):
        """Check status of all services"""
        print("\n📊 Deployment Status:")
        print("=" * 60)

        services = [
            {
                "name": "Backend API",
                "url": "http://localhost:8001/health",
                "port": 8001,
            },
            {"name": "Frontend", "url": "http://localhost:5173", "port": 5173},
            {"name": "AI Memory MCP", "url": None, "port": 9001},
            {"name": "Codacy MCP", "url": None, "port": 3008},
            {"name": "GitHub MCP", "url": None, "port": 9003},
        ]

        running_count = 0
        for service in services:
            # Check if port is in use
            result = subprocess.run(
                f"lsof -ti:{service['port']}", shell=True, capture_output=True
            )

            if result.returncode == 0:
                print(f"✅ {service['name']}: Running on port {service['port']}")
                running_count += 1
            else:
                print(f"❌ {service['name']}: Not running")

        print(f"\nTotal: {running_count}/{len(services)} services running")

    def run_deployment(self):
        """Run the full deployment"""
        print("🚀 SOPHIA AI FULL DEPLOYMENT WITH SNOWFLAKE")
        print("=" * 60)

        try:
            # Clean up existing processes
            self.kill_existing_processes()

            # Start backend
            if not self.start_backend():
                print("❌ Backend failed to start, aborting")
                return

            # Start frontend
            self.start_frontend()

            # Start MCP servers
            self.start_mcp_servers()

            # Wait for services to stabilize
            print("\n⏳ Waiting for services to stabilize...")
            time.sleep(5)

            # Check deployment status
            self.check_deployment_status()

            # Test Snowflake
            self.test_snowflake_connection()

            print("\n✅ DEPLOYMENT COMPLETE!")
            print("\nAccess points:")
            print("  Backend API: http://localhost:8001")
            print("  API Docs: http://localhost:8001/docs")
            print("  Frontend: http://localhost:5173")
            print("  Chat API: POST http://localhost:8001/api/v3/chat")

            print("\n📋 Next Steps:")
            print("1. Test chat functionality with Snowflake storage")
            print("2. Configure kubectl for K3s deployment")
            print("3. Add GitHub secrets for automated deployment")

            print("\nPress Ctrl+C to stop all services")

            # Keep running
            while True:
                time.sleep(1)

        except KeyboardInterrupt:
            print("\n\n🛑 Stopping all services...")
            self.cleanup()

    def cleanup(self):
        """Clean up all processes"""
        for process in self.processes:
            try:
                process.terminate()
                process.wait(timeout=5)
            except:
                try:
                    process.kill()
                except:
                    pass

        print("✅ All services stopped")


if __name__ == "__main__":
    deployment = FullDeployment()
    deployment.run_deployment()
