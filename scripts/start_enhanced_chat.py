#!/usr/bin/env python3
"""
Enhanced Unified Chat Startup Script for Sophia AI v3.0

Demonstrates complete ecosystem access including:
- Gong conversation intelligence (integrated with business systems)
- Slack team communication
- Linear engineering tasks
- Asana project management
- Notion documentation
- HubSpot CRM data
- Complete project management assessment across ALL data sources

Natural Language Query Examples:
- "What project risks were mentioned in Gong calls this week?"
- "Cross-reference Linear tasks with customer feedback from Gong"
- "Show me Slack discussions about the product launch"
- "Give me comprehensive project health across all systems"

Date: July 9, 2025
"""

import asyncio
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import logging

from backend.services.enhanced_multi_agent_orchestrator import (
    EnhancedMultiAgentOrchestrator,
)
from backend.services.enhanced_chat_service_v4 import (
    ECOSYSTEM_QUERY_EXAMPLES,
    EnhancedSophiaUnifiedOrchestrator,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EcosystemChatDemo:
    """Demonstration of complete ecosystem chat capabilities"""

    def __init__(self):
        self.enhanced_chat = EnhancedSophiaUnifiedOrchestrator()
        self.orchestrator = EnhancedMultiAgentOrchestrator()

    async def run_demo(self):
        """Run comprehensive ecosystem chat demonstration"""

        print("🚀 Sophia AI v3.0 - Enhanced Unified Chat with Complete Ecosystem Access")
        print("=" * 80)
        print("Current Date: July 9, 2025")
        print("System: Real Internet Sophia AI with complete Pay Ready ecosystem")
        print()

        # Test ecosystem status
        await self._test_ecosystem_status()

        # Demonstrate natural language queries
        await self._demo_natural_language_queries()

        # Test cross-system intelligence
        await self._demo_cross_system_intelligence()

        # Project health assessment
        await self._demo_project_health_assessment()

        # Interactive chat session
        await self._interactive_chat_session()

    async def _test_ecosystem_status(self):
        """Test ecosystem service status"""

        print("🔍 Testing Ecosystem Service Status")
        print("-" * 40)

        try:
            status = await self.enhanced_chat.get_ecosystem_status()

            print(f"✅ Current Date: {status['current_date']}")
            print(f"✅ Date Validated: {status['date_validated']}")
            print()

            print("📊 Ecosystem Services Status:")
            for service, info in status["services"].items():
                status_icon = "✅" if info["status"] == "active" else "⏳"
                print(f"  {status_icon} {service}: {info['status']} ({info['type']})")

            print()
            print("🎯 Ecosystem Capabilities:")
            for capability in status["capabilities"]:
                print(f"  • {capability}")

            print()

        except Exception as e:
            print(f"❌ Ecosystem status error: {e}")
            print()

    async def _demo_natural_language_queries(self):
        """Demonstrate natural language queries across ecosystem"""

        print("💬 Natural Language Query Demonstrations")
        print("-" * 40)

        # Example queries that showcase ecosystem integration
        demo_queries = [
            "What project risks were mentioned in Gong calls this week?",
            "Show me Linear engineering velocity and customer feedback patterns",
            "Cross-reference Slack team discussions with Asana project status",
            "What customer concerns came up in recent Gong conversations?",
        ]

        for i, query in enumerate(demo_queries, 1):
            print(f"🔍 Demo Query {i}: {query}")

            try:
                result = await self.enhanced_chat.process_ecosystem_query(
                    query=query,
                    user_id="demo_user",
                    session_id="ecosystem_demo",
                    context={"demo_mode": True},
                )

                print(f"✅ Confidence: {result['confidence']:.2f}")
                print(f"⚡ Processing Time: {result['processing_time']:.2f}s")
                print(f"📊 Sources Used: {', '.join(result['ecosystem_sources_used'])}")
                print(f"🔗 Patterns Found: {len(result['ecosystem_patterns'])}")

                if result["ecosystem_patterns"]:
                    print("   Patterns:")
                    for pattern in result["ecosystem_patterns"][:2]:  # Show first 2
                        print(f"   • {pattern}")

                print(f"💡 Response: {result['response'][:200]}...")
                print()

            except Exception as e:
                print(f"❌ Query error: {e}")
                print()

    async def _demo_cross_system_intelligence(self):
        """Demonstrate cross-system intelligence capabilities"""

        print("🔄 Cross-System Intelligence Demonstration")
        print("-" * 40)

        cross_system_query = """
        Provide a comprehensive analysis that combines insights from:
        1. Gong customer conversations about our product roadmap
        2. Slack engineering team discussions about feature development
        3. Linear task completion rates and engineering velocity
        4. Asana project timelines and milestone progress
        5. HubSpot customer satisfaction and deal progression

        Show me how these systems correlate and what patterns emerge.
        """

        print("🔍 Cross-System Query:")
        print(f"   {cross_system_query[:100]}...")
        print()

        try:
            result = await self.enhanced_chat.process_ecosystem_query(
                query=cross_system_query,
                user_id="cross_system_demo",
                session_id="intelligence_demo",
                context={"analysis_type": "cross_system_intelligence"},
            )

            print("✅ Cross-System Analysis Results:")
            print(f"   Confidence: {result['confidence']:.2f}")
            print(f"   Processing Time: {result['processing_time']:.2f}s")
            print(f"   Ecosystem Sources: {len(result['ecosystem_sources_used'])}")
            print(f"   Cross-System Patterns: {len(result['ecosystem_patterns'])}")

            if result["cross_system_correlations"]:
                print("   Correlations Found:")
                for key, value in list(result["cross_system_correlations"].items())[:3]:
                    print(f"   • {key}: {value}")

            print(f"   Analysis: {result['response'][:300]}...")
            print()

        except Exception as e:
            print(f"❌ Cross-system analysis error: {e}")
            print()

    async def _demo_project_health_assessment(self):
        """Demonstrate comprehensive project health assessment"""

        print("🏥 Project Health Assessment Demonstration")
        print("-" * 40)

        health_query = """
        Provide a comprehensive project health assessment using data from:
        - Gong customer conversations and feedback
        - Slack team communication and sentiment
        - Linear engineering velocity and task completion
        - Asana project progress and timeline adherence
        - HubSpot customer satisfaction and deal health

        Include overall health score, risk indicators, and opportunities.
        """

        print("🔍 Project Health Query:")
        print(f"   {health_query[:100]}...")
        print()

        try:
            result = await self.enhanced_chat.process_ecosystem_query(
                query=health_query,
                user_id="health_assessment",
                session_id="project_health",
                context={"assessment_type": "comprehensive_project_health"},
            )

            print("✅ Project Health Assessment:")
            print(f"   Overall Confidence: {result['confidence']:.2f}")
            print(f"   Processing Time: {result['processing_time']:.2f}s")
            print(f"   Data Sources: {len(result['ecosystem_sources_used'])}")

            if result["project_health_insights"]:
                print("   Health Insights:")
                for key, value in result["project_health_insights"].items():
                    print(f"   • {key}: {value}")

            if result["risk_indicators"]:
                print("   Risk Indicators:")
                for risk in result["risk_indicators"][:3]:
                    print(f"   ⚠️ {risk}")

            if result["opportunities"]:
                print("   Opportunities:")
                for opportunity in result["opportunities"][:3]:
                    print(f"   💡 {opportunity}")

            print(f"   Assessment: {result['response'][:300]}...")
            print()

        except Exception as e:
            print(f"❌ Project health assessment error: {e}")
            print()

    async def _interactive_chat_session(self):
        """Interactive chat session with ecosystem access"""

        print("💬 Interactive Ecosystem Chat Session")
        print("-" * 40)
        print(
            "Enter natural language queries to access the complete Pay Ready ecosystem."
        )
        print("Examples:")
        for example in ECOSYSTEM_QUERY_EXAMPLES[:5]:
            print(f"  • {example}")
        print()
        print("Type 'quit' to exit, 'examples' for more query examples")
        print()

        session_id = "interactive_session"
        user_id = "interactive_user"

        while True:
            try:
                query = input("🤖 Sophia AI > ").strip()

                if query.lower() in ["quit", "exit", "q"]:
                    print("👋 Goodbye! Ecosystem chat session ended.")
                    break

                if query.lower() in ["examples", "help"]:
                    print("\n📝 Ecosystem Query Examples:")
                    for i, example in enumerate(ECOSYSTEM_QUERY_EXAMPLES[:10], 1):
                        print(f"  {i}. {example}")
                    print()
                    continue

                if not query:
                    continue

                print(f"🔍 Processing: {query}")
                print("⏳ Analyzing ecosystem...")

                result = await self.enhanced_chat.process_ecosystem_query(
                    query=query,
                    user_id=user_id,
                    session_id=session_id,
                    context={"interactive_mode": True},
                )

                print(f"\n✅ Response (Confidence: {result['confidence']:.2f}):")
                print(f"{result['response']}")

                if result["ecosystem_sources_used"]:
                    print(f"\n📊 Sources: {', '.join(result['ecosystem_sources_used'])}")

                if result["ecosystem_patterns"]:
                    print(
                        f"🔗 Patterns: {len(result['ecosystem_patterns'])} cross-system patterns found"
                    )

                print(f"⚡ Processing Time: {result['processing_time']:.2f}s")
                print()

            except KeyboardInterrupt:
                print("\n👋 Goodbye! Ecosystem chat session ended.")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                print()

async def main():
    """Main startup function"""

    print("🚀 Starting Sophia AI v3.0 Enhanced Unified Chat")
    print("=" * 60)
    print("Complete Pay Ready Ecosystem Access:")
    print("• Gong conversation intelligence (integrated)")
    print("• Slack team communication")
    print("• Linear engineering tasks")
    print("• Asana project management")
    print("• Notion documentation")
    print("• HubSpot CRM data")
    print("• Web search and external intelligence")
    print("• Real-time project management assessment")
    print("• Current Date: July 9, 2025")
    print()

    # Initialize and run demo
    demo = EcosystemChatDemo()
    await demo.run_demo()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Startup interrupted. Goodbye!")
    except Exception as e:
        print(f"❌ Startup error: {e}")
        sys.exit(1)
