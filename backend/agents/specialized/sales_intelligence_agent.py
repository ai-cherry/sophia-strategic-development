"""
Sales Intelligence Agent - Enhanced AI-Powered Sales Analysis

Extends the existing SalesCoachAgent with advanced capabilities:
- Deal risk assessment with hybrid AI approach
- Sales email/follow-up generation using SmartAIService  
- Competitor talking points with Cortex Search
- Revenue forecasting and pipeline analysis
- Advanced sales coaching with performance tracking
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

from backend.agents.core.base_agent import BaseAgent
from backend.agents.specialized.sales_coach_agent import SalesCoachAgent
from backend.services.smart_ai_service import (
    smart_ai_service,
    LLMRequest,
    TaskType,
    generate_executive_insight
)
from backend.utils.snowflake_cortex_service import SnowflakeCortexService
from backend.utils.snowflake_gong_connector import SnowflakeGongConnector
from backend.utils.snowflake_hubspot_connector import SnowflakeHubSpotConnector
from backend.mcp.ai_memory_mcp_server import EnhancedAiMemoryMCPServer, MemoryCategory
from backend.services.foundational_knowledge_service import FoundationalKnowledgeService

logger = logging.getLogger(__name__)


class DealRiskLevel(str, Enum):
    """Deal risk assessment levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SalesStage(str, Enum):
    """Sales pipeline stages"""
    PROSPECTING = "prospecting"
    QUALIFICATION = "qualification"
    DISCOVERY = "discovery"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    CLOSING = "closing"
    WON = "won"
    LOST = "lost"


class EmailType(str, Enum):
    """Types of sales emails"""
    FOLLOW_UP = "follow_up"
    PROPOSAL = "proposal"
    OBJECTION_HANDLING = "objection_handling"
    CHECK_IN = "check_in"
    CLOSING = "closing"
    THANK_YOU = "thank_you"
    RE_ENGAGEMENT = "re_engagement"


@dataclass
class DealRiskAssessment:
    """Deal risk assessment result"""
    deal_id: str
    deal_name: str
    account_name: str
    deal_stage: SalesStage
    deal_value: float
    close_date: datetime
    
    # Risk factors
    risk_level: DealRiskLevel
    risk_score: float  # 0-100
    risk_factors: List[str]
    
    # AI insights
    ai_analysis: str
    recommendations: List[str]
    next_actions: List[str]
    
    # Supporting data
    recent_activities: List[Dict[str, Any]]
    gong_insights: List[Dict[str, Any]]
    stakeholder_sentiment: Dict[str, float]
    
    # Metadata
    confidence_score: float
    analysis_timestamp: datetime = datetime.now()


@dataclass
class SalesEmailRequest:
    """Request for AI-generated sales email"""
    email_type: EmailType
    deal_id: str
    recipient_name: str
    recipient_role: str
    context: str
    key_points: List[str]
    call_to_action: str
    tone: str = "professional"
    include_attachments: bool = False
    urgency_level: str = "normal"


@dataclass
class CompetitorTalkingPoints:
    """Competitor talking points and differentiators"""
    competitor_name: str
    deal_context: str
    
    # Talking points
    key_differentiators: List[str]
    competitive_advantages: List[str]
    objection_responses: List[str]
    proof_points: List[str]
    
    # AI insights
    positioning_strategy: str
    recommended_approach: str
    
    confidence_score: float


@dataclass
class PipelineAnalysis:
    """Sales pipeline analysis result"""
    analysis_period: str
    total_pipeline_value: float
    weighted_pipeline_value: float
    
    # Stage analysis
    deals_by_stage: Dict[str, int]
    value_by_stage: Dict[str, float]
    conversion_rates: Dict[str, float]
    
    # Forecasting
    forecast_confidence: float
    likely_close_value: float
    best_case_value: float
    worst_case_value: float
    
    # AI insights
    pipeline_health_score: float
    key_insights: List[str]
    recommendations: List[str]
    
    analysis_timestamp: datetime = datetime.now()


class SalesIntelligenceAgent(BaseAgent):
    """
    Enhanced Sales Intelligence Agent
    
    Capabilities:
    - Advanced deal risk assessment with AI insights
    - Sales email generation using SmartAIService
    - Competitor analysis and talking points
    - Pipeline forecasting and health analysis
    - Enhanced sales coaching with performance tracking
    """

    def __init__(self):
        super().__init__()
        self.name = "sales_intelligence"
        self.description = "AI-powered sales intelligence and coaching"

        # Service integrations
        self.cortex_service: Optional[SnowflakeCortexService] = None
        self.gong_connector: Optional[SnowflakeGongConnector] = None
        self.hubspot_connector: Optional[SnowflakeHubSpotConnector] = None
        self.ai_memory: Optional[EnhancedAiMemoryMCPServer] = None
        self.knowledge_service: Optional[FoundationalKnowledgeService] = None
        self.sales_coach: Optional[SalesCoachAgent] = None

        self.initialized = False

    async def initialize(self) -> None:
        """Initialize the Sales Intelligence Agent"""
        if self.initialized:
            return

        try:
            # Initialize services
            self.cortex_service = SnowflakeCortexService()
            self.gong_connector = SnowflakeGongConnector()
            self.hubspot_connector = SnowflakeHubSpotConnector()
            self.ai_memory = EnhancedAiMemoryMCPServer()
            self.knowledge_service = FoundationalKnowledgeService()
            self.sales_coach = SalesCoachAgent()

            # Initialize all services
            await self.ai_memory.initialize()
            await self.sales_coach.initialize()
            await smart_ai_service.initialize()

            self.initialized = True
            logger.info("✅ Sales Intelligence Agent initialized")

        except Exception as e:
            logger.error(f"Failed to initialize Sales Intelligence Agent: {e}")
            raise

    async def assess_deal_risk(
        self, deal_id: str, include_gong_analysis: bool = True
    ) -> Optional[DealRiskAssessment]:
        """
        Comprehensive deal risk assessment using hybrid AI approach
        
        Args:
            deal_id: HubSpot deal ID
            include_gong_analysis: Whether to include Gong call insights
            
        Returns:
            Comprehensive deal risk assessment
        """
        if not self.initialized:
            await self.initialize()

        try:
            # Get deal data from HubSpot via Snowflake
            async with self.hubspot_connector as connector:
                deal_data = await connector.get_deal_details(deal_id)

                if not deal_data:
                    logger.warning(f"No deal data found for ID: {deal_id}")
                    return None

            # Get recent activities and engagement data
            recent_activities = await self._get_recent_deal_activities(deal_id)
            
            # Get Gong insights if requested
            gong_insights = []
            stakeholder_sentiment = {}
            
            if include_gong_analysis:
                gong_insights = await self._get_gong_insights_for_deal(deal_id)
                stakeholder_sentiment = await self._analyze_stakeholder_sentiment(deal_id)

            # Calculate risk factors using Snowflake Cortex
            risk_factors = await self._calculate_risk_factors(
                deal_data, recent_activities, gong_insights
            )

            # Generate comprehensive AI analysis using SmartAIService
            ai_analysis = await self._generate_deal_analysis(
                deal_data, risk_factors, gong_insights, stakeholder_sentiment
            )

            # Calculate overall risk score
            risk_score = self._calculate_risk_score(risk_factors, stakeholder_sentiment)
            risk_level = self._determine_risk_level(risk_score)

            # Generate specific recommendations
            recommendations = await self._generate_deal_recommendations(
                deal_data, risk_factors, ai_analysis
            )

            # Create assessment result
            assessment = DealRiskAssessment(
                deal_id=deal_id,
                deal_name=deal_data.get("DEAL_NAME", "Unknown"),
                account_name=deal_data.get("COMPANY_NAME", "Unknown"),
                deal_stage=SalesStage(deal_data.get("DEAL_STAGE", "qualification").lower().replace(" ", "_")),
                deal_value=deal_data.get("AMOUNT", 0.0),
                close_date=deal_data.get("CLOSE_DATE", datetime.now()),
                risk_level=risk_level,
                risk_score=risk_score,
                risk_factors=risk_factors,
                ai_analysis=ai_analysis,
                recommendations=recommendations,
                next_actions=await self._generate_next_actions(deal_data, risk_factors),
                recent_activities=recent_activities,
                gong_insights=gong_insights,
                stakeholder_sentiment=stakeholder_sentiment,
                confidence_score=0.9
            )

            # Store assessment in AI Memory
            await self.ai_memory.store_memory(
                content=f"Deal risk assessment for {deal_data.get('DEAL_NAME')}: {risk_level.value} risk, {ai_analysis}",
                category=MemoryCategory.HUBSPOT_DEAL_INSIGHT,
                tags=[
                    "deal_risk_assessment",
                    risk_level.value,
                    deal_data.get("DEAL_STAGE", "unknown").lower(),
                    f"value_{int(deal_data.get('AMOUNT', 0)/1000)}k"
                ],
                importance_score=0.9,
                metadata={
                    "deal_id": deal_id,
                    "risk_score": risk_score,
                    "deal_value": deal_data.get("AMOUNT", 0)
                }
            )

            logger.info(f"Completed deal risk assessment for {deal_id}: {risk_level.value} risk")
            return assessment

        except Exception as e:
            logger.error(f"Error assessing deal risk for {deal_id}: {e}")
            return None

    async def generate_sales_email(
        self, request: SalesEmailRequest
    ) -> Dict[str, Any]:
        """
        Generate personalized sales email using SmartAIService
        
        Args:
            request: Sales email generation request
            
        Returns:
            Generated email with metadata
        """
        if not self.initialized:
            await self.initialize()

        try:
            # Get deal context
            deal_context = ""
            async with self.hubspot_connector as connector:
                deal_data = await connector.get_deal_details(request.deal_id)
                if deal_data:
                    deal_context = f"""
                    Deal: {deal_data.get('DEAL_NAME', 'Unknown')}
                    Company: {deal_data.get('COMPANY_NAME', 'Unknown')}
                    Stage: {deal_data.get('DEAL_STAGE', 'Unknown')}
                    Value: ${deal_data.get('AMOUNT', 0):,.2f}
                    Close Date: {deal_data.get('CLOSE_DATE', 'TBD')}
                    """

            # Get recent Gong call context
            gong_context = ""
            recent_calls = await self._get_recent_gong_calls(request.deal_id, limit=2)
            if recent_calls:
                gong_context = "Recent call insights:\n" + "\n".join([
                    f"- {call.get('summary', 'Call summary not available')}"
                    for call in recent_calls
                ])

            # Build comprehensive email prompt
            email_prompt = f"""
            Generate a {request.email_type.value} sales email:
            
            Recipient: {request.recipient_name} ({request.recipient_role})
            Tone: {request.tone}
            Urgency: {request.urgency_level}
            
            Deal Context:
            {deal_context}
            
            Situation Context:
            {request.context}
            
            {gong_context}
            
            Key Points to Address:
            {chr(10).join([f"- {point}" for point in request.key_points])}
            
            Call to Action: {request.call_to_action}
            
            Requirements:
            - Personalized and relevant to {request.recipient_role}
            - Professional yet engaging tone
            - Clear value proposition
            - Specific next steps
            - Appropriate urgency level
            - Include relevant context from recent interactions
            
            Generate a compelling email that drives action.
            """

            # Use SmartAIService for high-quality email generation
            llm_request = LLMRequest(
                messages=[{"role": "user", "content": email_prompt}],
                task_type=TaskType.DOCUMENT_ANALYSIS,  # Good for structured content
                performance_priority=True,
                cost_sensitivity=0.7,
                user_id="sales_agent",
                temperature=0.7,  # Balanced creativity and consistency
                metadata={
                    "email_type": request.email_type.value,
                    "deal_id": request.deal_id
                }
            )

            response = await smart_ai_service.generate_response(llm_request)
            generated_email = response.content

            # Generate subject line variations using Cortex
            subject_lines = []
            async with self.cortex_service as cortex:
                subject_prompt = f"""
                Generate 3 compelling email subject lines for this {request.email_type.value} email:
                
                Email content: {generated_email[:500]}...
                Recipient role: {request.recipient_role}
                Urgency: {request.urgency_level}
                
                Subject lines should be:
                - Specific and relevant
                - Action-oriented
                - Appropriate urgency level
                - Under 50 characters
                """

                subject_response = await cortex.complete_text_with_cortex(
                    prompt=subject_prompt,
                    max_tokens=150
                )

                if subject_response:
                    subject_lines = [
                        line.strip().strip('"').strip("'")
                        for line in subject_response.split('\n')
                        if line.strip() and not line.strip().startswith(('1.', '2.', '3.', '-'))
                    ][:3]

            # Analyze email quality
            quality_score = await self._analyze_email_quality(generated_email, request)

            # Store email in AI Memory
            await self.ai_memory.store_memory(
                content=f"Generated {request.email_type.value} email for {request.recipient_name} on deal {request.deal_id}",
                category=MemoryCategory.SALES_EMAIL_GENERATED,
                tags=[
                    "sales_email",
                    request.email_type.value,
                    request.recipient_role.lower(),
                    request.urgency_level
                ],
                importance_score=0.7,
                metadata={
                    "deal_id": request.deal_id,
                    "email_type": request.email_type.value,
                    "quality_score": quality_score
                }
            )

            result = {
                "email_content": generated_email,
                "subject_lines": subject_lines,
                "email_type": request.email_type.value,
                "recipient": {
                    "name": request.recipient_name,
                    "role": request.recipient_role
                },
                "deal_id": request.deal_id,
                "quality_score": quality_score,
                "word_count": len(generated_email.split()),
                "generated_at": datetime.now().isoformat(),
                "model_used": response.model,
                "cost_usd": response.cost_usd,
                "generation_time_ms": response.latency_ms
            }

            logger.info(f"Generated {request.email_type.value} email for deal {request.deal_id}")
            return result

        except Exception as e:
            logger.error(f"Error generating sales email: {e}")
            return {"error": str(e), "email_content": ""}

    async def get_competitor_talking_points(
        self, competitor_name: str, deal_id: str
    ) -> Optional[CompetitorTalkingPoints]:
        """
        Generate competitor talking points using Cortex Search and knowledge base
        
        Args:
            competitor_name: Name of competitor
            deal_id: Related deal ID for context
            
        Returns:
            Competitor talking points and strategy
        """
        if not self.initialized:
            await self.initialize()

        try:
            # Get deal context
            deal_context = ""
            async with self.hubspot_connector as connector:
                deal_data = await connector.get_deal_details(deal_id)
                if deal_data:
                    deal_context = f"Deal: {deal_data.get('DEAL_NAME')} at {deal_data.get('COMPANY_NAME')} (${deal_data.get('AMOUNT', 0):,.0f})"

            # Search knowledge base for competitor information using Cortex
            competitor_info = ""
            if self.knowledge_service:
                competitor_data = await self.knowledge_service.search_entities(
                    query=competitor_name,
                    entity_type="competitor",
                    limit=1
                )
                if competitor_data:
                    competitor_info = competitor_data[0].get("description", "")

            # Generate comprehensive competitive analysis
            competitive_prompt = f"""
            Generate competitive talking points for sales conversation against {competitor_name}:
            
            Deal Context: {deal_context}
            
            Competitor Information:
            {competitor_info}
            
            Provide:
            1. Key differentiators (5 specific points)
            2. Competitive advantages (3-5 points)
            3. Objection responses (common objections and responses)
            4. Proof points (case studies, metrics, testimonials)
            5. Positioning strategy
            6. Recommended approach for this specific deal
            
            Focus on factual, defensible points that highlight our strengths.
            """

            # Use SmartAIService for competitive analysis
            llm_request = LLMRequest(
                messages=[{"role": "user", "content": competitive_prompt}],
                task_type=TaskType.COMPETITIVE_ANALYSIS,
                performance_priority=True,
                cost_sensitivity=0.8,
                user_id="sales_agent",
                metadata={
                    "competitor": competitor_name,
                    "deal_id": deal_id
                }
            )

            response = await smart_ai_service.generate_response(llm_request)
            analysis_content = response.content

            # Extract structured talking points using Cortex
            async with self.cortex_service as cortex:
                extraction_prompt = f"""
                From this competitive analysis, extract structured talking points:
                
                {analysis_content}
                
                Extract and format as:
                DIFFERENTIATORS: (list 5 key points)
                ADVANTAGES: (list 3-5 competitive advantages)
                OBJECTIONS: (list common objections and responses)
                PROOF: (list proof points and evidence)
                """

                structured_points = await cortex.complete_text_with_cortex(
                    prompt=extraction_prompt,
                    max_tokens=600
                )

                # Parse structured points
                differentiators = []
                advantages = []
                objection_responses = []
                proof_points = []

                if structured_points:
                    sections = structured_points.split('\n')
                    current_section = None
                    
                    for line in sections:
                        line = line.strip()
                        if line.startswith('DIFFERENTIATORS:'):
                            current_section = 'diff'
                        elif line.startswith('ADVANTAGES:'):
                            current_section = 'adv'
                        elif line.startswith('OBJECTIONS:'):
                            current_section = 'obj'
                        elif line.startswith('PROOF:'):
                            current_section = 'proof'
                        elif line and line.startswith('-'):
                            point = line[1:].strip()
                            if current_section == 'diff':
                                differentiators.append(point)
                            elif current_section == 'adv':
                                advantages.append(point)
                            elif current_section == 'obj':
                                objection_responses.append(point)
                            elif current_section == 'proof':
                                proof_points.append(point)

            # Generate positioning strategy
            positioning_strategy = await self._generate_positioning_strategy(
                competitor_name, deal_context, analysis_content
            )

            # Create talking points result
            talking_points = CompetitorTalkingPoints(
                competitor_name=competitor_name,
                deal_context=deal_context,
                key_differentiators=differentiators[:5],
                competitive_advantages=advantages[:5],
                objection_responses=objection_responses[:5],
                proof_points=proof_points[:5],
                positioning_strategy=positioning_strategy,
                recommended_approach=analysis_content.split('\n')[-1] if analysis_content else "",
                confidence_score=0.85
            )

            # Store talking points in AI Memory
            await self.ai_memory.store_memory(
                content=f"Competitor talking points for {competitor_name} in deal {deal_id}: {positioning_strategy}",
                category=MemoryCategory.COMPETITIVE_INTELLIGENCE,
                tags=[
                    "competitor_talking_points",
                    competitor_name.lower().replace(" ", "_"),
                    "sales_enablement",
                    f"deal_{deal_id}"
                ],
                importance_score=0.8,
                metadata={
                    "competitor": competitor_name,
                    "deal_id": deal_id
                }
            )

            logger.info(f"Generated talking points for {competitor_name} in deal {deal_id}")
            return talking_points

        except Exception as e:
            logger.error(f"Error generating competitor talking points: {e}")
            return None

    async def analyze_pipeline_health(
        self, sales_rep: Optional[str] = None, time_period_days: int = 90
    ) -> Optional[PipelineAnalysis]:
        """
        Analyze sales pipeline health and forecasting
        
        Args:
            sales_rep: Specific sales rep (None for all)
            time_period_days: Analysis period in days
            
        Returns:
            Comprehensive pipeline analysis
        """
        if not self.initialized:
            await self.initialize()

        try:
            # Get pipeline data from HubSpot via Snowflake
            async with self.hubspot_connector as connector:
                pipeline_data = await connector.get_pipeline_data(
                    sales_rep=sales_rep,
                    time_period_days=time_period_days
                )

                if not pipeline_data:
                    logger.warning("No pipeline data available")
                    return None

            # Calculate pipeline metrics
            total_pipeline_value = sum(deal.get("AMOUNT", 0) for deal in pipeline_data)
            
            # Group by stage
            deals_by_stage = {}
            value_by_stage = {}
            
            for deal in pipeline_data:
                stage = deal.get("DEAL_STAGE", "unknown")
                deals_by_stage[stage] = deals_by_stage.get(stage, 0) + 1
                value_by_stage[stage] = value_by_stage.get(stage, 0) + deal.get("AMOUNT", 0)

            # Calculate weighted pipeline (probability-adjusted)
            stage_probabilities = {
                "prospecting": 0.1,
                "qualification": 0.2,
                "discovery": 0.3,
                "proposal": 0.5,
                "negotiation": 0.7,
                "closing": 0.9
            }
            
            weighted_pipeline_value = sum(
                value * stage_probabilities.get(stage.lower(), 0.3)
                for stage, value in value_by_stage.items()
            )

            # Generate AI insights using SmartAIService
            pipeline_prompt = f"""
            Analyze this sales pipeline and provide insights:
            
            Pipeline Overview:
            - Total pipeline value: ${total_pipeline_value:,.2f}
            - Weighted pipeline value: ${weighted_pipeline_value:,.2f}
            - Total deals: {len(pipeline_data)}
            - Analysis period: {time_period_days} days
            
            Deals by stage: {deals_by_stage}
            Value by stage: {value_by_stage}
            
            Provide:
            1. Pipeline health assessment (score 0-100)
            2. Key insights about pipeline composition
            3. Forecasting analysis and confidence level
            4. Specific recommendations for improvement
            5. Risk factors and opportunities
            """

            insights_response = await generate_executive_insight(
                pipeline_prompt, user_id="sales_agent"
            )

            # Extract pipeline health score
            health_score = 75.0  # Default
            if "score" in insights_response.lower():
                import re
                score_match = re.search(r'(\d+\.?\d*)/100|(\d+\.?\d*)%', insights_response)
                if score_match:
                    health_score = float(score_match.group(1) or score_match.group(2))

            # Generate forecasting
            forecast_confidence = min(0.9, weighted_pipeline_value / max(total_pipeline_value, 1))
            likely_close_value = weighted_pipeline_value
            best_case_value = total_pipeline_value * 0.8
            worst_case_value = weighted_pipeline_value * 0.6

            # Extract key insights and recommendations
            insights_lines = insights_response.split('\n')
            key_insights = [line.strip() for line in insights_lines if line.strip() and any(
                keyword in line.lower() for keyword in ['insight', 'key', 'important', 'notable']
            )][:5]
            
            recommendations = [line.strip() for line in insights_lines if line.strip() and any(
                keyword in line.lower() for keyword in ['recommend', 'suggest', 'should', 'improve']
            )][:5]

            # Create pipeline analysis
            analysis = PipelineAnalysis(
                analysis_period=f"{time_period_days} days",
                total_pipeline_value=total_pipeline_value,
                weighted_pipeline_value=weighted_pipeline_value,
                deals_by_stage=deals_by_stage,
                value_by_stage=value_by_stage,
                conversion_rates=stage_probabilities,  # Simplified
                forecast_confidence=forecast_confidence,
                likely_close_value=likely_close_value,
                best_case_value=best_case_value,
                worst_case_value=worst_case_value,
                pipeline_health_score=health_score,
                key_insights=key_insights,
                recommendations=recommendations
            )

            # Store analysis in AI Memory
            await self.ai_memory.store_memory(
                content=f"Pipeline analysis: ${total_pipeline_value:,.0f} total, {health_score:.0f}/100 health score",
                category=MemoryCategory.SALES_PIPELINE_ANALYSIS,
                tags=[
                    "pipeline_analysis",
                    f"health_{health_score:.0f}",
                    f"value_{int(total_pipeline_value/1000)}k",
                    sales_rep.lower().replace(" ", "_") if sales_rep else "all_reps"
                ],
                importance_score=0.9,
                metadata={
                    "total_value": total_pipeline_value,
                    "health_score": health_score,
                    "sales_rep": sales_rep
                }
            )

            logger.info(f"Completed pipeline analysis: ${total_pipeline_value:,.0f} total value")
            return analysis

        except Exception as e:
            logger.error(f"Error analyzing pipeline health: {e}")
            return None

    # Helper methods
    async def _get_recent_deal_activities(self, deal_id: str) -> List[Dict[str, Any]]:
        """Get recent activities for a deal"""
        try:
            # Mock implementation - in production would query actual activity data
            return [
                {
                    "activity_type": "email",
                    "date": datetime.now() - timedelta(days=2),
                    "description": "Follow-up email sent"
                },
                {
                    "activity_type": "call",
                    "date": datetime.now() - timedelta(days=5),
                    "description": "Discovery call completed"
                }
            ]
        except Exception as e:
            logger.error(f"Error getting deal activities: {e}")
            return []

    async def _get_gong_insights_for_deal(self, deal_id: str) -> List[Dict[str, Any]]:
        """Get Gong call insights related to a deal"""
        try:
            async with self.gong_connector as connector:
                calls = await connector.get_calls_for_deal(deal_id, limit=5)
                return calls or []
        except Exception as e:
            logger.error(f"Error getting Gong insights: {e}")
            return []

    async def _analyze_stakeholder_sentiment(self, deal_id: str) -> Dict[str, float]:
        """Analyze sentiment of stakeholders in deal"""
        try:
            # Mock implementation - in production would analyze actual call data
            return {
                "decision_maker": 0.7,
                "influencer": 0.5,
                "user": 0.8,
                "champion": 0.9
            }
        except Exception as e:
            logger.error(f"Error analyzing stakeholder sentiment: {e}")
            return {}

    async def _calculate_risk_factors(
        self, deal_data: Dict, activities: List, gong_insights: List
    ) -> List[str]:
        """Calculate risk factors for a deal"""
        risk_factors = []
        
        # Check deal age
        if deal_data.get("CREATED_DATE"):
            deal_age = (datetime.now() - deal_data["CREATED_DATE"]).days
            if deal_age > 90:
                risk_factors.append("Deal has been open for over 90 days")
        
        # Check close date
        if deal_data.get("CLOSE_DATE"):
            days_to_close = (deal_data["CLOSE_DATE"] - datetime.now()).days
            if days_to_close < 0:
                risk_factors.append("Deal is past close date")
            elif days_to_close < 7:
                risk_factors.append("Deal close date is within 7 days")
        
        # Check activity level
        if len(activities) < 2:
            risk_factors.append("Low activity level in past 30 days")
        
        # Check Gong insights
        if len(gong_insights) == 0:
            risk_factors.append("No recent call activity recorded")
        
        return risk_factors

    async def _generate_deal_analysis(
        self, deal_data: Dict, risk_factors: List, gong_insights: List, sentiment: Dict
    ) -> str:
        """Generate comprehensive deal analysis using AI"""
        try:
            analysis_prompt = f"""
            Analyze this sales deal and provide insights:
            
            Deal: {deal_data.get('DEAL_NAME', 'Unknown')}
            Company: {deal_data.get('COMPANY_NAME', 'Unknown')}
            Value: ${deal_data.get('AMOUNT', 0):,.2f}
            Stage: {deal_data.get('DEAL_STAGE', 'Unknown')}
            Close Date: {deal_data.get('CLOSE_DATE', 'TBD')}
            
            Risk Factors:
            {chr(10).join([f"- {factor}" for factor in risk_factors])}
            
            Stakeholder Sentiment: {sentiment}
            Recent Call Insights: {len(gong_insights)} calls analyzed
            
            Provide a comprehensive analysis of deal health, likelihood to close, and strategic recommendations.
            """

            return await generate_executive_insight(analysis_prompt, user_id="sales_agent")

        except Exception as e:
            logger.error(f"Error generating deal analysis: {e}")
            return "Analysis unavailable due to technical issues."

    def _calculate_risk_score(self, risk_factors: List[str], sentiment: Dict[str, float]) -> float:
        """Calculate numerical risk score (0-100)"""
        base_score = 50.0  # Neutral starting point
        
        # Adjust for risk factors
        risk_penalty = len(risk_factors) * 15
        base_score += risk_penalty
        
        # Adjust for sentiment
        avg_sentiment = sum(sentiment.values()) / len(sentiment) if sentiment else 0.5
        sentiment_adjustment = (0.5 - avg_sentiment) * 40
        base_score += sentiment_adjustment
        
        return max(0, min(100, base_score))

    def _determine_risk_level(self, risk_score: float) -> DealRiskLevel:
        """Determine risk level from score"""
        if risk_score >= 80:
            return DealRiskLevel.CRITICAL
        elif risk_score >= 60:
            return DealRiskLevel.HIGH
        elif risk_score >= 40:
            return DealRiskLevel.MEDIUM
        else:
            return DealRiskLevel.LOW

    async def _generate_deal_recommendations(
        self, deal_data: Dict, risk_factors: List, analysis: str
    ) -> List[str]:
        """Generate specific recommendations for deal"""
        try:
            async with self.cortex_service as cortex:
                rec_prompt = f"""
                Based on this deal analysis, provide 5 specific actionable recommendations:
                
                {analysis}
                
                Risk factors: {risk_factors}
                
                Format as numbered list of concrete actions.
                """

                recommendations = await cortex.complete_text_with_cortex(
                    prompt=rec_prompt,
                    max_tokens=300
                )

                if recommendations:
                    return [
                        rec.strip() for rec in recommendations.split('\n')
                        if rec.strip() and any(char.isdigit() for char in rec[:5])
                    ][:5]

        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")

        return ["Schedule follow-up meeting", "Clarify decision timeline", "Identify key stakeholders"]

    async def _generate_next_actions(self, deal_data: Dict, risk_factors: List) -> List[str]:
        """Generate immediate next actions"""
        actions = []
        
        if "past close date" in str(risk_factors).lower():
            actions.append("Update close date and timeline")
        
        if "low activity" in str(risk_factors).lower():
            actions.append("Schedule stakeholder meeting")
        
        if "no recent call" in str(risk_factors).lower():
            actions.append("Book discovery/check-in call")
        
        actions.append("Send follow-up email with next steps")
        actions.append("Review and update deal stage")
        
        return actions[:5]

    async def _get_recent_gong_calls(self, deal_id: str, limit: int = 5) -> List[Dict]:
        """Get recent Gong calls for context"""
        try:
            async with self.gong_connector as connector:
                return await connector.get_calls_for_deal(deal_id, limit=limit) or []
        except Exception as e:
            logger.error(f"Error getting recent calls: {e}")
            return []

    async def _analyze_email_quality(self, email_content: str, request: SalesEmailRequest) -> float:
        """Analyze generated email quality"""
        try:
            async with self.cortex_service as cortex:
                quality_prompt = f"""
                Rate this sales email quality (0-100):
                
                Email: {email_content}
                Type: {request.email_type.value}
                Recipient: {request.recipient_role}
                
                Evaluate: personalization, clarity, value proposition, call-to-action, professionalism.
                
                Provide only numeric score.
                """

                score_text = await cortex.complete_text_with_cortex(
                    prompt=quality_prompt,
                    max_tokens=10
                )

                if score_text and score_text.strip().replace('.', '').isdigit():
                    return float(score_text.strip())

        except Exception as e:
            logger.error(f"Error analyzing email quality: {e}")

        return 80.0  # Default score

    async def _generate_positioning_strategy(
        self, competitor: str, deal_context: str, analysis: str
    ) -> str:
        """Generate positioning strategy against competitor"""
        try:
            async with self.cortex_service as cortex:
                strategy_prompt = f"""
                Create a positioning strategy against {competitor}:
                
                Deal context: {deal_context}
                Analysis: {analysis[:500]}...
                
                Provide concise positioning strategy (2-3 sentences).
                """

                return await cortex.complete_text_with_cortex(
                    prompt=strategy_prompt,
                    max_tokens=150
                ) or "Focus on our unique value proposition and proven results."

        except Exception as e:
            logger.error(f"Error generating positioning strategy: {e}")
            return "Focus on our unique value proposition and proven results." 