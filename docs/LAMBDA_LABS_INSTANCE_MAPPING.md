# Lambda Labs Instance Mapping

**Updated**: Fri Jul  4 23:01:22 PDT 2025

## Current Active Instances

### sophia-platform-prod
- **IP Address**: `192.222.58.232`
- **Instance Type**: `gpu_1x_a10`
- **Purpose**: Main Platform Services

### sophia-mcp-prod
- **IP Address**: `165.1.69.44`
- **Instance Type**: `gpu_1x_a10`
- **Purpose**: MCP Servers (Codacy, etc.)

### sophia-ai-prod
- **IP Address**: `192.222.58.232`
- **Instance Type**: `gpu_1x_a100_sxm4`
- **Purpose**: AI Processing & ML Workloads

## Service Deployment Mapping

| Service Type | Target Instance | IP Address | Purpose |
|--------------|----------------|------------|---------|
| Codacy | sophia-mcp-prod | `165.1.69.44` | MCP Servers (Codacy, etc.) |
| Mcp | sophia-mcp-prod | `165.1.69.44` | MCP Servers (Codacy, etc.) |
| Main | sophia-platform-prod | `192.222.58.232` | Main Platform Services |
| Api | sophia-platform-prod | `192.222.58.232` | Main Platform Services |
| Platform | sophia-platform-prod | `192.222.58.232` | Main Platform Services |
| Ai | sophia-ai-prod | `192.222.58.232` | AI Processing & ML Workloads |
| Ml | sophia-ai-prod | `192.222.58.232` | AI Processing & ML Workloads |
| Cortex | sophia-ai-prod | `192.222.58.232` | AI Processing & ML Workloads |

## Migration Summary

- **Old IP**: `104.171.202.64` (deprecated)
- **Codacy MCP Server**: Now deploys to `165.1.69.44` (sophia-mcp-prod)
- **Main Platform**: Now targets `192.222.58.232` (sophia-platform-prod)
- **AI Processing**: Now targets `192.222.58.232` (sophia-ai-prod)

## Access URLs

### MCP Services (sophia-mcp-prod: 165.1.69.44)
- Codacy MCP: `http://165.1.69.44:3008`
- AI Memory: `http://165.1.69.44:9001`
- Other MCP Servers: `http://165.1.69.44:<port>`

### Platform Services (sophia-platform-prod: 192.222.58.232)
- Main API: `http://192.222.58.232:8000`
- Frontend: `http://192.222.58.232:3000`
- API Docs: `http://192.222.58.232:8000/docs`

### AI Services (sophia-ai-prod: 192.222.58.232)
- Snowflake Cortex: `http://192.222.58.232:9030`
- AI Processing: `http://192.222.58.232:<port>`

## Monitoring Commands

```bash
# Test Codacy MCP Server
python scripts/monitor_codacy_mcp_server.py

# Test all connectivity
python scripts/test_lambda_labs_connectivity.py

# Check deployment status
python scripts/check_deployment_status.py
```
