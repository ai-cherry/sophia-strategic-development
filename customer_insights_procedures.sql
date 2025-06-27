
-- ==================================================
-- SOPHIA AI CUSTOMER INSIGHTS PROCEDURES
-- ==================================================

-- =====================================
-- PROCEDURE: Generate Customer AI Insights
-- =====================================
CREATE OR REPLACE PROCEDURE GENERATE_CUSTOMER_AI_INSIGHTS(customer_id VARCHAR)
RETURNS VARIANT
LANGUAGE PYTHON
AS
$$
def main(session, customer_id):
    import json
    from datetime import datetime, timedelta
    
    results = {
        "customer_id": customer_id,
        "insights_generated": 0,
        "processing_time": datetime.now().isoformat(),
        "status": "success"
    }
    
    try:
        # Get customer profile and recent interactions
        customer_query = f'''
        SELECT 
            cp.*,
            COUNT(ci.interaction_id) as total_interactions,
            AVG(ci.sentiment_score) as avg_sentiment,
            ARRAY_AGG(DISTINCT ci.interaction_type) as interaction_types
        FROM CUSTOMER_PROFILES cp
        LEFT JOIN CUSTOMER_INTERACTIONS ci ON cp.customer_id = ci.customer_id
        WHERE cp.customer_id = '{customer_id}'
        GROUP BY cp.customer_id, cp.customer_name, cp.company, cp.industry, 
                 cp.customer_tier, cp.total_revenue, cp.health_score
        '''
        
        customer_data = session.sql(customer_query).collect()
        
        if not customer_data:
            results["status"] = "error"
            results["message"] = f"Customer {customer_id} not found"
            return results
        
        customer = customer_data[0]
        
        # Generate health score insight
        health_score = float(customer['HEALTH_SCORE']) if customer['HEALTH_SCORE'] else 0.5
        
        if health_score < 0.3:
            insight_query = f'''
            INSERT INTO CUSTOMER_AI_INSIGHTS (
                insight_id, customer_id, insight_type, insight_title, 
                insight_description, confidence_score, impact_score,
                evidence, recommended_actions
            ) VALUES (
                '{customer_id}_health_risk_{datetime.now().strftime("%Y%m%d")}',
                '{customer_id}',
                'risk_factor',
                'Low Customer Health Score Detected',
                'Customer health score of {health_score:.2f} indicates potential risk. Recent interactions show declining engagement.',
                0.85,
                0.75,
                ARRAY_CONSTRUCT('Health score: {health_score:.2f}', 'Below threshold of 0.5'),
                ARRAY_CONSTRUCT('Schedule immediate check-in call', 'Review recent support tickets', 'Analyze usage patterns')
            )
            '''
            session.sql(insight_query).collect()
            results["insights_generated"] += 1
            
        elif health_score > 0.8:
            insight_query = f'''
            INSERT INTO CUSTOMER_AI_INSIGHTS (
                insight_id, customer_id, insight_type, insight_title,
                insight_description, confidence_score, impact_score,
                evidence, recommended_actions
            ) VALUES (
                '{customer_id}_expansion_opp_{datetime.now().strftime("%Y%m%d")}',
                '{customer_id}',
                'growth_opportunity',
                'High Health Score - Expansion Opportunity',
                'Customer health score of {health_score:.2f} indicates strong satisfaction. Consider expansion opportunities.',
                0.78,
                0.82,
                ARRAY_CONSTRUCT('Health score: {health_score:.2f}', 'Above excellent threshold'),
                ARRAY_CONSTRUCT('Present upsell opportunities', 'Schedule strategic account review', 'Explore new use cases')
            )
            '''
            session.sql(insight_query).collect()
            results["insights_generated"] += 1
        
        # Sentiment analysis insight
        avg_sentiment = float(customer['AVG_SENTIMENT']) if customer['AVG_SENTIMENT'] else 0.0
        
        if avg_sentiment < -0.2:
            insight_query = f'''
            INSERT INTO CUSTOMER_AI_INSIGHTS (
                insight_id, customer_id, insight_type, insight_title,
                insight_description, confidence_score, impact_score,
                evidence, recommended_actions
            ) VALUES (
                '{customer_id}_sentiment_risk_{datetime.now().strftime("%Y%m%d")}',
                '{customer_id}',
                'behavior_pattern',
                'Declining Sentiment Trend',
                'Average sentiment score of {avg_sentiment:.2f} indicates customer frustration or dissatisfaction.',
                0.82,
                0.70,
                ARRAY_CONSTRUCT('Average sentiment: {avg_sentiment:.2f}', 'Multiple negative interactions'),
                ARRAY_CONSTRUCT('Immediate customer success intervention', 'Review support case history', 'Schedule feedback session')
            )
            '''
            session.sql(insight_query).collect()
            results["insights_generated"] += 1
        
        return results
        
    except Exception as e:
        results["status"] = "error"
        results["message"] = str(e)
        return results
$$;

-- =====================================
-- PROCEDURE: Update Customer Health Score
-- =====================================
CREATE OR REPLACE PROCEDURE UPDATE_CUSTOMER_HEALTH_SCORE(customer_id VARCHAR)
RETURNS VARIANT
LANGUAGE PYTHON
AS
$$
def main(session, customer_id):
    import json
    from datetime import datetime, timedelta
    
    try:
        # Calculate health score based on multiple factors
        health_calculation = f'''
        WITH customer_metrics AS (
            SELECT 
                cp.customer_id,
                -- Interaction recency factor (0-1)
                CASE 
                    WHEN DATEDIFF(day, cp.last_interaction_date, CURRENT_DATE()) <= 7 THEN 1.0
                    WHEN DATEDIFF(day, cp.last_interaction_date, CURRENT_DATE()) <= 30 THEN 0.8
                    WHEN DATEDIFF(day, cp.last_interaction_date, CURRENT_DATE()) <= 60 THEN 0.5
                    ELSE 0.2
                END as recency_score,
                
                -- Sentiment factor (0-1)
                COALESCE(
                    (SELECT (AVG(sentiment_score) + 1) / 2 
                     FROM CUSTOMER_INTERACTIONS 
                     WHERE customer_id = cp.customer_id 
                     AND interaction_date >= DATEADD(day, -90, CURRENT_DATE())), 
                    0.5
                ) as sentiment_score,
                
                -- Interaction frequency factor (0-1)
                LEAST(1.0, 
                    (SELECT COUNT(*) * 0.1 
                     FROM CUSTOMER_INTERACTIONS 
                     WHERE customer_id = cp.customer_id 
                     AND interaction_date >= DATEADD(day, -30, CURRENT_DATE()))
                ) as frequency_score,
                
                -- Revenue factor (0-1, normalized)
                CASE 
                    WHEN cp.total_revenue >= 100000 THEN 1.0
                    WHEN cp.total_revenue >= 50000 THEN 0.8
                    WHEN cp.total_revenue >= 25000 THEN 0.6
                    WHEN cp.total_revenue >= 10000 THEN 0.4
                    ELSE 0.2
                END as revenue_score
                
            FROM CUSTOMER_PROFILES cp
            WHERE cp.customer_id = '{customer_id}'
        )
        UPDATE CUSTOMER_PROFILES 
        SET 
            health_score = (
                cm.recency_score * 0.3 + 
                cm.sentiment_score * 0.4 + 
                cm.frequency_score * 0.2 + 
                cm.revenue_score * 0.1
            ),
            updated_at = CURRENT_TIMESTAMP()
        FROM customer_metrics cm
        WHERE CUSTOMER_PROFILES.customer_id = cm.customer_id
        '''
        
        session.sql(health_calculation).collect()
        
        # Get updated health score
        result_query = f'''
        SELECT customer_id, health_score, updated_at
        FROM CUSTOMER_PROFILES 
        WHERE customer_id = '{customer_id}'
        '''
        
        result = session.sql(result_query).collect()
        
        if result:
            return {
                "status": "success",
                "customer_id": customer_id,
                "new_health_score": float(result[0]['HEALTH_SCORE']),
                "updated_at": result[0]['UPDATED_AT'].isoformat()
            }
        else:
            return {
                "status": "error",
                "message": f"Customer {customer_id} not found"
            }
            
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
$$;

-- =====================================
-- PROCEDURE: Generate Customer Predictions
-- =====================================
CREATE OR REPLACE PROCEDURE GENERATE_CUSTOMER_PREDICTIONS(customer_id VARCHAR)
RETURNS VARIANT
LANGUAGE PYTHON
AS
$$
def main(session, customer_id):
    import json
    from datetime import datetime, timedelta
    
    try:
        # Get customer data for predictions
        customer_query = f'''
        SELECT 
            cp.*,
            COUNT(ci.interaction_id) as interaction_count,
            AVG(ci.sentiment_score) as avg_sentiment,
            DATEDIFF(day, MAX(ci.interaction_date), CURRENT_DATE()) as days_since_last_interaction
        FROM CUSTOMER_PROFILES cp
        LEFT JOIN CUSTOMER_INTERACTIONS ci ON cp.customer_id = ci.customer_id
        WHERE cp.customer_id = '{customer_id}'
        GROUP BY cp.customer_id, cp.customer_name, cp.health_score, cp.total_revenue, cp.customer_tier
        '''
        
        customer_data = session.sql(customer_query).collect()
        
        if not customer_data:
            return {"status": "error", "message": f"Customer {customer_id} not found"}
        
        customer = customer_data[0]
        health_score = float(customer['HEALTH_SCORE']) if customer['HEALTH_SCORE'] else 0.5
        avg_sentiment = float(customer['AVG_SENTIMENT']) if customer['AVG_SENTIMENT'] else 0.0
        days_since_interaction = int(customer['DAYS_SINCE_LAST_INTERACTION']) if customer['DAYS_SINCE_LAST_INTERACTION'] else 0
        
        predictions_made = 0
        
        # Churn risk prediction
        churn_risk = 0.5  # baseline
        churn_factors = []
        
        if health_score < 0.3:
            churn_risk += 0.3
            churn_factors.append("Low health score")
        if avg_sentiment < -0.2:
            churn_risk += 0.2
            churn_factors.append("Negative sentiment trend")
        if days_since_interaction > 60:
            churn_risk += 0.2
            churn_factors.append("Extended silence period")
        
        churn_risk = min(0.95, churn_risk)  # Cap at 95%
        
        churn_insert = f'''
        INSERT INTO CUSTOMER_PREDICTIONS (
            prediction_id, customer_id, prediction_type, prediction_value,
            prediction_confidence, prediction_factors, prediction_horizon_days, model_version
        ) VALUES (
            '{customer_id}_churn_{datetime.now().strftime("%Y%m%d")}',
            '{customer_id}',
            'churn_risk',
            {churn_risk:.4f},
            0.75,
            ARRAY_CONSTRUCT{tuple(churn_factors) if churn_factors else '()'},
            90,
            'v1.0'
        )
        '''
        session.sql(churn_insert).collect()
        predictions_made += 1
        
        # Expansion opportunity prediction
        expansion_likelihood = 0.2  # baseline
        expansion_factors = []
        
        if health_score > 0.8:
            expansion_likelihood += 0.4
            expansion_factors.append("High health score")
        if avg_sentiment > 0.3:
            expansion_likelihood += 0.3
            expansion_factors.append("Positive sentiment")
        if customer['CUSTOMER_TIER'] == 'Enterprise':
            expansion_likelihood += 0.2
            expansion_factors.append("Enterprise tier customer")
        
        expansion_likelihood = min(0.95, expansion_likelihood)
        
        expansion_insert = f'''
        INSERT INTO CUSTOMER_PREDICTIONS (
            prediction_id, customer_id, prediction_type, prediction_value,
            prediction_confidence, prediction_factors, prediction_horizon_days, model_version
        ) VALUES (
            '{customer_id}_expansion_{datetime.now().strftime("%Y%m%d")}',
            '{customer_id}',
            'expansion_opportunity',
            {expansion_likelihood:.4f},
            0.70,
            ARRAY_CONSTRUCT{tuple(expansion_factors) if expansion_factors else '()'},
            60,
            'v1.0'
        )
        '''
        session.sql(expansion_insert).collect()
        predictions_made += 1
        
        return {
            "status": "success",
            "customer_id": customer_id,
            "predictions_made": predictions_made,
            "churn_risk": churn_risk,
            "expansion_likelihood": expansion_likelihood
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
$$;
