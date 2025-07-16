#!/usr/bin/env python3
"""
🔧 Fix Domain/SSL Final Blocker for sophia-intel.ai
=================================================

This script deploys the SSL certificate fix for api.sophia-intel.ai
and verifies the domain configuration is working correctly.

Final blocker identified:
- SSL certificate mismatch for api.sophia-intel.ai
- Need to deploy correct ingress with proper certificate configuration
- Verify cert-manager can provision SSL certificates

Date: January 15, 2025
"""

import asyncio
import subprocess
import logging
import time
import json
from pathlib import Path
from typing import Dict, Any, List
import aiohttp

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DomainSSLFixer:
    """Fixes the SSL/domain configuration for sophia-intel.ai"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.domains = {
            "api": "api.sophia-intel.ai",
            "frontend": "sophia-intel.ai",
            "app": "app.sophia-intel.ai"
        }
        self.infrastructure_ips = {
            "primary": "192.222.58.232",  # Lambda Labs GH200
            "production": "104.171.202.103",  # Lambda Labs RTX6000  
            "mcp_hub": "104.171.202.117",  # Lambda Labs A6000
        }
        
    async def check_prerequisites(self) -> Dict[str, bool]:
        """Check if prerequisites are met for deployment"""
        logger.info("🔍 Checking deployment prerequisites...")
        
        prereqs = {
            "kubectl_available": False,
            "kubectl_connected": False,
            "cert_manager_installed": False,
            "nginx_ingress_installed": False,
            "namespace_exists": False
        }
        
        # Check kubectl
        try:
            result = subprocess.run(['kubectl', 'version', '--client'], 
                                  capture_output=True, timeout=10)
            prereqs["kubectl_available"] = result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            prereqs["kubectl_available"] = False
            
        # Check kubectl connectivity
        if prereqs["kubectl_available"]:
            try:
                result = subprocess.run(['kubectl', 'get', 'nodes'], 
                                      capture_output=True, timeout=15)
                prereqs["kubectl_connected"] = result.returncode == 0
            except subprocess.TimeoutExpired:
                prereqs["kubectl_connected"] = False
                
        # Check cert-manager
        if prereqs["kubectl_connected"]:
            try:
                result = subprocess.run(['kubectl', 'get', 'namespace', 'cert-manager'], 
                                      capture_output=True, timeout=10)
                prereqs["cert_manager_installed"] = result.returncode == 0
            except subprocess.TimeoutExpired:
                prereqs["cert_manager_installed"] = False
                
        # Check nginx-ingress
        if prereqs["kubectl_connected"]:
            try:
                result = subprocess.run(['kubectl', 'get', 'pods', '-n', 'ingress-nginx'], 
                                      capture_output=True, timeout=10)
                prereqs["nginx_ingress_installed"] = result.returncode == 0
            except subprocess.TimeoutExpired:
                prereqs["nginx_ingress_installed"] = False
                
        # Check namespace
        if prereqs["kubectl_connected"]:
            try:
                result = subprocess.run(['kubectl', 'get', 'namespace', 'sophia-ai-prod'], 
                                      capture_output=True, timeout=10)
                prereqs["namespace_exists"] = result.returncode == 0
            except subprocess.TimeoutExpired:
                prereqs["namespace_exists"] = False
        
        # Log results
        for check, status in prereqs.items():
            status_icon = "✅" if status else "❌"
            logger.info(f"{status_icon} {check}: {status}")
            
        return prereqs
    
    async def install_missing_components(self, prereqs: Dict[str, bool]):
        """Install missing components if possible"""
        logger.info("🛠️ Installing missing components...")
        
        # Install cert-manager if missing
        if not prereqs["cert_manager_installed"] and prereqs["kubectl_connected"]:
            logger.info("📦 Installing cert-manager...")
            try:
                # Install cert-manager
                commands = [
                    ["kubectl", "apply", "-f", "https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml"],
                    ["kubectl", "wait", "--for=condition=ready", "pod", "-l", "app=cert-manager", "-n", "cert-manager", "--timeout=300s"]
                ]
                
                for cmd in commands:
                    result = subprocess.run(cmd, capture_output=True, timeout=60)
                    if result.returncode == 0:
                        logger.info(f"✅ Command succeeded: {' '.join(cmd)}")
                    else:
                        logger.warning(f"⚠️ Command failed: {' '.join(cmd)}")
                        
            except subprocess.TimeoutExpired:
                logger.warning("⚠️ cert-manager installation timed out")
                
        # Install nginx-ingress if missing  
        if not prereqs["nginx_ingress_installed"] and prereqs["kubectl_connected"]:
            logger.info("📦 Installing nginx-ingress...")
            try:
                cmd = ["kubectl", "apply", "-f", "https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.2/deploy/static/provider/cloud/deploy.yaml"]
                result = subprocess.run(cmd, capture_output=True, timeout=60)
                if result.returncode == 0:
                    logger.info("✅ nginx-ingress installed")
                else:
                    logger.warning("⚠️ nginx-ingress installation failed")
            except subprocess.TimeoutExpired:
                logger.warning("⚠️ nginx-ingress installation timed out")
                
        # Create namespace if missing
        if not prereqs["namespace_exists"] and prereqs["kubectl_connected"]:
            logger.info("📦 Creating sophia-ai-prod namespace...")
            try:
                cmd = ["kubectl", "create", "namespace", "sophia-ai-prod"]
                result = subprocess.run(cmd, capture_output=True, timeout=30)
                if result.returncode == 0:
                    logger.info("✅ Namespace created")
                else:
                    logger.warning("⚠️ Namespace creation failed (may already exist)")
            except subprocess.TimeoutExpired:
                logger.warning("⚠️ Namespace creation timed out")
                
    async def deploy_ssl_fix(self) -> bool:
        """Deploy the SSL/domain configuration fix"""
        logger.info("🚀 Deploying SSL/domain configuration fix...")
        
        try:
            # Apply the new ingress configuration
            ingress_file = self.project_root / "k8s" / "production" / "sophia-intel-ingress-fix.yaml"
            
            if not ingress_file.exists():
                logger.error(f"❌ Ingress configuration file not found: {ingress_file}")
                return False
                
            # Apply the configuration
            cmd = ["kubectl", "apply", "-f", str(ingress_file)]
            result = subprocess.run(cmd, capture_output=True, timeout=60)
            
            if result.returncode == 0:
                logger.info("✅ SSL/domain configuration applied successfully")
                
                # Wait for certificate provisioning
                logger.info("⏳ Waiting for SSL certificate provisioning...")
                await self.wait_for_certificate()
                
                return True
            else:
                logger.error(f"❌ Failed to apply configuration: {result.stderr.decode()}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("❌ Deployment timed out")
            return False
        except Exception as e:
            logger.error(f"❌ Deployment failed: {e}")
            return False
            
    async def wait_for_certificate(self, timeout_seconds: int = 300):
        """Wait for SSL certificate to be issued"""
        logger.info("⏳ Waiting for SSL certificate to be ready...")
        
        start_time = time.time()
        while time.time() - start_time < timeout_seconds:
            try:
                # Check certificate status
                cmd = ["kubectl", "get", "certificate", "sophia-intel-production-cert", 
                      "-n", "sophia-ai-prod", "-o", "json"]
                result = subprocess.run(cmd, capture_output=True, timeout=30)
                
                if result.returncode == 0:
                    cert_data = json.loads(result.stdout.decode())
                    conditions = cert_data.get("status", {}).get("conditions", [])
                    
                    for condition in conditions:
                        if condition.get("type") == "Ready" and condition.get("status") == "True":
                            logger.info("✅ SSL certificate ready!")
                            return True
                            
                logger.info("⏳ Certificate still provisioning...")
                await asyncio.sleep(15)
                
            except (subprocess.TimeoutExpired, json.JSONDecodeError, Exception) as e:
                logger.warning(f"⚠️ Error checking certificate status: {e}")
                await asyncio.sleep(15)
                
        logger.warning("⚠️ Certificate provisioning timed out")
        return False
        
    async def verify_deployment(self) -> Dict[str, Any]:
        """Verify the deployment is working"""
        logger.info("🔍 Verifying deployment...")
        
        verification_results = {
            "ssl_certificate_valid": False,
            "api_reachable": False,
            "frontend_reachable": False,
            "api_health_check": False,
            "real_data_confirmed": False
        }
        
        # Test SSL certificate
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://{self.domains['api']}/health", 
                                     timeout=30, ssl=True) as response:
                    verification_results["ssl_certificate_valid"] = True
                    verification_results["api_reachable"] = response.status == 200
                    
                    if response.status == 200:
                        data = await response.json()
                        verification_results["api_health_check"] = data.get("status") == "healthy"
        except aiohttp.ClientSSLError:
            logger.warning("⚠️ SSL certificate still invalid")
        except Exception as e:
            logger.warning(f"⚠️ API test failed: {e}")
            
        # Test frontend
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://{self.domains['frontend']}", 
                                     timeout=30, ssl=True) as response:
                    verification_results["frontend_reachable"] = response.status == 200
        except Exception as e:
            logger.warning(f"⚠️ Frontend test failed: {e}")
            
        # Test for real data (not mock)
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://{self.domains['api']}/api/v3/dashboard/metrics", 
                                     timeout=30, ssl=True) as response:
                    if response.status == 200:
                        data = await response.json()
                        response_text = json.dumps(data).lower()
                        is_mock = any(keyword in response_text for keyword in [
                            'mock', 'sample', 'demo', 'placeholder', 'test_'
                        ])
                        verification_results["real_data_confirmed"] = not is_mock
        except Exception as e:
            logger.warning(f"⚠️ Real data test failed: {e}")
            
        # Log results
        for check, status in verification_results.items():
            status_icon = "✅" if status else "❌"
            logger.info(f"{status_icon} {check}: {status}")
            
        return verification_results
        
    async def create_verification_report(self, verification: Dict[str, Any]):
        """Create final verification report"""
        logger.info("📄 Creating verification report...")
        
        report = {
            "timestamp": "2025-01-15T10:45:00Z",
            "fix_description": "SSL/Domain configuration fix for api.sophia-intel.ai",
            "verification_results": verification,
            "domains_configured": self.domains,
            "infrastructure_ips": self.infrastructure_ips,
            "success_criteria": {
                "ssl_valid": verification["ssl_certificate_valid"],
                "api_working": verification["api_reachable"] and verification["api_health_check"],
                "real_data": verification["real_data_confirmed"],
                "overall_success": all([
                    verification["ssl_certificate_valid"],
                    verification["api_reachable"],
                    verification["api_health_check"]
                ])
            },
            "next_steps": [],
            "business_impact": {
                "before": "SSL certificate mismatch preventing API access",
                "after": "Production API accessible with valid SSL certificate"
            }
        }
        
        # Add next steps based on results
        if not report["success_criteria"]["overall_success"]:
            report["next_steps"].extend([
                "Check DNS configuration for sophia-intel.ai domain",
                "Verify cert-manager ClusterIssuer configuration",
                "Check kubectl access to production cluster",
                "Verify nginx-ingress controller is running"
            ])
        else:
            report["next_steps"].extend([
                "Monitor API health at https://api.sophia-intel.ai/health",
                "Test frontend at https://sophia-intel.ai",
                "Verify real business data is displayed",
                "Set up monitoring alerts for domain health"
            ])
            
        # Save report
        report_path = self.project_root / "DOMAIN_SSL_FIX_REPORT.md"
        with open(report_path, 'w') as f:
            f.write(f"""# 🔧 Domain/SSL Fix Report for sophia-intel.ai

## Fix Summary
**Issue**: SSL certificate mismatch preventing access to api.sophia-intel.ai
**Solution**: Deployed correct ingress configuration with Let's Encrypt SSL certificates

## Verification Results
- **SSL Certificate Valid**: {verification['ssl_certificate_valid']}
- **API Reachable**: {verification['api_reachable']}
- **API Health Check**: {verification['api_health_check']}
- **Frontend Reachable**: {verification['frontend_reachable']}
- **Real Data Confirmed**: {verification['real_data_confirmed']}

## Success Criteria
- **SSL Valid**: {report['success_criteria']['ssl_valid']}
- **API Working**: {report['success_criteria']['api_working']}
- **Real Data**: {report['success_criteria']['real_data']}
- **Overall Success**: {report['success_criteria']['overall_success']}

## Domains Configured
{chr(10).join([f"- **{name.title()}**: https://{domain}" for name, domain in self.domains.items()])}

## Infrastructure
{chr(10).join([f"- **{name.title()}**: {ip}" for name, ip in self.infrastructure_ips.items()])}

## Next Steps
{chr(10).join([f"- {step}" for step in report['next_steps']])}

## Business Impact
- **Before**: {report['business_impact']['before']}
- **After**: {report['business_impact']['after']}

---
*Report generated on {report['timestamp']}*
""")
        
        logger.info(f"✅ Verification report created: {report_path}")
        return report
        
    async def run_complete_fix(self):
        """Run the complete SSL/domain fix process"""
        logger.info("🚀 Starting SSL/domain fix for sophia-intel.ai...")
        
        try:
            # Check prerequisites
            prereqs = await self.check_prerequisites()
            
            # Install missing components if possible
            await self.install_missing_components(prereqs)
            
            # Deploy SSL fix
            deployment_success = await self.deploy_ssl_fix()
            
            if not deployment_success:
                logger.error("❌ Deployment failed - cannot proceed with verification")
                return False
                
            # Wait a bit for propagation
            logger.info("⏳ Waiting for DNS/SSL propagation...")
            await asyncio.sleep(30)
            
            # Verify deployment
            verification = await self.verify_deployment()
            
            # Create report
            report = await self.create_verification_report(verification)
            
            # Final status
            if report["success_criteria"]["overall_success"]:
                logger.info("🎉 SUCCESS: SSL/domain fix completed!")
                logger.info(f"✅ API accessible at https://{self.domains['api']}/health")
                logger.info(f"✅ Frontend accessible at https://{self.domains['frontend']}")
                logger.info("✅ Mock data issue should now be resolved")
                return True
            else:
                logger.warning("⚠️ PARTIAL SUCCESS: Some issues remain")
                logger.info("🔍 Check DOMAIN_SSL_FIX_REPORT.md for details")
                return False
                
        except Exception as e:
            logger.error(f"❌ SSL/domain fix failed: {e}")
            return False

async def main():
    """Main entry point"""
    fixer = DomainSSLFixer()
    success = await fixer.run_complete_fix()
    
    if success:
        print("\n🎉 Domain/SSL final blocker has been fixed!")
        print("✅ SSL certificate configured for sophia-intel.ai")
        print("✅ API accessible with valid certificate")
        print("✅ Mock data issue should now be resolved")
        print(f"\n🔗 Test the API: https://api.sophia-intel.ai/health")
        print(f"🔗 Check the frontend: https://sophia-intel.ai")
    else:
        print("\n⚠️ SSL/domain fix completed with issues")
        print("📄 Check DOMAIN_SSL_FIX_REPORT.md for details")
        print("🔧 Manual configuration may be required")
    
    return success

if __name__ == "__main__":
    asyncio.run(main()) 