import os
import sys
import psycopg2

parent_dir = os.path.abspath(os.path.join(os.getcwd(), "..", os.pardir))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from src.utils import timing, generate
from src.storage import storage


@timing.timing_decorator
def _fetch_similar_messages_for_bot_conversation(
    config_data,
    scenerio_data,
    bot_data, 
    message,
    num_messages,
):
    query_data = storage.get_conversation_bot_message_query_data(scenerio_data, bot_data, message)
    message_embedding = generate.get_embeddings(config_data, message, config_data["search"]["embedding_model"])
    try:
        connection = psycopg2.connect(**config_data["database"]["params"])
        with connection.cursor() as cursor:
            cursor.execute(f"""
                SELECT 
                    metadata,
                    message_id,
                    message_timestamp,
                    message_embedding <=> %s::vector AS distance
                FROM {config_data["database"]["schema"]}.{config_data["database"]["message_table"]}
                WHERE bot_in_channel_identity_id=%s
                    AND external_channel_id=%s
                ORDER BY distance, message_timestamp DESC
                LIMIT %s
            """, (
                    message_embedding,
                    query_data["bot_in_channel_identity_id"],
                    query_data["external_channel_id"],
                    num_messages
                )
            )
            results = cursor.fetchall()
            return [
                {"metadata": metadata, "message_id": message_id, "message_timestamp": message_timestamp}
                for metadata, message_id, message_timestamp, _ in results
            ]
    except Exception as error:
        if connection:
            connection.rollback()
        raise error
    finally:
        connection.close()


@timing.timing_decorator
def _fetch_recent_messages_for_bot_conversation(
    config_data,
    scenerio_data,
    bot_data,
    num_messages,
):
    query_data = storage.get_conversation_bot_query_data(scenerio_data, bot_data)
    try:
        connection = psycopg2.connect(**config_data["database"]["params"])
        with connection.cursor() as cursor:
            cursor.execute(f"""
                SELECT 
                    metadata,
                    message_id,
                    message_timestamp
                FROM {config_data["database"]["schema"]}.{config_data["database"]["message_table"]}
                WHERE bot_in_channel_identity_id=%s
                    AND external_channel_id=%s
                ORDER BY message_timestamp DESC
                LIMIT %s
                """, (
                    query_data["bot_in_channel_identity_id"],
                    query_data["external_channel_id"],
                    num_messages
                )
            )
            results = cursor.fetchall()
            return [
                {"metadata": metadata, "message_id": message_id, "message_timestamp": message_timestamp}
                for metadata, message_id, message_timestamp in results
            ]
    except Exception as error:
        if connection:
            connection.rollback()
        raise error
    finally:
        connection.close()


@timing.timing_decorator
def _fetch_recent_messages_for_conversation(
    config_data,
    scenerio_data,
    num_messages,
):
    query_data = storage.get_conversation_query_data(scenerio_data)
    try:
        connection = psycopg2.connect(**config_data["database"]["params"])
        with connection.cursor() as cursor:
            cursor.execute(f"""
                SELECT 
                    metadata,
                    message_id,
                    message_timestamp
                FROM {config_data["database"]["schema"]}.{config_data["database"]["message_table"]}
                WHERE bot_in_channel_identity_id=%s
                    AND external_channel_id=%s
                ORDER BY message_timestamp DESC
                LIMIT %s
                """, (
                    query_data["external_channel_id"],
                    num_messages
                )
            )
            results = cursor.fetchall()
            return [
                {"metadata": metadata, "message_id": message_id, "message_timestamp": message_timestamp}
                for metadata, message_id, message_timestamp in results
            ]
    except Exception as error:
        if connection:
            connection.rollback()
        raise error
    finally:
        connection.close()
        


def _process_aggregate_message_metadatas(messages, num_messages):
    sorted_messages = sorted(messages, key=lambda message: message["message_timestamp"])
    processed_messages = [{"message_id": message["message_id"], **message["metadata"]} for message in sorted_messages]
    unique_messages = list({frozenset(message.items()): message for message in processed_messages}.values())
    pruned_messages = unique_messages[:num_messages]
    return pruned_messages


def get_relevant_messages_from_message_table(config_data, scenerio_data, bot_data, message, num_messages):
    messages = _fetch_similar_messages_for_bot_conversation(config_data, scenerio_data, bot_data, message, num_messages)

    return _process_aggregate_message_metadatas(messages, num_messages)


def get_recent_messages_from_message_table(config_data, scenerio_data, bot_data, message, num_messages):
    messages = _fetch_recent_messages_for_bot_conversation(config_data, scenerio_data, bot_data, num_messages)

    return _process_aggregate_message_metadatas(messages, num_messages)


def get_latest_conversation_event(config_data, scenerio_data):
    messages = _fetch_recent_messages_for_bot_conversation(config_data, scenerio_data, 1)

    return _process_aggregate_message_metadatas(messages, 1)[0]


@timing.timing_decorator
def get_conversation_state(config_data, scenerio_data, bot_data):
    query_data = storage.get_conversation_bot_query_data(scenerio_data)
    try:
        connection = psycopg2.connect(**config_data["database"]["params"])
        with connection.cursor() as cursor:
            cursor.execute(f"""
                SELECT 
                    state
                FROM {config_data["database"]["schema"]}.{config_data["database"]["conversation_state_table"]}
                WHERE external_channel_id = %s
                LIMIT %s
                """, (
                    query_data["external_channel_id"],
                )
            )
            results = cursor.fetchall()
            if len(results) == 0:
                return None
            elif len(results) == 1:
                return results[0]
            else:
                raise ValueError("More than one conversation state found")
    except Exception as error:
        if connection:
            connection.rollback()
        raise error
    finally:
        connection.close()


@timing.timing_decorator
def get_bot_state(config_data, scenerio_data, bot_data):
    query_data = storage.get_conversation_bot_query_data(scenerio_data, bot_data)
    try:
        connection = psycopg2.connect(**config_data["database"]["params"])
        with connection.cursor() as cursor:
            cursor.execute(f"""
                SELECT 
                    state
                FROM {config_data["database"]["schema"]}.{config_data["database"]["bot_state_table"]}
                WHERE external_channel_id = %s
                    AND external_identity_id = %s
                LIMIT %s
                """, (
                    query_data["external_channel_id"],
                    query_data["external_identity_id"]
                )
            )
            results = cursor.fetchall()
            if len(results) == 0:
                return None
            elif len(results) == 1:
                return results[0]
            else:
                raise ValueError("More than one conversation state found")
    except Exception as error:
        if connection:
            connection.rollback()
        raise error
    finally:
        connection.close()