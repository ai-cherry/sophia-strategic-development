# Cursor AI Coding Setup & Virtual Environment Fix

## Problem: Cursor AI Kicks You Out of Virtual Environment

Cursor IDE has a known issue where it constantly switches between virtual environment and system Python, causing import errors and package conflicts.

## Generic Solution (Works for Any Project)

### 1. Cursor Settings Configuration

Create `.vscode/settings.json` in your project root:

```json
{
    "python.defaultInterpreterPath": "./.venv/bin/python",
    "python.terminal.activateEnvironment": true,
    "python.terminal.activateEnvInCurrentTerminal": true,
    "terminal.integrated.env.osx": {
        "VIRTUAL_ENV": "${workspaceFolder}/.venv",
        "PATH": "${workspaceFolder}/.venv/bin:${env:PATH}",
        "PYTHONPATH": "${workspaceFolder}"
    },
    "terminal.integrated.shellIntegration.enabled": true,
    "terminal.integrated.profiles.osx": {
        "Auto-VEnv": {
            "path": "/bin/zsh",
            "args": ["-c", "if [ -f '${workspaceFolder}/.venv/bin/activate' ]; then source '${workspaceFolder}/.venv/bin/activate' && echo '🚀 Virtual environment activated'; fi && exec zsh"]
        }
    },
    "terminal.integrated.defaultProfile.osx": "Auto-VEnv"
}
```

### 2. Shell Profile Auto-Activation

Add to your `~/.zshrc` (or `~/.bashrc`):

```bash
# Generic auto-activation for any Python project with .venv
auto_activate_venv() {
    if [[ -f ".venv/bin/activate" ]] && [[ "$VIRTUAL_ENV" == "" ]]; then
        source .venv/bin/activate
        echo "🚀 Auto-activated virtual environment in $(basename "$PWD")"
    fi
}

# Override cd to auto-activate venv
cd() {
    builtin cd "$@"
    auto_activate_venv
}

# Auto-activate when shell starts
auto_activate_venv
```

### 3. Quick Activation Script

Use the included `activate_env.sh` script:

```bash
# Make executable
chmod +x activate_env.sh

# Activate environment
source activate_env.sh
```

### 4. Environment Variables

Create `.env` file for project-specific variables:

```bash
# Copy template and customize
cp .env.template .env
# Edit .env with your specific configuration
```

## Cline Integration for Enhanced AI Coding

For even more powerful AI assistance, consider integrating **Cline** (the in-editor AI command line) with your development workflow.

### What is Cline?

Cline is a VSCode extension that provides conversational AI assistance directly in your editor. It can:

- Understand your entire codebase through knowledge graphs
- Connect to multiple MCP servers for specialized functionality
- Provide contextual code analysis and suggestions
- Integrate with remote infrastructure tools

### Setting Up Cline

For detailed Cline setup instructions, see: [Cline & Cognee Setup Guide](./CLINE_AND_COGNEE_SETUP_GUIDE.md)

**Quick Overview:**

1. **Install Cline Extension** in VSCode
2. **Configure MCP Servers** in `cline_mcp_settings.json`:
   ```json
   {
     "mcpServers": {
       "ai_memory": {
         "url": "http://localhost:9000",
         "description": "AI Memory for persistent context"
       },
       "codacy": {
         "url": "http://localhost:3008",
         "description": "Code quality analysis"
       }
     }
   }
   ```
3. **Launch VSCode with Environment**:
   ```bash
   source .venv/bin/activate
   export $(cat .env | xargs) 2>/dev/null || true
   code .
   ```

### Cline + Virtual Environment Best Practices

- Always launch VSCode from an activated virtual environment
- Use the generic activation scripts before starting Cline
- Configure Cline to use local MCP servers that respect your virtual environment
- Test MCP server connectivity after virtual environment changes

## AI Memory MCP Integration for Coders

### Using AI Memory in Cursor

The AI Memory MCP server helps AI assistants remember important coding decisions and patterns across sessions.

#### Natural Language Commands:

```bash
# Store important decisions
@ai_memory store this conversation about database architecture

# Recall past decisions
@ai_memory recall "how we decided to handle authentication"

# Auto-store with categories
@ai_memory auto_store_conversation "Fixed aioredis Python 3.11 compatibility"

# Get coding tips
@ai_memory get_ai_coding_tips "async python patterns"
```

#### Pre-loaded Knowledge Base:

The AI Memory MCP comes with pre-loaded coding knowledge:

- **Python 3.11 Compatibility**: Redis patterns, async/await best practices
- **FastAPI Patterns**: Lifespan context managers, deprecation fixes
- **OpenAI Integration**: Embedding best practices, rate limiting
- **Vector Databases**: Pinecone patterns, metadata handling
- **Security Patterns**: API key management, environment variables
- **Error Handling**: Retry logic, circuit breakers, logging patterns
- **Cursor Virtual Environment Fix**: Solutions for IDE environment switching

#### Integration with Development Workflow:

1. **Architecture Decisions**: Automatically categorized and stored
2. **Bug Solutions**: Searchable by error patterns and solutions
3. **Performance Tips**: Optimization patterns and bottleneck solutions
4. **Security Patterns**: Best practices for secure coding
5. **IDE Issues**: Solutions for common development environment problems

### MCP Server Health Check

```bash
# Check if AI Memory MCP is running
curl -X GET "http://localhost:9000/health"

# Expected response:
{
    "status": "healthy",
    "openai_available": true,
    "pinecone_available": true,
    "memory_count": 150
}
```

## Troubleshooting

### Virtual Environment Issues:

1. **Check if venv exists**: `ls -la .venv/`
2. **Recreate if needed**: `python3 -m venv .venv`
3. **Install requirements**: `pip install -r requirements.txt`
4. **Restart Cursor**: Close and reopen Cursor IDE

### Import Errors:

1. **Check Python path**: `which python` (should show .venv path)
2. **Check PYTHONPATH**: `echo $PYTHONPATH`
3. **Clear Python cache**: `find . -name "*.pyc" -delete`

### MCP Server Issues:

1. **Check server status**: `ps aux | grep mcp_server`
2. **Check logs**: Look for import errors or port conflicts
3. **Restart server**: Kill existing processes and restart

### Cline Integration Issues:

1. **Verify MCP server URLs**: Check that servers are accessible
2. **Check environment variables**: Ensure all required vars are loaded
3. **Restart Cline**: Use Command Palette > "Cline: Restart"
4. **Check virtual environment**: Ensure Cline is using the correct Python

## Best Practices

1. **Always use virtual environments** for Python projects
2. **Store important decisions** in AI Memory for future reference
3. **Use consistent naming** for environment variables
4. **Test imports** after environment changes
5. **Keep documentation updated** with AI Memory integration
6. **Launch VSCode from activated virtual environment** for Cline compatibility
7. **Use generic configuration files** that work across different projects

## Memory Integration Tips

- Use descriptive categories when storing memories
- Include relevant tags for better searchability
- Store both successful solutions AND failed attempts
- Regularly query past decisions before making new ones
- Use auto-store for important conversations with AI assistants
- Store IDE configuration solutions for team knowledge sharing

This setup ensures consistent virtual environment activation and provides AI assistants with persistent memory across coding sessions, whether using Cursor alone or with Cline integration.
