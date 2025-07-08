-- ========================================
-- APOLLO.IO SNOWFLAKE INTEGRATION SCHEMA
-- ========================================
-- Comprehensive data warehouse schema for Apollo.io prospect and contact data
-- Supports lead enrichment, contact management, and sales intelligence
-- Account: ZNB04675 | User: SCOOBYJAVA15 | Role: ACCOUNTADMIN

-- ========================================
-- 1. SCHEMA CREATION
-- ========================================

-- Create Apollo.io schema in all environments
CREATE SCHEMA IF NOT EXISTS SOPHIA_AI_PROD.APOLLO_IO
    COMMENT = 'Apollo.io prospect enrichment and contact management data - Production';

CREATE SCHEMA IF NOT EXISTS SOPHIA_AI_STG.APOLLO_IO
    COMMENT = 'Apollo.io prospect enrichment and contact management data - Staging';

CREATE SCHEMA IF NOT EXISTS SOPHIA_AI_DEV.APOLLO_IO
    COMMENT = 'Apollo.io prospect enrichment and contact management data - Development';

-- ========================================
-- 2. RAW DATA TABLES (ELT Pattern)
-- ========================================

-- Raw contacts from Apollo.io API
CREATE OR REPLACE TABLE SOPHIA_AI_PROD.APOLLO_IO.RAW_CONTACTS (
    -- Primary identifiers
    apollo_contact_id VARCHAR(50) PRIMARY KEY,
    apollo_person_id VARCHAR(50),

    -- Basic contact information
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    full_name VARCHAR(200),
    email VARCHAR(255),
    email_status VARCHAR(50), -- verified, unverified, bounced, etc.
    phone_numbers ARRAY,

    -- Professional information
    title VARCHAR(200),
    seniority VARCHAR(100),
    departments ARRAY,
    functions ARRAY,

    -- Company association
    organization_id VARCHAR(50),
    organization_name VARCHAR(255),

    -- Social profiles
    linkedin_url VARCHAR(500),
    twitter_url VARCHAR(500),
    facebook_url VARCHAR(500),

    -- Apollo.io metadata
    apollo_created_at TIMESTAMP_TZ,
    apollo_updated_at TIMESTAMP_TZ,
    contact_stage VARCHAR(100),

    -- Data quality indicators
    email_confidence_score FLOAT,
    phone_confidence_score FLOAT,
    data_quality_score FLOAT,

    -- AI Memory Integration
    ai_memory_embedding VECTOR(FLOAT, 768) COMMENT 'Contact profile embedding for semantic search',
    ai_memory_metadata VARIANT COMMENT 'AI processing metadata and insights',
    ai_memory_last_updated TIMESTAMP_TZ DEFAULT CURRENT_TIMESTAMP(),

    -- Audit fields
    ingested_at TIMESTAMP_TZ DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP_TZ DEFAULT CURRENT_TIMESTAMP(),
    source_system VARCHAR(50) DEFAULT 'apollo_api',
    data_version INTEGER DEFAULT 1,

    -- Raw API response
    raw_api_response VARIANT COMMENT 'Complete Apollo.io API response for debugging'
)
CLUSTER BY (organization_id, apollo_updated_at)
COMMENT = 'Raw contact data from Apollo.io API with AI memory integration';

-- Raw organizations from Apollo.io API
CREATE OR REPLACE TABLE SOPHIA_AI_PROD.APOLLO_IO.RAW_ORGANIZATIONS (
    -- Primary identifiers
    apollo_organization_id VARCHAR(50) PRIMARY KEY,

    -- Basic company information
    name VARCHAR(255),
    website_url VARCHAR(500),
    domain VARCHAR(255),

    -- Company details
    industry VARCHAR(200),
    sub_industry VARCHAR(200),
    company_size_range VARCHAR(100),
    estimated_num_employees INTEGER,

    -- Location information
    headquarters_address VARIANT,
    headquarters_city VARCHAR(100),
    headquarters_state VARCHAR(100),
    headquarters_country VARCHAR(100),

    -- Financial information
    annual_revenue_range VARCHAR(100),
    estimated_annual_revenue BIGINT,
    funding_stage VARCHAR(100),
    total_funding BIGINT,

    -- Technology stack
    technologies ARRAY,
    tech_stack VARIANT,

    -- Social presence
    linkedin_url VARCHAR(500),
    twitter_url VARCHAR(500),
    facebook_url VARCHAR(500),

    -- Apollo.io metadata
    apollo_created_at TIMESTAMP_TZ,
    apollo_updated_at TIMESTAMP_TZ,

    -- AI Memory Integration
    ai_memory_embedding VECTOR(FLOAT, 768) COMMENT 'Company profile embedding for semantic search',
    ai_memory_metadata VARIANT COMMENT 'AI processing metadata and company insights',
    ai_memory_last_updated TIMESTAMP_TZ DEFAULT CURRENT_TIMESTAMP(),

    -- Audit fields
    ingested_at TIMESTAMP_TZ DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP_TZ DEFAULT CURRENT_TIMESTAMP(),
    source_system VARCHAR(50) DEFAULT 'apollo_api',
    data_version INTEGER DEFAULT 1,

    -- Raw API response
    raw_api_response VARIANT COMMENT 'Complete Apollo.io API response for debugging'
)
CLUSTER BY (industry, company_size_range)
COMMENT = 'Raw organization data from Apollo.io API with AI memory integration';

-- Raw search results and sequences
CREATE OR REPLACE TABLE SOPHIA_AI_PROD.APOLLO_IO.RAW_SEARCH_RESULTS (
    -- Search metadata
    search_id VARCHAR(50) PRIMARY KEY,
    search_query VARIANT,
    search_type VARCHAR(50), -- people_search, company_search, etc.

    -- Search parameters
    search_filters VARIANT,
    search_criteria VARIANT,

    -- Results
    total_results INTEGER,
    results_returned INTEGER,
    search_results VARIANT,

    -- Pagination
    page_number INTEGER,
    per_page INTEGER,
    has_more_results BOOLEAN,

    -- Timing
    search_executed_at TIMESTAMP_TZ DEFAULT CURRENT_TIMESTAMP(),

    -- User context
    executed_by VARCHAR(100),
    search_purpose VARCHAR(255),

    -- Audit fields
    ingested_at TIMESTAMP_TZ DEFAULT CURRENT_TIMESTAMP(),
    raw_api_response VARIANT
)
CLUSTER BY (search_executed_at, search_type)
COMMENT = 'Raw search results from Apollo.io API for audit and analysis';

-- ========================================
-- 3. TRANSFORMED DATA TABLES
-- ========================================

-- Enriched contacts with business intelligence
CREATE OR REPLACE TABLE SOPHIA_AI_PROD.APOLLO_IO.CONTACTS_ENRICHED (
    -- Primary key
    contact_key VARCHAR(100) PRIMARY KEY,

    -- Source identifiers
    apollo_contact_id VARCHAR(50) NOT NULL,
    apollo_person_id VARCHAR(50),

    -- Standardized contact information
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    full_name VARCHAR(200),
    email_primary VARCHAR(255),
    email_work VARCHAR(255),
    phone_primary VARCHAR(50),
    phone_mobile VARCHAR(50),

    -- Professional profile
    current_title VARCHAR(200),
    seniority_level VARCHAR(100),
    department_primary VARCHAR(100),
    function_primary VARCHAR(100),
    years_experience INTEGER,

    -- Company association
    company_key VARCHAR(100),
    company_name VARCHAR(255),
    company_domain VARCHAR(255),

    -- Contact scoring
    lead_score INTEGER,
    engagement_score INTEGER,
    data_quality_score INTEGER,

    -- Enrichment status
    email_verified BOOLEAN,
    phone_verified BOOLEAN,
    linkedin_verified BOOLEAN,
    last_enriched_at TIMESTAMP_TZ,

    -- AI insights
    personality_insights VARIANT,
    communication_preferences VARIANT,
    buying_signals VARIANT,

    -- AI Memory Integration
    ai_memory_embedding VECTOR(FLOAT, 768),
    ai_memory_metadata VARIANT,
    ai_memory_last_updated TIMESTAMP_TZ,

    -- Audit fields
    created_at TIMESTAMP_TZ DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP_TZ DEFAULT CURRENT_TIMESTAMP(),
    is_active BOOLEAN DEFAULT TRUE,

    -- Foreign key constraints
    FOREIGN KEY (company_key) REFERENCES SOPHIA_AI_PROD.APOLLO_IO.COMPANIES_ENRICHED(company_key)
)
CLUSTER BY (company_key, seniority_level)
COMMENT = 'Enriched and standardized contact data with AI insights';

-- Enriched companies with market intelligence
CREATE OR REPLACE TABLE SOPHIA_AI_PROD.APOLLO_IO.COMPANIES_ENRICHED (
    -- Primary key
    company_key VARCHAR(100) PRIMARY KEY,

    -- Source identifiers
    apollo_organization_id VARCHAR(50) NOT NULL,

    -- Standardized company information
    company_name VARCHAR(255),
    company_domain VARCHAR(255),
    website_url VARCHAR(500),

    -- Industry classification
    industry_primary VARCHAR(200),
    industry_secondary VARCHAR(200),
    naics_code VARCHAR(20),
    sic_code VARCHAR(20),

    -- Company size and scale
    employee_count INTEGER,
    employee_range VARCHAR(100),
    annual_revenue BIGINT,
    revenue_range VARCHAR(100),

    -- Geographic information
    headquarters_city VARCHAR(100),
    headquarters_state VARCHAR(100),
    headquarters_country VARCHAR(100),
    headquarters_region VARCHAR(100),

    -- Technology and innovation
    technology_stack ARRAY,
    tech_categories ARRAY,
    innovation_score INTEGER,

    -- Market position
    market_cap BIGINT,
    funding_stage VARCHAR(100),
    total_funding BIGINT,
    last_funding_date DATE,

    -- Business intelligence
    growth_rate FLOAT,
    market_position VARCHAR(100),
    competitive_landscape VARIANT,

    -- AI insights
    company_health_score INTEGER,
    buying_intent_signals VARIANT,
    expansion_indicators VARIANT,

    -- AI Memory Integration
    ai_memory_embedding VECTOR(FLOAT, 768),
    ai_memory_metadata VARIANT,
    ai_memory_last_updated TIMESTAMP_TZ,

    -- Audit fields
    created_at TIMESTAMP_TZ DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP_TZ DEFAULT CURRENT_TIMESTAMP(),
    is_active BOOLEAN DEFAULT TRUE
)
CLUSTER BY (industry_primary, employee_range)
COMMENT = 'Enriched and standardized company data with market intelligence';

-- ========================================
-- 4. ANALYTICAL VIEWS
-- ========================================

-- Unified prospect view combining contacts and companies
CREATE OR REPLACE VIEW SOPHIA_AI_PROD.APOLLO_IO.VW_PROSPECT_INTELLIGENCE AS
SELECT
    c.contact_key,
    c.apollo_contact_id,
    c.full_name,
    c.email_primary,
    c.current_title,
    c.seniority_level,
    c.lead_score,
    c.engagement_score,

    -- Company information
    co.company_key,
    co.company_name,
    co.company_domain,
    co.industry_primary,
    co.employee_count,
    co.annual_revenue,
    co.company_health_score,

    -- Combined scoring
    (c.lead_score + c.engagement_score + co.company_health_score) / 3 AS overall_prospect_score,

    -- AI insights
    c.buying_signals,
    co.buying_intent_signals,
    co.expansion_indicators,

    -- Contact information
    c.phone_primary,
    c.linkedin_verified,
    c.last_enriched_at,

    -- Geographic
    co.headquarters_city,
    co.headquarters_state,
    co.headquarters_country

FROM SOPHIA_AI_PROD.APOLLO_IO.CONTACTS_ENRICHED c
JOIN SOPHIA_AI_PROD.APOLLO_IO.COMPANIES_ENRICHED co
    ON c.company_key = co.company_key
WHERE c.is_active = TRUE
    AND co.is_active = TRUE
    AND c.email_verified = TRUE;

-- Contact search optimization view
CREATE OR REPLACE VIEW SOPHIA_AI_PROD.APOLLO_IO.VW_CONTACT_SEARCH AS
SELECT
    contact_key,
    apollo_contact_id,
    full_name,
    email_primary,
    current_title,
    company_name,
    industry_primary,
    seniority_level,
    lead_score,

    -- Search optimization
    CONCAT(full_name, ' ', current_title, ' ', company_name) AS search_text,
    ai_memory_embedding,

    -- Filters
    email_verified,
    phone_verified,
    linkedin_verified,
    is_active,
    last_enriched_at

FROM SOPHIA_AI_PROD.APOLLO_IO.CONTACTS_ENRICHED
WHERE is_active = TRUE;

-- ========================================
-- 5. DATA QUALITY AND MONITORING
-- ========================================

-- Data quality monitoring table
CREATE OR REPLACE TABLE SOPHIA_AI_PROD.APOLLO_IO.DATA_QUALITY_METRICS (
    metric_id VARCHAR(100) PRIMARY KEY,
    metric_name VARCHAR(200),
    metric_category VARCHAR(100), -- completeness, accuracy, consistency, timeliness

    -- Metric values
    metric_value FLOAT,
    metric_threshold FLOAT,
    metric_status VARCHAR(50), -- pass, warning, fail

    -- Context
    table_name VARCHAR(100),
    column_name VARCHAR(100),
    record_count INTEGER,

    -- Timing
    measured_at TIMESTAMP_TZ DEFAULT CURRENT_TIMESTAMP(),
    measurement_period VARCHAR(50),

    -- Details
    metric_details VARIANT,
    remediation_notes VARCHAR(1000)
)
CLUSTER BY (measured_at, metric_category)
COMMENT = 'Data quality metrics and monitoring for Apollo.io data';

-- ========================================
-- 6. STORED PROCEDURES
-- ========================================

-- Contact enrichment procedure
CREATE OR REPLACE PROCEDURE SOPHIA_AI_PROD.APOLLO_IO.SP_ENRICH_CONTACTS()
LANGUAGE SQL
EXECUTE AS CALLER
AS
$$
DECLARE
    processed_count INTEGER DEFAULT 0;
    error_count INTEGER DEFAULT 0;
    result_message VARCHAR(1000);
BEGIN
    -- First insert new records that don't exist
    INSERT INTO SOPHIA_AI_PROD.APOLLO_IO.CONTACTS_ENRICHED (
        contact_key, apollo_contact_id, apollo_person_id, first_name, last_name,
        full_name, email_primary, current_title, seniority_level, company_key,
        company_name, email_verified, lead_score, ai_memory_embedding,
        ai_memory_metadata, ai_memory_last_updated
    )
    SELECT
        CONCAT('APOLLO_', apollo_contact_id) AS contact_key,
        apollo_contact_id,
        apollo_person_id,
        first_name,
        last_name,
        CONCAT(COALESCE(first_name, ''), ' ', COALESCE(last_name, '')) AS full_name,
        email AS email_primary,
        title AS current_title,
        seniority AS seniority_level,
        CONCAT('APOLLO_ORG_', organization_id) AS company_key,
        organization_name AS company_name,
        CASE
            WHEN email_status = 'verified' THEN TRUE
            ELSE FALSE
        END AS email_verified,
        COALESCE(email_confidence_score * 100, 0)::INTEGER AS lead_score,
        ai_memory_embedding,
        ai_memory_metadata,
        ai_memory_last_updated
    FROM SOPHIA_AI_PROD.APOLLO_IO.RAW_CONTACTS src
    WHERE apollo_updated_at > CURRENT_TIMESTAMP - INTERVAL '24 HOURS'
    AND NOT EXISTS (
        SELECT 1 FROM SOPHIA_AI_PROD.APOLLO_IO.CONTACTS_ENRICHED tgt
        WHERE tgt.apollo_contact_id = src.apollo_contact_id
    );

    -- Then update existing records
    UPDATE SOPHIA_AI_PROD.APOLLO_IO.CONTACTS_ENRICHED tgt
    SET
        full_name = src.full_name,
        email_primary = src.email_primary,
        current_title = src.current_title,
        seniority_level = src.seniority_level,
        company_name = src.company_name,
        email_verified = src.email_verified,
        lead_score = src.lead_score,
        ai_memory_embedding = src.ai_memory_embedding,
        ai_memory_metadata = src.ai_memory_metadata,
        ai_memory_last_updated = src.ai_memory_last_updated,
        updated_at = CURRENT_TIMESTAMP
    FROM (
        SELECT
            apollo_contact_id,
            CONCAT(COALESCE(first_name, ''), ' ', COALESCE(last_name, '')) AS full_name,
            email AS email_primary,
            title AS current_title,
            seniority AS seniority_level,
            organization_name AS company_name,
            CASE
                WHEN email_status = 'verified' THEN TRUE
                ELSE FALSE
            END AS email_verified,
            COALESCE(email_confidence_score * 100, 0)::INTEGER AS lead_score,
            ai_memory_embedding,
            ai_memory_metadata,
            ai_memory_last_updated
        FROM SOPHIA_AI_PROD.APOLLO_IO.RAW_CONTACTS
        WHERE apollo_updated_at > CURRENT_TIMESTAMP - INTERVAL '24 HOURS'
    ) src
    WHERE tgt.apollo_contact_id = src.apollo_contact_id;

    -- Count processed records
    SELECT COUNT(*) INTO processed_count
    FROM SOPHIA_AI_PROD.APOLLO_IO.CONTACTS_ENRICHED;

    -- Generate result message for output
    SET result_message = 'Contact enrichment completed. Processed: ' || processed_count || ' records.';

    -- Output the result
    SELECT result_message;
END;
$$;

-- Company enrichment procedure
CREATE OR REPLACE PROCEDURE SOPHIA_AI_PROD.APOLLO_IO.SP_ENRICH_COMPANIES()
LANGUAGE SQL
EXECUTE AS CALLER
AS
$$
DECLARE
    processed_count INTEGER DEFAULT 0;
    result_message VARCHAR(1000);
BEGIN
    -- First insert new companies that don't exist
    INSERT INTO SOPHIA_AI_PROD.APOLLO_IO.COMPANIES_ENRICHED (
        company_key, apollo_organization_id, company_name, company_domain,
        website_url, industry_primary, industry_secondary, employee_count,
        employee_range, annual_revenue, revenue_range, headquarters_city,
        headquarters_state, headquarters_country, technology_stack,
        funding_stage, total_funding, ai_memory_embedding, ai_memory_metadata,
        ai_memory_last_updated
    )
    SELECT
        CONCAT('APOLLO_ORG_', apollo_organization_id) AS company_key,
        apollo_organization_id,
        name AS company_name,
        domain AS company_domain,
        website_url,
        industry AS industry_primary,
        sub_industry AS industry_secondary,
        estimated_num_employees AS employee_count,
        company_size_range AS employee_range,
        estimated_annual_revenue AS annual_revenue,
        annual_revenue_range AS revenue_range,
        headquarters_city,
        headquarters_state,
        headquarters_country,
        technologies AS technology_stack,
        funding_stage,
        total_funding,
        ai_memory_embedding,
        ai_memory_metadata,
        ai_memory_last_updated
    FROM SOPHIA_AI_PROD.APOLLO_IO.RAW_ORGANIZATIONS src
    WHERE apollo_updated_at > CURRENT_TIMESTAMP - INTERVAL '24 HOURS'
    AND NOT EXISTS (
        SELECT 1 FROM SOPHIA_AI_PROD.APOLLO_IO.COMPANIES_ENRICHED tgt
        WHERE tgt.apollo_organization_id = src.apollo_organization_id
    );

    -- Then update existing records
    UPDATE SOPHIA_AI_PROD.APOLLO_IO.COMPANIES_ENRICHED tgt
    SET
        company_name = src.company_name,
        company_domain = src.company_domain,
        website_url = src.website_url,
        industry_primary = src.industry_primary,
        industry_secondary = src.industry_secondary,
        employee_count = src.employee_count,
        employee_range = src.employee_range,
        annual_revenue = src.annual_revenue,
        revenue_range = src.revenue_range,
        headquarters_city = src.headquarters_city,
        headquarters_state = src.headquarters_state,
        headquarters_country = src.headquarters_country,
        technology_stack = src.technology_stack,
        funding_stage = src.funding_stage,
        total_funding = src.total_funding,
        ai_memory_embedding = src.ai_memory_embedding,
        ai_memory_metadata = src.ai_memory_metadata,
        ai_memory_last_updated = src.ai_memory_last_updated,
        updated_at = CURRENT_TIMESTAMP
    FROM (
        SELECT
            apollo_organization_id,
            name AS company_name,
            domain AS company_domain,
            website_url,
            industry AS industry_primary,
            sub_industry AS industry_secondary,
            estimated_num_employees AS employee_count,
            company_size_range AS employee_range,
            estimated_annual_revenue AS annual_revenue,
            annual_revenue_range AS revenue_range,
            headquarters_city,
            headquarters_state,
            headquarters_country,
            technologies AS technology_stack,
            funding_stage,
            total_funding,
            ai_memory_embedding,
            ai_memory_metadata,
            ai_memory_last_updated
        FROM SOPHIA_AI_PROD.APOLLO_IO.RAW_ORGANIZATIONS
        WHERE apollo_updated_at > CURRENT_TIMESTAMP - INTERVAL '24 HOURS'
    ) src
    WHERE tgt.apollo_organization_id = src.apollo_organization_id;

    -- Count processed records
    SELECT COUNT(*) INTO processed_count
    FROM SOPHIA_AI_PROD.APOLLO_IO.COMPANIES_ENRICHED;

    -- Generate result message for output
    SET result_message = 'Company enrichment completed. Processed: ' || processed_count || ' records.';

    -- Output the result
    SELECT result_message;
END;
$$;

-- AI embedding generation procedure using Snowflake Cortex
CREATE OR REPLACE PROCEDURE SOPHIA_AI_PROD.APOLLO_IO.SP_GENERATE_EMBEDDINGS()
LANGUAGE SQL
EXECUTE AS CALLER
AS
$$
DECLARE
    contact_count INTEGER DEFAULT 0;
    company_count INTEGER DEFAULT 0;
    result_message VARCHAR(1000);
BEGIN
    -- Generate embeddings for contacts
    UPDATE SOPHIA_AI_PROD.APOLLO_IO.CONTACTS_ENRICHED
    SET
        ai_memory_embedding = SNOWFLAKE.CORTEX.EMBED_TEXT_768(
            'e5-base-v2',
            CONCAT(
                COALESCE(full_name, ''), ' ',
                COALESCE(current_title, ''), ' ',
                COALESCE(company_name, ''), ' ',
                COALESCE(seniority_level, ''), ' ',
                COALESCE(department_primary, '')
            )
        ),
        ai_memory_last_updated = CURRENT_TIMESTAMP
    WHERE ai_memory_embedding IS NULL
        OR ai_memory_last_updated < updated_at;

    -- Count updated contacts
    SELECT COUNT(*) INTO contact_count
    FROM SOPHIA_AI_PROD.APOLLO_IO.CONTACTS_ENRICHED
    WHERE ai_memory_embedding IS NOT NULL;

    -- Generate embeddings for companies
    UPDATE SOPHIA_AI_PROD.APOLLO_IO.COMPANIES_ENRICHED
    SET
        ai_memory_embedding = SNOWFLAKE.CORTEX.EMBED_TEXT_768(
            'e5-base-v2',
            CONCAT(
                COALESCE(company_name, ''), ' ',
                COALESCE(industry_primary, ''), ' ',
                COALESCE(industry_secondary, ''), ' ',
                COALESCE(headquarters_city, ''), ' ',
                COALESCE(headquarters_country, ''), ' ',
                ARRAY_TO_STRING(technology_stack, ' ')
            )
        ),
        ai_memory_last_updated = CURRENT_TIMESTAMP
    WHERE ai_memory_embedding IS NULL
        OR ai_memory_last_updated < updated_at;

    -- Count updated companies
    SELECT COUNT(*) INTO company_count
    FROM SOPHIA_AI_PROD.APOLLO_IO.COMPANIES_ENRICHED
    WHERE ai_memory_embedding IS NOT NULL;

    -- Generate result message for output
    SET result_message = 'Embedding generation completed. Contacts: ' || contact_count || ', Companies: ' || company_count;

    -- Output the result
    SELECT result_message;
END;
$$;

-- ========================================
-- 7. SCHEDULED TASKS
-- ========================================

-- Daily contact enrichment task
CREATE OR REPLACE TASK SOPHIA_AI_PROD.APOLLO_IO.TASK_DAILY_CONTACT_ENRICHMENT
    WAREHOUSE = 'WH_SOPHIA_ETL_TRANSFORM'
    SCHEDULE = 'USING CRON 0 2 * * * UTC'  -- Daily at 2 AM UTC
    COMMENT = 'Daily enrichment of Apollo.io contact data'
AS
    CALL SOPHIA_AI_PROD.APOLLO_IO.SP_ENRICH_CONTACTS();

-- Daily company enrichment task
CREATE OR REPLACE TASK SOPHIA_AI_PROD.APOLLO_IO.TASK_DAILY_COMPANY_ENRICHMENT
    WAREHOUSE = 'WH_SOPHIA_ETL_TRANSFORM'
    SCHEDULE = 'USING CRON 0 3 * * * UTC'  -- Daily at 3 AM UTC
    COMMENT = 'Daily enrichment of Apollo.io company data'
AS
    CALL SOPHIA_AI_PROD.APOLLO_IO.SP_ENRICH_COMPANIES();

-- Weekly embedding generation task
CREATE OR REPLACE TASK SOPHIA_AI_PROD.APOLLO_IO.TASK_WEEKLY_EMBEDDING_GENERATION
    WAREHOUSE = 'WH_SOPHIA_AI_PROCESSING'
    SCHEDULE = 'USING CRON 0 4 * * 0 UTC'  -- Weekly on Sunday at 4 AM UTC
    COMMENT = 'Weekly AI embedding generation for Apollo.io data'
AS
    CALL SOPHIA_AI_PROD.APOLLO_IO.SP_GENERATE_EMBEDDINGS();

-- ========================================
-- 8. SEARCH OPTIMIZATION
-- ========================================

-- Enable search optimization for contact search
ALTER TABLE SOPHIA_AI_PROD.APOLLO_IO.CONTACTS_ENRICHED
ADD SEARCH OPTIMIZATION ON EQUALITY(email_primary, company_name, current_title);

-- Enable search optimization for company search
ALTER TABLE SOPHIA_AI_PROD.APOLLO_IO.COMPANIES_ENRICHED
ADD SEARCH OPTIMIZATION ON EQUALITY(company_name, company_domain, industry_primary);

-- ========================================
-- 9. SECURITY AND GOVERNANCE
-- ========================================

-- PII masking policy for email addresses
CREATE OR REPLACE MASKING POLICY SOPHIA_AI_PROD.APOLLO_IO.EMAIL_MASK AS (val STRING)
RETURNS STRING ->
    CASE
        WHEN CURRENT_ROLE() IN ('ROLE_SOPHIA_OWNER', 'ROLE_SOPHIA_ADMIN', 'ROLE_SOPHIA_AI_AGENT_SERVICE')
        THEN val
        WHEN CURRENT_ROLE() IN ('ROLE_SOPHIA_ANALYST_READONLY')
        THEN REGEXP_REPLACE(val, '(.{2}).*(@.*)', '\\1***\\2')
        ELSE '***MASKED***'
    END;

-- Apply email masking to contact tables
ALTER TABLE SOPHIA_AI_PROD.APOLLO_IO.CONTACTS_ENRICHED
MODIFY COLUMN email_primary SET MASKING POLICY SOPHIA_AI_PROD.APOLLO_IO.EMAIL_MASK;

ALTER TABLE SOPHIA_AI_PROD.APOLLO_IO.RAW_CONTACTS
MODIFY COLUMN email SET MASKING POLICY SOPHIA_AI_PROD.APOLLO_IO.EMAIL_MASK;

-- Data classification tags
CREATE OR REPLACE TAG SOPHIA_AI_PROD.APOLLO_IO.PII_LEVEL
ALLOWED_VALUES 'HIGH', 'MEDIUM', 'LOW', 'NONE'
COMMENT = 'PII sensitivity level for Apollo.io data';

-- Apply PII tags
ALTER TABLE SOPHIA_AI_PROD.APOLLO_IO.CONTACTS_ENRICHED
MODIFY COLUMN email_primary SET TAG (SOPHIA_AI_PROD.APOLLO_IO.PII_LEVEL = 'HIGH');

ALTER TABLE SOPHIA_AI_PROD.APOLLO_IO.CONTACTS_ENRICHED
MODIFY COLUMN phone_primary SET TAG (SOPHIA_AI_PROD.APOLLO_IO.PII_LEVEL = 'HIGH');

ALTER TABLE SOPHIA_AI_PROD.APOLLO_IO.CONTACTS_ENRICHED
MODIFY COLUMN full_name SET TAG (SOPHIA_AI_PROD.APOLLO_IO.PII_LEVEL = 'MEDIUM');

-- ========================================
-- 10. REPLICATION TO OTHER ENVIRONMENTS
-- ========================================

-- Replicate schema structure to staging and development
-- (Tables will be created with same structure but different data)

-- Staging environment
CREATE SCHEMA IF NOT EXISTS SOPHIA_AI_STG.APOLLO_IO CLONE SOPHIA_AI_PROD.APOLLO_IO;

-- Development environment
CREATE SCHEMA IF NOT EXISTS SOPHIA_AI_DEV.APOLLO_IO CLONE SOPHIA_AI_PROD.APOLLO_IO;

-- ========================================
-- DEPLOYMENT SUMMARY
-- ========================================

-- This schema provides:
-- 1. Complete Apollo.io data warehouse with raw and enriched tables
-- 2. AI memory integration with vector embeddings
-- 3. Automated enrichment procedures and scheduled tasks
-- 4. Data quality monitoring and governance
-- 5. Security policies and PII protection
-- 6. Search optimization for performance
-- 7. Multi-environment support (PROD/STG/DEV)
-- 8. Integration points for Airbyte and custom ETL
-- 9. Analytical views for business intelligence
-- 10. Comprehensive audit and lineage tracking

-- Next steps:
-- 1. Configure Apollo.io API credentials in Pulumi ESC
-- 2. Set up Estuary Flow connector for Apollo.io
-- 3. Deploy ETL pipelines for data ingestion
-- 4. Configure monitoring and alerting
-- 5. Test end-to-end data flow
