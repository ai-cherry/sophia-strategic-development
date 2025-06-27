# Gemini CLI Integration for Sophia AI

This integration provides free access to Gemini models through the Gemini CLI, enabling cost-effective AI operations for large documents and general tasks.

## Features

- **Free Access**: Use Gemini 2.5 Pro without API costs
- **Large Context**: Support for up to 1M tokens
- **Automatic Fallback**: Seamlessly switch from paid APIs when limits are reached
- **Native Integration**: Works with Sophia AI's model routing system

## Setup

1. **Install Gemini CLI**:
   ```bash
   # Install the Gemini CLI
   curl -sSL https://gemini.google.com/cli/install.sh | bash
   
   # Or using npm
   npm install -g @google/gemini-cli
   ```

2. **Authenticate**:
   ```bash
   gemini auth login
   ```

3. **Verify Installation**:
   ```bash
   gemini --version
   gemini models list
   ```

## Usage

The Gemini CLI integration is automatically available through:

1. **Direct MCP Server Usage**:
   - Large document processing (>100K tokens)
   - Cost-sensitive operations
   - Batch processing tasks

2. **Automatic Model Routing**:
   - The StandardizedMCPServer automatically routes to Gemini CLI when:
     - Context size exceeds 200K tokens
     - API rate limits are reached
     - Cost optimization is enabled

3. **Natural Language Commands**:
   - "Process this large document with Gemini"
   - "Use free tier for this analysis"
   - "Analyze this 500K token file"

## Configuration

Add to your environment:
```bash
export GEMINI_CLI_PATH="/usr/local/bin/gemini"
export GEMINI_MODEL_PREFERENCE="gemini-2.5-pro"
export ENABLE_GEMINI_FALLBACK=true
```

## Model Capabilities

- **gemini-2.5-pro**: 1M context, multimodal, free tier
- **gemini-2.5-flash**: Fast responses, 256K context
- **gemini-experimental**: Latest features, variable context

## Cost Optimization

The integration automatically selects Gemini CLI when:
- Document size > 200K tokens
- Hourly API spend > threshold
- Specific "use free tier" command given
- Rate limits on paid APIs reached

## Monitoring

Check usage:
```bash
python scripts/check_gemini_usage.py
```

View routing decisions:
```bash
tail -f logs/model_routing.log | grep GEMINI
