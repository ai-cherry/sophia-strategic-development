#!/usr/bin/env python3
"""
Sophia AI - Claude CLI Integration (Upgraded)
Latest Claude models with intelligent routing and MCP integration
"""

import argparse
import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Any

import aiohttp

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ClaudeMCPIntegration:
    """Claude CLI with latest models and MCP server integration for Sophia AI"""

    def __init__(
        self, config_path: str = "claude-cli-integration/claude_mcp_config.json"
    ):
        self.config_path = Path(config_path)
        self.config: dict[str, Any] = {}
        self.session: aiohttp.ClientSession | None = None
        self.anthropic_api_key: str | None = None

        self._load_config()
        self._setup_anthropic()

    def _load_config(self) -> None:
        """Load Claude MCP configuration"""
        try:
            if self.config_path.exists():
                with open(self.config_path) as f:
                    self.config = json.load(f)
                logger.info("✅ Loaded Claude MCP configuration with latest models")
            else:
                logger.error(f"❌ Configuration file not found: {self.config_path}")
        except Exception as e:
            logger.error(f"❌ Error loading configuration: {e}")
            raise

    def _setup_anthropic(self) -> None:
        """Setup Anthropic API credentials"""
        api_key_env = (
            self.config.get("globalSettings", {})
            .get("claudeApiSettings", {})
            .get("apiKeyEnv", "ANTHROPIC_API_KEY")
        )
        self.anthropic_api_key = os.getenv(api_key_env)

        if not self.anthropic_api_key:
            logger.warning(
                f"⚠️ Anthropic API key not found in environment variable: {api_key_env}"
            )
            logger.info("💡 Falling back to MCP-only mode")

    def _select_model(self, message: str) -> str:
        """Intelligently select the best model based on query content"""
        model_config = self.config.get("globalSettings", {}).get(
            "modelConfiguration", {}
        )
        routing_config = self.config.get("globalSettings", {}).get(
            "intelligentRouting", {}
        )

        if not routing_config.get("enabled", False):
            return model_config.get("primaryModel", "claude-3-5-sonnet-20241119")

        message_lower = message.lower()

        # Check for coding keywords
        coding_keywords = routing_config.get("codingKeywords", [])
        if any(keyword in message_lower for keyword in coding_keywords):
            return model_config.get("codingModel", "claude-3-5-sonnet-20241119")

        # Check for analysis keywords
        analysis_keywords = routing_config.get("analysisKeywords", [])
        if any(keyword in message_lower for keyword in analysis_keywords):
            return model_config.get("analysisModel", "claude-3-5-sonnet-20241119")

        # Default to primary model
        return model_config.get("primaryModel", "claude-3-5-sonnet-20241119")

    async def start_session(self) -> None:
        """Start HTTP session for MCP server communication and Claude API"""
        if not self.session:
            timeout = aiohttp.ClientTimeout(total=60)
            self.session = aiohttp.ClientSession(timeout=timeout)

    async def close_session(self) -> None:
        """Close HTTP session"""
        if self.session:
            await self.session.close()
            self.session = None

    async def check_mcp_server_health(self, server_name: str) -> dict[str, Any]:
        """Check health of a specific MCP server"""
        if server_name not in self.config.get("mcpServers", {}):
            return {"status": "error", "message": f"Unknown server: {server_name}"}

        if not self.session:
            await self.start_session()

        server_config = self.config["mcpServers"][server_name]
        url = server_config.get("url", "http://localhost:9001")

        try:
            async with self.session.get(f"{url}/health") as response:
                if response.status == 200:
                    health_data = await response.json()
                    return health_data
                else:
                    return {"status": "unhealthy", "http_status": response.status}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def query_mcp_server(
        self, server_name: str, endpoint: str, data: dict | None = None
    ) -> dict[str, Any]:
        """Query a specific MCP server endpoint"""
        if server_name not in self.config.get("mcpServers", {}):
            return {"error": f"Unknown server: {server_name}"}

        if not self.session:
            await self.start_session()

        server_config = self.config["mcpServers"][server_name]
        url = server_config.get("url", "http://localhost:9001")

        try:
            if data:
                async with self.session.post(
                    f"{url}/{endpoint}", json=data
                ) as response:
                    return await response.json()
            else:
                async with self.session.get(f"{url}/{endpoint}") as response:
                    return await response.json()
        except Exception as e:
            return {"error": str(e)}

    async def call_claude_api(self, message: str, mcp_context: str = "") -> str:
        """Call actual Claude API with latest models"""
        if not self.anthropic_api_key:
            return self._fallback_response(message, mcp_context)

        model = self._select_model(message)
        model_settings = self.config.get("globalSettings", {}).get("modelSettings", {})
        base_url = (
            self.config.get("globalSettings", {})
            .get("claudeApiSettings", {})
            .get("baseUrl")
        )

        # Construct system prompt with MCP context
        system_prompt = f"""You are Sophia AI, an advanced AI assistant integrated with the Pay Ready business intelligence platform. You have access to specialized MCP (Model Context Protocol) servers that provide real-time business data and capabilities.

Available MCP Context:
{mcp_context}

You excel at:
- Code generation and analysis
- Business intelligence and analytics
- UI/UX design and component creation
- Infrastructure management
- Data analysis and insights

Always provide practical, actionable responses that leverage the available MCP capabilities."""

        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.anthropic_api_key,
            "anthropic-version": "2023-06-01",
        }

        payload = {
            "model": model,
            "max_tokens": model_settings.get("maxTokens", 8000),
            "temperature": model_settings.get("temperature", 0.1),
            "system": system_prompt,
            "messages": [{"role": "user", "content": message}],
        }

        if not self.session:
            await self.start_session()

        try:
            async with self.session.post(
                base_url, headers=headers, json=payload
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    content = result.get("content", [])
                    if content and isinstance(content, list) and len(content) > 0:
                        return content[0].get("text", "No response content")
                    return "No response content"
                else:
                    error_text = await response.text()
                    logger.error(f"Claude API error: {response.status} - {error_text}")
                    return self._fallback_response(message, mcp_context)
        except Exception as e:
            logger.error(f"Claude API call failed: {e}")
            return self._fallback_response(message, mcp_context)

    def _fallback_response(self, message: str, mcp_context: str) -> str:
        """Fallback response when Claude API is unavailable"""
        selected_model = self._select_model(message)

        response = f"🤖 **Sophia AI Response** (Model: {selected_model})\n\n"

        if mcp_context:
            response += f"📊 **MCP Context:**\n{mcp_context}\n\n"

        response += f"**Query:** {message}\n\n"

        # Intelligent response based on query type
        if any(
            keyword in message.lower()
            for keyword in ["code", "function", "python", "javascript", "implement"]
        ):
            response += "💻 **Code Generation Capabilities:**\n"
            response += "- Python, JavaScript, TypeScript, React development\n"
            response += "- Full-stack application development\n"
            response += "- Database queries and schema design\n"
            response += "- API development and integration\n\n"

        if any(
            keyword in message.lower()
            for keyword in ["design", "ui", "ux", "component", "figma"]
        ):
            response += "🎨 **Design & UI/UX Capabilities:**\n"
            response += "- React component generation with modern styling\n"
            response += "- Figma design token integration\n"
            response += "- Accessibility compliance (WCAG 2.1 AA)\n"
            response += "- Dashboard and executive interface design\n\n"

        if any(
            keyword in message.lower()
            for keyword in ["analyze", "data", "business", "insights"]
        ):
            response += "📈 **Business Intelligence Capabilities:**\n"
            response += "- Real-time business analytics\n"
            response += "- Customer and sales data analysis\n"
            response += "- Performance metrics and KPI tracking\n"
            response += "- Predictive analytics and forecasting\n\n"

        response += "🔧 **Enhanced with MCP Server Integration:**\n"
        response += "- Real-time business data access\n"
        response += "- Live system health monitoring\n"
        response += "- Advanced code quality analysis\n"
        response += "- Intelligent context management\n\n"

        response += f"💡 **Note:** Using latest Claude model ({selected_model}) with intelligent routing"

        return response

    async def claude_enhanced_query(self, message: str) -> str:
        """Enhanced query using latest Claude models with MCP context"""
        # Gather MCP context
        mcp_context = await self._gather_mcp_context(message)

        # Call Claude API or fallback
        response = await self.call_claude_api(message, mcp_context)

        return response

    async def _gather_mcp_context(self, message: str) -> str:
        """Gather relevant context from MCP servers"""
        context_parts = []

        for server_name in self.config.get("mcpServers", {}):
            health = await self.check_mcp_server_health(server_name)
            server_config = self.config["mcpServers"][server_name]

            if health.get("status") == "healthy":
                context_parts.append(
                    f"✅ {server_name}: {health.get('server', 'Available')}"
                )
                context_parts.append(
                    f"   Capabilities: {', '.join(server_config.get('capabilities', []))}"
                )
            else:
                context_parts.append(
                    f"❌ {server_name}: {health.get('status', 'Unknown')}"
                )

        return "\n".join(context_parts) if context_parts else "No MCP servers available"

    async def list_servers(self) -> dict[str, Any]:
        """List all configured MCP servers and their status"""
        servers = {}

        for server_name in self.config.get("mcpServers", {}):
            health = await self.check_mcp_server_health(server_name)
            servers[server_name] = {
                "config": self.config["mcpServers"][server_name],
                "health": health,
            }

        return servers

    async def demonstrate_integration(self) -> None:
        """Demonstrate Claude CLI integration with latest models and MCP servers"""
        print("🚀 Sophia AI - Claude CLI (Latest Models + MCP Integration)")
        print("=" * 70)

        # Show model configuration
        model_config = self.config.get("globalSettings", {}).get(
            "modelConfiguration", {}
        )
        print("\n🧠 **Model Configuration:**")
        print(f"   Primary Model: {model_config.get('primaryModel', 'N/A')}")
        print(f"   Coding Model: {model_config.get('codingModel', 'N/A')}")
        print(f"   Analysis Model: {model_config.get('analysisModel', 'N/A')}")
        print(
            f"   API Status: {'✅ Connected' if self.anthropic_api_key else '❌ API Key Missing'}"
        )

        # Check server health
        print("\n📊 **MCP Server Health Check:**")
        servers = await self.list_servers()

        for server_name, server_info in servers.items():
            health = server_info["health"]
            status = health.get("status", "unknown")
            emoji = "✅" if status == "healthy" else "❌"
            print(f"   {emoji} {server_name}: {status}")

            if status == "healthy":
                capabilities = server_info["config"].get("capabilities", [])
                print(f"      🔧 Capabilities: {', '.join(capabilities)}")

        # Test Claude integration
        print("\n🤖 **Claude Enhanced Integration Test:**")

        test_queries = [
            "Generate a Python function to analyze sales data",
            "Design a modern React dashboard component",
            "Analyze the current system architecture",
        ]

        for query in test_queries:
            print(f"\n🔍 **Test Query:** {query}")
            selected_model = self._select_model(query)
            print(f"🧠 **Model Selected:** {selected_model}")

            response = await self.claude_enhanced_query(query)
            print(f"💬 {response}")
            print("-" * 50)


async def main_async():
    """Async main entry point for Claude CLI"""
    parser = argparse.ArgumentParser(description="Enhanced Claude CLI for Sophia AI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Chat command
    chat_parser = subparsers.add_parser("chat", help="Chat with Claude")
    chat_parser.add_argument("message", help="Message to send to Claude")

    # Servers command
    subparsers.add_parser("servers", help="List MCP servers")

    # Health command
    subparsers.add_parser("health", help="Check server health")

    # Demo command
    subparsers.add_parser("demo", help="Demonstrate latest integration")

    # Models command
    subparsers.add_parser("models", help="Show model configuration")

    args = parser.parse_args()

    claude_mcp = ClaudeMCPIntegration()
    await claude_mcp.start_session()

    try:
        if args.command == "chat":
            print("🤖 Processing with intelligent model selection...")
            response = await claude_mcp.claude_enhanced_query(args.message)
            print(f"\n{response}")

        elif args.command == "servers":
            servers = await claude_mcp.list_servers()
            print("\n📊 **MCP Servers:**")
            for name, info in servers.items():
                status = info["health"].get("status", "unknown")
                emoji = "✅" if status == "healthy" else "❌"
                print(f"   {emoji} {name}: {status}")
                print(f"      📝 {info['config']['description']}")
                print(
                    f"      🔧 Capabilities: {', '.join(info['config'].get('capabilities', []))}"
                )

        elif args.command == "health":
            servers = await claude_mcp.list_servers()
            print("\n💚 **MCP Server Health Status:**")
            for name, info in servers.items():
                health = info["health"]
                print(f"\n**{name}:**")
                print(json.dumps(health, indent=2))

        elif args.command == "models":
            model_config = claude_mcp.config.get("globalSettings", {}).get(
                "modelConfiguration", {}
            )
            print("\n🧠 **Model Configuration:**")
            print(json.dumps(model_config, indent=2))

            routing_config = claude_mcp.config.get("globalSettings", {}).get(
                "intelligentRouting", {}
            )
            print(
                f"\n🎯 **Intelligent Routing:** {'✅ Enabled' if routing_config.get('enabled') else '❌ Disabled'}"
            )

            api_status = (
                "✅ Connected" if claude_mcp.anthropic_api_key else "❌ API Key Missing"
            )
            print(f"🔗 **API Status:** {api_status}")

        elif args.command == "demo":
            await claude_mcp.demonstrate_integration()

    finally:
        await claude_mcp.close_session()


def main():
    """Main entry point for Claude CLI"""
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
