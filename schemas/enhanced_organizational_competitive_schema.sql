-- =====================================================================
-- ENHANCED PAY READY ORGANIZATIONAL & COMPETITIVE INTELLIGENCE SCHEMA
-- Builds on existing FOUNDATIONAL_KNOWLEDGE structure
-- =====================================================================

USE SCHEMA FOUNDATIONAL_KNOWLEDGE;

-- =====================================================================
-- 1. ENHANCED EMPLOYEES TABLE (extends existing)
-- =====================================================================

-- Add columns to existing EMPLOYEES table for competitive intelligence
ALTER TABLE EMPLOYEES ADD COLUMN IF NOT EXISTS 
    COMPETITIVE_FOCUS_AREAS ARRAY DEFAULT [],  -- ['EliseAI', 'Entrata', 'PropertyRadar']
    MARKET_SEGMENTS ARRAY DEFAULT [],          -- ['Multifamily', 'Student Housing', 'Senior Living']
    EXPERTISE_AREAS ARRAY DEFAULT [],          -- ['AI/ML', 'Collections', 'Property Management']
    CUSTOMER_TERRITORIES ARRAY DEFAULT [],     -- ['West Coast', 'NMHC Top 50', 'Mid-Market']
    BATTLE_CARD_ACCESS_LEVEL VARCHAR(50) DEFAULT 'standard', -- 'restricted', 'standard', 'full'
    COMPETITIVE_WIN_RATE DECIMAL(5,2) DEFAULT 0.0,           -- Personal win rate vs competitors
    LAST_COMPETITIVE_TRAINING DATE,                          -- When they last had competitive training
    PREFERRED_BATTLE_CARDS ARRAY DEFAULT [];                 -- ['vs_EliseAI', 'vs_Entrata', 'pricing']

-- =====================================================================
-- 2. ORGANIZATIONAL HIERARCHY ENHANCEMENT
-- =====================================================================

-- Enhanced org chart view with competitive responsibility mapping
CREATE OR REPLACE VIEW VW_PAY_READY_ORG_CHART AS
SELECT 
    e.EMPLOYEE_ID,
    e.FIRST_NAME,
    e.LAST_NAME,
    CONCAT(e.FIRST_NAME, ' ', e.LAST_NAME) as FULL_NAME,
    e.JOB_TITLE,
    e.DEPARTMENT,
    e.EMAIL,
    
    -- Manager relationships
    e.MANAGER_ID,
    CONCAT(m.FIRST_NAME, ' ', m.LAST_NAME) as MANAGER_NAME,
    m.JOB_TITLE as MANAGER_TITLE,
    
    -- Competitive intelligence context
    e.COMPETITIVE_FOCUS_AREAS,
    e.MARKET_SEGMENTS,
    e.EXPERTISE_AREAS,
    e.CUSTOMER_TERRITORIES,
    e.COMPETITIVE_WIN_RATE,
    
    -- Hierarchical path for executive reporting
    CASE 
        WHEN e.JOB_TITLE ILIKE '%CEO%' THEN 1
        WHEN e.JOB_TITLE ILIKE '%VP%' OR e.JOB_TITLE ILIKE '%Chief%' THEN 2
        WHEN e.JOB_TITLE ILIKE '%Director%' THEN 3
        WHEN e.JOB_TITLE ILIKE '%Manager%' THEN 4
        ELSE 5 
    END as HIERARCHY_LEVEL,
    
    -- Executive team identification
    CASE 
        WHEN e.EMAIL = 'lynn@payready.com' THEN 'CEO'
        WHEN e.EMAIL = 'tiffany@payready.com' THEN 'CPO'
        WHEN e.EMAIL = 'steve@payready.com' THEN 'VP_Strategic'
        ELSE 'Team_Member'
    END as EXECUTIVE_ROLE,
    
    e.STATUS,
    e.CREATED_AT,
    e.UPDATED_AT
    
FROM EMPLOYEES e
LEFT JOIN EMPLOYEES m ON e.MANAGER_ID = m.EMPLOYEE_ID
WHERE e.STATUS = 'active'
ORDER BY HIERARCHY_LEVEL, e.DEPARTMENT, e.LAST_NAME;

-- =====================================================================
-- 3. COMPETITIVE-ORGANIZATIONAL RELATIONSHIP PATTERNS
-- =====================================================================

-- Enhanced entity relationships for competitive intelligence
CREATE TABLE IF NOT EXISTS COMPETITIVE_EMPLOYEE_ASSIGNMENTS (
    ASSIGNMENT_ID VARCHAR(255) PRIMARY KEY DEFAULT UUID_STRING(),
    EMPLOYEE_ID VARCHAR(255) NOT NULL,
    COMPETITOR_ID VARCHAR(255) NOT NULL,
    ASSIGNMENT_TYPE VARCHAR(100) NOT NULL, -- 'primary_analyst', 'territory_owner', 'product_specialist'
    RESPONSIBILITY_LEVEL VARCHAR(50) NOT NULL, -- 'lead', 'support', 'monitor'
    WIN_RATE_TARGET DECIMAL(5,2) DEFAULT 75.0,
    CURRENT_WIN_RATE DECIMAL(5,2) DEFAULT 0.0,
    LAST_COMPETITIVE_WIN DATE,
    NOTES TEXT,
    
    -- Metadata
    CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UPDATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CREATED_BY VARCHAR(255) DEFAULT CURRENT_USER,
    
    FOREIGN KEY (EMPLOYEE_ID) REFERENCES EMPLOYEES(EMPLOYEE_ID),
    FOREIGN KEY (COMPETITOR_ID) REFERENCES COMPETITORS(COMPETITOR_ID),
    
    -- Prevent duplicate assignments
    UNIQUE(EMPLOYEE_ID, COMPETITOR_ID, ASSIGNMENT_TYPE)
);

-- =====================================================================
-- 4. ORGANIZATIONAL COMPETITIVE INTELLIGENCE VIEWS
-- =====================================================================

-- Executive competitive overview
CREATE OR REPLACE VIEW VW_EXECUTIVE_COMPETITIVE_OVERVIEW AS
SELECT 
    e.EXECUTIVE_ROLE,
    e.FULL_NAME,
    e.EMAIL,
    e.JOB_TITLE,
    e.DEPARTMENT,
    
    -- Competitive responsibilities
    ARRAY_SIZE(e.COMPETITIVE_FOCUS_AREAS) as COMPETITIVE_FOCUS_COUNT,
    e.COMPETITIVE_FOCUS_AREAS,
    e.COMPETITIVE_WIN_RATE,
    
    -- Team competitive performance (for managers)
    (SELECT AVG(team.COMPETITIVE_WIN_RATE) 
     FROM VW_PAY_READY_ORG_CHART team 
     WHERE team.MANAGER_ID = e.EMPLOYEE_ID) as TEAM_AVG_WIN_RATE,
     
    (SELECT COUNT(*) 
     FROM VW_PAY_READY_ORG_CHART team 
     WHERE team.MANAGER_ID = e.EMPLOYEE_ID) as DIRECT_REPORTS_COUNT,
    
    -- Recent competitive activity
    e.LAST_COMPETITIVE_TRAINING,
    
    e.STATUS
FROM VW_PAY_READY_ORG_CHART e
WHERE e.EXECUTIVE_ROLE IN ('CEO', 'CPO', 'VP_Strategic')
   OR e.HIERARCHY_LEVEL <= 3; -- Include Directors+

-- Department competitive strength analysis
CREATE OR REPLACE VIEW VW_DEPARTMENT_COMPETITIVE_ANALYSIS AS
SELECT 
    DEPARTMENT,
    COUNT(*) as EMPLOYEE_COUNT,
    AVG(COMPETITIVE_WIN_RATE) as AVG_WIN_RATE,
    
    -- Competitive focus distribution
    ARRAY_AGG(DISTINCT ARRAY_TO_STRING(COMPETITIVE_FOCUS_AREAS, ',')) as DEPT_COMPETITIVE_FOCUS,
    
    -- Market segment coverage
    ARRAY_AGG(DISTINCT ARRAY_TO_STRING(MARKET_SEGMENTS, ',')) as DEPT_MARKET_COVERAGE,
    
    -- Expertise areas
    ARRAY_AGG(DISTINCT ARRAY_TO_STRING(EXPERTISE_AREAS, ',')) as DEPT_EXPERTISE,
    
    -- Battle card readiness
    SUM(CASE WHEN BATTLE_CARD_ACCESS_LEVEL = 'full' THEN 1 ELSE 0 END) as FULL_ACCESS_COUNT,
    SUM(CASE WHEN LAST_COMPETITIVE_TRAINING >= CURRENT_DATE - 90 THEN 1 ELSE 0 END) as RECENTLY_TRAINED_COUNT
    
FROM VW_PAY_READY_ORG_CHART
WHERE STATUS = 'active'
GROUP BY DEPARTMENT
ORDER BY AVG_WIN_RATE DESC;

-- =====================================================================
-- 5. SOPHIA AI ACCESS PATTERNS
-- =====================================================================

-- Unified knowledge search enhancement for organizational + competitive
CREATE OR REPLACE VIEW VW_UNIFIED_ORGANIZATIONAL_COMPETITIVE_SEARCH AS
SELECT 
    -- Employee information
    'EMPLOYEE_COMPETITIVE' AS ENTITY_TYPE,
    e.EMPLOYEE_ID AS ENTITY_ID,
    e.FULL_NAME AS NAME,
    e.EMAIL AS PRIMARY_IDENTIFIER,
    e.DEPARTMENT AS CATEGORY,
    
    -- Enhanced description with competitive context
    CONCAT(
        e.JOB_TITLE, ' in ', e.DEPARTMENT,
        CASE WHEN ARRAY_SIZE(e.COMPETITIVE_FOCUS_AREAS) > 0 
             THEN ' - Competitive Focus: ' || ARRAY_TO_STRING(e.COMPETITIVE_FOCUS_AREAS, ', ')
             ELSE '' END,
        CASE WHEN e.COMPETITIVE_WIN_RATE > 0 
             THEN ' - Win Rate: ' || e.COMPETITIVE_WIN_RATE || '%'
             ELSE '' END
    ) AS ENHANCED_DESCRIPTION,
    
    -- Metadata for AI processing
    OBJECT_CONSTRUCT(
        'employee_id', e.EMPLOYEE_ID,
        'full_name', e.FULL_NAME,
        'job_title', e.JOB_TITLE,
        'department', e.DEPARTMENT,
        'email', e.EMAIL,
        'manager_id', e.MANAGER_ID,
        'manager_name', e.MANAGER_NAME,
        'hierarchy_level', e.HIERARCHY_LEVEL,
        'executive_role', e.EXECUTIVE_ROLE,
        'competitive_focus_areas', e.COMPETITIVE_FOCUS_AREAS,
        'market_segments', e.MARKET_SEGMENTS,
        'expertise_areas', e.EXPERTISE_AREAS,
        'competitive_win_rate', e.COMPETITIVE_WIN_RATE,
        'battle_card_access_level', e.BATTLE_CARD_ACCESS_LEVEL
    ) AS METADATA,
    
    e.STATUS,
    e.CREATED_AT,
    e.UPDATED_AT
    
FROM VW_PAY_READY_ORG_CHART e

UNION ALL

SELECT 
    -- Competitor information with organizational context
    'COMPETITOR_WITH_COVERAGE' AS ENTITY_TYPE,
    c.COMPETITOR_ID AS ENTITY_ID,
    c.COMPANY_NAME AS NAME,
    c.WEBSITE AS PRIMARY_IDENTIFIER,
    c.INDUSTRY AS CATEGORY,
    
    -- Enhanced description with coverage information
    CONCAT(
        c.COMPANY_NAME, ' - Threat Level: ', c.THREAT_LEVEL,
        ' - Covered by: ', 
        COALESCE(
            (SELECT ARRAY_TO_STRING(ARRAY_AGG(e.FULL_NAME), ', ')
             FROM COMPETITIVE_EMPLOYEE_ASSIGNMENTS cea
             JOIN EMPLOYEES e ON cea.EMPLOYEE_ID = e.EMPLOYEE_ID
             WHERE cea.COMPETITOR_ID = c.COMPETITOR_ID 
               AND cea.ASSIGNMENT_TYPE = 'primary_analyst'), 
            'Unassigned'
        )
    ) AS ENHANCED_DESCRIPTION,
    
    -- Metadata including organizational coverage
    OBJECT_CONSTRUCT(
        'competitor_id', c.COMPETITOR_ID,
        'company_name', c.COMPANY_NAME,
        'website', c.WEBSITE,
        'industry', c.INDUSTRY,
        'threat_level', c.THREAT_LEVEL,
        'assigned_analysts', 
            (SELECT ARRAY_AGG(OBJECT_CONSTRUCT('employee_id', cea.EMPLOYEE_ID, 'name', e.FULL_NAME, 'role', cea.ASSIGNMENT_TYPE))
             FROM COMPETITIVE_EMPLOYEE_ASSIGNMENTS cea
             JOIN EMPLOYEES e ON cea.EMPLOYEE_ID = e.EMPLOYEE_ID
             WHERE cea.COMPETITOR_ID = c.COMPETITOR_ID),
        'coverage_strength',
            (SELECT COUNT(*) 
             FROM COMPETITIVE_EMPLOYEE_ASSIGNMENTS cea 
             WHERE cea.COMPETITOR_ID = c.COMPETITOR_ID)
    ) AS METADATA,
    
    c.CREATED_AT,
    c.UPDATED_AT,
    c.UPDATED_AT
    
FROM COMPETITORS c;

-- =====================================================================
-- 6. SAMPLE DATA POPULATION
-- =====================================================================

-- Insert Pay Ready executive team (example)
INSERT INTO EMPLOYEES (
    EMPLOYEE_ID, EMAIL, FIRST_NAME, LAST_NAME, JOB_TITLE, DEPARTMENT, 
    COMPETITIVE_FOCUS_AREAS, MARKET_SEGMENTS, EXPERTISE_AREAS, BATTLE_CARD_ACCESS_LEVEL
) VALUES 
(
    'emp_lynn_musil', 'lynn@payready.com', 'Lynn Patrick', 'Musil', 
    'Chief Executive Officer', 'Executive',
    ['EliseAI', 'Entrata', 'YieldStar'], 
    ['Multifamily', 'Student Housing', 'Senior Living'],
    ['Strategic Planning', 'AI/ML', 'Market Analysis'],
    'full'
),
(
    'emp_tiffany_york', 'tiffany@payready.com', 'Tiffany', 'York',
    'Chief Product Officer', 'Product',
    ['EliseAI', 'PropertyRadar', 'Rentspree'],
    ['Multifamily', 'Property Management Tech'],
    ['Product Strategy', 'AI/ML', 'User Experience'],
    'full'
),
(
    'emp_steve_gabel', 'steve@payready.com', 'Steve', 'Gabel',
    'VP Strategic Initiatives', 'Strategy',
    ['Market Analysis', 'Competitive Intelligence'],
    ['All Segments'],
    ['Strategic Planning', 'Market Research', 'Business Development'],
    'full'
)
ON CONFLICT (EMAIL) DO UPDATE SET
    COMPETITIVE_FOCUS_AREAS = EXCLUDED.COMPETITIVE_FOCUS_AREAS,
    MARKET_SEGMENTS = EXCLUDED.MARKET_SEGMENTS,
    EXPERTISE_AREAS = EXCLUDED.EXPERTISE_AREAS,
    BATTLE_CARD_ACCESS_LEVEL = EXCLUDED.BATTLE_CARD_ACCESS_LEVEL;

-- =====================================================================
-- 7. SOPHIA AI QUERY PATTERNS
-- =====================================================================

-- Common queries Sophia AI would use:

-- "Who owns competitive analysis for EliseAI?"
/*
SELECT e.FULL_NAME, e.JOB_TITLE, e.EMAIL, cea.ASSIGNMENT_TYPE, cea.CURRENT_WIN_RATE
FROM COMPETITIVE_EMPLOYEE_ASSIGNMENTS cea
JOIN VW_PAY_READY_ORG_CHART e ON cea.EMPLOYEE_ID = e.EMPLOYEE_ID
JOIN COMPETITORS c ON cea.COMPETITOR_ID = c.COMPETITOR_ID
WHERE c.COMPANY_NAME ILIKE '%EliseAI%'
  AND cea.ASSIGNMENT_TYPE IN ('primary_analyst', 'territory_owner');
*/

-- "Show me competitive win rates by department"
/*
SELECT 
    DEPARTMENT,
    AVG_WIN_RATE,
    EMPLOYEE_COUNT,
    RECENTLY_TRAINED_COUNT
FROM VW_DEPARTMENT_COMPETITIVE_ANALYSIS
ORDER BY AVG_WIN_RATE DESC;
*/

-- "Who should I notify about a new Entrata competitive threat?"
/*
SELECT DISTINCT e.FULL_NAME, e.EMAIL, e.JOB_TITLE
FROM VW_PAY_READY_ORG_CHART e
WHERE 'Entrata' = ANY(e.COMPETITIVE_FOCUS_AREAS)
   OR e.EXECUTIVE_ROLE IN ('CEO', 'CPO', 'VP_Strategic')
   OR e.HIERARCHY_LEVEL <= 2;
*/

-- =====================================================================
-- 8. INDEXES FOR PERFORMANCE
-- =====================================================================

CREATE INDEX IF NOT EXISTS idx_employees_competitive_focus ON EMPLOYEES USING GIN(COMPETITIVE_FOCUS_AREAS);
CREATE INDEX IF NOT EXISTS idx_employees_market_segments ON EMPLOYEES USING GIN(MARKET_SEGMENTS);
CREATE INDEX IF NOT EXISTS idx_employees_hierarchy ON EMPLOYEES(HIERARCHY_LEVEL, DEPARTMENT);
CREATE INDEX IF NOT EXISTS idx_competitive_assignments_employee ON COMPETITIVE_EMPLOYEE_ASSIGNMENTS(EMPLOYEE_ID);
CREATE INDEX IF NOT EXISTS idx_competitive_assignments_competitor ON COMPETITIVE_EMPLOYEE_ASSIGNMENTS(COMPETITOR_ID);

-- =====================================================================
-- END SCHEMA
-- ===================================================================== 