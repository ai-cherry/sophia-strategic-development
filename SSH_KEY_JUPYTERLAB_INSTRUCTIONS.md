# 🔑 Add SSH Key via JupyterLab - Step by Step

**Your SSH Public Key** (copy this exactly):
```
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCKAPI0WU9UcB5vVnneP3oExytrPcD0PON5NeQxeNAJOWQSWi/fvkQ97dhAEtjyddmaCti7LFrp3CW+4gtGSiC+2/jOVqERLkmycbC8UZNpyqCiLIwO4MkIuxVNiRkg/ucPuf0DjakJh92xFDIyeDAR55OrpMWqX6O0+OZL0DFXE7jBDaloez+oLytM16CMHtlnx+5Br7O+RoPLEFvBz9RZyqlzs5144pvgHyRSwuvXBcYLKqT24kAPqvxc0SqGYLnNAD1q96BPqMwZONAFPDf3jTFGznmO+I3f+cyiR9Mai7Na9C2/21UJL/9APt7unjQhyQtCF++pwUXxhJX42tId SophiaSSH5
```

---

## 🚀 **FOR EACH SERVER - DO THIS:**

### **Step 1: Access JupyterLab**
1. Go to: **https://cloud.lambdalabs.com/instances**
2. Find your server in the list
3. Click **"Launch"** under the "Cloud IDE" column
4. Wait for JupyterLab to load

### **Step 2: Open Terminal**
1. In JupyterLab, click **"Terminal"** (or File → New → Terminal)
2. A terminal window will open

### **Step 3: Add SSH Key**
Copy and paste this command (all on one line):

```bash
echo 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCKAPI0WU9UcB5vVnneP3oExytrPcD0PON5NeQxeNAJOWQSWi/fvkQ97dhAEtjyddmaCti7LFrp3CW+4gtGSiC+2/jOVqERLkmycbC8UZNpyqCiLIwO4MkIuxVNiRkg/ucPuf0DjakJh92xFDIyeDAR55OrpMWqX6O0+OZL0DFXE7jBDaloez+oLytM16CMHtlnx+5Br7O+RoPLEFvBz9RZyqlzs5144pvgHyRSwuvXBcYLKqT24kAPqvxc0SqGYLnNAD1q96BPqMwZONAFPDf3jTFGznmO+I3f+cyiR9Mai7Na9C2/21UJL/9APt7unjQhyQtCF++pwUXxhJX42tId SophiaSSH5' >> ~/.ssh/authorized_keys
```

### **Step 4: Verify**
Run this command to verify the key was added:
```bash
cat ~/.ssh/authorized_keys
```

You should see your SSH key in the output.

---

## 📋 **SERVERS TO UPDATE:**

**Do the above steps for each of these servers:**

1. **Primary Production (GH200)** - IP: 192.222.58.232
2. **MCP Orchestrator (A6000)** - IP: 104.171.202.117  
3. **Data Pipeline (A100)** - IP: 104.171.202.134
4. **Production Services (RTX6000)** - IP: 104.171.202.103
5. **Development (A10)** - IP: 155.248.194.183

---

## ✅ **AFTER ADDING TO ALL SERVERS:**

Test SSH access with:
```bash
ssh -i ~/.ssh/sophia_correct_key ubuntu@192.222.58.232
```

If that works, then run the deployment:
```bash
python3 scripts/deploy_to_lambda_labs.py
```

---

## 🎯 **QUICK CHECKLIST:**

- [ ] Server 1 (192.222.58.232) - SSH key added via JupyterLab
- [ ] Server 2 (104.171.202.117) - SSH key added via JupyterLab  
- [ ] Server 3 (104.171.202.134) - SSH key added via JupyterLab
- [ ] Server 4 (104.171.202.103) - SSH key added via JupyterLab
- [ ] Server 5 (155.248.194.183) - SSH key added via JupyterLab
- [ ] Test SSH access locally
- [ ] Run deployment script

**This should take about 5-10 minutes total for all servers.** 