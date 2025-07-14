# 🔑 Lambda Labs SSH Setup Guide

## 🚨 **Current Issue: SSH Authentication Failed**

Your deployment failed because SSH access to Lambda Labs servers needs to be configured.

## 🔐 **Your SSH Public Key (Generated)**

Add this key to your Lambda Labs servers:

```
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQCzGl7DQOjlj2G5iUkCP8mVdIrhRY2WxfweWeWXBn012z9z9gW6Nl6INoMmLNM/bILT6Of/1bOP4Gn+CqVlCiQAhyjWxKpOf6Tkr9RPqQyWj3xxClA9ocRK14OImcYjFGRA4wg1DVoUiUi7EvL4hpP4WzwCVim30wPQ45xOeTEDNR2jhTKTI/pPp4EZoXiD23HzgyaVqUoUnBkJBtHSgVvwSXoV4bor1vIoEGIcYollUUYDZhga/Goa3gxhF8mtuw5nLb3wXivCj2fdkbCJQVzo/sm8z1NlXkce0PpkMVx0mvuFtszB+xEJX4rx3xX8UsrfvNhFNWHv8J/E4tCB/3A9obB6+hTu92sY673LHnlEBsuwepntup5Sm5NMqci+G9mwoFD3BaeWeWJ0tNttjfbS6e8pHmAHcddP+9UdegwTx7wEl3imMBZkhDH/XQZ75sWtCjn8vAse2YpZNO2CJ2aCHKtnrEaPMXqI9DPkqHOEX/ptMTvTWNqQdjYmw/K8e4xAVvx2gFCCnzJ4FFnu6GDwV/lxVIP3DwiPc5PDZY6J83ZTp3/lEFysLzayrBx90gFE9C/IkDwt+oEmk/tQHXZ1wqAn/nQOqYTxkiKtN5eCeeN2mlHDiupAjVsf+MLercQruAumC1KXd9IFyiG0srrtbraa+WHrZKThPR6yDGWdiw== sophia-ai-deployment
```

## 🚀 **Option 1: Lambda Labs Console (Recommended)**

### **Step 1: Access Lambda Labs Console**
1. Go to: https://cloud.lambdalabs.com/
2. Log in to your account
3. Navigate to "Instances"

### **Step 2: Add SSH Key to Each Server**
For each server, do the following:

#### **Primary Server (192.222.58.232)**
1. Click on your primary instance
2. Go to "SSH Keys" or "Access" section
3. Add the SSH public key above
4. Save changes

#### **MCP Orchestrator (104.171.202.117)**
1. Click on your MCP orchestrator instance  
2. Go to "SSH Keys" or "Access" section
3. Add the SSH public key above
4. Save changes

#### **Data Pipeline (104.171.202.134)**
1. Click on your data pipeline instance
2. Go to "SSH Keys" or "Access" section
3. Add the SSH public key above
4. Save changes

#### **Development (155.248.194.183)**
1. Click on your development instance
2. Go to "SSH Keys" or "Access" section
3. Add the SSH public key above
4. Save changes

### **Step 3: Test SSH Access**
```bash
# Test each server
ssh root@192.222.58.232
ssh root@104.171.202.117
ssh root@104.171.202.134
ssh root@155.248.194.183
```

### **Step 4: Run Deployment**
```bash
python3 scripts/master_deploy.py
```

---

## 🚀 **Option 2: Manual Server Access (Alternative)**

If SSH key setup is complex, you can deploy directly on each server:

### **Primary Server (192.222.58.232)**
```bash
# SSH to server (use Lambda Labs console SSH or existing key)
ssh root@192.222.58.232

# Clone repository
git clone https://github.com/ai-cherry/sophia-main.git
cd sophia-main

# Run deployment script
bash scripts/deploy_primary_server.sh
```

### **MCP Orchestrator (104.171.202.117)**
```bash
# SSH to server
ssh root@104.171.202.117

# Clone repository
git clone https://github.com/ai-cherry/sophia-main.git
cd sophia-main

# Run deployment script
bash scripts/deploy_mcp_server.sh
```

### **Setup SSL (on Primary Server)**
```bash
# SSH to primary server
ssh root@192.222.58.232
cd sophia-main

# Run SSL setup
bash scripts/setup_ssl.sh
```

---

## 🚀 **Option 3: Use Lambda Labs SSH Key (If Available)**

If you have the Lambda Labs private key file:

### **Step 1: Copy Key**
```bash
# Copy your Lambda Labs key
cp /path/to/your/lambda-labs-key ~/.ssh/lambda_labs_key
chmod 600 ~/.ssh/lambda_labs_key
```

### **Step 2: Update SSH Config**
```bash
# Edit SSH config
nano ~/.ssh/config

# Add this configuration:
Host sophia-primary
    HostName 192.222.58.232
    User root
    IdentityFile ~/.ssh/lambda_labs_key

Host sophia-mcp
    HostName 104.171.202.117
    User root
    IdentityFile ~/.ssh/lambda_labs_key

Host sophia-data
    HostName 104.171.202.134
    User root
    IdentityFile ~/.ssh/lambda_labs_key

Host sophia-dev
    HostName 155.248.194.183
    User root
    IdentityFile ~/.ssh/lambda_labs_key
```

### **Step 3: Test and Deploy**
```bash
# Test SSH
ssh sophia-primary

# Run deployment
python3 scripts/master_deploy.py
```

---

## 🎯 **Expected Results After SSH Setup**

Once SSH is working, the deployment will:

1. **Install Docker & K3s** on all servers
2. **Deploy Sophia AI backend** to primary server
3. **Deploy frontend** with nginx reverse proxy
4. **Setup SSL certificates** with Let's Encrypt
5. **Deploy MCP services** to orchestrator server
6. **Configure monitoring** with Prometheus + Grafana

### **Live Endpoints:**
- 🌐 **https://sophia-intel.ai** - Main interface
- 🔗 **https://api.sophia-intel.ai** - Backend API
- 📱 **https://app.sophia-intel.ai** - Frontend app
- 🪝 **https://webhooks.sophia-intel.ai** - Webhooks
- 🤖 **https://mcp.sophia-intel.ai** - MCP services

---

## 🆘 **Troubleshooting**

### **SSH Connection Issues:**
```bash
# Check SSH key exists
ls -la ~/.ssh/id_rsa*

# Test SSH with verbose output
ssh -v root@192.222.58.232

# Check SSH config
cat ~/.ssh/config
```

### **Permission Denied:**
- Ensure SSH public key is added to server's authorized_keys
- Check file permissions: `chmod 600 ~/.ssh/id_rsa`
- Verify correct username (root vs ubuntu)

### **Connection Timeout:**
- Check server is running in Lambda Labs console
- Verify IP addresses are correct
- Check firewall settings

---

## 💡 **Quick Start Summary**

1. **Add SSH key** to Lambda Labs console (Option 1)
2. **Test SSH access**: `ssh root@192.222.58.232`
3. **Run deployment**: `python3 scripts/master_deploy.py`
4. **Test endpoints**: `curl https://sophia-intel.ai/health`

**🎉 Once SSH is configured, deployment takes 30-45 minutes and everything will be live!** 