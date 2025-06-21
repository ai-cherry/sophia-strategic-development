# The AI-Driven Dashboard Deployment Workflow

**Date:** December 20, 2024
**Status:** The Official Continuous Deployment Strategy for the Sophia Dashboard

## 1. The Goal: Zero-Touch, AI-Orchestrated Frontend Deployment

This document describes the modern, AI-driven workflow that replaces manual frontend deployments. The entire process is orchestrated by a specialized AI agent, the **`FrontendOps Agent`**, which uses our standard MCP servers as its tools.

---

## 2. The Workflow Visualized

```mermaid
sequenceDiagram
    participant Dev as Developer
    participant Git as GitHub Repository
    participant Action as GitHub Action
    participant Agent as FrontendOps Agent
    participant Pulumi as Pulumi MCP Server
    participant AWS as AWS (S3/CloudFront)

    Dev->>+Git: Push changes to `sophia-dashboard/`
    Git->>+Action: Trigger "Build Sophia Dashboard" workflow
    Action->>Action: Run `npm ci` and `npm run build`
    Action->>AWS: `aws s3 sync ./dist s3://sophia-dashboard-build-artifacts/`
    Action-->>-Git: Build successful

    Note over Agent: A new build is ready. Deployment can be triggered.

    Dev->>+Agent: "Deploy the latest version of the dashboard"
    Agent->>+Pulumi: "Get the output 'deployment_sync_command' from the 'dashboard-hosting-prod' stack"
    Pulumi-->>-Agent: "aws s3 sync s3://sophia-dashboard-build-artifacts/ s3://sophia-dashboard-hosting-bucket-xyz/"

    Agent->>+Agent: Execute the received AWS CLI command
    Note over Agent: Agent runs the sync command in its secure environment

    Agent->>+AWS: Sync files from build bucket to hosting bucket
    AWS-->>-Agent: Sync complete

    Agent->>+Pulumi: "Trigger an invalidation for the 'sophia-dashboard-cdn' CloudFront distribution"
    Pulumi-->>-Agent: "Invalidation request created"

    Agent-->>-Dev: "Deployment complete. The latest version is now live."
```

---

## 3. The Core Components

### The `FrontendOps Agent`
This is an Agno agent with a simple persona: "You are an expert DevOps engineer responsible for the Sophia Dashboard. Your only tools are the `pulumi` and `github` MCP servers."

### The Key Tools (MCP Servers)

The agent needs only two tools to accomplish this entire workflow:

1.  **`pulumi/mcp-server`:**
    *   **To get the sync command:** Before deploying, the agent asks the Pulumi MCP server for the output of the `dashboard-hosting-prod` stack. This is a crucial security step: the agent doesn't need to know the destination bucket name; it just asks Pulumi for the correct, deployed command.
    *   **To trigger a CDN invalidation:** After syncing the files, the agent tells the Pulumi MCP server to run a command that invalidates the CloudFront cache, ensuring users see the latest version immediately.

2.  **`github/mcp-server` (Optional but Recommended):**
    *   Before deploying, the agent can use this server to query for the latest commit hash from the `sophia-dashboard/` directory.
    *   It can then create a git tag for the deployment (e.g., `dashboard-deploy-20241220-1`), providing a perfect audit trail and linking every deployment back to a specific code change.

---

## 4. How It Works in Practice

1.  A developer makes changes to the React components in the `sophia-dashboard` directory and pushes to `main`.
2.  The **GitHub Action** automatically runs, builds the production assets, and places them in the `s3://sophia-dashboard-build-artifacts` bucket.
3.  A release manager (or an automated timer) tells the **`FrontendOps Agent`**: `"Deploy the latest dashboard."`
4.  The agent asks the **Pulumi MCP Server** for the sync command.
5.  The agent executes the command, copying the new files to the live hosting bucket.
6.  The agent tells the **Pulumi MCP Server** to invalidate the CloudFront CDN cache.
7.  The new dashboard is live for all users.

---

## Conclusion

This workflow is the pinnacle of the modern architecture we have built. It is:
-   **Secure:** The agent never needs to know any AWS credentials or bucket names directly. It only uses the high-level tools provided by the Pulumi MCP server.
-   **Auditable:** Every deployment can be traced back to a specific agent request and a specific git commit.
-   **Simple:** The agent's logic is incredibly simple: `get command`, `run command`, `invalidate cache`. All the complexity is handled by the underlying infrastructure.
-   **AI-Driven:** We have fully automated our frontend CI/CD pipeline and put it under the control of a conversational AI agent.

This completes the vision for building and deploying our dashboards. We have all the tools, infrastructure, and the strategic workflow defined to make it a reality.
