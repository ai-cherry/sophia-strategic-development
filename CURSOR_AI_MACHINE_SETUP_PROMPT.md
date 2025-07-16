# 🚀 CURSOR AI MACHINE SETUP PROMPT
## Complete Virtual Environment & FastAPI Alignment Setup

**COPY THIS ENTIRE PROMPT TO CURSOR AI ON YOUR NEW MACHINE**

---

## 🎯 OBJECTIVE
Set up identical virtual environment consistency across all AI coding tools (Cursor, Cline, etc.) with aligned FastAPI applications and eliminate shell errors when switching between tools.

## 📋 BACKGROUND CONTEXT
This setup solves a critical issue where Python environment mismatches cause shell errors between AI coding tools. The solution creates a unified virtual environment configuration with proper Python 3.11.6 setup and eliminates conflicting system Python aliases.

## 🔧 IMPLEMENTATION REQUIREMENTS

### 1. CREATE VIRTUAL ENVIRONMENT ACTIVATION SCRIPT
Create file: `activate_sophia_env.sh`
```bash
#!/bin/bash
# 🚀 Sophia AI Environment Activation Script
# Ensures consistent Python 3.11.6 virtual environment across ALL AI coding tools

echo "🚀 Activating Sophia AI Environment..."

# Remove problematic Python aliases that conflict with virtual environment
unalias python 2>/dev/null || true
unalias python3 2>/dev/null || true

# Activate virtual environment
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
    echo "✅ Virtual environment activated"
else
    echo "❌ Virtual environment not found. Creating..."
    python3.11 -m venv .venv
    source .venv/bin/activate
    echo "✅ Virtual environment created and activated"
fi

# Verify Python version
PYTHON_VERSION=$(python --version 2>&1)
echo "🐍 Python version: $PYTHON_VERSION"

# Verify virtual environment path
PYTHON_PATH=$(which python)
echo "📍 Python path: $PYTHON_PATH"

# Verify virtual environment is active
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "🔧 Virtual environment: $VIRTUAL_ENV"
    echo "✅ Environment properly activated"
else
    echo "❌ Virtual environment not properly activated"
    exit 1
fi

# Install/upgrade core packages if needed
echo "📦 Checking core packages..."
pip install --upgrade pip fastapi uvicorn redis sqlalchemy python-dotenv > /dev/null 2>&1

# Load Sophia-specific environment variables
if [ -f ".sophia-env-config" ]; then
    source .sophia-env-config
    echo "⚙️ Sophia environment config loaded"
fi

# Create helpful shortcuts
alias run-working='python -m uvicorn backend.app.working_fastapi:app --host 0.0.0.0 --port 8000'
alias run-simple='python -m uvicorn backend.app.simple_fastapi:app --host 0.0.0.0 --port 8001'
alias run-minimal='python -m uvicorn backend.app.minimal_fastapi:app --host 0.0.0.0 --port 8002'
alias run-distributed='python -m uvicorn api.main:app --host 0.0.0.0 --port 8003'
alias check-env='echo "Python: $(python --version)" && echo "Path: $(which python)" && echo "Env: $VIRTUAL_ENV"'

echo "🎯 FastAPI Applications Available:"
echo "   - Working App (port 8000): run-working"
echo "   - Simple App (port 8001): run-simple"
echo "   - Minimal App (port 8002): run-minimal"
echo "   - Distributed App (port 8003): run-distributed"
echo "   - Environment Check: check-env"

echo ""
echo "✅ Sophia AI Environment Ready!"
echo "💡 Use 'check-env' to verify setup anytime"
```

### 2. CREATE ENVIRONMENT CONFIGURATION FILE
Create file: `.sophia-env-config`
```bash
# 🔧 Sophia AI Environment Configuration
# Loaded automatically by activate_sophia_env.sh

# Environment Settings
export ENVIRONMENT="prod"
export PULUMI_ORG="scoobyjava-org"

# FastAPI Settings
export FASTAPI_ENV="production"
export LOG_LEVEL="info"

# Development Settings
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
export PYTHONDONTWRITEBYTECODE=1

# Troubleshooting Information
export SOPHIA_TROUBLESHOOTING="
🔧 TROUBLESHOOTING GUIDE:
1. Shell errors? Run: source activate_sophia_env.sh
2. Wrong Python? Check: which python (should be .venv/bin/python)
3. Import errors? Verify: python --version (should be 3.11.6)
4. Environment issues? Run: check-env
5. Need help? Check: VIRTUAL_ENVIRONMENT_CONSISTENCY_GUIDE.md
"

echo "📋 Environment variables loaded for Sophia AI"
```

### 3. UPDATE .CURSORRULES FILE
Add this section to your `.cursorrules` file (or create it):
```
## 🐍 **VIRTUAL ENVIRONMENT CONSISTENCY (MANDATORY)**

**CRITICAL FOR ALL AI CODING TOOLS (Cursor, Cline, GitHub Copilot, etc.)**

### **REQUIRED SETUP FOR EVERY SESSION:**
```bash
# ALWAYS START ANY AI CODING SESSION WITH:
source activate_sophia_env.sh
```

### **Environment Requirements (NON-NEGOTIABLE):**
1. **Python Version:** MUST use Python 3.11.6 from virtual environment
2. **Virtual Environment:** MUST be activated before any Python operations
3. **Python Command:** Use `python` (not `python3` or system Python)
4. **Environment Verification:** Look for `(.venv)` in shell prompt

### **FORBIDDEN ACTIONS:**
- ❌ **NEVER use system Python** (`/usr/bin/python3`)
- ❌ **NEVER skip virtual environment activation**
- ❌ **NEVER use `python3` command directly**
- ❌ **NEVER install packages without activated environment**

### **Required Verification Before Coding:**
```bash
# 1. Check environment is active
echo $VIRTUAL_ENV  # Should show: /path/to/project/.venv

# 2. Verify Python version
python --version   # Should show: Python 3.11.6

# 3. Verify Python location
which python      # Should show: /path/to/project/.venv/bin/python

# 4. Quick environment check
check-env         # Available after activation
```

### **Available FastAPI Applications (All ports aligned):**
- **Working FastAPI**: `run-working` → port 8000
- **Simple FastAPI**: `run-simple` → port 8001  
- **Minimal FastAPI**: `run-minimal` → port 8002
- **Distributed API**: `run-distributed` → port 8003

### **Troubleshooting:**
- **Import Errors**: Run `source activate_sophia_env.sh`
- **Wrong Python Version**: Ensure virtual environment is properly activated
- **Shell Errors**: Check that `(.venv)` appears in prompt
- **Reference**: See `VIRTUAL_ENVIRONMENT_CONSISTENCY_GUIDE.md`

**WHY THIS MATTERS:** Prevents shell errors between AI tools, ensures package consistency, eliminates import conflicts, and maintains stable development environment across all AI assistants.
```

### 4. CREATE CURSOR-SPECIFIC RULES
Create file: `.cursor-rules`
```markdown
# 🎯 CURSOR AI SPECIFIC VIRTUAL ENVIRONMENT RULES

## MANDATORY STARTUP SEQUENCE
1. **ALWAYS** run: `source activate_sophia_env.sh`
2. **VERIFY** (.venv) appears in terminal prompt
3. **CHECK** Python version: `python --version` → Should be 3.11.6
4. **CONFIRM** Python path: `which python` → Should be `.venv/bin/python`

## CURSOR AI INTEGRATION
- Use integrated terminal for all Python operations
- Virtual environment auto-activates with shortcuts
- All FastAPI apps available via shortcuts (run-working, run-simple, etc.)

## TROUBLESHOOTING FOR CURSOR
- **Terminal not showing (.venv)?** → Run activation script again
- **Import errors?** → Verify virtual environment is active
- **Wrong Python version?** → Check system Python aliases in ~/.zshrc
- **Package not found?** → Ensure pip install runs in virtual environment

## BEST PRACTICES
- Keep activation script open in terminal for reference
- Use shortcuts for FastAPI applications
- Always verify environment before coding
- Check documentation if issues persist
```

### 5. CREATE CLINE-SPECIFIC RULES  
Create file: `.cline-rules`
```markdown
# 🤖 CLINE AI ASSISTANT VIRTUAL ENVIRONMENT RULES

## CRITICAL STARTUP FOR CLINE
**FIRST COMMAND EVERY SESSION:**
```bash
source activate_sophia_env.sh && check-env
```

## CLINE TERMINAL BEST PRACTICES
- **Terminal Focus**: Cline works primarily through terminal commands
- **Environment Verification**: Always check (.venv) in prompt before operations
- **Command Verification**: Use `check-env` to verify setup
- **Shortcuts**: Use provided shortcuts (run-working, run-simple, etc.)

## CLINE-SPECIFIC TROUBLESHOOTING
- **Commands failing?** → Ensure virtual environment is active
- **Python not found?** → Run activation script
- **Package issues?** → Verify pip is from virtual environment
- **Shell errors?** → Check for conflicting Python aliases

## INTEGRATION WITH SOPHIA AI
- All FastAPI applications available via shortcuts
- Environment automatically configured for Sophia AI development
- Comprehensive error handling and recovery
- Full documentation available in guide files
```

### 6. CREATE UNIVERSAL AI ASSISTANT RULES
Create file: `.ai-assistant-rules`
```markdown
# 🤖 UNIVERSAL AI CODING ASSISTANT ENVIRONMENT GUIDE

## FOR ANY AI CODING TOOL (Cursor, Cline, GitHub Copilot, etc.)

### MANDATORY FIRST STEP
```bash
source activate_sophia_env.sh
```

### VERIFICATION CHECKLIST
- [ ] (.venv) visible in terminal prompt
- [ ] `python --version` returns Python 3.11.6
- [ ] `which python` points to `.venv/bin/python`
- [ ] `echo $VIRTUAL_ENV` shows correct path

### AVAILABLE COMMANDS
- `run-working` → Start Working FastAPI (port 8000)
- `run-simple` → Start Simple FastAPI (port 8001)
- `run-minimal` → Start Minimal FastAPI (port 8002)
- `run-distributed` → Start Distributed API (port 8003)
- `check-env` → Verify environment setup

### TOOL-SPECIFIC NOTES
- **Cursor AI**: Use integrated terminal, virtual environment auto-integrates
- **Cline**: Terminal-focused, always verify environment first
- **GitHub Copilot**: Works with any environment, ensure correct Python path
- **Other Tools**: Follow universal setup, refer to documentation

### EMERGENCY RECOVERY
If anything breaks:
1. Run: `source activate_sophia_env.sh`
2. Verify: `check-env`
3. Check: Documentation in `VIRTUAL_ENVIRONMENT_CONSISTENCY_GUIDE.md`
4. Reset: Delete `.venv` and re-run activation script
```

### 7. FIX FASTAPI APPLICATIONS

#### Fix Simple FastAPI (backend/app/simple_fastapi.py) - Line 62 IndentationError
Find line 62 and ensure proper indentation:
```python
        logger.info("✅ Qdrant memory service initialized")
```

#### Verify Minimal FastAPI (backend/app/minimal_fastapi.py) exists and works

#### Verify Working FastAPI (backend/app/working_fastapi.py) exists and works

#### Verify Distributed API (api/main.py) exists and works

### 8. CREATE DOCUMENTATION
Create file: `VIRTUAL_ENVIRONMENT_CONSISTENCY_GUIDE.md`
```markdown
# 🔧 Virtual Environment Consistency Guide

## Root Cause Analysis
**PROBLEM**: Shell errors when switching between AI coding tools due to Python environment mismatches.

**ROOT CAUSE**: System Python (3.9.6) vs Virtual Environment Python (3.11.6) conflicts caused by shell aliases.

## Solution Implemented
1. **Activation Script**: `activate_sophia_env.sh` removes conflicting aliases and properly activates environment
2. **Configuration File**: `.sophia-env-config` sets consistent environment variables
3. **AI Tool Rules**: Tool-specific configuration files for Cursor, Cline, and universal AI assistants
4. **FastAPI Alignment**: Four aligned applications with consistent patterns

## Verification Process
```bash
# 1. Activate environment
source activate_sophia_env.sh

# 2. Verify setup
check-env

# 3. Test FastAPI apps
run-working  # Should start on port 8000
run-simple   # Should start on port 8001
run-minimal  # Should start on port 8002
run-distributed # Should start on port 8003
```

## Expected Output
```
(.venv) user@machine project %
Python: Python 3.11.6
Path: /path/to/project/.venv/bin/python
Env: /path/to/project/.venv
```

## Troubleshooting
- **No (.venv) in prompt**: Re-run activation script
- **Wrong Python version**: Check for system aliases in shell config
- **Import errors**: Verify virtual environment activation
- **Shell errors**: Clear Python aliases and restart terminal

## Business Value
- **Development Efficiency**: Consistent environment across all AI tools
- **Error Prevention**: Eliminates shell errors between tool switches
- **Package Consistency**: Ensures correct Python and package versions
- **Operational Excellence**: Reliable development environment
```

## 🚀 EXECUTION STEPS

1. **Run the activation script**: `chmod +x activate_sophia_env.sh && source activate_sophia_env.sh`

2. **Verify setup**: `check-env`

3. **Test FastAPI applications**:
   ```bash
   run-working    # Test port 8000
   run-simple     # Test port 8001  
   run-minimal    # Test port 8002
   run-distributed # Test port 8003
   ```

4. **Verify AI tool integration**: Check that all rule files are created and environment works consistently

## ✅ SUCCESS CRITERIA
- (.venv) appears in terminal prompt
- Python 3.11.6 from virtual environment
- All four FastAPI applications start without errors
- Environment consistent across AI coding tools
- No shell errors when switching between tools

## 🆘 EMERGENCY RECOVERY
If anything goes wrong:
```bash
# Reset everything
rm -rf .venv
source activate_sophia_env.sh
check-env
```

---

**COPY THIS ENTIRE PROMPT TO CURSOR AI ON YOUR NEW MACHINE FOR IDENTICAL SETUP** 