# 🚀 Getting Started with Sophia AI

> **Enterprise AI Orchestrator for Pay Ready** - Modern development setup with UV package management

## 📋 **Prerequisites**

- **Python 3.12+** (specified in `.python-version`)
- **UV Package Manager** (modern, 6x faster than pip)
- **Git** with access to `ai-cherry/sophia-main` repository
- **Terminal** with shell access (zsh/bash)

## ⚡ **Quick Start (2 minutes)**

### **1. Clone and Navigate**
```bash
git clone https://github.com/ai-cherry/sophia-main.git
cd sophia-main
```

### **2. Verify Workspace**
```bash
# Use our automated verification system
verify-sophia
```

If the command isn't available, run:
```bash
python scripts/verify_workspace.py
```

### **3. Install Dependencies (UV)**
```bash
# Install all 231 packages in under 1 second
uv sync

# Verify installation
uv --version  # Should show: uv 0.7.16+
```

### **4. Activate Environment**
```bash
# Use our convenience alias
go-sophia

# Or manually
source .venv/bin/activate
```

### **5. Verify Everything Works**
```bash
# Run comprehensive verification
ready-to-code

# Test FastAPI application
python -c "from backend.app.fastapi_app import app; print('✅ All systems operational')"
```

## 🎯 **Development Workflow**

### **Daily Commands**
```bash
verify-sophia           # Always start here
uv sync                # Update dependencies  
uv run pytest          # Run tests
uv add package-name     # Add new packages
```

### **Running the Application**
```bash
# Start FastAPI backend
uv run uvicorn backend.app.fastapi_app:app --reload --port 8000

# In another terminal, start frontend (if needed)
cd frontend && npm run dev
```

### **Code Quality**
```bash
# Format code (Black + Ruff)
uv run ruff format .
uv run ruff check . --fix

# Type checking
uv run mypy backend/
```

## 🔧 **IDE Setup**

### **Cursor IDE (Recommended)**
1. Open project: `cursor ~/sophia-main`
2. Cursor will automatically use `.cursorrules` (1117 lines of configuration)
3. MCP servers will auto-configure for AI assistance

### **VS Code**
1. Install Python extension
2. Select interpreter: `~/sophia-main/.venv/bin/python`
3. Configure workspace settings from `.vscode/settings.json`

## 🧠 **Understanding the Architecture**

### **Project Structure**
```
sophia-main/
├── backend/           # FastAPI backend (35+ API routes)
├── frontend/          # React frontend
├── mcp-servers/       # 23 MCP servers for AI integration
├── infrastructure/    # Pulumi infrastructure as code
├── scripts/          # 118+ utility scripts
├── pyproject.toml    # UV configuration (231 packages)
└── uv.lock          # Locked dependencies (522KB)
```

### **Key Systems**
- **UV Package Management:** 6x faster than pip
- **Secret Management:** GitHub Org → Pulumi ESC → Backend
- **MCP Integration:** AI Memory, Codacy, Linear, Asana servers
- **Clean Architecture:** Domain-driven design patterns

## 🚨 **Troubleshooting**

### **Common Issues**

| Problem | Solution | Verification |
|---------|----------|-------------|
| Wrong directory | `go-sophia` | `verify-sophia` |
| Import errors | `uv sync` | `python -c "import backend"` |
| Environment issues | `source .venv/bin/activate` | `echo $VIRTUAL_ENV` |
| Package problems | `uv sync --force` | `uv --version` |

### **Emergency Recovery**
```bash
# Nuclear option - reset everything
cd ~/sophia-main
rm -rf .venv
uv sync
source .venv/bin/activate
verify-sophia
```

## 📚 **Next Steps**

### **For New Developers**
1. Read **[WORKSPACE_VERIFICATION_GUIDE.md](../../WORKSPACE_VERIFICATION_GUIDE.md)**
2. Review **[.cursorrules](../../.cursorrules)** for development patterns
3. Explore **[backend/](../../backend/)** for API structure
4. Check **[mcp-servers/](../../mcp-servers/)** for AI integration

### **For AI Tool Users**
1. Configure your AI tool with workspace verification
2. Use `verify-sophia` before every coding session
3. Follow environment policies in `.cursorrules`
4. Leverage MCP servers for enhanced capabilities

### **For Contributors**
1. Always run `verify-sophia` before committing
2. Use UV for all package management
3. Follow clean architecture patterns
4. Test with `uv run pytest`

## 🎉 **Success Metrics**

You're ready when you see:
```bash
$ verify-sophia
🎉 WORKSPACE VERIFICATION: ✅ PERFECT!
🚀 Ready for Sophia AI development!

$ python -c "from backend.app.fastapi_app import app; print('Success!')"
Success!
```

## Remote Deployment

For one-click deployment on Lambda Labs, see the [Lambda Labs Quick Deployment Guide](../04-deployment/LAMBDA_LABS_DEPLOYMENT_GUIDE.md).

---

**🚀 Welcome to the future of AI development with Sophia AI!**

**💡 Remember: Use `verify-sophia` whenever you're unsure about your environment**
