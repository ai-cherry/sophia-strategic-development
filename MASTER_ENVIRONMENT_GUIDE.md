# 🚀 MASTER ENVIRONMENT GUIDE - Sophia AI

> **THE DEFINITIVE GUIDE** for maintaining your Sophia AI development environment across all AI coding tools

## ⚡ **QUICK START (Copy & Paste)**

```bash
cd ~/sophia-main
source .venv/bin/activate
export ENVIRONMENT="prod"
export PULUMI_ORG="scoobyjava-org"
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

## 🎯 **GOLDEN RULE: ALWAYS BE HERE**
```bash
# Your coding environment should ALWAYS be:
Directory: /Users/lynnmusil/sophia-main
Virtual Env: /Users/lynnmusil/sophia-main/.venv (ACTIVATED)
Environment: ENVIRONMENT=prod
Pulumi Org: PULUMI_ORG=scoobyjava-org
```

## 🛠️ **INSTANT RECOVERY (When AI Tools Kick You Out)**

### 🔧 **Method 1: One-Line Recovery**
```bash
cd ~/sophia-main && source .venv/bin/activate && export ENVIRONMENT=prod && export PULUMI_ORG=scoobyjava-org && export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### 🛠️ **Method 2: Script Recovery**
```bash
./restore_sophia_env.sh
```

### ⚡ **Method 3: Alias Recovery** (Recommended)
```bash
# Add to ~/.zshrc:
alias sophia='cd ~/sophia-main && source .venv/bin/activate && export ENVIRONMENT=prod && export PULUMI_ORG=scoobyjava-org && export PYTHONPATH="${PYTHONPATH}:$(pwd)" && echo "🚀 Sophia AI Environment Ready!"'

# Then use:
sophia
```

### 🔍 **Method 4: Verification Script**
```bash
./verify_and_activate_env.sh
```

## 📋 **COMPLETE SETUP INSTRUCTIONS**

### **1. Initial Setup**
```bash
# Navigate to project directory
cd ~/sophia-main

# Create virtual environment if it doesn't exist
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
uv add -r backend/requirements.txt
```

### **2. Set Environment Variables**
```bash
# Required environment variables
export ENVIRONMENT="prod"
export PULUMI_ORG="scoobyjava-org"
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Optional: Set Pulumi access token
export PULUMI_ACCESS_TOKEN="your_token_here"
```

### **3. Verify Setup**
```bash
# Check Python
which python  # Should show .venv/bin/python
python --version

# Test backend import
python -c "import backend; print('✅ Backend module loaded successfully')"

# Check environment variables
echo "ENVIRONMENT: $ENVIRONMENT"
echo "PULUMI_ORG: $PULUMI_ORG"
echo "PYTHONPATH: $PYTHONPATH"
```

## 🔧 **PERMANENT SETUP (Add to Shell Profile)**

Add these lines to your `~/.bashrc` or `~/.zshrc`:

```bash
# Sophia AI Environment
alias sophia='cd ~/sophia-main && source .venv/bin/activate && export ENVIRONMENT=prod && export PULUMI_ORG=scoobyjava-org && export PYTHONPATH="${PYTHONPATH}:$(pwd)" && echo "🚀 Sophia AI Environment Ready!"'

# Auto-activate when entering directory
function cd() {
    builtin cd "$@"
    if [[ $(pwd) == *"sophia-main"* ]] && [[ -f ".venv/bin/activate" ]]; then
        source .venv/bin/activate
        export ENVIRONMENT="prod"
        export PULUMI_ORG="scoobyjava-org"
        export PYTHONPATH="${PYTHONPATH}:$(pwd)"
        echo "🚀 Auto-activated Sophia AI environment"
    fi
}
```

Then reload your shell:
```bash
source ~/.zshrc  # or source ~/.bashrc
```

## 📁 **KEY FILE LOCATIONS**

- **Virtual Environment**: `~/sophia-main/.venv`
- **Backend Module**: `~/sophia-main/backend/`
- **MCP Servers**: `~/sophia-main/backend/mcp_servers/`
- **Scripts**: `~/sophia-main/scripts/`
- **Configuration**: `~/sophia-main/config/`
- **Documentation**: `~/sophia-main/docs/`

## 🎯 **COMMON COMMANDS**

### **Environment Management**
```bash
sophia                                    # Quick activation
./verify_and_activate_env.sh            # Full verification
python scripts/validate_environment.py   # Comprehensive check
```

### **Application Management**
```bash
# Start main application
uvicorn backend.app.stabilized_fastapi_app:app --host 0.0.0.0 --port 8001

# Start minimal app for testing
python backend.app.minimal_app:app --host 0.0.0.0 --port 8002

# Run Phase 2 optimized app
uvicorn backend.app.phase2_optimized_app:app --host 0.0.0.0 --port 8003
```

### **Development Tools**
```bash
# Run tests
python -m pytest tests/

# Check environment health
python scripts/check_environment_health.py

# Validate configuration
python scripts/validate_environment.py --auto-fix

# Clean up documentation
python docs/cleanup_documentation.py
```

## ❗ **CRITICAL RULES**

1. **Always use production environment**: `ENVIRONMENT="prod"`
2. **Never default to staging**: The system is configured for production-first
3. **Virtual environment is mandatory**: Always activate before running Python scripts
4. **PYTHONPATH must include project root**: For proper module imports
5. **Never hardcode secrets**: Use Pulumi ESC or environment variables

## 🆘 **TROUBLESHOOTING**

### **Import Errors**
```bash
# Problem: ModuleNotFoundError: No module named 'backend'
# Solution:
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python -c "import backend; print('✅ Fixed!')"
```

### **Virtual Environment Issues**
```bash
# Problem: Virtual environment not found
# Solution:
python3 -m venv .venv
source .venv/bin/activate

# Problem: Wrong Python being used
# Solution:
deactivate
source .venv/bin/activate
which python  # Should show .venv/bin/python
```

### **Permission Errors**
```bash
chmod +x scripts/*.sh
chmod +x scripts/*.py
chmod +x *.sh
```

### **Environment Variable Issues**
```bash
# Quick fix
export ENVIRONMENT="prod"
export PULUMI_ORG="scoobyjava-org"
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Permanent fix - add to ~/.bashrc or ~/.zshrc
echo 'export ENVIRONMENT="prod"' >> ~/.zshrc
echo 'export PULUMI_ORG="scoobyjava-org"' >> ~/.zshrc
```

### **MCP Import Conflicts**
```bash
# Problem: MCP package shadowing
# Solution: This was fixed by renaming backend/mcp → backend/mcp_servers
python -c "from mcp.server import Server; print('✅ MCP imports work')"
```

### **Shell Integration Issues**
```bash
# Problem: Cline/Cursor shell integration not working
# Solution 1: Update VSCode
# CMD/CTRL + Shift + P → "Update"

# Solution 2: Set default shell
# CMD/CTRL + Shift + P → "Terminal: Select Default Profile"
# Choose: zsh, bash, fish, or PowerShell

# Solution 3: Manual terminal
# Open external terminal and run commands there
```

## 🔍 **VERIFICATION CHECKLIST**

Run this comprehensive check:
```bash
./verify_and_activate_env.sh
```

Or manual verification:
```bash
# ✅ Directory check
pwd | grep sophia-main

# ✅ Virtual environment check  
echo $VIRTUAL_ENV | grep sophia-main

# ✅ Python check
which python | grep .venv

# ✅ Environment variables check
echo "ENVIRONMENT=$ENVIRONMENT PULUMI_ORG=$PULUMI_ORG"

# ✅ Backend import check
python -c "import backend; print('✅ Backend imports successfully')"

# ✅ Configuration check
python -c "from backend.core.auto_esc_config import get_config_value; print('✅ Config system works')"
```

## 📊 **ENVIRONMENT STATUS CHECKLIST**

- [ ] In sophia-main directory (`pwd` shows `/Users/lynnmusil/sophia-main`)
- [ ] Virtual environment activated (`which python` shows `.venv/bin/python`)
- [ ] ENVIRONMENT="prod" set
- [ ] PULUMI_ORG="scoobyjava-org" set  
- [ ] PYTHONPATH includes project root
- [ ] Backend module imports successfully
- [ ] All key files exist
- [ ] No import chain errors

## 🎉 **SUCCESS INDICATORS**

When everything is set up correctly, you should see:
- ✅ Python from `.venv/bin/python`
- ✅ Environment variables properly set
- ✅ Backend module imports without errors
- ✅ All scripts executable
- ✅ FastAPI applications start successfully
- ✅ MCP servers can be imported
- ✅ Configuration system loads secrets

## 🚀 **SHELL INTEGRATION FIX**

### **For VSCode/Cursor Users:**
1. **Update VSCode**: `CMD/CTRL + Shift + P` → "Update"
2. **Set Default Shell**: `CMD/CTRL + Shift + P` → "Terminal: Select Default Profile" → Choose `zsh`
3. **Restart VSCode**: Close and reopen VSCode
4. **Test Integration**: Open terminal in VSCode and run `sophia`

### **For Cline Users:**
1. **Use External Terminal**: Open Terminal.app or iTerm2
2. **Run Commands There**: Execute all commands in external terminal
3. **Copy Results Back**: Copy output back to Cline if needed
4. **Alternative**: Use `echo` commands to show results

---

**🎯 REMEMBER: Always start with `sophia` command in new terminals!**

**🔧 EMERGENCY RECOVERY: `cd ~/sophia-main && source .venv/bin/activate && export ENVIRONMENT=prod && export PULUMI_ORG=scoobyjava-org`**
