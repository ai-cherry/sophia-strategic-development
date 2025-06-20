from typing import Dict, List, Optional

import pulumi
import pulumi_aws as aws

from .base_component import BaseComponent


class DashboardPlatform(BaseComponent):
    """Pulumi IDP Dashboard Platform Component
    Replaces Retool with self-hosted dashboard infrastructure
    """

    def __init__(self, name: str, args: "DashboardPlatformArgs", opts=None):
        super().__init__(name, opts)

        self.args = args
        self.vpc = None
        self.cluster = None
        self.dashboard_services = {}
        self.load_balancer = None

        # Create infrastructure
        self._create_vpc()
        self._create_ecs_cluster()
        self._create_dashboard_services()
        self._create_load_balancer()
        self._create_ai_powered_dashboard_generator()

        # Register outputs
        self.register_outputs(
            {
                "dashboard_url": self.load_balancer.dns_name,
                "cluster_name": self.cluster.name,
                "vpc_id": self.vpc.id,
                "dashboard_services": pulumi.Output.all(
                    **self.dashboard_services
                ).apply(
                    lambda services: {
                        k: v.get("url", "pending") for k, v in services.items()
                    }
                ),
            }
        )

    def _create_vpc(self):
        """Create VPC for dashboard platform"""
        self.vpc = aws.ec2.Vpc(
            f"{self.args.name}-dashboard-vpc",
            cidr_block="10.0.0.0/16",
            enable_dns_hostnames=True,
            enable_dns_support=True,
            tags={
                "Name": f"{self.args.name}-dashboard-vpc",
                "Environment": self.args.environment,
                "Component": "DashboardPlatform",
            },
        )

        # Public subnets for load balancer
        self.public_subnets = []
        for i, az in enumerate(self.args.availability_zones):
            subnet = aws.ec2.Subnet(
                f"{self.args.name}-public-subnet-{i}",
                vpc_id=self.vpc.id,
                cidr_block=f"10.0.{i+1}.0/24",
                availability_zone=az,
                map_public_ip_on_launch=True,
                tags={"Name": f"public-subnet-{i}"},
            )
            self.public_subnets.append(subnet)

        # Private subnets for dashboard services
        self.private_subnets = []
        for i, az in enumerate(self.args.availability_zones):
            subnet = aws.ec2.Subnet(
                f"{self.args.name}-private-subnet-{i}",
                vpc_id=self.vpc.id,
                cidr_block=f"10.0.{i+10}.0/24",
                availability_zone=az,
                tags={"Name": f"private-subnet-{i}"},
            )
            self.private_subnets.append(subnet)

        # Internet Gateway
        self.igw = aws.ec2.InternetGateway(
            f"{self.args.name}-igw",
            vpc_id=self.vpc.id,
            tags={"Name": f"{self.args.name}-igw"},
        )

        # Route table for public subnets
        public_rt = aws.ec2.RouteTable(
            f"{self.args.name}-public-rt",
            vpc_id=self.vpc.id,
            routes=[
                aws.ec2.RouteTableRouteArgs(
                    cidr_block="0.0.0.0/0", gateway_id=self.igw.id
                )
            ],
            tags={"Name": "public-route-table"},
        )

        for i, subnet in enumerate(self.public_subnets):
            aws.ec2.RouteTableAssociation(
                f"{self.args.name}-public-rta-{i}",
                subnet_id=subnet.id,
                route_table_id=public_rt.id,
            )

    def _create_ecs_cluster(self):
        """Create ECS cluster for dashboard services"""
        self.cluster = aws.ecs.Cluster(
            f"{self.args.name}-dashboard-cluster",
            capacity_providers=["FARGATE"],
            default_capacity_provider_strategies=[
                aws.ecs.ClusterDefaultCapacityProviderStrategyArgs(
                    capacity_provider="FARGATE", weight=1
                )
            ],
            tags={
                "Name": f"{self.args.name}-dashboard-cluster",
                "Environment": self.args.environment,
            },
        )

        # Security group for dashboard services
        self.dashboard_sg = aws.ec2.SecurityGroup(
            f"{self.args.name}-dashboard-sg",
            description="Security group for dashboard services",
            vpc_id=self.vpc.id,
            ingress=[
                aws.ec2.SecurityGroupIngressArgs(
                    protocol="tcp", from_port=80, to_port=80, cidr_blocks=["0.0.0.0/0"]
                ),
                aws.ec2.SecurityGroupIngressArgs(
                    protocol="tcp",
                    from_port=443,
                    to_port=443,
                    cidr_blocks=["0.0.0.0/0"],
                ),
                aws.ec2.SecurityGroupIngressArgs(
                    protocol="tcp",
                    from_port=3000,
                    to_port=3000,
                    cidr_blocks=["10.0.0.0/16"],
                ),
            ],
            egress=[
                aws.ec2.SecurityGroupEgressArgs(
                    protocol="-1", from_port=0, to_port=0, cidr_blocks=["0.0.0.0/0"]
                )
            ],
            tags={"Name": f"{self.args.name}-dashboard-sg"},
        )

    def _create_dashboard_services(self):
        """Create dashboard services to replace Retool functionality"""
        # CEO Dashboard Service
        self.dashboard_services["ceo"] = self._create_dashboard_service(
            "ceo",
            {
                "DASHBOARD_TYPE": "executive",
                "DATA_SOURCES": "snowflake,gong,openai",
                "FEATURES": "strategic-chat,client-health,revenue-analytics",
            },
        )

        # Knowledge Admin Dashboard Service
        self.dashboard_services["knowledge"] = self._create_dashboard_service(
            "knowledge",
            {
                "DASHBOARD_TYPE": "knowledge-admin",
                "DATA_SOURCES": "pinecone,s3,openai",
                "FEATURES": "document-upload,insight-curation,discovery-queue",
            },
        )

        # Project Intelligence Dashboard Service
        self.dashboard_services["project"] = self._create_dashboard_service(
            "project",
            {
                "DASHBOARD_TYPE": "project-intelligence",
                "DATA_SOURCES": "linear,github,asana,slack",
                "FEATURES": "portfolio-overview,okr-alignment,team-performance",
            },
        )

        # AI Dashboard Generator Service
        self.dashboard_services["generator"] = self._create_ai_dashboard_generator()

    def _create_dashboard_service(
        self, dashboard_type: str, environment_vars: Dict[str, str]
    ):
        """Create a dashboard service with ECS Fargate"""
        # Task definition
        task_definition = aws.ecs.TaskDefinition(
            f"{self.args.name}-{dashboard_type}-task",
            family=f"{self.args.name}-{dashboard_type}",
            cpu="512",
            memory="1024",
            network_mode="awsvpc",
            requires_compatibility=["FARGATE"],
            execution_role_arn=self._get_execution_role().arn,
            task_role_arn=self._get_task_role().arn,
            container_definitions=pulumi.Output.json_dumps(
                [
                    {
                        "name": f"{dashboard_type}-dashboard",
                        "image": f"sophia-dashboard-{dashboard_type}:latest",
                        "essential": True,
                        "portMappings": [{"containerPort": 3000, "protocol": "tcp"}],
                        "environment": [
                            {"name": k, "value": v} for k, v in environment_vars.items()
                        ]
                        + [
                            {"name": "API_BASE_URL", "value": self.args.backend_url},
                            {"name": "ENVIRONMENT", "value": self.args.environment},
                        ],
                        "logConfiguration": {
                            "logDriver": "awslogs",
                            "options": {
                                "awslogs-group": f"/ecs/{self.args.name}-{dashboard_type}",
                                "awslogs-region": self.args.region,
                                "awslogs-stream-prefix": "ecs",
                            },
                        },
                    }
                ]
            ),
        )

        # CloudWatch log group
        aws.cloudwatch.LogGroup(
            f"{self.args.name}-{dashboard_type}-logs",
            name=f"/ecs/{self.args.name}-{dashboard_type}",
            retention_in_days=7,
        )

        # ECS Service
        service = aws.ecs.Service(
            f"{self.args.name}-{dashboard_type}-service",
            cluster=self.cluster.arn,
            task_definition=task_definition.arn,
            desired_count=2,
            launch_type="FARGATE",
            network_configuration=aws.ecs.ServiceNetworkConfigurationArgs(
                subnets=[subnet.id for subnet in self.private_subnets],
                security_groups=[self.dashboard_sg.id],
                assign_public_ip=False,
            ),
            load_balancers=[
                aws.ecs.ServiceLoadBalancerArgs(
                    target_group_arn=self._create_target_group(dashboard_type).arn,
                    container_name=f"{dashboard_type}-dashboard",
                    container_port=3000,
                )
            ],
            depends_on=[self.load_balancer],
        )

        return {
            "service": service,
            "task_definition": task_definition,
            "url": pulumi.Output.concat(
                "https://", self.load_balancer.dns_name, f"/{dashboard_type}"
            ),
        }

    def _create_ai_dashboard_generator(self):
        """Create AI-powered dashboard generator service"""
        # This service uses Cursor AI + Pulumi AI to generate dashboards on-demand
        task_definition = aws.ecs.TaskDefinition(
            f"{self.args.name}-ai-generator-task",
            family=f"{self.args.name}-ai-generator",
            cpu="1024",
            memory="2048",
            network_mode="awsvpc",
            requires_compatibility=["FARGATE"],
            execution_role_arn=self._get_execution_role().arn,
            task_role_arn=self._get_task_role().arn,
            container_definitions=pulumi.Output.json_dumps(
                [
                    {
                        "name": "ai-dashboard-generator",
                        "image": "sophia-ai-dashboard-generator:latest",
                        "essential": True,
                        "portMappings": [{"containerPort": 8080, "protocol": "tcp"}],
                        "environment": [
                            {"name": "OPENAI_API_KEY", "value": "${OPENAI_API_KEY}"},
                            {
                                "name": "ANTHROPIC_API_KEY",
                                "value": "${ANTHROPIC_API_KEY}",
                            },
                            {
                                "name": "PULUMI_ACCESS_TOKEN",
                                "value": "${PULUMI_ACCESS_TOKEN}",
                            },
                            {
                                "name": "DASHBOARD_GENERATION_MODE",
                                "value": "ai-powered",
                            },
                            {
                                "name": "SUPPORTED_FRAMEWORKS",
                                "value": "react,vue,svelte,next",
                            },
                            {"name": "AI_MODEL", "value": "claude-3-sonnet"},
                        ],
                        "logConfiguration": {
                            "logDriver": "awslogs",
                            "options": {
                                "awslogs-group": f"/ecs/{self.args.name}-ai-generator",
                                "awslogs-region": self.args.region,
                                "awslogs-stream-prefix": "ecs",
                            },
                        },
                    }
                ]
            ),
        )

        # CloudWatch log group
        aws.cloudwatch.LogGroup(
            f"{self.args.name}-ai-generator-logs",
            name=f"/ecs/{self.args.name}-ai-generator",
            retention_in_days=30,
        )

        # ECS Service
        service = aws.ecs.Service(
            f"{self.args.name}-ai-generator-service",
            cluster=self.cluster.arn,
            task_definition=task_definition.arn,
            desired_count=1,
            launch_type="FARGATE",
            network_configuration=aws.ecs.ServiceNetworkConfigurationArgs(
                subnets=[subnet.id for subnet in self.private_subnets],
                security_groups=[self.dashboard_sg.id],
                assign_public_ip=False,
            ),
        )

        return {
            "service": service,
            "task_definition": task_definition,
            "url": pulumi.Output.concat(
                "https://", self.load_balancer.dns_name, "/ai-generator"
            ),
        }

    def _create_load_balancer(self):
        """Create Application Load Balancer for dashboard services"""
        # ALB Security Group
        alb_sg = aws.ec2.SecurityGroup(
            f"{self.args.name}-alb-sg",
            description="Security group for dashboard ALB",
            vpc_id=self.vpc.id,
            ingress=[
                aws.ec2.SecurityGroupIngressArgs(
                    protocol="tcp", from_port=80, to_port=80, cidr_blocks=["0.0.0.0/0"]
                ),
                aws.ec2.SecurityGroupIngressArgs(
                    protocol="tcp",
                    from_port=443,
                    to_port=443,
                    cidr_blocks=["0.0.0.0/0"],
                ),
            ],
            egress=[
                aws.ec2.SecurityGroupEgressArgs(
                    protocol="-1", from_port=0, to_port=0, cidr_blocks=["0.0.0.0/0"]
                )
            ],
        )

        # Application Load Balancer
        self.load_balancer = aws.lb.LoadBalancer(
            f"{self.args.name}-dashboard-alb",
            load_balancer_type="application",
            subnets=[subnet.id for subnet in self.public_subnets],
            security_groups=[alb_sg.id],
            tags={
                "Name": f"{self.args.name}-dashboard-alb",
                "Environment": self.args.environment,
            },
        )

        # Default listener (redirect HTTP to HTTPS)
        aws.lb.Listener(
            f"{self.args.name}-http-listener",
            load_balancer_arn=self.load_balancer.arn,
            port="80",
            protocol="HTTP",
            default_actions=[
                aws.lb.ListenerDefaultActionArgs(
                    type="redirect",
                    redirect=aws.lb.ListenerDefaultActionRedirectArgs(
                        port="443", protocol="HTTPS", status_code="HTTP_301"
                    ),
                )
            ],
        )

    def _create_target_group(self, dashboard_type: str):
        """Create target group for dashboard service"""
        return aws.lb.TargetGroup(
            f"{self.args.name}-{dashboard_type}-tg",
            port=3000,
            protocol="HTTP",
            vpc_id=self.vpc.id,
            target_type="ip",
            health_check=aws.lb.TargetGroupHealthCheckArgs(
                enabled=True,
                healthy_threshold=2,
                interval=30,
                matcher="200",
                path="/health",
                port="traffic-port",
                protocol="HTTP",
                timeout=5,
                unhealthy_threshold=2,
            ),
        )

    def _get_execution_role(self):
        """Get or create ECS execution role"""
        if not hasattr(self, "_execution_role"):
            self._execution_role = aws.iam.Role(
                f"{self.args.name}-ecs-execution-role",
                assume_role_policy="""{
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Action": "sts:AssumeRole",
                            "Effect": "Allow",
                            "Principal": {
                                "Service": "ecs-tasks.amazonaws.com"
                            }
                        }
                    ]
                }""",
            )

            aws.iam.RolePolicyAttachment(
                f"{self.args.name}-ecs-execution-policy",
                role=self._execution_role.name,
                policy_arn="arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy",
            )

        return self._execution_role

    def _get_task_role(self):
        """Get or create ECS task role"""
        if not hasattr(self, "_task_role"):
            self._task_role = aws.iam.Role(
                f"{self.args.name}-ecs-task-role",
                assume_role_policy="""{
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Action": "sts:AssumeRole",
                            "Effect": "Allow",
                            "Principal": {
                                "Service": "ecs-tasks.amazonaws.com"
                            }
                        }
                    ]
                }""",
            )

            # Attach policies for accessing AWS services
            task_policy = aws.iam.Policy(
                f"{self.args.name}-ecs-task-policy",
                policy="""{
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Action": [
                                "secretsmanager:GetSecretValue",
                                "ssm:GetParameter",
                                "ssm:GetParameters",
                                "s3:GetObject",
                                "s3:PutObject"
                            ],
                            "Resource": "*"
                        }
                    ]
                }""",
            )

            aws.iam.RolePolicyAttachment(
                f"{self.args.name}-task-policy-attachment",
                role=self._task_role.name,
                policy_arn=task_policy.arn,
            )

        return self._task_role

    def _create_ai_powered_dashboard_generator(self):
        """Create Lambda function for AI-powered dashboard generation"""
        # Lambda function for natural language dashboard creation
        dashboard_generator_lambda = aws.lambda_.Function(
            f"{self.args.name}-dashboard-generator",
            runtime=aws.lambda_.Runtime.PYTHON3_9,
            handler="dashboard_generator.handler",
            code=pulumi.AssetArchive(
                {".": pulumi.FileArchive("../lambda/dashboard-generator")}
            ),
            environment=aws.lambda_.FunctionEnvironmentArgs(
                variables={
                    "OPENAI_API_KEY": "${OPENAI_API_KEY}",
                    "ANTHROPIC_API_KEY": "${ANTHROPIC_API_KEY}",
                    "PULUMI_ACCESS_TOKEN": "${PULUMI_ACCESS_TOKEN}",
                    "ECS_CLUSTER_NAME": self.cluster.name,
                    "VPC_ID": self.vpc.id,
                    "SUBNET_IDS": pulumi.Output.all(
                        *[s.id for s in self.private_subnets]
                    ).apply(lambda ids: ",".join(ids)),
                }
            ),
            timeout=300,
            memory_size=1024,
        )

        # API Gateway for dashboard generation
        api_gateway = aws.apigateway.RestApi(
            f"{self.args.name}-dashboard-api",
            description="API for AI-powered dashboard generation",
        )

        # API Gateway integration with Lambda
        generate_resource = aws.apigateway.Resource(
            f"{self.args.name}-generate-resource",
            rest_api=api_gateway.id,
            parent_id=api_gateway.root_resource_id,
            path_part="generate-dashboard",
        )

        generate_method = aws.apigateway.Method(
            f"{self.args.name}-generate-method",
            rest_api=api_gateway.id,
            resource_id=generate_resource.id,
            http_method="POST",
            authorization="NONE",
        )

        integration = aws.apigateway.Integration(
            f"{self.args.name}-lambda-integration",
            rest_api=api_gateway.id,
            resource_id=generate_resource.id,
            http_method=generate_method.http_method,
            integration_http_method="POST",
            type="AWS_PROXY",
            uri=dashboard_generator_lambda.invoke_arn,
        )

        # Lambda permission for API Gateway
        aws.lambda_.Permission(
            f"{self.args.name}-lambda-permission",
            statement_id="AllowExecutionFromAPIGateway",
            action="lambda:InvokeFunction",
            function=dashboard_generator_lambda.name,
            principal="apigateway.amazonaws.com",
            source_arn=pulumi.Output.concat(api_gateway.execution_arn, "/*/*"),
        )

        # Deploy API Gateway
        deployment = aws.apigateway.Deployment(
            f"{self.args.name}-api-deployment",
            rest_api=api_gateway.id,
            depends_on=[integration],
        )

        stage = aws.apigateway.Stage(
            f"{self.args.name}-api-stage",
            deployment=deployment.id,
            rest_api=api_gateway.id,
            stage_name="prod",
        )

        return {
            "api_url": pulumi.Output.concat(
                "https://",
                api_gateway.id,
                ".execute-api.",
                self.args.region,
                ".amazonaws.com/prod/generate-dashboard",
            ),
            "lambda_function": dashboard_generator_lambda,
        }


class DashboardPlatformArgs:
    """Arguments for DashboardPlatform component"""

    def __init__(
        self,
        name: str,
        environment: str,
        region: str,
        availability_zones: List[str],
        backend_url: str,
        dashboard_types: Optional[List[str]] = None,
    ):
        self.name = name
        self.environment = environment
        self.region = region
        self.availability_zones = availability_zones
        self.backend_url = backend_url
        self.dashboard_types = dashboard_types or ["ceo", "knowledge", "project"]
