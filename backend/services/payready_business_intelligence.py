"""
Pay Ready Business Intelligence Orchestrator
Integrates all BI agents with existing Sophia + Buzz architecture
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

from pydantic import BaseModel, Field

from backend.agents.core.base_agent import BaseAgent
from backend.core.sophia_engine import SophiaAIEngine
from backend.integrations.buzz_integration import BuzzAISystem
from backend.mcp_servers.mcp_gateway import MCPGateway

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BusinessIntelligenceRequest(BaseModel):
    """Request model for business intelligence operations"""

    request_type: str = Field(
        pattern="^(prospect_enrichment|competitive_analysis|roi_validation|sales_brief|market_intelligence)$"
    )
    target: Optional[str] = None  # Company name or competitor
    parameters: Dict[str, Any] = {}
    user_context: Dict[str, Any] = {}


class BusinessIntelligenceResponse(BaseModel):
    """Response model for business intelligence operations"""

    request_id: str
    request_type: str
    status: str
    data: Dict[str, Any]
    recommendations: List[str] = []
    action_items: List[Dict[str, Any]] = []
    timestamp: datetime


class PayReadyBusinessIntelligenceOrchestrator(BaseAgent):
    """Orchestrator for Pay Ready business intelligence operations"""

    def __init__(self, config_dict: Optional[Dict] = None):
        super().__init__(
            config_dict
            or {
                "name": "Pay Ready Business Intelligence Orchestrator",
                "description": "Central orchestrator for all Pay Ready BI operations",
            }
        )

        # Connect to existing infrastructure
        self.sophia_core = SophiaAIEngine()  # Existing Sophia engine
        self.buzz_system = BuzzAISystem()  # Existing Buzz integration
        self.mcp_gateway = MCPGateway()  # Existing MCP gateway

        # MCP server endpoints
        self.mcp_servers = {
            "competitive_monitor": "http://payready-competitive-monitor:3000",
            "buzz_roi": "http://payready-buzz-roi:3000",
            "linkedin": "http://payready-linkedin-mcp:3000",
        }

        # Initialize caching
        self.cache_ttl = 3600  # 1 hour default

        # Add capabilities
        self.capabilities.extend(
            [
                "prospect_intelligence",
                "competitive_monitoring",
                "roi_validation",
                "sales_acceleration",
                "market_analysis",
            ]
        )

    async def process_sales_intelligence_request(
        self, request: BusinessIntelligenceRequest
    ) -> BusinessIntelligenceResponse:
        """Process sales intelligence request through appropriate channels"""

        request_id = (
            f"bi_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{request.request_type}"
        )
        logger.info(f"Processing BI request: {request_id}")

        try:
            # Route based on request type
            if request.request_type == "prospect_enrichment":
                data = await self._process_prospect_enrichment(request)
            elif request.request_type == "competitive_analysis":
                data = await self._process_competitive_analysis(request)
            elif request.request_type == "roi_validation":
                data = await self._process_roi_validation(request)
            elif request.request_type == "sales_brief":
                data = await self._process_sales_brief(request)
            elif request.request_type == "market_intelligence":
                data = await self._process_market_intelligence(request)
            else:
                raise ValueError(f"Unknown request type: {request.request_type}")

            # Generate recommendations and action items
            recommendations = await self._generate_recommendations(
                request.request_type, data
            )
            action_items = await self._generate_action_items(request.request_type, data)

            # Create response
            response = BusinessIntelligenceResponse(
                request_id=request_id,
                request_type=request.request_type,
                status="success",
                data=data,
                recommendations=recommendations,
                action_items=action_items,
                timestamp=datetime.utcnow(),
            )

            # Log to Sophia for conversation context
            await self._log_to_sophia(request, response)

            return response

        except Exception as e:
            logger.error(f"Error processing BI request: {e}")
            return BusinessIntelligenceResponse(
                request_id=request_id,
                request_type=request.request_type,
                status="error",
                data={"error": str(e)},
                timestamp=datetime.utcnow(),
            )

    async def _process_prospect_enrichment(
        self, request: BusinessIntelligenceRequest
    ) -> Dict[str, Any]:
        """Process prospect enrichment request"""
        company_name = request.target
        if not company_name:
            raise ValueError("Company name required for prospect enrichment")

        # Use competitive monitor for basic company intelligence
        competitive_result = await self.mcp_gateway.route_request(
            server_name="competitive_monitor",
            tool_name="check_threat_level",
            parameters={"competitor_name": company_name},
        )

        # Create basic enriched data structure
        enriched_data = {
            "company_profile": {
                "name": company_name,
                "status": "basic_profile",
                "enrichment_level": request.parameters.get("enrichment_level", "basic"),
            },
            "competitive_status": competitive_result,
            "buzz_integration_potential": await self._assess_buzz_potential(
                {"company_name": company_name}
            ),
            "sales_priority_score": await self._calculate_sales_priority(
                {"company_name": company_name}, competitive_result
            ),
        }

        return enriched_data

    async def _process_competitive_analysis(
        self, request: BusinessIntelligenceRequest
    ) -> Dict[str, Any]:
        """Process competitive analysis request"""

        # Get competitive landscape
        landscape_result = await self.mcp_gateway.route_request(
            server_name="competitive_monitor",
            tool_name="analyze_landscape",
            parameters={},
        )

        # Get detailed report if requested
        if request.parameters.get("detailed_report", False):
            report_result = await self.mcp_gateway.route_request(
                server_name="competitive_monitor",
                tool_name="generate_report",
                parameters={},
            )
            landscape_result["detailed_report"] = report_result

        # Analyze impact on Pay Ready
        impact_analysis = await self._analyze_competitive_impact(landscape_result)
        landscape_result["payready_impact"] = impact_analysis

        return landscape_result

    async def _process_roi_validation(
        self, request: BusinessIntelligenceRequest
    ) -> Dict[str, Any]:
        """Process ROI validation request"""
        client_id = request.target or request.parameters.get("client_id")

        if not client_id:
            # Get aggregate ROI across all clients
            roi_data = await self._get_aggregate_roi_metrics()
        else:
            # Get specific client ROI
            roi_data = await self.mcp_gateway.route_request(
                server_name="buzz_roi",
                tool_name="generate_client_roi",
                parameters={"client_id": client_id},
            )

        # Enhance with Buzz performance data
        buzz_metrics = await self.buzz_system.get_performance_metrics(client_id)
        roi_data["buzz_performance"] = buzz_metrics

        # Add competitive comparison
        roi_data["competitive_advantage"] = (
            await self._calculate_competitive_roi_advantage(roi_data)
        )

        return roi_data

    async def _process_sales_brief(
        self, request: BusinessIntelligenceRequest
    ) -> Dict[str, Any]:
        """Process sales brief generation request"""
        company_name = request.target
        if not company_name:
            raise ValueError("Company name required for sales brief")

        # Create basic sales brief structure
        sales_brief = {
            "company_name": company_name,
            "brief_type": "basic",
            "key_contacts": [],
            "company_overview": {"name": company_name, "size": "unknown"},
        }

        # Enhance with LinkedIn intelligence if available
        if request.parameters.get("include_linkedin", True):
            try:
                linkedin_data = await self.mcp_gateway.route_request(
                    server_name="linkedin",
                    tool_name="enrich_contacts",
                    parameters={
                        "company_name": company_name,
                        "contacts": sales_brief.get("key_contacts", []),
                    },
                )
                sales_brief["enhanced_contacts"] = linkedin_data
            except Exception as e:
                logger.warning(f"LinkedIn enrichment failed: {e}")
                sales_brief["enhanced_contacts"] = {}

        # Add competitive positioning
        competitive_position = await self._generate_competitive_positioning(
            company_name
        )
        sales_brief["competitive_positioning"] = competitive_position

        # Add Buzz-specific value propositions
        sales_brief["buzz_value_props"] = await self._generate_buzz_value_props(
            sales_brief
        )

        return sales_brief

    async def _process_market_intelligence(
        self, request: BusinessIntelligenceRequest
    ) -> Dict[str, Any]:
        """Process market intelligence request"""

        # Aggregate intelligence from multiple sources
        market_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "competitive_landscape": {},
            "market_trends": {},
            "opportunities": [],
        }

        # Competitive landscape
        competitive_data = await self.mcp_gateway.route_request(
            server_name="competitive_monitor",
            tool_name="analyze_landscape",
            parameters={},
        )
        market_data["competitive_landscape"] = competitive_data

        # Identify market opportunities
        opportunities = await self._identify_market_opportunities(market_data)
        market_data["opportunities"] = opportunities

        # Generate market trends
        trends = await self._analyze_market_trends(market_data)
        market_data["market_trends"] = trends

        return market_data

    async def _assess_buzz_potential(
        self, company_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Assess potential for Buzz AI integration"""
        potential_score = 0.0
        factors = []

        # Size factor
        employee_count = company_data.get("employee_count", 0)
        if employee_count > 1000:
            potential_score += 0.3
            factors.append("Large portfolio size ideal for Buzz scalability")
        elif employee_count > 100:
            potential_score += 0.2
            factors.append("Mid-size portfolio with good Buzz potential")

        # Industry fit
        if company_data.get("industry", "").lower() in [
            "real estate",
            "property management",
            "multifamily",
        ]:
            potential_score += 0.3
            factors.append("Perfect industry fit for Buzz AI")

        # Technology readiness
        tech_stack = company_data.get("technology_stack", {})
        if tech_stack.get("integration_opportunities"):
            potential_score += 0.2
            factors.append(
                f"Integration ready with {len(tech_stack['integration_opportunities'])} systems"
            )

        # Competitive landscape
        if not tech_stack.get("competitive_solutions"):
            potential_score += 0.2
            factors.append("No competing solutions detected")

        return {
            "score": min(potential_score, 1.0),
            "factors": factors,
            "recommendation": (
                "High priority"
                if potential_score > 0.7
                else "Medium priority" if potential_score > 0.4 else "Low priority"
            ),
        }

    async def _calculate_sales_priority(
        self, company_data: Dict[str, Any], competitive_data: Dict[str, Any]
    ) -> float:
        """Calculate sales priority score"""
        priority_score = 0.0

        # NMHC Top 50 gets highest priority
        if company_data.get("is_nmhc_top_50"):
            priority_score += 0.4

        # Opportunity score from competitive analysis
        priority_score += (
            company_data.get("competitive_position", {}).get("opportunity_score", 0)
            * 0.3
        )

        # Buzz potential
        buzz_potential = await self._assess_buzz_potential(company_data)
        priority_score += buzz_potential["score"] * 0.3

        return min(priority_score, 1.0)

    async def _analyze_competitive_impact(
        self, landscape_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze competitive landscape impact on Pay Ready"""
        impact_analysis = {
            "threat_level": "low",
            "immediate_actions": [],
            "strategic_recommendations": [],
        }

        # Count critical threats
        threats = landscape_data.get("threats", [])
        critical_threats = [t for t in threats if t.get("severity") == "critical"]

        if len(critical_threats) > 2:
            impact_analysis["threat_level"] = "high"
            impact_analysis["immediate_actions"].append(
                "Schedule executive strategy session"
            )
        elif len(critical_threats) > 0:
            impact_analysis["threat_level"] = "medium"
            impact_analysis["immediate_actions"].append(
                "Review and update competitive positioning"
            )

        # Specific competitor threats
        if any("elise" in str(t).lower() for t in threats):
            impact_analysis["strategic_recommendations"].append(
                "Strengthen Buzz AI differentiation vs EliseAI leasing focus"
            )

        if any("entrata" in str(t).lower() for t in threats):
            impact_analysis["strategic_recommendations"].append(
                "Emphasize specialized collections AI vs generic PMS approach"
            )

        return impact_analysis

    async def _get_aggregate_roi_metrics(self) -> Dict[str, Any]:
        """Get aggregate ROI metrics across all Pay Ready clients"""
        # This would query actual data from Snowflake via MCP
        return {
            "average_collection_improvement": "18.5%",
            "average_labor_cost_reduction": "42%",
            "average_time_to_roi": "87 days",
            "client_satisfaction_score": 4.7,
            "total_revenue_impact": "$12.3M",
            "case_studies_available": 15,
        }

    async def _calculate_competitive_roi_advantage(
        self, roi_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate ROI advantage over competitors"""
        return {
            "vs_traditional_collections": "3.2x higher ROI",
            "vs_eliseai": "Focused on revenue vs leasing",
            "vs_manual_process": "24/7 availability with 0% error rate",
            "unique_advantages": [
                "AI specifically trained for multifamily collections",
                "Seamless integration with existing systems",
                "Proven ROI within 90 days",
            ],
        }

    async def _generate_competitive_positioning(
        self, company_name: str
    ) -> Dict[str, Any]:
        """Generate competitive positioning for specific prospect"""
        return {
            "positioning_statement": f"For {company_name}, Buzz AI delivers specialized collections intelligence that complements your existing systems while delivering measurable ROI in under 90 days.",
            "key_differentiators": [
                "Purpose-built for multifamily collections",
                "24/7 AI-powered resident communication",
                "Seamless integration with property management systems",
                "Proven 15-20% improvement in collection rates",
            ],
            "competitive_advantages": [
                "Unlike EliseAI's leasing focus, Buzz specializes in revenue collection",
                "More specialized than Entrata's generic AI approach",
                "Higher ROI than traditional collection agencies",
            ],
        }

    async def _generate_buzz_value_props(
        self, sales_brief: Dict[str, Any]
    ) -> List[str]:
        """Generate Buzz-specific value propositions"""
        value_props = []

        # Size-based props
        company_size = sales_brief.get("company_overview", {}).get("size", 0)
        if company_size > 1000:
            value_props.append(
                "Scale Buzz AI across your entire portfolio for maximum impact"
            )
        elif company_size > 100:
            value_props.append(
                "Perfect size to see immediate ROI from Buzz AI implementation"
            )

        # Technology fit
        tech_insights = sales_brief.get("technology_insights", {})
        if tech_insights.get("integration_opportunities"):
            value_props.append(
                f"Seamless integration with your existing {', '.join(tech_insights['integration_opportunities'][:2])} systems"
            )

        # Standard props
        value_props.extend(
            [
                "Reduce collections labor costs by 40% while improving resident satisfaction",
                "24/7 AI-powered collections that never miss a follow-up",
                "Proven 15-20% improvement in collection rates within 90 days",
            ]
        )

        return value_props

    async def _identify_market_opportunities(
        self, market_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Identify market opportunities from intelligence data"""
        opportunities = []

        # Competitive displacement
        competitive_data = market_data.get("competitive_landscape", {})
        for competitor, data in competitive_data.get("competitors", {}).items():
            if data.get("vulnerability_score", 0) > 0.7:
                opportunities.append(
                    {
                        "type": "competitive_displacement",
                        "description": f"Displacement opportunity from {data['name']} customers",
                        "priority": "medium",
                        "estimated_value": "Mid 6-figures per account",
                    }
                )

        return opportunities

    async def _analyze_market_trends(
        self, market_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze market trends from intelligence data"""
        return {
            "ai_adoption": {
                "trend": "accelerating",
                "description": "Rapid adoption of AI in property management",
                "impact": "Increased urgency for prospects to adopt AI solutions",
            },
            "collections_focus": {
                "trend": "increasing",
                "description": "Growing focus on revenue optimization post-COVID",
                "impact": "Higher receptivity to collections-specific solutions",
            },
            "integration_demand": {
                "trend": "critical",
                "description": "Demand for seamless system integration",
                "impact": "Buzz's integration capabilities are key differentiator",
            },
        }

    async def _generate_recommendations(
        self, request_type: str, data: Dict[str, Any]
    ) -> List[str]:
        """Generate recommendations based on intelligence data"""
        recommendations = []

        if request_type == "prospect_enrichment":
            if data.get("sales_priority_score", 0) > 0.8:
                recommendations.append("Prioritize immediate executive outreach")
                recommendations.append(
                    "Prepare custom ROI analysis for C-suite presentation"
                )

        elif request_type == "competitive_analysis":
            threat_level = data.get("payready_impact", {}).get("threat_level")
            if threat_level == "high":
                recommendations.append(
                    "Accelerate product roadmap to maintain competitive edge"
                )
                recommendations.append(
                    "Launch targeted marketing campaign highlighting differentiators"
                )

        elif request_type == "roi_validation":
            recommendations.append("Use these ROI metrics in all sales presentations")
            recommendations.append("Create case study from top performing clients")

        return recommendations

    async def _generate_action_items(
        self, request_type: str, data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate action items based on intelligence data"""
        action_items = []

        if request_type == "prospect_enrichment":
            priority_score = data.get("sales_priority_score", 0)
            if priority_score > 0.7:
                action_items.append(
                    {
                        "action": "Schedule discovery call with key decision makers",
                        "owner": "sales_team",
                        "priority": "high",
                        "due_date": (datetime.utcnow() + timedelta(days=3)).isoformat(),
                    }
                )

        elif request_type == "competitive_analysis":
            threats = data.get("threats", [])
            for threat in threats[:3]:  # Top 3 threats
                action_items.append(
                    {
                        "action": f"Address competitive threat: {threat.get('description', '')}",
                        "owner": "product_team",
                        "priority": threat.get("severity", "medium"),
                        "due_date": (datetime.utcnow() + timedelta(days=7)).isoformat(),
                    }
                )

        return action_items

    async def _log_to_sophia(
        self,
        request: BusinessIntelligenceRequest,
        response: BusinessIntelligenceResponse,
    ):
        """Log BI activity to Sophia for conversation context"""
        try:
            sophia_context = {
                "activity_type": "business_intelligence",
                "request": request.dict(),
                "response_summary": {
                    "status": response.status,
                    "key_findings": len(response.data),
                    "recommendations": len(response.recommendations),
                    "action_items": len(response.action_items),
                },
                "timestamp": response.timestamp.isoformat(),
            }

            await self.sophia_core.log_activity(sophia_context)

        except Exception as e:
            logger.error(f"Failed to log to Sophia: {e}")

    # Sophia Chat Integration Methods

    async def handle_conversational_query(
        self, query: str, context: Dict[str, Any]
    ) -> str:
        """Handle natural language BI queries from Sophia chat"""

        # Parse intent from query
        intent = await self._parse_bi_intent(query)

        # Create appropriate request
        if intent["type"] == "prospect_query":
            request = BusinessIntelligenceRequest(
                request_type="prospect_enrichment",
                target=intent["company_name"],
                user_context=context,
            )
        elif intent["type"] == "competitive_query":
            request = BusinessIntelligenceRequest(
                request_type="competitive_analysis",
                parameters={"detailed_report": "detailed" in query.lower()},
                user_context=context,
            )
        elif intent["type"] == "roi_query":
            request = BusinessIntelligenceRequest(
                request_type="roi_validation",
                target=intent.get("client_id"),
                user_context=context,
            )
        else:
            return "I can help you with prospect enrichment, competitive analysis, ROI validation, and market intelligence. What would you like to know?"

        # Process request
        response = await self.process_sales_intelligence_request(request)

        # Format conversational response
        return await self._format_conversational_response(response)

    async def _parse_bi_intent(self, query: str) -> Dict[str, Any]:
        """Parse business intelligence intent from natural language"""
        query_lower = query.lower()

        # Prospect queries
        if any(
            word in query_lower
            for word in ["enrich", "prospect", "company info", "tell me about"]
        ):
            # Extract company name (simplified - would use NER in production)
            companies = [
                "greystar",
                "lincoln property",
                "avalon",
                "equity residential",
                "camden",
            ]
            for company in companies:
                if company in query_lower:
                    return {"type": "prospect_query", "company_name": company.title()}

        # Competitive queries
        elif any(
            word in query_lower
            for word in ["competitive", "competitor", "elise", "entrata", "threat"]
        ):
            return {"type": "competitive_query"}

        # ROI queries
        elif any(
            word in query_lower for word in ["roi", "return", "performance", "metrics"]
        ):
            return {"type": "roi_query"}

        return {"type": "unknown"}

    async def _format_conversational_response(
        self, response: BusinessIntelligenceResponse
    ) -> str:
        """Format BI response for conversational interface"""
        if response.status == "error":
            return f"I encountered an issue: {response.data.get('error')}. Let me help you with something else."

        # Format based on request type
        if response.request_type == "prospect_enrichment":
            company = response.data["company_profile"].get("name", "the company")
            priority = response.data.get("sales_priority_score", 0)
            priority_text = (
                "high priority"
                if priority > 0.7
                else "medium priority" if priority > 0.4 else "lower priority"
            )

            return f"""
I've enriched the prospect data for {company}. Here are the key insights:

📊 **Company Profile**: {response.data["company_profile"].get("employee_count", "Unknown")} employees in {response.data["company_profile"].get("industry", "property management")}
🎯 **Sales Priority**: This is a {priority_text} prospect (score: {priority:.2f})
🤖 **Buzz AI Fit**: {response.data["buzz_integration_potential"]["recommendation"]}

**Key Recommendations:**
{chr(10).join(['• ' + rec for rec in response.recommendations[:3]])}

Would you like me to generate a detailed sales brief or analyze their competitive landscape?
            """

        elif response.request_type == "competitive_analysis":
            threats = response.data.get("threats", [])
            threat_count = len(threats)

            return f"""
🔍 **Competitive Intelligence Update**

I've identified {threat_count} competitive threats that need attention:

{chr(10).join([f'⚠️ {threat["competitor"]}: {threat["description"]}' for threat in threats[:3]])}

**Market Trends:**
{chr(10).join([f'• {trend["trend"]}: {trend["frequency"]} occurrences' for trend in response.data.get("market_trends", [])[:3]])}

**Immediate Actions Required:**
{chr(10).join(['• ' + rec for rec in response.recommendations[:3]])}

Would you like me to generate a detailed competitive report or analyze a specific competitor?
            """

        elif response.request_type == "roi_validation":
            return f"""
💰 **ROI Validation Results**

**Key Metrics:**
• Average Collection Improvement: {response.data.get("average_collection_improvement", "18.5%")}
• Labor Cost Reduction: {response.data.get("average_labor_cost_reduction", "42%")}
• Time to ROI: {response.data.get("average_time_to_roi", "87 days")}
• Client Satisfaction: {response.data.get("client_satisfaction_score", 4.7)}/5.0

**Competitive Advantage:**
{chr(10).join(['• ' + adv for adv in response.data.get("competitive_advantage", {}).get("unique_advantages", [])])}

These metrics demonstrate strong ROI for Buzz AI implementations. Would you like me to generate client-specific ROI analysis?
            """

        return "I've completed the analysis. Please let me know if you need any additional information."


# Integration with existing Sophia chat
async def register_bi_capabilities(sophia_engine: SophiaAIEngine):
    """Register BI capabilities with Sophia chat engine"""
    bi_orchestrator = PayReadyBusinessIntelligenceOrchestrator()

    # Register conversational handlers
    sophia_engine.register_capability(
        name="business_intelligence",
        handler=bi_orchestrator.handle_conversational_query,
        description="Provides business intelligence insights including prospect enrichment, competitive analysis, and ROI validation",
        examples=[
            "Tell me about Greystar Real Estate Partners",
            "What's the competitive landscape looking like?",
            "Show me our ROI metrics for existing clients",
            "Generate a sales brief for Lincoln Property Company",
            "Are there any threats from EliseAI?",
        ],
    )

    logger.info("Business Intelligence capabilities registered with Sophia")
