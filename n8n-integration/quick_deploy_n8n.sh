#!/bin/bash
# Quick N8N + Sophia AI Integration Deployment

echo "🚀 Deploying N8N + Sophia AI Integration..."

# Set environment variables
export N8N_PASSWORD="sophia_secure_password_$(date +%s)"
export N8N_ENCRYPTION_KEY="sophia_encryption_key_32_chars_$(date +%s | cut -c1-8)"

# Create directory structure
mkdir -p n8n_data custom-nodes workflows

# Create basic workflow
cat > workflows/linkedin_ads_intelligence.json << 'WORKFLOW'
{
  "name": "LinkedIn Ads Intelligence",
  "nodes": [
    {
      "parameters": {
        "cronExpression": "0 */4 * * *"
      },
      "name": "Every 4 hours",
      "type": "n8n-nodes-base.cron",
      "typeVersion": 1,
      "position": [250, 300]
    },
    {
      "parameters": {
        "url": "http://sophia-mcp-bridge:9099/api/v1/n8n/process",
        "options": {}
      },
      "name": "Route to Sophia AI",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 1,
      "position": [450, 300]
    }
  ],
  "connections": {
    "Every 4 hours": {
      "main": [
        [
          {
            "node": "Route to Sophia AI",
            "type": "main",
            "index": 0
          }
        ]
      ]
    }
  }
}
WORKFLOW

echo "✅ N8N workflows created"

# Start services
docker-compose up -d

echo "🎉 N8N + Sophia AI Integration deployed!"
echo "Access N8N at: http://localhost:5678"
echo "Username: sophia_admin"
echo "Password: $N8N_PASSWORD"
echo "Sophia AI Bridge: http://localhost:9099/health"

