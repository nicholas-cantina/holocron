BEGIN;

CREATE SCHEMA IF NOT EXISTS memory;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'vector') THEN
        CREATE EXTENSION vector;
    END IF;
END
$$;

CREATE TABLE IF NOT EXISTS memory.messages
(
  bot_in_channel_identity_id  VARCHAR(255)             NOT NULL,  -- bot id (optimization -- messages will be duplicated for each bot in room)  
  external_channel_id         VARCHAR(255)             NOT NULL,  -- room id
  external_identity_id        VARCHAR(255)             NOT NULL,  -- user id of message sender
  message_id                  VARCHAR(255)             NOT NULL,  -- message id
  message_timestamp           TIMESTAMP WITH TIME ZONE NOT NULL,
  message_embedding           vector(1536)             NOT NULL,  -- message embedding
  metadata                    JSONB                    NOT NULL,  -- (message, ...)
  PRIMARY KEY (bot_in_channel_identity_id, external_channel_id, message_id)
);

CREATE UNIQUE INDEX IF NOT EXISTS messages_external_identity_id_external_channel_id_bot_in_channel_identity_id_message_id_idx
ON memory.messages (
  bot_in_channel_identity_id,
  external_identity_id,
  external_channel_id,
  message_id
);

CREATE TABLE IF NOT EXISTS memory.conversation_state
(
  external_channel_id         VARCHAR(255)             NOT NULL, -- room id
  "state"                     JSONB                    NOT NULL, -- (???, ...)
  PRIMARY KEY (external_channel_id)
);

CREATE TABLE IF NOT EXISTS memory.bot_state
(
  external_channel_id         VARCHAR(255)             NOT NULL, -- room id
  external_identity_id        VARCHAR(255)             NOT NULL, -- bot id
  "state"                     JSONB                    NOT NULL, -- (???, ...)
  PRIMARY KEY (external_channel_id, external_identity_id)
);

