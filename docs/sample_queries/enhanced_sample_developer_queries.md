# Enhanced Sample Developer Queries for Sophia AI

## Overview
This document provides comprehensive sample queries for all Sophia AI schemas, including the newly implemented PAYREADY_CORE_SQL, NETSUITE_DATA, PROPERTY_ASSETS, AI_WEB_RESEARCH, and Unified_INTELLIGENCE schemas.

## Security Levels
- **STANDARD**: FOUNDATIONAL_KNOWLEDGE, HUBSPOT_DATA, GONG_DATA, SLACK_DATA
- **EXECUTIVE**: All STANDARD + PAYREADY_CORE_SQL, NETSUITE_DATA, PROPERTY_ASSETS, AI_WEB_RESEARCH
- **Unified_ONLY**: All EXECUTIVE + Unified_INTELLIGENCE (CONFIDENTIAL)

---

## 1. PAYREADY_CORE_SQL Schema Queries

### Payment Transactions Analysis

#### Natural Language Queries:
- "What's our payment volume this month?"
- "Show me failed transactions and their reasons"
- "Analyze payment success rates by property"
- "What's the average transaction amount?"

#### SQL Queries:

```sql
-- Monthly payment volume analysis
SELECT 
    DATE_TRUNC('month', PROCESSING_DATE) as month,
    COUNT(*) as total_transactions,
    SUM(CASE WHEN STATUS = 'COMPLETED' THEN AMOUNT ELSE 0 END) as successful_amount,
    ROUND(COUNT(CASE WHEN STATUS = 'COMPLETED' THEN 1 END) * 100.0 / COUNT(*), 2) as success_rate
FROM PAYREADY_CORE_SQL.PAYMENT_TRANSACTIONS
WHERE PROCESSING_DATE >= CURRENT_DATE - 365
GROUP BY DATE_TRUNC('month', PROCESSING_DATE)
ORDER BY month DESC;

-- Top failure reasons analysis
SELECT 
    FAILURE_REASON,
    COUNT(*) as failure_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
FROM PAYREADY_CORE_SQL.PAYMENT_TRANSACTIONS
WHERE STATUS = 'FAILED' 
AND PROCESSING_DATE >= CURRENT_DATE - 30
GROUP BY FAILURE_REASON
ORDER BY failure_count DESC
LIMIT 10;

-- Payment performance by property
SELECT 
    p.PROPERTY_ID,
    COUNT(pt.TRANSACTION_ID) as transaction_count,
    SUM(pt.AMOUNT) as total_amount,
    AVG(pt.AMOUNT) as avg_amount,
    ROUND(COUNT(CASE WHEN pt.STATUS = 'COMPLETED' THEN 1 END) * 100.0 / COUNT(*), 2) as success_rate
FROM PAYREADY_CORE_SQL.PAYMENT_TRANSACTIONS pt
JOIN PROPERTY_ASSETS.PROPERTIES p ON pt.PROPERTY_ID = p.PROPERTY_ID
WHERE pt.PROCESSING_DATE >= CURRENT_DATE - 90
GROUP BY p.PROPERTY_ID
ORDER BY total_amount DESC;
```

### Customer Features Analysis

#### Natural Language Queries:
- "Which features drive the most revenue?"
- "Show me feature adoption rates"
- "What features improve customer retention?"

#### SQL Queries:

```sql
-- Feature revenue impact analysis
SELECT 
    FEATURE_NAME,
    COUNT(*) as customers_using,
    SUM(MONTHLY_FEE) as monthly_revenue,
    AVG(RETENTION_IMPACT) as avg_retention_impact,
    AVG(CUSTOMER_SATISFACTION_IMPACT) as avg_satisfaction_impact
FROM PAYREADY_CORE_SQL.CUSTOMER_FEATURES
WHERE IS_ENABLED = TRUE
GROUP BY FEATURE_NAME
ORDER BY monthly_revenue DESC;

-- Feature adoption trends
SELECT 
    DATE_TRUNC('month', ACTIVATION_DATE) as month,
    FEATURE_NAME,
    COUNT(*) as new_adoptions
FROM PAYREADY_CORE_SQL.CUSTOMER_FEATURES
WHERE ACTIVATION_DATE >= CURRENT_DATE - 365
GROUP BY DATE_TRUNC('month', ACTIVATION_DATE), FEATURE_NAME
ORDER BY month DESC, new_adoptions DESC;
```

### Business Rules Analysis

#### Natural Language Queries:
- "Show me active business rules"
- "Which rules have the highest impact?"
- "Analyze rule execution performance"

#### SQL Queries:

```sql
-- Business rules performance analysis
SELECT 
    RULE_NAME,
    RULE_CATEGORY,
    EXECUTION_COUNT,
    AVG_EXECUTION_TIME_MS,
    SUCCESS_RATE,
    IMPACT_LEVEL
FROM PAYREADY_CORE_SQL.BUSINESS_RULES
WHERE IS_ACTIVE = TRUE
ORDER BY EXECUTION_COUNT DESC;

-- Rules affecting payments
SELECT 
    RULE_NAME,
    RULE_DESCRIPTION,
    EXECUTION_COUNT,
    SUCCESS_RATE
FROM PAYREADY_CORE_SQL.BUSINESS_RULES
WHERE AFFECTS_PAYMENTS = TRUE
AND IS_ACTIVE = TRUE
ORDER BY EXECUTION_COUNT DESC;
```

---

## 2. NETSUITE_DATA Schema Queries

### Financial Analysis

#### Natural Language Queries:
- "Show me the P&L summary for this quarter"
- "What are our biggest expenses?"
- "Analyze cash flow trends"

#### SQL Queries:

```sql
-- Quarterly P&L summary
SELECT 
    DATE_TRUNC('quarter', TRANSACTION_DATE) as quarter,
    SUM(DEBIT_AMOUNT) as total_debits,
    SUM(CREDIT_AMOUNT) as total_credits,
    SUM(NET_AMOUNT) as net_amount
FROM NETSUITE_DATA.GENERAL_LEDGER
WHERE TRANSACTION_DATE >= CURRENT_DATE - 365
GROUP BY DATE_TRUNC('quarter', TRANSACTION_DATE)
ORDER BY quarter DESC;

-- Expense analysis by category
SELECT 
    er.EXPENSE_CATEGORY,
    COUNT(*) as expense_count,
    SUM(er.AMOUNT) as total_amount,
    AVG(er.AMOUNT) as avg_amount,
    COUNT(DISTINCT er.EMPLOYEE_ID) as employees_submitting
FROM NETSUITE_DATA.EXPENSE_REPORTS er
WHERE er.EXPENSE_DATE >= CURRENT_DATE - 90
GROUP BY er.EXPENSE_CATEGORY
ORDER BY total_amount DESC;

-- Purchase order analysis
SELECT 
    po.VENDOR_NAME,
    COUNT(*) as po_count,
    SUM(po.TOTAL_AMOUNT) as total_amount,
    AVG(DATEDIFF('day', po.ORDER_DATE, po.EXPECTED_DELIVERY_DATE)) as avg_delivery_days
FROM NETSUITE_DATA.PURCHASE_ORDERS po
WHERE po.ORDER_DATE >= CURRENT_DATE - 180
GROUP BY po.VENDOR_NAME
ORDER BY total_amount DESC;
```

### Accounts Payable Analysis

#### Natural Language Queries:
- "Show me outstanding purchase orders"
- "Which vendors do we spend the most with?"
- "Analyze expense approval patterns"

#### SQL Queries:

```sql
-- Outstanding purchase orders
SELECT 
    PO_NUMBER,
    VENDOR_NAME,
    TOTAL_AMOUNT,
    ORDER_DATE,
    EXPECTED_DELIVERY_DATE,
    STATUS
FROM NETSUITE_DATA.PURCHASE_ORDERS
WHERE STATUS IN ('PENDING', 'APPROVED', 'PARTIALLY_RECEIVED')
ORDER BY TOTAL_AMOUNT DESC;

-- Vendor spending analysis
SELECT 
    VENDOR_NAME,
    COUNT(*) as po_count,
    SUM(TOTAL_AMOUNT) as total_spent,
    AVG(TOTAL_AMOUNT) as avg_po_amount,
    MAX(ORDER_DATE) as last_order_date
FROM NETSUITE_DATA.PURCHASE_ORDERS
WHERE ORDER_DATE >= CURRENT_DATE - 365
GROUP BY VENDOR_NAME
ORDER BY total_spent DESC;
```

---

## 3. PROPERTY_ASSETS Schema Queries

### Property Portfolio Analysis

#### Natural Language Queries:
- "What's our overall occupancy rate?"
- "Show me property performance by type"
- "Which properties generate the most revenue?"

#### SQL Queries:

```sql
-- Portfolio overview
SELECT 
    COUNT(*) as total_properties,
    SUM(TOTAL_UNITS) as total_units,
    SUM(OCCUPIED_UNITS) as occupied_units,
    ROUND(AVG(OCCUPANCY_RATE), 2) as avg_occupancy_rate,
    SUM(MONTHLY_RENT_POTENTIAL) as total_rent_potential,
    SUM(ACTUAL_MONTHLY_RENT) as actual_monthly_rent,
    ROUND((SUM(ACTUAL_MONTHLY_RENT) / SUM(MONTHLY_RENT_POTENTIAL)) * 100, 2) as rent_realization_rate
FROM PROPERTY_ASSETS.PROPERTIES
WHERE PROPERTY_STATUS = 'ACTIVE';

-- Performance by property type
SELECT 
    PROPERTY_TYPE,
    COUNT(*) as property_count,
    SUM(TOTAL_UNITS) as total_units,
    AVG(OCCUPANCY_RATE) as avg_occupancy,
    SUM(ACTUAL_MONTHLY_RENT) as monthly_revenue,
    AVG(PROPERTY_VALUE) as avg_property_value
FROM PROPERTY_ASSETS.PROPERTIES
WHERE PROPERTY_STATUS = 'ACTIVE'
GROUP BY PROPERTY_TYPE
ORDER BY monthly_revenue DESC;

-- Top performing properties
SELECT 
    PROPERTY_NAME,
    ADDRESS,
    PROPERTY_TYPE,
    OCCUPANCY_RATE,
    ACTUAL_MONTHLY_RENT,
    ROUND((ACTUAL_MONTHLY_RENT / MONTHLY_RENT_POTENTIAL) * 100, 2) as rent_efficiency
FROM PROPERTY_ASSETS.PROPERTIES
WHERE PROPERTY_STATUS = 'ACTIVE'
ORDER BY ACTUAL_MONTHLY_RENT DESC
LIMIT 10;
```

### Unit Analysis

#### Natural Language Queries:
- "Show me vacant units"
- "Analyze rent by unit type"
- "Which units have the longest leases?"

#### SQL Queries:

```sql
-- Vacant units analysis
SELECT 
    pu.PROPERTY_ID,
    p.PROPERTY_NAME,
    pu.UNIT_NUMBER,
    pu.UNIT_TYPE,
    pu.MONTHLY_RENT,
    pu.SQUARE_FOOTAGE,
    ROUND(pu.MONTHLY_RENT / pu.SQUARE_FOOTAGE, 2) as rent_per_sqft
FROM PROPERTY_ASSETS.PROPERTY_UNITS pu
JOIN PROPERTY_ASSETS.PROPERTIES p ON pu.PROPERTY_ID = p.PROPERTY_ID
WHERE pu.OCCUPANCY_STATUS = 'VACANT'
ORDER BY pu.MONTHLY_RENT DESC;

-- Rent analysis by unit type
SELECT 
    UNIT_TYPE,
    COUNT(*) as unit_count,
    AVG(MONTHLY_RENT) as avg_rent,
    MIN(MONTHLY_RENT) as min_rent,
    MAX(MONTHLY_RENT) as max_rent,
    AVG(SQUARE_FOOTAGE) as avg_sqft,
    ROUND(AVG(MONTHLY_RENT / SQUARE_FOOTAGE), 2) as avg_rent_per_sqft
FROM PROPERTY_ASSETS.PROPERTY_UNITS
WHERE OCCUPANCY_STATUS = 'OCCUPIED'
GROUP BY UNIT_TYPE
ORDER BY avg_rent DESC;
```

---

## 4. AI_WEB_RESEARCH Schema Queries

### Industry Trends Analysis

#### Natural Language Queries:
- "What are the latest fintech trends?"
- "Show me high-impact industry developments"
- "Which trends are most relevant to our business?"

#### SQL Queries:

```sql
-- High-relevance industry trends
SELECT 
    TREND_TITLE,
    TREND_DESCRIPTION,
    KEY_INSIGHTS,
    RELEVANCE_SCORE,
    BUSINESS_IMPACT_SCORE,
    PUBLICATION_DATE
FROM AI_WEB_RESEARCH.INDUSTRY_TRENDS
WHERE RELEVANCE_SCORE > 0.8
AND PUBLICATION_DATE >= CURRENT_DATE - 30
ORDER BY RELEVANCE_SCORE DESC, BUSINESS_IMPACT_SCORE DESC;

-- Trends by category
SELECT 
    TREND_CATEGORY,
    COUNT(*) as trend_count,
    AVG(RELEVANCE_SCORE) as avg_relevance,
    AVG(BUSINESS_IMPACT_SCORE) as avg_impact,
    MAX(PUBLICATION_DATE) as latest_trend
FROM AI_WEB_RESEARCH.INDUSTRY_TRENDS
WHERE PUBLICATION_DATE >= CURRENT_DATE - 90
GROUP BY TREND_CATEGORY
ORDER BY avg_relevance DESC;

-- Geographic trend analysis
SELECT 
    GEOGRAPHIC_SCOPE,
    INDUSTRY_SECTOR,
    COUNT(*) as trend_count,
    AVG(RELEVANCE_SCORE) as avg_relevance
FROM AI_WEB_RESEARCH.INDUSTRY_TRENDS
WHERE PUBLICATION_DATE >= CURRENT_DATE - 60
GROUP BY GEOGRAPHIC_SCOPE, INDUSTRY_SECTOR
ORDER BY trend_count DESC;
```

### Competitive Intelligence

#### Natural Language Queries:
- "Show me high-threat competitive intelligence"
- "Which competitors are expanding into our space?"
- "What opportunities do we see in the market?"

#### SQL Queries:

```sql
-- High-threat competitive intelligence
SELECT 
    COMPETITOR_NAME,
    INTELLIGENCE_SUMMARY,
    THREAT_LEVEL,
    OPPORTUNITY_LEVEL,
    COMPETITIVE_MOAT_IMPACT,
    COLLECTION_DATE
FROM AI_WEB_RESEARCH.COMPETITOR_INTELLIGENCE
WHERE THREAT_LEVEL = 'HIGH'
AND COLLECTION_DATE >= CURRENT_DATE - 60
ORDER BY COMPETITIVE_MOAT_IMPACT DESC;

-- Competitive opportunities
SELECT 
    COMPETITOR_NAME,
    INTELLIGENCE_SUMMARY,
    OPPORTUNITY_LEVEL,
    STRATEGIC_IMPLICATIONS,
    COLLECTION_DATE
FROM AI_WEB_RESEARCH.COMPETITOR_INTELLIGENCE
WHERE OPPORTUNITY_LEVEL IN ('HIGH', 'MEDIUM')
AND COLLECTION_DATE >= CURRENT_DATE - 90
ORDER BY COLLECTION_DATE DESC;
```

### Partnership Opportunities

#### Natural Language Queries:
- "Show me high-fit partnership opportunities"
- "Which partnerships have the highest potential value?"
- "What technology integrations should we consider?"

#### SQL Queries:

```sql
-- High-value partnership opportunities
SELECT 
    PARTNER_NAME,
    OPPORTUNITY_DESCRIPTION,
    PARTNERSHIP_TYPE,
    STRATEGIC_FIT_SCORE,
    POTENTIAL_VALUE,
    IMPLEMENTATION_COMPLEXITY,
    TIMELINE_ESTIMATE
FROM AI_WEB_RESEARCH.PARTNERSHIP_OPPORTUNITIES
WHERE STRATEGIC_FIT_SCORE > 0.8
ORDER BY POTENTIAL_VALUE DESC;

-- Partnership opportunities by type
SELECT 
    PARTNERSHIP_TYPE,
    COUNT(*) as opportunity_count,
    AVG(STRATEGIC_FIT_SCORE) as avg_fit_score,
    SUM(POTENTIAL_VALUE) as total_potential_value,
    AVG(POTENTIAL_VALUE) as avg_potential_value
FROM AI_WEB_RESEARCH.PARTNERSHIP_OPPORTUNITIES
GROUP BY PARTNERSHIP_TYPE
ORDER BY total_potential_value DESC;
```

---

## 5. Unified_INTELLIGENCE Schema Queries (CONFIDENTIAL - Unified ACCESS ONLY)

### Strategic Plans Analysis

#### Natural Language Queries:
- "Show me our strategic plan progress"
- "Which plans have the highest ROI?"
- "What are our critical strategic initiatives?"

#### SQL Queries:

```sql
-- Strategic plans overview (Unified ONLY)
SELECT 
    PLAN_TITLE,
    STATUS,
    PRIORITY_LEVEL,
    ESTIMATED_INVESTMENT,
    PROJECTED_ROI,
    RISK_ASSESSMENT,
    RESPONSIBLE_EXECUTIVE,
    NEXT_REVIEW_DATE
FROM Unified_INTELLIGENCE.STRATEGIC_PLANS
WHERE STATUS IN ('IN_EXECUTION', 'PLANNING')
ORDER BY PRIORITY_LEVEL, PROJECTED_ROI DESC;

-- Strategic investment analysis
SELECT 
    STATUS,
    COUNT(*) as plan_count,
    SUM(ESTIMATED_INVESTMENT) as total_investment,
    AVG(PROJECTED_ROI) as avg_roi,
    SUM(ESTIMATED_INVESTMENT * PROJECTED_ROI) as projected_return
FROM Unified_INTELLIGENCE.STRATEGIC_PLANS
GROUP BY STATUS
ORDER BY total_investment DESC;
```

### Board Materials Analysis

#### Natural Language Queries:
- "Show me recent board materials"
- "What materials need review?"
- "Analyze board meeting content"

#### SQL Queries:

```sql
-- Recent board materials (Unified ONLY)
SELECT 
    MATERIAL_TITLE,
    MATERIAL_TYPE,
    BOARD_MEETING_DATE,
    CONFIDENTIALITY_LEVEL,
    APPROVAL_STATUS,
    PREPARED_BY
FROM Unified_INTELLIGENCE.BOARD_MATERIALS
WHERE BOARD_MEETING_DATE >= CURRENT_DATE - 180
ORDER BY BOARD_MEETING_DATE DESC;

-- Materials by confidentiality level
SELECT 
    CONFIDENTIALITY_LEVEL,
    COUNT(*) as material_count,
    COUNT(CASE WHEN APPROVAL_STATUS = 'APPROVED' THEN 1 END) as approved_count
FROM Unified_INTELLIGENCE.BOARD_MATERIALS
WHERE BOARD_MEETING_DATE >= CURRENT_DATE - 365
GROUP BY CONFIDENTIALITY_LEVEL;
```

### Competitive Intelligence (Unified Level)

#### Natural Language Queries:
- "Show me critical competitive threats"
- "What strategic intelligence do we have?"
- "Which competitors require immediate attention?"

#### SQL Queries:

```sql
-- Critical competitive intelligence (Unified ONLY)
SELECT 
    INTELLIGENCE_TITLE,
    DETAILED_ANALYSIS,
    STRATEGIC_IMPLICATIONS,
    CONFIDENCE_LEVEL,
    COMPETITIVE_IMPACT,
    RECOMMENDED_ACTIONS,
    COLLECTION_DATE
FROM Unified_INTELLIGENCE.COMPETITIVE_INTELLIGENCE
WHERE COMPETITIVE_IMPACT = 'CRITICAL'
AND COLLECTION_DATE >= CURRENT_DATE - 90
ORDER BY COLLECTION_DATE DESC;

-- Intelligence by confidence and impact
SELECT 
    CONFIDENCE_LEVEL,
    COMPETITIVE_IMPACT,
    COUNT(*) as intelligence_count,
    MAX(COLLECTION_DATE) as latest_intelligence
FROM Unified_INTELLIGENCE.COMPETITIVE_INTELLIGENCE
WHERE COLLECTION_DATE >= CURRENT_DATE - 180
GROUP BY CONFIDENCE_LEVEL, COMPETITIVE_IMPACT
ORDER BY intelligence_count DESC;
```

---

## 6. Cross-Schema Analysis Queries

### Comprehensive Business Intelligence

#### Natural Language Queries:
- "Give me a complete business overview"
- "How do our properties perform against payments?"
- "Show me the connection between customer features and revenue"

#### SQL Queries:

```sql
-- Comprehensive business performance
WITH payment_metrics AS (
    SELECT 
        SUM(CASE WHEN STATUS = 'COMPLETED' THEN AMOUNT ELSE 0 END) as monthly_payment_revenue,
        COUNT(CASE WHEN STATUS = 'COMPLETED' THEN 1 END) as successful_transactions
    FROM PAYREADY_CORE_SQL.PAYMENT_TRANSACTIONS
    WHERE PROCESSING_DATE >= DATE_TRUNC('month', CURRENT_DATE)
),
property_metrics AS (
    SELECT 
        SUM(ACTUAL_MONTHLY_RENT) as monthly_rent_revenue,
        AVG(OCCUPANCY_RATE) as avg_occupancy
    FROM PROPERTY_ASSETS.PROPERTIES
    WHERE PROPERTY_STATUS = 'ACTIVE'
),
expense_metrics AS (
    SELECT 
        SUM(AMOUNT) as monthly_expenses
    FROM NETSUITE_DATA.EXPENSE_REPORTS
    WHERE EXPENSE_DATE >= DATE_TRUNC('month', CURRENT_DATE)
)
SELECT 
    pm.monthly_payment_revenue,
    pm.successful_transactions,
    prm.monthly_rent_revenue,
    prm.avg_occupancy,
    em.monthly_expenses,
    (pm.monthly_payment_revenue + prm.monthly_rent_revenue - em.monthly_expenses) as net_monthly_income
FROM payment_metrics pm
CROSS JOIN property_metrics prm
CROSS JOIN expense_metrics em;

-- Property payment correlation
SELECT 
    p.PROPERTY_NAME,
    p.OCCUPANCY_RATE,
    p.ACTUAL_MONTHLY_RENT,
    COUNT(pt.TRANSACTION_ID) as transaction_count,
    SUM(pt.AMOUNT) as payment_volume,
    ROUND(COUNT(CASE WHEN pt.STATUS = 'COMPLETED' THEN 1 END) * 100.0 / COUNT(*), 2) as payment_success_rate
FROM PROPERTY_ASSETS.PROPERTIES p
LEFT JOIN PAYREADY_CORE_SQL.PAYMENT_TRANSACTIONS pt ON p.PROPERTY_ID = pt.PROPERTY_ID
WHERE p.PROPERTY_STATUS = 'ACTIVE'
AND pt.PROCESSING_DATE >= CURRENT_DATE - 30
GROUP BY p.PROPERTY_NAME, p.OCCUPANCY_RATE, p.ACTUAL_MONTHLY_RENT
ORDER BY payment_volume DESC;
```

---

## 7. AI-Enhanced Semantic Search Queries

### Using AI Memory Embeddings

#### Natural Language Queries:
- "Find documents similar to 'payment processing innovation'"
- "Search for strategic plans related to AI"
- "Show me competitive intelligence about fintech"

#### Vector Search SQL:

```sql
-- Semantic search across all schemas using embeddings
WITH search_query AS (
    SELECT SNOWFLAKE.CORTEX.EMBED_TEXT_768('e5-base-v2', 'payment processing innovation') as query_embedding
)
SELECT 
    'PAYREADY_CORE_SQL.PAYMENT_TRANSACTIONS' as source_table,
    TRANSACTION_ID as record_id,
    FAILURE_REASON as content,
    VECTOR_COSINE_SIMILARITY(AI_MEMORY_EMBEDDING, sq.query_embedding) as similarity_score
FROM PAYREADY_CORE_SQL.PAYMENT_TRANSACTIONS pt
CROSS JOIN search_query sq
WHERE AI_MEMORY_EMBEDDING IS NOT NULL
AND VECTOR_COSINE_SIMILARITY(AI_MEMORY_EMBEDDING, sq.query_embedding) > 0.7

UNION ALL

SELECT 
    'AI_WEB_RESEARCH.INDUSTRY_TRENDS' as source_table,
    TREND_ID as record_id,
    TREND_TITLE || ': ' || TREND_DESCRIPTION as content,
    VECTOR_COSINE_SIMILARITY(AI_MEMORY_EMBEDDING, sq.query_embedding) as similarity_score
FROM AI_WEB_RESEARCH.INDUSTRY_TRENDS it
CROSS JOIN search_query sq
WHERE AI_MEMORY_EMBEDDING IS NOT NULL
AND VECTOR_COSINE_SIMILARITY(AI_MEMORY_EMBEDDING, sq.query_embedding) > 0.7

ORDER BY similarity_score DESC
LIMIT 20;
```

---

## 8. Natural Language Query Examples

### Enhanced Chat Interface Queries

#### Executive Dashboard Queries:
- "What's our financial performance this quarter?"
- "Show me property portfolio health"
- "Analyze customer feature adoption trends"
- "What are the latest industry trends affecting us?"

#### Unified Dashboard Queries (CONFIDENTIAL):
- "Give me a strategic overview of our competitive position"
- "Show me board materials for the next meeting"
- "What M&A opportunities are we tracking?"
- "Analyze our strategic plan execution progress"

#### Operational Queries:
- "Which properties have the lowest occupancy?"
- "Show me failed payments by reason"
- "What expenses need approval?"
- "Find partnership opportunities in fintech"

---

## 9. Performance Optimization Tips

### Query Optimization:
- Use date filters to limit data ranges
- Leverage AI_MEMORY_EMBEDDING columns for semantic search
- Use appropriate indexes on frequently queried columns
- Consider materialized views for complex aggregations

### Security Considerations:
- Always verify user access level before querying Unified_INTELLIGENCE
- Use role-based access control for sensitive data
- Audit all access to confidential information
- Implement data masking for non-authorized users

### Best Practices:
- Use parameterized queries to prevent SQL injection
- Implement proper error handling and logging
- Cache frequently accessed results
- Monitor query performance and optimize as needed

---

This comprehensive query reference enables developers to effectively utilize all Sophia AI schemas while maintaining appropriate security controls and performance optimization. 