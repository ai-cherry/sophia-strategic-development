
-- ==================================================
-- TEST CUSTOMER INSIGHTS PROCEDURES
-- ==================================================

-- Test customer insights generation
CALL GENERATE_CUSTOMER_AI_INSIGHTS('CUST_001');
CALL GENERATE_CUSTOMER_AI_INSIGHTS('CUST_002');
CALL GENERATE_CUSTOMER_AI_INSIGHTS('CUST_004');

-- Test health score updates
CALL UPDATE_CUSTOMER_HEALTH_SCORE('CUST_001');
CALL UPDATE_CUSTOMER_HEALTH_SCORE('CUST_002');
CALL UPDATE_CUSTOMER_HEALTH_SCORE('CUST_004');

-- Test predictions generation
CALL GENERATE_CUSTOMER_PREDICTIONS('CUST_001');
CALL GENERATE_CUSTOMER_PREDICTIONS('CUST_002');
CALL GENERATE_CUSTOMER_PREDICTIONS('CUST_004');

-- Validation queries
SELECT 'Customer Profiles' as table_name, COUNT(*) as record_count FROM CUSTOMER_PROFILES
UNION ALL
SELECT 'Customer Interactions', COUNT(*) FROM CUSTOMER_INTERACTIONS
UNION ALL
SELECT 'Customer Journey', COUNT(*) FROM CUSTOMER_JOURNEY
UNION ALL
SELECT 'AI Insights', COUNT(*) FROM CUSTOMER_AI_INSIGHTS
UNION ALL
SELECT 'Customer Predictions', COUNT(*) FROM CUSTOMER_PREDICTIONS;

-- Customer health dashboard query
SELECT 
    cp.customer_id,
    cp.customer_name,
    cp.company,
    cp.health_score,
    COUNT(cai.insight_id) as ai_insights_count,
    COUNT(cpred.prediction_id) as predictions_count,
    MAX(ci.interaction_date) as last_interaction
FROM CUSTOMER_PROFILES cp
LEFT JOIN CUSTOMER_AI_INSIGHTS cai ON cp.customer_id = cai.customer_id
LEFT JOIN CUSTOMER_PREDICTIONS cpred ON cp.customer_id = cpred.customer_id
LEFT JOIN CUSTOMER_INTERACTIONS ci ON cp.customer_id = ci.customer_id
GROUP BY cp.customer_id, cp.customer_name, cp.company, cp.health_score
ORDER BY cp.health_score DESC;
