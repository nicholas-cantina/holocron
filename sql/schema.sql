BEGIN;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'vector') THEN
        CREATE EXTENSION vector;
    END IF;
END
$$;

CREATE SCHEMA IF NOT EXISTS stm;

CREATE TABLE IF NOT EXISTS stm.messages (
    bot_in_conversation_identity_id VARCHAR(255) NOT NULL,  -- bot id (optimization -- messages will be duplicated for each bot in room)
    conversation_id VARCHAR(255) NOT NULL,  -- room id
    user_id VARCHAR(255) NOT NULL,  -- user id of message sender
    id VARCHAR(255) NOT NULL,  -- message id
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    metadata JSONB NOT NULL,  -- (message, ...)
    PRIMARY KEY (bot_in_conversation_identity_id, conversation_id, id)
)
PARTITION BY HASH (bot_in_conversation_identity_id);

DO $func$
BEGIN
  FOR i IN 0..9 LOOP
    EXECUTE FORMAT('CREATE TABLE IF NOT EXISTS stm.messages_%s PARTITION OF stm.messages FOR VALUES WITH (modulus 10, remainder %s)', TO_CHAR(i, 'fm000'), i);
  END LOOP;
END;
$func$ language 'plpgsql';

CREATE UNIQUE INDEX IF NOT EXISTS 
messages_user_id_conversation_id_bot_in_conversation_identity_id_id_idx
ON stm.messages (bot_in_conversation_identity_id, conversation_id, user_id, id);

CREATE SCHEMA IF NOT EXISTS mtm;

CREATE TABLE IF NOT EXISTS mtm.summaries (
    conversation_id VARCHAR(255) NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    state JSONB NOT NULL,
    PRIMARY KEY (conversation_id, user_id)
)
PARTITION BY HASH (conversation_id, user_id);

DO $func$
BEGIN
  FOR i IN 0..9 LOOP
    EXECUTE FORMAT('CREATE TABLE IF NOT EXISTS mtm.summaries_%s PARTITION OF mtm.summaries FOR VALUES WITH (modulus 10, remainder %s)', TO_CHAR(i, 'fm000'), i);
  END LOOP;
END;
$func$ language 'plpgsql';

CREATE SCHEMA IF NOT EXISTS ltm;

CREATE TABLE IF NOT EXISTS ltm.summaries (
    bot_in_conversation_identity_id VARCHAR(255) NOT NULL,  -- bot id (optimization -- summaries will be duplicated for each bot in room)
    conversation_id VARCHAR(255) NOT NULL,
    id VARCHAR(255) NOT NULL,  -- summary id
    user_id VARCHAR(255) NOT NULL,  -- user id of summary creator
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    embedding vector(1536) NOT NULL,  -- summary embedding
    metadata JSONB NOT NULL,  -- (summary, ...)
    PRIMARY KEY (bot_in_conversation_identity_id, conversation_id, id)
)
PARTITION BY HASH (bot_in_conversation_identity_id, conversation_id);

DO $func$
BEGIN
  FOR i IN 0..9 LOOP
    EXECUTE FORMAT('CREATE TABLE IF NOT EXISTS ltm.summaries_%s PARTITION OF ltm.summaries FOR VALUES WITH (modulus 10, remainder %s)', TO_CHAR(i, 'fm000'), i);
  END LOOP;
END;
$func$ language 'plpgsql';

CREATE UNIQUE INDEX IF NOT EXISTS 
summaries_conversation_id_bot_in_conversation_identity_id_id_idx
ON ltm.summaries (bot_in_conversation_identity_id, conversation_id, id);

CREATE INDEX IF NOT EXISTS 
summaries_conversation_id_bot_in_conversation_identity_id_embedding_idx
ON ltm.summaries USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64);

COMMIT;