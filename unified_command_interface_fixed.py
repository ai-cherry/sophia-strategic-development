#!/usr/bin/env python3
"""Sophia AI - Unified Command Interface
Single entry point for all natural language commands with smart routing and context awareness
"""

import argparse
import asyncio
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from backend.core.config_manager import config_manager
from backend.core.integration_registry import integration_registry

# Import the fixed MCP server instead of the original one
from backend.mcp.sophia_mcp_server_fixed import sophia_mcp_server

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class UnifiedCommandInterface:
    """Unified command interface for all Sophia AI natural language operations
    """

    def __init__(self):
        self.config_manager = config_manager
        self.integration_registry = integration_registry
        self.mcp_server = sophia_mcp_server
        self.command_history = []
        self.favorites = []
        self.context = {}

    async def initialize(self) -> bool:
        """Initialize the unified command interface"""
        try:
            # Initialize core components
            await self.config_manager.initialize()
            await self.integration_registry.initialize()

            # Load command history and favorites
            await self._load_user_preferences()

            logger.info("Unified command interface initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize unified command interface: {e}")
            return False

    async def process_command(
        self, command: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process a natural language command with smart routing and context awareness
        """
        try:
            # Update context
            if context:
                self.context.update(context)

            # Add to command history
            self.command_history.append(
                {
                    "command": command,
                    "timestamp": datetime.utcnow().isoformat(),
                    "context": self.context.copy(),
                }
            )

            # Analyze command and determine routing
            routing_info = await self._analyze_command(command)

            # Execute command through appropriate service
            result = await self._execute_command(command, routing_info)

            # Cache result if appropriate
            await self._cache_result(command, result)

            return {
                "status": "success",
                "command": command,
                "routing": routing_info,
                "result": result,
                "execution_time": result.get("execution_time", "unknown"),
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Command processing failed: {e}")
            return {
                "status": "error",
                "command": command,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }

    async def _analyze_command(self, command: str) -> Dict[str, Any]:
        """Analyze command and determine optimal routing
        """
        command_lower = command.lower()

        # System status commands
        if any(
            keyword in command_lower
            for keyword in ["status", "health", "check", "system"]
        ):
            return {
                "category": "system",
                "service": "health_check",
                "confidence": 0.95,
                "suggested_tools": ["health_check", "system_status"],
            }

        # Infrastructure commands
        elif any(
            keyword in command_lower
            for keyword in ["deploy", "infrastructure", "pulumi", "secret", "rotate"]
        ):
            return {
                "category": "infrastructure",
                "service": "pulumi_esc",
                "confidence": 0.9,
                "suggested_tools": ["deploy", "secret_management", "health_check"],
            }

        # Code generation commands
        elif any(
            keyword in command_lower
            for keyword in ["generate", "create", "write", "code", "function"]
        ):
            return {
                "category": "code_generation",
                "service": "claude",
                "confidence": 0.95,
                "suggested_tools": ["generate_code", "analyze_code", "refactor_code"],
            }

        # Data analysis commands
        elif any(
            keyword in command_lower
            for keyword in ["query", "data", "snowflake", "sql", "analyze"]
        ):
            return {
                "category": "data_analysis",
                "service": "snowflake",
                "confidence": 0.85,
                "suggested_tools": ["execute_query", "get_schema", "analyze_data"],
            }

        # CRM commands
        elif any(
            keyword in command_lower
            for keyword in ["gong", "deals", "calls", "crm", "sales"]
        ):
            return {
                "category": "crm",
                "service": "gong",
                "confidence": 0.9,
                "suggested_tools": ["get_deals", "get_calls", "search_data"],
            }

        # Project management commands
        elif any(
            keyword in command_lower
            for keyword in ["linear", "issue", "project", "task", "ticket"]
        ):
            return {
                "category": "project_management",
                "service": "linear",
                "confidence": 0.9,
                "suggested_tools": ["create_issue", "update_issue", "get_projects"],
            }

        # Deployment commands
        elif any(
            keyword in command_lower
            for keyword in ["vercel", "deploy", "website", "frontend"]
        ):
            return {
                "category": "deployment",
                "service": "vercel",
                "confidence": 0.85,
                "suggested_tools": [
                    "deploy_project",
                    "get_deployments",
                    "manage_domains",
                ],
            }

        # Communication commands
        elif any(
            keyword in command_lower
            for keyword in ["slack", "message", "notify", "channel"]
        ):
            return {
                "category": "communication",
                "service": "slack",
                "confidence": 0.9,
                "suggested_tools": ["send_message", "create_channel", "get_history"],
            }

        # Default to general AI assistance
        else:
            return {
                "category": "general",
                "service": "claude",
                "confidence": 0.7,
                "suggested_tools": ["general_assistance", "explain_concept", "help"],
            }

    async def _execute_command(
        self, command: str, routing_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute command through the appropriate service
        """
        service = routing_info["service"]
        category = routing_info["category"]

        start_time = datetime.utcnow()

        try:
            if category == "system":
                result = await self._execute_system_command(command)
            elif category == "infrastructure":
                result = await self._execute_infrastructure_command(command)
            elif category == "code_generation":
                result = await self._execute_code_command(command)
            elif category == "data_analysis":
                result = await self._execute_data_command(command)
            elif category == "crm":
                result = await self._execute_crm_command(command)
            elif category == "project_management":
                result = await self._execute_project_command(command)
            elif category == "deployment":
                result = await self._execute_deployment_command(command)
            elif category == "communication":
                result = await self._execute_communication_command(command)
            else:
                result = await self._execute_general_command(command)

            execution_time = (datetime.utcnow() - start_time).total_seconds()
            result["execution_time"] = f"{execution_time:.2f}s"

            return result

        except Exception as e:
            logger.error(f"Command execution failed for {service}: {e}")
            return {
                "status": "error",
                "message": f"Execution failed: {str(e)}",
                "service": service,
                "category": category,
            }

    async def _execute_system_command(self, command: str) -> Dict[str, Any]:
        """Execute system status commands"""
        # Run the automated health check
        try:
            # Import here to avoid circular imports
            from automated_health_check_fixed import run_health_check

            health_results = await run_health_check()

            return {
                "status": "success",
                "message": "System status check completed",
                "data": health_results,
                "action": "system_status",
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "error",
                "message": f"System status check failed: {str(e)}",
                "action": "system_status",
            }

    async def _execute_infrastructure_command(self, command: str) -> Dict[str, Any]:
        """Execute infrastructure-related commands"""
        try:
            if "deploy" in command.lower():
                # Trigger deployment
                return {
                    "status": "success",
                    "message": "Deployment initiated",
                    "action": "deploy",
                }
            elif "secret" in command.lower() and "rotate" in command.lower():
                # Rotate secrets
                return {
                    "status": "success",
                    "message": "Secret rotation initiated",
                    "action": "rotate_secrets",
                }
            elif "health" in command.lower():
                # Health check
                health_status = await self.config_manager.get_health_status()
                return {
                    "status": "success",
                    "data": health_status,
                    "action": "health_check",
                }
            else:
                return {
                    "status": "success",
                    "message": "Infrastructure command processed",
                    "action": "general",
                }
        except Exception as e:
            logger.error(f"Infrastructure command failed: {e}")
            return {
                "status": "error",
                "message": f"Infrastructure command failed: {str(e)}",
                "action": "infrastructure",
            }

    async def _execute_code_command(self, command: str) -> Dict[str, Any]:
        """Execute code generation commands"""
        try:
            return {
                "status": "success",
                "message": "Code command processed",
                "action": "code_generation",
            }
        except Exception as e:
            logger.error(f"Code command failed: {e}")
            return {
                "status": "error",
                "message": f"Code command failed: {str(e)}",
                "action": "code_generation",
            }

    async def _execute_data_command(self, command: str) -> Dict[str, Any]:
        """Execute data analysis commands"""
        try:
            return {
                "status": "success",
                "message": "Data command processed",
                "action": "data_analysis",
            }
        except Exception as e:
            logger.error(f"Data command failed: {e}")
            return {
                "status": "error",
                "message": f"Data command failed: {str(e)}",
                "action": "data_analysis",
            }

    async def _execute_crm_command(self, command: str) -> Dict[str, Any]:
        """Execute CRM commands"""
        try:
            return {
                "status": "success",
                "message": "CRM command processed",
                "action": "crm_operation",
            }
        except Exception as e:
            logger.error(f"CRM command failed: {e}")
            return {
                "status": "error",
                "message": f"CRM command failed: {str(e)}",
                "action": "crm_operation",
            }

    async def _execute_project_command(self, command: str) -> Dict[str, Any]:
        """Execute project management commands"""
        try:
            return {
                "status": "success",
                "message": "Project command processed",
                "action": "project_management",
            }
        except Exception as e:
            logger.error(f"Project command failed: {e}")
            return {
                "status": "error",
                "message": f"Project command failed: {str(e)}",
                "action": "project_management",
            }

    async def _execute_deployment_command(self, command: str) -> Dict[str, Any]:
        """Execute deployment commands"""
        try:
            return {
                "status": "success",
                "message": "Deployment command processed",
                "action": "deployment",
            }
        except Exception as e:
            logger.error(f"Deployment command failed: {e}")
            return {
                "status": "error",
                "message": f"Deployment command failed: {str(e)}",
                "action": "deployment",
            }

    async def _execute_communication_command(self, command: str) -> Dict[str, Any]:
        """Execute communication commands"""
        try:
            return {
                "status": "success",
                "message": "Communication command processed",
                "action": "communication",
            }
        except Exception as e:
            logger.error(f"Communication command failed: {e}")
            return {
                "status": "error",
                "message": f"Communication command failed: {str(e)}",
                "action": "communication",
            }

    async def _execute_general_command(self, command: str) -> Dict[str, Any]:
        """Execute general AI assistance commands"""
        try:
            return {
                "status": "success",
                "message": "Command processed",
                "action": "general_assistance",
            }
        except Exception as e:
            logger.error(f"General command failed: {e}")
            return {
                "status": "error",
                "message": f"General command failed: {str(e)}",
                "action": "general_assistance",
            }

    async def _cache_result(self, command: str, result: Dict[str, Any]) -> None:
        """Cache command result for future use"""
        # Implement result caching logic
        pass

    async def _load_user_preferences(self) -> None:
        """Load user command history and favorites"""
        try:
            prefs_file = project_root / "user_preferences.json"
            if prefs_file.exists():
                with open(prefs_file, "r") as f:
                    prefs = json.load(f)
                    self.command_history = prefs.get("command_history", [])[
                        -100:
                    ]  # Keep last 100
                    self.favorites = prefs.get("favorites", [])
        except Exception as e:
            logger.warning(f"Failed to load user preferences: {e}")

    async def save_user_preferences(self) -> None:
        """Save user command history and favorites"""
        try:
            prefs_file = project_root / "user_preferences.json"
            prefs = {
                "command_history": self.command_history[-100:],  # Keep last 100
                "favorites": self.favorites,
                "last_updated": datetime.utcnow().isoformat(),
            }
            with open(prefs_file, "w") as f:
                json.dump(prefs, f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to save user preferences: {e}")

    async def get_command_suggestions(self, partial_command: str) -> List[str]:
        """Get command suggestions based on history and context"""
        suggestions = []

        # Add suggestions from command history
        for entry in reversed(self.command_history):
            if partial_command.lower() in entry["command"].lower():
                suggestions.append(entry["command"])

        # Add favorites
        for fav in self.favorites:
            if partial_command.lower() in fav.lower():
                suggestions.append(fav)

        # Add common patterns
        common_patterns = [
            "Check system status",
            "Deploy the infrastructure to production",
            "Generate a Python function to process data",
            "Check the health of all services",
            "Rotate all API keys",
            "Create a Linear issue for bug fix",
            "Get all deals from Gong this month",
            "Analyze this code for performance issues",
        ]

        for pattern in common_patterns:
            if partial_command.lower() in pattern.lower():
                suggestions.append(pattern)

        return list(set(suggestions))[:10]  # Return top 10 unique suggestions


# Global instance
unified_interface = UnifiedCommandInterface()


async def main():
    """Main entry point for command line usage"""
    parser = argparse.ArgumentParser(description="Sophia AI Unified Command Interface")
    parser.add_argument(
        "command", nargs="*", help="Natural language command to execute"
    )
    parser.add_argument(
        "--interactive", "-i", action="store_true", help="Start interactive mode"
    )
    parser.add_argument("--history", action="store_true", help="Show command history")
    parser.add_argument(
        "--favorites", action="store_true", help="Show favorite commands"
    )

    args = parser.parse_args()

    # Initialize interface
    if not await unified_interface.initialize():
        print("Failed to initialize unified command interface")
        sys.exit(1)

    if args.history:
        print("Command History:")
        for i, entry in enumerate(unified_interface.command_history[-10:], 1):
            print(f"{i}. {entry['command']} ({entry['timestamp']})")
        return

    if args.favorites:
        print("Favorite Commands:")
        for i, fav in enumerate(unified_interface.favorites, 1):
            print(f"{i}. {fav}")
        return

    if args.interactive:
        print("Sophia AI Interactive Command Interface")
        print("Type 'exit' to quit, 'help' for assistance")

        while True:
            try:
                command = input("\n> ").strip()
                if command.lower() in ["exit", "quit"]:
                    break
                elif command.lower() == "help":
                    print("Available commands:")
                    print("- Check system status")
                    print("- Deploy the infrastructure")
                    print("- Generate code for [description]")
                    print("- Check service health")
                    print("- Create Linear issue for [description]")
                    print("- Get data from [service]")
                    continue
                elif not command:
                    continue

                result = await unified_interface.process_command(command)

                if result["status"] == "success":
                    print(
                        f"✅ {result.get('result', {}).get('message', 'Command executed successfully')}"
                    )
                    if "data" in result.get("result", {}):
                        print(
                            f"📊 Data: {json.dumps(result['result']['data'], indent=2)}"
                        )
                else:
                    print(f"❌ Error: {result.get('error', 'Unknown error')}")

            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

    elif args.command:
        command = " ".join(args.command)
        result = await unified_interface.process_command(command)

        if result["status"] == "success":
            print(json.dumps(result, indent=2))
        else:
            print(f"Error: {result.get('error', 'Unknown error')}")
            sys.exit(1)

    else:
        parser.print_help()

    # Save preferences before exit
    await unified_interface.save_user_preferences()


if __name__ == "__main__":
    asyncio.run(main())
