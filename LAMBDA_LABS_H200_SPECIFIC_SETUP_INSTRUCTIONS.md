# 🎯 Lambda Labs H200 GPU Setup - EXACT INSTRUCTIONS

**Purpose**: Step-by-step instructions for setting up the H200 GPU infrastructure in Lambda Labs for Sophia AI

---

## 📋 **STEP 1: Lambda Labs Account Setup**

### **1.1 Create Lambda Labs Account**
1. Go to: https://cloud.lambdalabs.com/
2. Click "Sign Up"
3. Use email: `admin@payready.com` (or company email)
4. Complete verification
5. Add billing information (credit card required)

### **1.2 Generate API Credentials**
1. Log into Lambda Labs dashboard
2. Navigate to: **Account → API Keys**
3. Click "Create API Key"
4. Name: `sophia-ai-h200-production`
5. Permissions: Select ALL checkboxes:
   - ✅ Instance Management
   - ✅ Cluster Operations
   - ✅ File System Access
   - ✅ SSH Key Management
   - ✅ Billing Read Access
6. Copy the API key: `YOUR_LAMBDA_LABS_API_KEY`
7. **SAVE THIS KEY** - it won't be shown again

### **1.3 Upload SSH Key**
1. Generate SSH key locally:
   ```bash
   ssh-keygen -t ed25519 -C "sophia-ai-h200@payready.com" -f ~/.ssh/sophia_h200_key -N ""
   ```
2. Go to: **Account → SSH Keys**
3. Click "Add SSH Key"
4. Name: `sophia-ai-h200-key`
5. Paste contents of: `~/.ssh/sophia_h200_key.pub`
6. Click "Add Key"

---

## 🖥️ **STEP 2: Request H200 GPU Access**

### **2.1 Check H200 Availability**
1. Go to: **Dashboard → Instance Types**
2. Look for: `gpu_1x_h200` or `gpu_8x_h200`
3. If not visible, contact Lambda Labs support:
   - Subject: "H200 GPU Access Request for Enterprise Account"
   - Message: "We need access to H200 GPUs for our AI platform deployment"

### **2.2 Request Quota Increase**
1. Go to: **Account → Quotas**
2. Current limits may show:
   - GPU instances: 1-2 (default)
3. Click "Request Increase"
4. Fill out:
   - Resource Type: `GPU Instances`
   - Requested Quota: `16` (for auto-scaling)
   - Justification: "Enterprise AI platform with auto-scaling requirements"

---

## 🚀 **STEP 3: Launch H200 GPU Instances**

### **3.1 Instance Configuration**

**EXACT INSTANCE SPECIFICATIONS:**

```yaml
Instance Type: gpu_1x_h200
GPU: NVIDIA H200 (141GB HBM3e)
vCPUs: 24
RAM: 128GB
Storage: 2TB NVMe SSD
Network: 25 Gbps
Region: us-west-1 (or your preferred region)
```

### **3.2 Launch 3 Initial Nodes**

**Node 1 - Master Node:**
1. Go to: **Dashboard → Launch Instance**
2. Configuration:
   ```
   Name: sophia-ai-h200-master-01
   Instance Type: gpu_1x_h200
   Region: us-west-1
   SSH Key: sophia-ai-h200-key
   File System: Create New
   File System Name: sophia-ai-shared-fs
   ```
3. Click "Launch Instance"
4. Note the IP address: `MASTER_IP`

**Node 2 - Worker Node:**
1. Launch another instance:
   ```
   Name: sophia-ai-h200-worker-01
   Instance Type: gpu_1x_h200
   Region: us-west-1 (SAME AS MASTER)
   SSH Key: sophia-ai-h200-key
   File System: Use Existing → sophia-ai-shared-fs
   ```
2. Note the IP: `WORKER1_IP`

**Node 3 - Worker Node:**
1. Launch third instance:
   ```
   Name: sophia-ai-h200-worker-02
   Instance Type: gpu_1x_h200
   Region: us-west-1 (SAME AS MASTER)
   SSH Key: sophia-ai-h200-key
   File System: Use Existing → sophia-ai-shared-fs
   ```
2. Note the IP: `WORKER2_IP`

---

## 🔧 **STEP 4: Network Configuration**

### **4.1 Security Group Setup**
Lambda Labs instances come with default security groups, but verify:

1. Go to instance details for each node
2. Ensure these ports are open:
   ```
   SSH: 22 (for management)
   Kubernetes API: 6443
   ETCD: 2379-2380
   Kubelet: 10250
   NodePort Services: 30000-32767
   Application: 8000-9000
   Monitoring: 3000, 9090
   ```

### **4.2 Inter-node Communication**
1. SSH into master node:
   ```bash
   ssh -i ~/.ssh/sophia_h200_key ubuntu@MASTER_IP
   ```
2. Test connectivity to workers:
   ```bash
   ping WORKER1_IP
   ping WORKER2_IP
   ```

---

## 📊 **STEP 5: Storage Configuration**

### **5.1 Shared File System**
The shared file system (`sophia-ai-shared-fs`) should be:
- **Size**: 10TB minimum
- **Type**: High-performance NFS
- **Mount Point**: `/mnt/shared`

### **5.2 GPU Memory Allocation**
Configure GPU memory pools (141GB total):
```
Active Models Pool: 60GB
Inference Cache: 40GB
Vector Cache: 30GB
Buffer: 11GB
```

---

## 🌐 **STEP 6: API Integration Setup**

### **6.1 Create API Gateway**
1. In Lambda Labs dashboard, go to: **API Gateway**
2. Create new gateway:
   ```
   Name: sophia-ai-h200-gateway
   Type: REST API
   Authentication: API Key
   ```
3. Add endpoints:
   ```
   POST /gpu-inference
   GET /gpu-status
   POST /memory-management
   GET /cluster-health
   ```

### **6.2 Configure Webhooks**
1. Go to: **Account → Webhooks**
2. Add webhook for auto-scaling:
   ```
   URL: https://your-domain.com/lambda-labs-webhook
   Events:
   - instance.created
   - instance.terminated
   - instance.status_changed
   ```

---

## 🔐 **STEP 7: Environment Variables & Secrets**

### **7.1 Required Environment Variables**
Set these in your GitHub/Pulumi:

```bash
# Lambda Labs Configuration
LAMBDA_LABS_API_KEY="your-api-key-from-step-1.2"
LAMBDA_LABS_SSH_KEY_NAME="sophia-ai-h200-key"
LAMBDA_LABS_SSH_PRIVATE_KEY="$(cat ~/.ssh/sophia_h200_key)"
LAMBDA_LABS_REGION="us-west-1"
LAMBDA_LABS_INSTANCE_TYPE="gpu_1x_h200"
LAMBDA_LABS_CLUSTER_SIZE="3"
LAMBDA_LABS_MAX_CLUSTER_SIZE="16"

# Instance IPs (after launch)
LAMBDA_LABS_MASTER_IP="MASTER_IP"
LAMBDA_LABS_WORKER1_IP="WORKER1_IP"
LAMBDA_LABS_WORKER2_IP="WORKER2_IP"

# Shared Storage
LAMBDA_LABS_SHARED_FS_ID="sophia-ai-shared-fs"
LAMBDA_LABS_SHARED_FS_MOUNT="/mnt/shared"
```

### **7.2 Add to GitHub Organization Secrets**
1. Go to: https://github.com/organizations/ai-cherry/settings/secrets/actions
2. Add each secret above with exact names
3. These will auto-sync to Pulumi ESC

---

## 🎮 **STEP 8: GPU Configuration**

### **8.1 CUDA & Driver Setup**
On each instance, verify/install:

```bash
# Check current CUDA version
nvidia-smi

# Should show:
# CUDA Version: 12.3
# Driver Version: 545.23.08
# GPU: NVIDIA H200

# If not, update:
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.1-1_all.deb
sudo dpkg -i cuda-keyring_1.1-1_all.deb
sudo apt-get update
sudo apt-get -y install cuda-12-3
```

### **8.2 GPU Memory Configuration**
```bash
# Set GPU memory allocation
sudo nvidia-smi -pm 1  # Enable persistence mode
sudo nvidia-smi -ac 2619,1980  # Set application clocks for H200

# Create memory pool config
cat > /etc/gpu-memory-pools.conf << EOF
ACTIVE_MODELS_POOL=60GB
INFERENCE_CACHE_POOL=40GB
VECTOR_CACHE_POOL=30GB
BUFFER_POOL=11GB
EOF
```

---

## 📈 **STEP 9: Auto-Scaling Configuration**

### **9.1 Lambda Labs Auto-Scaling API**
Configure auto-scaling rules via API:

```python
import requests

headers = {"Authorization": f"Bearer {LAMBDA_LABS_API_KEY}"}

# Create auto-scaling group
scaling_config = {
    "name": "sophia-ai-h200-asg",
    "min_instances": 3,
    "max_instances": 16,
    "target_gpu_utilization": 70,
    "target_memory_utilization": 80,
    "scale_up_cooldown": 300,  # 5 minutes
    "scale_down_cooldown": 600, # 10 minutes
    "instance_template": {
        "instance_type": "gpu_1x_h200",
        "ssh_key_name": "sophia-ai-h200-key",
        "file_system_name": "sophia-ai-shared-fs",
        "user_data": "#!/bin/bash\n# Join Kubernetes cluster script"
    }
}

response = requests.post(
    "https://cloud.lambdalabs.com/api/v1/auto-scaling-groups",
    headers=headers,
    json=scaling_config
)
```

---

## 🔍 **STEP 10: Monitoring Setup**

### **10.1 Lambda Labs Monitoring**
1. Go to: **Dashboard → Monitoring**
2. Create new dashboard: `sophia-ai-h200-monitoring`
3. Add widgets:
   - GPU Utilization (per instance)
   - GPU Memory Usage
   - GPU Temperature
   - Network Throughput
   - Instance Health

### **10.2 Alert Configuration**
1. Go to: **Monitoring → Alerts**
2. Create alerts:
   ```
   GPU Memory > 90%: Warning
   GPU Temperature > 85°C: Critical
   Instance Down: Critical
   Auto-scaling Triggered: Info
   ```

---

## ✅ **STEP 11: Validation Checklist**

Before proceeding with Kubernetes setup, verify:

- [ ] 3 H200 instances launched and running
- [ ] All instances can communicate with each other
- [ ] SSH access works to all instances
- [ ] GPU drivers show CUDA 12.3
- [ ] Shared file system mounted on all nodes
- [ ] API key and credentials stored in GitHub secrets
- [ ] Auto-scaling group configured
- [ ] Monitoring dashboard created

---

## 🚨 **IMPORTANT NOTES**

1. **Billing**: H200 instances cost $2.49/hour each ($5,976/month for 3 instances)
2. **Availability**: H200s may have limited availability - have A100 as backup
3. **Region**: All instances MUST be in same region for cluster
4. **Storage**: Shared file system is critical for model caching
5. **Scaling**: Start with 3, scale to 16 as needed

---

## 🆘 **Lambda Labs Support**

If you encounter issues:
- **Email**: support@lambdalabs.com
- **Chat**: Available in dashboard
- **Phone**: Enterprise support (if available)
- **Reference**: Mention "H200 GPU Cluster for Sophia AI"

---

**Status**: Ready for Kubernetes installation once all instances are running
