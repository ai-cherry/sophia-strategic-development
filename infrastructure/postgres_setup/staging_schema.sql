-- =====================================================================
-- PostgreSQL Staging Schema for Sophia AI
-- =====================================================================
--
-- This script creates the staging schemas and tables for structured
-- business data with pgvector integration for AI embeddings.
--
-- =====================================================================

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- =====================================================================
-- Gong Schema
-- =====================================================================
CREATE SCHEMA IF NOT EXISTS gong_raw;

CREATE TABLE IF NOT EXISTS gong_raw.stg_gong_calls (
    call_id TEXT PRIMARY KEY,
    call_title TEXT,
    call_datetime_utc TIMESTAMP WITH TIME ZONE,
    call_duration_seconds NUMERIC,
    primary_user_email TEXT,
    primary_user_name TEXT,
    hubspot_deal_id TEXT,
    deal_stage TEXT,
    deal_value NUMERIC(15,2),
    sentiment_score REAL,
    call_summary TEXT,
    key_topics JSONB,
    risk_indicators JSONB,
    next_steps JSONB,
    embedding VECTOR(768),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_gong_calls_embedding ON gong_raw.stg_gong_calls USING GIN (embedding);

CREATE TABLE IF NOT EXISTS gong_raw.stg_gong_call_transcripts (
    transcript_id TEXT PRIMARY KEY,
    call_id TEXT NOT NULL,
    speaker_name TEXT,
    transcript_text TEXT,
    embedding VECTOR(768),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    FOREIGN KEY (call_id) REFERENCES gong_raw.stg_gong_calls(call_id)
);
CREATE INDEX IF NOT EXISTS idx_gong_transcripts_embedding ON gong_raw.stg_gong_call_transcripts USING GIN (embedding);

-- =====================================================================
-- HubSpot Schema
-- =====================================================================
CREATE SCHEMA IF NOT EXISTS hubspot_raw;

CREATE TABLE IF NOT EXISTS hubspot_raw.stg_hubspot_contacts (
    contact_id TEXT PRIMARY KEY,
    first_name TEXT,
    last_name TEXT,
    email TEXT,
    phone TEXT,
    company_name TEXT,
    job_title TEXT,
    lifecycle_stage TEXT,
    lead_status TEXT,
    associated_company_id TEXT,
    create_date TIMESTAMP WITH TIME ZONE,
    last_modified_date TIMESTAMP WITH TIME ZONE,
    full_name TEXT,
    embedding VECTOR(768),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_hubspot_contacts_embedding ON hubspot_raw.stg_hubspot_contacts USING GIN (embedding);


CREATE TABLE IF NOT EXISTS hubspot_raw.stg_hubspot_deals (
    deal_id TEXT PRIMARY KEY,
    deal_name TEXT,
    deal_stage TEXT,
    deal_amount NUMERIC(15,2),
    close_date TIMESTAMP WITH TIME ZONE,
    create_date TIMESTAMP WITH TIME ZONE,
    pipeline_name TEXT,
    deal_owner TEXT,
    associated_contact_id TEXT,
    associated_company_id TEXT,
    embedding VECTOR(768),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_hubspot_deals_embedding ON hubspot_raw.stg_hubspot_deals USING GIN (embedding);

-- =====================================================================
-- Salesforce Schema
-- =====================================================================
CREATE SCHEMA IF NOT EXISTS salesforce_raw;

CREATE TABLE IF NOT EXISTS salesforce_raw.stg_salesforce_opportunities (
    opportunity_id TEXT PRIMARY KEY,
    opportunity_name TEXT,
    account_id TEXT,
    amount NUMERIC(15,2),
    close_date TIMESTAMP WITH TIME ZONE,
    stage_name TEXT,
    owner_id TEXT,
    embedding VECTOR(768),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_sf_opps_embedding ON salesforce_raw.stg_salesforce_opportunities USING GIN (embedding);

-- =====================================================================
-- Asana Schema
-- =====================================================================
CREATE SCHEMA IF NOT EXISTS asana_raw;

CREATE TABLE IF NOT EXISTS asana_raw.stg_asana_tasks (
    task_id TEXT PRIMARY KEY,
    task_name TEXT,
    assignee_id TEXT,
    project_id TEXT,
    workspace_id TEXT,
    due_on DATE,
    completed BOOLEAN,
    notes TEXT,
    embedding VECTOR(768),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_asana_tasks_embedding ON asana_raw.stg_asana_tasks USING GIN (embedding);


-- =====================================================================
-- Linear Schema
-- =====================================================================
CREATE SCHEMA IF NOT EXISTS linear_raw;

CREATE TABLE IF NOT EXISTS linear_raw.stg_linear_issues (
    issue_id TEXT PRIMARY KEY,
    title TEXT,
    description TEXT,
    priority TEXT,
    team_id TEXT,
    project_id TEXT,
    creator_id TEXT,
    assignee_id TEXT,
    status TEXT,
    embedding VECTOR(768),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_linear_issues_embedding ON linear_raw.stg_linear_issues USING GIN (embedding);

-- =====================================================================
-- Notion Schema
-- =====================================================================
CREATE SCHEMA IF NOT EXISTS notion_raw;

CREATE TABLE IF NOT EXISTS notion_raw.stg_notion_pages (
    page_id TEXT PRIMARY KEY,
    title TEXT,
    content TEXT,
    database_id TEXT,
    author_id TEXT,
    url TEXT,
    embedding VECTOR(768),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_notion_pages_embedding ON notion_raw.stg_notion_pages USING GIN (embedding);

-- =====================================================================
-- Slack Schema
-- =====================================================================
CREATE SCHEMA IF NOT EXISTS slack_raw;

CREATE TABLE IF NOT EXISTS slack_raw.stg_slack_messages (
    message_id TEXT PRIMARY KEY,
    channel_id TEXT,
    user_id TEXT,
    message_text TEXT,
    thread_ts TEXT,
    message_ts TIMESTAMP WITH TIME ZONE,
    embedding VECTOR(768),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_slack_messages_embedding ON slack_raw.stg_slack_messages USING GIN (embedding); 