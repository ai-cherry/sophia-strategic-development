-- Add column to GONG_CALLS to store the timestamp of the Slack notification
ALTER TABLE GONG_CALLS ADD COLUMN slack_notification_ts VARCHAR(255);

-- Create table to link Slack threads to Gong conversations
CREATE TABLE IF NOT EXISTS SLACK_CONVERSATIONS (
    thread_ts VARCHAR(255) PRIMARY KEY,
    gong_conversation_key VARCHAR(255) NOT NULL,
    channel_id VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (gong_conversation_key) REFERENCES GONG_CONVERSATIONS(conversation_key)
);

COMMENT ON COLUMN GONG_CALLS.slack_notification_ts IS 'Timestamp of the initial Slack notification for this call, linking to a thread in SLACK_CONVERSATIONS.';
COMMENT ON TABLE SLACK_CONVERSATIONS IS 'Stores mapping between Slack conversation threads and Gong conversations.';
COMMENT ON COLUMN SLACK_CONVERSATIONS.thread_ts IS 'The timestamp of the parent message in a Slack thread, acts as the thread identifier.';
COMMENT ON COLUMN SLACK_CONVERSATIONS.gong_conversation_key IS 'Foreign key linking to the GONG_CONVERSATIONS table.';
COMMENT ON COLUMN SLACK_CONVERSATIONS.channel_id IS 'The Slack channel ID where the conversation is taking place.';
