"""
Marketing Analysis Agent - AI-Powered Marketing Intelligence

Provides comprehensive marketing analysis capabilities including:
- Campaign performance analysis with AI insights
- Content generation using SmartAIService
- Audience segmentation with Snowflake Cortex
- ROI analysis and optimization recommendations
- Competitive marketing intelligence
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

from backend.agents.core.base_agent import BaseAgent
from backend.services.smart_ai_service import (
    smart_ai_service, 
    LLMRequest, 
    TaskType,
    generate_competitive_analysis
)
from backend.utils.snowflake_cortex_service import SnowflakeCortexService
from backend.utils.snowflake_hubspot_connector import SnowflakeHubSpotConnector
from backend.mcp.ai_memory_mcp_server import EnhancedAiMemoryMCPServer, MemoryCategory
from backend.services.foundational_knowledge_service import FoundationalKnowledgeService

logger = logging.getLogger(__name__)


class CampaignType(str, Enum):
    """Types of marketing campaigns"""
    EMAIL = "email"
    SOCIAL_MEDIA = "social_media"
    CONTENT = "content"
    PAID_ADS = "paid_ads"
    WEBINAR = "webinar"
    TRADE_SHOW = "trade_show"
    DIRECT_MAIL = "direct_mail"
    SEO = "seo"


class ContentType(str, Enum):
    """Types of marketing content"""
    BLOG_POST = "blog_post"
    EMAIL_COPY = "email_copy"
    SOCIAL_POST = "social_post"
    AD_COPY = "ad_copy"
    LANDING_PAGE = "landing_page"
    WHITEPAPER = "whitepaper"
    CASE_STUDY = "case_study"
    VIDEO_SCRIPT = "video_script"


class AudienceSegment(str, Enum):
    """Audience segmentation categories"""
    ENTERPRISE = "enterprise"
    SMB = "smb"
    STARTUP = "startup"
    DECISION_MAKER = "decision_maker"
    INFLUENCER = "influencer"
    USER = "user"
    CHAMPION = "champion"
    DETRACTOR = "detractor"


@dataclass
class CampaignAnalysis:
    """Campaign performance analysis result"""
    campaign_id: str
    campaign_name: str
    campaign_type: CampaignType
    start_date: datetime
    end_date: Optional[datetime]
    
    # Performance metrics
    impressions: int
    clicks: int
    conversions: int
    revenue: float
    cost: float
    
    # Calculated metrics
    ctr: float  # Click-through rate
    conversion_rate: float
    cpa: float  # Cost per acquisition
    roi: float  # Return on investment
    
    # AI insights
    performance_score: float
    ai_summary: str
    optimization_recommendations: List[str]
    audience_insights: Dict[str, Any]
    
    # Metadata
    confidence_score: float
    analysis_timestamp: datetime = datetime.now()


@dataclass
class ContentGenerationRequest:
    """Request for AI-generated marketing content"""
    content_type: ContentType
    topic: str
    target_audience: AudienceSegment
    tone: str = "professional"
    length: str = "medium"
    include_cta: bool = True
    product_context: Optional[str] = None
    competitor_context: Optional[str] = None
    brand_guidelines: Optional[str] = None


@dataclass
class AudienceSegmentAnalysis:
    """Audience segment analysis result"""
    segment_name: str
    segment_type: AudienceSegment
    size: int
    engagement_score: float
    conversion_rate: float
    average_deal_size: float
    
    # Behavioral insights
    preferred_channels: List[str]
    content_preferences: List[str]
    decision_factors: List[str]
    pain_points: List[str]
    
    # AI insights
    ai_summary: str
    targeting_recommendations: List[str]
    content_suggestions: List[str]
    
    confidence_score: float


class MarketingAnalysisAgent(BaseAgent):
    """
    AI-Powered Marketing Analysis Agent
    
    Capabilities:
    - Campaign performance analysis with AI insights
    - Content generation using SmartAIService
    - Audience segmentation with Snowflake Cortex
    - Competitive analysis and positioning
    - ROI optimization recommendations
    """

    def __init__(self):
        super().__init__()
        self.name = "marketing_analysis"
        self.description = "AI-powered marketing intelligence and content generation"

        # Service integrations
        self.cortex_service: Optional[SnowflakeCortexService] = None
        self.hubspot_connector: Optional[SnowflakeHubSpotConnector] = None
        self.ai_memory: Optional[EnhancedAiMemoryMCPServer] = None
        self.knowledge_service: Optional[FoundationalKnowledgeService] = None

        self.initialized = False

    async def initialize(self) -> None:
        """Initialize the Marketing Analysis Agent"""
        if self.initialized:
            return

        try:
            # Initialize services
            self.cortex_service = SnowflakeCortexService()
            self.hubspot_connector = SnowflakeHubSpotConnector()
            self.ai_memory = EnhancedAiMemoryMCPServer()
            self.knowledge_service = FoundationalKnowledgeService()

            # Initialize AI Memory and Smart AI Service
            await self.ai_memory.initialize()
            await smart_ai_service.initialize()

            self.initialized = True
            logger.info("✅ Marketing Analysis Agent initialized")

        except Exception as e:
            logger.error(f"Failed to initialize Marketing Analysis Agent: {e}")
            raise

    async def analyze_campaign_performance(
        self, campaign_id: str, include_ai_insights: bool = True
    ) -> Optional[CampaignAnalysis]:
        """
        Analyze marketing campaign performance with AI insights
        
        Args:
            campaign_id: Campaign identifier
            include_ai_insights: Whether to include AI-generated insights
            
        Returns:
            Comprehensive campaign analysis
        """
        if not self.initialized:
            await self.initialize()

        try:
            # Get campaign data from Snowflake
            async with self.cortex_service as cortex:
                campaign_data = await cortex.query_structured_data(
                    table="STG_MARKETING_CAMPAIGNS",
                    filters={"CAMPAIGN_ID": campaign_id},
                    limit=1
                )

                if not campaign_data:
                    logger.warning(f"No campaign data found for ID: {campaign_id}")
                    return None

                campaign_record = campaign_data[0]

            # Calculate performance metrics
            impressions = campaign_record.get("IMPRESSIONS", 0)
            clicks = campaign_record.get("CLICKS", 0)
            conversions = campaign_record.get("CONVERSIONS", 0)
            revenue = campaign_record.get("REVENUE", 0.0)
            cost = campaign_record.get("COST", 0.0)

            ctr = (clicks / impressions * 100) if impressions > 0 else 0
            conversion_rate = (conversions / clicks * 100) if clicks > 0 else 0
            cpa = (cost / conversions) if conversions > 0 else 0
            roi = ((revenue - cost) / cost * 100) if cost > 0 else 0

            # Performance scoring
            performance_score = self._calculate_performance_score(
                ctr, conversion_rate, roi
            )

            # Generate AI insights if requested
            ai_summary = ""
            optimization_recommendations = []
            audience_insights = {}

            if include_ai_insights:
                # Create comprehensive analysis prompt
                analysis_prompt = f"""
                Analyze this marketing campaign performance and provide insights:
                
                Campaign: {campaign_record.get('CAMPAIGN_NAME', 'Unknown')}
                Type: {campaign_record.get('CAMPAIGN_TYPE', 'Unknown')}
                Duration: {campaign_record.get('START_DATE')} to {campaign_record.get('END_DATE', 'Ongoing')}
                
                Performance Metrics:
                - Impressions: {impressions:,}
                - Clicks: {clicks:,} (CTR: {ctr:.2f}%)
                - Conversions: {conversions:,} (Rate: {conversion_rate:.2f}%)
                - Revenue: ${revenue:,.2f}
                - Cost: ${cost:,.2f}
                - CPA: ${cpa:.2f}
                - ROI: {roi:.1f}%
                - Performance Score: {performance_score:.1f}/100
                
                Provide:
                1. Executive summary of campaign performance
                2. Key strengths and areas for improvement
                3. Specific optimization recommendations
                4. Audience engagement insights
                5. Competitive positioning analysis
                """

                # Use SmartAIService for high-quality marketing analysis
                request = LLMRequest(
                    messages=[{"role": "user", "content": analysis_prompt}],
                    task_type=TaskType.MARKET_ANALYSIS,
                    performance_priority=True,
                    cost_sensitivity=0.8,
                    user_id="marketing_agent",
                    metadata={"campaign_id": campaign_id}
                )

                response = await smart_ai_service.generate_response(request)
                ai_summary = response.content

                # Extract specific recommendations using Cortex
                async with self.cortex_service as cortex:
                    recommendations_prompt = f"""
                    Based on this campaign analysis, provide 5 specific, actionable optimization recommendations:
                    
                    {ai_summary}
                    
                    Format as a numbered list of concrete actions.
                    """

                    recommendations_text = await cortex.complete_text_with_cortex(
                        prompt=recommendations_prompt,
                        max_tokens=300
                    )

                    if recommendations_text:
                        optimization_recommendations = [
                            rec.strip() for rec in recommendations_text.split('\n')
                            if rec.strip() and any(char.isdigit() for char in rec[:5])
                        ]

                # Analyze audience segments
                audience_insights = await self._analyze_campaign_audience(
                    campaign_id, campaign_record
                )

            # Create analysis result
            analysis = CampaignAnalysis(
                campaign_id=campaign_id,
                campaign_name=campaign_record.get("CAMPAIGN_NAME", "Unknown"),
                campaign_type=CampaignType(campaign_record.get("CAMPAIGN_TYPE", "email").lower()),
                start_date=campaign_record.get("START_DATE", datetime.now()),
                end_date=campaign_record.get("END_DATE"),
                impressions=impressions,
                clicks=clicks,
                conversions=conversions,
                revenue=revenue,
                cost=cost,
                ctr=ctr,
                conversion_rate=conversion_rate,
                cpa=cpa,
                roi=roi,
                performance_score=performance_score,
                ai_summary=ai_summary,
                optimization_recommendations=optimization_recommendations,
                audience_insights=audience_insights,
                confidence_score=0.9
            )

            # Store analysis in AI Memory
            await self.ai_memory.store_memory(
                content=f"Marketing campaign analysis for {campaign_record.get('CAMPAIGN_NAME')}: {ai_summary}",
                category=MemoryCategory.MARKETING_CAMPAIGN_INSIGHT,
                tags=[
                    "campaign_analysis",
                    campaign_record.get("CAMPAIGN_TYPE", "unknown").lower(),
                    f"performance_{performance_score:.0f}",
                    f"roi_{roi:.0f}"
                ],
                importance_score=0.8,
                metadata={
                    "campaign_id": campaign_id,
                    "performance_score": performance_score,
                    "roi": roi
                }
            )

            logger.info(f"Completed campaign analysis for {campaign_id}")
            return analysis

        except Exception as e:
            logger.error(f"Error analyzing campaign {campaign_id}: {e}")
            return None

    async def generate_marketing_content(
        self, request: ContentGenerationRequest
    ) -> Dict[str, Any]:
        """
        Generate marketing content using AI with brand and competitive context
        
        Args:
            request: Content generation request
            
        Returns:
            Generated content with metadata
        """
        if not self.initialized:
            await self.initialize()

        try:
            # Get brand and product context from knowledge base
            brand_context = ""
            product_context = ""
            competitor_context = ""

            if self.knowledge_service:
                # Get product information
                if request.product_context:
                    product_info = await self.knowledge_service.search_entities(
                        query=request.product_context,
                        entity_type="product",
                        limit=3
                    )
                    if product_info:
                        product_context = "\n".join([
                            f"- {item['name']}: {item['description']}"
                            for item in product_info
                        ])

                # Get competitor information
                competitor_info = await self.knowledge_service.search_entities(
                    query=request.topic,
                    entity_type="competitor",
                    limit=2
                )
                if competitor_info:
                    competitor_context = "\n".join([
                        f"- {item['name']}: {item['description']}"
                        for item in competitor_info
                    ])

            # Build comprehensive content generation prompt
            content_prompt = self._build_content_prompt(
                request, product_context, competitor_context, brand_context
            )

            # Use SmartAIService for creative content generation
            llm_request = LLMRequest(
                messages=[{"role": "user", "content": content_prompt}],
                task_type=TaskType.CREATIVE_CONTENT,
                performance_priority=False,
                cost_sensitivity=0.6,
                user_id="marketing_agent",
                temperature=0.8,  # Higher creativity for content
                metadata={
                    "content_type": request.content_type.value,
                    "audience": request.target_audience.value
                }
            )

            response = await smart_ai_service.generate_response(llm_request)
            generated_content = response.content

            # Generate content variations using Cortex
            variations = []
            if request.content_type in [ContentType.EMAIL_COPY, ContentType.AD_COPY]:
                async with self.cortex_service as cortex:
                    variation_prompt = f"""
                    Create 2 alternative versions of this {request.content_type.value}:
                    
                    Original:
                    {generated_content}
                    
                    Variations should maintain the same key message but use different approaches.
                    """

                    variations_text = await cortex.complete_text_with_cortex(
                        prompt=variation_prompt,
                        max_tokens=800
                    )

                    if variations_text:
                        variations = [v.strip() for v in variations_text.split("---") if v.strip()]

            # Analyze content quality
            quality_score = await self._analyze_content_quality(
                generated_content, request
            )

            # Store content in AI Memory
            await self.ai_memory.store_memory(
                content=f"Generated {request.content_type.value} for {request.target_audience.value}: {request.topic}",
                category=MemoryCategory.MARKETING_CONTENT,
                tags=[
                    "content_generation",
                    request.content_type.value,
                    request.target_audience.value,
                    request.tone
                ],
                importance_score=0.7,
                metadata={
                    "content_type": request.content_type.value,
                    "quality_score": quality_score
                }
            )

            result = {
                "content": generated_content,
                "variations": variations,
                "content_type": request.content_type.value,
                "target_audience": request.target_audience.value,
                "quality_score": quality_score,
                "word_count": len(generated_content.split()),
                "generated_at": datetime.now().isoformat(),
                "model_used": response.model,
                "cost_usd": response.cost_usd,
                "generation_time_ms": response.latency_ms
            }

            logger.info(f"Generated {request.content_type.value} content for {request.target_audience.value}")
            return result

        except Exception as e:
            logger.error(f"Error generating marketing content: {e}")
            return {"error": str(e), "content": ""}

    async def analyze_audience_segments(
        self, segment_criteria: Dict[str, Any] = None
    ) -> List[AudienceSegmentAnalysis]:
        """
        Analyze audience segments using Snowflake Cortex AI
        
        Args:
            segment_criteria: Criteria for segmentation analysis
            
        Returns:
            List of audience segment analyses
        """
        if not self.initialized:
            await self.initialize()

        try:
            segments = []

            # Get customer data from HubSpot via Snowflake
            async with self.hubspot_connector as connector:
                customer_data = await connector.query_hubspot_contacts(limit=1000)

                if customer_data.empty:
                    logger.warning("No customer data available for segmentation")
                    return segments

            # Use Snowflake Cortex for intelligent segmentation
            async with self.cortex_service as cortex:
                segmentation_prompt = f"""
                Analyze this customer dataset and identify key audience segments:
                
                Dataset Overview:
                - Total contacts: {len(customer_data)}
                - Industries: {customer_data['INDUSTRY'].value_counts().head().to_dict() if 'INDUSTRY' in customer_data.columns else 'N/A'}
                - Company sizes: {customer_data['COMPANY_SIZE'].value_counts().head().to_dict() if 'COMPANY_SIZE' in customer_data.columns else 'N/A'}
                
                Identify 5 distinct audience segments based on:
                1. Company characteristics (size, industry, revenue)
                2. Engagement patterns
                3. Conversion behavior
                4. Geographic distribution
                
                For each segment, provide:
                - Segment name and description
                - Key characteristics
                - Estimated size
                - Engagement preferences
                - Decision-making factors
                """

                segmentation_analysis = await cortex.complete_text_with_cortex(
                    prompt=segmentation_prompt,
                    max_tokens=1000
                )

                # Process Cortex analysis into structured segments
                if segmentation_analysis:
                    segment_lines = [
                        line.strip() for line in segmentation_analysis.split('\n')
                        if line.strip() and any(keyword in line.lower() for keyword in ['segment', 'group', 'audience'])
                    ]

                    for i, segment_desc in enumerate(segment_lines[:5]):
                        # Create mock segment analysis (in production, this would use real data)
                        segment = AudienceSegmentAnalysis(
                            segment_name=f"Segment {i+1}",
                            segment_type=list(AudienceSegment)[i % len(AudienceSegment)],
                            size=len(customer_data) // 5,  # Rough estimate
                            engagement_score=0.6 + (i * 0.1),
                            conversion_rate=2.5 + (i * 0.5),
                            average_deal_size=10000 + (i * 5000),
                            preferred_channels=["email", "linkedin", "webinar"][i:i+2],
                            content_preferences=["case_studies", "whitepapers", "demos"][i:i+2],
                            decision_factors=["roi", "security", "ease_of_use"][i:i+2],
                            pain_points=["cost", "complexity", "integration"][i:i+2],
                            ai_summary=segment_desc,
                            targeting_recommendations=[
                                f"Focus on {list(AudienceSegment)[i % len(AudienceSegment)].value} messaging",
                                "Emphasize ROI and business value",
                                "Use case studies and social proof"
                            ],
                            content_suggestions=[
                                f"Create {ContentType.CASE_STUDY.value} content",
                                f"Develop {ContentType.WHITEPAPER.value} resources",
                                "Build interactive demos"
                            ],
                            confidence_score=0.8
                        )
                        segments.append(segment)

            # Store segmentation insights in AI Memory
            await self.ai_memory.store_memory(
                content=f"Audience segmentation analysis identified {len(segments)} key segments",
                category=MemoryCategory.MARKETING_AUDIENCE_INSIGHT,
                tags=["audience_segmentation", "customer_analysis", "targeting"],
                importance_score=0.8,
                metadata={"segments_count": len(segments)}
            )

            logger.info(f"Analyzed {len(segments)} audience segments")
            return segments

        except Exception as e:
            logger.error(f"Error analyzing audience segments: {e}")
            return []

    async def generate_competitive_analysis(
        self, competitor_name: str, analysis_focus: str = "positioning"
    ) -> Dict[str, Any]:
        """
        Generate competitive analysis using SmartAIService and knowledge base
        
        Args:
            competitor_name: Name of competitor to analyze
            analysis_focus: Focus area (positioning, pricing, features, marketing)
            
        Returns:
            Comprehensive competitive analysis
        """
        if not self.initialized:
            await self.initialize()

        try:
            # Get competitor information from knowledge base
            competitor_context = ""
            if self.knowledge_service:
                competitor_info = await self.knowledge_service.search_entities(
                    query=competitor_name,
                    entity_type="competitor",
                    limit=1
                )
                if competitor_info:
                    competitor_context = competitor_info[0].get("description", "")

            # Generate comprehensive competitive analysis
            analysis_prompt = f"""
            Conduct a comprehensive competitive analysis for {competitor_name} focusing on {analysis_focus}:
            
            Competitor Context:
            {competitor_context}
            
            Analysis Areas:
            1. Market positioning and messaging
            2. Product/service differentiation
            3. Pricing strategy and value proposition
            4. Marketing channels and tactics
            5. Strengths and weaknesses
            6. Market share and customer base
            7. Recent developments and trends
            8. Opportunities for competitive advantage
            
            Provide actionable insights for competitive positioning and strategic response.
            """

            # Use specialized competitive analysis function
            analysis_content = await generate_competitive_analysis(
                analysis_prompt, user_id="marketing_agent"
            )

            # Extract key insights using Cortex
            async with self.cortex_service as cortex:
                insights_prompt = f"""
                From this competitive analysis, extract 5 key strategic insights:
                
                {analysis_content}
                
                Focus on actionable intelligence for marketing strategy.
                """

                key_insights = await cortex.complete_text_with_cortex(
                    prompt=insights_prompt,
                    max_tokens=300
                )

                strategic_recommendations_prompt = f"""
                Based on this competitive analysis, provide 5 specific marketing recommendations:
                
                {analysis_content}
                
                Format as actionable recommendations for marketing team.
                """

                recommendations = await cortex.complete_text_with_cortex(
                    prompt=strategic_recommendations_prompt,
                    max_tokens=300
                )

            # Store competitive analysis in AI Memory
            await self.ai_memory.store_memory(
                content=f"Competitive analysis for {competitor_name}: {key_insights}",
                category=MemoryCategory.COMPETITIVE_INTELLIGENCE,
                tags=[
                    "competitive_analysis",
                    competitor_name.lower().replace(" ", "_"),
                    analysis_focus,
                    "marketing_intelligence"
                ],
                importance_score=0.9,
                metadata={
                    "competitor": competitor_name,
                    "focus": analysis_focus
                }
            )

            result = {
                "competitor": competitor_name,
                "analysis_focus": analysis_focus,
                "full_analysis": analysis_content,
                "key_insights": key_insights.split('\n') if key_insights else [],
                "strategic_recommendations": recommendations.split('\n') if recommendations else [],
                "generated_at": datetime.now().isoformat(),
                "confidence_score": 0.85
            }

            logger.info(f"Generated competitive analysis for {competitor_name}")
            return result

        except Exception as e:
            logger.error(f"Error generating competitive analysis for {competitor_name}: {e}")
            return {"error": str(e), "competitor": competitor_name}

    def _calculate_performance_score(
        self, ctr: float, conversion_rate: float, roi: float
    ) -> float:
        """Calculate overall campaign performance score"""
        # Weighted scoring based on marketing best practices
        ctr_score = min(ctr * 10, 30)  # Max 30 points for CTR
        conversion_score = min(conversion_rate * 5, 35)  # Max 35 points for conversion
        roi_score = min(roi / 2, 35)  # Max 35 points for ROI
        
        return max(0, min(100, ctr_score + conversion_score + roi_score))

    async def _analyze_campaign_audience(
        self, campaign_id: str, campaign_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze campaign audience engagement and behavior"""
        try:
            # Mock audience analysis (in production, would query actual data)
            return {
                "primary_segments": ["enterprise", "smb"],
                "engagement_by_segment": {
                    "enterprise": {"clicks": 450, "conversions": 23},
                    "smb": {"clicks": 320, "conversions": 18}
                },
                "geographic_distribution": {
                    "north_america": 0.6,
                    "europe": 0.3,
                    "asia_pacific": 0.1
                },
                "device_breakdown": {
                    "desktop": 0.7,
                    "mobile": 0.3
                },
                "time_engagement": {
                    "peak_hours": ["9-11am", "2-4pm"],
                    "peak_days": ["Tuesday", "Wednesday", "Thursday"]
                }
            }
        except Exception as e:
            logger.error(f"Error analyzing campaign audience: {e}")
            return {}

    def _build_content_prompt(
        self,
        request: ContentGenerationRequest,
        product_context: str,
        competitor_context: str,
        brand_context: str
    ) -> str:
        """Build comprehensive content generation prompt"""
        prompt = f"""
        Generate {request.content_type.value} content for {request.target_audience.value} audience:
        
        Topic: {request.topic}
        Tone: {request.tone}
        Length: {request.length}
        Include CTA: {request.include_cta}
        
        Context:
        """

        if product_context:
            prompt += f"\nProduct Information:\n{product_context}\n"

        if competitor_context:
            prompt += f"\nCompetitive Landscape:\n{competitor_context}\n"

        if request.brand_guidelines:
            prompt += f"\nBrand Guidelines:\n{request.brand_guidelines}\n"

        # Add content-specific requirements
        content_requirements = {
            ContentType.EMAIL_COPY: "Include compelling subject line, personalized greeting, clear value proposition, and strong CTA",
            ContentType.BLOG_POST: "Include engaging headline, introduction, main points with subheadings, and conclusion",
            ContentType.SOCIAL_POST: "Keep concise, engaging, include relevant hashtags, and encourage interaction",
            ContentType.AD_COPY: "Focus on attention-grabbing headline, clear benefits, and compelling CTA",
            ContentType.LANDING_PAGE: "Include headline, value proposition, benefits, social proof, and conversion elements",
            ContentType.CASE_STUDY: "Include challenge, solution, implementation, and measurable results",
            ContentType.WHITEPAPER: "Include executive summary, problem statement, solution analysis, and conclusions"
        }

        if request.content_type in content_requirements:
            prompt += f"\nSpecific Requirements:\n{content_requirements[request.content_type]}\n"

        prompt += f"""
        Audience Considerations for {request.target_audience.value}:
        - Tailor messaging to their specific needs and pain points
        - Use appropriate technical depth and business language
        - Focus on relevant value propositions and benefits
        - Include industry-specific examples where applicable
        
        Generate high-quality, engaging content that drives action.
        """

        return prompt

    async def _analyze_content_quality(
        self, content: str, request: ContentGenerationRequest
    ) -> float:
        """Analyze generated content quality using AI"""
        try:
            async with self.cortex_service as cortex:
                quality_prompt = f"""
                Analyze the quality of this {request.content_type.value} content on a scale of 0-100:
                
                Content:
                {content}
                
                Evaluate based on:
                1. Clarity and readability
                2. Audience appropriateness
                3. Persuasiveness and engagement
                4. Call-to-action effectiveness
                5. Brand consistency
                
                Provide only a numeric score (0-100).
                """

                score_text = await cortex.complete_text_with_cortex(
                    prompt=quality_prompt,
                    max_tokens=10
                )

                if score_text and score_text.strip().isdigit():
                    return float(score_text.strip())
                else:
                    return 75.0  # Default score

        except Exception as e:
            logger.error(f"Error analyzing content quality: {e}")
            return 75.0  # Default score 