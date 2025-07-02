#!/bin/bash

# Start Enhanced MCP Servers

echo '🚀 Starting Enhanced MCP Servers...'

# Start ai_memory
echo 'Starting ai_memory on port 9000...'
cd /Users/lynnmusil/sophia-main/mcp-servers/ai_memory && PORT=9000 python ai_memory_mcp_server.py &
sleep 2

# Start snowflake
echo 'Starting snowflake on port 9010...'
cd /Users/lynnmusil/sophia-main/mcp-servers/snowflake && PORT=9010 python snowflake_mcp_server.py &
sleep 2

# Start snowflake_cortex
echo 'Starting snowflake_cortex on port 9011...'
cd /Users/lynnmusil/sophia-main/mcp-servers/snowflake_cortex && PORT=9011 python production_snowflake_cortex_mcp_server.py &
sleep 2

# Start hubspot
echo 'Starting hubspot on port 9020...'
cd /Users/lynnmusil/sophia-main/mcp-servers/hubspot && PORT=9020 python hubspot_mcp_server.py &
sleep 2

# Start slack
echo 'Starting slack on port 9030...'
cd /Users/lynnmusil/sophia-main/mcp-servers/slack && PORT=9030 python slack_mcp_server.py &
sleep 2

# Start linear
echo 'Starting linear on port 9031...'
cd /Users/lynnmusil/sophia-main/mcp-servers/linear && PORT=9031 python linear_mcp_server.py &
sleep 2

# Start notion
echo 'Starting notion on port 9032...'
cd /Users/lynnmusil/sophia-main/mcp-servers/notion && PORT=9032 python notion_mcp_server.py &
sleep 2

# Start lambda_labs_cli
echo 'Starting lambda_labs_cli on port 9050...'
cd /Users/lynnmusil/sophia-main/mcp-servers/lambda_labs_cli && PORT=9050 python lambda_labs_cli_mcp_server.py &
sleep 2

# Start snowflake_admin
echo 'Starting snowflake_admin on port 9050...'
cd /Users/lynnmusil/sophia-main/mcp-servers/snowflake_admin && PORT=9050 python snowflake_admin_mcp_server.py &
sleep 2

# Start graphiti
echo 'Starting graphiti on port 9050...'
cd /Users/lynnmusil/sophia-main/mcp-servers/graphiti && PORT=9050 python graphiti_mcp_server.py &
sleep 2

# Start ui_ux_agent
echo 'Starting ui_ux_agent on port 9050...'
cd /Users/lynnmusil/sophia-main/mcp-servers/ui_ux_agent && PORT=9050 python ui_ux_agent_mcp_server.py &
sleep 2

# Start apify_intelligence
echo 'Starting apify_intelligence on port 9050...'
cd /Users/lynnmusil/sophia-main/mcp-servers/apify_intelligence && PORT=9050 python apify_intelligence_mcp_server.py &
sleep 2

# Start github
echo 'Starting github on port 9034...'
cd /Users/lynnmusil/sophia-main/mcp-servers/github && PORT=9034 python github_mcp_server.py &
sleep 2

# Start huggingface_ai
echo 'Starting huggingface_ai on port 9050...'
cd /Users/lynnmusil/sophia-main/mcp-servers/huggingface_ai && PORT=9050 python huggingface_ai_mcp_server.py &
sleep 2

# Start ag_ui
echo 'Starting ag_ui on port 9050...'
cd /Users/lynnmusil/sophia-main/mcp-servers/ag_ui && PORT=9050 python enhanced_ag_ui_mcp_server.py &
sleep 2

# Start bright_data
echo 'Starting bright_data on port 9041...'
cd /Users/lynnmusil/sophia-main/mcp-servers/bright_data && PORT=9041 python bright_data_mcp_server.py &
sleep 2

# Start portkey_admin
echo 'Starting portkey_admin on port 9050...'
cd /Users/lynnmusil/sophia-main/mcp-servers/portkey_admin && PORT=9050 python portkey_admin_mcp_server.py &
sleep 2

# Start codacy
echo 'Starting codacy on port 9040...'
cd /Users/lynnmusil/sophia-main/mcp-servers/codacy && PORT=9040 python codacy_mcp_server.py &
sleep 2

# Start snowflake_cli_enhanced
echo 'Starting snowflake_cli_enhanced on port 9050...'
cd /Users/lynnmusil/sophia-main/mcp-servers/snowflake_cli_enhanced && PORT=9050 python snowflake_cli_enhanced_mcp_server.py &
sleep 2

# Start asana
echo 'Starting asana on port 9033...'
cd /Users/lynnmusil/sophia-main/mcp-servers/asana && PORT=9033 python asana_mcp_server.py &
sleep 2

echo '✅ All servers started!'
echo 'Check health at: http://localhost:<port>/health'
