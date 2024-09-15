import os
import sys
import psycopg2

parent_dir = os.path.abspath(os.path.join(os.getcwd(), "..", os.pardir))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from src.utils import timing, generate
from src.storage import storage


@timing.timing_decorator
def _fetch_similar_messages_for_bot_room(
    config_data,
    scenerio_data,
    message,
    num_messages,
    message_type
):
    query_data = storage.get_message_query_data(scenerio_data, message, message_type)
    message_embedding = generate.get_embeddings(config_data, message, config_data["search"]["embedding_model"])
    try:
        connection = psycopg2.connect(**config_data["database"]["params"])
        with connection.cursor() as cursor:
            cursor.execute(f"""
                SELECT 
                    metadata,
                    message_timestamp,
                    message_embedding <=> %s::vector AS distance
                FROM {config_data["database"]["schema"]}.{config_data["database"]["message_table"]}
                WHERE bot_in_channel_identity_id=%s
                    AND external_channel_id=%s
                ORDER BY distance
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
                {"metadata": metadata, "message_timestamp": message_timestamp}
                for metadata, message_timestamp, _ in results
            ]
    except Exception as error:
        if connection:
            connection.rollback()
        raise error
    finally:
        connection.close()


@timing.timing_decorator
def _fetch_recent_messages_for_bot_room(
    config_data,
    scenerio_data,
    message,
    num_messages,
    message_type
):
    query_data = storage.get_message_query_data(scenerio_data, message, message_type)
    try:
        connection = psycopg2.connect(**config_data["database"]["params"])
        with connection.cursor() as cursor:
            cursor.execute(f"""
                SELECT 
                    metadata,
                    message_timestamp
                FROM {config_data["database"]["schema"]}.{config_data["database"]["message_table"]}
                WHERE bot_in_channel_identity_id = %s
                    AND external_channel_id = %s
                LIMIT %s
                """, (
                    query_data["bot_in_channel_identity_id"],
                    query_data["external_channel_id"],
                    num_messages
                )
            )
            results = cursor.fetchall()
            return [
                {"metadata": metadata, "message_timestamp": message_timestamp}
                for metadata, message_timestamp in results
            ]
    except Exception as error:
        if connection:
            connection.rollback()
        raise error
    finally:
        connection.close()


def _process_aggregate_message_metadatas(messages, num_messages):
    sorted_messages = sorted(messages, key=lambda message: message["message_timestamp"])
    processed_messages = [message["metadata"] for message in sorted_messages]
    unique_messages = list({frozenset(d.items()): d for d in processed_messages}.values())
    pruned_messages = unique_messages[:num_messages]
    return pruned_messages


def get_relevant_messages_from_message_table(config_data, scenerio_data, message, num_messages, message_type):
    messages = _fetch_recent_messages_for_bot_room(config_data, scenerio_data, message, num_messages, message_type)
    messages += _fetch_similar_messages_for_bot_room(config_data, scenerio_data, message, num_messages, message_type)

    return _process_aggregate_message_metadatas(messages, num_messages)


def get_recent_messages_from_message_table(config_data, scenerio_data, message, num_messages, message_type):
    messages = _fetch_recent_messages_for_bot_room(config_data, scenerio_data, message, num_messages, message_type)

    return _process_aggregate_message_metadatas(messages, num_messages)