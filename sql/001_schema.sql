CREATE SCHEMA IF NOT EXISTS memory;

BEGIN;

CREATE TABLE IF NOT EXISTS memory.memories
(
  bot_in_channel_id     VARCHAR(255)             NOT NULL, -- bot (this will be duplicated for each bot in room)  
  external_channel_id   VARCHAR(255)             NOT NULL, -- room id
  external_identity_id  VARCHAR(255)             NOT NULL, -- user id
  message_id            VARCHAR(255)             NOT NULL, -- message id
  message_timestamp     TIMESTAMP WITH TIME ZONE NOT NULL,
  message_embedding     JSONB                    NOT NULL, -- message embedding
  metadata              JSONB                    NOT NULL  -- TODO
);

-- metadata: {
--   "message": message, // string
--   ...
-- }

CREATE UNIQUE INDEX IF NOT EXISTS memories_external_identity_id_external_channel_id_bot_in_channel_id_message_id_idx
ON memory.memories (
  bot_in_channel_id,
  external_identity_id,
  external_channel_id,
  message_id
);

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'vector') THEN
        CREATE EXTENSION vector;
    END IF;
END
$$;

COMMIT;