# 🚀 **FULLY AUTOMATED LAMBDA LABS DEPLOYMENT**
## Three Ways to Deploy Sophia AI (Choose Your Preferred Method)

---

## 🎯 **METHOD 1: WEB INTERFACE (EASIEST)**

### **One-Click Web Deployment:**
1. Open `scripts/web_deployment_interface.html` in your browser
2. Enter your Lambda Labs API key
3. Click "Deploy Sophia AI to Lambda Labs" 
4. Download the generated script
5. Run the script in Terminal
6. Wait 20-30 minutes
7. Your AI is ready!

**Perfect for:** Non-technical users who prefer a visual interface

---

## 🖥️ **METHOD 2: COMMAND LINE (RECOMMENDED)**

### **Two-Command Deployment:**
```bash
# Step 1: Setup the automation
python3 scripts/automated_lambda_labs_deployment.py

# Step 2: Run one-click deployment
./scripts/one_click_lambda_deploy.sh
```

**Perfect for:** Developers who like command line but want automation

---

## ⚡ **METHOD 3: MANUAL STEPS (TRADITIONAL)**

### **If You Want Full Control:**
```bash
# 1. SSH into your Lambda Labs server
ssh ubuntu@your-server-ip

# 2. Download the code
git clone https://github.com/ai-cherry/sophia-main.git
cd sophia-main

# 3. Run deployment
./scripts/deploy_lambda_labs_kubernetes.sh
```

**Perfect for:** Advanced users who want to see every step

---

## 📋 **PREREQUISITES (FOR ALL METHODS)**

### **What You Need:**
1. **Lambda Labs Account** - Sign up at https://lambdalabs.com/
2. **API Key** - Get from https://cloud.lambdalabs.com/api-keys
3. **Credit Card** - For Lambda Labs billing (~$1.50/hour)

### **Set Your API Key:**
```bash
export LAMBDA_LABS_API_KEY="your-api-key-here"
```

---

## ⏱️ **WHAT TO EXPECT**

### **Timeline:**
- **Setup:** 2-3 minutes
- **Server Provisioning:** 3-5 minutes  
- **Environment Setup:** 10-15 minutes
- **Sophia AI Deployment:** 5-10 minutes
- **Total:** 20-30 minutes

### **Costs:**
- **RTX 4090 Instance:** ~$1.50/hour
- **Development:** Use RTX 3080 (~$0.90/hour)
- **Testing:** Use smaller GPU (~$0.50/hour)

---

## 🎉 **WHAT YOU GET AFTER DEPLOYMENT**

### **Fully Operational AI System:**
✅ **GPU-Accelerated AI** - 3-5x faster than CPU-only
✅ **Business Intelligence** - Ask questions in plain English  
✅ **Real-time Analytics** - Snowflake, Gong, HubSpot integration
✅ **Auto-scaling** - Handles more users automatically
✅ **24/7 Monitoring** - Alerts if anything breaks

### **Access Your AI:**
- **Web Interface:** `http://your-server-ip:8000`
- **API Documentation:** `http://your-server-ip:8000/docs`
- **SSH Access:** `ssh -i ~/.ssh/lambda_labs_key ubuntu@your-server-ip`

---

## 🔧 **TROUBLESHOOTING**

### **Common Issues:**

**"API Key Invalid"**
```bash
# Get new API key from Lambda Labs dashboard
export LAMBDA_LABS_API_KEY="new-key-here"
```

**"Instance Launch Failed"**
```bash
# Check Lambda Labs capacity in different regions
# Try us-east-1 instead of us-west-2
```

**"SSH Connection Failed"**
```bash
# Wait longer for instance to be ready
sleep 300  # Wait 5 more minutes
```

**"GPU Not Working"**
```bash
# SSH into server and check
ssh -i ~/.ssh/lambda_labs_key ubuntu@your-ip
nvidia-smi  # Should show GPU info
```

### **Get Help:**
```bash
# Check deployment status
kubectl get pods -n sophia-ai

# Check logs
kubectl logs -f deployment/sophia-mcp-ai-memory -n sophia-ai

# Restart if needed
kubectl rollout restart deployment/sophia-mcp-ai-memory -n sophia-ai
```

---

## 💰 **COST OPTIMIZATION TIPS**

### **Save Money:**
1. **Stop when not using:**
   ```bash
   # Stop all services
   kubectl scale deployment --all --replicas=0 -n sophia-ai
   ```

2. **Use smaller GPUs for development:**
   - Development: RTX 3080 ($0.90/hr)
   - Production: RTX 4090 ($1.50/hr)

3. **Terminate instance when done:**
   - Go to https://cloud.lambdalabs.com/instances
   - Click "Terminate" on your instance

### **Monitor Costs:**
```bash
# Check how long instance has been running
ssh -i ~/.ssh/lambda_labs_key ubuntu@your-ip 'uptime'
```

---

## 🚀 **NEXT STEPS AFTER DEPLOYMENT**

### **Start Using Your AI:**
1. **Open the dashboard:** `http://your-server-ip:8000`
2. **Ask business questions:**
   - "What's our revenue trend for the last 6 months?"
   - "Show me recent call sentiment analysis"
   - "What are the top project risks?"

3. **Monitor performance:**
   ```bash
   # Watch GPU usage
   ssh -i ~/.ssh/lambda_labs_key ubuntu@your-ip 'watch nvidia-smi'
   ```

### **Scale Up:**
- Add more GPU instances for higher load
- Configure auto-scaling for peak times
- Set up monitoring and alerting

---

## 📞 **SUPPORT**

### **If Something Goes Wrong:**
1. **Check the logs first**
2. **Try restarting the service**
3. **Check GPU availability**
4. **Verify network connectivity**

### **Emergency Commands:**
```bash
# Nuclear option - restart everything
kubectl delete namespace sophia-ai
./scripts/deploy_lambda_labs_kubernetes.sh
```

**🎉 That's it! You now have three different ways to deploy Sophia AI to Lambda Labs with full automation!**
