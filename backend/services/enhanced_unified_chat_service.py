"""
Enhanced Unified Chat Service
Advanced natural language processing for CEO dashboard with multi-domain intelligence
"""

import asyncio
import json
import logging
import re
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import time

# Core imports
from backend.core.auto_esc_config import get_config_value
from backend.utils.snowflake_cortex_service import SnowflakeCortexService
from backend.utils.snowflake_hubspot_connector import SnowflakeHubSpotConnector
from backend.utils.snowflake_gong_connector import SnowflakeGongConnector
from backend.mcp.ai_memory_mcp_server import EnhancedAiMemoryMCPServer
from backend.workflows.langgraph_agent_orchestration import (
    LangGraphWorkflowOrchestrator,
)

logger = logging.getLogger(__name__)


class QueryIntent(Enum):
    """Types of user query intents"""

    SALES_PERFORMANCE = "sales_performance"
    DEAL_ANALYSIS = "deal_analysis"
    CALL_INSIGHTS = "call_insights"
    REVENUE_METRICS = "revenue_metrics"
    TEAM_PERFORMANCE = "team_performance"
    CUSTOMER_HEALTH = "customer_health"
    PIPELINE_STATUS = "pipeline_status"
    COMPETITIVE_INTELLIGENCE = "competitive_intelligence"
    TREND_ANALYSIS = "trend_analysis"
    EXECUTIVE_SUMMARY = "executive_summary"
    PREDICTIVE_INSIGHTS = "predictive_insights"
    ACTION_ITEMS = "action_items"
    SNOWFLAKE_ADMIN = "snowflake_admin"
    # New KB management intents
    KB_ADD_ENTITY = "kb_add_entity"
    KB_UPDATE_ENTITY = "kb_update_entity"
    KB_DELETE_ENTITY = "kb_delete_entity"
    KB_ADD_ARTICLE = "kb_add_article"
    KB_UPDATE_ARTICLE = "kb_update_article"
    KB_SEARCH_KNOWLEDGE = "kb_search_knowledge"
    KB_UPLOAD_DOCUMENT = "kb_upload_document"
    KB_MANAGE_CATEGORY = "kb_manage_category"
    # Enhanced Gong-specific intents
    GONG_CALL_SEARCH = "gong_call_search"
    GONG_TRANSCRIPT_SEARCH = "gong_transcript_search"
    GONG_ACCOUNT_INSIGHTS = "gong_account_insights"
    GONG_SENTIMENT_ANALYSIS = "gong_sentiment_analysis"
    GONG_TOPIC_ANALYSIS = "gong_topic_analysis"
    GONG_COACHING_INSIGHTS = "gong_coaching_insights"


class QueryComplexity(Enum):
    """Complexity levels for query processing"""

    SIMPLE = "simple"  # Single metric, direct query
    MODERATE = "moderate"  # Multiple metrics, some analysis
    COMPLEX = "complex"  # Cross-domain analysis, aggregation
    ADVANCED = "advanced"  # Predictive analysis, deep insights


@dataclass
class QueryContext:
    """Context information for query processing"""

    user_role: str = "ceo"
    time_period: Optional[str] = None
    specific_entities: List[str] = field(default_factory=list)
    filters: Dict[str, Any] = field(default_factory=dict)
    preferred_format: str = "executive_summary"
    urgency_level: str = "normal"


@dataclass
class ProcessedQuery:
    """Processed and analyzed query"""

    original_query: str
    intent: QueryIntent
    complexity: QueryComplexity
    context: QueryContext
    entities: List[str]
    metrics_requested: List[str]
    time_filters: Dict[str, Any]
    confidence: float
    processing_plan: List[str]


@dataclass
class QueryResponse:
    """Structured response to user query"""

    query: str
    intent: QueryIntent
    executive_summary: str
    key_metrics: Dict[str, Any]
    insights: List[str]
    recommendations: List[str]
    data_sources: List[str]
    confidence: float
    processing_time: float
    follow_up_questions: List[str]
    visualizations: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class KBEntity:
    """Knowledge Base entity structure"""

    entity_type: str  # 'employee', 'customer', 'product', 'competitor', etc.
    entity_id: Optional[str] = None
    attributes: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class KBArticle:
    """Knowledge Base article structure"""

    title: str
    content: str
    category: str
    tags: List[str] = field(default_factory=list)
    article_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class IntentClassifier:
    """Advanced intent classification for CEO queries"""

    def __init__(self):
        self.intent_patterns = self._initialize_intent_patterns()
        self.openai_client = None
        self.initialized = False

    async def initialize(self):
        """Initialize OpenAI client for advanced intent classification"""
        if self.initialized:
            return

        try:
            import openai

            api_key = await get_config_value("openai_api_key")
            if api_key:
                self.openai_client = openai.AsyncOpenAI(api_key=api_key)
                logger.info("✅ Intent Classifier initialized with OpenAI")
            else:
                logger.warning(
                    "OpenAI API key not available, using pattern-based classification only"
                )

            self.initialized = True

        except Exception as e:
            logger.error(f"Failed to initialize Intent Classifier: {e}")
            self.initialized = True

    def _initialize_intent_patterns(self) -> Dict[QueryIntent, Dict[str, Any]]:
        """Initialize patterns for intent classification"""
        return {
            QueryIntent.SALES_PERFORMANCE: {
                "keywords": [
                    "sales",
                    "performance",
                    "quota",
                    "target",
                    "achievement",
                    "revenue",
                ],
                "phrases": [
                    "how are sales",
                    "sales performance",
                    "revenue numbers",
                    "quota attainment",
                ],
                "entities": ["sales_rep", "team", "region", "product"],
                "complexity_indicators": ["trend", "comparison", "forecast"],
            },
            QueryIntent.DEAL_ANALYSIS: {
                "keywords": ["deal", "opportunity", "proposal", "contract", "close"],
                "phrases": [
                    "deal status",
                    "opportunity analysis",
                    "close rate",
                    "deal health",
                ],
                "entities": ["deal_id", "company", "amount", "stage"],
                "complexity_indicators": ["risk", "probability", "forecast"],
            },
            QueryIntent.CALL_INSIGHTS: {
                "keywords": ["call", "conversation", "meeting", "discussion", "talk"],
                "phrases": [
                    "call analysis",
                    "conversation insights",
                    "meeting outcomes",
                    "call sentiment",
                ],
                "entities": ["customer", "prospect", "sales_rep", "topic"],
                "complexity_indicators": ["sentiment", "topics", "coaching"],
            },
            QueryIntent.REVENUE_METRICS: {
                "keywords": [
                    "revenue",
                    "income",
                    "earnings",
                    "financial",
                    "money",
                    "dollars",
                ],
                "phrases": [
                    "revenue growth",
                    "financial performance",
                    "earnings report",
                    "revenue forecast",
                ],
                "entities": ["period", "segment", "product", "region"],
                "complexity_indicators": ["growth", "forecast", "trend", "comparison"],
            },
            QueryIntent.TEAM_PERFORMANCE: {
                "keywords": [
                    "team",
                    "rep",
                    "salesperson",
                    "performance",
                    "productivity",
                ],
                "phrases": [
                    "team performance",
                    "rep productivity",
                    "sales team",
                    "individual performance",
                ],
                "entities": ["team_member", "manager", "region", "role"],
                "complexity_indicators": ["ranking", "improvement", "coaching"],
            },
            QueryIntent.CUSTOMER_HEALTH: {
                "keywords": [
                    "customer",
                    "client",
                    "account",
                    "health",
                    "satisfaction",
                    "retention",
                ],
                "phrases": [
                    "customer health",
                    "account status",
                    "client satisfaction",
                    "retention risk",
                ],
                "entities": ["customer", "account", "segment", "value"],
                "complexity_indicators": ["risk", "churn", "expansion"],
            },
            QueryIntent.PIPELINE_STATUS: {
                "keywords": ["pipeline", "funnel", "stage", "progress", "flow"],
                "phrases": [
                    "pipeline status",
                    "sales funnel",
                    "deal flow",
                    "stage progression",
                ],
                "entities": ["stage", "period", "team", "product"],
                "complexity_indicators": ["velocity", "conversion", "bottleneck"],
            },
            QueryIntent.EXECUTIVE_SUMMARY: {
                "keywords": [
                    "summary",
                    "overview",
                    "dashboard",
                    "status",
                    "update",
                    "report",
                ],
                "phrases": [
                    "executive summary",
                    "overall status",
                    "high level",
                    "business overview",
                ],
                "entities": ["period", "metric", "kpi"],
                "complexity_indicators": ["comprehensive", "detailed", "complete"],
            },
            QueryIntent.TREND_ANALYSIS: {
                "keywords": ["trend", "pattern", "direction", "movement", "change"],
                "phrases": [
                    "trending",
                    "pattern analysis",
                    "trend direction",
                    "what's changing",
                ],
                "entities": ["metric", "period", "segment"],
                "complexity_indicators": ["forecast", "prediction", "correlation"],
            },
            QueryIntent.PREDICTIVE_INSIGHTS: {
                "keywords": ["predict", "forecast", "future", "projection", "estimate"],
                "phrases": [
                    "what will happen",
                    "forecast",
                    "prediction",
                    "future outlook",
                ],
                "entities": ["metric", "period", "scenario"],
                "complexity_indicators": ["model", "probability", "scenario"],
            },
            # Knowledge Base Management Intents
            QueryIntent.KB_ADD_ENTITY: {
                "keywords": [
                    "add",
                    "create",
                    "new",
                    "employee",
                    "customer",
                    "product",
                    "competitor",
                ],
                "phrases": [
                    "add employee",
                    "create customer",
                    "new product",
                    "define competitor",
                ],
                "entities": [
                    "name",
                    "email",
                    "department",
                    "skills",
                    "company",
                    "description",
                ],
                "complexity_indicators": ["attributes", "metadata", "properties"],
            },
            QueryIntent.KB_UPDATE_ENTITY: {
                "keywords": [
                    "update",
                    "modify",
                    "change",
                    "edit",
                    "employee",
                    "customer",
                    "product",
                ],
                "phrases": [
                    "update employee",
                    "modify customer",
                    "change product",
                    "edit competitor",
                ],
                "entities": ["id", "name", "attribute", "value"],
                "complexity_indicators": ["multiple", "batch", "bulk"],
            },
            QueryIntent.KB_ADD_ARTICLE: {
                "keywords": [
                    "add",
                    "create",
                    "write",
                    "article",
                    "knowledge",
                    "document",
                    "content",
                ],
                "phrases": [
                    "add article",
                    "create knowledge",
                    "write document",
                    "new content",
                ],
                "entities": ["title", "category", "content", "tags"],
                "complexity_indicators": ["detailed", "comprehensive", "structured"],
            },
            QueryIntent.KB_SEARCH_KNOWLEDGE: {
                "keywords": [
                    "search",
                    "find",
                    "lookup",
                    "knowledge",
                    "who",
                    "what",
                    "where",
                ],
                "phrases": [
                    "search for",
                    "find information",
                    "lookup knowledge",
                    "who knows",
                ],
                "entities": ["topic", "person", "skill", "expertise"],
                "complexity_indicators": ["semantic", "related", "similar"],
            },
            QueryIntent.KB_UPLOAD_DOCUMENT: {
                "keywords": [
                    "upload",
                    "import",
                    "load",
                    "document",
                    "file",
                    "pdf",
                    "docx",
                ],
                "phrases": [
                    "upload document",
                    "import file",
                    "load content",
                    "process document",
                ],
                "entities": ["file", "document", "content", "type"],
                "complexity_indicators": ["extract", "parse", "process"],
            },
        }

    async def classify_intent(
        self, query: str, context: Optional[QueryContext] = None
    ) -> Tuple[QueryIntent, float]:
        """
        Classify user query intent with confidence score

        Args:
            query: User query text
            context: Optional query context

        Returns:
            Tuple of (intent, confidence_score)
        """
        if not self.initialized:
            await self.initialize()

        # Pattern-based classification
        pattern_intent, pattern_confidence = self._classify_with_patterns(query)

        # AI-enhanced classification if available
        if self.openai_client:
            ai_intent, ai_confidence = await self._classify_with_ai(query, context)

            # Combine results (AI gets higher weight if confidence is high)
            if ai_confidence > 0.8:
                return ai_intent, ai_confidence
            elif pattern_confidence > 0.7:
                return pattern_intent, pattern_confidence
            else:
                # Average the confidences, prefer AI if close
                if ai_confidence >= pattern_confidence - 0.1:
                    return ai_intent, (ai_confidence + pattern_confidence) / 2
                else:
                    return pattern_intent, (ai_confidence + pattern_confidence) / 2

        return pattern_intent, pattern_confidence

    def _classify_with_patterns(self, query: str) -> Tuple[QueryIntent, float]:
        """Pattern-based intent classification"""
        query_lower = query.lower()
        intent_scores = {}

        for intent, patterns in self.intent_patterns.items():
            score = 0.0

            # Check keywords
            for keyword in patterns["keywords"]:
                if keyword in query_lower:
                    score += 0.1

            # Check phrases (higher weight)
            for phrase in patterns["phrases"]:
                if phrase in query_lower:
                    score += 0.3

            # Check complexity indicators
            for indicator in patterns.get("complexity_indicators", []):
                if indicator in query_lower:
                    score += 0.05

            intent_scores[intent] = score

        # Get best match
        if intent_scores:
            best_intent = max(intent_scores.items(), key=lambda x: x[1])
            return best_intent[0], min(best_intent[1], 1.0)

        # Default fallback
        return QueryIntent.EXECUTIVE_SUMMARY, 0.3

    async def _classify_with_ai(
        self, query: str, context: Optional[QueryContext] = None
    ) -> Tuple[QueryIntent, float]:
        """AI-enhanced intent classification"""
        try:
            context_info = ""
            if context:
                context_info = f"\nUser context: Role={context.user_role}, Format preference={context.preferred_format}"

            prompt = f"""
            Classify this CEO/executive query into the most appropriate intent category:
            
            Query: "{query}"
            {context_info}
            
            Available intent categories:
            - sales_performance: Sales metrics, quota attainment, team performance
            - deal_analysis: Specific deal insights, opportunity analysis
            - call_insights: Call analysis, conversation insights, customer interactions
            - revenue_metrics: Revenue, financial performance, earnings
            - team_performance: Individual/team productivity and performance
            - customer_health: Customer satisfaction, retention, account health
            - pipeline_status: Sales pipeline, funnel analysis, deal flow
            - competitive_intelligence: Competitor analysis, market insights
            - trend_analysis: Patterns, trends, directional analysis
            - executive_summary: High-level overview, dashboard summary
            - predictive_insights: Forecasting, predictions, future outlook
            - action_items: Tasks, recommendations, next steps
            
            Respond with JSON:
            {{
                "intent": "intent_category",
                "confidence": 0.95,
                "reasoning": "brief explanation"
            }}
            """

            response = await self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=200,
            )

            result = json.loads(response.choices[0].message.content)
            intent_str = result.get("intent", "executive_summary")
            confidence = float(result.get("confidence", 0.5))

            # Map string to enum
            intent_mapping = {intent.value: intent for intent in QueryIntent}
            intent = intent_mapping.get(intent_str, QueryIntent.EXECUTIVE_SUMMARY)

            return intent, confidence

        except Exception as e:
            logger.error(f"AI intent classification failed: {e}")
            return QueryIntent.EXECUTIVE_SUMMARY, 0.3


class QueryProcessor:
    """Advanced query processing and analysis"""

    def __init__(self):
        self.intent_classifier = IntentClassifier()
        self.entity_patterns = self._initialize_entity_patterns()
        self.time_patterns = self._initialize_time_patterns()

    async def initialize(self):
        """Initialize query processor"""
        await self.intent_classifier.initialize()

    def _initialize_entity_patterns(self) -> Dict[str, str]:
        """Initialize entity extraction patterns"""
        return {
            "deal_id": r"deal[_\s]*(?:id|#)?\s*:?\s*([A-Za-z0-9\-_]+)",
            "company": r"(?:company|client|account)\s+([A-Za-z\s&]+)",
            "sales_rep": r"(?:rep|salesperson|sales\s+rep)\s+([A-Za-z\s]+)",
            "amount": r"\$?([\d,]+(?:\.\d{2})?)[kKmMbB]?",
            "percentage": r"(\d+(?:\.\d+)?)%",
            "date_range": r"(?:last|past|previous)\s+(\d+)\s+(day|week|month|quarter|year)s?",
            "specific_date": r"(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})",
            "team": r"(?:team|group|division)\s+([A-Za-z\s]+)",
            "product": r"(?:product|solution|service)\s+([A-Za-z\s]+)",
        }

    def _initialize_time_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize time period patterns"""
        return {
            "today": {"days": 1, "type": "current"},
            "yesterday": {"days": 1, "type": "previous"},
            "this week": {"days": 7, "type": "current"},
            "last week": {"days": 7, "type": "previous"},
            "this month": {"days": 30, "type": "current"},
            "last month": {"days": 30, "type": "previous"},
            "this quarter": {"days": 90, "type": "current"},
            "last quarter": {"days": 90, "type": "previous"},
            "this year": {"days": 365, "type": "current"},
            "last year": {"days": 365, "type": "previous"},
            "ytd": {"days": 365, "type": "year_to_date"},
            "year to date": {"days": 365, "type": "year_to_date"},
        }

    async def process_query(
        self, query: str, context: Optional[QueryContext] = None
    ) -> ProcessedQuery:
        """
        Process and analyze user query

        Args:
            query: User query text
            context: Optional query context

        Returns:
            Processed query with intent, entities, and processing plan
        """
        if not context:
            context = QueryContext()

        # Classify intent
        intent, confidence = await self.intent_classifier.classify_intent(
            query, context
        )

        # Extract entities
        entities = self._extract_entities(query)

        # Extract time filters
        time_filters = self._extract_time_filters(query)

        # Determine complexity
        complexity = self._determine_complexity(query, intent, entities)

        # Extract requested metrics
        metrics = self._extract_metrics(query, intent)

        # Create processing plan
        processing_plan = self._create_processing_plan(
            intent, complexity, entities, metrics
        )

        return ProcessedQuery(
            original_query=query,
            intent=intent,
            complexity=complexity,
            context=context,
            entities=entities,
            metrics_requested=metrics,
            time_filters=time_filters,
            confidence=confidence,
            processing_plan=processing_plan,
        )

    def _extract_entities(self, query: str) -> List[str]:
        """Extract named entities from query"""
        entities = []

        for entity_type, pattern in self.entity_patterns.items():
            matches = re.findall(pattern, query, re.IGNORECASE)
            for match in matches:
                entities.append(f"{entity_type}:{match}")

        return entities

    def _extract_time_filters(self, query: str) -> Dict[str, Any]:
        """Extract time-related filters from query"""
        query_lower = query.lower()
        time_filters = {}

        # Check for predefined time periods
        for period, config in self.time_patterns.items():
            if period in query_lower:
                time_filters["period"] = period
                time_filters["days"] = config["days"]
                time_filters["type"] = config["type"]
                break

        # Check for specific date ranges
        date_match = re.search(r"from\s+([^\s]+)\s+to\s+([^\s]+)", query_lower)
        if date_match:
            time_filters["start_date"] = date_match.group(1)
            time_filters["end_date"] = date_match.group(2)
            time_filters["type"] = "custom_range"

        return time_filters

    def _determine_complexity(
        self, query: str, intent: QueryIntent, entities: List[str]
    ) -> QueryComplexity:
        """Determine query complexity level"""
        complexity_indicators = {
            "simple": 0,
            "moderate": 0,
            "complex": 0,
            "advanced": 0,
        }

        # Length-based complexity
        word_count = len(query.split())
        if word_count > 20:
            complexity_indicators["complex"] += 1
        elif word_count > 10:
            complexity_indicators["moderate"] += 1
        else:
            complexity_indicators["simple"] += 1

        # Entity-based complexity
        if len(entities) > 5:
            complexity_indicators["complex"] += 1
        elif len(entities) > 2:
            complexity_indicators["moderate"] += 1

        # Intent-based complexity
        complex_intents = [
            QueryIntent.PREDICTIVE_INSIGHTS,
            QueryIntent.TREND_ANALYSIS,
            QueryIntent.COMPETITIVE_INTELLIGENCE,
        ]
        if intent in complex_intents:
            complexity_indicators["advanced"] += 2

        # Keyword-based complexity
        complex_keywords = [
            "forecast",
            "predict",
            "correlation",
            "trend",
            "pattern",
            "compare",
            "analyze",
        ]
        for keyword in complex_keywords:
            if keyword in query.lower():
                complexity_indicators["complex"] += 1

        # Advanced keywords
        advanced_keywords = [
            "machine learning",
            "ai",
            "model",
            "algorithm",
            "statistical",
        ]
        for keyword in advanced_keywords:
            if keyword in query.lower():
                complexity_indicators["advanced"] += 2

        # Determine final complexity
        max_complexity = max(complexity_indicators.items(), key=lambda x: x[1])
        return QueryComplexity(max_complexity[0])

    def _extract_metrics(self, query: str, intent: QueryIntent) -> List[str]:
        """Extract requested metrics from query"""
        query_lower = query.lower()
        metrics = []

        # Intent-based default metrics
        intent_metrics = {
            QueryIntent.SALES_PERFORMANCE: [
                "revenue",
                "quota_attainment",
                "deals_closed",
            ],
            QueryIntent.DEAL_ANALYSIS: [
                "deal_value",
                "close_probability",
                "deal_stage",
            ],
            QueryIntent.CALL_INSIGHTS: ["call_sentiment", "talk_ratio", "call_outcome"],
            QueryIntent.REVENUE_METRICS: ["revenue", "growth_rate", "forecast"],
            QueryIntent.TEAM_PERFORMANCE: [
                "individual_performance",
                "team_ranking",
                "productivity",
            ],
            QueryIntent.CUSTOMER_HEALTH: [
                "satisfaction_score",
                "retention_rate",
                "expansion_revenue",
            ],
            QueryIntent.PIPELINE_STATUS: [
                "pipeline_value",
                "conversion_rate",
                "velocity",
            ],
        }

        metrics.extend(intent_metrics.get(intent, []))

        # Explicit metric mentions
        metric_keywords = {
            "revenue": ["revenue", "sales", "income"],
            "deals": ["deals", "opportunities", "contracts"],
            "calls": ["calls", "meetings", "conversations"],
            "customers": ["customers", "clients", "accounts"],
            "performance": ["performance", "productivity", "results"],
            "growth": ["growth", "increase", "improvement"],
            "forecast": ["forecast", "prediction", "projection"],
        }

        for metric, keywords in metric_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                if metric not in metrics:
                    metrics.append(metric)

        return metrics[:10]  # Limit to 10 metrics

    def _create_processing_plan(
        self,
        intent: QueryIntent,
        complexity: QueryComplexity,
        entities: List[str],
        metrics: List[str],
    ) -> List[str]:
        """Create step-by-step processing plan"""
        plan = []

        # Basic data retrieval
        if intent in [QueryIntent.SALES_PERFORMANCE, QueryIntent.REVENUE_METRICS]:
            plan.append("Retrieve HubSpot sales data")

        if intent in [QueryIntent.CALL_INSIGHTS, QueryIntent.CUSTOMER_HEALTH]:
            plan.append("Retrieve Gong call data")

        if intent == QueryIntent.DEAL_ANALYSIS:
            plan.append("Retrieve specific deal information")
            plan.append("Analyze deal progression and health")

        # Analysis steps based on complexity
        if complexity in [QueryComplexity.MODERATE, QueryComplexity.COMPLEX]:
            plan.append("Perform cross-domain data analysis")
            plan.append("Calculate derived metrics and KPIs")

        if complexity in [QueryComplexity.COMPLEX, QueryComplexity.ADVANCED]:
            plan.append("Apply statistical analysis and trend detection")
            plan.append("Generate predictive insights")

        # AI enhancement
        plan.append("Generate AI-powered insights using Snowflake Cortex")
        plan.append("Create executive summary and recommendations")

        return plan

    # Enhanced Gong call search patterns
    gong_call_patterns = [
        r"(?:search|find|show|get).*(?:gong|call|conversation).*(?:about|for|with).*([^.?!]+)",
        r"(?:calls|conversations).*(?:about|regarding|with).*([^.?!]+)",
        r"(?:gong|call).*(?:data|insights|analysis).*([^.?!]+)",
        r"(?:show|find).*(?:calls|meetings).*(?:sentiment|positive|negative)",
        r"(?:recent|latest).*(?:calls|gong).*(?:data|insights)"
    ]
    
    gong_transcript_patterns = [
        r"(?:search|find).*(?:transcript|conversation|discussion).*([^.?!]+)",
        r"(?:what.*said|who.*mentioned).*([^.?!]+)",
        r"(?:transcript|conversation).*(?:about|regarding).*([^.?!]+)",
        r"(?:find|search).*(?:speaker|participant).*([^.?!]+)"
    ]
    
    gong_account_patterns = [
        r"(?:account|customer|client).*([A-Za-z][A-Za-z0-9\s]+).*(?:calls|insights|data)",
        r"(?:calls|conversations).*(?:with|from).*([A-Za-z][A-Za-z0-9\s]+)",
        r"(?:gong|call).*(?:data|insights).*(?:for|about).*([A-Za-z][A-Za-z0-9\s]+)"
    ]
    
    gong_sentiment_patterns = [
        r"(?:sentiment|mood|feeling).*(?:calls|conversations|gong)",
        r"(?:positive|negative|neutral).*(?:calls|sentiment)",
        r"(?:how.*feel|customer.*sentiment).*(?:calls|gong)",
        r"(?:analyze|show).*(?:sentiment|mood).*(?:calls|data)"
    ]
    
    gong_topic_patterns = [
        r"(?:topics|themes|subjects).*(?:discussed|mentioned).*(?:calls|gong)",
        r"(?:what.*talked|discussed).*(?:about|in).*(?:calls|meetings)",
        r"(?:key|main|important).*(?:topics|themes).*(?:calls|conversations)",
        r"(?:analyze|show).*(?:topics|themes).*(?:gong|calls)"
    ]
    
    gong_coaching_patterns = [
        r"(?:coaching|feedback|improvement).*(?:insights|recommendations)",
        r"(?:sales|call).*(?:coaching|training|improvement)",
        r"(?:performance|effectiveness).*(?:analysis|insights).*(?:calls|sales)",
        r"(?:recommendations|suggestions).*(?:sales|calls|gong)"
    ]


class EnhancedUnifiedChatService:
    """
    Enhanced unified chat service with advanced NLP and multi-domain intelligence
    """

    def __init__(self):
        self.query_processor = QueryProcessor()
        self.cortex_service = None
        self.hubspot_connector = None
        self.gong_connector = None
        self.ai_memory = None
        self.workflow_orchestrator = None
        self.initialized = False

        # Response cache
        self.response_cache = {}
        self.cache_ttl = 300  # 5 minutes

    async def initialize(self):
        """Initialize all service components"""
        if self.initialized:
            return

        try:
            # Initialize core services
            await self.query_processor.initialize()

            self.cortex_service = SnowflakeCortexService()
            self.hubspot_connector = SnowflakeHubSpotConnector()
            self.gong_connector = SnowflakeGongConnector()
            self.ai_memory = EnhancedAiMemoryMCPServer()
            self.workflow_orchestrator = LangGraphWorkflowOrchestrator()

            # Initialize AI Memory and Workflow Orchestrator
            await self.ai_memory.initialize()
            await self.workflow_orchestrator.initialize()

            self.initialized = True
            logger.info("✅ Enhanced Unified Chat Service initialized")

        except Exception as e:
            logger.error(f"Failed to initialize Enhanced Unified Chat Service: {e}")
            raise

    async def process_query(
        self, query: str, user_context: Optional[Dict[str, Any]] = None
    ) -> QueryResponse:
        """
        Process user query and generate comprehensive response

        Args:
            query: User query text
            user_context: Optional user context

        Returns:
            Comprehensive query response
        """
        if not self.initialized:
            await self.initialize()

        start_time = asyncio.get_event_loop().time()

        try:
            # Check cache
            cache_key = f"{hash(query)}_{hash(str(user_context))}"
            if cache_key in self.response_cache:
                cached_response, timestamp = self.response_cache[cache_key]
                if (datetime.now().timestamp() - timestamp) < self.cache_ttl:
                    logger.info(f"Returning cached response for query: {query[:50]}...")
                    return cached_response

            # Create query context
            context = QueryContext(
                user_role=user_context.get("role", "ceo") if user_context else "ceo",
                time_period=user_context.get("time_period") if user_context else None,
                preferred_format=(
                    user_context.get("format", "executive_summary")
                    if user_context
                    else "executive_summary"
                ),
            )

            # Process query
            processed_query = await self.query_processor.process_query(query, context)

            # Generate response based on intent and complexity
            response = await self._generate_response(processed_query)

            # Calculate processing time
            processing_time = asyncio.get_event_loop().time() - start_time
            response.processing_time = processing_time

            # Cache response
            self.response_cache[cache_key] = (response, datetime.now().timestamp())

            # Store interaction in AI Memory
            await self._store_interaction(query, response)

            logger.info(f"Processed query in {processing_time:.2f}s: {query[:50]}...")
            return response

        except Exception as e:
            logger.error(f"Query processing failed: {e}")
            return QueryResponse(
                query=query,
                intent=QueryIntent.EXECUTIVE_SUMMARY,
                executive_summary=f"I encountered an error processing your query: {str(e)}",
                key_metrics={},
                insights=["Unable to process query due to technical error"],
                recommendations=[
                    "Please try rephrasing your question or contact support"
                ],
                data_sources=[],
                confidence=0.0,
                processing_time=asyncio.get_event_loop().time() - start_time,
                follow_up_questions=[],
            )

    async def _generate_response(
        self, processed_query: ProcessedQuery
    ) -> QueryResponse:
        """Generate comprehensive response based on processed query"""

        # Route to appropriate handler based on intent
        if processed_query.intent == QueryIntent.DEAL_ANALYSIS:
            return await self._handle_deal_analysis(processed_query)
        elif processed_query.intent == QueryIntent.SALES_PERFORMANCE:
            return await self._handle_sales_performance(processed_query)
        elif processed_query.intent == QueryIntent.CALL_INSIGHTS:
            return await self._handle_call_insights(processed_query)
        elif processed_query.intent == QueryIntent.REVENUE_METRICS:
            return await self._handle_revenue_metrics(processed_query)
        elif processed_query.intent == QueryIntent.EXECUTIVE_SUMMARY:
            return await self._handle_executive_summary(processed_query)
        elif processed_query.intent == QueryIntent.PREDICTIVE_INSIGHTS:
            return await self._handle_predictive_insights(processed_query)
        else:
            return await self._handle_general_query(processed_query)

    async def _handle_deal_analysis(
        self, processed_query: ProcessedQuery
    ) -> QueryResponse:
        """Handle deal-specific analysis queries"""

        # Extract deal ID if specified
        deal_id = None
        for entity in processed_query.entities:
            if entity.startswith("deal_id:"):
                deal_id = entity.split(":", 1)[1]
                break

        if deal_id:
            # Use LangGraph workflow for comprehensive deal analysis
            workflow_result = await self.workflow_orchestrator.analyze_deal(
                deal_id=deal_id,
                analysis_type="comprehensive",
                user_request=processed_query.original_query,
            )

            if workflow_result.get("status") == "completed":
                consolidated_findings = workflow_result.get("consolidated_findings", {})
                recommendations = workflow_result.get("recommendations", [])

                return QueryResponse(
                    query=processed_query.original_query,
                    intent=processed_query.intent,
                    executive_summary=consolidated_findings.get(
                        "executive_summary", "Deal analysis completed"
                    ),
                    key_metrics=consolidated_findings.get("key_metrics", {}),
                    insights=[
                        f"Deal health score: {consolidated_findings.get('deal_health_score', 'N/A')}",
                        "Comprehensive analysis completed using AI workflow",
                    ],
                    recommendations=[
                        rec.get("description", "") for rec in recommendations[:5]
                    ],
                    data_sources=["HubSpot CRM", "Gong Calls", "AI Workflow Analysis"],
                    confidence=0.9,
                    processing_time=0.0,
                    follow_up_questions=[
                        "What are the specific risks for this deal?",
                        "What actions should the sales rep take next?",
                        "How does this deal compare to similar opportunities?",
                    ],
                )

        # General deal analysis without specific ID
        async with self.hubspot_connector as connector:
            recent_deals = await connector.query_hubspot_deals(limit=10)

            if not recent_deals.empty:
                # Analyze recent deals using Cortex
                async with self.cortex_service as cortex:
                    analysis_prompt = f"""
                    Analyze these recent deals and provide executive insights:
                    
                    Recent Deals Summary:
                    - Total deals: {len(recent_deals)}
                    - Average value: ${recent_deals['AMOUNT'].mean():,.0f}
                    - Top stage: {recent_deals['DEAL_STAGE'].mode().iloc[0] if not recent_deals['DEAL_STAGE'].mode().empty else 'Unknown'}
                    
                    Provide:
                    1. Overall deal pipeline health
                    2. Key opportunities and risks
                    3. Strategic recommendations
                    """

                    executive_summary = await cortex.complete_text_with_cortex(
                        prompt=analysis_prompt, max_tokens=400
                    )

                return QueryResponse(
                    query=processed_query.original_query,
                    intent=processed_query.intent,
                    executive_summary=executive_summary,
                    key_metrics={
                        "total_deals": len(recent_deals),
                        "average_deal_value": float(recent_deals["AMOUNT"].mean()),
                        "pipeline_value": float(recent_deals["AMOUNT"].sum()),
                    },
                    insights=[
                        f"Analyzed {len(recent_deals)} recent deals",
                        f"Pipeline value: ${recent_deals['AMOUNT'].sum():,.0f}",
                        f"Average deal size: ${recent_deals['AMOUNT'].mean():,.0f}",
                    ],
                    recommendations=[
                        "Focus on high-value opportunities",
                        "Address deals stuck in early stages",
                        "Implement deal acceleration strategies",
                    ],
                    data_sources=["HubSpot CRM", "Snowflake Cortex AI"],
                    confidence=0.8,
                    processing_time=0.0,
                    follow_up_questions=[
                        "Which deals need immediate attention?",
                        "What's our deal velocity trend?",
                        "How can we improve our close rate?",
                    ],
                )

        # Fallback response
        return QueryResponse(
            query=processed_query.original_query,
            intent=processed_query.intent,
            executive_summary="Unable to retrieve deal data at this time.",
            key_metrics={},
            insights=["Deal analysis requires access to CRM data"],
            recommendations=["Ensure HubSpot integration is active"],
            data_sources=[],
            confidence=0.3,
            processing_time=0.0,
            follow_up_questions=[],
        )

    async def _handle_executive_summary(
        self, processed_query: ProcessedQuery
    ) -> QueryResponse:
        """Handle executive summary requests"""

        # Gather data from multiple sources
        summary_data = {}
        data_sources = []

        try:
            # HubSpot data
            async with self.hubspot_connector as connector:
                deals_data = await connector.query_hubspot_deals(limit=100)
                if not deals_data.empty:
                    summary_data["deals"] = {
                        "total_deals": len(deals_data),
                        "pipeline_value": float(deals_data["AMOUNT"].sum()),
                        "average_deal_size": float(deals_data["AMOUNT"].mean()),
                    }
                    data_sources.append("HubSpot CRM")
        except Exception as e:
            logger.error(f"Failed to get HubSpot data: {e}")

        try:
            # Gong data
            async with self.gong_connector as connector:
                calls_data = await connector.get_calls_for_coaching(
                    date_range_days=30, limit=50
                )
                if calls_data:
                    avg_sentiment = sum(
                        call.get("SENTIMENT_SCORE", 0) for call in calls_data
                    ) / len(calls_data)
                    summary_data["calls"] = {
                        "total_calls": len(calls_data),
                        "average_sentiment": avg_sentiment,
                    }
                    data_sources.append("Gong Conversations")
        except Exception as e:
            logger.error(f"Failed to get Gong data: {e}")

        # Generate executive summary using Cortex
        async with self.cortex_service as cortex:
            summary_prompt = f"""
            Create an executive summary based on this business data:
            
            Sales Data: {json.dumps(summary_data.get('deals', {}), indent=2)}
            Call Data: {json.dumps(summary_data.get('calls', {}), indent=2)}
            
            Provide a comprehensive executive summary covering:
            1. Current business performance
            2. Key metrics and trends
            3. Areas of strength and concern
            4. Strategic recommendations
            
            Format for CEO consumption - concise but comprehensive.
            """

            executive_summary = await cortex.complete_text_with_cortex(
                prompt=summary_prompt, max_tokens=500
            )

        # Combine metrics
        key_metrics = {}
        key_metrics.update(summary_data.get("deals", {}))
        key_metrics.update(summary_data.get("calls", {}))

        return QueryResponse(
            query=processed_query.original_query,
            intent=processed_query.intent,
            executive_summary=executive_summary,
            key_metrics=key_metrics,
            insights=[
                "Multi-source business intelligence analysis completed",
                f"Data integrated from {len(data_sources)} systems",
                "AI-powered insights generated using Snowflake Cortex",
            ],
            recommendations=[
                "Monitor pipeline velocity closely",
                "Focus on customer sentiment improvement",
                "Implement data-driven decision making",
            ],
            data_sources=data_sources,
            confidence=0.85,
            processing_time=0.0,
            follow_up_questions=[
                "What are our biggest risks right now?",
                "Which metrics need immediate attention?",
                "How do we compare to last quarter?",
            ],
        )

    async def _handle_general_query(
        self, processed_query: ProcessedQuery
    ) -> QueryResponse:
        """Handle general queries that don't fit specific intents"""

        # Use AI Memory to find relevant context
        relevant_memories = await self.ai_memory.recall_memory(
            query=processed_query.original_query, limit=3
        )

        # Generate response using Cortex with memory context
        async with self.cortex_service as cortex:
            context_info = ""
            if relevant_memories:
                context_info = "\n\nRelevant context from previous interactions:\n"
                for memory in relevant_memories:
                    context_info += f"- {memory.get('content', '')[:200]}...\n"

            response_prompt = f"""
            Answer this business query from a CEO perspective:
            
            Query: {processed_query.original_query}
            {context_info}
            
            Provide:
            1. Direct answer to the question
            2. Relevant business insights
            3. Actionable recommendations
            
            Keep response executive-level and actionable.
            """

            ai_response = await cortex.complete_text_with_cortex(
                prompt=response_prompt, max_tokens=400
            )

        return QueryResponse(
            query=processed_query.original_query,
            intent=processed_query.intent,
            executive_summary=ai_response,
            key_metrics={},
            insights=[
                f"Query processed with {processed_query.confidence:.1%} confidence",
                f"Used {len(relevant_memories)} relevant memories for context",
            ],
            recommendations=[
                "Consider providing more specific details for better insights",
                "Regular data review helps identify trends early",
            ],
            data_sources=["AI Memory", "Snowflake Cortex"],
            confidence=processed_query.confidence,
            processing_time=0.0,
            follow_up_questions=[
                "Would you like more specific data on any aspect?",
                "What time period should we focus on?",
                "Are there specific metrics you want to track?",
            ],
        )

    async def _store_interaction(self, query: str, response: QueryResponse):
        """Store query-response interaction in AI Memory"""
        try:
            interaction_content = f"""
            CEO Query: {query}
            
            Intent: {response.intent.value}
            Confidence: {response.confidence:.2f}
            
            Response Summary: {response.executive_summary[:300]}...
            
            Key Metrics: {json.dumps(response.key_metrics, indent=2)}
            
            Data Sources: {', '.join(response.data_sources)}
            Processing Time: {response.processing_time:.2f}s
            """

            await self.ai_memory.store_memory(
                content=interaction_content,
                category="ceo_dashboard_interaction",
                tags=["ceo_query", response.intent.value, "dashboard"],
                importance_score=0.7,
                auto_detected=True,
            )

        except Exception as e:
            logger.error(f"Failed to store interaction in AI Memory: {e}")

    # Additional handler methods would be implemented similarly...
    async def _handle_sales_performance(
        self, processed_query: ProcessedQuery
    ) -> QueryResponse:
        """Handle sales performance queries"""
        # Implementation similar to deal analysis but focused on sales metrics
        pass

    async def _handle_call_insights(
        self, processed_query: ProcessedQuery
    ) -> QueryResponse:
        """Handle call insights queries"""
        # Implementation focused on Gong call data analysis
        pass

    async def _handle_revenue_metrics(
        self, processed_query: ProcessedQuery
    ) -> QueryResponse:
        """Handle revenue metrics queries"""
        # Implementation focused on financial metrics
        pass

    async def _handle_predictive_insights(
        self, processed_query: ProcessedQuery
    ) -> QueryResponse:
        """Handle predictive analytics queries"""
        # Implementation using advanced AI for predictions
        pass

    async def _handle_gong_call_search(
        self, processed_query: ProcessedQuery
    ) -> QueryResponse:
        """Enhanced Gong call search using STG_TRANSFORMED tables"""
        try:
            # Extract search parameters from query
            search_terms = []
            account_filter = None
            sentiment_filter = None
            date_filter = None
            
            # Parse entities for search parameters
            for entity in processed_query.entities:
                if entity.startswith("company:"):
                    account_filter = entity.split(":", 1)[1]
                elif "sentiment" in processed_query.original_query.lower():
                    if "positive" in processed_query.original_query.lower():
                        sentiment_filter = "> 0.5"
                    elif "negative" in processed_query.original_query.lower():
                        sentiment_filter = "< -0.5"
            
            # Build semantic search query for Gong calls
            semantic_query = processed_query.original_query
            if account_filter:
                semantic_query += f" {account_filter}"
            
            # Search using AI Memory for semantic matching
            memory_results = await self.ai_memory_server.search_memories(
                query=semantic_query,
                category="gong_calls",
                limit=10
            )
            
            # Get detailed call data from STG_TRANSFORMED tables
            database = get_config_value("snowflake_database", "SOPHIA_AI_DEV")
            
            # Build SQL query for structured data
            sql_filters = ["1=1"]  # Base condition
            
            if account_filter:
                sql_filters.append(f"(ACCOUNT_NAME ILIKE '%{account_filter}%' OR CONTACT_NAME ILIKE '%{account_filter}%')")
            
            if sentiment_filter:
                sql_filters.append(f"SENTIMENT_SCORE {sentiment_filter}")
            
            if processed_query.time_filters.get("period"):
                if processed_query.time_filters["type"] == "current":
                    days = processed_query.time_filters["days"]
                    sql_filters.append(f"CALL_DATETIME_UTC >= DATEADD('day', -{days}, CURRENT_TIMESTAMP())")
            
            calls_query = f"""
            SELECT 
                CALL_ID,
                CALL_TITLE,
                CALL_DATETIME_UTC,
                CALL_DURATION_SECONDS,
                CALL_DIRECTION,
                PRIMARY_USER_NAME,
                ACCOUNT_NAME,
                CONTACT_NAME,
                DEAL_STAGE,
                DEAL_VALUE,
                SENTIMENT_SCORE,
                CALL_SUMMARY,
                KEY_TOPICS,
                RISK_INDICATORS,
                NEXT_STEPS,
                TALK_RATIO,
                INTERACTIVITY_SCORE,
                QUESTIONS_ASKED_COUNT
            FROM {database}.STG_TRANSFORMED.STG_GONG_CALLS
            WHERE {' AND '.join(sql_filters)}
            ORDER BY CALL_DATETIME_UTC DESC
            LIMIT 20
            """
            
            calls_data = await self.cortex_service.execute_query(calls_query)
            
            # Generate insights using Snowflake Cortex
            if len(calls_data) > 0:
                # Aggregate insights
                total_calls = len(calls_data)
                avg_sentiment = calls_data['SENTIMENT_SCORE'].mean() if 'SENTIMENT_SCORE' in calls_data.columns else 0
                avg_duration = calls_data['CALL_DURATION_SECONDS'].mean() / 60  # Convert to minutes
                avg_talk_ratio = calls_data['TALK_RATIO'].mean() if 'TALK_RATIO' in calls_data.columns else 0
                
                # Extract key topics and risks
                all_topics = []
                all_risks = []
                for _, call in calls_data.iterrows():
                    if call.get('KEY_TOPICS'):
                        try:
                            topics = json.loads(call['KEY_TOPICS']) if isinstance(call['KEY_TOPICS'], str) else call['KEY_TOPICS']
                            if isinstance(topics, list):
                                all_topics.extend(topics)
                        except:
                            pass
                    
                    if call.get('RISK_INDICATORS'):
                        try:
                            risks = json.loads(call['RISK_INDICATORS']) if isinstance(call['RISK_INDICATORS'], str) else call['RISK_INDICATORS']
                            if isinstance(risks, list):
                                all_risks.extend(risks)
                        except:
                            pass
                
                # Generate executive summary using Cortex
                summary_prompt = f"""
                Analyze these {total_calls} Gong calls:
                - Average sentiment: {avg_sentiment:.2f}
                - Average duration: {avg_duration:.1f} minutes
                - Average talk ratio: {avg_talk_ratio:.1%}
                - Key topics discussed: {', '.join(set(all_topics[:10]))}
                - Risk indicators: {', '.join(set(all_risks[:5]))}
                
                Provide executive insights and recommendations.
                """
                
                executive_summary = await self.cortex_service.complete_text(
                    summary_prompt,
                    model="mistral-large"
                )
                
                # Build detailed insights
                insights = [
                    f"Found {total_calls} calls matching your criteria",
                    f"Average sentiment score: {avg_sentiment:.2f} ({'Positive' if avg_sentiment > 0 else 'Negative' if avg_sentiment < 0 else 'Neutral'})",
                    f"Average call duration: {avg_duration:.1f} minutes",
                    f"Average talk ratio: {avg_talk_ratio:.1%}"
                ]
                
                if all_topics:
                    top_topics = list(set(all_topics))[:5]
                    insights.append(f"Most discussed topics: {', '.join(top_topics)}")
                
                if all_risks:
                    insights.append(f"Risk indicators identified in {len(set(all_risks))} calls")
                
                # Generate recommendations
                recommendations = []
                if avg_sentiment < -0.2:
                    recommendations.append("🚨 Low sentiment detected - review customer concerns and provide coaching")
                elif avg_sentiment > 0.5:
                    recommendations.append("✅ Positive sentiment trend - identify and replicate successful approaches")
                
                if avg_talk_ratio < 0.4:
                    recommendations.append("📢 Low talk ratio - encourage more customer engagement")
                elif avg_talk_ratio > 0.7:
                    recommendations.append("👂 High talk ratio - ensure adequate listening time")
                
                if all_risks:
                    recommendations.append("⚠️ Review identified risk indicators and develop mitigation strategies")
                
                # Key metrics
                key_metrics = {
                    "total_calls": total_calls,
                    "avg_sentiment": round(avg_sentiment, 3),
                    "avg_duration_minutes": round(avg_duration, 1),
                    "avg_talk_ratio": round(avg_talk_ratio, 3),
                    "positive_calls": len([c for _, c in calls_data.iterrows() if c.get('SENTIMENT_SCORE', 0) > 0.2]),
                    "negative_calls": len([c for _, c in calls_data.iterrows() if c.get('SENTIMENT_SCORE', 0) < -0.2]),
                    "high_value_calls": len([c for _, c in calls_data.iterrows() if c.get('DEAL_VALUE', 0) > 50000])
                }
                
                # Create visualizations data
                visualizations = [
                    {
                        "type": "sentiment_distribution",
                        "title": "Call Sentiment Distribution",
                        "data": calls_data[['CALL_ID', 'SENTIMENT_SCORE']].to_dict('records') if 'SENTIMENT_SCORE' in calls_data.columns else []
                    },
                    {
                        "type": "timeline",
                        "title": "Calls Timeline",
                        "data": calls_data[['CALL_DATETIME_UTC', 'CALL_TITLE', 'SENTIMENT_SCORE']].to_dict('records')
                    }
                ]
                
                return QueryResponse(
                    query=processed_query.original_query,
                    intent=processed_query.intent,
                    executive_summary=executive_summary or f"Analysis of {total_calls} Gong calls with average sentiment of {avg_sentiment:.2f}",
                    key_metrics=key_metrics,
                    insights=insights,
                    recommendations=recommendations,
                    data_sources=["STG_TRANSFORMED.STG_GONG_CALLS", "AI_MEMORY.MEMORY_RECORDS"],
                    confidence=0.9,
                    processing_time=0.0,
                    follow_up_questions=[
                        "Would you like to see transcript details for any specific call?",
                        "Should I analyze sentiment trends over time?",
                        "Do you want coaching recommendations for specific reps?"
                    ],
                    visualizations=visualizations
                )
            
            else:
                return QueryResponse(
                    query=processed_query.original_query,
                    intent=processed_query.intent,
                    executive_summary="No Gong calls found matching your search criteria.",
                    key_metrics={"total_calls": 0},
                    insights=["No calls found with the specified criteria"],
                    recommendations=["Try broadening your search criteria or check data availability"],
                    data_sources=["STG_TRANSFORMED.STG_GONG_CALLS"],
                    confidence=0.8,
                    processing_time=0.0,
                    follow_up_questions=[
                        "Would you like to search with different criteria?",
                        "Should I check recent data ingestion status?"
                    ]
                )
                
        except Exception as e:
            logger.error(f"Error in Gong call search: {e}")
            return QueryResponse(
                query=processed_query.original_query,
                intent=processed_query.intent,
                executive_summary=f"Error occurred while searching Gong calls: {str(e)}",
                key_metrics={},
                insights=[],
                recommendations=["Please try again or contact support"],
                data_sources=[],
                confidence=0.0,
                processing_time=0.0,
                follow_up_questions=[]
            )

    async def _handle_gong_transcript_search(
        self, processed_query: ProcessedQuery
    ) -> QueryResponse:
        """Handle Gong transcript search queries"""
        try:
            start_time = time.time()
            
            query_text = processed_query.original_query
            
            # Extract speaker type filter
            speaker_type = None
            if "internal" in query_text.lower():
                speaker_type = "Internal"
            elif "external" in query_text.lower() or "customer" in query_text.lower():
                speaker_type = "External"
            
            # Perform transcript search
            transcript_results = await self.cortex_service.search_gong_transcripts_with_ai_memory(
                query_text=query_text,
                top_k=15,
                similarity_threshold=0.7,
                speaker_type=speaker_type
            )
            
            # Generate summary
            total_segments = len(transcript_results)
            unique_calls = len(set(segment["call_id"] for segment in transcript_results))
            
            avg_sentiment = sum(
                segment["ai_insights"]["segment_sentiment"] or 0 
                for segment in transcript_results 
                if segment["ai_insights"]["segment_sentiment"] is not None
            ) / max(total_segments, 1)
            
            executive_summary = f"""
            Found {total_segments} transcript segments across {unique_calls} calls matching your search. 
            Average segment sentiment: {avg_sentiment:.2f}. 
            Results include both internal and external speaker perspectives.
            """
            
            # Generate insights from transcript analysis
            insights = []
            
            if transcript_results:
                # Speaker insights
                internal_segments = sum(1 for seg in transcript_results if seg["speaker"]["type"] == "Internal")
                external_segments = total_segments - internal_segments
                insights.append(f"Speaker distribution: {internal_segments} internal, {external_segments} external segments")
                
                # Entity insights
                all_entities = []
                for segment in transcript_results:
                    if segment["content"]["extracted_entities"]:
                        all_entities.extend(segment["content"]["extracted_entities"])
                
                if all_entities:
                    from collections import Counter
                    top_entities = Counter(all_entities).most_common(3)
                    insights.append(f"Key entities mentioned: {', '.join([entity for entity, _ in top_entities])}")
            
            # Generate recommendations
            recommendations = []
            if avg_sentiment < 0:
                recommendations.append("Review negative sentiment segments for coaching opportunities")
            
            if transcript_results:
                recommendations.append("Consider creating talking points based on successful conversation patterns")
            
            key_metrics = {
                "transcript_segments_found": total_segments,
                "unique_calls": unique_calls,
                "average_segment_sentiment": round(avg_sentiment, 2),
                "internal_speaker_segments": sum(1 for seg in transcript_results if seg["speaker"]["type"] == "Internal"),
                "external_speaker_segments": sum(1 for seg in transcript_results if seg["speaker"]["type"] == "External")
            }
            
            processing_time = time.time() - start_time
            
            return QueryResponse(
                query=processed_query.original_query,
                intent=processed_query.intent,
                executive_summary=executive_summary.strip(),
                key_metrics=key_metrics,
                insights=insights,
                recommendations=recommendations,
                data_sources=["Gong Transcripts", "AI Memory", "Snowflake Cortex"],
                confidence=processed_query.confidence,
                processing_time=processing_time,
                follow_up_questions=[
                    "Would you like to see the actual transcript text?",
                    "Should I analyze conversation patterns for coaching?",
                    "Do you want to search for similar conversations?"
                ],
                visualizations=[
                    {
                        "type": "speaker_sentiment",
                        "data": transcript_results,
                        "title": "Speaker Sentiment Analysis"
                    }
                ]
            )
            
        except Exception as e:
            logger.error(f"Error handling Gong transcript search: {e}")
            return QueryResponse(
                query=processed_query.original_query,
                intent=processed_query.intent,
                executive_summary=f"Error searching Gong transcripts: {str(e)}",
                key_metrics={},
                insights=[],
                recommendations=[],
                data_sources=[],
                confidence=0.0,
                processing_time=0.0,
                follow_up_questions=[]
            )

    async def _handle_gong_account_insights(
        self, processed_query: ProcessedQuery
    ) -> QueryResponse:
        """Handle Gong account-specific insights queries"""
        try:
            start_time = time.time()
            
            # Extract account name from query
            query_text = processed_query.original_query
            entities = processed_query.entities
            
            # Try to extract account name from entities or query
            account_name = None
            for entity in entities:
                if entity.startswith("company:"):
                    account_name = entity.split(":", 1)[1].strip()
                    break
            
            # If no account found in entities, try regex
            if not account_name:
                import re
                account_match = re.search(r"(?:account|company|client)\s+([A-Za-z][A-Za-z0-9\s&]+)", query_text, re.IGNORECASE)
                if account_match:
                    account_name = account_match.group(1).strip()
            
            if not account_name:
                return QueryResponse(
                    query=processed_query.original_query,
                    intent=processed_query.intent,
                    executive_summary="Please specify an account name to search for insights.",
                    key_metrics={},
                    insights=[],
                    recommendations=["Try: 'Show me Gong insights for Acme Corp'"],
                    data_sources=[],
                    confidence=0.0,
                    processing_time=0.0,
                    follow_up_questions=[]
                )
            
            # Search for account-specific insights
            account_insights = await self.ai_memory.search_gong_insights_by_account(
                account_name=account_name,
                limit=20,
                include_transcripts=True
            )
            
            # Generate comprehensive account analysis
            call_level_insights = [insight for insight in account_insights if insight.get("insight_level") == "call"]
            transcript_level_insights = [insight for insight in account_insights if insight.get("insight_level") == "transcript"]
            
            total_insights = len(account_insights)
            
            # Calculate account health metrics
            sentiments = [insight.get("sentiment_score") for insight in call_level_insights if insight.get("sentiment_score") is not None]
            avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0
            
            executive_summary = f"""
            Account Analysis for {account_name}: Found {total_insights} insights across {len(call_level_insights)} calls 
            and {len(transcript_level_insights)} transcript segments. 
            Overall sentiment: {avg_sentiment:.2f} ({'Positive' if avg_sentiment > 0.3 else 'Negative' if avg_sentiment < -0.3 else 'Neutral'}).
            """
            
            # Generate account-specific insights
            insights = []
            
            if call_level_insights:
                # Deal stage insights
                deal_stages = [insight.get("deal_stage") for insight in call_level_insights if insight.get("deal_stage")]
                if deal_stages:
                    from collections import Counter
                    stage_counts = Counter(deal_stages)
                    current_stage = stage_counts.most_common(1)[0][0]
                    insights.append(f"Most recent deal stage: {current_stage}")
                
                # Risk analysis
                risks = []
                for insight in call_level_insights:
                    if insight.get("risk_indicators"):
                        risks.extend(insight["risk_indicators"])
                
                if risks:
                    from collections import Counter
                    top_risks = Counter(risks).most_common(2)
                    insights.append(f"Key risks identified: {', '.join([risk for risk, _ in top_risks])}")
                
                # Relationship health
                if avg_sentiment > 0.5:
                    insights.append("Strong positive relationship - high engagement and satisfaction")
                elif avg_sentiment < -0.3:
                    insights.append("Relationship requires attention - negative sentiment trends detected")
            
            # Generate recommendations
            recommendations = []
            
            if avg_sentiment < 0:
                recommendations.append(f"Schedule relationship recovery call with {account_name}")
                recommendations.append("Review recent interactions for improvement opportunities")
            elif avg_sentiment > 0.5:
                recommendations.append(f"Consider expansion opportunities with {account_name}")
            
            if call_level_insights:
                recent_calls = sorted(call_level_insights, key=lambda x: x.get("call_datetime", ""), reverse=True)[:3]
                if recent_calls:
                    recommendations.append("Follow up on action items from recent calls")
            
            key_metrics = {
                "total_insights": total_insights,
                "call_level_insights": len(call_level_insights),
                "transcript_level_insights": len(transcript_level_insights),
                "average_sentiment": round(avg_sentiment, 2),
                "account_name": account_name,
                "sentiment_trend": "Positive" if avg_sentiment > 0.3 else "Negative" if avg_sentiment < -0.3 else "Neutral"
            }
            
            processing_time = time.time() - start_time
            
            return QueryResponse(
                query=processed_query.original_query,
                intent=processed_query.intent,
                executive_summary=executive_summary.strip(),
                key_metrics=key_metrics,
                insights=insights,
                recommendations=recommendations,
                data_sources=["Gong Calls", "Gong Transcripts", "AI Memory"],
                confidence=processed_query.confidence,
                processing_time=processing_time,
                follow_up_questions=[
                    f"Would you like detailed call history for {account_name}?",
                    "Should I analyze conversation topics with this account?",
                    "Do you want to see risk mitigation strategies?"
                ],
                visualizations=[
                    {
                        "type": "account_sentiment_timeline",
                        "data": call_level_insights,
                        "title": f"{account_name} Sentiment Over Time"
                    },
                    {
                        "type": "account_interaction_summary",
                        "data": account_insights,
                        "title": f"{account_name} Interaction Summary"
                    }
                ]
            )
            
        except Exception as e:
            logger.error(f"Error handling Gong account insights: {e}")
            return QueryResponse(
                query=processed_query.original_query,
                intent=processed_query.intent,
                executive_summary=f"Error retrieving account insights: {str(e)}",
                key_metrics={},
                insights=[],
                recommendations=[],
                data_sources=[],
                confidence=0.0,
                processing_time=0.0,
                follow_up_questions=[]
            )

    async def _handle_gong_sentiment_analysis(
        self, processed_query: ProcessedQuery
    ) -> QueryResponse:
        """Handle Gong sentiment analysis queries"""
        try:
            start_time = time.time()
            
            # Get comprehensive Gong analytics with sentiment focus
            analytics = await self.cortex_service.get_gong_call_analytics(
                date_range_days=30,  # Default to last 30 days
                include_ai_insights=True
            )
            
            if "error" in analytics:
                raise Exception(analytics["error"])
            
            # Extract sentiment data
            sentiment_dist = analytics["sentiment_distribution"]
            total_calls = analytics["summary"]["total_calls"]
            avg_sentiment = analytics["summary"]["avg_sentiment_score"]
            
            # Calculate sentiment percentages
            positive_pct = (sentiment_dist["positive"] / total_calls * 100) if total_calls > 0 else 0
            negative_pct = (sentiment_dist["negative"] / total_calls * 100) if total_calls > 0 else 0
            neutral_pct = (sentiment_dist["neutral"] / total_calls * 100) if total_calls > 0 else 0
            
            executive_summary = f"""
            Sentiment Analysis for {total_calls} calls over the last 30 days:
            Overall sentiment score: {avg_sentiment:.2f}
            Distribution: {positive_pct:.1f}% positive, {neutral_pct:.1f}% neutral, {negative_pct:.1f}% negative.
            """
            
            # Generate sentiment insights
            insights = []
            
            if positive_pct > 60:
                insights.append("Strong positive sentiment trend - customer relationships are healthy")
            elif negative_pct > 30:
                insights.append("Concerning negative sentiment levels - immediate attention required")
            
            if avg_sentiment > 0.5:
                insights.append("Exceptional customer satisfaction levels detected")
            elif avg_sentiment < -0.3:
                insights.append("Customer satisfaction below acceptable threshold")
            
            # Trend analysis
            if analytics.get("ai_insights", {}).get("top_topics"):
                top_topics = analytics["ai_insights"]["top_topics"][:3]
                insights.append(f"Top discussion topics: {', '.join([topic['topic'] for topic in top_topics])}")
            
            # Generate recommendations
            recommendations = []
            
            if negative_pct > 20:
                recommendations.append("Implement immediate coaching for calls with negative sentiment")
                recommendations.append("Review and improve customer interaction protocols")
            
            if positive_pct > 70:
                recommendations.append("Identify and replicate successful conversation patterns")
                recommendations.append("Consider case studies from high-performing interactions")
            
            recommendations.append("Schedule regular sentiment monitoring and reporting")
            
            key_metrics = {
                "total_calls_analyzed": total_calls,
                "average_sentiment_score": avg_sentiment,
                "positive_calls": sentiment_dist["positive"],
                "negative_calls": sentiment_dist["negative"],
                "neutral_calls": sentiment_dist["neutral"],
                "positive_percentage": round(positive_pct, 1),
                "negative_percentage": round(negative_pct, 1),
                "neutral_percentage": round(neutral_pct, 1),
                "sentiment_health_score": round((positive_pct - negative_pct), 1)
            }
            
            processing_time = time.time() - start_time
            
            return QueryResponse(
                query=processed_query.original_query,
                intent=processed_query.intent,
                executive_summary=executive_summary.strip(),
                key_metrics=key_metrics,
                insights=insights,
                recommendations=recommendations,
                data_sources=["Gong Calls", "Snowflake Cortex", "AI Analytics"],
                confidence=processed_query.confidence,
                processing_time=processing_time,
                follow_up_questions=[
                    "Would you like to see sentiment trends over time?",
                    "Should I identify specific calls needing attention?",
                    "Do you want coaching recommendations for negative sentiment calls?"
                ],
                visualizations=[
                    {
                        "type": "sentiment_pie_chart",
                        "data": sentiment_dist,
                        "title": "Call Sentiment Distribution"
                    },
                    {
                        "type": "sentiment_trend",
                        "data": analytics,
                        "title": "Sentiment Trend Over Time"
                    }
                ]
            )
            
        except Exception as e:
            logger.error(f"Error handling Gong sentiment analysis: {e}")
            return QueryResponse(
                query=processed_query.original_query,
                intent=processed_query.intent,
                executive_summary=f"Error analyzing sentiment: {str(e)}",
                key_metrics={},
                insights=[],
                recommendations=[],
                data_sources=[],
                confidence=0.0,
                processing_time=0.0,
                follow_up_questions=[]
            )


# Global service instance
enhanced_chat_service = EnhancedUnifiedChatService()


async def process_ceo_query(
    query: str, user_context: Optional[Dict[str, Any]] = None
) -> QueryResponse:
    """
    Convenience function for processing CEO queries

    Args:
        query: User query text
        user_context: Optional user context

    Returns:
        Comprehensive query response
    """
    return await enhanced_chat_service.process_query(query, user_context)


# Example usage
if __name__ == "__main__":

    async def test_chat_service():
        """Test the enhanced chat service"""

        test_queries = [
            "What were the key topics and sentiment for recent calls related to our top 5 largest open deals?",
            "Show me our sales performance this quarter",
            "Which deals need immediate attention?",
            "Give me an executive summary of our business status",
            "What's our revenue forecast for next quarter?",
        ]

        for query in test_queries:
            print(f"\n--- Query: {query} ---")
            response = await process_ceo_query(query)
            print(f"Intent: {response.intent.value}")
            print(f"Summary: {response.executive_summary[:200]}...")
            print(f"Confidence: {response.confidence:.2f}")
            print(f"Processing Time: {response.processing_time:.2f}s")

    asyncio.run(test_chat_service())
