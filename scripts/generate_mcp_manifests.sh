#!/bin/bash

# MCP Server configurations
MCP_SERVERS=(
    "ai-memory:9000"
    "gong:9001"
    "qdrant:9002"
    "slack:9003"
    "linear:9004"
    "github:9005"
    "codacy:9006"
    "asana:9007"
)

echo "🚀 Generating MCP server manifests..."

for server_config in "${MCP_SERVERS[@]}"; do
    IFS=':' read -r server_name port <<< "$server_config"
    
    echo "Generating manifests for MCP server: $server_name (port: $port)"
    
    # Generate deployment
    sed "s/{{SERVER_NAME}}/$server_name/g; s/{{PORT}}/$port/g" \
        kubernetes/production/mcp-server-template.yaml > \
        kubernetes/production/mcp-${server_name}-deployment.yaml
    
    # Generate service
    cat > kubernetes/production/mcp-${server_name}-service.yaml << EOF
apiVersion: v1
kind: Service
metadata:
  name: mcp-${server_name}
  namespace: sophia-ai-prod
  labels:
    app: mcp-${server_name}
    component: mcp-server
    server: ${server_name}
spec:
  selector:
    app: mcp-${server_name}
  ports:
  - port: ${port}
    targetPort: ${port}
    name: http
  type: ClusterIP
EOF
    
    echo "✅ Generated manifests for $server_name"
done

echo "🎉 All MCP server manifests generated successfully!" 