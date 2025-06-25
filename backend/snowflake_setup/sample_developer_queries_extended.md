# 📊 **EXTENDED SAMPLE DEVELOPER QUERIES**
## **Slack, Linear & Foundational Knowledge Base Integration**

---

## **🗣️ SLACK KNOWLEDGE QUERIES**

### **1. Slack Conversation Analysis**

#### **Find High-Value Business Conversations**
```sql
-- Find Slack conversations with high business value
SELECT 
    conv.CONVERSATION_TITLE,
    sc.CHANNEL_NAME,
    conv.PARTICIPANT_COUNT,
    conv.BUSINESS_VALUE_SCORE,
    conv.CONVERSATION_SUMMARY,
    conv.KEY_TOPICS,
    conv.DECISIONS_MADE,
    conv.ACTION_ITEMS
FROM SLACK_DATA.STG_SLACK_CONVERSATIONS conv
JOIN SLACK_DATA.STG_SLACK_CHANNELS sc ON conv.CHANNEL_ID = sc.CHANNEL_ID
WHERE conv.BUSINESS_VALUE_SCORE > 0.8
ORDER BY conv.BUSINESS_VALUE_SCORE DESC
LIMIT 20;
```

#### **Semantic Search Across Slack Conversations**
```sql
-- Vector search for Slack conversations about competitors
SELECT 
    conv.CONVERSATION_TITLE,
    sc.CHANNEL_NAME,
    conv.CONVERSATION_SUMMARY,
    VECTOR_COSINE_SIMILARITY(
        conv.AI_MEMORY_EMBEDDING, 
        SNOWFLAKE.CORTEX.EMBED_TEXT('e5-base-v2', 'competitor analysis pricing strategy')
    ) as similarity_score
FROM SLACK_DATA.STG_SLACK_CONVERSATIONS conv
JOIN SLACK_DATA.STG_SLACK_CHANNELS sc ON conv.CHANNEL_ID = sc.CHANNEL_ID
WHERE conv.AI_MEMORY_EMBEDDING IS NOT NULL
ORDER BY similarity_score DESC
LIMIT 10;
```

#### **Customer Feedback from Slack**
```sql
-- Extract customer feedback discussions from Slack
SELECT 
    conv.CONVERSATION_TITLE,
    sc.CHANNEL_NAME,
    conv.CONVERSATION_SUMMARY,
    conv.MENTIONS_CUSTOMERS,
    conv.SENTIMENT_SCORE,
    ins.INSIGHT_DESCRIPTION
FROM SLACK_DATA.STG_SLACK_CONVERSATIONS conv
JOIN SLACK_DATA.STG_SLACK_CHANNELS sc ON conv.CHANNEL_ID = sc.CHANNEL_ID
LEFT JOIN SLACK_DATA.SLACK_KNOWLEDGE_INSIGHTS ins ON conv.CONVERSATION_ID = ins.CONVERSATION_ID
WHERE conv.MENTIONS_CUSTOMERS IS NOT NULL
AND ins.INSIGHT_TYPE = 'customer_feedback'
ORDER BY conv.SENTIMENT_SCORE DESC;
```

### **2. Slack Channel Analytics**

#### **Most Valuable Channels for Knowledge**
```sql
-- Rank channels by knowledge value
SELECT 
    sc.CHANNEL_NAME,
    sc.BUSINESS_FUNCTION,
    COUNT(DISTINCT conv.CONVERSATION_ID) as conversation_count,
    AVG(conv.BUSINESS_VALUE_SCORE) as avg_business_value,
    COUNT(DISTINCT ins.INSIGHT_ID) as insights_generated,
    sc.KNOWLEDGE_VALUE_SCORE
FROM SLACK_DATA.STG_SLACK_CHANNELS sc
LEFT JOIN SLACK_DATA.STG_SLACK_CONVERSATIONS conv ON sc.CHANNEL_ID = conv.CHANNEL_ID
LEFT JOIN SLACK_DATA.SLACK_KNOWLEDGE_INSIGHTS ins ON conv.CONVERSATION_ID = ins.CONVERSATION_ID
GROUP BY sc.CHANNEL_NAME, sc.BUSINESS_FUNCTION, sc.KNOWLEDGE_VALUE_SCORE
ORDER BY sc.KNOWLEDGE_VALUE_SCORE DESC, insights_generated DESC;
```

#### **Team Communication Patterns**
```sql
-- Analyze team communication effectiveness
SELECT 
    su.DEPARTMENT,
    COUNT(DISTINCT sm.MESSAGE_ID) as message_count,
    COUNT(DISTINCT sm.CONVERSATION_ID) as conversation_count,
    AVG(sm.IMPORTANCE_SCORE) as avg_message_importance,
    COUNT(DISTINCT CASE WHEN sm.CONTAINS_ACTION_ITEMS = TRUE THEN sm.MESSAGE_ID END) as action_items_count
FROM SLACK_DATA.STG_SLACK_USERS su
JOIN SLACK_DATA.STG_SLACK_MESSAGES sm ON su.USER_ID = sm.USER_ID
WHERE sm.MESSAGE_DATETIME >= DATEADD('week', -4, CURRENT_DATE())
GROUP BY su.DEPARTMENT
ORDER BY avg_message_importance DESC;
```

---

## **🎯 LINEAR DEVELOPMENT QUERIES**

### **1. Linear Issue Analysis**

#### **Development Velocity by Project**
```sql
-- Calculate team velocity and cycle times
SELECT 
    PROJECT_NAME,
    COUNT(*) as total_issues,
    COUNT(CASE WHEN STATUS = 'Done' THEN 1 END) as completed_issues,
    COUNT(CASE WHEN STATUS = 'Done' THEN 1 END)::FLOAT / COUNT(*) * 100 as completion_rate,
    AVG(CASE WHEN CYCLE_TIME_DAYS IS NOT NULL THEN CYCLE_TIME_DAYS END) as avg_cycle_time,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY CYCLE_TIME_DAYS) as median_cycle_time
FROM LINEAR_DATA.STG_LINEAR_ISSUES
WHERE CREATED_AT >= DATEADD('month', -3, CURRENT_DATE())
GROUP BY PROJECT_NAME
ORDER BY completion_rate DESC;
```

#### **High-Priority Issue Tracking**
```sql
-- Track urgent and high priority issues
SELECT 
    ISSUE_TITLE,
    PROJECT_NAME,
    PRIORITY,
    STATUS,
    ASSIGNEE_NAME,
    DATEDIFF('day', CREATED_AT, CURRENT_DATE()) as age_days,
    LABELS,
    CASE 
        WHEN PRIORITY = 'Urgent' AND age_days > 3 THEN 'OVERDUE'
        WHEN PRIORITY = 'High' AND age_days > 7 THEN 'ATTENTION_NEEDED'
        ELSE 'ON_TRACK'
    END as urgency_status
FROM LINEAR_DATA.STG_LINEAR_ISSUES
WHERE PRIORITY IN ('Urgent', 'High')
AND STATUS NOT IN ('Done', 'Canceled')
ORDER BY 
    CASE PRIORITY WHEN 'Urgent' THEN 1 WHEN 'High' THEN 2 END,
    age_days DESC;
```

#### **Semantic Search for Linear Issues**
```sql
-- Vector search for Linear issues about specific features
SELECT 
    ISSUE_TITLE,
    PROJECT_NAME,
    ISSUE_DESCRIPTION,
    PRIORITY,
    STATUS,
    VECTOR_COSINE_SIMILARITY(
        AI_MEMORY_EMBEDDING, 
        SNOWFLAKE.CORTEX.EMBED_TEXT('e5-base-v2', 'payment processing API integration')
    ) as similarity_score
FROM LINEAR_DATA.STG_LINEAR_ISSUES
WHERE AI_MEMORY_EMBEDDING IS NOT NULL
ORDER BY similarity_score DESC
LIMIT 15;
```

### **2. Linear Project Management**

#### **Sprint Performance Analysis**
```sql
-- Analyze sprint performance and trends
WITH sprint_data AS (
    SELECT 
        PROJECT_NAME,
        DATE_TRUNC('week', CREATED_AT) as sprint_week,
        COUNT(*) as issues_created,
        COUNT(CASE WHEN STATUS = 'Done' THEN 1 END) as issues_completed,
        AVG(CYCLE_TIME_DAYS) as avg_cycle_time
    FROM LINEAR_DATA.STG_LINEAR_ISSUES
    WHERE CREATED_AT >= DATEADD('week', -8, CURRENT_DATE())
    GROUP BY PROJECT_NAME, sprint_week
)
SELECT 
    PROJECT_NAME,
    sprint_week,
    issues_created,
    issues_completed,
    issues_completed::FLOAT / NULLIF(issues_created, 0) * 100 as completion_rate,
    avg_cycle_time,
    LAG(issues_completed) OVER (PARTITION BY PROJECT_NAME ORDER BY sprint_week) as prev_completed,
    issues_completed - LAG(issues_completed) OVER (PARTITION BY PROJECT_NAME ORDER BY sprint_week) as velocity_change
FROM sprint_data
ORDER BY PROJECT_NAME, sprint_week;
```

#### **Feature Request Prioritization**
```sql
-- Analyze feature requests and their business impact
SELECT 
    ISSUE_TITLE,
    PROJECT_NAME,
    PRIORITY,
    ARRAY_TO_STRING(LABELS, ', ') as labels,
    BUSINESS_VALUE_SCORE,
    CUSTOMER_IMPACT_SCORE,
    EFFORT_ESTIMATE,
    BUSINESS_VALUE_SCORE / NULLIF(EFFORT_ESTIMATE, 0) as value_effort_ratio,
    CREATED_AT
FROM LINEAR_DATA.STG_LINEAR_ISSUES
WHERE ARRAY_CONTAINS('feature'::VARIANT, LABELS)
OR ARRAY_CONTAINS('enhancement'::VARIANT, LABELS)
ORDER BY value_effort_ratio DESC, BUSINESS_VALUE_SCORE DESC;
```

---

## **🏢 FOUNDATIONAL KNOWLEDGE QUERIES**

### **1. Employee Knowledge**

#### **Team Expertise Mapping**
```sql
-- Map team skills and expertise
SELECT 
    DEPARTMENT,
    TEAM,
    COUNT(*) as team_size,
    ARRAY_AGG(DISTINCT UNNEST(PRIMARY_SKILLS)) as team_skills,
    AVG(TENURE_YEARS) as avg_tenure,
    COUNT(CASE WHEN EMPLOYEE_LEVEL LIKE '%Manager%' THEN 1 END) as managers_count
FROM FOUNDATIONAL_KNOWLEDGE.EMPLOYEES
WHERE EMPLOYMENT_STATUS = 'Active'
GROUP BY DEPARTMENT, TEAM
ORDER BY team_size DESC;
```

#### **Semantic Search for Employee Expertise**
```sql
-- Find employees with specific skills using vector search
SELECT 
    FULL_NAME,
    JOB_TITLE,
    DEPARTMENT,
    PRIMARY_SKILLS,
    VECTOR_COSINE_SIMILARITY(
        AI_MEMORY_EMBEDDING, 
        SNOWFLAKE.CORTEX.EMBED_TEXT('e5-base-v2', 'Python machine learning data science')
    ) as skill_match_score
FROM FOUNDATIONAL_KNOWLEDGE.EMPLOYEES
WHERE AI_MEMORY_EMBEDDING IS NOT NULL
AND EMPLOYMENT_STATUS = 'Active'
ORDER BY skill_match_score DESC
LIMIT 10;
```

### **2. Customer Intelligence**

#### **Customer Segmentation Analysis**
```sql
-- Analyze customer segments and characteristics
SELECT 
    CUSTOMER_TIER,
    INDUSTRY,
    COUNT(*) as customer_count,
    COUNT(CASE WHEN CUSTOMER_STATUS = 'Active' THEN 1 END) as active_customers,
    ARRAY_AGG(DISTINCT COMPANY_SIZE) as company_sizes,
    ARRAY_AGG(DISTINCT ANNUAL_REVENUE_RANGE) as revenue_ranges
FROM FOUNDATIONAL_KNOWLEDGE.CUSTOMERS
GROUP BY CUSTOMER_TIER, INDUSTRY
ORDER BY customer_count DESC;
```

#### **Customer-Product Affinity**
```sql
-- Analyze which products appeal to which customer segments
WITH customer_product_context AS (
    SELECT 
        c.CUSTOMER_TIER,
        c.INDUSTRY,
        c.COMPANY_SIZE,
        p.PRODUCT_CATEGORY,
        p.TARGET_CUSTOMER_SEGMENT,
        VECTOR_COSINE_SIMILARITY(c.AI_MEMORY_EMBEDDING, p.AI_MEMORY_EMBEDDING) as affinity_score
    FROM FOUNDATIONAL_KNOWLEDGE.CUSTOMERS c
    CROSS JOIN FOUNDATIONAL_KNOWLEDGE.PRODUCTS_SERVICES p
    WHERE c.AI_MEMORY_EMBEDDING IS NOT NULL 
    AND p.AI_MEMORY_EMBEDDING IS NOT NULL
)
SELECT 
    CUSTOMER_TIER,
    INDUSTRY,
    PRODUCT_CATEGORY,
    AVG(affinity_score) as avg_affinity,
    COUNT(*) as customer_count
FROM customer_product_context
WHERE affinity_score > 0.7
GROUP BY CUSTOMER_TIER, INDUSTRY, PRODUCT_CATEGORY
ORDER BY avg_affinity DESC;
```

### **3. Competitive Intelligence**

#### **Competitive Landscape Analysis**
```sql
-- Analyze competitive positioning
SELECT 
    COMPETITIVE_TIER,
    MARKET_SEGMENT,
    COUNT(*) as competitor_count,
    AVG(THREAT_LEVEL_NUMERIC) as avg_threat_level,
    AVG(MARKET_SHARE_ESTIMATE) as avg_market_share,
    ARRAY_AGG(COMPANY_NAME) as competitors
FROM FOUNDATIONAL_KNOWLEDGE.COMPETITORS
GROUP BY COMPETITIVE_TIER, MARKET_SEGMENT
ORDER BY avg_threat_level DESC, avg_market_share DESC;
```

#### **Competitive Feature Gap Analysis**
```sql
-- Compare our products against competitor strengths
SELECT 
    p.PRODUCT_NAME,
    p.PRODUCT_CATEGORY,
    c.COMPANY_NAME as competitor,
    c.COMPETITIVE_TIER,
    ARRAY_TO_STRING(c.STRENGTHS, ', ') as competitor_strengths,
    ARRAY_TO_STRING(c.WEAKNESSES, ', ') as competitor_weaknesses,
    VECTOR_COSINE_SIMILARITY(p.AI_MEMORY_EMBEDDING, c.AI_MEMORY_EMBEDDING) as competitive_overlap
FROM FOUNDATIONAL_KNOWLEDGE.PRODUCTS_SERVICES p
CROSS JOIN FOUNDATIONAL_KNOWLEDGE.COMPETITORS c
WHERE p.PRODUCT_STATUS = 'Active'
AND c.THREAT_LEVEL IN ('High', 'Medium')
AND competitive_overlap > 0.6
ORDER BY competitive_overlap DESC;
```

---

## **📚 KNOWLEDGE BASE QUERIES**

### **1. Knowledge Article Management**

#### **Knowledge Article Effectiveness**
```sql
-- Analyze knowledge article usage and effectiveness
SELECT 
    ARTICLE_CATEGORY,
    COUNT(*) as article_count,
    AVG(ARTICLE_QUALITY_SCORE) as avg_quality,
    COUNT(CASE WHEN ARTICLE_STATUS = 'Published' THEN 1 END) as published_count,
    COUNT(CASE WHEN LAST_ACCESSED_DATE >= DATEADD('month', -1, CURRENT_DATE()) THEN 1 END) as recently_accessed
FROM KNOWLEDGE_BASE.KB_ARTICLES
GROUP BY ARTICLE_CATEGORY
ORDER BY avg_quality DESC, recently_accessed DESC;
```

#### **Knowledge Gap Analysis**
```sql
-- Identify knowledge gaps using semantic search
WITH common_queries AS (
    SELECT DISTINCT
        'customer onboarding' as query_topic UNION ALL
    SELECT 'payment processing troubleshooting' UNION ALL
    SELECT 'API integration guide' UNION ALL
    SELECT 'security best practices' UNION ALL
    SELECT 'product feature comparison'
)
SELECT 
    cq.query_topic,
    COUNT(ka.ARTICLE_ID) as relevant_articles,
    MAX(VECTOR_COSINE_SIMILARITY(
        ka.AI_MEMORY_EMBEDDING, 
        SNOWFLAKE.CORTEX.EMBED_TEXT('e5-base-v2', cq.query_topic)
    )) as best_match_score,
    CASE 
        WHEN COUNT(ka.ARTICLE_ID) = 0 THEN 'CRITICAL_GAP'
        WHEN best_match_score < 0.7 THEN 'CONTENT_GAP'
        ELSE 'ADEQUATE_COVERAGE'
    END as gap_status
FROM common_queries cq
LEFT JOIN KNOWLEDGE_BASE.KB_ARTICLES ka ON 
    VECTOR_COSINE_SIMILARITY(
        ka.AI_MEMORY_EMBEDDING, 
        SNOWFLAKE.CORTEX.EMBED_TEXT('e5-base-v2', cq.query_topic)
    ) > 0.5
WHERE ka.ARTICLE_STATUS = 'Published' OR ka.ARTICLE_ID IS NULL
GROUP BY cq.query_topic
ORDER BY gap_status, best_match_score;
```

### **2. Cross-Source Knowledge Integration**

#### **Unified Knowledge Search**
```sql
-- Search across all knowledge sources for comprehensive insights
WITH unified_knowledge AS (
    -- Foundational Knowledge
    SELECT 
        'FOUNDATIONAL' as source_type,
        'EMPLOYEE' as knowledge_type,
        FULL_NAME as title,
        JOB_TITLE || ' - ' || DEPARTMENT as description,
        AI_MEMORY_EMBEDDING,
        UPDATED_AT
    FROM FOUNDATIONAL_KNOWLEDGE.EMPLOYEES
    WHERE AI_MEMORY_EMBEDDING IS NOT NULL
    
    UNION ALL
    
    -- Slack Conversations
    SELECT 
        'SLACK' as source_type,
        'CONVERSATION' as knowledge_type,
        CONVERSATION_TITLE as title,
        CONVERSATION_SUMMARY as description,
        AI_MEMORY_EMBEDDING,
        UPDATED_AT
    FROM SLACK_DATA.STG_SLACK_CONVERSATIONS
    WHERE AI_MEMORY_EMBEDDING IS NOT NULL
    
    UNION ALL
    
    -- Linear Issues
    SELECT 
        'LINEAR' as source_type,
        'ISSUE' as knowledge_type,
        ISSUE_TITLE as title,
        ISSUE_DESCRIPTION as description,
        AI_MEMORY_EMBEDDING,
        UPDATED_AT
    FROM LINEAR_DATA.STG_LINEAR_ISSUES
    WHERE AI_MEMORY_EMBEDDING IS NOT NULL
    
    UNION ALL
    
    -- Knowledge Base Articles
    SELECT 
        'KNOWLEDGE_BASE' as source_type,
        'ARTICLE' as knowledge_type,
        ARTICLE_TITLE as title,
        ARTICLE_SUMMARY as description,
        AI_MEMORY_EMBEDDING,
        UPDATED_AT
    FROM KNOWLEDGE_BASE.KB_ARTICLES
    WHERE AI_MEMORY_EMBEDDING IS NOT NULL
)
SELECT 
    source_type,
    knowledge_type,
    title,
    description,
    VECTOR_COSINE_SIMILARITY(
        AI_MEMORY_EMBEDDING, 
        SNOWFLAKE.CORTEX.EMBED_TEXT('e5-base-v2', 'payment processing customer integration')
    ) as relevance_score,
    UPDATED_AT
FROM unified_knowledge
WHERE relevance_score > 0.6
ORDER BY relevance_score DESC, UPDATED_AT DESC
LIMIT 20;
```

#### **Knowledge Cross-References**
```sql
-- Find related knowledge across different sources
WITH slack_customer_discussions AS (
    SELECT 
        CONVERSATION_ID,
        CONVERSATION_TITLE,
        MENTIONS_CUSTOMERS,
        AI_MEMORY_EMBEDDING
    FROM SLACK_DATA.STG_SLACK_CONVERSATIONS
    WHERE ARRAY_SIZE(MENTIONS_CUSTOMERS) > 0
),
related_foundational AS (
    SELECT 
        scd.CONVERSATION_ID,
        scd.CONVERSATION_TITLE,
        fc.COMPANY_NAME,
        fc.CUSTOMER_TIER,
        VECTOR_COSINE_SIMILARITY(scd.AI_MEMORY_EMBEDDING, fc.AI_MEMORY_EMBEDDING) as relationship_strength
    FROM slack_customer_discussions scd
    CROSS JOIN FOUNDATIONAL_KNOWLEDGE.CUSTOMERS fc
    WHERE fc.AI_MEMORY_EMBEDDING IS NOT NULL
)
SELECT 
    CONVERSATION_TITLE,
    COMPANY_NAME,
    CUSTOMER_TIER,
    relationship_strength,
    CASE 
        WHEN relationship_strength > 0.8 THEN 'STRONG_RELATION'
        WHEN relationship_strength > 0.6 THEN 'MODERATE_RELATION'
        ELSE 'WEAK_RELATION'
    END as relation_type
FROM related_foundational
WHERE relationship_strength > 0.6
ORDER BY relationship_strength DESC;
```

---

## **🔍 ADVANCED ANALYTICS QUERIES**

### **1. Business Intelligence Insights**

#### **Cross-Source Business Impact Analysis**
```sql
-- Analyze business impact across all knowledge sources
WITH business_insights AS (
    -- High-value Slack conversations
    SELECT 
        'Slack Conversation' as insight_type,
        CONVERSATION_TITLE as title,
        BUSINESS_VALUE_SCORE as impact_score,
        'Communication' as category
    FROM SLACK_DATA.STG_SLACK_CONVERSATIONS
    WHERE BUSINESS_VALUE_SCORE > 0.7
    
    UNION ALL
    
    -- Critical Linear issues
    SELECT 
        'Linear Issue' as insight_type,
        ISSUE_TITLE as title,
        CASE PRIORITY 
            WHEN 'Urgent' THEN 1.0 
            WHEN 'High' THEN 0.8 
            WHEN 'Medium' THEN 0.6 
            ELSE 0.4 
        END as impact_score,
        'Development' as category
    FROM LINEAR_DATA.STG_LINEAR_ISSUES
    WHERE STATUS NOT IN ('Done', 'Canceled')
    
    UNION ALL
    
    -- Strategic customers
    SELECT 
        'Customer' as insight_type,
        COMPANY_NAME as title,
        CASE CUSTOMER_TIER 
            WHEN 'Strategic' THEN 1.0 
            WHEN 'Key' THEN 0.8 
            WHEN 'Standard' THEN 0.6 
            ELSE 0.4 
        END as impact_score,
        'Customer' as category
    FROM FOUNDATIONAL_KNOWLEDGE.CUSTOMERS
    WHERE CUSTOMER_STATUS = 'Active'
)
SELECT 
    category,
    insight_type,
    COUNT(*) as count,
    AVG(impact_score) as avg_impact,
    MAX(impact_score) as max_impact,
    ARRAY_AGG(title) WITHIN GROUP (ORDER BY impact_score DESC) as top_items
FROM business_insights
GROUP BY category, insight_type
ORDER BY avg_impact DESC;
```

#### **Knowledge Utilization Trends**
```sql
-- Track knowledge creation and utilization trends
SELECT 
    DATE_TRUNC('week', created_date) as week,
    source_type,
    COUNT(*) as items_created,
    SUM(COUNT(*)) OVER (PARTITION BY source_type ORDER BY week) as cumulative_count
FROM (
    SELECT CREATED_AT::DATE as created_date, 'Slack' as source_type
    FROM SLACK_DATA.STG_SLACK_CONVERSATIONS
    
    UNION ALL
    
    SELECT CREATED_AT::DATE as created_date, 'Linear' as source_type
    FROM LINEAR_DATA.STG_LINEAR_ISSUES
    
    UNION ALL
    
    SELECT CREATED_AT::DATE as created_date, 'Foundational' as source_type
    FROM FOUNDATIONAL_KNOWLEDGE.EMPLOYEES
    
    UNION ALL
    
    SELECT CREATED_AT::DATE as created_date, 'Knowledge_Base' as source_type
    FROM KNOWLEDGE_BASE.KB_ARTICLES
) knowledge_items
WHERE created_date >= DATEADD('month', -6, CURRENT_DATE())
GROUP BY week, source_type
ORDER BY week, source_type;
```

---

## **🚀 PERFORMANCE OPTIMIZATION QUERIES**

### **1. Embedding Quality Assessment**

#### **Embedding Coverage Analysis**
```sql
-- Check embedding coverage across all tables
SELECT 
    'Slack Conversations' as table_name,
    COUNT(*) as total_records,
    COUNT(AI_MEMORY_EMBEDDING) as embedded_records,
    COUNT(AI_MEMORY_EMBEDDING)::FLOAT / COUNT(*) * 100 as coverage_percentage
FROM SLACK_DATA.STG_SLACK_CONVERSATIONS

UNION ALL

SELECT 
    'Linear Issues' as table_name,
    COUNT(*) as total_records,
    COUNT(AI_MEMORY_EMBEDDING) as embedded_records,
    COUNT(AI_MEMORY_EMBEDDING)::FLOAT / COUNT(*) * 100 as coverage_percentage
FROM LINEAR_DATA.STG_LINEAR_ISSUES

UNION ALL

SELECT 
    'Foundational Employees' as table_name,
    COUNT(*) as total_records,
    COUNT(AI_MEMORY_EMBEDDING) as embedded_records,
    COUNT(AI_MEMORY_EMBEDDING)::FLOAT / COUNT(*) * 100 as coverage_percentage
FROM FOUNDATIONAL_KNOWLEDGE.EMPLOYEES

UNION ALL

SELECT 
    'Knowledge Articles' as table_name,
    COUNT(*) as total_records,
    COUNT(AI_MEMORY_EMBEDDING) as embedded_records,
    COUNT(AI_MEMORY_EMBEDDING)::FLOAT / COUNT(*) * 100 as coverage_percentage
FROM KNOWLEDGE_BASE.KB_ARTICLES

ORDER BY coverage_percentage DESC;
```

#### **Vector Search Performance Test**
```sql
-- Test vector search performance across different data sources
WITH search_terms AS (
    SELECT 'customer payment processing' as search_term UNION ALL
    SELECT 'team collaboration tools' UNION ALL
    SELECT 'product feature development' UNION ALL
    SELECT 'competitive market analysis'
),
search_results AS (
    SELECT 
        st.search_term,
        'Slack' as source,
        COUNT(*) as result_count,
        AVG(VECTOR_COSINE_SIMILARITY(
            sc.AI_MEMORY_EMBEDDING, 
            SNOWFLAKE.CORTEX.EMBED_TEXT('e5-base-v2', st.search_term)
        )) as avg_similarity
    FROM search_terms st
    CROSS JOIN SLACK_DATA.STG_SLACK_CONVERSATIONS sc
    WHERE sc.AI_MEMORY_EMBEDDING IS NOT NULL
    AND VECTOR_COSINE_SIMILARITY(
        sc.AI_MEMORY_EMBEDDING, 
        SNOWFLAKE.CORTEX.EMBED_TEXT('e5-base-v2', st.search_term)
    ) > 0.5
    GROUP BY st.search_term
    
    UNION ALL
    
    SELECT 
        st.search_term,
        'Linear' as source,
        COUNT(*) as result_count,
        AVG(VECTOR_COSINE_SIMILARITY(
            li.AI_MEMORY_EMBEDDING, 
            SNOWFLAKE.CORTEX.EMBED_TEXT('e5-base-v2', st.search_term)
        )) as avg_similarity
    FROM search_terms st
    CROSS JOIN LINEAR_DATA.STG_LINEAR_ISSUES li
    WHERE li.AI_MEMORY_EMBEDDING IS NOT NULL
    AND VECTOR_COSINE_SIMILARITY(
        li.AI_MEMORY_EMBEDDING, 
        SNOWFLAKE.CORTEX.EMBED_TEXT('e5-base-v2', st.search_term)
    ) > 0.5
    GROUP BY st.search_term
)
SELECT 
    search_term,
    source,
    result_count,
    ROUND(avg_similarity, 3) as avg_similarity_score
FROM search_results
ORDER BY search_term, avg_similarity_score DESC;
```

---

## **📝 QUERY USAGE GUIDELINES**

### **Best Practices**
1. **Always filter by date ranges** for performance on large datasets
2. **Use vector similarity thresholds > 0.5** for meaningful semantic search results
3. **Include LIMIT clauses** when exploring data to avoid large result sets
4. **Leverage indexes** on frequently queried columns (ID, date, status fields)
5. **Use EXPLAIN PLAN** to optimize complex queries

### **Performance Tips**
- Vector similarity calculations are compute-intensive; use appropriate thresholds
- Cache frequently used embeddings for repeated searches
- Use materialized views for complex aggregations
- Consider partitioning large tables by date for better performance

### **Security Considerations**
- Always validate user permissions before executing queries
- Use parameterized queries to prevent SQL injection
- Log all data access for audit purposes
- Respect data privacy and access controls

---

## **🎯 CONCLUSION**

These extended sample queries demonstrate the powerful capabilities of the integrated Slack, Linear, and Foundational Knowledge Base system. They enable:

- **Cross-source knowledge discovery** through semantic search
- **Business intelligence insights** from communication and development data
- **Performance monitoring** and optimization opportunities
- **Comprehensive analytics** across all organizational knowledge sources

The queries serve as templates that can be adapted for specific business needs and use cases within the Sophia AI platform. 