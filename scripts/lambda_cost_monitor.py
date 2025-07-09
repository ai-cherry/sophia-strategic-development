#!/usr/bin/env python3
"""
Lambda Labs Cost Monitor
Optimized cost monitoring and optimization for Lambda Labs infrastructure
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Lambda Labs instance configuration
LAMBDA_INSTANCES = {
    "sophia-ai-core": {
        "ip": "192.222.58.232",
        "gpu": "GH200",
        "cost_per_hour": 1.49,
        "workload": "training,large-inference"
    },
    "sophia-mcp-orchestrator": {
        "ip": "104.171.202.117", 
        "gpu": "A6000",
        "cost_per_hour": 0.80,
        "workload": "mcp-orchestration"
    },
    "sophia-data-pipeline": {
        "ip": "104.171.202.134",
        "gpu": "A100", 
        "cost_per_hour": 1.29,
        "workload": "data-processing"
    },
    "sophia-production": {
        "ip": "104.171.202.103",
        "gpu": "RTX6000",
        "cost_per_hour": 0.50,
        "workload": "production-backend"
    },
    "sophia-development": {
        "ip": "155.248.194.183",
        "gpu": "A10",
        "cost_per_hour": 0.75,
        "workload": "development"
    }
}

class LambdaCostMonitor:
    def __init__(self):
        self.total_hourly_cost = sum(instance["cost_per_hour"] for instance in LAMBDA_INSTANCES.values())
        self.daily_budget = 120.00  # $120/day budget
        self.monthly_budget = 3600.00  # $3600/month budget
        
    async def monitor_costs(self):
        """Monitor current costs and usage"""
        logger.info("🔍 Monitoring Lambda Labs costs...")
        
        current_hour_cost = self.total_hourly_cost
        daily_cost = current_hour_cost * 24
        monthly_cost = daily_cost * 30
        
        cost_report = {
            "timestamp": datetime.now().isoformat(),
            "costs": {
                "hourly": round(current_hour_cost, 2),
                "daily": round(daily_cost, 2), 
                "monthly": round(monthly_cost, 2),
                "yearly": round(monthly_cost * 12, 2)
            },
            "budgets": {
                "daily_budget": self.daily_budget,
                "monthly_budget": self.monthly_budget,
                "daily_utilization": round((daily_cost / self.daily_budget) * 100, 1),
                "monthly_utilization": round((monthly_cost / self.monthly_budget) * 100, 1)
            },
            "instances": {}
        }
        
        for name, config in LAMBDA_INSTANCES.items():
            instance_daily = config["cost_per_hour"] * 24
            cost_report["instances"][name] = {
                "gpu": config["gpu"],
                "hourly": config["cost_per_hour"],
                "daily": round(instance_daily, 2),
                "monthly": round(instance_daily * 30, 2),
                "workload": config["workload"]
            }
        
        # Check budget alerts
        if daily_cost > self.daily_budget:
            logger.warning(f"⚠️  Daily budget exceeded: ${daily_cost:.2f} > ${self.daily_budget}")
            
        if monthly_cost > self.monthly_budget:
            logger.warning(f"⚠️  Monthly budget exceeded: ${monthly_cost:.2f} > ${self.monthly_budget}")
        
        return cost_report
    
    async def optimization_recommendations(self):
        """Generate cost optimization recommendations"""
        logger.info("💡 Generating optimization recommendations...")
        
        recommendations = []
        
        # Development instance optimization
        dev_cost = LAMBDA_INSTANCES["sophia-development"]["cost_per_hour"] * 24
        business_hours_cost = dev_cost * (8/24) * (5/7)  # 8 hours/day, 5 days/week
        dev_savings = dev_cost - business_hours_cost
        
        if dev_savings > 5:  # If savings > $5/day
            recommendations.append({
                "type": "business_hours_scheduling",
                "instance": "sophia-development", 
                "current_daily": round(dev_cost, 2),
                "optimized_daily": round(business_hours_cost, 2),
                "daily_savings": round(dev_savings, 2),
                "monthly_savings": round(dev_savings * 30, 2),
                "action": "Implement auto-shutdown outside business hours"
            })
        
        # Serverless inference migration
        inference_cost_current = 930  # Current monthly cost for dedicated inference
        inference_cost_serverless = 250  # Serverless cost
        inference_savings = inference_cost_current - inference_cost_serverless
        
        recommendations.append({
            "type": "serverless_migration",
            "service": "inference_workloads",
            "current_monthly": inference_cost_current,
            "optimized_monthly": inference_cost_serverless, 
            "monthly_savings": inference_savings,
            "savings_percentage": round((inference_savings / inference_cost_current) * 100, 1),
            "action": "Migrate to Lambda Labs Serverless Inference API"
        })
        
        # Auto-scaling recommendations
        total_monthly = sum(config["cost_per_hour"] * 24 * 30 for config in LAMBDA_INSTANCES.values())
        auto_scale_savings = total_monthly * 0.25  # Estimated 25% savings
        
        recommendations.append({
            "type": "auto_scaling",
            "current_monthly": round(total_monthly, 2),
            "potential_savings": round(auto_scale_savings, 2),
            "savings_percentage": 25,
            "action": "Implement intelligent auto-scaling based on workload patterns"
        })
        
        return recommendations
    
    async def generate_report(self):
        """Generate comprehensive cost report"""
        logger.info("📊 Generating comprehensive cost report...")
        
        cost_data = await self.monitor_costs()
        recommendations = await self.optimization_recommendations()
        
        total_potential_savings = sum(
            rec.get("monthly_savings", rec.get("potential_savings", 0)) 
            for rec in recommendations
        )
        
        report = {
            "report_date": datetime.now().isoformat(),
            "current_costs": cost_data,
            "optimization_recommendations": recommendations,
            "summary": {
                "current_monthly_cost": cost_data["costs"]["monthly"],
                "potential_monthly_savings": round(total_potential_savings, 2),
                "optimized_monthly_cost": round(cost_data["costs"]["monthly"] - total_potential_savings, 2),
                "savings_percentage": round((total_potential_savings / cost_data["costs"]["monthly"]) * 100, 1)
            }
        }
        
        return report

async def main():
    monitor = LambdaCostMonitor()
    report = await monitor.generate_report()
    
    print("\n" + "="*60)
    print("🏷️  LAMBDA LABS COST OPTIMIZATION REPORT")
    print("="*60)
    
    print(f"\n💰 Current Costs:")
    print(f"   Daily: ${report['current_costs']['costs']['daily']}")
    print(f"   Monthly: ${report['current_costs']['costs']['monthly']}")
    print(f"   Yearly: ${report['current_costs']['costs']['yearly']}")
    
    print(f"\n📊 Budget Utilization:")
    print(f"   Daily: {report['current_costs']['budgets']['daily_utilization']}%")
    print(f"   Monthly: {report['current_costs']['budgets']['monthly_utilization']}%")
    
    print(f"\n💡 Optimization Opportunities:")
    for i, rec in enumerate(report['optimization_recommendations'], 1):
        savings = rec.get('monthly_savings', rec.get('potential_savings', 0))
        print(f"   {i}. {rec['type']}: ${savings}/month savings")
    
    print(f"\n🎯 Summary:")
    print(f"   Current Monthly Cost: ${report['summary']['current_monthly_cost']}")
    print(f"   Potential Savings: ${report['summary']['potential_monthly_savings']}")
    print(f"   Optimized Cost: ${report['summary']['optimized_monthly_cost']}")
    print(f"   Savings Percentage: {report['summary']['savings_percentage']}%")
    
    # Save report
    with open(f"lambda_cost_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Report saved to lambda_cost_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")

if __name__ == "__main__":
    asyncio.run(main())
