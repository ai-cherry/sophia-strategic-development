-- Table to store historical client health scores
CREATE TABLE IF NOT EXISTS CLIENT_HEALTH_SCORES (
    score_id VARCHAR(255) PRIMARY KEY,
    client_entity_id VARCHAR(255) NOT NULL,
    score INTEGER NOT NULL,
    trend VARCHAR(50),
    positive_factors JSONB,
    risk_factors JSONB,
    calculation_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (client_entity_id) REFERENCES ENTITIES(entity_id)
);

CREATE INDEX idx_client_health_scores_client_id ON CLIENT_HEALTH_SCORES (client_entity_id);
CREATE INDEX idx_client_health_scores_timestamp ON CLIENT_HEALTH_SCORES (calculation_timestamp);

COMMENT ON TABLE CLIENT_HEALTH_SCORES IS 'Stores a historical record of calculated health scores for clients.';
COMMENT ON COLUMN CLIENT_HEALTH_SCORES.score IS 'The calculated health score, typically from 0 to 100.';
COMMENT ON COLUMN CLIENT_HEALTH_SCORES.trend IS 'The trend of the health score, e.g., "improving", "stable", "declining".';
COMMENT ON COLUMN CLIENT_HEALTH_SCORES.positive_factors IS 'A JSON object detailing the factors that contributed positively to the score.';
COMMENT ON COLUMN CLIENT_HEALTH_SCORES.risk_factors IS 'A JSON object detailing the factors that contributed negatively to the score.';
