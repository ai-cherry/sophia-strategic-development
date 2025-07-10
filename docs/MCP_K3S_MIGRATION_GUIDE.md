# MCP Ecosystem K3s Migration Guide

**Date:** July 10, 2025  
**Scope:** Complete migration of MCP servers from Docker Swarm to K3s  
**Duration:** 16 weeks (4 phases)

## 🎯 Migration Overview

This guide provides step-by-step instructions for migrating the entire Sophia AI MCP ecosystem from Docker Swarm to K3s, based on the strategic decision to use K3s as our Kubernetes platform.

### Why K3s?
- **Lower overhead:** ~500MB RAM vs 2GB for full K8s
- **GPU support:** Native NVIDIA support for Lambda Labs instances
- **100% K8s compatible:** All learning transfers to full K8s if needed
- **Faster deployment:** 4-6 weeks vs 12-16 weeks
- **Built-in features:** Traefik, metrics server, local storage

## 📊 Current State

### MCP Servers Status
- **Total Servers:** 16 planned, 9 implemented (56.25%)
- **Migration Status:** 9 servers ready for K3s deployment
- **Deployment Method:** Docker Swarm across 5 Lambda Labs instances

### Lambda Labs Infrastructure
| Instance | Role | IP | GPU | Current Use |
|----------|------|----|----|-------------|
| sophia-production | Core Services | 104.171.202.103 | RTX6000 | API, Dashboard |
| sophia-ai-core | AI Compute | 192.222.58.232 | GH200 | AI Memory, ML |
| sophia-mcp-orchestrator | MCP Hub | 104.171.202.117 | A6000 | MCP Servers |
| sophia-data-pipeline | Data Processing | 104.171.202.134 | A100 | Snowflake |
| sophia-development | Dev/Test | 155.248.194.183 | A10 | Testing |

## 🚀 Phase 1: K3s Foundation (Weeks 1-4)

### Week 1: Development Instance Setup

1. **Install K3s on Development Instance**
   ```bash
   # SSH to development instance
   ssh -i ~/.ssh/sophia2025.pem ubuntu@155.248.194.183
   
   # Run installation script
   curl -O https://raw.githubusercontent.com/ai-cherry/sophia-main/main/scripts/install_k3s_lambda_labs.sh
   chmod +x install_k3s_lambda_labs.sh
   ./install_k3s_lambda_labs.sh master
   
   # Save the node token (displayed after installation)
   K3S_TOKEN=<save-this-token>
   ```

2. **Verify K3s Installation**
   ```bash
   # Check nodes
   sudo k3s kubectl get nodes
   
   # Check GPU support
   sudo k3s kubectl describe nodes | grep nvidia
   
   # Check namespaces
   sudo k3s kubectl get namespaces
   ```

3. **Configure kubectl Access**
   ```bash
   # Copy kubeconfig to local machine
   scp -i ~/.ssh/sophia2025.pem ubuntu@155.248.194.183:/etc/rancher/k3s/k3s.yaml ~/.kube/k3s-dev-config
   
   # Edit the config to use external IP
   sed -i 's/127.0.0.1/155.248.194.183/g' ~/.kube/k3s-dev-config
   
   # Use the config
   export KUBECONFIG=~/.kube/k3s-dev-config
   kubectl get nodes
   ```

### Week 2: Deploy First MCP Servers

1. **Convert Docker Compose to K3s Manifests**
   ```bash
   # Convert MCP orchestrator compose file
   python scripts/convert_compose_to_k3s.py \
     deployment/docker-compose-mcp-orchestrator.yml \
     -o k3s-manifests/
   ```

2. **Deploy Core MCP Servers**
   ```bash
   # Apply namespace
   kubectl apply -f - <<EOF
   apiVersion: v1
   kind: Namespace
   metadata:
     name: sophia-mcp
   EOF
   
   # Deploy AI Memory (non-GPU test)
   kubectl apply -f k3s-manifests/mcp-ai-memory.yaml
   
   # Deploy Snowflake Unified
   kubectl apply -f k3s-manifests/mcp-snowflake-unified.yaml
   
   # Check deployments
   kubectl get pods -n sophia-mcp
   kubectl logs -n sophia-mcp -l app=mcp-ai-memory
   ```

3. **Test Inter-MCP Communication**
   ```bash
   # Port forward to test
   kubectl port-forward -n sophia-mcp svc/mcp-ai-memory 9000:9000 &
   kubectl port-forward -n sophia-mcp svc/mcp-snowflake-unified 9001:9001 &
   
   # Test health endpoints
   curl http://localhost:9000/health
   curl http://localhost:9001/health
   ```

### Week 3: Monitoring and Observability

1. **Deploy Prometheus and Grafana**
   ```bash
   # Add Prometheus Helm repo
   helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
   helm repo update
   
   # Install kube-prometheus-stack
   helm install prometheus prometheus-community/kube-prometheus-stack \
     --namespace monitoring \
     --create-namespace \
     --set prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues=false
   ```

2. **Configure MCP Metrics**
   ```bash
   # Create ServiceMonitor for MCP servers
   kubectl apply -f - <<EOF
   apiVersion: monitoring.coreos.com/v1
   kind: ServiceMonitor
   metadata:
     name: mcp-servers
     namespace: sophia-mcp
   spec:
     selector:
       matchLabels:
         tier: mcp
     endpoints:
     - port: mcp
       path: /metrics
   EOF
   ```

### Week 4: Production Preparation

1. **Document Lessons Learned**
   - GPU scheduling issues and solutions
   - Network policy requirements
   - Performance benchmarks
   - Security considerations

2. **Create Deployment Automation**
   ```bash
   # Create deployment script
   cat > scripts/deploy_mcp_to_k3s.sh <<'EOF'
   #!/bin/bash
   # Deploy MCP servers to K3s
   
   NAMESPACE="sophia-mcp"
   MANIFESTS_DIR="k3s-manifests"
   
   # Apply all MCP manifests
   kubectl apply -f $MANIFESTS_DIR/
   
   # Wait for deployments
   kubectl wait --for=condition=available --timeout=300s \
     deployment -n $NAMESPACE -l tier=mcp
   
   # Check status
   kubectl get pods -n $NAMESPACE
   EOF
   
   chmod +x scripts/deploy_mcp_to_k3s.sh
   ```

## 🚀 Phase 2: Multi-Node K3s Cluster (Weeks 5-8)

### Week 5: Production Master Setup

1. **Install K3s Master on Production Instance**
   ```bash
   # SSH to production instance
   ssh -i ~/.ssh/sophia2025.pem ubuntu@104.171.202.103
   
   # Install as master
   ./install_k3s_lambda_labs.sh master
   
   # Save token and IP
   K3S_TOKEN=<token>
   MASTER_IP=104.171.202.103
   ```

2. **Configure High Availability**
   ```bash
   # Install external datastore (optional for HA)
   # For now, use embedded SQLite for simplicity
   ```

### Week 6: Add Worker Nodes

1. **Join AI Core Instance**
   ```bash
   # SSH to AI core instance
   ssh -i ~/.ssh/sophia2025.pem ubuntu@192.222.58.232
   
   # Install as worker
   K3S_TOKEN=<token-from-master> ./install_k3s_lambda_labs.sh worker 104.171.202.103
   ```

2. **Join MCP Orchestrator Instance**
   ```bash
   # Repeat for other instances
   ssh -i ~/.ssh/sophia2025.pem ubuntu@104.171.202.117
   K3S_TOKEN=<token> ./install_k3s_lambda_labs.sh worker 104.171.202.103
   ```

3. **Verify Cluster**
   ```bash
   # From master node
   kubectl get nodes
   kubectl label nodes <node-name> instance-role=ai-core
   kubectl label nodes <node-name> instance-role=mcp-hub
   ```

### Week 7: Migrate PRIMARY Tier Services

1. **Deploy with Node Affinity**
   ```yaml
   # Update manifests with node affinity
   spec:
     affinity:
       nodeAffinity:
         requiredDuringSchedulingIgnoredDuringExecution:
           nodeSelectorTerms:
           - matchExpressions:
             - key: instance-role
               operator: In
               values:
               - ai-core  # For GPU workloads
   ```

2. **Migrate Services**
   ```bash
   # PRIMARY tier services
   kubectl apply -f k3s-manifests/primary/
   
   # Verify GPU allocation
   kubectl describe pod -n sophia-mcp mcp-ai-memory-<pod-id>
   ```

### Week 8: Performance Testing

1. **Load Testing**
   ```bash
   # Deploy load testing pod
   kubectl run -it --rm load-test --image=curlimages/curl -- sh
   
   # Test MCP endpoints
   while true; do
     curl http://mcp-ai-memory.sophia-mcp:9000/health
     sleep 0.1
   done
   ```

2. **Collect Metrics**
   - Response times
   - Resource utilization
   - GPU usage
   - Network latency

## 🚀 Phase 3: Production Migration (Weeks 9-12)

### Week 9: Data Migration Strategy

1. **Backup Current Data**
   ```bash
   # Backup Redis data
   docker exec redis redis-cli BGSAVE
   
   # Backup PostgreSQL
   docker exec postgres pg_dump -U sophia sophia_ai > backup.sql
   ```

2. **Create Persistent Volumes**
   ```yaml
   # PVC for stateful services
   apiVersion: v1
   kind: PersistentVolumeClaim
   metadata:
     name: postgres-pvc
     namespace: sophia-ai
   spec:
     accessModes:
       - ReadWriteOnce
     resources:
       requests:
         storage: 100Gi
   ```

### Week 10: Migrate SECONDARY Tier

1. **Deploy SECONDARY Services**
   ```bash
   kubectl apply -f k3s-manifests/secondary/
   ```

2. **Update Service Discovery**
   - Update application configs to use K3s DNS
   - Test inter-service communication

### Week 11: Migrate Core Platform

1. **Deploy Core Services**
   ```bash
   # Deploy backend API
   kubectl apply -f k3s-manifests/sophia-backend.yaml
   
   # Deploy unified chat
   kubectl apply -f k3s-manifests/sophia-unified-chat.yaml
   
   # Deploy dashboard
   kubectl apply -f k3s-manifests/sophia-dashboard.yaml
   ```

2. **Configure Ingress**
   ```yaml
   apiVersion: networking.k8s.io/v1
   kind: Ingress
   metadata:
     name: sophia-ingress
     namespace: sophia-ai
   spec:
     rules:
     - host: app.sophia-ai.com
       http:
         paths:
         - path: /api
           pathType: Prefix
           backend:
             service:
               name: sophia-backend
               port:
                 number: 8000
   ```

### Week 12: Cutover and Validation

1. **Blue-Green Deployment**
   - Keep Docker Swarm running
   - Route traffic to K3s gradually
   - Monitor for issues

2. **Validation Checklist**
   - [ ] All services healthy
   - [ ] GPU allocation working
   - [ ] Inter-service communication
   - [ ] External access via ingress
   - [ ] Monitoring and alerting
   - [ ] Backup and restore tested

## 🚀 Phase 4: Optimization (Weeks 13-16)

### Week 13: Auto-scaling Configuration

1. **Configure HPA**
   ```bash
   # Already configured in manifests
   kubectl get hpa -n sophia-mcp
   ```

2. **Test Scaling**
   ```bash
   # Generate load to trigger scaling
   kubectl run -it --rm loadgen --image=busybox -- sh -c \
     "while true; do wget -q -O- http://mcp-ai-memory.sophia-mcp:9000/health; done"
   ```

### Week 14: Security Hardening

1. **Network Policies**
   ```yaml
   apiVersion: networking.k8s.io/v1
   kind: NetworkPolicy
   metadata:
     name: mcp-isolation
     namespace: sophia-mcp
   spec:
     podSelector:
       matchLabels:
         tier: mcp
     policyTypes:
     - Ingress
     - Egress
   ```

2. **RBAC Configuration**
   ```bash
   # Create service accounts
   kubectl create serviceaccount mcp-operator -n sophia-mcp
   ```

### Week 15: Disaster Recovery

1. **Backup Strategy**
   ```bash
   # Install Velero for backups
   helm install velero vmware-tanzu/velero \
     --namespace velero \
     --create-namespace
   ```

2. **Test Recovery**
   - Simulate node failure
   - Test data restoration
   - Validate service recovery

### Week 16: Documentation and Training

1. **Create Runbooks**
   - Deployment procedures
   - Troubleshooting guides
   - Scaling procedures
   - Disaster recovery

2. **Team Training**
   - K3s basics
   - kubectl commands
   - Monitoring tools
   - Incident response

## 📋 Post-Migration Checklist

### Technical Validation
- [ ] All 16 MCP servers deployed and healthy
- [ ] GPU scheduling working correctly
- [ ] Service discovery functional
- [ ] Monitoring and alerting configured
- [ ] Backup and restore tested
- [ ] Auto-scaling validated
- [ ] Security policies applied

### Performance Validation
- [ ] Response times ≤ Docker Swarm
- [ ] Resource utilization optimized
- [ ] GPU utilization > 60%
- [ ] Network latency < 10ms

### Operational Validation
- [ ] Runbooks created
- [ ] Team trained
- [ ] Incident response tested
- [ ] Deployment automation working

## 🎯 Success Metrics

### Technical Metrics
- **Uptime:** 99.9% availability
- **Deployment Time:** < 10 minutes
- **Recovery Time:** < 5 minutes
- **Resource Efficiency:** 25% improvement

### Business Metrics
- **Cost Savings:** 15% infrastructure optimization
- **Developer Productivity:** 25% improvement
- **Time to Market:** 30% faster deployments
- **Operational Overhead:** 50% reduction

## 🚨 Rollback Plan

If critical issues arise:

1. **Immediate Rollback**
   ```bash
   # Route traffic back to Docker Swarm
   # Update DNS/Load balancer
   ```

2. **Data Recovery**
   ```bash
   # Restore from backups
   # Sync any data changes
   ```

3. **Post-Mortem**
   - Document issues
   - Plan remediation
   - Schedule retry

## 📚 Resources

### Documentation
- [K3s Official Docs](https://docs.k3s.io/)
- [Kubernetes MCP Patterns](./MCP_KUBERNETES_DEPLOYMENT_PATTERNS.md)
- [GPU Scheduling Guide](https://kubernetes.io/docs/tasks/manage-gpus/scheduling-gpus/)

### Tools
- `install_k3s_lambda_labs.sh` - K3s installation script
- `convert_compose_to_k3s.py` - Compose to K3s converter
- `deploy_mcp_to_k3s.sh` - Deployment automation

### Support
- K3s GitHub Issues
- Sophia AI Slack Channel
- Lambda Labs Support

---

**Remember:** K3s is just Kubernetes. Everything you learn applies to full K8s if we need to migrate later. 