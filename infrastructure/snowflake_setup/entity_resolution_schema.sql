-- ========================================================================================
-- SOPHIA AI ENTITY RESOLUTION SYSTEM - CANONICAL REGISTRY & FUZZY MATCHING
-- ========================================================================================
-- Implements comprehensive entity resolution for property/company/person names
-- across Slack, Gong, HubSpot, Asana, and other business systems
-- ========================================================================================

-- Create schema for entity resolution
CREATE SCHEMA IF NOT EXISTS SOPHIA_ENTITY_RESOLUTION;
USE SCHEMA SOPHIA_ENTITY_RESOLUTION;

-- ========================================================================================
-- 1. CANONICAL ENTITY REGISTRY TABLE
-- ========================================================================================

CREATE OR REPLACE TABLE ENTITY_CANONICAL (
    ENTITY_ID STRING PRIMARY KEY,           -- GUID for the canonical entity
    ENTITY_TYPE STRING NOT NULL,            -- 'property','company','person','customer'
    CANONICAL_NAME STRING NOT NULL,         -- Clean, standardized name
    NORMALIZED_NAME STRING NOT NULL,        -- UPPER/ASCII/trimmed for fuzzy matching
    PRIMARY_IDS ARRAY,                      -- Source-specific IDs (hubspot_id, slack_uid, etc.)
    ALIASES ARRAY,                          -- All seen spelling variations
    CREATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    UPDATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    CONFIDENCE FLOAT DEFAULT 0.5,           -- 0-1 confidence score based on validation
    METADATA VARIANT,                       -- Additional context (domains, locations, etc.)
    SOURCE_SYSTEM_COUNT INTEGER DEFAULT 1,  -- Number of systems this entity appears in
    LAST_SEEN_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS IDX_ENTITY_TYPE ON ENTITY_CANONICAL(ENTITY_TYPE);
CREATE INDEX IF NOT EXISTS IDX_NORMALIZED_NAME ON ENTITY_CANONICAL(NORMALIZED_NAME);
CREATE INDEX IF NOT EXISTS IDX_CONFIDENCE ON ENTITY_CANONICAL(CONFIDENCE);

-- ========================================================================================
-- 2. ENTITY RESOLUTION EVENTS TABLE (GOVERNANCE & LEARNING)
-- ========================================================================================

CREATE OR REPLACE TABLE ENTITY_RESOLUTION_EVENTS (
    EVENT_ID STRING PRIMARY KEY,
    USER_QUERY STRING NOT NULL,             -- Original user query
    ENTITY_CANDIDATES ARRAY,                -- Entities that were found/suggested
    SELECTED_ENTITY_ID STRING,              -- Entity user confirmed (if any)
    USER_CONFIRMED BOOLEAN DEFAULT FALSE,   -- Whether user explicitly confirmed
    SUGGESTIONS_COUNT INTEGER,              -- Number of suggestions shown
    MODEL_CONFIDENCE FLOAT,                 -- AI confidence in the match
    RESOLUTION_METHOD STRING,               -- 'automatic', 'user_clarification', 'manual'
    USER_ID STRING,
    SESSION_ID STRING,
    CREATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    RESOLUTION_TIME_MS INTEGER,             -- Time taken to resolve
    FEEDBACK_PROVIDED VARIANT               -- User feedback about the resolution
);

-- ========================================================================================
-- 3. AI-SQL HELPER FUNCTIONS FOR FUZZY MATCHING
-- ========================================================================================

-- Enhanced Jaro-Winkler similarity function with business logic
CREATE OR REPLACE FUNCTION SIMILARITY_JW(name1 STRING, name2 STRING)
RETURNS FLOAT
LANGUAGE SQL
AS
$$
    CASE 
        WHEN name1 IS NULL OR name2 IS NULL THEN 0.0
        WHEN UPPER(TRIM(name1)) = UPPER(TRIM(name2)) THEN 1.0
        ELSE JAROWINKLER_SIMILARITY(UPPER(TRIM(name1)), UPPER(TRIM(name2)))
    END
$$;

-- Normalize entity names for consistent matching
CREATE OR REPLACE FUNCTION NORMALIZE_ENTITY_NAME(entity_name STRING)
RETURNS STRING
LANGUAGE SQL
AS
$$
    REGEXP_REPLACE(
        REGEXP_REPLACE(
            REGEXP_REPLACE(
                REGEXP_REPLACE(
                    UPPER(TRIM(entity_name)),
                    '\\b(LLC|INC|CORP|CORPORATION|COMPANY|CO|LTD|LIMITED|MGMT|MANAGEMENT|APARTMENTS|APTS|APARTMENT|APT)\\b',
                    ''
                ),
                '[^A-Z0-9\\s]',  -- Remove special characters
                ''
            ),
            '\\s+',  -- Normalize whitespace
            ' '
        ),
        '^\\s+|\\s+$',  -- Trim
        ''
    )
$$;

-- Enhanced edit distance for property/company names
CREATE OR REPLACE FUNCTION ENHANCED_EDIT_DISTANCE(name1 STRING, name2 STRING)
RETURNS INTEGER
LANGUAGE SQL
AS
$$
    EDITDISTANCE(
        NORMALIZE_ENTITY_NAME(name1),
        NORMALIZE_ENTITY_NAME(name2)
    )
$$;

-- Composite similarity score combining multiple factors
CREATE OR REPLACE FUNCTION ENTITY_SIMILARITY_SCORE(
    name1 STRING, 
    name2 STRING,
    domain1 STRING DEFAULT NULL,
    domain2 STRING DEFAULT NULL
)
RETURNS FLOAT
LANGUAGE SQL
AS
$$
    CASE 
        WHEN name1 IS NULL OR name2 IS NULL THEN 0.0
        ELSE 
            -- Base name similarity (70% weight)
            (SIMILARITY_JW(name1, name2) * 0.7) +
            
            -- Domain similarity bonus (30% weight) if domains provided
            CASE 
                WHEN domain1 IS NOT NULL AND domain2 IS NOT NULL THEN
                    CASE 
                        WHEN LOWER(domain1) = LOWER(domain2) THEN 0.3
                        WHEN SIMILARITY_JW(domain1, domain2) > 0.8 THEN 0.15
                        ELSE 0.0
                    END
                ELSE 0.0
            END
    END
$$;

-- ========================================================================================
-- 4. ENTITY LOOKUP AND RESOLUTION FUNCTIONS
-- ========================================================================================

-- Find potential entity matches with confidence scoring
CREATE OR REPLACE FUNCTION FIND_ENTITY_MATCHES(
    search_name STRING,
    entity_type STRING DEFAULT NULL,
    confidence_threshold FLOAT DEFAULT 0.75
)
RETURNS TABLE (
    entity_id STRING,
    canonical_name STRING,
    similarity_score FLOAT,
    match_reason STRING,
    aliases ARRAY
)
LANGUAGE SQL
AS
$$
    WITH candidate_matches AS (
        SELECT 
            e.entity_id,
            e.canonical_name,
            e.aliases,
            -- Direct name similarity
            SIMILARITY_JW(search_name, e.canonical_name) as name_score,
            
            -- Normalized name similarity
            SIMILARITY_JW(
                NORMALIZE_ENTITY_NAME(search_name), 
                e.normalized_name
            ) as normalized_score,
            
            -- Alias matching
            (
                SELECT MAX(SIMILARITY_JW(search_name, alias.value::STRING))
                FROM TABLE(FLATTEN(e.aliases)) as alias
            ) as alias_score,
            
            -- Confidence boost for high-confidence entities
            e.confidence as entity_confidence
            
        FROM ENTITY_CANONICAL e
        WHERE (entity_type IS NULL OR e.entity_type = entity_type)
        AND (
            -- Quick filter to avoid computing similarity for obviously unrelated entities
            SIMILARITY_JW(NORMALIZE_ENTITY_NAME(search_name), e.normalized_name) > 0.3
            OR EXISTS (
                SELECT 1 FROM TABLE(FLATTEN(e.aliases)) as alias
                WHERE SIMILARITY_JW(search_name, alias.value::STRING) > 0.3
            )
        )
    ),
    
    scored_matches AS (
        SELECT 
            entity_id,
            canonical_name,
            aliases,
            -- Composite scoring with multiple factors
            GREATEST(name_score, normalized_score, COALESCE(alias_score, 0.0)) * 
            (0.8 + 0.2 * entity_confidence) as similarity_score,
            
            CASE 
                WHEN name_score >= GREATEST(normalized_score, COALESCE(alias_score, 0.0)) THEN 'canonical_name_match'
                WHEN normalized_score >= COALESCE(alias_score, 0.0) THEN 'normalized_name_match'
                ELSE 'alias_match'
            END as match_reason
            
        FROM candidate_matches
        WHERE GREATEST(name_score, normalized_score, COALESCE(alias_score, 0.0)) >= confidence_threshold
    )
    
    SELECT 
        entity_id,
        canonical_name,
        similarity_score,
        match_reason,
        aliases
    FROM scored_matches
    ORDER BY similarity_score DESC
    LIMIT 10
$$;

-- ========================================================================================
-- 5. ENTITY REGISTRATION AND LEARNING PROCEDURES
-- ========================================================================================

-- Register a new entity or update existing one
CREATE OR REPLACE PROCEDURE REGISTER_ENTITY(
    p_entity_type STRING,
    p_name STRING,
    p_source_id STRING DEFAULT NULL,
    p_source_system STRING DEFAULT NULL,
    p_metadata VARIANT DEFAULT NULL
)
RETURNS STRING
LANGUAGE SQL
AS
$$
DECLARE
    v_entity_id STRING;
    v_normalized_name STRING;
    v_existing_entity_id STRING DEFAULT NULL;
BEGIN
    -- Normalize the name
    v_normalized_name := NORMALIZE_ENTITY_NAME(p_name);
    
    -- Check for existing entity with high similarity
    SELECT entity_id INTO v_existing_entity_id
    FROM TABLE(FIND_ENTITY_MATCHES(p_name, p_entity_type, 0.9))
    LIMIT 1;
    
    IF (v_existing_entity_id IS NOT NULL) THEN
        -- Update existing entity
        UPDATE ENTITY_CANONICAL 
        SET 
            aliases = ARRAY_APPEND(aliases, p_name),
            primary_ids = CASE 
                WHEN p_source_id IS NOT NULL THEN 
                    ARRAY_APPEND(primary_ids, OBJECT_CONSTRUCT('id', p_source_id, 'system', p_source_system))
                ELSE primary_ids
            END,
            source_system_count = source_system_count + 1,
            confidence = LEAST(1.0, confidence + 0.1),
            updated_at = CURRENT_TIMESTAMP(),
            last_seen_at = CURRENT_TIMESTAMP()
        WHERE entity_id = v_existing_entity_id;
        
        RETURN v_existing_entity_id;
    ELSE
        -- Create new entity
        v_entity_id := UPPER(REGEXP_REPLACE(UUID_STRING(), '-', ''));
        
        INSERT INTO ENTITY_CANONICAL (
            entity_id,
            entity_type,
            canonical_name,
            normalized_name,
            primary_ids,
            aliases,
            confidence,
            metadata
        ) VALUES (
            v_entity_id,
            p_entity_type,
            p_name,
            v_normalized_name,
            CASE 
                WHEN p_source_id IS NOT NULL THEN 
                    ARRAY_CONSTRUCT(OBJECT_CONSTRUCT('id', p_source_id, 'system', p_source_system))
                ELSE ARRAY_CONSTRUCT()
            END,
            ARRAY_CONSTRUCT(p_name),
            0.5,
            p_metadata
        );
        
        RETURN v_entity_id;
    END IF;
END;
$$;

-- Learn from user feedback
CREATE OR REPLACE PROCEDURE LEARN_FROM_USER_FEEDBACK(
    p_event_id STRING,
    p_selected_entity_id STRING,
    p_user_query STRING,
    p_user_id STRING
)
RETURNS STRING
LANGUAGE SQL
AS
$$
BEGIN
    -- Record the user feedback
    UPDATE ENTITY_RESOLUTION_EVENTS
    SET 
        selected_entity_id = p_selected_entity_id,
        user_confirmed = TRUE,
        resolution_method = 'user_clarification'
    WHERE event_id = p_event_id;
    
    -- Boost confidence of the selected entity
    UPDATE ENTITY_CANONICAL
    SET 
        confidence = LEAST(1.0, confidence + 0.05),
        updated_at = CURRENT_TIMESTAMP()
    WHERE entity_id = p_selected_entity_id;
    
    -- Add the user's query terms as potential aliases if similarity is high
    IF (SIMILARITY_JW(p_user_query, (SELECT canonical_name FROM ENTITY_CANONICAL WHERE entity_id = p_selected_entity_id)) > 0.7) THEN
        UPDATE ENTITY_CANONICAL
        SET aliases = ARRAY_APPEND(aliases, p_user_query)
        WHERE entity_id = p_selected_entity_id;
    END IF;
    
    RETURN 'SUCCESS';
END;
$$;

-- ========================================================================================
-- 6. BATCH ENTITY DISCOVERY AND POPULATION
-- ========================================================================================

-- Populate entities from existing data sources
CREATE OR REPLACE PROCEDURE POPULATE_ENTITIES_FROM_SOURCES()
RETURNS STRING
LANGUAGE SQL
AS
$$
BEGIN
    -- Populate companies from HubSpot
    INSERT INTO ENTITY_CANONICAL (
        entity_id,
        entity_type,
        canonical_name,
        normalized_name,
        primary_ids,
        aliases,
        confidence,
        metadata
    )
    SELECT 
        UPPER(REGEXP_REPLACE(UUID_STRING(), '-', '')),
        'company',
        name,
        NORMALIZE_ENTITY_NAME(name),
        ARRAY_CONSTRUCT(OBJECT_CONSTRUCT('id', hs_object_id, 'system', 'hubspot')),
        ARRAY_CONSTRUCT(name),
        0.7,
        OBJECT_CONSTRUCT('domain', domain, 'industry', industry, 'source', 'hubspot')
    FROM HUBSPOT_DATA.COMPANIES
    WHERE name IS NOT NULL
    AND NOT EXISTS (
        SELECT 1 FROM ENTITY_CANONICAL ec 
        WHERE SIMILARITY_JW(name, ec.canonical_name) > 0.9 
        AND ec.entity_type = 'company'
    );
    
    -- Add Slack user entities
    INSERT INTO ENTITY_CANONICAL (
        entity_id,
        entity_type,
        canonical_name,
        normalized_name,
        primary_ids,
        aliases,
        confidence,
        metadata
    )
    SELECT 
        UPPER(REGEXP_REPLACE(UUID_STRING(), '-', '')),
        'person',
        display_name,
        NORMALIZE_ENTITY_NAME(display_name),
        ARRAY_CONSTRUCT(OBJECT_CONSTRUCT('id', user_id, 'system', 'slack')),
        ARRAY_CONSTRUCT(display_name, real_name),
        0.6,
        OBJECT_CONSTRUCT('email', email, 'title', title, 'source', 'slack')
    FROM SLACK_DATA.USERS
    WHERE display_name IS NOT NULL
    AND NOT EXISTS (
        SELECT 1 FROM ENTITY_CANONICAL ec 
        WHERE SIMILARITY_JW(display_name, ec.canonical_name) > 0.9 
        AND ec.entity_type = 'person'
    );
    
    RETURN 'Entities populated from source systems';
END;
$$;

-- ========================================================================================
-- 7. MONITORING AND ANALYTICS VIEWS
-- ========================================================================================

-- Entity resolution performance metrics
CREATE OR REPLACE VIEW ENTITY_RESOLUTION_METRICS AS
SELECT 
    DATE_TRUNC('day', created_at) as resolution_date,
    resolution_method,
    COUNT(*) as total_resolutions,
    AVG(model_confidence) as avg_confidence,
    SUM(CASE WHEN user_confirmed THEN 1 ELSE 0 END) as user_confirmed_count,
    AVG(resolution_time_ms) as avg_resolution_time_ms,
    COUNT(DISTINCT user_id) as unique_users
FROM ENTITY_RESOLUTION_EVENTS
GROUP BY DATE_TRUNC('day', created_at), resolution_method
ORDER BY resolution_date DESC;

-- Top ambiguous entities needing attention
CREATE OR REPLACE VIEW AMBIGUOUS_ENTITIES AS
SELECT 
    e.canonical_name,
    e.entity_type,
    e.confidence,
    ARRAY_SIZE(e.aliases) as alias_count,
    COUNT(ere.event_id) as resolution_attempts,
    AVG(ere.model_confidence) as avg_query_confidence
FROM ENTITY_CANONICAL e
LEFT JOIN ENTITY_RESOLUTION_EVENTS ere ON ere.selected_entity_id = e.entity_id
WHERE e.confidence < 0.7 OR ARRAY_SIZE(e.aliases) > 5
GROUP BY e.entity_id, e.canonical_name, e.entity_type, e.confidence, ARRAY_SIZE(e.aliases)
ORDER BY resolution_attempts DESC, e.confidence ASC;

-- Usage analytics
CREATE OR REPLACE VIEW ENTITY_USAGE_ANALYTICS AS
SELECT 
    e.entity_type,
    e.source_system_count,
    COUNT(*) as entity_count,
    AVG(e.confidence) as avg_confidence,
    AVG(ARRAY_SIZE(e.aliases)) as avg_aliases_per_entity
FROM ENTITY_CANONICAL e
GROUP BY e.entity_type, e.source_system_count
ORDER BY e.entity_type, e.source_system_count;

COMMENT ON SCHEMA SOPHIA_ENTITY_RESOLUTION IS 'Comprehensive entity resolution system for Sophia AI - handles fuzzy matching, learning, and disambiguation across all business systems'; 