#!/usr/bin/env python3
"""
Unified AI Coding Assistant for Sophia AI
Natural language interface to ALL AI coding solutions, agents, and tools
"""

import asyncio
import logging
import os
import subprocess
import sys
from datetime import datetime
from typing import Any

import httpx

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UnifiedAICodingAssistant:
    """
    Master interface for all AI coding solutions in Sophia AI ecosystem
    Provides natural language access to:
    - CLI tools (Gemini, Claude)
    - Specialized agents (Infrastructure, Snowflake, Sales, Marketing, UI/UX)
    - MCP servers (16+ available)
    - Chat interfaces and workflow automation
    """

    def __init__(self):
        self.conversation_history = []
        self.available_solutions = {}
        self.mcp_servers = {}
        self.agents = {}
        self.cli_tools = {}

        # Define solution categories and their capabilities
        self.solution_map = {
            "coding": ["claude_cli", "gemini_cli", "codacy_mcp", "github_mcp"],
            "infrastructure": [
                "infrastructure_agent",
                "pulumi_mcp",
                "docker_mcp",
                "sophia_infrastructure_mcp",
            ],
            "database": ["snowflake_admin_agent", "snowflake_mcp", "postgres_mcp"],
            "business": ["sales_intelligence_agent", "marketing_analysis_agent"],
            "design": ["ui_ux_agent", "figma_mcp"],
            "project": ["linear_mcp", "asana_mcp", "notion_mcp"],
            "communication": ["slack_mcp"],
            "memory": ["ai_memory_mcp"],
            "quality": ["codacy_mcp"],
        }

        # Natural language intent patterns
        self.intent_patterns = {
            "coding": [
                "write code",
                "generate function",
                "debug",
                "refactor",
                "optimize code",
                "create class",
                "fix bug",
                "code review",
                "programming help",
            ],
            "infrastructure": [
                "deploy",
                "scale",
                "monitor system",
                "infrastructure health",
                "server status",
                "performance",
                "optimize infrastructure",
            ],
            "database": [
                "query database",
                "snowflake",
                "sql",
                "data analysis",
                "database health",
                "table structure",
                "data migration",
            ],
            "business": [
                "sales analysis",
                "marketing",
                "revenue",
                "customer data",
                "business intelligence",
                "kpi",
                "metrics",
            ],
            "design": [
                "ui design",
                "ux",
                "figma",
                "component",
                "dashboard",
                "user interface",
                "design system",
            ],
            "project": [
                "project status",
                "task management",
                "linear",
                "asana",
                "project health",
                "team productivity",
            ],
            "communication": ["slack", "notification", "team communication", "alert"],
            "memory": [
                "remember",
                "recall",
                "store context",
                "development history",
                "past decisions",
                "knowledge base",
            ],
            "quality": [
                "code quality",
                "security scan",
                "vulnerabilities",
                "best practices",
                "code analysis",
            ],
        }

    async def initialize(self):
        """Initialize all available AI solutions"""

        # Check available solutions
        await self._discover_solutions()
        await self._check_service_health()

        self._display_capabilities()

    async def _discover_solutions(self):
        """Discover available AI solutions"""

        # Check CLI tools
        self.cli_tools = {
            "claude_cli": await self._check_claude_cli(),
            "gemini_cli": await self._check_gemini_cli(),
        }

        # Check MCP servers
        mcp_ports = {
            "ai_memory": 9000,
            "figma": 9001,
            "ui_ux_agent": 9002,
            "codacy": 3008,
            "asana": 3006,
            "notion": 3007,
        }

        for name, port in mcp_ports.items():
            self.mcp_servers[name] = await self._check_service_health_port(port)

        # Check main Sophia AI services
        self.agents = {
            "sophia_main": await self._check_service_health_port(8000),
            "sophia_frontend": await self._check_service_health_port(3000),
        }

    async def _check_claude_cli(self) -> bool:
        """Check Claude CLI availability"""
        try:
            return bool(os.path.exists("claude-cli-integration/claude"))
        except Exception:
            return False

    async def _check_gemini_cli(self) -> bool:
        """Check Gemini CLI availability"""
        try:
            return bool(
                os.path.exists("gemini-cli-integration/gemini_mcp_integration.py")
            )
        except Exception:
            return False

    async def _check_service_health_port(self, port: int) -> bool:
        """Check if service is running on given port"""
        try:
            async with httpx.AsyncClient(timeout=2) as client:
                response = await client.get(f"http://localhost:{port}/health")
                return response.status_code == 200
        except httpx.RequestError:
            return False

    async def _check_service_health(self):
        """Check health of all services"""
        logger.info("Checking service health...")

        health_status = {}
        for category, services in {
            **self.cli_tools,
            **self.mcp_servers,
            **self.agents,
        }.items():
            health_status[category] = services

        return health_status

    def _display_capabilities(self):
        """Display available capabilities"""

        for _tool, _available in self.cli_tools.items():
            pass

        for _server, _available in self.mcp_servers.items():
            pass

        for _service, _available in self.agents.items():
            pass

    async def process_request(self, user_input: str) -> dict[str, Any]:
        """Process natural language request and route to appropriate solution"""

        # Detect intent
        intent = self._detect_intent(user_input)

        # Log the request
        self.conversation_history.append(
            {
                "timestamp": datetime.now().isoformat(),
                "user_input": user_input,
                "detected_intent": intent,
            }
        )

        # Route to appropriate solution
        if intent == "coding":
            return await self._handle_coding_request(user_input)
        elif intent == "infrastructure":
            return await self._handle_infrastructure_request(user_input)
        elif intent == "database":
            return await self._handle_database_request(user_input)
        elif intent == "business":
            return await self._handle_business_request(user_input)
        elif intent == "design":
            return await self._handle_design_request(user_input)
        elif intent == "project":
            return await self._handle_project_request(user_input)
        elif intent == "communication":
            return await self._handle_communication_request(user_input)
        elif intent == "memory":
            return await self._handle_memory_request(user_input)
        elif intent == "quality":
            return await self._handle_quality_request(user_input)
        else:
            return await self._handle_general_request(user_input)

    def _detect_intent(self, user_input: str) -> str:
        """Detect user intent from natural language input"""
        user_input_lower = user_input.lower()

        # Score each intent category
        intent_scores = {}
        for intent, patterns in self.intent_patterns.items():
            score = sum(1 for pattern in patterns if pattern in user_input_lower)
            if score > 0:
                intent_scores[intent] = score

        # Return highest scoring intent or 'general' if no match
        if intent_scores:
            return max(intent_scores.items(), key=lambda x: x[1])[0]
        return "general"

    async def _handle_coding_request(self, user_input: str) -> dict[str, Any]:
        """Handle coding-related requests"""

        # Prefer Claude CLI for coding tasks
        if self.cli_tools.get("claude_cli", False):
            return await self._call_claude_cli(user_input)
        elif self.cli_tools.get("gemini_cli", False):
            return await self._call_gemini_cli(user_input)
        else:
            return await self._call_sophia_main_chat(user_input)

    async def _handle_infrastructure_request(self, user_input: str) -> dict[str, Any]:
        """Handle infrastructure-related requests"""

        # Use infrastructure chat interface
        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "backend/services/infrastructure_chat/sophia_infrastructure_chat.py",
                    user_input,
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )

            return {
                "solution": "infrastructure_agent",
                "response": result.stdout if result.returncode == 0 else result.stderr,
                "success": result.returncode == 0,
            }
        except Exception as e:
            return {
                "solution": "infrastructure_agent",
                "response": f"Error: {e}",
                "success": False,
            }

    async def _handle_database_request(self, user_input: str) -> dict[str, Any]:
        """Handle database-related requests"""

        # Route to Snowflake admin agent or main chat
        return await self._call_sophia_main_chat(f"Snowflake: {user_input}")

    async def _handle_business_request(self, user_input: str) -> dict[str, Any]:
        """Handle business intelligence requests"""

        return await self._call_sophia_main_chat(f"Business Intelligence: {user_input}")

    async def _handle_design_request(self, user_input: str) -> dict[str, Any]:
        """Handle design-related requests"""

        # Check if UI/UX agent is available
        if self.mcp_servers.get("ui_ux_agent", False):
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        "http://localhost:9002/analyze-design",
                        json={"query": user_input},
                    )
                    return {
                        "solution": "ui_ux_agent",
                        "response": response.json(),
                        "success": response.status_code == 200,
                    }
            except Exception as e:
                return {
                    "solution": "ui_ux_agent",
                    "response": f"Error: {e}",
                    "success": False,
                }

        return await self._call_sophia_main_chat(f"Design: {user_input}")

    async def _handle_project_request(self, user_input: str) -> dict[str, Any]:
        """Handle project management requests"""

        return await self._call_sophia_main_chat(f"Project Management: {user_input}")

    async def _handle_communication_request(self, user_input: str) -> dict[str, Any]:
        """Handle communication requests"""

        return await self._call_sophia_main_chat(f"Slack: {user_input}")

    async def _handle_memory_request(self, user_input: str) -> dict[str, Any]:
        """Handle AI memory requests"""

        # Use AI Memory MCP server if available
        if self.mcp_servers.get("ai_memory", False):
            # Implementation would call AI Memory MCP server
            pass

        return await self._call_sophia_main_chat(f"Memory: {user_input}")

    async def _handle_quality_request(self, user_input: str) -> dict[str, Any]:
        """Handle code quality requests"""

        # Use Codacy MCP server if available
        if self.mcp_servers.get("codacy", False):
            # Implementation would call Codacy MCP server
            pass

        return await self._call_sophia_main_chat(f"Code Quality: {user_input}")

    async def _handle_general_request(self, user_input: str) -> dict[str, Any]:
        """Handle general requests"""

        return await self._call_sophia_main_chat(user_input)

    async def _call_claude_cli(self, user_input: str) -> dict[str, Any]:
        """Call Claude CLI"""
        try:
            result = subprocess.run(
                ["./claude-cli-integration/claude", user_input],
                capture_output=True,
                text=True,
                timeout=30,
            )

            return {
                "solution": "claude_cli",
                "response": result.stdout if result.returncode == 0 else result.stderr,
                "success": result.returncode == 0,
            }
        except Exception as e:
            return {
                "solution": "claude_cli",
                "response": f"Error: {e}",
                "success": False,
            }

    async def _call_gemini_cli(self, user_input: str) -> dict[str, Any]:
        """Call Gemini CLI"""
        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "gemini-cli-integration/gemini_mcp_integration.py",
                    user_input,
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )

            return {
                "solution": "gemini_cli",
                "response": result.stdout if result.returncode == 0 else result.stderr,
                "success": result.returncode == 0,
            }
        except Exception as e:
            return {
                "solution": "gemini_cli",
                "response": f"Error: {e}",
                "success": False,
            }

    async def _call_sophia_main_chat(self, user_input: str) -> dict[str, Any]:
        """Call main Sophia AI chat interface"""
        try:
            # Use the main Sophia AI backend API
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "http://localhost:8000/chat", json={"message": user_input}
                )

                return {
                    "solution": "sophia_main",
                    "response": response.json(),
                    "success": response.status_code == 200,
                }
        except Exception as e:
            return {
                "solution": "sophia_main",
                "response": f"Error: {e}",
                "success": False,
            }

    async def interactive_session(self):
        """Start interactive chat session"""

        while True:
            try:
                user_input = input("You: ").strip()

                if user_input.lower() in ["exit", "quit", "bye"]:
                    break

                if not user_input:
                    continue

                # Process the request
                result = await self.process_request(user_input)

                # Display response
                if result["success"]:
                    pass
                else:
                    pass

            except KeyboardInterrupt:
                break
            except Exception:
                continue


async def main():
    """Main entry point"""
    assistant = UnifiedAICodingAssistant()
    await assistant.initialize()
    await assistant.interactive_session()


if __name__ == "__main__":
    asyncio.run(main())
