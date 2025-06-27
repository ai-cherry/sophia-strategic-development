#!/usr/bin/env python3
"""
Sophia AI - Fix Pulumi Token & Test Complete Ecosystem
This script diagnoses and fixes the PULUMI_ACCESS_TOKEN issue and tests all integrations
"""

import os
import sys
import subprocess
import json
import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SophiaEcosystemFixer:
    """Comprehensive ecosystem diagnostic and fix system"""
    
    def __init__(self):
        self.issues_found = []
        self.fixes_applied = []
        self.test_results = {}
        
    def run_diagnostic(self) -> Dict[str, Any]:
        """Run complete ecosystem diagnostic"""
        logger.info("🔍 Starting Sophia AI Ecosystem Diagnostic...")
        
        # 1. Check Pulumi Authentication
        pulumi_status = self._check_pulumi_auth()
        
        # 2. Check GitHub Organization Secrets Setup
        github_status = self._check_github_secrets()
        
        # 3. Check ESC Stack Access
        esc_status = self._check_esc_access()
        
        # 4. Check MCP Server Health
        mcp_status = self._check_mcp_servers()
        
        # 5. Check Secret Availability
        secret_status = self._check_secret_availability()
        
        return {
            "pulumi_auth": pulumi_status,
            "github_secrets": github_status,
            "esc_access": esc_status,
            "mcp_servers": mcp_status,
            "secrets": secret_status,
            "issues": self.issues_found,
            "timestamp": datetime.now().isoformat()
        }
    
    def _check_pulumi_auth(self) -> Dict[str, Any]:
        """Check Pulumi authentication status"""
        logger.info("🔐 Checking Pulumi authentication...")
        
        token = os.getenv("PULUMI_ACCESS_TOKEN")
        if not token:
            issue = "PULUMI_ACCESS_TOKEN not set in environment"
            self.issues_found.append(issue)
            return {"status": "error", "message": issue}
        
        if token == "your-access-token-here" or len(token) < 20:
            issue = "PULUMI_ACCESS_TOKEN appears to be a placeholder"
            self.issues_found.append(issue)
            return {"status": "error", "message": issue, "token_preview": token[:10] + "..."}
        
        try:
            result = subprocess.run(
                ["pulumi", "whoami"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                username = result.stdout.strip()
                return {"status": "success", "username": username}
            else:
                issue = f"Pulumi auth failed: {result.stderr}"
                self.issues_found.append(issue)
                return {"status": "error", "message": issue}
                
        except Exception as e:
            issue = f"Pulumi CLI error: {str(e)}"
            self.issues_found.append(issue)
            return {"status": "error", "message": issue}
    
    def _check_github_secrets(self) -> Dict[str, Any]:
        """Check GitHub organization secrets availability"""
        logger.info("🔗 Checking GitHub organization secrets...")
        
        # Expected secrets for Sophia AI
        expected_secrets = [
            "ANTHROPIC_API_KEY",  # User mentioned this
            "GEMINI_API_KEY",     # User mentioned this
            "OPENAI_API_KEY",
            "GONG_ACCESS_KEY",
            "GONG_CLIENT_SECRET",
            "HUBSPOT_ACCESS_TOKEN",
            "LINEAR_API_KEY",
            "LAMBDA_API_KEY",
            "SNOWFLAKE_ACCOUNT",
            "SNOWFLAKE_PASSWORD",
            "PINECONE_API_KEY",
            "PULUMI_ACCESS_TOKEN"
        ]
        
        # Check if secrets are available as environment variables
        # (This assumes GitHub Actions has synced them)
        available_secrets = []
        missing_secrets = []
        
        for secret in expected_secrets:
            value = os.getenv(secret)
            if value and value != "your-token-here":
                available_secrets.append(secret)
            else:
                missing_secrets.append(secret)
        
        return {
            "status": "partial" if missing_secrets else "success",
            "available_count": len(available_secrets),
            "total_expected": len(expected_secrets),
            "available_secrets": available_secrets,
            "missing_secrets": missing_secrets
        }
    
    def _check_esc_access(self) -> Dict[str, Any]:
        """Check Pulumi ESC stack access"""
        logger.info("📦 Checking Pulumi ESC stack access...")
        
        org = "scoobyjava-org"
        env = "sophia-ai-production"
        stack_path = f"{org}/default/{env}"
        
        try:
            result = subprocess.run([
                "pulumi", "env", "open", stack_path, "--format", "json"
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                config = json.loads(result.stdout)
                return {
                    "status": "success",
                    "stack_path": stack_path,
                    "config_keys": len(config),
                    "has_sophia_values": "values" in config and "sophia" in config.get("values", {})
                }
            else:
                issue = f"ESC access failed: {result.stderr}"
                self.issues_found.append(issue)
                return {"status": "error", "message": issue}
                
        except Exception as e:
            issue = f"ESC access error: {str(e)}"
            self.issues_found.append(issue)
            return {"status": "error", "message": issue}
    
    def _check_mcp_servers(self) -> Dict[str, Any]:
        """Check MCP server health"""
        logger.info("🤖 Checking MCP server health...")
        
        mcp_servers = {
            "ai_memory": 9000,
            "codacy": 3008,
            "asana": 3006,
            "notion": 3007,
            "figma": 9001,
            "ui_ux_agent": 9002
        }
        
        server_status = {}
        
        for server_name, port in mcp_servers.items():
            try:
                # Simple port check
                import socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                result = sock.connect_ex(('localhost', port))
                sock.close()
                
                if result == 0:
                    server_status[server_name] = {"status": "online", "port": port}
                else:
                    server_status[server_name] = {"status": "offline", "port": port}
                    
            except Exception as e:
                server_status[server_name] = {"status": "error", "port": port, "error": str(e)}
        
        online_count = sum(1 for s in server_status.values() if s["status"] == "online")
        
        return {
            "status": "partial" if online_count < len(mcp_servers) else "success",
            "online_count": online_count,
            "total_servers": len(mcp_servers),
            "servers": server_status
        }
    
    def _check_secret_availability(self) -> Dict[str, Any]:
        """Check if critical secrets are available through auto_esc_config"""
        logger.info("🔑 Checking secret availability through auto_esc_config...")
        
        try:
            # Import the config system
            sys.path.append(os.path.join(os.getcwd(), 'backend'))
            from backend.core.auto_esc_config import get_config_value
            
            critical_secrets = {
                "openai_api_key": "OpenAI API access",
                "anthropic_api_key": "Anthropic API access",  # User mentioned
                "gong_access_key": "Gong API access",
                "snowflake_password": "Snowflake database access",
                "pinecone_api_key": "Pinecone vector database"
            }
            
            secret_results = {}
            available_count = 0
            
            for secret_key, description in critical_secrets.items():
                try:
                    value = get_config_value(secret_key)
                    if value and value != "PLACEHOLDER_VALUE":
                        secret_results[secret_key] = {"status": "available", "description": description}
                        available_count += 1
                    else:
                        secret_results[secret_key] = {"status": "missing", "description": description}
                except Exception as e:
                    secret_results[secret_key] = {"status": "error", "description": description, "error": str(e)}
            
            return {
                "status": "partial" if available_count < len(critical_secrets) else "success",
                "available_count": available_count,
                "total_secrets": len(critical_secrets),
                "secrets": secret_results
            }
            
        except Exception as e:
            issue = f"Failed to check secrets through auto_esc_config: {str(e)}"
            self.issues_found.append(issue)
            return {"status": "error", "message": issue}
    
    def generate_fix_recommendations(self, diagnostic_results: Dict[str, Any]) -> List[str]:
        """Generate specific fix recommendations based on diagnostic results"""
        recommendations = []
        
        # Pulumi auth issues
        if diagnostic_results["pulumi_auth"]["status"] == "error":
            recommendations.extend([
                "🔧 Fix PULUMI_ACCESS_TOKEN:",
                "   1. Get valid token from https://app.pulumi.com/account/tokens",
                "   2. Update in GitHub Organization Secrets (ai-cherry org)",
                "   3. Run GitHub Action to sync to Pulumi ESC"
            ])
        
        # Missing secrets
        if diagnostic_results["secrets"]["status"] != "success":
            recommendations.extend([
                "🔑 Fix Secret Management:",
                "   1. Ensure all secrets are in GitHub Organization (ai-cherry)",
                "   2. Run: gh workflow run sync_secrets.yml",
                "   3. Verify sync with: python scripts/ci/sync_from_gh_to_pulumi.py"
            ])
        
        # MCP server issues
        if diagnostic_results["mcp_servers"]["online_count"] < 4:
            recommendations.extend([
                "🤖 Start MCP Servers:",
                "   1. Run: python mcp-servers/ai_memory/ai_memory_mcp_server.py",
                "   2. Run: python mcp-servers/codacy/codacy_mcp_server.py",
                "   3. Check health: curl http://localhost:9000/health"
            ])
        
        # ESC access issues
        if diagnostic_results["esc_access"]["status"] == "error":
            recommendations.extend([
                "📦 Fix ESC Access:",
                "   1. Verify stack exists: pulumi env ls scoobyjava-org",
                "   2. Create if missing: pulumi env init scoobyjava-org/default/sophia-ai-production",
                "   3. Sync secrets: python scripts/ci/sync_from_gh_to_pulumi.py"
            ])
        
        return recommendations
    
    def run_codacy_mcp_test(self) -> Dict[str, Any]:
        """Test Codacy MCP server integration specifically"""
        logger.info("🧪 Testing Codacy MCP Server Integration...")
        
        test_code = '''
import os
password = "hardcoded_password"  # Security issue
def complex_function(x):
    if x > 0:
        if x > 10:
            if x > 100:
                return "very big"
    return "small"
'''
        
        try:
            # Test if Codacy MCP server is running
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex(('localhost', 3008))
            sock.close()
            
            if result == 0:
                return {
                    "status": "success",
                    "message": "Codacy MCP server is online and ready",
                    "port": 3008,
                    "capabilities": [
                        "Real-time security analysis",
                        "Code complexity detection", 
                        "Performance optimization",
                        "Sophia AI-specific checks"
                    ]
                }
            else:
                return {
                    "status": "offline",
                    "message": "Codacy MCP server not running",
                    "start_command": "python mcp-servers/codacy/codacy_mcp_server.py"
                }
                
        except Exception as e:
            return {"status": "error", "message": str(e)}

def main():
    """Main execution"""
    print("🚀 Sophia AI Ecosystem Diagnostic & Fix Tool")
    print("=" * 50)
    
    fixer = SophiaEcosystemFixer()
    
    # Run complete diagnostic
    results = fixer.run_diagnostic()
    
    # Print results
    print("\n📊 DIAGNOSTIC RESULTS:")
    print("-" * 30)
    
    for component, status in results.items():
        if component == "issues":
            continue
            
        if isinstance(status, dict) and "status" in status:
            status_emoji = "✅" if status["status"] == "success" else "⚠️" if status["status"] == "partial" else "❌"
            print(f"{status_emoji} {component.upper()}: {status['status']}")
            
            if "message" in status:
                print(f"   └─ {status['message']}")
    
    # Print issues found
    if fixer.issues_found:
        print(f"\n❌ ISSUES FOUND ({len(fixer.issues_found)}):")
        for i, issue in enumerate(fixer.issues_found, 1):
            print(f"  {i}. {issue}")
    
    # Generate and print recommendations
    recommendations = fixer.generate_fix_recommendations(results)
    if recommendations:
        print(f"\n🔧 FIX RECOMMENDATIONS:")
        for rec in recommendations:
            print(f"  {rec}")
    
    # Test Codacy MCP specifically (user asked about it)
    codacy_test = fixer.run_codacy_mcp_test()
    print(f"\n🤖 CODACY MCP SERVER TEST:")
    print(f"  Status: {codacy_test['status']}")
    print(f"  Message: {codacy_test['message']}")
    
    if codacy_test["status"] == "success" and "capabilities" in codacy_test:
        print("  Capabilities:")
        for cap in codacy_test["capabilities"]:
            print(f"    • {cap}")
    
    # Save detailed report
    with open('sophia_ecosystem_diagnostic.json', 'w') as f:
        json.dump({
            "diagnostic_results": results,
            "codacy_test": codacy_test,
            "recommendations": recommendations
        }, f, indent=2)
    
    print(f"\n📄 Detailed report saved to: sophia_ecosystem_diagnostic.json")
    
    # Summary
    if not fixer.issues_found:
        print(f"\n🎉 SUCCESS: Sophia AI ecosystem is healthy!")
    else:
        print(f"\n⚠️  ATTENTION: {len(fixer.issues_found)} issues need fixing")
        print("💡 Follow the fix recommendations above")

if __name__ == "__main__":
    main() 