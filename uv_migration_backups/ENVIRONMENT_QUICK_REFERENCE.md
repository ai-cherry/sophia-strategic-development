# 🚀 Sophia AI Environment Quick Reference

## When Other AI Coding Tools Kick You Out

### 🔧 **Quick Recovery (Manual)**
```bash
cd ~/sophia-main
source .venv/bin/activate
export ENVIRONMENT=prod
export PULUMI_ORG=scoobyjava-org
export PULUMI_ACCESS_TOKEN=your_pulumi_token_here
```

### 🛠️ **Quick Recovery (Script)**
```bash
./restore_sophia_env.sh
```

### ⚡ **Quick Recovery (Alias)**
```bash
# First, add to ~/.zshrc:
source sophia_aliases.sh

# Then use:
sophia
```

## 🎯 **Verification Commands**
```bash
# Check environment
echo "Directory: $(pwd)"
echo "Python: $(which python)"
echo "Virtual Env: $VIRTUAL_ENV"
echo "Environment: $ENVIRONMENT"

# Check git status
git status

# Test configuration
python -c "from backend.core.auto_esc_config import get_config_value; print('Config loaded:', bool(get_config_value('openai_api_key')))"
```

## 🚀 **Common Operations**

### Run Stabilized FastAPI App
```bash
uvicorn backend.app.stabilized_fastapi_app:app --host 0.0.0.0 --port 8001
```

### Test Phase 2 Minimal App
```bash
python backend/app/phase2_minimal_app.py
```

### Run Phase 2 Optimized App
```bash
uvicorn backend.app.phase2_optimized_fastapi_app:app --host 0.0.0.0 --port 8002
```

## 🔍 **Troubleshooting**

### If imports fail with "aiomysql" error:
This is expected - the optimized connection manager includes optional dependencies.

### If Pulumi ESC fails:
```bash
# Check token
echo $PULUMI_ACCESS_TOKEN

# Re-export if needed
export PULUMI_ACCESS_TOKEN=your_pulumi_token_here
```

### If wrong directory:
```bash
cd ~/sophia-main
pwd  # Should show /Users/lynnmusil/sophia-main
```

### If wrong Python:
```bash
which python  # Should show /Users/lynnmusil/sophia-main/.venv/bin/python
source .venv/bin/activate
```

## 📊 **Environment Health Check**
```bash
echo "🔍 Environment Health Check"
echo "Directory: $(pwd)"
echo "Python: $(which python)"
echo "Virtual Env: $VIRTUAL_ENV"
echo "Environment: $ENVIRONMENT"
echo "Pulumi Org: $PULUMI_ORG"
echo "Pulumi Token: ${PULUMI_ACCESS_TOKEN:+SET}${PULUMI_ACCESS_TOKEN:-NOT SET}"
git status --short
```

## 💡 **Pro Tips**

1. **Always verify your environment** after any AI coding tool interaction
2. **Use the restoration script** for fastest recovery
3. **Set up aliases** for one-command environment setup
4. **Keep this reference handy** for quick troubleshooting
5. **The .venv should always be activated** when working with Sophia AI

---

**🎯 Bottom Line:** When in doubt, run `./restore_sophia_env.sh` and you'll be back in business! 