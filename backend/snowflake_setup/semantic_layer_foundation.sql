-- Create semantic views for core business entities
-- File: backend/snowflake_setup/semantic_layer_foundation.sql

-- Customer Entity Semantic View
CREATE OR REPLACE VIEW SOPHIA_SEMANTIC.CUSTOMER_360 AS
SELECT
    c.customer_id,
    c.company_name,
    c.industry,
    c.lifecycle_stage,
    -- Aggregate metrics from multiple sources
    COUNT(DISTINCT g.call_id) as total_calls,
    COUNT(DISTINCT s.message_id) as slack_mentions,
    COUNT(DISTINCT i.ticket_id) as support_tickets,
    AVG(g.sentiment_score) as avg_sentiment,
    MAX(c.last_activity_date) as last_activity
FROM FOUNDATIONAL_KNOWLEDGE.CUSTOMERS c
LEFT JOIN GONG_DATA.CALLS g ON c.customer_id = g.customer_id
LEFT JOIN SLACK_DATA.MESSAGES s ON c.company_name ILIKE '%' || s.message_text || '%'
LEFT JOIN INTERCOM_DATA.TICKETS i ON c.customer_id = i.customer_id
GROUP BY c.customer_id, c.company_name, c.industry, c.lifecycle_stage;

-- Employee Entity Semantic View
CREATE OR REPLACE VIEW SOPHIA_SEMANTIC.EMPLOYEE_360 AS
SELECT
    e.employee_id,
    e.full_name,
    e.department,
    e.role,
    -- Performance and activity metrics
    COUNT(DISTINCT g.call_id) as calls_participated,
    COUNT(DISTINCT s.message_id) as slack_activity,
    AVG(g.talk_time_percentage) as avg_talk_time,
    COUNT(DISTINCT p.project_id) as active_projects
FROM FOUNDATIONAL_KNOWLEDGE.EMPLOYEES e
LEFT JOIN GONG_DATA.CALL_PARTICIPANTS gp ON e.email = gp.participant_email
LEFT JOIN GONG_DATA.CALLS g ON gp.call_id = g.call_id
LEFT JOIN SLACK_DATA.MESSAGES s ON e.slack_user_id = s.user_id
LEFT JOIN PROJECT_MANAGEMENT.PROJECT_ASSIGNMENTS pa ON e.employee_id = pa.employee_id
LEFT JOIN PROJECT_MANAGEMENT.PROJECTS p ON pa.project_id = p.project_id
GROUP BY e.employee_id, e.full_name, e.department, e.role;

-- Business Metrics Semantic Layer
CREATE OR REPLACE VIEW SOPHIA_SEMANTIC.BUSINESS_METRICS AS
SELECT
    DATE_TRUNC('month', metric_date) as month,
    'revenue' as metric_type,
    SUM(amount) as value,
    'USD' as currency
FROM PAYREADY_CORE.REVENUE_DATA
GROUP BY DATE_TRUNC('month', metric_date)
UNION ALL
SELECT
    DATE_TRUNC('month', call_date) as month,
    'sales_activity' as metric_type,
    COUNT(*) as value,
    'calls' as currency
FROM GONG_DATA.CALLS
GROUP BY DATE_TRUNC('month', call_date);
