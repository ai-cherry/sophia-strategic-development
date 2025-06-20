import asyncio
import json
import os
from datetime import datetime
from typing import Any, Dict, List

import anthropic
import boto3
import openai

# Initialize clients
openai_client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
anthropic_client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
ecs_client = boto3.client("ecs")
ec2_client = boto3.client("ec2")


class AIDashboardGenerator:
    """AI-powered dashboard generator using natural language"""

    def __init__(self):
        self.cluster_name = os.environ.get("ECS_CLUSTER_NAME")
        self.vpc_id = os.environ.get("VPC_ID")
        self.subnet_ids = os.environ.get("SUBNET_IDS", "").split(",")

    async def generate_dashboard(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a dashboard from natural language description"""
        try:
            description = request.get("description", "")
            dashboard_type = request.get("type", "custom")
            data_sources = request.get("data_sources", [])
            features = request.get("features", [])

            # Use Claude to understand the requirements
            requirements = await self._analyze_requirements(
                description, data_sources, features
            )

            # Generate React component code
            react_code = await self._generate_react_component(requirements)

            # Generate backend API endpoints
            api_code = await self._generate_api_endpoints(requirements)

            # Generate Pulumi infrastructure code
            infrastructure_code = await self._generate_infrastructure_code(requirements)

            # Create deployment package
            deployment_result = await self._deploy_dashboard(
                dashboard_type, react_code, api_code, infrastructure_code
            )

            return {
                "success": True,
                "dashboard_id": deployment_result["dashboard_id"],
                "dashboard_url": deployment_result["url"],
                "requirements": requirements,
                "generated_code": {
                    "react": react_code[:500] + "...",  # Truncate for response
                    "api": api_code[:500] + "...",
                    "infrastructure": infrastructure_code[:500] + "...",
                },
                "deployment_status": deployment_result["status"],
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }

    async def _analyze_requirements(
        self, description: str, data_sources: List[str], features: List[str]
    ) -> Dict[str, Any]:
        """Analyze natural language requirements using Claude"""
        prompt = f"""
        Analyze this dashboard requirement and extract structured information:

        Description: {description}
        Data Sources: {', '.join(data_sources)}
        Features: {', '.join(features)}

        Extract and return JSON with:
        1. dashboard_purpose: What is this dashboard for?
        2. target_users: Who will use this dashboard?
        3. key_metrics: What metrics should be displayed?
        4. data_integrations: What APIs/databases are needed?
        5. ui_components: What UI components are needed (charts, tables, forms, etc.)?
        6. layout_structure: How should the dashboard be organized?
        7. interactivity: What interactive features are needed?
        8. update_frequency: How often should data refresh?

        Context: This is for Sophia AI, a business intelligence platform for Pay Ready company.
        Available integrations: Gong, Snowflake, HubSpot, Slack, Linear, GitHub, OpenAI, Pinecone
        """

        response = await anthropic_client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}],
        )

        try:
            return json.loads(response.content[0].text)
        except json.JSONDecodeError:
            # Fallback parsing if JSON is not perfect
            return self._parse_requirements_fallback(response.content[0].text)

    async def _generate_react_component(self, requirements: Dict[str, Any]) -> str:
        """Generate React dashboard component using OpenAI"""
        prompt = f"""
        Generate a complete React dashboard component based on these requirements:

        {json.dumps(requirements, indent=2)}

        Requirements:
        1. Use modern React with hooks (functional components)
        2. Use Tailwind CSS for styling
        3. Include proper TypeScript types
        4. Use React Query for data fetching
        5. Include loading states and error handling
        6. Make it responsive and accessible
        7. Use Recharts for data visualization
        8. Include proper component structure and organization

        Generate a complete, production-ready component that can be deployed immediately.
        Include imports, interfaces, and the main component.
        """

        response = await openai_client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert React developer creating production-ready dashboard components.",
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=3000,
            temperature=0.1,
        )

        return response.choices[0].message.content

    async def _generate_api_endpoints(self, requirements: Dict[str, Any]) -> str:
        """Generate FastAPI backend endpoints"""
        prompt = f"""
        Generate FastAPI backend endpoints for this dashboard:

        {json.dumps(requirements, indent=2)}

        Requirements:
        1. Use FastAPI with async/await
        2. Include proper Pydantic models
        3. Add authentication and authorization
        4. Include error handling and logging
        5. Add data validation
        6. Include CORS configuration
        7. Add rate limiting
        8. Use proper HTTP status codes

        Generate complete, production-ready API endpoints that integrate with:
        - Sophia AI backend architecture
        - Existing data sources (Snowflake, Gong, etc.)
        - Authentication system
        """

        response = await openai_client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert Python FastAPI developer creating production-ready APIs.",
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=3000,
            temperature=0.1,
        )

        return response.choices[0].message.content

    async def _generate_infrastructure_code(self, requirements: Dict[str, Any]) -> str:
        """Generate Pulumi infrastructure code"""
        prompt = f"""
        Generate Pulumi infrastructure code (Python) for this dashboard:

        {json.dumps(requirements, indent=2)}

        Requirements:
        1. Use AWS ECS Fargate for container hosting
        2. Include Application Load Balancer
        3. Add CloudWatch monitoring and logging
        4. Include proper security groups
        5. Add auto-scaling configuration
        6. Include health checks
        7. Add SSL/TLS termination
        8. Include backup and disaster recovery

        Generate complete Pulumi code that integrates with existing Sophia AI infrastructure.
        """

        response = await openai_client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert DevOps engineer creating production-ready Pulumi infrastructure.",
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=3000,
            temperature=0.1,
        )

        return response.choices[0].message.content

    async def _deploy_dashboard(
        self,
        dashboard_type: str,
        react_code: str,
        api_code: str,
        infrastructure_code: str,
    ) -> Dict[str, Any]:
        """Deploy the generated dashboard"""
        dashboard_id = (
            f"ai-generated-{dashboard_type}-{int(datetime.utcnow().timestamp())}"
        )

        try:
            # Create S3 bucket for code storage
            s3_client = boto3.client("s3")
            bucket_name = f"sophia-ai-generated-dashboards-{os.environ.get('AWS_REGION', 'us-east-1')}"

            # Store generated code in S3
            code_key = f"dashboards/{dashboard_id}/code.json"
            code_package = {
                "react": react_code,
                "api": api_code,
                "infrastructure": infrastructure_code,
                "generated_at": datetime.utcnow().isoformat(),
                "dashboard_id": dashboard_id,
            }

            s3_client.put_object(
                Bucket=bucket_name,
                Key=code_key,
                Body=json.dumps(code_package, indent=2),
                ContentType="application/json",
            )

            # Create ECS task definition for the new dashboard
            task_definition = await self._create_task_definition(
                dashboard_id, dashboard_type
            )

            # Create ECS service
            service = await self._create_ecs_service(
                dashboard_id, task_definition["taskDefinitionArn"]
            )

            # Generate dashboard URL
            dashboard_url = f"https://sophia-dashboards.com/{dashboard_id}"

            return {
                "dashboard_id": dashboard_id,
                "url": dashboard_url,
                "status": "deployed",
                "task_definition_arn": task_definition["taskDefinitionArn"],
                "service_arn": service["service"]["serviceArn"],
                "code_location": f"s3://{bucket_name}/{code_key}",
            }

        except Exception as e:
            return {
                "dashboard_id": dashboard_id,
                "url": None,
                "status": "failed",
                "error": str(e),
            }

    async def _create_task_definition(
        self, dashboard_id: str, dashboard_type: str
    ) -> Dict[str, Any]:
        """Create ECS task definition for the dashboard"""
        task_definition = {
            "family": f"sophia-ai-dashboard-{dashboard_id}",
            "networkMode": "awsvpc",
            "requiresCompatibilities": ["FARGATE"],
            "cpu": "512",
            "memory": "1024",
            "executionRoleArn": f"arn:aws:iam::{boto3.Session().get_credentials().access_key}:role/ecsTaskExecutionRole",
            "containerDefinitions": [
                {
                    "name": f"dashboard-{dashboard_type}",
                    "image": "sophia-ai-dashboard:latest",
                    "essential": True,
                    "portMappings": [{"containerPort": 3000, "protocol": "tcp"}],
                    "environment": [
                        {"name": "DASHBOARD_ID", "value": dashboard_id},
                        {"name": "DASHBOARD_TYPE", "value": dashboard_type},
                        {"name": "API_BASE_URL", "value": "https://api.sophia-ai.com"},
                        {"name": "NODE_ENV", "value": "production"},
                    ],
                    "logConfiguration": {
                        "logDriver": "awslogs",
                        "options": {
                            "awslogs-group": f"/ecs/sophia-ai-dashboard-{dashboard_id}",
                            "awslogs-region": os.environ.get("AWS_REGION", "us-east-1"),
                            "awslogs-stream-prefix": "ecs",
                        },
                    },
                }
            ],
        }

        response = ecs_client.register_task_definition(**task_definition)
        return response["taskDefinition"]

    async def _create_ecs_service(
        self, dashboard_id: str, task_definition_arn: str
    ) -> Dict[str, Any]:
        """Create ECS service for the dashboard"""
        service_definition = {
            "serviceName": f"sophia-ai-dashboard-{dashboard_id}",
            "cluster": self.cluster_name,
            "taskDefinition": task_definition_arn,
            "desiredCount": 1,
            "launchType": "FARGATE",
            "networkConfiguration": {
                "awsvpcConfiguration": {
                    "subnets": self.subnet_ids,
                    "securityGroups": [await self._get_security_group_id()],
                    "assignPublicIp": "DISABLED",
                }
            },
        }

        response = ecs_client.create_service(**service_definition)
        return response

    async def _get_security_group_id(self) -> str:
        """Get security group ID for dashboard services"""
        response = ec2_client.describe_security_groups(
            Filters=[
                {"Name": "group-name", "Values": ["sophia-dashboard-sg"]},
                {"Name": "vpc-id", "Values": [self.vpc_id]},
            ]
        )

        if response["SecurityGroups"]:
            return response["SecurityGroups"][0]["GroupId"]
        else:
            raise Exception("Dashboard security group not found")

    def _parse_requirements_fallback(self, text: str) -> Dict[str, Any]:
        """Fallback parser for requirements if JSON parsing fails"""
        return {
            "dashboard_purpose": "Custom AI-generated dashboard",
            "target_users": ["business users"],
            "key_metrics": ["performance", "usage", "trends"],
            "data_integrations": ["api"],
            "ui_components": ["charts", "tables", "metrics"],
            "layout_structure": "grid",
            "interactivity": ["filters", "drill-down"],
            "update_frequency": "real-time",
        }


def lambda_handler(event, context):
    """AWS Lambda handler for dashboard generation"""
    try:
        # Parse request
        if "body" in event:
            request_body = json.loads(event["body"])
        else:
            request_body = event

        # Initialize generator
        generator = AIDashboardGenerator()

        # Generate dashboard
        result = asyncio.run(generator.generate_dashboard(request_body))

        return {
            "statusCode": 200 if result["success"] else 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization",
            },
            "body": json.dumps(result),
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
            "body": json.dumps(
                {
                    "success": False,
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat(),
                }
            ),
        }


# Example usage for testing
if __name__ == "__main__":
    test_event = {
        "description": "Create a sales performance dashboard that shows revenue trends, top deals, and sales rep performance",
        "type": "sales",
        "data_sources": ["snowflake", "gong", "hubspot"],
        "features": ["real-time-updates", "drill-down-analysis", "export-reports"],
    }

    result = lambda_handler(test_event, None)
    print(json.dumps(result, indent=2))
