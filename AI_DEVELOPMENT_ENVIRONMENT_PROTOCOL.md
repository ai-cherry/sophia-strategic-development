# 🤖 AI DEVELOPMENT ENVIRONMENT PROTOCOL

> **MANDATORY PROTOCOL** for all AI coding tools working on Sophia AI

## 🎯 **PROTOCOL OVERVIEW**

This protocol ensures that ANY AI coding tool (Cursor, Cline, GitHub Copilot, etc.) maintains environment consistency and follows established patterns when working on the Sophia AI codebase.

## 🔒 **MANDATORY PRE-FLIGHT CHECKS**

### **Before ANY Code Operation**
Every AI tool MUST execute these checks:

```bash
# 1. Environment Validation
if [ "$(pwd)" != "/Users/lynnmusil/sophia-main" ]; then
    echo "❌ WRONG DIRECTORY: $(pwd)"
    echo "🔧 FIXING: cd ~/sophia-main"
    cd ~/sophia-main
fi

# 2. Virtual Environment Check
if [ -z "$VIRTUAL_ENV" ] || [ "$VIRTUAL_ENV" != "/Users/lynnmusil/sophia-main/.venv" ]; then
    echo "❌ VIRTUAL ENV NOT ACTIVE"
    echo "🔧 FIXING: source .venv/bin/activate"
    source .venv/bin/activate
fi

# 3. Environment Variables Check
if [ "$ENVIRONMENT" != "prod" ]; then
    echo "❌ WRONG ENVIRONMENT: $ENVIRONMENT"
    echo "🔧 FIXING: export ENVIRONMENT=prod"
    export ENVIRONMENT="prod"
fi

if [ "$PULUMI_ORG" != "scoobyjava-org" ]; then
    echo "❌ WRONG PULUMI_ORG: $PULUMI_ORG"
    echo "🔧 FIXING: export PULUMI_ORG=scoobyjava-org"
    export PULUMI_ORG="scoobyjava-org"
fi

# 4. PYTHONPATH Check
if [[ "$PYTHONPATH" != *"$(pwd)"* ]]; then
    echo "❌ PYTHONPATH MISSING PROJECT ROOT"
    echo "🔧 FIXING: export PYTHONPATH"
    export PYTHONPATH="${PYTHONPATH}:$(pwd)"
fi

# 5. Backend Import Test
python -c "import backend" 2>/dev/null || {
    echo "❌ BACKEND IMPORT FAILED"
    echo "🔧 RUN: python scripts/validate_environment.py --auto-fix"
}
```

## ⚡ **QUICK ACTIVATION COMMANDS**

### **Method 1: One-Line Setup**
```bash
cd ~/sophia-main && source .venv/bin/activate && export ENVIRONMENT=prod && export PULUMI_ORG=scoobyjava-org && export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### **Method 2: Alias (Recommended)**
```bash
sophia  # If alias is set up
```

### **Method 3: Verification Script**
```bash
./verify_and_activate_env.sh
```

### **Method 4: Environment Script**
```bash
./restore_sophia_env.sh
```

## 📂 **CRITICAL DIRECTORY STRUCTURE**

```
~/sophia-main/
├── backend/                    # Main Python backend
│   ├── __init__.py            # Conditional imports (FIXED)
│   ├── app/                   # FastAPI applications
│   ├── core/                  # Core services
│   ├── mcp_servers/           # MCP servers (renamed from mcp)
│   └── api/                   # API routes
├── frontend/                  # React frontend
├── scripts/                   # Utility scripts
├── docs/                      # Documentation (organized)
├── config/                    # Configuration files
├── .venv/                     # Virtual environment
└── requirements.txt           # Python dependencies
```

## 🚨 **CRITICAL RULES FOR AI TOOLS**

### **1. Environment Rules**
- ✅ **ALWAYS** use `ENVIRONMENT="prod"`
- ❌ **NEVER** default to staging
- ✅ **ALWAYS** activate virtual environment
- ❌ **NEVER** use system Python
- ✅ **ALWAYS** set PYTHONPATH to include project root

### **2. Import Rules**
- ✅ **ALWAYS** test `import backend` before code operations
- ❌ **NEVER** use relative imports outside project structure
- ✅ **ALWAYS** use `backend.mcp_servers` (not `backend.mcp`)
- ❌ **NEVER** assume modules are importable without verification

### **3. File Operation Rules**
- ✅ **ALWAYS** use absolute paths from project root
- ❌ **NEVER** assume current directory
- ✅ **ALWAYS** check file existence before operations
- ❌ **NEVER** create files without proper directory structure

### **4. Shell Integration Rules**
- ✅ **ALWAYS** handle shell integration failures gracefully
- ❌ **NEVER** assume shell output is available
- ✅ **ALWAYS** provide alternative methods
- ❌ **NEVER** fail silently on shell issues

## 🛠️ **SHELL INTEGRATION TROUBLESHOOTING**

### **For Cline (Current Issue)**
```bash
# Problem: "Shell Integration Unavailable"
# Solutions:

# 1. Update VSCode
# CMD/CTRL + Shift + P → "Update"

# 2. Set Default Shell Profile
# CMD/CTRL + Shift + P → "Terminal: Select Default Profile"
# Choose: zsh (recommended)

# 3. Use External Terminal
# Open Terminal.app or iTerm2
# Run commands there and copy results

# 4. Use Echo Commands for Verification
echo "Current directory: $(pwd)"
echo "Python path: $(which python)"
echo "Virtual env: $VIRTUAL_ENV"
```

### **For Cursor**
```bash
# Usually works better, but if issues:
# 1. Restart Cursor
# 2. Clear terminal and try again
# 3. Use integrated terminal instead of external
```

### **Universal Fallback**
```bash
# When shell integration fails, use verification commands:
python -c "import os; print(f'Directory: {os.getcwd()}')"
python -c "import sys; print(f'Python: {sys.executable}')"
python -c "import os; print(f'ENVIRONMENT: {os.getenv(\"ENVIRONMENT\")}')"
python -c "import backend; print('✅ Backend imports successfully')"
```

## 📋 **COMMON TASKS FOR AI TOOLS**

### **Starting Development Session**
```bash
# 1. Navigate and activate
cd ~/sophia-main
source .venv/bin/activate

# 2. Set environment variables
export ENVIRONMENT="prod"
export PULUMI_ORG="scoobyjava-org"
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# 3. Verify setup
python -c "import backend; print('✅ Ready for development')"
```

### **Running Applications**
```bash
# Main application
uvicorn backend.app.stabilized_fastapi_app:app --host 0.0.0.0 --port 8001

# Minimal application (for testing)
uvicorn backend.app.minimal_app:app --host 0.0.0.0 --port 8002

# Phase 2 optimized application
uvicorn backend.app.phase2_optimized_app:app --host 0.0.0.0 --port 8003
```

### **Running Scripts**
```bash
# Environment validation
python scripts/validate_environment.py --auto-fix

# Documentation cleanup
python docs/cleanup_documentation.py

# Testing
python -m pytest tests/
```

### **File Operations**
```bash
# Always verify location first
pwd | grep sophia-main || cd ~/sophia-main

# Check if file exists before editing
test -f "path/to/file" && echo "File exists" || echo "File not found"

# Use proper imports
python -c "from backend.core.auto_esc_config import get_config_value"
```

## 🔧 **ERROR HANDLING PROTOCOLS**

### **Import Errors**
```bash
# Problem: ModuleNotFoundError: No module named 'backend'
# Protocol:
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python -c "import backend" || echo "❌ Still failing - check environment"
```

### **Environment Errors**
```bash
# Problem: Wrong environment or missing variables
# Protocol:
export ENVIRONMENT="prod"
export PULUMI_ORG="scoobyjava-org"
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### **Shell Integration Errors**
```bash
# Problem: Commands not showing output
# Protocol:
# 1. Try external terminal
# 2. Use echo commands for feedback
# 3. Verify with Python commands
echo "Testing shell: $(date)"
python -c "print('Python works')"
```

### **Application Startup Errors**
```bash
# Problem: FastAPI app won't start
# Protocol:
# 1. Check imports first
python -c "from backend.app.stabilized_fastapi_app import app"

# 2. Check port availability
lsof -i :8001 || echo "Port 8001 available"

# 3. Use minimal app for testing
python -c "from backend.app.minimal_app import app; print('Minimal app works')"
```

## 📊 **VALIDATION CHECKLIST FOR AI TOOLS**

Before any significant operation, verify:

- [ ] ✅ Directory: `/Users/lynnmusil/sophia-main`
- [ ] ✅ Virtual env: `.venv/bin/python`
- [ ] ✅ Environment: `ENVIRONMENT=prod`
- [ ] ✅ Pulumi org: `PULUMI_ORG=scoobyjava-org`
- [ ] ✅ Python path: Includes project root
- [ ] ✅ Backend import: `import backend` works
- [ ] ✅ Config system: `from backend.core.auto_esc_config import get_config_value` works
- [ ] ✅ MCP imports: `from backend.mcp_servers.enhanced_ai_memory_mcp_server import EnhancedAiMemoryMCPServer` works

## 🎯 **SUCCESS CRITERIA**

AI tools should achieve:
- ✅ **100% Environment Consistency**: Same setup every time
- ✅ **Zero Import Failures**: All modules load correctly
- ✅ **Graceful Error Handling**: Recover from shell integration issues
- ✅ **Proper Documentation**: Follow established documentation patterns
- ✅ **Security Compliance**: Never hardcode secrets or tokens

## 🚀 **INTEGRATION WITH DOCUMENTATION SYSTEM**

When creating or updating documentation:

1. **Follow Structure**: Use organized `docs/` directory
2. **Update Index**: Add to `SOPHIA_AI_DOCUMENTATION_MASTER_INDEX.md`
3. **Use Templates**: Follow established patterns
4. **Consolidate**: Use cleanup script to organize
5. **Verify Links**: Ensure all references work

## 💡 **BEST PRACTICES FOR AI TOOLS**

### **Development Workflow**
1. ✅ Always start with environment validation
2. ✅ Test imports before complex operations
3. ✅ Use verification scripts regularly
4. ✅ Handle shell integration failures gracefully
5. ✅ Provide multiple solution methods

### **Code Generation**
1. ✅ Use proper import paths (`backend.mcp_servers`)
2. ✅ Include error handling in generated code
3. ✅ Follow established patterns
4. ✅ Test generated code immediately
5. ✅ Update documentation when needed

### **Error Recovery**
1. ✅ Provide clear error messages
2. ✅ Offer specific solutions
3. ✅ Include verification steps
4. ✅ Document common issues
5. ✅ Test recovery procedures

---

**🎯 REMEMBER: This protocol ensures consistent, reliable development regardless of which AI tool is being used!**

**🔧 EMERGENCY COMMAND: `cd ~/sophia-main && source .venv/bin/activate && export ENVIRONMENT=prod && export PULUMI_ORG=scoobyjava-org && export PYTHONPATH="${PYTHONPATH}:$(pwd)"`**
