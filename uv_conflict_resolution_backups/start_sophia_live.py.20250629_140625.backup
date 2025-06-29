#!/usr/bin/env python3
"""
Sophia AI Live Deployment Script
Starts both backend and frontend services for immediate testing
"""

import logging
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class SophiaLiveDeployment:
    def __init__(self):
        self.backend_process = None
        self.frontend_process = None
        self.running = True

    def check_environment(self):
        """Check if required dependencies are available"""
        logger.info("🔍 Checking environment...")

        # Check Python version

        # Check if we're in the right directory
        if not Path("backend").exists() or not Path("frontend").exists():
            logger.error("❌ Please run from sophia-main root directory")
            return False

        # Check if frontend dependencies are installed
        if not Path("frontend/node_modules").exists():
            logger.error(
                "❌ Frontend dependencies not installed. Run 'cd frontend && npm install' first"
            )
            return False

        logger.info("✅ Environment check passed")
        return True

    def setup_environment_variables(self):
        """Setup environment variables for development"""
        logger.info(" Setting up environment variables...")

        # Backend environment
        os.environ.update(
            {
                "SOPHIA_ENVIRONMENT": "development",
                "PYTHONPATH": str(Path.cwd() / "backend"),
            }
        )

        logger.info("✅ Environment variables set")

    def start_backend(self):
        """Start the backend server"""
        logger.info("🚀 Starting Sophia AI Backend...")

        try:
            # Use the standalone server for maximum compatibility
            backend_script = Path("sophia_standalone_server.py")
            if backend_script.exists():
                cmd = [sys.executable, str(backend_script)]
            else:
                # Fallback to enhanced chat service
                cmd = [
                    sys.executable,
                    "-m",
                    "uvicorn",
                    "backend.services.enhanced_unified_chat_service:app",
                    "--host",
                    "0.0.0.0",
                    "--port",
                    "8000",
                    "--reload",
                ]

            self.backend_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1,
            )

            logger.info("✅ Backend server starting on http://localhost:8000")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to start backend: {e}")
            return False

    def start_frontend(self):
        """Start the frontend development server"""
        logger.info("🎨 Starting Sophia AI Frontend...")

        try:
            # Set environment variables for frontend
            env = os.environ.copy()
            env.update(
                {
                    "VITE_API_URL": "http://localhost:8000",
                    "VITE_WS_URL": "ws://localhost:8000",
                    "VITE_ENVIRONMENT": "development",
                    # Keep REACT_APP_ for compatibility
                    "REACT_APP_API_URL": "http://localhost:8000",
                    "REACT_APP_WS_URL": "ws://localhost:8000",
                    "REACT_APP_ENVIRONMENT": "development",
                }
            )

            # Use Vite dev command with specific port
            self.frontend_process = subprocess.Popen(
                ["npm", "run", "dev", "--", "--port", "3000", "--host", "0.0.0.0"],
                cwd="frontend",
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1,
            )

            logger.info("✅ Frontend server starting on http://localhost:3000")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to start frontend: {e}")
            return False

    def wait_for_services(self):
        """Wait for services to start"""
        logger.info("⏳ Waiting for services to start...")
        time.sleep(5)  # Give services time to initialize

    def show_access_info(self):
        """Show access information"""
        print("\n" + "=" * 60)
        print("🎉 SOPHIA AI IS NOW RUNNING!")
        print("=" * 60)
        print()
        print("📊 Frontend Dashboard:")
        print("   🌐 http://localhost:3000")
        print("   💼 Executive Dashboard with Live Chat")
        print()
        print("🔧 Backend API:")
        print("   🌐 http://localhost:8000")
        print("   📚 API Documentation: http://localhost:8000/docs")
        print("   💚 Health Check: http://localhost:8000/health")
        print()
        print("💬 Features Available:")
        print("   ✅ Live WebSocket Chat with Sophia AI")
        print("   ✅ Document Upload & Knowledge Base")
        print("   ✅ Real-time Dashboard Updates")
        print("   ✅ Executive KPI Monitoring")
        print()
        print("📝 Test Steps:")
        print("   1. Open http://localhost:3000 in your browser")
        print("   2. Click on the AI Assistant tab in the sidebar")
        print("   3. Start chatting with Sophia AI!")
        print("   4. Try uploading a document via the Upload button")
        print()
        print("🛑 To stop: Press Ctrl+C")
        print("=" * 60)
        print()

    def cleanup(self):
        """Clean up processes"""
        logger.info("🧹 Cleaning up...")
        self.running = False

        if self.backend_process:
            self.backend_process.terminate()
            try:
                self.backend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.backend_process.kill()
            logger.info("✅ Backend stopped")

        if self.frontend_process:
            self.frontend_process.terminate()
            try:
                self.frontend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.frontend_process.kill()
            logger.info("✅ Frontend stopped")

    def run(self):
        """Main deployment process"""
        try:
            # Setup signal handler for graceful shutdown
            def signal_handler(signum, frame):
                logger.info("🛑 Shutdown requested...")
                self.cleanup()
                sys.exit(0)

            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)

            logger.info("🚀 Starting Sophia AI Live Deployment...")

            # Environment checks
            if not self.check_environment():
                return False

            # Setup environment
            self.setup_environment_variables()

            # Start services
            if not self.start_backend():
                return False

            if not self.start_frontend():
                return False

            # Wait for services
            self.wait_for_services()

            # Show access info
            self.show_access_info()

            # Keep running
            try:
                while self.running:
                    # Check if processes are still running
                    if self.backend_process and self.backend_process.poll() is not None:
                        logger.error("❌ Backend process stopped unexpectedly")
                        break
                    if (
                        self.frontend_process
                        and self.frontend_process.poll() is not None
                    ):
                        logger.error("❌ Frontend process stopped unexpectedly")
                        break
                    time.sleep(1)
            except KeyboardInterrupt:
                pass

            return True

        except Exception as e:
            logger.error(f"❌ Deployment failed: {e}")
            return False
        finally:
            self.cleanup()


def main():
    """Main entry point"""
    deployment = SophiaLiveDeployment()
    success = deployment.run()

    if success:
        logger.info("✅ Sophia AI deployment completed successfully")
    else:
        logger.error("❌ Sophia AI deployment failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
