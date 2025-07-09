-- Lambda Labs Analytics Schema
-- Tracks usage, costs, and optimization opportunities

USE ROLE SOPHIA_ADMIN_ROLE;
USE DATABASE SOPHIA_AI;
USE SCHEMA AI_INSIGHTS;

-- Usage tracking table
CREATE TABLE IF NOT EXISTS LAMBDA_LABS_USAGE (
    id NUMBER AUTOINCREMENT PRIMARY KEY,
    timestamp TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    request_id VARCHAR(100),
    user_id VARCHAR(100),
    session_id VARCHAR(100),
    model VARCHAR(100) NOT NULL,
    backend VARCHAR(20) NOT NULL, -- 'serverless' or 'gpu'
    prompt_tokens NUMBER NOT NULL,
    completion_tokens NUMBER NOT NULL,
    total_tokens NUMBER NOT NULL,
    cost_usd NUMBER(10,6) NOT NULL,
    latency_ms NUMBER,
    cost_priority VARCHAR(20),
    error_message VARCHAR(1000),
    metadata VARIANT
);

-- Daily aggregates for reporting
CREATE OR REPLACE VIEW LAMBDA_LABS_DAILY_STATS AS
SELECT
    DATE_TRUNC('day', timestamp) as date,
    model,
    backend,
    COUNT(*) as request_count,
    SUM(total_tokens) as total_tokens,
    SUM(cost_usd) as total_cost,
    AVG(latency_ms) as avg_latency_ms,
    COUNT(DISTINCT user_id) as unique_users,
    SUM(CASE WHEN error_message IS NOT NULL THEN 1 ELSE 0 END) as error_count
FROM LAMBDA_LABS_USAGE
GROUP BY 1, 2, 3;

-- Model performance comparison
CREATE OR REPLACE VIEW LAMBDA_LABS_MODEL_PERFORMANCE AS
SELECT
    model,
    backend,
    COUNT(*) as usage_count,
    AVG(cost_usd / NULLIF(total_tokens, 0) * 1000000) as avg_cost_per_million,
    AVG(latency_ms) as avg_latency_ms,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY latency_ms) as p50_latency,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY latency_ms) as p95_latency,
    PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY latency_ms) as p99_latency,
    SUM(cost_usd) as total_cost,
    AVG(completion_tokens / NULLIF(prompt_tokens, 0)) as avg_output_ratio
FROM LAMBDA_LABS_USAGE
WHERE timestamp >= DATEADD('day', -30, CURRENT_TIMESTAMP())
GROUP BY 1, 2;

-- Cost optimization opportunities
CREATE OR REPLACE FUNCTION IDENTIFY_COST_OPTIMIZATIONS()
RETURNS TABLE (
    optimization_type VARCHAR,
    current_model VARCHAR,
    recommended_model VARCHAR,
    estimated_monthly_savings NUMBER,
    affected_requests NUMBER,
    recommendation VARCHAR
)
LANGUAGE SQL
AS
$$
WITH monthly_usage AS (
    SELECT
        model,
        cost_priority,
        COUNT(*) as request_count,
        SUM(cost_usd) as total_cost,
        AVG(prompt_tokens + completion_tokens) as avg_tokens
    FROM LAMBDA_LABS_USAGE
    WHERE timestamp >= DATEADD('day', -30, CURRENT_TIMESTAMP())
    GROUP BY 1, 2
),
optimizations AS (
    -- Find expensive models used for simple tasks
    SELECT
        'downgrade_model' as optimization_type,
        model as current_model,
        'llama3.1-8b-instruct' as recommended_model,
        total_cost * 0.8 as estimated_monthly_savings, -- 80% savings
        request_count as affected_requests,
        'Simple queries using expensive model' as recommendation
    FROM monthly_usage
    WHERE model != 'llama3.1-8b-instruct'
    AND avg_tokens < 500
    AND cost_priority = 'low_cost'

    UNION ALL

    -- Find opportunities to batch process
    SELECT
        'batch_processing' as optimization_type,
        model as current_model,
        model as recommended_model,
        total_cost * 0.3 as estimated_monthly_savings, -- 30% from batching
        request_count as affected_requests,
        'High volume of similar requests - consider batching' as recommendation
    FROM monthly_usage
    WHERE request_count > 1000
)
SELECT * FROM optimizations
ORDER BY estimated_monthly_savings DESC
$$;

-- Stored procedure to record usage
CREATE OR REPLACE PROCEDURE RECORD_LAMBDA_USAGE(
    p_request_id VARCHAR,
    p_user_id VARCHAR,
    p_session_id VARCHAR,
    p_model VARCHAR,
    p_backend VARCHAR,
    p_prompt_tokens NUMBER,
    p_completion_tokens NUMBER,
    p_cost_usd NUMBER,
    p_latency_ms NUMBER,
    p_cost_priority VARCHAR,
    p_error_message VARCHAR,
    p_metadata VARIANT
)
RETURNS VARCHAR
LANGUAGE SQL
AS
$$
BEGIN
    INSERT INTO LAMBDA_LABS_USAGE (
        request_id,
        user_id,
        session_id,
        model,
        backend,
        prompt_tokens,
        completion_tokens,
        total_tokens,
        cost_usd,
        latency_ms,
        cost_priority,
        error_message,
        metadata
    ) VALUES (
        p_request_id,
        p_user_id,
        p_session_id,
        p_model,
        p_backend,
        p_prompt_tokens,
        p_completion_tokens,
        p_prompt_tokens + p_completion_tokens,
        p_cost_usd,
        p_latency_ms,
        p_cost_priority,
        p_error_message,
        p_metadata
    );

    RETURN 'Usage recorded successfully';
END;
$$;

-- Alert on budget thresholds
CREATE OR REPLACE PROCEDURE CHECK_LAMBDA_BUDGET_ALERTS()
RETURNS TABLE (alert_type VARCHAR, current_value NUMBER, threshold NUMBER, message VARCHAR)
LANGUAGE SQL
AS
$$
DECLARE
    daily_budget NUMBER := 50.0;
    monthly_budget NUMBER := 1000.0;
    daily_spend NUMBER;
    monthly_spend NUMBER;
BEGIN
    -- Calculate current spend
    SELECT SUM(cost_usd) INTO daily_spend
    FROM LAMBDA_LABS_USAGE
    WHERE timestamp >= DATEADD('hour', -24, CURRENT_TIMESTAMP());

    SELECT SUM(cost_usd) INTO monthly_spend
    FROM LAMBDA_LABS_USAGE
    WHERE timestamp >= DATEADD('day', -30, CURRENT_TIMESTAMP());

    -- Check daily budget
    IF daily_spend >= daily_budget * 0.8 THEN
        INSERT INTO TEMP_ALERTS
        SELECT 'daily_budget', daily_spend, daily_budget,
               'Daily Lambda Labs spend at ' || ROUND(daily_spend / daily_budget * 100, 1) || '% of budget';
    END IF;

    -- Check monthly budget
    IF monthly_spend >= monthly_budget * 0.8 THEN
        INSERT INTO TEMP_ALERTS
        SELECT 'monthly_budget', monthly_spend, monthly_budget,
               'Monthly Lambda Labs spend at ' || ROUND(monthly_spend / monthly_budget * 100, 1) || '% of budget';
    END IF;

    RETURN TABLE(TEMP_ALERTS);
END;
$$;
