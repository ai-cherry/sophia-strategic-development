-- =====================================================================
-- Pay Ready Foundational Knowledge Extensions
-- Extends the base foundational knowledge schema with Pay Ready-specific intelligence
-- =====================================================================

USE DATABASE SOPHIA_AI;
USE SCHEMA FOUNDATIONAL_KNOWLEDGE;

-- =====================================================================
-- PAY READY BUSINESS INTELLIGENCE EXTENSIONS
-- =====================================================================

-- Company Overview Table
CREATE TABLE IF NOT EXISTS COMPANY_OVERVIEW (
    company_id VARCHAR(255) PRIMARY KEY DEFAULT UUID_STRING(),
    company_name VARCHAR(500) NOT NULL DEFAULT 'Pay Ready',
    headquarters VARCHAR(255) DEFAULT 'Las Vegas, NV',
    founded_year INTEGER DEFAULT 2016,
    current_valuation DECIMAL(15,2) DEFAULT 150000000, -- $150M+ estimated post-Buzz
    total_units_contracted INTEGER DEFAULT 4000000, -- 4M+ units
    total_properties INTEGER DEFAULT 50000, -- 50K+ properties
    business_model TEXT DEFAULT 'SaaS CRM/payment platform specializing in multifamily post-resident AR recovery',
    mission_statement TEXT DEFAULT 'Redefine post-resident recovery: Automate chasing ex-renters while preventing delinquency upstream via fintech',
    tech_stack TEXT DEFAULT 'React Native, Google Cloud (GKE/Firebase), microservices, OpenRouter/Pinecone for AI memory',
    data_moat TEXT DEFAULT '$3.5B+ aged debt dataset for ML models',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Acquisitions Timeline Table
CREATE TABLE IF NOT EXISTS ACQUISITIONS (
    acquisition_id VARCHAR(255) PRIMARY KEY DEFAULT UUID_STRING(),
    acquired_company VARCHAR(500) NOT NULL,
    acquisition_date DATE NOT NULL,
    acquisition_type VARCHAR(100), -- strategic, talent, technology
    integration_status VARCHAR(100), -- completed, in-progress, planned
    strategic_value TEXT,
    integration_notes TEXT,
    rebranded_to VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Product Roadmap Table
CREATE TABLE IF NOT EXISTS PRODUCT_ROADMAP (
    roadmap_id VARCHAR(255) PRIMARY KEY DEFAULT UUID_STRING(),
    product_id VARCHAR(255),
    quarter VARCHAR(10) NOT NULL, -- Q2-2025, Q3-2025, etc.
    feature_name VARCHAR(500) NOT NULL,
    feature_description TEXT,
    status VARCHAR(100), -- planned, in-progress, completed, cancelled
    strategic_importance VARCHAR(50), -- high, medium, low
    ai_component BOOLEAN DEFAULT FALSE,
    target_segment VARCHAR(255), -- enterprise, mid-market, smb
    estimated_impact TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES PRODUCTS(PRODUCT_ID)
);

-- Market Segments Table
CREATE TABLE IF NOT EXISTS MARKET_SEGMENTS (
    segment_id VARCHAR(255) PRIMARY KEY DEFAULT UUID_STRING(),
    segment_name VARCHAR(255) NOT NULL,
    segment_type VARCHAR(100), -- multifamily, student-housing, single-family
    market_size DECIMAL(15,2), -- Total addressable market
    penetration_percentage DECIMAL(5,2), -- Pay Ready's penetration
    growth_rate DECIMAL(5,2), -- Annual growth rate
    key_players TEXT, -- Major competitors in this segment
    pay_ready_position VARCHAR(100), -- leader, challenger, niche
    strategic_priority VARCHAR(50), -- high, medium, low
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- AI Capabilities Tracking
CREATE TABLE IF NOT EXISTS AI_CAPABILITIES (
    capability_id VARCHAR(255) PRIMARY KEY DEFAULT UUID_STRING(),
    capability_name VARCHAR(500) NOT NULL,
    capability_type VARCHAR(100), -- communication, prediction, automation, analysis
    product_integration VARCHAR(255), -- Which product uses this
    ai_model VARCHAR(255), -- OpenRouter, Pinecone, custom
    automation_percentage DECIMAL(5,2), -- 80-90% for Buzz
    human_escalation_rate DECIMAL(5,2),
    performance_metrics TEXT,
    compliance_features TEXT,
    enhancement_roadmap TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Competitive Intelligence Table (Enhanced)
CREATE TABLE IF NOT EXISTS COMPETITIVE_ANALYSIS (
    analysis_id VARCHAR(255) PRIMARY KEY DEFAULT UUID_STRING(),
    competitor_id VARCHAR(255),
    analysis_date DATE DEFAULT CURRENT_DATE,
    threat_assessment VARCHAR(50), -- high, medium, low
    competitive_moats TEXT,
    weaknesses TEXT,
    opportunities TEXT, -- How Pay Ready can win
    market_share_estimate DECIMAL(5,2),
    revenue_estimate DECIMAL(15,2),
    strategic_response TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (competitor_id) REFERENCES COMPETITORS(COMPETITOR_ID)
);

-- =====================================================================
-- POPULATE WITH PAY READY DATA
-- =====================================================================

-- Insert Pay Ready Company Overview
INSERT INTO COMPANY_OVERVIEW DEFAULT VALUES;

-- Insert Key Acquisitions
INSERT INTO ACQUISITIONS (acquired_company, acquisition_date, acquisition_type, integration_status, strategic_value, rebranded_to) VALUES
('Buzz CRS', '2025-03-18', 'strategic', 'completed', 'AI rent collections for last-mile resident connections', 'BuzzCenter'),
('EvictionAssistant', '2024-07-01', 'strategic', 'completed', 'Expands eviction workflows and legal compliance', 'EvictionCenter');

-- Insert 2025-2026 Product Roadmap
INSERT INTO PRODUCT_ROADMAP (quarter, feature_name, feature_description, status, strategic_importance, ai_component, target_segment) VALUES
('Q2-2025', 'Buzz Concierge Full Rollout', 'Complete integration post-acquisition', 'completed', 'high', true, 'enterprise'),
('Q2-2025', 'Inbound Voice AI', 'Pay-by-phone IVR integration', 'completed', 'high', true, 'all'),
('Q3-2025', 'Lease Renewals', 'Automated lease renewal workflows', 'in-progress', 'high', true, 'all'),
('Q3-2025', 'SmartRent Pilot', 'IoT locks integration pilot', 'planned', 'medium', false, 'enterprise'),
('Q3-2025', 'Buzz Persona Config', 'Configurable tone and escalation settings', 'in-progress', 'high', true, 'all'),
('Q4-2025', 'In-app Payment Plans', 'Buzz-driven payment plan creation', 'planned', 'high', true, 'all'),
('Q4-2025', 'Credit Reporting', 'Experian/RentReporters integration', 'planned', 'high', false, 'all'),
('Q4-2025', 'AI Mood Analysis', 'Emotional analysis for escalation prediction', 'planned', 'high', true, 'enterprise'),
('2026', 'Flexible Rent', 'Pay-by-paycheck functionality', 'planned', 'high', true, 'all'),
('2026', 'AI Prediction Models', 'Who/when/how payment prediction', 'planned', 'high', true, 'enterprise'),
('2026', 'Multilingual AI', 'Spanish/Vietnamese support', 'planned', 'medium', true, 'all'),
('2027+', 'AI Swarms', 'Multi-agent recovery orchestration', 'planned', 'high', true, 'enterprise');

-- Insert Market Segments
INSERT INTO MARKET_SEGMENTS (segment_name, segment_type, market_size, penetration_percentage, growth_rate, pay_ready_position, strategic_priority) VALUES
('Large Multifamily (>25K units)', 'multifamily', 50000000000, 15.2, 8.5, 'leader', 'high'),
('Mid-Market Multifamily (2K-25K units)', 'multifamily', 25000000000, 5.8, 12.3, 'challenger', 'high'),
('Student Housing', 'student-housing', 8000000000, 8.2, 6.7, 'challenger', 'medium'),
('Single Family Rental', 'single-family', 35000000000, 0.1, 15.2, 'niche', 'low');

-- Insert AI Capabilities
INSERT INTO AI_CAPABILITIES (capability_name, capability_type, product_integration, ai_model, automation_percentage, human_escalation_rate, performance_metrics) VALUES
('Omnichannel Communication', 'communication', 'BuzzCenter', 'OpenRouter/Pinecone', 85.0, 15.0, '67-91.5% recovery rate in 90 days'),
('Proactive Delinquency Prevention', 'prediction', 'BuzzCenter', 'Custom ML on $3.5B dataset', 80.0, 20.0, '15% reduction in delinquencies'),
('Automated Negotiation', 'automation', 'Buzz Concierge', 'OpenRouter NLP', 90.0, 10.0, 'Payment plans with 75% acceptance'),
('Voice AI Processing', 'communication', 'BuzzCenter', 'OpenRouter Voice', 88.0, 12.0, '24/7 availability, multilingual'),
('Mood Analysis', 'analysis', 'BuzzCenter', 'Custom sentiment models', 85.0, 15.0, 'Escalation prediction accuracy 90%+');

-- Insert Competitive Analysis
INSERT INTO COMPETITIVE_ANALYSIS (competitor_id, threat_assessment, competitive_moats, weaknesses, opportunities, market_share_estimate, strategic_response) 
SELECT 
    competitor_id,
    CASE 
        WHEN company_name = 'EliseAI' THEN 'high'
        WHEN company_name = 'Yardi' THEN 'high'
        WHEN company_name = 'RealPage' THEN 'high'
        WHEN company_name = 'TrueAccord' THEN 'medium'
        ELSE 'medium'
    END,
    CASE 
        WHEN company_name = 'EliseAI' THEN 'Advanced NLP, Proven ROI, Comprehensive Platform'
        WHEN company_name = 'Yardi' THEN 'Market dominance, extensive integrations'
        WHEN company_name = 'RealPage' THEN 'Large customer base, established relationships'
        ELSE 'Specialized focus'
    END,
    CASE 
        WHEN company_name = 'EliseAI' THEN 'Text-only bots, no voice/full recovery'
        WHEN company_name = 'Yardi' THEN 'Fragmented UX, outdated technology'
        WHEN company_name = 'RealPage' THEN 'Outdated platform, acquisition uncertainty'
        ELSE 'Limited AI capabilities'
    END,
    CASE 
        WHEN company_name = 'EliseAI' THEN 'Attack with voice AI + end-to-end recovery'
        WHEN company_name = 'Yardi' THEN 'Unified UX vs fragmented experience'
        WHEN company_name = 'RealPage' THEN 'Modern AI platform vs legacy systems'
        ELSE 'Superior AI automation'
    END,
    CASE 
        WHEN company_name = 'EliseAI' THEN 12.5
        WHEN company_name = 'Yardi' THEN 35.2
        WHEN company_name = 'RealPage' THEN 28.7
        ELSE 5.0
    END,
    'Leverage AI-first approach with voice capabilities and unified lifecycle management'
FROM COMPETITORS 
WHERE company_name IN ('EliseAI', 'Yardi', 'RealPage', 'TrueAccord', 'Hunter Warfield', 'Entrata');

-- =====================================================================
-- ENHANCED SEARCH VIEWS
-- =====================================================================

-- Pay Ready Business Intelligence View
CREATE OR REPLACE VIEW VW_PAY_READY_INTELLIGENCE AS
SELECT
    'COMPANY' AS entity_type,
    company_id AS entity_id,
    company_name AS name,
    CONCAT('Valuation: $', current_valuation/1000000, 'M | Units: ', total_units_contracted/1000000, 'M | Properties: ', total_properties/1000, 'K') AS summary,
    'company_overview' AS category,
    created_at,
    updated_at
FROM COMPANY_OVERVIEW

UNION ALL

SELECT
    'ACQUISITION' AS entity_type,
    acquisition_id AS entity_id,
    acquired_company AS name,
    CONCAT('Acquired: ', acquisition_date, ' | Status: ', integration_status, ' | Value: ', strategic_value) AS summary,
    'acquisition' AS category,
    created_at,
    created_at AS updated_at
FROM ACQUISITIONS

UNION ALL

SELECT
    'ROADMAP' AS entity_type,
    roadmap_id AS entity_id,
    feature_name AS name,
    CONCAT(quarter, ' | Status: ', status, ' | AI: ', CASE WHEN ai_component THEN 'Yes' ELSE 'No' END, ' | Impact: ', estimated_impact) AS summary,
    'product_roadmap' AS category,
    created_at,
    created_at AS updated_at
FROM PRODUCT_ROADMAP

UNION ALL

SELECT
    'AI_CAPABILITY' AS entity_type,
    capability_id AS entity_id,
    capability_name AS name,
    CONCAT('Type: ', capability_type, ' | Automation: ', automation_percentage, '% | Escalation: ', human_escalation_rate, '%') AS summary,
    'ai_capability' AS category,
    created_at,
    created_at AS updated_at
FROM AI_CAPABILITIES;

-- =====================================================================
-- PAY READY SEARCH PROCEDURES
-- =====================================================================

-- Search Pay Ready Business Intelligence
CREATE OR REPLACE PROCEDURE SEARCH_PAY_READY_INTELLIGENCE(SEARCH_TERM STRING)
RETURNS TABLE (
    entity_type STRING,
    entity_id STRING,
    name STRING,
    summary STRING,
    category STRING
)
LANGUAGE SQL
AS
$$
BEGIN
    RETURN TABLE(
        SELECT
            entity_type,
            entity_id,
            name,
            summary,
            category
        FROM VW_PAY_READY_INTELLIGENCE
        WHERE LOWER(name) LIKE LOWER(CONCAT('%', SEARCH_TERM, '%'))
           OR LOWER(summary) LIKE LOWER(CONCAT('%', SEARCH_TERM, '%'))
           OR LOWER(category) LIKE LOWER(CONCAT('%', SEARCH_TERM, '%'))
        ORDER BY
            CASE
                WHEN LOWER(name) = LOWER(SEARCH_TERM) THEN 1
                WHEN LOWER(name) LIKE LOWER(CONCAT(SEARCH_TERM, '%')) THEN 2
                ELSE 3
            END,
            name
        LIMIT 25
    );
END;
$$;

-- Get Product Roadmap by Quarter
CREATE OR REPLACE PROCEDURE GET_ROADMAP_BY_QUARTER(TARGET_QUARTER STRING)
RETURNS TABLE (
    feature_name STRING,
    feature_description STRING,
    status STRING,
    strategic_importance STRING,
    ai_component BOOLEAN,
    target_segment STRING
)
LANGUAGE SQL
AS
$$
BEGIN
    RETURN TABLE(
        SELECT
            feature_name,
            feature_description,
            status,
            strategic_importance,
            ai_component,
            target_segment
        FROM PRODUCT_ROADMAP
        WHERE quarter = TARGET_QUARTER
        ORDER BY 
            CASE strategic_importance
                WHEN 'high' THEN 1
                WHEN 'medium' THEN 2
                WHEN 'low' THEN 3
            END,
            feature_name
    );
END;
$$;

-- =====================================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================================

CREATE INDEX IF NOT EXISTS IDX_ACQUISITIONS_DATE ON ACQUISITIONS(acquisition_date DESC);
CREATE INDEX IF NOT EXISTS IDX_ROADMAP_QUARTER ON PRODUCT_ROADMAP(quarter);
CREATE INDEX IF NOT EXISTS IDX_ROADMAP_STATUS ON PRODUCT_ROADMAP(status);
CREATE INDEX IF NOT EXISTS IDX_AI_CAPABILITIES_TYPE ON AI_CAPABILITIES(capability_type);
CREATE INDEX IF NOT EXISTS IDX_COMPETITIVE_ANALYSIS_DATE ON COMPETITIVE_ANALYSIS(analysis_date DESC);

-- =====================================================================
-- SETUP COMPLETE
-- =====================================================================

SELECT 'Pay Ready foundational knowledge extensions created successfully!' AS STATUS; 