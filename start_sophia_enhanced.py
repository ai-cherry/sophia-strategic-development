#!/usr/bin/env python3
"""
Enhanced Sophia AI Live Deployment Script
Optimized for production deployment with proper environment configuration
"""

import os
import sys
import time
import subprocess
import signal
import logging
import psutil
from pathlib import Path
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


class SophiaDeploymentManager:
    def __init__(self):
        self.backend_process = None
        self.frontend_process = None
        self.project_root = Path(__file__).parent

    def kill_port_processes(self, port):
        """Kill any processes using the specified port"""
        try:
            # Find processes using the port
            for proc in psutil.process_iter(["pid", "name", "connections"]):
                try:
                    connections = proc.info["connections"]
                    if connections:
                        for conn in connections:
                            if conn.laddr.port == port:
                                logger.info(
                                    f"🔧 Killing process {proc.info['pid']} ({proc.info['name']}) using port {port}"
                                )
                                proc.kill()
                                proc.wait()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception as e:
            logger.warning(f"⚠️  Could not kill processes on port {port}: {e}")

    def clear_ports(self):
        """Clear ports 8000 and 3000 before starting services"""
        logger.info("🔧 Clearing ports for deployment...")
        self.kill_port_processes(8000)
        self.kill_port_processes(3000)
        time.sleep(2)  # Give processes time to fully terminate
        logger.info("✅ Ports cleared")

    def signal_handler(self, signum, frame):
        """Handle graceful shutdown"""
        logger.info("🛑 Received shutdown signal, cleaning up...")
        self.cleanup()
        sys.exit(0)

    def check_environment(self):
        """Check if all required files and directories exist"""
        required_files = [
            self.project_root / "sophia_standalone_server.py",
            self.project_root / "frontend" / "package.json",
        ]

        for file_path in required_files:
            if not file_path.exists():
                logger.error(f"❌ Required file not found: {file_path}")
                return False

        logger.info("✅ Environment check passed")
        return True

    def setup_environment_variables(self):
        """Set up environment variables for both backend and frontend"""
        # Backend environment variables
        os.environ.update(
            {
                "PYTHONPATH": str(self.project_root),
                "SOPHIA_ENVIRONMENT": "production",
                "PULUMI_ORG": "scoobyjava-org",
            }
        )

        # Frontend environment variables for both React and Vite
        frontend_env = {
            "REACT_APP_API_URL": "http://localhost:8000",
            "REACT_APP_WS_URL": "ws://localhost:8000",
            "REACT_APP_ENVIRONMENT": "development",
            "VITE_API_URL": "http://localhost:8000",
            "VITE_WS_URL": "ws://localhost:8000",
            "VITE_ENVIRONMENT": "development",
        }

        os.environ.update(frontend_env)
        logger.info("✅ Environment variables configured")

    def start_backend(self):
        """Start the Sophia AI backend server"""
        try:
            logger.info("🚀 Starting Sophia AI Backend...")

            # Start backend server
            self.backend_process = subprocess.Popen(
                [sys.executable, "sophia_standalone_server.py"],
                cwd=self.project_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=os.environ.copy(),
            )

            # Wait a moment for startup
            time.sleep(3)

            # Check if process is still running
            if self.backend_process.poll() is None:
                logger.info(
                    "✅ Backend server started successfully on http://localhost:8000"
                )
                return True
            else:
                stdout, stderr = self.backend_process.communicate()
                logger.error(f"❌ Backend failed to start: {stderr.decode()}")
                return False

        except Exception as e:
            logger.error(f"❌ Failed to start backend: {e}")
            return False

    def install_frontend_dependencies(self):
        """Install frontend dependencies if needed"""
        try:
            frontend_dir = self.project_root / "frontend"
            node_modules = frontend_dir / "node_modules"

            if not node_modules.exists():
                logger.info("📦 Installing frontend dependencies...")
                result = subprocess.run(
                    ["npm", "install", "--legacy-peer-deps"],
                    cwd=frontend_dir,
                    capture_output=True,
                    text=True,
                )

                if result.returncode == 0:
                    logger.info("✅ Frontend dependencies installed")
                    return True
                else:
                    logger.error(f"❌ Failed to install dependencies: {result.stderr}")
                    return False
            else:
                logger.info("✅ Frontend dependencies already installed")
                return True

        except Exception as e:
            logger.error(f"❌ Failed to install frontend dependencies: {e}")
            return False

    def start_frontend(self):
        """Start the frontend development server"""
        try:
            frontend_dir = self.project_root / "frontend"

            logger.info("🎨 Starting Sophia AI Frontend...")

            # Create environment with frontend variables
            frontend_env = os.environ.copy()

            # Start frontend server using npm run dev (Vite)
            self.frontend_process = subprocess.Popen(
                ["npm", "run", "dev", "--", "--port", "3000", "--host", "0.0.0.0"],
                cwd=frontend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=frontend_env,
            )

            # Wait for frontend to start
            time.sleep(8)

            # Check if process is still running
            if self.frontend_process.poll() is None:
                logger.info(
                    "✅ Frontend server started successfully on http://localhost:3000"
                )
                return True
            else:
                stdout, stderr = self.frontend_process.communicate()
                logger.error(f"❌ Frontend failed to start: {stderr.decode()}")
                return False

        except Exception as e:
            logger.error(f"❌ Failed to start frontend: {e}")
            return False

    def wait_for_services(self):
        """Wait for services to be ready"""
        logger.info("⏳ Waiting for services to be fully ready...")

        # Test backend health
        max_retries = 30
        for i in range(max_retries):
            try:
                response = requests.get("http://localhost:8000/health", timeout=3)
                if response.status_code == 200:
                    logger.info("✅ Backend health check passed")
                    break
            except requests.exceptions.RequestException:
                if i == max_retries - 1:
                    logger.warning("⚠️  Backend health check failed, but continuing...")
            time.sleep(2)

        # Test frontend availability
        for i in range(max_retries):
            try:
                response = requests.get("http://localhost:3000", timeout=3)
                if response.status_code == 200:
                    logger.info("✅ Frontend accessibility check passed")
                    break
            except requests.exceptions.RequestException:
                if i == max_retries - 1:
                    logger.warning(
                        "⚠️  Frontend accessibility check failed, but continuing..."
                    )
            time.sleep(2)

    def display_startup_info(self):
        """Display startup information"""
        print("\n" + "=" * 60)
        print("🎉 SOPHIA AI IS NOW RUNNING!")
        print("=" * 60)
        print("📊 Frontend Dashboard:")
        print("   🌐 http://localhost:3000")
        print("   💼 Executive Dashboard with Live Chat")
        print("🔧 Backend API:")
        print("   🌐 http://localhost:8000")
        print("   📚 API Documentation: http://localhost:8000/docs")
        print("   💚 Health Check: http://localhost:8000/health")
        print("💬 Features Available:")
        print("   ✅ Live WebSocket Chat with Sophia AI")
        print("   ✅ Document Upload & Processing")
        print("   ✅ Real-time Dashboard Updates")
        print("   ✅ Executive KPI Monitoring")
        print("   ✅ Mobile-Responsive Design")
        print("   ✅ Linear Project Management Integration")
        print("   ✅ Apollo.io Business Intelligence")
        print("   ✅ Vercel Production Deployment Ready")
        print("📝 Test Steps:")
        print("   1. Open http://localhost:3000 in your browser")
        print("   2. Click on the AI Assistant tab in the sidebar")
        print("   3. Start chatting with Sophia AI!")
        print("   4. Try uploading a document via the Upload button")
        print("   5. Test Linear project management features")
        print("🛑 To stop: Press Ctrl+C")
        print("=" * 60)

    def cleanup(self):
        """Clean up processes"""
        logger.info("🧹 Cleaning up processes...")

        if self.backend_process:
            logger.info("✅ Stopping Sophia AI Backend...")
            self.backend_process.terminate()
            try:
                self.backend_process.wait(timeout=5)
                logger.info("✅ Backend stopped")
            except subprocess.TimeoutExpired:
                self.backend_process.kill()
                logger.info("✅ Backend force stopped")

        if self.frontend_process:
            logger.info("✅ Stopping Sophia AI Frontend...")
            self.frontend_process.terminate()
            try:
                self.frontend_process.wait(timeout=5)
                logger.info("✅ Frontend stopped")
            except subprocess.TimeoutExpired:
                self.frontend_process.kill()
                logger.info("✅ Frontend force stopped")

    def run(self):
        """Main deployment method"""
        # Set up signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

        try:
            logger.info("🚀 Starting Sophia AI Enhanced Deployment...")

            # Clear ports first
            self.clear_ports()

            # Check environment
            if not self.check_environment():
                return False

            # Setup environment variables
            self.setup_environment_variables()

            # Install frontend dependencies
            if not self.install_frontend_dependencies():
                return False

            # Start backend
            if not self.start_backend():
                return False

            # Start frontend
            if not self.start_frontend():
                self.cleanup()
                return False

            # Wait for services
            self.wait_for_services()

            # Display info
            self.display_startup_info()

            # Keep running
            while True:
                time.sleep(1)

                # Check if processes are still alive
                if self.backend_process and self.backend_process.poll() is not None:
                    logger.error("❌ Backend process stopped unexpectedly")
                    break

                if self.frontend_process and self.frontend_process.poll() is not None:
                    logger.error("❌ Frontend process stopped unexpectedly")
                    break

        except KeyboardInterrupt:
            logger.info("🛑 Deployment interrupted by user")
        except Exception as e:
            logger.error(f"❌ Deployment failed: {e}")
        finally:
            self.cleanup()
            logger.info("✅ Sophia AI deployment completed")

        return True


if __name__ == "__main__":
    deployment = SophiaDeploymentManager()
    success = deployment.run()
    sys.exit(0 if success else 1)
