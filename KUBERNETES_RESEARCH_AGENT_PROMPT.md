# 🔍 Deep Web Research Agent Prompt: Kubernetes Lambda Labs Deployment

## 🎯 **RESEARCH MISSION**

You are a specialized Kubernetes deployment research agent. Your mission is to find comprehensive solutions for deploying a production-ready AI platform on Lambda Labs cloud infrastructure using Kubernetes/K3s.

## 📋 **SPECIFIC PROBLEMS TO SOLVE**

### **Problem 1: Lambda Labs K3s Cluster Setup**
**Search Query**: `"Lambda Labs" kubernetes k3s cluster setup production deployment GPU instances`

**Research Focus**:
- How to properly configure K3s cluster on Lambda Labs GPU instances
- Best practices for multi-node K3s setup with Lambda Labs
- Lambda Labs specific networking configurations for Kubernetes
- GPU node scheduling and resource allocation in K3s
- Lambda Labs firewall and security group configurations for K8s

**Key Questions**:
1. What are the exact steps to install K3s on Lambda Labs instances?
2. How to configure K3s master/worker nodes across multiple Lambda Labs instances?
3. What networking plugins work best with Lambda Labs infrastructure?
4. How to handle Lambda Labs instance IP changes in K3s cluster?
5. What are the Lambda Labs specific security considerations for K3s?

### **Problem 2: Kubernetes Cluster Connectivity**
**Search Query**: `kubernetes cluster connectivity issues "cannot connect" kubeconfig remote cluster`

**Research Focus**:
- Common kubeconfig connectivity issues and solutions
- Remote Kubernetes cluster access from local machines
- Troubleshooting "cannot connect to cluster" errors
- Network connectivity issues between local kubectl and remote clusters
- Firewall and port configuration for Kubernetes API access

**Key Questions**:
1. What ports need to be open for kubectl to connect to remote K3s cluster?
2. How to troubleshoot kubeconfig connection failures?
3. What are common networking issues with remote Kubernetes clusters?
4. How to validate Kubernetes cluster connectivity step-by-step?
5. What tools can diagnose Kubernetes networking problems?

### **Problem 3: Docker Registry Integration with K3s**
**Search Query**: `k3s docker hub private registry integration deployment issues`

**Research Focus**:
- Configuring K3s to pull images from Docker Hub private registries
- Image pull secrets and authentication in K3s
- Docker registry connectivity issues in Kubernetes
- Best practices for container image management in K3s
- Troubleshooting image pull failures in Kubernetes

**Key Questions**:
1. How to configure K3s to authenticate with Docker Hub private registry?
2. What are the proper image pull secrets configurations?
3. How to troubleshoot "image not found" errors in K3s?
4. What are best practices for container registry integration?
5. How to handle Docker Hub rate limiting in K3s deployments?

### **Problem 4: GPU Workload Scheduling in K3s**
**Search Query**: `k3s GPU scheduling nvidia device plugin lambda labs kubernetes`

**Research Focus**:
- NVIDIA GPU device plugin installation and configuration in K3s
- GPU resource allocation and scheduling in Kubernetes
- Lambda Labs GPU-specific Kubernetes configurations
- GPU workload optimization in K3s clusters
- Multi-GPU node management in Kubernetes

**Key Questions**:
1. How to install and configure NVIDIA device plugin in K3s?
2. What are the proper GPU resource requests and limits?
3. How to schedule AI workloads on specific GPU types?
4. What are Lambda Labs GPU-specific Kubernetes considerations?
5. How to monitor GPU utilization in K3s clusters?

### **Problem 5: Production Deployment Patterns**
**Search Query**: `kubernetes production deployment patterns CI/CD GitOps best practices`

**Research Focus**:
- Production-ready Kubernetes deployment architectures
- CI/CD pipeline integration with Kubernetes
- GitOps workflows for Kubernetes deployments
- Monitoring and observability in production K8s
- Security best practices for production Kubernetes

**Key Questions**:
1. What are proven production deployment patterns for Kubernetes?
2. How to implement robust CI/CD pipelines for K8s deployments?
3. What monitoring and alerting should be configured?
4. How to handle secrets management in production K8s?
5. What are the security hardening steps for production clusters?

## 🎯 **RESEARCH METHODOLOGY**

### **Phase 1: Problem-Specific Research (30 minutes)**
For each problem above:
1. **Search multiple sources**: Official docs, Stack Overflow, GitHub issues, Reddit, Medium articles
2. **Look for recent solutions**: Focus on 2023-2025 content for latest best practices
3. **Find Lambda Labs specific**: Search for Lambda Labs + Kubernetes combinations
4. **Collect code examples**: Working configurations, scripts, and manifests
5. **Identify common pitfalls**: What typically goes wrong and how to avoid it

### **Phase 2: Solution Synthesis (15 minutes)**
1. **Prioritize solutions**: Rank by relevance to our specific setup
2. **Create action plan**: Step-by-step implementation guide
3. **Prepare alternatives**: Backup solutions if primary approach fails
4. **Estimate effort**: Time and complexity for each solution
5. **Risk assessment**: Potential issues and mitigation strategies

### **Phase 3: Implementation Guidance (15 minutes)**
1. **Create deployment scripts**: Based on research findings
2. **Prepare troubleshooting guide**: Common issues and solutions
3. **Document configuration**: All necessary settings and parameters
4. **Test procedures**: How to validate each step
5. **Rollback plans**: How to revert if deployment fails

## 🔍 **SPECIFIC SEARCH STRINGS**

### **Lambda Labs Specific**
```
"Lambda Labs" kubernetes setup guide
"Lambda Labs" k3s cluster configuration
"Lambda Labs" GPU kubernetes deployment
"Lambda Labs" cloud kubernetes networking
"Lambda Labs" firewall kubernetes ports
```

### **K3s Deployment Issues**
```
k3s cluster setup multi-node production
k3s connectivity issues troubleshooting
k3s docker registry authentication
k3s GPU device plugin installation
k3s production deployment best practices
```

### **Kubernetes Connectivity**
```
kubernetes "cannot connect to cluster" fix
kubeconfig remote cluster connection issues
kubernetes API server connectivity problems
kubectl connection timeout solutions
kubernetes networking troubleshooting guide
```

### **Docker Registry Integration**
```
kubernetes docker hub private registry setup
k3s image pull secrets configuration
kubernetes "image not found" troubleshooting
docker registry authentication kubernetes
container registry integration k3s
```

### **AI/ML Kubernetes Deployments**
```
kubernetes AI workload deployment patterns
kubernetes GPU scheduling best practices
kubernetes machine learning production deployment
kubernetes AI platform architecture
kubernetes ML model serving patterns
```

## 📊 **EXPECTED DELIVERABLES**

### **1. Comprehensive Solution Guide**
- Step-by-step Lambda Labs K3s setup instructions
- Complete kubeconfig and connectivity configuration
- Docker registry integration procedures
- GPU workload scheduling configuration
- Production deployment checklist

### **2. Troubleshooting Playbook**
- Common error messages and solutions
- Diagnostic commands and tools
- Network connectivity testing procedures
- Performance optimization techniques
- Security hardening steps

### **3. Implementation Scripts**
- Automated K3s cluster setup script
- Kubernetes manifest templates
- Docker registry configuration scripts
- GPU device plugin installation script
- Monitoring and alerting setup

### **4. Alternative Solutions**
- Backup deployment strategies
- Simpler alternatives to complex setups
- Hybrid approaches (Docker + K8s)
- Migration paths from current setup
- Cost optimization strategies

## 🚨 **CRITICAL SUCCESS FACTORS**

### **Must-Have Outcomes**
1. **Working K3s cluster** on Lambda Labs infrastructure
2. **Reliable kubectl connectivity** from local machine
3. **Successful image pulls** from Docker Hub registry
4. **GPU workload scheduling** working correctly
5. **Production-ready deployment** with monitoring

### **Success Metrics**
- Cluster nodes all in "Ready" state
- Pods successfully scheduled and running
- External connectivity to services working
- GPU resources properly allocated
- Monitoring and alerting functional

## 🎯 **RESEARCH PRIORITY ORDER**

1. **HIGH PRIORITY**: Lambda Labs K3s cluster setup (Problem 1)
2. **HIGH PRIORITY**: Kubernetes connectivity issues (Problem 2)
3. **MEDIUM PRIORITY**: Docker registry integration (Problem 3)
4. **MEDIUM PRIORITY**: GPU workload scheduling (Problem 4)
5. **LOW PRIORITY**: Production deployment patterns (Problem 5)

## 📞 **FALLBACK RESEARCH**

If primary solutions don't work, research these alternatives:
- **Docker Swarm on Lambda Labs** as K8s alternative
- **Nomad orchestration** for simpler deployment
- **Direct Docker deployment** with service discovery
- **Hybrid approaches** combining multiple orchestrators
- **Managed Kubernetes services** compatible with Lambda Labs

---

**RESEARCH AGENT INSTRUCTIONS**: Use this prompt to conduct deep web research on our Kubernetes deployment challenges. Focus on Lambda Labs specific solutions and provide actionable implementation guidance with working code examples. 