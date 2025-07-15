# 🚀 MCP Project Production Deployment Plan

## Executive Summary
**Objective:** Deploy Sophia AI MCP platform for 24/7 production operation
**Timeline:** 2-3 weeks for full production deployment
**Target:** 99.9% uptime, <2s response times, enterprise security

## 🏗️ Current State Analysis

### ✅ What's Ready for Production
- **Backend API**: Operational on port 8000 with all endpoints
- **MCP Servers**: 7 platforms integrated (Linear, Asana, Notion, HubSpot, Gong, Slack, GitHub)
- **Pulumi ESC**: Consolidated secret management
- **API Endpoints**: All `/api/v4/mcp/{platform}/projects` working
- **Error Handling**: Comprehensive fallback systems
- **Documentation**: Complete implementation docs

### ⚠️ What Needs Production Hardening
- **Infrastructure**: Currently running locally, needs cloud deployment
- **Database**: No persistent storage for production data
- **Monitoring**: Basic health checks, needs comprehensive observability
- **Security**: API keys configured but need production security hardening
- **Scaling**: Single instance, needs horizontal scaling
- **CI/CD**: Manual deployment, needs automated pipelines

## 🎯 Production Deployment Strategy

### Phase 1: Infrastructure Foundation (Week 1)
**Goal:** Deploy core infrastructure with 99% uptime capability

#### 1.1 Lambda Labs Production Deployment
```bash
# Deploy to Lambda Labs K8s cluster
kubectl apply -f k8s/production/sophia-ai-production.yaml

# Target Infrastructure:
# - Primary: 192.222.58.232 (GH200 GPU)
# - Load Balancer: 104.171.202.117 (A6000)
# - Database: 104.171.202.134 (A100)
```

#### 1.2 Container Registry & Images
```bash
# Build and push production images
docker build -t scoobyjava15/sophia-ai-backend:latest .
docker build -t scoobyjava15/sophia-ai-mcp-orchestrator:latest .
docker push scoobyjava15/sophia-ai-backend:latest
docker push scoobyjava15/sophia-ai-mcp-orchestrator:latest
```

#### 1.3 Database Infrastructure
```yaml
# PostgreSQL for persistent data
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 100Gi
```

### Phase 2: Security & Secrets (Week 1)
**Goal:** Enterprise-grade security with zero secret exposure

#### 2.1 API Key Configuration
```bash
# Add all production API keys to Pulumi ESC
pulumi env set scoobyjava-org/default/sophia-ai-production \
  --secret linear_api_key="lin_api_PRODUCTION_KEY"
pulumi env set scoobyjava-org/default/sophia-ai-production \
  --secret asana_api_token="ASANA_PRODUCTION_TOKEN"
pulumi env set scoobyjava-org/default/sophia-ai-production \
  --secret notion_api_key="secret_NOTION_PRODUCTION_KEY"
pulumi env set scoobyjava-org/default/sophia-ai-production \
  --secret hubspot_access_token="HUBSPOT_PRODUCTION_TOKEN"
```

#### 2.2 Network Security
```yaml
# Network policies for K8s
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: sophia-ai-network-policy
spec:
  podSelector:
    matchLabels:
      app: sophia-ai
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: sophia-ai-prod
    ports:
    - protocol: TCP
      port: 8000
```

### Phase 3: Monitoring & Observability (Week 2)
**Goal:** Comprehensive 24/7 monitoring with proactive alerting

#### 3.1 Prometheus Monitoring Stack
```yaml
# Deploy monitoring stack
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
    scrape_configs:
    - job_name: 'sophia-ai-backend'
      static_configs:
      - targets: ['sophia-ai-backend:8000']
    - job_name: 'mcp-servers'
      static_configs:
      - targets: ['mcp-linear:9040', 'mcp-asana:9006', 'mcp-notion:9102']
```

#### 3.2 Grafana Dashboards
```json
{
  "dashboard": {
    "title": "Sophia AI MCP Production Dashboard",
    "panels": [
      {
        "title": "API Response Times",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          }
        ]
      },
      {
        "title": "MCP Server Health",
        "targets": [
          {
            "expr": "up{job=\"mcp-servers\"}",
            "legendFormat": "{{instance}}"
          }
        ]
      }
    ]
  }
}
```

#### 3.3 Alerting Rules
```yaml
# Alert when API response time > 2s
- alert: HighAPILatency
  expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 2
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "High API latency detected"
    description: "95th percentile latency is {{ $value }}s"

# Alert when MCP server is down
- alert: MCPServerDown
  expr: up{job="mcp-servers"} == 0
  for: 1m
  labels:
    severity: critical
  annotations:
    summary: "MCP server is down"
    description: "{{ $labels.instance }} has been down for more than 1 minute"
```

### Phase 4: CI/CD Pipeline (Week 2)
**Goal:** Automated deployment with zero-downtime updates

#### 4.1 GitHub Actions Production Pipeline
```yaml
# .github/workflows/production-deployment.yml
name: Production Deployment
on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Build and Push Images
      run: |
        docker build -t scoobyjava15/sophia-ai-backend:${{ github.sha }} .
        docker push scoobyjava15/sophia-ai-backend:${{ github.sha }}
    
    - name: Deploy to Lambda Labs
      run: |
        kubectl set image deployment/sophia-ai-backend \
          sophia-ai-backend=scoobyjava15/sophia-ai-backend:${{ github.sha }}
        kubectl rollout status deployment/sophia-ai-backend
    
    - name: Run Health Checks
      run: |
        curl -f http://192.222.58.232:8000/health || exit 1
        python scripts/production_health_check.py
```

#### 4.2 Automated Testing Pipeline
```yaml
# .github/workflows/production-tests.yml
name: Production Tests
on:
  schedule:
    - cron: '*/15 * * * *'  # Every 15 minutes

jobs:
  health-check:
    runs-on: ubuntu-latest
    steps:
    - name: Test All MCP Endpoints
      run: |
        python scripts/production_endpoint_tests.py
    
    - name: Performance Tests
      run: |
        python scripts/production_performance_tests.py
    
    - name: Security Scan
      run: |
        python scripts/production_security_scan.py
```

### Phase 5: High Availability & Scaling (Week 3)
**Goal:** 99.9% uptime with automatic scaling

#### 5.1 Horizontal Pod Autoscaler
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: sophia-ai-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: sophia-ai-backend
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

#### 5.2 Load Balancer Configuration
```yaml
apiVersion: v1
kind: Service
metadata:
  name: sophia-ai-loadbalancer
spec:
  type: LoadBalancer
  selector:
    app: sophia-ai-backend
  ports:
  - port: 80
    targetPort: 8000
    protocol: TCP
  loadBalancerIP: 192.222.58.232
```

#### 5.3 Database High Availability
```yaml
# PostgreSQL with replication
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: postgres-cluster
spec:
  instances: 3
  postgresql:
    parameters:
      max_connections: "200"
      shared_buffers: "256MB"
  bootstrap:
    initdb:
      database: sophia_ai_production
      owner: sophia_ai
```

## 🔧 Production Scripts & Tools

### 1. Production Health Check Script
```python
#!/usr/bin/env python3
"""
Production Health Check Script
Comprehensive health monitoring for 24/7 operation
"""

import asyncio
import httpx
import json
from datetime import datetime
from typing import Dict, List

class ProductionHealthChecker:
    def __init__(self):
        self.base_url = "http://192.222.58.232:8000"
        self.mcp_platforms = ["linear", "asana", "notion", "hubspot", "gong", "slack", "github"]
        self.health_thresholds = {
            "response_time": 2.0,  # seconds
            "error_rate": 0.01,    # 1%
            "uptime": 0.999        # 99.9%
        }
    
    async def check_all_endpoints(self) -> Dict:
        """Check all MCP endpoints for health"""
        results = {
            "timestamp": datetime.now().isoformat(),
            "overall_health": "healthy",
            "platforms": {},
            "alerts": []
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            for platform in self.mcp_platforms:
                start_time = datetime.now()
                
                try:
                    response = await client.get(f"{self.base_url}/api/v4/mcp/{platform}/projects")
                    response_time = (datetime.now() - start_time).total_seconds()
                    
                    if response.status_code == 200:
                        data = response.json()
                        results["platforms"][platform] = {
                            "status": "healthy",
                            "response_time": response_time,
                            "data_source": data.get("source", "unknown"),
                            "project_count": len(data.get("projects", []))
                        }
                        
                        # Check response time threshold
                        if response_time > self.health_thresholds["response_time"]:
                            results["alerts"].append({
                                "level": "warning",
                                "platform": platform,
                                "message": f"High response time: {response_time:.2f}s"
                            })
                    else:
                        results["platforms"][platform] = {
                            "status": "error",
                            "response_time": response_time,
                            "error": f"HTTP {response.status_code}"
                        }
                        results["alerts"].append({
                            "level": "critical",
                            "platform": platform,
                            "message": f"HTTP error: {response.status_code}"
                        })
                        
                except Exception as e:
                    results["platforms"][platform] = {
                        "status": "error",
                        "error": str(e)
                    }
                    results["alerts"].append({
                        "level": "critical",
                        "platform": platform,
                        "message": f"Connection error: {e}"
                    })
        
        # Determine overall health
        healthy_count = sum(1 for p in results["platforms"].values() if p.get("status") == "healthy")
        total_count = len(results["platforms"])
        health_percentage = (healthy_count / total_count) * 100 if total_count > 0 else 0
        
        if health_percentage < 90:
            results["overall_health"] = "critical"
        elif health_percentage < 95:
            results["overall_health"] = "warning"
        
        return results
    
    async def send_alerts(self, results: Dict):
        """Send alerts to monitoring systems"""
        if results["alerts"]:
            # Send to Slack
            slack_webhook = "YOUR_SLACK_WEBHOOK_URL"
            
            alert_message = f"🚨 Sophia AI Health Alert\\n"
            alert_message += f"Overall Health: {results['overall_health']}\\n"
            alert_message += f"Alerts: {len(results['alerts'])}\\n\\n"
            
            for alert in results["alerts"]:
                alert_message += f"• {alert['level'].upper()}: {alert['platform']} - {alert['message']}\\n"
            
            # Send webhook (implement based on your monitoring system)
            print(f"ALERT: {alert_message}")

async def main():
    checker = ProductionHealthChecker()
    results = await checker.check_all_endpoints()
    
    print(json.dumps(results, indent=2))
    
    if results["alerts"]:
        await checker.send_alerts(results)
        exit(1)  # Exit with error code if alerts
    else:
        exit(0)  # Success

if __name__ == "__main__":
    asyncio.run(main())
```

### 2. Production Deployment Script
```bash
#!/bin/bash
# Production Deployment Script
# Automated deployment with health checks and rollback

set -e

echo "🚀 Starting Production Deployment..."

# 1. Build and push images
echo "📦 Building production images..."
docker build -t scoobyjava15/sophia-ai-backend:latest .
docker build -t scoobyjava15/sophia-ai-mcp-orchestrator:latest .

docker push scoobyjava15/sophia-ai-backend:latest
docker push scoobyjava15/sophia-ai-mcp-orchestrator:latest

# 2. Deploy to Kubernetes
echo "🚢 Deploying to Lambda Labs K8s..."
kubectl apply -f k8s/production/

# 3. Wait for rollout
echo "⏳ Waiting for deployment rollout..."
kubectl rollout status deployment/sophia-ai-backend -n sophia-ai-prod
kubectl rollout status deployment/sophia-ai-mcp-orchestrator -n sophia-ai-prod

# 4. Health check
echo "🏥 Running health checks..."
sleep 30  # Wait for pods to be ready

python scripts/production_health_check.py

if [ $? -eq 0 ]; then
    echo "✅ Deployment successful!"
    echo "🌐 Production URL: http://192.222.58.232:8000"
else
    echo "❌ Health check failed, rolling back..."
    kubectl rollout undo deployment/sophia-ai-backend -n sophia-ai-prod
    kubectl rollout undo deployment/sophia-ai-mcp-orchestrator -n sophia-ai-prod
    exit 1
fi

echo "🎉 Production deployment complete!"
```

### 3. Performance Monitoring Script
```python
#!/usr/bin/env python3
"""
Production Performance Monitoring
Continuous performance monitoring with SLA tracking
"""

import asyncio
import httpx
import time
import statistics
from datetime import datetime
from typing import List, Dict

class PerformanceMonitor:
    def __init__(self):
        self.base_url = "http://192.222.58.232:8000"
        self.sla_targets = {
            "response_time_p95": 2.0,  # 95th percentile < 2s
            "response_time_avg": 1.0,  # Average < 1s
            "error_rate": 0.01,        # < 1% errors
            "throughput": 100          # > 100 req/s
        }
    
    async def run_performance_test(self, duration_minutes: int = 5) -> Dict:
        """Run performance test for specified duration"""
        print(f"🚀 Running performance test for {duration_minutes} minutes...")
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        response_times = []
        error_count = 0
        success_count = 0
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            while time.time() < end_time:
                # Test multiple endpoints concurrently
                tasks = []
                for platform in ["linear", "asana", "notion"]:
                    task = self.test_endpoint(client, f"/api/v4/mcp/{platform}/projects")
                    tasks.append(task)
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for result in results:
                    if isinstance(result, Exception):
                        error_count += 1
                    else:
                        response_times.append(result)
                        success_count += 1
                
                # Wait before next batch
                await asyncio.sleep(0.1)
        
        # Calculate metrics
        total_requests = success_count + error_count
        duration_seconds = time.time() - start_time
        
        metrics = {
            "duration_seconds": duration_seconds,
            "total_requests": total_requests,
            "success_count": success_count,
            "error_count": error_count,
            "error_rate": error_count / total_requests if total_requests > 0 else 0,
            "throughput": total_requests / duration_seconds,
            "response_time_avg": statistics.mean(response_times) if response_times else 0,
            "response_time_p95": statistics.quantiles(response_times, n=20)[18] if len(response_times) > 20 else 0,
            "response_time_max": max(response_times) if response_times else 0,
            "response_time_min": min(response_times) if response_times else 0
        }
        
        # Check SLA compliance
        sla_violations = []
        if metrics["response_time_p95"] > self.sla_targets["response_time_p95"]:
            sla_violations.append(f"P95 response time: {metrics['response_time_p95']:.2f}s > {self.sla_targets['response_time_p95']}s")
        
        if metrics["response_time_avg"] > self.sla_targets["response_time_avg"]:
            sla_violations.append(f"Average response time: {metrics['response_time_avg']:.2f}s > {self.sla_targets['response_time_avg']}s")
        
        if metrics["error_rate"] > self.sla_targets["error_rate"]:
            sla_violations.append(f"Error rate: {metrics['error_rate']:.2%} > {self.sla_targets['error_rate']:.2%}")
        
        if metrics["throughput"] < self.sla_targets["throughput"]:
            sla_violations.append(f"Throughput: {metrics['throughput']:.1f} req/s < {self.sla_targets['throughput']} req/s")
        
        metrics["sla_violations"] = sla_violations
        metrics["sla_compliant"] = len(sla_violations) == 0
        
        return metrics
    
    async def test_endpoint(self, client: httpx.AsyncClient, endpoint: str) -> float:
        """Test single endpoint and return response time"""
        start_time = time.time()
        try:
            response = await client.get(f"{self.base_url}{endpoint}")
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                return response_time
            else:
                raise Exception(f"HTTP {response.status_code}")
        except Exception as e:
            raise e

async def main():
    monitor = PerformanceMonitor()
    metrics = await monitor.run_performance_test(duration_minutes=5)
    
    print("📊 Performance Test Results:")
    print(f"  Duration: {metrics['duration_seconds']:.1f}s")
    print(f"  Total Requests: {metrics['total_requests']}")
    print(f"  Success Rate: {(metrics['success_count'] / metrics['total_requests']):.2%}")
    print(f"  Error Rate: {metrics['error_rate']:.2%}")
    print(f"  Throughput: {metrics['throughput']:.1f} req/s")
    print(f"  Response Time (avg): {metrics['response_time_avg']:.2f}s")
    print(f"  Response Time (p95): {metrics['response_time_p95']:.2f}s")
    print(f"  Response Time (max): {metrics['response_time_max']:.2f}s")
    
    if metrics["sla_compliant"]:
        print("✅ SLA Compliant")
    else:
        print("❌ SLA Violations:")
        for violation in metrics["sla_violations"]:
            print(f"  • {violation}")
    
    # Exit with error code if SLA violations
    exit(0 if metrics["sla_compliant"] else 1)

if __name__ == "__main__":
    asyncio.run(main())
```

## 📊 Production Monitoring Dashboard

### Key Metrics to Monitor 24/7
1. **API Response Times** (Target: <2s P95)
2. **Error Rates** (Target: <1%)
3. **Throughput** (Target: >100 req/s)
4. **MCP Server Health** (Target: 100% uptime)
5. **Database Performance** (Target: <100ms queries)
6. **Memory Usage** (Target: <80%)
7. **CPU Usage** (Target: <70%)

### Alert Thresholds
- **Critical**: API down, >5% error rate, >10s response time
- **Warning**: >2s response time, >1% error rate, >80% resource usage
- **Info**: New deployments, scheduled maintenance

## 🔐 Security Hardening Checklist

### ✅ Network Security
- [ ] VPN access for administrative tasks
- [ ] Firewall rules restricting access
- [ ] TLS/SSL certificates for all endpoints
- [ ] Network segmentation between services

### ✅ Application Security
- [ ] API rate limiting (100 req/min per IP)
- [ ] Input validation on all endpoints
- [ ] SQL injection prevention
- [ ] XSS protection headers

### ✅ Infrastructure Security
- [ ] Regular security patches
- [ ] Container image scanning
- [ ] Secrets rotation (monthly)
- [ ] Audit logging enabled

## 💰 Production Cost Estimation

### Lambda Labs Infrastructure
- **Primary Server (GH200)**: $2,000/month
- **Load Balancer (A6000)**: $800/month  
- **Database (A100)**: $1,200/month
- **Monitoring (RTX6000)**: $600/month
- **Total**: ~$4,600/month

### Additional Services
- **Lambda Labs Pro**: $20/month
- **Monitoring Tools**: $100/month
- **Backup Storage**: $50/month
- **Total**: ~$4,770/month

### ROI Calculation
- **Development Time Saved**: 40 hours/month × $150/hour = $6,000/month
- **Executive Efficiency**: 25% faster decisions = $10,000/month value
- **Total ROI**: $16,000/month value for $4,770/month cost = **235% ROI**

## 🎯 Success Metrics

### Availability Targets
- **Uptime**: 99.9% (8.76 hours downtime/year)
- **Response Time**: <2s P95
- **Error Rate**: <1%
- **Recovery Time**: <5 minutes

### Business Metrics
- **Executive Dashboard Usage**: >80% daily active usage
- **Decision Speed**: 25% faster executive decisions
- **Data Freshness**: <5 minutes for all platforms
- **User Satisfaction**: >90% satisfaction score

## 📋 Deployment Checklist

### Pre-Deployment
- [ ] All API keys configured in Pulumi ESC
- [ ] Database backups verified
- [ ] Monitoring alerts configured
- [ ] Load testing completed
- [ ] Security scan passed

### Deployment
- [ ] Blue-green deployment executed
- [ ] Health checks passed
- [ ] Performance tests passed
- [ ] Rollback plan tested
- [ ] Documentation updated

### Post-Deployment
- [ ] 24-hour monitoring period
- [ ] User acceptance testing
- [ ] Performance baseline established
- [ ] Incident response plan activated
- [ ] Team training completed

---

**This comprehensive plan provides everything needed for 24/7 production operation of the Sophia AI MCP platform with enterprise-grade reliability, security, and performance.** 