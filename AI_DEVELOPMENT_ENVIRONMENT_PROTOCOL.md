# AI Development Environment Protocol for Sophia AI

## 🎯 For AI Assistants Working on Sophia AI

### ALWAYS Start With:
```bash
cd ~/sophia-main
source .venv/bin/activate
```

### Required Environment Variables:
```bash
export ENVIRONMENT="prod"
export PULUMI_ORG="scoobyjava-org"
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Before Any Python Work:
1. Verify you're in the correct directory: `pwd` should show `/Users/lynnmusil/sophia-main`
2. Check virtual environment is active: `which python` should show `.venv/bin/python`
3. Test backend import: `python -c "import backend"`

### Key Directories:
- **Backend Code**: `backend/`
- **MCP Servers**: `mcp-servers/`
- **Scripts**: `scripts/`
- **Frontend**: `frontend/`
- **Infrastructure**: `infrastructure/`

### Important Rules:
1. **NEVER** use relative imports outside the project structure
2. **ALWAYS** ensure PYTHONPATH includes the project root
3. **NEVER** default to staging environment - always use "prod"
4. **ALWAYS** use the virtual environment for Python operations
5. **NEVER** install packages globally - use the venv

### Common Tasks:

#### Running Scripts:
```bash
cd ~/sophia-main
source .venv/bin/activate
python scripts/[script_name].py
```

#### Starting MCP Servers:
```bash
cd ~/sophia-main
source .venv/bin/activate
python scripts/start_mcp_servers.py
```

#### Testing Code:
```bash
cd ~/sophia-main
source .venv/bin/activate
python -m pytest tests/
```

### When Working with Files:
- Always use absolute paths from project root
- Never assume current directory without checking
- Always ensure backend module is importable

### Common Issues and Solutions:

#### ModuleNotFoundError: No module named 'backend'
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

#### Permission denied errors:
```bash
chmod +x scripts/*.py
chmod +x scripts/*.sh
```

#### Virtual environment not activated:
```bash
source .venv/bin/activate
```

### Essential Commands Reference:
```bash
# Full environment setup
cd ~/sophia-main
source .venv/bin/activate
export ENVIRONMENT="prod"
export PULUMI_ORG="scoobyjava-org"
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Quick verification
python -c "import backend; print('Environment ready!')"
```

### 🚨 Critical Reminders:
- **ENVIRONMENT must be "prod"** - Never use staging
- **Virtual environment is mandatory** - Never use system Python
- **PYTHONPATH must include project root** - For module imports
- **Always verify setup before running scripts**

### For VSCode Settings:
The project includes `.vscode/settings.json` with proper Python interpreter path.
Ensure VSCode uses the virtual environment interpreter.

---

**Remember**: Every new terminal session requires environment activation!
