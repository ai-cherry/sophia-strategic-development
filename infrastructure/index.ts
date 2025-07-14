import * as pulumi from "@pulumi/pulumi";
import * as aws from "@pulumi/aws";
import * as k8s from "@pulumi/kubernetes";
import { LambdaLabsProvider } from "./providers/lambda-labs";
import { modern_stackProvider } from "./providers/modern_stack";
import { EstuaryProvider } from "./providers/estuary";
import { GitHubProvider } from "./providers/github";
import { PortkeyProvider } from "./providers/portkey";

// Get configuration from Pulumi ESC
const config = new pulumi.Config();
const pulumiOrg = config.require("pulumiOrg");
const environment = config.require("environment");

// Import ESC secrets
const escConfig = new pulumi.StackReference(`${pulumiOrg}/default/sophia-ai-${environment}`);

// Load cloud-init template
const cloudInitScript = `#!/bin/bash
echo "Starting Sophia AI instance initialization..."
`;

// Lambda Labs Infrastructure
export const lambdaLabs = new LambdaLabsProvider("lambda-labs", {
    apiKey: escConfig.getOutput("lambda_api_key"),
    sshPublicKeyBase64: escConfig.getOutput("lambda_labs_ssh_public_key_base64"),
    instances: [
        {
            name: "sophia-platform-prod",
            instanceType: "gpu_1x_a100",
            region: "us-west-1",
            userData: pulumi.interpolate`${cloudInitScript}`,
        },
        {
            name: "sophia-mcp-prod",
            instanceType: "gpu_1x_a100",
            region: "us-west-1",
            userData: pulumi.interpolate`${cloudInitScript}`,
        }
    ]
});

// modern_stack Infrastructure
export const modern_stack = new modern_stackProvider("modern_stack", {
    account: escConfig.getOutput("modern_stack_account"),
    username: escConfig.getOutput("modern_stack_user"),
    password: escConfig.getOutput("modern_stack_password"),
    role: escConfig.getOutput("modern_stack_role"),
    databases: [
        {
            name: "SOPHIA_AI_PROD",
            schemas: ["PUBLIC", "AI_MEMORY", "BUSINESS_INTELLIGENCE"],
            warehouses: ["COMPUTE_WH", "ANALYTICS_WH"],
        }
    ]
});

// Estuary Flow Infrastructure
export const estuary = new EstuaryProvider("estuary", {
    accessToken: escConfig.getOutput("estuary_access_token"),
    tenant: escConfig.getOutput("estuary_tenant"),
    flows: [
        {
            name: "gong-to-modern_stack",
            source: "gong",
            destination: "modern_stack",
            schedule: "0 */2 * * *", // Every 2 hours
        },
        {
            name: "hubspot-to-modern_stack",
            source: "hubspot",
            destination: "modern_stack",
            schedule: "0 */4 * * *", // Every 4 hours
        }
    ]
});

// GitHub Infrastructure
export const github = new GitHubProvider("github", {
    token: escConfig.getOutput("github_token"),
    organization: "ai-cherry",
    repositories: [
        {
            name: "sophia-main",
            private: true,
            branchProtection: {
                branches: ["main"],
                requiredReviews: 1,
            }
        }
    ],
    secrets: {
        organization: true,
        syncWithPulumiESC: true,
    }
});

// Portkey Infrastructure
export const portkey = new PortkeyProvider("portkey", {
    apiKey: escConfig.getOutput("portkey_api_key"),
    projects: [
        {
            name: "sophia-ai-production",
            virtualKeys: true,
            costAlerts: {
                daily: 1000,
                monthly: 25000,
            }
        }
    ]
});

// Export important values
export const lambdaLabsInstances = lambdaLabs.instances;
export const modern_stackDatabase = modern_stack.database;
export const estuaryFlows = estuary.flows;
export const githubRepos = github.repositories;
export const portkeyProject = portkey.project;
