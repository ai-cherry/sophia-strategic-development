# 🔑 Lambda Labs SSH Configuration - DEFINITIVE GUIDE

**Last Updated**: July 6, 2025
**Status**: ✅ **PRODUCTION READY**

## 🎯 Current Production Configuration

### **Active Instance**
- **Name**: lynn-sophia-gh200-master-01
- **IP**: 192.222.51.151
- **SSH Key in Lambda Labs**: lynn-sophia-key
- **Local Private Key**: ~/.ssh/lynn_sophia_h200_key
- **Local Public Key**: ~/.ssh/lynn_sophia_h200_key.pub

### **SSH Connection Command**
```bash
ssh -i ~/.ssh/lynn_sophia_h200_key ubuntu@192.222.51.151
```

## 🔐 Key Management

### **Local SSH Keys**
```bash
# Your local private key (KEEP THIS SECURE)
~/.ssh/lynn_sophia_h200_key

# Your local public key
~/.ssh/lynn_sophia_h200_key.pub
# Content: ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAID5Oz2Q3EZFGl0Zap+eZaCIn55FfVjpt5Y+lE+t8/pxI lynn-sophia-h200-key
```

### **Lambda Labs SSH Keys**
The following key is registered in Lambda Labs and matches your local key:
- **Key Name**: lynn-sophia-key
- **Key ID**: b6d556aad0f64c8eb22c9224b3dff66a
- **Public Key**: Matches your local ~/.ssh/lynn_sophia_h200_key.pub

## 🚀 Common Operations

### **Test SSH Connection**
```bash
ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no \
    -i ~/.ssh/lynn_sophia_h200_key ubuntu@192.222.51.151 \
    "echo 'SSH Working' && hostname"
```

### **Check GPU Status**
```bash
ssh -i ~/.ssh/lynn_sophia_h200_key ubuntu@192.222.51.151 \
    "nvidia-smi --query-gpu=name,memory.total,memory.used --format=csv,noheader"
```

### **Check Docker Services**
```bash
ssh -i ~/.ssh/lynn_sophia_h200_key ubuntu@192.222.51.151 \
    "docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'"
```

### **Deploy Application**
```bash
# Copy files
scp -i ~/.ssh/lynn_sophia_h200_key -r ./backend ubuntu@192.222.51.151:~/sophia-deployment/

# Run deployment
ssh -i ~/.ssh/lynn_sophia_h200_key ubuntu@192.222.51.151 \
    "cd ~/sophia-deployment && docker-compose up -d"
```

## 🔄 GitHub Secrets Integration

### **Required GitHub Secrets**
Update these in your GitHub Organization Secrets:

1. **LAMBDA_LABS_SSH_PRIVATE_KEY**
   ```bash
   # Encode your private key
   base64 -w 0 ~/.ssh/lynn_sophia_h200_key
   # Copy the output and set as GitHub secret
   ```

2. **LAMBDA_LABS_SSH_KEY_NAME**
   ```
   lynn-sophia-key
   ```

3. **LAMBDA_LABS_INSTANCE_IP**
   ```
   192.222.51.151
   ```

## 📋 Deployment Scripts Configuration

All deployment scripts should use these environment variables:
```python
ssh_key_path = os.path.expanduser("~/.ssh/lynn_sophia_h200_key")
instance_ip = "192.222.51.151"
ssh_key_name = "lynn-sophia-key"
```

## ⚠️ Important Notes

1. **DO NOT** create new SSH keys unless absolutely necessary
2. **DO NOT** use `lynn-sophia-key-fixed` - this was deleted
3. **ALWAYS** use `~/.ssh/lynn_sophia_h200_key` as your local private key
4. **ALWAYS** ensure new instances use `lynn-sophia-key` from Lambda Labs

## 🔧 Troubleshooting

### If SSH Fails
1. Verify instance is active: Check Lambda Labs dashboard
2. Verify IP is correct: `192.222.51.151`
3. Verify key permissions: `chmod 600 ~/.ssh/lynn_sophia_h200_key`
4. Verify key exists: `ls -la ~/.ssh/lynn_sophia_h200_key`

### Creating New Instances
Always use this command pattern:
```bash
curl -u $LAMBDA_LABS_API_KEY: -X POST \
  https://cloud.lambdalabs.com/api/v1/instance-operations/launch \
  -H "Content-Type: application/json" \
  -d '{
    "region_name": "us-east-3",
    "instance_type_name": "gpu_1x_gh200",
    "ssh_key_names": ["lynn-sophia-key"],
    "name": "lynn-sophia-gh200-master-01"
  }'
```

## ✅ Validation Checklist

- [ ] Local private key exists: `~/.ssh/lynn_sophia_h200_key`
- [ ] Key has correct permissions: `600`
- [ ] Lambda Labs has key: `lynn-sophia-key`
- [ ] Instance uses correct key: `lynn-sophia-key`
- [ ] SSH connection works
- [ ] GitHub secrets updated
- [ ] Deployment scripts use correct paths

---
**This is the authoritative SSH configuration. Any conflicting documentation should be updated to match this guide.**
