# 🚀 Sophia AI Master Environment Guide

## Quick Start (Copy & Paste)

```bash
cd ~/sophia-main
source .venv/bin/activate
export ENVIRONMENT="prod"
export PULUMI_ORG="scoobyjava-org"
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

## 📋 Complete Setup Instructions

### 1. Initial Setup
```bash
# Navigate to project directory
cd ~/sophia-main

# Create virtual environment if it doesn't exist
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate
```

### 2. Set Environment Variables
```bash
# Required environment variables
export ENVIRONMENT="prod"
export PULUMI_ORG="scoobyjava-org"
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### 3. Verify Setup
```bash
# Check Python
which python
python --version

# Test backend import
python -c "import backend; print('✅ Backend module loaded successfully')"

# Check environment variables
echo "ENVIRONMENT: $ENVIRONMENT"
echo "PULUMI_ORG: $PULUMI_ORG"
echo "PYTHONPATH: $PYTHONPATH"
```

## 🔧 Permanent Setup (Add to Shell Profile)

Add these lines to your `~/.bashrc` or `~/.zshrc`:

```bash
# Sophia AI Environment
alias sophia='cd ~/sophia-main && source .venv/bin/activate'
export ENVIRONMENT="prod"
export PULUMI_ORG="scoobyjava-org"
```

Then reload your shell:
```bash
source ~/.bashrc  # or source ~/.zshrc
```

## 📁 Key File Locations

- **Virtual Environment**: `~/sophia-main/.venv`
- **Backend Module**: `~/sophia-main/backend/`
- **Scripts**: `~/sophia-main/scripts/`
- **Configuration**: `~/sophia-main/config/`
- **MCP Servers**: `~/sophia-main/mcp-servers/`

## 🎯 Common Commands

### Start MCP Servers
```bash
sophia  # Using the alias
python scripts/start_mcp_servers.py
```

### Run Tests
```bash
sophia
python scripts/test_environment_setup.py
```

### Check Environment Health
```bash
sophia
python backend/scripts/check_environment_health.py
```

### Deploy Services
```bash
sophia
python scripts/deploy_mcp_servers.py
```

## ❗ Important Notes

1. **Always use production environment**: `ENVIRONMENT="prod"`
2. **Never default to staging**: The system is configured for production-first
3. **Virtual environment is required**: Always activate before running Python scripts
4. **PYTHONPATH must include project root**: For proper module imports

## 🆘 Troubleshooting

### Import Errors
If you get `ModuleNotFoundError: No module named 'backend'`:
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Virtual Environment Not Found
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Permission Errors
```bash
chmod +x scripts/*.sh
chmod +x scripts/*.py
```

### Environment Variable Not Set
```bash
# Quick fix
export ENVIRONMENT="prod"
export PULUMI_ORG="scoobyjava-org"

# Permanent fix - add to ~/.bashrc or ~/.zshrc
```

## 🔍 Verification Script

Run this to verify everything is set up correctly:
```bash
./verify_and_activate_env.sh
```

Or manually:
```bash
python scripts/test_environment_setup.py
```

## 📊 Environment Status Checklist

- [ ] In sophia-main directory
- [ ] Virtual environment activated
- [ ] ENVIRONMENT="prod" set
- [ ] PULUMI_ORG="scoobyjava-org" set
- [ ] PYTHONPATH includes project root
- [ ] Backend module imports successfully
- [ ] All key files exist

## 🎉 Success!

When everything is set up correctly, you should see:
- Python from `.venv/bin/python`
- Environment variables properly set
- Backend module imports without errors
- All scripts executable

---

**Remember**: Always start with `cd ~/sophia-main && source .venv/bin/activate` in new terminals!
