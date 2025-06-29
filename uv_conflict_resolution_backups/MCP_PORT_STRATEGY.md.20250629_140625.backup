# Sophia AI - MCP Server Port Strategy

This document outlines the official port allocation strategy for all Micro-service Connection Protocol (MCP) servers within the Sophia AI ecosystem. Adhering to this strategy is critical for preventing port conflicts, simplifying service discovery, and ensuring a stable development and production environment.

## 🎯 Guiding Principles

1.  **Single Source of Truth**: All port assignments are managed in a single, authoritative file: `config/mcp_ports.json`.
2.  **No Hardcoded Ports**: No service should ever have a port number hardcoded in its source code. All servers must read their assigned port from the central configuration file.
3.  **Logical Grouping**: Ports are assigned in logical ranges based on the server's function, making the system easier to understand and manage.
4.  **Extensibility**: The process for adding a new server and assigning it a port is clearly defined and simple to follow.

## 📂 The Authoritative Configuration File

The single source of truth for all port assignments is:

`config/mcp_ports.json`

This file contains a JSON object with a `servers` key, which maps each server's name to its assigned port number.

### Example:
```json
{
  "comment": "Single source of truth for all MCP server port assignments.",
  "servers": {
    "ai_memory": 9000,
    "codacy": 9003,
    "gong": 9100,
    "docker": 9300
  }
}
```

## 📊 Port Ranges

To maintain order, ports are allocated in the following ranges:

| Range         | Category                  | Description                                      |
|---------------|---------------------------|--------------------------------------------------|
| `9000-9099`   | Core Services             | Essential Sophia AI services (memory, agents, etc.) |
| `9100-9199`   | Business Intelligence     | BI tool integrations (Gong, HubSpot, etc.)       |
| `9200-9299`   | Data Integrations         | Data pipeline and ETL integrations (Estuary, etc.)|
| `9300-9399`   | Development & Ops Tools   | Utility servers (Codacy, Pulumi, etc.)           |

## ⚙️ Operational Scripts

A suite of new scripts has been developed to manage, test, and monitor the MCP ecosystem based on this centralized configuration.

### 1. **Run All MCP Servers**

This script is the primary way to start the entire MCP ecosystem for local development.

- **Command**: `python scripts/run_all_mcp_servers.py`
- **Functionality**:
    - Reads `config/mcp_ports.json`.
    - Kills any existing processes on the required ports for a clean start.
    - Starts all implemented MCP servers in parallel.
    - Provides a single point of control to start and stop the environment.

### 2. **Test All MCP Servers**

This script runs a comprehensive health check on all defined MCP servers.

- **Command**: `python scripts/test_all_mcp_servers.py`
- **Functionality**:
    - Reads `config/mcp_ports.json`.
    - Asynchronously calls the `/health` endpoint of every server.
    - Prints a consolidated report of the status and response time for each server.

### 3. **Monitor All MCP Servers**

This script provides a real-time, terminal-based dashboard for monitoring the ecosystem.

- **Command**: `python scripts/monitor_all_mcp_servers.py`
- **Functionality**:
    - Continuously polls the `/health` endpoint of all servers.
    - Displays a live, updating table with the status, port, and health details of each server.
    - Allows for at-a-glance visibility into the health of the entire microservice architecture.

## ➕ How to Add a New MCP Server

Adding a new server is now a simple, standardized process:

1.  **Choose a Port**: Select an available port from the appropriate range in `config/mcp_ports.json`.
2.  **Add to Config**: Add a new entry for your server in `config/mcp_ports.json`.
    ```json
    "servers": {
      "my_new_server": 9302,
      ...
    }
    ```
3.  **Implement the Server**: Create your server, ensuring it inherits from `StandardizedMCPServer`. The base class will automatically handle reading the port from the config file.
4.  **Update Deployment Script**: Add your new server to the list of `implemented_servers` in `scripts/run_all_mcp_servers.py` so it can be started automatically.
5.  **Done**: Your server is now fully integrated into the deployment, testing, and monitoring framework. 