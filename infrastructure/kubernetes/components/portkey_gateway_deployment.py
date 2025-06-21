"""A Pulumi ComponentResource for deploying a self-hosted Portkey Gateway."""import pulumi

import json

import pulumi_aws as aws


class PortkeyGatewayDeployment(pulumi.ComponentResource):
    """Provisions a self-hosted Portkey AI Gateway on AWS ECS Fargate."""
    def __init__(self,
                 name: str,
                 cluster_arn: pulumi.Input[str],
                 vpc_subnets: pulumi.Input[list[str]],
                 opts: pulumi.ResourceOptions = None):
        super().__init__('custom:res:PortkeyGatewayDeployment', name, None, opts)

        esc_config = pulumi.Config("scoobyjava-org/default/sophia-ai-production")
        portkey_api_key = esc_config.require_secret("PORTKEY_API_KEY")
        openrouter_api_key = esc_config.require_secret("OPENROUTER_API_KEY")

        exec_role = aws.iam.Role(f"{name}-exec-role",
            assume_role_policy=aws.iam.get_policy_document(statements=[aws.iam.GetPolicyDocumentStatementArgs(
                actions=["sts:AssumeRole"],
                principals=[aws.iam.GetPolicyDocumentStatementPrincipalArgs(
                    type="Service",
                    identifiers=["ecs-tasks.amazonaws.com"],
                )],
            )]).json,
            opts=pulumi.ResourceOptions(parent=self))

        aws.iam.RolePolicyAttachment(f"{name}-exec-policy-attachment",
            role=exec_role.name,
            policy_arn="arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy",
            opts=pulumi.ResourceOptions(parent=exec_role))

        log_group = aws.cloudwatch.LogGroup(f"{name}-logs",
            retention_in_days=7,
            opts=pulumi.ResourceOptions(parent=self))

        # This container definition assumes a public Portkey Gateway image.
        # It injects the necessary API keys as secrets.
        container_definitions = pulumi.Output.all(
            portkey_api_key, openrouter_api_key, log_group.name
        ).apply(lambda args: json.dumps([{
            "name": "portkey-gateway",
            "image": "portkeyai/gateway:latest", # Use the official Portkey image
            "essential": True,
            "memory": 512,
            "cpu": 256,
            "logConfiguration": {
                "logDriver": "awslogs",
                "options": {
                    "awslogs-group": args[2],
                    "awslogs-region": aws.get_region().name,
                    "awslogs-stream-prefix": name
                }
            },
            "secrets": [
                {"name": "PORTKEY_API_KEY", "valueFrom": args[0]},
                {"name": "OPENROUTER_API_KEY", "valueFrom": args[1]},
            ],
            "portMappings": [{
                "containerPort": 8787,
                "hostPort": 8787
            }]
        }]))

        task_definition = aws.ecs.TaskDefinition(f"{name}-task-def",
            family=name,
            cpu="256",
            memory="512",
            network_mode="awsvpc",
            requires_compatibilities=["FARGATE"],
            execution_role_arn=exec_role.arn,
            container_definitions=container_definitions,
            opts=pulumi.ResourceOptions(parent=self))

        security_group = aws.ec2.SecurityGroup(f"{name}-sg",
            description="Allow inbound traffic to Portkey Gateway",
            ingress=[aws.ec2.SecurityGroupIngressArgs(
                protocol="tcp", from_port=8787, to_port=8787, cidr_blocks=["0.0.0.0/0"]
            )],
            egress=[aws.ec2.SecurityGroupEgressArgs(
                protocol="-1", from_port=0, to_port=0, cidr_blocks=["0.0.0.0/0"]
            )],
            opts=pulumi.ResourceOptions(parent=self))

        self.service = aws.ecs.Service(f"{name}-service",
            cluster=cluster_arn,
            task_definition=task_definition.arn,
            desired_count=1,
            launch_type="FARGATE",
            network_configuration=aws.ecs.ServiceNetworkConfigurationArgs(
                assign_public_ip=True,
                subnets=vpc_subnets,
                security_groups=[security_group.id],
            ),
            opts=pulumi.ResourceOptions(parent=self, depends_on=[log_group]))

        self.service_arn = self.service.arn
        self.register_outputs({
            "service_arn": self.service_arn,
        })
