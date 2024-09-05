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


def get_message_query_data(scenerio_data, bot_data, message):
    return {
        "bot_in_channel_identity_id": bot_data["id"],
        "external_channel_id": scenerio_data["id"],
        "external_identity_id": message["user_id"],
        "message_id": _hash_string(message["user_id"] + ":" + message["message"]),
        "message_timestamp": datetime.now(),
        "metadata": {
            **message
        }
    }


def _get_bot_query_data(scenerio_data, bot_data):
    return {
        "external_channel_id": scenerio_data["id"],  # This is a placeholder
        "external_identity_id": bot_data["full_name"],  # This is a placeholder
    }


def _get_conversation_query_data(scenerio_data):
    return {
        "external_channel_id": scenerio_data["_id"],  # This is a placeholder
    }


@timing.timing_decorator
def save_message(
    config_data,
    scenerio_data,
    bot_data,
    message,
):
    query_data = get_message_query_data(scenerio_data, bot_data, message)
    message_embedding = generate.get_embeddings(config_data, message, config_data["generation"]["embedding_model"])
    try:
        connection = psycopg2.connect(**config_data["database"]["params"])
        with connection.cursor() as cursor:
            cursor.execute(
                f"""
                INSERT INTO {config_data["database"]["schema"]}.{config_data["database"]["message_table"]} 
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


@timing.timing_decorator
def get_conversation_state(config_data, scenerio_data, bot_data):
    query_data = _get_conversation_query_data(scenerio_data)
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
                raise ValueError("More than one room state found")
    except Exception as error:
        if connection:
            connection.rollback()
        raise error
    finally:
        connection.close()


@timing.timing_decorator
def get_bot_state(config_data, scenerio_data, bot_data):
    query_data = _get_bot_query_data(scenerio_data, bot_data)
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
                raise ValueError("More than one room state found")
    except Exception as error:
        if connection:
            connection.rollback()
        raise error
    finally:
        connection.close()
