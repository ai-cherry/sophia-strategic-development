# 🎯 COMPETITOR INTELLIGENCE FLOW ANALYSIS
**Sophia AI - Complete Data Pipeline Documentation**

## 📊 SYSTEM ARCHITECTURE OVERVIEW

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────────┐
│  Data Sources   │───▶│  Ingestion Layer │───▶│   Storage Layer     │
│                 │    │                  │    │                     │
│ • Web Scraping  │    │ • Intelligence   │    │ • Qdrant Vector DB  │
│ • API Feeds     │    │   Service        │    │ • Collections:      │
│ • Manual Input  │    │ • Embeddings     │    │   - competitor_     │
│ • Social Media  │    │ • Processing     │    │     profiles        │
│                 │    │                  │    │   - competitor_     │
└─────────────────┘    └──────────────────┘    │     intelligence    │
                                               └─────────────────────┘
                                                         │
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────────┘
│  Chat Interface │◀───│  AI Orchestrator │◀───│
│                 │    │                  │    │
│ • Natural Lang  │    │ • Query Router   │    │
│ • Contextual    │    │ • Memory Search  │    │
│ • Real-time     │    │ • Response Gen   │    │
│                 │    │                  │    │
└─────────────────┘    └──────────────────┘    │
                                               │
┌─────────────────┐    ┌──────────────────┐    │
│   Dashboard     │◀───│  Frontend APIs   │◀───┘
│                 │    │                  │
│ • External      │    │ • Search Endpoints
│   Intelligence │    │ • Real-time Updates
│ • Visualizations│    │ • WebSocket Streams
└─────────────────┘    └──────────────────┘
```

---

## 🔍 DETAILED COMPONENT ANALYSIS

### **1. Data Ingestion Layer**

#### **A. CompetitorIntelligenceService** (`backend/services/competitor_intelligence_service.py`)

**Primary Storage Service:**
```python
class CompetitorIntelligenceService:
    """Service for managing competitor intelligence with Qdrant vector storage"""
    
    def __init__(self):
        self.client = QDRANT_client
        self.profiles_collection = "competitor_profiles"       # Company profiles
        self.intelligence_collection = "competitor_intelligence" # Intelligence items
        self.embeddings_dimension = 768
```

**Data Structures:**
```python
@dataclass
class CompetitorProfile:
    id: str
    name: str
    category: CompetitorCategory  # DIRECT, INDIRECT, EMERGING, SUBSTITUTE
    description: str
    website: str
    threat_level: int  # 1-10 scale
    market_share: float
    growth_rate: float
    key_products: List[str]
    strengths: List[str]
    weaknesses: List[str]

@dataclass
class CompetitorIntelligence:
    id: str
    competitor_id: str
    intelligence_type: IntelligenceType  # PRODUCT_LAUNCH, PRICING, FUNDING, etc.
    title: str
    description: str
    source: str  # website, social_media, news, etc.
    impact_score: float  # 0-10
    confidence_score: float  # 0-1
    timestamp: datetime
    tags: List[str]
```

#### **B. Data Ingestion Methods**

**1. Manual Addition:**
```python
async def add_competitor_profile(self, profile: CompetitorProfile) -> bool:
    """Add or update competitor profile"""
    try:
        # Generate embedding from profile data
        profile_text = f"{profile.name} {profile.description} {' '.join(profile.key_products)}"
        embedding = self._generate_embedding(profile_text)
        
        # Store in Qdrant with full metadata
        point = PointStruct(
            id=profile.id,
            vector=embedding,
            payload=asdict(profile)
        )
        
        result = self.client.upsert(
            collection_name=self.profiles_collection,
            points=[point]
        )
        return result.status == UpdateStatus.COMPLETED
```

**2. Intelligence Item Addition:**
```python
async def add_intelligence(self, intelligence: CompetitorIntelligence) -> bool:
    """Add competitor intelligence"""
    try:
        # Generate embedding from intelligence content
        intelligence_text = f"{intelligence.title} {intelligence.description} {' '.join(intelligence.tags)}"
        embedding = self._generate_embedding(intelligence_text)
        
        # Store with searchable metadata
        point = PointStruct(
            id=intelligence.id,
            vector=embedding,
            payload={
                **asdict(intelligence),
                "timestamp": intelligence.timestamp.isoformat(),
                "intelligence_type": intelligence.intelligence_type.value,
                "search_text": intelligence_text
            }
        )
        
        result = self.client.upsert(
            collection_name=self.intelligence_collection,
            points=[point]
        )
```

### **2. Storage Architecture**

#### **A. Qdrant Vector Collections**

**Collection 1: `competitor_profiles`**
```python
# Configuration
{
    "name": "competitor_profiles",
    "vector_size": 768,  # OpenAI embedding dimension
    "distance": "Cosine"
}

# Stored Data Structure
{
    "id": "comp_001",
    "vector": [0.1, 0.2, ...], # 768-dimensional embedding
    "payload": {
        "name": "TechCorp",
        "category": "DIRECT",
        "description": "AI-powered property management platform",
        "website": "https://techcorp.com",
        "threat_level": 8,
        "market_share": 0.15,
        "growth_rate": 0.45,
        "key_products": ["AI Assistant", "Property Analytics"],
        "strengths": ["Strong enterprise sales", "Advanced AI"],
        "weaknesses": ["High pricing", "Complex onboarding"]
    }
}
```

**Collection 2: `competitor_intelligence`**
```python
# Configuration
{
    "name": "competitor_intelligence", 
    "vector_size": 768,
    "distance": "Cosine"
}

# Stored Data Structure
{
    "id": "intel_001",
    "vector": [0.3, 0.1, ...], # 768-dimensional embedding
    "payload": {
        "competitor_id": "comp_001",
        "intelligence_type": "PRODUCT_LAUNCH",
        "title": "TechCorp launches AI copilot for property managers",
        "description": "New AI assistant with natural language interface...",
        "source": "company_blog",
        "impact_score": 8.5,
        "confidence_score": 0.95,
        "timestamp": "2025-07-14T20:00:00Z",
        "tags": ["AI", "product-launch", "copilot"],
        "search_text": "TechCorp launches AI copilot..."
    }
}
```

#### **B. Integration with Unified Memory Service**

The competitor data integrates with the broader memory architecture:

```python
# From unified_memory_service_v3.py
class UnifiedMemoryServiceV3:
    def __init__(self):
        self.collections = {
            "competitors": CollectionConfig(
                name="sophia_competitors",
                vector_size=768,
                ttl_seconds=None  # Permanent storage
            ),
            "competitor_events": CollectionConfig(
                name="sophia_competitor_events", 
                vector_size=768,
                ttl_seconds=2592000  # 30 days for events
            )
        }
```

### **3. Retrieval & Search Layer**

#### **A. Search Methods**

**1. Competitor Profile Search:**
```python
async def search_competitors(self, query: str, limit: int = 10, 
                           category: Optional[CompetitorCategory] = None) -> List[Dict[str, Any]]:
    """Search competitors by query"""
    try:
        # Generate query embedding
        query_embedding = self._generate_embedding(query)
        
        # Build filters
        filter_conditions = []
        if category:
            filter_conditions.append(
                FieldCondition(key="category", match=MatchValue(value=category.value))
            )
        
        # Execute vector search
        results = self.client.search(
            collection_name=self.profiles_collection,
            query_vector=query_embedding,
            query_filter=Filter(must=filter_conditions) if filter_conditions else None,
            limit=limit,
            with_payload=True,
            score_threshold=0.5  # Minimum similarity threshold
        )
        
        # Format results with similarity scores
        competitors = []
        for result in results:
            competitor = result.payload.copy()
            competitor["similarity_score"] = result.score
            competitors.append(competitor)
            
        return competitors
```

**2. Intelligence Search:**
```python
async def search_intelligence(self, query: str, limit: int = 20,
                            competitor_id: Optional[str] = None,
                            intelligence_type: Optional[IntelligenceType] = None,
                            days_back: int = 30) -> List[Dict[str, Any]]:
    """Search competitor intelligence"""
    try:
        query_embedding = self._generate_embedding(query)
        
        # Build comprehensive filters
        filter_conditions = []
        
        # Competitor filter
        if competitor_id:
            filter_conditions.append(
                FieldCondition(key="competitor_id", match=MatchValue(value=competitor_id))
            )
        
        # Intelligence type filter
        if intelligence_type:
            filter_conditions.append(
                FieldCondition(key="intelligence_type", match=MatchValue(value=intelligence_type.value))
            )
        
        # Time-based filter (last N days)
        cutoff_date = datetime.now(UTC) - timedelta(days=days_back)
        filter_conditions.append(
            FieldCondition(
                key="timestamp",
                range=DatetimeRange(gte=cutoff_date.isoformat())
            )
        )
        
        # Execute search
        results = self.client.search(
            collection_name=self.intelligence_collection,
            query_vector=query_embedding,
            query_filter=Filter(must=filter_conditions),
            limit=limit,
            with_payload=True,
            score_threshold=0.4
        )
        
        # Format and return results
        intelligence_items = []
        for result in results:
            item = result.payload.copy()
            item["similarity_score"] = result.score
            intelligence_items.append(item)
            
        return intelligence_items
```

#### **B. Analytics & Aggregation**

**1. Threat Analysis:**
```python
async def get_threat_analysis(self) -> Dict[str, Any]:
    """Generate comprehensive threat analysis"""
    try:
        # Get all competitor profiles
        all_profiles = self.client.scroll(
            collection_name=self.profiles_collection,
            limit=1000,
            with_payload=True
        )[0]
        
        # Analyze threat distribution
        threat_distribution = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        category_distribution = {"direct": 0, "indirect": 0, "emerging": 0, "substitute": 0}
        
        for profile in all_profiles:
            payload = profile.payload
            threat_level = payload.get("threat_level", 0)
            category = payload.get("category", "").lower()
            
            # Categorize threat level
            if threat_level >= 9:
                threat_distribution["critical"] += 1
            elif threat_level >= 7:
                threat_distribution["high"] += 1
            elif threat_level >= 5:
                threat_distribution["medium"] += 1
            else:
                threat_distribution["low"] += 1
                
            # Count categories
            if category in category_distribution:
                category_distribution[category] += 1
        
        return {
            "total_competitors": len(all_profiles),
            "threat_distribution": threat_distribution,
            "category_distribution": category_distribution,
            "top_threats": sorted(all_profiles, key=lambda x: x.payload.get("threat_level", 0), reverse=True)[:5],
            "market_insights": {
                "total_market_share": sum(p.payload.get("market_share", 0) for p in all_profiles),
                "average_growth_rate": sum(p.payload.get("growth_rate", 0) for p in all_profiles) / len(all_profiles)
            }
        }
```

**2. Intelligence Summary:**
```python
async def get_intelligence_summary(self, days_back: int = 7) -> Dict[str, Any]:
    """Get intelligence summary for recent period"""
    try:
        # Time-based filter
        cutoff_date = datetime.now(UTC) - timedelta(days=days_back)
        
        # Get recent intelligence
        results = self.client.scroll(
            collection_name=self.intelligence_collection,
            scroll_filter=Filter(
                must=[
                    FieldCondition(
                        key="timestamp",
                        range=DatetimeRange(gte=cutoff_date.isoformat())
                    )
                ]
            ),
            limit=1000,
            with_payload=True
        )[0]
        
        # Aggregate data
        summary = {
            "total_items": len(results),
            "period_days": days_back,
            "type_distribution": {},
            "impact_analysis": {"high_impact": 0, "medium_impact": 0, "low_impact": 0},
            "top_intelligence": [],
            "competitor_activity": {}
        }
        
        for result in results:
            payload = result.payload
            intel_type = payload.get("intelligence_type", "unknown")
            impact_score = payload.get("impact_score", 0)
            competitor_id = payload.get("competitor_id", "unknown")
            
            # Type distribution
            summary["type_distribution"][intel_type] = summary["type_distribution"].get(intel_type, 0) + 1
            
            # Impact analysis
            if impact_score >= 7:
                summary["impact_analysis"]["high_impact"] += 1
                summary["top_intelligence"].append({
                    "title": payload.get("title", ""),
                    "competitor_id": competitor_id,
                    "impact_score": impact_score,
                    "intelligence_type": intel_type,
                    "timestamp": payload.get("timestamp", "")
                })
            elif impact_score >= 4:
                summary["impact_analysis"]["medium_impact"] += 1
            else:
                summary["impact_analysis"]["low_impact"] += 1
            
            # Competitor activity tracking
            summary["competitor_activity"][competitor_id] = summary["competitor_activity"].get(competitor_id, 0) + 1
        
        # Sort top intelligence by impact
        summary["top_intelligence"].sort(key=lambda x: x["impact_score"], reverse=True)
        
        return summary
```

### **4. AI Orchestrator Integration**

#### **A. Memory Service Integration**

The competitor intelligence is accessible through the unified memory service:

```python
# From unified_memory_service_primary.py
class UnifiedMemoryService(UnifiedMemoryServiceV3):
    """Primary memory service for Sophia AI"""
    
    async def search_memories(self, query: str, user_id: str, limit: int = 10, 
                            filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Unified memory search interface"""
        return await super().search_knowledge(
            query=query,
            limit=limit,
            metadata_filter=filters or {}
        )
```

#### **B. Business Intelligence Integration**

Competitor data integrates with broader business intelligence:

```python
# From advanced_hybrid_search_service.py
async def _search_market_intelligence(self, query: str, context: SearchContext) -> BusinessInsights:
    """Search market intelligence layer"""
    
    # Search competitor intelligence
    competitor_results = await self.competitor_service.search_intelligence(
        query=query,
        limit=20,
        days_back=30
    )
    
    # Search competitor profiles
    profile_results = await self.competitor_service.search_competitors(
        query=query,
        limit=10
    )
    
    # Combine and analyze
    market_insights = BusinessInsights(
        primary_insights=competitor_results + profile_results,
        related_entities=self._extract_competitor_entities(competitor_results),
        temporal_context=self._analyze_competitor_trends(competitor_results),
        confidence_score=self._calculate_market_confidence(competitor_results, profile_results)
    )
    
    return market_insights
```

### **5. Chat Interface Access**

#### **A. Natural Language Query Processing**

When users ask competitor-related questions in the chat:

```python
# Example chat processing flow
async def process_competitor_query(user_message: str, context: ChatContext) -> ChatResponse:
    """Process competitor-related queries"""
    
    # 1. Detect competitor intent
    if any(keyword in user_message.lower() for keyword in ["competitor", "competition", "market", "rival"]):
        
        # 2. Route to competitor intelligence service
        if "recent" in user_message or "latest" in user_message:
            # Get recent intelligence
            intelligence_results = await competitor_service.search_intelligence(
                query=user_message,
                days_back=7,
                limit=10
            )
            
        elif "threat" in user_message or "analysis" in user_message:
            # Get threat analysis
            threat_analysis = await competitor_service.get_threat_analysis()
            
        elif "profile" in user_message or "about" in user_message:
            # Search competitor profiles
            profile_results = await competitor_service.search_competitors(
                query=user_message,
                limit=5
            )
        
        # 3. Generate contextualized response
        response = await generate_competitor_response(
            query=user_message,
            intelligence_data=intelligence_results,
            threat_data=threat_analysis,
            profile_data=profile_results,
            context=context
        )
        
        return response
```

#### **B. Contextualized Response Generation**

```python
async def generate_competitor_response(query: str, intelligence_data: List, 
                                     threat_data: Dict, profile_data: List,
                                     context: ChatContext) -> ChatResponse:
    """Generate contextualized competitor intelligence response"""
    
    # Build comprehensive context
    response_context = {
        "recent_intelligence": intelligence_data[:5],
        "threat_summary": {
            "total_competitors": threat_data.get("total_competitors", 0),
            "high_threat_count": threat_data.get("threat_distribution", {}).get("high", 0),
            "top_threat": threat_data.get("top_threats", [{}])[0].get("name", "Unknown")
        },
        "relevant_profiles": profile_data[:3]
    }
    
    # Generate AI response with full context
    response_content = f"""
    **Competitor Intelligence Summary:**
    
    📊 **Market Overview:**
    - Total tracked competitors: {response_context['threat_summary']['total_competitors']}
    - High-threat competitors: {response_context['threat_summary']['high_threat_count']}
    - Top threat: {response_context['threat_summary']['top_threat']}
    
    🔍 **Recent Intelligence ({len(intelligence_data)} items):**
    """
    
    # Add recent intelligence items
    for item in response_context["recent_intelligence"]:
        response_content += f"""
    • **{item.get('title', 'Untitled')}** ({item.get('competitor_id', 'Unknown')})
      Impact: {item.get('impact_score', 0)}/10 | Confidence: {int(item.get('confidence_score', 0) * 100)}%
      {item.get('description', '')[:100]}...
        """
    
    # Add competitor profiles
    if response_context["relevant_profiles"]:
        response_content += f"""
        
    🏢 **Relevant Competitors:**
        """
        for profile in response_context["relevant_profiles"]:
            response_content += f"""
    • **{profile.get('name', 'Unknown')}** (Threat Level: {profile.get('threat_level', 0)}/10)
      Category: {profile.get('category', 'Unknown')} | Market Share: {profile.get('market_share', 0)*100:.1f}%
      Strengths: {', '.join(profile.get('strengths', [])[:2])}
            """
    
    return ChatResponse(
        content=response_content,
        sources=["competitor_intelligence_service", "qdrant_vector_db"],
        insights=[
            f"Monitored {response_context['threat_summary']['total_competitors']} competitors",
            f"Found {len(intelligence_data)} recent intelligence items",
            f"{response_context['threat_summary']['high_threat_count']} high-threat competitors identified"
        ],
        recommendations=[
            "Monitor top threats for product launches and pricing changes",
            "Analyze competitor strengths for potential partnership opportunities",
            "Track emerging competitors for early threat detection"
        ],
        metadata={
            "intelligence_sources": len(intelligence_data),
            "competitor_profiles": len(profile_data),
            "threat_analysis_included": bool(threat_data),
            "data_freshness": "< 5 minutes"
        }
    )
```

### **6. Frontend Dashboard Display**

#### **A. ExternalIntelligenceMonitor Component**

The frontend displays competitor intelligence through the External Intelligence Monitor:

```typescript
// From ExternalIntelligenceMonitor.tsx
const ExternalIntelligenceMonitor: React.FC = () => {
  // Real-time data fetching
  const { data: competitorIntelligence } = useQuery({
    queryKey: ['competitor-intelligence', searchQuery],
    queryFn: () => fetchCompetitorIntelligence(searchQuery || 'AI', 20),
    refetchInterval: 5 * 60 * 1000, // Refresh every 5 minutes
  });

  const { data: threatAnalysis } = useQuery({
    queryKey: ['threat-analysis'],
    queryFn: fetchThreatAnalysis,
    refetchInterval: 10 * 60 * 1000, // Refresh every 10 minutes
  });
```

#### **B. API Endpoints**

```python
# API routes for frontend access
@router.get("/api/v1/competitors/intelligence/search")
async def search_competitor_intelligence(
    query: str = Query(..., description="Search query"),
    limit: int = Query(20, description="Result limit"),
    days_back: int = Query(30, description="Days to look back")
):
    """Search competitor intelligence for frontend"""
    try:
        service = create_competitor_intelligence_service()
        results = await service.search_intelligence(
            query=query,
            limit=limit,
            days_back=days_back
        )
        
        return {
            "results": results,
            "query": query,
            "total": len(results),
            "timestamp": datetime.now(UTC).isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/v1/competitors/analytics/threat-analysis")
async def get_threat_analysis():
    """Get comprehensive threat analysis"""
    try:
        service = create_competitor_intelligence_service()
        analysis = await service.get_threat_analysis()
        
        return {
            "analysis": analysis,
            "timestamp": datetime.now(UTC).isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

## 🔄 COMPLETE DATA FLOW SUMMARY

### **1. Data Ingestion:**
- **Sources:** Web scraping, API feeds, manual input, social media monitoring
- **Processing:** Text embedding generation (768-dimensional vectors)
- **Storage:** Qdrant vector database with rich metadata

### **2. Storage Architecture:**
- **Collections:** 
  - `competitor_profiles` - Company information and threat assessment
  - `competitor_intelligence` - Intelligence items with impact scoring
- **Features:** Vector similarity search, metadata filtering, time-based queries

### **3. Retrieval Methods:**
- **Semantic Search:** Vector similarity matching for natural language queries
- **Filtered Search:** Competitor-specific, type-specific, time-based filtering
- **Analytics:** Threat analysis, intelligence summaries, trend analysis

### **4. AI Orchestrator Integration:**
- **Memory Service:** Unified access through primary memory service
- **Business Intelligence:** Integration with broader business intelligence layer
- **Context Enrichment:** Multi-source data aggregation for comprehensive responses

### **5. Chat Interface Access:**
- **Natural Language Processing:** Intent detection for competitor queries
- **Contextual Responses:** Rich responses with intelligence summaries, threat analysis, and recommendations
- **Real-time Data:** Fresh intelligence items and current threat assessments

### **6. Frontend Display:**
- **External Intelligence Monitor:** Real-time dashboard with competitor alerts
- **API Integration:** RESTful endpoints with real-time updates
- **Interactive Features:** Search, filtering, drill-down capabilities

---

## 🎯 EXAMPLE USAGE SCENARIOS

### **Scenario 1: CEO asks "What are our competitors doing this week?"**

**Flow:**
1. Natural language query processed by AI orchestrator
2. Intent detection identifies competitor intelligence request
3. Search recent intelligence (last 7 days) across all competitors
4. Aggregate and prioritize by impact score
5. Generate contextual response with insights and recommendations
6. Display in chat with source citations and confidence scores

**Sample Response:**
```
🎯 **Competitor Intelligence - This Week**

📊 **Activity Overview:**
- 12 intelligence items from 6 competitors
- 3 high-impact developments identified
- 2 new product launches detected

🔍 **Key Developments:**
• **TechCorp launched AI Copilot v2.0** (Impact: 8.5/10)
  Advanced natural language interface for property management
  Source: Company blog | Confidence: 95%

• **PropAI raised $15M Series A** (Impact: 7.2/10)
  Funding round led by Andreessen Horowitz
  Source: TechCrunch | Confidence: 90%

🎯 **Recommendations:**
- Analyze TechCorp's new AI features for competitive response
- Monitor PropAI's expansion plans post-funding
- Track pricing changes from funded competitors
```

### **Scenario 2: "Show me our biggest threats"**

**Flow:**
1. Query routed to threat analysis function
2. Retrieve all competitor profiles with threat levels
3. Calculate threat distribution and top threats
4. Generate comprehensive threat assessment
5. Include market share and growth rate analysis

### **Scenario 3: Dashboard real-time monitoring**

**Flow:**
1. WebSocket connection streams real-time updates
2. New intelligence items automatically processed and embedded
3. Dashboard receives updates every 30 seconds
4. Alerts generated for high-impact intelligence (impact score > 7)
5. Executive notifications for critical threats (threat level > 8)

---

This comprehensive flow ensures that competitor intelligence is seamlessly integrated throughout Sophia AI, providing real-time, contextual, and actionable insights through both chat interface and dashboard visualizations.
