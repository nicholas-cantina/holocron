import os
import sys
import psycopg2
import json
import hashlib

from datetime import datetime

parent_dir = os.path.abspath(os.path.join(os.getcwd(), "..", os.pardir))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from src.utils import timing, generate


def _hash_string(input_string):
    hash_object = hashlib.sha256()
    hash_object.update(input_string.encode("utf-8"))
    hashed_string = hash_object.hexdigest()

    return hashed_string


# This is specific to the way our test data is configured
def _get_query_data(conversation_data, message, message_type):
    message_full_name = message["full_name"] if message["role"] == "user" else conversation_data["bot"]["full_name"]

    return {
        "bot_in_channel_identity_id": conversation_data["bot"]["full_name"],  # This is a placeholder
        "external_channel_id": conversation_data["_id"],  # This is a placeholder
        "external_identity_id": message_full_name,  # This is a placeholder
        "message_id": _hash_string(conversation_data["_id"] + ":" + message_full_name + ":" + message["message"]),  # This is a placeholder
        "message_timestamp": datetime.now(),  # This is a placeholder
        "metadata": {
            "message_type": message_type,
            **message
        }
    }


@timing.timing_decorator
def save_message_to_search_table(
    config_data,
    conversation_data,
    message,
    message_type,
):
    query_data = _get_query_data(conversation_data, message, message_type)
    message_embedding = generate.get_embeddings(config_data, message, config_data["generation"]["embedding_model"])
    try:
        connection = psycopg2.connect(**config_data["database"]["params"])
        with connection.cursor() as cursor:
            cursor.execute(
                f"""
                INSERT INTO {config_data["database"]["schema"]}.{config_data["database"]["search_table"]} 
                (
                    bot_in_channel_identity_id, 
                    external_channel_id, 
                    external_identity_id, 
                    message_id, 
                    message_timestamp, 
                    message_embedding, 
                    metadata
                )
                VALUES (%s, %s, %s, %s, %s, %s::vector, %s)
                ON CONFLICT (message_id) DO NOTHING -- This is a placeholder
                """,
                (   
                    query_data["bot_in_channel_identity_id"],
                    query_data["external_channel_id"],
                    query_data["external_identity_id"],
                    query_data["message_id"],
                    query_data["message_timestamp"],
                    message_embedding,
                    json.dumps(query_data["metadata"])
                )
            )
            connection.commit()
    except Exception as error:
        if connection:
            connection.rollback()
        raise error 
    finally:
        connection.close()


def save_conversation_to_search_table(config_data, conversation_data):
    messages = conversation_data["messages"]

    for message in messages:
        save_message_to_search_table(config_data, conversation_data, message, "chat")


@timing.timing_decorator
def _fetch_similar_messages_for_bot_room(
    config_data,
    conversation_data,
    message,
    num_messages,
    message_type
):
    query_data = _get_query_data(conversation_data, message, message_type)
    message_embedding = generate.get_embeddings(config_data, message, config_data["generation"]["embedding_model"])
    try:
        connection = psycopg2.connect(**config_data["database"]["params"])
        with connection.cursor() as cursor:
            cursor.execute(f"""
                SELECT 
                    metadata,
                    message_timestamp,
                    message_embedding <=> %s::vector AS distance
                FROM {config_data["database"]["schema"]}.{config_data["database"]["search_table"]}
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
    conversation_data,
    message,
    num_messages,
    message_type
):
    query_data = _get_query_data(conversation_data, message, message_type)
    try:
        connection = psycopg2.connect(**config_data["database"]["params"])
        with connection.cursor() as cursor:
            cursor.execute(f"""
                SELECT 
                    metadata,
                    message_timestamp
                FROM {config_data["database"]["schema"]}.{config_data["database"]["search_table"]}
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
    sorted_messages = sorted(messages, key=lambda x: x["message_timestamp"])
    processed_messages = [message["metadata"] for message in sorted_messages]
    unique_messages = list({frozenset(d.items()): d for d in processed_messages}.values())
    pruned_messages = unique_messages[:num_messages]
    return pruned_messages


def get_relevant_messages_from_search_table(config_data, conversation_data, message, num_messages, message_type):
    messages = _fetch_recent_messages_for_bot_room(config_data, conversation_data, message, num_messages, message_type)
    messages += _fetch_similar_messages_for_bot_room(config_data, conversation_data, message, num_messages, message_type)

    return _process_aggregate_message_metadatas(messages, num_messages)


def get_recent_messages_from_search_table(config_data, conversation_data, message, num_messages, message_type):
    messages = _fetch_recent_messages_for_bot_room(config_data, conversation_data, message, num_messages, message_type)

    return _process_aggregate_message_metadatas(messages, num_messages)
