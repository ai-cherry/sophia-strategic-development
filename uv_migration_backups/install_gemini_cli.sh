#!/bin/bash

echo "🚀 Installing Gemini CLI for Cline v3.18 Integration"
echo "=================================================="

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install Node.js and npm first."
    echo "   Visit: https://nodejs.org/"
    exit 1
fi

echo "✅ npm found at: $(which npm)"
echo ""

# Install Gemini CLI globally
echo "📦 Installing @google/generative-ai-cli globally..."
npm install -g @google/generative-ai-cli

# Check if installation was successful
if command -v gemini &> /dev/null; then
    echo ""
    echo "✅ Gemini CLI installed successfully!"
    echo "   Location: $(which gemini)"
    echo "   Version: $(gemini --version 2>/dev/null || echo 'Version info not available')"
    echo ""
    echo "🔑 Next steps:"
    echo "   1. Set up your API key: export GEMINI_API_KEY='your-api-key'"
    echo "   2. Or use the free tier with: gemini auth login"
    echo ""
    echo "📚 Documentation: https://github.com/google/generative-ai-docs/tree/main/cli"
else
    echo ""
    echo "⚠️  Installation completed but 'gemini' command not found in PATH"
    echo "   You may need to add npm's global bin directory to your PATH"
    echo "   Try: export PATH=\"$PATH:$(npm config get prefix)/bin\""
fi

echo ""
echo "🎯 Ready to test Cline v3.18 integration!"
