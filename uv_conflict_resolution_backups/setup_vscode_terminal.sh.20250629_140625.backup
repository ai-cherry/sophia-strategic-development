#!/bin/bash

# Setup VSCode Terminal Integration for Sophia AI
# This script fixes the "Shell Integration Unavailable" issue

echo "🚀 Setting up VSCode Terminal Integration for Sophia AI..."

# Function to add sophia alias
add_sophia_alias() {
    local shell_rc="$1"
    local alias_cmd='alias sophia="cd ~/sophia-main && source .venv/bin/activate"'
    
    if [ -f "$shell_rc" ]; then
        if ! grep -q "alias sophia=" "$shell_rc"; then
            echo "" >> "$shell_rc"
            echo "# Sophia AI quick access" >> "$shell_rc"
            echo "$alias_cmd" >> "$shell_rc"
            echo "✅ Added sophia alias to $shell_rc"
        else
            echo "✅ Sophia alias already exists in $shell_rc"
        fi
    fi
}

# Function to add auto-activation
add_auto_activation() {
    local shell_rc="$1"
    local activation_code='
# Auto-activate Sophia AI environment
if [[ "$PWD" == "$HOME/sophia-main"* ]] && [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi'
    
    if [ -f "$shell_rc" ]; then
        if ! grep -q "Auto-activate Sophia AI environment" "$shell_rc"; then
            echo "$activation_code" >> "$shell_rc"
            echo "✅ Added auto-activation to $shell_rc"
        else
            echo "✅ Auto-activation already exists in $shell_rc"
        fi
    fi
}

# Update .zshrc
if [ -f "$HOME/.zshrc" ]; then
    echo "📝 Updating .zshrc..."
    add_sophia_alias "$HOME/.zshrc"
    add_auto_activation "$HOME/.zshrc"
fi

# Update .bashrc
if [ -f "$HOME/.bashrc" ]; then
    echo "📝 Updating .bashrc..."
    add_sophia_alias "$HOME/.bashrc"
    add_auto_activation "$HOME/.bashrc"
fi

# Create or update VSCode workspace file
echo "📝 Creating VSCode workspace configuration..."
cat > ~/sophia-main/sophia-main.code-workspace << 'EOF'
{
    "folders": [
        {
            "path": "."
        }
    ],
    "settings": {
        "terminal.integrated.defaultProfile.osx": "zsh",
        "terminal.integrated.profiles.osx": {
            "zsh": {
                "path": "/bin/zsh",
                "args": ["-l"],
                "env": {
                    "SOPHIA_PROJECT_ROOT": "${workspaceFolder}",
                    "PYTHONPATH": "${workspaceFolder}:${workspaceFolder}/backend"
                }
            }
        },
        "terminal.integrated.shellIntegration.enabled": true,
        "terminal.integrated.shellIntegration.decorationsEnabled": "both",
        "terminal.integrated.cwd": "${workspaceFolder}",
        "terminal.integrated.env.osx": {
            "SOPHIA_PROJECT_ROOT": "${workspaceFolder}",
            "PYTHONPATH": "${workspaceFolder}:${workspaceFolder}/backend"
        },
        "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
        "python.terminal.activateEnvironment": true,
        "python.terminal.activateEnvInCurrentTerminal": true
    }
}
EOF

echo "✅ VSCode workspace file created"

# Create a simple activation script
echo "📝 Creating quick activation script..."
cat > ~/sophia-main/activate_sophia.sh << 'EOF'
#!/bin/bash
cd ~/sophia-main
source .venv/bin/activate
echo "🧠 Welcome to Sophia AI workspace!"
echo "✅ Virtual environment activated"
echo "📍 Current directory: $(pwd)"
EOF

chmod +x ~/sophia-main/activate_sophia.sh

echo ""
echo "✅ Setup complete!"
echo ""
echo "🎯 Next steps:"
echo "1. Close VSCode completely"
echo "2. Reopen using: code ~/sophia-main/sophia-main.code-workspace"
echo "3. The terminal will now have shell integration enabled"
echo ""
echo "💡 Quick tips:"
echo "- Use 'sophia' command from any terminal to jump to Sophia AI"
echo "- Virtual environment activates automatically in ~/sophia-main"
echo "- Shell integration provides better command history and navigation"
echo ""
