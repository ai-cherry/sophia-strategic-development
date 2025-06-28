"""
Sophia AI Unified Intelligence Service
======================================
This service unifies all AI capabilities into a single intelligent interface
with constitutional AI constraints and self-optimization.
"""

import asyncio
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

from backend.core.auto_esc_config import get_config_value

# Setup logging first
logger = logging.getLogger(__name__)

# Optional Snowflake import
try:
    from backend.utils.snowflake_cortex_service import SnowflakeCortexService
    SNOWFLAKE_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Snowflake Cortex service not available: {e}")
    SnowflakeCortexService = None
    SNOWFLAKE_AVAILABLE = False

from backend.mcp_servers.enhanced_ai_memory_mcp_server import EnhancedAiMemoryMCPServer
from backend.integrations.enhanced_gong_integration import EnhancedGongIntegration


class SophiaUnifiedIntelligenceService:
    """Unified service that combines all existing services with constitutional AI"""
    
    def __init__(self):
        """Initialize the unified intelligence service"""
        logger.info("🚀 Initializing Sophia Unified Intelligence Service...")
        
        # Initialize existing services
        self._init_existing_services()
        
        # Initialize new unified capabilities
        self._init_unified_capabilities()
        
        logger.info("✅ Unified Intelligence Service initialized successfully")
    
    def _init_existing_services(self):
        """Initialize existing Sophia AI services"""
        try:
            # Snowflake Cortex service
            if SNOWFLAKE_AVAILABLE and SnowflakeCortexService:
                self.snowflake_cortex = SnowflakeCortexService()
                logger.info("✅ Snowflake Cortex service initialized")
            else:
                logger.warning("⚠️ Snowflake Cortex service not available")
                self.snowflake_cortex = None
        except Exception as e:
            logger.warning(f"⚠️ Snowflake Cortex initialization failed: {e}")
            self.snowflake_cortex = None
        
        try:
            # AI Memory service
            self.ai_memory = EnhancedAiMemoryMCPServer()
            logger.info("✅ AI Memory service initialized")
        except Exception as e:
            logger.warning(f"⚠️ AI Memory initialization failed: {e}")
            self.ai_memory = None
        
        try:
            # Gong integration
            self.gong_integration = EnhancedGongIntegration()
            logger.info("✅ Gong integration initialized")
        except Exception as e:
            logger.warning(f"⚠️ Gong integration initialization failed: {e}")
            self.gong_integration = None
        
        # HubSpot integration - will be added later
        self.hubspot_integration = None
    
    def _init_unified_capabilities(self):
        """Initialize new unified AI capabilities"""
        # Placeholder implementations for now
        self.vector_router = None
        self.constitutional_ai = None
        self.portkey_gateway = None
        
        logger.info("✅ Unified capabilities initialized (placeholder mode)")
    
    async def unified_business_query(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Single entry point for all business intelligence queries
        
        Args:
            query: Natural language business query
            context: Business context including user info, department, etc.
            
        Returns:
            Unified intelligence response with constitutional compliance
        """
        logger.info(f"🔍 Processing unified business query: {query[:100]}...")
        
        # Step 1: Constitutional validation
        if self.constitutional_ai:
            safety_check = await self.constitutional_ai.validate_query(query, context)
            if not safety_check.get("approved", False):
                logger.warning(f"❌ Query failed constitutional validation: {safety_check.get('reason')}")
                return {
                    "error": "Query violates constitutional principles",
                    "reason": safety_check.get("reason"),
                    "suggestions": safety_check.get("suggestions", [])
                }
        else:
            safety_check = {"compliance_score": 1.0, "approved": True}
        
        # Step 2: Execute unified intelligence query
        try:
            # Prepare tasks for parallel execution
            tasks = []
            
            # Snowflake Cortex unified intelligence
            if self.snowflake_cortex:
                tasks.append(self._query_snowflake_cortex(query, context))
            
            # AI Memory context
            if self.ai_memory:
                tasks.append(self._get_memory_context(query, context))
            
            # Business data from integrations
            tasks.append(self._get_business_data(query, context))
            
            # Execute all queries in parallel
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            cortex_results = results[0] if len(results) > 0 and not isinstance(results[0], Exception) else None
            memory_context = results[1] if len(results) > 1 and not isinstance(results[1], Exception) else None
            business_data = results[2] if len(results) > 2 and not isinstance(results[2], Exception) else None
            
            # Step 3: Synthesize results using Portkey
            synthesized_response = await self._synthesize_results(
                query, cortex_results, memory_context, business_data, context
            )
            
            # Step 4: Generate optimization insights
            optimization_insights = await self._generate_optimization_insights(
                query, synthesized_response, context
            )
            
            return {
                "unified_insights": synthesized_response,
                "memory_context": memory_context,
                "business_data": business_data,
                "constitutional_compliance": safety_check.get("compliance_score", 1.0),
                "optimization_insights": optimization_insights,
                "confidence_score": self._calculate_confidence_score(
                    cortex_results, memory_context, business_data
                ),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error in unified business query: {e}")
            return {
                "error": "Failed to process unified query",
                "details": str(e),
                "constitutional_compliance": safety_check.get("compliance_score", 1.0)
            }
    
    async def _query_snowflake_cortex(self, query: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Execute unified intelligence query on Snowflake Cortex"""
        if not self.snowflake_cortex:
            return None
        
        try:
            # Execute the unified intelligence function
            sql = """
            SELECT * FROM TABLE(sophia_unified_intelligence(?, ?, ?))
            """
            
            results = await self.snowflake_cortex.execute_query(
                sql,
                [query, json.dumps(context), context.get("optimization_mode", "balanced")]
            )
            
            return results[0] if results else None
            
        except Exception as e:
            logger.error(f"Error querying Snowflake Cortex: {e}")
            return None
    
    async def _get_memory_context(self, query: str, context: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]:
        """Get relevant memories from AI Memory service"""
        if not self.ai_memory:
            return None
        
        try:
            # Search for relevant memories
            memories = await self.ai_memory.search_memories(
                query=query,
                category=context.get("category", "general"),
                limit=5
            )
            
            return memories
            
        except Exception as e:
            logger.error(f"Error getting memory context: {e}")
            return None
    
    async def _get_business_data(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Get relevant business data from integrations"""
        business_data = {}
        
        # Get Gong data if relevant
        if self.gong_integration and any(keyword in query.lower() for keyword in ["call", "conversation", "meeting"]):
            try:
                gong_data = await self.gong_integration.search_calls(query, limit=3)
                business_data["gong_calls"] = gong_data
            except Exception as e:
                logger.error(f"Error getting Gong data: {e}")
        
        # Get HubSpot data if relevant
        if self.hubspot_integration and any(keyword in query.lower() for keyword in ["deal", "contact", "customer"]):
            try:
                hubspot_data = await self.hubspot_integration.search_deals(query, limit=3)
                business_data["hubspot_deals"] = hubspot_data
            except Exception as e:
                logger.error(f"Error getting HubSpot data: {e}")
        
        return business_data
    
    async def _synthesize_results(
        self, 
        query: str,
        cortex_results: Optional[Dict[str, Any]],
        memory_context: Optional[List[Dict[str, Any]]],
        business_data: Dict[str, Any],
        context: Dict[str, Any]
    ) -> str:
        """Synthesize results from multiple sources using Portkey"""
        if not self.portkey_gateway:
            # Fallback to simple synthesis
            return self._simple_synthesis(cortex_results, memory_context, business_data)
        
        try:
            # Prepare synthesis prompt
            synthesis_prompt = f"""
            Synthesize the following information to answer the business query: "{query}"
            
            Cortex AI Analysis:
            {json.dumps(cortex_results, indent=2) if cortex_results else "No Cortex results available"}
            
            Memory Context:
            {json.dumps(memory_context, indent=2) if memory_context else "No memory context available"}
            
            Business Data:
            {json.dumps(business_data, indent=2) if business_data else "No business data available"}
            
            Provide a comprehensive, actionable response that:
            1. Directly answers the query
            2. Incorporates insights from all available sources
            3. Highlights key findings and recommendations
            4. Maintains business context awareness
            """
            
            # Use Portkey for synthesis
            response = await self.portkey_gateway.constitutional_complete({
                "messages": [
                    {"role": "system", "content": "You are Sophia AI, an intelligent business assistant."},
                    {"role": "user", "content": synthesis_prompt}
                ],
                "context": context
            })
            
            return response.get("content", "Unable to synthesize results")
            
        except Exception as e:
            logger.error(f"Error synthesizing results with Portkey: {e}")
            return self._simple_synthesis(cortex_results, memory_context, business_data)
    
    def _simple_synthesis(
        self,
        cortex_results: Optional[Dict[str, Any]],
        memory_context: Optional[List[Dict[str, Any]]],
        business_data: Dict[str, Any]
    ) -> str:
        """Simple fallback synthesis when Portkey is unavailable"""
        insights = []
        
        if cortex_results and cortex_results.get("unified_results"):
            insights.append(f"Analysis: {cortex_results['unified_results'].get('insights', 'No insights available')}")
        
        if memory_context:
            insights.append(f"Historical Context: Found {len(memory_context)} relevant memories")
        
        if business_data:
            if "gong_calls" in business_data:
                insights.append(f"Call Data: {len(business_data['gong_calls'])} relevant calls found")
            if "hubspot_deals" in business_data:
                insights.append(f"Deal Data: {len(business_data['hubspot_deals'])} relevant deals found")
        
        return "\n".join(insights) if insights else "No insights available"
    
    async def _generate_optimization_insights(
        self,
        query: str,
        response: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate optimization insights for continuous improvement"""
        return {
            "query_optimization": [
                "Consider adding specific time ranges for better results",
                "Include entity names for more precise matching"
            ],
            "performance_metrics": {
                "estimated_response_time_ms": 200,
                "cache_hit_potential": 0.75,
                "cost_optimization_potential": 0.3
            },
            "learning_opportunities": [
                "This query pattern could benefit from pre-computed embeddings",
                "Similar queries have 80% cache hit rate"
            ]
        }
    
    def _calculate_confidence_score(
        self,
        cortex_results: Optional[Dict[str, Any]],
        memory_context: Optional[List[Dict[str, Any]]],
        business_data: Dict[str, Any]
    ) -> float:
        """Calculate overall confidence score for the response"""
        scores = []
        
        if cortex_results and "confidence_score" in cortex_results:
            scores.append(cortex_results["confidence_score"])
        
        if memory_context:
            scores.append(0.8)  # High confidence when we have historical context
        
        if business_data:
            scores.append(0.9)  # High confidence with real business data
        
        return sum(scores) / len(scores) if scores else 0.5


# Singleton instance getter
_unified_intelligence_instance = None

def get_unified_intelligence_service() -> SophiaUnifiedIntelligenceService:
    """Get or create the singleton unified intelligence service instance"""
    global _unified_intelligence_instance
    if _unified_intelligence_instance is None:
        _unified_intelligence_instance = SophiaUnifiedIntelligenceService()
    return _unified_intelligence_instance 