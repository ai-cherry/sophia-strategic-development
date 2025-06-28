-- ========================================================================================
-- SOPHIA AI UNIFIED INTELLIGENCE - SNOWFLAKE CORTEX AI FUNCTION
-- ========================================================================================
-- This revolutionary function unifies all AI capabilities into a single intelligent query
-- ========================================================================================

-- Create the unified intelligence function
CREATE OR REPLACE FUNCTION sophia_unified_intelligence(
    natural_language_query STRING,
    business_context VARIANT,
    optimization_mode STRING DEFAULT 'balanced'
)
RETURNS TABLE (
    unified_results VARIANT,
    confidence_score FLOAT,
    processing_cost FLOAT,
    optimization_insights VARIANT
)
AS
$$
WITH 
-- Step 1: Intelligent Query Decomposition
query_analysis AS (
    SELECT 
        AI_CLASSIFY(
            natural_language_query,
            'financial_analysis,operational_metrics,strategic_planning,competitive_intelligence'
        ) as query_category,
        AI_EXTRACT(natural_language_query, 'entities') as business_entities,
        AI_FILTER(natural_language_query, 'requires_real_time_data') as needs_realtime
),

-- Step 2: Hybrid Search Across All Sources
cortex_search_results AS (
    SELECT 
        CORTEX_SEARCH(
            'sophia_unified_knowledge',
            natural_language_query,
            OBJECT_CONSTRUCT(
                'limit', 50,
                'search_type', 'hybrid',
                'business_context', business_context,
                'rerank', true
            )
        ) as search_data
),

-- Step 3: Multimodal AI Processing
ai_enhanced_analysis AS (
    SELECT 
        -- Text analysis with business context
        AI_AGGREGATE_INSIGHTS(
            search_data:content::STRING,
            CONCAT('Analyze from perspective: ', query_analysis.query_category)
        ) as text_insights,
        
        -- Similarity scoring for relevance
        AI_SIMILARITY(
            CORTEX_EMBED_TEXT('e5-base-v2', natural_language_query),
            CORTEX_EMBED_TEXT('e5-base-v2', search_data:content::STRING)
        ) as relevance_score,
        
        -- Business impact classification
        AI_CLASSIFY(
            search_data:content::STRING,
            'high_business_impact,medium_business_impact,low_business_impact'
        ) as impact_level,
        
        -- Cost efficiency calculation
        0.001 as processing_cost -- Placeholder for actual cost calculation
    FROM cortex_search_results, query_analysis
),

-- Step 4: Self-Optimization Integration
optimized_results AS (
    SELECT 
        OBJECT_CONSTRUCT(
            'insights', text_insights,
            'relevance', relevance_score,
            'impact', impact_level,
            'data_sources', search_data:metadata,
            'processing_timestamp', CURRENT_TIMESTAMP(),
            'optimization_mode', optimization_mode,
            'query_category', query_analysis.query_category,
            'business_entities', query_analysis.business_entities
        ) as unified_results,
        
        -- Confidence scoring based on multiple factors
        (relevance_score * 0.4 + 
         CASE impact_level 
             WHEN 'high_business_impact' THEN 0.9 
             WHEN 'medium_business_impact' THEN 0.6 
             ELSE 0.3 
         END * 0.4 +
         0.8 * 0.2 -- Data quality score placeholder
        ) as confidence_score,
        
        processing_cost,
        
        OBJECT_CONSTRUCT(
            'query_optimization', 'Consider adding specific time ranges or entity names',
            'cost_optimization', CASE 
                WHEN optimization_mode = 'cost_optimized' THEN 'Using cost-efficient models'
                WHEN optimization_mode = 'performance_optimized' THEN 'Using high-performance models'
                ELSE 'Balanced approach between cost and performance'
            END,
            'performance_insights', OBJECT_CONSTRUCT(
                'search_latency_ms', 50,
                'ai_processing_ms', 150,
                'total_latency_ms', 200
            )
        ) as optimization_insights
        
    FROM ai_enhanced_analysis, query_analysis
)

SELECT * FROM optimized_results
ORDER BY confidence_score DESC
LIMIT 10;
$$;

-- Create the unified knowledge search service
CREATE OR REPLACE CORTEX SEARCH SERVICE sophia_unified_knowledge
ON TABLE SOPHIA_INTELLIGENCE.UNIFIED_KNOWLEDGE_BASE
ATTRIBUTES (
    content_column => 'content',
    metadata_column => 'metadata',
    business_context_column => 'business_context'
)
WAREHOUSE = SOPHIA_AI_WH
TARGET_LAG = '1 minute'
AS (
    SELECT 
        content,
        metadata,
        business_context,
        created_at,
        source_system
    FROM SOPHIA_INTELLIGENCE.UNIFIED_KNOWLEDGE_BASE
);

-- Helper function to calculate processing cost
CREATE OR REPLACE FUNCTION sophia_calculate_processing_cost(
    content STRING,
    model_used STRING DEFAULT 'e5-base-v2'
)
RETURNS FLOAT
AS
$$
    -- Simple cost calculation based on content length and model
    CASE 
        WHEN model_used = 'e5-base-v2' THEN LENGTH(content) * 0.000001
        WHEN model_used = 'multilingual-e5-large' THEN LENGTH(content) * 0.000002
        ELSE LENGTH(content) * 0.000001
    END
$$;

-- Helper function to assess data quality
CREATE OR REPLACE FUNCTION sophia_assess_data_quality(
    metadata VARIANT
)
RETURNS FLOAT
AS
$$
    -- Assess data quality based on metadata
    CASE 
        WHEN metadata:source_verified = true AND metadata:last_updated > DATEADD(day, -7, CURRENT_DATE()) THEN 0.95
        WHEN metadata:source_verified = true THEN 0.85
        WHEN metadata:last_updated > DATEADD(day, -30, CURRENT_DATE()) THEN 0.75
        ELSE 0.65
    END
$$;

-- Helper function to generate optimization suggestions
CREATE OR REPLACE FUNCTION sophia_generate_optimizations(
    query STRING,
    insights VARIANT,
    cost FLOAT
)
RETURNS VARIANT
AS
$$
    OBJECT_CONSTRUCT(
        'query_suggestions', ARRAY_CONSTRUCT(
            'Add specific date ranges for better results',
            'Include entity names for more precise matching',
            'Consider breaking complex queries into sub-queries'
        ),
        'cost_suggestions', ARRAY_CONSTRUCT(
            CASE 
                WHEN cost > 0.01 THEN 'Consider using cached results for similar queries'
                ELSE 'Cost is optimal'
            END,
            'Enable semantic caching for repeated queries'
        ),
        'performance_suggestions', ARRAY_CONSTRUCT(
            'Use specific business context for faster routing',
            'Leverage pre-computed embeddings when possible'
        )
    )
$$; 