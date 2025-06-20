import asyncio
import logging
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

from backend.agents.core.base_agent import BaseAgent, AgentConfig, AgentCapability, Task, create_agent_response
from backend.integrations.gong.gong_integration import GongIntegration
from backend.integrations.portkey_client import PortkeyClient
from backend.core.config_manager import get_secret

logger = logging.getLogger(__name__)


class InsightType(Enum):
    NEW_COMPETITOR = "new_competitor"
    PRODUCT_GAP = "product_gap"
    USE_CASE = "use_case"
    PRICING_OBJECTION = "pricing_objection"
    FEATURE_REQUEST = "feature_request"
    INTEGRATION_NEED = "integration_need"
    SECURITY_CONCERN = "security_concern"


@dataclass
class ProactiveInsight:
    id: str
    type: InsightType
    source: str
    source_url: str
    insight: str
    question: str
    context: str
    confidence: float
    timestamp: datetime
    status: str = "pending"
    metadata: Dict[str, Any] = None


class InsightExtractionAgent(BaseAgent):
    """
    Analyzes Gong transcripts and other data sources to proactively extract
    insights that should be added to the knowledge base.
    """
    
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.gong_integration = GongIntegration()
        self.portkey_client = PortkeyClient()
        self.pending_insights: List[ProactiveInsight] = []
        
    async def get_capabilities(self) -> List[AgentCapability]:
        return [
            AgentCapability(
                name="analyze_transcript_for_insights",
                description="Analyzes a Gong transcript to extract novel insights",
                input_types=["call_id"],
                output_types=["insights"],
                estimated_duration=45.0
            ),
            AgentCapability(
                name="batch_analyze_recent_calls",
                description="Analyzes recent calls to extract insights in batch",
                input_types=["hours_back"],
                output_types=["insights_summary"],
                estimated_duration=300.0
            ),
            AgentCapability(
                name="get_pending_insights",
                description="Retrieves all pending insights awaiting review",
                input_types=[],
                output_types=["pending_insights"],
                estimated_duration=1.0
            ),
            AgentCapability(
                name="update_insight_status",
                description="Updates the status of an insight (approved/rejected)",
                input_types=["insight_id", "status", "edited_content"],
                output_types=["update_result"],
                estimated_duration=5.0
            )
        ]
    
    async def process_task(self, task: Task) -> Dict[str, Any]:
        """Process insight extraction tasks"""
        
        if task.task_type == "analyze_transcript_for_insights":
            return await self._analyze_single_transcript(task)
        elif task.task_type == "batch_analyze_recent_calls":
            return await self._batch_analyze_calls(task)
        elif task.task_type == "get_pending_insights":
            return await self._get_pending_insights()
        elif task.task_type == "update_insight_status":
            return await self._update_insight_status(task)
        else:
            return await create_agent_response(False, error=f"Unknown task type: {task.task_type}")
    
    async def _analyze_single_transcript(self, task: Task) -> Dict[str, Any]:
        """Analyze a single call transcript for insights"""
        call_id = task.task_data.get("call_id")
        if not call_id:
            return await create_agent_response(False, error="call_id is required")
        
        try:
            # Get call details and transcript
            call_details = await self.gong_integration.get_call_details(call_id)
            transcript = await self.gong_integration.get_call_transcript(call_id)
            
            if not transcript:
                return await create_agent_response(False, error="No transcript available")
            
            # Convert transcript to text for analysis
            transcript_text = "\n".join([f"{t.speaker_name}: {t.text}" for t in transcript])
            
            # Extract insights using LLM
            insights = await self._extract_insights_with_llm(
                transcript_text, 
                call_details,
                call_id
            )
            
            # Store insights
            self.pending_insights.extend(insights)
            
            return await create_agent_response(True, data={
                "call_id": call_id,
                "insights_found": len(insights),
                "insights": [self._insight_to_dict(i) for i in insights]
            })
            
        except Exception as e:
            logger.error(f"Error analyzing transcript: {e}")
            return await create_agent_response(False, error=str(e))
    
    async def _extract_insights_with_llm(
        self, 
        transcript_text: str, 
        call_details: Dict[str, Any],
        call_id: str
    ) -> List[ProactiveInsight]:
        """Use LLM to extract insights from transcript"""
        
        # Prepare the prompt
        prompt = f"""
        Analyze this sales call transcript and identify any novel information that should be added to our knowledge base.
        Focus on:
        1. New competitors mentioned (not in our current list: Entrata, RealPage, Yardi)
        2. Product gaps or limitations the customer expressed frustration about
        3. Unexpected use cases for our product
        4. Pricing objections or concerns
        5. Feature requests
        6. Integration needs with other systems
        7. Security or compliance concerns

        For each insight found, provide:
        - Type (one of: new_competitor, product_gap, use_case, pricing_objection, feature_request, integration_need, security_concern)
        - The specific insight (brief, factual statement)
        - A question to ask the user about adding this to the knowledge base
        - The relevant context from the conversation
        - Confidence score (0.0 to 1.0)

        Transcript:
        {transcript_text[:8000]}  # Limit to avoid token limits

        Return the results as a JSON array. If no insights found, return empty array.
        """
        
        try:
            response = await self.portkey_client.llm_call(
                prompt=prompt,
                model="claude-3-5-sonnet-20241022",
                temperature=0.3
            )
            
            # Parse the response
            response_content = response.get("choices", [{}])[0].get("message", {}).get("content", "[]")
            insights_data = json.loads(response_content)
            
            # Convert to ProactiveInsight objects
            insights = []
            for idx, insight_data in enumerate(insights_data):
                insight = ProactiveInsight(
                    id=f"insight_{call_id}_{idx}_{datetime.now().timestamp()}",
                    type=InsightType(insight_data.get("type", "use_case")),
                    source=f"Gong Call - {call_details.get('title', 'Unknown')}",
                    source_url=call_details.get('url', f"https://app.gong.io/call/{call_id}"),
                    insight=insight_data.get("insight", ""),
                    question=insight_data.get("question", "Should I add this to the knowledge base?"),
                    context=insight_data.get("context", ""),
                    confidence=float(insight_data.get("confidence", 0.7)),
                    timestamp=datetime.now(),
                    metadata={
                        "call_id": call_id,
                        "participants": call_details.get("participants", [])
                    }
                )
                insights.append(insight)
            
            return insights
            
        except Exception as e:
            logger.error(f"Error extracting insights with LLM: {e}")
            return []
    
    async def _batch_analyze_calls(self, task: Task) -> Dict[str, Any]:
        """Analyze recent calls in batch"""
        hours_back = task.task_data.get("hours_back", 24)
        
        try:
            # Get recent calls
            from_date = datetime.now() - timedelta(hours=hours_back)
            to_date = datetime.now()
            
            calls = await self.gong_integration.get_calls(from_date, to_date, limit=50)
            
            if not calls:
                return await create_agent_response(True, data={
                    "message": "No recent calls found",
                    "total_insights": 0
                })
            
            # Analyze each call
            total_insights = 0
            analyzed_calls = 0
            
            for call in calls[:10]:  # Limit to 10 calls for performance
                call_id = call.get('id')
                if call_id:
                    try:
                        # Create a task for single analysis
                        single_task = Task(
                            task_type="analyze_transcript_for_insights",
                            task_data={"call_id": call_id}
                        )
                        result = await self._analyze_single_transcript(single_task)
                        
                        if result.get("success"):
                            insights_count = result.get("data", {}).get("insights_found", 0)
                            total_insights += insights_count
                            analyzed_calls += 1
                            
                    except Exception as e:
                        logger.error(f"Error analyzing call {call_id}: {e}")
            
            return await create_agent_response(True, data={
                "analyzed_calls": analyzed_calls,
                "total_insights": total_insights,
                "time_range": {
                    "from": from_date.isoformat(),
                    "to": to_date.isoformat()
                }
            })
            
        except Exception as e:
            logger.error(f"Error in batch analysis: {e}")
            return await create_agent_response(False, error=str(e))
    
    async def _get_pending_insights(self) -> Dict[str, Any]:
        """Get all pending insights"""
        pending = [i for i in self.pending_insights if i.status == "pending"]
        
        return await create_agent_response(True, data={
            "pending_count": len(pending),
            "insights": [self._insight_to_dict(i) for i in pending]
        })
    
    async def _update_insight_status(self, task: Task) -> Dict[str, Any]:
        """Update the status of an insight"""
        insight_id = task.task_data.get("insight_id")
        new_status = task.task_data.get("status")
        edited_content = task.task_data.get("edited_content")
        
        if not insight_id or not new_status:
            return await create_agent_response(False, error="insight_id and status are required")
        
        # Find and update the insight
        for insight in self.pending_insights:
            if insight.id == insight_id:
                insight.status = new_status
                if edited_content:
                    insight.insight = edited_content
                
                # If approved, we would trigger adding to knowledge base here
                if new_status == "approved":
                    # TODO: Integrate with KnowledgeManager to add the insight
                    logger.info(f"Insight {insight_id} approved: {insight.insight}")
                
                return await create_agent_response(True, data={
                    "insight_id": insight_id,
                    "new_status": new_status,
                    "message": f"Insight {new_status}"
                })
        
        return await create_agent_response(False, error=f"Insight {insight_id} not found")
    
    def _insight_to_dict(self, insight: ProactiveInsight) -> Dict[str, Any]:
        """Convert insight to dictionary for serialization"""
        return {
            "id": insight.id,
            "type": insight.type.value,
            "source": insight.source,
            "source_url": insight.source_url,
            "insight": insight.insight,
            "question": insight.question,
            "context": insight.context,
            "confidence": insight.confidence,
            "timestamp": insight.timestamp.isoformat(),
            "status": insight.status,
            "metadata": insight.metadata
        } 