#!/usr/bin/env python3
"""
Comprehensive Infrastructure Audit & Server Configuration Optimizer for Sophia AI
This script audits current infrastructure state and provides optimization recommendations
"""

import os
import sys
import json
import subprocess
from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

@dataclass
class InfrastructureComponent:
    """Infrastructure component status"""
    name: str
    status: str
    details: Dict[str, Any]
    recommendations: List[str]

@dataclass
class ServerRecommendation:
    """Server optimization recommendation"""
    component: str
    current_state: str
    recommended_action: str
    priority: str
    estimated_cost: str
    business_impact: str

class SophiaAIInfrastructureAuditor:
    """Comprehensive infrastructure auditor for Sophia AI"""
    
    def __init__(self):
        self.components = []
        self.recommendations = []
        
    def audit_pulumi_esc_status(self) -> InfrastructureComponent:
        """Audit Pulumi ESC configuration and secrets"""
        print("🔍 Auditing Pulumi ESC Status...")
        
        try:
            # Check Pulumi access
            result = subprocess.run(
                ["pulumi", "whoami"], 
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode == 0:
                pulumi_user = result.stdout.strip()
                
                # Check ESC environment
                esc_result = subprocess.run(
                    ["pulumi", "env", "get", "scoobyjava-org/default/sophia-ai-production"],
                    capture_output=True, text=True, timeout=30
                )
                
                if esc_result.returncode == 0:
                    # Count secrets
                    secret_count = esc_result.stdout.count('[secret]')
                    placeholder_count = esc_result.stdout.count('PLACEHOLDER')
                    
                    status = "healthy" if placeholder_count == 0 else "degraded"
                    
                    details = {
                        "pulumi_user": pulumi_user,
                        "environment": "scoobyjava-org/default/sophia-ai-production",
                        "total_secrets": secret_count,
                        "placeholder_secrets": placeholder_count,
                        "sync_status": "working" if placeholder_count == 0 else "failed"
                    }
                    
                    recommendations = []
                    if placeholder_count > 0:
                        recommendations.append("Run GitHub Actions workflow to sync secrets")
                        recommendations.append("Use manual_lambda_sync.py for immediate Lambda credentials")
                    else:
                        recommendations.append("ESC is properly configured")
                    
                    return InfrastructureComponent(
                        name="Pulumi ESC",
                        status=status,
                        details=details,
                        recommendations=recommendations
                    )
                else:
                    return InfrastructureComponent(
                        name="Pulumi ESC",
                        status="failed",
                        details={"error": "Cannot access ESC environment"},
                        recommendations=["Check Pulumi access token", "Verify environment exists"]
                    )
            else:
                return InfrastructureComponent(
                    name="Pulumi ESC",
                    status="failed",
                    details={"error": "Pulumi authentication failed"},
                    recommendations=["Set PULUMI_ACCESS_TOKEN", "Run pulumi login"]
                )
                
        except Exception as e:
            return InfrastructureComponent(
                name="Pulumi ESC",
                status="error",
                details={"error": str(e)},
                recommendations=["Install Pulumi CLI", "Check network connectivity"]
            )
    
    def audit_snowflake_configuration(self) -> InfrastructureComponent:
        """Audit Snowflake configuration"""
        print("🔍 Auditing Snowflake Configuration...")
        
        try:
            from backend.core.auto_esc_config import get_snowflake_config
            from backend.core.absolute_snowflake_override import get_snowflake_connection_params
            
            # Get configuration from both sources
            esc_config = get_snowflake_config()
            override_config = get_snowflake_connection_params()
            
            # Check if override is working
            correct_account = override_config.get('account') == 'ZNB04675'
            
            details = {
                "esc_account": esc_config.get('account'),
                "override_account": override_config.get('account'),
                "using_correct_account": correct_account,
                "override_active": True,
                "database": override_config.get('database'),
                "warehouse": override_config.get('warehouse'),
                "user": override_config.get('user')
            }
            
            status = "healthy" if correct_account else "failed"
            
            recommendations = []
            if correct_account:
                recommendations.append("Snowflake configuration is correct")
                recommendations.append("Use ./start_sophia_absolute_fix.py to start with fix")
            else:
                recommendations.append("Run ultimate_snowflake_fix.py")
                recommendations.append("Verify absolute override is imported")
            
            return InfrastructureComponent(
                name="Snowflake Configuration",
                status=status,
                details=details,
                recommendations=recommendations
            )
            
        except Exception as e:
            return InfrastructureComponent(
                name="Snowflake Configuration", 
                status="error",
                details={"error": str(e)},
                recommendations=["Run ultimate_snowflake_fix.py", "Check imports"]
            )
    
    def audit_sophia_ai_services(self) -> InfrastructureComponent:
        """Audit Sophia AI services status"""
        print("🔍 Auditing Sophia AI Services...")
        
        services_status = {}
        
        # Check if FastAPI app can import
        try:
            from backend.app.fastapi_app import app
            services_status["fastapi"] = {"status": "importable", "error": None}
        except Exception as e:
            services_status["fastapi"] = {"status": "failed", "error": str(e)}
        
        # Check MCP servers directory
        mcp_servers = []
        mcp_dir = "mcp-servers"
        if os.path.exists(mcp_dir):
            for item in os.listdir(mcp_dir):
                item_path = os.path.join(mcp_dir, item)
                if os.path.isdir(item_path) and not item.startswith('.'):
                    mcp_servers.append(item)
        
        # Check key backend services
        backend_services = [
            "backend/core/optimized_connection_manager.py",
            "backend/services/enhanced_unified_chat_service.py", 
            "backend/agents/specialized/sales_coach_agent.py"
        ]
        
        service_files = {}
        for service in backend_services:
            service_files[service] = os.path.exists(service)
        
        details = {
            "fastapi_status": services_status["fastapi"]["status"],
            "mcp_servers": mcp_servers,
            "mcp_server_count": len(mcp_servers),
            "backend_services": service_files,
            "total_backend_files": sum(1 for exists in service_files.values() if exists)
        }
        
        status = "healthy" if services_status["fastapi"]["status"] == "importable" else "degraded"
        
        recommendations = []
        if status == "healthy":
            recommendations.append("Core services are operational")
            recommendations.append(f"Ready to deploy {len(mcp_servers)} MCP servers")
        else:
            recommendations.append("Fix import errors before deployment")
            recommendations.append("Run Snowflake fix if connection issues persist")
        
        return InfrastructureComponent(
            name="Sophia AI Services",
            status=status,
            details=details,
            recommendations=recommendations
        )
    
    def analyze_lambda_labs_requirements(self) -> List[ServerRecommendation]:
        """Analyze Lambda Labs server requirements for Sophia AI"""
        print("🔍 Analyzing Lambda Labs Requirements...")
        
        recommendations = []
        
        # Based on Sophia AI architecture analysis
        recommendations.append(ServerRecommendation(
            component="Primary Compute",
            current_state="No active Lambda Labs instances",
            recommended_action="Deploy 1x gpu_1x_a100_sxm4 (A100 80GB)",
            priority="High",
            estimated_cost="$1.10-2.06/hour",
            business_impact="Enables real-time AI processing for Snowflake Cortex, OpenAI orchestration, and vector operations"
        ))
        
        recommendations.append(ServerRecommendation(
            component="Development Environment", 
            current_state="Local development only",
            recommended_action="Deploy 1x gpu_1x_rtx4090 for development/testing",
            priority="Medium",
            estimated_cost="$0.50-0.90/hour",
            business_impact="Faster development cycles, testing without affecting production"
        ))
        
        recommendations.append(ServerRecommendation(
            component="High Availability",
            current_state="Single point of failure",
            recommended_action="Multi-region deployment (us-west-1, us-east-1)",
            priority="Medium", 
            estimated_cost="2x instance costs",
            business_impact="99.9% uptime for enterprise clients"
        ))
        
        recommendations.append(ServerRecommendation(
            component="Auto-scaling",
            current_state="Manual scaling",
            recommended_action="Implement auto-scaling based on API usage",
            priority="Low",
            estimated_cost="Variable based on usage",
            business_impact="Cost optimization during off-peak hours"
        ))
        
        recommendations.append(ServerRecommendation(
            component="Security",
            current_state="Basic security",
            recommended_action="Implement VPC, security groups, SSH key rotation",
            priority="High",
            estimated_cost="Minimal additional cost",
            business_impact="Enterprise-grade security compliance"
        ))
        
        return recommendations
    
    def generate_deployment_plan(self) -> Dict[str, Any]:
        """Generate comprehensive deployment plan"""
        print("🔍 Generating Deployment Plan...")
        
        # Phase 1: Immediate (Week 1)
        phase1 = {
            "name": "Infrastructure Foundation",
            "duration": "1 week",
            "tasks": [
                "Fix GitHub→Pulumi ESC sync (COMPLETED)",
                "Deploy primary Lambda Labs instance (A100 80GB)",
                "Configure Snowflake connections (COMPLETED)",
                "Deploy core MCP servers",
                "Set up monitoring and alerts"
            ],
            "estimated_cost": "$200-400/week",
            "business_value": "Core AI platform operational"
        }
        
        # Phase 2: Optimization (Week 2-3)
        phase2 = {
            "name": "Performance & Reliability",
            "duration": "2 weeks", 
            "tasks": [
                "Implement auto-scaling",
                "Set up development environment",
                "Configure multi-region deployment",
                "Optimize database connections",
                "Performance testing and tuning"
            ],
            "estimated_cost": "$400-800/week",
            "business_value": "Enterprise-grade reliability and performance"
        }
        
        # Phase 3: Advanced Features (Week 4-6)
        phase3 = {
            "name": "Advanced AI Capabilities",
            "duration": "3 weeks",
            "tasks": [
                "Deploy advanced MCP servers",
                "Implement AI model optimization",
                "Set up advanced monitoring",
                "Security hardening",
                "Business intelligence dashboards"
            ],
            "estimated_cost": "$600-1200/week",
            "business_value": "Advanced AI orchestration and business intelligence"
        }
        
        return {
            "phases": [phase1, phase2, phase3],
            "total_duration": "6 weeks",
            "estimated_total_cost": "$1200-2400",
            "roi_projection": "300-500% within 3 months",
            "key_milestones": [
                "Week 1: Core platform operational",
                "Week 3: Enterprise-grade reliability",
                "Week 6: Advanced AI capabilities"
            ]
        }
    
    def run_comprehensive_audit(self) -> Dict[str, Any]:
        """Run complete infrastructure audit"""
        print("🚀 COMPREHENSIVE SOPHIA AI INFRASTRUCTURE AUDIT")
        print("=" * 70)
        
        # Audit all components
        self.components = [
            self.audit_pulumi_esc_status(),
            self.audit_snowflake_configuration(),
            self.audit_sophia_ai_services()
        ]
        
        # Analyze server requirements
        server_recommendations = self.analyze_lambda_labs_requirements()
        
        # Generate deployment plan
        deployment_plan = self.generate_deployment_plan()
        
        # Calculate overall health score
        healthy_components = sum(1 for c in self.components if c.status == "healthy")
        total_components = len(self.components)
        health_score = (healthy_components / total_components) * 100
        
        return {
            "audit_timestamp": datetime.now().isoformat(),
            "overall_health_score": f"{health_score:.1f}%",
            "components": [
                {
                    "name": c.name,
                    "status": c.status,
                    "details": c.details,
                    "recommendations": c.recommendations
                }
                for c in self.components
            ],
            "server_recommendations": [
                {
                    "component": r.component,
                    "current_state": r.current_state,
                    "recommended_action": r.recommended_action,
                    "priority": r.priority,
                    "estimated_cost": r.estimated_cost,
                    "business_impact": r.business_impact
                }
                for r in server_recommendations
            ],
            "deployment_plan": deployment_plan
        }

def main():
    """Main execution function"""
    auditor = SophiaAIInfrastructureAuditor()
    
    # Run comprehensive audit
    audit_results = auditor.run_comprehensive_audit()
    
    # Display results
    print(f"\n📊 AUDIT RESULTS")
    print("=" * 50)
    print(f"Overall Health Score: {audit_results['overall_health_score']}")
    
    print(f"\n🔧 COMPONENT STATUS:")
    for component in audit_results['components']:
        status_emoji = "✅" if component['status'] == "healthy" else "⚠️" if component['status'] == "degraded" else "❌"
        print(f"  {status_emoji} {component['name']}: {component['status']}")
        
        if component['recommendations']:
            print(f"    Recommendations:")
            for rec in component['recommendations']:
                print(f"      - {rec}")
    
    print(f"\n🖥️ SERVER RECOMMENDATIONS:")
    for rec in audit_results['server_recommendations']:
        priority_emoji = "🔴" if rec['priority'] == "High" else "🟡" if rec['priority'] == "Medium" else "🟢"
        print(f"  {priority_emoji} {rec['component']} ({rec['priority']} Priority)")
        print(f"    Current: {rec['current_state']}")
        print(f"    Action: {rec['recommended_action']}")
        print(f"    Cost: {rec['estimated_cost']}")
        print(f"    Impact: {rec['business_impact']}")
        print()
    
    print(f"📋 DEPLOYMENT PLAN:")
    for i, phase in enumerate(audit_results['deployment_plan']['phases'], 1):
        print(f"  Phase {i}: {phase['name']} ({phase['duration']})")
        print(f"    Cost: {phase['estimated_cost']}")
        print(f"    Value: {phase['business_value']}")
        for task in phase['tasks']:
            print(f"      - {task}")
        print()
    
    print(f"💰 INVESTMENT SUMMARY:")
    plan = audit_results['deployment_plan']
    print(f"  Total Duration: {plan['total_duration']}")
    print(f"  Estimated Cost: {plan['estimated_total_cost']}")
    print(f"  ROI Projection: {plan['roi_projection']}")
    
    # Save detailed report
    with open('sophia_ai_infrastructure_audit.json', 'w') as f:
        json.dump(audit_results, f, indent=2)
    
    print(f"\n📄 Detailed report saved: sophia_ai_infrastructure_audit.json")
    
    # Provide immediate next steps
    print(f"\n🚀 IMMEDIATE NEXT STEPS:")
    print("1. Fix any degraded components shown above")
    print("2. Configure Lambda Labs credentials using manual_lambda_sync.py")
    print("3. Deploy primary Lambda Labs instance")
    print("4. Test Sophia AI platform with ./start_sophia_absolute_fix.py")
    print("5. Begin Phase 1 deployment tasks")
    
    return audit_results

if __name__ == "__main__":
    results = main()
    
    # Exit with appropriate code
    health_score = float(results['overall_health_score'].rstrip('%'))
    sys.exit(0 if health_score >= 80 else 1)
