-- Snowflake Schemas for Storing Processed Gong Data

-- Table to store the main details of each Gong call
CREATE TABLE IF NOT EXISTS gong_calls (
    call_id VARCHAR(255) PRIMARY KEY,
    title VARCHAR,
    url VARCHAR,
    started_at TIMESTAMP_TZ,
    duration_seconds INTEGER,
    direction VARCHAR(50),
    is_meeting BOOLEAN,
    system VARCHAR(50),
    apartment_relevance_score FLOAT,
    business_impact_score FLOAT,
    created_at TIMESTAMP_TZ DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP_TZ DEFAULT CURRENT_TIMESTAMP()
);

-- Table to store the participants of each call
CREATE TABLE IF NOT EXISTS gong_participants (
    id SERIAL PRIMARY KEY,
    call_id VARCHAR(255) REFERENCES gong_calls(call_id),
    participant_id VARCHAR(255),
    email_address VARCHAR,
    name VARCHAR,
    title VARCHAR,
    company_name VARCHAR,
    talk_time_percentage FLOAT,
    is_customer BOOLEAN,
    is_internal BOOLEAN,
    created_at TIMESTAMP_TZ DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP_TZ DEFAULT CURRENT_TIMESTAMP(),
    UNIQUE(call_id, participant_id)
);

-- Table to store the AI-generated insights from Sophia
CREATE TABLE IF NOT EXISTS sophia_conversation_intelligence (
    call_id VARCHAR(255) PRIMARY KEY REFERENCES gong_calls(call_id),
    ai_summary TEXT,
    confidence_level FLOAT,
    key_insights JSON,
    recommended_actions JSON,
    deal_health_score FLOAT,
    created_at TIMESTAMP_TZ DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP_TZ DEFAULT CURRENT_TIMESTAMP()
);

-- Table for apartment industry specific analysis
CREATE TABLE IF NOT EXISTS sophia_apartment_analysis (
    call_id VARCHAR(255) PRIMARY KEY REFERENCES gong_calls(call_id),
    market_segment VARCHAR(100),
    apartment_terminology_count INTEGER,
    industry_relevance_factors JSON,
    created_at TIMESTAMP_TZ DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP_TZ DEFAULT CURRENT_TIMESTAMP()
);

-- Table for deal signals and progression
CREATE TABLE IF NOT EXISTS sophia_deal_signals (
    call_id VARCHAR(255) PRIMARY KEY REFERENCES gong_calls(call_id),
    positive_signals JSON,
    negative_signals JSON,
    deal_progression_stage VARCHAR(100),
    win_probability FLOAT,
    created_at TIMESTAMP_TZ DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP_TZ DEFAULT CURRENT_TIMESTAMP()
);

-- Table for competitive intelligence
CREATE TABLE IF NOT EXISTS sophia_competitive_intelligence (
    call_id VARCHAR(255) PRIMARY KEY REFERENCES gong_calls(call_id),
    competitors_mentioned JSON,
    competitive_threat_level VARCHAR(50),
    win_probability_impact FLOAT,
    created_at TIMESTAMP_TZ DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP_TZ DEFAULT CURRENT_TIMESTAMP()
);
