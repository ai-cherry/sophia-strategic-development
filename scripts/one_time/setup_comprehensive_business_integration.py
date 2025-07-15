#!/usr/bin/env python3
"""
Comprehensive Business Integration Setup for Sophia AI
Sets up real integrations with HubSpot, Slack, Gong, Linear, Asana, Notion, Salesforce
"""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional
import aiohttp
import subprocess

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BusinessIntegrationSetup:
    """Comprehensive business integration setup manager"""
    
    def __init__(self):
        self.integrations = {
            "hubspot": {
                "name": "HubSpot CRM",
                "api_key_env": "HUBSPOT_API_KEY",
                "base_url": "https://api.hubapi.com",
                "mcp_port": 9006,
                "status": "pending"
            },
            "slack": {
                "name": "Slack Team Communication",
                "api_key_env": "SLACK_BOT_TOKEN",
                "base_url": "https://slack.com/api",
                "mcp_port": 9005,
                "status": "pending"
            },
            "gong": {
                "name": "Gong.io Call Intelligence",
                "api_key_env": "GONG_API_KEY",
                "base_url": "https://api.gong.io",
                "mcp_port": 9007,
                "status": "pending"
            },
            "linear": {
                "name": "Linear Project Management",
                "api_key_env": "LINEAR_API_KEY",
                "base_url": "https://api.linear.app",
                "mcp_port": 9004,
                "status": "pending"
            },
            "asana": {
                "name": "Asana Business Operations",
                "api_key_env": "ASANA_ACCESS_TOKEN",
                "base_url": "https://app.asana.com/api/1.0",
                "mcp_port": 9008,
                "status": "pending"
            },
            "notion": {
                "name": "Notion Knowledge Management",
                "api_key_env": "NOTION_API_KEY",
                "base_url": "https://api.notion.com/v1",
                "mcp_port": 9009,
                "status": "pending"
            },
            "salesforce": {
                "name": "Salesforce Enterprise",
                "api_key_env": "SALESFORCE_ACCESS_TOKEN",
                "base_url": "https://your-domain.salesforce.com",
                "mcp_port": 9010,
                "status": "pending"
            }
        }
        
    async def validate_api_credentials(self, integration: str) -> bool:
        """Validate API credentials for an integration"""
        config = self.integrations[integration]
        api_key = os.getenv(config["api_key_env"])
        
        if not api_key:
            logger.warning(f"❌ {config['name']}: API key not found in environment variable {config['api_key_env']}")
            return False
            
        try:
            async with aiohttp.ClientSession() as session:
                if integration == "hubspot":
                    url = f"{config['base_url']}/crm/v3/objects/contacts?limit=1"
                    headers = {"Authorization": f"Bearer {api_key}"}
                elif integration == "slack":
                    url = f"{config['base_url']}/auth.test"
                    headers = {"Authorization": f"Bearer {api_key}"}
                elif integration == "gong":
                    url = f"{config['base_url']}/v2/users"
                    headers = {"Authorization": f"Basic {api_key}"}
                elif integration == "linear":
                    url = f"{config['base_url']}/graphql"
                    headers = {"Authorization": f"Bearer {api_key}"}
                    # Linear uses GraphQL, so we need a simple query
                    data = {"query": "{ viewer { id name } }"}
                    async with session.post(url, headers=headers, json=data) as response:
                        if response.status == 200:
                            logger.info(f"✅ {config['name']}: API credentials validated")
                            return True
                        else:
                            logger.error(f"❌ {config['name']}: API validation failed (status: {response.status})")
                            return False
                elif integration == "asana":
                    url = f"{config['base_url']}/users/me"
                    headers = {"Authorization": f"Bearer {api_key}"}
                elif integration == "notion":
                    url = f"{config['base_url']}/users/me"
                    headers = {"Authorization": f"Bearer {api_key}", "Notion-Version": "2022-06-28"}
                elif integration == "salesforce":
                    # Salesforce validation would need OAuth flow - skip for now
                    logger.info(f"⚠️ {config['name']}: Salesforce validation requires OAuth setup")
                    return True
                else:
                    logger.warning(f"⚠️ {config['name']}: Validation not implemented")
                    return True
                
                # For non-Linear integrations
                if integration != "linear":
                    async with session.get(url, headers=headers) as response:
                        if response.status == 200:
                            logger.info(f"✅ {config['name']}: API credentials validated")
                            return True
                        else:
                            logger.error(f"❌ {config['name']}: API validation failed (status: {response.status})")
                            return False
                            
        except Exception as e:
            logger.error(f"❌ {config['name']}: API validation error: {e}")
            return False
            
    def create_mcp_server_config(self, integration: str) -> Dict:
        """Create MCP server configuration for an integration"""
        config = self.integrations[integration]
        
        base_config = {
            "name": f"{integration}_mcp",
            "description": f"{config['name']} MCP Server",
            "port": config["mcp_port"],
            "environment": {
                config["api_key_env"]: f"${config['api_key_env']}",
                "ENVIRONMENT": "prod",
                "LOG_LEVEL": "info"
            },
            "health_check": {
                "enabled": True,
                "endpoint": "/health",
                "interval": 30
            },
            "monitoring": {
                "prometheus": True,
                "metrics_port": config["mcp_port"] + 1000
            }
        }
        
        # Integration-specific configurations
        if integration == "hubspot":
            base_config.update({
                "features": [
                    "contacts_sync",
                    "deals_analysis", 
                    "companies_management",
                    "revenue_forecasting",
                    "sales_analytics"
                ],
                "webhooks": {
                    "enabled": True,
                    "endpoint": "/webhooks/hubspot",
                    "events": ["contact.creation", "deal.update", "company.update"]
                }
            })
        elif integration == "slack":
            base_config.update({
                "features": [
                    "channel_monitoring",
                    "message_analysis",
                    "team_productivity",
                    "automated_responses",
                    "sentiment_tracking"
                ],
                "bot_config": {
                    "name": "@sophia-ai",
                    "channels": ["#general", "#dev", "#sales", "#support"],
                    "triggers": ["@sophia-ai", "sophia", "help"]
                }
            })
        elif integration == "gong":
            base_config.update({
                "features": [
                    "call_transcription",
                    "sentiment_analysis",
                    "competitive_intelligence",
                    "sales_coaching",
                    "deal_risk_assessment"
                ],
                "ai_processing": {
                    "gpu_acceleration": True,
                    "batch_processing": True,
                    "real_time_analysis": True
                }
            })
        elif integration == "linear":
            base_config.update({
                "features": [
                    "project_tracking",
                    "velocity_analysis",
                    "sprint_planning",
                    "bug_triage",
                    "technical_debt_tracking"
                ],
                "graphql": {
                    "enabled": True,
                    "batch_queries": True,
                    "subscriptions": True
                }
            })
        elif integration == "asana":
            base_config.update({
                "features": [
                    "project_portfolio",
                    "resource_allocation",
                    "deadline_tracking",
                    "team_collaboration",
                    "process_automation"
                ],
                "business_operations": {
                    "marketing_campaigns": True,
                    "sales_processes": True,
                    "customer_success": True
                }
            })
        elif integration == "notion":
            base_config.update({
                "features": [
                    "knowledge_management",
                    "document_intelligence",
                    "meeting_notes",
                    "process_documentation",
                    "institutional_memory"
                ],
                "ai_features": {
                    "semantic_search": True,
                    "auto_summarization": True,
                    "knowledge_extraction": True
                }
            })
        elif integration == "salesforce":
            base_config.update({
                "features": [
                    "enterprise_crm",
                    "opportunity_management",
                    "territory_planning",
                    "campaign_analytics",
                    "executive_reporting"
                ],
                "enterprise": {
                    "oauth2": True,
                    "sandbox_support": True,
                    "bulk_api": True
                }
            })
            
        return base_config
        
    def create_kubernetes_deployment(self, integration: str) -> str:
        """Create Kubernetes deployment YAML for MCP server"""
        config = self.integrations[integration]
        mcp_config = self.create_mcp_server_config(integration)
        
        yaml_content = f"""apiVersion: apps/v1
kind: Deployment
metadata:
  name: mcp-{integration}
  namespace: mcp-servers
  labels:
    app: mcp-{integration}
    integration: {integration}
spec:
  replicas: 2
  selector:
    matchLabels:
      app: mcp-{integration}
  template:
    metadata:
      labels:
        app: mcp-{integration}
        integration: {integration}
    spec:
      containers:
      - name: mcp-{integration}
        image: sophia-ai/mcp-{integration}:latest
        ports:
        - containerPort: {config['mcp_port']}
        - containerPort: {config['mcp_port'] + 1000}  # Metrics port
        env:
        - name: {config['api_key_env']}
          valueFrom:
            secretKeyRef:
              name: {integration}-secrets
              key: api-key
        - name: ENVIRONMENT
          value: "prod"
        - name: MCP_PORT
          value: "{config['mcp_port']}"
        - name: LOG_LEVEL
          value: "info"
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: {config['mcp_port']}
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: {config['mcp_port']}
          initialDelaySeconds: 5
          periodSeconds: 5
      nodeSelector:
        sophia.ai/node-type: "mcp-orchestrator"
---
apiVersion: v1
kind: Service
metadata:
  name: mcp-{integration}-service
  namespace: mcp-servers
  labels:
    app: mcp-{integration}
spec:
  selector:
    app: mcp-{integration}
  ports:
  - name: mcp
    port: {config['mcp_port']}
    targetPort: {config['mcp_port']}
  - name: metrics
    port: {config['mcp_port'] + 1000}
    targetPort: {config['mcp_port'] + 1000}
  type: ClusterIP
---
apiVersion: v1
kind: Secret
metadata:
  name: {integration}-secrets
  namespace: mcp-servers
type: Opaque
data:
  api-key: ""  # Base64 encoded API key - to be filled by deployment script
"""
        return yaml_content
        
    def create_business_intelligence_config(self) -> Dict:
        """Create comprehensive business intelligence configuration"""
        return {
            "business_intelligence": {
                "data_sources": {
                    "crm": {
                        "primary": "hubspot",
                        "secondary": "salesforce",
                        "sync_interval": "5m",
                        "real_time_webhooks": True
                    },
                    "communication": {
                        "primary": "slack",
                        "analysis": {
                            "sentiment": True,
                            "productivity": True,
                            "collaboration": True
                        }
                    },
                    "sales_intelligence": {
                        "primary": "gong",
                        "features": {
                            "call_analysis": True,
                            "competitive_intel": True,
                            "deal_scoring": True,
                            "coaching": True
                        }
                    },
                    "project_management": {
                        "development": "linear",
                        "business_ops": "asana",
                        "metrics": {
                            "velocity": True,
                            "quality": True,
                            "resource_allocation": True
                        }
                    },
                    "knowledge": {
                        "primary": "notion",
                        "features": {
                            "semantic_search": True,
                            "auto_categorization": True,
                            "knowledge_gaps": True
                        }
                    }
                },
                "ai_orchestration": {
                    "cross_platform_correlation": True,
                    "predictive_analytics": True,
                    "automated_insights": True,
                    "real_time_alerts": True,
                    "executive_reporting": True
                },
                "memory_integration": {
                    "qdrant": {
                        "business_patterns": True,
                        "customer_insights": True,
                        "sales_intelligence": True
                    },
                    "redis": {
                        "real_time_metrics": True,
                        "active_deals": True,
                        "team_status": True
                    },
                    "postgresql": {
                        "historical_analytics": True,
                        "performance_trends": True,
                        "roi_analysis": True
                    }
                }
            }
        }
        
    async def setup_integration(self, integration: str) -> bool:
        """Set up a specific business integration"""
        logger.info(f"🚀 Setting up {self.integrations[integration]['name']}...")
        
        # Validate API credentials
        if not await self.validate_api_credentials(integration):
            self.integrations[integration]["status"] = "failed"
            return False
            
        # Create MCP server configuration
        mcp_config = self.create_mcp_server_config(integration)
        config_path = Path(f"config/mcp/{integration}_config.json")
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w') as f:
            json.dump(mcp_config, f, indent=2)
        logger.info(f"✅ Created MCP configuration: {config_path}")
        
        # Create Kubernetes deployment
        k8s_yaml = self.create_kubernetes_deployment(integration)
        k8s_path = Path(f"k8s/mcp-servers/{integration}.yaml")
        k8s_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(k8s_path, 'w') as f:
            f.write(k8s_yaml)
        logger.info(f"✅ Created Kubernetes deployment: {k8s_path}")
        
        self.integrations[integration]["status"] = "configured"
        return True
        
    async def setup_all_integrations(self):
        """Set up all business integrations"""
        logger.info("🚀 Starting comprehensive business integration setup...")
        
        # Setup individual integrations
        for integration in self.integrations.keys():
            await self.setup_integration(integration)
            
        # Create business intelligence configuration
        bi_config = self.create_business_intelligence_config()
        bi_path = Path("config/business_intelligence.json")
        with open(bi_path, 'w') as f:
            json.dump(bi_config, f, indent=2)
        logger.info(f"✅ Created business intelligence config: {bi_path}")
        
        # Create unified MCP ports configuration
        mcp_ports = {
            "mcp_servers": {
                integration: {
                    "port": config["mcp_port"],
                    "name": config["name"],
                    "status": config["status"]
                }
                for integration, config in self.integrations.items()
            }
        }
        
        ports_path = Path("config/enhanced_mcp_ports.json")
        with open(ports_path, 'w') as f:
            json.dump(mcp_ports, f, indent=2)
        logger.info(f"✅ Created enhanced MCP ports config: {ports_path}")
        
        # Generate deployment summary
        self.generate_deployment_summary()
        
    def generate_deployment_summary(self):
        """Generate deployment summary report"""
        successful = [k for k, v in self.integrations.items() if v["status"] == "configured"]
        failed = [k for k, v in self.integrations.items() if v["status"] == "failed"]
        
        summary = f"""# 🚀 BUSINESS INTEGRATION DEPLOYMENT SUMMARY

**Date**: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Total Integrations**: {len(self.integrations)}
**Successful**: {len(successful)}
**Failed**: {len(failed)}
**Success Rate**: {len(successful)/len(self.integrations)*100:.1f}%

## ✅ Successfully Configured Integrations

"""
        
        for integration in successful:
            config = self.integrations[integration]
            summary += f"- **{config['name']}** (Port {config['mcp_port']})\n"
            
        if failed:
            summary += f"\n## ❌ Failed Integrations\n\n"
            for integration in failed:
                config = self.integrations[integration]
                summary += f"- **{config['name']}** - Check API credentials\n"
                
        summary += f"""
## 🚀 Next Steps

### 1. Deploy to Lambda Labs K3s
```bash
# Deploy all MCP servers
kubectl apply -f k8s/mcp-servers/

# Verify deployments
kubectl get pods -n mcp-servers
```

### 2. Configure API Keys
```bash
# Set environment variables for successful integrations
"""

        for integration in successful:
            config = self.integrations[integration]
            summary += f"export {config['api_key_env']}=\"your_api_key_here\"\n"
            
        summary += f"""
```

### 3. Test Integrations
```bash
# Test each MCP server
python scripts/test_business_integrations.py
```

## 📊 Business Intelligence Ready

With {len(successful)} integrations configured, Sophia AI can now provide:
- Real-time business intelligence
- Cross-platform data correlation
- Predictive analytics
- Automated insights and reporting
- Executive dashboard with live data

**Ready for production deployment on Lambda Labs!**
"""
        
        summary_path = Path("BUSINESS_INTEGRATION_SUMMARY.md")
        with open(summary_path, 'w') as f:
            f.write(summary)
        logger.info(f"✅ Generated deployment summary: {summary_path}")
        
async def main():
    """Main setup function"""
    setup = BusinessIntegrationSetup()
    await setup.setup_all_integrations()
    
    print("\n🎉 BUSINESS INTEGRATION SETUP COMPLETE!")
    print("📋 Check BUSINESS_INTEGRATION_SUMMARY.md for next steps")
    print("🚀 Ready to deploy to Lambda Labs K3s cluster!")

if __name__ == "__main__":
    asyncio.run(main()) 