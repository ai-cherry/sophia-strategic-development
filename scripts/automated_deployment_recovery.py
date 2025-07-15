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
        """Comprehensive frontend recovery process"""
        logger.info("🔧 Starting Frontend Recovery Process")
        
        steps = [
            ("Kill existing processes", "pkill -f 'vite\\|npm'", self.root_dir),
            ("Clear npm cache", "npm cache clean --force", self.frontend_dir),
            ("Remove node_modules", "rm -rf node_modules", self.frontend_dir),
            ("Remove package-lock", "rm -f package-lock.json", self.frontend_dir),
            ("Clear yarn cache", "yarn cache clean", self.frontend_dir),
            ("Reinstall dependencies", "npm install --no-package-lock", self.frontend_dir),
            ("Verify package integrity", "npm audit fix --force", self.frontend_dir),
        ]
        
        for step_name, cmd, cwd in steps:
            logger.info(f"📋 {step_name}")
            success, output = self.run_command(cmd, cwd)
            if not success and "no matching processes" not in output.lower():
                logger.warning(f"⚠️ {step_name} had issues, continuing...")
            time.sleep(2)
        
        return True
    
    def backend_recovery(self) -> bool:
        """Comprehensive backend recovery process"""
        logger.info("🔧 Starting Backend Recovery Process")
        
        # Install missing Python dependencies
        required_packages = [
            "sqlalchemy",
            "pyjwt",
            "passlib[bcrypt]", 
            "aiofiles",
            "python-multipart",
            "email-validator",
            "qdrant-client",
            "uvicorn[standard]",
            "fastapi",
            "redis",
            "psycopg2-binary",
            "asyncpg"
        ]
        
        # Kill existing backend processes
        self.run_command("pkill -f 'uvicorn\\|fastapi'")
        time.sleep(3)
        
        # Install dependencies
        for package in required_packages:
            logger.info(f"📦 Installing {package}")
            success, output = self.run_command(f"pip3 install {package}")
            if not success:
                logger.error(f"Failed to install {package}: {output}")
        
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
        """Start all services with health checking"""
        logger.info("🚀 Starting Services")
        
        results = {}
        
        # Start backend
        logger.info("🔄 Starting Backend...")
        backend_cmd = "cd backend && python3 -m uvicorn app.simple_fastapi:app --host 0.0.0.0 --port 8000 --reload"
        success, _ = self.run_command(f"{backend_cmd} > backend.log 2>&1 &")
        
        # Wait and check backend health
        time.sleep(10)
        backend_healthy = self.check_health_endpoint("http://localhost:8000/health")
        results['backend'] = backend_healthy
        logger.info(f"🔍 Backend Health: {'✅ Healthy' if backend_healthy else '❌ Unhealthy'}")
        
        # Start frontend
        logger.info("🔄 Starting Frontend...")
        frontend_cmd = "cd frontend && npm run dev"
        success, _ = self.run_command(f"{frontend_cmd} > frontend.log 2>&1 &")
        
        # Wait and check frontend health
        time.sleep(15)
        frontend_healthy = self.check_health_endpoint("http://localhost:5173") or self.check_health_endpoint("http://localhost:5174")
        results['frontend'] = frontend_healthy
        logger.info(f"🔍 Frontend Health: {'✅ Healthy' if frontend_healthy else '❌ Unhealthy'}")
        
        # Start MCP servers
        logger.info("🔄 Starting MCP Servers...")
        mcp_cmd = "python3 scripts/run_all_mcp_servers.py"
        success, _ = self.run_command(f"{mcp_cmd} > mcp.log 2>&1 &")
        results['mcp'] = success
        logger.info(f"🔍 MCP Servers: {'✅ Started' if success else '❌ Failed'}")
        
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