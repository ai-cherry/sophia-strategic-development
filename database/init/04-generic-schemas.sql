-- Generic EVENTS table for tracking actions across all integrated systems
CREATE TABLE IF NOT EXISTS EVENTS (
    event_id VARCHAR(255) PRIMARY KEY,
    event_type VARCHAR(255) NOT NULL,
    source_system VARCHAR(100),
    user_id VARCHAR(255),
    entity_id VARCHAR(255),
    event_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    event_properties JSONB,
    raw_event JSONB,
    etl_inserted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE EVENTS IS 'A generic table to capture time-series events from any integrated system (e.g., deal stage changed, user logged in).';
COMMENT ON COLUMN EVENTS.event_type IS 'The type of the event, e.g., "deal_stage_changed".';
COMMENT ON COLUMN EVENTS.source_system IS 'The system where the event originated, e.g., "HubSpot", "Gong", "Sophia".';


-- Generic ENTITIES table for storing master data about key business objects
CREATE TABLE IF NOT EXISTS ENTITIES (
    entity_id VARCHAR(255) PRIMARY KEY,
    entity_type VARCHAR(100) NOT NULL,
    source_system VARCHAR(100),
    name VARCHAR(255),
    properties JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_entities_entity_type ON ENTITIES (entity_type);

COMMENT ON TABLE ENTITIES IS 'A generic table to store master data for key business entities like Companies, Contacts, Projects, etc.';
COMMENT ON COLUMN ENTITIES.entity_id IS 'A unique identifier for the entity across all systems.';
COMMENT ON COLUMN ENTITIES.entity_type IS 'The type of entity, e.g., "Company", "Contact".';


-- Generic RELATIONSHIPS table to define connections between entities
CREATE TABLE IF NOT EXISTS RELATIONSHIPS (
    relationship_id VARCHAR(255) PRIMARY KEY,
    source_entity_id VARCHAR(255) NOT NULL,
    target_entity_id VARCHAR(255) NOT NULL,
    relationship_type VARCHAR(100) NOT NULL,
    properties JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (source_entity_id) REFERENCES ENTITIES(entity_id),
    FOREIGN KEY (target_entity_id) REFERENCES ENTITIES(entity_id)
);

COMMENT ON TABLE RELATIONSHIPS IS 'Defines the links between entities, e.g., Contact A "works for" Company B.';
COMMENT ON COLUMN RELATIONSHIPS.relationship_type IS 'The nature of the relationship, e.g., "works_for", "is_subsidiary_of".';
