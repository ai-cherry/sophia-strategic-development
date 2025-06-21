"""Main Pulumi entry point for deploying the Sophia AI platform."""

import pulumi
import pulumi_aws as aws
from components.agno_agent_deployment import AgnoAgentDeployment
from components.portkey_gateway_deployment import PortkeyGatewayDeployment

# --- 1. Fetch Core Infrastructure ---
# In a real-world scenario, these would be fetched from a dedicated infrastructure stack.
# For this example, we'll assume they are available or create them.
# It's best practice to manage VPC and ECS Cluster in a separate Pulumi project/stack.
vpc = aws.ec2.get_vpc(default=True)
subnets = aws.ec2.get_subnets(
    filters=[
        aws.ec2.GetSubnetsFilterArgs(
            name="vpc-id",
            values=[vpc.id],
        )
    ]
)
cluster = aws.ecs.Cluster(
    "sophia-ai-cluster"
)  # Or get an existing one: aws.ecs.Cluster.get(...)

# --- 2. Define Portkey Configuration ---
# This configuration defines the LLM fallback strategy as code.
portkey_fallback_config = {
    "strategy": {"mode": "fallback", "on_status_codes": [429, 500, 503]},
    "targets": [
        {
            "virtual_key": "openrouter-key",
            "override_params": {"model": "openai/gpt-4o"},
        },
        {
            "virtual_key": "openrouter-key",
            "override_params": {"model": "anthropic/claude-3-sonnet"},
        },
        {
            "virtual_key": "openrouter-key",
            "override_params": {"model": "google/gemini-pro-1.5"},
        },
    ],
}

# Store this configuration as a Pulumi secret
# An agent or a startup script can later retrieve this to configure Portkey.
portkey_config_secret = pulumi.Config().set_secret(
    "portkeyFallbackConfig", portkey_fallback_config
)

# --- 3. Deploy the Portkey Gateway ---
portkey_gateway = PortkeyGatewayDeployment(
    name="portkey-gateway", cluster_arn=cluster.arn, vpc_subnets=subnets.ids
)

# --- 4. Define Agent Configurations ---
# This data could come from a YAML/JSON config file, a database, or be defined in code.
agent_definitions = [
    {
        "name": "analyst-agent",
        "persona": "You are an expert financial analyst. Your task is to analyze financial data and provide concise insights.",
        "tools": ["gong_tools", "looker_tools", "snowflake_tools"],
        "knowledge_bases": ["quarterly_reports_kb", "sec_filings_kb"],
        "image": "123456789012.dkr.ecr.us-west-2.amazonaws.com/analyst-agent:latest",  # Replace with your actual ECR image URI
    },
    {
        "name": "sales-coach-agent",
        "persona": "You are an encouraging and insightful sales coach. You review call transcripts to provide actionable feedback.",
        "tools": ["gong_tools", "hubspot_tools"],
        "knowledge_bases": ["sales_playbooks_kb", "best_practices_kb"],
        "image": "123456789012.dkr.ecr.us-west-2.amazonaws.com/sales-coach-agent:latest",  # Replace with your actual ECR image URI
    },
]

# --- 5. Deploy Agents using the Component ---
# Loop through the definitions and create a deployment for each one.
agent_services = []
for agent_def in agent_definitions:
    agent_deployment = AgnoAgentDeployment(
        name=agent_def["name"],
        image_uri=agent_def["image"],
        persona=agent_def["persona"],
        tools=agent_def["tools"],
        knowledge_bases=agent_def["knowledge_bases"],
        cluster_arn=cluster.arn,
        vpc_subnets=subnets.ids,
    )
    agent_services.append(agent_deployment.service_arn)

# --- 6. Export Outputs ---
pulumi.export("cluster_name", cluster.name)
pulumi.export("portkey_gateway_service_arn", portkey_gateway.service_arn)
pulumi.export("deployed_agent_services", pulumi.Output.all(*agent_services))
pulumi.export(
    "portkey_fallback_config_note",
    "Fallback config stored in Pulumi secrets. Use `pulumi config get --secret portkeyFallbackConfig` to view.",
)
