---
title: Sophia AI - Copilot Integration Usage
description: Sophia AI leverages Pulumi's AI‑Copilot to provide automated suggestions when infrastructure operations fail. This feature is available through the `PulumiAgent` and the `pulumi_mcp_client`.
tags: mcp, docker, security, agent
last_updated: 2025-06-23
dependencies: none
related_docs: none
---

# Sophia AI - Copilot Integration Usage


## Table of Contents

- [Getting Suggestions](#getting-suggestions)
- [Typical Workflow](#typical-workflow)
- [Troubleshooting](#troubleshooting)
- [Maintenance](#maintenance)

Sophia AI leverages Pulumi's AI‑Copilot to provide automated suggestions when infrastructure operations fail.
This feature is available through the `PulumiAgent` and the `pulumi_mcp_client`.

## Getting Suggestions

Use the Pulumi agent to request fixes when a command fails:

```python
# Example usage:
python
```python

The agent collects the most recent error from context and calls `/api/copilot/suggestions` on the Pulumi MCP server.

## Typical Workflow

1. Run a Pulumi command via the agent (e.g. `deploy dev`).
2. If an error occurs, issue a `fix` command.
3. Review the Copilot suggestion returned in the response.
4. Apply the suggestion manually or let the agent attempt an automatic patch.

## Troubleshooting

- **No suggestions returned** – verify `copilot.enabled` is `true` in `config/services/pulumi-mcp.json` and that your Pulumi access token is valid.
- **Network errors** – check connectivity between the API container and the Pulumi MCP server.
- **Outdated context** – ensure the session ID used for `fix` matches the one from the failed command.

## Maintenance

- Keep your Pulumi CLI version up to date in the `iac-toolkit` container.
- Rotate the Pulumi access token stored in GitHub organization secrets when required.
- Periodically review Copilot responses to improve automation rules.
