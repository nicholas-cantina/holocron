CREATE SCHEMA IF NOT EXISTS memory;

BEGIN;

CREATE TABLE IF NOT EXISTS memory.memories
(
  bot_in_channel_id     VARCHAR(255)             NOT NULL, -- bot (this will be duplicated for each bot in room)  
  external_channel_id   VARCHAR(255)             NOT NULL, -- room id
  external_identity_id  VARCHAR(255)             NOT NULL, -- user id
  message_id            VARCHAR(255)             NOT NULL, -- message id
  message_timestamp     TIMESTAMP WITH TIME ZONE NOT NULL,
  message_embedding     JSONB                    NOT NULL, -- message embedding (for semantic search)
  metadata              JSONB                    NOT NULL  -- TODO
);

-- metadata: {
--   "messages": [message_1, message_2, ...],
--   ...
-- }

-- message: {
--   "message_history": ["message_id", "message_id", ...],
-- }

CREATE UNIQUE INDEX IF NOT EXISTS memories_external_identity_id_external_channel_id_bot_in_channel_id_message_id_idx
ON memory.memories (
  external_identity_id,
  external_channel_id,
  bot_in_channel_id,
  message_id
);

CREATE EXTENSION vector;

COMMIT;