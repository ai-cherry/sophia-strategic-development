# 🚀 Sophia AI - Client Extension Instructions (UPDATED July 17, 2025)

## **AUTOMATIC ENVIRONMENT (No Manual Setup Required)**

### **✅ New Simplified Workflow:**
```bash
# 1. Open terminal in Cursor
# 2. Navigate to project
cd /Users/lynnmusil/sophia-main-2

# 3. Environment auto-activates! ✨
# You'll see: (.venv) lynnmusil@PR901-LMUSIL ~/sophia-main-2 %

# 4. Start coding immediately!
```

### **🔍 Quick Verification:**
```bash
sophia-status    # Check environment status
```

### **🎯 Available Shortcuts:**
```bash
sophia-activate  # Manual activation (if needed)
sophia-cd        # Quick navigation to project
run-working      # Start FastAPI (port 8000)
run-simple       # Start FastAPI (port 8001)
```

### **✅ Environment Requirements:**
- **Python:** 3.11.6 (virtual environment)
- **Environment:** `ENVIRONMENT=prod` (auto-set)
- **Pulumi Org:** `PULUMI_ORG=scoobyjava-org` (auto-set)
- **Prompt:** Single `(.venv)` indicator (not double)

### **❌ What NOT to Do:**
- ❌ Don't run `source activate_sophia_env.sh` (automatic now)
- ❌ Don't use `python3` command (use `python`)
- ❌ Don't manually set environment variables (auto-configured)

### **🆘 If Environment Issues:**
```bash
sophia-activate  # Manual activation
reload          # Reload shell config
sophia-status   # Check status
```

**🎉 That's it! Environment is now fully automated.** 