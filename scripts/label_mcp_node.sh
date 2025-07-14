#!/bin/bash

# Label the MCP node for nodeSelector targeting
# This script should be run from a machine with kubectl access to the cluster

MCP_NODE_IP="104.171.202.117"
LABEL_KEY="kubernetes.io/hostname"
LABEL_VALUE="sophia-mcp-orchestrator"

echo "🏷️  Labeling MCP node for deployment targeting..."
echo "Target IP: $MCP_NODE_IP"
echo "Label: $LABEL_KEY=$LABEL_VALUE"

# Find the node with the MCP IP
NODE_NAME=$(kubectl get nodes -o wide | grep $MCP_NODE_IP | awk '{print $1}')

if [ -z "$NODE_NAME" ]; then
    echo "❌ Error: Could not find node with IP $MCP_NODE_IP"
    echo "Available nodes:"
    kubectl get nodes -o wide
    exit 1
fi

echo "Found node: $NODE_NAME"

# Apply the label
kubectl label node $NODE_NAME $LABEL_KEY=$LABEL_VALUE --overwrite

if [ $? -eq 0 ]; then
    echo "✅ Successfully labeled node $NODE_NAME"
    echo ""
    echo "Verification:"
    kubectl get node $NODE_NAME --show-labels | grep $LABEL_VALUE
else
    echo "❌ Failed to label node"
    exit 1
fi

echo ""
echo "MCP deployments will now be scheduled on this node." 