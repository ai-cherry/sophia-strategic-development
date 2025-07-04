-- CoStar Real Estate Market Intelligence Database Schema
-- Commercial real estate market data tables for Sophia AI

-- Table for storing metro area/market information
CREATE TABLE IF NOT EXISTS costar_markets (
    id SERIAL PRIMARY KEY,
    metro_area VARCHAR(255) NOT NULL UNIQUE,
    state VARCHAR(50),
    region VARCHAR(100),
    population INTEGER,
    market_tier VARCHAR(20), -- 'Primary', 'Secondary', 'Tertiary'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table for storing detailed market data by property type and time period
CREATE TABLE IF NOT EXISTS costar_market_data (
    id SERIAL PRIMARY KEY,
    market_id INTEGER REFERENCES costar_markets(id),
    property_type VARCHAR(100) NOT NULL, -- 'Office', 'Retail', 'Industrial', 'Multifamily'
    submarket VARCHAR(255), -- Optional submarket within metro area
    total_inventory BIGINT, -- Total square footage
    vacancy_rate DECIMAL(5,2), -- Percentage (0-100)
    asking_rent_psf DECIMAL(8,2), -- Dollars per square foot annually
    effective_rent_psf DECIMAL(8,2), -- Effective rent after concessions
    net_absorption INTEGER, -- Square footage absorbed (positive) or vacated (negative)
    construction_deliveries INTEGER, -- New construction completed this period
    under_construction INTEGER, -- Square footage currently under construction
    construction_starts INTEGER, -- New construction started this period
    cap_rate DECIMAL(5,2), -- Capitalization rate percentage
    price_per_sf DECIMAL(8,2), -- Sale price per square foot
    market_date DATE NOT NULL,
    quarter VARCHAR(10), -- 'Q1 2024', 'Q2 2024', etc.
    data_source VARCHAR(100) DEFAULT 'CoStar',
    data_quality_score INTEGER DEFAULT 100, -- 1-100 quality score
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- Ensure no duplicate entries for same market/property/date combination
    UNIQUE(market_id, property_type, market_date, submarket)
);

-- Table for tracking data imports and processing status
CREATE TABLE IF NOT EXISTS costar_import_log (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255),
    file_size_bytes BIGINT,
    file_checksum VARCHAR(64), -- MD5 or SHA256 hash
    records_processed INTEGER DEFAULT 0,
    records_imported INTEGER DEFAULT 0,
    records_failed INTEGER DEFAULT 0,
    import_method VARCHAR(50) DEFAULT 'file_upload', -- 'file_upload', 'api', 'scheduled'
    import_status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'processing', 'success', 'failed', 'partial'
    error_message TEXT,
    processing_start_time TIMESTAMP WITH TIME ZONE,
    processing_end_time TIMESTAMP WITH TIME ZONE,
    imported_by VARCHAR(100), -- User or system that initiated import
    metadata JSONB, -- Additional import metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table for storing market analysis and AI-generated insights
CREATE TABLE IF NOT EXISTS costar_market_insights (
    id SERIAL PRIMARY KEY,
    market_id INTEGER REFERENCES costar_markets(id),
    property_type VARCHAR(100),
    insight_type VARCHAR(50), -- 'trend_analysis', 'forecast', 'risk_assessment', 'opportunity'
    insight_title VARCHAR(255) NOT NULL,
    insight_description TEXT NOT NULL,
    confidence_score DECIMAL(3,2), -- 0.00 to 1.00
    supporting_data JSONB, -- Metrics and data supporting the insight
    time_horizon VARCHAR(20), -- 'current', '6_months', '1_year', '2_years'
    impact_level VARCHAR(20), -- 'low', 'medium', 'high', 'critical'
    generated_by VARCHAR(50) DEFAULT 'sophia_ai',
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE, -- When insight becomes stale
    validated_by VARCHAR(100), -- Human validation
    validation_status VARCHAR(20) DEFAULT 'pending' -- 'pending', 'validated', 'rejected'
);

-- Table for storing comparative market analysis
CREATE TABLE IF NOT EXISTS costar_market_comparisons (
    id SERIAL PRIMARY KEY,
    primary_market_id INTEGER REFERENCES costar_markets(id),
    comparison_market_id INTEGER REFERENCES costar_markets(id),
    property_type VARCHAR(100),
    comparison_type VARCHAR(50), -- 'peer_analysis', 'competitive_set', 'investment_alternative'
    similarity_score DECIMAL(3,2), -- 0.00 to 1.00
    comparison_factors JSONB, -- Factors used in comparison
    analysis_date DATE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- Prevent duplicate comparisons
    UNIQUE(primary_market_id, comparison_market_id, property_type, analysis_date)
);

-- Indexes for performance optimization
CREATE INDEX IF NOT EXISTS idx_costar_market_data_market_date ON costar_market_data(market_id, market_date);
CREATE INDEX IF NOT EXISTS idx_costar_market_data_property_type ON costar_market_data(property_type);
CREATE INDEX IF NOT EXISTS idx_costar_market_data_quarter ON costar_market_data(quarter);
CREATE INDEX IF NOT EXISTS idx_costar_import_log_status ON costar_import_log(import_status);
CREATE INDEX IF NOT EXISTS idx_costar_import_log_created ON costar_import_log(created_at);
CREATE INDEX IF NOT EXISTS idx_costar_insights_market_property ON costar_market_insights(market_id, property_type);
CREATE INDEX IF NOT EXISTS idx_costar_insights_type ON costar_market_insights(insight_type);

-- Insert sample metro areas for testing
INSERT INTO costar_markets (metro_area, state, region, market_tier) VALUES
('San Francisco, CA', 'California', 'West Coast', 'Primary'),
('New York, NY', 'New York', 'Northeast', 'Primary'),
('Los Angeles, CA', 'California', 'West Coast', 'Primary'),
('Chicago, IL', 'Illinois', 'Midwest', 'Primary'),
('Dallas, TX', 'Texas', 'South', 'Primary'),
('Houston, TX', 'Texas', 'South', 'Primary'),
('Atlanta, GA', 'Georgia', 'Southeast', 'Primary'),
('Boston, MA', 'Massachusetts', 'Northeast', 'Primary'),
('Seattle, WA', 'Washington', 'West Coast', 'Primary'),
('Denver, CO', 'Colorado', 'Mountain West', 'Secondary')
ON CONFLICT (metro_area) DO NOTHING;

-- Comments for documentation
COMMENT ON TABLE costar_markets IS 'Master table of metropolitan areas and markets tracked in CoStar system';
COMMENT ON TABLE costar_market_data IS 'Time-series market data including vacancy, rent, inventory, and construction metrics';
COMMENT ON TABLE costar_import_log IS 'Audit trail of all data imports with processing status and error tracking';
COMMENT ON TABLE costar_market_insights IS 'AI-generated insights and analysis based on market data trends';
COMMENT ON TABLE costar_market_comparisons IS 'Comparative analysis between different markets and property types';

COMMENT ON COLUMN costar_market_data.vacancy_rate IS 'Percentage of vacant space (0-100)';
COMMENT ON COLUMN costar_market_data.asking_rent_psf IS 'Average asking rent per square foot annually';
COMMENT ON COLUMN costar_market_data.net_absorption IS 'Net change in occupied space (positive = absorption, negative = give-back)';
COMMENT ON COLUMN costar_market_data.data_quality_score IS 'Quality score from 1-100 based on data completeness and accuracy';
