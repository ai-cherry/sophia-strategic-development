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
    echo "❌ VIRTUAL ENV NOT ACTIVATED"
    echo "🔧 FIXING: source .venv/bin/activate"
    source .venv/bin/activate
fi

# 3. Environment Variables Check
if [ "$ENVIRONMENT" != "prod" ]; then
    echo "❌ WRONG ENVIRONMENT: $ENVIRONMENT"
    echo "🔧 FIXING: export ENVIRONMENT=prod"
    export ENVIRONMENT=prod
fi

# 4. Pulumi Org Check
if [ "$PULUMI_ORG" != "scoobyjava-org" ]; then
    echo "❌ WRONG PULUMI ORG: $PULUMI_ORG"
    echo "🔧 FIXING: export PULUMI_ORG=scoobyjava-org"
    export PULUMI_ORG=scoobyjava-org
fi

echo "✅ Environment validated successfully"
```

### **Documentation Check**
Before creating new documentation:

1. **Check [SOPHIA_AI_DOCUMENTATION_MASTER_INDEX.md](SOPHIA_AI_DOCUMENTATION_MASTER_INDEX.md)**
2. **Verify if similar documentation already exists**
3. **Update existing documentation rather than creating new files**
4. **Follow established naming conventions**

## 🛡️ **ENVIRONMENT PROTECTION RULES**

### **Rule 1: Never Break the Environment**
- NEVER change the working directory without restoring it
- NEVER deactivate the virtual environment
- NEVER modify core environment variables
- ALWAYS restore environment state after operations

### **Rule 2: Use Safe Import Patterns**
```python
# ✅ CORRECT - Module import pattern
python -m backend.app.script_name

# ❌ WRONG - Direct script execution (causes import chain issues)
python backend/app/script_name.py
```

### **Rule 3: Handle Import Errors Gracefully**
```python
# ✅ CORRECT - Graceful handling
try:
    from backend.core.optimized_connection_manager import connection_manager
except ImportError as e:
    print(f"Optional dependency not available: {e}")
    # Continue with fallback behavior
```

### **Rule 4: Respect MCP Server Ports**
- ALWAYS check [config/mcp_ports.json](config/mcp_ports.json) for port assignments
- NEVER hardcode port numbers
- ALWAYS use the centralized port configuration

## 📋 **CODING STANDARDS COMPLIANCE**

### **Python Development**
- **Type hints**: Required for all functions
- **Docstrings**: Required for all classes and methods
- **Error handling**: Comprehensive try/catch blocks
- **Async patterns**: Use async/await for I/O operations
- **Import organization**: Follow established patterns

### **Secret Management**
```python
# ✅ CORRECT - Use centralized config
from backend.core.auto_esc_config import get_config_value
api_key = get_config_value("openai_api_key")

# ❌ WRONG - Direct environment access
import os
api_key = os.getenv("OPENAI_API_KEY")
```

### **Configuration Patterns**
```python
# ✅ CORRECT - Production-first default
ENVIRONMENT = os.getenv("ENVIRONMENT", "prod")

# ❌ WRONG - Staging default
ENVIRONMENT = os.getenv("ENVIRONMENT", "staging")
```

## 🔄 **WORKFLOW INTEGRATION**

### **AI Memory Integration**
All AI tools should:
1. **Store important decisions** in AI Memory
2. **Recall previous patterns** before implementing new solutions
3. **Update memory** with new learnings
4. **Cross-reference** similar implementations

### **Code Quality Integration**
Before committing code:
1. **Run Codacy analysis** if available
2. **Check for security vulnerabilities**
3. **Validate performance patterns**
4. **Ensure documentation is updated**

## 🚨 **EMERGENCY RECOVERY PROCEDURES**

### **If Environment is Disrupted**
```bash
# Immediate recovery
./restore_sophia_env.sh

# Or manual recovery
cd ~/sophia-main
source .venv/bin/activate
export ENVIRONMENT=prod
export PULUMI_ORG=scoobyjava-org
```

### **If Import Errors Occur**
1. **Check if it's expected** (aiomysql, optional dependencies)
2. **Use module import pattern** instead of direct execution
3. **Check virtual environment activation**
4. **Verify Python path**

### **If Documentation is Inconsistent**
1. **Refer to master index** for current documentation
2. **Update existing documentation** rather than creating new
3. **Validate against current codebase state**
4. **Follow established patterns**

## 📊 **COMPLIANCE MONITORING**

### **Automated Checks**
```python
# Example compliance check
def validate_ai_tool_compliance():
    """Validate that AI tool is following the protocol"""
    checks = {
        "directory": os.getcwd() == "/Users/lynnmusil/sophia-main",
        "virtual_env": os.getenv("VIRTUAL_ENV") == "/Users/lynnmusil/sophia-main/.venv",
        "environment": os.getenv("ENVIRONMENT") == "prod",
        "pulumi_org": os.getenv("PULUMI_ORG") == "scoobyjava-org"
    }
    
    failed_checks = [check for check, passed in checks.items() if not passed]
    
    if failed_checks:
        print(f"❌ Compliance failures: {failed_checks}")
        return False
    
    print("✅ AI tool compliance validated")
    return True
```

### **Success Metrics**
- **Environment Stability**: 99%+ successful operations
- **Documentation Consistency**: No conflicting information
- **Code Quality**: All standards followed
- **Performance**: No degradation from tool usage

## 🔧 **TOOL-SPECIFIC GUIDELINES**

### **Cursor AI**
- Follows `.cursorrules` configuration
- Uses MCP server integration
- Maintains environment through session

### **Cline v3.18**
- Follows `config/cline_v3_18_config.json`
- Uses enhanced features (Claude 4, Gemini CLI, WebFetch)
- Integrates with AI Memory and Codacy

### **Other AI Tools**
- Must implement equivalent environment validation
- Should follow the same coding standards
- Must respect the documentation hierarchy

## 📈 **CONTINUOUS IMPROVEMENT**

### **Protocol Updates**
- This protocol evolves with the codebase
- All AI tools must adapt to protocol changes
- Regular validation of protocol effectiveness

### **Feedback Loop**
- AI tools should report protocol violations
- Successful patterns should be documented
- Failed patterns should trigger protocol updates

## 🎯 **IMPLEMENTATION CHECKLIST**

For any AI tool working on Sophia AI:

- [ ] Environment validation implemented
- [ ] Safe import patterns used
- [ ] Documentation hierarchy respected
- [ ] Secret management compliance
- [ ] MCP server port compliance
- [ ] Emergency recovery procedures known
- [ ] Compliance monitoring active
- [ ] Tool-specific guidelines followed

---

**🤖 This protocol ensures that all AI tools work harmoniously on Sophia AI while maintaining environment stability and code quality.** 