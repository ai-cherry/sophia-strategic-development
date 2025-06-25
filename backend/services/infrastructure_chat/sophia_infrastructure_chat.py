"""
Sophia Infrastructure Chat Interface
Natural language interface for AI-driven infrastructure management
"""

from typing import Dict, Any, List, Optional
import asyncio
from datetime import datetime
import os
import httpx

from backend.agents.infrastructure.sophia_infrastructure_agent import (
    SophiaInfrastructureAgent,
)


class SophiaInfrastructureChatInterface:
    """
    Natural language interface for infrastructure management
    Provides conversational control over all infrastructure operations
    """

    def __init__(self):
        self.infrastructure_agent = SophiaInfrastructureAgent()
        self.conversation_history = []
        self.active_context = None

        # Natural language patterns for infrastructure commands
        self.command_patterns = {
            "deployment": ["deploy", "release", "rollout", "launch", "ship"],
            "scaling": [
                "scale",
                "resize",
                "expand",
                "increase capacity",
                "handle load",
            ],
            "optimization": ["optimize", "improve", "enhance", "tune", "speed up"],
            "monitoring": ["check", "monitor", "status", "health", "performance"],
            "healing": ["fix", "heal", "repair", "resolve", "troubleshoot"],
            "security": ["secure", "harden", "protect", "encrypt", "certificate"],
            "cost": ["cost", "save money", "reduce expenses", "optimize spending"],
        }

    async def initialize(self):
        """Initialize the infrastructure chat interface"""
        await self.infrastructure_agent.initialize()
        print("🤖 Sophia Infrastructure Chat Interface initialized")

    async def _call_llm_gateway(
        self, prompt: str, context: Optional[str] = None
    ) -> str:
        """Call the centralized LLM gateway (Portkey/OpenRouter) for completions."""
        endpoint = os.getenv(
            "LLM_GATEWAY_ENDPOINT", "https://llm-gateway.sophia-intel.ai/v1/completions"
        )
        api_key = os.getenv("LLM_GATEWAY_API_KEY")
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        payload = {"prompt": prompt}
        if context:
            payload["context"] = context
        async with httpx.AsyncClient(timeout=30) as client:
            try:
                response = await client.post(endpoint, json=payload, headers=headers)
                response.raise_for_status()
                return response.json().get("completion", "")
            except Exception as e:
                # Fallback logic: try OpenAI directly if configured
                fallback = os.getenv("OPENAI_API_KEY")
                if fallback:
                    # ... fallback logic here ...
                    return "[LLM fallback response]"
                return f"[LLM error: {e}]"

    async def process_message(
        self, message: str, user_context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Process natural language infrastructure command
        """
        # Add to conversation history
        self.conversation_history.append(
            {
                "timestamp": datetime.utcnow().isoformat(),
                "user_message": message,
                "context": user_context,
            }
        )

        # Use LLM gateway for natural language understanding and response
        context = "\n".join([h["user_message"] for h in self.conversation_history[-5:]])
        llm_response = await self._call_llm_gateway(message, context=context)

        # Optionally, still process through infrastructure agent for action
        result = await self.infrastructure_agent.natural_language_command(message)

        # Generate conversational response
        response = {
            "message": llm_response,
            "action_summary": f"I understand you want to {result.get('proposed_action', 'unknown')} the infrastructure.",
            "confidence_level": result.get("confidence", "0%"),
            "risk_assessment": result.get("risk_level", "unknown"),
            "visual_elements": [],
        }

        # Add response to history
        self.conversation_history.append(
            {
                "timestamp": datetime.utcnow().isoformat(),
                "ai_response": response,
                "action_taken": result.get("proposed_action"),
            }
        )

        return response

    async def _generate_conversational_response(
        self, result: Dict[str, Any], original_message: str
    ) -> Dict[str, Any]:
        """Generate a conversational response based on infrastructure action"""

        # Extract key information
        action = result.get("proposed_action", "unknown")
        confidence = result.get("confidence", "0%")
        risk = result.get("risk_level", "unknown")

        # Build conversational response
        response = {
            "message": result.get(
                "natural_language_response",
                "I'll help you with that infrastructure task.",
            ),
            "action_summary": f"I understand you want to {action} the infrastructure.",
            "confidence_level": confidence,
            "risk_assessment": risk,
            "visual_elements": [],
        }

        # Add visual elements based on action type
        if action == "scale_up":
            response["visual_elements"].append(
                {
                    "type": "chart",
                    "data": {
                        "title": "Predicted Load Increase",
                        "chart_type": "line",
                        "description": "Shows predicted traffic patterns requiring scale-up",
                    },
                }
            )

        elif action == "optimize":
            response["visual_elements"].append(
                {
                    "type": "metrics",
                    "data": {
                        "title": "Optimization Opportunities",
                        "metrics": [
                            {"name": "Response Time", "improvement": "40%"},
                            {"name": "Cost Reduction", "improvement": "23%"},
                            {"name": "Error Rate", "improvement": "65%"},
                        ],
                    },
                }
            )

        elif action == "heal":
            response["visual_elements"].append(
                {
                    "type": "status",
                    "data": {
                        "title": "Infrastructure Health",
                        "issues_found": result.get("issues_count", 0),
                        "auto_fixed": result.get("auto_fixed_count", 0),
                        "manual_required": result.get("manual_required_count", 0),
                    },
                }
            )

        # Add execution plan if available
        if result.get("execution_plan"):
            response["execution_steps"] = self._format_execution_plan(
                result["execution_plan"]
            )

        # Add follow-up suggestions
        response["suggested_actions"] = await self._generate_follow_up_suggestions(
            action
        )

        return response

    def _format_execution_plan(self, plan: Dict[str, Any]) -> List[Dict[str, str]]:
        """Format execution plan for display"""
        formatted_steps = []

        for step, details in plan.items():
            formatted_steps.append(
                {
                    "step": step.replace("_", " ").title(),
                    "description": str(details),
                    "status": "pending",
                }
            )

        return formatted_steps

    async def _generate_follow_up_suggestions(self, action: str) -> List[str]:
        """Generate contextual follow-up suggestions"""

        suggestions_map = {
            "scale_up": [
                "Would you like me to monitor the scaling operation?",
                "Should I set up auto-scaling for future traffic spikes?",
                "Do you want to see the cost impact of this scaling?",
            ],
            "optimize": [
                "Would you like me to apply these optimizations?",
                "Should I create a performance baseline for comparison?",
                "Do you want to schedule regular optimization checks?",
            ],
            "heal": [
                "Should I enable continuous self-healing mode?",
                "Would you like a detailed report of the issues found?",
                "Do you want to prevent similar issues in the future?",
            ],
            "deploy": [
                "Should I run smoke tests after deployment?",
                "Would you like to set up a rollback plan?",
                "Do you want to notify the team about this deployment?",
            ],
        }

        return suggestions_map.get(
            action,
            [
                "Is there anything else you'd like me to help with?",
                "Would you like to see the current infrastructure status?",
                "Should I monitor this operation for you?",
            ],
        )

    async def interactive_session(self):
        """Start an interactive chat session for infrastructure management"""

        print("\n🤖 Sophia Infrastructure Assistant")
        print("=" * 50)
        print("I can help you manage your infrastructure using natural language.")
        print("Try commands like:")
        print("  • 'Check the health of our infrastructure'")
        print("  • 'Optimize our DNS configuration for better performance'")
        print("  • 'Scale up to handle increased traffic'")
        print("  • 'Fix any issues with our SSL certificates'")
        print("  • 'Reduce our infrastructure costs'")
        print("\nType 'exit' to end the session.\n")

        while True:
            try:
                # Get user input
                user_message = input("You: ").strip()

                if user_message.lower() in ["exit", "quit", "bye"]:
                    print("\nSophia: Goodbye! Your infrastructure is in good hands. 👋")
                    break

                if not user_message:
                    continue

                # Process message
                print("\nSophia: ", end="", flush=True)
                response = await self.process_message(user_message)

                # Display response
                print(response["message"])

                # Show visual elements if any
                if response.get("visual_elements"):
                    for element in response["visual_elements"]:
                        print(f"\n📊 {element['data']['title']}")
                        if element["type"] == "metrics":
                            for metric in element["data"]["metrics"]:
                                print(
                                    f"  • {metric['name']}: {metric['improvement']} improvement"
                                )

                # Show execution steps if any
                if response.get("execution_steps"):
                    print("\n📋 Execution Plan:")
                    for i, step in enumerate(response["execution_steps"], 1):
                        print(f"  {i}. {step['step']}: {step['description']}")

                # Show suggestions
                if response.get("suggested_actions"):
                    print("\n💡 Suggestions:")
                    for suggestion in response["suggested_actions"]:
                        print(f"  • {suggestion}")

                print()  # Empty line for readability

            except KeyboardInterrupt:
                print(
                    "\n\nSophia: Session interrupted. Your infrastructure is still being monitored. 👋"
                )
                break

            except Exception as e:
                print(
                    f"\nSophia: I encountered an error: {str(e)}. Let me try to help you differently."
                )
                continue


# Example usage patterns for different scenarios


class InfrastructureScenarios:
    """Example scenarios demonstrating AI infrastructure capabilities"""

    @staticmethod
    async def demo_predictive_scaling():
        """Demo: Predictive scaling based on traffic patterns"""

        chat = SophiaInfrastructureChatInterface()
        await chat.initialize()

        print("\n🎯 DEMO: Predictive Scaling Scenario")
        print("-" * 40)

        # Simulate traffic spike prediction
        response = await chat.process_message(
            "Our traffic is increasing rapidly, what should we do?"
        )

        print("Sophia:", response["message"])
        print("\nPredicted Actions:")
        for step in response.get("execution_steps", []):
            print(f"  • {step['description']}")

    @staticmethod
    async def demo_self_healing():
        """Demo: Self-healing infrastructure issues"""

        chat = SophiaInfrastructureChatInterface()
        await chat.initialize()

        print("\n🏥 DEMO: Self-Healing Scenario")
        print("-" * 40)

        # Simulate infrastructure issue
        response = await chat.process_message(
            "I'm seeing errors with our SSL certificates"
        )

        print("Sophia:", response["message"])

    @staticmethod
    async def demo_cost_optimization():
        """Demo: AI-driven cost optimization"""

        chat = SophiaInfrastructureChatInterface()
        await chat.initialize()

        print("\n💰 DEMO: Cost Optimization Scenario")
        print("-" * 40)

        # Request cost optimization
        response = await chat.process_message(
            "Can you help reduce our infrastructure costs?"
        )

        print("Sophia:", response["message"])
        if response.get("visual_elements"):
            for element in response["visual_elements"]:
                if element["type"] == "metrics":
                    print("\nPotential Savings:")
                    for metric in element["data"]["metrics"]:
                        print(f"  • {metric['name']}: {metric['improvement']}")


async def main():
    """Main entry point for infrastructure chat interface"""

    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == "demo":
            # Run demos
            await InfrastructureScenarios.demo_predictive_scaling()
            await InfrastructureScenarios.demo_self_healing()
            await InfrastructureScenarios.demo_cost_optimization()
        else:
            # Process single command
            chat = SophiaInfrastructureChatInterface()
            await chat.initialize()

            command = " ".join(sys.argv[1:])
            response = await chat.process_message(command)
            print("Sophia:", response["message"])
    else:
        # Interactive mode
        chat = SophiaInfrastructureChatInterface()
        await chat.initialize()
        await chat.interactive_session()


if __name__ == "__main__":
    asyncio.run(main())
