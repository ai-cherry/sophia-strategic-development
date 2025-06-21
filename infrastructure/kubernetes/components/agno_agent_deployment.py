"""A Pulumi ComponentResource for deploying a standardized, scalable Agno Agent.

This component encapsulates all the necessary AWS infrastructure to run an
agent as a containerized service on ECS Fargate, complete with auto-scaling,
logging, and secure secret injection from Pulumi ESC.
"""

import json

import pulumi
import pulumi_aws as aws


class AgnoAgentDeployment(pulumi.ComponentResource):
    """A Pulumi component that provisions a complete, production-ready.

    environment for a single Agno agent on AWS ECS Fargate.
    """

    def __init__(
        self,
        name: str,
        image_uri: pulumi.Input[str],
        persona: pulumi.Input[str],
        tools: pulumi.Input[list[str]],
        knowledge_bases: pulumi.Input[list[str]],
        cluster_arn: pulumi.Input[str],
        vpc_subnets: pulumi.Input[list[str]],
        opts: pulumi.ResourceOptions = None,
    ):
        """:param name: The unique name for the agent deployment (e.g., 'analyst-agent').

        :param image_uri: The URI of the Docker image for the agent.
        :param persona: A string describing the agent's persona or system prompt.
        :param tools: A list of tool names the agent has access to (e.g., ['gong_tools']).
        :param knowledge_bases: A list of knowledge base names the agent can query.
        :param cluster_arn: The ARN of the ECS cluster to deploy into.
        :param vpc_subnets: A list of VPC subnet IDs for the ECS service.
        """
        super().__init__("custom:res:AgnoAgentDeployment", name, None, opts)

        # Pull required secrets from the centralized Pulumi ESC environment.
        # This assumes the Pulumi program is configured to use this ESC environment.
        esc_config = pulumi.Config("scoobyjava-org/default/sophia-ai-production")
        agno_api_key = esc_config.require_secret("AGNO_API_KEY")
        arize_api_key = esc_config.require_secret("ARIZE_API_KEY")
        arize_space_id = esc_config.require_secret("ARIZE_SPACE_ID")

        # --- 1. IAM Roles ---
        # Role for the ECS task to execute (pulling images, writing logs)
        exec_role = aws.iam.Role(
            f"{name}-exec-role",
            assume_role_policy=aws.iam.get_policy_document(
                statements=[
                    aws.iam.GetPolicyDocumentStatementArgs(
                        actions=["sts:AssumeRole"],
                        principals=[
                            aws.iam.GetPolicyDocumentStatementPrincipalArgs(
                                type="Service",
                                identifiers=["ecs-tasks.amazonaws.com"],
                            )
                        ],
                    )
                ]
            ).json,
            opts=pulumi.ResourceOptions(parent=self),
        )

        aws.iam.RolePolicyAttachment(
            f"{name}-exec-policy-attachment",
            role=exec_role.name,
            policy_arn="arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy",
            opts=pulumi.ResourceOptions(parent=exec_role),
        )

        # --- 2. CloudWatch Log Group ---
        log_group = aws.cloudwatch.LogGroup(
            f"{name}-logs",
            retention_in_days=14,
            opts=pulumi.ResourceOptions(parent=self),
        )

        # --- 3. ECS Task Definition ---
        # NEW PATTERN: We no longer inject secrets directly. Instead, we use
        # `esc run` as the command/entrypoint for the container. `esc run` will
        # populate the environment with the secrets from our ESC environment
        # before starting the actual agent process.
        container_definitions = pulumi.Output.all(
            image_uri, persona, tools, knowledge_bases, log_group.name
        ).apply(
            lambda args: json.dumps(
                [
                    {
                        "name": "agent-container",
                        "image": args[0],
                        "essential": True,
                        "memory": 512,
                        "cpu": 256,
                        "logConfiguration": {
                            "logDriver": "awslogs",
                            "options": {
                                "awslogs-group": args[4],
                                "awslogs-region": aws.get_region().name,
                                "awslogs-stream-prefix": name,
                            },
                        },
                        # This is the key change. We now use `esc run` to start our application.
                        # This injects the environment and then executes our agent's main script.
                        "command": [
                            "esc",
                            "run",
                            "scoobyjava-org/default/sophia-ai-production",
                            "--",
                            "python",
                            "agent_main.py",  # The actual entrypoint of the agent container
                        ],
                        # We no longer pass secrets directly. The Task Role must have OIDC configured
                        # to allow access to the secrets in Pulumi ESC.
                        "environment": [
                            {"name": "PERSONA", "value": args[1]},
                            {"name": "TOOLS", "value": ",".join(args[2])},
                            {"name": "KNOWLEDGE_BASES", "value": ",".join(args[3])},
                        ],
                    }
                ]
            )
        )

        task_definition = aws.ecs.TaskDefinition(
            f"{name}-task-def",
            family=name,
            cpu="256",
            memory="512",
            network_mode="awsvpc",
            requires_compatibilities=["FARGATE"],
            execution_role_arn=exec_role.arn,
            container_definitions=container_definitions,
            opts=pulumi.ResourceOptions(parent=self),
        )

        # --- 4. Security Group ---
        # Allows outbound traffic and can be configured for specific inbound rules.
        security_group = aws.ec2.SecurityGroup(
            f"{name}-sg",
            description=f"Security group for the {name} agent",
            egress=[
                aws.ec2.SecurityGroupEgressArgs(
                    protocol="-1", from_port=0, to_port=0, cidr_blocks=["0.0.0.0/0"]
                )
            ],
            opts=pulumi.ResourceOptions(parent=self),
        )

        # --- 5. ECS Service ---
        self.service = aws.ecs.Service(
            f"{name}-service",
            cluster=cluster_arn,
            task_definition=task_definition.arn,
            desired_count=1,
            launch_type="FARGATE",
            network_configuration=aws.ecs.ServiceNetworkConfigurationArgs(
                assign_public_ip=True,
                subnets=vpc_subnets,
                security_groups=[security_group.id],
            ),
            opts=pulumi.ResourceOptions(parent=self, depends_on=[log_group]),
        )

        # --- 6. Auto Scaling ---
        scaling_target = aws.appautoscaling.Target(
            f"{name}-scaling-target",
            max_capacity=5,
            min_capacity=1,
            resource_id=self.service.id.apply(
                lambda id: f"service/{cluster_arn.split('/')[-1]}/{id.split('/')[-1]}"
            ),
            scalable_dimension="ecs:service:DesiredCount",
            service_namespace="ecs",
            opts=pulumi.ResourceOptions(parent=self),
        )

        aws.appautoscaling.Policy(
            f"{name}-cpu-scaling-policy",
            policy_type="TargetTrackingScaling",
            resource_id=scaling_target.resource_id,
            scalable_dimension=scaling_target.scalable_dimension,
            service_namespace=scaling_target.service_namespace,
            target_tracking_scaling_policy_configuration=aws.appautoscaling.PolicyTargetTrackingScalingPolicyConfigurationArgs(
                target_value=60.0,  # Target 60% CPU utilization
                predefined_metric_specification=aws.appautoscaling.PolicyPredefinedMetricSpecificationArgs(
                    predefined_metric_type="ECSServiceAverageCPUUtilization",
                ),
                scale_in_cooldown=60,
                scale_out_cooldown=60,
            ),
            opts=pulumi.ResourceOptions(parent=scaling_target),
        )

        # --- Outputs of this Component ---
        self.service_arn = self.service.arn
        self.task_definition_arn = task_definition.arn
        self.register_outputs(
            {
                "service_arn": self.service_arn,
                "task_definition_arn": self.task_definition_arn,
            }
        )
