# Sophia AI Master Environment Guide

## 🚀 Quick Fix for Shell Integration Issues

### Problem: "Shell Integration Unavailable" in Cline
This happens when VSCode can't properly integrate with your shell or when the environment isn't properly activated.

## 🔧 Solution 1: Update VSCode Settings

1. **Update VSCode Terminal Settings**
   - Press `CMD + Shift + P`
   - Type "Preferences: Open Settings (JSON)"
   - Add these settings:

```json
{
  "terminal.integrated.defaultProfile.osx": "zsh",
  "terminal.integrated.profiles.osx": {
    "zsh": {
      "path": "/bin/zsh",
      "args": ["-l"],
      "env": {
        "PYTHONPATH": "${workspaceFolder}",
        "SOPHIA_HOME": "${workspaceFolder}"
      }
    }
  },
  "terminal.integrated.shellIntegration.enabled": true,
  "terminal.integrated.env.osx": {
    "PYTHONPATH": "${workspaceFolder}",
    "SOPHIA_HOME": "${workspaceFolder}"
  },
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
  "python.terminal.activateEnvironment": true,
  "python.terminal.activateEnvInCurrentTerminal": true
}
```

## 🔧 Solution 2: Auto-Environment Activation

### Step 1: Add to your shell configuration (~/.zshrc or ~/.bashrc)

```bash
# Sophia AI Environment Auto-Activation
export SOPHIA_HOME="$HOME/sophia-main"

# Function to activate Sophia environment
activate_sophia() {
    if [[ -f "$SOPHIA_HOME/.venv/bin/activate" ]]; then
        source "$SOPHIA_HOME/.venv/bin/activate"
        export PYTHONPATH="$SOPHIA_HOME:$PYTHONPATH"
        export ENVIRONMENT="prod"
        export PULUMI_ORG="scoobyjava-org"
        echo "✅ Sophia AI environment activated!"
    else
        echo "❌ Sophia virtual environment not found at $SOPHIA_HOME/.venv"
        echo "💡 Run: cd $SOPHIA_HOME && python -m venv .venv"
    fi
}

# Auto-activate when entering Sophia directory
cd() {
    builtin cd "$@"
    if [[ "$PWD" == "$SOPHIA_HOME"* ]] && [[ -z "$VIRTUAL_ENV" ]]; then
        activate_sophia
    fi
}

# Aliases for quick access
alias sophia="cd $SOPHIA_HOME && activate_sophia"
alias sophia-check="cd $SOPHIA_HOME && python backend/scripts/check_environment_health.py"
alias sophia-backend="cd $SOPHIA_HOME && activate_sophia && python start_backend_services.py"
alias sophia-mcp="cd $SOPHIA_HOME && activate_sophia && python start_mcp_servers.py"
alias sophia-test="cd $SOPHIA_HOME && activate_sophia && pytest"
```

### Step 2: Apply the configuration

```bash
# For Zsh
source ~/.zshrc

# For Bash
source ~/.bashrc
```

## 🔧 Solution 3: VSCode Workspace Settings

Create/update `.vscode/settings.json` in your project:

```json
{
  "terminal.integrated.defaultProfile.osx": "zsh",
  "terminal.integrated.shellIntegration.enabled": true,
  "python.defaultInterpreterPath": ".venv/bin/python",
  "python.terminal.activateEnvironment": true,
  "terminal.integrated.env.osx": {
    "PYTHONPATH": "${workspaceFolder}",
    "ENVIRONMENT": "prod",
    "PULUMI_ORG": "scoobyjava-org"
  }
}
```

## 🔧 Solution 4: Cline-Specific Configuration

### Create a .envrc file in the project root:

```bash
# .envrc - direnv configuration for automatic environment activation
export SOPHIA_HOME="$(pwd)"
export VIRTUAL_ENV="$SOPHIA_HOME/.venv"
export PATH="$VIRTUAL_ENV/bin:$PATH"
export PYTHONPATH="$SOPHIA_HOME:$PYTHONPATH"
export ENVIRONMENT="prod"
export PULUMI_ORG="scoobyjava-org"

# Activate virtual environment if it exists
if [[ -f "$VIRTUAL_ENV/bin/activate" ]]; then
    source "$VIRTUAL_ENV/bin/activate"
fi
```

Then install direnv (if not already installed):
```bash
brew install direnv
echo 'eval "$(direnv hook zsh)"' >> ~/.zshrc  # For Zsh
echo 'eval "$(direnv hook bash)"' >> ~/.bashrc  # For Bash
direnv allow .
```

## 🚨 Quick Troubleshooting

### If you see "Shell Integration Unavailable":

1. **Restart VSCode Terminal**
   - Kill all terminals: `CMD + Shift + P` → "Terminal: Kill All Terminals"
   - Open new terminal: `` CMD + ` ``

2. **Force Shell Reload**
   ```bash
   exec $SHELL -l
   ```

3. **Verify Shell Type**
   ```bash
   echo $SHELL
   # Should output: /bin/zsh or /bin/bash
   ```

4. **Check Shell Integration**
   ```bash
   # In VSCode terminal
   echo $TERM_PROGRAM
   # Should output: vscode
   ```

## 🎯 Best Practices for Cline

1. **Always start Cline from within VSCode** with the Sophia project open
2. **Ensure terminal is using the correct shell profile** (zsh/bash)
3. **Keep VSCode updated** to the latest version
4. **Use the integrated terminal** rather than external terminals

## 🔄 Environment Health Check

Run this command to verify everything is set up correctly:

```bash
cd ~/sophia-main && \
source .venv/bin/activate && \
python -c "
import sys
import os
print('✅ Python:', sys.executable)
print('✅ PYTHONPATH:', os.environ.get('PYTHONPATH', 'Not set'))
print('✅ ENVIRONMENT:', os.environ.get('ENVIRONMENT', 'Not set'))
print('✅ Virtual Env:', os.environ.get('VIRTUAL_ENV', 'Not set'))
print('✅ All systems go!' if all([
    'sophia-main' in sys.executable,
    os.environ.get('PYTHONPATH'),
    os.environ.get('VIRTUAL_ENV')
]) else '❌ Check your environment setup')
"
```

## 💡 Pro Tips

1. **Use VSCode Command Palette** (`CMD + Shift + P`):
   - "Python: Select Interpreter" → Choose `.venv/bin/python`
   - "Terminal: Select Default Profile" → Choose `zsh` or `bash`

2. **For persistent issues**, try:
   - Delete `.vscode/settings.json` and recreate
   - Clear VSCode cache: `CMD + Shift + P` → "Developer: Reload Window"
   - Update VSCode and all extensions

3. **Cline-specific tips**:
   - Always ensure the virtual environment is activated BEFORE starting Cline
   - If Cline loses environment context, use the `sophia` alias to quickly restore it
