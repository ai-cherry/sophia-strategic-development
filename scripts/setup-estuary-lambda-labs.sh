#!/bin/bash
# Setup Estuary Flow on Lambda Labs

set -e

# Configuration
LAMBDA_LABS_HOST="${LAMBDA_LABS_HOST:-146.235.200.1}"
LAMBDA_LABS_USER="${LAMBDA_LABS_USER:-ubuntu}"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Function to print colored output
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

echo "🌊 Estuary Flow Setup on Lambda Labs"
echo "===================================="
echo ""

# Check SSH access
echo "📋 Checking Lambda Labs access..."
if ! ssh -o ConnectTimeout=5 ${LAMBDA_LABS_USER}@${LAMBDA_LABS_HOST} "echo 'SSH OK'" &>/dev/null; then
    print_error "Cannot connect to Lambda Labs via SSH"
    print_info "Please ensure SSH key is configured for ${LAMBDA_LABS_USER}@${LAMBDA_LABS_HOST}"
    exit 1
fi
print_status "Lambda Labs SSH connection verified"

# Create setup script for Lambda Labs
echo ""
echo "📦 Installing flowctl CLI on Lambda Labs..."

ssh ${LAMBDA_LABS_USER}@${LAMBDA_LABS_HOST} << 'REMOTE_SETUP'
#!/bin/bash

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "Installing flowctl CLI..."

# Detect architecture
ARCH=$(uname -m)
OS=$(uname -s)

if [ "$ARCH" = "x86_64" ]; then
    ARCH="amd64"
elif [ "$ARCH" = "aarch64" ]; then
    ARCH="arm64"
fi

# Download flowctl
FLOWCTL_URL="https://github.com/estuary/flow/releases/latest/download/flowctl-${OS}-${ARCH}"
echo "Downloading from: $FLOWCTL_URL"

if curl -L "$FLOWCTL_URL" -o /tmp/flowctl; then
    echo -e "${GREEN}✓${NC} Downloaded flowctl"
else
    echo -e "${RED}✗${NC} Failed to download flowctl"
    exit 1
fi

# Install flowctl
sudo mv /tmp/flowctl /usr/local/bin/flowctl
sudo chmod +x /usr/local/bin/flowctl

# Verify installation
if flowctl version &>/dev/null; then
    echo -e "${GREEN}✓${NC} flowctl installed successfully"
    flowctl version
else
    echo -e "${RED}✗${NC} flowctl installation failed"
    exit 1
fi

# Create Estuary config directory
mkdir -p ~/.estuary
echo -e "${GREEN}✓${NC} Created Estuary config directory"

# Install additional dependencies
echo "Installing additional dependencies..."

# jq for JSON processing
if ! command -v jq &> /dev/null; then
    sudo apt-get update -qq
    sudo apt-get install -y jq
    echo -e "${GREEN}✓${NC} Installed jq"
fi

# yq for YAML processing
if ! command -v yq &> /dev/null; then
    sudo wget -qO /usr/local/bin/yq https://github.com/mikefarah/yq/releases/latest/download/yq_linux_amd64
    sudo chmod +x /usr/local/bin/yq
    echo -e "${GREEN}✓${NC} Installed yq"
fi

echo ""
echo "✅ Estuary Flow CLI setup complete on Lambda Labs!"
REMOTE_SETUP

# Copy Estuary configurations to Lambda Labs
echo ""
echo "📋 Copying Estuary configurations to Lambda Labs..."

# Create remote directories
ssh ${LAMBDA_LABS_USER}@${LAMBDA_LABS_HOST} "mkdir -p ~/sophia-ai/config/estuary/derivations ~/sophia-ai/config/estuary/materializations"

# Copy configuration files
scp -r config/estuary/* ${LAMBDA_LABS_USER}@${LAMBDA_LABS_HOST}:~/sophia-ai/config/estuary/
print_status "Copied Estuary configurations"

# Copy deployment script
scp scripts/deploy-estuary-flow.sh ${LAMBDA_LABS_USER}@${LAMBDA_LABS_HOST}:~/sophia-ai/
ssh ${LAMBDA_LABS_USER}@${LAMBDA_LABS_HOST} "chmod +x ~/sophia-ai/deploy-estuary-flow.sh"
print_status "Copied deployment script"

# Create Estuary secrets configuration
echo ""
echo "🔐 Setting up Estuary credentials..."

cat > /tmp/estuary-secrets.yaml << EOF
# Estuary Flow Secrets Configuration
# These values should come from Pulumi ESC

# Estuary API credentials
estuary_api_key: \${ESTUARY_API_KEY}
estuary_api_secret: \${ESTUARY_API_SECRET}

# Webhook tokens for MCP servers
estuary_gong_token: \${ESTUARY_GONG_TOKEN}
estuary_slack_token: \${ESTUARY_SLACK_TOKEN}
estuary_github_token: \${ESTUARY_GITHUB_TOKEN}

# Target credentials
redis_password: \${REDIS_PASSWORD}
snowflake_account: \${SNOWFLAKE_ACCOUNT}
snowflake_user: \${SNOWFLAKE_USER}
snowflake_password: \${SNOWFLAKE_PASSWORD}

# Monitoring
grafana_api_key: \${GRAFANA_API_KEY}
slack_webhook: \${SLACK_WEBHOOK}
EOF

scp /tmp/estuary-secrets.yaml ${LAMBDA_LABS_USER}@${LAMBDA_LABS_HOST}:~/sophia-ai/config/estuary/secrets.yaml.template
rm /tmp/estuary-secrets.yaml
print_status "Created secrets template"

# Create environment setup script
ssh ${LAMBDA_LABS_USER}@${LAMBDA_LABS_HOST} << 'CREATE_ENV_SCRIPT'
cat > ~/sophia-ai/setup-estuary-env.sh << 'EOF'
#!/bin/bash
# Source this script to set up Estuary environment

# Load secrets from Pulumi ESC (these should be set via Pulumi)
export ESTUARY_API_KEY="${ESTUARY_API_KEY}"
export ESTUARY_API_SECRET="${ESTUARY_API_SECRET}"
export ESTUARY_ORG="sophia-ai"
export ESTUARY_ENDPOINT="https://api.estuary.dev"

# MCP webhook tokens
export ESTUARY_GONG_TOKEN="${ESTUARY_GONG_TOKEN}"
export ESTUARY_SLACK_TOKEN="${ESTUARY_SLACK_TOKEN}"
export ESTUARY_GITHUB_TOKEN="${ESTUARY_GITHUB_TOKEN}"

# Target credentials
export REDIS_PASSWORD="${REDIS_PASSWORD}"
export SNOWFLAKE_ACCOUNT="${SNOWFLAKE_ACCOUNT}"
export SNOWFLAKE_USER="${SNOWFLAKE_USER}"
export SNOWFLAKE_PASSWORD="${SNOWFLAKE_PASSWORD}"

# Monitoring
export GRAFANA_API_KEY="${GRAFANA_API_KEY}"
export SLACK_WEBHOOK="${SLACK_WEBHOOK}"

echo "✅ Estuary environment configured"
EOF

chmod +x ~/sophia-ai/setup-estuary-env.sh
echo "✅ Created environment setup script"
CREATE_ENV_SCRIPT

# Create Grafana dashboard
echo ""
echo "📊 Setting up Grafana dashboard..."

cat > /tmp/estuary_flow_dashboard.json << 'EOF'
{
  "dashboard": {
    "id": null,
    "uid": "estuary-flow",
    "title": "Estuary Flow - Sophia AI",
    "tags": ["estuary", "data-pipeline", "sophia-ai"],
    "timezone": "browser",
    "schemaVersion": 30,
    "version": 0,
    "panels": [
      {
        "datasource": "Prometheus",
        "fieldConfig": {
          "defaults": {
            "color": {
              "mode": "palette-classic"
            },
            "custom": {
              "axisLabel": "",
              "axisPlacement": "auto",
              "barAlignment": 0,
              "drawStyle": "line",
              "fillOpacity": 10,
              "gradientMode": "none",
              "hideFrom": {
                "tooltip": false,
                "viz": false,
                "legend": false
              },
              "lineInterpolation": "linear",
              "lineWidth": 1,
              "pointSize": 5,
              "scaleDistribution": {
                "type": "linear"
              },
              "showPoints": "never",
              "spanNulls": true,
              "stacking": {
                "group": "A",
                "mode": "none"
              },
              "thresholdsStyle": {
                "mode": "off"
              }
            },
            "mappings": [],
            "thresholds": {
              "mode": "absolute",
              "steps": [
                {
                  "color": "green",
                  "value": null
                },
                {
                  "color": "red",
                  "value": 5
                }
              ]
            },
            "unit": "s"
          },
          "overrides": []
        },
        "gridPos": {
          "h": 8,
          "w": 12,
          "x": 0,
          "y": 0
        },
        "id": 1,
        "options": {
          "legend": {
            "calcs": [],
            "displayMode": "list",
            "placement": "bottom"
          },
          "tooltip": {
            "mode": "single"
          }
        },
        "pluginVersion": "8.0.0",
        "targets": [
          {
            "expr": "estuary_flow_lag_seconds{flow=~\"gong.*|slack.*|github.*\"}",
            "refId": "A"
          }
        ],
        "title": "Flow Lag (seconds)",
        "type": "timeseries"
      },
      {
        "datasource": "Prometheus",
        "fieldConfig": {
          "defaults": {
            "color": {
              "mode": "thresholds"
            },
            "mappings": [],
            "thresholds": {
              "mode": "absolute",
              "steps": [
                {
                  "color": "green",
                  "value": null
                },
                {
                  "color": "red",
                  "value": 1
                }
              ]
            },
            "unit": "short"
          },
          "overrides": []
        },
        "gridPos": {
          "h": 8,
          "w": 12,
          "x": 12,
          "y": 0
        },
        "id": 2,
        "options": {
          "orientation": "auto",
          "reduceOptions": {
            "values": false,
            "calcs": [
              "lastNotNull"
            ],
            "fields": ""
          },
          "showThresholdLabels": false,
          "showThresholdMarkers": true,
          "text": {}
        },
        "pluginVersion": "8.0.0",
        "targets": [
          {
            "expr": "sum(rate(estuary_flow_errors_total[5m]))",
            "refId": "A"
          }
        ],
        "title": "Error Rate",
        "type": "gauge"
      }
    ]
  },
  "overwrite": true
}
EOF

scp /tmp/estuary_flow_dashboard.json ${LAMBDA_LABS_USER}@${LAMBDA_LABS_HOST}:~/sophia-ai/infrastructure/monitoring/
rm /tmp/estuary_flow_dashboard.json
print_status "Created Grafana dashboard configuration"

echo ""
echo "🎉 Estuary Flow Setup Complete!"
echo "==============================="
echo ""
echo "📋 Next Steps on Lambda Labs:"
echo ""
echo "1. SSH to Lambda Labs:"
echo "   ssh ${LAMBDA_LABS_USER}@${LAMBDA_LABS_HOST}"
echo ""
echo "2. Configure Estuary credentials:"
echo "   cd ~/sophia-ai"
echo "   source setup-estuary-env.sh"
echo "   flowctl auth login"
echo ""
echo "3. Deploy Estuary flows:"
echo "   ./deploy-estuary-flow.sh"
echo ""
echo "4. Monitor flows:"
echo "   flowctl flows list --prefix sophia-ai/"
echo ""
echo "📚 Configuration files location: ~/sophia-ai/config/estuary/"
echo "📊 Grafana dashboard: http://${LAMBDA_LABS_HOST}:3000/d/estuary-flow"
echo ""
echo "⚠️  Remember to set all required environment variables via Pulumi ESC!"
