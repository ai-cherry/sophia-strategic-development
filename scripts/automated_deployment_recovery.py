#!/usr/bin/env python3
"""
Sophia AI Automated Deployment Recovery System
Handles common deployment issues automatically with health checking and recovery.
"""

import os
import sys
import subprocess
import time
import json
import requests
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('deployment_recovery.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SophiaDeploymentRecovery:
    """Automated deployment recovery and health management"""
    
    def __init__(self):
        self.root_dir = Path(__file__).parent.parent
        self.frontend_dir = self.root_dir / "frontend"
        self.backend_dir = self.root_dir / "backend"
        self.max_retries = 3
        self.health_check_timeout = 30
        
    def run_command(self, cmd: str, cwd: Optional[Path] = None, timeout: int = 120) -> Tuple[bool, str]:
        """Run shell command with error handling"""
        try:
            logger.info(f"Running: {cmd}")
            result = subprocess.run(
                cmd,
                shell=True,
                cwd=cwd or self.root_dir,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            if result.returncode == 0:
                logger.info(f"✅ Command succeeded: {cmd}")
                return True, result.stdout
            else:
                logger.error(f"❌ Command failed: {cmd}")
                logger.error(f"Error: {result.stderr}")
                return False, result.stderr
                
        except subprocess.TimeoutExpired:
            logger.error(f"⏰ Command timed out: {cmd}")
            return False, "Command timed out"
        except Exception as e:
            logger.error(f"💥 Command exception: {cmd} - {e}")
            return False, str(e)
    
    def check_health_endpoint(self, url: str, timeout: int = 10) -> bool:
        """Check if health endpoint is responding"""
        try:
            response = requests.get(url, timeout=timeout)
            return response.status_code == 200
        except:
            return False
    
    def frontend_recovery(self) -> bool:
        """Comprehensive frontend recovery process - fixes 'Invalid package config ms/package.json' error"""
        logger.info("🔧 Starting Frontend Recovery Process")
        
        # Verify we're in the right place
        if not self.frontend_dir.exists():
            logger.error(f"❌ Frontend directory not found: {self.frontend_dir}")
            return False
            
        logger.info(f"📁 Working in frontend directory: {self.frontend_dir}")
        
        steps = [
            ("Kill existing frontend processes", "pkill -f 'vite\\|npm\\|node'", self.root_dir),
            ("Clear npm cache (global)", "npm cache clean --force", self.root_dir),  
            ("Remove corrupted node_modules", "rm -rf node_modules", self.frontend_dir),
            ("Remove package-lock.json", "rm -f package-lock.json", self.frontend_dir),
            ("Remove yarn.lock if exists", "rm -f yarn.lock", self.frontend_dir),
            ("Clear node cache", "rm -rf ~/.npm", self.root_dir),
            ("Reinstall dependencies fresh", "npm install", self.frontend_dir),
            ("Verify install integrity", "npm ls --depth=0", self.frontend_dir),
        ]
        
        for step_name, cmd, cwd in steps:
            logger.info(f"📋 {step_name}")
            success, output = self.run_command(cmd, cwd)
            if not success:
                if "no matching processes" in output.lower() or "ENOENT" in output:
                    logger.info(f"ℹ️ {step_name} - {output.strip()}")
                else:
                    logger.warning(f"⚠️ {step_name} had issues: {output.strip()}")
            else:
                logger.info(f"✅ {step_name} completed")
            time.sleep(2)
        
        # Specific fix for ms package corruption issue
        ms_package_path = self.frontend_dir / "node_modules" / "ms" / "package.json"
        if ms_package_path.exists():
            logger.info("🔍 Checking ms package.json integrity")
            try:
                with open(ms_package_path, 'r') as f:
                    json.load(f)  # Try to parse JSON
                logger.info("✅ ms package.json is valid")
            except json.JSONDecodeError:
                logger.warning("⚠️ ms package.json corrupted, reinstalling ms package")
                self.run_command("npm uninstall ms && npm install ms", self.frontend_dir)
        
        return True
    
    def backend_recovery(self) -> bool:
        """Comprehensive backend recovery process based on current error logs"""
        logger.info("🔧 Starting Backend Recovery Process")
        
        # Current missing dependencies from actual terminal errors
        required_packages = [
            "sqlalchemy",           # ModuleNotFoundError: No module named 'sqlalchemy' 
            "PyJWT",               # ModuleNotFoundError: No module named 'jwt' (package is PyJWT)
            "passlib[bcrypt]",     # ModuleNotFoundError: No module named 'passlib'
            "aiofiles", 
            "python-multipart",
            "email-validator",
            "qdrant-client",
            "uvicorn[standard]",
            "fastapi",
            "redis",
            "psycopg2-binary",
            "asyncpg",
            "python-dotenv",
            "httpx",
            "pydantic[email]"
        ]
        
        # Kill existing backend processes
        logger.info("🔪 Killing existing backend processes")
        self.run_command("pkill -f 'uvicorn\\|fastapi'")
        time.sleep(3)
        
        # Install all dependencies at once for better resolution
        logger.info(f"📦 Installing all backend dependencies: {len(required_packages)} packages")
        packages_str = " ".join(required_packages)
        success, output = self.run_command(f"pip3 install --upgrade {packages_str}", timeout=180)
        
        if not success:
            logger.error(f"❌ Failed to install packages: {output}")
            # Try installing individually as fallback
            logger.info("🔄 Trying individual package installation...")
            for package in required_packages:
                logger.info(f"📦 Installing {package}")
                individual_success, individual_output = self.run_command(f"pip3 install --upgrade {package}")
                if not individual_success:
                    logger.warning(f"⚠️ Failed to install {package}: {individual_output}")
        else:
            logger.info("✅ All backend dependencies installed successfully")
        
        return True
    
    def mcp_recovery(self) -> bool:
        """Recovery for MCP servers"""
        logger.info("🔧 Starting MCP Recovery Process")
        
        # Kill existing MCP processes
        self.run_command("pkill -f 'mcp\\|anthropic'")
        time.sleep(3)
        
        # Check if MCP startup script exists
        mcp_script = self.root_dir / "scripts" / "run_all_mcp_servers.py"
        if not mcp_script.exists():
            logger.warning("⚠️ MCP startup script not found, skipping")
            return True
            
        return True
    
    def start_services(self) -> Dict[str, bool]:
        """Start all services with health checking - uses correct paths from terminal testing"""
        logger.info("🚀 Starting Services")
        
        results = {}
        
        # Start backend with correct uvicorn path
        logger.info("🔄 Starting Backend...")
        # Use the correct path that works: backend.app.simple_fastapi:app
        backend_cmd = "python3 -m uvicorn backend.app.simple_fastapi:app --host 0.0.0.0 --port 8000 --reload"
        success, output = self.run_command(f"cd {self.root_dir} && {backend_cmd} > backend.log 2>&1 &")
        
        # Wait and check backend health
        logger.info("⏳ Waiting for backend to start...")
        time.sleep(10)
        backend_healthy = self.check_health_endpoint("http://localhost:8000/health")
        results['backend'] = backend_healthy
        logger.info(f"🔍 Backend Health: {'✅ Healthy' if backend_healthy else '❌ Unhealthy'}")
        
        if not backend_healthy:
            # Try alternative backend startup method
            logger.info("🔄 Trying alternative backend startup...")
            alt_backend_cmd = "python3 -c \"from backend.app.simple_fastapi import app; import uvicorn; uvicorn.run(app, host='0.0.0.0', port=8000)\""
            self.run_command(f"cd {self.root_dir} && {alt_backend_cmd} > backend_alt.log 2>&1 &")
            time.sleep(8)
            backend_healthy = self.check_health_endpoint("http://localhost:8000/health")
            results['backend'] = backend_healthy
        
        # Start frontend from correct directory
        logger.info("🔄 Starting Frontend...")
        # Ensure we're in the frontend directory
        frontend_cmd = "npm run dev"
        success, output = self.run_command(f"{frontend_cmd} > ../frontend.log 2>&1 &", cwd=self.frontend_dir)
        
        # Wait and check frontend health (try both common ports)
        logger.info("⏳ Waiting for frontend to start...")
        time.sleep(15)
        frontend_5173 = self.check_health_endpoint("http://localhost:5173")
        frontend_5174 = self.check_health_endpoint("http://localhost:5174")
        frontend_healthy = frontend_5173 or frontend_5174
        results['frontend'] = frontend_healthy
        
        active_port = "5173" if frontend_5173 else ("5174" if frontend_5174 else "none")
        logger.info(f"🔍 Frontend Health: {'✅ Healthy' if frontend_healthy else '❌ Unhealthy'} (port: {active_port})")
        
        # Start MCP servers (using working script from terminal output)
        logger.info("🔄 Starting MCP Servers...")
        mcp_script = self.root_dir / "scripts" / "run_all_mcp_servers.py"
        if mcp_script.exists():
            mcp_cmd = f"python3 {mcp_script}"
            success, output = self.run_command(f"{mcp_cmd} > mcp.log 2>&1 &")
            results['mcp'] = success
            logger.info(f"🔍 MCP Servers: {'✅ Started' if success else '❌ Failed'}")
        else:
            logger.warning("⚠️ MCP script not found, skipping")
            results['mcp'] = False
        
        return results
    
    def comprehensive_recovery(self) -> bool:
        """Run full recovery process with retries"""
        logger.info("🌟 Starting Comprehensive Deployment Recovery")
        
        for attempt in range(1, self.max_retries + 1):
            logger.info(f"🔄 Recovery Attempt {attempt}/{self.max_retries}")
            
            try:
                # Recovery phases
                self.frontend_recovery()
                self.backend_recovery()
                self.mcp_recovery()
                
                # Start services
                health_results = self.start_services()
                
                # Check overall health
                healthy_services = sum(health_results.values())
                total_services = len(health_results)
                health_percentage = (healthy_services / total_services) * 100
                
                logger.info(f"📊 Health Status: {healthy_services}/{total_services} services healthy ({health_percentage:.1f}%)")
                
                if health_percentage >= 66:  # At least 2/3 services healthy
                    logger.info("✅ Recovery successful - minimum health threshold met")
                    return True
                elif attempt < self.max_retries:
                    logger.warning(f"⚠️ Health below threshold, retrying in 30 seconds...")
                    time.sleep(30)
                
            except Exception as e:
                logger.error(f"💥 Recovery attempt {attempt} failed: {e}")
                if attempt < self.max_retries:
                    time.sleep(30)
        
        logger.error("❌ All recovery attempts failed")
        return False
    
    def create_deployment_status_report(self) -> Dict:
        """Generate comprehensive deployment status report"""
        report = {
            "timestamp": time.time(),
            "services": {},
            "logs": {},
            "recommendations": []
        }
        
        # Check service health
        services = {
            "backend": "http://localhost:8000/health",
            "frontend_5173": "http://localhost:5173",
            "frontend_5174": "http://localhost:5174"
        }
        
        for service, url in services.items():
            report["services"][service] = self.check_health_endpoint(url)
        
        # Collect recent logs
        log_files = ["backend.log", "frontend.log", "mcp.log"]
        for log_file in log_files:
            log_path = self.root_dir / log_file
            if log_path.exists():
                try:
                    with open(log_path, 'r') as f:
                        # Get last 20 lines
                        lines = f.readlines()
                        report["logs"][log_file] = lines[-20:] if len(lines) > 20 else lines
                except:
                    report["logs"][log_file] = ["Error reading log file"]
        
        # Generate recommendations
        if not report["services"].get("backend", False):
            report["recommendations"].append("Backend unhealthy - check Python dependencies and port 8000")
        
        if not any([report["services"].get("frontend_5173"), report["services"].get("frontend_5174")]):
            report["recommendations"].append("Frontend unhealthy - check npm dependencies and node_modules")
        
        return report

def main():
    """Main deployment recovery execution"""
    recovery = SophiaDeploymentRecovery()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--status-only":
        # Just generate status report
        report = recovery.create_deployment_status_report()
        print(json.dumps(report, indent=2))
        return
    
    # Run full recovery
    logger.info("🚀 Sophia AI Automated Deployment Recovery Starting")
    success = recovery.comprehensive_recovery()
    
    # Generate final report
    report = recovery.create_deployment_status_report()
    
    if success:
        logger.info("🎉 Deployment Recovery Completed Successfully")
        healthy_count = sum(report["services"].values())
        total_count = len(report["services"])
        logger.info(f"📊 Final Status: {healthy_count}/{total_count} services healthy")
    else:
        logger.error("💥 Deployment Recovery Failed")
        logger.error("📋 Recommendations:")
        for rec in report["recommendations"]:
            logger.error(f"  - {rec}")
    
    # Save report
    with open("deployment_recovery_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    return success

if __name__ == "__main__":
    main() 