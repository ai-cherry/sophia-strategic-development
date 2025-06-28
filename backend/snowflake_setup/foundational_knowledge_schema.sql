-- =====================================================================
-- Foundational Knowledge Base Schema for Pay Ready
-- =====================================================================
-- 
-- This schema creates the foundational knowledge infrastructure for Pay Ready,
-- storing critical business information that will be contextualized with
-- Gong calls, Slack conversations, and other operational data.
--
-- Schema: FOUNDATIONAL_KNOWLEDGE
-- Purpose: Central repository for organizational knowledge and business context
-- =====================================================================

USE DATABASE SOPHIA_AI;
CREATE SCHEMA IF NOT EXISTS FOUNDATIONAL_KNOWLEDGE;
USE SCHEMA FOUNDATIONAL_KNOWLEDGE;

-- =====================================================================
-- 1. ORGANIZATIONAL STRUCTURE
-- =====================================================================

-- Employee directory and organizational structure
CREATE TABLE IF NOT EXISTS EMPLOYEES (
    EMPLOYEE_ID VARCHAR(255) PRIMARY KEY,
    EMPLOYEE_NUMBER VARCHAR(50) UNIQUE,
    
    -- Personal information
    FIRST_NAME VARCHAR(255) NOT NULL,
    LAST_NAME VARCHAR(255) NOT NULL,
    FULL_NAME VARCHAR(500) GENERATED ALWAYS AS (FIRST_NAME || ' ' || LAST_NAME),
    EMAIL_ADDRESS VARCHAR(255) UNIQUE NOT NULL,
    PHONE_NUMBER VARCHAR(50),
    
    -- Organizational information
    DEPARTMENT VARCHAR(100), -- 'Sales', 'Engineering', 'Marketing', 'Operations', 'Executive'
    TEAM VARCHAR(100), -- Sub-team within department
    JOB_TITLE VARCHAR(255),
    EMPLOYEE_LEVEL VARCHAR(50), -- 'Individual Contributor', 'Manager', 'Director', 'VP', 'C-Level'
    REPORTS_TO_EMPLOYEE_ID VARCHAR(255), -- Self-referencing for org chart
    
    -- Employment details
    HIRE_DATE DATE,
    EMPLOYMENT_STATUS VARCHAR(50) DEFAULT 'Active', -- 'Active', 'On Leave', 'Terminated'
    EMPLOYMENT_TYPE VARCHAR(50), -- 'Full-Time', 'Part-Time', 'Contract', 'Intern'
    LOCATION VARCHAR(255), -- 'Remote', 'New York', 'San Francisco', etc.
    TIMEZONE VARCHAR(50) DEFAULT 'America/New_York',
    
    -- Skills and expertise
    PRIMARY_SKILLS VARIANT, -- JSON array of primary skills
    SECONDARY_SKILLS VARIANT, -- JSON array of secondary skills
    CERTIFICATIONS VARIANT, -- JSON array of certifications
    LANGUAGES VARIANT, -- JSON array of spoken languages
    
    -- Communication preferences
    SLACK_USER_ID VARCHAR(255), -- For Slack integration
    GONG_USER_ID VARCHAR(255), -- For Gong integration
    HUBSPOT_OWNER_ID VARCHAR(255), -- For HubSpot integration
    
    -- AI Memory integration
    AI_MEMORY_EMBEDDING VECTOR(FLOAT, 768), -- For semantic search
    AI_MEMORY_METADATA VARCHAR(16777216), -- JSON metadata
    AI_MEMORY_UPDATED_AT TIMESTAMP_NTZ,
    
    -- Metadata
    CREATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    UPDATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    CREATED_BY VARCHAR(255),
    UPDATED_BY VARCHAR(255),
    
    -- Constraints
    FOREIGN KEY (REPORTS_TO_EMPLOYEE_ID) REFERENCES EMPLOYEES(EMPLOYEE_ID)
);

-- Team structure and relationships
CREATE TABLE IF NOT EXISTS TEAMS (
    TEAM_ID VARCHAR(255) PRIMARY KEY,
    TEAM_NAME VARCHAR(255) NOT NULL,
    TEAM_DESCRIPTION VARCHAR(1000),
    DEPARTMENT VARCHAR(100),
    
    -- Team leadership
    TEAM_LEAD_EMPLOYEE_ID VARCHAR(255),
    MANAGER_EMPLOYEE_ID VARCHAR(255),
    
    -- Team configuration
    TEAM_TYPE VARCHAR(50), -- 'Functional', 'Cross-Functional', 'Project', 'Committee'
    TEAM_STATUS VARCHAR(50) DEFAULT 'Active', -- 'Active', 'Inactive', 'Archived'
    
    -- Communication channels
    SLACK_CHANNEL_ID VARCHAR(255),
    PRIMARY_COMMUNICATION_CHANNEL VARCHAR(255),
    
    -- Metadata
    CREATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    UPDATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    
    FOREIGN KEY (TEAM_LEAD_EMPLOYEE_ID) REFERENCES EMPLOYEES(EMPLOYEE_ID),
    FOREIGN KEY (MANAGER_EMPLOYEE_ID) REFERENCES EMPLOYEES(EMPLOYEE_ID)
);

-- =====================================================================
-- 2. CUSTOMER KNOWLEDGE BASE
-- =====================================================================

-- Customer master data
CREATE TABLE IF NOT EXISTS CUSTOMERS (
    CUSTOMER_ID VARCHAR(255) PRIMARY KEY,
    CUSTOMER_NUMBER VARCHAR(50) UNIQUE,
    
    -- Company information
    COMPANY_NAME VARCHAR(500) NOT NULL,
    LEGAL_COMPANY_NAME VARCHAR(500),
    DOING_BUSINESS_AS VARCHAR(500),
    COMPANY_WEBSITE VARCHAR(500),
    
    -- Industry classification
    INDUSTRY VARCHAR(255),
    SUB_INDUSTRY VARCHAR(255),
    INDUSTRY_CATEGORY VARCHAR(100), -- 'Property Management', 'Real Estate', 'Financial Services'
    COMPANY_SIZE VARCHAR(50), -- 'Small', 'Medium', 'Large', 'Enterprise'
    EMPLOYEE_COUNT_RANGE VARCHAR(50), -- '1-50', '51-200', '201-1000', '1000+'
    ANNUAL_REVENUE_RANGE VARCHAR(50), -- '<$1M', '$1M-$10M', '$10M-$100M', '$100M+'
    
    -- Geographic information
    HEADQUARTERS_ADDRESS VARCHAR(1000),
    HEADQUARTERS_CITY VARCHAR(255),
    HEADQUARTERS_STATE VARCHAR(100),
    HEADQUARTERS_COUNTRY VARCHAR(100),
    HEADQUARTERS_POSTAL_CODE VARCHAR(20),
    OPERATING_REGIONS VARIANT, -- JSON array of regions where they operate
    
    -- Business model and characteristics
    BUSINESS_MODEL VARCHAR(255), -- 'B2B', 'B2C', 'B2B2C', 'Marketplace'
    CUSTOMER_SEGMENT VARCHAR(255), -- 'Enterprise', 'Mid-Market', 'SMB'
    PAYMENT_PROCESSING_VOLUME_MONTHLY NUMBER(15,2),
    PROPERTY_PORTFOLIO_SIZE NUMBER,
    
    -- Relationship information
    CUSTOMER_STATUS VARCHAR(50) DEFAULT 'Active', -- 'Prospect', 'Active', 'Churned', 'Inactive'
    CUSTOMER_TIER VARCHAR(50), -- 'Strategic', 'Key', 'Standard', 'Basic'
    ACQUISITION_DATE DATE,
    FIRST_CONTRACT_DATE DATE,
    LAST_CONTRACT_DATE DATE,
    
    -- Account management
    ACCOUNT_MANAGER_EMPLOYEE_ID VARCHAR(255),
    CUSTOMER_SUCCESS_MANAGER_EMPLOYEE_ID VARCHAR(255),
    SALES_REP_EMPLOYEE_ID VARCHAR(255),
    
    -- Integration IDs
    HUBSPOT_COMPANY_ID VARCHAR(255),
    SALESFORCE_ACCOUNT_ID VARCHAR(255),
    STRIPE_CUSTOMER_ID VARCHAR(255),
    
    -- AI Memory integration
    AI_MEMORY_EMBEDDING VECTOR(FLOAT, 768),
    AI_MEMORY_METADATA VARCHAR(16777216),
    AI_MEMORY_UPDATED_AT TIMESTAMP_NTZ,
    
    -- Metadata
    CREATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    UPDATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    CREATED_BY VARCHAR(255),
    UPDATED_BY VARCHAR(255),
    
    FOREIGN KEY (ACCOUNT_MANAGER_EMPLOYEE_ID) REFERENCES EMPLOYEES(EMPLOYEE_ID),
    FOREIGN KEY (CUSTOMER_SUCCESS_MANAGER_EMPLOYEE_ID) REFERENCES EMPLOYEES(EMPLOYEE_ID),
    FOREIGN KEY (SALES_REP_EMPLOYEE_ID) REFERENCES EMPLOYEES(EMPLOYEE_ID)
);

-- Customer contacts and decision makers
CREATE TABLE IF NOT EXISTS CUSTOMER_CONTACTS (
    CONTACT_ID VARCHAR(255) PRIMARY KEY,
    CUSTOMER_ID VARCHAR(255) NOT NULL,
    
    -- Contact information
    FIRST_NAME VARCHAR(255),
    LAST_NAME VARCHAR(255),
    FULL_NAME VARCHAR(500) GENERATED ALWAYS AS (FIRST_NAME || ' ' || LAST_NAME),
    EMAIL_ADDRESS VARCHAR(255),
    PHONE_NUMBER VARCHAR(50),
    
    -- Role and influence
    JOB_TITLE VARCHAR(255),
    DEPARTMENT VARCHAR(255),
    SENIORITY_LEVEL VARCHAR(100), -- 'C-Level', 'VP', 'Director', 'Manager', 'Individual Contributor'
    DECISION_MAKING_ROLE VARCHAR(100), -- 'Decision Maker', 'Influencer', 'User', 'Gatekeeper'
    INFLUENCE_SCORE NUMBER(3,2), -- 0.0 to 1.0 scale
    
    -- Engagement preferences
    PREFERRED_COMMUNICATION VARCHAR(100), -- 'Email', 'Phone', 'Slack', 'In-Person'
    COMMUNICATION_FREQUENCY VARCHAR(50), -- 'Daily', 'Weekly', 'Monthly', 'Quarterly'
    BEST_CONTACT_TIME VARCHAR(100),
    
    -- Relationship tracking
    RELATIONSHIP_STRENGTH VARCHAR(50), -- 'Strong', 'Medium', 'Weak', 'Unknown'
    LAST_INTERACTION_DATE DATE,
    INTERACTION_COUNT NUMBER DEFAULT 0,
    
    -- Integration IDs
    HUBSPOT_CONTACT_ID VARCHAR(255),
    SALESFORCE_CONTACT_ID VARCHAR(255),
    LINKEDIN_PROFILE_URL VARCHAR(500),
    
    -- AI Memory integration
    AI_MEMORY_EMBEDDING VECTOR(FLOAT, 768),
    AI_MEMORY_METADATA VARCHAR(16777216),
    AI_MEMORY_UPDATED_AT TIMESTAMP_NTZ,
    
    -- Metadata
    CREATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    UPDATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    IS_ACTIVE BOOLEAN DEFAULT TRUE,
    
    FOREIGN KEY (CUSTOMER_ID) REFERENCES CUSTOMERS(CUSTOMER_ID)
);

-- =====================================================================
-- 3. PRODUCT AND SERVICE CATALOG
-- =====================================================================

-- Product and service offerings
CREATE TABLE IF NOT EXISTS PRODUCTS_SERVICES (
    PRODUCT_ID VARCHAR(255) PRIMARY KEY,
    PRODUCT_CODE VARCHAR(100) UNIQUE,
    
    -- Product information
    PRODUCT_NAME VARCHAR(500) NOT NULL,
    PRODUCT_DESCRIPTION VARCHAR(4000),
    PRODUCT_CATEGORY VARCHAR(255), -- 'Payment Processing', 'Property Management', 'Analytics'
    PRODUCT_TYPE VARCHAR(100), -- 'Core Product', 'Add-On', 'Service', 'Integration'
    
    -- Product details
    PRODUCT_STATUS VARCHAR(50) DEFAULT 'Active', -- 'Active', 'Beta', 'Deprecated', 'Discontinued'
    LAUNCH_DATE DATE,
    RETIREMENT_DATE DATE,
    
    -- Pricing information
    PRICING_MODEL VARCHAR(100), -- 'Subscription', 'Transaction-Based', 'One-Time', 'Custom'
    BASE_PRICE NUMBER(15,2),
    PRICING_CURRENCY VARCHAR(10) DEFAULT 'USD',
    PRICING_FREQUENCY VARCHAR(50), -- 'Monthly', 'Annual', 'Per Transaction', 'Per Unit'
    
    -- Product positioning
    TARGET_CUSTOMER_SEGMENT VARCHAR(255),
    VALUE_PROPOSITION VARCHAR(1000),
    KEY_BENEFITS VARIANT, -- JSON array of key benefits
    COMPETITIVE_ADVANTAGES VARIANT, -- JSON array of competitive advantages
    
    -- Technical specifications
    TECHNICAL_REQUIREMENTS VARIANT, -- JSON object with technical requirements
    INTEGRATION_CAPABILITIES VARIANT, -- JSON array of integration options
    API_ENDPOINTS VARIANT, -- JSON array of API endpoints
    
    -- Sales and marketing information
    SALES_PLAYBOOK_URL VARCHAR(500),
    MARKETING_MATERIALS VARIANT, -- JSON array of marketing material URLs
    DEMO_SCRIPT_URL VARCHAR(500),
    PRICING_SHEET_URL VARCHAR(500),
    
    -- Performance metrics
    MONTHLY_RECURRING_REVENUE NUMBER(15,2),
    CUSTOMER_COUNT NUMBER,
    CHURN_RATE FLOAT,
    CUSTOMER_SATISFACTION_SCORE FLOAT,
    
    -- Product management
    PRODUCT_MANAGER_EMPLOYEE_ID VARCHAR(255),
    ENGINEERING_LEAD_EMPLOYEE_ID VARCHAR(255),
    
    -- AI Memory integration
    AI_MEMORY_EMBEDDING VECTOR(FLOAT, 768),
    AI_MEMORY_METADATA VARCHAR(16777216),
    AI_MEMORY_UPDATED_AT TIMESTAMP_NTZ,
    
    -- Metadata
    CREATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    UPDATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    CREATED_BY VARCHAR(255),
    UPDATED_BY VARCHAR(255),
    
    FOREIGN KEY (PRODUCT_MANAGER_EMPLOYEE_ID) REFERENCES EMPLOYEES(EMPLOYEE_ID),
    FOREIGN KEY (ENGINEERING_LEAD_EMPLOYEE_ID) REFERENCES EMPLOYEES(EMPLOYEE_ID)
);

-- Product features and capabilities
CREATE TABLE IF NOT EXISTS PRODUCT_FEATURES (
    FEATURE_ID VARCHAR(255) PRIMARY KEY,
    PRODUCT_ID VARCHAR(255) NOT NULL,
    
    -- Feature information
    FEATURE_NAME VARCHAR(500) NOT NULL,
    FEATURE_DESCRIPTION VARCHAR(2000),
    FEATURE_CATEGORY VARCHAR(255),
    FEATURE_TYPE VARCHAR(100), -- 'Core', 'Premium', 'Add-On', 'Beta'
    
    -- Feature status
    FEATURE_STATUS VARCHAR(50) DEFAULT 'Active', -- 'Active', 'Beta', 'Planned', 'Deprecated'
    RELEASE_DATE DATE,
    DEPRECATION_DATE DATE,
    
    -- Feature details
    BUSINESS_VALUE VARCHAR(1000),
    TECHNICAL_COMPLEXITY VARCHAR(50), -- 'Low', 'Medium', 'High'
    CUSTOMER_IMPACT VARCHAR(50), -- 'Low', 'Medium', 'High', 'Critical'
    
    -- Usage and adoption
    ADOPTION_RATE FLOAT, -- Percentage of customers using this feature
    CUSTOMER_FEEDBACK_SCORE FLOAT,
    SUPPORT_TICKET_COUNT NUMBER DEFAULT 0,
    
    -- AI Memory integration
    AI_MEMORY_EMBEDDING VECTOR(FLOAT, 768),
    AI_MEMORY_METADATA VARCHAR(16777216),
    AI_MEMORY_UPDATED_AT TIMESTAMP_NTZ,
    
    -- Metadata
    CREATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    UPDATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    
    FOREIGN KEY (PRODUCT_ID) REFERENCES PRODUCTS_SERVICES(PRODUCT_ID)
);

-- =====================================================================
-- 4. COMPETITIVE INTELLIGENCE
-- =====================================================================

-- Competitor profiles
CREATE TABLE IF NOT EXISTS COMPETITORS (
    COMPETITOR_ID VARCHAR(255) PRIMARY KEY,
    
    -- Company information
    COMPANY_NAME VARCHAR(500) NOT NULL,
    COMPANY_WEBSITE VARCHAR(500),
    COMPANY_DESCRIPTION VARCHAR(2000),
    
    -- Market position
    MARKET_SEGMENT VARCHAR(255), -- 'Direct Competitor', 'Indirect Competitor', 'Adjacent Player'
    COMPETITIVE_TIER VARCHAR(50), -- 'Tier 1', 'Tier 2', 'Tier 3', 'Emerging'
    THREAT_LEVEL VARCHAR(50), -- 'High', 'Medium', 'Low'
    MARKET_SHARE_ESTIMATE FLOAT, -- Estimated market share percentage
    
    -- Company details
    COMPANY_SIZE VARCHAR(50),
    EMPLOYEE_COUNT_ESTIMATE NUMBER,
    ANNUAL_REVENUE_ESTIMATE NUMBER(15,2),
    FUNDING_STATUS VARCHAR(100), -- 'Public', 'Private', 'Startup', 'Acquired'
    LAST_FUNDING_ROUND VARCHAR(100),
    LAST_FUNDING_AMOUNT NUMBER(15,2),
    
    -- Geographic presence
    HEADQUARTERS_LOCATION VARCHAR(255),
    GEOGRAPHIC_PRESENCE VARIANT, -- JSON array of regions/countries
    
    -- Competitive analysis
    STRENGTHS VARIANT, -- JSON array of competitive strengths
    WEAKNESSES VARIANT, -- JSON array of competitive weaknesses
    DIFFERENTIATION_FACTORS VARIANT, -- JSON array of key differentiators
    
    -- Monitoring and intelligence
    MONITORING_PRIORITY VARCHAR(50), -- 'High', 'Medium', 'Low'
    LAST_INTELLIGENCE_UPDATE DATE,
    INTELLIGENCE_SOURCES VARIANT, -- JSON array of intelligence sources
    
    -- Win/loss tracking
    WINS_AGAINST_COMPETITOR NUMBER DEFAULT 0,
    LOSSES_TO_COMPETITOR NUMBER DEFAULT 0,
    WIN_RATE FLOAT GENERATED ALWAYS AS (
        CASE 
            WHEN (WINS_AGAINST_COMPETITOR + LOSSES_TO_COMPETITOR) > 0 
            THEN WINS_AGAINST_COMPETITOR::FLOAT / (WINS_AGAINST_COMPETITOR + LOSSES_TO_COMPETITOR)
            ELSE NULL 
        END
    ),
    
    -- AI Memory integration
    AI_MEMORY_EMBEDDING VECTOR(FLOAT, 768),
    AI_MEMORY_METADATA VARCHAR(16777216),
    AI_MEMORY_UPDATED_AT TIMESTAMP_NTZ,
    
    -- Metadata
    CREATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    UPDATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    CREATED_BY VARCHAR(255),
    UPDATED_BY VARCHAR(255)
);

-- Competitor products and offerings
CREATE TABLE IF NOT EXISTS COMPETITOR_PRODUCTS (
    COMPETITOR_PRODUCT_ID VARCHAR(255) PRIMARY KEY,
    COMPETITOR_ID VARCHAR(255) NOT NULL,
    
    -- Product information
    PRODUCT_NAME VARCHAR(500) NOT NULL,
    PRODUCT_DESCRIPTION VARCHAR(2000),
    PRODUCT_CATEGORY VARCHAR(255),
    
    -- Competitive positioning
    COMPETES_WITH_PRODUCT_ID VARCHAR(255), -- References our PRODUCTS_SERVICES
    COMPETITIVE_ADVANTAGE VARCHAR(1000),
    COMPETITIVE_DISADVANTAGE VARCHAR(1000),
    
    -- Pricing intelligence
    PRICING_MODEL VARCHAR(100),
    ESTIMATED_PRICE NUMBER(15,2),
    PRICING_CURRENCY VARCHAR(10) DEFAULT 'USD',
    PRICING_NOTES VARCHAR(1000),
    
    -- Market intelligence
    MARKET_POSITION VARCHAR(100), -- 'Market Leader', 'Strong Player', 'Niche Player'
    CUSTOMER_COUNT_ESTIMATE NUMBER,
    CUSTOMER_FEEDBACK_SUMMARY VARCHAR(2000),
    
    -- Intelligence tracking
    LAST_UPDATED DATE,
    INTELLIGENCE_CONFIDENCE VARCHAR(50), -- 'High', 'Medium', 'Low'
    
    -- AI Memory integration
    AI_MEMORY_EMBEDDING VECTOR(FLOAT, 768),
    AI_MEMORY_METADATA VARCHAR(16777216),
    AI_MEMORY_UPDATED_AT TIMESTAMP_NTZ,
    
    -- Metadata
    CREATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    UPDATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    
    FOREIGN KEY (COMPETITOR_ID) REFERENCES COMPETITORS(COMPETITOR_ID),
    FOREIGN KEY (COMPETES_WITH_PRODUCT_ID) REFERENCES PRODUCTS_SERVICES(PRODUCT_ID)
);

-- =====================================================================
-- 5. ORGANIZATIONAL KNOWLEDGE
-- =====================================================================

-- Company mission, vision, and values
CREATE TABLE IF NOT EXISTS ORGANIZATIONAL_VALUES (
    VALUE_ID VARCHAR(255) PRIMARY KEY,
    VALUE_TYPE VARCHAR(100), -- 'Mission', 'Vision', 'Core Value', 'Principle', 'Goal'
    
    -- Value information
    VALUE_NAME VARCHAR(255) NOT NULL,
    VALUE_STATEMENT VARCHAR(2000) NOT NULL,
    VALUE_DESCRIPTION VARCHAR(4000),
    
    -- Context and application
    APPLICABLE_CONTEXTS VARIANT, -- JSON array of where this value applies
    BEHAVIORAL_EXAMPLES VARIANT, -- JSON array of behavioral examples
    SUCCESS_METRICS VARIANT, -- JSON array of success metrics
    
    -- Organization hierarchy
    APPLIES_TO_DEPARTMENT VARCHAR(255), -- NULL means company-wide
    PRIORITY_LEVEL VARCHAR(50), -- 'Critical', 'High', 'Medium', 'Low'
    
    -- Tracking and measurement
    LAST_REVIEWED_DATE DATE,
    REVIEW_FREQUENCY VARCHAR(50), -- 'Annual', 'Semi-Annual', 'Quarterly'
    CHAMPION_EMPLOYEE_ID VARCHAR(255), -- Employee responsible for this value
    
    -- AI Memory integration
    AI_MEMORY_EMBEDDING VECTOR(FLOAT, 768),
    AI_MEMORY_METADATA VARCHAR(16777216),
    AI_MEMORY_UPDATED_AT TIMESTAMP_NTZ,
    
    -- Metadata
    CREATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    UPDATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    CREATED_BY VARCHAR(255),
    UPDATED_BY VARCHAR(255),
    IS_ACTIVE BOOLEAN DEFAULT TRUE,
    
    FOREIGN KEY (CHAMPION_EMPLOYEE_ID) REFERENCES EMPLOYEES(EMPLOYEE_ID)
);

-- Business processes and procedures
CREATE TABLE IF NOT EXISTS BUSINESS_PROCESSES (
    PROCESS_ID VARCHAR(255) PRIMARY KEY,
    
    -- Process information
    PROCESS_NAME VARCHAR(500) NOT NULL,
    PROCESS_DESCRIPTION VARCHAR(4000),
    PROCESS_CATEGORY VARCHAR(255), -- 'Sales', 'Marketing', 'Operations', 'HR', 'Finance'
    PROCESS_TYPE VARCHAR(100), -- 'Standard Operating Procedure', 'Workflow', 'Policy', 'Guideline'
    
    -- Process details
    PROCESS_OWNER_EMPLOYEE_ID VARCHAR(255),
    PROCESS_STATUS VARCHAR(50) DEFAULT 'Active', -- 'Active', 'Under Review', 'Deprecated', 'Draft'
    PROCESS_VERSION VARCHAR(50) DEFAULT '1.0',
    
    -- Documentation
    PROCESS_DOCUMENTATION_URL VARCHAR(500),
    PROCESS_STEPS VARIANT, -- JSON array of process steps
    REQUIRED_TOOLS VARIANT, -- JSON array of required tools/systems
    REQUIRED_SKILLS VARIANT, -- JSON array of required skills
    
    -- Process metrics
    AVERAGE_COMPLETION_TIME_MINUTES NUMBER,
    SUCCESS_RATE FLOAT,
    ERROR_RATE FLOAT,
    CUSTOMER_IMPACT_SCORE FLOAT,
    
    -- Compliance and governance
    COMPLIANCE_REQUIREMENTS VARIANT, -- JSON array of compliance requirements
    AUDIT_FREQUENCY VARCHAR(50), -- 'Monthly', 'Quarterly', 'Annual'
    LAST_AUDIT_DATE DATE,
    NEXT_AUDIT_DATE DATE,
    
    -- Training and enablement
    TRAINING_REQUIRED BOOLEAN DEFAULT FALSE,
    TRAINING_MATERIALS VARIANT, -- JSON array of training material URLs
    CERTIFICATION_REQUIRED BOOLEAN DEFAULT FALSE,
    
    -- AI Memory integration
    AI_MEMORY_EMBEDDING VECTOR(FLOAT, 768),
    AI_MEMORY_METADATA VARCHAR(16777216),
    AI_MEMORY_UPDATED_AT TIMESTAMP_NTZ,
    
    -- Metadata
    CREATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    UPDATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    CREATED_BY VARCHAR(255),
    UPDATED_BY VARCHAR(255),
    LAST_REVIEWED_DATE DATE,
    
    FOREIGN KEY (PROCESS_OWNER_EMPLOYEE_ID) REFERENCES EMPLOYEES(EMPLOYEE_ID)
);

-- =====================================================================
-- 6. KNOWLEDGE ARTICLES AND DOCUMENTATION
-- =====================================================================

-- Knowledge base articles
CREATE TABLE IF NOT EXISTS KNOWLEDGE_ARTICLES (
    ARTICLE_ID VARCHAR(255) PRIMARY KEY,
    
    -- Article information
    ARTICLE_TITLE VARCHAR(500) NOT NULL,
    ARTICLE_CONTENT VARCHAR(16777216), -- Full article content
    ARTICLE_SUMMARY VARCHAR(2000),
    ARTICLE_CATEGORY VARCHAR(255), -- 'FAQ', 'How-To', 'Policy', 'Product Info', 'Process'
    ARTICLE_TYPE VARCHAR(100), -- 'Internal', 'Customer-Facing', 'Partner-Facing'
    
    -- Content management
    CONTENT_FORMAT VARCHAR(50), -- 'Markdown', 'HTML', 'Plain Text', 'Rich Text'
    CONTENT_SOURCE VARCHAR(255), -- 'Manual', 'Imported', 'Generated', 'Confluence', 'Notion'
    CONTENT_STATUS VARCHAR(50) DEFAULT 'Published', -- 'Draft', 'Review', 'Published', 'Archived'
    
    -- Authorship and ownership
    AUTHOR_EMPLOYEE_ID VARCHAR(255),
    CONTENT_OWNER_EMPLOYEE_ID VARCHAR(255),
    REVIEWER_EMPLOYEE_ID VARCHAR(255),
    
    -- Access control
    VISIBILITY_LEVEL VARCHAR(50) DEFAULT 'Internal', -- 'Public', 'Internal', 'Restricted', 'Confidential'
    ACCESSIBLE_DEPARTMENTS VARIANT, -- JSON array of departments with access
    ACCESSIBLE_ROLES VARIANT, -- JSON array of roles with access
    
    -- Content metrics
    VIEW_COUNT NUMBER DEFAULT 0,
    LIKE_COUNT NUMBER DEFAULT 0,
    SHARE_COUNT NUMBER DEFAULT 0,
    AVERAGE_RATING FLOAT,
    RATING_COUNT NUMBER DEFAULT 0,
    
    -- Content lifecycle
    PUBLISH_DATE DATE,
    LAST_UPDATED_DATE DATE,
    REVIEW_FREQUENCY VARCHAR(50), -- 'Monthly', 'Quarterly', 'Annual', 'As Needed'
    NEXT_REVIEW_DATE DATE,
    EXPIRATION_DATE DATE,
    
    -- SEO and discoverability
    KEYWORDS VARIANT, -- JSON array of keywords
    TAGS VARIANT, -- JSON array of tags
    RELATED_ARTICLES VARIANT, -- JSON array of related article IDs
    
    -- AI Memory integration
    AI_MEMORY_EMBEDDING VECTOR(FLOAT, 768),
    AI_MEMORY_METADATA VARCHAR(16777216),
    AI_MEMORY_UPDATED_AT TIMESTAMP_NTZ,
    
    -- Metadata
    CREATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    UPDATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    CREATED_BY VARCHAR(255),
    UPDATED_BY VARCHAR(255),
    
    FOREIGN KEY (AUTHOR_EMPLOYEE_ID) REFERENCES EMPLOYEES(EMPLOYEE_ID),
    FOREIGN KEY (CONTENT_OWNER_EMPLOYEE_ID) REFERENCES EMPLOYEES(EMPLOYEE_ID),
    FOREIGN KEY (REVIEWER_EMPLOYEE_ID) REFERENCES EMPLOYEES(EMPLOYEE_ID)
);

-- =====================================================================
-- 7. INTEGRATION VIEWS AND PROCEDURES
-- =====================================================================

-- Comprehensive knowledge search view
CREATE OR REPLACE VIEW VW_COMPREHENSIVE_KNOWLEDGE_SEARCH AS
SELECT 
    'EMPLOYEE' AS KNOWLEDGE_TYPE,
    EMPLOYEE_ID AS RECORD_ID,
    FULL_NAME AS TITLE,
    (DEPARTMENT || ' - ' || JOB_TITLE) AS DESCRIPTION,
    EMAIL_ADDRESS AS CONTACT_INFO,
    AI_MEMORY_EMBEDDING,
    AI_MEMORY_METADATA,
    UPDATED_AT
FROM EMPLOYEES
WHERE EMPLOYMENT_STATUS = 'Active'

UNION ALL

SELECT 
    'CUSTOMER' AS KNOWLEDGE_TYPE,
    CUSTOMER_ID AS RECORD_ID,
    COMPANY_NAME AS TITLE,
    (INDUSTRY || ' - ' || CUSTOMER_SEGMENT) AS DESCRIPTION,
    COMPANY_WEBSITE AS CONTACT_INFO,
    AI_MEMORY_EMBEDDING,
    AI_MEMORY_METADATA,
    UPDATED_AT
FROM CUSTOMERS
WHERE CUSTOMER_STATUS = 'Active'

UNION ALL

SELECT 
    'PRODUCT' AS KNOWLEDGE_TYPE,
    PRODUCT_ID AS RECORD_ID,
    PRODUCT_NAME AS TITLE,
    PRODUCT_DESCRIPTION AS DESCRIPTION,
    PRICING_MODEL AS CONTACT_INFO,
    AI_MEMORY_EMBEDDING,
    AI_MEMORY_METADATA,
    UPDATED_AT
FROM PRODUCTS_SERVICES
WHERE PRODUCT_STATUS = 'Active'

UNION ALL

SELECT 
    'COMPETITOR' AS KNOWLEDGE_TYPE,
    COMPETITOR_ID AS RECORD_ID,
    COMPANY_NAME AS TITLE,
    COMPANY_DESCRIPTION AS DESCRIPTION,
    COMPANY_WEBSITE AS CONTACT_INFO,
    AI_MEMORY_EMBEDDING,
    AI_MEMORY_METADATA,
    UPDATED_AT
FROM COMPETITORS

UNION ALL

SELECT 
    'PROCESS' AS KNOWLEDGE_TYPE,
    PROCESS_ID AS RECORD_ID,
    PROCESS_NAME AS TITLE,
    PROCESS_DESCRIPTION AS DESCRIPTION,
    PROCESS_DOCUMENTATION_URL AS CONTACT_INFO,
    AI_MEMORY_EMBEDDING,
    AI_MEMORY_METADATA,
    UPDATED_AT
FROM BUSINESS_PROCESSES
WHERE PROCESS_STATUS = 'Active'

UNION ALL

SELECT 
    'ARTICLE' AS KNOWLEDGE_TYPE,
    ARTICLE_ID AS RECORD_ID,
    ARTICLE_TITLE AS TITLE,
    ARTICLE_SUMMARY AS DESCRIPTION,
    ARTICLE_CATEGORY AS CONTACT_INFO,
    AI_MEMORY_EMBEDDING,
    AI_MEMORY_METADATA,
    UPDATED_AT
FROM KNOWLEDGE_ARTICLES
WHERE CONTENT_STATUS = 'Published';

-- Procedure to generate embeddings for foundational knowledge
CREATE OR REPLACE PROCEDURE GENERATE_FOUNDATIONAL_KNOWLEDGE_EMBEDDINGS()
RETURNS STRING
LANGUAGE SQL
AS
$$
DECLARE
    processed_count NUMBER DEFAULT 0;
BEGIN
    
    -- Generate embeddings for employees
    UPDATE EMPLOYEES
    SET 
        AI_MEMORY_EMBEDDING = SNOWFLAKE.CORTEX.EMBED_TEXT('e5-base-v2', 
            FULL_NAME || ' ' || 
            COALESCE(JOB_TITLE, '') || ' ' || 
            COALESCE(DEPARTMENT, '') || ' ' ||
            COALESCE(ARRAY_TO_STRING(PRIMARY_SKILLS, ' '), '')
        ),
        AI_MEMORY_UPDATED_AT = CURRENT_TIMESTAMP()
    WHERE AI_MEMORY_EMBEDDING IS NULL OR AI_MEMORY_UPDATED_AT < DATEADD('day', -7, CURRENT_TIMESTAMP());
    
    -- Generate embeddings for customers
    UPDATE CUSTOMERS
    SET 
        AI_MEMORY_EMBEDDING = SNOWFLAKE.CORTEX.EMBED_TEXT('e5-base-v2',
            COMPANY_NAME || ' ' ||
            COALESCE(INDUSTRY, '') || ' ' ||
            COALESCE(CUSTOMER_SEGMENT, '') || ' ' ||
            COALESCE(BUSINESS_MODEL, '')
        ),
        AI_MEMORY_UPDATED_AT = CURRENT_TIMESTAMP()
    WHERE AI_MEMORY_EMBEDDING IS NULL OR AI_MEMORY_UPDATED_AT < DATEADD('day', -7, CURRENT_TIMESTAMP());
    
    -- Generate embeddings for products
    UPDATE PRODUCTS_SERVICES
    SET 
        AI_MEMORY_EMBEDDING = SNOWFLAKE.CORTEX.EMBED_TEXT('e5-base-v2',
            PRODUCT_NAME || ' ' ||
            COALESCE(PRODUCT_DESCRIPTION, '') || ' ' ||
            COALESCE(VALUE_PROPOSITION, '') || ' ' ||
            COALESCE(ARRAY_TO_STRING(KEY_BENEFITS, ' '), '')
        ),
        AI_MEMORY_UPDATED_AT = CURRENT_TIMESTAMP()
    WHERE AI_MEMORY_EMBEDDING IS NULL OR AI_MEMORY_UPDATED_AT < DATEADD('day', -7, CURRENT_TIMESTAMP());
    
    -- Generate embeddings for competitors
    UPDATE COMPETITORS
    SET 
        AI_MEMORY_EMBEDDING = SNOWFLAKE.CORTEX.EMBED_TEXT('e5-base-v2',
            COMPANY_NAME || ' ' ||
            COALESCE(COMPANY_DESCRIPTION, '') || ' ' ||
            COALESCE(MARKET_SEGMENT, '') || ' ' ||
            COALESCE(ARRAY_TO_STRING(STRENGTHS, ' '), '') || ' ' ||
            COALESCE(ARRAY_TO_STRING(WEAKNESSES, ' '), '')
        ),
        AI_MEMORY_UPDATED_AT = CURRENT_TIMESTAMP()
    WHERE AI_MEMORY_EMBEDDING IS NULL OR AI_MEMORY_UPDATED_AT < DATEADD('day', -7, CURRENT_TIMESTAMP());
    
    -- Generate embeddings for business processes
    UPDATE BUSINESS_PROCESSES
    SET 
        AI_MEMORY_EMBEDDING = SNOWFLAKE.CORTEX.EMBED_TEXT('e5-base-v2',
            PROCESS_NAME || ' ' ||
            COALESCE(PROCESS_DESCRIPTION, '') || ' ' ||
            COALESCE(PROCESS_CATEGORY, '') || ' ' ||
            COALESCE(ARRAY_TO_STRING(REQUIRED_SKILLS, ' '), '')
        ),
        AI_MEMORY_UPDATED_AT = CURRENT_TIMESTAMP()
    WHERE AI_MEMORY_EMBEDDING IS NULL OR AI_MEMORY_UPDATED_AT < DATEADD('day', -7, CURRENT_TIMESTAMP());
    
    -- Generate embeddings for knowledge articles
    UPDATE KNOWLEDGE_ARTICLES
    SET 
        AI_MEMORY_EMBEDDING = SNOWFLAKE.CORTEX.EMBED_TEXT('e5-base-v2',
            ARTICLE_TITLE || ' ' ||
            COALESCE(ARTICLE_SUMMARY, '') || ' ' ||
            COALESCE(SUBSTR(ARTICLE_CONTENT, 1, 2000), '') || ' ' ||
            COALESCE(ARRAY_TO_STRING(KEYWORDS, ' '), '')
        ),
        AI_MEMORY_UPDATED_AT = CURRENT_TIMESTAMP()
    WHERE AI_MEMORY_EMBEDDING IS NULL OR AI_MEMORY_UPDATED_AT < DATEADD('day', -7, CURRENT_TIMESTAMP());
    
    GET DIAGNOSTICS processed_count = ROW_COUNT;
    
    RETURN 'Generated embeddings for ' || processed_count || ' foundational knowledge records';
    
EXCEPTION
    WHEN OTHER THEN
        RETURN 'Error generating embeddings: ' || SQLERRM;
END;
$$;

-- =====================================================================
-- 8. AUTOMATED TASKS
-- =====================================================================

-- Task to generate embeddings for new foundational knowledge
CREATE OR REPLACE TASK TASK_GENERATE_FOUNDATIONAL_EMBEDDINGS
    WAREHOUSE = COMPUTE_WH
    SCHEDULE = 'USING CRON 0 2 * * * UTC' -- Daily at 2 AM UTC
    COMMENT = 'Generate embeddings for foundational knowledge base'
AS
    CALL GENERATE_FOUNDATIONAL_KNOWLEDGE_EMBEDDINGS();

-- Enable the task (execute manually after setup)
-- ALTER TASK TASK_GENERATE_FOUNDATIONAL_EMBEDDINGS RESUME;

-- =====================================================================
-- 9. SAMPLE DATA INSERTION PROCEDURES
-- =====================================================================

-- Procedure to insert sample Pay Ready data
CREATE OR REPLACE PROCEDURE INSERT_SAMPLE_PAYREADY_DATA()
RETURNS STRING
LANGUAGE SQL
AS
$$
BEGIN
    
    -- Insert sample employees
    INSERT INTO EMPLOYEES (
        EMPLOYEE_ID, FIRST_NAME, LAST_NAME, EMAIL_ADDRESS, DEPARTMENT, JOB_TITLE, 
        EMPLOYEE_LEVEL, HIRE_DATE, EMPLOYMENT_STATUS, LOCATION, PRIMARY_SKILLS
    ) VALUES 
    ('emp_001', 'Lynn', 'Musil', 'lynn@payready.com', 'Executive', 'CEO', 'C-Level', '2020-01-01', 'Active', 'Remote', 
     PARSE_JSON('["Strategic Planning", "Business Development", "Leadership", "Product Strategy"]')),
    ('emp_002', 'John', 'Smith', 'john.smith@payready.com', 'Sales', 'VP of Sales', 'VP', '2020-06-01', 'Active', 'New York', 
     PARSE_JSON('["Sales Strategy", "Team Leadership", "Customer Relations", "Revenue Growth"]')),
    ('emp_003', 'Sarah', 'Johnson', 'sarah.johnson@payready.com', 'Engineering', 'VP of Engineering', 'VP', '2020-03-01', 'Active', 'San Francisco', 
     PARSE_JSON('["Software Architecture", "Team Management", "Python", "Cloud Infrastructure"]')),
    ('emp_004', 'Mike', 'Davis', 'mike.davis@payready.com', 'Marketing', 'VP of Marketing', 'VP', '2020-09-01', 'Active', 'Remote', 
     PARSE_JSON('["Digital Marketing", "Content Strategy", "Brand Management", "Growth Marketing"]'));
    
    -- Insert sample customers
    INSERT INTO CUSTOMERS (
        CUSTOMER_ID, COMPANY_NAME, INDUSTRY, CUSTOMER_SEGMENT, BUSINESS_MODEL, 
        CUSTOMER_STATUS, CUSTOMER_TIER, ACCOUNT_MANAGER_EMPLOYEE_ID
    ) VALUES 
    ('cust_001', 'Acme Property Management', 'Property Management', 'Enterprise', 'B2B', 'Active', 'Strategic', 'emp_002'),
    ('cust_002', 'Summit Real Estate Group', 'Real Estate', 'Mid-Market', 'B2B', 'Active', 'Key', 'emp_002'),
    ('cust_003', 'Urban Living Apartments', 'Property Management', 'SMB', 'B2B', 'Active', 'Standard', 'emp_002');
    
    -- Insert sample products
    INSERT INTO PRODUCTS_SERVICES (
        PRODUCT_ID, PRODUCT_NAME, PRODUCT_DESCRIPTION, PRODUCT_CATEGORY, PRICING_MODEL, 
        VALUE_PROPOSITION, PRODUCT_MANAGER_EMPLOYEE_ID
    ) VALUES 
    ('prod_001', 'Pay Ready Core', 'Comprehensive payment processing platform for property management', 'Payment Processing', 'Subscription', 
     'Streamline rent collection and reduce payment processing costs', 'emp_003'),
    ('prod_002', 'Pay Ready Analytics', 'Advanced analytics and reporting for payment data', 'Analytics', 'Add-On', 
     'Gain insights into payment trends and optimize cash flow', 'emp_003'),
    ('prod_003', 'Pay Ready Mobile', 'Mobile app for tenants to make payments and manage accounts', 'Mobile Application', 'Included', 
     'Improve tenant experience and reduce support costs', 'emp_003');
    
    -- Insert sample competitors
    INSERT INTO COMPETITORS (
        COMPETITOR_ID, COMPANY_NAME, COMPANY_WEBSITE, MARKET_SEGMENT, COMPETITIVE_TIER, THREAT_LEVEL
    ) VALUES 
    ('comp_001', 'RentSpree', 'https://rentspree.com', 'Direct Competitor', 'Tier 1', 'High'),
    ('comp_002', 'Zego', 'https://zego.com', 'Direct Competitor', 'Tier 2', 'Medium'),
    ('comp_003', 'PayLease', 'https://paylease.com', 'Direct Competitor', 'Tier 1', 'High');
    
    -- Insert organizational values
    INSERT INTO ORGANIZATIONAL_VALUES (
        VALUE_ID, VALUE_TYPE, VALUE_NAME, VALUE_STATEMENT, VALUE_DESCRIPTION
    ) VALUES 
    ('val_001', 'Mission', 'Company Mission', 'Simplify property management through innovative payment solutions', 
     'We exist to make property management easier and more efficient through technology'),
    ('val_002', 'Vision', 'Company Vision', 'To be the leading payment platform for the property management industry', 
     'We envision a future where all property payments are seamless and automated'),
    ('val_003', 'Core Value', 'Customer Success', 'Our customers success is our success', 
     'We measure our success by the success of our customers'),
    ('val_004', 'Core Value', 'Innovation', 'Continuously innovate to solve customer problems', 
     'We embrace new technologies and approaches to better serve our customers');
    
    RETURN 'Sample Pay Ready data inserted successfully';
    
EXCEPTION
    WHEN OTHER THEN
        RETURN 'Error inserting sample data: ' || SQLERRM;
END;
$$;

-- Execute sample data insertion (uncomment to run)
-- CALL INSERT_SAMPLE_PAYREADY_DATA();

-- =====================================================================
-- 10. PERFORMANCE OPTIMIZATION
-- =====================================================================

-- Create indexes for better query performance
-- Snowflake does not support traditional indexes; consider search optimization or clustering.
-- CREATE INDEX IF NOT EXISTS IDX_EMPLOYEES_DEPARTMENT ON EMPLOYEES(DEPARTMENT);
-- -- Snowflake does not support traditional indexes; consider search optimization or clustering.
-- CREATE INDEX IF NOT EXISTS IDX_EMPLOYEES_EMAIL ON EMPLOYEES(EMAIL_ADDRESS);
-- -- Snowflake does not support traditional indexes; consider search optimization or clustering.
-- CREATE INDEX IF NOT EXISTS IDX_CUSTOMERS_SEGMENT ON CUSTOMERS(CUSTOMER_SEGMENT);
-- -- Snowflake does not support traditional indexes; consider search optimization or clustering.
-- CREATE INDEX IF NOT EXISTS IDX_CUSTOMERS_STATUS ON CUSTOMERS(CUSTOMER_STATUS);
-- -- Snowflake does not support traditional indexes; consider search optimization or clustering.
-- CREATE INDEX IF NOT EXISTS IDX_PRODUCTS_CATEGORY ON PRODUCTS_SERVICES(PRODUCT_CATEGORY);
-- -- Snowflake does not support traditional indexes; consider search optimization or clustering.
-- CREATE INDEX IF NOT EXISTS IDX_COMPETITORS_TIER ON COMPETITORS(COMPETITIVE_TIER);
-- -- Snowflake does not support traditional indexes; consider search optimization or clustering.
-- CREATE INDEX IF NOT EXISTS IDX_ARTICLES_CATEGORY ON KNOWLEDGE_ARTICLES(ARTICLE_CATEGORY);
-- -- Snowflake does not support traditional indexes; consider search optimization or clustering.
-- CREATE INDEX IF NOT EXISTS IDX_PROCESSES_CATEGORY ON BUSINESS_PROCESSES(PROCESS_CATEGORY);
-- 
-- =====================================================================
-- END OF FOUNDATIONAL KNOWLEDGE SCHEMA
-- ===================================================================== 