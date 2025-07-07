#!/bin/bash
set -euo pipefail

MASTER_IP="192.222.51.151"
WORKERS=("192.222.50.209" "192.222.50.213")
SSH_KEY="$HOME/.ssh/lynn_sophia_h200_key"

# NEW: Disable firewall on all nodes to ensure connectivity
for IP in "$MASTER_IP" "${WORKERS[@]}"; do
  echo "🔥 Disabling firewall on $IP for setup..."
  ssh -o StrictHostKeyChecking=no -i "$SSH_KEY" ubuntu@$IP "sudo ufw disable"
done

echo "🚪 Cleaning up existing swarm state on master..."
ssh -i "$SSH_KEY" ubuntu@$MASTER_IP "sudo docker swarm leave --force || true"

echo "🌐 Initializing Docker Swarm on master $MASTER_IP..."
ssh -i "$SSH_KEY" ubuntu@$MASTER_IP "sudo docker swarm init --advertise-addr $MASTER_IP"

echo "🔑 Retrieving worker join token..."
TOKEN=$(ssh -i "$SSH_KEY" ubuntu@$MASTER_IP "sudo docker swarm join-token worker -q")

for IP in "${WORKERS[@]}"; do
  echo "🚪 Cleaning up existing swarm state on worker $IP..."
  ssh -i "$SSH_KEY" ubuntu@$IP "sudo docker swarm leave --force || true"
  echo "👷 Joining worker $IP to swarm using public master IP..."
  ssh -i "$SSH_KEY" ubuntu@$IP "sudo docker swarm join --token $TOKEN $MASTER_IP:2377"
done

echo "✅ Docker Swarm cluster should now be ready."
echo "🔍 Verifying node status..."
ssh -i "$SSH_KEY" ubuntu@$MASTER_IP "sudo docker node ls"
