#!/bin/bash
# Update systemd service ports on remote instances


# Update ai_memory_mcp service
sudo sed -i 's/--port 8001/--port 8101/g' /etc/systemd/system/sophia-ai_memory_mcp.service
sudo systemctl daemon-reload
sudo systemctl restart sophia-ai_memory_mcp.service
echo "✅ Updated ai_memory_mcp port to 8101"

# Update ai_memory service
sudo sed -i 's/--port 9000/--port 9001/g' /etc/systemd/system/sophia-ai_memory.service
sudo systemctl daemon-reload
sudo systemctl restart sophia-ai_memory.service
echo "✅ Updated ai_memory port to 9001"
