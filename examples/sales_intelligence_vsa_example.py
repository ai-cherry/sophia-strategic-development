#!/usr/bin/env python3
"""Sophia AI - Sales Intelligence Vertical Slice Example.

Demonstrates Agno framework integration with VSA architecture for sales intelligence.

This example shows:
1. Vertical Slice Architecture implementation
2. Five Levels of Agentic Systems progression
3. Agno performance optimization
4. Multi-agent team coordination
5. Agentic RAG knowledge management
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path

# Agno framework imports (simulated - replace with actual agno imports)
try:
    from agno import Agent, Team, Workflow, WorkflowState, tool
    from agno.tools import Toolkit
    from agno.knowledge import KnowledgeBase
    from agno.storage import AgentStorage
    from agno.vectordb import PineconeDb
    from agno.memory import MemoryManager
    from agno.monitoring import AgentMonitoring
except ImportError:
    # Fallback for when agno is not installed
    print("Note: Agno framework not installed. This is a demonstration example.")
    
    # Create mock classes for demonstration
    class Agent:
        def __init__(self, **kwargs): pass
        async def run(self, message): return {"response": "Mock response"}
    
    class Team:
        def __init__(self, **kwargs): pass
        async def run(self, message): return {"response": "Mock team response"}
    
    class Workflow:
        def __init__(self, **kwargs): pass
    
    class Toolkit: pass
    class KnowledgeBase: pass
    class AgentStorage: pass
    class PineconeDb: pass
    class MemoryManager: pass
    class AgentMonitoring: pass
    class WorkflowState: pass
    
    def tool(func): return func

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ===== SALES INTELLIGENCE FEATURE SLICE =====

@dataclass
class CallData:
    """Sales call data structure."""
    call_id: str
    gong_call_id: str
    transcript: str
    participants: List[str]
    duration_minutes: int
    call_date: datetime
    deal_id: Optional[str] = None

@dataclass 
class CoachingInsight:
    """Sales coaching insight structure."""
    insight_type: str
    message: str
    confidence: float
    actionable_steps: List[str]
    examples: List[str]

# ===== LEVEL 1: AGENTS WITH TOOLS AND INSTRUCTIONS =====

class SalesIntelligenceToolkit(Toolkit):
    """Comprehensive toolkit for sales intelligence operations."""
    
    @tool
    async def analyze_gong_call(self, call_data: CallData) -> Dict[str, Any]:
        """Advanced call analysis with sentiment, objections, and coaching points."""
        logger.info(f"Analyzing Gong call: {call_data.call_id}")
        
        # Simulate advanced call analysis
        analysis = {
            "call_id": call_data.call_id,
            "sentiment_score": 0.75,  # Positive sentiment
            "talk_time_ratio": {"rep": 0.4, "prospect": 0.6},  # Good listening ratio
            "objections": [
                {"type": "price", "timestamp": "12:34", "response_quality": "good"},
                {"type": "timing", "timestamp": "18:45", "response_quality": "needs_improvement"}
            ],
            "next_steps": [
                "Send pricing proposal within 24 hours",
                "Schedule demo for next week",
                "Follow up on technical requirements"
            ],
            "coaching_opportunities": [
                "Improve objection handling for timing concerns",
                "Better discovery questions about decision process",
                "More confident closing statements"
            ]
        }
        
        logger.info(f"Call analysis completed with sentiment: {analysis['sentiment_score']}")
        return analysis
    
    @tool
    async def update_hubspot_deal(self, deal_id: str, insights: Dict[str, Any]) -> bool:
        """Sync call insights to HubSpot with automated field mapping."""
        logger.info(f"Updating HubSpot deal: {deal_id}")
        
        # Simulate HubSpot update
        hubspot_fields = {
            "last_call_sentiment": insights.get("sentiment_score"),
            "call_notes": f"Call analyzed on {datetime.now()}. Key insights: {insights.get('coaching_opportunities', [])}",
            "next_call_date": "2025-01-28",  # Based on next_steps
            "deal_stage": "qualification"  # Based on call analysis
        }
        
        logger.info(f"HubSpot deal updated with fields: {list(hubspot_fields.keys())}")
        return True
    
    @tool
    async def generate_coaching_report(self, rep_id: str, analysis: Dict[str, Any]) -> CoachingInsight:
        """AI-powered coaching recommendations based on call patterns."""
        logger.info(f"Generating coaching report for rep: {rep_id}")
        
        # Simulate AI-powered coaching insight generation
        insight = CoachingInsight(
            insight_type="objection_handling",
            message="Focus on improving timing objection responses. Current responses lack confidence and specific next steps.",
            confidence=0.87,
            actionable_steps=[
                "Practice the 'Feel, Felt, Found' technique for timing objections",
                "Prepare 3 specific case studies of quick implementations",
                "Use trial closes after addressing timing concerns"
            ],
            examples=[
                "I understand how you feel about timing. Other clients felt the same way but found that starting sooner actually saved time overall.",
                "Let me share how [similar client] implemented this in just 2 weeks and saw immediate results."
            ]
        )
        
        logger.info(f"Coaching insight generated with confidence: {insight.confidence}")
        return insight
    
    @tool
    async def send_slack_notification(self, message: str, channel: str = "#sales-coaching") -> bool:
        """Send intelligent Slack notifications to relevant team members."""
        logger.info(f"Sending Slack notification to {channel}")
        
        # Simulate Slack notification
        slack_message = {
            "channel": channel,
            "text": message,
            "timestamp": datetime.now().isoformat(),
            "delivered": True
        }
        
        logger.info(f"Slack notification sent: {slack_message['text'][:50]}...")
        return True

# ===== LEVEL 1: ENHANCED AGENTS =====

class CallAnalysisAgent(Agent):
    """Specialized agent for analyzing sales calls with Gong integration."""
    
    def __init__(self):
        super().__init__(
            model="gpt-4o",
            tools=[SalesIntelligenceToolkit()],
            instructions="""You are an expert sales call analyst with access to Gong call data.
            Analyze sales calls for sentiment, objections, talk time ratios, and coaching opportunities.
            Provide specific, actionable insights for sales improvement.""",
            markdown=True,
            show_tool_calls=True
        )

class CoachingAgent(Agent):
    """Specialized agent for generating AI-powered sales coaching insights."""
    
    def __init__(self):
        super().__init__(
            model="gpt-4o", 
            tools=[SalesIntelligenceToolkit()],
            instructions="""You are an experienced sales coach and trainer.
            Generate specific, actionable coaching recommendations based on call analysis.
            Focus on practical techniques and provide concrete examples.""",
            markdown=True,
            show_tool_calls=True
        )

class CRMSyncAgent(Agent):
    """Specialized agent for HubSpot CRM synchronization and data management."""
    
    def __init__(self):
        super().__init__(
            model="gpt-4o",
            tools=[SalesIntelligenceToolkit()],
            instructions="""You are a CRM data specialist focused on HubSpot integration.
            Update CRM records with call insights, maintain data quality, and ensure
            all relevant information is properly categorized and accessible.""",
            markdown=True,
            show_tool_calls=True
        )

# ===== LEVEL 2: KNOWLEDGE AND STORAGE INTEGRATION =====

class SalesKnowledgeBase(KnowledgeBase):
    """Sales-specific knowledge base with playbooks and best practices."""
    
    def __init__(self):
        super().__init__(
            vector_db=PineconeDb(
                index_name="sophia-sales-intelligence", 
                namespace="sales-playbooks"
            ),
            sources=[
                "features/sales-intelligence/knowledge/sales-playbooks/",
                "features/sales-intelligence/knowledge/call-patterns/",
                "features/sales-intelligence/knowledge/objection-handling/"
            ]
        )

class KnowledgeEnabledCoachingAgent(Agent):
    """Coaching agent enhanced with sales knowledge base and persistent storage."""
    
    def __init__(self):
        super().__init__(
            model="gpt-4o",
            tools=[SalesIntelligenceToolkit()],
            knowledge=SalesKnowledgeBase(),
            storage=AgentStorage(
                table_name="sales_coaching_sessions",
                db_url="postgresql://localhost/sophia_ai"
            ),
            instructions="""You have access to comprehensive sales knowledge including
            playbooks, successful call patterns, and objection handling strategies.
            Use this knowledge to provide contextual coaching and recommendations
            based on proven best practices."""
        )

# ===== LEVEL 3: MEMORY AND REASONING =====

class ReasoningCoachingAgent(Agent):
    """Advanced coaching agent with long-term memory and reasoning capabilities."""
    
    def __init__(self):
        super().__init__(
            model="gpt-4o",
            tools=[SalesIntelligenceToolkit()],
            knowledge=SalesKnowledgeBase(),
            memory=MemoryManager(
                memory_type="long_term",
                retention_days=90
            ),
            instructions="""You maintain memory of all sales interactions and can reason
            about patterns across multiple calls, deals, and time periods. Use this
            capability to identify trends, track improvement over time, and provide
            strategic coaching insights."""
        )

# ===== LEVEL 4: AGENT TEAMS =====

class SalesIntelligenceTeam(Team):
    """Coordinated team of sales intelligence agents."""
    
    def __init__(self, mode: str = "collaborate"):
        agents = [
            CallAnalysisAgent(),
            KnowledgeEnabledCoachingAgent(),
            CRMSyncAgent()
        ]
        
        instructions_by_mode = {
            "route": "Route sales requests to the most specialized agent based on the task type.",
            "collaborate": "Work together to provide comprehensive sales intelligence. Call analysis provides data, coaching provides insights, CRM sync ensures data persistence.",
            "coordinate": "Coordinate systematically: analyze call first, generate coaching insights second, update CRM third."
        }
        
        super().__init__(
            agents=agents,
            mode=mode,
            instructions=instructions_by_mode.get(mode, instructions_by_mode["collaborate"])
        )

# ===== LEVEL 5: AGENTIC WORKFLOWS =====

class SalesIntelligenceWorkflow(Workflow):
    """End-to-end sales intelligence workflow from call to actionable insights."""
    
    def __init__(self):
        super().__init__(
            name="sales-intelligence-pipeline",
            description="Complete pipeline from Gong call to HubSpot update and team notification"
        )
    
    async def setup(self, state: WorkflowState):
        """Initialize workflow state."""
        state.team = SalesIntelligenceTeam(mode="coordinate")
        state.call_data = None
        state.call_analysis = None
        state.coaching_insights = None
        state.crm_updated = False
        state.team_notified = False
    
    async def analyze_call(self, state: WorkflowState):
        """Step 1: Analyze incoming call data with CallAnalysisAgent."""
        logger.info("Workflow Step 1: Analyzing call")
        
        if not state.call_data:
            raise ValueError("Call data not provided")
        
        # Use team in coordinate mode for systematic analysis
        analysis_request = f"Analyze this sales call: {state.call_data.call_id}"
        response = await state.team.run(analysis_request, context={
            "call_data": state.call_data,
            "step": "analysis"
        })
        
        state.call_analysis = response
        logger.info("Call analysis completed")
    
    async def generate_coaching_insights(self, state: WorkflowState):
        """Step 2: Generate coaching insights based on call analysis.""" 
        logger.info("Workflow Step 2: Generating coaching insights")
        
        coaching_request = "Generate specific coaching recommendations based on the call analysis"
        response = await state.team.run(coaching_request, context={
            "call_analysis": state.call_analysis,
            "step": "coaching"
        })
        
        state.coaching_insights = response
        logger.info("Coaching insights generated")
    
    async def update_crm(self, state: WorkflowState):
        """Step 3: Update HubSpot CRM with insights."""
        logger.info("Workflow Step 3: Updating CRM")
        
        crm_request = "Update HubSpot with call analysis and coaching insights"
        response = await state.team.run(crm_request, context={
            "call_analysis": state.call_analysis,
            "coaching_insights": state.coaching_insights,
            "deal_id": state.call_data.deal_id,
            "step": "crm_update"
        })
        
        state.crm_updated = response.get("success", False)
        logger.info(f"CRM update completed: {state.crm_updated}")
    
    async def notify_team(self, state: WorkflowState):
        """Step 4: Send Slack notifications to relevant team members."""
        logger.info("Workflow Step 4: Notifying team")
        
        notification_request = "Send Slack notification with key insights and coaching recommendations"
        response = await state.team.run(notification_request, context={
            "call_analysis": state.call_analysis,
            "coaching_insights": state.coaching_insights,
            "rep_id": "john_doe",  # Would come from call_data
            "step": "notification"
        })
        
        state.team_notified = response.get("success", False)
        logger.info(f"Team notification completed: {state.team_notified}")

# ===== AGENTIC RAG SYSTEM =====

class SalesAgenticRAG:
    """AI-powered knowledge discovery and retrieval for sales intelligence."""
    
    def __init__(self):
        self.vector_dbs = {
            "pinecone": PineconeDb(index_name="sophia-sales-knowledge"),
            # "weaviate": WeaviateDb(url="http://localhost:8080")  # Additional vector DB
        }
        self.discovery_agent = Agent(
            model="gpt-4o",
            instructions="You are a knowledge discovery expert. Identify what knowledge would be most valuable for sales scenarios."
        )
    
    async def proactive_knowledge_discovery(self, context: str) -> Dict[str, Any]:
        """Proactively discover relevant knowledge based on sales context."""
        logger.info(f"Discovering knowledge for context: {context[:50]}...")
        
        # Use agent to understand knowledge needs
        knowledge_needs_response = await self.discovery_agent.run(
            f"What sales knowledge would be most valuable for this context: {context}"
        )
        
        # Simulate knowledge search and synthesis
        knowledge_results = {
            "relevant_playbooks": [
                "Enterprise Sales Discovery Framework",
                "Objection Handling Best Practices",
                "Closing Techniques for Technical Sales"
            ],
            "similar_call_patterns": [
                "Successful calls with similar objections",
                "Effective discovery questions for this industry",
                "Proven next steps for this deal stage"
            ],
            "coaching_resources": [
                "Scripts for timing objections",
                "Best practices for demo scheduling", 
                "Follow-up email templates"
            ],
            "confidence_score": 0.85
        }
        
        logger.info(f"Knowledge discovery completed with confidence: {knowledge_results['confidence_score']}")
        return knowledge_results

# ===== PERFORMANCE MONITORING =====

class SalesIntelligenceMonitoring(AgentMonitoring):
    """Enhanced monitoring for sales intelligence agents with business metrics."""
    
    def __init__(self):
        super().__init__(
            app_name="sophia-sales-intelligence",
            server_url="https://monitoring.sophia.ai"
        )
        self.business_metrics = {}
    
    async def track_sales_impact(self, session_data: Dict[str, Any]):
        """Track business impact of sales intelligence operations."""
        logger.info("Tracking sales impact metrics")
        
        # Track key business metrics
        metrics = {
            "calls_analyzed": 1,
            "coaching_insights_generated": len(session_data.get("coaching_insights", [])),
            "crm_records_updated": 1 if session_data.get("crm_updated") else 0,
            "team_notifications_sent": 1 if session_data.get("team_notified") else 0,
            "average_confidence_score": session_data.get("confidence_score", 0),
            "timestamp": datetime.now().isoformat()
        }
        
        self.business_metrics.update(metrics)
        logger.info(f"Sales impact tracked: {metrics}")

# ===== EXAMPLE USAGE AND DEMONSTRATION =====

async def demonstrate_sales_intelligence_vsa():
    """Comprehensive demonstration of the sales intelligence vertical slice."""
    logger.info("🚀 Starting Sales Intelligence VSA Demonstration")
    
    # Sample call data
    sample_call = CallData(
        call_id="call_20250121_001",
        gong_call_id="gong_abc123",
        transcript="Sample call transcript with discovery questions and objections...",
        participants=["John Doe (Rep)", "Jane Smith (Prospect)"],
        duration_minutes=45,
        call_date=datetime.now(),
        deal_id="hubspot_deal_456"
    )
    
    logger.info(f"📞 Processing call: {sample_call.call_id}")
    
    # ===== LEVEL 1 DEMONSTRATION: Individual Agents =====
    logger.info("\n🔹 Level 1: Individual Agent Analysis")
    
    # Call Analysis Agent
    call_agent = CallAnalysisAgent()
    analysis_result = await call_agent.run(f"Analyze call {sample_call.call_id}")
    logger.info(f"✅ Call analysis completed: {analysis_result}")
    
    # Coaching Agent  
    coaching_agent = CoachingAgent()
    coaching_result = await coaching_agent.run("Generate coaching insights for this call")
    logger.info(f"✅ Coaching insights generated: {coaching_result}")
    
    # ===== LEVEL 4 DEMONSTRATION: Team Collaboration =====
    logger.info("\n🔹 Level 4: Team Collaboration")
    
    # Demonstrate different team modes
    team_modes = ["route", "collaborate", "coordinate"]
    
    for mode in team_modes:
        logger.info(f"\n📊 Testing team mode: {mode}")
        team = SalesIntelligenceTeam(mode=mode)
        team_result = await team.run(f"Process call {sample_call.call_id} comprehensively")
        logger.info(f"✅ Team ({mode}) result: {team_result}")
    
    # ===== LEVEL 5 DEMONSTRATION: Workflow Orchestration =====
    logger.info("\n🔹 Level 5: Workflow Orchestration")
    
    workflow = SalesIntelligenceWorkflow()
    state = WorkflowState()
    
    # Initialize workflow
    await workflow.setup(state)
    state.call_data = sample_call
    
    # Execute workflow steps
    try:
        await workflow.analyze_call(state)
        await workflow.generate_coaching_insights(state)
        await workflow.update_crm(state)
        await workflow.notify_team(state)
        
        logger.info("✅ Complete workflow executed successfully")
        logger.info(f"📊 Workflow results:")
        logger.info(f"  - Call analyzed: ✅")
        logger.info(f"  - Coaching insights: ✅")
        logger.info(f"  - CRM updated: {'✅' if state.crm_updated else '❌'}")
        logger.info(f"  - Team notified: {'✅' if state.team_notified else '❌'}")
        
    except Exception as e:
        logger.error(f"❌ Workflow execution failed: {e}")
    
    # ===== AGENTIC RAG DEMONSTRATION =====
    logger.info("\n🔹 Agentic RAG Knowledge Discovery")
    
    rag_system = SalesAgenticRAG()
    knowledge_context = f"Sales call with timing objections and technical questions, deal value $50K"
    knowledge_results = await rag_system.proactive_knowledge_discovery(knowledge_context)
    
    logger.info(f"✅ Knowledge discovery completed:")
    logger.info(f"  - Relevant playbooks: {len(knowledge_results['relevant_playbooks'])}")
    logger.info(f"  - Similar patterns: {len(knowledge_results['similar_call_patterns'])}")
    logger.info(f"  - Coaching resources: {len(knowledge_results['coaching_resources'])}")
    logger.info(f"  - Confidence: {knowledge_results['confidence_score']}")
    
    # ===== PERFORMANCE MONITORING =====
    logger.info("\n🔹 Performance Monitoring")
    
    monitoring = SalesIntelligenceMonitoring()
    session_data = {
        "call_id": sample_call.call_id,
        "coaching_insights": ["objection_handling", "discovery_improvement"],
        "crm_updated": True,
        "team_notified": True,
        "confidence_score": 0.87
    }
    
    await monitoring.track_sales_impact(session_data)
    logger.info(f"✅ Performance monitoring completed: {monitoring.business_metrics}")
    
    logger.info("\n🎉 Sales Intelligence VSA Demonstration Completed!")
    logger.info("This example shows how Agno framework concepts enhance Sophia AI with:")
    logger.info("  ✅ 5000x faster agent instantiation")
    logger.info("  ✅ Feature-based vertical slice architecture") 
    logger.info("  ✅ Progressive five-level agentic capabilities")
    logger.info("  ✅ Advanced team coordination modes")
    logger.info("  ✅ Deterministic workflow orchestration")
    logger.info("  ✅ Proactive knowledge discovery")
    logger.info("  ✅ Comprehensive business metrics tracking")

# ===== PERFORMANCE COMPARISON =====

async def demonstrate_performance_improvements():
    """Show performance improvements from Agno framework integration."""
    logger.info("\n⚡ Performance Improvements Demonstration")
    
    # Simulate traditional vs Agno performance
    traditional_metrics = {
        "agent_instantiation_ms": 100,
        "memory_per_agent_mb": 50,
        "max_concurrent_agents": 10,
        "response_time_ms": 800
    }
    
    agno_metrics = {
        "agent_instantiation_us": 3,  # microseconds
        "memory_per_agent_kib": 6.5,
        "max_concurrent_agents": 1000,
        "response_time_ms": 150
    }
    
    logger.info("📊 Performance Comparison:")
    logger.info(f"Agent Instantiation: {traditional_metrics['agent_instantiation_ms']}ms → {agno_metrics['agent_instantiation_us']}μs (5000x improvement)")
    logger.info(f"Memory Usage: {traditional_metrics['memory_per_agent_mb']}MB → {agno_metrics['memory_per_agent_kib']}KiB (50x improvement)")
    logger.info(f"Concurrent Agents: {traditional_metrics['max_concurrent_agents']} → {agno_metrics['max_concurrent_agents']} (100x improvement)")
    logger.info(f"Response Time: {traditional_metrics['response_time_ms']}ms → {agno_metrics['response_time_ms']}ms (5x improvement)")

if __name__ == "__main__":
    asyncio.run(demonstrate_sales_intelligence_vsa())
    asyncio.run(demonstrate_performance_improvements()) 