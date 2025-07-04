
-- ==================================================
-- SOPHIA AI CUSTOMER INSIGHTS PROCEDURES
-- ==================================================

-- =====================================
-- PROCEDURE: Generate Customer AI Insights
-- =====================================
-- Note: ANSI SQL doesn't support Python stored procedures
-- This is a simplified version using standard SQL
CREATE PROCEDURE GENERATE_CUSTOMER_AI_INSIGHTS(IN customer_id VARCHAR(50), OUT status VARCHAR(50), OUT insights_generated INT)
LANGUAGE SQL
AS
BEGIN
    DECLARE health_score DECIMAL(3,2);
    DECLARE avg_sentiment DECIMAL(3,2);
    DECLARE result_text VARCHAR(1000);

    -- Set default output values
    SET status = 'success';
    SET insights_generated = 0;

    -- Get customer profile data
    SELECT cp.health_score,
           AVG(ci.sentiment_score) AS avg_sentiment
    INTO health_score, avg_sentiment
    FROM CUSTOMER_PROFILES cp
    LEFT JOIN CUSTOMER_INTERACTIONS ci ON cp.customer_id = ci.customer_id
    WHERE cp.customer_id = customer_id
    GROUP BY cp.customer_id, cp.health_score;

    -- Generate health score insight if low
    IF health_score < 0.3 THEN
        INSERT INTO CUSTOMER_AI_INSIGHTS (
            insight_id, customer_id, insight_type, insight_title,
            insight_description, confidence_score, impact_score,
            evidence, recommended_actions
        ) VALUES (
            CONCAT(customer_id, '_health_risk_', DATE_FORMAT(CURRENT_DATE, '%Y%m%d')),
            customer_id,
            'risk_factor',
            'Low Customer Health Score Detected',
            CONCAT('Customer health score of ', CAST(health_score AS VARCHAR(10)), ' indicates potential risk. Recent interactions show declining engagement.'),
            0.85,
            0.75,
            CONCAT('Health score: ', CAST(health_score AS VARCHAR(10)), ', Below threshold of 0.5'),
            'Schedule immediate check-in call, Review recent support tickets, Analyze usage patterns'
        );

        SET insights_generated = insights_generated + 1;

    -- Generate health score insight if high
    ELSEIF health_score > 0.8 THEN
        INSERT INTO CUSTOMER_AI_INSIGHTS (
            insight_id, customer_id, insight_type, insight_title,
            insight_description, confidence_score, impact_score,
            evidence, recommended_actions
        ) VALUES (
            CONCAT(customer_id, '_expansion_opp_', DATE_FORMAT(CURRENT_DATE, '%Y%m%d')),
            customer_id,
            'growth_opportunity',
            'High Health Score - Expansion Opportunity',
            CONCAT('Customer health score of ', CAST(health_score AS VARCHAR(10)), ' indicates strong satisfaction. Consider expansion opportunities.'),
            0.78,
            0.82,
            CONCAT('Health score: ', CAST(health_score AS VARCHAR(10)), ', Above excellent threshold'),
            'Present upsell opportunities, Schedule strategic account review, Explore new use cases'
        );

        SET insights_generated = insights_generated + 1;
    END IF;

    -- Generate sentiment insight if negative
    IF avg_sentiment < -0.2 THEN
        INSERT INTO CUSTOMER_AI_INSIGHTS (
            insight_id, customer_id, insight_type, insight_title,
            insight_description, confidence_score, impact_score,
            evidence, recommended_actions
        ) VALUES (
            CONCAT(customer_id, '_sentiment_risk_', DATE_FORMAT(CURRENT_DATE, '%Y%m%d')),
            customer_id,
            'behavior_pattern',
            'Declining Sentiment Trend',
            CONCAT('Average sentiment score of ', CAST(avg_sentiment AS VARCHAR(10)), ' indicates customer frustration or dissatisfaction.'),
            0.82,
            0.70,
            CONCAT('Average sentiment: ', CAST(avg_sentiment AS VARCHAR(10)), ', Multiple negative interactions'),
            'Immediate customer success intervention, Review support case history, Schedule feedback session'
        );

        SET insights_generated = insights_generated + 1;
    END IF;

    -- Return results via SELECT
    SET result_text = CONCAT('Generated ', CAST(insights_generated AS VARCHAR(10)), ' insights for customer ', customer_id);
    SELECT result_text AS result;
END;

-- =====================================
-- PROCEDURE: Update Customer Health Score
-- =====================================
CREATE PROCEDURE UPDATE_CUSTOMER_HEALTH_SCORE(IN customer_id VARCHAR(50), OUT status VARCHAR(50), OUT new_health_score DECIMAL(3,2))
LANGUAGE SQL
AS
BEGIN
    DECLARE recency_score DECIMAL(3,2);
    DECLARE sentiment_score DECIMAL(3,2);
    DECLARE frequency_score DECIMAL(3,2);
    DECLARE revenue_score DECIMAL(3,2);
    DECLARE days_since_interaction INT;
    DECLARE total_revenue DECIMAL(15,2);
    DECLARE interaction_count INT;
    DECLARE result_text VARCHAR(1000);

    -- Set default status
    SET status = 'success';

    -- Get data for health score calculation
    SELECT
        DATEDIFF(DAY, cp.last_interaction_date, CURRENT_DATE) AS days_since,
        cp.total_revenue,
        COUNT(ci.interaction_id) AS interaction_count,
        AVG(ci.sentiment_score) AS avg_sentiment
    INTO
        days_since_interaction,
        total_revenue,
        interaction_count,
        sentiment_score
    FROM CUSTOMER_PROFILES cp
    LEFT JOIN CUSTOMER_INTERACTIONS ci
        ON cp.customer_id = ci.customer_id
        AND ci.interaction_date >= DATE_SUB(CURRENT_DATE, INTERVAL 90 DAY)
    WHERE cp.customer_id = customer_id
    GROUP BY cp.customer_id, cp.last_interaction_date, cp.total_revenue;

    -- Calculate recency score
    IF days_since_interaction <= 7 THEN SET recency_score = 1.0;
    ELSEIF days_since_interaction <= 30 THEN SET recency_score = 0.8;
    ELSEIF days_since_interaction <= 60 THEN SET recency_score = 0.5;
    ELSE SET recency_score = 0.2;
    END IF;

    -- Normalize sentiment score (from -1..1 to 0..1)
    SET sentiment_score = (sentiment_score + 1) / 2;

    -- Calculate frequency score
    SET frequency_score = LEAST(1.0, interaction_count * 0.1);

    -- Calculate revenue score
    IF total_revenue >= 100000 THEN SET revenue_score = 1.0;
    ELSEIF total_revenue >= 50000 THEN SET revenue_score = 0.8;
    ELSEIF total_revenue >= 25000 THEN SET revenue_score = 0.6;
    ELSEIF total_revenue >= 10000 THEN SET revenue_score = 0.4;
    ELSE SET revenue_score = 0.2;
    END IF;

    -- Calculate final health score
    SET new_health_score = (
        recency_score * 0.3 +
        sentiment_score * 0.4 +
        frequency_score * 0.2 +
        revenue_score * 0.1
    );

    -- Update customer profile
    UPDATE CUSTOMER_PROFILES
    SET
        health_score = new_health_score,
        updated_at = CURRENT_TIMESTAMP
    WHERE customer_id = customer_id;

    -- Return results via SELECT
    SET result_text = CONCAT('Updated health score to ', CAST(new_health_score AS VARCHAR(10)), ' for customer ', customer_id);
    SELECT result_text AS result;
END;

-- =====================================
-- PROCEDURE: Generate Customer Predictions
-- =====================================
CREATE PROCEDURE GENERATE_CUSTOMER_PREDICTIONS(IN customer_id VARCHAR(50), OUT status VARCHAR(50), OUT predictions_made INT)
LANGUAGE SQL
AS
BEGIN
    DECLARE health_score DECIMAL(3,2);
    DECLARE avg_sentiment DECIMAL(3,2);
    DECLARE days_since_interaction INT;
    DECLARE customer_tier VARCHAR(20);
    DECLARE churn_risk DECIMAL(10,4);
    DECLARE expansion_likelihood DECIMAL(10,4);
    DECLARE churn_factors VARCHAR(1000);
    DECLARE expansion_factors VARCHAR(1000);
    DECLARE result_text VARCHAR(1000);

    -- Set default values
    SET status = 'success';
    SET predictions_made = 0;
    SET churn_risk = 0.5; -- baseline
    SET expansion_likelihood = 0.2; -- baseline
    SET churn_factors = '';
    SET expansion_factors = '';

    -- Get customer data for predictions
    SELECT
        cp.health_score,
        cp.customer_tier,
        AVG(ci.sentiment_score) AS avg_sentiment,
        DATEDIFF(DAY, MAX(ci.interaction_date), CURRENT_DATE) AS days_since
    INTO
        health_score,
        customer_tier,
        avg_sentiment,
        days_since_interaction
    FROM CUSTOMER_PROFILES cp
    LEFT JOIN CUSTOMER_INTERACTIONS ci ON cp.customer_id = ci.customer_id
    WHERE cp.customer_id = customer_id
    GROUP BY cp.customer_id, cp.health_score, cp.customer_tier;

    -- Calculate churn risk and factors
    IF health_score < 0.3 THEN
        SET churn_risk = churn_risk + 0.3;
        SET churn_factors = CONCAT(churn_factors, 'Low health score, ');
    END IF;

    IF avg_sentiment < -0.2 THEN
        SET churn_risk = churn_risk + 0.2;
        SET churn_factors = CONCAT(churn_factors, 'Negative sentiment trend, ');
    END IF;

    IF days_since_interaction > 60 THEN
        SET churn_risk = churn_risk + 0.2;
        SET churn_factors = CONCAT(churn_factors, 'Extended silence period, ');
    END IF;

    -- Cap churn risk at 95%
    IF churn_risk > 0.95 THEN SET churn_risk = 0.95; END IF;

    -- Insert churn prediction
    INSERT INTO CUSTOMER_PREDICTIONS (
        prediction_id, customer_id, prediction_type, prediction_value,
        prediction_confidence, prediction_factors, prediction_horizon_days, model_version
    ) VALUES (
        CONCAT(customer_id, '_churn_', DATE_FORMAT(CURRENT_DATE, '%Y%m%d')),
        customer_id,
        'churn_risk',
        churn_risk,
        0.75,
        churn_factors,
        90,
        'v1.0'
    );

    SET predictions_made = predictions_made + 1;

    -- Calculate expansion likelihood and factors
    IF health_score > 0.8 THEN
        SET expansion_likelihood = expansion_likelihood + 0.4;
        SET expansion_factors = CONCAT(expansion_factors, 'High health score, ');
    END IF;

    IF avg_sentiment > 0.3 THEN
        SET expansion_likelihood = expansion_likelihood + 0.3;
        SET expansion_factors = CONCAT(expansion_factors, 'Positive sentiment, ');
    END IF;

    IF customer_tier = 'Enterprise' THEN
        SET expansion_likelihood = expansion_likelihood + 0.2;
        SET expansion_factors = CONCAT(expansion_factors, 'Enterprise tier customer, ');
    END IF;

    -- Cap expansion likelihood at 95%
    IF expansion_likelihood > 0.95 THEN SET expansion_likelihood = 0.95; END IF;

    -- Insert expansion prediction
    INSERT INTO CUSTOMER_PREDICTIONS (
        prediction_id, customer_id, prediction_type, prediction_value,
        prediction_confidence, prediction_factors, prediction_horizon_days, model_version
    ) VALUES (
        CONCAT(customer_id, '_expansion_', DATE_FORMAT(CURRENT_DATE, '%Y%m%d')),
        customer_id,
        'expansion_opportunity',
        expansion_likelihood,
        0.70,
        expansion_factors,
        60,
        'v1.0'
    );

    SET predictions_made = predictions_made + 1;

    -- Return results via SELECT
    SET result_text = CONCAT('Generated ', CAST(predictions_made AS VARCHAR(10)), ' predictions for customer ', customer_id);
    SELECT result_text AS result;
END;
