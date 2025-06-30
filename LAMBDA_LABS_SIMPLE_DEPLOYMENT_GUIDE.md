# 🚀 **HOW TO DEPLOY SOPHIA AI TO LAMBDA LABS (Simple Guide)**
## Step-by-Step Instructions for Non-Technical Users

---

## 📋 **WHAT YOU NEED BEFORE STARTING**

1. **Lambda Labs Account** - Sign up at https://lambdalabs.com/
2. **GPU Instance Running** - Rent a GPU server (RTX 4090 recommended)
3. **SSH Access** - Connect to your Lambda Labs server
4. **This Codebase** - The Sophia AI code we just prepared

---

## 🎯 **STEP 1: GET ACCESS TO YOUR LAMBDA LABS SERVER**

### **Option A: Using Lambda Labs Web Interface**
1. Go to https://cloud.lambdalabs.com/
2. Click "Launch Instance"
3. Choose **RTX 4090** GPU type
4. Select **Ubuntu 22.04** operating system
5. Click "Launch"
6. Wait 2-3 minutes for server to start
7. Copy the SSH command they give you (looks like: `ssh ubuntu@XXX.XXX.XXX.XXX`)

### **Option B: Using Terminal/Command Line**
```bash
# They'll give you a command like this:
ssh ubuntu@your-server-ip-address
```

---

## 🛠️ **STEP 2: PREPARE YOUR LAMBDA LABS SERVER**

Once you're connected to your server, run these commands **one by one**:

### **Install Kubernetes (the container system)**
```bash
# Update the server
sudo apt update && sudo apt upgrade -y

# Install Docker (for containers)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Kubernetes
curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
echo "deb https://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee /etc/apt/sources.list.d/kubernetes.list
sudo apt update
sudo apt install -y kubelet kubeadm kubectl
```

### **Install Helm (the deployment tool)**
```bash
# Install Helm
curl https://get.helm.sh/helm-v3.12.0-linux-amd64.tar.gz -o helm.tar.gz
tar -zxvf helm.tar.gz
sudo mv linux-amd64/helm /usr/local/bin/helm
```

### **Setup GPU Support**
```bash
# Install NVIDIA drivers (for GPU)
sudo apt install -y nvidia-driver-535
sudo reboot  # Server will restart - wait 2 minutes then reconnect

# After reboot, install NVIDIA container toolkit
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt update && sudo apt install -y nvidia-container-toolkit
sudo systemctl restart docker
```

---

## 📦 **STEP 3: GET THE SOPHIA AI CODE**

```bash
# Download the code
git clone https://github.com/ai-cherry/sophia-main.git
cd sophia-main

# Make the deployment script executable
chmod +x scripts/deploy_lambda_labs_kubernetes.sh
```

---

## 🚀 **STEP 4: DEPLOY SOPHIA AI (THE EASY WAY)**

### **One-Command Deployment:**
```bash
# This does everything automatically
./scripts/deploy_lambda_labs_kubernetes.sh
```

**What this script does for you:**
- Sets up GPU resources
- Installs all the AI services
- Configures everything for Lambda Labs
- Tests that GPUs are working
- Shows you the status

---

## 🔍 **STEP 5: CHECK IF IT'S WORKING**

### **Check if services are running:**
```bash
# See all your AI services
kubectl get pods -n sophia-ai

# You should see something like:
# sophia-mcp-ai-memory-xxx     Running
# sophia-mcp-snowflake-xxx     Running
# sophia-mcp-linear-xxx        Running
```

### **Test GPU access:**
```bash
# Test if AI can use the GPU
kubectl exec -it deployment/sophia-mcp-ai-memory -n sophia-ai -- nvidia-smi

# You should see GPU information displayed
```

### **Check the main API:**
```bash
# Forward the API to your local machine
kubectl port-forward service/sophia-api-service 8000:80 -n sophia-ai

# Now open your browser to: http://localhost:8000
# You should see the Sophia AI interface
```

---

## 🎉 **STEP 6: USE YOUR AI SYSTEM**

### **Access the AI Chat:**
1. Open browser to `http://your-lambda-server-ip:8000`
2. You'll see the Sophia AI dashboard
3. Start asking questions like:
   - "What's our revenue trend?"
   - "Show me recent call analysis"
   - "What are the top project risks?"

### **Monitor GPU Usage:**
```bash
# Watch GPU usage in real-time
watch -n 1 nvidia-smi
```

---

## 🔧 **TROUBLESHOOTING (If Something Goes Wrong)**

### **If deployment fails:**
```bash
# Check what went wrong
kubectl get pods -n sophia-ai
kubectl logs deployment/sophia-mcp-ai-memory -n sophia-ai
```

### **If GPU isn't working:**
```bash
# Check GPU drivers
nvidia-smi

# If this doesn't work, reinstall drivers:
sudo apt install --reinstall nvidia-driver-535
sudo reboot
```

### **If services won't start:**
```bash
# Restart everything
kubectl delete namespace sophia-ai
./scripts/deploy_lambda_labs_kubernetes.sh
```

---

## 💰 **COST OPTIMIZATION TIPS**

1. **Stop when not using:**
   ```bash
   # Stop all services (saves money)
   kubectl scale deployment --all --replicas=0 -n sophia-ai
   
   # Start them again later
   kubectl scale deployment --all --replicas=2 -n sophia-ai
   ```

2. **Use smaller GPU for testing:**
   - Start with RTX 3080 for development
   - Upgrade to RTX 4090 for production

3. **Monitor usage:**
   ```bash
   # Check how much GPU you're actually using
   kubectl top nodes
   ```

---

## 🎯 **WHAT YOU GET AFTER DEPLOYMENT**

✅ **AI-Powered Business Intelligence** - Ask questions in plain English
✅ **Real-time Data Analysis** - Snowflake, Gong, HubSpot integration  
✅ **GPU-Accelerated Performance** - 3-5x faster than CPU-only
✅ **Scalable Infrastructure** - Automatically handles more users
✅ **24/7 Monitoring** - Alerts if anything breaks

---

## 📞 **NEED HELP?**

1. **Check the logs:** `kubectl logs -f deployment/sophia-mcp-ai-memory -n sophia-ai`
2. **Restart a service:** `kubectl rollout restart deployment/sophia-mcp-ai-memory -n sophia-ai`
3. **Get status:** `kubectl get all -n sophia-ai`

**🚀 That's it! Your AI system is now running on Lambda Labs with GPU acceleration!** 