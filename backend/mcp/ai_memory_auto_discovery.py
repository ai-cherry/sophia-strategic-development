"""AI Memory MCP Auto-Discovery System
Ensures AI coding assistants automatically discover and use the AI Memory MCP server.
"""
import asyncio
import json
import logging
from typing import Any, Dict, List

from backend.mcp.mcp_client import MCPClient

logger = logging.getLogger(__name__)


class AIMemoryAutoDiscovery:
    """Auto-discovery system that helps AI coders find and use the AI Memory MCP server.
    """

    def __init__(self):
        self.mcp_client = None
        self.memory_tools = {}
        self.discovery_metadata = {
            "server_name": "ai_memory",
            "purpose": "AI Coding Assistant Memory System",
            "automatic_usage": True,
            "priority": "high",
            "categories": [
                "conversation",
                "code_decision",
                "bug_solution",
                "architecture",
                "workflow",
                "requirement",
                "pattern",
                "api_usage",
            ],
        }

    async def initialize(self, gateway_url: str = "http://localhost:8090"):
        """Initialize connection to MCP gateway and discover AI Memory tools."""
        try:
            self.mcp_client = MCPClient(gateway_url)
            await self.mcp_client.connect()

            # Specifically discover AI Memory tools
            await self._discover_ai_memory_tools()

            logger.info(
                f"AI Memory auto-discovery initialized with {len(self.memory_tools)} tools"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to initialize AI Memory auto-discovery: {e}")
            return False

    async def _discover_ai_memory_tools(self):
        """Discover and catalog AI Memory MCP tools."""
        try:
            # Get all tools for ai_memory server
            ai_memory_tools = self.mcp_client.list_tools("ai_memory")

            for tool_key in ai_memory_tools:
                tool_info = self.mcp_client.get_tool_info(tool_key)
                if tool_info:
                    self.memory_tools[tool_key] = {
                        **tool_info,
                        "auto_usage_hints": self._generate_usage_hints(tool_info),
                    }

        except Exception as e:
            logger.error(f"Error discovering AI Memory tools: {e}")

    def _generate_usage_hints(self, tool_info: Dict[str, Any]) -> Dict[str, Any]:
        """Generate usage hints for AI coders."""
        tool_name = tool_info.get("tool", "")

        hints = {
            "when_to_use": "",
            "example_triggers": [],
            "automation_level": "automatic",
        }

        if tool_name == "store_conversation":
            hints.update(
                {
                    "when_to_use": "After any significant coding conversation or decision",
                    "example_triggers": [
                        "User asks about architecture decisions",
                        "Bug is discussed and solved",
                        "Code patterns are explained",
                        "Development workflow is established",
                    ],
                    "automation_level": "automatic",
                }
            )
        elif tool_name == "recall_memory":
            hints.update(
                {
                    "when_to_use": "Before starting new tasks or when encountering similar problems",
                    "example_triggers": [
                        "User asks 'How did we handle X before?'",
                        "Similar error patterns detected",
                        "Architecture questions arise",
                        "Starting work on familiar components",
                    ],
                    "automation_level": "automatic",
                }
            )

        return hints

    def get_ai_coder_instructions(self) -> Dict[str, Any]:
        """Get instructions for AI coding assistants on how to use AI Memory."""
        return {
            "system_prompt_addition": self._generate_system_prompt(),
            "available_tools": self.memory_tools,
            "auto_discovery_metadata": self.discovery_metadata,
            "usage_patterns": self._get_usage_patterns(),
        }

    def _generate_system_prompt(self) -> str:
        """Generate system prompt addition for AI coders."""
        return """
AI MEMORY SYSTEM INTEGRATION:

You have access to an AI Memory MCP server that provides persistent memory for coding assistance. 

AUTOMATIC USAGE RULES:
1. ALWAYS store significant conversations using 'ai_memory.store_conversation' after:
   - Architecture discussions
   - Bug fixes and solutions
   - Code pattern explanations
   - Development decisions

2. ALWAYS query memory using 'ai_memory.recall_memory' before:
   - Starting work on familiar components
   - Answering questions about past decisions
   - Debugging similar issues
   - Explaining code patterns

AVAILABLE TOOLS:
- ai_memory.store_conversation: Store conversations for future reference
- ai_memory.recall_memory: Search previous conversations and decisions

EXAMPLE USAGE:
User: "How should we implement authentication in the MCP servers?"
AI: First, let me check if we've discussed this before...
[Call ai_memory.recall_memory with query="MCP server authentication implementation"]
[Based on results, provide context-aware answer]
[After discussion, call ai_memory.store_conversation to save the new insights]

This memory system ensures continuity across coding sessions and helps build institutional knowledge.
"""

    def _get_usage_patterns(self) -> List[Dict[str, Any]]:
        """Get common usage patterns for AI Memory."""
        return [
            {
                "pattern": "conversation_storage",
                "trigger": "End of significant coding discussion",
                "action": "store_conversation",
                "automatic": True,
            },
            {
                "pattern": "context_retrieval",
                "trigger": "Start of new task or similar problem",
                "action": "recall_memory",
                "automatic": True,
            },
            {
                "pattern": "decision_documentation",
                "trigger": "Architecture or design decision made",
                "action": "store_conversation",
                "automatic": True,
            },
        ]

    async def create_ai_coder_config(self, output_path: str = ".ai_memory_config.json"):
        """Create configuration file for AI coding assistants."""
        config = {
            "ai_memory_integration": {
                "enabled": True,
                "server_name": "ai_memory",
                "auto_discovery": True,
                "instructions": self.get_ai_coder_instructions(),
                "mcp_config": {
                    "gateway_url": "http://localhost:8090",
                    "server_endpoint": "ai_memory",
                    "tools": list(self.memory_tools.keys()),
                },
            }
        }

        try:
            with open(output_path, "w") as f:
                json.dump(config, f, indent=2)
            logger.info(f"AI coder configuration saved to {output_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save AI coder configuration: {e}")
            return False

    async def test_memory_integration(self) -> Dict[str, Any]:
        """Test the AI Memory integration."""
        test_results = {
            "discovery": False,
            "tools_available": False,
            "store_test": False,
            "recall_test": False,
            "errors": [],
        }

        try:
            # Test discovery
            if self.mcp_client and len(self.memory_tools) > 0:
                test_results["discovery"] = True
                test_results["tools_available"] = True

            # Test store functionality
            store_result = await self.mcp_client.call_tool(
                "ai_memory",
                "store_conversation",
                conversation_text="Test conversation for AI Memory integration",
                context="Integration testing",
            )

            if store_result.get("success"):
                test_results["store_test"] = True
            else:
                test_results["errors"].append(f"Store test failed: {store_result}")

            # Test recall functionality
            recall_result = await self.mcp_client.call_tool(
                "ai_memory", "recall_memory", query="integration testing"
            )

            if recall_result.get("success"):
                test_results["recall_test"] = True
            else:
                test_results["errors"].append(f"Recall test failed: {recall_result}")

        except Exception as e:
            test_results["errors"].append(f"Integration test error: {e}")

        return test_results


# Global auto-discovery instance
ai_memory_discovery = AIMemoryAutoDiscovery()


async def main():
    """Test the auto-discovery system."""
    print("🔍 Testing AI Memory Auto-Discovery System")
    print("=" * 50)

    # Initialize auto-discovery
    success = await ai_memory_discovery.initialize()
    if not success:
        print("❌ Failed to initialize auto-discovery")
        return

    print("✅ Auto-discovery initialized")

    # Create AI coder configuration
    config_created = await ai_memory_discovery.create_ai_coder_config()
    if config_created:
        print("✅ AI coder configuration created")

    # Test integration
    test_results = await ai_memory_discovery.test_memory_integration()
    print("\n📊 Integration Test Results:")
    for test, result in test_results.items():
        if test != "errors":
            status = "✅" if result else "❌"
            print(f"   {status} {test}: {result}")

    if test_results["errors"]:
        print("\n❌ Errors:")
        for error in test_results["errors"]:
            print(f"   • {error}")

    # Close connection
    if ai_memory_discovery.mcp_client:
        await ai_memory_discovery.mcp_client.close()


if __name__ == "__main__":
    asyncio.run(main())
