CREATE SCHEMA IF NOT EXISTS memory;

BEGIN;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'vector') THEN
        CREATE EXTENSION vector;
    END IF;
END
$$;

CREATE TABLE IF NOT EXISTS memory.search
(
  bot_in_channel_identity_id  VARCHAR(255)             NOT NULL, -- bot (messages will be duplicated for each bot in room)  
  external_channel_id         VARCHAR(255)             NOT NULL, -- room id
  external_identity_id        VARCHAR(255)             NOT NULL, -- user id of message sender
  message_id                  VARCHAR(255)             NOT NULL PRIMARY KEY, -- message id
  message_timestamp           TIMESTAMP WITH TIME ZONE NOT NULL,
  message_embedding           vector(1536)             NOT NULL, -- message embedding (from openai currently)
  metadata                    JSONB                    NOT NULL  -- (message, ...)
);

CREATE UNIQUE INDEX IF NOT EXISTS search_external_identity_id_external_channel_id_bot_in_channel_identity_id_message_id_idx
ON memory.search (
  bot_in_channel_identity_id,
  external_identity_id,
  external_channel_id,
  message_id
);

COMMIT;