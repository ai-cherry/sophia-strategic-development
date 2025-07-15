#!/usr/bin/env python3
"""
Comprehensive Pulumi ESC Configuration Test & Consolidation
Tests all ESC configurations and consolidates the best practices
"""

import json
import subprocess
import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.core.auto_esc_config import get_config_value, get_pulumi_config

class PulumiESCTester:
    def __init__(self):
        self.environment = "scoobyjava-org/default/sophia-ai-production"
        self.test_results = {}
        
    def test_pulumi_auth(self) -> bool:
        """Test Pulumi authentication"""
        try:
            result = subprocess.run(
                ["pulumi", "whoami"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                user = result.stdout.strip()
                print(f"✅ Pulumi authenticated as: {user}")
                return True
            else:
                print(f"❌ Pulumi authentication failed: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ Pulumi authentication error: {e}")
            return False
    
    def test_esc_environment_access(self) -> bool:
        """Test ESC environment access"""
        try:
            result = subprocess.run(
                ["pulumi", "env", "get", self.environment],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                print(f"✅ ESC environment accessible: {self.environment}")
                return True
            else:
                print(f"❌ ESC environment access failed: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ ESC environment access error: {e}")
            return False
    
    def test_secret_retrieval(self) -> Dict[str, Any]:
        """Test secret retrieval for key services"""
        secrets_to_test = {
            # MCP Project Critical Secrets
            "linear_api_key": "Linear API key for project management",
            "openai_api_key": "OpenAI API key for AI services",
            "anthropic_api_key": "Anthropic API key for Claude",
            "gong_access_key": "Gong API key for call intelligence",
            "hubspot_access_token": "HubSpot API key for CRM",
            "notion_api_key": "Notion API key for knowledge management",
            "slack_bot_token": "Slack bot token for notifications",
            
            # Infrastructure Secrets
            "lambda_api_key": "Lambda Labs API key",
            "docker_hub_access_token": "Docker Hub access token",
            "pulumi_access_token": "Pulumi access token",
            
            # Database Secrets
            "qdrant_api_key": "Qdrant API key",
            "qdrant_url": "Qdrant URL",
            "redis_password": "Redis password",
        }
        
        results = {}
        print("\n🔍 Testing Secret Retrieval:")
        print("-" * 50)
        
        for secret_key, description in secrets_to_test.items():
            try:
                # Test via auto_esc_config
                value = get_config_value(secret_key)
                if value and value != "[secret]" and not value.startswith("PLACEHOLDER"):
                    status = "✅ FOUND"
                    length = len(value)
                    masked = value[:4] + "***" + value[-4:] if length > 8 else "***"
                elif value == "[secret]":
                    status = "🔒 SECRET (encrypted)"
                    length = "unknown"
                    masked = "[secret]"
                else:
                    status = "❌ MISSING"
                    length = 0
                    masked = "N/A"
                
                results[secret_key] = {
                    "status": status,
                    "description": description,
                    "length": length,
                    "masked_value": masked,
                    "found": value is not None
                }
                
                print(f"{status} {secret_key}: {description}")
                if value and value != "[secret]":
                    print(f"    Value: {masked} (length: {length})")
                
            except Exception as e:
                results[secret_key] = {
                    "status": "❌ ERROR",
                    "description": description,
                    "error": str(e),
                    "found": False
                }
                print(f"❌ ERROR {secret_key}: {e}")
        
        return results
    
    def test_direct_pulumi_access(self) -> Dict[str, Any]:
        """Test direct Pulumi ESC access"""
        print("\n🔍 Testing Direct Pulumi ESC Access:")
        print("-" * 50)
        
        try:
            # Get specific secret values
            test_secrets = ["linear_api_key", "openai_api_key", "gong_access_key"]
            results = {}
            
            for secret in test_secrets:
                try:
                    result = subprocess.run(
                        ["pulumi", "env", "get", self.environment, f"values.{secret}"],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    
                    if result.returncode == 0:
                        value = result.stdout.strip()
                        if value and value != "[secret]":
                            results[secret] = {
                                "status": "✅ ACCESSIBLE",
                                "value_length": len(value),
                                "masked": value[:4] + "***" + value[-4:] if len(value) > 8 else "***"
                            }
                            print(f"✅ {secret}: Accessible (length: {len(value)})")
                        else:
                            results[secret] = {
                                "status": "🔒 ENCRYPTED",
                                "value": "[secret]"
                            }
                            print(f"🔒 {secret}: Encrypted secret")
                    else:
                        results[secret] = {
                            "status": "❌ NOT FOUND",
                            "error": result.stderr
                        }
                        print(f"❌ {secret}: Not found - {result.stderr}")
                        
                except Exception as e:
                    results[secret] = {
                        "status": "❌ ERROR",
                        "error": str(e)
                    }
                    print(f"❌ {secret}: Error - {e}")
            
            return results
            
        except Exception as e:
            print(f"❌ Direct Pulumi access error: {e}")
            return {}
    
    def analyze_config_files(self) -> Dict[str, Any]:
        """Analyze all Pulumi ESC configuration files"""
        print("\n📄 Analyzing Pulumi ESC Configuration Files:")
        print("-" * 50)
        
        config_files = [
            "infrastructure/esc/sophia-ai-production.yaml",
            "pulumi-esc-configuration.yaml",
            "pulumi-esc-github-imports.yaml",
            "infrastructure/pulumi-esc-config.yaml",
            "infrastructure/esc/consolidated.yaml"
        ]
        
        analysis = {}
        
        for config_file in config_files:
            if os.path.exists(config_file):
                try:
                    with open(config_file, 'r') as f:
                        content = f.read()
                    
                    # Count secrets and structure
                    secret_count = content.count('fn::secret:')
                    env_var_count = content.count('${')
                    lines = len(content.split('\n'))
                    
                    analysis[config_file] = {
                        "exists": True,
                        "size_kb": len(content) / 1024,
                        "lines": lines,
                        "secret_count": secret_count,
                        "env_var_count": env_var_count,
                        "has_imports": "imports:" in content,
                        "has_env_vars": "environmentVariables:" in content,
                        "has_linear": "linear" in content.lower()
                    }
                    
                    print(f"✅ {config_file}:")
                    print(f"    Size: {analysis[config_file]['size_kb']:.1f}KB, Lines: {lines}")
                    print(f"    Secrets: {secret_count}, Variables: {env_var_count}")
                    print(f"    Has Linear: {analysis[config_file]['has_linear']}")
                    
                except Exception as e:
                    analysis[config_file] = {
                        "exists": True,
                        "error": str(e)
                    }
                    print(f"❌ {config_file}: Error reading - {e}")
            else:
                analysis[config_file] = {"exists": False}
                print(f"❌ {config_file}: Not found")
        
        return analysis
    
    def generate_consolidated_config(self) -> str:
        """Generate consolidated ESC configuration"""
        print("\n🔧 Generating Consolidated ESC Configuration:")
        print("-" * 50)
        
        consolidated_config = """# Sophia AI - Consolidated Pulumi ESC Configuration
# Generated by comprehensive test and consolidation script
# This is the single source of truth for all secrets and configuration

values:
  # AI Services (Critical for MCP Project)
  ai_services:
    openai:
      api_key:
        fn::secret: ${OPENAI_API_KEY}
    anthropic:
      api_key:
        fn::secret: ${ANTHROPIC_API_KEY}
    portkey:
      api_key:
        fn::secret: ${PORTKEY_API_KEY}
    openrouter:
      api_key:
        fn::secret: ${OPENROUTER_API_KEY}

  # Business Intelligence (MCP Project Core)
  business_intelligence:
    gong:
      access_key:
        fn::secret: ${GONG_ACCESS_KEY}
      access_key_secret:
        fn::secret: ${GONG_ACCESS_KEY_SECRET}
    hubspot:
      access_token:
        fn::secret: ${HUBSPOT_ACCESS_TOKEN}
    linear:
      api_key:
        fn::secret: ${LINEAR_API_KEY}
    notion:
      api_key:
        fn::secret: ${NOTION_API_KEY}
    asana:
      api_token:
        fn::secret: ${ASANA_API_TOKEN}
    slack:
      bot_token:
        fn::secret: ${SLACK_BOT_TOKEN}
      webhook_url:
        fn::secret: ${SLACK_WEBHOOK_URL}

  # Data Infrastructure
  data_infrastructure:
    qdrant:
      api_key:
        fn::secret: ${QDRANT_API_KEY}
      url:
        fn::secret: ${QDRANT_URL}
      cluster_name: "sophia-ai-production"
    redis:
      password:
        fn::secret: ${REDIS_PASSWORD}
      url:
        fn::secret: ${REDIS_URL}
    postgres:
      host:
        fn::secret: ${POSTGRES_HOST}
      password:
        fn::secret: ${POSTGRES_PASSWORD}
      database:
        fn::secret: ${POSTGRES_DATABASE}

  # Infrastructure
  infrastructure:
    lambda_labs:
      api_key:
        fn::secret: ${LAMBDA_API_KEY}
      ssh_private_key:
        fn::secret: ${LAMBDA_SSH_PRIVATE_KEY}
      region: "us-west-1"
    docker:
      hub_access_token:
        fn::secret: ${DOCKER_HUB_ACCESS_TOKEN}
      username:
        fn::secret: ${DOCKER_HUB_USERNAME}
    pulumi:
      access_token:
        fn::secret: ${PULUMI_ACCESS_TOKEN}

# Environment Variables for Runtime
environmentVariables:
  # AI Services
  OPENAI_API_KEY: ${ai_services.openai.api_key}
  ANTHROPIC_API_KEY: ${ai_services.anthropic.api_key}
  PORTKEY_API_KEY: ${ai_services.portkey.api_key}
  OPENROUTER_API_KEY: ${ai_services.openrouter.api_key}
  
  # Business Intelligence (MCP Project)
  GONG_ACCESS_KEY: ${business_intelligence.gong.access_key}
  GONG_ACCESS_KEY_SECRET: ${business_intelligence.gong.access_key_secret}
  HUBSPOT_ACCESS_TOKEN: ${business_intelligence.hubspot.access_token}
  LINEAR_API_KEY: ${business_intelligence.linear.api_key}
  NOTION_API_KEY: ${business_intelligence.notion.api_key}
  ASANA_API_TOKEN: ${business_intelligence.asana.api_token}
  SLACK_BOT_TOKEN: ${business_intelligence.slack.bot_token}
  SLACK_WEBHOOK_URL: ${business_intelligence.slack.webhook_url}
  
  # Data Infrastructure
  QDRANT_API_KEY: ${data_infrastructure.qdrant.api_key}
  QDRANT_URL: ${data_infrastructure.qdrant.url}
  REDIS_PASSWORD: ${data_infrastructure.redis.password}
  REDIS_URL: ${data_infrastructure.redis.url}
  POSTGRES_HOST: ${data_infrastructure.postgres.host}
  POSTGRES_PASSWORD: ${data_infrastructure.postgres.password}
  POSTGRES_DATABASE: ${data_infrastructure.postgres.database}
  
  # Infrastructure
  LAMBDA_API_KEY: ${infrastructure.lambda_labs.api_key}
  LAMBDA_SSH_PRIVATE_KEY: ${infrastructure.lambda_labs.ssh_private_key}
  DOCKER_HUB_ACCESS_TOKEN: ${infrastructure.docker.hub_access_token}
  DOCKER_HUB_USERNAME: ${infrastructure.docker.username}
  PULUMI_ACCESS_TOKEN: ${infrastructure.pulumi.access_token}
"""
        
        return consolidated_config
    
    def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run comprehensive test suite"""
        print("🚀 Sophia AI - Comprehensive Pulumi ESC Test & Consolidation")
        print("=" * 80)
        
        # Test 1: Authentication
        auth_success = self.test_pulumi_auth()
        if not auth_success:
            return {"error": "Pulumi authentication failed"}
        
        # Test 2: ESC Environment Access
        env_success = self.test_esc_environment_access()
        if not env_success:
            return {"error": "ESC environment access failed"}
        
        # Test 3: Secret Retrieval
        secret_results = self.test_secret_retrieval()
        
        # Test 4: Direct Pulumi Access
        direct_results = self.test_direct_pulumi_access()
        
        # Test 5: Config File Analysis
        config_analysis = self.analyze_config_files()
        
        # Test 6: Generate Consolidated Config
        consolidated_config = self.generate_consolidated_config()
        
        # Summary
        total_secrets = len(secret_results)
        found_secrets = sum(1 for r in secret_results.values() if r.get('found', False))
        success_rate = (found_secrets / total_secrets * 100) if total_secrets > 0 else 0
        
        print(f"\n📊 Test Summary:")
        print(f"    Total secrets tested: {total_secrets}")
        print(f"    Secrets found: {found_secrets}")
        print(f"    Success rate: {success_rate:.1f}%")
        
        # Check MCP Project readiness
        mcp_critical_secrets = [
            "linear_api_key", "openai_api_key", "gong_access_key", 
            "hubspot_access_token", "notion_api_key", "slack_bot_token"
        ]
        
        mcp_ready = all(
            secret_results.get(secret, {}).get('found', False) 
            for secret in mcp_critical_secrets
        )
        
        print(f"\n🎯 MCP Project Readiness: {'✅ READY' if mcp_ready else '❌ NOT READY'}")
        
        return {
            "auth_success": auth_success,
            "env_success": env_success,
            "secret_results": secret_results,
            "direct_results": direct_results,
            "config_analysis": config_analysis,
            "consolidated_config": consolidated_config,
            "success_rate": success_rate,
            "mcp_ready": mcp_ready,
            "total_secrets": total_secrets,
            "found_secrets": found_secrets
        }

def main():
    """Main function"""
    tester = PulumiESCTester()
    results = tester.run_comprehensive_test()
    
    # Save results
    with open("pulumi_esc_test_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    # Save consolidated config
    if "consolidated_config" in results:
        with open("CONSOLIDATED_PULUMI_ESC_CONFIG.yaml", "w") as f:
            f.write(results["consolidated_config"])
    
    print(f"\n💾 Results saved to:")
    print(f"    - pulumi_esc_test_results.json")
    print(f"    - CONSOLIDATED_PULUMI_ESC_CONFIG.yaml")
    
    # Return exit code based on MCP readiness
    if results.get("mcp_ready", False):
        print(f"\n🎉 SUCCESS: Ready to proceed with MCP project!")
        return 0
    else:
        print(f"\n⚠️  WARNING: Some secrets missing for MCP project")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 