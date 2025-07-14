#!/usr/bin/env python3
"""
Sophia AI - Infrastructure as Code Orchestrator
Central AI agent for managing all platform configurations and integrations
"""

import asyncio
import json
import logging
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# LangChain imports
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate
from langchain.tools import BaseTool
from langchain_openai import ChatOpenAI

from backend.infrastructure.adapters.apollo_adapter import ApolloAdapter
from backend.infrastructure.adapters.asana_adapter import AsanaAdapter
from backend.infrastructure.adapters.estuary_adapter import EstuaryAdapter
from backend.infrastructure.adapters.figma_adapter import FigmaAdapter
from backend.infrastructure.adapters.gong_adapter import GongAdapter
from backend.infrastructure.adapters.hubspot_adapter import HubSpotAdapter
from backend.infrastructure.adapters.lambda_labs_adapter import LambdaLabsAdapter
from backend.infrastructure.adapters.linear_adapter import LinearAdapter
from backend.infrastructure.adapters.openrouter_adapter import OpenRouterAdapter
from backend.infrastructure.adapters.portkey_adapter import PortkeyAdapter
from backend.infrastructure.adapters.slack_adapter import SlackAdapter

# Platform adapters
from backend.infrastructure.adapters.snowflake_adapter import SnowflakeAdapter
from backend.infrastructure.adapters.usergems_adapter import UserGemsAdapter
from backend.infrastructure.adapters.vercel_adapter import VercelAdapter
from backend.infrastructure.core.dependency_manager import DependencyManager
from backend.infrastructure.core.policy_engine import PolicyEngine

# Core infrastructure components
from backend.infrastructure.core.state_manager import InfrastructureStateManager
from backend.infrastructure.core.webhook_router import WebhookRouter
from core.config_manager import get_config_value


class PlatformType(Enum):
    """Platform categories for organized management."""

    DATA_STACK = "data_stack"
    DEV_STACK = "dev_stack"
    AI_STACK = "ai_stack"
    OPS_STACK = "ops_stack"


@dataclass
class PlatformStatus:
    """Status information for a platform."""

    name: str
    type: PlatformType
    status: str  # "healthy", "degraded", "down", "unknown"
    last_check: datetime
    configuration: dict[str, Any] = field(default_factory=dict)
    metrics: dict[str, Any] = field(default_factory=dict)
    dependencies: list[str] = field(default_factory=list)
    webhooks_active: bool = False


@dataclass
class InfrastructureCommand:
    """Command structure for infrastructure operations."""

    command: str
    platforms: list[str]
    parameters: dict[str, Any] = field(default_factory=dict)
    rollback_plan: dict[str, Any] | None = None
    dry_run: bool = False


class PlatformAdapter(ABC):
    """Abstract base class for all platform adapters."""

    def __init__(self, name: str, platform_type: PlatformType):
        self.name = name
        self.platform_type = platform_type
        self.logger = logging.getLogger(f"adapter.{name}")

    @abstractmethod
    async def configure(self, config: dict[str, Any]) -> dict[str, Any]:
        """Configure the platform with given settings."""
        pass

    @abstractmethod
    async def get_status(self) -> PlatformStatus:
        """Get current platform status and health."""
        pass

    @abstractmethod
    async def handle_webhook(self, payload: dict[str, Any]) -> None:
        """Handle incoming webhooks from the platform."""
        pass

    @abstractmethod
    async def validate_configuration(self, config: dict[str, Any]) -> bool:
        """Validate configuration before applying."""
        pass

    async def rollback(self, checkpoint: dict[str, Any]) -> dict[str, Any]:
        """Rollback to a previous configuration state."""
        return {"success": False, "error": "Rollback not implemented"}


class SophiaIaCOrchestrator:
    """
    Central AI orchestrator for managing all infrastructure platforms.
    Uses LangChain for intelligent decision making and natural language processing.
    """

    def __init__(self):
        self.setup_logging()
        self.platform_adapters: dict[str, PlatformAdapter] = {}
        self.state_manager = InfrastructureStateManager()
        self.policy_engine = PolicyEngine()
        self.webhook_router = WebhookRouter()
        self.dependency_manager = DependencyManager()

        # Initialize LangChain agent
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.1,
            openai_api_key=get_config_value("openai_api_key"),
        )

        self.agent_executor = None
        self._initialize_adapters()
        self._setup_agent()

    def setup_logging(self):
        """Configure logging for the orchestrator."""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler("sophia_iac_orchestrator.log"),
                logging.StreamHandler(),
            ],
        )
        self.logger = logging.getLogger("sophia.iac.orchestrator")

    def _initialize_adapters(self):
        """Initialize all platform adapters."""
        # Data Stack
        self.platform_adapters["snowflake"] = SnowflakeAdapter(
            "snowflake", PlatformType.DATA_STACK
        )
        self.platform_adapters["estuary"] = EstuaryAdapter(
            "estuary", PlatformType.DATA_STACK
        )
        self.platform_adapters["hubspot"] = HubSpotAdapter(
            "hubspot", PlatformType.DATA_STACK
        )
        self.platform_adapters["gong"] = GongAdapter("gong", PlatformType.DATA_STACK)
        self.platform_adapters["usergems"] = UserGemsAdapter(
            "usergems", PlatformType.DATA_STACK
        )
        self.platform_adapters["apollo"] = ApolloAdapter(
            "apollo", PlatformType.DATA_STACK
        )

        # Dev Stack
        self.platform_adapters["vercel"] = VercelAdapter(
            "vercel", PlatformType.DEV_STACK
        )
        self.platform_adapters["lambda_labs"] = LambdaLabsAdapter(
            "lambda_labs", PlatformType.DEV_STACK
        )
        self.platform_adapters["figma"] = FigmaAdapter("figma", PlatformType.DEV_STACK)

        # AI Stack
        self.platform_adapters["portkey"] = PortkeyAdapter(
            "portkey", PlatformType.AI_STACK
        )
        self.platform_adapters["openrouter"] = OpenRouterAdapter(
            "openrouter", PlatformType.AI_STACK
        )

        # Ops Stack
        self.platform_adapters["slack"] = SlackAdapter("slack", PlatformType.OPS_STACK)
        self.platform_adapters["linear"] = LinearAdapter(
            "linear", PlatformType.OPS_STACK
        )
        self.platform_adapters["asana"] = AsanaAdapter("asana", PlatformType.OPS_STACK)

        self.logger.info(f"Initialized {len(self.platform_adapters)} platform adapters")

    def _setup_agent(self):
        """Setup the LangChain agent with infrastructure management tools."""
        tools = [
            self._create_configure_platform_tool(),
            self._create_get_status_tool(),
            self._create_execute_command_tool(),
            self._create_manage_dependencies_tool(),
            self._create_rollback_tool(),
        ]

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """You are Sophia, an AI Infrastructure as Code orchestrator. You manage all platform configurations and integrations for a comprehensive technology stack.

Your capabilities include:
- Configuring and managing 14+ platforms across data, dev, AI, and ops stacks
- Understanding dependencies between platforms
- Executing complex multi-platform operations
- Providing intelligent recommendations for optimization
- Handling rollbacks and error recovery

Platforms you manage:
Data Stack: Snowflake, Estuary, HubSpot, Gong, UserGems, Apollo.io
Dev Stack: Vercel, Lambda Labs, Figma
AI Stack: Portkey, OpenRouter
Ops Stack: Slack, Linear, Asana

Always consider:
1. Dependencies between platforms
2. Security and compliance requirements
3. Cost optimization opportunities
4. Performance implications
5. Rollback strategies

Respond with specific, actionable steps and use the available tools to execute operations.""",
                ),
                ("human", "{input}"),
                (
                    "assistant",
                    "I'll help you manage your infrastructure. Let me analyze your request and execute the appropriate operations.",
                ),
                ("placeholder", "{agent_scratchpad}"),
            ]
        )

        agent = create_openai_functions_agent(self.llm, tools, prompt)
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            return_intermediate_steps=True,
            max_iterations=10,
        )

    def _create_configure_platform_tool(self) -> BaseTool:
        """Create tool for configuring platforms."""

        class ConfigurePlatformTool(BaseTool):
            name = "configure_platform"
            description = "Configure a specific platform with given settings"
            orchestrator = self

            def _run(self, platform: str, config: dict[str, Any]) -> str:
                return asyncio.run(
                    self.orchestrator._configure_platform(platform, config)
                )

        return ConfigurePlatformTool()

    def _create_get_status_tool(self) -> BaseTool:
        """Create tool for getting platform status."""

        class GetStatusTool(BaseTool):
            name = "get_platform_status"
            description = "Get current status and health of platforms"
            orchestrator = self

            def _run(self, platforms: list[str] | None = None) -> str:
                return asyncio.run(self.orchestrator._get_platform_status(platforms))

        return GetStatusTool()

    def _create_execute_command_tool(self) -> BaseTool:
        """Create tool for executing infrastructure commands."""

        class ExecuteCommandTool(BaseTool):
            name = "execute_infrastructure_command"
            description = (
                "Execute complex infrastructure operations across multiple platforms"
            )
            orchestrator = self

            def _run(
                self,
                command: str,
                platforms: list[str],
                parameters: dict[str, Any] | None = None,
            ) -> str:
                return asyncio.run(
                    self.orchestrator._execute_infrastructure_command(
                        command, platforms, parameters or {}
                    )
                )

        return ExecuteCommandTool()

    def _create_manage_dependencies_tool(self) -> BaseTool:
        """Create tool for managing platform dependencies."""

        class ManageDependenciesTool(BaseTool):
            name = "manage_dependencies"
            description = "Analyze and manage dependencies between platforms"
            orchestrator = self

            def _run(self, operation: str) -> str:
                return asyncio.run(self.orchestrator._manage_dependencies(operation))

        return ManageDependenciesTool()

    def _create_rollback_tool(self) -> BaseTool:
        """Create tool for rollback operations."""

        class RollbackTool(BaseTool):
            name = "rollback_changes"
            description = "Rollback recent changes to platforms"
            orchestrator = self

            def _run(self, platforms: list[str], checkpoint_id: str) -> str:
                return asyncio.run(
                    self.orchestrator._rollback_changes(platforms, checkpoint_id)
                )

        return RollbackTool()

    async def _configure_platform(self, platform: str, config: dict[str, Any]) -> str:
        """Configure a specific platform."""
        if platform not in self.platform_adapters:
            return f"Platform '{platform}' not found"

        try:
            adapter = self.platform_adapters[platform]

            # Validate configuration
            if not await adapter.validate_configuration(config):
                return f"Configuration validation failed for {platform}"

            # Create checkpoint for rollback
            current_status = await adapter.get_status()
            checkpoint_id = await self.state_manager.create_checkpoint(
                platform, current_status.configuration
            )

            # Apply configuration
            await adapter.configure(config)

            # Update state
            await self.state_manager.update_platform_state(platform, config)

            self.logger.info(f"Successfully configured {platform}")
            return f"Successfully configured {platform}. Checkpoint: {checkpoint_id}"

        except Exception as e:
            self.logger.exception(f"Failed to configure {platform}: {e}")
            return f"Failed to configure {platform}: {e!s}"

    async def _get_platform_status(self, platforms: list[str] | None = None) -> str:
        """Get status of specified platforms or all platforms."""
        target_platforms = platforms or list(self.platform_adapters.keys())
        status_report = {"timestamp": datetime.now().isoformat(), "platforms": {}}

        for platform_name in target_platforms:
            if platform_name in self.platform_adapters:
                try:
                    adapter = self.platform_adapters[platform_name]
                    status = await adapter.get_status()
                    status_report["platforms"][platform_name] = {
                        "status": status.status,
                        "type": status.type.value,
                        "last_check": status.last_check.isoformat(),
                        "webhooks_active": status.webhooks_active,
                        "dependencies": status.dependencies,
                    }
                except Exception as e:
                    status_report["platforms"][platform_name] = {
                        "status": "error",
                        "error": str(e),
                    }

        return json.dumps(status_report, indent=2)

    async def _execute_infrastructure_command(
        self, command: str, platforms: list[str], parameters: dict[str, Any]
    ) -> str:
        """Execute a complex infrastructure command across multiple platforms."""
        try:
            # Analyze dependencies
            execution_order = await self.dependency_manager.get_execution_order(
                platforms
            )

            results = {}
            for platform in execution_order:
                if platform in self.platform_adapters:
                    adapter = self.platform_adapters[platform]

                    # Execute platform-specific command
                    if hasattr(adapter, f"execute_{command}"):
                        method = getattr(adapter, f"execute_{command}")
                        result = await method(parameters)
                        results[platform] = result
                    else:
                        results[platform] = {
                            "error": f"Command '{command}' not supported"
                        }

            return json.dumps(results, indent=2)

        except Exception as e:
            self.logger.exception(f"Failed to execute command '{command}': {e}")
            return f"Failed to execute command: {e!s}"

    async def _manage_dependencies(self, operation: str) -> str:
        """Manage platform dependencies."""
        try:
            if operation == "analyze":
                dependencies = await self.dependency_manager.analyze_dependencies()
                return json.dumps(dependencies, indent=2)
            elif operation == "validate":
                validation_result = (
                    await self.dependency_manager.validate_dependencies()
                )
                return json.dumps(validation_result, indent=2)
            else:
                return f"Unknown dependency operation: {operation}"
        except Exception as e:
            return f"Dependency management failed: {e!s}"

    async def _rollback_changes(self, platforms: list[str], checkpoint_id: str) -> str:
        """Rollback changes to specified platforms."""
        try:
            results = {}
            for platform in platforms:
                if platform in self.platform_adapters:
                    adapter = self.platform_adapters[platform]
                    checkpoint = await self.state_manager.get_checkpoint(
                        platform, checkpoint_id
                    )

                    if checkpoint:
                        result = await adapter.rollback(checkpoint)
                        results[platform] = result
                    else:
                        results[platform] = {"error": "Checkpoint not found"}

            return json.dumps(results, indent=2)

        except Exception as e:
            return f"Rollback failed: {e!s}"

    async def process_natural_language_command(self, command: str) -> str:
        """Process natural language infrastructure commands."""
        try:
            self.logger.info(f"Processing command: {command}")

            result = await self.agent_executor.ainvoke({"input": command})

            return result["output"]

        except Exception as e:
            self.logger.exception(f"Failed to process command: {e}")
            return f"Failed to process command: {e!s}"

    async def start_webhook_server(self, port: int = 8000):
        """Start the webhook server for receiving platform events."""
        await self.webhook_router.start_server(port, self.platform_adapters)

    async def health_check(self) -> dict[str, Any]:
        """Perform comprehensive health check of all platforms."""
        health_report = {
            "timestamp": datetime.now().isoformat(),
            "orchestrator_status": "healthy",
            "platforms": {},
            "dependencies": {},
            "recommendations": [],
        }

        # Check all platforms
        for name, adapter in self.platform_adapters.items():
            try:
                status = await adapter.get_status()
                health_report["platforms"][name] = {
                    "status": status.status,
                    "type": status.type.value,
                    "metrics": status.metrics,
                }
            except Exception as e:
                health_report["platforms"][name] = {"status": "error", "error": str(e)}

        # Analyze dependencies
        health_report[
            "dependencies"
        ] = await self.dependency_manager.analyze_dependencies()

        # Generate recommendations
        health_report["recommendations"] = await self._generate_recommendations(
            health_report
        )

        return health_report

    async def _generate_recommendations(
        self, health_report: dict[str, Any]
    ) -> list[str]:
        """Generate intelligent recommendations based on system health."""
        recommendations = []

        # Analyze platform health
        unhealthy_platforms = [
            name
            for name, status in health_report["platforms"].items()
            if status.get("status") not in ["healthy", "operational"]
        ]

        if unhealthy_platforms:
            recommendations.append(
                f"Address issues with: {', '.join(unhealthy_platforms)}"
            )

        # Check for optimization opportunities
        # This would include cost optimization, performance improvements, etc.

        return recommendations


# CLI Interface
async def main():
    """Main entry point for the Sophia IaC Orchestrator."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Sophia AI Infrastructure as Code Orchestrator"
    )
    parser.add_argument("command", help="Command to execute")
    parser.add_argument("--platforms", nargs="+", help="Target platforms")
    parser.add_argument("--config", help="Configuration file path")
    parser.add_argument("--dry-run", action="store_true", help="Dry run mode")

    args = parser.parse_args()

    orchestrator = SophiaIaCOrchestrator()

    if args.command == "status":
        await orchestrator._get_platform_status(args.platforms)
    elif args.command == "health":
        await orchestrator.health_check()
    elif args.command.startswith("configure"):
        if args.config and args.platforms:
            with open(args.config) as f:
                config = json.load(f)
            for platform in args.platforms:
                await orchestrator._configure_platform(platform, config)
    else:
        # Process as natural language command
        await orchestrator.process_natural_language_command(args.command)


if __name__ == "__main__":
    asyncio.run(main())
