
-- ==================================================
-- SAMPLE DATA FOR CUSTOMER INSIGHTS TESTING
-- ==================================================

-- Sample customer profiles
INSERT INTO CUSTOMER_PROFILES (
    customer_id, customer_name, company, industry, customer_tier, 
    total_revenue, health_score, churn_risk_score, growth_potential_score
) VALUES 
('CUST_001', 'John Smith', 'TechCorp Inc', 'Technology', 'Enterprise', 150000.00, 0.85, 0.15, 0.80),
('CUST_002', 'Sarah Johnson', 'HealthPlus', 'Healthcare', 'SMB', 45000.00, 0.65, 0.35, 0.60),
('CUST_003', 'Mike Chen', 'FinanceFirst', 'Financial Services', 'Enterprise', 220000.00, 0.92, 0.08, 0.90),
('CUST_004', 'Lisa Brown', 'RetailMax', 'Retail', 'SMB', 25000.00, 0.40, 0.70, 0.30),
('CUST_005', 'David Wilson', 'StartupXYZ', 'Technology', 'Startup', 15000.00, 0.75, 0.25, 0.85);

-- Sample customer interactions
INSERT INTO CUSTOMER_INTERACTIONS (
    interaction_id, customer_id, interaction_type, interaction_date,
    interaction_content, interaction_summary, sentiment_score, topics, key_insights, action_items
) VALUES 
('INT_001', 'CUST_001', 'call', '2024-01-15 10:00:00', 
 'Quarterly business review discussing expansion plans and ROI metrics.',
 'Positive QBR with expansion discussion', 0.7, 
 ARRAY_CONSTRUCT('expansion', 'ROI', 'quarterly-review'),
 ARRAY_CONSTRUCT('Strong ROI demonstrated', 'Ready for expansion'),
 ARRAY_CONSTRUCT('Prepare expansion proposal', 'Schedule follow-up')),
 
('INT_002', 'CUST_002', 'support', '2024-01-16 14:30:00',
 'Customer reported integration issues with API connectivity.',
 'Technical support for API integration problems', -0.3,
 ARRAY_CONSTRUCT('API', 'integration', 'technical-issue'),
 ARRAY_CONSTRUCT('Integration complexity', 'Need better documentation'),
 ARRAY_CONSTRUCT('Provide API documentation', 'Schedule technical review')),
 
('INT_003', 'CUST_003', 'demo', '2024-01-17 11:00:00',
 'Product demo for advanced analytics features and new dashboard.',
 'Enthusiastic response to new analytics features', 0.8,
 ARRAY_CONSTRUCT('analytics', 'dashboard', 'demo'),
 ARRAY_CONSTRUCT('High interest in analytics', 'Potential for premium upgrade'),
 ARRAY_CONSTRUCT('Send analytics proposal', 'Schedule implementation call'));

-- Sample customer journey stages
INSERT INTO CUSTOMER_JOURNEY (
    journey_id, customer_id, journey_stage, stage_entered_date,
    stage_duration_days, stage_success_probability, next_best_action
) VALUES 
('JOUR_001', 'CUST_001', 'expansion', '2024-01-01', 30, 0.85, 'Present comprehensive expansion package'),
('JOUR_002', 'CUST_002', 'renewal', '2024-01-10', 15, 0.60, 'Address technical concerns and demonstrate value'),
('JOUR_003', 'CUST_003', 'expansion', '2024-01-05', 25, 0.90, 'Finalize analytics package proposal'),
('JOUR_004', 'CUST_004', 'at_risk', '2024-01-12', 20, 0.30, 'Immediate intervention required'),
('JOUR_005', 'CUST_005', 'growth', '2024-01-08', 18, 0.75, 'Explore additional use cases');
