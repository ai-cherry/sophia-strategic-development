-- Watermark ledger for incremental jobs
CREATE TABLE IF NOT EXISTS OPS_MONITORING.DEDUPE_WATERMARKS (
    source_system VARCHAR(100),
    job_name VARCHAR(150),
    last_watermark VARIANT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    PRIMARY KEY (source_system, job_name)
);