"""
Main Pulumi entrypoint for deploying the entire Sophia AI stack to a
production-grade cloud environment (e.g., AWS).

This script orchestrates the following:
1. Building and publishing production Docker images.
2. Provisioning core infrastructure like databases and caches.
3. Deploying the application services as managed containers.
"""
import pulumi
import pulumi_aws as aws
import json

# --- Import our modular IaC components ---
# Note: We are importing the *scripts* themselves. Pulumi will understand
# that the resources defined within them need to be created.
from .docker_build import sophia_api_image, mcp_gateway_image # and others
from .snowflake_setup import sophia_db # and others
# We would also have a script for core AWS infra like VPCs, RDS, etc.
# For now, we will create placeholder resources here.

# --- 1. Core Infrastructure (VPC, Database, Cache) ---

# A real implementation would have a dedicated VPC script.
vpc = aws.ec2.Vpc("sophia-vpc", cidr_block="10.0.0.0/16")
subnet = aws.ec2.Subnet("sophia-subnet",
    vpc_id=vpc.id,
    cidr_block="10.0.1.0/24"
)

# A real implementation would have a dedicated RDS script.
db_password = pulumi.Config("postgres").require_secret("password")
db_instance = aws.rds.Instance("sophia-db",
    instance_class="db.t3.micro",
    allocated_storage=20,
    engine="postgres",
    engine_version="15",
    username="sophia_admin",
    password=db_password,
    skip_final_snapshot=True
)

# --- 2. ECS Cluster for running our containers ---
cluster = aws.ecs.Cluster("sophia-ecs-cluster")

# --- 3. Deploy the Sophia API Service ---

# Define the ECS Task Definition for the API
api_task_definition = aws.ecs.TaskDefinition("sophia-api-task",
    family="sophia-api",
    cpu="256",
    memory="512",
    network_mode="awsvpc",
    requires_compatibilities=["FARGATE"],
    execution_role_arn=aws.iam.Role("ecs-task-execution-role", # A real setup would use a predefined role
        assume_role_policy="""{
            "Version": "2012-10-17",
            "Statement": [{"Action": "sts:AssumeRole","Effect": "Allow","Principal": {"Service": "ecs-tasks.amazonaws.com"}}]
        }"""
    ).arn,
    container_definitions=pulumi.Output.all(
        sophia_api_image.image_name,
        db_instance.address,
        db_password
    ).apply(lambda args: json.dumps([{
        "name": "sophia-api",
        "image": args[0],
        "portMappings": [{"containerPort": 8000}],
        "environment": [
            {"name": "DATABASE_URL", "value": f"postgresql://sophia_admin:{args[2]}@{args[1]}/sophia"},
            # ... other environment variables from Pulumi secrets ...
        ],
        "logConfiguration": { # Send logs to CloudWatch
            "logDriver": "awslogs",
            "options": {
                "awslogs-group": "/ecs/sophia-api",
                "awslogs-region": "us-east-1",
                "awslogs-stream-prefix": "ecs"
            }
        }
    }]))
)

# Deploy the API as a Fargate Service
api_service = aws.ecs.Service("sophia-api-service",
    cluster=cluster.arn,
    task_definition=api_task_definition.arn,
    desired_count=1, # Start with one instance
    launch_type="FARGATE",
    network_configuration=aws.ecs.ServiceNetworkConfigurationArgs(
        subnets=[subnet.id],
        assign_public_ip=True # For simplicity, a real setup would use a load balancer
    )
)


# --- Outputs ---
pulumi.export("vpc_id", vpc.id)
pulumi.export("rds_instance_address", db_instance.address)
pulumi.export("ecs_cluster_name", cluster.name)
pulumi.export("api_service_name", api_service.name)
pulumi.export("deployment_status", "Production deployment orchestrated via Pulumi. Further services (MCP Gateway, etc.) would be added similarly.") 